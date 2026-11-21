import json

import pandas as pd

c = pd.read_csv("l36/census_l36.csv")
fam = c[c.family.isin(["flex", "ext", "jump"])]
mod = fam[fam.cells_dyn > 0].sort_values(["u_max"], ascending=False)
print(f"family types {len(fam)} | viable-modulating {len(mod)} | "
      f"freely_viable {int((fam.u_max > 0).sum())} | "
      f"ceiling-pinned {int(((fam.u_max > 0) & (fam.mean_X >= .95)).sum())} | "
      f"buried<-0.8 {int((fam.u_max <= -.8).sum())} | "
      f"need-amp(-0.8..0] {int(((fam.u_max <= 0) & (fam.u_max > -.8)).sum())}")
print()
print("TOP viable-modulating per family:")
for f in ["flex", "ext", "jump"]:
    t = mod[mod.family == f].head(4)
    print(f"-- {f}: {len(mod[mod.family == f])} types")
    print(t[["dn_type", "n_cells", "u_max", "u_mean", "mean_X", "w_flex",
             "w_ext", "w_jump", "org", "med_hop"]].to_string(index=False))
print()
print("ceiling-pinned family types:")
print(fam[(fam.u_max > 0) & (fam.mean_X >= .95)][["dn_type", "family", "u_max",
                                                  "mean_X"]].to_string(index=False))
print()
print("buried family types (u_max<=-.8):", len(fam[fam.u_max <= -.8]))
print(fam[fam.u_max <= -.8][["dn_type", "family", "u_max", "n_cells"]].head(8).to_string(index=False))
r = json.load(open("l36/results_l36.json"))
print()
print("atlas absent from sub:", r["atlas_types_absent"])
spot = r["spot"]["flex:DNge046"]["0.2"]
print("DNge046@0.2 f_Ti c/a per seed:", [(round(m["f_Ti_c"], 3), round(m["f_Ti_a"], 3)) for m in spot])
spot = r["spot"]["jump:DNg110"]["0.2"]
print("DNg110@0.2 f_Ti c/a per seed:", [(round(m["f_Ti_c"], 3), round(m["f_Ti_a"], 3)) for m in spot])
print("DNge046@0.2 mm_shift:", [round(m["mm_shift"], 4) for m in r["spot"]["flex:DNge046"]["0.2"]])
print("DNge046@0.2 first_div:", [m["first_div"] for m in r["spot"]["flex:DNge046"]["0.2"]])
