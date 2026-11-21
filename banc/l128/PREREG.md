# L128 PREREG — scr1/scr2/scr3 batch rebase: pinning the .045–.0544 heaviness threshold. Registered BEFORE build/run.

Card: LANE.md ideas-67 L128 (amended by L127/tick 151: scr0 do-not-reroll —
2 batches banked; the live question is scr1). Registered 2026-11-17 ~23:0x
by Miso, tick 152. Pins re-derived from STORED artifacts (results_l125.json,
results_l127.json, l125/static.json, l121/static.json), never from log
sentences (L44 rule). Zero dynamic rollouts before this file; l128's static
pins are asserted by the run itself (drop sets == l125/static.json EXACT).

Static pins (asserted in-run): scr drops == l125/static.json EXACT — masses
.2490/.2422/.2409/.2388, extras .0544/.0476/.0463/.0442, edges
643802/643848/643807/643942; k19/k29/k58 == l121 EXACT; DNg100 in no drop.

## Amendment interpretation (registered): scr0 rolls on B23 as a structural
necessity of the uniform arm set (the C0A-125 anchor requires scr0 at stored
seeds; per-seed arm masking = machinery drift risk, L75 class). Its 3rd
batch is banked as BONUS (pooled n=48) — never the card's question.

## Arms (12, machinery VERBATIM from l125_run.py — the identical arm list)

full / b65 / cut / cut19 / cut58 (C0A stored arms) / cutk5 / cutng19 /
cutng29 / cutscr0 / cutscr1 / cutscr2 / cutscr3. ALL gains STORED-FORM with
deterministic re-bisect asserts (re-land EXACT): g_cut .14510760426521305,
g_cut19 .15096808075904844, g_cut58 .15417299151420596, g_cutk5
0.13981970071792604, g_cutng19 0.15025991678237915, g_cutng29
0.1442639136314392, g_cutscr0 0.15423982501029967, g_cutscr1
0.16989078283309933, g_cutscr2 0.1424216973781586, g_cutscr3
0.16503094553947448 (l125 scr_fresh_gains, scr0 re-verified EXACT in l127).
scr1/scr3 sit OUTSIDE the .14-.16 band (af-matched bisects, disclosed).
Seeds: [801, 901] anchors + FRESH B23 = 2701-2716, asserted absent from
raw_l113, l115, l117, l118, l119, l120, l121, l122, l123, l124, l125,
l126 AND l127 npzs.

## P0 anchors (gates)

- C0A vs raw_l113 {full,b65,cut,cut19,cut58} x {801,901}: max 0.0 (58th
  consecutive).
- C0A-120 (cutk5 vs raw_l120); C0A-121 (3 arms vs raw_l121); C0A-122 (3
  arms vs raw_l122); C0A-123 (3 shared arms vs raw_l123); C0A-124 (3 shared
  arms vs raw_l124); C0A-126 (3 arms vs raw_l126) — all retained.
- C0A-125 EXTENDED to ALL 12 arms vs raw_l125 (l125 ran the IDENTICAL arm
  list at all 18 seeds — strongest chain form yet: 22 keys x 12 arms x 2
  seeds).
- C0A-127 (NEW forward chain): 9 shared arms {full,b65,cut,cut19,cut58,
  cutk5,cutng19,cutng29,cutscr0} vs raw_l127 (cl40/scrL1/scrL2 have no L128
  counterpart — excluded by name, DISCLOSED).
- C0B machinery certification on stored raw_l113 (Ti+Tr, 5 stored arms)
  BEFORE any L128 pin; PLUS B22-cert: duty machinery recomputed on raw_l127
  B22 == results_l127.json Ti table (9 shared arms) BEFORE any B23 read.

## PRIMARY registered reads (B23; criteria VERBATIM L118-L127)

KILL: meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20 (m0 =
full-arm Ti meanR on B23). RESTORE: meanR >= .45 AND kR >= 12. SUPER:
meanR >= .60 AND kR >= 12. PARTIAL: meanR in [.35,.50] AND kR in 3..8.
Labeled arms: cutscr1/2/3 (the question) + cutscr0 (context, expected SUPER).

- H1A (scr1 KILL replicates): pooled 2/2 batches -> the scattered .0476
  KILL is draw-reliable -> the band edge is DRAW-STRUCTURED, not
  mass-ordered (scr2 at .0463 sits .0013 below and does not kill-reliably);
  report scr1-vs-scr2 as the discriminator.
- H1B (scr1 re-rolls, no kill no super): the .0442-.0476 scattered band is
  a LOTTERY on both batches -> L127's law extends: reliable kill->super
  starts ~.054 removed-extra; everything below re-rolls; scr1's B20 deep
  kill (.041 0/16) disclosed as one draw.
- H1C (scr1 SUPER): same conclusion as H1B with the widest lottery spread
  (kill -> super across batches at a fixed draw); disclose prominently.
- H2: scr2/scr3 expected PARTIAL-band replication (B20: .469/.425, kR 6/6);
  miss = disclosed watch, no gate.
- H3 (bonus): scr0 expected SUPER 3rd batch; miss = scr-family
  batch-fragility disclosure qualifying every cell above.

## Secondaries (registered, no gate on watch axes)

- S1: cutk5 KILLs on B23 -> 11th consecutive batch; miss DISCLOSED.
- S2: cutng19 KILLs + cutng29 SUPER-RAISES in-batch (8th batch each).
- POOLED (L90 full-precision Wilson): R4 arms {full,cutng19,cutng29,cutk5,
  cut58} batch union B16..B23 n=128; NEW pooled scr1/scr2/scr3 B20+B23
  n=32 each; scr0 pooled B20+B22+B23 n=48. B16-B22 sides CERTIFIED vs
  stored results jsons before pooling (B22-cert this tick).
- Watch: Ti_L (side-flip anticorrelation), Sr_R (6th batch), Tr_R, Ta_L
  (scr3 raised .606 on B22 — new watch), 5-pair x 12-arm table.
- full-arm B23 band disclosure (never abort): Ti L (.25,.48), R (.35,.58);
  Sr L (.08,.25), R (.30,.50).
- P4: af in (.01,.9) every arm/seed; b65 band [.105056,.113056].

## Sanity cells (secondary; miss = disclose)

cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12.
