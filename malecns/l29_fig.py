"""L29 figure: cord transfer function — modulation depth + phase vs freq.
House style: SVG + rsvg-convert (no matplotlib)."""
import json
import math
import subprocess

import numpy as np

R = json.load(open("l29/results_l29.json"))
S = R["summary"]
FREQS = R["meta"]["freqs"]
NF = R["meta"]["null_freqs"]

BG, FG, MUT = "#282c34", "#abb2bf", "#5c6370"
GRID, AX = "#3e4451", "#5c6370"
PC = {"Ti_flex": "#e06c75", "Ti_ext": "#61afef", "Tr_flex": "#ff9896",
      "Tr_ext": "#c678dd", "all": "#e5c07b"}

W, H = 1640, 620
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<text x="30" y="30" fill="{FG}" font-size="17" font-weight="bold">L29: the homogeneous-tau cord is a ~3-stage low-pass — half-depth cutoff 5 Hz on every pool; stride rhythm (5-10 Hz) does not survive the interior</text>']

XMIN, XMAX, YMIN, YMAX = math.log10(0.4), math.log10(25), math.log10(0.0008), math.log10(0.55)


def panel(px, py, pw, ph):
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#21252b" stroke="{GRID}"/>')
    for f in (0.5, 1, 2, 5, 10, 20):
        x = px + (math.log10(f) - XMIN) / (XMAX - XMIN) * pw
        o.append(f'<line x1="{x:.1f}" y1="{py}" x2="{x:.1f}" y2="{py+ph}" stroke="{GRID}" stroke-width="0.6"/>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+18}" fill="{MUT}" font-size="12" text-anchor="middle">{f:g}</text>')
    o.append(f'<text x="{px+pw/2}" y="{py+ph+38}" fill="{FG}" font-size="13" text-anchor="middle">drive frequency (Hz, log)</text>')


# ---- panel 1: depth ----
px, py, pw, ph = 60, 88, 720, 382
panel(px, py, pw, ph)
for d in (0.001, 0.01, 0.1, 0.3):
    y = py + ph - (math.log10(d) - YMIN) / (YMAX - YMIN) * ph
    o.append(f'<line x1="{px}" y1="{y:.1f}" x2="{px+pw}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
    o.append(f'<text x="{px-8}" y="{y+4:.1f}" fill="{MUT}" font-size="12" text-anchor="end">{d:g}</text>')
o.append(f'<text x="26" y="{py+ph/2}" fill="{FG}" font-size="13" text-anchor="middle" transform="rotate(-90 26 {py+ph/2})">modulation depth (amp/mean, log)</text>')


def LX(f): return px + (math.log10(f) - XMIN) / (XMAX - XMIN) * pw
def LY(d): return py + ph - (math.log10(max(d, 1e-4)) - YMIN) / (YMAX - YMIN) * ph


# half-depth cutoff band 2-5 Hz
o.append(f'<rect x="{LX(2):.1f}" y="{py}" width="{LX(5)-LX(2):.1f}" height="{ph}" fill="#e06c75" opacity="0.07"/>')
o.append(f'<text x="{(LX(2)+LX(5))/2:.1f}" y="{py+ph-10}" fill="#d19a66" font-size="11.5" text-anchor="middle">corner: 2&#8211;5 Hz</text>')

# cascade fit overlay (all pool)
f0 = S["f0_hz"]
n_fit = S["cascade_fit_n"]["all"]["n"]
fs = np.logspace(XMIN, XMAX, 90)
Hv = 1 / np.sqrt(1 + (fs / f0) ** 2)
base = S["cutoffs"]["all"]["curve"][0]
pts = " ".join(f"{LX(f):.1f},{LY(base*(h/Hv[0])**n_fit):.1f}" for f, h in zip(fs, Hv))
o.append(f'<polyline points="{pts}" fill="none" stroke="#98c379" stroke-width="1.6" stroke-dasharray="5,4" opacity="0.9"/>')
o.append(f'<text x="{LX(12):.0f}" y="{LY(base*0.028):.0f}" fill="#98c379" font-size="12.5" text-anchor="start">{n_fit:.1f}-stage 50ms cascade fit</text>')

DASH = {"Tr_flex": "2,3", "Tr_ext": "8,4"}
for pname, c in PC.items():
    cur = S["cutoffs"][pname]["curve"]
    ls = "7,4" if pname == "all" else DASH.get(pname, "")
    pts = " ".join(f"{LX(f):.1f},{LY(d):.1f}" for f, d in zip(FREQS, cur))
    o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{2.4 if pname=="all" else 1.9}"{" stroke-dasharray="+chr(34)+ls+chr(34) if ls else ""}/>')
    for f, d in zip(FREQS, cur):
        o.append(f'<circle cx="{LX(f):.1f}" cy="{LY(d):.1f}" r="3.4" fill="{c}"/>')

# null band (all pool): mean +/- sd squares with error bars, offset right of the 'all' points
for f in NF:
    vals = [e["pools"]["all"]["depth"] for e in R["null"] if e["f"] == f]
    m, s = float(np.mean(vals)), float(np.std(vals))
    x, y = LX(f * 1.13), LY(m)
    o.append(f'<rect x="{x-6:.1f}" y="{y-6:.1f}" width="12" height="12" fill="none" stroke="#e5c07b" stroke-width="2"/>')
    o.append(f'<line x1="{x:.1f}" y1="{LY(m-s):.1f}" x2="{x:.1f}" y2="{LY(m+s):.1f}" stroke="#e5c07b" stroke-width="1.6"/>')

# legend (lower-left, clear of the curves)
lx = px + 34
for i, (pname, c) in enumerate(PC.items()):
    yy = py + ph - 128 + i * 20
    o.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+26}" y2="{yy-4}" stroke="{c}" stroke-width="2.2"/>')
    o.append(f'<text x="{lx+32}" y="{yy}" fill="{FG}" font-size="12.5">{pname}</text>')
