"""L113 verdict: C0B certification on stored raw_l111 BEFORE any fresh pin
(L85/L109 rule), then per-side duty07 cells on B10 (5 arms) + P0-P6 gates.
PREREG l113/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK = 500, 500
SIGS = ("fL", "fR", "eL", "eR")
B9 = list(range(1301, 1317))
B10 = list(range(1401, 1417))
ARMS = ["full", "b65", "cut", "cut19", "cut58"]
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z111 = np.load("l111/raw_l111.npz")
z113 = np.load("l113/raw_l113.npz")
r111 = json.load(open("l111/results_l111.json"))
ar = json.load(open("l113/anchors_run.json"))
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


def per_seed(raw, a, seeds, pk="Ti"):
    """Rounded per-seed duty values (the l109/l111 rounding-path atom)."""
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        L.append(round(float(np.nanmean(SL[TS[q07]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[q07]] >= .25)), 3))
    return np.array(L), np.array(R)


def side_k(raw, a, seeds, pk="Ti"):
    L, R = per_seed(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---- Part 1: C0B on stored l111 (BEFORE any L113 pin) ----
c0b_fail = []
for a in ["full", "b65", "cut", "cut19"]:
    want = r111["table_b9"][a]
    got = side_k(z111, a, B9)
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            c0b_fail.append((a, kk, got[kk], want[kk]))
    want_tr = r111["tr_b9"][a]
    got_tr = side_k(z111, a, B9, "Tr")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got_tr[kk] != want_tr[kk]:
            c0b_fail.append((a, f"tr_{kk}", got_tr[kk], want_tr[kk]))
c0b_pass = not c0b_fail
print("C0B certification (stored l111, Ti+Tr tables):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:5]}")

# ---- P0 anchors (gate booleans ONLY in the aggregate; c0a_max 0.0 is a
# diagnostic magnitude, not a gate — L59 anchor-key class, caught in v1 print)
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0_pass = bool(p0["c0a_pass"] and p0["g_cut_stored_exact"]
               and p0["g_cut19_stored_exact"])
p0["pass"] = p0_pass
print("P0 anchors vs raw_l111:", "PASS" if p0_pass else "FAIL",
      f"(max {p0['c0a_max']:.1e}, g_cut exact {p0['g_cut_stored_exact']}, "
      f"g_cut19 exact {p0['g_cut19_stored_exact']})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z113[f"af_{a}_{s}"]) for s in B10])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z113[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B10)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean,
          af_final_cut58=ar["af_final58"],
          cut58_staircase=abs(ar["af_final58"] - 0.10905611018339793))
print("P4", json.dumps(p4))

# ---- Part 2: per-side duty table on B10 (n=16/arm) ----
table = {}
for a in ARMS:
    t = side_k(z113, a, B10)
    lbL, ubL = wilson(t["kL"], 16)
    lbR, ubR = wilson(t["kR"], 16)
    t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
    table[a] = t
    print(f"{a:6s} Ti  kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} "
          f"[{lbL:.3f},{ubL:.3f}] | kR {t['kR']:2d}/16 meanR {t['meanR']:.3f} "
          f"[{lbR:.3f},{ubR:.3f}]")
tr_tab = {a: side_k(z113, a, B10, "Tr") for a in ARMS}
for a in ARMS:
    t = tr_tab[a]
    print(f"{a:6s} Tr  kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
          f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- P1 (cut58 Ti_L mirror test) ----
c58 = table["cut58"]
p1 = dict(
    mass_placement_carried=bool(c58["kL"] >= 12 and c58["meanL"] >= .70),
    glut_alone=bool(c58["kL"] <= 8 and c58["meanL"] <= .55),
    kL=c58["kL"], meanL=c58["meanL"])
p1["verdict"] = ("MASS/PLACEMENT-carried residual (58 also restore L)"
                 if p1["mass_placement_carried"] else
                 ("GLUT-ALONE (L-restore is 19-specific)"
                  if p1["glut_alone"] else "MIXED (between registered bands)"))

# ---- P2 (cut58 Ti_R, paired vs full-B10) ----
ful = table["full"]
p2 = dict(kR=c58["kR"], meanR=c58["meanR"], full_kR=ful["kR"],
          full_meanR=ful["meanR"],
          r_killed_by_58=bool(c58["kR"] <= 4 and c58["meanR"] <= .30))
abs_leg = c58["kR"] >= 8
paired_leg = bool(c58["kR"] >= ful["kR"] and c58["meanR"] >= ful["meanR"] - .10)
p2["r_stays"] = bool(abs_leg or paired_leg)
p2["abs_leg"] = bool(abs_leg)
p2["paired_leg"] = bool(paired_leg)
p2["verdict"] = ("R-KILLED-BY-58 (L111 verdict needs revision)"
                 if p2["r_killed_by_58"] else
                 ("R-STAYS (glut-alone R-kill stands)"
                  if p2["r_stays"] else "R intermediate"))

# ---- P3 ladder sanity on B10 ----
p3 = dict(cut_kL=table["cut"]["kL"], b65_kL=table["b65"]["kL"],
          b65_kR=table["b65"]["kR"], cut19_kL=table["cut19"]["kL"])
p3["pass"] = bool(table["cut"]["kL"] >= 12 and table["b65"]["kL"] == 16
                  and table["b65"]["kR"] == 16 and table["cut19"]["kL"] >= 12)

# ---- P5 disclosure ----
p5 = dict(removed58=float(z113["mass_split"][1]),
          kept19=float(z113["mass_split"][0]),
          n_cut58=int(z113["cut58_drop"].shape[0]),
          note="cord out-mass share of removed-58 vs kept-19 heavy (mirror of "
               "l111; sums to heavy .5024); duty-form cells only per tick-136 "
               "amendment (2611.14498 LERS)")
print("P1", json.dumps(p1))
print("P2", json.dumps(p2))
print("P3", json.dumps(p3))
print("P5", json.dumps(p5))

# ---- P6 (L114 rebase read): pooled B9+B10 cut19 ----
L9, R9 = per_seed(z111, "cut19", B9)
L10, R10 = per_seed(z113, "cut19", B10)
L32 = np.concatenate([L9, L10])
kL32, meanL32 = int((L32 >= .5).sum()), round(float(L32.mean()), 3)
lb32, ub32 = wilson(kL32, 32)
p6 = dict(kL_B9=int((L9 >= .5).sum()), kL_B10=int((L10 >= .5).sum()),
          kL32=kL32, meanL32=meanL32, lb32=lb32, ub32=ub32)
p6["transmitter_confirmed"] = bool(kL32 >= 24 and meanL32 >= .70)
p6["mass_placement_leg"] = bool(kL32 <= 20 or meanL32 <= .55)
p6["verdict"] = ("TRANSMITTER arm CONFIRMED at 2 batches"
                 if p6["transmitter_confirmed"] else
                 ("MASS/PLACEMENT leg fires" if p6["mass_placement_leg"]
                  else "MIXED persists (L111 verdict stands)"))
print("P6", json.dumps(p6))

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           table_b10=table, tr_b10=tr_tab, p1=p1, p2=p2, p3=p3, p5=p5, p6=p6,
           g_cut=ar["g_cut"], g_cut19=ar["g_cut19"], g_cut58=ar["g_cut58"])
json.dump(out, open("l113/results_l113.json", "w"), indent=1)
print("results_l113.json written")
