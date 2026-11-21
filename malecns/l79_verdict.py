"""L79 verdict: re-derive ALL analysis from checkpointed l79/raw_l79.npz
(l77-precedent: analysis crash after rollouts -> zero reruns). Anchors
re-computed from the npz + l59 raw. C1 (af range) was an in-run assert that
PASSED before the crash (run.out line 'C0a True ... C1 True') — disclosed.
"""
import json
import math

import numpy as np

WIN = 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
BLK = 500
MEAS0 = 500
DT = 0.01
SETTLE = 400
SEEDS = [11, 22, 33] + list(range(101, 114))
ANCHOR_SEEDS = [11, 22, 33]
ENT_AMP = 0.3
LOCK_TOL = 0.10
GAP0, GAP1 = 2500, 2700
ARMS = ["hynohop", "hybrid", "reprime", "hyreprime"]
TWINS = {"reprime": "hynohop", "hyreprime": "hybrid"}
SIGS = ("fL", "fR", "eL", "eR")
W_EARLY = (2500, 3200)
W_POST = (3200, 4000)
W_SPLIT = (3600, 4000)

z = np.load("l79/raw_l79.npz")
z59 = np.load("l59/raw_l59.npz")
res = {}
for s in SEEDS:
    res[str(s)] = dict(
        mm={a: z[f"mm_{a}_{s}"].astype(np.float32) for a in ARMS},
        tr={a: {c: z[f"{c}_{a}_{s}"].astype(np.float32) for c in SIGS}
            for a in ARMS})


def dom_freq(x, lo=0.3):
    x = np.asarray(x)
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    return float(f_hat)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


