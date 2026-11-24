
# ===================== L212 TAIL ==========================================
# CERT-MV (HALTING): the fast bincount matvec must be EXACTLY array-equal to
# the verbatim np.add.at kernel, and the gated reach/power-iteration must
# reproduce the verbatim functions at FLOAT EQUALITY, before any cohort value
# is read (the L210/L211 pattern).

SUB = build_v783(BETA_L, POOL_G, "V783_primary")
log(f"[sub] n {SUB['n']} edges {SUB['n_edges']} om>0 {int((SUB['om']>0).sum())}")
assert SUB["om"][GI_CARRIER] > 0 and SUB["om"][GI_MIR] > 0, "zero out-mass (STOP)"


def mv_slow(sub, x):
    y = np.zeros(sub["n"])
    np.add.at(y, sub["rows"], sub["jv"] * x[sub["cols"]])
    return y


def mv_fast(sub, x):
    return np.bincount(sub["rows"], weights=sub["jv"] * x[sub["cols"]],
                       minlength=sub["n"])


_rng = np.random.default_rng(21200)
n_mv = 0
for _p in range(4):
    if _p == 0:
        _x = np.zeros(SUB["n"]); _x[GI_CARRIER] = 1.0
    elif _p == 1:
        _x = np.zeros(SUB["n"]); _x[GI_MIR] = 1.0
    elif _p == 2:
        _x = np.ones(SUB["n"]) / math.sqrt(SUB["n"])
    else:
        _x = _rng.random(SUB["n"])
    assert np.array_equal(mv_slow(SUB, _x), mv_fast(SUB, _x)), (_p, "CERT-MV")
    n_mv += 1
log(f"[CERT-MV] GREEN {n_mv} EXACT array equalities (bincount == np.add.at)")


def reach_fast(c_local, sub, depth=2):
    """reach_sub's EXPRESSION with the gated matvec substituted."""
    x = np.zeros(sub["n"])
    x[c_local] = 1.0
    res = {}
    for d in range(1, depth + 1):
        x = mv_fast(sub, x)
        res[d] = {pk: float(x[sub["pool_l"][pk]].sum()) for pk in sub["pool_l"]}
    return res


def power_iter_fast(sub, jv, iters=400):
    """power_iter_sub's EXPRESSION with the gated matvec substituted."""
    n = sub["n"]
    v = np.ones(n) / math.sqrt(n)
    lam, hist = 0.0, []
    _s = dict(sub)
    _s["jv"] = jv
    for i in range(iters):
        w = mv_fast(_s, v)
        nrm = float(np.linalg.norm(w))
        if nrm == 0.0:
            return 0.0, []
        v = w / nrm
        lam = nrm
        if i >= iters - 6:
            hist.append(nrm)
    return lam, float((max(hist) - min(hist)) / max(hist))


# gate reach: float equality vs the VERBATIM reach_sub on both actors
n_gate = 0
for _nm, _gi in (("carrier", GI_CARRIER), ("mirror", GI_MIR)):
    _a = reach_sub(int(SUB["loc"][_gi]), SUB, 2)
    _b = reach_fast(int(SUB["loc"][_gi]), SUB, 2)
    for _d in (1, 2):
        for _pk in SUB["pool_l"]:
            assert _a[_d][_pk] == _b[_d][_pk], (_nm, _d, _pk, "reach gate (STOP)")
            n_gate += 1
# gate the power iteration: 12 iters, both kernels, float equality
_l1, _s1 = power_iter_sub(SUB, SUB["jv"], iters=12)
_l2, _s2 = power_iter_fast(SUB, SUB["jv"], iters=12)
assert _l1 == _l2 and _s1 == _s2, (_l1, _l2, "power gate (STOP)")
n_gate += 2
log(f"[CERT-GATE] GREEN {n_gate} float equalities: the fast kernels ARE the "
    f"verbatim l207_tail functions")
o["cert_mv"] = dict(n_checks=n_mv, mode="EXACT array_equal (==)")
o["cert_gate"] = dict(n_checks=n_gate, mode="float equality (==)",
                      source="l207_tail.py reach_sub / power_iter_sub verbatim")

# ---------------- lam1 and the registered NO-OP check ----------------------
LAM1, SPR = power_iter_fast(SUB, SUB["jv"], iters=400)
log(f"[lam1] {LAM1:.6f} (rel spread last6 {SPR:.3e})")
if SPR >= 1e-6:
    o["branch"] = "V_DEGENERATE"
    o["degenerate_reason"] = f"power iteration rel spread {SPR}"
    json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
    sys.exit("V_DEGENERATE: power iteration did not converge")
