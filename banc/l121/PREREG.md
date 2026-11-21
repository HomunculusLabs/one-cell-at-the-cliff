# L121 PREREG — nonglut-dose-ladder (registered BEFORE l121_run.py)

Card: LANE.md ideas-61 L121. Registered 2026-11-17 ~10:55 by Miso, tick 145.
Expectation numbers re-derived from STORED artifacts (l121/static.json —
zero-rollout derivation run BEFORE this file; l118/l119/l120 results jsons),
never from log sentences (L44 rule). Zero rollouts before this file.

## Arms (9)

Anchors (stored seeds 801/901 vs raw_l113): full, b65, cut, cut19, cut58.
- cutk5 RETAINED (not in the card; registered purposes): (a) C0A-120
  forward-chain anchor vs raw_l120 (L120 ran every arm at all 18 seeds, so
  cutk5 has a stored counterpart at 801/901); (b) free B16 replication read
  of the L120 XOR kill (currently single-batch B15; L88/L90 batch rule).
  drop [204,286,313,561,32014] mass .0425 n 21804 edges 647252, pins
  asserted == l117/l119/l120 stored EXACTLY.
NEW dose ladder (deterministic heaviest-first positional prefixes of the 58
NON-glutamatergic heavy cells in mass-DESC order; l121/static.json pins,
run asserts STOP on miss; NO RNG anywhere in L121):
- cutng19 drop ng_desc[:19]  mass .1946  n 21790  edges 644729
- cutng29 drop ng_desc[:29]  mass .2588  n 21780  edges 643623
- cutng39 drop ng_desc[:39]  mass .3132  n 21770  edges 642698
- k58 endpoint = the cut58 arm itself (set identity + n + edges recomputed
  on the same mask in static: 641205, mass .3921 == mass_split other58).
Card's "~.11/.20/.30" guess was WRONG on k19: heaviest-first 19 = .1946
(almost 2x glut-19's .1103). ng top-5 ids [32160,250,744,493,3248]; the
single heaviest heavy cell (32160, .01715) is NON-glutamatergic.
Seeds: [801, 901] anchors + FRESH B16 = 2001-2016 (asserted absent from
raw_l113.npz, l115, l117, l118, l119, AND l120/raw_l120.npz).

## P0 anchors (gates)

- C0A FULL-BATCH bit-identity vs raw_l113: stored arms {full,b65,cut,cut19,
  cut58} x seeds {801,901} x keys {mm,xm,Ti/Tr f/e x L/R} + af; max |diff|
  MUST be 0.0 (51st consecutive chain anchor if green).
- C0A-120 (NEW anchor class): cutk5 x seeds {801,901} vs l120/raw_l120.npz
  on ALL pool keys (Ti/Tr f/e + Ta/Sr/Pr a/b, both sides) + mm/xm + af;
  max |diff| MUST be 0.0. cutng19/29/39 have NO stored counterpart
  anywhere (excluded BY NAME, disclosed).
- Stored-gain re-bisects EXACT: g_cut == 0.14510760426521305 (l107),
  g_cut19 == 0.15096808075904844 (l111), g_cut58 == 0.15417299151420596
  (l113), g_cutk5 == 0.13981970071792604 (l117/l119/l120).
- cutng19/cutng29/cutng39 bisected FRESH; gain band .14-.16 is a DISCLOSURE
  band, never an abort (l117-l120 precedent).
- C0B machinery certification on stored raw_l113 (Ti+Tr tables, all 5
  stored arms, B10) BEFORE any L121 pin (L85/L109 rule) — in verdict.

## P1 PRIMARY — does the non-glut R-kill track MASS or POOL-COMPLETENESS?

Kill criterion (L118/L119/L120 registered form, verbatim): an arm KILLS iff
  meanR <= m0 - .10  AND  kR <= 4  AND  mean paired dR <= -.20,
where m0 = full-arm Ti meanR on B16, paired legs per-seed vs full on B16.
Same-batch curve points: {0 (full), 19 (.1946), 29 (.2588), 39 (.3132),
58 (cut58, .3921)} all fresh on B16.
Registered outcomes:
- MASS-FRACTION iff cutng19 kills: the R axis falls with removed non-glut
  mass already at .1946; report monotonicity of meanR across 19/29/39/58
  (deepening expected, no gate on the slope).
- POOL-COHERENCE/THRESHOLD iff NONE of cutng19/29/39 kills (each meanR >=
  m0 - .10 AND kR >= 12) while cut58 kills in-batch: the non-glut kill
  needs near-whole-pool removal — mirroring the glut-side step (L117/L119)
  at pool scale.
- Else MIXED/LOTTERY (L118 class): per-dose kill booleans + means disclosed,
  no rounding to either story.

## P2 (registered, no gate) — cutk5 B16 replication

Kill criterion verbatim on cutk5/B16: kill = 4th independent batch
replicate (B12/B14/B15 + B16) of the L117 step / L119 placement / L120 XOR;
no-kill = batch-drift DISCLOSED (L118 lottery class), never a fail — the
L120 single-cell claim keeps its B15 evidence either way.

## Secondaries (registered, no gate)

- Ti_L watch: L115 mass-law predicts removal-side L-restore grows with mass
  (random-19s .525-.793 at .11; cut58 .790 at .3921); report meanL/kL per
  dose, no claim (l119 measured single-cell chaos on L).
- Sr_R watch (lottery axis, L116-L120 form); Tr/Ta/Pr 5-pair table reported.
- P4: 0.01 < af < 0.9 every arm/seed; b65 af-mean band [.105056, .113056].
- Full-arm B16 disclosure bands: Ti L (.30,.45) R (.35,.55);
  Sr L (.08,.25) R (.30,.50) (l118/l119/l120 form).
- Sanity cells: Ti cut kL >= 14; b65 16/16 BOTH sides; cut19 kL >= 12.
  A miss is DISCLOSED, never an abort.

## Verdict output

l121/results_l121.json: c0b, p0 (incl. c0a120 block), p4, table (5 pairs x
9 arms, per-side k/mean/Wilson), dose (Ti/Sr R+L curve over ng k + cut58
endpoint + kill booleans + classification MASS/POOL/MIXED), cutk5 B16
replication read, sr_watch, sanity. raw_l121.npz checkpointed BEFORE
analysis (L45a rule); raw_partial.npz resume-safe per-seed.
