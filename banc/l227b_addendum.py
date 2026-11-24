#!/usr/bin/env python3
"""l227b_addendum.py — POST-HOC, UNREGISTERED, declared. No branch, no bar,
no prediction. PURE ARITHMETIC on values already certified by
l227_static.py, read from l227/static.json (read-only, fingerprinted).
Exactly ONE write: l227/addendum.json.

Why it exists: the parent's auto-generated `rule.one_line` recommends the
SIGN comparison at the crossing — where the parent's own stored field says
that comparison has power 0.075. A branch defined on a CROSSING of two
power curves cannot answer "at what mirror does MY instrument stop
working" (L225's law: a branch defined on one object cannot answer a
question about another). This addendum ASSERTS that contradiction against
stored fields rather than describing it.
"""
import json, os
import numpy as np

B = "/home/t3rpz/critters/peabrain-lab/banc/"
P = B + "l227/static.json"
st0 = os.stat(P)
S = json.load(open(P))

OUT = {"label": ("POST-HOC, UNREGISTERED, ARITHMETIC ONLY on values already "
                 "certified by l227_static.py. No branch depends on it."),
       "cert": {}, "contradiction": {}, "power_floor": {}, "retro": {},
       "rule_v2": {}}

# ===== CERT-227: the parent's branch-bearing values, float equality =====
_n = 0


def _eq(a, b, w):
    global _n
    assert a == b, f"CERT-227 {w}: {a!r} != {b!r}"
    _n += 1


_eq(S["branch"]["verdict"], "M_CROSSES", "branch")
_eq(S["predictions"]["P3_threshold_le_0.6767"], False, "P3 false")
_eq(S["predictions"]["P2_mag_power_zero_at_lam1"], True, "P2 true")
_eq(S["pairs"]["lvl_vs_margin"]["klass"], "C_ANALYTIC_MIRROR", "pair1")
_eq(S["pairs"]["flo_vs_fhi"]["klass"], "C_DEGENERATE", "pair2")
_eq(S["pairs"]["A_vs_dM"]["klass"], "C_EMPIRICAL_NEAR_MIRROR", "pair3")
_eq(S["pairs"]["duty_vs_Smean"]["agg_branch"], "A_ROUNDED", "pair4")
_mr4 = S["pairs"]["duty_vs_Smean"]["mirror_r"]
# NOT == 1.0: the stored means are rounded to 3 decimals, which manufactures
# TIES the unrounded means do not have, and a midrank Spearman on a tied
# vector cannot reach 1. Asserted as a BRACKET (strictly stronger than the
# equality it replaces) and the mechanism is counted below from the sources.
assert 0.9999 < _mr4 < 1.0, f"pair4 mirror out of bracket: {_mr4}"
_n += 1
cal = S["sim"]["grid"]["cal"]
fx = S["sim"]["grid"]["fixed50"]
_eq(len(cal), 11, "grid len")
_eq(cal[-1]["power_mag"], 0.0, "lam1 MAG power")
_eq(cal[-1]["max_abs_dv"], 0.0, "lam1 diff identically zero")
R = S["rule"]
_eq(R["retro_flags_L214_Q3"], False, "retro flag")
for k in ("X_lam", "X_abs_r_rho", "power_mag_at_X", "power_sgn_at_X",
          "X50_lam", "X50_abs_r_rho", "measured_pair_abs_r_rho"):
    assert isinstance(R[k], float), k
    _n += 1
OUT["cert"]["cert_227"] = _n

# ===== (A) the tie mechanism behind pair4's 0.99998, counted from the sources
_l200 = json.load(open(B + "l200/results_l200.json"))
_l202 = json.load(open(B + "l202/results_l202.json"))
_raw, _st = [], []
for dd in (_l200, _l202):
    for arm, v in dd["arms"].items():
        for side in ("L", "R"):
            if v.get("duty" + side) is None or v.get("mean" + side) is None:
                continue
            _raw.append(float(np.mean(np.array(v["duty" + side], dtype=float))))
            _st.append(float(v["mean" + side]))
