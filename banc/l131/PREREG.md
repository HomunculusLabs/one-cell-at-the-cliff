# L131 PREREG — rank-25/26 completion XOR (ideas 69, tick 154)

Card: does ONE named cell carry the k24-PARTIAL -> k26-SUPER flip inside
the ng[19:29] window (L126: transition band ranks 25-26)? The L120
cell-204 pattern at window scale. Static pins (l131/static.json, zero
rollouts, extraction re-pinned == l121/l123/l126 stored EXACT):
- rank 25 = ng_desc[24] = id **1110**, mass .006436
- rank 26 = ng_desc[25] = id **319**, mass .006045
- pair delta 3.91e-04 (mass-twins at 4-decimal pin resolution)
- cutng25 = ng_desc[:25] = wA + {1110} ONLY: n=21784, edges=644084,
  mass_removed .2350 (card estimated ~.2348 — confirmed within rounding)
- nesting verified strict: wA < ng25 < ng26; DNg100 in NO drop.

## Run design (l126 machinery VERBATIM: pools, graphs, draw order, noise)

- ARMS (12): full, b65, cut, cut19, cut58, cutng19, cutng23, cutwA,
  **cutng25 (the XOR arm)**, cutng26, cutng29, cutk5.
  cutng21/cutng28 NOT run (l126 interpolation points, 1 batch each,
  disclosed; C0A-126 extension covers the arms actually shared).
- FRESH B24 = 2801-2816, asserted absent from raw_l113 + l115 + l117 +
  l118 + l119 + l120 + l121 + l122 + l123 + l124 + l125 + l126 + l127 +
  l128 (14 npzs) BEFORE any rollout.
- Gains: 9 STORED-FORM (deterministic re-bisects land EXACT): cut (l107),
  cut19 (l111), cut58 (l113), cutk5 (l117), cutng19/cutng29 (l121), cutwA
  (l123), **cutng23 + cutng26 NEW stored-form** (l126 prefix_fresh_gains
  0.14696856379508969 / 0.14545363783836368). ONE fresh bisect: cutng25
  (.14-.16 band is a DISCLOSURE, never an abort; staircase disclosed).
- ANCH = [801, 901] first; raw checkpoint to l131/raw_l131.npz BEFORE
  analysis; resume via l131/raw_partial.npz (own dir, direction-checked).

## Anchors (all must PASS before any B24 number is pinned)

- C0A 59th consecutive: 5 stored arms (full, b65, cut, cut19, cut58),
  10 old keys, vs raw_l113 at 801/901 — max must be 0.0.
- C0A-120 (cutk5 vs raw_l120), C0A-121 (cutk5/cutng19/cutng29 vs
  raw_l121), C0A-122 (same 3 vs raw_l122), C0A-123 (4 arms incl wA vs
  raw_l123), C0A-124 (4 vs raw_l124), C0A-125 (3 vs raw_l125): retained,
  22 keys x arms x 2 seeds, max 0.0.
- C0A-126 EXTENDED: ALL 9 shared cut arms with raw_l126 (cut, cut19,
  cut58, cutk5, cutng19, cutng23, cutwA, cutng26, cutng29) — was 3 arms
  in l127/l128; extension registered HERE (forward-chain addendum form).
- NEW C0A-127: 6 shared cut arms (cut, cut19, cut58, cutk5, cutng19,
  cutng29) vs raw_l127. NEW C0A-128: same 6 vs raw_l128.
- B-CERT (C0B line): before ANY B24 read, verdict machinery recomputed on
  raw_l128 B23 must reproduce results_l128.json's Ti table on ALL its
  table arms, exact (rounding-path identical, l109/l111 atom).
- P4 health: af in (0.01, 0.9) all arms/seeds; b65 af-mean band
  [0.105056, 0.113056].

## PRIMARY registered reads (B24; criteria VERBATIM L118-L126)

Arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B24). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band: meanR in [.35,.50]
AND kR in 3..8.

- X1 (rank-25 COMPLETES): cutng25 is SUPER or RESTORE -> id 1110 carries
  the kill->super flip alone; report dR(k25->k26) as the k26-adds-nothing
  leg.
- X2 (rank-26 COMPLETES): cutng25 is PARTIAL (both legs: band AND kR
  3-8) -> id 319 is the completing cell; same-batch cutng26 SUPER is the
  context leg.
- X3 (NEITHER — registered degenerate branch, L55 rule): cutng25 KILLs
  or lands outside every band -> NO single named cell carries the flip
  at this resolution; the {1110, 319} PAIR stays the unit. Report which
  branch fired; never read X1/X2 off a band-edge miss.
- P2 (confound disclosure, no gate): the two arms differ by one full cell
  mass each way (m1110 .006436 vs m319 .006045); the alternative reading
  is "any ~.006 mass beyond .2350 completes". Report alongside X1/X2.
- P3 (L132-prebase): transition arms {cutng23, cutwA, cutng26, cutng29}
  re-rolled on B24; POOLED B21+B24 n=32 full-precision Wilson per arm
  (L90 form) registered HERE so L132 reads without new rollouts.

## Secondaries (disclose, never abort)

- S1: cutk5 KILL 12th consecutive batch (B12..B24); pooled R4 union
  B16..B24 n=144 full-precision Wilson.
- S2: endpoints cutng19/cutng29 9th batch. NOTE (3-batch pattern): the
  ng19 KILL label failed its paired-dR leg (-.196/-.180 vs -.20) three
  straight batches while kR/meanR legs held — report the legs separately;
  the dR leg is informational, the kR+meanR legs carry the label.
- S3: cutwA PARTIAL band 4th batch (B18 .413/5, B19 .376/4, B21 .365/3,
  B24).
- Watch (no gate): Ti_L through the same steps (ng29 L-death
  anticorrelation), Sr_R (killed by every ng dose, 5+ batches), Tr_R.
- Sanity: cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12; Sr b65
  cells.
- full-arm B24 band disclosure (never abort): Ti L (.25,.48), R
  (.35,.58); Sr L (.08,.25), R (.30,.50).

## Disclosure list

cutng21/cutng28 not re-run (single-batch l126 points stand); scr arms
not re-run (l128 rebase stands); cutng25 fresh gain band disclosed;
single-batch X1/X2 verdict labeled single-batch (the L132 pooled table
carries the robust read); P4/band cells secondary.
