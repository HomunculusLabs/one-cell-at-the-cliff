"""L170 PRE-CHECK (feasibility, runs BEFORE the PREREG registers floor arms).

L146 lesson: histogram the RELEASE's effective weight floor before registering
any synapse-floor robustness arm. L125 lesson: feasibility-check numeric
constraints against stored pins first.

Zero rollouts, no RNG. Reads the MaleCNS release only; writes nothing but
l170/precheck.json.
"""
import json
import os

import numpy as np
import pandas as pd

MD = "../malecns/data/"
mw = pd.read_feather(
    MD + "connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
print(f"rows {len(mw):,}")
w = mw["weight"].to_numpy(np.float64)
print(f"weight min {w.min()} max {w.max()} dtype {mw['weight'].dtype}")
hist = {}
for k in (1, 2, 3, 4, 5, 10):
    hist[f"ge{k}"] = int((w >= k).sum())
for k in (1, 2, 3, 4, 5):
    hist[f"eq{k}"] = int((w == k).sum())
print("histogram:", hist)

# pair uniqueness (does the release carry one row per ordered body pair?)
npairs = mw.groupby(["body_pre", "body_post"], sort=False).size()
dups = int((npairs > 1).sum())
print(f"ordered pairs {len(npairs):,} | pairs with >1 row {dups:,}")

# what does the floor delete among pairs that matter (in-graph only is checked
# in the real script; here just the release-level view)
out = dict(rows=int(len(mw)), w_min=float(w.min()), w_max=float(w.max()),
           hist=hist, n_pairs=int(len(npairs)), dup_pairs=dups,
           frac_ge3=round(float((w >= 3).sum() / len(w)), 6),
           frac_ge4=round(float((w >= 4).sum() / len(w)), 6))
os.makedirs("l170", exist_ok=True)
json.dump(out, open("l170/precheck.json", "w"), indent=1)
print("\nl170/precheck.json written")
