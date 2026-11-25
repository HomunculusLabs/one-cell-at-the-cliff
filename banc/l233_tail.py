# ================= L233 BODY (appended by l233_build.py) ==================
# Above this line, VERBATIM: SLICE A (l216_static.py 1-1360), SLICE B
# (l217_tail.py 245-258 = dcross), the HEAD (P only), SLICE C (l230_tail.py
# 39-211 = L230's OWN EPS/leafcmp/leaves + CERT-216 + the lam1 NO-OP
# re-assertion + CERT-AINF + CERT-217) and SLICE D (l231_tail.py 429-450 =
# L231's midrank + spearman, the L221 tie law in certified form).
# This body adds ONLY: the destination-geometry predictors (in-degree,
# operator-native in-mass, L205's in-mass), their side asymmetries on the
# certified side_stats_from expression, the log-OLS share decomposition with
# its exact identity gate, the leave-one-out leverage statistic with its
# permutation null, and the TYPE-level mirror-match leg.
# NO new RNG: PERM is the prefix's fixed boolean draw matrix.
import math

# ---------------- PREMISE asserts (PREREG 0a, 0c, 0f, 0g) -----------------
assert len(SUBS) == 2 and sorted(SUBS) == ["cutwA", "f4wA"], sorted(SUBS)
assert len(CELLS) == 8 and JOINTS == ("Ti", "Tr"), (len(CELLS), JOINTS)
assert NDRAW == 2000 and RESFLOOR == 1.0 / (NDRAW + 1)
Z_ARMS = [(sn, op) for sn in ("f4wA", "cutwA") for op in ("beta", "crofts")]
Z_PRIMARY = ("f4wA", "beta")
assert len(Z_ARMS) == 4 and Z_PRIMARY in Z_ARMS
# PREREG 0f: PERM is keyed by (joint, group) ONLY -> ONE draw is ONE Ti
# relabelling (serving 4 cells) and ONE Tr relabelling (the other 4).
assert sorted(PERM.keys()) == [("Ti", "e"), ("Ti", "f"), ("Tr", "e"),
                               ("Tr", "f")], sorted(PERM.keys())
Z_WIDTH = len(JOINTS)
log(f"[premise] PREREG 0f GREEN — {len(CELLS)} cells consume {Z_WIDTH} "
    f"independent randomisations (PERM keyed by {len(PERM)} (joint, group) "
    f"pairs); PRIMARIES ARE MAGNITUDES, percentiles are description")

# registered bars, fixed in advance
Z_SHARE_HI, Z_SHARE_LO = 0.70, 0.30
Z_LEV_BAR = 0.50
Z_RHO_BAR = 0.50
Z_HOM_BAR = 0.50
Z_DY_BAR = 0.01                 # PREREG 0d
Z_P5_BAR = 0.20

# ---------------- the joint's combined pool cell set ----------------------
# GROUPS[(J,g)] = (GLOBAL cell indices, isL) in L-then-R order; LOCAL maps the
# same cells onto a substrate. The combined set is flexor THEN extensor, the
# order side_stats_from itself consumes.
ZG, ZL = {}, {}
for J in JOINTS:
    gcf, isLf = GROUPS[(J, "f")]
    gce, isLe = GROUPS[(J, "e")]
    ZG[J] = dict(g=np.concatenate([gcf, gce]),
                 isL=np.concatenate([isLf, isLe]),
                 n_f=len(gcf), n_e=len(gce))
    for sname in SUBS:
        ZL[(sname, J)] = np.concatenate([LOCAL[sname][(J, "f")],
                                         LOCAL[sname][(J, "e")]])
    assert len(ZG[J]["g"]) == len(ZL[("f4wA", J)])
Z_SIDEN = {J: (int(ZG[J]["isL"].sum()), int((~ZG[J]["isL"]).sum()))
           for J in JOINTS}
assert Z_SIDEN == {"Ti": (56, 57), "Tr": (55, 55)}, Z_SIDEN
log(f"[premise] PREREG 0g GREEN — pool side counts {Z_SIDEN}; A_n(Ti) "
    f"{asym(56, 57):+.6f}, A_n(Tr) {asym(55, 55):+.6f}")

