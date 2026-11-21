"""L36 figure v3: two-sided viability map. x = u_max (clip [-2,5]), y = mean X.
Horizontal legend strip above the plot; kill zones shaded; family shapes."""
import numpy as np
import pandas as pd

c = pd.read_csv("l36/census_l36.csv")
fam = c[c.family.isin(["flex", "ext", "jump"])].copy()

W, H = 1000, 660
ML, MR, MT, MB = 78, 40, 104, 100
PW, PH = W - ML - MR, H - MT - MB
X0, X1 = -2.0, 5.0
Y0, Y1 = -0.03, 1.06


def px(v):
    v = max(X0, min(X1, v))
    return ML + (v - X0) / (X1 - X0) * PW


def py(v):
    return MT + (1 - (v - Y0) / (Y1 - Y0)) * PH


s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="DejaVu Sans, sans-serif">')
s.append(f'<rect width="{W}" height="{H}" fill="#14161c"/>')
s.append(f'<text x="{ML}" y="34" fill="#e8e4da" font-size="21" '
         f'font-weight="bold">L36 — DN drive-channel viability under the cord-rhythm regime</text>')
s.append(f'<text x="{ML}" y="56" fill="#9aa3b2" font-size="13">'
         f'u = W&#183;X&#183;g + BG at the attractor (g .01, beta 2) vs baseline activity X — '
         f'tonic drive needs floor headroom (u_max&gt;0) AND ceiling headroom (X&lt;.95)</text>')

COL = {"flex": "#e08fb8", "ext": "#7fb8e0", "jump": "#9fe0a8"}


def mark(x, y, famname, filled, r=7):
    f = COL[famname]
    fill = f if filled else "none"
    sw = 2.2 if filled else 1.6
    if famname == "flex":
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{f}" stroke-width="{sw}"/>'
    if famname == "ext":
        d = r * 1.1
        return (f'<rect x="{x-d/2}" y="{y-d/2}" width="{d}" height="{d}" '
                f'fill="{fill}" stroke="{f}" stroke-width="{sw}"/>')
    d = r * 1.25
    return (f'<polygon points="{x},{y-d/2} {x-d/2},{y+d/2} {x+d/2},{y+d/2}" '
            f'fill="{fill}" stroke="{f}" stroke-width="{sw}"/>')


# legend strip above plot
ly = 88
xs = ML
for lab, f_ in [("flex (Ti/Tr flexor)", "flex"), ("extensor", "ext"),
                ("jump/flight MNs", "jump")]:
    s.append(mark(xs + 8, ly, f_, True, 6))
    s.append(f'<text x="{xs+22}" y="{ly+4}" fill="#c9d0dc" font-size="12.5">{lab}</text>')
    xs += 22 + len(lab) * 7.2 + 26
s.append(mark(xs + 8, ly, "flex", True, 6))
s.append(f'<text x="{xs+22}" y="{ly+4}" fill="#c9d0dc" font-size="12.5">'
         f'viable-modulating (34)</text>')
xs += 22 + 23 * 7.2 + 26
s.append(mark(xs + 8, ly, "flex", False, 6))
s.append(f'<text x="{xs+22}" y="{ly+4}" fill="#c9d0dc" font-size="12.5">'
         f'not (floor / ceiling / buried: 42)</text>')

# plot frame + kill zones
s.append(f'<rect x="{ML}" y="{MT}" width="{PW}" height="{PH}" fill="#1a1d26" '
         f'stroke="#3a3f4d" stroke-width="1"/>')
s.append(f'<rect x="{ML}" y="{MT}" width="{px(0)-ML}" height="{PH}" '
         f'fill="#3a2530" opacity="0.5"/>')
s.append(f'<rect x="{px(0)}" y="{MT}" width="{ML+PW-px(0)}" '
         f'height="{py(0.95)-MT}" fill="#3a3525" opacity="0.45"/>')
s.append(f'<line x1="{px(0)}" y1="{MT}" x2="{px(0)}" y2="{MT+PH}" '
         f'stroke="#c8746a" stroke-width="1.4" stroke-dasharray="5 4"/>')
s.append(f'<line x1="{px(0)}" y1="{py(0.95)}" x2="{ML+PW}" y2="{py(0.95)}" '
         f'stroke="#c8b06a" stroke-width="1.4" stroke-dasharray="5 4"/>')

