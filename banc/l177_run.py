"""L177 stage (b) — the af-matched beta ladder, arm B, BANC female cord.

Executes l177/PREREG.md section 2-3 exactly. Build block + run() copied verbatim
from l65_banc_oppoint.py (certified bit-identical this tick by l177_cert.py:
C0S-177 13/13, C0A-177 max|d| 0.0 over 15 traces, stored S/af exact 3/3).

Rungs beta {1.0,1.5,2.0,3.0,4.0}; fresh af-matched bisect per rung to l65's
frozen arm-B af; 16 paired seeds (batch B41 = 3601-3616, fresh); 60 s window;
per-SIDE decomposition; d=0 bit-identity arm per rung; u/X viability census.
Writes l177/rung_b*.npz + l177/ladder.json. No live changes, no draft edits.
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU, DT, RMAX = 0.05, 0.01, 1.0
BG, NOISE = 0.02, 0.01
SETTLE = 400
CONF_WIN = 6000
BETAS = [1.0, 1.5, 2.0, 3.0, 4.0]
SEEDS = list(range(3601, 3617))          # batch B41, 16 seeds, fresh
D_ON, D_OFF = 0.2, 0.0
D = "/home/t3rpz/critters/peabrain-lab/banc/data"
os.makedirs("l177", exist_ok=True)
t0 = time.time()


def log(*a):
    print(*a, flush=True)


assert len(SEEDS) == 16 and SEEDS[0] == 3601 and SEEDS[-1] == 3616, "seed batch pin"

# ---------------- build (l65 verbatim) ------------------------------------
G = torch.load("banc_graph.pt", weights_only=False)
ids_all = G["ids"].numpy().astype(np.uint64)
Nall = int(G["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = G["sign"].numpy()

ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

nt = pd.read_csv(f"{D}/dv_11837016", low_memory=False,
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

conn = pd.read_csv(f"{D}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
pre = np.array([int(a) for a, _ in g_grp.index], np.int64)
post = np.array([int(b) for _, b in g_grp.index], np.int64)
src_all = np.array([idx_all[r] for r in pre], np.int64)
dst_all = np.array([idx_all[r] for r in post], np.int64)
w_syn = g_grp.to_numpy(np.float64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into
emask = keep[src_all] & keep[dst_all]
gsrc, gdst = src_all[emask], dst_all[emask]
gcount = w_syn[emask]
loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]
gsign_a = sign_all[gsrc]
gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
Wb_vals = (np.log1p(gcount) * gsign_b).astype(np.float32)

mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
mside = mot_rows.side.fillna("").astype(str).to_numpy()
mgi = mot_rows.gi.to_numpy()
in_sub = keep[mgi]


def pool(sel):
    return loc[mgi[in_sub & sel]]


def has(s):
    return np.array([s in t for t in ptt])


PAIRS, SIDEP = {}, {}
for k, fpat, epat in [
    ("Ti", (has("tibia") & has("flexor")), (has("tibia") & has("extensor"))),
    ("Tr", (has("trochanter") & has("flexor")), (has("trochanter") & has("extensor"))),
]:
    PAIRS[k] = (pool(fpat), pool(epat))
    for sd in ("L", "R"):
        sm = mside == ("left" if sd == "L" else "right")
        SIDEP[f"{k}_{sd}"] = (pool(fpat & sm), pool(epat & sm))

sub_dn = ann[ann.super_class == "descending"]
dng100_all = sub_dn.gi[sub_dn.cell_type.fillna("").astype(str)
                        .to_numpy() == "DNg100"].to_numpy()
dng100 = np.sort(loc[dng100_all[keep[dng100_all]]])
motor = np.zeros(n, bool)
mg = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor[loc[mg[keep[mg]]]] = True


def build_W(dst, src, vals):
    t = torch.sparse_coo_tensor(
        torch.from_numpy(np.vstack([dst, src])).long(),
        torch.from_numpy(vals.astype(np.float32)), (n, n))
    return t.coalesce().to_sparse_csr()


Wb = build_W(ldst, lsrc, Wb_vals)
stored = json.load(open("l65/results_l65.json"))
sB = stored["arms"]["B"]
AF_TARGET = sB["frozen"]["af"]
C0S = dict(n=n == stored["subnet"]["n"], edges=len(lsrc) == stored["subnet"]["edges"],
           Ti=[len(PAIRS["Ti"][0]), len(PAIRS["Ti"][1])] == stored["pools"]["Ti"],
           Tr=[len(PAIRS["Tr"][0]), len(PAIRS["Tr"][1])] == stored["pools"]["Tr"],
           dng100=len(dng100) == 2)
assert all(C0S.values()), f"C0S {C0S}"
log(f"build OK n {n:,} edges {len(lsrc):,} | af target {AF_TARGET:.5f} | "
    f"sides " + " ".join(f"{k} {len(v[0])}/{len(v[1])}" for k, v in SIDEP.items())
    + f" | {time.time()-t0:.0f}s")


# ---------------- rollout (l65 run() + per-side + census) ------------------
def mk_wbeta(beta):
    vals = Wb.values().clone()
    vals[Wb.values() < 0] *= beta
    return torch.sparse_csr_tensor(Wb.crow_indices(), Wb.col_indices(), vals,
                                   Wb.shape)


def rollout(Wbeta, g, d, seed, win, census=False):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    I = torch.zeros(n, 1)
    I[dng100] = d
    Z = torch.zeros(n, 1)

    def step(cur, drive_I):
        drive = torch.sparse.mm(Wbeta, cur) * g + drive_I
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        return cur + (DT / TAU) * (t - cur)

    for _ in range(SETTLE):
        X = step(X, Z)
    af = float((X > 0.05).float().mean())
    assert not torch.isnan(X).any(), "NaN"
    cen = None
    if census:
        u = (torch.sparse.mm(Wbeta, X) * g + I).squeeze(1).numpy()
        Xn = X.squeeze(1).numpy()
        cen = {}
        for pk, (f, e) in SIDEP.items():
            for nm, idxs in ((f"{pk}_f", f), (f"{pk}_e", e)):
                cen[nm] = dict(u_max=float(u[idxs].max()),
                               u_mean=float(u[idxs].mean()),
                               mean_X=float(Xn[idxs].mean()))
    T = win
    tr = {k: (np.zeros(T, np.float32), np.zeros(T, np.float32)) for k in PAIRS}
    trs = {k: (np.zeros(T, np.float32), np.zeros(T, np.float32)) for k in SIDEP}
    mm = np.zeros(T, np.float32)
    for k in range(T):
        X = step(X, I)
        for pk, (f, e) in PAIRS.items():
            tr[pk][0][k] = X[f].mean()
            tr[pk][1][k] = X[e].mean()
        for pk, (f, e) in SIDEP.items():
            trs[pk][0][k] = X[f].mean()
            trs[pk][1][k] = X[e].mean()
        mm[k] = X[motor].mean()
    return af, tr, trs, mm, cen


def S_of(a, b):
    sl = slice(int(0.25 * len(a)), len(a))
    a, b = a[sl], b[sl]
    if a.std() <= 1e-6 or b.std() <= 1e-6:
        return float("nan"), float(max(np.ptp(a), np.ptp(b)))
    return float(-np.corrcoef(a, b)[0, 1]), float(max(np.ptp(a), np.ptp(b)))


def af_only(Wbeta, g, seed=11):
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(n, 1, generator=gen)).clamp(0, 1)
    Z = torch.zeros(n, 1)
    for _ in range(SETTLE):
        drive = torch.sparse.mm(Wbeta, X) * g + Z
        t = torch.relu(drive + BG)
        t = (t + NOISE * torch.randn(n, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / TAU) * (t - X)
    return float((X > 0.05).float().mean())


# ---------------- the ladder ----------------------------------------------
out = {"prereg": "l177/PREREG.md", "seeds": SEEDS, "af_target": AF_TARGET,
       "betas": BETAS, "rungs": {}}
for beta in BETAS:
    Wbeta = mk_wbeta(beta)
    lo, hi, g, af = 1e-4, 1e2, None, None
    for it in range(40):
        g = float(np.sqrt(lo * hi))
        af = af_only(Wbeta, g)
        if abs(af - AF_TARGET) <= 2e-3:
            break
        if af < AF_TARGET:
            lo = g
        else:
            hi = g
    log(f"beta {beta}: bisect g {g:.6g} af {af:.5f} "
        f"(|d| {abs(af-AF_TARGET):.2e}, {it+1} its) | {time.time()-t0:.0f}s")
    rung = dict(g=g, af_bisect=af, af_resid=abs(af - AF_TARGET), its=it + 1,
                seeds={}, census=None)
    npz = {}
    for s in SEEDS:
        af_on, tr, trs, mm, cen = rollout(Wbeta, g, D_ON, s, CONF_WIN,
                                          census=(s == SEEDS[0]))
        af_off, tr0, trs0, mm0, _ = rollout(Wbeta, g, D_OFF, s, CONF_WIN)
        if cen is not None:
            rung["census"] = cen
        rec = dict(af=af_on, af_d0=af_off,
                   d0_maxd=float(max(np.max(np.abs(trs[k][i] - trs0[k][i]))
                                     for k in SIDEP for i in (0, 1))),
                   op_ok=bool(abs(af_on - AF_TARGET) < 0.02))
        for pk in PAIRS:
            rec[f"S_{pk}"], rec[f"d_{pk}"] = S_of(tr[pk][0], tr[pk][1])
        for pk in SIDEP:
            rec[f"S_{pk}"], rec[f"d_{pk}"] = S_of(trs[pk][0], trs[pk][1])
        rung["seeds"][str(s)] = rec
        for pk in SIDEP:
            npz[f"b{beta}_s{s}_{pk}_f"] = trs[pk][0]
            npz[f"b{beta}_s{s}_{pk}_e"] = trs[pk][1]
        for pk in PAIRS:
            npz[f"b{beta}_s{s}_{pk}_f"] = tr[pk][0]
            npz[f"b{beta}_s{s}_{pk}_e"] = tr[pk][1]
        npz[f"b{beta}_s{s}_mm"] = mm
    np.savez_compressed(f"l177/rung_b{beta}.npz", **npz)
    agg = {k: float(np.nanmean([rung["seeds"][str(s)][f"S_{k}"] for s in SEEDS]))
           for k in list(PAIRS) + list(SIDEP)}
    rung["S_mean"] = agg
    rung["d0_bit_identical"] = bool(all(rung["seeds"][str(s)]["d0_maxd"] == 0.0
                                        for s in SEEDS))
    rung["op_ok_all"] = bool(all(rung["seeds"][str(s)]["op_ok"] for s in SEEDS))
    out["rungs"][str(beta)] = rung
    log(f"  beta {beta}: S {{" + " ".join(f"{k} {agg[k]:+.3f}" for k in
        ["Ti", "Tr", "Ti_L", "Ti_R", "Tr_L", "Tr_R"]) + "} "
        f"| d0_bitid {rung['d0_bit_identical']} op_ok {rung['op_ok_all']} "
        f"| {time.time()-t0:.0f}s")
    json.dump(out, open("l177/ladder.json", "w"), indent=1)

# ---------------- registered verdicts (PREREG section 3) -------------------
S = {k: [out["rungs"][str(b)]["S_mean"][k] for b in BETAS]
     for k in list(PAIRS) + list(SIDEP)}
steps = np.diff(S["Ti"])
P1 = bool(np.all(steps >= 0))
sides = ["Ti_L", "Ti_R", "Tr_L", "Tr_R"]
argm = {k: BETAS[int(np.nanargmax(S[k]))] for k in sides}
P2 = sum(argm[k] in (1.5, 2.0, 3.0) for k in sides) >= 2
cen_flag = {}
for b in BETAS:
    c = out["rungs"][str(b)]["census"]
    cen_flag[str(b)] = bool(any(v["mean_X"] <= 0.02 or v["u_max"] < 0
                                for v in c.values()))
hi_drop = bool(min(S["Ti"][3], S["Ti"][4]) < max(S["Ti"][0:3]))
P3 = bool(hi_drop and (cen_flag["3.0"] or cen_flag["4.0"]))
P5 = bool(out["rungs"]["1.0"]["d0_bit_identical"]
          and out["rungs"]["2.0"]["d0_bit_identical"]
          and not (out["rungs"]["3.0"]["d0_bit_identical"]
                   and out["rungs"]["4.0"]["d0_bit_identical"]))
branch = ("B_MONOTONE" if P1 else ("B_INTERIOR" if P2 else
          ("B_COLLAPSE" if P3 else "B_ARTIFACT")))
out["verdict"] = dict(
    S_series=S, Ti_steps=[float(x) for x in steps], P1_monotone=P1,
    P2_interior=P2, per_side_argmax={k: float(v) for k, v in argm.items()},
    P3_collapse=P3, census_flag=cen_flag, P5_drive_gating=P5,
    branch=branch,
    g_spread=[out["rungs"][str(b)]["g"] for b in BETAS],
    af_resid=[out["rungs"][str(b)]["af_resid"] for b in BETAS],
    stored_unmatched_Ti={"0.5": -0.055, "1.0": 0.575, "2.0": 0.873, "4.0": 0.077},
)
json.dump(out, open("l177/ladder.json", "w"), indent=1)
log("\n=== VERDICT ===")
log(f"S_Ti over beta {BETAS}: " + " ".join(f"{v:+.3f}" for v in S["Ti"]))
for k in sides:
    log(f"  {k}: " + " ".join(f"{v:+.3f}" for v in S[k]) + f"  argmax beta {argm[k]}")
log(f"P1 monotone {P1} | P2 interior {P2} | P3 collapse {P3} | P5 drive-gating {P5}")
log(f"census flags {cen_flag}")
log(f"g spread {[round(x,5) for x in out['verdict']['g_spread']]} "
    f"af resid {[round(x,5) for x in out['verdict']['af_resid']]}")
log(f"BRANCH: {branch} | wall {time.time()-t0:.0f}s -> l177/ladder.json")
