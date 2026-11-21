"""L24: STEERING-LATERALITY — which DN classes own LEFT vs RIGHT leg motor?

Static pass (this file):
  1. Per DN type (>=2 cells, >=5 block edges, l22 filter): L-target weight
     wL, R-target weight wR (motor somaSide), laterality index
     LI = (wL-wR)/(wL+wR). NULL: 500 draws permuting the motor side labels
     (keeps the 409/406 marginals + each type's total weight) -> z per type.
  2. L/R HOMOLOGUE test: for types with both L-soma and R-soma members,
     laterality of the L-members' edges (LI_L) vs R-members' (LI_R):
     mirrored channels => LI_L ~ -LI_R with both ipsi-leaning.
     IPSI INDEX = (LI_L - LI_R)/2 > 0 = both prefer their own side.
     NULL: permute DN member side labels WITHIN each type (500 draws),
     pooled ipsi-vs-contra weight z.
  3. Report ranked table + candidate list for the dynamic volley demo
     (types with an L cell AND an R cell, strongest |LI| or ipsi z).
CPU-only, no live changes.
"""
import collections
import json
import time

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
t0 = time.time()
rng = np.random.default_rng(20261111 + 24)

ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].fillna("").astype(str).to_numpy()
side = lab["somaSide"].fillna("").astype(str).to_numpy()   # L/R/M/''

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
mside = side[motor]
ML = np.where(mside == "L")[0]      # indices INTO motor array
MR = np.where(mside == "R")[0]
assert len(ML) == 409 and len(MR) == 406, (len(ML), len(MR))

# ---- DN->motor block (l22 extraction) ----
rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
mrow = np.zeros(N, bool); mrow[motor] = True
sdn = np.zeros(N, bool); sdn[dn] = True
blk = mrow[rows] & sdn[cols]
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
B = len(b_dst)
mpos = np.full(N, -1, np.int64); mpos[motor] = np.arange(len(motor))

cnt = collections.Counter(dn_typ)
types = sorted(set(typ[b_src]))
tcode = {t: i for i, t in enumerate(types)}
T = len(types)
src_c = np.array([tcode[t] for t in typ[b_src]])
dst_m = mpos[b_dst]                        # motor-cell index per edge
nedge = np.bincount(src_c, minlength=T)
keep = np.array([cnt.get(t, 0) >= 2 for t in types])
print(f"block {B:,} edges | {T} src types | {int(keep.sum())} >=2-cell", flush=True)

# ---- cell-level weight matrices (tiny: T x 815) ----
M = len(motor)
def wmat(mask_edges=None):
    S = np.zeros((T, M), np.float64)
    e = slice(None) if mask_edges is None else mask_edges
    np.add.at(S, (src_c[e], dst_m[e]), b_w[e])
    return S
S_all = wmat()                              # per DN type, all members
wtot = S_all.sum(1)

sL = np.zeros(M); sL[ML] = 1.0
sR = np.zeros(M); sR[MR] = 1.0
wL = S_all @ sL
wR = S_all @ sR
LI = (wL - wR) / (wtot + 1e-12)

# ---- NULL 1: permute motor side labels (500 draws) ----
NDRAW = 500
li_draws = np.zeros((NDRAW, T))
perm = np.arange(M)
for d in range(NDRAW):
    rng.shuffle(perm)
    lp = sL[perm]
    wLp = S_all @ lp
    li_draws[d] = (wLp - (wtot - wLp)) / (wtot + 1e-12)
mu1, sd1 = li_draws.mean(0), li_draws.std(0)
z1 = (LI - mu1) / np.maximum(sd1, 1e-6)

# ---- homologue split: per type, edges from L-soma members vs R-soma ----
dn_side = side[dn]                          # side of each DN cell
src_cell_side = side[b_src]                 # per edge
S_fromL = wmat(src_cell_side == "L")
S_fromR = wmat(src_cell_side == "R")
wlL, wlR = S_fromL @ sL, S_fromL @ sR        # L-soma members' L/R weights
wrL, wrR = S_fromR @ sL, S_fromR @ sR
tot_lr = wlL + wlR + wrL + wrR + 1e-12
LI_L = (wlL - wlR) / (wlL + wlR + 1e-12)     # laterality of LEFT-soma output
LI_R = (wrL - wrR) / (wrL + wrR + 1e-12)     # laterality of RIGHT-soma output
ipsi_idx = (LI_L - LI_R) / 2                 # >0: both lean ipsi (mirrored)

# members with both sides present?
has_both = np.zeros(T, bool)
type_members = collections.defaultdict(list)
for i, c in zip(dn, dn_side):
    type_members[typ[i]].append(c)
for i, t in enumerate(types):
    ss = type_members.get(t, [])
    has_both[i] = "L" in ss and "R" in ss

