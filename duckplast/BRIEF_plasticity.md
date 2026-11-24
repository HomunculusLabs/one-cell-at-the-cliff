# EXPERIMENT brief — astra: duck PLASTICITY (she learns; offline first)

Owner-directed (2026-11-21 ~18:4x, evening wave). You ran her lesion
scan (ducklesion/); now the marquee: bounded Hebbian plasticity on her
real connectome — the duck that learns. OFFLINE ONLY (lab convention:
her live modules imported read-only; writes to
/home/t3rpz/critters/peabrain-lab/duckplast/).

## Design task (PREREG FIRST — behavioral predictions before any run)

1. **The plasticity rule (declare exactly):** bounded Hebbian update on
   her graph's effective weights, e.g. Δw_ij = η · x_i · x_j, clipped to
   a symmetric band around the initial weight (max ±20% drift), applied
   ONLY to a declared synapse subset — start with synapses onto/from the
   cells active in social windows (to_you/feeding interactions). State η,
   band, subset, and the consolidation schedule (update per interaction
   vs per day). NO changes to her live modules.
2. **The harness:** replay scripted interaction batteries (reuse the lab
   README's 24-conversation battery pattern: kindness/feeding/fear/apology/
   bedtime arcs, fixed gaps) through her real senses→mood→intent pipeline
   with the plastic weights, against the FROZEN control (η=0, same seeds).
3. **Pre-registered predictions (bind before running):**
   - P1: trust acquisition curve differs in SHAPE (faster early rise or
     higher asymptote) under kindness arcs vs frozen — state the band
   - P2: fear extinction after apology arcs is faster/slower — predict
   - P3: a specificity control — kindness toward the duck does NOT raise
     trust-equivalent responses to the rake/umbrella stimuli
   - P4: catastrophic-forgetting check — sleep-arc behavior and baseline
     needs unchanged within tolerance after the full battery
4. **Run, score, and report honestly** — including if plasticity does
   nothing (a null is a result: her behavior would be rule-driven, not
   synapse-driven).

## Deliverables

duckplast/{PREREG.md, harness scripts, results json, weight-drift stats,
DUCKPLAST-FINDINGS.md (≤70 lines: the four predictions vs outcomes, the
drift census, whether she learned)}, final answer ≤300 words. If results
support a live rollout, PROPOSE it (service-gate discipline) — do not
touch live anything. CPU ≤4, wall ≤2.5 h.
