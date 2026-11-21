#!/usr/bin/env python3
"""L42 figure — the stack trajectory: motor rhythm (A), rolling antagonist
structure with the restart reset (B), per-block frequency vs target (C).
Hand-built SVG (house style) -> rsvg-convert PNG."""
import json
import subprocess

import numpy as np

z = np.load("l42/traces.npz")
r = json.load(open("l42/results_l42.json"))
SEGS = [(0, 2000, "0.7 Hz"), (2000, 4000, "1.4 Hz"), (4000, 5000, "STOP"),
        (5000, 7000, "0.7 Hz")]
TG = np.array([0.7, 1.4, 0.0, 0.7])

W, H = 1180, 700
BGc, PANEL, FG, MUT = "#161a21", "#1c2129", "#e8e4d8", "#9aa3b2"
L, Rm = 78, 20
PH = 168
GAP = 58
TS = [46 + i * (PH + GAP) for i in range(3)]


def xs(k):  # steps -> panel x (0..70 s window)
    return L + k / 7000.0 * (W - L - Rm)


s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
     f'font-family="DejaVu Sans, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="{BGc}"/>',
     '<text x="24" y="24" fill="#e8e4d8" font-size="17" font-weight="bold">'
     'L42 entrain-hop-stop stack: frequency tracked end-to-end; the 10-s stop '
     'suppresses structure but does not park the cord</text>',
     '<text x="24" y="44" fill="#9aa3b2" font-size="12">'
     'frozen L32 substrate &#183; stack = entrain .3 + DNge046 hops (@20 s, '
     '@50 s) + DNg88 -8 (40-50 s) &#183; targets 0.7&#8594;1.4&#8594;STOP&#8594;0.7 Hz</text>']

for pi in range(3):
    T = TS[pi]
    s.append(f'<rect x="{L}" y="{T}" width="{W-L-Rm}" height="{PH}" '
             f'fill="{PANEL}" stroke="#2a303c"/>')
    # segment bands
    for i, (a, b, lab) in enumerate(SEGS):
        if lab == "STOP":
            s.append(f'<rect x="{xs(a):.1f}" y="{T}" width="{xs(b)-xs(a):.1f}" '
                     f'height="{PH}" fill="#5c2a35" opacity="0.45"/>')
        if i:
            s.append(f'<line x1="{xs(a):.1f}" y1="{T}" x2="{xs(a):.1f}" '
                     f'y2="{T+PH}" stroke="#3a4150" stroke-dasharray="3 4"/>')
        s.append(f'<text x="{(xs(a)+xs(b))/2:.1f}" y="{T+14}" fill="{MUT}" '
                 f'font-size="11" text-anchor="middle">{lab}</text>')
    for sec in (0, 20, 40, 50, 70):
        s.append(f'<text x="{xs(sec*100):.1f}" y="{T+PH+16}" fill="{MUT}" '
                 f'font-size="10" text-anchor="middle">{sec}s</text>')
    s.append(f'<text x="{L-8}" y="{T+PH/2+4}" fill="{MUT}" font-size="11" '
             f'text-anchor="end" transform="rotate(-90 {L-8} {T+PH/2})">'
             f'{["motor mean", "rolling S(Tr)", "block f (Hz)"][pi]}</text>')
    s.append(f'<text x="{L+8}" y="{T+PH-8}" fill="{FG}" font-size="12" '
             f'font-weight="bold">{"ABC"[pi]} &#183; '
             f'{["stack motor trace (seed 22)", "rolling antagonist structure (seed 11)",
                 "stack frequency vs target"][pi]}</text>')

# ---- panel A: mm traces seed 22 ----
T = TS[0]
mm = {"free": z["mm_free_22"], "ent": z["mm_ent_22"], "stack": z["mm_stack_22"]}
allv = np.concatenate([v for v in mm.values()])
lo, hi = allv.min(), allv.max()


def yA(v):
    return T + 12 + (hi - v) / max(hi - lo, 1e-9) * (PH - 40)


STYLE = {"free": ("#77839a", "4 4", 1.5), "ent": ("#c2405a", "", 1.4),
         "stack": ("#e8e4d8", "", 2.0)}
for a, (c, dash, wd) in STYLE.items():
    v = mm[a]
    step = 12
    pts = " ".join(f"{xs(k):.1f},{yA(v[k]):.1f}" for k in range(0, 7000, step))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" '
             f'stroke-width="{wd}" {f"stroke-dasharray=\"{dash}\"" if dash else ""}/>')
s.append(f'<rect x="{L+8}" y="{T+PH-40}" width="228" height="26" '
         f'fill="{BGc}" opacity="0.82"/>')
lx = L + 14
for a, (c, dash, wd) in STYLE.items():
    s.append(f'<line x1="{lx}" y1="{T+PH-27}" x2="{lx+26}" y2="{T+PH-27}" '
             f'stroke="{c}" stroke-width="{wd}" '
             f'{f"stroke-dasharray=\"{dash}\"" if dash else ""}/>')
    s.append(f'<text x="{lx+32}" y="{T+PH-23}" fill="{FG}" font-size="11">{a}</text>')
    lx += 76

