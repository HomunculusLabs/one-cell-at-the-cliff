"""L134 STATIC characterization (zero rollouts): who is id 1110 (DNp33-L)?

Card (LANE.md ideas-70 L134): full annotation columns, NT join, in-subnet
wiring profile (out-degree, L107 target-tier form, direct antagonist-pool
mass), glut/non-glut status (assert, it is in the ng ladder), MaleCNS
'DNp33' string join. Frames X1's carrier for the writeup.

Extraction VERBATIM from l133_static.py (l113 form), pins re-asserted
(l121 k-ladder, l126/l131 prefixes, rank twins) so any drift trips BEFORE
a characterization number is read. Deterministic, no RNG, no rollouts.
"""
import json
import os

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
ST = json.load(open("l107/static.json"))
S92 = json.load(open("l92/static.json"))
S121 = json.load(open("l121/static.json"))
S126 = json.load(open("l126/static.json"))
S131 = json.load(open("l131/static.json"))

# ---------------- extraction (l133_static.py verbatim) ----------------
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
assert int(keep_old.sum()) == S92["n_old"] and int(keep_new.sum()) == S92["n_new"]

gsign_a = sign_all[src_all]
gsign_b = np.where(is_glut[src_all], -np.abs(gsign_a), gsign_a)
vals_all = (np.log1p(w_syn) * gsign_b).astype(np.float64)
emask_o = keep_old[src_all] & keep_old[dst_all]
emask_n = keep_new[src_all] & keep_new[dst_all]
added = emask_n & ~emask_o
gi_new = np.where(keep_new)[0]
gi_old = np.where(keep_old)[0]
dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
assert len(dn_new_g) == S92["dn_new"]
in_new_cell = np.zeros(Nall, bool)
in_new_cell[dn_new_g] = True
out_rows = added & in_new_cell[src_all]

tier_of_dst = np.full(Nall, "", dtype=object)
tier_of_dst[ann_gi[sup == "motor"]] = "motor_other"
tier_of_dst[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier_of_dst[ann_gi[(sup == "sensory")
                   & (region == "ventral_nerve_cord")]] = "vnc_sensory"
cord_of_dst = np.isin(tier_of_dst[dst_all],
                      ["motor_other", "intrinsic", "vnc_sensory"])
om = out_rows & cord_of_dst
outmass = np.zeros(Nall)
np.add.at(outmass, src_all[om], np.abs(vals_all[om]))
cell_mass = outmass[dn_new_g]
order = np.argsort(-cell_mass)
cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1)
cut_drop = np.sort(dn_new_g[order[:K]])
keep_cut = keep_new.copy()
keep_cut[cut_drop] = False
assert (K, round(float(cum[K - 1]), 4)) == (ST["cut"]["K"], ST["cut"]["mass_share"])
assert int(keep_cut.sum()) == ST["n_cut"]
heav = dn_new_g[order[:K]]
cut19_drop = np.sort(heav[is_glut[heav]])
assert len(cut19_drop) == 19, f"glut heavy = {len(cut19_drop)} != 19 (STOP)"
_mass_heavy = cell_mass[order[:K]]
mass_split = dict(
    glut19=round(float(_mass_heavy[is_glut[heav]].sum() / cell_mass.sum()), 4),
    other58=round(float(_mass_heavy[~is_glut[heav]].sum() / cell_mass.sum()), 4))
assert mass_split == {"glut19": 0.1103, "other58": 0.3921}, mass_split

glut_desc = heav[is_glut[heav]]
ng_desc = heav[~is_glut[heav]]
assert len(glut_desc) == 19 and len(ng_desc) == 58
total = cell_mass.sum()
ngmass = cell_mass[order[:K]][~is_glut[heav]]
for kk in (19, 29, 58):
    d = np.sort(ng_desc[:kk])
    want = S121["ngladder"][f"k{kk}"]["drop_ids"]
    assert [int(x) for x in d] == want, f"k{kk} drop drift (STOP)"
rank25_id, rank26_id = int(ng_desc[24]), int(ng_desc[25])
assert rank25_id == S131["rank_ids"]["rank25"] == 1110
assert rank26_id == S131["rank_ids"]["rank26"] == 319
print("extraction pins green: k-ladder + rank twins (1110/319)")

# ================= L134: characterization of gi 1110 =================
G = 1110
root626 = int(ids_all[G])
row = ann[ann.gi == G]
assert len(row) == 1, f"gi 1110 annotation rows = {len(row)} (STOP)"
row = row.iloc[0]

