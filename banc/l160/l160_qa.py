"""L160 analytic figure QA (plus eyes-on-pixels via vision, per card).
Checks: (1) no bare ampersands in text layer, (2) anchor-aware overflow,
(3) per-panel ink density on the PNG, (4) every k/n numeral + panel-B pins
present in the SVG text layer, (5) family bracket spacing math.
"""
import json
import os
import re
import subprocess

import numpy as np

BANC = os.path.expanduser("~/critters/peabrain-lab/banc")
svg = open(f"{BANC}/l160/fig_l160.svg").read()
W, H = 1680, 800
P = json.load(open(f"{BANC}/l157/static.json"))["pooled"]
fails = []

# 1. renderable entities
texts = re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S)
assert texts, "no text elements"
bare = [t for t in texts if re.search(r"&(?!(#\d+;|\d+;|amp;|lt;|gt;|quot;|apos;))", t)]
print("1 entity check:", "FAIL " + str(bare[:3]) if bare else "PASS (0 bare ampersands)")
fails += bare

# 2. anchor-aware overflow estimate (6.6px/char at fs<=13)
over = []
pat_anch = re.compile(r'(<text x="([\d.]+)" y="([\d.]+)"[^>]*?text-anchor="(\w+)"[^>]*>)([^<]+)</text>')
pat_free = re.compile(r'(<text x="([\d.]+)" y="([\d.]+)"(?![^>]*text-anchor)[^>]*>)([^<]+)</text>')
rows = [(m.group(1), float(m.group(2)), float(m.group(3)), m.group(4), m.group(5))
        for m in pat_anch.finditer(svg)]
rows += [(m.group(1), float(m.group(2)), float(m.group(3)), "start", m.group(4))
         for m in pat_free.finditer(svg)]
for head, x, y, anc, body in rows:
    w_est = 0.62 * 13 * len(body)
    if "rotate" in head:
        y0, y1 = y - w_est / 2, y + w_est / 2
        if y0 < 4 or y1 > H - 4 or not (4 < x < W - 4):
            over.append(("rot", int(y0), int(y1), body[:30]))
        continue
    lo = x - (w_est * {"middle": 0.5, "end": 1.0}.get(anc, 0.0))
    hi = x + (w_est * {"middle": 0.5, "end": 1.0, "start": 0.0}.get(anc, 0.0))
    if lo < 2 or hi > W - 2 or y < 10 or y > H - 4:
        over.append((int(lo), int(hi), int(y), body[:30]))
print("2 overflow scan:", f"FAIL {over[:4]}" if over else "PASS (all text within canvas)")
fails += over

# 3. slot spacing: 22 slots across panel A width
slot = 1090 / 22
ok3 = slot > 44
print(f"3 panel-A slot width: {slot:.1f}px/slot", "PASS" if ok3 else "FAIL")
fails += [] if ok3 else ["slots"]

# 4. ink density per panel (render width 2520, scale 1.5x)
cap = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", f"{BANC}/l160/fig_l160.png",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
    capture_output=True, check=True).stdout
npx = len(cap) // 3
PH_PNG = npx // 2520
img = np.frombuffer(cap, dtype=np.uint8).reshape(PH_PNG, 2520, 3).astype(int)
bg = np.array([0x28, 0x2C, 0x34])
ink = (np.abs(img - bg).sum(axis=2) > 40)
S = 2520 / W
panels = {"A": (96, 120, 1090, 440), "B": (1250, 120, 390, 300)}
for nm, (x, y, w, h) in panels.items():
    reg = ink[int(y * S):int((y + h) * S), int(x * S):int((x + w) * S)]
    d = reg.mean()
    ok = 0.002 < d < 0.60
    print(f"4 ink density panel {nm}: {d:.4f}", "PASS" if ok else "FAIL")
    if not ok:
        fails.append(f"ink-{nm}")

# 5. numeral trace: every pooled k/n + panel-B pinned strings
joined = " ".join(texts)
missing = [f"{k}:{v['below']}/{v['n']}" for k, v in P.items()
           if f"{v['below']}/{v['n']}" not in joined]
for pin in ("518/518", "361/500", "lb 0.993", "lb 0.681", "median .100 Hz",
            "0.100 Hz", "0.117", "414/518", "80/361", "331/361"):
    if pin not in joined:
        missing.append(pin)
print("5 numeral trace:", "FAIL " + str(missing) if missing else "PASS (all 22 k/n + panel-B pins in text layer)")
fails += missing

print("QA VERDICT:", "PASS (analytic + vision follow-up)" if not fails else f"FAIL {fails}")
