# ================= L217 BODY (appended by l217_build.py) =================
# Above this line, VERBATIM: l209_tail.py 34-226 and l216_tail.py 1-204.
# By the time this body starts, CERT-205, CERT-GAP and CERT-209 have ALL
# already run as free halting gates, the lam1^d no-op has been re-measured at
# all 8 depths, TABLE/NULLS carry the beta and Crofts depth 1..8 sweep, AINF
# carries the Perron asymptotes and GAPS the spectral gaps.
# This body adds ONLY: CERT-216, the two random-walk operators, the crossing
# phase d_cross with its per-draw null, the three-operator sign table and the
# exact additive source decomposition.
# RNG: none beyond the membership permutation stream already seeded above and
# L210's seed 21004 inside the verbatim lam2_defl.

# ---------------- CERT-216 (HALTING): this card's required anchor ----------
_f216 = os.stat("l216/static.json")
S216 = json.load(open("l216/static.json"))
assert S216["branch"] == "R_SPECTRAL", "L216 branch drifted (STOP)"
assert S216["primary"] == "f4wA|beta|Ti", "L216 primary drifted (STOP)"
_A216F = ("M_L", "M_R", "m_L", "m_R", "A_tot", "A_cell", "M_fL", "M_fR",
          "M_eL", "M_eR", "A_cell_pct_up", "A_cell_pct_abs", "A_tot_pct_up",
          "null_A_cell_mean", "null_A_cell_p05", "null_A_cell_p95",
          "null_A_cell_sd")
_n216 = 0
for (sname, op, J) in CELLS:
    for d in range(1, DMAX + 1):
        assert TABLE[(sname, op, J, d)]["A_cell"] == \
            S216["table"][f"{sname}|{op}|{J}|d{d}"]["A_cell"], \
            (sname, op, J, d, "CERT-216 A_cell (STOP)")
        _n216 += 1
    for f in _A216F:
        assert AINF[(sname, op, J)][f] == S216["A_inf"][f"{sname}|{op}|{J}"][f], \
            (sname, op, J, f, "CERT-216 A_inf (STOP)")
        _n216 += 1
for (sname, op) in GAPS:
    for f in ("lam1", "lam2", "gap"):
        assert GAPS[(sname, op)][f] == S216["gaps"][f"{sname}|{op}"][f], \
            (sname, op, f, "CERT-216 gap (STOP)")
        _n216 += 1
log(f"[CERT-216] GREEN {_n216} stored L216 values reproduced by FLOAT "
    f"EQUALITY (8 cells x 8 depths of A_cell + 8 x 17 A_inf fields + 4 "
    f"operator-substrate pairs x 3 spectral fields) BEFORE any L217 number")
o["cert_216"] = dict(n_checks=_n216, mode="float equality (==)",
                     source="l216/static.json table + A_inf + gaps",
                     l216_branch=S216["branch"], l216_primary=S216["primary"])

# ---------------- the two random-walk operators (PREMISE CORRECTION 0a) ----
# rw    = beta / s_out(SOURCE)  -> column-stochastic, Seguin's T_pq = W_pq/s_p
# rw_in = beta / s_in(TARGET)   -> the card's literal form, row-stochastic
RWINFO = {}
PI_SPREAD = {}
PERRON_RESID = {}
PI_RESID_BAR = 1e-3   # derived below, in the Perron-residual block
for sname, s in SUBS.items():
    jv = s["jv"]
    s_out_l = np.zeros(s["n"])
    np.add.at(s_out_l, s["cols"], jv)
    s_in_l = np.zeros(s["n"])
    np.add.at(s_in_l, s["rows"], jv)
    jv_rw = jv / np.where(s_out_l > 0, s_out_l, 1.0)[s["cols"]]
    jv_rwin = jv / np.where(s_in_l > 0, s_in_l, 1.0)[s["rows"]]
    OPS[sname]["rw"] = jv_rw
    OPS[sname]["rw_in"] = jv_rwin
    # TOOLING FIX, disclosed (made after the PREREG, changes no registered
    # quantity): the inherited `spr < 1e-6` bar is calibrated to the BETA
    # operators, which converge to ~1e-16. The stochastic operators have
    # lam2/lam1 near 1 by construction (a random walk mixes slowly), so a
    # 400-iteration power iteration cannot reach that spread and the bar is
    # a statement about the iteration budget, not about the operator. Per
    # L216's law the bar is DERIVED from what the claim needs, and the
    # instrument is upgraded from a convergence PROXY to a direct PERRON
    # RESIDUAL ||A v - lam v|| / (lam ||v||), which certifies the eigenpair
    # itself. rw_in gets NO spectral assert at all: it is excluded from every
    # claim by PREREG amendment 0a-i, and its exact d=1 identity below is a
    # stronger certificate than any iteration.
    for op in ("rw", "rw_in"):
        lam, spr = power_iter_sub(s, OPS[sname][op])
        assert lam > 0, (sname, op, "power iteration gave lam1 <= 0 (STOP)")
        LAMS[sname][op] = lam
        PI_SPREAD[(sname, op)] = float(spr)
        log(f"[spectral] {sname} {op}: lam1 {lam:.9f} (rel spread {spr:.2e}"
            f"{'' if op == 'rw' else ' — NOT gated, excluded operator'})")
    # column-stochasticity of rw on out-positive nodes (exact by construction)
    _cs = np.zeros(s["n"])
    np.add.at(_cs, s["cols"], jv_rw)
    _pos_out = s_out_l > 0
    _cs_err = float(np.abs(_cs[_pos_out] - 1.0).max())
    assert _cs_err < 1e-12, (sname, _cs_err, "rw not column-stochastic (STOP)")
    RWINFO[sname] = dict(
        n_zero_out=int((~_pos_out).sum()), n_zero_in=int((s_in_l <= 0).sum()),
        col_stochastic_max_err=_cs_err, lam1_rw=LAMS[sname]["rw"],
        lam1_rw_in=LAMS[sname]["rw_in"])

