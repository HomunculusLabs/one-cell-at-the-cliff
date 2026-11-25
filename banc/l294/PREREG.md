# L294 PREREG -- WHAT PREDICTS A WEIGHT-MATCHED SET'S EFFECT

Frozen 2026-11-25 13:10 EST by Miso, tick 287 (LANE.md card L294). Re-taken after tick 283
(08:19) and tick 285 (10:5x) both died on HTTP 429 before any PREREG existed; neither scored
anything (their dirs hold survey scripts + structure output only).
Parents: L290 (PREREG 27b6a473bdb2f9d6, NO_DECISION) and L291 (PREREG 670e8f682e48749c,
NO_DECISION). Static re-analysis of STORED arrays. Zero rollouts.
Rule: no edit after freezing. Amendments only as new dated files. A journaled blocker is a
valid tick; a fabricated number is the only failure.

## s0 The question
L291 saw, AFTER the fact and unbanked, that across its 15 stratified arms the effect ranks with
the arm's own gain compensation (ordinal rho +0.82) against +0.20 for the raw synapse sum, and
that every arm with a negative gain delta sits at the floor. Q: is a set's effect predicted by
(a) the drive it actually removed in the NORMALISED graph, (b) the gain delta the bisection had
to apply -- or by nothing measurable from the set (a per-set lottery)?
L227, binding: dgain is a CONSEQUENCE of the cut (you must run the bisection to have it), so a
fit on dgain is a MECHANISM PROBE and at best a cheap screen, never a prediction for an unseen
set. The instrument that can separate mediator from marker is the TWIN: one set, two gains.

## s1 Declared as SEEN before this freeze (structure only; banc/l294/survey2.out, survey3.out,
## survey4.out -- none scores a covariate against an effect)
- Menu: carrier gi 1110, 69 out-edges, 69 DISTINCT targets (j->target one-to-one), every sign +1,
  0 negative weights. effective_weight = log1p(syn) to 1.06e-7 (float32). 8 no-op edges
  j in {1,2,8,9,16,21,47,55}.
- 0 of the 69 menu targets lie inside the 303-cell readout pool union (l291/pools_w0.json ==
  l290/pools_w0.json, n_union 303): the carrier reaches the pool only polysynaptically.
- Unit F = 0.00022931491480943385; eps = 2F. Seeds 3769-3784 (16). Base gain
  g_cutwA = 0.14365819573402408. Stored per arm: E (signed, pool mean minus cutwA, mean of 16
  seeds), in_F = E/F, gain, syn_sum, eff, has14.
- Stored xmean_{arm}_{seed} arrays (21,785 cells = whole-window mean rate per cell) exist for
  every arm in both dirs; the pool union ids index into that vector (checked by the script's gate
  G2b before anything is read).
- ALREADY-OBSERVED relations on these arms (therefore DESCRIPTION here, never re-tested):
  DGAIN x E ordinal +0.82 pooled over L291-15 (L291 VERDICT); SYN x E +0.20 (L291-15 ordinal)
  and +0.59 (L290-15, stored rho_E_synsum_random 0.5892857142857143); eff x E +0.09 (L291-15,
  stored rho_E_eff_strat) and +0.43 (L290-15, stored 0.4286057678550518); e14 cell means with /
  without: +5.64 / +4.07 (n 11), +8.31 / +0.02 (30), +11.72 / -2.90 (46) F (stored `means`);
  twin differences in F: gc30 1.37, gh46 3.28 (L291), e14 1.69, e25 4.55, e67 0.52, e12 1.93,
  e27 1.93 (L290 `twins`).
- NEVER scored anywhere: dgain against E on L290's 18 arms; ANY within-size-stratum form;
  the effective-weight SUM; the twin difference against the SIGN of dgain; any non-pool readout.

