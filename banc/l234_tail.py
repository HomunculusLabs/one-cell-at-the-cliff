# ================= L234 TAIL (appended by l234_build.py) =================
# Everything above this line is SLICE A = l218_static.py lines 1-1691
# VERBATIM: a literal PREFIX of the generated parent, cut immediately before
# L218's own predictions/writer block, so every gate L218 ran re-runs here as
# the code that ACTUALLY produced l218/static.json (CERT-218T 1224 and
# CERT-W50 1010 among them) while the parent's json.dump is excluded by
# construction. Nothing below re-transcribes a certified def (L85) and no lab
# module is imported (L175: a lab run script is a SCRIPT, never a library).
# PREREG: l234/PREREG.md (registered first). Writes l234/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics.

_T234 = _time.time()


def _e234(tag):
    log(f"[time-234] {tag}: {_time.time() - _T234:.1f}s")


_e234("SLICE A complete (L218's whole measurement block re-run)")

# ---------------- CERT-234A (HALTING): the parent artifact reproduced -------
# Every leaf of l218/static.json outside the five keys the parent writes AFTER
# the slice boundary must equal what THIS run put in o, at float equality.
# Coverage bar DERIVED from the artifact's own leaf count (L224), never fixed.
S218 = json.load(open("l218/static.json"))
_LATE234 = ("predictions", "amendments", "limitations", "priors_readonly",
            "rows_per_draw_recomputed")
_n234a = 0


def _lc234(got, want, path):
    """recursive leaf compare at FLOAT/EXACT equality (the L211 pattern)."""
    global _n234a
    if isinstance(want, dict):
        assert isinstance(got, dict), (path, "type", type(got))
        assert set(got) == set(want), (path, "keys",
                                       sorted(set(got) ^ set(want)))
        for k in want:
            _lc234(got[k], want[k], f"{path}.{k}")
    elif isinstance(want, list):
        assert isinstance(got, list), (path, "type", type(got))
        assert len(got) == len(want), (path, "len", len(got), len(want))
        for i, w in enumerate(want):
            _lc234(got[i], w, f"{path}[{i}]")
    else:
        assert got == want, (path, got, want, "CERT-234A MISMATCH (STOP)")
        _n234a += 1


def _nleaf234(x):
    if isinstance(x, dict):
        return sum(_nleaf234(v) for v in x.values())
    if isinstance(x, list):
        return sum(_nleaf234(v) for v in x)
    return 1


_BAR234A = sum(_nleaf234(S218[k]) for k in S218 if k not in _LATE234)
for _k in S218:
    if _k in _LATE234:
        continue
    assert _k in o, (_k, "SLICE A did not produce a key the parent stored")
    _lc234(o[_k], S218[_k], _k)
assert _n234a == _BAR234A, (_n234a, _BAR234A, "CERT-234A coverage (STOP)")
# the FLOOR is DERIVED from the artifact's own blocks, never guessed (L224 —
# the fourth instance of this lesson: a hand-typed `>= 1000` halted this very
# run at the artifact's true non-verdict leaf count).
_CORE234 = ("Q218_1_primary", "Q218_2_rate", "Q218_3_u2", "profile",
            "cert_218t", "cert_w50", "Q210_1_primary", "Q210_4_gap",
            "cert_206", "cert_rebuild")
_floor234 = sum(_nleaf234(S218[k]) for k in _CORE234)
assert _floor234 > 0 and _n234a >= _floor234, \
    (_n234a, _floor234, "CERT-234A misses a core block (STOP)")
log(f"[CERT-234A] GREEN {_n234a} float equalities == the artifact's own leaf "
    f"count {_BAR234A} over {len([k for k in S218 if k not in _LATE234])} "
    f"keys: L218's ENTIRE measurement block (CERT-218T "
    f"{o['cert_218t']['n_checks']} + CERT-W50 {o['cert_w50']['n_checks']} + "
    f"CERT-DEFLV + Q218-1/2/3 + the 50-depth profile) reproduced")
o234_certA = dict(n_checks=_n234a, coverage_bar_derived=_BAR234A,
                  mode="float equality (==)",
                  n_keys=len([k for k in S218 if k not in _LATE234]),
                  excluded=list(_LATE234),
                  subsumes=dict(cert_218t=o["cert_218t"]["n_checks"],
                                cert_w50=o["cert_w50"]["n_checks"]))
