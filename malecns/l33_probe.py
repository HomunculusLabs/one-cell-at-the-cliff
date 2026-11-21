"""L33 preflight: read l32 frozen params; check DNg95 + somaSide in the L32 subnetwork."""
import json
import numpy as np
import pandas as pd

r = json.load(open("l32/results_l32.json"))
for arm in ("A", "B"):
    fz = r.get(arm, {}).get("frozen")
    conf = r.get(arm, {}).get("confirm")
    print(arm, "frozen:", None if fz is None else
          {k: (round(v, 8) if isinstance(v, float) else v) for k, v in fz.items() if k in ("g", "beta", "d", "mean_S", "rhythm", "rhythm_f")})
    if conf:
        print(arm, "confirm S:", [p["S"] for p in conf])

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
print("somaSide uniques:", lab["somaSide"].value_counts(dropna=False).to_dict())

ids = set(lab["bodyId"].astype(np.uint64))
w = pd.read_feather("data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
                    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(ids) & w["body_post"].isin(ids)]
idx = {int(r_): i for i, r_ in enumerate(lab["bodyId"].to_numpy(np.uint64))}
sup = lab["superclass"].astype(str).to_numpy()
gsrc = w["body_pre"].map(idx).to_numpy(np.int64)
cord = np.isin(sup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
dn_all = sup == "descending_neuron"
dn_into = np.zeros(len(lab), bool)
gdst = w["body_post"].map(idx).to_numpy(np.int64)
dn_into[gdst[cord[gsrc]]] = True
dn_into &= dn_all
keep = cord | dn_into
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
for t in ("DNg95", "DNg100", "DNg35", "MDN"):
    m = keep & (typ == t)
    print(t, "in sub:", int(m.sum()), dict(pd.Series(side[m]).value_counts()))
mo = keep & np.isin(sup, ["vnc_motor", "cb_motor"])
fl = mo & typ.isin(["Ti flexor MN", "Tr flexor MN"]) if hasattr(typ, "isin") else None
tm = pd.Series(typ)
for j in ("Ti", "Tr"):
    f = keep & mo & tm.isin([f"{j} flexor MN", f"{j.lower()} flexor MN"])
    e = keep & mo & (tm == f"{j} extensor MN")
    print(j, "flexor L/R:", int((f & (side == "L")).sum()), int((f & (side == "R")).sum()),
          "| ext L/R:", int((e & (side == "L")).sum()), int((e & (side == "R")).sum()))
