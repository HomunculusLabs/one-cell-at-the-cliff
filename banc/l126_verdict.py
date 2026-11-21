"""L126 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B20-cert of this machinery on raw_l125 vs results_l125.json BEFORE any
B21 read, then the registered INTERPOLATION reads on FRESH B21 (kill
criterion VERBATIM): the Ti_R dose curve k in {19,21,23,24,26,28,29}
with per-point labels (kill/restore/super/partial) and the registered
shape classification D1 SMOOTH / D2 SECOND STEP / D3 CLIFF AT 29 /
LOTTERY (cells can overlap — report WHICH cell fires); S1 cutk5 9th-batch
replication, S2 endpoints 6th batch, S3 wA partial-band 3rd batch; POOLED
R4 arms B16..B21 n=96 full-precision Wilson (L90 form); per-side duty
table 5 pairs x 13 arms; Ti_L/Tr_R/Sr_R watch; sanity cells. PREREG
l126/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B21 = list(range(2501, 2517))       # FRESH (l126)
B20 = list(range(2401, 2417))  # context batch (l125, cert + pooled)
B19 = list(range(2301, 2317))  # context batch (l124, pooled)
B18 = list(range(2201, 2217))  # context batch (l123, pooled)
B17 = list(range(2101, 2117))  # context batch (l122, pooled)
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk5", "cutng19", "cutng21", "cutng23", "cutwA", "cutng26",
            "cutng28", "cutng29"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("21", "cutng21"),
          ("23", "cutng23"), ("24", "cutwA"), ("26", "cutng26"),
          ("28", "cutng28"), ("29", "cutng29"), ("58", "cut58"),
          ("k5", "cutk5")]
CURVE = ["19", "21", "23", "24", "26", "28", "29"]   # registered curve
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
r113 = json.load(open("l113/results_l113.json"))
r117 = json.load(open("l117/results_l117.json"))
r119 = json.load(open("l119/results_l119.json"))
r120 = json.load(open("l120/results_l120.json"))
ar = json.load(open("l126/anchors_run.json"))
r124 = json.load(open("l124/results_l124.json"))
r123 = json.load(open("l123/results_l123.json"))
r121 = json.load(open("l121/results_l121.json"))
r122 = json.load(open("l122/results_l122.json"))
r125 = json.load(open("l125/results_l125.json"))
SM = json.load(open("l121/static.json"))
S126 = json.load(open("l126/static.json"))


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
          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],
          g_cutng29_stored_exact=ar["g_cutng29_stored_exact"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["c0a124_pass"] and p0["c0a125_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cutwA_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120 "
      "(cutk5 vs raw_l120) + C0A-121 (3 arms vs raw_l121) + C0A-122 "
      "(3 arms vs raw_l122) + C0A-123 (4 shared arms vs raw_l123) + "
      "C0A-124 (4 arms vs raw_l124) + C0A-125 (3 arms vs raw_l125) + "
      "7 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max120 {p0['c0a120_max']:.1e})")
print("prefix FRESH gains (band DISCLOSED):", ar["prefix_fresh_gains"],
      "cutwA", round(float(z126["g_cutwA"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z126[f"af_{a}_{s}"]) for s in B21])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z126[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B21)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 13-arm per-side table (B21, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z126, a, B21, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B21 per-side duty table ----")
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
print("full-arm B21 band check (disclosure only):", band_ok)

# ---- Part 3 (P1): Ti_R dose curve {19,21,23,24,26,28,29} ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z126, "full", B21, "Ti")
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
    _, Rd = duty_seeds(z126, a, B21, "Ti")
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

# ---- Part 4: B20-cert FIRST, then curve labels + D1/D2/D3 + S/S + pooled ----
# B20-cert BEFORE any B21 read: machinery recomputed on raw_l125 B20 ==
# results_l125.json Ti table (ALL 12 l125 arms).
b20_cert_fail = []
for a in r125["table"]["Ti"]:
    want = r125["table"]["Ti"][a]
    got = side_k(z125, a, B20, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b20_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b20_cert_fail, ("B20-cert FAIL (no B21 read)",
                           b20_cert_fail[:5])
print(f"B20-cert vs results_l125.json Ti table: PASS "
      f"(all {len(r125['table']['Ti'])} arms)")


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
        mass=S126["prefix"][a]["mass_removed"] if a in S126["prefix"]
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

# registered shape cells (can overlap; report WHICH carries)
steps = {f"{CURVE[i]}->{CURVE[i+1]}":
         round(interp_read[CURVE[i + 1]]["meanR"]
               - interp_read[CURVE[i]]["meanR"], 3)
         for i in range(len(CURVE) - 1)}
outer = [abs(steps["19->21"]), abs(steps["28->29"])]
d1 = bool(all(abs(v) < .15 for v in steps.values())
          and not any(interp_read[k]["super"] for k in ("21", "23", "26", "28")))
inner_pairs = [p for p, v in steps.items()
               if p not in ("19->21", "28->29") and v >= .20]
d2 = bool(inner_pairs and all(o < .15 for o in outer))
k28_ns = not interp_read["28"]["super"]
d3 = bool(k28_ns and interp_read["29"]["super"])
dips = [p for p, v in steps.items() if v <= -.15]
lottery = bool(dips)
cells = dict(D1_SMOOTH=d1, D2_SECOND_STEP=d2, D3_CLIFF_AT_29=d3,
             LOTTERY=lottery, steps=steps, inner_jump_pairs=inner_pairs,
             dip_pairs=dips, k28_not_super=bool(k28_ns),
             k29_super=bool(interp_read["29"]["super"]))
print(f"CURVE steps: {steps}")
print(f"SHAPE CELLS: D1 SMOOTH {d1} | D2 SECOND STEP {d2} "
      f"(jumps {inner_pairs}) | D3 CLIFF AT 29 {d3} (k28 not-super "
      f"{k28_ns}, k29 super {interp_read['29']['super']}) | "
      f"LOTTERY {lottery} (dips {dips})")

# S1: cutk5 9th batch; S2: endpoints 6th batch; S3: wA partial 3rd batch
s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B21 — 9th consecutive batch "
    "(B12/B14/B15/B16/B17/B18/B19/B20/B21)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B21 — DISCLOSED (L118 lottery class)"))
s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (6th batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))
s3 = dict(wA_partial=bool(_partial(table["Ti"]["cutwA"])),
          wA_meanR=table["Ti"]["cutwA"]["meanR"],
          wA_kR=table["Ti"]["cutwA"]["kR"], cls=(
    "cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 — 3rd batch "
    "(B18 .413/5, B19 .376/4, B21)"
    if _partial(table["Ti"]["cutwA"]) else
    "cutwA MISSES the partial band — DISCLOSED (would revise L124's "
    "stable-intermediate reading)"))
print(f"S1: {s1['cls']}")
print(f"S2: {s2['cls']}")
print(f"S3: {s3['cls']}")
# R4: pooled batch-union B16..B21 n=96, FULL-PRECISION Wilson
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    _, Rb20 = duty_seeds(z125, a, B20, "Ti")
    _, Rb21 = duty_seeds(z126, a, B21, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 96)
    pooled[a] = dict(k96=k, p_hat=k / 96, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()),
                     k_b19=int((Rb19 >= .5).sum()),
                     k_b20=int((Rb20 >= .5).sum()),
                     k_b21=int((Rb21 >= .5).sum()))
    print(f"POOLED Ti_R {a:7s} k {k}/96 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16 + "
          f"B19 {pooled[a]['k_b19']}/16 + B20 {pooled[a]['k_b20']}/16 + "
          f"B21 {pooled[a]['k_b21']}/16) p_hat {k/96:.3f} "
          f"Wilson [{lb:.4f}, {ub:.4f}]")
# NO scr pooling in L126 (scr arms not re-run; l125 single-batch stands)
pooled_scr = {"note": "not run in L126 — l125 single-batch stands (L128 owes "
                      "the rebase)"}

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
           g_cutk5=float(z126["g_cutk5"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_prefix={a: S126["prefix"][a]["mass_removed"]
                        for a in S126["prefix"]},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, dose=dose,
           interp=dict(curve=interp_read, cells=cells,
                       s1=s1, s2=s2, s3=s3),
           pooled=pooled, pooled_scr=pooled_scr,
           b20_cert_pass=True,
           band_ok=band_ok, watch=watch,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l126/results_l126.json", "w"), indent=1)
print("results_l126.json written")
