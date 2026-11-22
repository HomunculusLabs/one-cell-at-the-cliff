# FIGURE brief — Figure 6: the circuit (opus-5.5, house style)

Owner-directed (2026-11-21 ~21:5x, burn window). The paper's Figure 6:
the three-character circuit with its asymmetric necessity.

## Content (data from stored artifacts ONLY — no invented anatomy)

- Panel A — wiring cartoon (schematic, stated as such): carrier DNp33-L
  (gi 1110) → relay (gi 75494, 21-syn edge, ~60% of chopped effect) →
  right Ti pools; ru2 IN07B031-R (gi 70994) → both Ti pools (even, 5
  edges/side); the carrier's ~80 other outputs fanning wide (the
  signature's substrate). Use the L184/L198/L200 wiring JSONs for edge
  counts and laterality; label every number with its artifact key.
- Panel B — the asymmetric-necessity bars: right-side duty + signature
  for {base, carrier-cut, ru2-cut, carrier+ru2-cut, ru2-clamp variants}
  from banc/l200 + (when it lands) banc/l202 replication; left-side duty
  for the same arms.
- Panel C — the phase rotation: preferred-offset histogram or circular
  plot, base vs carrier-removed (theta +172 → +55, flexor/extensor peak
  phases from L199 parts B/C).
- Captions file with per-number artifact pointers; a fig6_verify.py
  (mirror fig4_verify.py; check every plotted value against its JSON).

## Style + rules

Match figures/l152_clamp_cut_grid.svg house style (fonts, strokes,
palette). SVG + PNG (rsvg-convert). Writes ONLY paper/figures/fig6* +
one LAB-INTENT append. No DRAFT edits. Wall ≤90 min. Final ≤150 words.
