# L126 PREREG — window-interpolation (B21). Registered BEFORE build/run.

Card: LANE.md ideas-66 L126 (seeded tick 148). Registered 2026-11-17 ~19:0x
by Miso, tick 150. Expectation numbers re-derived from STORED artifacts
(results_l124.json + results_l125.json + l121/l123/l126 static pins), never
from log sentences (L44 rule). Zero rollouts before this file. Static pins
computed by l126_static.py (zero-rollout) BEFORE this registration:
cutng21 n=21788 edges=644509 mass .2086 / cutng23 n=21786 e=644282 .2220 /
cutwA(=k24) n=21785 e=644177 .2286 (== l123 stored EXACT) / cutng26
n=21783 e=643979 .2411 / cutng28 n=21781 e=643725 .2529; strictly nested
ng21<ng23<wA<ng26<ng28<k29-window; DNg100 in no drop.

## Why

L124 made the ng[19:29] window a batch-robust 2-step placement unit: cutwA
(k24) sits PARTIAL (.413/5 B18, .376/4 B19 — band [.35,.50] & k 3-8) and
k29 SUPER-RAISES (.774-.779, 16/16, both batches; pooled 78/80). L125
showed a coherent ADJACENT decile also supers (scr0 .622 12/16) while
scattered 10s re-roll. This tick interpolates INSIDE the window with
positional prefixes ng_desc[:k], k in {21,23,26,28} (+ endpoints k19/k24/
k29 already stored) — L125 tested WHICH cells, L126 tests HOW MANY.

## Arms (13, machinery VERBATIM from l124_run.py)

full / b65 / cut / cut19 / cut58 (C0A stored arms) / cutk5 / cutng19 /
cutng29 / cutwA (STORED gains, re-bisected EXACT: g_cut
.14510760426521305, g_cut19 .15096808075904844, g_cut58
.15417299151420596, g_cutk5 0.13981970071792604, g_cutng19
0.15025991678237915, g_cutng29 0.1442639136314392, g_cutwA
0.14365819573402408) / cutng21 / cutng23 / cutng26 / cutng28 (FRESH
bisects, staircase + .14-.16 band DISCLOSED, never abort). cutwB is NOT
run (its 2-batch union is complete; trimmed from C0A-123 — DISCLOSED).
Seeds: [801, 901] anchors + FRESH B21 = 2501-2516, asserted absent from
raw_l113, l115, l117, l118, l119, l120, l121, l122, l123, l124 AND
l125/raw_l125.npz.

## P0 anchors (gates)

- C0A vs raw_l113: {full,b65,cut,cut19,cut58} x {801,901} x {mm,xm,Ti/Tr
  f/e L/R} + af; max|diff| MUST be 0.0 (56th consecutive).
- C0A-120 retained (cutk5 vs raw_l120); C0A-121 retained (3 arms vs
  raw_l121); C0A-122 retained (3 arms vs raw_l122).
- C0A-123 trimmed to the 4 SHARED arms {cutk5,cutng19,cutng29,cutwA} vs
  raw_l123 (cutwB not run here; DISCLOSED).
- C0A-124 (NEW forward-chain class): {cutk5,cutng19,cutng29,cutwA} x
  {801,901} vs raw_l124.npz on all 22 pool keys + mm/xm + af; max 0.0
  (l124 ran every arm incl wA at all 18 seeds).
- C0A-125 (NEW forward-chain class): {cutk5,cutng19,cutng29} x {801,901}
  vs raw_l125.npz (scr arms not run here; DISCLOSED).
- Stored-gain re-bisects EXACT (7, listed above).
- C0B machinery certification on stored raw_l113 (Ti+Tr, 5 stored arms)
  BEFORE any L126 pin; PLUS B20-cert: duty machinery recomputed on
  raw_l125 B20 == results_l125.json Ti table (ALL 12 l125 arms) BEFORE
  any B21 read.

## PRIMARY registered reads (B21; criteria VERBATIM L118-L125)

Arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B21). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band: meanR in [.35,.50]
AND kR in 3..8. The DOSE CURVE = Ti_R over k in {19,21,23,24,26,28,29}
on B21, each point labeled by the criteria above. Registered shapes:

- D1 SMOOTH: meanR rises gradually — every adjacent step |d meanR| < .15
  and no label jumps PARTIAL -> SUPER between adjacent k.
- D2 SECOND STEP: a DISCRETE jump inside 21..28 — some adjacent pair
  (k,k+2..4) gains >= .20 meanR (or flips PARTIAL -> SUPER) while both
  outer neighbors (19->21, 28->29) move < .15; the jump k* is reported.
- D3 CLIFF AT 29: k28 does NOT super-raise (meanR < .45 or kR < 12) and
  k29 DOES — the whole-unit story (L124) survives interpolation; the
  window acts as one 10-cell gate.
- Lottery shape (registered fallback): non-monotone with a dip > .15
  between adjacent prefixes -> the middle is the L115/L118/L121 lottery
  class at rank resolution; disclose per-rank labels, no curve claim.

## Secondaries (registered, no gate on watch axes)

- S1: cutk5 KILLs on B21 -> 9th consecutive batch; a miss DISCLOSED.
- S2: cutng19 KILLs + cutng29 SUPER-RAISES in-batch (6th batch each).
- S3: cutwA lands in the PARTIAL band [.35,.50] & kR 3-8 (3rd batch:
  B18 .413/5, B19 .376/4); a miss DISCLOSED (would revise the stable-
  intermediate reading of L124).
- POOLED (L90 full-precision Wilson): R4 arms {full, cutng19, cutng29,
  cutk5, cut58} batch union B16..B21 n=96 (extending l125's n=80);
  B16-B20 sides CERTIFIED vs stored results jsons before pooling. NO scr
  pooling (scr arms not re-run).
- Watch: Ti_L (ng29 L-death anticorrelation), Sr_R (killed by every ng
  dose 4 batches; lottery, no gate), Tr_R, 5-pair x 13-arm table.
- full-arm B21 band disclosure (never abort): Ti L (.25,.48), R
  (.35,.58); Sr L (.08,.25), R (.30,.50).

## Sanity cells (secondary; miss = disclose)

cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12.
