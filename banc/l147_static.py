"""L147 STATIC (zero rollouts): forward-walking channel join on all three graphs.

PREREG l147/PREREG.md registered FIRST (before any census number was computed).
Forms verbatim: BANC extraction l138_static.py, male census l138_probe.py,
v783 annotation join L134. Deterministic, no RNG, CPU-only.
"""
import json

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
NAMES = ["DNg100", "DNg97", "BDN2", "oDN1", "DNp33"]
out = {}

# ---------------- BANC v626 (l138_static.py forms verbatim) ----------------
Gf = torch.load("banc_graph.pt", weights_only=False)
ids_all = Gf["ids"].numpy().astype(np.uint64)
Nall = int(Gf["N"])
idx_all = {int(r): i for i, r in enumerate(ids_all)}

ann = pd.read_csv("data/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()].copy()
ann["gi"] = ann["pt_root_id"].astype(np.uint64).map(idx_all)
ann = ann[ann["gi"].notna()]
ann["gi"] = ann["gi"].astype(int)

region = ann.region.fillna("").astype(str).to_numpy()
sup = ann.super_class.fillna("").astype(str).to_numpy()
ann_gi = ann.gi.to_numpy()
cord_cls = np.isin(sup, ["sensory", "ventral_nerve_cord_intrinsic", "motor"])
cord_mask = np.zeros(Nall, bool)
cord_mask[ann_gi[cord_cls & (region == "ventral_nerve_cord")]] = True
dn_mask = np.zeros(Nall, bool)
dn_mask[ann_gi[sup == "descending"]] = True

conn = pd.read_csv("data/dv_11842997", compression="gzip",
                   usecols=["pre_root_id", "post_root_id", "syn_count"])
in_g = (conn["pre_root_id"].astype(np.uint64).isin(idx_all)
        & conn["post_root_id"].astype(np.uint64).isin(idx_all))
conn = conn[in_g]
g_grp = conn.groupby(["pre_root_id", "post_root_id"], sort=False)["syn_count"].sum()
src_all = np.array([idx_all[r] for r, _ in g_grp.index], np.int64)
dst_all = np.array([idx_all[r] for _, r in g_grp.index], np.int64)
w_syn = g_grp.to_numpy(np.float64)

ct = ann.cell_type.fillna("").astype(str).to_numpy()
side = ann.side.fillna("").astype(str).to_numpy()
banc = {}
for nm in NAMES:
    rows = []
    for gi in ann_gi[ct == nm]:
        oe = (src_all == gi) & cord_mask[dst_all]
        ie = (dst_all == gi) & cord_mask[src_all]
        into, proj = bool(ie.sum()), bool(oe.sum())
        rows.append({
            "gi": int(gi), "root": int(ids_all[gi]), "side": side[np.where(ann_gi == gi)[0][0]],
            "out_cord_edges": int(oe.sum()), "out_cord_syn": float(w_syn[oe].sum()),
            "in_cord_edges": int(ie.sum()), "in_cord_syn": float(w_syn[ie].sum()),
            "dn_into": into, "dn_proj": proj, "pure_proj": bool(proj and not into),
            "in_l65": into, "in_closure": bool(into or proj)})
    banc[nm] = rows
    for r in rows:
        print(f"BANC {nm} gi {r['gi']} {r['side']}: OUT->cord {r['out_cord_edges']}e/"
              f"{r['out_cord_syn']:.0f}s IN<-cord {r['in_cord_edges']}e/"
              f"{r['in_cord_syn']:.0f}s l65={r['in_l65']} closure={r['in_closure']}")
# DNp33 control pin (ADDENDUM 1): homologue pair full-graph gis 928 (R) + 1110 (L);
# 319 = l131 ladder rank-26 holder, a different "twin" (vocabulary collision disclosed)
p33 = sorted(r["gi"] for r in banc["DNp33"])
assert p33 == [928, 1110], f"DNp33 BANC pin FAIL {p33}"
n_dn = int(dn_mask.sum())
into_any = np.zeros(Nall, bool)
into_any[dst_all[cord_mask[src_all]]] = True
proj_any = np.zeros(Nall, bool)
proj_any[src_all[cord_mask[dst_all]]] = True
banc["dn_totals"] = {
    "n_descending": n_dn,
    "n_dn_into": int((dn_mask & into_any).sum()),
    "n_dn_proj": int((dn_mask & proj_any).sum()),
    "n_dn_pure_proj": int((dn_mask & proj_any & ~into_any).sum())}
print("BANC DN totals:", banc["dn_totals"])
out["banc"] = banc

# ---------------- MaleCNS v1.0 (l138_probe.py verbatim) ----------------
M = pd.read_feather("../malecns/data/"
                    "body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = M[M["superclass"].notna()].reset_index(drop=True)
mids = lab["bodyId"].to_numpy(np.uint64)
midx = {int(r): i for i, r in enumerate(mids)}
msup = lab["superclass"].astype(str).to_numpy()
mw = pd.read_feather(
    "../malecns/data/"
    "connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
mw = mw[mw["body_pre"].isin(midx) & mw["body_post"].isin(midx)]
msrc = mw["body_pre"].map(midx).to_numpy(np.int64)
mdst = mw["body_post"].map(midx).to_numpy(np.int64)
wv = mw["weight"].to_numpy()
m_cord = np.isin(msup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
m_dn = msup == "descending_neuron"
into = np.zeros(len(mids), bool)
into[mdst[m_cord[msrc]]] = True
into = into & m_dn
proj = np.zeros(len(mids), bool)
proj[msrc[m_cord[mdst]]] = True
proj = proj & m_dn
male = {}
for nm in NAMES:
    rows = []
    for g in np.where(lab["type"].astype(str) == nm)[0]:
        oe = (msrc == g) & m_cord[mdst]
        ie = (mdst == g) & m_cord[msrc]
        rows.append({
            "gi": int(g), "side": str(lab.somaSide.iloc[g]),
            "out_cord_edges": int(oe.sum()), "out_cord_w": float(wv[oe].sum()),
            "in_cord_edges": int(ie.sum()), "in_cord_w": float(wv[ie].sum()),
            "dn_into": bool(into[g]), "dn_proj": bool(proj[g]),
            "pure_proj": bool(proj[g] and not into[g]),
            "in_l65": bool(into[g]), "in_closure": bool(into[g] or proj[g])})
    male[nm] = rows
    for r in rows:
        print(f"MALE {nm} gi {r['gi']} {r['side']}: OUT->cord {r['out_cord_edges']}e/"
              f"{r['out_cord_w']:.0f}w IN<-cord {r['in_cord_edges']}e/"
              f"{r['in_cord_w']:.0f}w l65={r['in_l65']} closure={r['in_closure']}")
assert len(male["DNp33"]) == 2 and len(male["DNg100"]) == 2, "male pin FAIL"
male["dn_totals"] = {
    "n_descending": int(m_dn.sum()),
    "n_dn_into": int(into.sum()), "n_dn_proj": int(proj.sum()),
    "n_dn_pure_proj": int((proj & ~into).sum())}
print("MALE DN totals:", male["dn_totals"])
out["male"] = male

# ---------------- v783 live brain (brain-only; L134 join form) ----------------
v = pd.read_csv("/home/t3rpz/critters/peabrain/data/neuron_annotations.tsv",
                sep="\t", low_memory=False)
v["root_id"] = v["root_id"].astype(np.uint64)
roots783 = set(np.load("/home/t3rpz/critters/peabrain/data/"
                       "proofread_root_ids_783.npy").tolist())
v783 = {}
for nm in NAMES:
    sub = v[v["cell_type"].astype(str) == nm]
    rows = []
    for _, r in sub.iterrows():
        rows.append({
            "root": int(r["root_id"]), "side": str(r["side"]),
            "super_class": str(r["super_class"]),
            "in_brain_graph": int(r["root_id"]) in roots783,
            "top_nt": str(r["top_nt"]), "synonyms": str(r["synonyms"])[:120],
            "hemibrain_type": str(r["hemibrain_type"])})
    v783[nm] = rows
    for r in rows:
        print(f"v783 {nm} {r['side']} sc={r['super_class']} nt={r['top_nt']} "
              f"graph={r['in_brain_graph']} hbt={r['hemibrain_type'][:24]} "
              f"syn={r['synonyms'][:60]}")
assert len(v783["DNp33"]) == 2 and len(v783["DNg100"]) == 2, "v783 pin FAIL"
out["v783"] = v783

# alias check: oDN1 / BDN2 inside v783 synonym/hemibrain_type vocab?
hay = (v["synonyms"].fillna("").astype(str) + "|" +
       v["hemibrain_type"].fillna("").astype(str)).str.lower()
out["alias_scan_v783"] = {a: int(hay.str.contains(a.lower()).sum())
                          for a in ["oDN1", "BDN2"]}

# ---------------- RRN / BPN scan (PREREG interpretation rule) ----------------
def scan(df, cols, tags):
    res = {}
    for c in cols:
        if c not in df.columns:
            continue
        s = df[c].fillna("").astype(str).str.lower()
        for t in tags:
            n = int(s.str.contains(t).sum())
            if n:
                res[f"{c}:{t}"] = n
    return res

tags = ["rrn", "roadrunner", "bpn"]
out["rrn_bpn_scan"] = {
    "v783": scan(v, ["cell_class", "cell_type", "supertype", "synonyms",
                     "nerve", "super_class"], tags),
    "banc": scan(ann, ["super_class", "cell_class", "cell_type"], tags),
    "male": scan(lab, ["superclass", "type"], tags)}
print("RRN/BPN scan:", out["rrn_bpn_scan"])
print("alias scan v783 synonyms|hbt:", out["alias_scan_v783"])

json.dump(out, open("l147/static.json", "w"), indent=1)
print("VERDICT rows: DNg100 BANC cells in_l65:",
      [r["in_l65"] for r in banc["DNg100"]],
      "| DNg97 BANC in_l65:", [r["in_l65"] for r in banc["DNg97"]],
      "| male both names into:",
      {nm: [r["dn_into"] for r in male[nm]] for nm in ["DNg100", "DNg97"]})
print("L147 static COMPLETE")
