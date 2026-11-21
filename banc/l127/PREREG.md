# L127 PREREG — contiguous-light-decile (coherence vs heaviness, B22). Registered BEFORE build/run.

Card: LANE.md ideas-67 L127 (seeded tick 149). Registered 2026-11-17 ~21:1x
by Miso, tick 151. Expectation numbers re-derived from STORED artifacts
(results_l124.json + results_l125.json + results_l126.json + l121/l123/l125
static pins), never from log sentences (L44 rule). Zero dynamic rollouts
before this file (l127_static.py is zero-rollout and already ran).

Static pins (l127/static.json, zero-rollout): decile masses ranks 30-39 =
.0544 (scr0 extra) / ranks 40-49 = .0450 (cl40 extra) / ranks 50-58 =
.0338; pool 10-draw extra range [.0381, .0544]. CARD AMENDMENT (registered
pre-run): the card's "~.03" estimate for ranks 40-49 was WRONG — the
contiguous-light decile carries .0450, only 17% below scr0's .0544 and
well inside the reachable 10-draw range. The HEAVY-scattered cell of the
2x2 (scattered 10 at ~.05 extra) is IMPOSSIBLE to re-draw at matched mass
by construction (max 10-of-pool draw = ranks 30-39 = scr0 itself) — that
cell remains l125's scr1-3 on B20 (.0442-.0476 extra, cross-batch,
DISCLOSED). Arms as run: cutscr0 re-run same-batch (contiguous-HEAVY
context, .2490); cutcl40 = k19 + ranks 40-49 (contiguous, .2396,
DETERMINISTIC); cutscrL1/2 = k19 + pinned-RNG scattered 10-of-ranks-30-58
mass-matched to cl40 (.2406/.2386, extras .0460/.0439, delta vs cl40
.0010/.0011, band +-.002 achieved at 1 attempt each — the light band was
NOT restrictive). scr0 re-pin == l125/static.json EXACT (n 21780, edges
643802, .2490); k19/k29/k58 == l121 EXACT; wA == l123 EXACT (identity
only, arm not run); DNg100 in no drop; every drop = k19 ∪ extra-10 ⊂
cut58; extras disjoint from the ng[19:29] window and ≠ the cl40 decile.

## Why

L125 split the super-raise story: scr0 (k19 + ranks 30-39, contiguous
ADJACENT decile, .0544 extra) SUPER-RAISED .622 12/16 while scattered 10s
at similar mass re-rolled {kill, partial, partial} — but scr0 is BOTH the
heaviest possible non-window 10 AND contiguous, so coherence-vs-heaviness
is confounded (L127 seeded for exactly this). L126 completed the window
curve (kill→super completes at k=26, band ranks 25-26). This tick holds
mass FIXED at the light decile's .0450 and varies GEOMETRY only:
contiguous (cl40) vs scattered (scrL1/2), with scr0 same-batch as the
heavy-contiguous point.

## Arms (12, machinery VERBATIM from l125_run.py)

full / b65 / cut / cut19 / cut58 (C0A stored arms) / cutk5 / cutng19 /
cutng29 / cutscr0 (STORED gains, re-bisected EXACT: g_cut
.14510760426521305, g_cut19 .15096808075904844, g_cut58
.15417299151420596, g_cutk5 0.13981970071792604, g_cutng19
0.15025991678237915, g_cutng29 0.1442639136314392, g_cutscr0
0.15423982501029967 — l125 scr_fresh_gains, NEW stored-form) / cutcl40 /
cutscrL1 / cutscrL2 (FRESH bisects, staircase + .14-.16 band DISCLOSED,
never abort). Seeds: [801, 901] anchors + FRESH B22 = 2601-2616,
asserted absent from raw_l113, l115, l117, l118, l119, l120, l121, l122,
l123, l124, l125 AND l126/raw_l126.npz.

## P0 anchors (gates)

- C0A vs raw_l113: {full,b65,cut,cut19,cut58} x {801,901} x {mm,xm,Ti/Tr
  f/e L/R} + af; max|diff| MUST be 0.0 (57th consecutive).
