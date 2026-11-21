"""Isolate the l52-vs-l49 first-divergence: settle + 6 window steps, seed 11,
f07a3 arm only, comparing my per-arm phase accumulator vs l49's precomputed
PHI, and the resulting mech-cell X + mm against l49's stored raw."""
import math

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 6
G, BETA, D = 0.01, 2.0, 0.05
SEED = 11

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
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
lsup, ltyp, lside, lcls = sup[keep], typ[keep], side[keep], cls[keep]
assert n == 21516 and len(gsrc) == 2977920
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in nt_names[keep]], np.float32)
Wa_vals = gw * signA[loc[gsrc]]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()
motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
dng100 = np.where(ltyp == "DNg100")[0]
mech = np.where((lsup == "vnc_sensory")
                & pd.Series(lcls).str.contains("mechano").to_numpy())[0]
print("mech", len(mech), "dng100", len(dng100), "motor", int(motor.sum()))

gen = torch.Generator().manual_seed(SEED)
X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
X = X0.clone()
neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
I = torch.zeros(n, 1)
I[dng100] = D

# l49 phase: precomputed PHI
ph = 0.0
for _ in range(SETTLE):
    ph += 2 * math.pi * 0.7 * DT
PHI = np.empty(18000, np.float64)
php = ph
for i in range(18000):
    php += 2 * math.pi * 0.7 * DT
    PHI[i] = php


def step(k, use_phi):
    global X
    nz = NOISE * torch.randn(n, 1, generator=gen)
    if use_phi:
        ph_k = math.sin(PHI[k])
    else:
        ph_k = math.sin(PH_MINE[k])
    drive = torch.sparse.mm(Wb, X) * G + I
    if k >= 0:
        drive[mech, 0] = drive[mech, 0] + 0.3 * (0.5 + 0.5 * ph_k)
    t = torch.relu(drive + BG)
    t = (t + nz).clamp(max=RMAX)
    X = X + (DT / TAU) * (t - X)


# my per-arm accumulator
ph_mine = 0.0
for _ in range(SETTLE):
    ph_mine += 2 * math.pi * 0.7 * DT
PH_MINE = np.empty(18000, np.float64)
phm = ph_mine
for i in range(18000):
    phm += 2 * math.pi * 0.7 * DT
    PH_MINE[i] = phm
print("PHI vs mine max diff:", float(np.abs(PHI - PH_MINE).max()))
print("sin PHI[0:3]", [round(math.sin(PHI[i]), 12) for i in range(3)])

for k in range(SETTLE):
    step(-1 - k, True)
for i in range(WIN):
    step(i, True)
    mm = float(X[motor].mean())
    print(f"step {i}: mm={mm:.6f}")

z49 = np.load("l49/raw_l49.npz")
print("l49 stored mm[0:6]:", z49[f"mm_cont_{SEED}"][:6].round(6))
