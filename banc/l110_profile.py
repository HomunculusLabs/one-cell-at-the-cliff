"""L110 static: heavy-77 vs light-483 dn_new intrinsic-target profile diff.

PREREG l110/PREREG.md written FIRST. C0A/C0B hard-stop certification against
l107/static.json before any new read; R1-R6 as registered. Zero rollouts.
Extraction = l107_static.py verbatim (lines 19-160).
"""
import json
import os

import numpy as np
import pandas as pd

os.makedirs("l110", exist_ok=True)
STATIC = json.load(open("l107/static.json"))

# ---------------- extraction (l107_static.py verbatim) ----------------
import torch  # noqa: E402

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
nt_of = np.array([""] * Nall, dtype=object)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None:
        if name == "glutamate":
            is_glut[j] = True
        nt_of[j] = name

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

# ---- C0A pins vs l107/static.json (HARD STOP) ----
assert int(keep_old.sum()) == STATIC["n_old"], "C0A n_old"
assert int(keep_new.sum()) == STATIC["n_new"], "C0A n_new"
emask_o = keep_old[src_all] & keep_old[dst_all]
emask_n = keep_new[src_all] & keep_new[dst_all]
assert int(emask_o.sum()) == STATIC["edges_old"], "C0A edges_old"
assert int(emask_n.sum()) == STATIC["edges_new"], "C0A edges_new"

gi_new = np.where(keep_new)[0]
gi_old = np.where(keep_old)[0]
dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
assert len(dn_new_g) == STATIC["pins"]["dn_new"], "C0A dn_new"

gsign_a = sign_all[src_all]
gsign_b = np.where(is_glut[src_all], -np.abs(gsign_a), gsign_a)
vals_all = (np.log1p(w_syn) * gsign_b).astype(np.float64)

added = emask_n & ~emask_o
assert int(added.sum()) == STATIC["edges_new"] - STATIC["edges_old"]

in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True

# pools (l94 POOLS form verbatim)
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}


def has(s):
    return np.array([s in x for x in ptt])


POOL_G = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor")),
]:
    for c in ("fL", "fR", "eL", "eR"):
        sel = fpat if c[0] == "f" else epat
        POOL_G[f"{k}_{c}"] = np.sort(mgi[sel & (side_m == SIDE_MAP[c[1].upper()])])

pool_mask_g = np.zeros(Nall, bool)
for k in POOL_G:
    pool_mask_g[POOL_G[k]] = True

tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[(sup == "motor") & pool_mask_g[ann_gi]]] = "motor_pools"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = "vnc_sensory"

# per-dn_new out-mass onto CORD -> heavy split (l107 verbatim)
src_add, dst_add, v_add = src_all[added], dst_all[added], vals_all[added]
is_dnnew_src = in_new_cell[src_add]
out_rows = is_dnnew_src & ~in_new_cell[dst_add]
tier_add = np.array([tier_of_dst[d] for d in dst_add], dtype=object)
cord_of_dst = np.isin(tier_add, ["motor_pools", "motor_other", "intrinsic",
                                 "vnc_sensory"])
om = out_rows & cord_of_dst
outmass = np.zeros(Nall)
np.add.at(outmass, src_add[om], np.abs(v_add[om]))
cell_mass = outmass[dn_new_g]
order = np.argsort(-cell_mass)
cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1)
assert K == STATIC["cut"]["K"], "C0A K"
assert round(float(cum[K - 1]), 4) == STATIC["cut"]["mass_share"], "C0A share"
cut_drop = np.sort(dn_new_g[order[:K]])
assert cut_drop.max() < Nall

# C0A cut.families EXACT
ann_idx = {int(g): i for i, g in enumerate(ann_gi)}
ct = ann.cell_type.fillna("").astype(str).to_numpy()
drop_fam = {}
for g in cut_drop:
    drop_fam[ct[ann_idx[int(g)]]] = drop_fam.get(ct[ann_idx[int(g)]], 0) + 1
# stored dict is top-12 truncated (l107_static.py:173) — subset-compare
stored_fam = STATIC["cut"]["families"]
assert all(drop_fam.get(k) == v for k, v in stored_fam.items()), \
    f"C0A families {drop_fam}"
