import glob
import json
import math
import os
import re
import sys
import time
import zipfile

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(int(os.environ.get("L175_THREADS", "2")))
MODE = os.environ["L175_MODE"]
assert MODE in ("static", "census", "work"), MODE
WID = int(os.environ.get("L175_WID", "0"))
NW = int(os.environ.get("L175_NW", "1"))
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
ARMS = ["cutwA"]  # L175: per-mode / per-seed arm list assigned below
GAIN = dict(full=G_NEW, b65=G65, cutwA=None)
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
ANCH_BIT = [801, 901]               # bit-identity anchors (excluded from sample)
sys.path.insert(0, 'l197b')
import gj
import hashlib
SCHED = json.load(open('l197b/schedule.json'))
_FRZ = json.load(open('l197b/FREEZE.json'))
assert hashlib.sha256(open('l197b/PREREG.md','rb').read()).hexdigest() == _FRZ['prereg_sha256'], 'PREREG changed after freeze (STOP)'
assert hashlib.sha256(open('l197b/schedule.json','rb').read()).hexdigest() == _FRZ['schedule_sha256'], 'schedule changed after freeze (STOP)'
assert SCHED['gate']['pass'] is True, 'overlap gate REFUSED — no rollout'
assert all(SCHED['arms'][a]['overlap']['mean_overlap'] <= .25 for a in ('S', 'W'))
SEEDS_S, SEEDS_W = SCHED['arms']['S']['seeds'], SCHED['arms']['W']['seeds']
assert NW == 6 and 0 <= WID < NW
B39 = SEEDS_S[WID::NW] + SEEDS_W[WID::NW]   # this worker's fresh seeds
SEEDS = ANCH_BIT + B39
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S101 = json.load(open("l101/static.json"))["sizes"]
t0 = time.time()


def log(*a):
    print(f"[{MODE}{WID} {time.strftime('%H:%M:%S')}]", *a, flush=True)


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

# ======================= L175 GEN BLOCK (additive) =======================
# Generic single-cell arms on the cutwA (k=24) base: wA + ONE extra cell.
OUT="l197b"
n_new_total = int(keep_new.sum())
total_mass = float(cell_mass.sum())
ngmass = cell_mass[order[:K]][~is_glut[heav]]      # ng_desc order (l131_static form)
WIN_CELLS = [int(x) for x in ng_desc[24:58]]       # ranks 25..58
WIN_RANKS = list(range(25, 59))
assert len(WIN_CELLS) == 34 and len(set(WIN_CELLS)) == 34
# --- window / id pins re-derived from stored tables (never prose) ---
assert WIN_CELLS[0] == GI_CARRIER == S131["rank_ids"]["rank25"] == 1110
assert WIN_CELLS[1] == S131["rank_ids"]["rank26"] == 319
assert float(ngmass[24] / total_mass) == S131["rank_mass"]["rank25"]
assert float(ngmass[25] / total_mass) == S131["rank_mass"]["rank26"]
_r135 = json.load(open("l135/results_l135.json"))
assert _r135["xor"]["p2"]["rank25_id"] == 1110
assert _r135["xor"]["p2"]["rank26_id"] == 319
assert _r135["xor"]["p2"]["m25"] == float(ngmass[24] / total_mass)
assert _r135["xor"]["p2"]["m26"] == float(ngmass[25] / total_mass)
assert sorted(int(x) for x in ng_desc) == S121["ngladder"]["k58"]["drop_ids"]
assert [int(x) for x in np.sort(ng_desc[:24])] == \
    S131["prefix"]["cutwA"]["drop_ids"]
assert all(ngmass[i] >= ngmass[i + 1] for i in range(57)), "ng not mass-desc"

