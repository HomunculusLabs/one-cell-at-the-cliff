"""L37 figure v2: dose-response of turn SHIFT (vs paired base) vs tonic amp.
Dodged x per channel; base reference = 0 shift (paired lockstep)."""
import json

import numpy as np

res = json.load(open("l37/results_l37.json"))
AMPS = [0.05, 0.2, 0.8]
CHANNELS = ["DNge059", "DNg105", "DNge046"]

W, H = 880, 560
ML, MR, MT, MB = 78, 40, 70, 76
PW, PH = W - ML - MR, H - MT - MB
xmin, xmax, ymin, ymax = 0.0, 1.12, -0.30, 0.12
xa = {0.05: 0.16, 0.2: 0.46, 0.8: 0.78}
DODGE = {"DNge059": -0.035, "DNg105": 0.0, "DNge046": 0.035}


def X(v):
    return ML + (v - xmin) / (xmax - xmin) * PW


def Y(v):
    return MT + (ymax - v) / (ymax - ymin) * PH


COL = {"DNge059": "#e8604c", "DNg105": "#5ba3e0", "DNge046": "#63c96a"}
DASH = {"DNge059": "", "DNg105": "9 5", "DNge046": "2 5"}

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="#14161c"/>']
for i in range(-30, 15, 10):
    v = i / 100
    svg.append(f'<line x1="{ML}" y1="{Y(v):.1f}" x2="{ML+PW}" y2="{Y(v):.1f}" '
               f'stroke="#2a2e3a" stroke-width="1"/>')
    svg.append(f'<text x="{ML-10}" y="{Y(v)+4:.1f}" fill="#9aa3b5" font-size="13" '
               f'text-anchor="end">{v:+.1f}</text>')
for a in AMPS:
    svg.append(f'<line x1="{X(xa[a]):.1f}" y1="{MT}" x2="{X(xa[a]):.1f}" y2="{MT+PH}" '
               f'stroke="#232734" stroke-width="1"/>')
    svg.append(f'<text x="{X(xa[a]):.1f}" y="{MT+PH+24}" fill="#9aa3b5" font-size="13" '
               f'text-anchor="middle">{a}</text>')
# base reference: paired lockstep -> a no-steer arm has shift exactly 0
svg.append(f'<line x1="{ML}" y1="{Y(0):.1f}" x2="{ML+PW}" y2="{Y(0):.1f}" '
           f'stroke="#e8c268" stroke-width="1.6" stroke-dasharray="3 4" opacity="0.85"/>')

# steering gate line at +0.15 (just above range: draw at clip edge, label)
svg.append(f'<text x="{ML+10}" y="{MT+16}" fill="#b06a6a" font-size="11" '
           f'text-anchor="start">PREREG steering gate (+0.15, off-scale) &#8212; every channel flat</text>')


def shift(name):
    a = res["arms"][name]
    return [p["steer"]["turn"]["Tif"] - res["arms"]["base"]["seeds"][i]["base"]["turn"]["Tif"]
            for i, p in enumerate(a["seeds"])]


for ct in CHANNELS:
    xs = [xa[a] + DODGE[ct] for a in AMPS]
    means = [float(np.mean(shift(f"{ct}_Lx{a}"))) for a in AMPS]
    path = " ".join(f"{X(x):.1f},{Y(m):.1f}" for x, m in zip(xs, means))
    svg.append(f'<polyline points="{path}" fill="none" stroke="{COL[ct]}" '
               f'stroke-width="2.6" stroke-dasharray="{DASH[ct]}"/>')
    for x, a in zip(xs, AMPS):
        for vi in shift(f"{ct}_Lx{a}"):
            svg.append(f'<circle cx="{X(x):.1f}" cy="{Y(vi):.1f}" r="3.4" '
                       f'fill="{COL[ct]}" opacity="0.5"/>')
        svg.append(f'<circle cx="{X(x):.1f}" '
                   f'cy="{Y(float(np.mean(shift(f"{ct}_Lx{a}")))):.1f}" '
                   f'r="5.4" fill="{COL[ct]}"/>')
for ct in CHANNELS:
    v = shift(f"{ct}_Rx0.8")
    m = float(np.mean(v))
    x = 0.95 + DODGE[ct]
    svg.append(f'<path d="M {X(x)-6:.1f} {Y(m):.1f} L {X(x):.1f} {Y(m)-7:.1f} '
               f'L {X(x)+6:.1f} {Y(m):.1f} L {X(x):.1f} {Y(m)+7:.1f} Z" '
               f'fill="none" stroke="{COL[ct]}" stroke-width="3.0"/>')
    for vi in v:
        svg.append(f'<circle cx="{X(x):.1f}" cy="{Y(vi):.1f}" r="3.0" '
                   f'fill="none" stroke="{COL[ct]}" stroke-width="1.6" opacity="0.7"/>')
for dr in range(2):
    v = shift(f"rand{dr}")
    for vi in v:
        svg.append(f'<text x="{X(1.06):.1f}" y="{Y(vi)+6:.1f}" fill="#a7adc0" '
                   f'font-size="20" text-anchor="middle">&#215;</text>')
svg.append(f'<text x="{X(0.95):.1f}" y="{MT+30}" fill="#9aa3b5" font-size="12" '
           f'text-anchor="middle">R-side ctl (0.8)</text>')
svg.append(f'<text x="{X(1.06):.1f}" y="{MT+30}" fill="#a7adc0" font-size="12" '
           f'text-anchor="middle">random pairs</text>')

leg = [("paired base (shift = 0)", "#e8c268", "3 4"),
       ("DNge059 L (ipsi, exc)", COL["DNge059"], DASH["DNge059"]),
       ("DNg105 L (crossed, inh)", COL["DNg105"], DASH["DNg105"]),
       ("DNge046 L (crossed)", COL["DNge046"], DASH["DNge046"])]
lx = ML
for t, c, d in leg:
    svg.append(f'<line x1="{lx}" y1="52" x2="{lx+34}" y2="52" stroke="{c}" '
               f'stroke-width="2.8" stroke-dasharray="{d}"/>')
    svg.append(f'<circle cx="{lx+17}" cy="52" r="4.4" fill="{c}" '
               f'stroke="none" opacity="{1.0 if c == COL.get("DNge059") else 0.0}"/>')
    svg.append(f'<text x="{lx+40}" y="56" fill="#c8cedb" font-size="13">{t}</text>')
    lx += 46 + int(len(t) * 7.1)
svg.append(f'<text x="{ML+4}" y="{MT+PH-8}" fill="#8b93a7" font-size="12">'
           f'&#215; nulls at 0.8: rand0 breaks antiphase (S(Tr) &#8722;0.22); channels preserve it (S(Tr) &#8805; 0.38)</text>')
svg.append(f'<text x="{W/2}" y="{H-14}" fill="#c8cedb" font-size="15" '
           f'text-anchor="middle">unilateral tonic amp on L-side cells (R-side mirror ctl at 0.8)</text>')
svg.append(f'<text x="22" y="{H/2}" fill="#c8cedb" font-size="15" '
           f'transform="rotate(-90 22 {H/2})">turn shift &#916; (L&#8722;R)/(L+R) Ti+Tr flexor mass</text>')
svg.append(f'<text x="{W/2}" y="32" fill="#e6ebf5" font-size="17" '
           f'text-anchor="middle">L37 &#8212; tonic-bias steering on viable DN channels: flat</text>')
svg.append("</svg>")
open("l37/steer.svg", "w").write("\n".join(svg))
print("wrote l37/steer.svg")
