import numpy as np, re, collections
z=np.load('../l135/raw_l135.npz')
ks=list(z.keys())
pat=collections.Counter()
for k in ks:
    kk=re.sub(r'\d+','#',k)
    pat[kk]+=1
for k,v in pat.most_common(40): print(v,k)
print('--- sample arm/seed keys')
for k in ks:
    if 'Ti' in k or 'Tr' in k:
        print(k, z[k].shape, z[k].dtype); break
samp=[k for k in ks if k.endswith('_Ti_fL')][:5]
print(samp)
