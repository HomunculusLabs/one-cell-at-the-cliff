#!/usr/bin/env python3
"""Independent verification of fig4_scatter.svg/.png (run AFTER fig4_scatter.py).

Re-parses the emitted SVG and re-derives, from the stored results files and
an independently rewritten transform, every marker position, reference line,
band edge, tick and annotation. Fails loudly on any mismatch. No values are
taken from the generator's memory: only from results_l175.json,
results_l185.json and the SVG/PNG bytes on disk.
"""
import json, math, os, struct, hashlib
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.expanduser("~/critters/peabrain-lab")
L175 = json.load(open(f"{P}/banc/l175/results_l175.json"))
L185 = json.load(open(f"{P}/banc/l185/results_l185.json"))
NS = "{http://www.w3.org/2000/svg}"

fails, checks = [], 0
def A(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)

# --- independent transform (spec: x log10 floor 1e-4 -> -4..log10(1.6); y .10-.85)
PX0, PX1, PYT, PYB = 170.0, 1200.0, 112.0, 576.0
def X(v): return PX0 + (math.log10(max(v, 1e-4)) + 4.0) / (4.0 + math.log10(1.6)) * (PX1 - PX0)
def Y(v): return PYB - (v - 0.10) / 0.75 * (PYB - PYT)

root = ET.parse(f"{HERE}/fig4_scatter.svg").getroot()
A(root.get("width") == "1260" and root.get("height") == "700", "canvas 1260x700")
A(root.get("data-n-arms") == "36" and root.get("data-y") == "meanR", "root metadata")

# --- rebuild the expected marker table from the stored files
win = L175["window"]
by_arm = {e["arm"]: e for e in win}
by_arm.update({"dmA": L175["twins"]["dmA"], "dmC": L175["twins"]["dmC"]})
exp = []  # (arm, batch, role, xpx, ypx)
for e in win:
    if e["arm"] == "sc25":
        exp.append(("sc25", "b39", "carrier", X(e["x_mean"]), Y(e["meanR"])))  # ring + main share center
        exp.append(("sc25", "b39", "carrier", X(e["x_mean"]), Y(e["meanR"])))
    elif e["arm"] == "sc26":
        exp.append(("sc26", "b39", "twin-mass", X(e["x_mean"]), Y(e["meanR"])))
    else:
        exp.append((e["arm"], "b39", "window", X(e["x_mean"]), Y(e["meanR"])))
for a in ("dmA", "dmC"):
    e = by_arm[a]
    exp.append((a, "b39", "twin-drive", X(e["x_mean"]), Y(e["meanR"])))
KEYS = ["sc25", "sc26", "sc27", "sc40", "dmA", "dmC"]
for k in KEYS:
    exp.append((k, "b40", "overlay", X(by_arm[k]["x_mean"]), Y(L185["R1"][k]["rematched"]["meanR"])))
s2t = L185["R3"]["arm"]
exp.append(("s2t", "b40", "twin-s2t", X(s2t["x_mean"]), Y(s2t["meanR"])))

# --- collect drawn markers (exclude legend shapes)
def verts_for(shape, r, w, cx, cy):
    if shape == "tri-up":
        return [(cx, cy - r), (cx - w, cy + 0.75 * r), (cx + w, cy + 0.75 * r)]
    if shape == "tri-down":
        return [(cx, cy + r), (cx - w, cy - 0.75 * r), (cx + w, cy - 0.75 * r)]
    if shape == "diamond":
        return [(cx, cy - r), (cx - w, cy), (cx, cy + r), (cx + w, cy)]
    return None  # square handled via rect x/y/size

