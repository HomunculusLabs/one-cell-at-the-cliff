"""L107 static: decompose the l65-extraction vs L92-closure membership difference.

Claim-carrier per LANE.md L107: which cell classes/edges the closure ADDS over
l65 (dn_new = dn_proj & ~dn_into, 560 cells), their targets by tier, and the
out-mass ranking that defines the ONE bisection slice (cut graph = closure
minus the top-out-mass dn_new subset). No rollouts here; every pin goes to
l107/static.json BEFORE PREREG (L44 rule).
Extraction = l94_run.py verbatim (lines 56-107).
"""
import json
import os

import numpy as np
import pandas as pd

os.makedirs("l107", exist_ok=True)
STATIC92 = json.load(open("l92/static.json"))

# ---------------- extraction (l94_run.py verbatim) ----------------
Gf = None
import torch  # noqa: E402 (only for the .pt load)

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
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into = dn_into & dn_all
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj = dn_proj & dn_all
keep_old = cord_mask | dn_into
keep_new = cord_mask | dn_into | dn_proj

# ---- L107 sanity pins vs l92 static ----
assert int(keep_old.sum()) == STATIC92["n_old"]
assert int(keep_new.sum()) == STATIC92["n_new"]
emask_o = keep_old[src_all] & keep_old[dst_all]
emask_n = keep_new[src_all] & keep_new[dst_all]
assert int(emask_o.sum()) == STATIC92["edges_old"]
assert int(emask_n.sum()) == STATIC92["edges_new"]

gi_new = np.where(keep_new)[0]
gi_old = np.where(keep_old)[0]
dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
assert len(dn_new_g) == STATIC92["dn_new"]
assert dn_new_g.max() < Nall

# same val form as build()
gsign_a = sign_all[src_all]
gsign_b = np.where(is_glut[src_all], -np.abs(gsign_a), gsign_a)
vals_all = (np.log1p(w_syn) * gsign_b).astype(np.float64)

added = emask_n & ~emask_o
assert int(added.sum()) == STATIC92["edges_new"] - STATIC92["edges_old"]

src_add, dst_add, v_add = src_all[added], dst_all[added], vals_all[added]
in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True
is_dnnew_src = in_new_cell[src_add]
is_dnnew_dst = in_new_cell[dst_add]

# pool masks (global ids) — l94 POOLS form
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOL_G = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor")),
]:
    for c in ("fL", "fR", "eL", "eR"):
        sel = fpat if c[0] == "f" else epat
        POOL_G[f"{k}_{c}"] = np.sort(mgi[sel & (side_m == SIDE_MAP[c[1].upper()])])

pool_mask_g = np.zeros(Nall, bool)
for k in POOL_G:
    pool_mask_g[POOL_G[k]] = True

# tiers for added-edge targets
tier_of_dst = np.full(Nall, "", dtype=object)
reg_ann = region  # ann-row numpy arrays (built above)
sup_ann = sup
tier_of_dst[ann_gi[sup_ann == "motor"]] = "motor_other"
tier_of_dst[ann_gi[(sup_ann == "motor") & pool_mask_g[ann_gi]]] = "motor_pools"
tier_of_dst[ann_gi[sup_ann == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup_ann == "sensory") & (reg_ann == "ventral_nerve_cord")]] = "vnc_sensory"

cat = np.where(is_dnnew_src & is_dnnew_dst, "dnnew->dnnew",
               np.where(is_dnnew_src & ~is_dnnew_dst, "dnnew->old",
                        "old->dnnew"))
tier = np.array([tier_of_dst[d] for d in dst_add], dtype=object)
out_rows = cat == "dnnew->old"
out_tiers = {}
for t in ("motor_pools", "motor_other", "intrinsic", "vnc_sensory", ""):
    m = out_rows & (tier == t)
    out_tiers[t or "dn(old non-cord)"] = dict(
        edges=int(m.sum()), mass=round(float(np.abs(v_add[m]).sum()), 3))

# per-dn_new out-mass onto CORD (motor_pools/motor_other/intrinsic/vnc_sensory)
cord_of_dst = np.isin(tier, ["motor_pools", "motor_other", "intrinsic",
                             "vnc_sensory"])
om = out_rows & cord_of_dst
outmass = np.zeros(Nall)
np.add.at(outmass, src_add[om], np.abs(v_add[om]))
cell_mass = outmass[dn_new_g]
order = np.argsort(-cell_mass)
cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1)
cut_drop = np.sort(dn_new_g[order[:K]])          # removed by the slice
keep_cut = keep_new.copy()
keep_cut[cut_drop] = False
assert (keep_cut.sum()) == keep_new.sum() - K
emask_c = keep_cut[src_all] & keep_cut[dst_all]

# dn_new annotation families
ann_idx = {int(g): i for i, g in enumerate(ann_gi)}
ct = ann.cell_type.fillna("").astype(str).to_numpy()
fam = {}
for g in dn_new_g:
    fam[ct[ann_idx[int(g)]]] = fam.get(ct[ann_idx[int(g)]], 0) + 1
top_fam = dict(sorted(fam.items(), key=lambda x: -x[1])[:12])
drop_fam = {}
for g in cut_drop:
    drop_fam[ct[ann_idx[int(g)]]] = drop_fam.get(ct[ann_idx[int(g)]], 0) + 1
drop_fam = dict(sorted(drop_fam.items(), key=lambda x: -x[1])[:12])

# direct added edges onto Ti/Tr pools + their share of pool in-mass (old graph)
pool_direct = {}
for pk in ("Ti_fL", "Ti_fR", "Ti_eL", "Ti_eR", "Tr_fL", "Tr_fR", "Tr_eL", "Tr_eR"):
    pm = np.zeros(Nall, bool)
    pm[POOL_G[pk]] = True
    added_in = added & pm[dst_all] & in_new_cell[src_all]
    old_in = emask_o & pm[dst_all]
    pool_direct[pk] = dict(
        added_edges=int(added_in.sum()),
        added_mass=round(float(np.abs(vals_all[added_in]).sum()), 3),
        old_in_mass=round(float(np.abs(vals_all[old_in]).sum()), 3))

out = dict(
    n_old=int(keep_old.sum()), n_new=int(keep_new.sum()),
    n_cut=int(keep_cut.sum()), edges_old=int(emask_o.sum()),
    edges_new=int(emask_n.sum()), edges_cut=int(emask_c.sum()),
    added_edges=int(added.sum()),
    added_categories={
        "dnnew->old": int(out_rows.sum()),
        "dnnew->dnnew": int((cat == "dnnew->dnnew").sum()),
        "old->dnnew": int((cat == "old->dnnew").sum())},
    out_tiers_by_target=out_tiers,
    dnnew_families=top_fam,
    outmass_total=round(float(cell_mass.sum()), 3),
    cut=dict(K=K, mass_share=round(float(cum[K - 1]), 4),
             families=drop_fam,
             n_cells=int((keep_new.sum() - keep_cut.sum()))),
    pool_direct_in=pool_direct,
    af_target=STATIC92["af_target"],
    pins=dict(n_old=STATIC92["n_old"], n_new=STATIC92["n_new"],
              edges_old=STATIC92["edges_old"], edges_new=STATIC92["edges_new"],
              dn_new=STATIC92["dn_new"]))
json.dump(out, open("l107/static.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "pool_direct_in"},
                 indent=1))
print("--- added edges onto pools (direct) ---")
for pk, d in pool_direct.items():
    print(f"{pk:6s} added {d['added_edges']:3d} mass {d['added_mass']:8.3f} "
          f"vs old in-mass {d['old_in_mass']:9.3f}")
