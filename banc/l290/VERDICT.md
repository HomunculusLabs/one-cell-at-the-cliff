# L290 stage B -- VERDICT (tick 278, 2026-11-25 00:26 EST)

**Branch (PREREG s5, first match): NO_DECISION** -- the registered else-branch. Not (a) ESCAPE,
not (b) WINS, not (c) I_INSTRUMENT_AT_GROUP. Unit F = 2.2931e-4 (A1 noise-twin SD/4); eps = 2F.
Read strictly under PREREG sha256 `27b6a473bdb2f9d6` (frozen 2026-11-24 22:32:17 EST).

## Why each registered branch did not fire

- **(a) ESCAPE -- no.** Two used-sets beat several random subsets, and the Crofts set is beaten
  by two. Only the abs set beats everything it was compared with.
- **(b) WINS -- no.** The raw leg fails for every metric: abs beats the 11 heaviest edges by
  +2.92 F with p_up 0.0078 (bar 0.001); Crofts-30 vs the 30 heaviest: -0.53 F (WITHIN);
  hop-46 vs the 46 heaviest: -0.97 F (WITHIN).
- **(c) I_INSTRUMENT_AT_GROUP -- no.** 9 of 15 random arms clear 2F (the bar is "fewer than 8").
  The null's support is adequate: 3 of 5 at each size.

| metric | used-set arm | E | vs raw comparator | random subsets EXCEEDED | random subsets that EXCEED it | label |
|---|---|---|---|---|---|---|
| abs (11) | g11 (A1 stored) | +4.34 F | rw11: +2.92 F, p 0.0078 EXCEEDS | 5 of 5 | 0 | NO_CLEAN_RESULT |
| Crofts (30, eff 28) | gc30 | +8.73 F | rw30: -0.53 F WITHIN | 3 of 5 | 2 (r30k1 -3.17 F, r30k3 -3.48 F) | NO_CLEAN_RESULT |
| hop (46, eff 43) | gh46 | +9.15 F | rw46: -0.97 F WITHIN | 4 of 5 | 0 (r46k3 +0.48 F WITHIN) | NO_CLEAN_RESULT |

Advantage A = sign(E_U) * D over 16 paired seeds, exact 2^16 sign-flip test, arm-vs-arm.
CI of E: g11 [6.90e-4, 1.30e-3] (15/16 seeds), gc30 [1.68e-3, 2.33e-3] (16/16),
gh46 [1.74e-3, 2.46e-3] (16/16). Raw comparators themselves: rw11 +1.42 F, rw30 +9.26 F,
rw46 +10.12 F.

**The load-bearing observation (registered quantities, no branch):** at 30 and 46 edges the
metric's set and the heaviest-synapse set land within 1 F of each other, and random subsets
that contain e14 reach the same level or higher (r30k1 +11.90 F, r30k3 +12.22 F). At this
carrier the length metric does not pick out a group that behaves differently from heavy edges
or from an e14-bearing random subset of the same size.

## Random arms (the null's support)

| size | arm: E in F (e14) | clear 2F |
|---|---|---|
| 11 | r11k1 +0.99, r11k2 -4.34, r11k3 -2.22, r11k4 -4.69, r11k5 +1.74 (none has e14) | 3 of 5, all NEGATIVE |
| 30 | r30k1 +11.90 (e14), r30k2 +2.91, r30k3 +12.22 (e14), r30k4 -1.62, r30k5 -0.23 | 3 of 5 |
| 46 | r46k1 +3.87 (e14), r46k2 +1.92 (e14), r46k3 +8.67 (e14), r46k4 -1.89, r46k5 +4.77 | 3 of 5 |

9 of 15 clear; with e14 4 of 5; without e14 5 of 10.

## Predictions: 0 of 8 (score 0)

- S1 FALSE: |RW_11 ^ U_abs| = 3 (predicted 7-10). S2 FALSE: e14 is not among the 11 heaviest.
- N1 FALSE: exact no-ops inside U_crofts = 2 (e21, e55; inside 2-4), inside U_hop = 3
  (e21, e47, e55; predicted 4-6).
- R1 FALSE: 4 of 5 e14-containing random subsets clear; 5 of 10 e14-free subsets clear (<= 1 predicted).
- R2 FALSE: E(g11) +9.96e-4, E(gc30) +2.00e-3, E(gh46) +2.10e-3 against E(e14) +1.25e-3 -- the two
  larger groups exceed the single edge's effect by 3.3 F and 3.7 F (bar 2 F).
- R3 FALSE (verdict is not I_INSTRUMENT). R4 FALSE (9 >= 8). R5 FALSE (3 of 5 twins).

## Companion branches (reported beside the verdict; never override it)

