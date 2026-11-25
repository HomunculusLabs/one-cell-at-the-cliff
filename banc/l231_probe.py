"""l231_probe.py — TOOLING feasibility probe, declared in l231/PREREG.md.

Asks ONLY: does the certified generic substrate builder build_sub() accept a
WHOLE-GRAPH keep mask, i.e. are all pool cells present in the unrestricted
node set with the SAME per-pool counts that S92 pins? Reads NOTHING about any
Perron vector or any left/right asymmetry.
"""
import json

import numpy as np
import pandas as pd
import torch

S92 = json.load(open("l92/static.json"))
S101 = json.load(open("l101/static.json"))["sizes"]

Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)
region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

print(f"Nall={Nall} annotated-in-graph={len(ann)}")
print(f"cord_mask={int(cord_mask.sum())}")

mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOL_G = {}
for k, fpat, epat, pf, pe in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor"), "f", "e"),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor"), "f", "e"),
    ("Ta", has("tarsus") & has("depressor"), has("tarsus") & has("levator"), "a", "b"),
    ("Sr", has("sternal") & has("anterior") & has("rotator"),
     has("sternal") & has("posterior") & has("rotator"), "a", "b"),
    ("Pr", has("promotor"), has("remotor"), "a", "b"),
]:
    for c in ("L", "R"):
        m1 = np.zeros(Nall, bool)
        m1[mgi[fpat & (side_m == SIDE_MAP[c])]] = True
        POOL_G[f"{k}_{pf}{c}"] = m1
        m2 = np.zeros(Nall, bool)
        m2[mgi[epat & (side_m == SIDE_MAP[c])]] = True
        POOL_G[f"{k}_{pe}{c}"] = m2

bad = []
for pk, want in S92["pool_sizes"].items():
    got_all = int(POOL_G[pk].sum())
    got_cord = int((POOL_G[pk] & cord_mask).sum())
    if got_all != want:
        bad.append((pk, want, got_all, got_cord))
print(f"S92 pool_sizes mismatched under keep=ALL: {len(bad)} -> {bad}")

bad2 = []
for pk, want in S101.items():
    if pk.split("_")[0] in ("Ti", "Tr"):
        continue
    got_all = int(POOL_G[pk].sum())
    if got_all != want:
        bad2.append((pk, want, got_all))
print(f"S101 (non-Ti/Tr) mismatched under keep=ALL: {len(bad2)} -> {bad2}")

# per-side label census of the annotated-in-graph population (the
# reconstruction caveat's row 1, population level only — no v1 involved)
sd = ann.side.fillna("").astype(str).str.lower().to_numpy()
print("side census (annotated & in graph):",
      {s: int((sd == s).sum()) for s in ("left", "right", "midline", "")})
for rg in ("ventral_nerve_cord", "central_brain", "optic_lobe",
           "neck_connective"):
    m = region == rg
    print(f"  {rg:20s} L {int((m & (sd=='left')).sum()):6d} "
          f"R {int((m & (sd=='right')).sum()):6d}")

# cross-pool disjointness under keep=ALL (build_sub's `pall` assert)
tot = 0
seen = {}
dup = []
for pk, m in POOL_G.items():
    g = np.where(m)[0]
    tot += len(g)
    for x in g:
        if x in seen:
            dup.append((int(x), seen[x], pk))
        seen[x] = pk
print(f"pool cells total {tot} unique {len(seen)} duplicates {dup}")
