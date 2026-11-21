"""L135 pre-check: B26 seeds 3001-3016 absent from every stored raw npz
(zero rollouts; the run re-asserts this itself, but the PREREG wants the
absence verified BEFORE any code runs)."""
import numpy as np

B26 = list(range(3001, 3017))
Npz = ["l113/raw_l113.npz", "l115/raw_l115.npz", "l117/raw_l117.npz",
       "l118/raw_l118.npz", "l119/raw_l119.npz", "l120/raw_l120.npz",
       "l121/raw_l121.npz", "l122/raw_l122.npz", "l123/raw_l123.npz",
       "l124/raw_l124.npz", "l125/raw_l125.npz", "l126/raw_l126.npz",
       "l127/raw_l127.npz", "l128/raw_l128.npz", "l131/raw_l131.npz",
       "l133/raw_l133.npz"]
bad = []
for p in Npz:
    z = np.load(p)
    hit = [s for s in B26 if f"mm_full_{s}" in z.files]
    print(f"{p:24s} arms-in-npz~{sum(1 for f in z.files if f.startswith('mm_full_')) // 100} collision {len(hit)}")
    bad += hit
assert not bad, ("B26 collides", bad[:5], [p for p in Npz if any(f"mm_full_{s}" in np.load(p).files for s in bad[:1])])
print("B26 3001-3016 ABSENT from all 16 stored npzs — OK")