_e234("CERT-234A")

# the parent's banner, as recorded INSIDE its own artifact (PREREG 0a)
assert o["banner"] == S218["banner"], "banner drift (STOP)"

# ---------------- PREREG 0b: r2 is SIGNED, and its sign is a measurement ----
assert _lfR > 0.0 and _lfL > 0.0, (_lfR, _lfL, "lam2 signed (STOP)")
R2 = GAP
assert R2 == abs(_lfR) / LAM1 or abs(R2 - abs(_lfR) / LAM1) < 1e-9, \
    (R2, abs(_lfR) / LAM1, "GAP vs signed Rayleigh (STOP)")

# ---------------- CERT-234B (HALTING): a multi-pair deflation, gated --------
def defl_multi(jv, ls, ld, pairs, iters=400, seed=21004):
    """Hotelling deflation against a LIST of (v,u) pairs. With a single pair
    this is bit-for-bit the certified defl_pair (PREREG 0e); admitted only by
    that exact agreement."""
    uvs = [float(u @ v) for v, u in pairs]
    rng = np.random.default_rng(seed)
    x = rng.random(NL)
    for (v, u), uv in zip(pairs, uvs):
        x -= v * float(u @ x) / uv
    x /= np.linalg.norm(x)
    hist = []
    for i in range(iters):
        y = mv(x, jv, ls, ld)
        for (v, u), uv in zip(pairs, uvs):
            y -= v * float(u @ y) / uv
        nrm = float(np.linalg.norm(y))
        if nrm == 0.0:
            return 0.0, x, dict(rel_spread_last6=0.0, last6=[], converged=True)
        x = y / nrm
        if i >= iters - 6:
            hist.append(nrm)
    sp = float((max(hist) - min(hist)) / max(hist))
    return float(np.median(hist)), x, dict(rel_spread_last6=sp, last6=hist,
                                           converged=bool(sp < 1e-6))


def defl_resid_multi(jv, ls, ld, pairs, x):
    """L217's law: diagnose an eigenpair with its RESIDUAL. SIGNED Rayleigh
    quotient on the multiply-deflated operator + relative residual."""
    uvs = [float(u @ v) for v, u in pairs]
    y = mv(x, jv, ls, ld)
    for (v, u), uv in zip(pairs, uvs):
        y = y - v * float(u @ y) / uv
    lam_fit = float(x @ y) / float(x @ x)
    r = y - lam_fit * x
    ny = float(np.linalg.norm(y))
    return lam_fit, (float(np.linalg.norm(r)) / ny if ny else float("inf"))


_n234b = 0
_m1, _x1, _i1 = defl_multi(jv_abs_an, csr_cols, csr_rows, [(V1, U1)])
_p1, _xp1, _ip1 = defl_pair(jv_abs_an, csr_cols, csr_rows, V1, U1)
assert _m1 == _p1, (_m1, _p1, "CERT-234B lam (STOP)")
assert np.array_equal(_x1, _xp1), "CERT-234B iterate (STOP)"
_lc234(_i1, _ip1, "CERT-234B info")
_n234b += 2
_f1, _r1 = defl_resid_multi(jv_abs_an, csr_cols, csr_rows, [(V1, U1)], V2)
assert (_f1, _r1) == (_lfR, _resR), ((_f1, _r1), (_lfR, _resR),
                                     "CERT-234B resid right (STOP)")
_f2, _r2b = defl_resid_multi(jv_abs_an, csr_rows, csr_cols, [(U1, V1)], U2)
assert (_f2, _r2b) == (_lfL, _resL), ((_f2, _r2b), (_lfL, _resL),
                                      "CERT-234B resid left (STOP)")
_n234b += 2
_m1L, _x1L, _ = defl_multi(jv_abs_an, csr_rows, csr_cols, [(U1, V1)])
assert _m1L == L2L and np.array_equal(_x1L, U2), "CERT-234B left pair (STOP)"
_n234b += 2
log(f"[CERT-234B] GREEN {_n234b} exact agreements: defl_multi with ONE pair "
    f"is bit-for-bit the certified defl_pair/defl_resid on eigenvalue, "
    f"iterate and every convergence field (both directions)")
