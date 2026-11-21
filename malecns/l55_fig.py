"""L55 figure: (A) pooled duty per arm x seed, gate .5 — every policy drops
exactly one seed below .5, a different seed each time; (B) fast-window duty:
the ENTRY hop alone sets it (identical .22/.8/.213 without, .133/.627/.0
with = P3 cost on 3/3); (C) seg2 re-roll: any hop redraws the downstream
attractor lottery (entry hop at k=2000 moves seg2 20 s later); (D) cond
record: never fired — in-flight lock err .0002-.001 << THR .05 (the variance
is structural, not tracking). SVG -> rsvg-convert. Numbers from artifacts."""
import json
import subprocess

import numpy as np

SEEDS = [11, 22, 33]
ARMS = ["hynohop", "cond", "hop2k", "hop4k", "hybrid"]
LABEL = {"hynohop": "no hop", "cond": "cond (never fired \u2261 no hop)",
         "hop2k": "entry hop", "hop4k": "exit hop", "hybrid": "both hops"}
res = json.load(open("l55/results_l55.json"))
f = res["factorial"]
W, H = 1560, 900
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
ARM_COL = {"hynohop": "#8fd9d9", "cond": "#c9c9c9", "hop2k": "#8fd98f",
           "hop4k": "#d98fc6", "hybrid": "#ff8f8f"}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L55 hop scheduling: no policy owns the pooled gate &#8212; the '
       f'attractor lottery does</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">2x2 hop factorial '
       f'(+ conditional policy) on the hybrid AMPA schedule; hops = DNge046_L '
       f'volley .5 for 40 steps; duty = both S sides &#8805; .25 (rolling '
       f'5 s); seeds 11/22/33; drive-on 48 s every arm</text>']


def dots_panel(px, py, pw, ph, title, key, ylab, ylim=(0.0, 1.0)):
    svg.append(f'<text x="{px}" y="{py-16}" fill="{FG}" font-size="16" '
               f'font-weight="bold">{title}</text>')

    def X(i):
        return px + 60 + (pw - 90) * i / (len(ARMS) - 1)

    def Y(v):
        return py + (ph - 46) * (1 - (v - ylim[0]) / (ylim[1] - ylim[0]))

    svg.append(f'<rect x="{px+60}" y="{py}" width="{pw-90}" '
               f'height="{ph-46}" fill="none" stroke="{GRID}"/>')
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        dash = '5 3' if abs(v - 0.5) < 1e-9 else '2 4'
        svg.append(f'<line x1="{px+60}" y1="{Y(v):.1f}" x2="{px+pw-30}" '
                   f'y2="{Y(v):.1f}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
        svg.append(f'<text x="{px+54}" y="{Y(v)+4:.1f}" fill="{MUT}" '
                   f'font-size="12" text-anchor="end">{v:.2f}</text>')
    svg.append(f'<text x="{px+14}" y="{py+(ph-46)/2}" fill="{MUT}" '
               f'font-size="13" transform="rotate(-90 {px+14} '
               f'{py+(ph-46)/2})">{ylab}</text>')
    for i, a in enumerate(ARMS):
        vals = f[a][key]
        for s, v in zip(SEEDS, vals):
            svg.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="6" '
                       f'fill="{SEED_COL[s]}" fill-opacity="0.75" '
                       f'stroke="{ARM_COL[a]}" stroke-width="2"/>')
        mv = float(np.mean(vals))
        svg.append(f'<rect x="{X(i)-7:.1f}" y="{Y(mv)-7:.1f}" width="14" '
                   f'height="14" fill="none" stroke="{ARM_COL[a]}" '
                   f'stroke-width="2.5"/>')
        svg.append(f'<text x="{X(i)+13:.1f}" y="{Y(mv)+4:.1f}" '
                   f'fill="{ARM_COL[a]}" font-size="12">{mv:.3f}</text>')
    for i, a in enumerate(ARMS):
        svg.append(f'<text x="{X(i):.1f}" y="{py+ph-24}" fill="{MUT}" '
                   f'font-size="12" text-anchor="middle">{LABEL[a]}</text>')
        if i < len(ARMS) - 1:
            svg.append(f'<line x1="{X(i)+28:.1f}" y1="{py+8}" '
                       f'x2="{X(i+1)-28:.1f}" y2="{py+8}" stroke="{GRID}"/>')


