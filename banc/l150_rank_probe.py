"""L150 probe: why does the ported rank disagree with l145/static.json?
Replicates the RUN-script extraction verbatim, computes the 10 motor
out-edges of 1110, ranks by log1p(syn) and by absv, prints vs stored."""
import json

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()
print("sign uniques:", np.unique(sign_all)[:8])

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)
nt = pd.read_csv("data/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True
region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)
gsign_a = sign_all[src_all]
gsign_b = np.where(is_glut[src_all], -np.abs(gsign_a), gsign_a)
vals_all = (np.log1p(w_syn) * gsign_b).astype(np.float64)
absv = np.abs(vals_all)
tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = "vnc_sensory"

GI = 1110
sel = (src_all == GI) & (tier_of_dst[dst_all] == "motor_other")
mp = np.where(sel)[0]
print("n motor out-edges:", len(mp))
by_log = mp[np.lexsort((mp, -np.log1p(w_syn[mp])))]
by_abs = mp[np.lexsort((mp, -absv[mp]))]
S = json.load(open("l145/static.json"))
stored = [e["pos"] for e in S["motor_edges_ranked"]]
print("by log1p:", by_log.tolist())
print("by absv :", by_abs.tolist())
print("stored  :", stored)
print("log==stored:", by_log.tolist() == stored)
print("abs==stored:", by_abs.tolist() == stored)
for p in mp:
    print(p, "syn", w_syn[p], "sign", gsign_a[p], "absv", round(absv[p], 4),
          "log1p", round(float(np.log1p(w_syn[p])), 4))