o234_certB = dict(n_checks=_n234b, mode="exact float/array equality (==)",
                  source="the certified defl_pair / defl_resid (l218_tail.py)")
_e234("CERT-234B")

# ---------------- Q1 leg (a): the THIRD mode by DOUBLE deflation ------------
PAIRS_R = [(V1, U1), (V2, U2)]
PAIRS_L = [(U1, V1), (U2, V2)]
L3R, V3, INF3R = defl_multi(jv_abs_an, csr_cols, csr_rows, PAIRS_R)
L3L, U3, INF3L = defl_multi(jv_abs_an, csr_rows, csr_cols, PAIRS_L)
_lf3R, _res3R = defl_resid_multi(jv_abs_an, csr_cols, csr_rows, PAIRS_R, V3)
_lf3L, _res3L = defl_resid_multi(jv_abs_an, csr_rows, csr_cols, PAIRS_L, U3)

# PREREG 0d: the gate is the RESIDUAL and the SIGN, never the spread.
_res3_ok = bool(_res3R <= RES_BAR and _res3L <= RES_BAR)
_sgn3_ok = bool((_lf3R > 0) == (_lf3L > 0))
# degeneracy escape: a failed deflation converges back onto mode 2
_distinct3 = bool(abs(abs(_lf3R) - L2R) / L2R > 1e-6)
RESOLVED3 = bool(_res3_ok and _sgn3_ok and _distinct3)

K3_REAL = float(U3[LC]) * float(V3[POOL_IDX].sum()) / float(U3 @ V3)
A3_REAL = K3_REAL / K_REAL
R3 = _lf3R / LAM1
GAP3 = abs(_lf3R) / LAM1
log(f"[Q1 third mode] |lam3| R {L3R:.6f} / L {L3L:.6f} | signed Rayleigh "
    f"{_lf3R:+.6f} / {_lf3L:+.6f} | residual {_res3R:.3e} / {_res3L:.3e} "
    f"(bar {RES_BAR:.0e}) | resolved {RESOLVED3} (res {_res3_ok} sign "
    f"{_sgn3_ok} distinct {_distinct3}) | r3 {R3:+.6f} gap3 {GAP3:.6f} | "
    f"K3 {K3_REAL:+.6e} | A3 = K3/K {A3_REAL:+.6f} | u3[car] "
    f"{float(U3[LC]):+.6e}")

# _e and _pred_e are the slice's OWN certified arrays (never recomputed here,
# so no ulp can enter between the parent's expression and this card's).
_E = _e                                  # the stored, certified deficit
_ONE = _pred_e                           # L218's one-mode form A2*GAP^d
_RESID1 = _E - _ONE
_J10 = slice(9, DEEP)                    # the registered read range d>=10
_rel1 = float(max(_cf_relerr))
assert _rel1 == o["Q218_3_u2"]["closed_form_max_relerr_d10_50"], \
    (_rel1, "one-mode relerr must reproduce the parent's stored value (STOP)")

if RESOLVED3:
    _TWO = _ONE + np.array([A3_REAL * (R3 ** d) for d in DS])
    _rel2list = [abs(_TWO[j] - _E[j]) / abs(_E[j]) for j in range(9, DEEP)]
    _rel2 = float(max(_rel2list))
    _rel2_d10 = float(_rel2list[0])
    _rel2_d50 = float(_rel2list[-1])
    _improve = _rel1 / _rel2 if _rel2 > 0 else float("inf")
    if _rel2 < 0.01:
        BRANCH234_1 = "CF_TWO_MODE"
    elif _improve >= 2.0:
        BRANCH234_1 = "CF_PARTIAL"
    else:
        BRANCH234_1 = "CF_NO_IMPROVEMENT"
else:
    _TWO = None
    _rel2 = _rel2_d10 = _rel2_d50 = _improve = None
    BRANCH234_1 = "CF_UNRESOLVED"

# DESCRIPTIVE companion (one free parameter, r3 FIXED at the measurement):
# does the DIRECT A3 carry the miss, or the mode structure?
_A3_fit = float(np.sum(_RESID1[_J10] * (R3 ** DS[_J10]))
                / np.sum((R3 ** DS[_J10]) ** 2))
