# ================= L216 BODY (appended by l216_build.py) ==================
# Above this line, VERBATIM: l209_tail.py lines 34-226 (CERT-205 has already
# re-run as a free halting gate, the two substrates are built by the certified
# generic builder, OPS/LAMS carry the beta and Crofts operators with their
# lam1 by certified power iteration, and arrivals() is L209's own walk).
# This body adds ONLY: the depth 1..8 sweep, CERT-209, the Perron asymptote
# A_inf, the spectral gaps by L210's deflation, and the registered fits.
# RNG: the membership permutation null ONLY (seeded above, L205's stream),
# plus L210's own seed 21004 inside the verbatim lam2_defl.

# ---------------- NL swap so the verbatim mv/pi_dir/lam2_defl are generic ---
# L210's machinery reads the module-global NL (the f4wA node count) for its
# bincount minlength and its start vector. The functions are used VERBATIM;
# only the global they read is set around the call, and it is restored in a
# finally. Nothing inside the certified functions is modified.
_NL_F4 = NL


def _set_nl(n):
    global NL
    NL = int(n)


def pi_sub(s, jv, left=False):
    """Right (or left) Perron pair of the substrate operator, via CERT-PI."""
    _set_nl(s["n"])
    try:
        ls, ld = (s["rows"], s["cols"]) if left else (s["cols"], s["rows"])
        return pi_dir(jv, ls, ld)
    finally:
        _set_nl(_NL_F4)


def gap_sub(s, jv, v1, u1):
    """|lam2| by CERT-DEFL on the substrate operator."""
    _set_nl(s["n"])
    try:
        return lam2_defl(jv, s["cols"], s["rows"], v1, u1)
    finally:
        _set_nl(_NL_F4)


# ---------------- CERT-GAP (HALTING): L210's lam2/gap at FLOAT EQUALITY ----
_f210 = os.stat("l210/static.json")
S210 = json.load(open("l210/static.json"))
_LAMR, _VR, _INFR = pi_dir(jv_abs_an, csr_cols, csr_rows)
assert abs(_LAMR - LAM1) / LAM1 < 1e-12 and abs(abs(float(_VR @ V1)) - 1.0) < 1e-12, \
    "CERT-GAP right replay (STOP)"
_LAM1L, U1, _INFL = pi_dir(jv_abs_an, csr_rows, csr_cols)
assert _INFL["rel_spread_last6"] < 1e-6 and float(U1.min()) >= 0.0, \
    "CERT-GAP left iteration (STOP)"
LAM2_210, INF2_210 = lam2_defl(jv_abs_an, csr_cols, csr_rows, V1, U1)
_GAP210 = LAM2_210 / LAM1
_ngap = 0
for _f, _v in (("lam2_estimate", LAM2_210), ("gap", _GAP210), ("lam1", LAM1),
               ("rel_spread_last6", INF2_210["rel_spread_last6"])):
    assert _v == S210["Q210_4_gap"][_f], (_f, _v, S210["Q210_4_gap"][_f],
                                          "CERT-GAP (STOP)")
    _ngap += 1
for _i, _h in enumerate(INF2_210["last6"]):
    assert _h == S210["Q210_4_gap"]["last6"][_i], (_i, "CERT-GAP last6 (STOP)")
    _ngap += 1
log(f"[CERT-GAP] GREEN {_ngap} stored L210 values at FLOAT EQUALITY "
    f"(lam2 {LAM2_210:.9f}, gap {_GAP210:.10f}, 6 growth factors) -> the "
    f"deflation machinery, V1, the left vector and seed 21004 all certified")
o["cert_gap"] = dict(n_checks=_ngap, mode="float equality (==)",
                     source="l210/static.json Q210_4_gap",
                     lam2=LAM2_210, gap=_GAP210,
                     note="L210 ran this on the GAIN-SCALED operator; the "
                          "L216 beta operator is the same operator up to the "
                          "scalar g_f4wA and a spectral RATIO is invariant "
                          "to a global rescaling (L209's no-op law)")

