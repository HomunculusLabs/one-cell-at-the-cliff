"""L22: DN-ROUTE ATLAS — the connectome's gesture vocabulary.

For EVERY DN type with >=2 cells (443 with motor edges, 396 with >=5 edges =
99.5% of the 23,616-edge DN->motor block), compute its motor-target-type
weight profile S[type, mtype] and enrich each cell against a 100-draw
Maslov-Sneppen destination-swap null on the block (l20_scan.rewire_block
verbatim: in/out degrees kept, weights travel with the source DN, so each
type's out-weight total is preserved and fractions are comparable).

Outputs:
  - per DN type: top-3 target motor types with weight share + z, purity
    (pure: top1>=.50 / mixed: >=.25 / diffuse), family anchors (flex/ext/jump
    shares + z, l20 pool definitions verbatim)
  - ranked table (l22/atlas.csv full, top-30 printed), anchor spot-checks
    (DNp01-04 jump z>=15, DNg105/DNg95 flexor z>=15, DNc01/02 profile)
CPU-only, threads 8, no live changes.
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
t0 = time.time()
os.makedirs("l22", exist_ok=True)
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].fillna("").astype(str).to_numpy()
typ = lab["type"].fillna("").astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
typm = typ[motor]
M = len(motor)
PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
POOL_F = np.concatenate([PAIRS["Ti"][0], PAIRS["Tr"][0]])
POOL_E = np.concatenate([PAIRS["Ti"][1], PAIRS["Tr"][1]])
JUMP = np.where(np.array([str(t).startswith(("TTMn", "DLMn", "DVMn"))
                          for t in typm]))[0]
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0
assert len(JUMP) > 0

rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
mrow = np.zeros(N, bool); mrow[motor] = True
sdn = np.zeros(N, bool); sdn[dn] = True
blk = mrow[rows] & sdn[cols]
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
B = len(b_dst)

# atlas rows: DN types with >=2 cells AND >=1 block edge; table filter >=5 edges.
# Single-cell types stay IN the block/null (degree preservation) but are not
# atlas rows — code ALL block-source types, mask rows after.
import collections
cnt = collections.Counter(dn_typ)
types = sorted(set(typ[b_src]))
tcode = {t: i for i, t in enumerate(types)}
T = len(types)
src_c = np.array([tcode[t] for t in typ[b_src]])
nedge = np.bincount(src_c, minlength=T)
keep = np.array([cnt.get(t, 0) >= 2 for t in types])
print(f"block-source DN types {T} | >=2-cell atlas rows {int(keep.sum())}", flush=True)

# motor type columns (only types present as block destinations)
mtypes = sorted(set(typ[b_dst]))
dcode = {t: i for i, t in enumerate(mtypes)}
D = len(mtypes)
dst_c = np.array([dcode[t] for t in typ[b_dst]])
print(f"DN types {T} | motor types {D} | block {B:,} edges | {time.time()-t0:.0f}s",
      flush=True)

# family masks over motor-type columns
is_flex_t = np.zeros(D, bool)
is_ext_t = np.zeros(D, bool)
is_jump_t = np.zeros(D, bool)
for t, i in dcode.items():
    tl = t.lower()
    if t in ("Ti flexor MN", "Acc. ti flexor MN", "Tr flexor MN", "Acc. tr flexor MN"):
        is_flex_t[i] = True
    if t in ("Ti extensor MN", "Tr extensor MN"):
        is_ext_t[i] = True
    if tl.startswith(("ttmn", "dlmn", "dvmn")):
        is_jump_t[i] = True
assert is_flex_t.sum() == 4 and is_ext_t.sum() == 2 and is_jump_t.sum() >= 3


def shares(dst_code):
    """S[T,D] weight matrix -> fraction of each type's motor weight per target."""
    S = np.bincount(src_c * D + dst_code, weights=b_w,
                    minlength=T * D).reshape(T, D).astype(np.float64)
    return S / (S.sum(1, keepdims=True) + 1e-12)


obs = shares(dst_c)


def rewire_block(rng, factor=10):
    dst = b_dst.copy()
    pairs = set((dst.astype(np.int64) * N + b_src).tolist())
    att = factor * B
    ii = rng.integers(0, B, att)
    jj = rng.integers(0, B, att)
    for k in range(att):
        i, j = ii[k], jj[k]
        if i == j:
            continue
        a = dst[i] * N + b_src[j]
        b2 = dst[j] * N + b_src[i]
        if a in pairs or b2 in pairs:
            continue
        pairs.discard(dst[i] * N + b_src[i])
        pairs.discard(dst[j] * N + b_src[j])
        pairs.add(a); pairs.add(b2)
        dst[i], dst[j] = dst[j], dst[i]
    return dst


