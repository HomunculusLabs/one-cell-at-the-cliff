"""L120 run: cutk4-disambiguation. PREREG l120/PREREG.md FIRST.

L119 machinery VERBATIM (5-pair pools, graphs, gains, draw order); arms
full/b65/cut/cut19/cut58 retained as ANCHORS (stored seeds 801/901 vs
raw_l113) + ladder arms cutk3/cutk4a/cutk4b/cutk5 = closure minus
positional drops of the glut_desc mass-DESC order: k3 [286,313,561],
k4a [204,286,313,561] (4th heaviest), k4b [286,313,561,32014] (5th),
k5 all five — k4a/k4b MASS-MATCHED by construction (delta .0001 rounded,
9.2e-05 unrounded; l120/static.json pins; k3/k5 == l119 stored EXACT).
NO RNG draw arm. Seeds: [801, 901] + FRESH B15 1901-1916 (asserted
absent from raw_l113 + l115 + l117 + l118 + l119). g_cut/g_cut19/g_cut58/
g_cutk5 AND g_cutk3 (l119 fresh gain, NEW stored-form anchor) re-bisected
+ asserted == stored EXACT; cutk4a/cutk4b gains bisected FRESH (staircase
+ band DISCLOSED, never asserted). C0A-119: cutk3/cutk5 bit-anchored vs
raw_l119 at 801/901. CPU-only; raw checkpoint BEFORE analysis.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
BETA, D = 2.0, 0.2
ENT_AMP = 0.1
G_NEW, G65 = 0.153125, 0.14
GH = G_NEW
AF_T = 0.10905611018339793
ARMS = ["full", "b65", "cut", "cut19", "cut58",
        "cutk3", "cutk4a", "cutk4b", "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutk3=None, cutk4a=None, cutk4b=None, cutk5=None)
G_CUT19_STORED = 0.15096808075904844  # l111 stored, PREREG C0A(c19)
G_CUT_STORED = 0.14510760426521305  # l107 stored, PREREG C0A(c)
G_CUT58_STORED = 0.15417299151420596  # l113 stored, PREREG C0A(c58)
G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)
G_CUTK3_STORED = 0.17404209494590758  # l119 stored fresh gain, C0A(k3)
ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B15 = list(range(1901, 1917))       # fresh, absent l113/l115/l117/l118/l119
SEEDS = ANCH + B15                  # anchors FIRST: early wiring verdict
FRESH = B15
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S101 = json.load(open("l101/static.json"))["sizes"]
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- extraction (l94_run.py verbatim) ----------------
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

# cut rule (l107/static.json): closure minus top-K dn_new by cord out-mass
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

reg_ann = region
sup_ann = sup
tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup_ann == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup_ann == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup_ann == "sensory")
                   & (reg_ann == "ventral_nerve_cord")]] = "vnc_sensory"
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
# L111: glutamatergic subset of the heavy-77 (l110 addendum: 19/77, z +5.9)
heav = dn_new_g[order[:K]]
cut19_drop = np.sort(heav[is_glut[heav]])
assert len(cut19_drop) == 19, f"glut heavy = {len(cut19_drop)} != 19 (STOP)"
keep_cut19 = keep_new.copy()
keep_cut19[cut19_drop] = False
n_cut19 = int(keep_cut19.sum())
assert n_cut19 == int(keep_new.sum()) - 19
_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))
# L113: NON-glutamatergic subset of the heavy-77 (mirror of L111's cut19)
cut58_drop = np.sort(heav[~is_glut[heav]])
assert len(cut58_drop) == 58, f"non-glut heavy = {len(cut58_drop)} != 58 (STOP)"
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split
keep_cut58 = keep_new.copy()
keep_cut58[cut58_drop] = False
n_cut58 = int(keep_cut58.sum())
assert n_cut58 == int(keep_new.sum()) - 58
# L119: minimal glut subset — k HEAVIEST glut cells (deterministic
# mass-desc positional filter; l119/static.json pins; k5 asserted ==
# l117 stored) + pinned-RNG random 5-of-19-glut draw (seed 1190).
S120 = json.load(open("l120/static.json"))
NEW_ARMS = ("cutk3", "cutk4a", "cutk4b", "cutk5")
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
keep_cutk, n_cutk, cutk_drop, cutk_pins = {}, {}, {}, {}
for _pk, _a, _pos in (("k3", "cutk3", [0, 1, 2]),
                      ("k4a", "cutk4a", [0, 1, 2, 3]),
                      ("k4b", "cutk4b", [0, 1, 2, 4]),
                      ("k5", "cutk5", [0, 1, 2, 3, 4])):
    _pin = S120["ladder"][_pk]
    _drop = np.sort(glut_desc[_pos])
    assert len(_drop) == len(_pos)
    assert np.isin(_drop, cut19_drop).all(), "ladder drop not subset of glut-19"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
assert [int(x) for x in cutk_drop["cutk4a"]] == [204, 286, 313, 561]
assert [int(x) for x in cutk_drop["cutk4b"]] == [286, 313, 561, 32014]
assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]
assert cutk_pins["cutk4a"]["mass_removed"] == 0.0347, "k4a mass drift (STOP)"
assert cutk_pins["cutk4b"]["mass_removed"] == 0.0346, "k4b mass drift (STOP)"
assert cutk_pins["cutk5"]["mass_removed"] == 0.0425, "k5 mass drift (STOP)"
assert cutk_pins["cutk3"]["edges"] == 647526, "k3 edges drift (STOP)"
assert cutk_pins["cutk5"]["edges"] == 647252, "k5 edges drift (STOP)"
# (DNg100-not-in-heavy-77 asserted downstream in the dng100 section + pinned
# in l120/static.json — dng100_all is not yet defined at this point.)


def build(keep):
    emask = keep[src_all] & keep[dst_all]
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a2 = sign_all[gsrc]
    gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)
    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([ldst, lsrc])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W, loc


def wb(W):
    neg = W.values() < 0
    vals = W.values().clone()
    vals[neg] *= BETA
    return torch.sparse_csr_tensor(W.crow_indices(), W.col_indices(), vals, W.shape)


Wc_o, loc_o = build(keep_old)
Wc_n, loc_n = build(keep_new)
Wc_c, loc_c = build(keep_cut)
Wc_c19, loc_c19 = build(keep_cut19)
Wc_c58, loc_c58 = build(keep_cut58)
Wc_k4a, loc_k4a = build(keep_cutk["cutk4a"])
Wc_k4b, loc_k4b = build(keep_cutk["cutk4b"])
Wc_k3, loc_k3 = build(keep_cutk["cutk3"])
Wc_k5, loc_k5 = build(keep_cutk["cutk5"])
assert Wc_k4a.values().numel() == cutk_pins["cutk4a"]["edges"]
assert Wc_k4b.values().numel() == cutk_pins["cutk4b"]["edges"]
assert Wc_k3.values().numel() == cutk_pins["cutk3"]["edges"]
assert Wc_k5.values().numel() == cutk_pins["cutk5"]["edges"]
assert Wc_o.values().numel() == S92["edges_old"]
assert Wc_n.values().numel() == S92["edges_new"]
assert Wc_c.values().numel() == ST["edges_cut"]
Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),
                                    wb(Wc_c19), wb(Wc_c58))
Wb_k4a, Wb_k4b, Wb_k3, Wb_k5 = (wb(Wc_k4a), wb(Wc_k4b), wb(Wc_k3), wb(Wc_k5))

n_old, n_new, n_cut = int(keep_old.sum()), int(keep_new.sum()), int(keep_cut.sum())
n_add = len(dn_new_g)
new_g = dn_new_g
old_pos_in_new = loc_n[gi_old]
new_pos = loc_n[new_g]
old_pos_in_cut = loc_c[gi_old]
gi_cut = np.where(keep_cut)[0]
cut_pos_in_new = loc_n[gi_cut]
kept_new_mask = keep_cut[new_g]                      # new_g order
kept_new_cut = loc_c[new_g[kept_new_mask]]           # cut-local of kept new
gi_cut19 = np.where(keep_cut19)[0]
cut19_pos_in_new = loc_n[gi_cut19]
old_pos_in_c19 = loc_c19[gi_old]
kept_new_mask19 = keep_cut19[new_g]                  # new_g order
kept_new_cut19 = loc_c19[new_g[kept_new_mask19]]     # cut19-local of kept new
gi_cut58 = np.where(keep_cut58)[0]
cut58_pos_in_new = loc_n[gi_cut58]
old_pos_in_c58 = loc_c58[gi_old]
kept_new_mask58 = keep_cut58[new_g]                  # new_g order
kept_new_cut58 = loc_c58[new_g[kept_new_mask58]]     # cut58-local of kept new
gi_k4a = np.where(keep_cutk["cutk4a"])[0]
k1_pos_in_new = loc_n[gi_k4a]
old_pos_in_k4a = loc_k4a[gi_old]
kept_new_mask_k4a = keep_cutk["cutk4a"][new_g]
kept_new_cutk4a = loc_k4a[new_g[kept_new_mask_k4a]]
gi_k4b = np.where(keep_cutk["cutk4b"])[0]
k2_pos_in_new = loc_n[gi_k4b]
old_pos_in_k4b = loc_k4b[gi_old]
kept_new_mask_k4b = keep_cutk["cutk4b"][new_g]
kept_new_cutk4b = loc_k4b[new_g[kept_new_mask_k4b]]
gi_k3 = np.where(keep_cutk["cutk3"])[0]
k3_pos_in_new = loc_n[gi_k3]
old_pos_in_k3 = loc_k3[gi_old]
kept_new_mask_k3 = keep_cutk["cutk3"][new_g]
kept_new_cutk3 = loc_k3[new_g[kept_new_mask_k3]]
gi_k5 = np.where(keep_cutk["cutk5"])[0]
k5_pos_in_new = loc_n[gi_k5]
old_pos_in_k5 = loc_k5[gi_old]
kept_new_mask_k5 = keep_cutk["cutk5"][new_g]
kept_new_cutk5 = loc_k5[new_g[kept_new_mask_k5]]

# pools / mech / motor / dng100 per graph
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


def pools_for(loc, keep):
    out = {}
    # L116: 5 semantic pairs (l101/l101_run.py patterns VERBATIM); Ti/Tr
    # keep f/e names (C0A key match), new pairs use l101 a/b names.
    for k, fpat, epat, pf, pe in [
        ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor"),
         "f", "e"),
        ("Tr", has("trochanter") & has("flexor"),
         has("trochanter") & has("extensor"), "f", "e"),
        ("Ta", has("tarsus") & has("depressor"), has("tarsus") & has("levator"),
         "a", "b"),
        ("Sr", has("sternal") & has("anterior") & has("rotator"),
         has("sternal") & has("posterior") & has("rotator"), "a", "b"),
        ("Pr", has("promotor"), has("remotor"), "a", "b"),
    ]:
        for c in ("L", "R"):
            m = keep[mgi] & fpat & (side_m == SIDE_MAP[c])
            out[f"{k}_{pf}{c}"] = np.sort(loc[mgi[m]])
            m = keep[mgi] & epat & (side_m == SIDE_MAP[c])
            out[f"{k}_{pe}{c}"] = np.sort(loc[mgi[m]])
    return out


POOLS = {"full": pools_for(loc_n, keep_new), "cut": pools_for(loc_c, keep_cut),
         "cut19": pools_for(loc_c19, keep_cut19),
         "cut58": pools_for(loc_c58, keep_cut58),
         "cutk4a": pools_for(loc_k4a, keep_cutk["cutk4a"]),
         "cutk4b": pools_for(loc_k4b, keep_cutk["cutk4b"]),
         "cutk3": pools_for(loc_k3, keep_cutk["cutk3"]),
         "cutk5": pools_for(loc_k5, keep_cutk["cutk5"]),
         "b65": pools_for(loc_o, keep_old)}
for pk, want in S92["pool_sizes"].items():
    assert len(POOLS["full"][pk]) == want, pk
    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk
    for _da in ("cutk3", "cutk4a", "cutk4b", "cutk5"):
        assert len(POOLS[_da][pk]) == want, (_da, pk)
# L116 NEW pools: sizes == l101 static, all arms (drops are DNs, never motor)
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue  # covered above via the f/e form + cross-check below
    assert len(POOLS["full"][pk]) == want, pk
    for a in ("cut", "cut19", "cut58", "cutk4a", "cutk4b", "cutk3",
              "cutk5", "b65"):
        assert len(POOLS[a][pk]) == want, (a, pk)
# cross-check: l101 a/b sizes == l92 f/e sizes (extraction drift tripwire)
for k, (ag, bg) in {"Ti": ("f", "e"), "Tr": ("f", "e")}.items():
    for sd in ("L", "R"):
        assert len(POOLS["full"][f"{k}_{ag}{sd}"]) == S101[f"{k}_a{sd}"], (k, sd)
        assert len(POOLS["full"][f"{k}_{bg}{sd}"]) == S101[f"{k}_b{sd}"], (k, sd)

cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech = {"full": np.where(mech_mask[keep_new])[0],
        "cut": np.where(mech_mask[keep_cut])[0],
        "cut19": np.where(mech_mask[keep_cut19])[0],
        "cut58": np.where(mech_mask[keep_cut58])[0],
        "cutk4a": np.where(mech_mask[keep_cutk["cutk4a"]])[0],
        "cutk4b": np.where(mech_mask[keep_cutk["cutk4b"]])[0],
        "cutk3": np.where(mech_mask[keep_cutk["cutk3"]])[0],
        "cutk5": np.where(mech_mask[keep_cutk["cutk5"]])[0],
        "b65": np.where(mech_mask[keep_old])[0]}
assert len(mech["full"]) == S92["mech"]

mg_all = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("cutk4a", n_cutk["cutk4a"]), ("cutk4b", n_cutk["cutk4b"]),
          ("cutk3", n_cutk["cutk3"]), ("cutk5", n_cutk["cutk5"]),
          ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cut58", keep_cut58, loc_c58),
                     ("cutk4a", keep_cutk["cutk4a"], loc_k4a),
                     ("cutk4b", keep_cutk["cutk4b"], loc_k4b),
                     ("cutk3", keep_cutk["cutk3"], loc_k3),
                     ("cutk5", keep_cutk["cutk5"], loc_k5),
                     ("b65", keep_old, loc_o)):
    motor[a][loc[mg_all[keep[mg_all]]]] = True

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100 = {"full": np.sort(loc_n[dng100_all[keep_new[dng100_all]]]),
          "cut": np.sort(loc_c[dng100_all[keep_cut[dng100_all]]]),
          "cut19": np.sort(loc_c19[dng100_all[keep_cut19[dng100_all]]]),
          "cut58": np.sort(loc_c58[dng100_all[keep_cut58[dng100_all]]]),
          "cutk4a": np.sort(loc_k4a[dng100_all[keep_cutk["cutk4a"][dng100_all]]]),
          "cutk4b": np.sort(loc_k4b[dng100_all[keep_cutk["cutk4b"][dng100_all]]]),
          "cutk3": np.sort(loc_k3[dng100_all[keep_cutk["cutk3"][dng100_all]]]),
          "cutk5": np.sort(loc_k5[dng100_all[keep_cutk["cutk5"][dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]
# L115/L117/L118 pin: no DNg100 cell sits in the heavy-77 (draw drops
# cannot touch the drive channel) — STOP if violated.
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"
for _da in ("cutk3", "cutk4a", "cutk4b", "cutk5"):
    assert len(dng100[_da]) == S92["dng100"], _da
WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "cutk4a": Wb_k4a, "cutk4b": Wb_k4b, "cutk3": Wb_k3, "cutk5": Wb_k5,
      "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "cutk4a": n_cutk["cutk4a"], "cutk4b": n_cutk["cutk4b"],
        "cutk3": n_cutk["cutk3"], "cutk5": n_cutk["cutk5"],
        "b65": n_old}

AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
log(f"graphs built {time.time()-t0:.0f}s | K {K} n_cut {n_cut:,} "
    f"edges_cut {Wc_c.values().numel():,}")


# ---------------- settle machinery (l94 two-generator form) ----------------
def settle_states(seed, gains):
    """Draw per l94 order; settle all arms under `gains[arm]`."""
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Xc_full = torch.zeros(n_new, 1)
    Xc_full[old_pos_in_new] = X0o
    Xc_full[new_pos] = X0n
    Xc_cut = torch.zeros(n_cut, 1)
    Xc_cut[old_pos_in_cut] = X0o
    Xc_cut[kept_new_cut] = X0n[kept_new_mask]
    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xc_k4a = torch.zeros(n_cutk["cutk4a"], 1)
    Xc_k4a[old_pos_in_k4a] = X0o
    Xc_k4a[kept_new_cutk4a] = X0n[kept_new_mask_k4a]
    Xc_k4b = torch.zeros(n_cutk["cutk4b"], 1)
    Xc_k4b[old_pos_in_k4b] = X0o
    Xc_k4b[kept_new_cutk4b] = X0n[kept_new_mask_k4b]
    Xc_k3 = torch.zeros(n_cutk["cutk3"], 1)
    Xc_k3[old_pos_in_k3] = X0o
    Xc_k3[kept_new_cutk3] = X0n[kept_new_mask_k3]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xo65 = X0o.clone()
    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
              cutk4a=Xc_k4a.clone(), cutk4b=Xc_k4b.clone(),
              cutk3=Xc_k3.clone(), cutk5=Xc_k5.clone(),
              b65=Xo65.clone())
    I = {}
    for a in ARMS:
        Iv = torch.zeros(N_OF[a], 1)
        Iv[dng100[a]] = D
        I[a] = Iv
    sp = 0.0
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cut58=nzn[cut58_pos_in_new],
                     cutk4a=nzn[k1_pos_in_new],
                     cutk4b=nzn[k2_pos_in_new],
                     cutk3=nzn[k3_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     b65=nz_o)
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], st[a]) * gains[a] + I[a]
            drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            st[a] = st[a] + (DT / TAU) * ((torch.relu(drive + BG) + noise[a])
                                          .clamp(max=RMAX) - st[a])
    return st


def af_of(st):
    return {a: float((st[a] > 0.05).float().mean()) for a in ARMS}


# ---------------- P1 bisect for g_cut (l92 form, settle-only) ----------------
ANCH = [11, 22, 33]
lo_g, hi_g = 0.12, 0.18


def bisect_af_mean(g, arm="cut"):
    afs = []
    for s in ANCH:
        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutk4a=g, cutk4b=g, cutk3=g,
                                  cutk5=g))
        afs.append(float((st[arm] > 0.05).float().mean()))
    return float(np.mean(afs))


af_lo, af_hi = bisect_af_mean(lo_g), bisect_af_mean(hi_g)
log(f"bisect bracket af({lo_g})={af_lo:.5f} af({hi_g})={af_hi:.5f} "
    f"target {AF_T:.5f}")
assert af_lo < AF_T < af_hi, "bracket fail"
for it in range(24):
    mid = (lo_g + hi_g) / 2
    if bisect_af_mean(mid) < AF_T:
        lo_g = mid
    else:
        hi_g = mid
GAIN["cut"] = lo_g
af_final = bisect_af_mean(lo_g)
# C0A(c): deterministic re-bisect must land on the stored l107 gain EXACTLY
assert GAIN["cut"] == G_CUT_STORED, (GAIN["cut"], G_CUT_STORED)
log(f"g_cut {lo_g:.6f} == stored EXACT | af_final {af_final:.6f} "
    f"({time.time()-t0:.0f}s)")

# L111: fresh bisect for the cut19 subnet (staircase disclosed)
lo2, hi2 = 0.12, 0.18
af_lo2, af_hi2 = bisect_af_mean(lo2, "cut19"), bisect_af_mean(hi2, "cut19")
log(f"cut19 bracket af({lo2})={af_lo2:.5f} af({hi2})={af_hi2:.5f} "
    f"target {AF_T:.5f}")
assert af_lo2 < AF_T < af_hi2, "cut19 bracket fail"
for it in range(24):
    mid = (lo2 + hi2) / 2
    if bisect_af_mean(mid, "cut19") < AF_T:
        lo2 = mid
    else:
        hi2 = mid
GAIN["cut19"] = lo2
af_final19 = bisect_af_mean(lo2, "cut19")
# C0A(c19): deterministic re-bisect must land on the stored l111 gain EXACT
assert GAIN["cut19"] == G_CUT19_STORED, (GAIN["cut19"], G_CUT19_STORED)
log(f"g_cut19 {lo2:.6f} == stored EXACT | af_final19 {af_final19:.6f} "
    f"|af-target| {abs(af_final19 - AF_T):.2e} (staircase disclosed)")

# L113: fresh bisect for the cut58 subnet (staircase disclosed)
lo3, hi3 = 0.12, 0.18
af_lo3, af_hi3 = bisect_af_mean(lo3, "cut58"), bisect_af_mean(hi3, "cut58")
log(f"cut58 bracket af({lo3})={af_lo3:.5f} af({hi3})={af_hi3:.5f} "
    f"target {AF_T:.5f}")
assert af_lo3 < AF_T < af_hi3, "cut58 bracket fail"
for it in range(24):
    mid = (lo3 + hi3) / 2
    if bisect_af_mean(mid, "cut58") < AF_T:
        lo3 = mid
    else:
        hi3 = mid
GAIN["cut58"] = lo3
af_final58 = bisect_af_mean(lo3, "cut58")
# C0A(c58): deterministic re-bisect must land on the stored l113 gain EXACT
assert GAIN["cut58"] == G_CUT58_STORED, (GAIN["cut58"], G_CUT58_STORED)
log(f"g_cut58 {lo3:.6f} == l113 stored EXACT | af_final58 {af_final58:.6f} "
    f"|af-target| {abs(af_final58 - AF_T):.2e} (staircase disclosed)")

# L119: cutk5 re-bisect must land on the stored l117 dose gain EXACT
lo4, hi4 = 0.12, 0.18
af_lo4, af_hi4 = bisect_af_mean(lo4, "cutk5"), bisect_af_mean(hi4, "cutk5")
log(f"cutk5 bracket af({lo4})={af_lo4:.5f} af({hi4})={af_hi4:.5f} "
    f"target {AF_T:.5f}")
assert af_lo4 < AF_T < af_hi4, "cutk5 bracket fail"
for it in range(24):
    mid = (lo4 + hi4) / 2
    if bisect_af_mean(mid, "cutk5") < AF_T:
        lo4 = mid
    else:
        hi4 = mid
GAIN["cutk5"] = lo4
af_finalk5 = bisect_af_mean(lo4, "cutk5")
assert GAIN["cutk5"] == G_CUTK5_STORED, (GAIN["cutk5"], G_CUTK5_STORED)
log(f"g_cutk5 {lo4:.6f} == l117 stored EXACT | af_finalk5 {af_finalk5:.6f} "
    f"|af-target| {abs(af_finalk5 - AF_T):.2e} (staircase disclosed)")

# L120: cutk3 re-bisect must land on the stored l119 fresh gain EXACTLY
lo5, hi5 = 0.12, 0.18
af_lo5, af_hi5 = bisect_af_mean(lo5, "cutk3"), bisect_af_mean(hi5, "cutk3")
log(f"cutk3 bracket af({lo5})={af_lo5:.5f} af({hi5})={af_hi5:.5f} "
    f"target {AF_T:.5f}")
assert af_lo5 < AF_T < af_hi5, "cutk3 bracket fail"
for it in range(24):
    mid = (lo5 + hi5) / 2
    if bisect_af_mean(mid, "cutk3") < AF_T:
        lo5 = mid
    else:
        hi5 = mid
GAIN["cutk3"] = lo5
af_finalk3 = bisect_af_mean(lo5, "cutk3")
assert GAIN["cutk3"] == G_CUTK3_STORED, (GAIN["cutk3"], G_CUTK3_STORED)
log(f"g_cutk3 {lo5:.6f} == l119 stored EXACT | af_finalk3 {af_finalk3:.6f} "
    f"|af-target| {abs(af_finalk3 - AF_T):.2e} (staircase disclosed)")

# L118: fresh bisects for the draw arms (no stored form; staircase + band
# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an abort)
new_stairs = {}
for _a in ("cutk4a", "cutk4b"):
    lo_d, hi_d = 0.12, 0.18
    af_lo_d, af_hi_d = bisect_af_mean(lo_d, _a), bisect_af_mean(hi_d, _a)
    log(f"{_a} bracket af({lo_d})={af_lo_d:.5f} af({hi_d})={af_hi_d:.5f} "
        f"target {AF_T:.5f}")
    assert af_lo_d < AF_T < af_hi_d, f"{_a} bracket fail"
    for it in range(24):
        mid = (lo_d + hi_d) / 2
        if bisect_af_mean(mid, _a) < AF_T:
            lo_d = mid
        else:
            hi_d = mid
    GAIN[_a] = lo_d
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    _band = " [OUTSIDE PREREG band .14-.16 — DISCLOSED]" \
        if not (0.14 <= lo_d <= 0.16) else ""
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")

# ---------------- rollouts ----------------
store = {}
if os.path.exists("l120/raw_partial.npz"):
    z = np.load("l120/raw_partial.npz")
    store = {k: z[k] for k in z.files}
for seed in SEEDS:
    if f"mm_full_{seed}" in store:
        log(f"seed {seed} cached, skip")
        continue
    # l94 draw order, ONE generator pair across settle+WIN (contiguous)
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Xc_full = torch.zeros(n_new, 1)
    Xc_full[old_pos_in_new] = X0o
    Xc_full[new_pos] = X0n
    Xc_cut = torch.zeros(n_cut, 1)
    Xc_cut[old_pos_in_cut] = X0o
    Xc_cut[kept_new_cut] = X0n[kept_new_mask]
    Xc_cut19 = torch.zeros(n_cut19, 1)
    Xc_cut19[old_pos_in_c19] = X0o
    Xc_cut19[kept_new_cut19] = X0n[kept_new_mask19]
    Xc_cut58 = torch.zeros(n_cut58, 1)
    Xc_cut58[old_pos_in_c58] = X0o
    Xc_cut58[kept_new_cut58] = X0n[kept_new_mask58]
    Xc_k4a = torch.zeros(n_cutk["cutk4a"], 1)
    Xc_k4a[old_pos_in_k4a] = X0o
    Xc_k4a[kept_new_cutk4a] = X0n[kept_new_mask_k4a]
    Xc_k4b = torch.zeros(n_cutk["cutk4b"], 1)
    Xc_k4b[old_pos_in_k4b] = X0o
    Xc_k4b[kept_new_cutk4b] = X0n[kept_new_mask_k4b]
    Xc_k3 = torch.zeros(n_cutk["cutk3"], 1)
    Xc_k3[old_pos_in_k3] = X0o
    Xc_k3[kept_new_cutk3] = X0n[kept_new_mask_k3]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xo65 = X0o.clone()
    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             cutk4a=Xc_k4a.clone(), cutk4b=Xc_k4b.clone(),
             cutk3=Xc_k3.clone(), cutk5=Xc_k5.clone(),
             b65=Xo65.clone())
    Iv = {}
    for a in ARMS:
        v = torch.zeros(N_OF[a], 1)
        v[dng100[a]] = D
        Iv[a] = v
    sp = 0.0
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cut58=nzn[cut58_pos_in_new],
                     cutk4a=nzn[k1_pos_in_new],
                     cutk4b=nzn[k2_pos_in_new],
                     cutk3=nzn[k3_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     b65=nz_o)
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            X[a] = X[a] + (DT / TAU) * ((torch.relu(drive + BG) + noise[a])
                                        .clamp(max=RMAX) - X[a])
    af_c = {a: float((X[a] > 0.05).float().mean()) for a in ARMS}
    for a in ARMS:
        assert 0.01 < af_c[a] < 0.9, (a, af_c[a])
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {kk: np.zeros(WIN, np.float32) for kk in POOLS[a]} for a in ARMS}
    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        noise = dict(full=nzn, cut=nzn[cut_pos_in_new],
                     cut19=nzn[cut19_pos_in_new],
                     cut58=nzn[cut58_pos_in_new],
                     cutk4a=nzn[k1_pos_in_new],
                     cutk4b=nzn[k2_pos_in_new],
                     cutk3=nzn[k3_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     b65=nz_o)
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if sin_t > 0:
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            t = torch.relu(drive + BG)
            t = (t + noise[a]).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
        for a in ARMS:
            mm[a][k] = X[a][motor[a]].mean()
            xm[a][k] = X[a][mech[a]].mean()
            for kk in POOLS[a]:
                tr[a][kk][k] = X[a][POOLS[a][kk]].mean()
    for a in ARMS:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        for kk in POOLS[a]:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_c[a])
    np.savez("l120/raw_partial.npz", **store)
    log(f"seed {seed} done af {af_c} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l120/raw_l120.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_cutk5=GAIN["cutk5"],
                    g_cutk4a=GAIN["cutk4a"], g_cutk4b=GAIN["cutk4b"],
                    g_cutk3=GAIN["cutk3"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutk4a_drop=cutk_drop["cutk4a"], cutk4b_drop=cutk_drop["cutk4b"],
                    cutk3_drop=cutk_drop["cutk3"], cutk5_drop=cutk_drop["cutk5"],
                    new_mass=np.array([cutk_pins[a]["mass_removed"] for a in NEW_ARMS]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l120.npz checkpointed BEFORE analysis")

# ---------------- C0A (PREREG): FULL-BATCH anchors vs raw_l113 ----------------
# Enumerated OLD keys only (L59 anchor-key rule): the 8 Ti/Tr pools + mm/xm.
# New Ta/Sr/Pr keys do not exist in z113 and are excluded BY NAME.
zprev = np.load("l113/raw_l113.npz")
C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                           for c in ("f", "e") for s in ("L", "R")]
assert all(f"{k}_full_801" in zprev.files for k in C0A_KEYS)
# B15 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B15), \
    "B15 collides with stored batches (STOP)"
for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz", "l119/raw_l119.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B15), \
        ("B15 collides with " + _prev + " (STOP)")
STORED_ARMS = ("full", "b65", "cut", "cut19", "cut58")
c0a = {}
for s in (801, 901):  # stored seeds only: anchors vs raw_l113
    for key in C0A_KEYS:
        for a in STORED_ARMS:
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
    for a in STORED_ARMS:
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))
# C0A-119 (NEW anchor class): cutk3/cutk5 at stored seeds vs raw_l119.
# l119 ran every arm at all 18 seeds, so these two arms have stored
# counterparts on ALL pool keys; cutk4a/cutk4b have NONE (excluded by name).
z119 = np.load("l119/raw_l119.npz")
_c0a119_poolkeys = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _c0a119_poolkeys.append(f"{_pk}_{_c}{_s}")
C0A119_KEYS = ["mm", "xm"] + _c0a119_poolkeys
assert all(f"{_k}_cutk3_801" in z119.files for _k in C0A119_KEYS)
c0a119 = {}
for s in (801, 901):
    for key in C0A119_KEYS:
        for a in ("cutk3", "cutk5"):
            c0a119[f"119_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z119[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk3", "cutk5"):
        c0a119[f"119_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z119[f"af_{a}_{s}"]))
c0a119_max = max(c0a119.values())
c0a119_pass = bool(all(v == 0.0 for v in c0a119.values()))
log(f"C0A-119 cutk3/cutk5 vs raw_l119: {'PASS' if c0a119_pass else 'FAIL'} "
    f"(max {c0a119_max:.1e}, {len(C0A119_KEYS)} keys x 2 arms x 2 seeds)")
c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}
                       - {"Ti", "Tr"})
log(f"C0A covered keys {len(C0A_KEYS)} x stored arms {len(STORED_ARMS)} "
    f"x anchor seeds 2 | NEW pools excluded by name: {c0a_new_pools} "
    f"| NEW arms excluded (no l113 counterpart): ['cutk3','cutk4a','cutk4b',"
    "'cutk5'] | cutk3/cutk5 additionally C0A-anchored vs raw_l119")
out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           g_cutk5_stored_exact=bool(GAIN["cutk5"] == G_CUTK5_STORED),
           g_cutk3_stored_exact=bool(GAIN["cutk3"] == G_CUTK3_STORED),
           g_cutk4a=GAIN["cutk4a"], g_cutk4b=GAIN["cutk4b"],
           g_cutk3=GAIN["cutk3"],
           new_stairs=new_stairs,
           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutk4a", "cutk4b"))),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           af_finalk5=af_finalk5, af_finalk3=af_finalk3,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           new_mass={a: cutk_pins[a]["mass_removed"] for a in NEW_ARMS},
           c0a_max=max(c0a.values()),
           c0a119_max=c0a119_max, c0a119_pass=c0a119_pass,
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a119_pass))
json.dump(out, open("l120/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")
