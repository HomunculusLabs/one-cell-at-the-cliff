
# ===================== L222 TAIL ==========================================
# Everything above this line is VERBATIM inherited source (l212_head.py sliced
# to CUT its blocker-writer and to re-point OUT, the three l207_tail.py
# function slices, and l212_tail.py lines 1-227 = L212's ENTIRE measurement
# pipeline). So CERT-783, CERT-L207, CERT-MV, CERT-GATE, the lam1 power
# iteration, the rescale NO-OP and L212's Q1/Q2/Q3 legs all re-ran as SOURCE
# before a single L222 number exists.

assert OUT.endswith("/l222") and os.path.isdir(OUT), (OUT, "OUT (STOP)")
PARENT_BRANCH = o.get("branch")
o["design"] = ("L222 the BILATERAL BREAK: is the v783 DNp33 left/right "
               "asymmetry a SYNAPSE-FLOOR artifact? static, zero rollouts.")
o["prereg"] = "l222/PREREG.md"
o["parent_branch_reproduced"] = PARENT_BRANCH
FLOORS = [1, 2, 4]
GAP_ARTIFACT_BAR = 0.10
GAP_SURVIVES_BAR = 0.15
# NOTE: l212_tail sets o["bars"] at line 254, BEYOND the inherited 1-227 slice,
# so this card builds its own bars dict rather than mutating a missing one.
o["bars"] = dict(gap_artifact=GAP_ARTIFACT_BAR, gap_survives=GAP_SURVIVES_BAR,
                 floors=FLOORS, pct_extreme=PCT_BAR, cohort_k=COHORT_K,
                 beta_L=BETA_L, degenerate_zero_frac=0.50,
                 power_rel_spread=1e-6)

# ---------------- CERT-212 (HALTING): reproduce the parent exactly ----------
_stp = os.stat(f"{LAB}/l212/static.json")
_fpp = (_stp.st_size, _stp.st_mtime_ns)
with open(f"{LAB}/l212/static.json") as _fh:
    S212 = json.load(_fh)
n212 = 0
_bad = []


def _eq(path, got, want):
    global n212
    n212 += 1
    if isinstance(want, float) or isinstance(got, float):
        ok = (float(got) == float(want))
    else:
        ok = (got == want)
    if not ok:
        _bad.append((path, got, want))


def _walk(path, got, want):
    if isinstance(want, dict):
        assert isinstance(got, dict), (path, "shape (STOP)")
        assert set(got.keys()) == set(want.keys()), (path, "keys (STOP)")
        for k in sorted(want.keys()):
            _walk(f"{path}.{k}", got[k], want[k])
    elif isinstance(want, list):
        assert isinstance(got, list) and len(got) == len(want), (path, "len")
        for i, (g, w) in enumerate(zip(got, want)):
            _walk(f"{path}[{i}]", g, w)
    else:
        _eq(path, got, want)


_mine = dict(Q1_primary=o["Q1_primary"],
             Q2_secondary_descriptive=o["Q2_secondary_descriptive"],
             Q3_robust_beta1=o["Q3_robust_beta1"],
             lam1=o["lam1"], rescale_noop=o["rescale_noop"],
             readout_primary=o["readout_primary"],
             readout_secondary=o["readout_secondary"],
             cert_783=o["cert_783"], cert_mv=o["cert_mv"],
             cert_gate=o["cert_gate"], cert_l207=o["cert_l207"],
             nt_mix=o["nt_mix"], beta_L=o["beta_L"])
for _k in sorted(_mine):
    _walk(_k, _mine[_k], S212[_k])
assert not _bad, ("CERT-212 MISMATCH (STOP)", _bad[:12])
assert PARENT_BRANCH == S212["branch"] == "V_AVOIDS", (PARENT_BRANCH, "STOP")
n212 += 1
_stp2 = os.stat(f"{LAB}/l212/static.json")
assert (_stp2.st_size, _stp2.st_mtime_ns) == _fpp, "l212/static.json MUTATED"
o["cert_212"] = dict(n_checks=n212, mode="float/int equality (==), recursive",
                     source="l212/static.json (read-only, mtime asserted)",
                     note="L212's whole Q1/Q2/Q3 table reproduced by RE-RUNNING "
                          "its pipeline as a verbatim source slice, never by "
                          "re-implementing it (L211 lesson).")
