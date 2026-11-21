import numpy as np, pandas as pd
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
dn = lab["superclass"].to_numpy() == "descending_neuron"
typ = lab["type"].astype(str)
hits = sorted(set(typ[dn & typ.str.startswith("DNp")]))
hitsc = sorted(set(typ[dn & typ.str.startswith("DNc")]))
print("DNp types:", hits[:20])
print("DNc types:", hitsc[:20])
