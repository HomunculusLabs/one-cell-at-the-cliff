"""L21 figure: interior-kinetics invariance, descriptive (owner movement law).

Panels:
  A : TTMn t_pk per arm (per-seed dots + mean) — flat ~344-466 ms under every
      intrinsic/asc-dn tau assignment; collapses only at whole-graph 5 ms.
  B : seed-11 TTMn pool-mean traces — u51 vs u5 identical (corr .998),
      all5 sharp + early; all5 leg dotted (TTMn leads).
  C : brain-origin (looming): b1 pool SNR bars (flat across tau) +
      b2 early-window margins (inside seed noise at DT 2 ms).

Reads l21/{results_l21_a0a1,a3,b}.json + traces npz; writes l21/delay.svg/.png.
"""
import json
import subprocess

import numpy as np

rA = json.load(open("l21/results_l21_a0a1.json"))
r3 = json.load(open("l21/results_l21_a3.json"))
rB = json.load(open("l21/results_l21_b.json"))
tA = np.load("l21/traces_l21_a0a1.npz")
t3 = np.load("l21/traces_l21_a3.npz")

ARMS = [("u51", "u51"), ("u20", "u20"), ("u10", "u10"),
        ("u5", "u5"), ("d1", "d1"), ("d2", "d2"),
        ("far", "far"), ("asc5", "asc+dn"), ("all5", "ALL 5")]
TP = {a: (rA if a in rA else r3)[a]["ttm_tp_ms"] for a, _ in ARMS}

PURPLE, ORANGE, BLUE, GREY = "#c678dd", "#ffb454", "#61afef", "#5c6370"
RED, GREEN, BG, FG = "#e06c75", "#98c379", "#282c34", "#abb2bf"
W = 1120
MX = 210
PW = W - MX - 90
Y_A, H_A = 96, 250
Y_B, H_B = Y_A + H_A + 78, 250
Y_C, H_C = Y_B + H_B + 78, 250
H = Y_C + H_C + 78

S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"',
     f' viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     '<style>text{font-family:DejaVu Sans Mono,monospace;fill:#abb2bf}'
     '.t{font-size:21px;font-weight:bold;fill:#d7dce0}'
     '.s{font-size:15px}.h{font-size:13px;fill:#5c6370}</style>']
S.append(f'<text x="40" y="44" class="t">L21 — interior delay is '
         f'PATH-INTEGRAL: no class shortcut</text>')
S.append(f'<text x="40" y="68" class="h">DT 2 ms, TTMn 4 ms reporter; cord '
         'mechano volley; arm = which cells get tau 5 ms (rest 51 ms)</text>')
S.append(f'<text x="{MX+PW/2:.0f}" y="{Y_A+H_A+46}" text-anchor="middle" '
         f'class="h">u* = uniform vnc_intrinsic tau (ms); d1/d2 = hop tiers; '
         f'ALL 5 = whole graph</text>')


def sc(v, v0, v1, y, h):
    return y + h - h * (v - v0) / (v1 - v0)


# --- Panel A: t_pk per arm -------------------------------------------------
S.append(f'<text x="40" y="{Y_A-14}" class="s" fill="#d7dce0">A · TTMn t_pk '
         f'(ms) — flat everywhere except whole-graph 5 ms</text>')
v0, v1 = 0, 500
for g in range(0, 501, 100):
    y = sc(g, v0, v1, Y_A, H_A)
    S.append(f'<line x1="{MX}" y1="{y:.0f}" x2="{MX+PW}" y2="{y:.0f}" '
             f'stroke="#3a3f4b" stroke-width="1"/>')
    S.append(f'<text x="{MX-8}" y="{y+5:.0f}" text-anchor="end" class="h">{g}</text>')
