# ================= L221b ADDENDUM TAIL (appended by l221b_build.py) =========
# POST-HOC, DECLARED AS SUCH. Everything above this line is the L221 parent
# SLICED AT LINE 440 -- i.e. the parent's own nine verbatim source slices plus
# its measurement body up to and including the leg-(a) block, with its
# leg (b) / primary / predictions / writer blocks CUT (the L213 pattern). So
# CERT-F4, CERT-178 (420), CERT-NULL (8), CERT-REW, CERT-SI (240), CERT-MENU
# (100), CERT-FH (61,819), CERT-211 (434), CERT-SIGEN (1,922,356), CERT-D5,
# CERT-CROFTS, CERT-FHE (93,930) and CERT-DAG ALL re-run as free certification
# before this addendum reads a single number, and the parent's l221/static.json
# is NOT touched (this writes l221/addendum.json only).
#
# WHY IT EXISTS: the parent measured `identity_holds == False` on PREREG 0b's
# analytic identity rho(w, used) == -rho(T_L, used). The identity is TRUE
# (T_L is a strictly decreasing function of A[e] at a fixed source). The
# parent's ESTIMATOR was wrong: np.argsort(np.argsort(x)) assigns distinct
# ORDINAL ranks to tied values by array position, and reversing the value
# order does NOT reverse positional tie-breaking. This addendum re-measures
# with AVERAGE ranks (the definition Spearman's rho is stated for) and
# diagnoses the tie structure that broke it. Nothing in the parent's branch,
# bar or verdict depends on it: leg (a) was registered as reporting a
# MECHANICALLY EXPECTED quantity, explicitly not as evidence.
import os as _os221b

o221B = dict(
    design="L221b post-hoc addendum: the leg-(a) rank identity under AVERAGE "
           "ranks, and the EDGE-vs-COST tie structure of the null that the "
           "parent's 11-vs-16 comparison conflated.",
    status="POST-HOC (not pre-registered). Both items are DIAGNOSTIC: the "
           "first repairs an estimator, the second re-expresses an already-"
           "registered comparison in the currency the parent's own PREREG 0a "
           "declared primary. Neither moves L221's branch (F_METRIC) or bar.",
    parent="l221/static.json", parent_prereg="l221/PREREG.md")
log("=" * 72)
log("[L221b] post-hoc addendum: the rank identity and the null's tie structure")


def _avg_rank(x):
    """ranks with TIES AVERAGED -- the definition Spearman's rho is stated
    for. np.argsort(np.argsort(x)) is an ORDINAL rank and is NOT invariant to
    value-order reversal in the presence of ties, which is exactly how the
    parent's estimator broke a true analytic identity."""
    x = np.asarray(x, float)
    n = x.size
    order = np.argsort(x, kind="stable")
    r = np.empty(n, float)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def _spear_avg(x, y):
    return float(np.corrcoef(_avg_rank(x), _avg_rank(y))[0, 1])


_TL69 = np.array([T_L[CB0 + j] for j in range(K_OUT)], float)
_LL69 = np.array([L_L[CB0 + j] for j in range(K_OUT)], float)

# the analytic premise, asserted rather than trusted: T_L and L_L are strictly
# DECREASING in the weight at a fixed source, i.e. the value ORDERS are exact
# reversals. Checked pairwise over all 69*68/2 pairs.
_npair, _bad = 0, 0
for _i in range(K_OUT):
    for _j in range(_i + 1, K_OUT):
        _npair += 1
        if _w[_i] < _w[_j]:
            if not (_TL69[_i] > _TL69[_j] and _LL69[_i] > _LL69[_j]):
                _bad += 1
        elif _w[_i] > _w[_j]:
            if not (_TL69[_i] < _TL69[_j] and _LL69[_i] < _LL69[_j]):
                _bad += 1
        else:
            if not (_TL69[_i] == _TL69[_j] and _LL69[_i] == _LL69[_j]):
                _bad += 1
