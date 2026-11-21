"""L45a figure: (A) per-arm perturbation effect vs random-type bar,
(B) antagonist structure S_dur per seed, (C) mediator probe: X464 rescues E1.
Hand-built SVG (house style), rsvg-convert -> png. Data: l45 JSONs only."""
import json

import numpy as np

d = json.load(open("l45/results_l45a.json"))
pr = json.load(open("l45/results_l45a_probe.json"))
SEEDS = ["11", "22", "33"]
rnd_bar = d["verdict"]["C3_rank"]["rnd_bar"]
ORDER = ["c_E1", "c_core3all", "c_X464", "c_E1T1", "c_coreT1", "c_E2",
         "c_coreAll", "c_I1", "c_E3", "c_I2", "rnd1", "rnd2", "rnd3"]
LABEL = {"c_E1": "E1\nIN17A001", "c_E2": "E2\nINXXX466", "c_I1": "I1\nIN16B036",
         "c_I2": "I2\nIN19A007", "c_E3": "E3\nIN19B012", "c_X464": "X464\nINXXX464",
         "c_core3all": "E1+E2+I1", "c_coreAll": "ALL 36", "c_E1T1": "E1@T1",
         "c_coreT1": "core@T1", "rnd1": "rnd1", "rnd2": "rnd2", "rnd3": "rnd3"}
W, H = 1560, 600
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_STYLE = {"11": ("#7fd4ff", "none"), "22": ("#ffb37f", "6 4"),
              "33": ("#b39dff", "2 3")}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="42" fill="{FG}" font-size="25" font-weight="bold">'
       f'L45a pruning screen: no 6- or 36-cell core owns the rhythm&#8217;s existence &#8212; but E1&#8594;X464 owns its structure</text>',
       f'<text x="40" y="68" fill="{MUT}" font-size="14">'
       f'Pugliese-style type silencing (X=0 clamp, 50 s) on the frozen intrinsic regime; 3 seeds, one shared noise stream; '
   f'effect = max(|dS|, |df|, log-ratio-drop) vs the random-type bar ({rnd_bar:.2f})</text>']
PANES = [(50, 110, 480, 440), (560, 110, 480, 440), (1060, 110, 470, 440)]


def py(v, pane, ymin, ymax):
    y0, chh = pane[1], pane[3]
    return y0 + (chh - 46) * (1 - (v - ymin) / (ymax - ymin))


def frame(pane, title, ylab, ymin, ymax, yticks, fmt="{:+.2f}"):
    x0, y0, cw, chh = pane
    x1, y1 = x0 + cw, y0 + chh
    svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" font-weight="bold">{title}</text>')
    svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
               f'fill="none" stroke="{GRID}"/>')
    svg.append(f'<text x="{x0+6}" y="{y0+(chh-40)//2}" fill="{MUT}" font-size="13" '
               f'transform="rotate(-90 {x0+6} {y0+(chh-40)//2})" text-anchor="middle">{ylab}</text>')
    for tv in yticks:
        yy = y1 - 40 - (chh - 40) * (tv - ymin) / (ymax - ymin)
        svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x1-20}" y2="{yy:.1f}" '
                   f'stroke="{GRID}" stroke-dasharray="2 4" stroke-width="1"/>')
        svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="12" '
                   f'text-anchor="end">{fmt.format(tv)}</text>')


def bars_x(pane, i, n):
    x0, cw = pane[0], pane[2]
    step = (cw - 60) / n
    return x0 + 40 + step * (i + 0.5), step


# ---- Panel A: effect bars ----
p = PANES[0]
frame(p, "A. perturbation effect (median of 3 seeds)", "effect", 0, 1.0,
      [0, 0.25, 0.5, 0.75, 1.0], "{:.2f}")
yy = py(rnd_bar, p, 0, 1.0)
svg.append(f'<rect x="{p[0]+40}" y="{p[1]}" width="{p[2]-60}" height="{yy-p[1]:.1f}" '
           f'fill="#4a5568" fill-opacity="0.18"/>')
svg.append(f'<line x1="{p[0]+40}" y1="{yy:.1f}" x2="{p[0]+p[2]-20}" y2="{yy:.1f}" '
           f'stroke="#e0c555" stroke-width="2" stroke-dasharray="6 4"/>')
svg.append(f'<text x="{p[0]+44}" y="{yy-6:.1f}" fill="#e0c555" font-size="12">'
           f'random-type bar ({rnd_bar:.2f}) &#8212; below = indistinguishable from noise</text>')
for i, a in enumerate(ORDER):
    v = d["effects"][a]["med"]
    xc, step = bars_x(p, i, len(ORDER))
    bw = step * 0.52
    col = "#e07a5f" if v > 2 * rnd_bar else ("#5f87a8" if a.startswith("rnd") else "#6da28b")
    yv = py(v, p, 0, 1.0)
    svg.append(f'<rect x="{xc-bw/2:.1f}" y="{yv:.1f}" width="{bw:.1f}" '
               f'height="{py(0,p,0,1.0)-yv:.1f}" fill="{col}" rx="2"/>')
    svg.append(f'<text x="{xc:.1f}" y="{py(0,p,0,1.0)+14:.1f}" fill="{MUT}" font-size="10.5" '
               f'text-anchor="middle" transform="rotate(-38 {xc:.1f} {py(0,p,0,1.0)+14:.1f})">'
               f'{LABEL[a].replace(chr(10), " ")}</text>')
    if v > 2 * rnd_bar:
        svg.append(f'<text x="{xc:.1f}" y="{yv-5:.1f}" fill="{FG}" font-size="11" '
                   f'text-anchor="middle">{v:.2f}</text>')