# ---------------- the depth 1..3 table FIRST, for CERT-209 -----------------
_f209 = os.stat("l209/static.json")
S209 = json.load(open("l209/static.json"))
CELLS = [(sn, op, J) for sn in SUBS for op in ("beta", "crofts") for J in JOINTS]
assert len(CELLS) == 8, len(CELLS)

T3 = {}
for sname, s in SUBS.items():
    for op in ("beta", "crofts"):
        rn = arrivals(s, OPS[sname][op], DMAX_CERT, lam=LAMS[sname][op])
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            for d in range(1, DMAX_CERT + 1):
                real, nAc, nAt = side_stats_from(rn[d][lf], rn[d][le], J)
                T3[(sname, op, J, d)] = decorate(real, nAc, nAt)

_C209F = ("M_L", "M_R", "m_L", "m_R", "A_tot", "A_cell", "M_fL", "M_fR",
          "M_eL", "M_eR", "A_cell_pct_up", "A_cell_pct_abs", "A_tot_pct_up",
          "null_A_cell_mean", "null_A_cell_p05", "null_A_cell_p95",
          "null_A_cell_sd")
_n209 = 0
for (sname, op, J) in CELLS:
    for d in range(1, DMAX_CERT + 1):
        st = S209["table"][f"{sname}|{op}|{J}|d{d}"]
        for f in _C209F:
            assert T3[(sname, op, J, d)][f] == st[f], \
                (sname, op, J, d, f, "CERT-209 (STOP)")
            _n209 += 1
for sname in SUBS:
    for op in ("beta", "crofts"):
        assert LAMS[sname][op] == S209["substrates"][sname][f"lam1_{op}"], \
            (sname, op, "CERT-209 lam1 (STOP)")
        _n209 += 1
    assert SUBS[sname]["n"] == S209["substrates"][sname]["n"]
    assert SUBS[sname]["n_edges"] == S209["substrates"][sname]["n_edges"]
assert S209["branch"] == "D_NULL_RIGHTWARD", "L209 branch drifted (STOP)"
log(f"[CERT-209] GREEN {_n209} stored L209 values reproduced by FLOAT "
    f"EQUALITY (8 cells x 3 depths x 17 fields + 4 lam1) BEFORE any depth "
    f"> {DMAX_CERT} was read")
o["cert_209"] = dict(n_checks=_n209, mode="float equality (==)",
                     source="l209/static.json table + substrates",
                     depths_certified=list(range(1, DMAX_CERT + 1)),
                     n_cells=len(CELLS))

# ---------------- NOW the full depth 1..8 sweep ---------------------------
TABLE, NULLS = {}, {}
MAXREL = 0.0
for sname, s in SUBS.items():
    for op in ("beta", "crofts"):
        rn = arrivals(s, OPS[sname][op], DMAX, lam=LAMS[sname][op])
        ru = arrivals(s, OPS[sname][op], DMAX, lam=None)
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            for d in range(1, DMAX + 1):
                real, nAc, nAt = side_stats_from(rn[d][lf], rn[d][le], J)
                real = decorate(real, nAc, nAt)
                ru_real, _, _ = side_stats_from(ru[d][lf], ru[d][le], J)
                rel = abs(ru_real["A_cell"] - real["A_cell"]) / \
                    max(abs(real["A_cell"]), 1e-300)
                MAXREL = max(MAXREL, rel)
                real["A_cell_unnormalised"] = ru_real["A_cell"]
                real["A_cell_norm_rel_diff"] = float(rel)
                TABLE[(sname, op, J, d)] = real
                NULLS[(sname, op, J, d)] = nAc
assert MAXREL < 1e-10, (MAXREL, "lam1 normalisation NOT a no-op (STOP)")
log(f"[NO-OP] GREEN lam1^d normalisation is a measured no-op for A_cell at "
    f"all 8 depths (max rel diff {MAXREL:.2e} over {len(TABLE)} cells)")
