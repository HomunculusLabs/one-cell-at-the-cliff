#!/usr/bin/env python3
"""Tick 287 -- verification + POST-HOC DESCRIPTION only (nothing here gates, nothing registered).
Reads results_l294.json (read-only) and the stored parent artifacts.
 (1) T4's 128-pattern sign-flip null, enumerated one pattern at a time and PRINTED.
 (2) cross-correlation between the two predictors DGAIN and EW_SUM (L227: name the mirror).
 (3) base rate for 'negative dgain -> floor' on the out-of-sample L18 (seen after the fact on L291;
     never registered as a test -> description)."""
import itertools
import json
import math
import os
import sys

import numpy as np

B = os.path.expanduser("~/critters/peabrain-lab/banc")
D = os.path.join(B, "l294")
J = lambda p: json.load(open(os.path.join(B, p)))
R = json.load(open(os.path.join(D, "results_l294.json")))
r291, r290 = J("l291/results_l291.json"), J("l290/results_l290.json")
F = R["F"]
tw = R["twin_pairs"]
u = np.array([math.copysign(1.0, t["dgain"]) * t["dE_F"] for t in tw])   # sign(dgain) * dE
names = [t["bisected"] for t in tw]
S_obs = float(np.mean(u))
cnt = 0
print("T4 enumeration: u_i = sign(dgain_i)*dE_i =", [round(x, 6) for x in u], " S_obs %.6f" % S_obs)
for s in itertools.product([1.0, -1.0], repeat=7):
    S = float(np.dot(np.array(s), u) / 7.0)
    ge = S >= S_obs - 1e-12
    cnt += int(ge)
    if ge or s == tuple([-1.0 if i == 6 else 1.0 for i in range(7)]):
        print("  pattern %s  S %+.6f  %s" % ("".join("+" if x > 0 else "-" for x in s), S, ">= obs" if ge else "<  obs (flip e27 only)"))
print("T4 count >= S_obs: %d / 128 = %.5f   (script stored p_one %.5f)" % (cnt, cnt / 128.0, R["tests"]["T4"]["p_one"]))

# (2) mirror between the two predictors, same stratified midrank machinery
def midrank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort")
    xs = x[o]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[i:j + 1] = 0.5 * (i + j) + 1.0
        i = j + 1
    out = np.empty(len(x))
    out[o] = r
    return out


def pear(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float(a @ b) / math.sqrt(float(a @ a) * float(b @ b))


arms = {a["arm"]: a for a in R["arms"]}
B33 = R["populations"]["B33"]
strata = {}
for a in B33:
    strata.setdefault(arms[a]["size"], []).append(a)
num = 0.0
den = 0.0
print("\nPOSTHOC mirror STRAT-RHO(EW_SUM, DGAIN) on B33 (the two predictors against each other):")
for n in sorted(strata):
    xs = np.array([arms[a]["ew"] for a in strata[n]])
    ys = np.array([arms[a]["dgain"] for a in strata[n]])
    rr = pear(midrank(xs), midrank(ys))
    num += (len(xs) - 1) * rr
    den += len(xs) - 1
    print("  n%d: rho(EW, DGAIN) %+.3f  (k arms %d)" % (n, rr, len(xs)))
print("  strat-rho %+.4f" % (num / den))
for a in B33:
    pass
# (3) floor base rate on L18
L18 = R["populations"]["L290_18"]
neg = [a for a in L18 if arms[a]["dgain"] < 0]
pos = [a for a in L18 if arms[a]["dgain"] >= 0]
fl = lambda a: abs(arms[a]["E_F"]) <= 2.0
a_, b_ = sum(fl(x) for x in neg), len(neg) - sum(fl(x) for x in neg)
c_, d_ = sum(fl(x) for x in pos), len(pos) - sum(fl(x) for x in pos)


def C(n, k):
    return math.comb(n, k)


def ptab(x):   # X = negative-dgain arms among the 7 floor arms: Hypergeom(N=18, K=9 neg, n=7)
    return C(len(neg), x) * C(len(pos), (a_ + c_) - x) / C(18, a_ + c_)


po = ptab(a_)
two = sum(ptab(x) for x in range(0, 8) if ptab(x) <= po + 1e-15)
print("\nPOSTHOC L18 'negative dgain -> floor (|E| <= 2F)': %d of %d negative-dgain arms vs %d of %d others; Fisher two-sided %.3f (unregistered)" % (
    a_, len(neg), c_, len(pos), two))
print("  not at floor despite negative dgain:", [(x, arms[x]["E_F"], arms[x]["dgain"]) for x in neg if not fl(x)])
print("  at floor despite non-negative dgain:", [(x, arms[x]["E_F"], arms[x]["dgain"]) for x in pos if fl(x)])
print("\nparents untouched: results_l290 sha %s | results_l291 sha %s" % (
    R["provenance"]["results_l290_sha256"][:16], R["provenance"]["results_l291_sha256"][:16]))
