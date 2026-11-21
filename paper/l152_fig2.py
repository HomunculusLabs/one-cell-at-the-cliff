#!/usr/bin/env python3
"""L152 Fig. 2: the clamp-vs-cut grid, hand-built SVG (house style, l136/l160
form). Two curve families — dashed = activity clamps on the INTACT closure,
solid = wiring cuts on the cutwA base — answering the two-factor question in
one picture: the same carrier's ACTIVITY does nothing on the intact brain,
its EDGES flip the cut base, and silencing it flips only the cut base
(substrate-gated).

Before ANY element is drawn, every plotted value is asserted against
numbers.json (the L44 rule) and every pooled Wilson lower bound is
INDEPENDENTLY recomputed (dev < 1e-12). The figure is its own verifier."""
import json, math, subprocess, os

P = os.path.expanduser("~/critters/peabrain-lab")
N = json.load(open(f"{P}/paper/numbers.json"))["__doc__"] if False else json.load(open(f"{P}/paper/numbers.json"))
N = {k: v["v"] for k, v in json.load(open(f"{P}/paper/numbers.json")).items()}

def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - hw, ctr + hw

# ---------------- asserts: every drawn value vs its stored key -------------
A = lambda cond, msg: (_ for _ in ()).throw(AssertionError(msg)) if not cond else None
# family A: activity clamps, intact base
sil_b27 = N["l137.g1"]["sil1110"]; sil_b30 = N["l144.silf"]
vol = N["l137.vol1110"]; s24 = N["l137.sil24"]
A(sil_b27["meanR"] == 0.376 and sil_b27["kR"] == 2 and sil_b27["in_full_band"], "sil1110 B27")
A(sil_b30["meanR"] == 0.392 and sil_b30["kR"] == 3 and sil_b30["dR_vs_full"] == -0.036, "sil1110 B30")
A(vol["meanR"] == 0.486 and vol["kR"] == 7, "vol1110")
A(s24["meanR"] == 0.432 and s24["kR"] == 5 and s24["partial"], "sil24")
# family B: wiring cuts, cutwA base
pw = N["l150.pooled"]; cutwA = pw["cutwA_9batch"]; silW = pw["silW_B30_B33"]; ng25 = pw["cutng25_8batch"]
eOutMot = N["l145.pooled"]["eOutMot_B29_B31"]; eAll = N["l148.pooled"]["eAll_B29_B32"]
top5 = pw["eMotTop5_B31_B33"]; bot5 = pw["eMotBot5_B31_B33"]
h2a = N["l142.h2a"]; h3 = N["l142.h3"]; h2b = N["l142.h2b"]; motin = N["l145.motin"]
A((cutwA["kR"], cutwA["n"]) == (43, 144), "cutwA pooled 43/144")
A((silW["kR"], silW["n"]) == (28, 32) and N["l150.h1"]["b33_class"] == "SUPER", "silW pooled 28/32 SUPER")
A((ng25["kR"], ng25["n"]) == (124, 128), "cutng25 pooled 124/128")
A((eOutMot["kR"], eOutMot["n"]) == (21, 32) and h2b["fires"] is False, "eOutMot pooled 21/32")
A((eAll["kR"], eAll["n"]) == (29, 32), "eAll pooled 29/32")
A((top5["kR"], top5["n"]) == (14, 32) and (bot5["kR"], bot5["n"]) == (8, 32), "motor halves pooled")
A(h2a["fires"] is True and h2a["kR"] == 15 and h2a["meanR"] == 0.781, "eOutInt")
A(h3["kR"] == 15 and h3["meanR"] == 0.793, "eIn")
A(motin["kR"] == 15 and motin["meanR"] == 0.801, "eMotIn")
# the substrate gate, asserted into the figure's bones
A(sil_b27["in_full_band"] is True and sil_b30["dR_vs_full"] == -0.036, "gate: clamp inert on INTACT")
A(N["l144.silw"]["dR_vs_wA"] == 0.189 and N["l144.silw"]["n_down"] == 0, "gate: clamp flips CUT base")
A(N["l148.h_id"]["bit_identical"] is True and N["l148.seid"] == 0.0, "se0 == eAll bit-identical")
# Wilson recompute, dev < 1e-12, on every pooled entry drawn with a whisker
for name, d in (("cutwA", cutwA), ("silW", silW), ("ng25", ng25), ("eOutMot", eOutMot),
                ("eAll", eAll), ("top5", top5), ("bot5", bot5)):
    lb, ub = wilson(d["kR"], d["n"])
    A(abs(lb - d["lbR"]) < 1e-12 and abs(ub - d["ubR"]) < 1e-12, f"wilson recompute {name}")

# ---------------- data rows (label, meanR, k, n, lb|None, class) -----------
CLS = {"SUPER": "#98c379", "PARTIAL": "#e5c07b", "INERT": "#c678dd", "GATE": "#61afef"}
def row(m, k, n, pooled):
    lb = wilson(k, n)[0] if pooled else wilson(k, n)[0]
    return {"m": m, "k": k, "n": n, "lb": lb}

