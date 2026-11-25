#!/usr/bin/env python3
"""tick 287: does the seeded L294 run reproduce? compares run 1 (stored copy) with run 2 on every
number EXCEPT the one field added between them (gates.G2_max_abs_dev_E)."""
import json
import sys

a = json.load(open("results_l294_run1.json"))
b = json.load(open("results_l294.json"))
a["gates"].pop("G2_max_abs_dev_E", None)
b["gates"].pop("G2_max_abs_dev_E", None)
print("G2 max |E_rederived - E_stored| over 37 arms:", b.get("x"), json.load(open("results_l294.json"))["gates"]["G2_max_abs_dev_E"])


def diff(x, y, path=""):
    if isinstance(x, dict) and isinstance(y, dict):
        assert set(x) == set(y), (path, set(x) ^ set(y))
        n = 0
        for k in x:
            n += diff(x[k], y[k], path + "/" + str(k))
        return n
    if isinstance(x, list) and isinstance(y, list):
        assert len(x) == len(y), path
        return sum(diff(p, q, path + "[%d]" % i) for i, (p, q) in enumerate(zip(x, y)))
    if x != y:
        print("  DIFF", path, x, y)
        return 1
    return 0


n = diff(a, b)
leaves = json.dumps(a).count(":")
print("leaves compared (approx): %d | differing leaves: %d" % (leaves, n))
print("same tests/verdict:", a["tests"] == b["tests"] and a["verdict"] == b["verdict"] and a["qvals"] == b["qvals"] and a["predictions"] == b["predictions"])
sys.exit(1 if n else 0)
