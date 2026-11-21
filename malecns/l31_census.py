"""L31: CX->DN CENSUS — endgame preflight (R1/L7 CX-gait).

Which CX cell types (EB/PB/FB columns) reach which DN families, at what hop
depth and weight — the static vocabulary a learned gait policy would act
through (L11: read at the DN port, never motor). Joins the L22 atlas
(DN family -> motor targets) and L24 laterality (L/R mirror organization) so
(d_L,d_R)-style DIAYN primitives are enumerable straight from the table
(tick-46 amendment, 2610.34638).

Parts:
  S1 DIRECT BLOCK: CX->DN edges, abs weight per DN type + net sign; per DN
     type the CX share of its TOTAL in-weight; top CX source types.
     Enrichment: 300-draw destination-swap null ON THE BLOCK (l20/l22 form,
     weights travel with source, in/out degrees kept) -> z per DN type
     (binomial-SE floor for never-hit types, l22 rule).
  S2 HOP PROFILE: min-hop from the CX population to every DN cell over abs
     weights (mm with [N,1] operands, L30 lesson; abs everywhere, L21);
     per DN type: median hop, frac cells reachable <=2; whole-DN histogram.
  S3 PRIMITIVE TABLE: join atlas + laterality -> one row per DN family:
     cells/L/R membership/ipsi-crossed org/motor target family (flex/ext/
     jump/top1)/direct CX weight + z + hop. Ranked by CX direct weight.
CPU-only, threads 8, no live changes. Sessions untouched.
"""
import collections
import json
import os
import re
import time

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
t0 = time.time()
rng = np.random.default_rng(20261111 + 31)
os.makedirs("l31", exist_ok=True)

ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].fillna("").astype(str).to_numpy()
typ = lab["type"].fillna("").astype(str).to_numpy()
cls = lab["class"].fillna("").astype(str).to_numpy()
side = lab["somaSide"].fillna("").astype(str).to_numpy()

cx = np.where(cls == "CX")[0]
dn = np.where(sup == "descending_neuron")[0]
print(f"CX {len(cx)} | DN {len(dn)} cells | {time.time()-t0:.0f}s", flush=True)

# ---- CX subregion from type name (FlyEM-style nomenclature) ----
def cx_region(x):
    x = str(x)
    if re.match(r"^(ER|EP|EL|ring)", x):
        return "EB"
    if re.match(r"^(PE|PB)", x):
        return "PB"
    if re.match(r"^(FB|FC\d|FS\d|FR\d|hDelta|Delta)", x):
        return "FB"
    if re.match(r"^(LNO|GLNO|LCNO|PFN)", x):
        return "NO/PFN"
    if re.match(r"^PFL", x):
        return "PFL(out)"
    if re.match(r"^ExR", x):
        return "ExR(out)"
    return "other"


cxreg = collections.Counter(cx_region(typ[i]) for i in cx)
print("CX regions:", dict(cxreg), flush=True)

# ---- S1 direct CX->DN block ----
rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
iscx = np.zeros(N, bool); iscx[cx] = True
isdn = np.zeros(N, bool); isdn[dn] = True
blk = isdn[rows] & iscx[cols]
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
B = len(b_dst)
print(f"direct CX->DN block: {B:,} edges, abs w {np.abs(b_w).sum():,.0f} "
      f"(net sign {b_w.sum():+,.0f}) | {time.time()-t0:.0f}s", flush=True)

dn_type_of = np.where(typ == "", "(untyped)", typ)
types_dn = sorted(set(dn_type_of[dn]))
tcode = {t: i for i, t in enumerate(types_dn)}
T = len(types_dn)
dst_c = np.array([tcode[dn_type_of[i]] for i in b_dst])
src_cx_type = np.where(typ[b_src] == "", "(untyped)", typ[b_src])

obs = np.bincount(dst_c, weights=np.abs(b_w), minlength=T)  # abs direct w
net = np.bincount(dst_c, weights=b_w, minlength=T)          # signed direct w
# per-DN-type total abs in-weight (for CX-share)
cell_in = np.abs(vals).copy()
sums = np.bincount(rows, weights=cell_in, minlength=N)
tot = np.bincount(np.array([tcode[dn_type_of[i]] for i in dn]),
                  weights=sums[dn], minlength=T)
cx_share = obs / (tot + 1e-12)
cnt = collections.Counter(dn_type_of[dn])
cells_t = np.array([cnt.get(t, 0) for t in types_dn])

# top CX SOURCE types by direct DN weight
cxsrc = collections.Counter()
for s, w in zip(src_cx_type, np.abs(b_w)):
    cxsrc[s] += float(w)
top_cxsrc = cxsrc.most_common(15)

