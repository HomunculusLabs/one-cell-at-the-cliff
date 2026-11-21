"""L68 verdict: G1/G2/G3 reads from l68/raw_l68.npz (no reruns).

Fixes the probe's swapped dom_freq unpack (f/ratio labels crossed — L35
class, caught by sanity-reading magnitudes; raw rollouts unaffected).
Anchor decomposition: mm bit-identical 0.0 (state exact); pooled pool
means 2-6e-08 (float32 sum-order, concat vs row order — disclosed).
"""
import json

import numpy as np

SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG, BLK, MEAS0, WIN, DT = 2000, 500, 500, 6000, 0.01
SEEDS = [11, 22, 33]
GROUP = ["open", "hyb03", "hyb01"]
LOCK_TOL = 0.10
PAIRS = ("Ti", "Tr")
SIGS = ("fL", "fR", "eL", "eR")
TS = np.arange(WIN)


def dom_freq(x, lo=0.3):
    z = x - x.mean()
    ps = np.abs(np.fft.rfft(z)) ** 2
    fr = np.fft.rfftfreq(len(z), DT)
    band = (fr >= lo) & (fr <= 10)
    pb, fb = ps[band], fr[band]
    i = int(np.argmax(pb))
    f_hat = fb[i]
    if 0 < i < len(pb) - 1:
        y0, y1, y2 = pb[i - 1], pb[i], pb[i + 1]
        den = y0 - 2 * y1 + y2
        if abs(den) > 1e-30:
            f_hat = fb[i] + 0.5 * (y0 - y2) / den * (fb[1] - fb[0])
    ratio = float(pb.max() / max(np.median(pb), 1e-30))
    return float(f_hat), ratio


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


z = np.load("l68/raw_l68.npz")
scan = json.load(open("l68/scan_l68.json"))

out = dict(anchor=None, open={}, arms={}, gates={})


def s_arrays(a, s, pk):
    fL, fR = z[f"{a}_s{s}_{pk}_fL"], z[f"{a}_s{s}_{pk}_fR"]
    eL, eR = z[f"{a}_s{s}_{pk}_eL"], z[f"{a}_s{s}_{pk}_eR"]
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in range(499, WIN):
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    return SL, SR


# anchor decomposition (mm exact / pools ulp)
dec = {}
for s in SEEDS:
    dec[str(s)] = dict(
        mm=float(np.abs(z[f"l65conv_s{s}_mm"] - np.load("l65/raw_l65.npz")[f"B_s{s}_mm"]).max()))
out["anchor"] = dec

# open arm: rhythm + S (fixed unpack)
for s in SEEDS:
    f_hat, ratio = dom_freq(z[f"open_s{s}_mm"])
    SL, SR = s_arrays("open", s, "Ti")
    out["open"][str(s)] = dict(
        f=round(f_hat, 3), ratio=round(ratio, 1),
        S_Ti_L=round(float(np.nanmedian(SL[1000:])), 3),
        S_Ti_R=round(float(np.nanmedian(SR[1000:])), 3))
out["gates"]["open_gate"] = all(v["ratio"] > 100 for v in out["open"].values()) and \
    all(max(v["S_Ti_L"], v["S_Ti_R"]) > 0.40 for v in out["open"].values())

