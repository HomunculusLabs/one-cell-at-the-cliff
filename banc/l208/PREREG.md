# L208 PREREG — the less-saturated-side hypothesis

Written BEFORE any saturation number is read. Tick 237 (2026-11-22), lane
item L208. ZERO new rollouts: every value comes from the already-stored
`l169b2/raw_l169b2.npz` (batch B36, seeds 3449-3464) and
`l175f/raw_l175f.npz` (batch B37, seeds 3701-3716), opened READ-ONLY and
never rewritten (L175: a lab run script is a SCRIPT, not a library — no lab
module is imported; helper code arrives as VERBATIM SOURCE SLICES).

## The hypothesis, as the card poses it

L205 measured the LEFT tibia pools as the less-driven side (per-cell
in-mass 254.8 vs 309.4 = -18%; per-side shared-drive companion -0.14) and
L178 measured only 19 of 303 readout cells above threshold at the f4wA
operating point. The floored arms' antiphase is LEFT-dominant (f4wA meanL
.698, kL 16/16) while the base arms' is RIGHT-dominant (cutng25 meanR .754,
kR 16/16). HYPOTHESIS: side-dominance of the antagonist antiphase S rides
the side's own SATURATION MARGIN — the dominant side is the one with more
headroom below the ceiling (RMAX = 1.0) and/or less time pinned at the relu
floor — and this holds WITHIN seed, in both batches.

## MEASUREMENT-CAPABILITY LIMIT, registered first (this is load-bearing)

The stored traces are **POOL MEANS**, not per-cell rates: the run writes
`tr[a][kk][k] = X[a][POOLS[a][kk]].mean()` (l169b2_run.py, rollout block),
one float32 per pool per step. Therefore **the fraction of CELLS at the
ceiling is NOT recoverable from stored data** and cannot be measured under
the zero-new-rollout constraint. What IS measurable is the pool-mean
trajectory's own distance from RMAX and from the floor. The registered
statistic is therefore a **pool-mean saturation margin**, named as such in
the verdict, and the per-cell version is explicitly declared out of reach
this tick (it would need fresh rollouts storing per-cell quantiles — if the
result warrants it, that becomes its own queue item, not a substitution).

## Registered substrate, window and statistics

- Pairs: **Ti** (primary — the L205/L175f joint) and **Tr** (second leg).
  Preferred/antagonist naming per the stored convention: Ti/Tr -> (f, e).
- Arms: the five arms both batches share — `f4wA`, `f4ng`, `f4tw` (floored)
  and `cutwA`, `cutng25` (base). Each arm is a SEPARATE object (L109); no
  pooling across arms for any gate.
- Dynamics constants, read from the run script and asserted in-script:
  `TAU, DT, RMAX = 0.05, 0.01, 1.0`, `BG, NOISE = 0.02, 0.01`,
  `WIN = 6000`, `SEGB = [(0,2000,.7),(2000,4000,1.4),(4000,6000,.7)]`,
  `MEAS0 = 500`, `ENT_AMP = 0.1`, pulsed drive `AMPA` (500-on / 400-off
  within each 2000-step segment, with 2000:4000 fully on).
- **WINDOW (L164 obeyed — whole registered window, never a terminal
  value):** the step set `W = {k : 500 <= k < 2000} ∪ {k : 4500 <= k < 6000}`
  = 3000 steps. These are exactly the index ranges the stored duty gate
  selects (`q07` over `TS` with `MEAS0 = 500` on the two 0.7-Hz segments);
  the duty uses a 500-step correlation grid inside them, the saturation
  statistic uses every step in them. Declared companion sub-window:
  `W_on = {k in W : AMPA[k] > 0}` (tone-on only), reported beside the
  primary because the drive is pulsed and a margin averaged across on/off
  phases is a mixture.
