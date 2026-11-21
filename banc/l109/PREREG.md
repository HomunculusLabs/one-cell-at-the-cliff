# L109 PREREG — per-side membership-ladder rebase (L107 follow-up)

Written BEFORE rollouts. All pins re-derived from STORED artifacts (L44 rule),
not from log sentences.

## Card amendment (L44 instance, disclosed)

Card text says "2 FRESH batches (B5 901-916, B6 1001-1016)" — but l94's
stored meta (results_l94.json) shows its batches WERE B4 801-816, B5 901-916,
B6 1001-1016 (seeds verified present in raw_l94.npz). The card's labels
collide with already-run seeds; truly fresh batches are
**B7 1101-1116 and B8 1201-1216** (verified absent from raw_l94.npz AND
raw_l107.npz). Amendment: B7/B8 are the fresh sample.

## Design

4 arms x 16 seeds x 2 fresh batches, l107_run.py machinery VERBATIM
(same graphs, same two-generator draw order, same schedule, same gains;
cut re-bisected deterministically then asserted == stored).

- full  = closure @ .153125 (cfn form)   — anchor arm
- b65   = l65     @ .14
- h65   = l65     @ .153125
- cut   = closure minus top-77 dn_new @ g_cut (stored 0.14510760426521305, K 77)

Anchor seeds run FIRST inside the same script (not part of the fresh sample):
801 (in raw_l94 cfn + raw_l107 all arms), 901 (in raw_l94 cfn only).

## Pinned expectations (from stored artifacts, pre-derived)

L107 B4 Ti per-side cells (re-derived from raw_l107.npz this tick, exact):

| arm  | k_L | k_R | meanL | meanR |
|------|-----|-----|-------|-------|
| full | 3   | 5   | .378  | .425  |
| b65  | 16  | 16  | 1.000 | .993  |
| h65  | 16  | 16  | .933  | .990  |
| cut  | 16  | 0   | .836  | .143  |

(results_l107.json m_ti agrees on all means; k-side cells are new derived
pins.) l94 cfn per-side B4 = full row above (same arm).

## Gates

- C0A (HARD STOP if fail):
  (a) full_801, full_901 == raw_l94 cfn_801/cfn_901 max|d| 0.0 exactly
      (mm, xm, 8 Ti/Tr pools, af);
  (b) b65/h65/cut_801 == raw_l107 same seeds max|d| 0.0 exactly;
  (c) re-bisected g_cut == stored 0.14510760426521305 bit-exact.
- C0B (verdict, BEFORE any fresh pin; L85 rule): my cells code on
  raw_l107.npz reproduces results_l107.json pinned reads EXACTLY
  (k_ti all 4 arms; m_ti 5 fields x 4 arms; m_tr dL/dR x 4 arms).
- C1: every arm-seed settle af in (0.01, 0.9); b65 fresh-mean in
  [.105056, .113056] (l107 band); cut af disclosed (staircase, L92 form).
- P1 PRIMARY (per-side ladder law, pooled over 32 fresh = B7+B8):
  - cut   L recovery:  pooled k_L >= 24/32 (p-hat .75)
  - cut   R collapse:  pooled k_R <= 8/32  (p-hat .25)
  - b65   both sides:  pooled k_L >= 30 and k_R >= 30 (p-hat .917,
    matching l91's 48/48 family level)
  - h65   both sides:  pooled k_L >= 30 and k_R >= 30
  - full  dead/side:   pooled k_L <= 11 and k_R <= 11 (p-hat .333)
  P1 LAW holds iff ALL five conditions hold. Full-precision Wilson lb/ub
  (z=1.959964) reported per cell, never rounded (L90 rule).
- P2 (secondary, means): per-side ladder ORDER survives —
  meanL: cut > full; meanR: b65 > cut; non-monotone per-side shape
  (cut R < full R is the L107 signature) reported as replicate/draw.
- P3 (batch-stability disclosure, L88/L90 rule): per-batch k for every
  arm-side; axes replicating on BOTH batches individually = batch-stable;
  pooled-only = batch-drawn. THIS is the settle: law vs single-batch draw.
- Descriptives: Tr per-side means, seg duties, dom_ratio lock count,
  af table. Zero-rollout extra: l94's stored cfn B5+B6 (901-1016, 32
  seeds) per-side cells computed from raw_l94.npz to widen the full-arm
  base axis to n=80 disclosed (not part of P1).

## Interpretation (pre-registered)

- P1 LAW → side-specific membership law is real; per-side reads become
  the required form for any future substrate edit (L46 class promoted).
- cut_L or cut_R fails while b65/h65 hold → the ladder's cut step is a
  batch draw; membership law weakens to "distributed kill" only.
- b65 fails → l65 robustness itself is stream/batch-fragile (protocol
  finding, weakens L94's framing); disclose loudly.

## Scope / disclosures

Single connectome (BANC closure), Ti pair primary; h65 af-unmatched by
design; anchor seeds (801, 901) excluded from fresh pools; pooled n = 32
per arm-side (bars above stated /32); no live changes; sessions/
untouched.
