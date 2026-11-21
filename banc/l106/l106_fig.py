"""L106 figure: laterality scatter, one-dark house style, hand-built SVG.

Panel A: 5 antagonist pairs, per-side structure duty (S>=.25, 0.7-Hz windows).
Panel B: 2 unpaired pools, per-side activity (alive >=.05). AXES DIFFER - disclosed.
Filled warm = cfn base (entrainment trunk + tonic DNg100); open cool = free-run
(zero drive, L105); dotted connector = same pool across arms. Whiskers = batch
min/max of per-batch means (3 batches x 16 seeds).
"""
import json
import subprocess

D = json.load(open("l106/figure_data.json"))
BG, FG, MUT, GRID = "#282c34", "#abb2bf", "#5c6370", "#3e4451"
WARM, COOL = "#e06c75", "#61afef"
W, H = 960, 560
TAG = {"Ti": "flips side when free", "Tr": "R>>L", "Ta": "L>>R (inverted)",
       "Sr": "R>L", "Pr": "dead", "LT": "L-only", "FR": "L-only"}
# label dx,dy per pool (points px) to avoid collisions; tuned after render pass
OFF = {"Ti_cfn": (12, -4), "Ti_free": (-12, -12), "Tr_cfn": (12, 2), "Tr_free": (12, -8),
       "Ta_cfn": (14, -6), "Ta_free": (12, -2), "Sr_cfn": (-12, 18), "Sr_free": (14, -2),
       "Pr_cfn": (16, -10), "Pr_free": (-4, 18), "LT_cfn": (14, -8), "LT_free": (14, -6),
       "FR_cfn": (14, 16), "FR_free": (14, 14)}
# free marker sits ~on the cfn marker: one shared label covers both
SHARED_LABEL = {"Pr", "FR"}

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<text x="24" y="34" fill="{FG}" font-size="19" font-weight="bold">'
     f'One-sided antagonist structure is joint-heterogeneous &#8212; and survives zero drive</text>',
     f'<text x="24" y="54" fill="{MUT}" font-size="12.5">BANC female cord, L92 closure substrate &#183; '
     f'per-side means over 48 seeds (3 batches); whiskers = batch min/max &#183; from stored L101/L103/L105 artifacts</text>']


def panel(x0, y0, pw, title, xlab, ylab, rows, lo=0.0, hi=1.0):
    o.append(f'<text x="{x0}" y="{y0-14}" fill="{FG}" font-size="14.5" font-weight="bold">{title}</text>')
    gx0, gy0, gw, gh = x0, y0, pw, pw
    # grid + frame
    for i in range(6):
        v = lo + (hi - lo) * i / 5
        gx = gx0 + gw * i / 5; gy = gy0 + gh - gh * i / 5
        o.append(f'<line x1="{gx:.1f}" y1="{gy0}" x2="{gx:.1f}" y2="{gy0+gh}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<line x1="{gx0}" y1="{gy:.1f}" x2="{gx0+gw}" y2="{gy:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{gx:.1f}" y="{gy0+gh+18}" fill="{MUT}" font-size="11.5" text-anchor="middle">{v:.1f}</text>')
        o.append(f'<text x="{gx0-10}" y="{gy+4:.1f}" fill="{MUT}" font-size="11.5" text-anchor="end">{v:.1f}</text>')
    o.append(f'<rect x="{gx0}" y="{gy0}" width="{gw}" height="{gh}" fill="none" stroke="{MUT}" stroke-width="1.2"/>')
    o.append(f'<text x="{gx0+gw/2}" y="{gy0+gh+38}" fill="{FG}" font-size="12.5" text-anchor="middle">{xlab}</text>')
    o.append(f'<text x="{x0-58}" y="{gy0+gh/2}" fill="{FG}" font-size="12.5" text-anchor="middle" '
             f'transform="rotate(-90 {x0-58} {gy0+gh/2})">{ylab}</text>')

    def P(v):
        return gx0 + gw * (v - lo) / (hi - lo), gy0 + gh - gh * (v - lo) / (hi - lo)

    # diagonal y=x
    dx0, dy1 = P(lo); dx1, dy0 = P(hi)
    o.append(f'<line x1="{dx0:.1f}" y1="{dy0:.1f}" x2="{dx1:.1f}" y2="{dy1:.1f}" stroke="{MUT}" '
             f'stroke-width="1" stroke-dasharray="5 5"/>')
    o.append(f'<text x="{dx1-6:.1f}" y="{dy1+16:.1f}" fill="{MUT}" font-size="11" text-anchor="end">symmetric (L=R)</text>')

    for name, row in rows.items():
        c, f_ = row["cfn"], row["free"]
        cx, cy = P(c["R"]); fx, fy = P(f_["R"])
        # connector cfn -> free
        o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="{COOL}" '
                 f'stroke-width="1" stroke-dasharray="2 4" opacity="0.75"/>')
        # batch whiskers (cfn): horizontal on x (R), vertical on y (L)
        rb0, rb1 = P(c["Rb"][0])[0], P(c["Rb"][1])[0]
        lb0, lb1 = P(c["Lb"][0])[1], P(c["Lb"][1])[1]
        o.append(f'<line x1="{rb0:.1f}" y1="{cy:.1f}" x2="{rb1:.1f}" y2="{cy:.1f}" stroke="{WARM}" stroke-width="1.2"/>')
        o.append(f'<line x1="{cx:.1f}" y1="{lb0:.1f}" x2="{cx:.1f}" y2="{lb1:.1f}" stroke="{WARM}" stroke-width="1.2"/>')
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.5" fill="{WARM}" stroke="#ffffff" stroke-width="0.6"/>')
        o.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="5" fill="{BG}" stroke="{COOL}" stroke-width="2"/>')
        dx, dy = OFF[f"{name}_cfn"]; dx2, dy2 = OFF[f"{name}_free"]
        o.append(f'<text x="{cx+dx:.1f}" y="{cy+dy:.1f}" fill="{FG}" font-size="12" font-weight="bold" '
                 f'text-anchor="{"start" if dx>=0 else "end"}">{name}</text>')
        o.append(f'<text x="{cx+dx:.1f}" y="{cy+dy+12:.1f}" fill="{MUT}" font-size="10.5" '
                 f'text-anchor="{"start" if dx>=0 else "end"}">{TAG[name]}</text>')
        if name not in SHARED_LABEL:
            o.append(f'<text x="{fx+dx2:.1f}" y="{fy+dy2:.1f}" fill="{COOL}" font-size="10.5" '
                     f'text-anchor="{"start" if dx2>=0 else "end"}">{name}</text>')


