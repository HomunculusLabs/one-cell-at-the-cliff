"""L35 figure (tick 52 rewrite): reads the CORRECTED verdict_l35.json (the
in-run C3_detail carried the name-swap). Negative-verdict layout:
A PRC (mean over seeds) + sham band + absorbed-channel zero line;
B paired-noise trace zoom at the strongest bin;
C persistence (early vs late) + duration arms.
Hand-built SVG (no matplotlib on this box) -> rsvg-convert -> PNG."""
import json
import subprocess

import numpy as np

V = json.load(open("l35/verdict_l35.json"))
r = json.load(open("l35/results_l35.json"))
tr = np.load("l35/traces.npz")
SEEDS = [11, 22, 33]
PRC = V["prc"]
SHAM = V["sham"]["max_mean"]

W, H = 1470, 600
MXA, MYA, PW, PH = 62, 84, 400, 330
MXB = MXA + PW + 66
MXC = MXB + PW + 66

CURVES = {
    "dng95_A0.05": ("#5b6b7a", "10,5", "DNg95 V=.05 (8/24 absorbed)"),
    "dng95_A0.15": ("#d1495b", "none", "DNg95 V=.15 (0/24 absorbed)"),
    "dng100pulse_A0.15": ("#2a9d8f", "2,5", "DNg100 pulse (48/48 absorbed)"),
}

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
     f'font-family="DejaVu Sans, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#14171c"/>',
     f'<text x="{W//2}" y="30" fill="#e8e6e3" font-size="17" text-anchor="middle" font-weight="bold">'
     f'L35 — brief DN volleys do NOT reliably re-time the self-rhythmic cord (PRC &lt; 3x sham; deflection is transient)</text>',
     f'<text x="{W//2}" y="52" fill="#9aa4b2" font-size="13" text-anchor="middle">'
     f'L32 substrate, paired-noise heterodyne PRC, 3 seeds x 8 phase bins; volley lands only when it lifts DNg95 over the relu floor</text>']

# ---------- panel A: PRC ----------
allv = [abs(m) for k in PRC for p, m in PRC[k]["curve"]] + [3 * SHAM]
ymax = max(20.0, np.ceil(max(allv) / 10.0) * 10.0 + 5)
sx_a = lambda v: MXA + v / 360.0 * PW
sy_a = lambda v: H - MYA - (v + ymax) / (2 * ymax) * PH
s.append(f'<rect x="{MXA}" y="{H-MYA-PH}" width="{PW}" height="{PH}" fill="#1b1f26" stroke="#3a414d"/>')
for gv in range(0, 361, 45):
    s.append(f'<line x1="{sx_a(gv):.1f}" y1="{H-MYA}" x2="{sx_a(gv):.1f}" y2="{H-MYA-PH}" stroke="#282e38"/>')
    if gv % 90 == 0:
        s.append(f'<text x="{sx_a(gv):.1f}" y="{H-MYA+18}" fill="#9aa4b2" font-size="12" text-anchor="middle">{gv}</text>')
for gv in np.arange(-ymax, ymax + 1, ymax / 2):
    s.append(f'<line x1="{MXA}" y1="{sy_a(gv):.1f}" x2="{MXA+PW}" y2="{sy_a(gv):.1f}" stroke="#282e38"/>')
    s.append(f'<text x="{MXA-8}" y="{sy_a(gv)+4:.1f}" fill="#9aa4b2" font-size="12" text-anchor="end">{gv:+.0f}</text>')
s.append(f'<line x1="{MXA}" y1="{sy_a(0):.1f}" x2="{MXA+PW}" y2="{sy_a(0):.1f}" stroke="#8b949e" stroke-width="1.2"/>')
band = max(SHAM, 3.0)
s.append(f'<rect x="{MXA}" y="{sy_a(band):.1f}" width="{PW}" height="{sy_a(-band)-sy_a(band):.1f}" fill="#3a414d" opacity="0.45"/>')
s.append(f'<text x="{MXA+PW-6}" y="{sy_a(-band)+16:.1f}" fill="#9aa4b2" font-size="11" text-anchor="end">sham band (random DN pair, |mean| &lt;= {band:.1f} deg)</text>')
s.append(f'<line x1="{MXA}" y1="{sy_a(3*SHAM):.1f}" x2="{MXA+PW}" y2="{sy_a(3*SHAM):.1f}" stroke="#e8a33d" stroke-width="1.4" stroke-dasharray="3,6"/>')
s.append(f'<text x="{MXA+6}" y="{sy_a(3*SHAM)-5:.1f}" fill="#e8a33d" font-size="11">C3 gate: 3x sham = {3*SHAM:.1f} deg</text>')
for key, (col, dash, lab) in CURVES.items():
    pts = PRC[key]["curve"]
    dd = f' stroke-dasharray="{dash}"' if dash != "none" else ""
    poly = " ".join(f"{sx_a(p):.1f},{sy_a(np.clip(m, -ymax, ymax)):.1f}" for p, m in pts)
    s.append(f'<polyline points="{poly}" fill="none" stroke="{col}" stroke-width="2.4"{dd}/>')
    for p, m in pts:
        s.append(f'<circle cx="{sx_a(p):.1f}" cy="{sy_a(np.clip(m, -ymax, ymax)):.1f}" r="3.2" fill="{col}"/>')
