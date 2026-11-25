# ================= L232 BODY (appended by l232_build.py) ==================
# Above this line, VERBATIM: SLICE A (l216_static.py 1-1360), SLICE B
# (l217_tail.py 245-258 = dcross), the HEAD (P only), and SLICE C
# (l230_tail.py 39-211 = L230's OWN EPS/leafcmp/leaves + CERT-216 + the
# lam1 NO-OP re-assertion + CERT-AINF + CERT-217, re-used as a verbatim
# source slice rather than re-implemented — the L225 law).
# This body adds ONLY: the extended depth sweep to D=40 with its halting
# equality gate against L216's stored table AND per-draw null vectors, the
# censoring-rate-vs-D curve and its plateau depth, the nonselective BH-FDR
# family of 12 existence tests, and the multiplicity-free omnibus.
# NO new RNG: PERM is the prefix's fixed boolean draw matrix.

# ---------------- PREMISE asserts (PREREG 0a, 0g) -------------------------
assert len(SUBS) == 2 and sorted(SUBS) == ["cutwA", "f4wA"], sorted(SUBS)
assert len(CELLS) == 8, (len(CELLS), "PREREG 0a: the card's 12 is wrong")
assert JOINTS == ("Ti", "Tr"), JOINTS
assert DMAX == 8 and DMAX_CERT == 3 and NDRAW == 2000, (DMAX, NDRAW)
assert RESFLOOR == 1.0 / (NDRAW + 1)

DBIG = 40                      # PREREG 0g, fixed in advance
DGRID = list(range(2, DBIG + 1))
Q_BH = 0.05
SAT_BAR = 1e-12                # PREREG 0f
PLATEAU_TOL = 0.01             # PREREG Q1
RATIO_TRUNC = 2.0
RATIO_STABLE = 0.5
PRIMARY = ("f4wA", "beta")
ARMS = [(sn, op) for sn in ("f4wA", "cutwA") for op in ("beta", "crofts")]
assert len(ARMS) == 4 and PRIMARY in ARMS
assert len(CELLS) + len(ARMS) == 12, "PREREG 0a: the 12-test family"
log(f"[premise] PREREG 0a GREEN — {len(SUBS)} substrates x 2 operators x "
    f"{len(JOINTS)} joints = {len(CELLS)} cells (NOT 12); the registered "
    f"family of 12 TESTS = {len(CELLS)} single-joint + {len(ARMS)} "
    f"pair-level")
P["premise"] = dict(n_subs=len(SUBS), n_cells=len(CELLS), n_arms=len(ARMS),
                    n_tests_registered=len(CELLS) + len(ARMS), dmax=DMAX,
                    dbig=DBIG, ndraw=NDRAW, resfloor=RESFLOOR,
                    card_said_12_cells_actual=len(CELLS))

# ---------------- CERT-232X (HALTING): the extended sweep IS L216's -------
# The sweep is re-run to D=40 with the SAME certified arrivals()/
# side_stats_from() calls. Its first DMAX depths must reproduce L216's
# stored A_cell at FLOAT EQUALITY and L216's per-draw null vectors at ARRAY
# EQUALITY — that is what proves extending the horizon did not move the
# draw stream (PREREG 0c) before any new D is read.
AX, NX = {}, {}
_n232x = 0
for sname, s in SUBS.items():
    for op in ("beta", "crofts"):
        rn = arrivals(s, OPS[sname][op], DBIG, lam=LAMS[sname][op])
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            ra = np.empty(DBIG, float)
            nm = np.empty((NDRAW, DBIG), float)
            for d in range(1, DBIG + 1):
                real, nAc, nAt = side_stats_from(rn[d][lf], rn[d][le], J)
                ra[d - 1] = real["A_cell"]
                nm[:, d - 1] = nAc
            for d in range(1, DMAX + 1):
                assert float(ra[d - 1]) == TABLE[(sname, op, J, d)]["A_cell"], \
                    (sname, op, J, d, "CERT-232X real A_cell (STOP)")
                assert np.array_equal(nm[:, d - 1],
                                      NULLS[(sname, op, J, d)]), \
                    (sname, op, J, d, "CERT-232X null vector (STOP)")
                _n232x += 2
            AX[(sname, op, J)] = ra
            NX[(sname, op, J)] = nm