log(f"[CERT-212] GREEN {n212} stored L212 values reproduced at float equality")

# the floor-1 anchors, read from MY rebuild (identical to the parent by CERT-212)
PCT_CAR_1 = o["Q1_primary"]["carrier_pct"]
PCT_MIR_1 = o["Q1_primary"]["mirror_pct"]
GAP_1 = abs(PCT_MIR_1 - PCT_CAR_1)
assert o["Q1_primary"]["carrier_P1"] == 0.0, "carrier P1 != 0 at floor 1 (STOP)"
assert o["Q1_primary"]["mirror_P1"] == math.log1p(1.0), "mirror P1 (STOP)"
del SUB2, SUB3, CV2, CV3

# ---------------- the floored builders -------------------------------------
assert float(w_syn.min()) >= 1.0, (float(w_syn.min()), "PREREG 0d (STOP)")
MOT_MASK = mot_all.copy()
assert int(MOT_MASK.sum()) == 110


def build_v783_floor(beta, pools, name, floor, dst_only=None):
    """build_v783's EXPRESSION with a syn_count floor on the COLLAPSED pair
    (PREREG 0a). dst_only=None -> GLOBAL floor; dst_only=mask -> the floor
    applies ONLY to edges landing in that mask (PREREG 0c LOCAL floor).
    floor == 1 with dst_only=None is a provable no-op (w_syn.min() >= 1)."""
    hit = w_syn >= float(floor)
    keep_e = hit if dst_only is None else (hit | (~dst_only[dst_all]))
    s_e = src_all[keep_e]
    d_e = dst_all[keep_e]
    _sa = sign_all[s_e]
    _sb = np.where(is_glut[s_e], -np.abs(_sa), _sa)
    ev = (np.log1p(w_syn[keep_e]) * _sb).astype(np.float64)
    vv = ev.copy()
    vv[vv < 0] *= beta
    jv = np.abs(vv)
    om = np.zeros(Nall)
    np.add.at(om, s_e, jv)
    loc = np.arange(Nall, dtype=np.int64)
    keep = np.ones(Nall, bool)
    pl = {pk: np.where(P)[0] for pk, P in pools.items()}
    return dict(name=name, keep=keep, loc=loc, n=Nall, n_edges=int(keep_e.sum()),
                jv=jv, rows=d_e, cols=s_e, pool_l=pl, floor=int(floor),
                pool_all=np.unique(np.concatenate([pl[k] for k in pl])), om=om,
                keep_e=keep_e, local=(dst_only is not None))


# CERT-FLOORGEN (HALTING): floor 1 == the verbatim build_v783, EXACTLY
_g1 = build_v783_floor(BETA_L, POOL_G, "gen_f1", 1)
n_fg = 0
for _k in ("jv", "rows", "cols", "om"):
    assert np.array_equal(_g1[_k], SUB[_k]), (_k, "CERT-FLOORGEN (STOP)")
    n_fg += 1
assert _g1["n_edges"] == SUB["n_edges"] == NEDGE, "CERT-FLOORGEN n_edges (STOP)"
n_fg += 1
for _pk in SUB["pool_l"]:
    assert np.array_equal(_g1["pool_l"][_pk], SUB["pool_l"][_pk]), (_pk, "STOP")
    n_fg += 1
assert bool(_g1["keep_e"].all()), "floor 1 is not a no-op mask (STOP)"
n_fg += 1
# and the LOCAL builder at floor 1 is the same no-op
_g1l = build_v783_floor(BETA_L, POOL_G, "gen_f1_local", 1, dst_only=MOT_MASK)
for _k in ("jv", "rows", "cols", "om"):
    assert np.array_equal(_g1l[_k], SUB[_k]), (_k, "CERT-FLOORGEN local (STOP)")
    n_fg += 1