_TWOF = A2_REAL * R2 ** DS + _A3_fit * R3 ** DS
_rel2_fit = float(np.max(np.abs(_TWOF[_J10] - _E[_J10]) / np.abs(_E[_J10])))
# and the stored-derivable two-point anchor the PREREG registered against
_r3_2pt = float((abs(_RESID1[49]) / abs(_RESID1[9])) ** (1.0 / 40.0))
_A3_2pt = float(abs(_RESID1[9]) / _r3_2pt ** 10)
log(f"[Q1] {BRANCH234_1} | one-mode max relerr d10-50 {_rel1:.6f} -> two-mode "
    f"{_rel2 if _rel2 is None else round(_rel2, 6)} (improve "
    f"{_improve if _improve is None else round(_improve, 3)}x) | d10 "
    f"{_rel2_d10 if _rel2_d10 is None else round(_rel2_d10, 6)} d50 "
    f"{_rel2_d50 if _rel2_d50 is None else round(_rel2_d50, 6)} | fitted A3 "
    f"{_A3_fit:+.6f} -> relerr {_rel2_fit:.6f} | two-point implied r3 "
    f"{_r3_2pt:.6f} A3 {_A3_2pt:.6f}")

o234_Q1 = dict(
    branch=BRANCH234_1, resolved=RESOLVED3,
    res_ok=_res3_ok, sign_ok=_sgn3_ok, distinct_from_mode2=_distinct3,
    lam3_signed_rayleigh_right=_lf3R, lam3_signed_rayleigh_left=_lf3L,
    lam3_abs_right=L3R, lam3_abs_left=L3L,
    residual_right=_res3R, residual_left=_res3L, residual_bar=RES_BAR,
    rel_spread_last6_right=INF3R["rel_spread_last6"],
    rel_spread_last6_left=INF3L["rel_spread_last6"],
    r3_signed=R3, gap3=GAP3, gap2=R2,
    K3_real=K3_REAL, A3_real=A3_REAL, u3_carrier_real=float(U3[LC]),
    u3v3=float(U3 @ V3),
    one_mode_max_relerr=_rel1, two_mode_max_relerr=_rel2,
    two_mode_relerr_d10=_rel2_d10, two_mode_relerr_d50=_rel2_d50,
    improvement_factor=_improve, bar_close=0.01, bar_improve=2.0,
    A3_fitted_r3_fixed=_A3_fit, two_mode_fitted_max_relerr=_rel2_fit,
    r3_two_point_implied=_r3_2pt, A3_two_point_implied=_A3_2pt,
    relerr_profile_d10_50=([float(v) for v in _rel2list]
                           if RESOLVED3 else None),
    note=("the third eigenpair of the f4wA operator by DOUBLE Hotelling "
          "deflation; A3 = K3/K is the same sign- and scale-invariant "
          "construction as A2 (PREREG 0c), and the closed form uses the "
          "SIGNED ratio r3 = lam3/lam1 (PREREG 0b) so a negative third "
          "eigenvalue would alternate"))
_e234("Q1 third mode")

# ---------------- Q2 leg (b): K2's own null, re-computed exactly ------------
# PREREG 0f: K2_k is RE-COMPUTED (not derived from A2K*KK) and every draw is
# gated on reproducing the slice's own certified A2K at float equality.
K2K, _n234c = [], 0
for k in range(len(rows210)):
    ls2, ld2, va2 = REB[k]
    _lk, _vk, _ = pi_dir(va2, ls2, ld2)
    _lkL, _uk, _ = pi_dir(va2, ld2, ls2)
    _l2r, _v2k, _ = defl_pair(va2, ls2, ld2, _vk, _uk)
    _l2l, _u2k, _ = defl_pair(va2, ld2, ls2, _uk, _vk)
    _k2k = float(_u2k[LC]) * float(_v2k[POOL_IDX].sum()) / float(_u2k @ _v2k)
    assert _k2k / KK[k] == A2K[k], (k, _k2k / KK[k], A2K[k],
                                    "CERT-234C ratio drift (STOP)")
    assert _lk == rows210[k]["lam"], (k, "per-draw lam drift (STOP)")
    K2K.append(_k2k)
    _n234c += 1
