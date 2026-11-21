# PREREG — L198: the relay-matched cord-interneuron twin (closes L187's caveat)

Registered 2026-11-21 ~18:50 EST. Owner-directed (`BRIEF_relaytwin.md`);
experimenter = Miso session (claude-fable-5-2). TWO-STAGE freeze:

- **Stage 1 (this text, frozen BEFORE the selection code is ever executed):**
  selection rule, pool, arms, readout, bands, branches, predictions. At this
  point nothing under `banc/l198/` has been run except the builder (text
  transform, no graph, no census read). The stored census
  (`l175/census_k24.npz`) has NOT been opened by me for any cell other than the
  relay / carrier pins already printed in `l187/static.json`.
- **Stage 2 (`SELECTION.md` + `selection.json` + `FREEZE.json`, written by the
  zero-rollout static pass and frozen BEFORE any rollout):** the picked cell
  and the five runners-up, with covariates. Workers assert both shas.

## Question

L187: removing relay GI 75494 (IN06B033-L, inhibitory VNC interneuron) alone
lifts the chopped 0.7-Hz right-tibia duty into SUPER (rcut 13/16 .697; fixed
gain 13/16 .630) WITHOUT the carrier's continuous 1.4-Hz middle-segment
signature (.020 vs .530). L187's caveat: no matched twin for a cord
interneuron exists, so "the relay does it" is not shown to be special to this
cell. Does a drive-matched cord interneuron do the same?

## Selection rule (brief's rule, the L175 `select()` form re-pointed at the relay)

- **Census:** the STORED 3-seed census of the k=24 base (L175 census mode,
  seeds 801 / 901 / 3561, g_cutwA) — zero new rollouts.
  drive(c) = x_mean_3seed(c) × out|w|(c), out|w| = model-true |Wb| column
  abs-sum on the k=24 closure (`OW_EFF`; inhibitory edges × BETA). Relay
  reference: 86.503 (x̄ .3289 × 262.977), stored.
- **Pool `POOL_T`:** in the k=24 base ∧ annotation `super_class` equal to the
  relay's (`ventral_nerve_cord_intrinsic` = "cord interneuron") ∧ not motor ∧
  not DNg100 ∧ NOT in any prior arm. Prior-arm set, derived from stored
  files (never memory): the lineage `USED` set (78 cells, every `_drop` /
  `silrand_ids` / `clamp_id` key of every `l*/raw_l*.npz`) ∪ all 58 ng-ladder
  cells (covers the L175 window scan) ∪ L175 twins dmA / dmC ∪ L185's cells
  (`r1_cells` + its S2 pick) ∪ L187's cells {75494, 559, 1110} ∪ both
  endpoints of L190's two cut edges.
- **Pick:** argmin |log(drive_c / drive_relay)|; tie-break smaller
  |log(mass_c / mass_relay)| with mass = raw out|w| onto the closure; then
  lowest GI. Cells with zero drive are inadmissible (score = inf).
  **Top-5 runners-up** registered in the same order.
- No sign, side, degree, type or adjacency filter is applied: the brief's rule
  is drive within class. Sign, cell type, side, in/out degree, mass ratio,
  direct edges onto the four Ti pools, and direct edges to / from the carrier,
  the relay and gi 74914 are RECORDED for all six and reported as covariates
  (the L198 lane card's out-degree / out-mass / direct-current matching is a
  different rule; it is reported, not optimised). If the pick is excitatory
  or is wired directly to the relay, that is stated in the findings as a limit
  on "matched", not repaired by re-selection.

## Machinery (inherited; nothing lineage-side edited)

