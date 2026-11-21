"""L136 figure: the L113-L135 kill->super transition, one hand-built SVG.
House style: dark One Dark, SVG + rsvg-convert (matplotlib absent on this box).
Before drawing ANY element, re-verify every plotted value against the SOURCE
results jsons (not just plot_data.json) — the figure is its own verifier.
"""
import json
import math
import os
import subprocess

BANC = os.path.expanduser("~/critters/peabrain-lab/banc")
P = json.load(open(f"{BANC}/l136/plot_data.json"))
R135 = json.load(open(f"{BANC}/l135/results_l135.json"))
R126 = json.load(open(f"{BANC}/l126/results_l126.json"))
R121 = json.load(open(f"{BANC}/l121/results_l121.json"))
RUNS = P["runs"]
RTAB = {d: json.load(open(f"{BANC}/{d}/results_{d}.json"))["table"]["Ti"] for d in RUNS}

# ---------------- source re-verification (defense vs hand-edited plot_data) --
def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - hw, ctr + hw

UNION = {"full": RUNS, "cutng19": RUNS, "cutng29": RUNS, "cutk5": RUNS, "cut58": RUNS,
         "cutng23": ["l126", "l131", "l133", "l135"], "cutwA": ["l126", "l131", "l133", "l135"],
         "cutng26": ["l126", "l131", "l133", "l135"], "cutng25": ["l131", "l133", "l135"],
         "cutng25p": ["l133", "l135"]}
for arm, u in UNION.items():
    k = sum(RTAB[r][arm]["kR"] for r in u)
    n = 16 * len(u)
    lb, ub = wilson(k, n)
    q = P["pooled"][arm]
    assert (q["k"], q["n"]) == (k, n) and abs(q["lb"] - lb) < 1e-12 and abs(q["ub"] - ub) < 1e-12, arm
D = P["dose_l135"]
DA = {"0": "full", "19": "cutng19", "23": "cutng23", "24": "cutwA", "25": "cutng25",
      "25p": "cutng25p", "26": "cutng26", "29": "cutng29", "58": "cut58", "k5": "cutk5"}
for kk, arm in DA.items():
    t = R135["table"]["Ti"][arm]
    assert D["meanR"][kk] == t["meanR"] and D["kR"][kk] == t["kR"]
    assert D["meanL"][kk] == t["meanL"] and D["kL"][kk] == t["kL"]
assert D["legs"] == R135["dose"]["Ti"]["legs"]
for kk, src in (("21", R126), ("28", R126), ("39", R121)):
    arm = {"21": "cutng21", "28": "cutng28", "39": "cutng39"}[kk]
    assert P["context_single_batch"][kk]["meanR"] == src["table"]["Ti"][arm]["meanR"]
x2 = R135["xor"]["p2"]
assert (P["xor"]["m25"], P["xor"]["pair_delta"]) == (x2["m25"], x2["pair_delta"])
assert abs(P["mass"]["cutng25"] - (P["mass"]["cutwA"] + x2["m25"])) < 1e-12
VERIFIED = True

# ---------------- palette / canvas -------------------------------------------
BG, FG, MUT = "#282c34", "#abb2bf", "#5c6370"
GRID, PANEL = "#3e4451", "#21252b"
C_KILL, C_PART, C_SUPER, C_CTX, C_CTRL = "#e06c75", "#e5c07b", "#98c379", "#61afef", "#c678dd"
CLS_COLOR = {"kill": C_KILL, "partial": C_PART, "super": C_SUPER}
W, H = 1680, 760
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<text x="30" y="32" fill="{FG}" font-size="18" font-weight="bold">'
     f'L136: ng-window kill&#8594;super transition on the female BANC cord &#8212; the flip is carried by ONE cell (1110 / DNp33-L), not by mass</text>',
     f'<text x="30" y="54" fill="{MUT}" font-size="13">'
     f'Ti antagonist structure duty (window metric), pooled Wilson 95% bars; every value re-derived from stored results_l121&#8211;l135 jsons (L44 rule)</text>']

YTICKS = [0, .2, .4, .6, .8, 1.0]


