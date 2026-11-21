"""L28 figure: grooming alternation traces (alt drive, seed 0) at 1/2/5 Hz.
flexor pool (DNg95) purple vs extensor pool (DNg79) orange, faint bands =
which DN class is vollied that half-cycle. House style: SVG + rsvg-convert.
Also prints per-seed phase stats for the LAB-INTENT entry."""
import json
import subprocess

import numpy as np

d = json.load(open("l28/results_l28.json"))
z = np.load("l28/pool_traces.npz")
DT = 0.010

BG, FG, MUT = "#282c34", "#abb2bf", "#5c6370"
PUR, ORN, BLU = "#c678dd", "#ffb454", "#61afef"

PW, PH = 560, 300
MX, GAP = 60, 40
TOT_W = MX * 2 + PW * 3 + GAP * 2
TOT_H = PH + 175
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOT_W}" '
       f'height="{TOT_H}" viewBox="0 0 {TOT_W} {TOT_H}">',
       f'<rect width="{TOT_W}" height="{TOT_H}" fill="{BG}"/>',
       f'<text x="{MX}" y="34" fill="{FG}" font-size="19" '
       f'font-family="monospace">L28 grooming: anti-phase DN drive '
       f'-&gt; anti-phase antagonist pools (seed 0)</text>']

for pi, f in enumerate(["1", "2", "5"]):
    x0 = MX + pi * (PW + GAP)
    y0 = 70
    fa = z[f"alt{f}__trF__0"]
    ea = z[f"alt{f}__trE__0"]
    T = len(fa)
    t_ms = np.arange(T) * DT * 1000
    lo = min(fa.min(), ea.min())
    hi = max(fa.max(), ea.max())
    pad = (hi - lo) * 0.08 + 1e-6
    lo, hi = lo - pad, hi + pad

    def X(k):
        return x0 + PW * k / (T - 1)

    def Y(v):
        return y0 + PH * (1 - (v - lo) / (hi - lo))

    # drive half-cycle bands: A(flex) purple / B(ext) orange, alt mode
    P = int(round(1.0 / (float(f) * DT)))
    H = max(1, P // 2)
    for cyc in range((T + P - 1) // P):
        for half, col in [(0, PUR), (1, ORN)]:
            a, b = cyc * P + half * H, min(cyc * P + (half + 1) * H, T)
            if a >= T:
                break
            svg.append(f'<rect x="{X(a):.0f}" y="{y0}" '
                       f'width="{X(b)-X(a):.1f}" height="{PH}" '
                       f'fill="{col}" opacity="0.07"/>')
    svg.append(f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" '
               f'fill="none" stroke="{MUT}"/>')

    def path(vals, col, w):
        pts = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in enumerate(vals))
        return (f'<polyline points="{pts}" fill="none" stroke="{col}" '
                f'stroke-width="{w}"/>')

    svg.append(path(fa, PUR, 2.4))
    svg.append(path(ea, ORN, 2.4))
    m = d["arms"][f"alt{f}"]["mean"]
    sc = d["arms"][f"alt{f}"]["mean_circ_phase"]
    ss = d["arms"][f"sim{f}"]["mean_circ_phase"]
    svg.append(f'<text x="{x0}" y="{y0-10}" fill="{FG}" font-size="15" '
               f'font-family="monospace">{f} Hz alt: rel phase {sc:+.0f}&#176; '
               f'(in-phase ctrl {ss:+.0f}&#176;)</text>')
    svg.append(f'<text x="{x0}" y="{y0+PH+20}" fill="{MUT}" font-size="13" '
               f'font-family="monospace">pow@f flex {m["powfrac_f"]:.2f} '
               f'ext {m["powfrac_e"]:.2f} | amp@f flex {m["amp_f"]:.3f} '
               f'ext {m["amp_e"]:.3f} | snr {m["snr_f"]:.0f}x/'
               f'{m["snr_e"]:.0f}x</text>')
    svg.append(f'<text x="{x0}" y="{y0+PH+40}" fill="{MUT}" font-size="12" '
               f'font-family="monospace">ms (bands: purple=DNg95 volley, '
               f'orange=DNg79 volley)</text>')

svg.append(f'<rect x="{MX}" y="{TOT_H-42}" width="14" height="4" '
           f'fill="{PUR}"/><text x="{MX+22}" y="{TOT_H-36}" fill="{FG}" '
           f'font-size="13" font-family="monospace">Ti/Tr flexor pool '
           f'(tau 255 ms)</text>')
svg.append(f'<rect x="{MX+250}" y="{TOT_H-42}" width="14" height="4" '
           f'fill="{ORN}"/><text x="{MX+272}" y="{TOT_H-36}" fill="{FG}" '
           f'font-size="13" font-family="monospace">Ti/Tr extensor pool '
           f'(tau 51 ms)</text>')
svg.append("</svg>")
open("l28/grooming.svg", "w").write("\n".join(svg))
subprocess.run(["rsvg-convert", "-w", "1800", "l28/grooming.svg",
                "-o", "l28/grooming.png"], check=True)
print("wrote l28/grooming.svg + grooming.png")

for f in ["1", "2", "5"]:
    for mode in ["alt", "sim"]:
        ps = d["arms"][f"{mode}{f}"]["per_seed"]
        print(f"{mode}{f}: rel_phase/seed "
              f"{[round(x['rel_phase_deg']) for x in ps]} dist180 "
              f"{[round(x['dist_from_antiphase_deg']) for x in ps]} "
              f"powfrac_f {[round(x['powfrac_f'], 2) for x in ps]} "
              f"powfrac_e {[round(x['powfrac_e'], 2) for x in ps]}")
print("SNR gate: soloA flex", round(d["arms"]["soloA"]["mean"]["snr_f"]),
      "x | soloB ext", round(d["arms"]["soloB"]["mean"]["snr_e"]), "x")
print("static:", json.dumps(d["static"]))
