# L294 VERDICT -- WHAT PREDICTS A WEIGHT-MATCHED SET'S EFFECT

Tick 287, 2026-11-25 13:10-13:3x EST, Miso. Static re-analysis of STORED L290 + L291 arrays,
zero rollouts, parents untouched (results_l290 sha 83498d7c933414c7..., results_l291 sha
a8b80c85491417a1..., both with their original mtimes).

- PREREG sha256 `77b3dfb022d1a0b8c1d862ebfb5b000514a015af52933014c89d65ff5f7a5a37` (frozen 13:10 EST)
- results_l294.json sha256 `3b6d85df32f710ba68ac3692f8f94a01d1691a71cb705cbb001f6d7fed4378b1`
- script `l294_final.py` (nice +15, om); output `run.out`; gates G1 G2 G2b G3 G4 G5 all PASS

## VERDICT: A_GAIN_DELTA_MEDIATED / A_POOL_SPECIFIC, G_SHIFT_ON

By the registered first-match rule (PREREG s5) -- and it rests on TWO HAIRLINE legs (below).
Predictions 4/6: P2, P3, P4, P6 held. **P1 FALSE, P5 FALSE.**

## The registered family (midrank Spearman within size stratum, df-weighted; label permutation
## within stratum, B = 20,000, PCG64(29400); BH q 0.10 over m = 6, all six readable)

| test | statistic | value | per stratum n11 / n30 / n46 | p | BH q |
|---|---|---|---|---|---|
| T1 | STRAT-RHO(E, DGAIN), L290's 18 (out of sample) | +0.4476 | -0.371 / +0.943 / +0.771 | 0.08785 | 0.0878 |
| T2 | STRAT-RHO(E, DGAIN), all 33 bisected arms | +0.7000 | +0.518 / +0.845 / +0.736 | 0.00005 | 0.00015 |
| T3 | STRAT-RHO(E, EW_SUM), 33 arms | +0.5455 | +0.764 / +0.445 / +0.427 | 0.00210 | 0.0042 |
| T4 | twins, S = mean sign(dgain)*dE, 7 pairs | +1.630 F | 6 of 7 concordant | 6/128 = 0.04688 | (0.056) |
| T5 | STRAT-RHO(E_CTRL, DGAIN), 33 arms | +0.5182 | +0.755 / +0.136 / +0.664 | 0.00390 | 0.00585 |
| T6 | STRAT-RHO(E_DIFF, DGAIN), 33 arms | +0.6788 | +0.473 / +0.827 / +0.736 | 0.00005 | 0.00015 |

Companion, never gating: CARD35 (33 + the 2 fixed twins at dgain = 0): +0.6764, p 0.00010.
Resolution floor of the family: 1/(B+1) = 0.00005; T2 and T6 sit ON it (no draw reached them).

## Reading, in the registered order

1. CONFOUND FIRST -- T5 fires: G_SHIFT_ON. The 21,482 cells OUTSIDE the pool union also move with
   the gain delta (mean E_CTRL +0.39 / +1.23 / +1.08 F by stratum), so part of any DGAIN -> E
   association is a shift the pool shares. Surviving share (T2 - T6)/T2 = 0.03 (description): the
   pool-minus-common readout KEEPS 97% of the association. The pool tracks dgain beyond a common
   additive shift. (Not a multiplicative control; the log-ratio form reads +0.700, +0.52/+0.84/+0.75.)
2. TWIN INSTRUMENT -- T4: S = +1.63 F, 6 of 7 pairs concordant, p_one = 6/128 = 0.047 <= 0.05 ->
   TWIN_GAIN. With the set and the seeds held fixed, moving only the gain moves the pool in dgain's
   direction: the gain is a within-set mediator, i.e. part of the intervention. The discordant pair
   is e27 (dgain -0.95e-3, the bisected arm reads +1.93 F ABOVE its fixed twin).
   Twin pairs, dE = bisected - fixed (F): gc30 +1.371 (dgain +0.39e-3), gh46 +3.281 (+0.68e-3),
   e14 +1.690 (+0.16e-3), e25 +4.549 (+0.85e-3), e67 -0.516 (-0.51e-3), e12 -1.930 (-0.94e-3),
   e27 +1.927 (-0.95e-3). Spearman(dgain, dE) +0.607, exact p 0.083 (stored beside, not gating).
3. VERDICT -- A_GAIN_DELTA_MEDIATED (T1 and T2 q <= 0.10 with sign +, and TWIN_GAIN); T6 is
   significant -> A_POOL_SPECIFIC.

## The two hairline legs (stated, not chosen around)

- T1 (the out-of-sample leg): p 0.0879 against the q 0.10 bar. It MISSES 0.05 (P1 false), and its
  n-11 stratum is REVERSED: -0.371 over its six arms (five uniform 11-sets and rw11; r11k5 carries the stratum's
  most negative dgain and reads +1.74 F; r11k3 a positive dgain and -2.22 F). Sizes 30 and 46 hold
  at +0.94 and +0.77.
- T4: 6 of 128 patterns against a 0.05 bar = 6.4 patterns. One more null pattern and it is
  TWIN_FAIL.
