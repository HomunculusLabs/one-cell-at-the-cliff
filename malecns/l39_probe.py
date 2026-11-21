"""L39 probe: name the DNg110 dead-channel mechanism — census viability was
measured in the INTRINSIC regime; under A=.3 mech entrainment the arm came
back bit-identical (dm=0). Measure u (pre-noise drive) and X of the hop
cells inside the ENTRAINED regime: pinned (u_mean>>0, X>=.95) vs buried
(u_max<0). Two-sided census rule (L36/L38) applied regime-conditional."""
import json
import math
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN, SEG = 400, 6000, 2000
G, BETA, D = 0.01, 2.0, 0.05
ENT_AMP = 0.3
TARGETS = [0.7, 1.4, 0.7]
t0 = time.time()

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5-minconf-0.5.feather") \
    if False else pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
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
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
lnt = nt_names[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy((gw * signA[lsrc]).astype(np.float32)),
    (n, n)).coalesce().to_sparse_csr()
motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
dng100 = np.where(ltyp == "DNg100")[0]
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
hop046 = np.where((ltyp == "DNge046") & (lside == "L"))[0]
hop110 = np.where(ltyp == "DNg110")[0]
probe_cells = {"h046_L": hop046, "h110": hop110}

gen = torch.Generator().manual_seed(11)
X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
I = torch.zeros(n, 1)
I[dng100] = D
ph = 0.0
ustat = {k: [] for k in probe_cells}
xstat = {k: [] for k in probe_cells}

def step(k):
    global X, ph
    seg = min(k // SEG, 2)
    fd = TARGETS[seg] if k >= 0 else TARGETS[0]
    ph += 2 * math.pi * fd * DT
    drive = torch.sparse.mm(Wb, X) * G + I
    if k >= 0:
        drive[mech, 0] = drive[mech, 0] + ENT_AMP * (0.5 + 0.5 * math.sin(ph))
    for k2, cells in probe_cells.items():
        ustat[k2].append(drive[cells, 0].detach().numpy().copy())
        xstat[k2].append(X[cells, 0].detach().numpy().copy())
    t = torch.relu(drive + BG)
    t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
    X = X + (DT / TAU) * (t - X)

for k in range(SETTLE):
    step(-1 - k)
for k in range(WIN):
    step(k)

out = {}
for k2 in probe_cells:
    U = np.stack(ustat[k2][SETTLE:])      # window-only
    Xs = np.stack(xstat[k2][SETTLE:])
    out[k2] = dict(cells=int(len(probe_cells[k2])),
                   u_max=float(U.max()), u_mean=float(U.mean()),
                   u_min=float(U.min()),
                   mean_X=float(Xs.mean()), frac_X_ge95=float((Xs >= .95).mean()),
                   frac_u_pos=float((U > 0).mean()),
                   verdict=("PINNED" if U.mean() > 1 and Xs.mean() >= .95
                            else "BURIED" if U.max() < 0 else "VIABLE"))
    print(k2, json.dumps(out[k2]))
json.dump(dict(regime="ent A=.3 targets 0.7/1.4/0.7", cells=out,
               meta=dict(g=G, beta=BETA, ent_amp=ENT_AMP, seed=11)),
          open("l39/probe_h110.json", "w"), indent=1)
print(f"done {time.time()-t0:.0f}s")