bw = PW / len(ARMS)
for i, (a, lab) in enumerate(ARMS):
    x = MX + i * bw
    col = ORANGE if a == "all5" else PURPLE
    vals = TP[a]
    m = float(np.mean(vals))
    yb = sc(m, v0, v1, Y_A, H_A)
    S.append(f'<rect x="{x+bw*0.28:.0f}" y="{yb:.0f}" width="{bw*0.28:.0f}" '
             f'height="{Y_A+H_A-yb:.0f}" fill="{col}" opacity="0.82"/>')
    for v in vals:
        yv = sc(v, v0, v1, Y_A, H_A)
        S.append(f'<circle cx="{x+bw*0.62:.0f}" cy="{yv:.0f}" r="3.4" '
                 f'fill="{FG}"/>')
    S.append(f'<text x="{x+bw*0.42:.0f}" y="{Y_A+H_A+22}" text-anchor="middle"'
             f' class="s" fill="{col}">{lab}</text>')
S.append(f'<line x1="{MX}" y1="{Y_A+H_A}" x2="{MX+PW}" y2="{Y_A+H_A}" '
         f'stroke="#5c6370" stroke-width="1.4"/>')

# --- Panel B: traces --------------------------------------------------------
S.append(f'<text x="40" y="{Y_B-14}" class="s" fill="#d7dce0">B · seed-11 '
         f'TTMn dm trace: u51 vs u5 identical (r=.998); whole-5 collapses</text>')
tr_u51, tr_u5 = tA["u51_ttm"], tA["u5_ttm"]
tr_all5, leg5 = t3["all5_ttm"], t3["all5_leg"]
T = len(tr_u51)
lo, hi = -0.002, 0.046
X0, X1 = 0, (T - 1) * 2


def px(k):
    return MX + PW * (k * 2 - X0) / (X1 - X0)


def py(v):
    return sc(v, lo, hi, Y_B, H_B)


for ms in range(0, 681, 100):
    x = MX + PW * ms / 680
    S.append(f'<line x1="{x:.0f}" y1="{Y_B}" x2="{x:.0f}" y2="{Y_B+H_B}" '
             f'stroke="#3a3f4b" stroke-width="1"/>')
    S.append(f'<text x="{x:.0f}" y="{Y_B+H_B+20}" text-anchor="middle" '
             f'class="h">{ms}</text>')
S.append(f'<rect x="{MX}" y="{Y_B}" width="{px(20)-MX:.0f}" height="{H_B}" '
         f'fill="#e5c07b" opacity="0.10"/>')
S.append(f'<text x="{MX+6}" y="{Y_B+14}" class="h">volley 40 ms</text>')
for tr, col, dash, lab in ((tr_u51, PURPLE, None, "uniform 51 ms"),
                           (tr_u5, BLUE, "7,5", "uniform 5 ms"),
                           (tr_all5, ORANGE, None, "whole-graph 5 ms"),
                           (leg5, GREY, "2,4", "whole-5 leg pool")):
    pts = " ".join(f"{px(k):.1f},{py(v):.1f}" for k, v in enumerate(tr))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    S.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
             f'stroke-width="2.1"{dd}/>')
LGD = [("uniform 51 ms", PURPLE, None), ("uniform 5 ms (=same)", BLUE, "7,5"),
       ("whole-graph 5 ms", ORANGE, None), ("whole-5 leg pool", GREY, "2,4")]
lx, ly = MX + PW - 258, Y_B + 18
S.append(f'<rect x="{lx-10}" y="{ly-14}" width="266" height="92" '
         f'fill="#21252b" opacity="0.9" rx="4"/>')
for i, (lab, col, dash) in enumerate(LGD):
    yy = ly + i * 20
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    S.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+30}" y2="{yy-4}" '
             f'stroke="{col}" stroke-width="2.4"{dd}/>')
    S.append(f'<text x="{lx+38}" y="{yy}" class="s" fill="{col}">{lab}</text>')
S.append(f'<line x1="{MX}" y1="{py(0):.0f}" x2="{MX+PW}" y2="{py(0):.0f}" '
         f'stroke="#5c6370" stroke-width="1"/>')
