# ============== L225b ADDENDUM (appended by l225b_build.py) ==============
# DECLARED POST-HOC. No branch, no bar, no prediction. Written AFTER the
# parent's verdict was read, and it exists because the parent's registered
# branch set turned out to answer a COUNT question while the card's real
# question was a MEMBERSHIP question.
#
# Everything above this line is l225_static.py lines 1-1735 VERBATIM (the
# parent with its runtime stamp and its WRITER cut), so premise 0a,
# CERT-213 (289), CERT-GRP (12), CERT-FAST (9), CERT-SEED (15), CERT-207,
# CERT-T, CERT-178 and the whole sweep re-run as free certification.
# Writes l225/addendum.json ONLY.

a = {}
a["status"] = ("POST-HOC addendum to L225. Declared post-hoc: no branch, no "
               "registered bar, no prediction. The parent's registered "
               "quantities are UNCHANGED and are re-certified here before "
               "any addendum number is read (CERT-225).")
a["parent"] = "l225/static.json"
a["prereg"] = "l225/PREREG.md (parent's; this addendum is NOT registered)"

# =====================================================================
# CERT-225 (HALTING): the parent's branch-bearing stored values at
# float/int/str equality, from the artifact, before anything new is read.
# =====================================================================
_PP225 = "l225/static.json"
_stp = os.stat(_PP225)
_fpp = (_stp.st_size, _stp.st_mtime_ns)
with open(_PP225) as _fh:
    S225 = json.load(_fh)
_n225 = 0
assert S225["branches"]["Q225_1"] == BR1, "parent branch drift (STOP)"
_n225 += 1
for _k in GRP:
    _sp = S225["Q225_1_fdr"]["per_substrate"][_k]
    _lv = Q225_1[_k]
    for _f in ("m_types", "n_survivors_low", "n_survivors_high",
               "n_at_p_floor_low", "dnp33_p_low", "dnp33_q_low",
               "dnp33_rank_by_p", "dnp33_n_types_with_smaller_p",
               "survivor_share", "dnp33_pct_strict_at_20k",
               "dnp33_l213_null_pct", "dnp33_pct_among_type_medians"):
        assert float(_sp[_f]) == float(_lv[_f]), (_k, _f, "CERT-225 (STOP)")
        _n225 += 1
    assert bool(_sp["dnp33_survives"]) == bool(_lv["dnp33_survives"])
    assert _sp["survivor_types"] == _lv["survivor_types"]
    assert _sp["branch"] == _lv["branch"]
    _n225 += 3
    _fl = S225["premise_0a_resolution_floor"][_k]
    for _f in ("m_types", "p_min_at_l213_draws", "p_min_at_l225_draws",
               "bh_rank1_threshold",
               "min_floor_tied_types_for_any_rejection_at_l213"):
        assert float(_fl[_f]) == float(RESFLOOR[_k][_f]), (_k, _f, "floor")
        _n225 += 1
assert S225["cert_seed"]["n_checks"] == 15 and \
    S225["cert_213"]["n_checks"] == 289, "parent cert counts moved (STOP)"
_n225 += 2
log(f"[CERT-225] GREEN {_n225} stored parent values at float/int/str "
    f"equality BEFORE any addendum number was read")
a["cert_225"] = dict(n_checks=_n225, mode="float/int/str equality (==)",
                     source="l225/static.json (read-only, fingerprinted)")

# =====================================================================
# (A) THE PARENT'S AUTO-GENERATED `headline` STRING IS WRONG, AND THE
# ARTIFACT PROVES IT AGAINST ITSELF.
# The registered branch set {F_UNIQUE, F_SMALL_FAMILY, F_COMMON,
# F_DEGENERATE} is defined on a COUNT of survivors.  F_SMALL_FAMILY fired
# at 5 survivors -- correctly -- and the prose generator then said "DNp33
# is one of a small family of 5 types surviving", because its author
# (me, pre-measurement) assumed that if few types survived the actor
# would be among them.  The parent's OWN stored field says otherwise.
# This block asserts the contradiction rather than describing it.
# =====================================================================
_hl = S225["headline"]
_surv33 = {k: bool(Q225_1[k]["dnp33_survives"]) for k in Q225_1}
assert "surviving the nonselective FDR" in _hl, "headline text moved (STOP)"
assert not _surv33[PRIMARY], \
    "the parent says DNp33 survives -- then the headline was right (STOP)"
