# Reviewer's analytic figure QA (vision endpoint down): parses the SVG sources, rasterises single elements with rsvg-convert
# to get true ink boxes, detects text/text and text/frame collisions, computes contrast + effective print sizes. Read-only on lab files.
import re, subprocess, sys, os, itertools, json
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
FIGS = {
 "fig1": ("/home/t3rpz/critters/peabrain-lab/banc/l136/fig_l136.svg", "/home/t3rpz/critters/peabrain-lab/banc/l136/fig_l136.png"),
 "fig2": ("/home/t3rpz/critters/peabrain-lab/paper/fig_l152.svg", "/home/t3rpz/critters/peabrain-lab/paper/fig_l152.png"),
 "fig3": ("/home/t3rpz/critters/peabrain-lab/banc/l160/fig_l160.svg", "/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain-figs/l160_slowline_carrier.png"),
}
NS = "{http://www.w3.org/2000/svg}"
def lum(hexc):
    hexc = hexc.lstrip("#"); r, g, b = [int(hexc[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def contrast(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb); return (hi + 0.05) / (lo + 0.05)
def ink_bbox(svg_header, elem_xml, W, H, tmp):
    doc = f'{svg_header}<rect width="{W}" height="{H}" fill="#000000"/>{elem_xml}</svg>'
    open(tmp + ".svg", "w").write(doc)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), tmp + ".svg", "-o", tmp + ".png"], check=True)
    a = np.asarray(Image.open(tmp + ".png").convert("L"))
    ys, xs = np.where(a > 40)
    if len(xs) == 0: return None
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
out = {}
for name, (svgp, pngp) in FIGS.items():
    raw = open(svgp).read()
    root = ET.fromstring(raw)
    W, H = int(float(root.get("width"))), int(float(root.get("height")))
    header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    texts = []
    for i, el in enumerate(root.iter(NS + "text")):
        xml = ET.tostring(el, encoding="unicode").replace('xmlns="http://www.w3.org/2000/svg" ', "").replace("ns0:", "")
        xml = re.sub(r'fill="#[0-9a-fA-F]{6}"', 'fill="#ffffff"', xml)
        bb = ink_bbox(header, xml, W, H, f"/home/t3rpz/.hermes/profiles/maple/cache/scratch/review_figs/_t_{name}")
        texts.append(dict(i=i, txt="".join(el.itertext()), fs=float(el.get("font-size")), fill=el.get("fill"), bb=bb, rot=bool(el.get("transform"))))
    # canvas clipping
    clipped = [t for t in texts if t["bb"] and (t["bb"][0] <= 1 or t["bb"][1] <= 1 or t["bb"][2] >= W - 2 or t["bb"][3] >= H - 2)]
    # text-text overlaps
    ov = []
    for a, b in itertools.combinations(texts, 2):
        if not a["bb"] or not b["bb"]: continue
        x0 = max(a["bb"][0], b["bb"][0]); y0 = max(a["bb"][1], b["bb"][1]); x1 = min(a["bb"][2], b["bb"][2]); y1 = min(a["bb"][3], b["bb"][3])
        if x1 - x0 >= 2 and y1 - y0 >= 2:
            ov.append((a["txt"][:60], b["txt"][:60], (x0, y0, x1, y1), (x1 - x0) * (y1 - y0)))
    # text vs panel-frame (rect with stroke) edges and long lines
    frames = []
    for el in root.iter(NS + "rect"):
        if el.get("stroke"):
            x, y, w, h = [float(el.get(k)) for k in ("x", "y", "width", "height")]
            frames.append((x, y, x + w, y + h))
    fr_hits = []
    for t in texts:
        if not t["bb"]: continue
        bx0, by0, bx1, by1 = t["bb"]
        for (x0, y0, x1, y1) in frames:
            for (ex0, ey0, ex1, ey1, lab) in ((x0, y0, x1, y0, "top"), (x0, y1, x1, y1, "bottom"), (x0, y0, x0, y1, "left"), (x1, y0, x1, y1, "right")):
                if bx0 <= ex1 and bx1 >= ex0 and by0 <= ey1 and by1 >= ey0 and (bx0 < ex0 - 0 or True):
                    # require the edge to pass through the interior of the text box
                    if (ex0 == ex1 and bx0 + 1 < ex0 < bx1 - 1) or (ey0 == ey1 and by0 + 1 < ey0 < by1 - 1):
                        fr_hits.append((t["txt"][:70], lab, (x0, y0, x1, y1), t["bb"]))
    fs = sorted(set(t["fs"] for t in texts))
    bg = "#282c34"; panel = "#21252b"
    fills = sorted(set(t["fill"] for t in texts))
    png = Image.open(pngp); pw, ph = png.size
    # PNG vs rsvg render of the SVG
    subprocess.run(["rsvg-convert", "-w", str(pw), "-h", str(ph), svgp, "-o", f"_r_{name}.png"], check=True)
    A = np.asarray(png.convert("RGB")).astype(int); Bm = np.asarray(Image.open(f"_r_{name}.png").convert("RGB")).astype(int)
    diff = np.abs(A - Bm).mean(); frac_big = float((np.abs(A - Bm).max(axis=2) > 60).mean())
    info = dict(svg_size=(W, H), png_size=(pw, ph), n_text=len(texts), font_sizes_px=fs,
                pt_at_6p5in=[round(f * 468 / W, 1) for f in fs], pt_at_3p4in=[round(f * 245 / W, 1) for f in fs],
                share_text_below_6pt_at_6p5in=round(sum(1 for t in texts if t["fs"] * 468 / W < 6) / len(texts), 2),
                contrast={f: (round(contrast(f, bg), 2), round(contrast(f, panel), 2)) for f in fills},
                png_vs_rsvg_meanabsdiff=round(float(diff), 2), png_vs_rsvg_frac_pixels_diff=round(frac_big, 4),
                clipped=[t["txt"][:80] for t in clipped], n_overlaps=len(ov), n_frame_hits=len(fr_hits))
    out[name] = info
    print("=====", name, json.dumps(info, indent=1))
    print("  TEXT-TEXT OVERLAPS (ink boxes):")
    for a, b, box, area in sorted(ov, key=lambda x: -x[3])[:14]: print("    ", repr(a), "<->", repr(b), box, "area", area)
    print("  TEXT crossing a stroked panel-frame edge:")
    for t, lab, fr, bb in fr_hits[:14]: print("    ", repr(t), "| edge", lab, "of frame", fr, "| text box", bb)
    longest = sorted(texts, key=lambda t: -(t["bb"][2] - t["bb"][0]) if t["bb"] and not t["rot"] else 0)[:3]
    for t in longest: print("  widest text:", t["bb"], "W", W, repr(t["txt"][:90]))
