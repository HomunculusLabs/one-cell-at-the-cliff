# L139 PREREG — gain-ensemble robustness of the BANC identity cliff (ideas-72, referee Q2)

Owner context: FlyHack critique (2610.13018) — silencing/lesion claims swing across
model seeds/gains. The L113-L135 cliff (ng19 KILL -> wA PARTIAL -> ng25 SUPER ->
ng29 SUPER -> cut58 KILL; carrier 1110/DNp33-L, twin 319/DNpe025-R neutral) is
measured under ONE certified gain family (per-arm bisect to AF_T on the un-jittered
graph). This run re-measures the DECISIVE arms under a jitter-ensemble of af-matched
gain families and reports the SUSTAIN FRACTION (L103 amendment) beside the pooled
cells.

## Substrate / machinery (verbatim l135_run.py unless named below)

- Arms (6): full, cutng23, cutwA, cutng25, cutng25p, cutng29.
  DROPPED from l135's 13 (spectators only, never advanced): b65, cut, cut19,
  cut58, cutng19, cutng26, cutk5 — their per-arm locals/dicts stay in the file
  verbatim; ARMS subsetting means the settle/rollout step loops never touch them.
  Arms evolve independently (drive = mm(WB[a], X[a])), so dropped arms cannot
  perturb kept-arm traces — proven by anchor A1, not assumed.
- Batch: FRESH B28 = 3201-3216 (B27 3101-3116 reserved by l137 PREREG section D /
  L141). Absence asserted across every stored raw npz in banc/ BEFORE launch.
- Sets: 6 invocations of l139_run.py argv[j], j in {0,1,2,3,4,5}.
  - j=0 (base): NO jitter, stored-form gains asserted EXACT by re-bisect
    (cutng23/wA/25/25p/29; full = G_NEW fixed, l135 form), seeds ANCH[801,901]+B28.
  - j>=1: JIT = 1 + 0.01*z, z ~ N(0,1) iid per BASE edge-table entry
    (numpy default_rng(2000+j)), applied multiplicatively to the post-log1p
    SIGNED vals inside build() (sign preserved; assert JIT.min() > 0.9).
    Same jitter array instance flows into every arm's subnet extraction (one
    base table -> per-arm emask) = per-edge multiplier identical across arms.
    ALL 6 arms freshly bisected to AF_T on the jittered graph (bracket
    [0.10, 0.20], 40 iters, settle-only, bisect-local seeds [11,22,33] verbatim).
    Seeds = B28 only (no anchor seeds; no stored twin exists by construction).
- Noise streams are seed-parameterized (generators from seed), independent of W:
  same B28 seed = same noise draw in every set = PAIRED cross-set reads by design.
- Metrics VERBATIM l135_verdict.py (duty_seeds/side_k atoms, same rounding path):
  duty = mean over TS=499..5990 step 10 of (S >= .25) within 0.7-Hz segment
  windows post-MEAS0=500; kR = count of 16 seeds with Ti_R duty >= .5; meanR =
  mean duty; paired dR = per-seed duty(arm) - duty(full) same set, mean.

## Certification (ALL must pass BEFORE any B28/jitter number is read)

- C0B-135 (L85 rule): this verdict machinery re-derives l135's stored B26 Ti
  per-side table for the 6 shared arms from raw_l135.npz and asserts EXACT
  equality against results_l135.json (kL/kR/meanL/meanR to the stored rounding).
- A1 (C0A-135, runs inside set 0): for the 6 arms x seeds {801,901} x keys
  {mm, xm, Ti_fL/eL/fR/eR, Tr_fL/eL/fR/eR} vs raw_l135.npz: max |d| == 0.0
  (bit-identity of the ARMS-subset transform; L45b paired-arm class).
- A2: set-0 stored-gain re-bisects land EXACT (asserts in-run).
- A3: per-set jitter stats logged (n, mean ~1, std ~0.01, min > 0.9).
- A4: per-arm |af_final - AF_T| disclosed UNROUNDED; assert < 2e-3 (staircase,
  L107 note: discrete-cell settle makes af(g) a staircase; l135 stairs ~5e-4).
- A5: rollout af sanity 0.01 < af < 0.9 every arm every set (lineage form).

## Registered classes (VERBATIM lineage criteria; m0j = set-j full meanR)

- KILL:  meanR <= m0j - .10 AND kR <= 4 AND mean paired dR <= -.20   (l117 form)
- SUPER: meanR >= .60 AND kR >= 12                                    (lineage form)
- PARTIAL: meanR in [.35,.50] AND kR in 3..8                          (L124 band)
- NEUTRAL-INT: none of K/S/P AND |mean paired dR| < .10               (25p form;
  l133/l135 paired dR -.017/-.038)

## Registered arm -> class priors + sustain read

- ng23 -> KILL (pooled 0/48+); wA -> PARTIAL (20/64, 6 batches); ng25 -> SUPER
  (47/48); ng25p -> NEUTRAL-INT (12/32 pooled contains .5); ng29 -> SUPER
  (170/176); full = reference, NO class (base Ti_R is a noisy distribution,
  L90 law — reported per set as context, never a point).
- SUSTAIN(arm) = # of sets j in 1..5 landing the registered class.
  GATE: sustain >= 4/5 = gain-robust claim; < 4/5 = boundary disclosed AS THE
  RESULT (both outcomes publishable; no re-roll).
- Secondary (descriptive, no gate): per-seed paired flips — for each seed, count
  of sets where duty>=.5 membership differs from set 0 (per arm); full's kR
  range across sets = the batch-noise context line.

## Registered predictions (both directions scored)

- P1: ng25 SUPER sustains >= 4/5 (mechanism: single-cell identity carrier with
  3/48 pooled failures; a 1% weight jitter should not move a kR>=12/16 margin
  built by one cell). Counter-direction read: if ng25 drops below 4/5, the
  carrier claim is GAIN-FRAGILE and the L140 limitation section must say so.
- P2 (OPEN both ways): ng23 KILL under jitter. Robust-side argument: pooled
  0/48. Fragile-side argument: the kill is an attractor-selection effect and
  in-degree renormalization shifts under jitter (each arm's row-normalization
  is over its OWN subnet — jitter changes relative row masses).
- P3: full kR across 6 sets stays inside the historical base spread (2-10/16,
  L90); if it EXITS that range in any set, that set's class reads carry a
  base-regime caveat line (disclosed, not re-rolled).
- P4: 25p NEUTRAL-INT is the most likely fragile class (its pooled Wilson
  contains .5 by a hair) — registered BEFORE reading; a 25p class-flip is a
  finding, not a failure.

## Slice rule (registered)

One argv invocation per set, checkpoint npz per set (raw_l139_j{j}.npz +
anchors_j{j}.json + partial_j{j}.npz resume). If wall time exceeds ~50 min,
remaining sets run at the NEXT tick; the verdict runs only when all 6 exist.
Single batch per set (16 seeds) DISCLOSED: sustain is over SETS, not seeds;
L88/L90 batch-swing caveat printed beside any verdict <= 4/5.

## Outputs

l139/raw_l139_j{0..5}.npz, l139/anchors_j{0..5}.json, l139/run_j{j}.out,
l139_verdict.py -> l139/results_l139.json (per-set table + sustain fractions +
cert blocks). No live changes.
