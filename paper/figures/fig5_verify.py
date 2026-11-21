#!/usr/bin/env python3
"""Independent verification of fig5_threepanel.svg/.png (run AFTER
fig5_threepanel.py).  Mirrors fig4_verify.py.

Re-parses the emitted SVG and re-derives, from the stored data and an
independently rewritten transform, every dot position, row order, k column,
axis tick and legend entry, and checks every number the caption quotes.
Nothing is taken from the generator's memory: only banc/l184/threepanel.csv,
banc/l175/results_l175.json, paper/numbers.json (the values Table 1 prints),
the caption file and the SVG/PNG bytes on disk.  Fails loudly on any
mismatch.  Added by the L197 repairs (fourth-round referee, M3).
"""
import csv, json, os, re, struct
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.expanduser("~/critters/peabrain-lab")
ROWS = list(csv.DictReader(open(f"{P}/banc/l184/threepanel.csv")))
L175 = json.load(open(f"{P}/banc/l175/results_l175.json"))
NUMS = json.load(open(f"{P}/paper/numbers.json"))
CAP = open(f"{HERE}/fig5_caption.md").read()
NS = "{http://www.w3.org/2000/svg}"

fails, checks, notes = [], 0, []
def A(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)

# --- independent transform (spec: linear mean duty 0..0.8 across x 140..1150)
PX0, PX1, VMAX = 140.0, 1150.0, 0.8
def X(v): return PX0 + v / VMAX * (PX1 - PX0)
COLS = {"chopped": "chopped_mean", "fast": "fast_mean", "cross": "cross_mean"}
KCOL = ("chopped_k", "fast_k", "cross_k")
FILL = {"chopped": "#98c379", "fast": "#61afef", "cross": "#e5c07b"}

# --- the stored table, and its ties to the other stored files
src = {r["arm"]: r for r in ROWS}
A(len(ROWS) == 37 and len(src) == 37, "csv: 37 distinct arms")
by175 = {r["arm"]: r for r in [L175["base"], *L175["window"], *L175["twins"].values()]}
A(set(src) == set(by175), "csv arm set == results_l175.json arm set")
TP = NUMS["l184.threepanel"]["v"]
A(set(src) == set(TP), "csv arm set == numbers.json l184.threepanel (Table 1)")
for a, r in src.items():
    A(all(r[c] not in ("", None) for c in list(COLS.values()) + list(KCOL)), f"{a}: no missing value")
    A(int(r["chopped_k"]) == by175[a]["kR"]
      and abs(float(r["chopped_mean"]) - by175[a]["meanR"]) < 6e-4, f"{a}: chopped column == l175 kR / meanR")
    if a in TP:
        A((int(r["chopped_k"]), int(r["fast_k"]), int(r["cross_k"]))
          == (TP[a]["chopped_k"], TP[a]["fast_k"], TP[a]["cross_k"]), f"{a}: k columns == Table 1 source")
        A(all(abs(float(r[c + "_mean"]) - TP[a][c + "_mean"]) < 6e-4 for c in COLS), f"{a}: means == Table 1 source")

# --- parse the figure
root = ET.parse(f"{HERE}/fig5_threepanel.svg").getroot()
W, H = int(root.get("width")), int(root.get("height"))
A(root.get("viewBox") == f"0 0 {W} {H}", "viewBox == canvas")
A(root.get("data-n-arms") == "37" and root.get("data-source") == "banc/l184/threepanel.csv", "root metadata")

dots = [e for e in root.iter(f"{NS}circle") if e.get("data-arm")]
A(len(dots) == 111, f"111 data dots, got {len(dots)}")
seen, rowy = {}, {}
for e in dots:
    arm, rd = e.get("data-arm"), e.get("data-readout")
    A(arm in src and rd in COLS, f"dot identity {arm}/{rd}")
    if arm not in src or rd not in COLS:
        continue
    v = float(src[arm][COLS[rd]])
    A(float(e.get("data-v")) == v, f"{arm}.{rd}: data-v {e.get('data-v')} != csv {v!r}")
    A(abs(float(e.get("cx")) - X(v)) < 0.6, f"{arm}.{rd}: cx {e.get('cx')} vs {X(v):.1f}")
    A(e.get("fill") == FILL[rd], f"{arm}.{rd}: colour encodes the readout")
    A(e.get("class") == f"dot {arm} {dict(chopped='ch', fast='fa', cross='xr')[rd]}", f"{arm}.{rd}: class agrees with data-*")
    seen.setdefault(arm, set()).add(rd)
    rowy.setdefault(arm, set()).add(float(e.get("cy")))
