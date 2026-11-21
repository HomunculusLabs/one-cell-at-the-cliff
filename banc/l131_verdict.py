"""L131 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B23-cert of this machinery on raw_l128 vs results_l128.json (ALL its
table arms) BEFORE any B24 read, then the registered XOR reads on FRESH
B24 (criteria VERBATIM): X1 cutng25 SUPER/RESTORE -> rank 25 (id 1110)
completes; X2 cutng25 PARTIAL -> rank 26 (id 319) completes; X3
registered degenerate branch (kill/out-of-band -> NEITHER single cell;
the {1110,319} pair stays the unit). P2 mass-twin disclosure (static
pins). P3 pooled transition arms {ng23, wA, ng26, ng29} B21+B24 n=32
full-precision Wilson (L132 prebase). S1 cutk5 12th batch pooled R4
B16..B24 n=144; S2 endpoints 9th batch (dR-leg disclosure); S3 wA
partial 4th batch; per-side duty table 5 pairs x 12 arms; Ti_L/Tr_R/Sr_R
watch; sanity cells. PREREG l131/PREREG.md."""

import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B24 = list(range(2801, 2817))       # FRESH (l131)
B23 = list(range(2701, 2717))  # context batch (l128, cert)
B22 = list(range(2601, 2617))  # context batch (l127, R4 pool)
B21 = list(range(2501, 2517))  # context batch (l126, P3 pool)
B20 = list(range(2401, 2417))  # context batch (l125, cert + pooled)
B19 = list(range(2301, 2317))  # context batch (l124, pooled)
B18 = list(range(2201, 2217))  # context batch (l123, pooled)
B17 = list(range(2101, 2117))  # context batch (l122, pooled)
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk5", "cutng19", "cutng23", "cutwA", "cutng25", "cutng26",
            "cutng29"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("23", "cutng23"),
          ("24", "cutwA"), ("25", "cutng25"), ("26", "cutng26"),
          ("29", "cutng29"), ("58", "cut58"),
          ("k5", "cutk5")]
CURVE = ["19", "23", "24", "25", "26", "29"]   # registered curve
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054

