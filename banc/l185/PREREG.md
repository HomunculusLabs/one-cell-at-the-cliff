# PREREG — L185: fresh-batch replication + gain-only null + signed-current twin

Registered 2026-11-21 11:58 EST, BEFORE any rollout of this card (no settle,
no bisect, no trace exists under `banc/l185/`). Owner-directed
(`BRIEF_replicate.md`); experimenter = fable session. What exists at
registration: the brief, `build_rep.py` + three block files, the generated
`rep_run.py`, `build_verdict.py` + `verdict_tail.py.txt` + `verdict_l185.py`,
`run_all.sh`, and `static.json` from `L185_MODE=static` (ZERO rollouts, no
RNG: graph tables, stored-file reads, seed-key scan). The R3 twin has NOT been
selected: its rule is frozen below and is executed after this file exists.
Nothing here was tuned on an L185 outcome. L175's stored results (one batch,
B39) are prior data and are used openly to form predictions.

## Question

L175 fired D2 (identity-carried) on ONE batch. Three ways it could be soft:
(R1) the batch (L90 rule: a single-batch class is not a class); (R1-fixed /
R2) the per-arm gain re-matching, since the scan's non-carrier meanR covaries
with the re-bisected gain (Spearman -.72); (R3) the drive twins matched
UNSIGNED pooled output, not signed current onto the right tibia.

## Machinery (inherited; nothing lineage-side edited)

`rep_run.py` (sha256 c4db9ac96902…) is a count-asserted ADDITIVE transform of
the certified L175 harness `l175/scan_run.py` (sha256 bbfea4e07ff4…, 1397
lines; builder `build_rep.py` 4bd0a445319b…, 10 rep sites). VERBATIM:
extraction, ladder, `build()/wb()/pools_for()`, `add_arm()/gen_init()`,
out-weight tables, USED / POOL_A, `settle_states`, `bisect_vec`, the rollout
step loop, store keys, per-seed atomic checkpoints. REPLACED: the seed list,
the arm block, the gains + anchors block, the tail; census mode removed.
Constants unchanged (TAU .05, DT .01, BG .02, NOISE .01, SETTLE 400, WIN 6000,
BETA 2, D .2, AF_T 0.10905611018339793). Readout: `verdict_l185.py`
(515655914e47…) = the `l150_verdict.py` helper block lines 1-71 VERBATIM
(sha 5c8323f2755f1d0c, the same slice L175 used) + `verdict_tail.py.txt`
(d10c5957be23…), written before any rollout.

## Seeds

FRESH **B40 = 3577..3592, n = 16 for EVERY arm** (next slot of the lineage's
32-step batch grid). Verified absent from all 213 npz files in the lab
(`banc/**` INCLUDING the L175 outputs, plus sibling dirs) by an
any-key-endswith scan, in-script assert re-run by every process
(`static.json`: 213 scanned, 0 unreadable). Non-sample anchor seeds, rolled
FIRST: 801, 901 (vs `l135/raw_l135.npz`) and 3545 (one stored B39 seed, vs the
L175 raws). Bisect settle anchors 11/22/33 (lineage).

## Arms (all on the k=24 = cutwA base; 19 arms + the base in every worker)

Gains are exact floats; `d%` = 100·(g/g_cutwA − 1); g_cutwA =
0.14365819573402408 (lineage stored).

| arm | graph | gain | role |
|---|---|---|---|
| `cutwA` | base (lineage plumbing VERBATIM) | 0.14365819573402408 | base; C0A anchor; in EVERY worker |
| `sc25` | wA − gi 1110 (carrier, DNp33-L) | 0.1454454553127289 (+1.244%) | R1 rematched |
| `sc26` | wA − gi 319 (mass twin) | 0.1435265743732452 (−0.092%) | R1 rematched |
| `sc27` | wA − gi 707 (boundary, 11/16 on B39) | 0.143261958360672 (−0.276%) | R1 rematched |
| `sc40` | wA − gi 559 (boundary, 11/16 on B39) | 0.14203338861465453 (−1.131%) | R1 rematched |
| `dmA` | wA − gi 511 (drive twin, any class) | 0.14381492614746094 (+0.109%) | R1 rematched |
| `dmC` | wA − gi 1480 (drive twin, carrier class) | 0.14841871619224548 (+3.314%) | R1 rematched |
| `sc25F … dmCF` | the SAME six graphs (same matrix objects) | g_cutwA | R1 fixed gain |
| `gM50, gM25, g000, gP25, gP50` | base, NO deletion | g_cutwA·(1+δ), δ = −.005, −.0025, 0, +.0025, +.005 → 0.14293990475535395, 0.14329905024468903, 0.14365819573402408, 0.14401734122335913, 0.14437648671269418 | R2 gain-only null |
| `s2t` | wA − the R3 pick | own stored-form bisect | R3 signed-current twin |

