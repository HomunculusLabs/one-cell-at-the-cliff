"""Offline, CPU numpy + standard library only. Run from lab root or any directory."""
from pathlib import Path
import csv,hashlib,json,math,statistics,re
from collections import Counter,defaultdict
import numpy as np
E=Path(__file__).resolve().parent; R=E.parents[1]; B=R/'banc'; L=B/'l175'
def load(f): return json.loads(f.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for f in [R/'paper/DRAFT.md',R/'paper/numbers.json',R/'paper/CLAIM-MAP.md',B/'l172/stats.json',L/'PREREG.md',L/'results_l175.json',L/'verdict.out',L/'L175-FINDINGS.md']:print(f.relative_to(R),sha(f))
s=load(B/'l172/stats.json'); ledger=load(R/'paper/numbers.json')['l172.pooled']['v']; v=load(L/'results_l175.json');assert v['status']=='FINAL' and v['prereg_sha256']==sha(L/'PREREG.md')
def wil(k,n):
 z=statistics.NormalDist().inv_cdf(.975); c=(k+z*z/2)/(n+z*z);h=z*math.sqrt(k*(n-k)/n+z*z/4)/(n+z*z);return max(0,c-h),min(1,c+h)
# Per-seed source JSON is an input; independently verify it below from raw.
hist={}
for a in ['cutng25','cutng25p','cutwA','cut58','cutscr0']:
 t=s['per_seed'][a]; row=dict(zip(t['seeds'],t['dutyR'],strict=True)); assert len(row)==len(t['seeds']);hist[a]=row;k=sum(x>=.5 for x in row.values());n=len(row);assert (k,n)==(ledger[a]['kR'],ledger[a]['n']);print('canonical json',a,k,n,wil(k,n))
t=hist['cutng25p']; base=hist['cutwA']; c=Counter((x>=.5,base[i]>=.5) for i,x in t.items());u,w=c[True,False],c[False,True];print('matched twin/base',c,'p',min(1,2*sum(math.comb(u+w,j) for j in range(min(u,w)+1))/2**(u+w)))
z=np.load(B/'l137/raw_l137.npz'); x=z['census_x'].mean(axis=1); ids=z['census_ids'].tolist();print('intact means',[(i,x[ids.index(i)]) for i in (1110,319)],'active',sum(x>.05),len(x));z.close()
# Compute both windows together using non-overlapping index ranges in endpoint space.
ends=np.arange(499,6000,10);mask07=((ends>=500)&(ends<2000))|(ends>=4500);mask14=(ends>=2500)&(ends<4000)
def duty(z,a,i,side='R'):
 f,e=[np.lib.stride_tricks.sliding_window_view(z[f'Ti_{p}{side}_{a}_{i}'][:6000].astype(float),500)[::10] for p in 'fe'];f=f-f.mean(1)[:,None];e=e-e.mean(1)[:,None];ff=np.einsum('ij,ij->i',f,f);ee=np.einsum('ij,ij->i',e,e);fe=np.einsum('ij,ij->i',f,e);ok=(ff>500e-12)&(ee>500e-12)&(-fe>=.25*np.sqrt(ff*ee));return tuple(round(float(ok[m].mean()),3) for m in (mask07,mask14))
raw=defaultdict(dict)
for file in s['admissibility']['admissible']:
 with np.load(B/file) as z:
  for name in z.files:
   h=re.fullmatch(r'Ti_fR_(cutng25p?|cutwA|cut58|cutscr0)_(\d+)',name)
   if h:
    a,i=h[1],int(h[2]); d=duty(z,a,i);assert raw[a].setdefault(i,d)==d
for a,rows in raw.items():
 assert set(rows)==set(hist[a]);assert all(abs(ds[0]-hist[a][i])<.00051 for i,ds in rows.items());print('historic raw',a,len(rows),'chopped/unchopped k',np.sum(np.array(list(rows.values()))>=.5,axis=0))
# L175 every fresh seed, both sides. Save arm and seed-level data for reuse.
assert v['seeds']==list(range(3545,3561)); rows=[v['base'],*v['window'],*v['twins'].values()]; by={r['arm']:r for r in rows};obs={};records=[]
for file in sorted(L.glob('raw_w*.npz')):
 with np.load(file) as z:
  for a in sorted(set(n.split('_')[2] for n in z.files if n.startswith('Ti_fR_'))):
   vals=np.array([[*duty(z,a,i),*duty(z,a,i,'L')] for i in v['seeds']]);assert a not in obs or np.array_equal(vals,obs[a]);obs[a]=vals
assert set(obs)==set(by) and len(obs)==37
with (E/'b39-seeds.csv').open('w') as f:
 out=csv.writer(f);out.writerow(['arm','seed','R07','R14','L07','L14']);
 for a,ds in obs.items():
  for i,row in zip(v['seeds'],ds):out.writerow([a,i,*row])
def band(k,m):return 'S' if k>=12 and m>=.60 else ('N' if k<=8 and m<=.50 else 'I')
for a,r in by.items():
 ds=obs[a];k=(ds>=.5).sum(axis=0);m=np.round(ds.mean(axis=0),3);assert np.array_equal(ds[:,0],r['dutyR']) and np.array_equal(ds[:,2],r['dutyL']);assert (k[0],k[2])==(r['kR'],r['kL']);assert abs(m[0]-r['meanR'])<=.00101
 records.append([a,*k,*m,band(k[0],r['meanR']),band(k[1],m[1])]);
with (E/'b39-arms.csv').open('w') as f:
 out=csv.writer(f);out.writerow(['arm','kR07','kR14','kL07','kL14','meanR07','meanR14','meanL07','meanL14','registered_band','descriptive_fast_band']);out.writerows(records)
print('unchopped notable',[(r[0],r[2],r[6],r[-1]) for r in records if r[-1]!='N' or r[0] in ('dmA','dmC','cutwA','sc26')]);
cls={r[0]:r[-2] for r in records}; win=v['window'];cen=np.load(L/'census_k24.npz');ids=cen['gi'].tolist();xb=cen['x_mean_3seed'];out=cen['out_w_eff'];
for r in rows[1:]:
 j=ids.index(r['gi']);assert abs(r['x_mean']-xb[j])<1e-7 and abs(xb[j]*out[j]-r['delivered_drive'])<1e-4
A=[r for r in win[1:] if r['x_mean']>.05];H=[r for r in A if r['drive_ratio_to_carrier']>=.5];active=[win[0],*A];sil=[r for r in win if r['x_mean']<=.05]; ns=lambda rr:sum(cls[r['arm']]=='S' for r in rr)
def rho(rr,x,y):
 def rank(vals):return [sum(t<v for t in vals)+(sum(t==v for t in vals)+1)/2 for v in vals]
 return np.corrcoef(rank([r[x] for r in rr]),rank([r[y] for r in rr]))[0,1]
rh=rho(active,'delivered_drive','meanR'); E0=cls['sc25']!='S' or any(cls[a]=='S' for a in ('cutwA','sc26'));D1=cls['dmA']=='S' and rh>=.50 and (not H or ns(H)>=len(H)/2);D2=cls['dmA']=='N' and cls['sc25']=='S' and A and ns(A)<=len(A)/4
print('branch','E0' if E0 else 'D1' if D1 else 'D2' if D2 else 'D3');print('window',Counter(cls[r['arm']] for r in win),'A,H,silent',[(ns(g),len(g)) for g in (A,H,sil)],'rho',rh,rho([r for r in active if r['eff_sign']>0],'delivered_drive','meanR')); print('rho gain',*[rho(rr,'gain','meanR') for rr in (win[1:],sil)]);
for a in ('sc25','sc26','dmA','dmC'):
 r=by[a];print('targeted',a,'matched B39 drive ratio',r['x_mean_base_b39']*r['out_w_eff']/(by['sc25']['x_mean_base_b39']*by['sc25']['out_w_eff']),'motor mass fraction',r['out_w_motor']/r['out_w_eff'],'gross motor drive',r['x_mean']*r['out_w_motor'],'paired07 mean vs base',float((obs[a][:,0]-obs['cutwA'][:,0]).mean()))