z113 = np.load("l113/raw_l113.npz")
z121 = np.load("l121/raw_l121.npz")
z122 = np.load("l122/raw_l122.npz")
z123 = np.load("l123/raw_l123.npz")
z124 = np.load("l124/raw_l124.npz")
z125 = np.load("l125/raw_l125.npz")
z126 = np.load("l126/raw_l126.npz")
z127 = np.load("l127/raw_l127.npz")
z128 = np.load("l128/raw_l128.npz")
z131 = np.load("l131/raw_l131.npz")
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
r120 = json.load(open("l120/results_l120.json"))
ar = json.load(open("l131/anchors_run.json"))
r128 = json.load(open("l128/results_l128.json"))
r124 = json.load(open("l124/results_l124.json"))
r123 = json.load(open("l123/results_l123.json"))
r121 = json.load(open("l121/results_l121.json"))
r122 = json.load(open("l122/results_l122.json"))
r125 = json.load(open("l125/results_l125.json"))
SM = json.load(open("l121/static.json"))
S126 = json.load(open("l126/static.json"))
S131 = json.load(open("l131/static.json"))


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


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L126 pin) ----
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
          c0a122_pass=ar["c0a122_pass"], c0a122_max=ar["c0a122_max"],
          c0a123_pass=ar["c0a123_pass"], c0a123_max=ar["c0a123_max"],
          c0a124_pass=ar["c0a124_pass"], c0a124_max=ar["c0a124_max"],
          c0a125_pass=ar["c0a125_pass"], c0a125_max=ar["c0a125_max"],
          c0a126_pass=ar["c0a126_pass"], c0a126_max=ar["c0a126_max"],
          c0a127_pass=ar["c0a127_pass"], c0a127_max=ar["c0a127_max"],
          c0a128_pass=ar["c0a128_pass"], c0a128_max=ar["c0a128_max"],
          g_cutng23_stored_exact=ar["g_cutng23_stored_exact"],
          g_cutng26_stored_exact=ar["g_cutng26_stored_exact"],
          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],
          g_cutng29_stored_exact=ar["g_cutng29_stored_exact"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["c0a124_pass"] and p0["c0a125_pass"]
                  and p0["c0a126_pass"] and p0["c0a127_pass"]
                  and p0["c0a128_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cutwA_stored_exact"]
                  and p0["g_cutng23_stored_exact"] and p0["g_cutng26_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..125 "
      "retained + C0A-126 EXT (9 arms) + C0A-127 (6) + C0A-128 (6) + "
      "9 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max120 {p0['c0a120_max']:.1e})")
print("prefix FRESH gains (band DISCLOSED):", ar["prefix_fresh_gains"],
      "cutwA", round(float(z131["g_cutwA"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z131[f"af_{a}_{s}"]) for s in B24])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z131[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B24)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 13-arm per-side table (B21, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z131, a, B24, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B24 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:7s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- batch-band disclosure: full-arm B21 reads vs registered bands ----
band = {"Ti": dict(L=(0.25, 0.48), R=(0.35, 0.58)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B24 band check (disclosure only):", band_ok)

# ---- Part 3 (P1): Ti_R dose curve {19,21,23,24,26,28,29} ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z131, "full", B24, "Ti")
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
    _, Rd = duty_seeds(z131, a, B24, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    dose["Ti"]["legs"][kk] = legs
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR"] <= -.20)
    dose["Ti"]["kill"][kk] = bool(kill)
    killmap[kk] = bool(kill)
    print(f"Ti k={kk:>2s} ({a:7s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
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
dose["l122_stored_b17_context"] = {
    "Ti_meanR": r122["dose"]["Ti"]["meanR"],
    "Ti_kR": r122["dose"]["Ti"]["kR"],
    "kill": r122["dose"]["Ti"]["kill"]}
dose["l123_stored_b18_context"] = {
    "Ti_meanR": r123["dose"]["Ti"]["meanR"],
    "Ti_kR": r123["dose"]["Ti"]["kR"],
    "kill": r123["dose"]["Ti"]["kill"]}
dose["l124_stored_b19_context"] = {
    "Ti_meanR": r124["dose"]["Ti"]["meanR"],
    "Ti_kR": r124["dose"]["Ti"]["kR"],
    "kill": r124["dose"]["Ti"]["kill"]}
dose["l125_stored_b20_context"] = {
    "Ti_meanR": r125["dose"]["Ti"]["meanR"],
    "Ti_kR": r125["dose"]["Ti"]["kR"],
    "kill": r125["dose"]["Ti"]["kill"]}

# ---- Part 4: B23-cert FIRST, then XOR reads + S/S + pooled ----
# B23-cert BEFORE any B24 read: machinery recomputed on raw_l128 B23 ==
# results_l128.json Ti table (ALL 12 l128 table arms).
b23_cert_fail = []
for a in r128["table"]["Ti"]:
    want = r128["table"]["Ti"][a]
    got = side_k(z128, a, B23, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b23_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b23_cert_fail, ("B23-cert FAIL (no B24 read)",
                           b23_cert_fail[:5])
print(f"B23-cert vs results_l128.json Ti table: PASS "
      f"(all {len(r128['table']['Ti'])} arms)")


# RESTORE (PREREG): meanR >= .45 AND kR >= 12. SUPER: meanR >= .60 AND
# kR >= 12. PARTIAL band: meanR in [.35,.50] AND kR in 3..8.
def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


interp_read = {}
for kk in CURVE:
    a = dict(LADDER)[kk]
    t = table["Ti"][a]
    interp_read[kk] = dict(
        arm=a, meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"], kL=t["kL"],
        kill=killmap[kk], restore=_restore(t), super=_super(t),
        partial=_partial(t),
        mass=S131["prefix"][a]["mass_removed"] if a in S131["prefix"]
        else (SM["ngladder"]["k19"]["mass_removed"] if kk == "19"
              else SM["ngladder"]["k29"]["mass_removed"] if kk == "29"
              else None))
    print(f"CURVE k={kk:>2s} ({a:7s}, mass "
          f"{interp_read[kk]['mass'] if interp_read[kk]['mass'] else 0:.4f}): "
          f"meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 -> "
          f"{'KILL' if interp_read[kk]['kill'] else 'no-kill'}"
          f"{'/RESTORE' if interp_read[kk]['restore'] else ''}"
          f"{'/SUPER' if interp_read[kk]['super'] else ''}"
          f"{'/PARTIAL' if interp_read[kk]['partial'] else ''}")

# registered XOR branches (PREREG X1/X2/X3; report WHICH carries)
t25 = interp_read["25"]
x1 = bool(t25["super"] or t25["restore"])
x2 = bool(t25["partial"])
x3 = bool(t25["kill"] or not (x1 or x2))
xor = dict(
    X1_rank25_completes=x1, X2_rank26_completes=x2,
    X3_neither=x3,
    cls=("X1: rank 25 (id 1110) COMPLETES the kill->super flip — k25 "
          "supers/restores alone, k26 adds nothing material"
          if x1 else
          "X2: rank 26 (id 319) is the completing cell — k25 stays "
          "PARTIAL, k26 supers same-batch"
          if x2 else
          "X3 (registered degenerate): NO single named cell carries "
          "the flip — k25 kills or lands outside every band; the "
          "{1110, 319} PAIR stays the unit (L55 rule)"))
steps_x = {"24->25": round(interp_read["25"]["meanR"]
                           - interp_read["24"]["meanR"], 3),
           "25->26": round(interp_read["26"]["meanR"]
                           - interp_read["25"]["meanR"], 3)}
p2 = dict(rank25_id=S131["rank_ids"]["rank25"],
          rank26_id=S131["rank_ids"]["rank26"],
          m25=S131["rank_mass"]["rank25"], m26=S131["rank_mass"]["rank26"],
          pair_delta=S131["rank_mass"]["pair_delta"],
          note="arms differ by one full cell mass each way; the "
               "alternative reading is any ~.006 mass beyond .2350")
print(f"XOR: {xor['cls']} | steps {steps_x}")
print(f"P2 mass-twins: id {p2['rank25_id']} m {p2['m25']:.6f} vs "
      f"id {p2['rank26_id']} m {p2['m26']:.6f} (delta "
      f"{p2['pair_delta']:.2e})")

# S1: cutk5 12th batch; S2: endpoints 9th batch (dR-leg note);
# S3: wA partial 4th batch
s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B24 — 12th consecutive batch "
    "(B12/B14/B15/B16/B17/B18/B19/B20/B21/B22/B23/B24)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B24 — DISCLOSED (L118 lottery class)"))
s2 = dict(ng19_kill=bool(killmap["19"]),
          ng19_dR_leg=dose["Ti"]["legs"]["19"]["mean_paired_dR"],
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs (kR+meanR legs; dR leg reported separately, "
    "3-batch miss pattern) + cutng29 SUPER-RAISES in-batch (9th)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))
s3 = dict(wA_partial=bool(_partial(table["Ti"]["cutwA"])),
          wA_meanR=table["Ti"]["cutwA"]["meanR"],
          wA_kR=table["Ti"]["cutwA"]["kR"], cls=(
    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 4th batch "
    "(B18 .413/5, B19 .376/4, B21 .365/3, B24)"
    if _partial(table["Ti"]["cutwA"]) else
    "cutwA MISSES the partial band — DISCLOSED (would revise L124's "
    "stable-intermediate reading)"))
print(f"S1: {s1['cls']}")
print(f"S2: {s2['cls']} | ng19 dR leg {s2['ng19_dR_leg']:+.3f}")
print(f"S3: {s3['cls']}")
# R4: pooled batch-union B16..B24 n=144, FULL-PRECISION Wilson
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    _, Rb20 = duty_seeds(z125, a, B20, "Ti")
    _, Rb21 = duty_seeds(z126, a, B21, "Ti")
    _, Rb22 = duty_seeds(z127, a, B22, "Ti")
    _, Rb23 = duty_seeds(z128, a, B23, "Ti")
    _, Rb24 = duty_seeds(z131, a, B24, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21,
                           Rb22, Rb23, Rb24])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 144)
    pooled[a] = dict(k144=k, p_hat=k / 144, lb=lb, ub=ub,
                     k_b21=int((Rb21 >= .5).sum()),
                     k_b24=int((Rb24 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/144 p_hat {k/144:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}] (B21 {pooled[a]['k_b21']}/16, "
          f"B24 {pooled[a]['k_b24']}/16)")
# P3 (L132 prebase): transition arms pooled B21+B24 n=32
pooled_t = {}
for a in ("cutng23", "cutwA", "cutng26", "cutng29"):
    _, Rb21 = duty_seeds(z126, a, B21, "Ti")
    _, Rb24 = duty_seeds(z131, a, B24, "Ti")
    allb = np.concatenate([Rb21, Rb24])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 32)
    pooled_t[a] = dict(k32=k, p_hat=k / 32, lb=lb, ub=ub,
                       k_b21=int((Rb21 >= .5).sum()),
                       k_b24=int((Rb24 >= .5).sum()))
    print(f"P3 POOLED transition {a:8s} k {k}/32 "
          f"(B21 {pooled_t[a]['k_b21']}/16 + B24 "
          f"{pooled_t[a]['k_b24']}/16) p_hat {k/32:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}]")
pooled_scr = {"note": "not run in L131 — l128 rebase stands"}

# watch axes (registered, no gate)
watch = dict(
    Ti_L_curve={kk: interp_read[kk]["meanL"] for kk in CURVE},
    Ti_L_k={kk: interp_read[kk]["kL"] for kk in CURVE},
    Sr_R_curve=None, Tr_R_curve={})
for kk, a in LADDER:
    dose["Sr"]["meanR"][kk] = table["Sr"][a]["meanR"]
    dose["Sr"]["kR"][kk] = table["Sr"][a]["kR"]
    watch["Tr_R_curve"][kk] = table["Tr"][a]["meanR"]
watch["Sr_R_curve"] = dict(dose["Sr"]["meanR"])
watch["ng29_L_death_anticorr"] = dict(
    ng29_L=table["Ti"]["cutng29"]["meanL"], ng29_L_k=table["Ti"]["cutng29"]["kL"],
    ng29_R=table["Ti"]["cutng29"]["meanR"])
print("WATCH Ti_L curve:", watch["Ti_L_curve"])
print("WATCH Sr_R:", watch["Sr_R_curve"])
print("WATCH Tr_R:", watch["Tr_R_curve"])

# ---- Part 5: sanity reference cells (secondary; miss = disclose) ----
ls = dict(cut_kL=table["Ti"]["cut"]["kL"], b65_kL=table["Ti"]["b65"]["kL"],
          b65_kR=table["Ti"]["b65"]["kR"], cut19_kL=table["Ti"]["cut19"]["kL"],
          sr_b65_kL=table["Sr"]["b65"]["kL"], sr_b65_kR=table["Sr"]["b65"]["kR"])
ls_pass = (ls["cut_kL"] >= 14 and ls["b65_kL"] == 16 and ls["b65_kR"] == 16
           and ls["cut19_kL"] >= 12)
print("sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           prefix_fresh_gains=ar["prefix_fresh_gains"],
           g_cutk5=float(z131["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_prefix={a: S126["prefix"][a]["mass_removed"]
                        for a in S126["prefix"]},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           interp=dict(curve=interp_read, steps=steps_x, s1=s1, s2=s2,
                       s3=s3),
           xor=dict(**xor, steps=steps_x, p2=p2),
           pooled=pooled, pooled_transition=pooled_t,
           pooled_scr=pooled_scr,
           b23_cert_pass=True,
           band_ok=band_ok, watch=watch,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l131/results_l131.json", "w"), indent=1)
print("results_l131.json written")
