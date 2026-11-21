"""L40 figure — stop-and-go composition. House style: hand-built SVG +
rsvg-convert (no matplotlib). Panel A: seed-11 Tr pooled traces (ctl/rel/
s_rh; flexor solid, extensor dashed) with phase bands. Panel B: S(Tr) per
window x arm, seed means + per-seed dots, gates at .25/.15.
"""
import json

import numpy as np

z = np.load("l40/traces.npz")
J = json.load(open("l40/results_l40.json"))
SEEDS = (11, 22, 33)
ARMS = ["ctl", "hop", "rel", "joint", "s_rh", "s_hr", "hop_2b"]
LBL = {"ctl": "control", "hop": "hop", "rel": "release", "joint": "joint",
       "s_rh": "stop-then-go", "s_hr": "go-then-stop", "hop_2b": "hop(2b)"}
HUE = {"ctl": "#9aa0a6", "hop": "#7ec8a9", "rel": "#e06c75", "joint": "#c88bea",
       "s_rh": "#61afef", "s_hr": "#e5c07b", "hop_2b": "#98c379"}
WINS = ["2a", "2b", "post"]
WLBL = {"2a": "ON-1 (stop phase)", "2b": "ON-2 (go phase)", "post": "POST"}

W, H = 1240, 800
A_Y0, A_H = 70, 300          # panel A plot box
B_Y0, B_H = 430, 250
PX0, PX1 = 90, 1180
DT = 0.01

# ---- panel A data (seed 11) ----
t = np.arange(10400) * DT
flex = {n: z[f"{n}_11_fL"] + z[f"{n}_11_fR"] for n in ("ctl", "rel", "s_rh")}
ext = {n: z[f"{n}_11_eL"] + z[f"{n}_11_eR"] for n in ("ctl", "rel", "s_rh")}
allv = np.concatenate([*flex.values(), *ext.values()])
ymin, ymax = float(allv.min()), float(allv.max())
pad = 0.06 * (ymax - ymin)
ymin, ymax = ymin - pad, ymax + pad


def X(x):
    return PX0 + (x / 104.0) * (PX1 - PX0)


def Y(v):
    return A_Y0 + A_H - (v - ymin) / (ymax - ymin) * A_H


def path(arr, dash):
    d = []
    for i in range(0, 10400, 8):
        d.append(("M" if i == 0 else "L") + f"{X(t[i]):.1f},{Y(arr[i]):.2f}")
    return " ".join(d)


sv = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"',
      ' font-family="DejaVu Sans, sans-serif">',
      f'<rect width="{W}" height="{H}" fill="#1d2027"/>',
      '<text x="40" y="36" fill="#d7dae0" font-size="22" font-weight="bold">',
      'L40 stop-and-go: release (DNg88 -8) x hop (DNge046_L +0.2) — seed 11</text>']

# phase bands
for x0, x1, c, lab in [(25, 40, "#3a2f36", "STOP drive"),
                       (40, 55, "#26333f", "GO drive")]:
    sv.append(f'<rect x="{X(x0)}" y="{A_Y0}" width="{X(x1)-X(x0)}" height="{A_H}"'
              f' fill="{c}" opacity="0.55"/>')
    sv.append(f'<text x="{(X(x0)+X(x1))/2}" y="{A_Y0-8}" fill="#e8b0b8" '
              f'font-size="13" font-weight="bold" text-anchor="middle">{lab}</text>')
sv.append(f'<text x="{X(12)}" y="{A_Y0-8}" fill="#5c6370" font-size="12" '
          f'text-anchor="middle">free</text>')
sv.append(f'<text x="{X(78)}" y="{A_Y0-8}" fill="#5c6370" font-size="12" '
          f'text-anchor="middle">drives off (recovery)</text>')
sv.append(f'<rect x="{PX0}" y="{A_Y0}" width="{PX1-PX0}" height="{A_H}" '
          f'fill="none" stroke="#3b4048"/>')
for v in np.linspace(ymin, ymax, 5):
    sv.append(f'<line x1="{PX0}" y1="{Y(v):.1f}" x2="{PX1}" y2="{Y(v):.1f}" '
              f'stroke="#2b2f36"/>')
    sv.append(f'<text x="{PX0-8}" y="{Y(v)+4:.1f}" fill="#7c828d" font-size="11" '
              f'text-anchor="end">{v:.2f}</text>')
for n in ("ctl", "rel", "s_rh"):
    sv.append(f'<path d="{path(flex[n], None)}" fill="none" stroke="{HUE[n]}" '
              f'stroke-width="1.6"/>')
    sv.append(f'<path d="{path(ext[n], None)}" fill="none" stroke="{HUE[n]}" '
              f'stroke-width="1.6" stroke-dasharray="7 4" opacity="0.75"/>')
for sec in (0, 25, 40, 55, 104):
    sv.append(f'<text x="{X(sec)}" y="{A_Y0+A_H+18}" fill="#7c828d" '
              f'font-size="11" text-anchor="middle">{sec}s</text>')
