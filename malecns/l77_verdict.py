"""L77 verdict: full analysis re-derived from raw_l77.npz checkpoint
(rollout crash was analysis-only: dom_freq tuple-vs-float, l59 analysis form
over l66's single-value dom_freq; L45a rule — zero reruns). Also diagnoses
C0P first_div values from the checkpoint. Reads identical to PREREG.
"""
import json
import math

import numpy as np

WIN = 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
BLK = 500
MEAS0 = 500
SEEDS = [11, 22, 33] + list(range(101, 114))
ANCHOR_SEEDS = [11, 22, 33]
DT = 0.01
LOCK_TOL = 0.10
FB = dict(gfb=.1, delay=5, sign=-1.0)
ARMS = ["hynohop", "hybrid", "hynohop_fb", "hybrid_fb"]
FB_ARMS = ["hynohop_fb", "hybrid_fb"]
TWINS = {"hynohop_fb": "hynohop", "hybrid_fb": "hybrid"}
SIGS = ("fL", "fR", "eL", "eR")

z = np.load("l77/raw_l77.npz")
z59 = np.load("l59/raw_l59.npz")
z66 = np.load("l66/raw_l66.npz")


def mm(a, s):
    return z[f"mm_{a}_{s}"]


def tr(a, s, c):
    return z[f"{c}_{a}_{s}"]