# rw_in degeneracy probe: d=1 identity HALTING, d>=2 leakage MEASURED
DEGEN_RWIN = {}
for sname, s in SUBS.items():
    s_in_l = np.zeros(s["n"])
    np.add.at(s_in_l, s["rows"], s["jv"])
    pos_in = s_in_l > 0
    rn = arrivals(s, OPS[sname]["rw_in"], DMAX, lam=None)
    e1 = float(np.abs(rn[1][pos_in] - 1.0).max())
    assert e1 < 1e-10, (sname, e1, "rw_in d=1 identity BROKEN (STOP)")
    devs = {d: float(np.abs(rn[d][pos_in] - 1.0).max()) for d in range(1, DMAX + 1)}
    meandev = {d: float(np.abs(rn[d][pos_in] - 1.0).mean()) for d in range(1, DMAX + 1)}
    DEGEN_RWIN[sname] = dict(max_dev_from_one=devs, mean_dev_from_one=meandev,
                             n_pos_in=int(pos_in.sum()),
                             n_zero_in=int((~pos_in).sum()))
    log(f"[rw_in] {sname}: r_1 == 1 EXACT on {int(pos_in.sum())} in-positive "
        f"nodes (max dev {e1:.2e}); d>=2 leakage via {int((~pos_in).sum())} "
        f"zero-in-degree nodes, max dev d8 {devs[DMAX]:.3e}")
o["rw_in_degeneracy"] = dict(
    verdict="DEGENERATE AT d=1 BY THEOREM, EXCLUDED FROM THE SIGN TABLE",
    per_substrate=DEGEN_RWIN,
    note="A/s_in(target) is ROW-stochastic under A[dst,src], so r_1 = A 1 = 1 "
         "identically on every in-mass-positive node and the readout r_d = "
         "A^d 1 carries no wiring asymmetry at d=1. At d>=2 the deviation "
         "from 1 is leakage through zero-in-degree sources, i.e. a statement "
         "about which nodes are pure sources, not about handedness. Excluded "
         "unconditionally per PREREG amendment 0a-i.")

# ---------------- the rw depth 1..8 sweep (into TABLE/NULLS) ---------------
CELLS3 = [(sn, op, J) for sn in SUBS for op in OPS3 for J in JOINTS]
assert len(CELLS3) == 12, len(CELLS3)
_maxrel_rw = 0.0
for sname, s in SUBS.items():
    rn = arrivals(s, OPS[sname]["rw"], DMAX, lam=LAMS[sname]["rw"])
    ru = arrivals(s, OPS[sname]["rw"], DMAX, lam=None)
    for J in JOINTS:
        lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
        for d in range(1, DMAX + 1):
            real, nAc, nAt = side_stats_from(rn[d][lf], rn[d][le], J)
            real = decorate(real, nAc, nAt)
            ru_real, _, _ = side_stats_from(ru[d][lf], ru[d][le], J)
            rel = abs(ru_real["A_cell"] - real["A_cell"]) / \
                max(abs(real["A_cell"]), 1e-300)
            _maxrel_rw = max(_maxrel_rw, rel)
            real["A_cell_unnormalised"] = ru_real["A_cell"]
            real["A_cell_norm_rel_diff"] = float(rel)
            TABLE[(sname, "rw", J, d)] = real
            NULLS[(sname, "rw", J, d)] = nAc
assert _maxrel_rw < 1e-10, (_maxrel_rw, "rw lam1^d NOT a no-op (STOP)")
log(f"[NO-OP] GREEN lam1^d is a measured no-op for the rw operator too "
    f"(max rel {_maxrel_rw:.2e})")

