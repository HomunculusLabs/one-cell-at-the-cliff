# L142 PREREG — dnp33-edge-footprint-ladder (registered BEFORE the run)

Item: LANE.md ideas 74 / L142. Static FIRST (l142_static.py done, exit 0 —
numbers below are its measured feasibility pins, not predictions).

## Substrate & machinery

- Base graph: cutwA window (closure minus ng_desc[:24]; n 21785, 644177
  edges — re-pinned == l131 static EXACT). Carrier 1110 (DNp33-L, ng rank
  25) is PRESENT in this base with all its edges; twin 319 rank 26.
- L142 arms (9 total): `full`, `b65`, `cutwA`, `cutng25` (stored-form
  gains, re-bisect asserted EXACT: .14365819573402408 / .1454454553127289)
  + FIVE edge-drop arms on the cutwA NODE SET (1110 kept as a cell):
  - `eOutInt` — drop 1110's 70 out-edges onto vnc_intrinsic (mass frac .005599)
  - `eOutMot` — drop 1110's 10 out-edges onto motor (mass frac .000837)
  - `eOutAll` — drop all 80 out-edges (.006436 == the ladder rank-25 mass)
  - `eIn` — drop 1110's 13 in-edges (all-DN sources, NONE in the ng-58
    family — src_ng_ranks {} measured; mass frac .000987)
  - `eAll` — drop all 93 incident edges (.007423)
  Each edge arm gets a FRESH af-matched bisect (bracket .12-.18, target
  AF_T .10905611018339793, 24 iters, seeds 11/22/33 settle-only); band
  .14-.16 disclosed per arm (never abort).
- Spectator arms: cut/cut19/cut58/cutk5/cutng19/cutng23/cutng25p/cutng26/
  cutng29 keep their graphs/pins verbatim but are NOT advanced (l139
  spectator-arm subset law; their bisects RETIRED this run).
- Paired-noise law (by construction): edge arms share cutwA's node set,
  X0 init, and per-step noise vector EXACTLY — paired dR vs cutwA is
  fork-grade within every seed.
- Fresh batch B29 = 3301-3316 (asserted absent from ALL stored raw npzs
  l107..l137 + l139 j0..j5 before any read). ANCH 801/901 first.

## Structural law (zero-rollout, measured)

`eAll` selects the SAME global edge positions as cutng25's node drop
(np.array_equal on where() indices, 644084 edges EXACT). Corollary: eAll
and cutng25 differ ONLY by (a) isolated node 1110 in eAll (N 21785 vs
21784, X ~ .02 < .05 threshold, no out-edges, no pool membership) and
(b) the af denominator. If g_eAll == g_cutng25 EXACT, their pool
readouts must be BIT-IDENTICAL (registered anchor A-EALL, max|d| == 0
over mm/xm/pools at 801/901); if the bisect lands one staircase step
away (af diff ~ 1/21785 can flip a comparison), DISCLOSE and read the
arm on its own gain — either branch is publishable, neither is a failure.

## Criteria (VERBATIM L118-L131, same code path as l135_verdict)

KILL: meanR <= m0 - .10 AND kR <= 4 AND mean_paired_dR <= -.20.
RESTORE: meanR >= .45 AND kR >= 12. SUPER: meanR >= .60 AND kR >= 12.
PARTIAL band: .35 <= meanR <= .50 AND 3 <= kR <= 8. m0 = full's meanR on
B29. Pools/metric: Ti duty07 per side, round-per-seed-then-mean (l109
rounding path), 5-pair table reported.

## Hypotheses (registered BOTH directions)

- H1 (edge-carrier): eAll classifies == cutng25's B29 class. Counter:
  they diverge -> the af-denominator/noise-index difference is doing
  work; disclose with paired per-seed table, do NOT force a class.
- H2a (intrinsic-carrier): eOutInt alone SUPERs/RESTOREs — identity
  beats mass at .0056 << the .0544 reliable-super band (L127) and below
  the whole lottery band .0442-.0544: a clean single-population-sheet
  counterexample to the heaviness law AT THE CELL SCALE.
- H2b (motor-carrier): eOutMot (10 edges, .00084) carries it — extreme.
- H2c (distributed): neither eOutInt nor eOutMot alone, but eOutAll
  flips -> footprint is the union, not one sheet.
- H3 (in-edges inert): eIn stays in cutwA's partial band with small
  paired dR vs cutwA.
- Sham/single-cell reference scale: L141 silrand spread .075 (clamp arms,
  intact closure); the paired dR legs vs cutwA are the primary
  discriminators (shared noise stream).
- Mass-feasibility (measured, L125 rule): every arm's removed mass
  (.00084-.00742) is FAR BELOW any previously-measured flip threshold —
  no registered arm can be accused of buying the flip with mass.

## Anchors (gates; all must be green BEFORE any B29 read)

- A0 structural: eAll edge set == cutng25 edge set (static, PASS).
- A1 stored gains: cutwA/cutng25 re-bisect EXACT (assert, STOP on drift).
- A2 C0A-142: {full, b65, cutwA, cutng25} × {mm, xm, 22 pool keys} ×
  {801, 901} vs raw_l135.npz — max|d| == 0.0 (spectator-transform proof).
- A3 B29 absence across all 39 stored npzs (STOP on collision).
- A4 P4 health: per-arm af in (0.01, 0.9) every seed; b65 mean-af band
  .105056-.113056.
- A5 A-EALL: registered branch above (== 0 if gains equal; else disclose).
- Verdict B-cert BEFORE any B29 read: machinery recomputed on raw_l135
  B26 for {cutwA, cutng25} == results_l135.json Ti table EXACT (L85 cert).

## Pooled reads (L90 full-precision Wilson, unrounded)

- cutng25 pooled B24+B25+B26+B29 n=64; cutwA pooled B21+B24+B25+B26+B29
  n=80 (batches where the arm actually rolled; recomputed from stored
  raws + B29, never from log prose). e-arms: single-batch B29, disclosed.

## Disclosures (pre-registered)

- full's own class on B29 is batch-drawn (2-10/16 base spread): class
  labels are read against m0/paired legs, not bare bands (L109 rule).
- cutk5/ng19/ng29 secondaries NOT re-run (14/11/11 consecutive batches
  stand on stored pooled tables; spectator law).
- No renormalization arm: the lineage build path has NO in-degree
  renormalization (verified by grep + build() reading — vals = log1p
  raw); the card's "renormalization control" was a mis-carry from
  banc_graph.pt's preprocessing, which the lineage does not use. The
  honest decomposition is edge-subset only (L44 lesson applied to card
  text: derive from the stored build code, never the narrative).
