# PREREG — L202: ru2-necessity registered replicate + the bilateral twin + chain second batches

Registered 2026-11-22 ~15:45 EST. Owner-directed (`BRIEF_necessity.md`);
experimenter = Miso session (claude-fable-5-2). Frozen (sha256 in
`PREREG.sha256`) BEFORE the L202 harness is written or executed; `FREEZE.json`
(script + static shas) is written after the zero-rollout static pass and
BEFORE any rollout. Workers and the verdict assert both.

What I had seen before writing this (all of it): `l200/L200-FINDINGS.md`,
`l200/PREREG.md`, `l200/SELECTION.md` (covariates of ranks 1-5, incl. 67125 and
67756), `l187/L187-FINDINGS.md`, `l190/` PREREG + FINDINGS + selection, the
L200 harness source, and one zero-rollout probe (`ref_probe.py`: seed key scan
over 301 npz, which stored file carries which arm, stored gain floats). NOT
looked at: L198's stored rcut / rcutF rows, any outcome of removing 67125 or
67756, any ru2 trace under carrier removal beyond L200's printed +.030.

## Ids (re-derived in-script from stored artifacts, never prose)

carrier = gi 1110 (DNp33-L, +); ru2 = gi 70994 (IN07B031-R, inhibitory cord
interneuron); relay = gi 75494; **rank-4 bilateral twin = gi 67125**
(IN00A048-L; frozen `l200/selection.json` top5[3]: dL 7.854 / dR 7.298, 9 / 8
edges onto PM_L / PM_R, x̄ .248, total-drive ratio .286); rank 5 = gi 67756
(IN09A043-L; dL 8.127 / dR 8.214, 7 / 7 edges, x̄ .199, total-drive ratio
.168); L190 edge = 1110→75494 (21 syn), sham = 48→75494 (22 syn). Limit fixed
now: both bilateral candidates match ru2's LEFT and RIGHT premotor drive
(ru2 7.977 / 6.634) but carry 29% / 17% of its TOTAL drive.

## Machinery

`nec_run.py` = count-asserted additive transform (`build_nec.py`) of the
certified L200 harness `l200/ru2_run.py` (sha d3dffb6b7032…, in L200's
FREEZE). VERBATIM: extraction, build()/wb()/pools_for(), add_arm /
add_arm_multi / add_alias / add_base_alias / gen_init, the L187 arms block,
the L198 twin block and the L200 block (both re-pointed READ-ONLY at their
frozen selection files), settle_states, bisect_vec, the rollout step loop,
store keys, per-seed atomic checkpoints, the L200 carrier-replay line.
ADDED: the L202 block (new graphs, edge arms in L190's CSR-entry-removal form,
CERT-SUB), ONE ru2-replay line pair (settle + window loops), gains + anchors
block, tail. Constants unchanged. Readout `verdict_l202.py` = the L200
verdict's helper block VERBATIM (L198 helpers + left mirror) + an L202 tail.

## Seeds

FRESH **B45 = 3737..3752, n = 16 for every arm** (next free 16-block on the
lineage's 32-grid; key-scanned absent from every npz in the lab, re-asserted
in-script by every process). Anchor seeds rolled FIRST, never sampled:
801, 901, 3545, 3609, **3641**, 3673, **3705**.

## Arms (k=24 cutwA base; 4 workers × 1 thread = 4 CPU; cutwA in EVERY worker)

| arm | graph | gain | role |
|---|---|---|---|
| `sc25` / `sc25F` | wA − 1110 | L175 stored 0.1454454553127289 EXACT / g_cutwA | carrier removal; `sc25F` = the OWED fixed-gain comparator |
| `l2c` / `l2cF` | wA − {70994, 1110} | re-bisected, must equal L200's 0.14273352026939398 EXACT / g_cutwA | **replicate**: ru2 cut on the carrier-removed graph |
| `s2k` / `s2kF` | wA − 1110, **ru2 replay-clamped at its base trajectory** | sc25's gain (no bisect under a clamp) / g_cutwA | **necessity direction** |
| `l2` | wA − 70994 | L198 stored 0.14322753667831417 EXACT | same-batch reference for the twin branch |
| `lt4` / `lt4F` | wA − 67125 | re-bisected / g_cutwA | **rank-4 bilateral twin** |
| `lt5` | wA − 67756 | re-bisected | secondary bilateral twin (declared addition) |
| `t4c` / `t4cF` | wA − {67125, 1110} | re-bisected / g_cutwA | wipe-specificity control (declared addition) |
| `rcut` / `rcutF` | wA − 75494 | L187 stored 0.14347783327102664 EXACT / g_cutwA | chain batch |
| `edge` | base minus the single CSR entry 1110→75494 | re-bisected, must equal L190's 0.14314373373985292 EXACT | chain batch |
| `sham` | base minus the single CSR entry 48→75494 | re-bisected, must equal L190's 0.14365692973136904 EXACT | chain batch |