# ---------------- rw Perron asymptotes -------------------------------------
# The rw operator is (near-)stochastic, so lam1 ~ 1 and the subdominant
# eigenvalue sits right beneath it: a 400-iteration power iteration CANNOT
# resolve its Perron vector, and the residual gate below is what says so.
# Budget is ESCALATED until the eigenpair certificate clears, and if it never
# does the leg is marked UNRESOLVED and carries no claim (it is NOT reported
# as a number). pi_dir is used VERBATIM; only its iteration budget moves.
RW_BUDGETS = (400, 3200, 25600, 102400)
RW_RESOLVED, RW_BUDGET_USED = {}, {}


def _rw_perron(s, jv, iters, left=False):
    _set_nl(s["n"])
    try:
        ls, ld = (s["rows"], s["cols"]) if left else (s["cols"], s["rows"])
        return pi_dir(jv, ls, ld, iters=iters)
    finally:
        _set_nl(_NL_F4)


def _resid(s, jv, lam, v, left=False):
    ls, ld = (s["rows"], s["cols"]) if left else (s["cols"], s["rows"])
    y = np.zeros(s["n"])
    np.add.at(y, ld, jv * v[ls])
    return float(np.linalg.norm(y - lam * v) / (lam * np.linalg.norm(v)))


for sname, s in SUBS.items():
    jvrw = OPS[sname]["rw"]
    best = None
    for nit in RW_BUDGETS:
        lam_r, v1, inf_r = _rw_perron(s, jvrw, nit)
        lam_l, u1, inf_l = _rw_perron(s, jvrw, nit, left=True)
        rr = _resid(s, jvrw, lam_r, v1)
        ru = _resid(s, jvrw, lam_l, u1, left=True)
        best = (nit, lam_r, v1, inf_r, lam_l, u1, inf_l, rr, ru)
        log(f"[rw-PI] {sname:6s} iters {nit:6d}: lam1 R {lam_r:.9f} "
            f"L {lam_l:.9f} | residual R {rr:.3e} L {ru:.3e} "
            f"(bar {PI_RESID_BAR:.0e})")
        if rr < PI_RESID_BAR and ru < PI_RESID_BAR:
            break
    nit, lam_r, v1, inf_r, lam_l, u1, inf_l, rr, ru = best
    RW_BUDGET_USED[sname] = int(nit)
    RW_RESOLVED[sname] = bool(rr < PI_RESID_BAR and ru < PI_RESID_BAR)
    PI_SPREAD[(sname, "rw_pi_right")] = float(inf_r["rel_spread_last6"])
    PI_SPREAD[(sname, "rw_pi_left")] = float(inf_l["rel_spread_last6"])
    assert float(v1.min()) >= -1e-14 and float(u1.min()) >= -1e-14, \
        (sname, "rw Perron vector not nonnegative (STOP)")
    v1 = np.abs(v1)
    u1 = np.abs(u1)
    LAMS[sname]["rw"] = lam_r
    PERRON[(sname, "rw")] = (lam_r, v1, u1, inf_r, inf_l)
    lam2, inf2 = gap_sub(s, jvrw, v1, u1)
    GAPS[(sname, "rw")] = dict(lam1=lam_r, lam2=lam2, gap=lam2 / lam_r,
                               rel_spread_last6=inf2["rel_spread_last6"],
                               converged=bool(inf2["converged"]),
                               last6=[float(x) for x in inf2["last6"]])
    for J in JOINTS:
        lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
        real, nAc, nAt = side_stats_from(v1[lf], v1[le], J)
        AINF[(sname, "rw", J)] = decorate(real, nAc, nAt)
        AINF[(sname, "rw", J)]["resolved"] = RW_RESOLVED[sname]
        log(f"[A_inf] {sname:6s} rw     {J}: A_inf {real['A_cell']:+.6f} "
            f"pct_abs {real['A_cell_pct_abs']:.3f} "
            f"resolved {RW_RESOLVED[sname]} (budget {nit})")
o["rw_perron_resolution"] = {
    sn: dict(resolved=RW_RESOLVED[sn], iters=RW_BUDGET_USED[sn],
             budgets_tried=list(RW_BUDGETS))
    for sn in SUBS}