assert _n232x == len(CELLS) * DMAX * 2, (_n232x, "CERT-232X coverage (STOP)")
log(f"[CERT-232X] GREEN {_n232x} checks ({len(CELLS)} cells x {DMAX} depths "
    f"x [A_cell FLOAT EQUALITY, {NDRAW}-draw null vector ARRAY EQUALITY]) — "
    f"the D={DBIG} sweep's first {DMAX} depths ARE the certified ones, so "
    f"the draw stream is depth-invariant BY MEASUREMENT")
P["cert_232x"] = dict(n_checks=_n232x, dbig=DBIG, dmax_certified=DMAX,
                      mode="A_cell float equality + null vector array "
                           "equality", ndraw=NDRAW)

# ---------------- PREREG 0f: the SATURATION depth per cell ----------------
SAT = {}
for key in CELLS:
    _ainf = float(AINF[key]["A_cell"])
    _dd = [d for d in range(1, DBIG + 1)
           if abs(float(AX[key][d - 1]) - _ainf) < SAT_BAR]
    SAT[key] = (min(_dd) if _dd else None)
log("[saturation] |A_cell(d) - A_inf| < " + f"{SAT_BAR:.0e} first at d = " +
    ", ".join(f"{sn}|{op}|{J}:{SAT[(sn, op, J)]}" for (sn, op, J) in CELLS))
P["saturation_depth"] = {f"{sn}|{op}|{J}": SAT[(sn, op, J)]
                         for (sn, op, J) in CELLS}

# ---------------- existence curves (PREREG 0d, 0e) ------------------------


def exist_curve(mat):
    """[:, D-1] = True iff a sign change exists in depths 1..D. Cumulative
    ANY over adjacent-product-negative indicators, so monotone in D BY
    CONSTRUCTION (PREREG 0e)."""
    m = np.atleast_2d(np.asarray(mat, float))
    sc = (m[:, :-1] * m[:, 1:]) < 0
    out = np.zeros((m.shape[0], m.shape[1]), bool)
    out[:, 1:] = np.cumsum(sc, axis=1) > 0
    return out


EXR, EXN = {}, {}
for key in CELLS:
    EXR[key] = exist_curve(AX[key])[0]
    EXN[key] = exist_curve(NX[key])
    assert EXN[key].shape == (NDRAW, DBIG)
    # monotone non-decreasing in D, asserted never claimed (PREREG 0e)
    assert (np.diff(EXN[key].astype(int), axis=1) >= 0).all(), (key, "mono")
    assert (np.diff(EXR[key].astype(int)) >= 0).all(), (key, "mono real")

# ---------------- CERT-232D (HALTING): D=8 reproduces L217 exactly --------
# The existence statistic read off the extended curves at D = DMAX must equal
# L217's stored censoring and crossing rates, which SLICE C has already
# certified against l217/static.json. This ties the new instrument to the
# stored primary with zero new freedom.
_n232d = 0
for key in CELLS:
    assert float(EXN[key][:, DMAX - 1].mean()) == \
        float(DX[key]["null_frac_cross"]), (key, "CERT-232D null rate (STOP)")
    assert bool(EXR[key][DMAX - 1]) == (not bool(DX[key]["censored"])), \
        (key, "CERT-232D real existence (STOP)")
    assert int(EXN[key][:, DMAX - 1].sum()) == \
        int(np.isfinite(DXNULL[key]).sum()), (key, "CERT-232D count (STOP)")
    _n232d += 3
_BOTH8 = float((EXN[(PRIMARY[0], PRIMARY[1], "Ti")][:, DMAX - 1]
                & EXN[(PRIMARY[0], PRIMARY[1], "Tr")][:, DMAX - 1]).mean())
assert _BOTH8 == float(_L217_RATE), \
    (_BOTH8, _L217_RATE, "CERT-232D L217's 0.0505 (STOP)")
