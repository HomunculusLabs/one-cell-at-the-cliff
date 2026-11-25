
# =========================== L237 TAIL =====================================
# WHY do those 69 cells have low u1? the destination-geometry leg.
# PREREG l237/PREREG.md, registered BEFORE this run. Writes l237/static.json.

_RO237 = ["l236/static.json", "l233/static.json", "l231_tail.py"]
_FP237 = {}
for _p in _RO237:
    _st = _os236.stat(_p)
    _FP237[_p] = (int(_st.st_size), int(_st.st_mtime_ns))
S236 = json.load(open("l236/static.json"))
log(f"[L237 read-only] fingerprinted {len(_FP237)} further artifacts")

o237 = {}
o237["design"] = dict(
    card="L237",
    question=("WHY do the carrier's 69 target cells have low u1? the "
              "destination-geometry leg, against the 9,803-cell l169c menu"),
    prereg="l237/PREREG.md",
    rollouts=0,
    parent_branch_l219=S219["Q219_1_primary"]["branch"],
    carrier_Q_stored=S219["Q219_1_primary"]["real"]["Q"],
    carrier_align_stored=S219["Q219_1_primary"]["real"]["align"])

# ---------------- the population: the MENU's distinct cells ----------------
MCELLS = np.unique(MENU).astype(np.int64)
_menu_stored = S219["Q219_3_weight_matched"]["menu"]
assert int(MCELLS.size) == int(_menu_stored["n_distinct"]), \
    (MCELLS.size, _menu_stored, "menu cell count moved (STOP)")
assert int(MENU.size) == int(_menu_stored["n_edges"]), "menu edge count (STOP)"
NM = int(MCELLS.size)

# global ids per local f4wA index (inverse of loc_f4)
GI_OF_LOC = np.where(keep_f4)[0]
assert GI_OF_LOC.size == NL and int(loc_f4[GI_OF_LOC[LC_CAR]]) == LC_CAR
assert int(GI_OF_LOC[LC_CAR]) == GI_CARRIER, "local<->global map (STOP)"


def _anncol237(name):
    """annotation column lifted to a per-GLOBAL-id array (blank = unlabelled)."""
    v = np.full(Nall, "", dtype=object)
    v[ann_gi] = ann[name].fillna("").astype(str).to_numpy()
    return v


SUPG = _anncol237("super_class")
CLSG = _anncol237("cell_class")
TYPG = _anncol237("cell_type")
SIDEG = _anncol237("side")
REGG = _anncol237("region")

# ---------------- operator-native degrees and masses, BOTH directions ------
# CSR orientation (asserted in SLICE P): csr_rows = TARGET, csr_cols = SOURCE.
IN_MASS = np.bincount(csr_rows, weights=jv_abs_an, minlength=NL)
OUT_MASS = np.bincount(csr_cols, weights=jv_abs_an, minlength=NL)
IN_DEG = np.bincount(csr_rows, minlength=NL).astype(np.float64)
OUT_DEG = np.bincount(csr_cols, minlength=NL).astype(np.float64)
assert IN_MASS.size == NL and OUT_MASS.size == NL
assert abs(float(IN_MASS.sum()) - float(jv_abs_an.sum())) < 1e-6
assert abs(float(OUT_MASS.sum()) - float(jv_abs_an.sum())) < 1e-6
assert int(OUT_DEG[LC_CAR]) == 69, (OUT_DEG[LC_CAR], "carrier out-degree")
assert abs(float(OUT_MASS[LC_CAR]) - MOUT_OP) < 1e-12, "carrier out-mass"
log(f"[L237 pop] menu cells {NM:,} / {int(MENU.size):,} edges | in-mass "
    f"median {float(np.median(IN_MASS[MCELLS])):.6f} out-mass median "
    f"{float(np.median(OUT_MASS[MCELLS])):.6f}")

# ---------------- PREREG 0c: the outcome's ZEROS, measured BEFORE any fit --
UM = U1[MCELLS].astype(np.float64)
_zero = UM == 0.0
N_ZERO = int(_zero.sum())
FRAC_ZERO = float(N_ZERO / NM)
_t_car_u = U1[T_CAR].astype(np.float64)
o237["Q0_zeros"] = dict(
    n_menu_cells=NM, n_zero=N_ZERO, frac_zero=FRAC_ZERO,
    n_zero_among_69_targets=int((_t_car_u == 0.0).sum()),
    n_distinct_69_targets=int(np.unique(T_CAR).size),
    median_out_deg_zero=(float(np.median(OUT_DEG[MCELLS[_zero]]))
                         if N_ZERO else None),
    median_out_deg_nonzero=float(np.median(OUT_DEG[MCELLS[~_zero]])),
    median_in_deg_zero=(float(np.median(IN_DEG[MCELLS[_zero]]))
                        if N_ZERO else None),
    median_in_deg_nonzero=float(np.median(IN_DEG[MCELLS[~_zero]])),
    law=("L224: a zero in the outcome is a MODEL-FAMILY verdict. The midrank "
         "Spearman is the PRIMARY currency because it admits zeros as a tie "
         "group; the log reading is a disclosed secondary on u1 > 0."))
