"""Exploratory stimulus/time-locked negative control: compare flexor of seed i with extensor of j. No rollouts."""
from pathlib import Path
import json, numpy as np,csv
E=Path(__file__).resolve().parent;L=E.parents[1]/'banc/l175';v=json.loads((L/'results_l175.json').read_text());ends=np.arange(499,6000,10); bins=[(ends>=500)&(ends<2000),(ends>=2500)&(ends<4000),ends>=4500]; chopped=bins[0]|bins[2]; seeds=v['seeds']; arms=['cutwA','sc25','sc26','sc27','sc40','dmA','dmC']; extra=[]
for a in arms:
 file=next(p for p in sorted(L.glob('gains_w*.json')) if a in json.loads(p.read_text())['gain']); w=file.stem.split('_')[-1]
 with np.load(L/f'raw_{w}.npz') as z:
  arr=[]; valid=[]
  for p in ('fR','eR'):
   X=np.stack([z[f'Ti_{p}_{a}_{i}'][:6000] for i in seeds]).astype(float);X=np.lib.stride_tricks.sliding_window_view(X,500,axis=1)[:,::10,:];X=X-X.mean(axis=2,keepdims=True);norm=np.sqrt((X**2).sum(axis=2));valid.append(norm.T>np.sqrt(500)*1e-6);arr.append(np.transpose(X/np.maximum(norm[:,:,None],1e-100),(1,0,2)).copy())
  ok=(arr[0]@arr[1].transpose(0,2,1)<=-.25)&valid[0][:,:,None]&valid[1][:,None,:]; ix=~np.eye(len(seeds),dtype=bool)
  for label,m in zip(('chopped','first','fast','last'),[chopped,*bins]):
   duty=ok[m].mean(0);same=duty.diagonal();cross=duty[ix];extra.append([a,label,round(float(same.mean()),4),round(float(cross.mean()),4),int(sum(same>=.5)),int(sum(cross>=.5)),len(cross)]);
with (E/'locked.csv').open('w') as f:
 out=csv.writer(f);out.writerow(['arm','segment','same_mean','cross_mean','same_k_of_16','cross_k','cross_pairs_nonindependent']);out.writerows(extra)
print(*extra,sep='\n')
