# PREREG — L200: the ru2 left-tibia phenotype

Registered 2026-11-21 ~20:25 EST. Owner-directed (`BRIEF_ru2.md`); experimenter
= Miso session (claude-fable-5-2, anthropic-pinned). TWO-STAGE freeze, L198 form:

- **Stage 1 (this text, frozen BEFORE the selection / wiring code is ever
  executed):** id re-derivation, arms, clamp transform, selection rule, A4
  metrics, readout, bands, branches, predictions.
- **Stage 2 (`selection.json` + `SELECTION.md` + `a4_wiring.json` +
  `FREEZE.json`, written by the zero-rollout static pass, frozen BEFORE any
  rollout):** the top-5 left-matched cells, the two picks, the homolog pick,
  the A4 wiring table. Workers assert both shas.

What I had seen before writing this (all of it): `l198/results_l198.json`
(every arm's stored row, incl. ru2's left duty and x_carrier), L198's
`selection.json` row for ru2, and one feasibility probe (`ref_probe.py`, zero
rollouts, no candidate enumerated, no left/right comparison): left-Ti premotor
pool size 1910; ru2 has 5 edges onto it, sum |w_eff| 26.642, x̄ .2994 →
reference dL 7.977 (the A2 rule is well-posed); seeds 3705..3720 absent from
268 npz. NOT looked at: any candidate twin, ru2's or the carrier's right-side
wiring, ru2's left 1.4-Hz value, any homolog.

## Id re-derivation (brief says: do not trust its prose)

