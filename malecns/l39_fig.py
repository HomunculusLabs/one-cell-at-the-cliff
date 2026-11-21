"""L39 figure: controller tracking — f_track (5-s blocks) per arm vs the
stepped target, one panel per seed; volley ticks + S<0.25 shading."""
import json

import numpy as np

r = json.load(open("l39/results_l39.json"))
SEEDS = ["11", "22", "33"]
W, H, PADX, PADY, PH = 940, 300, 56, 34, 208
FY0, FYH = 0.3, 3.2          # Hz range
BT = (W - PADX - 14) / 60.0  # px per second (was hardcoded 2.5 -> half-scale)
LGH = 80
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" '
       f'height="{H * 3 + LGH + 12}" font-family="DejaVu Sans" font-size="12">']
svg.append(f'<rect width="{W}" height="{H * 3 + LGH + 12}" fill="#111318"/>')
COL = {"free": ("#8a8f98", "2 3"), "ent": ("#7aa2f7", ""),
       "ent_h046": ("#e06c9f", "7 3"), "ent_h110": ("#9ece6a", "1 3")}
LBL = {"free": "free-run", "ent": "entrain only (A=.3)",
       "ent_h046": "entrain + DNge046-L hop", "ent_h110": "entrain + DNg110 hop"}
for pi, s in enumerate(SEEDS):
    y0 = pi * H + 4
    svg.append(f'<text x="{PADX}" y="{y0 + 20}" fill="#c0caf5" font-size="15">'
               f'seed {s} — attractor { {11: "0.80", 22: "1.44", 33: "1.42"}[int(s)] } Hz</text>')
    # plot frame
    px, py, pw, ph = PADX, y0 + PADY, W - PADX - 14, PH
    for f in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        yy = py + ph - (f - FY0) / (FYH - FY0) * ph
        svg.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + pw}" y2="{yy:.1f}" '
                   f'stroke="#2a2e3a" stroke-width="1"/>')
        svg.append(f'<text x="{px - 8}" y="{yy + 4:.1f}" fill="#6b7280" '
                   f'text-anchor="end" font-size="11">{f}</text>')
    # S<0.25 shading per segment (hop arm segments)
    for i in range(3):
        seg = r["segments"]["ent_h046"][s][i]
        if seg["S"] < 0.25:
            x1 = px + i * 20 * BT
            svg.append(f'<rect x="{x1:.1f}" y="{py}" width="{20 * BT:.1f}" '
                       f'height="{ph}" fill="#e06c9f" opacity="0.07"/>')
    # target steps
    pts = []
    for i, f in enumerate((0.7, 1.4, 0.7)):
        pts.append((px + i * 20 * BT, f))
        pts.append((px + (i + 1) * 20 * BT, f))
    d = " ".join(f"{x:.1f},{py + ph - (f - FY0) / (FYH - FY0) * ph:.1f}"
                 for x, f in pts)
    svg.append(f'<polyline points="{d}" fill="none" stroke="#e0af68" '
               f'stroke-width="2" stroke-dasharray="5 4"/>')
    # volley ticks
    for t in (20, 40):
        x = px + t * BT
        svg.append(f'<line x1="{x:.1f}" y1="{py}" x2="{x:.1f}" y2="{py + ph}" '
                   f'stroke="#e06c9f" stroke-width="1.5" stroke-dasharray="2 2" '
                   f'opacity="0.7"/>')
    # arm curves
    for arm in ("free", "ent", "ent_h110", "ent_h046"):
        col, dash = COL[arm]
        bl = r["blocks"][arm][s]
        pts = [(px + (x["b"] * 5 + 2.5) * BT,
                py + ph - (min(max(x["f"], FY0), FYH) - FY0) / (FYH - FY0) * ph)
               for x in bl]
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        wd = 3 if arm == "ent_h046" else 2
        svg.append(f'<polyline points="{d}" fill="none" stroke="{col}" '
                   f'stroke-width="{wd}" stroke-dasharray="{dash}"/>')
    svg.append(f'<line x1="{px}" y1="{py + ph}" x2="{px + pw}" y2="{py + ph}" '
               f'stroke="#4b5563" stroke-width="1"/>')
    for t in (0, 20, 40, 60):
        svg.append(f'<text x="{px + t * BT:.1f}" y="{py + ph + 16}" fill="#6b7280" '
                   f'text-anchor="middle" font-size="11">{t}s</text>')
svg.append(f'<text x="14" y="{H * 3 + LGH - 6}" fill="#8a8f98" font-size="11" '
           f'transform="rotate(-90 14 {H * 3 + LGH - 6})">gait frequency (Hz)</text>')
# legend (bottom, clear of panels)
lx, ly = PADX + 8, H * 3 + 6
svg.append(f'<rect x="{lx}" y="{ly}" width="440" height="{LGH - 12}" '
           f'fill="#111318" opacity="0.92" stroke="#2a2e3a"/>')
svg.append(f'<text x="{lx + 8}" y="{ly + 16}" fill="#e0af68" font-size="11">'
           f'dashed gold = target 0.7→1.4→0.7 Hz; pink dotted verticals = hop volleys; '
           f'pink shade = S(Tr)&lt;0.25 segment</text>')
for i, arm in enumerate(("free", "ent", "ent_h046", "ent_h110")):
    col, dash = COL[arm]
    yy = ly + 32 + i * 13
    svg.append(f'<line x1="{lx + 8}" y1="{yy}" x2="{lx + 40}" y2="{yy}" '
               f'stroke="{col}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{lx + 46}" y="{yy + 4}" fill="#c0caf5" font-size="11">'
               f'{LBL[arm]}</text>')
svg.append("</svg>")
open("l39/ctrl.svg", "w").write("\n".join(svg))
import subprocess
subprocess.run(["rsvg-convert", "-w", "1880", "l39/ctrl.svg", "-o", "l39/ctrl.png"],
               check=True)
print("wrote l39/ctrl.png")
