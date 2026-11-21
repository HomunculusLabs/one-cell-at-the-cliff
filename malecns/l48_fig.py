"""L48 figure: (A) ramp30 — S_R persists THROUGH the fade, dies at the amp->0
crossing; (B) the release lottery is shape-INSENSITIVE and bimodal (0.7-memory
vs 1.4-hop, core-tracked); (C) post per-side medians — no arm reaches both>=.25.
SVG -> rsvg-convert."""
import json

import numpy as np

SEEDS = [11, 22, 33]
ARMS = ["norepair", "rep0", "ramp10", "ramp30", "ramp60", "dwell60", "dwell120"]
tr = np.load("l48/traces_l48.npz")
res = json.load(open("l48/results_l48.json"))
W, H = 1560, 560
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
T0S, T1S = 60.0, 170.0
STOPS, STOPE = 40.0, 60.0
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L48 release-shaping: NO shape repairs &#8212; the lottery rides the '
       f'amp&#8594;0 crossing</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">'
       f'h40 cord + stop 20 s DNg88 &#8722;8, repair drive 0.7 Hz; ramps '
       f'10/30/60 s, dwell 60/120 s; S per side, rolling 5 s; '
       f'duty(both&#8805;.25) post &lt; .5 in 18/18 treatment cells</text>']


def sx(pane, t):
    return pane[0] + 40 + (pane[2] - 60) * (t - T0S) / (T1S - T0S)


def sy(pane, v, ymin=-1.0, ymax=1.0):
    return pane[1] + (pane[3] - 40) * (1 - (v - ymin) / (ymax - ymin))


def frame(pane, title, ylabs, yv=True):
    x0, y0, cw, chh = pane
    svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
               f'font-weight="bold">{title}</text>')
    svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
               f'fill="none" stroke="{GRID}"/>')
    for tv, lab in ylabs:
        yy = sy(pane, tv)
        svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" '
                   f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="2 4" '
                   f'stroke-width="1"/>')
        svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" '
                   f'font-size="12" text-anchor="end">{lab}</text>')
    for t in (80, 110, 140, 170):
        xx = sx(pane, t)
        svg.append(f'<text x="{xx:.1f}" y="{y0+chh-18}" fill="{MUT}" '
                   f'font-size="12" text-anchor="middle">{t}</text>')
    svg.append(f'<text x="{x0+(cw-20)//2+20}" y="{y0+chh-2}" fill="{MUT}" '
               f'font-size="13" text-anchor="middle">time (s)</text>')
    svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" '
               f'font-size="13" '
               f'transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" '
               f'text-anchor="middle">S(Tr) right side</text>')
    xa, xb = sx(pane, STOPS), sx(pane, STOPE)
    svg.append(f'<rect x="{xa:.1f}" y="{y0}" width="{xb-xa:.1f}" '
               f'height="{chh-40}" fill="#e05555" fill-opacity="0.13"/>')
    svg.append(f'<text x="{(xa+xb)/2:.1f}" y="{y0+16}" fill="#e08080" '
               f'font-size="12" text-anchor="middle">stop</text>')


def curve(pane, arr, col, dash, width=1.6, op=1.0):
    ts = np.arange(499, 24000, 50)
    pts = " ".join(f"{sx(pane, tt*0.01):.1f},{sy(pane, v):.1f}"
                   for tt, v in zip(ts, arr[ts])
                   if np.isfinite(v) and 60.0 <= tt * 0.01 < 170.0)
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
               f'stroke-width="{width}" stroke-opacity="{op}" '
               f'stroke-dasharray="{dash}"/>')


YL = [(-0.5, "-.5"), (-0.25, "-.25"), (0.0, "0"), (0.25, ".25 gate"), (0.5, ".5"),
      (0.75, ".75")]

# A: ramp30 — structure lives through the fade, dies at the crossing
P0 = (60, 118, 470, 392)
frame(P0, "A. ramp30: S_R rides the 30-s fade, collapses at amp&#8594;0", YL)
for s in SEEDS:
    curve(P0, tr[f"SL_ramp30_{s}"], SEED_COL[s], "none", 1.1, 0.45)
    curve(P0, tr[f"SR_ramp30_{s}"], SEED_COL[s], "5 4", 1.8)
ra, rb = sx(P0, 60.0), sx(P0, 80.0)
svg.append(f'<rect x="{ra:.1f}" y="{P0[1]}" width="{rb-ra:.1f}" '
           f'height="{P0[3]-40}" fill="#7fd4ff" fill-opacity="0.10"/>')
fa, fb = sx(P0, 80.0), sx(P0, 110.0)
svg.append(f'<rect x="{fa:.1f}" y="{P0[1]}" width="{fb-fa:.1f}" '
           f'height="{P0[3]-40}" fill="#7fd4ff" fill-opacity="0.05"/>')
svg.append(f'<line x1="{fb:.1f}" y1="{P0[1]}" x2="{fb:.1f}" '
           f'y2="{P0[1]+P0[3]-40}" stroke="#e8e6e3" stroke-width="1.4" '
           f'stroke-dasharray="6 3"/>')
svg.append(f'<text x="{(ra+rb)/2:.1f}" y="{P0[1]+P0[3]-46}" fill="#9fd8ff" '
           f'font-size="12" text-anchor="middle">drive</text>')
svg.append(f'<text x="{(fa+fb)/2:.1f}" y="{P0[1]+P0[3]-46}" fill="#9fd8ff" '
           f'font-size="12" text-anchor="middle">fade</text>')