From `l198/selection.json` + `results_l198.json` (asserted in-script):
**ru2 = gi 70994, IN07B031, side right, inhibitory (glut), cord interneuron**
(the brief's first guess gi 67353 is ru4, IN02A026-L). Stored B43 row: left
duty 16/16 mean .840 (base 0/16 .262), right 10/16 .541 INTERMEDIATE, right
1.4-Hz .000, carrier rate x̄ .3906 → .5926, gain 0.14322753667831417 (−0.300%).

## Machinery (inherited; nothing lineage-side edited)

`ru2_run.py` = count-asserted additive transform (`build_ru2.py`) of the
certified L198 harness `l198/twin_run.py` (sha c382f0c4adf0…). VERBATIM:
extraction, ladder, `build()/wb()/pools_for()`, `add_arm()/add_arm_multi()/
add_alias()/add_base_alias()/gen_init()`, the L187 arms block, the L198 twin
block (re-pointed read-only at the frozen `l198/selection.json`, so `ru2`'s
graph is L198's own object), `settle_states`, `bisect_vec`, the rollout step
loop, store keys, per-seed atomic checkpoints. ADDED: the L200 block
(selection, graphs, CERT-SUB, A4), one replay-clamp line in each of the two
rollout loops, gains + anchors block, tail. Constants unchanged. Readout
`verdict_l200.py` = the L198 verdict's helper block VERBATIM + a left-side
mirror of `duty14_seeds` (same instrument, `SL` instead of `SR`) + an L200 tail.

## Seeds

FRESH **B44 = 3705..3720, n = 16 for every arm** (next slot of the lineage's
32-step grid after L198's 3673..3688); key-scanned absent (any-key-endswith
scan over every npz in the lab), re-asserted in-script by every process.
Non-sample anchor seeds rolled FIRST: 801, 901, 3545, 3609, **3673**.

## Arms (k=24 = cutwA base; 6 workers × 1 thread = 6 CPU)

| arm | graph | gain | role |
|---|---|---|---|
| `cutwA` | base | stored 0.14365819573402408 | base; C0A anchor; EVERY worker |
| `l2` / `l2F` | wA − 70994 | re-bisected, must equal L198's stored 0.14322753667831417 EXACT / g_cutwA | **A1 replicate** |
| `lt1`,`lt2` / `lt1F`,`lt2F` | wA − twin i | re-bisected / g_cutwA | **A2 left-matched twins** |
| `l2c` / `l2cF` | wA − {70994, 1110} (`add_arm_multi`) | re-bisected / g_cutwA | **A3a** ru2 + carrier removed together |
| `l2k` / `l2kF` | wA − 70994, carrier replay-clamped | g_l2 (no fresh bisect) / g_cutwA | **A3b** ru2 removal, carrier held at base levels |
| `sc25` | wA − 1110 | L175 stored 0.1454454553127289 EXACT | same-batch carrier reference |
| `l2h` | wA − ru2's left homolog (rule below) | re-bisected | SECONDARY, descriptive (not in the brief's letter; declared) — if no homolog exists, `sc25F` is rolled in its slot |

Plan: w0 sc25 + l2h · w1 l2, l2F · w2 lt1, lt1F · w3 lt2, lt2F · w4 l2c, l2cF ·
w5 l2k, l2kF (+ cert arm `bk` on 801 / 901 only).

**A3b transform, exactly (feasible; registered):** `l2k` steps ru2's removed
graph; after every state update — init, all 400 settle steps, all 6000 window
steps — the carrier's entry is overwritten with the carrier's value in the
SAME-seed, SAME-step `cutwA` rollout of the same process
(`X[l2k][carrier] = X[cutwA][467]`; cutwA is stepped first each step). So the
carrier's whole rate trajectory is the base's, bit-for-bit, while every other
cell is free. Gain = `l2`'s re-bisected gain (no bisect under the clamp), so
`l2k` differs from `l2` ONLY by the clamp line; `l2kF` likewise from `l2F`.
Certs: CERT-REPLAY (every seed: stored carrier trace of `l2k`/`l2kF` ==
cutwA's, max 0.0) and CERT-NULL (`bk` = base graph + the same replay line must
be bit-identical to cutwA on 801 / 901: 22 keys + af + x_mean — replaying a
cell onto itself is the identity).
Limit, stated now: this holds the carrier's OUTPUT at base; inputs to the
carrier still change and are simply not propagated. It tests "the flip needs
the carrier's rate change", which is what "routes through the carrier" means
here. A3a (carrier absent) answers a different question (flip needs the
carrier at all) and is corroboration only.

## A2 selection rule (register rule + top-5 before choosing)

- **Left-Ti premotor pool `PM_L`:** non-motor cells of the k=24 base with ≥ 1
  base edge onto a left-tibia motor neuron (`Ti_fL ∪ Ti_eL`, 56 MNs). `PM_R`
  mirrored (`Ti_fR ∪ Ti_eR`). Pools may overlap; that is reported in A4.
- **dL(c)** = x̄_3seed(c) × Σ over c's base edges onto `PM_L` of model-true |Wb|
  (inhibitory × BETA); x̄ from the STORED 3-seed census `l175/census_k24.npz`
  (801 / 901 / 3561) — zero new rollouts. Reference dL(ru2) = 7.977.
- **Pool:** in the k=24 base ∧ `super_class` = ru2's (cord interneuron) ∧
  effective sign = ru2's (inhibitory) ∧ not motor ∧ not DNg100 ∧ not in any
  prior arm (L198's `PRIOR` set ∪ L198's six cells) ∧ not ru2's homolog pick.
  Sign filter is a declared tightening of L198's rule: an excitatory cell with
  equal drive onto the pool is not a twin of an inhibitory one.
- **Rank:** ascending |log(dL(c) / dL(ru2))|; tie-break |log(total-drive
  ratio)|, then gi. dL = 0 inadmissible. **Top-5 registered; twins = ranks 1
  and 2** (`lt1`, `lt2`); ranks 3-5 recorded, not rolled.
- No side, type, degree, total-drive or adjacency filter. Recorded covariates
  for all five + ru2: side, type, x̄, total drive ratio, dL, dR, edges onto
  PM_L / PM_R, membership in PM_L / PM_R, direct edges onto the four Ti MN
  pools, edges to / from the carrier and ru2. A twin that is itself left-Ti
  premotor, or far from ru2 in total drive, is reported as a limit on
  "matched", not repaired by re-selection.
- **Homolog (`l2h`, secondary):** cord interneurons in the base with
  `cell_type` == ru2's and side == left, not motor / DNg100 / prior-arm; if
  several, the largest census total drive; if none, no arm.

## A4 mirror-symmetry probe (wiring only, zero rollouts; metrics fixed now)

For s ∈ {carrier 1110, ru2 70994} on the base edge set, model-true weights:
1. one-hop: edges and Σ|w| onto `PM_L`, `PM_R`, their intersection; share of
   s's total out-mass; **LI1(s) = (m_R − m_L) / (m_R + m_L)**.
2. direct edges onto the four Ti MN pools.
3. two-hop onto each Ti MN pool (f/e × L/R): signed Σ_p W[m,p]·W[p,s] and abs
   Σ_p |W[m,p]|·|W[p,s]|; **LI2(s) = (A_R − A_L) / (A_R + A_L)** on the abs
   two-hop mass per side (flexor + extensor).
4. target overlap: Jaccard of the two direct target sets (`J_same`); Jaccard
   of {(cell_type, side)} of the carrier's targets vs {(cell_type, flipped
   side)} of ru2's (`J_mirror`), typed + sided targets only; same two on the
   premotor-restricted target sets (carrier ∩ PM_R vs ru2 ∩ PM_L).
