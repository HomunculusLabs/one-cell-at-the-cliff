"""L51 figure: (A) cost plane — the hybrid lands at 48 s drive with .484 pooled
duty (gate .5 dashed), holding allw-level tracking; (B) per-segment duty —
hybrid matches duty58 in the 0.7 windows (.64/.56) while the fast window is
a seed lottery (.133/.627/0.0); (C) seed 33 per-side S — hybrid (solid, with
hop) collapses in the fast window while hynohop (dashed) keeps structure:
the hop that buys the lock from continuous entry COSTS structure when the
chopped entry locks for free. SVG -> rsvg-convert. Numbers from artifacts."""
import json
import subprocess

import numpy as np

SEEDS = [11, 22, 33]
ARMS = ["duty58", "hybrid", "hynohop", "allw"]
LABEL = {"duty58": "duty58 (40 s)", "hybrid": "hybrid (48 s)",
         "hynohop": "hynohop (48 s)", "allw": "allw (64 s)"}
tr = np.load("l51/traces_l51.npz")
res = json.load(open("l51/results_l51.json"))
W, H = 1560, 900
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
ARM_COL = {"duty58": "#ffb37f", "hybrid": "#8fd98f", "hynohop": "#8fd9d9",
           "allw": "#ff8f8f"}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L51 hybrid schedule: window-scoped spec closes, pooled duty misses '
       f'by .016</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">chopped 5-on/4-off '
       f'on the 0.7 segments + continuous on the fast 1.4, hops at both '
       f'transitions; duty = both S sides &#8805; .25 (rolling 5 s); seeds '
       f'11/22/33</text>']

# ---------- panel A: cost plane ----------
ax, ay, aw, ah = 60, 120, 660, 300


def AX(v):   # drive seconds 30..70
    return ax + 50 + (aw - 80) * (v - 30) / 40.0


def AY(v):   # duty 0..1
    return ay + (ah - 50) * (1 - v)


svg.append(f'<text x="{ax}" y="{ay-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">A &#8226; cost plane: pooled duty vs '
           f'drive-on (gate .5 dashed)</text>')
svg.append(f'<rect x="{ax+50}" y="{ay}" width="{aw-80}" height="{ah-50}" '
           f'fill="none" stroke="{GRID}"/>')
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    dash = '5 3' if abs(v - 0.5) < 1e-9 else '2 4'
    svg.append(f'<line x1="{ax+50}" y1="{AY(v):.1f}" x2="{ax+aw-30}" '
               f'y2="{AY(v):.1f}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{ax+44}" y="{AY(v)+4:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="end">{v:.2f}</text>')
for t in (40, 48, 64):
    svg.append(f'<line x1="{AX(t):.1f}" y1="{ay+ah-50}" x2="{AX(t):.1f}" '
               f'y2="{ay+ah-44}" stroke="{MUT}"/>')
    svg.append(f'<text x="{AX(t):.1f}" y="{ay+ah-26}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{t} s</text>')
svg.append(f'<text x="{ax+(aw-30)/2+18}" y="{ay+ah-6}" fill="{MUT}" '
           f'font-size="13" text-anchor="middle">drive-on seconds '
           f'(task 60 s + settle 4 s)</text>')
svg.append(f'<text x="{ax+14}" y="{ay+(ah-50)/2}" fill="{MUT}" '
           f'font-size="13" transform="rotate(-90 {ax+14} '
           f'{ay+(ah-50)/2})">pooled bilateral duty</text>')
ERR1 = {a: round(float(np.mean([res["segments"][a][str(s)]["segs"][1]["err"]
                                for s in SEEDS])), 3) for a in ARMS}
LBL_DY = {"hybrid": -70, "hynohop": 26, "duty58": -34, "allw": -34}
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
    dy = LBL_DY[a]
    svg.append(f'<text x="{AX(xs)+12:.1f}" y="{AY(mv)+dy:.1f}" fill="{FG}" '
               f'font-size="14" font-weight="bold">{a}</text>')
    svg.append(f'<text x="{AX(xs)+12:.1f}" y="{AY(mv)+dy+15:.1f}" '
               f'fill="{MUT}" font-size="11">mean {mv:.3f} | seg1 err '
               f'{ERR1[a]:.3f}</text>')
