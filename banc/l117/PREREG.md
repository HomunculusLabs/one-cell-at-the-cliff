# L117 PREREG — glut-dose-ladder (registered 2026-11-17 04:2x, BEFORE any rollout)

Question (ideas 59 card + L116 amendment): L115 split the axes — L-restore is
MASS-LIKE (any ~19-58 cells flip it) but the Ti_R KILL needs a coherent
transmitter-class half (0/3 random-19 draws killed R vs 0/16 for both true
partition halves), and the n=3 covariate (glut 8/7/3 -> kR 3/13/10) is
unresolved. Remove k of the 19 glutamatergic heavy cells for k in {5,10,15}:
does R-kill strength track k monotonically (FRACTION), or does R stay
full-like until the whole class is gone (COHERENCE)? Watch Sr_R alongside
Ti_R (L116: it died under BOTH half-removals yet re-drew marginal under full
cut — marginal-side lottery vs class coherence is exactly what a dose curve
separates).

## Design (l116 machinery VERBATIM — 5-pair pools, graphs, gains, draw order)

- Dose selection DETERMINISTIC, no RNG: `heav` is already in descending
  individual cord-out-mass order, so the positional glut filter gives the
  k HEAVIEST glut cells — cutk{5,10,15} = closure minus those k. Dose axis
  = COUNT k (primary); mass column disclosed (L118 owns mass-matching).
- Dose endpoints in-run: full (k=0) and cut19 (k=19, the whole class).
  Reference arms retained verbatim: b65, cut (all 77), cut58.
- Seeds: anchors [801, 901] (C0A vs raw_l113, stored arms only) + FRESH
  B12 1601-1616 (verified absent from raw_l113 batches pre-launch:
  stored = {801,901,1401..1416}).
- Gains: g_cut + g_cut19 + g_cut58 re-bisected, asserted == stored EXACT
  (.14510760426521305 / .15096808075904844 / .15417299151420596); dose
  gains bisected FRESH (bracket [.12,.18]; registered expectation band
  [.14,.16] from the stored arm gains — outside = DISCLOSED, never abort).

## Static pins (from l117_static.py, zero rollouts; asserted in-run; STOP on miss)

- glut-19 mass shares desc: .00958 .0089 .00827 .00791 .00782 .00736
  .00593 .0057 .00566 .00515 .0051 .00475 .00459 .00431 .00414 .00398
  .00387 .0038 .00348 (sum .1103 == mass_split glut19, l113 pin).
- k5:  n 21804, edges 647252, mass_removed .0425 (38.5% of glut-19 mass)
- k10: n 21799, edges 646680, mass_removed .0723 (65.5%)
- k15: n 21794, edges 646157, mass_removed .0952 (86.3%)
- Dose drops are strict subsets of cut19_drop; DNg100 not in heavy-77
  (l115 pin, re-asserted — no dose arm can touch the drive channel).

## Registered anchors (MUST PASS before any new read)

- C0A: the 5 STORED arms (full/b65/cut/cut19/cut58) x anchor seeds
  {801, 901} x l113-schema keys (mm, xm, Ti/Tr f/e pools, af) ==
  raw_l113.npz EXACT, max|d| == 0.0 (47th consecutive chain anchor;
  l116's full-batch C0A covered B10 — B12 is fresh, no stored
  counterpart, disclosed). Enumerated OLD keys only (L59 rule); the new
  cutk arms and Ta/Sr/Pr pools are excluded from C0A BY NAME.
- C0B certification BEFORE any L117 pin: pair-generalized side_k machinery
  on STORED raw_l113.npz must reproduce results_l113.json table_b10 +
  tr_b10 for ALL 5 stored arms, every pinned read EXACT (l109/l113
  rounding path: round per-seed duty to 3 then mean; k = duty >= .5).
- C1 health: 0.01 < af < 0.9 every arm/seed (8 arms incl. cutk); b65
  af-mean band [.105056, .113056] (l113/l116 pin).

## Registered read (primary = Ti_R and Sr_R dose curves on B12, n=16)

Per pair (Ti/Tr/Ta/Sr/Pr), per side: duty07 mean + k-cell + Wilson CI for
all 8 arms. Base EXPECTATION bands (stored: l101 51-seed, l113/l115/l116):
full Ti meanR ~ .42-.51 (B11 .424 / B10 .505), Sr meanR ~ .39-.49, Ti meanL
~ .36-.40, Sr meanL ~ .14-.17; cut19 Ti kR -> 0 (.026/.043 both batches),
Sr kR -> 0 (.101). A fresh-B12 full-arm read OUTSIDE its band is DISCLOSED
as batch drift (the paired same-seed delta vs full stays primary — L45b
form; k-cells are diagnostic only, known swing: full kR 6->9 across
B11->B10).

Dose-curve classification for Ti_R (m(k) = B12 meanR of cutk, m0 = full,
m19 = cut19):
- COHERENCE iff m(k) >= m0 - .10 for ALL k in {5,10,15} AND m19 <= .15.
- FRACTION iff m(k) non-increasing in k (<= one inversion of .03) AND
  m(15) < m0 - .10.
- Else MIXED (disclosed).
Paired leg: per-seed dR vs full on B12; n_down(k) = count(dR <= -.20).

Sr_R watch (L116 amendment, registered):
- FRAGILE iff Sr m(k) <= m0 - .10 at EVERY k in {5,10,15} (any dose kills
  it — marginal-side lottery, perturbation class).
- CLASS-LIKE iff Sr m(k) >= m0 - .10 for some k < 15 and dies only at
  15/19 (tracks the Ti_R story).

L-axis secondary (descriptive, no gate — L115/L116 already own the claim):
expect meanL monotone RISING with k toward cut19's restore level.

Ladder sanity (P3-form reference cells, from stored B10/B11): B12 cut kL
>= 14, b65 kL = 16 AND kR = 16, cut19 kL >= 12 (bands from 16/16, 16/16,
15/14). Miss = disclose, never abort (L109 rule: reference cells are
secondary).

## Honesty clauses

- One batch (n=16) + the two anchor seeds; k-cell reads carry the L88/L90
  batch swing — the verdict names which reads are batch-fragile if the
  L118 mass-matched control later contradicts.
- Mass and count co-vary by construction here (heaviest-first ladder);
  this design CANNOT separate mass-dose from count-dose at fixed class —
  that separation is L118's registered job. Scope every verdict
  accordingly.
