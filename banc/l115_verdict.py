"""L115 verdict: C0B certification on stored raw_l113 BEFORE any fresh pin
(L85/L109 rule), then per-side duty07 cells on B11 (7 arms) + P0-P6 gates.
PREREG l115/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0, BLK = 500, 500
SIGS = ("fL", "fR", "eL", "eR")
B9 = list(range(1301, 1317))
B10 = list(range(1401, 1417))
B11 = list(range(1501, 1517))
ARMS = ["full", "b65", "cut", "cut19", "cutR1", "cutR2", "cutR3"]
RND = ["cutR1", "cutR2", "cutR3"]
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z111 = np.load("l111/raw_l111.npz")
z113 = np.load("l113/raw_l113.npz")
z115 = np.load("l115/raw_l115.npz")
r113 = json.load(open("l113/results_l113.json"))
ar = json.load(open("l115/anchors_run.json"))
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
    """Rounded per-seed duty values (the l109/l111/l113 rounding-path atom)."""
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


# ---- Part 1: C0B on stored l113 (BEFORE any L115 pin) ----
c0b_fail = []
for a in ["full", "b65", "cut", "cut19", "cut58"]:
    want = r113["table_b10"][a]
    got = side_k(z113, a, B10)
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            c0b_fail.append((a, kk, got[kk], want[kk]))
    want_tr = r113["tr_b10"][a]
    got_tr = side_k(z113, a, B10, "Tr")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got_tr[kk] != want_tr[kk]:
            c0b_fail.append((a, f"tr_{kk}", got_tr[kk], want_tr[kk]))
c0b_pass = not c0b_fail
print("C0B certification (stored l113, Ti+Tr B10 tables):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:5]}")

# ---- P0 anchors (gate booleans ONLY in the aggregate; c0a_max 0.0 is a
# diagnostic magnitude, not a gate — L59/L113 anchor-key class) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0_pass = bool(p0["c0a_pass"] and p0["g_cut_stored_exact"]
               and p0["g_cut19_stored_exact"])
p0["pass"] = p0_pass
print("P0 anchors vs raw_l113:", "PASS" if p0_pass else "FAIL",
      f"(max {p0['c0a_max']:.1e}, g_cut exact {p0['g_cut_stored_exact']}, "
      f"g_cut19 exact {p0['g_cut19_stored_exact']})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z115[f"af_{a}_{s}"]) for s in B11])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z115[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B11)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean,
          staircases={k: abs(v - 0.10905611018339793) for k, v in ar["af_finalR"].items()})
print("P4", json.dumps(p4))

# ---- Part 2: per-side duty table on B11 (n=16/arm) ----
table = {}
for a in ARMS:
    t = side_k(z115, a, B11)
    lbL, ubL = wilson(t["kL"], 16)
    lbR, ubR = wilson(t["kR"], 16)
    t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
    table[a] = t
    print(f"{a:6s} Ti  kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} "
          f"[{lbL:.3f},{ubL:.3f}] | kR {t['kR']:2d}/16 meanR {t['meanR']:.3f} "
          f"[{lbR:.3f},{ubR:.3f}]")
tr_tab = {a: side_k(z115, a, B11, "Tr") for a in ARMS}
for a in ARMS:
    t = tr_tab[a]
    print(f"{a:6s} Tr  kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
          f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- P1 PRIMARY (random-flip test, per draw arm on B11) ----
draws = {}
for d in RND:
    t = table[d]
    flip = bool(t["kL"] >= 12 and t["meanL"] >= .70 and t["kR"] <= 4)
    noflip = bool(t["kL"] <= 8 or t["meanL"] <= .55)
    draws[d] = dict(kL=t["kL"], meanL=t["meanL"], kR=t["kR"], meanR=t["meanR"],
                    flip=flip, noflip=noflip,
                    verdict=("FLIP" if flip else
                             "NO-FLIP" if noflip else "MIXED"))
n_flip = sum(1 for d in RND if draws[d]["flip"])
n_noflip = sum(1 for d in RND if draws[d]["noflip"])
p1 = dict(draws=draws, n_flip=n_flip, n_noflip=n_noflip)
p1["mass_threshold_law"] = bool(n_flip >= 2)
p1["subset_class_specific"] = bool(n_flip == 0 and n_noflip >= 2)
p1["verdict"] = ("MASS/THRESHOLD LAW (membership meaningless at 19-of-77)"
                 if p1["mass_threshold_law"] else
                 ("SUBSET-CLASS-SPECIFIC (which-19 matters)"
                  if p1["subset_class_specific"] else "MIXED (disclosed)"))
print("P1", json.dumps(p1))

# ---- P2 R-side (descriptive + paired; batch-drawn axis disclosed) ----
ful = table["full"]
p2 = {d: dict(kR=table[d]["kR"], meanR=table[d]["meanR"],
              paired_leg=bool(table[d]["kR"] >= ful["kR"]
                              and table[d]["meanR"] >= ful["meanR"] - .10))
      for d in RND}
p2["full"] = dict(kR=ful["kR"], meanR=ful["meanR"])
print("P2", json.dumps(p2))

# ---- P3 ladder sanity on B11 ----
p3 = dict(cut_kL=table["cut"]["kL"], b65_kL=table["b65"]["kL"],
          b65_kR=table["b65"]["kR"], cut19_kL=table["cut19"]["kL"])
p3["pass"] = bool(table["cut"]["kL"] >= 12 and table["b65"]["kL"] == 16
                  and table["b65"]["kR"] == 16 and table["cut19"]["kL"] >= 12)
print("P3", json.dumps(p3))

# ---- P5 disclosure (mass, glut count, glut-19 cell overlap per draw) ----
c19_set = set(z113["cut19_drop"].tolist())
p5 = dict(rand_mass=[float(x) for x in z115["rand_mass"]],
          rand_glut=[int(x) for x in z115["rand_glut"]],
          glut19_overlap={f"cutR{i}": len(c19_set & set(z115[f"cutR{i}_drop"].tolist()))
                          for i in (1, 2, 3)},
          note="removed heavy cord out-mass share, glut count, and cell overlap "
               "with the glut-19 set, per draw; duty-form cells only "
               "(tick-136 amendment, 2611.14498 LERS)")
print("P5", json.dumps(p5))

# ---- P6 DIAGNOSTIC ONLY (gates nothing): pooled cut19 B9+B10+B11 ----
L9, R9 = per_seed(z111, "cut19", B9)
L10, R10 = per_seed(z113, "cut19", B10)
L11, R11 = per_seed(z115, "cut19", B11)
L48 = np.concatenate([L9, L10, L11])
kL48, meanL48 = int((L48 >= .5).sum()), round(float(L48.mean()), 3)
lb48, ub48 = wilson(kL48, 48)
p6 = dict(kL_B9=int((L9 >= .5).sum()), kL_B10=int((L10 >= .5).sum()),
          kL_B11=int((L11 >= .5).sum()), kL48=kL48, meanL48=meanL48,
          lb48=lb48, ub48=ub48, gates="NOTHING (L114 box closed MIXED; "
          "3rd diagnostic batch, L88/L90 rule)")
print("P6", json.dumps(p6))

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           table_b11=table, tr_b11=tr_tab, p1=p1, p2=p2, p3=p3, p5=p5, p6=p6,
           g_cut=ar["g_cut"], g_cut19=ar["g_cut19"], g_cutR=ar["g_cutR"])
json.dump(out, open("l115/results_l115.json", "w"), indent=1)
print("results_l115.json written")