# ---------------- PERRON RESIDUAL gate (the upgraded instrument) ----------
# A convergence SPREAD is a proxy; the residual ||A v - lam v|| / (lam ||v||)
# certifies the eigenpair itself. Computed for every operator that enters a
# claim, with the beta/Crofts values printed as the calibration reference the
# bar is read off. The bar is DERIVED, not inherited: A_inf is a ratio of
# sums of v1 entries, so a relative eigenvector error eps perturbs A_inf by
# O(eps); the claims here are sign + a 0.95 percentile against nulls whose
# half-width is ~0.05-0.12, so 1e-3 is three orders of margin.
for (sname, op) in sorted(PERRON.keys()):
    lam1, v1, u1, _, _ = PERRON[(sname, op)]
    s = SUBS[sname]
    jv = OPS[sname][op]
    av = np.zeros(s["n"])
    np.add.at(av, s["rows"], jv * v1[s["cols"]])
    rr = float(np.linalg.norm(av - lam1 * v1) / (lam1 * np.linalg.norm(v1)))
    au = np.zeros(s["n"])
    np.add.at(au, s["cols"], jv * u1[s["rows"]])
    ru = float(np.linalg.norm(au - lam1 * u1) / (lam1 * np.linalg.norm(u1)))
    ok = bool(rr < PI_RESID_BAR and ru < PI_RESID_BAR)
    PERRON_RESID[(sname, op)] = dict(right=rr, left=ru, passes=ok)
    log(f"[resid] {sname:6s} {op:6s}: Perron residual right {rr:.3e} "
        f"left {ru:.3e} (bar {PI_RESID_BAR:.0e}) -> "
        f"{'RESOLVED' if ok else 'UNRESOLVED'}")
    if op in ("beta", "crofts"):
        assert ok, (sname, op, rr, ru,
                    "a CERTIFIED L216 operator failed the residual (STOP)")
    else:
        assert ok == RW_RESOLVED[sname], (sname, "resolution flag drift (STOP)")
o["perron_residual"] = {f"{sn}|{op}": PERRON_RESID[(sn, op)]
                        for (sn, op) in PERRON_RESID}
o["pi_spread"] = {f"{sn}|{op}": v for (sn, op), v in PI_SPREAD.items()}

# ---------------- Q2: d_cross, defined in the PREREG -----------------------
def dcross(series):
    """LAST sign change in A_cell(1..DMAX), linearly interpolated.
    Returns (d_cross or None, n_sign_changes)."""
    a = np.asarray(series, float)
    last, nch = None, 0
    for i in range(len(a) - 1):
        if a[i] * a[i + 1] < 0:
            nch += 1
            last = i
    if last is None:
        return None, nch
    lo, hi = abs(a[last]), abs(a[last + 1])
    return float((last + 1) + lo / (lo + hi)), nch


DX = {}
for (sname, op, J) in CELLS3:
    A = [TABLE[(sname, op, J, d)]["A_cell"] for d in range(1, DMAX + 1)]
    dc, nch = dcross(A)
    NM = np.column_stack([NULLS[(sname, op, J, d)] for d in range(1, DMAX + 1)])
    assert NM.shape == (NDRAW, DMAX), NM.shape
    ndc = np.full(NDRAW, np.nan)
    for j in range(NDRAW):
        v, _ = dcross(NM[j])
        if v is not None:
            ndc[j] = v
    ok = ~np.isnan(ndc)
    DX[(sname, op, J)] = dict(
        A=[float(x) for x in A], d_cross=dc, n_sign_changes=int(nch),
        censored=bool(dc is None),
        sign_first=int(np.sign(A[0])), sign_last=int(np.sign(A[-1])),
        A_inf=float(AINF[(sname, op, J)]["A_cell"]),
        A_inf_pct_abs=float(AINF[(sname, op, J)]["A_cell_pct_abs"]),
        pre_asymptotic_residue=float(abs(A[-1] - AINF[(sname, op, J)]["A_cell"])),
        null_frac_cross=float(ok.mean()),
        null_d_cross_mean=(float(ndc[ok].mean()) if ok.any() else None),
        null_d_cross_p05=(float(np.percentile(ndc[ok], 5)) if ok.any() else None),
        null_d_cross_p95=(float(np.percentile(ndc[ok], 95)) if ok.any() else None),
        description=bool(op in ("beta", "crofts") and sname == "f4wA")
        or bool(op == "beta" and sname == "cutwA"))
    DX[(sname, op, J)]["_null_vec"] = ndc
    log(f"[d_cross] {sname:6s} {op:6s} {J}: d_cross "
        f"{'CENSORED' if dc is None else round(dc, 4)} "
        f"(changes {nch}) | null crosses {ok.mean():.3f} of draws, "
        f"mean {DX[(sname,op,J)]['null_d_cross_mean']}")

# ---------------- Q1 PRIMARY: the Ti-minus-Tr crossing gap vs its null -----
PRIMARY_SUB, PRIMARY_OP = "f4wA", "beta"
_ti = DX[(PRIMARY_SUB, PRIMARY_OP, "Ti")]
_tr = DX[(PRIMARY_SUB, PRIMARY_OP, "Tr")]
_nti, _ntr = _ti["_null_vec"], _tr["_null_vec"]
_both = (~np.isnan(_nti)) & (~np.isnan(_ntr))
_frac_both = float(_both.mean())
if _ti["d_cross"] is None or _tr["d_cross"] is None \
        or _frac_both < NULL_CROSS_FRAC_BAR:
    Q1_BRANCH = "PHASE_DEGENERATE"
    D_real, pct_abs_D = None, None