# zone labels in empty areas
s.append(f'<text x="{ML+10}" y="{MT+PH*0.42}" fill="#c8746a" font-size="12">'
         f'relu floor</text>')
s.append(f'<text x="{ML+10}" y="{MT+PH*0.42+16}" fill="#c8746a" font-size="12">'
         f'absorbed</text>')
s.append(f'<text x="{ML+10}" y="{MT+PH*0.42+32}" fill="#c8746a" font-size="12">'
         f'(27 types, amp&#8804;.8)</text>')
s.append(f'<text x="{px(0)+10}" y="{py(0.95)-8}" fill="#c8b06a" font-size="12" '
         f'text-anchor="start">clamp ceiling — X pinned at 1 (2 types: MDN, DNg88)</text>')

# axes
for v in [-2, -1, 0, 1, 2, 3, 4, 5]:
    s.append(f'<line x1="{px(v)}" y1="{MT+PH}" x2="{px(v)}" y2="{MT+PH+6}" stroke="#8a92a3"/>')
    s.append(f'<text x="{px(v)}" y="{MT+PH+22}" fill="#8a92a3" font-size="12" '
             f'text-anchor="middle">{v:+d}</text>')
for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
    s.append(f'<line x1="{ML-6}" y1="{py(v)}" x2="{ML}" y2="{py(v)}" stroke="#8a92a3"/>')
    s.append(f'<text x="{ML-10}" y="{py(v)+4}" fill="#8a92a3" font-size="12" '
             f'text-anchor="end">{v:.2f}</text>')
s.append(f'<text x="{ML+PW/2}" y="{H-40}" fill="#c9d0dc" font-size="14" '
         f'text-anchor="middle">u_max over 3 seeds x 6 s (clipped at -2; '
         f'DNg100 sits at -15.8)</text>')
s.append(f'<text x="24" y="{MT+PH/2}" fill="#c9d0dc" font-size="14" '
         f'transform="rotate(-90 24 {MT+PH/2})" text-anchor="middle">'
         f'baseline mean activity X</text>')

ann = {
    "DNge046": (10, -10, "start"), "DNg110": (10, 4, "start"), "MDN": (-14, 22, "end"),
    "DNg88": (-12, 18, "end"), "DNg95": (12, -6, "start"), "DNg105": (10, -10, "start"),
    "DNge059": (10, -8, "start"), "DNp02": (10, 12, "start"),
}
for _, r in fam.iterrows():
    x, y = px(r.u_max), py(r.mean_X)
    if r.u_max >= X1:            # clipped at the right edge: nudge marker inside
        x -= 14
    filled = r.cells_dyn > 0
    s.append(mark(x, y, r.family, filled))
    if r.dn_type in ann:
        dx, dy, anc = ann[r.dn_type]
        s.append(f'<text x="{x+dx}" y="{y+dy}" fill="#d8dce6" font-size="11.5" '
                 f'text-anchor="{anc}">{r.dn_type}</text>')

# DNg100 note in floor-zone bottom
s.append(f'<text x="{ML+10}" y="{MT+PH-70}" fill="#c8746a" font-size="11.5">'
         f'DNg100 u_max -15.8</text>')
s.append(f'<text x="{ML+10}" y="{MT+PH-54}" fill="#c8746a" font-size="11.5">'
         f'(buried; bit-identical at amp .8)</text>')
s.append(f'<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" '
         f'orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#c8746a"/></marker></defs>')
s.append(f'<path d="M {ML+98} {MT+PH-48} L {ML+8} {MT+PH-20}" stroke="#c8746a" '
         f'stroke-width="1.4" marker-end="url(#ar)" opacity="0.85"/>')

s.append(f'<text x="{ML}" y="{H-12}" fill="#767e8d" font-size="11.5">'
         f'76 atlas family types x L22/L24/L31 tables; spot-checks: DNge046/DNg110 tonic 0.2 '
         f'shift rhythm f 0.8-2.0 &#8594; 2.2-3.4 Hz; MDN ceiling-pinned, bit-identical; '
         f'anchors DNg100 (inert) / DNg95 (lands at 0.2) reproduced</text>')

svg = "\n".join(s) + "</svg>"
open("l36/viability.svg", "w").write(svg)
print("wrote l36/viability.svg")
