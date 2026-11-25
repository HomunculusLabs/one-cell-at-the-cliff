# ================= L230 BODY (appended by l230_build.py) ==================
# Above this line, VERBATIM:
#   SLICE A = l216_static.py lines 1-1360 (a literal PREFIX of the parent,
#     cut immediately BEFORE its writer; AST-verified to hold ZERO write
#     sites), so every pin plus CERT-F4, CERT-178, CERT-GEN, CERT-205,
#     CERT-GAP, CERT-209 and the NO-OP re-run as the code that actually
#     produced l216/static.json, and TABLE / NULLS / AINF / PERRON / GAPS /
#     FITS / CELLS are in memory.
#   SLICE B = l217_tail.py lines 245-258 (L217's `dcross` function), so the
#     crossing depth is measured by the EXPRESSION that produced
#     l217/static.json, not by a re-implementation (L206/L211).
# This body adds ONLY: CERT-216, CERT-217, CERT-AINF, the closed-form
# crossing phase with its exact additive attribution, and the per-draw
# closed-form null. No new RNG: the permutation draws are the prefix's
# (seed 20526), re-used.

_T230 = time.time()
log("=" * 72)
log("[L230] the CROSSING-PHASE law | closed form d_cross = log(-A_inf/K)/"
    "log(rho) | PREREG l230/PREREG.md")

P = dict(
    design="L230 the CROSSING-PHASE law. L216's two-term model A_cell(d) = "
           "A_inf + K rho^d gives a closed form for the depth at which a "
           "pool cell's L/R asymmetry changes sign: d_cross = "
           "log(-A_inf/K)/log(rho). Q1/Q2 attribute the Ti-vs-Tr phase "
           "difference to A_inf vs the depth-1 overlap K by an EXACT log "
           "identity (DESCRIPTION, PREREG 0a). Q3 is the inferential leg: "
           "the closed form's own membership-permutation null, which exists "
           "on far more draws than the measured crossing L217 could not "
           "score.",
    prereg="l230/PREREG.md")
P["inherited_certs"] = {k: o[k] for k in
                        ("cert_f4", "cert_178", "cert_gen", "cert_205",
                         "cert_gap", "cert_209", "gain_invariance",
                         "csr_orientation", "pools", "gains")}
P["norm_noop_max_rel_diff"] = MAXREL

EPS = float(np.finfo(float).eps)
RESFLOOR = 1.0 / (NDRAW + 1)


def leafcmp(got, want, path, n):
    """Recursive leaf compare at FLOAT EQUALITY with artifact-derived
    coverage: the WANT structure dictates every key and every leaf."""
    if isinstance(want, dict):
        assert isinstance(got, dict), (path, "want dict got", type(got))
        assert set(got.keys()) == set(want.keys()), \
            (path, sorted(set(got) ^ set(want)), "key set (STOP)")
        for k in sorted(want):
            n = leafcmp(got[k], want[k], f"{path}/{k}", n)
        return n
    if isinstance(want, list):
        assert isinstance(got, (list, tuple)) and len(got) == len(want), \
            (path, "length (STOP)")
        for i in range(len(want)):
            n = leafcmp(got[i], want[i], f"{path}[{i}]", n)
        return n
    if want is None:
        assert got is None, (path, got, "want None (STOP)")
        return n + 1
    if isinstance(want, bool):
        assert isinstance(got, (bool, np.bool_)) and bool(got) == want, \
            (path, got, want, "bool (STOP)")
        return n + 1
    assert float(got) == float(want), (path, repr(got), repr(want),
                                       "FLOAT EQUALITY (STOP)")
    return n + 1


def leaves(want):
    """Leaf count of a stored structure — the coverage bar DERIVED FROM THE
    ARTIFACT, never hand-typed (L224: a hand-typed bar halted L229)."""
    if isinstance(want, dict):
        return sum(leaves(v) for v in want.values())
    if isinstance(want, list):
        return sum(leaves(v) for v in want)
    return 1


# ---------------- CERT-216 (HALTING): l216/static.json at FLOAT EQUALITY ---
_f216 = os.stat("l216/static.json")
S216 = json.load(open("l216/static.json"))

