"""L14: null-duck the L13 per-class DN->motor gait channel.

L13b: amplifying ONLY DNp01-04->motor (118 edges) + DNc01/02->motor (60) x200
gave a reproducible looming motor vector (self-cos .971), odor-orthogonal
(cross -.002), clamps kill it, tonic ~base; looming loaded on TTMn jump MNs /
DLMn, at x2000 on Ti extensor + i1 leg MNs.

Question: is that the REAL target PLACEMENT (wiring) or just gain + source
class identity (bulk)?  Focused null: Maslov-Sneppen rewiring of the DN->motor
block ONLY (~23.6k edges) — destination swaps between block edges keep every
DN's out-degree/out-strength (weights travel with the SOURCE DN) and every
motor cell's in-degree; the other 25.5M edges (interior, sensory->DN routing)
are FROZEN — isolates the L13 claim.  Same per-class amplification rule is
re-applied on each rewired graph (wherever the class edges now land).

Arms:
  A. static enrichment (100 draws, block arrays only): fraction of DNp01-04
     block weight landing on the real top-5 target TYPES, z vs null draws;
     same for DNc01/02.
  B. dynamic (5 draws): full L13b protocol at g=200 — looming/odor x3 seeds,
     clampLeg; self/cross cos, clamp-kill ratio, anatomy overlap vs the real
     loading profile (cos + |dm| mass on the real top-6 cells), motor tonic,
     global activity (operating-point stability check).
"""
import json
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, EVENT = 300, 20
GAIN = 0.8846
G = 200
SEEDS = [11, 22, 33]
NDRAW, NSTA = 5, 100