s.append(f'<text x="{MXA+PW//2}" y="{H-MYA+38}" fill="#c9d1d9" font-size="13" text-anchor="middle">volley phase in gait cycle (deg; heterodyne angle of motor mean)</text>')
s.append(f'<text x="20" y="{H-MYA-PH//2}" fill="#c9d1d9" font-size="13" transform="rotate(-90 20 {H-MYA-PH//2})" text-anchor="middle">phase shift dphi (deg, + = delay)</text>')
s.append(f'<text x="{MXA}" y="{H-MYA-PH-10}" fill="#e8e6e3" font-size="14" font-weight="bold">A — PRC (3-seed mean): max 18.9 deg, below gate</text>')

# ---------- panel B: trace zoom at strongest bin ----------
key = "dng95_A0.15"
binp = PRC[key]["argmax_bin"]
pers = PRC[key]["per_seed_at_argmax"]
seed = SEEDS[int(np.argmax([abs(x) for x in pers]))]
arm = next(a for a in r["arms"] if a["tag"] == "dng95" and a["seed"] == seed
           and abs(a["phi"] - binp) < 1e-6 and a["vsteps"] == 25
           and abs(a["vamp"] - 0.15) < 1e-9)
k0, vsteps = arm["k0"], arm["vsteps"]
c = tr[f"ctrl_{seed}_mm"]
p = tr[f"dng95_s{seed}_phi{int(binp)}_mm"]
lo, hi = k0 - 180, k0 + 420
tt = (np.arange(lo, hi) - k0) * 0.01
sxn = lambda v: MXB + (v - tt[0]) / (tt[-1] - tt[0]) * PW
syn = lambda v, a, b: H - MYA - (v - a) / (b - a) * PH
lo_c, hi_c = min(c[lo:hi].min(), p[lo:hi].min()), max(c[lo:hi].max(), p[lo:hi].max())
pad = (hi_c - lo_c) * 0.12 + 1e-9
s.append(f'<rect x="{MXB}" y="{H-MYA-PH}" width="{PW}" height="{PH}" fill="#1b1f26" stroke="#3a414d"/>')
s.append(f'<rect x="{sxn(0):.1f}" y="{H-MYA-PH}" width="{sxn(vsteps*0.01)-sxn(0):.1f}" height="{PH}" fill="#d1495b" opacity="0.18"/>')
s.append(f'<text x="{sxn(vsteps*0.01)+4:.1f}" y="{H-MYA-PH+14}" fill="#d1495b" font-size="11">volley</text>')
pc = " ".join(f"{sxn(t):.1f},{syn(c[k], lo_c-pad, hi_c+pad):.1f}" for k, t in zip(range(lo, hi), tt))
pp = " ".join(f"{sxn(t):.1f},{syn(p[k], lo_c-pad, hi_c+pad):.1f}" for k, t in zip(range(lo, hi), tt))
s.append(f'<polyline points="{pc}" fill="none" stroke="#8b949e" stroke-width="1.6"/>')
s.append(f'<polyline points="{pp}" fill="none" stroke="#d1495b" stroke-width="1.8" stroke-dasharray="7,4"/>')
s.append(f'<text x="{MXB+PW-6}" y="{H-MYA-PH+30}" fill="#8b949e" font-size="11" text-anchor="end">control</text>')
s.append(f'<text x="{MXB+PW-6}" y="{H-MYA-PH+44}" fill="#d1495b" font-size="11" text-anchor="end">volley @ {binp:.0f} deg (seed {seed}, dphi {pers[SEEDS.index(seed)]:+.0f} deg)</text>')
s.append(f'<text x="{MXB}" y="{H-MYA-PH-10}" fill="#e8e6e3" font-size="14" font-weight="bold">B — strongest bin, paired noise (motor mean)</text>')
s.append(f'<text x="{MXB+PW//2}" y="{H-MYA+38}" fill="#c9d1d9" font-size="13" text-anchor="middle">time from volley onset (s) — rhythm survives, phase relaxes back</text>')