o["cert_floorgen"] = dict(n_checks=n_fg, mode="EXACT array_equal (==)",
                          note="the generic floored builder at F=1 IS the "
                               "verbatim build_v783 (L207 CERT-GEN pattern)")
log(f"[CERT-FLOORGEN] GREEN {n_fg} exact array equalities")
del _g1, _g1l

# CERT-MONOTONE (HALTING): the floors are strictly NESTED and om is monotone
KEEPS = {F: (w_syn >= float(F)) for F in FLOORS}
OMS = {}
n_mon = 0
for F in FLOORS:
    _sf = build_v783_floor(BETA_L, POOL_G, f"mon_f{F}", F)
    OMS[F] = _sf["om"].copy()
    del _sf
for a, b in ((1, 2), (2, 4)):
    assert bool((KEEPS[b] <= KEEPS[a]).all()), (a, b, "not nested (STOP)")
    n_mon += 1
    assert bool((OMS[b] <= OMS[a] + 0.0).all()), (a, b, "om not monotone (STOP)")
    n_mon += 1
    assert int(KEEPS[b].sum()) < int(KEEPS[a].sum()), (a, b, "floor inert (STOP)")
    n_mon += 1
o["cert_monotone"] = dict(n_checks=n_mon, n_cells_checked=Nall,
                          mode="elementwise <= over 139255 cells / 15091983 edges",
                          note="a floor that is not nested is not a floor")
log(f"[CERT-MONOTONE] GREEN {n_mon} nesting/monotonicity gates over {Nall} cells")

# ---------------- leg (a): the ANATOMICAL per-target edge table -------------
_ct_full = np.array([""] * Nall, dtype=object)
_nv_full = np.array([""] * Nall, dtype=object)
_sd_full = np.array([""] * Nall, dtype=object)
_ct_full[ann_gi] = ctype
_nv_full[ann_gi] = nerve
_sd_full[ann_gi] = side
ACT = (("carrier", GI_CARRIER), ("mirror", GI_MIR))
EDGE_TBL = {}
OUTDEG = {}
for _nm, _gi in ACT:
    _sel = np.where((src_all == _gi) & MOT_MASK[dst_all])[0]
    rows_t = []
    for _e in _sel:
        _d = int(dst_all[_e])
        rows_t.append(dict(
            dst_gi=_d, dst_root_id=str(int(ids_all[_d])),
            cell_type=str(_ct_full[_d]), nerve=str(_nv_full[_d]),
            side=str(_sd_full[_d]),
            syn_count=float(w_syn[_e]), log1p_w=float(np.log1p(w_syn[_e])),
            survives_f2=bool(w_syn[_e] >= 2.0),
            survives_f4=bool(w_syn[_e] >= 4.0)))
    rows_t.sort(key=lambda r: (-r["syn_count"], r["dst_gi"]))
    EDGE_TBL[_nm] = rows_t
    _all_out = np.where(src_all == _gi)[0]
    _ws = w_syn[_all_out]
    OUTDEG[_nm] = dict(
        n_out_edges=int(len(_all_out)),
        n_out_edges_f2=int((_ws >= 2.0).sum()),
        n_out_edges_f4=int((_ws >= 4.0).sum()),
        syn_min=float(_ws.min()), syn_median=float(np.median(_ws)),
        syn_max=float(_ws.max()),
        frac_edges_syn1=float((_ws == 1.0).mean()),
        frac_edges_below4=float((_ws < 4.0).mean()),
        out_mass_f1=float(OMS[1][_gi]), out_mass_f2=float(OMS[2][_gi]),
        out_mass_f4=float(OMS[4][_gi]),
        mass_retention_f4=float(OMS[4][_gi] / OMS[1][_gi]),
        n_direct_motor_edges=int(len(EDGE_TBL[_nm])))
