"""L46 figure: (A) h40 S(t) — protected through stop, collapses after;
(B) h0 S(t) — killed during, rebounds immediately; (C) per-side S medians
(the SR inversion the pooled S hides). Hand-built SVG -> rsvg-convert."""
import json
import numpy as np

SEEDS = [11, 22, 33]
ARMS = ["h0", "h20", "h40"]
tr = np.load("l46/traces_l46.npz")
raw = np.load("l46/raw_l46.npz")
W, H = 1560, 560
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_STYLE = {11: ("#7fd4ff", "none"), 22: ("#ffb37f", "6 4"),
              33: ("#b39dff", "2 3")}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L46 post-stop recovery: the most protected arm (h40) never re-organizes</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">'
       f'stop = DNg88 &#8722;8, 20 s; 0.7 Hz entrain history before it; 120-s post window; S(Tr) rolling 5 s; seeds 11/22/33</text>']

T0S, T1S = 30.0, 180.0          # x window (s)
STOPS, STOPE = 40.0, 60.0       # stop band


def sx(pane, t):
    return pane[0] + 40 + (pane[2] - 60) * (t - T0S) / (T1S - T0S)


def sy(pane, v, ymin=-1.0, ymax=1.0):
    return pane[1] + (pane[3] - 40) * (1 - (v - ymin) / (ymax - ymin))


def frame(pane, title):
    x0, y0, cw, chh = pane
    svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
               f'font-weight="bold">{title}</text>')
    svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
               f'fill="none" stroke="{GRID}"/>')
    for tv, lab in ((-0.5, "-.5"), (-0.25, ""), (0.0, "0"), (0.25, ".25 gate"),
                    (0.5, ".5"), (0.75, "")):
        yy = sy(pane, tv)
        svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" y2="{yy:.1f}" '
                   f'stroke="{GRID}" stroke-dasharray="2 4" stroke-width="1"/>')
        if lab:
            svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="12" '
                       f'text-anchor="end">{lab}</text>')
    for t in (60, 90, 120, 150, 180):
        xx = sx(pane, t)
        svg.append(f'<text x="{xx:.1f}" y="{y0+chh-18}" fill="{MUT}" font-size="12" '
                   f'text-anchor="middle">{t}</text>')
    svg.append(f'<text x="{x0+(cw-20)//2+20}" y="{y0+chh-2}" fill="{MUT}" '
               f'font-size="13" text-anchor="middle">time (s)</text>')
    svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" font-size="13" '
               f'transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" '
               f'text-anchor="middle">S(Tr)</text>')
    xa, xb = sx(pane, STOPS), sx(pane, STOPE)
    svg.append(f'<rect x="{xa:.1f}" y="{y0}" width="{xb-xa:.1f}" height="{chh-40}" '
               f'fill="#e05555" fill-opacity="0.13"/>')
    svg.append(f'<text x="{(xa+xb)/2:.1f}" y="{y0+16}" fill="#e08080" font-size="12" '
               f'text-anchor="middle">stop</text>')


def strip(pane):
    ts = np.arange(499, 18000, 50)
    t = ts * 0.01
    return ts, t


PANES = [(60, 118, 470, 392), (570, 118, 470, 392), (1080, 118, 420, 392)]
for pane, arm, ttl in ((PANES[0], "h40", "A. H=40: protected through the stop &#8212; no post recovery"),
                       (PANES[1], "h0", "B. H=0: killed during &#8212; rebounds in seconds")):
    frame(pane, ttl)
    ts, t = strip(pane)
    for s in SEEDS:
        S = tr[f"SR_{arm}_{s}"][ts]
        col, dash = SEED_STYLE[s]
        pts = " ".join(f"{sx(pane,tt):.1f},{sy(pane,v):.1f}"
                       for tt, v in zip(t, S) if np.isfinite(v))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
                   f'stroke-width="2" stroke-dasharray="{dash}"/>')
svg.append(f'<text x="{PANES[0][0]+46}" y="{PANES[0][1]+PANES[0][3]-52}" '
           f'fill="{MUT}" font-size="12">entrain 0-40 s (out of frame)</text>')
svg.append(f'<text x="{PANES[1][0]+46}" y="{PANES[1][1]+PANES[1][3]-52}" '
           f'fill="{MUT}" font-size="12">free-run before stop</text>')


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