`twin_run.py` = count-asserted additive transform (`build_twin.py`, 9 rep
sites) of the certified L187 harness `l187/relay_run.py` (sha256
b7c486bf3250…, itself a transform of `l175/scan_run.py`). VERBATIM:
extraction, ladder, `build()/wb()/pools_for()`, `add_arm()/gen_init()`, the
whole L187 arms block, `settle_states`, `bisect_vec`, the rollout step loop,
store keys, per-seed atomic checkpoints. REPLACED: env names, seed list,
output dir, the static dump (→ `twin_block.py.txt`: selection + six
`add_arm()` graphs + the L187 CERT-SUB loop on them), the gains + anchors
block, the tail. Constants unchanged. Readout `verdict_l198.py` = the
`l150_verdict.py` helper block (lines 1-71 of `l187/verdict_l187.py`, sha
5c8323f2755f1d0c) + `duty14_seeds` (lines 117-125) VERBATIM + an L198 tail,
written before any rollout.

## Seeds

FRESH **B43 = 3673..3688, n = 16 for every arm** (next slot of the lineage's
32-step grid after L190's 3641..3656). Verified absent from all 242 npz in the
lab by the any-key-endswith scan (pre-registration scan, zero rollouts);
re-asserted in-script by every process. Non-sample anchor seeds rolled FIRST:
801, 901, 3545, 3609.

## Arms (all on the k=24 = cutwA base; 6 workers × 2 threads)

| arm | graph | gain | role |
|---|---|---|---|
| `cutwA` | base | stored 0.14365819573402408 | base; C0A anchor; in EVERY worker |
| `tw` | wA − twin | re-bisected (stored-form, 24 halvings) | **the registered arm — carries the T-branch** |
| `twF` | wA − twin | g_cutwA | fixed-gain twin (L187 lesson: a re-bisect alone moves duty); reported beside |
| `rcut` / `rcutF` | wA − 75494 | must re-bisect to L187's stored 0.14347783327102664 EXACT / g_cutwA | same-batch relay reference ("the relay's profile") |
| `sc25` / `sc25F` | wA − 1110 | L175 stored 0.1454454553127289 EXACT / g_cutwA | carrier removal: same-batch reference for the 1.4-Hz signature |
| `ru1`..`ru5` | wA − runner-up i | re-bisected | SECONDARY, descriptive: the five registered runners-up, rolled as a small drive-matched class null (not in the brief's letter; declared) |

Plan: w0 sc25, sc25F · w1 rcut, rcutF · w2 tw, twF · w3 ru1, ru2 · w4 ru3,
ru4 · w5 ru5. Per-step traces stored for cells 1110 / 75494 / 559 / 74914 /
twin in every arm where the cell exists.

## Readout and bands (inherited verbatim; no new instrument)

`duty_07` on the right Ti pair (chopped 0.7-Hz windows). Per arm: kR (seeds
with duty ≥ .5), meanR, paired dR vs same-seed cutwA (mean, 95% t-CI, df 15).
Bands (n = 16, L175 / L185 / L187): **SUPER** meanR ≥ .60 AND kR ≥ 12;
**NOT-SUPER** kR ≤ 8 AND meanR ≤ .50; else **INTERMEDIATE** (unresolved,
never rounded). **1.4-Hz signature** (L190's registered fingerprint): mean
middle-segment right duty (`duty14_seeds`) ≥ .25. The twin's 1.4-Hz middle
value is recorded and reported whatever the branch.

## Certification (all must hold BEFORE any B43 value is read)

- **C0A-198a (mandatory):** cutwA @801/901 bit-identical to `l135/raw_l135.npz`
  on 22 trace keys + af in EVERY worker (sc25 vs stored cutng25 in w0).
- **C0A-198b:** cutwA (+ sc25 in w0) @3545 bit-identical to the stored L175
  raws (22 keys + af + full x_mean + xwin).
- **C0A-198c:** cutwA in every worker, sc25 / sc25F (w0) and **rcut / rcutF
  (w1)** @3609 bit-identical to the stored L187 raws (22 keys + af + x_mean +
  xwin + stored single-cell traces): the relay arm itself reproduces.
- **CERT-G:** stored-form bisect returns g_cutwA in every worker, the L175
  float for sc25, the L187 float for rcut — EXACT.
- **CERT-SUB (static):** each of the six twin graphs == the base matrix minus
  that cell's rows / columns EXACTLY, maps restricted (L187 loop verbatim).
- **CERT-X:** cutwA identical across the 6 workers on all 20 seeds.
- **CERT-METRIC:** the verdict helper reproduces the stored L187 B41 rows
  (cutwA / sc25 / rcut / rcutF kR + meanR, and the 1.4-Hz means) from the L187
  raws EXACT before any B43 read.
Any C0A / CERT-G failure = that worker VOID before a fresh seed; no read.

## Registered branches (read in this order; `tw` = rematched form)

0. `E0_base_super` — cutwA SUPER on B43: no claim, all descriptive.
1. Reference flags (printed, they qualify the wording, not the label):
   `REF_relay_ok` = rcut SUPER on B43 (the relay's own effect replicates on a
   second batch) else `REF_relay_not_super` (then "special / generic" is
   relative to a relay effect that did not replicate, and the T-label is
   DESCRIPTIVE); `CTRL_carrier_ok` = sc25 SUPER AND signature ≥ .25.
2. **T-branch (on `tw`):**
   - **T2 relay-generic** — `tw` SUPER and no 1.4-Hz signature: the twin
     matches the relay's profile (chopped rise without the fingerprint). A
     drive-matched cord interneuron does what the relay does.
   - **T1 relay-special** — `tw` strict NOT-SUPER and no 1.4-Hz signature:
     the twin reaches neither.
   - **T3 intermediate** — everything else: `T3_band` (`tw` INTERMEDIATE, no
     signature — unresolved by the registered band) or `T3_signature` (`tw`
     shows the 1.4-Hz signature at any class: carrier-like, neither pole).
   `twF`'s class is printed beside; `T_gain_form` = AGREE / GAIN_FORM_DEPENDENT.
   Paired `tw − rcut` and `twF − rcutF` chopped-duty contrasts (95% t-CI) and
   the twin's gain shift are reported under every branch.
3. **Runner-up panel (secondary, descriptive, no branch):** class and 1.4-Hz
   value of each of ru1..ru5; count of the six drive-matched cells (tw +
   ru1..5) in each band. Reading aid fixed now: 0/6 SUPER = the relay's rise
   is not a class property at this drive; ≥ 3/6 SUPER = it is common; 1-2/6 =
   occasional. One batch each.

Nothing here licenses a paper edit; FINDINGS states what it would change.

## Predictions (registered, to be scored)

- P1 (.80): controls — cutwA not SUPER; sc25 SUPER with signature ≥ .25.
- P2 (.65): rcut is SUPER again on B43 (it was 13/16 .697, one seed above the
  kR bar; a miss would not surprise me) and its 1.4-Hz middle stays < .10 (.90).
- P3: T-branch prior **T1 .50 / T3 .30 / T2 .20**. Modal guess T1: L175's
  window null and L185's twins say most single removals leave the base regime
  alone, and the relay sits on the carrier's route while a drive-matched cell
  generally does not.
- P4 (.85): the twin's 1.4-Hz middle mean < .10 (the signature has only ever
  appeared with the carrier removed).
- P5 (.65): at most 1 of the 6 drive-matched cells is SUPER.
- P6 (.60): |gain shift| of `tw` ≤ 0.5% and `tw` vs `twF` agree in class.

## Scope

One batch; one model class; one base (k=24); the chopped 0.7-Hz right-tibia
classifier + the 1.4-Hz panel. ONE primary twin: T1 would say "this
drive-matched cell does not", not "no cord interneuron does" — the runner-up
panel (n = 5, one batch each, descriptive) is what bounds the class. Drive
matching does not match sign, wiring position or downstream targets; those are
reported. No DRAFT / numbers.json / LANE edit follows.

## Compute and writes

CPU only, 6 worker processes × 2 threads (the chain's cap), staggered; seeds
outer loop, atomic raw checkpoint per seed; `results_l198.json` rewritten
atomically by the verdict as seeds complete. Writes: `banc/l198/**` and one
LAB-INTENT.md §L198 append. Deviations from the brief's letter, declared:
same-batch relay and carrier reference arms; a fixed-gain twin; the five
registered runners-up rolled as secondary arms; one extra anchor seed (3609)
that re-rolls the stored L187 relay arm; per-step single-cell traces.