sv.append(f'<text x="30" y="{A_Y0+A_H/2}" fill="#9aa0a6" font-size="12" '
          f'transform="rotate(-90 30 {A_Y0+A_H/2})" text-anchor="middle">'
          f'Tr pooled pool mean (flex solid / ext dashed)</text>')

ly = A_Y0 + 24
for n in ("ctl", "rel", "s_rh"):
    sv.append(f'<line x1="{PX1-190}" y1="{ly}" x2="{PX1-160}" y2="{ly}" '
              f'stroke="{HUE[n]}" stroke-width="2.4"/>')
    sv.append(f'<text x="{PX1-152}" y="{ly+4}" fill="#d7dae0" font-size="12">'
              f'{LBL[n]}</text>')
    ly += 18

# ---- panel B: S bars ----
sv.append(f'<text x="40" y="415" fill="#d7dae0" font-size="17">'
          f'S(Tr) per window — seed mean (dots: seeds 11/22/33)</text>')
bw = (PX1 - PX0) / (len(ARMS) * len(WINS) + 1)
x = PX0 + bw * 0.5
for a in ARMS:
    for wname in WINS:
        vals = [0.0 if np.isnan(J["win"][a][str(s)][wname]["S"])
                else J["win"][a][str(s)][wname]["S"] for s in SEEDS]
        m = float(np.mean(vals))
        hgt = m / 0.8 * B_H
        x0 = x
        sv.append(f'<rect x="{x0:.1f}" y="{B_Y0+B_H-hgt:.1f}" width="{bw*0.86:.1f}"'
                  f' height="{hgt:.1f}" fill="{HUE[a]}" opacity='
                  f'"{0.55 if wname=="2a" else 0.75 if wname=="2b" else 0.95}"/>')
        for i, v in enumerate(vals):
            yy = B_Y0 + B_H - v / 0.8 * B_H
            sv.append(f'<circle cx="{x0+bw*0.43:.1f}" cy="{yy:.1f}" r="3" '
                      f'fill="#1d2027" stroke="{HUE[a]}" stroke-width="1.4"/>')
        x += bw
    x += bw * 0.35
sv.append(f'<rect x="{PX0}" y="{B_Y0}" width="{PX1-PX0}" height="{B_H}" '
          f'fill="none" stroke="#3b4048"/>')
for gv, c, lbl in ((0.25, "#61afef", "survival gate .25"),
                   (0.15, "#e06c75", "kill gate .15")):
    yy = B_Y0 + B_H - gv / 0.8 * B_H
    sv.append(f'<line x1="{PX0}" y1="{yy:.1f}" x2="{PX1}" y2="{yy:.1f}" '
              f'stroke="{c}" stroke-dasharray="6 5" opacity="0.8"/>')
    sv.append(f'<text x="{PX1-150}" y="{yy-5:.1f}" fill="{c}" font-size="11" '
              f'font-weight="bold" text-anchor="end">{lbl}</text>')
for v in (0.0, 0.4, 0.8):
    yy = B_Y0 + B_H - v / 0.8 * B_H
    sv.append(f'<text x="{PX0-8}" y="{yy+4:.1f}" fill="#7c828d" font-size="11" '
              f'text-anchor="end">{v:.1f}</text>')
x = PX0 + bw * 0.5
for a in ARMS:
    cx = x + (bw * len(WINS) + bw * 0.35) / 2 - bw * 0.35 / 2
    sv.append(f'<text x="{cx:.1f}" y="{B_Y0+B_H+18}" fill="{HUE[a]}" '
              f'font-size="12" text-anchor="middle">{LBL[a]}</text>')
    x += bw * len(WINS) + bw * 0.35
lx = PX0
for wname in WINS:
    sv.append(f'<text x="{lx+ (PX1-PX0)/3/2:.1f}" y="{B_Y0+B_H+36}" '
              f'fill="#7c828d" font-size="11" text-anchor="middle" '
              f'opacity="0.9">{WLBL[wname]}</text>')
    lx += (PX1 - PX0) / 3
sv.append(f'<text x="30" y="{B_Y0+B_H/2}" fill="#9aa0a6" font-size="12" '
          f'transform="rotate(-90 30 {B_Y0+B_H/2})" text-anchor="middle">'
          f'S(Tr) antiphase</text>')
sv.append(f'<text x="40" y="{H-18}" fill="#5c6370" font-size="12">'
          f'C3 PASS: after the release kills the rhythm, the hop still lands '
          f'(f-shift 1.04/1.52 Hz) and antiphase RECOVERS post-drive '
          f'(.52/.45/.36) — stop-and-go is ONE vocabulary</text>')
sv.append("</svg>")
open("l40/release.svg", "w").write("\n".join(sv))
import subprocess
subprocess.run(["rsvg-convert", "-o", "l40/release.png", "--background-color",
                "#1d2027", "l40/release.svg"], check=True)
print("wrote l40/release.svg -> release.png")
