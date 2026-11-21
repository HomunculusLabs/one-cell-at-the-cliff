"""L93 run: Tr-L volley census on the L92 closure substrate.

PREREG l93/PREREG.md FIRST. Machinery = l92_run.py verbatim (extraction,
two-generator noise law, settle, AMPA schedule); arms = PREREG table.
CPU-only; raw checkpoint BEFORE analysis (L43 rule).
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
VOL0, VOL1 = 0, 2000          # volley window (seg0)
SEEDS = [11, 22, 33]
STATIC92 = json.load(open("l92/static.json"))
STATIC = json.load(open("l93/static.json"))
G_NEW = 0.153125              # l92 stored g_new (pinned)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- extraction (l92_run.py verbatim) ----------------
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

# pools / masks (l92 verbatim)
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
    assert len(POOLS_O[k]) == len(POOLS_N[k]) == STATIC92["pool_sizes"][k], k

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
assert len(mech_o) == len(mech_n) == STATIC92["mech"]

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_o = np.sort(loc_o[dng100_all[keep_old[dng100_all]]])
dng100_n = np.sort(loc_n[dng100_all[keep_new[dng100_all]]])
assert len(dng100_o) == len(dng100_n) == STATIC92["dng100"]

# ---------------- volley arm table (PREREG-pinned) ----------------
INT16 = np.array(sorted(c["loc"] for c in STATIC["int_cand"]), np.int64)
TI16 = np.array(sorted(c["loc"] for c in STATIC["ti_cand"]), np.int64)
V = pd.read_csv("l93/viability.csv")
viable = V[(V.u_max > 0) & (V.x_mean < .95)]
viab_pool = viable["loc"].to_numpy()
# intrinsic cells in the subnet (LOCAL indices) for the random-intrinsic sham
ct_ann = ann.cell_type.fillna("").astype(str).to_numpy()
sup_n = np.full(Nall, "", dtype=object)
sup_n[ann_gi] = sup
int_pool_local = loc_n[gi_new[sup_n[gi_new] == "ventral_nerve_cord_intrinsic"]]
assert len(int_pool_local) > 100
assert np.isin(INT16, int_pool_local).all(), "intr16 not intrinsic"
assert np.isin(TI16, int_pool_local).all(), "tidon not intrinsic"

r1 = np.random.default_rng(9301)
r2 = np.random.default_rng(9302)
r3 = np.random.default_rng(9311)
r4 = np.random.default_rng(9312)
shamdn_a = np.sort(r1.choice(viab_pool, 3, replace=False))
shamdn_b = np.sort(r2.choice(viab_pool, 3, replace=False))
shamint_a = np.sort(r3.choice(int_pool_local, 16, replace=False))
shamint_b = np.sort(r4.choice(int_pool_local, 16, replace=False))

# DN candidate cells (type-side unique in closure subnet, static-pinned locs)
def cand_loc(t_, s_):
    q = V[(V.type == t_) & (V.side == s_)]
    return np.sort(q["loc"].to_numpy()).astype(np.int64)


XL080 = cand_loc("DNxl080", "LEFT")
D74B = cand_loc("DNg74_b", "RIGHT")
D105 = cand_loc("DNg105", "RIGHT")
assert len(XL080) == 1 and len(D74B) == 1 and len(D105) == 1, \
    (len(XL080), len(D74B), len(D105))

VOLLEYS = {                      # arm -> (cells, amp)   [drive += amp, k<2000]
    "base": (None, 0.0),
    "xl080_L_20": (XL080, 2.0),
    "d74b_R_20": (D74B, 2.0),
    "d105_R_20": (D105, 2.0),
    "intr16_05": (INT16, 0.5),
    "intr16_20": (INT16, 2.0),
    "tidon_20": (TI16, 2.0),
    "shamdn_20a": (shamdn_a, 2.0),
    "shamdn_20b": (shamdn_b, 2.0),
    "shamint_20a": (shamint_a, 2.0),
    "shamint_20b": (shamint_b, 2.0),
}
ARMS = list(VOLLEYS)
# write-time checks (L81 rule): disjoint-or-declared cells, amps, window
for a, (cells, amp) in VOLLEYS.items():
    if cells is None:
        continue
    assert 0 < amp <= 2.0 and len(cells) > 0
    assert cells.max() < n_new and cells.min() >= 0
ov = len(set(INT16.tolist()).intersection(set(TI16.tolist())))
assert ov == 6, f"Tr16/Ti16 overlap changed: {ov}"

# schedule (l92 verbatim)
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

log(f"subnet ok n {n_new} arms {len(ARMS)} | volley window [{VOL0},{VOL1}) "
    f"| {time.time()-t0:.0f}s")

# ---------------- rollouts (paired noise, shared settle) ----------------
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
    for _ in range(SETTLE):                     # joint settle (l92 verbatim)
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
    AF_C[seed] = af_c
    X = {a: Xc.clone() for a in ARMS}            # identical post-settle state
    mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
    tr = {a: {k: np.zeros(WIN, np.float32) for k in POOLS_N} for a in ARMS}
    vsum = {a: 0.0 for a in ARMS}
    vn = 0

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
            if sin_t > 0:
                drive[mech_n, 0] = drive[mech_n, 0] + sin_t
            if on and cells is not None:
                drive[cells, 0] = drive[cells, 0] + amp
            t = torch.relu(drive + BG)
            t = (t + nzn).clamp(max=RMAX)
            X[a] = X[a] + (DT / TAU) * (t - X[a])
            if on and cells is not None:
                vsum[a] += float(X[a][cells, 0].mean())
            mm[a][k] = X[a][motor_n].mean()
            xm[a][k] = X[a][mech_n].mean()
            for kk in POOLS_N:
                tr[a][kk][k] = X[a][POOLS_N[kk]].mean()
        if on:
            vn += 1
    for a in ARMS:
        store[f"mm_{a}_{seed}"] = mm[a]
        store[f"xm_{a}_{seed}"] = xm[a]
        for kk in POOLS_N:
            store[f"{kk}_{a}_{seed}"] = tr[a][kk]
        store[f"af_{a}_{seed}"] = np.float32(af_c)
        cells, amp = VOLLEYS[a]
        store[f"vsat_{a}_{seed}"] = np.float32(
            vsum[a] / vn if cells is not None else float("nan"))
    log(f"seed {seed} done af {af_c:.5f} | {time.time()-t0:.0f}s")


for s in SEEDS:
    run_seed(s)

np.savez_compressed("l93/raw_l93.npz", g_new=np.float64(G_NEW),
                    shamdn_a=shamdn_a, shamdn_b=shamdn_b,
                    shamint_a=shamint_a, shamint_b=shamint_b,
                    int16=INT16, ti16=TI16, xl080=XL080, d74b=D74B,
                    d105=D105, **store)
log("raw_l93.npz checkpointed BEFORE analysis")

# ---------------- anchors C0/C1 (enumerated keys only) ----------------
out = dict(g_new=G_NEW)
c0 = {}
for s in SEEDS:
    for key in (["mm", "xm"] + [f"{k}" for k in POOLS_N]):
        c0[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_base_{s}"] - z92[f"{key}_cfn_{s}"][:WIN]).max())
out["c0_max"] = max(c0.values())
out["c0_detail"] = c0
c1 = {}
for s in SEEDS:
    afs = [float(store[f"af_{a}_{s}"]) for a in ARMS]
    c1[f"af_equal_{s}"] = (max(afs) - min(afs)) == 0.0
    c1[f"af_vs_l92_{s}"] = abs(float(store[f"af_base_{s}"])
                               - float(z92[f"af_cfn_{s}"]))
out["c1"] = c1
json.dump(out, open("l93/anchors_run.json", "w"), indent=1)
log(f"C0 max|d| {out['c0_max']:.3e} | C1 af-equal "
    f"{all(v for k, v in c1.items() if 'af_equal' in k)} "
    f"| {time.time()-t0:.0f}s done")
