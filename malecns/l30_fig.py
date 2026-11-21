"""L30 figure: segment-modularity heatmaps + T1-volley pool traces.
House style: SVG + rsvg-convert (no matplotlib)."""
import json
import subprocess

import numpy as np

R = json.load(open("l30/results_l30.json"))
d = np.load("l30/traces_T1v.npz", allow_pickle=True)
tr, pnames = d["tr"], [str(x) for x in d["pnames"]]

T = ["T1", "T2", "T3"]
S1 = np.array(R["T1_direct"]); Z1 = np.array(R["cellz_S1"])
S2 = np.array(R["T2_sheet"]); Z2 = np.array(R["cellz_S2"])
cs = R["cross_share"]

BG, FG, MUT = "#282c34", "#abb2bf", "#5c6370"
GRID, AX = "#3e4451", "#5c6370"
WARM, COOL = "#e06c75", "#61afef"
PCC = {"T1L": "#e06c75", "T1R": "#ff7b69", "T2L": "#98c379", "T2R": "#7ec9a3",
       "T3L": "#61afef", "T3R": "#89b8e8", "abd": "#9a9fa8"}

def lerp(c1, c2, t):
    return c1 + (c2 - c1) * t

def rgb_hex(c):
    return "#%02x%02x%02x" % tuple(int(x) for x in c)

def cell_fill(m, vmax):
    t = min(1.0, abs(m) / vmax)
    base = np.array([40, 44, 52])
    if m >= 0:
        c = lerp(base, np.array([224, 108, 117]), 0.25 + 0.75 * t)
    else:
        c = lerp(base, np.array([97, 175, 239]), 0.25 + 0.75 * t)
    return rgb_hex(c)

def heat_panel(x0, M, Z, title):
    o = [f'<text x="{x0}" y="52" fill="{FG}" font-size="15" font-weight="bold">{title}</text>']
    cw, ch, gy = 86, 62, 70
    vmax = max(abs(M).max(), 1e-9)
    for a in range(3):
        o.append(f'<text x="{x0-12}" y="{gy + a*ch + 40}" fill="{MUT}" font-size="13" text-anchor="end">{T[a]}</text>')
        o.append(f'<text x="{x0 + a*cw + cw/2}" y="{gy + 3*ch + 18}" fill="{MUT}" font-size="13" text-anchor="middle">&#8594;{T[a]}</text>')
        for b in range(3):
            cx, cy = x0 + b * cw, gy + a * ch
            f = cell_fill(M[a, b], vmax)
            zc = FG if abs(Z[a, b]) >= 5 else MUT
            o.append(f'<rect x="{cx+1}" y="{cy+1}" width="{cw-2}" height="{ch-2}" fill="{f}"/>')
            o.append(f'<text x="{cx+cw/2}" y="{cy+27}" fill="#e8e9eb" font-size="13" text-anchor="middle">{M[a,b]:+.0f}</text>')
            zc = "#d7dae0" if abs(Z[a, b]) >= 5 else "#9da1a8"
            o.append(f'<text x="{cx+cw/2}" y="{cy+46}" fill="{zc}" font-size="11.5" text-anchor="middle">z {Z[a,b]:+.0f}</text>')
    return o

W, H = 1620, 470
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<text x="30" y="30" fill="{FG}" font-size="17" font-weight="bold">L30: the cord is SEGMENT-MODULAR — every cross-segment cell is DEPLETED (500-draw label-perm null)</text>']
o += heat_panel(70, S1, Z1, f"direct intr(Ta)&#8594;motor(Tb) | cross {cs['S1']:.2f} vs null .67, z &#8722;27")
o += heat_panel(430, S2, Z2, f"sheet intr(Ta)&#8594;intr(Tb) | cross {cs['S2']:.2f} vs null .66, z &#8722;125")

# trace panel
px, py, pw, ph = 840, 70, 720, 300
tms = np.arange(tr.shape[0]) * 0.010
o.append(f'<text x="{px}" y="52" fill="{FG}" font-size="15" font-weight="bold">T1 volley &#8594; pool mean &#916; (seed 11)</text>')
for i, p in enumerate(pnames):
    lx, ly = px + 258 + i * 72, 52
    o.append(f'<rect x="{lx}" y="{ly-10}" width="11" height="11" fill="{PCC[p]}"/>')
    o.append(f'<text x="{lx+14}" y="{ly}" fill="{FG}" font-size="12">{p}</text>')
vy = np.array([min(0, tr.min() - 0.02), tr.max() * 1.08 + 0.02])
def X(t): return px + (t / 7.3) * pw
def Y(v): return py + ph - (v - vy[0]) / (vy[1] - vy[0]) * ph
o.append(f'<rect x="{X(0)}" y="{py}" width="{X(0.3)-X(0)}" height="{ph}" fill="#e5c07b" opacity="0.13"/>')
o.append(f'<line x1="{px}" y1="{Y(0)}" x2="{px+pw}" y2="{Y(0)}" stroke="{AX}" stroke-width="1"/>')
for gv in np.linspace(vy[0], vy[1], 5):
    o.append(f'<text x="{px+pw+6}" y="{Y(gv)+4}" fill="{MUT}" font-size="11">{gv:+.2f}</text>')
for tsec in (1, 2, 3, 4, 5, 6, 7):
    o.append(f'<text x="{X(tsec)}" y="{py+ph+16}" fill="{MUT}" font-size="11" text-anchor="middle">{tsec}s</text>')
for i, p in enumerate(pnames):
    pts = " ".join(f"{X(tms[k]):.1f},{Y(tr[k, i]):.1f}" for k in range(0, len(tms), 4))
    o.append(f'<polyline points="{pts}" fill="none" stroke="{PCC[p]}" stroke-width="2" opacity="0.95"/>')
o.append(f'<text x="{px}" y="{py+ph+34}" fill="{MUT}" font-size="11.5">own-segment 580-733x noise vs T2 96-129x / T3 71-89x; T3 volley drives abd 164x (caudal neighbor); random-volley arm flattens to 150-260x</text>')
o.append(f'<text x="30" y="{H-14}" fill="{MUT}" font-size="12">2-hop (MS-rewire null, 3 draws x 2.5M swaps): cross .22 real vs .64&#177;.003 rewired, z &#8722;132 | S4: own-segment intrinsic carries 51-58% of every leg pool in-weight | af0 0.163 (L11 op point) | pool-mean amplitude SNR class (L21)</text>')
o.append("</svg>")
svg = "\n".join(o)
open("l30/crossleg.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "1620", "l30/crossleg.svg", "-o", "l30/crossleg.png"], check=True)
print("wrote l30/crossleg.png")
