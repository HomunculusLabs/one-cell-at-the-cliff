# L125 PREREG — window-scramble control (B20). Registered BEFORE build/run.

Card: LANE.md ideas-66 L125 (seeded tick 148). Registered 2026-11-17 ~17:2x
by Miso, tick 149. Expectation numbers re-derived from STORED artifacts
(results_l124.json + l121/static.json pins + l125/static.json pins), never
from log sentences (L44 rule). Zero rollouts before this file.

## Why

L124 made the ng[19:29] window a batch-robust 2-step placement unit (cutwA
partial .376 4/16, cutwB deep-kill .164 1/16 pooled 9/32 vs 1/32). The
strongest remaining null for the PLACEMENT story is COUNT/DOSE: would ANY
10 more ng cells at this dose complete the ng19-kill -> ng29-super-raise
flip? This tick drops k19 + 10 NON-window cells instead and asks whether
the super-raise appears.

## CARD AMENDMENT (registered pre-run, feasibility)

The card's "mass-matched to .2588 within ±.01" is INFEASIBLE for 10-of-
ranks-30-58: the entire 29-cell pool carries only .1333 (l121 pins: k29
.2588, k39 .3132, k58 .3921), so the heaviest possible non-window 10
(ranks 30-39) gives .2490 — a random 10 averages ~.2406 — and 100000
rejection attempts found ZERO qualifying draws (l125_static.py run 1).
Amended arms (pins in l125/static.json, deterministic):
- cutscr0 = DETERMINISTIC max-mass scramble: k19 + ranks 30-39, mass
  .2490, only .0098 below the window .2588 — the MASS-ARMmor arm. If
  even scr0 does not super-raise, mass cannot rescue the count story
  (L123 measured a .0038 mass delta explaining nothing at this scale).
- cutscr1/2/3 = pinned-RNG random 10-of-pool draws (seeds 1251/1252/1253,
  attempt-1 draws), masses DISCLOSED: .2422 / .2409 / .2388.

## Arms (12, machinery VERBATIM from l124_run.py)

full / b65 / cut / cut19 / cut58 (C0A stored arms) / cutk5 / cutng19 /
cutng29 (endpoints, 6 stored gains re-bisected EXACT: g_cut
.14510760426521305, g_cut19 .15096808075904844, g_cut58
.15417299151420596, g_cutk5 0.13981970071792604, g_cutng19
0.15025991678237915, g_cutng29 0.1442639136314392) / cutscr0/1/2/3
(FRESH bisects, staircase + .14-.16 band DISCLOSED, never abort).
cutwA/cutwB arms are NOT re-run (their batch union n=32 is complete);
their drop-set identity is re-pinned in l125_static.py as extraction
regression only. Seeds: [801, 901] anchors + FRESH B20 = 2401-2416,
asserted absent from raw_l113, l115, l117, l118, l119, l120, l121, l122,
l123 AND l124/raw_l124.npz.

## P0 anchors (gates)

- C0A vs raw_l113: {full,b65,cut,cut19,cut58} x {801,901} x {mm,xm,Ti/Tr
  f/e L/R} + af; max|diff| MUST be 0.0 (55th consecutive).
- C0A-120 retained (cutk5 vs raw_l120); C0A-121 retained (3 arms vs
  raw_l121); C0A-122 retained (3 arms vs raw_l122).
- C0A-123 retained on the 3 SHARED arms {cutk5,cutng19,cutng29} vs
  raw_l123 (wA/wB trimmed — those arms are not run here; DISCLOSED).
- C0A-124 (NEW forward-chain class): {cutk5,cutng19,cutng29} x {801,901}
  vs raw_l124.npz on all 22 pool keys + mm/xm + af; max 0.0 (l124 ran
  every arm at all 18 seeds — L120 addendum rule).
- Stored-gain re-bisects EXACT (6, listed above).
- C0B machinery certification on stored raw_l113 (Ti+Tr, 5 stored arms)
  BEFORE any L125 pin; PLUS B19-cert: duty machinery recomputed on
  raw_l124 B19 == results_l124.json Ti table (ALL 10 l124 arms incl
  wA/wB) BEFORE any B20 read.

## PRIMARY registered reads (B20; kill criterion VERBATIM L118-L124)

An arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B20). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band (L123 wA shape):
meanR in [.35,.50] AND kR in 3..8.

- SC1 (count/dose story ALIVE): >=1 scramble arm (scr0/1/2/3) SUPER-
  RAISES on B20 -> the flip is count-carried; the placement story dies;
  disclose which mass tier fired.
- SC2 (placement story holds — registered expectation, from the card):
  NO scramble arm super-raises AND none restores. scr0 is the decisive
  arm (max-mass .2490): scr0 no-super closes the mass objection.
- Classification (pre-registered decision tree):
  any SUPER -> "COUNT-CARRIED (placement dead; disclosed)";
  else any RESTORE (>=.45/12) -> "MIXED: a scramble restores without
  super-raising — neither pure story; disclosed";
  else (registered expectation) -> "PLACEMENT-OWNED: no scramble flips
  the window's super-raise; per-arm labels (kill / partial / full-like
  meanR in (.50,.60) or kR>=9) reported per draw".
- Mass covariate DISCLOSED beside the table (scr .2388-.2490 vs window
  .2588 vs ng19 .1946) — never a gate.

## Secondaries (registered, no gate on watch axes)

- S1: cutk5 KILLs on B20 -> 8th consecutive batch (B12/B14/B15/B16/B17/
  B18/B19/B20); a miss DISCLOSED.
- S2: cutng19 KILLs + cutng29 SUPER-RAISES in-batch (5th batch each).
- POOLED (L90 full-precision Wilson): R4 arms {full, cutng19, cutng29,
  cutk5, cut58} batch union B16+B17+B18+B19+B20 n=80 (updating l124's
  n=64 citables); B16-B19 sides CERTIFIED vs stored results jsons before
  pooling. NO window pooling (wA/wB not re-run).
- Watch: Ti_L (ng29 side-flip anticorrelation), Sr_R (killed by every ng
  dose 4 batches; lottery, no gate), Tr_R, 5-pair x 12-arm table.
- full-arm B20 band disclosure (never abort): Ti L (.25,.48), R
  (.35,.58); Sr L (.08,.25), R (.30,.50).

## Sanity cells (secondary; miss = disclose)

cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12.
