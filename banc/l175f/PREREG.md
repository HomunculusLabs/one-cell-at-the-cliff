# L175 (floor-4 LEFT-side) PREREG — registered BEFORE any B37 value is read

Tick 231, 2026-11-22, Miso (cron). Card: LANE.md ideas 88, L175.

## Why this card exists (honesty statement)

L169 stage (b2) ran the floor-4 dynamic arms (f4wA / f4ng / f4tw) on the
INHERITED R-side duty axis and branch G2_no_transfer fired honestly (all three
f4 arms kR 0/16). The LEFT-side numbers printed by the same table were loud and
in the opposite direction and were written up as `addendum_L_descriptive`,
explicitly DESCRIPTIVE (L162 A2/A3 class: measured with the table in hand, so
no claim). This card registers that read properly on a FRESH batch.

Stored B36 descriptive comparators (quoted here so the bars below cannot be
tuned after the fact; they are re-derived by CERT-L from the stored npz, never
trusted as quoted):

| arm | meanL | kL | meanR | kR |
|---|---|---|---|---|
| f4wA | 0.698 | 16 | 0.043 | 0 |
| f4ng | 0.289 | 2 | 0.081 | 0 |
| f4tw | 0.560 | 10 | 0.082 | 0 |
| cutwA | 0.233 | 0 | 0.371 | 3 |
| cutng25 | 0.106 | 0 | 0.754 | 16 |

Stored paired legs (B36): f4ng−f4wA dL −0.409 (0 up / 16 down);
f4tw−f4wA dL −0.139 (6 up / 9 down); f4ng−f4tw dL −0.270 (5 up / 11 down).

## Design

- Substrate / protocol / arms: l169b2_run.py VERBATIM (floor-4 edge floor on
  the closure node set, f4-re-derived window, fresh per-arm bisects). The run
  script for this card is a MECHANICAL derivation of l169b2_run.py: the ONLY
  edits are (i) the fresh batch, (ii) the output paths, (iii) one added
  forward-chain anchor block. No parameter, gain, arm, metric or window moves.
- Fresh batch **B37 = seeds 3701-3716** (n = 16, matching B36's n), key-scanned
  for absence across every stored `.npz` under `banc/` INCLUDING l169b2's own
  raw + partial before launch (L157).
- Anchors 801/901 ride along (excluded from the sample) for forward-chain
  bit-identity.
- Arms rolled: all 12 of l169b2 (removing arms would be a stream edit). The
  five the card reads are f4wA, f4ng, f4tw, cutwA, cutng25.

## The primary axis (a MIRROR, not a new instrument)

The house duty classifier is applied to the LEFT side with the bands MIRRORED
from `l169b2_verdict.py` (`_super` / `_partial` / `_notsuper`), identical
numbers, side swapped:

- `superL`  := meanL >= .60 AND kL >= 12
- `partialL`:= .35 <= meanL <= .50 AND 3 <= kL <= 8
- `notsuperL`:= kL <= 8 AND meanL <= .50

Per-seed duty, the rounding path, the 0.7-Hz segment mask, MEAS0, the S >= .25
threshold and the Wilson interval are COPIED VERBATIM from
`l169b2_verdict.py` (L85) and certified before use (CERT-L below).

Pair read: `Ti` (as in the stored addendum).

## Registered gate cells (L109 — one object per cell, never ANDed into one verdict)

- **G1 — REPLICATION (the gate on everything else).** On B37, f4wA satisfies
  `superL`: meanL >= 0.60 AND kL >= 12. Reported as two separate bars.
- **G2 — THE CLAIM CARRIER (carrier vs mass-matched twin, L axis).** Paired
  per-seed dL = L(f4ng) − L(f4tw). Registered cell: n_down >= 12 of 16
  (one-sided sign test p = 0.0384) AND mean_paired_dL <= −0.10. Reported as
  two separate bars. NOTE REGISTERED IN ADVANCE: the stored B36 read is
  11/16 down at −0.270, i.e. it FAILS the 12/16 count bar it is being held to.
  That is deliberate — the count bar is the house 12-of-16 band mirrored, and a
  descriptive read that sits one seed under its own bar is exactly the kind of
  claim a fresh batch exists to adjudicate.
- **G3 — ASYMMETRY OF COST (the "nearly 3x" read).** |mean dL(f4ng − f4wA)|
  >= 2.0 x |mean dL(f4tw − f4wA)|. One bar.
- **G4 — SIDE-SWAP DIAGNOSTIC (descriptive, no claim).** Per-seed side
  dominance (meanL > meanR per seed) on the floored arms vs the base arms, plus
  a STATIC per-side in-mass read of the Ti pools on the base vs floored graph
  with a membership permutation null (L45b/L70 handedness class: permute the
  per-side pool membership before hunting a wiring cause). Reported; no branch
  depends on it.

## Branches (registered before the run)

- **B_REPLICATES_IDENTITY** — G1 passes AND G2 passes: the floored substrate's
  LEFT-side structure is real on a fresh batch and the carrier/twin separation
  is a registered identity signal on the L axis. The §4 DESCRIPTIVE label on
  this sentence may be lifted, with the floor-4-substrate scope stated.
- **B_REPLICATES_FLAT** — G1 passes, G2 fails: the L-side structure is real but
  the carrier/twin leg does not separate at the registered bar; the identity
  claim stays DESCRIPTIVE and the card reports a substrate finding only.
- **B_BATCH_DRAW** — G1 fails: the stored L-side read was a batch draw (L88
  class). The card is then a negative replication report; G2/G3 are reported
  for completeness but carry nothing, and the §4 sentence stays labelled.
- **B_VOID** — any anchor/CERT below fails: the run is void and nothing is read.

## Verification (all must pass BEFORE any B37 number is read)

1. **PREREG first** — this file is written and frozen before the run script.
2. **FC-169B2 (the card's registered anchor)** — all 12 arms x the stored trace
   keys x seeds 801/901 must reproduce `l169b2/raw_l169b2.npz` at
   max|d| == 0.0, plus af exact. Any non-zero = stream break = B_VOID.
3. **The inherited anchors ride along unchanged** — FC-169 (9 arms vs
   `l169/raw_l169.npz`), C0A-150, FC-144, FC-145, C0-NT, C0-NT(b2), and the
   four stored-form bisect EXACT asserts, all as in l169b2_run.py.
4. **Gain identity** — the three fresh f4 bisects must land EXACTLY on
   l169b2's stored gains (f4wA 0.15051452517509462, f4ng 0.16230986118316648,
   f4tw 0.15261898636817928); the bisect is deterministic over anchors 11/22/33
   and a drift here is a substrate change.
5. **CERT-L (the metric copy)** — my L-side metric, run on the STORED
   `l169b2/raw_l169b2.npz` over B36, must reproduce the stored
   `addendum_L_descriptive` rows (meanL / kL / meanR / kR for all five arms)
   and all three stored paired legs EXACTLY, before any B37 trace is touched.
6. **B37 absence scan** across all stored npzs (L157), re-asserted post hoc.
7. **Op point** asserted per seed per arm (L30); raw checkpointed BEFORE
   analysis (L43).

## Fold rule

Fold into the draft ONLY on B_REPLICATES_IDENTITY, and only as a sentence that
names the floor-4 substrate scope. On any other branch the §4 sentence keeps
its DESCRIPTIVE label and this card reports the branch.
