"""Independently compare stored array payloads, not nanmax differences."""
from pathlib import Path
import json,numpy as np
E=Path(__file__).resolve().parent;B=E.parents[1]/'banc';L=B/'l175'
def ident(a,b):return a.shape==b.shape and a.dtype==b.dtype and a.tobytes()==b.tobytes()
keys=['mm','xm','af']+[f'{p}_{x}{s}' for p,xy in [('Ti','fe'),('Tr','fe'),('Ta','ab'),('Sr','ab'),('Pr','ab')] for x in xy for s in 'LR'];old=np.load(B/'l135/raw_l135.npz');ref=np.load(L/'raw_w0.npz');n=m=0
for w in range(5):
 assert (L/f'done_w{w}.json').exists();z=np.load(L/f'raw_w{w}.npz'); g=json.loads((L/f'gains_w{w}.json').read_text())['gain']
 for a,b in [('cutwA','cutwA'),('sc25','cutng25'),('sc26','cutng25p')]:
  if a not in g:continue
  for i in (801,901):
   for k in keys:
    assert ident(z[f'{k}_{a}_{i}'],old[f'{k}_{b}_{i}']); n+=1
 if w:
  for i in [801,901,*range(3545,3561)]:
   for k in [*keys,'xwin']:
    name=f'{k}_cutwA_{i}';assert ident(z[name],ref[name]);m+=1
 z.close()
print('L135 to L175 arrays identical (dtype, shape and bytes):',n,'; cross-worker base:',m)