# ---- A. annotation columns (full) ----
COLS = ["pt_root_id", "super_class", "cell_class", "cell_sub_class",
        "cell_type", "side", "nerve", "region", "peripheral_target_type",
        "body_part_effector", "cell_function", "cell_function_detailed",
        "other_names", "neurotransmitter_predicted",
        "neurotransmitter_verified", "fafb_783_match_id",
        "manc_121_match_id", "hemilineage", "flow"]
annot = {c: (None if pd.isna(row.get(c)) else str(row.get(c)))
         for c in COLS if c in ann.columns}
nt_file = nt_map.get(root626, "<absent>")
assert not is_glut[G], "1110 glut! contradicts ng ladder (STOP)"
print("\n== A. annotation row gi 1110 ==")
for c, v in annot.items():
    print(f"  {c:28s} {v}")
print(f"  nt_join(dv_11837016)         {nt_file}")
inline_nt = annot.get("neurotransmitter_predicted")
if inline_nt is not None and inline_nt.lower() != nt_file:
    print(f"  !! inline vs join-file NT DISAGREE: '{inline_nt}' vs '{nt_file}'")

# ---- B. BANC DNp33 homologues ----
dn33 = ann[ann.cell_type.astype(str) == "DNp33"]
print("\n== B. BANC 'DNp33' cells ==")
twin_info = []
for _, r in dn33.iterrows():
    g = int(r.gi)
    in_clo = bool(keep_new[g])
    in_hv = bool(np.isin(g, heav))
    in_ng = bool(np.isin(g, ng_desc))
    cm = float(outmass[g]) if g in set(int(x) for x in dn_new_g) else None
    rk = None
    if in_hv:
        pos = int(np.where(heav == g)[0][0])
        rk = pos + 1  # heavy-77 rank
    twin_info.append(dict(gi=g, root=int(r.pt_root_id),
                          side=str(r.side), in_graph=True, in_closure=in_clo,
                          in_heavy77=in_hv, in_ng58=in_ng,
                          cell_mass=cm, heavy_rank=rk))
    print(f"  gi {g:6d} root {int(r.pt_root_id):>10d} side {str(r.side):>6s}"
          f"  closure {in_clo!s:5s} heavy77 {in_hv!s:5s} ng58 {in_ng!s:5s}"
          f"  mass {cm}  heavy_rank {rk}")
assert any(t["gi"] == G for t in twin_info), "1110 not cell_type DNp33? (STOP)"

# ---- C. wiring profile in the CLOSURE subnet (L107 tier form) ----
mot_rows = ann[ann.super_class == "motor"]
ptt = mot_rows.peripheral_target_type.fillna("").astype(str).to_numpy()
side_m = mot_rows.side.fillna("").astype(str).str.lower().to_numpy()
mgi = mot_rows.gi.to_numpy()


def has(s):
    return np.array([s in x for x in ptt])


pool_masks = {}
for k, fpat, epat in [
    ("Ti", has("tibia") & has("flexor"), has("tibia") & has("extensor")),
    ("Tr", has("trochanter") & has("flexor"),
     has("trochanter") & has("extensor")),
    ("Ta", has("tarsus") & has("depressor"), has("tarsus") & has("levator")),
    ("Sr", has("sternal") & has("anterior") & has("rotator"),
     has("sternal") & has("posterior") & has("rotator")),
    ("Pr", has("promotor"), has("remotor")),
]:
    for c, cc in (("L", "left"), ("R", "right")):
        pool_masks[f"{k}_f{c}"] = mgi[fpat & (side_m == cc)]
        pool_masks[f"{k}_e{c}"] = mgi[epat & (side_m == cc)]
for k, v in pool_masks.items():
    if k in S92["pool_sizes"]:
        assert len(v) == S92["pool_sizes"][k], (k, len(v))
n_pool = sum(len(v) for v in pool_masks.values())
print(f"antagonist pools: Ti/Tr keys == l92 pins EXACT; "
      f"5-pair union cells = {n_pool}")
pool_union = np.zeros(Nall, bool)
for v in pool_masks.values():
    pool_union[v] = True

out_e = emask_n & (src_all == G)
in_e = emask_n & (dst_all == G)
o_w = np.abs(vals_all[out_e])
o_dst = dst_all[out_e]
tot_o = float(o_w.sum())
# target tiers
tiers = {}
for t in ("motor_other", "intrinsic", "vnc_sensory"):
    m = tier_of_dst[o_dst] == t
    tiers[t] = dict(n=int(m.sum()), mass=float(o_w[m].sum()))
m_pool = pool_union[o_dst]
tiers["antagonist_pools_direct"] = dict(n=int(m_pool.sum()),
                                        mass=float(o_w[m_pool].sum()))