log(f"[Q0] u1 zeros on the menu: {N_ZERO}/{NM} = {FRAC_ZERO:.6f} | zero-cell "
    f"median out-deg {o237['Q0_zeros']['median_out_deg_zero']} vs nonzero "
    f"{o237['Q0_zeros']['median_out_deg_nonzero']}")

# ---------------- CERT-237Z (HALTING): PREREG 0k's proof -------------------
# out-degree 0 => u1 == 0 exactly; and a cell all of whose targets are zero-u1
# is itself zero-u1. Every zero-u1 menu cell must satisfy one of the two.
_n237z = 0
_zcells = MCELLS[_zero]
_byz = dict(no_out_edges=0, all_targets_zero=0)
for _c in _zcells.tolist():
    _ie = np.where(csr_cols == _c)[0]
    if _ie.size == 0:
        _byz["no_out_edges"] += 1
    else:
        assert float(np.abs(U1[csr_rows[_ie]]).max()) == 0.0, \
            (_c, "CERT-237Z: zero-u1 cell with a nonzero-u1 target (STOP)")
        _byz["all_targets_zero"] += 1
    _n237z += 1
# and the converse direction on a sample: out-degree 0 cells ARE zero
_od0 = MCELLS[OUT_DEG[MCELLS] == 0]
for _c in _od0.tolist():
    assert float(U1[_c]) == 0.0, (_c, "CERT-237Z converse (STOP)")
    _n237z += 1
log(f"[CERT-237Z] GREEN {_n237z} checks | {_byz} | out-deg-0 menu cells "
    f"{int(_od0.size)}")
o237["cert_237z"] = dict(n_checks=int(_n237z), breakdown=_byz,
                         n_outdeg0_menu_cells=int(_od0.size),
                         law="PREREG 0k: a PROOF, asserted, never a finding")

# ---------------- the vectorised decomposition + CERT-237D -----------------
# u1[t] = (m_out(t)/lam1) * Q(t) * align(t), the identity SLICE H's decomp219
# computes per cell. Vectorised here over the whole menu, then GATED against
# decomp219 on EVERY measurable cell (the CERT-MV / CERT-236K pattern).
MU_U1 = float(U1.mean())
assert MU_U1 > 0.0


def dec237(cells):
    """vectorised decomp219 over an array of local cell indices."""
    n = cells.size
    mo = np.zeros(n); S = np.zeros(n); mq = np.zeros(n); nt = np.zeros(n)
    for i, c in enumerate(cells.tolist()):
        ie = np.where(csr_cols == c)[0]
        if ie.size == 0:
            mq[i] = np.nan
            continue
        w = jv_abs_an[ie]
        ut = U1[csr_rows[ie]]
        mo[i] = float(w.sum())
        S[i] = float(w @ ut)
        mq[i] = float(ut.mean())
        nt[i] = ie.size
    with np.errstate(divide="ignore", invalid="ignore"):
        U = U1[cells] / MU_U1
        Q = mq / MU_U1
        al = (S / mo) / mq
    return dict(U=U, Q=Q, align=al, m_out=mo, S=S, mean_target_u=mq, n_out=nt)


D237 = dec237(MCELLS)
MEAS = np.isfinite(D237["Q"]) & (D237["Q"] > 0.0) & (D237["m_out"] > 0.0)
N_MEAS = int(MEAS.sum())
log(f"[L237 decomp] measurable menu cells {N_MEAS:,}/{NM:,} "
    f"(unmeasurable {NM - N_MEAS:,}: no out-edges or all-zero-u1 targets)")