for (sname, op, J) in CELLS:
    for d in range(1, DMAX_CERT + 1):
        assert TABLE[(sname, op, J, d)]["A_cell"] == T3[(sname, op, J, d)]["A_cell"], \
            (sname, op, J, d, "depth-8 sweep disagrees with the certified "
             "depth-3 sweep (STOP)")

# ---------------- A_inf: the Perron asymptote (PREMISE CORRECTION 0a) ------
PERRON, AINF = {}, {}
for sname, s in SUBS.items():
    for op in ("beta", "crofts"):
        lam_r, v1, inf_r = pi_sub(s, OPS[sname][op])
        lam_l, u1, inf_l = pi_sub(s, OPS[sname][op], left=True)
        assert inf_r["rel_spread_last6"] < 1e-6, (sname, op, "right PI (STOP)")
        assert inf_l["rel_spread_last6"] < 1e-6, (sname, op, "left PI (STOP)")
        assert abs(lam_r - LAMS[sname][op]) / LAMS[sname][op] < 1e-6, \
            (sname, op, lam_r, LAMS[sname][op], "PI lam1 disagreement (STOP)")
        # left/right lam1 agreement: a power iteration can only agree to its
        # OWN convergence level, so the bar is DERIVED from the two measured
        # rel spreads rather than fixed in advance (the Crofts operators have
        # spreads ~1e-8/4e-10 where the beta operators have ~1e-16).
        _spr = max(inf_r["rel_spread_last6"], inf_l["rel_spread_last6"])
        _lr_bar = max(1e-9, 1e3 * _spr)
        _lr_rel = abs(lam_l - lam_r) / lam_r
        log(f"[PI] {sname:6s} {op:6s}: lam1 R {lam_r:.9g} L {lam_l:.9g} "
            f"rel {_lr_rel:.2e} (bar {_lr_bar:.2e}, spreads R "
            f"{inf_r['rel_spread_last6']:.2e} L {inf_l['rel_spread_last6']:.2e})")
        assert _lr_rel < _lr_bar, (sname, op, _lr_rel, _lr_bar, "left lam1")
        assert float(v1.min()) >= -1e-14 and float(u1.min()) >= -1e-14, \
            (sname, op, "Perron vector not nonnegative (STOP)")
        v1 = np.abs(v1)
        u1 = np.abs(u1)
        PERRON[(sname, op)] = (lam_r, v1, u1, inf_r, inf_l)
        for J in JOINTS:
            lf, le = LOCAL[sname][(J, "f")], LOCAL[sname][(J, "e")]
            real, nAc, nAt = side_stats_from(v1[lf], v1[le], J)
            real = decorate(real, nAc, nAt)
            AINF[(sname, op, J)] = real
            log(f"[A_inf] {sname:6s} {op:6s} {J}: A_inf {real['A_cell']:+.6f} "
                f"pct_abs {real['A_cell_pct_abs']:.3f} "
                f"[null {real['null_A_cell_p05']:+.4f},"
                f"{real['null_A_cell_p95']:+.4f}]")

# ---------------- the spectral gaps -----------------------------------------
GAPS = {}
for sname, s in SUBS.items():
    for op in ("beta", "crofts"):
        lam1, v1, u1, _, _ = PERRON[(sname, op)]
        lam2, inf2 = gap_sub(s, OPS[sname][op], v1, u1)
        g = lam2 / lam1
        GAPS[(sname, op)] = dict(lam1=lam1, lam2=lam2, gap=g,
                                 rel_spread_last6=inf2["rel_spread_last6"],
                                 converged=bool(inf2["converged"]),
                                 last6=[float(x) for x in inf2["last6"]],
                                 gap_range=[float(min(inf2["last6"])) / lam1,
                                            float(max(inf2["last6"])) / lam1]
                                 if inf2["last6"] else None)
        log(f"[gap] {sname:6s} {op:6s}: lam1 {lam1:.6f} |lam2| {lam2:.6f} "
            f"gap {g:.6f} spread {inf2['rel_spread_last6']:.2e} "
            f"converged {inf2['converged']}")
