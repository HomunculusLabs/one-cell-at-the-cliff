"""L59 figure: (A) pooled duty per seed x arm — the .5 gate is a FAIR COIN at
census n (8/16 both arms, Wilson [.28,.72]), miss seeds MIGRATE between arms
(4/8 shared); (B) fast-window duty spread — wide but the dead tail is 4/16
(P2 marginal FAIL), 7/16 below .25; (C) failing-segment side anatomy —
S_L-owned majority both arms (P3) + the hop decorrelates entry state from
outcome (P5: +.61 -> +.17). SVG -> rsvg-convert. Numbers from artifacts."""
import json
import subprocess

res = json.load(open("l59/results_l59.json"))
dist, anat, preds = res["distributions"], res["miss_anatomy"], res["predictions"]
SEEDS = res["meta"]["seeds"]
ARM_COL = {"hynohop": "#7fd4ff", "hybrid": "#ffb0d4"}
W, H = 1560, 880
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L59 spec ensemble (n=16 census seeds): the pooled gate is a FAIR '
       f'COIN, the miss MIGRATES, S_L owns it</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">l51 hybrid + l55 '
       f'hynohop schedules verbatim; substrate l32 arm-A frozen; duty = '
       f'both antagonist S &#8805; .25 over [seg+500, seg)</text>',
       f'<text x="40" y="82" fill="{MUT}" font-size="13">anchors: seeds '
       f'11/22/33 bit-identical to l55 (0.0, mm + 4 antagonist traces) = '
       f'15th chain anchor; hop wiring fd=2000 on 16/16</text>']

AXH = 300


def frame(x, y, w, h, title):
    svg.append(f'<text x="{x}" y="{y-14}" fill="{FG}" font-size="16" '
               f'font-weight="bold">{title}</text>')
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
               f'fill="none" stroke="{GRID}"/>')


def yline(x, y, w, h, v, lab, col="#33363f", dash=""):
    yy = y + h * (1 - v)
    svg.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x+w}" y2="{yy:.1f}" '
               f'stroke="{col}" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{x-6}" y="{yy+4:.1f}" fill="{MUT}" font-size="12" '
               f'text-anchor="end">{lab}</text>')


# ---------------- panel A: pooled duty per seed ----------------
ax, ay, aw = 60, 140, 460
frame(ax, ay, aw, AXH, "A &#183; pooled duty per seed: 8/16 &#8805; .5 in BOTH arms")
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yline(ax, ay, aw, AXH, v, f"{v:.2f}")
yline(ax, ay, aw, AXH, .5, "", "#ff8f8f", "6 3")
svg.append(f'<text x="{ax+8}" y="{ay+AXH*(1-.5)-8:.1f}" fill="#ff8f8f" '
           f'font-size="12">pooled gate .5</text>')
missA = {a: {m["seed"] for m in anat[a]["misses"]} for a in ARM_COL}
for j, a in enumerate(ARM_COL):
    x0 = ax + 70 + j * 210
    for i, s in enumerate(SEEDS):
        v = dist[a]["pooled"][i]
        yy = ay + AXH * (1 - v)
        miss = s in missA[a]
        svg.append(f'<circle cx="{x0 + i*12:.1f}" cy="{yy:.1f}" r="6" '
                   f'fill="{ARM_COL[a]}" fill-opacity="{0.3 if miss else 1}" '
                   f'stroke="{ARM_COL[a] if not miss else "#ff8f8f"}" '
                   f'stroke-width="1.5"/>')
    svg.append(f'<text x="{x0+90}" y="{ay+AXH+24}" fill="{ARM_COL[a]}" '
               f'font-size="13" text-anchor="middle">{a} (mean '
               f'{dist[a]["pooled_mean"]})</text>')
svg.append(f'<text x="{ax}" y="{ay+AXH+46}" fill="{MUT}" font-size="12">'
           f'Wilson 95% CI [.28,.72] both arms &#8212; inconclusive-at-16, '
           f'the gas owns the gate</text>')
svg.append(f'<text x="{ax}" y="{ay+AXH+62}" fill="{MUT}" font-size="12">'
           f'open circles = miss seeds; sets DIFFER (4/8 shared)</text>')
svg.append(f'<text x="{ax}" y="{ay+AXH+78}" fill="{MUT}" font-size="12">'
           f's11/s33 miss only under hybrid = re-roll law at census n</text>')
svg.append(f'<text x="{ax-46}" y="{ay+AXH/2}" fill="{MUT}" font-size="13" '
           f'transform="rotate(-90 {ax-46} {ay+AXH/2})">pooled duty</text>')

