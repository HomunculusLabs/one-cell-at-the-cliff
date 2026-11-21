# Run from banc/ after edge_run.py. Re-read persisted raw arrays, not simulator memory.
from pathlib import Path
import json,os,hashlib,numpy as np
out=Path('l190'); read=lambda n:json.loads((out/n).read_text()); r=read('results_l190.json'); done=read('done_w0.json'); st=read('selection.json'); arms=done['arms']; seeds=r['seeds']; assert done['seeds']==[801,901,3545]+seeds and len(seeds)==len(r['rows'])==16 and set(arms)=={'E-edge','E-sham','sc25','cutwA'}; assert r['prereg']==done['prereg_sha256']==hashlib.sha256((out/'PREREG.md').read_bytes()).hexdigest(); an=r['anchors']; assert an['c0a135_pass'] and an['c0a175_pass'] and an['c0a135_max']==an['c0a175_max']==0
v=Path('l187/verdict_l187.py').read_text().splitlines(True); m={};exec(''.join(v[:71]+v[117:125]),m);z=np.load(out/'raw_w0.npz'); trace_count=0
for s in done['seeds']:
    for a in (arms if s in seeds else ['cutwA','sc25']):
        for g in [1110,75494,559,74914]:
            key=f'c{g}_{a}_{s}';
            if a=='sc25' and g==1110: assert key not in z;continue
            x=z[key];assert x.shape==(6000,) and x.dtype==np.float32 and np.isfinite(x).all();trace_count+=1
        if s in seeds:
            l,d=m['duty_seeds'](z,a,[s],'Ti');f=m['duty14_seeds'](z,a,[s]);assert r['rows'][str(s)][a]==dict(L=l[0],R=d[0],mid=f[0])
vec=lambda a,k:np.array([r['rows'][str(s)][a][k] for s in seeds]); tab={}
for a in arms:
    right=vec(a,'R');d=right-vec('cutwA','R');delta=float(d.mean());half=2.131449546*d.std(ddof=1)/4;lo,hi=delta-half,delta+half;kr=int((right>=.5).sum());mean=float(right.mean());mid=float(vec(a,'mid').mean());sup=mean>=.6 and kr>=12;fp=mid>=.25
    tab[a]=dict(kR=kr,meanR=mean,meanL=float(vec(a,'L').mean()),mid=mid,delta=delta,CI=[lo,hi],SUPER=bool(sup),fingerprint=bool(fp),branch=('B1-edge-carries' if sup and fp else 'B2-edge-inert' if not fp and abs(delta)<.10 else 'B3-partial' if not fp and delta>=.10 and lo>0 else 'unresolved') if a.startswith('E-') else None)
r.update(summary=tab,controls_pass=not tab['cutwA']['SUPER'] and tab['sc25']['SUPER'] and tab['sc25']['fingerprint'],trace_arrays_verified=trace_count,worker_seconds=done['secs'],status='FINAL');tmp=out/'results_l190.json.tmp';tmp.write_text(json.dumps(r,indent=1)+'\n');os.replace(tmp,out/'results_l190.json');print(json.dumps({k:r[k] for k in ['summary','gain','controls_pass','trace_arrays_verified','worker_seconds']},indent=1))
