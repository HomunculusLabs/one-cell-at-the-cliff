"""L56 figure v2: (A) seg2 duty per arm x seed — only the TRANSITION volley
rescues s22 (.147 -> .627); mid-seg2 volleys never do; (B) S-sign LABEL
flips happen ONLY at drive-edge volleys (k=4000 seg boundary, k=4900
chopped re-on): 3/6 edge cells flip, 0/6 mid-window (Fisher p=.091);
(C) mean-neutrality: seg2 duty mean over volley arms .421 vs nohop .438 =
the gas distribution is volley-invariant; misses annotated slow|0+
(SL-marginal). SVG -> rsvg-convert. Numbers from artifacts."""
import json
import subprocess

res = json.load(open("l56/results_l56.json"))
rows, seg2 = res["rows"], res["seg2"]
W, H = 1560, 880
BG, FG, GRID, MUT = "#1b1d24", "#e8e6e3", "#33363f", "#9aa0ae"
SEED_COL = {11: "#7fd4ff", 22: "#ffb37f", 33: "#b39dff"}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="DejaVu Sans, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>',
       f'<text x="40" y="40" fill="{FG}" font-size="24" font-weight="bold">'
       f'L56 seg2 re-roll law: the DISTRIBUTION is volley-invariant, the '
       f'S-STATE flip needs a drive edge</text>',
       f'<text x="40" y="64" fill="{MUT}" font-size="13">volley = DNge046_L '
       f'.5 for 40 steps on the l55 hybrid schedule; k=4000 seg1&#8594;2 '
       f'transition &#183; k=4300 mid on-window &#183; k=4600 mid off-window '
       f'&#183; k=4900 chopped re-on; duty = both S &#8805; .25</text>',
       f'<text x="40" y="82" fill="{MUT}" font-size="13">seeds 11/22/33; '
       f'drive-on 48 s every arm; anchors bit-identical to l55 (0.0, mm + all '
       f'antagonist traces, first_div exact)</text>']

# ---------------- panel A: seg2 duty per arm ----------------
ARMS_A = ["nohop", "hop4k", "v43", "v46", "v49"]
LAB_A = {"nohop": ["no volley"], "hop4k": ["k=4000", "transition"],
         "v43": ["k=4300", "mid (on)"], "v46": ["k=4600", "mid (off)"],
         "v49": ["k=4900", "re-on edge"]}
px, py, pw, ph = 40, 130, 740, 320


def YA(v):
    return py + (ph - 50) * (1 - v)


svg.append(f'<text x="{px}" y="{py-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">A &#183; seg2 duty: only the transition '
           f'volley rescues seed 22</text>')
svg.append(f'<rect x="{px+70}" y="{py}" width="{pw-100}" height="{ph-50}" '
           f'fill="none" stroke="{GRID}"/>')
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    svg.append(f'<line x1="{px+70}" y1="{YA(v):.1f}" x2="{px+pw-30}" '
               f'y2="{YA(v):.1f}" stroke="{GRID}"/>')
    svg.append(f'<text x="{px+64}" y="{YA(v)+4:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="end">{v:.2f}</text>')
svg.append(f'<line x1="{px+70}" y1="{YA(0.25):.1f}" x2="{px+pw-30}" '
           f'y2="{YA(0.25):.1f}" stroke="#ff8f8f" stroke-width="1.5" '
           f'stroke-dasharray="6 3"/>')
svg.append(f'<text x="{px+76}" y="{YA(0.25)-6:.1f}" fill="#ff8f8f" '
           f'font-size="12">miss gate .25</text>')
for i, a in enumerate(ARMS_A):
    x = px + 110 + (pw - 180) * i / (len(ARMS_A) - 1)
    for s, v in zip((11, 22, 33), seg2[a]):
        miss = v < 0.25
        svg.append(f'<circle cx="{x:.1f}" cy="{YA(v):.1f}" r="7" '
                   f'fill="{SEED_COL[s]}" fill-opacity="{0.35 if miss else 1}" '
                   f'stroke="{"#ff8f8f" if miss else SEED_COL[s]}" '
                   f'stroke-width="{"2" if miss else 1}"/>')
    for j, ln in enumerate(LAB_A[a]):
        svg.append(f'<text x="{x:.1f}" y="{py+ph-26+j*15}" fill="{MUT}" '
                   f'font-size="12" text-anchor="middle">{ln}</text>')
