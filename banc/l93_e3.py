import json

import numpy as np

r = json.load(open("l93/results_l93.json"))
t = r["table"]
print("arm          df0(seg0 lock)      TiL(noharm)      vsat")
for a, v in t.items():
    print(f"{a:<12} {str(v['df0']):<19} {str(v['TiL']):<16} {str(v['vsat'])}")
print("\nE3:", r["e3_noharm"])
# which arms break what
for a, v in t.items():
    if min(v["TiL"]) <= -0.25:
        print("TiL breach:", a, v["TiL"])
    if max(abs(np.array(v["df0"]))) > 0.10:
        print("lock breach:", a, v["df0"])
