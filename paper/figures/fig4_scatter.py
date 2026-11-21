#!/usr/bin/env python3
"""Fig. 4 (L175+L185): the 36-arm scatter — one carrier, 35 non-flippers.

House style per paper/fig_l152.svg (One Dark palette, no chartjunk). Every
drawn value is read from the stored results files (no recomputation, no
smoothing) and asserted BEFORE drawing (the L152 "figure is its own
verifier" rule); the base Wilson band is independently recomputed.

Transform (stated in-figure and in fig4_caption.md):
  X = per-cell mean rate x_mean on the k=24 cutwA base, log10 scale with a
      floor at 1e-4 (values <= 1e-4, incl. numerically ~0 negatives, plot at
      the left edge).
  Y = meanR (mean response over the 16 right-side seeds), linear 0.10-0.85.
      (kR/16 is NOT drawn; meanR carries the band thresholds.)

Points: 34 window cells (sc25-sc58) + dmA/dmC twins = 36 L175 arms; carrier
sc25 (DNp33-L, gi 1110) large highlighted marker; four twin families get
distinct shapes (mass gi 319 square, drive dmA/dmC triangles, signed-current
gi 1508 diamond, b40-only); silent cells (x_mean <= 0.05) hollow; fresh-batch
b40 overlays (open markers + dashed ties) for the six L185 key arms.
Base = horizontal Wilson 95% reference band; SUPER threshold = dashed line.

Output: fig4_scatter.svg (+ .png via rsvg-convert, rendered by run.sh call).
"""
import json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.expanduser("~/critters/peabrain-lab")
L175 = json.load(open(f"{P}/banc/l175/results_l175.json"))
L185 = json.load(open(f"{P}/banc/l185/results_l185.json"))

# ---------------- asserts: structure + every headline drawn value ----------
A = lambda cond, msg: (_ for _ in ()).throw(AssertionError(msg)) if not cond else None

def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - hw, ctr + hw

win = L175["window"]
A(len(win) == 34, "34 window cells")
A([e["rank"] for e in win] == list(range(25, 59)), "ranks 25..58")
car = win[0]
A(car["arm"] == "sc25" and car["gi"] == 1110 and car["cell_type"] == "DNp33"
  and car["side"] == "left" and car["kR"] == 16 and car["cls"] == "SUPER",
  "carrier sc25 gi 1110 DNp33 left 16/16 SUPER")
mass = win[1]
A(mass["arm"] == "sc26" and mass["gi"] == 319, "mass twin sc26 gi 319")
tw = L175["twins"]
A(tw["dmA"]["gi"] == 511 and tw["dmA"]["cell_type"] == "DNge046", "dmA 511")
A(tw["dmC"]["gi"] == 1480 and tw["dmC"]["cell_type"] == "DNpe019", "dmC 1480")
for e in win + [tw["dmA"], tw["dmC"]]:
    A(e["active"] == (e["x_mean"] > 0.05), f"active==x>0.05 for {e['arm']}")
base = L175["base"]
A(base["arm"] == "cutwA" and (base["kR"], base["n"]) == (5, 16), "cutwA base 5/16")
lb, ub = wilson(base["kR"], base["n"])
A(abs(lb - base["lbR"]) < 1e-12 and abs(ub - base["ubR"]) < 1e-12, "base Wilson recompute")
B = L175["bands"]
A(B["n"] == 16 and B["super_meanR_min"] == 0.6 and B["super_kR_min"] == 12
  and B["not_meanR_max"] == 0.5 and B["not_kR_max"] == 8, "band thresholds")
hi = [e for e in win if e["arm"] != "sc25" and e["delivered_drive"] > car["delivered_drive"]]
A(len(hi) == 7 and all(e["cls"] != "SUPER" for e in hi) and all(e["active"] for e in hi),
  "7 hi-drive cells, none SUPER, all active")
A(max(e["drive_ratio_to_carrier"] for e in hi) < 4.2
  and min(e["drive_ratio_to_carrier"] for e in hi) > 1.4, "hi-drive ratio 1.5-4.2x")