_n237d = 0
_maxd = 0.0
for _i in np.where(MEAS)[0].tolist():
    _c = int(MCELLS[_i])
    _ie = np.where(csr_cols == _c)[0]
    _ref = decomp219(U1, jv_abs_an[_ie], csr_rows[_ie].astype(np.int64),
                     LAM1, _c)
    for _k, _v in (("U", D237["U"][_i]), ("Q", D237["Q"][_i]),
                   ("align", D237["align"][_i]), ("m_out", D237["m_out"][_i]),
                   ("S", D237["S"][_i])):
        assert float(_ref[_k]) == float(_v), \
            (_c, _k, _ref[_k], _v, "CERT-237D (STOP)")
        _n237d += 1
    _maxd = max(_maxd, float(_ref["ident_rel"]))
assert _maxd < 1e-10, (_maxd, "identity (II) on the menu (STOP)")
log(f"[CERT-237D] GREEN {_n237d:,} float equalities vs SLICE H's decomp219 "
    f"on all {N_MEAS:,} measurable menu cells | max identity rel {_maxd:.3e}")
o237["cert_237d"] = dict(n_checks=int(_n237d), n_cells=N_MEAS,
                         max_identity_rel=_maxd, bar=1e-10,
                         mode="float equality (==)",
                         note=("a new kernel is admitted only by EXACT "
                               "agreement with the certified one"))

# ---------------- Q1: composition of the 69 vs the EDGE-weighted menu ------
# PREREG 0f: the reference is a draw of 69 EDGE destinations from MENU.
MENU_SUP = SUPG[GI_OF_LOC[MENU]]
CAR_SUP = SUPG[GI_OF_LOC[T_CAR]]
CLASSES = sorted(set(MENU_SUP.tolist()) | set(CAR_SUP.tolist()))
_mi = {c: i for i, c in enumerate(CLASSES)}
_menu_code = np.array([_mi[x] for x in MENU_SUP.tolist()], np.int64)
_car_code = np.array([_mi[x] for x in CAR_SUP.tolist()], np.int64)
SH_MENU = np.bincount(_menu_code, minlength=len(CLASSES)) / float(MENU.size)
SH_CAR = np.bincount(_car_code, minlength=len(CLASSES)) / 69.0
D_MAX_REAL = float(np.abs(SH_CAR - SH_MENU).max())

B1 = 20000
_rng1 = np.random.default_rng(23702)
_idx1 = _rng1.integers(0, MENU.size, size=(B1, 69))
_dr = _menu_code[_idx1]
_cnt = np.zeros((B1, len(CLASSES)), np.float64)
for _k in range(len(CLASSES)):
    _cnt[:, _k] = (_dr == _k).sum(axis=1)
_shd = _cnt / 69.0
_dmax_null = np.abs(_shd - SH_MENU[None, :]).max(axis=1)
P_DMAX = float((_dmax_null >= D_MAX_REAL).mean())
FLOOR1 = 1.0 / (B1 + 1.0)
P_DMAX = max(P_DMAX, FLOOR1) if P_DMAX == 0.0 else P_DMAX

# per-class two-sided permutation p + BH-FDR (PREREG 0g)
_pcls = []
for _k, _c in enumerate(CLASSES):
    _d = abs(SH_CAR[_k] - SH_MENU[_k])
    _pk = float((np.abs(_shd[:, _k] - SH_MENU[_k]) >= _d).mean())
    _pk = max(_pk, FLOOR1)
    _pcls.append(dict(super_class=_c, share_menu=float(SH_MENU[_k]),
                      share_69=float(SH_CAR[_k]),
                      n_69=int((_car_code == _k).sum()),
                      enrichment=(float(SH_CAR[_k] / SH_MENU[_k])
                                  if SH_MENU[_k] > 0 else None),
                      p_perm=_pk))
_m1 = len(_pcls)
_ordp = sorted(range(_m1), key=lambda i: _pcls[i]["p_perm"])
_q = [None] * _m1
_run = 1.0
for _r in range(_m1 - 1, -1, -1):
    _i = _ordp[_r]
    _run = min(_run, _pcls[_i]["p_perm"] * _m1 / (_r + 1))
    _q[_i] = _run
for _i in range(_m1):
    _pcls[_i]["q_bh"] = float(_q[_i])
    _pcls[_i]["bh_reject_q05"] = bool(_q[_i] < 0.05)
N_FLOOR_TIED = int(sum(1 for r in _pcls if r["p_perm"] <= FLOOR1))
BRANCH_Q1 = "C_BIASED" if P_DMAX < 0.05 else "C_TYPICAL"
log(f"[Q1] D_max {D_MAX_REAL:.4f} p_perm {P_DMAX:.5f} -> {BRANCH_Q1} | "
    f"{_m1} classes, {sum(r['bh_reject_q05'] for r in _pcls)} BH-rejected, "
    f"{N_FLOOR_TIED} tied at the floor {FLOOR1:.2e}")