FAM_A = [  # activity clamps, INTACT base (dashed)
    dict(lab="sil1110\n(intact)", dots=[row(0.376, 2, 16, False), row(0.392, 3, 16, False)], cls=CLS["INERT"], sub="2,3 of 16"),
    dict(lab="vol1110", dots=[row(0.486, 7, 16, False)], cls=CLS["INERT"], sub="7 of 16"),
    dict(lab="sil24", dots=[row(0.432, 5, 16, False)], cls=CLS["PARTIAL"], sub="5 of 16"),
]
FAM_B = [  # wiring cuts, cutwA base (solid)
    dict(lab="cutwA\n(nodes 1-24)", dots=[row(cutwA["meanR"], 43, 144, True)], cls=CLS["PARTIAL"], sub="43 of 144"),
    dict(lab="silW\n(the clamp!)", dots=[row(silW["meanR"], 28, 32, True)], cls=CLS["GATE"], sub="28 of 32"),
    dict(lab="cutng25\n(+1110)", dots=[row(ng25["meanR"], 124, 128, True)], cls=CLS["SUPER"], sub="124 of 128"),
    dict(lab="eOutInt\n(70 edges)", dots=[row(0.781, 15, 16, False)], cls=CLS["SUPER"], sub="15 of 16"),
    dict(lab="eIn\n(13 edges)", dots=[row(0.793, 15, 16, False)], cls=CLS["SUPER"], sub="15 of 16"),
    dict(lab="eOutMot\n(10 edges)", dots=[row(eOutMot["meanR"], 21, 32, True)], cls=CLS["PARTIAL"], sub="21 of 32"),
    dict(lab="eMotTop5", dots=[row(top5["meanR"], 14, 32, True)], cls=CLS["INERT"], sub="14 of 32"),
    dict(lab="eMotBot5", dots=[row(bot5["meanR"], 8, 32, True)], cls=CLS["INERT"], sub="8 of 32"),
    dict(lab="eMotIn\n(23 edges)", dots=[row(0.801, 15, 16, False)], cls=CLS["SUPER"], sub="15 of 16"),
    dict(lab="eAll\n(93 edges)", dots=[row(eAll["meanR"], 29, 32, True)], cls=CLS["SUPER"], sub="29 of 32"),
]

# ---------------- SVG (house style: One Dark) -------------------------------
BG, FG, MUT, GRID, PANEL = "#282c34", "#abb2bf", "#5c6370", "#3e4451", "#21252b"
FAM_A_LINE, FAM_B_LINE = "#61afef", "#d19a66"
W, H = 1260, 690
x0, x1, y0, y1 = 140, 1225, 96, 560
Y = lambda v: y1 - v * (y1 - y0)
slots = 14.0; gap_at = 3  # A: slots 0-2, gap 3, B: slots 4-13
SX = lambda i: x0 + (i + 0.5) * (x1 - x0) / slots
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<rect x="{x0-16}" y="{y0-26}" width="{x1-x0+32}" height="{y1-y0+150}" fill="{PANEL}" rx="6"/>',
     f'<text x="30" y="34" fill="{FG}" font-size="19" font-weight="bold">Fig. 2 — clamp vs cut: one carrier, two substrates, opposite verdicts</text>',
     f'<text x="30" y="56" fill="{MUT}" font-size="12">Ti_R mean response (rate model, certified matched operating point) · whiskers = Wilson 95% lower bounds · pooled batches where n&gt;16</text>',
     f'<text x="30" y="74" fill="{MUT}" font-size="12">dashed blue = ACTIVITY family (intact closure) · solid orange = WIRING family (cutwA base, window 1–24 removed)</text>']
for gv in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
    o.append(f'<line x1="{x0}" y1="{Y(gv):.1f}" x2="{x1}" y2="{Y(gv):.1f}" stroke="{GRID}" stroke-width="1"/>')
    o.append(f'<text x="{x0-10}" y="{Y(gv)+4:.1f}" fill="{MUT}" font-size="12" text-anchor="end">{gv:.1f}</text>')
o.append(f'<text x="34" y="{(y0+y1)/2:.0f}" fill="{FG}" font-size="13" text-anchor="middle" transform="rotate(-90 34 {(y0+y1)/2:.0f})">Ti_R mean response</text>')

def family_line(fam, i0, color, dash):
    pts = []
    for j, r in enumerate(fam):
        xs = SX(i0 + j)
        if len(r["dots"]) == 1:
            pts.append((xs, Y(r["dots"][0]["m"])))
        else:  # multi-dot row: use the mean of means for the family line
            pts.append((xs, Y(sum(d["m"] for d in r["dots"]) / len(r["dots"]))))
    d = f' M {pts[0][0]:.1f} {pts[0][1]:.1f} ' + " ".join(f'L {x:.1f} {y:.1f}' for x, y in pts[1:])
    o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.8"{" stroke-dasharray=\"8 5\"" if dash else ""} opacity="0.85"/>')

