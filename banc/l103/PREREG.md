# L103 PREREG — unpaired-pool closure census (long_tendon + femur_reductor)

Question (from L101): the closure-vocabulary scan left the two
unpaired-by-semantics motor pools unscanned (disclosed there: long_tendon
47, femur_reductor 34 in-subnet). Complete the motor-vocabulary census:
does either pool show a batch-robust structure cell on the closure
substrate at base, or does the whole motor vocabulary close with no
robust base anywhere but l65's Ti?

## Definitional port (DISCLOSED BEFORE ROLLOUTS)

Antagonism is undefined by semantics for these pools — there is no
homologous antagonist token. The registered antagonist surrogate is the
CONTRALATERAL HOMOLOGUE: the only antagonist-like relation an unpaired
bilateral pool offers (bilateral alternation = stepping-like structure).
Everything else is l101 machinery verbatim.

- Pools (l103/static.json, pinned BEFORE this file's rollouts; token
  substrings on peripheral_target_type, per-side, in-subnet):
  LT "long_tendon" → LT_L 23 / LT_R 24; FR "femur_reductor" →
  FR_L 17 / FR_R 17; side values {left,right} only, no "other" cells;
  totals 47/34 == l101's disclosed numbers exactly; both ELIGIBLE
  (>= 3 cells/side, l101 rule).
- Cell (primary): S_LR(t) = -corr(pool_L, pool_R) on 5-s rolling windows
  (t = 499..5999 step 10, s_of verbatim incl. the NaN law: std <= 1e-6
  → NaN → that seed FAILS the cell, NaN count disclosed).
  duty_07 = mean over 0.7 Hz windows of (S_LR >= .25); per-seed clear =
  duty_07 >= .5 — identical threshold law to l101.
- Per-side cells (the registered meaning of "per-side split" for an
  UNPAIRED pool; diagnostic, never verdict-carrier alone): per-side
  ALIVE duty = fraction of 0.7 windows with pool-trace mean >= 0.05
  (the af active threshold), L and R separately, pooled-Wilson form.
  Detects a dead pool (alive ~0, S degenerate) and a clamp-pinned pool
  (alive ~1, flat).

## Registered gates

- G2a-multi (primary, both-sides analog): k = #{48 fresh seeds (B4+B5+B6):
  duty_07 >= .5} per pool; PASS iff wilson_lb_full(k, 48) >= .717
  (k_min 41; assert wilson_lb_full(41,48) >= .717 >
  wilson_lb_full(40,48)).
- FlyHack two-sided secondary check (tick-126 amendment; computed ALWAYS
  on the SAME stored traces, zero rollouts; VERDICT-CARRIER only when the
  primary clears): phase-shift null = circular shift of the R trace by
  500 steps (5 s — destroys window-scale cross-side phase), recompute
  duty_07^shuf; SECONDARY PASS requires fresh duty_07 mean >= null mean
  + .20. Extra shifts {100,300,700,900} reported descriptive.
  NEVER-FIRES BRANCH registered explicitly (L55 lesson): if no pool
  clears the primary, the secondary is reported descriptively and the
  verdict rests on the primary alone.
- Seed-sustain fraction beside EVERY k/n cell (tick-126): sustain_frac =
  (# of 3 batches with per-batch k >= 8) / 3, plus the per-batch k list.
- VERDICT-vocabulary-complete: PASS iff >= 1 unpaired pool clears the
  PRIMARY G2a-multi cell → closure substrate "second life sign", female
  endgame reopens on that pool (3 batches already = multibatch form;
  disclose per-batch swing per L88/L90). Both FAIL → the motor
  vocabulary is fully scanned under THIS registered cell definition:
  no robust base anywhere but l65's Ti, closure endgame closed as a
  base substrate (definitional caveat carried in the claim wording).
- Descriptive (no gate): seg1 fast-window duty mean + per-batch spread
  (the batch-STABLE axis, L88/L90); per-batch k spread; alive duties.

## Registered anchors (all must pass BEFORE any L103 number is pinned)

- S1: static sizes == l103/static.json (fired in static.py, exit 0;
  totals == l101 disclosed 47/34).
- C0A bit-identity vs raw_l101.npz (cfn): max|d| == 0.0 for mm + xm
  ALL 51 seeds AND Ti_aL + Ti_bR pool traces for seeds {11,22,33}
  (pool-extraction certification) AND af_cfn_seed exact all 51
  (noise-stream law; 40th consecutive chain anchor).
- C0B metric certification: THIS run's verdict script re-implements
  l101 cells_of VERBATIM; on stored raw_l101.npz it must reproduce
  results_l101.json EXACTLY — per-pair per-batch {k,kL,kR,wilson,
  duty07_mean,seg1_mean,duty07L_mean,duty07R_mean} x 5 pairs x 3
  batches, pooled {k,n,lb_full,g2a_multi} x 5, side {kL,lbL,g2aL,kR,
  lbR,g2aR} x 5, nan_seed_count x 5, lock 48.
- C1: af in (0.01, 0.9) every seed (in-run assert, l101 verbatim).
- Expectations pinned from STORED artifacts only (L44 rule): l101
  results — Ti pooled k 0/48 lb 0.0, Tr 0/48 lb 0.0, lock 48, no
  robust pair, no side clear (max lbR .326 Ti); anchors c0a/c1/c0b
  all true there.

## Small-pool disclosure

FR (17/17) sits between Tr (31/31) and Ti_b (6/6) precedent sizes; no
pool here is below the Ti_b precedent. Alive-duty cells guard the
degenerate end.

Run budget: 1 arm x 51 seeds, CPU (~2 s/seed measured on l101) ~4 min.