o["lam1"] = dict(value=LAM1, rel_spread_last6=SPR, iters=400)


def Rfast(sub, gi, lam1):
    """Rstat's EXPRESSION with the gated reach."""
    lc = int(sub["loc"][gi])
    assert lc >= 0, (sub["name"], gi, "cell absent (STOP)")
    rr = reach_fast(lc, sub, 2)
    p2 = float(sum(rr[2].values()))
    p1 = float(sum(rr[1].values()))
    m = float(sub["om"][gi])
    return dict(gi=int(gi), P1=p1, P2=p2, m_out=m,
                R=(p2 / (lam1 ** 2 * m)) if m > 0 else None,
                R1=(p1 / (lam1 * m)) if m > 0 else None)


for _nm, _gi in (("carrier", GI_CARRIER), ("mirror", GI_MIR)):
    _ra = Rstat(SUB, _gi, LAM1)
    _rb = Rfast(SUB, _gi, LAM1)
    for _k in ("P1", "P2", "m_out", "R", "R1"):
        assert _ra[_k] == _rb[_k], (_nm, _k, "Rstat gate (STOP)")
log("[CERT-GATE] GREEN Rfast == verbatim Rstat on both actors (10 checks)")

# registered NO-OP: R is invariant to a global rescale of A (L209's law)
_s3 = dict(SUB)
_s3["jv"] = SUB["jv"] * 3.0
_l3, _ = power_iter_fast(_s3, _s3["jv"], iters=400)
_r_a = Rfast(SUB, GI_CARRIER, LAM1)["R"]
_r_b = Rfast(_s3, GI_CARRIER, _l3)["R"]
_noop = abs(_r_b - _r_a) / abs(_r_a)
o["rescale_noop"] = dict(rel_diff=_noop, lam1_scaled=_l3,
                         note="R measured invariant under A -> 3A (L209)")
assert _noop < 1e-9, (_noop, "R not rescale-invariant (STOP)")
log(f"[NO-OP] GREEN R rescale-invariance rel diff {_noop:.2e}")
del _s3

# ---------------- PRIMARY leg ----------------------------------------------
R_CAR = Rfast(SUB, GI_CARRIER, LAM1)
R_MIR = Rfast(SUB, GI_MIR, LAM1)
COH_C = matched_cohort(SUB, GI_CARRIER)
COH_M = matched_cohort(SUB, GI_MIR)
COH_U = sorted(set(COH_C) | set(COH_M))
log(f"[cohort] carrier {len(COH_C)} mirror {len(COH_M)} union {len(COH_U)} "
    f"- measuring R on each")
CV = {}
for _i, _g in enumerate(COH_U):
    CV[_g] = Rfast(SUB, _g, LAM1)["R"]
    if _i % 25 == 0:
        log(f"  cohort {_i}/{len(COH_U)}")


def leg(r_car, r_mir, cohc, cohm, cv, sub):
    _vc = [cv[g] for g in cohc]
    _vm = [cv[g] for g in cohm]
    return dict(
        carrier_R=r_car["R"], mirror_R=r_mir["R"],
        carrier_P2=r_car["P2"], mirror_P2=r_mir["P2"],
        carrier_P1=r_car["P1"], mirror_P1=r_mir["P1"],
        carrier_m_out=r_car["m_out"], mirror_m_out=r_mir["m_out"],
        carrier_pct=pct_of(r_car["R"], _vc),
        mirror_pct=pct_of(r_mir["R"], _vm),
        cohort_k=COHORT_K, cohort_union_n=len(set(cohc) | set(cohm)),
        cohort_median_carrier=float(np.median(_vc)),
        cohort_median_mirror=float(np.median(_vm)),
        cohort_zero_frac_carrier=float(np.mean([v == 0.0 for v in _vc])),
        cohort_zero_frac_mirror=float(np.mean([v == 0.0 for v in _vm])),
        cohort_min_carrier=float(np.min(_vc)), cohort_max_carrier=float(np.max(_vc)),
        carrier_rank_of_cohort=int(1 + sum(1 for v in _vc if v < r_car["R"])),
        mirror_rank_of_cohort=int(1 + sum(1 for v in _vm if v < r_mir["R"])),
        deficit_vs_median=(float(np.median(_vc)) / r_car["R"]
                           if r_car["R"] > 0 else None),
        mass_match_logspread_carrier=float(np.max(np.abs(
            np.log([sub["om"][g] for g in cohc]) - math.log(r_car["m_out"])))),
        mass_match_logspread_mirror=float(np.max(np.abs(
            np.log([sub["om"][g] for g in cohm]) - math.log(r_mir["m_out"])))))