svg.append(f'<text x="{fb+6:.1f}" y="{P0[1]+16}" fill="{FG}" font-size="12">'
           f'release-off</text>')
svg.append(f'<text x="{P0[0]+46}" y="{P0[1]+312}" fill="{MUT}" font-size="12">'
           f'dashed = S_R &#183; solid = S_L</text>')
svg.append(f'<text x="{P0[0]+46}" y="{P0[1]+330}" fill="{MUT}" font-size="12">'
           f'fade medians S_R +.39..+.64</text>')

# B: release lottery — f_post per arm/seed, bimodal, shape-insensitive
P1 = (570, 118, 470, 392)
x0, y0, cw, chh = P1
svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">B. post-release frequency: two basins, '
           f'every shape</text>')
svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
           f'fill="none" stroke="{GRID}"/>')


def fy(v, lo=0.3, hi=2.1):
    return y0 + (chh - 40) * (1 - (v - lo) / (hi - lo))


for lo, hi, col in ((0.55, 0.85, "#7fd4aa"), (1.42, 1.68, "#e08a8a")):
    svg.append(f'<rect x="{x0+40}" y="{fy(hi):.1f}" width="{cw-60}" '
               f'height="{fy(lo)-fy(hi):.1f}" fill="{col}" '
               f'fill-opacity="0.10"/>')
for fv, lab in ((0.7, "0.7 memory"), (1.55, "1.4&#8211;1.6 hop")):
    svg.append(f'<line x1="{x0+40}" y1="{fy(fv):.1f}" x2="{x0+cw-20}" '
               f'y2="{fy(fv):.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
    svg.append(f'<text x="{x0+cw-24}" y="{fy(fv)-5:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="end">{lab}</text>')
for i, a in enumerate(ARMS):
    cx = x0 + 40 + (cw - 60) * (i + 0.5) / 7
    svg.append(f'<text x="{cx:.0f}" y="{y0+chh-18}" fill="{MUT}" '
               f'font-size="11" text-anchor="middle">{a}</text>')
    for j, s in enumerate(SEEDS):
        t = res["table"][a][str(s)]
        dy = (j - 1) * 11
        hopped = t["hop"] > 0.3
        svg.append(f'<circle cx="{cx+dy:.0f}" cy="{fy(t["f_post"]):.1f}" r="5" '
                   f'fill="{SEED_COL[s]}" fill-opacity="0.35" '
                   f'stroke="{SEED_COL[s]}" stroke-width="{2 if hopped else 1}"/>')
svg.append(f'<text x="{x0+46}" y="{y0+16}" fill="{MUT}" font-size="12">'
           f'f post (60 s window); outlined = hop; 13/18 treatment releases '
           f'hop, 5/18 keep 0.7; core tracks: .247 vs .196</text>')

# C: post per-side medians, arm x seed
P2 = (1080, 118, 440, 392)
x0, y0, cw, chh = P2
svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C. post state map (medians)</text>')
svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
           f'fill="none" stroke="{GRID}"/>')
for tv, lab in ((-0.5, "-.5"), (-0.25, "-.25 gate"), (0.0, "0"),
                (0.25, ".25 gate"), (0.5, ".5")):
    yy = sy(P2, tv)
    svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" y2="{yy:.1f}" '
               f'stroke="{GRID}" stroke-dasharray="2 4" stroke-width="1"/>')
    svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="11" '
               f'text-anchor="end">{lab}</text>')
for i, a in enumerate(ARMS):
    cx = x0 + 40 + (cw - 60) * (i + 0.5) / 7
    svg.append(f'<text x="{cx:.0f}" y="{y0+chh-18}" fill="{MUT}" font-size="11" '
               f'text-anchor="middle">{a}</text>')
    for j, s in enumerate(SEEDS):
        t = res["table"][a][str(s)]
        dy = (j - 1) * 9
        yl, yr = sy(P2, t["SL_med_post"]), sy(P2, t["SR_med_post"])
        svg.append(f'<line x1="{cx-11+dy:.0f}" y1="{yl:.1f}" '
                   f'x2="{cx+11+dy:.0f}" y2="{yr:.1f}" '
                   f'stroke="{SEED_COL[s]}" stroke-width="1" '
                   f'stroke-opacity="0.55"/>')
        svg.append(f'<circle cx="{cx-11+dy:.0f}" cy="{yl:.1f}" r="4" '
                   f'fill="{SEED_COL[s]}"/>')
        svg.append(f'<rect x="{cx+11+dy-3.5:.0f}" y="{yr-3.5:.1f}" width="8" '
                   f'height="8" fill="none" stroke="{SEED_COL[s]}" '
                   f'stroke-width="2"/>')
svg.append(f'<text x="{x0+46}" y="{y0+16}" fill="{MUT}" font-size="12">'
           f'&#9679; S_L &#9634; S_R &#8212; nearest: ramp30/s33 '
           f'+.54 / +.24 (duty .44)</text>')
svg.append(f'<text x="{x0+46}" y="{y0+34}" fill="{MUT}" font-size="12">'
           f'norepair holds SL+|SR&#8722; out to 220 s</text>')
svg.append("</svg>")
open("l48/release.svg", "w").write("\n".join(svg))
import subprocess
subprocess.run(["rsvg-convert", "-o", "l48/release.png", "l48/release.svg"],
               check=True)
print("l48/release.png written")
