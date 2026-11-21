"""L44 figure: (A) protection curve S_med_during vs entrain-history H,
(B) frequency fingerprint f_late through the stop, (C) CPG-core recruitment.
Hand-built SVG (house style), rsvg-convert -> png."""
import json
import numpy as np

d = json.load(open("l44/results_l44.json"))
SEEDS = ["11", "22", "33"]
ARMS = ["h0", "h5", "h10", "h20", "h40"]
HIST = [0, 5, 10, 20, 40]
W, H = 1500, 560
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_STYLE = {"11": ("#7fd4ff", "none"), "22": ("#ffb37f", "6 4"),
              "33": ("#b39dff", "2 3")}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="44" fill="{FG}" font-size="25" font-weight="bold">'
       f'L44 entrain-history protection: basin entry at 10-20 s; short pulses are a lottery</text>',
       f'<text x="40" y="70" fill="{MUT}" font-size="14">'
       f'0.7 Hz mech history for H s immediately before a fixed stop (DNg88 -8, 20 s); free-settled cord, one shared noise stream; seeds 11/22/33</text>']

PANES = [(60, 100, 440, 400), (560, 100, 440, 400), (1060, 100, 400, 400)]
TITLES = ["A. antagonist structure through the stop (S, rolling 5 s median)",
          "B. rhythm frequency late in stop (f_late)",
          "C. named CPG core pool (mean X)"]


def px(pane, x):  # H: 0..40 -> pane x
    return pane[0] + 40 + (pane[2] - 80) * (np.log10(x + 1) / np.log10(41))


def frame(pane, title, ylab, ymin, ymax, yticks, fmt="{:.2f}"):
    x0, y0, cw, chh = pane
    x1, y1 = x0 + cw, y0 + chh
    svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" font-weight="bold">{title}</text>')
    svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
               f'fill="none" stroke="{GRID}"/>')
    svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" font-size="13" '
               f'transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" text-anchor="middle">{ylab}</text>')
    for tv in yticks:
        yy = y1 - 40 - (chh - 40) * (tv - ymin) / (ymax - ymin)
        svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x1-20}" y2="{yy:.1f}" '
                   f'stroke="{GRID}" stroke-dasharray="2 4" stroke-width="1"/>')
        svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="12" '
                   f'text-anchor="end">{fmt.format(tv)}</text>')
    for h in HIST:
        xx = px(pane, h)
        svg.append(f'<text x="{xx:.1f}" y="{y1-18}" fill="{MUT}" font-size="12" text-anchor="middle">{h}</text>')
    svg.append(f'<text x="{x0+(cw-20)//2+20}" y="{y1-2}" fill="{MUT}" font-size="13" '
               f'text-anchor="middle">entrain history H (s)</text>')


def py(pane, v, ymin, ymax):
    y0, chh = pane[1], pane[3]
    return y0 + (chh - 40) * (1 - (v - ymin) / (ymax - ymin))


# ---- Panel A: S_med_durve ----
p = PANES[0]
frame(p, TITLES[0], "S(Tr) during stop", -0.8, 0.8, [-0.5, 0, 0.25, 0.5], "{:+.2f}")
yy = py(p, 0.25, -0.8, 0.8)
svg.append(f'<rect x="{p[0]+40}" y="{p[1]}" width="{p[2]-60}" height="{yy-p[1]:.1f}" '
           f'fill="#2f6e4f" fill-opacity="0.18"/>')