- (d) SINGLE-EDGE CARRIER: FALSE. Of 5 e14-containing random subsets, 1 is within eps of its
  used-set (r46k3), 2 exceed it (r30k1, r30k3) and 2 sit 5.3 F and 7.2 F below hop-46 (r46k1,
  r46k2). All 10 e14-free subsets sit below their used-set by >= eps.
- (e) INSTRUMENT WITHOUT e14: TRUE -- 5 of 10 e14-free subsets clear the floor (>= 4).
- (f) EDGE NOT GAIN: FALSE -- 3 of 5. Fixed-gain twin vs re-bisected arm (E in F):
  e14f +3.77 vs +5.46; e67f -1.01 vs -1.53; e27f +0.98 vs +2.91 (concordant, within 2 F).
  e25f -4.48 vs +0.07 (sign flip, 4.55 F apart; its bisect had moved the gain by +8.5e-4) and
  e12f +1.72 vs -0.21 (sign flip, 1.93 F apart; bisect -9.4e-4). For these two edges the
  "single-edge effect" measured in L240 depended on the re-bisected operating point.

## Descriptive (non-branching)

Mean E of random arms with e14 +1.77e-3 (+7.7 F), without e14 -1.05e-4 (-0.46 F).
Over the 15 random arms: Spearman(E, effective size) +0.43, Spearman(E, synapse sum) +0.59.
e14's share of the sum of its used-set's SINGLE effects: abs 100 %, Crofts 49 %, hop 32 %
(R = G/S = 0.80 / 0.78 / 0.54). Raw-comparator boundary ties left out: 0 / 0 / 0.

## Certification

Three `exit_w*` files all 0 (1150 / 1200 / 1296 s, hard stop 1700); PREREG, sets
(`0a48800bdcec39ca`) and harness (`4c60ce6e8e81029b`) sha256 asserted at analysis; every L290
cutwA array bit-identical to A1's STORED traces (532 arrays per worker: control-cell, pool,
mm/xm/af/xwin), 7,196 control-cell trace arrays + 35,980 pool traces finite across the 13
workers read (A1 3, A2 7, L290 3); gains inside [.12, .18], fixed twins at the stored gain.
Independent re-derivation straight from the npz files (separate code path, same formula):
8 arms agree with the script to < 1e-9, and r30k1 - gc30 by hand = +7.26e-4, 15 of 16 seeds.

## Disclosed: the analysis script needed four fixes before it would run

`final_l290.py` was written at 22:44, four minutes after the 22:40 launch and before any
effect existed. It had never been executed. Four halts, each with ZERO bytes of stdout, so no
effect was seen before the last fix; the tick-277 original is kept byte-identical as
`final_l290_pre_fix_tick278.py` (sha `43fef618a2143a14`), the running file is sha
`e85b1f50f8289aa6`, and every diff is in `AMEND_ANALYSIS_20261125.md`.

1. Coverage check demanded the anchor seeds for every arm; the harness runs only cutwA on them.
2. Worker keys collided (A1's l240 workers 0-2 and L290's 0-2 shared one dict), which silently
   replaced A1's stored arrays and made the "cutwA == A1 stored" gate compare L290 with itself.
3. A synthetic self-check fed a 15/16 vector an expectation that holds only for 16/16.
4. The tail rule of the arm-vs-arm test chose its p-value by the sign of the observed advantage,
   so "IS EXCEEDED BY" could not fire and a beaten used-set still counted as ESCAPES. The
   PREREG text (s5: A <= -eps and 1 - p_up <= 0.01) is now implemented verbatim. EXCEEDS and
   every WINS leg are identical under both rules; the rule change moved 2 of 18 contrasts
   (Crofts vs r30k1, vs r30k3: WITHIN -> EXCEEDED_BY) and the stored verdict under the old
   rule is also NO_DECISION (`amendment_tick278` in the results file).

## Limits

One carrier (gi 1110), one substrate, one gain family, 16 seeds. Random subsets are uniform
over the 69-edge menu, NOT matched on synapse weight, so "metric set vs random" and "heavy
edges vs light" are not separable here. Every used-set contains e14. The scalar pool mean is
blind to redistribution. NO_DECISION is a statement about this design, not evidence that the
metrics are equivalent.

Evidence: `~/critters/peabrain-lab/banc/l290/` -- `PREREG.md` + `PREREG.sha256`, `sets.json`,
`results_l290.json` (sha256 `83498d7c933414c7`), `final_run.out`, `final_l290.py`,
`final_l290_pre_fix_tick278.py`, `PRERUN_AUDIT.md`, `AMEND_ANALYSIS_20261125.md`,
`final_run_attempt{1,2,3}.out`, `raw_w0-2.npz`, `xm_w0-2.npz`.
