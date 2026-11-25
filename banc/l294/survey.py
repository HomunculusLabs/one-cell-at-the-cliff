#!/usr/bin/env python3
"""t283 survey: print ONE record of every STORED type in l291/ and l290/ before any
analysis loop is written (the L293 build lesson). Read-only."""
import json, os, hashlib, numpy as np

B = os.path.expanduser("~/critters/peabrain-lab/banc")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]

def brief(v, depth=0):
    if isinstance(v, dict):
        return "dict(%d) keys=%s" % (len(v), list(v.keys())[:12])
    if isinstance(v, list):
        if len(v) and isinstance(v[0], (dict, list)):
            return "list(%d) of %s" % (len(v), type(v[0]).__name__)
        return "list(%d) %s" % (len(v), str(v[:6])[:80])
    if isinstance(v, float):
        return "float %.17g" % v
    return "%s %s" % (type(v).__name__, str(v)[:80])

def show(path, maxkeys=40):
    print("=" * 100)
    print(path, os.path.getsize(path), "B sha", sha(path))
    d = json.load(open(path))
    if isinstance(d, dict):
        for k, v in list(d.items())[:maxkeys]:
            print("  [%s] %s" % (k, brief(v)))
    else:
        print("  top-level", brief(d))
    return d

# ---- L291 ----
r291 = show(f"{B}/l291/results_l291.json")
print("\n--- one record of each l291 results type ---")
for k, v in r291.items():
    if isinstance(v, dict) and v:
        k0 = next(iter(v))
        print(f"  results[{k!r}] -> [{k0!r}] = {json.dumps(v[k0])[:600]}")
    elif isinstance(v, list) and v:
        print(f"  results[{k!r}] -> [0] = {json.dumps(v[0])[:600]}")
    else:
        print(f"  results[{k!r}] = {json.dumps(v)[:300]}")

s291 = show(f"{B}/l291/sets.json")
print("\n--- l291 sets: first record per top key ---")
for k, v in s291.items():
    if isinstance(v, dict) and v:
        k0 = next(iter(v))
        print(f"  sets[{k!r}] -> [{k0!r}] = {json.dumps(v[k0])[:500]}")
    elif isinstance(v, list) and v:
        print(f"  sets[{k!r}] -> [0] = {json.dumps(v[0])[:500]}")
    else:
        print(f"  sets[{k!r}] = {json.dumps(v)[:300]}")

for w in ("w0", "w1"):
    g = show(f"{B}/l291/gains_{w}.json")
    a = show(f"{B}/l291/arms_{w}.json")
    if isinstance(a, dict) and a:
        k0 = next(iter(a))
        v0 = a[k0]
        if isinstance(v0, dict):
            print(f"  arms[{k0!r}] keys={list(v0.keys())}")
            for kk, vv in v0.items():
                print(f"     {kk}: {brief(vv)}")
    p = show(f"{B}/l291/pools_{w}.json")
    n = show(f"{B}/l291/anchors_{w}.json")

# ---- L290 ----
r290 = show(f"{B}/l290/results_l290.json")
print("\n--- one record of each l290 results type ---")
for k, v in r290.items():
    if isinstance(v, dict) and v:
        k0 = next(iter(v))
        print(f"  results[{k!r}] -> [{k0!r}] = {json.dumps(v[k0])[:600]}")
    elif isinstance(v, list) and v:
        print(f"  results[{k!r}] -> [0] = {json.dumps(v[0])[:600]}")
    else:
        print(f"  results[{k!r}] = {json.dumps(v)[:300]}")

s290 = show(f"{B}/l290/sets.json")
print("\n--- l290 sets: first record per top key ---")
for k, v in s290.items():
    if isinstance(v, dict) and v:
        k0 = next(iter(v))
        print(f"  sets[{k!r}] -> [{k0!r}] = {json.dumps(v[k0])[:500]}")
    elif isinstance(v, list) and v:
        print(f"  sets[{k!r}] -> [0] = {json.dumps(v[0])[:500]}")
    else:
        print(f"  sets[{k!r}] = {json.dumps(v)[:300]}")

for w in ("w0", "w1", "w2"):
    g = show(f"{B}/l290/gains_{w}.json")
    a = show(f"{B}/l290/arms_{w}.json")
    if isinstance(a, dict) and a:
        k0 = next(iter(a))
        v0 = a[k0]
        if isinstance(v0, dict):
            print(f"  arms[{k0!r}] keys={list(v0.keys())}")
            for kk, vv in v0.items():
                print(f"     {kk}: {brief(vv)}")
    p = show(f"{B}/l290/pools_{w}.json")
