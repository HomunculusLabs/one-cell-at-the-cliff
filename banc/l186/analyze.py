from pathlib import Path
import numpy as np,json
p=Path(__file__).resolve().parent
seeds=list(range(18601,18617)); arms=['cutwA','sc25']; t=np.arange(6000); phase=np.cumsum(2*np.pi*.01*np.where(t//2000==1,1.4,.7)); offsets=np.arange(-250,251,10); W=offsets[:,None]+np.arange(500); raw=np.load(p/'raw.npz'); anc=json.loads((p/'anchors.json').read_text());gain=json.loads((p/'gains.json').read_text()); assert anc['c0a_pass'] and anc['n_checks']==92 and anc['c0a_max']==0 and all(gain['stored_exact'].values())
onsets={}; phasefits={}; matrices={}; phases={}
for s in [801,901,*seeds]:
 g=raw[f'gate_{s}'];j=np.zeros(2,int) if s<1000 else np.random.default_rng([186,s]).integers(-300,301,2); ons=np.array([900,4900])+j; expected=(t//2000==1)|((t%2000<500)|(t%2000>=1800));
 for o in ons:expected[o:o+500]=True
 assert np.array_equal(g,expected) and list(g.reshape(3,-1).sum(1))==[1200,2000,1200];onsets[s]=ons.tolist();ph={};ii=np.concatenate([np.arange(o,o+500) for o in ons]);X=np.column_stack([ii<2000,ii>=4000,np.sin(phase[ii]),np.cos(phase[ii])]);
 for a in arms:
  for k in ['GI1110','Ti_fR','Ti_eR']:
   y=raw[f'{k}_{a}_{s}'];assert y.shape==(6000,)
   if a=='sc25' and k=='GI1110': assert np.isnan(y).all();continue
   assert np.isfinite(y).all();cs,cc=np.linalg.lstsq(X,y[ii],rcond=None)[0][-2:];ph[k+'_'+a]=dict(peak=float(np.arctan2(cs,cc)),amp=float(np.hypot(cs,cc)))
 phasefits[s]=ph
for k in ['Ti_fR','Ti_eR']:
 d=[]
 for s in seeds:
  ph=phasefits[s]; f=ph[k+'_cutwA'];c=ph['GI1110_cutwA'];
  if min(f['amp'],c['amp'])>1e-6:d.append(f['peak']-c['peak'])
 z=np.mean(np.exp(1j*np.array(d))) if d else None;phases[k]=dict(n=len(d),degrees=float(np.angle(z,deg=True)) if d else None,R=float(abs(z)) if d else None)
def unit(y,idx):
 v=y[idx].astype(float);v-=v.mean(-1,keepdims=True);n=np.linalg.norm(v,axis=-1);return v/np.maximum(n[:,None],1e-99),n>np.sqrt(500)*1e-6
for a in arms:
 f=[raw[f'Ti_fR_{a}_{s}'] for s in seeds];e=[raw[f'Ti_eR_{a}_{s}'] for s in seeds];mat=np.zeros((2,16,16));
 for seg in range(2):
  for i,s in enumerate(seeds):
   idx=W+onsets[s][seg];v,ok=unit(f[i],idx)
   for j,q in enumerate(seeds):
    for clock,pos in enumerate([W+onsets[q][seg],idx]):
     w,ok2=unit(e[j],pos);mat[clock,i,j]+=np.mean(ok&ok2&((v*w).sum(-1)<=-.25))*.5
 assert np.array_equal(mat[0].diagonal(),mat[1].diagonal());matrices[a]=mat
h=matrices['sc25']-matrices['cutwA'];h=np.array([*h,h[0]-h[1]]);mask=~np.eye(16,dtype=bool);est=h[:,mask].mean(1);jk=[]
for i in range(16):
 m=mask.copy();m[i]=False;m[:,i]=False;jk.append(h[:,m].mean(1))
se=np.sqrt(15/16*((jk-np.mean(jk,0))**2).sum(0));lo=est-1.96*se;hi=est+1.96*se;A,T,D=est
branch='E1-external' if A>=.15 and D>=.10 and lo[2]>0 else 'E2-elapsed' if T>=.15 and D<=-.10 and hi[2]<0 else 'E3-mixed/unresolved';surv='survives' if A>=.15 else 'reversed' if A<=-.15 else 'small'
means={a:{'aligned':float(m[0,mask].mean()),'elapsed':float(m[1,mask].mean()),'same':float(m[0].diagonal().mean())} for a,m in matrices.items()};stats={k:dict(value=float(x),ci95=[float(l),float(u)]) for k,x,l,u in zip('ATD',est,lo,hi)}
obj=dict(status='FINAL',branch=branch,survival=surv,means=means,contrasts=stats,phase=phases,phase_fits=phasefits,gains=gain,anchors=anc,seeds=seeds,onsets=onsets,ordered_pair_duties={a:m.tolist() for a,m in matrices.items()},clock_order=['aligned','elapsed']);text=json.dumps(obj,indent=1,allow_nan=False);(p/'results_l186.json').write_text(text+'\n');assert json.loads((p/'results_l186.json').read_text())['status']=='FINAL'
lines=['L186 gate-jitter discriminator — '+branch,'16 paired jitter schedules; anchor seeds 801/901 excluded.','Re-bisected gains: '+str(gain['gain'])+'; C0A: 92 exact, max difference 0.','Duty: aligned / elapsed / same-seed']+[f"  {a}: {v['aligned']:.3f} / {v['elapsed']:.3f} / {v['same']:.3f}" for a,v in means.items()]+['Deletion contrasts, seed-jackknife 95% intervals:']+[f'  {k} = {x:+.3f} [{l:+.3f}, {u:+.3f}]' for k,x,l,u in zip(['aligned','elapsed','aligned minus elapsed'],est,lo,hi)]+['Aligned deletion elevation: '+surv+'.',{'E1-external':'The deletion effect preferentially followed the displaced drive gate.','E2-elapsed':'Elapsed time was favored. The carrier tone kept elapsed phase; this does not establish an internal oscillator. Requires a second batch.','E3-mixed/unresolved':'Neither clock won by the registered margin and uncertainty rule; this is not evidence for two independent rhythms.'}[branch],'Carrier-present tone phase: pool peak relative to GI 1110 (positive = later).']+[f"  {k}: {v['degrees']} deg, R={v['R']}, n={v['n']} ({'concentrated' if v['n'] and v['R']>=.7 else 'dispersed or unavailable'})." for k,v in phases.items()]+['Deleted GI is structurally missing, not zero. Phase is not a causal transmission delay.','Inference is about the movable pulse in the 0.7-Hz segments, at graph-specific AF-matched gains; not whole-segment duty.']
assert len(lines)<=60;(p/'L186-FINDINGS.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