assert _bad == 0, ("PREREG 0b's monotonicity premise FAILED", _bad, _npair)
log(f"[CERT-MONO] GREEN {_npair} pairwise order checks: T_L and L_L are exact "
    f"order-REVERSALS of the out-weight (PREREG 0b's premise, asserted)")

_rw = _spear_avg(_w, _used)
_rt = _spear_avg(_TL69, _used)
_rl = _spear_avg(_LL69, _used)
_vals, _cnts = np.unique(_w, return_counts=True)
_ord_w = np.argsort(np.argsort(_w)).astype(float)
_ord_t = np.argsort(np.argsort(_TL69)).astype(float)
_ord_mismatch = int(np.sum(_ord_w != (K_OUT - 1 - _ord_t)))
o221B["A_rank_identity"] = dict(
    prereg_claim="0b: weight-vs-used, T_L-vs-used and L_L-vs-used are ONE "
                 "statistic up to sign",
    parent_estimator="ordinal ranks via np.argsort(np.argsort(x))",
    parent_rho_w_used=_rho_w_used, parent_rho_T_used=_rho_t_used,
    parent_rho_L_used=_rho_l_used,
    parent_identity_holds=bool(o["Q221_a_weight_skew"]["identity_holds"]),
    avg_rank_rho_w_used=_rw, avg_rank_rho_T_used=_rt, avg_rank_rho_L_used=_rl,
    avg_rank_identity_abs_err_T=abs(_rw + _rt),
    avg_rank_identity_abs_err_L=abs(_rw + _rl),
    identity_holds_avg_rank=bool(abs(_rw + _rt) < 1e-12
                                 and abs(_rw + _rl) < 1e-12),
    n_distinct_weights=int(_vals.size), menu=int(K_OUT),
    n_tied_edges=int(K_OUT - _vals.size),
    largest_tie_group=int(_cnts.max()),
    tie_group_sizes=[int(c) for c in sorted(_cnts[_cnts > 1], reverse=True)],
    ordinal_rank_mismatches=_ord_mismatch,
    verdict="the identity is TRUE and the parent's estimator was wrong: with "
            "ties averaged the three rhos are exact mirrors; with ordinal "
            "ranks they are not, because reversing the value order does not "
            "reverse positional tie-breaking.")
log(f"[L221b] A: avg-rank rho(w,used) {_rw:+.6f} vs -rho(T_L,used) {-_rt:+.6f} "
    f"(|err| {abs(_rw + _rt):.3e}) and -rho(L_L,used) {-_rl:+.6f} "
    f"(|err| {abs(_rw + _rl):.3e}) -> identity "
    f"{o221B['A_rank_identity']['identity_holds_avg_rank']}; the parent read "
    f"{_rho_w_used:+.4f} vs {_rho_t_used:+.4f} on ORDINAL ranks with "
    f"{int(K_OUT - _vals.size)} tied edges ({_vals.size} distinct weights of "
    f"{K_OUT}, largest tie group {int(_cnts.max())}, "
    f"{_ord_mismatch} ordinal ranks not mirrored)")