A(all(seen.get(a) == set(COLS) for a in src), "every arm has exactly one dot per readout")
A(all(len(ys) == 1 for ys in rowy.values()), "the three dots of an arm share one row")
A(0 <= min(float(r[c]) for r in ROWS for c in COLS.values())
  and max(float(r[c]) for r in ROWS for c in COLS.values()) <= VMAX, "every value inside the drawn axis range")

# --- row order, labels, k columns
order = sorted(src, key=lambda a: next(iter(rowy[a])))
exp = [r["arm"] for r in sorted(ROWS, key=lambda r: -float(r["chopped_mean"]))]
A(order == exp, "rows sorted by chopped mean duty, high to low")
ys = [next(iter(rowy[a])) for a in order]
pitch = {round(b - a, 3) for a, b in zip(ys, ys[1:])}
A(len(pitch) == 1 and min(pitch) >= 16, f"uniform row pitch that clears the label font: {pitch}")
labels = sorted(((float(t.get("y")), t.text) for t in root.iter(f"{NS}text")
                 if t.get("text-anchor") == "end" and t.get("x") == "122"), key=lambda t: t[0])
A(len(labels) == 37, f"37 row labels, got {len(labels)}")
for (ly, txt), a, y in zip(labels, order, ys):
    A(abs(ly - 4 - y) < 0.6 and re.split(r" [·(]", txt)[0] == a, f"row label {txt!r} sits on the {a} row")
want_lab = {"sc25": "DNp33-L", "sc26": "DNpe025", "dmA": "DNge046", "dmC": "DNpe019",
            "sc27": "DNpe055", "sc40": "DNge084"}
lab_txt = {re.split(r" [·(]", t)[0]: t for _, t in labels}
for a, ct in want_lab.items():
    A(ct in lab_txt.get(a, "") and by175[a]["cell_type"] == ct.split("-")[0], f"highlight label {a} carries its stored cell type")
A("base" in lab_txt.get("cutwA", "") and L175["base"]["arm"] == "cutwA", "base row labelled")
ktx = [t for t in root.iter(f"{NS}text") if t.get("font-size") == "11" and t.get("text-anchor") == "middle"
       and float(t.get("y")) > 105]
A(len(ktx) == 111, f"111 k cells, got {len(ktx)}")
kx = sorted({float(t.get("x")) for t in ktx})
A(len(kx) == 3, "three k columns")
for a, y in zip(order, ys):
    cells = sorted((float(t.get("x")), t.text) for t in ktx if abs(float(t.get("y")) - 4 - y) < 0.6)
    A([c[1] for c in cells] == [src[a][c] for c in KCOL], f"{a}: k cells == csv (chopped, 1.4 Hz, cross)")

# --- axis ticks land on their gridline; legend names the three readouts
for v in [i / 10 for i in range(9)]:
    tel = [t for t in root.iter(f"{NS}text") if t.text == f"{v:.1f}" and t.get("text-anchor") == "middle"
           and t.get("font-size") == "13"]
    A(len(tel) == 1 and abs(float(tel[0].get("x")) - X(v)) < 0.6, f"x tick {v:.1f}")
    A(any(abs(float(l.get("x1")) - X(v)) < 0.6 and l.get("x1") == l.get("x2") for l in root.iter(f"{NS}line")), f"gridline {v:.1f}")
joined = " | ".join(t.text or "" for t in root.iter(f"{NS}text"))
for need in ["chopped gate 0.7 Hz (matched, 16 seeds)", "continuous 1.4 Hz (middle segment)",
             "cross-seed, chopped (240 ordered pairs)", "all 37 B39 arms", "no values missing",
             "r(flex, ext) \u2264 \u22120.25"]:
    A(need in joined, f"text missing: {need!r}")