o237["Q1_composition"] = dict(
    branch=BRANCH_Q1, D_max=D_MAX_REAL, p_perm=P_DMAX, B=B1,
    resolution_floor=FLOOR1, bh_rank1_bar=0.05 / _m1, n_classes=_m1,
    n_bh_rejected=int(sum(r["bh_reject_q05"] for r in _pcls)),
    n_tied_at_floor=N_FLOOR_TIED, per_class=_pcls,
    reference=("PREREG 0f: 69 EDGE destinations drawn from the 49,076-edge "
               "menu, matching L219's own null"))

# ---------------- Q2: the nested held-out comparison (the card's order) ----
Y = midrank(UM)
_x_in_mass = np.log1p(IN_MASS[MCELLS])
_x_out_mass = np.log1p(OUT_MASS[MCELLS])
_x_in_deg = np.log1p(IN_DEG[MCELLS])
_x_out_deg = np.log1p(OUT_DEG[MCELLS])
_sup_m = SUPG[GI_OF_LOC[MCELLS]]
_sup_lv = sorted(set(_sup_m.tolist()))
_OH = np.zeros((NM, len(_sup_lv) - 1))
for _k, _c in enumerate(_sup_lv[1:]):
    _OH[:, _k] = (_sup_m == _c).astype(np.float64)

RHO_IN_OUT = spearman(_x_in_mass, _x_out_mass)          # PREREG 0e, FIRST
log(f"[Q2 0e] rho(in-mass, out-mass) over the menu = {RHO_IN_OUT:.6f}")

MODELS = {
    "M1_in_mass": np.column_stack([_x_in_mass]),
    "M2_plus_out_mass": np.column_stack([_x_in_mass, _x_out_mass]),
    "M3_plus_superclass": np.column_stack([_x_in_mass, _x_out_mass, _OH]),
    "M4_plus_degrees": np.column_stack([_x_in_mass, _x_out_mass, _OH,
                                        _x_in_deg, _x_out_deg]),
}
_rng0 = np.random.default_rng(23701)
FOLD = _rng0.permutation(NM) % 5
assert set(np.unique(FOLD).tolist()) == {0, 1, 2, 3, 4}


def cv237(X, y):
    per = []
    for f in range(5):
        te = FOLD == f
        tr = ~te
        A = np.column_stack([np.ones(int(tr.sum())), X[tr]])
        b, *_ = np.linalg.lstsq(A, y[tr], rcond=None)
        pr = np.column_stack([np.ones(int(te.sum())), X[te]]) @ b
        per.append(spearman(pr, y[te]))
    return float(np.mean(per)), [float(x) for x in per]


Q2 = {}
for _nm, _X in MODELS.items():
    _mu, _per = cv237(_X, Y)
    Q2[_nm] = dict(rho_heldout=_mu, per_fold=_per, n_features=int(_X.shape[1]))
RHO1 = Q2["M1_in_mass"]["rho_heldout"]
GAIN2 = Q2["M2_plus_out_mass"]["rho_heldout"] - RHO1
GAIN3 = Q2["M3_plus_superclass"]["rho_heldout"] \
    - Q2["M2_plus_out_mass"]["rho_heldout"]
GAIN4 = Q2["M4_plus_degrees"]["rho_heldout"] \
    - Q2["M3_plus_superclass"]["rho_heldout"]
BRANCH_Q2 = ("IN_STRUCTURE_EXPLAINS" if RHO1 >= 0.70
             else "PARTIAL" if RHO1 >= 0.30 else "NOT_IN_STRUCTURE")
# the single out-side predictor ALONE, as a disclosed diagnostic
RHO_OUT_ONLY, _per_oo = cv237(np.column_stack([_x_out_mass]), Y)
log(f"[Q2] rho1(in-mass) {RHO1:.6f} -> {BRANCH_Q2} | +out-mass {GAIN2:+.6f} "
    f"| +superclass {GAIN3:+.6f} | +degrees {GAIN4:+.6f} | out-mass ALONE "
    f"{RHO_OUT_ONLY:.6f}")
