#!/usr/bin/env python3
"""L104 ADDENDUM 1: circular clock baseline + global-normalised population
reads. Registered in lane/l104/PREREG.md (ADDENDUM 1) before this ran.
Read-only, CPU."""
import json
import os
import sys
from datetime import datetime

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "lane", "archive"))
sys.path.insert(0, HERE)
import load_brain_states as L                      # noqa: E402
from l104_probe import populations, auc            # noqa: E402

SEED = 104


def arc_classifier(h, y):
    """Best accuracy of 'hour in circular arc => class 1' over all arcs."""
    best = (0.0, None, None)
    grid = np.arange(0, 24, 0.5)
    for s in grid:
        for w in np.arange(0.5, 24.0, 0.5):
            inarc = ((h - s) % 24.0) < w
            acc = float((inarc.astype(int) == y).mean())
            if acc > best[0]:
                best = (acc, float(s), float(w))
    return {"acc": best[0], "start": best[1], "width": best[2]}


def main():
    ps = [p for p in L.pairs() if p["intent"]]
    hours = np.array([datetime.fromisoformat(p["captured_at"]).hour
                      + datetime.fromisoformat(p["captured_at"]).minute / 60.0
                      for p in ps])
    intents = np.array([p["intent"] for p in ps])
    n = len(ps)

    pops, rand, n_nodes = populations()
    allpops = dict(pops)
    allpops.update(rand)

    gmean = np.zeros(n)
    means = {k: np.zeros(n) for k in allpops}
    for i, p in enumerate(ps):
        d = torch.load(p["pt"], map_location="cpu", weights_only=False)
        X = d["X"].numpy().astype(np.float64).ravel()
        gmean[i] = float(X.mean())
        for k, ix in allpops.items():
            means[k][i] = float(X[ix].mean())
        del d, X

    rng = np.random.default_rng(SEED)
    out = {"n": n, "seed": SEED,
           "gmean": {"min": float(gmean.min()), "max": float(gmean.max()),
                     "ratio": float(gmean.max() / gmean.min())},
           "contrasts": {}}

    def nulls(score, y, c0, c1, key, norm):
        obs = abs(auc(score, y) - 0.5)
        yy = y.copy()
        cnt = 0
        for _ in range(2000):
            rng.shuffle(yy)
            if abs(auc(score, yy) - 0.5) >= obs:
                cnt += 1
        p1 = (cnt + 1) / 2001.0
        hits, tot = 0, 0
        for sh in range(1, n):
            lab = np.roll(intents, sh)
            mm = (lab == c0) | (lab == c1)
            y2 = (lab[mm] == c1).astype(int)
            if y2.sum() < 3 or (1 - y2).sum() < 3:
                continue
            tot += 1
            s2 = (means[key][mm] / gmean[mm]) if norm else means[key][mm]
            if abs(auc(s2, y2) - 0.5) >= obs:
                hits += 1
        return p1, ((hits + 1) / (tot + 1.0) if tot else float("nan"))

    for cname, (c0, c1) in {"stay_vs_settle": ("stay", "settle"),
                            "stay_vs_to_fence": ("stay", "to_fence")}.items():
        m = (intents == c0) | (intents == c1)
        y = (intents[m] == c1).astype(int)
        res = {"n_pos": int(y.sum()), "n_neg": int((1 - y).sum()),
               "majority": float(max(y.sum(), (1 - y).sum()) / m.sum())}
        # A1 clock baselines
        res["arc"] = arc_classifier(hours[m], y)
        res["hour_linear_auc"] = auc(hours[m], y)
        res["circ_midnight_auc"] = auc(np.minimum(hours[m], 24 - hours[m]), y)
        res["hours_pos"] = sorted(round(float(x), 1) for x in hours[m][y == 1])
        res["hours_neg"] = sorted(round(float(x), 1) for x in hours[m][y == 0])
        # A2 whole-brain level
        a_g = auc(gmean[m], y)
        p1g, p2g = nulls(gmean[m], y, c0, c1, "CX", False)   # key unused
        res["whole_brain"] = {"auc": a_g, "d": abs(a_g - 0.5)}
        res["pops_norm"] = {}
        for k in allpops:
            s = means[k][m] / gmean[m]
            a = auc(s, y)
            p1, p2 = nulls(s, y, c0, c1, k, True)
            res["pops_norm"][k] = {"auc": a, "d": abs(a - 0.5),
                                   "p1": p1, "p2": p2}
        out["contrasts"][cname] = res

    # re-read C4 on the normalised instrument
    def spec(res, name, base):
        mx = max(res["pops_norm"]["rand_%s_%d" % (base, j)]["d"]
                 for j in range(5))
        return {"named_d": res["pops_norm"][name]["d"], "max_rand_d": mx,
                "pass": bool(res["pops_norm"][name]["d"] > mx)}
    ss = out["contrasts"]["stay_vs_settle"]
    tf = out["contrasts"]["stay_vs_to_fence"]
    out["C4_normalised"] = {
        "stay_vs_settle_CX": spec(ss, "CX", "CX"),
        "stay_vs_settle_DN_all": spec(ss, "DN_all", "DN_all"),
        "stay_vs_to_fence_CX": spec(tf, "CX", "CX"),
        "stay_vs_to_fence_DN_all": spec(tf, "DN_all", "DN_all")}
    out["A_P1_arc_ge_95"] = bool(ss["arc"]["acc"] >= 0.95)
    out["A_P2_wholebrain_ge_99"] = bool(ss["whole_brain"]["auc"] >= 0.99)
    out["A_P3_CX_norm_retains"] = bool(ss["pops_norm"]["CX"]["d"] >= 0.20)

    with open(os.path.join(HERE, "results_l104_add1.json"), "w") as f:
        json.dump(out, f, indent=1)

    print("global mean activity: %.6f .. %.6f (ratio %.3f)"
          % (out["gmean"]["min"], out["gmean"]["max"], out["gmean"]["ratio"]))
    for cname, res in out["contrasts"].items():
        print("\n== %s (pos n=%d, neg n=%d, majority %.3f)"
              % (cname, res["n_pos"], res["n_neg"], res["majority"]))
        print("   CLOCK arc: acc %.3f (start %.1f h, width %.1f h) | "
              "hour-linear AUC %.3f | circ-midnight AUC %.3f"
              % (res["arc"]["acc"], res["arc"]["start"], res["arc"]["width"],
                 res["hour_linear_auc"], res["circ_midnight_auc"]))
        print("   pos hours:", res["hours_pos"])
        print("   neg hours:", res["hours_neg"])
        print("   WHOLE-BRAIN mean AUC %.4f" % res["whole_brain"]["auc"])
        print("   --- global-normalised (pop_mean / whole_brain_mean) ---")
        for k in ["CX", "DN_all", "DN_left", "DN_right", "KC", "DAN",
                  "rand_CX_0", "rand_DN_all_0"]:
            v = res["pops_norm"][k]
            print("   %-13s AUC %.3f  d %.3f  p1 %.4f  p2 %.3f"
                  % (k, v["auc"], v["d"], v["p1"], v["p2"]))
        mx = {b: max(res["pops_norm"]["rand_%s_%d" % (b, j)]["d"]
                     for j in range(5)) for b in ("CX", "DN_all")}
        print("   rand max d (normalised):", {b: round(mx[b], 3) for b in mx})
    print("\nC4 (normalised):", json.dumps(out["C4_normalised"], indent=1))
    print("A-P1 arc>=.95:", out["A_P1_arc_ge_95"],
          "| A-P2 wholebrain>=.99:", out["A_P2_wholebrain_ge_99"],
          "| A-P3 CX-norm retains:", out["A_P3_CX_norm_retains"])


if __name__ == "__main__":
    main()
