# LAB-DIFFDUCK — differential-duck-v1 (L1)

Distilling the production rules engine into the connectome's own parameters:
can the duck's per-class gains and mood readout be LEARNED instead of hand-set?

Code: `diffduck.py` (modes check | data | train | eval). Live modules imported
read-only; nothing in `~/critters/peabrain` or `~/critters/puddle` is modified.

## Setup

- **Teacher** = production physics + hand-tuned readout: the real `FlyBrain`
  (scalar gain 0.95/rho) stepped exactly like `MoodState.observe()` (idle gap
  observe, then 2 s event window, peak-hold mood integrators, trust/hunger/
  sleep body rules, `mood_tag()` cascade), run batched over sequences.
- **Student** = same connectome, same step equation, but:
  - per-cell-class gain multiplier `g0 * exp(u_c)` (58 classes -> 58 params)
  - per-cell-class threshold `softplus(v_c)` (58 params)
  - linear mood readout, 10 features -> fear/food_joy/salience targets
    (features: lc, dan, kc, cx, oct, ser, dop population means, active_frac,
    lc x looming, oct x looming — the bridge-side event gate production uses)
  - total free params: ~146. Body semantics (trust/hunger/sleep, the
    water/shiny/hold floors) are bridge-side in production and shared, not
    learned — the student only has to earn the NEURAL axes; tags are then
    computed end-to-end through the real `mood_tag()` with teacher body state.
- **Training**: Adam (lr .04 cosine, grad-clip 1.0), MSE on the three neural
  axes per turn + criticality regularizer `0.05 * |rho_eff - 0.99|`, gradients
  through the 20-step stimulus rollout + the last 20 gap steps (40 rate-dyn
  steps, gradient-checkpointed, deterministic zero-noise grad window),
  per-turn truncated BPTT. 200 train seqs (batch 40), 20 val seqs (model
  selection on val tag agreement), 60 held-out seqs never seen.

## Dataset

220 train + 60 held-out sequences (8-14 turns; events drawn from the 14
production events weighted toward kindness; gaps 2/4/6 s + one long idle
300/900 s at a random turn; trust0 U[.1,.9], hunger0 U[.1,.7]; forced noon
so no circadian tonic). Held-out teacher tag distribution (840 labels):
scared:high 314, happy:high 170, scared:low 112, happy:low 97, curious:low 63,
hungry:high 29, angry:high 22, neutral:low 12, hungry:low 11, angry:low 10.

## Teacher faithfulness (batched vs production, gate for everything below)

Two fixed 6-turn sequences run through the REAL `MoodState` (serial, forced
noon) vs the batched teacher: **max axis |diff| = 0.0070, mood tags 12/12**.
(The two noise streams differ; 0.007 is the noise floor.)

## Approximations (documented, checked above)

- Inter-event relaxation: 2 s exact dt=0.01, then dt=0.05 coarse Euler, capped
  at 12 s of simulated decay (X reaches its background attractor in ~3 s;
  longer-gap memory is carried analytically by the mood hold, exactly like
  production). Training relaxes coarse-only, capped 4 s.
- The 40-step grad window runs with zero noise (recompute-safe checkpointing);
  teacher/eval keep production noise.

## Results (run 1, 2026-11-09) — CAVEAT, see run 2

- **Held-out exact tag agreement: 56.8%** (family 58.8%) — BELOW the 80%
  gate. L1 stayed open.
