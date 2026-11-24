
# ===================== L223 TAIL ==========================================
# Everything above this line is VERBATIM inherited source: l212_head.py sliced
# to CUT its blocker-writer and re-point OUT, the three l207_tail.py function
# slices, l212_tail.py lines 1-227 (L212's ENTIRE measurement pipeline, writer
# CUT) and l222_tail.py lines 26-88 (CERT-212, inherited as SOURCE rather than
# re-implemented -- the L211 lesson).  So CERT-783, CERT-L207, CERT-MV,
# CERT-GATE, the lam1 power iteration, the rescale NO-OP, L212's Q1/Q2/Q3 legs
# and CERT-212's whole float-equality table all ran before a single L223 number
# exists.

ZERO_FRAC_BAR = 0.10
RHO_DEGEN_BAR = 0.95
o["bars"] = dict(pct_specific=PCT_BAR, rho_degenerate=RHO_DEGEN_BAR,
                 zero_frac_escape=ZERO_FRAC_BAR, cohort_k=COHORT_K,
                 beta_L=BETA_L)

# ---------------- CERT-PAIR (HALTING): the paired table IS the published one -
nP = 0
assert set(CV.keys()) == set(COH_U), "CV keys != COH_U (STOP)"
nP += 1
assert set(CV2.keys()) == set(COH_U), "CV2 keys != COH_U (STOP)"
nP += 1
assert len(COH_U) == o["Q1_primary"]["cohort_union_n"] == \
    o["Q2_secondary_descriptive"]["cohort_union_n"], "union n (STOP)"
nP += 1
assert np.array_equal(SUB2["jv"], SUB["jv"]), "legs differ in operator (STOP)"
nP += 1
assert np.array_equal(SUB2["rows"], SUB["rows"]) and \
    np.array_equal(SUB2["cols"], SUB["cols"]), "legs differ in edges (STOP)"
nP += 1
for _nm, _ra, _rb, _blk, _key in (
        ("carrier_motor", R_CAR, None, "Q1_primary", "carrier_R"),
        ("mirror_motor", R_MIR, None, "Q1_primary", "mirror_R"),
        ("carrier_desc", R_CAR2, None, "Q2_secondary_descriptive", "carrier_R"),
        ("mirror_desc", R_MIR2, None, "Q2_secondary_descriptive", "mirror_R")):
    assert _ra["R"] == o[_blk][_key], (_nm, "paired value != published (STOP)")
    nP += 1
assert R_CAR["m_out"] == R_CAR2["m_out"] and R_MIR["m_out"] == R_MIR2["m_out"], \
    "m_out differs between legs (STOP)"
nP += 1
assert all(CV[g] is not None and CV2[g] is not None for g in COH_U), \
    "a cohort cell has R=None (zero out-mass) (STOP)"
nP += 1
o["cert_pair"] = dict(n_checks=nP, mode="set / array_equal / float equality",
                      note="CV (motor) and CV2 (descending) cover the IDENTICAL "
                           "cohort key set on the IDENTICAL operator, and both "
                           "actors' entries equal L212's published R values.")
log(f"[CERT-PAIR] GREEN {nP} checks - both legs on one cohort, one operator")

# ---------------- CERT-RANK (HALTING): rankvec IS a midrank -----------------
_ra_in = [CV[g] for g in COH_U] + [R_CAR["R"], R_MIR["R"]]
_rb_in = [CV2[g] for g in COH_U] + [R_CAR2["R"], R_MIR2["R"]]
nR = 0
for _vec in (_ra_in, _rb_in):
    _rk = rankvec(_vec)
    _n = len(_vec)
    assert abs(sum(_rk) - _n * (_n + 1) / 2.0) < 1e-9, "rank sum (STOP)"
    nR += 1
    _by = {}
    for _v, _r in zip(_vec, _rk):
        _by.setdefault(_v, set()).add(_r)
    for _v, _rs in _by.items():
        assert len(_rs) == 1, (_v, "a tie group got DIFFERENT ranks (STOP)")
        nR += 1
    assert len(_by) == len(set(_rk)), "distinct values != distinct ranks (STOP)"
    nR += 1
o["cert_rank"] = dict(n_checks=nR, mode="exact tie-group identity",
                      note="the inherited rankvec is verified to be an "
                           "AVERAGE-rank (midrank) estimator on THIS data "
                           "before any C_rank is read (tick-252 midrank law); "
                           "argsort-of-argsort would fail the tie-group gate.")