# ---- Panel B: S_dur per seed ----
p = PANES[1]
frame(p, "B. antagonist structure S(Tr) while clamped", "S(Tr)", -0.8, 0.8,
      [-0.5, 0, 0.25, 0.5], "{:+.2f}")
yy = py(0, p, -0.8, 0.8)
svg.append(f'<line x1="{p[0]+40}" y1="{yy:.1f}" x2="{p[0]+p[2]-20}" y2="{yy:.1f}" '
           f'stroke="#e05555" stroke-width="1"/>')
for lo, hi, lab in ((0.44, 0.50, "base free-run .45-.49"),):
    y1, y2 = py(hi, p, -0.8, 0.8), py(lo, p, -0.8, 0.8)
    svg.append(f'<rect x="{p[0]+40}" y="{y1:.1f}" width="{p[2]-60}" height="{y2-y1:.1f}" '
               f'fill="#7fd4ff" fill-opacity="0.15"/>')
    svg.append(f'<text x="{p[0]+p[2]-24}" y="{y1-5:.1f}" fill="#7fd4ff" font-size="12" text-anchor="end">{lab}</text>')
meds = []
for i, a in enumerate(ORDER):
    xc, step = bars_x(p, i, len(ORDER))
    if a.startswith("rnd"):
        continue
    meds.append((a, xc))
    for s in SEEDS:
        col, dash = SEED_STYLE[s]
        v = d["table"][a][s]["S_dur"]
        svg.append(f'<circle cx="{xc:.1f}" cy="{py(v,p,-0.8,0.8):.1f}" r="6" fill="none" '
                   f'stroke="{col}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
    mv = float(np.median([d["table"][a][s]["S_dur"] for s in SEEDS]))
    svg.append(f'<line x1="{xc-8:.1f}" y1="{py(mv,p,-0.8,0.8):.1f}" x2="{xc+8:.1f}" '
               f'y2="{py(mv,p,-0.8,0.8):.1f}" stroke="{FG}" stroke-width="2.5"/>')
svg.append(f'<text x="{p[0]+(p[2]-20)//2+20}" y="{p[1]+p[3]-4}" fill="{MUT}" font-size="13" '
           f'text-anchor="middle">clamped type (seed dots 11/22/33, dash-coded; bar = median; rnd clouds omitted)</text>')

# ---- Panel C: mediator probe ----
p = PANES[2]
frame(p, "C. mediator probe: X464 clamp RESCUES the E1 clamp", "S(Tr)", -0.8, 0.8,
      [-0.5, 0, 0.25, 0.5], "{:+.2f}")
yy = py(0, p, -0.8, 0.8)
svg.append(f'<line x1="{p[0]+40}" y1="{yy:.1f}" x2="{p[0]+p[2]-20}" y2="{yy:.1f}" '
           f'stroke="#e05555" stroke-width="1"/>')
PARMS = ["base", "c_E1", "c_I2E3", "c_E1I2E3", "c_E1X464"]
PLAB = ["base", "E1", "I2+E3", "E1+I2+E3", "E1+X464"]
for i, (a, lab) in enumerate(zip(PARMS, PLAB)):
    xc, step = bars_x(p, i, len(PARMS))
    for s in SEEDS:
        col, dash = SEED_STYLE[s]
        v = pr[f"{a}_{s}"]["S_dur"]
        svg.append(f'<circle cx="{xc:.1f}" cy="{py(v,p,-0.8,0.8):.1f}" r="7" fill="none" '
                   f'stroke="{col}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
    mv = float(np.median([pr[f"{a}_{s}"]["S_dur"] for s in SEEDS]))
    svg.append(f'<line x1="{xc-9:.1f}" y1="{py(mv,p,-0.8,0.8):.1f}" x2="{xc+9:.1f}" '
               f'y2="{py(mv,p,-0.8,0.8):.1f}" stroke="{FG}" stroke-width="2.5"/>')
    svg.append(f'<text x="{xc:.1f}" y="{p[1]+p[3]-22}" fill="{MUT}" font-size="12" text-anchor="middle">{lab}</text>')
svg.append(f'<text x="{p[0]+(p[2]-20)//2+20}" y="{p[1]+p[3]-4}" fill="{MUT}" font-size="13" '
           f'text-anchor="middle">joint clamps (E1+X464 restores S AND f 1.25-1.48 Hz; E1+I2+E3 does not)</text>')

svg.append("</svg>")
open("l45/prune.svg", "w").write("\n".join(svg))
import subprocess
subprocess.run(["rsvg-convert", "-o", "l45/prune.png", "l45/prune.svg"], check=True)
print("wrote l45/prune.png")
