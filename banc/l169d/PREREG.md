# PREREG — L169 stage (d): carrier-vs-twin on a fresh batch at the swapped gains

Registered 2026-11-20 ~12:20 EST (tick 197), BEFORE any computation of this
stage. Lane tick 197. Parent card: LANE.md L169 (ideas 87, external-review
pre-posting controls). Final stage of L169. This stage spends rollouts.

## Question

The preprint's headline is an IDENTITY claim carried by a twin-XOR pair:
`cutng25` (base window + the carrier gi **1110**, DNp33-L, removed) flips the
cord to the SUPER regime while `cutng25p` (the SAME window + the mass-twin
gi **319**, DNpe025-R, removed instead — a 3.9e-04 mass delta) does not.
Stage (a) showed the cutwA-vs-cutng25 transition tracks the GRAPH and not the
af-matched gain. That test has NOT been run on the XOR pair that actually
carries the claim, and the pair's two arms sit at DIFFERENT bisected gains:

    g_cutng25p = 0.1435265743732452   (l135 stored)
    g_cutwA    = 0.14365819573402408  (l123/l135 stored)
    g_cutng25  = 0.1454454553127289   (l135 stored)

so the twin arm runs at a gain **1.33% BELOW** the carrier arm's. Two things
are therefore untested: (i) does the XOR contrast reproduce on a FRESH seed
batch (L88/L90 batch-robustness rule — the stored contrast rests on B24/B25),
and (ii) is it an artifact of that 1.33% gain difference?

## Substrate convention (verbatim, inherited)

l142_run.py extraction, re-used verbatim by l169/l169b2/l169c2: BANC v626
closure (`keep_new = cord_mask | dn_into | dn_proj`), masses
`|log1p(syn) * sign|` with the flyvis glutamate-inhibitory sign arm, ladder
over `dn_new_g` cut at 50% cumulative mass -> K=77, `ng_desc` = the 58
non-glut heavy DNs. `cutng25` = `ng_desc[:25]` deleted (prefix, carrier is
rank 25); `cutng25p` = `ng_desc[:24] + ng_desc[25:26]` deleted (NOT a prefix
— it skips the carrier and takes the twin instead), pins from
`l133/static.json["xor25p"]` (n, drop_ids, mass_removed .2346, edges 644072).
No synapse floor (this is the base substrate, not (b2)'s f4).

## Arms (3 new; the 16 l169c2 arms ride along)

- `cutng25p` — the XOR twin graph, at its OWN af-matched gain. Bisected
  FRESH in-run in the **stored-form** loop: the bisect MUST reproduce
  `G_CUTNG25P_STORED = 0.1435265743732452` EXACTLY (l135/anchors_run.json)
  or the run is VOID. The arm's full per-arm plumbing (POOLS / mech / motor /
  dng100 / WB / N_OF / Xc init / noise slice) already exists verbatim in the
  l131-l169c2 lineage; this stage only adds it to `ARMS`.
