# L118 PREREG — mass-matched-pure-nonglut-19 (registered 2026-11-17 05:5x, BEFORE any rollout)

Question (ideas 59 card): L115's random-19-of-heavy-77 draws at mass
.106-.131 did NOT kill Ti_R (kR 3/13/10, meanR .329-.629) while BOTH true
partition halves do (cut19 glut-19 @ .1103: kR 0 everywhere; cut58 non-glut
58 @ .3921: kR 0) — and L117 sharpened it: the R-kill fires COMPLETE at
just the 5 heaviest glut (mass .0425). Is the R axis's kill about CLASS
COHERENCE (any single-transmitter-class half at glut-19 mass kills R) or
about GLUT IDENTITY (only glutamatergic removal kills R at this mass)?

## Design (l117 machinery VERBATIM — 5-pair pools, graphs, gains, draw order)

- NEW arms cutnga/cutngb/cutngc = closure minus 19 NON-glutamatergic heavy
  cells, each mass-matched to the glut-19's UNROUNDED share .11033 by
  rejection sampling (pinned torch.Generator seeds 1180/1181/1182, tol
  .0045, no fallback fired). CARD AMENDMENT (registered pre-run): THREE
  draws, not the card's one — L115's own lesson is that draw-to-draw spread
  is a live axis (its 3 random draws spread kL 15/13/10); n=3 matches that
  form. Pure = ZERO glutamate cells in every drop (asserted in-run).
- Reference arms retained verbatim: full, b65, cut (all 77), cut19, cut58.
- Seeds: anchors [801, 901] (C0A vs raw_l113, stored arms only) + FRESH
  B13 1701-1716 (verified absent from raw_l113 {801,901,1401-1416},
  raw_l115 {801,901,1501-1516}, raw_l117 {801,901,1601-1616} pre-launch;
  asserted in-run vs all three).
- Gains: g_cut + g_cut19 + g_cut58 re-bisected, asserted == stored EXACT
  (.14510760426521305 / .15096808075904844 / .15417299151420596); draw
  gains bisected FRESH (bracket [.12,.18]; expectation band [.14,.16] from
  stored arm gains — mass-matched to cut19's own mass, cut19 landed .1510;
  outside band = DISCLOSED, never abort).

## Static pins (from l118_static.py -> l118/static.json; asserted in-run; STOP on miss)

- target_unrounded .11033 (the .1103 pin is its 4dp rounding), tol .0045,
  feasibility [.07886, .19461]; nong58 total share .3921.
- cutnga: seed 1180, mass .11187 (|dev| .00154), n 21790, edges 645963.
- cutngb: seed 1181, mass .10958 (|dev| .00075), n 21790, edges 646088.
- cutngc: seed 1182, mass .11145 (|dev| .00113), n 21790, edges 646007.
- Pairwise cell overlaps 7/4/9 of 19 (independent-ish draws, disclosed).
- Drops ⊂ heavy-77, disjoint from cut19_drop, zero glutamate, DNg100 not
  in heavy-77 (re-asserted — no draw arm can touch the drive channel).

## Registered anchors (MUST PASS before any new read)

- C0A: the 5 STORED arms (full/b65/cut/cut19/cut58) x anchor seeds
  {801, 901} x l113-schema keys (mm, xm, Ti/Tr f/e pools, af) ==
  raw_l113.npz EXACT, max|d| == 0.0 (48th consecutive chain anchor).
  Enumerated OLD keys + OLD arms only (L59 rule); the new cutng arms and
  Ta/Sr/Pr pools are excluded from C0A BY NAME.
- C0B certification BEFORE any L118 pin: pair-generalized side_k machinery
  on STORED raw_l113.npz must reproduce results_l113.json table_b10 +
  tr_b10 for ALL 5 stored arms, every pinned read EXACT (l109/l113
  rounding path: round per-seed duty to 3 then mean; k = duty >= .5).
- C1 health: 0.01 < af < 0.9 every arm/seed (8 arms incl. cutng); b65
  af-mean band [.105056, .113056] (l113/l116/l117 pin).

## Registered read (primary = Ti_R on B13, n=16, 3 draws vs full)

Per pair (Ti/Tr/Ta/Sr/Pr), per side: duty07 mean + k-cell + Wilson CI for
all 8 arms. Base EXPECTATION bands (stored: l101 51-seed, l113/l115/
l116/l117): full Ti meanR ~ .42-.51 (B11 .424 / B12 .473 / B10 .505),
full kR 5-9; cut19 Ti meanR <= .05 kR 0; cut58 meanR .207-.232 kR 0;
L115 random-19 (mixed) meanR .329-.629 kR 3-13. A fresh-B13 full-arm read
OUTSIDE its band is DISCLOSED as batch drift (the paired same-seed delta
vs full stays primary — L45b form; k-cells diagnostic only).

Classification for Ti_R (m0 = full-B13 meanR, per draw d in {a,b,c}):
- COHERENCE-KILL iff >= 2 of 3 draws have meanR(d) <= m0 - .10 AND
  kR(d) <= 4 AND paired mean dR(d) <= -.20 (the cut19/cutk5 signature).
  Reading: any single-class-coherent half at glut-19 mass kills R; glut
  identity irrelevant.
- GLUT-IDENTITY iff >= 2 of 3 draws have meanR(d) >= m0 - .10 (survivor
  side of the L115 band). Reading: only glutamatergic removal kills R at
  this mass; cut58's R-dead then needs a 58-cell-mass story (L118b).
- Else MIXED (disclosed, draw-to-draw spread reported per draw).

Secondary (registered, no gate): L axis — the L115 mass-law predicts a
.11-mass 19-cut RESTORES Ti_L (random-19s .525-.793, cut19 .712-.790):
report meanL/kL per draw; a draw that kills R while restoring L would
isolate the two axes cleanly. Sr_R watch stays a lottery axis (no gate,
L116/L117 form). Tr/Ta/Pr table reported.

Paired leg: per-seed dR vs full on B13; n_down(d) = count(dR <= -.20).