Rematched gains are the L175 stored floats (read from `l175/gains_w*.json`,
cross-checked against `results_l175.json` rows and the lineage constants).
Each worker ALSO re-runs the stored-form bisect for cutwA and its own
rematched arm and asserts the result == the stored float EXACTLY (so the gain
used is the stored float by assertion, and the bisect is re-certified in every
process before `s2t` relies on it). R2's centre `g000` is rolled as its own
arm through the generic base alias (`add_base_alias`) and must be
bit-identical to `cutwA` on every seed: that certifies the plumbing all five
R2 arms use. So "13 R1 arms" = 12 + the base, "5 R2 arms" include the centre.

Worker plan (fixed): w0 sc25, sc25F, gM50 · w1 sc26, sc26F, gM25 · w2 sc27,
sc27F, g000 · w3 sc40, sc40F, gP25 · w4 dmA, dmAF, gP50 · w5 dmC, dmCF, s2t.

## Readout and bands (inherited verbatim, no new instrument)

`duty_07` on the Ti pair per side. Per arm: kR, kL (seeds with duty >= .5), n,
meanR, meanL, Wilson 95%, paired dR vs same-seed cutwA. Bands (n=16):
**SUPER** ("flips") meanR >= .60 AND kR >= 12; **NOT-SUPER** kR <= 8 AND
meanR <= .50 (PARTIAL sub-label .35 <= meanR <= .50 AND 3 <= kR); else
**INTERMEDIATE**. "Did not flip" = not SUPER; the strict NOT-SUPER band is
reported beside it and never rounded up. Truncation (seed-outer loop, first m
seeds complete on all arms): SUPER kR >= ceil(.75m), NOT-SUPER kR <=
floor(.5m); m < 8 = no branch read.

Contrasts: fixed − rematched per cell on the SAME seeds (mean paired
difference in duty R, sd, t, n_up/n_dn at ±.20, ΔkR). Pooled B39+B40
(n = 32, scaled bands) is DESCRIPTIVE for sc27/sc40: B39 selected them as
"boundary", so B40 alone is the confirmatory read (winner's curse).

Power (n=16, as L175): a base-like arm (.297 per-seed rate) is called SUPER
with p = 2.4e-4; a carrier-like arm (.964) with p = .9998; a mid-rate arm
(.65) lands SUPER .29 / NOT-SUPER .16 / between .55 — one batch cannot
resolve a true mid-rate cell, and such arms stay INTERMEDIATE.

## R2 estimand

x = δ in units of +0.1% gain (−5, −2.5, 0, +2.5, +5). **slope** = mean over
seeds of the per-seed OLS slope of duty R on x (== OLS slope of the five arm
means); SE = sd of per-seed slopes / sqrt(m); 95% CI with t(m−1). Label:
GAIN_SENSITIVE_NEGATIVE / _POSITIVE if the CI excludes 0, else
NO_RESOLVED_SLOPE. Expected resolution: per-seed duty sd ~.15, arms
decorrelate under any gain change, so SE ~ .005 per +0.1% (CI half-width
~.010); slopes smaller than that are not resolved by this card.
"Share of the scan spread" = R² of the line (B39 base meanR + slope × arm's
re-bisect shift) against the L175 non-carrier arms' meanR, on arms with
|shift| <= .5% (the range R2 actually sweeps); the silent-cell subset and the
all-arm extrapolation are reported beside it, labelled.

## R3 selection rule (frozen here; ZERO rollouts; executed after this file)

Reading of the brief's "signed current onto right-Ti premotor, sign-aware sum
over paths of length <= 2": current delivered to the right-tibia motor pools
(the readout's own pools) directly and through one interneuron (the premotor
stage). Inputs: `l175/census_k24.npz` (x̄ = 3-seed mean rate on the k=24
base, seeds 801/901/3561) and the matrix the model steps (`Wb` of the cutwA
graph: signed log1p weights, inhibitory × BETA; rows = targets).

For pool P ∈ {f = Ti_fR (right tibia flexor), e = Ti_eR (right tibia
extensor)} and any base cell c, with g = g_cutwA:

    u_P[m]  = (1/|P|) · Σ_{t∈P} Wb[t, m]                 (pool-mean signed weight)
    a_m     = 1 if .05 < x̄_m < .95 else 0               (linear-regime gate)
    J_P(c)  = g · x̄_c · ( u_P[c]  +  g · Σ_{m≠c} u_P[m] · a_m · Wb[m, c] )

J(c) = (J_f(c), J_e(c)). The length-1 term is the exact mean synaptic current
c delivers to the pool; the length-2 term is the first-order relayed current.
The gate is needed because ~78% of base cells are silent on the census
(stored `active_frac_k24` = .2235) and a silent or rail-saturated relay passes
no current: lower bar .05 = the paper's "active" bar, upper bar .95 = the
same margin below the RMAX clamp.

- **Score**: D(c) = ‖J(c) − J(carrier)‖₂ over the (flexor, extensor)
  2-vector; reported as dist_rel = D / ‖J(carrier)‖₂. Matching the vector
  bounds the brief's scalar: |ΣJ(c) − ΣJ(carrier)| <= √2 · D.
- **Pool** ("non-window"): L175 Pool A (in the k=24 base, not ng ranks 1..58,
  not in the 78-cell prior-arm set, not motor, not DNg100 — the last two are
  machinery STOP-asserts) minus L175's own twin picks 511 and 1480 (prior
  arms with known outcomes) = 20,999 cells; AND active on the base
  (x̄ > .05): a twin for a current-delivering cell must itself deliver
  current — L175's adjudicated lesson is that a silent twin is no control.