- C0A-120 (cutk5 vs raw_l120); C0A-121 (3 arms vs raw_l121); C0A-122 (3
  arms vs raw_l122); C0A-123 (3 shared arms vs raw_l123 — wA not run
  here, DISCLOSED); C0A-124 (3 shared arms vs raw_l124) — all retained.
- C0A-125 EXTENDED (4 arms incl cutscr0 vs raw_l125 — l125 ran scr0 at
  all 18 seeds): max 0.0.
- C0A-126 (NEW forward-chain class): {cutk5,cutng19,cutng29} x {801,901}
  vs raw_l126.npz on all 22 pool keys + mm/xm + af; max 0.0 (l126 ran
  every arm at all 18 seeds; scr/cl arms have no l126 counterpart,
  excluded by name).
- Stored-gain re-bisects EXACT (7, listed above).
- C0B machinery certification on stored raw_l113 (Ti+Tr, 5 stored arms)
  BEFORE any L127 pin; PLUS B21-cert: duty machinery recomputed on
  raw_l126 B21 == results_l126.json Ti table (ALL 13 l126 arms) BEFORE
  any B22 read.

## PRIMARY registered reads (B22; criteria VERBATIM L118-L126)

Arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B22). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band: meanR in [.35,.50]
AND kR in 3..8. Per-arm labels for {cutscr0, cutcl40, cutscrL1,
cutscrL2} (Ti side table + paired dR legs + Wilson per side).

- C1 COHERENCE: cutcl40 SUPER-RAISES AND both scrL arms do NOT (each
  kill / partial / below-super) -> at matched mass the GEOMETRY of the
  removed set (a contiguous decile) owns the kill->super flip; scr1's
  B20 kill at HIGHER extra (.0476) is then a placement fact.
- C2 HEAVINESS: cutcl40 does NOT super-raise (kill or partial) AND both
  scrL arms do NOT -> the operative variable is the HEAVINESS of the
  coherent block (.0544/.0642 deciles flip; .0450 does not) — L125's
  "coherent decile" revised to "HEAVY coherent decile".
- C3 MASS-SUFFICIENCY: any scrL arm SUPER-RAISES -> total ~.239 mass is
  sufficient and scattered draws re-roll across the flip (lottery at
  matched mass); coherence claim dies, disclose scr1-vs-scrL draw spread.
- MIXED (e.g. cl40 partial, one scrL partial): intermediate regime —
  report per-arm labels + which cell carries the discrimination (L55/L109
  rule), no class claim.
- scr0 context: EXPECTED SUPER (2nd batch; miss = scr-family
  batch-fragility disclosure qualifying every cell above).

## Secondaries (registered, no gate on watch axes)

- S1: cutk5 KILLs on B22 -> 10th consecutive batch; a miss DISCLOSED.
- S2: cutng19 KILLs + cutng29 SUPER-RAISES in-batch (7th batch each).
- POOLED (L90 full-precision Wilson): R4 arms {full, cutng19, cutng29,
  cutk5, cut58} batch union B16..B22 n=112 (extending l126's n=96);
  B16-B21 sides CERTIFIED vs stored results jsons before pooling. NEW
  pooled scr0: B20 + B22 union n=32 (2-batch; the fuller scr rebase
  stays L128's). cl40/scrL arms single-batch (DISCLOSED).
- Watch: Ti_L (ng29 L-death anticorrelation + cl40/scrL L reads), Sr_R
  (killed by every ng dose 5 batches; lottery, no gate), Tr_R, 5-pair x
  12-arm table.
- full-arm B22 band disclosure (never abort): Ti L (.25,.48), R
  (.35,.58); Sr L (.08,.25), R (.30,.50).
- Fresh gains: cl40/scrL1/scrL2 disclosed against the .14-.16 band
  (scr0's stored .1542 is in-band).

## Sanity cells (secondary; miss = disclose)

cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12.
