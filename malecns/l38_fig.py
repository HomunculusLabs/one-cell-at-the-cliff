"""L38 figure: dose-response (amp -> df_Ti) for the tested channels + the
negative-side S(Tr) survival panel. House style: dark bg, dash patterns per
channel, per-seed dots, median line; dm==0 arms marked as no-entry."""
import json

import numpy as np

res = json.load(open("l38/results_l38.json"))
spot = res["spot"]

W, H = 980, 600
ML, MR, MT, MB = 78, 26, 66, 100
GAP = 60
PW = (W - ML - MR - GAP) / 2
PH = H - MT - MB

# panel A: amp in [-0.9, 0.9]; panel B: |amp| log 1..12
ax0, ax1 = -0.95, 0.95
bx0, bx1 = 0.8, 14.0
ymin, ymax = -2.2, 3.8


def XA(a):
    return ML + (a - ax0) / (ax1 - ax0) * PW


def XB(a):
    x0, x1 = np.log10(bx0), np.log10(bx1)
    return ML + PW + GAP + (np.log10(a) - x0) / (x1 - x0) * PW


def Y(v):
    return MT + (ymax - v) / (ymax - ymin) * PH


COL = {"DNge046_L": "#2ca02c", "DNge046_R": "#9467bd", "DNg110": "#e8c268",
       "MDN": "#1f77b4", "DNg88": "#d62728"}
DASH = {"DNge046_L": "2 5", "DNge046_R": "9 5", "DNg110": "",
        "MDN": "9 5", "DNg88": "2 5"}

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="#14161c"/>']
svg.append(f'<text x="{ML}" y="{MT-36}" fill="#e8e8f0" font-size="16" '
           f'font-weight="bold">A  dose&#8211;response: amp &#8594; &#916;f(Ti)</text>')
svg.append(f'<text x="{ML}" y="{MT-16}" fill="#9aa3b5" font-size="12.5" '
           f'>per-seed dots + median; &#215; = no entry (dm=0)</text>')
svg.append(f'<text x="{ML+PW+GAP}" y="{MT-36}" fill="#e8e8f0" font-size="16" '
           f'font-weight="bold">B  negative drive on pinned types</text>')
svg.append(f'<text x="{ML+PW+GAP}" y="{MT-16}" fill="#9aa3b5" font-size="12.5" '
           f'>S(Tr) survival vs amp magnitude</text>')

# grid + axes both panels
for v in (-2, -1, 0, 1, 2, 3):
    svg.append(f'<line x1="{ML}" y1="{Y(v):.1f}" x2="{ML+2*PW+GAP}" '
               f'y2="{Y(v):.1f}" stroke="#2a2e3a" stroke-width="1"/>')
    svg.append(f'<text x="{ML-10}" y="{Y(v)+4:.1f}" fill="#9aa3b5" '
               f'font-size="13" text-anchor="end">{v:+d}</text>')
for a in (-0.8, -0.4, -0.2, 0.2, 0.4, 0.8):
    svg.append(f'<line x1="{XA(a):.1f}" y1="{MT}" x2="{XA(a):.1f}" '
               f'y2="{MT+PH}" stroke="#2a2e3a" stroke-width="1"/>')
    svg.append(f'<text x="{XA(a):.1f}" y="{MT+PH+22}" fill="#9aa3b5" '
               f'font-size="13" text-anchor="middle">{a:+.1f}</text>')
svg.append(f'<line x1="{ML}" y1="{Y(0):.1f}" x2="{ML+PW}" y2="{Y(0):.1f}" '
           f'stroke="#4a5068" stroke-width="1.4"/>')
for a in (1, 2, 4, 8, 12):
    svg.append(f'<line x1="{XB(a):.1f}" y1="{MT}" x2="{XB(a):.1f}" '
               f'y2="{MT+PH}" stroke="#2a2e3a" stroke-width="1"/>')
    svg.append(f'<text x="{XB(a):.1f}" y="{MT+PH+22}" fill="#9aa3b5" '
               f'font-size="13" text-anchor="middle">{a:g}</text>')
svg.append(f'<text x="{ML+PW/2:.0f}" y="{MT+PH+46}" fill="#9aa3b5" '
           f'font-size="14" text-anchor="middle">tonic amp (signed)</text>')
svg.append(f'<text x="{ML+PW+GAP+PW/2:.0f}" y="{MT+PH+46}" fill="#9aa3b5" '
           f'font-size="14" text-anchor="middle">negative amp magnitude (log)</text>')
svg.append(f'<text x="26" y="{MT+PH/2:.0f}" fill="#9aa3b5" font-size="14" '
           f'transform="rotate(-90 26 {MT+PH/2:.0f})" text-anchor="middle">'
           f'&#916;f(Ti) Hz (A)  /  S(Tr) (B)</text>')

# ---- panel A: channels
AMP_A = [-0.8, -0.4, -0.2, 0.2, 0.4, 0.8]
for ch in ("DNge046_L", "DNge046_R", "DNg110"):
    meds, alive = [], []
    for a in AMP_A:
        ms = spot[f"{ch}@{a}"]
        dfs = [m["f_Ti_a"] - m["f_Ti_c"] for m in ms]
        ent = any(m["dm_max"] > 0 for m in ms)
        meds.append(float(np.median(dfs)))
        alive.append(ent)
        for i, d in enumerate(dfs):
            if not ent:
                continue  # flat-zero arms drawn as x at 0
            dx = (i - 1) * 7
            svg.append(f'<circle cx="{XA(a)+dx:.1f}" cy="{Y(d):.1f}" r="4.2" '
                       f'fill="{COL[ch]}" opacity="0.75"/>')
        if not ent:
            svg.append(f'<text x="{XA(a):.1f}" y="{Y(0)-8:.1f}" fill="{COL[ch]}" '
                       f'font-size="15" text-anchor="middle" font-weight="bold">&#215;</text>')
    pts = " ".join(f"{XA(a):.1f},{Y(m):.1f}" for a, m in zip(AMP_A, meds))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{COL[ch]}" '
               f'stroke-width="2" stroke-dasharray="{DASH[ch]}"/>')

