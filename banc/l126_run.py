"""L126 run: window-INTERPOLATION on FRESH B21. PREREG
l126/PREREG.md FIRST (positional prefixes ng_desc[:k], k in {21,23,26,28};
curves the k19-kill -> k29-super-raise transition INSIDE the window).

L124 machinery VERBATIM (pools, graphs, draw order) — cutwA RESTORED as
the k=24 point (stored gain, re-bisect EXACT); cutwB NOT run (2-batch
union complete; trimmed from C0A-123, DISCLOSED); cutng21/23/26/28 =
strictly nested prefixes (l126/static.json pins, wA re-pinned == l123
stored EXACT), FRESH bisects (staircase + band DISCLOSED). Re-rolled on
FRESH B21 2501-2516 (asserted absent from raw_l113 + l115 + l117 + l118
+ l119 + l120 + l121 + l122 + l123 + l124 + l125).
C0A-123 retained on 4 shared arms + NEW C0A-124 (4 arms incl wA) and
C0A-125 (3 arms) forward chains. CPU-only; raw checkpoint BEFORE
analysis.
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
        "cutng19", "cutng21", "cutng23", "cutwA", "cutng26", "cutng28",
        "cutng29", "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutng19=None, cutng21=None, cutng23=None, cutwA=None,
            cutng26=None, cutng28=None, cutng29=None, cutk5=None)
G_CUT19_STORED = 0.15096808075904844  # l111 stored, PREREG C0A(c19)
G_CUT_STORED = 0.14510760426521305  # l107 stored, PREREG C0A(c)
G_CUT58_STORED = 0.15417299151420596  # l113 stored, PREREG C0A(c58)
G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)
G_CUTNG19_STORED = 0.15025991678237915  # l121 fresh gain -> stored-form (C0A-121)
G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)
G_CUTWA_STORED = 0.14365819573402408  # l123 fresh gain -> stored-form (C0A-123)
# (L126: cutwB stored const removed — arm not run here; C0A-123 is
# retained on the 4 shared arms only.)
ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B21 = list(range(2501, 2517))  # fresh, absent l113..l125 incl raw_l125
SEEDS = ANCH + B21                  # anchors FIRST: early wiring verdict
FRESH = B21
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
# L126: window INTERPOLATION — positional prefixes ng_desc[:k] for k in
# {21,23,24,26,28}, strictly nested into the ng[19:29] window. l121/
# static.json pins for k19/k29/k58 (re-pinned EXACT by l126_static.py) +
# l126/static.json pins for wA + the 4 prefixes; retained cutk5 anchor
# arm (pins == l117/l119/l120 stored EXACT).
S121 = json.load(open("l121/static.json"))
S126 = json.load(open("l126/static.json"))
NEW_ARMS = ("cutk5", "cutng19", "cutng21", "cutng23", "cutwA",
            "cutng26", "cutng28", "cutng29")
glut_desc = heav[is_glut[heav]]
assert len(glut_desc) == 19
ng_desc = heav[~is_glut[heav]]
assert len(ng_desc) == 58
assert np.array_equal(np.sort(ng_desc), cut58_drop), "ng58 != cut58 set (STOP)"
keep_cutk, n_cutk, cutk_drop, cutk_pins = {}, {}, {}, {}
_pin5 = S121["ladder"]["k5"]
_drop5 = np.sort(glut_desc[[0, 1, 2, 3, 4]])
assert np.isin(_drop5, cut19_drop).all(), "k5 drop not subset of glut-19"
_keep5 = keep_new.copy()
_keep5[_drop5] = False
assert int(_keep5.sum()) == _pin5["n"], ("cutk5", int(_keep5.sum()))
keep_cutk["cutk5"] = _keep5
n_cutk["cutk5"] = int(_keep5.sum())
cutk_drop["cutk5"] = _drop5
cutk_pins["cutk5"] = _pin5
# window endpoints: k19/k29 positional prefixes (l121 stored pins)
for _pk, _a, _kk in (("k19", "cutng19", 19), ("k29", "cutng29", 29)):
    _pin = S121["ngladder"][_pk]
    _drop = np.sort(ng_desc[:_kk])
    assert len(_drop) == _kk
    assert np.isin(_drop, cut58_drop).all(), "ng drop not subset of cut58"
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
# L126 nested prefixes (l126/static.json pins): ng_desc[:k] for k in
# {21,23,24,26,28}; cutwA == ng_desc[:24] re-pinned == l123 stored
# (extraction regression). Strictly nested by construction; DNg100 in
# no drop.
_prev_ids = set()
for _a, _k in (("cutng21", 21), ("cutng23", 23), ("cutwA", 24),
               ("cutng26", 26), ("cutng28", 28)):
    _drop = np.sort(ng_desc[:_k])
    assert len(_drop) == _k
    _ids = set(int(x) for x in _drop)
    assert _prev_ids < _ids, (_a, "nesting broken (STOP)")
    _prev_ids = _ids
    _pin = S126["prefix"][_a]
    assert _pin["drop_ids"] == [int(x) for x in _drop], (_a, "drop drift")
    assert np.isin(_drop, cut58_drop).all()
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
assert [int(x) for x in cutk_drop["cutk5"]] == [204, 286, 313, 561, 32014]
assert cutk_pins["cutk5"]["mass_removed"] == 0.0425, "k5 mass drift (STOP)"
assert cutk_pins["cutk5"]["edges"] == 647252, "k5 edges drift (STOP)"
assert cutk_pins["cutng19"]["mass_removed"] == 0.1946, "ng19 mass drift (STOP)"
assert cutk_pins["cutng29"]["mass_removed"] == 0.2588, "ng29 mass drift (STOP)"
assert cutk_pins["cutng19"]["edges"] == 644729, "ng19 edges drift (STOP)"
assert cutk_pins["cutng29"]["edges"] == 643623, "ng29 edges drift (STOP)"
assert cutk_pins["cutwA"]["mass_removed"] == 0.2286, "wA mass drift (STOP)"
assert cutk_pins["cutwA"]["edges"] == 644177, "wA edges drift (STOP)"
for _a, _m, _e in (
    ("cutng21", 0.2086, 644509),
    ("cutng23", 0.222, 644282),
    ("cutng26", 0.2411, 643979),
    ("cutng28", 0.2529, 643725),
):
    assert cutk_pins[_a]["mass_removed"] == _m, (_a, "mass drift (STOP)")
    assert cutk_pins[_a]["edges"] == _e, (_a, "edges drift (STOP)")
assert S121["ngladder"]["k58"]["edges"] == int(
    (keep_cut58[src_all] & keep_cut58[dst_all]).sum()), "k58 != cut58 arm (STOP)"

# (DNg100-not-in-heavy-77 asserted downstream in the dng100 section + pinned
# in l121/static.json — dng100_all is not yet defined at this point.)


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
Wc_ng19, loc_ng19 = build(keep_cutk["cutng19"])
Wc_ng29, loc_ng29 = build(keep_cutk["cutng29"])
Wc_wA, loc_wA = build(keep_cutk["cutwA"])
Wc_p21, loc_p21 = build(keep_cutk["cutng21"])
Wc_p23, loc_p23 = build(keep_cutk["cutng23"])
Wc_p26, loc_p26 = build(keep_cutk["cutng26"])
Wc_p28, loc_p28 = build(keep_cutk["cutng28"])
Wc_k5, loc_k5 = build(keep_cutk["cutk5"])
assert Wc_ng19.values().numel() == cutk_pins["cutng19"]["edges"]
assert Wc_ng29.values().numel() == cutk_pins["cutng29"]["edges"]
assert Wc_wA.values().numel() == cutk_pins["cutwA"]["edges"]
for _a, _W in (("cutng21", Wc_p21), ("cutng23", Wc_p23),
               ("cutng26", Wc_p26), ("cutng28", Wc_p28)):
    assert _W.values().numel() == cutk_pins[_a]["edges"], (_a, "Wc edges")
assert Wc_k5.values().numel() == cutk_pins["cutk5"]["edges"]
assert Wc_o.values().numel() == S92["edges_old"]
assert Wc_n.values().numel() == S92["edges_new"]
assert Wc_c.values().numel() == ST["edges_cut"]
Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),
                                    wb(Wc_c19), wb(Wc_c58))
Wb_ng19, Wb_ng29, Wb_wA, Wb_p21, Wb_p23, Wb_p26, Wb_p28, Wb_k5 = (
    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p21), wb(Wc_p23),
    wb(Wc_p26), wb(Wc_p28), wb(Wc_k5))

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
gi_ng19 = np.where(keep_cutk["cutng19"])[0]
k1_pos_in_new = loc_n[gi_ng19]
old_pos_in_ng19 = loc_ng19[gi_old]
kept_new_mask_ng19 = keep_cutk["cutng19"][new_g]
kept_new_cutng19 = loc_ng19[new_g[kept_new_mask_ng19]]
gi_ng29 = np.where(keep_cutk["cutng29"])[0]
k2_pos_in_new = loc_n[gi_ng29]
old_pos_in_ng29 = loc_ng29[gi_old]
kept_new_mask_ng29 = keep_cutk["cutng29"][new_g]
kept_new_cutng29 = loc_ng29[new_g[kept_new_mask_ng29]]
gi_wA = np.where(keep_cutk["cutwA"])[0]
wA_pos_in_new = loc_n[gi_wA]
old_pos_in_wA = loc_wA[gi_old]
kept_new_mask_wA = keep_cutk["cutwA"][new_g]
kept_new_cutwA = loc_wA[new_g[kept_new_mask_wA]]
gi_p21 = np.where(keep_cutk["cutng21"])[0]
p21_pos_in_new = loc_n[gi_p21]
old_pos_in_p21 = loc_p21[gi_old]
kept_new_mask_p21 = keep_cutk["cutng21"][new_g]
kept_new_cutcutng21 = loc_p21[new_g[kept_new_mask_p21]]
gi_p23 = np.where(keep_cutk["cutng23"])[0]
p23_pos_in_new = loc_n[gi_p23]
old_pos_in_p23 = loc_p23[gi_old]
kept_new_mask_p23 = keep_cutk["cutng23"][new_g]
kept_new_cutcutng23 = loc_p23[new_g[kept_new_mask_p23]]
gi_p26 = np.where(keep_cutk["cutng26"])[0]
p26_pos_in_new = loc_n[gi_p26]
old_pos_in_p26 = loc_p26[gi_old]
kept_new_mask_p26 = keep_cutk["cutng26"][new_g]
kept_new_cutcutng26 = loc_p26[new_g[kept_new_mask_p26]]
gi_p28 = np.where(keep_cutk["cutng28"])[0]
p28_pos_in_new = loc_n[gi_p28]
old_pos_in_p28 = loc_p28[gi_old]
kept_new_mask_p28 = keep_cutk["cutng28"][new_g]
kept_new_cutcutng28 = loc_p28[new_g[kept_new_mask_p28]]
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
         "cutng19": pools_for(loc_ng19, keep_cutk["cutng19"]),
         "cutng29": pools_for(loc_ng29, keep_cutk["cutng29"]),
         "cutwA": pools_for(loc_wA, keep_cutk["cutwA"]),
         "cutng21": pools_for(loc_p21, keep_cutk["cutng21"]),
         "cutng23": pools_for(loc_p23, keep_cutk["cutng23"]),
         "cutng26": pools_for(loc_p26, keep_cutk["cutng26"]),
         "cutng28": pools_for(loc_p28, keep_cutk["cutng28"]),
         "cutk5": pools_for(loc_k5, keep_cutk["cutk5"]),
         "b65": pools_for(loc_o, keep_old)}
for pk, want in S92["pool_sizes"].items():
    assert len(POOLS["full"][pk]) == want, pk
    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk
    for _da in ("cutwA", "cutng21", "cutng23", "cutng26", "cutng28",
                "cutng19", "cutng29", "cutk5"):
        assert len(POOLS[_da][pk]) == want, (_da, pk)
# L116 NEW pools: sizes == l101 static, all arms (drops are DNs, never motor)
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue  # covered above via the f/e form + cross-check below
    assert len(POOLS["full"][pk]) == want, pk
    for a in ("cut", "cut19", "cut58", "cutng19", "cutng21", "cutng23",
              "cutwA", "cutng26", "cutng28", "cutng29", "cutk5", "b65"):
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
        "cutng19": np.where(mech_mask[keep_cutk["cutng19"]])[0],
        "cutng29": np.where(mech_mask[keep_cutk["cutng29"]])[0],
        "cutwA": np.where(mech_mask[keep_cutk["cutwA"]])[0],
        "cutng21": np.where(mech_mask[keep_cutk["cutng21"]])[0],
        "cutng23": np.where(mech_mask[keep_cutk["cutng23"]])[0],
        "cutng26": np.where(mech_mask[keep_cutk["cutng26"]])[0],
        "cutng28": np.where(mech_mask[keep_cutk["cutng28"]])[0],
        "cutk5": np.where(mech_mask[keep_cutk["cutk5"]])[0],
        "b65": np.where(mech_mask[keep_old])[0]}
assert len(mech["full"]) == S92["mech"]

mg_all = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("cutng19", n_cutk["cutng19"]), ("cutng29", n_cutk["cutng29"]),
          ("cutwA", n_cutk["cutwA"]), ("cutng21", n_cutk["cutng21"]),
          ("cutng23", n_cutk["cutng23"]), ("cutng26", n_cutk["cutng26"]),
          ("cutng28", n_cutk["cutng28"]),
          ("cutk5", n_cutk["cutk5"]),
          ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cut58", keep_cut58, loc_c58),
                     ("cutng19", keep_cutk["cutng19"], loc_ng19),
                     ("cutng29", keep_cutk["cutng29"], loc_ng29),
                     ("cutwA", keep_cutk["cutwA"], loc_wA),
                     ("cutng21", keep_cutk["cutng21"], loc_p21),
                     ("cutng23", keep_cutk["cutng23"], loc_p23),
                     ("cutng26", keep_cutk["cutng26"], loc_p26),
                     ("cutng28", keep_cutk["cutng28"], loc_p28),
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
          "cutng19": np.sort(loc_ng19[dng100_all[keep_cutk["cutng19"][dng100_all]]]),
          "cutng29": np.sort(loc_ng29[dng100_all[keep_cutk["cutng29"][dng100_all]]]),
          "cutwA": np.sort(loc_wA[dng100_all[keep_cutk["cutwA"][dng100_all]]]),
          "cutng21": np.sort(loc_p21[dng100_all[keep_cutk["cutng21"][dng100_all]]]),
          "cutng23": np.sort(loc_p23[dng100_all[keep_cutk["cutng23"][dng100_all]]]),
          "cutng26": np.sort(loc_p26[dng100_all[keep_cutk["cutng26"][dng100_all]]]),
          "cutng28": np.sort(loc_p28[dng100_all[keep_cutk["cutng28"][dng100_all]]]),
          "cutk5": np.sort(loc_k5[dng100_all[keep_cutk["cutk5"][dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]
# L115/L117/L118 pin: no DNg100 cell sits in the heavy-77 (draw drops
# cannot touch the drive channel) — STOP if violated.
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"
for _da in ("cutwA", "cutng21", "cutng23", "cutng26", "cutng28",
            "cutng19", "cutng29", "cutk5"):
    assert len(dng100[_da]) == S92["dng100"], _da
WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA,
      "cutng21": Wb_p21, "cutng23": Wb_p23, "cutng26": Wb_p26,
      "cutng28": Wb_p28, "cutk5": Wb_k5,
      "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "cutng19": n_cutk["cutng19"], "cutng29": n_cutk["cutng29"],
        "cutwA": n_cutk["cutwA"], "cutng21": n_cutk["cutng21"],
        "cutng23": n_cutk["cutng23"], "cutng26": n_cutk["cutng26"],
        "cutng28": n_cutk["cutng28"],
        "cutk5": n_cutk["cutk5"],
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
    Xc_ng19 = torch.zeros(n_cutk["cutng19"], 1)
    Xc_ng19[old_pos_in_ng19] = X0o
    Xc_ng19[kept_new_cutng19] = X0n[kept_new_mask_ng19]
    Xc_ng29 = torch.zeros(n_cutk["cutng29"], 1)
    Xc_ng29[old_pos_in_ng29] = X0o
    Xc_ng29[kept_new_cutng29] = X0n[kept_new_mask_ng29]
    Xc_wA = torch.zeros(n_cutk["cutwA"], 1)
    Xc_wA[old_pos_in_wA] = X0o
    Xc_wA[kept_new_cutwA] = X0n[kept_new_mask_wA]
    Xc_p21 = torch.zeros(n_cutk["cutng21"], 1)
    Xc_p21[old_pos_in_p21] = X0o
    Xc_p21[kept_new_cutcutng21] = X0n[kept_new_mask_p21]
    Xc_p23 = torch.zeros(n_cutk["cutng23"], 1)
    Xc_p23[old_pos_in_p23] = X0o
    Xc_p23[kept_new_cutcutng23] = X0n[kept_new_mask_p23]
    Xc_p26 = torch.zeros(n_cutk["cutng26"], 1)
    Xc_p26[old_pos_in_p26] = X0o
    Xc_p26[kept_new_cutcutng26] = X0n[kept_new_mask_p26]
    Xc_p28 = torch.zeros(n_cutk["cutng28"], 1)
    Xc_p28[old_pos_in_p28] = X0o
    Xc_p28[kept_new_cutcutng28] = X0n[kept_new_mask_p28]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xo65 = X0o.clone()
    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
              cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),
              cutwA=Xc_wA.clone(), cutng21=Xc_p21.clone(),
              cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),
              cutng28=Xc_p28.clone(), cutk5=Xc_k5.clone(),
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
                     cutng19=nzn[k1_pos_in_new],
                     cutng29=nzn[k2_pos_in_new],
                     cutwA=nzn[wA_pos_in_new],
                     cutng21=nzn[p21_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutng28=nzn[p28_pos_in_new],
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
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutng21=g, cutng23=g, cutng26=g,
                                  cutng28=g, cutk5=g))
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


# L126 form: endpoint + wA gains are STORED-FORM anchors (re-bisect
# EXACT, l121/l123); the 4 interpolation prefixes are FRESH bisects
# below. Staircase + band disclosures retained per PREREG (never abort).
new_stairs = {}
for _a in ("cutng19", "cutng29", "cutwA"):
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
    _st = {"cutng19": G_CUTNG19_STORED, "cutng29": G_CUTNG29_STORED,
           "cutwA": G_CUTWA_STORED}[_a]
    assert GAIN[_a] == _st, (_a, GAIN[_a], _st)
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    _band = " [OUTSIDE PREREG band .14-.16 — DISCLOSED]" \
        if not (0.14 <= lo_d <= 0.16) else ""
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_band}")
# L126 FRESH bisects: interpolation prefixes (staircase + band
# DISCLOSED per PREREG — the .14-.16 band is a disclosure, never an
# abort).
for _a in ("cutng21", "cutng23", "cutng26", "cutng28"):
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
if os.path.exists("l126/raw_partial.npz"):
    z = np.load("l126/raw_partial.npz")
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
    Xc_ng19 = torch.zeros(n_cutk["cutng19"], 1)
    Xc_ng19[old_pos_in_ng19] = X0o
    Xc_ng19[kept_new_cutng19] = X0n[kept_new_mask_ng19]
    Xc_ng29 = torch.zeros(n_cutk["cutng29"], 1)
    Xc_ng29[old_pos_in_ng29] = X0o
    Xc_ng29[kept_new_cutng29] = X0n[kept_new_mask_ng29]
    Xc_wA = torch.zeros(n_cutk["cutwA"], 1)
    Xc_wA[old_pos_in_wA] = X0o
    Xc_wA[kept_new_cutwA] = X0n[kept_new_mask_wA]
    Xc_p21 = torch.zeros(n_cutk["cutng21"], 1)
    Xc_p21[old_pos_in_p21] = X0o
    Xc_p21[kept_new_cutcutng21] = X0n[kept_new_mask_p21]
    Xc_p23 = torch.zeros(n_cutk["cutng23"], 1)
    Xc_p23[old_pos_in_p23] = X0o
    Xc_p23[kept_new_cutcutng23] = X0n[kept_new_mask_p23]
    Xc_p26 = torch.zeros(n_cutk["cutng26"], 1)
    Xc_p26[old_pos_in_p26] = X0o
    Xc_p26[kept_new_cutcutng26] = X0n[kept_new_mask_p26]
    Xc_p28 = torch.zeros(n_cutk["cutng28"], 1)
    Xc_p28[old_pos_in_p28] = X0o
    Xc_p28[kept_new_cutcutng28] = X0n[kept_new_mask_p28]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xo65 = X0o.clone()
    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),
             cutwA=Xc_wA.clone(), cutng21=Xc_p21.clone(),
             cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),
             cutng28=Xc_p28.clone(), cutk5=Xc_k5.clone(),
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
                     cutng19=nzn[k1_pos_in_new],
                     cutng29=nzn[k2_pos_in_new],
                     cutwA=nzn[wA_pos_in_new],
                     cutng21=nzn[p21_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutng28=nzn[p28_pos_in_new],
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
                     cutng19=nzn[k1_pos_in_new],
                     cutng29=nzn[k2_pos_in_new],
                     cutwA=nzn[wA_pos_in_new],
                     cutng21=nzn[p21_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutng28=nzn[p28_pos_in_new],
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
    np.savez("l126/raw_partial.npz", **store)
    log(f"seed {seed} done af {af_c} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l126/raw_l126.npz", K=K, g_cut=GAIN["cut"],
                    g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
                    g_cutk5=GAIN["cutk5"],
                    g_cutng19=GAIN["cutng19"], g_cutng29=GAIN["cutng29"],
                    g_cutwA=GAIN["cutwA"], g_cutng21=GAIN["cutng21"],
                    g_cutng23=GAIN["cutng23"], g_cutng26=GAIN["cutng26"],
                    g_cutng28=GAIN["cutng28"],
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutng19_drop=cutk_drop["cutng19"], cutng29_drop=cutk_drop["cutng29"],
                    cutwA_drop=cutk_drop["cutwA"],
                    cutng21_drop=cutk_drop["cutng21"],
                    cutng23_drop=cutk_drop["cutng23"],
                    cutng26_drop=cutk_drop["cutng26"],
                    cutng28_drop=cutk_drop["cutng28"],
                    cutk5_drop=cutk_drop["cutk5"],
                    new_mass=np.array([cutk_pins[a]["mass_removed"] for a in NEW_ARMS]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l126.npz checkpointed BEFORE analysis")

# ---------------- C0A (PREREG): FULL-BATCH anchors vs raw_l113 ----------------
# Enumerated OLD keys only (L59 anchor-key rule): the 8 Ti/Tr pools + mm/xm.
# New Ta/Sr/Pr keys do not exist in z113 and are excluded BY NAME.
zprev = np.load("l113/raw_l113.npz")
C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                           for c in ("f", "e") for s in ("L", "R")]
assert all(f"{k}_full_801" in zprev.files for k in C0A_KEYS)
# B21 is fresh: no stored counterpart (asserted absent pre-C0A)
assert not any(f"mm_full_{s}" in zprev.files for s in B21), \
    "B21 collides with stored batches (STOP)"
for _prev in ("l115/raw_l115.npz", "l117/raw_l117.npz",
              "l118/raw_l118.npz", "l119/raw_l119.npz",
              "l120/raw_l120.npz", "l121/raw_l121.npz",
              "l122/raw_l122.npz", "l123/raw_l123.npz",
              "l124/raw_l124.npz", "l125/raw_l125.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B21), \
        ("B21 collides with " + _prev + " (STOP)")
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
# C0A-120 (NEW anchor class): cutk5 at stored seeds vs raw_l120.
# l120 ran every arm at all 18 seeds, so cutk5 has a stored counterpart
# on ALL pool keys; cutng19/29/39 have NONE (excluded by name).
z120 = np.load("l120/raw_l120.npz")
_c0a120_poolkeys = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _c0a120_poolkeys.append(f"{_pk}_{_c}{_s}")
C0A120_KEYS = ["mm", "xm"] + _c0a120_poolkeys
assert all(f"{_k}_cutk5_801" in z120.files for _k in C0A120_KEYS)
c0a120 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5",):
            c0a120[f"120_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z120[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5",):
        c0a120[f"120_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z120[f"af_{a}_{s}"]))
c0a120_max = max(c0a120.values())
c0a120_pass = bool(all(v == 0.0 for v in c0a120.values()))
log(f"C0A-120 cutk5 vs raw_l120: {'PASS' if c0a120_pass else 'FAIL'} "
    f"(max {c0a120_max:.1e}, {len(C0A120_KEYS)} keys x 1 arm x 2 seeds)")
# C0A-121 (NEW anchor class): ng arms + cutk5 at stored seeds vs raw_l121.
# l121 ran every arm at all 18 seeds, so all three run here have stored counterparts
# on ALL pool keys (L120 addendum forward-chain rule).
z121 = np.load("l121/raw_l121.npz")
c0a121 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29"):
            c0a121[f"121_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z121[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29"):
        c0a121[f"121_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z121[f"af_{a}_{s}"]))
c0a121_max = max(c0a121.values())
c0a121_pass = bool(all(v == 0.0 for v in c0a121.values()))
log(f"C0A-121 ng arms vs raw_l121: {'PASS' if c0a121_pass else 'FAIL'} "
    f"(max {c0a121_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
# C0A-122 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29} at
# stored seeds vs raw_l122 (l122 ran every arm at all 18 seeds).
z122 = np.load("l122/raw_l122.npz")
c0a122 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29"):
            c0a122[f"122_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z122[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29"):
        c0a122[f"122_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z122[f"af_{a}_{s}"]))
c0a122_max = max(c0a122.values())
c0a122_pass = bool(all(v == 0.0 for v in c0a122.values()))
log(f"C0A-122 forward chain vs raw_l122: {'PASS' if c0a122_pass else 'FAIL'} "
    f"(max {c0a122_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
# C0A-123 (RETAINED, 4 shared arms): {cutk5,cutng19,cutng29,cutwA} at
# stored seeds vs raw_l123 (cutwB trimmed — not run in L126; DISCLOSED).
z123c = np.load("l123/raw_l123.npz")
c0a123 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29", "cutwA"):
            c0a123[f"123_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z123c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29", "cutwA"):
        c0a123[f"123_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z123c[f"af_{a}_{s}"]))
c0a123_max = max(c0a123.values())
c0a123_pass = bool(all(v == 0.0 for v in c0a123.values()))
log(f"C0A-123 (4 shared arms) vs raw_l123: {'PASS' if c0a123_pass else 'FAIL'} "
    f"(max {c0a123_max:.1e}, {len(C0A120_KEYS)} keys x 4 arms x 2 seeds)")
# C0A-124 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29,
# cutwA} at stored seeds vs raw_l124 (l124 ran every arm incl wA at all
# 18 seeds).
z124c = np.load("l124/raw_l124.npz")
c0a124 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29", "cutwA"):
            c0a124[f"124_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z124c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29", "cutwA"):
        c0a124[f"124_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z124c[f"af_{a}_{s}"]))
c0a124_max = max(c0a124.values())
c0a124_pass = bool(all(v == 0.0 for v in c0a124.values()))
log(f"C0A-124 forward chain vs raw_l124: {'PASS' if c0a124_pass else 'FAIL'} "
    f"(max {c0a124_max:.1e}, {len(C0A120_KEYS)} keys x 4 arms x 2 seeds)")
# C0A-125 (NEW anchor class): forward chain — {cutk5,cutng19,cutng29} at
# stored seeds vs raw_l125 (scr arms not run in L126; DISCLOSED).
z125c = np.load("l125/raw_l125.npz")
c0a125 = {}
for s in (801, 901):
    for key in C0A120_KEYS:
        for a in ("cutk5", "cutng19", "cutng29"):
            c0a125[f"125_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z125c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ("cutk5", "cutng19", "cutng29"):
        c0a125[f"125_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z125c[f"af_{a}_{s}"]))
c0a125_max = max(c0a125.values())
c0a125_pass = bool(all(v == 0.0 for v in c0a125.values()))
log(f"C0A-125 forward chain vs raw_l125: {'PASS' if c0a125_pass else 'FAIL'} "
    f"(max {c0a125_max:.1e}, {len(C0A120_KEYS)} keys x 3 arms x 2 seeds)")
c0a_new_pools = sorted({pk.split("_")[0] for pk in POOLS["full"]}
                       - {"Ti", "Tr"})
log(f"C0A covered keys {len(C0A_KEYS)} x stored arms {len(STORED_ARMS)} "
    f"x anchor seeds 2 | NEW pools excluded by name: {c0a_new_pools} "
    f"| NEW arms excluded (no l113 counterpart): ['cutk5','cutng19','cutng29',"
    "'cutng21'] | cutk5 additionally C0A-anchored vs raw_l120 (C0A-120)")
out = dict(g_cut=GAIN["cut"], g_cut19=GAIN["cut19"], g_cut58=GAIN["cut58"],
           g_cut58_stored_exact=bool(GAIN["cut58"] == G_CUT58_STORED),
           g_cutk5_stored_exact=bool(GAIN["cutk5"] == G_CUTK5_STORED),
           g_cutng19=GAIN["cutng19"], g_cutng29=GAIN["cutng29"],
           g_cutwA=GAIN["cutwA"], g_cutng21=GAIN["cutng21"],
           g_cutng23=GAIN["cutng23"], g_cutng26=GAIN["cutng26"],
           g_cutng28=GAIN["cutng28"],
           new_stairs=new_stairs,
           new_band_ok=bool(all(0.14 <= GAIN[a] <= 0.16
                                 for a in ("cutng21", "cutng23", "cutng26",
                                           "cutng28"))),
           af_final=af_final, af_final19=af_final19, af_final58=af_final58,
           af_finalk5=af_finalk5,
           K=K, mass_split=mass_split, n_seeds=len(SEEDS),
           new_mass={a: cutk_pins[a]["mass_removed"] for a in NEW_ARMS},
           c0a_max=max(c0a.values()),
           c0a120_max=c0a120_max, c0a120_pass=c0a120_pass,
           c0a121_max=c0a121_max, c0a121_pass=c0a121_pass,
           c0a122_max=c0a122_max, c0a122_pass=c0a122_pass,
           c0a123_max=c0a123_max, c0a123_pass=c0a123_pass,
           c0a124_max=c0a124_max, c0a124_pass=c0a124_pass,
           c0a125_max=c0a125_max, c0a125_pass=c0a125_pass,
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           prefix_fresh_gains={a: GAIN[a] for a in
                               ("cutng21", "cutng23", "cutng26",
                                "cutng28")},
           g_cutng19_stored_exact=bool(GAIN["cutng19"] == G_CUTNG19_STORED),
           g_cutng29_stored_exact=bool(GAIN["cutng29"] == G_CUTNG29_STORED),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values()) and c0a120_pass
                          and c0a121_pass and c0a122_pass and c0a123_pass
                          and c0a124_pass and c0a125_pass))
json.dump(out, open("l126/anchors_run.json", "w"), indent=1)
log(f"C0A {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a_max']:.1e}) | done {time.time()-t0:.0f}s")
