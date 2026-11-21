"""L93 static: Tr-L conduction census on the L92 CLOSURE subnet.

Question (card L93): Tr duty07_L is dead (~.16) while R lives (.95+) — is
Tr-L dead because NOTHING drives it (pathway absence) or because its drive
is buried? Pure static derivation + duty07 pin from STORED l92 cfn traces;
no new rollouts here. Everything the PREREG pins comes out of static.json.

Census forms:
  - 1-hop in-edge provenance of Tr_fL / Tr_eL (and R twins): share of the
    pool's total |in-weight| by source class (DN / intrinsic / sensory /
    motor), plus per-candidate shares (L36 >=2% conduction floor at the hop
    the volley enters, L60 depth rule).
  - DN candidate viability join: l92 stored cen_u_max/u_mean/x_mean (L36
    two-sided rule), per cell, PER SIDE (L37).
  - Intrinsic premotor candidates: top cells by SIGNED val into the Tr-L
    joint (both pools touched), excitatory preferred (L24 sign rule).
  - Base duty07_L/R for Tr recomputed on l92's stored cfn arm (l91's exact
    500-step cell form) — the pre-registered base pin.
"""
import json
import time

import numpy as np
import pandas as pd

t0 = time.time()
WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500

# ---------------- closure subnet rebuild (l92_static.py verbatim) ----------------
G = pd.read_csv  # (placeholder to keep imports tight)
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
dn_proj = np.zeros(Nall, bool)
dn_proj[src_all[cord_mask[dst_all]]] = True
dn_proj &= dn_all
keep_new = cord_mask | dn_into | dn_proj
n_new = int(keep_new.sum())

emask = keep_new[src_all] & keep_new[dst_all]
gsrc, gdst, gcount = src_all[emask], dst_all[emask], w_syn[emask]
loc = -np.ones(Nall, np.int64)
loc[keep_new] = np.arange(n_new)
lsrc, ldst = loc[gsrc], loc[gdst]
gsign_a = sign_all[gsrc]
gsign_b = np.where(is_glut[gsrc], -np.abs(gsign_a), gsign_a)
vals = (np.log1p(gcount) * gsign_b).astype(np.float32)

