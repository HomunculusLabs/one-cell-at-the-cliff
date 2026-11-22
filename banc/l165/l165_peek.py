import numpy as np, json, os
B="/home/t3rpz/critters/peabrain-lab/banc/"
z=np.load(B+"l150/raw_l150.npz")
ks=list(z.keys())
print("n_keys",len(ks))
# group by prefix
import re
from collections import Counter
pref=Counter()
for k in ks:
    pref[k.split("_")[0]]+=1
print("prefixes",dict(pref))
for k in ks[:40]:
    print(" ",k, z[k].shape, z[k].dtype)
print("...")
st=json.load(open(B+"l150/static.json"))
print("STATIC KEYS",list(st.keys()))
print(json.dumps(st,indent=1)[:2000])
