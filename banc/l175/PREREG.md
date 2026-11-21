# PREREG — L175 stage (b): single-cell scan + drive-matched twin

Registered 2026-11-21 ~10:55 EST, BEFORE any rollout of this stage (no settle,
no bisect, no census has run). Owner-directed experiment (BRIEF_scan.md);
experimenter = fable 5.2 session. What exists at registration time: the brief,
`build_scan.py` + its three block files, the generated `scan_run.py`, and
`static.json` from `L175_MODE=static` (ZERO rollouts, no RNG: graph tables
only). Nothing in this file was tuned on an outcome.

## Question

Referee r2 §N1: the carrier-vs-mass-twin contrast matches static removal mass
but not delivered drive (twin gi 319 is near-silent). Is the regime flip
(a) carried by delivered drive, (b) carried by the carrier's identity, or
(c) mixed?

## Substrate + machinery (inherited verbatim)

`scan_run.py` is a count-asserted ADDITIVE transform of `banc/l150_run.py`
(sha256 a81a5773ba02…, 1059 lines; 18 rep sites; builder `l175/build_scan.py`).
Extraction, ladder, `build()/wb()/pools_for()`, `settle_states` body, the
rollout step loop and store keys are untouched. Added: `add_arm()` (wA + ONE
extra cell through the lineage builders), a vectorized form of the stored-form
bisect, per-cell x_mean accumulation, MODE dispatch, atomic per-seed
checkpoints, in-run anchors. Constants unchanged (TAU .05, DT .01, BG .02,
NOISE .01, SETTLE 400, WIN 6000, BETA 2, D .2, AF_T 0.10905611018339793).

Window, re-derived with asserts (`static.json`): ng_desc ranks 25..58 = 34
cells; rank 25 = gi 1110 (carrier, DNp33-L), rank 26 = gi 319 (mass twin,
DNpe025-R); masses == `l131/static.json` and `results_l135.json["xor"]["p2"]`
full-precision EXACT; cutwA drop == `l131/static.json` prefix; k58 set ==
`l121/static.json`; carrier out-edges 80 / raw out-mass == `l169c/static.json`
P1. 22 window cells are excitatory, 12 inhibitory (glut-arm sign rule).

## Arms (all on the k=24 = cutwA base: cutwA n = 21,785; every single-cell arm n = 21,784)

| arm | removal | role |
|---|---|---|
| `cutwA` | ng_desc[:24] (lineage plumbing VERBATIM) | base; C0A anchor; rides in EVERY worker |
| `sc25` | wA + gi 1110 | carrier = positive control (== lineage `cutng25`) |
| `sc26` | wA + gi 319 | mass twin = negative control (== lineage `cutng25p`) |
| `sc27`…`sc58` | wA + that rank's cell | the scan (32 new arms) |
| `dmA` | wA + drive-matched twin, any class | Experiment 2 PRIMARY |
| `dmC` | wA + drive-matched twin, carrier's class | Experiment 2 SECONDARY (skipped if == dmA) |

Gain: every arm gets its OWN af-matched gain from the stored-form bisect
(lo .12, hi .18, 24 halvings, 3 settle anchors 11/22/33, GAIN = lo) — the
lineage rule under which the stored carrier/twin results exist. Gains are
reported per arm as a covariate.

Seeds: FRESH **B39 = 3545..3560, n = 16 for EVERY arm** (the brief allows 8
for scan arms; 16 is affordable and is what the referee asked for). Anchors
801/901 rolled FIRST for cutwA/sc25/sc26. Census-only reference seeds
801, 901, 3561 (never in the sample). B39 and 3561 verified absent from all
93 stored npz files under banc/ by an any-key-endswith scan (in-script
assert, re-run by every process).