assert sum(drop_fam.values()) == 77

# ---- C0B: per-pool direct added edges/mass EXACT ----
c0b_fail = []
for pk, ref in STATIC["pool_direct_in"].items():
    pm = np.zeros(Nall, bool)
    pm[POOL_G[pk]] = True
    added_in = added & pm[dst_all] & in_new_cell[src_all]
    if int(added_in.sum()) != ref["added_edges"]:
        c0b_fail.append((pk, "edges", int(added_in.sum()), ref["added_edges"]))
    if round(float(np.abs(vals_all[added_in]).sum()), 3) != ref["added_mass"]:
        c0b_fail.append((pk, "mass",
                         round(float(np.abs(vals_all[added_in]).sum()), 3),
                         ref["added_mass"]))
if c0b_fail:
    print("C0B FAIL", c0b_fail)
    raise SystemExit(1)
print("C0 PASS (A: all pins EXACT; B: 8 pools x 2 fields EXACT)")

# ---------------- registered reads ----------------
POOLS = ["Ti_fL", "Ti_fR", "Ti_eL", "Ti_eR", "Tr_fL", "Tr_fR", "Tr_eL", "Tr_eR"]
pool_of = {}
for pi, pk in enumerate(POOLS):
    for g in POOL_G[pk]:
        pool_of[int(g)] = pi

dn_row = {int(g): i for i, g in enumerate(dn_new_g)}          # 560
heavy_row = np.zeros(560, bool)
for g in cut_drop:
    heavy_row[dn_row[int(g)]] = True
assert heavy_row.sum() == 77

# --- R1: signed 2-hop dn->intrinsic->pool, closure wiring ---
e1 = added & in_new_cell[src_all] & (tier_of_dst[dst_all] == "intrinsic")
d1 = src_all[e1].astype(np.int64)
t1 = dst_all[e1].astype(np.int64)
v1 = vals_all[e1]
e2_sel = emask_n & (tier_of_dst[src_all] == "intrinsic") & pool_mask_g[dst_all]
t2 = src_all[e2_sel].astype(np.int64)
p2 = np.array([pool_of[int(g)] for g in dst_all[e2_sel]], np.int64)
v2 = vals_all[e2_sel]

ut, first, counts = np.unique(t2, return_index=True, return_counts=True)
pos = np.searchsorted(ut, t1)
pos_clipped = np.clip(pos, 0, len(ut) - 1)
match = ut[pos_clipped] == t1
M = np.zeros((560, 8))
# expand join: for each e1 edge with target t in ut, cross with its e2 rows
starts = np.zeros(len(ut) + 1, np.int64)
starts[1:] = np.cumsum(counts)
cd1 = np.array([dn_row[int(g)] for g in d1])
m_idx = np.where(match)[0]
t_pos = pos_clipped[m_idx]
n_rep = counts[t_pos]
cd_rep = np.repeat(cd1[m_idx], n_rep)
v1_rep = np.repeat(v1[m_idx], n_rep)
off = np.arange(len(ut) + 1)
# per-row relative offsets
seq = np.concatenate([np.arange(c) for c in n_rep]) if len(n_rep) else np.array([], int)
e2_rows = np.repeat(starts[t_pos], n_rep) + seq
M = np.zeros((560, 8))
np.add.at(M, (cd_rep, p2[e2_rows]), v1_rep * v2[e2_rows])
print("2-hop join terms:", len(cd_rep), "e1:", int(e1.sum()), "e2:", int(e2_sel.sum()))


def asym(cells, joint):
    sel = [i for i, pk in enumerate(POOLS) if pk.startswith(joint)]
    L = [i for i in sel if POOLS[i].endswith("L")]
    R = [i for i in sel if POOLS[i].endswith("R")]
    S = M[cells][:, sel].sum(axis=1).sum()
    SL = M[cells][:, L].sum(axis=1).sum()
    SR = M[cells][:, R].sum(axis=1).sum()
    a_sign = (SL - SR) / (abs(SL) + abs(SR)) if (abs(SL) + abs(SR)) > 0 else 0.0
    aL, aR = np.abs(M[cells][:, L]).sum(), np.abs(M[cells][:, R]).sum()
    a_abs = (aL - aR) / (aL + aR) if (aL + aR) > 0 else 0.0
    return dict(SL=SL, SR=SR, S=S, A_signed=a_sign, A_abs=a_abs,
                absL=aL, absR=aR)