# ---- panel B: MDN / DNg88 S(Tr) survival + control band
ctrl_lo = min(min(m["STr_c"] for m in spot[f"MDN@{a}"]) for a in (-1.0, -2.0, -4.0, -8.0))
ctrl_hi = max(max(m["STr_c"] for m in spot[f"MDN@{a}"]) for a in (-1.0, -2.0, -4.0, -8.0))
yminB, ymaxB = -0.06, 1.0


def YB(v):
    return MT + (ymaxB - v) / (ymaxB - yminB) * PH


for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    svg.append(f'<text x="{W-8}" y="{YB(v)+4:.1f}" fill="#9aa3b5" font-size="12" '
               f'text-anchor="end">{v:.2f}</text>')
for ch, amps in (("MDN", (-1.0, -2.0, -4.0, -8.0)), ("DNg88", (-2.0, -4.0, -8.0, -12.0))):
    meds, dots = [], []
    for a in amps:
        ms = spot[f"{ch}@{a}"]
        ent = any(m["dm_max"] > 0 for m in ms)
        ss = [m["STr_a"] for m in ms]
        meds.append(float(np.median(ss)))
        dots.append((a, ss, ent))
    pts = " ".join(f"{XB(-a):.1f},{YB(m):.1f}" for (a, m) in zip(amps, meds))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{COL[ch]}" '
               f'stroke-width="2" stroke-dasharray="{DASH[ch]}"/>')
    for a, ss, ent in dots:
        for i, s_ in enumerate(ss):
            dx = (i - 1) * 7
            svg.append(f'<circle cx="{XB(-a)+dx:.1f}" cy="{YB(s_):.1f}" r="4.2" '
                       f'fill="{COL[ch]}" opacity="0.75"/>')
        if not ent:
            svg.append(f'<text x="{XB(-a):.1f}" y="{YB(ss[0])-10:.1f}" fill="{COL[ch]}" '
                       f'font-size="15" text-anchor="middle" font-weight="bold">&#215;</text>')
# control S band (panel-B local scale)
svg.append(f'<rect x="{ML+PW+GAP}" y="{YB(ctrl_hi):.1f}" width="{PW}" '
           f'height="{YB(ctrl_lo)-YB(ctrl_hi):.1f}" fill="#7aa" opacity="0.14"/>')
svg.append(f'<text x="{ML+PW+GAP+8}" y="{YB(ctrl_hi)-6:.1f}" fill="#8fb" '
           f'font-size="12">control S(Tr) {ctrl_lo:.2f}&#8211;{ctrl_hi:.2f}</text>')

# legend, split per panel, in upper area
lx, ly = ML + 14, MT + 26
for i, ch in enumerate(("DNge046_L", "DNge046_R", "DNg110")):
    y = ly + i * 20
    lab = {"DNge046_L": "DNge046 L side (1 free cell)",
           "DNge046_R": "DNge046 R side (2 pinned cells)",
           "DNg110": "DNg110 whole type (6 cells)"}[ch]
    svg.append(f'<line x1="{lx}" y1="{y-4}" x2="{lx+30}" y2="{y-4}" '
               f'stroke="{COL[ch]}" stroke-width="2" stroke-dasharray="{DASH[ch]}"/>')
    svg.append(f'<circle cx="{lx+15}" cy="{y-4}" r="3.5" fill="{COL[ch]}" opacity="0.75"/>')
    svg.append(f'<text x="{lx+38}" y="{y}" fill="#c8cede" font-size="12.5">{lab}</text>')
lx2 = ML + PW + GAP + 14
for i, ch in enumerate(("MDN", "DNg88")):
    y = ly + i * 20
    lab = {"MDN": "MDN (pinned, neg drive)",
           "DNg88": "DNg88 (pinned, neg drive)"}[ch]
    svg.append(f'<line x1="{lx2}" y1="{y-4}" x2="{lx2+30}" y2="{y-4}" '
               f'stroke="{COL[ch]}" stroke-width="2" stroke-dasharray="{DASH[ch]}"/>')
    svg.append(f'<circle cx="{lx2+15}" cy="{y-4}" r="3.5" fill="{COL[ch]}" opacity="0.75"/>')
    svg.append(f'<text x="{lx2+38}" y="{y}" fill="#c8cede" font-size="12.5">{lab}</text>')
svg.append(f'<text x="{ML}" y="{H-14}" fill="#778" font-size="12">'
           f'L38: substrate L32 (g .01 / beta 2); df vs same-seed paired control, '
           f'last-45s window; flat-zero arms are bit-identical (no entry)</text>')
svg.append("</svg>")
open("l38/dose.svg", "w").write("\n".join(svg))
import subprocess
subprocess.run(["rsvg-convert", "-o", "l38/dose.png", "l38/dose.svg"], check=True)
print("wrote l38/dose.svg + dose.png")
