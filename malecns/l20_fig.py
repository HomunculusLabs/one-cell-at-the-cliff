"""L20 figure: crouch-then-jump, descriptive (owner movement law — lab
evidence only, never app-side motion).

Panels:
  A : two-phase DEL=60 — flexor/extensor pool means + theta(t), volley
      onsets marked (crouch k=0-20, stroke k=60-80)
  B : controls — crouch-only theta (pure trough) vs stroke-only (pure swing)
  C : stroke recovery vs DEL — peak theta by DEL with biphasic verdicts
      (DEL=30 swallowed by the slow flexor = cannot jump mid-crouch)

Reads l20/two_phase.npz + l20/results_l20.json; writes l20/crouch.svg/.png.
"""
import json
import subprocess

import numpy as np

d = np.load("l20/two_phase.npz")
res = json.load(open("l20/results_l20.json"))
DEL = int(d["del_"])
CRO, STR = 20, 20
theta, flex, ext, ttm = d["theta"], d["flex"], d["ext"], d["ttm"]
th_c, th_s = d["theta_cro"], d["theta_str"]
T = theta.shape[1]
noise = res["theta_noise"]

MX, W_P = 78, 860
H_A = 300
Y_A = 60
Y_B = Y_A + H_A + 64
H_B = 190
Y_C = Y_B + H_B + 64
H_C = 170
TOT_W = MX + W_P + 210
TOT_H = Y_C + H_C + 70
PURPLE, ORANGE, BLUE, GREY = "#c678dd", "#ffb454", "#61afef", "#5c6370"


def xpx(k):
    return MX + W_P * k / (T - 1)


def line(y_px, tr, color, w=2.2, dash=None, y0=None, y1=None, h=None):
    if y0 is None:
        y0, y1 = tr.min(), tr.max()
    if h is None:
        h = H
    pts = " ".join(f"{xpx(k):.1f},{py(v, y0, y1, y_px, h):.1f}"
                   for k, v in enumerate(tr))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{dd} stroke-linejoin="round"/>')


def py(v, v0, v1, ytop, h):
    return ytop + h - (v - v0) / (v1 - v0 + 1e-12) * h


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOT_W}" '
       f'height="{TOT_H}" font-family="DejaVu Sans" '
       f'viewBox="0 0 {TOT_W} {TOT_H}">',
       f'<rect width="{TOT_W}" height="{TOT_H}" fill="#282c34"/>',
       '<text x="24" y="30" fill="#abb2bf" font-size="19">'
       'L20 crouch-then-jump (descriptive): DNg flexor volley -> DNp01-04 volley, lit5x taus'
       '</text>']

# --- panel A: two-phase --------------------------------------------------
H = H_A - 46
ytop = Y_A + 34
svg.append(f'<text x="{MX}" y="{Y_A+18}" fill="#abb2bf" font-size="15">'
           f'A two-phase DEL={DEL} (3 seeds, mean) — pools and theta = ext − flex</text>')
pool0 = min(flex.mean(0).min(), ext.mean(0).min())
pool1 = max(flex.mean(0).max(), ext.mean(0).max()) * 1.12
svg.append(line(ytop, flex.mean(0), PURPLE, 2.6, y0=pool0, y1=pool1, h=95))
svg.append(line(ytop, ext.mean(0), ORANGE, 2.6, y0=pool0, y1=pool1, h=95))
# TTMn on its own sub-scale (L19 lesson: jump MN dwarfs leg pools)
ttm0, ttm1 = ttm.mean(0).min(), ttm.mean(0).max() * 1.1
svg.append(line(ytop + 105, ttm.mean(0), BLUE, 2.0, y0=ttm0, y1=ttm1, h=62))
th0 = theta.mean(0).min() * 1.25
th1 = max(theta.mean(0).max() * 1.35, 0.004)
svg.append(line(ytop + 180, theta.mean(0), "#e5c07b", 3.0, y0=th0, y1=th1,
                h=H - 188))
for k0, k1, lab, col in [(0, CRO, "crouch", PURPLE), (DEL, DEL + STR, "stroke", ORANGE)]:
    x0, x1 = xpx(k0), xpx(k1)
    svg.append(f'<rect x="{x0:.0f}" y="{ytop}" width="{x1-x0:.0f}" '
               f'height="{H_A-40}" fill="{col}" opacity="0.10"/>')
    svg.append(f'<text x="{x0:.0f}" y="{ytop-8}" fill="{col}" '
               f'font-size="13">{lab}</text>')
