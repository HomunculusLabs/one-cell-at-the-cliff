import json

r = json.load(open("l45/results_l45b.json"))
v = r["verdict"]
print("== census states (SEG-A, 16 seeds):", v["census_states"])
print("== migrations (A->B->C label changes):", v["n_migrations"], "seeds")
for s, labs in list(v["migrations"].items())[:8]:
    print("  seed", s, " ".join(labs))
print("\n== transition edges (FROM -> TO, credit only if TO != base's own SEG-C) ==")
for ch, byfrom in v["edges"].items():
    for frm, d in byfrom.items():
        tos = {k: n for k, n in d["to"].items() if not k.startswith("<same") and k != "<pinned:dm=0>"}
        same = sum(n for k, n in d["to"].items() if k.startswith("<same"))
        pin = d["to"].get("<pinned:dm=0>", 0)
        flat = d["flat"]
        dm = d["dm"]
        print(f"{ch:11s} {frm:9s} -> {tos} | same-as-base {same} pinned {pin} flat {flat} dm {dm}")
print("\n== dm (channel pool dX, SEG-C) ==")
from collections import defaultdict
dd = defaultdict(list)
for k, val in v["dm"].items():
    ch, s = k.rsplit("_", 1)
    dd[ch].append(val)
for ch, vals in dd.items():
    print(f"  {ch:11s} min {min(vals):+.3f} max {max(vals):+.3f}")
print("\n== per-seed census detail (anchor seeds) ==")
for s in ("11", "22", "33"):
    c = r["census"][s]
    for seg in ("A", "B", "C"):
        d = c[seg]
        print(f"  seed {s} {seg}: {d['label']:9s} f={d['f']:.2f} r={d['r']:.0f} SL={d['SL']:+.2f} SR={d['SR']:+.2f}")
