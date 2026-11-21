"""L123 STATIC derivation (zero rollouts): ng[19:29] window XOR pins.

Extraction VERBATIM from l121_static.py (l113 form), then:
  - re-pin k19/k29/k58 == l121/static.json EXACT (extraction regression);
  - NEW window arms: the 10 cells ng_desc[19:29] (mass-desc ranks 20-29,
    ids sorted {80,319,354,558,585,628,707,1110,32072,32271}) split in
    mass-desc halves:
      wA (cutwA) = ng_desc[:24]          (prefix: k19 + ranks 20-24, 24 cells)
      wB (cutwB) = ng_desc[:19] + ng_desc[24:29]  (k19 + ranks 25-29, 24 cells)
    Both drop 24 cells; masses differ (heavier half vs lighter half) —
    DISCLOSED beside the duty table, never matched.
  - set identities: wA_drop | wB_drop == k29 drop set EXACTLY; both subset
    of cut58; DNg100 not in any drop.
Writes l123/static.json for the PREREG pins. NO RNG anywhere in L123.
"""
import json
import os

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S121 = json.load(open("l121/static.json"))

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

# ---------------- L123: window pins ----------------
glut_desc = heav[is_glut[heav]]
ng_desc = heav[~is_glut[heav]]
assert len(glut_desc) == 19 and len(ng_desc) == 58
total = cell_mass.sum()
ngmass = cell_mass[order[:K]][~is_glut[heav]]           # ng_desc order
sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[(sub_dn.cell_type == "DNg100").to_numpy()].to_numpy()
assert not np.isin(dng100_all, heav).any(), "DNg100 in heavy-77 (STOP)"

# re-pin k19/k29/k58 == l121 stored EXACT (extraction regression)
for kk in (19, 29, 58):
    d = np.sort(ng_desc[:kk])
    want = S121["ngladder"][f"k{kk}"]["drop_ids"]
    assert [int(x) for x in d] == want, f"k{kk} drop drift (STOP)"

window = ng_desc[19:29]                                  # mass-desc ranks 20-29
assert len(window) == 10
wA_drop = np.sort(ng_desc[:24])                          # prefix, 24 cells
wB_drop = np.sort(np.concatenate([ng_desc[:19], ng_desc[24:29]]))
assert len(wA_drop) == len(wB_drop) == 24
assert np.isin(wA_drop, np.sort(ng_desc)).all()
assert np.isin(wB_drop, np.sort(ng_desc)).all()
# window set identity: the two halves partition the k29 window EXACTLY
k29_drop = np.array(S121["ngladder"]["k29"]["drop_ids"], np.int64)
union = np.union1d(wA_drop, wB_drop)
assert np.array_equal(union, k29_drop), "wA|wB != k29 window (STOP)"
inter = np.intersect1d(wA_drop, wB_drop)
assert np.array_equal(inter, np.sort(ng_desc[:19])), "halves overlap beyond k19 (STOP)"
assert not np.isin(dng100_all, wA_drop).any() and not np.isin(dng100_all, wB_drop).any()

pins = {"mass_split": mass_split,
        "window_ids_desc_mass": [int(x) for x in window],
        "window_cell_mass_share": [round(float(m / total), 5) for m in ngmass[19:29]],
        "wA_extra_desc": [int(x) for x in ng_desc[19:24]],
        "wB_extra_desc": [int(x) for x in ng_desc[24:29]]}
for name, drop, extra in (("wA", wA_drop, ng_desc[19:24]),
                          ("wB", wB_drop, ng_desc[24:29])):
    keep_v = keep_new.copy()
    keep_v[drop] = False
    n_v = int(keep_v.sum())
    assert n_v == int(keep_new.sum()) - 24
    em = int((keep_v[src_all] & keep_v[dst_all]).sum())
    mr = round(float((ngmass[:24].sum() if name == "wA"
                      else ngmass[:19].sum() + ngmass[24:29].sum()) / total), 4)
    pins[f"window_{name}"] = dict(
        drop_ids=[int(x) for x in drop],
        n=n_v, edges=em, mass_removed=mr,
        extra_ids_desc=[int(x) for x in extra],
        extra_mass=round(float(
            (ngmass[19:24].sum() if name == "wA" else ngmass[24:29].sum())
            / total), 4))
    print(f"window-{name}: n={n_v} edges={em} mass_removed={mr} "
          f"extra(d Mass-desc)={[int(x) for x in extra]}")

pins["edges_stored"] = {
    "cut": int((keep_cut[src_all] & keep_cut[dst_all]).sum()),
    "n_cut": int(keep_cut.sum()), "n_new": int(keep_new.sum())}
assert pins["edges_stored"]["cut"] == ST["edges_cut"]

os.makedirs("l123", exist_ok=True)
json.dump(pins, open("l123/static.json", "w"), indent=1)
print("window cells (mass-desc):", pins["window_ids_desc_mass"],
      "shares:", pins["window_cell_mass_share"])
print("halves extra mass: wA", pins["window_wA"]["extra_mass"],
      "wB", pins["window_wB"]["extra_mass"])
print("k19/k29/k58 re-pin == l121 stored EXACT; l123/static.json written")