- **POST-MORTEM (found in tick 2): run 1's training targets were
  misaligned.** `train()` drew each batch through a permutation
  (`chunk = seqs[order[b0:b0+bs]]`) but indexed teacher targets by batch
  offset (`teacher_rec[t][b0+i]`), not by the permuted id — verified
  numerically: with run-1's seeds, input/target pairs coincided on
  0-2 of 200 sequences per epoch. The student was distilled against
  ANOTHER sequence's mood targets ~99% of turns; its training loss
  plateau (~.119) was cross-sequence variance, not a learning limit, and
  the saved model ≈ its warm-start readout. Run-1's *evaluations* were
  honest (aligned, cached traces); its *diagnosis* ("MSE under-serves
  the tag cascade") was incomplete — the signal itself was scrambled.
  The gain-placement/readout-structure observations below stand as
  descriptions of that (barely-trained) model.
- Val-tag curve (best kept): ep0 43.2% (loss .1345), then 38.6 / 38.6 /
  41.1 / 38.6 / 39.6 — loss plateaus ~.119 while tags oscillate: the
  MSE-on-axes objective improves regression but flips threshold-cascade
  tags. This is THE finding of run 1: distilling moods by axis-MSE
  under-serves the tag metric; the loss needs tag-margin awareness.
- Per-axis MAE (held-out): fear 0.124, food_joy 0.197, salience 0.127 —
  joy is the weakest axis (serotonin/DAN blend hardest to hit).

## Where the learned gain lands (the interesting part)

- **rho_eff(learned gains) = 0.9956** — essentially AT the criticality
  regularizer's 0.99 target, vs the hand-set operating point 0.95/rho.
  Asked to match the rules engine while staying near criticality, the
  optimizer moves her brain slightly UP toward criticality, not away.
- Spontaneous active fraction at learned gains: 7.8% (production: ~15.5%
  at 0.95/rho) — a sparser, still-healthy operating point.
- Per-class gain multipliers stay narrow: [0.959, 1.049]. Up: visual
  (+4.9%), ALLN, mechanosensory (+4.0%), ALIN, mAL, MBIN. Down:
  olfactory (-4.1%), gustatory, descending, Kenyon_Cell, DAN (-3.2%).
- **The learned readout recovers the hand formulas' structure:**
  fear <- lc x looming (0.96) + octopamine (1.33); joy <- serotonin
  (1.40) + DAN (1.21); salience <- dopamine (2.72). Cross-terms are
  small (dan->fear .21, kc->joy -.51, af negative on joy/sal: overall
  activity suppresses positive readouts). The looming gate and the
  oct-amplifier are things the linear readout CHOSE, not priors — they
  were only init'd at 0.8x and training moved them (fear oct 1.33 vs
  init 1.2, lc*loom 0.96 vs init 0.96 held, joy ser 1.40 vs init 2.0,
  dan 1.21 vs 1.6 — training rebalanced toward dan).