5. context: ru2's LI2 percentile among all cord interneurons of the base with
   positive two-hop Ti mass.
**Label:** `A4_mirror` iff LI2(carrier) ≥ +.20 AND LI2(ru2) ≤ −.20;
`A4_same_side` if both |LI2| ≥ .20 with equal sign; else
`A4_no_laterality_contrast`. Wiring describes routes, not dynamics; the label
is reported beside the M-branch and never changes it.

## Readout and bands (inherited instrument; left side read with the same code)

`duty_07` (chopped 0.7-Hz windows) on the LEFT and RIGHT Ti pairs; 1.4-Hz
middle-segment duty on both sides. Per arm and side: k (seeds ≥ .5), mean,
paired d vs same-seed cutwA (95% t-CI, df 15). Bands (n = 16), both applied to
both sides: **SUPER** mean ≥ .60 AND k ≥ 12; **NOT-SUPER** k ≤ 8 AND mean ≤
.50; else **INTERMEDIATE** (never rounded). **1.4-Hz signature**: middle-
segment mean ≥ .25 on that side. Carrier rate = window-mean x of gi 1110.

## Certification (all must hold BEFORE any B44 value is read)

- **C0A-200a (mandatory):** cutwA @801/901 bit-identical to `l135/raw_l135.npz`
  (22 trace keys + af) in EVERY worker (sc25 vs stored cutng25 in w0).
- **C0A-200b:** cutwA (+ sc25, w0) @3545 == stored L175 raws.
- **C0A-200c:** cutwA every worker (+ sc25, w0) @3609 == stored L187 raws.
- **C0A-200d (forward chain):** @3673 cutwA every worker, sc25 (w0) and
  **`l2` (w1) vs L198's stored `ru2` arm** == stored L198 raws (22 keys + af +
  x_mean + xwin + cell traces): the phenotype's own source arm reproduces.
- **CERT-G:** stored-form bisect returns g_cutwA in every worker, the L175
  float for sc25, the L198 float for l2 (w1 and w5) — EXACT.
- **CERT-SUB (static):** lt1, lt2, l2c, l2h graphs == base minus the cell(s).
- **CERT-REPLAY / CERT-NULL:** as above. **CERT-X:** cutwA identical across
  workers on all 21 seeds. **CERT-METRIC:** the verdict helper reproduces the
  stored L198 B43 rows (cutwA / sc25 / sc25F / ru2: kL, kR, meanL, meanR,
  1.4-Hz k + mean) from the L198 raws EXACT before any B44 read.