# ---------------- anchors from npz ----------------
c0a, c0b = {}, {}
for s in ANCHOR_SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hynohop"] - z59[f"mm_hynohop_{s}"][:WIN]).max())
    c0b[f"mm_{s}"] = float(np.abs(
        res[str(s)]["mm"]["hybrid"] - z59[f"mm_hybrid_{s}"][:WIN]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hynohop"][c] - z59[f"{c}_hynohop_{s}"][:WIN]).max())
        c0b[f"{c}_{s}"] = float(np.abs(
            res[str(s)]["tr"]["hybrid"][c] - z59[f"{c}_hybrid_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0b_pass = all(v == 0.0 for v in c0b.values())

c0p1, c0p2, dm = {}, {}, {}
for rp in TWINS:
    tw = TWINS[rp]
    for s in SEEDS:
        m = res[str(s)]
        pre = [np.abs(m["mm"][rp][:GAP0] - m["mm"][tw][:GAP0])]
        pre += [np.abs(m["tr"][rp][c][:GAP0] - m["tr"][tw][c][:GAP0]) for c in SIGS]
        c0p1[f"{rp}_{s}"] = float(np.concatenate(pre).max())
        diffs = np.concatenate(
            [np.abs(m["mm"][rp] - m["mm"][tw])]
            + [np.abs(m["tr"][rp][c] - m["tr"][tw][c]) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        c0p2[f"{rp}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{rp}_{s}"] = round(float(diffs.max()), 5)
wired_dead = [k for k, v in dm.items() if v == 0.0]
c0p1_pass = all(v == 0.0 for v in c0p1.values())
c0p2_pass = (not wired_dead and all(v == GAP0 + 1 for v in c0p2.values()))
print(f"anchors: C0a {c0a_pass} C0b {c0b_pass} C0P-1 {c0p1_pass} "
      f"C0P-2 {c0p2_pass} wired_dead {len(wired_dead)} "
      f"(C1 af: in-run assert PASSED pre-crash, run.out)")

# ---------------- S arrays + cells ----------------
TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (res[s]["tr"][a][c] for c in SIGS)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    SM[(a, s)] = (SL, SR)
    return SL, SR


def wmed(lo, hi, arr):
    q = (TS >= lo) & (TS < hi)
    if not q.any():
        return None
    return round(float(np.nanmedian(arr[TS[q]])), 3)


cells = {a: {str(s): {} for s in SEEDS} for a in ARMS}
for a in ARMS:
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        rows = []
        for si, (a0_, b0, tg) in enumerate(SEGB):
            lo, hi = a0_ + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])
            bl_errs, ttl = [], None
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    f_hat = dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK])
                    e = abs(f_hat - tg)
                    bl_errs.append(e)
                    if ttl is None and e <= LOCK_TOL:
                        ttl = b * BLK - a0_
            rows.append(dict(
                duty=round(float(np.nanmean(both)), 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3),
                err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
        post_errs = []
        for b0 in (3000, 3500):
            f_hat = dom_freq(res[str(s)]["mm"][a][b0:b0 + BLK])
            post_errs.append(abs(f_hat - 1.4))
        f_strad = dom_freq(res[str(s)]["mm"][a][2500:3000])
        wins = {}
        for name, (lo, hi) in (("wearly", W_EARLY), ("wpost", W_POST),
                               ("wpost_late", (W_SPLIT[0], W_SPLIT[1]))):
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            wins[name] = dict(
                duty=round(float(np.nanmean(both)), 3),
                SL=round(float(np.nanmedian(SL[TS[q]])), 3),
                SR=round(float(np.nanmedian(SR[TS[q]])), 3))
        qa = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qa |= (TS >= a0_ + MEAS0) & (TS < b0)
        both_all = (SL[TS[qa]] >= 0.25) & (SR[TS[qa]] >= 0.25)
        cells[a][str(s)] = dict(
            segs=rows, **wins,
            lock_post=round(float(np.mean(post_errs)), 4),
            lock_straddle=round(abs(f_strad - 1.4), 4),
            seg1=rows[1]["duty"],
            duty_all=round(float(np.nanmean(both_all)), 3))


def wilson(k, nn, z_=1.96):
    p = k / nn
    den = 1 + z_ * z_ / nn
    c = (p + z_ * z_ / (2 * nn)) / den
    hw = z_ * math.sqrt(p * (1 - p) / nn + z_ * z_ / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


def dist_of(a, key, sub=None):
    v = np.array([cells[a][str(s)][key] if sub is None
                  else cells[a][str(s)][key][sub] for s in SEEDS])
    return dict(vals=[round(float(x), 3) for x in v],
                mean=round(float(v.mean()), 3),
                med=round(float(np.median(v)), 3),
                mn=round(float(v.min()), 3))


p1 = {}
for rp in TWINS:
    tw = TWINS[rp]
    d_early = np.array([cells[rp][str(s)]["wearly"]["duty"]
                        - cells[tw][str(s)]["wearly"]["duty"] for s in SEEDS])
    d_post = np.array([cells[rp][str(s)]["wpost"]["duty"]
                       - cells[tw][str(s)]["wpost"]["duty"] for s in SEEDS])
    d_late = np.array([cells[rp][str(s)]["wpost_late"]["duty"]
                       - cells[tw][str(s)]["wpost_late"]["duty"] for s in SEEDS])
    kp = int((np.array([cells[rp][str(s)]["wpost"]["duty"] for s in SEEDS]) >= .25).sum())
    kt = int((np.array([cells[tw][str(s)]["wpost"]["duty"] for s in SEEDS]) >= .25).sum())
    mean_d = round(float(d_post.mean()), 3)
    n_up = int((d_post >= 0).sum())
    if mean_d >= .10 and n_up >= 11:
        verdict = "HELP"
    elif mean_d <= -.10 and int((d_post <= 0).sum()) >= 11:
        verdict = "HURT"
    else:
        verdict = "NULL/INCONCLUSIVE"
    p1[rp] = dict(
        twin=tw,
        wpost_twin=dist_of(tw, "wpost", "duty"), wpost=dist_of(rp, "wpost", "duty"),
        wearly_twin=dist_of(tw, "wearly", "duty"), wearly=dist_of(rp, "wearly", "duty"),
        wpost_late_twin=dist_of(tw, "wpost_late", "duty"),
        wpost_late=dist_of(rp, "wpost_late", "duty"),
        d_post=[round(float(x), 3) for x in d_post],
        d_early=[round(float(x), 3) for x in d_early],
        d_late=[round(float(x), 3) for x in d_late],
        d_post_mean=mean_d, d_post_up=n_up,
        d_early_mean=round(float(d_early.mean()), 3),
        d_late_mean=round(float(d_late.mean()), 3),
        k_post_ge25=kp, k_twin_ge25=kt,
        wilson_post=wilson(kp, len(SEEDS)), wilson_twin=wilson(kt, len(SEEDS)),
        verdict=verdict)

p2 = {}
for a in ARMS:
    errs = np.array([cells[a][str(s)]["lock_post"] for s in SEEDS])
    strad = np.array([cells[a][str(s)]["lock_straddle"] for s in SEEDS])
    p2[a] = dict(le01=int((errs <= .01).sum()), mean=round(float(errs.mean()), 4),
                 vals=[round(float(x), 4) for x in errs],
                 straddle_mean=round(float(strad.mean()), 4),
                 straddle_vals=[round(float(x), 4) for x in strad])

p4 = {}
for rp in TWINS:
    sl = sr = bothb = 0
    miss = []
    for s in SEEDS:
        cell = cells[rp][str(s)]
        if cell["wpost"]["duty"] >= .25:
            continue
        sl_low = cell["wpost"]["SL"] < .25
        sr_low = cell["wpost"]["SR"] < .25
        if sl_low and sr_low:
            bothb += 1
        elif sl_low:
            sl += 1
        elif sr_low:
            sr += 1
        miss.append(dict(seed=s, duty=cell["wpost"]["duty"],
                         SL=cell["wpost"]["SL"], SR=cell["wpost"]["SR"]))
    tot = sl + sr + bothb
    p4[rp] = dict(n_miss=len(miss), sl_owned=sl, sr_owned=sr, both=bothb,
                  sl_share=round(sl / tot, 3) if tot else None, misses=miss)

# P5: entrain masses from the pure-math schedule (no graph needed)
def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
AMPA = {a: np.zeros(WIN) for a in ARMS}
for a in ARMS:
    for seg0, _, _ in SEGB:
        c = 0
        while seg0 + c * 900 < seg0 + SEG:
            lo = seg0 + c * 900
            AMPA[a][lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
            c += 1
    AMPA[a][2000:4000] = ENT_AMP
for a in ("reprime", "hyreprime"):
    AMPA[a][GAP0:GAP1] = 0.0
on = {a: int((AMPA[a] > 0).sum()) for a in ARMS}
mass = {a: round(float(ENT_AMP * sum(0.5 + 0.5 * math.sin(PHI[k])
                                      for k in range(WIN) if AMPA[a][k] > 0)), 1)
        for a in ARMS}
p5 = dict(drive_on_steps=on, entrain_mass=mass,
          budget_delta=round(4600 / 4800 - 1, 4))
assert on["hynohop"] == 4400 and on["reprime"] == 4200   # pre-settle counts

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, gap=[GAP0, GAP1],
                     windows=dict(wearly=W_EARLY, wpost=W_POST,
                                  wpost_late=W_SPLIT),
                     drive_on={a: on[a] + SETTLE for a in ARMS},
                     derived_from="l79/raw_l79.npz (rollouts 245 s, run.out)"),
           anchors=dict(c0a_pass=c0a_pass, c0b_pass=c0b_pass,
                        c0p1_pass=c0p1_pass, c0p2_pass=bool(c0p2_pass),
                        c1="in-run assert PASSED pre-crash (run.out)",
                        wired_dead=wired_dead,
                        first_div=c0p2, prefix_maxd=c0p1, dm=dm),
           p1=p1, p2=p2, p4=p4, p5=p5,
           seg1={a: dist_of(a, "seg1") for a in ARMS},
           duty_all={a: dist_of(a, "duty_all") for a in ARMS},
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l79/results_l79.json", "w"), indent=1)
print("P1 " + json.dumps({k: dict(verdict=v["verdict"],
                                  d_post_mean=v["d_post_mean"],
                                  d_early_mean=v["d_early_mean"],
                                  d_late_mean=v["d_late_mean"],
                                  k=v["k_post_ge25"], k_twin=v["k_twin_ge25"],
                                  d_post_up=v["d_post_up"])
                          for k, v in p1.items()}))
print("P2 " + json.dumps({a: {kk: v for kk, v in p2[a].items()
                              if kk != "vals" and kk != "straddle_vals"}
                          for a in ARMS}))
print("P4 " + json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "misses"}
                          for k, v in p4.items()}))
print("P5 " + json.dumps(p5))
print("done -> l79/results_l79.json")
