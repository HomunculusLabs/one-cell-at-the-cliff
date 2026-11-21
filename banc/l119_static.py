"""L119 STATIC derivation (zero rollouts): minimal glut subset pins.

Extraction VERBATIM from l117_static.py (l113 form), then NEW:
(a) dose ladder k in {1, 2, 3, 5} — the k HEAVIEST glutamatergic heavy cells
    (deterministic mass-desc positional filter, NO RNG); k=5 re-derived and
    asserted == l117/static.json ladder k5 EXACTLY (zero-rollout cross-check);
(b) cutr5 — a PINNED-RNG random 5-of-19-glut draw (torch.Generator seed
    1190, randperm(19)[:5], uniform without replacement; mass disclosed,
    overlap with the heaviest-5 disclosed).
Writes l119/static.json for the PREREG pins. PREREG l119/PREREG.md BEFORE
l119_run.
"""
import json
import os

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S117 = json.load(open("l117/static.json"))

# ---------------- extraction (l113_run.py verbatim) ----------------
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
assert int(keep_old.sum()) == S92["n_old"] and int(keep_new.sum()) == S92["n_new"]

gsign_a = sign_all[src_all]
gsign_b = np.where(is_glut[src_all], -np.abs(gsign_a), gsign_a)
vals_all = (np.log1p(w_syn) * gsign_b).astype(np.float64)
emask_o = keep_old[src_all] & keep_old[dst_all]
emask_n = keep_new[src_all] & keep_new[dst_all]
added = emask_n & ~emask_o
gi_new = np.where(keep_new)[0]
gi_old = np.where(keep_old)[0]
dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
assert len(dn_new_g) == S92["dn_new"]
in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True
out_rows = added & in_new_cell[src_all]

tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory")
                   & (region == "ventral_nerve_cord")]] = "vnc_sensory"
cord_of_dst = np.isin(tier_of_dst[dst_all],
                      ["motor_other", "intrinsic", "vnc_sensory"])
om = out_rows & cord_of_dst
outmass = np.zeros(Nall)
np.add.at(outmass, src_all[om], np.abs(vals_all[om]))
cell_mass = outmass[dn_new_g]
order = np.argsort(-cell_mass)
cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1)
cut_drop = np.sort(dn_new_g[order[:K]])
keep_cut = keep_new.copy()
keep_cut[cut_drop] = False
assert (K, round(float(cum[K - 1]), 4)) == (ST["cut"]["K"], ST["cut"]["mass_share"])
assert int(keep_cut.sum()) == ST["n_cut"]
heav = dn_new_g[order[:K]]
cut19_drop = np.sort(heav[is_glut[heav]])
assert len(cut19_drop) == 19, f"glut heavy = {len(cut19_drop)} != 19 (STOP)"
_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split

# ---------------- L119 NEW (a): minimal dose ladder ----------------
# glut_desc is mass-DESC (positional filter of heav); glut_desc[:k] = the k
# HEAVIEST glut cells. k=5 must reproduce l117's stored ladder pin EXACTLY.
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
gmass = cell_mass[order[:K]][is_glut[heav]]           # same order as glut_desc
total = cell_mass.sum()
sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[(sub_dn.cell_type == "DNg100").to_numpy()].to_numpy()
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"

pins = {"glut19_ids_desc_mass": [int(x) for x in glut_desc],
        "glut19_cell_mass_share": [round(float(m / total), 5) for m in gmass],
        "mass_split": mass_split}
ladder = {}
for k in (1, 2, 3, 5):
    drop = np.sort(glut_desc[:k])
    assert len(drop) == k
    assert np.isin(drop, cut19_drop).all(), "ladder drop not subset of glut-19"
    keep_v = keep_new.copy()
    keep_v[drop] = False
    n_v = int(keep_v.sum())
    assert n_v == int(keep_new.sum()) - k
    em = int((keep_v[src_all] & keep_v[dst_all]).sum())
    ladder[f"k{k}"] = dict(
        drop_ids=[int(x) for x in drop],
        n=int(n_v),
        edges=em,
        mass_removed=round(float(gmass[:k].sum() / total), 4),
        mass_cum_in_glut19=round(float(gmass[:k].sum() / gmass.sum()), 4))
# zero-rollout cross-check: k5 re-derivation == l117 stored static EXACTLY
assert ladder["k5"]["drop_ids"] == S117["ladder"]["k5"]["drop_ids"], "k5 drift"
for kk in ("n", "edges", "mass_removed", "mass_cum_in_glut19"):
    assert ladder["k5"][kk] == S117["ladder"]["k5"][kk], f"k5 {kk} drift"
pins["ladder"] = ladder

# ---------------- L119 NEW (b): pinned random 5-of-19-glut draw ----------
g5 = torch.Generator().manual_seed(1190)
perm = torch.randperm(19, generator=g5)
sel = perm[:5].numpy()                                  # uniform, no replacement
r5_drop = np.sort(glut_desc[sel])
assert len(r5_drop) == 5
assert np.isin(r5_drop, cut19_drop).all(), "r5 draw not subset of glut-19"
assert is_glut[r5_drop].all(), "non-glut cell in r5 draw (STOP)"
assert not np.isin(dng100_all, r5_drop).any(), "DNg100 in r5 draw (STOP)"
keep_r5 = keep_new.copy()
keep_r5[r5_drop] = False
n_r5 = int(keep_r5.sum())
assert n_r5 == int(keep_new.sum()) - 5
em_r5 = int((keep_r5[src_all] & keep_r5[dst_all]).sum())
top5 = set(int(x) for x in ladder["k5"]["drop_ids"])
pins["draw"] = {"cutr5": dict(
    seed=1190,
    method="torch.Generator(1190).randperm(19)[:5], glut_desc order",
    sel_desc_pos=[int(x) for x in sel],
    drop_ids=[int(x) for x in r5_drop],
    n=int(n_r5),
    edges=em_r5,
    mass_removed=round(float(gmass[sel].sum() / total), 4),
    overlap_with_heaviest5=int(len(top5 & set(int(x) for x in r5_drop))),
    includes_heaviest1=bool(int(glut_desc[0]) in set(int(x) for x in r5_drop)),
    includes_second1=bool(int(glut_desc[1]) in set(int(x) for x in r5_drop)))}

# stored-arm edge pins re-derived for the C0S-form sanity (must equal stored)
pins["edges_stored"] = {
    "cut": int((keep_cut[src_all] & keep_cut[dst_all]).sum()),
    "n_cut": int(keep_cut.sum()), "n_new": int(keep_new.sum())}
assert pins["edges_stored"]["cut"] == ST["edges_cut"]
os.makedirs("l119", exist_ok=True)
json.dump(pins, open("l119/static.json", "w"), indent=1)
print(json.dumps({k: pins[k] for k in ("ladder", "draw")}, indent=1))
print("l119/static.json written")