# the parent's OWN expressions (l216_tail.py lines 318-323), verbatim
_got_table = {f"{sn}|{op}|{J}|d{d}": TABLE[(sn, op, J, d)]
              for (sn, op, J, d) in TABLE}
_got_ainf = {f"{sn}|{op}|{J}": AINF[(sn, op, J)] for (sn, op, J) in CELLS}
_got_gaps = {f"{sn}|{op}": GAPS[(sn, op)] for (sn, op) in GAPS}
_got_fits = {f"{sn}|{op}|{J}": FITS[(sn, op, J)] for (sn, op, J) in CELLS}

_n216 = 0
_bar216 = 0
for _nm, _got in (("table", _got_table), ("A_inf", _got_ainf),
                  ("gaps", _got_gaps), ("fits", _got_fits)):
    _n216 = leafcmp(_got, S216[_nm], _nm, _n216)
    _bar216 += leaves(S216[_nm])
assert _n216 == _bar216, (_n216, _bar216, "CERT-216 coverage (STOP)")
assert len(S216["table"]) == 64 and len(S216["A_inf"]) == 8 \
    and len(S216["gaps"]) == 4 and len(S216["fits"]) == 8, "CERT-216 shape"
assert MAXREL == S216["norm_noop_max_rel_diff"], \
    (MAXREL, S216["norm_noop_max_rel_diff"], "CERT-216 no-op (STOP)")
assert S216["branch"] == "R_SPECTRAL" and S216["primary"] == "f4wA|beta|Ti", \
    "L216 branch/primary drifted (STOP)"
_n216 += 3
log(f"[CERT-216] GREEN {_n216} stored L216 values reproduced at FLOAT "
    f"EQUALITY (table 64 depth cells + A_inf 8 + gaps 4 + fits 8; coverage "
    f"bar {_bar216} DERIVED from the artifact's own leaves) BEFORE any "
    f"crossing was read")
P["cert_216"] = dict(n_checks=_n216, coverage_bar_derived=_bar216,
                     mode="float equality (==)",
                     source="l216/static.json table + A_inf + gaps + fits",
                     l216_branch=S216["branch"], l216_primary=S216["primary"])

# the NO-OP, re-asserted explicitly (the card's Verify line)
_nnoop = 0
for (sn, op, J, d) in TABLE:
    _st = S216["table"][f"{sn}|{op}|{J}|d{d}"]
    assert TABLE[(sn, op, J, d)]["A_cell_unnormalised"] == \
        _st["A_cell_unnormalised"], (sn, op, J, d, "no-op unnorm (STOP)")
    assert TABLE[(sn, op, J, d)]["A_cell_norm_rel_diff"] == \
        _st["A_cell_norm_rel_diff"], (sn, op, J, d, "no-op rel (STOP)")
    _nnoop += 2
assert MAXREL < 1e-10
log(f"[NO-OP] RE-ASSERTED GREEN {_nnoop} checks over {len(TABLE)} depth "
    f"cells, max rel diff {MAXREL:.2e} == L216's stored value")
P["noop"] = dict(n_checks=_nnoop, max_rel_diff=MAXREL,
                 equals_l216_stored=True)

# ---------------- CERT-AINF (HALTING): the per-draw A_inf null -------------
# The A_inf null vector is not stored anywhere; it is obtained by calling the
# CERTIFIED side_stats_from on the stored Perron vector, and the call is
# GATED by asserting it reproduces every stored A_inf field (percentiles
# included) at float equality — which proves the vector belongs to the same
# draw stream that produced those percentiles.
AINF_NULL = {}
_nainf = 0
for sname in SUBS:
    for op in ("beta", "crofts"):
        _v1 = PERRON[(sname, op)][1]
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            _real, _nAc, _nAt = side_stats_from(_v1[lf], _v1[le], J)
            _real = decorate(_real, _nAc, _nAt)
            _nainf = leafcmp(_real, S216["A_inf"][f"{sname}|{op}|{J}"],
                             f"A_inf/{sname}|{op}|{J}", _nainf)
            assert _nAc.shape == (NDRAW,), (sname, op, J, _nAc.shape)
            AINF_NULL[(sname, op, J)] = np.asarray(_nAc, float)
