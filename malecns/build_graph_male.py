"""R4: port build_graph.py to MaleCNS v1.0 (lab artifact — NOT the live graph).

Differences from the female v783 build:
  - ids come from the annotations feather (superclass non-null), no .npy
  - per-body consensus_nt replaces per-edge *_avg argmax (same granularity:
    build_graph collapses per-connection probs to per-presynaptic anyway)
  - carries a superclass class-code array for DN/motor/sensory masking (L7)
Saves male_graph.pt in this lab dir. Never touches ~/critters/peabrain/.
"""
import numpy as np
import pandas as pd
import torch

DATA = "/home/t3rpz/critters/peabrain-lab/malecns/data"
NT_CLASS = {  # same convention as build_graph.py
    "acetylcholine": ("exc", 1.0), "glutamate": ("exc", 1.0),
    "gaba": ("inh", -1.0),
    "dopamine": ("mod", 0.2), "serotonin": ("mod", 0.2),
    "octopamine": ("mod", 0.2),
}
NT_ID = {n: i for i, n in enumerate(
    ["acetylcholine", "glutamate", "gaba", "dopamine", "serotonin",
     "octopamine", "unknown"])}

ann = pd.read_feather(f"{DATA}/body-annotations-male-cns-v1.0-minconf-0.5.feather")
labeled = ann[ann["superclass"].notna()]
ids = labeled["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
N = len(ids)
print(f"{N} labeled neurons")

nt = pd.read_feather(
    f"{DATA}/body-neurotransmitters-male-cns-v1.0.feather",
    columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64), nt["consensus_nt"]))
nt_names = labeled["bodyId"].map(nt_map).fillna("unknown")
nt_ids = np.array([NT_ID.get(str(n).lower(), NT_ID["unknown"]) for n in nt_names], np.int8)
sign = np.array([NT_CLASS.get(str(n).lower(), ("unk", 0.3))[1] for n in nt_names], np.float32)
print("transmitter mix:", pd.Series(nt_names).value_counts().head(8).to_dict())

w = pd.read_feather(
    f"{DATA}/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(idx) & w["body_post"].isin(idx)]
print(f"{len(w):,} edges after id filter")
src = w["body_pre"].map(idx).to_numpy(np.int64)
dst = w["body_post"].map(idx).to_numpy(np.int64)
wv = np.log1p(w["weight"].to_numpy(np.float32))

Wv = wv * sign[src]
indeg = np.zeros(N, np.float32)
np.add.at(indeg, dst, np.abs(Wv))
Wv = Wv / np.maximum(indeg, 1.0)[dst]

W = torch.sparse_coo_tensor(
    torch.from_numpy(np.stack([dst, src])), torch.from_numpy(Wv), (N, N)
).coalesce().to_sparse_csr()
print("graph:", tuple(W.shape), "nnz:", W._nnz())

# superclass codes for L7 masking
classes = sorted(labeled["superclass"].unique().tolist())
cid = {c: i for i, c in enumerate(classes)}
cls = labeled["superclass"].map(cid).to_numpy(np.int16)

# spectral radius sanity (power iteration, like brain.py's gain setting).
# CPU + 2-D operand: sparse.mm with a 1-D vector falls back to DENSE
# (103 GiB alloc attempt measured) — [N,1] keeps it a true sparse matmul.
v = torch.rand(N, 1); v /= v.norm()
rho = 0.0
for _ in range(200):
    u = torch.sparse.mm(W, v)
    n = u.norm()
    if n == 0 or torch.isnan(n):
        rho = float("nan"); break
    rho = float(n)
    v = u / n
print(f"rho (power iteration, cpu): {rho:.4f}")

torch.save({
    "W": W, "ids": torch.from_numpy(ids), "nt": torch.from_numpy(nt_ids),
    "nt_names": list(NT_ID.keys()),
    "cls": torch.from_numpy(cls), "cls_names": classes,
    "meta": {
        "source": "MaleCNS v1.0 (Berg et al. 2026 Cell 189:5504, CC BY 4.0), "
                  "significant-only weights, minconf 0.5",
        "neurons": int(N), "edges": int(len(w)),
        "signs": {k: v[1] for k, v in NT_CLASS.items()},
    },
}, "male_graph.pt")
print("saved male_graph.pt")
