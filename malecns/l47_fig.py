"""L47 figure: (A) norepair census state holds; (B) rep0 — drive holds the
inverted side during repair, release re-lotteries (hop+decorrelate or census);
(C) late per-side medians per arm/seed (the state map). SVG -> rsvg-convert."""
import json

import numpy as np

SEEDS = [11, 22, 33]
tr = np.load("l47/traces_l47.npz")
res = json.load(open("l47/results_l47.json"))
W, H = 1560, 560
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
T0S, T1S = 30.0, 180.0
STOPS, STOPE = 40.0, 60.0
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L47 repair-after-stop: the re-entrain restart is NOT a repair</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">'
       f'h40 cord, stop 20 s DNg88 &#8722;8, repair = 20 s re-entrain 0.7 Hz; '
       f'S per side, rolling 5 s; duty(both&#8805;.25) late = 0.000 everywhere</text>']


def sx(pane, t):
    return pane[0] + 40 + (pane[2] - 60) * (t - T0S) / (T1S - T0S)


def sy(pane, v, ymin=-1.0, ymax=1.0):
    return pane[1] + (pane[3] - 40) * (1 - (v - ymin) / (ymax - ymin))


def frame(pane, title):
    x0, y0, cw, chh = pane
    svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
               f'font-weight="bold">{title}</text>')
    svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
               f'fill="none" stroke="{GRID}"/>')
    for tv, lab in ((-0.5, "-.5"), (-0.25, "-.25"), (0.0, "0"),
                    (0.25, ".25 gate"), (0.5, ".5")):
        yy = sy(pane, tv)
        svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" '
                   f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="2 4" '
                   f'stroke-width="1"/>')
        svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" '
                   f'font-size="12" text-anchor="end">{lab}</text>')
    for t in (60, 90, 120, 150, 180):
        xx = sx(pane, t)
        svg.append(f'<text x="{xx:.1f}" y="{y0+chh-18}" fill="{MUT}" '
                   f'font-size="12" text-anchor="middle">{t}</text>')
    svg.append(f'<text x="{x0+(cw-20)//2+20}" y="{y0+chh-2}" fill="{MUT}" '
               f'font-size="13" text-anchor="middle">time (s)</text>')
    svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" '
               f'font-size="13" '
               f'transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" '
               f'text-anchor="middle">S(Tr) per side</text>')
    xa, xb = sx(pane, STOPS), sx(pane, STOPE)
    svg.append(f'<rect x="{xa:.1f}" y="{y0}" width="{xb-xa:.1f}" '
               f'height="{chh-40}" fill="#e05555" fill-opacity="0.13"/>')
    svg.append(f'<text x="{(xa+xb)/2:.1f}" y="{y0+16}" fill="#e08080" '
               f'font-size="12" text-anchor="middle">stop</text>')


def curve(pane, arr, col, dash, width=1.6, op=1.0):
    ts = np.arange(499, 18000, 50)
    pts = " ".join(f"{sx(pane, tt*0.01):.1f},{sy(pane, v):.1f}"
                   for tt, v in zip(ts, arr[ts])
                   if np.isfinite(v) and tt * 0.01 >= T0S)
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
               f'stroke-width="{width}" stroke-opacity="{op}" '
               f'stroke-dasharray="{dash}"/>')


P0 = (60, 118, 470, 392)
P1 = (570, 118, 470, 392)
P2 = (1080, 118, 440, 392)

frame(P0, "A. no repair: census state SL+|SR&#8722; holds all 120 s")
for s in SEEDS:
    curve(P0, tr[f"SL_norepair_{s}"], SEED_COL[s], "none", 1.8)
    curve(P0, tr[f"SR_norepair_{s}"], SEED_COL[s], "5 4", 1.8)
svg.append(f'<text x="{P0[0]+46}" y="{P0[1]+P0[3]-34}" fill="{MUT}" '
           f'font-size="12">solid = S_L (+.28) &#183; dashed = S_R '
           f'(&#8722;.47..&#8722;.49)</text>')

frame(P1, "B. immediate repair: drive holds S_R &#8212; release re-lotteries")
for s in SEEDS:
    curve(P1, tr[f"SL_rep0_{s}"], SEED_COL[s], "none", 1.1, 0.45)
    curve(P1, tr[f"SR_rep0_{s}"], SEED_COL[s], "5 4", 1.8)
ra, rb = sx(P1, 60.0), sx(P1, 80.0)
svg.append(f'<rect x="{ra:.1f}" y="{P1[1]}" width="{rb-ra:.1f}" '
           f'height="{P1[3]-40}" fill="#7fd4ff" fill-opacity="0.10"/>')
svg.append(f'<text x="{(ra+rb)/2:.1f}" y="{P1[1]+P1[3]-46}" fill="#9fd8ff" '
           f'font-size="12" text-anchor="middle">repair 20 s</text>')
svg.append(f'<text x="{P1[0]+46}" y="{P1[1]+P1[3]-34}" fill="{MUT}" '
           f'font-size="12">during: S_R +.68..+.78; after: hop (s11/33) '
           f'or census (s22)</text>')

# C: late per-side medians, arm x seed
x0, y0, cw, chh = P2
svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C. late state map (medians)</text>')
svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
           f'fill="none" stroke="{GRID}"/>')
for tv, lab in ((-0.5, "-.5"), (-0.25, "-.25 gate"), (0.0, "0"),
                (0.25, ".25 gate"), (0.5, ".5")):
    yy = sy(P2, tv)
    svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" y2="{yy:.1f}" '
               f'stroke="{GRID}" stroke-dasharray="2 4" stroke-width="1"/>')
    svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="11" '
               f'text-anchor="end">{lab}</text>')
ARMS = ["norepair", "rep0", "rep60"]
for i, a in enumerate(ARMS):
    cx = x0 + 40 + (cw - 60) * (i + 0.5) / 3
    svg.append(f'<text x="{cx:.0f}" y="{y0+chh-18}" fill="{MUT}" font-size="12" '
               f'text-anchor="middle">{a}</text>')
    for j, s in enumerate(SEEDS):
        t = res["table"][a][str(s)]
        dy = (j - 1) * 14
        yl, yr = sy(P2, t["SL_med_late"]), sy(P2, t["SR_med_late"])
        svg.append(f'<line x1="{cx-14+dy:.0f}" y1="{yl:.1f}" '
                   f'x2="{cx+14+dy:.0f}" y2="{yr:.1f}" '
                   f'stroke="{SEED_COL[s]}" stroke-width="1" '
                   f'stroke-opacity="0.55"/>')
        svg.append(f'<circle cx="{cx-14+dy:.0f}" cy="{yl:.1f}" r="5" '
                   f'fill="{SEED_COL[s]}"/>')
        svg.append(f'<rect x="{cx+14+dy-4:.0f}" y="{yr-4:.1f}" width="9" '
                   f'height="9" fill="none" stroke="{SEED_COL[s]}" '
                   f'stroke-width="2"/>')
svg.append(f'<text x="{x0+46}" y="{y0+16}" fill="{MUT}" font-size="12">'
           f'&#9679; S_L &#9634; S_R &#8212; paired per seed; '
           f'none reach both&#8805;.25</text>')
svg.append("</svg>")
open("l47/repair.svg", "w").write("\n".join(svg))
import subprocess
subprocess.run(["rsvg-convert", "-o", "l47/repair.png", "l47/repair.svg"],
               check=True)
print("l47/repair.png written")
