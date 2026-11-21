"""L91: female BANC endgame multibatch (LANE.md ideas 46). PREREG l91/PREREG.md FIRST.

L90 protocol ported to the female cord: trunk arms (fn/fh x echo on/off) +
donor-sham transport control, 3 batches x 16 fresh seeds + 3 anchor seeds.
Substrate = l78_run.py VERBATIM; batch/resume = l90_multibatch.py form.
Cells + certification live in l91_verdict.py (crash-isolated).
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
G, BETA, D = 0.14, 2.0, 0.2          # L65 arm-B frozen (l68/l78 verbatim)
ENT_AMP = 0.1                        # hyb01
HOP_AMP, HOP_VW = 0.5, 40            # male l59/l90 volley params
TRANS = [2000, 4000]
FB = dict(gfb=.1, delay=5, sign=-1.0)          # male literal cell (l78 fbn_g01)
SIGS = ("fL", "fR", "eL", "eR")
TRUNKS = ["fn", "fn_fb", "fh", "fh_fb"]
ECHO_ARMS = ["fn_fb", "fh_fb"]
HOP_TRUNKS = {"fh", "fh_fb"}
SHAM = "fsham"
ARMS = TRUNKS + [SHAM]
ANCHOR = [11, 22, 33]
B1 = list(range(501, 517))
B2 = list(range(601, 617))
B3 = list(range(701, 717))
PLAN = [("ANCH", ANCHOR), ("B1", B1), ("B2", B2), ("B3", B3)]
DATA = "data"
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


# ---------------- subnet (l78_run.py extraction verbatim) ----------------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()

ann = pd.read_csv(f"{DATA}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv(f"{DATA}/dv_11837016", low_memory=False,
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

conn = pd.read_csv(f"{DATA}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into
assert int(keep.sum()) == 21249, keep.sum()

emask = keep[src_all] & keep[dst_all]
gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
assert len(gsrc) == 627051, len(gsrc)
loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
gsign_a = sign_all[gsrc]
gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
Wb_vals = (np.log1p(gcount) * gsign_b).astype(np.float32)

Wc = torch.sparse_coo_tensor(
    torch.from_numpy(np.vstack([ldst, lsrc])).long(),
    torch.from_numpy(Wb_vals.astype(np.float32)), (n, n)
).coalesce().to_sparse_csr()

# pools per side (l68 verbatim)
mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
in_sub = keep[mgi]

SIDE_MAP = {"L": "left", "R": "right"}


def pool(sel, sd):
    sdl = SIDE_MAP[sd.upper()]
    m = in_sub & sel & (side_m == sdl)
    return loc[mgi[m]]


def has(s, t=ptt):
    return np.array([s in x for x in t])


PAIRS = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"), has("trochanter") & has("extensor")),
]:
    PAIRS[k] = {c: pool(fpat if c[0] == "f" else epat, c[1])
                for c in ("fL", "fR", "eL", "eR")}
    assert all(len(v) > 0 for v in PAIRS[k].values()), (k, PAIRS[k])
assert {k: [len(v) for v in d.values()] for k, d in PAIRS.items()} == \
    {"Ti": [50, 51, 6, 6], "Tr": [31, 31, 24, 24]}, "pool sizes drifted"

sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100 = np.sort(loc[dng100_all[keep[dng100_all]]])
assert len(dng100) == 2, len(dng100)
dn46_all = sub_dn.gi[ct_dn == "DNge046"].to_numpy()
hop46 = np.sort(loc[dn46_all[keep[dn46_all]]])
assert len(hop46) == 1, len(hop46)   # substrate probe: 1 cell, side RIGHT

motor = np.zeros(n, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor[loc[mg[keep[mg]]]] = True

cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech = np.where(mech_mask[keep])[0]
MECH_N = int(mech_mask[keep].sum())
assert MECH_N == 4848, MECH_N

ANTAG = np.concatenate([PAIRS["Tr"][c] for c in SIGS])   # male echo-source form
pools_str = {k: [len(v) for v in d.values()] for k, d in PAIRS.items()}
log(f"subnet {n:,} edges {len(lsrc):,} | mech {MECH_N} | antag {len(ANTAG)} "
    f"| hop46 {len(hop46)} | pools {pools_str} | {time.time()-t0:.0f}s")

# ---------------- schedule: l68 hyb01 AMPA table + male HOPA ----------------
AMPA = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * 900 < seg0 + SEG:
        lo = seg0 + c * 900
        AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP
        c += 1
AMPA[2000:4000] = ENT_AMP
assert (AMPA[:500] == ENT_AMP).all() and (AMPA[500:900] == 0).all()
assert (AMPA[2000:4000] == ENT_AMP).all()
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

# donors: l68 stored hyb01 ANTAG-mean (l66/l78 form)
z68 = np.load("l68/raw_l68.npz")
z78 = np.load("l78/raw_l78.npz")
DON_M = {}
for s in ANCHOR:
    DON_M[s] = ((z68[f"hyb01_s{s}_Tr_fL"] + z68[f"hyb01_s{s}_Tr_fR"]
                 + z68[f"hyb01_s{s}_Tr_eL"] + z68[f"hyb01_s{s}_Tr_eR"])
                / 4.0).astype(np.float32)
NEXT = {11: 22, 22: 33, 33: 11}      # l78 next-seed cyclic (anchor seeds)


def donor_of(seed, bname, seeds):
    if seed in NEXT:
        return DON_M[NEXT[seed]]
    return DON_M[ANCHOR[seeds.index(seed) % 3]]


# ---------------- resume ----------------
store = {}
if os.path.exists("l91/raw_partial.npz"):
    z = np.load("l91/raw_partial.npz")
    store = {k: z[k] for k in z.files}
    n_cached = len({k.rsplit("_", 1)[1] for k in store if k.startswith("mm_")})
    log(f"resume: {n_cached} seeds cached")


def save_partial():
    if store:
        np.savez("l91/raw_partial.npz", **store)


# ---------------- rollouts (l78 step order verbatim + hop/sham) ----------------
for bname, seeds in PLAN:
    for seed in seeds:
        if f"mm_fn_{seed}" in store:
            log(f"{bname} seed {seed} cached, skip")
            continue
        gen = torch.Generator().manual_seed(seed)
        X0 = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
        X = {a: X0.clone() for a in ARMS}
        neg = Wc.values() < 0
        vals = Wc.values().clone()
        vals[neg] *= BETA
        Wb = torch.sparse_csr_tensor(Wc.crow_indices(), Wc.col_indices(), vals,
                                     Wc.shape)
        I = torch.zeros(n, 1)
        I[dng100] = D
        settle_ph = 0.0
        mm = {a: np.zeros(WIN, np.float32) for a in ARMS}
        xm = {a: np.zeros(WIN, np.float32) for a in ARMS}
        mA = {a: np.zeros(WIN, np.float32) for a in ECHO_ARMS}
        tr = {a: {pk: {c: np.zeros(WIN, np.float32) for c in SIGS}
                  for pk in PAIRS} for a in ARMS}
        af = {}
        don = donor_of(seed, bname, seeds)

        def step_all(k):
            global settle_ph
            nz = NOISE * torch.randn(n, 1, generator=gen)
            ph_k = PHI[k] if k >= 0 else settle_ph
            if k < 0:
                settle_ph += 2 * math.pi * 0.7 * DT
            sin_ph = math.sin(ph_k)
            amp_k = ENT_AMP if k < 0 else float(AMPA[k])
            sin_term = amp_k * (0.5 + 0.5 * sin_ph)
            for a in ARMS:
                drive = torch.sparse.mm(Wb, X[a]) * G + I
                if amp_k > 0.0:
                    drive[mech, 0] = drive[mech, 0] + sin_term
                if k >= 0 and HOPA[a][k]:
                    drive[hop46, 0] += HOP_AMP
                if a in ECHO_ARMS and k >= FB["delay"]:
                    drive[mech, 0] += (FB["gfb"] * FB["sign"]
                                       * float(mA[a][k - FB["delay"]]))
                elif a == SHAM and k >= FB["delay"]:
                    drive[mech, 0] += (FB["gfb"] * FB["sign"]
                                       * float(don[k - FB["delay"]]))
                t = torch.relu(drive + BG)
                t = (t + nz).clamp(max=RMAX)
                X[a] = X[a] + (DT / TAU) * (t - X[a])

        for k in range(SETTLE):
            step_all(-1 - k)
        for a in ARMS:
            af[a] = float((X[a] > 0.05).float().mean())
            assert 0.01 < af[a] < 0.9, (a, af[a])
        for i in range(WIN):
            step_all(i)
            for a in ARMS:
                mm[a][i] = X[a][motor].mean()
                xm[a][i] = X[a][mech].mean()
                for pk in PAIRS:
                    for c in SIGS:
                        tr[a][pk][c][i] = X[a][PAIRS[pk][c]].mean()
                if a in ECHO_ARMS:
                    mA[a][i] = X[a][ANTAG].mean()
        for a in ARMS:
            store[f"mm_{a}_{seed}"] = mm[a]
            store[f"xm_{a}_{seed}"] = xm[a]
            for pk in PAIRS:
                for c in SIGS:
                    store[f"{pk}_{c}_{a}_{seed}"] = tr[a][pk][c]
        for a in ECHO_ARMS:
            store[f"mA_{a}_{seed}"] = mA[a]
        store[f"afv_{seed}"] = np.array([af[a] for a in ARMS], np.float32)
        save_partial()
        log(f"{bname} seed {seed} done | {time.time()-t0:.0f}s")

log(f"rollouts done {time.time()-t0:.0f}s")

# ---------------- raw checkpoint (BEFORE any analysis) ----------------
np.savez_compressed(
    "l91/raw_l91.npz",
    **{k: v for k, v in store.items() if not k.startswith("afv_")},
    **{k: v for k, v in store.items() if k.startswith("afv_")})
log("raw_l91.npz checkpointed BEFORE analysis")

# ---------------- anchors (enumerated keys ONLY) ----------------
# C0A: fn == l68 stored hyb01 bit-identical; C0A2: fn_fb == l78 fbn_g01;
#      C0A3: fsham == l78 sham_g01 (same generator + draw order).
c0a, c0a2, c0a3 = {}, {}, {}
for s in ANCHOR:
    c0a[f"fn_mm_{s}"] = float(np.abs(
        store[f"mm_fn_{s}"] - z68[f"hyb01_s{s}_mm"][:WIN]).max())
    c0a2[f"fnfb_mm_{s}"] = float(np.abs(
        store[f"mm_fn_fb_{s}"] - z78[f"mm_fbn_g01_{s}"][:WIN]).max())
    c0a3[f"sham_mm_{s}"] = float(np.abs(
        store[f"mm_fsham_{s}"] - z78[f"mm_sham_g01_{s}"][:WIN]).max())
    for pk in PAIRS:
        for c in SIGS:
            c0a[f"fn_{pk}_{c}_{s}"] = float(np.abs(
                store[f"{pk}_{c}_fn_{s}"] - z68[f"hyb01_s{s}_{pk}_{c}"][:WIN]).max())
            c0a2[f"fnfb_{pk}_{c}_{s}"] = float(np.abs(
                store[f"{pk}_{c}_fn_fb_{s}"]
                - z78[f"{pk}_{c}_fbn_g01_{s}"][:WIN]).max())
            c0a3[f"sham_{pk}_{c}_{s}"] = float(np.abs(
                store[f"{pk}_{c}_fsham_{s}"]
                - z78[f"{pk}_{c}_sham_g01_{s}"][:WIN]).max())
c0a_pass = all(v == 0.0 for v in c0a.values())
c0a2_pass = all(v == 0.0 for v in c0a2.values())
c0a3_pass = all(v == 0.0 for v in c0a3.values())

# C0P: first divergence vs fn (xm/mm), echo+sham law {5,6}; hop window law
c0p = {}
for a in ("fn_fb", "fsham", "fh", "fh_fb"):
    for s in ANCHOR + B1:
        dx = np.abs(store[f"xm_{a}_{s}"] - store[f"xm_fn_{s}"])
        dm = np.abs(store[f"mm_{a}_{s}"] - store[f"mm_fn_{s}"])
        c0p[f"fd_xm_{a}_{s}"] = int(np.argmax(dx > 0)) if (dx > 0).any() else -1
        c0p[f"fd_mm_{a}_{s}"] = int(np.argmax(dm > 0)) if (dm > 0).any() else -1
c0p_echo = all(c0p[f"fd_xm_fn_fb_{s}"] == 5 and c0p[f"fd_mm_fn_fb_{s}"] == 6
               and c0p[f"fd_mm_fsham_{s}"] == 6 for s in ANCHOR + B1)
c0p_hop_mm = [c0p[f"fd_mm_fh_{s}"] for s in ANCHOR + B1]

# C2: every treatment arm actually diverges
c2 = {f"{a}_{s}": float(np.abs(store[f"mm_{a}_{s}"] - store[f"mm_fn_{s}"]).max())
      for a in ("fn_fb", "fh", "fh_fb", "fsham")
      for s in ANCHOR + B1 + B2 + B3 if f"mm_{a}_{s}" in store}
c2_pass = all(v > 0.0 for v in c2.values())

# C1: operating point
c1 = all(0.01 < float(v) < 0.9 for k, v in store.items()
         if k.startswith("afv_") for v in v)

out = dict(c0a_max=max(c0a.values()), c0a_pass=bool(c0a_pass),
           c0a2_max=max(c0a2.values()), c0a2_pass=bool(c0a2_pass),
           c0a3_max=max(c0a3.values()), c0a3_pass=bool(c0a3_pass),
           c0p=c0p, c0p_echo=bool(c0p_echo), c0p_hop_mm=c0p_hop_mm,
           c2_pass=bool(c2_pass), c2_min=min(c2.values()), c1=bool(c1),
           hop46_n=int(len(hop46)), arms=ARMS)
json.dump(out, open("l91/anchors_run.json", "w"), indent=1)
log(f"C0A {c0a_pass} (max {max(c0a.values()):.1e}) | C0A2 {c0a2_pass} "
    f"({max(c0a2.values()):.1e}) | C0A3 {c0a3_pass} ({max(c0a3.values()):.1e}) "
    f"| C0P-echo {c0p_echo} | hop fd_mm {sorted(set(c0p_hop_mm))} | "
    f"C2 {c2_pass} | C1 {c1}")
log(f"done {time.time()-t0:.0f}s -> l91/raw_l91.npz + anchors_run.json")
