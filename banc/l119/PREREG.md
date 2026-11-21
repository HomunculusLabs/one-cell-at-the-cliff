# L119 PREREG — minimal-glut-subset-step (registered BEFORE l119_run.py)

Card: LANE.md ideas-60 L119. Registered 2026-11-17 ~07:30 by Miso, tick 143.
All expectation numbers below are re-derived from STORED artifacts
(results_l117.json / l119 static cross-check), never from log sentences
(L44 rule). Zero rollouts before this file is complete.

## Arms (10)

Anchors (stored seeds 801/901 vs raw_l113 + stored-gain asserts):
full, b65, cut, cut19, cut58.
NEW ladder arms (deterministic, mass-desc positional filter of glut_desc;
l119/static.json pins, run asserts STOP on miss):
- cutk1  drop [286]                 mass .0096  n 21808  edges 647809
- cutk2  drop [286, 313]            mass .0185  n 21807  edges 647680
- cutk3  drop [286, 313, 561]       mass .0268  n 21806  edges 647526
- cutk5  drop [204,286,313,561,32014] mass .0425 n 21804 edges 647252
  (k5 re-derived == l117/static.json ladder k5 EXACTLY, zero-rollout check)
NEW draw arm (pinned RNG, torch.Generator(1190).randperm(19)[:5]):
- cutr5  drop [763,994,1304,1434,1777] mass .0231 n 21804 edges 647501
  overlap_with_heaviest5 = 0; excludes #1 and #2; drawn from glut mass
  positions {7,9,12,16,17} (lighter half).
Seeds: [801, 901] anchors + FRESH B14 = 1801-1816 (asserted absent from
raw_l113.npz, l115/raw_l115.npz, l117/raw_l117.npz, l118/raw_l118.npz).
NOTE (L44 batch-label class): the card says "fresh B13" — B13 was consumed
by L118 (1701-1716); B14 used instead, disclosed here.

## P0 anchors (gates)

- C0A FULL-BATCH bit-identity: stored arms {full,b65,cut,cut19,cut58} x
  seeds {801,901} x keys {mm, xm, Ti/Tr f/e x L/R} vs raw_l113.npz, plus
  af keys; max |diff| MUST be 0.0 (49th consecutive chain anchor if green).
- Stored-gain re-bisects EXACT: g_cut == 0.14510760426521305 (l107),
  g_cut19 == 0.15096808075904844 (l111), g_cut58 == 0.15417299151420596
  (l113), g_cutk5 == 0.13981970071792604 (l117 dose_gains; NEW anchor
  class for this run). cutk1/cutk2/cutk3/cutr5 bisected FRESH.
- Gain band .14-.16 for the four fresh-bisected arms is a DISCLOSURE band,
  never an abort (l117 precedent: cutk5 .13982 outside, af-matched).
- C0B machinery certification on stored raw_l113 (Ti+Tr tables, all 5
  stored arms, B10) BEFORE any L119 pin (L85/L109 rule).

## P1 PRIMARY — step location (Ti_R dose curve, B14, n=16)

Kill criterion (L118 registered form, verbatim): an arm KILLS iff
  meanR <= m0 - .10  AND  kR <= 4  AND  mean paired dR <= -.20,
where m0 = full-arm Ti meanR on B14, paired legs per-seed vs full.
Registered outcomes (k* = min k in {1,2,3,5} that kills):
- k*=1: single-cell control point (.0096 mass) — ultra-local placement.
- k* in {2,3}: step at 2-3 cells.
- k* = 5 with {1,2,3} clean: step lands in the 4-cell window {k=4..5}
  (k=4 untested, disclosed); consistent with l117 B12 (k5 .023/0 killed,
  full .473/7).
- No arm kills incl. k5: BATCH-DRIFT disclosed (l117's k5 kill was B12);
  the k5 point re-rolls (L118 lottery class) — never rounded into a kill.
Same-batch curve points: k in {0 (full), 1, 2, 3, 5, 19 (cut19)} all fresh
on B14; k10/k15 quoted from l117 stored B12 as CROSS-BATCH context only.

## P2 PRIMARY — cutr5 (random 5-of-19 glut, .0231 mass, B14)

- KILLS (criterion above): glut IDENTITY at 5-cell granularity — any
  5-of-19 kills R; mass irrelevant (.0231 < k3 .0268 which may not kill).
- SURVIVES (meanR >= m0 - .10): the HEAVIEST-5 placement carries the kill
  (mass-ranking-specific); random-5 at 0 overlap cannot reproduce it.
- Between (partial): MIXED band, disclosed with paired legs + kR, never
  rounded (L118 precedent).

## Secondaries (registered, no gate)

- L-axis (Ti_L): L117 measured NON-MONOTONE L (.364/.196/.266/.710/.712 at
  k 0/5/10/15/19 on B12); B14 curve reported, no monotonicity claim.
- Sr_R watch (lottery axis, L116/L117/L118): reported, no gate.
- P4: 0.01 < af < 0.9 every arm/seed; b65 af-mean band [.105056, .113056].
- Full-arm B14 disclosure bands: Ti L (.30, .45) R (.35, .55);
  Sr L (.08, .25) R (.30, .50) (L118 form).
- Sanity cells: Ti cut kL >= 14; b65 16/16 BOTH sides; cut19 kL >= 12.
  A miss is DISCLOSED, never an abort.

## Verdict output

l119/results_l119.json: p0, p4, table (5 pairs x 10 arms, per-side
k/mean/Wilson), dose (Ti/Sr R+L curve incl. k* classification), r5
classification, legs, sr_watch, sanity. raw_l119.npz checkpointed BEFORE
analysis (L45a rule); raw_partial.npz resume-safe per-seed.
