#!/usr/bin/env python3
"""Referee R4 figure spot check: invert the SVG pixel geometry back to data
values and compare against the stored results files. Independent of the lab's
own fig4_verify.py (which asserts forward, from data to pixels)."""
import json, re, math, csv

ROOT = "/home/t3rpz/critters/peabrain-lab"
svg = open(f"{ROOT}/paper/figures/fig4_scatter.svg").read()
L = json.load(open(f"{ROOT}/banc/l175/results_l175.json"))

# geometry PARSED from fig4_scatter.py so this check cannot go stale when the
# figure is re-polished (it was, mid-review: XDOM upper went 1.25 -> 1.6)
gen = open(f"{ROOT}/paper/figures/fig4_scatter.py").read()
PX0, PX1, PYT, PYB = [int(v) for v in re.search(
    r'PX0, PX1, PYT, PYB = *(\d+), *(\d+), *(\d+), *(\d+)', gen).groups()]
xd = re.search(r'XDOM = \(math\.log10\(([^)]+)\), math\.log10\(([^)]+)\)\)', gen).groups()
XDOM = (math.log10(float(xd[0])), math.log10(float(xd[1])))
YLO, YHI = [float(v) for v in re.search(r'YLO, YHI = *([\d.]+), *([\d.]+)', gen).groups()]
print(f"parsed geometry: PX0={PX0} PX1={PX1} PYT={PYT} PYB={PYB} "
      f"XDOM=({xd[0]},{xd[1]}) YLO={YLO} YHI={YHI}")
inv_x = lambda px: 10 ** (XDOM[0] + (px - PX0) / (PX1 - PX0) * (XDOM[1] - XDOM[0]))
inv_y = lambda py: YLO + (PYB - py) / (PYB - PYT) * (YHI - YLO)

index = {L["base"]["arm"]: L["base"]}
for w in L["window"]:
    index[w["arm"]] = w
for t in L["twins"].values():
    index[t["arm"]] = t

print("=" * 72)
print("[1d-fig] FIG 4 INVERSE GEOMETRY CHECK (pixels -> data)")
print("=" * 72)
print("source: paper/figures/fig4_scatter.svg")
print("declared header:", re.search(r'data-n-arms="[^"]*" data-y="[^"]*" data-x="[^"]*"', svg).group(0))
print()

# markers carry data-arm plus cx/cy (circle) or a transform-free points list
pat = re.compile(r'<(circle|rect|polygon|path)[^>]*data-arm="([^"]+)"[^>]*>')
found = {}
for m in re.finditer(r'<[^>]*data-arm="([^"]+)"[^>]*>', svg):
    tag = m.group(0)
    arm = m.group(1)
    cx = re.search(r'\bcx="([-\d.]+)"', tag)
    cy = re.search(r'\bcy="([-\d.]+)"', tag)
    if cx and cy:
        found.setdefault(arm, []).append((float(cx.group(1)), float(cy.group(1)), tag))

print(f"circle-type markers with data-arm: {len(found)} distinct arms, "
      f"{sum(len(v) for v in found.values())} markers total")
print()
hdr = f"{'arm':7s} {'px':>8s} {'py':>8s} | {'x̄ from px':>11s} {'stored x̄':>11s} | {'meanR from px':>13s} {'stored':>8s}  verdict"
print(hdr)
print("-" * len(hdr))
bad = 0
for arm in ["sc25", "sc26", "sc27", "sc40", "dmA", "dmC", "sc41", "sc50", "sc33"]:
    if arm not in found:
        print(f"{arm:7s} NOT FOUND as a circle marker")
        continue
    # the b39 (primary) marker is the one whose y inverts to the stored meanR
    a = index[arm]
    best = None
    for (px, py, tag) in found[arm]:
        dv, mv = inv_x(px), inv_y(py)
        err = abs(mv - a["meanR"])
        if best is None or err < best[0]:
            best = (err, px, py, dv, mv)
    err, px, py, dv, mv = best
    # x̄ is floored at 1e-4 in the plot
    xs = max(a["x_mean"], 1e-4)
    okx = abs(math.log10(dv) - math.log10(xs)) < 0.01
    oky = abs(mv - a["meanR"]) < 0.002
    if not (okx and oky):
        bad += 1
    print(f"{arm:7s} {px:8.1f} {py:8.1f} | {dv:11.5f} {xs:11.5f} | "
          f"{mv:13.4f} {a['meanR']:8.3f}  {'OK' if okx and oky else 'MISMATCH'}")