# ---- B: the EDGE-vs-COST tie structure of the null (PREREG 0a, extended) ---
# The parent registered 0a for the CARRIER (its 11 costs turned out to be 11
# edges). The same distinction applies to the NULL, and there it BITES: L211
# compared the carrier's 11 distinct COSTS against a null median of 16 distinct
# COSTS. In the edge currency the null median is larger, so the parent's
# headline comparison UNDERSTATED the narrowness by exactly the null's own tie
# deficit. Reported here in both currencies.
_ne = np.array([r["n_edges"] for r in NULL_FE], float)
_nc = np.array([r["n_costs"] for r in NULL_FE], float)
_defi = _ne - _nc
o221B["B_edge_vs_cost_null"] = dict(
    carrier_n_edges=int(_ab["n_realised"]),
    carrier_n_costs=int(_ab["n_realised_costs"]),
    carrier_tie_deficit=int(_ab["n_realised"] - _ab["n_realised_costs"]),
    null_edges_med=float(np.median(_ne)), null_edges_p05=float(np.percentile(_ne, 5)),
    null_costs_med=float(np.median(_nc)), null_costs_p05=float(np.percentile(_nc, 5)),
    null_tie_deficit_med=float(np.median(_defi)),
    null_tie_deficit_max=float(_defi.max()),
    n_draws_with_ties=int((_defi > 0).sum()),
    parent_L211_null_cost_med=float(
        o["L211_primary"]["menu"]["null_n_distinct_first_hops_med"]),
    ratio_edges=float(np.median(_ne)) / float(_ab["n_realised"]),
    ratio_costs=float(np.median(_nc)) / float(_ab["n_realised_costs"]),
    verdict="the real wiring's realised first hops carry NO cost ties while "
            "the null's do, so a COST-count contrast is a mixture of "
            "narrowness and tie structure. The edge-currency contrast is the "
            "clean one and it is LARGER.")
log(f"[L221b] B: carrier {int(_ab['n_realised'])} edges / "
    f"{int(_ab['n_realised_costs'])} costs (tie deficit 0) vs null med "
    f"{float(np.median(_ne)):.1f} edges / {float(np.median(_nc)):.1f} costs "
    f"(deficit med {float(np.median(_defi)):.1f}, "
    f"{int((_defi > 0).sum())}/100 draws tied) -> ratio "
    f"{float(np.median(_ne)) / float(_ab['n_realised']):.3f}x in EDGES vs "
    f"{float(np.median(_nc)) / float(_ab['n_realised_costs']):.3f}x in COSTS")

o221B["limitations"] = [
    "POST-HOC. Item A repairs an estimator for a quantity the PREREG "
    "explicitly declared mechanically expected and not evidence; item B "
    "re-expresses an already-registered count in the currency PREREG 0a "
    "declared primary. Neither is a new test and neither moves F_METRIC.",
    "The avg-rank rho is still a 69-point correlation against a binary "
    "indicator with 11 positives; no null is attached to it and none is "
    "claimed.",
    "Item B's edge-currency null median is measured on the same single "
    "l169c null family as the parent (L207's cross-null law)."]
o221B["certification"] = dict(
    parent_slice="l221_tail.py lines 1-440 VERBATIM (writer, predictions, "
                 "primary and leg (b) CUT)",
    free_regates=["CERT-F4", "CERT-178 420", "CERT-NULL 8", "CERT-REW",
                  "CERT-SI 240", "CERT-MENU 100", "CERT-FH 61,819",
                  "CERT-211 434", "CERT-SIGEN 1,922,356", "CERT-D5 6",
                  "CERT-CROFTS", "CERT-FHE 93,930", "CERT-DAG"],
    new_halting=dict(CERT_MONO=dict(
        checks=_npair,
        what="all 69*68/2 pairwise order comparisons confirm T_L and L_L are "
             "EXACT order-reversals of the out-weight -- PREREG 0b's analytic "
             "premise asserted rather than trusted, which is what makes the "
             "avg-rank identity a GATE on the estimator and not an opinion")),
    parent_untouched="l221/static.json is NOT written by this script")
for _p, _fp in FP221.items():
    _st = _os221b.stat(_p)
    assert (int(_st.st_size), int(_st.st_mtime_ns)) == _fp, (_p, "MUTATED")
_stp = _os221b.stat("l221/static.json")
o221B["parent_fingerprint"] = [int(_stp.st_size), int(_stp.st_mtime_ns)]
json.dump(o221B, open("l221/addendum.json", "w"), indent=1)
log("=" * 72)
log(f"L221b DONE {time.time()-t0:.0f}s | identity under avg ranks "
    f"{o221B['A_rank_identity']['identity_holds_avg_rank']} | null edges/costs "
    f"{float(np.median(_ne)):.1f}/{float(np.median(_nc)):.1f} | CERT-MONO "
    f"{_npair}")
