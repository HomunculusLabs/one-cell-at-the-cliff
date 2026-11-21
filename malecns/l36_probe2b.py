"""L36 probe 2: localize the divergence. Identical X, I with 0.8 on the two
DNg100 cells; diff mm outputs, drives, and t row-wise. Which rows differ?"""
import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
BG, NOISE = 0.02, 0.01
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
lsrc, ldst, loc_ = loc[gsrc], loc[gdst], loc
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

gen = torch.Generator().manual_seed(11)
X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
I = torch.zeros(n, 1)
I[g100] = 0.8
nz = NOISE * torch.randn(n, 1, generator=gen)

m1 = torch.sparse.mm(Wb, X)
m2 = torch.sparse.mm(Wb, X.clone())
print("mm deterministic:", bool((m1 == m2).all()))
dc = m1 * G
da = m2 * G + I
db = (dc != da)
rows = db[:, 0].nonzero().flatten().numpy()
print(f"drive-diff rows: {len(rows)} | g100 rows {g100}")
extra = np.setdiff1d(rows, g100)
print(f"non-g100 diff rows: {len(extra)}")
if len(extra):
    vdc = dc[extra, 0].numpy()
    vda = da[extra, 0].numpy()
    nz_ = np.signbit(vdc.astype(np.float64)) & (vdc == 0)
    print("  sample dc:", [f"{v:.1e}" for v in vdc[:5]],
          "| signbit-zero:", int(nz_.sum()))
tc = (torch.relu(dc + BG) + nz).clamp(max=1.0)
ta = (torch.relu(da + BG) + nz).clamp(max=1.0)
tr = (tc != ta)[:, 0].nonzero().flatten().numpy()
print(f"t-diff rows: {len(tr)} (first 10: {tr[:10]})")
if len(tr):
    print("  t diffs:", [f"{float(tc[i])-float(ta[i]):+.3e}" for i in tr[:10]])
    print("  their dc:", [f"{float(dc[i]):+.3e}" for i in tr[:10]])
    print("  their type:", [ltyp[i] for i in tr[:10]])
