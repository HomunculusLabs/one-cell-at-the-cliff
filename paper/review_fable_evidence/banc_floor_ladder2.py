# Reviewer's read-only probe v2: floor sensitivity of the BANC ladder, (A) membership FROZEN at floor 3 (paper's l146 design, as inferred)
# vs (B) membership RE-DERIVED by re-applying the extraction rule under the floor. Mirrors l135_run.py lines 80-203. Writes nothing.
import numpy as np, pandas as pd, torch
B = "/home/t3rpz/critters/peabrain-lab/banc/"
Gf = torch.load(B + "banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64); Nall = int(Gf["N"]); idx_all = {int(r): i for i, r in enumerate(ids_all)}
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
print("pairs:", len(Wn), "| min pair weight:", Wn.min(), "| pairs == 3:", int((Wn == 3).sum()), "| ==4:", int((Wn == 4).sum()))
dn_all = np.zeros(Nall, bool); dn_all[ann_gi[sup == "descending"]] = True
tier_ok = np.zeros(Nall, bool)
tier_ok[ann_gi[sup == "motor"]] = True; tier_ok[ann_gi[sup == "ventral_nerve_cord_intrinsic"]] = True; tier_ok[ann_gi[(sup == "sensory") & (region == "ventral_nerve_cord")]] = True
def members(fl):
    k = Wn >= fl; s, d = S[k], Dd[k]
    into = np.zeros(Nall, bool); into[d[cord_mask[s]]] = True; into &= dn_all
    proj = np.zeros(Nall, bool); proj[s[cord_mask[d]]] = True; proj &= dn_all
    keep_old = cord_mask | into; keep_new = keep_old | proj
    return keep_old, keep_new, int(into.sum()), int(proj.sum())
def ladder(fl, keep_old, keep_new):
    k = Wn >= fl; s, d, w = S[k], Dd[k], Wn[k]
    dn_new = np.where(keep_new & ~keep_old)[0]; in_new = np.zeros(Nall, bool); in_new[dn_new] = True
    added = (keep_new[s] & keep_new[d]) & ~(keep_old[s] & keep_old[d])
    om = added & in_new[s] & tier_ok[d]
    out = np.zeros(Nall); np.add.at(out, s[om], np.log1p(w[om]))
    cm = out[dn_new]; order = np.argsort(-cm); cum = np.cumsum(cm[order]) / cm.sum(); K = int(np.searchsorted(cum, 0.5) + 1)
    heav = dn_new[order[:K]]; ng = heav[~is_glut[heav]]
    closure_edges = int((keep_new[s] & keep_new[d]).sum())
    return dict(dn_new=len(dn_new), K=K, heav=set(int(x) for x in heav), ng=[int(x) for x in ng], n_glut=int(is_glut[heav].sum()), closure_edges=closure_edges)
ko3, kn3, i3, p3 = members(3); L3 = ladder(3, ko3, kn3)
rk = lambda L, c: (L["ng"].index(c) + 1) if c in L["ng"] else None
jac = lambda a, b: round(len(a & b) / len(a | b), 4)
print(f"floor 3 (paper): DN-into {i3} | dn_new {L3['dn_new']} | K {L3['K']} (ng {len(L3['ng'])}, glut {L3['n_glut']}) | closure edges {L3['closure_edges']:,} | carrier rank {rk(L3,1110)} twin {rk(L3,319)}")
for fl in (4, 5):
    A = ladder(fl, ko3, kn3)                      # (A) frozen membership
    ko, kn, i_, p_ = members(fl); R = ladder(fl, ko, kn)   # (B) re-derived membership
    print(f"floor {fl} (A) FROZEN membership : dn_new {A['dn_new']} | K {A['K']} (ng {len(A['ng'])}, glut {A['n_glut']}) | closure edges {A['closure_edges']:,} | carrier rank {rk(A,1110)} twin {rk(A,319)} | heavy Jaccard {jac(A['heav'], L3['heav'])} | ng Jaccard {jac(set(A['ng']), set(L3['ng']))}")
    print(f"floor {fl} (B) RE-DERIVED        : DN-into {i_} | dn_new {R['dn_new']} | K {R['K']} (ng {len(R['ng'])}, glut {R['n_glut']}) | closure edges {R['closure_edges']:,} | carrier rank {rk(R,1110)} twin {rk(R,319)} | heavy Jaccard {jac(R['heav'], L3['heav'])} | ng Jaccard {jac(set(R['ng']), set(L3['ng']))} | of floor-3 ng58, still in ng ladder: {len(set(R['ng']) & set(L3['ng']))} | first-24 overlap: {len(set(R['ng'][:24]) & set(L3['ng'][:24]))}/24")
