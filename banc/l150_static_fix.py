"""L150 static fix: pin the CORRECTED motor_edges_ranked table (ADDENDUM 1)
to l150/static.json. Re-derives the ranking from the unchanged data files
(probe-proven form); writes pos correctly paired with dst/w/syn; records
the l145 zip-bug defect + scope. l145/static.json itself stays untouched
(stored artifacts immutable). Zero rollouts, deterministic."""
import json

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(4)
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()
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
tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = "vnc_sensory"

GI = 1110
mp = np.where((src_all == GI)
              & (tier_of_dst[dst_all] == "motor_other"))[0]
assert len(mp) == 10
mo = mp[np.lexsort((mp, -np.log1p(w_syn[mp])))]
ann_by_gi = ann.set_index("gi")


def ident(g):
    try:
        return str(ann_by_gi.loc[int(g)].get("cell_type", "") or "")
    except Exception:
        return "?"


corrected = [dict(pos=int(p), dst_gi=int(dst_all[p]),
                  w=round(float(np.log1p(w_syn[p])), 6),
                  syn=int(w_syn[p]), dst_type=ident(dst_all[p]))
             for p in mo]
S145 = json.load(open("l145/static.json"))
# defect re-signature: stored pos column ascending; dst/syn columns match
# the corrected ranked order (they were the ranked columns all along)
stored_pos = [e["pos"] for e in S145["motor_edges_ranked"]]
assert stored_pos == sorted(int(p) for p in mp), "defect signature changed"
for i, e in enumerate(S145["motor_edges_ranked"]):
    assert e["syn"] == corrected[i]["syn"] and \
        e["dst_gi"] == corrected[i]["dst_gi"], ("column mismatch", i)
out = dict(
    design="L150 ADDENDUM 1: corrected motor_edges_ranked (l145 zip bug). "
           "Zero rollouts, no RNG; ranking re-derived from unchanged data "
           "(mtimes 11-14).",
    defect="l145_static.py zipped UNRANKED mot_pos with RANKED dst/w/syn "
           "columns (zip(mot_pos, mot_dst, mot_w, mot_cnt) should pair "
           "mot_ord); stored 'pos' column = ascending np.where(out_mot)[0].",
    scope="l145 RUN arms unaffected (masks from mot_ord in l145_run.py, "
          "subset law asserted on masks); mass splits + top5_share "
          "(computed from masks) correct; dst_gi/syn columns were the "
          "ranked order and are reproduced here verbatim; consumed "
          "nowhere downstream (draft grep clean, 11-19).",
    top5_dsts=[e["dst_type"] for e in corrected[:5]],
    bot5_dsts=[e["dst_type"] for e in corrected[5:]],
    top5_pos=[e["pos"] for e in corrected[:5]],
    bot5_pos=[e["pos"] for e in corrected[5:]],
    motor_edges_ranked=corrected)
json.dump(out, open("l150/static.json", "w"), indent=1)
print("corrected top5:", out["top5_dsts"], out["top5_pos"])
print("corrected bot5:", out["bot5_dsts"], out["bot5_pos"])
print("l150/static.json written")
