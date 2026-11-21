"""L62 banc-eval: port build_graph.py to BANC v626 (lab artifact — NOT live).

Same pattern as the MaleCNS port (build_graph_male.py):
  - ids from the codex flat annotations (superclass non-null)
  - per-body NT sign from the NT prediction table (root_626 join)
  - per-neuropil connection rows collapsed to unique pairs (sum syn_count),
    log1p weights, sign from presynaptic NT
  - super_class code array for DN/motor/sensory masking
Histamine sign rule: -1 (inhibitory, photoreceptor convention — ConnectomeKG);
tyramine unresolved -> unk 0.3.
Saves banc_graph.pt in this lab dir. Never touches ~/critters/peabrain/.
"""
import numpy as np
import pandas as pd
import torch

DATA = "/home/t3rpz/critters/peabrain-lab/banc/data"
NT_CLASS = {
    "acetylcholine": ("exc", 1.0), "glutamate": ("exc", 1.0),
    "gaba": ("inh", -1.0), "histamine": ("inh", -1.0),
    "dopamine": ("mod", 0.2), "serotonin": ("mod", 0.2),
    "octopamine": ("mod", 0.2), "tyramine": ("unk", 0.3),
}
NT_ID = {n: i for i, n in enumerate(
    ["acetylcholine", "glutamate", "gaba", "histamine", "dopamine",
     "serotonin", "octopamine", "tyramine", "unknown"])}

ann = pd.read_csv(f"{DATA}/dv_11845666", sep="\t", low_memory=False)
labeled = ann[ann["super_class"].notna()].copy()
ids = labeled["pt_root_id"].astype(np.uint64).to_numpy()
idx = {int(r): i for i, r in enumerate(ids)}
N = len(ids)
print(f"{N:,} labeled neurons")

nt = pd.read_csv(f"{DATA}/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
nt_names = labeled["pt_root_id"].astype(np.uint64).map(nt_map).fillna("unknown")
nt_ids = np.array([NT_ID.get(n, NT_ID["unknown"]) for n in nt_names], np.int8)
sign = np.array([NT_CLASS.get(n, ("unk", 0.3))[1] for n in nt_names], np.float32)
print("transmitter mix:", pd.Series(nt_names).value_counts().head(9).to_dict())

cls_names = ["other", "descending", "motor", "sensory", "vnc_intrinsic",
             "cb_intrinsic", "ascending", "optic"]
SC2CLS = {"descending": 1, "motor": 2, "sensory": 3,
          "ventral_nerve_cord_intrinsic": 4, "central_brain_intrinsic": 5,
          "ascending": 6, "optic_lobe_intrinsic": 7, "visual_projection": 7,
          "visual_centrifugal": 7, "sensory_ascending": 3,
          "sensory_descending": 3, "visceral_circulatory": 5,
          "ascending_visceral_circulatory": 6}
cls = np.array([SC2CLS.get(s, 0) for s in labeled["super_class"]], np.int8)
print("cls counts:", {cls_names[c]: int((cls == c).sum()) for c in range(8)})

conn = pd.read_csv(f"{DATA}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx)
            & conn["post_root_id"].astype(np.uint64).isin(idx)]
print(f"{len(conn):,} neuropil rows after id filter")
g = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
pre = np.array([int(a) for a, _ in g.index], np.int64)
post = np.array([int(b) for _, b in g.index], np.int64)
src = np.array([idx[r] for r in pre], np.int64)
dst = np.array([idx[r] for r in post], np.int64)
wv = np.log1p(g.to_numpy(np.float32))
print(f"{len(src):,} unique edges, syn total {g.sum():,}")

Wv = wv * sign[src]
indeg = np.zeros(N, np.float32)
np.add.at(indeg, dst, np.abs(Wv))
Wv = Wv / np.maximum(indeg, 1.0)[dst]

W = torch.sparse_coo_tensor(
    torch.from_numpy(np.stack([dst, src])), torch.from_numpy(Wv), (N, N)
).coalesce().to_sparse_csr()
n_edges = int(W._nnz())

torch.save({
    "ids": torch.from_numpy(ids), "nt_ids": torch.from_numpy(nt_ids),
    "sign": torch.from_numpy(sign), "cls": torch.from_numpy(cls),
    "cls_names": cls_names, "n_edges": n_edges,
    "W": W, "N": N,
}, "banc_graph.pt")
print(f"saved banc_graph.pt: N={N:,} nnz={n_edges:,}")

Wc = W.to(torch.float64)
X = torch.rand(N, 1, dtype=torch.float64) + 0.5
for _ in range(60):
    X = Wc @ X / (X.norm() + 1e-12)
rho = float(X.abs().max())
print(f"rho (raw weights, unnormalized) = {rho:.4f}")
