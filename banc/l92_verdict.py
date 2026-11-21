"""L92 verdict: census classification + volley diagnostics + decomposition.

Re-derivable from l92/raw_l92.npz + l92/static.json + l92/dn_census.csv alone.
"""
import json

import numpy as np
import pandas as pd

z = np.load("l92/raw_l92.npz")
anchors = json.load(open("l92/anchors_run.json"))
static = json.load(open("l92/static.json"))
SEEDS = [11, 22, 33]
VERDICTS = {}

def af(x):
    return x

# ---- E2 census: join static census with dynamic u/X (3-seed means) ----
df = pd.read_csv("l92/dn_census.csv")
um = np.mean([z[f"cen_u_max_{s}"] for s in SEEDS], axis=0)
umean = np.mean([z[f"cen_u_mean_{s}"] for s in SEEDS], axis=0)
xmean = np.mean([z[f"cen_x_mean_{s}"] for s in SEEDS], axis=0)
df["u_max"] = um
df["u_mean"] = umean
df["x_mean"] = xmean
df["pool_any"] = df.pool_reach.fillna("{}").ne("{}")

def verdict(r):
    if r.x_mean >= 0.95:
        return "pinned"
    if r.u_max <= 0:
        return "buried"
    return "viable"

df["verdict"] = df.apply(verdict, axis=1)
tab = df.groupby(["cls", "verdict"]).size().unstack(fill_value=0)
print("== E2 census: verdict x class (cls 0=DNi 1=DNn) ==")
print(tab.to_string())
vocab = df[(df.verdict == "viable") & (df.out_cord > 0)]
print(f"\nviable WITH cord out-edges: DNi {len(vocab[vocab.cls==0])} "
      f"/ DNn {len(vocab[vocab.cls==1])}")
vp = vocab[vocab.pool_any]
print(f"viable + cord out + DIRECT antagonist-pool reach: "
      f"DNi {len(vp[vp.cls==0])} / DNn {len(vp[vp.cls==1])}")
print("DNn viable+pool-reachers by type:")
print(vp[vp.cls == 1].groupby("type").size().sort_values(
    ascending=False).to_string())
print("\n== DNge046 trio (the male-port question) ==")
d46 = df[df.type == "DNge046"][
    ["loc", "cls", "side", "out_cord", "out_w", "u_max", "u_mean", "x_mean",
     "verdict", "pool_reach"]]
print(d46.to_string())

# ---- direct motor edges of the DNge046 DNn cells (fd 2001 explanation) ----
import torch
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
motor_g = ann_gi[sup == "motor"]
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
region = ann.region.fillna("").astype(str).to_numpy()
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True
conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
g_grp = conn[in_g].groupby(["pre_root_id", "post_root_id"], sort=False)[
    "syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
sub_dn = ann[ann.super_class == "descending"]
ct_dn = sub_dn.cell_type.fillna("").astype(str).to_numpy()
dn46_all = sub_dn.gi[ct_dn == "DNge046"].to_numpy()
dn_proj46 = dn46_all[[bool(np.any((src_all == g) + (cord_mask[dst_all]) > 1)
                              ) for g in dn46_all]]
motor_set = set(motor_g[cord_mask[motor_g]].tolist())
for g in dn46_all:
    outs = dst_all[src_all == g]
    n_m = sum(1 for d in outs if int(d) in motor_set)
    print(f"DNge046 gi {g}: cord-out {sum(1 for d in outs if cord_mask[d])} "
          f"direct-MOTOR {n_m}")

# ---- C2/E1 volley diagnostics ----
print("\n== C2/E1 volley (chop vs cfn) ==")
c2 = anchors["c2_detail"]
for a in ("chop50", "chop200"):
    for s in SEEDS:
        fd = c2[f"fd_mm_{a}_{s}"]
        print(f"{a} seed {s}: dm {c2[f'dm_{a}_{s}']:.5f} fd_mm {fd} "
              f"fd_xm {c2[f'fd_xm_{a}_{s}']}")
pools = [f"{k}_{c}" for k in ("Ti", "Tr") for c in ("fL", "fR", "eL", "eR")]
print("\nper-pool max|d| (mean over 3 seeds):")
for a in ("chop50", "chop200"):
    row = [np.mean([c2[f"dpool_{a}_{p}_{s}"] for s in SEEDS]) for p in pools]
    print(f"  {a}: " + " ".join(f"{p}={v:.4f}" for p, v in zip(pools, row)))

# ---- C0A/C0C decomposition ----
print("\n== decomposition ==")
print(f"g_old {anchors['g_old']} -> g_new {anchors['g_new']:.6f} "
      f"(af {anchors['af_target']:.5f} -> {anchors['af_final']:.5f})")
print(f"C0A gain-decomp max|d| (oldref@g_new vs stored l91 fn@g_old): "
      f"{anchors['c0a_max']:.4f}")
c0c_mm = [anchors["c0c_detail"][f"mm_{s}"] for s in SEEDS]
print(f"C0C closure footprint max|d| (cfn vs oldref @g_new, matched noise): "
      f"{anchors['c0c_max']:.4f} | mm-only {max(c0c_mm):.4f}")
print(f"C1 {anchors['c1']} | af_cfn_mean {anchors['af_cfn_mean']:.5f}")

# ---- structured output ----
res = dict(
    meta=dict(g_old=anchors["g_old"], g_new=anchors["g_new"],
              af_target=anchors["af_target"], af_final=anchors["af_final"],
              n_old=anchors["n_old"], n_new=anchors["n_new"]),
    census=dict(
        by_class={str(c): df[df.cls == c].verdict.value_counts().to_dict()
                  for c in (0, 1)},
        viable_cord=dict(DNi=int(len(vocab[vocab.cls == 0])),
                         DNn=int(len(vocab[vocab.cls == 1]))),
        viable_cord_pool=dict(DNi=int(len(vp[vp.cls == 0])),
                              DNn=int(len(vp[vp.cls == 1]))),
        dn46=df[df.type == "DNge046"][
            ["loc", "cls", "side", "out_cord", "out_w", "u_max", "u_mean",
             "x_mean", "verdict"]].to_dict("records")),
    volley=dict(
        lands_50=anchors["c2_lands_50"], lands_200=anchors["c2_lands_200"],
        fd_min=anchors["fd_min"],
        dm_50={s: c2[f"dm_chop50_{s}"] for s in SEEDS},
        dm_200={s: c2[f"dm_chop200_{s}"] for s in SEEDS},
        dpool_mean={a: {p: float(np.mean([c2[f"dpool_{a}_{p}_{s}"]
                                          for s in SEEDS])) for p in pools}
                    for a in ("chop50", "chop200")}),
    decomp=dict(c0a_gain=anchors["c0a_max"], c0c_closure=anchors["c0c_max"],
                c0c_mm=max(c0c_mm), c1=anchors["c1"]),
    e1=dict(fd_mm={a: {s: c2[f"fd_mm_{a}_{s}"] for s in SEEDS}
                   for a in ("chop50", "chop200")}),
)
json.dump(res, open("l92/results_l92.json", "w"), indent=1)
df.to_csv("l92/dn_census_dyn.csv", index=False)
print("\nverdict written -> l92/results_l92.json + dn_census_dyn.csv")
