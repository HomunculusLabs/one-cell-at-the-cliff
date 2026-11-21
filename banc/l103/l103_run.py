"""L103 run: unpaired-pool closure census (long_tendon + femur_reductor).
PREREG l103/PREREG.md FIRST. Machinery = l101_run.py VERBATIM (extraction,
two-generator noise law, joint settle, AMPA/PHI, DNg100 tonic); ARMS =
["cfn"] only — with the l101 draw order kept exactly, the cfn trajectory
must be BIT-IDENTICAL to raw_l101.npz (mm/xm 51 seeds, af exact) and the
Ti_aL/Ti_bR pool traces (ANCHOR seeds) must reproduce l101's too
(pool-extraction certification). Pools: LT_L/LT_R/FR_L/FR_R from
l103/static.json. Resume-safe; raw checkpoint BEFORE analysis.
"""
import json
import math
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, WIN = 400, 6000
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
BETA, D = 2.0, 0.2
ENT_AMP = 0.1
G_NEW = 0.153125
ANCHOR = [11, 22, 33]
B4 = list(range(801, 817))
B5 = list(range(901, 917))
B6 = list(range(1001, 1017))
PLAN = [("ANCH", ANCHOR), ("B4", B4), ("B5", B5), ("B6", B6)]
STATIC = json.load(open("l103/static.json"))
STATIC92 = json.load(open("l92/static.json"))
UNPAIRED = ["LT", "FR"]
TOKEN = {"LT": "long_tendon", "FR": "femur_reductor"}
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- extraction (l101_run.py verbatim) ----------------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv("data/dv_11837016", low_memory=False,
                 usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64),
                  nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate":
        is_glut[j] = True

region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
ann_gi = ann.gi.to_numpy()
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True

conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into = dn_into & dn_all
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj = dn_proj & dn_all
keep_old = cord_mask | dn_into
keep_new = cord_mask | dn_into | dn_proj
n_old, n_new = int(keep_old.sum()), int(keep_new.sum())
assert (n_old, n_new) == (STATIC92["n_old"], STATIC92["n_new"]), (n_old, n_new)


def build(keep):
    emask = keep[src_all] & keep[dst_all]
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a = sign_all[gsrc]
    gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
    vals = (np.log1p(gcount) * gsign_b).astype(np.float32)
    W = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([ldst, lsrc])).long(),
        torch.from_numpy(vals), (int(keep.sum()), int(keep.sum()))
    ).coalesce().to_sparse_csr()
    return W, loc


Wc_old, loc_o = build(keep_old)
Wc_new, loc_n = build(keep_new)
assert Wc_old.values().numel() == STATIC92["edges_old"]
assert Wc_new.values().numel() == STATIC92["edges_new"]


def wb(W):
    neg = W.values() < 0
    vals = W.values().clone()
    vals[neg] *= BETA
    return torch.sparse_csr_tensor(W.crow_indices(), W.col_indices(), vals, W.shape)


Wb_old, Wb_new = wb(Wc_old), wb(Wc_new)

gi_old = np.where(keep_old)[0]
gi_new = np.where(keep_new)[0]
new_g = gi_new[~np.isin(gi_new, gi_old)]
n_add = len(new_g)
assert n_add == STATIC92["dn_new"], (n_add, STATIC92["dn_new"])
old_pos_in_new = loc_n[gi_old]
new_pos = loc_n[new_g]

# pools: 2 unpaired pools x 2 sides + Ti cert pools (l101 names)
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOLS = {}
for k in UNPAIRED:
    hit = has(TOKEN[k])
    for c in ("L", "R"):
        m_n = keep_new[mgi] & hit & (side_m == SIDE_MAP[c])
        POOLS[f"{k}_{c}"] = np.sort(loc_n[mgi[m_n]])
for k in UNPAIRED:
    for c in ("L", "R"):
        assert len(POOLS[f"{k}_{c}"]) == STATIC["sizes"][f"{k}_{c}"], (k, c)
# cert pools: Ti agonist L + antagonist R (l101 exact definitions)
CERT_POOLS = {
    "Ti_aL": np.sort(loc_n[mgi[keep_new[mgi] & has("tibia") & has("flexor")
                               & (side_m == "left")]]),
    "Ti_bR": np.sort(loc_n[mgi[keep_new[mgi] & has("tibia") & has("extensor")
                               & (side_m == "right")]]),
}
assert len(CERT_POOLS["Ti_aL"]) == 50 and len(CERT_POOLS["Ti_bR"]) == 6

motor_n = np.zeros(n_new, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor_n[loc_n[mg[keep_new[mg]]]] = True
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech_n = np.where(mech_mask[keep_new])[0]
mech_o = np.where(mech_mask[keep_old])[0]
assert len(mech_n) == STATIC92["mech"]

dng100_all = ann[ann.super_class == "descending"]
ct_dn = dng100_all.cell_type.fillna("").astype(str).to_numpy()
dng100_gi = dng100_all.gi[ct_dn == "DNg100"].to_numpy()
dng100_n = np.sort(loc_n[dng100_gi[keep_new[dng100_gi]]])
assert len(dng100_n) == STATIC92["dng100"]
log(f"subnet {n_new:,} edges {Wc_new.values().numel():,} | mech {len(mech_n)} "
    f"| pools {sum(len(v) for v in POOLS.values())} cells "
    f"(+{len(CERT_POOLS)} cert pools) | {time.time()-t0:.0f}s")

# schedule (l101 verbatim)
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + 2000:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + 2000)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
assert int((AMPA > 0).sum()) + SETTLE == 4800
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------------- resume ----------------
store = {}
if os.path.exists("l103/raw_partial.npz"):
    z = np.load("l103/raw_partial.npz")
    store = {k: z[k] for k in z.files}
    log(f"resume: {len([k for k in store if k.startswith('mm_')])} seeds cached")


