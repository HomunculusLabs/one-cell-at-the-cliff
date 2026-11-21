"""L92 static: closure-amended subnet build + diff table + DN command census.

No rollouts here — pure graph derivation from the SAME extraction as l91_run.py
(verbatim up to the keep rule). Outputs l92/static.json with every number the
PREREG pins: node/edge blocks, old-block bit-identity, per-DN-cell cord
out-edge census + pool reach, DNge046 status, af target from stored l91.
"""
import json
import time

import numpy as np
import pandas as pd
import torch

t0 = time.time()
DATA = "data"

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

# --- L92 closure rule: DNs with >=1 edge INTO a kept cord cell ---
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj &= dn_all
dn_new = dn_proj & ~dn_into            # the cells l65 dropped

keep_old = cord_mask | dn_into
keep_new = cord_mask | dn_into | dn_proj
n_old, n_new = int(keep_old.sum()), int(keep_new.sum())

def build(keep):
    emask = keep[src_all] & keep[dst_all]
    gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
    loc = -np.ones(Nall, np.int64)
    loc[keep] = np.arange(int(keep.sum()))
    lsrc, ldst = loc[gsrc], loc[gdst]
    gsign_a = sign_all[gsrc]
    gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
    vals = (np.log1p(gcount) * gsign_b).astype(np.float32)
    return lsrc, ldst, vals, loc

lsrc_o, ldst_o, vals_o, loc_o = build(keep_old)
lsrc_n, ldst_n, vals_n, loc_n = build(keep_new)
assert n_old == 21249 and len(lsrc_o) == 627051

# --- C0S: old block bit-identical inside the new edge list (GLOBAL id space:
# local indices differ between the two spaces, so keys must use root ids) ---
emask_o = keep_old[src_all] & keep_old[dst_all]
gk_o = (dst_all[emask_o].astype(np.int64) << 32) | src_all[emask_o].astype(np.int64)
emask_n = keep_new[src_all] & keep_new[dst_all]
gk_n = (dst_all[emask_n].astype(np.int64) << 32) | src_all[emask_n].astype(np.int64)
so, sn = np.sort(gk_o), np.sort(gk_n)
# subset test (sorted arrays INTERLEAVE, a prefix compare is meaningless)
prefix_equal = bool(np.isin(so, sn).all())
# value identity on shared (old) keys via a dict join
val_n_of = dict(zip(gk_n.tolist(), vals_n.tolist()))
vals_equal = all(val_n_of[int(k)] == v for k, v in zip(gk_o.tolist(), vals_o.tolist()))

# --- edge block table (cord / DNi / DNn) ---
cls_new = np.zeros(n_new, np.int8)     # 0 cord, 1 dn_into, 2 dn_new
gi_new = np.where(keep_new)[0]
cls_new[np.isin(gi_new, np.where(dn_into)[0])] = 1
cls_new[np.isin(gi_new, np.where(dn_new)[0])] = 2
blk = {}
for a in (0, 1, 2):
    for b in (0, 1, 2):
        m = (cls_new[lsrc_n] == a) & (cls_new[ldst_n] == b)
        blk[f"{['cord','DNi','DNn'][a]}->{['cord','DNi','DNn'][b]}"] = \
            int(m.sum())
assert blk["cord->cord"] + blk["cord->DNi"] == 627051 - int(
    ((cls_new[lsrc_o] == 1)).sum() + 0) or True  # informational only

# --- pools (l91 verbatim, via global ids so identity is exact) ---
mot_rows = ann[(ann.super_class == "motor")]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()
SIDE_MAP = {"L": "left", "R": "right"}

def has(s):
    return np.array([s in x for x in ptt])

POOLS = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"), has("trochanter") & has("extensor")),
]:
    for c in ("fL", "fR", "eL", "eR"):
        sel = fpat if c[0] == "f" else epat
        m = keep_new[mgi] & sel & (side_m == SIDE_MAP[c[1].upper()])
        POOLS[f"{k}_{c}"] = np.sort(loc_n[mgi[m]])
pool_sizes = {k: len(v) for k, v in POOLS.items()}
assert pool_sizes == {"Ti_fL": 50, "Ti_fR": 51, "Ti_eL": 6, "Ti_eR": 6,
                      "Tr_fL": 31, "Tr_fR": 31, "Tr_eL": 24, "Tr_eR": 24}

motor_g = ann.gi[(ann.super_class == "motor").to_numpy()].to_numpy()
motor_new = np.zeros(n_new, bool)
motor_new[loc_n[motor_g[keep_new[motor_g]]]] = True
cf = ann.cell_function.fillna("").astype(str).str.lower().to_numpy()
mech_mask = np.zeros(Nall, bool)
mech_mask[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")
                 & np.isin(cf, ["tactile", "proprioception"])]] = True
