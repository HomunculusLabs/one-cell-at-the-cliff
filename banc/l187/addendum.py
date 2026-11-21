"""L187 addendum — POST HOC, DESCRIPTIVE, zero rollouts: arithmetic over
results_l187.json (+ the L185 gain-null slope). Two panels the PREREG listed
as descriptive companions: (1) paired contrasts on the continuous 1.4-Hz
middle segment; (2) the sign of the fixed-minus-rematched duty change per
graph, expressed per +0.1% gain. Run from banc/."""
import json
import math

import numpy as np

r = json.load(open("l187/results_l187.json"))
assert r["status"] == "FINAL"
rows = dict(r["arms"])
rows["cutwA"] = r["base"]
T975_15 = 2.131


def paired(a, b, key):
    d = np.array(rows[a][key]) - np.array(rows[b][key])
    se = d.std(ddof=1) / math.sqrt(len(d))
    return dict(a=a, b=b, mean_a=round(float(np.mean(rows[a][key])), 3),
                mean_b=round(float(np.mean(rows[b][key])), 3),
                diff=round(float(d.mean()), 3),
                ci95=[round(float(d.mean() - T975_15 * se), 3),
                      round(float(d.mean() + T975_15 * se), 3)],
                n_pos=int((d > 0).sum()), n_neg=int((d < 0).sum()))


fast = [paired(a, b, "duty14") for a, b in (
    ("sc25", "cutwA"), ("sc25F", "cutwA"), ("rcut", "cutwA"), ("rcutF", "cutwA"),
    ("rsilW", "cutwA"), ("pp", "cutwA"), ("ppF", "cutwA"), ("occ", "cutwA"),
    ("occF", "cutwA"), ("occ", "sc25"), ("occF", "sc25F"), ("occ", "rcut"),
    ("occF", "rcutF"), ("pp", "sc25"), ("ppF", "sc25F"))]
gain = []
for g, f, carrier_present in (("sc25", "sc25F", False), ("pp", "ppF", False),
                              ("occ", "occF", False), ("sc40", "sc40F", True),
                              ("rcut", "rcutF", True)):
    dg = rows[g]["gain_delta_pct"]                 # rematched minus fixed, %
    c = paired(g, f, "dutyR")
    gain.append(dict(graph=g, carrier_present=carrier_present,
                     rematch_shift_pct=round(dg, 3),
                     rematched_minus_fixed=c["diff"], ci95=c["ci95"],
                     slope_per_0p1pct=round(c["diff"] / (dg * 10), 4)))
out = dict(note="POST HOC / DESCRIPTIVE (not registered contrasts)",
           fast_1p4Hz_paired=fast, gain_form_slopes=gain,
           base_graph_gain_null_slope_b40=r["gain_null_slope_b40"],
           relay_rate=dict(base=r["base"]["x_relay"], sc25=rows["sc25"]["x_relay"],
                           sc25F=rows["sc25F"]["x_relay"], sc40=rows["sc40"]["x_relay"],
                           sc40F=rows["sc40F"]["x_relay"], pp=rows["pp"]["x_relay"],
                           ppF=rows["ppF"]["x_relay"]),
           g74914_rate={a: rows[a]["x_74914"] for a in rows})
json.dump(out, open("l187/addendum.json", "w"), indent=1)
print("1.4-Hz middle segment, paired (a - b), 16 seeds")
for c in fast:
    print(f"  {c['a']:6s} - {c['b']:6s} {c['mean_a']:.3f} vs {c['mean_b']:.3f} "
          f"diff {c['diff']:+.3f} ci {c['ci95']} pos/neg {c['n_pos']}/{c['n_neg']}")
print("rematched - fixed duty per graph (slope per +0.1% gain); base-graph "
      f"gain-null slope (B40) {r['gain_null_slope_b40']:+.4f}")
for g in gain:
    print(f"  {g['graph']:5s} carrier_present={g['carrier_present']!s:5s} shift "
          f"{g['rematch_shift_pct']:+.3f}% d {g['rematched_minus_fixed']:+.3f} "
          f"ci {g['ci95']} slope {g['slope_per_0p1pct']:+.4f}")
print("relay rate", out["relay_rate"])
