#!/usr/bin/env python3
"""L104 probe: does intent separate from population activity in the L102
archive, beyond a shuffle null? Read-only, offline, CPU.

Registered in lane/l104/PREREG.md BEFORE any separation statistic was run.
Run with the peabrain venv python.
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))          # lane/l104
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))     # peabrain
sys.path.insert(0, os.path.join(ROOT, "lane", "archive"))
import load_brain_states as L                              # noqa: E402

SEED = 104
ANN = os.path.join(ROOT, "data", "neuron_annotations.tsv")   # senses.py default


# ---------------------------------------------------------------- populations
def populations():
    """CX / DN / KC / DAN row-index sets on the v783 graph, from senses.py's
    own join rule (cell_class / super_class), rebuilt here WITHOUT loading
    the brain service."""
    d = torch.load(os.path.join(ROOT, "brain_graph.pt"), map_location="cpu",
                   weights_only=False)
    ids = d["ids"].numpy()
    n_nodes = int(len(ids))
    del d
    idx = {int(r): i for i, r in enumerate(ids)}
    ann = ANN
    if not os.path.exists(ann):
        cand = [p for p in (
            os.path.join(ROOT, "Supplemental_file1_neuron_annotations.tsv"),
            os.path.join(ROOT, "data",
                         "Supplemental_file1_neuron_annotations.tsv"),
        ) if os.path.exists(p)]
        if not cand:
            raise SystemExit("annotation TSV not found; looked at %s" % ann)
        ann = cand[0]
    df = pd.read_csv(ann, sep="\t", low_memory=False)
    df = df[df["root_id"].isin(idx)]
    df["row"] = df["root_id"].map(idx)

    def rows(mask):
        return np.sort(df.loc[mask, "row"].to_numpy(np.int64))

    side = df["side"].astype(str)
    dn = df["super_class"] == "descending"
    pops = {
        "CX":       rows(df["cell_class"] == "CX"),
        "DN_all":   rows(dn),
        "DN_left":  rows(dn & side.eq("left")),
        "DN_right": rows(dn & side.eq("right")),
        "KC":       rows(df["cell_class"] == "Kenyon_Cell"),
        "DAN":      rows(df["cell_class"] == "DAN"),
    }
    # C4 specificity control: 5 size-matched random index sets per target
    rng = np.random.default_rng(SEED)
    rand = {}
    for name in ("CX", "DN_all"):
        k = len(pops[name])
        for j in range(5):
            rand["rand_%s_%d" % (name, j)] = np.sort(
                rng.choice(n_nodes, size=k, replace=False))
    return pops, rand, n_nodes


# ---------------------------------------------------------------- statistics
def auc(scores, labels):
    """AUC of `scores` separating labels==1 from labels==0 (rank/Mann-Whitney,
    ties averaged)."""
    s = np.asarray(scores, float)
    y = np.asarray(labels, int)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), float)
    sortd = s[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and sortd[j + 1] == sortd[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def loo_nearest_centroid(F, y):
    """Leave-one-out nearest-centroid accuracy, cosine distance."""
    F = np.asarray(F, float)
    nrm = np.linalg.norm(F, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    U = F / nrm
    y = np.asarray(y)
    classes = np.unique(y)
    correct = 0
    for i in range(len(y)):
        best, bestc = -2.0, None
        for c in classes:
            m = (y == c)
            m[i] = False
            if not m.any():
                continue
            cen = U[m].mean(axis=0)
            nn = np.linalg.norm(cen)
            sim = float(U[i] @ cen / nn) if nn > 0 else -1.0
            if sim > best:
                best, bestc = sim, c
        correct += int(bestc == y[i])
    return correct / len(y)


# ---------------------------------------------------------------- main
def main():
    ps = [p for p in L.pairs() if p["intent"]]
    assert len(ps) >= 50, "L104 condition not met: n=%d" % len(ps)
    for p in ps:
        assert p["exists"], "pruned .pt referenced: %s" % p["snap"]

    hours, intents = [], []
    for p in ps:
        t = datetime.fromisoformat(p["captured_at"])
        hours.append(t.hour + t.minute / 60.0)          # already local EST
        intents.append(p["intent"])
    hours = np.array(hours)
    intents = np.array(intents)
    n = len(ps)

    pops, rand, n_nodes = populations()
    allpops = dict(pops)
    allpops.update(rand)
    sizes = {k: int(len(v)) for k, v in allpops.items()}

    # ---- load X once, keep only population means + the two named subvectors
    means = {k: np.zeros(n) for k in allpops}
    sub = {k: np.zeros((n, len(allpops[k])), np.float32)
           for k in ("CX", "DN_all", "DN_left", "DN_right")}
    for i, p in enumerate(ps):
        d = torch.load(p["pt"], map_location="cpu", weights_only=False)
        X = d["X"].numpy().astype(np.float64).ravel()
        assert X.shape[0] == n_nodes, (X.shape, n_nodes)
        for k, ix in allpops.items():
            means[k][i] = float(X[ix].mean())
        for k in sub:
            sub[k][i] = X[allpops[k]].astype(np.float32)
        del d, X
    global_mean = np.array([means["CX"][i] for i in range(n)])  # placeholder

    rng = np.random.default_rng(SEED)

    def contrast(c0, c1):
        """Full gate table for one labelled contrast. c1 is the positive class."""
        m = (intents == c0) | (intents == c1)
        y = (intents[m] == c1).astype(int)
        res = {"pos": c1, "neg": c0, "n_pos": int(y.sum()),
               "n_neg": int((1 - y).sum()), "pops": {}}
        # N3 clock baselines (not brain reads)
        res["hour_auc"] = auc(hours[m], y)
        res["order_auc"] = auc(np.arange(n)[m], y)
        res["hour_overlap"] = overlap_frac(hours[m], y)
        for k in allpops:
            s = means[k][m]
            a = auc(s, y)
            # N1 iid label shuffle
            obs = abs(a - 0.5)
            cnt = 0
            yy = y.copy()
            for _ in range(2000):
                rng.shuffle(yy)
                if abs(auc(s, yy) - 0.5) >= obs:
                    cnt += 1
            p1 = (cnt + 1) / 2001.0
            # N2 circular shift of the FULL 73-label sequence
            hits, tot = 0, 0
            for sh in range(1, n):
                lab = np.roll(intents, sh)
                mm = (lab == c0) | (lab == c1)
                yy2 = (lab[mm] == c1).astype(int)
                if yy2.sum() < 3 or (1 - yy2).sum() < 3:
                    continue
                tot += 1
                if abs(auc(means[k][mm], yy2) - 0.5) >= obs:
                    hits += 1
            p2 = (hits + 1) / (tot + 1.0) if tot else float("nan")
            res["pops"][k] = {"auc": a, "d": obs, "p1": p1, "p2": p2,
                              "n_shift": tot, "size": sizes[k]}
        for k in sub:
            res["pops"][k]["loo"] = loo_nearest_centroid(sub[k][m], y)
        res["majority"] = max(res["n_pos"], res["n_neg"]) / float(m.sum())
        return res

    def overlap_frac(h, y):
        """Fraction of samples whose hour lies inside the other class's
        [min,max] hour range — how hour-separable the contrast is."""
        a, b = h[y == 1], h[y == 0]
        if len(a) == 0 or len(b) == 0:
            return float("nan")
        ina = ((a >= b.min()) & (a <= b.max())).mean()
        inb = ((b >= a.min()) & (b <= a.max())).mean()
        return float((ina * len(a) + inb * len(b)) / (len(a) + len(b)))

    out = {"n": n, "seed": SEED, "n_nodes": n_nodes, "sizes": sizes,
           "intent_counts": dict(Counter(intents.tolist())),
           "window": [ps[0]["captured_at"], ps[-1]["captured_at"]],
           "contrasts": {}}
    out["contrasts"]["stay_vs_settle"] = contrast("stay", "settle")
    out["contrasts"]["stay_vs_to_fence"] = contrast("stay", "to_fence")

    # ---- P5 descriptive: DN side asymmetry for directed intents
    asym = (means["DN_left"] - means["DN_right"]) / (
        means["DN_left"] + means["DN_right"] + 1e-12)
    out["dn_asym"] = {k: {"n": int((intents == k).sum()),
                          "mean": float(asym[intents == k].mean()),
                          "sd": float(asym[intents == k].std())}
                      for k in sorted(set(intents.tolist()))}
    out["dn_asym_overall_sd"] = float(asym.std())

    # ---- gate cells, one object each
    ss = out["contrasts"]["stay_vs_settle"]
    tf = out["contrasts"]["stay_vs_to_fence"]
    cx = ss["pops"]["CX"]
    c1 = bool(cx["d"] >= 0.20 and cx["p1"] < 0.05)
    c2 = bool(cx["p2"] < 0.05)
    c3_named = {k: tf["pops"][k] for k in ("CX", "DN_all", "DN_left",
                                           "DN_right")}
    c3 = bool(any(v["d"] >= 0.20 and v["p1"] < 0.05
                  for v in c3_named.values()))
    def spec(res, name, base):
        mx = max(res["pops"]["rand_%s_%d" % (base, j)]["d"] for j in range(5))
        return {"named_d": res["pops"][name]["d"], "max_rand_d": mx,
                "pass": bool(res["pops"][name]["d"] > mx)}
    c4 = {"stay_vs_settle_CX": spec(ss, "CX", "CX"),
          "stay_vs_settle_DN_all": spec(ss, "DN_all", "DN_all"),
          "stay_vs_to_fence_CX": spec(tf, "CX", "CX"),
          "stay_vs_to_fence_DN_all": spec(tf, "DN_all", "DN_all")}
    out["gates"] = {
        "C1_naive_stay_vs_settle_CX": {"pass": c1, "auc": cx["auc"],
                                       "p1": cx["p1"],
                                       "label": "CONFOUNDED by construction"},
        "C2_temporal_null_stay_vs_settle_CX": {"pass": c2, "p2": cx["p2"]},
        "C3_dissociation_stay_vs_to_fence": {"pass": c3,
                                             "named": c3_named},
        "C4_specificity": c4,
    }
    if c1 and not c3:
        branch = "B_CONFOUND_ONLY"
    elif c3 and all(v["pass"] for k, v in c4.items()
                    if k.startswith("stay_vs_to_fence")):
        branch = "B_INTENT_CODE"
    elif c3:
        branch = "B_BULK"
    elif not c1:
        branch = "B_DEAD"
    else:
        branch = "B_CONFOUND_ONLY"
    out["branch"] = branch

    with open(os.path.join(HERE, "results_l104.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ---- report
    print("n=%d  window %s -> %s" % (n, out["window"][0][:16],
                                     out["window"][1][:16]))
    print("sizes:", {k: sizes[k] for k in pops})
    for cname, res in out["contrasts"].items():
        print("\n== %s  (pos=%s n=%d, neg=%s n=%d, majority %.3f)" % (
            cname, res["pos"], res["n_pos"], res["neg"], res["n_neg"],
            res["majority"]))
        print("   CLOCK: hour AUC %.3f | order AUC %.3f | hour-overlap %.3f"
              % (res["hour_auc"], res["order_auc"], res["hour_overlap"]))
        for k in list(pops) + ["rand_CX_0", "rand_DN_all_0"]:
            v = res["pops"][k]
            loo = "  loo %.3f" % v["loo"] if "loo" in v else ""
            print("   %-12s n=%6d  AUC %.3f  d %.3f  p1 %.4f  p2 %.3f (%d sh)%s"
                  % (k, v["size"], v["auc"], v["d"], v["p1"], v["p2"],
                     v["n_shift"], loo))
        mx = {b: max(res["pops"]["rand_%s_%d" % (b, j)]["d"] for j in range(5))
              for b in ("CX", "DN_all")}
        print("   rand max d:", {b: round(mx[b], 3) for b in mx})
    print("\nDN L/R asymmetry (P5, descriptive): overall sd %.4f"
          % out["dn_asym_overall_sd"])
    for k, v in out["dn_asym"].items():
        print("   %-9s n=%2d  mean %+.4f  sd %.4f" % (k, v["n"], v["mean"],
                                                      v["sd"]))
    print("\nGATES:")
    for k, v in out["gates"].items():
        print("  ", k, json.dumps(v)[:300])
    print("BRANCH:", branch)


if __name__ == "__main__":
    main()