Plan: w0 sc25, sc25F, l2c, l2cF · w1 l2, s2k, s2kF, lt5 (+ cert arm `bk2` on
801 / 901) · w2 lt4, lt4F, t4c, t4cF · w3 rcut, rcutF, edge, sham.

**Necessity transform, exactly:** `s2k` steps the carrier-removed graph; after
every state update (all 400 settle steps, all 6000 window steps; the init draw
is already the base's) ru2's entry is overwritten with ru2's value in the
SAME-seed, SAME-step `cutwA` rollout of the same process (cutwA stepped first).
ru2 is present with all its wiring and emits its base trajectory bit-for-bit;
every other cell is free. `s2k` runs at sc25's gain so it differs from `sc25`
ONLY by the clamp line; `s2kF` likewise from `sc25F`. "ru2-cut on the sc25
graph" is `l2c` itself (same matrix: wA − {70994, 1110}).
Limits, stated now: (i) in this model class a cell acts only through its rate,
and a cell clamped to 0 from t = 0 IS the cut graph (L187 item 7, bit-identical),
so "wiring present, activity absent" is not a separate condition — the cut is
the activity-absent pole. The clamp is the pole "present, emitting what it
emits when the carrier is there". (ii) The base trajectory differs from ru2's
free trajectory under carrier removal in mean (L200: +.030) AND in its
moment-to-moment coupling to the carrier-absent network; N2 below cannot
separate those two.

## Readout and bands (inherited instrument, unchanged)

`duty_07` (chopped 0.7-Hz windows) and 1.4-Hz middle-segment duty on the LEFT
and RIGHT Ti pairs. Per arm and side: k (seeds ≥ .5), mean, paired d vs
same-seed cutwA and vs named arms (95% t-CI, df 15). n = 16 bands: **SUPER**
mean ≥ .60 AND k ≥ 12; **NOT-SUPER** k ≤ 8 AND mean ≤ .50; else
**INTERMEDIATE**. **Signature** (`sig`): 1.4-Hz middle-segment mean ≥ .25.

## Certification (all must hold BEFORE any B45 value is read)

- **C0A-a (mandatory):** cutwA @801/901 == `l135/raw_l135.npz` (22 trace keys
  + af) in EVERY worker (+ sc25 vs stored cutng25, w0).
- **C0A-b..f:** @3545 vs L175 raws (cutwA; sc25) · @3609 vs L187 (cutwA; sc25,
  sc25F; rcut, rcutF) · @3641 vs L190 (cutwA; sc25; **edge ~ E-edge, sham ~
  E-sham** — my re-implementation of L190's arms must reproduce L190's raws) ·
  @3673 vs L198 (cutwA; sc25, sc25F; l2 ~ ru2; rcut, rcutF) · **@3705 vs L200
  (cutwA; sc25; l2c, l2cF; l2)** — the wipe's own source arms reproduce.
  Each: 22 keys + af + x_mean + xwin + stored cell traces, max 0.0.
- **CERT-G:** stored-form bisect returns the stored float EXACT for cutwA
  (every worker), sc25, l2c, l2, rcut, edge, sham.
- **CERT-SUB (static):** lt4, lt5, t4c == base minus the cell(s); edge / sham
  == base minus exactly one CSR entry whose value equals L190's stored weight.
- **CERT-REPLAY:** stored ru2 trace of `s2k` / `s2kF` == same-worker cutwA's on
  every seed. **CERT-NULL:** `bk2` (base graph + the ru2 replay line) ==
  cutwA on 801 / 901 (22 keys + af + x_mean). **CERT-X:** cutwA identical
  across workers on all 23 seeds. **CERT-METRIC:** the verdict reproduces the
  stored L200 B44 rows (cutwA, sc25, l2c, l2cF, l2: k, mean both sides, right
  1.4-Hz) EXACT before any B45 read.
Any C0A / CERT-G / CERT-REPLAY / CERT-NULL failure = that worker VOID, no read
of its arms; a voided worker may be repaired and re-launched only if no B45
value of that worker was read, and the repair is disclosed.

## Registered branches (RIGHT side unless stated; re-matched form carries the label)

0. **Gates.** `E0`: cutwA right SUPER on B45 → no W / S / N claim (left SUPER →
   no T claim). `CTRL_carrier_ok` iff sc25 right SUPER AND sig; else W, S, N
   are DESCRIPTIVE (nothing to wipe).
1. **W — the wipe (registered prediction: l2c ≪ sc25, signature ≈ 0, all seeds
   lower).** d = paired right duty l2c − sc25.
   - CI upper < 0 and l2c NOT-SUPER and no sig → **W1_wipe_replicates**
   - CI upper < 0 otherwise → **W2_partial_wipe**
   - CI spans 0: l2c SUPER with sig → **W0_no_wipe**; else **W2_unresolved**
   - CI lower > 0 → **W3_reversed**
   Same rule on l2cF − sc25F = `W_fixed` (the owed comparator); `gain_form`
   AGREE / DEPENDENT. "Replicates with the fixed-gain comparator" = W1 in BOTH
   forms. Printed, not gating: seeds lower (of 16), paired 1.4-Hz contrast,
   `signature_near_zero` = l2c 1.4-Hz mean ≤ .10, l2c vs base.
2. **T — the bilateral twin (LEFT duty).** `REF_ru2_ok` iff `l2` left SUPER on
   B45 (else T is DESCRIPTIVE). lt4 left NOT-SUPER → **T1_bilateral_specific**
   (no flip); SUPER → **T2_flip**; INTERMEDIATE → **T_unresolved_band**.
   Flags: lt4F class (gain form), lt5 class, `T_count` = number of {lt4, lt5}
   left SUPER, right classes of both. Scope: with L200's lt1 / lt2 this makes
   four cells, two of them bilateral.
3. **S — is the wipe specific to ru2 (t4c, RIGHT).** t4c SUPER with sig →
   **S1_wipe_specific** (the regime survives the twin's absence); NOT-SUPER
   and no sig → **S2_generic_wipe**; else **S_partial**. t4cF flag. Read only
   under W1 / W2_partial; otherwise descriptive.
4. **N — activity vs presence (s2k, RIGHT).**
   - s2k SUPER with sig → **N1_presence_at_base_activity_suffices** (the
     carrier phenotype needs ru2 there and emitting; it does not need ru2's
     response to the carrier's loss)
   - s2k NOT-SUPER and no sig → **N2_needs_ru2_free_activity** (holding ru2 on
     its base trajectory abolishes the phenotype like the cut does)
   - else **N3_partial**, sub-labelled `chopped_only` (SUPER, no sig),
     `signature_only` (sig, not SUPER) or `band`.
   Reported: retained fraction (s2k − l2c) / (sc25 − l2c) for chopped duty and
   for the 1.4-Hz duty (a direction only if the denominator CI spans 0),
   paired s2k − sc25 and s2k − l2c, ru2's free rate under sc25 vs its clamped
   (= base) rate, s2kF by the same rule (`gain_form`). Read only under
   W1 / W2_partial; otherwise descriptive.
5. **C — chain batches (descriptive replication labels).** rcut / rcutF:
   `replicates` iff right SUPER without sig (L187's class). edge / sham: L190's
   registered rule VERBATIM (B1 SUPER + sig; B2 no sig and |paired shift| <
   .10; B3 no sig, shift ≥ .10, CI lower > 0; else unresolved); `replicates`
   iff edge = B3-partial, sham = B2-edge-inert. Pooled rows with the stored
   batches (rcut: B41 + B43 + B45; edge / sham: B42 + B45; sc25 / l2c: B44 +
   B45) are recomputed from stored raws by the same helper.
A result outside every cell above is labelled `UNREGISTERED_SHAPE` and reported
as such. Nothing here licenses a paper edit.

## Predictions (to be scored)

- P1 (.80) W = W1_wipe_replicates; (.70) W_fixed = W1 too. (.60) all 16 seeds
  lower; (.75) l2c 1.4-Hz mean ≤ .10.
- P2 (.85) CTRL_carrier_ok; (.75) sc25F right SUPER with sig.
- P3 lt4 left: NOT-SUPER .70 / SUPER .15 / INTERMEDIATE .15. lt5 NOT-SUPER .70.
- P4 (.85) l2 left SUPER; (.85) l2c left SUPER.
- P5 N: N1 .50 / N2 .20 / N3 .30 — no confident mode; ru2's mean rate barely
  moves under carrier removal, which favours N1, but the 1.4-Hz regime may
  need ru2 in the loop.
- P6 S: S1 .65 / S2 .15 / partial .20.
- P7 (.70) rcut right SUPER; (.60) rcutF right SUPER.
- P8 (.55) edge = B3-partial again (it sat on the band edge, 12/16 .624);
  (.70) sham = B2.

## Scope and declared deviations

One fresh batch; one model class; one base (k=24); chopped 0.7-Hz classifier +
1.4-Hz panel. Additions to the brief's letter: fixed-gain twins `l2cF`,
`lt4F`, `s2kF`, `t4cF`; `l2` as same-batch reference; `lt5`; `t4c`; anchors
3641 and 3705. rcut / rcutF already have a second batch (L198 B43) — this is
their THIRD; edge / sham get their second. NOT rolled (slot budget at 4 CPU):
fixed-gain forms of edge / sham, so L190's "no fixed-gain twin" caveat stands.
The clamp holds one cell's output; it cannot say which downstream route
carries the dependence. Two bilateral twins bound "unique" better than none
and still weakly.

## Compute and writes

CPU only, 4 workers × 1 thread, staggered; seeds outer loop; atomic raw
checkpoint per seed; one verdict process after the workers exit. Writes:
`banc/l202/**` and one `LAB-INTENT.md` §L202 append. No DRAFT / LANE edit.