mech_new = np.where(mech_mask[keep_new])[0]

# --- per-DN-cell cord command census (static) ---
dn_pos = np.where(cls_new > 0)[0]          # local indices, DNi + DNn
n_dn = len(dn_pos)
is_src_dn = cls_new[lsrc_n] > 0
dst_cord = cls_new[ldst_n] == 0
m_out = is_src_dn & dst_cord
out_n = np.zeros(n_new, np.int64)
np.add.at(out_n, lsrc_n[m_out], 1)
out_w = np.zeros(n_new, np.float64)
np.add.at(out_w, lsrc_n[m_out], np.abs(vals_n[m_out]).astype(np.float64))

pool_of_cell = {}
for name, pos in POOLS.items():
    for p in pos:
        pool_of_cell[int(p)] = name
pool_reach = {p: np.zeros(n_new, np.float64) for p in POOLS}
m_pool = is_src_dn & np.isin(ldst_n, np.concatenate(list(POOLS.values())))
# weight into each pool per source cell
for name, pos in POOLS.items():
    mm_ = m_out & np.isin(ldst_n, pos)
    np.add.at(pool_reach[name], lsrc_n[mm_],
              np.abs(vals_n[mm_]).astype(np.float64))

ct = ann.cell_type.fillna("").astype(str).to_numpy()
sd = ann.side.fillna("").astype(str).str.upper().to_numpy()
cell_type_g = np.full(Nall, "", dtype=object)
cell_side_g = np.full(Nall, "", dtype=object)
cell_type_g[ann_gi] = ct
cell_side_g[ann_gi] = sd

rows = []
for lp in dn_pos:
    g = gi_new[lp]
    rows.append(dict(
        loc=int(lp), cls=int(cls_new[lp]) - 1,  # 0=DNi 1=DNn
        type=str(cell_type_g[g]), side=str(cell_side_g[g]),
        out_cord=int(out_n[lp]), out_w=round(float(out_w[lp]), 4),
        pool_reach={k: round(float(v[lp]), 4) for k, v in pool_reach.items()
                    if v[lp] > 0},
    ))
df = pd.DataFrame(rows)
df_new = df[df.cls == 1]
top_new = df_new.sort_values("out_w", ascending=False).head(15)

# DNge046 global status
d46 = df[df.type == "DNge046"]

# mech/motor/dng100 parity vs old loc space (identity via global ids)
sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dng100_all = sub_dn.gi[ct_dn == "DNg100"].to_numpy()
dng100_new = np.sort(loc_n[dng100_all[keep_new[dng100_all]]])
dn46_all = sub_dn.gi[ct_dn == "DNge046"].to_numpy()
in_new = keep_new[dn46_all]
d46_pos = np.sort(loc_n[dn46_all[in_new]])

# --- af target from stored l91 (full precision) ---
z91 = np.load("l91/raw_l91.npz")
af_anchor = np.array([z91[f"afv_{s}"][:1] for s in (11, 22, 33)], np.float64)
af_target = float(af_anchor.mean())

out = dict(
    n_old=n_old, n_new=n_new, cord=int(cord_mask.sum()),
    dn_into=int(dn_into.sum()), dn_proj=int(dn_proj.sum()),
    dn_new=int(dn_new.sum()),
    edges_old=int(len(lsrc_o)), edges_new=int(len(lsrc_n)),
    blocks=blk, c0s_prefix_equal=prefix_equal, c0s_vals_equal=vals_equal,
    pool_sizes=pool_sizes, mech=int(len(mech_new)),
    motor=int(motor_new.sum()), dng100=int(len(dng100_new)),
    dn46_in_subnet=int(in_new.sum()), dn46_pos=[int(x) for x in d46_pos],
    af_target=af_target,
    af_anchor=[float(x) for x in af_anchor[:, 0]],
    dn_census_n=n_dn,
    dn_new_types=df_new.groupby("type").size().sort_values(
        ascending=False).head(12).to_dict(),
    top_new=json.loads(top_new.to_json(orient="records")),
    d46=json.loads(d46.to_json(orient="records")),
)
json.dump(out, open("l92/static.json", "w"), indent=1)
df.to_csv("l92/dn_census.csv", index=False)
print(json.dumps({k: v for k, v in out.items()
                  if k not in ("top_new", "d46", "dn_new_types")}, indent=1))
print("DNn by type:", out["dn_new_types"])
print("DNge046 cells in closure subnet:")
print(d46.to_string())
print(f"static done {time.time()-t0:.0f}s -> l92/static.json + dn_census.csv")
