"""L146 static: synapse-floor robustness census. PREREG l146/PREREG.md
FIRST. Verbatim l145_static.py extraction+pin slice (lines 1-366) + L146
census tail. Zero rollouts, no RNG."""
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

# ============ L146 census tail (synapse-floor robustness) ============
# PREREG l146/PREREG.md registered BEFORE this computation (S0-S4 + D1-D3).
# Floors act on the PAIR-LEVEL SUMMED syn count (convention registered).
# Zero rollouts, no RNG, deterministic.

S145 = json.load(open("l145/static.json"))
# S0 addendum: motor-edge syn values == l145 stored EXACT
mot_syn_l146 = sorted(int(x) for x in w_syn[out_mot])
mot_syn_145 = sorted(e["syn"] for e in S145["motor_edges_ranked"])
assert mot_syn_l146 == mot_syn_145, (mot_syn_l146, mot_syn_145)


def hist(w):
    w = np.asarray(w, np.int64)
    if w.size == 0:
        return dict(n=0, s1=0, s2=0, s3=0, eq3=0, min=-1, max=-1)
    return dict(n=int(w.size), s1=int((w == 1).sum()), s2=int((w == 2).sum()),
                s3=int((w >= 3).sum()), eq3=int((w == 3).sum()),
                min=int(w.min()), max=int(w.max()))


# --- S1 substrate ---
S1 = dict(
    all_in_graph_pairs=hist(w_syn),
    closure=hist(w_syn[emask_n]),
    wA_window=hist(w_syn[emask_wA]),
    deleted=dict(
        all_f2=int((w_syn < 2).sum()), all_f3=int((w_syn < 3).sum()),
        closure_f2=int((w_syn[emask_n] < 2).sum()),
        closure_f3=int((w_syn[emask_n] < 3).sum()),
        wA_f2=int((w_syn[emask_wA] < 2).sum()),
        wA_f3=int((w_syn[emask_wA] < 3).sum()),
    ),
)
# secondary: pre-collapse per-ROW distribution (in-graph rows)
conn["pre_gi"] = conn["pre_root_id"].astype(np.uint64).map(idx_all)
conn["post_gi"] = conn["post_root_id"].astype(np.uint64).map(idx_all)
row_in = conn["pre_gi"].notna() & conn["post_gi"].notna()
rows_syn = conn.loc[row_in, "syn_count"].to_numpy(np.int64)
S1["rows_pre_collapse"] = hist(rows_syn)

# --- S2 ng-58 cohort ---
ng58_set = cut58_drop
ng_out_m = emask_n & np.isin(src_all, ng58_set)
ng_in_m = emask_n & np.isin(dst_all, ng58_set)
per_cell = []
for c in ng58_set:
    mo = ng_out_m & (src_all == c)
    mi = ng_in_m & (dst_all == c)
    wo, wi = w_syn[mo], w_syn[mi]
    per_cell.append(dict(gi=int(c),
                         out_n=int(wo.size), out_s1=int((wo == 1).sum()),
                         in_n=int(wi.size), in_s1=int((wi == 1).sum())))
S2 = dict(out=hist(w_syn[ng_out_m]), in_=hist(w_syn[ng_in_m]),
          per_cell=per_cell,
          per_cell_share_out_s1=float(np.mean(
              [p["out_s1"] / p["out_n"] if p["out_n"] else 0.0
               for p in per_cell])))

# --- S3 carrier footprint ---
S3 = dict(
    out80=hist(w_syn[out_sel]), out_int70=hist(w_syn[out_int]),
    out_mot10=hist(w_syn[out_mot]), in13=hist(w_syn[in_sel]),
    survive=dict(
        out80_f2=int((w_syn[out_sel] >= 2).sum()),
        out80_f3=int((w_syn[out_sel] >= 3).sum()),
        out_int70_f2=int((w_syn[out_int] >= 2).sum()),
        out_int70_f3=int((w_syn[out_int] >= 3).sum()),
        out_mot10_f2=int((w_syn[out_mot] >= 2).sum()),
        out_mot10_f3=int((w_syn[out_mot] >= 3).sum()),
        in13_f2=int((w_syn[in_sel] >= 2).sum()),
        in13_f3=int((w_syn[in_sel] >= 3).sum()),
    ),
)