# ---------------- CERT-233C (HALTING): the probe's census, asserted -------
# l233/probe.out declared these from the annotations alone, BEFORE any v1
# statistic existed. cell_type coverage is 100% on all 8 pool-sides and NO
# type is one-to-one across sides (PREREG 0a).
Z_CT = dict(zip(mot_rows.gi.to_numpy(),
                mot_rows.cell_type.fillna("").astype(str).to_numpy()))
_n233c = 0
for J in JOINTS:
    for g, key in (("f", "f"), ("e", "e")):
        gc, isl = GROUPS[(J, g)]
        for c, m in (("L", isl), ("R", ~isl)):
            want = POOLSZ[f"{J}_{g}{c}"]
            assert int(m.sum()) == want, (J, g, c, int(m.sum()), want)
            tys = [Z_CT[int(x)] for x in gc[m]]
            assert all(t != "" for t in tys), (J, g, c, "untyped pool cell")
            _n233c += 2
Z_PROBE = {"Ti_fL": (50, 6), "Ti_fR": (51, 7), "Ti_eL": (6, 2),
           "Ti_eR": (6, 2), "Tr_fL": (31, 10), "Tr_fR": (31, 11),
           "Tr_eL": (24, 9), "Tr_eR": (24, 9)}
for J in JOINTS:
    for g in ("f", "e"):
        gc, isl = GROUPS[(J, g)]
        for c, m in (("L", isl), ("R", ~isl)):
            tys = [Z_CT[int(x)] for x in gc[m]]
            wn, wt = Z_PROBE[f"{J}_{g}{c}"]
            assert (len(tys), len(set(tys))) == (wn, wt), \
                (J, g, c, len(tys), len(set(tys)), wn, wt, "CERT-233C (STOP)")
            _n233c += 2
Z_SHARED, Z_MULT = {}, {}
for J in JOINTS:
    tL = [Z_CT[int(x)] for x in ZG[J]["g"][ZG[J]["isL"]]]
    tR = [Z_CT[int(x)] for x in ZG[J]["g"][~ZG[J]["isL"]]]
    kL = {t: tL.count(t) for t in set(tL)}
    kR = {t: tR.count(t) for t in set(tR)}
    sh = sorted(set(kL) & set(kR))
    npair = sum(min(kL[t], kR[t]) for t in sh)
    one2one = [t for t in sh if kL[t] == 1 and kR[t] == 1]
    Z_SHARED[J] = sh
    Z_MULT[J] = (kL, kR)
    assert len(one2one) == 0, (J, one2one, "PREREG 0a: a 1:1 type exists")
    _n233c += 1
    log(f"[CERT-233C] {J}: shared_types {len(sh)} paired_cells {npair} "
        f"one_to_one_types 0 (the card's cell-level twin is UNMEASURABLE)")
assert (len(Z_SHARED["Ti"]), len(Z_SHARED["Tr"])) == (8, 13), \
    (len(Z_SHARED["Ti"]), len(Z_SHARED["Tr"]), "CERT-233C shared (STOP)")
assert _n233c == 34, (_n233c, "CERT-233C coverage (STOP)")
log(f"[CERT-233C] GREEN {_n233c} checks — pool sizes, 100% cell_type "
    f"coverage, per-side distinct-type counts and the shared-type census "
    f"are EXACTLY what l233/probe.out declared before any v1 was read")
P["cert_233c"] = dict(n_checks=_n233c, source="l233/probe.out",
                      shared_types={J: len(Z_SHARED[J]) for J in JOINTS},
                      one_to_one_types=0,
                      side_counts={J: list(Z_SIDEN[J]) for J in JOINTS})

# ---------------- the predictors (PREREG 0b, 0c) --------------------------
Z_DEG, Z_MOP = {}, {}
for sname, s in SUBS.items():
    Z_DEG[sname] = np.bincount(s["rows"], minlength=s["n"]).astype(float)
    assert Z_DEG[sname].sum() == s["n_edges"], (sname, "in-degree total")
    for op in ("beta", "crofts"):
        m = np.zeros(s["n"])
        np.add.at(m, s["rows"], OPS[sname][op])
        Z_MOP[(sname, op)] = m
log("[predictors] in-degree (operator-INVARIANT per substrate, PREREG 0c) "
    "and operator-native in-mass (row sum of OPS, PREREG 0b) built")