## s2 Populations (all stored, same seeds, same cutwA lineage)
- B33 = 33 BISECTED arms: L291's 15 stratified (s11*/s30*/s46*) + L290's 15 uniform (r11k*/r30k*/
  r46k*) + its 3 heaviest-synapse sets (rw11, rw30, rw46). Strata by set size n: 11 -> 10 arms,
  30 -> 11, 46 -> 11. A fixed-gain arm has no bisection, so dgain = 0 there is a convention, not
  a measurement: the fixed twins are NOT in B33.
- L18 = L290's 18 arms alone (6 per stratum): the clean out-of-sample test of the L291 pattern.
- TW7 = 7 twin pairs (same set, same seeds, same cutwA; bisected arm vs fixed-gain arm):
  (gc30, gc30f), (gh46, gh46f) [L290 bisected, L291 fixed]; (e14, e14f), (e25, e25f),
  (e67, e67f), (e12, e12f), (e27, e27f) [all L290].
- CARD35 companion (the card's literal population) = B33 + gc30f + gh46f at dgain = 0: reported
  for T2 only, never gating.

## s3 Covariates (definition-first; computed from arms_w*.json `edges[arm].removed` + the menu)
- EW_SUM = sum_i log1p(syn_i) over the removed edges ("the drive removed in the normalised
  graph"). It is a concave MIRROR of SYN (raw synapse sum): the mirror coefficient
  rho_mid(EW_SUM, SYN) over B33 is reported BEFORE any reading of T3 (L227).
- EW_POS / EW_NEG (sign-split): EW_NEG is identically 0 (0 of 69 negative) -> UNMEASURABLE BY
  DEFINITION, scored as such, never dropped silently. EW_POS == EW_SUM.
- NTGT (distinct removed targets) is identically n on this menu -> within a stratum it is a
  constant: UNMEASURABLE BY DEFINITION within stratum; pooled it IS the stratum.
- NTGT_POOL (distinct removed targets inside the pool union) is identically 0 -> UNMEASURABLE.
- DGAIN = bisected gain - g_cutwA (stored `gain`; L291 also stores `dgain`; the two must agree to
  0.0 for L291 arms -- gate G3).
- E14 = membership (0/1): DESCRIPTION only (s1).
- NEFF = eff (n minus no-op edges): DESCRIPTION only (s1).

## s4 Statistics (midrank Spearman everywhere -- average ranks, L221; argsort only to reproduce
## the +0.82 anchor, where both variables have 15 distinct values)
STRAT-RHO(x, y) = sum_s w_s rho_s, w_s = (n_s - 1) / sum(n_s - 1), rho_s the within-stratum
midrank Spearman. Per-stratum rho_s are stored beside it. Null: covariate labels permuted WITHIN
stratum, B = 20,000, rng numpy Generator(PCG64(29400)); p_two = (1 + #{|rho_perm| >= |rho_obs|})/(B + 1).
Degeneracy guard: a stratum with fewer than 4 distinct covariate values is UNMEASURABLE and
drops out of the mean with its weight renormalised; fewer than 2 readable strata -> the test is
UNMEASURABLE (not a non-rejection).

FAMILY (m = 6), BH at q = 0.10:
 T1  STRAT-RHO(E, DGAIN) on L18.              sign predicted +
 T2  STRAT-RHO(E, DGAIN) on B33.              sign predicted +   (CARD35 companion reported)
 T3  STRAT-RHO(E, EW_SUM) on B33.             sign predicted + ; predicted NOT to clear p 0.05
 T4  TWIN leg, TW7: S = mean_i sign(dgain_i) * dE_i, dE_i = E_bisected,i - E_fixed,i (F).
     Null: each dE_i sign-flipped independently, all 2^7 = 128 patterns, exact.
     p_one = #{S_null >= S_obs} / 128. Concordance count stored beside it (L233: a 7-unit sign
     count resolves no better than 1/128 at 7/7 and 8/128 at 6/7, so it cannot carry the branch).
 T5  STRAT-RHO(E_CTRL, DGAIN) on B33.  E_CTRL,a = same readout as E but over the 21,482 cells
     OUTSIDE the pool union: does the rest of the network move with dgain? (the GLOBAL-SHIFT
     confound named before the DGAIN legs are read)
 T6  STRAT-RHO(E_DIFF, DGAIN) on B33.  E_DIFF,a = mean_s [(P_a - P_cutwA) - (C_a - C_cutwA)]:
     the pool's shift MINUS the common shift. Removes a common ADDITIVE shift only; it is not a
     multiplicative control (a log-ratio form is reported as description, never gating).

## s5 Registered reading (in this order)
 1. CONFOUND FIRST. T5 significant -> G_SHIFT_ON: the non-pool network moves with dgain, so part
    of any DGAIN->E association is a shift the pool shares. The surviving share is reported as
    (T2 rho - T6 rho)/T2 rho, description only. T5 not significant -> G_SHIFT_OFF.
 2. TWIN INSTRUMENT. T4 p_one <= 0.05 and S > 0 -> TWIN_GAIN (with the set held fixed, moving
    only the gain moves the pool in dgain's direction: the gain is a within-set MEDIATOR).
    Otherwise TWIN_FAIL (dgain is at most a MARKER between sets).
 3. VERDICT (first match):
    A  GAIN_DELTA_MEDIATED: T1 and T2 both q <= 0.10 with sign +, AND TWIN_GAIN.
       Sub-label A_COMMON if T6 is not significant, A_POOL_SPECIFIC if it is.
    B  GAIN_DELTA_MARKER:   T1 and T2 both q <= 0.10 with sign +, and TWIN_FAIL.
    C  WEIGHT_CARRIES:      T3 q <= 0.10 (sign +) while T1 or T2 fails.
    D  LOTTERY:             T1, T2 and T3 all fail q <= 0.10.
    else NO_DECISION.
Predictions, registered before any test is computed:
 P1 T1 sign +, p_two <= 0.05.      P2 T2 sign +, p_two <= 0.05.
 P3 T4 S > 0, p_one <= 0.05.       P4 T5 q <= 0.10.
 P5 T3 p_two > 0.05 (weight does not carry). 
 P6 All six anchors of s6 reproduce inside their tolerances.

## s6 Gates (a failure HALTS before any test is printed or written)
 G1 stored shapes: 15 + 18 + 2 arms present in both results files; every arm has 16 per_seed
    values and E == mean(per_seed) to 1e-15.
 G2 re-derivation from the npz: E for all 35 arms + gc30 + gh46 recomputed from
    xmean_{arm}_{seed} over the pool union, per worker against that worker's own cutwA arrays;
    |E_rederived - E_stored| <= 2e-9 for every arm.
 G2b index-space check: for one arm per worker the mean of a stored pool TRACE equals the mean
    over that pool's cells of xmean (rtol 1e-4).
 G3 covariate provenance: set j-list targets == `removed` targets; sum(syn) == stored syn_sum;
    EW_SUM from the menu == sum of stored effective_weight to 1e-5; L291 `dgain` == gain -
    g_cutwA to 0.0.
 G4 ANCHORS (the prior cards' own numbers, re-derived here): DGAIN x E ordinal on L291-15
    = 0.82 +/- 0.005; SYN x E on L290-15 = 0.5892857142857143 +/- 1e-12; eff x E on L290-15
    = 0.4286057678550518 +/- 1e-12; L291 cell means with/without within 0.005 F of s1.
 G5 the results file carries this file's sha256; the script refuses to run if PREREG.sha256 is absent.

## s7 Compute, writes, honesty
Static, read-only on l290/ l291/ and every other prior dir; nice +15; writes confined to
banc/l294/. sessions/ never read. The fly duck is never touched (PID, NRestarts, /needs probed
before and after). sessions/ and live modules untouched. One carrier, one substrate, one gain
family, 16 seeds reused across every arm: L291's 15 and L290's 18 share seeds and cutwA, so L18
is out-of-sample in SETS, not in seeds. Midrank on 10-11 arms per stratum is a low-power
instrument; a non-rejection is read as NOT SHOWN, never as absent.
