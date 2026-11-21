"""L169 run: pre-posting control (a), the GAIN-SWAP 2x2. PREREG
l169/PREREG.md FIRST (registered before this build). NEW ARMS: wAgN =
cutwA graph VERBATIM at g_cutng25, n25gW = cutng25 graph VERBATIM at
g_cutwA — the two off-diagonal cells of {graph} x {gain}. Both are
DELIBERATELY off their matched operating point (that is the test);
P-af direction registered instead of an af identity. C0-NT probe: a
swap arm bit-identical to its own-gain twin = VOID run. Inherited
arms (all seven) ride along for free forward-chain anchors and a
third batch. FRESH B35 3417-3432. Arms: full, b65,
cutwA (partial base), cutng25 (super ref), silW (cutwA graph VERBATIM +
window-only clamp X[loc 467]=0, l144 form, gain graph-identity to cutwA —
NO fresh bisect, l144 A1) + eMotTop5/eMotBot5 (l145 dose split verbatim,
fresh bisects asserted == l145 stored gains EXACT). FRESH B35 3417-3432.
Anchors: stored gains EXACT (cutwA/cutng25/eMot pair), C0A-150 vs raw_l135
(4 arms), FC-144 silW-vs-l144-sil1110_wA @801/901 (clamp-wiring cert),
FC-145 eMot arms vs raw_l145 @801/901 + bisect EXACT. CPU-only; raw
checkpoint BEFORE analysis. (the prior run's identity arms stand on their
own batch — see its results json; not re-rolled here.)
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
ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
        "eMotBot5", "wAgN", "n25gW"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            silW=None, eMotTop5=None, eMotBot5=None,
            wAgN=None, n25gW=None)  # silW/swap arms below
G_CUT19_STORED = 0.15096808075904844  # l111 stored, PREREG C0A(c19)
G_CUT_STORED = 0.14510760426521305  # l107 stored, PREREG C0A(c)
G_CUT58_STORED = 0.15417299151420596  # l113 stored, PREREG C0A(c58)
G_CUTK5_STORED = 0.13981970071792604  # l117 stored dose gain, C0A(k5)
G_CUTNG19_STORED = 0.15025991678237915  # l121 fresh gain -> stored-form (C0A-121)
G_CUTNG29_STORED = 0.1442639136314392  # l121 fresh gain -> stored-form (C0A-121)
G_CUTWA_STORED = 0.14365819573402408  # l123 fresh gain -> stored-form (C0A-123)
G_CUTNG23_STORED = 0.14696856379508969  # l126 fresh gain -> stored-form
G_CUTNG26_STORED = 0.14545363783836368  # l126 fresh gain -> stored-form
G_CUTNG25_STORED = 0.1454454553127289  # l131 fresh gain -> stored-form (C0A-131)
G_CUTNG25P_STORED = 0.1435265743732452  # l133 fresh gain -> stored-form (C0A-133)
G_EMOTTOP5_STORED = 0.1436134350299835  # l145 stored, FC-145 EXACT assert
G_EMOTBOT5_STORED = 0.14367126345634465  # l145 stored, FC-145 EXACT assert
# (L131: cutng21/cutng28 not run — l126 single-batch points stand,
# DISCLOSED; C0A-123 retained on the 4 shared arms.)
ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B35 = list(range(3417, 3433))  # fresh (B34 = l154; lineage in PREREG)
SEEDS = ANCH + B35                  # anchors FIRST: early wiring verdict
FRESH = B35
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
S131 = json.load(open("l131/static.json"))
S133 = json.load(open("l133/static.json"))
S135 = json.load(open("l135/static.json"))
assert S135 == S133  # L135 re-pin EXACT (no new arm)
NEW_ARMS = ("cutk5", "cutng19", "cutng23", "cutwA", "cutng25",
            "cutng25p", "cutng26", "cutng29")
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
# L131 prefixes (l131/static.json pins): ng_desc[:k] for k in
# {23,24,25,26}; cutng25 = wA + rank 25 (id 1110) ONLY — the XOR arm;
# cutng23/wA/cutng26 re-pinned == l126/l123 stored EXACT. Strictly
# nested by construction; DNg100 in no drop.
_prev_ids = set()
for _a, _k in (("cutng23", 23), ("cutwA", 24), ("cutng25", 25),
               ("cutng26", 26)):
    _drop = np.sort(ng_desc[:_k])
    assert len(_drop) == _k
    _ids = set(int(x) for x in _drop)
    assert _prev_ids < _ids, (_a, "nesting broken (STOP)")
    _prev_ids = _ids
    _pin = S131["prefix"][_a]
    assert _pin["drop_ids"] == [int(x) for x in _drop], (_a, "drop drift")
    assert np.isin(_drop, cut58_drop).all()
    _keep = keep_new.copy()
    _keep[_drop] = False
    assert int(_keep.sum()) == _pin["n"], (_a, int(_keep.sum()))
    keep_cutk[_a] = _keep
    n_cutk[_a] = int(_keep.sum())
    cutk_drop[_a] = _drop
    cutk_pins[_a] = _pin
# L133 XOR arm: cutng25p = wA + rank 26 (id 319) ONLY — NOT a prefix
# (skips rank 25 / id 1110); pins from l133/static.json (static-first).
_pin25p = S133["xor25p"]["cutng25p"]
_drop25p = np.sort(np.concatenate([ng_desc[:24], ng_desc[25:26]]))
assert _pin25p["drop_ids"] == [int(x) for x in _drop25p], \
    "cutng25p drop drift (STOP)"
assert np.isin(_drop25p, cut58_drop).all()
_keep25p = keep_new.copy()
_keep25p[_drop25p] = False
assert int(_keep25p.sum()) == _pin25p["n"], ("cutng25p", int(_keep25p.sum()))
keep_cutk["cutng25p"] = _keep25p
n_cutk["cutng25p"] = int(_keep25p.sum())
cutk_drop["cutng25p"] = _drop25p
cutk_pins["cutng25p"] = _pin25p
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
    ("cutng23", 0.222, 644282),
    ("cutng25", 0.235, 644084),
    ("cutng25p", 0.2346, 644072),
    ("cutng26", 0.2411, 643979),
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
Wc_p23, loc_p23 = build(keep_cutk["cutng23"])
Wc_p25, loc_p25 = build(keep_cutk["cutng25"])
Wc_p25p, loc_p25p = build(keep_cutk["cutng25p"])
Wc_p26, loc_p26 = build(keep_cutk["cutng26"])
Wc_k5, loc_k5 = build(keep_cutk["cutk5"])
assert Wc_ng19.values().numel() == cutk_pins["cutng19"]["edges"]
assert Wc_ng29.values().numel() == cutk_pins["cutng29"]["edges"]
assert Wc_wA.values().numel() == cutk_pins["cutwA"]["edges"]
for _a, _W in (("cutng25", Wc_p25), ("cutng25p", Wc_p25p),
               ("cutng23", Wc_p23), ("cutng26", Wc_p26)):
    assert _W.values().numel() == cutk_pins[_a]["edges"], (_a, "Wc edges")
assert Wc_k5.values().numel() == cutk_pins["cutk5"]["edges"]
assert Wc_o.values().numel() == S92["edges_old"]
assert Wc_n.values().numel() == S92["edges_new"]
assert Wc_c.values().numel() == ST["edges_cut"]
Wb_o, Wb_n, Wb_c, Wb_c19, Wb_c58 = (wb(Wc_o), wb(Wc_n), wb(Wc_c),
                                    wb(Wc_c19), wb(Wc_c58))
Wb_ng19, Wb_ng29, Wb_wA, Wb_p23, Wb_p25, Wb_p25p, Wb_p26, Wb_k5 = (
    wb(Wc_ng19), wb(Wc_ng29), wb(Wc_wA), wb(Wc_p23), wb(Wc_p25),
    wb(Wc_p25p), wb(Wc_p26), wb(Wc_k5))

# ---- L142: edge-footprint arms on the cutwA node set (PREREG l142) ----
GI_CARRIER = 1110
E_ARMS = ("eMotTop5", "eMotBot5")
assert int(ng_desc[24]) == GI_CARRIER and int(ng_desc[25]) == 319
keep_wA_e = keep_cutk["cutwA"]
emask_wA = keep_wA_e[src_all] & keep_wA_e[dst_all]
assert int(emask_wA.sum()) == cutk_pins["cutwA"]["edges"]
_sel_out = emask_wA & (src_all == GI_CARRIER)
out_mot_e = _sel_out & (tier_of_dst[dst_all] == "motor_other")
in_sel_e = emask_wA & (dst_all == GI_CARRIER)
# L145 dose split VERBATIM: rank the 10 motor edges by |vals| = log1p(syn)
# DESC, tiebreak global edge pos ASC (rank pins vs l145/static.json below)
_mp = np.where(out_mot_e)[0]
_mo = _mp[np.lexsort((_mp, -np.log1p(w_syn[_mp])))]
_top5 = np.zeros_like(emask_wA)
_top5[_mo[:5]] = True
_bot5 = np.zeros_like(emask_wA)
_bot5[_mo[5:]] = True
assert int(_top5.sum()) == 5 and int(_bot5.sum()) == 5
assert np.array_equal(np.where(_top5 | _bot5)[0],
                      np.where(out_mot_e)[0]), "top5|bot5 != all-10 motor"
e_drop = {"eMotTop5": _top5, "eMotBot5": _bot5}
E_EDGES = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert E_EDGES == {"eMotTop5": 5, "eMotBot5": 5}, E_EDGES
# ADDENDUM 1 pin: l145 static TABLE has a zip bug (pos column = unranked
# ascending list); TRUSTED columns are dst_gi/syn (the ranked order).
_S145 = json.load(open("l145/static.json"))
_stored_pos = [int(e["pos"]) for e in _S145["motor_edges_ranked"]]
assert _stored_pos == sorted(_stored_pos),     "stored pos column no longer ascending — defect signature changed"
assert _stored_pos == sorted(int(p) for p in _mo),     "position SET mismatch vs stored table (real drift, STOP)"
for _i, _e in enumerate(_S145["motor_edges_ranked"]):
    assert int(_e["syn"]) == int(w_syn[_mo[_i]]), ("rank syn drift", _i)
    assert int(_e["dst_gi"]) == int(dst_all[_mo[_i]]), ("rank dst drift", _i)


def build_e(keep, drop):
    em = keep[src_all] & keep[dst_all] & ~drop
    gsrc, gdst, gcount = src_all[em], dst_all[em], w_syn[em]
    loc_e = -np.ones(Nall, np.int64)
    loc_e[keep] = np.arange(int(keep.sum()))
    gsign_a3 = sign_all[gsrc]
    gsign_b3 = np.where(is_glut[gsrc], -np.abs(gsign_a3), gsign_a3)
    vals_e = (np.log1p(gcount) * gsign_b3).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([loc_e[gdst], loc_e[gsrc]])).long(),
        torch.from_numpy(vals_e),
        (int(keep.sum()), int(keep.sum()))).coalesce().to_sparse_csr()
    return W


We = {a: build_e(keep_wA_e, e_drop[a]) for a in E_ARMS}
for _a in E_ARMS:
    assert int(We[_a].values().numel()) == int(emask_wA.sum()) - E_EDGES[_a], _a
# (edge-positions == node-drop identity law settled l142 static+run;
# not re-asserted here)
Wb_e = {a: wb(We[a]) for a in E_ARMS}


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
gi_p25 = np.where(keep_cutk["cutng25"])[0]
p25_pos_in_new = loc_n[gi_p25]
old_pos_in_p25 = loc_p25[gi_old]
kept_new_mask_p25 = keep_cutk["cutng25"][new_g]
kept_new_cutcutng25 = loc_p25[new_g[kept_new_mask_p25]]
gi_p25p = np.where(keep_cutk["cutng25p"])[0]
p25p_pos_in_new = loc_n[gi_p25p]
old_pos_in_p25p = loc_p25p[gi_old]
kept_new_mask_p25p = keep_cutk["cutng25p"][new_g]
kept_new_cutcutng25p = loc_p25p[new_g[kept_new_mask_p25p]]
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
         "cutng25": pools_for(loc_p25, keep_cutk["cutng25"]),
         "cutng25p": pools_for(loc_p25p, keep_cutk["cutng25p"]),
         "cutng23": pools_for(loc_p23, keep_cutk["cutng23"]),
         "cutng26": pools_for(loc_p26, keep_cutk["cutng26"]),
         "cutk5": pools_for(loc_k5, keep_cutk["cutk5"]),
         "b65": pools_for(loc_o, keep_old)}
for pk, want in S92["pool_sizes"].items():
    assert len(POOLS["full"][pk]) == want, pk
    assert len(POOLS["cut"][pk]) == want and len(POOLS["b65"][pk]) == want
    assert len(POOLS["cut19"][pk]) == want, pk
    assert len(POOLS["cut58"][pk]) == want, pk
    for _da in ("cutwA", "cutng25", "cutng25p", "cutng23", "cutng26",
                "cutng19", "cutng29", "cutk5"):
        assert len(POOLS[_da][pk]) == want, (_da, pk)
# L116 NEW pools: sizes == l101 static, all arms (drops are DNs, never motor)
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue  # covered above via the f/e form + cross-check below
    assert len(POOLS["full"][pk]) == want, pk
    for a in ("cut", "cut19", "cut58", "cutng19", "cutng23", "cutwA",
              "cutng25", "cutng25p", "cutng26", "cutng29", "cutk5",
              "b65"):
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
        "cutng25": np.where(mech_mask[keep_cutk["cutng25"]])[0],
        "cutng25p": np.where(mech_mask[keep_cutk["cutng25p"]])[0],
        "cutng23": np.where(mech_mask[keep_cutk["cutng23"]])[0],
        "cutng26": np.where(mech_mask[keep_cutk["cutng26"]])[0],
        "cutk5": np.where(mech_mask[keep_cutk["cutk5"]])[0],
        "b65": np.where(mech_mask[keep_old])[0]}
assert len(mech["full"]) == S92["mech"]

mg_all = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor = {a: np.zeros(n, bool) for a, n in
         (("full", n_new), ("cut", n_cut), ("cut19", n_cut19),
          ("cut58", n_cut58), ("cutng19", n_cutk["cutng19"]), ("cutng29", n_cutk["cutng29"]),
          ("cutwA", n_cutk["cutwA"]), ("cutng25", n_cutk["cutng25"]),
          ("cutng25p", n_cutk["cutng25p"]),
          ("cutng23", n_cutk["cutng23"]), ("cutng26", n_cutk["cutng26"]),
          ("cutk5", n_cutk["cutk5"]),
          ("b65", n_old))}
for a, keep, loc in (("full", keep_new, loc_n), ("cut", keep_cut, loc_c),
                     ("cut19", keep_cut19, loc_c19),
                     ("cut58", keep_cut58, loc_c58),
                     ("cutng19", keep_cutk["cutng19"], loc_ng19),
                     ("cutng29", keep_cutk["cutng29"], loc_ng29),
                     ("cutwA", keep_cutk["cutwA"], loc_wA),
                     ("cutng25", keep_cutk["cutng25"], loc_p25),
                     ("cutng25p", keep_cutk["cutng25p"], loc_p25p),
                     ("cutng23", keep_cutk["cutng23"], loc_p23),
                     ("cutng26", keep_cutk["cutng26"], loc_p26),
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
          "cutng25": np.sort(loc_p25[dng100_all[keep_cutk["cutng25"][dng100_all]]]),
          "cutng25p": np.sort(loc_p25p[dng100_all[keep_cutk["cutng25p"][dng100_all]]]),
          "cutng23": np.sort(loc_p23[dng100_all[keep_cutk["cutng23"][dng100_all]]]),
          "cutng26": np.sort(loc_p26[dng100_all[keep_cutk["cutng26"][dng100_all]]]),
          "cutk5": np.sort(loc_k5[dng100_all[keep_cutk["cutk5"][dng100_all]]]),
          "b65": np.sort(loc_o[dng100_all[keep_old[dng100_all]]])}
assert len(dng100["full"]) == S92["dng100"]
# L115/L117/L118 pin: no DNg100 cell sits in the heavy-77 (draw drops
# cannot touch the drive channel) — STOP if violated.
assert not np.isin(dng100_all, cut_drop).any(), "DNg100 in heavy-77 (STOP)"
for _da in ("cutwA", "cutng25", "cutng25p", "cutng23", "cutng26",
            "cutng19", "cutng29", "cutk5"):
    assert len(dng100[_da]) == S92["dng100"], _da
WB = {"full": Wb_n, "cut": Wb_c, "cut19": Wb_c19, "cut58": Wb_c58,
      "cutng19": Wb_ng19, "cutng29": Wb_ng29, "cutwA": Wb_wA,
      "cutng25": Wb_p25, "cutng25p": Wb_p25p, "cutng23": Wb_p23,
      "cutng26": Wb_p26,
      "cutk5": Wb_k5,
      "b65": Wb_o}
N_OF = {"full": n_new, "cut": n_cut, "cut19": n_cut19, "cut58": n_cut58,
        "cutng19": n_cutk["cutng19"], "cutng29": n_cutk["cutng29"],
        "cutwA": n_cutk["cutwA"], "cutng25": n_cutk["cutng25"],
        "cutng25p": n_cutk["cutng25p"],
        "cutng23": n_cutk["cutng23"], "cutng26": n_cutk["cutng26"],
        "cutk5": n_cutk["cutk5"],
        "b65": n_old}

# L142: edge arms share cutwA's node set — alias every per-arm map
for _ea in E_ARMS:
    POOLS[_ea] = POOLS["cutwA"]
    mech[_ea] = mech["cutwA"]
    motor[_ea] = motor["cutwA"]
    dng100[_ea] = dng100["cutwA"]
    WB[_ea] = Wb_e[_ea]
    N_OF[_ea] = n_cutk["cutwA"]

# ---- L150: silW = cutwA graph + window clamp on 1110 (l144 form) ----
CLAMP = {"silW": torch.tensor([int(loc_wA[GI_CARRIER])])}
assert int(loc_wA[GI_CARRIER]) == 467, "clamp loc != 467 (l144 pin)"
POOLS["silW"] = POOLS["cutwA"]
mech["silW"] = mech["cutwA"]
motor["silW"] = motor["cutwA"]
dng100["silW"] = dng100["cutwA"]
WB["silW"] = Wb_wA  # cutwA matrix VERBATIM — clamp is the only difference
N_OF["silW"] = n_cutk["cutwA"]

# ---- L169: gain-swap arms. Graph objects are the SAME CSR objects as
# their own-gain twins (asserted by object identity below); the ONLY
# difference is the scalar GAIN. No clamp, no bisect.
for _sa, _tw, _Wtw in (("wAgN", "cutwA", Wb_wA), ("n25gW", "cutng25", Wb_p25)):
    POOLS[_sa] = POOLS[_tw]
    mech[_sa] = mech[_tw]
    motor[_sa] = motor[_tw]
    dng100[_sa] = dng100[_tw]
    WB[_sa] = _Wtw
    N_OF[_sa] = n_cutk[_tw]
assert WB["wAgN"] is WB["cutwA"] and WB["n25gW"] is WB["cutng25"], \
    "L169 GRAPH-IDENTITY broken (STOP)"
assert N_OF["wAgN"] == n_cutk["cutwA"] and N_OF["n25gW"] == n_cutk["cutng25"]

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
    Xc_p25 = torch.zeros(n_cutk["cutng25"], 1)
    Xc_p25[old_pos_in_p25] = X0o
    Xc_p25[kept_new_cutcutng25] = X0n[kept_new_mask_p25]
    Xc_p25p = torch.zeros(n_cutk["cutng25p"], 1)
    Xc_p25p[old_pos_in_p25p] = X0o
    Xc_p25p[kept_new_cutcutng25p] = X0n[kept_new_mask_p25p]
    Xc_p23 = torch.zeros(n_cutk["cutng23"], 1)
    Xc_p23[old_pos_in_p23] = X0o
    Xc_p23[kept_new_cutcutng23] = X0n[kept_new_mask_p23]
    Xc_p26 = torch.zeros(n_cutk["cutng26"], 1)
    Xc_p26[old_pos_in_p26] = X0o
    Xc_p26[kept_new_cutcutng26] = X0n[kept_new_mask_p26]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xo65 = X0o.clone()
    st = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
              cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
              cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),
              cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),
              cutng25p=Xc_p25p.clone(),
              cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),
              cutk5=Xc_k5.clone(),
              silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
              eMotBot5=Xc_wA.clone(),
              wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),
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
                     cutng25=nzn[p25_pos_in_new],
                     cutng25p=nzn[p25p_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     silW=nzn[wA_pos_in_new], eMotTop5=nzn[wA_pos_in_new],
                     eMotBot5=nzn[wA_pos_in_new],
                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],
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
                                  cutng25=g, cutng25p=g, cutng23=g,
                                  cutng26=g, cutk5=g, silW=g,
                                  eMotTop5=g, eMotBot5=g,
                                  wAgN=g, n25gW=g))
        afs.append(float((st[arm] > 0.05).float().mean()))
    return float(np.mean(afs))

# ---------------- bisects (L142: 2 stored-form + 5 fresh) ----------------
new_stairs = {}
for _a in ("cutwA", "cutng25"):
    _stored = {"cutwA": G_CUTWA_STORED, "cutng25": G_CUTNG25_STORED}[_a]
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
    assert GAIN[_a] == _stored, (_a, GAIN[_a], _stored)
    af_d = bisect_af_mean(lo_d, _a)
    new_stairs[_a] = abs(af_d - AF_T)
    log(f"g_{_a} {lo_d:.6f} == stored EXACT | af_final {af_d:.6f}")
e_band_ok = {}
for _a in E_ARMS:
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
    e_band_ok[_a] = bool(0.14 <= lo_d <= 0.16)
    _note = "" if e_band_ok[_a] else " [OUTSIDE .14-.16 band — DISCLOSED]"
    log(f"g_{_a} {lo_d:.6f} | af_final {af_d:.6f} | "
        f"|af-target| {abs(af_d - AF_T):.2e} (staircase){_note}")
assert GAIN["eMotTop5"] == G_EMOTTOP5_STORED, \
    ("eMotTop5 bisect drift", GAIN["eMotTop5"])
assert GAIN["eMotBot5"] == G_EMOTBOT5_STORED, \
    ("eMotBot5 bisect drift", GAIN["eMotBot5"])
GAIN["silW"] = GAIN["cutwA"]  # graph-identity af-match (l144 A1 form)
assert GAIN["silW"] == G_CUTWA_STORED == GAIN["cutwA"], \
    (GAIN["silW"], "silW/cutwA gain identity broken (STOP)")
# L169 swap: the OTHER arm's bisected gain, imported, never re-bisected.
GAIN["wAgN"] = GAIN["cutng25"]
GAIN["n25gW"] = GAIN["cutwA"]
assert GAIN["wAgN"] == G_CUTNG25_STORED and GAIN["n25gW"] == G_CUTWA_STORED, \
    "L169 swap gains not the stored pair (STOP)"
assert GAIN["wAgN"] != GAIN["cutwA"] and GAIN["n25gW"] != GAIN["cutng25"], \
    "L169 swap is a no-op (STOP)"
log(f"L169 swap gains | wAgN {GAIN['wAgN']:.9f} (cutwA graph) | "
    f"n25gW {GAIN['n25gW']:.9f} (cutng25 graph)")

# ---------------- rollouts ----------------
store = {}
paf = {}
if os.path.exists("l169/raw_partial.npz"):
    z = np.load("l169/raw_partial.npz")   # L120 direction fix (l150 loaded l148)
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
    Xc_p25 = torch.zeros(n_cutk["cutng25"], 1)
    Xc_p25[old_pos_in_p25] = X0o
    Xc_p25[kept_new_cutcutng25] = X0n[kept_new_mask_p25]
    Xc_p25p = torch.zeros(n_cutk["cutng25p"], 1)
    Xc_p25p[old_pos_in_p25p] = X0o
    Xc_p25p[kept_new_cutcutng25p] = X0n[kept_new_mask_p25p]
    Xc_p23 = torch.zeros(n_cutk["cutng23"], 1)
    Xc_p23[old_pos_in_p23] = X0o
    Xc_p23[kept_new_cutcutng23] = X0n[kept_new_mask_p23]
    Xc_p26 = torch.zeros(n_cutk["cutng26"], 1)
    Xc_p26[old_pos_in_p26] = X0o
    Xc_p26[kept_new_cutcutng26] = X0n[kept_new_mask_p26]
    Xc_k5 = torch.zeros(n_cutk["cutk5"], 1)
    Xc_k5[old_pos_in_k5] = X0o
    Xc_k5[kept_new_cutk5] = X0n[kept_new_mask_k5]
    Xo65 = X0o.clone()
    X = dict(full=Xc_full.clone(), cut=Xc_cut.clone(),
             cut19=Xc_cut19.clone(), cut58=Xc_cut58.clone(),
             cutng19=Xc_ng19.clone(), cutng29=Xc_ng29.clone(),
             cutwA=Xc_wA.clone(), cutng25=Xc_p25.clone(),
             cutng25p=Xc_p25p.clone(),
             cutng23=Xc_p23.clone(), cutng26=Xc_p26.clone(),
             cutk5=Xc_k5.clone(),
             silW=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
             eMotBot5=Xc_wA.clone(),
             wAgN=Xc_wA.clone(), n25gW=Xc_p25.clone(),
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
                     cutng25=nzn[p25_pos_in_new],
                     cutng25p=nzn[p25p_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     silW=nzn[wA_pos_in_new], eMotTop5=nzn[wA_pos_in_new],
                     eMotBot5=nzn[wA_pos_in_new],
                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],
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
    # P-af (PREREG): swap arms are DELIBERATELY off the matched point.
    paf[seed] = dict(wAgN=af_c["wAgN"], n25gW=af_c["n25gW"],
                     cutwA=af_c["cutwA"], cutng25=af_c["cutng25"],
                     wAgN_above=bool(af_c["wAgN"] > AF_T),
                     n25gW_below=bool(af_c["n25gW"] < AF_T))
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
                     cutng25=nzn[p25_pos_in_new],
                     cutng25p=nzn[p25p_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     silW=nzn[wA_pos_in_new], eMotTop5=nzn[wA_pos_in_new],
                     eMotBot5=nzn[wA_pos_in_new],
                     wAgN=nzn[wA_pos_in_new], n25gW=nzn[p25_pos_in_new],
                     b65=nz_o)
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if sin_t > 0:
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            t = torch.relu(drive + BG)
            t = (t + noise[a]).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
            if a in CLAMP:
                X[a][CLAMP[a], 0] = 0.0
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
    np.savez("l169/raw_partial.npz", **store)
    log(f"seed {seed} done af {af_c} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l169/raw_l169.npz", K=K,
                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
                    g_silW=GAIN["silW"], g_eMotTop5=GAIN["eMotTop5"],
                    g_wAgN=GAIN["wAgN"], g_n25gW=GAIN["n25gW"],
                    g_eMotBot5=GAIN["eMotBot5"],
                    clamp_loc=np.array([467]), clamp_id=np.array([1110]),
                    g_full=G_NEW, g65=G65,
                    cut_drop=cut_drop, cut19_drop=cut19_drop,
                    cut58_drop=cut58_drop,
                    cutng19_drop=cutk_drop["cutng19"], cutng29_drop=cutk_drop["cutng29"],
                    cutwA_drop=cutk_drop["cutwA"],
                    cutng25_drop=cutk_drop["cutng25"],
                    cutng25p_drop=cutk_drop["cutng25p"],
                    cutng23_drop=cutk_drop["cutng23"],
                    cutng26_drop=cutk_drop["cutng26"],
                    cutk5_drop=cutk_drop["cutk5"],
                    e_edges=np.array([E_EDGES[a] for a in E_ARMS]),
                    new_mass=np.array([cutk_pins[a]["mass_removed"] for a in NEW_ARMS]),
                    mass_split=np.array([mass_split["glut19"], mass_split["other58"]]),
                    batches=np.array(SEEDS), **store)
log("raw_l169.npz checkpointed BEFORE analysis")

# ---------------- C0A-142 (L142): anchors vs raw_l135 + B29 absence -----
_prevs = ["l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
          "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
          "l122/raw_l122.npz", "l123/raw_l123.npz", "l124/raw_l124.npz",
          "l125/raw_l125.npz", "l126/raw_l126.npz", "l127/raw_l127.npz",
          "l128/raw_l128.npz", "l131/raw_l131.npz", "l133/raw_l133.npz",
          "l135/raw_l135.npz", "l137/raw_l137.npz",
          "l139/raw_l139_j0.npz", "l139/raw_l139_j1.npz",
          "l139/raw_l139_j2.npz", "l139/raw_l139_j3.npz",
          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",
          "l113/raw_l113.npz", "l142/raw_l142.npz",
          "l144/raw_l144.npz", "l145/raw_l145.npz",
          "l142/raw_partial.npz", "l144/raw_partial.npz",
          "l145/raw_partial.npz", "l148/raw_l148.npz",
          "l148/raw_partial.npz", "l150/raw_l150.npz",
          "l150/raw_partial.npz", "l154/raw_l154.npz",
          "l154/raw_partial.npz"]
for _p in _prevs:
    _zp = np.load(_p)
    assert not any(f"mm_full_{s}" in _zp.files for s in B35), \
        ("B35 collides with " + _p + " (STOP)")
log(f"B35 absence across {len(_prevs)} stored npzs: PASS")
_poolkeys150 = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _poolkeys150.append(f"{_pk}_{_c}{_s}")
C0A150_KEYS = ["mm", "xm"] + _poolkeys150
z135c = np.load("l135/raw_l135.npz")
_arms150 = ("full", "b65", "cutwA", "cutng25")
assert all(f"{_k}_{_a}_801" in z135c.files for _k in C0A150_KEYS
           for _a in _arms150), "C0A-148 coverage miss"
z144c = np.load("l144/raw_l144.npz")
assert all(f"{_k}_sil1110_wA_801" in z144c.files for _k in C0A150_KEYS), \
    "FC-144 coverage miss"
c0a150 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        for a in _arms150:
            c0a150[f"135_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z135c[f"{key}_{a}_{s}"][:WIN]).max())
    for a in _arms150:
        c0a150[f"135_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z135c[f"af_{a}_{s}"]))
c0a150_max = max(c0a150.values())
c0a150_pass = bool(all(v == 0.0 for v in c0a150.values()))
log(f"C0A-148 (4 arms x {len(C0A150_KEYS)} keys x 2 seeds) vs raw_l135: "
    f"{'PASS' if c0a150_pass else 'FAIL'} (max {c0a150_max:.1e})")
fc144 = {}
for s in (801, 901):
    for key in C0A150_KEYS:
        fc144[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_silW_{s}"]
            - z144c[f"{key}_sil1110_wA_{s}"][:WIN]).max())
    fc144[f"af_{s}"] = abs(float(store[f"af_silW_{s}"])
                           - float(z144c[f"af_sil1110_wA_{s}"]))
fc144_max = max(fc144.values())
fc144_pass = bool(all(v == 0.0 for v in fc144.values()))
log(f"FC-144 silW (24 keys x 2 seeds) vs raw_l144 sil1110_wA: "
    f"{'PASS' if fc144_pass else 'FAIL'} (max {fc144_max:.1e})")
z145c = np.load("l145/raw_l145.npz")
assert all(f"{_k}_eMotTop5_801" in z145c.files for _k in C0A150_KEYS), \
    "FC-145 coverage miss"
fc145 = {}
for _ea in ("eMotTop5", "eMotBot5"):
    for s in (801, 901):
        for key in C0A150_KEYS:
            fc145[f"{_ea}_{key}_{s}"] = float(np.abs(
                store[f"{key}_{_ea}_{s}"]
                - z145c[f"{key}_{_ea}_{s}"][:WIN]).max())
        fc145[f"{_ea}_af_{s}"] = abs(float(store[f"af_{_ea}_{s}"])
                                     - float(z145c[f"af_{_ea}_{s}"]))
fc145_max = max(fc145.values())
fc145_pass = bool(all(v == 0.0 for v in fc145.values()))
log(f"FC-145 eMot arms (2 x 24 keys x 2 seeds) vs raw_l145: "
    f"{'PASS' if fc145_pass else 'FAIL'} (max {fc145_max:.1e})")
# ---- C0-NT (PREREG): a swap arm bit-identical to its own-gain twin
# means the gain never entered the step loop -> VOID, read nothing.
nt = {}
for _sa, _tw in (("wAgN", "cutwA"), ("n25gW", "cutng25")):
    for s in (801, 901):
        nt[f"{_sa}_{s}"] = float(np.abs(
            store[f"mm_{_sa}_{s}"] - store[f"mm_{_tw}_{s}"]).max())
nt_pass = bool(all(v > 0.0 for v in nt.values()))
log(f"C0-NT swap-vs-own-gain mm separation: "
    f"{'PASS' if nt_pass else 'VOID'} (min {min(nt.values()):.3e})")
paf_ok = bool(all(d["wAgN_above"] and d["n25gW_below"] for d in paf.values()))
log(f"P-af direction (wAgN above / n25gW below AF_T) on "
    f"{len(paf)} seeds: {'PASS' if paf_ok else 'PARTIAL'}")
_afmis = {k: dict(wAgN=abs(d["wAgN"] - AF_T), n25gW=abs(d["n25gW"] - AF_T))
          for k, d in paf.items()}
log("af mismatch |af-AF_T| mean | wAgN "
    f"{np.mean([v['wAgN'] for v in _afmis.values()]):.4f} | n25gW "
    f"{np.mean([v['n25gW'] for v in _afmis.values()]):.4f}")
out = dict(g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
           g_cutwA_stored_exact=bool(GAIN["cutwA"] == G_CUTWA_STORED),
           g_cutng25_stored_exact=bool(GAIN["cutng25"] == G_CUTNG25_STORED),
           g_silW=GAIN["silW"], g_eMotTop5=GAIN["eMotTop5"],
           g_eMotBot5=GAIN["eMotBot5"],
           g_emottop5_stored_exact=bool(
               GAIN["eMotTop5"] == G_EMOTTOP5_STORED),
           g_emotbot5_stored_exact=bool(
               GAIN["eMotBot5"] == G_EMOTBOT5_STORED),
           clamp_loc=467, clamp_id=1110,
           e_band_ok=e_band_ok, new_stairs=new_stairs,
           e_edges=E_EDGES, K=K, mass_split=mass_split,
           n_seeds=len(SEEDS),
           c0a150_max=c0a150_max, c0a150_pass=c0a150_pass,
           fc144_max=fc144_max, fc144_pass=fc144_pass,
           fc145_max=fc145_max, fc145_pass=fc145_pass,
           g_wAgN=GAIN["wAgN"], g_n25gW=GAIN["n25gW"],
           nt=nt, nt_pass=nt_pass, paf=paf, paf_ok=paf_ok,
           af_target=AF_T,
           c0a_pass=bool(c0a150_pass and fc144_pass and fc145_pass
                         and nt_pass))
json.dump(out, open("l169/anchors_run.json", "w"), indent=1)
log(f"C0A-150 {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(c0a {out['c0a150_max']:.1e} | FC-144 {out['fc144_max']:.1e} | "
    f"FC-145 {out['fc145_max']:.1e}) | done {time.time()-t0:.0f}s")
