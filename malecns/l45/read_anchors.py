import csv, json
from collections import Counter

import numpy as np

# ---- L40 stored windows: per-seed pre/post attractor numbers ----
r40 = json.load(open("l40/results_l40.json"))
for arm in ("ctl",):
    for s, w in r40["win"][arm].items():
        pre, post = w["pre"], w["post"]
        print(f"L40 {arm} seed {s}: pre f={pre.get('f_mm'):.2f} SL={pre.get('SL'):.2f} "
              f"SR={pre.get('SR'):.2f} S={pre.get('S'):.2f} | post f={post.get('f_mm'):.2f} "
              f"SL={post.get('SL'):.2f} SR={post.get('SR'):.2f}")

# ---- L36 census table ----
rows = list(csv.DictReader(open("l36/census_l36.csv")))
print("\nL36 cols:", list(rows[0].keys()))
print("L36 n:", len(rows))
for col in rows[0].keys():
    if any(k in col.lower() for k in ("verdict", "class", "status", "side")):
        print(col, "->", Counter(r[col] for r in rows).most_common(8))
