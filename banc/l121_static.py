"""L121 STATIC derivation (zero rollouts): non-glut dose ladder pins.

Extraction VERBATIM from l120_static.py (l113 form), then:
  - retained arm cutk5 re-pinned and asserted == l120/l119/l117 stored EXACT;
  - NEW ng ladder: the 58 NON-glutamatergic heavy cells in mass-DESC order
    (ng_desc), deterministic positional drops k in {19, 29, 39} + the k58
    endpoint (== the l113 cut58 arm, cross-checked by set identity and by
    recomputing its edge count on the same keep mask).
Writes l121/static.json for the PREREG pins. PREREG l121/PREREG.md BEFORE
l121_run. NO RNG anywhere in L121 (deterministic heaviest-first ladder).
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
S119 = json.load(open("l119/static.json"))
S120 = json.load(open("l120/static.json"))

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

# ---------------- L121 NEW: retained k5 + non-glut dose ladder ----------------
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
ng_desc = heav[~is_glut[heav]]
assert len(ng_desc) == 58, f"non-glut heavy = {len(ng_desc)} != 58 (STOP)"
# set identity: ng ladder endpoint == the l113 cut58 arm
assert np.array_equal(np.sort(ng_desc), np.sort(heav[~is_glut[heav]]))
assert len(np.union1d(np.sort(glut_desc), np.sort(ng_desc))) == K == 77

total = cell_mass.sum()
sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[(sub_dn.cell_type == "DNg100").to_numpy()].to_numpy()
assert not np.isin(dng100_all, heav).any(), "DNg100 in heavy-77 (STOP)"

gmass = cell_mass[order[:K]][is_glut[heav]]           # glut_desc order
ngmass = cell_mass[order[:K]][~is_glut[heav]]         # ng_desc order
assert abs(ngmass.sum() / total - mass_split["other58"]) < 5e-4

pins = {"glut19_ids_desc_mass": [int(x) for x in glut_desc],
        "glut19_cell_mass_share": [round(float(m / total), 5) for m in gmass],
        "mass_split": mass_split}

# retained anchor arm: cutk5 == l120/l119/l117 stored EXACTLY
ladder = {}
drop5 = np.sort(glut_desc[[0, 1, 2, 3, 4]])
keep5 = keep_new.copy()
keep5[drop5] = False
ladder["k5"] = dict(
    drop_ids=[int(x) for x in drop5],
    n=int(keep5.sum()),
    edges=int((keep5[src_all] & keep5[dst_all]).sum()),
    mass_removed=round(float(gmass[[0, 1, 2, 3, 4]].sum() / total), 4),
    mass_cum_in_glut19=round(float(gmass[[0, 1, 2, 3, 4]].sum() / gmass.sum()), 4))
for _prev in (S117, S119, S120):
    assert ladder["k5"]["drop_ids"] == _prev["ladder"]["k5"]["drop_ids"], "k5 drift"
    for f in ("n", "edges", "mass_removed", "mass_cum_in_glut19"):
        assert ladder["k5"][f] == _prev["ladder"]["k5"][f], f"k5 {f} drift"
assert ladder["k5"]["mass_removed"] == 0.0425
assert ladder["k5"]["edges"] == 647252
pins["ladder"] = ladder

# the NEW non-glut dose ladder (deterministic, mass-desc positional prefixes)
ngl = {"ng58_ids_desc_mass": [int(x) for x in ng_desc],
       "ng58_cell_mass_share": [round(float(m / total), 5) for m in ngmass]}
for kk in (19, 29, 39, 58):
    drop = np.sort(ng_desc[:kk])
    keep_v = keep_new.copy()
    keep_v[drop] = False
    n_v = int(keep_v.sum())
    assert n_v == int(keep_new.sum()) - kk
    assert np.isin(drop, np.sort(ng_desc)).all()
    em = int((keep_v[src_all] & keep_v[dst_all]).sum())
    ngl[f"k{kk}"] = dict(
        drop_ids=[int(x) for x in drop],
        n=n_v,
        edges=em,
        mass_removed=round(float(ngmass[:kk].sum() / total), 4),
        mass_cum_in_58=round(float(ngmass[:kk].sum() / ngmass.sum()), 4))
    assert not np.isin(dng100_all, drop).any(), f"DNg100 in ng-k{kk} (STOP)"
# endpoint identity: k58 IS the cut58 arm (set + n + edges recomputed)
assert ngl["k58"]["drop_ids"] == [int(x) for x in np.sort(ng_desc)]
keep58 = keep_new.copy()
keep58[np.array(ngl["k58"]["drop_ids"], np.int64)] = False
assert int(keep58.sum()) == int(keep_new.sum()) - 58
assert ngl["k58"]["edges"] == int((keep58[src_all] & keep58[dst_all]).sum())
assert ngl["k58"]["mass_removed"] == mass_split["other58"] == 0.3921
pins["ngladder"] = ngl

# stored-arm edge pins re-derived for the C0S-form sanity (must equal stored)
pins["edges_stored"] = {
    "cut": int((keep_cut[src_all] & keep_cut[dst_all]).sum()),
    "n_cut": int(keep_cut.sum()), "n_new": int(keep_new.sum())}
assert pins["edges_stored"]["cut"] == ST["edges_cut"]

os.makedirs("l121", exist_ok=True)
json.dump(pins, open("l121/static.json", "w"), indent=1)
for kk in ("k19", "k29", "k39", "k58"):
    d = ngl[kk]
    print(f"ng-{kk}: n={d['n']} edges={d['edges']} "
          f"mass_removed={d['mass_removed']} cum_in_58={d['mass_cum_in_58']}")
print("ng top-5 ids:", ngl["ng58_ids_desc_mass"][:5],
      "mass:", ngl["ng58_cell_mass_share"][:5])
print("k5 pin (stored-form):", ladder["k5"])
print("l121/static.json written")
