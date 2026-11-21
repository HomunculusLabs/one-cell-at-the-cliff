# L59 PREREG — spec-seed-ensemble (LANE.md ideas-28, L59)

Written BEFORE any rollout. Machinery: l55_hop.py verbatim (substrate l32
arm-A frozen g .01 / beta 2 / d .05, ENT_AMP .3, SETTLE 400 driven at 0.7 Hz
l39-l51 lineage convention, WIN 6000, SEGB 0.7/1.4/0.7 Hz, BLK 500,
MEAS0 500, LOCK_TOL .10, DT 10 ms).

## Arms (exactly the two LANE-named schedules)

- `hynohop` = l55 hynohop: hybrid AMPA (500-on/400-off chop on both 0.7 segs,
  CONTINUOUS on the 1.4 seg), NO hop volleys. Drive-on 4800 steps (48 s).
- `hybrid` = l51 hybrid: same AMPA + DNge046_L hop volleys (amp .5, 40 steps)
  at transitions 2000 and 4000.

Seeds = the l45b CENSUS GRID: [11, 22, 33] + range(101, 114) = 16 seeds.
CPU-only, torch threads 8, ONE generator per seed shared across arms,
per-step shared noise tensor (L36 lesson), X0 drawn once per seed and cloned
per arm (L45b lesson).

## Metrics (l55-verbatim windows)

Per (arm, seed): per-seg duty(both S >= .25) over [seg0+500, seg1),
SL/SR window medians, pooled duty_all (all segs, same windows), duty_07,
seg tracking err (mean block err excl. first block), lock TTL, seg f.

## Anchors (C0) — 15th consecutive chain anchor

1. Seeds 11/22/33, BOTH arms: mm + all four antagonist traces (fL/fR/eL/eR)
   bit-identical (max|d| == 0.0) to l55/raw_l55.npz, full [0,6000).
2. dm probe: hybrid-vs-hynohop first_div == 2000 on ALL 16 seeds
   (volley wiring check, L35/L39 class), vmax > 1e-6 in the hop windows.
3. C1: settled af in (0.01, 0.9) every cell.

## Registered distributional predictions (scored, never summed into one J)

- P1 pooled gate: P(duty_all >= .5) per arm with Wilson 95% CI at n=16.
  Registered expectation (from L58: best fixed min-seed .473; L55 nohop
  mean .496 n=3): point estimate < .5 for BOTH arms (gas-owned gate).
- P2 fast-window lottery: seg1 duty distribution is wide/bimodal — predict
  >= 5/16 seeds with seg1 duty < .1 in at least one arm.
- P3 miss anatomy (L56 form): among pooled-miss seeds (duty_all < .5),
  failing segments (duty < .5) are S_L-owned majority — registered: share of
  failing segments with SL_med < .25 & SR_med >= .25 is >= 50%.
- P4 tracking: seg1 err <= .01 on >= 12/16 seeds for BOTH arms (chopped-entry
  free lock; L51/L55/L58).
- P5 entry join (exploratory, small-n disclosed): seg0 side-health vs pooled
  duty rank correlation — no registered sign; either way reported.

## Verdict shape

A distribution table that replaces the L57 contract's n=3 single-seed reads
with census-n claims: pooled-gate probability (CI), fast-window duty
distribution, miss anatomy share, tracking robustness. If P1's CI spans .5
the read is INCONCLUSIVE-AT-16 (named, that is the honest number). No new
gate invented; no controller claim; descriptive only.

## Deviations

None yet. Any window/units amendment gets an addendum here BEFORE the
affected read is quoted.

## ADDENDUM 1 (post-run, disclosed — gate-logic fix, zero rollout effect)

Run 1's `C0_pass` computed False while every anchor value was perfect: the
gate's "all float values in c0 must be 0.0" sweep accidentally included the
DIAGNOSTIC `volley_vmax_min` (0.4788 — a magnitude, meant to be checked
`> 1e-6` separately, which it passes). Fixed in l59_ensemble.py to test only
the `_maxd` anchor keys; C0_pass re-derived from the stored results json
(af_ok True, all ten maxd 0.0, fd 2000 on 16/16, vmax .4788). Rollouts and
every distributional read untouched (raw npz checkpointed pre-analysis,
L45a lesson). The 15th chain anchor stands: bit-identical 0.0.