o["Qa_anatomical"] = dict(
    edge_table=EDGE_TBL, out_degree=OUTDEG,
    readout="the 110-cell v783 super_class==motor set (5 nerve pools)",
    note="COLLAPSED-pair syn_count per PREREG 0a: one synapse TOTAL across all "
         "neuropils, which is the reading that makes 'at the detection floor' "
         "correct.")
log(f"[leg a] carrier direct motor edges {len(EDGE_TBL['carrier'])} | "
    f"mirror {len(EDGE_TBL['mirror'])} "
    f"| mirror syns {[r['syn_count'] for r in EDGE_TBL['mirror']]}")

# ---------------- the per-floor legs ---------------------------------------
DEG = None


def floor_leg(F, beta, dst_only, tag):
    """one floor x one beta: substrate report + both actors + both cohorts."""
    global DEG
    SUBF = build_v783_floor(beta, POOL_G, tag, F, dst_only=dst_only)
    # CERT-MV re-run AT THIS FLOOR (never assumed from floor 1)
    _r = np.random.default_rng(22200 + F)
    nmv = 0
    for _p in range(3):
        if _p == 0:
            _x = np.zeros(SUBF["n"]); _x[GI_CARRIER] = 1.0
        elif _p == 1:
            _x = np.zeros(SUBF["n"]); _x[GI_MIR] = 1.0
        else:
            _x = _r.random(SUBF["n"])
        assert np.array_equal(mv_slow(SUBF, _x), mv_fast(SUBF, _x)), (tag, _p)
        nmv += 1
    # CERT-GATE re-run AT THIS FLOOR: fast kernels == verbatim l207 functions
    ngt = 0
    for _nm, _gi in ACT:
        _a = reach_sub(int(SUBF["loc"][_gi]), SUBF, 2)
        _b = reach_fast(int(SUBF["loc"][_gi]), SUBF, 2)
        for _d in (1, 2):
            for _pk in SUBF["pool_l"]:
                assert _a[_d][_pk] == _b[_d][_pk], (tag, _nm, _d, _pk, "STOP")
                ngt += 1
    _l1, _s1 = power_iter_sub(SUBF, SUBF["jv"], iters=12)
    _l2, _s2 = power_iter_fast(SUBF, SUBF["jv"], iters=12)
    assert _l1 == _l2 and _s1 == _s2, (tag, "power gate (STOP)")
    ngt += 2
    LAMF, SPRF = power_iter_fast(SUBF, SUBF["jv"], 400)
    if SPRF >= 1e-6:
        DEG = f"F_DEGENERATE_POWER ({tag} rel spread {SPRF})"
    rc = Rfast(SUBF, GI_CARRIER, LAMF)
    rm = Rfast(SUBF, GI_MIR, LAMF)
    # card-required halting assert: the carrier has no direct motor edge to lose
    assert rc["P1"] == 0.0, (tag, rc["P1"], "carrier P1 != 0 (STOP)")
    omc = float(SUBF["om"][GI_CARRIER])
    omm = float(SUBF["om"][GI_MIR])
    _elig = np.where(dn_all)[0]
    _elig = int((SUBF["om"][_elig] > 0).sum())
    base = dict(floor=int(F), beta_L=float(beta),
                local_floor=bool(dst_only is not None),
                n_edges=int(SUBF["n_edges"]),
                edge_retention_vs_f1=float(SUBF["n_edges"] / NEDGE),
                lam1=float(LAMF), rel_spread_last6=float(SPRF),
                carrier_m_out=omc, mirror_m_out=omm,
                carrier_P1=rc["P1"], mirror_P1=rm["P1"],
                carrier_P2=rc["P2"], mirror_P2=rm["P2"],
                cohort_eligible_dn=_elig,
                P1_per_pool_carrier=reach_fast(int(SUBF["loc"][GI_CARRIER]),
                                               SUBF, 1)[1],
                P1_per_pool_mirror=reach_fast(int(SUBF["loc"][GI_MIR]),
                                              SUBF, 1)[1],
                per_pool_carrier=reach_fast(int(SUBF["loc"][GI_CARRIER]),
                                            SUBF, 2)[2],
                per_pool_mirror=reach_fast(int(SUBF["loc"][GI_MIR]),
                                           SUBF, 2)[2],
                cert_mv_checks=nmv, cert_gate_checks=ngt)
    # ---- the REGISTERED F_DEGENERATE_ACTOR escape --------------------------
    # An actor with zero surviving out-mass has no R, no cohort (matched_cohort
    # takes math.log of its out-mass) and no percentile: the card's branch
    # table is UNREACHABLE at this floor, which is the escape's whole point.
    if omc <= 0.0 or omm <= 0.0:
        DEG = (f"F_DEGENERATE_ACTOR ({tag}: carrier om {omc} mirror om {omm} "
               f"- no surviving out-edges, so R / cohort / percentile do not "
               f"exist at this floor)")
        L = dict(base)
        L["degenerate"] = True
        L["degenerate_reason"] = DEG
        for _k in ("carrier_R", "mirror_R", "carrier_pct", "mirror_pct", "gap",
                   "ratio_R", "ratio_P2", "gap_union", "gap_cohC",
                   "pct_carrier_union", "pct_mirror_union",
                   "pct_carrier_cohC", "pct_mirror_cohC",
                   "cohort_jaccard_carrier_vs_f1",
                   "cohort_jaccard_mirror_vs_f1"):
            L[_k] = None
        L["ratio_m_out"] = (float(omm / omc) if omc > 0 else None)
        log(f"[{tag}] DEGENERATE edges {L['n_edges']} "
            f"({L['edge_retention_vs_f1']:.4f}) lam1 {LAMF:.4f} | om car {omc} "
            f"mir {omm} | eligible DN {_elig} of 1303 | P2 car {rc['P2']:.4f} "
            f"mir {rm['P2']:.4f}")
        del SUBF
        return L
    cc = matched_cohort(SUBF, GI_CARRIER)
    cm = matched_cohort(SUBF, GI_MIR)
    cu = sorted(set(cc) | set(cm))
    cv = {}
    for _i, _g in enumerate(cu):
        cv[_g] = Rfast(SUBF, _g, LAMF)["R"]
    L = leg(rc, rm, cc, cm, cv, SUBF)
    if L["cohort_zero_frac_carrier"] > 0.50:
        DEG = f"F_DEGENERATE_COHORT ({tag} zero frac)"
    # cohort-COMMON companions (PREREG 0b): one distribution, both actors
    _vu = [cv[g] for g in cu]
    _vc = [cv[g] for g in cc]
    L["pct_carrier_union"] = pct_of(rc["R"], _vu)
    L["pct_mirror_union"] = pct_of(rm["R"], _vu)
    L["gap_union"] = abs(L["pct_mirror_union"] - L["pct_carrier_union"])
    L["pct_carrier_cohC"] = pct_of(rc["R"], _vc)
    L["pct_mirror_cohC"] = pct_of(rm["R"], _vc)
    L["gap_cohC"] = abs(L["pct_mirror_cohC"] - L["pct_carrier_cohC"])
    # cohort-FREE companions
    L["ratio_R"] = float(rm["R"] / rc["R"]) if rc["R"] > 0 else None
    L["ratio_P2"] = float(rm["P2"] / rc["P2"]) if rc["P2"] > 0 else None
    L["ratio_m_out"] = float(rm["m_out"] / rc["m_out"])
    # the registered gap
    L["gap"] = abs(L["mirror_pct"] - L["carrier_pct"])
    # substrate report (card-required)
    L.update(base)
    L["degenerate"] = False
    L["cohort_jaccard_carrier_vs_f1"] = float(
        len(set(cc) & set(COH_C)) / len(set(cc) | set(COH_C)))
    L["cohort_jaccard_mirror_vs_f1"] = float(
        len(set(cm) & set(COH_M)) / len(set(cm) | set(COH_M)))
    log(f"[{tag}] edges {L['n_edges']} ({L['edge_retention_vs_f1']:.4f}) "
        f"lam1 {LAMF:.4f} | car pct {L['carrier_pct']:.3f} mir pct "
        f"{L['mirror_pct']:.3f} GAP {L['gap']:.3f} | union gap "
        f"{L['gap_union']:.3f} | ratio_R {L['ratio_R']:.4f} "
        f"| P1 car {rc['P1']:.6f} mir {rm['P1']:.6f} "
        f"| J_car {L['cohort_jaccard_carrier_vs_f1']:.3f}")
    del SUBF
    return L