yy = py + ph - 128 + 5 * 20
o.append(f'<rect x="{lx}" y="{yy-10}" width="12" height="12" fill="none" stroke="#e5c07b" stroke-width="2"/>')
o.append(f'<text x="{lx+18}" y="{yy}" fill="{FG}" font-size="12.5">interior-null (all), 3 draws &#177;sd</text>')
o.append(f'<text x="{px}" y="{py-12}" fill="{FG}" font-size="14" font-weight="bold">modulation depth vs frequency (2 seeds; DT 10ms / 2ms at f&#8805;10)</text>')

# ---- panel 2: phase ----
px2, pw2 = 860, 720
PMIN, PMAX = -310, -40
panel(px2, py, pw2, ph)
for d in (-60, -120, -180, -240, -300):
    y = py + ph - (d - PMIN) / (PMAX - PMIN) * ph
    o.append(f'<line x1="{px2}" y1="{y:.1f}" x2="{px2+pw2}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
    o.append(f'<text x="{px2-8}" y="{y+4:.1f}" fill="{MUT}" font-size="12" text-anchor="end">{d}</text>')
o.append(f'<text x="{px2-30}" y="{py+ph/2}" fill="{FG}" font-size="13" text-anchor="middle" transform="rotate(-90 {px2-30} {py+ph/2})">DFT phase at drive f (deg)</text>')


def PY(p): return py + ph - (p - PMIN) / (PMAX - PMIN) * ph


UNWRAP = {"all": [-111, -131, -166, -220, -245]}  # +140/+115 unwrapped; 20Hz dropped (snr 0.2)
pred = [-90 - math.degrees(math.atan(f / f0)) * n_fit for f in fs]
pts = " ".join(f"{px2 + (math.log10(f)-XMIN)/(XMAX-XMIN)*pw2:.1f},{PY(p):.1f}" for f, p in zip(fs, pred))
o.append(f'<polyline points="{pts}" fill="none" stroke="#98c379" stroke-width="1.6" stroke-dasharray="5,4"/>')
o.append(f'<text x="{px2+pw2-20}" y="{PY(pred[-1])-26:.0f}" fill="#98c379" font-size="12.5" text-anchor="end">cascade pred (n={n_fit:.1f})</text>')
for pname, c in PC.items():
    phv = S["phase"][pname]
    phu = [p - 360 if p > 0 else p for p in phv[:5]]  # unwrap +, drop 20Hz
    ls2 = "7,4" if pname == "all" else DASH.get(pname, "")
    pts = " ".join(f"{px2 + (math.log10(f)-XMIN)/(XMAX-XMIN)*pw2:.1f},{PY(p):.1f}" for f, p in zip(FREQS[:5], phu))
    o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{2.4 if pname=="all" else 1.9}"{" stroke-dasharray="+chr(34)+ls2+chr(34) if ls2 else ""}/>')
    for f, p in zip(FREQS[:5], phu):
        o.append(f'<circle cx="{px2 + (math.log10(f)-XMIN)/(XMAX-XMIN)*pw2:.1f}" cy="{PY(p):.1f}" r="3.4" fill="{c}"/>')
o.append(f'<text x="{px2}" y="{py-12}" fill="{FG}" font-size="14" font-weight="bold">phase lag vs drive (sin convention; 20 Hz dropped, snr 0.2)</text>')

o.append(f'<text x="30" y="{H-64}" fill="#82858d" font-size="12.5">depth(5 Hz) = 0.22x depth(0.5 Hz), 10 Hz = 0.05x, 20 Hz dead &#8212; the uniform-tau interior cannot carry a 5-10 Hz stride rhythm; kinetics (L17/L18 taus) or direct DN routes (L19) must</text>')
o.append(f'<text x="30" y="{H-42}" fill="#82858d" font-size="12.5">null (L16 interior rewire, 3 draws): +20% MORE depth at 0.5-2 Hz (0.349&#177;.002 vs 0.288) &#8212; real wiring attenuates rhythm below its degree class (L16 envelope-width twin); both arms die at 10 Hz = floor is model-class</text>')
o.append(f'<text x="30" y="{H-20}" fill="#82858d" font-size="12.5">n_fit 2.7-3.2 per pool = the L21 2-hop sheet, NOT the ~9-stage transit delay &#8212; attenuation rides short paths, smear rides the long tail | 5Hz DT10 0.064 vs DT2 0.057 (corner verdict unchanged)</text>')
o.append("</svg>")
open("l29/transfer.svg", "w").write("\n".join(o))
subprocess.run(["rsvg-convert", "-w", "1640", "l29/transfer.svg", "-o", "l29/transfer.png"], check=True)
print("wrote l29/transfer.png")
for k, v in S["cutoffs"].items():
    print(k, "curve", [round(x, 3) for x in v["curve"]], "cutoff", v["half_depth_cutoff"])
