"""L109 verdict: C0B certification on stored raw_l107 BEFORE any fresh pin
(L85 rule), then per-side ladder reads from raw_l109.npz. PREREG gates.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK = 500, 500
SIGS = ("fL", "fR", "eL", "eR")
B4 = list(range(801, 817))
B7 = list(range(1101, 1117))
B8 = list(range(1201, 1217))
FRESH = B7 + B8
L94_B56 = list(range(901, 917)) + list(range(1001, 1017))
ARMS = ["full", "b65", "h65", "cut"]
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054  # full-precision 95%

z94 = np.load("l94/raw_l94.npz")
z107 = np.load("l107/raw_l107.npz")
z109 = np.load("l109/raw_l109.npz")
r107 = json.load(open("l107/results_l107.json"))
ar = json.load(open("l109/anchors_run.json"))
SM = {}


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in SM:
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN] for c in SIGS}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr["fL"][t - 499:t + 1], tr["eL"][t - 499:t + 1])
            SR[t] = S_of(tr["fR"][t - 499:t + 1], tr["eR"][t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


def dom_ratio(x):
    zz = x - x.mean()
    ps = np.abs(np.fft.rfft(zz)) ** 2
    fr = np.fft.rfftfreq(len(zz), DT)
    band = (fr >= 0.3) & (fr <= 10)
    return float(ps[band].max() / max(np.median(ps[band]), 1e-30))


def side_k(raw, a, seeds, pk="Ti"):
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        # l107 rounding path EXACT: round per-seed to 3, then mean (C0B-safe)
        L.append(round(float(np.nanmean(SL[TS[q07]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[q07]] >= .25)), 3))
    L, R = np.array(L), np.array(R)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---------------- Part 1: C0B on stored l107 (BEFORE any L109 pin) ----------
c0b_fail = []
for a in ARMS:
    want_k = r107["k_ti"][a]
    want_m = r107["m_ti"][a]
    want_tr = r107["m_tr"][a]
    got = side_k(z107, a, B4)
    got_tr = side_k(z107, a, B4, "Tr")
    for kk, wv in (("meanL", want_m["dL"]), ("meanR", want_m["dR"])):
        if got[kk] != wv:
            c0b_fail.append((a, kk, got[kk], wv))
    for kk, wv in (("meanL", want_tr["dL"]), ("meanR", want_tr["dR"])):
        if got_tr[kk] != wv:
            c0b_fail.append((a, f"Tr_{kk}", got_tr[kk], wv))
c0b_pass = not c0b_fail
print("C0B certification (stored l107 B4 means):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:4]}")
# k-side pins from PREREG table (derived from raw_l107 pre-run)
PREREG_K = {"full": (3, 5), "b65": (16, 16), "h65": (16, 16), "cut": (16, 0)}
k_pin_fail = [(a, side_k(z107, a, B4)[kk], PREREG_K[a][i])
              for i, kk in ((0, "kL"), (1, "kR")) for a in ARMS
              if side_k(z107, a, B4)[kk] != PREREG_K[a][i]]
print("PREREG k-side pins:", "PASS" if not k_pin_fail else f"FAIL {k_pin_fail}")

# ---------------- Part 2: C1 af gates ----------------
af_mean = {a: round(float(np.mean([float(z109[f"af_{a}_{s}"]) for s in FRESH])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z109[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS for s in FRESH)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
c1 = dict(af_range_ok=af_range_ok, b65_band=bool(b65_band), af_mean=af_mean)
print("C1", c1)

# ---------------- Part 3: fresh per-side ladder ----------------
per_batch = {a: {"B7": side_k(z109, a, B7), "B8": side_k(z109, a, B8)}
             for a in ARMS}
pooled = {}
for a in ARMS:
    b7k, b8k = per_batch[a]["B7"], per_batch[a]["B8"]
    kL, kR = b7k["kL"] + b8k["kL"], b7k["kR"] + b8k["kR"]
    lbL, ubL = wilson(kL, 32)
    lbR, ubR = wilson(kR, 32)
    pooled[a] = dict(kL=kL, kR=kR, lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR,
                     meanL=round((b7k["meanL"] + b8k["meanL"]) / 2, 3),
                     meanR=round((b7k["meanR"] + b8k["meanR"]) / 2, 3))
p1 = dict(
    cut_L=bool(pooled["cut"]["kL"] >= 24),
    cut_R=bool(pooled["cut"]["kR"] <= 8),
    b65=bool(pooled["b65"]["kL"] >= 30 and pooled["b65"]["kR"] >= 30),
    h65=bool(pooled["h65"]["kL"] >= 30 and pooled["h65"]["kR"] >= 30),
    full=bool(pooled["full"]["kL"] <= 11 and pooled["full"]["kR"] <= 11))
p1_law = all(p1.values())
p2 = dict(
    cutL_gt_fullL=bool(pooled["cut"]["meanL"] > pooled["full"]["meanL"]),
    b65R_gt_cutR=bool(pooled["b65"]["meanR"] > pooled["cut"]["meanR"]),
    cutR_lt_fullR=bool(pooled["cut"]["meanR"] < pooled["full"]["meanR"]),
    means={a: (pooled[a]["meanL"], pooled[a]["meanR"]) for a in ARMS})
# P3 batch-stability (descriptive; per-batch bars = pooled prop x 16)
PB_BAR = {"cut_L": 12, "cut_R": 4, "b65_L": 15, "b65_R": 15,
          "h65_L": 15, "h65_R": 15, "full_L": 5, "full_R": 5}


def p3_ok(a, side, v):
    bar = PB_BAR[f"{a}_{side}"]
    return v <= bar if (a == "full" or (a == "cut" and side == "R")) else v >= bar


p3 = {}
for a in ARMS:
    for side in ("L", "R"):
        vals = [per_batch[a][b][f"k{side}"] for b in ("B7", "B8")]
        p3[f"{a}_{side}"] = dict(B7=vals[0], B8=vals[1], bar=PB_BAR[f"{a}_{side}"],
                                 both=bool(p3_ok(a, side, vals[0])
                                           and p3_ok(a, side, vals[1])))
# ---------------- Part 4: zero-rollout l94 stored base axis ----------------
base56 = side_k(z94, "cfn", L94_B56)
base56_w = dict(kL=base56["kL"], n=32,
                lbL=wilson(base56["kL"], 32)[0], lbR=wilson(base56["kR"], 32)[0],
                kR=base56["kR"], meanL=base56["meanL"], meanR=base56["meanR"])

# lock descriptive
lock = {a: int(sum(all(dom_ratio(z109[f"mm_{a}_{s}"][s0:s0 + 2000][:WIN]) >= 10
                       for s0, _, _ in SEGB) for s in FRESH)) for a in ARMS}
tr_fresh = {a: side_k(z109, a, FRESH, "Tr") for a in ARMS}

verdict = (f"P1 {'LAW' if p1_law else 'DRAW'} " +
           " ".join(f"{k}:{'y' if v else 'n'}" for k, v in p1.items()) +
           f" | pooled cut L {pooled['cut']['kL']}/32 R {pooled['cut']['kR']}/32"
           f" | b65 {pooled['b65']['kL']}/{pooled['b65']['kR']}"
           f" h65 {pooled['h65']['kL']}/{pooled['h65']['kR']}"
           f" full {pooled['full']['kL']}/{pooled['full']['kR']}")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:4], k_pin_fail=k_pin_fail,
           c0a=dict(passed=ar["c0a_pass"], max=ar["c0a_max"]),
           g_cut=ar["g_cut"], c1=c1, per_batch=per_batch, pooled=pooled,
           p1=p1, p1_law=p1_law, p2=p2, p3=p3, base_l94_B56=base56_w,
           lock=lock, tr_fresh=tr_fresh, verdict=verdict)
json.dump(out, open("l109/results_l109.json", "w"), indent=1)
print("C0A", ar["c0a_pass"], "| k-pins", not k_pin_fail)
for a in ARMS:
    pb = per_batch[a]
    print(f"{a:5s} B7 L{pb['B7']['kL']:2d} R{pb['B7']['kR']:2d} "
          f"(mL {pb['B7']['meanL']:.3f} mR {pb['B7']['meanR']:.3f}) | "
          f"B8 L{pb['B8']['kL']:2d} R{pb['B8']['kR']:2d} "
          f"(mL {pb['B8']['meanL']:.3f} mR {pb['B8']['meanR']:.3f}) | "
          f"pooled L{pooled[a]['kL']:2d}/32 R{pooled[a]['kR']:2d}/32 "
          f"lbL {pooled[a]['lbL']:.3f} lbR {pooled[a]['lbR']:.3f}")
print("P2", {k: v for k, v in p2.items() if k != "means"})
print("P3 batch-stable axes:", [k for k, v in p3.items() if v["both"]],
      "| batch-drawn:", [k for k, v in p3.items() if not v["both"]])
print("l94 stored B5/B6 base axis:", base56_w)
print("VERDICT:", verdict)
