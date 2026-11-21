"""L20 stage 1: STATIC scan — which DN classes target Ti/Tr FLEXOR MNs?

L19 found the looming->DNp01-04 route is a monophasic extensor/jump power
stroke (flexor SNR 1.5-1.7x = undriven). The crouch of a real escape jump
must come from somewhere. Scan ALL DN types for flexor-target enrichment:

  For each DN type with edges into motor:
    f_flex(type) = w(type -> flexor MNs) / w(type -> motor)
  Null: 100 Maslov-Sneppen destination-swap draws of the DN->motor block
  (l14_null.rewire_block verbatim: in/out degrees kept, weights travel with
  the source DN). z = (f_obs - mean_null) / std_null per type.

Also reports extensor + jump-family fractions and, for the top flexor hits,
the top upstream classes (is there a sensory route into the crouch class?).

Pools verbatim from l19_chain.py (Ti/Tr flex+Acc flex vs ext, TTMn jump).
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
t0 = time.time()
os.makedirs("l20", exist_ok=True)
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].fillna("").astype(str).to_numpy()
typ = lab["type"].fillna("").astype(str).to_numpy()
cls = lab["class"].fillna("").astype(str).to_numpy()

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
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
JUMP = np.where(np.array([str(t).startswith(("TTMn", "DLMn", "DVMn"))
                          for t in typm]))[0]
for k, (f, e) in PAIRS.items():
    assert len(f) > 0 and len(e) > 0
assert len(TTM) > 0 and len(JUMP) > 0

rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
mrow = np.zeros(N, bool); mrow[motor] = True
sdn = np.zeros(N, bool); sdn[dn] = True
blk = mrow[rows] & sdn[cols]
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
B = len(b_dst)
print(f"motor {M} | flex pool {len(POOL_F)} | ext {len(POOL_E)} | "
      f"jump {len(JUMP)} | DN->motor block {B:,} edges | {time.time()-t0:.0f}s",
      flush=True)

is_flex = np.zeros(M, bool); is_flex[POOL_F] = True
is_ext = np.zeros(M, bool); is_ext[POOL_E] = True
is_jump = np.zeros(M, bool); is_jump[JUMP] = True
mpos = np.full(N, -1, np.int64); mpos[motor] = np.arange(M)

# per-type observed fractions (weight-carried)
types = sorted(set(typ[b_src]))
tcode = {t: i for i, t in enumerate(types)}
src_c = np.array([tcode[t] for t in typ[b_src]])
tw = np.bincount(src_c, weights=b_w, minlength=len(types))


def fracs(dst):
    d = mpos[dst]
    out = {}
    for name, mask in [("flex", is_flex), ("ext", is_ext), ("jump", is_jump)]:
        num = np.bincount(src_c, weights=b_w * mask[d], minlength=len(types))
        out[name] = num / (tw + 1e-12)
    return out


obs = fracs(b_dst)


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


rng = np.random.default_rng(20261111 + 20)
NDRAW = 100
acc = {k: np.zeros((NDRAW, len(types)), np.float32) for k in obs}
for d in range(NDRAW):
    fd = fracs(rewire_block(rng))
    for k in acc:
        acc[k][d] = fd[k]
    if d % 20 == 19:
        print(f"  null draw {d+1}/{NDRAW} | {time.time()-t0:.0f}s", flush=True)

mu = {k: acc[k].mean(0) for k in acc}
sd = {k: acc[k].std(0) + 1e-9 for k in acc}
ncells = np.array([(dn_typ == t).sum() for t in types])
nedge = np.bincount(src_c, minlength=len(types))

# flexor enrichment table
z_flex = (obs["flex"] - mu["flex"]) / sd["flex"]
order = np.argsort(-z_flex)
print(f"\n=== flexor-target enrichment, top 15 by z (types with >=5 edges) ===")
print(f"{'DN type':>10s} {'cells':>5s} {'edges':>5s} {'w_flex%':>8s} "
      f"{'null%':>7s} {'z':>7s} {'ext%':>6s} {'jump%':>6s}")
tab = []
for i in order:
    if nedge[i] < 5:
        continue
    tab.append(dict(type=types[i], cells=int(ncells[i]), edges=int(nedge[i]),
                    w_flex=float(obs["flex"][i]), null_flex=float(mu["flex"][i]),
                    z_flex=float(z_flex[i]), w_ext=float(obs["ext"][i]),
                    w_jump=float(obs["jump"][i])))
    if len(tab) <= 15:
        print(f"{types[i]:>10s} {ncells[i]:5d} {nedge[i]:5d} "
              f"{100*obs['flex'][i]:7.2f}% {100*mu['flex'][i]:6.2f}% "
              f"{z_flex[i]:+7.1f} {100*obs['ext'][i]:5.1f}% "
              f"{100*obs['jump'][i]:5.1f}%")
print(f"(block-level flexor weight share observed "
      f"{100*(is_flex[mpos[b_dst]]*b_w).sum()/b_w.sum():.2f}% | null "
      f"{100*np.mean([ (acc['flex'][d]*tw).sum()/tw.sum() for d in range(NDRAW)]):.2f}%)")

# DNp01-04 reference + biggest raw flexor mass
print("\nDNp01-04 reference (the power-stroke class):")
for t in ["DNp01", "DNp02", "DNp03", "DNp04"]:
    if t in tcode:
        i = tcode[t]
        print(f"  {t}: w_flex {100*obs['flex'][i]:.2f}% z {z_flex[i]:+.1f} "
              f"| w_ext {100*obs['ext'][i]:.1f}% w_jump {100*obs['jump'][i]:.1f}%")
flex_mass = (obs["flex"] * tw)
order2 = np.argsort(-flex_mass)
print("\ntop 10 DN types by RAW flexor weight mass:")
for i in order2[:10]:
    print(f"  {types[i]:>10s} flex mass {flex_mass[i]:8.1f} "
          f"({100*obs['flex'][i]:5.1f}% of its motor out, z {z_flex[i]:+6.1f}) "
          f"cells {ncells[i]}")

# upstream route for the top-3 enriched flexor types (edges INTO those DNs)
top3 = [types[i] for i in order[:3] if nedge[i] >= 5][:3]
up = {}
for t in top3:
    cells = dn[dn_typ == t]
    inm = np.isin(cols, cells)
    src_cls = pd.Series(cls[rows[inm]]).value_counts().head(5)
    src_sup = pd.Series(sup[rows[inm]]).value_counts().head(5)
    up[t] = {"n_cells": int(len(cells)),
             "in_edges": int(inm.sum()),
             "top_src_classes": {str(k): int(v) for k, v in src_cls.items()},
             "top_src_superclass": {str(k): int(v) for k, v in src_sup.items()}}
    print(f"\nupstream of {t} ({len(cells)} cells, {inm.sum():,} in-edges):")
    print("  classes:", dict(src_cls))
    print("  superclass:", dict(src_sup))

json.dump({
    "block_edges": int(B), "ndraw": NDRAW,
    "pools": {"flex": int(len(POOL_F)), "ext": int(len(POOL_E)),
              "jump": int(len(JUMP))},
    "flex_table_top30": tab[:30],
    "block_flex_share_obs": float((is_flex[mpos[b_dst]] * b_w).sum() / b_w.sum()),
    "upstream": up,
}, open("l20/scan_results.json", "w"), indent=1)
print(f"\nwrote l20/scan_results.json | {time.time()-t0:.0f}s", flush=True)