# --- out-weights onto the k=24-base closure (emask_wA = the cutwA edge set) ---
_ev = vals_all[emask_wA]
_es = src_all[emask_wA]
OW_RAW = np.zeros(Nall)
np.add.at(OW_RAW, _es, np.abs(_ev))
OW_EFF = np.zeros(Nall)          # model-true |Wb| column sum (inhibitory x BETA)
np.add.at(OW_EFF, _es, np.abs(_ev) * np.where(_ev < 0, BETA, 1.0))
OW_N = np.zeros(Nall, np.int64)
np.add.at(OW_N, _es, 1)
OW_MOT = np.zeros(Nall)          # raw |w| onto motor targets only
_em = tier_of_dst[dst_all[emask_wA]] == "motor_other"
np.add.at(OW_MOT, _es[_em], np.abs(_ev[_em]))
EFF_SIGN = np.where(is_glut, -np.abs(sign_all), sign_all).astype(np.float64)
_c1 = json.load(open("l169c/static.json"))["P1_carrier"]
assert _c1["gi"] == GI_CARRIER
assert int(OW_N[GI_CARRIER]) == _c1["out_edges"] == 80, int(OW_N[GI_CARRIER])
assert abs(float(OW_RAW[GI_CARRIER]) - _c1["out_mass"]) < 1e-9, \
    float(OW_RAW[GI_CARRIER])
# matrix-level cross-check: OW_EFF == |Wb_wA| column abs-sum (float32 tol)
_colsum = np.zeros(n_cutk["cutwA"])
np.add.at(_colsum, Wb_wA.col_indices().numpy(), np.abs(Wb_wA.values().numpy()))
for _g in (GI_CARRIER, 319):
    assert abs(_colsum[loc_wA[_g]] - OW_EFF[_g]) < 1e-3 * max(1.0, OW_EFF[_g]), _g
assert np.allclose(_colsum, OW_EFF[gi_wA], rtol=1e-4, atol=1e-3)
from pathlib import Path
nfiles=0
for archive in Path('.').rglob('*.npz'):
    if archive.parts[0]==OUT: continue
    with zipfile.ZipFile(archive) as z:
        assert all(not (set(map(int,re.findall(r'\d+',k))) & set(B39)) for k in z.namelist()),archive
    nfiles+=1
log('fresh keyscan PASS',nfiles)
in_wA = keep_cutk["cutwA"]
is_motor_g = np.zeros(Nall, bool)
is_motor_g[mg_all] = True
is_dng100_g = np.zeros(Nall, bool)
is_dng100_g[dng100_all] = True
GEN = {}
GEN_ARMS = []


def add_arm(name, extra_gi):
    """wA + one extra cell, through the lineage build()/wb()/pools_for()."""
    extra_gi = int(extra_gi)
    assert name not in GEN and name not in WB
    assert in_wA[extra_gi], (name, "cell absent from the k=24 base (STOP)")
    assert not is_motor_g[extra_gi] and not is_dng100_g[extra_gi], name
    drop = np.sort(np.concatenate([ng_desc[:24], np.array([extra_gi])]))
    assert len(set(int(x) for x in drop)) == 25
    keep = keep_new.copy()
    keep[drop] = False
    assert int(keep.sum()) == n_new_total - 25, name
    W, loc = build(keep)
    assert W.values().numel() == cutk_pins["cutwA"]["edges"] - int(
        ((src_all == extra_gi) | (dst_all == extra_gi))[emask_wA].sum()), name
    gi_a = np.where(keep)[0]
    old_mask = keep[gi_old]
    kept_mask = keep[new_g]
    GEN[name] = dict(
        extra=extra_gi, drop=drop, loc=loc, pos_in_new=loc_n[gi_a],
        old_mask=old_mask, old_pos=loc[gi_old[old_mask]],
        kept_mask=kept_mask, kept_new=loc[new_g[kept_mask]],
        edges=int(W.values().numel()), n=int(keep.sum()))
    POOLS[name] = pools_for(loc, keep)
    for pk in POOLS["cutwA"]:
        assert len(POOLS[name][pk]) == len(POOLS["cutwA"][pk]), (name, pk)
    mech[name] = np.where(mech_mask[keep])[0]
    _m = np.zeros(int(keep.sum()), bool)
    _m[loc[mg_all[keep[mg_all]]]] = True
    motor[name] = _m
    dng100[name] = np.sort(loc[dng100_all[keep[dng100_all]]])
    assert len(dng100[name]) == S92["dng100"], name
    WB[name] = wb(W)
    N_OF[name] = int(keep.sum())
    GAIN[name] = None
    GEN_ARMS.append(name)


