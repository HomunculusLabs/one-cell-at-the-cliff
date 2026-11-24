# EXPERIMENT brief — duck wave-6: the routing-threshold lever (fable, offline)

Owner-directed (2026-11-21 ~21:5x, burn window). v1: synapses drift,
choices don't. v2: scores move (+.10 vigor, 12 mood-tag flips), choices
still don't — the thresholds sit in a dead zone. Wave 6 tests the
diagnosed lever: THRESHOLD PLACEMENT. OFFLINE ONLY (live modules
read-only; writes to duckroute/).

## Design (PREREG Q1-Q4 FIRST)

1. **Map the boundaries:** for every intent decision boundary in
   bridge.py's routing, measure the frozen distribution of its driving
   score across the 24-arc battery (where do real scores sit relative to
   thresholds? — the v2 dead-zone map, completed for ALL boundaries).
2. **Three placement regimes (declared, not tuned per-outcome):**
   (a) AS-IS control; (b) **percentile placement** — every threshold at
   the 70th percentile of its own frozen score distribution (a
   principled, outcome-blind rule); (c) **adaptive margins** — threshold
   minus a small hysteresis proportional to accumulated plastic drift
   (the "mood can matter" regime). Apply the SAME plasticity v2 used.
3. **Registered predictions:** Q1 regime (b) produces ≥10 near-threshold
   decision flips vs ~0 in (a) — the flips v2's mood shifts were denied;
   Q2 the flips concentrate on kindness/feeding arcs (specificity);
   Q3 no pathological oscillation (flip-flop rate < 1 per 8 turns);
   Q4 settle/sleep behavior unchanged.
4. Also log: the picked_up neutral→curious tag under each regime (does
   it become a visible behavior difference?).

## Deliverables

duckroute/{PREREG.md, harness, results, DUCKROUTE-FINDINGS.md (≤70
lines: the boundary map, the three regimes, Q1-Q4 verdicts, and — if Q1
holds — the live-rollout PROPOSAL with the service-gate plan)}. CPU ≤4.
Wall ≤2.5 h. Final ≤250 words.
