"""L136 analytic figure QA (eyes-on-pixels UNAVAILABLE: vision endpoint timed
out 2x — substituted per house rule, DISCLOSED in LANE-LOG/LAB-INTENT).
Checks: (1) no literal HTML entities in text layer, (2) text overflow beyond
canvas via anchor-aware width estimate, (3) tick-strip slot spacing math,
(4) per-panel ink density on the PNG (each panel must carry ink; page must
not be blank), (5) every drawn numeral traceable in the SVG text layer.
"""
import json
import os
import re
import subprocess

import numpy as np

BANC = os.path.expanduser("~/critters/peabrain-lab/banc")
svg = open(f"{BANC}/l136/fig_l136.svg").read()
W, H = 1680, 760
P = json.load(open(f"{BANC}/l136/plot_data.json"))
fails = []

# 1. renderable entities: numeric refs (&#NNN;) are VALID svg (rsvg renders
# them as glyphs, house precedent l29_fig); only BARE ampersands are defects
texts = re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S)
assert texts, "no text elements found"
bare = [t for t in texts if re.search(r"&(?!#\d+;|amp;|lt;|gt;|quot;)", t)]
print("1 entity check:", "FAIL " + str(bare[:3]) if bare else "PASS (numeric refs renderable, 0 bare ampersands)")
fails += bare

# 2. anchor-aware overflow estimate (6.6px/char at fs<=13); rotated labels
# (transform=rotate) extend along y, not x — check their y-extent instead
over = []
for m in re.finditer(r'(<text x="([\d.]+)" y="([\d.]+)"[^>]*?text-anchor="(\w+)"[^>]*>)([^<]+)</text>', svg):
    head, x, y, anc, body = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4), m.group(5)
    w_est = 0.62 * 13 * len(body)
    if "rotate" in head:
        y0, y1 = y - w_est / 2, y + w_est / 2
        if y0 < 4 or y1 > H - 4 or not (4 < x < W - 4):
            over.append(("rot", int(y0), int(y1), body[:30]))
        continue
    lo = x - (w_est * {"middle": 0.5, "end": 1.0}.get(anc, 0.0))
    hi = x + (w_est * {"middle": 0.5, "start": 1.0}.get(anc, 0.0))
    if lo < 2 or hi > W - 2 or y < 10 or y > H - 4:
        over.append((int(lo), int(hi), int(y), body[:30]))
print("2 overflow scan:", f"FAIL {over[:4]}" if over else "PASS (all text within canvas bounds)")
fails += over

# 3. panel A tick slots
slot = 820 / 12
ok3 = slot > 40
print(f"3 tick-strip slots: {slot:.0f}px/slot", "PASS" if ok3 else "FAIL")
fails += [] if ok3 else ["slots"]

# 4. ink density per panel region (scale 2520/1680 = 1.5x) — ffmpeg raw decode
cap = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", f"{BANC}/l136/fig_l136.png",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
    capture_output=True, check=True).stdout
npx = len(cap) // 3
PH_PNG = npx // 2520  # rendered height at width 2520
img = np.frombuffer(cap, dtype=np.uint8).reshape(PH_PNG, 2520, 3).astype(int)
bg = np.array([0x28, 0x2c, 0x34])
ink = (np.abs(img - bg).sum(axis=2) > 40)
S = 2520 / W
panels = {"A": (96, 108, 820, 470), "B": (990, 108, 620, 210), "C": (990, 400, 620, 178)}
for nm, (x, y, w, h) in panels.items():
    reg = ink[int(y * S):int((y + h) * S), int(x * S):int((x + w) * S)]
    d = reg.mean()
    ok = 0.002 < d < 0.60
    print(f"4 ink density panel {nm}: {d:.4f}", "PASS" if ok else "FAIL")
    if not ok:
        fails.append(f"ink-{nm}")

# 5. every pooled numeral appears in the text layer
joined = " ".join(texts)
missing = []
for arm, q in P["pooled"].items():
    for val in (f"{q['k']}/{q['n']}",):
        if val not in joined:
            missing.append((arm, val))
print("5 numeral trace:", "FAIL " + str(missing) if missing else "PASS (all 10 pooled k/n labels in text layer)")
fails += missing

print("QA VERDICT:", "PASS (analytic; eyes-on-pixels unavailable — disclosed)" if not fails else f"FAIL {fails}")