# L185: six key arms, fresh b40 rematched points; b39_stored must equal L175
KEYS = ["sc25", "sc26", "sc27", "sc40", "dmA", "dmC"]
A(sorted(L185["R1"].keys()) == sorted(KEYS), "L185 R1 six key arms")
by_arm = {e["arm"]: e for e in win}
by_arm.update({"dmA": tw["dmA"], "dmC": tw["dmC"]})
for k in KEYS:
    A(L185["R1"][k]["b39_stored"]["meanR"] == by_arm[k]["meanR"]
      and L185["R1"][k]["gi"] == by_arm[k]["gi"], f"b39 cross-file match {k}")
s2t = L185["R3"]["arm"]
A(s2t["arm"] == "s2t" and s2t["gi"] == 1508 and s2t["cell_type"] == "DNg19"
  and s2t["cls"] == "NOT-SUPER", "signed-current twin s2t gi 1508")
A(L185["base"]["arm"] == "cutwA", "L185 base cutwA")

# ---------------- geometry --------------------------------------------------
W, H = 1260, 700
PX0, PX1, PYT, PYB = 170, 1200, 112, 576
XDOM = (math.log10(1e-4), math.log10(1.6))          # -4 .. 0.2041 (headroom past x=1 for the s2t diamond)
YLO, YHI = 0.10, 0.85
def X(v):  return PX0 + (math.log10(max(v, 1e-4)) - XDOM[0]) / (XDOM[1] - XDOM[0]) * (PX1 - PX0)
def Y(v):  return PYB - (v - YLO) / (YHI - YLO) * (PYB - PYT)

# palette (house, One Dark)
BG, PANEL, GRID = "#282c34", "#21252b", "#3e4451"
TXT, MUT = "#abb2bf", "#5c6370"
BLUE, PURP, YELL, GREEN, ORNG, RED, CYAN, GRAY = ("#61afef", "#c678dd", "#e5c07b",
    "#98c379", "#d19a66", "#e06c75", "#56b6c2", "#7f848e")