# ---- S1b enrichment null: destination swaps within the block ----
NDRAW = 300
null = np.zeros((NDRAW, T))
pairs = set((b_dst.astype(np.int64) * N + b_src).tolist())
att = 10 * B
for d in range(NDRAW):
    dstv = b_dst.copy()
    ii = rng.integers(0, B, att)
    jj = rng.integers(0, B, att)
    for k in range(att):
        i, j = ii[k], jj[k]
        if i == j or b_src[i] == b_src[j] or dstv[i] == dstv[j]:
            continue
        ki, kj = dstv[i] * N + b_src[i], dstv[j] * N + b_src[j]
        ni, nj = dstv[j] * N + b_src[i], dstv[i] * N + b_src[j]
        if ni in pairs or nj in pairs:
            continue
        dstv[i], dstv[j] = dstv[j], dstv[i]
    null[d] = np.bincount(np.array([tcode[dn_type_of[x]] for x in dstv]),
                          weights=np.abs(b_w), minlength=T)
mu = null.mean(0)
sd = null.std(0)
print(f"null sanity: draws vary on {int((null.std(0) > 0).sum())}/{T} types, "
      f"null mean total {null.sum(1).mean():.2f} vs obs {obs.sum():.2f} "
      f"| {time.time()-t0:.0f}s", flush=True)
# binomial-SE floor for never-hit types (l22 rule): p_t from destination
# cells' block in-degree share, E_eff = B edges per draw
deg_t = np.bincount(dst_c, minlength=T).astype(np.float64)
p_t = deg_t / max(B, 1)
mean_w = np.abs(b_w).mean()
se_floor = np.sqrt(B * p_t * (1 - p_t)) * mean_w
sd = np.maximum(sd, np.maximum(se_floor, 1e-9))
z = (obs - mu) / sd
print(f"null {NDRAW} draws done | {time.time()-t0:.0f}s", flush=True)

# ---- S2 hop profile (abs weights, [N,1] operands) ----
Wc = W.to_sparse_coo().coalesce()
Wa = torch.sparse_coo_tensor(Wc.indices(), Wc.values().abs(),
                             Wc.shape).coalesce()
seen = np.zeros(N, bool)
cx_t = torch.from_numpy(cx).long()
cur = torch.zeros(N, 1)
cur[cx_t] = 1.0
seen[cx] = True
hop = np.full(N, -1, np.int16)
hop[cx] = 0
lvl = 0
while True:
    lvl += 1
    nxt = (torch.sparse.mm(Wa, cur) > 0).squeeze(1).numpy()
    nxt &= ~seen
    idx = np.where(nxt)[0]
    if len(idx) == 0 or lvl > 12:
        break
    hop[idx] = lvl
    seen[idx] = True
    cur = torch.zeros(N, 1)
    cur[torch.from_numpy(idx).long()] = 1.0
hop_dn = hop[dn]
hist = collections.Counter(int(h) for h in hop_dn)
reach_dn = int((hop_dn > 0).sum())
print(f"DN hop histogram: {dict(sorted(hist.items()))} "
      f"| reachable {reach_dn}/{len(dn)} | {time.time()-t0:.0f}s", flush=True)

# linearized 2-hop CX->DN weight (descriptive, abs product, no cancellation
# claim): cxvec -> hidden mass Wa@cx, then DN rows read it.
cxv = np.zeros((N, 1)); cxv[cx] = 1.0
h1 = torch.sparse.mm(Wa, torch.from_numpy(cxv).float())        # 1-hop mass
h2 = torch.sparse.mm(Wa, h1)                                   # 2-hop mass
lin2_cell = h2.squeeze(1).numpy()
lin2 = np.bincount(np.array([tcode[dn_type_of[i]] for i in dn]),
                   weights=lin2_cell[dn], minlength=T)
print(f"linearized 2-hop CX->DN abs mass total {lin2.sum():,.0f} "
      f"(vs direct {obs.sum():,.0f}) | {time.time()-t0:.0f}s", flush=True)

# S2b: decompose the 2-hop DN-arriving mass by INTERMEDIATE type (the relay
# station: CX -> x -> DN). Descriptive, same linearized-abs caveat.
blkind = isdn[rows]
r_d, s_d, w_d = rows[blkind].copy(), cols[blkind].copy(), vals[blkind].copy()
h1np = h1.squeeze(1).numpy()
contrib = np.abs(w_d) * h1np[s_d]          # mass this edge delivers from CX
relay = collections.Counter()
for s, c in zip(s_d, contrib):
    relay[typ[s] if typ[s] else "(untyped)"] += float(c)
top_relay = relay.most_common(20)
cls_of = {}
for s in set(s_d):
    t = typ[s]
    if t not in cls_of:
        cls_of[t] = f"{cls[s]}/{sup[s]}"
