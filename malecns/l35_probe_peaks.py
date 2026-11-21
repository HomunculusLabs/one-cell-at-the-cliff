"""L35 probe: peak-detector params on the seed-11 control mm trace (run 3
stopped at the train-vs-anchor gate; no PRC arm has run)."""
import sys

import numpy as np

sys.path.insert(0, ".")
import importlib.util

spec = importlib.util.spec_from_file_location("l35m", "l35_phasereset.py")
# we canNOT import the module (it runs everything); copy the minimal funcs
DT = 0.01
ANCHOR = {11: 0.800, 22: 1.444, 33: 1.422}


def smooth(x, w):
    return np.convolve(x, np.ones(w) / w, mode="same")


def peaks(sig, lo, gap, w):
    s = smooth(sig, w)[lo:]
    cand = np.where((s[1:-1] > s[:-2]) & (s[1:-1] >= s[2:]))[0] + 1
    keep_i = []
    for c in cand:
        if keep_i and c - keep_i[-1] < gap:
            if s[c] > s[keep_i[-1]]:
                keep_i[-1] = c
        else:
            keep_i.append(c)
    return np.array([lo + c for c in keep_i], float)


# regenerate seed 11 control mm by re-running the l35 stage machinery
import torch

torch.set_num_threads(8)
import pandas as pd

TAU, RMAX, BG, NOISE = 0.05, 1.0, 0.02, 0.01
SETTLE, WIN, MEAS0 = 400, 6000, 1500
G, BETA, D = 0.01, 2.0, 0.05
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
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
lnt = nt_names[keep]
SIG_A = {"acetylcholine": 1.0, "glutamate": 1.0, "gaba": -1.0, "dopamine": 0.2,
         "serotonin": 0.2, "octopamine": 0.2}
signA = np.array([SIG_A.get(t, 0.3) for t in lnt], np.float32)
Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([loc[gdst], loc[gsrc]])).long(),
    torch.from_numpy((gw * signA[loc[gsrc]]).astype(np.float32)), (n, n)
).coalesce().to_sparse_csr()
motor = np.isin(sup[keep], ["vnc_motor", "cb_motor"])
dng100 = np.where(sup[keep] == "descending_neuron")[0][0:0]  # unused
typk = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()[keep]
dng100 = np.where(typk == "DNg100")[0]

gen = torch.Generator().manual_seed(11)
X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
neg = Wc.values() < 0
vals = Wc.values().clone()
vals[neg] *= BETA
Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals, Wc.shape)
I = torch.zeros(n, 1)
I[dng100] = D


def step(cur, k):
    drive = torch.sparse.mm(Wb, cur) * G + I
    t = torch.relu(drive + BG)
    t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
    return cur + (DT / TAU) * (t - cur)


for k in range(SETTLE):
    X = step(X, k)
mm = np.zeros(WIN, np.float32)
for i in range(WIN):
    X = step(X, SETTLE + i)
    mm[i] = X[motor].mean()
np.save("l35/probe_s11_mm.npy", mm)
z = mm[MEAS0:] - mm[MEAS0:].mean()
ps = np.abs(np.fft.rfft(z)) ** 2
fr = np.fft.rfftfreq(len(z), DT)
band = (fr >= 0.5) & (fr <= 10)
print("dom", fr[band][np.argmax(ps[band])])
for wsm in (15, 21, 31):
    for frac in (0.55, 0.7, 0.8):
        gap = int(round(frac / 0.800 / DT))
        pk = peaks(mm, MEAS0, gap, wsm)
        per = np.median(np.diff(pk)) * DT
        print(f"smooth {wsm:>2} frac {frac:.2f} gap {gap:>3}: {len(pk)} peaks, "
              f"median {per:.3f}s ({1/per:.2f} Hz), "
              f"int-spread {np.diff(pk).min()*DT:.2f}-{np.diff(pk).max()*DT:.2f}s")