S = []
def el(s): S.append(s)
def txt(x, y, s, size=12, fill=TXT, anchor="start", bold=False, opacity=None, rotate=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    b = ' font-weight="bold"' if bold else ""
    o = f' opacity="{opacity}"' if opacity else ""
    r = f' transform="rotate({rotate[0]} {rotate[1]} {rotate[2]})"' if rotate else ""
    el(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}"{a}{b}{o}{r}>{s}</text>')

el(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" id="fig4-root" '
   f'data-n-arms="36" data-y="meanR" data-x="x_mean log10 floor 1e-4">')
el(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
el(f'<rect x="124" y="92" width="1117" height="522" fill="{PANEL}" rx="6"/>')
txt(30, 34, "Fig. 4 — the 36-arm scan: one carrier, 35 non-flippers", 19, TXT, bold=True)
txt(30, 56, "per-cell mean rate x&#772; on the k=24 cutwA base (log10 scale, floor 10&#8315;&#8308;) vs mean response "
            "meanR, 16 seeds · 34 window cells (sc25–sc58) + dmA/dmC twins", 12, MUT)
txt(30, 74, "hollow = silent · base band = 95% CI for kR/16, not meanR · green = SUPER "
            "(meanR ≥ 0.60 and kR ≥ 12) · open markers + dashed ties = fresh batch b40 (L185)", 12, MUT)

# grid + axes
nflo = sum(1 for e in win if e["x_mean"] <= 1e-4)   # floor-pinned silent cells (left-edge stack)
for t in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    el(f'<line x1="{PX0}" y1="{Y(t):.1f}" x2="{PX1}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="1"/>')
    txt(PX0 - 12, Y(t) + 4, f"{t:.1f}", 12, MUT, anchor="end")
for t, lab in [(1e-4, "10&#8315;&#8308;"), (1e-3, "10&#8315;&#179;"), (1e-2, "10&#8315;&#178;"),
               (1e-1, "10&#8315;&#185;"), (1.0, "1")]:
    el(f'<line x1="{X(t):.1f}" y1="{PYT}" x2="{X(t):.1f}" y2="{PYB}" stroke="{GRID}" stroke-width="1" opacity="0.6"/>')
    txt(X(t), PYB + 20, lab, 12, MUT, anchor="middle")
txt(X(1e-4), PYB + 34, f"(floor · {nflo} pinned)", 9.5, MUT, anchor="middle")
txt(34, 344, "mean response meanR (16 seeds)", 13, TXT, anchor="middle", rotate=(-90, 34, 344))
txt((PX0 + PX1) / 2, 626, "per-cell mean rate x&#772; on the k=24 cutwA base (log10 scale, floor 10&#8315;&#8308; — "
    "values ≤ 10&#8315;&#8308; plot at the left edge)", 13, TXT, anchor="middle")

# base reference band (Wilson 95% on cutwA b39) + fresh-b40 base line
yb0, yb1 = Y(base["ubR"]), Y(base["lbR"])
el(f'<rect id="base-band" data-lo="{base["lbR"]}" data-hi="{base["ubR"]}" x="{PX0}" y="{yb0:.1f}" '
   f'width="{PX1 - PX0}" height="{yb1 - yb0:.1f}" fill="{TXT}" opacity="0.06"/>')
el(f'<line id="base-line" data-v="{base["meanR"]}" x1="{PX0}" y1="{Y(base["meanR"]):.1f}" x2="{PX1}" '
   f'y2="{Y(base["meanR"]):.1f}" stroke="{TXT}" stroke-width="1.2" opacity="0.55"/>')
txt(PX1 - 8, Y(base["meanR"]) - 6, f"cutwA base b39 · {base['kR']}/{base['n']} · meanR {base['meanR']:.3f} (Wilson 95% band)",
    11, TXT, anchor="end", opacity=0.85)
el(f'<line id="base-b40" data-v="{L185["base"]["meanR"]}" x1="{PX0}" y1="{Y(L185['base']['meanR']):.1f}" '
   f'x2="{PX1}" y2="{Y(L185['base']['meanR']):.1f}" stroke="{TXT}" stroke-width="1.2" opacity="0.4" stroke-dasharray="5 5"/>')
txt(PX0 + 12, Y(L185["base"]["meanR"]) + 14, f"base fresh b40 · {L185['base']['kR']}/16 · meanR {L185['base']['meanR']:.3f}",
    11, MUT, anchor="start")

# SUPER threshold
el(f'<line id="super-threshold" data-v="0.6" x1="{PX0}" y1="{Y(0.6):.1f}" x2="{PX1}" y2="{Y(0.6):.1f}" '
   f'stroke="{GREEN}" stroke-width="1.8" stroke-dasharray="8 5"/>')
txt(PX1 - 8, Y(0.6) - 6, "SUPER threshold: meanR ≥ 0.60 (and kR ≥ 12)", 11.5, GREEN, anchor="end")

# fresh-b40 ties (under the markers)
FRESH = {k: L185["R1"][k]["rematched"]["meanR"] for k in KEYS}
for k in KEYS:
    e = by_arm[k]
    el(f'<line class="tie-b40" data-arm="{k}" x1="{X(e["x_mean"]):.1f}" y1="{Y(e["meanR"]):.1f}" '
       f'x2="{X(e["x_mean"]):.1f}" y2="{Y(FRESH[k]):.1f}" stroke="{MUT}" stroke-width="1" stroke-dasharray="2 3"/>')

def dot(e, batch, role, r=4):
    x, y = X(e["x_mean"]), Y(e["meanR"])
    if e["active"]:
        el(f'<circle class="pt" data-arm="{e["arm"]}" data-batch="{batch}" data-role="{role}" '
           f'cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BLUE}" opacity="0.85"/>')
    else:
        el(f'<circle class="pt" data-arm="{e["arm"]}" data-batch="{batch}" data-role="{role}" '
           f'cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{GRAY}" stroke-width="1.4"/>')

def square(x, y, arm, batch, role, s=5.5, hollow=None, color=YELL, sw=2.0):
    h = "none" if hollow else color
    st = f' stroke="{color}" stroke-width="{sw}"' if hollow else ""
    el(f'<rect class="pt" data-arm="{arm}" data-batch="{batch}" data-role="{role}" data-shape="square" '
       f'data-r="{s}" x="{x - s:.1f}" y="{y - s:.1f}" width="{2 * s}" height="{2 * s}" fill="{h}"{st}/>')

def tri(x, y, arm, batch, role, up=True, r=8, w=7.6, color=GREEN, fill=None, sw=2.0):
    dy1, dy2 = (-r, r * 0.75) if up else (r, -r * 0.75)
    pts = f"{x:.1f},{y + dy1:.1f} {x - w:.1f},{y + dy2:.1f} {x + w:.1f},{y + dy2:.1f}"
    f_ = fill or ("none" if fill is None else fill)
    st = f' stroke="{color}" stroke-width="{sw}"' if fill in (None, "none") else ""
    el(f'<polygon class="pt" data-arm="{arm}" data-batch="{batch}" data-role="{role}" '
       f'data-shape="{'tri-up' if up else 'tri-down'}" data-r="{r}" data-w="{w}" points="{pts}" fill="{f_}"{st}/>')

def diamond(x, y, arm, batch, role, r=8.5, w=7, color=CYAN, fill=CYAN):
    pts = f"{x:.1f},{y - r:.1f} {x - w:.1f},{y:.1f} {x:.1f},{y + r:.1f} {x + w:.1f},{y:.1f}"
    el(f'<polygon class="pt" data-arm="{arm}" data-batch="{batch}" data-role="{role}" data-shape="diamond" '
       f'data-r="{r}" data-w="{w}" points="{pts}" fill="{fill}"/>')

# window cells (plain dots; carrier + mass twin drawn separately below)
for e in win:
    if e["arm"] in ("sc25", "sc26"):
        continue
    dot(e, "b39", "window")

# twins (b39)
square(X(mass["x_mean"]), Y(mass["meanR"]), "sc26", "b39", "twin-mass", hollow=not mass["active"])
txt(X(mass["x_mean"]), Y(mass["meanR"]) + 36, "mass twin · DNpe025 gi 319", 10, YELL, anchor="middle")
tri(X(tw["dmA"]["x_mean"]), Y(tw["dmA"]["meanR"]), "dmA", "b39", "twin-drive", up=True)
txt(X(tw["dmA"]["x_mean"]) - 14, Y(tw["dmA"]["meanR"]) + 4, "dmA · 511", 10, GREEN, anchor="end")
tri(X(tw["dmC"]["x_mean"]), Y(tw["dmC"]["meanR"]), "dmC", "b39", "twin-drive", up=False)
txt(X(tw["dmC"]["x_mean"]) - 14, Y(tw["dmC"]["meanR"]) - 8, "dmC · 1480", 10, GREEN, anchor="end")

# floor-pinned silent stack note (left edge): nflo cells pinned at the 1e-4 floor
txt(180, 320, "floor-pinned: rate &#8804; 10&#8315;&#8308;", 9.5, MUT, anchor="start", opacity=0.9)

# carrier (the paper's face)
cx, cy = X(car["x_mean"]), Y(car["meanR"])
el(f'<circle class="pt" data-arm="sc25" data-batch="b39" data-role="carrier" cx="{cx:.1f}" cy="{cy:.1f}" '
   f'r="16" fill="none" stroke="{RED}" stroke-width="1.6"/>')
el(f'<circle class="pt" data-arm="sc25" data-batch="b39" data-role="carrier" cx="{cx:.1f}" cy="{cy:.1f}" '
   f'r="10" fill="{RED}"/>')
txt(cx - 26, cy - 8, "DNp33-L · gi 1110 — the carrier", 12.5, RED, anchor="end", bold=True)
txt(cx - 26, cy + 8, f"x&#772; {car['x_mean']:.3f} · drive {car['delivered_drive']:.1f} · 16/16 SUPER", 10.5, MUT, anchor="end")

# signed-current twin (L185 b40 only)
dx, dy = X(s2t["x_mean"]), Y(s2t["meanR"])
diamond(dx, dy, "s2t", "b40", "twin-s2t")
el(f'<line x1="{dx - 4:.1f}" y1="{dy + 10:.1f}" x2="{dx - 14:.1f}" y2="{dy + 36:.1f}" stroke="{CYAN}" stroke-width="1" opacity="0.6"/>')
txt(dx - 16, dy + 48, f"s2t · DNg19 gi 1508 (b40 only · drive {L185['R3']['selection']['pick']['drive_ratio']:.2f}×)",
    10, CYAN, anchor="end")

# fresh-b40 overlays for the six key arms
ov = {"sc25": (RED, "circle"), "sc26": (YELL, "square"), "sc27": (BLUE, "circle"),
      "sc40": (BLUE, "circle"), "dmA": (GREEN, "tri-up"), "dmC": (GREEN, "tri-down")}
for k in KEYS:
    e = by_arm[k]
    x, y = X(e["x_mean"]), Y(FRESH[k])
    col, shape = ov[k]
    if shape == "circle":
        el(f'<circle class="pt ov-b40" data-arm="{k}" data-batch="b40" data-role="overlay" cx="{x:.1f}" '
           f'cy="{y:.1f}" r="4.5" fill="none" stroke="{col}" stroke-width="1.7"/>')
    elif shape == "square":
        square(x, y, k, "b40", "overlay", s=4, hollow=True, color=col, sw=1.7)
    elif shape == "tri-up":
        tri(x, y, k, "b40", "overlay", up=True, r=5.5, w=5.2, color=col, fill="none", sw=1.7)
    else:
        tri(x, y, k, "b40", "overlay", up=False, r=5.5, w=5.2, color=col, fill="none", sw=1.7)

# annotation: the honesty arrow at the high-drive cluster
txt(880, 205, "7 cells with drive &gt; carrier: none flip", 12.5, TXT, anchor="middle", bold=True)
txt(880, 221, "delivered drive 1.5–4.2× carrier · 0 of 7 SUPER", 10.5, MUT, anchor="middle")
el(f'<path d="M 873 232 C 953 260, 1023 310, 1076 362" fill="none" stroke="{TXT}" stroke-width="1.4" '
   f'stroke-dasharray="3 4" marker-end="url(#arr)"/>')

# legend
LY = 648
el(f'<circle cx="40" cy="{LY}" r="5.5" fill="{BLUE}" opacity="0.85"/>'); txt(54, LY + 4, "window cell, active", 11.5)
el(f'<circle cx="205" cy="{LY}" r="5.5" fill="none" stroke="{GRAY}" stroke-width="1.4"/>'); txt(219, LY + 4, "silent cell (x&#772; ≤ 0.05)", 11.5)
el(f'<circle cx="392" cy="{LY}" r="7" fill="{RED}"/>'); txt(406, LY + 4, "carrier DNp33-L (16/16)", 11.5)
square(578, LY, None, "legend", "legend", s=5, hollow=True); txt(596, LY + 4, "mass twin gi 319", 11.5)
tri(733, LY, None, "legend", "legend", up=True, r=6, w=5.6); tri(748, LY, None, "legend", "legend", up=False, r=6, w=5.6)
txt(760, LY + 4, "drive twins dmA/dmC", 11.5)
diamond(918, LY, None, "legend", "legend", r=6.5, w=5.4); txt(932, LY + 4, "signed-current gi 1508", 11.5)
el(f'<line x1="1088" y1="{LY - 7}" x2="1088" y2="{LY + 7}" stroke="{MUT}" stroke-width="1" stroke-dasharray="2 3"/>')
el(f'<circle cx="1088" cy="{LY}" r="4.5" fill="none" stroke="{BLUE}" stroke-width="1.7"/>')
txt(1100, LY + 4, "fresh b40 (L185)", 11.5)
txt(1230, 690, "asserted vs stored results_l175.json + results_l185.json at draw time · Wilson band recomputed (dev &lt; 1e-12) · png: rsvg-convert",
    10.5, MUT, anchor="end")
el('<defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">'
   f'<path d="M0,0 L9,4.5 L0,9 z" fill="{TXT}"/></marker></defs>')
el("</svg>")

SVG = "\n".join(S) + "\n"

def build(write=True, render_png=True):
    if write:
        open(f"{HERE}/fig4_scatter.svg", "w").write(SVG)
    if write and render_png:
        subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                        "-o", f"{HERE}/fig4_scatter.png", f"{HERE}/fig4_scatter.svg"], check=True)
    return SVG

if __name__ == "__main__":
    build()
    n_pt = SVG.count('class="pt"')
    n_b39 = SVG.count('data-batch="b39"')
    n_b40 = SVG.count('data-batch="b40"')
    print(f"fig4_scatter.svg written; {n_pt} pt markers total, {n_b39} b39 (want 37: 36 arms + base-band n/a), {n_b40} b40 (want 7: 6 overlays + s2t)")
    print("png rendered with rsvg-convert")