_qstr = ", ".join(f"{Q225_1[k]['dnp33_q_low']:.3f}" for k in Q225_1)
_fixed = (
    f"DNp33's TYPE-level avoidance does NOT survive multiplicity "
    f"correction. Its uncorrected permutation p is "
    f"{Q225_1[PRIMARY]['dnp33_p_low']:.5f} (BH q "
    f"{Q225_1[PRIMARY]['dnp33_q_low']:.4f}), rank "
    f"{Q225_1[PRIMARY]['dnp33_rank_by_p']} of "
    f"{Q225_1[PRIMARY]['m_types']} descending types, and it is NOT one of "
    f"the {Q225_1[PRIMARY]['n_survivors_low']} types that do survive BH at "
    f"alpha {ALPHA} -- a result that holds on all three substrates "
    f"(q {_qstr}).")
a["parent_headline_is_wrong"] = dict(
    parent_headline=_hl,
    corrected_headline=_fixed,
    dnp33_survives_per_substrate=_surv33,
    why=("the registered branch set is defined on the COUNT of survivors, "
         "so F_SMALL_FAMILY is a true statement about the family SIZE and "
         "carries no information about whether the ACTOR is in it; the "
         "prose generator silently supplied that missing clause"),
    method_law=("a branch defined on a COUNT cannot answer a MEMBERSHIP "
                "question: when the card asks 'is this actor special', the "
                "branch definition must contain the actor's membership, or "
                "the verdict sentence will be generated from an assumption "
                "the measurement never made"))
log(f"[A] PARENT HEADLINE WRONG (proved against the artifact's own "
    f"dnp33_survives field). CORRECTED: {_fixed}")

# =====================================================================
# (B) POWER OR MAGNITUDE?  Is DNp33's non-survival a draw-count artifact?
# A permutation p estimates a fixed tail probability pi = P(null <= real).
# BH would need p <= alpha * rank / m at the cell's own rank (and at best
# alpha / m at rank 1).  If a confidence interval for pi EXCLUDES that
# requirement, no draw count can ever rescue the claim.
# Wilson score interval (closed form, no new dependency).
# =====================================================================
_z = 1.959963984540054          # two-sided 95%


def _wilson(k, n, z=_z):
    ph = k / n
    d = 1.0 + z * z / n
    c = ph + z * z / (2 * n)
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


POW = {}
for _k in Q225_1:
    _v = Q225_1[_k]
    _m = _v["m_types"]
    _p = _v["dnp33_p_low"]
    _kcnt = int(round(_p * (N_EXT + 1) - 1))     # #{null <= real}
    _lo95, _hi95 = _wilson(_kcnt, N_EXT)
    _req_own = ALPHA * _v["dnp33_rank_by_p"] / _m
    _req_rank1 = ALPHA / _m
    POW[_k] = dict(
        n_draws=N_EXT, n_null_le_real=_kcnt, p_point=_p,
        pi_wilson95=[_lo95, _hi95],
        bh_required_p_at_own_rank=_req_own,
        bh_required_p_at_rank1=_req_rank1,
        ci_excludes_own_rank_requirement=bool(_lo95 > _req_own),
        ci_excludes_rank1_requirement=bool(_lo95 > _req_rank1),
        verdict=("MAGNITUDE: the tail probability itself is too large; no "
                 "draw count can make this p BH-significant"
                 if _lo95 > _req_own else
                 "POWER: more draws could plausibly cross the bar"))
    log(f"[B] {_k}: DNp33 {_kcnt}/{N_EXT} null draws <= real -> pi 95% CI "
        f"[{_lo95:.5f}, {_hi95:.5f}] vs BH requirement {_req_own:.5f} at "
        f"its own rank {_v['dnp33_rank_by_p']} (and {_req_rank1:.6f} at "
        f"rank 1) -> {POW[_k]['verdict'].split(':')[0]}")
a["B_power_or_magnitude"] = dict(
    method="Wilson score 95% interval for the permutation tail probability",
    per_substrate=POW,
    reading=("L213's draw count was not the limitation on the ACTOR. The "
             "resolution floor (premise 0a) was the limitation on the "
             "FAMILY: it is why the survivors were invisible, not why "
             "DNp33 failed."))

