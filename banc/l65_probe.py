"""L65 pre-probe: antagonist pool vocab + neuromere-ish column for tiers."""
import pandas as pd

D = "/home/t3rpz/critters/peabrain-lab/banc/data"
ann = pd.read_csv(f"{D}/dv_11845666", sep="\t", low_memory=False)
ann = ann[ann["super_class"].notna()]
mot = ann[ann.super_class == "motor"]
ptt = mot.peripheral_target_type.fillna("")
print("motor target vocab (top 30):")
print(ptt.value_counts().head(30).to_string())
print("\ntrochanter rows:", int(ptt.str.contains("trochanter").sum()))
tr = ptt[ptt.str.contains("trochanter")]
if len(tr):
    print(tr.value_counts().to_dict())
# columns that could serve as leg/neuromere blocks
for c in ["region", "nerve", "cell_sub_class", "body_part_effector"]:
    if c in ann.columns:
        vc = ann[c].fillna("?").astype(str).value_counts()
        print(f"\n{c}: {len(vc)} values, top: {vc.head(8).to_dict()}")