else:
    D_real = float(_ti["d_cross"] - _tr["d_cross"])
    Dn = _nti[_both] - _ntr[_both]
    pct_abs_D = float((np.abs(Dn) <= abs(D_real)).mean())
    if abs(D_real) >= D_SEP_BAR and pct_abs_D >= PCT_HI:
        Q1_BRANCH = "PHASE_SEPARATED"
    else:
        Q1_BRANCH = "PHASE_NULL"
_Dn_stats = None
if D_real is not None:
    Dn = _nti[_both] - _ntr[_both]
    _Dn_stats = dict(mean=float(Dn.mean()), sd=float(Dn.std()),
                     p05=float(np.percentile(Dn, 5)),
                     p95=float(np.percentile(Dn, 95)),
                     max_abs=float(np.abs(Dn).max()))
o["Q1_crossing_phase"] = dict(
    branch=Q1_BRANCH, substrate=PRIMARY_SUB, operator=PRIMARY_OP,
    d_cross_Ti=_ti["d_cross"], d_cross_Tr=_tr["d_cross"], D_real=D_real,
    pct_abs=pct_abs_D, bar_pct=PCT_HI, bar_D=D_SEP_BAR,
    null_frac_both_cross=_frac_both, null_D=_Dn_stats, n_draws=NDRAW,
    note="the d_cross POINT ESTIMATES on beta/crofts are observed-derivable "
         "from l216/static.json and are DESCRIPTION (PREREG 0b); the NULL "
         "for D, and therefore this branch, is the registered inferential "
         "object and had never been computed on any card.")
log(f"[Q1] {Q1_BRANCH} | d_cross Ti {_ti['d_cross']} Tr {_tr['d_cross']} "
    f"D {D_real} pct_abs {pct_abs_D} (null both-cross {_frac_both:.3f})")

# ---------------- Q2: the three-operator SIGN table ------------------------
SIGNTAB = {}
for sname in SUBS:
    for J in JOINTS:
        row = {}
        for op in OPS3:
            a = AINF[(sname, op, J)]
            row[op] = dict(A_inf=float(a["A_cell"]),
                           sign=int(np.sign(a["A_cell"])),
                           pct_abs=float(a["A_cell_pct_abs"]),
                           passes=bool(a["A_cell_pct_abs"] >= PCT_HI))
        signs = {row[op]["sign"] for op in OPS3}
        npass = sum(1 for op in OPS3 if row[op]["passes"])
        if not RW_RESOLVED[sname]:
            shape = "THIRD_LEG_UNRESOLVED"
        elif len(signs) == 1 and npass == 3:
            shape = "ALL_THREE_AGREE"
        elif npass == 0:
            shape = "ALL_THREE_INSIDE"
        else:
            shape = "SPLIT"
        row["shape"] = shape
        row["n_pass"] = npass
        row["rw_resolved"] = bool(RW_RESOLVED[sname])
        row["signs_agree"] = bool(len(signs) == 1)
        # the two-operator (certified) sub-table, always readable
        _s2 = {row[op]["sign"] for op in ("beta", "crofts")}
        _n2 = sum(1 for op in ("beta", "crofts") if row[op]["passes"])
        row["shape_certified_pair"] = (
            "BOTH_AGREE" if (len(_s2) == 1 and _n2 == 2)
            else "BOTH_INSIDE" if _n2 == 0 else "SPLIT")
        SIGNTAB[(sname, J)] = row
        log(f"[sign] {sname:6s} {J}: {shape:17s} n_pass {npass} | "
            + " ".join(f"{op} {row[op]['A_inf']:+.5f}"
                       f"({row[op]['pct_abs']:.3f})" for op in OPS3))
# the same table at d=2 and d=3 (the L209 object)
SIGND = {}
for sname in SUBS:
    for J in JOINTS:
        for d in (2, 3):
            row = {}
            for op in OPS3:
                t = TABLE[(sname, op, J, d)]
                row[op] = dict(A_cell=float(t["A_cell"]),
                               sign=int(np.sign(t["A_cell"])),
                               pct_abs=float(t["A_cell_pct_abs"]),
                               passes=bool(t["A_cell_pct_abs"] >= PCT_HI))
            signs = {row[op]["sign"] for op in OPS3}
            npass = sum(1 for op in OPS3 if row[op]["passes"])
            row["shape"] = ("ALL_THREE_AGREE" if (len(signs) == 1 and npass == 3)
                            else "ALL_THREE_INSIDE" if npass == 0 else "SPLIT")
            row["signs_agree"] = bool(len(signs) == 1)
            SIGND[(sname, J, d)] = row