_n232d += 1
log(f"[CERT-232D] GREEN {_n232d} checks — the existence curves read at "
    f"D={DMAX} reproduce L217's stored per-cell null crossing rates, its "
    f"censoring flags, its finite-draw counts AND its both-joints rate "
    f"{_BOTH8:.4f} EXACTLY")
P["cert_232d"] = dict(n_checks=_n232d, p_both_at_dmax=_BOTH8,
                      equals_l217_stored=True)

# ---------------- Q1: the censoring rate as a function of D ---------------
RATE = {key: EXN[key].mean(0) for key in CELLS}
PAIRR = {arm: (EXN[(arm[0], arm[1], "Ti")] & EXN[(arm[0], arm[1], "Tr")]
               ).mean(0) for arm in ARMS}
CURVE = {}
for key in CELLS:
    CURVE[f"{key[0]}|{key[1]}|{key[2]}"] = dict(
        null_cross_rate={f"D{d}": float(RATE[key][d - 1])
                         for d in (2, 4, 8, 12, 16, 20, 30, DBIG)},
        null_censor_rate_at_dbig=float(1.0 - RATE[key][DBIG - 1]),
        real_crosses_at_dmax=bool(EXR[key][DMAX - 1]),
        real_crosses_at_dbig=bool(EXR[key][DBIG - 1]),
        real_first_cross_D=(int(np.argmax(EXR[key]) + 1)
                            if EXR[key].any() else None),
        saturation_depth=SAT[key])
P["curves"] = CURVE
P["pair_curves"] = {f"{a[0]}|{a[1]}": {f"D{d}": float(PAIRR[a][d - 1])
                                       for d in (2, 4, 8, 12, 16, 20, 30,
                                                 DBIG)} for a in ARMS}

_gap = {d: max(float(RATE[k][DBIG - 1] - RATE[k][d - 1]) for k in CELLS)
        for d in DGRID}
DSTAR = next((d for d in DGRID if _gap[d] <= PLATEAU_TOL), None)
log(f"[Q1 plateau] worst remaining rise to D={DBIG}: "
    + ", ".join(f"D{d}:{_gap[d]:.4f}" for d in (4, 8, 12, 16, 20, 24, 30))
    + f" | tol {PLATEAU_TOL} -> D* = {DSTAR}")

if DSTAR is None:
    BRANCH = "T_NO_PLATEAU"
    P_BOTH_DSTAR = None
    RATIO = None
else:
    P_BOTH_DSTAR = float(PAIRR[PRIMARY][DSTAR - 1])
    RATIO = (P_BOTH_DSTAR / _BOTH8) if _BOTH8 > 0 else None
    if RATIO is not None and RATIO >= RATIO_TRUNC:
        BRANCH = "T_TRUNCATION"
    elif RATIO is not None and abs(RATIO - 1.0) < RATIO_STABLE:
        BRANCH = "T_STABLE"
    else:
        BRANCH = "T_INTERMEDIATE"
_satpost = (None if DSTAR is None else
            sorted(k for k in CELLS if SAT[k] is not None and SAT[k] <= DSTAR))
P["Q1_plateau"] = dict(
    branch=BRANCH, dstar=DSTAR, plateau_tol=PLATEAU_TOL,
    worst_remaining_rise={f"D{d}": _gap[d] for d in
                          (2, 4, 8, 12, 16, 20, 24, 30, DBIG)},
    p_both_at_dmax8=_BOTH8, p_both_at_dstar=P_BOTH_DSTAR, ratio=RATIO,
    ratio_bars=dict(truncation=RATIO_TRUNC, stable=RATIO_STABLE),
    n_cells_saturated_by_dstar=(None if _satpost is None else len(_satpost)),
    cells_saturated_by_dstar=(None if _satpost is None else
                              [f"{a}|{b}|{c}" for (a, b, c) in _satpost]),
    plateau_numerically_forced=(None if DSTAR is None else
                                bool(_satpost and len(_satpost) == len(CELLS))),
    d_dependent_p_is_a_truncation_artifact=(
        "PREREG 0i: registered in advance. p_both rises from "
        f"{_BOTH8:.4f} at D=8 to "
        + (f"{P_BOTH_DSTAR:.4f} at D*={DSTAR}" if DSTAR else "n/a")
        + " — reported AS a truncation property of the horizon, never as an "
          "effect size."))