# ---------------- PREREG 0e: the ZERO census, before any log --------------
Z_ZERO = {}
for (sname, op, J) in CELLS:
    lc = ZL[(sname, J)]
    gc = ZG[J]["g"]
    v1 = PERRON[(sname, op)][1]
    row = {}
    for nm, vec in (("v1", v1[lc]), ("m_op", Z_MOP[(sname, op)][lc]),
                    ("indeg", Z_DEG[sname][lc]),
                    ("m_205", INMASS[sname][gc])):
        z = int((np.asarray(vec) == 0).sum())
        row[nm] = dict(n_zero=z, frac=z / len(lc),
                       n_zero_L=int((np.asarray(vec)[ZG[J]["isL"]] == 0).sum()),
                       n_zero_R=int((np.asarray(vec)[~ZG[J]["isL"]] == 0).sum()))
    Z_ZERO[f"{sname}|{op}|{J}"] = row
_zt = sum(r[k]["n_zero"] for r in Z_ZERO.values() for k in r)
log(f"[PREREG 0e] zero census over 8 cells x 4 vectors: {_zt} zeros total "
    f"-> the log leg is {'FULL' if _zt == 0 else 'SUBSET'}-population")
P["zero_census"] = Z_ZERO
P["zero_total"] = _zt
assert _zt == 0, (_zt, "PREREG 0e: a zero exists — the log leg must be "
                       "re-scoped to the nonzero subset before proceeding")

# ---------------- CERT-233A (HALTING): A_inf and A_m205 are STORED --------
_n233a = 0
Z_ROW = {}
for (sname, op, J) in CELLS:
    lcf = LOCAL[sname][(J, "f")]
    lce = LOCAL[sname][(J, "e")]
    gcf, _ = GROUPS[(J, "f")]
    gce, _ = GROUPS[(J, "e")]
    v1 = PERRON[(sname, op)][1]
    r_v1, n_v1c, n_v1t = side_stats_from(v1[lcf], v1[lce], J)
    r_v1 = decorate(r_v1, n_v1c, n_v1t)
    for f in ("A_cell", "A_tot", "M_L", "M_R", "A_cell_pct_abs",
              "null_A_cell_p95"):
        assert r_v1[f] == AINF[(sname, op, J)][f], \
            (sname, op, J, f, "CERT-233A A_inf (STOP)")
        _n233a += 1
    r_dg, n_dgc, n_dgt = side_stats_from(Z_DEG[sname][lcf], Z_DEG[sname][lce], J)
    r_dg = decorate(r_dg, n_dgc, n_dgt)
    r_mo, n_moc, n_mot = side_stats_from(Z_MOP[(sname, op)][lcf],
                                         Z_MOP[(sname, op)][lce], J)
    r_mo = decorate(r_mo, n_moc, n_mot)
    r_25, n_25c, n_25t = side_stats_from(INMASS[sname][gcf], INMASS[sname][gce], J)
    r_25 = decorate(r_25, n_25c, n_25t)
    # leg (b) is a STORED, already-certified L205 quantity
    for f in ("A_cell", "A_tot", "M_L", "M_R", "A_cell_pct_abs"):
        assert r_25[f] == S205["table"][J][sname][f], \
            (sname, J, f, "CERT-233A A_m205 vs l205/static.json (STOP)")
        _n233a += 1
    _An = asym(r_v1["n_L"], r_v1["n_R"])
    Z_ROW[(sname, op, J)] = dict(
        sub=sname, op=op, joint=J, arm=f"{sname}|{op}",
        primary=bool((sname, op) == Z_PRIMARY),
        A_inf=r_v1["A_cell"], A_inf_tot=r_v1["A_tot"],
        A_inf_pct_abs=r_v1["A_cell_pct_abs"],
        A_inf_null_p95=r_v1["null_A_cell_p95"],
        A_n=_An, identity_residual=r_v1["A_cell"] + _An,
        A_indeg=r_dg["A_cell"], A_indeg_tot=r_dg["A_tot"],
        A_indeg_pct_abs=r_dg["A_cell_pct_abs"],
        A_mop=r_mo["A_cell"], A_mop_tot=r_mo["A_tot"],
        A_mop_pct_abs=r_mo["A_cell_pct_abs"],
        A_m205=r_25["A_cell"], A_m205_tot=r_25["A_tot"],
        A_m205_pct_abs=r_25["A_cell_pct_abs"],
        n_L=r_v1["n_L"], n_R=r_v1["n_R"])
