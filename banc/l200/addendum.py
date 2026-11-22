"""L200 addendum — POST HOC, descriptive (written after the FINAL verdict was
read). Zero rollouts: stored results_l200.json / results_l198.json only.
(1) ru2 left flip pooled over its two batches (B43 L198 + B44 L200);
(2) right-side rows vs base for every arm (the registered table prints left);
(3) the double-removal right-side occlusion: l2c vs sc25, chopped + 1.4-Hz;
(4) clamp arm: left contrast and what the carrier's rise does."""
import json, math
import numpy as np
r = json.load(open("l200/results_l200.json")); r8 = json.load(open("l198/results_l198.json"))
assert r["status"] == "FINAL" and r8["status"] == "FINAL"
T = 2.131
def paired(x, y):
    d = np.array(x, float) - np.array(y, float); mu = float(d.mean()); h = T * float(d.std(ddof=1)) / math.sqrt(len(d))
    return dict(mean=round(mu, 4), ci95=[round(mu - h, 4), round(mu + h, 4)])
A, B = r["arms"], r["base"]
out = {}
L = np.array(r8["arms"]["ru2"]["dutyL"] + A["l2"]["dutyL"]); bL = np.array(r8["base"]["dutyL"] + B["dutyL"])
out["ru2_left_pooled"] = dict(n=len(L), k=int((L >= .5).sum()), mean=round(float(L.mean()), 3), min_seed=float(L.min()),
                              base_k=int((bL >= .5).sum()), base_mean=round(float(bL.mean()), 3), base_max_seed=float(bL.max()),
                              batches=dict(B43=[r8["arms"]["ru2"]["kL"], r8["arms"]["ru2"]["meanL"]], B44=[A["l2"]["kL"], A["l2"]["meanL"]]),
                              x_carrier=dict(B43=[r8["base"]["x_carrier"], r8["arms"]["ru2"]["x_carrier"]], B44=[B["x_carrier"], A["l2"]["x_carrier"]]),
                              xcar_paired_B44=A["l2"]["xcar_vs_base"])
out["right_vs_base"] = {a: dict(kR=A[a]["kR"], meanR=A[a]["meanR"], cls=A[a]["clsR"], d=A[a]["R_vs_base"]["mean"], ci95=A[a]["R_vs_base"]["ci95"], mean14R=A[a]["mean14R"]) for a in A}
out["occlusion_right"] = dict(
    sc25=dict(kR=A["sc25"]["kR"], meanR=A["sc25"]["meanR"], mean14R=A["sc25"]["mean14R"], k14R=A["sc25"]["k14R"]),
    l2c=dict(kR=A["l2c"]["kR"], meanR=A["l2c"]["meanR"], mean14R=A["l2c"]["mean14R"], k14R=A["l2c"]["k14R"]),
    l2cF=dict(kR=A["l2cF"]["kR"], meanR=A["l2cF"]["meanR"], mean14R=A["l2cF"]["mean14R"]),
    chopped_l2c_minus_sc25=paired(A["l2c"]["dutyR"], A["sc25"]["dutyR"]),
    mid14_l2c_minus_sc25=paired(A["l2c"]["duty14R"], A["sc25"]["duty14R"]),
    chopped_l2c_minus_l2=paired(A["l2c"]["dutyR"], A["l2"]["dutyR"]),
    chopped_l2c_minus_base=paired(A["l2c"]["dutyR"], B["dutyR"]),
    n_seeds_l2c_below_sc25=int((np.array(A["l2c"]["dutyR"]) < np.array(A["sc25"]["dutyR"])).sum()),
    l198_sc25F_other_batch=dict(kR=r8["arms"]["sc25F"]["kR"], meanR=r8["arms"]["sc25F"]["meanR"], mean14=r8["arms"]["sc25F"]["mean14"]),
    x_ru2=dict(base=B["x_ru2"], sc25=A["sc25"]["x_ru2"]),
    left_sc25_vs_base=A["sc25"]["L_vs_base"], left_l2c_minus_sc25=paired(A["l2c"]["dutyL"], A["sc25"]["dutyL"]))
out["clamp"] = dict(left_l2k_minus_l2=paired(A["l2k"]["dutyL"], A["l2"]["dutyL"]), left_l2kF_minus_l2F=paired(A["l2kF"]["dutyL"], A["l2F"]["dutyL"]),
                    retained=r["retained_fraction"], x_carrier=dict(l2=A["l2"]["x_carrier"], l2k=A["l2k"]["x_carrier"], base=B["x_carrier"]),
                    n_seeds_l2k_ge_l2=int((np.array(A["l2k"]["dutyL"]) >= np.array(A["l2"]["dutyL"])).sum()))
out["twins"] = {a: dict(left=[A[a]["kL"], A[a]["meanL"]], right=[A[a]["kR"], A[a]["meanR"]], dL=A[a]["L_vs_base"], dR=A[a]["R_vs_base"], gain_d=round(A[a]["gain_delta_pct"], 3),
                        x_carrier=A[a]["x_carrier"]) for a in ("lt1", "lt1F", "lt2", "lt2F", "l2h")}
json.dump(out, open("l200/addendum.json", "w"), indent=1)
print(json.dumps(out, indent=1))
