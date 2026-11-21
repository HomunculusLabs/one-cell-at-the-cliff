"""L122 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B16-cert of this machinery on raw_l121 vs results_l121.json BEFORE any
pooling, then the registered REBASE reads on FRESH B17 (kill criterion
VERBATIM): R1 cutng19 kill, R2 cutng29 raise, R3 endpoints (cut58 3rd
batch, cutk5 5th), R4 pooled batch-union B16+B17 n=32 full-precision
Wilson (L90 form — the CITABLE number); per-side duty table 5 pairs x 9
arms; L-axis + Sr_R watch; sanity cells. PREREG l122/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B17 = list(range(2101, 2117))
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutng39"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("29", "cutng29"),
          ("39", "cutng39"), ("58", "cut58"), ("k5", "cutk5")]
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z121 = np.load("l121/raw_l121.npz")
z122 = np.load("l122/raw_l122.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
r120 = json.load(open("l120/results_l120.json"))
ar = json.load(open("l122/anchors_run.json"))
r121 = json.load(open("l121/results_l121.json"))
SM = json.load(open("l121/static.json"))


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
          c0a120_pass=ar["c0a120_pass"], c0a120_max=ar["c0a120_max"],
          c0a121_pass=ar["c0a121_pass"], c0a121_max=ar["c0a121_max"],
          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],
          g_cutng29_stored_exact=ar["g_cutng29_stored_exact"],
          g_cutng39_stored_exact=ar["g_cutng39_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cutng39_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (4 arms vs raw_l121) + 7 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max120 {p0['c0a120_max']:.1e})")
print("fresh gains:", {k: round(ar["g_" + k], 6)
                       for k in ("cutng19", "cutng29", "cutng39")},
      "cutk5", round(float(z122["g_cutk5"]), 6), "(stored, asserted)",
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z122[f"af_{a}_{s}"]) for s in B17])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z122[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B17)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 10-arm per-side table (B16, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z122, a, B17, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B17 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:6s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- batch-band disclosure: full-arm B16 reads vs registered bands ----
band = {"Ti": dict(L=(0.25, 0.48), R=(0.35, 0.58)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B17 band check (disclosure only):", band_ok)

# ---- Part 3 (P1): Ti_R curve {0,3,4a,4b,5,19}, kill criterion ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z122, "full", B17, "Ti")
dose = {"Ti": {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {},
               "kill": {}},
        "Sr": {"meanR": {}, "kR": {}}}
killmap = {}
for kk, a in LADDER:
    t = table["Ti"][a]
    dose["Ti"]["meanR"][kk] = t["meanR"]
    dose["Ti"]["kR"][kk] = t["kR"]
    dose["Ti"]["meanL"][kk] = t["meanL"]
    dose["Ti"]["kL"][kk] = t["kL"]
    _, Rd = duty_seeds(z122, a, B17, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    dose["Ti"]["legs"][kk] = legs
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR"] <= -.20)
    dose["Ti"]["kill"][kk] = bool(kill)
    killmap[kk] = bool(kill)
    print(f"Ti k={kk:>2s} ({a:6s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | paired dR "
          f"{legs['mean_paired_dR']:+.3f} n_down {legs['n_down']}/16 "
          f"-> {'KILL' if kill else 'no-kill'}")
dose["Ti"]["m0"] = m0
# cross-batch context (stored, disclosure only)
dose["l117_stored_b12_context"] = {
    "Ti_meanR": r117["dose"]["Ti"]["meanR"],
    "Ti_kR": r117["dose"]["Ti"]["kR"]}
dose["l119_stored_b14_context"] = {
    "Ti_meanR": r119["dose"]["Ti"]["meanR"],
    "Ti_kR": r119["dose"]["Ti"]["kR"]}
dose["l121_stored_b16_context"] = {
    "Ti_meanR": r121["dose"]["Ti"]["meanR"],
    "Ti_kR": r121["dose"]["Ti"]["kR"],
    "kill": r121["dose"]["Ti"]["kill"]}
dose["l120_stored_b15_context"] = {
    "k5_Ti_meanR": r120["dose"]["Ti"]["meanR"]["5"],
    "k5_Ti_kR": r120["dose"]["Ti"]["kR"]["5"],
    "k5_kill": r120["k4"]["k5_kill"]}
print("l117 B12 / l119 B14 / l120 B15 / l121 B16 cross-batch context:",
      dose["l117_stored_b12_context"], dose["l119_stored_b14_context"],
      dose["l120_stored_b15_context"])

# ---- Part 4: REBASE reads R1/R2/R3 + B16-cert + R4 pooled union ----
ng_kills = {k: killmap[k] for k in ("19", "29", "39")}
k58_kill = killmap["58"]
k5_kill = killmap["k5"]
r1 = dict(kill=bool(killmap["19"]), cls=(
    "cutng19 KILL replicates on B17 — the .1946 non-glut kill is "
    "BATCH-ROBUST (2/2 batches, pooled n=32 citable)" if killmap["19"] else
    "cutng19 does NOT kill on B17 — B16 kill reclassified batch-drawn "
    "(L88 class); L121 MASS-FRACTION firing amended single-batch"))
r2_raise = (table["Ti"]["cutng29"]["meanR"] >= m0
            and table["Ti"]["cutng29"]["kR"] >= 12
            and dose["Ti"]["legs"]["29"]["mean_paired_dR"] >= .20)
r2 = dict(raise_replicates=bool(r2_raise), cls=(
    "cutng29 raise REPLICATES on B17 — the middle-dose super-raise is "
    "batch-robust" if r2_raise else
    "cutng29 raise does NOT replicate on B17 — B16's .727 (highest R of "
    "any arm) is a single-batch draw; middle stays lottery (L118 class)"))
r3 = dict(cut58_kill=bool(k58_kill), cutk5_kill=bool(k5_kill), cls=(
    "cut58 kills (endpoint, 3rd batch) + cutk5 kills (5th consecutive "
    "batch B12/B14/B15/B16/B17)" if k58_kill and k5_kill else
    "endpoint miss DISCLOSED (registered R3, never silent)"))
print(f"R1: {r1['cls']}")
print(f"R2: {r2['cls']}")
print(f"R3: {r3['cls']}")
# B16-cert BEFORE pooling: recomputed B16 Ti cells == results_l121.json
b16_cert_fail = []
for a in ARMS:
    want = r121["table"]["Ti"][a]
    got = side_k(z121, a, B16, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b16_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b16_cert_fail, ("B16-cert FAIL (no pooling read)",
                           b16_cert_fail[:5])
print(f"B16-cert vs results_l121.json Ti table: PASS (all {len(ARMS)} arms)")
# R4: pooled batch-union, FULL-PRECISION Wilson, unrounded pins (L90)
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutng39", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    both = np.concatenate([Rb16, Rb17])
    k = int((both >= .5).sum())
    lb, ub = wilson(k, 32)
    pooled[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/32 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16) p_hat {k/32:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}]")

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
           fresh_gains={a: ar["g_" + a]
                        for a in ("cutng19", "cutng29", "cutng39")},
           g_cutk5=float(z122["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cutng39", "k39"), ("cut58", "k58"))},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           rebase=dict(r1=r1, r2=r2, r3=r3, ng_kills=ng_kills,
                       k58_kill=bool(k58_kill), k5_kill=bool(k5_kill)),
           pooled=pooled, b16_cert_pass=True,
           band_ok=band_ok,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l122/results_l122.json", "w"), indent=1)
print("results_l122.json written")