assert _n233a == len(CELLS) * 11, (_n233a, "CERT-233A coverage (STOP)")
log(f"[CERT-233A] GREEN {_n233a} checks — every A_inf field reproduced from "
    f"AINF at FLOAT EQUALITY and leg (b) A_m205 reproduced from "
    f"l205/static.json at FLOAT EQUALITY (the in-mass asymmetry is a STORED "
    f"certified quantity, not a new measurement)")
P["cert_233a"] = dict(n_checks=_n233a, mode="float equality (==)",
                      sources=["AINF (l216, CERT-AINF)",
                               "l205/static.json table"])

# ---------------- rho: the L207/L213 prerequisite (MIDRANK, PREREG 0h) ----
for key in CELLS:
    sname, op, J = key
    lc, gc = ZL[(sname, J)], ZG[J]["g"]
    v1 = PERRON[(sname, op)][1]
    ly = np.log(v1[lc])
    xs = dict(m_op=np.log(Z_MOP[(sname, op)][lc]),
              indeg=np.log(Z_DEG[sname][lc]),
              m_205=np.log(INMASS[sname][gc]))
    for nm, xv in xs.items():
        Z_ROW[key][f"rho_{nm}"] = spearman(ly, xv)
        Z_ROW[key][f"ndistinct_{nm}"] = int(len(np.unique(xv)))
    Z_ROW[key]["ndistinct_logv1"] = int(len(np.unique(ly)))
    log(f"[rho] {sname:6s} {op:6s} {J}: log v1 vs log m_op "
        f"{Z_ROW[key]['rho_m_op']:+.4f} | indeg "
        f"{Z_ROW[key]['rho_indeg']:+.4f} | m_205 "
        f"{Z_ROW[key]['rho_m_205']:+.4f}  (distinct values "
        f"{Z_ROW[key]['ndistinct_logv1']}/{Z_ROW[key]['ndistinct_m_op']}/"
        f"{Z_ROW[key]['ndistinct_indeg']}/{Z_ROW[key]['ndistinct_m_205']})")

# ---------------- the share decomposition + CERT-233B identity gate -------
_n233b = 0
_maxid = 0.0
_maxsc = 0.0
for key in CELLS:
    sname, op, J = key
    lc, gc = ZL[(sname, J)], ZG[J]["g"]
    isL = ZG[J]["isL"]
    v1 = PERRON[(sname, op)][1]
    y = np.log(v1[lc])
    Dy = float(y[isL].mean() - y[~isL].mean())
    Z_ROW[key]["D_logv1"] = Dy
    Z_ROW[key]["cond_factor"] = (float(1.0 / abs(Dy)) if Dy != 0 else None)
    Z_ROW[key]["Dy_readable"] = bool(abs(Dy) >= Z_DY_BAR)
    XS = dict(m_op=np.log(Z_MOP[(sname, op)][lc]),
              indeg=np.log(Z_DEG[sname][lc]),
              m_205=np.log(INMASS[sname][gc]))
    for nm, x in XS.items():
        xm, ym = x - x.mean(), y - y.mean()
        b = float((xm * ym).sum() / (xm * xm).sum())
        a = float(y.mean() - b * x.mean())
        r = y - (a + b * x)
        Dx = float(x[isL].mean() - x[~isL].mean())
        Dr = float(r[isL].mean() - r[~isL].mean())
        _id = abs(Dy - (b * Dx + Dr))
        # The identity is an EXACT cancellation whose OPERANDS live on the
        # log scale (|log v1| ~ 14) while its RESULT lives at ~0.1, so the
        # absolute resolution is set by the operands, not by Dy (the
        # CERT-231A law, applied to an identity instead of a ratio). The
        # scale is DERIVED from this cell's own fitted magnitudes.
        _scale = max(1.0, float(np.abs(y).max()), abs(a),
                     float(np.abs(b * x).max()), abs(Dy), abs(b * Dx), abs(Dr))
        _maxid = max(_maxid, _id)
        _maxsc = max(_maxsc, _id / _scale)
        assert _id <= 8 * EPS * _scale, \
            (key, nm, _id, _scale, "CERT-233B OLS identity (STOP)")
        _n233b += 1
        Z_ROW[key][f"b_{nm}"] = b
        Z_ROW[key][f"D_{nm}"] = Dx
        Z_ROW[key][f"expl_{nm}"] = float(b * Dx)
        Z_ROW[key][f"resid_{nm}"] = Dr
        Z_ROW[key][f"share_{nm}"] = (float(b * Dx / Dy) if Dy != 0 else None)
    # two-predictor (in-degree AND operator-native in-mass)
    Xd = np.column_stack([np.ones(len(y)), XS["m_op"], XS["indeg"]])
    bb = np.linalg.lstsq(Xd, y, rcond=None)[0]
    rr = y - Xd @ bb
    Dp = float(bb[1] * (XS["m_op"][isL].mean() - XS["m_op"][~isL].mean())
               + bb[2] * (XS["indeg"][isL].mean() - XS["indeg"][~isL].mean()))
    Dr2 = float(rr[isL].mean() - rr[~isL].mean())
    _id2 = abs(Dy - (Dp + Dr2))
    _sc2 = max(1.0, float(np.abs(y).max()), abs(Dp), abs(Dr2))
    _maxid = max(_maxid, _id2)
    _maxsc = max(_maxsc, _id2 / _sc2)
    assert _id2 <= 64 * EPS * _sc2, (key, _id2, _sc2,
                                     "CERT-233B both (STOP)")
    _n233b += 1
    Z_ROW[key]["expl_both"] = Dp
    Z_ROW[key]["resid_both"] = Dr2
    Z_ROW[key]["share_both"] = (float(Dp / Dy) if Dy != 0 else None)
    log(f"[share] {sname:6s} {op:6s} {J}: D_logv1 {Dy:+.5f} "
        f"(1/|Dy| {Z_ROW[key]['cond_factor']:.1f}) share m_op "
        f"{Z_ROW[key]['share_m_op']:+.4f} indeg "
        f"{Z_ROW[key]['share_indeg']:+.4f} m_205 "
        f"{Z_ROW[key]['share_m_205']:+.4f} both "
        f"{Z_ROW[key]['share_both']:+.4f}")
