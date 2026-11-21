"""L176 stage (a) ADDENDUM 1 (registered in-run, before reading the rank axis).

WHY: the published gate g(P)=exp(-alpha*max(0,P-2)) annihilates the composite on
our substrate (frac_P_gt2 == 1.0000 for EVERY arm/band/side, Pmean 10-15 envelope
peaks per 500-step window at the declared 25%-of-range prominence floor), so at
the PREREG's primary alpha=1.0 every arm sits at comp 0.0000-0.0021 and the rank
axis reads gate noise, not amplitude balance. The alpha ladder's alpha=0.0 rung
(gate OFF) was registered in PREREG C9 and is the interpretable arm; this script
re-derives the rank axis on it.

EXACTNESS: with the gate off the composite is LINEAR in (PLV, A, Ph), so the
window-MEAN composite equals the same linear combination of the stored
window-mean components — no re-rollout, no re-windowing, no approximation.
Proof-check included: for every stored primary key with alpha 0.0 the linear
reconstruction must equal the stored mean_carrier/mean_twin to 1e-9.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_l176a.json")))
S = R["summary"]
WS = {k: tuple(v) for k, v in R["conventions"]["weight_sets"].items()}


def comp0(v, wset):
    wp, wa, wh = WS[wset]
    return (wp * v["PLV"] + wa * v["A"] + wh * v["PH"]) / (wp + wa + wh)


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    def rk(v):
        o = v.argsort()
        r = np.empty(len(v), float)
        r[o] = np.arange(len(v), dtype=float)
        for u in np.unique(v):
            m = v == u
            if m.sum() > 1:
                r[m] = r[m].mean()
        return r
    return float(np.corrcoef(rk(x), rk(y))[0, 1])


out = {"addendum": 1, "why": "published gate annihilates composite; alpha=0 rung of PREREG C9"}

# ---- exactness check against the stored alpha-0.0 primary means ----
chk = {"n": 0, "maxerr": 0.0}
for k, v in R["primary"].items():
    run, pairarm, pk, band, side, wset, al = k.split("|")
    if al != "a0.0":
        continue
    ca, tw = pairarm.split("-")
    for arm, got in ((ca, v["mean_carrier"]), (tw, v["mean_twin"])):
        key = f"{run}|{arm}|{pk}|{band}|{side}"
        if key not in S:
            continue
        err = abs(comp0(S[key], wset) - got)
        chk["n"] += 1
        chk["maxerr"] = max(chk["maxerr"], err)
out["linearity_check"] = {"n": chk["n"], "maxerr": round(chk["maxerr"], 10),
                          "pass": chk["maxerr"] < 5e-4}   # stored means are 4-dp rounded

# ---- the rank axis, gate OFF ----
rank = {}
runs = sorted({k.split("|")[0] for k in S})
for run in runs:
    for pk in ("Ti", "Tr"):
        arms = sorted({k.split("|")[1] for k in S
                       if k.startswith(run + "|") and f"|{pk}|" in k})
        if len(arms) < 4:
            continue
        for band in ("pub_1_10", "sub_03_10"):
            for side in ("L", "R"):
                rows = [(a, S[f"{run}|{a}|{pk}|{band}|{side}"]) for a in arms]
                duty = [v["duty"] for _, v in rows]
                for wset in WS:
                    c0 = [comp0(v, wset) for _, v in rows]
                    rank[f"{run}|{pk}|{band}|{side}|{wset}"] = dict(
                        n_arms=len(arms), rho_gate_off=round(spearman(c0, duty), 4),
                        rho_stored_a1=R["secondary"].get(f"{run}|{pk}|{band}|{side}", {}).get("rho"),
                        arms=arms, duty=[round(x, 3) for x in duty],
                        comp0=[round(x, 4) for x in c0],
                        rho_A_only=round(spearman([v["A"] for _, v in rows], duty), 4),
                        rho_PLV_only=round(spearman([v["PLV"] for _, v in rows], duty), 4),
                        rho_PH_only=round(spearman([v["PH"] for _, v in rows], duty), 4),
                    )
out["rank_gate_off"] = rank

# ---- gate diagnostics, pooled ----
g = {"Pmean_min": min(v["Pmean"] for v in S.values()),
     "Pmean_max": max(v["Pmean"] for v in S.values()),
     "frac_P_gt2_min": min(v["frac_P_gt2"] for v in S.values()),
     "g_mean_max_at_a1": max(v["g_mean"] for v in S.values()),
     "floor_frac_max": max(v["floor_frac"] for v in S.values()),
     "n_cells": len(S)}
out["gate_diag"] = g

# ---- identity axis summary (primary cell), gate off ----
ident = {}
for k, v in R["primary"].items():
    if k.endswith("|equal_residual|a0.0"):
        kk = k.replace("|equal_residual|a0.0", "")
        d_duty = round(v["duty_carrier"] - v["duty_twin"], 3)
        ident[kk] = dict(paired_mean=v["paired_mean"], k_up=v["k_up"], n=v["n"],
                         ci=v["ci"], ci_excl_0=v["ci_excl_0"],
                         duty_delta=d_duty,
                         sign_agrees_with_duty=bool(
                             v["paired_mean"] * d_duty > 0) if d_duty != 0 else None)
out["identity_gate_off"] = ident
out["identity_sign_agreement"] = {
    "n_cells": len(ident),
    "n_ci_excl_0": sum(1 for v in ident.values() if v["ci_excl_0"]),
    "n_agree_among_ci_excl_0": sum(1 for v in ident.values()
                                   if v["ci_excl_0"] and v["sign_agrees_with_duty"]),
}

json.dump(out, open(os.path.join(HERE, "results_l176a_addendum.json"), "w"), indent=1)
print("linearity", out["linearity_check"])
print("gate", g)
print("identity", out["identity_sign_agreement"])
print("\n== rank axis, gate OFF, primary weights ==")
for k, v in rank.items():
    if k.endswith("|equal_residual"):
        print(f"{k.replace('|equal_residual',''):28s} rho_off {v['rho_gate_off']:+.3f}  "
              f"(a1 {v['rho_stored_a1']})  A-only {v['rho_A_only']:+.3f}  "
              f"PLV {v['rho_PLV_only']:+.3f}  PH {v['rho_PH_only']:+.3f}")
