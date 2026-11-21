# L169 PREREG — pre-posting control (a): the GAIN-SWAP 2x2

Card: LANE.md ideas-87 L169 (L167 response card #2, the referee's ranked #2
issue I4). Registered 2026-11-20 ~03:5x EST **BEFORE** any L169 rollout, build
or read. This run is **stage (a) only** — the card's four controls are sliced,
(b) floor-4 re-derived membership, (c) carrier-edge rewire + right-homolog
deletion, (d) fresh-batch carrier-vs-twin at swapped gains are appended to the
queue as L169b/c/d (see LANE.md patch this tick).

## The confound being tested (I4, CONFIRMED-direction / PARTIAL-attribution)

Every arm is re-gained to a matched active fraction (AF_T = 0.10905611018339793).
Our L167 scan of stored gains found the FLIP arms sit **+1.06 .. +1.30%** above
`g_cutwA = 0.14365819573402408` while the non-flip arms sit at **±0.03%**. So
"removing the carrier" and "running at a slightly higher gain" are confounded on
the diagonal of the experiment we have published. `silW` already flips at
g_cutwA UNCHANGED, which bounds the confound but does not break it.

The clean control is the **2x2**: {graph cutwA, graph cutng25} x {gain g_cutwA,
gain g_cutng25}. Two diagonal cells are already stored. This run rolls the two
OFF-DIAGONAL cells on a fresh batch, with the two diagonal cells re-rolled on
the SAME batch and the SAME noise stream so every comparison is paired.

| | gain g_cutwA (.143658…) | gain g_cutng25 (.145445…) |
|---|---|---|
| graph cutwA (K=24 window, carrier KEPT) | `cutwA` (stored: PARTIAL) | **`wAgN`** (new) |
| graph cutng25 (window + carrier 1110 REMOVED) | **`n25gW`** (new) | `cutng25` (stored: SUPER) |

## Arms (ARMS list, additive transform of l150_run.py — no arm removed)

`full`, `b65`, `cutwA`, `cutng25`, `silW`, `eMotTop5`, `eMotBot5` (all seven
inherited verbatim, giving free forward-chain anchors and a third batch for
each) **plus**:

- `wAgN` — `WB = Wb_wA` (the cutwA CSR object itself), `GAIN = G_CUTNG25_STORED`.
  Node set, pools, mech, motor, dng100 aliased to `cutwA`. No bisect, no clamp.
- `n25gW` — `WB = Wb_p25` (the cutng25 CSR object itself), `GAIN =
  G_CUTWA_STORED`. Aliased to `cutng25`. No bisect, no clamp.

Imported gain constants (fixed in advance, both re-derived by this run's own
bisect and asserted EXACT before use):
`G_CUTWA_STORED = 0.14365819573402408`, `G_CUTNG25_STORED = 0.1454454553127289`.

## Operating point — registered DEVIATION, not a failure

The swap arms are **deliberately OFF their matched operating point**; that is
the test. The L30 settled-af assert is therefore re-scoped:

- `af(cutwA) == af(wAgN)` is NOT expected and NOT asserted.
- Registered direction **P-af**: `af(wAgN) > AF_T` (same graph, higher gain)
  and `af(n25gW) < AF_T` (same graph, lower gain), on every seed.
- The four unswapped arms keep the house af identity asserts.
- `|af - AF_T|` is reported for both swap arms as the disclosed mismatch.

## Non-triviality probe (L35/L39 dead-channel class) — must pass first

A swapped-gain arm that comes out bit-identical to its own-gain twin means the
gain never entered the step loop (an arm-leak or alias bug), not a null result.
Registered **C0-NT**: `max|mm(wAgN) - mm(cutwA)| > 0` and
`max|mm(n25gW) - mm(cutng25)| > 0` at seeds 801/901. If either is exactly 0 the
run is VOID and nothing is read.

## Anchor / CERT block (all must pass BEFORE any B35 number is read)

- **Bisect EXACT**: this run's fresh bisects reproduce `G_CUTWA_STORED` and
  `G_CUTNG25_STORED` bit-exactly (house assert, already in l150_run.py), and
  `GAIN["eMotTop5"] / GAIN["eMotBot5"]` reproduce their l145 stored values.
- **C0A-169**: `full, b65, cutwA, cutng25` at seeds 801/901 bit-identical to
  `l135/raw_l135.npz` on mm, xm, the 20 antagonist pools and af (max == 0.0).
- **FC-144**: `silW` at 801/901 bit-identical to `l144/raw_l144.npz`
  `sil1110_wA` (clamp-wiring cert).
- **FC-145**: `eMotTop5`, `eMotBot5` at 801/901 bit-identical to
  `l145/raw_l145.npz`.
- **GRAPH-IDENTITY**: `WB["wAgN"] is WB["cutwA"]` and `WB["n25gW"] is
  WB["cutng25"]` (python object identity) and `N_OF` equal — the ONLY difference
  between each pair is the scalar `GAIN`.
- **B35 absence**: seeds 3417-3432 absent from every stored raw npz in the
  lineage (l107..l154 incl partials).
- **B-cert**: the verdict script reproduces `l150`'s stored B33 Ti table EXACTLY
  (cutwA / cutng25 / silW / eMotTop5 / eMotBot5 kR, kL, meanR, meanL) before any
  B35 value is read.

## Readout (house form, VERBATIM l150_verdict.py)

Ti antagonist pair, per-seed `duty07` (S >= .25 duty over both 0.7-Hz segments
after a 500-step measurement offset), rounded 3dp; `kR/kL` = seeds with
duty >= .5 out of 16; class bands `SUPER = meanR >= .60 and kR >= 12`,
`PARTIAL = .35 <= meanR <= .50 and 3 <= kR <= 8`; paired `dR` against `cutwA`
on the SAME batch is the claim-carrier.

## Registered branches (decided before the data)

- **D1 GRAPH-TRACKING** — `wAgN` NOT SUPER (kR <= 8 and meanR <= .50) **and**
  `n25gW` SUPER (meanR >= .60 and kR >= 12). Verdict: the flip follows the
  GRAPH, not the gain; the I4 confound is **refuted** as the mechanism and the
  draft gains a one-paragraph control with this 2x2.
- **D2 GAIN-TRACKING** — `wAgN` SUPER **and** `n25gW` not SUPER. Verdict: the
  confound is real and load-bearing; the identity claim must be re-scoped to
  "carrier removal acts through the re-gained operating point" and §2 rewritten.
- **D3 MIXED** — anything else (both SUPER, both non-SUPER, or a cell landing
  between the bands). Verdict: report the 2x2 cell by cell, name which axis
  moved and which did not, and state explicitly that the control is
  PARTIALLY informative. No single-word verdict may be written in this branch.

Whatever branch fires, the paired per-seed `dR` tables and the af mismatches
are reported, and **no referee-reported number enters the draft** (L167
evidence rule: every value re-derived under our own tree).

## Scope / limits registered up front

- ONE fresh batch (n=16) per new cell. A single-batch class is BATCH-DRAWN
  (L88/L90); the pooled form needs >= 2 batches before any citable bound, so
  this run's new cells are reported with their n=16 Wilson interval and the
  batch-fragility caveat attached.
- The swap is a 2-point gain probe, not a dose curve; it cannot locate a gain
  threshold between .143658 and .145445.
- CPU only; raw npz checkpointed BEFORE analysis.