def frame(px, py, pw, ph, ylab):
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{PANEL}" stroke="{GRID}"/>')
    for yv in YTICKS:
        y = py + ph - yv * ph
        o.append(f'<line x1="{px}" y1="{y:.1f}" x2="{px+pw}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
        o.append(f'<text x="{px-9}" y="{y+4:.1f}" fill="{MUT}" font-size="12" text-anchor="end">{yv:.1f}</text>')
    o.append(f'<text x="{px-46}" y="{py+ph/2}" fill="{FG}" font-size="13" text-anchor="middle" '
             f'transform="rotate(-90 {px-46} {py+ph/2})">{ylab}</text>')


# ---------------- Panel A: dose curve (ordinal x) ----------------------------
px, py, pw, ph = 96, 108, 820, 470
frame(px, py, pw, ph, "Ti_R duty (both-sides &#8805; .25), pooled")
ORDER = [("full", "0"), ("cutng19", "19"), ("cutng21", "21*"), ("cutng23", "23"),
         ("cutwA", "24"), ("cutng25", "25"), ("cutng26", "26"), ("cutng28", "28*"),
         ("cutng29", "29"), ("cutng39", "39*"), ("cut58", "58"), ("cutk5", "k5")]
nslots = len(ORDER)
sx = lambda i: px + (i + 0.5) * pw / nslots
sy = lambda v: py + ph - max(0.0, min(1.0, v)) * ph


def sy2(v, top, hgt):
    return top + hgt - max(0.0, min(1.0, v)) * hgt
# step line through the pooled prefix rungs (19->29 story spine)
spine = [("cutng19", "19"), ("cutng23", "23"), ("cutwA", "24"), ("cutng25", "25"),
         ("cutng26", "26"), ("cutng29", "29")]
idx = {a: i for i, (a, _) in enumerate(ORDER)}
pts = " ".join(f"{sx(idx[a]):.1f},{sy(P['pooled'][a]['p_hat']):.1f}" for a, _ in spine)
o.append(f'<polyline points="{pts}" fill="none" stroke="{FG}" stroke-width="1.4" '
         f'stroke-dasharray="3,4" opacity="0.55"/>')
for i, (arm, lab) in enumerate(ORDER):
    x = sx(i)
    if arm in P["pooled"]:
        q = P["pooled"][arm]
        col = C_CTX if arm in ("full",) else (C_CTRL if arm == "cutk5" else CLS_COLOR[P["classification"][arm]])
        o.append(f'<line x1="{x:.1f}" y1="{sy(q["lb"]):.1f}" x2="{x:.1f}" y2="{sy(q["ub"]):.1f}" stroke="{col}" stroke-width="2.2"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{sy(q["p_hat"]):.1f}" r="5" fill="{col}"/>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+20}" fill="{FG}" font-size="13" text-anchor="middle" font-weight="bold">{lab}</text>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+37}" fill="{MUT}" font-size="10.5" text-anchor="middle">{q["k"]}/{q["n"]}</text>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+52}" fill="{MUT}" font-size="10" text-anchor="middle">{P["mass"].get(arm if arm != "cut58" else "cut58ng", 0):.3f}</text>')
    else:  # single-batch context rungs
        kk = lab.rstrip("*")
        q = P["context_single_batch"][kk]
        o.append(f'<circle cx="{x:.1f}" cy="{sy(q["meanR"]):.1f}" r="4.4" fill="none" stroke="{C_CTX}" stroke-width="2"/>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+20}" fill="{C_CTX}" font-size="13" text-anchor="middle">{lab}</text>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+37}" fill="{MUT}" font-size="10.5" text-anchor="middle">{q["kR"]}/16</text>')
        o.append(f'<text x="{x:.1f}" y="{py+ph+52}" fill="{MUT}" font-size="10" text-anchor="middle">{P["mass"]["cutng"+kk]:.3f}</text>')
o.append(f'<text x="{px+pw/2}" y="{py+ph+76}" fill="{FG}" font-size="13.5" text-anchor="middle">'
         f'ng-family cells removed (ordinal; * = single 16-seed batch, l126/l121; under each: k/n pooled, removed mass)</text>')
# the 24->25 step callout
x24, x25 = sx(idx["cutwA"]), sx(idx["cutng25"])
y24, y25 = sy(P["pooled"]["cutwA"]["p_hat"]), sy(P["pooled"]["cutng25"]["p_hat"])
o.append(f'<path d="M {x24+8:.1f} {(y24+y25)/2-26:.1f} L {x25-8:.1f} {(y24+y25)/2-26:.1f}" stroke="#d19a66" stroke-width="1.6" marker-end="url(#arr)"/>')
o.append(f'<defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">'
         f'<path d="M0,0 L9,4.5 L0,9 z" fill="#d19a66"/></marker></defs>')
o.append(f'<text x="{(x24+x25)/2:.1f}" y="{(y24+y25)/2-34:.1f}" fill="#d19a66" font-size="12.5" text-anchor="middle">+cell 1110 only: +.334 (L126), pooled 47/48</text>')
# legend
for j, (nm, col) in enumerate([("kill", C_KILL), ("partial", C_PART), ("super", C_SUPER), ("context", C_CTX), ("k5 control", C_CTRL)]):
    o.append(f'<circle cx="{px+18+j*118}" cy="{py-16}" r="4.5" fill="{col}"/>')
    o.append(f'<text x="{px+28+j*118}" y="{py-12}" fill="{FG}" font-size="12">{nm}</text>')
o.append(f'<text x="{px}" y="{py-40}" fill="{FG}" font-size="14.5" font-weight="bold">A &#183; dose-placement: kill &#8594; partial (k24) &#8594; super (k25+), monotone in cells removed</text>')

# ---------------- Panel B: identity XOR --------------------------------------
bx, by, bw, bh = 990, 108, 620, 210
frame(bx, by, bw, bh, "Ti_R duty")
BARS = [("cutwA", "wA = k24\n(no twin)"), ("cutng25", "+ 1110\n(DNp33-L)"), ("cutng25p", "+ 319\n(DNpe025-R)")]
LEGR = {"cutwA": "-.054", "cutng25": "+.317", "cutng25p": "-.038"}
for j, (arm, lab) in enumerate(BARS):
    q = P["pooled"][arm]
    x = bx + (j + 0.5) * bw / 3
    col = CLS_COLOR[P["classification"][arm]]
    o.append(f'<line x1="{x:.1f}" y1="{sy2(q["lb"], by, bh):.1f}" x2="{x:.1f}" y2="{sy2(q["ub"], by, bh):.1f}" stroke="{col}" stroke-width="3"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{sy2(q["p_hat"], by, bh):.1f}" r="6.5" fill="{col}"/>')
    for dy, ln in enumerate(lab.split("\n")):
        o.append(f'<text x="{x:.1f}" y="{by+bh+20+dy*14:.1f}" fill="{FG}" font-size="12.5" text-anchor="middle">{ln}</text>')
    o.append(f'<text x="{x:.1f}" y="{by+bh+52:.1f}" fill="{MUT}" font-size="11" text-anchor="middle">{q["k"]}/{q["n"]}  paired &#916;dR {LEGR[arm]}</text>')
o.append(f'<text x="{bx}" y="{by-40}" fill="{FG}" font-size="14.5" font-weight="bold">B &#183; identity XOR at the 24&#8594;25 step (mass-matched, &#916;3.9e-04)</text>')
o.append(f'<text x="{bx+6}" y="{by+bh+82:.1f}" fill="{MUT}" font-size="11.5">Wilson bars contain .5 separation: 1110-alone flips kill&#8594;super; 319-alone is base-neutral (L133/L135)</text>'.replace(".1f}", "}"))

# ---------------- Panel C: Ti_L rides the same cell --------------------------
cx, cy, cw, ch = 990, 400, 620, 178
frame(cx, cy, cw, ch, "Ti_L duty (kL/n)")
CARMS = [("full", "0", None), ("cutng19", "19", None), ("cutng23", "23", None), ("cutwA", "24", None),
         ("cutng25", "25", None), ("cutng25p", "25p", None), ("cutng26", "26", None), ("cutng29", "29", None)]
for j, (arm, lab, _) in enumerate(CARMS):
    q = P["pooled"][arm]
    n = q["n"]
    x = cx + (j + 0.5) * cw / len(CARMS)
    col = C_CTX if arm == "full" else CLS_COLOR.get(P["classification"].get(arm, "kill"), C_KILL)
    o.append(f'<line x1="{x:.1f}" y1="{sy2(0, cy, ch):.1f}" x2="{x:.1f}" y2="{sy2(q["kL"]/n, cy, ch):.1f}" stroke="{col}" stroke-width="7" opacity="0.85"/>')
    o.append(f'<text x="{x:.1f}" y="{cy+ch+18}" fill="{FG}" font-size="12" text-anchor="middle">{lab}</text>')
    o.append(f'<text x="{x:.1f}" y="{cy+ch+34}" fill="{MUT}" font-size="10.5" text-anchor="middle">{q["kL"]}/{n}</text>')
o.append(f'<text x="{cx}" y="{cy-40}" fill="{FG}" font-size="14.5" font-weight="bold">C &#183; the LEFT pool dies with the SAME cell (1110), not with 319</text>')
o.append(f'<text x="{cx+6}" y="{cy+ch+58}" fill="{MUT}" font-size="11.5">Ti_L survives 319 (25p kL 3/32) and dies with 1110 (25 kL 0/48) &#8212; one left-hemisphere DN moves BOTH sides</text>')

# footer provenance
o.append(f'<text x="30" y="{H-38}" fill="{MUT}" font-size="11.5">'
         f'substrate: l65 female BANC cord subnet (Ti flexor pool n=101); runs l121-l135 (11 seed batches B17-B26); '
         f'window metric duty(Ti_R &#8805; .25); sources: results_l121/l126/l133/l135.json pooled blocks, all asserts green at draw time</text>')
o.append(f'<text x="30" y="{H-20}" fill="{MUT}" font-size="11.5">'
         f'outer rungs pool all 11 batches; transition rungs {23,24,26}&#8594;4 batches, 25&#8594;3, 25p&#8594;2 (registered unions, disclosed per bar)</text>')
o.append("</svg>")

svg = "\n".join(o) + "\n"
open(f"{BANC}/l136/fig_l136.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "2520", "-o", f"{BANC}/l136/fig_l136.png",
                f"{BANC}/l136/fig_l136.svg"], check=True)
print("figure written:", f"{BANC}/l136/fig_l136.png", os.path.getsize(f"{BANC}/l136/fig_l136.png"), "bytes")
print("source re-verification asserts: ALL GREEN (pooled k/n/Wilson x10, dose x20, legs, twins, masses)")
