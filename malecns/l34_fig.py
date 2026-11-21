"""L34 figure: entrainment tongue + antiphase cost. Hand-built SVG (house
style: no matplotlib on this box) -> rsvg-convert -> PNG."""
import json
import subprocess

import numpy as np

r = json.load(open("l34/results_l34.json"))
AMPS = [0.01, 0.03, 0.1, 0.3]
COL = {0.01: "#5b6b7a", 0.03: "#d1495b", 0.1: "#e8a33d", 0.3: "#2a9d8f"}
DASH = {0.01: "none", 0.03: "10,5", 0.1: "2,5", 0.3: "14,4,2,4"}
FREQS = r["meta"]["freqs"]
SEEDS = [11, 22, 33]
free_f = {int(s): r["free"][s]["f"] for s in r["free"]}

W, H = 1060, 504
MXA, MYA, MXB = 60, 70, 60
PW, PH = 430, 330
sx_a = lambda v: MXA + (v - 0.5) / (3.3 - 0.5) * PW
sy_a = lambda v: H - MYA - (v - 0.4) / (3.7 - 0.4) * PH
sx_b = lambda v: MXA + PW + 70 + (v - 0.5) / (3.3 - 0.5) * PW
sy_b = lambda v: H - MYA - (v + 0.55) / (1.0 + 0.55) * PH

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
     f'font-family="DejaVu Sans, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#14171c"/>',
     f'<text x="{W//2}" y="30" fill="#e8e6e3" font-size="17" text-anchor="middle" font-weight="bold">'
     f'L34 — the self-rhythmic cord ENTRAINS to mechanosensory drive (L32 substrate, 3 seeds)</text>']

# ---------- panel A ----------
s.append(f'<rect x="{MXA}" y="{H-MYA-PH}" width="{PW}" height="{PH}" fill="#1b1f26" stroke="#3a414d"/>')
for gv in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
    s.append(f'<line x1="{sx_a(gv):.1f}" y1="{H-MYA}" x2="{sx_a(gv):.1f}" y2="{H-MYA-PH}" stroke="#282e38"/>')
    s.append(f'<text x="{sx_a(gv):.1f}" y="{H-MYA+18}" fill="#9aa4b2" font-size="12" text-anchor="middle">{gv:g}</text>')
for gv in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
    s.append(f'<line x1="{MXA}" y1="{sy_a(gv):.1f}" x2="{MXA+PW}" y2="{sy_a(gv):.1f}" stroke="#282e38"/>')
    s.append(f'<text x="{MXA-8}" y="{sy_a(gv)+4:.1f}" fill="#9aa4b2" font-size="12" text-anchor="end">{gv:g}</text>')
s.append(f'<text x="{MXA+PW//2}" y="{H-MYA+36}" fill="#c9d1d9" font-size="13" text-anchor="middle">drive frequency f_d (Hz)</text>')
s.append(f'<text x="18" y="{H-MYA-PH//2}" fill="#c9d1d9" font-size="13" transform="rotate(-90 18 {H-MYA-PH//2})" text-anchor="middle">motor rhythm f_mot (Hz)</text>')
# lock diagonal
s.append(f'<line x1="{sx_a(0.5):.1f}" y1="{sy_a(0.5):.1f}" x2="{sx_a(3.3):.1f}" y2="{sy_a(3.3):.1f}" stroke="#8b949e" stroke-dasharray="4,4"/>')
s.append(f'<text x="{sx_a(2.62):.1f}" y="{sy_a(2.86):.1f}" fill="#8b949e" font-size="11">1:1 lock</text>')
# free-run freqs: text legend in the empty bottom-left corner of panel A
fl = " · ".join(f"s{sd} {f:.2f}" for sd, f in sorted(free_f.items()))
s.append(f'<text x="{MXA+8}" y="{H-MYA-8}" fill="#58a6ff" font-size="11">f_free (Hz): {fl}</text>')
# seed points per amp
MK = {0.01: "c", 0.03: "s", 0.1: "t", 0.3: "d"}
for amp in AMPS:
    rows = [g for g in r["grid"] if abs(g["amp"] - amp) < 1e-9]
    c = COL[amp]
    for g in rows:
        for j, p in enumerate(g["seeds"]):
            x = sx_a(g["fd"]) + (j - 1) * 4
            y = sy_a(min(max(p["f_mot"], 0.4), 3.7))
            if MK[amp] == "c":
                s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c}"/>')
            elif MK[amp] == "s":
                s.append(f'<rect x="{x-3.5:.1f}" y="{y-3.5:.1f}" width="7" height="7" fill="{c}"/>')
            elif MK[amp] == "t":
                s.append(f'<polygon points="{x:.1f},{y-4.5:.1f} {x-4.5:.1f},{y+3.5:.1f} {x+4.5:.1f},{y+3.5:.1f}" fill="{c}"/>')
            else:
                s.append(f'<polygon points="{x:.1f},{y-5:.1f} {x+4.5:.1f},{y:.1f} {x:.1f},{y+5:.1f} {x-4.5:.1f},{y:.1f}" fill="{c}"/>')