assert len(_raw) == S["pairs"]["duty_vs_Smean"]["n_units"], "unit count drift"
_nd_raw, _nd_st = len(set(_raw)), len(set(_st))
assert _nd_st < _nd_raw, "rounding did not create ties"
OUT["pair4_tie_mechanism"] = {
    "n_units": len(_raw), "n_distinct_unrounded_means": _nd_raw,
    "n_distinct_stored_means": _nd_st, "mirror_r": _mr4,
    "reading": ("The stored means are 3-decimal rounded, so %d distinct "
                "unrounded values collapse to %d distinct stored values. The "
                "relation is a perfect monotone aggregation, yet its midrank "
                "Spearman reads %.7f rather than 1: ROUNDING A STORED VALUE "
                "MANUFACTURES TIES, and ties cap a rank correlation below its "
                "analytic value. Same law as 0h, from the opposite direction."
                % (_nd_raw, _nd_st, _mr4)),
}

# ===== (B) the contradiction, ASSERTED =====
pm_X, ps_X = R["power_mag_at_X"], R["power_sgn_at_X"]
assert pm_X < ps_X, "crossing definition broken"
assert ps_X < 0.20, f"SGN at the crossing is not near-powerless: {ps_X}"
sgn_max = max(r["power_sgn"] for r in cal)
assert sgn_max <= 0.20, f"SGN tops out above 0.20: {sgn_max}"
OUT["contradiction"] = {
    "parent_rule_recommends": "the SIGN comparison at |r_rho| >= %.3f" % R["X_abs_r_rho"],
    "power_sgn_at_that_threshold": ps_X,
    "power_mag_at_that_threshold": pm_X,
    "power_sgn_max_over_grid": sgn_max,
    "reading": ("The crossing is a statement about the SIGN test's weakness, "
                "not about the magnitude test's adequacy: at the crossing the "
                "recommended instrument has power %.3f. A threshold derived "
                "from where two power curves CROSS is reported in units of the "
                "WEAKER instrument and therefore answers a different question "
                "than 'at what mirror does my instrument stop working'."
                % ps_X),
}

# ===== (B) the power floor, and its EFFECT-SIZE dependence =====
def floor_at(rows, bar):
    prev = None
    for r in rows:
        if r["power_mag"] < bar:
            return dict(lam=r["lam"], abs_r_rho=abs(r["r_rho"]),
                        power_mag=r["power_mag"],
                        prev_lam=(prev["lam"] if prev else None))
        prev = r
    return None


f50_cal, f50_fx = floor_at(cal, 0.50), floor_at(fx, 0.50)
f80_cal, f80_fx = floor_at(cal, 0.80), floor_at(fx, 0.80)
OUT["power_floor"] = {
    "bar_0.50": {"calibrated_beta": f50_cal, "beta_0.50": f50_fx},
    "bar_0.80": {"calibrated_beta": f80_cal, "beta_0.80_arm": f80_fx},
    "beta_calibrated": S["sim"]["beta_calibrated"],
    "mean_absrhoA_cal": cal[0]["mean_absrhoA"],
    "mean_absrhoA_fixed50": fx[0]["mean_absrhoA"],
    "reading": ("The |mirror r| at which the magnitude test loses half its "
                "power is %.4f at the lane's own measured effect size and "
                "%.4f at beta = 0.50 — a factor of %.2f. So the card's "
                "requested ONE-LINE RULE does not exist as a single number: "
                "the threshold is a 2-D condition in (mirror, effect size). "
                "The only mirror-ONLY statement that is unconditional is the "
                "analytic one: at |r| = 1 the magnitude test has EXACTLY zero "
                "power (measured: max|diff| == 0.0, p_D == 1 in every draw)."
                % (f50_cal["abs_r_rho"], f50_fx["abs_r_rho"],
                   f50_fx["abs_r_rho"] / f50_cal["abs_r_rho"])),
}

