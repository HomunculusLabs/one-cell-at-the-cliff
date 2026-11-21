"""L150 precheck: B33 (3365-3380) absent from EVERY npz under banc/.
Standalone form (l148_precheck pattern). Exit non-zero on any collision."""
import glob
import sys

import numpy as np

B33 = list(range(3365, 3381))
bad = []
files = sorted(glob.glob("**/*.npz", recursive=True))
assert len(files) >= 80, f"npz census suspicious: {len(files)}"
for f in files:
    try:
        z = np.load(f)
    except Exception as e:  # noqa: BLE001
        print("UNREADABLE", f, e)
        bad.append((f, "unreadable"))
        continue
    hit = [s for s in B33 if f"mm_full_{s}" in z.files]
    if hit:
        bad.append((f, hit))
        print("COLLISION", f, hit)
print(f"checked {len(files)} npz under banc/: "
      f"{'PASS (zero B33 collisions)' if not bad else 'FAIL'}")
sys.exit(1 if bad else 0)