assert _n233b == len(CELLS) * 4, (_n233b, "CERT-233B coverage (STOP)")
log(f"[CERT-233B] GREEN {_n233b} exact OLS identity checks "
    f"D_y == b*D_x + D_r (max |err| {_maxid:.3e}; max err/scale "
    f"{_maxsc:.3e} against 8*eps {8 * EPS:.3e}, the scale DERIVED from each "
    f"cell's own log-magnitudes — the share is an EXACT decomposition)")
P["cert_233b"] = dict(n_checks=_n233b, max_abs_identity_err=_maxid,
                      max_scaled_identity_err=_maxsc,
                      bar_single="8*eps*scale", bar_both="64*eps*scale",
                      scale="max(1, |log v1|max, |a|, |b*x|max, |Dy|, "
                            "|b*Dx|, |Dr|)",
                      repair="PREREG said 8*eps ABSOLUTE; the identity's "
                             "operands live on the log scale (|log v1| ~ 14) "
                             "while its result lives at ~0.1, so the bar is "
                             "conditioned on the operands (CERT-231A law). "
                             "Tooling repair, no registered quantity changed.")


# ---------------- leverage: leave-one-out, with its permutation null ------
def z_loo(v, isL):
    """A_cell^{-i} for every i, as a vector (per-cell mean asymmetry)."""
    v = np.asarray(v, float)
    ML, MR = float(v[isL].sum()), float(v[~isL].sum())
    nL, nR = int(isL.sum()), int((~isL).sum())
    a = np.where(isL, (ML - v) / (nL - 1), ML / nL)
    b = np.where(isL, MR / nR, (MR - v) / (nR - 1))
    return (a - b) / (a + b)


def z_gini(x):
    x = np.sort(np.abs(np.asarray(x, float)))
    n = len(x)
    s = x.sum()
    if s <= 0:
        return None
    return float((2.0 * np.arange(1, n + 1) - n - 1).dot(x) / (n * s))