heavy_idx = np.where(heavy_row)[0]
light_idx = np.where(~heavy_row)[0]

rng = np.random.default_rng(1100)
NDRAW = 1000
null_A = {j: np.zeros(NDRAW) for j in ("Ti", "Tr")}
null_Aabs = {j: np.zeros(NDRAW) for j in ("Ti", "Tr")}
for i in range(NDRAW):
    sub = rng.choice(560, 77, replace=False)
    for j in ("Ti", "Tr"):
        r = asym(sub, j)
        null_A[j][i] = r["A_signed"]
        null_Aabs[j][i] = r["A_abs"]


def zsc(x, arr):
    sd = float(np.std(arr))
    return 0.0 if sd < 1e-12 else (float(x) - float(np.mean(arr))) / sd


R1 = {}
for j in ("Ti", "Tr"):
    for nm, idxs in (("heavy", heavy_idx), ("light", light_idx)):
        r = asym(idxs, j)
        r["z_signed_vs77of560"] = round(zsc(r["A_signed"], null_A[j]), 2)
        r["z_abs_vs77of560"] = round(zsc(r["A_abs"], null_Aabs[j]), 2)
        R1[f"{nm}_{j}"] = {k: (round(float(v), 4) if isinstance(v, float) else v)
                           for k, v in r.items()}
R1["per_pool"] = {
    pk: {"heavy": round(float(M[heavy_idx, i].sum()), 3),
         "light": round(float(M[light_idx, i].sum()), 3)}
    for i, pk in enumerate(POOLS)}
R1["null_mean_sd_A_signed"] = {j: [round(float(null_A[j].mean()), 4),
                                   round(float(null_A[j].std()), 4)]
                               for j in ("Ti", "Tr")}

# --- R2: sign mix onto intrinsic (1-hop) + source NT composition ---
cd_hv = heavy_row[cd1]                      # heavy mask over the e1 edge rows
neg_h = float(np.abs(v1[cd_hv][v1[cd_hv] < 0]).sum())
tot_h = float(np.abs(v1[cd_hv]).sum())
neg_l = float(np.abs(v1[~cd_hv][v1[~cd_hv] < 0]).sum())
tot_l = float(np.abs(v1[~cd_hv]).sum())
# null: fraction-negative-mass over random 77 subsets
negfrac = np.zeros(NDRAW)
for i in range(NDRAW):
    sub = rng.choice(560, 77, replace=False)
    m = np.isin(d1, dn_new_g[sub])
    n_ = float(np.abs(v1[m][v1[m] < 0]).sum())
    t_ = float(np.abs(v1[m]).sum())
    negfrac[i] = n_ / t_ if t_ > 0 else 0.0
nf_h = neg_h / tot_h if tot_h else 0.0
nf_l = neg_l / tot_l if tot_l else 0.0
R2 = {"neg_mass_frac_heavy": round(nf_h, 4),
      "neg_mass_frac_light": round(nf_l, 4),
      "z_heavy_vs_null": round(zsc(nf_h, negfrac), 2),
      "null_mean_sd": [round(float(negfrac.mean()), 4),
                       round(float(negfrac.std()), 4)]}
ntc = {}
for nm, idxs in (("heavy", heavy_idx), ("light", light_idx)):
    c = {}
    for g in dn_new_g[idxs]:
        x = nt_of[int(g)] or "unknown"
        c[x] = c.get(x, 0) + 1
    ntc[nm] = dict(sorted(c.items(), key=lambda kv: -kv[1]))
R2["source_nt_counts"] = ntc

