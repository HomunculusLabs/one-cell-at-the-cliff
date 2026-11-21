# PREREG — L197b: gate-jitter v2, the discriminator with POWER

Registered 2026-11-21 ~19:00 EST, BEFORE any v2 rollout (no settle, no bisect,
no trace exists under `banc/l197b/`). Owner-directed (`banc/l198/BRIEF_relaytwin.md`,
second job of the chain; runs only after L198 is FINAL). Implements the lane's
L197 card. Experimenter = Miso session (claude-fable-5-2).

What exists at registration: this text; `gj.py` (shared readout); `pilot.py` +
`pilot.json` (ZERO rollouts, stored v1 data only); `schedule.py` +
`schedule.json` (every gate schedule drawn, zero rollouts); `build_v2.py` →
`run_v2.py`; `analyze_v2.py`; `run_all.sh`.

## Question (unchanged from L186)

The carrier-removal (sc25 − cutwA) rise in cross-seed right-tibia antagonist
duty lives in SHARED timing. Is that timing locked to the displaced external
gate (aligned clock) or to elapsed time (elapsed clock)? v1 (L186) came out
E3 with D = −.015 [−.156, +.126]: an interval too wide to resolve a ±.10
difference, from a readout whose two clocks shared 62% of their samples.

## What was looked at before registering (disclosed; all zero-rollout)

1. **CERT-V1.** `gj.analyse` with v1's parameters reproduces
   `l186/results_l186.json` to 1e-12 (A / T / D values and intervals, six
   means, four ordered-pair matrices).
2. **Pilot on v1's 16 stored seeds** (old data, already adjudicated; used for
   the power analysis the brief asks for, and it informs my predictions):
   short window W = 150 → A +.083, T +.135, D −.052, jackknife SE(D) .0435.
3. **A v1-data observation I did not expect, which changes what the fresh
   batch should be asked.** Split by each pair-SEGMENT's own tone rotation,
   v1's aligned elevation is +.579 [+.445, +.713] for in-phase pair-segments
   and −.068 [−.208, +.072] for antiphase ones (difference +.647 [+.435,
   +.859]); at W = 150, +.303 vs −.163. Tick 216's tone instrument read
   "not predictive" (rho +.148 / −.110) because it averaged the two outer
   segments' INDEPENDENT lags into one pair-level rotation. This is post hoc
   on seen data — it is registered below as a prediction for the fresh batch,
   not claimed.

## Design: two registered design arms (the card's option iii)

Both graph arms (cutwA base, sc25 = carrier removed) see the SAME schedule per
seed; gains = the stored-form bisects, which must equal the stored floats.
Per seed and outer (0.7-Hz) segment ONE pulse is displaced; boundary pulses
[0,500) and [1800,2000) and the 1.4-Hz middle segment are untouched; the tone
runs on elapsed time exactly as before (the jitter moves the gate, it does not
reset the tone). Onsets: independent integers, PCG64
`SeedSequence([197, arm code, seed])`, first then last outer segment.

