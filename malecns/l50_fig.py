"""L50 figure: (A) the cost plane — duty vs drive-on seconds, non-monotone:
the budgeted duty58 (40 s) DOUBLES allw's structure while losing the fast-seg
lock; (B) per-segment duty — the 1.4-Hz segment is structure-toxic under
continuous drive (allw .022 vs free .538); (C) seed 11 S traces, allw vs
duty58. SVG -> rsvg-convert. Numbers loaded from results/traces (no hardcode).
"""
import json
import subprocess

import numpy as np

SEEDS = [11, 22, 33]
ARMS = ["free", "min5", "duty58", "ent", "allw"]
LABEL = {"free": "free (0 s)", "min5": "min5 (19 s)", "duty58": "duty58 (40 s)",
         "ent": "ent (64 s)", "allw": "allw (64 s)"}
tr = np.load("l50/traces_l50.npz")
res = json.load(open("l50/results_l50.json"))
W, H = 1560, 880
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
ARM_COL = {"free": "#9aa0ae", "min5": "#b39dff", "duty58": "#ffb37f",
           "ent": "#7fd4ff", "allw": "#ff8f8f"}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L50 always-driven trajectory: tracking costs drive, structure does '
       f'not follow</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">0.7&#8594;1.4&#8594;'
       f'0.7 Hz, hops at both transitions; duty = both S sides &#8805; .25 '
       f'(rolling 5 s, seg spans skip first 5 s); seeds 11/22/33</text>']

# ---------- panel A: cost plane ----------
ax, ay, aw, ah = 60, 110, 660, 300


def AX(v):   # drive seconds 0..70
    return ax + 50 + (aw - 80) * v / 70.0


def AY(v):   # duty 0..1
    return ay + (ah - 50) * (1 - v)


svg.append(f'<text x="{ax}" y="{ay-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">A &#8226; cost plane: structure duty vs '
           f'drive-on time</text>')
