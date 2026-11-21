import numpy as np, glob, re, zipfile, json, os
from collections import defaultdict
files=sorted(glob.glob('l1*/raw_l1*.npz'))
print('%-22s %5s %6s %6s %s'%('file','nTi','WIN','arms','seeds(range)'))
info={}
for f in files:
    z=zipfile.ZipFile(f); ks=[n[:-4] for n in z.namelist()]
    ti=[k for k in ks if k.startswith('Ti_fL_')]
    arms=sorted({re.match(r'Ti_fL_(.+)_(\d+)$',k).group(1) for k in ti if re.match(r'Ti_fL_(.+)_(\d+)$',k)})
    seeds=sorted({int(re.match(r'Ti_fL_(.+)_(\d+)$',k).group(2)) for k in ti if re.match(r'Ti_fL_(.+)_(\d+)$',k)})
    W=None
    if ti:
        zz=np.load(f); W=zz[ti[0]].shape[0]
    info[f]=dict(arms=arms,seeds=seeds,W=W,nti=len(ti))
    print('%-22s %5d %6s %6d %s'%(f,len(ti),W,len(arms), (f'{min(seeds)}-{max(seeds)} n={len(seeds)}' if seeds else '-')))
json.dump({k:{'arms':v['arms'],'seeds':v['seeds'],'W':v['W']} for k,v in info.items()},open('l172/inv2.json','w'),indent=1)
