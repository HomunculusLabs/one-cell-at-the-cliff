#!/usr/bin/env python3
"""L227 PROBE — expression-form check only. Writes NOTHING. Run before the
card script so an expression-form mismatch cannot halt the real run (L206:
a float-equality claim is a claim about the EXPRESSION, not the operands)."""
import json, numpy as np

B = "/home/t3rpz/critters/peabrain-lab/banc/"
l214 = json.load(open(B + "l214/static.json"))
l208 = json.load(open(B + "l208/static.json"))
add = json.load(open(B + "l214/addendum.json"))

keys = list(l214["cells"].keys())
print("n cells", len(keys))
rA = [l214["cells"][k]["rho"] for k in keys]
rM = [l208["arms"][k]["rho"] for k in keys]

tgtA = l214["q3"]["mean_absrhoA"]
tgtM = l214["q3"]["mean_absrhoM"]
forms = {
    "np.mean(np.abs(arr))": lambda v: float(np.mean(np.abs(np.array(v)))),
    "sum(abs(x))/n py": lambda v: sum(abs(x) for x in v) / len(v),
    "float(np.abs(arr).sum())/n": lambda v: float(np.abs(np.array(v)).sum()) / len(v),
}
for nm, f in forms.items():
    a, m = f(rA), f(rM)
    print(f"  {nm:30s} A exact={a == tgtA} d={a-tgtA:+.3e}  M exact={m == tgtM} d={m-tgtM:+.3e}")

# D
D = l214["q3"]["D"]
for nm, f in forms.items():
    d = f(rA) - f(rM)
    print(f"  D via {nm:24s} exact={d == D} d={d-D:+.3e}")
dv = [abs(a) - abs(b) for a, b in zip(rA, rM)]
for nm, f in {"py sum/n": lambda v: sum(v)/len(v),
              "np.mean": lambda v: float(np.mean(np.array(v)))}.items():
    d = f(dv)
    print(f"  D paired {nm:12s} exact={d == D} d={d-D:+.3e}")

print("sign_agree_floor stored", l214["q3"]["sign_agree_floor"],
      "recomputed >0:", sum(1 for x in rA if x > 0))
print("sign_agree_ceiling stored", l214["q3"]["sign_agree_ceiling"],
      "recomputed >0:", sum(1 for x in rM if x > 0))


def midrank(a):
    a = np.asarray(a, dtype=np.float64)
    lt = (a[..., None, :] < a[..., :, None]).sum(-1)
    eq = (a[..., None, :] == a[..., :, None]).sum(-1)
    return lt + (eq + 1.0) / 2.0


def spear(x, y):
    rx, ry = midrank(x), midrank(y)
    rx = rx - rx.mean(-1, keepdims=True)
    ry = ry - ry.mean(-1, keepdims=True)
    return (rx * ry).sum(-1) / np.sqrt((rx * rx).sum(-1) * (ry * ry).sum(-1))


sp = float(spear(np.array(rA), np.array(rM)))
print("spearman(rhoA,rhoM) mine", repr(sp), "stored",
      repr(add["mirror_test"]["spearman_rhoA_rhoM"]),
      "exact=", sp == add["mirror_test"]["spearman_rhoA_rhoM"])
mA = [l214["cells"][k]["mean_A"] for k in keys]
mM = [l208["arms"][k]["mean_dM"] for k in keys]
sp2 = float(spear(np.array(mA), np.array(mM)))
print("spearman(meanA,mean_dM) mine", repr(sp2), "stored",
      repr(add["mirror_test"]["spearman_meanA_meandM"]),
      "exact=", sp2 == add["mirror_test"]["spearman_meanA_meandM"])
print("n_opposite_sign_rho stored", add["mirror_test"]["n_opposite_sign_rho"],
      "recomputed", sum(1 for a, b in zip(rA, rM) if (a > 0) != (b > 0)))
print("n_opposite_sign_currency stored", add["mirror_test"]["n_opposite_sign_currency"],
      "recomputed", sum(1 for a, b in zip(mA, mM) if (a > 0) != (b > 0)))

# identity tolerance
mx = max(abs(l208["arms"][k]["mean_dM"] + (l208["arms"][k]["lvlL"] - l208["arms"][k]["lvlR"]))
         for k in keys)
mlv = max(max(abs(l208["arms"][k]["lvlL"]), abs(l208["arms"][k]["lvlR"])) for k in keys)
print("identity maxdiff", mx, "4*eps*max|lvl|", 4 * np.finfo(np.float64).eps * mlv,
      "passes:", mx <= 4 * np.finfo(np.float64).eps * mlv)

# duty / S-mean availability
for p in ("l200/results_l200.json", "l202/results_l202.json"):
    d = json.load(open(B + p))["arms"]
    print(p, "arms", list(d.keys()))
    for k, v in d.items():
        print("   ", k, "dutyL", v.get("dutyL"), "dutyR", v.get("dutyR"),
              "meanL", v.get("meanL"), "meanR", v.get("meanR"))
