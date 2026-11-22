"""L177 pre-step v2: structure dump of l65 stored artifacts (read-only)."""
import json
import numpy as np


def walk(o, path="", depth=0):
    if depth > 3:
        return
    if isinstance(o, dict):
        print("  " * depth + f"{path} dict[{len(o)}] keys={list(o.keys())[:12]}")
        for k, v in list(o.items())[:12]:
            walk(v, f"{path}.{k}", depth + 1)
    elif isinstance(o, list):
        print("  " * depth + f"{path} list[{len(o)}]"
              + (f" e0={json.dumps(o[0])[:200]}" if o else ""))
        if o and isinstance(o[0], (dict, list)):
            walk(o[0], path + "[0]", depth + 1)
    else:
        print("  " * depth + f"{path} = {json.dumps(o)[:160]}")


for f in ["l65/scan_l65.json", "l65/results_l65.json"]:
    print("=" * 20, f)
    walk(json.load(open(f)))

z = np.load("l65/raw_l65.npz")
print("\nnpz keys:", list(z.keys()))
for k in list(z.keys()):
    print(" ", k, z[k].shape, z[k].dtype)
