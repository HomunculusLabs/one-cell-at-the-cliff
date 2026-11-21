"""L151 followup: name the sheet intermediaries carrying 1110's 2-hop pathway
per pool (why five R-side pools share the cut-invariant 0.10016 share), and
the Ti_eL sheet cells whose DN input the wA cut touches. Zero rollouts.
"""
import json

import numpy as np
import pandas as pd
import torch

exec(open("l151_static.py").read().split("out = {")[0])  # reuse extraction+pools

ann_idx = {int(g): (ct, sd) for g, ct, sd in zip(
    ann.gi.to_numpy(),
    ann.cell_type.fillna("").astype(str).to_numpy(),
    ann.side.fillna("").astype(str).str.lower().to_numpy())}

rows = []
dn_in_g = {}
for gname, (E, keep) in GRAPHS.items():
    if gname == "G2_eAll":
        continue
    dn_present = dn_all & keep
    dn_in = np.zeros(Nall)
    em = E & dn_present[src_all] & T70[dst_all]
    np.add.at(dn_in, dst_all[em], np.abs(vals_all[em]))
    w1110 = np.zeros(Nall)
    em1 = E & (src_all == GI) & T70[dst_all]
    np.add.at(w1110, dst_all[em1], np.abs(vals_all[em1]))
    dn_in_g[gname] = dn_in
    for pk in ("Ti_fL", "Ti_fR", "Ti_eL", "Tr_fR", "Ta_aR", "Sr_bR", "Pr_bR"):
        P = POOL_G[pk]
        e2 = E & T70[src_all] & P[dst_all]
        if not e2.any():
            rows.append((gname, pk, None, 0.0, 0.0, 0))
            continue
        contrib = np.abs(vals_all[e2]) * w1110[src_all[e2]]
        j = int(np.argmax(contrib))
        i = int(src_all[e2][j])
        ct, sd = ann_idx.get(i, ("?", "?"))
        rows.append((gname, pk, f"gi{i}:{ct}:{sd}",
                     float(contrib[j]), float(dn_in[i]), int(e2.sum())))

for r in rows:
    if r[2] is None:
        print(f"{r[0]:11s} {r[1]:5s} NO SHEET->POOL EDGES ({r[5]})")
    else:
        print(f"{r[0]:11s} {r[1]:5s} top_i {r[2]:28s} contrib {r[3]:7.2f} "
              f"dn_in(i) {r[4]:7.2f} n_e2 {r[5]}")

# which sheet cells lost DN input on the cut (Ti_eL dn_tot 235.6 -> 211.4)?
e2L0 = emask_n & T70[src_all] & POOL_G["Ti_eL"][dst_all]
inter = np.unique(src_all[e2L0])
print("\nTi_eL intermediaries (DN input G0 -> G1):")
for i in inter:
    ct, sd = ann_idx.get(int(i), ("?", "?"))
    print(f"  gi{i} {ct}:{sd} dn_in {dn_in_g['G0_closure'][i]:.2f} -> "
          f"{dn_in_g['G1_cutwA'][i]:.2f}")