o237["Q2_nested"] = dict(
    branch=BRANCH_Q2, rho1_in_mass=RHO1, bars=dict(explains=0.70, partial=0.30),
    models=Q2, gains=dict(out_mass=GAIN2, superclass=GAIN3, degrees=GAIN4),
    rho_out_mass_alone=RHO_OUT_ONLY, out_mass_alone_per_fold=_per_oo,
    rho_in_mass_vs_out_mass=RHO_IN_OUT,
    outcome="midrank(u1) over the full menu population (PREREG 0d)",
    folds=5, seed=23701,
    nesting_order=("the CARD's own order, kept verbatim per PREREG 0a: "
                   "in-mass first even though u1 is an OUT-edge identity"))

# ---------------- Q2b: the identity decomposition of the 69's deficit ------
# PREREG 0L. log u1 = log m_out + log Q + log align - log lam1, exactly.
_tc = np.unique(T_CAR).astype(np.int64)
DT = dec237(_tc)
_ok_t = np.isfinite(DT["Q"]) & (DT["Q"] > 0.0) & (DT["m_out"] > 0.0) \
    & (DT["align"] > 0.0) & (U1[_tc] > 0.0)
_ok_m = MEAS & (D237["align"] > 0.0) & (U1[MCELLS] > 0.0)
N_T_OK, N_M_OK = int(_ok_t.sum()), int(_ok_m.sum())


def _lm(a):
    return float(np.mean(np.log(a)))


_d_logu = _lm(U1[_tc][_ok_t]) - _lm(U1[MCELLS][_ok_m])
_d_mout = _lm(DT["m_out"][_ok_t]) - _lm(D237["m_out"][_ok_m])
_d_q = _lm(DT["Q"][_ok_t]) - _lm(D237["Q"][_ok_m])
_d_al = _lm(DT["align"][_ok_t]) - _lm(D237["align"][_ok_m])
_sum = _d_mout + _d_q + _d_al
_scale = max(1.0, abs(_d_logu), abs(_d_mout), abs(_d_q), abs(_d_al))
_ident_err = abs(_sum - _d_logu)
assert _ident_err / _scale < 64 * np.finfo(np.float64).eps, \
    (_ident_err, _scale, "GATE-IDENT (STOP)")
SH_MOUT, SH_Q, SH_AL = (_d_mout / _d_logu, _d_q / _d_logu, _d_al / _d_logu)
BRANCH_Q2B = ("M_OUT_MASS" if SH_MOUT >= 0.50 else
              "M_RECURSES" if SH_Q >= 0.50 else
              "M_ALIGN" if SH_AL >= 0.50 else "M_MIXED")
log(f"[Q2b] D log u1 {_d_logu:+.6f} = m_out {_d_mout:+.6f} + Q {_d_q:+.6f} "
    f"+ align {_d_al:+.6f} | shares {SH_MOUT:+.4f}/{SH_Q:+.4f}/{SH_AL:+.4f} "
    f"-> {BRANCH_Q2B} | ident err/scale {_ident_err / _scale:.3e}")
o237["Q2b_identity_shares"] = dict(
    branch=BRANCH_Q2B, delta_log_u1=_d_logu,
    delta_log_m_out=_d_mout, delta_log_Q=_d_q, delta_log_align=_d_al,
    share_m_out=float(SH_MOUT), share_Q=float(SH_Q), share_align=float(SH_AL),
    identity_err=_ident_err, identity_scale=_scale,
    identity_err_over_scale=float(_ident_err / _scale),
    identity_ulps=float(_ident_err / _scale / np.finfo(np.float64).eps),
    n_targets_used=N_T_OK, n_targets=int(_tc.size),
    n_menu_used=N_M_OK, n_menu=NM,
    signed_share_law=("L211/L233: every share admits every sign its own "
                      "definition allows; a negative share is a SUPPRESSOR"),
    excluded=("cells with u1 == 0, no out-edges, or an all-zero-u1 target "
              "set: undefined in logs, counted not dropped silently (L224)"))

# ---------------- Q3: robustness of the Q2 branch --------------------------
_pos = UM > 0.0
_Ylog = np.log(UM[_pos])
Q3 = {}
for _nm, _X in MODELS.items():
    _Xp = _X[_pos]
    _per = []
    _Fp = FOLD[_pos]
    for _f in range(5):
        _te = _Fp == _f
        _tr = ~_te
        _A = np.column_stack([np.ones(int(_tr.sum())), _Xp[_tr]])
        _b, *_ = np.linalg.lstsq(_A, _Ylog[_tr], rcond=None)
        _pr = np.column_stack([np.ones(int(_te.sum())), _Xp[_te]]) @ _b
        _per.append(spearman(_pr, _Ylog[_te]))
    Q3[_nm] = dict(rho_heldout=float(np.mean(_per)),
                   per_fold=[float(x) for x in _per])
