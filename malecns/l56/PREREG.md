# L56 PREREG — seg2-reroll-law (written BEFORE any run)

Question (LANE ideas-27, L55's factorial surprise): is "any hop re-rolls the
downstream attractor lottery" a LAW (any volley at any time = pure re-draw
from the same gas distribution, mean-neutral), or are the TRANSITIONS special
(volleys only re-roll when delivered at a segment boundary / re-lock window)?

## Design (substrate frozen: l32 arm-A, l34 entrain, l39/l50/l51/l55 schedule)

Same hybrid AMPA schedule as l55 for EVERY arm (0.7 segs chopped 500-on/400-off,
1.4 seg continuous, amp .3, drive-on 48 s). Per-arm volley tables (write-time
asserted, no inline conditionals — L39-v1/L48 lesson):

- `nohop`  — no volleys. CHAIN ANCHOR: bit-identical to l55 `hynohop`.
- `hop4k`  — DNge046_L volley @ k=4000 (seg1->seg2 TRANSITION; 40 steps, amp .5).
             CHAIN ANCHOR: bit-identical to l55 `hop4k`.
- `v43`    — same volley @ k=4300 (1.5 s INTO seg2, during a drive-ON window).
- `v46`    — same volley @ k=4600 (6 s into seg2, drive-OFF window 4500-4900).
- `v49`    — same volley @ k=4900 (9 s into seg2, coincident with drive re-on).

Seeds 11/22/33. ONE generator per seed, ONE shared per-step noise tensor, X0
drawn once and cloned per arm (L36/L45b lessons). CPU-only, P1-labeled.

## Pre-registered gates / predictions

- C0 ANCHORS: nohop and hop4k mm traces bit-identical to l55/raw_l55.npz over
  the full [0,6000) window (max|d| == 0.0); first_div of every volley arm ==
  its volley start step (4000/4300/4600/4900 exactly).
- C1 WIRING: volley_max > 1e-6 for every volley arm (dm probe, window = volley
  span); af in (0.01, 0.9) for every arm/seed at settle end.
- P1a TRANSITION-SPECIALNESS (the law's core): seg2 duty (l55-verbatim window
  [4500,6000), both S >= .25) of v46 vs hop4k — the law predicts volley TIME
  does not matter: |mean over seeds(v46) − mean(hop4k)| < .10 AND no per-seed
  consistent ordering (NOT all 3 seeds differ by > .15 in the same direction).
- P1b MID-SEG2 RE-DRAW: for each mid-seg2 arm, seg2 census label (l45 seg_state
  conventions: fband|rhythm2 on mm, ssign at |.15| on window-median SL/SR) of
  the POST-volley window [v_start+140, 6000) vs the same arm's PRE window
  [4500 or seg2 start+50, v_start): re-draw = label changes in >= 1 seed with
  S-sign flip; absorbed = all seeds' post labels == their own seg2-start
  trajectory's label (label at [4050, v_start) window). LAW expects re-draw;
  TRANSITIONS-SPECIAL expects absorbed (E1/X464-like HELD).
- P1c DISTRIBUTION UNCHANGED: pooled S-sign labels over ALL 12 volley cells
  (4 volley arms x 3 seeds) vs the no-volley reference (nohop+hop4k seg2 labels,
  n=6): chi-square on the S_L / S_R sign axes, SMALL-N DISCLOSED (expected
  counts < 5 everywhere; report per-axis counts + chi2 + p as descriptive, no
  reject/accept at n this size). Secondary, drive-confound NAMED: vs L45b
  free-cord census marginals (SL + 11/16, SR + 0/16) — seg2 cells sit under
  chopped 0.7 drive where L49 measured SR rebuild, so free-cord marginals are
  NOT the matched reference; reported for continuity only.
- P2 MISS DECOMPOSITION (queue question): every seg2 cell with duty < .25 gets
  its per-side decomposition (SL, SR medians + label). Exploratory expectation
  from L46/L48: misses are one-side/marginal states (SL 0|SR + etc.), never
  bilateral-negative. No gate — descriptive deliverable.
- P3 MEAN-NEUTRALITY: mean seg2 duty over the 4 volley arms within ±.10 of the
  nohop mean (gas is mean-neutral; L55 measured single hops RAISING pooled
  mean — seg2-scoped version here).

## Verdict shape (registered)

- LAW-SUPPORTED: P1a AND P1b(re-draw) hold; P1c counts reported, small-n named.
- TRANSITIONS-SPECIAL: P1b absorbed (mid-seg2 volleys change nothing) while
  hop4k's boundary re-roll stands (L55 P4 numbers reproduce: seg2
  .507/.147/.66 -> hop4k .487/.627/.507 under l55 conventions).
- MIXED: table delivered, mechanism named per axis.

## Deviations

None yet. Any change after data is an ADDENDUM with reason.