log(f"[Q1] BRANCH {BRANCH} | p_both(8) {_BOTH8:.4f} -> p_both(D*) "
    f"{P_BOTH_DSTAR if P_BOTH_DSTAR is None else round(P_BOTH_DSTAR, 4)} "
    f"| ratio {RATIO if RATIO is None else round(RATIO, 3)}")

# ---------------- Q2: the NONSELECTIVE family, BH-FDR --------------------
DREAD = DSTAR if DSTAR is not None else DBIG
TESTS = []
for key in CELLS:
    nm = f"cell/{key[0]}|{key[1]}|{key[2]}"
    if bool(EXR[key][DREAD - 1]):
        TESTS.append(dict(name=nm, kind="single_joint", measurable=True,
                          p=float(RATE[key][DREAD - 1])))
    else:
        TESTS.append(dict(name=nm, kind="single_joint", measurable=False,
                          p=None, verdict="FALSE BY UNMEASURABILITY "
                          "(PREREG 0h): the REAL cell does not cross within "
                          "D*, so there is no event to test"))
for arm in ARMS:
    nm = f"arm/{arm[0]}|{arm[1]}"
    _rb = bool(EXR[(arm[0], arm[1], "Ti")][DREAD - 1]
               and EXR[(arm[0], arm[1], "Tr")][DREAD - 1])
    if _rb:
        TESTS.append(dict(name=nm, kind="pair_both", measurable=True,
                          p=float(PAIRR[arm][DREAD - 1])))
    else:
        TESTS.append(dict(name=nm, kind="pair_both", measurable=False,
                          p=None, verdict="FALSE BY UNMEASURABILITY "
                          "(PREREG 0h): the REAL arm does not cross in both "
                          "joints within D*"))
assert len(TESTS) == 12, (len(TESTS), "registered family size (STOP)")

MEAS = [t for t in TESTS if t["measurable"]]
M_BH = len(MEAS)
_order = sorted(range(M_BH), key=lambda i: MEAS[i]["p"])
_rej = set()
for _r, _i in enumerate(_order, start=1):
    if MEAS[_i]["p"] <= Q_BH * _r / M_BH:
        _rej = set(_order[:_r])
for _r, _i in enumerate(_order, start=1):
    MEAS[_i]["bh_rank"] = _r
    MEAS[_i]["bh_bar"] = Q_BH * _r / M_BH
    MEAS[_i]["bh_reject"] = bool(_i in _rej)
BH_SIG = [MEAS[i]["name"] for i in sorted(_rej, key=lambda i: MEAS[i]["p"])]
Q2 = "E_FAMILY_SIG" if BH_SIG else "E_FAMILY_NULL"
_rank1 = Q_BH * 1.0 / M_BH
log(f"[Q2] BRANCH {Q2} | m={M_BH} measurable of 12 | rank-1 bar "
    f"{_rank1:.3e} vs resolution floor {RESFLOOR:.4e} "
    f"({'REJECTABLE' if RESFLOOR <= _rank1 else 'UNREACHABLE'}, headroom "
    f"{_rank1 / RESFLOOR:.1f}x) | rejections {len(BH_SIG)}: {BH_SIG}")
P["Q2_family"] = dict(
    branch=Q2, d_read=DREAD, q=Q_BH, m_registered=12, m_measurable=M_BH,
    n_unmeasurable=12 - M_BH,
    unmeasurable=[t["name"] for t in TESTS if not t["measurable"]],
    rank1_bar=_rank1, resolution_floor=RESFLOOR,
    rank1_rejectable=bool(RESFLOOR <= _rank1),
    rank1_headroom=_rank1 / RESFLOOR,
    n_rejected=len(BH_SIG), rejected=BH_SIG,
    smallest_p=(float(MEAS[_order[0]]["p"]) if M_BH else None),
    tests=TESTS)

