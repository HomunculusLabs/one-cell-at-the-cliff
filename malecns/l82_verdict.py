"""L82 verdict: re-derive ALL reads from the checkpointed raw npz (l77/l79
precedent — the run's analysis block crashed post-checkpoint on the l77-class
dom_freq[0] slip; rollouts + anchors already green in run.out). Zero reruns."""
import json
import math

import numpy as np

WIN, SEG, BLK, MEAS0 = 6000, 2000, 500, 500
SETTLE, DT = 400, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEEDS = [11, 22, 33] + list(range(101, 114))
ANCHOR_SEEDS = [11, 22, 33]
ARMS = ["hynohop", "hynohop_fb", "hynohop_fb07"]
FB_ARMS = ["hynohop_fb", "hynohop_fb07"]
SIGS = ("fL", "fR", "eL", "eR")
FB = dict(gfb=.1, delay=5, sign=-1.0)
ENT_AMP, LOCK_TOL = 0.3, 0.10

z = np.load("l82/raw_l82.npz")
res = {}
for s in SEEDS:
    res[str(s)] = dict(
        mm={a: z[f"mm_{a}_{s}"] for a in ARMS},
        tr={a: {c: z[f"{c}_{a}_{s}"] for c in SIGS} for a in ARMS},
        mA={a: z[f"mA_{a}_{s}"] for a in FB_ARMS})

# ---------- anchors re-derived from checkpoint ----------
z59, z77, z66 = np.load("l59/raw_l59.npz"), np.load("l77/raw_l77.npz"), np.load("l66/raw_l66.npz")
c0a = c0x = True
for s in ANCHOR_SEEDS:
    c0a &= float(np.abs(res[str(s)]["mm"]["hynohop"] - z59[f"mm_hynohop_{s}"][:WIN]).max()) == 0.0
    c0x &= float(np.abs(res[str(s)]["mm"]["hynohop_fb"] - z77[f"mm_hynohop_fb_{s}"][:WIN]).max()) == 0.0
    c0x &= float(np.abs(res[str(s)]["mm"]["hynohop_fb"] - z66[f"mm_g01_d05_m_{s}"][:WIN]).max()) == 0.0
    for c in SIGS:
        c0a &= float(np.abs(res[str(s)]["tr"]["hynohop"][c] - z59[f"{c}_hynohop_{s}"][:WIN]).max()) == 0.0
        c0x &= float(np.abs(res[str(s)]["tr"]["hynohop_fb"][c] - z77[f"{c}_hynohop_fb_{s}"][:WIN]).max()) == 0.0
        c0x &= float(np.abs(res[str(s)]["tr"]["hynohop_fb"][c] - z66[f"{c}_g01_d05_m_{s}"][:WIN]).max()) == 0.0
PAIRSETS = [("hynohop_fb", "hynohop"), ("hynohop_fb07", "hynohop"),
            ("hynohop_fb07", "hynohop_fb")]
first_div, dm, prefix = {}, {}, {}
for a, b in PAIRSETS:
    for s in SEEDS:
        m = res[str(s)]
        arrs = [np.abs(m["mm"][a] - m["mm"][b])] + [
            np.abs(m["tr"][a][c] - m["tr"][b][c]) for c in SIGS]
        diffs = np.concatenate(arrs)
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{a}|{b}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{a}|{b}_{s}"] = round(float(diffs.max()), 5)
        prefix[f"{a}|{b}_{s}"] = float(max(x[:2001].max() for x in arrs))
c0p1 = all(prefix[f"hynohop_fb07|hynohop_fb_{s}"] == 0.0 for s in SEEDS)
c0p2 = (all(first_div[f"hynohop_fb|hynohop_{s}"] == 6 for s in SEEDS)
        and all(first_div[f"hynohop_fb07|hynohop_{s}"] == 6 for s in SEEDS)
        and all(first_div[f"hynohop_fb07|hynohop_fb_{s}"] == 2001 for s in SEEDS))
wired_dead = [k for k, v in dm.items() if v == 0.0]
print(f"anchors: C0a {c0a} C0x {c0x} C0P-1 {c0p1} C0P-2 {c0p2} "
      f"wired_dead {len(wired_dead)}")


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


def dom_freq(x, lo=0.3):
    x = np.asarray(x, np.float64)
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


