from pathlib import Path
import numpy as np,json,hashlib,math,csv
D=Path(__file__).resolve().parent
r=json.loads((D/'results.json').read_text());c=np.load(D/'census.npz'); assert r['prereg_sha256']==hashlib.sha256((D/'PREREG.md').read_bytes()).hexdigest()
def hides(a):
 a=np.asarray(a);assert a.shape==(8,3) and np.isfinite(a).all(); assert all(int(round(v,3)>.4)==y for y,v in a[:,[0,2]]);return a[:,0].astype(int)
ctrl=r['controls']; base=hides(ctrl['intact']); n,q,l=[int(sum(hides(ctrl[k]))) for k in ('intact','quiet','LC_clamp')];usable=2<=n<=7 and max(q,l)<=1
matches=r['matches']; cells=r['scan'];roles={k:{m[k] for m in matches} for k in ('row','mass','joint')};assert set(map(int,cells))==set.union(*roles.values()) and roles['row']==set(c['top']) and len(matches)==32
points=[]; changes={}; carriers=[];tol=math.log(1.25)
for j,tr in cells.items():
 i=int(j);d=base-hides(tr);changes[i]=int(np.abs(d).sum());points.append((i,int(c['root'][i]),'+'.join(k for k,v in roles.items() if i in v),c['rate'][i],int(sum(d==1)),int(sum(d==-1)),d.mean(),np.mean(np.array(ctrl['intact'])[:,1]-np.array(tr)[:,1])))
for m in matches:
 d=base-hides(cells[str(m['row'])]);
 if usable and sum(d==1)>=4 and min(d)>=0 and max(changes[m['mass']],changes[m['joint']])<=1 and max(m['mass_loggap'],m['joint_loggap'])<=tol:carriers.append(m['row'])
verdict='readout-too-weak' if not usable else 'carrier candidate' if carriers else 'distributed-compatible within the scan' if max(changes[i] for i in roles['row'])<=1 else 'inconclusive'
with (D/'scatter.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['row','root_id','roles','rate','lost','gained','paired_hide_loss','mean_peak_fear_loss']);w.writerows(points)
x=np.array([p[3] for p in points]);lo=x.min();span=max(np.ptp(x),1e-6)
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 300"><rect width="640" height="300" fill="white"/><path d="M75 40V245H610 M75 145H610" fill="none" stroke="gray"/><g font-family="sans-serif" font-size="14"><text x="10" y="22">Paired hide probability lost (intact − clamped)</text><text x="38" y="50">+1</text><text x="38" y="150">0</text><text x="38" y="245">−1</text><text x="220" y="283">Mean intact scare-window rate</text>',f'<text x="75" y="262">{lo:.4f}</text><text x="560" y="262">{x.max():.4f}</text>']
for i,root,role,rate,lost,gained,y,_ in points:
 color='tomato' if 'row' in role else 'steelblue';svg.append(f'<circle cx="{78+520*(rate-lo)/span}" cy="{145-100*y}" r="3" opacity="0.5" fill="{color}"><title>{root}: {role}, {rate:.6f}, loss {y}</title></circle>')
(D/'scatter.svg').write_text(''.join(svg)+'</g></svg>');valid=sum(m['joint_loggap']<=tol for m in matches);active=int(sum(c['rate']>.05)); maxch=max(changes.values()); top=[p for p in points if 'row' in p[2]]
text=f'''Duck lesion scan — {verdict}

First autonomous hide after a distant rake, paired across eight seed/lag combinations.
Intact: {n}/8 hides; quiet: {q}/8; whole looming pool clamped: {l}/8.
Intact peak fear range {min(t[1] for t in ctrl['intact']):.6f}–{max(t[1] for t in ctrl['intact']):.6f}. The preregistered dynamic-range gate {'passed' if usable else 'failed'}.

Full graph: {r['N']:,} cells, {r['edges']:,} edges, intact rho {r['rho']:.6g}, fixed gain {r['gain']:.6g}.
{active:,} rows exceeded mean rate 0.05. Tested 32 highest-rate cells plus mass-only and joint twins ({len(points)} unique rows); {valid}/32 joint matches inside both calipers.
Scatter: scatter.svg (red targets, blue twins; overlapping dots are not jittered); exact coordinates in scatter.csv.
Top-cell rate range {min(p[3] for p in top):.6f}–{max(p[3] for p in top):.6f}; paired hide loss {min(p[6] for p in top):+.3f} to {max(p[6] for p in top):+.3f}.
Most decisions flipped by any single clamp, including twins: {maxch}/8.
Largest absolute mean peak-fear shift among the top cells: {max(abs(p[-1]) for p in top):.6f}.

'''
text+=('The whole-pool contrast and null/small single-cell effects support a population readout here, not proof that every untested neuron is dispensable.' if verdict.startswith('distributed') else 'The fixed cue/lag assay cannot separate a carrier from a distributed response.' if not usable else 'Candidate rows: '+str(carriers)+'. Replicate offline with fresh seeds and benign cue discrimination before considering any service-gated teaching.' if carriers else 'Effects did not satisfy the predeclared carrier or distributed bands.')+'\nNo live trial or training. No inference about an animal or a visitor-specific learned state.\n';assert len(text.splitlines())<=70;(D/'DUCK-FINDINGS.md').write_text(text);print(text)