# the f4wA beta gap must agree with L210's (same operator up to scale)
_gb = GAPS[("f4wA", "beta")]["gap"]
_rel210 = abs(_gb - _GAP210) / _GAP210
log(f"[gap] f4wA beta gap {_gb:.12f} vs L210's {_GAP210:.12f} "
    f"(rel {_rel210:.2e}) — scale invariance of a spectral ratio")


# ---------------- the registered fits ---------------------------------------
def fit_exp(ds, ys):
    """OLS of log(y) on d. Returns (r, c, rms_log_resid, n, min_y)."""
    ds = np.asarray(ds, float)
    ys = np.asarray(ys, float)
    if (ys <= 0).any() or (ys < 1e-300).any():
        return None, None, None, int(len(ds)), float(ys.min())
    L = np.log(ys)
    A = np.vstack([ds, np.ones_like(ds)]).T
    sol, *_ = np.linalg.lstsq(A, L, rcond=None)
    pred = A @ sol
    rms = float(np.sqrt(((L - pred) ** 2).mean()))
    return (float(np.exp(sol[0])), float(np.exp(sol[1])), rms,
            int(len(ds)), float(ys.min()))


FITS = {}
DEGEN = {}
for (sname, op, J) in CELLS:
    A = [TABLE[(sname, op, J, d)]["A_cell"] for d in range(1, DMAX + 1)]
    ainf = AINF[(sname, op, J)]["A_cell"]
    res = [a - ainf for a in A]
    absres = [abs(x) for x in res]
    # successive-difference ratios (A_inf cancels; the cheapest rate estimate)
    diffs = [A[i + 1] - A[i] for i in range(DMAX - 1)]
    rdiff = {}
    for i in range(1, DMAX - 1):
        rdiff[f"d{i+1}"] = (float(diffs[i] / diffs[i - 1])
                            if diffs[i - 1] != 0 else None)
    r_deep, c_deep, rms_deep, n_deep, miny = fit_exp(
        list(DEEP), [absres[d - 1] for d in DEEP])
    r_full, c_full, rms_full, _, _ = fit_exp(list(range(1, DMAX + 1)), absres)
    r_bare, c_bare, rms_bare, _, _ = fit_exp(list(range(1, DMAX + 1)),
                                             [abs(a) for a in A])
    gap = GAPS[(sname, op)]["gap"]
    degen = bool(miny < 1e-12 or r_deep is None
                 or not GAPS[(sname, op)]["converged"])
    DEGEN[(sname, op, J)] = degen
    FITS[(sname, op, J)] = dict(
        A=[float(x) for x in A], A_inf=float(ainf),
        resid=[float(x) for x in res],
        r_deep=r_deep, c_deep=c_deep, rms_log_resid_deep=rms_deep,
        r_full=r_full, rms_log_resid_full=rms_full,
        r_bare=r_bare, rms_log_resid_bare=rms_bare,
        r_diff=rdiff, gap=gap,
        ratio_deep_over_gap=(float(r_deep / gap) if r_deep else None),
        rel_err_vs_gap=(float(abs(r_deep - gap) / gap) if r_deep else None),
        within_10pct=(bool(abs(r_deep - gap) / gap <= GAP_BAR)
                      if r_deep else None),
        min_abs_resid_deep=miny, degenerate=degen,
        crosses_zero=bool(min(A) < 0 < max(A)),
        bare_ratios=[float(abs(A[i + 1] / A[i])) if A[i] != 0 else None
                     for i in range(DMAX - 1)])
    log(f"[fit] {sname:6s} {op:6s} {J}: A_inf {ainf:+.5f} r_deep "
        f"{r_deep if r_deep is None else round(r_deep, 6)} "
        f"(rms {rms_deep if rms_deep is None else round(rms_deep, 5)}) "
        f"r_full {r_full if r_full is None else round(r_full, 6)} "
        f"r_bare {r_bare if r_bare is None else round(r_bare, 6)} "
        f"(rms {rms_bare if rms_bare is None else round(rms_bare, 5)}) "
        f"gap {gap:.6f} rel {FITS[(sname,op,J)]['rel_err_vs_gap']} "
        f"degen {degen}")

