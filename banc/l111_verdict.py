"""L111 verdict: C0B certification on stored raw_l109 BEFORE any fresh pin
(L85/L109 rule), then per-side duty07 cells on B9 + registered gates P0-P5.
PREREG l111/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK = 500, 500
SIGS = ("fL", "fR", "eL", "eR")
B7 = list(range(1101, 1117))
B8 = list(range(1201, 1217))
B9 = list(range(1301, 1317))
ARMS = ["full", "b65", "cut", "cut19"]
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z109 = np.load("l109/raw_l109.npz")
z111 = np.load("l111/raw_l111.npz")
r109 = json.load(open("l109/results_l109.json"))
ar = json.load(open("l111/anchors_run.json"))
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


def side_k(raw, a, seeds, pk="Ti"):
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        # l107/l109 rounding path EXACT: round per-seed to 3, then mean
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


# ---- Part 1: C0B on stored l109 (BEFORE any L111 pin) ----
def pooled_l109_form(a):
    """l109's EXACT pooled form: mean of ROUNDED per-batch means (rounding
    path matched; grand-mean over 32 differs in the 3rd decimal — the known
    L109 cert class)."""
    b7k = side_k(z109, a, B7)
    b8k = side_k(z109, a, B8)
    return dict(meanL=round((b7k["meanL"] + b8k["meanL"]) / 2, 3),
                meanR=round((b7k["meanR"] + b8k["meanR"]) / 2, 3))


c0b_fail = []
for a in ["full", "b65", "h65", "cut"]:
    want = r109["pooled"][a]
    got = side_k(z109, a, B7 + B8)
    pl = pooled_l109_form(a)
    for kk in ("kL", "kR"):
        if got[kk] != want[kk]:
            c0b_fail.append((a, kk, got[kk], want[kk]))
    for kk in ("meanL", "meanR"):
        if pl[kk] != want[kk]:
            c0b_fail.append((a, f"pooled_{kk}", pl[kk], want[kk]))
for a in ["full", "b65", "h65", "cut"]:
    for b, seeds in (("B7", B7), ("B8", B8)):
        want = r109["per_batch"][a][b]
        got = side_k(z109, a, seeds)
        for kk in ("kL", "kR", "meanL", "meanR"):
            if got[kk] != want[kk]:
                c0b_fail.append((a, b, kk, got[kk], want[kk]))
c0b_pass = not c0b_fail
print("C0B certification (stored l109, pooled + per-batch):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:5]}")

# ---- P0 anchors ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"])
print("P0 anchors vs raw_l109:", "PASS" if p0["c0a_pass"] else "FAIL",
      f"(max {p0['c0a_max']:.1e})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z111[f"af_{a}_{s}"]) for s in B9])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z111[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B9)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean,
          af_final_cut19=ar["af_final19"],
          cut19_staircase=abs(ar["af_final19"] - 0.10905611018339793))
print("P4", json.dumps(p4))

# ---- Part 2: per-side duty table on B9 (n=16/arm) ----
table = {}
for a in ARMS:
    t = side_k(z111, a, B9)
    lbL, ubL = wilson(t["kL"], 16)
    lbR, ubR = wilson(t["kR"], 16)
    t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
    table[a] = t
    print(f"{a:6s} Ti  kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} "
          f"[{lbL:.3f},{ubL:.3f}] | kR {t['kR']:2d}/16 meanR {t['meanR']:.3f} "
          f"[{lbR:.3f},{ubR:.3f}]")
tr_tab = {a: side_k(z111, a, B9, "Tr") for a in ARMS}
for a in ARMS:
    t = tr_tab[a]
    print(f"{a:6s} Tr  kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
          f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Gates ----
c19 = table["cut19"]
p1 = dict(
    transmitter_carried=bool(c19["kL"] >= 12 and c19["meanL"] >= .70),
    mass_placement_carried=bool(c19["kL"] <= 8 and c19["meanL"] <= .55),
    kL=c19["kL"], meanL=c19["meanL"])
p1["verdict"] = ("TRANSMITTER-carried" if p1["transmitter_carried"] else
                 ("MASS/PLACEMENT-carried" if p1["mass_placement_carried"]
                  else "MIXED (between registered bands)"))
p2 = dict(kR=c19["kR"], meanR=c19["meanR"],
          r_collapses_too=bool(c19["kR"] <= 4),
          r_stays_closure_like=bool(c19["kR"] >= 8))
p2["verdict"] = ("R-collapses-too (19 carry BOTH side actions)"
                 if p2["r_collapses_too"] else
                 ("R-stays (side actions dissociate by transmitter)"
                  if p2["r_stays_closure_like"] else "R intermediate"))
p3 = dict(cut_kL=table["cut"]["kL"], b65_kL=table["b65"]["kL"],
          b65_kR=table["b65"]["kR"])
p3["pass"] = bool(table["cut"]["kL"] >= 12 and table["b65"]["kL"] == 16
                  and table["b65"]["kR"] == 16)
p5 = dict(mass_split=dict(glut19=float(z111["mass_split"][0]),
                          other58=float(z111["mass_split"][1])),
          note="cord out-mass share of removed-19 vs kept-58 heavy "
               "(sums to heavy .5024); duty-form cells only per tick-136 "
               "amendment (2611.14498 LERS)")
print("P1", json.dumps(p1))
print("P2", json.dumps(p2))
print("P3", json.dumps(p3))
print("P5", json.dumps(p5))

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           table_b9=table, tr_b9=tr_tab, p1=p1, p2=p2, p3=p3, p5=p5,
           g_cut=ar["g_cut"], g_cut19=ar["g_cut19"])
json.dump(out, open("l111/results_l111.json", "w"), indent=1)
print("results_l111.json written")
