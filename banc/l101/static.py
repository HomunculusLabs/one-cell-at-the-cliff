"""L101 static: enumerate the FULL semantic antagonist-pool vocabulary on the
L92 closure subnet (keep_new), pin in-subnet per-side sizes + eligibility
(>= 3 cells per side pool) BEFORE rollouts. Extraction verbatim l94_run.py.
Pairs (semantic tokens in peripheral_target_type, lowercase substrings):
  Ti tibia flexor/extensor (l94 exact)      Tr trochanter flexor/extensor
  Ta tarsus depressor/levator               Sr sternal anterior/posterior rotator
  Pr tergopleural promotor / pleural remotor+abductor
Unpaired-by-semantics pools (disclosed, NOT scanned): long_tendon_muscle,
femur_reductor_muscle, and all head/wing/abdomen muscles.
"""
import json
import time

import numpy as np
import pandas as pd

t0 = time.time()
Gf = torch = None
import torch  # noqa: E402

STATIC92 = json.load(open("l92/static.json"))
ids_all = None

Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)
sup = ann.super_class.fillna("").astype(str).to_numpy()
region = ann.region.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()

conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)

cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True
dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into = dn_into & dn_all
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj = dn_proj & dn_all
keep_new = cord_mask | dn_into | dn_proj
n_new = int(keep_new.sum())
assert (int((cord_mask | dn_into).sum()), n_new) == (STATIC92["n_old"],
                                                     STATIC92["n_new"])

mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
loc = -np.ones(Nall, np.int64)
loc[keep_new] = np.arange(n_new)
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


PAIRS = {
    "Ti": (has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    "Tr": (has("trochanter") & has("flexor"),
           has("trochanter") & has("extensor")),
    "Ta": (has("tarsus") & has("depressor"), has("tarsus") & has("levator")),
    "Sr": (has("sternal") & has("anterior") & has("rotator"),
           has("sternal") & has("posterior") & has("rotator")),
    "Pr": (has("promotor"), has("remotor")),
}
# token-exclusivity asserts (no cross-pair leakage in the ptt vocabulary)
for tok in ("tarsus", "promotor", "remotor"):
    assert list(np.unique(ptt[has(tok)])) == [
        x for x in np.unique(ptt) if tok in x]
for tok, expect_n in (("depressor", 1), ("levator", 1), ("promotor", 1),
                      ("remotor", 1)):
    assert len(set(ptt[has(tok)])) == expect_n, (tok, set(ptt[has(tok)]))

sizes = {}
elig = {}
for k, (apat, bpat) in PAIRS.items():
    ok = True
    for c in ("aL", "aR", "bL", "bR"):
        pat = apat if c[0] == "a" else bpat
        m = keep_new[mgi] & pat & (side_m == SIDE_MAP[c[1].upper()])
        sizes[f"{k}_{c}"] = int(m.sum())
        ok = ok and int(m.sum()) >= 3
    elig[k] = bool(ok)
# l94 pool-name compatibility: Ti/Tr fL..eR sizes must equal l92 pins
l94map = {"f": "a", "e": "b"}
for k in ("Ti", "Tr"):
    for c in ("fL", "fR", "eL", "eR"):
        assert sizes[f"{k}_{l94map[c[0]]}{c[1]}"] == \
            STATIC92["pool_sizes"][f"{k}_{c}"], (k, c)

# disclosed: unpaired-by-semantics large pools in-subnet
unpaired = {}
for name in ("long_tendon_muscle", "femur_reductor_muscle"):
    unpaired[name] = int((keep_new[mgi] & (ptt == name)).sum())

out = dict(n_new=n_new, sizes=sizes, eligible=elig, unpaired=unpaired,
           min_side_pool=3)
json.dump(out, open("l101/static.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print(f"static done {time.time()-t0:.0f}s")
