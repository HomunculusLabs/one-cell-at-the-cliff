from pathlib import Path
import os,sys,json,math,hashlib
D=Path(__file__).resolve().parent; P=D.parent.parent/'peabrain';sys.path.insert(0,str(P));os.environ['PEBRAIN_FORCE_HOUR']='12'
import numpy as np,torch
from brain import FlyBrain
from senses import DuckSenses
from mood import MoodState,AXIS_TAU
torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(0)
b=FlyBrain(str(P/'brain_graph.pt'),'cpu'); b.op_gain=.95/b.rho
s=DuckSenses(b,str(P/'data/neuron_annotations.tsv')); native=s.input_for
s.input_for=lambda event:native(event)*(.2 if event=='rake' else 1.)
step=b.step; seeds=list(range(100,108)); starts=[];rate=np.zeros(b.N);pre=rate.copy()
for seed in seeds:
 b.gen.manual_seed(seed);b.seed();b.run(100,gain=b.op_gain); starts.append((b.X.clone(),b.gen.get_state()))
def trial(k,idx=None,event='rake',census=False):
 x,g=starts[k];b.X=x.clone();b.gen.set_state(g);m=MoodState(s)
 if idx is not None:b.X[idx]=0
 def tick(**kw):
  if census:pre[:]+=np.abs(b.X.numpy())/160
  step(**kw)
  if idx is not None:b.X[idx]=0
  if census:rate[:]+=b.X.numpy()/160
  return b.X
 b.step=tick;m.observe(.2,event);f=m.fear;m.fear*=math.exp(-5*k/AXIS_TAU['fear']);out=[int(m.axes()['fear']>.4),f,m.fear];b.step=step;return out
def series(idx=None,event='rake',census=False):return [trial(k,idx,event,census) for k in range(8)]
ctrl={'intact':series(census=True),'quiet':series(event='quiet'),'LC_clamp':series(s.probes['LC'])}
W=b.W; mass=np.bincount(W.col_indices().numpy(),weights=np.abs(W.values().numpy()),minlength=b.N); drive=mass*pre*b.op_gain;nt=b.nt.numpy();rows=np.arange(b.N);top=np.flatnonzero(rate>.05);top=top[np.argsort(-rate[top],kind='stable')[:32]];assert len(top)==32
np.savez_compressed(D/'census.npz',rate=rate,pre_abs_rate=pre,mass=mass,drive=drive,root=b.ids.numpy(),nt=nt,top=top)
matches=[]
for i in top:
 pool=rows[(nt==nt[i]) & ~np.isin(rows,top)]; a=np.abs(np.log((mass[pool]+1e-12)/(mass[i]+1e-12)));c=np.abs(np.log((drive[pool]+1e-12)/(drive[i]+1e-12))); v=np.maximum(a,c);j=a.argmin();h=v.argmin();matches.append(dict(row=int(i),mass=int(pool[j]),joint=int(pool[h]),mass_loggap=float(a[j]),joint_loggap=float(v[h])))
R=dict(seeds=seeds,lags_s=list(range(0,40,5)),columns=['hide','peak_fear','decision_fear'],controls=ctrl,rho=b.rho,gain=b.op_gain,N=b.N,edges=W._nnz(),matches=matches,scan={},prereg_sha256=hashlib.sha256((D/'PREREG.md').read_bytes()).hexdigest()); targets=sorted({m[key] for m in matches for key in ('row','mass','joint')});print('controls',ctrl,'scan',len(targets),flush=True)
for i in targets:
 R['scan'][str(i)]=series(i);(D/'results.partial').write_text(json.dumps(R));print('row',i,flush=True)
(D/'results.partial').rename(D/'results.json')
