"""L33 figure: (a) turn vs bias amp — no graded steering; (b) S_side —
metastable L-dominant antiphase organization. Hand-built SVG (house style)."""
import json
import subprocess

r = json.load(open("l33/results_l33.json"))
ARMS = ["base", "Lx0.25", "Lx0.5", "Lx1.0", "Lx2.0", "Lx4.0"]
AMPS = [0, 0.0125, 0.025, 0.05, 0.1, 0.2]
SEEDCOL = {11: "#c0392b", 22: "#2471a3", 33: "#1e8449"}

W, H = 1060, 470
M = 70
PW = (W - 2 * M - 40) / 2
PH = H - 2 * M + 10

def px(a, x, ylo, yhi, ymin, ymax):
    return a[0] + (x - xmin) / (xmax - xmin) * a[2], a[1] + a[3] * (1 - (y - ymin) / (ymax - ymin))

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="DejaVu Sans, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#14161a"/>',
     '<text x="530" y="30" fill="#e8e6e3" font-size="19" text-anchor="middle" font-weight="bold">L33: tonic DN bias does not steer the self-rhythmic cord (DNg100 sustained, g .01 beta 2 d .05)</text>']

def frame(x0, title, xlab, ylab, xmax_, ymax_, xticks):
    s.append(f'<rect x="{x0}" y="{M-10}" width="{PW}" height="{PH}" fill="#1b1e24" stroke="#3a3f47"/>')
    s.append(f'<text x="{x0+PW/2}" y="{M+PH+42}" fill="#b8b2aa" font-size="14" text-anchor="middle">{xlab}</text>')
    s.append(f'<text x="{x0-48}" y="{M+PH/2}" fill="#b8b2aa" font-size="14" text-anchor="middle" transform="rotate(-90 {x0-48} {M+PH/2})">{ylab}</text>')
    s.append(f'<text x="{x0+PW/2}" y="{M-18}" fill="#e8e6e3" font-size="15" text-anchor="middle">{title}</text>')
    for i in range(6):
        y = M - 10 + PH * i / 5
        s.append(f'<line x1="{x0}" y1="{y:.0f}" x2="{x0+PW}" y2="{y:.0f}" stroke="#2a2e35"/>')
        s.append(f'<text x="{x0-8}" y="{y+5:.0f}" fill="#8f8a83" font-size="12" text-anchor="end">{ymax_*(1-i/5):.2f}</text>')
    for xv, lb in xticks:
        x = x0 + xv / xmax_ * PW
        s.append(f'<line x1="{x:.0f}" y1="{M-10}" x2="{x:.0f}" y2="{M-10+PH}" stroke="#2a2e35"/>')
        s.append(f'<text x="{x:.0f}" y="{M+PH+18}" fill="#8f8a83" font-size="12" text-anchor="middle">{lb}</text>')

# ---- panel A: turn vs amp
a1 = (M, M - 10, PW, PH)
frame(M, "A  turn (L-R flexor mass asym, Ti) vs DNg95-L bias amp", "bias amp (DNg95-L tonic)", "turn  (L-R)/(L+R)", 0.2, 0.35,
      [(0, "0"), (0.05, ".05"), (0.1, ".1"), (0.15, ".15"), (0.2, ".2")])
s.append(f'<line x1="{M}" y1="{M-10+PH:.0f}" x2="{M+PW}" y2="{M-10+PH:.0f}" stroke="#8f8a83"/>')
for i, sd in enumerate((11, 22, 33)):
    pts = []
    for ai, arm in enumerate(ARMS):
        y = r[arm]["seeds"][i]["turn"]["Ti"]["f"]
        x = M + AMPS[ai] / 0.2 * PW
        yy = M - 10 + PH * (1 - y / 0.35)
        pts.append((x, yy))
    dash = "" if sd == 11 else ("stroke-dasharray='7 5'" if sd == 22 else "stroke-dasharray='2 4'")
    s.append(f'<polyline points="{" ".join(f"{p[0]:.0f},{p[1]:.0f}" for p in pts)}" fill="none" stroke="{SEEDCOL[sd]}" stroke-width="2.2" {dash}/>')
    for p in pts:
        s.append(f'<circle cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="4" fill="{SEEDCOL[sd]}"/>')
# random-pair nulls at amp .2
for dr in (0, 1):
    for i in range(3):
        y = r[f"rand{dr}"]["seeds"][i]["turn"]["Ti"]["f"]
        x = M + PW
        yy = M - 10 + PH * (1 - y / 0.35)
        s.append(f'<circle cx="{x:.0f}" cy="{yy:.0f}" r="6" fill="none" stroke="#e8e6e3" stroke-width="1.6"/>')
s.append(f'<text x="{M+PW-6}" y="{M+8}" fill="#b8b2aa" font-size="11" text-anchor="end">o = random DN pair (amp .2)</text>')

# ---- panel B: S_side vs amp (seed 11 bold, 22/33 thin)
x0 = M + PW + 40
frame(x0, "B  per-side antiphase S(Tr) — left-organized, metastable flip", "bias amp (DNg95-L tonic)", "S(Tr) per side", 0.2, 1.0,
      [(0, "0"), (0.05, ".05"), (0.1, ".1"), (0.15, ".15"), (0.2, ".2")])
for i, sd in enumerate((11, 22, 33)):
    for side, col in (("L", "#c0392b"), ("R", "#2471a3")):
        pts = []
        for ai, arm in enumerate(ARMS):
            y = r[arm]["seeds"][i]["S_side"]["Tr" + side]
            x = x0 + AMPS[ai] / 0.2 * PW
            yy = M - 10 + PH * (1 - y / 1.0)
            pts.append((x, yy))
        wdt = 2.6 if sd == 11 else 1.1
        op = 1.0 if sd == 11 else 0.45
        dash = "" if side == "L" else "stroke-dasharray='6 4'"
        s.append(f'<polyline points="{" ".join(f"{p[0]:.0f},{p[1]:.0f}" for p in pts)}" fill="none" stroke="{col}" stroke-width="{wdt}" opacity="{op}" {dash}/>')

leg = [("#c0392b", "", "seed 11 L"), ("#c0392b", "7 5", "seed 22 L"), ("#c0392b", "2 4", "seed 33 L"),
       ("#2471a3", "", "seed 11 R"), ("#2471a3", "7 5", "seed 22 R"), ("#2471a3", "2 4", "seed 33 R")]
for i, (c, d, t) in enumerate(leg):
    x = x0 + 8 + (i % 3) * 110
    y = M + 26 + (i // 3) * 22
    dd = f"stroke-dasharray='{d}'" if d else ""
    s.append(f'<line x1="{x}" y1="{y}" x2="{x+26}" y2="{y}" stroke="{c}" stroke-width="2.4" {dd}/>')
    s.append(f'<text x="{x+32}" y="{y+4}" fill="#b8b2aa" font-size="12">{t}</text>')
s.append("</svg>")
open("l33/steering.svg", "w").write("\n".join(s))
subprocess.run(["rsvg-convert", "-w", "1060", "l33/steering.svg", "-o", "l33/steering.png"], check=True)
print("wrote l33/steering.png")