# =====================================================================
# (C) HOW MANY TYPES CLEAR THE UNCORRECTED BAR?  The card's own framing:
# "a null pct of .013 on ONE preselected type says nothing about how many
# of 426 types clear it by chance."  Under the null, alpha*m types are
# expected to clear an uncorrected alpha bar.
# =====================================================================
UNC = {}
for _k, _g in GRP.items():
    _pl = SWEEP[_k]["p_low"]
    _ph = SWEEP[_k]["p_high"]
    _m = len(_g["names"])
    _n05 = int((_pl <= ALPHA).sum())
    _n05h = int((_ph <= ALPHA).sum())
    _n013 = int((_pl <= Q1[_k]["null_pct"]).sum())
    UNC[_k] = dict(
        m_types=_m, expected_by_chance=ALPHA * _m,
        n_pass_uncorrected_low=_n05, n_pass_uncorrected_high=_n05h,
        excess_over_chance_low=float(_n05 / (ALPHA * _m)),
        n_at_or_below_dnp33_l213_pct=_n013,
        dnp33_l213_null_pct=Q1[_k]["null_pct"],
        n_survivors_after_bh=Q225_1[_k]["n_survivors_low"])
    log(f"[C] {_k}: {_n05} of {_m} types clear the UNCORRECTED p<={ALPHA} "
        f"bar vs {ALPHA * _m:.1f} expected by chance ({_n05 / (ALPHA * _m):.2f}x)"
        f" | {_n013} types sit at or below DNp33's own L213 percentile "
        f"{Q1[_k]['null_pct']} | {Q225_1[_k]['n_survivors_low']} survive BH")
a["C_uncorrected_vs_corrected"] = dict(
    per_substrate=UNC,
    reading=("the type-level signal is REAL in aggregate -- more types "
             "clear the uncorrected bar than chance allows -- and that is "
             "exactly why a single preselected type's uncorrected "
             "percentile cannot carry the claim"))

# =====================================================================
# (D) WHO DOES survive, and does the family transport across substrates?
# =====================================================================
_sets = {k: set(Q225_1[k]["survivor_types"]) for k in Q225_1}
_all3 = sorted(set.intersection(*_sets.values()))
_any = sorted(set.union(*_sets.values()))
FAM = []
for _t in _any:
    _row = dict(type=_t,
                substrates=[k for k in Q225_1 if _t in _sets[k]],
                n_substrates=sum(1 for k in Q225_1 if _t in _sets[k]))
    for _k in Q225_1:
        _hit = [r for r in Q225_1[_k]["top20"] if r["type"] == _t]
        if _hit:
            _row[_k] = dict(n_members=_hit[0]["n_members"],
                            median_R=_hit[0]["median_R"],
                            p_low=_hit[0]["p_low"], q_low=_hit[0]["q_low"])
    _gis = [POP[PRIMARY]["gis"][i]
            for i in GRP[PRIMARY]["big"].get(_t, np.array([], np.int64))]
    _row["annotation_primary"] = {c: type_mode(_gis, c) for c in sorted(_ANN)} \
        if _gis else None
    FAM.append(_row)
_d33 = [POP[PRIMARY]["gis"][i] for i in GRP[PRIMARY]["big"][TYPE_NAME]]
a["D_survivor_family"] = dict(
    survivors_on_all_three=_all3,
    survivors_on_any=_any,
    n_any=len(_any), n_all3=len(_all3),
    rows=FAM,
    dnp33_annotation_primary={c: type_mode(_d33, c) for c in sorted(_ANN)},
    reading=("the only type surviving on ALL THREE substrates is "
             f"{_all3[0] if _all3 else 'NONE'}; DNp33 survives on none. "
             "Q225-2's shared-annotation rule fired on G1_cutwA "
             "(hemilineage SMPpv1 at share 1.000, p .0005 <= .05/25) and "
             "the survivors' modal neurotransmitter there is gaba -- "
             "neither of which is DNp33's (putative_primary / "
             "acetylcholine), so the cheaper explanation that exists "
             "belongs to the SURVIVORS and not to the actor"))
log(f"[D] survivors on all three: {_all3} | on any: {_any} | DNp33 on none")