# ---------------- BRANCH (primary cell only) --------------------------------
PRIMARY = ("f4wA", "beta", "Ti")
_pf = FITS[PRIMARY]
if DEGEN[PRIMARY]:
    BRANCH = "R_DEGENERATE"
elif _pf["rel_err_vs_gap"] <= GAP_BAR:
    BRANCH = "R_SPECTRAL"
elif ORDER_LO <= _pf["ratio_deep_over_gap"] <= ORDER_HI:
    BRANCH = "R_ORDER"
else:
    BRANCH = "R_OTHER"
_agree = sum(1 for k in CELLS if FITS[k]["within_10pct"])
_order = sum(1 for k in CELLS if FITS[k]["ratio_deep_over_gap"] is not None
             and ORDER_LO <= FITS[k]["ratio_deep_over_gap"] <= ORDER_HI)
log(f"[BRANCH] {BRANCH} | primary {PRIMARY}: r_deep {_pf['r_deep']:.6f} vs "
    f"gap {_pf['gap']:.6f} (rel {_pf['rel_err_vs_gap']:.4f}) | table "
    f"agreement {_agree}/8 within 10%, {_order}/8 within a factor 2")

# ---------------- predictions, scored ---------------------------------------
_p2 = AINF[("f4wA", "beta", "Tr")]["A_cell"]
_p3 = {sn: abs(GAPS[(sn, "crofts")]["gap"] - GAPS[(sn, "beta")]["gap"])
       / GAPS[(sn, "beta")]["gap"] for sn in SUBS}
_rc, _rf = FITS[("cutwA", "beta", "Ti")]["r_deep"], FITS[PRIMARY]["r_deep"]
_p4 = abs(_rc - _rf) / _rf if (_rc and _rf) else None
o["predictions"] = dict(
    P1=dict(registered="R_SPECTRAL", measured=BRANCH,
            correct=BRANCH == "R_SPECTRAL"),
    P2=dict(registered="A_inf(Tr,f4wA,beta) > +0.05 (nonzero asymptote "
                       "refutes the card's bare c*r^d)",
            measured=float(_p2), correct=bool(_p2 > 0.05)),
    P3=dict(registered="|gap_crofts - gap_beta|/gap_beta > 0.10 on at least "
                       "one substrate (the gap is operator-specific)",
            measured={k: float(v) for k, v in _p3.items()},
            correct=bool(any(v > 0.10 for v in _p3.values()))),
    P4=dict(registered="|r_deep(cutwA)-r_deep(f4wA)|/r_deep(f4wA) <= 0.05 "
                       "for beta/Ti",
            measured=(float(_p4) if _p4 is not None else None),
            correct=bool(_p4 is not None and _p4 <= 0.05)),
    P5=dict(registered="L210's lam2 26.94691005681583 and gap "
                       "0.8928793607351002 reproduced at FLOAT EQUALITY",
            measured=dict(lam2=LAM2_210, gap=_GAP210, n_checks=_ngap),
            correct=bool(LAM2_210 == S210["Q210_4_gap"]["lam2_estimate"]
                         and _GAP210 == S210["Q210_4_gap"]["gap"])))
o["n_predictions_correct"] = int(sum(1 for v in o["predictions"].values()
                                     if v["correct"]))