_nloo = 0
for key in CELLS:
    sname, op, J = key
    lc, isL = ZL[(sname, J)], ZG[J]["isL"]
    v1 = PERRON[(sname, op)][1]
    v = v1[lc]
    A0 = Z_ROW[key]["A_inf"]
    dA = z_loo(v, isL) - A0
    # CERT-233B(ii): the closed-form LOO equals a direct recomputation on the
    # reduced cell set, on a deterministic 10% sample of cells.
    for i in range(0, len(v), 10):
        m = np.ones(len(v), bool)
        m[i] = False
        _ML = float(v[m & isL].sum()) / int((m & isL).sum())
        _MR = float(v[m & ~isL].sum()) / int((m & ~isL).sum())
        assert abs(asym(_ML, _MR) - (A0 + dA[i])) <= 8 * EPS, \
            (key, i, "LOO closed form (STOP)")
        _nloo += 1
    lev = np.abs(dA)
    lev1 = float(lev.max() / abs(A0))
    j1 = int(np.argmax(lev))
    # permutation null on the SAME statistic, over the fixed PERM draws
    Pf, Pe = PERM[(J, "f")], PERM[(J, "e")]
    LM = np.concatenate([Pf, Pe], axis=1)
    assert LM.shape == (NDRAW, len(v)), LM.shape
    nlev1 = np.empty(NDRAW)
    nL, nR = Z_SIDEN[J]
    for d in range(NDRAW):
        mL = LM[d]
        assert int(mL.sum()) == nL
        An = z_loo(v, mL)
        A0n = asym(float(v[mL].sum()) / nL, float(v[~mL].sum()) / nR)
        nlev1[d] = np.abs(An - A0n).max() / abs(A0n)
    # greedy drop count — DESCRIPTION only (PREREG 0i), no branch
    keep = np.ones(len(v), bool)
    kneed, p95 = None, abs(Z_ROW[key]["A_inf_null_p95"])
    for step in range(1, len(v)):
        if min(int((keep & isL).sum()), int((keep & ~isL).sum())) <= 3:
            break
        cand = z_loo(v[keep], isL[keep])
        jj = int(np.argmin(np.abs(cand)))
        idx = np.where(keep)[0][jj]
        keep[idx] = False
        cur = abs(asym(float(v[keep & isL].sum()) / int((keep & isL).sum()),
                       float(v[keep & ~isL].sum()) / int((keep & ~isL).sum())))
        if cur < p95:
            kneed = step
            break
    Z_ROW[key].update(
        lev1=lev1, lev1_cell_is_left=bool(isL[j1]),
        lev1_cell_type=Z_CT[int(ZG[J]["g"][j1])],
        lev1_null_mean=float(nlev1.mean()),
        lev1_null_p95=float(np.percentile(nlev1, 95)),
        lev1_pct_up=float((nlev1 <= lev1).mean()),
        lev_gini=z_gini(dA),
        lev_top5_share=float(np.sort(lev)[-5:].sum() / lev.sum()),
        greedy_k_to_null_p95=kneed,
        greedy_k_frac=(kneed / len(v) if kneed else None))
    log(f"[lev] {sname:6s} {op:6s} {J}: lev1 {lev1:.4f} (null mean "
        f"{nlev1.mean():.4f} p95 {np.percentile(nlev1, 95):.4f} pct "
        f"{Z_ROW[key]['lev1_pct_up']:.3f}) gini "
        f"{Z_ROW[key]['lev_gini']:.3f} top5 "
        f"{Z_ROW[key]['lev_top5_share']:.3f} greedy_k {kneed}")
log(f"[CERT-233B ii] GREEN {_nloo} closed-form LOO checks against direct "
    f"recomputation at <= 8*eps")
P["cert_233b_loo"] = dict(n_checks=_nloo, bar=8 * EPS)