# --- S4 ladder re-derivation under floors ---
def ladder(floor):
    pm = w_syn >= floor
    om_f = out_rows & cord_of_dst & pm
    om_f = np.asarray(om_f)
    outmass_f = np.zeros(Nall)
    np.add.at(outmass_f, src_all[om_f], absv[om_f])
    cm = outmass_f[dn_new_g]
    tot = float(cm.sum())
    o = np.argsort(-cm)
    cum = np.cumsum(cm[o]) / tot
    K = int(np.searchsorted(cum, 0.50) + 1)
    heav_f = dn_new_g[o[:K]]
    ng_desc_f = heav_f[~is_glut[heav_f]]      # desc order (base form)
    heav_set = set(int(x) for x in heav)
    heav_f_set = set(int(x) for x in heav_f)
    jac = len(heav_set & heav_f_set) / len(heav_set | heav_f_set)
    ranks = {}
    for nm, g in (("carrier_1110", GI_CARRIER), ("twin_319", GI_TWIN)):
        w_ = np.where(ng_desc_f == g)[0]
        ranks[nm] = int(w_[0]) + 1 if w_.size else None
    # prefix mass_removed re-derivation (floor denominator), desc order
    ng_masses_desc = outmass_f[ng_desc_f]
    pref = {}
    for k in (19, 24, 25, 29):
        pref[f"ng{k}"] = round(float(ng_masses_desc[:k].sum() / tot), 4)
    return dict(
        floor=floor, K=K, n_glut=int(is_glut[heav_f].sum()),
        n_ng=int((~is_glut[heav_f]).sum()), jaccard_heavy=round(jac, 4),
        carrier_rank=ranks["carrier_1110"], twin_rank=ranks["twin_319"],
        prefix_mass_removed=pref,
        closure_edges=int((emask_n & pm).sum()),
        wA_edges=int((emask_wA & pm).sum()),
        heav_f_ids=[int(x) for x in np.sort(heav_f)][:5],  # spot ids
    )


# base re-derivation must reproduce the stored pins (floor=1 == base)
_base = ladder(1)
assert _base["K"] == K and _base["n_ng"] == 58 and _base["n_glut"] == 19, _base
assert _base["carrier_rank"] == 25 and _base["twin_rank"] == 26, _base
assert _base["prefix_mass_removed"]["ng19"] == 0.1946, _base
assert _base["prefix_mass_removed"]["ng29"] == 0.2588, _base
assert _base["prefix_mass_removed"]["ng24"] == 0.2286, _base  # wA form
assert _base["wA_edges"] == n_edges_wA, _base
# ADDENDUM A: f2/f3 came out VACUOUS-BY-RELEASE (every pair >= 3; pinned
# in PREREG l146/PREREG.md ADDENDUM A BEFORE this f4 computation).
S4 = dict(base=_base, f2=ladder(2), f3=ladder(3), f4=ladder(4))

# --- decision rule (registered D1-D3 + ADDENDUM A2 D4a-c) ---
f2 = S4["f2"]
sv = S3["survive"]
d1 = (f2["carrier_rank"] is not None and f2["twin_rank"] is not None
      and sv["out80_f2"] >= 48)   # >=60% of 80
d2 = ((f2["carrier_rank"] is None) or sv["out80_f2"] < 48
      or (S4["f3"]["carrier_rank"] is None and sv["out80_f3"] < 48))
decision = "D1_survives" if d1 else ("D2_breaks" if d2 else "D3_partial")
# A2: f2/f3 vacuous-by-release -> the informative read is f4
f4 = S4["f4"]
out80_f4 = int((w_syn[out_sel] >= 4).sum())
cr4 = f4["carrier_rank"]
d4a = (cr4 is not None and f4["twin_rank"] is not None
       and 19 <= cr4 <= 29 and out80_f4 >= 48)
d4b = (cr4 is None) or (out80_f4 < 48)
decision_a = ("D4a_robust_to_strongest_admissible_floor" if d4a
              else ("D4b_floor3_contingent" if d4b else "D4c_mixed"))
out_json = dict(
    design="L146 static: synapse-floor robustness census of the identity "
           "cliff (f2 keep>=2, f3 keep>=3, f4 keep>=4; pair-level summed "
           "syn). PREREG l146/PREREG.md FIRST + ADDENDUM A (f2/f3 "
           "VACUOUS-BY-RELEASE disclosed BEFORE f4 computed). Zero "
           "rollouts, no RNG.",
    carrier=dict(gi=1110, cell_type="DNp33", side="left",
                 nt="acetylcholine", ng_rank=25),
    S1_substrate=S1, S2_ng58=S2, S3_carrier=S3, S4_ladder=S4,
    decision=decision, decision_addendum=decision_a,
    decision_detail=dict(
        d1=d1, d2=d2,
        f2_carrier_rank=f2["carrier_rank"], f2_twin_rank=f2["twin_rank"],
        out80_f2=sv["out80_f2"], out80_f3=sv["out80_f3"],
        f4_carrier_rank=cr4, f4_twin_rank=f4["twin_rank"],
        out80_f4=out80_f4, d4a=d4a, d4b=d4b),
    convention="floors act on PAIR-LEVEL SUMMED syn_count (post-collapse, "
               "L62 form); per-ROW pre-collapse distribution is secondary "
               "descriptor S1.rows_pre_collapse; weights log1p(summed).",
)
import json as _json
import os as _os
_json.dump(out_json, open("l146/static.json", "w"), indent=1)
print(_json.dumps(out_json, indent=1))
print("L146 STATIC DONE", time.time() - t0)
