"""L60 static pre-checks (LANE.md ideas-29 + t80 amendment).

1. Laterality join: vnc_sensory mechano cells by rootSide (somaSide is NaN
   for peripheral somata — measured 3586/3588 NaN).
2. Minnick 2610.33881 input-share conduction floor: L/R mech share onto each
   antagonist pool, 1-hop direct and 2-hop via intrinsic, ABS weights (L21).
   ip = ipsilateral (mech side == pool side), co = contralateral.
"""
import json

import numpy as np
import pandas as pd

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
ids = lab["bodyId"].to_numpy(np.uint64)
idx = {int(r): i for i, r in enumerate(ids)}
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).str.replace("Acc. ", "", regex=False).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()
rside = lab["rootSide"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()

cord = np.isin(sup, ["vnc_sensory", "vnc_intrinsic", "vnc_motor"])
dn_all = sup == "descending_neuron"
w = pd.read_feather(
    "data/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather",
    columns=["body_pre", "body_post", "weight"])
w = w[w["body_pre"].isin(idx) & w["body_post"].isin(idx)]
gsrc = w["body_pre"].map(idx).to_numpy(np.int64)
gdst = w["body_post"].map(idx).to_numpy(np.int64)
gw = np.abs(w["weight"].to_numpy(np.float32))          # ABS (L21 rule)
dn_into = np.zeros(len(ids), bool)
dn_into[gdst[cord[gsrc]]] = True
dn_into &= dn_all
keep = cord | dn_into

motor = np.isin(sup, ["vnc_motor", "cb_motor"]) & keep
tm = pd.Series(typ)
pools = {}
for k in ("Tr", "Ti"):
    f = np.where(motor & tm.isin([f"{k} flexor MN", f"{k.lower()} flexor MN"]))[0]
    e = np.where(motor & (tm == f"{k} extensor MN"))[0]
    pools[f"{k}fL"] = f[side[f] == "L"]
    pools[f"{k}fR"] = f[side[f] == "R"]
    pools[f"{k}eL"] = e[side[e] == "L"]
    pools[f"{k}eR"] = e[side[e] == "R"]

mech_g = np.where((sup == "vnc_sensory")
                  & pd.Series(cls).str.contains("mechano").to_numpy() & keep)[0]
mL = mech_g[rside[mech_g] == "L"]
mR = mech_g[rside[mech_g] == "R"]
mU = mech_g[~np.isin(rside[mech_g], ["L", "R"])]
print(f"mech {len(mech_g)} | rootSide L {len(mL)} R {len(mR)} unkn {len(mU)}")
print(f"join_rate {(len(mL)+len(mR))/len(mech_g):.4f}")

intr = np.where(keep & (sup == "vnc_intrinsic"))[0]
edges_ok = keep[gsrc] & keep[gdst]
hdr = f"{'pool':5s} {'totw':>9s} {'1hLip':>7s} {'1hLco':>7s} {'1hRip':>7s} {'1hRco':>7s} {'2hLip':>7s} {'2hLco':>7s} {'2hRip':>7s} {'2hRco':>7s}"
print(hdr)
rows = []
for pname, pidx in pools.items():
    totm = np.isin(gdst, pidx) & edges_ok
    totw = gw[totm].sum()

    def one_hop(msk):
        m = totm & np.isin(gsrc, msk)
        return gw[m].sum() / max(totw, 1e-9)

    def two_hop(msk):
        m1 = np.isin(gsrc, msk) & np.isin(gdst, intr) & edges_ok
        w_in = np.zeros(len(ids), np.float64)
        np.add.at(w_in, gdst[m1], gw[m1])
        m2 = np.isin(gsrc, intr) & totm
        return float((gw[m2] * w_in[gsrc[m2]]).sum() / max(totw, 1e-9))

    r = dict(pool=pname, totw=float(totw),
             h1_fromL=one_hop(mL), h1_fromR=one_hop(mR),
             h2_fromL=two_hop(mL), h2_fromR=two_hop(mR))
    ipsi, contra = (r["h2_fromL"], r["h2_fromR"]) if "L" in pname \
        else (r["h2_fromR"], r["h2_fromL"])
    r["h2_ipsi"], r["h2_contra"] = ipsi, contra
    r["h2_ipsi_contra_ratio"] = ipsi / max(contra, 1e-9)
    r["h1_ipsi"] = r["h1_fromL"] if "L" in pname else r["h1_fromR"]
    rows.append(r)
    print(f"{pname:5s} {totw:9.0f} {r['h1_fromL']:7.4f} {r['h1_fromR']:7.4f} "
          f"{r['h2_fromL']:9.2f} {r['h2_fromR']:9.2f}  ipsi/co {r['h2_ipsi_contra_ratio']:6.1f}x  1h_ip {r['h1_ipsi']:.4f}")

ip = float(np.mean([x["h2_ipsi"] for x in rows]))
co = float(np.mean([x["h2_contra"] for x in rows]))
ratios = [x["h2_ipsi_contra_ratio"] for x in rows]
ip1 = float(np.mean([x["h1_ipsi"] for x in rows]))
print(f"\nmean 1-hop ipsi direct share {ip1:.4f} (2% floor: Minnick)")
print(f"mean 2-hop ipsi mass {ip:.1f} vs contra {co:.1f} | per-pool ipsi/co "
      f"{min(ratios):.1f}-{max(ratios):.1f}x, all > 1" if all(x > 1 for x in ratios) else "")
json.dump(dict(rows=[{k: (v if k == "pool" else float(v)) for k, v in x.items()}
                     for x in rows],
               nL=int(len(mL)), nR=int(len(mR)), nU=int(len(mU)),
               join_rate=(len(mL) + len(mR)) / len(mech_g),
               mean_1hop_ipsi=ip1, mean_2hop=dict(ip=ip, co=co),
               h2_ratio_min=float(min(ratios)), h2_ratio_max=float(max(ratios))),
          open("l60/l60_static.json", "w"), indent=1)
print("saved l60/l60_static.json")
