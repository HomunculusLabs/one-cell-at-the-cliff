# L133 PREREG — wA-plus-319-alone XOR (ideas 70, tick 155)

Card: the missing XOR leg from L131's P2 disclosure — cutng25p = wA +
rank 26 (id 319) ONLY. If it PARTIALs, 1110-vs-319 is a clean identity
XOR at near-identical mass and the L120 cell-204 claim upgrades to
mass-matched; if it SUPERs, the flip is position-thin and BOTH
transition cells complete (report honestly). Static pins
(l133/static.json, zero rollouts, extraction re-pinned == l121/l123/
l126/l131 stored EXACT):
- rank 25 = id 1110 m .006436 / rank 26 = id 319 m .006045 (== l131
  pins EXACT); pair delta 3.91e-04.
- cutng25p = ng_desc[:24] ∪ {319} — NOT a prefix (skips 1110):
  n=21784 (== ng25 count), edges=644072, mass_removed .2346 (delta vs
  ng25 = -3.9e-04 = the pair delta: mass-matched by construction).
- Set identities verified: wA ⊂ 25p; 25p ⊂ 26 (26 = 25p ∪ {1110});
  (25 ∪ {319}) − {1110} = 25p; DNg100 in NO drop.

## Run design (l131 machinery VERBATIM: pools, graphs, draw order, noise)

- ARMS (13): full, b65, cut, cut19, cut58, cutng19, cutng23, cutwA,
  cutng25, **cutng25p (the XOR arm)**, cutng26, cutng29, cutk5.
- FRESH B25 = 2901-2916, asserted absent from raw_l113 + l115 + l117 +
  l118 + l119 + l120 + l121 + l122 + l123 + l124 + l125 + l126 + l127 +
  l128 + l131 (15 npzs) BEFORE any rollout.
- Gains: 10 STORED-FORM (deterministic re-bisects land EXACT): cut
  (l107), cut19 (l111), cut58 (l113), cutk5 (l117), cutng19/cutng29
  (l121), cutwA (l123), cutng23/cutng26 (l126), **cutng25 NEW
  stored-form (l131 fresh gain 0.1454454553127289)**. ONE fresh
  bisect: cutng25p (.14-.16 band is a DISCLOSURE, never an abort;
  staircase disclosed).
- ANCH = [801, 901] first; raw checkpoint to l133/raw_l133.npz BEFORE
  analysis; resume via l133/raw_partial.npz (own dir, direction-checked).

## Anchors (all must PASS before any B25 number is pinned)

- C0A 60th consecutive: 5 stored arms (full, b65, cut, cut19, cut58),
  10 old keys, vs raw_l113 at 801/901 — max must be 0.0.
- C0A-120 (cutk5 vs raw_l120), C0A-121 (3 vs raw_l121), C0A-122 (3 vs
  raw_l122), C0A-123 (4 vs raw_l123), C0A-124 (4 vs raw_l124), C0A-125
  (3 vs raw_l125), C0A-126 (9 vs raw_l126), C0A-127 (6 vs raw_l127),
  C0A-128 (6 vs raw_l128): retained, 22 keys x arms x 2 seeds, max 0.0.
- NEW C0A-131: ALL 10 shared cut arms (cut, cut19, cut58, cutk5,
  cutng19, cutng23, cutwA, cutng25, cutng26, cutng29) vs raw_l131
  (cutng25p has NO stored counterpart — excluded by name).
- B-CERT (C0B line): before ANY B25 read, verdict machinery recomputed
  on raw_l131 B24 must reproduce results_l131.json's Ti table on ALL
  12 its table arms, exact (rounding-path identical, l109/l111 atom).
- P4 health: af in (0.01, 0.9) all arms/seeds; b65 af-mean band
  [0.105056, 0.113056].

## PRIMARY registered reads (B25; criteria VERBATIM L118-L131)

Arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B25). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band: meanR in [.35,.50]
AND kR in 3..8.

- W1 (IDENTITY XOR): cutng25p lands in the PARTIAL band (BOTH legs:
  band AND kR 3-8) -> 1110-vs-319 is a clean identity XOR at
  mass-match; L120's cell-204 claim upgrades to mass-matched. Context
  legs: same-batch cutng25 SUPER (X1 replication) and cutng26 SUPER.
- W2 (POSITION-THIN): cutng25p SUPER or RESTORE -> BOTH transition
  cells complete individually; the window claim revises to either-cell
  (report honestly, L131's flip is thinner than one cell).
- W3 (registered degenerate branch, L55 rule): cutng25p KILLs or lands
  outside every band -> neither branch; report which band it landed in;
  never read W1/W2 off a band-edge miss.
- P2 (mass disclosure, no gate): 25p vs 25 differ ONLY by which twin is
  in the drop (319 vs 1110), 3.9e-04 mass delta; the mass twin design
  is what makes W1 a cell-IDENTITY claim rather than a mass claim.

## Secondaries (disclose, never abort)

- S1: cutk5 KILL 13th consecutive batch (B12..B25); pooled R4 union
  B16..B25 n=160 full-precision Wilson.
- S2: endpoints cutng19/cutng29 10th batch (dR-leg note retained: the
  ng19 dR leg is informational, kR+meanR legs carry the label).
- S3: cutwA PARTIAL band 5th batch (B18 .413/5, B19 .376/4, B21
  .365/3, B24 .436/6, B25).
- S4 (NEW): cutng25 SUPER 2nd batch — L131's X1 replication; pooled
  B24+B25 n=32 Wilson.
- P3: transition arms {cutng23, cutwA, cutng26, cutng29} pooled
  B21+B24+B25 n=48; cutng25 pooled n=32; cutng25p single-batch n=16
  (disclosed).
- Watch (no gate): Ti_L through the same steps (ng29 L-death
  anticorrelation), Sr_R (killed by every ng dose, 6+ batches), Tr_R.
- Sanity: cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12; Sr b65
  cells.
- full-arm B25 band disclosure (never abort): Ti L (.25,.48), R
  (.35,.58); Sr L (.08,.25), R (.30,.50).

## Disclosure list

cutng21/cutng28 not re-run (l126 single-batch points stand); scr/cl
arms not run (l127/l128 stand); cutng25p fresh gain band disclosed;
cutng25p verdict labeled SINGLE-BATCH (n=16, no pooled citable until a
rebase); pooled keys renamed k144->k160/k32->k48 (metric code
otherwise verbatim); P4/band cells secondary.
