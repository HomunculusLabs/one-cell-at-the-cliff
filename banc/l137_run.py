"""L137 run (L141): the REGISTERED dynamic DNp33 probe — why does
removing 1110 (with ranks 1-24) flip kill->super while mass-twin 319
does nothing? Clamp/volley grid on the INTACT closure substrate:
{full, b65, sil1110, sil319, silrand1-3, vol1110+volrand, sil24},
fresh B27 3101-3116 (absent from ALL stored npzs, precheck passed).
L135 machinery verbatim (extraction, pools, draw order, noise); NO
bisect phase (ADDENDUM A1 — gains stored, certified by full/b65
bit-identity at 801/901 vs raw_l113 + raw_l135); probe census FIRST
(ADDENDUM A4, L95 form) -> VAMP; sil24 cells == cutwA drop (l131 pin).
CPU-only; raw checkpoint BEFORE analysis.
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
ARMS = ["full", "b65", "sil1110", "sil319", "silrand1", "silrand2",
        "silrand3", "vol1110", "volrand", "sil24"]
INT_ARMS = ARMS[2:]
GAIN = dict(full=G_NEW, b65=G65,
            **{a: G_NEW for a in INT_ARMS})
# L137 (ADDENDUM A1): zero bisects — all gains stored-form;
# certified by full/b65 bit-identity anchors at the tail.
ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B27 = list(range(3101, 3117))  # fresh, absent ALL stored npzs  # fresh, absent l113..l133 incl raw_l133
SEEDS = ANCH + B27                  # anchors FIRST: early wiring verdict
FRESH = B27
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

# ---- L137: intervention arms share the FULL graph (PREREG D) ----
for a in INT_ARMS:
    WB[a] = Wb_n
    N_OF[a] = n_new
    POOLS[a] = POOLS["full"]
    mech[a] = mech["full"]
    motor[a] = motor["full"]
    dng100[a] = dng100["full"]
assert len(dng100["sil24"]) == S92["dng100"]
# twins pinned (l131 static): rank25 = 1110 carrier, rank26 = 319 neutral
assert int(ng_desc[24]) == 1110 and int(ng_desc[25]) == 319, "twin pins"
_pn = lambda g: int(loc_n[int(g)])
POOL56 = np.array(sorted(int(x) for x in ng_desc
                         if int(x) not in (1110, 319)))
assert len(POOL56) == 56
_rng = np.random.default_rng(20261118)
_rand4 = _rng.choice(POOL56, size=4, replace=False)
assert not np.isin(_rand4, (1110, 319)).any()
CLAMP = {a: torch.tensor([_pn(g)]) for a, g in
         (("sil1110", 1110), ("sil319", 319),
          ("silrand1", int(_rand4[0])), ("silrand2", int(_rand4[1])),
          ("silrand3", int(_rand4[2])))}
CLAMP["sil24"] = torch.tensor([_pn(g) for g in cutk_drop["cutwA"]])
assert len(CLAMP["sil24"]) == 24
VOLLEY_CELL = {"vol1110": _pn(1110), "volrand": _pn(int(_rand4[3]))}
CEN_IDS = [1110, 319] + [int(x) for x in ng_desc]
CEN_POS = torch.tensor([_pn(g) for g in CEN_IDS], dtype=torch.long)
log(f"interventions: silrand {list(map(int, _rand4[:3]))} volrand "
    f"{int(_rand4[3])} | sil24 n=24 | census n={len(CEN_IDS)}")
VAMP = None  # set by the probe below (ADDENDUM A4)

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
                     b65=nz_o,
                     **{a: nzn for a in INT_ARMS})
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


# ---------------- L137: NO bisect phase (ADDENDUM A1) ----------------
# settle_states/af_of retained verbatim above (reference, uncalled).

# ---------------- rollouts ----------------
# ---------------- L137 probe (ADDENDUM A4): ONE base rollout --------
# Full arm ONLY at seed 3101, L95 form: window u/X census for the twins
# + all ng-58 -> VAMP = |u_min(1110)| + .1. Same generator seeds and
# draw order as the main loop => main-pass full@3101 must reproduce
# these traces bit-identically (free anchor, checked at the tail).
def probe_full(seed):
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Xf = torch.zeros(n_new, 1)
    Xf[old_pos_in_new] = X0o
    Xf[new_pos] = X0n
    Ivf = torch.zeros(n_new, 1)
    Ivf[dng100["full"]] = D
    sp = 0.0
    for _ in range(SETTLE):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        drive = torch.sparse.mm(WB["full"], Xf) * GAIN["full"] + Ivf
        drive[mech["full"], 0] = drive[mech["full"], 0] + sin_t
        Xf = Xf + (DT / TAU) * ((torch.relu(drive + BG) + nzn)
                                .clamp(max=RMAX) - Xf)
    cen_u_l = np.zeros((len(CEN_POS), WIN), np.float32)
    cen_x_l = np.zeros((len(CEN_POS), WIN), np.float32)
    mm = np.zeros(WIN, np.float32)
    xm = np.zeros(WIN, np.float32)
    tr = {kk: np.zeros(WIN, np.float32) for kk in POOLS["full"]}
    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        drive = torch.sparse.mm(WB["full"], Xf) * GAIN["full"] + Ivf
        if sin_t > 0:
            drive[mech["full"], 0] = drive[mech["full"], 0] + sin_t
        cen_u_l[:, k] = (drive[CEN_POS, 0] + BG).numpy()
        t = torch.relu(drive + BG)
        t = (t + nzn).clamp(max=RMAX)
        Xf = Xf + (DT / TAU) * (t - Xf)
        cen_x_l[:, k] = Xf[CEN_POS, 0].numpy()
        mm[k] = Xf[motor["full"]].mean()
        xm[k] = Xf[mech["full"]].mean()
        for kk in POOLS["full"]:
            tr[kk][k] = Xf[POOLS["full"][kk]].mean()
    return cen_u_l, cen_x_l, mm, xm, tr


cen_u, cen_x, probe_mm, probe_xm, probe_tr = probe_full(3101)
VAMP = abs(float(cen_u[CEN_IDS.index(1110)].min())) + 0.1
assert VAMP > 0
log(f"probe done {time.time()-t0:.0f}s | VAMP {VAMP:.4f} "
    f"(1110 u_min {float(cen_u[CEN_IDS.index(1110)].min()):+.4f})")

store = {}
if os.path.exists("l137/raw_partial.npz"):
    z = np.load("l137/raw_partial.npz")
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
    X = dict(full=Xc_full.clone(), b65=Xo65.clone(),
             **{a: Xc_full.clone() for a in INT_ARMS})
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
                     b65=nz_o,
                     **{a: nzn for a in INT_ARMS})
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
                     cutng25=nzn[p25_pos_in_new],
                     cutng25p=nzn[p25p_pos_in_new],
                     cutng23=nzn[p23_pos_in_new],
                     cutng26=nzn[p26_pos_in_new],
                     cutk5=nzn[k5_pos_in_new],
                     b65=nz_o,
                     **{a: nzn for a in INT_ARMS})
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        for a in ARMS:
            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if sin_t > 0:
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t
            if a in VOLLEY_CELL:
                drive[VOLLEY_CELL[a], 0] = drive[VOLLEY_CELL[a], 0] + VAMP
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
    np.savez("l137/raw_partial.npz", **store)
    log(f"seed {seed} done af {af_c} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l137/raw_l137.npz",
                    g_full=G_NEW, g65=G65, vamp=np.float64(VAMP),
                    census_ids=np.array(CEN_IDS),
                    census_u=cen_u, census_x=cen_x,
                    silrand_ids=_rand4.astype(np.int64),
                    clamp_sil24=np.array([int(x) for x in cutk_drop["cutwA"]],
                                         np.int64),
                    batches=np.array(SEEDS), **store)
log("raw_l137.npz checkpointed BEFORE analysis")

# ---------------- anchors (ADDENDUM A1/A4) ----------------
zprev = np.load("l113/raw_l113.npz")
z135a = np.load("l135/raw_l135.npz")
C0A_KEYS = ["mm", "xm"] + [f"{k}_{c}{s}" for k in ("Ti", "Tr")
                           for c in ("f", "e") for s in ("L", "R")]
assert all(f"{k}_full_801" in zprev.files for k in C0A_KEYS)
assert all(f"{k}_full_801" in z135a.files for k in C0A_KEYS)
# B27 freshness across the whole stored shelf (precheck re-assert)
for _prev in ("l113/raw_l113.npz", "l115/raw_l115.npz",
              "l117/raw_l117.npz", "l118/raw_l118.npz",
              "l119/raw_l119.npz", "l120/raw_l120.npz",
              "l121/raw_l121.npz", "l122/raw_l122.npz",
              "l123/raw_l123.npz", "l124/raw_l124.npz",
              "l125/raw_l125.npz", "l126/raw_l126.npz",
              "l127/raw_l127.npz", "l128/raw_l128.npz",
              "l131/raw_l131.npz", "l133/raw_l133.npz",
              "l135/raw_l135.npz",
              "l139/raw_l139_j0.npz", "l139/raw_l139_j1.npz",
              "l139/raw_l139_j2.npz", "l139/raw_l139_j3.npz",
              "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz"):
    _zp = np.load(_prev)
    assert not any(f"mm_full_{s}" in _zp.files for s in B27), \
        ("B27 collides with " + _prev + " (STOP)")
    _zp.close()
ANCH_ARMS = ("full", "b65")
c0a = {}
c0a135 = {}
for s in (801, 901):
    for key in C0A_KEYS:
        for a in ANCH_ARMS:
            c0a[f"113_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - zprev[f"{key}_{a}_{s}"][:WIN]).max())
            c0a135[f"135_{key}_{a}_{s}"] = float(np.abs(
                store[f"{key}_{a}_{s}"] - z135a[f"{key}_{a}_{s}"][:WIN]).max())
    for a in ANCH_ARMS:
        c0a[f"113_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                     - float(zprev[f"af_{a}_{s}"]))
        c0a135[f"135_af_{a}_{s}"] = abs(float(store[f"af_{a}_{s}"])
                                        - float(z135a[f"af_{a}_{s}"]))
c0a_pass = bool(all(v == 0.0 for v in c0a.values()))
c0a135_pass = bool(all(v == 0.0 for v in c0a135.values()))
log(f"C0A full/b65 vs raw_l113: {'PASS' if c0a_pass else 'FAIL'} "
    f"(max {max(c0a.values()):.1e}) | vs raw_l135: "
    f"{'PASS' if c0a135_pass else 'FAIL'} (max {max(c0a135.values()):.1e})")
# probe anchor (ADDENDUM A4): deterministic same-generator reroll
probe_keys = ["mm", "xm"] + sorted(POOLS["full"])
pa = {"mm": float(np.abs(store["mm_full_3101"] - probe_mm).max()),
      "xm": float(np.abs(store["xm_full_3101"] - probe_xm).max())}
for key in sorted(POOLS["full"]):
    pa[key] = float(np.abs(store[f"{key}_full_3101"]
                           - probe_tr[key]).max())
probe_pass = bool(all(v == 0.0 for v in pa.values()))
log(f"PROBE anchor full@3101 reroll: {'PASS' if probe_pass else 'FAIL'} "
    f"(max {max(pa.values()):.1e}, {len(pa)} keys)")


def _census(cid):
    i = CEN_IDS.index(cid)
    return dict(u_min=float(cen_u[i].min()), u_mean=float(cen_u[i].mean()),
                u_max=float(cen_u[i].max()), x_mean=float(cen_x[i].mean()))


cen_1110 = _census(1110)
cen_319 = _census(319)
log(f"census 1110 {cen_1110} | 319 {cen_319} | VAMP {VAMP:.4f}")
out = dict(c0a_pass=c0a_pass, c0a_max=max(c0a.values()),
           c0a135_pass=c0a135_pass, c0a135_max=max(c0a135.values()),
           probe_pass=probe_pass, probe_max=max(pa.values()),
           vamp=VAMP, census_1110=cen_1110, census_319=cen_319,
           silrand=[int(x) for x in _rand4],
           clamp_sil24_n=len(CLAMP["sil24"]),
           n_seeds=len(SEEDS))
json.dump(out, open("l137/anchors_run.json", "w"), indent=1)
log(f"anchors written | done {time.time()-t0:.0f}s")
