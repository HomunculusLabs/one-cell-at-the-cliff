"""L43 figure: (A) dose grid late ratios + during-release S, (B) deepest-dose
timeline d30a12 vs fixed-entx vs ent (mm + rolling S). Hand-built SVG (house
style: no matplotlib on this box), rsvg-convert -> png."""
import json
import numpy as np

d = json.load(open("l43/results_l43.json"))
z = np.load("l43/traces.npz")
DOSE = ["d10a4","d10a8","d10a12","d20a4","d20a8","d20a12","d30a4","d30a8","d30a12"]
SEEDS = ["11","22","33"]
W, H = 1440, 800
BG, FG, GRID = "#1b1d24", "#e8e6e3", "#33363f"

def esc(s): return s.replace("&","&amp;").replace("<","&lt;")
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="DejaVu Sans, sans-serif">']
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'<text x="40" y="46" fill="{FG}" font-size="26" font-weight="bold">L43 stop-dose-resurrection: NO kill dose; structure inverts, entrainment protects</text>')
svg.append(f'<text x="40" y="72" fill="#9aa0ae" font-size="15">DNg88 release on the entrained cord (l42 substrate, anchors bit-identical). late ratio = rhythm2 peak/median, last 5 s of stop; S during = rolling antagonist-S median in-window</text>')

# ---- Panel A: dose grid ----
x0, y0, cw, chh = 60, 120, 130, 96
amps = [4, 8, 12]
svg.append(f'<text x="{x0}" y="{y0-18}" fill="{FG}" font-size="18" font-weight="bold">A. dose grid (rows: duration; cols: release amp)</text>')
for j, a in enumerate(amps):
    svg.append(f'<text x="{x0+j*cw+cw//2}" y="{y0-2}" fill="#9aa0ae" font-size="14" text-anchor="middle">-{a}</text>')
for i, du in enumerate([10,20,30]):
    yy = y0 + i*chh
    svg.append(f'<text x="{x0-12}" y="{yy+chh//2+5}" fill="#9aa0ae" font-size="14" text-anchor="end">{du}s</text>')
    for j, a in enumerate(amps):
        arm = f"d{du}a{a}"
        xx = x0 + j*cw
        lr = [d["dose"][arm][s]["late_ratio"] for s in SEEDS]
        sd = [d["post"][arm][s]["S_med_during"] for s in SEEDS]
        med = float(np.median(lr))
        t = 1 - min(np.log10(max(med,1))/np.log10(2000), 1)   # 0 dead..1 alive
        r,g2,b = int(40+215*t), int(60+140*t), int(70+60*t)
        svg.append(f'<rect x="{xx+4}" y="{yy+4}" width="{cw-8}" height="{chh-8}" rx="8" fill="rgb({r},{g2},{b})" fill-opacity="0.28" stroke="{GRID}"/>')
        killed = sum(v < 5 for v in lr)
        if killed: svg.append(f'<rect x="{xx+4}" y="{yy+4}" width="{cw-8}" height="{chh-8}" rx="8" fill="none" stroke="#e05555" stroke-width="3"/>')
        svg.append(f'<text x="{xx+cw//2}" y="{yy+26}" fill="{FG}" font-size="13" text-anchor="middle">late {lr[0]:.0f}/{lr[1]:.0f}/{lr[2]:.0f}</text>')
        svg.append(f'<text x="{xx+cw//2}" y="{yy+46}" fill="#c8cdd8" font-size="13" text-anchor="middle">S {sd[0]:+.2f}/{sd[1]:+.2f}/{sd[2]:+.2f}</text>')
        x88m = d["dose"][arm]["11"]["min_x88"]
        svg.append(f'<text x="{xx+cw//2}" y="{yy+66}" fill="#8b93a3" font-size="12" text-anchor="middle">x88min {x88m:.2f}</text>')
        kl = [d["dose"][arm][s]["kill_latency"] for s in SEEDS]
        kls = "/".join("—" if k is None else str(k) for k in kl)
        svg.append(f'<text x="{xx+cw//2}" y="{yy+84}" fill="#8b93a3" font-size="12" text-anchor="middle">kill {kls}</text>')

# ent / entx reference cards (below panel A, stacked)
cards = (("ent", "ent: no release, drive stays on 0.7 Hz (reference)", "post"),
         ("entx", "entx: DNg88 -12 x 30 s + drive ON through the release", "dur"))
for k, (nm, label, smode) in enumerate(cards):
    yy = 452 + k * 74
    svg.append(f'<rect x="{x0}" y="{yy}" width="620" height="64" rx="8" fill="#262a33" stroke="{GRID}"/>')
    svg.append(f'<text x="{x0+14}" y="{yy+24}" fill="{FG}" font-size="14">{label}</text>')
    lr = [d["dose"][nm][s]["late_ratio"] for s in SEEDS]
    sd = [d["post"][nm][s]["S_med_during" if smode == "dur" else "S_med_after"] for s in SEEDS]
    rl = [d["post"][nm][s]["resurrect_latency"] for s in SEEDS]
    rls = "/".join("--" if v is None else f"{v/100:.1f}s" for v in rl)
    sl = "/".join("--" if v != v else f"{v:+.2f}" for v in sd)
    tag = "S during" if smode == "dur" else "S post-win"
    svg.append(f'<text x="{x0+14}" y="{yy+48}" fill="#c8cdd8" font-size="13">late {lr[0]:.0f}/{lr[1]:.0f}/{lr[2]:.0f}   {tag} {sl}   repair {rls}</text>')