panel(70, 96, 350, "A &#183; antagonist pairs &#8212; structure duty per side (S &#8805; 0.25)",
      "RIGHT side duty", "LEFT side duty", D["pairs"])
panel(540, 96, 300, "B &#183; unpaired pools &#8212; activity per side (alive &#8805; 0.05)",
      "RIGHT side alive", "LEFT side alive", D["unpaired"], lo=0.0, hi=0.6)

# legend (panel A right edge)
lx, ly = 348, 118
o.append(f'<circle cx="{lx}" cy="{ly}" r="5.5" fill="{WARM}"/>')
o.append(f'<text x="{lx+12}" y="{ly+4}" fill="{FG}" font-size="11.5">base (entrainment trunk)</text>')
o.append(f'<circle cx="{lx}" cy="{ly+20}" r="5" fill="{BG}" stroke="{COOL}" stroke-width="2"/>')
o.append(f'<text x="{lx+12}" y="{ly+24}" fill="{FG}" font-size="11.5">free-run (zero drive)</text>')
o.append(f'<line x1="{lx-4}" y1="{ly+40}" x2="{lx+7}" y2="{ly+40}" stroke="{COOL}" stroke-width="1" stroke-dasharray="2 4"/>')
o.append(f'<text x="{lx+12}" y="{ly+44}" fill="{FG}" font-size="11.5">same pool, arm &#8594; arm</text>')
# side-flip callout
o.append(f'<text x="70" y="{96+350+58}" fill="{MUT}" font-size="11.5">'
         'Ti is the exception: its dominant side flips R&#8594;L when drive is removed (attractor re-roll class); '
         'Tr/Ta/Sr keep their side, magnitudes shrink.</text>')
o.append(f'<text x="24" y="{H-30}" fill="{MUT}" font-size="11">'
         'Pooled both-sides robustness is 0/48 everywhere (L101/L103/L105) &#8212; this scatter shows the one-sided '
         'structure those gates cannot see.</text>')
o.append(f'<text x="24" y="{H-12}" fill="{MUT}" font-size="11">'
         'Axes differ between panels (structure duty vs activity) &#8212; disclosed &#183; '
         'peabrain lane L106 &#183; figure_data.json (C0B-certified extraction)</text>')
o.append("</svg>")

svg = "l106/l106_laterality.svg"
open(svg, "w").write("\n".join(o))
subprocess.run(["rsvg-convert", "-w", "960", "-o", "l106/l106_laterality.png", svg], check=True)
print("rendered", svg, "->", "l106/l106_laterality.png")