# ---------------- panel B: fast-window duty ----------------
bx, by, bw = 600, 140, 420
frame(bx, by, bw, AXH, "B &#183; fast-window (1.4 Hz) duty: wide, dead tail 4/16")
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yline(bx, by, bw, AXH, v, f"{v:.2f}")
yline(bx, by, bw, AXH, .25, "", "#ff8f8f", "6 3")
for j, a in enumerate(ARM_COL):
    x0 = bx + 80 + j * 180
    for i, s in enumerate(SEEDS):
        v = dist[a]["seg1"][i]
        yy = by + AXH * (1 - v)
        dead = v < .1
        svg.append(f'<circle cx="{x0 + i*10:.1f}" cy="{yy:.1f}" r="6" '
                   f'fill="{ARM_COL[a]}" fill-opacity="{0.3 if dead else 1}" '
                   f'stroke="{"#ff8f8f" if dead else ARM_COL[a]}" '
                   f'stroke-width="1.5"/>')
    svg.append(f'<text x="{x0+75}" y="{by+AXH+24}" fill="{ARM_COL[a]}" '
               f'font-size="13" text-anchor="middle">{a}</text>')
svg.append(f'<text x="{bx}" y="{by+AXH+48}" fill="{MUT}" font-size="12">'
           f'P2 FAIL (marginal): &lt;.1 in 4/16 (registered &#8805;5); '
           f'&lt;.25 in 7/16; mean .375/.402</text>')
svg.append(f'<text x="{bx}" y="{by+AXH+66}" fill="{MUT}" font-size="12">'
           f'tracking is FREE everywhere: seg1 err &#8804; .01 on 16/16 both '
           f'arms (P4, lock universal)</text>')

# ---------------- panel C: miss anatomy ----------------
cx, cy, cw = 1100, 140, 420
frame(cx, cy, cw, AXH, "C &#183; failing segments: S_L owns the miss (P3)")
for j, a in enumerate(ARM_COL):
    x0 = cx + 90 + j * 180
    tot = anat[a]["fail_segs"]
    parts = [("S_L&lt;.25", anat[a]["sl_owned"], "#7fd4ff" if a == "hynohop" else "#ffb0d4"),
             ("S_R&lt;.25", anat[a]["sr_owned"], "#9dffb0"),
             ("both&lt;.25", anat[a]["both_below"], "#ff8f8f")]
    ytop = cy + 30
    full = AXH - 70
    yy = ytop
    for lab, v, col in parts:
        hh = full * v / tot
        svg.append(f'<rect x="{x0}" y="{yy:.1f}" width="70" height="{hh:.1f}" '
                   f'fill="{col}" fill-opacity="0.75"/>')
        if hh > 16:
            svg.append(f'<text x="{x0+35}" y="{yy+hh/2+4:.1f}" fill="#1b1d24" '
                       f'font-size="12" text-anchor="middle" '
                       f'font-weight="bold">{v}</text>')
        yy += hh
    svg.append(f'<text x="{x0+35}" y="{ytop-10}" fill="{FG}" font-size="13" '
               f'text-anchor="middle">{a} ({tot} segs)</text>')
    svg.append(f'<text x="{x0+35}" y="{yy+18}" fill="{MUT}" font-size="12" '
               f'text-anchor="middle">SL share {anat[a]["sl_share"]}</text>')
lx = cx + 60
for lab, col in (("S_L&lt;.25 (SR healthy)", "#ffb0d4"), ("S_R&lt;.25", "#9dffb0"),
                 ("both &lt; .25", "#ff8f8f")):
    svg.append(f'<rect x="{lx}" y="{cy+AXH+40}" width="12" height="12" '
               f'fill="{col}"/>')
    svg.append(f'<text x="{lx+16}" y="{cy+AXH+50}" fill="{MUT}" '
               f'font-size="12">{lab}</text>')
    lx += 150
svg.append(f'<text x="{cx}" y="{cy+AXH+86}" fill="{MUT}" font-size="12">'
           f'P5 entry join: seg0 S_L vs pooled rank corr +.612 (hynohop) '
           f'&#8594; +.174 (hybrid)</text>')
svg.append(f'<text x="{cx}" y="{cy+AXH+104}" fill="{MUT}" font-size="12">'
           f'&#8212; hops decorrelate entry state from outcome (re-roll law)</text>')

svg.append("</svg>")
open("l59/ensemble.svg", "w").write("\n".join(svg))
subprocess.run(["rsvg-convert", "-o", "l59/ensemble.png", "l59/ensemble.svg"],
               check=True)
print("wrote l59/ensemble.svg + ensemble.png")
