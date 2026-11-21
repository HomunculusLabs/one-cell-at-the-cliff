#!/usr/bin/env python3
"""L184 Fig. 5 — three readouts per arm (the honesty panel), house style
(fig_l152.svg / l152_fig2.py form: dark #282c34 ground, #21252b panel,
one crimson title + grey sub-lines, #3e4451 grid, 5-col accent palette,
r=5 dots, labels in #abb2bf, footer assert line).

Data: banc/l184/threepanel.csv ONLY (arm x chopped / fast=continuous-1.4Hz /
cross-seed columns). Arm identities (gi / cell type / role tags) are read
from banc/l175/results_l175.json — also a stored file, no recomputation.
Every drawn value is asserted against those files before drawing; the
emitted SVG is then re-parsed and every dot position re-derived, so the
figure verifies itself (L152 rule)."""
import csv, json, os, subprocess
import xml.etree.ElementTree as ET

P = os.path.expanduser("~/critters/peabrain-lab")
OUT = f"{P}/paper/figures"

# ---------------- load stored data, assert identities ---------------------
rows = list(csv.DictReader(open(f"{P}/banc/l184/threepanel.csv")))
J = json.load(open(f"{P}/banc/l175/results_l175.json"))
by = {r["arm"]: r for r in [J["base"], *J["window"], *J["twins"].values()]}
A = lambda c, m: (_ for _ in ()).throw(AssertionError(m)) if not c else None
A(len(rows) == 37 and {r["arm"] for r in rows} == set(by), "37 arms, same set as l175")
A(J["base"]["arm"] == "cutwA" and J["base"]["role"] == "k=24 base", "cutwA base")
w = {r["arm"]: r for r in J["window"]}
A(w["sc25"]["gi"] == 1110 and w["sc25"]["cell_type"] == "DNp33" and w["sc25"]["side"] == "left", "sc25 = DNp33-L carrier")
A(w["sc26"]["gi"] == 319, "sc26 = mass twin dm 319")
A(J["twins"]["dmA"]["gi"] == 511 and J["twins"]["dmC"]["gi"] == 1480, "dmA/dmC drive twins")
A(w["sc27"]["gi"] == 707 and w["sc40"]["gi"] == 559, "boundary cells")
for r in rows:  # chopped column cross-check vs l175 stored means
    if "meanR" in by[r["arm"]]:
        A(int(r["chopped_k"]) == int(by[r["arm"]]["kR"]) and abs(float(r["chopped_mean"]) - float(by[r["arm"]]["meanR"])) < 6e-4, f"{r['arm']} vs l175")  # l175 meanR is 3-dp rounded
A(all(r[c] not in ("", None) for r in rows for c in ("chopped_mean", "fast_mean", "cross_mean")), "no missing values")

# ---------------- geometry ----------------
W, H = 1330, 830
X0, X1, VMAX = 140.0, 1150.0, 0.8
SX = lambda v: X0 + v / VMAX * (X1 - X0)
YTOP, DY = 112.0, 17.5
C_CH, C_FA, C_XR = "#98c379", "#61afef", "#e5c07b"   # chopped / fast / cross
HL = {  # arm -> (label, colour, band)
    "sc25": ("sc25 · DNp33-L", "#98c379", "#98c379"),
    "sc26": ("sc26 · DNpe025", "#c678dd", "#c678dd"),
    "dmA": ("dmA · DNge046", "#c678dd", "#c678dd"),
    "dmC": ("dmC · DNpe019", "#c678dd", "#c678dd"),
    "sc27": ("sc27 · DNpe055", "#61afef", "#61afef"),
    "sc40": ("sc40 · DNge084", "#61afef", "#61afef"),
    "cutwA": ("cutwA (base)", "#d19a66", "#d19a66"),
}
s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
s.append(f'<rect width="{W}" height="{H}" fill="#282c34"/>')
s.append(f'<rect x="124" y="64" width="1190" height="750" fill="#21252b" rx="6"/>')
s.append('<text x="30" y="34" fill="#abb2bf" font-size="19" font-weight="bold">Fig. 5 — three readouts per arm: the honesty panel</text>')
s.append('<text x="30" y="56" fill="#5c6370" font-size="13">Right-Ti mean duty, all 37 B39 arms · one row per arm, three readouts per row · rows sorted by chopped-gate duty (high → low)</text>')
s.append('<text x="30" y="76" fill="#5c6370" font-size="13">chopped = 5-s-on/4-s-off gate at 0.7 Hz (16 matched seeds) · fast = continuous 1.4-Hz middle segment · cross = chopped, flex/ext from different seeds (240 ordered pairs, nonindependent)</text>')
# grid + axis numbers
for v in [i / 10 for i in range(9)]:
    x = SX(v)
    s.append(f'<line x1="{x:.1f}" y1="102" x2="{x:.1f}" y2="750" stroke="#3e4451" stroke-width="1"/>')
    s.append(f'<text x="{x:.1f}" y="766" fill="#5c6370" font-size="13" text-anchor="middle">{v:.1f}</text>')
