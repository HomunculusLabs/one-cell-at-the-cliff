"""L56 fig analytic QA v2 (vision endpoint down 000, disclosed):
rotation-aware bboxes; plot-frame rects (fill=none) excluded from
collisions; OOB strict; every numeric claim re-derived from results json."""
import json
import re

svg = open("l56/reroll.svg").read()
W, H = 1560, 880
res = json.load(open("l56/results_l56.json"))
rows, seg2 = res["rows"], res["seg2"]

boxes = []
for m in re.finditer(
        r'<text x="([\d.-]+)" y="([\d.-]+)"([^>]*)>(.*?)</text>', svg):
    x, y, attrs, txt = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4)
    fs = 13.0
    fsm = re.search(r'font-size="(\d+)"', attrs)
    if fsm:
        fs = float(fsm.group(1))
    anchor = "middle" if 'text-anchor="middle"' in attrs else \
        ("end" if 'text-anchor="end"' in attrs else "start")
    clean = re.sub(r"&[a-z#0-9]+;", "x", txt)
    w = 0.62 * fs * len(clean)
    rot = 'rotate(' in attrs
    if rot:                            # rotated: tall-narrow around (x,y)
        hgt, wid = w, fs * 1.1
        x0, y0, x1, y1 = x - wid / 2, y - hgt / 2, x + wid / 2, y + hgt / 2
    else:
        x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        x1 = x0 + w
        y0, y1 = y - fs, y + 2
    boxes.append((x0, y0, x1, y1, clean[:36], "text"))
for m in re.finditer(r'<circle cx="([\d.-]+)" cy="([\d.-]+)" r="([\d.]+)"', svg):
    x, y, r = float(m.group(1)), float(m.group(2)), float(m.group(3))
    boxes.append((x - r, y - r, x + r, y + r, "circle", "shape"))
for m in re.finditer(
        r'<rect x="([\d.-]+)" y="([\d.-]+)" width="([\d.-]+)" height="([\d.-]+)"'
        r'([^>]*)>', svg):
    x, y, w, h = (float(m.group(i)) for i in range(1, 5))
    attrs = m.group(5)
    if w >= W - 5 or 'fill="none"' in attrs:
        continue                          # bg canvas + plot frames excluded
    boxes.append((x, y, x + w, y + h, "rect", "shape"))

oob = [b for b in boxes if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H]
coll = []
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        a, b = boxes[i], boxes[j]
        if a[5] == "shape" and b[5] == "shape":
            continue
        ox = min(a[2], b[2]) - max(a[0], b[0])
        oy = min(a[3], b[3]) - max(a[1], b[1])
        if ox > 2 and oy > 2:
            coll.append((a[4], b[4], round(ox, 1), round(oy, 1)))

# ---- numeric re-derivation ----
checks = []
checks.append(("s22 transition rescue",
               seg2["nohop"][1] == 0.147 and seg2["hop4k"][1] == 0.627))
mid22 = [seg2[a][1] for a in ("v43", "v46", "v49")]
checks.append(("s22 mid-seg2 never rescues",
               mid22 == [0.187, 0.113, 0.147] and max(mid22) < 0.25))
flips = []
for a in ("hop4k", "v43", "v46", "v49"):
    for s in ("11", "22", "33"):
        c = rows[f"{a}|{s}"]
        pre = rows[f"nohop|{s}"]["seg2_label"] if a == "hop4k" else c["pre_label"]
        post = c.get("post_label", c["seg2_label"])
        if pre != post:
            flips.append((a, s))
edge = [f for f in flips if f[0] in ("hop4k", "v49")]
mid = [f for f in flips if f[0] in ("v43", "v46")]
checks.append(("3 edge flips 0 mid flips", len(edge) == 3 and len(mid) == 0))
p3 = res["P3"]
checks.append(("means panel", p3["nohop"] == 0.438
               and p3["volley_means"] == {"hop4k": 0.54, "v43": 0.4,
                                          "v46": 0.338, "v49": 0.405}))
misses = res["P2_misses"]
checks.append(("4 misses all seed-22 SL<.20 SR>.30",
               len(misses) == 4 and all(k.endswith("|22") for k in misses)
               and all(v["SL"] < 0.20 and v["SR"] > 0.30
                       for v in misses.values())))
checks.append(("P1a/P1b/P1c footer",
               res["P1a"]["diff"] == 0.203 and res["P1b"]["n_redraw"] == 2
               and res["P1c"]["chi2_vs_ref"] == {"L": 0.6, "R": 0.0}))
from math import comb
pfisher = comb(3, 3) * comb(9, 3) / comb(12, 6)
checks.append(("fisher p=.091 label", abs(pfisher - 0.0909) < 5e-4
               and "p=.091" in svg))
print(f"boxes {len(boxes)} | out-of-bounds {len(oob)} | collisions {len(coll)}")
for c in oob:
    print("  OOB:", c)
for c in coll:
    print("  COLL:", c)
for name, ok in checks:
    print(("PASS " if ok else "FAIL ") + name)
print("flip cells:", flips)
assert not oob and not coll and all(ok for _, ok in checks), "QA FAIL"
print("ANALYTIC-QA PASS (vision endpoint down, disclosed)")
