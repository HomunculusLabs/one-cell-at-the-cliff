"""L95 probe: fd-burial instrument validation on the L92 closure substrate.

PREREG l95/PREREG.md FIRST. Machinery = l93_run.py VERBATIM (extraction,
two-generator noise law, settle, AMPA schedule) — arms changed to the
registered d74b amp sweep; adds passive recording of base-arm drive u(k)
for all l93 volley cells during seg0 + d74b cell X per arm. No extra
generator draws inside the loop (noise order preserved -> bit-identity
anchors vs raw_l93.npz). CPU-only; raw checkpoint BEFORE analysis.
"""
import json
import math
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
SEG = 2000
BETA, D = 2.0, 0.2
ENT_AMP = 0.1
VOL0, VOL1 = 0, 2000
SEEDS = [11, 22, 33]
STATIC92 = json.load(open("l92/static.json"))
G_NEW = 0.153125
AMPS = [1.5, 1.8, 2.0, 3.0, 5.0]          # PREREG-pinned sweep
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- extraction (l93_run.py verbatim) ----------------
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
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
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

mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOLS_N = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor")),
]:
    for c in ("fL", "fR", "eL", "eR"):
        sel = fpat if c[0] == "f" else epat
        m_n = keep_new[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
        POOLS_N[f"{k}_{c}"] = np.sort(loc_n[mgi[m_n]])
for k in POOLS_N:
    assert len(POOLS_N[k]) == STATIC92["pool_sizes"][k], k

motor_n = np.zeros(n_new, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor_n[loc_n[mg[keep_new[mg]]]] = True
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech_n = np.where(mech_mask[keep_new])[0]
assert len(mech_n) == STATIC92["mech"]
mech_o = np.where(mech_mask[keep_old])[0]
assert len(mech_o) == STATIC92["mech"]

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_o = np.sort(loc_o[dng100_all[keep_old[dng100_all]]])
dng100_n = np.sort(loc_n[dng100_all[keep_new[dng100_all]]])
assert len(dng100_o) == len(dng100_n) == STATIC92["dng100"]

# ---------------- arms (PREREG-pinned) ----------------
z93 = np.load("l93/raw_l93.npz")
D74B = z93["d74b"].astype(np.int64)
assert len(D74B) == 1 and 0 <= D74B[0] < n_new
# union of ALL l93 volley cells -> base-drive recording set
UNION = np.unique(np.concatenate([
    z93["int16"], z93["ti16"], z93["xl080"], z93["d74b"], z93["d105"],
    z93["shamdn_a"], z93["shamdn_b"], z93["shamint_a"], z93["shamint_b"],
]).astype(np.int64))
assert np.isin(D74B, UNION).all()
log(f"union cells {len(UNION)} | d74b loc {int(D74B[0])}")

VOLLEYS = {"base": (None, 0.0)}
for amp in AMPS:
    VOLLEYS[f"d74b_{amp}"] = (D74B, float(amp))
ARMS = list(VOLLEYS)
for a, (cells, amp) in VOLLEYS.items():
    if cells is None:
        continue
    assert 0 < amp <= 5.0 and len(cells) > 0

# schedule (l93 verbatim)
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
assert int((AMPA > 0).sum()) + SETTLE == 4800
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

log(f"subnet ok n {n_new} arms {len(ARMS)} | {time.time()-t0:.0f}s")

# ---------------- rollouts (paired noise, shared settle; l93 verbatim) ----------------
z92 = np.load("l92/raw_l92.npz")
store = {}
AF_C = {}


def run_seed(seed):
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    Io = torch.zeros(n_old, 1)
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
    af_o = float((Xo > 0.05).float().mean())
    af_c = float((Xc > 0.05).float().mean())
    assert 0.01 < af_o < 0.9 and 0.01 < af_c < 0.9, (af_o, af_c)
    assert abs(af_c - float(z93[f"af_base_{seed}"])) < 1e-6, (seed, af_c)
    AF_C[seed] = af_c
    X = {a: Xc.clone() for a in ARMS}
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {k: np.zeros(WIN, np.float32) for k in POOLS_N} for a in ARMS}
    ub = np.zeros((SEG, len(UNION)), np.float32)          # base drive, seg0
    xd = {a: np.zeros(WIN, np.float32) for a in ARMS}     # d74b cell X
    ut = torch.zeros(n_new, 1)                            # scratch

    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        on = VOL0 <= k < VOL1
        for a in ARMS:
            cells, amp = VOLLEYS[a]
            drive = torch.sparse.mm(Wb_new, X[a]) * G_NEW + In
            if a == "base" and on:
                ut[UNION, 0] = drive[UNION, 0]
                ub[k] = ut[UNION, 0].numpy()
            if sin_t > 0:
                drive[mech_n, 0] = drive[mech_n, 0] + sin_t
            if on and cells is not None:
                drive[cells, 0] = drive[cells, 0] + amp
            t = torch.relu(drive + BG)
            t = (t + nzn).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
            mm[a][k] = X[a][motor_n].mean()
            xm[a][k] = X[a][mech_n].mean()
            xd[a][k] = float(X[a][D74B[0], 0])
            for kk in POOLS_N:
                tr[a][kk][k] = X[a][POOLS_N[kk]].mean()

    for a in ARMS:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        store[f"xd74b_{a}_{seed}"] = xd[a]
        for kk in POOLS_N:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_c)
    store[f"ub_{seed}"] = ub
    log(f"seed {seed} done af {af_c:.5f} | {time.time()-t0:.0f}s")


for s in SEEDS:
    run_seed(s)

np.savez_compressed("l95/raw_l95.npz", g_new=np.float64(G_NEW),
                    amps=np.array(AMPS), union=UNION, d74b=D74B, **store)
log("raw_l95.npz checkpointed BEFORE analysis")

# ---------------- anchors C0A/C0B (enumerated keys only) ----------------
out = dict(g_new=G_NEW)
c0 = {}
A20 = "d74b_2.0"
for s in SEEDS:
    for key in (["mm", "xm", "xd74b"] + [f"{k}" for k in POOLS_N]):
        if key == "xd74b":
            continue
        c0[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_{A20}_{s}"] - z93[f"{key}_d74b_R_20_{s}"]).max())
        c0[f"b_{key}_{s}"] = float(np.abs(
            store[f"{key}_base_{s}"] - z93[f"{key}_base_{s}"]).max())
out["c0_max"] = max(c0.values())
out["c0_detail"] = c0
out["af"] = AF_C
json.dump(out, open("l95/anchors_run.json", "w"), indent=1)
log(f"C0 max|d| {out['c0_max']:.3e} | {time.time()-t0:.0f}s done")
