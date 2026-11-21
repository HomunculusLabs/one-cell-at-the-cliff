"""Probe: why does my L34 free-run seed 11 give f=0.80 when l33's json says 1.33?
Rerun the L33 base arm verbatim (stage A + run copied) and compare the mm
trace bit-for-bit against l33/mm_traces.npz base_0. Also check v1 vs v2 jsons.
"""
import json

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
WIN = 6000
SEEDS = [11, 22, 33]
G, BETA, D = 0.01, 2.0, 0.05

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()

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
lsup, ltyp, lside = sup[keep], typ[keep], side[keep]
lnt = nt_names[keep]

SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wa_vals = gw * signA[lsrc]
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wa_vals.astype(np.float32)), (n, n)).coalesce().to_sparse_csr()

motor = np.isin(lsup, ["vnc_motor", "cb_motor"])
dng100 = np.where(ltyp == "DNg100")[0]
assert len(dng100) == 2


def run(seed):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    neg = Wc.values() < 0
    vals = Wc.values().clone()
    vals[neg] *= BETA
    Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
    I = torch.zeros(n, 1)
    I[dng100] = D

    def step(cur):
        drive = torch.sparse.mm(Wb, cur) * G + I
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        X = step(X)
    T = WIN
    mm = np.zeros(T, np.float32)
    for i in range(T):
        X = step(X)
        mm[i] = X[motor].mean()
    return mm


z = np.load("l33/mm_traces.npz")
r1 = json.load(open("l33/results_l33_v1.json"))
r2 = json.load(open("l33/results_l33.json"))
print("v1 vs v2 base seed11 rhythm:", r1["base"]["seeds"][0]["rhythm"], r2["base"]["seeds"][0]["rhythm"])
for i, s in enumerate(SEEDS):
    mm = run(s)
    ref = z[f"base_{i}"]
    a, b = mm[1500:], ref
    print(f"seed {s}: max|diff| {np.max(np.abs(a - b)):.3e} corr {np.corrcoef(a, b)[0,1]:.6f} "
          f"first-div {int(np.argmax(np.abs(a-b) > 1e-6)) if np.max(np.abs(a-b)) > 1e-6 else -1}")
    x = a - a.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    fr = np.fft.rfftfreq(len(x), DT)
    band = (fr >= 0.5) & (fr <= 10)
    j = int(np.argmax(ps[band]))
    print(f"  my rerun dominant f {fr[band][j]:.3f} ratio {ps[band][j]/max(np.median(ps[band]),1e-30):.0f}")
    x = b - b.mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    j = int(np.argmax(ps[band]))
    print(f"  npz  base_{i} dominant f {fr[band][j]:.3f} ratio {ps[band][j]/max(np.median(ps[band]),1e-30):.0f}")
