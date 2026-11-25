# Run from banc/:  python l290/build_l290.py   -> writes l290/edge_run_l290.py
# L290 harness = the CERTIFIED L240 A2 rollout harness (edge_run_a2.py, sha-pinned)
# sliced verbatim, with 7 asserted literal replacements (and one inserted line) in the head, the A2 menu
# derivation and _cut240() re-used as verbatim slices, a new L290 ARMS BLOCK, and the
# rollout tail verbatim but for 2 asserted literal replacements. Nothing lineage-side
# is edited; l240/ files are only read.
from pathlib import Path
import hashlib

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha('l240/edge_run_a2.py') == '2c71eded96e90af03aeb2fc4ca270627667f8879ffac7c7244e81b5b1dcf0496', 'A2 harness drift'
assert sha('l187/relay_run.py') == 'b7c486bf32505e95b57405db719c5ebe1389c3f3e65e925f4119791451b94327', 'relay_run drift'
assert sha('l240/edge_run.py') == '29bb9ad627e0a921cc4a3bcc2a1412c2930573faedbb3e0b220da14fba89d933', 'edge_run drift'
assert sha('l240/checkpoint.py') == '822dd066f0bab52052b1f6979c3d1e6dfff54d50993744f6ee6dc4d5803a2c9a', 'checkpoint drift'
assert sha('l290/PREREG.md') == Path('l290/PREREG.sha256').read_text().split()[0], 'L290 PREREG sha'
assert sha('l290/sets.json') == Path('l290/sets.sha256').read_text().split()[0], 'L290 sets sha'
A2 = Path('l240/edge_run_a2.py').read_text().split('\n')
assert len(A2) == 1652 and A2[-1] == '', (len(A2), 'A2 line count drift')


def idx(line):
    hits = [i + 1 for i, s in enumerate(A2) if s == line]
    assert len(hits) == 1, (line, hits)
    return hits[0]


L = lambda a, b: A2[a - 1:b]          # inclusive, 1-indexed


def rep(lines, old, new):
    hits = [k for k, s in enumerate(lines) if s == old]
    assert len(hits) == 1, (old, hits)
    lines[hits[0]] = new
    return lines


i_sc25 = idx("add_arm('sc25',GI_CARRIER)")
assert A2[i_sc25] == '# ======================= L240 A2 ARMS BLOCK (additive) ======================='
i_s221 = idx("S221=json.load(open('l221/static.json'))")
_i = [i + 1 for i, s in enumerate(A2) if s.startswith('assert CERT_MENU==11,')]
assert len(_i) == 1
i_cert = _i[0]
i_cut = idx('def _cut240(name,targets):')
i_ret = i_cut + 1 + A2[i_cut:].index('    return out')     # A2[i_cut:] starts one line AFTER the def
i_tail = idx('CLAMPF={}')
assert A2[i_tail - 2] == '    raise SystemExit(0)' and '# ===================== end L175 GEN BLOCK =====================' in L(i_tail, i_tail + 15), 'tail boundaries'
assert A2[i_s221 - 6] == '# ======================= L240 A2 ARMS BLOCK (additive) ======================='

# ---- head: A2 lines 1..978 verbatim but for these literal replacements ----
head = L(1, i_sc25)
head = rep(head, 'torch.set_num_threads(int(os.environ.get("L240_THREADS", "2")))',
           'torch.set_num_threads(int(os.environ.get("L290_THREADS", "2")))')
head = rep(head, 'MODE = os.environ["L240_MODE"]', 'MODE = os.environ["L290_MODE"]')
head = rep(head, 'WID = int(os.environ.get("L240_WID", "0"))', 'WID = int(os.environ.get("L290_WID", "0"))')
head = rep(head, 'NW = int(os.environ.get("L240_NW", "6"))', 'NW = int(os.environ.get("L290_NW", "3"))')
head = rep(head, "assert hashlib.sha256(Path('l240/A2_ADDENDUM.md').read_bytes()).hexdigest()==Path('l240/A2_ADDENDUM.sha256').read_text().split()[0]",
           "assert hashlib.sha256(Path('l290/PREREG.md').read_bytes()).hexdigest()==Path('l290/PREREG.sha256').read_text().split()[0]\n"
           "assert hashlib.sha256(Path('l290/sets.json').read_bytes()).hexdigest()==Path('l290/sets.sha256').read_text().split()[0]")
