"""L49 figure: (A) gap80 — S_R crashes ~5.5 s into the drive-off, long-gap
end-points are a lottery (seed 33 re-forms, 11/22 stick SL+|SR-); (B) the slack
curve: max safe gap 5 s, sharp; (C) resume re-forms 15/15 (S_R rebuilt, S_L
marginal = the operating point's own weakness). SVG -> rsvg-convert."""
import json

import numpy as np

SEEDS = [11, 22, 33]
tr = np.load("l49/traces_l49.npz")
res = json.load(open("l49/results_l49.json"))
W, H = 1560, 560
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
GS = [5, 10, 20, 40, 80]
GKEY = {5: "gap5", 10: "gap10", 20: "gap20", 40: "gap40", 80: "gap80"}
T0S, T1S = 30.0, 170.0
GAP_A = (40.0, 120.0)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L49 drive-gap tolerance: slack = 5 s, sharp &#8212; then a collapse '
       f'at ~5.5 s and a lottery</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">'
       f'h40 cord, entrain .3 @ 0.7 Hz; drive OFF for G s, then back on; '
       f'S per side, rolling 5 s; held = both &#8805; .25</text>']


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
                    (0.25, ".25 gate"), (0.5, ".5"), (0.75, ".75")):
        yy = sy(pane, tv)
        svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" '
                   f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="2 4" '
                   f'stroke-width="1"/>')
        svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" '
                   f'font-size="12" text-anchor="end">{lab}</text>')
    for t in (50, 80, 110, 140, 170):
        xx = sx(pane, t)
        svg.append(f'<text x="{xx:.1f}" y="{y0+chh-18}" fill="{MUT}" '
                   f'font-size="12" text-anchor="middle">{t}</text>')
    svg.append(f'<text x="{x0+(cw-20)//2+20}" y="{y0+chh-2}" fill="{MUT}" '
               f'font-size="13" text-anchor="middle">time (s)</text>')
    svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" '
               f'font-size="13" transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" '
               f'text-anchor="middle">S(Tr)</text>')


def curve(pane, arr, col, dash, width=1.6, op=1.0):
    ts = np.arange(499, 18000, 50)
    pts = " ".join(f"{sx(pane, tt*0.01):.1f},{sy(pane, v):.1f}"
                   for tt, v in zip(ts, arr[ts])
                   if np.isfinite(v) and T0S <= tt * 0.01 < T1S)
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
               f'stroke-width="{width}" stroke-opacity="{op}" '
               f'stroke-dasharray="{dash}"/>')


YL = [(-0.5, "-.5"), (-0.25, "-.25"), (0.0, "0"), (0.25, ".25 gate"),
      (0.5, ".5"), (0.75, ".75")]

# A: gap80 — the crash and the lottery
P0 = (60, 118, 470, 392)
frame(P0, "A. gap80: S_R crashes ~5.5 s into drive-off; end = lottery")
for s in SEEDS:
    curve(P0, tr[f"SL_gap80_{s}"], SEED_COL[s], "none", 1.1, 0.45)
    curve(P0, tr[f"SR_gap80_{s}"], SEED_COL[s], "5 4", 1.8)
ga, gb = sx(P0, GAP_A[0]), sx(P0, GAP_A[1])
svg.append(f'<rect x="{ga:.1f}" y="{P0[1]}" width="{gb-ga:.1f}" '
           f'height="{P0[3]-40}" fill="#e05555" fill-opacity="0.10"/>')
svg.append(f'<text x="{(ga+gb)/2:.1f}" y="{P0[1]+16}" fill="#e08080" '
           f'font-size="12" text-anchor="middle">drive off 80 s</text>')
cx = sx(P0, 45.5)
svg.append(f'<line x1="{cx:.1f}" y1="{P0[1]}" x2="{cx:.1f}" '
           f'y2="{P0[1]+P0[3]-40}" stroke="#e08080" stroke-width="1.3" '
           f'stroke-dasharray="5 3"/>')
svg.append(f'<text x="{cx+5:.1f}" y="{P0[1]+34}" fill="#e08080" '
           f'font-size="12">collapse ~5.5 s</text>')
svg.append(f'<text x="{gb+6:.1f}" y="{P0[1]+16}" fill="{FG}" font-size="12">'
           f'drive on</text>')
svg.append(f'<text x="{P0[0]+46}" y="{P0[1]+312}" fill="{MUT}" font-size="12">'
           f'dashed = S_R &#183; solid = S_L</text>')
svg.append(f'<text x="{P0[0]+46}" y="{P0[1]+330}" fill="{MUT}" font-size="12">'
           f'ends: s11 SL+|SR&#8722; &#183; s22 both&#8722; &#183; s33 re-forms</text>')

# B: slack curve — end-of-gap min side vs G
P1 = (570, 118, 470, 392)
x0, y0, cw, chh = P1
svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">B. slack curve: max safe gap 5 s '
           f'(3/3 held); &#8805;10 s lost</text>')
svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
           f'fill="none" stroke="{GRID}"/>')
for tv, lab in ((-0.75, "-.75"), (-0.5, "-.5"), (-0.25, "-.25"), (0.0, "0"),
                (0.25, ".25 gate"), (0.5, ".5"), (0.75, ".75")):
    yy = sy(P1, tv)
    svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" '
               f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
    svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="11" '
               f'text-anchor="end">{lab}</text>')
svg.append(f'<rect x="{x0+40}" y="{sy(P1,0.75):.1f}" width="{cw-60}" '
           f'height="{sy(P1,0.25)-sy(P1,0.75):.1f}" fill="#7fd4aa" '
           f'fill-opacity="0.08"/>')
