import numpy as np, json, re
from collections import defaultdict
B="/home/t3rpz/critters/peabrain-lab/banc/"
z=np.load(B+"l150/raw_l150.npz")
arms=defaultdict(list)
for k in z.keys():
    m=re.match(r'^mm_(.+)_(\d+)$',k)
    if m: arms[m.group(1)].append(int(m.group(2)))
for a in sorted(arms): print("ARM",a,"seeds",sorted(arms[a]))
# channel suffix list for one arm/seed
chs=sorted({k.rsplit("_",2)[0] for k in z.keys() if re.match(r'^(Ti|Tr|Ta|Sr|Pr)_',k)})
print("CHANNELS",chs)
print("af example", {a: float(z[f"af_{a}_{sorted(arms[a])[0]}"]) for a in sorted(arms)})
print("K",int(z["K"]), "g_full",float(z["g_full"]),"g65",float(z["g65"]))
print("batches",z["batches"])