K2K = np.array(K2K)
assert _n234c == len(rows210) == len(S218["rows_per_draw_recomputed"]), \
    (_n234c, "CERT-234C coverage, DERIVED from the artifact (STOP)")
# the cost slice this card DECLINED to take, measured rather than assumed
_DERIV = A2K * KK
_deriv_maxrel = float(np.max(np.abs(_DERIV - K2K) / np.abs(K2K)))
log(f"[CERT-234C] GREEN {_n234c} per-draw K2 re-computed; every ratio "
    f"K2_k/K_k == the slice's certified A2K at FLOAT EQUALITY | the derived "
    f"shortcut A2K*KK disagrees by max rel {_deriv_maxrel:.3e} (L226: a cost "
    f"slice is an intervention until measured)")
o234_certC = dict(n_checks=_n234c, mode="float equality (==)",
                  source="the slice's own A2K (Q218-3) and rows210 lam",
                  derived_shortcut_max_rel_diff=_deriv_maxrel)

_pct_K2 = float((K2K < K2_REAL).mean())
_pct_K = o["Q210_1_primary"]["carrier_K_percentile"]
BRANCH234_2 = "K2_FLOOR" if _pct_K2 == 0.0 else "K2_SEPARATED"
_medK2 = float(np.median(K2K))
_medK = float(np.median(KK))
assert _medK == o["Q210_1_primary"]["null_K_med"], "median K drift (STOP)"
_ratio_of_medians = _medK2 / _medK
_median_of_ratios = o["Q218_3_u2"]["A2_draw_med"]
_compose_rel = abs(_ratio_of_medians - _median_of_ratios) / abs(_median_of_ratios)
log(f"[Q2] {BRANCH234_2} | K2_real {K2_REAL:.6e} vs draws median {_medK2:.6e} "
    f"[p05 {float(np.percentile(K2K, 5)):.6e}, p95 "
    f"{float(np.percentile(K2K, 95)):.6e}] pct {_pct_K2:.3f} (K's own pct "
    f"{_pct_K:.3f}, floor resolution 0.01) | suppression folds: K "
    f"{_medK / K_REAL:.3f}x K2 {_medK2 / K2_REAL:.3f}x")
log(f"[Q3 compose] ratio-of-medians {_ratio_of_medians:.6f} vs "
    f"median-of-ratios {_median_of_ratios:.6f} -> rel disagreement "
    f"{_compose_rel:.6f} (PREREG 0g: these are DIFFERENT statistics)")

o234_Q2 = dict(
    branch=BRANCH234_2, pct_K2=_pct_K2, pct_K_stored=_pct_K,
    floor_resolution=1.0 / len(rows210),
    K2_real=K2_REAL, K_real=K_REAL,
    K2_draw_med=_medK2, K_draw_med=_medK,
    K2_p05=float(np.percentile(K2K, 5)), K2_p95=float(np.percentile(K2K, 95)),
    K2_min=float(K2K.min()), K2_max=float(K2K.max()),
    n_draws_K2_negative=int((K2K < 0).sum()),
    suppression_fold_K=_medK / K_REAL, suppression_fold_K2=_medK2 / K2_REAL,
    per_draw_K2=[float(v) for v in K2K],
    note=("K2's own marginal null, which did not exist in the stored "
          "artifacts (per-draw K2 was computed and discarded by L218); "
          "pct == 0.0 means below all 100 draws and nothing finer "
          "(PREREG 0h)"))
o234_Q3 = dict(
    ratio_of_medians=_ratio_of_medians, median_of_ratios=_median_of_ratios,
    rel_disagreement=_compose_rel, bar=0.01,
    A2_real=A2_REAL, A2_percentile_stored=o["Q218_3_u2"]["A2_percentile"],
    note=("DESCRIPTION, no branch: median(K2)/median(K) and median(K2/K) are "
          "different statistics (PREREG 0g)"))
_e234("Q2 + Q3")