# ---- panel B: S_roll seed 11 ----
T = TS[1]
t = np.arange(499, 7000, 10)
SRO = {"stack": z["SR_stack_11"][t], "entstop": z["SR_entstop_11"][t],
       "stack_lo": z["SR_stack_lo_11"][t]}


def yB(v):
    return T + 10 + (1.0 - v) / 1.9 * (PH - 34)


for gv in (0.25,):
    s.append(f'<line x1="{L}" y1="{yB(gv):.1f}" x2="{W-Rm}" y2="{yB(gv):.1f}" '
             f'stroke="#b8860b" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{L+8}" y="{yB(gv)-5:.1f}" fill="#b8860b" '
             f'font-size="10">S = .25 gate</text>')
for gv in (-1, 0, 1):
    s.append(f'<text x="{L-6}" y="{yB(gv)+4:.1f}" fill="{MUT}" font-size="10" '
             f'text-anchor="end">{gv:+d}</text>')
SB = {"stack": ("#e8e4d8", "", 2.0), "entstop": ("#c2405a", "7 4", 1.4),
      "stack_lo": ("#0e7c86", "2 4", 1.4)}
for a, (c, dash, wd) in SB.items():
    v = SRO[a]
    pts = " ".join(f"{xs(tt):.1f},{yB(x):.1f}" for tt, x in zip(t, v)
                   if not np.isnan(x))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" '
             f'stroke-width="{wd}" {f"stroke-dasharray=\"{dash}\"" if dash else ""}/>')
# restart marker: seed 11 inversion clears at 5089
s.append(f'<line x1="{xs(5089):.1f}" y1="{T+10}" x2="{xs(5089):.1f}" '
         f'y2="{T+PH-10}" stroke="#7dc98f" stroke-dasharray="2 3"/>')
s.append(f'<rect x="{L+8}" y="{T+18}" width="262" height="18" '
         f'fill="{BGc}" opacity="0.82"/>')
s.append(f'<text x="{L+14}" y="{T+31}" fill="#7dc98f" font-size="10">'
         'restart resets: 30-s inversion clears (med +.53 after)</text>')
lx = L + 14
for a, (c, dash, wd) in SB.items():
    s.append(f'<line x1="{lx}" y1="{T+PH-26}" x2="{lx+26}" y2="{T+PH-26}" '
             f'stroke="{c}" stroke-width="{wd}" '
             f'{f"stroke-dasharray=\"{dash}\"" if dash else ""}/>')
    s.append(f'<text x="{lx+32}" y="{T+PH-22}" fill="{FG}" font-size="11">{a}</text>')
    lx += 100

# ---- panel C: block f vs target, stack, 3 seeds ----
T = TS[2]
SEED_C = {"11": "#0e7c86", "22": "#c2405a", "33": "#a08fe8"}


def yC(v):
    return T + 12 + (2.2 - v) / 2.2 * (PH - 40)


for gv in (0, 0.7, 1.4, 2.0):
    s.append(f'<text x="{L-6}" y="{yC(gv)+4:.1f}" fill="{MUT}" font-size="10" '
             f'text-anchor="end">{gv:.1f}</text>')
# target step line (skip stop)
s.append(f'<polyline points="{xs(0):.1f},{yC(.7):.1f} {xs(2000):.1f},{yC(.7):.1f} '
         f'{xs(2000):.1f},{yC(1.4):.1f} {xs(4000):.1f},{yC(1.4):.1f} '
         f'{xs(4000):.1f},{yC(0):.1f} {xs(5000):.1f},{yC(0):.1f} '
         f'{xs(5000):.1f},{yC(.7):.1f} {xs(7000):.1f},{yC(.7):.1f}" '
         f'fill="none" stroke="#b8860b" stroke-width="1.6" stroke-dasharray="8 4"/>')
for sd, c in SEED_C.items():
    bl = r["blocks"]["stack"][sd]
    pts = " ".join(f"{xs(b['b']*500+250):.1f},{yC(min(b['f'],2.2)):.1f}"
                   for b in bl if b["target"] > 0)
    s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" '
             f'stroke-width="1.5" stroke-linejoin="round"/>')
lx = L + 14
s.append(f'<line x1="{lx}" y1="{T+26}" x2="{lx+26}" y2="{T+26}" '
         f'stroke="#b8860b" stroke-width="1.6" stroke-dasharray="8 4"/>')
s.append(f'<text x="{lx+32}" y="{T+30}" fill="{FG}" font-size="11">target</text>')
for sd, c in SEED_C.items():
    lx2 = lx + 84 + list(SEED_C).index(sd) * 74
    s.append(f'<line x1="{lx2}" y1="{T+26}" x2="{lx2+22}" y2="{T+26}" '
             f'stroke="{c}" stroke-width="1.5"/>')
    s.append(f'<text x="{lx2+27}" y="{T+30}" fill="{FG}" font-size="11">s{sd}</text>')
s.append(f'<text x="{W-Rm-8}" y="{T+PH-8}" fill="{MUT}" font-size="10" '
         f'text-anchor="end">stop blocks excluded (target 0)</text>')
s.append('</svg>')
open("l42/stack.svg", "w").write("\n".join(s))
subprocess.run(["rsvg-convert", "-w", "1770", "l42/stack.svg",
                "-o", "l42/stack.png"], check=True)
print("wrote l42/stack.png")