# ---------------- Q3: the EXACT additive source decomposition --------------
sup_glob = np.full(Nall, "", dtype=object)
sup_glob[ann_gi] = sup
eff_glob = np.where(is_glut, -1.0, np.sign(sign_all))


def arrivals_from(s, jv, dmax, x0, lam=None):
    """r_d = A^d x0 — the certified arrivals() generalised to an arbitrary
    seed vector. Certified below against arrivals() at FLOAT EQUALITY for
    x0 = 1 (L44: certify the generic against the certified specialisation)."""
    v = jv if lam is None else jv / lam
    x = np.asarray(x0, float).copy()
    out = {}
    for d in range(1, dmax + 1):
        y = np.zeros(s["n"])
        np.add.at(y, s["rows"], v * x[s["cols"]])
        x = y
        out[d] = x.copy()
    return out


_cg = 0
for sname, s in SUBS.items():
    _a = arrivals(s, OPS[sname]["beta"], DMAX, lam=LAMS[sname]["beta"])
    _b = arrivals_from(s, OPS[sname]["beta"], DMAX, np.ones(s["n"]),
                       lam=LAMS[sname]["beta"])
    for d in range(1, DMAX + 1):
        assert np.array_equal(_a[d], _b[d]), (sname, d, "CERT-SEED (STOP)")
        _cg += 1
log(f"[CERT-SEED] GREEN {_cg} depth vectors: arrivals_from(x0=1) is "
    f"ARRAY-IDENTICAL to the certified arrivals() on both substrates")
o["cert_seed"] = dict(n_checks=_cg, mode="np.array_equal")

PARTS = {}
for sname, s in SUBS.items():
    gl = np.where(s["keep"])[0]          # global id of each local node
    assert len(gl) == s["n"], (sname, "keep->local map (STOP)")
    sc = np.array([sup_glob[g] if sup_glob[g] in
                   ("sensory", "ventral_nerve_cord_intrinsic", "motor",
                    "descending") else "other" for g in gl], dtype=object)
    ef = eff_glob[gl]
    nt = np.where(ef > 0, "E", np.where(ef < 0, "I", "U")).astype(object)
    cd = np.where(cord_mask[gl], "cord", "noncord").astype(object)
    PARTS[sname] = dict(super_class=sc, nt_sign=nt, cord=cd)

DECOMP = {}
ADD_MAXREL = 0.0
for sname, s in SUBS.items():
    for pname, labels in PARTS[sname].items():
        keys = sorted(set(labels.tolist()))
        tot = {d: np.zeros(s["n"]) for d in DEC_DEPTHS}
        per = {}
        for k in keys:
            x0 = (labels == k).astype(float)
            rn = arrivals_from(s, OPS[sname]["beta"], DMAX, x0,
                               lam=LAMS[sname]["beta"])
            per[k] = {d: rn[d] for d in DEC_DEPTHS}
            for d in DEC_DEPTHS:
                tot[d] += rn[d]
        ref = arrivals(s, OPS[sname]["beta"], DMAX, lam=LAMS[sname]["beta"])
        for d in DEC_DEPTHS:
            den = np.maximum(np.abs(ref[d]), 1e-300)
            rel = float((np.abs(tot[d] - ref[d]) / den).max())
            ADD_MAXREL = max(ADD_MAXREL, rel)
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            cf, isLf = GROUPS[(J, "f")]
            ce, isLe = GROUPS[(J, "e")]
            nL = int(isLf.sum() + isLe.sum())
            nR = (len(cf) - int(isLf.sum())) + (len(ce) - int(isLe.sum()))
            for d in DEC_DEPTHS:
                rows = {}
                dsum = 0.0
                for k in keys:
                    mf, me = per[k][d][lf], per[k][d][le]
                    ML = float(mf[isLf].sum() + me[isLe].sum())
                    MR = float(mf[~isLf].sum() + me[~isLe].sum())
                    dc_g = ML / nL - MR / nR
                    dsum += dc_g
                    rows[k] = dict(M_L=ML, M_R=MR, dcell=dc_g,
                                   A_cell_group=(asym(ML / nL, MR / nR)
                                                 if (ML + MR) > 0 else None),
                                   mass_share=None)
                mtot = sum(rows[k]["M_L"] + rows[k]["M_R"] for k in keys)
                for k in keys:
                    rows[k]["share_of_drift"] = (float(rows[k]["dcell"] / dsum)
                                                 if dsum != 0 else None)
                    rows[k]["mass_share"] = (float((rows[k]["M_L"]
                                                    + rows[k]["M_R"]) / mtot)
                                             if mtot else None)
                DECOMP[(sname, pname, J, d)] = dict(
                    groups=rows, dcell_total=float(dsum),
                    A_cell_total=float(TABLE[(sname, "beta", J, d)]["A_cell"]))
