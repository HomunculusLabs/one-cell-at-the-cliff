"""Probe: does DNge059-L really have u_max +4.5 (my census) while L37 found
it drive-dead? Per-cell u_max + a direct paired drive test. Throwaway."""
import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX, BG, NOISE = 0.05, 0.01, 1.0, 0.02, 0.01
G, BETA = 0.01, 2.0

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side_raw = lab["somaSide"].to_numpy()
side_all = np.array([s if isinstance(s, str) else "?" for s in side_raw])
bid = lab["bodyId"].to_numpy(np.uint64)

nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather",
                     columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64).astype(str), nt["consensus_nt"]))
nt_names = np.array([str(nt_map.get(str(int(b)), "unknown")).lower() for b in ids])
w = pd.read_feather(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(idx) & w["body_post"].isin(idx)]
gsrc = w["body_pre"].map(idx).to_numpy(np.int64)
gdst = w["body_post"].map(idx).to_numpy(np.int64)
gw = w["weight"].to_numpy(np.float32)
cord = np.isin(sup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
dn_all = sup == "descending_neuron"
dn_into = np.zeros(len(ids), bool)
dn_into[gdst[cord[gsrc]]] = True
dn_into &= dn_all
keep = cord | dn_into
emask = keep[gsrc] & keep[gdst]
gsrc, gdst, gw = gsrc[emask], gdst[emask], gw[emask]
loc = -np.ones(len(ids), np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
lsup, ltyp, lnt = sup[keep], typ[keep], nt_names[keep]
lside, lbid = side_all[keep], bid[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy((gw * signA[lsrc]).astype(np.float32)), (n, n)
).coalesce().to_sparse_csr()
neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
Z = torch.zeros(n, 1)

cells = {}
for t in ("DNge059", "DNge046"):
    for sd in ("L", "R"):
        cells[f"{t}_{sd}"] = np.where((ltyp == t) & (lside == sd))[0]
allc = np.unique(np.concatenate(list(cells.values())))
print("cell map:", {k: (v.tolist(), lbid[v].tolist()) for k, v in cells.items()})

# per-cell u_max on free run, seeds 11/22/33 (census form, 600-step window)
umax = {int(c): -1e9 for c in allc}
umean = {int(c): 0.0 for c in allc}
cnt = {int(c): 0 for c in allc}
for seed in (11, 22, 33):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    for _ in range(400):
        d = torch.sparse.mm(Wb, X) * G
        tt = torch.relu(d + BG)
        tt = (tt + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (tt - X)
    for _ in range(600):
        d = torch.sparse.mm(Wb, X) * G
        tt = torch.relu(d + BG)
        tt = (tt + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (tt - X)
        u = (torch.sparse.mm(Wb, X) * G + BG)[allc, 0].numpy()
        for j, c in enumerate(allc):
            umax[int(c)] = max(umax[int(c)], float(u[j]))
            umean[int(c)] += float(u[j])
            cnt[int(c)] += 1
for c in allc:
    print(f"cell {int(lbid[c])} side {lside[c]} type {ltyp[c]}: "
          f"u_max {umax[int(c)]:+.3f} u_mean {umean[int(c)]/cnt[int(c)]:+.3f}")

# direct paired drive test: DNge059_L @0.8 and DNge046_R @0.8, 1200 steps
def pair_test(tag, cc, amp, seed, steps=1200):
    gen = torch.Generator().manual_seed(seed)
    Xc = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    Xa = Xc.clone()
    I = torch.zeros(n, 1)
    I[cc] = amp

    def step2(a, b, on):
        dc = torch.sparse.mm(Wb, a) * G
        da = torch.sparse.mm(Wb, b) * G + (I if on else 0.0)
        nz = NOISE * torch.randn(n, 1, generator=gen)
        tc = (torch.relu(dc + BG) + nz).clamp(max=RMAX)
        ta = (torch.relu(da + BG) + nz).clamp(max=RMAX)
        return (a + (DT / TAU) * (tc - a), b + (DT / TAU) * (ta - b))

    for _ in range(400):
        Xc, Xa = step2(Xc, Xa, False)
    dm = 0.0
    for _ in range(steps):
        Xc, Xa = step2(Xc, Xa, True)
        dm = max(dm, float((Xa - Xc).abs().max()))
    print(f"drive {tag} amp {amp} seed {seed}: dm {dm:.4f}")

for tag in ("DNge059_L", "DNge046_R", "DNge059_R", "DNge046_L"):
    for seed in (11, 22):
        pair_test(tag, cells[tag], 0.8, seed)