- Verdict for the wiring question: with gains confined near 1.0 by the
  criticality regularizer, the mood chemistry is carried by the READOUT
  (consistent with NULL-DUCK's "mood = bulk-path" verdict); the learnable
  substrate for structure remains the KC/DAN side (L9/L1b territory).

## Results (run 2 = L1b, 2026-11-09, diffduck15.py) — GATE PASSED

Three changes: (1) **alignment fix** (targets indexed by permuted ids),
(2) **tag-margin band hinge** at the cascade thresholds (fear .25/.5,
joy .35/.6, sal .15; conditional sal .3 / fear .08 on the angry branches;
margin ±0.05, weight 2.0 on mean hinge), (3) **edge-jitter ensemble**:
every 4th batch runs on a 1%-weight-noise CSR copy of W (3 copies,
rotate). Warm start from run 1, 4 epochs, lr .02 cosine, model selection
on val tag agreement (unchanged protocol: 20 held-back train seqs;
60-seq held-out never used for selection).

- **Held-out exact 97.3%** (817/840; family 99.5%) — gate was ≥80%.
  Same eval harness, same teacher traces, same held-out set as run 1
  (warm-start re-eval reproduced 56.8% exactly before training).
- Val-tag: ep0 83.6%, ep1 **96.4%** (kept), ep2 92.9%, ep3 92.5%.
  One epoch of ALIGNED distillation already clears the gate — the
  alignment fix, not the hinge, is the dominant lever; the hinge
  polishes the high/low splits (residual confusions are almost all
  happy:high→happy:low, 19/840 — joy still the weakest axis).
- Per-axis MAE (held-out): fear .011, joy .059, sal .049 (run 1:
  .124/.197/.127) — joy error cut 3.3x.
- **Jitter-transfer (fresh seeds, never trained on): 97.3-97.4%.**
  1% iid edge-weight noise is a no-op at the population-mean readout —
  replicates the flyvis finding (per-class gains repair small
  perturbations); structure-level rewiring (L9) is the real test.
- rho_eff(learned) = 0.9704 (run 1: 0.9956, hand: 0.95/rho) — still
  near-critical, a notch further from 0.99 with the hinge pushing axes.
- Artifacts: diffduck15/{diffduck15.pt, trainlog.json, eval.json}.

## Next

- L9 (null-critic followup): the jitter/eval infra now lives in
  diffduck15 (jitter_W + eval15) — degree-preserving rewiring is the
  comparison that matters; iid noise was always going to wash out.


## Notes / gotchas paid for

- Summing per-turn losses and backprop once retains EVERY turn's rollout
  graph (~1.2 GB x 14 turns -> OOM). Per-turn backward with detached mood
  axes (truncated BPTT) is exactly equivalent and holds one turn of graph.
- Shared parameter subgraphs (gain/threshold vectors computed once outside
  the turn loop) are freed by the first turn's backward — recompute per turn.
- numpy `Generator` has `.integers`, not `.randint`/`.choices`.

## L9a appendix — frozen learned student × rewiring ensemble (2026-11-10)

Design = R2 amendments a/b/c: 5 Maslov-Sneppen draws (all edges) + 5
boundary-preserving draws (the 291,601 sensory-SOURCE edges of 15.09M
frozen, interior rewired only; signs travel with sources), SAME frozen
diffduck15 weights for every arm, op-point bisected (scalar α on the
learned gain; target = real spontaneous af 0.0660). Real reference
re-run in-pipeline: exact 97.3% / family 99.5% — reproduces eval.json.

Arm validation (direct sensory-output edge share): real {DAN .0084, KC
.0000, desc .0834}; MS {DAN .0434 = ×5.2, KC .0266 from zero, desc
.0221 = ×0.27} — replicates r2_boundary_check; BP identical to real by
construction. α = 1.078 and af .059-.066 on every draw (learned gain
transfers at the same scale on all rewires).

| arm      | exact        | family | mae f/j/s      | peas→KC      | peas→DAN    | swat→dop    | greet→ser   |
|----------|--------------|--------|----------------|--------------|-------------|-------------|-------------|
| REAL     | 97.3         | 99.5   | .011/.059/.049 | .0413        | .0186       | .1794       | .0313       |
| MS  ×5   | 96.71 ± .07  | 98.98  | .029/.054/.049 | .0106 (×.26) | .0109 (×.59)| .1794 (×1.00)| .0373 (×1.19)|
| BP  ×5   | 97.74 ± .00  | 99.29  | .016/.061/.057 | .0036 (×.09) | .0039 (×.21)| .1744 (×.97)| .0399 (×1.27)|

Findings — claims scoped to "this wiring (v783), this rate-model
fidelity" (10-draw ensemble, spread reported; BP draws differ as graphs
— nnz and 4th-decimal fingerprints vary — but population-mean readouts
converge):

1. The LEARNED mood-tag surface is bulk-path: full rewiring costs only
   −0.6 pts exact (97.3 → 96.7). Distillation did not make the tags
   structure-dependent; the hand-set NULL-DUCK mood verdict replicates
   under the student, the ensemble, and the matched op point.
2. The memory circuit is INTERIOR-wiring-load-bearing, and the standard
   MS null UNDERSTATES the collapse: peas→KC ×.26 under MS but ×.09
   under BP — MS's fake sensory→KC shortcuts (0 → 2.7% direct share)
   partially compensate for the scrambled interior path. Hand-set
   historical anchor x0.21 ≈ MS-learned ×.26.
3. The BP null EXCEEDS real wiring on tag agreement (97.7 vs 97.3):
   with the sensory→readout boundary intact, interior scrambling
   contributes ≈ nothing to the mood surface. At this fidelity the mood
   surface is boundary-defined, not wiring-defined.
4. Consequence for L6/L7: learned systems (DAN-critic, DN readout
   heads) belong on the KC/DAN pathway — the one place structure does
   measurable work (peas→DAN ×.21-.59 across arms). Mood tags are a
   fine UI signal but are not evidence about wiring.

