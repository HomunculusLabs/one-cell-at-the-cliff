"""L107 addendum: the registered FlyHack-style shifted-window stability read
for the k>=12 arms (b65, h65) — my in-verdict stub was vacuous, this computes
it — plus the per-side ladder table (l65 -> cut -> closure) that the
both-sides cell hides (L46 lesson).
"""
import json

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
SIGS = ("fL", "fR", "eL", "eR")
B4 = list(range(801, 817))
SHIFT = 250

z107 = np.load("l107/raw_l107.npz")
z94 = np.load("l94/raw_l94.npz")
TS0 = np.arange(499, WIN, 10)
TS = TS0 + SHIFT
TS = TS[(TS - 499 >= 0) & (TS + 1 <= WIN)]


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(raw, a, s, pk, ts):
    tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN] for c in SIGS}
    fL, fR, eL, eR = (tr[c] for c in SIGS)
    SL = np.full(len(ts), np.nan)
    SR = np.full(len(ts), np.nan)
    for i, t in enumerate(ts):
        SL[i] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[i] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    return SL, SR


def duty_shifted(raw, a, s, pk):
    SL, SR = s_arrays(raw, a, s, pk, TS)
    q07 = np.zeros(len(TS), bool)
    for a0_, b0, f in SEGB:
        if f == 0.7:
            q07 |= (TS >= a0_ + MEAS0) & (TS < b0)
    L = SL[q07] >= .25
    R = SR[q07] >= .25
    return (round(float(np.nanmean(L & R)), 3),
            round(float(np.nanmean(L)), 3), round(float(np.nanmean(R)), 3))


out = {}
for raw, tag, arms in ((z107, "l107", ["b65", "h65", "cut"]),
                       (z94, "l94cfn", ["cfn"])):
    for a in arms:
        name = f"{tag}:{a}"
        rows = [duty_shifted(raw, a, s, "Ti") for s in B4]
        both = np.array([r[0] for r in rows])
        out[name] = dict(
            duty07_shifted=round(float(both.mean()), 3),
            k_shifted=int((both >= .5).sum()),
            dL=round(float(np.mean([r[1] for r in rows])), 3),
            dR=round(float(np.mean([r[2] for r in rows])), 3))

print("shifted(+250 steps) Ti reads:")
for k_, v in out.items():
    print(f"  {k_:12s} duty07 {v['duty07_shifted']:.3f} k {v['k_shifted']}/16 "
          f"L {v['dL']:.3f} R {v['dR']:.3f}")
json.dump(out, open("l107/addendum_shift.json", "w"), indent=1)