def save_partial():
    if store:
        np.savez("l103/raw_partial.npz", **store)


# ---------------- rollouts: cfn only, l101 draw order EXACT ----------------
for bname, seeds in PLAN:
    for seed in seeds:
        if f"mm_cfn_{seed}" in store:
            continue
        gen = torch.Generator().manual_seed(seed)
        gen2 = torch.Generator().manual_seed(seed + 9000)
        X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
        X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
        Io = torch.zeros(n_old, 1)
        dng100_o = np.sort(loc_o[dng100_gi[keep_old[dng100_gi]]])
        Io[dng100_o] = D
        In = torch.zeros(n_new, 1)
        In[dng100_n] = D
        Xc = torch.zeros(n_new, 1)
        Xc[old_pos_in_new] = X0o
        Xc[new_pos] = X0n
        Xo = X0o.clone()
        sp = 0.0
        for _ in range(SETTLE):
            nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
            nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
            nzn = torch.zeros(n_new, 1)
            nzn[old_pos_in_new] = nz_o
            nzn[new_pos] = nz_a
            sp += 2 * math.pi * 0.7 * DT
            sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
            drive = torch.sparse.mm(Wb_old, Xo) * G_NEW + Io
            drive[mech_o, 0] = drive[mech_o, 0] + sin_t
            Xo = Xo + (DT / TAU) * ((torch.relu(drive + BG) + nz_o)
                                    .clamp(max=RMAX) - Xo)
            drive = torch.sparse.mm(Wb_new, Xc) * G_NEW + In
            drive[mech_n, 0] = drive[mech_n, 0] + sin_t
            Xc = Xc + (DT / TAU) * ((torch.relu(drive + BG) + nzn)
                                    .clamp(max=RMAX) - Xc)
        af_c = float((Xc > 0.05).float().mean())
        assert 0.01 < af_c < 0.9, af_c
        X = Xc.clone()
        mm = np.zeros(WIN, np.float32)
        xm = np.zeros(WIN, np.float32)
        tr = {kk: np.zeros(WIN, np.float32) for kk in POOLS}
        if seed in ANCHOR:
            tr.update({kk: np.zeros(WIN, np.float32) for kk in CERT_POOLS})
        for k in range(WIN):
            nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
            nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
            nzn = torch.zeros(n_new, 1)
            nzn[old_pos_in_new] = nz_o
            nzn[new_pos] = nz_a
            sin_t = ENT_AMP * (0.5 + 0.5 * np.sin(PHI[k])) if AMPA[k] > 0 else 0.0
            drive = torch.sparse.mm(Wb_new, X) * G_NEW + In
            if sin_t > 0:
                drive[mech_n, 0] = drive[mech_n, 0] + sin_t
            t = torch.relu(drive + BG)
            t = (t + nzn).clamp(max=RMAX)
            X = X + (DT / TAU) * (t - X)
            mm[k] = X[motor_n].mean()
            xm[k] = X[mech_n].mean()
            for kk in tr:
                tr[kk][k] = X[POOLS.get(kk, CERT_POOLS.get(kk))].mean()
        store[f"mm_cfn_{seed}"] = mm
        store[f"xm_cfn_{seed}"] = xm
        for kk in tr:
            store[f"{kk}_cfn_{seed}"] = tr[kk]
        store[f"af_cfn_{seed}"] = np.float32(af_c)
        save_partial()
        log(f"{bname} seed {seed} done af {af_c:.5f} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")
np.savez_compressed("l103/raw_l103.npz", g_new=np.float64(G_NEW),
                    pools=np.array(list(POOLS)),
                    cert_pools=np.array(list(CERT_POOLS)), **store)
log("raw_l103.npz checkpointed BEFORE analysis")

# ---------------- anchors (enumerated keys ONLY) ----------------
z101 = np.load("l101/raw_l101.npz")
ALL = ANCHOR + B4 + B5 + B6
c0a = {}
for s in ALL:
    for key in ("mm", "xm"):
        c0a[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_cfn_{s}"] - z101[f"{key}_cfn_{s}"][:WIN]).max())
    # af exact (C1 leg)
    c0a[f"af_{s}"] = float(store[f"af_cfn_{s}"]) - float(z101[f"af_cfn_{s}"])
for s in ANCHOR:
    for kk in CERT_POOLS:
        c0a[f"{kk}_{s}"] = float(np.abs(
            store[f"{kk}_cfn_{s}"] - z101[f"{kk}_cfn_{s}"][:WIN]).max())
out = dict(c0a_max=max(c0a.values()),
           c0a_pass=bool(all(v == 0.0 for v in c0a.values())),
           c0a_detail=c0a)
c1 = all(0.01 < float(store[f"af_cfn_{s}"]) < 0.9 for s in ALL)
out["c1"] = bool(c1)
out["af_anchor"] = {str(s): float(store[f"af_cfn_{s}"]) for s in ANCHOR}
json.dump(out, open("l103/anchors_run.json", "w"), indent=1)
log(f"C0A {out['c0a_pass']} (max {out['c0a_max']:.1e}) | C1 {out['c1']} "
    f"| done {time.time()-t0:.0f}s")
