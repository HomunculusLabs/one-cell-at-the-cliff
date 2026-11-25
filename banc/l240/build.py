# Run from banc/. Keep audited lineage step, bisect, RNG and anchor functions verbatim.
# L240 stage A1: l187/relay_run.py (sha-pinned) sliced exactly as l190/build.py did;
# only the arm block and the worker plan are L240's, plus the noise-twin draws.
from pathlib import Path as P
from hashlib import sha256
p = P('l187/relay_run.py')
assert sha256(p.read_bytes()).hexdigest() == 'b7c486bf32505e95b57405db719c5ebe1389c3f3e65e925f4119791451b94327'
s = p.read_text().splitlines(True)


def lines(a, b):
    return ''.join(s[a - 1:b])


# slice anchors, asserted against the pinned source before anything is composed
assert s[75].startswith('ANCH_175 = [3545]'), s[75]
assert s[77].startswith('SEEDS = ANCH_BIT') and s[78].startswith('FRESH = B41'), s[77]
assert s[1130].startswith('CHAIN = [GI_RELAY'), s[1130]
assert s[1176].startswith('# ===================== end L175 GEN BLOCK'), s[1176]
assert s[1357].startswith('assert MODE == "work"'), s[1357]
assert s[1358].startswith('assert os.path.exists(PREREG_PATH)'), s[1358]
assert s[1378].startswith('BIS = ["cutwA"]') and s[1379].startswith('STORED_G = '), s[1378]
assert s[1750].startswith('    post_seed(seed)'), s[1750]

h = lines(26, 76) + '''from pathlib import Path
assert hashlib.sha256(Path('l240/PREREG.md').read_bytes()).hexdigest()==Path('l240/PREREG.sha256').read_text().split()[0]
seen=set(); archives=0
for p in sorted(Path('..').rglob('*.npz')):
    if 'l240' in p.parts: continue
    with zipfile.ZipFile(p) as z:
        seen.update(int(m[1]) for k in z.namelist() if (m:=re.search(r'_(\\d+)\\.npy$',k)))
    archives+=1
start=3641
while seen.intersection(range(start,start+16)): start+=32
B240=list(range(start,start+16))
assert B240==list(range(3769,3785)), (B240[0], 'PREREG seed block drift (STOP)')
B41=B240
PLAN240={0:['e4','e12','e13','e14','e25'],1:['e38','e39','e59','e62','e64'],2:['e67','g11','g11f','nf']}
''' + lines(78, 711) + lines(731, 1007)
h += "add_arm('sc25',GI_CARRIER)\n"
h += '''# ======================= L240 ARMS BLOCK (additive) =======================
# Single-out-edge ablations of the carrier (gi 1110) on cutwA, the 11-as-GROUP
# arm, its fixed-gain twin, and the noise-twin arm. Same CSR surgery as L190's
# E-edge (one entry out of the carrier's row), asserted structurally.
S221=json.load(open('l221/static.json'))
_tb=S221['Q221_b_target_reach']['used_edge_table']
EJ=[int(r['edge_j']) for r in _tb]
TG={int(r['edge_j']):int(r['target_gid']) for r in _tb}
assert EJ==[4,12,13,14,25,38,39,59,62,64,67]==S221['L221_primary']['per_metric']['abs']['feasible_edges'], EJ
assert len(set(TG.values()))==11
assert GI_CARRIER==1110 and loc_wA[GI_CARRIER]>=0 and loc_wA[TG[67]]==RELAY_LOC and TG[67]==GI_RELAY
base=Wb_wA; crb=base.crow_indices(); cib=base.col_indices(); vb=base.values()
ccol=int(loc_wA[GI_CARRIER]); MENU_N=int((cib==ccol).sum())
assert 69<=MENU_N<=80, (MENU_N, 'carrier cutwA menu outside [69,80] (STOP)')
def _cut240(name,targets):
    add_base_alias(name)
    rows=[int(loc_wA[g]) for g in targets]
    assert all(r>=0 for r in rows), (name, 'labelled target absent from cutwA (UNMEASURABLE, STOP)')
    hits=[]
    for r in rows:
        a,b=map(int,crb[r:r+2])
        w=torch.where(cib[a:b]==ccol)[0]
        assert len(w)==1, (name, r, 'entry multiplicity (STOP)')
        hits.append(a+int(w[0]))
    assert len(set(hits))==len(hits) and len(set(rows))==len(rows)
    km=torch.ones(len(cib),dtype=torch.bool)
    for j in hits:
        assert vb[j]!=0
        km[j]=False
    newcr=crb.clone()
    for r in rows: newcr[r+1:]-=1
    WB[name]=torch.sparse_csr_tensor(newcr,cib[km],vb[km],size=base.shape); w=WB[name]
    assert torch.equal(w.col_indices(),cib[km]) and torch.equal(w.values(),vb[km])
    _exp=torch.zeros(len(crb)-1,dtype=crb.dtype); _exp[rows]=1
    assert torch.equal(crb[1:]-crb[:-1]-(w.crow_indices()[1:]-w.crow_indices()[:-1]),_exp)
    assert w.values().numel()==GEN[name]['edges']-len(hits)
    GEN[name]['edges']-=len(hits)
    out=[]
    for g,j in zip(targets,hits):
        _m=emask_wA & (src_all==GI_CARRIER) & (dst_all==g)
        assert int(_m.sum())==1, (name, g, 'raw edge multiplicity (STOP)')
        out.append(dict(target=int(g),csr_index=int(j),effective_weight=float(vb[j]),syn=int(w_syn[_m][0]),sign=float(np.sign(vb[j]))))
    return out
EDGE240={}
for a in PLAN240[WID]:
    if a.startswith('e') and a[1:].isdigit():
        j=int(a[1:]); assert j in EJ, a
        EDGE240[a]=dict(edge_j=j,removed=_cut240(a,[TG[j]]))
    elif a=='g11':
        EDGE240[a]=dict(edge_j=None,removed=_cut240(a,[TG[j] for j in EJ]))
    elif a=='g11f':
        pass
    else:
        assert a=='nf', a
if 'g11' in EDGE240 and 'g11f' in PLAN240[WID]:
    add_base_alias('g11f'); WB['g11f']=WB['g11']; GEN['g11f']['edges']=GEN['g11']['edges']
if 'nf' in PLAN240[WID]:
    add_base_alias('nf')
atomic_json(f'{OUT}/arms_w{WID}.json',dict(wid=WID,menu_n=MENU_N,carrier_col=ccol,carrier=int(GI_CARRIER),
    base_edges=int(crb[-1]),edges=EDGE240,arms_built=list(PLAN240[WID]),
    seeds=B240,archives=archives,prereg=prereg_sha()))
CLAMPF={}
''' + lines(1131, 1141).replace('GI_SC40]     #', 'GI_SC40, 74914]     #')
h += lines(1177, 1359)
h += '''MY_ARMS=PLAN240[WID]; MY_CERT=[]
RAW_PATH, XM_PATH = f'{OUT}/raw_w{WID}.npz', f'{OUT}/xm_w{WID}.npz'
GAINS_PATH = f'{OUT}/gains_w{WID}.json'
FIXED=[a for a in MY_ARMS if a in ('g11f','nf')]
BIS=['cutwA']+[a for a in MY_ARMS if a not in FIXED]
log(f'worker {WID}: cutwA + {MY_ARMS} | bisected {BIS} | fixed {FIXED}')
'''
body = lines(1380, 1751)