def gen_init(name, X0o, X0n):
    """Lineage init form (Xc[old_pos]=X0o; Xc[kept_new]=X0n[kept_mask])."""
    g = GEN[name]
    Xc = torch.zeros(N_OF[name], 1)
    Xc[g["old_pos"]] = X0o[g["old_mask"]]
    Xc[g["kept_new"]] = X0n[g["kept_mask"]]
    return Xc.clone()


def LOC_OF(a):
    return loc_wA if a == "cutwA" else GEN[a]["loc"]


def atomic_savez(path, d):
    tmp = path[:-4] + ".tmp.npz"
    np.savez(tmp, **d)
    os.replace(tmp, path)


def atomic_json(path, obj):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    os.replace(tmp, path)


add_arm('sc25',1110)
if True:
    def _cert_gen(name, lin, Wb_ref, pos_ref, oldpos_ref, mask_ref, kn_ref):
        g = GEN[name]
        assert torch.equal(WB[name].crow_indices(), Wb_ref.crow_indices())
        assert torch.equal(WB[name].col_indices(), Wb_ref.col_indices())
        assert torch.equal(WB[name].values(), Wb_ref.values())
        assert np.array_equal(g["drop"], cutk_drop[lin])
        assert np.array_equal(g["pos_in_new"], pos_ref)
        assert g["old_mask"].all() and np.array_equal(g["old_pos"], oldpos_ref)
        assert np.array_equal(g["kept_mask"], mask_ref)
        assert np.array_equal(g["kept_new"], kn_ref)
        assert sorted(POOLS[name]) == sorted(POOLS[lin])
        for pk in POOLS[lin]:
            assert np.array_equal(POOLS[name][pk], POOLS[lin][pk]), pk
        assert np.array_equal(mech[name], mech[lin])
        assert np.array_equal(motor[name], motor[lin])
        assert np.array_equal(dng100[name], dng100[lin])
        assert N_OF[name] == N_OF[lin] and g["edges"] == cutk_pins[lin]["edges"]

    _cert_gen("sc25", "cutng25", Wb_p25, p25_pos_in_new, old_pos_in_p25,
              kept_new_mask_p25, kept_new_cutcutng25)
TRACK=[1110]; DM={}
assert LOC_OF('sc25')[1110]<0
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
              b65=Xo65.clone())
    for _ga in ARMS:
        if _ga in GEN:
            st[_ga] = gen_init(_ga, X0o, X0n)
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
                     b65=nz_o)
        for _ga in ARMS:
            if _ga in GEN:
                noise[_ga] = nzn[GEN[_ga]["pos_in_new"]]
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
                                  eMotTop5=g, eMotBot5=g))
        afs.append(float((st[arm] > 0.05).float().mean()))
    return float(np.mean(afs))

# ---------------- L175 bisects: stored-form loop, vectorized over arms ----
# Per-arm arithmetic IDENTICAL to the lineage stored-form loop (lo=.12,
# hi=.18, bracket assert, 24 halvings on bisect_af_mean, GAIN = lo). Arms
# are dynamically independent (each arm's state reads only its own W, its
# own gain and the seed-parameterized noise), so ONE settle pass serves
# every arm's own midpoint. Certified by g_cutwA / g_sc25 / g_sc26 ==
# stored floats EXACT.
def bisect_vec(arms):
    global ARMS
    _save = ARMS
    ARMS = list(arms)

    def af_mean(gd):
        acc = {a: [] for a in arms}
        for s in ANCH:
            st = settle_states(s, gd)
            for a in arms:
                acc[a].append(float((st[a] > 0.05).float().mean()))
        return {a: float(np.mean(acc[a])) for a in arms}

    lo_d = {a: 0.12 for a in arms}
    hi_d = {a: 0.18 for a in arms}
    af_lo_d, af_hi_d = af_mean(lo_d), af_mean(hi_d)
    for a in arms:
        log(f"{a} bracket af(0.12)={af_lo_d[a]:.5f} af(0.18)={af_hi_d[a]:.5f} "
            f"target {AF_T:.5f}")
        assert af_lo_d[a] < AF_T < af_hi_d[a], f"{a} bracket fail"
    for it in range(24):
        mid = {a: (lo_d[a] + hi_d[a]) / 2 for a in arms}
        afm = af_mean(mid)
        for a in arms:
            if afm[a] < AF_T:
                lo_d[a] = mid[a]
            else:
                hi_d[a] = mid[a]
    af_d = af_mean(lo_d)
    ARMS = _save
    return lo_d, af_d


