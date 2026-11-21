# L101 PREREG — closure-pool-vocabulary scan (female BANC, L92 closure substrate)

Question (from L94): "the honest closure substrate has NO robust base pair"
was measured on exactly 2 pairs (Ti 0/48, Tr 0/48 both-sides). Is that a
property of the WHOLE semantic antagonist vocabulary, or just tibia/
trochanter? Scan every semantic antagonist pair the BANC
peripheral_target_type column defines on the closure subnet.

## Design

- Substrate: L92 closure subnet (n 21,809, g* .153125), machinery
  l94_run.py VERBATIM (extraction, two-generator noise law, joint settle,
  AMPA/PHI schedule, DNg100 tonic D=.2, BETA 2).
- Arm: cfn BASE ONLY. Seeds: ANCHOR [11,22,33] + B4 801-816 + B5 901-916
  + B6 1001-1016 (48 fresh) — IDENTICAL to l94, so cfn traces must
  reproduce raw_l94.npz bit-for-bit (strongest available anchor).
- Pairs (semantic token substrings, static.py): agonist a / antagonist b
  per side L/R; pool = in-subnet motor cells.
  Ti tibia flex/ext (l94 exact), Tr trochanter flex/ext (l94 exact),
  Ta tarsus depressor/levator, Sr sternal anterior/posterior rotator,
  Pr tergopleural promotor / pleural remotor+abductor.
- Static pins (l101/static.json, written BEFORE this file's rollouts):
  sizes Ti 50/51/6/6, Tr 31/31/24/24, Ta 12/12/3/3, Sr 6/6/11/13,
  Pr 4/4/3/3 (aL/aR/bL/bR); all >= 3 => all 5 ELIGIBLE. Unpaired-by-
  semantics disclosed, NOT scanned: long_tendon 47, femur_reductor 34.

## Registered gates

- Cell (l94 verbatim): duty_07 = mean over 0.7 Hz windows of
  (SL >= .25 & SR >= .25), SL/SR = -corr(fL,eL)/(fR,eR) 5-s rolling
  (t=499..5999 step 10); side cells duty07_L/R = single-side >= .25.
- G2a-multi (primary, both-sides): k = #{seeds: duty_07 >= .5} per pair,
  pooled over 48 fresh, PASS iff wilson_lb_full(k,48) >= .717
  (k_min 41; assert wilson_lb_full(41,48) >= .717 > wilson_lb_full(40,48)).
- G2a-multi-side (secondary, L91/L94 side-split law): same form on
  duty07_L and duty07_R separately.
- VERDICT-robust-vocabulary: PASS iff >= 1 pair clears the PRIMARY cell
  (Ti/Tr expected FAIL: stored l94 cfn pooled k 0/48 lb 0.0 both).
  A new pair clearing => female endgame REOPENS on that pair (3 batches
  already = multibatch form; disclose per-batch swing per L88/L90).
- NaN law: a flat pool trace (std <= 1e-6) gives S = NaN -> that seed's
  duty cell counts as FAIL for k; NaN counts disclosed per pair
  (small pools 3 cells may sit at the relu floor).
- Descriptive (no gate): seg1 fast-window duty mean + per-batch spread
  (the batch-STABLE axis, L88/L90); per-batch k spread.

## Registered anchors (all must pass BEFORE any L101 number is pinned)

- S1: subnet n_new 21,809 == l92 static; Ti/Tr sizes == l92 pool_sizes
  (fired in static.py, exit 0).
- C0A bit-identity vs raw_l94.npz (cfn): max|d| == 0.0 for mm + xm ALL
  51 seeds AND Ti/Tr 8 pool traces for seeds {11,22,33,801,901,1001}.
- C0B metric certification: THIS run's generalized cells/table code on
  raw_l94.npz reproduces results_l94.json cfn reads EXACTLY — per-batch
  k/wilson/duty07_mean/seg1_mean/seg2_mean/duty07L_mean/duty07R_mean
  (B4/B5/B6) x {Ti,Tr}, pooled k/n/lb_full/g2a_multi/k_min, anchor
  duty_07 pins {11,22,33} x {Ti,Tr}; lock_g1p(cfn, 48 seeds,
  dom_ratio(mm seg) >= 10 all 3 segs) == 48 (L85 rule).
- C1: af in (0.01, 0.9) every seed AND af == l94 stored af_cfn_seed
  exact, all 51.
- Expectations pinned from STORED artifacts only (L44 rule): l94
  results table_Ti/table_Tr cfn per-batch means above; Tr side split
  L [.032,.051,.056] < R [.372,.421,.451].

## Small-pool disclosure

Ta_b (3/3), Sr_a (6/6), Pr (4/4/3/3) pools are at or below the Ti_b
precedent (6); a clear on these carries a small-pool caveat; the NaN
law above governs flat-trace degeneracy.

Run budget: 1 arm x 51 seeds, CPU (~2 s/seed measured on l94) ~4 min.
