"""L160 figure: the .100 Hz sub-band slow line is carried by a Tr/Ta/Sr pool
subset, not an antagonist clock. Hand-built SVG (house style; matplotlib absent).
Numbered Fig. 3: Fig 1 = l136 transition law, Fig 2 is reserved for the L152
clamp-vs-cut grid (seeded earlier, owner-gated) — collision disclosed in LANE.md.
Before drawing ANY element, re-verify every plotted value against the SOURCE
static jsons (l157 + l156) and recompute Wilson lbs from stored k/n (L44 rule).
"""
import json
import math
import os
import subprocess

BANC = os.path.expanduser("~/critters/peabrain-lab/banc")
S157 = json.load(open(f"{BANC}/l157/static.json"))
S156 = json.load(open(f"{BANC}/l156/static.json"))
P = S157["pooled"]


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - hw, ctr + hw


# ---------------- source re-verification (defense vs hand-edited jsons) -----
POOLS = ["Ti_fL", "Ti_fR", "Ti_eL", "Ti_eR", "Tr_fL", "Tr_fR", "Tr_eL", "Tr_eR",
         "Ta_aL", "Ta_aR", "Ta_bL", "Ta_bR", "Pr_aL", "Pr_aR", "Pr_bL", "Pr_bR",
         "Sr_aL", "Sr_aR", "Sr_bL", "Sr_bR"]
assert list(P.keys()) == POOLS + ["mm", "xm"], "pooled key set/order drifted"
for k, e in P.items():
    lb, ub = wilson(e["below"], e["n"])
    assert e["n"] == 36, k
    assert abs(e["wilson_lb"] - lb) < 1e-12, (k, e["wilson_lb"], lb)
CARRIER = [k for k in POOLS if P[k]["wilson_lb"] >= 0.5]          # PREREG rule
assert CARRIER == ["Tr_fL", "Tr_eL", "Tr_eR", "Ta_aL", "Ta_aR", "Ta_bR",
                   "Sr_aL", "Sr_bL"], CARRIER
assert len(CARRIER) == 8
assert max(P[k]["below"] for k in POOLS if k.startswith("Ti")) <= 6
assert max(P[k]["below"] for k in POOLS if k.startswith("Pr")) == 20
assert P["mm"]["below"] == P["xm"]["below"] == P["mm"]["n"] == 36
med_mm = P["mm"]["med_f_below"]
assert abs(med_mm - 0.10011638190876199) < 1e-9
carmed = sorted(P[k]["med_f_below"] for k in CARRIER)
subset_med = (carmed[3] + carmed[4]) / 2
assert round(subset_med, 3) == 0.100, subset_med
B6 = S156["pooled"]["b65_nonjitter"]
FU = S156["pooled"]["full_nonjitter"]
for q, (k_, n_, lb_) in ((B6, (518, 518, 0.9926386477046583)),
                         (FU, (361, 500, 0.6811514003636959))):
    assert (q["below"], q["n"]) == (k_, n_) and abs(q["wilson_lb"] - lb_) < 1e-12
assert B6["files"] == 28 and FU["files"] == 27
assert round(B6["med_f_below"], 3) == 0.100 and round(FU["med_f_below"], 3) == 0.117
assert (B6["survive"], B6["agree"]) == (518, 414) and (FU["survive"], FU["agree"]) == (331, 80)
VERIFIED = True

# ---------------- palette / canvas -------------------------------------------
BG, FG, MUT = "#282c34", "#abb2bf", "#5c6370"
GRID, PANEL = "#3e4451", "#21252b"
C_CAR, C_WEAK, C_DEAD, C_AGG, C_CLO = "#98c379", "#e5c07b", "#e06c75", "#61afef", "#c678dd"
W, H = 1680, 800
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<text x="30" y="32" fill="{FG}" font-size="18" font-weight="bold">'
     f'L160 / Fig. 3: the .100 Hz sub-band slow line is carried by a Tr/Ta/Sr pool subset &#8212; not an antagonist clock</text>',
     f'<text x="30" y="54" fill="{MUT}" font-size="13">'
     f'per-pool Wilson 95% lb, slow line present (global peak below the 0.3 Hz band floor); pooled l150/l154 b65-class arms, n=36 traces/pool;'
     f' every value re-verified against l157 + l156 static.jsons at draw time</text>']

YTICKS = [0, .2, .4, .6, .8, 1.0]