# ---------- panel A: pooled duty ----------
dots_panel(60, 120, 700, 330, "A &#8226; pooled duty (gate .5 dashed; "
            "square = mean)", "pooled", "pooled bilateral duty")
nb = [sum(1 for v in f[a]["pooled"] if v >= .5) for a in ARMS]
svg.append(f'<text x="120" y="470" fill="{MUT}" font-size="13">seeds at '
           f'&#8805; .5: ' + " | ".join(
               f'{LABEL[a].split(" ")[0]} {n}/3' for a, n in zip(ARMS, nb))
           + ' &#8212; each single-hop policy drops exactly one seed, '
           'never the same one; both-hops drops two</text>')

# ---------- panel B: fast-window duty ----------
dots_panel(820, 120, 700, 330, "B &#8226; fast-window (1.4 Hz) duty &#8212; "
            "entry hop alone sets it", "seg1", "fast-window duty")

# ---------- panel C: seg2 re-roll ----------
dots_panel(60, 540, 700, 330, "C &#8226; seg2 (0.7 Hz) duty &#8212; any hop "
            "re-rolls the downstream lottery", "seg2", "seg2 duty")

# ---------- panel D: which seed fails + cond record ----------
px, py, pw, ph = 820, 540, 700, 330
svg.append(f'<text x="{px}" y="{py-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">D &#8226; gate matrix + conditional record'
           f'</text>')
cw, ch = 163, 52
ROWLBL = {"hynohop": "no hop", "cond": "cond (never fired)",
          "hop2k": "entry hop", "hop4k": "exit hop", "hybrid": "both hops"}
for i, a in enumerate(ARMS):
    yy = py + 40 + i * ch
    svg.append(f'<text x="{px+8}" y="{yy+33}" fill="{ARM_COL[a]}" '
               f'font-size="14">{ROWLBL[a]}</text>')
    for j, s in enumerate(SEEDS):
        xx = px + 208 + j * cw
        v = f[a]["pooled"][j]
        ok = v >= .5
        col = "#3f7d4f" if ok else "#8d4444"
        svg.append(f'<rect x="{xx}" y="{yy}" width="{cw-12}" height="{ch-10}" '
                   f'fill="{col}" fill-opacity="0.32" stroke="{col}" '
                   f'stroke-width="1.5"/>')
        svg.append(f'<text x="{xx+(cw-12)/2}" y="{yy+ch/2+2}" fill="{FG}" '
                   f'font-size="17" text-anchor="middle" '
                   f'font-weight="bold">{v:.3f} {"PASS" if ok else "MISS"}'
                   f'</text>')
        if i == 0:
            svg.append(f'<text x="{xx+(cw-12)/2}" y="{yy-10}" fill="{MUT}" '
                       f'font-size="12" text-anchor="middle">seed {s}</text>')
cr = res["verdict"]["cond_record"]
err_s = ", ".join(f"s{s} {cr[str(s)]['err']}" for s in SEEDS)
svg.append(f'<text x="{px+8}" y="{py+40+5*ch+18}" fill="{MUT}" '
           f'font-size="13">cond decision @ k=3000 (10 s into fast seg): '
           f'in-flight lock err {err_s} vs THR .05 &#8212; never fires'
           f'</text>')
svg.append(f'<text x="{px+8}" y="{py+40+5*ch+36}" fill="{MUT}" '
           f'font-size="13">nothing to trigger on: the miss is structural, '
           f'never tracking (ratios {cr["11"]["ratio"]:.0f}/'
           f'{cr["22"]["ratio"]:.0f}/{cr["33"]["ratio"]:.0f} = razor-locked)'
           f'</text>')

svg.append('</svg>')
out = "\n".join(svg)
open("l55/hop.svg", "w").write(out)

# analytic QA: no text outside canvas, no circle outside its panel box
import re
bad = []
for m in re.finditer(r'<text x="(\d+)" y="(\d+)"', out):
    if int(m.group(1)) > W - 10 or int(m.group(2)) > H - 6:
        bad.append(("text-overflow", m.group(0)))
for m in re.finditer(r'<circle cx="([\d.]+)" cy="([\d.]+)"', out):
    cx, cy = float(m.group(1)), float(m.group(2))
    if not (60 <= cx <= 1500 and 100 <= cy <= 880):
        bad.append(("circle-out", m.group(0)))
print("QA:", bad if bad else "clean (no overflow)")
subprocess.run(["rsvg-convert", "-o", "l55/hop.png", "l55/hop.svg"],
               check=True)
print("wrote l55/hop.png")
