"""L133 STATIC derivation (zero rollouts): wA-plus-319-alone XOR pins.

Extraction VERBATIM from l131_static.py (l113 form), then:
  - re-pin k19/k29/k58 == l121/static.json EXACT (extraction regression);
  - re-pin ALL l126 prefixes + l131 prefixes (wA/23/25/26) == stored EXACT;
  - re-pin rank ids/masses == l131/static.json EXACT (1110 / 319 twins);
  - NEW pin cutng25p = wA + rank 26 (id 319) ONLY — NOT a prefix (skips
    rank 25 / id 1110): the L133 XOR arm;
  - set identities: 25p ∪ {1110} == ng25, ng25 ∪ {319} == 25p,
    25p ⊂ ng26 (26 = 25p + 1110), wA ⊂ 25p; DNg100 in NO drop.
Writes l133/static.json for the PREREG pins. Deterministic, no RNG.
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
S123 = json.load(open("l123/static.json"))
S126 = json.load(open("l126/static.json"))
S131 = json.load(open("l131/static.json"))

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

# ---------------- L133: XOR pin ----------------
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

cut58_drop = np.sort(ng_desc)          # the 58 non-glut heavy (cut58 drop)
assert len(cut58_drop) == 58

k29_mass_share = float(ngmass[:29].sum() / total)
assert round(k29_mass_share, 4) == 0.2588, k29_mass_share

# re-pin ALL l126 + l131 prefixes == stored EXACT (extraction regression)
for _a, _pin in S126["prefix"].items():
    _k = _pin["k"]
    _drop = np.sort(ng_desc[:_k])
    assert [int(x) for x in _drop] == _pin["drop_ids"], (_a, "drop drift (STOP)")
    assert _pin["mass_removed"] == round(float(ngmass[:_k].sum() / total), 4), \
        (_a, "mass drift (STOP)")
for _a, _pin in S131["prefix"].items():
    _k = _pin["k"]
    _drop = np.sort(ng_desc[:_k])
    assert [int(x) for x in _drop] == _pin["drop_ids"], (_a, "drop drift (STOP)")
    assert _pin["mass_removed"] == round(float(ngmass[:_k].sum() / total), 4), \
        (_a, "mass drift (STOP)")
print("k19/k29/k58 + ALL l126/l131 prefixes re-pinned == stored EXACT")

# rank identification re-pinned == l131/static.json EXACT
rank25_id, rank26_id = int(ng_desc[24]), int(ng_desc[25])
rank25_mass = float(ngmass[24] / total)
rank26_mass = float(ngmass[25] / total)
assert rank25_id == S131["rank_ids"]["rank25"] == 1110
assert rank26_id == S131["rank_ids"]["rank26"] == 319
assert rank25_mass == S131["rank_mass"]["rank25"]
assert rank26_mass == S131["rank_mass"]["rank26"]
print(f"rank twins re-pinned: 1110 m {rank25_mass:.6f} / "
      f"319 m {rank26_mass:.6f}")

pins = {"mass_split": mass_split,
        "k29_window_mass": round(k29_mass_share, 4),
        "rank_ids": {"rank25": rank25_id, "rank26": rank26_id},
        "rank_mass": {"rank25": rank25_mass, "rank26": rank26_mass,
                      "pair_delta": abs(rank25_mass - rank26_mass)},
        "design": ("L133 wA-plus-319-alone XOR: cutng25p = wA + rank 26 "
                   "(id 319) ONLY — NOT a prefix (skips rank 25 / 1110). "
                   "If 25p PARTIALs -> clean identity XOR at mass-match "
                   "(L120 cell-204 claim upgrades to mass-matched); if "
                   "SUPERs -> flip position-thin, both cells complete. "
                   "wA < 25p < 26. DNg100 in no drop. Deterministic, no RNG.")}

# ---------------- NEW: the 25p XOR pin ----------------
drop_wA = np.sort(ng_desc[:24])
drop_25 = np.sort(ng_desc[:25])
drop_26 = np.sort(ng_desc[:26])
drop_25p = np.sort(np.concatenate([ng_desc[:24], ng_desc[25:26]]))
assert len(drop_25p) == 25
_ids25p = set(int(x) for x in drop_25p)
assert set(int(x) for x in drop_wA) < _ids25p, "wA not nested in 25p (STOP)"
assert _ids25p < set(int(x) for x in drop_26), "25p not nested in 26 (STOP)"
assert (set(int(x) for x in drop_25) | {319}) - {1110} == _ids25p, \
    "25+319-1110 != 25p (STOP)"
assert _ids25p - {319} == set(int(x) for x in drop_wA), "25p-319 != wA (STOP)"
assert np.isin(drop_25p, cut58_drop).all()
_keep25p = keep_new.copy()
_keep25p[drop_25p] = False
_n25p = int(_keep25p.sum())
_em25p = int((_keep25p[src_all] & _keep25p[dst_all]).sum())
assert _n25p == int(keep_new.sum()) - 25, _n25p
assert not np.isin(dng100_all, drop_25p).any(), "DNg100 in 25p drop (STOP)"
_mr25p = float((ngmass[:24].sum() + ngmass[25]) / total)
pins["xor25p"] = {"cutng25p": dict(
    drop_ids=[int(x) for x in drop_25p], n=_n25p, edges=_em25p,
    mass_removed=round(_mr25p, 4), mass_full=_mr25p,
    delta_vs_ng25=round(_mr25p - float(ngmass[:25].sum() / total), 6))}
print(f"cutng25p (wA + 319): n={_n25p} edges={_em25p} "
      f"mass_removed={_mr25p:.4f} (ng25 delta "
      f"{_mr25p - float(ngmass[:25].sum() / total):+.6f})  [NEW — XOR arm]")

pins["edges_stored"] = {
    "cut": int((keep_cut[src_all] & keep_cut[dst_all]).sum()),
    "n_cut": int(keep_cut.sum()), "n_new": int(keep_new.sum())}
assert pins["edges_stored"]["cut"] == ST["edges_cut"]

os.makedirs("l133", exist_ok=True)
json.dump(pins, open("l133/static.json", "w"), indent=1)
print("l133/static.json written")