svg.append(f'<text x="{xpx(23)-60:.0f}" y="{py(theta.mean(0).min(), th0, th1, ytop+180, H-188)+26:.0f}" fill="#e5c07b" font-size="13">trough (crouch)</text>')
tp_x = min(max(xpx(int(np.argmax(theta.mean(0)))) - 40, MX + 8), MX + W_P - 210)
svg.append(f'<text x="{tp_x:.0f}" y="{py(theta.mean(0).max(), th0, th1, ytop+180, H-188)-8:.0f}" fill="#e5c07b" font-size="13">swing + TTMn jump</text>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+16}" fill="{PURPLE}" font-size="13">Ti/Tr flexors</text>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+32}" fill="{ORANGE}" font-size="13">Ti/Tr extensors</text>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+117}" fill="{BLUE}" font-size="13">TTMn (jump)</text>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+192}" fill="#e5c07b" font-size="13">theta = ext − flex</text>')

# --- panel B: controls ---------------------------------------------------
H = H_B - 40
ytop = Y_B + 78
svg.append(f'<text x="{MX}" y="{Y_B+22}" fill="#abb2bf" font-size="15">'
           'B controls — crouch-only (pure trough) vs stroke-only (pure swing), theta</text>')
c0 = min(th_c.mean(0).min(), th_s.mean(0).min()) * 1.2
c1 = max(th_c.mean(0).max(), th_s.mean(0).max()) * 1.3
svg.append(line(ytop, th_c.mean(0), PURPLE, 2.6, y0=c0, y1=c1))
svg.append(line(ytop, th_s.mean(0), ORANGE, 2.6, y0=c0, y1=c1))
svg.append(f'<line x1="{MX}" x2="{MX+W_P}" y1="{py(0, c0, c1, ytop, H):.1f}" '
           f'y2="{py(0, c0, c1, ytop, H):.1f}" stroke="#5c6370" stroke-width="1"/>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+16}" fill="{PURPLE}" font-size="13">crouch-only</text>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+32}" fill="{ORANGE}" font-size="13">stroke-only</text>')
svg.append(f'<text x="{xpx(95):.0f}" y="{Y_B+H_B-2}" fill="{PURPLE}" font-size="13">−0.079 trough, no swing</text>')
svg.append(f'<text x="{xpx(230):.0f}" y="{Y_B+H_B-2}" fill="{ORANGE}" font-size="13">+0.031 swing, no dip</text>')

# --- panel C: DEL sweep --------------------------------------------------
H = H_C - 46
ytop = Y_C + 32
svg.append(f'<text x="{MX}" y="{Y_C+18}" fill="#abb2bf" font-size="15">'
           'C stroke recovery vs crouch-stroke delay DEL (peak theta; biphasic?)</text>')
dels = sorted(int(k) for k in res["two_phase"])
peaks = [np.mean([s["peak"] for s in res["two_phase"][str(k)]["theta"]]) for k in dels]
so_pk = np.mean([s["peak"] for s in res["stroke_only"]])
p0, p1 = 0, so_pk * 1.25
for k, pk, bip in zip(dels, peaks, [res["biphasic"][str(k)] for k in dels]):
    x = MX + 60 + (W_P - 160) * (k - dels[0]) / (dels[-1] - dels[0])
    y = py(pk, p0, p1, ytop, H)
    col = "#98c379" if bip else "#e06c75"
    svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{col}"/>')
    svg.append(f'<text x="{x-14:.0f}" y="{y-16:.0f}" fill="{col}" font-size="14">'
               f'{"biphasic" if bip else "swallowed"} DEL={k}</text>')
svg.append(f'<line x1="{MX+40}" x2="{MX+W_P-60}" y1="{py(so_pk, p0, p1, ytop, H):.1f}" y2="{py(so_pk, p0, p1, ytop, H):.1f}" stroke="#61afef" stroke-dasharray="6 5" stroke-width="1.6"/>')
svg.append(f'<text x="{MX+52:.0f}" y="{py(so_pk, p0, p1, ytop, H)-10:.0f}" fill="#61afef" font-size="13">stroke-only peak (full swing)</text>')
svg.append(f'<text x="{MX+W_P+10}" y="{ytop+H+16}" fill="#5c6370" font-size="12">'
           f'flexor tau 255 ms swallows the stroke at DEL=30 — cannot jump mid-crouch</text>')

svg.append("</svg>")
open("l20/crouch.svg", "w").write("\n".join(svg))
subprocess.run(["rsvg-convert", "-w", "1400", "l20/crouch.svg",
                "-o", "l20/crouch.png"], check=True)
print("wrote l20/crouch.svg + crouch.png")