def draw_fam(fam, i0):
    family_line(fam, i0, FAM_A_LINE if i0 == 0 else FAM_B_LINE, dash=(i0 == 0))
    for j, r in enumerate(fam):
        xs = SX(i0 + j)
        for d in r["dots"]:
            yv = Y(d["m"]); ylb = Y(d["lb"])
            o.append(f'<line x1="{xs:.1f}" y1="{yv:.1f}" x2="{xs:.1f}" y2="{ylb:.1f}" stroke="{r["cls"]}" stroke-width="2" opacity="0.9"/>')
            o.append(f'<line x1="{xs-5:.1f}" y1="{ylb:.1f}" x2="{xs+5:.1f}" y2="{ylb:.1f}" stroke="{r["cls"]}" stroke-width="2"/>')
            o.append(f'<circle cx="{xs:.1f}" cy="{yv:.1f}" r="7" fill="{r["cls"]}"/>')
        for k2, ln in enumerate(r["lab"].split("\n")):
            o.append(f'<text x="{xs:.1f}" y="{y1+22+13*k2}" fill="{FG if k2==0 else MUT}" font-size="{12 if k2==0 else 10.5}" text-anchor="middle"{" font-weight=\"bold\"" if k2==0 else ""}>{ln}</text>')
        o.append(f'<text x="{xs:.1f}" y="{y1+58}" fill="{MUT}" font-size="9.5" text-anchor="middle">{r["sub"]}</text>')

draw_fam(FAM_A, 0)
draw_fam(FAM_B, 4)
# group captions
o.append(f'<text x="{SX(1):.1f}" y="{y1+84}" fill="{FAM_A_LINE}" font-size="13" font-weight="bold" text-anchor="middle">ACTIVITY · intact base</text>')
o.append(f'<text x="{SX(8.5):.1f}" y="{y1+84}" fill="{FAM_B_LINE}" font-size="13" font-weight="bold" text-anchor="middle">WIRING · cutwA base (window 1–24 removed)</text>')
# se0 == eAll annotation (bit-identical, drawn as an open twin of the eAll dot)
xe, ye = SX(13), Y(eAll["meanR"])
o.append(f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="11" fill="none" stroke="{CLS["GATE"]}" stroke-width="1.6"/>')
o.append(f'<text x="{xe:.1f}" y="{ye-17:.1f}" fill="{CLS["GATE"]}" font-size="10.5" text-anchor="middle">+clamp ≡ bit-identical</text>')
# the gate annotation: same clamp, two bases
xa, ya = SX(0) + 6, Y(0.384)
xb, yb = SX(5) - 6, Y(silW["meanR"])
o.append(f'<path d="M {xa:.1f} {ya-24:.1f} C {(xa+xb)/2:.1f} {ya-110:.1f}, {(xa+xb)/2:.1f} {yb-60:.1f}, {xb:.1f} {yb-22:.1f}" fill="none" stroke="{CLS["GATE"]}" stroke-width="1.6" stroke-dasharray="3 4" marker-end="url(#arr)"/>')
o.append(f'<text x="{(xa+xb)/2:.1f}" y="{min(ya,yb)-96:.1f}" fill="{CLS["GATE"]}" font-size="12" font-weight="bold" text-anchor="middle">same clamp, X[1110]=0 — inert here…</text>')
o.append(f'<text x="{(xa+xb)/2:.1f}" y="{min(ya,yb)-80:.1f}" fill="{CLS["GATE"]}" font-size="12" text-anchor="middle">…SUPER here (substrate-gated)</text>')
# legend
lg = [(CLS["SUPER"], "SUPER (class leg)"), (CLS["PARTIAL"], "PARTIAL / half-step"), (CLS["INERT"], "inert / noise"), (CLS["GATE"], "substrate-gated flip")]
for i2, (c, t) in enumerate(lg):
    lx = 30 + i2 * 205
    o.append(f'<circle cx="{lx}" cy="{H-22}" r="6" fill="{c}"/><text x="{lx+12}" y="{H-18}" fill="{FG}" font-size="11.5">{t}</text>')
o.append(f'<text x="{W-30}" y="{H-18}" fill="{MUT}" font-size="10.5" text-anchor="end">asserted vs numbers.json at draw time · L152</text>')
o.append('<defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="' + CLS["GATE"] + '"/></marker></defs>')
o.append("</svg>")
svg = "\n".join(o)

# analytic QA: every y-position on canvas
import re
ys = [float(m) for m in re.findall(r'y="([0-9.]+)"', svg)]
A(max(ys) < H and min(ys) >= 0, "text/element off-canvas vertically")

out_svg = f"{P}/paper/fig_l152.svg"
open(out_svg, "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W), out_svg, "-o", f"{P}/paper/fig_l152.png"], check=True)
print("Fig. 2 drawn:", out_svg, "->", f"{P}/paper/fig_l152.png")
print("rows: 3 activity + 10 wiring + se0≡; asserts ALL GREEN pre-ink")