# cont reference (G=0): min-side median over [40,80) s
TSr = np.arange(499, 18000, 10)
cont_ref = []
for s in SEEDS:
    SL, SR = tr[f"SL_cont_{s}"], tr[f"SR_cont_{s}"]
    q = (TSr >= 4000) & (TSr < 8000)
    cont_ref.append(min(np.nanmedian(SL[TSr[q]]), np.nanmedian(SR[TSr[q]])))
xc0 = x0 + 40 + (cw - 60) * 0.5 / 6
svg.append(f'<line x1="{xc0-8:.0f}" y1="{sy(P1, min(cont_ref)):.1f}" '
           f'x2="{xc0+8:.0f}" y2="{sy(P1, min(cont_ref)):.1f}" '
           f'stroke="{FG}" stroke-width="2"/>')
svg.append(f'<text x="{xc0:.0f}" y="{y0+chh-18}" fill="{MUT}" font-size="11" '
           f'text-anchor="middle">cont</text>')
svg.append(f'<text x="{xc0:.0f}" y="{sy(P1, min(cont_ref))-8:.1f}" '
           f'fill="{MUT}" font-size="11" text-anchor="middle">'
           f'{min(cont_ref):+.2f}</text>')
for i, gv in enumerate(GS):
    cx = x0 + 40 + (cw - 60) * (i + 1.5) / 6
    svg.append(f'<text x="{cx:.0f}" y="{y0+chh-18}" fill="{MUT}" '
               f'font-size="11" text-anchor="middle">{gv} s</text>')
    for j, s in enumerate(SEEDS):
        t = res["table"][GKEY[gv]][str(s)]
        v = min(t["SL_end"], t["SR_end"])
        dy = (j - 1) * 0
        lotto = (not t["held"]) and v >= 0.25
        svg.append(f'<circle cx="{cx+dy*11:.0f}" cy="{sy(P1, v):.1f}" r="5.5" '
                   f'fill="{SEED_COL[s]}" fill-opacity="{1.0 if t["held"] else 0.30}" '
                   f'stroke="{SEED_COL[s]}" stroke-width="2"'
                   + (' stroke-dasharray="3 2"' if lotto else "") + "/>")
held_n = [res["verdict"]["C2"][GKEY[gv]]["held_n"] for gv in GS]
svg.append(f'<text x="{x0+46}" y="{y0+16}" fill="{MUT}" font-size="12">'
           f'held 3/3 &#183; open-pale = collapsed then re-held (lottery, s33) '
           f'&#183; held n = {held_n}</text>')
svg.append(f'<text x="{x0+46}" y="{y0+34}" fill="{MUT}" font-size="12">'
           f't_collapse 5.49&#8211;5.69 s in 15/15 arm-seeds &#8805;10 s</text>')

# C: resume re-formation — duty + latency
P2 = (1080, 118, 440, 392)
x0, y0, cw, chh = P2
svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C. resume (60 s): S_R rebuilt, S_L '
           f'marginal</text>')
svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
           f'fill="none" stroke="{GRID}"/>')


def dy_(v):
    return y0 + (chh - 40) * (1 - v / 1.0)


for tv, lab in ((0.0, "0"), (0.25, ".25"), (0.5, ".5 gate"), (0.75, ".75"),
                (1.0, "1")):
    svg.append(f'<line x1="{x0+40}" y1="{dy_(tv):.1f}" x2="{x0+cw-20}" '
               f'y2="{dy_(tv):.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
    svg.append(f'<text x="{x0+36}" y="{dy_(tv)+4:.1f}" fill="{MUT}" '
               f'font-size="11" text-anchor="end">{lab}</text>')
svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" font-size="13" '
           f'transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" '
           f'text-anchor="middle">duty both &#8805; .25</text>')
for i, gv in enumerate(GS):
    cx = x0 + 40 + (cw - 60) * (i + 0.5) / 5
    svg.append(f'<text x="{cx:.0f}" y="{y0+chh-18}" fill="{MUT}" font-size="11" '
               f'text-anchor="middle">{gv} s</text>')
    for j, s in enumerate(SEEDS):
        t = res["table"][GKEY[gv]][str(s)]
        dy = (j - 1) * 11
        svg.append(f'<circle cx="{cx+dy:.0f}" cy="{dy_(t["duty_resume"]):.1f}" '
                   f'r="5" fill="{SEED_COL[s]}" fill-opacity="0.85"/>')
        lat = t.get("lat_sust5_s")
        if lat is not None:
            svg.append(f'<line x1="{cx+dy:.0f}" y1="{dy_(t["duty_resume"])-8:.1f}" '
                       f'x2="{cx+dy:.0f}" y2="{dy_(t["duty_resume"])-13:.1f}" '
                       f'stroke="{SEED_COL[s]}" stroke-width="1.4"/>')
svg.append(f'<text x="{x0+46}" y="{y0+16}" fill="{MUT}" font-size="12">'
           f're-formed sustained-5s 15/15 (0.1&#8211;50.8 s; tick = fast) &#183; '
           f'S_R med +.68..+.79 all</text>')
svg.append(f'<text x="{x0+46}" y="{y0+34}" fill="{MUT}" font-size="12">'
           f'S_L marginal even in cont (SL med .23/.28/&#8722;.10) '
           f'&#8212; the op point, not the gap</text>')
svg.append("</svg>")
open("l49/gap.svg", "w").write("\n".join(svg))
import subprocess
subprocess.run(["rsvg-convert", "-o", "l49/gap.png", "l49/gap.svg"], check=True)
print("l49/gap.png written")
