"""L118 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
draw reads: Ti_R per draw (cutnga/cutngb/cutngc) vs full on B13 with the
COHERENCE-KILL / GLUT-IDENTITY / MIXED classification, per-side duty table
for all 8 arms x 5 pairs, paired per-seed legs, L-axis secondary, sanity
reference cells. PREREG l118/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B13 = list(range(1701, 1717))
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
DRAW_ARMS = ["cutnga", "cutngb", "cutngc"]
ARMS = STORED_ARMS + DRAW_ARMS
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z118 = np.load("l118/raw_l118.npz")
r113 = json.load(open("l113/results_l113.json"))
ar = json.load(open("l118/anchors_run.json"))
SM = json.load(open("l118/static.json"))


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


_SM = {}


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in _SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        _SM[key] = (SL, SR)
    return _SM[key]


def duty_seeds(raw, a, seeds, pk):
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


def side_k(raw, a, seeds, pk):
    L, R = duty_seeds(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L118 pin) ----
c0b_fail = []
for a in STORED_ARMS:
    for tab, pk in ((r113["table_b10"], "Ti"), (r113["tr_b10"], "Tr")):
        want = tab[a]
        got = side_k(z113, a, B10, pk)
        for kk in ("kL", "kR", "meanL", "meanR"):
            if got[kk] != want[kk]:
                c0b_fail.append((a, pk, kk, got[kk], want[kk]))
c0b_pass = not c0b_fail
print("C0B certification (stored l113, Ti+Tr tables, ALL 5 stored arms):",
      "PASS" if c0b_pass else f"FAIL {c0b_fail[:5]}")

# ---- P0 anchors (gate booleans ONLY; c0a_max/ng_band are diagnostics) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cut58_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (stored arms, seeds 801/901):",
      "PASS" if p0["pass"] else "FAIL", f"(max {p0['c0a_max']:.1e})")
print("draw gains:", {k: round(ar["g_" + k], 6) for k in DRAW_ARMS},
      "band_ok", ar["ng_band_ok"], "stairs",
      {k: f"{v:.1e}" for k, v in ar["ng_stairs"].items()})
print("draw disclosure (static):",
      {a: (SM["draws"][a]["mass_removed"], SM["draws"][a]["seed"]) for a in DRAW_ARMS},
      "target", SM["target_unrounded"], "tol", SM["tol"])

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z118[f"af_{a}_{s}"]) for s in B13])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z118[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B13)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 8-arm per-side table (B13, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z118, a, B13, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B13 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:6s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Part 3: registered draw reads (PRIMARY = Ti_R) ----
# batch-band disclosure: full-arm B13 reads vs registered bands
band = {"Ti": dict(L=(0.30, 0.45), R=(0.35, 0.55)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B13 band check (disclosure only):", band_ok)

m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z118, "full", B13, "Ti")
draws = {}
n_kill = n_surv = 0
for a in DRAW_ARMS:
    mR, kR = table["Ti"][a]["meanR"], table["Ti"][a]["kR"]
    _, Rd = duty_seeds(z118, a, B13, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    kill = (mR <= m0 - .10) and (kR <= 4) and (legs["mean_paired_dR"] <= -.20)
    surv = mR >= m0 - .10
    n_kill += kill
    n_surv += surv
    draws[a] = dict(meanR=mR, kR=kR, meanL=table["Ti"][a]["meanL"],
                    kL=table["Ti"][a]["kL"], legs=legs, kill=bool(kill),
                    survivor=bool(surv))
    print(f"Ti {a}: meanR {mR:.3f} kR {kR:2d}/16 | meanL "
          f"{draws[a]['meanL']:.3f} kL {draws[a]['kL']:2d}/16 | "
          f"paired dR {legs['mean_paired_dR']:+.3f} "
          f"n_down {legs['n_down']}/16 n_up {legs['n_up']}/16")
if n_kill >= 2:
    cls = ("COHERENCE-KILL (any single-class-coherent half at glut-19 mass "
           "kills R; glut identity irrelevant)")
elif n_surv >= 2:
    cls = ("GLUT-IDENTITY (only glutamatergic removal kills R at this mass; "
           "cut58 R-dead needs a 58-cell-mass story)")
else:
    cls = "MIXED (disclosed, draw-to-draw spread reported)"
print(f"CLASSIFICATION (>=2 of 3 rule): {cls} [kills {n_kill}/3, "
      f"survivors {n_surv}/3]")

# L-axis secondary (registered, no gate): does a .11-mass 19-cut RESTORE L?
print("L-axis secondary (mass-law predicts restore):",
      {a: (draws[a]["meanL"], draws[a]["kL"]) for a in DRAW_ARMS},
      "cut19 ref", (table["Ti"]["cut19"]["meanL"], table["Ti"]["cut19"]["kL"]))

# Sr_R watch (registered, NO gate — lottery axis, L116/L117 form)
sr = {a: (table["Sr"][a]["meanR"], table["Sr"][a]["kR"])
      for a in DRAW_ARMS + ["full", "cut19"]}
print("Sr_R watch (no gate):", sr)

# ---- Part 4: sanity reference cells (secondary; miss = disclose) ----
ls = dict(cut_kL=table["Ti"]["cut"]["kL"], b65_kL=table["Ti"]["b65"]["kL"],
          b65_kR=table["Ti"]["b65"]["kR"], cut19_kL=table["Ti"]["cut19"]["kL"],
          sr_b65_kL=table["Sr"]["b65"]["kL"], sr_b65_kR=table["Sr"]["b65"]["kR"])
ls_pass = (ls["cut_kL"] >= 14 and ls["b65_kL"] == 16 and ls["b65_kR"] == 16
           and ls["cut19_kL"] >= 12)
print("sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           ng_band_ok=ar["ng_band_ok"],
           draw_gains={a: ar["g_" + a] for a in DRAW_ARMS},
           ng_stairs=ar["ng_stairs"], table=table, draws=draws,
           cls=cls, n_kill=n_kill, n_surv=n_surv, m0=m0,
           band_ok=band_ok, sr_watch=sr, sanity=ls,
           sanity_pass=bool(ls_pass))
json.dump(out, open("l118/results_l118.json", "w"), indent=1)
print("results_l118.json written")