RHO1_LOG = Q3["M1_in_mass"]["rho_heldout"]
BR_LOG = ("IN_STRUCTURE_EXPLAINS" if RHO1_LOG >= 0.70
          else "PARTIAL" if RHO1_LOG >= 0.30 else "NOT_IN_STRUCTURE")

_od1 = OUT_DEG[MCELLS] >= 1
Q3B = {}
for _nm, _X in MODELS.items():
    _per = []
    _Fp = FOLD[_od1]
    _Xp, _Yp = _X[_od1], Y[_od1]
    for _f in range(5):
        _te = _Fp == _f
        _tr = ~_te
        _A = np.column_stack([np.ones(int(_tr.sum())), _Xp[_tr]])
        _b, *_ = np.linalg.lstsq(_A, _Yp[_tr], rcond=None)
        _pr = np.column_stack([np.ones(int(_te.sum())), _Xp[_te]]) @ _b
        _per.append(spearman(_pr, _Yp[_te]))
    Q3B[_nm] = dict(rho_heldout=float(np.mean(_per)),
                    per_fold=[float(x) for x in _per])
RHO1_OD1 = Q3B["M1_in_mass"]["rho_heldout"]
BR_OD1 = ("IN_STRUCTURE_EXPLAINS" if RHO1_OD1 >= 0.70
          else "PARTIAL" if RHO1_OD1 >= 0.30 else "NOT_IN_STRUCTURE")
BRANCH_Q3 = "H_ROBUST" if (BR_LOG == BRANCH_Q2 and BR_OD1 == BRANCH_Q2) \
    else "H_FRAGILE"
log(f"[Q3] {BRANCH_Q3} | log-currency rho1 {RHO1_LOG:.6f} ({BR_LOG}, n "
    f"{int(_pos.sum()):,}) | out-deg>=1 rho1 {RHO1_OD1:.6f} ({BR_OD1}, n "
    f"{int(_od1.sum()):,})")
o237["Q3_robustness"] = dict(
    branch=BRANCH_Q3, arm_log=dict(models=Q3, rho1=RHO1_LOG, branch=BR_LOG,
                                   n=int(_pos.sum())),
    arm_outdeg1=dict(models=Q3B, rho1=RHO1_OD1, branch=BR_OD1,
                     n=int(_od1.sum())))

# ---------------- the bilateral homolog (PREREG 0h) ------------------------
_lc_h = int(loc_f4[GI_HOMOLOG])
assert _lc_h >= 0, "homolog dropped by keep_f4 (STOP)"
_ieh = np.where(csr_cols == _lc_h)[0]
DH = decomp219(U1, jv_abs_an[_ieh], csr_rows[_ieh].astype(np.int64),
               LAM1, _lc_h)
_th = csr_rows[_ieh].astype(np.int64)
_hsup = SUPG[GI_OF_LOC[_th]]
_hcode = np.array([_mi.get(x, -1) for x in _hsup.tolist()], np.int64)
SH_HOM = np.bincount(_hcode[_hcode >= 0], minlength=len(CLASSES)) \
    / float(_th.size)
_dmax_hom = float(np.abs(SH_HOM - SH_MENU).max())
log(f"[homolog] gi {GI_HOMOLOG} n_out {_th.size} Q {DH['Q']:.6f} align "
    f"{DH['align']:.6f} (carrier Q {DR['Q']:.6f}) D_max {_dmax_hom:.4f}")
o237["homolog"] = dict(
    gi=GI_HOMOLOG, source="l207/static.json Q2_mirror.mirror_identity.gi",
    n_out=int(_th.size), Q=DH["Q"], align=DH["align"], U=DH["U"],
    m_out=DH["m_out"], carrier_Q=DR["Q"], carrier_align=DR["align"],
    Q_over_carrier_Q=float(DH["Q"] / DR["Q"]), D_max_vs_menu=_dmax_hom,
    per_class=[dict(super_class=CLASSES[_k], share=float(SH_HOM[_k]),
                    share_menu=float(SH_MENU[_k]))
               for _k in range(len(CLASSES)) if SH_HOM[_k] > 0 or
               SH_CAR[_k] > 0],
    l236_r_mean_homolog=S236["Q236_3_homolog"]["r_mean"],
    l236_Q_homolog=S236["Q236_3_homolog"]["Q"],
    l236_n_out_homolog=S236["Q236_3_homolog"]["n_out"],
    law="L207/L212: the homolog is the cheapest control available")
