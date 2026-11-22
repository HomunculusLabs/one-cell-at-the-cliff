#!/usr/bin/env python3
"""Independent verification of fig6_circuit.svg/.png + fig6_caption.md
(run AFTER fig6_circuit.py; mirrors fig4_verify.py).

Nothing is taken from the generator's memory or code: this file re-implements
the pointer resolver, the number formatter and every axis transform, then
re-derives each plotted value and position from the stored artifacts:
  banc/l184/edges.csv, banc/l190/results_l190.json, banc/l198/static.json,
  banc/l200/{a4_wiring,selection,results_l200}.json, banc/l199/results_primary.json
Checks: (1) every data-src pointer resolves to exactly its data-v;
(2) every printed number equals its pointer's value under the stated format;
(3) no printed number in the figure is unsourced (allowlisted protocol
constants and ticks only); (4) bar / seed / diamond / threshold / octant /
theta / phase-arrow geometry from independent transforms; (5) inventory and
data truths (k = #seeds with duty >= .5, arm removal sets, class labels vs
bands); (6) caption: every number pointer resolves and appears, and the
caption prose carries no unsourced decimal; (7) layout: no text-text overlap,
text inside its panel, no edge line through text; (8) PNG magic, size, ink in
every panel; (9) L202 status consistent with the artifact tree; (10) earlier
figure files byte-pinned (untouched by this dispatch).
"""
import csv, hashlib, json, math, os, re, struct
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.expanduser("~/critters/peabrain-lab")
NS = "{http://www.w3.org/2000/svg}"
SRC = {
    "l190r": json.load(open(f"{P}/banc/l190/results_l190.json")),
    "l198s": json.load(open(f"{P}/banc/l198/static.json")),
    "l200a4": json.load(open(f"{P}/banc/l200/a4_wiring.json")),
    "l200s": json.load(open(f"{P}/banc/l200/selection.json")),
    "l200r": json.load(open(f"{P}/banc/l200/results_l200.json")),
    "l199p": json.load(open(f"{P}/banc/l199/results_primary.json")),
}
with open(f"{P}/banc/l184/edges.csv") as fh:
    EDGES = list(csv.DictReader(fh))

fails, checks = [], 0


