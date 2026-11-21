"""L106 analytic QA via ImageMagick text dumps (no PIL): right-edge strips of
each caption band must be pure background; outer border must be empty."""
import subprocess

BANDS = {"title/sub": (20, 60), "ti-callout": (498, 514),
         "footer1": (528, 544), "footer2": (544, 560)}
W = 960
ok = True
for name, (y, h) in BANDS.items():
    out = subprocess.run(
        ["convert", "l106/l106_laterality.png", "-crop", f"8x{h-y}+{W-8}+{y}",
         "-depth", "8", "txt:-"], capture_output=True, text=True).stdout
    worst = 0
    for line in out.splitlines():
        if "(" not in line or ")" not in line or ":" not in line:
            continue
        rgb = line.split("(", 1)[1].split(")")[0].split(",")
        worst = max([worst] + [abs(int(c) - b) for c, b in zip(rgb, (0x28, 0x2C, 0x34))])
    clean = worst <= 6
    ok &= clean
    print(f"{name:12s} right-edge max |dBG| = {worst:3d}  {'OK' if clean else 'CLIP!'}")
# outer border: 3px frame all around must be background
for edge, geo in [("top", "960x3+0+0"), ("bottom", "960x3+0+557"), ("left", "3x560+0+0"), ("right", "3x560+957+0")]:
    out = subprocess.run(
        ["convert", "l106/l106_laterality.png", "-crop", geo, "-depth", "8", "txt:" + ":"],
        capture_output=True, text=True).stdout
    worst = 0
    for line in out.splitlines():
        if "(" not in line or ")" not in line:
            continue
        rgb = line.split("(", 1)[1].split(")")[0].split(",")
        worst = max([worst] + [abs(int(c) - b) for c, b in zip(rgb, (0x28, 0x2C, 0x34))])
    ok &= worst <= 6
    print(f"border {edge:6s} max |dBG| = {worst:3d}  {'OK' if worst <= 6 else 'INK!'}")
print("overall:", "PASS" if ok else "FAIL")