assert ANCH == [11, 22, 33]
MY_ARMS=['sc25']
RAW_PATH,XM_PATH=OUT+f'/raw_w{WID}.npz',OUT+f'/xm_w{WID}.npz'; GAINS_PATH=OUT+f'/gains_w{WID}.json'
STORED_G = {"cutwA": G_CUTWA_STORED, "sc25": G_CUTNG25_STORED,
            "sc26": G_CUTNG25P_STORED}
new_stairs, af_final = {}, {}
if os.path.exists(GAINS_PATH):
    _gj = json.load(open(GAINS_PATH))
    assert sorted(_gj["gain"]) == sorted(["cutwA"] + MY_ARMS), "gains file arm drift"
    for _a, _g in _gj["gain"].items():
        GAIN[_a] = float(_g)
    new_stairs, af_final = _gj["stairs"], _gj["af_final"]
    log(f"gains loaded from {GAINS_PATH} (resume)")
else:
    _lo, _afd = bisect_vec(["cutwA"] + MY_ARMS)
    for _a in ["cutwA"] + MY_ARMS:
        GAIN[_a] = _lo[_a]
        af_final[_a] = _afd[_a]
        new_stairs[_a] = abs(_afd[_a] - AF_T)
        log(f"g_{_a} {_lo[_a]!r} | af_final {_afd[_a]:.6f} | "
            f"|af-target| {abs(_afd[_a] - AF_T):.2e}"
            + ("" if 0.14 <= _lo[_a] <= 0.16 else " [OUTSIDE .14-.16 — DISCLOSED]"))
for _a, _g in STORED_G.items():
    if _a == "cutwA" or _a in MY_ARMS:
        assert GAIN[_a] == _g, (_a, GAIN[_a], _g, "stored-form bisect drift (VOID)")
        log(f"g_{_a} == stored EXACT ({_g!r})")
atomic_json(GAINS_PATH, dict(gain={a: GAIN[a] for a in ["cutwA"] + MY_ARMS},
                             stairs=new_stairs, af_final=af_final,
                             stored_exact={a: bool(GAIN[a] == g)
                                           for a, g in STORED_G.items()
                                           if a == "cutwA" or a in MY_ARMS}))
log(f"bisects done {time.time()-t0:.0f}s")


def arms_for(seed):
    if MODE == "census":
        return ["cutwA"]
    if seed in ANCH_BIT:
        return ["cutwA"] + [a for a in MY_ARMS if a in ("sc25", "sc26")]
    return ["cutwA"] + MY_ARMS