svg.append(f'<text x="{px+14}" y="{py+(ph-50)/2}" fill="{MUT}" font-size="13" '
           f'transform="rotate(-90 {px+14} {py+(ph-50)/2})">'
           f'seg2 duty</text>')
svg.append(f'<text x="{px+110}" y="{py+266}" fill="{SEED_COL[22]}" '
           f'font-size="12">s22: no-volley .147 &#8594; transition .627 '
           f'(rescue); mid-seg2 .187/.113/.147 (never)</text>')

# ---------------- panel B: label flips by volley moment ----------------
bx, by, bw, bh = 830, 130, 690, 320
svg.append(f'<text x="{bx}" y="{by-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">B &#183; S-sign state flips: only at drive '
           f'edges</text>')
cells = []
for a in ("hop4k", "v43", "v46", "v49"):
    for s in ("11", "22", "33"):
        c = rows[f"{a}|{s}"]
        if a == "hop4k":
            pre_lab = rows[f"nohop|{s}"]["seg2_label"]
        else:
            pre_lab = c["pre_label"]
        post_lab = c.get("post_label", c["seg2_label"])
        cells.append((a, s, pre_lab, post_lab))
edge_arms = {"hop4k", "v49"}
cw = (bw - 60) / len(cells)
svg.append(f'<rect x="{bx+40}" y="{by}" width="{bw-70}" height="{bh-80}" '
           f'fill="none" stroke="{GRID}"/>')
for i, (a, s, pre, post) in enumerate(cells):
    x = bx + 40 + i * cw + cw / 2
    flipped = pre != post
    edge = a in edge_arms
    col = "#8fd98f" if flipped else ("#5b6270" if edge else "#434854")
    svg.append(f'<rect x="{x-cw*0.30:.1f}" y="{by+34}" width="{cw*0.60:.1f}" '
               f'height="{bh-160}" rx="4" fill="{col}" '
               f'fill-opacity="{0.95 if flipped else 0.55}"/>')
    svg.append(f'<text x="{x:.1f}" y="{by+24}" fill="{SEED_COL[int(s)]}" '
               f'font-size="12" text-anchor="middle">s{s}</text>')
    svg.append(f'<text x="{x:.1f}" y="{by+bh-56}" fill="{MUT}" font-size="11" '
               f'text-anchor="middle">{a}</text>')
    svg.append(f'<text x="{x:.1f}" y="{by+bh-40}" fill="{FG if flipped else MUT}" '
               f'font-size="10" text-anchor="middle">'
               f'{"FLIP" if flipped else "held"}</text>')
    if flipped:
        svg.append(f'<text x="{x:.1f}" y="{by+bh-24}" fill="{FG}" '
                   f'font-size="9" text-anchor="middle">{pre[-2:]}&#8594;'
                   f'{post[-2:]}</text>')
svg.append(f'<text x="{bx+40}" y="{by+bh+8}" fill="{MUT}" font-size="12">'
           f'edge volley (k=4000 / k=4900): 3/6 flip &#183; mid-window '
           f'(k=4300/4600): 0/6</text>')
svg.append(f'<text x="{bx+40}" y="{by+bh+26}" fill="{MUT}" font-size="12">'
           f'Fisher one-sided p=.091, n small; green = S-sign label changed'
           f'</text>')
svg.append(f'<text x="{bx+14}" y="{by+(bh-80)/2}" fill="{MUT}" '
           f'font-size="13" transform="rotate(-90 {bx+14} {by+(bh-80)/2})">'
           f'seg2 state</text>')

