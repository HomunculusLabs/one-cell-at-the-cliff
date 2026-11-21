"""L169b2 ADDENDUM (DESCRIPTIVE, post-hoc): the floor-4 laterality swap.

The registered metric is the inherited R-side duty (house classifiers in
l169_verdict.py), and on that axis the verdict is G2_no_transfer: all
three f4 arms sit at kR 0/16. The L-side numbers printed by the same
table are loud and in the OPPOSITE direction, so this file quantifies
them with paired legs and labels them DESCRIPTIVE — post-hoc, not a
registered pass (L162 A2/A3 class). It writes into a separate key of the
results json and touches no registered field.
"""
import json

import numpy as np

import l169b2_verdict as V   # helpers VERBATIM + already CERT-green

z = V.z
B36 = V.B36
F4 = V.F4

rows = {}
for a in F4 + ("cutwA", "cutng25"):
    L, R = V.duty_seeds(z, a, B36, "Ti")
    lbL, ubL = V.wilson(int((L >= .5).sum()), 16)
    rows[a] = dict(meanL=round(float(L.mean()), 3),
                   kL=int((L >= .5).sum()), lbL=lbL, ubL=ubL,
                   meanR=round(float(R.mean()), 3),
                   kR=int((R >= .5).sum()),
                   perseedL=[float(x) for x in L])

L_wA, _ = V.duty_seeds(z, "f4wA", B36, "Ti")
legs = {}
for a in ("f4ng", "f4tw"):
    L_a, _ = V.duty_seeds(z, a, B36, "Ti")
    d = L_a - L_wA
    legs[f"{a}_vs_f4wA"] = dict(mean_paired_dL=round(float(d.mean()), 3),
                                n_up=int((d > 0).sum()),
                                n_down=int((d < 0).sum()))
L_ng, _ = V.duty_seeds(z, "f4ng", B36, "Ti")
L_tw, _ = V.duty_seeds(z, "f4tw", B36, "Ti")
d = L_ng - L_tw
legs["f4ng_vs_f4tw"] = dict(mean_paired_dL=round(float(d.mean()), 3),
                            n_up=int((d > 0).sum()),
                            n_down=int((d < 0).sum()))

print("---- DESCRIPTIVE: B36 Ti LEFT-side duty (n=16) ----")
for a in F4 + ("cutwA", "cutng25"):
    r = rows[a]
    print(f"{a:9s} meanL {r['meanL']:.3f} kL {r['kL']:2d}/16 "
          f"[{r['lbL']:.3f},{r['ubL']:.3f}] | meanR {r['meanR']:.3f} "
          f"kR {r['kR']:2d}/16")
for k, v in legs.items():
    print(f"paired {k}: dL {v['mean_paired_dL']:+.3f} "
          f"up {v['n_up']}/16 down {v['n_down']}/16")

# side-dominance read: which side carries structure on each substrate
dom = {a: ("L" if rows[a]["meanL"] > rows[a]["meanR"] else "R")
       for a in rows}
print("side carrying structure:", dom)

out = json.load(open("l169b2/results_l169b2.json"))
out["addendum_L_descriptive"] = dict(
    label="DESCRIPTIVE, post-hoc — the registered axis is R-side duty "
          "(branch G2_no_transfer). These L-side numbers are reported "
          "because an unreported loud side would misrepresent the "
          "substrate (L46/L107 per-side law); they carry NO registered "
          "claim and no branch depends on them.",
    rows=rows, paired_legs=legs, side_dominance=dom)
json.dump(out, open("l169b2/results_l169b2.json", "w"), indent=1)
print("\nresults_l169b2.json += addendum_L_descriptive")