s.append(f'<text x="{MXA+PW//2}" y="{H-MYA-PH-10}" fill="#e8e6e3" font-size="13" text-anchor="middle">A · Arnold tongue: f_mot tracks f_d as amp grows (C2/C4 PASS)</text>')

# ---------- panel B ----------
X0 = MXA + PW + 70
s.append(f'<rect x="{X0}" y="{H-MYA-PH}" width="{PW}" height="{PH}" fill="#1b1f26" stroke="#3a414d"/>')
for gv in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
    s.append(f'<line x1="{sx_b(gv):.1f}" y1="{H-MYA}" x2="{sx_b(gv):.1f}" y2="{H-MYA-PH}" stroke="#282e38"/>')
    s.append(f'<text x="{sx_b(gv):.1f}" y="{H-MYA+18}" fill="#9aa4b2" font-size="12" text-anchor="middle">{gv:g}</text>')
for gv in (-0.5, 0.0, 0.5, 1.0):
    s.append(f'<line x1="{X0}" y1="{sy_b(gv):.1f}" x2="{X0+PW}" y2="{sy_b(gv):.1f}" stroke="#282e38"/>')
    s.append(f'<text x="{X0-8}" y="{sy_b(gv)+4:.1f}" fill="#9aa4b2" font-size="12" text-anchor="end">{gv:+g}</text>' if gv else
             f'<text x="{X0-8}" y="{sy_b(gv)+4:.1f}" fill="#9aa4b2" font-size="12" text-anchor="middle">0</text>')
s.append(f'<text x="{X0+PW//2}" y="{H-MYA+36}" fill="#c9d1d9" font-size="13" text-anchor="middle">drive frequency f_d (Hz)</text>')
s.append(f'<text x="{X0-46}" y="{H-MYA-PH//2}" fill="#c9d1d9" font-size="13" transform="rotate(-90 {X0-46} {H-MYA-PH//2})" text-anchor="middle">S(Tr) antagonist antiphase</text>')
s.append(f'<line x1="{X0}" y1="{sy_b(0.40):.1f}" x2="{X0+PW}" y2="{sy_b(0.40):.1f}" stroke="#8b949e" stroke-dasharray="4,4"/>')
s.append(f'<text x="{X0+PW*0.52:.1f}" y="{sy_b(0.40)+13:.1f}" fill="#adb6c2" font-size="11">L32 free-run level +.40</text>')
for amp in AMPS:
    rows = [g for g in r["grid"] if abs(g["amp"] - amp) < 1e-9]
    pts = []
    for g in sorted(rows, key=lambda x: x["fd"]):
        m = float(np.mean([p["S_tr"] for p in g["seeds"]]))
        pts.append((g["fd"], m))
    d = " ".join(f"{sx_b(f):.1f},{sy_b(m):.1f}" for f, m in pts)
    s.append(f'<polyline points="{d}" fill="none" stroke="{COL[amp]}" stroke-width="2" stroke-dasharray="{DASH[amp]}"/>')
    for f, m in pts:
        s.append(f'<circle cx="{sx_b(f):.1f}" cy="{sy_b(m):.1f}" r="3" fill="{COL[amp]}"/>')
s.append(f'<text x="{X0+PW//2}" y="{H-MYA-PH-10}" fill="#e8e6e3" font-size="13" text-anchor="middle">B · cost: antiphase dips at locking onset, restored at A=.3 (seed mean)</text>')

# ---------- legend: strip below panel B ----------
lx = X0 + 10
for i, amp in enumerate(AMPS):
    xx = lx + i * 112
    s.append(f'<line x1="{xx}" y1="{H-16}" x2="{xx+24}" y2="{H-16}" stroke="{COL[amp]}" stroke-width="3" stroke-dasharray="{DASH[amp]}"/>')
    s.append(f'<text x="{xx+30}" y="{H-12}" fill="#c9d1d9" font-size="11">A={amp}</text>')
s.append("</svg>")
open("l34/entrain.svg", "w").write("\n".join(s))
subprocess.run(["rsvg-convert", "-o", "l34/entrain.png", "l34/entrain.svg"], check=True)
print("wrote l34/entrain.png")
