#!/usr/bin/env python3
"""t287 survey 3 (L294): full record of the types the analysis loop will walk.
READ-ONLY. Structure only -- prints NO covariate against NO effect."""
import json, os, math
import numpy as np

B = os.path.expanduser("~/critters/peabrain-lab/banc")
L = lambda p: json.load(open(os.path.join(B, p)))
J = lambda x, n=900: json.dumps(x)[:n]

POP291 = ["s11f1", "s11f2", "s11w1", "s11w2", "s11w3", "s30f1", "s30f2", "s30w1", "s30w2",
          "s30w3", "s46f1", "s46f2", "s46w1", "s46w2", "s46w3", "gc30f", "gh46f"]
POP290 = ["r11k1", "r11k2", "r11k3", "r11k4", "r11k5", "r30k1", "r30k2", "r30k3", "r30k4",
          "r30k5", "r46k1", "r46k2", "r46k3", "r46k4", "r46k5", "rw11", "rw30", "rw46"]

r291, r290 = L("l291/results_l291.json"), L("l290/results_l290.json")
s291 = L("l291/sets.json")
print("results top keys l291:", list(r291.keys()))
print("results top keys l290:", list(r290.keys()))

print("\n### menu: distinct targets / signs / noop")
tg = [m["target"] for m in s291["menu"]]
print(" menu len", len(s291), "distinct targets", len(set(tg)), "signs", sorted(set(m["sign"] for m in s291["menu"])),
      "effective_weight min/max", min(m["effective_weight"] for m in s291["menu"]), max(m["effective_weight"] for m in s291["menu"]))
print(" j->target one-to-one:", len(set(tg)) == len(tg))
print(" log1p identity over the menu: max|ew - log1p(syn)| = %.3g" % max(
    abs(m["effective_weight"] - math.log1p(m["syn"])) for m in s291["menu"]))
print(" menu rows with a NEGATIVE weight:", sum(1 for m in s291["menu"] if m["effective_weight"] < 0 or m["sign"] < 0))
print(" noop js:", s291["noop"], "| noop menu rows:", [s291["menu"][j] for j in s291["noop"]])
print(" random (l290) type/len:", type(s291["random"]).__name__, len(s291["random"]), "| one:", J(s291["random"][0] if isinstance(s291["random"], list) else list(s291["random"].items())[0], 300))
print(" random_draw_order:", J(s291.get("random_draw_order"), 400))
print(" same_set_pairs:", J(s291.get("same_set_pairs"), 400))
print(" raw_boundary_ties_left_out:", J(s291.get("raw_boundary_ties_left_out"), 400))
print(" used full:", J(s291["used"], 700))
print(" raw full:", J(s291["raw"], 700))
print(" rule:", J(s291.get("rule"), 500))

print("\n### arms results: which population names are present, with which fields")
for tag, r, pop in (("l291", r291, POP291), ("l290", r290, POP290)):
    miss = [a for a in pop if a not in r["arms"]]
    print(" ", tag, "missing:", miss)
    for a in pop[:2] + pop[-3:]:
        rec = dict(r["arms"][a])
        ps = rec.pop("per_seed", None)
        print("   [%s] fields=%s" % (a, J(rec, 520)))
        if ps is not None:
            print("      per_seed type %s len %s one=%s" % (type(ps).__name__, len(ps), J(ps[0] if isinstance(ps, list) else list(ps.items())[0], 300)))

print("\n### arms_w* edges record: every key of one metric arm, one group arm")
for tag, ws in (("l291", ("w0", "w1")), ("l290", ("w0", "w1", "w2"))):
    for w in ws:
        ar = L("%s/arms_%s.json" % (tag, w))
        print(" ", tag, w, "top keys:", list(ar.keys()), "| arms_built", len(ar["arms_built"]))
        for a in ar["arms_built"][:1] + ar["arms_built"][-2:]:
            e = ar["edges"][a]
            print("   edges[%s] keys=%s" % (a, list(e.keys())))
            for k, v in e.items():
                if k == "removed":
                    print("      removed len %d | first %s | last %s" % (len(v), J(v[0], 200), J(v[-1], 200)))
                    print("      distinct targets %d | distinct csr_index %d | signs %s" % (
                        len(set(x["target"] for x in v)), len(set(x["csr_index"] for x in v)), sorted(set(x["sign"] for x in v))))
                else:
                    print("      %s: %s" % (k, J(v, 260)))

print("\n### npz arrays (names/shapes only)")
for p in ("l291/raw_w0.npz", "l291/xm_w0.npz", "l290/raw_w0.npz", "l290/xm_w0.npz"):
    z = np.load(os.path.join(B, p), allow_pickle=False)
    ks = list(z.keys())
    print(" ", p, len(ks), "keys; first 14:", [(k, z[k].shape, str(z[k].dtype)) for k in ks[:14]])