# ---------------- predictions ------------------------------------------------
o234_pred = dict(
    P1=dict(registered="Q1 branch == CF_PARTIAL", measured=BRANCH234_1,
            correct=bool(BRANCH234_1 == "CF_PARTIAL")),
    P2=dict(registered="signed lam3 > 0", measured=_lf3R,
            correct=bool(_lf3R > 0)),
    P3=dict(registered="gap3 = |lam3|/lam1 in [0.82, 0.90]", measured=GAP3,
            correct=bool(0.82 <= GAP3 <= 0.90)),
    P4=dict(registered="direct A3 = K3/K in [0.0593, 0.2372] (2x around the "
                       "two-point implied 0.118575)",
            measured=A3_REAL, correct=bool(0.0593 <= A3_REAL <= 0.2372)),
    P5=dict(registered="Q2 branch == K2_FLOOR", measured=BRANCH234_2,
            correct=bool(BRANCH234_2 == "K2_FLOOR")),
    P6=dict(registered="|ratio-of-medians - median-of-ratios| / "
                       "median-of-ratios > 0.01",
            measured=_compose_rel, correct=bool(_compose_rel > 0.01)))
_np234 = sum(1 for v in o234_pred.values() if v["correct"])
log(f"[PREDICTIONS-234] {_np234} of {len(o234_pred)} correct: "
    + " ".join(f"{k}={'Y' if v['correct'] else 'N'}"
               for k, v in o234_pred.items()))

# ---------------- write ------------------------------------------------------
import os as _os234
_FP234 = {p: (_os234.stat(p).st_size, _os234.stat(p).st_mtime_ns)
          for p in ("l178/static.json", "l206/static.json",
                    "l210/static.json", "l210_static.py",
                    "l218/static.json", "l218_static.py")}
for _p, _v in _FP234.items():
    assert (_os234.stat(_p).st_size, _os234.stat(_p).st_mtime_ns) == _v, \
        (_p, "prior artifact MOVED during the run (STOP)")
log(f"[priors-234] GREEN {len(_FP234)} prior artifacts unchanged "
    f"(size, mtime_ns) across the run")

out234 = dict(o)
out234["design"] = (
    "L234 the TWO-MODE closed form, and K2's own null: measure the THIRD "
    "eigenpair of the f4wA operator by DOUBLE Hotelling deflation and ask "
    "whether e(d) = C_car(d)-1 = A2*r2^d + A3*r3^d closes L218's 11.6% "
    "one-mode band to under 1% at every d>=10 with A3 = K3/K measured "
    "directly; and store the 100 per-draw K2 L218 computed and discarded, so "
    "K2's own suppression percentile can be read beside K's 0.0. "
    "PREREG l234/PREREG.md.")
out234["prereg"] = "l234/PREREG.md"
out234["parent_l218"] = dict(
    design=S218["design"], prereg="l218/PREREG.md",
    slice="l218_static.py lines 1-1691 VERBATIM (literal PREFIX)")
out234["cert_234a"] = o234_certA
out234["cert_234b"] = o234_certB
out234["cert_234c"] = o234_certC
out234["Q1_two_mode"] = o234_Q1
out234["Q2_K2_null"] = o234_Q2
out234["Q3_compose"] = o234_Q3
out234["predictions_234"] = o234_pred
out234["n_predictions_true_234"] = _np234
out234["limitations_234"] = [
    "one substrate (f4wA), one operator |g*W_beta|, one null family (the "
    "l169c destination swaps), one carrier; L207's cross-null law applies",
    "100 draws cap every percentile at 0.01 resolution, so pct == 0.0 means "
    "'below all 100 draws' and nothing finer (PREREG 0h)",
    "e(d) is a RATIO profile, so a mode coefficient here is a ratio of "
    "overlap coefficients, not an amplitude in any physical unit",
    "no per-draw THIRD mode: Q1 is a real-operator question and the card "
    "registered no K3 null, so A3 has no null of its own (exactly the gap "
    "this card closed for K2)",
    "the fitted-A3 companion has one free parameter and is DESCRIPTION",
]
out234["priors_readonly_234"] = {k: list(v) for k, v in _FP234.items()}
_os234.makedirs("l234", exist_ok=True)
json.dump(out234, open("l234/static.json", "w"), indent=1)
_e234("total")
log("[done] wrote l234/static.json")