S.append(f'<text x="{MX+PW/2:.0f}" y="{Y_B+H_B+42}" text-anchor="middle" '
         f'class="h">time (ms)</text>')

# --- Panel C: brain-origin ---------------------------------------------------
S.append(f'<text x="40" y="{Y_C-14}" class="s" fill="#d7dce0">C · looming '
         f'event: pool SNR flat; ordering margins inside seed noise</text>')
S.append(f'<text x="40" y="{Y_C+6}" class="h">b1 (no amp): pool SNR vs noise '
         f'floor — flat across tau</text>')
gx0, gx1 = MX, MX + PW * 0.52
sv0, sv1 = 0, 14
for g in (0, 7, 14):
    y = sc(g, sv0, sv1, Y_C + 18, H_C - 60)
    S.append(f'<line x1="{gx0}" y1="{y:.0f}" x2="{gx1}" y2="{y:.0f}" '
             f'stroke="#3a3f4b" stroke-width="1"/>')
    S.append(f'<text x="{gx0-8}" y="{y+5:.0f}" text-anchor="end" '
             f'class="h">{g}x</text>')
tauz = ["tau51", "tau10", "tau5"]
gw = (gx1 - gx0) / len(tauz)
for i, tz in enumerate(tauz):
    x = gx0 + i * gw
    for j, (nm, col) in enumerate((("ttm", PURPLE), ("leg", GREEN))):
        v = float(np.mean(rB["b1"][tz]["snr"][nm]))
        yv = sc(v, sv0, sv1, Y_C + 18, H_C - 60)
        S.append(f'<rect x="{x+gw*0.18+j*gw*0.32:.0f}" y="{yv:.0f}" '
                 f'width="{gw*0.26:.0f}" height="{Y_C+18+(H_C-60)-yv:.0f}" '
                 f'fill="{col}" opacity="0.85"/>')
    S.append(f'<text x="{x+gw/2:.0f}" y="{Y_C+18+(H_C-60)+18}" '
             f'text-anchor="middle" class="h">{tz}ms</text>')
# margin dots, own axis on the right
mx0, mx1 = MX + PW * 0.62, MX + PW
mv0, mv1 = -60, 210
yy0, hh = Y_C + 18, H_C - 60
S.append(f'<line x1="{mx0}" y1="{sc(0,mv0,mv1,yy0,hh):.0f}" x2="{mx1}" '
         f'y2="{sc(0,mv0,mv1,yy0,hh):.0f}" stroke="#5c6370" '
         f'stroke-width="1.2"/>')
S.append(f'<text x="{mx0}" y="{yy0-6}" class="h">b2 early margin '
         f'(leg − TTMn, steps)</text>')
for i, tz in enumerate(tauz):
    x = mx0 + (i + 0.5) * (mx1 - mx0) / 3
    for j, v in enumerate(rB["b2"][tz]["margin_early"]):
        col = RED if v < 0 else GREEN
        yv = sc(v, mv0, mv1, yy0, hh)
        S.append(f'<circle cx="{x:.0f}" cy="{yv:.0f}" r="4" fill="{col}"/>')
    S.append(f'<text x="{x:.0f}" y="{yy0+hh+18}" text-anchor="middle" '
             f'class="h">{tz}ms</text>')
S.append(f'<text x="{mx1+8}" y="{sc(0,mv0,mv1,yy0,hh)+4:.0f}" class="h">0</text>')
S.append(f'<text x="{mx0-8}" y="{yy0+hh+40}" class="h" fill="#e06c75">'
         f'mixed sign every tau — not resolvable at DT 2 ms</text>')
S.append("</svg>")
open("l21/delay.svg", "w").write("\n".join(S))
subprocess.run(["rsvg-convert", "-w", "1400", "-b", "#282c34",
                "-o", "l21/delay.png", "l21/delay.svg"], check=True)
print("wrote l21/delay.svg + delay.png")
