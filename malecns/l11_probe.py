"""L11 probe: joinability of looming (LC) and odor (olfactory) channels + side columns."""
import pandas as pd

ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()]
for c in ["type", "hemibrainType", "flywireType"]:
    s = lab[c].astype(str)
    lc = s[s.isin(["LC4", "LC16", "LC11", "LC12"])]
    print(f"{c}: LC looming = {len(lc)}", lc.value_counts().to_dict() if len(lc) else "")
mo = lab[lab["superclass"].isin(["vnc_motor", "cb_motor"])]
dn = lab[lab["superclass"] == "descending_neuron"]
print("motor somaSide:", mo["somaSide"].value_counts(dropna=False).to_dict())
print("motor rootSide:", mo["rootSide"].value_counts(dropna=False).to_dict())
print("DN somaSide:", dn["somaSide"].value_counts(dropna=False).to_dict())
olf = lab[lab["class"] == "olfactory"]
print("olfactory cells:", len(olf), "superclasses:", olf["superclass"].value_counts().to_dict())
vp = lab[lab["superclass"] == "visual_projection"]
print("visual_projection types head:", vp["type"].value_counts().head(8).to_dict())
