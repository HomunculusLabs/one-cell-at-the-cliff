"""l213_scope.py — SCOPING ONLY (no certified values, writes nothing).
How many present descending cells per substrate, how many cell_types with
>= 2 present members, and does DNp33 have exactly 2? Needed to size the
depth-2 reach census and the within-stratum permutation null.
"""
import json

import numpy as np
import pandas as pd
import torch

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
pure_proj = dn_proj & ~dn_into

print("n descending annotated:", int(dn_all.sum()))
print("dn_into:", int(dn_into.sum()), "dn_proj:", int(dn_proj.sum()),
      "pure_proj:", int(pure_proj.sum()))
pres = np.where(keep_new & dn_all)[0]
print("present descending on closure:", len(pres))
print("  of which pure_proj:", int(pure_proj[pres].sum()))

ct = ann.cell_type.fillna("").astype(str).to_numpy()
ct_of = {int(g): c for g, c in zip(ann_gi, ct)}
types = {}
for g in pres:
    c = ct_of.get(int(g), "")
    if c and c.lower() != "nan":
        types.setdefault(c, []).append(int(g))
big = {k: v for k, v in types.items() if len(v) >= 2}
print("named types among present descending:", len(types),
      "| with >= 2 members:", len(big))
print("cells covered by >=2 types:", sum(len(v) for v in big.values()))
sizes = sorted((len(v) for v in big.values()), reverse=True)
print("type size distribution head:", sizes[:15], "... n2:",
      sum(1 for s in sizes if s == 2))
print("DNp33 present members:", types.get("DNp33"))
print("DNp33 pure_proj flags:",
      [bool(pure_proj[g]) for g in types.get("DNp33", [])])
json.dump({"ok": True}, open("/dev/null", "w"))
