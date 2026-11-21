"""L70 M5: female BANC premotor reciprocity census (PREREG l70/PREREG.md G4).

l68 loader verbatim (subnet 21,249 / 627,051 pair-collapsed edges); sheet =
premotor VNC-intrinsic (>=1 out-edge onto motor) + motor; reciprocity census
+ per-side fractions + 100-draw side-shuffle LI null. Compare vs male
(results_l70.json M3, prediction: female >= 0.5x male fraction).
"""
import json
import time

import numpy as np
import pandas as pd
import torch

rng = np.random.default_rng(70)
NDRAW = 100
DATA = "/home/t3rpz/critters/peabrain-lab/banc/data"
t0 = time.time()


def log(*a):
    print(*a, flush=True)


Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}

ann = pd.read_csv(f"{DATA}/dv_11845666", sep="\t", low_memory=False)
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

conn = pd.read_csv(f"{DATA}/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all)
            & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)

dn_all = np.zeros(Nall, bool)
dn_all[ann_gi[sup == "descending"]] = True
dn_into = np.zeros(Nall, bool)
dn_into[dst_all[cord_mask[src_all]]] = True
dn_into &= dn_all
keep = cord_mask | dn_into
assert int(keep.sum()) == 21249, keep.sum()

emask = keep[src_all] & keep[dst_all]
gsrc, gdst = src_all[emask], dst_all[emask]
assert len(gsrc) == 627051, len(gsrc)
loc = -np.ones(Nall, np.int64)
loc[keep] = np.arange(int(keep.sum()))
n = int(keep.sum())
lsrc, ldst = loc[gsrc], loc[gdst]

# per-node side + superclass in subnet coords (annotation-row aligned)
side_raw = ann.side.fillna("").astype(str).str.lower().to_numpy()
sup_raw = sup
_lside = np.array([""] * n, object)
_lsup = np.array([""] * n, object)
gi_kept = ann_gi[keep[ann_gi]]
_lside[loc[gi_kept]] = side_raw[keep[ann_gi]]
_lsup[loc[gi_kept]] = sup_raw[keep[ann_gi]]
lside, lsup = _lside, _lsup

motor = lsup == "motor"
log(f"subnet {n:,} edges {len(lsrc):,} motor {int(motor.sum())} | "
    f"labeled L {int((lside == 'left').sum())} R {int((lside == 'right').sum())}")

# premotor sheet
pm_mask = np.zeros(n, bool)
pm_mask[np.unique(lsrc[np.isin(ldst, np.where(motor)[0])])] = True
pm_mask &= lsup == "ventral_nerve_cord_intrinsic"
sheet = np.sort(np.concatenate([np.where(pm_mask)[0], np.where(motor)[0]]))

remap = np.full(n, -1, np.int64)
remap[sheet] = np.arange(len(sheet))
inb = (remap[lsrc] >= 0) & (remap[ldst] >= 0)
s_local, d_local = remap[lsrc[inb]], remap[ldst[inb]]
sl = s_local == d_local
if sl.any():
    s_local, d_local = s_local[~sl], d_local[~sl]
s = len(sheet)
m = len(s_local)
a_ = np.minimum(s_local, d_local)
b_ = np.maximum(s_local, d_local)
pid = a_ * s + b_
u, inv = np.unique(pid, return_inverse=True)
cnt = np.bincount(inv)
recip = cnt == 2
p_src, p_dst = u // s, u % s
dens = m / (s * (s - 1))
frac_er = dens**2 / (2 * dens - dens**2)
frac = float(recip.mean())
lab = np.where(lside[sheet] == "left", "L",
               np.where(lside[sheet] == "right", "R", ""))


def side_frac(sm):
    both = sm[p_src] & sm[p_dst]
    den = int(both.sum())
    return (float(recip[both].sum()) / den) if den else float("nan"), den


fL, dL = side_frac(lab == "L")
fR, dR = side_frac(lab == "R")
lm, rm = lab == "L", lab == "R"
cross = (lm[p_src] & rm[p_dst]) | (rm[p_src] & lm[p_dst])
fX = float(recip[cross].sum()) / int(cross.sum()) if cross.sum() else float("nan")

obs_li = (fL - fR) / (fL + fR)
nl_count = int((lab == "L").sum())
nulls = np.empty(NDRAW)
for d in range(NDRAW):
    pl = rng.permutation(len(lab))
    isL = np.zeros(len(lab), bool)
    isL[pl[:nl_count]] = True
    bothL = isL[p_src] & isL[p_dst]
    bothR = (~isL[p_src]) & (~isL[p_dst])
    fLd = recip[bothL].sum() / max(bothL.sum(), 1)
    fRd = recip[bothR].sum() / max(bothR.sum(), 1)
    nulls[d] = (fLd - fRd) / (fLd + fRd)
mu, sd = float(np.mean(nulls)), float(np.std(nulls))
z = (obs_li - mu) / sd if sd > 1e-12 else float("nan")

res = dict(
    sheet=dict(size=int(s), edges=int(m), premotor_intrinsic=int(pm_mask.sum()),
               motor=int(motor.sum())),
    recip_pairs=int(recip.sum()), connected=int(len(u)),
    fraction=round(frac, 6), er_fraction=round(float(frac_er), 8),
    over_rep=round(frac / frac_er, 1),
    fL=round(fL, 4), fL_den=dL, fR=round(fR, 4), fR_den=dR,
    f_cross=round(fX, 4), cross_den=int(cross.sum()),
    LI_recip=round(float(obs_li), 4), z=round(float(z), 2))
np.savez_compressed("/home/t3rpz/critters/peabrain-lab/malecns/l70/raw_l70_banc.npz",
                    m3banc_null=nulls, m3banc_obs=np.array([obs_li]))
with open("/home/t3rpz/critters/peabrain-lab/malecns/l70/results_l70_banc.json",
          "w") as f:
    json.dump(res, f, indent=1)

male = json.load(open("/home/t3rpz/critters/peabrain-lab/malecns/l70/results_l70.json"))
mf = male["M3"]["sheet"]["fraction"]
g4 = res["fraction"] >= 0.5 * mf
log(f"female sheet {s:,} nodes {m:,} edges | recip {res['recip_pairs']:,}/"
    f"{res['connected']:,} = {frac:.4f} (ER {frac_er:.2e}, over-rep "
    f"{res['over_rep']}x)")
log(f"per-side fL {fL:.4f} (n={dL}) fR {fR:.4f} (n={dR}) cross {fX:.4f} "
    f"(n={res['cross_den']}) | LI {obs_li:+.4f} z {z:.2f}")
log(f"G4 female ({frac:.4f}) vs male ({mf:.4f}): ratio {frac/mf:.2f} -> "
    f"{'PASS comparable-or-higher' if g4 else 'FALSIFIED'} | {time.time()-t0:.0f}s")
