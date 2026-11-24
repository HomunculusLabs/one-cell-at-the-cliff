
# ===================== L223b ADDENDUM (POST-HOC, declared) ================
# Q223-5 FAILED: the carrier's two currencies disagree by 0.1496 of a
# percentile (C_log .0404 vs C_rank .1900) while the mirror's agree to 0.0134.
# This addendum asks the ONE question that decides whether that is a statement
# about the CARRIER or about the CURRENCIES, and it is POST-HOC: it was
# written after reading l223/static.json and carries NO registered branch.
#
# Everything above this line is l223_static.py lines 1-819 VERBATIM, with ONE
# declared modification (the inherited V_DEGENERATE escape at 432-436, whose
# json-dump write targets the PARENT's artifact, replaced by a halting assert), so
# this prefix contains ZERO writes and every L223 gate re-ran for free.

assert OUTB.endswith("/l223"), (OUTB, "OUT (STOP)")
a = {}
a["design"] = ("L223b POST-HOC: is the C_log / C_rank currency disagreement a "
               "property of the CARRIER or of the two currencies? Nonselective "
               "leave-one-out over the carrier's own cohort.")
a["post_hoc"] = ("Written AFTER reading l223/static.json. No branch, no bar, "
                 "no prediction - descriptive only (the L214 rule).")
a["parent_sha_checked"] = True

# ---------------- CERT-223 (HALTING): the parent's own numbers --------------
_stp = os.stat(f"{LAB}/l223/static.json")
_fpp = (_stp.st_size, _stp.st_mtime_ns)
with open(f"{LAB}/l223/static.json") as _fh:
    S223 = json.load(_fh)
n223 = 0
for _k, _v in (("carrier_C_log", C_CAR), ("mirror_C_log", C_MIR),
               ("carrier_pct_own_cohort", PCT_LOG_CAR),
               ("mirror_pct_own_cohort", PCT_LOG_MIR)):
    assert S223["Q223_1_primary"][_k] == _v, (_k, "CERT-223 (STOP)")
    n223 += 1
for _k, _v in (("carrier_pct_rank", PC_RANK_CAR), ("mirror_pct_rank", PC_RANK_MIR),
               ("carrier_C_rank", CR_CAR), ("mirror_C_rank", CR_MIR)):
    assert S223["Q223_3_companion_rank"][_k] == _v, (_k, "CERT-223 (STOP)")
    n223 += 1
for _k in ("rho_COH_C", "rho_COH_M", "rho_COH_U"):
    assert S223["Q223_0_rho_first"][_k] == RHO[_k.split("_", 1)[1]], \
        (_k, "CERT-223 rho (STOP)")
    n223 += 1
assert S223["branch"] == "S_SPECIFIC" and S223["n_predictions_correct"] == 5
n223 += 2
assert S223["cert_212"]["n_checks"] == 139 and S223["cert_pair"]["n_checks"] == 11 \
    and S223["cert_rank"]["n_checks"] == 252
n223 += 3
a["cert_223"] = dict(n_checks=n223, mode="float/int equality (==)",
                     source="l223/static.json (read-only, mtime asserted)")
log(f"[CERT-223] GREEN {n223} parent values reproduced at float equality")

# ---------------- the leave-one-out currency comparison ---------------------
# For EVERY cohort cell, score it the way the carrier was scored: its own
# C_log percentile against the OTHER cohort members, and its own C_rank
# percentile against theirs. Nonselective by construction - the carrier is
# one more point, not the subject.
_keep = [int(g) for g in COH_C if CV[g] > 0.0 and CV2[g] > 0.0]
_clog = {g: math.log(CV[g]) - math.log(CV2[g]) for g in _keep}
_am = [CV[g] for g in _keep] + [R_CAR["R"]]
_ad = [CV2[g] for g in _keep] + [R_CAR2["R"]]
_rm, _rd = rankvec(_am), rankvec(_ad)
_nn = float(len(_am))
_crank = {g: (_rm[i] - _rd[i]) / _nn for i, g in enumerate(_keep)}
_crank_car = (_rm[-1] - _rd[-1]) / _nn

ROWS = []
for g in _keep:
    _others_log = [_clog[h] for h in _keep if h != g]
    _others_rk = [_crank[h] for h in _keep if h != g]
    ROWS.append(dict(gi=g,
                     C_log=_clog[g], C_rank=_crank[g],
                     pct_log=pct_of(_clog[g], _others_log),
                     pct_rank=pct_of(_crank[g], _others_rk)))
