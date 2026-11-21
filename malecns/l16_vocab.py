"""L16 vocab probe: motor type names (antagonist pairs?), cord class names, arc edge counts."""
import numpy as np, pandas as pd, torch

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()

print("superclass counts:")
for s, c in pd.Series(sup).value_counts().items():
    print(f"  {s:24s} {c}")

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
mt = pd.Series(typ[motor])
print(f"\nmotor cells {len(motor)}; unique types {mt.nunique()}")
kw = ["flex", "exten", "swing", "stance", "tibia", "femur", "tarsus", "trochanter"]
for k in kw:
    hits = sorted(set(mt[mt.str.contains(k, case=False)]))
    print(f"  {k:12s} {len(hits):3d} types: {hits[:10]}")

# intrinsic / local vnc classes
for cand in ["vnc_local", "vnc_intrinsic", "intrinsic", "vnc_interneuron", "cb_local"]:
    m = sup == cand
    if m.sum():
        print(f"\n{cand}: {m.sum()} cells; classes: {pd.Series(cls[m]).value_counts().head(8).to_dict()}")

ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
rows = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
cord_sens = sup == "vnc_sensory"
intr = np.isin(sup, ["vnc_local", "vnc_intrinsic", "intrinsic", "vnc_interneuron", "cb_local"])
mrow = np.zeros(N, bool); mrow[motor] = True
print(f"\narc edges: sensory->intrinsic {int((intr[rows] & cord_sens[cols]).sum()):,} | "
      f"intrinsic->motor {int((mrow[rows] & intr[cols]).sum()):,} | "
      f"sensory->motor direct {int((mrow[rows] & cord_sens[cols]).sum()):,} | "
      f"intrinsic->intrinsic {int((intr[rows] & intr[cols]).sum()):,}")
print(f"intrinsic mask total cells: {int(intr.sum())}")