# ---- Panel C: per-side S medians, pre [3500,4000) vs late post [12000,18000)
p = PANES[2]
x0, y0, cw, chh = p
svg.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C. per-side S &#8212; the stop inverts S&#8202;R (h40)</text>')
svg.append(f'<rect x="{x0+40}" y="{y0}" width="{cw-60}" height="{chh-40}" '
           f'fill="none" stroke="{GRID}"/>')
for tv, lab in ((-0.5, "-.5"), (0.0, "0"), (0.5, ".5"), (0.25, ".25 gate")):
    yy = y0 + (chh - 40) * (1 - (tv + 0.6) / 1.2)
    svg.append(f'<line x1="{x0+40}" y1="{yy:.1f}" x2="{x0+cw-20}" y2="{yy:.1f}" '
               f'stroke="{GRID}" stroke-dasharray="2 4" stroke-width="1"/>')
    svg.append(f'<text x="{x0+36}" y="{yy+4:.1f}" fill="{MUT}" font-size="12" '
               f'text-anchor="end">{lab}</text>')
svg.append(f'<text x="{x0+8}" y="{y0+(chh-40)//2}" fill="{MUT}" font-size="13" '
           f'transform="rotate(-90 {x0+8} {y0+(chh-40)//2})" '
           f'text-anchor="middle">side S median</text>')
allts = np.arange(499, 18000, 10)


def side_med(arm, s, lo, hi, side):
    fL, eL, fR, eR = (raw[f"{q}_{arm}_{s}"] for q in ("fL", "eL", "fR", "eR"))
    f, e = (fL, eL) if side == "L" else (fR, eR)
    vals = [S_of(f[t - 499:t + 1], e[t - 499:t + 1])
            for t in allts if lo <= t < hi]
    return float(np.nanmedian(vals))


groups = [("h0", "H=0"), ("h20", "H=20"), ("h40", "H=40")]
bw, gap = 16, 8
gx = x0 + 70
for arm, lab in groups:
    svg.append(f'<text x="{gx+2*bw+gap}" y="{y0+chh-18}" fill="{MUT}" '
               f'font-size="13" text-anchor="middle">{lab}</text>')
    for j, (side, lo, hi, tag) in enumerate((("L", 3500, 4000, "pre"),
                                             ("R", 3500, 4000, "pre"),
                                             ("L", 12000, 18000, "late"),
                                             ("R", 12000, 18000, "late"))):
        vals = [side_med(arm, str(s), lo, hi, side) for s in SEEDS]
        medv = float(np.median(vals))
        xx = gx + j * (bw + gap)
        col = "#7fc8a0" if tag == "pre" else "#e0b070"
        yy = y0 + (chh - 40) * (1 - (medv + 0.6) / 1.2)
        yb = y0 + (chh - 40)
        svg.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bw}" height="{yb-yy:.1f}" '
                   f'fill="{col}" fill-opacity="0.85"/>')
        for s, v in zip(SEEDS, vals):
            yd = y0 + (chh - 40) * (1 - (v + 0.6) / 1.2)
            c, dsh = SEED_STYLE[s]
            svg.append(f'<circle cx="{xx+bw/2:.1f}" cy="{yd:.1f}" r="4" fill="none" '
                       f'stroke="{c}" stroke-width="1.8" stroke-dasharray="{dsh}"/>')
    gx += 4 * bw + 3 * gap + 26
svg.append(f'<rect x="{x0+40}" y="{y0+chh-8}" width="12" height="8" fill="#7fc8a0"/>')
svg.append(f'<text x="{x0+56}" y="{y0+chh-1}" fill="{MUT}" font-size="12">pre-stop end</text>')
svg.append(f'<rect x="{x0+150}" y="{y0+chh-8}" width="12" height="8" fill="#e0b070"/>')
svg.append(f'<text x="{x0+166}" y="{y0+chh-1}" fill="{MUT}" font-size="12">late post (60-120 s after)</text>')
svg.append(f'<text x="{x0+40}" y="{y0+16}" fill="#e08080" font-size="12">'
           f'pairs: S&#8202;L, S&#8202;R &#215; pre/late; seed dots</text>')
svg.append('</svg>')
open("l46/recovery.svg", "w").write("\n".join(svg))
print("svg written", len("\n".join(svg)))
