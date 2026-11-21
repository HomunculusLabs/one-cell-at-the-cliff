# Reviewer's read-only probe: BANC cohort/ladder when membership is RE-DERIVED under a synapse floor (extraction rule of l135_run.py)
import numpy as np, pandas as pd, torch
B = "/home/t3rpz/critters/peabrain-lab/banc/"
Gf = torch.load(B + "banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64); Nall = int(Gf["N"]); idx_all = {int(r): i for i, r in enumerate(ids_all)}
sign_all = Gf["sign"].numpy()
ann = pd.read_csv(B + "data/dv_11845666", sep="\t", low_memory=False); ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all); ann = ann[ann["gi"].notna()]; ann["gi"] = ann["gi"].astype(int)
nt = pd.read_csv(B + "data/dv_11837016", low_memory=False, usecols=["root_626", "neurotransmitter_predicted"])
is_glut = np.zeros(Nall, bool)
for r, name in zip(nt["root_626"].astype(np.uint64), nt["neurotransmitter_predicted"].astype(str).str.lower()):
    j = idx_all.get(int(r))
    if j is not None and name == "glutamate": is_glut[j] = True
region = ann.region.fillna("").astype(str).to_numpy(); sup = ann.super_class.fillna("").astype(str).to_numpy(); ann_gi = ann.gi.to_numpy()
cord_mask = np.zeros(Nall, bool); cord_mask[ann_gi[np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"]) & (region == "ventral_nerve_cord")]] = True
conn = pd.read_csv(B + "data/dv_11842997", compression="gzip", usecols=["pre_root_id", "post_root_id", "syn_count"])
conn = conn[conn["pre_root_id"].astype(np.uint64).isin(idx_all) & conn["post_root_id"].astype(np.uint64).isin(idx_all)]
g = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
S = np.array([idx_all[r] for r, _ in g.index], np.int64); Dd = np.array([idx_all[r] for _, r in g.index], np.int64); Wn = g.to_numpy(np.float64)
dn_all = np.zeros(Nall, bool); dn_all[ann_gi[sup == "descending"]] = True
tier_ok = np.zeros(Nall, bool)
tier_ok[ann_gi[sup == "motor"]] = True; tier_ok[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = True; tier_ok[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = True
base = None
for fl in (3, 4, 5):
    k = Wn >= fl; s, d, w = S[k], Dd[k], Wn[k]
    into = np.zeros(Nall, bool); into[d[cord_mask[s]]] = True; into &= dn_all
    proj = np.zeros(Nall, bool); proj[s[cord_mask[d]]] = True; proj &= dn_all
    keep_old = cord_mask | into; keep_new = keep_old | proj
    dn_new = np.where(keep_new & ~keep_old)[0]; in_new = np.zeros(Nall, bool); in_new[dn_new] = True
    added = (keep_new[s] & keep_new[d]) & ~(keep_old[s] & keep_old[d])
    om = added & in_new[s] & tier_ok[d]
    out = np.zeros(Nall); np.add.at(out, s[om], np.log1p(w[om]))
    cm = out[dn_new]; order = np.argsort(-cm); cum = np.cumsum(cm[order]) / cm.sum(); K = int(np.searchsorted(cum, 0.5) + 1)
    heav = dn_new[order[:K]]; ng = heav[~is_glut[heav]]; gl = heav[is_glut[heav]]
    def rk(cell):
        w_ = np.where(ng == cell)[0]; return int(w_[0]) + 1 if len(w_) else None
    if base is None: base = set(int(x) for x in ng)
    jac = len(base & set(int(x) for x in ng)) / len(base | set(int(x) for x in ng))
    print(f"floor>={fl}: dn_new {len(dn_new)} | K {K} (ng {len(ng)}, glut {len(gl)}) | ng-rank of carrier 1110: {rk(1110)} | twin 319: {rk(319)} | homolog 928: {rk(928)} (in cohort: {bool(in_new[928])}) | ng-set Jaccard vs floor-3: {jac:.3f}")
    if rk(1110):
        r = rk(1110); print("     cells at ranks r-1, r, r+1:", [int(x) for x in ng[max(0, r - 2): r + 1]])
