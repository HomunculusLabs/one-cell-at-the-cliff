"""L214 addendum — POST-HOC, UNREGISTERED, ARITHMETIC ONLY.

Why: Q3 registered the head-to-head as mean(|rho_A| - |rho_M|) and scored
H_TIE (D +0.041, p_D .462) while the sign agreement with dominance read
17/20 (floor) vs 4/20 (ceiling). A currency that agrees 4/20 is not noise
(chance is 10/20) — it is INVERTED. The suspicion this tests: A and dM are
near-mirrors of one quantity (L208's own lesson: at a sparse operating
point, saturation margin and aliveness are the same number with opposite
meanings), which would make a MAGNITUDE head-to-head structurally unable to
separate them.

This script performs NO new measurement: it reads the two stored jsons
READ-ONLY (fingerprints asserted before and after) and does arithmetic on
values already certified at float equality by l214_static.py. It writes
only l214/addendum.json and must leave l214/static.json byte-identical.
"""
import json
import math
import os

import numpy as np

PRIOR = {"l214": "l214/static.json", "l208": "l208/static.json"}
FP0 = {k: (os.stat(v).st_size, os.stat(v).st_mtime_ns)
       for k, v in PRIOR.items()}
with open(PRIOR["l214"]) as fh:
    CUR = json.load(fh)
with open(PRIOR["l208"]) as fh:
    PREV = json.load(fh)
assert CUR["branch"]["q3"] == "H_TIE", "parent Q3 drift"
assert CUR["cert"]["cert_flo"] == 40 and CUR["cert"]["cert_rho"] == 100
keys20 = list(CUR["cells"].keys())
assert len(keys20) == 20


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx -= rx.mean()
    ry -= ry.mean()
    den = math.sqrt(float((rx * rx).sum()) * float((ry * ry).sum()))
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


rhoA = np.array([CUR["cells"][k]["rho"] for k in keys20])
rhoM = np.array([PREV["arms"][k]["rho"] for k in keys20])
mA = np.array([CUR["cells"][k]["mean_A"] for k in keys20])
mM = np.array([PREV["arms"][k]["mean_dM"] for k in keys20])

# how near-mirror are the two currencies?
r_rho = spearman(rhoA, rhoM)
r_cur = spearman(mA, mM)
p_rho = float(np.corrcoef(rhoA, rhoM)[0, 1])
p_cur = float(np.corrcoef(mA, mM)[0, 1])
opp_rho = int(sum((a > 0) != (b > 0) for a, b in zip(rhoA, rhoM)))
opp_cur = int(sum((a > 0) != (b > 0) for a, b in zip(mA, mM)))


def binom_le(k, n):
    """P(X <= k) for X ~ Bin(n, 1/2), exact."""
    return float(sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


ag_f = CUR["q3"]["sign_agree_floor"]
ag_c = CUR["q3"]["sign_agree_ceiling"]
OUT = {
    "label": ("POST-HOC, UNREGISTERED, ARITHMETIC ONLY on values already "
              "certified by l214_static.py. No branch depends on it."),
    "mirror_test": {
        "spearman_rhoA_rhoM": r_rho, "pearson_rhoA_rhoM": p_rho,
        "spearman_meanA_meandM": r_cur, "pearson_meanA_meandM": p_cur,
        "n_opposite_sign_rho": opp_rho, "n_opposite_sign_currency": opp_cur,
        "n_cells": 20},
    "sign_binomial": {
        "floor_agree": ag_f, "floor_p_two_tailed": 2 * binom_le(20 - ag_f, 20),
        "ceiling_agree": ag_c, "ceiling_p_two_tailed": 2 * binom_le(ag_c, 20)},
    "reading": "",
}
OUT["reading"] = (
    "The registered Q3 statistic was a MAGNITUDE (mean |rho| difference). "
    "If the two currencies are near-mirrors, |rho| is nearly invariant "
    "between them BY CONSTRUCTION and the magnitude head-to-head cannot "
    "separate them no matter how different their directional content is. "
    "The separating quantity is the SIGN agreement, which the PREREG "
    "reported but did not branch on.")

print("L214 ADDENDUM (post-hoc, arithmetic only)")
print(f"  rho_A vs rho_M over 20 cells: spearman {r_rho:+.4f} "
      f"pearson {p_rho:+.4f} | opposite sign in {opp_rho}/20")
print(f"  mean_A vs mean_dM over 20 cells: spearman {r_cur:+.4f} "
      f"pearson {p_cur:+.4f} | opposite sign in {opp_cur}/20")
print(f"  sign agreement floor {ag_f}/20 p(two-tailed) "
      f"{OUT['sign_binomial']['floor_p_two_tailed']:.5f}; "
      f"ceiling {ag_c}/20 p {OUT['sign_binomial']['ceiling_p_two_tailed']:.5f}")

for k, v in PRIOR.items():
    st = os.stat(v)
    assert (st.st_size, st.st_mtime_ns) == FP0[k], ("prior MUTATED", v)
print("  prior-json fingerprints unchanged")
with open("l214/addendum.json", "w") as fh:
    json.dump(OUT, fh, indent=1)
print("wrote l214/addendum.json")