Power (binomial, per arm, n=16): a base-like arm (pooled wA rate 38/128 =
.297) is called SUPER with p = 2.4e-4 and NOT-SUPER on the kR leg with p =
.976; a carrier-like arm (108/112 = .964) is SUPER with p = .9998; a
mid-rate arm (.65) lands SUPER .29 / NOT-SUPER .16 / in between .55 — the
scan cannot resolve mid-rate cells from one batch, and such arms are
labelled INTERMEDIATE, never rounded. With 34 scan tests the family-wise
false-SUPER rate under the base rate is < 1%. Had n been 8 (bands kR>=6 /
kR<=4), false-SUPER would be 1.1% per arm (~30% family-wise): the reason
for n=16. Single batch: L88/L90 batch-swing law applies to every new cell.

Truncation rule: seeds are the outer loop, so a truncated run leaves the
first m seeds complete on all arms. If m < 16, bands scale as SUPER: meanR
>= .60 and kR >= ceil(.75 m); NOT-SUPER: meanR <= .50 and kR <= floor(.5 m);
m < 8 = no branch read, descriptive only.

## Readout (inherited verbatim, no new instrument)

`duty_07` on the Ti pair per side, the `l150_verdict.py` helper block
(S_of / s_arrays / duty_seeds / side_k / wilson) sliced verbatim into
`verdict_l175.py`. Per arm: kR, kL (seeds with duty >= .5), n, meanR, meanL,
Wilson 95%, paired dR vs same-seed cutwA (mean, n_up >= +.20, n_down <= -.20).

Bands (house, verbatim, n=16):
- **SUPER** ("flips"): meanR >= .60 AND kR >= 12
- **NOT-SUPER** ("does not flip"): kR <= 8 AND meanR <= .50
  (PARTIAL sub-label: .35 <= meanR <= .50 AND 3 <= kR <= 8)
- **INTERMEDIATE**: neither

## Covariates

- x_mean = time-mean of the post-update rate over the full WIN (l137 census
  form), per cell.
- `census_k24.npz`: x_mean of ALL 21,785 k=24-base cells at seeds
  801/901/3561 (+ 3-seed mean, out-weights, drive).
- per arm x per seed: x_mean of every window cell (+ twin picks) in that
  arm (`xwin_*` keys); full x_mean vectors in `xm_w*.npz`.