# the homolog's Q/align/n_out are STORED by L236 — assert, never recompute
# blind (float equality against the parent's own measurement)
assert int(_th.size) == int(S236["Q236_3_homolog"]["n_out"]), "homolog n_out"
assert float(DH["Q"]) == float(S236["Q236_3_homolog"]["Q"]), "homolog Q"
assert float(DH["align"]) == float(S236["Q236_3_homolog"]["align"]), \
    "homolog align"
log("[CERT-237H] GREEN 3 float equalities vs l236's stored homolog block")
o237["cert_237h"] = dict(n_checks=3, source="l236/static.json Q236_3_homolog",
                         mode="float equality (==)")

# ---------------- the 69 targets, annotated (DESCRIPTION) ------------------
_rows69 = []
for _j in range(_tc.size):
    _c = int(_tc[_j])
    _g = int(GI_OF_LOC[_c])
    _rows69.append(dict(
        local=_c, gi=_g, super_class=str(SUPG[_g]), cell_class=str(CLSG[_g]),
        cell_type=str(TYPG[_g]), side=str(SIDEG[_g]), region=str(REGG[_g]),
        u1=float(U1[_c]), u1_over_mean=float(U1[_c] / MU_U1),
        in_mass=float(IN_MASS[_c]), out_mass=float(OUT_MASS[_c]),
        in_deg=int(IN_DEG[_c]), out_deg=int(OUT_DEG[_c]),
        Q=(float(DT["Q"][_j]) if np.isfinite(DT["Q"][_j]) else None),
        align=(float(DT["align"][_j]) if np.isfinite(DT["align"][_j])
               else None)))
_tgt_cls = {}
for _r in _rows69:
    _k = f"{_r['super_class']}|{_r['cell_class']}"
    _tgt_cls[_k] = _tgt_cls.get(_k, 0) + 1
o237["targets_69"] = dict(
    n_distinct=int(_tc.size), rows=_rows69,
    class_counts=dict(sorted(_tgt_cls.items(), key=lambda kv: -kv[1])),
    median=dict(
        u1_over_mean=float(np.median([r["u1_over_mean"] for r in _rows69])),
        in_mass=float(np.median([r["in_mass"] for r in _rows69])),
        out_mass=float(np.median([r["out_mass"] for r in _rows69])),
        in_deg=float(np.median([r["in_deg"] for r in _rows69])),
        out_deg=float(np.median([r["out_deg"] for r in _rows69]))),
    menu_median=dict(
        u1_over_mean=float(np.median(UM / MU_U1)),
        in_mass=float(np.median(IN_MASS[MCELLS])),
        out_mass=float(np.median(OUT_MASS[MCELLS])),
        in_deg=float(np.median(IN_DEG[MCELLS])),
        out_deg=float(np.median(OUT_DEG[MCELLS]))),
    label="DESCRIPTION (the 69 were selected by the carrier's own wiring)")

