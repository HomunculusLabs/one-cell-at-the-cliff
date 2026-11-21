"""L62 banc-eval v2: cord-lane objects on banc_graph.pt — SEGMENT arithmetic
on the CSR internals (no densify; 80k^2 dense = 26 GB, CSR internals are free).

CSR: W[target, source] — crow/col/val; row r's out... wait, CSR row = target.
W[dst, src]: row index = TARGET, col = SOURCE. So:
  - in-weight of node t = sum(val[crow[t]:crow[t+1]])           (row sums)
  - OUT-edges of node s = entries where col == s  (bincount over col)
"""
import numpy as np
import pandas as pd
import torch

D = "/home/t3rpz/critters/peabrain-lab/banc/data"
G = torch.load("banc_graph.pt", weights_only=False)
ids = G["ids"].numpy().astype(np.uint64)
crow = G["W"].crow_indices().numpy()
col = G["W"].col_indices().numpy()
val = G["W"].values().numpy()
N = int(G["N"])
idx = {int(r): i for i, r in enumerate(ids)}
rowsum = np.zeros(N, np.float64)
np.add.at(rowsum, np.repeat(np.arange(N), np.diff(crow)), val)  # in-weight

ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)
mm = pd.read_csv(f"{D}/dv_11837145", low_memory=False,
                 usecols=["pt_root_id", "match_cell_type", "valid"])
mv = mm[mm.valid.astype(str).str.lower().isin(["t", "true"])]
mv["gi"] = mv["pt_root_id"].astype(np.uint64).map(idx)

print("=== 1. antagonist pools (tibia flexor vs extensor MNs) ===")
mot = ann[ann.super_class == "motor"]
ptt = mot.peripheral_target_type.fillna("")
flex = mot[ptt.str.contains("tibia") & ptt.str.contains("flexor")]
ext = mot[ptt.str.contains("tibia") & ptt.str.contains("extensor")]
fi, ei = flex.gi.to_numpy(), ext.gi.to_numpy()
print(f"tibia flexor {len(fi)}, tibia extensor {len(ei)}")
print(f"  ext split: {ext.cell_type.value_counts().to_dict()}")
print(f"  flex split: {flex.cell_type.value_counts().head(5).to_dict()}")
print(f"  flex by leg: {flex.cell_sub_class.fillna('?').value_counts().to_dict()}")
fw, ew = rowsum[fi], rowsum[ei]
print(f"in-weight flex {fw.mean():.2f}±{fw.std():.2f} / ext {ew.mean():.2f}±{ew.std():.2f}")

vin_mask = np.zeros(N, bool)
vin_mask[ann[ann.super_class == "ventral_nerve_cord_intrinsic"].gi.to_numpy()] = True
flex_tot = fw.sum()
flex_from_vin = sum(val[crow[t]:crow[t+1]][vin_mask[col[crow[t]:crow[t+1]]]].sum()
                    for t in fi)
print(f"flexor in-weight from vnc_intrinsic: {flex_from_vin/flex_tot*100:.1f}%")

print("\n=== 2. Pugliese triad cells ===")
PUG = ["IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012"]
fset = set(fi.tolist())
outw = np.zeros(N); np.add.at(outw, col, val)  # out-weight per SOURCE
for t in PUG:
    hit = mv[mv.match_cell_type.astype(str) == t]
    gis = hit.gi.dropna().astype(int).to_numpy()
    if len(gis) == 0:
        print(f"  {t}: 0 in graph"); continue
    # direct triad->flexor: entries in flexor ROWS whose col is a triad cell
    tset = set(gis.tolist())
    tf = 0.0
    for r in fi:
        seg = slice(int(crow[r]), int(crow[r + 1]))
        m = np.isin(col[seg], list(tset))
        tf += float(val[seg][m].sum())
    print(f"  {t}: {len(gis)} cells, out-w {outw[gis].sum():.2f}, ->flexor w {tf:.3f}")

print("\n=== 3. DN command vocabulary (cell_type exact) ===")
dn = ann[ann.super_class == "descending"]
ct = dn.cell_type.fillna("")
for name in ["DNp01", "DNp02", "DNp03", "DNp04", "DNg100", "DNg95", "DNg105",
             "DNg88", "DNge046", "DNg35", "DNg110"]:
    print(f"  {name}: {(ct == name).sum()}", end="")
print()
ndn_type = dn.cell_type.notna().sum()
print(f"descending w/ any cell_type: {ndn_type:,}/{len(dn):,}")

print("\n=== 4. cord sheet size ===")
for s in ["ventral_nerve_cord_intrinsic", "sensory", "motor", "ascending", "descending"]:
    print(f"  {s}: {(ann.super_class == s).sum():,}")