head = rep(head, "    if 'l240' in p.parts: continue", "    if 'l240' in p.parts or 'l290' in p.parts: continue")
head = rep(head, 'OUT = "l240"', 'OUT = "l290"')
head = [t for s in head for t in s.split('\n')]   # the two-line sha replacement becomes two elements
_ins = head.index("assert hashlib.sha256(Path('l290/sets.json').read_bytes()).hexdigest()==Path('l290/sets.sha256').read_text().split()[0]")
h2 = head[:_ins] + head[_ins + 1:]          # drop the ONE inserted line, then compare positionally
assert len(head) == i_sc25 + 1 and sum(1 for a, b in zip(h2, L(1, i_sc25)) if a != b) == 7, 'head: replacement count'   # 4 env + sha line + scan + OUT

# ---- verbatim slices of the A2 block ----
menu = L(i_s221, i_cert)
assert menu[0].startswith('S221=json.load') and menu[-1].startswith('assert CERT_MENU==11,') and len(menu) == 19
cut = L(i_cut, i_ret)
assert cut[0] == 'def _cut240(name,targets):' and cut[-1] == '    return out' and len(cut) == 29

BLOCK = r'''
# ======================= L290 ARMS BLOCK (L290 PREREG s3; sets re-derived here) =======================
SETS=json.load(open('l290/sets.json'))
SETS_SHA=hashlib.sha256(Path('l290/sets.json').read_bytes()).hexdigest()
N0={1,2,8,9,16,21,47,55}
_pm=S221['L221_primary']['per_metric']
USED={m:sorted(int(j) for j in _pm[m]['feasible_edges']) for m in ('abs','crofts','hop')}
assert [len(USED[m]) for m in ('abs','crofts','hop')]==[11,30,46], USED
assert USED['abs']==EJ and USED=={m:sorted(int(j) for j in SETS['used'][m]) for m in USED}, ('used-set drift (STOP)',USED)
assert len(set(USED['abs'])&set(USED['crofts']))==10 and set(USED['crofts'])<set(USED['hop']) and set(USED['abs'])<set(USED['hop'])
assert all(14 in USED[m] for m in USED)
_order=sorted(range(69),key=lambda j:(-SY69[j],j))
RAW={n:sorted(_order[:n]) for n in (11,30,46)}
_rng=np.random.Generator(np.random.PCG64(29013)); RAND={}; _rorder={}
for _n in (11,30,46):
    for _k in range(1,6):
        _d=[int(j) for j in _rng.choice(69,size=_n,replace=False)]
        _rorder[f'r{_n}k{_k}']=_d; RAND[f'r{_n}k{_k}']=sorted(_d)
assert {str(n):RAW[n] for n in RAW}==SETS['raw'], ('raw comparator drift (STOP)',RAW)
assert RAND=={a:sorted(v) for a,v in SETS['random'].items()}, ('random subset drift (STOP)',RAND)
assert _rorder==SETS['random_draw_order'], 'random draw order drift (STOP)'
assert all(int(loc_wA[TG69[j]])>=0 for j in range(69)), 'a menu edge is unlabelled on cutwA (STOP)'
assert len(set(TG69))==69, 'menu targets not distinct (STOP)'
SET={'gc30':USED['crofts'],'gh46':USED['hop'],'rw11':RAW[11],'rw30':RAW[30],'rw46':RAW[46]}; SET.update(RAND)
FIXARMS=['e14f','e25f','e67f','e12f','e27f']
assert len(SET)==20 and set(SET)=={'gc30','gh46','rw11','rw30','rw46'}|set(RAND)
PLAN290={0:['gc30','gh46','rw11','rw30','rw46','e14f','e25f','e67f'],
         1:['r11k1','r11k2','r11k3','r11k4','r11k5','r30k1','r30k2','e12f'],
         2:['r30k3','r30k4','r30k5','r46k1','r46k2','r46k3','r46k4','r46k5','e27f']}
_all290=sum(PLAN290.values(),[])
assert sorted(_all290)==sorted(list(SET)+FIXARMS) and len(_all290)==25 and len(set(_all290))==25, 'PLAN290 != the 25 PREREG arms'
assert sorted(PLAN290)==[0,1,2] and [len(PLAN290[w]) for w in sorted(PLAN290)]==[8,8,9]
_stored={}
for _p in sorted(Path('l240').glob('arms_w*.json')):
    for _n,_e in json.loads(_p.read_text())['edges'].items():
        if _n[0]=='e' and _n[1:].isdigit(): _stored[_n]=_e['removed'][0]
EDGE290={}
for _a in sorted(SET):
    EDGE290[_a]=dict(edge_j=-1,removed=_cut240(_a,[TG69[j] for j in SET[_a]]),syn_raw=None,set=SET[_a],
                     contains14=bool(14 in SET[_a]),eff=len([j for j in SET[_a] if j not in N0]))
    assert len(EDGE290[_a]['removed'])==len(SET[_a])
for _a in FIXARMS:
    _j=int(_a[1:-1]); _r=_cut240(_a,[TG69[_j]])[0]; _s=_stored[f'e{_j}']
    assert (_r['csr_index'],_r['effective_weight'],_r['syn'],_r['target'])==(_s['csr_index'],_s['effective_weight'],_s['syn'],_s['target']), (_a,'fixed twin is not the stored single-edge graph (STOP)')
    EDGE290[_a]=dict(edge_j=_j,removed=[_r],syn_raw=SY69[_j],fixed_gain=True)
assert all(int(WB[a].values().numel())==int(crb[-1])-len(EDGE290[a]['removed']) for a in EDGE290)
atomic_json(f'{OUT}/arms_w{WID}.json',dict(wid=WID,stage='L290-B',menu_n=MENU_N,menu69_n=len(TG69),cert_menu_11=CERT_MENU,
    carrier_col=ccol,carrier=int(GI_CARRIER),base_edges=int(crb[-1]),edges=EDGE290,arms_built=list(PLAN290[WID]),
    fixed=[a for a in PLAN290[WID] if a in FIXARMS],seeds=B240,archives=archives,prereg=prereg_sha(),sets_sha=SETS_SHA,
    contains14={a:EDGE290[a]['contains14'] for a in SET},eff={a:EDGE290[a]['eff'] for a in SET}))
if os.environ.get('L290_DRY'):
    log(f'DRY worker {WID}: menu_n {MENU_N} menu69 {len(TG69)} cert_menu {CERT_MENU} | arms {PLAN290[WID]} | sets ok, raw+random re-derived, fixed twins == stored single-edge graphs')
    raise SystemExit(0)
'''