Any C0A / CERT-G / CERT-REPLAY failure = that worker VOID; no read. One thread
per worker is new for this lineage (L198 used 2): if it breaks bit-identity
the anchors VOID the run before any fresh seed and I relaunch at 2 threads ×
6 workers (the L198 form), disclosed.

## Registered branches (LEFT duty, re-matched form carries the label)

0. `E0_base_left_super` — cutwA left SUPER on B44: no claim.
1. `REF_ru2_ok` = `l2` left SUPER (A1 replicates) else `REF_ru2_not_super`
   (then the M-label is DESCRIPTIVE). Also printed: carrier-rate rise
   replicates (paired d x_carrier CI > 0), right-side class of `l2`.
2. Twins: T = number of {lt1, lt2} whose left class is SUPER.
   - T = 2 → **M3_generic_left_hotspot**; T = 1 → **M3_partial**.
3. T = 0, read the clamp arm `l2k` (left):
   - NOT-SUPER → **M2_cross_coupled** (holding the carrier at base abolishes
     the flip).
   - INTERMEDIATE → **M2_partial** (unresolved by band; retained fraction
     (meanL(l2k) − base) / (meanL(l2) − base) reported).
   - SUPER → not routed through the carrier's rate; then
     **M1_mirror_carrier** iff both twins strict NOT-SUPER AND `l2` shows the
     LEFT 1.4-Hz signature (≥ .25); **M1_unique_no_left_signature** if both
     twins NOT-SUPER without it; **M1_unresolved_twin_band** if a twin is
     INTERMEDIATE.
Printed under every branch (flags, never re-labelling): the clamp class
(`M2_flag`) even when T ≥ 1; fixed-gain classes and `gain_form` AGREE /
DEPENDENT for A1, twins, clamp; A3a `l2c` left class and its right class +
right 1.4-Hz (does the carrier-removal phenotype survive ru2's absence, does
the left flip survive the carrier's); paired left contrasts l2k − l2, l2kF −
l2F, l2c − l2, lt_i − l2; `l2h` right and left classes (literal mirror:
right SUPER); the A4 label.

Nothing here licenses a paper edit; FINDINGS states what it would change.

## Predictions (registered, to be scored)

- P1 (.85): `l2` left SUPER again; (.75) `l2F` left SUPER too.
- P2 (.80): carrier rate under `l2` ≥ .50 (base ≈ .39).
- P3 (.65): T = 0 (neither left-matched twin is left SUPER). M3 (T ≥ 1) .35.
- P4: clamp arm `l2k` left class — SUPER .50 / NOT-SUPER .30 / INTERMEDIATE
  .20. Overall M prior: **M1-family .35 / M2-family .30 / M3-family .35**
  (no modal confidence; I do not know which).
- P5 (.60): `l2` shows NO left 1.4-Hz signature (< .25) — the signature has
  only ever appeared on the right with the carrier removed.
- P6 (.70): `l2c` right is SUPER with right 1.4-Hz ≥ .25 (carrier-removal
  phenotype survives); (.50) `l2c` left SUPER.
- P7 (.30): A4 label = `A4_mirror`.
- P8 (.35): `l2h` right SUPER (literal mirror).

## Scope

One batch; one model class; one base (k=24); chopped 0.7-Hz classifier +
1.4-Hz panel on both tibiae. Two twins bound "generic" weakly: T = 0 says
"these two left-drive-matched cells do not", not "no cell does". Drive onto a
premotor pool is a one-hop static quantity. The clamp arm holds one cell's
output; it cannot exclude routes through cells the carrier does not drive.
No DRAFT / numbers.json / LANE edit follows.

## Compute and writes

CPU only, 6 workers × 1 thread, staggered; seeds outer loop, atomic raw
checkpoint per seed. Writes: `banc/l200/**` and one LAB-INTENT.md §L200
append. Deviations from the brief's letter, declared: fixed-gain forms for
A1 / A2 / A3; a same-batch carrier-removal reference; the homolog arm; the
3673 forward-chain anchor; a sign filter in the A2 pool; A4 adds two-hop
weights and a laterality index to "target overlap".