leg = {c.get("fill") for c in root.iter(f"{NS}circle") if not c.get("data-arm")}
A(leg == set(FILL.values()), "legend swatches use the three readout colours")
A(L175["design"] is not None and len(L175["seeds"]) == 16, "16 seeds in the scan batch")
A(NUMS["l184.design"]["v"]["n_cross_pairs"] == 240, "240 ordered cross-seed pairs")

# --- the caption: every number it quotes, and every reading it states
f3 = lambda a, c: f"{float(src[a][c]):.3f}"
A("all 37 arms" in CAP and "(of 16)" in CAP and "(of 240)" in CAP, "caption counts")
A(f"({f3('sc25', 'chopped_mean')} / {f3('sc25', 'fast_mean')} / {f3('sc25', 'cross_mean')})" in CAP, "caption: carrier triple")
A(f"dmA {f3('dmA', 'chopped_mean')}, dmC {f3('dmC', 'chopped_mean')}" in CAP, "caption: drive twins, chopped")
A(f"({f3('dmA', 'cross_mean')}, {f3('dmC', 'cross_mean')})" in CAP, "caption: drive twins, cross-seed")
A(f"sc47 {f3('sc47', 'fast_mean')}, sc33 {f3('sc33', 'fast_mean')}" in CAP, "caption: the two quoted 1.4-Hz exceptions")
A(f"cutwA {f3('cutwA', 'chopped_mean')}" in CAP, "caption: base")
A("0\u20130.8 scale" in CAP and "high to low" in CAP, "caption: axis and sort order as drawn")
hi_all = [a for a in src if all(float(src[a][c]) >= 0.5 for c in COLS.values())]
A(hi_all == ["sc25"], f"caption reading: the carrier is the only arm at or above .5 on all three: {hi_all}")
A(all(float(src[a]["chopped_mean"]) < 0.5 and float(src[a]["cross_mean"]) > float(src["cutwA"]["cross_mean"]) + 0.15
      for a in ("dmA", "dmC")), "caption reading: drive twins low chopped, high cross-seed")
A(by175["sc40"]["gi"] == 559 and by175["sc27"]["gi"] == 707, "caption: boundary cells are the stored ranks 27 and 40")
# NOT asserted (reported for the owner): the caption lists two exceptions to
# "collapses toward zero in the 1.4-Hz column".  Count them from the data.
exc = sorted((a for a in src if a != "sc25" and float(src[a]["fast_mean"]) >= 0.05),
             key=lambda a: -float(src[a]["fast_mean"]))
unlisted = [a for a in exc if f"{a} {f3(a, 'fast_mean')}" not in CAP]
if unlisted:
    notes.append("caption gap (not a figure error; captions are frozen by the L197 brief): arms with "
                 "1.4-Hz mean duty >= .05 that the caption's exception list does not name: "
                 + ", ".join(f"{a} {f3(a, 'fast_mean')}" for a in unlisted))

# --- PNG: magic, dimensions == the SVG canvas, non-trivial size
png = open(f"{HERE}/fig5_threepanel.png", "rb").read()
A(png[:8] == b"\x89PNG\r\n\x1a\n", "png magic")
w, h = struct.unpack(">II", png[16:24])
A((w, h) == (W, H), f"png dims {w}x{h} != svg canvas {W}x{H}")
A(len(png) > 50000, f"png size {len(png)}")

print(f"checks run: {checks}")
for n in notes:
    print("NOTE:", n)
if fails:
    print(f"FAILURES ({len(fails)}):")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("FIG5 VERIFY: ALL PASS")
print(f"  37 arms x 3 readouts = 111 dots == threepanel.csv (data-v exact, cx < 0.6 px); rows sorted by "
      f"chopped duty; 111 k cells == csv; csv == results_l175.json and numbers.json l184.threepanel")
print(f"  carrier row: chopped {f3('sc25', 'chopped_mean')} px {X(float(src['sc25']['chopped_mean'])):.1f} | "
      f"1.4 Hz {f3('sc25', 'fast_mean')} px {X(float(src['sc25']['fast_mean'])):.1f} | "
      f"cross {f3('sc25', 'cross_mean')} px {X(float(src['sc25']['cross_mean'])):.1f}; canvas {W}x{H}")
