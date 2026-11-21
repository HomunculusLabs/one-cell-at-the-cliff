# Run from banc/. Keep audited lineage step, bisect, RNG and anchor functions verbatim.
from pathlib import Path as P
from hashlib import sha256
p=P('l187/relay_run.py'); assert sha256(p.read_bytes()).hexdigest()=='b7c486bf32505e95b57405db719c5ebe1389c3f3e65e925f4119791451b94327'
s=p.read_text().splitlines(True)
def lines(a,b): return ''.join(s[a-1:b])
h=lines(26,76)+'''from pathlib import Path
assert hashlib.sha256(Path('l190/PREREG.md').read_bytes()).hexdigest()==Path('l190/PREREG.sha256').read_text().split()[0]
seen=set(); archives=0
for p in sorted(Path('..').rglob('*.npz')):
    if 'l190' in p.parts: continue
    with zipfile.ZipFile(p) as z:
        seen.update(int(m[1]) for k in z.namelist() if (m:=re.search(r'_(\\d+)\\.npy$',k)))
    archives+=1
start=3641
while seen.intersection(range(start,start+16)): start+=32
B41=list(range(start,start+16))
'''+lines(78,711)+lines(731,1007)
# The generic sc25 path is checked against stored lineage rollouts.
h+="add_arm('sc25',GI_CARRIER)\n"
h+='''cand=[]
for i in np.flatnonzero(_relay_in & (w_syn>=20) & (w_syn<=22)):
    g,n=int(src_all[i]),int(w_syn[i]);
    if g not in WIN_CELLS: cand.append((abs(n-21),not bool(dn_all[g]),abs(math.log(n/21)),g,n))
cand.sort(); picks={'E-edge':1110}
if cand: picks['E-sham']=cand[0][3]
info={}
for a,g in picks.items():
    add_base_alias(a); base=Wb_wA; row=int(loc_wA[75494]); col=int(loc_wA[g]); cr=base.crow_indices(); ci=base.col_indices(); val=base.values(); lo,hi=map(int,cr[row:row+2]); hits=torch.where(ci[lo:hi]==col)[0]; assert len(hits)==1
    j=lo+int(hits[0]); keep=torch.arange(len(ci))!=j; newcr=cr.clone(); newcr[row+1:]-=1
    WB[a]=torch.sparse_csr_tensor(newcr,ci[keep],val[keep],size=base.shape); w=WB[a]; assert torch.equal(w.col_indices(),ci[keep]) and torch.equal(w.values(),val[keep]) and torch.equal(cr[1:]-cr[:-1]-(w.crow_indices()[1:]-w.crow_indices()[:-1]),(torch.arange(len(cr)-1)==row).to(cr.dtype)); assert val[j]!=0
    GEN[a]['edges']-=1; info[a]=dict(source=g,target=75494,syn=int(w_syn[_relay_in & (src_all==g)].item()),effective_weight=float(val[j]),DN=bool(dn_all[g]),edges_after=GEN[a]['edges'])
atomic_json(f'{OUT}/selection.json',dict(candidates=cand,edges=info,seeds=B41,archives=archives,prereg=prereg_sha()))
CLAMPF={}
'''+lines(1131,1141).replace('GI_SC40]     #','GI_SC40, 74914]     #')
h+=lines(1177,1359)+'''MY_ARMS=['sc25']+list(picks); MY_CERT=[]; FIXED=[]; BIS=['cutwA']+MY_ARMS
RAW_PATH, XM_PATH=f'{OUT}/raw_w0.npz',f'{OUT}/xm_w0.npz'
GAINS_PATH=f'{OUT}/gains_w0.json'
'''+lines(1380,1751)+'''    exec(compile(Path('l190/checkpoint.py').read_text(),'checkpoint.py','exec'))
'''+lines(1752,1765)
h=h.replace('OUT = "l187"','OUT = "l190"').replace('L187_', 'L190_');P('l190/edge_run.py').write_text(h)