got = []
for el in root.iter():
    cls = el.get("class") or ""
    if not cls.startswith("pt") or el.get("data-role") == "legend":
        continue
    arm, batch, role = el.get("data-arm"), el.get("data-batch"), el.get("data-role")
    tag = el.tag.replace(NS, "")
    if tag == "circle":
        got.append((arm, batch, role, [(float(el.get("cx")), float(el.get("cy")))]))
    elif tag == "rect":
        x0, y0 = float(el.get("x")), float(el.get("y"))
        wd = float(el.get("width"))
        got.append((arm, batch, role, [(x0 + wd / 2, y0 + wd / 2)]))
    elif tag == "polygon":
        pts = [tuple(map(float, p.split(","))) for p in el.get("points").split()]
        got.append((arm, batch, role, pts))
A(len(exp) == 44, f"expected table size 44, got {len(exp)}")
A(len(got) == len(exp), f"marker count: drew {len(got)}, expected {len(exp)}")

def key(t):
    return (t[0], t[1], t[2])

for (ea, eb, er, ex, ey), (ga, gb, gr, gv) in zip(sorted(exp, key=lambda t: (t[0], t[1], t[2], t[3], t[4])),
                                                  sorted(got, key=lambda t: (t[0], t[1], t[2]))):
    A((ea, eb, er) == (ga, gb, gr), f"marker identity {ea}/{eb}/{er} vs {ga}/{gb}/{gr}")
    shape_v = None
    for el in root.iter():
        c2 = el.get("class") or ""
        if c2.startswith("pt") and el.get("data-arm") == ga and el.get("data-batch") == gb \
           and el.get("data-role") == gr and el.get("data-shape"):
            shape_v = verts_for(el.get("data-shape"), float(el.get("data-r")),
                                float(el.get("data-w", 0)), ex, ey)
            break
    want = shape_v if shape_v else [(ex, ey)]
    A(len(want) == len(gv), f"vertex count {ea}/{eb}/{er}")
    for (wx, wy), (gx, gy) in zip(sorted(want), sorted(gv)):
        A(abs(wx - gx) < 0.6 and abs(wy - gy) < 0.6, f"px mismatch {ea}/{eb}: exp ({wx:.1f},{wy:.1f}) got ({gx:.1f},{gy:.1f})")
A(len({g[0] for g in got if g[1] == 'b39'}) == 36, "36 distinct b39 arms")
A(sum(1 for g in got if g[2] == "carrier") == 2, "carrier ring + main")

# --- reference lines / band / ticks, straight from stored values
def line_y(lid, want, label):
    el = root.find(f".//*[@id='{lid}']")
    A(el is not None, f"{lid} present")
    if el is not None:
        A(abs(float(el.get("y1")) - Y(want)) < 0.6 and abs(float(el.get("y2")) - Y(want)) < 0.6, label)
line_y("super-threshold", L175["bands"]["super_meanR_min"], "SUPER threshold at stored super_meanR_min")
line_y("base-line", L175["base"]["meanR"], "base line at stored cutwA meanR")
line_y("base-b40", L185["base"]["meanR"], "fresh-b40 base line at stored meanR")
band = root.find(".//*[@id='base-band']")
A(band is not None, "base band present")
if band is not None:
    A(abs(float(band.get("y")) - Y(L175["base"]["ubR"])) < 0.6, "band top = Wilson ubR")
    A(abs(float(band.get("height")) - (Y(L175["base"]["lbR"]) - Y(L175["base"]["ubR"]))) < 0.6, "band height = lbR..ubR")

# ties connect b39 meanR to b40 rematched meanR at the arm's x
ties = [t for t in root.iter() if t.get("class") == "tie-b40"]
A(len(ties) == 6, "six b40 ties")
for t in ties:
    a = t.get("data-arm"); e = by_arm[a]
    A(abs(float(t.get("x1")) - X(e["x_mean"])) < 0.6 and abs(float(t.get("x2")) - X(e["x_mean"])) < 0.6, f"tie x {a}")
    A(abs(float(t.get("y1")) - Y(e["meanR"])) < 0.6, f"tie y1 {a}")
    A(abs(float(t.get("y2")) - Y(L185["R1"][a]["rematched"]["meanR"])) < 0.6, f"tie y2 {a}")