- out_mass = lineage cord out-mass share (the paper's currency).
- out|w| onto closure = column abs-sum of the matrix the model actually
  steps (`|Wb|`, inhibitory x BETA) over all k=24-base targets; the raw
  `|log1p(syn)|` sum is reported beside it (identical for excitatory cells;
  the carrier is excitatory).
- **delivered_drive = x_mean(k=24 base, 3-seed census mean) x out|w|_eff.**
- active = x_mean > .05 (the paper's bar).

## Experiment 2 selection rule (covariates only; frozen here)

Computed by the census tail of `scan_run.py` from `census_k24.npz` BEFORE
any single-cell arm is rolled; written to `selection.json`; workers read it
and assert pool membership.

- Pool A (primary, the brief's rule): k=24-base cells NOT in ng ranks 1..58,
  NOT in the prior-arm set (78 cells: union of every stored `*_drop`,
  `silrand_ids`, `clamp_id` key over 49 raw npz + hom gi 928), and NOT motor /
  NOT DNg100 — the last two are machinery-required (lineage STOP-asserts:
  pool sizes and the drive channel must be identical across arms; a motor
  drop would edit the readout itself). n = 21,001 (12,386 intrinsic, 7,407
  sensory, 1,208 descending).
- Pool C (secondary): Pool A ∩ pure-projector DNs (`dn_new_g`, the
  population the ladder and the carrier come from) ∩ carrier's effective
  sign (+). n = 313. Rationale: an intrinsic or sensory pick differs from the
  carrier in kind (recurrent participant / entrained input), not just
  identity; dmC holds class and sign fixed.
- pick = argmin |log(drive_cand / drive_carrier)|; tie-break smaller
  |log(mass_cand / mass_carrier)| with mass = raw out|w| onto the k=24-base
  closure (defined for every class); then lowest gi. Top-5 runners-up
  recorded for both pools.
- Each pick: 16 seeds (B39), own bisected gain, same readout.

## Certification (all must hold BEFORE any B39 value is read)

- **CERT-GEN (static)**: generic plumbing for sc25 / sc26 == the lineage's
  hand-written cutng25 / cutng25p plumbing field-for-field (CSR, init maps,
  noise slice, pools, mech, motor, dng100). PASS at registration.
- **CERT-G**: g_cutwA == 0.14365819573402408 in EVERY process;
  g_sc25 == 0.1454454553127289; g_sc26 == 0.1435265743732452 (EXACT floats;
  these also certify the vectorized bisect).
- **C0A-175**: cutwA @801/901 bit-identical to `l135/raw_l135.npz` on 22
  trace keys + af in EVERY process (census + each worker); sc25 vs stored
  cutng25 and sc26 vs stored cutng25p likewise. Any non-zero -> that process
  exits before rolling a fresh seed; run VOID.
- **CERT-X**: cutwA traces identical across all workers on all 18 seeds.
- **CERT-METRIC**: the verdict helper reproduces `results_l135.json` Ti
  cells for cutwA / cutng25 / cutng25p on B26 (kL, kR, meanL, meanR) EXACT.

## Predictions (registered, to be scored)

- P1: controls reproduce — sc25 SUPER, sc26 NOT-SUPER, cutwA NOT-SUPER.
- P2: the carrier is active (> .05) on the k=24 base; fewer than half of the
  34 window cells are.
- P3 (my prior over branches): D3 .45, D2 .35, D1 .20.
- P4: dmA is NOT a descending neuron (pool A is 94% cord cells).

## Registered branches (read in this order)

Definitions. A = window cells (excluding the carrier) with census x_mean >
.05. F_A = number of A whose arm is SUPER. H = cells of A with
delivered_drive >= 0.5 x drive_carrier ("carrier-scale drive"); F_H likewise.
rho_all = Spearman(delivered_drive, meanR) over the active window cells
INCLUDING the carrier; rho_exc = same over excitatory active cells only
(companion, reported always).

0. **E0_controls_fail** — sc25 not SUPER, or sc26 SUPER, or cutwA SUPER:
   the contrast did not reproduce on B39. No branch claim; everything
   DESCRIPTIVE. Overrides 1–3.
1. **D1 drive-carried** — dmA SUPER AND rho_all >= +.50 AND (H empty OR
   F_H/|H| >= .5). Title consequence: "delivered drive, not removal mass".
2. **D2 identity-carried** — dmA NOT-SUPER AND sc25 SUPER AND
   F_A/|A| <= .25 (A non-empty). Identity claim stands, now with a
   distribution behind it.
3. **D3 mixed** — anything else, with the sub-label that applies:
   - D3a twin flips, scan unordered (dmA SUPER, ordering or H leg fails);
   - D3b twin does not flip, several active cells do (dmA NOT-SUPER,
     F_A/|A| > .25);
   - D3c twin INTERMEDIATE;
   - D3d sign-conditional (rho_all < .50 but rho_exc >= .50, with dmA SUPER).
   The discriminator proposed in FINDINGS must name the covariate that
   separates flippers from non-flippers in THIS table (sign, motor
   out-weight, target overlap with the carrier) and the arm that tests it.

dmC is reported beside dmA in every branch. If dmA and dmC disagree
(one SUPER, the other NOT-SUPER) the headline must say so in the same
sentence as the branch label; the branch itself is read on dmA (the brief's
rule) and is not re-labelled post hoc.

Silent-cell guard: any SUPER among cells with x_mean <= .05 is reported as
its own line (a silent cell delivers no drive; such a flip can only come
through the re-bisected gain or the batch) and counts against BOTH D1 and
D2 narratives in the write-up.

## Scope

One batch, one model class, one base (k=24), each arm at its own af-matched
gain; single-cell removals from a base that already lacks 24 DNs. "Flips" is
the right-tibia duty classifier in the chopped 0.7-Hz windows (referee N2's
unchopped panel is NOT run here). No DRAFT/numbers.json/LANE edit follows
from this stage; the findings file states what it would change.

## Compute

CPU only. Census: 1 process. Scan: 5 worker processes x 2 threads (arm-split
round-robin, cutwA in each). Outputs under `banc/l175/` only, plus one
LAB-INTENT.md line.