# =====================================================================
# (E) WHAT THE L213 CLAIM BECOMES
# =====================================================================
a["E_what_l213_becomes"] = dict(
    l213_claim=("Q213-1 branch T_TYPE_LOW: the DNp33 type median sits at "
                "within-mass-stratum permutation null percentile "
                ".0145/.0105/.0130, read against a .05 bar on ONE "
                "preselected type"),
    unchanged=("the percentile itself is REPRODUCED here at float equality "
               "(CERT-SEED) and at 10x the draws reads "
               f"{Q225_1[PRIMARY]['dnp33_pct_strict_at_20k']:.5f} on the "
               "primary substrate -- it is a correct measurement"),
    what_changes=("it is UNCORRECTED. Benjamini-Hochberg over the "
                  f"{Q225_1[PRIMARY]['m_types']} >=2-member descending "
                  f"types puts DNp33 at q "
                  f"{Q225_1[PRIMARY]['dnp33_q_low']:.4f}, rank "
                  f"{Q225_1[PRIMARY]['dnp33_rank_by_p']}, outside the "
                  "surviving family on all three substrates; and (B) shows "
                  "no draw count can change that"),
    honest_reading=("the TYPE-level avoidance claim for DNp33 is "
                    "WITHDRAWN as an inferential claim and retained as a "
                    "DESCRIPTION of a cell selected for being extreme "
                    "(Kriegeskorte 2009). The CELL-level claims of "
                    "L206-L212 are untouched by this card: they were "
                    "already labelled selected, and their "
                    "de-circularising leg is L212's independent-specimen "
                    "v783 reading"),
    what_survives_instead=("a nonselective finding the family did not "
                           "have before: there IS a small, "
                           "substrate-consistent set of descending types "
                           "that avoid the motor pools beyond "
                           "multiplicity-corrected chance, headed by "
                           f"{_all3[0] if _all3 else 'NONE'}"))

a["method_laws"] = [
    "A branch defined on a COUNT cannot answer a MEMBERSHIP question. "
    "F_SMALL_FAMILY fired correctly at 5 survivors and the verdict prose "
    "then claimed the actor was one of them -- an assumption the "
    "measurement never made. Put the actor's membership INSIDE the branch "
    "definition whenever the card asks whether a specific unit is special.",
    "A permutation p-value's draw count has TWO separate consequences, and "
    "they bind on different objects: the RESOLUTION FLOOR 1/(B+1) decides "
    "whether the FAMILY's strongest members can be rejected at all (at "
    "B=2000 nothing could be, and 2 of 3 substrates' survivors sit AT the "
    "floor), while the tail probability's confidence interval decides "
    "whether a PARTICULAR unit can ever clear its own BH requirement. "
    "Compute both before calling a non-survival a power problem.",
    "An UNCORRECTED percentile on a preselected unit and a "
    "multiplicity-corrected one can disagree by an order of magnitude "
    "(.0145 -> q .157 = 10.8x) while the underlying measurement is "
    "bit-identical. The correction is not a detail of presentation; it is "
    "the difference between a claim and a description.",
    "When a card's own framing predicts the uncomfortable answer "
    "(Kriegeskorte's policy step (1) predicts the actor may be one of "
    "many), scoring the registered prediction FALSE is the cheap part; the "
    "work is deriving what the prior claim becomes, which is a different "
    "sentence, not a weaker adverb.",
]
a["limitations"] = [
    "The addendum is POST-HOC: nothing here carries a registered branch.",
    "BH assumes p-values are valid; permutation p-values here are censored "
    "at 5.00e-05 and discrete, so q-values near the floor are conservative.",
    "The Wilson interval is a normal-score approximation; the exact "
    "Clopper-Pearson interval would be marginally wider and is not "
    "computed (no new dependency introduced).",
    "Survivor-family membership is read on three non-independent "
    "substrates of ONE specimen; 'transport' here means substrate "
    "robustness, never cross-specimen replication.",
    "DNp33's type median remains a 2-POINT statistic (L213 limit 1).",
]
a["runtime_s"] = time.time() - t0
_stp2 = os.stat(_PP225)
assert (_stp2.st_size, _stp2.st_mtime_ns) == _fpp, \
    "l225/static.json CHANGED during the addendum (STOP)"
with open("l225/addendum.json", "w") as _fh:
    json.dump(a, _fh, indent=1, default=float)
log(f"[done-addendum] {a['runtime_s']:.1f}s -> l225/addendum.json | "
    f"CERT-225 {_n225} | corrected headline written")
