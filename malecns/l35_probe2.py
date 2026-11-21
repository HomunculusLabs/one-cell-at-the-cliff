"""L35 mechanism probe (tick 52): WHY are volleys absorbed?

Hypotheses from the amp-dependence (8/24 absorbed @A0.05 -> 0/24 @A0.15 for
DNg95; 48/48 for DNg100 at both amps):
  FLOOR: DNg95's total drive u = W@X*G + I + BG sits BELOW 0 at absorbed
         phases (relu floor) — the volley must out-lift inhibition; a bigger
         amp does that, so absorption falls with amp.
  CEILING: DNg100 sits at the clamp ceiling (t>=1 / X pinned ~1) — extra
         drive changes nothing at ANY amp.

Probe: control rollouts (seeds 11, 22) recording u (pre-relu pre-clamp drive
+ BG) and X for the 4 volley cells; read them over each bin's actual volley
window (k0 from results_l35.json). Labels absorption per bin and tests which
hypothesis the numbers support. CPU-only, no live changes.
"""
import json

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 6000
G, BETA, D = 0.01, 2.0, 0.05
VSTEPS = 25

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
dng100 = np.where(ltyp == "DNg100")[0]
dng95 = np.where(ltyp == "DNg95")[0]
probe_cells = np.concatenate([dng95, dng100])


def run_probe(seed):
    gen = torch.Generator().manual_seed(seed)
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
        return cur + (DT / TAU) * (t - cur), drive

    for k in range(SETTLE):
        X, _ = step(X, k)
    u = np.zeros((WIN, len(probe_cells)), np.float32)
    xv = np.zeros((WIN, len(probe_cells)), np.float32)
    for i in range(WIN):
        X, dr = step(X, SETTLE + i)
        u[i] = (dr[probe_cells, 0] + BG).numpy()
        xv[i] = X[probe_cells, 0].numpy()
    return u, xv


r = json.load(open("l35/results_l35.json"))
out = {}
for seed in (11, 22):
    u, xv = run_probe(seed)
    bins = {}
    for b in range(8):
        phi = b * 45.0
        arm = next(a for a in r["arms"] if a["tag"] == "dng95" and a["seed"] == seed
                   and a["phi"] == phi and a["vamp"] == 0.05 and a["vsteps"] == 25)
        k0 = arm["k0"]
        seg_u = u[k0:k0 + VSTEPS, :2]          # DNg95 cells
        seg_x = xv[k0:k0 + VSTEPS, :2]
        g100_u = u[k0:k0 + VSTEPS, 2:]         # DNg100 cells
        g100_x = xv[k0:k0 + VSTEPS, 2:]
        bins[b] = dict(
            absorbed=bool(arm["dm_mm"] == 0.0),
            dng95_u_min=float(seg_u.min()), dng95_u_max=float(seg_u.max()),
            dng95_u_mean=float(seg_u.mean()),
            dng95_x_max=float(seg_x.max()),
            dng100_u_min=float(g100_u.min()), dng100_u_max=float(g100_u.max()),
            dng100_x_max=float(g100_x.max()))
    out[seed] = bins
    for b, d in bins.items():
        print(f"seed {seed} bin {b*45:>3} absorbed={str(d['absorbed']):5} | "
              f"DNg95 u [{d['dng95_u_min']:+.3f},{d['dng95_u_max']:+.3f}] "
              f"mean {d['dng95_u_mean']:+.3f} Xmax {d['dng95_x_max']:.3f} | "
              f"DNg100 u [{d['dng100_u_min']:+.3f},{d['dng100_u_max']:+.3f}] "
              f"Xmax {d['dng100_x_max']:.3f}")

json.dump(out, open("l35/probe_mech.json", "w"), indent=1)

# test: at absorbed bins, is DNg95 u < +0.05 (floor) vs landed bins u > 0.05?
for seed in (11, 22):
    ab = [d["dng95_u_max"] for d in out[seed].values() if d["absorbed"]]
    ld = [d["dng95_u_max"] for d in out[seed].values() if not d["absorbed"]]
    if ab and ld:
        print(f"seed {seed}: absorbed bins u_max {[f'{v:+.3f}' for v in ab]} | "
              f"landed u_max {[f'{v:+.3f}' for v in ld]}")
print("done -> l35/probe_mech.json")
