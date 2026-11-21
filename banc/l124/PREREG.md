# L124 PREREG — cutwA/cutwB batch rebase (B19). Registered BEFORE build/run.

Card: LANE.md ideas-65 L124 (seeded tick 147). Registered 2026-11-17 ~15:35
by Miso, tick 148. Expectation numbers re-derived from STORED artifacts
(results_l123.json Ti table + pooled dict + fresh_gains, raw npz seed lists),
never from log sentences (L44 rule). Zero rollouts before this file.

## Why

L123 (B18) read the window halves as W4 MIXED, decomposed: cutwB (lighter
quintet ranks 25-29 out) = DEEP KILL (.183 0/16, paired dR -.328, == ng19's
own .243-class kill); cutwA (heavier quintet ranks 20-24 out) = PARTIAL
un-wind (.413 5/16, dR -.098, between kill and full .511). Single-batch —
this tick re-rolls BOTH halves on fresh B19 and pools the window arms'
batch union (L88/L90 rule) so the citable numbers exist.

## Arms (10, machinery VERBATIM)

full / b65 / cut / cut19 / cut58 (C0A stored arms) / cutk5 / cutng19 /
cutng29 (endpoints) / cutwA / cutwB. ALL gains now STORED-FORM anchors
(re-bisect EXACT): g_cut .14510760426521305, g_cut19 .15096808075904844,
g_cut58 .15417299151420596, g_cutk5 0.13981970071792604, g_cutng19
0.15025991678237915, g_cutng29 0.1442639136314392, g_cutwA
0.14365819573402408 (l123 fresh gain -> stored), g_cutwB
0.14922914385795596 (l123 fresh gain -> stored). NO fresh bisect arm;
staircase disclosures retained. Drops pinned to l121/static.json +
l123/static.json EXACTLY (asserted in run, unchanged graph). Seeds:
[801, 901] anchors + FRESH B19 = 2301-2316, asserted absent from
raw_l113, l115, l117, l118, l119, l120, l121, l122 AND l123/raw_l123.npz.

## P0 anchors (gates)

- C0A vs raw_l113: {full,b65,cut,cut19,cut58} x {801,901} x {mm,xm,Ti/Tr
  f/e L/R} + af; max|diff| MUST be 0.0 (54th consecutive).
- C0A-120 retained (cutk5 vs raw_l120); C0A-121 retained ({cutk5,cutng19,
  cutng29} vs raw_l121); C0A-122 retained (same 3 vs raw_l122).
- C0A-123 (NEW forward-chain class): {cutk5,cutng19,cutng29,cutwA,cutwB}
  x {801,901} vs raw_l123.npz on all 22 pool keys + mm/xm + af; max 0.0
  (l123 ran every arm at all 18 seeds — L120 addendum rule).
- Stored-gain re-bisects EXACT (8, listed above).
- C0B machinery certification on stored raw_l113 (Ti+Tr, 5 stored arms)
  BEFORE any L124 pin; PLUS B18-cert: duty machinery recomputed on
  raw_l123 B18 == results_l123.json Ti table (ALL 10 arms incl wA/wB)
  BEFORE any B19 window read.

## PRIMARY registered reads (B19; kill criterion VERBATIM L118-L123)

An arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B19). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band (L123 wA shape):
meanR in [.35,.50] AND kR in 3..8.

- R1 (cutwB deep-kill robust): cutwB KILLs on B19. PASS/FAIL by criterion.
- R2 (cutwA shape): PARTIAL-ROBUST iff B19 cutwA lands in the partial
  band; any other outcome = RE-DRAW (kill or restore/super) — disclosed,
  never rounded.
- R3 (revision trigger): EITHER half reaches RESTORE or SUPER-RAISE on
  B19 -> revises L123's W4 toward W1/W2 (a half CAN flip alone after all).
- Classification (pre-registered decision tree):
  R3 fired -> "REVISION toward W1/W2 (a half flips alone; disclosed)";
  else killA AND killB -> "REVISION toward W3 (both kill; window coherence
  extends past rank 24 on B19)";
  else R1 PASS AND R2 PARTIAL-ROBUST -> "W4 BATCH-ROBUST: neither half
  flips alone, cutwB kill + cutwA partial replicate — 2-step window
  structure holds";
  else -> "MIXED/RE-DRAW (lottery class; disclosed)".

## Secondaries (registered, no gate on watch axes)

- S1: cutk5 KILLs on B19 -> 7th consecutive batch (B12/B14/B15/B16/B17/
  B18/B19); a miss DISCLOSED.
- S2: cutng19 KILLs + cutng29 SUPER-RAISES in-batch (4th batch each).
- POOLED (L90 full-precision Wilson):
  (a) window arms {cutwA, cutwB}: batch union B18+B19 n=32, k(duty_Ti_R
  >= .5), per-batch k columns; B18 side CERTIFIED first (B18-cert above).
  (b) R4 arms {full, cutng19, cutng29, cutk5, cut58}: union
  B16+B17+B18+B19 n=64; B16/B17/B18 sides CERTIFIED vs stored results
  jsons before pooling.
- Watch: Ti_L (ng29 side-flip anticorrelation), Sr_R (killed by every ng
  dose 3 batches; lottery, no gate), 5-pair x 10-arm table.
- P4: 0.01 < af < 0.9 every arm/seed; b65 af-mean band [.105056,.113056].
- Full-arm B19 disclosure bands (l122 widened form): Ti L (.25,.48) R
  (.35,.58); Sr L (.08,.25) R (.30,.50).
- Sanity: Ti cut kL >= 14; b65 16/16 both sides; cut19 kL >= 12. Miss =
  DISCLOSED, never abort.

## Verdict output

l124/results_l124.json: c0b (+B18-cert), p0 (C0A/120/121/122/123 + 8
stored gains), p4, table (5 pairs x 10 arms, B19), dose (Ti/Sr curves +
kill booleans + R1/R2/R3 + classification + S1/S2), pooled_window (n=32),
pooled (n=64), watch, sanity. raw_l124.npz checkpointed BEFORE analysis
(L45a rule); raw_partial resume-safe per-seed.