# broader dst superclass table
sup_of = np.full(Nall, "", dtype=object)
sup_of[ann_gi] = sup
cls_of = np.full(Nall, "", dtype=object)
cls_of[ann_gi] = ann.cell_class.fillna("").astype(str).to_numpy()
sc = sup_of[o_dst]
sc_mass = {}
for s in set(sc.tolist()):
    m = sc == s
    sc_mass[s] = dict(n=int(m.sum()), mass_share=round(float(o_w[m].sum() / tot_o), 4))
sc_mass = dict(sorted(sc_mass.items(), key=lambda kv: -kv[1]["mass_share"]))
# per-pool direct detail
pool_detail = {}
for pname, pmask in pool_masks.items():
    sel = np.isin(o_dst, pmask)
    if sel.any():
        pool_detail[pname] = dict(n=int(sel.sum()), mass=float(o_w[sel].sum()))
# added-edges-only mass (the ladder metric) re-derived
add_e = out_rows & (src_all == G)
ladder_mass = float(np.abs(vals_all[add_e]).sum())
assert abs(ladder_mass / total - S131["rank_mass"]["rank25"]) < 1e-12, \
    "1110 ladder mass drift vs l131 pin (STOP)"
# in-edges brief
src_cls = cls_of[src_all[in_e]]
in_cls = {}
for s in set(src_cls.tolist()):
    m = src_cls == s
    in_cls[s] = int(m.sum())
in_cls = dict(sorted(in_cls.items(), key=lambda kv: -kv[1]))

print("\n== C. closure wiring profile gi 1110 ==")
print(f"  out-edges (closure): {int(out_e.sum())}  total |mass| {tot_o:.4f}")
for t, v in tiers.items():
    print(f"  tier {t:26s} n {v['n']:4d}  mass {v['mass']:.4f}")
print(f"  dst super_class mass shares: {sc_mass}")
print(f"  per-pool direct hits: {pool_detail if pool_detail else 'NONE'}")
# top named targets (for the writeup: which motor cells it touches directly)
type_of = np.full(Nall, "", dtype=object)
type_of[ann_gi] = ann.cell_type.fillna("").astype(str).to_numpy()
o_i = np.argsort(-o_w)[:10]
top_targets = [dict(gi=int(o_dst[i]), cell_type=str(type_of[o_dst[i]]),
                    tier=str(tier_of_dst[o_dst[i]]),
                    side=str(ann[ann.gi == o_dst[i]].side.iloc[0])
                    if (ann.gi == o_dst[i]).any() else "",
                    mass=round(float(o_w[i]), 3)) for i in o_i]
print("  top-10 |w| targets:")
for t in top_targets:
    print(f"    {t['cell_type']:<14s} {t['side']:>6s} {t['tier']:<12s} {t['mass']:.3f}")
motor_types = sorted(set(t["cell_type"] for t in top_targets
                         if t["tier"] == "motor_other"))
print(f"  motor-edge target types (top-10 window): {motor_types}")
# walking-CPG family string join (Pugliese/Brunton family, L65/L84 lineage)
CPG_FAM = ["IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN19B012"]
all_tgt_types = type_of[o_dst]
cpg_hits = {f: int((all_tgt_types == f).sum()) for f in CPG_FAM}
cpg_hits = {k: v for k, v in cpg_hits.items() if v}
print(f"  walking-CPG family direct hits (all {len(o_dst)} edges): "
      f"{cpg_hits if cpg_hits else 'NONE'}")
print(f"  ladder(added-edges) mass pinned: {ladder_mass/total:.6f}")
print(f"  in-edges: {int(in_e.sum())}  by src cell_class: {in_cls}")

# comparative: 1110's profile rank among the ng-58
rows58 = []
for g in ng_desc:
    oe = emask_n & (src_all == g)
    ww = np.abs(vals_all[oe])
    dd = dst_all[oe]
    t = float(ww.sum())
    rows58.append(dict(
        gi=int(g), out_n=int(oe.sum()), out_mass=t,
        intr_share=float(ww[(tier_of_dst[dd] == 'intrinsic')].sum() / t),
        pool_direct=float(ww[pool_union[dd]].sum() / t),
        motor_share=float(ww[(tier_of_dst[dd] == 'motor_other')].sum() / t)))
df58 = pd.DataFrame(rows58)


def rk(col, asc=False):
    return int(df58.sort_values(col, ascending=asc).reset_index()
               .query("gi == 1110").index[0]) + 1


me = df58[df58.gi == 1110].iloc[0]
print("\n== C2. 1110 vs the ng-58 (rank / 58; group medians) ==")
for col in ("out_n", "out_mass", "intr_share", "pool_direct", "motor_share"):
    print(f"  {col:12s} 1110 {me[col]:9.4f}  rank {rk(col):>2d}  "
          f"median {df58[col].median():9.4f}")