# ---------- panel C: persistence + duration ----------
c4 = V["c4"]["dng95"]
early, late = c4["dphi_early"], c4["dphi_late"]
dur = V["c4"]["dur"]
durvals = [v for ph in dur.values() for kk in ("dur100", "dur25") for v in ph[kk]]
ymc = max(20.0, np.ceil(max([abs(v) for v in early + late]
                            + durvals) / 10.0) * 10.0 + 5)
sy_c = lambda v: H - MYA - (v + ymc) / (2 * ymc) * PH
s.append(f'<rect x="{MXC}" y="{H-MYA-PH}" width="{PW}" height="{PH}" fill="#1b1f26" stroke="#3a414d"/>')
s.append(f'<line x1="{MXC}" y1="{sy_c(0):.1f}" x2="{MXC+PW}" y2="{sy_c(0):.1f}" stroke="#8b949e" stroke-width="1.2"/>')
for gv in (-ymc, -ymc / 2, ymc / 2, ymc):
    s.append(f'<text x="{MXC-8}" y="{sy_c(gv)+4:.1f}" fill="#9aa4b2" font-size="12" text-anchor="end">{gv:+.0f}</text>')
gw, gp = 22, 12
x0 = MXC + 26
for i, sd in enumerate(SEEDS):
    for j, (vals, lab, col) in enumerate(((early, "early (1st cycle)", "#e8a33d"),
                                          (late, "late (next 15 s)", "#2a9d8f"))):
        x = x0 + i * (2 * gw + 2 * gp) + j * gw
        hgt = sy_c(0) - sy_c(np.clip(vals[i], -ymc, ymc))
        y = min(sy_c(0), sy_c(np.clip(vals[i], -ymc, ymc)))
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{gw-3}" height="{max(abs(hgt),1):.1f}" fill="{col}"/>')
    s.append(f'<text x="{x0 + i*(2*gw+2*gp) + gw:.1f}" y="{H-MYA+18}" fill="#9aa4b2" font-size="12" text-anchor="middle">s{sd}</text>')
s.append(f'<text x="{MXC+10}" y="{H-MYA-PH+42}" fill="#c9d1d9" font-size="11">deflection is transient:</text>')
s.append(f'<text x="{MXC+10}" y="{H-MYA-PH+58}" fill="#c9d1d9" font-size="11">no persistent reset</text>')
# duration bars
xd = MXC + PW / 2 + 30
s.append(f'<text x="{xd}" y="{H-MYA-PH+22}" fill="#c9d1d9" font-size="12">volley duration 250 ms vs 1 s (seed mean)</text>')
for i, ph in enumerate(("0", "180")):
    v25 = float(np.mean(dur[ph]["dur25"]))
    v100 = float(np.mean(dur[ph]["dur100"]))
    for j, (v, lab2, col) in enumerate(((v25, "250 ms", "#5b6b7a"), (v100, "1000 ms", "#d1495b"))):
        wbar = 34
        x = xd + 10 + j * (wbar + 8)
        hgt = sy_c(0) - sy_c(np.clip(v, -ymc, ymc))
        y = min(sy_c(0), sy_c(np.clip(v, -ymc, ymc)))
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{wbar}" height="{max(abs(hgt),1):.1f}" fill="{col}"/>')
        s.append(f'<text x="{x+wbar/2:.1f}" y="{y-4:.1f}" fill="#9aa4b2" font-size="10" text-anchor="middle">{v:+.0f}</text>')
    s.append(f'<text x="{xd+10}" y="{H-MYA-PH+46+i*18}" fill="#9aa4b2" font-size="11">phi {ph}</text>')
s.append(f'<text x="{MXC}" y="{H-MYA-PH-10}" fill="#e8e6e3" font-size="14" font-weight="bold">C — persistence at the strongest bin (A=.15)</text>')
s.append(f'<text x="{MXC+PW//2}" y="{H-MYA+38}" fill="#c9d1d9" font-size="13" text-anchor="middle">early vs late window shift (deg)</text>')

# legend
lx = MXA
for key, (col, dash, lab) in CURVES.items():
    dd = f' stroke-dasharray="{dash}"' if dash != "none" else ""
    s.append(f'<line x1="{lx}" y1="{H-16}" x2="{lx+26}" y2="{H-16}" stroke="{col}" stroke-width="2.4"{dd}/>')
    s.append(f'<text x="{lx+32}" y="{H-12}" fill="#c9d1d9" font-size="12">{lab}</text>')
    lx += 40 + 8.2 * len(lab)
s.append('</svg>')
open("l35/prc.svg", "w").write("\n".join(s))
subprocess.run(["rsvg-convert", "-w", "1470", "l35/prc.svg", "-o", "l35/prc.png"], check=True)
print("wrote l35/prc.png | ymax", round(ymax, 1), "| panelB bin", binp, "seed", seed,
      "| gate", round(3 * SHAM, 1))
