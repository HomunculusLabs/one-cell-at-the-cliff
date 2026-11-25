#!/usr/bin/env python3
"""t287 survey 4 (L294): what STORED readout channels exist per arm (names only), so the
PREREG can name the control-cell confound instrument before anything is scored. READ-ONLY."""
import json, os, re, collections
import numpy as np

B = os.path.expanduser("~/critters/peabrain-lab/banc")
for p in ("l291/raw_w0.npz", "l291/raw_w1.npz", "l290/raw_w0.npz", "l290/raw_w1.npz", "l290/raw_w2.npz",
          "l291/xm_w0.npz", "l291/xm_w1.npz", "l290/xm_w0.npz", "l290/xm_w1.npz", "l290/xm_w2.npz"):
    z = np.load(os.path.join(B, p), allow_pickle=False)
    ks = list(z.keys())
    # stem = name with the trailing _<arm>_<seed> removed
    stems = collections.Counter()
    armseed = collections.defaultdict(set)
    for k in ks:
        m = re.match(r"^(.*)_(\d+)$", k)
        stem, rest = m.group(1), m.group(2)
        m2 = re.match(r"^(.*)_(\d+)$", stem)
        arm, seed = (m2.group(1), m2.group(2)) if m2 else (stem, None)
        stems[arm] += 1
        armseed[arm].add(seed)
    print(p, "| arrays", len(ks))
    print("   arm names (%d): %s" % (len(stems), sorted(stems)))
    print("   per-arm array counts:", {a: stems[a] for a in sorted(stems)})
    a0 = sorted(stems)[0]
    print("   seeds per arm (first 3 arms):", {a: sorted(armseed[a]) for a in sorted(stems)[:3]})
    ex = [k for k in ks if k.startswith(a0 + "_")]
    print("   example array names for arm %r: %s" % (a0, ex[:6] + ex[-4:]))

pools = json.load(open(os.path.join(B, "l291/pools_w0.json")))
print("\npools_w0 keys:", list(pools.keys()))
for k, v in pools.items():
    if k != "pools":
        print("  [%s] %s" % (k, json.dumps(v)[:300]))
s291 = json.load(open(os.path.join(B, "l291/sets.json")))
pool_cells = set()
for name, ids in pools["pools"].items():
    pool_cells.update(ids)
print("pool union size:", len(pool_cells))
tg = [m["target"] for m in s291["menu"]]
print("menu targets inside the pool union:", sum(1 for t in tg if t in pool_cells), "of", len(tg))
print("l291 pools_w0 == l290 pools_w0:", pools == json.load(open(os.path.join(B, "l290/pools_w0.json"))))
r = json.load(open(os.path.join(B, "l291/results_l291.json")))
print("l291 floorN:", json.dumps(r["floorN"])[:300])
print("l291 strat_meta:", json.dumps(r["strat_meta"])[:400])
print("l291 seeds:", r["seeds"] if not isinstance(r["seeds"], list) or len(r["seeds"]) < 20 else (len(r["seeds"]), r["seeds"][:3], r["seeds"][-3:]))
print("l291 arms_gain sample:", json.dumps(dict(list(r["arms_gain"].items())[:3]))[:300])
print("l290 anchors:", json.dumps(json.load(open(os.path.join(B, "l290/anchors_w0.json"))))[:300])
