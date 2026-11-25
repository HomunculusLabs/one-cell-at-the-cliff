# L291 VERDICT -- tick 281, 2026-11-25 05:27 EST

**Registered verdict: NO_DECISION (4 of 7 predictions hold).** Synapse weight
does not carry the group effect, and e14 membership carries it at one size
only: at raw-synapse sums within +/-5% of the used set, the comparators
scatter by 9 to 17 F between sets.

Research only. No live-module edits; the fly duck was never touched (same PID
2706698, NRestarts 0, `/needs` 200 in 0.336 s after); `sessions/` never read
or written.

## What ran

- PREREG frozen 05:05:35 EST, sha256 `670e8f682e48749c5d87383c896a416bacd16c4d2136719896be35912e275252`
  (8661 B). `sets.json` `bf4cba21780991d0…`, harness `edge_run_l291.py`
  `9a7965c7ced69dae…` (1704 lines; A2 lineage by byte-identical slices).
- 17 arms = 15 stratified comparators (5 per size; 3 with e14, 2 without) +
  2 fixed-gain twins. 2 workers, 16 seeds (3769-3784) + 3 anchors each:
  worker 0 exit 0 in 977.7 s (10 arms), worker 1 exit 0 in 892.1 s (9 arms).
- Gates (all in `final_l291.py`, all passed on both workers): cutwA
  bit-identical to A1's stored traces (xmean, the 4x19 control-cell traces,
  532 arrays, af); anchors 801 / 901 max 0.0 with 46 and 25 checks; base gain
  0.14365819573402408 exact; 3068 trace + 15340 pool arrays finite; F =
  0.00022931491480943385 == A1's stored value; L290's stored effects
  re-derived from its arrays to < 1e-9 F.
- `results_l291.json` sha256
  `a8b80c85491417a1f8fbb099c1c8c11854a0ab7ec623b6726c41055c132ff0f7`.

## Analysis script, exercised before the workers finished

`python l291/final_l291.py selftest` PASSED at 05:18, six minutes before the
first worker exited: 9 synthetic scenarios on arrays aliased to L290's stored
arms produced all 6 registered verdicts, all 5 per-metric labels, all 3
contrast statuses, and both values of all 7 predictions. The PARTIAL path ran
for real at 05:18 (0 workers) and 05:25 (1 worker): no effect was read either
time. The selftest caught two build errors in the structure gate before any
result existed.

One error got through: the FIRST FINAL run (05:25:48) halted in the
descriptive table builder with a KeyError on a twin's metric key -- the same
bug the selftest had caught in the structure gate, in a function the selftest
does not reach -- before any effect was printed or written. Fixed (two key
lookups), re-run, exit 0 at 05:26. The fix did not touch `analyse()`.

## Results

F = noise-floor unit 2.293e-4; eps = 2 F. Advantage A = sign(E_used) * D, in F.
Sign-flip p over 16 seeds, resolution 1/65536 (0.00002 is the floor).

| size | used set | E | with e14: E (A, status) | without e14: E (A, status) | label |
|---|---|---|---|---|---|
| 11 | g11 | +4.34 | s11w1 +7.10 (-2.75, BY); s11w2 +6.48 (-2.14, BY); s11w3 +3.35 (+1.00, WITHIN) | s11f1 +8.67 (-4.33, BY); s11f2 -0.54 (+4.88, EXCEEDS) | MIXED |
| 30 | gc30 | +8.73 | s30w1 +14.74 (-6.01, BY); s30w2 +8.28 (+0.45, WITHIN); s30w3 +1.90 (+6.83, EXCEEDS) | s30f1 -1.96 (+10.69, EXCEEDS); s30f2 +2.01 (+6.73, EXCEEDS) | MIXED |
| 46 | gh46 | +9.15 | s46w1 +10.98 (-1.83, WITHIN: under the 2 F floor); s46w2 +12.03 (-2.88, BY); s46w3 +12.16 (-3.01, BY) | s46f1 -2.90 (+12.04, EXCEEDS); s46f2 -2.90 (+12.05, EXCEEDS) | E14_MEMBERSHIP |

BY = EXCEEDED_BY (the comparator moves the pool more than the used set).
Counts (exW / exF / by / within): 11-set 0 / 1 / 3 / 1; 30-set 1 / 2 / 1 / 1;
46-set 0 / 2 / 2 / 1.

- Floor: 12 of 15 stratified arms clear eps (bar 8) -> P1 TRUE. The three at
  the floor are s11f2 -0.54 F, s30f1 -1.96 F, s46f1 -2.90 F (s46f2 -2.90 F
  clears it: 15 of 16 seeds negative).
- Verdict rule: (c) not fired; (a) no metric is exceeded in all 5; (b)
  E14_MEMBERSHIP on 1 metric (needs 2) -> P2 TRUE (exF == 2 on 30 and 46),
  P3 FALSE (the 11-set is beaten by an e14-FREE set), P4 FALSE (the 46-set
  reads as membership: exW 0); (w) 0 metrics; (n) 0 metrics -> NO_DECISION,
  P7 TRUE.
- Fixed-gain twins: gc30f +7.36 F against bisected +8.73 F (1.37 F, same
  sign, within the floor); gh46f +5.87 F against +9.15 F (3.28 F, same sign,
  OUTSIDE the floor). EDGE_NOT_GAIN_GROUP fires 1 of 2 -> P5 FALSE. No sign
  flip this time (L290: 2 of 5).
- Companion (g), e14-free weight-matched against L290's e14-free uniform sets:
  n 11 +5.77 F (p_up 1.5e-5) -> P6 TRUE; n 30 -0.33 F (p 0.68); n 46 -4.34 F
  (p_two 9.2e-5). Weight-matching moved the comparators in OPPOSITE
  directions at the two sizes, so L290's uniform subsets were not a neutral
  reference.
- Cell means (F), with e14 / without: +5.64 / +4.07 (n 11), +8.31 / +0.02
  (n 30), +11.72 / -2.90 (n 46). L290's uniform e14-free means: -1.71 / +0.35
  / +1.44. Single e14 alone: +5.46 F.
- rho(E, effective size) over the 15 arms: +0.09 (midrank).
- VACUOUS BY IDENTITY: none (no comparator equals a used set); duplicate
  draws: none.

## Reading

1. Weight is not the covariate. Inside a +/-5% synapse band the effects span
   9.2 F (n 11), 16.7 F (n 30), 15.1 F (n 46).
2. e14 is not sufficient either. Two e14-bearing 30-sets matched on weight sit
   12.8 F apart (+14.74 against +1.90).
3. The e14 pattern is size-dependent: it holds at 46 edges (both e14-free sets
   at the floor, both with-e14 twins above the used set), is mixed at 30, and
   is refuted at 11, where an e14-free set moves the pool twice as much as the
   used set.
4. Gain is part of the intervention: the 46-set's fixed-gain twin sits 3.28 F
   below its bisected version on the same edges and seeds.

## Seen after the fact -- NOT banked, registered next as L294

Across the 15 stratified arms the effect ranks with the arm's own gain
compensation (bisected gain minus base gain): ordinal rho +0.82 (15 distinct
values each; argsort ranks, no p, no multiplicity control), against +0.20 for
the raw synapse sum. Every arm with a negative gain delta sits at the floor.
The covariates must be registered before that is scored.

## Deviation from the card text (disclosed, PREREG s6)

The card said e14 membership is "REPORTED, never conditioned on". The draws
ARE conditioned on it (3 with / 2 without per size): under pure sum
stratification the chance of drawing no e14-bearing set at n = 11 is about
(1 - 0.201)^5 = 0.33, which would have left the membership question unasked.
