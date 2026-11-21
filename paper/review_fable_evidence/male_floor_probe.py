# Reviewer's read-only probe: does the MaleCNS "pure-projection DN" cohort (dn_new) depend on the edge-weight floor?
# Mirrors the extraction logic of banc/l138_static.py (male side) with a pair-weight floor parameter. Writes nothing.
import numpy as np, pandas as pd, json
D = "/home/t3rpz/critters/peabrain-lab/malecns/data/"
M = pd.read_feather(D + "body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = M[M["superclass"].notna()].reset_index(drop=True)
mids = lab["bodyId"].to_numpy(np.uint64)
midx = {int(r): i for i, r in enumerate(mids)}
msup = lab["superclass"].astype(str).to_numpy()
mtyp = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
mw = pd.read_feather(D + "connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
                     columns=["body_pre", "body_post", "weight"])
print("rows in weights file:", len(mw), "| weight min", mw["weight"].min(), "max", mw["weight"].max())
vc = mw["weight"].value_counts().sort_index()
print("weight histogram head:", {int(k): int(v) for k, v in vc.head(6).items()})
print("duplicate (pre,post) pairs:", int(mw.duplicated(["body_pre", "body_post"]).sum()))
mw = mw[mw["body_pre"].isin(midx) & mw["body_post"].isin(midx)]
msrc0 = mw["body_pre"].map(midx).to_numpy(np.int64)
mdst0 = mw["body_post"].map(midx).to_numpy(np.int64)
mwv0 = mw["weight"].to_numpy(np.float64)
N_m = len(mids)
m_cord = np.isin(msup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
m_dn_all = msup == "descending_neuron"
print("labeled cells", N_m, "| DN", int(m_dn_all.sum()), "| cord", int(m_cord.sum()), "| in-graph edges", len(mwv0))
d33 = np.where(mtyp == "DNp33")[0]
for floor in (1, 2, 3, 4, 5):
    keep = mwv0 >= floor
    msrc, mdst, mwv = msrc0[keep], mdst0[keep], mwv0[keep]
    into = np.zeros(N_m, bool); into[mdst[m_cord[msrc]]] = True; into &= m_dn_all
    proj = np.zeros(N_m, bool); proj[msrc[m_cord[mdst]]] = True; proj &= m_dn_all
    keep_old = m_cord | into; keep_new = m_cord | into | proj
    dn_new = np.where(keep_new & ~keep_old)[0]
    added = keep_new[msrc] & keep_new[mdst] & ~(keep_old[msrc] & keep_old[mdst])
    in_new = np.zeros(N_m, bool); in_new[dn_new] = True
    om = added & in_new[msrc] & m_cord[mdst]
    outmass = np.zeros(N_m); np.add.at(outmass, msrc[om], np.log1p(np.abs(mwv[om])))
    cm = outmass[dn_new]; order = np.argsort(-cm)
    K = int(np.searchsorted(np.cumsum(cm[order]) / cm.sum(), 0.50) + 1) if cm.sum() > 0 else 0
    d = [dict(side=str(lab["somaSide"].iloc[i]) if "somaSide" in lab else "?", dn_into=bool(into[i]), dn_proj=bool(proj[i]),
              in_dn_new=bool(in_new[i]), n_in_cord_edges=int((m_cord[msrc] & (mdst == i)).sum())) for i in d33]
    print(f"floor>={floor}: edges {int(keep.sum()):,} | DN into {int(into.sum())} proj {int(proj.sum())} | dn_new (pure-projection) {len(dn_new)} | heavy K {K} | DNp33 {json.dumps(d)}")
