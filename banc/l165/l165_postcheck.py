"""L165 postcheck: analytic free floor at n=18, Rayleigh p per arm, and the
cross-FILE b65 replication (independent seed batches B33 vs B34).
Zero rollouts, read-only, no RNG.
"""
import json
import math

import numpy as np

B = "/home/t3rpz/critters/peabrain-lab/banc/"
r = json.load(open(B + "l165/results_l165.json"))
CAR, CTL = r["carrier"], r["control"]
n150, n154 = len(r["seeds_l150"]), len(r["seeds_l154"])
assert n150 == n154 == 18

# analytic expected PLV of n iid uniform phases: sqrt(pi)/(2 sqrt(n))
floor = math.sqrt(math.pi) / (2 * math.sqrt(n150))
# Rayleigh: p = exp(-n R^2) (large-n form used in l162/l164 family)
def ray(R, n=18):
    return float(math.exp(-n * R * R))


print(f"free floor E[PLV | uniform, n={n150}] = {floor:.4f}")
print(f"Rayleigh p=.05 threshold R = {math.sqrt(-math.log(0.05)/n150):.4f}")

print("\narm           carr_med  ctl_med   p(carr_med)   p(ctl_med)  "
      "n_carr>floor  n_ctl>floor")
for a, row in r["rows"].items():
    pc = r["per_channel"][a]
    nc = sum(pc[c]["plv"] > floor for c in CAR)
    nt = sum(pc[c]["plv"] > floor for c in CTL)
    print(f"{a:<13} {row['carrier_med']:.4f}   {row['control_med']:.4f}   "
          f"{ray(row['carrier_med']):.2e}     {ray(row['control_med']):.2e}   "
          f"{nc}/8          {nt}/9")

# cross-file replication of the b65 uniqueness (independent seed batches)
b150 = [r["per_channel"]["b65"][c]["plv"] for c in CAR]
b154 = [r["per_channel"]["l154_b65"][c]["plv"] for c in CAR]
d = [abs(x - y) for x, y in zip(b150, b154)]
print(f"\nb65 CROSS-BATCH replication (B33 n=18 vs B34 n=18, disjoint seeds):")
print(f"  carrier med {r['rows']['b65']['carrier_med']:.4f} vs "
      f"{r['rows']['l154_b65']['carrier_med']:.4f}; per-channel max|d| "
      f"{max(d):.4f}, median|d| {float(np.median(d)):.4f}; "
      f"locked {r['rows']['b65']['n_carrier_locked']}/8 vs "
      f"{r['rows']['l154_b65']['n_carrier_locked']}/8")
assert not (set(r["seeds_l150"][2:]) & set(r["seeds_l154"][2:])), "batch overlap"
print("  batch disjointness asserted (anchors 801/901 shared by design)")

# carrier-set portability: does the l157 carrier/control split order ANY arm?
print("\nCARRIER-SET PORTABILITY (carrier_med - control_med):")
for a, row in r["rows"].items():
    print(f"  {a:<13} {row['carrier_med'] - row['control_med']:+.4f}")
inv = [a for a, row in r["rows"].items()
       if row["carrier_med"] < row["control_med"]]
print(f"  INVERTED in {len(inv)}/{len(r['rows'])} arms: {inv}")

# amplitude control: is the lower lock just unreadable amplitude?
print("\nAMPLITUDE CONTROL (median carrier ptp vs l65 readability floor .03):")
for a, row in r["rows"].items():
    print(f"  {a:<13} ptp {row['carrier_ptp_med']:.4f} = "
          f"{row['carrier_ptp_med']/0.03:.1f}x floor, "
          f"carrier_med {row['carrier_med']:.4f}")

out = dict(free_floor=floor,
           rayleigh_R05=math.sqrt(-math.log(0.05) / n150),
           b65_cross_batch=dict(max_abs_d=max(d),
                                med_abs_d=float(np.median(d)),
                                l150=r["rows"]["b65"]["carrier_med"],
                                l154=r["rows"]["l154_b65"]["carrier_med"]),
           carrier_minus_control={a: row["carrier_med"] - row["control_med"]
                                  for a, row in r["rows"].items()},
           inverted_arms=inv)
with open(B + "l165/postcheck.json", "w") as f:
    json.dump(out, f, indent=1)
print("\nwrote l165/postcheck.json")