log(f"[CERT-RANK] GREEN {nR} checks - rankvec is a midrank on this data")

# ---------------- Q223-0 (READ FIRST): are the two legs the same thing? -----
RHO = {}
for _nm, _coh in (("COH_C", COH_C), ("COH_M", COH_M), ("COH_U", COH_U)):
    RHO[_nm] = spearman_l([CV[g] for g in _coh], [CV2[g] for g in _coh])
o["Q223_0_rho_first"] = dict(
    rho_COH_C=RHO["COH_C"], rho_COH_M=RHO["COH_M"], rho_COH_U=RHO["COH_U"],
    n_COH_C=len(COH_C), n_COH_M=len(COH_M), n_COH_U=len(COH_U),
    bar=RHO_DEGEN_BAR,
    note="Spearman (midranks) between the motor-readout R and the "
         "descending-readout R across the cohort. Read BEFORE the carrier's "
         "contrast because it decides whether the contrast carries any "
         "information at all.")
log(f"[Q223-0] rho COH_C {RHO['COH_C']:.4f} | COH_M {RHO['COH_M']:.4f} "
    f"| COH_U {RHO['COH_U']:.4f} (bar {RHO_DEGEN_BAR})")

# ---------------- the contrast ----------------------------------------------
C_CAR = math.log(R_CAR["R"]) - math.log(R_CAR2["R"])
C_MIR = math.log(R_MIR["R"]) - math.log(R_MIR2["R"])


def clog_vec(coh):
    """C_log over a cohort, EXCLUDING cells with a zero leg (PREREG 0d)."""
    keep, drop = [], []
    for g in coh:
        if CV[g] > 0.0 and CV2[g] > 0.0:
            keep.append(math.log(CV[g]) - math.log(CV2[g]))
        else:
            drop.append(int(g))
    return keep, drop


VC, DROP_C = clog_vec(COH_C)
VM, DROP_M = clog_vec(COH_M)
VU, DROP_U = clog_vec(COH_U)
ZFRAC_C = len(DROP_C) / float(len(COH_C))
ZFRAC_M = len(DROP_M) / float(len(COH_M))
log(f"[C_log] carrier {C_CAR:.4f} mirror {C_MIR:.4f} "
    f"| excluded zero cells C {len(DROP_C)} M {len(DROP_M)} U {len(DROP_U)}")


def crank_pct(coh, r_act, r_act2):
    """C_rank on the common pool coh + {actor}; actor is the LAST element."""
    am = [CV[g] for g in coh] + [r_act["R"]]
    ad = [CV2[g] for g in coh] + [r_act2["R"]]
    rm, rd = rankvec(am), rankvec(ad)
    n = float(len(am))
    cr = [(rm[i] - rd[i]) / n for i in range(len(am))]
    return pct_of(cr[-1], cr[:-1]), cr[-1], cr[:-1]


# ---------------- BRANCH (registered order; the escape SHORT-CIRCUITS) ------
PRIMARY = None
if ZFRAC_C > ZERO_FRAC_BAR:
    BRANCH223 = "S_ZERO_DEGENERATE"
    PRIMARY = "C_rank (switched by the registered 0d escape)"
    _pc_car, _cr_car, _crv = crank_pct(COH_C, R_CAR, R_CAR2)
    _pc_mir, _cr_mir, _ = crank_pct(COH_M, R_MIR, R_MIR2)
    o["Q223_1_primary"] = dict(
        escape="S_ZERO_DEGENERATE: C_log is undefined on too much of the "
               "cohort, so the C_log legs were NOT read (control flow skipped "
               "them, not a flag - the L222 lesson).",
        zero_frac_COH_C=ZFRAC_C, bar=ZERO_FRAC_BAR,
        carrier_pct_rank=_pc_car, mirror_pct_rank=_pc_mir,
        carrier_C_rank=_cr_car, mirror_C_rank=_cr_mir)
    PCT_LOG_CAR = None
    PCT_LOG_MIR = None
