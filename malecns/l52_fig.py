"""L52 figure: (A) duty-vs-dwell curves per arm (6-s bins, mean over seeds;
per-seed dots on the two canonical arms) with early/late windows shaded;
(B) early-vs-late plane per seed — transient points sit above the diagonal
crossing .25, selection points cluster low-low; (C) t70 sensitivity table.
Numbers from l52/results_l52.json + traces_l52.npz. SVG -> rsvg-convert."""
import json
import subprocess

import numpy as np

SEEDS = [11, 22, 33]
FREQS, AMPS = (0.7, 1.4), (0.3, 0.2, 0.1)
ARMS = [f"f{int(f*10):02d}a{int(am*10)}" for f in FREQS for am in AMPS]
res = json.load(open("l52/results_l52.json"))
W, H = 1560, 940
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
FCOL = {0.7: "#7fb3ff", 1.4: "#ff8f7f"}
ADASH = {0.3: "none", 0.2: "7 4", 0.1: "2 3"}
AW = {0.3: 3.5, 0.2: 2.5, 0.1: 2.0}
ver = res["verdict"]
sens = res["sensitivity"]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L52 fast-segment toxicity: {ver.split(" (")[0]}</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">single 60-s '
       f'treatment from the shared h40 state, no transitions; duty = both S '
       f'sides &#8805; .25 (rolling 5 s, 6-s bins); mean over seeds 11/22/33 '
       f'unless dotted</text>']

# ---------- panel A: duty vs dwell ----------
ax, ay, aw, ah = 60, 120, 760, 460


def AX(t):
    return ax + 50 + (aw - 90) * t / 60.0


def AY(v):
    return ay + (ah - 50) * (1 - v)


svg.append(f'<text x="{ax}" y="{ay-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">A &#8226; duty vs dwell in treatment '
           f'(solid amp .3, dash .2, dot .1; blue 0.7 Hz, red 1.4 Hz)</text>')
# early/late shading: early [0,20), late [20,60)
svg.append(f'<rect x="{AX(0):.1f}" y="{ay}" width="{AX(20)-AX(0):.1f}" '
           f'height="{ah-50}" fill="#ffffff" fill-opacity="0.03"/>')
svg.append(f'<rect x="{AX(20):.1f}" y="{ay}" width="{AX(60)-AX(20):.1f}" '
           f'height="{ah-50}" fill="#ffffff" fill-opacity="0.06"/>')
svg.append(f'<text x="{AX(10):.1f}" y="{ay+16}" fill="{MUT}" font-size="12" '
           f'text-anchor="middle">early (first 20 s)</text>')
svg.append(f'<text x="{AX(40):.1f}" y="{ay+16}" fill="{MUT}" font-size="12" '
           f'text-anchor="middle">late (last 20 s)</text>')
svg.append(f'<rect x="{ax+50}" y="{ay}" width="{aw-90}" height="{ah-50}" '
           f'fill="none" stroke="{GRID}"/>')
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    dash = "5 3" if abs(v - 0.25) < 1e-9 else "2 4"
    svg.append(f'<line x1="{ax+50}" y1="{AY(v):.1f}" x2="{ax+aw-40}" '
               f'y2="{AY(v):.1f}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{ax+44}" y="{AY(v)+4:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="end">{v:.2f}</text>')
for t in (0, 10, 20, 30, 40, 50, 60):
    svg.append(f'<line x1="{AX(t):.1f}" y1="{ay+ah-50}" x2="{AX(t):.1f}" '
               f'y2="{ay+ah-44}" stroke="{MUT}"/>')
    svg.append(f'<text x="{AX(t):.1f}" y="{ay+ah-26}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{t} s</text>')
svg.append(f'<text x="{ax+(aw-40)/2+12}" y="{ay+ah-6}" fill="{MUT}" '
           f'font-size="13" text-anchor="middle">dwell time at treatment '
           f'frequency (treatment starts at 40 s of 0.7-Hz h40)</text>')
svg.append(f'<text x="{ax+14}" y="{ay+(ah-50)/2}" fill="{MUT}" '
           f'font-size="13" transform="rotate(-90 {ax+14} '
           f'{ay+(ah-50)/2})">bilateral structure duty</text>')
for f in FREQS:
    for am in AMPS:
        a = f"f{int(f*10):02d}a{int(am*10)}"
        bins = [float(np.mean([res["rows"][a][str(s)]["bins"][i]
                               for s in map(str, SEEDS)]))
                for i in range(10)]
        pts = " ".join(f"{AX(3+6*i):.1f},{AY(b):.1f}" for i, b in enumerate(bins))
        svg.append(f'<polyline points="{pts}" fill="none" '
                   f'stroke="{FCOL[f]}" stroke-width="{AW[am]}" '
                   f'stroke-dasharray="{ADASH[am]}" '
                   f'stroke-opacity="{1.0 if am == 0.3 else 0.75}"/>')
for a in ("f07a3", "f14a3"):                      # per-seed dots, canonical
    f = 0.7 if a.startswith("f07") else 1.4
    for s in SEEDS:
        for i, b in enumerate(res["rows"][a][str(s)]["bins"]):
            svg.append(f'<circle cx="{AX(3+6*i):.1f}" cy="{AY(b):.1f}" r="3.4" '
                       f'fill="{SEED_COL[s]}" fill-opacity="0.8"/>')
svg.append(f'<text x="{ax+aw-46}" y="{ay+ah-62}" fill="{MUT}" '
           f'font-size="12" text-anchor="end">dots: per-seed bins of the '
           f'amp-.3 arms</text>')

# ---------- panel B: early vs late ----------
bx, by, bw, bh = 880, 120, 620, 460