print(f"\nmarkers disagreeing with stored data: {bad}")

# the plotted threshold and base band must match the registered band / Wilson CI
th = re.search(r'id="super-threshold" data-v="([\d.]+)"', svg)
bb = re.search(r'id="base-band" data-lo="([\d.]+)" data-hi="([\d.]+)"', svg)
bl = re.search(r'id="base-line" data-v="([\d.]+)"', svg)
print(f"\nplotted SUPER threshold data-v={th.group(1)}  "
      f"(registered super_meanR_min={L['bands']['super_meanR_min']})  "
      f"{'OK' if float(th.group(1)) == L['bands']['super_meanR_min'] else 'MISMATCH'}")
print(f"plotted base band [{bb.group(1)},{bb.group(2)}]  "
      f"stored base Wilson [{L['base']['lbR']:.6f},{L['base']['ubR']:.6f}]  "
      f"{'OK' if abs(float(bb.group(1))-L['base']['lbR'])<1e-9 and abs(float(bb.group(2))-L['base']['ubR'])<1e-9 else 'MISMATCH'}")
print(f"plotted base line data-v={bl.group(1)}  stored base meanR={L['base']['meanR']}  "
      f"{'OK' if abs(float(bl.group(1))-L['base']['meanR'])<1e-9 else 'MISMATCH'}")

# --------------------------------------------------------------- fig4 caption
print("\n" + "=" * 72)
print("[1d-fig] CAPTION ARITHMETIC CHECKS")
print("=" * 72)
act = [w for w in L["window"] if w["active"]]
car = index["sc25"]
harder = [w for w in act if w["arm"] != "sc25"
          and w["delivered_drive"] > car["delivered_drive"]]
ratios = sorted(w["delivered_drive"] / car["delivered_drive"] for w in harder)
print(f"cells delivering MORE drive than the carrier: {len(harder)}  "
      f"ratio range x{ratios[0]:.2f}-x{ratios[-1]:.2f}")
print("  fig4 caption says: 'seven cells are driven harder than the carrier (1.5-4.2x)'")
print("  draft §2.1 says:   '7 that deliver more drive than the carrier (x1.46 to x4.16)'")
print(f"  none of them super? {[w['arm'] for w in harder if w['kR']>=12 and w['meanR']>=0.6] or 'confirmed none'}")
print()
# the caption's own 'active' rule (x̄ > 0.05) vs the stored active flag
for thr in (0.0, 0.001, 0.01, 0.05, 0.1):
    print(f"  x̄ > {thr:<6}: {sum(1 for w in L['window'] if w['x_mean'] > thr):2d} of 34 window cells active")
print(f"  stored 'active' flag:  {len(act)} of 34   (draft §2.1 says 14)")
border = [(w["arm"], w["x_mean"], w["active"]) for w in L["window"]
          if 0.0 < w["x_mean"] <= 0.05]
print(f"  cells with 0 < x̄ <= 0.05 (where the two rules can differ): {border}")

print("\n" + "=" * 72)
print("[1d-fig] FIG 5 ROW CHECK vs threepanel.csv")
print("=" * 72)
svg5 = open(f"{ROOT}/paper/figures/fig5_threepanel.svg").read()
tp = {r["arm"]: r for r in csv.DictReader(open(f"{ROOT}/banc/l184/threepanel.csv"))}
print(f"threepanel.csv arms: {len(tp)}   (fig5 caption says 'all 37 arms of the B39 scan')")
rows5 = set(re.findall(r'data-arm="([^"]+)"', svg5))
print(f"fig5 svg distinct data-arm values: {len(rows5)}")
print(f"arms in csv but not in svg: {sorted(set(tp) - rows5) or 'none'}")
print(f"arms in svg but not in csv: {sorted(rows5 - set(tp)) or 'none'}")
# spot check three plotted values
for m in re.finditer(r'<[^>]*data-arm="([^"]+)"[^>]*data-series="([^"]+)"[^>]*data-v="([-\d.]+)"[^>]*>', svg5):
    arm, ser, v = m.group(1), m.group(2), float(m.group(3))
    if arm in ("sc25", "cutwA", "dmA"):
        key = {"chopped": "chopped_mean", "fast": "fast_mean", "cross": "cross_mean"}.get(ser)
        if key:
            ok = abs(v - float(tp[arm][key])) < 1e-6
            print(f"  {arm:6s} {ser:8s} plotted={v:.6f} csv={float(tp[arm][key]):.6f} "
                  f"{'OK' if ok else 'MISMATCH'}")
print("\nDONE")