# --- noise-twin (nf) wiring, rollout loops only (the bisect's settle is untouched)
head, sep, roll = body.partition('# ---------------- rollouts ----------------\n')
assert sep and roll.count('    gen2 = torch.Generator().manual_seed(seed + 9000)\n') == 1, 'rollout split'
roll = roll.replace('    gen2 = torch.Generator().manual_seed(seed + 9000)\n',
                    '    gen2 = torch.Generator().manual_seed(seed + 9000)\n'
                    '    genNF = torch.Generator().manual_seed(seed + 1000000)\n'
                    '    gen2NF = torch.Generator().manual_seed(seed + 1090000)\n')
KEY = 'noise[_ga] = nzn[GEN[_ga]["pos_in_new"]]\n'
parts = roll.split(KEY)
assert len(parts) == 3, len(parts)
out = parts[0]
for k, seg in enumerate(parts[1:]):
    prev = out.rstrip('\n').split('\n')[-3]
    assert prev.strip() == 'for _ga in ARMS:', prev
    ind = len(prev) - len(prev.lstrip())
    i = ' ' * ind
    out += KEY + (i + '_nzo = NOISE * torch.randn(n_old, 1, generator=genNF)\n'
                  + i + '_nza = NOISE * torch.randn(n_add, 1, generator=gen2NF)\n'
                  + i + '_nzn = torch.zeros(n_new, 1)\n'
                  + i + '_nzn[old_pos_in_new] = _nzo\n'
                  + i + '_nzn[new_pos] = _nza\n'
                  + i + "noise['nf'] = _nzn[wA_pos_in_new]\n") + seg
h += head + sep + out
h += '''    exec(compile(Path('l240/checkpoint.py').read_text(),'checkpoint.py','exec'))
''' + lines(1752, 1765)
assert h.count('OUT = "l187"') == 1
h = h.replace('OUT = "l187"', 'OUT = "l240"').replace('L187_', 'L240_')
assert 'L187_' not in h and 'l187"' not in h
P('l240/edge_run.py').write_text(h)
print('built l240/edge_run.py', len(h), 'bytes', h.count('\n'), 'lines')