# --- R3: target-side profile (mass-weighted side of intrinsic targets) ---
side_ann = ann.side.fillna("").astype(str).str.lower().to_numpy()
side_of = np.array([""] * Nall, dtype=object)
side_of[ann_gi] = side_ann
ts = side_of[t1]
tside = np.where(ts == "left", -1, np.where(ts == "right", 1, 0))
wm = np.abs(v1)
def side_asym(cells_mask):                  # cells_mask over the 560 dn rows
    m = cells_mask[cd1]
    Lm = float(wm[m & (tside == -1)].sum())
    Rm = float(wm[m & (tside == 1)].sum())
    us = float((tside[m] == 0).mean()) if m.sum() else 0.0
    return ((Rm - Lm) / (Rm + Lm) if (Rm + Lm) > 0 else 0.0,
            round(us, 3), Lm, Rm)
sa_h, us_h, Lm_h, Rm_h = side_asym(heavy_row)
sa_l, us_l, Lm_l, Rm_l = side_asym(~heavy_row)
# subset null
sa_null = np.zeros(NDRAW)
for i in range(NDRAW):
    sub = rng.choice(560, 77, replace=False)
    sa_null[i], _, _, _ = side_asym(np.isin(np.arange(560), sub))
# L70 permutation null: shuffle side labels over intrinsic cells, heavy set fixed
uni_t = np.unique(t1)
side_labels = tside.copy()
perm_null = np.zeros(1000)
for i in range(1000):
    lab = rng.permutation(side_labels)
    Lm = float(wm[cd_hv & (lab == -1)].sum())
    Rm = float(wm[cd_hv & (lab == 1)].sum())
    perm_null[i] = (Rm - Lm) / (Rm + Lm) if (Rm + Lm) > 0 else 0.0
R3 = {"heavy_side_asym_RminusL": round(sa_h, 4),
      "light_side_asym_RminusL": round(sa_l, 4),
      "z_heavy_vs_subset": round(zsc(sa_h, sa_null), 2),
      "subset_null_mean_sd": [round(float(sa_null.mean()), 4),
                              round(float(sa_null.std()), 4)],
      "z_heavy_vs_sideperm": round(zsc(sa_h, perm_null), 2),
      "sideperm_null_mean_sd": [round(float(perm_null.mean()), 4),
                                round(float(perm_null.std()), 4)],
      "unside_frac_heavy": us_h, "unside_frac_light": us_l,
      "massL_heavy": round(Lm_h, 1), "massR_heavy": round(Rm_h, 1),
      "massL_light": round(Lm_l, 1), "massR_light": round(Rm_l, 1)}

# --- R4: cell-type enrichment of intrinsic targets, heavy vs subset null ---
ct_of = np.array([""] * Nall, dtype=object)
ct_of[ann_gi] = ct
ct_t = ct_of[t1]
types = np.unique(ct_t[ct_t != ""])
hv = cd_hv                                  # heavy mask over e1 rows
obs_share, null_share = {}, {}
for ty in types:
    obs_share[ty] = float(wm[hv & (ct_t == ty)].sum()) / tot_h if tot_h else 0.0
null_sh = {ty: np.zeros(NDRAW) for ty in types}
for i in range(NDRAW):
    sub = rng.choice(560, 77, replace=False)
    m = np.isin(d1, dn_new_g[sub])
    tt_ = float(wm[m].sum())
    for ty in types:
        s = float(wm[m & (ct_t == ty)].sum())
        null_sh[ty][i] = s / tt_ if tt_ > 0 else 0.0
rows = []
for ty in types:
    z = zsc(obs_share[ty], null_sh[ty])
    rows.append((ty, round(obs_share[ty], 4), round(z, 2)))
rows.sort(key=lambda r: -abs(r[2]))
types_out = [dict(type=r[0], heavy_share=r[1], z_vs_null=r[2]) for r in rows[:40]]
json.dump(types_out, open("l110/types_l110.json", "w"), indent=1)

# --- R6: hop-1 vs hop-2 |mass| onto Ti_L vs Ti_R per set ---
hop1 = {}
hop2 = {}
for nm, idxs in (("heavy", heavy_idx), ("light", light_idx)):
    h1, h2 = {}, {}
    for side in ("L", "R"):
        pools_s = [i for i, pk in enumerate(POOLS)
                   if pk.startswith("Ti") and pk.endswith(side)]
        pm = np.zeros(Nall, bool)
        for i in pools_s:
            pm[POOL_G[POOLS[i]]] = True
        ai = added & pm[dst_all] & in_new_cell[src_all]
        m_ = np.isin(src_all[ai], dn_new_g[idxs])
        h1[side] = round(float(np.abs(vals_all[ai][m_]).sum()), 3)
        h2[side] = round(float(np.abs(M[idxs][:, pools_s]).sum()), 3)
    hop1[nm], hop2[nm] = h1, h2