# ---- D. MaleCNS string join ----
print("\n== D. MaleCNS 'DNp33' join ==")
atl = pd.read_csv("../malecns/l22/atlas.csv")
a = atl[atl.dn_type == "DNp33"]
assert len(a) == 1, "atlas DNp33 rows != 1 (STOP)"
a = a.iloc[0]
print(f"  atlas: cells {int(a.cells)} edges {int(a.edges)} purity {a.purity}")
print(f"  top1 {a.top1_type} share {a.top1_share:.4f} z {a.top1_z:+.1f}"
      f" | top2 {a.top2_type} {a.top2_share:.4f} z {a.top2_z:+.1f}"
      f" | top3 {a.top3_type} {a.top3_share:.4f} z {a.top3_z:+.1f}")
print(f"  family weights: flex {a.w_flex:.3f} (z {a.z_flex:+.1f})"
      f"  ext {a.w_ext:.3f} (z {a.z_ext:+.1f})"
      f"  jump {a.w_jump:.3f} (z {a.z_jump:+.1f})")
m = pd.read_feather("../malecns/data/"
                    "body-annotations-male-cns-v1.0-minconf-0.5.feather")
md = m[m.type == "DNp33"]
male_nt = None
try:
    mn = pd.read_feather("../malecns/data/"
                         "body-neurotransmitters-male-cns-v1.0.feather")
    jcol = "bodyId" if "bodyId" in mn.columns else None
    if jcol and "type" in mn.columns:
        male_nt = mn[mn.type == "DNp33"]["neurotransmitter_predicted"
                                         if "neurotransmitter_predicted"
                                         in mn.columns
                                         else mn.columns[-1]].tolist()
except Exception as e:  # noqa: BLE001 - disclosed, optional
    print(f"  male NT join skipped ({e})")
print(f"  annotations: {len(md)} cells, somaSide {sorted(md.somaSide.tolist())}"
      f"{', NT ' + str(set(male_nt)) if male_nt else ''}")
assert len(md) == 2

# ---- E. bonus: does the fafb_783 homologue id exist in the LIVE brain ----
v783 = None
try:
    GfL = torch.load("/home/t3rpz/critters/peabrain/brain_graph.pt",
                     weights_only=False)
    live_ids = set(int(x) for x in GfL["ids"].numpy().astype(np.uint64))
    fam = annot.get("fafb_783_match_id")
    v783 = dict(match_id=fam,
                in_live_brain=bool(fam is not None and int(fam) in live_ids))
    print(f"\n== E. v783 cross-join: fafb match {fam} "
          f"in live brain_graph.pt -> {v783['in_live_brain']} ==")
except Exception as e:  # noqa: BLE001 - optional, disclosed
    print(f"\n== E. v783 cross-join skipped ({e}) ==")

# ---- write ----
out = dict(gi=G, root_626=root626, annotation=annot,
           nt_join=nt_file, twins=twin_info,
           wiring=dict(out_edges=int(out_e.sum()), out_mass=tot_o,
                       tiers=tiers, dst_super_class=sc_mass,
                       pool_direct=pool_detail, top_targets=top_targets,
                       cpg_family_hits=cpg_hits,
                       in_edges=int(in_e.sum()), in_by_class=in_cls),
           ng58_profile=dict(rank_out_n=rk("out_n"),
                             rank_out_mass=rk("out_mass"),
                             rank_intr=rk("intr_share"),
                             rank_pool=rk("pool_direct"),
                             rank_motor=rk("motor_share"),
                             medians={c: float(df58[c].median())
                                      for c in ("out_n", "out_mass",
                                                "intr_share", "pool_direct",
                                                "motor_share")}),
           malecns=dict(cells=int(a.cells), edges=int(a.edges),
                        purity=a.purity, top1=[a.top1_type, float(a.top1_share),
                                               float(a.top1_z)],
                        top2=[a.top2_type, float(a.top2_share),
                              float(a.top2_z)],
                        top3=[a.top3_type, float(a.top3_share),
                              float(a.top3_z)],
                        w_flex=float(a.w_flex), w_ext=float(a.w_ext),
                        w_jump=float(a.w_jump), male_nt=male_nt),
           v783=v783,
           design="L134 static characterization of gi 1110 (rank-25 ng cell, "
                  "the L131 X1 carrier). Zero rollouts, no RNG.")
os.makedirs("l134", exist_ok=True)
json.dump(out, open("l134/static.json", "w"), indent=1)
print("\nl134/static.json written")