GLOB = {}
# floor 1 global: reuse the inherited (parent) measurement, extended
L1 = dict(o["Q1_primary"])
L1["floor"] = 1
L1["beta_L"] = float(BETA_L)
L1["local_floor"] = False
L1["n_edges"] = int(NEDGE)
L1["edge_retention_vs_f1"] = 1.0
L1["lam1"] = float(LAM1)
L1["rel_spread_last6"] = float(SPR)
L1["gap"] = GAP_1
L1["ratio_R"] = float(R_MIR["R"] / R_CAR["R"])
L1["ratio_P2"] = float(R_MIR["P2"] / R_CAR["P2"])
L1["ratio_m_out"] = float(R_MIR["m_out"] / R_CAR["m_out"])
_vu1 = [CV[g] for g in COH_U]
_vc1 = [CV[g] for g in COH_C]
L1["pct_carrier_union"] = pct_of(R_CAR["R"], _vu1)
L1["pct_mirror_union"] = pct_of(R_MIR["R"], _vu1)
L1["gap_union"] = abs(L1["pct_mirror_union"] - L1["pct_carrier_union"])
L1["pct_carrier_cohC"] = pct_of(R_CAR["R"], _vc1)
L1["pct_mirror_cohC"] = pct_of(R_MIR["R"], _vc1)
L1["gap_cohC"] = abs(L1["pct_mirror_cohC"] - L1["pct_carrier_cohC"])
L1["P1_per_pool_carrier"] = reach_fast(int(SUB["loc"][GI_CARRIER]), SUB, 1)[1]
L1["P1_per_pool_mirror"] = reach_fast(int(SUB["loc"][GI_MIR]), SUB, 1)[1]
L1["cohort_jaccard_carrier_vs_f1"] = 1.0
L1["cohort_jaccard_mirror_vs_f1"] = 1.0
GLOB[1] = L1
L1["degenerate"] = False
L1["cohort_eligible_dn"] = int((OMS[1][np.where(dn_all)[0]] > 0).sum())
log(f"[global f1] GAP {GAP_1:.3f} union gap {L1['gap_union']:.3f} "
    f"ratio_R {L1['ratio_R']:.4f}")