print("== top relay types CX->x->DN (lin mass, class) ==")
for k, v in top_relay:
    print(f"  {v:12.4f}  {k}  [{cls_of.get(k, '')}]")

# per DN type hop stats
med_hop, frac12 = np.zeros(T), np.zeros(T)
for ti, t in enumerate(types_dn):
    m = dn_type_of[dn] == t
    h = hop[dn][m]
    pos = h[h > 0]
    med_hop[ti] = float(np.median(pos)) if len(pos) else -1
    frac12[ti] = float((h <= 2).mean())  # hop<=2 incl. 1
# (hop 1 == direct edge exists for that CELL)

# ---- S3 primitive table: join atlas + laterality ----
atl = pd.read_csv("l22/atlas.csv").set_index("dn_type")
lat = pd.read_csv("l24/laterality.csv").set_index("dn_type")

rowsout = []
for ti, t in enumerate(types_dn):
    m = dn[dn_type_of[dn] == t]
    nL = int((side[m] == "L").sum()); nR = int((side[m] == "R").sum())
    org = ""
    if t in lat.index:
        r = lat.loc[t]
        if bool(r["has_both_sides"]):
            org = ("ipsi" if r["ipsi_idx"] > 0.1 else
                   "crossed" if r["ipsi_idx"] < -0.1 else "weak")
        li, liz = float(r["LI"]), float(r["LI_z"])
    else:
        li, liz = np.nan, np.nan
    a = atl.loc[t] if t in atl.index else None
    rowsout.append({
        "dn_type": t, "cells": int(len(m)), "nL": nL, "nR": nR,
        "cx_w_direct": float(obs[ti]), "cx_w_2hop_lin": float(lin2[ti]),
        "cx_z": float(z[ti]),
        "cx_share_in": float(cx_share[ti]), "net_sign": float(net[ti]),
        "med_hop": float(med_hop[ti]), "frac_hops_le2": float(frac12[ti]),
        "li": li, "li_z": liz, "org": org,
        "top1_motor": "" if a is None else a["top1_type"],
        "w_flex": np.nan if a is None else a["w_flex"],
        "w_ext": np.nan if a is None else a["w_ext"],
        "w_jump": np.nan if a is None else a["w_jump"],
    })
tab = pd.DataFrame(rowsout).sort_values("cx_w_direct", ascending=False)
tab.to_csv("l31/cx_dn.csv", index=False)

summary = {
    "cx_cells": int(len(cx)), "cx_regions": dict(cxreg),
    "dn_cells": int(len(dn)), "block_edges": int(B),
    "block_abs_w": float(np.abs(b_w).sum()),
    "block_net_w": float(b_w.sum()),
    "top_cx_sources": [[k, round(v, 1)] for k, v in top_cxsrc],
    "dn_hop_histogram": {str(k): int(v) for k, v in sorted(hist.items())},
    "dn_reachable": reach_dn,
    "n_types_total": T,
    "n_types_cx_direct": int((obs > 0).sum()),
    "lin2_total": float(lin2.sum()),
    "top20_by_2hop": (tab.sort_values("cx_w_2hop_lin", ascending=False)
                      .head(20).to_dict("records")),
    "top_relay_types": [[k, round(v, 4), cls_of.get(k, "?")]
                        for k, v in top_relay],
    "n_types_cx_direct_ge1pct_inw": int((cx_share > 0.01).sum()),
    "top20_by_cxw": tab.head(20).to_dict("records"),
    "annotated": {
        "notes": "z: 300-draw destination-swap null on the CX->DN block, "
                 "weights travel with source; binomial-SE floor for "
                 "never-hit. hop: min-hops from CX set over abs weights; "
                 "med_hop over reachable cells (-1 none). cx_share_in: "
                 "direct CX abs weight / type total abs in-weight. org from "
                 "L24 (ipsi_idx>0.1 ipsi / <-0.1 crossed). P1-labeled "
                 "static census; no dynamics claims.",
    },
}
with open("l31/results_l31.json", "w") as f:
    json.dump(summary, f, indent=1, default=str)

print("\n== TOP 15 DN families by direct CX weight ==")
print(tab.head(15).to_string(index=False,
      columns=["dn_type", "cells", "nL", "nR", "cx_w_direct", "cx_z",
               "cx_share_in", "med_hop", "org", "top1_motor", "w_flex",
               "w_ext", "w_jump"]))
nswap_probe = None  # sanity: verify nulls actually moved
print("\n== top CX source types (abs w) ==")
for k, v in top_cxsrc:
    print(f"  {v:12.4f}  {k}  ({cx_region(k)})")
print(f"\ndone {time.time()-t0:.0f}s -> l31/cx_dn.csv results_l31.json",
      flush=True)