_poolkeys = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _poolkeys.append(f"{_pk}_{_c}{_s}")
C0A_KEYS = ["mm", "xm"] + _poolkeys
assert len(C0A_KEYS) == 22
ANCH_PATH=OUT+f'/anchors_w{WID}.json'
def post_seed(seed):
    """C0A anchor the moment both 801/901 are rolled (early wiring verdict):
    cutwA vs raw_l135 cutwA; sc25 vs raw_l135 cutng25; sc26 vs cutng25p.
    Any non-zero = VOID: stop before a single fresh seed is rolled."""
    if seed != 901:
        return
    z135c = np.load("l135/raw_l135.npz")
    pairs = [("cutwA", "cutwA")] + [(a, l) for a, l in (("sc25", "cutng25"),
                                                      ("sc26", "cutng25p"))
                                    if a in MY_ARMS]
    c0a = {}
    for a, lin in pairs:
        for s in (801, 901):
            for key in C0A_KEYS:
                assert f"{key}_{lin}_{s}" in z135c.files, "C0A coverage miss"
                c0a[f"{a}~{lin}_{key}_{s}"] = float(np.abs(
                    store[f"{key}_{a}_{s}"] - z135c[f"{key}_{lin}_{s}"][:WIN]).max())
            c0a[f"{a}~{lin}_af_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                          - float(z135c[f"af_{lin}_{s}"]))
    mx = max(c0a.values())
    ok = bool(all(v == 0.0 for v in c0a.values()))
    atomic_json(ANCH_PATH, dict(c0a_pass=ok, c0a_max=mx, n_checks=len(c0a),
                                pairs=pairs, g_cutwA=GAIN["cutwA"],
                                g_cutwA_stored_exact=bool(
                                    GAIN["cutwA"] == G_CUTWA_STORED)))
    log(f"C0A-175 {pairs} x 22 keys + af x 2 seeds vs raw_l135: "
        f"{'PASS' if ok else 'FAIL'} (max {mx:.1e}, {len(c0a)} checks)")
    if not ok:
        log("C0A FAIL -> VOID, stopping before any fresh seed")
        sys.exit(3)


# ---------------- rollouts ----------------
store, XM = {}, {}
if os.path.exists(RAW_PATH) and os.path.exists(XM_PATH):
    z = np.load(RAW_PATH)
    store = {k: z[k] for k in z.files}
    z = np.load(XM_PATH)
    XM = {k: z[k] for k in z.files}
canonical=AMPA.copy()
for seed in SEEDS:
    AMPA=canonical.copy()
    if seed not in ANCH_BIT:
        _arm = 'S' if seed in SEEDS_S else 'W'
        _P = gj.DESIGN[_arm]['pulse']
        _on = gj.draw_onsets(_arm, seed)
        assert _on == SCHED['arms'][_arm]['onsets'][str(seed)], 'schedule drift (STOP)'
        for b,o in zip((0,4000),_on):
            AMPA[b+900:b+1400]=0
            assert not AMPA[b+500:b+1800].any()
            AMPA[b+o:b+o+_P]=ENT_AMP
        assert np.array_equal(AMPA>0, gj.expected_gate(_arm, _on))
    else:
        assert np.array_equal(AMPA, canonical)
    store[f'gate_{seed}']=AMPA>0
    carrier=np.empty(WIN,np.float32)
    ARMS = arms_for(seed)
    if f"mm_cutwA_{seed}" in store and f"xmean_cutwA_{seed}" in XM:
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
             b65=Xo65.clone())
    for _ga in ARMS:
        if _ga in GEN:
            X[_ga] = gen_init(_ga, X0o, X0n)
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
                     b65=nz_o)
        for _ga in ARMS:
            if _ga in GEN:
                noise[_ga] = nzn[GEN[_ga]["pos_in_new"]]
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
    xs = {a: torch.zeros(N_OF[a], dtype=torch.float64) for a in ARMS}
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
                     b65=nz_o)
        for _ga in ARMS:
            if _ga in GEN:
                noise[_ga] = nzn[GEN[_ga]["pos_in_new"]]
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
        carrier[k]=X['cutwA'][loc_wA[1110],0].item()
        for a in ARMS:
            xs[a] += X[a][:, 0]
            mm[a][k] = X[a][motor[a]].mean()
            xm[a][k] = X[a][mech[a]].mean()
            for kk in POOLS[a]:
                tr[a][kk][k] = X[a][POOLS[a][kk]].mean()
    store[f'GI1110_cutwA_{seed}']=carrier
    store[f'GI1110_sc25_{seed}']=np.full(WIN,np.nan,np.float32)
    for a in ARMS:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        for kk in POOLS[a]:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_c[a])
    for a in ARMS:
        _xv = (xs[a] / WIN).numpy()
        XM[f"xmean_{a}_{seed}"] = _xv.astype(np.float32)
        _lc = LOC_OF(a)[np.array(TRACK)]
        store[f"xwin_{a}_{seed}"] = np.where(
            _lc >= 0, _xv[np.maximum(_lc, 0)], np.nan).astype(np.float64)
    atomic_savez(RAW_PATH, store)
    atomic_savez(XM_PATH, XM)
    post_seed(seed)
    log(f"seed {seed} done af {af_c} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
assert json.load(open(ANCH_PATH))['c0a_pass']
atomic_json(OUT+f'/done_w{WID}.json', dict(wid=WID, nw=NW, seeds=SEEDS, n_fresh=len(B39),
    gain={a: GAIN[a] for a in ['cutwA']+MY_ARMS}, prereg_sha256=_FRZ['prereg_sha256'], secs=time.time()-t0))
log(f"worker {WID} DONE {time.time()-t0:.0f}s")
