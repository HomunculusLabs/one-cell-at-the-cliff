import subprocess, re, xml.etree.ElementTree as ET
from PIL import Image, ImageOps
FIGS = {
 "fig1": ("/home/t3rpz/critters/peabrain-lab/banc/l136/fig_l136.svg", "/home/t3rpz/critters/peabrain-lab/banc/l136/fig_l136.png"),
 "fig2": ("/home/t3rpz/critters/peabrain-lab/paper/fig_l152.svg", "/home/t3rpz/critters/peabrain-lab/paper/fig_l152.png"),
 "fig3": ("/home/t3rpz/critters/peabrain-lab/banc/l160/fig_l160.svg", "/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain-figs/l160_slowline_carrier.png"),
}
NS = "{http://www.w3.org/2000/svg}"
def toks(s): return [t for t in re.findall(r"[A-Za-z0-9_./+\-]{2,}", s)]
def ocr(img, tag):
    img.save(f"_ocr_{tag}.png")
    r = subprocess.run(["tesseract", f"_ocr_{tag}.png", "-", "--psm", "11"], capture_output=True, text=True)
    return r.stdout
for name, (svgp, pngp) in FIGS.items():
    root = ET.parse(svgp).getroot()
    truth = []
    for el in root.iter(NS + "text"):
        truth += toks("".join(el.itertext()))
    tset = set(truth)
    im = ImageOps.invert(Image.open(pngp).convert("L"))
    res = {}
    for label, width in (("native", im.size[0]), ("6.5in@300dpi(1950px)", 1950), ("6.5in@150dpi(975px)", 975), ("3.4in@300dpi(1020px)", 1020)):
        if width > im.size[0]: 
            res[label] = None; continue
        h = round(im.size[1] * width / im.size[0]); j = im.resize((width, h), Image.LANCZOS)
        got = set(toks(ocr(j, name)))
        res[label] = round(len(tset & got) / len(tset), 2)
    print(name, "distinct text tokens:", len(tset), "| OCR token recall:", res)
