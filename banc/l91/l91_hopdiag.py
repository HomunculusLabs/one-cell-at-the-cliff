"""L91 ADDENDUM diagnostic: why did the female hop volley never land?

Static census on the BANC subnet edges: DNge046 out-edges (global, ->cord,
->kept), in-edges of the kept cell, DNg100 contrast (the drive that works).
"""
import json

import numpy as np
import pandas as pd
import torch

ar = json.load(open("l91/anchors_run.json"))
z = np.load("l91/raw_l91.npz")
for a in ("fn_fb", "fh", "fh_fb", "fsham"):
    dms = [float(np.abs(z[f"mm_{a}_{s}"] - z[f"mm_fn_{s}"]).max())
           for s in (11, 501)]
    print(a, "dm seeds 11/501:", [round(v, 6) for v in dms])

Gf = torch.load("banc_graph.pt", weights_only=False)
DATA = "data"
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
ann = pd.read_csv(f"{DATA}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)
region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True
conn = pd.read_csv(f"{DATA}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g.index], np.int64)
w_syn = g.to_numpy(np.float64)
dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into
sub_dn = ann[ann.super_class == "descending"]
ct = sub_dn.cell_type.fillna("").astype(str).to_numpy()
gi46 = sub_dn.gi[ct == "DNge046"].to_numpy()
print("DNge046 global cells:", len(gi46), "in-subnet:", int(keep[gi46].sum()))
loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
for gg in gi46:
    outs = (src_all == gg)
    to_cord = outs & cord_mask[dst_all]
    to_keep = outs & keep[dst_all]
    print(f"cell {int(gg)}: out-edges {outs.sum()}, syn "
          f"{w_syn[outs].sum():.0f}, ->cord {to_cord.sum()} "
          f"({w_syn[to_cord].sum():.0f} syn), ->kept {to_keep.sum()}")
gk = gi46[keep[gi46]][0]
ins = (dst_all == gk)
print(f"kept cell in-edges: {ins.sum()} total, from cord "
      f"{int((ins & cord_mask[src_all]).sum())}")
gi100 = sub_dn.gi[ct == "DNg100"].to_numpy()
for gg in gi100:
    outs = (src_all == gg)
    to_cord = outs & cord_mask[dst_all]
    print(f"DNg100 {int(gg)}: out-edges {outs.sum()}, ->cord "
          f"{to_cord.sum()} ({w_syn[to_cord].sum():.0f} syn)")