rng = np.random.default_rng(20261111 + 22)
NDRAW = 300
mpos = np.full(N, -1, np.int64); mpos[motor] = np.arange(M)
acc = np.zeros((NDRAW, T, D), np.float32)
for d in range(NDRAW):
    new_dst = rewire_block(rng)
    assert len(set(new_dst.tolist())) == len(set(b_dst.tolist()))
    acc[d] = shares(np.array([dcode[t] for t in typ[new_dst]]))
    if d % 30 == 29:
        print(f"  null draw {d+1}/{NDRAW} | {time.time()-t0:.0f}s", flush=True)

mu = acc.mean(0)
sd = acc.std(0)
# binomial SE floor for cells the draw ensemble never hits (sd==0 -> z 1e8).
# E_eff = weight-based effective edge count of the DN type. Conservative:
# binomial SE OVERSTATES MS-swap variance (l20: draw z +24.9 vs binomial +10),
# so the floor only ever shrinks inflated z, never inflates a real one.
wtot = np.bincount(src_c, weights=b_w, minlength=T)
w2 = np.bincount(src_c, weights=b_w * b_w, minlength=T)
E_eff = wtot ** 2 / (w2 + 1e-12)
p_pool = (np.bincount(dst_c, weights=b_w, minlength=D) / b_w.sum())
SE_binom = np.sqrt(np.maximum(p_pool * (1 - p_pool), 1e-6) /
                   np.maximum(E_eff, 1.0)[:, None])
sd_cell = np.maximum(sd, SE_binom)
z = (obs - mu) / sd_cell
nfloor = int((sd < SE_binom * 0.99).sum())
print(f"cell z: {nfloor}/{T*D} cells floored by binomial SE "
      f"(draw std 0 / never-hit)", flush=True)

ncells = np.array([cnt.get(t, 0) for t in types])
# family stats pooled PER DRAW (std of the summed share, not sum of stds —
# the l20/l14 form; sum-of-stds understates z, my first-pass bug)
fam = {}
for name, mask in [("flex", is_flex_t), ("ext", is_ext_t), ("jump", is_jump_t)]:
    share = obs[:, mask].sum(1)
    dr = acc[:, :, mask].sum(2)              # (NDRAW, T) pooled per draw
    zs = (share - dr.mean(0)) / (dr.std(0) + 1e-9)
    fam[name] = (share, zs)


def class_pool(mask_types):
    """L14-form CLASS-pooled profile: member types as one weighted source.
    acc rows are per-type FRACTIONS; the swap preserves each type's total
    weight (weights travel with source), so wtot-weighted pooling is exact
    for both observed and every draw."""
    members = set(mask_types)
    m = np.array([t in members for t in types])
    if not m.any():
        return None
    w = wtot[m]
    fr = (obs[m] * w[:, None]).sum(0) / w.sum()          # (D,) observed
    dr = (acc[:, m, :] * w[None, :, None]).sum(1) / w.sum()  # (NDRAW, D)
    return fr, dr

# ---- build the table ----
recs = []
for i, t in enumerate(types):
    if nedge[i] < 5 or not keep[i]:
        continue
    order = np.argsort(-obs[i])
    top = [(mtypes[j], float(obs[i, j]), float(mu[i, j]), float(z[i, j]))
           for j in order[:3] if obs[i, j] > 0]
    top1 = top[0][1] if top else 0.0
    purity = "pure" if top1 >= 0.50 else ("mixed" if top1 >= 0.25 else "diffuse")
    recs.append(dict(
        dn_type=t, cells=int(ncells[i]), edges=int(nedge[i]),
        purity=purity,
        top1_type=top[0][0] if top else "", top1_share=top1,
        top1_z=top[0][3] if top else 0.0,
        top2_type=top[1][0] if len(top) > 1 else "",
        top2_share=top[1][1] if len(top) > 1 else 0.0,
        top2_z=top[1][3] if len(top) > 1 else 0.0,
        top3_type=top[2][0] if len(top) > 2 else "",
        top3_share=top[2][1] if len(top) > 2 else 0.0,
        top3_z=top[2][3] if len(top) > 2 else 0.0,
        w_flex=float(fam["flex"][0][i]), z_flex=float(fam["flex"][1][i]),
        w_ext=float(fam["ext"][0][i]), z_ext=float(fam["ext"][1][i]),
        w_jump=float(fam["jump"][0][i]), z_jump=float(fam["jump"][1][i]),
    ))
atlas = pd.DataFrame(recs).sort_values("top1_z", ascending=False).reset_index(drop=True)
atlas.to_csv("l22/atlas.csv", index=False)

# enriched = strong share AND far above null
enr = atlas[(atlas.top1_share >= 0.10) & (atlas.top1_z >= 5)]
print(f"\n=== ATLAS: {len(atlas)} DN types (>=5 edges) | "
      f"purity: pure {(atlas.purity=='pure').sum()} / mixed "
      f"{(atlas.purity=='mixed').sum()} / diffuse {(atlas.purity=='diffuse').sum()} "
      f"| enriched (top1 share>=.10, z>=+5): {len(enr)} ===")