def frame(px, py, pw, ph, ylab):
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{PANEL}" stroke="{GRID}"/>')
    for yv in YTICKS:
        y = py + ph - yv * ph
        o.append(f'<line x1="{px}" y1="{y:.1f}" x2="{px+pw}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
        o.append(f'<text x="{px-9}" y="{y+4:.1f}" fill="{MUT}" font-size="12" text-anchor="end">{yv:.1f}</text>')
    o.append(f'<text x="{px-46}" y="{py+ph/2}" fill="{FG}" font-size="13" text-anchor="middle" '
             f'transform="rotate(-90 {px-46} {py+ph/2})">{ylab}</text>')


# ---------------- Panel A: per-pool Wilson-lb bars ---------------------------
px, py, pw, ph = 96, 120, 1090, 440
frame(px, py, pw, ph, "Wilson 95% lb, slow line present")
SLOTS = POOLS + ["mm", "xm"]
FAM = [("Ti", 0, 4), ("Tr", 4, 8), ("Ta", 8, 12), ("Pr", 12, 16), ("Sr", 16, 20), ("agg", 20, 22)]
sx = lambda i: px + (i + 0.5) * pw / len(SLOTS)
sy = lambda v: py + ph - max(0.0, min(1.0, v)) * ph
# showing threshold
yTh = sy(0.5)
o.append(f'<line x1="{px}" y1="{yTh:.1f}" x2="{px+pw}" y2="{yTh:.1f}" stroke="{FG}" stroke-width="1" '
         f'stroke-dasharray="5,5" opacity="0.7"/>')
o.append(f'<text x="{px+8}" y="{yTh-6:.1f}" fill="{FG}" font-size="11.5" text-anchor="start">showing threshold: pooled Wilson lb &#8805; .5 (PREREG)</text>')
# separator before aggregate columns
xsep = (sx(19) + sx(20)) / 2
o.append(f'<line x1="{xsep:.1f}" y1="{py+6}" x2="{xsep:.1f}" y2="{py+ph-6}" stroke="{GRID}" stroke-width="1.2" stroke-dasharray="2,4"/>')
kn_labels = []
for i, name in enumerate(SLOTS):
    e = P[name]
    lb = e["wilson_lb"]
    frac = e["below"] / e["n"]
    col = C_AGG if name in ("mm", "xm") else (C_CAR if name in CARRIER else (C_DEAD if e["below"] == 0 else C_WEAK))
    x = sx(i)
    o.append(f'<rect x="{x-14:.1f}" y="{sy(lb):.1f}" width="28" height="{py+ph-sy(lb):.1f}" fill="{col}" opacity="0.88"/>')
    o.append(f'<line x1="{x-17:.1f}" y1="{sy(frac):.1f}" x2="{x+17:.1f}" y2="{sy(frac):.1f}" stroke="{FG}" stroke-width="1.6"/>')
    kn = f"{e['below']}/{e['n']}"
    kn_labels.append(kn)
    bold = ' font-weight="bold"' if name in CARRIER or name in ("mm", "xm") else ""
    o.append(f'<text x="{x:.1f}" y="{py+ph+18}" fill="{MUT}" font-size="10" text-anchor="middle">{kn}</text>')
    o.append(f'<text x="{x:.1f}" y="{py+ph+34}" fill="{col}" font-size="10.5" text-anchor="middle"{bold}>{name}</text>')
# family brackets
FNAMES = {"Ti": "tibia", "Tr": "femur roll", "Ta": "tarsus", "Pr": "promotor", "Sr": "sternal rot"}
for fam, i0, i1 in FAM:
    xa, xb = sx(i0) - 20, sx(i1 - 1) + 20
    yb = py + ph + 48
    o.append(f'<path d="M {xa:.1f} {yb-6:.1f} L {xa:.1f} {yb:.1f} L {xb:.1f} {yb:.1f} L {xb:.1f} {yb-6:.1f}" fill="none" stroke="{MUT}" stroke-width="1"/>')
    lbl = fam if fam != "agg" else "motor-mass aggregates"
    if fam != "agg":
        lbl = f"{fam} ({FNAMES[fam]})"
    o.append(f'<text x="{(xa+xb)/2:.1f}" y="{yb+15}" fill="{FG}" font-size="11.5" text-anchor="middle">{lbl}</text>')
# .100 Hz annotation at mm
xmm = sx(20)
o.append(f'<text x="{xmm:.1f}" y="{sy(P["mm"]["wilson_lb"])-16:.1f}" fill="{FG}" font-size="11" text-anchor="middle">median .100 Hz</text>')
# legend
LEGL = [("carrier (lb &#8805; .5)", C_CAR), ("weak 0 &lt; lb &lt; .5", C_WEAK), ("dead (0/36)", C_DEAD), ("mm / xm aggregate", C_AGG)]
for j, (nm, col) in enumerate(LEGL):
    o.append(f'<rect x="{px+18+j*180}" y="{py-24}" width="12" height="12" fill="{col}"/>')
    o.append(f'<text x="{px+35+j*180}" y="{py-14}" fill="{FG}" font-size="12">{nm}</text>')
o.append(f'<text x="{px}" y="{py-46}" fill="{FG}" font-size="14.5" font-weight="bold">'
         f'A &#183; carrier census: 8 of 20 pools (Tr/Ta/Sr), subset median .100 Hz; Ti &#8804; 6/36, Pr max 20/36; mm/xm 36/36</text>')
o.append(f'<text x="{px}" y="{py-30}" fill="{MUT}" font-size="11.5">bar = pooled Wilson lb (claim metric); dash marker = raw k/n; two low-median carriers (Tr_eL, Ta_aR) peak even further below band</text>')

# ---------------- Panel B: b65 vs closure (dash separation) -----------------
bx, by, bw, bh = 1230, 120, 410, 300
frame(bx, by, bw, bh, "sub-band fraction (mm)")
BARSB = [("l65 baseline (b65)", B6, C_AGG, None), ("closure graph, 'full' arm", FU, C_CLO, "7,5")]  # dash on closure stem
for j, (lab, q, col, dash) in enumerate(BARSB):
    lb, ub = wilson(q["below"], q["n"])
    assert abs(lb - q["wilson_lb"]) < 1e-12
    phat = q["below"] / q["n"]
    x = bx + (j + 0.5) * bw / 2
    dashattr = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<line x1="{x:.1f}" y1="{sy(lb):.1f}" x2="{x:.1f}" y2="{sy(ub):.1f}" stroke="{col}" stroke-width="2.6"{dashattr}/>')
    if dash:
        o.append(f'<circle cx="{x:.1f}" cy="{sy(phat):.1f}" r="6" fill="{PANEL}" stroke="{col}" stroke-width="2.5"/>')
    else:
        o.append(f'<circle cx="{x:.1f}" cy="{sy(phat):.1f}" r="6" fill="{col}"/>')
    for dy, ln in enumerate(lab.split("\n")):
        o.append(f'<text x="{x:.1f}" y="{by+bh+22+dy*15}" fill="{FG}" font-size="12.5" text-anchor="middle">{ln}</text>')
    sub = [f"lb {round(q['wilson_lb'],3):.3f}",
           f"{q['below']}/{q['n']} &#183; median {round(q['med_f_below'],3):.3f} Hz",
           f"detrend-survive {q['survive']}/{q['below']}",
           f"agree {q['agree']}/{q['below']} &#183; {q['files']} files"]
    if not dash:
        sub.append("CI collapses at k=n")
    for dy, ln in enumerate(sub):
        o.append(f'<text x="{x:.1f}" y="{by+bh+44+dy*16}" fill="{MUT}" font-size="11" text-anchor="middle">{ln}</text>')
o.append(f'<text x="{bx}" y="{by-46}" fill="{FG}" font-size="13.5" font-weight="bold">B &#183; pervasion: near-universal on l65, weaker on closure</text>')
o.append(f'<text x="{bx}" y="{by-30}" fill="{MUT}" font-size="11.5">Wilson bars (mm traces); solid = b65; dashed stem + hollow = closure (dash rule)</text>')

# footer provenance
o.append(f'<text x="30" y="{H-38}" fill="{MUT}" font-size="11.5">'
         f'substrate: l65 female BANC cord subnet; pools enumerated from peripheral_target_type (L101 vocabulary); '
         f'sources: l157/static.json pooled (B33+l154 batches, 3 file-arm combos x n=12) + l156/static.json pooled (28+27 stored files)</text>')
o.append(f'<text x="30" y="{H-20}" fill="{MUT}" font-size="11.5">'
         f'all lbs recomputed from stored k/n at draw time (max dev &lt; 1e-12); carrier rule, Ti/Pr pins, medians and split-half counts asserted pre-ink; figure numbered Fig. 3 (Fig 2 reserved, L152)</text>')
o.append("</svg>")

svg = "\n".join(o) + "\n"
open(f"{BANC}/l160/fig_l160.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "2520", "-o", f"{BANC}/l160/fig_l160.png",
                f"{BANC}/l160/fig_l160.svg"], check=True)
# numeral trace guard: every k/n label is in the text layer
joined = " ".join(__import__("re").findall(r"<text[^>]*>(.*?)</text>", svg, __import__("re").S))
missing = [f"{n}:{k}" for n, k in zip(SLOTS, kn_labels) if k not in joined]
assert not missing, missing
print("figure written:", f"{BANC}/l160/fig_l160.png", os.path.getsize(f"{BANC}/l160/fig_l160.png"), "bytes")
print("source re-verification asserts: ALL GREEN (22 pooled lbs + 2 l156 arms recomputed; carrier/Ti/Pr/median/split-half pins)")
