"""L127 verdict: C0B certification on stored raw_l113 (L85/L109 rule) +
B21-cert of this machinery on raw_l126 vs results_l126.json BEFORE any
B22 read, then the registered COHERENCE-vs-HEAVINESS reads on FRESH B22
(kill criterion VERBATIM): per-arm labels for {cutscr0, cutcl40,
cutscrL1, cutscrL2} (kill/restore/super/partial) and the registered
classification cells C1 COHERENCE / C2 HEAVINESS / C3 MASS-SUFFICIENCY /
MIXED (report WHICH cell carries; L55/L109 rule); S1 cutk5 10th-batch
replication, S2 endpoints 7th batch; POOLED R4 arms B16..B22 n=112
full-precision Wilson (L90 form) + NEW pooled cutscr0 B20+B22 n=32;
per-side duty table 5 pairs x 12 arms; Ti_L/Tr_R/Sr_R watch; sanity
cells. PREREG l127/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B10 = list(range(1401, 1417))
B22 = list(range(2601, 2617))       # FRESH (l127)
B21 = list(range(2501, 2517))  # context batch (l126, cert + pooled)
B20 = list(range(2401, 2417))  # context batch (l125, scr0 pooled)
B19 = list(range(2301, 2317))  # context batch (l124, pooled)
B18 = list(range(2201, 2217))  # context batch (l123, pooled)
B17 = list(range(2101, 2117))  # context batch (l122, pooled)
B16 = list(range(2001, 2017))  # context batch (l121, pooled union)
STORED_ARMS = ["full", "b65", "cut", "cut19", "cut58"]
NEW_ARMS = ["cutk5", "cutng19", "cutng29", "cutscr0", "cutcl40",
            "cutscrL1", "cutscrL2"]
ARMS = STORED_ARMS + NEW_ARMS
LADDER = [("0", "full"), ("19", "cutng19"), ("29", "cutng29"),
          ("58", "cut58"), ("k5", "cutk5"), ("scr0", "cutscr0"),
          ("cl40", "cutcl40"), ("sL1", "cutscrL1"), ("sL2", "cutscrL2")]
SCR_ARMS = ["cutscr0", "cutcl40", "cutscrL1", "cutscrL2"]
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
r113 = json.load(open("l113/results_l113.json"))
ar = json.load(open("l127/anchors_run.json"))
r121 = json.load(open("l121/results_l121.json"))
r122 = json.load(open("l122/results_l122.json"))
r123 = json.load(open("l123/results_l123.json"))
r124 = json.load(open("l124/results_l124.json"))
r125 = json.load(open("l125/results_l125.json"))
r126 = json.load(open("l126/results_l126.json"))
SM = json.load(open("l121/static.json"))
S127 = json.load(open("l127/static.json"))


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


# ---- Part 1: C0B on stored raw_l113 (BEFORE any L127 pin) ----
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

# ---- Part 1b: B21-cert BEFORE any B22 read (machinery == l126 stored) ----
b21_cert_fail = []
for a in r126["table"]["Ti"]:
    want = r126["table"]["Ti"][a]
    got = side_k(z126, a, B21, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            b21_cert_fail.append((a, kk, got[kk], want[kk]))
assert not b21_cert_fail, ("B21-cert FAIL (no B22 read)",
                           b21_cert_fail[:5])
print(f"B21-cert vs results_l126.json Ti table: PASS "
      f"(all {len(r126['table']['Ti'])} arms)")

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
          g_cutng19_stored_exact=ar["g_cutng19_stored_exact"],
          g_cutng29_stored_exact=ar["g_cutng29_stored_exact"],
          g_cutscr0_stored_exact=ar["g_cutscr0_stored_exact"],
          g_cut_stored_exact=bool(ar["g_cut"] == 0.14510760426521305),
          g_cut19_stored_exact=bool(ar["g_cut19"] == 0.15096808075904844))
p0["pass"] = bool(p0["c0a_pass"] and p0["c0a120_pass"] and p0["c0a121_pass"]
                  and p0["c0a122_pass"] and p0["c0a123_pass"]
                  and p0["c0a124_pass"] and p0["c0a125_pass"]
                  and p0["c0a126_pass"]
                  and p0["g_cut58_stored_exact"]
                  and p0["g_cutk5_stored_exact"]
                  and p0["g_cutng19_stored_exact"] and p0["g_cutng29_stored_exact"]
                  and p0["g_cutscr0_stored_exact"]
                  and p0["g_cut_stored_exact"] and p0["g_cut19_stored_exact"])
print("P0 anchors vs raw_l113 (5 stored arms, 801/901) + C0A-120..C0A-124 "
      "+ EXTENDED C0A-125 (4 arms incl scr0) + NEW C0A-126 + 7 stored gains:",
      "PASS" if p0["pass"] else "FAIL",
      f"(max113 {p0['c0a_max']:.1e} max125 {p0['c0a125_max']:.1e} "
      f"max126 {p0['c0a126_max']:.1e})")
print("scr FRESH gains (band DISCLOSED):", ar["scr_fresh_gains"],
      "scr0 stored", round(float(z127["g_cutscr0"]), 6),
      "band_ok", ar["new_band_ok"],
      "stairs", {k: f"{v:.1e}" for k, v in ar["new_stairs"].items()})

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z127[f"af_{a}_{s}"]) for s in B22])), 6)
           for a in ARMS}
af_range_ok = all(0.01 < float(z127[f"af_{a}_{s}"]) < 0.9 for a in ARMS for s in B22)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band), af_mean=af_mean)
print("P4", json.dumps(p4))

# ---- Part 2: full 5-pair x 12-arm per-side table (B22, n=16) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS:
        t = side_k(z127, a, B22, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B22 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS:
        t = table[pk][a]
        print(f"{pk} {a:8s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- batch-band disclosure: full-arm B22 reads vs registered bands ----
band = {"Ti": dict(L=(0.25, 0.48), R=(0.35, 0.58)),
        "Sr": dict(L=(0.08, 0.25), R=(0.30, 0.50))}
band_ok = {pk: {sd: band[pk][sd][0] <= table[pk]["full"][f"mean{sd}"]
                <= band[pk][sd][1] for sd in ("L", "R")} for pk in band}
print("full-arm B22 band check (disclosure only):", band_ok)

# ---- Part 3 (P1): kill/super/partial labels + legs on the scr family ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z127, "full", B22, "Ti")


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


scr_read = {}
killmap = {}
for kk, a in LADDER:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z127, a, B22, "Ti")
    legs = dict(mean_paired_dR=round(float((Rd - Rfull).mean()), 3),
                n_down=int(((Rd - Rfull) <= -.20).sum()),
                n_up=int(((Rd - Rfull) >= .20).sum()))
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR"] <= -.20)
    killmap[kk] = bool(kill)
    if a in SCR_ARMS:
        scr_read[a] = dict(
            meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"], kL=t["kL"],
            legs=legs, kill=bool(kill), restore=_restore(t),
            super=_super(t), partial=_partial(t),
            mass=S127["scr"][a]["mass_removed"],
            extra_mass=S127["scr"][a]["extra_mass"])
        print(f"SCR {a:9s} (mass {S127['scr'][a]['mass_removed']:.4f} extra "
              f"{S127['scr'][a]['extra_mass']:.4f}): meanR {t['meanR']:.3f} "
              f"kR {t['kR']:2d}/16 | meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 "
              f"| paired dR {legs['mean_paired_dR']:+.3f} "
              f"n_down {legs['n_down']}/16 -> "
              f"{'KILL' if kill else 'no-kill'}"
              f"{'/RESTORE' if _restore(t) else ''}"
              f"{'/SUPER' if _super(t) else ''}"
              f"{'/PARTIAL' if _partial(t) else ''}")

# ---- registered classification cells (PREREG; report WHICH carries) ----
cl40_sup = bool(scr_read["cutcl40"]["super"])
sl_sup = {a: bool(scr_read[a]["super"]) for a in ("cutscrL1", "cutscrL2")}
scr0_sup = bool(scr_read["cutscr0"]["super"])
c1 = bool(cl40_sup and not sl_sup["cutscrL1"] and not sl_sup["cutscrL2"])
c2 = bool((not cl40_sup) and not sl_sup["cutscrL1"]
          and not sl_sup["cutscrL2"])
c3 = bool(sl_sup["cutscrL1"] or sl_sup["cutscrL2"])
mixed = not (c1 or c2 or c3)
cells = dict(C1_COHERENCE=c1, C2_HEAVINESS=c2, C3_MASS_SUFFICIENCY=c3,
             MIXED=mixed,
             scr0_super=scr0_sup,
             scr0_expected_super=bool(scr0_sup),
             cl40_super=cl40_sup,
             sL1_super=sl_sup["cutscrL1"], sL2_super=sl_sup["cutscrL2"],
             labels={a: ("KILL" if scr_read[a]["kill"] else "no-kill")
                     + ("/SUPER" if scr_read[a]["super"] else "")
                     + ("/RESTORE" if scr_read[a]["restore"] else "")
                     + ("/PARTIAL" if scr_read[a]["partial"] else "")
                     for a in SCR_ARMS})
cls_txt = ("C1 COHERENCE (cl40 supers, scrLs do not — geometry owns the "
           "flip at matched mass)" if c1 else
           "C2 HEAVINESS (nothing at .045-extra supers — the .0544/.0642 "
           "HEAVY coherent deciles flip, .0450 does not)" if c2 else
           "C3 MASS-SUFFICIENCY (a scattered scrL supers — lottery at "
           "matched mass, coherence claim dies)" if c3 else
           "MIXED — intermediate regime, per-arm labels carry, no class "
           "claim")
print(f"CLASSIFICATION: {cls_txt}")
if not scr0_sup:
    print("scr0 context MISS (expected SUPER 2nd batch) — scr-family "
          "batch-fragility disclosure QUALIFIES every cell above")

# ---- S1/S2 + R4 pooled B16..B22 n=112 + NEW pooled scr0 n=32 ----
s1 = dict(k5_kill=bool(killmap["k5"]), cls=(
    "cutk5 KILLS on B22 — 10th consecutive batch "
    "(B12/B14/B15/B16/B17/B18/B19/B20/B21/B22)"
    if killmap["k5"] else
    "cutk5 does NOT kill on B22 — DISCLOSED (L118 lottery class)"))
s2 = dict(ng19_kill=bool(killmap["19"]),
          ng29_super=bool(_super(table["Ti"]["cutng29"])),
          ng29_restore=bool(_restore(table["Ti"]["cutng29"])), cls=(
    "cutng19 KILLs + cutng29 SUPER-RAISES in-batch (7th batch each)"
    if killmap["19"] and _super(table["Ti"]["cutng29"]) else
    "endpoint miss DISCLOSED (registered S2, never silent)"))
print(f"S1: {s1['cls']}")
print(f"S2: {s2['cls']}")
pooled = {}
for a in ("full", "cutng19", "cutng29", "cutk5", "cut58"):
    _, Rb16 = duty_seeds(z121, a, B16, "Ti")
    _, Rb17 = duty_seeds(z122, a, B17, "Ti")
    _, Rb18 = duty_seeds(z123, a, B18, "Ti")
    _, Rb19 = duty_seeds(z124, a, B19, "Ti")
    _, Rb20 = duty_seeds(z125, a, B20, "Ti")
    _, Rb21 = duty_seeds(z126, a, B21, "Ti")
    _, Rb22 = duty_seeds(z127, a, B22, "Ti")
    allb = np.concatenate([Rb16, Rb17, Rb18, Rb19, Rb20, Rb21, Rb22])
    k = int((allb >= .5).sum())
    lb, ub = wilson(k, 112)
    pooled[a] = dict(k112=k, p_hat=k / 112, lb=lb, ub=ub,
                     k_b16=int((Rb16 >= .5).sum()),
                     k_b17=int((Rb17 >= .5).sum()),
                     k_b18=int((Rb18 >= .5).sum()),
                     k_b19=int((Rb19 >= .5).sum()),
                     k_b20=int((Rb20 >= .5).sum()),
                     k_b21=int((Rb21 >= .5).sum()),
                     k_b22=int((Rb22 >= .5).sum()))
    print(f"POOLED Ti_R {a:8s} k {k}/112 (B16 {pooled[a]['k_b16']}/16 + "
          f"B17 {pooled[a]['k_b17']}/16 + B18 {pooled[a]['k_b18']}/16 + "
          f"B19 {pooled[a]['k_b19']}/16 + B20 {pooled[a]['k_b20']}/16 + "
          f"B21 {pooled[a]['k_b21']}/16 + B22 {pooled[a]['k_b22']}/16) "
          f"p_hat {k/112:.3f} Wilson [{lb:.4f}, {ub:.4f}]")
# NEW pooled cutscr0: B20 + B22 union n=32 (2-batch; L128 owes the rest)
_, Rsc_b20 = duty_seeds(z125, "cutscr0", B20, "Ti")
_, Rsc_b22 = duty_seeds(z127, "cutscr0", B22, "Ti")
sc_all = np.concatenate([Rsc_b20, Rsc_b22])
k_sc = int((sc_all >= .5).sum())
lb, ub = wilson(k_sc, 32)
pooled_scr0 = dict(k32=k_sc, p_hat=k_sc / 32, lb=lb, ub=ub,
                   k_b20=int((Rsc_b20 >= .5).sum()),
                   k_b22=int((Rsc_b22 >= .5).sum()))
print(f"POOLED Ti_R cutscr0 k {k_sc}/32 (B20 {pooled_scr0['k_b20']}/16 + "
      f"B22 {pooled_scr0['k_b22']}/16) p_hat {k_sc/32:.3f} "
      f"Wilson [{lb:.4f}, {ub:.4f}]")

# watch axes (registered, no gate)
watch = dict(
    Ti_L={kk: dict(L=scr_read[a]["meanL"] if a in scr_read
                   else table["Ti"][a]["meanL"],
                   kL=scr_read[a]["kL"] if a in scr_read
                   else table["Ti"][a]["kL"]) for kk, a in LADDER},
    Sr_R={}, Tr_R={}, l125_scr_context=dict(
        scr0_B20=dict(meanR=r125["table"]["Ti"]["cutscr0"]["meanR"],
                      kR=r125["table"]["Ti"]["cutscr0"]["kR"]),
        scr1_B20=dict(meanR=r125["table"]["Ti"]["cutscr1"]["meanR"],
                      kR=r125["table"]["Ti"]["cutscr1"]["kR"]),
        note="scr1 (scattered, .0476 extra) KILLED on B20 — the "
             "heavy-scattered 2x2 cell, cross-batch"))
for kk, a in LADDER:
    watch["Sr_R"][kk] = table["Sr"][a]["meanR"]
    watch["Tr_R"][kk] = table["Tr"][a]["meanR"]
watch["ng29_L_death_anticorr"] = dict(
    ng29_L=table["Ti"]["cutng29"]["meanL"],
    ng29_L_k=table["Ti"]["cutng29"]["kL"],
    ng29_R=table["Ti"]["cutng29"]["meanR"])
print("WATCH Ti_L:", {kk: v["L"] for kk, v in watch["Ti_L"].items()})
print("WATCH Sr_R:", watch["Sr_R"])
print("WATCH Tr_R:", watch["Tr_R"])

# ---- Part 5: sanity reference cells (secondary; miss = disclose) ----
ls = dict(cut_kL=table["Ti"]["cut"]["kL"], b65_kL=table["Ti"]["b65"]["kL"],
          b65_kR=table["Ti"]["b65"]["kR"], cut19_kL=table["Ti"]["cut19"]["kL"],
          sr_b65_kL=table["Sr"]["b65"]["kL"], sr_b65_kR=table["Sr"]["b65"]["kR"])
ls_pass = (ls["cut_kL"] >= 14 and ls["b65_kL"] == 16 and ls["b65_kR"] == 16
           and ls["cut19_kL"] >= 12)
print("sanity:", ls, "PASS" if ls_pass else "MISS (disclosed, never abort)")

out = dict(c0b_pass=c0b_pass, c0b_fail=c0b_fail[:5], p0=p0, p4=p4,
           new_band_ok=ar["new_band_ok"],
           scr_fresh_gains=ar["scr_fresh_gains"],
           g_cutk5=float(z127["g_cutk5"]),
           g_cutscr0=float(z127["g_cutscr0"]),
           new_stairs=ar["new_stairs"],
           mass={a: SM["ngladder"][k]["mass_removed"]
                 for a, k in (("cutng19", "k19"), ("cutng29", "k29"),
                              ("cut58", "k58"))},
           mass_scr={a: S127["scr"][a]["mass_removed"] for a in SCR_ARMS},
           extra_mass_scr={a: S127["scr"][a]["extra_mass"] for a in SCR_ARMS},
           mass_cutk5=SM["ladder"]["k5"]["mass_removed"],
           table=table, m0=m0, scr_read=scr_read,
           coherence=dict(cells=cells, cls=cls_txt, s1=s1, s2=s2),
           pooled=pooled, pooled_scr0=pooled_scr0,
           b21_cert_pass=True,
           band_ok=band_ok, watch=watch,
           sanity=ls, sanity_pass=bool(ls_pass))
json.dump(out, open("l127/results_l127.json", "w"), indent=1)
print("results_l127.json written")
