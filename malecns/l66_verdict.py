"""L66 verdict re-derivation from STORED artifacts (results_l66.json + raw npz).
PREREG ADDENDUM 1: C0P corrected anchor = first_div == delay+1 (2-hop pool
visibility; l64 stored artifact carries the same +1 for every cell).
"""
import json

import numpy as np

d = json.load(open("l66/results_l66.json"))
SEEDS = d["seeds"]
CFG_DELAY = {"g01_d05_m": 5, "sham_d05m": 5, "n005_d03_m": 3, "n005_d04_m": 4,
             "n005_d06_m": 6, "n005_d08_m": 8, "n015_d03_m": 3, "n015_d04_m": 4,
             "n015_d06_m": 6, "n015_d08_m": 8}
fd = d["first_div"]
bad = {k: (v, CFG_DELAY["_".join(k.split("_")[:-1])])
       for k, v in fd.items() if v != CFG_DELAY["_".join(k.split("_")[:-1])] + 1}
c0p_fixed = not bad
r64 = json.load(open("l64/results.json"))
fd_l64_match = all(fd[f"g01_d05_m_{s}"] == r64["first_div"][f"g01_d05_m_{s}"]
                   for s in (11, 22, 33))
# prefix exactness on raw traces: fb vs open, steps [0, delay+1)
z = np.load("l66/raw_l66.npz")
pre_ok = all(
    float(np.abs(z[f"mm_g01_d05_m_{s}"][:6] - z[f"mm_hynohop_{s}"][:6]).max()) == 0.0
    and float(np.abs(z[f"mm_g01_d05_m_{s}"][6] - z[f"mm_hynohop_{s}"][6]).max()) > 0.0
    for s in SEEDS)

fb, sh, neis, op = d["fb"], d["sham"], d["neighbors"], d["open"]
lift = np.array(fb["lift"])
g1 = dict(pos=int((lift > 0).sum()), wilson=fb["pwilson"],
          lift_fb=fb["lift_mean"], lift_sham=sh["lift_mean"],
          pass_G1=bool((lift > 0).sum() >= 11 and sh["lift_mean"] <= 0.5 * fb["lift_mean"]))
carries = {a: bool(b["lift_mean"] >= 0.05 and b["pos"] >= 11 and b["lock_ok"]
                   and b["dm_min"] > 0) for a, b in neis.items()}
n_carry = sum(carries.values())
g2 = "BASIN" if n_carry >= 5 else ("POINT" if n_carry <= 2 else "MIXED")
miss = [i for i, v in enumerate(fb["lift"]) if v <= 0]
p3 = dict(n=len(miss),
          anatomy=[dict(seed=SEEDS[i], SL=fb["SL"][i], SR=fb["SR"][i],
                        sl_marginal=fb["SL"][i] < fb["SR"][i]) for i in miss],
          pass_P3=bool(len(miss) == 0 or
                       sum(fb["SL"][i] < fb["SR"][i] for i in miss) * 3 >= 2 * len(miss)))
out = dict(c0p_fixed_pass=bool(c0p_fixed), n_viol=len(bad),
           fd_l64_match=bool(fd_l64_match), prefix_exact=bool(pre_ok),
           anchors_original=d["anchors"], G1=g1,
           G2=dict(carries=carries, n_carry=n_carry, verdict=g2), P3=p3,
           fb_mean_SL=round(float(np.mean(fb["SL"])), 3),
           fb_mean_SR=round(float(np.mean(fb["SR"])), 3),
           open_mean_SL=round(float(np.mean(op["SL"])), 3),
           open_mean_SR=round(float(np.mean(op["SR"])), 3),
           wired_dead=d["wired_dead"], dm_min=fb["dm_min"])
with open("l66/verdict_l66.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