# ---------------- the TYPE-level mirror-match leg (PREREG 0a) -------------
for key in CELLS:
    sname, op, J = key
    lc, isL, gc = ZL[(sname, J)], ZG[J]["isL"], ZG[J]["g"]
    v = PERRON[(sname, op)][1][lc]
    ty = np.array([Z_CT[int(x)] for x in gc])
    sh = set(Z_SHARED[J])
    mm = np.array([t in sh for t in ty])
    A_sh = asym(float(v[mm & isL].sum()) / int((mm & isL).sum()),
                float(v[mm & ~isL].sum()) / int((mm & ~isL).sum()))
    lrs, tnames = [], []
    for t in Z_SHARED[J]:
        mt = ty == t
        mL = float(v[mt & isL].mean())
        mR = float(v[mt & ~isL].mean())
        lrs.append(math.log(mL) - math.log(mR))
        tnames.append(t)
    lrs = np.array(lrs)
    npos = int((lrs > 0).sum())
    nT = len(lrs)
    _le = sum(math.comb(nT, i) for i in range(npos + 1)) / 2.0 ** nT
    _ge = sum(math.comb(nT, i) for i in range(npos, nT + 1)) / 2.0 ** nT
    Z_ROW[key].update(
        n_mirror_cells=int(mm.sum()),
        mirror_frac=float(mm.mean()),
        A_inf_shared=A_sh,
        retention=float(abs(A_sh) / abs(Z_ROW[key]["A_inf"])),
        same_sign=bool(np.sign(A_sh) == np.sign(Z_ROW[key]["A_inf"])),
        n_shared_types=nT, n_types_positive=npos,
        type_logratio_mean=float(lrs.mean()),
        type_logratio_median=float(np.median(lrs)),
        signtest_p=float(min(1.0, 2.0 * min(_le, _ge))),
        type_logratio={t: float(x) for t, x in zip(tnames, lrs)})
    log(f"[hom] {sname:6s} {op:6s} {J}: mirror cells "
        f"{int(mm.sum())}/{len(v)} A_inf {Z_ROW[key]['A_inf']:+.6f} -> "
        f"A_inf_shared {A_sh:+.6f} retention "
        f"{Z_ROW[key]['retention']:.4f} | types {npos}/{nT} positive "
        f"(sign test p {Z_ROW[key]['signtest_p']:.4f}) mean log-ratio "
        f"{lrs.mean():+.4f}")

# ---------------- BRANCHES (registered order) ----------------------------
_pr = [Z_ROW[(Z_PRIMARY[0], Z_PRIMARY[1], J)] for J in JOINTS]
Z_SHARE_PRIM = float(np.mean([r["share_m_op"] for r in _pr]))
if Z_SHARE_PRIM >= Z_SHARE_HI:
    Q1 = "D_DEGREE"
elif Z_SHARE_PRIM >= Z_SHARE_LO:
    Q1 = "D_PARTIAL"
else:
    Q1 = "D_MODE"
Q2 = ("L_CONCENTRATED" if max(r["lev1"] for r in _pr) >= Z_LEV_BAR
      else "L_DISTRIBUTED")
_ti = Z_ROW[(Z_PRIMARY[0], Z_PRIMARY[1], "Ti")]
Q3 = ("H_ROBUST" if (_ti["same_sign"] and _ti["retention"] >= Z_HOM_BAR)
      else "H_COMPOSITION")
P["Q1_share"] = dict(branch=Q1, share_m_op_primary_mean=Z_SHARE_PRIM,
                     bars=[Z_SHARE_LO, Z_SHARE_HI],
                     per_joint={r["joint"]: r["share_m_op"] for r in _pr},
                     share_indeg={r["joint"]: r["share_indeg"] for r in _pr},
                     share_m205={r["joint"]: r["share_m_205"] for r in _pr},
                     share_both={r["joint"]: r["share_both"] for r in _pr},
                     demotes_A_inf_family=bool(Q1 == "D_DEGREE"))
P["Q2_leverage"] = dict(branch=Q2, bar=Z_LEV_BAR,
                        lev1_primary={r["joint"]: r["lev1"] for r in _pr},
                        lev1_max_all_cells=max(Z_ROW[k]["lev1"] for k in CELLS))
P["Q3_mirror"] = dict(branch=Q3, bar=Z_HOM_BAR,
                      Ti_retention=_ti["retention"],
                      Ti_same_sign=_ti["same_sign"],
                      Ti_A_inf=_ti["A_inf"], Ti_A_inf_shared=_ti["A_inf_shared"],
                      Tr_retention=Z_ROW[(Z_PRIMARY[0], Z_PRIMARY[1],
                                          "Tr")]["retention"])

