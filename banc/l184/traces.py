"""Offline Q1/Q3/Q4; run with OPENBLAS_NUM_THREADS=1 python banc/l184/traces.py."""
from pathlib import Path
import json,csv,numpy as np
P=Path(__file__).resolve().parent; L=P.parent/'l175'; R=P.parents[1]/'paper/review_astra_evidence_r3'; J=json.loads((L/'results_l175.json').read_bytes()); seeds=J['seeds']; assert seeds==list(range(3545,3561)) and J['status']=='FINAL'
def save(name,rows):
 with (P/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader();w.writerows(rows)
k=np.arange(6000); b=k//2000; gate=(k%2000%900<500)|(b==1); phase=np.cumsum(.02*np.pi*np.where(b==1,1.4,.7)); tmask=k%2000>=500; ends=k[499::10]; boot=np.random.default_rng(184).integers(0,16,(10000,16)); cmp=['cutwA','sc26','dmA','dmC']; coef={}; tab=[]; sr=[]; q1=[]; q3=[]; prev={r['arm']:r for r in csv.DictReader((R/'b39-arms.csv').open())}; by={r['arm']:r for r in [J['base'],*J['window'],*J['twins'].values()]}; order=list(by); maps={}
for path in sorted(L.glob('raw_w*.npz')):
 with np.load(path) as z:
  for a in {key.split('_')[2] for key in z.files if key.startswith('Ti_fR_')}:maps.setdefault(a,path)
assert len(order)==len(maps)==37
for a in order:
 with np.load(maps[a]) as z: X=np.array([[z[f'Ti_{p}R_{a}_{i}'] for i in seeds] for p in 'fe'],dtype=float)
 Y=[];valid=[]
 for x in X:
  v=np.lib.stride_tricks.sliding_window_view(x,500,axis=-1)[:,::10];v=v-v.mean(-1,keepdims=True);norm=np.linalg.norm(v,axis=-1);valid.append(norm.T>np.sqrt(500)*1e-6);Y.append((v/np.maximum(norm[...,None],1e-100)).transpose(1,0,2).copy())
 corr=Y[0]@Y[1].transpose(0,2,1); ok=(corr<=-.25)&valid[0][:,:,None]&valid[1][:,None,:]; ix=~np.eye(16,dtype=bool); row={'arm':a}
 for label,outer in [('chopped',True),('fast',False)]:
  mask=tmask&((b!=1)==outer); g=gate[mask]; design=np.column_stack([*([b[mask]==0,b[mask]==2,g] if outer else [np.ones(mask.sum())]),g*np.sin(phase[mask]),g*np.cos(phase[mask])]); C=np.linalg.lstsq(design,X[:,:,mask].reshape(32,-1).T,rcond=None)[0].T.reshape(2,16,-1)
  for i,p in enumerate('fe'):
   A=np.hypot(C[i,:,-1],C[i,:,-2]); metrics={'amp':A,'sin':C[i,:,-2],'cos':C[i,:,-1]};
   if outer:metrics.update(gate=C[i,:,2],abs_gate=abs(C[i,:,2]))
   for n,vals in metrics.items():
    coef[a,label,p,n]=vals;q1.append(dict(arm=a,segment=label,pool=p,metric=n,mean=vals.mean()));sr.extend(dict(arm=a,segment=label,pool=p,metric=n,seed=s,value=v) for s,v in zip(seeds,vals))
  d=ok[mask[ends]].mean(0); same=d.diagonal();cross=d[ix]; row[label+'_k']=sum(same>=.5);row[label+'_mean']=same.mean()
  if outer:
   assert np.array_equal(np.round(same,3),by[a]['dutyR']);row['cross_k']=sum(cross>=.5);row['cross_mean']=cross.mean(); q3.append(dict(arm=a,flex=X[0][:,mask].mean(),ext=X[1][:,mask].mean(),mean_neg_r_same=-corr[mask[ends]].diagonal(axis1=1,axis2=2).mean(),same=same.mean(),cross=cross.mean(),residual=same.mean()-cross.mean()))
  assert row[label+'_k']==int(prev[a]['kR'+('07' if outer else '14')]);assert abs(same.mean()-float(prev[a]['meanR'+('07' if outer else '14')]))<.001
 tab.append(row)
for row in q3:
 for n in ['flex','ext','mean_neg_r_same','same','cross','residual']:row['delta_'+n]=row[n]-q3[0][n]
 assert abs(row['delta_cross']+row['delta_residual']-row['delta_same'])<1e-12
old=list(csv.DictReader((R/'locked.csv').open()));
for d in old:
 if d['segment']=='chopped':
  r=next(x for x in tab if x['arm']==d['arm']);assert abs(r['cross_mean']-float(d['cross_mean']))<.000051 and r['cross_k']==int(d['cross_k'])
contr=[]
for (a,l,p,n),v in coef.items():
 if a=='sc25' and n not in ('sin','cos'):
  for c in cmp:
   delta=v-coef[c,l,p,n];lo,hi=np.quantile(delta[boot].mean(1),[.025,.975]);contr.append(dict(ref=c,segment=l,pool=p,metric=n,sc25_minus_ref=delta.mean(),lo=lo,hi=hi))
save('threepanel.csv',tab);save('q3.csv',q3);save('q1.csv',q1);save('q1-seeds.csv',sr);save('q1-contrasts.csv',contr)
print('Verified',len(tab),'arms;',len(sr),'seed metrics')
