"""L94 run: L91 multibatch protocol on the L92 CLOSURE substrate.

PREREG l94/PREREG.md FIRST. Machinery = l93_run.py verbatim (extraction,
two-generator noise law, joint settle, AMPA schedule); arms = L91 trunk
port (cfn/cfn_fb/csham/cfh/cfh_fb; hop target = ALL 3 in-subnet DNge046).
CPU-only; raw checkpoint BEFORE analysis (L43 rule); resume-safe.
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
SEG = 2000
BETA, D = 2.0, 0.2
ENT_AMP = 0.1
G_NEW = 0.153125              # l92 stored g_new (pinned)
HOP_AMP, HOP_VW = 0.5, 40     # male l59/l90 trunk volley params
TRANS = [2000, 4000]
FB = dict(gfb=.1, delay=5, sign=-1.0)          # male literal cell (l78/l91)
SIGS = ("fL", "fR", "eL", "eR")
ARMS = ["cfn", "cfn_fb", "csham", "cfh", "cfh_fb"]
ECHO_ARMS = ["cfn_fb", "cfh_fb"]
HOP_TRUNKS = {"cfh", "cfh_fb"}
SHAM = "csham"
ANCHOR = [11, 22, 33]
B4 = list(range(801, 817))
B5 = list(range(901, 917))
B6 = list(range(1001, 1017))
PLAN = [("ANCH", ANCHOR), ("B4", B4), ("B5", B5), ("B6", B6)]
ALLFRESH = B4 + B5 + B6
STATIC92 = json.load(open("l92/static.json"))
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

# pools / masks (l93 verbatim)
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
mech_o = np.where(mech_mask[keep_old])[0]
assert len(mech_n) == STATIC92["mech"]

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_n = np.sort(loc_n[dng100_all[keep_new[dng100_all]]])
assert len(dng100_n) == STATIC92["dng100"]

# hop target: ALL in-subnet DNge046 (PREREG-pinned [270, 302, 366])
dn46_all = sub_dn.gi[ct_dn == "DNge046"].to_numpy()
hop46 = np.sort(loc_n[dn46_all[keep_new[dn46_all]]]).astype(np.int64)
assert list(hop46) == STATIC92["dn46_pos"], hop46

ANTAG = np.concatenate([POOLS_N[f"Tr_{c}"] for c in SIGS])  # echo source
log(f"subnet {n_new:,} edges {Wc_new.values().numel():,} | mech {len(mech_n)} "
    f"| antag {len(ANTAG)} | hop46 {list(hop46)} | {time.time()-t0:.0f}s")

# ---------------- schedule (l91/l93 verbatim) ----------------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
assert int((AMPA > 0).sum()) + SETTLE == 4800
HOPA = {a: np.zeros(WIN, bool) for a in ARMS}
for o in TRANS:
    for a in HOP_TRUNKS:
        HOPA[a][o:o + HOP_VW] = True
assert all(HOPA[a].sum() == (2 * HOP_VW if a in HOP_TRUNKS else 0) for a in ARMS)
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph

# donors: l68 stored hyb01 ANTAG-mean (l91 verbatim)
z68 = np.load("l68/raw_l68.npz")
z93 = np.load("l93/raw_l93.npz")
DON_M = {}
for s in ANCHOR:
    DON_M[s] = ((z68[f"hyb01_s{s}_Tr_fL"] + z68[f"hyb01_s{s}_Tr_fR"]
                 + z68[f"hyb01_s{s}_Tr_eL"] + z68[f"hyb01_s{s}_Tr_eR"])
                / 4.0).astype(np.float32)
NEXT = {11: 22, 22: 33, 33: 11}


def donor_of(seed, seeds):
    if seed in NEXT:
        return DON_M[NEXT[seed]]
    return DON_M[ANCHOR[seeds.index(seed) % 3]]


# ---------------- resume ----------------
store = {}
if os.path.exists("l94/raw_partial.npz"):
    z = np.load("l94/raw_partial.npz")
    store = {k: z[k] for k in z.files}
    log(f"resume: {len({k.split('_')[-1] for k in store if k.startswith('mm_')})} "
        f"seeds cached")


def save_partial():
    if store:
        np.savez("l94/raw_partial.npz", **store)


# ---------------- rollouts (l93 step form + l91 trunk drives) ----------------
for bname, seeds in PLAN:
    for seed in seeds:
        if f"mm_cfn_{seed}" in store:
            log(f"{bname} seed {seed} cached, skip")
            continue
        gen = torch.Generator().manual_seed(seed)
        gen2 = torch.Generator().manual_seed(seed + 9000)
        X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen)).clamp(0, 1)
        X0n = (BG + NOISE * torch.randn(n_add, 1, generator=gen2)).clamp(0, 1)
        Io = torch.zeros(n_old, 1)
        dng100_o = np.sort(loc_o[dng100_all[keep_old[dng100_all]]])
        Io[dng100_o] = D
        In = torch.zeros(n_new, 1)
        In[dng100_n] = D
        Xc = torch.zeros(n_new, 1)
        Xc[old_pos_in_new] = X0o
        Xc[new_pos] = X0n
        Xo = X0o.clone()
        sp = 0.0
        for _ in range(SETTLE):                 # joint settle (l93 verbatim)
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
        X = {a: Xc.clone() for a in ARMS}
        mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
        xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
        mA = {a: np.zeros(WIN, np.float32) for a in ECHO_ARMS}
        tr = {a: {kk: np.zeros(WIN, np.float32) for kk in POOLS_N} for a in ARMS}
        don = donor_of(seed, seeds)

        for k in range(WIN):
            nz_o = NOISE * torch.randn(n_old, 1, generator=gen)
            nz_a = NOISE * torch.randn(n_add, 1, generator=gen2)
            nzn = torch.zeros(n_new, 1)
            nzn[old_pos_in_new] = nz_o
            nzn[new_pos] = nz_a
            sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0
            for a in ARMS:
                drive = torch.sparse.mm(Wb_new, X[a]) * G_NEW + In
                if sin_t > 0:
                    drive[mech_n, 0] = drive[mech_n, 0] + sin_t
                if HOPA[a][k]:
                    drive[hop46, 0] += HOP_AMP
                if a in ECHO_ARMS and k >= FB["delay"]:
                    drive[mech_n, 0] += (FB["gfb"] * FB["sign"]
                                         * float(mA[a][k - FB["delay"]]))
                elif a == SHAM and k >= FB["delay"]:
                    drive[mech_n, 0] += (FB["gfb"] * FB["sign"]
                                         * float(don[k - FB["delay"]]))
                t = torch.relu(drive + BG)
                t = (t + nzn).clamp(max=RMAX)
                X[a] = X[a] + (DT / TAU) * (t - X[a])
            for a in ARMS:
                mm[a][k] = X[a][motor_n].mean()
                xm[a][k] = X[a][mech_n].mean()
                for kk in POOLS_N:
                    tr[a][kk][k] = X[a][POOLS_N[kk]].mean()
                if a in ECHO_ARMS:
                    mA[a][k] = X[a][ANTAG].mean()
        for a in ARMS:
            store[f"mm_{a}_{seed}"] = mm[a]
            store[f"xm_{a}_{seed}"] = xm[a]
            for kk in POOLS_N:
                store[f"{kk}_{a}_{seed}"] = tr[a][kk]
            store[f"af_{a}_{seed}"] = np.float32(af_c)
        for a in ECHO_ARMS:
            store[f"mA_{a}_{seed}"] = mA[a]
        save_partial()
        log(f"{bname} seed {seed} done af {af_c:.5f} | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")

# ---------------- raw checkpoint (BEFORE any analysis) ----------------
np.savez_compressed("l94/raw_l94.npz", g_new=np.float64(G_NEW),
                    hop46=hop46, batches=np.array(B4 + B5 + B6), **store)
log("raw_l94.npz checkpointed BEFORE analysis")

# ---------------- anchors (enumerated keys ONLY) ----------------
out = dict(g_new=G_NEW, hop46=[int(v) for v in hop46])

# C0A: cfn == l93 base bit-identical (mm, xm, 8 pools) x 3 anchor seeds
c0a = {}
for s in ANCHOR:
    for key in (["mm", "xm"] + list(POOLS_N)):
        c0a[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_cfn_{s}"] - z93[f"{key}_base_{s}"][:WIN]).max())
out["c0a_max"] = max(c0a.values())
out["c0a_pass"] = bool(all(v == 0.0 for v in c0a.values()))
out["c0a_detail"] = c0a

# C0P-1 echo law: fd_xm==5 / fd_mm==6 vs cfn (echo arms + sham), all seeds
c0p = {}
for a in ("cfn_fb", "csham", "cfh", "cfh_fb"):
    for s in ANCHOR + ALLFRESH:
        dx = np.abs(store[f"xm_{a}_{s}"] - store[f"xm_cfn_{s}"])
        dm = np.abs(store[f"mm_{a}_{s}"] - store[f"mm_cfn_{s}"])
        c0p[f"fd_xm_{a}_{s}"] = int(np.argmax(dx > 0)) if (dx > 0).any() else -1
        c0p[f"fd_mm_{a}_{s}"] = int(np.argmax(dm > 0)) if (dm > 0).any() else -1
fd_echo = all(c0p[f"fd_xm_cfn_fb_{s}"] == 5 and c0p[f"fd_mm_cfn_fb_{s}"] == 6
              and c0p[f"fd_mm_csham_{s}"] == 6 for s in ANCHOR + ALLFRESH)
fd_hop = [c0p[f"fd_mm_cfh_{s}"] for s in ANCHOR + ALLFRESH]
fd_hopfb = [c0p[f"fd_mm_cfh_fb_{s}"] for s in ANCHOR + ALLFRESH]
out["c0p"] = c0p
out["fd_echo_law"] = bool(fd_echo)
out["fd_hop_mm"] = sorted(set(fd_hop))
out["fd_hopfb_mm"] = sorted(set(fd_hopfb))

# C2: every treatment arm diverges vs cfn
c2 = {f"{a}_{s}": float(np.abs(store[f"mm_{a}_{s}"] - store[f"mm_cfn_{s}"]).max())
      for a in ("cfn_fb", "csham", "cfh", "cfh_fb")
      for s in ANCHOR + ALLFRESH}
out["c2_pass"] = bool(all(v > 0.0 for v in c2.values()))
out["c2_min"] = min(c2.values())

# C1: af equal across arms and in range
c1_equal = all(float(store[f"af_{a}_{s}"]) == float(store[f"af_cfn_{s}"])
               for a in ARMS for s in ANCHOR + ALLFRESH)
c1_range = all(0.01 < float(store[f"af_{a}_{s}"]) < 0.9
               for a in ARMS for s in ANCHOR + ALLFRESH)
out["c1"] = bool(c1_equal and c1_range)
out["af_anchor"] = {str(s): float(store[f"af_cfn_{s}"]) for s in ANCHOR}

json.dump(out, open("l94/anchors_run.json", "w"), indent=1)
log(f"C0A {out['c0a_pass']} (max {out['c0a_max']:.1e}) | fd_echo {fd_echo} "
    f"| fd_hop {out['fd_hop_mm']} | fd_hopfb {out['fd_hopfb_mm']} | "
    f"C2 {out['c2_pass']} (min {out['c2_min']:.1e}) | C1 {out['c1']}")
log(f"done {time.time()-t0:.0f}s -> l94/raw_l94.npz + anchors_run.json")