t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].to_numpy()
typ = lab["type"].astype(str).to_numpy()
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
olf = np.where(lab["class"].astype(str) == "olfactory")[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4

rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
vals = W.values().numpy().astype(np.float32)
mrow = np.zeros(N, bool); mrow[motor] = True
sdn = np.zeros(N, bool); sdn[dn] = True
blk = mrow[rows] & sdn[cols]
b_dst, b_src, b_w = rows[blk].copy(), cols[blk].copy(), vals[blk].copy()
nb_dst, nb_src, nb_val = rows[~blk], cols[~blk], vals[~blk]
print(f"block edges {blk.sum():,} | non-block {len(nb_dst):,} | "
      f"{time.time()-t0:.0f}s", flush=True)


def rewire_block(rng, factor=10):
    """MS destination swaps; weights stay with sources; reject duplicates."""
    dst, src, w = b_dst.copy(), b_src.copy(), b_w.copy()
    M = len(dst)
    pairs = set((dst.astype(np.int64) * N + src).tolist())
    att = factor * M
    ii = rng.integers(0, M, att)
    jj = rng.integers(0, M, att)
    done = 0
    for k in range(att):
        i, j = ii[k], jj[k]
        if i == j:
            continue
        a = dst[i] * N + src[j]   # new edge j -> (dst_i, src_j)
        b = dst[j] * N + src[i]   # new edge i -> (dst_j, src_i)
        if a in pairs or b in pairs:
            continue
        pairs.discard(dst[i] * N + src[i])
        pairs.discard(dst[j] * N + src[j])
        pairs.add(a); pairs.add(b)
        dst[i], dst[j] = dst[j], dst[i]
        done += 1
    assert len(pairs) == M
    return dst, src, w, done


def build_W(dst, src, w):
    idx = np.vstack([np.concatenate([nb_dst, dst]),
                     np.concatenate([nb_src, src])])
    vv = np.concatenate([nb_val, w])
    t = torch.sparse_coo_tensor(torch.from_numpy(idx).long(),
                                torch.from_numpy(vv), (N, N))
    return t.coalesce().to_sparse_csr()


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


def make_pc(Wc, g):
    W2 = Wc.clone()
    r2 = np.repeat(np.arange(N), np.diff(W2.crow_indices().numpy()))
    c2 = W2.col_indices().numpy()
    ml = torch.from_numpy(mrow[r2] & legmask[c2])
    mn = torch.from_numpy(mrow[r2] & neckmask[c2])
    v = W2.values()
    v[ml] = v[ml] * g
    v[mn] = v[mn] * g
    return W2, int(ml.sum()), int(mn.sum())


legmask = np.zeros(N, bool); legmask[leg_dns] = True
neckmask = np.zeros(N, bool); neckmask[neck_dns] = True


def run(W_, channel, amp, seed, clamp=None):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[channel] = amp
    for _ in range(SETTLE):
        step(Z)
    Xb = X.clone()
    peak_m = -1.0
    Xpk = None
    for k in range(EVENT + 10):
        step(I0 if k < EVENT else Z)
        m = X[motor].mean().item()
        if m > peak_m:
            peak_m = m
            Xpk = X.clone()
    dm = (Xpk[motor].squeeze(1) - Xb[motor].squeeze(1)).numpy()
    return dm, peak_m, float(Xb.mean())


# ---------- arm A: static enrichment (100 draws, block only) ----------
rng_s = np.random.default_rng(101)
leg_e = np.isin(b_src, leg_dns)
neck_e = np.isin(b_src, neck_dns)


def wfrac_on_types(dst, src, w, emask, type_set):
    e = emask & np.isin(typ[dst], type_set)
    return float(w[e].sum() / w[emask].sum())


def top_types(dst, src, w, emask, k=5):
    e = np.where(emask)[0]
    df = pd.DataFrame({"t": typ[dst[e]], "w": w[e]}).groupby("t")["w"].sum()
    return list(df.sort_values(ascending=False).index[:k])


leg_types = top_types(b_dst, b_src, b_w, leg_e)
neck_types = top_types(b_dst, b_src, b_w, neck_e)
print("real DNp01-04 top target types:", leg_types, flush=True)
print("real DNc01/02 top target types:", neck_types, flush=True)
p_leg_real = wfrac_on_types(b_dst, b_src, b_w, leg_e, leg_types)
p_nk_real = wfrac_on_types(b_dst, b_src, b_w, neck_e, neck_types)
leg_null, nk_null = [], []
for s in range(NSTA):
    d2, s2, w2, _ = rewire_block(np.random.default_rng(1000 + s), factor=5)
    leg_null.append(wfrac_on_types(d2, s2, w2, leg_e, leg_types))
    nk_null.append(wfrac_on_types(d2, s2, w2, neck_e, neck_types))
leg_null, nk_null = np.array(leg_null), np.array(nk_null)
z_leg = (p_leg_real - leg_null.mean()) / (leg_null.std() + 1e-12)
z_nk = (p_nk_real - nk_null.mean()) / (nk_null.std() + 1e-12)
res = {
    "armA_static": {
        "leg_types": leg_types, "neck_types": neck_types,
        "p_leg_real": p_leg_real, "p_leg_null_mean": float(leg_null.mean()),
        "p_leg_null_sd": float(leg_null.std()), "z_leg": float(z_leg),
        "p_neck_real": p_nk_real, "p_neck_null_mean": float(nk_null.mean()),
        "p_neck_null_sd": float(nk_null.std()), "z_neck": float(z_nk),
    }, "armB_dynamic": {},
}
json.dump(res, open("l14/results_l14.json", "w"), indent=1)
print(f"A: leg p {p_leg_real:.3f} vs null {leg_null.mean():.3f}+-{leg_null.std():.3f}"
      f" z={z_leg:+.1f} | neck {p_nk_real:.3f} vs {nk_null.mean():.3f}"
      f"+-{nk_null.std():.3f} z={z_nk:+.1f} | {time.time()-t0:.0f}s", flush=True)

# ---------- arm B: dynamic nulls ----------
Wg_real, nl_r, nn_r = make_pc(W.clone(), G)
print(f"real amplified edges leg {nl_r} neck {nn_r} (L13b: 118/60)", flush=True)
Vr = {}
for key, ch, amp, clamp in [("looming", loom, 8.0, None),
                            ("odor", olf, 8.0, None)]:
    Vr[key] = [run(Wg_real, ch, amp, s, clamp=clamp) for s in SEEDS]
real_loom = np.mean([v[0] for v in Vr["looming"]], axis=0)
real_top6 = np.argsort(-real_loom)[:6]
self_r = np.mean([cos(Vr["looming"][i][0], Vr["looming"][j][0])
                  for i in range(3) for j in range(i + 1, 3)])
cross_r = np.mean([cos(Vr["looming"][i][0], Vr["odor"][j][0])
                   for i in range(3) for j in range(3)])
res["armB_real_ref"] = {
    "self_loom": float(self_r), "cross_loom_odor": float(cross_r),
    "mbase": float(np.mean([v[2] for v in Vr["looming"]])),
    "top6_types": [str(typ[motor][i]) for i in real_top6],
    "top6_frac": float(np.abs(real_loom)[real_top6].sum() / np.abs(real_loom).sum()),
}
print(f"real ref: self {self_r:+.3f} cross {cross_r:+.3f} top6 "
      f"{res['armB_real_ref']['top6_types']}", flush=True)
json.dump(res, open("l14/results_l14.json", "w"), indent=1)

chance6 = float(np.abs(real_loom)[real_top6].sum() * 0 + 6.0 / len(motor))
for d in range(NDRAW):
    dst, src, w, done = rewire_block(np.random.default_rng(2000 + d))
    Wn = build_W(dst, src, w)
    Wg, nl, nn = make_pc(Wn, G)
    assert nl == 118 and nn == 60, f"edge counts moved {nl}/{nn}"
    V = {}
    for key, ch, amp, clamp in [("looming", loom, 8.0, None),
                                ("odor", olf, 8.0, None),
                                ("clampLeg", loom, 8.0, leg_dns)]:
        V[key] = [run(Wg, ch, amp, s, clamp=clamp) for s in SEEDS[:2]]
    loom_mean = np.mean([v[0] for v in V["looming"]], axis=0)
    row = {
        "swaps_done": done,
        "self_loom": float(np.mean([cos(V["looming"][0][0], V["looming"][1][0])])),
        "self_odor": float(cos(V["odor"][0][0], V["odor"][1][0])),
        "cross": float(np.mean([cos(V["looming"][i][0], V["odor"][j][0])
                                for i in range(2) for j in range(2)])),
        "clamp_kill_ratio": float(np.abs(V["clampLeg"][0][0]).mean()
                                  / np.abs(V["looming"][0][0]).mean()),
        "anat_cos_real": cos(loom_mean, real_loom),
        "anat_top6_frac": float(np.abs(loom_mean)[real_top6].sum()
                                / np.abs(loom_mean).sum()),
        "mbase": float(np.mean([v[2] for v in V["looming"]])),
        "dpeak": float(np.mean([v[1] for v in V["looming"]])),
        "top_types": [str(t) for t in typ[motor][np.argsort(-loom_mean)[:5]]],
    }
    res["armB_dynamic"][f"draw{d}"] = row
    json.dump(res, open("l14/results_l14.json", "w"), indent=1)
    print(f"draw{d}: self {row['self_loom']:+.3f} cross {row['cross']:+.3f} "
          f"clamp {row['clamp_kill_ratio']:.3f} anat_cos {row['anat_cos_real']:+.3f} "
          f"top6frac {row['anat_top6_frac']:.3f} mbase {row['mbase']:.4f} "
          f"top {row['top_types'][:3]} | {time.time()-t0:.0f}s", flush=True)

D = res["armB_dynamic"]
agg = {k: [D[f"draw{d}"][k] for d in range(NDRAW)]
       for k in ["self_loom", "cross", "clamp_kill_ratio",
                 "anat_cos_real", "anat_top6_frac", "mbase"]}
res["armB_summary"] = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v))}
                       for k, v in agg.items()}
res["armB_summary"]["chance_top6frac"] = chance6
res["armB_summary"]["real_top6frac"] = res["armB_real_ref"]["top6_frac"]
json.dump(res, open("l14/results_l14.json", "w"), indent=1)
print(f"\nSUMMARY null mean+-sd: self {np.mean(agg['self_loom']):.3f} "
      f"cross {np.mean(agg['cross']):+.3f} clamp {np.mean(agg['clamp_kill_ratio']):.3f} "
      f"anat_cos {np.mean(agg['anat_cos_real']):+.3f} "
      f"top6frac {np.mean(agg['anat_top6_frac']):.3f} "
      f"(real {res['armB_real_ref']['top6_frac']:.3f}, chance {chance6:.4f})",
      flush=True)
print(f"done {time.time()-t0:.0f}s -> l14/results_l14.json", flush=True)