else:
    PRIMARY = "C_log percentile vs COH_C"
    PCT_LOG_CAR = pct_of(C_CAR, VC)
    PCT_LOG_MIR = pct_of(C_MIR, VM)
    PCT_LOG_CAR_U = pct_of(C_CAR, VU)
    PCT_LOG_MIR_U = pct_of(C_MIR, VU)
    if RHO["COH_C"] is not None and RHO["COH_C"] >= RHO_DEGEN_BAR:
        BRANCH223 = "S_DEGENERATE"
    elif PCT_LOG_CAR <= PCT_BAR:
        BRANCH223 = "S_SPECIFIC"
    else:
        BRANCH223 = "S_GENERIC"
    o["Q223_1_primary"] = dict(
        carrier_C_log=C_CAR, mirror_C_log=C_MIR,
        carrier_pct_own_cohort=PCT_LOG_CAR, mirror_pct_own_cohort=PCT_LOG_MIR,
        carrier_rank_of_cohort=int(1 + sum(1 for v in VC if v < C_CAR)),
        mirror_rank_of_cohort=int(1 + sum(1 for v in VM if v < C_MIR)),
        n_scored_carrier=len(VC), n_scored_mirror=len(VM),
        excluded_zero_carrier=len(DROP_C), excluded_zero_mirror=len(DROP_M),
        zero_frac_COH_C=ZFRAC_C, zero_frac_COH_M=ZFRAC_M,
        bar=PCT_BAR,
        note="C_log(g) = log R_motor(g) - log R_desc(g). COHORT-FREE by "
             "construction: a cell's value cannot move when the comparison "
             "set moves (L222's cohort-relocation law applied prophylactically)")
    o["Q223_2_homolog_and_common"] = dict(
        carrier_pct_union=PCT_LOG_CAR_U, mirror_pct_union=PCT_LOG_MIR_U,
        n_scored_union=len(VU), excluded_zero_union=len(DROP_U),
        d_pct_own=PCT_LOG_MIR - PCT_LOG_CAR,
        d_pct_union=PCT_LOG_MIR_U - PCT_LOG_CAR_U,
        cohort_free_d_C_log=C_MIR - C_CAR,
        cohort_free_ratio=math.exp(C_MIR - C_CAR),
        note="L222's companion set: the OWN-cohort reading, the COMMON-cohort "
             "(union) reading and the COHORT-FREE raw values, all three "
             "reported so a cohort relocation cannot flip the sign unseen.")
o["branch"] = BRANCH223
o["primary_currency"] = PRIMARY
log(f"[BRANCH] {BRANCH223} (primary = {PRIMARY})")

# ---------------- Q223-3 companion currency ---------------------------------
PC_RANK_CAR, CR_CAR, CRV_C = crank_pct(COH_C, R_CAR, R_CAR2)
PC_RANK_MIR, CR_MIR, CRV_M = crank_pct(COH_M, R_MIR, R_MIR2)
o["Q223_3_companion_rank"] = dict(
    carrier_C_rank=CR_CAR, mirror_C_rank=CR_MIR,
    carrier_pct_rank=PC_RANK_CAR, mirror_pct_rank=PC_RANK_MIR,
    agreement_carrier=(None if PCT_LOG_CAR is None
                       else abs(PCT_LOG_CAR - PC_RANK_CAR)),
    agreement_mirror=(None if PCT_LOG_MIR is None
                      else abs(PCT_LOG_MIR - PC_RANK_MIR)),
    pool_n=len(COH_C) + 1,
    note="C_rank = (midrank_motor - midrank_desc)/n on the common pool "
         "cohort + {actor}; reported beside C_log because L218 measured the "
         "same cell landing on OPPOSITE sides of the same null under two "
         "currencies of one quantity.")
log(f"[Q223-3] pct_rank carrier {PC_RANK_CAR:.3f} mirror {PC_RANK_MIR:.3f}")

# ---------------- Q223-4 descriptive ----------------------------------------
_q = lambda v, p: float(np.quantile(np.asarray(v, dtype=float), p))
o["Q223_4_descriptive"] = dict(
    cohort_C_log_min=_q(VC, 0.0), cohort_C_log_p05=_q(VC, 0.05),
    cohort_C_log_median=_q(VC, 0.5), cohort_C_log_p95=_q(VC, 0.95),
    cohort_C_log_max=_q(VC, 1.0),
    cohort_C_log_mean=float(np.mean(VC)), cohort_C_log_sd=float(np.std(VC)),
    cohort_C_rank_median=float(np.median(CRV_C)),
    ratio_of_medians_log=float(
        math.log(o["Q1_primary"]["cohort_median_carrier"])
        - math.log(o["Q2_secondary_descriptive"]["cohort_median_carrier"])),
    carrier_z_in_cohort=float((C_CAR - np.mean(VC)) / np.std(VC)),
    mirror_z_in_cohort=float((C_MIR - np.mean(VM)) / np.std(VM)),
    mass_match_logspread_carrier=o["Q1_primary"]["mass_match_logspread_carrier"],
    mass_match_logspread_mirror=o["Q1_primary"]["mass_match_logspread_mirror"],
    note="ratio_of_medians_log is the OBSERVED-DERIVABLE quantity (PREREG 0e) "
         "and is reported beside the median of ratios precisely because they "
         "are not the same number.")