- Neighbours of the label: one more T4 pattern -> B GAIN_DELTA_MARKER. T1's p 0.0122 higher -> C
  WEIGHT_CARRIES (T3 already satisfies it). What does not move under either neighbour: T2, T3, T5,
  T6. Read the stable content, not the letter: the gain delta tracks the effect, the removed
  effective weight tracks it too, and the rest of the network shifts with both.

## What the card asked

- (a) the drive removed in the NORMALISED graph (EW_SUM = sum of log1p(syn) over the removed
  edges): **YES, it carries** -- +0.55 within stratum, q 0.0042, positive in all three strata.
  This is AGAINST L294's own registered P5 ("weight does not carry"). It is the only covariate
  here that is available BEFORE any rollout. Mirror read first, as registered: rho(EW_SUM, SYN)
  = 0.972 over the 33 (a concave mirror of the raw synapse sum, which read +0.59 pooled on L290-15
  and +0.20 on L291-15).
- (b) the gain delta: **YES** -- +0.70 on 33 arms, +0.45 out of sample (p 0.088), 6 of 7 within a
  set. L227 stands, binding: dgain is a CONSEQUENCE of the cut (you must run the bisection to have
  it), so this is a mechanism probe and a cheap screen, never a prediction for an unseen set.
- (c) a per-set lottery: **not all of it, not none of it.** Rank R^2 against dgain is about 0.49 on
  the 33: roughly half the rank variance is not carried by the gain delta. The two predictors
  were not modelled together here (L297).
- Sign-split: degenerate on this carrier (0 of 69 negative weights; EW_NEG identically 0).
- Distinct targets: degenerate (== n within a stratum; 0 of 69 menu targets lie inside the pool).
- e14 (description only, as declared): with / without means on the 33 arms, +5.64 / +0.13 F (n 11),
  +9.72 / +0.22 (30), +8.54 / -0.73 (46).

## Post-hoc descriptions (NOT registered, never gating -- banc/l294/posthoc_check.out)

- The two predictors against each other: STRAT-RHO(EW_SUM, DGAIN) on the 33 = +0.215
  (+0.23 / +0.26 / +0.16). Near-orthogonal: they are NOT one quantity in two currencies.
- L291's "every negative-dgain arm sits at the floor", out of sample on L18: 6 of 9 negative-dgain
  arms at |E| <= 2F against 1 of 9 others (Fisher two-sided 0.050). Exceptions: r11k2 -4.34 F,
  r11k4 -4.69 F, r46k1 +3.87 F. Holds as a tendency, not as a rule.
- Floor-only readout (|E| > 2F): T2 +0.757 over 23 arms; T1 +0.60 over 11 (n-11 unmeasurable).

## Gates that carried this (all passed before any test was computed)

G1 shapes (35 arms + gc30/gh46/e14/e25/e67/e12/e27, 16 per-seed values each, E == mean(per_seed)
to 1e-15). G2 every E and every per-seed value re-derived from the stored xmean arrays over the
pool union: max |re-derived - stored| = 0.0 over 37 arms. G2b pool TRACE mean == mean over the
pool's cells of xmean (rtol 1e-4), one arm per worker. G3 covariate provenance (set targets ==
removed targets, syn sums, EW_SUM == stored effective weights to 1e-5, eff, has14, L291 dgain ==
gain - g_base to 0.0). G4 anchors: DGAIN x E ordinal on L291-15 = +0.8214 (L291's "+0.82"); SYN x E
on L290-15 = 0.5892857143; eff x E on L290-15 = 0.4286057679; L291 cell means to 0.005 F. G5 the
script refuses to run without the PREREG hash.

Reproducibility: run 2 reproduced run 1 on every stored leaf (repro_check.py: 0 differing, same
tests, q-values, verdict).

## Limits

One carrier, one substrate, one gain family. 16 seeds shared by every arm: L18 is out-of-sample in
SETS, not in seeds. Midrank on 10-11 arms per stratum is a low-power instrument -- a non-rejection
is NOT SHOWN, never absent. EW_SUM removes nothing: it is confounded with e14 membership and that
is not tested here. E_DIFF removes an additive shift only.

## Disclosures

- The PREREG header's freeze time was corrected (13:24 -> 13:10) after the first hash and before
  any test existed (the analysis script did not exist yet); both hashes are in
  PREREG_FREEZE_NOTE.md. The binding hash is the one above. No design text changed.
- The VERIFICATION script was wrong twice in its first run: `math.copysign(dE, dgain)` is |dE|
  with dgain's sign, not sign(dgain)*dE (it reported S 0.93 and 24/128), and its Fisher test was
  parametrised on the wrong margin (0.002). The analysis script was right both times (6/128,
  0.050), confirmed by hand-enumerating the 128 patterns on the printed magnitudes. Fixed before
  anything here was reported; posthoc_check.out is the corrected output.

## What it changes

L291's scatter inside a +/-5% synapse band is not pure lottery: sets in the band differ in gain
compensation and in effective weight, and both track the effect. Because the gain is part of the
intervention (T4), every future cut arm keeps BOTH its bisected and its fixed-gain twin. Registered
next as L297: a within-stratum two-predictor model (EW_SUM, DGAIN, E14) with a permutation for each
partial, the n-11 reversal, and whether EW_SUM alone ranks sets well enough to use before a rollout.
