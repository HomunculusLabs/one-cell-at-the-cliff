"""L35 probe 3 (tick 52): is the L32 'sustained DNg100 drive' load-bearing?

probe_mech.json shows DNg100 cells sit ~16 units below the relu floor
(u ~ [-17.5,-15.9], X ~ 0.006) under the frozen regime (g .01 / beta 2).
If so, the tonic drive D=0.05 on them is ABSORBED by the same floor and the
self-rhythm must be cord-intrinsic, not DN-driven. Decisive test: control
rollouts with D=0.0 — if relu() floor absorbs the tonic, the trajectory is
BIT-IDENTICAL to the saved controls (relu(-16.7) == relu(-16.75) == 0).
CPU-only, no live changes.
"""
import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN, MEAS0 = 400, 6000, 1500
G, BETA = 0.01, 2.0

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
lsrc, ldst, ltyp, lside, lnt = loc[gsrc], loc[gdst], typ[keep], side[keep], nt_names[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy((gw * signA[lsrc]).astype(np.float32)), (n, n)
).coalesce().to_sparse_csr()
motor = np.isin(sup[keep], ["vnc_motor", "cb_motor"])
tm = pd.Series(ltyp)
fT = np.where(motor & tm.isin(["Tr flexor MN", "tr flexor MN"]))[0]
eT = np.where(motor & (tm == "Tr extensor MN"))[0]
fL_T = fT[lside[fT] == "L"]
fR_T = fT[lside[fT] == "R"]
eL_T = eT[lside[eT] == "L"]
eR_T = eT[lside[eT] == "R"]
dng100 = np.where(ltyp == "DNg100")[0]


def run(seed, D):
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
    flx = np.zeros(WIN, np.float32)
    ext = np.zeros(WIN, np.float32)
    mm = np.zeros(WIN, np.float32)
    for i in range(WIN):
        X = step(X)
        flx[i] = X[fL_T].mean() + X[fR_T].mean()
        ext[i] = X[eL_T].mean() + X[eR_T].mean()
        mm[i] = X[motor].mean()
    return flx, ext, mm


tr = np.load("l35/traces.npz")
print(f"{'seed':>4} {'D':>5} | bit-identical flx/mm vs saved ctrl | max|dflx| max|dmm|")
for seed in (11, 22, 33):
    flx, ext, mm = run(seed, 0.0)
    c_flx, c_mm = tr[f"ctrl_{seed}"], tr[f"ctrl_{seed}_mm"]
    same = bool(np.array_equal(flx, c_flx) and np.array_equal(mm, c_mm))
    print(f"{seed:>4} {0.0:>5} | {str(same):>31} | "
          f"{np.abs(flx - c_flx).max():.2e} {np.abs(mm - c_mm).max():.2e}")
print("done")
