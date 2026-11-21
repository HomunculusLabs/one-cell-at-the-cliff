"""L38 addendum: per-SIDE cell counts (free vs pinned) — the side verdict
aggregates cells; record the composition. Census identical to l38_primitives
(3 seeds, settle 400, window 600). Amends primitives_viable.csv in place and
dumps per-cell stats for the dose channels."""
import json

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX, BG, NOISE = 0.05, 0.01, 1.0, 0.02, 0.01
G, BETA = 0.01, 2.0
WIN = 600

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side_raw = lab["somaSide"].to_numpy()
side_all = np.array([s if isinstance(s, str) else "?" for s in side_raw])
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
lside, lbid = side_all[keep], ids[keep]
assert n == 21516 and len(lsrc) == 2977920
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

dn_cells = np.where(lsup == "descending_neuron")[0]
dn_side, dn_typ = lside[dn_cells], ltyp[dn_cells]
dn_bid = lbid[dn_cells]
umax = np.full(len(dn_cells), -1e9)
xsum = np.zeros(len(dn_cells))
xc = 0.0
for seed in (11, 22, 33):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    for _ in range(400):
        d = torch.sparse.mm(Wb, X) * G
        t = (torch.relu(d + BG) + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
    for _ in range(WIN):
        d = torch.sparse.mm(Wb, X) * G
        t = (torch.relu(d + BG) + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
        umax = np.maximum(umax, (torch.sparse.mm(Wb, X) * G + BG)[dn_cells, 0].numpy())
        xsum += X[dn_cells, 0].numpy()
        xc += 1
xmean = xsum / xc
free = (umax > 0) & (xmean < 0.95)
pinned = (umax > 0) & (xmean >= 0.95)

df = pd.read_csv("l38/primitives_viable.csv")
rows = {r.dn_type: r for r in df.itertuples()}
add = {}
for tname in df.dn_type:
    m = dn_typ == tname
    entry = {}
    for sd in ("L", "R"):
        ms = m & (dn_side == sd)
        entry[f"cells_free_{sd}"] = int((free & ms).sum())
        entry[f"cells_pinned_{sd}"] = int((pinned & ms).sum())
        entry[f"cells_total_{sd}"] = int(ms.sum())
    add[tname] = entry
for col in [f"{k}_{sd}" for k in ("cells_free", "cells_pinned", "cells_total")
            for sd in ("L", "R")]:
    df[col] = [add[t][col] for t in df.dn_type]
df.to_csv("l38/primitives_viable.csv", index=False)

# per-cell dump for the dose channels
dump = {}
for tname in ("DNge059", "DNge046", "DNg110", "MDN", "DNg88", "DNg100", "DNg95"):
    m = np.where(dn_typ == tname)[0]
    dump[tname] = [dict(bodyId=int(dn_bid[i]), side=str(dn_side[i]),
                        u_max=round(float(umax[i]), 3),
                        mean_X=round(float(xmean[i]), 4),
                        cls=("pinned" if pinned[i] else
                             "free" if free[i] else "below-floor"))
                   for i in m]
json.dump(dump, open("l38/cells_dump.json", "w"), indent=1)
print("types with pinned-only side (R pinned & no free R):",
      int(sum(1 for t, e in add.items()
              if e["cells_pinned_R"] > 0 and e["cells_free_R"] == 0)))
print("types with free cells both sides:",
      int(sum(1 for t, e in add.items()
              if e["cells_free_L"] > 0 and e["cells_free_R"] > 0)))
print(json.dumps(dump["DNge059"], indent=0))
print(json.dumps(dump["DNg88"], indent=0))
