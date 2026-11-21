#!/usr/bin/env python3
"""L41 figure — S(Tr) per arm/seed/segment vs the .25 gate + seg1 tracking err.
Hand-built SVG (house style) -> rsvg-convert PNG."""
import json
import subprocess

r = json.load(open("l41/results_l41.json"))["verdict"]
ARMS = ["free", "ent", "base", "ramp_mm", "ramp_pm", "phase", "side", "combo"]
SEEDS = ["11", "22", "33"]
SEED_C = {"11": "#0e7c86", "22": "#c2405a", "33": "#b8860b"}
GATE = 0.25

W, H = 980, 470
L, Rm, T, B = 66, 24, 46, 88
PW1 = 560
pH = H - T - B
x0 = L
def xa(i):  # arm center in panel A
    return L + (i + 0.5) * (PW1 / len(ARMS))
# S range -0.4..0.9
def yS(v): return T + (0.9 - v) / 1.3 * pH

L2 = L + PW1 + 70
PW2 = W - L2 - Rm
def xb(i): return L2 + (i + 0.5) * (PW2 / len(ARMS))
# err range 0..0.7
def yE(v): return T + (0.7 - v) / 0.7 * pH

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
     f'font-family="DejaVu Sans, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#161a21"/>',
     '<text x="24" y="24" fill="#e8e4d8" font-size="17" font-weight="bold">'
     'L41 structure-preserving transitions: no guard holds the .25 floor; '
     'the lock-vs-structure tradeoff is measured</text>',
     '<text x="24" y="44" fill="#9aa3b2" font-size="12">'
     'seg S(Tr) per arm (L39 form; 3 seeds x 3 segments) &#183; '
     'hop = DNge046 &#183; targets 0.7&#8594;1.4&#8594;0.7 Hz</text>']

# panel A frame
s.append(f'<rect x="{L}" y="{T}" width="{PW1}" height="{pH}" fill="#1c2129" '
         f'stroke="#39414e"/>')
for v, lab, dash in ((0.9, "0.9", "none"), (0.5, "0.5", "none"),
                     (0.25, "gate .25", "6 4"), (0.0, "0", "2 3"),
                     (-0.4, "-0.4", "none")):
    s.append(f'<line x1="{L}" y1="{yS(v):.1f}" x2="{L+PW1}" y2="{yS(v):.1f}" '
             f'stroke="{"#c2405a" if v == 0.25 else "#39414e"}" '
             f'stroke-dasharray="{dash}" stroke-width="{2 if v == 0.25 else 1}"/>')
    s.append(f'<text x="{L-6}" y="{yS(v)+4:.1f}" fill="#9aa3b2" font-size="11" '
             f'text-anchor="end">{lab}</text>')
s.append(f'<text x="{L+8}" y="{T+pH-8}" fill="#e8e4d8" font-size="13" '
         f'font-weight="bold">A &#183; segment S(Tr)</text>')

for i, a in enumerate(ARMS):
    for si, sd in enumerate(SEEDS):
        for g in range(3):
            v = r["S"][a][sd][g]
            cx = xa(i) + (g - 1) * 6
            cy = yS(v)
            mark = "o" if g != 1 else "s"
            fill = SEED_C[sd] if g != 1 else "none"
            if mark == "o":
                s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.6" '
                         f'fill="{fill}" stroke="{SEED_C[sd]}" stroke-width="1.4"/>')
            else:  # seg1 square, hollow = the transition segment
                s.append(f'<rect x="{cx-4.4:.1f}" y="{cy-4.4:.1f}" width="8.8" '
                         f'height="8.8" fill="none" stroke="{SEED_C[sd]}" '
                         f'stroke-width="1.8"/>')
    # arm label + min
    mn = r["min_seg_S"][a]
    s.append(f'<text x="{xa(i):.1f}" y="{T+pH+18}" fill="#e8e4d8" font-size="11" '
             f'text-anchor="middle">{a}</text>')
    s.append(f'<text x="{xa(i):.1f}" y="{T+pH+32}" fill="#{"7fd08a" if mn >= 0.25 else "#c2405a"}" '
             f'font-size="10" text-anchor="middle">min {mn:+.3f}</text>')

# panel B frame
s.append(f'<rect x="{L2}" y="{T}" width="{PW2}" height="{pH}" fill="#1c2129" '
         f'stroke="#39414e"/>')
for v, lab in ((0.7, "0.7"), (0.35, "0.35"), (0.05, "0.05"), (0.0, "0")):
    s.append(f'<line x1="{L2}" y1="{yE(v):.1f}" x2="{L2+PW2}" y2="{yE(v):.1f}" '
             f'stroke="#39414e"/>')
    s.append(f'<text x="{L2-6}" y="{yE(v)+4:.1f}" fill="#9aa3b2" font-size="11" '
             f'text-anchor="end">{lab}</text>')
s.append(f'<text x="{L2+8}" y="{T+16}" fill="#e8e4d8" font-size="13" '
         f'font-weight="bold">B &#183; seg1 tracking err (lower = better)</text>')
s.append(f'<text x="{L2+8}" y="{T+31}" fill="#9aa3b2" font-size="10">'
         'the square volley buys ~.001; gentler forms lose the 1.4 lock</text>')
for i, a in enumerate(ARMS):
    for sd in SEEDS:
        v = r["track"][a][sd][1]
        s.append(f'<line x1="{xb(i)-5:.1f}" y1="{yE(0):.1f}" x2="{xb(i)-5:.1f}" '
                 f'y2="{yE(v):.1f}" stroke="{SEED_C[sd]}" stroke-width="1"/>')
        s.append(f'<circle cx="{xb(i)-5:.1f}" cy="{yE(v):.1f}" r="4.2" '
                 f'fill="{SEED_C[sd]}"/>')
    s.append(f'<text x="{xb(i):.1f}" y="{T+pH+16}" fill="#e8e4d8" font-size="10" '
             f'text-anchor="end" transform="rotate(-38 {xb(i):.1f} {T+pH+16})">{a}</text>')

# legend
ly = H - 34
for sd in SEEDS:
    lx = 90 + SEEDS.index(sd) * 130
    s.append(f'<circle cx="{lx}" cy="{ly}" r="5" fill="{SEED_C[sd]}"/>')
    s.append(f'<text x="{lx+10}" y="{ly+4}" fill="#e8e4d8" font-size="12">seed {sd}</text>')
s.append(f'<rect x="{470}" y="{ly-5}" width="10" height="10" fill="none" '
         f'stroke="#e8e4d8" stroke-width="1.8"/>')
s.append(f'<text x="486" y="{ly+4}" fill="#e8e4d8" font-size="12">seg1 (0.7&#8594;1.4 transition), '
         'hollow = transition segment</text>')
s.append('</svg>')
open("l41/transitions.svg", "w").write("\n".join(s))
subprocess.run(["rsvg-convert", "-w", "1470", "l41/transitions.svg",
                "-o", "l41/transitions.png"], check=True)
print("wrote l41/transitions.png")
