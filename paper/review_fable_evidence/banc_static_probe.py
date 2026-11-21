# Reviewer's read-only static probe on BANC (mirrors the extraction block of banc/l135_run.py lines 80-203). Writes nothing.
import json, numpy as np, pandas as pd, torch, collections
B = "/home/t3rpz/critters/peabrain-lab/banc/"
Gf = torch.load(B + "banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64); Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()
ann = pd.read_csv(B + "data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]; ann["gi"] = ann["gi"].astype(int)
nt = pd.read_csv(B + "data/dv_11837016", low_memory=False, usecols=["root_626", "neurotransmitter_predicted"])
nt_map = dict(zip(nt["root_626"].astype(np.uint64), nt["neurotransmitter_predicted"].astype(str).str.lower()))
is_glut = np.zeros(Nall, bool)
for r, name in nt_map.items():
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate": is_glut[j] = True
region = ann.region.fillna("").astype(str).to_numpy(); sup = ann.super_class.fillna("").astype(str).to_numpy(); ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool); cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True
conn = pd.read_csv(B + "data/dv_11842997", compression="gzip", usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = conn["pre_root_id"].astype(np.uint64).isin(idx_all) & conn["post_root_id"].astype(np.uint64).isin(idx_all)
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64); dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)
print("pairs in graph:", len(w_syn), "min syn", w_syn.min())
dn_all = np.zeros(Nall, bool); dn_all[ann_gi[sup == "descending"]] = True
side_of = np.full(Nall, "", dtype=object); side_of[ann_gi] = ann.side.fillna("").astype(str).str.lower().to_numpy()
type_of = np.full(Nall, "", dtype=object); type_of[ann_gi] = ann.cell_type.fillna("").astype(str).to_numpy()
sup_of = np.full(Nall, "", dtype=object); sup_of[ann_gi] = sup
def extract(floor):
    k = w_syn >= floor
    s, d, w = src_all[k], dst_all[k], w_syn[k]
    into = np.zeros(Nall, bool); into[d[cord_mask[s]]] = True; into &= dn_all
    proj = np.zeros(Nall, bool); proj[s[cord_mask[d]]] = True; proj &= dn_all
    return s, d, w, into, proj
