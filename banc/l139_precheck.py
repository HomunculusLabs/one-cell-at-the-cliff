"""L139 precheck: FRESH B28 = 3201-3216 must be absent from EVERY stored
raw npz in banc/ (lineage discipline: fresh-batch absence asserted BEFORE
launch; L44/L118 class). Zero rollouts, CPU-only, read-only."""

import glob
import os

import numpy as np

B28 = list(range(3201, 3217))
pats = ["raw_*.npz", "*/raw_*.npz"]
files = sorted({f for p in pats for f in glob.glob(p)})
assert files, "no stored npz found"
bad = []
n_checked = 0
for f in files:
    try:
        z = np.load(f)
    except Exception as e:                      # noqa: BLE001
        print(f"  skip {f}: {e}")
        continue
    hits = [s for s in B28 if f"mm_full_{s}" in z.files]
    n_checked += 1
    status = "OK (absent)" if not hits else f"PRESENT {hits}"
    if hits:
        bad.append((f, hits))
    print(f"{f:44s} {status}")
print(f"checked {n_checked} npz files")
assert n_checked >= 20, n_checked
assert not bad, bad
print("B28 3201-3216 ABSENT from all stored npzs — PRECHECK PASS")