| | **S — short window** (card ii) | **W — wide jitter** (card i, AMENDED) |
|---|---|---|
| pulse | 500 steps (v1's) | **250 steps** |
| onset | 900 ± 300 → U{600..1200} (v1's law) | U{525..1525} (band 1000) |
| on-steps per outer segment | 1200 (v1's) | 950 |
| correlation window | **150 steps** (≈ one 0.7-Hz period) | 250 steps |
| window starts rel. to the flexor seed's onset | −75..+425 step 10 (51) | −125..+125 step 10 (26) |
| seeds | 19001..19096 | 19201..19296 |

Window-start rule in both arms = v1's: at least half of every window lies
inside the displaced pulse; no window leaves its 2000-step segment.

**Amendment to the card, and why.** The card's (i) asks for "jitter ≥ 1000
steps" with the 500-step window and says "REFUSE to roll if mean overlap
exceeds .25". Those two conflict: with a 500-step window a 1000-step band
gives mean overlap .417 (W/2J − W²/12J²), and passing .25 needs a band of
≥ 1824 steps, which cannot fit a 500-step pulse inside a 2000-step segment
(1300 steps free between the boundary pulses). The card names the two ways
out ("widen the outer segment or shorten the pulse, and disclose which"):
I SHORTEN THE PULSE to 250 steps and the window with it, keeping the card's
1000-step band. Widening the segment would change WIN and with it every
stored-trace anchor. Costs, disclosed: 950 instead of 1200 on-steps per outer
segment, pulses as close as 25 steps to a boundary pulse (v1: 100), and a
pulse of 1.75 tone periods — so arm W also tests whether the elevation
survives a shorter pulse at all.

**Overlap gate (card's verify, computed from the DRAWN schedule, before
freeze):** S mean overlap **.2277**, W **.2302** (≤ .25 both; 56% of
pair-segments fully disjoint in each; median |lag| 174 / 289 steps).
`run_v2.py` asserts the stored gate flag and re-derives every seed's onsets.

## Power analysis (the brief's requirement)

Unit of inference = the seed (delete-one-seed jackknife over the ordered-pair
matrix, v1's estimator; pairs are not independent observations). Effect
scale: v1's elevation +.275; the quantity to resolve is an aligned − elapsed
difference of .10 (v1's registered E1/E2 margin).

| SE(D) source, n = 16 | SE | n for 80% | n for 90% | n for 95% power (two-sided .05, δ = .10) |
|---|---|---|---|---|
| v1 as run (W = 500) | .0720 | 66 | 88 | 108 |
| pilot W = 150 on v1 seeds | .0435 | 24 | 32 | 40 |
| pilot W = 250 on v1 seeds | .0499 | 32 | 42 | 52 |

n ∝ SE² (jackknife SE ∝ 1/√n). Arm W has no pilot (new schedule), so I size
BOTH arms to the most conservative row: **n = 96 seeds per design arm** (≥ 88;
6 workers × 16). Expected SE(D) at n = 96: .018 (S, pilot row) to .029
(v1 row) → 95% half-width .035–.058, power for δ = .10 ≥ .92 in the worst
row. v1's n = 16 had power .28 for the same δ. If a realised half-width
still exceeds .10 the arm is labelled UNDERPOWERED_AGAIN and no clock branch
is read.

Feasibility: 192 fresh seeds × 2 graph arms + 12 anchor rollouts ≈ 12 s per
seed-pair → ~10 min on 6 workers × 2 threads. No amendment needed for CPU.

## Readout (v1's metric, generalised only in window length; `gj.py`)

For ordered distinct seed pair (i, j), segment, start offset: Pearson r
between flexor seed i's window (at its own onset + offset) and extensor seed
j's window — ALIGNED: at j's own onset + the same offset; ELAPSED: at the same
absolute steps as the flexor window. Hit = r ≤ −.25 with both SDs > 1e-6.
Duty = mean hit, equal weight over offsets, segments, ordered pairs.
**A** = aligned duty sc25 − cutwA; **T** = elapsed; **D = A − T**; normal 95%
intervals from the delete-one-seed jackknife (v1 form).

## Registered branches — primary, per design arm

Read only if all certs pass, the overlap gate passed and all 96 seeds exist.
- flag `R0_no_elevation`: A < .15 AND T < .15 — the deletion elevation is not
  carried by this readout at this resolution; the clock label is then
  DESCRIPTIVE. (For S this is the card's own side question: does the duty
  readout survive at single-period resolution?)
- **E1_external** — D ≥ +.10 and CI(D) excludes 0 above (v1's rule).
- **E2_elapsed** — D ≤ −.10 and CI(D) excludes 0 below (v1's rule; a
  candidate internal rhythm ONLY — see the mechanism panel).
- **E3_equal_resolved** — CI(D) lies inside (−.10, +.10): neither clock is
  preferred, now as a POWERED null (v1 could not reach this label).
- **E3_unresolved** — anything else (+ UNDERPOWERED_AGAIN if half-width > .10).

**v2 verdict (joint):** `E1` / `E2` / `E3_EQUAL_POWERED` if both design arms
agree (an R0 arm does not vote); otherwise `ARM_DEPENDENT`, each arm stated.

## Registered mechanism panel — secondary, thresholds fixed now

D alone cannot separate three sources of shared timing, because the tone
phase runs on elapsed time while a seed's gate is on. Per design arm:
- **T_on / T_off**: the elapsed contrast restricted to windows where seed j's
  own gate is ON for ≥ half the window / OFF (ratio of sums over ordered
  pairs, jackknifed).
- **A_inphase / A_antiphase**: the aligned contrast restricted to
  pair-segments whose relative tone rotation |((lag/142.857) mod 1) − .5|·2
  is ≥ .75 / ≤ .25 (each ≈ 25% of pair-segments by the drawn schedule).
- Label: `M_internal` if T_off ≥ .15 with CI above 0 (a rhythm that persists
  on elapsed time while the partner is undriven); else `M_tone` if
  A_inphase − A_antiphase ≥ .15 with CI above 0 and A_antiphase < .15 (the
  shared timing is carried by the external tone's phase, present only while
  driven); else `M_gate` if A_inphase ≥ .15 and A_antiphase ≥ .15, both with
  CI above 0 (carried by the gate edge whatever the tone phase); else
  `M_unassigned`.
- **Tone control, the card's instrument VERBATIM** (pair-level rho between
  the rotation of the pair's mean lag and aligned − elapsed pair duty; v1
  +.148 sc25 / −.110 cutwA; "not predictive" = |rho| < .25 in both graph
  arms), reported beside the segment-level rho (same statistic, each
  pair-segment's own lag).

## Certification

- **C0A (mandatory, every worker):** unjittered cutwA and sc25 @801/901
  bit-identical to `l135/raw_l135.npz` on 22 traces + af (92 checks per
  worker), before any fresh seed. Non-zero = that worker VOID.
- **Gains:** stored-form bisect == the lineage pin g_cutwA
  0.14365819573402408 and the stored sc25 0.1454454553127289, EXACT.
- **Schedule:** every stored gate array == the registered schedule; on-steps
  per segment [700 + pulse, 2000, 700 + pulse]; anchors unjittered.
- **Fresh seeds:** 19001..19096, 19201..19296 — no numeric token of any
  member name in any of the lab's 254 npz equals a fresh seed (scan before
  freeze; re-asserted in-script).
- **CERT-V1:** `gj.analyse` reproduces v1 (see above), re-run by the analysis.
- Same canonical torch noise mapped across the two graphs (v1 form).

## Predictions (registered, to be scored)

- P1 (.85): certs, gains and gate pass; all 192 seeds complete.
- P2: arm S — `R0_no_elevation` flag set (.55; pilot A .083 / T .135);
  clock class `E3_equal_resolved` (.65), D between −.10 and 0 (.60).
- P3: arm W — the aligned elevation survives the 250-step pulse, A ≥ .10
  (.55); clock class E3_equal_resolved .40 / E1 .30 / unresolved .25 / E2
  .05; D > 0 (.65), because with 56% disjoint pulses the elapsed view mostly
  sees an undriven partner.
- P4 (.80): mechanism label `M_tone` in BOTH design arms (A_inphase −
  A_antiphase ≥ .15, CI above 0).
- P5 (.85): no `M_internal` in either arm (T_off CI below .15).
- P6 (.70): the card's verbatim pair-level instrument again reads |rho| < .25
  in both graph arms of arm S, while the segment-level rho(rotation, aligned
  duty) for sc25 exceeds +.25 — i.e. the instrument, not the biology, cleared
  the tone in v1.
- P7 (.75): half-width of CI(D) ≤ .06 in both arms.

## Scope

One batch per design arm; one model class; the movable pulse of the 0.7-Hz
segments at graph-specific AF-matched gains; cross-seed duty, not whole-
segment duty. "Elapsed" confounds the external tone with any internal clock;
only T_off speaks to an internal rhythm. Arm W changes pulse length and
on-time, so S and W are two designs, not replicates. No DRAFT / numbers.json /
LANE edit follows; FINDINGS states what it would change.

## Compute and writes

CPU only, 6 workers × 2 threads (the chain's cap; launched only after L198's
workers are gone), per-seed atomic checkpoints. Writes: `banc/l197b/**` and
one LAB-INTENT.md §L197b append.