# ---------- anchors re-derived ----------
c0a, c0b, c0x = {}, {}, {}
for s in ANCHOR_SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(mm("hynohop", s) - z59[f"mm_hynohop_{s}"]).max())
    c0b[f"mm_{s}"] = float(np.abs(mm("hybrid", s) - z59[f"mm_hybrid_{s}"]).max())
    c0x[f"mm_{s}"] = float(np.abs(
        mm("hynohop_fb", s) - z66[f"mm_g01_d05_m_{s}"]).max())
    for c in SIGS:
        c0a[f"{c}_{s}"] = float(np.abs(
            tr("hynohop", s, c) - z59[f"{c}_hynohop_{s}"]).max())
        c0b[f"{c}_{s}"] = float(np.abs(
            tr("hybrid", s, c) - z59[f"{c}_hybrid_{s}"]).max())
        c0x[f"{c}_{s}"] = float(np.abs(
            tr("hynohop_fb", s, c) - z66[f"{c}_g01_d05_m_{s}"]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0b_pass = all(v == 0.0 for v in c0b.values())
c0x_pass = all(v == 0.0 for v in c0x.values())

dm, first_div = {}, {}
for fb in FB_ARMS:
    twin = TWINS[fb]
    for s in SEEDS:
        diffs = np.concatenate(
            [np.abs(mm(fb, s) - mm(twin, s))]
            + [np.abs(tr(fb, s, c) - tr(twin, s, c)) for c in SIGS])
        fd = int(np.argmax(diffs > 0)) if (diffs > 0).any() else -1
        first_div[f"{fb}_{s}"] = int(fd % WIN) if fd >= 0 else -1
        dm[f"{fb}_{s}"] = round(float(diffs.max()), 5)
wired_dead = [k for k, v in dm.items() if v == 0.0]
fd_counts = {}
for fb in FB_ARMS:
    vals = [first_div[f"{fb}_{s}"] for s in SEEDS]
    fd_counts[fb] = {v: vals.count(v) for v in sorted(set(vals))}
c0p_ok = (not wired_dead
          and all(first_div[f"{fb}_{s}"] == FB["delay"]
                  for fb in FB_ARMS for s in SEEDS))
print(f"C0a {c0a_pass} C0b {c0b_pass} C0x {c0x_pass} C0P {c0p_ok} "
      f"wired_dead {len(wired_dead)}")
print(f"first_div histogram {json.dumps(fd_counts)}")


def dom_freq(x, lo=0.3):
    zc = x - x.mean()
    ps = np.abs(np.fft.rfft(zc)) ** 2
    fr = np.fft.rfftfreq(len(zc), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb_ = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb_[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb_[i] + 0.5 * (y0 - y2) / den * (fb_[1] - fb_[0])
    return float(f_hat)


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


TS = np.arange(499, WIN, 10)
SM = {}


def s_arrays(a, s):
    if (a, s) in SM:
        return SM[(a, s)]
    fL, fR, eL, eR = (tr(a, s, c) for c in SIGS)
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
            f_seg = dom_freq(mm(a, str(s))[a0_:b0])
            bl_errs, ttl = [], None
            for b in range(WIN // BLK):
                if a0_ <= b * BLK < b0 and b * BLK > a0_:
                    e = abs(dom_freq(mm(a, str(s))[b * BLK:(b + 1) * BLK]) - tg)
                    bl_errs.append(e)
                    if ttl is None and e <= LOCK_TOL:
                        ttl = b * BLK - a0_
            rows.append(dict(
                duty=round(float(np.nanmean(both)), 3),
                SL=wmed(lo, hi, SL), SR=wmed(lo, hi, SR),
                f=round(f_seg, 3),
                err=round(float(np.mean(bl_errs)), 4), ttl=ttl))
        qall = np.zeros(len(TS), bool)
        q07 = np.zeros(len(TS), bool)
        for a0_, b0, f in SEGB:
            qall |= (TS >= a0_ + MEAS0) & (TS < b0)
            if f == 0.7:
                q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
        cells[a][str(s)] = dict(
            segs=rows,
            duty_all=round(float(np.nanmean(
                (SL[TS[qall]] >= .25) & (SR[TS[qall]] >= .25))), 3),
            duty_07=round(float(np.nanmean(
                (SL[TS[q07]] >= .25) & (SR[TS[q07]] >= .25))), 3))

# ---------- P3 budget from stored mA ----------
ph = 0.0
for _ in range(400):
    ph += 2 * math.pi * 0.7 * DT


def target(k):
    for a_, b_, f in SEGB:
        if a_ <= k < b_:
            return f
    return SEGB[-1][2]


PHI = np.empty(WIN)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
on_steps = np.where((np.isclose(np.zeros(0), 0)))[0]  # placeholder, rebuilt below
AMPA = np.zeros(WIN)
for seg0, _, f in SEGB:
    if f != 0.7:
        AMPA[seg0:seg0 + 2000] = 0.3
        continue
    c = 0
    while seg0 + c * 900 < seg0 + 2000:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + 2000)] = 0.3
        c += 1
on_steps = np.where(AMPA > 0)[0]
sin_on = np.array([0.5 + 0.5 * math.sin(PHI[k]) for k in on_steps])
entrain_mass = float(0.3 * sin_on.sum())
budget = {}
for fb in FB_ARMS:
    em = [float(FB["gfb"] * z[f"mA_{fb}_{s}"][:WIN - FB["delay"]].sum())
          for s in SEEDS]
    amps = [float(z[f"mA_{fb}_{s}"][:WIN - FB["delay"]].mean()) for s in SEEDS]
    budget[fb] = dict(echo_mass_mean=round(float(np.mean(em)), 4),
                      echo_mass_min=round(float(np.min(em)), 4),
                      echo_mass_max=round(float(np.max(em)), 4),
                      entrain_mass=round(entrain_mass, 1),
                      ratio_mean=round(float(np.mean(em)) / entrain_mass, 4),
                      echo_amp_mean=round(float(np.mean(amps)) * FB["gfb"], 5))
print("P3 " + json.dumps(budget))


def wilson(k, nn, z_=1.96):
    p = k / nn
    den = 1 + z_ * z_ / nn
    c = (p + z_ * z_ / (2 * nn)) / den
    hw = z_ * math.sqrt(p * (1 - p) / nn + z_ * z_ / (4 * nn * nn)) / den
    return round(c - hw, 3), round(c + hw, 3)


dist = {}
for a in ARMS:
    pooled = np.array([cells[a][str(s)]["duty_all"] for s in SEEDS])
    seg1 = np.array([cells[a][str(s)]["segs"][1]["duty"] for s in SEEDS])
    seg1e = np.array([cells[a][str(s)]["segs"][1]["err"] for s in SEEDS])
    d07 = np.array([cells[a][str(s)]["duty_07"] for s in SEEDS])
    k_gate = int((pooled >= .5).sum())
    dist[a] = dict(
        pooled=[round(float(v), 3) for v in pooled],
        pooled_mean=round(float(pooled.mean()), 3),
        p_ge_half=k_gate, p_ge_half_wilson=wilson(k_gate, len(SEEDS)),
        seg1=[round(float(v), 3) for v in seg1],
        seg1_mean=round(float(seg1.mean()), 3),
        seg1_err_le01=int((seg1e <= .01).sum()),
        seg1_err=[round(float(v), 4) for v in seg1e],
        seg_err_means=[round(float(np.mean(
            [cells[a][str(s)]["segs"][i]["err"] for s in SEEDS])), 4)
            for i in range(3)],
        duty07_mean=round(float(d07.mean()), 3),
        duty07=[round(float(v), 3) for v in d07],
        seg_SL_means=[round(float(np.mean([
            cells[a][str(s)]["segs"][i]["SL"] for s in SEEDS
            if cells[a][str(s)]["segs"][i]["SL"] is not None])), 3)
            for i in range(3)],
        seg_SR_means=[round(float(np.mean([
            cells[a][str(s)]["segs"][i]["SR"] for s in SEEDS
            if cells[a][str(s)]["segs"][i]["SR"] is not None])), 3)
            for i in range(3)])

flips = {}
for fb in FB_ARMS:
    twin = TWINS[fb]
    up = down = both_up = both_dn = 0
    per_seed = []
    for s in SEEDS:
        v_fb = cells[fb][str(s)]["duty_all"]
        v_tw = cells[twin][str(s)]["duty_all"]
        per_seed.append(dict(seed=s, twin=v_tw, fb=v_fb,
                             d=round(v_fb - v_tw, 3)))
        if v_fb >= .5 and v_tw < .5:
            up += 1
        elif v_fb < .5 and v_tw >= .5:
            down += 1
        elif v_fb >= .5:
            both_up += 1
        else:
            both_dn += 1
    flips[fb] = dict(up=up, down=down, both_up=both_up, both_down=both_dn,
                     per_seed=per_seed)

anatomy = {}
for fb in FB_ARMS:
    sl_owned = sr_owned = both_below = 0
    miss_rows = []
    for s in SEEDS:
        cell = cells[fb][str(s)]
        if cell["duty_all"] >= .5:
            continue
        fails = []
        for si, row in enumerate(cell["segs"]):
            if row["duty"] < .5:
                fails.append(si)
                sl_low = (row["SL"] is not None and row["SL"] < .25)
                sr_low = (row["SR"] is not None and row["SR"] < .25)
                if sl_low and sr_low:
                    both_below += 1
                elif sl_low:
                    sl_owned += 1
                elif sr_low:
                    sr_owned += 1
        miss_rows.append(dict(seed=s, duty=cell["duty_all"], fail_segs=fails,
                              seg_duties=[r["duty"] for r in cell["segs"]],
                              seg_SL=[r["SL"] for r in cell["segs"]],
                              seg_SR=[r["SR"] for r in cell["segs"]]))
    tot = sl_owned + sr_owned + both_below
    anatomy[fb] = dict(
        n_miss=len(miss_rows), sl_owned=sl_owned, sr_owned=sr_owned,
        both_below=both_below,
        sl_share=round(sl_owned / tot, 3) if tot else None, misses=miss_rows)

preds = {}
for fb, label in (("hybrid_fb", "primary"), ("hynohop_fb", "secondary")):
    k = dist[fb]["p_ge_half"]
    lock_ok = dist[fb]["seg1_err_le01"] >= 12
    preds[f"P1_{label}"] = dict(k=k, n=16, biased=bool(k >= 11),
                                wilson=dist[fb]["p_ge_half_wilson"],
                                lock_le01=dist[fb]["seg1_err_le01"],
                                lock_ok=lock_ok,
                                verdict=("BIASED-LEVER" if k >= 11 and lock_ok
                                         else ("TOXIC-BIASED" if k >= 11
                                               else "REAL-NEGATIVE-or-null")))
preds["P2_lock"] = {a: dict(le01=dist[a]["seg1_err_le01"],
                            seg_err_means=dist[a]["seg_err_means"])
                    for a in ARMS}
preds["P4_anatomy"] = {fb: dict(n_miss=anatomy[fb]["n_miss"],
                                sl_share=anatomy[fb]["sl_share"])
                       for fb in FB_ARMS}

out = dict(meta=dict(seeds=SEEDS, arms=ARMS, fb=FB, drive_on=4800,
                     entrain_mass=round(entrain_mass, 1),
                     source="raw_l77.npz (analysis re-derived post crash)"),
           anchors=dict(c0a_pass=c0a_pass, c0b_pass=c0b_pass, c0x_pass=c0x_pass,
                        c0p_ok=bool(c0p_ok), fd_histogram=fd_counts,
                        c1=True,  # verified in-run pre-crash (run.out)
                        wired_dead=wired_dead,
                        first_div=first_div, dm=dm),
           distributions=dist, flips=flips, budget=budget,
           anatomy=anatomy, predictions=preds,
           cells={a: {str(s): cells[a][str(s)] for s in SEEDS} for a in ARMS})
json.dump(out, open("l77/results_l77.json", "w"), indent=1)
print("P1 " + json.dumps({k: v for k, v in preds.items()
                          if k.startswith("P1")}))
print("k    " + json.dumps({a: dist[a]["p_ge_half"] for a in ARMS}))
print("mean " + json.dumps({a: dist[a]["pooled_mean"] for a in ARMS}))
print("d07  " + json.dumps({a: dist[a]["duty07_mean"] for a in ARMS}))
print("seg1 " + json.dumps({a: dist[a]["seg1_mean"] for a in ARMS}))
print("flips " + json.dumps({fb: {k: v for k, v in flips[fb].items()
                                  if k != "per_seed"} for fb in FB_ARMS}))
print("P4 " + json.dumps(preds["P4_anatomy"]))
print("SL means " + json.dumps({a: dist[a]["seg_SL_means"] for a in ARMS}))
print("SR means " + json.dumps({a: dist[a]["seg_SR_means"] for a in ARMS}))
print("done -> l77/results_l77.json")