# ---------------- Q3: the multiplicity-free omnibus ----------------------
# PERM is keyed by (joint, side) only, so draw index j is ONE side
# relabelling readable across all 8 cells simultaneously.
_stack = np.column_stack([EXN[key][:, DREAD - 1] for key in CELLS])
assert _stack.shape == (NDRAW, len(CELLS))
NCROSS = _stack.sum(1)
NREAL = int(sum(bool(EXR[key][DREAD - 1]) for key in CELLS))
P_OMNI = float((NCROSS >= NREAL).mean())
Q3 = "O_REAL_EXTREME" if P_OMNI <= 0.05 else "O_REAL_TYPICAL"
_hist = {int(v): int((NCROSS == v).sum()) for v in range(len(CELLS) + 1)}
log(f"[Q3] BRANCH {Q3} | N_real {NREAL}/{len(CELLS)} cells cross by "
    f"D={DREAD}; null N_cross mean {NCROSS.mean():.3f} median "
    f"{np.median(NCROSS):.1f} max {NCROSS.max()} | p_omni {P_OMNI:.4f} "
    f"(floor {RESFLOOR:.4e})")
P["Q3_omnibus"] = dict(
    branch=Q3, d_read=DREAD, n_real=NREAL, n_cells=len(CELLS),
    p_omni=P_OMNI, resolution_floor=RESFLOOR,
    at_floor=bool(P_OMNI <= RESFLOOR),
    null_mean=float(NCROSS.mean()), null_median=float(np.median(NCROSS)),
    null_sd=float(NCROSS.std()), null_max=int(NCROSS.max()),
    null_hist=_hist,
    real_cells_crossing=[f"{a}|{b}|{c}" for (a, b, c) in CELLS
                         if bool(EXR[(a, b, c)][DREAD - 1])],
    real_cells_not_crossing=[f"{a}|{b}|{c}" for (a, b, c) in CELLS
                             if not bool(EXR[(a, b, c)][DREAD - 1])],
    note="PERM is keyed by (joint, side) only, so draw j is one side "
         "relabelling shared by all 8 cells; this is ONE test with no "
         "multiplicity correction needed.")

# ---------------- L230 cross-read (DESCRIPTION, no branch) ---------------
# L230's closed form predicted a crossing for the one cell L217 censored at
# DMAX=8: f4wA|crofts|Ti at d 15.03. The extended sweep can now say whether
# it happens, and at what depth the EXISTENCE first appears.
_k = ("f4wA", "crofts", "Ti")
P["l230_prediction_check"] = dict(
    cell="f4wA|crofts|Ti", l230_closed_form_d_cross=15.03,
    crosses_by_dbig=bool(EXR[_k][DBIG - 1]),
    measured_first_existence_D=(int(np.argmax(EXR[_k]) + 1)
                                if EXR[_k].any() else None),
    measured_d_cross_interpolated=(dcross(list(AX[_k]))[0]),
    n_sign_changes=int(dcross(list(AX[_k]))[1]),
    status="DESCRIPTION — no branch rests on this (L230's number was itself "
           "declared post-hoc arithmetic on stored values).")
_k2 = ("cutwA", "crofts", "Ti")
P["l230_nocross_check"] = dict(
    cell="cutwA|crofts|Ti",
    l230_said="UNAVAILABLE by premise: A_inf has the SAME sign as K, so the "
              "closed form says it never crosses",
    crosses_by_dbig=bool(EXR[_k2][DBIG - 1]),
    a_inf=float(AINF[_k2]["A_cell"]),
    status="DESCRIPTION — an agreement check on L230's premise 0d.")

# ---------------- predictions, scored ------------------------------------
PRED = {}
PRED["P1_plateau_exists"] = dict(
    registered="a plateau exists within D_BIG=40 (D* is not None)",
    value=DSTAR, passed=bool(DSTAR is not None))
PRED["P2_null_rate_rises"] = dict(
    registered="p_both(D*) > p_both(8)",
    value=P_BOTH_DSTAR, baseline=_BOTH8,
    passed=bool(P_BOTH_DSTAR is not None and P_BOTH_DSTAR > _BOTH8))
