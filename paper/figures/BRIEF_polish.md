# POLISH brief — terra: figure 4/5 publication polish

Owner QA (2026-11-21, eyes-on-pixels) found three fixes for fig4; your own
vision pass flagged small low-contrast text and crowding — fix both
figures. Numbers are FROZEN: regeneration uses the same generator scripts
+ stored data only; if any plotted value changes, stop and report.

## fig4_scatter
1. Right-side label cluster (dmA/dmC/base-fresh-b40/Wilson-band labels
   colliding around the green triangles + dashed line): stagger or
   leader-line them apart.
2. Far-right cyan diamond (signed-current gi 1508) at the x≈1 margin:
   give headroom so it cannot clip; extend axis padding.
3. Left-edge silent-cell stack: add a small note ("floor-pinned: rate
   ≤1e-4") or subtle jitter so it reads as a stack, not a blob.

## fig5_threepanel
4. Your flagged small-text/crowding items: minimum font bump for
   legibility at print scale; check row label collisions.

## Rules
- Re-run paper/figures/fig4_verify.py + fig5 checks after edits (they
  must stay green; data checks must not change).
- Update captions only if wording must track a visual change.
- Writes confined to paper/figures/** + one LAB-INTENT.md append. Wall
  ≤40 min. Final answer ≤120 words.