# ---- tail: A2 lines i_tail..1651 verbatim but for two literal replacements ----
tail = L(i_tail, 1651)
tail = rep(tail, 'MY_ARMS=PLAN240[WID]; MY_CERT=[]', 'MY_ARMS=PLAN290[WID]; MY_CERT=[]')
tail = rep(tail, "FIXED=[a for a in MY_ARMS if a in ('g11f','nf')]",
           "FIXED=[a for a in MY_ARMS if a in ('e14f','e25f','e67f','e12f','e27f')]")
assert sum(1 for a, b in zip(tail, L(i_tail, 1651)) if a != b) == 2, 'tail: replacement count'
gen = head + ['# ======================= L290 ARMS BLOCK (L290 PREREG s3) =======================',
              '# Menu derivation + _cut240(): VERBATIM slices of the certified A2 block (build_l290.py).'] + menu + cut + \
      BLOCK.split('\n')[1:] + tail
txt = '\n'.join(gen)
# forbidden-token audit: the generated file must not plan or build any A2 arm
for tok in ('PLAN240[WID]', 'NEW240', 'EDGE240', 'UNMEAS=', 'UNMEAS.append', "stage='A2'", 'A2_ADDENDUM', "os.environ.get('L240_DRY')"):
    assert tok not in txt, ('forbidden token', tok)
assert txt.count('PLAN290[WID]') == 4 and txt.count('def _cut240(') == 1 and 'L240_' not in txt
Path('l290/edge_run_l290.py').write_text(txt)
print('wrote l290/edge_run_l290.py', len(gen), 'lines | sha256', hashlib.sha256(txt.encode()).hexdigest())
print('head lines', len(head), '| menu slice', len(menu), '| cut slice', len(cut), '| block', len(BLOCK.split('\n')) - 1, '| tail', len(tail))