# ---------------- the leverage leg (PREREG 0j: DESCRIPTION only) -----------
_Xb = MODELS["M2_plus_out_mass"]
_Ab = np.column_stack([np.ones(NM), _Xb])
_bb, *_ = np.linalg.lstsq(_Ab, Y, rcond=None)
_res = Y - _Ab @ _bb
_hi = np.argsort(-np.abs(_res))[:max(1, NM // 100)]
_hi_sup = {}
for _i in _hi.tolist():
    _k = str(SUPG[GI_OF_LOC[MCELLS[_i]]])
    _hi_sup[_k] = _hi_sup.get(_k, 0) + 1
o237["leverage_description"] = dict(
    model="M2_plus_out_mass, in-sample fit on midrank(u1)",
    n_top1pct=int(_hi.size),
    superclass_counts=dict(sorted(_hi_sup.items(), key=lambda kv: -kv[1])),
    menu_superclass_shares={CLASSES[_k]: float(SH_MENU[_k])
                            for _k in range(len(CLASSES))},
    median_abs_resid_top=float(np.median(np.abs(_res[_hi]))),
    median_abs_resid_all=float(np.median(np.abs(_res))),
    label=("DESCRIPTION: these cells were selected for being extreme on the "
           "model's own residual (Kriegeskorte 2009); no branch rests here"))

# ---------------- predictions (registered in l237/PREREG.md) ---------------
_P = {}
_P["P1"] = dict(registered="Q2 branch == NOT_IN_STRUCTURE (rho1 < 0.30)",
                measured=f"{BRANCH_Q2} (rho1 {RHO1:.6f})",
                correct=bool(BRANCH_Q2 == "NOT_IN_STRUCTURE"))
_P["P2"] = dict(registered="rho(M2) - rho(M1) >= 0.10",
                measured=f"{GAIN2:+.6f}", correct=bool(GAIN2 >= 0.10))
_P["P3"] = dict(registered="Q1 == C_BIASED (D_max p_perm < 0.05)",
                measured=f"{BRANCH_Q1} (p {P_DMAX:.5f})",
                correct=bool(BRANCH_Q1 == "C_BIASED"))
_P["P4"] = dict(registered="Q2b == M_RECURSES (share_Q >= 0.50)",
                measured=f"{BRANCH_Q2B} (share_Q {SH_Q:+.4f})",
                correct=bool(BRANCH_Q2B == "M_RECURSES"))
_P["P5"] = dict(registered="superclass adds < 0.05 held-out rho over M2",
                measured=f"{GAIN3:+.6f}", correct=bool(GAIN3 < 0.05))
_P["P6"] = dict(registered="menu u1 zero fraction in (0, 0.05)",
                measured=f"{FRAC_ZERO:.6f}",
                correct=bool(0.0 < FRAC_ZERO < 0.05))
N_OK = sum(1 for v in _P.values() if v["correct"])
log(f"[L237 predictions] {N_OK} of {len(_P)} correct: "
    + ", ".join(f"{k}={'T' if v['correct'] else 'F'}" for k, v in _P.items()))
o237["predictions"] = dict(n_correct=N_OK, n_total=len(_P), detail=_P)

o237["limitations"] = [
    "PREREG 0i, DECLARED UP FRONT: L233 asked the same 'does destination "
    "geometry explain it' question in the ARRIVAL currency on the BANC cord "
    "subnet and found in-mass a SUPPRESSOR. If this card also finds "
    "in-structure uninformative, that is ONE mechanism (the left Perron "
    "vector is an out-reach quantity by identity) and is NOT banked twice.",
    "The 69 targets were selected by the carrier's own wiring, so every "
    "69-vs-menu contrast whose null does not relocate the carrier's edges is "
    "DESCRIPTIVE (Kriegeskorte 2009). Q1's null does relocate them.",
    "Q2b's identity shares are exact but are a DECOMPOSITION, not a causal "
    "attribution: Q recursing into the targets' own targets does not say "
    "which anatomical fact makes that sub-population low-u1.",
    "The rank transform in Q2 is computed over the full population and "
    "shared across folds (PREREG 0d) — disclosed, not hidden.",
    "super_class labels are missing on part of the graph; unlabelled cells "
    "form their own level rather than being dropped.",
]
o237["certification_summary_l237"] = dict(
    cert_236a=o_cert236a["n_checks"], cert_236b=o_cert236b["n_checks"],
    cert_237d=o237["cert_237d"]["n_checks"],
    cert_237z=o237["cert_237z"]["n_checks"],
    cert_237h=o237["cert_237h"]["n_checks"],
    gate_ident_ulps=o237["Q2b_identity_shares"]["identity_ulps"],
    total_halting=int(o_cert236a["n_checks"] + o_cert236b["n_checks"]
                      + o237["cert_237d"]["n_checks"]
                      + o237["cert_237z"]["n_checks"]
                      + o237["cert_237h"]["n_checks"]),
    read_only_fingerprints_stable=all(
        (int(_os236.stat(_p).st_size), int(_os236.stat(_p).st_mtime_ns))
        == _FP236[_p] for _p in _RO236) and all(
        (int(_os236.stat(_p).st_size), int(_os236.stat(_p).st_mtime_ns))
        == _FP237[_p] for _p in _RO237))
assert o237["certification_summary_l237"]["read_only_fingerprints_stable"], \
    "a read-only artifact changed during the run (STOP)"

o237["banner_l237"] = "".join(
    open(__file__).read().splitlines(keepends=True)[:14])
o237["cert_236a"] = o_cert236a
o237["cert_236b"] = o_cert236b
o237["priors_readonly"] = dict(
    l236=_RO236, l237=_RO237,
    note="fingerprints asserted unchanged after the run")

_os236.makedirs("l237", exist_ok=True)
json.dump(o237, open("l237/static.json", "w"), indent=1)
log(f"[L237] DONE in {time.time() - t0:.1f}s -> l237/static.json | "
    f"Q1 {BRANCH_Q1} | Q2 {BRANCH_Q2} | Q2b {BRANCH_Q2B} | Q3 {BRANCH_Q3} | "
    f"{N_OK}/{len(_P)} predictions")