PRED["P3_truncation_branch"] = dict(
    registered=f"T_TRUNCATION fires (ratio >= {RATIO_TRUNC})",
    value=RATIO, passed=bool(BRANCH == "T_TRUNCATION"))
PRED["P4_bh_rejection"] = dict(
    registered="at least one of the 12 tests is BH-rejected at q=0.05",
    value=len(BH_SIG), passed=bool(len(BH_SIG) >= 1))
PRED["P5_more_than_six_real"] = dict(
    registered="the real wiring crosses in MORE than 6 of 8 cells at D*",
    value=NREAL, passed=bool(NREAL > 6))
PRED["P6_omnibus_sig"] = dict(
    registered="p_omni < 0.05", value=P_OMNI, passed=bool(P_OMNI < 0.05))
_sc = len(PRED)
_ok = sum(1 for v in PRED.values() if v["passed"])
P["predictions"] = PRED
P["predictions_score"] = f"{_ok}/{_sc}"
log(f"[predictions] {_ok}/{_sc} — "
    + ", ".join(f"{k.split('_')[0]}:{'T' if v['passed'] else 'F'}"
                for k, v in PRED.items()))

P["branch"] = BRANCH
P["branches"] = dict(Q1=BRANCH, Q2=Q2, Q3=Q3)
P["constants"] = dict(DBIG=DBIG, DMAX=DMAX, NDRAW=NDRAW, Q_BH=Q_BH,
                      SAT_BAR=SAT_BAR, PLATEAU_TOL=PLATEAU_TOL,
                      RATIO_TRUNC=RATIO_TRUNC, RATIO_STABLE=RATIO_STABLE,
                      PRIMARY="f4wA|beta", SEED_PERM=SEED_PERM)
P["limitations"] = (
    "(1) Every D=8 quantity in this card is OBSERVED-DERIVABLE from "
    "l216/static.json and l217/static.json and is scored as DESCRIPTION "
    "(PREREG 0b); only the D>8 rates, D*, and the p-values read at D* have "
    "a null that was unknown at registration. (2) The existence rate is "
    "monotone non-decreasing in D BY CONSTRUCTION (cumulative ANY), so the "
    "plateau is a LEVEL statement and the monotonicity is an assert, not a "
    "finding. (3) A plateau reached only AFTER the per-cell saturation "
    "depth is numerically forced rather than structural: the stored "
    "saturation_depth field is what distinguishes the two, and the Q1 "
    "record carries plateau_numerically_forced. (4) The null is L205's "
    "within-pool side-label permutation; it holds per-side counts exact and "
    "relocates nothing else, so it cannot speak to reconstruction "
    "completeness (L231's caveat). (5) The 12-test family is the registered "
    "one; tests whose REAL event does not exist within D* are scored FALSE "
    "BY UNMEASURABILITY and excluded from BH, which SHRINKS m and therefore "
    "LOOSENS every bar — m_measurable is stored beside m_registered. (6) "
    "p_omni and every rate share one resolution floor 1/(NDRAW+1) = "
    "4.9975e-04; a p AT the floor is reported as '<= floor', never as a "
    "point value.")

# ---------------- prior artifacts untouched -------------------------------
for _p, _fp in (("l216/static.json", _f216), ("l217/static.json", _f217),
                ("l209/static.json", _f209), ("l210/static.json", _f210)):
    _n = os.stat(_p)
    assert (_n.st_size, _n.st_mtime_ns) == (_fp.st_size, _fp.st_mtime_ns), \
        (_p, "prior artifact MOVED during the run (STOP)")
log("[prior] l216/l217/l209/l210 static.json (size, mtime_ns) unchanged GREEN")

P["runtime_s"] = time.time() - _T232
P["total_runtime_s"] = time.time() - t0
os.makedirs("l232", exist_ok=True)
json.dump(P, open("l232/static.json", "w"), indent=1, default=str)
log(f"[L232] DONE Q1={BRANCH} Q2={Q2} Q3={Q3} preds={_ok}/{_sc} "
    f"({P['runtime_s']:.0f}s body, {P['total_runtime_s']:.0f}s total)")
