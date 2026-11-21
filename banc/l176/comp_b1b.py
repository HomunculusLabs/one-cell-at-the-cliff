"""L176 (b1) follow-up: the SECONDARY rank cell at full precision.

Reason, registered in the ADDENDUM-2 scoring block before this ran: the stage-(a)
secondary cell reads `summary[...]["comp"]`, which is (i) the alpha=1.0 rung,
where g(P) collapses the composite to ~1e-4, and (ii) rounded to 4 decimals at
write time. Both together can quantize the arm ordering into ties. This script
recomputes the rank cell with UNROUNDED composite means at the alpha=0 rung
(ADDENDUM 1's linear-exact rung) and at alpha=1.0, and prints the stage-(a)
magnitudes so the same question can be asked of (a)'s published rhos.

ZERO rollouts; same read-only npz.
"""
import json
import os

import numpy as np

import comp as C
import comp_b1 as B

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = {"note": "L176 (b1) full-precision secondary; alpha=0 rung vs alpha=1"}

    # --- stage (a): how big are the stored composite means? ---
    a = json.load(open(os.path.join(HERE, "results_l176a.json")))
    mags = [v["comp"] for v in a["summary"].values()]
    out["stage_a_comp_magnitudes"] = dict(
        n=len(mags), max=max(mags), min=min(mags),
        n_zero_at_4dp=int(sum(1 for m in mags if m == 0.0)),
        frac_zero_at_4dp=round(sum(1 for m in mags if m == 0.0) / len(mags), 4))
    tie_counts = {}
    for k, v in a["secondary"].items():
        cv = v["comp"]
        tie_counts[k] = dict(n_arms=len(cv), n_distinct=len(set(cv)),
                             rho_stored=v["rho"])
    out["stage_a_secondary_ties"] = tie_counts

    # --- (b1): recompute unrounded ---
    z = np.load(B.NPZ)
    r = json.load(open(B.RES))
    arms = list(r["table"].keys())
    seeds = sorted({int(k.rsplit("_", 1)[1]) for k in z.keys()
                    if k.startswith(f"{B.PAIR}_fR_{arms[0]}_")} - B.ANCHORS)
    store = {}
    for arm in arms:
        dL, dR, comp = [], [], {}
        for s in seeds:
            SL, SR, tr = C.s_arrays(z, arm, s, B.PAIR)
            x, y = C.duty_from_S(SL, SR)
            dL.append(x)
            dR.append(y)
            ag, bg = C.PREF[B.PAIR]
            for band in C.BANDS:
                for side in ("L", "R"):
                    comp.setdefault((band, side), []).append(
                        C.comp_windows(tr[f"{ag}{side}"], tr[f"{bg}{side}"], band))
        store[arm] = dict(dL=np.array(dL), dR=np.array(dR), comp=comp)
        print("  rolled", arm, flush=True)

    sec = {}
    for band in C.BANDS:
        for side in ("L", "R"):
            duty = [float((store[x]["dL"] if side == "L" else store[x]["dR"]).mean())
                    for x in arms]
            for al in (0.0, 1.0):
                cv = [float(np.mean([C.composite(c, C.PRIM_W, al).mean()
                                     for c in store[x]["comp"][(band, side)]]))
                      for x in arms]
                sec[f"{band}|{side}|a{al}"] = dict(
                    arms=arms, rho_full=round(C.spearman(cv, duty), 4),
                    rho_rounded4=round(C.spearman([round(v, 4) for v in cv], duty), 4),
                    n_distinct_rounded4=len({round(v, 4) for v in cv}),
                    comp_full=[float(f"{v:.8g}") for v in cv],
                    duty=[round(v, 3) for v in duty])
    out["secondary_b1_fullprec"] = sec
    json.dump(out, open(os.path.join(HERE, "results_l176b1_prec.json"), "w"), indent=1)
    for k, v in sec.items():
        print(k, "rho_full", v["rho_full"], "rho_round4", v["rho_rounded4"],
              "distinct4", v["n_distinct_rounded4"])
    print("stage (a) comp magnitudes:", out["stage_a_comp_magnitudes"])


if __name__ == "__main__":
    main()