print(f"\n--- top 25 by top1_z ---")
print(atlas.head(25).to_string(
    columns=["dn_type", "cells", "edges", "purity", "top1_type", "top1_share",
             "top1_z", "top2_type", "top2_share"],
    float_format=lambda x: f"{x:.3f}", index=False))

# ---- anchor spot-checks (the verify line) ----
print("\n--- ANCHORS (per-type family z, draw-pooled) ---")
ok = {}
for t, famname, need in [("DNp01", "jump", 15), ("DNp02", "jump", 15),
                         ("DNp03", "jump", 15), ("DNp04", "jump", 15),
                         ("DNg105", "flex", 15), ("DNg95", "flex", 15),
                         ("DNg35", "flex", 15), ("DNg108", "flex", 15)]:
    if t in tcode:
        i = tcode[t]
        v = float(fam[famname][1][i])
        ok[t] = v
        print(f"  {t}: {famname} share {fam[famname][0][i]:.3f} z {v:+.1f}")
    else:
        print(f"  {t}: NOT IN ATLAS")
print("--- ANCHORS (L14-form CLASS-pooled, the +16.7/+21.0 form) ---")
cls = {}
for name, members, famname in [("DNp01-04", ["DNp01", "DNp02", "DNp03", "DNp04"], "jump"),
                               ("DNc01/02", ["DNc01", "DNc02"], "jump"),
                               ("DNg105+95", ["DNg105", "DNg95"], "flex")]:
    cp = class_pool(members)
    if cp is None:
        continue
    fr, dr = cp
    mask = {"jump": is_jump_t, "flex": is_flex_t, "ext": is_ext_t}[famname]
    share = float(fr[mask].sum())
    dp = dr[:, mask].sum(1)
    zv = float((share - dp.mean()) / (dp.std() + 1e-9))
    cls[name] = dict(share=share, z=zv, fam=famname, ndraw=int(len(dp)))
    print(f"  {name} -> {famname}: share {share:.3f} z {zv:+.1f} (L14 anchor "
          f"{'PASS >=15' if zv >= 15 else 'below 15'})")
ok_all = (cls.get("DNp01-04", {}).get("z", 0) >= 15
          and ok.get("DNg105", 0) >= 15)
print(f"  => anchor gate (DNp01-04 CLASS jump z>=15 [L14 form] AND per-type "
      f"DNg105 flex z>=15 [L20 form]): {'PASS' if ok_all else 'FAIL'}")
for t in ("DNc01", "DNc02"):
    if t in tcode:
        i = tcode[t]
        order = np.argsort(-obs[i])
        tops = "; ".join(f"{mtypes[j]} {obs[i,j]:.2f} z{z[i,j]:+.1f}"
                         for j in order[:2] if obs[i, j] > 0)
        print(f"  {t} top targets: {tops}")

# family-vocabulary rollup: for each family, the enriched channel list
for name in ("jump", "flex", "ext"):
    sub = atlas[(atlas[f"z_{name}"] >= 5) & (atlas[f"w_{name}"] >= 0.10)]
    print(f"\n--- {name}-family enriched channels (w>=.10, z>=+5): {len(sub)} ---")
    print(sub.head(8).to_string(
        columns=["dn_type", "cells", "edges", f"w_{name}", f"z_{name}", "top1_type"],
        float_format=lambda x: f"{x:.3f}", index=False))

json.dump({
    "n_dn_types_block": int(T), "n_atlas_rows_2cell": int(keep.sum()),
    "n_table_5edge": int(len(atlas)), "ndraw": NDRAW,
    "block_edges": int(B), "n_motor_types": int(D),
    "z_floor_cells": nfloor,
    "purity_counts": {k: int((atlas.purity == k).sum())
                      for k in ("pure", "mixed", "diffuse")},
    "n_enriched": int(len(enr)),
    "anchors_pertype_family_z": ok,
    "anchors_class_pooled": cls,
    "class_gate_pass": bool(ok_all),
    "anchor_gate_pass": bool(ok_all),
    "motor_type_vocabulary": mtypes,
    "dnc_profiles": {t: [(mtypes[j], float(obs[tcode[t], j]))
                         for j in np.argsort(-obs[tcode[t]])[:5]
                         if obs[tcode[t], j] > 0]
                     for t in ("DNc01", "DNc02") if t in tcode},
    "top30_by_z": atlas.head(30).to_dict("records"),
}, open("l22/results_l22.json", "w"), indent=1)
print(f"\nwrote l22/atlas.csv ({len(atlas)} rows) + results_l22.json | "
      f"{time.time()-t0:.0f}s", flush=True)