# --- R5 gates ---
dTi = R1["heavy_Ti"]["A_signed"] - R1["light_Ti"]["A_signed"]
z_h = R1["heavy_Ti"]["z_signed_vs77of560"]
z_l = R1["light_Ti"]["z_signed_vs77of560"]
P1 = bool((z_h <= -2 or z_h >= 2 or z_l <= -2 or z_l >= 2)
          and abs(dTi) > 0.05)
P2_side = "R" if dTi > 0 else "L"
R5 = {"dA_signed_Ti_heavy_minus_light": round(float(dTi), 4),
      "z_heavy": z_h, "z_light": z_l, "P1_profile_predicts": P1,
      "P2_predicted_unchanged_side": P2_side,
      "P2_pass": bool(P2_side == "R"),
      "note": "P1: heavy/light Ti asymmetry separates at |z|>=2 and |dA|>.05; "
              "P2: sign of dA names the side cut fails to restore (dyn: R)"}

# --- ADDENDUM 1 (post-hoc, registered in PREREG before this rerun) ---
from math import sqrt
nt_counts = {}
for x in ("glutamate", "gaba", "acetylcholine"):
    k_h = int((nt_of[dn_new_g[heavy_idx]] == x).sum())
    K_tot = int((nt_of[dn_new_g] == x).sum())
    mean = 77 * K_tot / 560
    sd = sqrt(77 * (K_tot / 560) * (1 - K_tot / 560) * (560 - 77) / 559)
    nt_counts[x] = dict(heavy=k_h, pool_total=K_tot,
                        hyper_mean=round(mean, 2), sd=round(sd, 2),
                        z=round((k_h - mean) / sd, 2) if sd > 0 else 0.0)

fam_2hop = {}
for r in range(560):
    fy = ct[ann_idx[int(dn_new_g[r])]]
    fam_2hop.setdefault(fy, np.zeros(2))
    fam_2hop[fy] += M[r, [0, 1]]          # Ti_fL, Ti_fR
fam_rows = sorted(((fy, round(float(v[0]), 1), round(float(v[1]), 1))
                   for fy, v in fam_2hop.items()),
                  key=lambda r: -abs(r[1]) - abs(r[2]))[:12]

mTifL_h = M[heavy_idx, 0]
top_share = float(np.sort(mTifL_h)[::-1][:5].sum() / mTifL_h.sum()) \
    if mTifL_h.sum() != 0 else 0.0
n_pos = int((mTifL_h > 0).sum())
addendum = dict(
    label="POST-HOC descriptive (PREREG ADDENDUM 1); gates nothing",
    A1_nt_hypergeom=nt_counts,
    A2_family_2hop_Ti_fL_fR=[dict(family=f, Ti_fL=a, Ti_fR=b)
                             for f, a, b in fam_rows],
    A3_concentration=dict(top5_share_of_heavy_TifL=round(top_share, 3),
                          n_positive_cells=n_pos, n_heavy=77))

out = dict(c0="PASS (A pins + B pools EXACT vs l107/static.json)",
           sets=dict(heavy=77, light=483, dn_new=560),
           R1_twohop=R1, R2_signmix=R2, R3_target_side=R3,
           R5_gates=R5, R6_hops=dict(hop1_direct=hop1, hop2_via_intrinsic=hop2),
           addendum=addendum,
           dynamic_pins="results_l109.json Ti cut L .853 kL 32/32 / R .164 kR 0/32; "
                        "b65 .997/.996; full .394/.440; Tr cut .077/.366",
           null_seed=1100, ndraw=NDRAW)
json.dump(out, open("l110/results_l110.json", "w"), indent=1)
print(json.dumps(addendum, indent=1))
print("VERDICT P1:", R5["P1_profile_predicts"], "| P2:", R5["P2_pass"])