assert ADD_MAXREL < 1e-10, (ADD_MAXREL, "source decomposition NOT additive (STOP)")
log(f"[ADDITIVITY] GREEN sum_g A^d 1_g == A^d 1 at every decomposed depth "
    f"and every partition (max rel {ADD_MAXREL:.2e})")

# ---------------- Q4: does the drift survive source = cord only? -----------
Q4 = {}
for J in JOINTS:
    row = DECOMP[("f4wA", "cord", J, 8)]["groups"]["cord"]
    allA = TABLE[("f4wA", "beta", J, 8)]["A_cell"]
    Q4[J] = dict(A_cell_cord=row["A_cell_group"], A_cell_all=float(allA),
                 sign_match=bool(row["A_cell_group"] is not None
                                 and np.sign(row["A_cell_group"]) == np.sign(allA)),
                 mag_ratio=(float(abs(row["A_cell_group"]) / abs(allA))
                            if row["A_cell_group"] is not None and allA != 0
                            else None),
                 share_of_drift=row["share_of_drift"],
                 mass_share=row["mass_share"])
_sm = all(Q4[J]["sign_match"] for J in JOINTS)
_mg = all(Q4[J]["mag_ratio"] is not None and Q4[J]["mag_ratio"] >= CORD_FRAC_BAR
          for J in JOINTS)
Q4_BRANCH = "CORD_CARRIES" if (_sm and _mg) else \
            "CORD_PARTIAL" if _sm else "CORD_FAILS"
o["Q4_cord_restriction"] = dict(branch=Q4_BRANCH, per_joint=Q4,
                                bar_mag_ratio=CORD_FRAC_BAR, depth=8,
                                substrate="f4wA", operator="beta")
log(f"[Q4] {Q4_BRANCH} | " + " | ".join(
    f"{J} cord {Q4[J]['A_cell_cord']:+.5f} vs all {Q4[J]['A_cell_all']:+.5f} "
    f"(ratio {Q4[J]['mag_ratio']})" for J in JOINTS))

# ---------------- predictions, scored --------------------------------------
_p2_signs = {J: (int(np.sign(AINF[("f4wA", "rw", J)]["A_cell"]))
                 == int(np.sign(AINF[("f4wA", "beta", J)]["A_cell"])))
             for J in JOINTS}
_p2_valid = bool(RW_RESOLVED["f4wA"])
_p3_split = [f"{sn}|{J}" for sn in SUBS for J in JOINTS
             if SIGNTAB[(sn, J)]["shape"] == "SPLIT"]
_p3_split_cert = [f"{sn}|{J}" for sn in SUBS for J in JOINTS
                  if SIGNTAB[(sn, J)]["shape_certified_pair"] == "SPLIT"]
_p4_cord = DECOMP[("f4wA", "cord", "Ti", 2)]["groups"]["cord"]["share_of_drift"]
o["predictions"] = dict(
    P1=dict(registered="Q1 lands on PHASE_SEPARATED", measured=Q1_BRANCH,
            correct=Q1_BRANCH == "PHASE_SEPARATED"),
    P2=dict(registered="A_inf(rw) has the SAME SIGN as A_inf(beta) on f4wA "
                       "for both joints",
            measured={J: dict(rw=float(AINF[("f4wA", "rw", J)]["A_cell"]),
                              beta=float(AINF[("f4wA", "beta", J)]["A_cell"]),
                              same_sign=bool(_p2_signs[J])) for J in JOINTS},
            rw_resolved=_p2_valid,
            correct=bool(_p2_valid and all(_p2_signs.values())),
            note=("SCOREABLE" if _p2_valid else
                  "UNSCOREABLE: the f4wA rw Perron vector did not clear the "
                  "eigenpair residual at any budget tried, so its A_inf is "
                  "not a number this card is entitled to read. Scored FALSE "
                  "by the registered rule, reported as an instrument "
                  "failure, NOT as a sign disagreement.")),
    P3=dict(registered="Q2 lands on SPLIT for at least one of the four "
                       "substrate x joint cells",
            measured=_p3_split, measured_certified_pair=_p3_split_cert,
            correct=bool(len(_p3_split) >= 1)),
    P4=dict(registered="the CORD group carries > 50% of dcell at d=2 on "
                       "f4wA beta Ti",
            measured=(float(_p4_cord) if _p4_cord is not None else None),
            correct=bool(_p4_cord is not None and _p4_cord > 0.5)),
    P5=dict(registered="Q4 lands on CORD_CARRIES", measured=Q4_BRANCH,
            correct=Q4_BRANCH == "CORD_CARRIES"))