svg.append(f'<text x="{p[0]+p[2]-24}" y="{yy-6:.1f}" fill="#7fc8a0" font-size="12" text-anchor="end">protected (S&#8805;.25)</text>')
yy = py(p, 0, -0.8, 0.8)
svg.append(f'<line x1="{p[0]+40}" y1="{yy:.1f}" x2="{p[0]+p[2]-20}" y2="{yy:.1f}" stroke="#e05555" stroke-width="1"/>')
yy = py(p, 0.485, -0.8, 0.8)
svg.append(f'<line x1="{p[0]+40}" y1="{yy:.1f}" x2="{p[0]+p[2]-20}" y2="{yy:.1f}" stroke="#7fd4ff" stroke-dasharray="5 4" stroke-width="2"/>')
svg.append(f'<text x="{p[0]+46}" y="{yy-6:.1f}" fill="#7fd4ff" font-size="12">free-run band .45-.52 (L40 ctl)</text>')
med = [float(np.median([d["table"][a][s]["S_med_during"] for s in SEEDS])) for a in ARMS]
pts = " ".join(f"{px(p,h):.1f},{py(p,v,-0.8,0.8):.1f}" for h, v in zip(HIST, med))
svg.append(f'<polyline points="{pts}" fill="none" stroke="{FG}" stroke-width="2.5"/>')
for s in SEEDS:
    col, dash = SEED_STYLE[s]
    for h, a in zip(HIST, ARMS):
        v = d["table"][a][s]["S_med_during"]
        xx, yyp = px(p, h), py(p, v, -0.8, 0.8)
        svg.append(f'<circle cx="{xx:.1f}" cy="{yyp:.1f}" r="6" fill="none" '
                   f'stroke="{col}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
svg.append(f'<text x="{p[0]+46}" y="{p[1]+p[3]-52}" fill="{MUT}" font-size="12">'
           f'median line; circles per seed (dashes distinguish seeds); '
           f'h5/h10 inverted seeds sit below 0</text>')

# ---- Panel B: freq fingerprint ----
p = PANES[1]
frame(p, TITLES[1], "f (Hz)", 0.2, 1.8, [0.7, 1.0, 1.4], "{:.1f}")
for fv, col, lab in ((0.7, "#7fc8a0", "entrain 0.7 Hz"), (1.4, "#e0b255", "intrinsic attractor 1.4 Hz")):
    yy = py(p, fv, 0.2, 1.8)
    svg.append(f'<line x1="{p[0]+40}" y1="{yy:.1f}" x2="{p[0]+p[2]-20}" y2="{yy:.1f}" '
               f'stroke="{col}" stroke-dasharray="5 4" stroke-width="2"/>')
    svg.append(f'<text x="{p[0]+46}" y="{yy-6:.1f}" fill="{col}" font-size="12">{lab}</text>')
for s in SEEDS:
    col, dash = SEED_STYLE[s]
    pts = " ".join(f"{px(p,h):.1f},{py(p,d['table'][a][s]['f_late'],0.2,1.8):.1f}"
                   for h, a in zip(HIST, ARMS))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" '
               f'stroke-dasharray="{dash}" stroke-opacity="0.9"/>')
svg.append(f'<text x="{p[0]+46}" y="{p[1]+p[3]-52}" fill="{MUT}" font-size="12">'
           f'history &#8805;20 s carries the 0.6-0.7 Hz memory THROUGH the stop (3/3 at 40 s)</text>')

# ---- Panel C: core recruitment ----
p = PANES[2]
frame(p, TITLES[2], "mean X (core pool)", 0.10, 0.30, [0.15, 0.20, 0.25], "{:.2f}")
for key, col, dash, lab in (("core_late_hist", "#7fd4ff", "none", "late history (pre-stop)"),
                            ("core_late_stop", "#e08b55", "6 4", "late stop")):
    med = [float(np.median([d["table"][a][s][key] for s in SEEDS])) for a in ARMS]
    pts = " ".join(f"{px(p,h):.1f},{py(p,v,0.10,0.30):.1f}" for h, v in zip(HIST, med))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5" '
               f'stroke-dasharray="{dash}"/>')
for i, (key, col, dash, lab) in enumerate((
        ("core_late_hist", "#7fd4ff", "none", "late history (pre-stop)"),
        ("core_late_stop", "#e08b55", "6 4", "late stop"))):
    yleg = p[1] + 26 + i * 20
    svg.append(f'<line x1="{p[0]+60}" y1="{yleg-4}" x2="{p[0]+92}" y2="{yleg-4}" '
               f'stroke="{col}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{p[0]+98}" y="{yleg}" fill="{col}" font-size="12">{lab}</text>')
svg.append(f'<text x="{p[0]+46}" y="{p[1]+p[3]-52}" fill="{MUT}" font-size="12">'
           f'5 named CPG types x 6 cells (Pugliese core): recruited by entrainment,</text>')
svg.append(f'<text x="{p[0]+46}" y="{p[1]+p[3]-34}" fill="{MUT}" font-size="12">'
           f'never silenced by the stop (core ratio &#8805;5 in 15/15 protected pairs)</text>')

svg.append(f'<text x="40" y="{H-18}" fill="{MUT}" font-size="12">'
           f'L44 &#183; l44_history.py exit 0 (CPU 82 s) &#183; C1 pass (dm lands, prefix bit-identical, x88 un-pins) &#183; '
           f'C0 ratio-anchor failed (disclosed): L40 kill was structural, see PREREG ADDENDUM 1</text>')
svg.append("</svg>")
open("l44/history.svg", "w").write("\n".join(svg))
print("wrote l44/history.svg")
