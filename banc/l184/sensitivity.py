"""Post-registration sensitivity: subtract fitted chopped time templates, not a causal mediation test. Historical individual trace is not B39."""
import numpy as np,csv,json
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent;L=B/'l175';s=json.loads((L/'results_l175.json').read_text())['seeds'];k=np.arange(6000);b=k//2000;gate=((k%2000)%900<500)|(b==1);phi=np.cumsum(.02*np.pi*np.where(b==1,1.4,.7));ends=k[499::10];mask=(b!=1)&(k%2000>=500); D=np.column_stack((b==0,b==2,gate,gate*np.sin(phi),gate*np.cos(phi)));rows=[]
for arm in ['cutwA','sc25','sc26','dmA','dmC','sc27','sc40']:
 for p in sorted(L.glob('raw_w*.npz')):
  with np.load(p) as z:
   if f'Ti_fR_{arm}_{s[0]}' not in z:continue
   X=np.array([[z[f'Ti_{t}R_{arm}_{i}'] for i in s] for t in 'fe'],float);break
 C=np.linalg.lstsq(D[mask],X[:,:,mask].reshape(32,-1).T,rcond=None)[0]
 for label,cols in [('original',[]),('minus_gate',[2]),('minus_tone',[3,4]),('minus_both',[2,3,4])]:
  x=X-(D[:,cols]@C[cols]).T.reshape(2,16,6000);v=np.lib.stride_tricks.sliding_window_view(x,500,axis=-1)[:,:,::10][:,:,mask[ends]]
  y=v-v.mean(-1,keepdims=True);n=np.linalg.norm(y,axis=-1);y=(y/np.maximum(n[...,None],1e-100)).transpose(0,2,1,3).copy(); n=n.transpose(0,2,1)>np.sqrt(500)*1e-6; d=((y[0]@y[1].transpose(0,2,1)<=-.25)&n[0][:,:,None]&n[1][:,None,:]).mean(0);rows.append(dict(arm=arm,template=label,same=d.diagonal().mean(),cross=d[~np.eye(16,dtype=bool)].mean()))
with (P/'sensitivity.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with np.load(B/'l137/raw_l137.npz') as z:y=z['census_x'][list(z['census_ids']).index(1110)]
for h,m,design in [('chopped',mask,D),('middle',(b==1)&(k%2000>=500),np.column_stack((k>=0,np.sin(phi),np.cos(phi))))]:
 c=np.linalg.lstsq(design[m],y[m],rcond=None)[0];print('full only, seed 3101:',h,'harmonic',np.hypot(*c[-2:]),'angle atan2(cos,sin)',np.arctan2(c[-1],c[-2]),'coefficients',c)
for label in ['original','minus_gate','minus_tone','minus_both']:
 a,b=[r for r in rows if r['template']==label][:2];print(label,'delta sc25-base',*[b[n]-a[n] for n in ['same','cross']]);
