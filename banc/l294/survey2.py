#!/usr/bin/env python3
"""t285 survey 2 (L294): the stored records tick 283's survey printed only as
key lists. READ-ONLY. Prints structure only -- NO covariate is scored against
an effect here (the PREREG is written before any such scoring)."""
import json, os

B = os.path.expanduser("~/critters/peabrain-lab/banc")
L = lambda p: json.load(open(os.path.join(B, p)))


def J(x, n=700):
    return json.dumps(x)[:n]


r291 = L("l291/results_l291.json")
print("### L291 results")
print("arms keys (%d): %s" % (len(r291["arms"]), list(r291["arms"].keys())))
a = dict(r291["arms"]["s11f1"])
ps = a.pop("per_seed", None)
print("arms[s11f1] (sans per_seed):", J(a, 900))
print("  per_seed len", None if ps is None else len(ps))
print("twins:", J(r291["twins"], 1500))
print("per_metric[abs] keys:", list(r291["per_metric"]["abs"].keys()))
pm = dict(r291["per_metric"]["abs"])
pm.pop("comparators", None)
print("per_metric[abs] sans comparators:", J(pm, 900))
print("context:", J(r291["context"], 900))
print("means:", J(r291["means"], 600))
print("clear:", J(r291["clear"], 500))

s291 = L("l291/sets.json")
print("\n### L291 sets")
print("menu[0..5]:", J(s291["menu"][:6], 700))
neg = [m for m in s291["menu"] if m["sign"] < 0][:3]
print("menu negative-sign samples (%d of %d negative):" % (sum(1 for m in s291["menu"] if m["sign"] < 0), len(s291["menu"])), J(neg, 500))
print("bands:", J(s291["bands"], 300))
print("used:", J(s291["used"], 300))
print("raw:", J(s291["raw"], 300))
print("noop:", s291["noop"], "| all menu j:", [m["j"] for m in s291["menu"]][:80])
print("menu keys:", list(s291["menu"][0].keys()))
# do the menu ids agree with L290's?
s290 = L("l290/sets.json")
print("menu identical l291==l290:", s291["menu"] == s290["menu"], "| random identical:", s291["random"] == s290["random"], "| used identical:", s291["used"] == s290["used"])
print("l290 sets keys:", list(s290.keys()))
print("l290 contains14:", J(s290["contains14"], 700))
print("l290 eff:", J(s290["eff"], 700))

for tag in ("l291", "l290"):
    print("\n### %s gains / arms / pools" % tag)
    ws = ("w0", "w1") if tag == "l291" else ("w0", "w1", "w2")
    for w in ws:
        g = L("%s/gains_%s.json" % (tag, w))
        print(" gains_%s gain: %s" % (w, J(g["gain"], 900)))
        print("   source: %s" % J(g["source"], 500))
        k0 = next(iter(g["stairs"]))
        print("   stairs[%s] (len %d): %s" % (k0, len(g["stairs"][k0]) if hasattr(g["stairs"][k0], "__len__") else -1, J(g["stairs"][k0], 400)))
        print("   af_final: %s" % J(g["af_final"], 500))
        ar = L("%s/arms_%s.json" % (tag, w))
        print(" arms_%s edges keys (%d): %s" % (w, len(ar["edges"]), list(ar["edges"].keys())))
        k0 = next(iter(ar["edges"]))
        e0 = ar["edges"][k0]
        print("   edges[%s] type %s len %s head %s" % (k0, type(e0).__name__, len(e0), J(e0, 500)))
        if "contains14" in ar:
            print("   contains14:", J(ar["contains14"], 500))
        print("   arms_built:", ar.get("arms_built"), "fixed:", ar.get("fixed"))
    p = L("%s/pools_w0.json" % tag)
    print(" pools sizes:", J(p["sizes"], 700))
    k0 = next(iter(p["pools"]))
    print(" pools[%s] head: %s" % (k0, J(p["pools"][k0], 200)))

r290 = L("l290/results_l290.json")
print("\n### L290 results")
print("arms keys (%d): %s" % (len(r290["arms"]), list(r290["arms"].keys())))
a = dict(r290["arms"]["r11k1"])
ps = a.pop("per_seed", None)
print("arms[r11k1] (sans per_seed):", J(a, 900))
print("  per_seed len", None if ps is None else len(ps))
a = dict(r290["arms"]["gc30"])
ps = a.pop("per_seed", None)
print("arms[gc30] (sans per_seed):", J(a, 900))
print("twins:", J(r290["twins"], 2600))
d = dict(r290["descriptive"])
se = d.pop("single_effects", None)
print("descriptive (sans single_effects):", J(d, 1500))
print("instrument:", J(r290["instrument"], 700))
pm = dict(r290["per_metric"]["abs"])
pm.pop("comparators", None)
print("per_metric[abs] sans comparators:", J(pm, 700))
print("per_metric[abs] comparator keys:", list(r290["per_metric"]["abs"]["comparators"].keys()))
print("gains sample:", J(dict(list(r290["gains"].items())[:6]), 500))
