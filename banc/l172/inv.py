import json,glob,re,zipfile,os
from collections import defaultdict
files=sorted(glob.glob('l1*/raw_l1*.npz'))+sorted(glob.glob('l*/raw_partial.npz'))
inv=defaultdict(lambda: defaultdict(set))   # arm -> file -> seeds
for f in files:
    if 'partial' in f: continue
    try: ks=[n[:-4] for n in zipfile.ZipFile(f).namelist()]
    except Exception as e: print('ERR',f,e); continue
    for k in ks:
        m=re.match(r'^mm_(.+)_(\d+)$',k)
        if m: inv[m.group(1)][f].add(int(m.group(2)))
print('ARMS',len(inv))
rows=[]
for arm in sorted(inv):
    fl=inv[arm]; allseeds=set()
    dup=0
    for f in fl:
        allseeds_before=len(allseeds); allseeds|=fl[f]
        dup += len(fl[f]) - (len(allseeds)-allseeds_before)
    rows.append((arm,len(fl),sum(len(v) for v in fl.values()),len(allseeds),dup))
for r in sorted(rows,key=lambda r:-r[2])[:40]:
    print('%-14s files=%2d traces=%3d unique=%3d dup=%2d'%r)
# gains per run
print('=== gains ===')
for f in sorted(glob.glob('l1*/results_l1*.json')):
    try: d=json.load(open(f))
    except: continue
    g=d.get('gains')
    if isinstance(g,dict): print(os.path.dirname(f), {k:(round(v,9) if isinstance(v,(int,float)) else v) for k,v in list(g.items())[:14]})
