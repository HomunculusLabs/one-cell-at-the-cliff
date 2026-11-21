# L122 PREREG — cutng19/cutng29 batch-rebase (B17). Registered BEFORE build/run.

Card: LANE.md ideas-63 L122 (seeded this tick). Registered 2026-11-17 ~12:30
by Miso, tick 146. Expectation numbers re-derived from STORED artifacts
(l121/results_l121.json + raw_l121.npz + l121/static.json pins), never from
log sentences (L44 rule). Zero rollouts before this file.

## Why

L121 shipped two single-batch claims on B16 (2001-2016) that the L88/L90
batch rule says cannot be cited until re-based:
(a) cutng19 (.1946 mass) KILLS Ti_R (.250, kR 0/16, paired dR -.233) —
    first non-glut kill below pool completeness;
(b) cutng29 (.2588) RE-ROLLS R UP to .727 (kR 16/16, dR +.244) — the
    highest R of any arm in the lineage.
This tick re-runs the identical 9-arm dose ladder on FRESH B17 2101-2116
and pools the union (L90 form). l121 machinery VERBATIM (same graphs,
same draw order, same gains); NO RNG arm anywhere.

## Arms (9, identical to l121)

full / b65 / cut / cut19 / cut58 / cutk5 / cutng19 / cutng29 / cutng39.
Drops pinned to l121/static.json EXACTLY (masses .1946/.2588/.3132, edges
644729/643623/642698, k58 == cut58 by set identity + edge recompute).
Seeds: [801, 901] anchors + FRESH B17 = 2101-2116, asserted absent from
raw_l113.npz, l115, l117, l118, l119, l120 AND l121/raw_l121.npz.

## P0 anchors (gates)

- C0A vs raw_l113: stored arms {full,b65,cut,cut19,cut58} x {801,901} x
  {mm,xm,Ti/Tr f/e L/R} + af; max|diff| MUST be 0.0 (52nd consecutive).
- C0A-120 retained: cutk5 vs raw_l120 at 801/901, all pool keys + af.
- C0A-121 (NEW forward-chain class): {cutk5,cutng19,cutng29,cutng39} x
  {801,901} vs raw_l121.npz on ALL 22 pool keys + mm/xm + af; max 0.0.
  (l121 ran every arm at all 18 seeds — L120 addendum rule.)
- Stored-gain re-bisects EXACT: g_cut 0.14510760426521305 (l107),
  g_cut19 0.15096808075904844 (l111), g_cut58 0.15417299151420596 (l113),
  g_cutk5 0.13981970071792604 (l117), AND the new class:
  g_cutng19 == 0.15025991678237915, g_cutng29 == 0.1442639136314392,
  g_cut39.. g_cutng39 == 0.1462542486190796 (l121 fresh gains; deterministic
  re-bisects re-land EXACT — they are STORED-FORM anchors now, L120 rule).
- C0B machinery certification on stored raw_l113 (Ti+Tr, all 5 stored
  arms) BEFORE any L122 pin; PLUS a B16-cert: my duty machinery recomputed
  on raw_l121 B16 == results_l121.json Ti table (kL/kR/meanL/meanR, every
  arm) BEFORE any pooling read.

## PRIMARY registered reads (B17, kill criterion VERBATIM from L118-L121)

An arm KILLS iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20,
m0 = full-arm Ti meanR on B17, paired legs per-seed vs full on B17.
- R1 (kill rebase): cutng19 KILLS on B17 -> the .1946 kill is BATCH-ROBUST
  (2/2 batches); if not, the B16 kill is reclassified batch-drawn (L88
  class) and L121's MASS-FRACTION firing is amended to single-batch.
- R2 (raise rebase): cutng29 raise REPLICATES iff meanR(ng29) >= m0 AND
  kR >= 12 AND paired dR >= +.20 -> the middle-dose lottery + super-raise
  is batch-robust; else single-batch draw (amend L121's "highest R of any
  arm" to B16-only).
- R3 (endpoints, expected stable): cut58 kills (3rd batch of the endpoint)
  and cutk5 kills (5th consecutive batch: B12/B14/B15/B16/B17) — each
  miss DISCLOSED, never silently dropped.
- R4 (L90 pooled form): batch-union B16+B17 n=32 per-arm k(duty_Ti_R>=.5)
  with FULL-PRECISION Wilson bounds for {full,cutng19,cutng29,cutng39,
  cut58,cutk5}; the CITABLE number for any kill/raise claim is the n=32
  pooled read; per-batch k stays diagnostic. B16 side CERTIFIED vs
  results_l121.json before pooling (see C0B). No unrounded-bar rounding:
  Wilson bounds pinned unrounded (L90 note).

## Watch axes (registered, no gate)

- Ti_L per dose (l121 non-monotone mirror; l119 single-cell chaos).
- Sr_R (B16: killed by EVERY ng dose, meanR .002-.103 all kR 0 — most
  fragile axis in the vocabulary; lottery, no gate either direction).
- Tr/Ta/Pr 5-pair table reported.

## Secondaries

- P4: 0.01 < af < 0.9 every arm/seed; b65 af-mean band [.105056,.113056].
- Full-arm B17 disclosure bands (widened per observed B14-B16 swing,
  disclosure only): Ti L (.25,.48) R (.35,.58); Sr L (.08,.25) R (.30,.50).
- Sanity: Ti cut kL >= 14; b65 16/16 both sides; cut19 kL >= 12. A miss is
  DISCLOSED, never an abort.

## Verdict output

l122/results_l122.json: c0b (+B16-cert), p0 (incl. c0a120/c0a121 blocks,
7 stored-exact gain booleans), p4, table (5 pairs x 9 arms, per-side
k/mean/Wilson), dose (Ti/Sr curve + kill booleans + R1/R2/R3 calls),
pooled (R4 n=32 union table), watch, sanity. raw_l122.npz checkpointed
BEFORE analysis (L45a rule); raw_partial.npz resume-safe per-seed.