PRI = leg(R_CAR, R_MIR, COH_C, COH_M, CV, SUB)
PRI["readout"] = "PRIMARY v783 motor (110 cells, 5 nerve pools)"
PRI["per_pool_carrier"] = reach_fast(int(SUB["loc"][GI_CARRIER]), SUB, 2)[2]
PRI["per_pool_mirror"] = reach_fast(int(SUB["loc"][GI_MIR]), SUB, 2)[2]
o["Q1_primary"] = PRI
log(f"[PRIMARY] carrier R {PRI['carrier_R']:.6g} pct {PRI['carrier_pct']:.3f} "
    f"| mirror R {PRI['mirror_R']:.6g} pct {PRI['mirror_pct']:.3f} "
    f"| cohort med {PRI['cohort_median_carrier']:.6g} "
    f"| zero frac {PRI['cohort_zero_frac_carrier']:.3f}")

# ---------------- the branch (registered table) -----------------------------
_pc = PRI["carrier_pct"]
if (PRI["carrier_m_out"] == 0 or PRI["cohort_zero_frac_carrier"] > 0.50):
    BRANCH = "V_DEGENERATE"
elif _pc <= PCT_BAR:
    BRANCH = "V_AVOIDS"
elif _pc >= 0.90:
    BRANCH = "V_HIGH"
else:
    BRANCH = "V_MIDDLE"
o["branch"] = BRANCH
log(f"[BRANCH] {BRANCH} (carrier_pct {_pc})")

# ---------------- SECONDARY leg (descriptive, no branch) --------------------
SUB2 = build_v783(BETA_L, POOL_S, "V783_secondary_desc")
assert np.array_equal(SUB2["jv"], SUB["jv"]), "operator differs (STOP)"
R_CAR2 = Rfast(SUB2, GI_CARRIER, LAM1)
R_MIR2 = Rfast(SUB2, GI_MIR, LAM1)
CV2 = {g: Rfast(SUB2, g, LAM1)["R"] for g in COH_U}
SEC = leg(R_CAR2, R_MIR2, COH_C, COH_M, CV2, SUB2)
SEC["readout"] = "SECONDARY v783 descending minus actors (1301), DESCRIPTIVE"
o["Q2_secondary_descriptive"] = SEC
log(f"[SECONDARY] carrier pct {SEC['carrier_pct']:.3f} "
    f"mirror pct {SEC['mirror_pct']:.3f}")

# ---------------- BETA_L = 1.0 robustness leg (reported, no branch) ---------
SUB3 = build_v783(1.0, POOL_G, "V783_primary_beta1")
LAM3, SPR3 = power_iter_fast(SUB3, SUB3["jv"], iters=400)
R_CAR3 = Rfast(SUB3, GI_CARRIER, LAM3)
R_MIR3 = Rfast(SUB3, GI_MIR, LAM3)
COH_C3 = matched_cohort(SUB3, GI_CARRIER)
COH_M3 = matched_cohort(SUB3, GI_MIR)
CV3 = {g: Rfast(SUB3, g, LAM3)["R"] for g in sorted(set(COH_C3) | set(COH_M3))}
ROB = leg(R_CAR3, R_MIR3, COH_C3, COH_M3, CV3, SUB3)
ROB["readout"] = "PRIMARY readout, BETA_L=1.0 (pure |W|), ROBUSTNESS"
ROB["lam1"] = LAM3
ROB["rel_spread_last6"] = SPR3
ROB["cohort_identity_jaccard_carrier"] = float(
    len(set(COH_C3) & set(COH_C)) / len(set(COH_C3) | set(COH_C)))
ROB["d_carrier_pct_vs_primary"] = ROB["carrier_pct"] - PRI["carrier_pct"]
o["Q3_robust_beta1"] = ROB
log(f"[BETA1] carrier pct {ROB['carrier_pct']:.3f} "
    f"(d {ROB['d_carrier_pct_vs_primary']:+.3f}) lam1 {LAM3:.6f}")