# ===== (C) the retro-read of L214's Q3, by POWER rather than by crossing =====
mr = R["measured_pair_abs_r_rho"]
xs = [abs(r["r_rho"]) for r in cal]
ys = [r["power_mag"] for r in cal]
pw = float(np.interp(mr, xs, ys))
OUT["retro"] = {
    "measured_abs_r_rho": mr,
    "interp_power_mag_at_measured_mirror": pw,
    "bracketing_grid": [{"abs_r_rho": xs[i], "power_mag": ys[i]}
                        for i in range(len(xs))
                        if i + 1 < len(xs) and xs[i] <= mr <= xs[i + 1]
                        or (i > 0 and xs[i - 1] <= mr <= xs[i])],
    "l214_q3_branch": "H_TIE",
    "reading": ("At the measured mirror coefficient and the lane's own effect "
                "size, the magnitude head-to-head was running at about %.0f%% "
                "power. L214's Q3 therefore read H_TIE at roughly one-quarter "
                "power: 'tie' was never distinguishable from 'difference' on "
                "that data. This IS the retro-flag the card expected — but it "
                "is delivered by POWER AT THE MEASURED MIRROR, not by the "
                "crossing criterion the card implicitly assumed, which the "
                "measured pair does NOT reach (%.3f < %.3f). The card's "
                "registered expectation is false as stated and true in "
                "substance, and the two differ precisely because a crossing "
                "threshold depends on the rival instrument."
                % (100 * pw, mr, R["X_abs_r_rho"])),
}

# ===== (D) the rule as it should actually be written =====
OUT["rule_v2"] = {
    "pre_step": [
        "1. Name which currency each candidate instrument CONSUMES (a "
        "mean-|rho| statistic consumes the per-cell correlations; a "
        "sign-agreement statistic consumes the per-cell currency means). "
        "Compute the mirror coefficient in THAT currency, with AVERAGE "
        "(midrank) ranks.",
        "2. If the two currencies are related by a strictly monotone map "
        "(check the definitions, not the data), the magnitude head-to-head "
        "has exactly zero power: do not register it. This is a PROOF and it "
        "fires before any measurement.",
        "3. Otherwise compute the ACHIEVED POWER of the magnitude test at the "
        "measured mirror AND the measured effect size (a 20-cell, 16-seed "
        "simulation costs seconds). Register the magnitude test only if that "
        "power clears a stated bar.",
        "4. If it does not, the honest verdict on a null result is "
        "'underpowered instrument', never 'tie' — and the remedy is more "
        "cells or a different statistic, NOT automatically the sign "
        "comparison, whose own power at n = 20 topped out at %.3f across the "
        "whole mirror grid." % sgn_max,
    ],
    "supersedes": "l227/static.json rule.one_line (crossing-based, misleading)",
}

st1 = os.stat(P)
assert (st0.st_size, st0.st_mtime_ns) == (st1.st_size, st1.st_mtime_ns), "parent moved"
json.dump(OUT, open(B + "l227/addendum.json", "w"), indent=1)
print("CERT-227", OUT["cert"]["cert_227"], "checks")
print("A) contradiction: parent rule recommends SGN at |r_rho| >= %.3f where "
      "SGN power = %.3f (MAG %.3f); SGN max over grid %.3f"
      % (R["X_abs_r_rho"], ps_X, pm_X, sgn_max))
print("B) power floor .50:  cal beta=%.4f -> |r| %.4f (lam %.2f) | beta=.50 -> "
      "|r| %.4f (lam %.2f)" % (S["sim"]["beta_calibrated"], f50_cal["abs_r_rho"],
                               f50_cal["lam"], f50_fx["abs_r_rho"], f50_fx["lam"]))
print("   power floor .80:  cal -> |r| %.4f | beta=.50 -> |r| %.4f"
      % (f80_cal["abs_r_rho"], f80_fx["abs_r_rho"]))
print("C) retro: measured |r_rho| %.4f -> MAG power %.3f ; L214 Q3 H_TIE read "
      "at that power. crossing NOT reached (%.3f < %.3f)."
      % (mr, pw, mr, R["X_abs_r_rho"]))
print("D) rule_v2 written (4 steps), supersedes the parent's one_line.")
print("L227b DONE")
