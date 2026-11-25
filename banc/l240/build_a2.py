# Run from banc/. L240 stage A2 build (tick 275): the SAME audited lineage slices as
# build.py (A1, edge_run.py sha256 29bb9ad6... untouched); only the plan, the A2 menu
# derivation/certificate, the unmeasurable path, the addendum assert and the DRY hook
# are A2's. Writes l240/edge_run_a2.py.
from pathlib import Path as P
from hashlib import sha256
p = P('l187/relay_run.py')
assert sha256(p.read_bytes()).hexdigest() == 'b7c486bf32505e95b57405db719c5ebe1389c3f3e65e925f4119791451b94327'
assert sha256(P('l240/edge_run.py').read_bytes()).hexdigest().startswith('29bb9ad627e0a921'), 'A1 harness moved (STOP)'
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

EJ = [4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67]
NEW = [j for j in range(69) if j not in EJ]
assert len(NEW) == 58 and max(NEW) == 68
SIZE = [9, 9, 8, 8, 8, 8, 8]
assert sum(SIZE) == 58 and len(SIZE) == 7
PLAN, k = {}, 0
for i, n in enumerate(SIZE):
    PLAN[3 + i] = [f'e{j}' for j in NEW[k:k + n]]
    k += n
assert k == 58 and len(set(sum(PLAN.values(), []))) == 58
plan_line = 'PLAN240=' + repr(PLAN) + '\n'

h = lines(26, 76) + '''from pathlib import Path
assert hashlib.sha256(Path('l240/PREREG.md').read_bytes()).hexdigest()==Path('l240/PREREG.sha256').read_text().split()[0]
assert hashlib.sha256(Path('l240/A2_ADDENDUM.md').read_bytes()).hexdigest()==Path('l240/A2_ADDENDUM.sha256').read_text().split()[0]
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
''' + plan_line + '''EJ240=[4,12,13,14,25,38,39,59,62,64,67]
''' + lines(78, 711) + lines(731, 1007)
h += "add_arm('sc25',GI_CARRIER)\n"
h += '''# ======================= L240 A2 ARMS BLOCK (additive) =======================
# The remaining 58 edges of the carrier's 69-edge L221 menu as SINGLE-out-edge
# ablations on cutwA (A2_ADDENDUM s1-s2). Same CSR surgery as A1, asserted
# structurally; the 69-edge menu is DERIVED here and certified on L221's 11 stored
# (edge_j,target) pairs before any bisect or rollout.
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
_m69=emask_wA & (src_all==GI_CARRIER)
_tg69=np.asarray(dst_all[_m69],np.int64); _sy69=np.asarray(w_syn[_m69],np.float64)
_o=np.argsort(_tg69,kind='stable'); _tg69=_tg69[_o]; _sy69=_sy69[_o]
assert len(_tg69)==MENU_N, (len(_tg69),MENU_N,'raw carrier out-edge list != CSR menu (STOP)')
_k69=_sy69>=4
TG69=[int(g) for g in _tg69[_k69]]; SY69=[float(x) for x in _sy69[_k69]]
assert len(TG69)==69, (len(TG69),'menu with raw syn>=4 is not 69 (STOP)')
CERT_MENU=int(sum(1 for j in EJ if TG69[j]==TG[j]))
assert CERT_MENU==11, (CERT_MENU,'of 11 stored L221 (edge_j,target) pairs reproduced (STOP)')
NEW240=[j for j in range(69) if j not in EJ]
assert len(NEW240)==58 and not (set(PLAN240[WID]) & {f'e{j}' for j in EJ})
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
EDGE240={}; UNMEAS=[]
for a in PLAN240[WID]:
    assert a.startswith('e') and a[1:].isdigit(), a
    j=int(a[1:]); assert j in NEW240, a
    if int(loc_wA[TG69[j]])<0:
        UNMEAS.append(dict(edge_j=j,target=TG69[j])); continue
    EDGE240[a]=dict(edge_j=j,removed=_cut240(a,[TG69[j]]),syn_raw=SY69[j])
PLAN240[WID]=[a for a in PLAN240[WID] if a in EDGE240]
atomic_json(f'{OUT}/arms_w{WID}.json',dict(wid=WID,stage='A2',menu_n=MENU_N,menu69_n=len(TG69),cert_menu_11=CERT_MENU,
    unmeasurable=UNMEAS,carrier_col=ccol,carrier=int(GI_CARRIER),base_edges=int(crb[-1]),edges=EDGE240,
    arms_built=list(PLAN240[WID]),seeds=B240,archives=archives,prereg=prereg_sha(),
    addendum=hashlib.sha256(Path('l240/A2_ADDENDUM.md').read_bytes()).hexdigest()))
if os.environ.get('L240_DRY'):
    log(f'DRY worker {WID}: menu_n {MENU_N} menu69 {len(TG69)} cert_menu {CERT_MENU} arms {PLAN240[WID]} unmeasurable {UNMEAS}')
    raise SystemExit(0)
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
assert sha256(P('l240/edge_run.py').read_bytes()).hexdigest().startswith('29bb9ad627e0a921'), 'A1 harness moved (STOP)'
P('l240/edge_run_a2.py').write_text(h)
print('built l240/edge_run_a2.py', len(h), 'bytes', h.count('\n'), 'lines; plan sizes', [len(v) for v in PLAN.values()])
