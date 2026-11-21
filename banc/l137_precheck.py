"""L141 precheck: B27 = 3101-3116 absent from EVERY stored npz (l135 form)."""
import glob
import numpy as np

B27 = list(range(3101, 3117))
nps = sorted(glob.glob("l1*/raw_l*.npz")) + sorted(glob.glob("l139/partial_j*.npz"))
assert len(nps) >= 30, nps
bad = []
for p in nps:
    z = np.load(p)
    hit = [s for s in B27 if f"mm_full_{s}" in z.files]
    if hit:
        bad.append((p, hit[:3]))
    z.close()
print(f"checked {len(nps)} npzs; B27 collisions: {bad}")
assert not bad, bad
print("PRECHECK PASS: B27 fresh everywhere")