o["substrates"] = {k: dict(n=v["n"], n_edges=v["n_edges"],
                           lam1_beta=LAMS[k]["beta"],
                           lam1_crofts=LAMS[k]["crofts"]) for k, v in SUBS.items()}
o["table"] = {f"{sn}|{op}|{J}|d{d}": TABLE[(sn, op, J, d)]
              for (sn, op, J, d) in TABLE}
o["A_inf"] = {f"{sn}|{op}|{J}": AINF[(sn, op, J)] for (sn, op, J) in CELLS}
o["gaps"] = {f"{sn}|{op}": GAPS[(sn, op)] for (sn, op) in GAPS}
o["gap_f4wA_beta_vs_L210_rel"] = float(_rel210)
o["fits"] = {f"{sn}|{op}|{J}": FITS[(sn, op, J)] for (sn, op, J) in CELLS}
o["branch"] = BRANCH
o["primary"] = "|".join(PRIMARY)
o["table_agreement"] = dict(within_10pct=int(_agree), within_factor2=int(_order),
                            n_cells=len(CELLS))
o["norm_noop_max_rel_diff"] = MAXREL
o["bars"] = dict(gap_bar=GAP_BAR, order_lo=ORDER_LO, order_hi=ORDER_HI,
                 dmax=DMAX, deep_range=list(DEEP), ndraw=NDRAW,
                 seed=SEED_PERM, defl_seed=21004, defl_iters=400)
o["null"] = dict(kind="membership permutation (L45b/L70 handedness class), "
                      "L205's stream",
                 ndraw=NDRAW, seed=SEED_PERM,
                 note="used here only to give A_inf and every depth cell a "
                      "handedness percentile; the BRANCH rests on the "
                      "spectral comparison, not on this null")
o["limitations"] = [
    "ANATOMICAL leg only: wiring geometry, NOT an operating point (L164).",
    "Operator powers are walks WITH revisits, not paths; pool cells are "
    "themselves reachable so deeper arrivals include recurrent mass.",
    "r_d = A^d 1 is source-FREE (summed over all sources) — it is the "
    "depth-d generalisation of in-mass, not a per-actor reach.",
    "A_inf is read off the RIGHT Perron vector only; it is exact in the "
    "limit, so any disagreement with A_cell(8) is pre-asymptotic residue, "
    "not an error in A_inf.",
    "lam2 by real Hotelling deflation cannot represent a COMPLEX subdominant "
    "pair: non-convergence is reported with its range and routes the card to "
    "R_DEGENERATE, never to a number.",
    "The d=1..3 successive-difference ratios were derivable from "
    "l209/static.json before this card ran and are DESCRIPTION, not "
    "evidence (Kriegeskorte 2009; the PREREG states them in full).",
    "The Crofts leg is a different OPERATOR (per-edge reweighting), not a "
    "normalisation of the same one, and is scored as its own leg.",
    "No neuromere column exists on BANC, so no legblock tier is possible.",
]

# ---------------- prior artifacts untouched ---------------------------------
for _nm, _st0, _p in (("l209", _f209, "l209/static.json"),
                      ("l210", _f210, "l210/static.json")):
    _st1 = os.stat(_p)
    assert (_st0.st_size, _st0.st_mtime_ns) == (_st1.st_size, _st1.st_mtime_ns), \
        (_nm, "prior artifact CHANGED during the run (STOP)")
log("[read-only] l209/static.json and l210/static.json fingerprints unchanged")
o["pins"] = "ALL GREEN"

os.makedirs("l216", exist_ok=True)
json.dump(o, open("l216/static.json", "w"), indent=1, default=float)
log("=" * 72)
log(f"L216 DONE {time.time()-t0:.0f}s | BRANCH {BRANCH} | primary r_deep "
    f"{_pf['r_deep']:.6f} vs gap {_pf['gap']:.6f} | A_inf "
    f"{_pf['A_inf']:+.5f} | predictions {o['n_predictions_correct']}/5")