Slice b (open): train a FRESH student ON each null graph through the
same distillation pipeline — does learning RECOVER specificity on a
scrambled brain? (flyvis-replication proper; 2610.29205 predicts no —
the number is the deliverable.)

Artifacts: l9/l9a_results.json (all 10 draws + real, fingerprints
included), l9_null_ensemble.py, l9/run.log (2,713 s total).

## L9b appendix — fresh student TRAINED ON the nulls (2026-11-10, tick 20)

flyvis replication proper (2610.10014 control; 2610.29205 prediction tested).
Design: same warm start as the real student (diffduck.pt — amendment c),
same distillation hyperparams as train15 (tag hinge, 1%-jitter ensemble of
the NULL graph, criticality reg on the null W, bs 40, Adam groups, 2
epochs — real run's val curve had converged by ep1: 83.6→96.4), draw 0 of
each arm with rng seeds IDENTICAL to slice a (graphs paired across slices).
Teacher traces are wiring-independent (rules engine), so the null students
distill the exact same targets. No α bisect — the student learns its own
gain; op points recorded post-hoc. ~32 min wall for both arms in parallel
(GPU shared with the live duck, read-only).

| arm | val | held on OWN null | frozen (slice a) | xfer→real W | af | rho_own | peas→KC | peas→DAN | swat→dop | greet→ser |
|-----|-----|------------------|------------------|-------------|----|---------|---------|----------|----------|-----------|
| REAL (ref) | 96.4 | 97.3 / 99.5 | — | — | .066 | .970 | .0413 | .0186 | .1794 | .0313 |
| MS0 fresh | 91.8 | 94.6 / 99.0 | 96.7 | 95.7 / 99.3 | .027 | .509 | .0090 (×.22) | .0095 (×.51) | .1797 (×1.00) | .0340 (×1.09) |
| BP0 fresh | 96.4 | 98.3 / 99.3 | 97.7 | 93.9 / 98.9 | .031 | .982 | .0031 (×.08) | .0034 (×.18) | .1744 (×.97) | .0365 (×1.17) |

Verdicts (claims scoped to this wiring v783, this rate-model fidelity):

1. LEARNING DOES NOT RECOVER WIRING-SPECIFICITY — 2610.29205 confirmed.
   Fresh training ON the null leaves peas→KC collapsed (×.22 MS / ×.08 BP,
   vs frozen ×.25 / ×.09 — no recovery, within draw noise slightly worse)
   and peas→DAN degraded (×.51 / ×.18). No per-class gain or readout can
   rebuild a pathway the rewired interior no longer contains.
2. The mood-tag surface is bulk-path FROM THE TRAINING SIDE: a student
   trained on the boundary-preserving null beats the real-wiring student
   on its own null (98.3 vs 97.3), and null-trained readouts transfer to
   real wiring (95.7 / 93.9). The mood surface rides chemistry + boundary,
   not interior wiring — both directions now.
3. Channel split is clean, not global: swat→dopamine ×1.00/×.97 and
   greet→serotonin ×1.09/×1.17 fully recover while KC/DAN stay collapsed.
4. Op-point honesty: fresh students settled hypo-active (af .027/.031 vs
   real .066; MS rho_own .509 — its gain found a quieter basin, BP .982).
   Saturation compresses deltas; a quieter baseline if anything inflates
   them, so the collapse is not an op-point artifact in the compressing
   direction.
5. Slice a vs b agree on the memory channel (frozen ≈ fresh ratios), so
   the frozen monitor was adequate HERE — but per 2611.06940 frozen
   monitors under-detect in general; the fresh-trained numbers are the
   claim-carriers. Slice b is 1 paired draw/arm; the 5-draw ensemble
   requirement is carried by slice a (spread there was ±.07 / ±.00).

Consequence for the roadmap: L6 (DAN-critic) and L7 (DN readout) sit on
KC/DAN/descending — the only channels where structure does work that
neither rewiring nor retraining can fake. Mood tags: fine UI signal, not
evidence about wiring (now proven from both the frozen and trained sides).

Artifacts: l9/l9b_{MS,BP}.{json,pt,log}, l9b_fresh_student.py,
l9/{MS0,BP0}.out. L9 CLOSED (a: ensemble + b: fresh-trained replication).
