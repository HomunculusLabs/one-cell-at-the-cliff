"""L117 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
dose-curve reads: Ti_R + Sr_R across k in {0=full, 5, 10, 15, 19=cut19},
per-side duty table for all 8 arms x 5 pairs on B12, paired per-seed legs,
ladder-sanity reference cells. PREREG l117/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B12 = list(range(1601, 1617))
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
DOSE_ARMS = ["cutk5", "cutk10", "cutk15"]
ARMS = STORED_ARMS + DOSE_ARMS
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z117 = np.load("l117/raw_l117.npz")
r113 = json.load(open("l113/results_l113.json"))
ar = json.load(open("l117/anchors_run.json"))
SM = {}


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


def s_arrays(raw, a, s, pk):
    """Sliding 500-step antagonist anticorrelation per side (l113 VERBATIM,
    generalized only in the agonist/antagonist pool-name prefixes)."""
    key = (id(raw), a, s, pk)
    if key not in SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        SM[key] = (SL, SR)
    return SM[key]


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


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L117 pin) ----
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

# ---- P0 anchors (gate booleans ONLY; c0a_max/dose_band are diagnostics) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cut58_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (stored arms, seeds 801/901):",
      "PASS" if p0["pass"] else "FAIL", f"(max {p0['c0a_max']:.1e})")
print("dose gains:", {k: round(ar[k], 6) for k in ("g_cutk5", "g_cutk10", "g_cutk15")},
      "band_ok", ar["dose_band_ok"], "stairs",
      {k: f"{v:.1e}" for k, v in ar["dose_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z117[f"af_{a}_{s}"]) for s in B12])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z117[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B12)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 8-arm per-side table (B12, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z117, a, B12, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B12 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:6s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Part 3: registered dose curves (PRIMARY) ----
# batch-band disclosure: full-arm B12 reads vs registered bands
band = {"Ti": dict(L=(0.30, 0.45), R=(0.35, 0.55)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B12 band check (disclosure only):", band_ok)

LADDER = [("full", 0), ("cutk5", 5), ("cutk10", 10), ("cutk15", 15),
          ("cut19", 19)]
dose = {}
for pk in ("Ti", "Sr"):
    m = {k: table[pk][a]["meanR"] for a, k in LADDER}
    kc = {k: table[pk][a]["kR"] for a, k in LADDER}
    m0, m19 = m[0], m[19]
    surv = all(m[k] >= m0 - .10 for k in (5, 10, 15))
    mono = (m[5] >= m[10] - .03) and (m[10] >= m[15] - .03) and (m[15] >= m[19] - .03)
    kill15 = m[15] < m0 - .10
    if surv and m19 <= .15:
        cls = "COHERENCE (R full-like until the whole class is gone)"
    elif mono and kill15:
        cls = "FRACTION (R-kill tracks dose monotonically)"
    else:
        cls = "MIXED (disclosed)"
    # paired per-seed legs vs full (L45b form)
    _, Rfull = duty_seeds(z117, "full", B12, pk)
    legs = {}
    for a, k in LADDER[1:]:
        _, Rd = duty_seeds(z117, a, B12, pk)
        legs[k] = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                       n_down=int(((Rd - Rfull) <= -.20).sum()),
                       n_up=int(((Rd - Rfull) >= .20).sum()))
    # L-axis secondary (descriptive)
    mL = {k: table[pk][a]["meanL"] for a, k in LADDER}
    kL = {k: table[pk][a]["kL"] for a, k in LADDER}
    dose[pk] = dict(meanR=m, kR=kc, meanL=mL, kL=kL, cls=cls, legs=legs,
                    m0=m0, m19=m19)
    print(f"---- {pk} DOSE CURVE (B12) ----")
    for a, k in LADDER:
        print(f"  k={k:2d} ({a:6s}) meanR {m[k]:.3f} kR {kc[k]:2d}/16 | "
              f"meanL {mL[k]:.3f} kL {kL[k]:2d}/16")
    for k, v in legs.items():
        print(f"  paired k={k:2d}: mean dR {v['mean_paired_dR']:+.3f} "
              f"n_down {v['n_down']}/16 n_up {v['n_up']}/16")
    print(f"  CLASSIFICATION: {cls}")

# Sr_R watch classification (registered)
sr = dose["Sr"]
sr_frag = all(sr["meanR"][k] <= sr["m0"] - .10 for k in (5, 10, 15))
sr_like = (sr["meanR"][5] >= sr["m0"] - .10 or sr["meanR"][10] >= sr["m0"] - .10) \
    and sr["meanR"][15] <= sr["m0"] - .10
sr_watch = ("FRAGILE (every partial dose kills Sr_R — marginal-side lottery)"
            if sr_frag else
            "CLASS-LIKE (survives k<15, dies at 15/19)" if sr_like else
            "OTHER (disclosed)")
print("Sr_R watch:", sr_watch)

# ---- Part 4: ladder-sanity reference cells (secondary; miss = disclose) ----
ls = dict(cut_kL=table["Ti"]["cut"]["kL"], b65_kL=table["Ti"]["b65"]["kL"],
          b65_kR=table["Ti"]["b65"]["kR"], cut19_kL=table["Ti"]["cut19"]["kL"],
          sr_b65_kL=table["Sr"]["b65"]["kL"], sr_b65_kR=table["Sr"]["b65"]["kR"])
ls_pass = (ls["cut_kL"] >= 14 and ls["b65_kL"] == 16 and ls["b65_kR"] == 16
           and ls["cut19_kL"] >= 12)
print("ladder sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           dose_band_ok=ar["dose_band_ok"],
           dose_gains={k: ar[k] for k in ("g_cutk5", "g_cutk10", "g_cutk15")},
           dose_stairs=ar["dose_stairs"], table=table, dose=dose,
           band_ok=band_ok, sr_watch=sr_watch, ladder_sanity=ls,
           ladder_sanity_pass=bool(ls_pass))
json.dump(out, open("l117/results_l117.json", "w"), indent=1)
print("results_l117.json written")
