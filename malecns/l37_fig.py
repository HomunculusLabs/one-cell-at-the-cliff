"""L37 figure: dose-response of turn (L/R flexor mass asymmetry) vs tonic
amp for the three viable channels + base band + random-pair nulls."""
import json

import numpy as np

res = json.load(open("l37/results_l37.json"))
base = [res["arms"]["base"]["seeds"][i]["base"]["turn"]["Tif"] for i in range(3)]
bm = float(np.mean(base))
bsd = float(np.std(base))
AMPS = [0.05, 0.2, 0.8]
CHANNELS = ["DNge059", "DNg105", "DNge046"]

W, H = 860, 560
ML, MR, MT, MB = 78, 30, 64, 76
PW, PH = W - ML - MR, H - MT - MB
xmin, xmax, ymin, ymax = -0.72, 1.02, -0.30, 0.14


def X(a):
    return ML + (a - xmin) / (xmax - xmin) * PW


def Y(v):
    return MT + (ymax - v) / (ymax - ymin) * PH


COL = {"DNge059": "#d62728", "DNg105": "#1f77b4", "DNge046": "#2ca02c"}
# dash patterns distinguish channels beyond hue (house style)
DASH = {"DNge059": "", "DNg105": "9 5", "DNge046": "2 5"}

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="#14161c"/>']
# grid + axes
for i in range(-30, 15, 10):
    v = i / 100
    if ymin <= v <= ymax:
        svg.append(f'<line x1="{ML}" y1="{Y(v):.1f}" x2="{ML+PW}" y2="{Y(v):.1f}" '
                   f'stroke="#2a2e3a" stroke-width="1"/>')
        svg.append(f'<text x="{ML-10}" y="{Y(v)+4:.1f}" fill="#9aa3b5" font-size="13" '
                   f'text-anchor="end">{v:+.2f}</text>')
for a in (-0.6, -0.2, 0.2, 0.6, 0.8):
    svg.append(f'<line x1="{X(a):.1f}" y1="{MT}" x2="{X(a):.1f}" y2="{MT+PH}" '
               f'stroke="#2a2e3a" stroke-width="1"/>')
    lab = {0.2: "0.05", 0.6: "0.2", 0.8: "0.8"}.get(a)
    if lab:
        svg.append(f'<text x="{X(a):.1f}" y="{MT+PH+24}" fill="#9aa3b5" font-size="13" '
                   f'text-anchor="middle">{lab}</text>')
# base band (wiring-set asymmetry +- sd)
svg.append(f'<rect x="{ML}" y="{Y(bm+bsd):.1f}" width="{PW}" '
           f'height="{Y(bm-bsd)-Y(bm+bsd):.1f}" fill="#e8c268" opacity="0.13"/>')
svg.append(f'<line x1="{ML}" y1="{Y(bm):.1f}" x2="{ML+PW}" y2="{Y(bm):.1f}" '
           f'stroke="#e8c268" stroke-width="1.4" stroke-dasharray="3 4" opacity="0.8"/>')
svg.append(f'<text x="{ML+6}" y="{Y(bm+bsd)-6:.1f}" fill="#e8c268" font-size="12">'
           f'base (no steer) {bm:+.2f}&#177;{bsd:.2f}</text>')


def shift(name):
    a = res["arms"][name]
    return [p["steer"]["turn"]["Tif"] - res["arms"]["base"]["seeds"][i]["base"]["turn"]["Tif"]
            for i, p in enumerate(a["seeds"])]


for ct in CHANNELS:
    pts = [(a, shift(f"{ct}_Lx{a}")) for a in AMPS]
    # ladder position: spread the three amps for readability (annotated axis)
    xa = {0.05: 0.2, 0.2: 0.6, 0.8: 0.8}
    means = [float(np.mean(v)) for _, v in pts]
    path = " ".join(f"{X(xa[a]):.1f},{Y(m):.1f}" for a, m in zip(AMPS, means))
    svg.append(f'<polyline points="{path}" fill="none" stroke="{COL[ct]}" '
               f'stroke-width="2.6" stroke-dasharray="{DASH[ct]}"/>')
    for (a, v), m in zip(pts, means):
        for vi in v:
            svg.append(f'<circle cx="{X(xa[a]):.1f}" cy="{Y(vi):.1f}" r="3.4" '
                       f'fill="{COL[ct]}" opacity="0.55"/>')
        svg.append(f'<circle cx="{X(xa[a]):.1f}" cy="{Y(m):.1f}" r="5.2" '
                   f'fill="{COL[ct]}"/>')
# R-side mirror control at 0.8 (open diamonds) + nulls (grey X)
for ct in CHANNELS:
    v = shift(f"{ct}_Rx0.8")
    m = float(np.mean(v))
    svg.append(f'<path d="M {X(0.92)-6:.1f} {Y(m):.1f} L {X(0.92):.1f} {Y(m)-7:.1f} '
               f'L {X(0.92)+6:.1f} {Y(m):.1f} L {X(0.92):.1f} {Y(m)+7:.1f} Z" '
               f'fill="none" stroke="{COL[ct]}" stroke-width="2.2"/>')
for dr in range(2):
    v = shift(f"rand{dr}")
    for vi in v:
        svg.append(f'<text x="{X(0.92):.1f}" y="{Y(vi)+5:.1f}" fill="#8b93a7" '
                   f'font-size="17" text-anchor="middle">&#215;</text>')
svg.append(f'<text x="{X(0.92):.1f}" y="{MT-8}" fill="#9aa3b5" font-size="12" '
           f'text-anchor="middle">R-side ctl / nulls</text>')

leg = [("DNge059 (ipsi)", COL["DNge059"], DASH["DNge059"]),
       ("DNg105 (crossed, inh)", COL["DNg105"], DASH["DNg105"]),
       ("DNge046 (crossed)", COL["DNge046"], DASH["DNge046"])]
for i, (t, c, d) in enumerate(leg):
    y = MT + 18 + i * 22
    svg.append(f'<line x1="{ML+14}" y1="{y}" x2="{ML+52}" y2="{y}" stroke="{c}" '
               f'stroke-width="2.6" stroke-dasharray="{d}"/>')
    svg.append(f'<text x="{ML+60}" y="{y+4}" fill="#c8cedb" font-size="13">{t}</text>')
svg.append(f'<text x="{W/2}" y="{H-14}" fill="#c8cedb" font-size="15" '
           f'text-anchor="middle">unilateral tonic amp (L-side drive; R-side ctl open diamond at 0.8)</text>')
svg.append(f'<text x="22" y="{H/2}" fill="#c8cedb" font-size="15" '
           f'transform="rotate(-90 22 {H/2})">turn shift &#916; (L&#8722;R)/(L+R) flexor mass</text>')
svg.append(f'<text x="{W/2}" y="30" fill="#e6ebf5" font-size="17" '
           f'text-anchor="middle">L37 &#8212; tonic-bias steering on viable DN channels</text>')
svg.append("</svg>")
open("l37/steer.svg", "w").write("\n".join(svg))
print("wrote l37/steer.svg")