# ---------------- panel C: mean-neutrality ----------------
cx, cy, cw2, ch = 40, 510, 1480, 280
svg.append(f'<text x="{cx}" y="{cy-16}" fill="{FG}" font-size="16" '
           f'font-weight="bold">C &#183; mean-neutrality: the duty-level gas '
           f'is volley-invariant; every miss is seed-22 SL-marginal</text>')
means = {"nohop": res["P3"]["nohop"]}
means.update(res["P3"]["volley_means"])
order = ["nohop", "hop4k", "v43", "v46", "v49"]
mx0, mw = cx + 90, 540


def YC(v):
    return cy + 30 + (ch - 120) * (1 - (v - 0.25) / 0.35)


svg.append(f'<line x1="{mx0}" y1="{YC(0.438):.1f}" x2="{mx0+mw}" '
           f'y2="{YC(0.438):.1f}" stroke="#8fd9d9" stroke-dasharray="6 3"/>')
for i, a in enumerate(order):
    x = mx0 + 50 + (mw - 100) * i / (len(order) - 1)
    v = means[a]
    lab = f'{v:.3f} (no-volley mean)' if a == "nohop" else f'{v:.3f}'
    svg.append(f'<line x1="{x:.1f}" y1="{YC(v):.1f}" x2="{x:.1f}" '
               f'y2="{YC(0.25):.1f}" stroke="{MUT}" stroke-width="1" '
               f'stroke-dasharray="2 3"/>')
    svg.append(f'<circle cx="{x:.1f}" cy="{YC(v):.1f}" r="7" fill="#e8c98f"/>')
    svg.append(f'<text x="{x:.1f}" y="{YC(v)-14:.1f}" fill="{"#8fd9d9" if a == "nohop" else FG}" '
               f'font-size="13" text-anchor="middle">{lab}</text>')
    svg.append(f'<text x="{x:.1f}" y="{YC(0.25)+24:.1f}" fill="{MUT}" '
               f'font-size="12" text-anchor="middle">{a}</text>')
svg.append(f'<text x="{cx+14}" y="{cy+30+(ch-120)/2}" fill="{MUT}" '
           f'font-size="13" transform="rotate(-90 {cx+14} {cy+30+(ch-120)/2})">'
           f'seg2 duty mean</text>')
tx = cx + 700
svg.append(f'<text x="{tx}" y="{cy+22}" fill="{FG}" font-size="14" '
           f'font-weight="bold">all 4 misses = seed 22, SL-marginal, SR '
           f'healthy:</text>')
misses = res["P2_misses"]
for j, (k, m) in enumerate(sorted(misses.items())):
    note = "rescued by transition volley" if k == "nohop|22" \
        else "volley never rescues"
    svg.append(f'<text x="{tx}" y="{cy+48+j*20}" fill="{MUT}" font-size="12">'
               f'{k.replace("|", " "):10s} duty {m["duty"]:.3f} &#183; '
               f'SL {m["SL"]:+.3f} SR {m["SR"]:+.3f} &#183; {m["label"]} '
               f'&#183; {note}</text>')
svg.append(f'<text x="{tx}" y="{cy+48+len(misses)*20+18}" fill="{FG}" '
           f'font-size="12">SR .37-.60 everywhere &#8212; the seg2 lottery is '
           f'S_L-owned (L49 marginal side); never bilateral-negative</text>')
svg.append(f'<text x="{cx}" y="{H-34}" fill="{MUT}" font-size="12">'
           f'P1a FAIL (v46 vs hop4k mean diff .203; s22 carries it) &#183; '
           f'P1b 2/9 re-draw cells, both at the re-on edge</text>')
svg.append(f'<text x="{cx}" y="{H-16}" fill="{MUT}" font-size="12">'
           f'P1c chi2 L .6 / R .0 vs no-volley ref (n=12/6, descriptive) '
           f'&#183; P3 PASS (grand .421 vs .438)</text>')
svg.append("</svg>")
open("l56/reroll.svg", "w").write("\n".join(svg))
subprocess.run(["rsvg-convert", "-o", "l56/reroll.png", "l56/reroll.svg"],
               check=True)
print("fig written l56/reroll.png")
