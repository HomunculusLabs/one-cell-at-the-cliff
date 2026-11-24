"""Offline only: run with run.sh. Source-slice the native pre-speech pipeline."""
import ast, hashlib, json, os, random, sys, time, zlib
from pathlib import Path
from types import SimpleNamespace
D=Path(__file__).resolve().parent; L=D.parent; P=L.parent/'peabrain'; U=L.parent/'puddle'
os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:4]); sys.path[:0]=map(str,(P,U,L)); os.environ['PEBRAIN_FORCE_HOUR']='12'
import torch
from brain import FlyBrain
from senses import DuckSenses
from mood import MoodState
from engine import PuddleMind
from scenarios import SCENARIOS
pin=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert pin(D/'PREREG.md')=='d07258210d1f89c78708bbc26f6856722437da09eef1e46798c7947eb14d5967'
torch.set_num_threads(4); torch.set_num_interop_threads(1);torch.manual_seed(0)
# Keep the installed bridge's actual routing/intent code; truncate immediately before speech.
mod=ast.parse((P/'bridge.py').read_text()); cls=next(n for n in mod.body if isinstance(n,ast.ClassDef) and n.name=='DuckBridge'); env={}
for n in mod.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SIT_TO_EVENT','INTENTS','CARD') for t in n.targets): exec(compile(ast.Module([n],[]),'bridge','exec'),env)
for n in cls.body:
 if isinstance(n,ast.FunctionDef) and n.name in ('synapse_trust','cx_intent','_reply_inside'):
  if n.name=='_reply_inside':
   cut=next(i for i,v in enumerate(n.body) if isinstance(v,ast.Assign) and ast.unparse(v.targets[0])=='pre');n.body=n.body[:cut]+ast.parse('return sit,event,mood,level,intent').body
  exec(compile(ast.fix_missing_locations(ast.Module([n],[])),'bridge','exec'),env)
class Host:
 synapse_trust=env['synapse_trust'];cx_intent=env['cx_intent'];reply=env['_reply_inside']; CX_BASE,CX_SPAN=next(ast.literal_eval(n.value) for n in cls.body if isinstance(n,ast.Assign) and ast.unparse(n.targets[0])=='(CX_BASE, CX_SPAN)')
 def _hebbian(self,st,event): pass # consolidate explicitly below once intent/routing are known
 def _log_event(self,*args):pass
h=Host(); t0=time.monotonic(); b=h.brain=FlyBrain(str(P/'brain_graph.pt'),'cpu');b.op_gain=.95/b.rho;s=h.senses=DuckSenses(b,str(P/'data/neuron_annotations.tsv'))
c=b.W.crow_indices().long(); rows=s.probes['DAN'];idx=torch.cat([torch.arange(c[r],c[r+1]) for r in rows]);src=b.W.col_indices()[idx].long(); dst=rows.repeat_interleave(c[rows+1]-c[rows]); w0=b.W.values()[idx].clone();cap=.2*w0.abs();step=b.step
class WindowMood(MoodState):
 def observe(self,seconds,event=None):
  remaining=20
  def bounded(**kw):
   nonlocal remaining
   if remaining: remaining-=1;return step(**kw)
   return b.X
  b.step=bounded
  try:super().observe(seconds,event)
  finally:b.step=step

def conversation(name,msgs,gaps,seed,d,eta):
 key=zlib.crc32(f'{name}|{seed}'.encode())&0x7fffffff;b.gen.manual_seed(key);b.seed();m=WindowMood(s);m.observe(30);st=SimpleNamespace(mood=m,mind=PuddleMind(env['CARD'],random.Random(key)),plas_d=d);out=[]
 for i,text in enumerate(msgs):
  if i:m.observe(gaps[i-1])
  sit,event,mood,level,intent=h.reply(text,st)
  if eta and sit in ('greet','greet_again','tin','feeding'):
   x,y=b.X[src],b.X[dst]; d.add_(eta*x*y*((x>.05)&(y>.05))).clamp_(-cap,cap);b.W.values()[idx]=w0+d
  syn=h.synapse_trust(st);out.append(dict(sit=sit,event=event,mood=mood,level=level,intent=intent,cx=h.cx_intent(st),trust=round(.5*(m.trust+syn),3),body=m.trust,syn=syn,fear=m.fear,hunger=m.hunger,sleep=m.sleep))
 return out
R={'prereg':pin(D/'PREREG.md'),'sources':{p.name:pin(p) for p in [P/'bridge.py',P/'brain.py',P/'senses.py',P/'mood.py',U/'engine.py',L/'scenarios.py',P/'brain_graph.pt']},'histories':[]};dr=[]
for seed in range(3):
 for eta in (0,.01):
  b.W.values()[idx]=w0;d=torch.zeros_like(w0);a={};q={}
  for sc in SCENARIOS:
   n=sc['name'];a[n]=conversation(n,sc['messages'],sc['gaps'],seed,d,eta)
   if n=='kindness_slow':
    for ev in ('rake','umbrella'):q[ev]=conversation('probe_'+ev,['look, a '+ev],[],seed,d,0)
  sleep=next(v for v in SCENARIOS if v['name']=='bedtime');q['sleep']=conversation('probe_sleep',sleep['messages'],sleep['gaps'],seed,d,0);q['quiet']=conversation('probe_quiet',['the clouds are grey'],[],seed,d,0)
  actual=b.W.values()[idx]-w0; nz=w0!=0;rel=actual[nz].abs()/w0[nz].abs();assert torch.all(d.abs()<=cap) and torch.all(torch.sign(w0+d)==torch.sign(w0)) and rel.max()<.200001 and (eta or not actual.any());assert len(a)==24 and all(len(y)==8 for y in a.values())
  dr.append(dict(seed=seed,eta=eta,graph_edges=b.W._nnz(),candidate=len(d),changed=int(actual.count_nonzero()),cap_hits=int(((d.abs()==cap)&nz).sum()),max_rel=float(rel.max()),mean_rel=float(rel.mean()),sign_flips=0));R['histories'].append(dict(seed=seed,eta=eta,battery=a,probes=q));print(dr[-1],time.monotonic()-t0,flush=True)
R['seconds']=time.monotonic()-t0;(D/'results.json').write_text(json.dumps(R,allow_nan=False));(D/'weight-drift.json').write_text(json.dumps(dr,indent=2))