def BX(v):
    return bx + 50 + (bw - 90) * v


def BY(v):
    return by + (bh - 50) * (1 - v)


svg.append(f'<text x="{bx}" y="{by-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">B &#8226; early vs late duty per seed '
           f'(cross-hair .25/.25)</text>')
svg.append(f'<rect x="{bx+50}" y="{by}" width="{bw-90}" height="{bh-50}" '
           f'fill="none" stroke="{GRID}"/>')
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    for X, Y, Wd in ((bx, by, bw), ):
        pass
    dash = "5 3" if abs(v - 0.25) < 1e-9 else "2 4"
    svg.append(f'<line x1="{BX(v):.1f}" y1="{by}" x2="{BX(v):.1f}" '
               f'y2="{by+bh-50}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
    svg.append(f'<line x1="{bx+50}" y1="{BY(v):.1f}" x2="{bx+bw-40}" '
               f'y2="{BY(v):.1f}" stroke="{GRID}" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{BX(v):.1f}" y="{by+bh-26}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{v:.2f}</text>')
    svg.append(f'<text x="{bx+44}" y="{BY(v)+4:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="end">{v:.2f}</text>')
svg.append(f'<line x1="{BX(0):.1f}" y1="{BY(0):.1f}" x2="{BX(1):.1f}" '
           f'y2="{BY(1):.1f}" stroke="{MUT}" stroke-width="1" '
           f'stroke-dasharray="1 3"/>')
svg.append(f'<text x="{bx+(bw-40)/2+12}" y="{by+bh-6}" fill="{MUT}" '
           f'font-size="13" text-anchor="middle">early duty (first 20 s)</text>')
svg.append(f'<text x="{bx+14}" y="{by+(bh-50)/2}" fill="{MUT}" '
           f'font-size="13" transform="rotate(-90 {bx+14} '
           f'{by+(bh-50)/2})">late duty (last 20 s)</text>')
for f in FREQS:
    for am in AMPS:
        a = f"f{int(f*10):02d}a{int(am*10)}"
        for s in SEEDS:
            r = res["rows"][a][str(s)]
            x, y = BX(r["early"]), BY(r["late"])
            if f == 1.4:                      # diamond
                svg.append(f'<path d="M {x:.1f} {y-7:.1f} L {x+7:.1f} {y:.1f} '
                           f'L {x:.1f} {y+7:.1f} L {x-7:.1f} {y:.1f} Z" '
                           f'fill="{SEED_COL[s]}" fill-opacity="0.8" '
                           f'stroke="{FCOL[f]}" stroke-width="{4 if am==0.3 else 1.6}"/>')
            else:
                svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" '
                           f'r="{7 if am==0.3 else 4.5}" fill="{SEED_COL[s]}" '
                           f'fill-opacity="0.8" stroke="{FCOL[f]}" '
                           f'stroke-width="{4 if am==0.3 else 1.6}"/>')
svg.append(f'<text x="{bx+bw-44}" y="{by+20}" fill="{MUT}" font-size="12" '
           f'text-anchor="end">circle 0.7 / diamond 1.4; size &#8226; amp '
           f'.3 big, .2/.1 small; color = seed</text>')

# ---------- panel C: sensitivity table ----------
ty = 640
svg.append(f'<text x="60" y="{ty}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C &#8226; amp x freq sensitivity (t70 rule) '
           f'&#8212; canonical f14a3 verdict: {ver}</text>')
cols = [("arm", 60), ("duty_e", 280), ("duty_l", 370), ("slope", 460),
        ("lock err s11/s22/s33", 550), ("lock", 720), ("verdict", 880),
        ("vs canonical", 1040)]
svg.append(f'<text x="60" y="{ty+28}" fill="{MUT}" font-size="13">'
           + " ".join(f'<tspan x="{x}">{c}</tspan>' for c, x in cols)
           + '</text>')
yy = ty + 52
for f in FREQS:
    for am in AMPS:
        a = f"f{int(f*10):02d}a{int(am*10)}"
        r = sens[a]
        errs = "/".join(f'{r["err"][s]:.2f}' for s in map(str, SEEDS))
        locks = "/".join(r["lock"][s][:4] for s in map(str, SEEDS))
        col = FG if a == "f14a3" else MUT
        wt = ' font-weight="bold"' if a == "f14a3" else ''
        svg.append(f'<text x="60" y="{yy}" fill="{col}" font-size="13"{wt}>'
                   f'<tspan x="60">{a} ({f} Hz @ amp {am})</tspan>'
                   f'<tspan x="280">{r["duty_early"]:.3f}</tspan>'
                   f'<tspan x="370">{r["duty_late"]:.3f}</tspan>'
                   f'<tspan x="460">{r["slope"]:+.3f}</tspan>'
                   f'<tspan x="550">{errs}</tspan>'
                   f'<tspan x="720">{locks}</tspan>'
                   f'<tspan x="880">{r["verdict"]}</tspan>'
                   f'<tspan x="1040">{r["knob"]}</tspan></text>')
        yy += 24
svg.append(f'<text x="60" y="{yy+14}" fill="{MUT}" font-size="12">'
           f'GC anchor (f07a3 = l49 cont bit-identical): '
           f'{res["GC"]["got"]} vs expect {res["GC"]["expect"]} '
           f'| C0 pass {res["C0_pass"]} | C1 pass {res["C1"]["pass_"]}</text>')
svg.append("</svg>")
open("l52/toxic.svg", "w").write("\n".join(svg))
subprocess.run(["rsvg-convert", "-o", "l52/toxic.png", "l52/toxic.svg"],
               check=True)
print("wrote l52/toxic.png")
