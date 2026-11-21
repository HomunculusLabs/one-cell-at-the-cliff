import json

import numpy as np
import pandas as pd

S92 = json.load(open("l92/static.json"))
print("BANC l92 pins: n_old", S92["n_old"], "n_new", S92["n_new"],
      "dn_new", S92["dn_new"])

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
pure_proj = proj & ~into
for g in np.where(lab["type"].astype(str) == "DNp33")[0]:
    oe = (msrc == g) & m_cord[mdst]
    ie = (mdst == g) & m_cord[msrc]
    print(f"male DNp33 gi {g} side {lab.somaSide.iloc[g]}: "
          f"dn_into {bool(into[g])} dn_proj {bool(proj[g])} "
          f"| OUT->cord {int(oe.sum())} edges (w sum {wv[oe].sum():.0f}) "
          f"| IN<-cord {int(ie.sum())} edges")
print(f"male DNs total {int(m_dn.sum())}, dn_into {int(into.sum())} "
      f"({into.sum() / m_dn.sum():.1%}), dn_proj {int(proj.sum())}, "
      f"pure-proj (proj and not into) {int(pure_proj.sum())}")