s.append('<text x="645" y="784" fill="#abb2bf" font-size="14" text-anchor="middle">mean duty — fraction of 500-sample windows with r(flex, ext) ≤ −0.25</text>')
# k mini-columns (counts with duty >= .5, straight from the csv)
for hx, htxt in ((1180, "k·chop"), (1216, "k·1.4"), (1262, "k·cross")):
    s.append(f'<text x="{hx}" y="100" fill="#5c6370" font-size="11" text-anchor="middle">{htxt}</text>')

order = sorted(rows, key=lambda r: -float(r["chopped_mean"]))
for i, r in enumerate(order):
    arm = r["arm"]
    y = YTOP + i * DY
    vals = {"ch": float(r["chopped_mean"]), "fa": float(r["fast_mean"]), "xr": float(r["cross_mean"])}
    if arm in HL:
        lab, col, band = HL[arm]
        s.append(f'<rect x="136" y="{y - DY / 2 + 1:.1f}" width="1018" height="{DY - 2:.1f}" fill="{band}" opacity="0.08"/>')
        s.append(f'<text x="122" y="{y + 4:.1f}" fill="{col}" font-size="13" font-weight="bold" text-anchor="end">{lab}</text>')
    else:
        s.append(f'<text x="122" y="{y + 4:.1f}" fill="#abb2bf" font-size="13" text-anchor="end">{arm}</text>')
    xs = [SX(v) for v in vals.values()]
    s.append(f'<line x1="{min(xs):.1f}" y1="{y:.1f}" x2="{max(xs):.1f}" y2="{y:.1f}" stroke="#5c6370" stroke-width="1" opacity="0.55"/>')
    big = 'r="6" stroke="#abb2bf" stroke-width="1"' if arm == "sc25" else 'r="5"'
    for key, col in (("ch", C_CH), ("fa", C_FA), ("xr", C_XR)):
        s.append(f'<circle class="dot {arm} {key}" cx="{SX(vals[key]):.1f}" cy="{y:.1f}" {big} fill="{col}"/>')
    for hx, c in ((1180, "chopped_k"), (1216, "fast_k"), (1262, "cross_k")):
        s.append(f'<text x="{hx}" y="{y + 4:.1f}" fill="#5c6370" font-size="11" text-anchor="middle">{r[c]}</text>')

# annotation, placed only where the bottom rows leave clear space (asserted below)
ann_x, ann_y = 620.0, YTOP + (len(order) - 4) * DY
s.append(f'<text x="{ann_x}" y="{ann_y:.1f}" fill="#e5c07b" font-size="12">dmA / dmC: chopped duty low, cross-seed duty high —</text>')
s.append(f'<text x="{ann_x}" y="{ann_y + 15:.1f}" fill="#e5c07b" font-size="12">shared timing between seeds, not per-run gating (L184 Q3)</text>')
# legend + footer
s.append('<circle cx="36" cy="802" r="6" fill="#98c379"/><text x="48" y="806" fill="#abb2bf" font-size="13">chopped gate 0.7 Hz (matched, 16 seeds)</text>')
s.append('<circle cx="340" cy="802" r="6" fill="#61afef"/><text x="352" y="806" fill="#abb2bf" font-size="13">continuous 1.4 Hz (middle segment)</text>')
s.append('<circle cx="620" cy="802" r="6" fill="#e5c07b"/><text x="632" y="806" fill="#abb2bf" font-size="13">cross-seed, chopped (240 ordered pairs)</text>')
s.append('<text x="1300" y="806" fill="#5c6370" font-size="11.5" text-anchor="end">asserted vs threepanel.csv + results_l175.json at draw time · L184</text>')
s.append('<text x="36" y="822" fill="#5c6370" font-size="11.5">row labels: green = carrier (DNp33-L) · purple = twins (mass sc26, drive dmA/dmC) · blue = boundary cells (sc27, sc40 — sc40 shares leading relay GI 75494) · orange = k=24 base · k columns: runs/pairs with duty ≥ .5 (16 seeds; cross 240) · no values missing</text>')
s.append("</svg>")
svg = "\n".join(s) + "\n"
open(f"{OUT}/fig5_threepanel.svg", "w").write(svg)