# the FINEST MEASURABLE FLOOR: above it the card's statistic does not exist
FMAX_BOTH = int(min(OUTDEG["carrier"]["syn_max"], OUTDEG["mirror"]["syn_max"]))
o["finest_measurable_floor"] = dict(
    value=FMAX_BOTH,
    carrier_syn_max=OUTDEG["carrier"]["syn_max"],
    mirror_syn_max=OUTDEG["mirror"]["syn_max"],
    note="the largest F at which BOTH actors still have a surviving out-edge "
         "(= min over actors of their out-edge max syn_count). Above it the "
         "card's percentile statistic does not EXIST - it is not small.")
for F in (2, 4):
    GLOB[F] = floor_leg(F, BETA_L, None, f"global_f{F}")
EXTRA = [FMAX_BOTH] if FMAX_BOTH not in (1, 2, 4) else []
for F in EXTRA:
    GLOB[F] = floor_leg(F, BETA_L, None, f"global_f{F}_finest")
o["extra_floors_measured"] = EXTRA
o["Qb_global_floors"] = {str(F): GLOB[F] for F in sorted(GLOB)}

# ---------------- leg (e): the LOCAL floor control -------------------------
# DEG is a BRANCH gate and the branch is registered on the GLOBAL floor only,
# so a degenerate reading from a DESCRIPTIVE leg is recorded, never promoted.
_deg_global = DEG
LOC = {}
for F in (2, 4):
    LOC[F] = floor_leg(F, BETA_L, MOT_MASK, f"local_f{F}")
