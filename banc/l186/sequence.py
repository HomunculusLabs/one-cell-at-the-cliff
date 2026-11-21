"""Foreground sequencer. Never launch on dispatch exit alone."""
import os,sys,re,time,json,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent;b=p.parent;v=b/'l187/verdict.out'
def dispatch():
 found=[]
 for d in Path('/proc').glob('[0-9]*'):
  try:cmd=(d/'cmdline').read_bytes().split(b'\0');stat=(d/'stat').read_text().split();pid=int(d.name)
  except (FileNotFoundError,ProcessLookupError,PermissionError):continue
  if stat[2]=='Z':continue
  if (pid,stat[21]) in [(781933,'84471464'),(782155,'84471493')] or any(x.startswith(b'Experiment dispatch (owner request, L187') for x in cmd):found.append(pid)
 return found
while True:
 ids=dispatch();marker=v.exists() and bool(re.search(r'^.*\bFINAL\b.*$',v.read_text(),re.M));print(time.strftime('%FT%T%z'),'L187 FINAL:',marker,'dispatch:',ids,flush=True)
 if not ids:
  if marker:break
  sys.exit('STOP: L187 dispatch exited without FINAL')
 time.sleep(15)
start=time.monotonic(); deadline=start+5380
(p/'gate_clear.json').write_text(json.dumps(dict(time=time.time(),marker=[x for x in v.read_text().splitlines() if 'FINAL' in x][-1],dispatch=ids)))
env=dict(os.environ,L175_MODE='work',L175_THREADS='2',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='');py='/home/t3rpz/critters/peabrain/.venv/bin/python'
for script,out in [('run.py','worker.out'),('analyze.py','verdict.out')]:
 with (p/out).open('w') as f:subprocess.run([py,'-B',str(p/script)],env=env,cwd=b,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=deadline-time.monotonic())
r=json.loads((p/'results_l186.json').read_text());assert r['status']=='FINAL' and len(r['seeds'])==16 and r['anchors']['c0a_pass'] and len((p/'L186-FINDINGS.md').read_text().splitlines())<=60
line=f"\nL186 gate-jitter: {r['branch']}; aligned/elapsed deletion contrasts {r['contrasts']['A']['value']:+.3f}/{r['contrasts']['T']['value']:+.3f}, 16 paired seeds; C0A exact. banc/l186/L186-FINDINGS.md and results_l186.json.\n"
intent=b.parent/'LAB-INTENT.md';assert line not in intent.read_text();
with intent.open('a') as f:f.write(line)
assert line in intent.read_text();print((p/'L186-FINDINGS.md').read_text(),flush=True)