# ---------------- self-verification: re-parse the emitted SVG ----------------
t = ET.parse(f"{OUT}/fig5_threepanel.svg"); root = t.getroot()
A(root.get("width") == str(W) and root.get("height") == str(H), "canvas")
dots = [e for e in root.iter("{http://www.w3.org/2000/svg}circle") if e.get("class", "").startswith("dot")]
A(len(dots) == 111, f"111 dots, got {len(dots)}")
seen = {}
for e in dots:
    _, arm, key = e.get("class").split()
    col = {"ch": "chopped", "fa": "fast", "xr": "cross"}[key]
    v = (float(e.get("cx")) - X0) / (X1 - X0) * VMAX  # inverse of SX
    src = float(next(r for r in rows if r["arm"] == arm)[col + "_mean"])
    A(abs(v - src) < 0.5 / (X1 - X0) * VMAX, f"{arm}.{col} roundtrip {v} vs {src}")  # <0.5 px
    seen[arm] = seen.get(arm, 0) + 1
A(all(seen.get(r["arm"]) == 3 for r in rows) and len(seen) == 37, "3 dots per arm, 37 arms")
drawn_order = []
for e in root.iter("{http://www.w3.org/2000/svg}text"):
    if e.get("font-size") == "13" and e.get("text-anchor") == "end":
        drawn_order.append(e.text.split(" ·")[0].split(" (")[0])
exp = [r["arm"] for r in order]
A(drawn_order == exp, f"row order == sorted-by-chopped; got {drawn_order[:5]}…")
chop = [float(r["chopped_mean"]) for r in order]
A(chop == sorted(chop, reverse=True), "sort is monotone desc")
# row-label legibility checks (polish): pitch clears the bumped font, no vertical
# collision between adjacent labels, and labels clear the v=0 dot column
LAB_FS, LAB_X = 13, 122
A(DY >= LAB_FS + 3, f"row pitch {DY} clears label font {LAB_FS}")
ys = [float(e.get("y")) for e in root.iter("{http://www.w3.org/2000/svg}text")
      if e.get("font-size") == str(LAB_FS) and e.get("text-anchor") == "end"]
A(len(ys) == 37 and all(b - a == DY for a, b in zip(ys, ys[1:])), "37 row labels, uniform non-overlapping pitch")
A(all(int(e.get("x")) == LAB_X for e in root.iter("{http://www.w3.org/2000/svg}text")
      if e.get("font-size") == str(LAB_FS) and e.get("text-anchor") == "end"), "labels anchored clear of plot")
A(X0 - 6 - LAB_X >= 8, f"label-to-dot gap {X0 - 6 - LAB_X}px >= 8px")
ktexts = [e.text for e in root.iter("{http://www.w3.org/2000/svg}text") if e.get("font-size") == "11" and float(e.get("y")) > 105]
A(ktexts == [r[c] for r in order for c in ("chopped_k", "fast_k", "cross_k")], "k columns match csv, row-major")
# annotation clearance: no dot right of ann_x - 8 within the annotation's y-band
band = [YTOP + (len(order) - 5) * DY, ann_y + 16]
for e in dots:
    cy = float(e.get("cy"))
    if band[0] <= cy <= band[1]:
        A(float(e.get("cx")) < ann_x - 8, f"annotation clear of {e.get('class')}")
# render + check the png
subprocess.run(["rsvg-convert", "-w", str(W), "-o", f"{OUT}/fig5_threepanel.png", f"{OUT}/fig5_threepanel.svg"], check=True)
dim = subprocess.run(["magick", "identify", "-format", "%w %h", f"{OUT}/fig5_threepanel.png"], capture_output=True, text=True, check=True).stdout
A(dim == f"{W} {H}", f"png dims {dim}")
print("fig5 OK: 37 rows x 3 dots verified against threepanel.csv; order sorted by chopped; k cols match; annotation clear; png", dim)
