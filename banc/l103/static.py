"""L103 static: pin the two UNPAIRED-by-semantics motor pools (long_tendon,
femur_reductor) on the L92 closure subnet (keep_new) BEFORE rollouts.
Extraction verbatim l101/static.py. Tokens: substring match on
peripheral_target_type (lowercase). Discloses every distinct token string
matched so the substring choice is auditable, plus per-side sizes +
eligibility (>= 3 cells per side, l101 rule)."""
import json
import time

import numpy as np
import pandas as pd
import torch

t0 = time.time()
STATIC92 = json.load(open("l92/static.json"))
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
assert int(keep_new.sum()) == STATIC92["n_new"]

mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
keep_m = keep_new[mgi]

out = {"tokens": {}, "sizes": {}, "eligible": {}, "side_values": {}}
for key, tok in (("LT", "long_tendon"), ("FR", "femur_reductor")):
    hit = np.array([tok in x for x in ptt])
    out["tokens"][key] = sorted(set(ptt[hit]))
    sv = sorted(set(side_m[hit]))
    out["side_values"][key] = sv
    for c in ("L", "R"):
        m = hit & keep_m & (side_m == ("left" if c == "L" else "right"))
        out["sizes"][f"{key}_{c}"] = int(m.sum())
    other = hit & keep_m & ~np.isin(side_m, ["left", "right"])
    out["sizes"][f"{key}_other"] = int(other.sum())
    out["eligible"][key] = (out["sizes"][f"{key}_L"] >= 3
                            and out["sizes"][f"{key}_R"] >= 3)

# l101 disclosure cross-check: totals were 47 (long_tendon) / 34 (femur_reductor)
out["total_in_subnet"] = {k: int(out["sizes"][f"{k}_L"] + out["sizes"][f"{k}_R"]
                                 + out["sizes"][f"{k}_other"]) for k in ("LT", "FR")}
json.dump(out, open("l103/static.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print(f"static done {time.time()-t0:.0f}s")
