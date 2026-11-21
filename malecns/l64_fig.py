"""L64 figure: echo dose-phase map (hand-built SVG, house style)."""
import json
import numpy as np

r = json.load(open("l64/results.json"))
rs = json.load(open("l64/results_sham.json"))
GAINS = [(".1", "01"), (".25", "025"), (".5", "05")]
DELAYS = [("20ms", "02"), ("50ms", "05"), ("100ms", "10"), ("200ms", "20")]


def cell(gi, di, si):
    return r["grid"][f"g{gi}_d{di}_{si}"]


def color(v):
    # lift -.28..+.21 -> red..neutral gray..green
    t = max(-1.0, min(1.0, v / 0.28))
    if t >= 0:
        rr, gg, bb = int(120 + 60 * (1 - t)), int(120 + 100 * t), int(120 + 40 * (1 - t))
    else:
        rr, gg, bb = int(120 + 110 * (-t)), int(120 + 80 * t), int(120 + 30 * t)
    return f"rgb({rr},{gg},{bb})"


W, H = 1200, 560
CX, CY = 165, 96
CW, CH, GAP = 236, 74, 10
s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="DejaVu Sans, sans-serif">')
s.append(f'<rect width="{W}" height="{H}" fill="#16181d"/>')
s.append('<text x="24" y="34" fill="#e8e4da" font-size="19" font-weight="bold">'
         'L64 body-echo dose–phase map — off-window antagonist duty lift vs open '
         '(3 seeds: 11/22/33)</text>')
s.append('<text x="24" y="56" fill="#9aa0aa" font-size="13">'
         'delayed own-motor-mass echo onto leg mechanosensory; chop schedule; '
         'green = structure lift, red = loss; + / − = echo sign</text>')
for j, (dl, di) in enumerate(DELAYS):
    x = CX + j * (CW + GAP)
    s.append(f'<text x="{x + CW/2}" y="{CY - 14}" fill="#c8cdd6" font-size="14" '
             f'text-anchor="middle">delay {dl}</text>')
for i, (gl, gi) in enumerate(GAINS):
    y = CY + i * (CH + GAP)
    s.append(f'<text x="{CX - 16}" y="{y + CH/2 + 5}" fill="#c8cdd6" font-size="14" '
             f'text-anchor="end">gain {gl}</text>')
    for j, (_, dj) in enumerate(DELAYS):
        x = CX + j * (CW + GAP)
        for k, si in enumerate(("p", "m")):
            c = cell(gi, dj, si)
            hx = x + k * (CW / 2 + 2)
            hw = CW / 2 - 2
            lift = c["lift_mean"]
            win = c["pass_P1"]
            content = False
            if f"g{gi}_d{dj}_{si}" == "g01_d05_m":
                content = rs["verdict"]["g01_d05_m"]["content"]
            stroke = "#2c3038"
            sw = 1
            if win:
                stroke, sw = "#e8e4da", 1.5
            if content:
                stroke, sw = "#7de08b", 3
            sign = "+" if si == "p" else "−"
            s.append(f'<rect x="{hx:.0f}" y="{y}" width="{hw:.0f}" height="{CH}" '
                     f'rx="6" fill="{color(lift)}" stroke="{stroke}" '
                     f'stroke-width="{sw}"/>')
            s.append(f'<text x="{hx + 6:.0f}" y="{y + 16}" fill="#3a3f48" '
                     f'font-size="11" font-weight="bold">echo {sign}</text>')
            s.append(f'<text x="{hx + hw/2:.0f}" y="{y + 40}" fill="#101216" '
                     f'font-size="17" font-weight="bold" text-anchor="middle">'
                     f'{lift:+.3f}</text>')
            e2m = c["e2_med"]
            s.append(f'<text x="{hx + hw/2:.0f}" y="{y + 58}" fill="#3a3f48" '
                     f'font-size="11" text-anchor="middle">lock {e2m:.3f}</text>')
            if c["cat"]:
                s.append(f'<text x="{hx + hw/2:.0f}" y="{y + 70}" fill="#7a1f1f" '
                         f'font-size="11" font-weight="bold" text-anchor="middle">'
                         f'LOCK LOSS</text>')
# verdict strip
vy = CY + 3 * (CH + GAP) + 18
s.append(f'<line x1="24" y1="{vy - 12}" x2="{W-24}" y2="{vy - 12}" '
         f'stroke="#2c3038" stroke-width="1"/>')
s.append('<text x="24" y="470" fill="#7de08b" font-size="14" font-weight="bold">'
         'CONTENT CELL  gain .1 · sign − · 50 ms:  fb +.190 (3/3 seeds)  vs  '
         'donor sham −.068  →  loop-content benefit, lock pristine (.0003–.0011)</text>')
s.append('<text x="24" y="492" fill="#d9a94e" font-size="14">'
         'PERTURBATION CELL  gain .1 · + · 200 ms:  fb +.205 vs sham +.160 → '
         'mass-carried (donor does it too; sham crashes one seed\'s lock .334)</text>')
s.append('<text x="24" y="514" fill="#e07b7b" font-size="14">'
         'gain .5 hurts EVERYWHERE (−.038..−.280, all signs/delays) — dose dominates '
         'phase; L63 point (g .5 / 100 ms / +) = −.250 reproduced</text>')
s.append('<text x="24" y="536" fill="#9aa0aa" font-size="12">'
         'open baseline off-duty .288 (.227/.250/.386) · seg2 lock open .0016 · '
         'no floor-buried cells (all dm ≥ .059)</text>')
s.append('<text x="24" y="552" fill="#9aa0aa" font-size="12">'
         'anchors C0/C0x/C0P/C1 all pass · g05_d10_p bit-identical to L63 fbh · '
         'grid 24 cells × 3 seeds, CPU 295 s</text>')
s.append('</svg>')
open("l64/grid.svg", "w").write("\n".join(s))
print("svg written", len("\n".join(s)))