- **Pick** = argmin D; tie-break smaller |log(drive_c / drive_carrier)|
  (L175's unsigned delivered drive), then lowest gi. Top-5 runners-up stored.
- **Degenerate case**: if ‖J(carrier)‖ == 0 exactly, the tie-break decides and
  the arm is labelled DEGENERATE. If the pick's dist_rel > .10 the arm is
  labelled PARTIAL MATCH and R3 closes the loophole only to that tolerance.
- Recorded covariates of the pick, the runners-up, the carrier, sc26, sc27,
  sc40, dmA, dmC (NOT used to select): ungated (a ≡ 1) and lower-gate-only
  versions of J and their dist_rel, the direct-only dist_rel, the scalar
  difference, unsigned drive ratio, mass ratio, class, sign; and the rank
  dmA / dmC would have had under this score.
- An independent brute-force recomputation from the global edge arrays must
  agree with the matrix form for the carrier and the pick (assert).
- Arm: `s2t` = wA − pick, 16 seeds (B40), own stored-form bisect, same
  readout. A bracket failure of that bisect = arm VOID, disclosed, no re-pick.
- Output `selection_s2.json` carries this file's sha256; workers and the
  verdict assert it, so this file cannot change after the selection.

## Certification (all must hold BEFORE any B40 value is read)

- **CERT-GEN (static)**: generic plumbing for sc25 / sc26 == the lineage's
  hand-written cutng25 / cutng25p field-for-field. PASS at registration.
- **CERT-G**: in EVERY worker the stored-form bisect returns g_cutwA ==
  0.14365819573402408 and that worker's rematched arm == its L175 stored
  float, EXACT. Fixed and grid gains == the floats in this file.
- **C0A-185a**: cutwA @801/901 bit-identical to `l135/raw_l135.npz` on 22
  trace keys + af in EVERY worker (sc25 vs stored cutng25, sc26 vs cutng25p
  in their workers). Non-zero -> that worker exits before any fresh seed; VOID.
- **C0A-185b**: cutwA + the worker's rematched arm @3545 bit-identical to the
  stored L175 raws (22 keys + af + full x_mean vector + window x_mean).
- **CERT-ALIAS**: g000 == cutwA bit-identical on every rolled seed.
- **CERT-X**: cutwA identical across the 6 workers on all 19 seeds.
- **CERT-METRIC**: the verdict helper reproduces `results_l135.json` Ti cells
  (cutwA / cutng25 / cutng25p, B26) EXACT, and reproduces the stored
  `results_l175.json` rows (base + six arms, B39: kL, kR, means, per-seed
  duty) EXACT from the L175 raws.

## Predictions (registered, to be scored)

- P1 (.90): `sc25` rematched is SUPER on B40.
- P2 (.93): `sc26`, `dmA`, `dmC` rematched and `cutwA` are all not SUPER
  (all four in the strict NOT-SUPER band: .55).
- P3 (.75): neither boundary cell promotes — `sc27` and `sc40` rematched are
  both not SUPER; I expect regression toward the null (kR 7-10 each).
- P4 (.90): `sc25F` (fixed gain) is SUPER.
- P5 (.65): fixed − rematched meanR takes the sign of the arm's re-bisect
  shift (fixed gain BELOW rematched -> higher duty): sc25 +, dmC +, sc27 −,
  sc40 −; at least 3 of 4 signs correct.
- P6 (.70): for the two small-shift arms (sc26, dmA; |shift| <= .11%)
  |fixed − rematched| < .10 in meanR.
- P7 (.85 sign; .60 interval): R2 slope is NEGATIVE; point −0.030 meanR per
  +0.1% gain, 80% interval [−0.050, −0.010] (from the L175 cross-arm slope
  among |shift| <= .5% arms, −0.030; silent cells only −0.038; a silent cell
  delivers nothing, so that covariance should be the gain's own effect).
- P8 (.80): no R2 arm is SUPER (gain alone, within ±.5%, does not "flip").
- P9 (.90): `s2t` is not SUPER — the D2 prediction (strict NOT-SUPER .60).
- Branch priors: R1 REP_D2 .62 / REP_D2_plus_boundary .20 / REP_FAIL_carrier
  .08 / REP_FAIL_twin .07 / E0 .03. Gain form GAIN_ROBUST .45 /
  NONSPECIFIC_AT_FIXED_GAIN .45 (the candidate is dmCF: fixed gain sits 3.3%
  below its rematched gain) / CARRIER_GAIN_DEPENDENT .10.

## Registered branches

**R1 (confirmatory read = rematched form, the lineage's af-matched estimand
under which D2 was registered), in this order:**
0. `E0_base_super` — cutwA SUPER: no claim, everything descriptive.
1. `REP_FAIL_carrier` — sc25 not SUPER: the flip did not replicate.
2. `REP_FAIL_twin` — sc25 SUPER but sc26 or dmA or dmC SUPER.
3. `REP_D2_plus_boundary` — carrier SUPER, twins not, but sc27 or sc40 SUPER:
   D2 replicates as "few cells", not "one cell".
4. `REP_D2` — carrier SUPER; twins, base and both boundary cells not SUPER.

**Gain form (fixed arms; a second estimand — deletion at constant coupling,
network activity free to move — reported beside R1, never relabelling it):**
`CARRIER_GAIN_DEPENDENT` (sc25F not SUPER) > `NONSPECIFIC_AT_FIXED_GAIN`
(sc25F SUPER and >= 1 other fixed arm SUPER; the headline must then say the
single-cell specificity is conditional on af-matching) > `GAIN_ROBUST`.

**R2**: the label of §R2 estimand; any SUPER gain-null arm is reported as
"gain alone flips" and counts against every single-batch flip that rests on a
re-bisected gain (the carrier's own shift is +1.24%, against the trend).

**R3**: `S2_FLIPS` (s2t SUPER: a signed-current-matched cell reproduces the
flip — D2 is challenged, title cannot say "not delivered drive") /
`S2_NO_FLIP` (strict NOT-SUPER) / `S2_UNRESOLVED` (INTERMEDIATE: needs a
second batch; not counted for or against).

**D2_hardened** = REP_D2 AND S2_NO_FLIP. Anything else is stated as what it is.

## Scope

Two batches total for the six R1 cells, one for everything new here; one
model class; one base (k=24); the chopped 0.7-Hz right-tibia classifier only.
R3 matches a linearized, time-averaged, path-length-<=2 current under one
stated gate; it does not match phase, the 1.4-Hz middle segment, or longer
paths. No DRAFT / numbers.json / LANE / existing-artifact edit follows.

## Compute and writes

CPU only, 6 worker processes × 2 threads, launched staggered; seeds are the
outer loop with an atomic raw checkpoint per seed; `results_l185.json` is
rewritten atomically by the orchestrator whenever a further seed is complete
on all arms. Writes: `banc/l185/**` and one LAB-INTENT.md §L185 append.
Deviations from the brief's letter, declared: one extra non-sample anchor seed
(3545); gains re-bisected-and-asserted rather than only loaded; `g000` rolled
as a separate certified arm; the R3 pool additionally requires an active cell
and excludes L175's twin picks.
