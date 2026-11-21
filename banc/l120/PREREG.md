# L120 PREREG — cutk4-disambiguation (registered BEFORE l120_run.py)

Card: LANE.md ideas-62 L120. Registered 2026-11-17 ~09:15 by Miso, tick 144.
All expectation numbers re-derived from STORED artifacts (l119/static.json +
l119/results_l119.json + l117 stored dose pins), never from log sentences
(L44 rule). Zero rollouts before this file is complete.

## Arms (9)

Anchors (stored seeds 801/901 vs raw_l113): full, b65, cut, cut19, cut58.
NEW/retained ladder arms (deterministic positional filter of glut_desc,
l120/static.json pins, run asserts STOP on miss):
- cutk3  drop [286,313,561]          mass .0268  n 21806  edges 647526
- cutk4a drop [204,286,313,561]      mass .0347  n 21805  edges l120-static
- cutk4b drop [286,313,561,32014]    mass .0346  n 21805  edges l120-static
- cutk5  drop [204,286,313,561,32014] mass .0425 n 21804  edges 647252
k3/k5 pins asserted == l119/static.json EXACTLY (k5 also == l117 stored).
k4a/k4b are MASS-MATCHED BY CONSTRUCTION: rounded masses .0347 vs .0346,
unrounded delta disclosed from static (one-cell difference 204 vs 32014,
the two ids in k5 but not k3; 32014 = the id-block outlier seen since l107).
NO RNG draw arm in L120.
Seeds: [801, 901] anchors + FRESH B15 = 1901-1916 (asserted absent from
raw_l113.npz, l115, l117, l118, AND l119/raw_l119.npz).
NOTE (L121 sharing): card says B15 shared with L121, whoever runs second
takes B16 — L120 runs first, takes B15; L121 (if later) takes B16.

## P0 anchors (gates)

- C0A FULL-BATCH bit-identity vs raw_l113: stored arms {full,b65,cut,cut19,
  cut58} x seeds {801,901} x keys {mm,xm,Ti/Tr f/e x L/R} + af keys;
  max |diff| MUST be 0.0 (50th consecutive chain anchor if green).
- C0A-119 (NEW anchor class): cutk3/cutk5 x seeds {801,901} vs
  l119/raw_l119.npz on ALL pool keys (Ti/Tr f/e + Ta/Sr/Pr a/b, both sides)
  + mm/xm + af — l119 ran every arm at all 18 seeds, so these two arms have
  stored counterparts; max |diff| MUST be 0.0. cutk4a/cutk4b have NO stored
  counterpart (excluded BY NAME, disclosed).
- Stored-gain re-bisects EXACT: g_cut == 0.14510760426521305 (l107),
  g_cut19 == 0.15096808075904844 (l111), g_cut58 == 0.15417299151420596
  (l113), g_cutk5 == 0.13981970071792604 (l117/l119), g_cutk3 ==
  0.17404209494590758 (l119 fresh gain, NEW stored-form anchor for k3 —
  the bisect is deterministic, so l120 must land on it EXACTLY).
- cutk4a/cutk4b bisected FRESH; gain band .14-.16 is a DISCLOSURE band,
  never an abort (l117/l118/l119 precedent: outside-band gains disclosed,
  af target-matched).
- C0B machinery certification on stored raw_l113 (Ti+Tr tables, all 5
  stored arms, B10) BEFORE any L120 pin (L85/L109 rule) — in verdict.

## P1 PRIMARY — which cell completes the R-kill (B15, n=16)

Kill criterion (L118/L119 registered form, verbatim): an arm KILLS iff
  meanR <= m0 - .10  AND  kR <= 4  AND  mean paired dR <= -.20,
where m0 = full-arm Ti meanR on B15, paired legs per-seed vs full.
Same-batch curve points: {0 (full), 3 (cutk3), 4a (cutk4a), 4b (cutk4b),
5 (cutk5), 19 (cut19)} all fresh on B15.
Registered outcomes:
- XOR (exactly one of 4a/4b kills): the completing cell is NAMED (204 or
  32014); minimal killing set = 4 cells; placement claim at single-cell
  resolution INSIDE the heavy-5 set.
- BOTH kill: k* = 4; the kill window tightens to k3->k4; both remaining
  candidates suffice — placement is 2-cell-redundant at matched mass.
- NEITHER kills (while cutk5 kills): the kill needs the FULL heaviest-5
  SET — a 5-cell coherent unit; k4 arms at ~.0347 sit in the gap.
- cutk5 itself fails to kill on B15: BATCH-DRIFT disclosed (l119's k5 kill
  was B14; l117's B12) — 4a/4b reads still reported but the k* claim is
  downgraded to same-batch-only, never rounded (L118 lottery class).

## P1b PRIMARY — the mass bound (registered reading, no new arm)

If EITHER k4 arm kills at ~.0347 mass, the kill mass bound tightens from
l119's [.0268 no-kill, .0425 kill] to [.0268, .0347]; if neither kills the
bound stays [.0347, .0425]. Because k4a/k4b are mass-matched to .0001,
a XOR outcome is PLACEMENT-PURE by construction (mass cannot explain a
difference that small; disclose the unrounded delta from static).

## Secondaries (registered, no gate)

- L-axis (Ti_L): l119 measured single-cell CHAOS (.357/.553/.271 at
  k 0/1/2); B15 curve reported, no claim.
- Sr_R watch (lottery axis, L116/L117/L118/L119): reported, no gate.
- P4: 0.01 < af < 0.9 every arm/seed; b65 af-mean band [.105056, .113056].
- Full-arm B15 disclosure bands: Ti L (.30,.45) R (.35,.55);
  Sr L (.08,.25) R (.30,.50) (l118/l119 form).
- Sanity cells: Ti cut kL >= 14; b65 16/16 BOTH sides; cut19 kL >= 12.
  A miss is DISCLOSED, never an abort.

## Verdict output

l120/results_l120.json: c0b, p0 (incl. c0a119 block), p4, table (5 pairs x
9 arms, per-side k/mean/Wilson), dose (Ti/Sr R+L curve with 4a/4b legs +
kill booleans), k4 classification (XOR-named / both-k4 / neither /
batch-drift), mass bound line, sr_watch, sanity. raw_l120.npz checkpointed
BEFORE analysis (L45a rule); raw_partial.npz resume-safe per-seed.