svg.append(f'<rect x="{ax+50}" y="{ay}" width="{aw-80}" height="{ah-50}" '
           f'fill="none" stroke="{GRID}"/>')
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    svg.append(f'<line x1="{ax+50}" y1="{AY(v):.1f}" x2="{ax+aw-30}" '
               f'y2="{AY(v):.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
    svg.append(f'<text x="{ax+44}" y="{AY(v)+4:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="end">{v:.2f}</text>')
for t in (0, 20, 40, 64):
    svg.append(f'<line x1="{AX(t):.1f}" y1="{ay+ah-50}" x2="{AX(t):.1f}" '
               f'y2="{ay+ah-44}" stroke="{MUT}"/>')
    svg.append(f'<text x="{AX(t):.1f}" y="{ay+ah-26}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{t} s</text>')
svg.append(f'<text x="{ax+(aw-30)/2+18}" y="{ay+ah-6}" fill="{MUT}" '
           f'font-size="13" text-anchor="middle">drive-on seconds '
           f'(window 60 s + settle 4 s)</text>')
svg.append(f'<text x="{ax+14}" y="{ay+(ah-50)/2}" fill="{MUT}" '
           f'font-size="13" transform="rotate(-90 {ax+14} '
           f'{ay+(ah-50)/2})">bilateral duty (both sides &#8805; .25)</text>')
ERR1 = {a: round(float(np.mean([res["segments"][a][str(s)]["segs"][1]["err"]
                                for s in SEEDS])), 3) for a in ARMS}
for a in ARMS:
    xs = res["cost"][a]["drive_on_s"]
    vals = [res["segments"][a][str(s)]["duty_all"] for s in SEEDS]
    for s, v in zip(SEEDS, vals):
        svg.append(f'<circle cx="{AX(xs):.1f}" cy="{AY(v):.1f}" r="6" '
                   f'fill="{SEED_COL[s]}" fill-opacity="0.75" '
                   f'stroke="{ARM_COL[a]}" stroke-width="2"/>')
    mv = float(np.mean(vals))
    svg.append(f'<rect x="{AX(xs)-7:.1f}" y="{AY(mv)-7:.1f}" width="14" '
               f'height="14" fill="{ARM_COL[a]}" '
               f'transform="rotate(45 {AX(xs):.1f} {AY(mv):.1f})"/>')
    dy = -14 if a not in ("ent",) else 16
    svg.append(f'<text x="{AX(xs)+12:.1f}" y="{AY(mv)+dy:.1f}" fill="{FG}" '
               f'font-size="14" font-weight="bold">{a}</text>')
    svg.append(f'<text x="{AX(xs)+12:.1f}" y="{AY(mv)+dy+15:.1f}" '
               f'fill="{MUT}" font-size="11">seg1 err {ERR1[a]:.3f}</text>')
svg.append(f'<text x="{ax+60}" y="{ay+22}" fill="{MUT}" font-size="12">'
           f'dots = seeds, diamond = mean; only allw locks 1.4 (err .001)'
           f'</text>')

# ---------- panel B: per-segment duty bars ----------
bx, by, bw, bh = 790, 110, 700, 300
SEGN = ["seg0 0.7 Hz", "seg1 1.4 Hz", "seg2 0.7 Hz"]
svg.append(f'<text x="{bx}" y="{by-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">B &#8226; the fast segment is '
           f'structure-toxic under continuous drive</text>')
svg.append(f'<rect x="{bx+40}" y="{by}" width="{bw-60}" height="{bh-50}" '
           f'fill="none" stroke="{GRID}"/>')
gw = (bw - 80) / 3.0
barw = gw / (len(ARMS) + 1.4)
for gi in range(3):
    gx = bx + 40 + gi * gw + gw * 0.12
    svg.append(f'<text x="{gx + gw*0.44:.1f}" y="{by+bh-26}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{SEGN[gi]}</text>')
    if gi == 1:
        svg.append(f'<rect x="{bx+40+gi*gw+2}" y="{by}" width="{gw-4}" '
                   f'height="{bh-50}" fill="#ff8f8f" fill-opacity="0.06"/>')
    for ai, a in enumerate(ARMS):
        v = res["cost"][a]["mean_duty_seg"][gi]
        hh = (bh - 50) * v
        x0 = gx + ai * barw + barw * 0.25
        svg.append(f'<rect x="{x0:.1f}" y="{by+bh-50-hh:.1f}" '
                   f'width="{barw*0.72:.1f}" height="{hh:.1f}" '
                   f'fill="{ARM_COL[a]}" fill-opacity="0.85"/>')
        svg.append(f'<text x="{x0+barw*0.36:.1f}" y="{by+bh-54-hh:.1f}" '
                   f'fill="{MUT}" font-size="10" text-anchor="middle">'
                   f'{v:.2f}</text>')
for v in (0.0, 0.5, 1.0):
    yy = by + (bh - 50) * (1 - v)
    svg.append(f'<line x1="{bx+40}" y1="{yy:.1f}" x2="{bx+bw-20}" '
               f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="2 4"/>')
lx = bx + 44
for a in ARMS:
    svg.append(f'<rect x="{lx:.1f}" y="{by+bh-14}" width="11" height="11" '
               f'fill="{ARM_COL[a]}"/>')
    svg.append(f'<text x="{lx+15:.1f}" y="{by+bh-4}" fill="{MUT}" '
               f'font-size="12">{a}</text>')
    lx += 24 + 8.5 * len(a)

# ---------- panel C: seed 11 S traces, allw vs duty58 ----------
cx, cy, cw2, ch2 = 60, 470, 1440, 360
T0, T1 = 0.0, 60.0


def CX(t):
    return cx + 50 + (cw2 - 70) * t / (T1 - T0)


def CY(v, row):
    y0 = cy + 26 + row * (ch2 / 2 - 10)
    return y0 + (ch2 / 2 - 66) * (1 - (v + 1.0) / 2.0)


svg.append(f'<text x="{cx}" y="{cy-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C &#8226; seed 11, per-side antagonist S: '
           f'allw (solid) crashes in seg1; duty58 (dashed) holds through '
           f'4-s gaps</text>')
for row, (side, key) in enumerate((("S_L", "SL"), ("S_R", "SR"))):
    y0 = cy + 26 + row * (ch2 / 2 - 10)
    hhh = ch2 / 2 - 66
    svg.append(f'<text x="{cx+10}" y="{y0+14}" fill="{FG}" font-size="14" '
               f'font-weight="bold">{side}  (gate .25)</text>')
    svg.append(f'<rect x="{cx+50}" y="{y0}" width="{cw2-70}" height="{hhh}" '
               f'fill="none" stroke="{GRID}"/>')
    svg.append(f'<rect x="{CX(20)}" y="{y0}" width="{CX(40)-CX(20)}" '
               f'height="{hhh}" fill="#ff8f8f" fill-opacity="0.07"/>')
    for tv, lab in ((-1.0, "-1"), (-0.5, "-.5"), (0.0, "0"),
                    (0.25, ".25"), (0.5, ".5"), (1.0, "1")):
        yy = CY(tv, row)
        dash = '2 4' if abs(tv - 0.25) > 1e-9 else '6 3'
        svg.append(f'<line x1="{cx+50}" y1="{yy:.1f}" x2="{cx+cw2-20}" '
                   f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
    for a, col, dash in (("allw", "#ff8f8f", "none"), ("duty58", "#ffb37f", "7 4")):
        arr = tr[f"{key}_{a}_11"]
        ts = np.arange(499, 6000, 10)
        pts = " ".join(f"{CX(t*0.01):.1f},{CY(arr[t], row):.1f}" for t in ts)
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
                   f'stroke-width="2" stroke-dasharray="{dash}"/>')
for t, lab in ((0, "0"), (20, "20"), (40, "40"), (60, "60 s")):
    svg.append(f'<text x="{CX(t):.1f}" y="{cy+ch2-4}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{lab}</text>')
svg.append(f'<line x1="{CX(20)}" y1="{cy+18}" x2="{CX(20)}" y2="{cy+ch2-22}" '
           f'stroke="{MUT}" stroke-dasharray="3 3"/>')
svg.append(f'<line x1="{CX(40)}" y1="{cy+18}" x2="{CX(40)}" y2="{cy+ch2-22}" '
           f'stroke="{MUT}" stroke-dasharray="3 3"/>')
svg.append(f'<line x1="{CX(60)}" y1="{cy+18}" x2="{CX(60)}" y2="{cy+ch2-22}" '
           f'stroke="{MUT}" stroke-dasharray="3 3"/>')
svg.append(f'<line x1="{CX(20)}" y1="{cy+8}" x2="{CX(40)}" '
           f'y2="{cy+8}" stroke="#ff8f8f" stroke-width="3"/>')
svg.append(f'<text x="{CX(30):.1f}" y="{cy+6}" fill="{MUT}" font-size="11" '
           f'text-anchor="middle">target 1.4 Hz</text>')
lx = cx + cw2 - 580
for lab, col, dash in (("allw (64 s drive)", "#ff8f8f", "none"),
                       ("duty58 (40 s, 5-on/4-off)", "#ffb37f", "7 4")):
    svg.append(f'<line x1="{lx}" y1="{cy+14}" x2="{lx+26}" y2="{cy+14}" '
               f'stroke="{col}" stroke-width="3" '
               f'stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{lx+32}" y="{cy+18}" fill="{MUT}" '
               f'font-size="12">{lab}</text>')
    lx += 300

open("l50/cost.svg", "w").write("\n".join(svg) + "</svg>")
subprocess.run(["rsvg-convert", "-o", "l50/cost.png", "l50/cost.svg"],
               check=True)
print("wrote l50/cost.png")
