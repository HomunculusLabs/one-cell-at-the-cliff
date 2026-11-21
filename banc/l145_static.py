"""L142 static: PREREG-first; verbatim l135 extraction slice
(lines 18-338) + 1110 edge-footprint enumeration tail. Zero rollouts."""
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
        "cutng19", "cutng23", "cutwA", "cutng25", "cutng25p",
        "cutng26", "cutng29", "cutk5"]
GAIN = dict(full=G_NEW, b65=G65, cut=None, cut19=None, cut58=None,
            cutng19=None, cutng23=None, cutwA=None, cutng25=None,
            cutng25p=None, cutng26=None, cutng29=None, cutk5=None)
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
# (L131: cutng21/cutng28 not run — l126 single-batch points stand,
# DISCLOSED; C0A-123 retained on the 4 shared arms.)
ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B26 = list(range(3001, 3017))  # fresh, absent l113..l133 incl raw_l133
SEEDS = ANCH + B26                  # anchors FIRST: early wiring verdict
FRESH = B26
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


# ============ L142 static tail (edge-footprint enumeration) ============
# PREREG l142/PREREG.md registered BEFORE this computation's numbers are
# pinned into it (order: hypotheses first, feasibility numbers second).
GI_CARRIER = 1110            # DNp33-L, ng rank 25 (index 24)
GI_TWIN = 319                # DNpe025-R, ng rank 26 (index 25)
E_ARMS = ("eOutInt", "eOutMot", "eOutAll", "eIn", "eAll")

# rank re-pin (L131/L133 stored): rank 25 == 1110, rank 26 == 319
assert int(ng_desc[24]) == GI_CARRIER, (int(ng_desc[24]), "rank25 != 1110")
assert int(ng_desc[25]) == GI_TWIN, (int(ng_desc[25]), "rank26 != 319")

# cutwA keep + window edge mask (re-pin == l131 static)
keep_wA = keep_new.copy()
keep_wA[ng_desc[:24]] = False
n_wA = int(keep_wA.sum())
assert n_wA == S131["prefix"]["cutwA"]["n"], (n_wA, "wA n drift")
emask_wA = keep_wA[src_all] & keep_wA[dst_all]
n_edges_wA = int(emask_wA.sum())
assert n_edges_wA == cutk_pins["cutwA"]["edges"], (n_edges_wA, "wA edges drift")

# tier of dst (l135 lines 148-154 verbatim classes)
tier_dst = tier_of_dst

# ---- L145: motor-edge DOSE enumeration (top-5 / bottom-5 by mass) ----
# out/in masks recomputed exactly as L142 (verbatim forms)
tier_dst = tier_of_dst
out_sel = emask_wA & (src_all == GI_CARRIER)
out_int = out_sel & (tier_dst[dst_all] == "intrinsic")
out_mot = out_sel & (tier_dst[dst_all] == "motor_other")
absv = np.abs(vals_all)
total_dn_mass = float(cell_mass.sum())   # ladder mass convention


def _m(mask):
    return round(float(absv[mask].sum() / total_dn_mass), 6)


assert int(out_sel.sum()) == 80 and int(out_int.sum()) == 70
assert int(out_mot.sum()) == 10, int(out_mot.sum())
in_sel = emask_wA & (dst_all == GI_CARRIER)
assert int(in_sel.sum()) == 13, int(in_sel.sum())

# rank the 10 motor edges by |vals| DESC, tiebreak global edge pos ASC
mot_pos = np.where(out_mot)[0]
mot_ord = mot_pos[np.lexsort((mot_pos, -absv[mot_pos]))]
mot_w = absv[mot_ord]
mot_dst = dst_all[mot_ord]
mot_cnt = w_syn[mot_ord]
# per-edge destination identity for the dose table
ann_by_gi = ann.set_index("gi")
def _ident(g):
    try:
        r = ann_by_gi.loc[int(g)]
        return str(r.get("cell_type", "") or "")
    except Exception:
        return "?"
mot_table = [dict(pos=int(p), dst_gi=int(g), w=round(float(w), 6),
                  syn=int(c), dst_type=_ident(g))
             for p, g, w, c in zip(mot_pos, mot_dst, mot_w, mot_cnt)]
tie_note = "mass DESC, tiebreak global-pos ASC" if len(set(mot_w.tolist())) < 10 \
    else "all 10 masses distinct"
top5 = np.zeros_like(emask_wA)
top5[mot_ord[:5]] = True
bot5 = np.zeros_like(emask_wA)
bot5[mot_ord[5:]] = True
assert int(top5.sum()) == 5 and int(bot5.sum()) == 5
# subset law: top5 | bot5 == eOutMot edge set, EXACT positions
assert np.array_equal(np.where(top5 | bot5)[0], np.where(out_mot)[0]), \
    "top5|bot5 != eOutMot (STOP)"

E_ARMS = ("eOutMot", "eMotTop5", "eMotBot5", "eMotIn")
e_drop = {"eOutMot": out_mot, "eMotTop5": top5, "eMotBot5": bot5,
          "eMotIn": out_mot | in_sel}
arm_edges = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert arm_edges == {"eOutMot": 10, "eMotTop5": 5, "eMotBot5": 5,
                     "eMotIn": 23}, arm_edges
for a in E_ARMS:
    assert arm_edges[a] > 0, (a, "EMPTY edge set (STOP, L24 rule)")


def build_e(keep, drop):
    emask = keep[src_all] & keep[dst_all] & ~drop
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    gsign_a2 = sign_all[gsrc]
    gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)
    vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W


We = {a: build_e(keep_wA, e_drop[a]) for a in E_ARMS}
arm_nnz = {a: int(We[a].values().numel()) for a in E_ARMS}
for a in E_ARMS:
    assert arm_nnz[a] == n_edges_wA - arm_edges[a], (a, "nnz mismatch")
# structural cross-check vs L142 pins: eOutMot arm nnz must equal l142's
assert arm_nnz["eOutMot"] == 644167, arm_nnz["eOutMot"]

out_json = dict(
    design="L145 static: motor-edge DOSE (top-5/bottom-5 by |vals|) + "
           "eMotIn combo on the cutwA node set. Zero rollouts, no RNG. "
           "PREREG l145/PREREG.md FIRST. Subset law pinned: top5|bot5 == "
           "eOutMot edge positions EXACT.",
    carrier=dict(gi=GI_CARRIER, cell_type="DNp33", side="left",
                 nt="acetylcholine", ng_rank=25),
    motor_edges_ranked=mot_table,
    rank_rule=tie_note,
    mass_split=dict(
        mot_all=_m(out_mot), mot_top5=_m(top5), mot_bot5=_m(bot5),
        eMotIn=_m(e_drop["eMotIn"]),
        top5_share_of_mot=round(float(absv[top5].sum() / absv[out_mot].sum()), 4),
    ),
    arm_edge_counts=arm_edges,
    arm_mass_frac_dn={a: _m(emask_wA & e_drop[a]) for a in E_ARMS},
    arm_nnz=arm_nnz,
    mass_note="ladder convention (out-cord |vals| / dn out-cord total); "
              "eMotIn includes in-edge mass on the same denominator "
              "(disclosed, l142 form).",
)
import json as _json
import os as _os
_os.makedirs("l145", exist_ok=True)
_json.dump(out_json, open("l145/static.json", "w"), indent=1)
print(_json.dumps(out_json, indent=1))
print("L145 STATIC DONE")