o["n_predictions_correct"] = int(sum(1 for v in o["predictions"].values()
                                     if v["correct"]))

# ---------------- output ----------------------------------------------------
o["substrates"] = {k: dict(n=v["n"], n_edges=v["n_edges"],
                           lam1_beta=LAMS[k]["beta"],
                           lam1_crofts=LAMS[k]["crofts"],
                           lam1_rw=LAMS[k]["rw"],
                           lam1_rw_in=LAMS[k]["rw_in"]) for k, v in SUBS.items()}
o["rw_info"] = RWINFO
o["d_cross"] = {f"{sn}|{op}|{J}": {k: v for k, v in DX[(sn, op, J)].items()
                                   if not k.startswith("_")}
                for (sn, op, J) in CELLS3}
o["sign_table_A_inf"] = {f"{sn}|{J}": SIGNTAB[(sn, J)]
                         for (sn, J) in SIGNTAB}
o["sign_table_depth"] = {f"{sn}|{J}|d{d}": SIGND[(sn, J, d)]
                         for (sn, J, d) in SIGND}
o["A_inf_rw"] = {f"{sn}|rw|{J}": AINF[(sn, "rw", J)] for sn in SUBS
                 for J in JOINTS}
o["gaps_rw"] = {f"{sn}|rw": GAPS[(sn, "rw")] for sn in SUBS}
o["table_rw"] = {f"{sn}|rw|{J}|d{d}": TABLE[(sn, "rw", J, d)] for sn in SUBS
                 for J in JOINTS for d in range(1, DMAX + 1)}
o["decomposition"] = {f"{sn}|{pn}|{J}|d{d}": DECOMP[(sn, pn, J, d)]
                      for (sn, pn, J, d) in DECOMP}
o["additivity_max_rel"] = float(ADD_MAXREL)
o["branch"] = Q1_BRANCH
o["branch_Q4"] = Q4_BRANCH
o["bars"] = dict(pct_hi=PCT_HI, d_sep_bar=D_SEP_BAR,
                 null_cross_frac_bar=NULL_CROSS_FRAC_BAR,
                 cord_frac_bar=CORD_FRAC_BAR, dmax=DMAX, ndraw=NDRAW,
                 seed=SEED_PERM, dec_depths=list(DEC_DEPTHS),
                 operators=list(OPS3), excluded_operator="rw_in")
o["limitations"] = [
    "ANATOMICAL leg only: wiring geometry, NOT an operating point (L164).",
    "Operator powers are walks WITH revisits, not paths.",
    "r_d = A^d 1 is source-FREE in the undecomposed legs — the depth-d "
    "generalisation of in-mass, not a per-actor reach.",
    "The d_cross point estimates for beta and Crofts were derivable from "
    "l216/static.json before this card ran and are DESCRIPTION "
    "(Kriegeskorte 2009; PREREG 0b states all six series in full). The "
    "NULL for the Ti-minus-Tr gap, the entire rw leg, the source "
    "decomposition and the cord restriction are the unobserved objects.",
    "The source decomposition attributes a walk to its ORIGIN, not to its "
    "last hop: a cord-origin walk may traverse descending cells.",
    "rw normalises by out-strength and therefore DOWN-weights hub sources by "
    "construction — a sign agreement with beta is informative, a magnitude "
    "comparison between operators is not.",
    "d=8 is a near-asymptotic probe, not the asymptote; the pre-asymptotic "
    "residue |A_cell(8) - A_inf| is reported for every cell.",
    "rw_in is excluded unconditionally (PREREG amendment 0a-i), not because "
    "it measured badly.",
    "super_class labels come from the BANC annotation table; a root id "
    "appearing twice resolves to its last row, and unlabelled nodes fall in "
    "the 'other' group rather than being dropped.",
    "No neuromere column exists on BANC, so no legblock tier is possible.",
]

# ---------------- prior artifacts untouched ---------------------------------
for _nm, _st0, _p in (("l209", _f209, "l209/static.json"),
                      ("l210", _f210, "l210/static.json"),
                      ("l216", _f216, "l216/static.json")):
    _st1 = os.stat(_p)
    assert (_st0.st_size, _st0.st_mtime_ns) == (_st1.st_size, _st1.st_mtime_ns), \
        (_nm, "prior artifact CHANGED during the run (STOP)")
log("[read-only] l209/l210/l216 static.json fingerprints unchanged")
o["pins"] = "ALL GREEN"

os.makedirs("l217", exist_ok=True)
json.dump(o, open("l217/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L217 DONE {time.time()-t0:.0f}s | Q1 {Q1_BRANCH} | Q4 {Q4_BRANCH} | "
    f"predictions {o['n_predictions_correct']}/5")