- `p25gN` — the `cutng25p` CSR **by object identity**, run at
  `g_cutng25` (the carrier arm's HIGHER gain). Swapped UP.
- `n25gP` — the `cutng25` CSR **by object identity**, run at
  `g_cutng25p` (the twin arm's LOWER gain). Swapped DOWN.

Both swap arms are DELIBERATELY off their matched operating point — that is
the test (stage (a) convention). No clamp, no bisect, no new graph.

Inherited arms (full, b65, cutwA, cutng25, silW, eMotTop5, eMotBot5, wAgN,
n25gW, f4wA, f4ng, f4tw, rew1, rew2, rew3, hom) ride along for the
forward-chain anchors and the stored-gain certification; nothing about them
is re-claimed here.

Batch: FRESH **B38 = 3513-3528** (n=16), anchors 801/901 first. Range
verified absent from all **74** stored raw npzs by key scan BEFORE this
registration (L157 rule: enumerate from stored KEYS, never batch-number
memory; both the `mm_full_<seed>` form and an any-key-endswith scan).

## Metric (inherited verbatim, no new instrument)

`duty_07` per side on the Ti antagonist pair over the 0.7-Hz windows, the
l109/l111/l113 rounding path (round per seed, then mean) as implemented in
l169c2_verdict.py. Per arm: `kR` = seeds with R-side duty >= .5 of 16,
`meanR`, `meanL`, `kL`, Wilson 95% on kR/16.

House classifiers (verbatim):
- SUPER:   meanR >= .60 and kR >= 12
- PARTIAL: .35 <= meanR <= .50 and 3 <= kR <= 8
- NOT-SUPER (control form): kR <= 8 and meanR <= .50

## Certification block (must be green BEFORE any B38 value is read)

- **CERT-1 / FC-169C2** — all 16 inherited arms BIT-IDENTICAL to
  `l169c2/raw_l169c2.npz` at seeds 801/901 on all 22 trace keys + af.
  Adding arms consumes no generator draws (the noise stream is
  seed-parameterized and W-independent); any non-zero = stream break = VOID.
- **CERT-2 / C0A-150 extended to 5 arms** — `cutng25p` BIT-IDENTICAL to
  `l135/raw_l135.npz` at 801/901 alongside the four arms l169c2 already
  anchors there (full, b65, cutwA, cutng25). This is the new arm's wiring
  certificate and it is FREE: l135 rolled `cutng25p` at the same gain under
  the same convention. Non-zero = the new arm is not the l133/l135 arm = VOID.
- **CERT-3 / stored-form bisects** — g_cutwA, g_cutng25, **g_cutng25p**,
  g_eMotTop5, g_eMotBot5 all reproduce their stored values EXACTLY.
- **CERT-METRIC** — the verdict helper reproduces l169c2's stored B37 cells
  (rew1/rew2/rew3/hom/cutwA/cutng25, 4 fields each) EXACTLY before any B38
  value is read.
- **C0-NT(d)** — `p25gN` must NOT be bit-identical to `cutng25p`, and
  `n25gP` must NOT be bit-identical to `cutng25`, at either anchor seed. A
  bit-identical pair means the gain never entered the step loop -> VOID,
  read nothing (L35/L39 dead-channel class).
- **GRAPH IDENTITY** — asserted by python object identity
  (`WB["p25gN"] is WB["cutng25p"]`, `WB["n25gP"] is WB["cutng25"]`) plus a
  swap-is-not-a-no-op gain assert.

## Pre-registered predictions

- **P-af (direction, not identity)** — the swap arms are off the matched
  point BY CONSTRUCTION, so no af identity is registered. Direction:
  `p25gN` (twin graph at the HIGHER gain) settles ABOVE AF_T and `n25gP`
  (carrier graph at the LOWER gain) settles BELOW AF_T. Reported per seed;
  a partial hold is reported as PARTIAL, never rounded up (stage (a) rule).
- **P-stair** — `cutng25p`'s own-gain settled staircase residual
  |af - AF_T| <= 5e-3.
- **P-batch** — `cutng25` reproduces SUPER on B38 and `cutng25p` does not.
  Stored reference (l135, B25): cutng25 kR 15 / meanR .754 vs cutng25p
  kR 5 / meanR .399.

## Registered branches (read in this order; precedence explicit this time,
## after stage (c2)'s R2/R3 ambiguity)

1. **E0_batch_fail** — if `cutng25` on B38 is NOT SUPER (kR < 12), the XOR
   contrast did not reproduce on a fresh batch: report E0, label the whole
   2x2 DESCRIPTIVE, and make no gain claim (L88/L90 batch-fragility rule).
   This branch is checked FIRST and overrides 2-4.
2. **E1_graph_tracking** — `p25gN` NOT-SUPER **and** `n25gP` SUPER: the
   contrast tracks the GRAPH (cell identity), not the gain, on BOTH sides.
   The strongest result available here.
3. **E2_gain_tracking** — `p25gN` SUPER **and** `n25gP` NOT-SUPER: the
   contrast is gain-driven, which REFUTES the headline identity claim as
   currently stated. Must be reported as a refutation, not softened.
4. **E3_mixed** — exactly one of the two swap arms crosses. Report WHICH
   side carries it and scope the draft claim to that side.

Paired legs (per seed, same noise stream), reported for every branch:
`dR(p25gN - cutng25p)` and `dR(n25gP - cutng25)` with n_up / n_down of 16.

## Draft-fold rule

Fold the measured 2x2 into DRAFT §2.7 next to stage (a)'s gain-swap
paragraph, with the branch label the cells actually support. If E2 fires,
the fold is a REFUTATION of the identity sentence, not a caveat. No abstract
edit (the v3.8 vocabulary freeze holds unless a branch forces it).

## Scope clause

Two-point gain probes bound the readout at the two bisected gains only; they
cannot locate a threshold between them (stage (a) disclosure, re-registered).
`cutng25p` rides a 3rd batch here (B24/B25 stored + B38), which is NOT yet
the pooled 4-batch bar the L90 rule asks for — any pooled statement from
this stage is explicitly 3-batch.