DIS = [abs(r["pct_log"] - r["pct_rank"]) for r in ROWS]
D_CAR = abs(PCT_LOG_CAR - PC_RANK_CAR)
a["Q223b_1_disagreement_is_generic"] = dict(
    carrier_disagreement=D_CAR,
    carrier_pct_in_cohort_disagreement=pct_of(D_CAR, DIS),
    cohort_disagreement_median=float(np.median(DIS)),
    cohort_disagreement_p90=float(np.quantile(np.asarray(DIS), 0.90)),
    cohort_disagreement_max=float(np.max(DIS)),
    cohort_disagreement_mean=float(np.mean(DIS)),
    n_cohort_scored=len(ROWS),
    note="each cohort cell scored EXACTLY as the carrier was (leave-one-out "
         "against the other members), so the carrier's 0.1496 is placed in a "
         "distribution of disagreements that already exists in this cohort.")
log(f"[Q223b-1] carrier disagreement {D_CAR:.4f} at pct "
    f"{a['Q223b_1_disagreement_is_generic']['carrier_pct_in_cohort_disagreement']:.3f} "
    f"| cohort median {np.median(DIS):.4f} max {np.max(DIS):.4f}")

# ---------------- do the currencies rank the cohort the same way? -----------
_rho_cc = spearman_l([r["C_log"] for r in ROWS], [r["C_rank"] for r in ROWS])
_rho_pp = spearman_l([r["pct_log"] for r in ROWS], [r["pct_rank"] for r in ROWS])
# the compression test: |C_log| vs |C_rank| in the LOWER tail of C_log
_lo = sorted(ROWS, key=lambda r: r["C_log"])[:20]
a["Q223b_2_currency_relation"] = dict(
    spearman_C_log_vs_C_rank=_rho_cc,
    spearman_pct_log_vs_pct_rank=_rho_pp,
    lower20_mean_pct_log=float(np.mean([r["pct_log"] for r in _lo])),
    lower20_mean_pct_rank=float(np.mean([r["pct_rank"] for r in _lo])),
    lower20_mean_shift=float(np.mean([r["pct_rank"] - r["pct_log"] for r in _lo])),
    all_mean_shift=float(np.mean([r["pct_rank"] - r["pct_log"] for r in ROWS])),
    note="if the rank currency COMPRESSES the lower tail, the 20 most "
         "motor-specific cells by C_log sit systematically HIGHER in pct_rank "
         "than in pct_log, i.e. a positive lower20_mean_shift, while the "
         "cohort-wide mean shift stays ~0 by construction.")
log(f"[Q223b-2] rho(C_log,C_rank) {_rho_cc:.4f} | rho(pct,pct) {_rho_pp:.4f} "
    f"| lower-20 shift {a['Q223b_2_currency_relation']['lower20_mean_shift']:+.4f} "
    f"(all {a['Q223b_2_currency_relation']['all_mean_shift']:+.4f})")

# ---------------- would the branch have flipped? ----------------------------
a["Q223b_3_branch_under_companion"] = dict(
    registered_primary="C_log percentile vs COH_C",
    primary_pct=PCT_LOG_CAR, primary_branch="S_SPECIFIC",
    companion_pct=PC_RANK_CAR,
    companion_branch=("S_SPECIFIC" if PC_RANK_CAR <= PCT_BAR else "S_GENERIC"),
    bar=PCT_BAR,
    agree_in_direction=bool((PCT_LOG_CAR < PCT_LOG_MIR)
                            == (PC_RANK_CAR < PC_RANK_MIR)),
    note="DISCLOSED PLAINLY: the registered primary (declared in PREREG 0c "
         "BEFORE measurement) branches S_SPECIFIC; the companion currency does "
         "NOT clear the same 0.10 bar. Both order carrier BELOW mirror, so the "
         "DIRECTION is currency-invariant and the BINARY CALL is not.")
log(f"[Q223b-3] companion branch "
    f"{a['Q223b_3_branch_under_companion']['companion_branch']} "
    f"(direction agrees: {a['Q223b_3_branch_under_companion']['agree_in_direction']})")

a["rows"] = ROWS
a["limitations"] = [
    "POST-HOC: no registered bar, no prediction, no branch. Descriptive.",
    "The leave-one-out cohort is the carrier's own mass-matched cohort, which "
    "inherits L212's LOOSE mass match (log-spread 0.316 against a 0.15 bar).",
    "One cell is one percentile point in a 99-cell comparison set (L207).",
]
_stp2 = os.stat(f"{LAB}/l223/static.json")
assert (_stp2.st_size, _stp2.st_mtime_ns) == _fpp, "l223/static.json MUTATED"
a["runtime_s"] = time.time() - T0
json.dump(a, open(f"{LAB}/l223/addendum.json", "w"), indent=1)
log(f"[done] addendum -> {LAB}/l223/addendum.json")