if DEG != _deg_global:
    o["local_floor_degenerate_note"] = DEG
    DEG = _deg_global
o["Qe_local_floors"] = {str(F): LOC[F] for F in (2, 4)}

# ---------------- leg (f): BETA_L = 1.0 at the branch floor ----------------
o["Qf_beta1_at_f4"] = floor_leg(4, 1.0, None, "global_f4_beta1")
if DEG != _deg_global:
    o["beta1_degenerate_note"] = DEG
    DEG = _deg_global
o["Qf_beta1_at_f4"]["d_carrier_pct_vs_beta2"] = (
    None if (o["Qf_beta1_at_f4"]["carrier_pct"] is None
             or GLOB[4]["carrier_pct"] is None)
    else o["Qf_beta1_at_f4"]["carrier_pct"] - GLOB[4]["carrier_pct"])
o["Qf_beta1_at_f4"]["d_gap_vs_beta2"] = (
    None if (o["Qf_beta1_at_f4"]["gap"] is None or GLOB[4]["gap"] is None)
    else o["Qf_beta1_at_f4"]["gap"] - GLOB[4]["gap"])

# ---------------- THE BRANCH (registered table) ----------------------------
GAP_4 = GLOB[4]["gap"]
if DEG is not None:
    BRANCH = DEG.split(" ")[0]
    o["degenerate_reason"] = DEG
elif GAP_4 < GAP_ARTIFACT_BAR:
    BRANCH = "F_ARTIFACT"
elif GAP_4 >= GAP_SURVIVES_BAR:
    BRANCH = "F_SURVIVES"
else:
    BRANCH = "F_MIXED"
o["branch"] = BRANCH
o["primary"] = dict(statistic="gap_4 = |mirror_pct - carrier_pct| on the GLOBAL "
                              "syn>=4 floor",
                    gap_f1=GAP_1, gap_f2=GLOB[2]["gap"], gap_f4=GAP_4,
                    carrier_pct=[GLOB[F]["carrier_pct"] for F in FLOORS],
                    mirror_pct=[GLOB[F]["mirror_pct"] for F in FLOORS],
                    gap_union=[GLOB[F]["gap_union"] for F in FLOORS],
                    ratio_R=[GLOB[F]["ratio_R"] for F in FLOORS],
                    extra_floors={str(F): dict(
                        gap=GLOB[F]["gap"], gap_union=GLOB[F]["gap_union"],
                        ratio_R=GLOB[F]["ratio_R"],
                        carrier_pct=GLOB[F]["carrier_pct"],
                        mirror_pct=GLOB[F]["mirror_pct"]) for F in EXTRA},
                    branch=BRANCH)
log(f"[BRANCH] {BRANCH} (gap_1 {GAP_1} -> gap_2 {GLOB[2]['gap']} "
    f"-> gap_4 {GAP_4})")

# ---------------- predictions ----------------------------------------------


def _safe(f, default=False):
    try:
        v = f()
        return (default if v is None else bool(v))
    except TypeError:
        return default


P = {}
P["Q222_1"] = dict(registered="F_SURVIVES", measured=BRANCH,
                   correct=bool(BRANCH == "F_SURVIVES"))
_p1c = ([GLOB[F]["carrier_P1"] for F in FLOORS]
        + [LOC[F]["carrier_P1"] for F in (2, 4)])
P["Q222_2"] = dict(registered="carrier P1 == 0.0 on all 3 global + 2 local floors",
                   measured=_p1c, correct=bool(all(v == 0.0 for v in _p1c)))
P["Q222_3"] = dict(registered="mirror P1 == 0.0 exactly at global F=2",
                   measured=GLOB[2]["mirror_P1"],
                   correct=bool(GLOB[2]["mirror_P1"] == 0.0))
