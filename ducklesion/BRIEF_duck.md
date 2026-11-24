# EXPERIMENT brief — astra: the DUCK lesion scan (her brain, our method)

Owner-directed (2026-11-21 ~13:0x). We spent the day finding the one cell
that matters in a fly cord model. The duck's brain is the same kind of
object — FlyWire v783 connectome (~13k neurons) driving a live pet
(senses, mood, intent routing → locomotion). Run today's methodology on
HER. OFFLINE ONLY: the lab convention — her live modules under
~/critters/peabrain are imported READ-ONLY, never modified; all writes to
/home/t3rpz/critters/peabrain-lab/ducklesion/.

## Subject interface (read these first)

- ~/critters/peabrain/brain.py (rate model), senses.py, mood.py
  (mood axes incl. fear), bridge.py (intent routing: to_you/to_bowl/
  to_fence/to_boot/to_pond/settle + forage/dabble/nest/beg/hide),
  brain_graph.pt (v783 graph)
- ~/critters/peabrain-lab/README.md — the lab preamble pattern (read-only
  imports, fixed seeds, nothing live is touched)

## Design task (PREREG-analysis BEFORE computation)

1. Pick ONE behavioral readout with real dynamic range and ethical
   distance: recommended = SCARE RESPONSE — present a standardized scare
   stimulus (her senses pipeline) and measure hide-intent probability /
   latency / duration per rollout of her loop. Alternative if that lacks
   range: feeding-approach under hunger. State the choice + bands in the
   PREREG before touching data.
2. Census: which cells are active during the scare window (her graph,
   matched operating conventions — declare gain handling explicitly).
3. The scan: single-cell deletions (or activity-clamps) over the ~30-60
   most active scare-window cells, matched twins (out-mass AND delivered
   drive, the L175/L185 ladder), rate-vs-outcome scatter. Small n is fine
   (8 seeds/cell) — this is discovery, not confirmation.
4. Output: does SHE have a carrier? A cell whose removal flips her scare
   behavior while matched twins do nothing? Or is her fear distributed?

## Deliverables

- ducklesion/PREREG.md (analysis plan + bands first)
- probe scripts + outputs, census npz, results json
- ducklesion/DUCK-FINDINGS.md (≤70 lines): the scatter, the verdict
  (carrier / distributed / readout-too-weak), and — if a candidate exists —
  a proposal for what teaching her would look like (live rollout stays
  behind the service-gate discipline, NOT this dispatch)
- Final answer ≤300 words.

## Ground rules

Zero writes outside peabrain-lab/ducklesion/** (+ one LAB-INTENT.md
append). Her live services, sessions/, mood history = READ-ONLY. CPU ≤4
workers (concurrent lanes running). No vision. Wall ≤2 h. Never ping
anyone.