# ---- Panel B: deepest-dose timeline ----
bx, by, bw, bh = 700, 140, 660, 560
t_lo, t_hi = 30, 80   # s
def X(t): return bx + (t - t_lo)/(t_hi - t_lo)*bw
svg.append(f'<text x="{bx}" y="{by-18}" fill="{FG}" font-size="18" font-weight="bold">B. deepest dose (30s, -12): drive-through protects</text>')
# stop shading 40-70 s
svg.append(f'<rect x="{X(40)}" y="{by}" width="{X(70)-X(40)}" height="{bh}" fill="#e05555" fill-opacity="0.10"/>')
svg.append(f'<text x="{X(55)}" y="{by+bh+18}" fill="#c07a7a" font-size="13" text-anchor="middle">release window 40-70 s</text>')
svg.append(f'<line x1="{X(40)}" y1="{by}" x2="{X(40)}" y2="{by+bh}" stroke="{GRID}" stroke-dasharray="4 4"/>')
svg.append(f'<line x1="{X(70)}" y1="{by}" x2="{X(70)}" y2="{by+bh}" stroke="{GRID}" stroke-dasharray="4 4"/>')
# top: mm traces (motor mean), seed 22
mmy = by + 40; mmh = 180
mm1 = z["mm_d30a12_22"]; mm2 = z["mm_entx_22"]; mm3 = z["mm_ent_22"]
lo = float(min(mm1.min(), mm2.min(), mm3.min())); hi = float(max(mm1.max(), mm2.max(), mm3.max()))
def Ym(v): return mmy + mmh - (v-lo)/(hi-lo)*mmh
i0, i1 = int(t_lo/0.01), int(t_hi/0.01)
for arr, col, dash, lab in ((mm3,"#7f8896","1 4","ent (no release)"),
                            (mm1,"#e0a244","none","d30a12 (drive off)"),
                            (mm2,"#5fb878","7 4","entx (drive on)")):
    pts = " ".join(f"{X(t_lo+(i-i0)*0.01):.1f},{Ym(arr[i]):.1f}" for i in range(i0, i1, 8))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.6" stroke-dasharray="{dash}"/>')
svg.append(f'<text x="{bx+10}" y="{mmy-10}" fill="{FG}" font-size="14">motor mean (seed 22)</text>')
lx = bx + bw - 350
for col, dash, lab in (("#7f8896","1 4","ent"),("#e0a244","none","drive-off"),("#5fb878","7 4","drive-on")):
    svg.append(f'<line x1="{lx}" y1="{mmy-16}" x2="{lx+26}" y2="{mmy-16}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{lx+32}" y="{mmy-11}" fill="{FG}" font-size="13">{lab}</text>'); lx += 118
# bottom: rolling S
sy = by + 330; sh = 180
s1 = z["SR_d30a12_22"]; s2 = z["SR_entx_22"]; s3 = z["SR_ent_22"]
slo, shi = -1.0, 1.0
def Ys(v): return sy + sh - (v-slo)/(shi-slo)*sh
for gv in (-1,-0.5,0,0.5,1):
    svg.append(f'<line x1="{bx}" y1="{Ys(gv):.1f}" x2="{bx+bw}" y2="{Ys(gv):.1f}" stroke="{GRID}" stroke-width="{2 if gv==0 else 0.6}"/>')
for gv in (-0.5,0,0.5,1):
    svg.append(f'<text x="{bx-34}" y="{Ys(gv)+4:.1f}" fill="#8b93a3" font-size="12" text-anchor="end">{gv:+.1f}</text>')
svg.append(f'<line x1="{bx}" y1="{Ys(0.25)}" x2="{bx+bw}" y2="{Ys(0.25)}" stroke="#5fb878" stroke-dasharray="2 6" stroke-width="1.2"/>')
svg.append(f'<text x="{bx-8}" y="{Ys(0.25)+4:.1f}" fill="#5fb878" font-size="11" text-anchor="end">.25</text>')
ts = np.arange(499, 11000, 10)
for arr, col, dash in ((s3,"#7f8896","1 4"),(s1,"#e0a244","none"),(s2,"#5fb878","7 4")):
    m = (ts >= i0) & (ts < i1)
    pts = " ".join(f"{X(t_lo+(t-i0)*0.01):.1f},{Ys(min(max(arr[t],slo),shi)):.1f}" for t in ts[m])
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.8" stroke-dasharray="{dash}"/>')
svg.append(f'<text x="{bx+10}" y="{sy-10}" fill="{FG}" font-size="14">rolling antagonist S (500-step window, seed 22)</text>')
svg.append(f'<text x="{X(30)}" y="{by+bh+40}" fill="#8b93a3" font-size="13">30 s</text>')
svg.append(f'<text x="{X(80)-20}" y="{by+bh+40}" fill="#8b93a3" font-size="13">80 s</text>')
svg.append(f'<text x="{bx}" y="{by+bh+58}" fill="#9aa0ae" font-size="13">Verdict: no cell parks (late ratio &#8805; 63 everywhere, even 30 s at &#8722;12 fully un-pinned);</text>')
svg.append(f'<text x="{bx}" y="{by+bh+78}" fill="#9aa0ae" font-size="13">deep doses INVERT structure (S &#8594; &#8722;0.74); drive-through attenuates; repair &#8804; 2.8 s after drive resumes</text>')
svg.append("</svg>")
open("l43/dose.svg","w").write("\n".join(svg))
print("wrote l43/dose.svg")
