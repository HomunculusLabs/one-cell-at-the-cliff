"""L92 run: closure subnet op-point + decomposition arms + DN census.

PREREG l92/PREREG.md FIRST. Extraction verbatim from l92_static.py (asserted
against its pinned static.json). CPU-only; raw checkpoint before analysis.

Generator law (the decomposition instrument): gen(seed) draws ONLY old-cell
shaped tensors — X0 randn(21249,1), then ONE randn(21249,1) per settle+win
step = EXACTLY l91's draw sequence; gen2(seed+9000) draws the 560-cell
stream. oldref (old subnet, single gen) and the closure arms therefore share
a bit-identical old-cell noise stream; if g_new == 0.14 oldref IS the l91 fn
arm bitwise.
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
HOP_AMPS = {"chop50": 0.5, "chop200": 2.0}
HOP_VW = 40
TRANS = [2000, 4000]
SEEDS = [11, 22, 33]
STATIC = json.load(open("l92/static.json"))
AF_TARGET = STATIC["af_target"]
G_OLD = 0.14
t0 = time.time()

def log(*a):
    print(*a, flush=True)

def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]

# ---------------- extraction (l92_static.py verbatim) ----------------
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
assert (n_old, n_new) == (STATIC["n_old"], STATIC["n_new"]), (n_old, n_new)

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
assert Wc_old.values().numel() == STATIC["edges_old"]
assert Wc_new.values().numel() == STATIC["edges_new"]

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
assert n_add == STATIC["dn_new"], (n_add, STATIC["dn_new"])
old_pos_in_new = loc_n[gi_old]          # old local i -> new local index
new_pos = loc_n[new_g]
assert sorted(new_pos.tolist()) == sorted(
    (set(range(n_new)) - set(old_pos_in_new.tolist())))
assert len(old_pos_in_new) == n_old

# pools / masks in both spaces (global-id identity)
mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}

def has(s):
    return np.array([s in x for x in ptt])

POOLS_O, POOLS_N = {}, {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor")),
]:
    for c in ("fL", "fR", "eL", "eR"):
        sel = fpat if c[0] == "f" else epat
        m_o = keep_old[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
        m_n = keep_new[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
        POOLS_O[f"{k}_{c}"] = np.sort(loc_o[mgi[m_o]])
        POOLS_N[f"{k}_{c}"] = np.sort(loc_n[mgi[m_n]])
for k in POOLS_O:
    assert len(POOLS_O[k]) == len(POOLS_N[k]) == STATIC["pool_sizes"][k], k

motor_o = np.zeros(n_old, bool)
motor_n = np.zeros(n_new, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor_o[loc_o[mg[keep_old[mg]]]] = True
motor_n[loc_n[mg[keep_new[mg]]]] = True
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech_o = np.where(mech_mask[keep_old])[0]
mech_n = np.where(mech_mask[keep_new])[0]
assert len(mech_o) == len(mech_n) == STATIC["mech"]

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_o = np.sort(loc_o[dng100_all[keep_old[dng100_all]]])
dng100_n = np.sort(loc_n[dng100_all[keep_new[dng100_all]]])
assert len(dng100_o) == len(dng100_n) == STATIC["dng100"]
dn46_all = sub_dn.gi[ct_dn == "DNge046"].to_numpy()
assert list(np.sort(loc_n[dn46_all[keep_new[dn46_all]]])) == STATIC["dn46_pos"]
hop46n = np.sort(loc_n[new_g[np.isin(new_g, dn46_all)]])   # DNn DNge046 only
assert list(hop46n) == [270, 366], hop46n

dn_pos_n = np.sort(loc_n[gi_new[dn_all[gi_new]]])
n_dn = len(dn_pos_n)
assert n_dn == STATIC["dn_census_n"], (n_dn, STATIC["dn_census_n"])
log(f"subnets old {n_old}/{STATIC['edges_old']} new {n_new}/"
    f"{STATIC['edges_new']} | dn {n_dn} | hop46n {list(hop46n)} "
    f"| {time.time()-t0:.0f}s")

# ---------------- schedule (l91 verbatim) ----------------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
assert int((AMPA > 0).sum()) + SETTLE == 4800
HOPA = np.zeros(WIN, bool)
for o in TRANS:
    HOPA[o:o + HOP_VW] = True
assert HOPA.sum() == 2 * HOP_VW
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# ---------------- P1 bisect (closure settle-only) ----------------
def closure_af(seed, g):
    gen = torch.Generator().manual_seed(seed)
    gen2 = torch.Generator().manual_seed(seed + 9000)
    X = torch.zeros(n_new, 1)
    X[old_pos_in_new] = (BG + NOISE
                         * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
    X[new_pos] = (BG + NOISE
                  * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
    I = torch.zeros(n_new, 1)
    I[dng100_n] = D
    sp = 0.0
    for _ in range(SETTLE):
        nz = torch.zeros(n_new, 1)
        nz[old_pos_in_new] = NOISE * torch.randn(n_old, 1, generator=gen)
        nz[new_pos] = NOISE * torch.randn(n_add, 1, generator=gen2)
        sp += 2 * math.pi * 0.7 * DT
        drive = torch.sparse.mm(Wb_new, X) * g + I
        drive[mech_n, 0] = drive[mech_n, 0] + \
            ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        t = torch.relu(drive + BG)
        X = X + (DT / TAU) * ((t + nz).clamp(max=RMAX) - X)
    return float((X > 0.05).float().mean())

def af_mean(g):
    return float(np.mean([closure_af(s, g) for s in SEEDS]))

lo_g, hi_g = 0.05, 0.60
af_lo, af_hi = af_mean(lo_g), af_mean(hi_g)
log(f"bisect bracket af({lo_g})={af_lo:.5f} af({hi_g})={af_hi:.5f} "
    f"target {AF_TARGET:.5f}")
assert af_lo < AF_TARGET < af_hi, "bracket failed"
g_new = lo_g
for it in range(14):
    mid = 0.5 * (lo_g + hi_g)
    af_m = af_mean(mid)
    log(f"  bisect it{it} g={mid:.6f} af={af_m:.5f}")
    if abs(af_m - AF_TARGET) <= 1e-3:
        g_new = mid
        break
    if af_m < AF_TARGET:
        lo_g = mid
    else:
        hi_g = mid
    g_new = mid
af_final = af_mean(g_new)
log(f"g_new {g_new:.6f} (old {G_OLD}) af {af_final:.5f} "
    f"target {AF_TARGET:.5f} | {time.time()-t0:.0f}s")

# ---------------- main arms (joint settle, shared noise) ----------------
ARMS = ["oldref", "cfn", "chop50", "chop200"]
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
    for _ in range(SETTLE):                     # joint settle, one draw set
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sp += 2 * math.pi * 0.7 * DT
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))
        drive = torch.sparse.mm(Wb_old, Xo) * g_new + Io
        drive[mech_o, 0] = drive[mech_o, 0] + sin_t
        Xo = Xo + (DT / TAU) * ((torch.relu(drive + BG) + nz_o)
                                .clamp(max=RMAX) - Xo)
        drive = torch.sparse.mm(Wb_new, Xc) * g_new + In
        drive[mech_n, 0] = drive[mech_n, 0] + sin_t
        Xc = Xc + (DT / TAU) * ((torch.relu(drive + BG) + nzn)
                                .clamp(max=RMAX) - Xc)
    af_o = float((Xo > 0.05).float().mean())
    af_c = float((Xc > 0.05).float().mean())
    assert 0.01 < af_o < 0.9 and 0.01 < af_c < 0.9, (af_o, af_c)
    AF_C[seed] = af_c
    X = {"oldref": Xo, "cfn": Xc.clone(),
         "chop50": Xc.clone(), "chop200": Xc.clone()}
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {k: np.zeros(WIN, np.float32) for k in POOLS_N} for a in ARMS}
    cen = dict(u_max=np.full(n_dn, -1e30, np.float32),
               u_sum=np.zeros(n_dn, np.float32),
               x_sum=np.zeros(n_dn, np.float32), n=0)

    for k in range(WIN):
        nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
        nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
        nzn = torch.zeros(n_new, 1)
        nzn[old_pos_in_new] = nz_o
        nzn[new_pos] = nz_a
        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
        hop = bool(HOPA[k])
        for a in ARMS:
            if a == "oldref":
                drive = torch.sparse.mm(Wb_old, X[a]) * g_new + Io
                if sin_t > 0:
                    drive[mech_o, 0] = drive[mech_o, 0] + sin_t
                t = torch.relu(drive + BG)
                X[a] = X[a] + (DT / TAU) * ((t + nz_o).clamp(max=RMAX) - X[a])
                continue
            drive = torch.sparse.mm(Wb_new, X[a]) * g_new + In
            if sin_t > 0:
                drive[mech_n, 0] = drive[mech_n, 0] + sin_t
            if hop and a in HOP_AMPS:
                drive[hop46n, 0] = drive[hop46n, 0] + HOP_AMPS[a]
            if a == "cfn" and k < 2000:
                u = (drive + BG)[dn_pos_n, 0].numpy()
                np.maximum(cen["u_max"], u, out=cen["u_max"])
                cen["u_sum"] += u
                cen["x_sum"] += X[a][dn_pos_n, 0].numpy()
                cen["n"] += 1
            t = torch.relu(drive + BG)
            t = (t + nzn).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
        for a in ARMS:
            ps = POOLS_O if a == "oldref" else POOLS_N
            ms = motor_o if a == "oldref" else motor_n
            xs = mech_o if a == "oldref" else mech_n
            mm[a][k] = X[a][ms].mean()
            xm[a][k] = X[a][xs].mean()
            for kk in ps:
                tr[a][kk][k] = X[a][ps[kk]].mean()
    for a in ARMS:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        for kk in POOLS_N:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_o if a == "oldref" else af_c)
    store[f"cen_u_max_{seed}"] = cen["u_max"]
    store[f"cen_u_mean_{seed}"] = cen["u_sum"] / max(cen["n"], 1)
    store[f"cen_x_mean_{seed}"] = cen["x_sum"] / max(cen["n"], 1)
    log(f"seed {seed} done af old {af_o:.4f} new {af_c:.4f} "
        f"| {time.time()-t0:.0f}s")

for s in SEEDS:
    run_seed(s)

# bisect consistency: the 3-seed MEAN of the main-run af must equal af_final
af_c_mean = float(np.mean([AF_C[s] for s in SEEDS]))
assert abs(af_c_mean - af_final) < 1e-9, (af_c_mean, af_final)
log(f"bisect consistency OK: mean af_c {af_c_mean:.5f} == af_final")

np.savez_compressed("l92/raw_l92.npz", g_new=np.float64(g_new),
                    af_target=np.float64(AF_TARGET), **store)
log("raw_l92.npz checkpointed BEFORE analysis")

# ---------------- anchors (enumerated keys only) ----------------
z91 = np.load("l91/raw_l91.npz")
out = dict(g_new=g_new, g_old=G_OLD, af_final=af_final, af_target=AF_TARGET,
           n_old=n_old, n_new=n_new)

c0a = {}
for s in SEEDS:
    c0a[f"mm_{s}"] = float(np.abs(store[f"mm_oldref_{s}"]
                                   - z91[f"mm_fn_{s}"][:WIN]).max())
    c0a[f"xm_{s}"] = float(np.abs(store[f"xm_oldref_{s}"]
                                   - z91[f"xm_fn_{s}"][:WIN]).max())
    for kk in POOLS_N:
        c0a[f"{kk}_{s}"] = float(np.abs(store[f"{kk}_oldref_{s}"]
                                        - z91[f"{kk}_fn_{s}"][:WIN]).max())
out["c0a_branch"] = "bit" if g_new == G_OLD else "gain-decomp"
out["c0a_max"] = max(c0a.values())
out["c0a_detail"] = c0a

c0c = {}
for s in SEEDS:
    c0c[f"mm_{s}"] = float(np.abs(store[f"mm_cfn_{s}"]
                                   - store[f"mm_oldref_{s}"]).max())
    for kk in POOLS_N:
        c0c[f"{kk}_{s}"] = float(np.abs(store[f"{kk}_cfn_{s}"]
                                        - store[f"{kk}_oldref_{s}"]).max())
out["c0c_max"] = max(c0c.values())
out["c0c_detail"] = c0c

c2 = {}
for a in ("chop50", "chop200"):
    for s in SEEDS:
        dm = np.abs(store[f"mm_{a}_{s}"] - store[f"mm_cfn_{s}"])
        dx = np.abs(store[f"xm_{a}_{s}"] - store[f"xm_cfn_{s}"])
        c2[f"dm_{a}_{s}"] = float(dm.max())
        c2[f"fd_mm_{a}_{s}"] = int(np.argmax(dm > 0)) if (dm > 0).any() else -1
        c2[f"fd_xm_{a}_{s}"] = int(np.argmax(dx > 0)) if (dx > 0).any() else -1
        for kk in POOLS_N:
            c2[f"dpool_{a}_{kk}_{s}"] = float(np.abs(
                store[f"{kk}_{a}_{s}"] - store[f"{kk}_cfn_{s}"]).max())
out["c2_detail"] = c2
out["c2_lands_50"] = int(sum(c2[f"dm_chop50_{s}"] > 0 for s in SEEDS))
out["c2_lands_200"] = int(sum(c2[f"dm_chop200_{s}"] > 0 for s in SEEDS))
fds = [c2[f"fd_mm_{a}_{s}"] for a in ("chop50", "chop200") for s in SEEDS]
out["fd_min"] = int(min(fds))

af_cfn = float(np.mean([store[f"af_cfn_{s}"] for s in SEEDS]))
out["af_cfn_mean"] = af_cfn
out["c1"] = bool(all(0.01 < float(store[f"af_{a}_{s}"]) < 0.9
                     for a in ARMS for s in SEEDS)
                 and abs(af_cfn - AF_TARGET) <= 2e-3)
json.dump(out, open("l92/anchors_run.json", "w"), indent=1)
log(f"C0A branch {out['c0a_branch']} max {out['c0a_max']:.3e} | "
    f"C0C max {out['c0c_max']:.3e} | C2 lands .5:{out['c2_lands_50']}/3 "
    f"2.0:{out['c2_lands_200']}/3 | fd_min {out['fd_min']} | C1 {out['c1']}")
log(f"done {time.time()-t0:.0f}s -> l92/raw_l92.npz + anchors_run.json")