# per-arm seg table
for a in ("hyb03", "hyb01"):
    out["arms"][a] = {}
    for s in SEEDS:
        mm = z[f"{a}_s{s}_mm"]
        blocks = []
        for b in range(WIN // BLK):
            f_hat, ratio = dom_freq(mm[b * BLK:(b + 1) * BLK])
            seg = next(i for i, (a0, b0, _) in enumerate(SEGB)
                       if a0 <= b * BLK < b0)
            blocks.append(dict(b=b, f=round(f_hat, 3), ratio=round(ratio, 1),
                               seg=seg, target=SEGB[seg][2],
                               err=round(abs(f_hat - SEGB[seg][2]), 3)))
        rows = []
        for pk in PAIRS:
            SL, SR = s_arrays(a, s, pk)
            for si, (a0, b0, tg) in enumerate(SEGB):
                bl = [x for x in blocks if x["seg"] == si]
                err = round(float(np.mean([x["err"] for x in bl[1:]])), 4)
                q = (TS >= a0 + MEAS0) & (TS < b0)
                both = (SL[TS[q]] >= 0.25) & (SR[TS[q]] >= 0.25)
                rows.append(dict(
                    pair=pk, seg=si, target=tg, err=err,
                    duty=round(float(np.nanmean(both)), 3),
                    SL=round(float(np.nanmedian(SL[TS[q]])), 3),
                    SR=round(float(np.nanmedian(SR[TS[q]])), 3),
                    f_seg=round(dom_freq(mm[a0:b0])[0], 3)))
        # arm-seed summary on primary pair Ti
        SLT, SRT = s_arrays(a, s, "Ti")
        q07 = np.zeros(WIN, bool)
        qall = np.zeros(WIN, bool)
        for a0, b0, f in SEGB:
            qall |= (TS >= a0 + MEAS0) & (TS < b0)
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        fast_err = round(float(np.mean(
            [x["err"] for x in blocks if x["seg"] == 1][1:])), 4)
        slow_err = round(float(np.mean(
            [x["err"] for x in blocks if x["seg"] != 1][1:])), 4)
        out["arms"][a][str(s)] = dict(
            blocks=blocks, rows=rows, fast_err=fast_err, slow_err=slow_err,
            duty_07=round(float(np.nanmean(
                (SLT[TS[q07]] >= .25) & (SRT[TS[q07]] >= .25))), 3),
            duty_all=round(float(np.nanmean(
                (SLT[TS[qall]] >= .25) & (SRT[TS[qall]] >= .25))), 3),
            mm_amp=round(float(mm.max() - mm.min()), 3))

# gate reads
best = min(("hyb03", "hyb01"),
           key=lambda a: np.mean([out["arms"][a][str(s)]["fast_err"]
                                  for s in SEEDS]))
fast_ok = sum(out["arms"][best][str(s)]["fast_err"] <= LOCK_TOL
              for s in SEEDS)
slow_ok = sum(out["arms"][best][str(s)]["slow_err"] <= LOCK_TOL
              for s in SEEDS)
duty07 = [out["arms"][best][str(s)]["duty_07"] for s in SEEDS]
duty_ok = sum(d >= 0.30 for d in duty07)
out["gates"].update(
    best_arm=best,
    G1_entrains=bool(fast_ok >= 2 and slow_ok >= 2),
    G1_fast_ok=fast_ok, G1_slow_ok=slow_ok,
    G2_structure=bool(duty_ok >= 2), G2_duty07=duty07, G2_ok_n=duty_ok,
    G3_af_asserted=True, G3_dm=float(scan["g3_dm"]),
    G3_dm_lands=bool(scan["g3_dm"] > 0.0))
if out["gates"]["G1_entrains"] and out["gates"]["G2_structure"]:
    out["gates"]["verdict"] = "REPLICATES"
elif out["gates"]["G1_entrains"]:
    out["gates"]["verdict"] = "ENTRAINS-NO-STRUCTURE"
else:
    out["gates"]["verdict"] = "NO-ENTRAIN"

json.dump(out, open("l68/results_l68.json", "w"), indent=1)
g = out["gates"]
print(f"anchor mm-exact: {all(v['mm'] == 0.0 for v in dec.values())}")
print(f"open: {out['open']}")
print(f"best arm {best} | fast_err "
      f"{[out['arms'][best][str(s)]['fast_err'] for s in SEEDS]} ok {fast_ok}/3 "
      f"| slow_err {[out['arms'][best][str(s)]['slow_err'] for s in SEEDS]} "
      f"ok {slow_ok}/3")
print(f"duty_07 {duty07} ok {duty_ok}/3 | dm {g['G3_dm']:.3f}")
print(f"G1 {g['G1_entrains']} G2 {g['G2_structure']} -> VERDICT {g['verdict']}")
