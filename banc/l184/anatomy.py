"""Offline static Q2. Run with ../peabrain/.venv/bin/python from lab root."""
from pathlib import Path
import numpy as np,pandas as pd,torch,json,itertools
from collections import defaultdict, Counter
P=Path(__file__).resolve().parent;B=P.parent;L=B/'l175';z=np.load(L/'census_k24.npz');gi=z['gi'];gi_set=set(gi);gain=float(z['g_cutwA']);x=dict(zip(gi,z['x_mean_3seed']));g=torch.load(B/'banc_graph.pt',weights_only=False,map_location='cpu');ids=g['ids'].numpy();assert np.array_equal(ids[gi],z['root_id']);idx={int(ids[i]):i for i in gi};sig=dict(zip(gi,z['eff_sign']));ann=pd.read_csv(B/'data/dv_11845666',sep='\t',low_memory=False).dropna(subset=['super_class']).set_index('pt_root_id').loc[ids[gi]].fillna('');ann.index=gi
# Use grouped synapses, not normalized graph.pt values (scan_run.py build/wb).
c=pd.read_csv(B/'data/dv_11842997',compression='gzip',usecols=['pre_root_id','post_root_id','syn_count']); c=c[c.pre_root_id.isin(idx)&c.post_root_id.isin(idx)].groupby(['pre_root_id','post_root_id']).syn_count.sum();src=np.array([idx[v] for v in c.index.get_level_values(0)]);dst=np.array([idx[v] for v in c.index.get_level_values(1)]); syn=c.to_numpy(); eff=np.log1p(syn)*np.array([sig[i] for i in src]);eff=np.where(eff<0,2*eff,eff);assert len(src)==644177; assert np.allclose(np.bincount(src,weights=abs(eff),minlength=len(ids))[gi],z['out_w_eff']); assert np.array_equal(gi,z['gi']);
lookup=defaultdict(dict); adj=defaultdict(set)
for i,j,v in zip(src,dst,eff):lookup[i][j]=gain*v;adj[i].add(j)
mot=ann.super_class=='motor';pools={t:set(ann.index[mot&(ann.side=='right')&ann.peripheral_target_type.str.contains('tibia')&ann.peripheral_target_type.str.contains(t)]) for t in ('flexor','extensor')};pool={i:t for t,nodes in pools.items() for i in nodes};assert sum(map(len,pools.values()))==len(pool);pre=set(src[np.isin(dst,list(pool))]); target=lambda j: ('right-Ti '+pool[j] if j in pool else 'other motor' if mot[j] else 'direct right-Ti premotor' if j in pre else ann.at[j,'super_class']); C=1110; ed=[]
for n in np.flatnonzero((src==C)|(dst==C)):
 i,j=src[n],dst[n];other=j if i==C else i;ed.append(dict(direction='out' if i==C else 'in',src=i,dst=j,syn=int(syn[n]),effective_weight=eff[n],partner_type=ann.at[other,'cell_type'],partner_side=ann.at[other,'side'],partner_super=ann.at[other,'super_class'],target_class=target(j) if i==C else 'input',peripheral_target=ann.at[other,'peripheral_target_type']))
assert len(ed)==93;pd.DataFrame(ed).to_csv(P/'edges.csv',index=False); labels={'sc25':C,'sc26':319,'sc27':707,'sc40':559,'dmA':511,'dmC':1480}; terminals={i:adj[i]&pool.keys() for i in gi};tops=[];summary=[];overlap=[]
for a,start in labels.items():
 hits=[]
 def walk(path,w):
  i=path[-1];opts=terminals[i] if len(path)==4 else adj[i];
  for j in opts:
   if j in path:continue
   path2=(*path,j);w2=w*lookup[i][j];
   if j in pool:
    sens=all(.05<x[k]<.95 for k in path2[1:]);hits.append((pool[j],len(path),w2/len(pools[pool[j]]),path2,sens));continue
   if len(path)<4 and (len(path)<3 or j in pre):walk(path2,w2)
 walk((start,),1.); O=adj[start];shared=O&adj[C];overlap.append(dict(arm=a,gi=start,out=len(O),shared=len(shared),jaccard=len(shared)/len(O|adj[C]),direct_premotor=len((O-set(ann.index[mot]))&pre),shared_premotor=len((shared-set(ann.index[mot]))&pre),shared_gi=';'.join(map(str,sorted(shared)))))
 for mode in ['unit','interior_proxy']:
  for t in pools:
   h=[r for r in hits if r[0]==t and (mode=='unit' or r[4])];h.sort(key=lambda r:(-abs(r[2]),r[3]));
   for rank,(_,l,w,path,_) in enumerate(h[:10],1):tops.append(dict(arm=a,mode=mode,pool=t,rank=rank,hops=l,score=w,path='>'.join(map(str,path)),types='>'.join(str(ann.at[k,'cell_type']) for k in path)))
   for l in range(1,5):
    scores=[r[2] for r in h if r[1]==l];summary.append(dict(arm=a,mode=mode,pool=t,hops=l,count=len(scores),signed_sum=sum(scores),absolute_sum=sum(map(abs,scores))))
for name,rows in [('top_paths',tops),('path_totals',summary),('overlap',overlap)]:pd.DataFrame(rows).to_csv(P/(name+'.csv'),index=False)
print('pool sizes', {k:len(v) for k,v in pools.items()},'incident classes',Counter(r['target_class'] for r in ed));print(pd.DataFrame(overlap).to_string(index=False));print(pd.DataFrame(tops).query("arm=='sc25' and rank<=2").to_string(index=False))