# --- text content: annotation, legend, axis labels, escapes
texts = [t.text or "" for t in root.iter(f"{NS}text")]
joined = " | ".join(texts)
A(any(t.strip() == "7 cells with drive > carrier: none flip" for t in texts), "annotation verbatim")
for need in ["window cell, active", "silent cell (x\u0304 ≤ 0.05", "carrier DNp33-L (16/16)",
             "mass twin gi 319", "drive twins dmA/dmC", "signed-current gi 1508", "fresh b40 (L185)",
             "DNp33-L · gi 1110 — the carrier", "SUPER threshold: meanR ≥ 0.60",
             "cutwA base b39 · 5/16 · meanR 0.408", "base fresh b40 · 3/16 · meanR 0.370",
             "s2t · DNg19 gi 1508", "log10 scale, floor 10\u207b\u2074", "mean response meanR (16 seeds)"]:
    A(need in joined, f"text missing: {need!r}")
A("delivered drive 1.5–4.2× carrier · 0 of 7 SUPER" in joined, "annotation sub-line")

# y tick labels land on their gridline
tick = {t.text: t for t in root.iter(f"{NS}text") if t.text in ("0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8")}
for lab, tel in tick.items():
    A(abs(float(tel.get("y")) - 4 - Y(float(lab))) < 0.6, f"y tick {lab} position")
# x ticks: 1e-4..1 at their log positions
for lab, v in [("10\u207b\u2074", 1e-4), ("10\u207b\u00b3", 1e-3), ("10\u207b\u00b2", 1e-2), ("10\u207b\u00b9", 1e-1), ("1", 1.0)]:
    tel = [t for t in root.iter(f"{NS}text") if t.text == lab]
    A(len(tel) >= 1 and abs(float(tel[0].get("x")) - X(v)) < 0.6, f"x tick {lab}")

# --- value-level truths restated (drawn encodings must be backed by data)
car = by_arm["sc25"]
A(car["kR"] == 16 and car["cls"] == "SUPER", "carrier SUPER 16/16")
hi = [e for e in win if e["arm"] != "sc25" and e["delivered_drive"] > car["delivered_drive"]]
A(len(hi) == 7 and all(e["cls"] != "SUPER" for e in hi), "7 hi-drive, none SUPER")
for e in win + [by_arm["dmA"], by_arm["dmC"]]:
    hollow = e["x_mean"] <= 0.05
    # find the drawn marker and check fill matches active/silent encoding
    for el in root.iter():
        if el.get("class") == "pt" and el.get("data-arm") == e["arm"] and el.get("data-batch") == "b39":
            fill = el.get("fill")
            A((fill in (None, "none")) == hollow or e["arm"] in ("sc25", "sc26", "dmA", "dmC"),
               f"hollow encoding {e['arm']}")
            break

# --- PNG: magic, dimensions, non-trivial size
png = open(f"{HERE}/fig4_scatter.png", "rb").read()
A(png[:8] == b"\x89PNG\r\n\x1a\n", "png magic")
w, h = struct.unpack(">II", png[16:24])
A((w, h) == (1260, 700), f"png dims {w}x{h}")
A(len(png) > 50000, f"png size {len(png)}")

print(f"checks run: {checks}")
if fails:
    print(f"FAILURES ({len(fails)}):")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("FIG4 VERIFY: ALL PASS")
print(f"  markers: 36 b39 arms (carrier double-marked), 6 b40 overlays, 1 s2t")
print(f"  carrier px=({X(by_arm['sc25']['x_mean']):.1f},{Y(by_arm['sc25']['meanR']):.1f}) "
      f"threshold px y={Y(0.6):.1f} band px y={Y(L175['base']['ubR']):.1f}..{Y(L175['base']['lbR']):.1f}")