s, d, w, dn_into, dn_proj = extract(3)
keep_old = cord_mask | dn_into; keep_new = cord_mask | dn_into | dn_proj
print("n_old", int(keep_old.sum()), "n_new", int(keep_new.sum()), "dn_into", int(dn_into.sum()), "dn_new", int((keep_new & ~keep_old).sum()))
gsign_a = sign_all[s]; gsign_b = np.where(is_glut[s], -np.abs(gsign_a), gsign_a)
vals = np.log1p(w) * gsign_b
emask_o = keep_old[s] & keep_old[d]; emask_n = keep_new[s] & keep_new[d]; added = emask_n & ~emask_o
gi_new = np.where(keep_new)[0]; gi_old = np.where(keep_old)[0]; dn_new_g = gi_new[~np.isin(gi_new, gi_old)]
in_new_cell = np.zeros(Nall, bool); in_new_cell[dn_new_g] = True
tier = np.full(Nall, "", dtype=object)
tier[ann_gi[sup == "motor"]] = "motor"; tier[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = "intrinsic"
tier[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = "vnc_sensory"
cord_of_dst = np.isin(tier[d], ["motor", "intrinsic", "vnc_sensory"])
om = added & in_new_cell[s] & cord_of_dst
outmass = np.zeros(Nall); np.add.at(outmass, s[om], np.abs(vals[om]))
cell_mass = outmass[dn_new_g]; order = np.argsort(-cell_mass); cum = np.cumsum(cell_mass[order]) / cell_mass.sum()
K = int(np.searchsorted(cum, 0.50) + 1); heav = dn_new_g[order[:K]]
ng_desc = heav[~is_glut[heav]]; glut_desc = heav[is_glut[heav]]
print("K", K, "ng", len(ng_desc), "glut", len(glut_desc), "rank25", int(ng_desc[24]), "rank26", int(ng_desc[25]))
tot = cell_mass.sum()
print("--- ng ladder ranks 17-32: rank gi type side mass_share n_out(added,cord) n_in(closure)")
for r in range(16, 32):
    g = int(ng_desc[r]); n_out = int((om & (s == g)).sum()); n_in = int((emask_n & (d == g)).sum())
    print(f"  {r+1:2d} gi {g:6d} {type_of[g]:14s} {side_of[g]:6s} {outmass[g]/tot:.5f} out {n_out:3d} in {n_in:3d}")
def sides(arr): return dict(collections.Counter(side_of[g] for g in arr))
print("side composition: dn_new(560)", sides(dn_new_g), "| heavy77", sides(heav), "| ng58", sides(ng_desc), "| glut19", sides(glut_desc))
print("   ng ranks 1-19", sides(ng_desc[:19]), "| 20-24", sides(ng_desc[19:24]), "| 1-24", sides(ng_desc[:24]), "| 25-29", sides(ng_desc[24:29]), "| 30-58", sides(ng_desc[29:]))
print("   dn_into(728)", sides(np.where(dn_into)[0]))
# mass by side in the wA cohort
for nm, arr in (("ranks 1-24", ng_desc[:24]), ("ranks 1-19", ng_desc[:19]), ("ranks 25-29", ng_desc[24:29])):
    m = collections.defaultdict(float)
    for g in arr: m[side_of[g]] += outmass[g] / tot
    print("   mass share by side,", nm, {k: round(v, 4) for k, v in m.items()})
# DNp33 pair
for g in (1110, 928):
    cin = cord_mask[s] & (d == g)
    allin_raw = (dst_all == g) & cord_mask[src_all]
    print(f"DNp33 gi {g} side {side_of[g]}: dn_into {bool(dn_into[g])} dn_proj {bool(dn_proj[g])} in dn_new {bool(in_new_cell[g])} | cord->DN in-edges (>=3) {int(cin.sum())} syn {sorted(w[cin].tolist(), reverse=True)[:10]} | types {[type_of[x] for x in s[cin]][:6]} sup {[sup_of[x] for x in s[cin]][:6]}")
    co = (s == g) & cord_mask[d]
    print(f"     cord out-edges {int(co.sum())} log-mass {np.abs(vals[co]).sum():.2f} syn total {w[co].sum():.0f}")
# how many DN are in cohort only by a thin margin: dn_into cells whose total cord->DN evidence is a single pair of exactly 3 synapses
thin = 0; one_edge = 0
for g in np.where(dn_into)[0]:
    cin = cord_mask[s] & (d == g); 
    if cin.sum() == 1:
        one_edge += 1
        if w[cin][0] == 3: thin += 1
print("dn_into DNs:", int(dn_into.sum()), "| with exactly ONE cord->DN pair:", one_edge, "| of which that pair has exactly 3 synapses:", thin)
# floor sensitivity of cohort membership
for fl in (3, 4, 5, 6):
    s2, d2, w2, into2, proj2 = extract(fl)
    new2 = (cord_mask | into2 | proj2) & ~(cord_mask | into2)
    print(f"BANC floor>={fl}: dn_into {int(into2.sum())} dn_proj {int(proj2.sum())} dn_new {int(new2.sum())} | 1110 in dn_new {bool(new2[1110])} | 928 in dn_new {bool(new2[928])} | 319 in dn_new {bool(new2[319])}")
# pool sizes per side
mot = ann[ann.super_class == "motor"]; ptt = mot.peripheral_target_type.fillna("").astype(str).to_numpy(); sm = mot.side.fillna("").astype(str).str.lower().to_numpy()
def cnt(*pats):
    m = np.ones(len(ptt), bool)
    for p in pats: m &= np.array([p in x for x in ptt])
    return {sd: int((m & (sm == sd) & keep_new[mot.gi.to_numpy()]).sum()) for sd in ("left", "right")}
print("pool sizes: Ti flexor", cnt("tibia", "flexor"), "Ti extensor", cnt("tibia", "extensor"), "Tr flexor", cnt("trochanter", "flexor"), "Tr extensor", cnt("trochanter", "extensor"))
