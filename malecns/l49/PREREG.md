# L49 PREREG — drive-gap-tolerance (written before any run)

Question (LANE.md ideas-24, verbatim intent): with bilateral antagonist structure
established under continuous 0.7-Hz entrain, how long can the drive be SWITCHED
OFF before structure collapses — and does it re-form on resume? Output: the
scheduling slack curve (max safe gap) a real gait controller budgets around.

## Design (l46–l48 machinery verbatim; no stop, no DNg88 — a gap is pure drive-off)

- Substrate: frozen l32 arm-A cord (21,516 nodes / 2,977,920 edges asserted),
  g .01 / beta 2 / D .05 on DNg100, DT 10 ms, TAU .05, SETTLE 400, seeds 11/22/33.
- Shared prefix = h40 history: entrain amp .3 @ 0.7 Hz on mech, global phase
  accumulator (settle steps phase-advance too) — bit-identical by construction to
  l48 norepair [0,4000).
- Arms (6, ONE generator, shared per-step noise tensor, per-arm AMP table — no
  inline conditionals, L39v1/L43v1/L48 lessons):
  - cont: amp .3 for the whole [0, 18000) window (premise reference).
  - gap{5,10,20,40,80}: amp .3 [0,4000); amp 0 over the gap [4000, 4000+Gst);
    amp .3 from resume [4000+Gst, 18000). Gst = 500/1000/2000/4000/8000 steps.
- Resume window = first 6000 steps (60 s) after gap end; gap<=40 s arms carry a
  continued-drive tail beyond it (reported, no new claim).
- WIN = 18000. Rollout saves mm + fL/fR/eL/eR + core to raw npz BEFORE analysis
  (L45a lesson; x88 not read by any registered metric — no stop in this design).

## Pre-registered gates

- P0 premise: cont arm duty(both S_L,S_R >= .25) over [4000,18000) >= .5 on 3/3
  seeds AND both-side medians >= .25 (continuous drive DOES hold bilateral
  structure — the state whose gap-tolerance we measure).
- C0 anchor (9th consecutive in the chain): every arm x seed
  max|mm[0:4000] - l48/traces_l48.npz mm_norepair_s[0:4000]| == 0.0 exactly, and
  all arms pairwise bit-identical over [0,4000).
- C1 drive wiring: per gap arm — AMP asserts (amp==0 across the gap span,
  ==ENT_AMP at resume start); first divergence from cont at exactly t=4000
  (no arm leakage); dm = max|mm_gap - mm_cont| over the gap span > 0 (the off
  is REAL, not floor-buried; L35 class). af op-point assert post-settle, all arms.
- C2 slack table: per gap arm x seed — end-of-gap readout = S_L/S_R medians over
  the LAST 5 s of the gap [4000+Gst-500, 4000+Gst). HELD = both >= .25; LOST
  otherwise. Also gap-half medians (G >= 1000), f_gap (rhythm2 on mm over the
  gap span, G >= 1000 only — 5-s gap is below the 0.5–10 Hz window, disclosed),
  core_gap, and t_collapse = first TS sample inside the gap where NOT both >= .25.
- C3 resume re-formation: per gap arm x seed — duty(both >= .25) over the 60-s
  resume window; both-side medians over it; lat_first AND lat_sustained (first
  TS sample t with both >= .25 continuously through [t, t+500] — L46 first-
  crossing artifact lesson). Verdict: RE-FORMS = duty >= .5 AND both medians
  >= .25 on 3/3; PARTIAL = pooled-or-majority; NOT = otherwise.
- C4 slack curve: max safe gap = largest G with C2 HELD on 3/3 seeds. Registered
  outcome classes (all accepted honestly): (i) graded — short held, long lost →
  slack number + t_collapse scale; (ii) ALL held through 80 s → slack >= 80 s,
  structure is basin-carried (L44-consistent); (iii) even 5 s LOST → slack < 5 s,
  drive-continuity is mandatory (L48 crossing-consistent); (iv) seed-split →
  table + per-seed read. Also: resume re-forms for every G (L47's 20-s claim
  checked at every gap length).

## Prediction registered (falsifiable, from priors)

L48: S_R persists while ANY amp > 0 and dies AT the amp->0 crossing; L45b: the
free cord migrates state within 60 s on 11/16 seeds; L44: >= 20 s of entrain
history builds a basin that carries the 0.7-Hz memory through a stop. Tension:
basin memory (predicts HELD through long gaps) vs free-cord migration (predicts
decay). I expect SHORT gaps (5–10 s) HELD and the 80-s gap LOST with resume
re-forming <= 20 s (L47); the crossover location is the deliverable. Any of
(i)–(iv) accepted; no post-hoc gate moves.

## ADDENDUM 1 (post-run disclosures, gates not moved)

- C1 re-operationalized: first divergence from cont is at t=HIST+1=4001,
  uniformly in 15/15 arm-seeds. The entrain drive enters the sensory
  (mech) population and the MOTOR readout lags one synaptic step; the
  registered "exactly t=4000" was an operationalization error (L44 class).
  No arm leakage (uniformity + dm>0 in-gap carry the wiring proof).
- lat_sust5: in-run code passed hold=5000 steps (50 s), not the registered
  500 (5 s) — units slip caught post-run; recomputed from the saved
  traces npz at 500 steps. Registered-gate values: 15/15 re-form,
  0.09-50.79 s. results json carries both (addendum.lat_sust5_table).
- cont f field stored the FFT ratio (1.2e5) not frequency; corrected from
  traces (0.700 3/3) with the ratio retained as f_ratio.
- P0 FAILED as registered and the failure is informative: continuous
  entrain holds both-sides duty .157/.427/.559 only (seed 33 flips S_L
  mid-window under continuous drive). The L48 spec-line premise is
  window-scoped (20-40 s), not a 140-s property. C3's PARTIAL verdicts
  are read against this ceiling, not as a gap cost.