def A(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def get(ptr):
    m = re.fullmatch(r"(ratio|sub)\((.+);(.+)\)", ptr)
    if m:
        a, b = get(m.group(2)), get(m.group(3))
        return a / b if m.group(1) == "ratio" else a - b
    if ptr.startswith("l184e?"):
        query, what = ptr[len("l184e?"):].split("#")
        sel = EDGES
        for cond in query.split("&"):
            k, v = cond.split("=", 1)
            sel = [r for r in sel if r[k] == v]
        if what == "count":
            return len(sel)
        if len(sel) != 1:
            raise KeyError(f"{ptr}: {len(sel)} rows")
        return int(sel[0][what])
    head, *keys = ptr.split("/")
    node = SRC[head]
    for k in keys:
        node = node[int(k)] if isinstance(node, list) else node[k]
    return node


def show(v, f):
    if f == "d":
        out = str(int(v))
    elif f == "comma":
        out = format(int(v), ",")
    elif f == "pct":
        out = "%d%%" % round(v * 100)
    elif f[0] == "s":
        out = ("%+." + f[1:] + "f") % v
    elif f[0] == "f":
        out = ("%." + f[1:] + "f") % v
    else:
        raise ValueError(f)
    return out.replace("-", "\u2212")


def same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


root = ET.parse(f"{HERE}/fig6_circuit.svg").getroot()
A(root.get("width") == "1400" and root.get("height") == "1012", "canvas 1400x1012")

# ---------------- (9) L202 status ----------------
l202_landed = os.path.exists(f"{P}/banc/l202/results_l202.json")
A(root.get("data-l202") == ("landed" if l202_landed else "pending"), "L202 flag matches artifact tree (regenerate Panel B if it landed)")
A(root.find(".//*[@id='l202-slot']") is not None, "L202 slot drawn")

# ---------------- (1)+(2) every pointer-bearing element ----------------
n_ptr = 0
sourced_text = set()
for el in root.iter():
    ds = el.get("data-src")
    if ds is None:
        continue
    ptrs = ds.split("|")
    vals = el.get("data-v").split("|")
    A(len(ptrs) == len(vals), f"{ds}: pointer/value count")
    resolved = []
    for p_, v_ in zip(ptrs, vals):
        try:
            r = get(p_)
        except Exception as e:  # noqa
            A(False, f"pointer does not resolve: {p_} ({e})")
            continue
        n_ptr += 1
        A(same(r, eval(v_, {"nan": float("nan"), "NaN": float("nan")})), f"data-v mismatch {p_}: svg {v_} vs stored {r!r}")
        resolved.append(r)
    if el.tag == NS + "text":
        sourced_text.add(id(el))
        txt = "".join(el.itertext())
        pos = 0
        for r, f in zip(resolved, el.get("data-fmt").split("|")):
            want = show(r, f)
            i = txt.find(want, pos)
            A(i >= 0, f"printed value {want!r} ({ds}) not in text {txt!r}")
            pos = i + len(want) if i >= 0 else pos

# ---------------- (3) unsourced numbers in figure text ----------------
ALLOW = {"6", "0.7", "1.4", "24", "44", "96", "150", "500", "360", "0", "1",
         "0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.8", "1.0", "90", "180", "270", "−90", "16"}
# 6 = 'Fig. 6'; 0.7/1.4 Hz = protocol; k=24 base; B44 batch; 96/150/500 = L199 S design
# (also asserted below); 0/90/180/270/360/−90 = angle ticks; 0.0-1.0 = duty ticks;
# 16 = seeds per arm (asserted == l200 bands n); 1 = '(1 = ring)'.
NUM = re.compile(r"(?<![A-Za-z_\d.])[−+]?\d[\d,]*(?:\.\d+)?")
for el in root.iter(NS + "text"):
    txt = "".join(el.itertext())
    if el.get("data-src"):
        # strip the sourced values, then whatever is left must be allowlisted
        for p_, f in zip(el.get("data-src").split("|"), el.get("data-fmt").split("|")):
            txt = txt.replace(show(get(p_), f), " ", 1)
    for tok in NUM.findall(txt):
        A(tok.lstrip("+") in ALLOW, f"unsourced number {tok!r} in text {''.join(el.itertext())!r}")
A(SRC["l200r"]["bands"]["n"] == 16 and SRC["l199p"]["datasets"]["S"]["n"] == 96 and SRC["l199p"]["datasets"]["S"]["W"] == 150
  and SRC["l199p"]["datasets"]["S"]["pulse"] == 500, "allowlisted design constants equal the stored design")

# ---------------- (4) geometry, independent transforms ----------------
def yb(v): return 456.0 - v * 280.0
def xc(d): return 110.0 + d / 360.0 * 640.0
def yc(v): return 912.0 - v / 0.6 * 262.0
GX = {"R": 790.0, "R14": 990.0, "L": 1190.0}
MK = {"R": ("meanR", "dutyR", "kR"), "R14": ("mean14R", "duty14R", "k14R"), "L": ("meanL", "dutyL", "kL")}
ORDER = ["cutwA", "sc25", "l2", "l2k", "l2c"]
R = SRC["l200r"]


def arm(a):
    return R["base"] if a == "cutwA" else R["arms"][a]


bars = [e for e in root.iter(NS + "rect") if e.get("class") == "bar"]
A(len(bars) == 15, f"15 bars, got {len(bars)}")
for e in bars:
    g, a = e.get("data-group"), e.get("data-arm")
    v = arm(a)[MK[g][0]]
    x = GX[g] + ORDER.index(a) * 34.0
    A(abs(float(e.get("x")) - x) < 0.06, f"bar x {g}/{a}")
    A(abs(float(e.get("y")) - yb(v)) < 0.06 and abs(float(e.get("height")) - (456.0 - yb(v))) < 0.01, f"bar height {g}/{a} = {v}")
seeds = [e for e in root.iter(NS + "circle") if e.get("class") == "seed"]
A(len(seeds) == 15 * 16, f"240 seed dots, got {len(seeds)}")
for e in seeds:
    g, a, j = e.get("data-group"), e.get("data-arm"), int(e.get("data-j"))
    d = arm(a)[MK[g][1]][j]
    A(abs(float(e.get("cy")) - yb(d)) < 0.06, f"seed {g}/{a}/{j}")
    cx0 = GX[g] + ORDER.index(a) * 34.0 + 13.0
    A(abs(float(e.get("cx")) - cx0) <= 7.0, f"seed dot stays on its bar {g}/{a}/{j}")
dia = [e for e in root.iter(NS + "polygon") if e.get("class") == "fixed"]
A(len(dia) == 9, f"9 base-gain diamonds, got {len(dia)}")
for e in dia:
    g, aF = e.get("data-group"), e.get("data-arm")
    A(aF in ("l2F", "l2kF", "l2cF"), f"diamond arm {aF}")
    v = R["arms"][aF][MK[g][0]]
    pts = [tuple(map(float, p.split(","))) for p in e.get("points").split()]
    cy = (pts[0][1] + pts[2][1]) / 2
    A(abs(cy - yb(v)) < 0.1, f"diamond {g}/{aF} at {v}")
    A(abs(pts[0][0] - (GX[g] + ORDER.index(aF[:-1]) * 34.0 + 13.0)) < 0.1, f"diamond x {g}/{aF}")
thr = [e for e in root.iter(NS + "line") if e.get("class") == "thr"]
A(len(thr) == 3, "3 threshold lines")
for e in thr:
    want = R["bands"]["signature_mean14_min"] if e.get("data-group") == "R14" else R["bands"]["super_mean_min"]
    A(abs(float(e.get("y1")) - yb(want)) < 0.06, f"threshold {e.get('data-group')} at {want}")
octs = [e for e in root.iter(NS + "circle") if e.get("class") == "oct"]
A(len(octs) == 18, "18 octant points (8 + wrap, two graphs)")
OC = SRC["l199p"]["datasets"]["S"]["B"]["octants"]
for e in octs:
    g, k = e.get("data-graph"), int(e.get("data-k"))
    A(abs(float(e.get("cx")) - xc(45.0 * k)) < 0.06 and abs(float(e.get("cy")) - yc(OC[g][k % 8])) < 0.06, f"octant {g}/{k}")
for e in (x for x in root.iter(NS + "line") if x.get("class") == "theta"):
    th = SRC["l199p"]["datasets"]["S"]["B"]["graphs"][e.get("data-graph")]["theta"]["value"]
    A(abs(float(e.get("x1")) - xc(th % 360.0)) < 0.06, f"theta line {e.get('data-graph')}")
for e in (x for x in root.iter(NS + "rect") if x.get("class") == "thband"):
    th = SRC["l199p"]["datasets"]["S"]["B"]["graphs"][e.get("data-graph")]["theta"]
    A(abs(float(e.get("x")) - xc(th["value"] % 360.0 - th["se"])) < 0.06 and abs(float(e.get("width")) - th["se"] / 360.0 * 1280.0) < 0.02,
      f"theta SE band {e.get('data-graph')}")
arrows = [e for e in root.iter(NS + "line") if e.get("class") == "phase"]
A(len(arrows) == 4, "4 phase arrows")
for e in arrows:
    a_ = SRC["l199p"]["datasets"]["S"]["C"][e.get("data-graph")]["alpha"][e.get("data-pool")]
    ex = 1000.0 + 118.0 * a_["R"] * math.cos(math.radians(a_["mean_deg"]))
    ey = 772.0 - 118.0 * a_["R"] * math.sin(math.radians(a_["mean_deg"]))
    A(abs(float(e.get("x2")) - ex) < 0.01 and abs(float(e.get("y2")) - ey) < 0.01, f"phase arrow {e.get('data-graph')}/{e.get('data-pool')}")
for e in root.iter(NS + "text"):
    c = e.get("class")
    if c == "ytick":
        A(abs(float(e.get("y")) - 4 - yb(float(e.text))) < 0.06, f"B y-tick {e.text}")
    elif c == "yctick":
        A(abs(float(e.get("y")) - 4 - yc(float(e.text))) < 0.06, f"C y-tick {e.text}")
    elif c == "xctick":
        A(abs(float(e.get("x")) - xc(float(e.text.rstrip("°")))) < 0.06, f"C x-tick {e.text}")

# ---------------- (5) data truths behind the encodings ----------------
A(R["status"] == "FINAL" and SRC["l199p"]["status"] == "FINAL", "both result files FINAL")
A([R["arms"][a]["removed"] for a in ("sc25", "l2", "l2k", "l2c")] == [[1110], [70994], [70994], [70994, 1110]], "arm removal sets")
A(R["arms"]["l2k"]["x_carrier"] == R["base"]["x_carrier"], "l2k carrier rate == base (replay clamp)")
b = R["bands"]
for a in ORDER:
    for side, (mk, dk, kk) in MK.items():
        A(arm(a)[kk] == sum(1 for d in arm(a)[dk] if d >= 0.5), f"k {a}/{side} == #seeds with duty >= .5")
        A(len(arm(a)[dk]) == 16, f"16 seeds {a}/{side}")
    for side, (mk, kk, ck) in (("R", ("meanR", "kR", "clsR")), ("L", ("meanL", "kL", "clsL"))):
        m_, k_, c_ = arm(a)[mk], arm(a)[kk], arm(a)[ck]
        exp = "SUPER" if (k_ >= b["super_k_min"] and m_ >= b["super_mean_min"]) else \
              "NOT-SUPER" if (k_ <= b["not_k_max"] or m_ <= b["not_mean_max"]) else "INTERMEDIATE"
        A(c_ == exp, f"stored class {a}/{side} {c_} consistent with bands ({exp})")
A(R["arms"]["sc25"]["sigR"] and not R["arms"]["l2c"]["sigR"], "signature present on carrier cut, absent on double cut")
A(SRC["l190r"]["selection"]["E-edge"]["source"] == 1110 and SRC["l190r"]["selection"]["E-edge"]["target"] == 75494, "L190 edge is carrier->relay")
A(SRC["l198s"]["relay"]["carrier_to_relay"]["syn"] == SRC["l190r"]["selection"]["E-edge"]["syn"] == 21, "21 syn agrees L190/L198")
A(sorted(r["dst"] for r in EDGES if r["target_class"] == "direct right-Ti premotor") == ["69410", "72158", "75494"], "relay among 3 direct R-Ti premotor")
A(SRC["l200a4"]["cells"]["carrier"]["one_hop"]["PM_R"]["edges"] == 3, "a4 PM_R carrier edges == csv count 3")
A(sum(1 for r in EDGES if r["direction"] == "out") == SRC["l200a4"]["cells"]["carrier"]["out_edges"] == 80, "80 outputs csv == a4")
A(all(SRC["l200a4"]["cells"][c]["direct_onto"][p]["n_edges"] == 0 for c in ("carrier", "ru2") for p in ("Ti_fR", "Ti_eR", "Ti_fL", "Ti_eL")),
  "'no direct Ti motor edge from carrier or ru2'")
A(SRC["l198s"]["relay"]["cell"]["eff_sign"] == -1.0 and SRC["l200a4"]["cells"]["ru2"]["eff_sign"] == -1.0, "relay, ru2 inhibitory")
A(SRC["l199p"]["datasets"]["S"]["B"]["label"] == "Hq" and SRC["l199p"]["datasets"]["S"]["C"]["label"] == "Dq", "labels Hq / Dq as printed")
joined = " | ".join("".join(t.itertext()) for t in root.iter(NS + "text"))
for need in ["L202 replicate: pending", "label Hq", "Part C Dq · base co-move · cut intermediate", "schematic",
             "point ratio, no interval", "by elimination", "same arm, base gain"]:
    A(need in joined, f"text missing: {need!r}")

# ---------------- (6) caption ----------------
cap = open(f"{HERE}/fig6_caption.md").read()
prose = cap.split("### Per-number artifact pointers")[0]
ptrs = json.load(open(f"{HERE}/fig6_pointers.json"))
pos = 0
for c in ptrs["caption"]:
    r = get(c["src"])
    A(same(r, c["v"]), f"caption pointer {c['src']} value")
    want = show(r, c["fmt"])
    i = prose.find(want, pos)
    A(i >= 0, f"caption number {want!r} ({c['src']}) missing / out of order")
    pos = i + len(want) if i >= 0 else pos
    A(f"`{c['src']}`" in cap, f"caption table row for {c['src']}")
for f_ in ptrs["figure"]:
    A(f"`{f_['src']}`" in cap and same(get(f_["src"]), f_["v"]), f"figure pointer in caption table {f_['src']}")
stripped = prose
for c in ptrs["caption"]:
    stripped = stripped.replace(show(get(c["src"]), c["fmt"]), " ", 1)
for tok in re.findall(r"(?<![A-Za-z_\d.])[−+]?\d+\.\d+", stripped):
    A(tok in ("0.7", "1.4"), f"unsourced decimal in caption prose: {tok}")
A(len(ptrs["caption"]) >= 60 and len(ptrs["figure"]) >= 90, "pointer tables populated")

# ---------------- (7) layout (Liberation Serif = rsvg default here) ----------------
try:
    from PIL import ImageFont, Image
    FR = "/usr/share/fonts/liberation/LiberationSerif-Regular.ttf"
    FB = "/usr/share/fonts/liberation/LiberationSerif-Bold.ttf"
    boxes = []
    for t in root.iter(NS + "text"):
        if t.get("transform"):
            continue
        fs = float(t.get("font-size"))
        f = ImageFont.truetype(FB if t.get("font-weight") == "bold" else FR, int(round(fs * 4)))
        txt = "".join(t.itertext())
        w = f.getlength(txt) / 4
        x, y = float(t.get("x")), float(t.get("y"))
        an = t.get("text-anchor", "start")
        x0 = x - (w / 2 if an == "middle" else w if an == "end" else 0)
        boxes.append((x0, y - fs * 0.72, x0 + w, y + fs * 0.22, txt))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, c = boxes[i], boxes[j]
            A(not (a[0] < c[2] and c[0] < a[2] and a[1] < c[3] and c[1] < a[3]), f"text overlap: {a[4][:40]!r} / {c[4][:40]!r}")
    panels = [(24, 92, 700, 564), (716, 92, 1376, 564), (24, 580, 1376, 964)]
    for bx in boxes:
        for p_ in panels:
            hit = bx[0] < p_[2] and p_[0] < bx[2] and bx[1] < p_[3] and p_[1] < bx[3]
            inside = bx[0] >= p_[0] + 2 and bx[2] <= p_[2] - 2 and bx[1] >= p_[1] and bx[3] <= p_[3]
            A(not hit or inside, f"text crosses panel edge: {bx[4][:50]!r}")
        A(bx[0] >= 0 and bx[2] <= 1400, f"text on canvas: {bx[4][:40]!r}")
    for e in root.iter():
        if e.get("class") == "fixed":
            pts = [tuple(map(float, p.split(","))) for p in e.get("points").split()]
            mb = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        elif e.get("class") == "oct":
            cx_, cy_, r_ = float(e.get("cx")), float(e.get("cy")), float(e.get("r"))
            mb = (cx_ - r_, cy_ - r_, cx_ + r_, cy_ + r_)
        else:
            continue
        for bx in boxes:
            A(not (mb[0] < bx[2] and bx[0] < mb[2] and mb[1] < bx[3] and bx[1] < mb[3]), f"marker {e.get('class')} {e.get('data-arm') or e.get('data-graph')} covers text {bx[4][:30]!r}")
    for e in root.iter():
        cls = e.get("class")
        if cls not in ("edge", "fan", "phase"):
            continue
        if e.tag == NS + "line":
            pts = [(float(e.get("x1")), float(e.get("y1"))), (float(e.get("x2")), float(e.get("y2")))]
        else:
            n = list(map(float, re.findall(r"-?\d+\.?\d*", e.get("d"))))
            p0, p1, p2, p3 = list(zip(n[0::2], n[1::2]))[:4]
            pts = [tuple((1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * p1[k] + 3 * (1 - t) * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1))
                   for t in [i / 60 for i in range(61)]]
        dense = [(x1 + (x2 - x1) * k / 20, y1 + (y2 - y1) * k / 20) for (x1, y1), (x2, y2) in zip(pts, pts[1:]) for k in range(21)]
        for bx in boxes:
            A(not any(bx[0] < x < bx[2] and bx[1] < y < bx[3] for x, y in dense), f"{cls} {e.get('data-edge', '')} runs through text {bx[4][:40]!r}")
    # ---------------- (8) PNG ----------------
    png = open(f"{HERE}/fig6_circuit.png", "rb").read()
    A(png[:8] == b"\x89PNG\r\n\x1a\n", "png magic")
    A(struct.unpack(">II", png[16:24]) == (1400, 1012), "png dims 1400x1012")
    A(len(png) > 100000, f"png size {len(png)}")
    im = Image.open(f"{HERE}/fig6_circuit.png").convert("RGB")
    for name, (x0, y0, x1, y1) in zip("ABC", panels):
        crop = im.crop((x0 + 4, y0 + 30, x1 - 4, y1 - 4)).convert("L")
        hist = crop.histogram()
        ink = sum(hist[70:]) / (crop.width * crop.height)  # panel ground #21252b ~ L 37
        A(ink > 0.02, f"panel {name} ink {ink:.3f}")
except ImportError:
    A(False, "PIL needed for layout + PNG checks")

# ---------------- (10) earlier figures untouched ----------------
PIN = {
    "fig4_scatter.svg": None, "fig5_threepanel.svg": None, "l152_clamp_cut_grid.svg": None,
}
pin_file = f"{HERE}/fig6_verify.pins.json"
cur = {k: hashlib.sha256(open(f"{HERE}/{k}", "rb").read()).hexdigest() for k in PIN}
if os.path.exists(pin_file):
    old = json.load(open(pin_file))
    for k in PIN:
        A(old.get(k) == cur[k], f"{k} changed since fig6 pins were taken")
else:
    json.dump(cur, open(pin_file, "w"), indent=1)

print(f"checks run: {checks}  (pointers resolved: {n_ptr})")
if fails:
    print(f"FAILURES ({len(fails)}):")
    for f_ in fails:
        print("  -", f_)
    raise SystemExit(1)
print("FIG6 VERIFY: ALL PASS")
print(f"  15 bars + 240 seed dots + 9 base-gain diamonds (L200), 18 octant points + 2 theta lines + 4 phase arrows (L199), "
      f"{len(ptrs['figure'])} printed figure numbers + {len(ptrs['caption'])} caption numbers re-resolved; L202 {'landed' if l202_landed else 'pending'}")
