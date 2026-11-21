"""L138 STATIC slice A (zero rollouts): cross-connectome DNp33 triangulation.

PREREG l138/PREREG.md FIRST (registered before this ran).
BANC side: extraction VERBATIM l134_static.py (pins re-asserted so drift trips
before any L138 number). Male side: extraction VERBATIM l32_antagonism.py forms
(cord/dn_into/dn_proj closure mirror, type-name pools, consensus_nt).
Deterministic, no RNG, no rollouts, CPU-only.
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
S131 = json.load(open("l131/static.json"))

# ---------------- BANC extraction (l134_static.py verbatim) ----------------
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
for kk in (19, 29, 58):
    d = np.sort(ng_desc[:kk])
    want = S121["ngladder"][f"k{kk}"]["drop_ids"]
    assert [int(x) for x in d] == want, f"k{kk} drop drift (STOP)"
rank25_id, rank26_id = int(ng_desc[24]), int(ng_desc[25])
assert rank25_id == S131["rank_ids"]["rank25"] == 1110
assert rank26_id == S131["rank_ids"]["rank26"] == 319
print("BANC pins green: k-ladder + rank twins (1110/319) + K/mass_split")

# BANC window shares (S3 baseline)
banc_heavy_mass = _mass_heavy / total
banc_ng = banc_heavy_mass[~is_glut[heav]]  # desc order within ng
banc_window = dict(
    r1_19=round(float(banc_ng[:19].sum()), 4),
    r20_29=round(float(banc_ng[19:29].sum()), 4),
    r30_58=round(float(banc_ng[29:].sum()), 4))

# BANC DNp33 rows (S4 anchor side)
banc_dn33 = ann[ann.cell_type.astype(str) == "DNp33"]
row1110 = ann[ann.gi == 1110].iloc[0]
fafb_match = row1110.get("fafb_783_match_id")
fafb_match = None if pd.isna(fafb_match) else str(fafb_match)

# ---------------- MaleCNS closure mirror (l32 forms verbatim) ----------------
print("\n== MALE side (closure mirror) ==")
M = pd.read_feather("../malecns/data/"
                    "body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = M[M["superclass"].notna()].reset_index(drop=True)
mids = lab["bodyId"].to_numpy(np.uint64)
midx = {int(r): i for i, r in enumerate(mids)}
msup = lab["superclass"].astype(str).to_numpy()
mtyp = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()

mnt = pd.read_feather("../malecns/data/"
                      "body-neurotransmitters-male-cns-v1.0.feather",
                      columns=["body", "consensus_nt"])
mnt_map = dict(zip(mnt["body"].astype(np.uint64),
                   mnt["consensus_nt"].astype(str).str.lower()))
m_nt_names = np.array([str(mnt_map.get(int(b), "unknown")) for b in mids])
m_glut = m_nt_names == "glutamate"

mw = pd.read_feather(
    "../malecns/data/"
    "connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
mw = mw[mw["body_pre"].isin(midx) & mw["body_post"].isin(midx)]
msrc = mw["body_pre"].map(midx).to_numpy(np.int64)
mdst = mw["body_post"].map(midx).to_numpy(np.int64)
mwv = mw["weight"].to_numpy(np.float64)
N_m = len(mids)

m_cord = np.isin(msup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
m_dn_all = msup == "descending_neuron"
m_dn_into = np.zeros(N_m, bool)
m_dn_into[mdst[m_cord[msrc]]] = True
m_dn_into &= m_dn_all
m_dn_proj = np.zeros(N_m, bool)
m_dn_proj[msrc[m_cord[mdst]]] = True
m_dn_proj &= m_dn_all
m_keep_old = m_cord | m_dn_into
m_keep_new = m_cord | m_dn_into | m_dn_proj
m_added = m_keep_new[msrc] & m_keep_new[mdst] & ~(m_keep_old[msrc] & m_keep_old[mdst])
m_gi_new = np.where(m_keep_new)[0]
m_gi_old = np.where(m_keep_old)[0]
m_dn_new = m_gi_new[~np.isin(m_gi_new, m_gi_old)]

m_cord_dst = m_cord[mdst]
m_in_new_cell = np.zeros(N_m, bool)
m_in_new_cell[m_dn_new] = True
m_om = m_added & m_in_new_cell[msrc] & m_cord_dst
m_outmass = np.zeros(N_m)
np.add.at(m_outmass, msrc[m_om], np.log1p(np.abs(mwv[m_om])))
m_cell_mass = m_outmass[m_dn_new]
m_order = np.argsort(-m_cell_mass)
m_cum = np.cumsum(m_cell_mass[m_order]) / m_cell_mass.sum()
m_K = int(np.searchsorted(m_cum, 0.50) + 1)
m_heav = m_dn_new[m_order[:m_K]]
m_glut_desc = m_heav[m_glut[m_heav]]
m_ng_desc = m_heav[~m_glut[m_heav]]
m_total = m_cell_mass.sum()

s1 = dict(n_keep_old=int(m_keep_old.sum()), n_keep_new=int(m_keep_new.sum()),
          dn_new=int(len(m_dn_new)), added_edges=int(m_added.sum()),
          added_dn_out_edges=int(m_om.sum()),
          dn_new_glut=int(m_glut_desc.sum()),
          dn_new_ng=int(len(m_ng_desc)), heavy_K=int(m_K),
          heavy_mass_share=round(float(m_cum[m_K - 1]), 4))
print(f"S1: keep_old {s1['n_keep_old']:,} keep_new {s1['n_keep_new']:,} "
      f"dn_new {s1['dn_new']:,} added {s1['added_edges']:,} "
      f"(dn-out {s1['added_dn_out_edges']:,}) | heavy K {m_K} "
      f"({s1['dn_new_glut']} glut / {s1['dn_new_ng']} ng)")

# S2: DNp33 position
md33 = np.where(mtyp == "DNp33")[0]
assert len(md33) == 2, f"male DNp33 cells = {len(md33)} != 2 (STOP)"
d33_pos = []
for g in md33:
    in_hv = bool(np.isin(g, m_heav))
    glut = bool(m_glut[g])
    rk = int(np.where(m_heav == g)[0][0]) + 1 if in_hv else None
    ng_rk = (int(np.where(m_ng_desc == g)[0][0]) + 1
             if (in_hv and not glut) else None)
    d33_pos.append(dict(gi=int(g), bodyId=int(mids[g]),
                        somaSide=str(lab.somaSide.iloc[g]),
                        nt=str(m_nt_names[g]), glut=glut,
                        in_heavy=in_hv, heavy_rank=rk, ng_rank=ng_rk,
                        mass=round(float(m_outmass[g]), 4),
                        mass_share=round(float(m_outmass[g] / m_total), 6)))
print("S2: male DNp33:", json.dumps(d33_pos))

# S3: window shape (male ng shares at its own scale + DNp33 window content)
m_heavy_mass = m_cell_mass[m_order[:m_K]] / m_total
m_ng_mass = m_heavy_mass[~m_glut[m_heav]]
m_window = dict(
    r1_19=round(float(m_ng_mass[:19].sum()), 4) if len(m_ng_mass) >= 19 else None,
    r20_29=round(float(m_ng_mass[19:29].sum()), 4) if len(m_ng_mass) >= 29 else None,
    r30_rest=round(float(m_ng_mass[29:].sum()), 4) if len(m_ng_mass) > 29 else None,
    n_ng=len(m_ng_mass))
print(f"S3: window shares male {m_window} vs BANC {banc_window}")
# who are the male ng rank twins (descriptive)
m_twin_types = []
for rr in (24, 25):  # ranks 25/26 zero-based
    if len(m_ng_desc) > rr:
        g = int(m_ng_desc[rr])
        m_twin_types.append(dict(ng_rank=rr + 1, bodyId=int(mids[g]),
                                 type=str(lab.type.iloc[g]),
                                 somaSide=str(lab.somaSide.iloc[g]),
                                 mass_share=round(float(m_outmass[g] / m_total), 6)))
print("male ng rank-25/26 cells (descriptive):", json.dumps(m_twin_types))
m_top_types = [str(lab.type.iloc[int(g)]) for g in m_ng_desc[:10]]
print("male ng top-10 types:", m_top_types)

# S5: male pools (l32 type-name form)
m_motor = np.isin(msup, ["vnc_motor", "cb_motor"])
pools_m = {}
for k in ("Ti", "Tr"):
    f = m_motor & np.isin(mtyp, [f"{k} flexor MN", f"{k.lower()} flexor MN"])
    e = m_motor & (mtyp == f"{k} extensor MN")
    assert f.any() and e.any(), (k, int(f.sum()), int(e.sum()))
    pools_m[f"{k}_flex"] = int(f.sum())
    pools_m[f"{k}_ext"] = int(e.sum())
print(f"S5: male pools {pools_m} vs BANC "
      f"{ {k: S92['pool_sizes'][k] for k in ('Ti_fL','Ti_eL','Tr_fL','Tr_eL') if k in S92['pool_sizes']} }")

# S4: v783 triangulation
v783_n = None
try:
    va = pd.read_csv("/home/t3rpz/critters/peabrain/data/neuron_annotations.tsv",
                     sep="\t", low_memory=False)
    v33 = va[va.cell_type.astype(str) == "DNp33"]
    v783_n = dict(n=len(v33),
                  sides=sorted(v33.side.astype(str).tolist()) if "side" in v33.columns else None)
except Exception as e:  # noqa: BLE001
    v783_n = dict(error=str(e))
live_ok = None
try:
    Gl = torch.load("/home/t3rpz/critters/peabrain/brain_graph.pt",
                    weights_only=False)
    live_ids = set(int(x) for x in Gl["ids"].numpy().astype(np.uint64))
    fam = int(fafb_match) if fafb_match else None
    live_ok = bool(fam is not None and fam in live_ids)
except Exception as e:  # noqa: BLE001
    live_ok = f"error: {e}"
print(f"S4: v783 'DNp33' rows {v783_n} | BANC 1110 fafb match {fafb_match} "
      f"in live brain -> {live_ok}")

# post-hoc robustness (disclosed in PREREG S2 note): DNp33 rank under RAW weights
m_outmass_raw = np.zeros(N_m)
np.add.at(m_outmass_raw, msrc[m_om], np.abs(mwv[m_om]))
raw_ranks = []
for g in md33:
    rr = (int((m_outmass_raw[m_dn_new] > m_outmass_raw[g]).sum()) + 1)
    raw_ranks.append(dict(gi=int(g), raw_rank_of_dnnew=rr))
print("post-hoc RAW-weight rank of DNp33 among dn_new:", raw_ranks)


# ==================== L170: matched synapse floor (male side) ===============
# PREREG l170/PREREG.md registered FIRST (before any floor>=2 number).
# Everything ABOVE this line is l138_static.py VERBATIM (head-prefix byte
# identity asserted by l170_build.py), so all BANC + male pins above re-ran as
# free certification. l138/static.json is NEVER rewritten by this script.
print("\n== L170: matched synapse floor on the male side ==")
P170 = json.load(open("l170/precheck.json"))
S138 = json.load(open("l138/static.json"))
assert P170["w_min"] == 1.0 and P170["dup_pairs"] == 0, "precheck drift (STOP)"

m_cord_f = np.isin(msup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
assert bool((m_cord_f == m_cord).all()), "cord mask drift vs head (STOP)"


def male_ladder(floor):
    """l138 male closure-mirror extraction, forms VERBATIM, over weight>=floor."""
    ke = mwv >= float(floor)
    s, d, v = msrc[ke], mdst[ke], mwv[ke]
    into = np.zeros(N_m, bool)
    into[d[m_cord_f[s]]] = True
    into &= m_dn_all
    proj = np.zeros(N_m, bool)
    proj[s[m_cord_f[d]]] = True
    proj &= m_dn_all
    k_old = m_cord_f | into
    k_new = m_cord_f | into | proj
    add = k_new[s] & k_new[d] & ~(k_old[s] & k_old[d])
    gi_n, gi_o = np.where(k_new)[0], np.where(k_old)[0]
    dnn = gi_n[~np.isin(gi_n, gi_o)]
    inew = np.zeros(N_m, bool)
    inew[dnn] = True
    om = add & inew[s] & m_cord_f[d]
    omass = np.zeros(N_m)
    np.add.at(omass, s[om], np.log1p(np.abs(v[om])))
    cm = omass[dnn]
    assert len(dnn) > 0 and cm.sum() > 0, f"empty cohort at floor {floor} (STOP)"
    order = np.argsort(-cm)
    cum = np.cumsum(cm[order]) / cm.sum()
    K = int(np.searchsorted(cum, 0.50) + 1)
    heav = dnn[order[:K]]
    glut_d = heav[m_glut[heav]]
    ng_d = heav[~m_glut[heav]]
    hmass = cm[order[:K]] / cm.sum()
    ngmass = hmass[~m_glut[heav]]
    s1 = dict(n_keep_old=int(k_old.sum()), n_keep_new=int(k_new.sum()),
              dn_new=int(len(dnn)), added_edges=int(add.sum()),
              added_dn_out_edges=int(om.sum()),
              dn_new_glut=int(len(glut_d)), dn_new_ng=int(len(ng_d)),
              heavy_K=int(K), heavy_mass_share=round(float(cum[K - 1]), 4))
    window = dict(
        r1_19=round(float(ngmass[:19].sum()), 4) if len(ngmass) >= 19 else None,
        r20_29=round(float(ngmass[19:29].sum()), 4) if len(ngmass) >= 29 else None,
        r30_rest=round(float(ngmass[29:].sum()), 4) if len(ngmass) > 29 else None,
        n_ng=int(len(ngmass)))
    # DNp33 position under this floor
    d33 = []
    for g in md33:
        oe = int(((s == g) & m_cord_f[d]).sum())
        ie = int(((d == g) & m_cord_f[s]).sum())
        in_coh = bool(inew[g])
        ngr = (int(np.where(ng_d == g)[0][0]) + 1
               if (in_coh and bool(np.isin(g, ng_d))) else None)
        d33.append(dict(gi=int(g), bodyId=int(mids[g]),
                        somaSide=str(lab.somaSide.iloc[int(g)]),
                        dn_into=bool(into[g]), dn_proj=bool(proj[g]),
                        out_cord_edges=oe, in_cord_edges=ie,
                        in_cohort=in_coh, ng_rank=ngr,
                        mass=round(float(omass[g]), 4),
                        mass_share=round(float(omass[g] / cm.sum()), 6)))
    # design pins for a future dynamic walk (BANC analog: ng ranks 25/26 twins)
    pins = dict(ng_top10=[str(lab.type.iloc[int(g)]) for g in ng_d[:10]],
                ng_mass_list=[round(float(x), 6) for x in ngmass[:40]])
    if len(ng_d) > 25:
        a, b = int(ng_d[24]), int(ng_d[25])
        pins["rank25"] = dict(gi=a, bodyId=int(mids[a]),
                              type=str(lab.type.iloc[a]),
                              somaSide=str(lab.somaSide.iloc[a]),
                              mass_share=round(float(omass[a] / cm.sum()), 6))
        pins["rank26"] = dict(gi=b, bodyId=int(mids[b]),
                              type=str(lab.type.iloc[b]),
                              somaSide=str(lab.somaSide.iloc[b]),
                              mass_share=round(float(omass[b] / cm.sum()), 6))
        pins["twin_gap"] = round(float(abs(omass[a] - omass[b]) / cm.sum()), 8)
    return dict(floor=int(floor), edges_kept=int(ke.sum()), s1=s1,
                window=window, dnp33=d33, pins=pins,
                dn_total=int(m_dn_all.sum()), dn_into=int(into.sum()),
                dn_proj=int(proj.sum()))


LAD = {}
for fl in (1, 2, 3, 4):
    LAD[fl] = male_ladder(fl)
    r = LAD[fl]
    print(f"floor {fl}: edges {r['edges_kept']:>11,} | dn_into {r['dn_into']:>5,}"
          f" dn_proj {r['dn_proj']:>5,} | dn_new {r['s1']['dn_new']:>4,}"
          f" (glut {r['s1']['dn_new_glut']:>3} / ng {r['s1']['dn_new_ng']:>4})"
          f" | K {r['s1']['heavy_K']:>3} share {r['s1']['heavy_mass_share']}"
          f" | n_ng {r['window']['n_ng']:>4} window {r['window']['r1_19']},"
          f"{r['window']['r20_29']},{r['window']['r30_rest']}")

# ---------------- CERT block (before any floor>=2 number is READ) -----------
c1 = LAD[1]["s1"]
for k, want in S138["male_s1"].items():
    assert c1[k] == want, f"CERT-1 FAIL {k}: {c1[k]} != {want} (STOP)"
assert LAD[1]["s1"]["heavy_mass_share"] == 0.5187
assert (LAD[1]["dn_total"], LAD[1]["dn_into"]) == (
    S138["probe"]["male_dn_total"], S138["probe"]["male_dn_into"]), "CERT-2 dn counts"
assert LAD[1]["s1"]["dn_new"] == S138["probe"]["male_pure_proj"] == 28
for got, want in zip(LAD[1]["dnp33"], S138["probe"]["male_dnp33"]):
    assert got["gi"] == want["gi"] and got["somaSide"] == want["side"]
    assert got["out_cord_edges"] == want["out_cord_edges"], ("CERT-2 out", got, want)
    assert got["in_cord_edges"] == want["in_cord_edges"], ("CERT-2 in", got, want)
    assert got["dn_into"] is want["dn_into"] and got["dn_proj"] is want["dn_proj"]
assert LAD[1]["window"] == S138["male_s3_window"], (
    "CERT-2 window", LAD[1]["window"], S138["male_s3_window"])
assert LAD[1]["pins"]["ng_top10"] == S138["male_ng_top10"], "CERT-2 top10"
assert LAD[1]["pins"]["ng_mass_list"] == S138["male_ng_mass_list"], "CERT-2 mass"
print("CERT-1/2 GREEN: floor-1 arm reproduces the stored l138 male side EXACTLY")

# ---------------- registered verdict (PREREG branches) ----------------------
dn1, dn3 = LAD[1]["s1"]["dn_new"], LAD[3]["s1"]["dn_new"]
K1, K3 = LAD[1]["s1"]["heavy_K"], LAD[3]["s1"]["heavy_K"]
rel = abs(dn3 - dn1) / dn1
m1 = bool(rel >= 0.20)
m2 = bool((not m1) and abs(K3 - K1) <= 1)
d33_f3 = LAD[3]["dnp33"]
m3 = bool(all(x["in_cohort"] for x in d33_f3))
branch = ("M1_floor_changes_cohort" if m1 else
          ("M2_floor_neutral" if m2 else "NEITHER_disclose"))
p1 = bool(dn3 > dn1)
p2 = bool(all(a["in_cord_edges"] < b["in_cord_edges"]
              for a, b in zip(d33_f3, LAD[1]["dnp33"])))
print(f"\nBRANCH {branch} | rel change {rel:.4f} (dn_new {dn1} -> {dn3}), "
      f"K {K1} -> {K3}")
print(f"P1 (dn_new rises) {p1} | P2 (DNp33 in-edges fall) {p2} | "
      f"M3_dnp33_pure {m3} ({[x['ng_rank'] for x in d33_f3]} ng ranks)")
print("P4 window computable at floor 3:",
      LAD[3]["window"]["r30_rest"] is not None,
      "| BANC baseline", banc_window)

out170 = dict(
    design="L170 static: MaleCNS closure-mirror extraction at MATCHED synapse "
           "floor (BANC's implicit pair-level floor 3). Head block is "
           "l138_static.py VERBATIM. Zero rollouts, no RNG. PREREG "
           "l170/PREREG.md registered FIRST.",
    precheck=P170,
    ladder={str(k): v for k, v in LAD.items()},
    banc_window=banc_window, banc_K=K,
    verdict=dict(branch=branch, rel_change=round(float(rel), 4),
                 dn_new_1=dn1, dn_new_3=dn3, K_1=K1, K_3=K3,
                 M1=m1, M2=m2, M3_dnp33_pure=m3, P1=p1, P2=p2,
                 P4_window_computable=bool(
                     LAD[3]["window"]["r30_rest"] is not None)),
    reviewer_reported=dict(pure_proj=342, K=52,
                           note="REVIEWER-REPORTED (L167 I2), BARRED from the "
                                "draft; stored only for the lane log comparison"))
json.dump(out170, open("l170/static.json", "w"), indent=1)
print("\nl170/static.json written")
