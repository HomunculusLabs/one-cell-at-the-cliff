# FIGURES brief — terra: Figure 4 (the scatter) + Figure 5 (three readouts)

Owner-directed (2026-11-21 ~14:0x). The draft is gate-green; it needs its
two new figures. Match the existing house style (see
paper/fig_l152.svg and figures/l152_clamp_cut_grid.svg in the repo root —
same fonts, stroke weights, palette; small multiples, no chartjunk).

## Figure 4 — the 36-arm scatter (the paper's new face)

- Data: /home/t3rpz/critters/peabrain-lab/banc/l175/results_l175.json
  (per-cell x_mean on the k=24 base, delivered drive, kR/16, meanR) plus
  banc/l185/results_l185.json (fresh-batch points for the six key arms —
  show both batches where available)
- X: cell mean rate (log-ish scale honest for the .0005-.99 range — state
  the transform); Y: meanR (or kR/16, pick one, state it)
- Encoding: window cells = small dots; silent cells hollow; the carrier =
  large highlighted marker labeled DNp33-L; the four twin families
  (mass dm 319, drive dmA/dmC, signed-current gi 1508) = distinct marker
  shapes with a small legend; base = horizontal reference band; the
  SUPER threshold = dashed line
- A small annotation: "7 cells with drive > carrier: none flip" (arrow at
  the high-drive cluster)
- Output: paper/figures/fig4_scatter.svg + .png (render the png from the
  svg with whatever local tool exists — rsvg-convert/inkscape/cairosvg —
  state which; if none, svg only and say so)

## Figure 5 — three readouts per arm (the honesty panel)

- Data: /home/t3rpz/critters/peabrain-lab/banc/l184/threepanel.csv
  (arm × chopped / unchopped-1.4Hz / cross-seed columns)
- Form: small-multiples grid or a grouped dot plot — every arm a row,
  three colored dots per row, consistent ordering (by chopped value);
  highlight carrier/twins/relay arms
- Output: paper/figures/fig5_threepanel.svg + .png

## Rules

- Numbers come ONLY from those stored files; no recomputation, no
  invented smoothing. If a value is missing, leave the marker out and
  note it in the figure caption file.
- Write a one-paragraph caption per figure: paper/figures/fig4_caption.md,
  fig5_caption.md (what's shown, the transform, the reading).
- Writes confined to paper/figures/** + one LAB-INTENT.md append. No
  draft edits (the manuscript agent owns DRAFT.md). No vision. Wall ≤1 h.
- Final answer ≤150 words.
