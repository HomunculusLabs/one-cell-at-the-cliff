# L123 PREREG — ng[19:29] window XOR (B18). Registered BEFORE build/run.

Card: LANE.md ideas-64 L123 (seeded this tick). Registered 2026-11-17 ~14:00
by Miso, tick 147. Expectation numbers re-derived from STORED artifacts
(l121/l122 results jsons + raw npzs + l121/static.json + l123/static.json
pins written this tick by l123_static.py, zero rollouts), never from log
sentences (L44 rule). Zero rollouts before this file.

## Why

L121/L122 bracket the sharpest transition in the lineage: cutng19 (drop the
19 heaviest non-glut, mass .1946) KILLS Ti_R (0/16 x B16/B17), cutng29
(drop 29, .2588) SUPER-RAISES it (.727/.749, 15-16/16, the highest R of any
arm on BOTH batches). The 10 cells ng_desc[19:29] (mass-desc ranks 20-29)
flip kill -> super-raise. This tick splits that window in mass-desc halves:

- cutwA = ng_desc[:24]           (k19 + ranks 20-24; ids {558,80,628,32072,585})
- cutwB = ng_desc[:19] + ng_desc[24:29]  (k19 + ranks 25-29; ids {1110,319,707,354,32271})

Both drop 24 cells and are QUASI-MASS-MATCHED by construction: .2286 vs
.2248 (delta .0038) — a near-clean placement contrast. The window is FLAT
(per-cell share .00588-.00703; NO dominant cell, unlike L120's cell-204
XOR) — if a half flips alone it is a PLACEMENT pattern across 5 cells, not
one heavy hitter. Masses/edges pinned: wA {n 21785, edges 644177, .2286},
wB {n 21785, edges 644174, .2248}; halves partition the k29 window EXACTLY
(union == k29 drop set; overlap == k19 drop set; asserted in run).

## Arms (10)

full / b65 / cut / cut19 / cut58 (stored C0A arms) / cutk5 (C0A-120/121/122
anchor + S1 replication) / cutng19 / cutng29 (window endpoints, STORED-FORM
gains, C0A-121/122 anchors) / cutwA / cutwB (fresh af-matched bisects).
Drops pinned to l121/static.json (k19/k29/k58) + l123/static.json (wA/wB)
EXACTLY. Seeds: [801, 901] anchors + FRESH B18 = 2201-2216, asserted absent
from raw_l113.npz, l115, l117, l118, l119, l120, l121 AND l122/raw_l122.npz.
l122 machinery VERBATIM (same graphs, draw order, gains); NO RNG arm.

## P0 anchors (gates)

- C0A vs raw_l113: {full,b65,cut,cut19,cut58} x {801,901} x {mm,xm,Ti/Tr
  f/e L/R} + af; max|diff| MUST be 0.0 (53rd consecutive).
- C0A-120 retained: cutk5 vs raw_l120. C0A-121 retained (narrowed to the
  arms run): {cutk5,cutng19,cutng29} vs raw_l121, all 22 pool keys + af.
- C0A-122 (NEW forward-chain class): {cutk5,cutng19,cutng29} x {801,901}
  vs raw_l122.npz on all 22 pool keys + mm/xm + af; max 0.0 (l122 ran
  every arm at all 18 seeds — L120 addendum rule).
- Stored-gain re-bisects EXACT (6): g_cut 0.14510760426521305, g_cut19
  0.15096808075904844, g_cut58 0.15417299151420596, g_cutk5
  0.13981970071792604, g_cutng19 0.15025991678237915, g_cutng29
  0.1442639136314392. cutwA/cutwB bisect FRESH (band .14-.16 DISCLOSURE
  only, never an abort; af staircase |af_final - target| disclosed).
- C0B machinery certification on stored raw_l113 (Ti+Tr, 5 stored arms)
  BEFORE any L123 pin; PLUS B17-cert: duty machinery recomputed on
  raw_l122 B17 == results_l122.json Ti table (every arm, kL/kR/meanL/meanR)
  BEFORE any window read.

## PRIMARY registered reads (B18; kill criterion VERBATIM L118-L122)

An arm KILLS iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B18, paired legs per-seed vs full on B18).
An arm RESTOREs iff meanR >= .45 AND kR >= 12 (absolute bar; full sat
.469-.505 across B10-B17). SUPER-RAISE (secondary label): meanR >= .60
AND kR >= 12 (ng29: .727/.749).

- W1 (XOR): exactly one of {cutwA, cutwB} KILLs and the other RESTOREs ->
  the kill->raise flip is carried by ONE 5-cell half at quasi-equal mass
  = placement pattern; NAME the half; single-batch, rebase owed before
  citable (L88/L90).
- W2 (BOTH-RESTORE, neither kills): the flip completes within EITHER half
  (k* <= 24 total) — the k29 endpoint decomposes; window redundancy.
- W3 (BOTH-KILL): the flip needs cells beyond rank 24 (k* in (24,29]) or
  the whole window — kill-side coherence extends into the window.
- W4 (otherwise): intermediate/mixed — per-arm means/ks DISCLOSED, lottery
  class (L118/L121 middle); no rounding to any story.

## Secondaries (registered, no gate on the watch axes)

- S1: cutk5 KILLs on B18 -> 6th consecutive batch (B12/B14/B15/B16/B17/B18)
  of the L120 XOR kill; a miss DISCLOSED (L118 lottery class).
- S2: cutng19 KILLs + cutng29 SUPER-RAISES in-batch (3rd batch each;
  B16/B17/B18).
- R4 (L90 pooled form): batch-union B16+B17+B18 n=48 per-arm
  k(duty_Ti_R>=.5) FULL-PRECISION Wilson for {full, cutng19, cutng29,
  cutk5, cut58}; B16/B17 sides CERTIFIED vs stored results jsons before
  pooling. New arms (wA/wB) are B18-only: single-batch, no pooling.
- Watch: Ti_L (l121 non-monotone mirror), Sr_R (killed by every ng dose on
  2 batches; lottery, no gate), 5-pair x 10-arm table.
- P4: 0.01 < af < 0.9 every arm/seed; b65 af-mean band [.105056,.113056].
- Full-arm B18 disclosure bands (l122 widened form): Ti L (.25,.48) R
  (.35,.58); Sr L (.08,.25) R (.30,.50).
- Sanity: Ti cut kL >= 14; b65 16/16 both sides; cut19 kL >= 12. Miss =
  DISCLOSED, never abort.

## Verdict output

l123/results_l123.json: c0b (+B17-cert), p0 (C0A/120/121/122 + 6 stored
gains + fresh wA/wB), p4, table (5 pairs x 10 arms), dose (Ti/Sr curves
incl wA/wB + kill/restore booleans + W1-W4 + S1/S2), pooled (R4 n=48),
watch, sanity. raw_l123.npz checkpointed BEFORE analysis (L45a rule);
raw_partial resume-safe per-seed.
