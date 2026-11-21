"""L36 probe: WHY does the DNg100@0.8 paired arm diverge? It must not.
Checks: (a) post-init |dX|, (b) per-step |dX| through settle, (c) window,
for amp 0.8 vs amp 0.0 on DNg100, seed 11. Localizes the asymmetry."""
import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
G, BETA = 0.01, 2.0

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
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
g100 = np.where(ltyp == "DNg100")[0]
print("g100 cells:", g100, "n =", n)

for amp in (0.8, 0.0):
    gen = torch.Generator().manual_seed(11)
    Xc = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    Xa = Xc.clone()
    I = torch.zeros(n, 1)
    I[g100] = amp

    def step2(cc, ca):
        dc = torch.sparse.mm(Wb, cc) * G
        da = torch.sparse.mm(Wb, ca) * G + I
        nz = NOISE * torch.randn(n, 1, generator=gen)
        tc = (torch.relu(dc + BG) + nz).clamp(max=RMAX)
        ta = (torch.relu(da + BG) + nz).clamp(max=RMAX)
        return cc + (DT / TAU) * (tc - cc), ca + (DT / TAU) * (ta - ca)

    print(f"--- amp {amp}: post-init max|dX| {float((Xa-Xc).abs().max()):.3e}")
    first = -1
    for k in range(SETTLE):
        Xc, Xa = step2(Xc, Xa)
        d = float((Xa - Xc).abs().max())
        if d > 0 and first < 0:
            first = k
            u_d = float((torch.sparse.mm(Wb, Xa)[g100] * G).max())
            print(f"  first diff at settle step {k}: |dX| {d:.3e} "
                  f"(g100 drive max {u_d:+.3f})")
    print(f"  post-settle max|dX| {float((Xa-Xc).abs().max()):.3e} (first {first})")
    for k in range(5):
        Xc, Xa = step2(Xc, Xa)
        print(f"  window step {k}: max|dX| {float((Xa-Xc).abs().max()):.3e}")