# ---------------- predictions ----------------------------------------------
P = {}
P["Q212_1"] = dict(registered="V_AVOIDS", measured=BRANCH,
                   correct=bool(BRANCH == "V_AVOIDS"))
P["Q212_2"] = dict(registered="mirror_pct <= carrier_pct AND mirror low",
                   measured=dict(mirror_pct=PRI["mirror_pct"],
                                 carrier_pct=PRI["carrier_pct"]),
                   correct=bool(PRI["mirror_pct"] <= PRI["carrier_pct"]
                                and PRI["mirror_pct"] <= PCT_BAR))
P["Q212_3"] = dict(registered="secondary pct > primary pct",
                   measured=dict(secondary=SEC["carrier_pct"],
                                 primary=PRI["carrier_pct"]),
                   correct=bool(SEC["carrier_pct"] > PRI["carrier_pct"]))
P["Q212_4"] = dict(registered="|d carrier_pct| <= 0.10 under BETA_L=1",
                   measured=ROB["d_carrier_pct_vs_primary"],
                   correct=bool(abs(ROB["d_carrier_pct_vs_primary"]) <= 0.10))
P["Q212_5"] = dict(registered="cohort log-mass spread <= 0.15 both actors",
                   measured=dict(carrier=PRI["mass_match_logspread_carrier"],
                                 mirror=PRI["mass_match_logspread_mirror"]),
                   correct=bool(PRI["mass_match_logspread_carrier"] <= 0.15
                                and PRI["mass_match_logspread_mirror"] <= 0.15))
o["predictions"] = P
o["n_predictions_correct"] = int(sum(1 for v in P.values() if v["correct"]))
log(f"[predictions] {o['n_predictions_correct']} of 5")

o["bars"] = dict(pct_extreme=PCT_BAR, cohort_k=COHORT_K, beta_L=BETA_L,
                 degenerate_zero_frac=0.50)
o["comparators_L207"] = dict(
    G0_closure_carrier_pct=S207["Q1a_carrier_by_substrate"]["G0_closure"]["carrier_pct"],
    G1_cutwA_carrier_pct=S207["Q1a_carrier_by_substrate"]["G1_cutwA"]["carrier_pct"],
    F4_f4wA_carrier_pct=S207["Q1a_carrier_by_substrate"]["F4_f4wA"]["carrier_pct"],
    mirror_leg_closure=dict(
        mirror_pct=S207["Q2_mirror"]["per_substrate"]["G0_closure"]["mirror_pct"],
        carrier_pct=S207["Q2_mirror"]["per_substrate"]["G0_closure"]["carrier_pct"]),
    note="BANC leg-motor readout. NOT the same object as this card's readout; "
         "listed so the reader can see the direction, never as a test.")
o["limitations"] = [
    "EXPLORATORY (L78 non-transport law): the readout, the volume AND the body "
    "segment all changed at once, so neither direction can confirm or refute "
    "L207's leg-motor finding.",
    "ANATOMICAL leg only: no row mask, no settle, no seed, no rollouts - "
    "wiring geometry, NOT an operating point (L164).",
    "Operator powers are walks WITH revisits, not paths.",
    "v783 carries NO synapse floor, so the closest BANC comparator is the "
    "closure/cutwA substrate, not f4wA.",
    "The readout is 110 cells against BANC's 303-cell 20-pool readout, and "
    "head motor neurons are not leg motor neurons: a smaller, functionally "
    "different terminal set.",
    "A descending neuron's real output LEAVES this volume; its in-brain "
    "out-edges are not its functional output. This is the deepest limit of "
    "the whole v783 leg and it is why the card is exploratory.",
    "MASS-MATCHED COHORT percentile (k=100 nearest v783 descending cells in "
    "log out-mass), NOT the l169c degree-neutral rewire null - different "
    "nulls, never compared as if they were the same (L207).",
    "v783 'unknown' top_nt is scored at the build_graph_banc default "
    "magnitude 0.3; BANC's NT release has no unknown class.",
    "No BANC pin chain is inherited (the BANC head is not sliced because it "
    "loads banc_graph.pt); provenance rests on CERT-783 instead.",
]
o["pins"] = "ALL GREEN"
o["runtime_s"] = time.time() - T0
json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
log(f"[done] {o['runtime_s']:.1f}s -> {OUT}/static.json  branch={BRANCH}")