log(f"[CERT-AINF] GREEN {_nainf} float equalities — the per-draw A_inf null "
    f"({NDRAW} draws x 8 cells) comes from the same certified call that "
    f"reproduces every stored A_inf percentile")
P["cert_ainf"] = dict(n_checks=_nainf, ndraw=NDRAW, n_cells=8,
                      mode="float equality (==)")

# ---------------- CERT-217 (HALTING): L217's measured crossings ------------
_f217 = os.stat("l217/static.json")
S217 = json.load(open("l217/static.json"))
DX = {}
DXNULL = {}
_got_dx = {}
for (sname, op, J) in CELLS:
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
    rec = dict(
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
    DX[(sname, op, J)] = rec
    DXNULL[(sname, op, J)] = ndc
    _got_dx[f"{sname}|{op}|{J}"] = rec

_want_dx = {k: v for k, v in S217["d_cross"].items() if k in _got_dx}
assert len(_want_dx) == 8, (len(_want_dx), "CERT-217 cell coverage (STOP)")
_n217 = leafcmp(_got_dx, _want_dx, "d_cross", 0)
assert _n217 == leaves(_want_dx), (_n217, "CERT-217 coverage (STOP)")
_L217_RATE = S217["Q1_crossing_phase"]["null_frac_both_cross"]
assert S217["Q1_crossing_phase"]["branch"] == "PHASE_DEGENERATE" \
    and S217["Q1_crossing_phase"]["D_real"] is None \
    and S217["Q1_crossing_phase"]["n_draws"] == NDRAW, \
    "L217 Q1 drifted (STOP)"
assert S217["Q1_crossing_phase"]["d_cross_Ti"] == \
    _got_dx["f4wA|beta|Ti"]["d_cross"] \
    and S217["Q1_crossing_phase"]["d_cross_Tr"] == \
    _got_dx["f4wA|beta|Tr"]["d_cross"], "L217 Q1 d_cross drifted (STOP)"
_n217 += 6
log(f"[CERT-217] GREEN {_n217} stored L217 values reproduced at FLOAT "
    f"EQUALITY on the 8 beta/crofts cells (d_cross, sign changes, censoring, "
    f"null crossing rate and its three percentiles) via L217's VERBATIM "
    f"dcross — the crossing expression AND this run's draw stream certified")
P["cert_217"] = dict(n_checks=_n217, coverage_bar_derived=leaves(_want_dx),
                     mode="float equality (==)",
                     source="l217/static.json d_cross + Q1_crossing_phase",
                     l217_q1_branch=S217["Q1_crossing_phase"]["branch"],
                     l217_null_frac_both_cross=_L217_RATE)

# ---------------- Q1/Q2: the closed form (DESCRIPTION, PREREG 0a) ---------
LOGRHO = {}
CF = {}
for sname in SUBS:
    for op in ("beta", "crofts"):
        rho = GAPS[(sname, op)]["gap"]
        assert 0.0 < rho < 1.0, (sname, op, rho, "rho outside (0,1) (STOP)")
        LOGRHO[(sname, op)] = float(np.log(rho))
        for J in JOINTS:
            ainf = float(AINF[(sname, op, J)]["A_cell"])
            A1 = float(TABLE[(sname, op, J, 1)]["A_cell"])
            K = (A1 - ainf) / rho
            arg = (-ainf / K) if K != 0.0 else float("nan")
            defined = bool(K != 0.0 and np.isfinite(arg) and arg > 0.0)
            d_cf = (float(np.log(arg) / np.log(rho)) if defined else None)
            # the SPLIT-LOG form, which is what makes the attribution exact.
            # PREREG AMENDMENT 0h-i (disclosed, pre-outcome): the PREREG
            # wrote this as [ln(-A_inf) - ln|K|]/ln(rho), which is a
            # NOTATION SLIP — for a crossing cell A_inf > 0 and K < 0, so
            # the minus sign in -A_inf/K is carried entirely by K and the
            # split is [ln(A_inf) - ln|K|]/ln(rho). The slip produced
            # log(negative) = nan and this assert HALTED the run before any
            # Q1 number existed; repaired here, outcome untouched.
            d_split = (float((np.log(ainf) - np.log(abs(K))) / np.log(rho))
                       if (defined and ainf > 0.0 and K < 0.0) else None)
            if d_split is not None:
                _bar = 16.0 * EPS * (abs(np.log(ainf)) + abs(np.log(abs(K)))
                                     + abs(d_cf * np.log(rho))) \
                    / abs(np.log(rho))
                assert abs(d_split - d_cf) <= _bar, \
                    (sname, op, J, d_split, d_cf, _bar,
                     "closed-form split-log identity (STOP)")
            # the stored deep-fit companion currency (PREREG 0f)
            _fit = FITS[(sname, op, J)]
            _sgn = 1.0 if _fit["resid"][0] > 0 else -1.0
            K_fit = (_sgn * _fit["c_deep"] if _fit["c_deep"] else None)
            r_deep = _fit["r_deep"]
            arg_f = ((-ainf / K_fit) if (K_fit not in (None, 0.0)) else None)
            d_cf_fit = (float(np.log(arg_f) / np.log(r_deep))
                        if (arg_f is not None and arg_f > 0.0 and r_deep
                            and 0.0 < r_deep < 1.0) else None)
            d_meas = DX[(sname, op, J)]["d_cross"]
            CF[(sname, op, J)] = dict(
                rho=float(rho), A_inf=ainf, A1=A1, K_anchor=float(K),
                sign_A_inf=int(np.sign(ainf)), sign_K=int(np.sign(K)),
                cf_arg=(float(arg) if np.isfinite(arg) else None),
                cf_defined=defined, d_cf=d_cf, d_cf_split_log=d_split,
                d_meas=d_meas, censored=DX[(sname, op, J)]["censored"],
                resid=(float(abs(d_cf - d_meas))
                       if (d_cf is not None and d_meas is not None) else None),
                resid_measurable=bool(d_cf is not None and d_meas is not None),
                K_fit=K_fit, r_deep=r_deep, d_cf_fit=d_cf_fit,
                resid_fit=(float(abs(d_cf_fit - d_meas))
                           if (d_cf_fit is not None and d_meas is not None)
                           else None),
                A_inf_pct_abs=float(AINF[(sname, op, J)]["A_cell_pct_abs"]))
            log(f"[cf] {sname:6s} {op:6s} {J}: A_inf {ainf:+.6f} K {K:+.6f} "
                f"rho {rho:.6f} | d_cf "
                f"{'UNDEFINED' if d_cf is None else round(d_cf, 4)} "
                f"d_meas {'CENSORED' if d_meas is None else round(d_meas, 4)} "
                f"resid {CF[(sname,op,J)]['resid']} | d_cf_fit "
                f"{None if d_cf_fit is None else round(d_cf_fit, 4)}")

_n_cf_def = sum(1 for k in CELLS if CF[k]["cf_defined"])
_n_meas = sum(1 for k in CELLS if CF[k]["d_meas"] is not None)
log(f"[cf] closed form DEFINED on {_n_cf_def}/8 cells, measured crossing "
    f"exists on {_n_meas}/8 — the currencies have DIFFERENT populations "
    f"(PREREG 0d/0e)")

# ---------------- the EXACT additive attribution --------------------------
PAIRS = [(sn, op) for sn in SUBS for op in ("beta", "crofts")]
ATTR = {}
for (sname, op) in PAIRS:
    a, b = CF[(sname, op, "Ti")], CF[(sname, op, "Tr")]
    lr = LOGRHO[(sname, op)]
    avail = bool(a["cf_defined"] and b["cf_defined"]
                 and a["A_inf"] > 0 and b["A_inf"] > 0
                 and a["K_anchor"] < 0 and b["K_anchor"] < 0)
    rec = dict(available=avail, rho=a["rho"],
               A_inf_Ti=a["A_inf"], A_inf_Tr=b["A_inf"],
               K_Ti=a["K_anchor"], K_Tr=b["K_anchor"],
               d_cf_Ti=a["d_cf"], d_cf_Tr=b["d_cf"],
               d_meas_Ti=a["d_meas"], d_meas_Tr=b["d_meas"])
    if avail:
        D_cf = float(a["d_cf"] - b["d_cf"])
        ratio_A = float(a["A_inf"] / b["A_inf"])
        ratio_K = float(abs(a["K_anchor"]) / abs(b["K_anchor"]))
        T_A = float(np.log(ratio_A) / lr)
        T_K = float(-np.log(ratio_K) / lr)
        _bar = 32.0 * EPS * (abs(T_A) + abs(T_K) + abs(D_cf)
                             + abs(a["d_cf"]) + abs(b["d_cf"]))
        assert abs((T_A + T_K) - D_cf) <= _bar, \
            (sname, op, T_A, T_K, D_cf, _bar, "additive identity (STOP)")
        share_K = float(abs(T_K) / (abs(T_A) + abs(T_K))) \
            if (abs(T_A) + abs(T_K)) > 0 else None
        rec.update(D_cf=D_cf, T_A=T_A, T_K=T_K, share_K=share_K,
                   ratio_A_inf=ratio_A, ratio_K=ratio_K,
                   A_inf_within_2x=bool(0.5 <= ratio_A <= 2.0),
                   identity_abs_err=float(abs((T_A + T_K) - D_cf)),
                   identity_bar=float(_bar),
                   D_meas=(float(a["d_meas"] - b["d_meas"])
                           if (a["d_meas"] is not None
                               and b["d_meas"] is not None) else None),
                   resid_max=(max(a["resid"], b["resid"])
                              if (a["resid"] is not None
                                  and b["resid"] is not None) else None),
                   resid_measurable_both=bool(a["resid"] is not None
                                              and b["resid"] is not None))
        log(f"[attr] {sname:6s} {op:6s}: D_cf {D_cf:+.4f} = T_A {T_A:+.4f} + "
            f"T_K {T_K:+.4f} (err {rec['identity_abs_err']:.2e}) | share_K "
            f"{share_K:.4f} | A_inf ratio {ratio_A:.4f} within2x "
            f"{rec['A_inf_within_2x']} | D_meas {rec['D_meas']} resid_max "
            f"{rec['resid_max']}")
    else:
        rec.update(D_cf=None, T_A=None, T_K=None, share_K=None,
                   ratio_A_inf=None, ratio_K=None, A_inf_within_2x=None,
                   D_meas=None, resid_max=None, resid_measurable_both=False,
                   reason="closed form undefined on at least one joint "
                          "(PREREG 0d: cutwA|crofts|Ti has a NEGATIVE "
                          "asymptote, same sign as K, so the model says it "
                          "never crosses)")
        log(f"[attr] {sname:6s} {op:6s}: UNAVAILABLE — {rec['reason']}")
    ATTR[(sname, op)] = rec

# ---------------- Q1 BRANCH (PRIMARY pair, PRIMARY currency) --------------
PRI_SUB, PRI_OP = "f4wA", "beta"
_pa = ATTR[(PRI_SUB, PRI_OP)]
assert _pa["available"], "PRIMARY pair closed form unavailable (STOP)"
RESID_BAR, SHARE_HI, SHARE_LO = 0.5, 2.0 / 3.0, 1.0 / 3.0
if not _pa["resid_measurable_both"]:
    Q1_BRANCH = "PHASE_MODEL_INSUFFICIENT"
    Q1_WHY = "a primary joint's measured crossing is CENSORED — the residual " \
             "gate is FALSE BY UNMEASURABILITY (PREREG 0e)"
elif _pa["resid_max"] > RESID_BAR:
    Q1_BRANCH = "PHASE_MODEL_INSUFFICIENT"
    Q1_WHY = f"max residual {_pa['resid_max']:.4f} hops > {RESID_BAR}"
elif _pa["share_K"] >= SHARE_HI and _pa["A_inf_within_2x"]:
    Q1_BRANCH = "PHASE_FROM_K"
    Q1_WHY = f"share_K {_pa['share_K']:.4f} >= 2/3 with the asymptote " \
             f"ratio {_pa['ratio_A_inf']:.4f} inside [0.5, 2]"
elif _pa["share_K"] >= SHARE_HI:
    Q1_BRANCH = "PHASE_FROM_K_DESPITE_AINF"
    Q1_WHY = f"share_K {_pa['share_K']:.4f} >= 2/3 but the asymptote ratio " \
             f"{_pa['ratio_A_inf']:.4f} is outside [0.5, 2]"
elif _pa["share_K"] <= SHARE_LO:
    Q1_BRANCH = "PHASE_FROM_AINF"
    Q1_WHY = f"share_K {_pa['share_K']:.4f} <= 1/3: the phase difference is " \
             f"carried by the ASYMPTOTE, not by the depth-1 drive"
else:
    Q1_BRANCH = "PHASE_MIXED"
    Q1_WHY = f"share_K {_pa['share_K']:.4f} in (1/3, 2/3)"
log(f"[Q1] {Q1_BRANCH} | {Q1_WHY}")

# ---------------- Q3: the closed form's OWN null (the inferential leg) ----
def cf_null(sname, op, J):
    rho = GAPS[(sname, op)]["gap"]
    ainf_n = AINF_NULL[(sname, op, J)]
    A1_n = np.asarray(NULLS[(sname, op, J, 1)], float)
    assert ainf_n.shape == A1_n.shape == (NDRAW,), (sname, op, J, "shape")
    K_n = (A1_n - ainf_n) / rho
    with np.errstate(divide="ignore", invalid="ignore"):
        arg_n = -ainf_n / K_n
        ok = np.isfinite(arg_n) & (arg_n > 0.0) & (K_n != 0.0)
        d_n = np.where(ok, np.log(np.where(ok, arg_n, 1.0)) / np.log(rho),
                       np.nan)
    return ainf_n, K_n, ok, d_n


_na, _Ka, _oka, _dna = cf_null(PRI_SUB, PRI_OP, "Ti")
_nb, _Kb, _okb, _dnb = cf_null(PRI_SUB, PRI_OP, "Tr")
_both = _oka & _okb
_rate_joint = float(_both.mean())
_rate_Ti, _rate_Tr = float(_oka.mean()), float(_okb.mean())
log(f"[Q3 existence] closed form defined in Ti {_rate_Ti:.4f} / Tr "
    f"{_rate_Tr:.4f} / BOTH {_rate_joint:.4f} of {NDRAW} draws "
    f"(L217's measured-crossing joint rate was {_L217_RATE:.4f}; resolution "
    f"floor {RESFLOOR:.6f})")

CF_BAR_RATE, CF_BAR_PCT = 0.50, 0.95
_D_cf = _pa["D_cf"]
_Dn = (_dna - _dnb)[_both]
_med = lambda v: (float(np.median(v)) if v.size else None)
if _rate_joint < CF_BAR_RATE:
    Q3_BRANCH = "CF_NULL_DEGENERATE"
    _pct_D = None
    Q3_WHY = (f"the closed form exists in only {_rate_joint:.4f} of draws "
              f"(< {CF_BAR_RATE}) — percentile WITHHELD, not approximated "
              f"(L229); this is an INSTRUMENT verdict")
else:
    _pct_D = float((np.abs(_Dn) <= abs(_D_cf)).mean())
    Q3_BRANCH = ("CF_SEPARATED" if _pct_D >= CF_BAR_PCT
                 else "CF_NOT_SEPARATED")
    Q3_WHY = (f"|D_cf| {abs(_D_cf):.4f} at pct_abs {_pct_D:.4f} against "
              f"{int(_both.sum())} defined draws (bar {CF_BAR_PCT})")
log(f"[Q3] {Q3_BRANCH} | {Q3_WHY}")

# share_K's own null (P6)
with np.errstate(divide="ignore", invalid="ignore"):
    _rA = _na / _nb
    _okA = _both & np.isfinite(_rA) & (_rA > 0.0) & (_Ka != 0.0) & (_Kb != 0.0)
    _TAn = np.where(_okA, np.log(np.where(_okA, _rA, 1.0))
                    / LOGRHO[(PRI_SUB, PRI_OP)], np.nan)
    _rK = np.abs(_Ka) / np.abs(_Kb)
    _TKn = np.where(_okA, -np.log(np.where(_okA, _rK, 1.0))
                    / LOGRHO[(PRI_SUB, PRI_OP)], np.nan)
    _den = np.abs(_TAn) + np.abs(_TKn)
    _okS = _okA & np.isfinite(_den) & (_den > 0)
    _shn = np.where(_okS, np.abs(_TKn) / np.where(_okS, _den, 1.0), np.nan)
_sh_ok = _shn[_okS]
_pct_sh = (float((_sh_ok <= _pa["share_K"]).mean()) if _sh_ok.size else None)
log(f"[Q3 share_K] real {_pa['share_K']:.4f} at pct_up "
    f"{_pct_sh} against {_sh_ok.size} defined draws (null median "
    f"{_med(_sh_ok)})")

P["cf_cells"] = {f"{sn}|{op}|{J}": CF[(sn, op, J)] for (sn, op, J) in CELLS}
P["attribution"] = {f"{sn}|{op}": ATTR[(sn, op)] for (sn, op) in PAIRS}
P["Q1"] = dict(branch=Q1_BRANCH, why=Q1_WHY, primary=f"{PRI_SUB}|{PRI_OP}",
               currency="K_anchor = (A(1)-A_inf)/rho, rho = |lam2|/lam1",
               description=True,
               resid_bar=RESID_BAR, share_hi=SHARE_HI, share_lo=SHARE_LO,
               n_cf_defined=_n_cf_def, n_measured=_n_meas)
P["Q3"] = dict(
    branch=Q3_BRANCH, why=Q3_WHY, primary=f"{PRI_SUB}|{PRI_OP}",
    rate_Ti=_rate_Ti, rate_Tr=_rate_Tr, rate_joint=_rate_joint,
    n_defined_joint=int(_both.sum()), bar_rate=CF_BAR_RATE,
    bar_pct=CF_BAR_PCT, D_cf=_D_cf, pct_abs_D=_pct_D,
    null_D_median=_med(_Dn), null_D_p05=(float(np.percentile(_Dn, 5))
                                         if _Dn.size else None),
    null_D_p95=(float(np.percentile(_Dn, 95)) if _Dn.size else None),
    null_D_iqr=([float(np.percentile(_Dn, 25)), float(np.percentile(_Dn, 75))]
                if _Dn.size else None),
    null_d_cf_Ti_median=_med(_dna[_oka]), null_d_cf_Tr_median=_med(_dnb[_okb]),
    share_K=_pa["share_K"], pct_up_share_K=_pct_sh,
    n_defined_share=int(_sh_ok.size), null_share_K_median=_med(_sh_ok),
    l217_measured_joint_rate=_L217_RATE,
    resolution_floor=RESFLOOR, ndraw=NDRAW, seed=SEED_PERM,
    note="NO MOMENT of the null d_cf is reported: d_cf -> +-inf as K -> 0, so "
         "every read is a rate or a percentile and the null's spread is "
         "given as median/IQR (PREREG 0i).")

# ---------------- predictions, scored -------------------------------------
P["predictions"] = dict(
    P1=dict(registered="Q1 branch == PHASE_FROM_AINF",
            kind="DESCRIPTION (PREREG 0a: observed-derivable)",
            measured=Q1_BRANCH, correct=bool(Q1_BRANCH == "PHASE_FROM_AINF")),
    P2=dict(registered="|d_cf - d_meas| <= 0.5 hops on BOTH primary joints",
            kind="DESCRIPTION (PREREG 0a)",
            measured=_pa["resid_max"],
            correct=bool(_pa["resid_measurable_both"]
                         and _pa["resid_max"] <= RESID_BAR)),
    P3=dict(registered="closed-form JOINT existence rate in the null >= 0.50",
            kind="blind", measured=_rate_joint,
            correct=bool(_rate_joint >= CF_BAR_RATE)),
    P4=dict(registered="that rate >= 2x L217's measured-crossing joint rate "
                       "0.0505", kind="blind",
            measured=dict(rate_joint=_rate_joint, l217=_L217_RATE,
                          ratio=float(_rate_joint / _L217_RATE)),
            correct=bool(_rate_joint >= 2.0 * _L217_RATE)),
    P5=dict(registered="Q3 branch == CF_SEPARATED", kind="blind",
            measured=Q3_BRANCH, correct=bool(Q3_BRANCH == "CF_SEPARATED")),
    P6=dict(registered="real primary share_K NOT extreme: pct_up <= 0.95",
            kind="blind", measured=_pct_sh,
            correct=bool(_pct_sh is not None and _pct_sh <= 0.95)))
P["n_predictions_correct"] = int(sum(1 for v in P["predictions"].values()
                                     if v["correct"]))
P["branch"] = Q1_BRANCH
P["branch_Q3"] = Q3_BRANCH
P["bars"] = dict(resid_bar=RESID_BAR, share_hi=SHARE_HI, share_lo=SHARE_LO,
                 cf_bar_rate=CF_BAR_RATE, cf_bar_pct=CF_BAR_PCT,
                 dmax=DMAX, ndraw=NDRAW, seed=SEED_PERM,
                 resolution_floor=RESFLOOR)
P["limitations"] = [
    "ANATOMICAL leg only: wiring geometry, NOT an operating point (L164).",
    "Q1 and Q2 are DESCRIPTION: every input to the closed form is stored in "
    "l216/static.json and the measured crossing in l217/static.json, so the "
    "attribution is arithmetic on stored values and the registration buys a "
    "DECISION RULE only (PREREG 0a; L214; Kriegeskorte 2009). Q3 is the only "
    "inferential object on this card.",
    "L217 already owns the MEASURED-crossing null and found it degenerate "
    "(null_frac_both_cross 0.0505); L230 does not re-pose that contrast, it "
    "re-poses it in the closed-form currency.",
    "The closed form and the measurement have DIFFERENT populations: the "
    "closed form is defined on 7 of 8 cells (it predicts a crossing beyond "
    "d=8 for f4wA|crofts|Ti, which the sweep censors) and undefined on "
    "cutwA|crofts|Ti, whose asymptote is negative.",
    "A censored cell has no residual, so its model-adequacy leg is FALSE BY "
    "UNMEASURABILITY, never a small residual (L222).",
    "K has two currencies (depth-1 anchor with the shared spectral gap; the "
    "stored deep fit with the cell's own r_deep). The branch rests on the "
    "anchor, which is the card's own wording; the fit companion is reported "
    "and is NOT interchangeable, since it gives the two joints different "
    "rates and breaks the shared-rho premise (L218/L227/L229).",
    "d_cf is heavy-tailed in the null (d_cf -> +-inf as K -> 0): no moment of "
    "that distribution is admissible, so every read is a rate or a "
    "percentile with median/IQR for spread.",
    "The null is a membership permutation inside the handedness class: it "
    "relocates L/R labels over the same pool cells with per-side counts held "
    "exact. It cannot speak to pool MEMBERSHIP or to any L/R asymmetry in "
    "reconstruction completeness.",
    "The two-term model carries ONE rho per substrate x operator; a "
    "genuinely two-mode residual appears as a residual failure, which is why "
    "PHASE_MODEL_INSUFFICIENT is registered FIRST.",
    "No neuromere column exists on BANC, so no legblock tier is possible.",
]

# ---------------- prior artifacts untouched -------------------------------
for _nm, _st0, _p in (("l205", os.stat("l205/static.json"), "l205/static.json"),
                      ("l209", _f209, "l209/static.json"),
                      ("l210", _f210, "l210/static.json"),
                      ("l216", _f216, "l216/static.json"),
                      ("l217", _f217, "l217/static.json")):
    _st1 = os.stat(_p)
    assert (_st0.st_size, _st0.st_mtime_ns) == (_st1.st_size, _st1.st_mtime_ns), \
        (_nm, "prior artifact CHANGED during the run (STOP)")
log("[read-only] l205/l209/l210/l216/l217 static.json fingerprints unchanged")
P["pins"] = "ALL GREEN"

os.makedirs("l230", exist_ok=True)
json.dump(P, open("l230/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L230 DONE {time.time()-_T230:.0f}s (total {time.time()-t0:.0f}s) | Q1 "
    f"{Q1_BRANCH} | Q3 {Q3_BRANCH} | share_K {_pa['share_K']:.4f} | cf "
    f"joint existence {_rate_joint:.4f} vs L217 {_L217_RATE:.4f} | "
    f"predictions {P['n_predictions_correct']}/6")