svg.append(f'<text x="{ax+60}" y="{ay+22}" fill="{MUT}" font-size="12">'
           f'dots = seeds, diamond = mean; hybrid .484 misses .5 by .016 '
           f'(seed 33 fast window 0.0)</text>')

# ---------- panel B: per-segment duty bars ----------
bx, by, bw, bh = 790, 120, 700, 300
SEGN = ["seg0 0.7 Hz", "seg1 1.4 Hz", "seg2 0.7 Hz"]
svg.append(f'<text x="{bx}" y="{by-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">B &#8226; hybrid holds the 0.7 windows; '
           f'the fast window is a seed lottery</text>')
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
    dash = '5 3' if abs(v - 0.5) < 1e-9 else '2 4'
    svg.append(f'<line x1="{bx+40}" y1="{yy:.1f}" x2="{bx+bw-20}" '
               f'y2="{yy:.1f}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
svg.append(f'<text x="{bx+40+gw+2}" y="{by+16}" fill="#ff8f8f" '
           f'font-size="11">continuous 1.4 window</text>')
lx = bx + 44
for a in ARMS:
    svg.append(f'<rect x="{lx:.1f}" y="{by+bh-14}" width="11" height="11" '
               f'fill="{ARM_COL[a]}"/>')
    svg.append(f'<text x="{lx+15:.1f}" y="{by+bh-4}" fill="{MUT}" '
               f'font-size="12">{a}</text>')
    lx += 24 + 8.5 * len(a)

# ---------- panel C: seed 33 per-side S, hybrid vs hynohop ----------
cx, cy, cw2, ch2 = 60, 490, 1440, 370
T0, T1 = 0.0, 60.0


def CX(t):
    return cx + 50 + (cw2 - 70) * t / (T1 - T0)


def CY(v, row):
    y0 = cy + 26 + row * (ch2 / 2 - 10)
    return y0 + (ch2 / 2 - 66) * (1 - (v + 1.0) / 2.0)


svg.append(f'<text x="{cx}" y="{cy-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C &#8226; seed 33 per-side S: hybrid (solid, '
           f'hop) dies in the fast window; hynohop (dashed) keeps it &#8212; '
           f'the lock came free from chopped entry</text>')
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
    for a, dash in (("hybrid", "none"), ("hynohop", "7 4")):
        arr = tr[f"{key}_{a}_33"]
        ts = np.arange(499, 6000, 10)
        pts = " ".join(f"{CX(t*0.01):.1f},{CY(arr[t], row):.1f}" for t in ts)
        svg.append(f'<polyline points="{pts}" fill="none" '
                   f'stroke="{ARM_COL[a]}" stroke-width="2" '
                   f'stroke-dasharray="{dash}"/>')
for t, lab in ((0, "0"), (20, "20"), (40, "40"), (60, "60 s")):
    svg.append(f'<text x="{CX(t):.1f}" y="{cy+ch2-4}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{lab}</text>')
for t in (20, 40, 60):
    svg.append(f'<line x1="{CX(t)}" y1="{cy+18}" x2="{CX(t)}" '
               f'y2="{cy+ch2-22}" stroke="{MUT}" stroke-dasharray="3 3"/>')
lx = cx + cw2 - 620
for lab, a, dash in (("hybrid: hop at 2000/4000 (seg1 duty 0.00)", "hybrid", "none"),
                     ("hynohop: no hops (seg1 duty 0.21)", "hynohop", "7 4")):
    svg.append(f'<line x1="{lx}" y1="{cy+14}" x2="{lx+26}" y2="{cy+14}" '
               f'stroke="{ARM_COL[a]}" stroke-width="3" '
               f'stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{lx+32}" y="{cy+18}" fill="{MUT}" '
               f'font-size="12">{lab}</text>')
    lx += 340

open("l51/hybrid.svg", "w").write("\n".join(svg) + "</svg>")
subprocess.run(["rsvg-convert", "-o", "l51/hybrid.png", "l51/hybrid.svg"],
               check=True)
print("wrote l51/hybrid.png")