P["Q222_4"] = dict(registered="|carrier_pct_4 - carrier_pct_1| <= 0.10",
                   measured=(None if GLOB[4]["carrier_pct"] is None else
                             abs(GLOB[4]["carrier_pct"] - PCT_CAR_1)),
                   correct=_safe(lambda: abs(GLOB[4]["carrier_pct"]
                                             - PCT_CAR_1) <= 0.10),
                   note=("UNMEASURABLE at F=4 (F_DEGENERATE_ACTOR) -> scored "
                         "FALSE, and the honest reading is 'the question does "
                         "not exist at this floor'"
                         if GLOB[4]["carrier_pct"] is None else ""))
P["Q222_5"] = dict(registered="ratio_R > 2.0 at global F=4",
                   measured=GLOB[4]["ratio_R"],
                   correct=_safe(lambda: GLOB[4]["ratio_R"] > 2.0))
P["Q222_6"] = dict(registered="carrier cohort Jaccard(F4 vs F1) < 0.80",
                   measured=GLOB[4]["cohort_jaccard_carrier_vs_f1"],
                   correct=_safe(
                       lambda: GLOB[4]["cohort_jaccard_carrier_vs_f1"] < 0.80),
                   note=("no cohort exists at F=4; the F=2 reading is "
                         f"{GLOB[2]['cohort_jaccard_carrier_vs_f1']}"
                         if GLOB[4]["cohort_jaccard_carrier_vs_f1"] is None
                         else ""))
o["predictions"] = P
o["n_predictions_correct"] = int(sum(1 for v in P.values() if v["correct"]))
log(f"[predictions] {o['n_predictions_correct']} of 6")

o["limitations"] = [
    "EXPLORATORY: every L212 limitation is inherited verbatim (changed "
    "readout, changed volume, changed body segment; a descending neuron's "
    "real output LEAVES this volume; the mass-matched cohort percentile is "
    "NOT the l169c degree-neutral rewire null; v783 'unknown' top_nt is "
    "scored at the build_graph_banc default magnitude 0.3).",
    "PREREG 0b: the registered gap is a difference of percentiles against TWO "
    "DIFFERENT mass-matched cohorts, and a floor relocates both. The "
    "cohort-COMMON (union / cohort-C) and cohort-FREE (ratio_R, ratio_P2) "
    "companions are reported for exactly this reason and were read before the "
    "branch was called.",
    "v783's cohort mass match is LOOSE (log-spread 0.316 / 0.349 against the "
    "0.15 bar L212 registered and failed) - carried forward as a stated limit.",
    "PREREG 0a: the floor acts on the COLLAPSED (pre,post) pair weight, not on "
    "per-neuropil rows. A per-row floor is a different operation, not done.",
    "A floor is not a model of proofreading error, it is a monotone deletion "
    "of weak edges. 'Artifact' here means 'the contrast does not survive "
    "deletion of edges at the detection floor', never 'the edge is false'.",
    "PREREG 0c: the GLOBAL floor confounds deleting weak edges into the "
    "readout with rewriting lam1, every out-mass and the cohort; the LOCAL "
    "floor leg isolates the first and is descriptive (no branch).",
    "ANATOMICAL leg only: no row mask, no settle, no seed, no rollouts - "
    "wiring geometry, NOT an operating point (L164). Operator powers are "
    "walks WITH revisits, not paths.",
    "THE REGISTERED F_DEGENERATE_ACTOR ESCAPE FIRED at the branch floor: an "
    "actor with zero surviving out-mass has no R, no mass-matched cohort (the "
    "cohort is selected by log out-mass) and no percentile, so the card's "
    "F_ARTIFACT / F_SURVIVES / F_MIXED table is UNREACHABLE at syn>=4 on "
    "v783. That is a MEASUREMENT-CAPABILITY limit (the L208 class), not a "
    "small effect, and it is reported as such rather than scored as a zero.",
]
o["pins"] = "ALL GREEN"
o["runtime_s"] = time.time() - T0
json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
log(f"[done] {o['runtime_s']:.1f}s -> {OUT}/static.json  branch={BRANCH}")
