"""Research tick 61 (hour-21 scan) — static preflight for the L45 amendment,
informed by Pugliese/Chou/Abe/Turcu/Lancaster/Tuthill/Brunton, Nature 2026
("Connectome simulations identify a CPG for fly walking"; bioRxiv
2025.09.12.675944). Pure STATIC probe on MaleCNS raw feathers; no rollouts,
no live changes, CPU-only.

Questions (their instruments, our graph):
 1. What are DNg100's and DNb08's top OUT targets in MaleCNS (their screen:
    DNg100 top rhythm driver, DNb08 second pathway; DNg100 enters the CPG at
    ONE excitatory interneuron, E1, receiving only 0.49% of its output)?
 2. Cyclic E-E-I triad census (E1->E2->I->E1, signs from source nt:
    ach=+, gaba/glut=-) on the T1 cord-intrinsic sheet vs a label-shuffle
    null (5 draws). MANC front-leg reference: 21,544 instances vs 307+-29.
 3. Do DNg100/DNb08 top targets sit in the STRONGEST cyclic triads?
"""
import numpy as np
import pandas as pd

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
bodyids = lab["bodyId"].to_numpy(np.uint64)

neu_cols = [c for c in lab.columns if "euromere" in c.lower()]
neuro = lab[neu_cols[0]].astype(str).to_numpy() if neu_cols else np.array(["?"] * len(lab))

nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather",
                     columns=["body", "consensus_nt"])
nt_map = dict(zip(nt["body"].astype(np.uint64).astype(str), nt["consensus_nt"]))
ntn = np.array([str(nt_map.get(str(int(b)), "unknown")).lower() for b in bodyids])
EXC = ntn == "acetylcholine"
INH = np.isin(ntn, ["gaba", "glutamate"])

w = pd.read_feather(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
pos = {int(r): i for i, r in enumerate(bodyids)}
src = w["body_pre"].map(pos).to_numpy(np.float64)
dst = w["body_post"].map(pos).to_numpy(np.float64)
keep = ~np.isnan(src) & ~np.isnan(dst)
src = src[keep].astype(np.int64); dst = dst[keep].astype(np.int64)
gw = w["weight"].to_numpy(np.float32)[keep]
print(f"labeled edges: {len(src):,}", flush=True)


def out_targets(name, topn=12):
    cells = np.where(typ == name)[0]
    m = np.isin(src, cells)
    if not m.any():
        print(f"{name}: NOT FOUND"); return set()
    agg = {}
    for s, d, wt in zip(src[m], dst[m], gw[m]):
        agg[int(d)] = agg.get(int(d), 0.0) + float(wt)
    tot = sum(agg.values())
    top = sorted(agg.items(), key=lambda kv: -abs(kv[1]))[:topn]
    print(f"\n{name} ({len(cells)} cells, out-weight total {tot:,.0f}): top targets")
    for d, wsum in top:
        print(f"   {abs(wsum)/tot*100:5.2f}% -> {typ[d]:<28} {sup[d]:<14} nt={ntn[d]:<12} w={wsum:,.0f}")
    return set(agg)


dng100_t = out_targets("DNg100")
dnb08_t = out_targets("DNb08")

# ---- cyclic E-E-I triad census on T1 intrinsic sheet ----
t1 = (sup == "vnc_intrinsic") & (neuro == "T1")
t1_idx = set(np.where(t1)[0].tolist())
m = np.isin(src, list(t1_idx)) & np.isin(dst, list(t1_idx))
S, D, W = src[m], dst[m], gw[m]
print(f"\nT1 intrinsic subgraph: {len(t1_idx)} cells, {len(S):,} edges", flush=True)

edge = {}
for s, d, wt in zip(S, D, W):
    edge[(int(s), int(d))] = edge.get((int(s), int(d)), 0.0) + float(wt)
out_nbr = {}
for (s, d) in edge:
    out_nbr.setdefault(s, []).append(d)


def census(exc_mask):
    triads = []
    for e1, nbrs in out_nbr.items():
        if not exc_mask[e1]:
            continue
        for e2 in nbrs:
            if e2 == e1 or not exc_mask[e2]:
                continue
            for i1 in out_nbr.get(e2, ()):
                if i1 == e1 or i1 == e2 or exc_mask[i1] or not INH[i1]:
                    continue
                if (i1, e1) in edge:
                    triads.append((
                        min(abs(edge[(e1, e2)]), abs(edge[(e2, i1)]),
                            abs(edge.get((i1, e1), 0.0))),
                        e1, e2, i1))
    return triads


tr = census(EXC)
print(f"cyclic E-E-I triads (real labels): {len(tr):,}", flush=True)
rng = np.random.default_rng(7)
null_counts = []
t1_arr = np.where(t1)[0]
for _ in range(5):
    perm = rng.permutation(len(t1_arr))
    shuffled = np.zeros_like(EXC)
    shuffled[t1_arr[perm[:int(EXC[t1_arr].sum())]]] = True
    null_counts.append(len(census(shuffled)))
print(f"label-shuffle null (5 draws): {np.mean(null_counts):,.0f} +- {np.std(null_counts):,.0f}"
      f"  {null_counts}", flush=True)

tr.sort(key=lambda t: -t[0])
hit100 = dng100_t
print("\ntop-10 strongest triads (min-edge weight; * = direct DNg100 target, + = DNb08):")
for minw, e1, e2, i1 in tr[:10]:
    m1 = "*" if e1 in hit100 else " "
    m2 = "+" if e1 in dnb08_t else " "
    print(f"   minw={minw:8,.0f}  E1={typ[e1]:<22}{m1}{m2} E2={typ[e2]:<22} I={typ[i1]:<22}")
n_overlap = sum(1 for _, e1, _, _ in tr[:100] if e1 in hit100)
print(f"\nDNg100-direct-target E1s among top-100 triads: {n_overlap}/100")
