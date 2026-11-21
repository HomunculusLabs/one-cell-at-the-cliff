"""L119 verdict: C0B certification of the pair-generalized duty machinery on
stored raw_l113 BEFORE any fresh pin (L85/L109 rule), then the registered
reads: (P1) Ti_R dose curve k in {0,1,2,3,5,19} FRESH on B14 with the
L118-registered kill criterion and the k* step classification; (P2) cutr5
(random 5-of-19 glut, mass .0231, zero heaviest-5 overlap) classification
IDENTITY vs PLACEMENT vs MIXED; per-side duty table 5 pairs x 10 arms;
L-axis secondary; Sr_R watch; sanity cells. PREREG l119/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B14 = list(range(1801, 1817))
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk1", "cutk2", "cutk3", "cutk5", "cutr5"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("1", "cutk1"), ("2", "cutk2"), ("3", "cutk3"),
          ("5", "cutk5"), ("19", "cut19")]
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z119 = np.load("l119/raw_l119.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
ar = json.load(open("l119/anchors_run.json"))
SM = json.load(open("l119/static.json"))


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


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L119 pin) ----
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

# ---- P0 anchors (gate booleans ONLY; c0a_max/band are diagnostics) ----
p0 = dict(c0a_pass=ar["c0a_pass"], c0a_max=ar["c0a_max"], n_seeds=ar["n_seeds"],
          g_cut58_stored_exact=ar["g_cut58_stored_exact"],
          g_cutk5_stored_exact=ar["g_cutk5_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (stored arms, seeds 801/901) + l117 k5 gain:",
      "PASS" if p0["pass"] else "FAIL", f"(max {p0['c0a_max']:.1e})")
print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutk1", "cutk2", "cutk3", "cutr5")},
      "cutk5", round(float(z119["g_cutk5"]), 6), "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z119[f"af_{a}_{s}"]) for s in B14])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z119[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B14)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 10-arm per-side table (B14, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z119, a, B14, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B14 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:6s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- batch-band disclosure: full-arm B14 reads vs registered bands ----
band = {"Ti": dict(L=(0.30, 0.45), R=(0.35, 0.55)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B14 band check (disclosure only):", band_ok)

# ---- Part 3 (P1): Ti_R dose curve, kill criterion, k* step ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z119, "full", B14, "Ti")
dose = {"Ti": {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {},
               "kill": {}},
        "Sr": {"meanR": {}, "kR": {}}}
kill_ks = []
for kk, a in LADDER:
    t = table["Ti"][a]
    dose["Ti"]["meanR"][kk] = t["meanR"]
    dose["Ti"]["kR"][kk] = t["kR"]
    dose["Ti"]["meanL"][kk] = t["meanL"]
    dose["Ti"]["kL"][kk] = t["kL"]
    _, Rd = duty_seeds(z119, a, B14, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    dose["Ti"]["legs"][kk] = legs
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR"] <= -.20)
    dose["Ti"]["kill"][kk] = bool(kill)
    if kk in ("1", "2", "3", "5") and kill:
        kill_ks.append(int(kk))
    print(f"Ti k={kk:>2s} ({a:6s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | paired dR "
          f"{legs['mean_paired_dR']:+.3f} n_down {legs['n_down']}/16 "
          f"-> {'KILL' if kill else 'no-kill'}")
dose["Ti"]["m0"] = m0
if kill_ks:
    k_star = min(kill_ks)
    if k_star == 1:
        shape = ("SINGLE-CELL (.0096 mass): the R-kill is an ultra-local "
                 "placement effect — one cell's removal flips the axis")
    else:
        shape = f"STEP AT k={k_star} ({ {'2': '.0185', '3': '.0268', '5': '.0425'}[str(k_star)] } mass)"
else:
    k_star = None
    shape = ("NO KILL at k<=5 on B14 — batch-drift disclosed (l117's k5 kill "
             "was B12); k5 point re-rolls (L118 lottery class), never "
             "rounded into a kill")
print(f"P1 k* = {k_star}: {shape}")
# cross-batch context (l117 stored B12, disclosure only)
dose["l117_stored_b12_context"] = {
    "Ti_meanR": r117["dose"]["Ti"]["meanR"],
    "Ti_kR": r117["dose"]["Ti"]["kR"]}
print("l117 B12 cross-batch context (no gate):",
      dose["l117_stored_b12_context"])

# ---- Part 4 (P2): cutr5 classification ----
mR5, kR5 = table["Ti"]["cutr5"]["meanR"], table["Ti"]["cutr5"]["kR"]
_, Rr5 = duty_seeds(z119, "cutr5", B14, "Ti")
legs5 = dict(mean_paired_dR=round(float((Rr5 - Rfull).mean()), 3),
             n_down=int(((Rr5 - Rfull) <= -.20).sum()),
             n_up=int(((Rr5 - Rfull) >= .20).sum()))
kill5 = (mR5 <= m0 - .10) and (kR5 <= 4) and (legs5["mean_paired_dR"] <= -.20)
surv5 = mR5 >= m0 - .10
if kill5:
    cls5 = ("IDENTITY: ANY 5-of-19 glut kills R at .0231 mass (below k3's "
            ".0268) — mass irrelevant, class identity at 5-cell granularity")
elif surv5:
    cls5 = ("PLACEMENT: random-5 (.0231, zero heaviest-5 overlap) does NOT "
            "kill — the HEAVIEST-5's specific cells carry the R-kill")
else:
    cls5 = ("MIXED (near-miss band, disclosed with legs; never rounded — "
            "L118 precedent)")
print(f"P2 cutr5: meanR {mR5:.3f} kR {kR5:2d}/16 paired dR "
      f"{legs5['mean_paired_dR']:+.3f} n_down {legs5['n_down']}/16 -> {cls5}")

# Sr watch curve (registered, no gate — lottery axis)
for kk, a in LADDER:
    dose["Sr"]["meanR"][kk] = table["Sr"][a]["meanR"]
    dose["Sr"]["kR"][kk] = table["Sr"][a]["kR"]
print("Sr_R watch (no gate):", dose["Sr"]["meanR"],
      "kR", dose["Sr"]["kR"])

# ---- Part 5: sanity reference cells (secondary; miss = disclose) ----
ls = dict(cut_kL=table["Ti"]["cut"]["kL"], b65_kL=table["Ti"]["b65"]["kL"],
          b65_kR=table["Ti"]["b65"]["kR"], cut19_kL=table["Ti"]["cut19"]["kL"],
          sr_b65_kL=table["Sr"]["b65"]["kL"], sr_b65_kR=table["Sr"]["b65"]["kR"])
ls_pass = (ls["cut_kL"] >= 14 and ls["b65_kL"] == 16 and ls["b65_kR"] == 16
           and ls["cut19_kL"] >= 12)
print("sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           fresh_gains={a: ar["g_" + a] for a in ("cutk1", "cutk2",
                                                  "cutk3", "cutr5")},
           g_cutk5=float(z119["g_cutk5"]), new_stairs=ar["new_stairs"],
           mass={a: SM["ladder"][f"k{k}"]["mass_removed"]
                 for a, k in (("cutk1", 1), ("cutk2", 2), ("cutk3", 3),
                              ("cutk5", 5))} | {"cutr5": SM["draw"]["cutr5"]["mass_removed"]},
           table=table, dose=dose, k_star=k_star, shape=shape,
           cutr5=dict(meanR=mR5, kR=kR5, legs=legs5, kill=bool(kill5),
                      survivor=bool(surv5), cls=cls5,
                      overlap_with_heaviest5=SM["draw"]["cutr5"]["overlap_with_heaviest5"]),
           band_ok=band_ok, sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l119/results_l119.json", "w"), indent=1)
print("results_l119.json written")