# AMPA + phase rebuilt for budget
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(WIN)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
AMPA = np.zeros(WIN)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
on_steps = np.where(AMPA > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = float(ENT_AMP * sin_on.sum())

# ---------- cells ----------
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
    return round(float(np.nanmedian(arr[TS[q]])), 3) if q.any() else None


cells = {a: {} for a in ARMS}
for a in ARMS:
    for s in SEEDS:
        SL, SR = s_arrays(a, str(s))
        rows = []
        for a0_, b0, tg in SEGB:
            lo, hi = a0_ + MEAS0, b0
            q = (TS >= lo) & (TS < hi)
            both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
            f_seg = dom_freq(res[str(s)]["mm"][a][a0_:b0])
            bl_errs = []
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    bl_errs.append(abs(dom_freq(res[str(s)]["mm"][a][b * BLK:(b + 1) * BLK]) - tg))
            rows.append(dict(duty=round(float(np.nanmean(both)), 3),
                             SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                             f=round(f_seg, 3), err=round(float(np.mean(bl_errs)), 4)))
        qall = np.zeros(len(TS), bool)
        q07 = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
            if f == 0.7:
                q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
        cells[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean((SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
            duty_07=round(float(np.nanmean((SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))

# ---------- budget ----------
g07mask = np.zeros(WIN, bool)
g07mask[:2000] = True
g07mask[4000:] = True
EON = {"hynohop_fb": np.ones(WIN, bool), "hynohop_fb07": g07mask}
budget = {}
for fb in FB_ARMS:
    ks = np.where(EON[fb])[0]
    ks = ks[ks >= FB["delay"]]
    em = [float(FB["gfb"] * res[str(s)]["mA"][fb][ks - FB["delay"]].sum()) for s in SEEDS]
    budget[fb] = dict(echo_mass_mean=round(float(np.mean(em)), 4),
                      entrain_mass=round(entrain_mass, 1),
                      ratio_mean=round(float(np.mean(em)) / entrain_mass, 4))


def wilson(k, nn, z=1.96):
    p = k / nn
    den = 1 + z * z / nn
    c = (p + z * z / (2 * nn)) / den
    hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


dist = {}
for a in ARMS:
    per_seg = []
    for i in range(3):
        d = np.array([cells[a][str(s)]["segs"][i]["duty"] for s in SEEDS])
        e = np.array([cells[a][str(s)]["segs"][i]["err"] for s in SEEDS])
        per_seg.append(dict(mean=round(float(d.mean()), 3),
                            k_ge_half=int((d >= .5).sum()),
                            wilson=wilson(int((d >= .5).sum()), len(SEEDS)),
                            err_le01=int((e <= .01).sum()),
                            per_seed=[round(float(v), 3) for v in d]))
    d07 = np.array([cells[a][str(s)]["duty_07"] for s in SEEDS])
    k07 = int((d07 >= .5).sum())
    dist[a] = dict(segs=per_seg, duty07_mean=round(float(d07.mean()), 3),
                   duty07_k=k07, duty07_wilson=wilson(k07, len(SEEDS)),
                   duty07_per_seed=[round(float(v), 3) for v in d07])


def paired(a, b, seg):
    d = np.array([cells[a][str(s)]["segs"][seg]["duty"]
                  - cells[b][str(s)]["segs"][seg]["duty"] for s in SEEDS])
    return dict(mean=round(float(d.mean()), 3), pos=int((d > 0).sum()),
                neg=int((d < 0).sum()), per_seed=[round(float(v), 3) for v in d])


r1_pass = all(cells["hynohop_fb07"][str(s)]["segs"][0]["duty"]
              == cells["hynohop_fb"][str(s)]["segs"][0]["duty"] for s in SEEDS)
r2 = dict(fb07_vs_fb=paired("hynohop_fb07", "hynohop_fb", 2),
          fb07_vs_never=paired("hynohop_fb07", "hynohop", 2))
d1, d2 = r2["fb07_vs_fb"]["mean"], r2["fb07_vs_never"]["mean"]
if -.05 <= d1 <= .05 and d2 >= .05:
    r2v = "H-A WINDOW-LOCAL"
elif d1 <= -.10 and abs(d2) <= .05:
    r2v = "H-B CONTINUITY-NEEDED"
else:
    r2v = "MIXED"
r3 = dict(fb07_vs_never_seg1=paired("hynohop_fb07", "hynohop", 1),
          fb_vs_never_seg1=paired("hynohop_fb", "hynohop", 1),
          seg1_err_le01={a: dist[a]["segs"][1]["err_le01"] for a in ARMS})
r3_pass = (abs(r3["fb07_vs_never_seg1"]["mean"]) <= .05
           and r3["seg1_err_le01"]["hynohop_fb07"] == 16)

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, fb=FB, drive_on=4800,
                     entrain_mass=round(entrain_mass, 1),
                     source="l82/raw_l82.npz (verdict re-derive, zero reruns)"),
           anchors=dict(c0a_pass=bool(c0a), c0x_pass=bool(c0x),
                        c0p1_prefix=bool(c0p1), c0p2_first_div=bool(c0p2),
                        wired_dead=wired_dead,
                        first_div=first_div, dm=dm, prefix=prefix),
           distributions=dist, budget=budget,
           reads=dict(r1_parity=bool(r1_pass), r2=r2, r2_verdict=r2v,
                      r3=r3, r3_pass=bool(r3_pass),
                      r4_budget_ok=bool(budget["hynohop_fb07"]["ratio_mean"]
                                        < budget["hynohop_fb"]["ratio_mean"]),
                      r5_duty07={a: dict(k=dist[a]["duty07_k"],
                                         wilson=dist[a]["duty07_wilson"],
                                         mean=dist[a]["duty07_mean"]) for a in ARMS}),
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l82/results_l82.json", "w"), indent=1)
print(f"R1 parity {r1_pass} | R2 {r2v}: fb07-fb {d1} fb07-never {d2}")
print(f"R3 {r3_pass} | seg1 paired fb07-never {r3['fb07_vs_never_seg1']['mean']}"
      f" fb-never {r3['fb_vs_never_seg1']['mean']} | err_le01 {r3['seg1_err_le01']}")
print(f"R4 budget {json.dumps(budget)}")
print(f"R5 duty07 k/mean {json.dumps({a: [dist[a]['duty07_k'], dist[a]['duty07_mean']] for a in ARMS})}")
print(f"seg means {json.dumps({a: [dist[a]['segs'][i]['mean'] for i in range(3)] for a in ARMS})}")
print("verdict written -> l82/results_l82.json")