# ---------------- PREDICTIONS -------------------------------------------
_f4b = [Z_ROW[("f4wA", "beta", J)]["share_m_op"] for J in JOINTS]
_f4c = [Z_ROW[("f4wA", "crofts", J)]["share_m_op"] for J in JOINTS]
_d5 = float(np.mean(_f4b) - np.mean(_f4c))
PRED = dict(
    P1=dict(claim="rho_m_op >= +0.50 on the primary arm for BOTH joints",
            value=[r["rho_m_op"] for r in _pr],
            ok=bool(all(r["rho_m_op"] >= Z_RHO_BAR for r in _pr))),
    P2=dict(claim="sign(A_m205) == sign(A_inf), primary arm, both joints",
            value=[[r["A_m205"], r["A_inf"]] for r in _pr],
            ok=bool(all(np.sign(r["A_m205"]) == np.sign(r["A_inf"])
                        for r in _pr))),
    P3=dict(claim="Q1 == D_PARTIAL", value=Q1, ok=bool(Q1 == "D_PARTIAL")),
    P4=dict(claim="lev1 < 0.50 on ALL 8 cells (L_DISTRIBUTED)",
            value=max(Z_ROW[k]["lev1"] for k in CELLS),
            ok=bool(max(Z_ROW[k]["lev1"] for k in CELLS) < Z_LEV_BAR)),
    P5=dict(claim="on f4wA, mean share_m_op(beta) - share_m_op(crofts) "
                  "> +0.20 (Crofts is less degree-explained)",
            value=_d5, ok=bool(_d5 > Z_P5_BAR)),
    P6=dict(claim="Q3 == H_ROBUST", value=Q3, ok=bool(Q3 == "H_ROBUST")))
P["predictions"] = PRED
P["n_predictions_true"] = sum(1 for v in PRED.values() if v["ok"])

# ---------------- omnibus over the SHARED draw index (PREREG 0f) ---------
# The eight cells consume TWO relabellings, so the only honest aggregate
# significance statement is a joint statistic on the shared draw index.
_om = {}
for stat, fld in (("A_inf", "A_inf"), ("A_mop", "A_mop"),
                  ("A_indeg", "A_indeg")):
    cnt = np.zeros(NDRAW, int)
    real = 0
    for key in CELLS:
        sname, op, J = key
        lc, gc = ZL[(sname, J)], ZG[J]["g"]
        if stat == "A_inf":
            vv = PERRON[(sname, op)][1][lc]
        elif stat == "A_mop":
            vv = Z_MOP[(sname, op)][lc]
        else:
            vv = Z_DEG[sname][lc]
        nL, nR = Z_SIDEN[J]
        LM = np.concatenate([PERM[(J, "f")], PERM[(J, "e")]], axis=1)
        sL = LM @ vv
        sR = float(vv.sum()) - sL
        an = (sL / nL - sR / nR) / (sL / nL + sR / nR)
        cnt += (an > 0).astype(int)
        real += int(Z_ROW[key][fld] > 0)
    _om[stat] = dict(real_n_positive=real,
                     null_mean=float(cnt.mean()),
                     null_median=float(np.median(cnt)),
                     p_omni=float((cnt >= real).mean()),
                     note=("A_indeg is operator-INVARIANT (PREREG 0c), so "
                           "its 8 cells are 4 distinct vectors counted twice"
                           if stat == "A_indeg" else
                           "8 distinct vectors over 2 relabellings"),
                     hist={int(k): int(v) for k, v in
                           zip(*np.unique(cnt, return_counts=True))})
    log(f"[omni] {stat}: real {real}/8 cells positive vs null mean "
        f"{cnt.mean():.3f} -> p_omni {_om[stat]['p_omni']:.4f}")
P["omnibus"] = _om
P["effective_family_width"] = Z_WIDTH

# ---------------- table out ----------------------------------------------
P["table"] = {f"{sn}|{op}|{J}": Z_ROW[(sn, op, J)] for (sn, op, J) in CELLS}
P["bars"] = dict(share_hi=Z_SHARE_HI, share_lo=Z_SHARE_LO, lev=Z_LEV_BAR,
                 rho=Z_RHO_BAR, hom=Z_HOM_BAR, dy=Z_DY_BAR, p5=Z_P5_BAR)
P["runtime_s"] = time.time() - _T233
log(f"[L233] Q1 {Q1} (share_m_op {Z_SHARE_PRIM:+.4f}) | Q2 {Q2} | Q3 {Q3} | "
    f"predictions {P['n_predictions_true']}/6 | {P['runtime_s']:.0f}s")
os.makedirs("l233", exist_ok=True)
json.dump(P, open("l233/static.json", "w"), indent=1, default=str)
log("[L233] DONE")