# ---------------- predictions ------------------------------------------------
P = {}
P["Q223_1"] = dict(registered="S_SPECIFIC", measured=BRANCH223,
                   correct=bool(BRANCH223 == "S_SPECIFIC"))
_r = RHO["COH_C"]
P["Q223_2"] = dict(registered="rho(COH_C) in [0.40, 0.95)", measured=_r,
                   correct=bool(_r is not None and 0.40 <= _r < 0.95))
P["Q223_3"] = dict(registered="carrier C_log pct < mirror C_log pct",
                   measured=dict(carrier=PCT_LOG_CAR, mirror=PCT_LOG_MIR),
                   correct=bool(PCT_LOG_CAR is not None
                                and PCT_LOG_CAR < PCT_LOG_MIR))
P["Q223_4"] = dict(registered="excluded-zero count over COH_C <= 2",
                   measured=len(DROP_C), correct=bool(len(DROP_C) <= 2))
P["Q223_5"] = dict(registered="|pct_log - pct_rank| <= 0.10 for the carrier",
                   measured=(None if PCT_LOG_CAR is None
                             else abs(PCT_LOG_CAR - PC_RANK_CAR)),
                   correct=bool(PCT_LOG_CAR is not None
                                and abs(PCT_LOG_CAR - PC_RANK_CAR) <= 0.10))
P["Q223_6"] = dict(registered="mirror C_log pct > 0.10 (the twin is NOT specific)",
                   measured=PCT_LOG_MIR,
                   correct=bool(PCT_LOG_MIR is not None and PCT_LOG_MIR > PCT_BAR))
o["predictions"] = P
o["n_predictions_correct"] = int(sum(1 for v in P.values() if v["correct"]))
log(f"[predictions] {o['n_predictions_correct']}/{len(P)} correct")

o["design"] = ("L223 the READOUT-SPECIFICITY claim nulled properly: is the "
               "v783 DNp33 carrier unusual in its motor-vs-descending "
               "CONTRAST, scored in the cohort's OWN joint distribution? "
               "Static, zero rollouts.")
o["prereg"] = "l223/PREREG.md"
o["observed_derivable_DESCRIPTION"] = dict(
    note="PREREG 0e / Kriegeskorte 2009: l212/static.json was read while "
         "scoping, so the actors' R values in BOTH legs, hence both C_log "
         "values and their difference, and both cohort MEDIANS (hence the "
         "ratio-of-medians) were derivable before measurement and carry NO "
         "branch. Every branch sits on the cohort's per-cell JOINT "
         "distribution, its rho, and the percentiles of a contrast - none of "
         "which are determined by the stored summary.",
    carrier_C_log=C_CAR, mirror_C_log=C_MIR)
o["limitations"] = [
    "v783's cohort mass match is LOOSE (log-spread 0.316 / 0.349 against the "
    "0.15 bar L212 registered and FAILED, Q212-5) - every percentile here "
    "inherits that looseness; stated, not repaired.",
    "v783 is BRAIN-ONLY. L222 measured that ALL in-brain out-edges of BOTH "
    "actors sit below synapse 4, so the descending readout is a within-volume "
    "stand-in for 'everything else this cell talks to', not the cell's real "
    "output targets.",
    "COH_C is 100 cells, so one cell is one percentile point (L207's "
    "resolution law): a 0.10 bar cannot separate 0.10 from 0.11.",
    "ANATOMICAL leg only: no row mask, no settle, no seed, no rollouts - "
    "wiring geometry, NOT an operating point (L164). Operator powers are "
    "walks WITH revisits, not paths.",
    "The contrast cancels readout SIZE only to the extent that size enters "
    "every cell's two legs the same way; it does not cancel a readout-specific "
    "DEGREE structure. L233 is the card that asks that question directly.",
]
o["pins"] = "ALL GREEN"
o["runtime_s"] = time.time() - T0
json.dump(o, open(f"{OUT}/static.json", "w"), indent=1)
log(f"[done] {o['runtime_s']:.1f}s -> {OUT}/static.json  branch={BRANCH223}")