# ---- NULL 2: permute DN member sides WITHIN each type (500 draws) ----
# pooled statistic: total ipsi weight (Lsoma->L + Rsoma->R) / bilateral total
W_ipsi_obs = wlL.sum() + wrR.sum()
W_contra_obs = wlR.sum() + wrL.sum()
# build per-edge source-cell-type-local shuffle machinery:
# for each type, list of member cells with their sides; permute sides among
# members that HAVE block edges (weight-preserving per type only if we
# permute side labels of the edge-source cells within the type).
edge_type = src_c
b_src_side = src_cell_side
bilateral_mask = np.isin(b_src_side, ["L", "R"])
bt = edge_type[bilateral_mask]
bside = b_src_side[bilateral_mask]
# pooled draws
W_ipsi_draws = np.zeros(NDRAW)
# for the pooled test, shuffling within type = for each type, randomly
# reassign L/R labels to its bilateral edges preserving that type's
# L/R edge-count split (permutation of labels among that type's edges)
uni_t = np.unique(bt)
draws_ipsi_frac = np.zeros(NDRAW)
for d in range(NDRAW):
    new_side = bside.copy()
    for tt in uni_t:
        m = bt == tt
        vals_ = new_side[m]
        rng.shuffle(vals_)
        new_side[m] = vals_
    mLdst = mside[dst_m[bilateral_mask]] == "L"
    ipsi = np.sum(b_w[bilateral_mask][
        ((new_side == "L") & mLdst) | ((new_side == "R") & ~mLdst)])
    draws_ipsi_frac[d] = ipsi / (b_w[bilateral_mask].sum() + 1e-12)
obs_ipsi_frac = W_ipsi_obs / (W_ipsi_obs + W_contra_obs + 1e-12)
z_ipsi = (obs_ipsi_frac - draws_ipsi_frac.mean()) / (draws_ipsi_frac.std() + 1e-12)

# ---- table ----
recs = []
for i, t in enumerate(types):
    if nedge[i] < 5 or not keep[i]:
        continue
    recs.append(dict(
        dn_type=t, cells=int(cnt.get(t, 0)), edges=int(nedge[i]),
        wL=float(wL[i] / (wtot[i] + 1e-12)), wR=float(wR[i] / (wtot[i] + 1e-12)),
        LI=float(LI[i]), LI_z=float(z1[i]),
        has_both_sides=bool(has_both[i]),
        LI_L=float(LI_L[i]) if has_both[i] else np.nan,
        LI_R=float(LI_R[i]) if has_both[i] else np.nan,
        ipsi_idx=float(ipsi_idx[i]) if has_both[i] else np.nan,
    ))
tab = pd.DataFrame(recs)
tab["absLIz"] = tab.LI_z.abs()
tab.to_csv("l24/laterality.csv", index=False)

bi = tab[tab.has_both_sides & (tab.edges >= 10)].copy()
print(f"\n=== LATERALITY: {len(tab)} types | bilateral-membership types "
      f"(>=10 edges): {len(bi)} ===")
print(f"pooled IPSI fraction (bilateral types, Lsoma->L + Rsoma->R): "
      f"{obs_ipsi_frac:.4f} | null {draws_ipsi_frac.mean():.4f} "
      f"sd {draws_ipsi_frac.std():.4f} | z {z_ipsi:+.1f}")
print(f"\n--- top 15 by |LI z| (side-shuffle null) ---")
top = tab.reindex(tab.absLIz.sort_values(ascending=False).index)
print(top.head(15).to_string(
    columns=["dn_type", "cells", "edges", "wL", "wR", "LI", "LI_z",
             "has_both_sides"],
    float_format=lambda x: f"{x:.3f}", index=False))
print(f"\n--- top 12 bilateral types by |ipsi index| ---")
print(bi.reindex(bi.ipsi_idx.abs().sort_values(ascending=False).index)
      .head(12).to_string(
    columns=["dn_type", "cells", "edges", "LI", "LI_L", "LI_R", "ipsi_idx"],
    float_format=lambda x: f"{x:.3f}", index=False))

# ---- demo candidates: both an L and an R cell, strong laterality, leg mass ----
cand = bi[(bi.absLIz >= 5)].sort_values("absLIz", ascending=False)
print(f"\n--- DEMO CANDIDATES (both sides, |LI z|>=5): {len(cand)} ---")
print(cand.head(8).to_string(
    columns=["dn_type", "cells", "edges", "wL", "wR", "LI", "LI_z"],
    float_format=lambda x: f"{x:.3f}", index=False))

# anchors: DNg105/DNg95/DNp01 sides + member composition
for t in ("DNg105", "DNg95", "DNp01", "DNp02", "DNge079"):
    ss = type_members.get(t, [])
    if t in tcode:
        i = tcode[t]
        print(f"anchor {t}: members {collections.Counter(ss)} | "
              f"wL {wL[i]/(wtot[i]+1e-12):.3f} wR {wR[i]/(wtot[i]+1e-12):.3f} "
              f"LI {LI[i]:+.3f} z {z1[i]:+.1f}")

json.dump({
    "n_types": len(tab), "n_bilateral_10edge": int(len(bi)),
    "ndraw": NDRAW,
    "pooled_ipsi_fraction": float(obs_ipsi_frac),
    "pooled_ipsi_null_mean": float(draws_ipsi_frac.mean()),
    "pooled_ipsi_null_sd": float(draws_ipsi_frac.std()),
    "pooled_ipsi_z": float(z_ipsi),
    "n_side_lateralized_z5": int((tab.absLIz >= 5).sum()),
    "n_side_lateralized_z5_both": int((cand.shape[0])),
    "top_by_absLIz": top.head(20).to_dict("records"),
    "bilateral_by_ipsi": bi.reindex(
        bi.ipsi_idx.abs().sort_values(ascending=False).index)
        .head(20).to_dict("records"),
}, open("l24/results_l24_static.json", "w"), indent=1)
print(f"\nwrote l24/laterality.csv + results_l24_static.json | "
      f"{time.time()-t0:.0f}s", flush=True)