# class of every local cell: 0 cord-sensory 1 cord-intrinsic 2 motor 3 DNi 4 DNn
cls_cell = np.full(Nall, -1, np.int8)
cls_cell[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = 0
cls_cell[ann_gi[(sup == "ventral_nerve_cord_intrinsic")]] = 1
cls_cell[ann_gi[sup == "motor"]] = 2
cls_cell[np.where(dn_into)[0]] = 3
cls_cell[np.where(dn_proj & ~dn_into)[0]] = 4
cls_n = cls_cell[keep_new]
assert (cls_n >= 0).all(), "unclassified cell in subnet"

# pools (l92 verbatim)
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
        POOLS[f"{k}_{c}"] = np.sort(loc[mgi[m]])
pool_sizes = {k: len(v) for k, v in POOLS.items()}
assert pool_sizes == {"Ti_fL": 50, "Ti_fR": 51, "Ti_eL": 6, "Ti_eR": 6,
                      "Tr_fL": 31, "Tr_fR": 31, "Tr_eL": 24, "Tr_eR": 24}

# ---------------- 1-hop provenance shares ----------------
CLS_NAME = {0: "sensory", 1: "intrinsic", 2: "motor", 3: "DNi", 4: "DNn"}
prov = {}
for pk in ("Tr_fL", "Tr_eL", "Tr_fR", "Tr_eR", "Ti_fL", "Ti_eL"):
    pos = POOLS[pk]
    m = np.isin(ldst, pos)
    tot = float(np.abs(vals[m]).sum())
    by_cls = {}
    for c in range(5):
        mm_ = m & (cls_n[lsrc] == c)
        by_cls[CLS_NAME[c]] = round(float(np.abs(vals[mm_]).sum()) / tot, 4)
    # DN vs intrinsic mass split
    prov[pk] = dict(total_abs_w=round(tot, 1), share=by_cls)

# ---------------- DN candidates (per type-side, joint-L reach) ----------------
ct = ann.cell_type.fillna("").astype(str).to_numpy()
sd = ann.side.fillna("").astype(str).str.upper().to_numpy()
cell_type_g = np.full(Nall, "", dtype=object)
cell_side_g = np.full(Nall, "", dtype=object)
cell_type_g[ann_gi] = ct
cell_side_g[ann_gi] = sd
ct_n = cell_type_g[keep_new]
sd_n = cell_side_g[keep_new]

is_dn_edge = cls_n[lsrc] >= 3
rows = []
for pk in POOLS:
    m = is_dn_edge & np.isin(ldst, POOLS[pk])
    if not m.any():
        continue
    df_e = pd.DataFrame(dict(src=lsrc[m], val=np.abs(vals[m]).astype(np.float64),
                             sgn=vals[m].astype(np.float64),
                             type=np.array(ct_n[lsrc[m]], dtype=object),
                             side=np.array(sd_n[lsrc[m]], dtype=object)))
    for (t_, s_), gdf in df_e.groupby(["type", "side"]):
        rows.append(dict(type=t_, side=s_, pool=pk,
                         w_abs=round(float(gdf["val"].sum()), 3),
                         w_sgn=round(float(gdf["sgn"].sum()), 3),
                         n_cells=int(gdf.src.nunique())))
dn_pool = pd.DataFrame(rows)
# joint-L reach = Tr_fL + Tr_eL weight, requires BOTH pools > 0
piv = dn_pool.pivot_table(index=["type", "side"], columns="pool",
                          values="w_abs", aggfunc="sum").fillna(0)
piv["jointL"] = piv.get("Tr_fL", 0) + piv.get("Tr_eL", 0)
piv["both"] = ((piv.get("Tr_fL", 0) > 0) & (piv.get("Tr_eL", 0) > 0)).astype(int)
cand = piv[piv.both == 1].sort_values("jointL", ascending=False)

# viability join from stored l92 census (dn_pos_n local order)
z92 = np.load("l92/raw_l92.npz")
gi_new = np.where(keep_new)[0]
dn_pos_n = np.sort(loc[gi_new[dn_all[gi_new]]])
assert len(dn_pos_n) == 1288
pos_of = {int(p): i for i, p in enumerate(dn_pos_n)}
u_max = np.mean([z92[f"cen_u_max_{s}"] for s in (11, 22, 33)], axis=0)
u_mean = np.mean([z92[f"cen_u_mean_{s}"] for s in (11, 22, 33)], axis=0)
x_mean = np.mean([z92[f"cen_x_mean_{s}"] for s in (11, 22, 33)], axis=0)

viab_rows = []
for lp in dn_pos_n:
    g = gi_new[lp]
    viab_rows.append(dict(loc=int(lp), type=str(ct_n[lp]), side=str(sd_n[lp]),
                          cls=int(cls_n[lp]) - 3,
                          u_max=round(float(u_max[pos_of[int(lp)]]), 3),
                          u_mean=round(float(u_mean[pos_of[int(lp)]]), 3),
                          x_mean=round(float(x_mean[pos_of[int(lp)]]), 3)))
viab = pd.DataFrame(viab_rows)


def type_side_cells(t_, s_):
    q = viab[(viab.type == t_) & (viab.side == s_)]
    return q


top_cand = []
for (t_, s_), r in cand.head(12).iterrows():
    q = type_side_cells(t_, s_)
    top_cand.append(dict(
        type=t_, side=s_, jointL=round(float(r.jointL), 2),
        Tr_fL=round(float(r.get("Tr_fL", 0)), 2),
        Tr_eL=round(float(r.get("Tr_eL", 0)), 2),
        n=len(q),
        u_max=[float(x) for x in q.u_max], u_mean=[float(x) for x in q.u_mean],
        x_mean=[float(x) for x in q.x_mean],
        viable=int(((q.u_max > 0) & (q.x_mean < .95)).sum()),
        locs=[int(x) for x in q["loc"]],
    ))

# ---------------- intrinsic premotor candidates (joint, signed) ----------------
is_int_edge = cls_n[lsrc] == 1


def int_cand_for(fk, ek, k=16):
    rows_ = []
    for pk in (fk, ek):
        m = is_int_edge & np.isin(ldst, POOLS[pk])
        df_e = pd.DataFrame(dict(src=lsrc[m], sgn=vals[m].astype(np.float64)))
        gsum = df_e.groupby("src")["sgn"].sum()
        for src, v in gsum.items():
            rows_.append(dict(loc=int(src), pool=pk, w_sgn=round(float(v), 3)))
    ip_ = pd.DataFrame(rows_).pivot_table(index="loc", columns="pool",
                                          values="w_sgn", aggfunc="sum").fillna(0)
    ip_ = ip_[(ip_.get(fk, 0) != 0) | (ip_.get(ek, 0) != 0)]
    bp = ((ip_.get(fk, 0) > 0) & (ip_.get(ek, 0) > 0)).astype(int)
    ip_["both_pos"] = bp
    ip_["minpos"] = np.minimum(ip_.get(fk, 0), ip_.get(ek, 0))
    top_ = ip_[ip_.both_pos == 1].sort_values("minpos", ascending=False).head(k)
    out_ = [dict(loc=int(i), type=str(ct_n[i]),
                 **{fk: round(float(r[fk]), 2), ek: round(float(r[ek]), 2)})
            for i, r in top_.iterrows()]
    if out_:
        locs_ = [c["loc"] for c in out_]
        mf_ = np.isin(ldst, POOLS[fk]) & np.isin(lsrc, locs_)
        me_ = np.isin(ldst, POOLS[ek]) & np.isin(lsrc, locs_)
        sh_ = dict({fk: round(float(np.abs(vals[mf_]).sum())
                              / prov[fk]["total_abs_w"], 4)},
                   **{ek: round(float(np.abs(vals[me_]).sum())
                               / prov[ek]["total_abs_w"], 4)})
    else:
        sh_ = None
    return out_, sh_


int_rows = []
for pk in ("Tr_fL", "Tr_eL"):
    m = is_int_edge & np.isin(ldst, POOLS[pk])
    df_e = pd.DataFrame(dict(src=lsrc[m], sgn=vals[m].astype(np.float64)))
    gsum = df_e.groupby("src")["sgn"].sum()
    for src, v in gsum.items():
        int_rows.append(dict(loc=int(src), pool=pk, w_sgn=round(float(v), 3)))
ip = pd.DataFrame(int_rows).pivot_table(index="loc", columns="pool",
                                        values="w_sgn", aggfunc="sum").fillna(0)
ip = ip[(ip.get("Tr_fL", 0) != 0) | (ip.get("Tr_eL", 0) != 0)]
ip["both_pos"] = ((ip.get("Tr_fL", 0) > 0) & (ip.get("Tr_eL", 0) > 0)).astype(int)
ip["minpos"] = np.minimum(ip.get("Tr_fL", 0), ip.get("Tr_eL", 0))
top_int = ip[ip.both_pos == 1].sort_values("minpos", ascending=False).head(16)
int_cand = [dict(loc=int(i), type=str(ct_n[i]), Tr_fL=round(float(r.Tr_fL), 2),
                 Tr_eL=round(float(r.Tr_eL), 2))
            for i, r in top_int.iterrows()]
# share of the pool in-weight carried by those 16 cells
if len(int_cand):
    mfl = np.isin(ldst, POOLS["Tr_fL"]) & np.isin(lsrc, [c["loc"] for c in int_cand])
    mel = np.isin(ldst, POOLS["Tr_eL"]) & np.isin(lsrc, [c["loc"] for c in int_cand])
    int_share = dict(
        Tr_fL=round(float(np.abs(vals[mfl]).sum())
                    / prov["Tr_fL"]["total_abs_w"], 4),
        Tr_eL=round(float(np.abs(vals[mel]).sum())
                    / prov["Tr_eL"]["total_abs_w"], 4))
else:
    int_share = None
# Ti-L donor sham set (same selection rule, DIFFERENT joint = L78 transport arm)
ti_cand, ti_share = int_cand_for("Ti_fL", "Ti_eL", 16)

# ---------------- base duty07 pin from STORED l92 cfn (l91 cell form) ----------------
z92c = np.load("l92/raw_l92.npz")


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


TS = np.arange(MEAS0, WIN, 10)
base_cells = {}
for s in (11, 22, 33):
    fL = z92c[f"Tr_fL_cfn_{s}"][:WIN].astype(np.float64)
    fR = z92c[f"Tr_fR_cfn_{s}"][:WIN].astype(np.float64)
    eL = z92c[f"Tr_eL_cfn_{s}"][:WIN].astype(np.float64)
    eR = z92c[f"Tr_eR_cfn_{s}"][:WIN].astype(np.float64)
    SL = np.full(WIN, np.nan)
    SR = np.full(WIN, np.nan)
    for t in TS:
        SL[t] = S_of(fL[t - 499:t + 1], eL[t - 499:t + 1])
        SR[t] = S_of(fR[t - 499:t + 1], eR[t - 499:t + 1])
    q07 = np.zeros(len(TS), bool)
    for a0, b0, f in SEGB:
        if f == 0.7:
            q07 |= (TS >= a0 + MEAS0) & (TS < b0)
    L07 = SL[TS[q07]] >= .25
    R07 = SR[TS[q07]] >= .25
    base_cells[s] = dict(duty07_L=round(float(np.nanmean(L07)), 3),
                         duty07_R=round(float(np.nanmean(R07)), 3),
                         SL_med=round(float(np.nanmedian(SL[TS[q07]])), 3),
                         SR_med=round(float(np.nanmedian(SR[TS[q07]])), 3),
                         fL_std=round(float(fL.std()), 4),
                         eL_std=round(float(eL.std()), 4),
                         fR_std=round(float(fR.std()), 4))

out = dict(
    n_new=n_new, edges_new=int(len(vals)), pool_sizes=pool_sizes,
    prov=prov, dn_jointL_top=top_cand,
    int_cand=int_cand, int_cand_share=int_share,
    ti_cand=ti_cand, ti_cand_share=ti_share,
    base_cfn_cells=base_cells,
)
json.dump(out, open("l93/static.json", "w"), indent=1)
viab.to_csv("l93/viability.csv", index=False)
dn_pool.to_csv("l93/dn_pool_edges.csv", index=False)
print(json.dumps(prov, indent=1))
print("\nBASE (l92 cfn stored) Tr cells per seed:")
for s, c in base_cells.items():
    print(" ", s, c)
print("\nTop DN joint-L candidates (type-side):")
for c in top_cand[:10]:
    print(f"  {c['type']:>9} {c['side']:<5} jointL {c['jointL']:7.2f} "
          f"(fL {c['Tr_fL']:6.2f} eL {c['Tr_eL']:6.2f}) n {c['n']} "
          f"viable {c['viable']}/{c['n']} u_max {c['u_max']} x {c['x_mean']}")
print("\nIntrinsic premotor (both-pool excitatory) top-16:")
for c in int_cand[:8]:
    print(f"  loc {c['loc']:>6} {c['type'][:34]:<34} fL {c['Tr_fL']:7.2f} eL {c['Tr_eL']:7.2f}")
print("int cand 1-hop share:", int_share)
print(f"static done {time.time()-t0:.0f}s -> l93/static.json")
