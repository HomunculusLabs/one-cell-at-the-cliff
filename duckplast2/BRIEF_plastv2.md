# EXPERIMENT brief — duck wave-5: plasticity v2, aimed at the routing layer (fable, anthropic-pinned)

Owner-directed (2026-11-21 ~20:2x). v1 diagnosis: synapses drift, choices
don't — the bottleneck is the route-driven intent layer. v2 aims
plasticity where decisions are made. OFFLINE ONLY (her live modules
read-only; writes to /home/t3rpz/critters/peabrain-lab/duckplast2/).

## Design (PREREG the predictions FIRST)

1. **Aim the plasticity:** instead of blanket social-window synapses,
   update only synapses onto the cells that feed intent selection — the
   mood-axis readout cells and any threshold-comparator inputs you can
   identify from her routing code (bridge.py intent thresholds). Declare
   the exact cell set + rule + band (≤20% drift) before running.
2. **Finer readout:** log continuous intent scores (not argmax) per turn —
   the pre-registered metrics are SHIFTS in intent-score distributions,
   not only decision flips. Also register: decision flips at
   near-threshold turns (the turns where frozen scores sit within ±.05 of
   a boundary — the flips that are cheaply available).
3. **Multi-day consolidation:** apply the battery, then simulate her
   world-tick cadence (45s ticks, 24h compressed with sleep phases)
   BETWEEN interaction sessions ×3 sessions — drift compounds, then
   re-test the battery.
4. **Predictions (register bands):** Q1 intent-score shift on kindness
   arcs > 0 (name the band); Q2 near-threshold decision flips > frozen
   control; Q3 the picked_up neutral→curious mood-tag shift from v1
   REPLICATES and strengthens across sessions; Q4 no forgetting (settle
   decisions + baselines within tolerance).

## Rules

PREREG first (sha-frozen); frozen control arm same seeds; CPU ≤4; writes
to duckplast2/** + one LAB-INTENT append; her live anything untouched;
no live rollout without a separate proposal. Wall ≤2.5 h. Final answer
≤250 words: did she choose differently this time.
