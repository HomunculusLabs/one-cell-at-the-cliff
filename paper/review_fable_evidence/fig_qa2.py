# text-vs-graphics collision test: does any text ink sit on top of non-background marks (frames, bars, lines, markers)?
import re, subprocess, json
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
FIGS = {
 "fig1": "/home/t3rpz/critters/peabrain-lab/banc/l136/fig_l136.svg",
 "fig2": "/home/t3rpz/critters/peabrain-lab/paper/fig_l152.svg",
 "fig3": "/home/t3rpz/critters/peabrain-lab/banc/l160/fig_l160.svg",
}
NS = "{http://www.w3.org/2000/svg}"
BG = [(0x28, 0x2c, 0x34), (0x21, 0x25, 0x2b)]
def render(doc, W, H, tag):
    open(f"_{tag}.svg", "w").write(doc)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), f"_{tag}.svg", "-o", f"_{tag}.png"], check=True)
    return np.asarray(Image.open(f"_{tag}.png").convert("RGB")).astype(int)
for name, svgp in FIGS.items():
    raw = open(svgp).read()
    root = ET.fromstring(raw); W, H = int(float(root.get("width"))), int(float(root.get("height")))
    header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    notext = re.sub(r"<text\b.*?</text>", "", raw, flags=re.S)
    base = render(notext, W, H, f"nt_{name}")
    isbg = np.zeros(base.shape[:2], bool)
    for c in BG: isbg |= (np.abs(base - np.array(c)).max(axis=2) <= 6)
    print("=====", name)
    hits = []
    for el in root.iter(NS + "text"):
        xml = ET.tostring(el, encoding="unicode").replace('xmlns="http://www.w3.org/2000/svg" ', "")
        xml = re.sub(r'fill="#[0-9a-fA-F]{6}"', 'fill="#ffffff"', xml)
        a = render(f'{header}<rect width="{W}" height="{H}" fill="#000000"/>{xml}</svg>', W, H, f"one_{name}")
        ink = a.max(axis=2) > 90
        n = int(ink.sum())
        if n == 0: continue
        on_marks = int((ink & ~isbg).sum())
        if on_marks >= 6:
            ys, xs = np.where(ink & ~isbg)
            # dominant colour under the colliding ink
            cols = base[ys, xs]; u, cnt = np.unique(cols, axis=0, return_counts=True); dom = tuple(int(v) for v in u[cnt.argmax()])
            hits.append((round(on_marks / n, 3), on_marks, "".join(el.itertext())[:75], (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), "#%02x%02x%02x" % dom))
    for h in sorted(hits, reverse=True)[:25]: print("   ", h)
    print("   n texts colliding with drawn marks:", len(hits))