- Per arm, per seed, per pair, per SIDE s in {L, R}, over window W:
  - `lvl` = mean over W and over the side's two pools of the pool-mean rate
    (the side's operating level; higher = closer to ceiling).
  - `margin` = `RMAX - lvl` (registered as the hypothesis's currency).
  - `fhi` = fraction of (step, pool) cells in W with pool-mean >= 0.95
    (ceiling-pinned fraction of the pool mean). Robustness threshold 0.90
    reported beside it.
  - `flo` = fraction with pool-mean <= `BG` = 0.02 (floor-pinned).
  - `pmax` = max pool-mean over W (how close the side ever gets to RMAX).
- Side-dominance currency: the stored duty `S >= .25` fraction per side,
  reproduced with the VERBATIM `s_arrays` / `duty_seeds` helper source from
  `l169b2_verdict.py` (sliced as text, never imported). Per seed,
  `dS = dutyL - dutyR` and `dM = marginL - marginR`.

## The registered test

PRIMARY (within-seed, paired, per arm, per batch): Spearman
`rho(dS, dM)` across the 16 seeds. The hypothesis predicts **rho > 0**
(the side with MORE margin carries MORE antiphase duty). Significance by
exact-sign permutation of the seed pairing, 20,000 draws, seed 20837,
one-sided upper, bar p < .05. The SAME draws are reused across arms so the
arm-to-arm comparison is paired.

SECOND LEG (between arms, descriptive): the 5-arm table of
`sign(marginL - marginR)` against the stored `side_dominance`
(`f4wA/f4ng/f4tw = L`, `cutwA/cutng25 = R`) — does the margin ordering FLIP
with the floor the way dominance does?

## Branch table — SIGN x BAND = four cells (the L205 method lesson)

- **H0_VOID** (degenerate, registered explicitly as the card requires): if
  the two sides' margins are effectively identical — median over arms and
  seeds of `|dM| < 0.005` (0.5% of RMAX) — the hypothesis is VOID and says
  nothing about drive. Checked and reported BEFORE any rho.
- **H1_SUPPORT**: rho > 0 and p < .05 on the Ti primary in BOTH batches.
- **H2_INVERTED**: rho < 0 and p < .05 (lower-tailed) in BOTH batches — the
  MORE-saturated side dominates; refuted by sign, which is stronger
  evidence against the hypothesis than a null.
- **H3_NULL_BAND**: neither tail clears in either batch — margin carries no
  within-seed prediction of side dominance.
- **H4_SPLIT**: the two batches disagree in sign-with-significance — a
  replication failure, reported as such and never collapsed to one number.
- **H_UNREGISTERED_SHAPE**: anything else (e.g. significance in one batch
  with the other inside the band on the same sign). Reported honestly
  rather than mapped onto the nearest registered label.

## Predictions (recorded, scored in the verdict)

1. Q208-1: **H3_NULL_BAND** on the Ti primary. The floored/base dominance
   flip is already attributed to attractor selection (L205 C3), and margin
   is a mean-level statistic with little seed-to-seed contrast.
2. Q208-2: the between-arm margin sign does NOT flip with the floor — i.e.
   the same side carries more margin on floored and base arms, so the
   descriptive table cannot explain the dominance flip.
3. Q208-3: `fhi` is ~0 on every arm/side (the operating point is ~11%
   active; a pool MEAN reaching 0.95 would be extraordinary), so the
   ceiling leg is uninformative and the margin leg is carried entirely by
   `lvl`.
4. Q208-4: `flo` is nonzero and side-asymmetric on at least one arm (the
   relu floor, not the ceiling, is the live nonlinearity here).

## Verification gates (must pass before any L208 number is read)

- **CERT-ADD**: the stored `addendum_L_descriptive` rows of
  `results_l169b2.json` — meanL/kL/meanR/kR for all five arms AND all 16
  per-seed L values per arm — reproduced EXACTLY from the npz by my copy of
  the verbatim duty helpers. Plus the three stored `paired_legs`
  (`mean_paired_dL`, `n_up`, `n_down`).
- **CERT-175F**: the stored `l175f/results_l175f.json` `rows` (meanL/kL/
  meanR/kR, five arms) and `per_seed` L and R arrays reproduced EXACTLY
  from `raw_l175f.npz` by the same helpers.
- **CERT-CONST**: the dynamics constants and the AMPA/SEGB window shape
  asserted against the run script's own literals; `W` size asserted = 3000.
- Both npz opened read-only; mtime + size recorded before and after and
  asserted unchanged (no rewrite).
- Forbidden-token audit on the sliced helper source (no `savez`, no
  `open(`, no `json.dump`) so the slice cannot touch stored artifacts.
