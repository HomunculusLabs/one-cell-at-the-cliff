"""L164 post-check: three control channels show byte-identical PLV_self on
both arms (Pr_aL .271/.271, Pr_bL .191/.191, Sr_aR .152/.152) — test the
mechanistic reading that those pools are bit-identical ACROSS arms, i.e.
disconnected from the mech drive, so their numbers carry no arm
information. Also report the across-arm trace distance for every channel.
"""
import json

import numpy as np

WIN = 6000
z = np.load("l164/raw_l164.npz")
r = json.load(open("l164/results.json"))
SEEDS = [s for s in r["seeds"] if s >= 4201]
CH = list(r["plv_self"].keys())
CH = sorted({k.split("|", 1)[1] for k in CH})

rows = []
for ch in CH:
    d = max(float(np.abs(z[f"{ch}_fix_{s}"][:WIN].astype(np.float64)
                         - z[f"{ch}_rnd_{s}"][:WIN].astype(np.float64)).max())
            for s in SEEDS)
    rows.append((ch, d))
rows.sort(key=lambda x: x[1])
print(f"{'channel':10s} {'max|fix-rnd| over 16 seeds':>28s}  identical?")
ident = []
for ch, d in rows:
    if d == 0.0:
        ident.append(ch)
    print(f"{ch:10s} {d:28.6g}  {'YES' if d == 0.0 else ''}")
print(f"\nbit-identical across arms: {ident}")
json.dump(dict(max_abs_diff={c: d for c, d in rows}, identical=ident),
          open("l164/postcheck.json", "w"), indent=1)
exp = ["Pr_aL", "Pr_bL", "Sr_aR"]
print(f"predicted-from-PLV-equality set {exp} == measured {sorted(ident)}: "
      f"{sorted(ident) == sorted(exp)}")
