# L145 PREREG — eOutMot-middle-dose (registered BEFORE the build/run)

Item: LANE.md ideas 75 / L145. eOutMot (.525/9 on B29) landed BETWEEN the
partial band and super: read it properly — is the motor footprint a DOSE
(graded within-sheet) or another lottery draw (L115/L118 class)?

## Static pins (l145_static.py, exit 0, zero rollouts — measured, not predicted)

- 10 motor out-edges of 1110 in the wA window, ranked |vals| DESC
  (tiebreak global-pos ASC; two syn-8 ties broken by position, DISCLOSED):
  top-5 = iii4(35)/i2(31)/iv1(20)/DVM1a-c(12)/hi1-MN(9), mass frac
  .000523 = 62.55% of the motor mass; bottom-5 = i1(8)/DVM1a-c(8)/
  DVM1a-c(5)/DLM1-4(3)/iv4(3), .000313. Subset law: top5|bot5 selects
  eOutMot's edge positions EXACT (array_equal, pinned).
- The carrier's motor targets are LEG tarsus MNs (iii/i1/i2/iv1/iv4)
  plus INDIRECT FLIGHT muscle MNs (DVM/DLM) and one halter MN — top-5
  carries the leg+tarsus-heavy end (dose table reports dst types).
- eMotIn = 10 motor out + 13 in = 23 edges, .001824 (ladder denominator,
  l142 convention).

## Substrate & machinery

- Base VERBATIM l142/l144: full (G_NEW .153125), b65 (G65), cutwA
  (stored .14365819573402408), cutng25 (stored .1454454553127289).
- ARMS (8): `full`, `b65`, `cutwA`, `cutng25`, `eOutMot`, `eMotTop5`,
  `eMotBot5`, `eMotIn`. Edge arms on the cutwA NODE SET, share cutwA's
  X0/noise/pools/mech/motor/dng100/N_OF (l142 alias law) — paired dR vs
  cutwA is fork-grade per seed.
- Bisects: stored-form re-bisects cutwA/cutng25 asserted EXACT (STOP on
  drift); eOutMot fresh re-bisect asserted == l142 stored
  0.14284219264984138 EXACT (FC-142, L120 deterministic law); eMotTop5/
  eMotBot5/eMotIn FRESH (bracket .12-.18, 24 iters, seeds 11/22/33
  settle-only, AF_T .10905611018339793, band .14-.16 disclosed per arm).
- cutng25 stays a rolled arm (not just spectator): keeps the C0A 4-arm
  anchor form identical to l142/l144 AND grows the pooled super
  reference to n=96.
- Spectator graphs/pins verbatim, never advanced (l139 law).
- Fresh batch B31 = 3333..3348 (asserted absent from ALL stored raw npzs
  incl. l142 + l144 + partials before any read). ANCH 801/901 FIRST.

## Criteria (VERBATIM L118-L131, same code path as l142_verdict)

KILL: meanR <= m0 - .10 AND kR <= 4 AND mean_paired_dR <= -.20.
RESTORE: meanR >= .45 AND kR >= 12. SUPER: meanR >= .60 AND kR >= 12.
PARTIAL band: .35 <= meanR <= .50 AND 3 <= kR <= 8. m0 = full's meanR on
B31. Pools/metric: Ti duty07 per side, round-per-seed-then-mean (l109
rounding path), 5-pair table reported.

## Hypotheses (registered BOTH directions)

- H-REPLIC (eOutMot re-roll): (a) B31 lands again BETWEEN bands (meanR
  in (.50,.60) or kR in (8,12), off both class cells) -> the middle is a
  stable DOSE STEP, not batch noise; (b) B31 lands inside PARTIAL or
  SUPER band -> the .525 was batch-drawn (L88/L90 law); pooled B29+B31
  Wilson read carries the verdict, single-batch labels disclosed.
- H-DOSE (graded within-sheet): paired dR vs cutwA orders by mass —
  dR(eMotTop5) > dR(eMotBot5) on >= 12/16 seeds (sign count, one-sided
  registered) AND mean dR(eMotTop5) >= .5 * mean dR(eOutMot) (top5 holds
  62.5% of motor mass; the half-mass line is the pre-registered
  proportionality anchor).
- H-LOTTERY (the counter): ordering fails (sign count < 12/16) or the
  two subsets straddle bands without mass order -> within-sheet re-draw
  at the 5-edge scale, L115/L118 class; DISCLOSE, no class forced.
- H-COMBO (eMotIn): SUPER predicted (meanR >= .60, kR >= 12) — eIn alone
  was .793/15 SUPER on B29; if eMotIn FAILS to super on B31 while
  cutng25 supers, that is a batch/subset interaction, disclosed both
  directions.
- P3 (crossed-law read, descriptive): every flipping arm in the lineage
  killed Ti_L — read whether top5/bot5/eMotIn follow (mechanism carried)
  or Ti_L survives (dose split reaches the left side differently).
- Paired dR legs vs cutwA are PRIMARY (shared noise stream); class
  labels secondary (L109 rule; full's own class is batch-drawn 2-10/16).

## Anchors (gates; ALL green BEFORE any B31 read)

- A1 stored gains: cutwA/cutng25 re-bisect EXACT (STOP on drift).
- A2 C0A-145: {full, b65, cutwA, cutng25} x {mm, xm, 22 pool keys} x
  {801, 901} vs raw_l135.npz — max|d| == 0.0.
- A3 FC-142: eOutMot bisect == l142 stored EXACT AND eOutMot traces
  (24 keys x 801/901) vs raw_l142.npz == 0.0 (forward chain, L120 law).
- A4 B31 absence across ALL stored npzs (incl. l142/l144 raws +
  partials; STOP on collision).
- A5 P4: per-arm af in (0.01, 0.9) every seed; b65 mean-af band
  .105056-.113056.
- A6 subset law (static, PASS): top5|bot5 == eOutMot positions EXACT;
  in-run E_EDGES {10,5,5,23} assert.
- Verdict B-cert BEFORE any B31 read: (i) machinery on raw_l135 B26
  {cutwA, cutng25} == results_l135.json Ti table EXACT (L85 cert);
  (ii) machinery on raw_l142 B29 {eOutMot, cutwA, cutng25} ==
  results_l142.json Ti table EXACT (pooled-read cert).

## Pooled reads (L90 full-precision Wilson, unrounded)

- eOutMot pooled B29+B31 n=32 (recomputed from stored raws, never prose).
- cutwA pooled B21+B24+B25+B26+B29+B30+B31 n=112.
- cutng25 pooled B24+B25+B26+B29+B30+B31 n=96.
- eMotTop5/eMotBot5/eMotIn: single-batch B31, disclosed.

## Disclosures (pre-registered)

- Two syn-8 mass ties in the bottom-5 boundary region broken by global
  position (deterministic; the split is not tie-degenerate overall —
  all top-5 masses distinct and heavier than every bottom-5 mass).
- eMotIn includes in-edge mass on the ladder denominator (l142 form).
- Mass-feasibility (L125 rule): every arm's removed mass (.00031-.00182)
  is far below any measured flip threshold — no arm buys a flip with mass.
- No renormalization arm (lineage build has none — l142-verified).
