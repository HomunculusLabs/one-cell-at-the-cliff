# Run from banc/:  python l291/build_l291.py   -> writes l291/edge_run_l291.py
# L291 harness = the CERTIFIED L240 A2 rollout harness (edge_run_a2.py, sha-pinned) sliced verbatim,
# with 7 asserted literal replacements in the head, the A2 menu derivation and _cut240() re-used as
# verbatim slices, a new L291 ARMS BLOCK, and the rollout tail verbatim but for 2 asserted literal
# replacements -- the build_l290.py pattern. Nothing lineage-side is edited; l240/ and l290/ are only read.
from pathlib import Path
import hashlib

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha('l240/edge_run_a2.py') == '2c71eded96e90af03aeb2fc4ca270627667f8879ffac7c7244e81b5b1dcf0496', 'A2 harness drift'
assert sha('l187/relay_run.py') == 'b7c486bf32505e95b57405db719c5ebe1389c3f3e65e925f4119791451b94327', 'relay_run drift'
assert sha('l240/edge_run.py') == '29bb9ad627e0a921cc4a3bcc2a1412c2930573faedbb3e0b220da14fba89d933', 'edge_run drift'
assert sha('l240/checkpoint.py') == '822dd066f0bab52052b1f6979c3d1e6dfff54d50993744f6ee6dc4d5803a2c9a', 'checkpoint drift'
assert sha('l291/PREREG.md') == Path('l291/PREREG.sha256').read_text().split()[0], 'L291 PREREG sha'
assert sha('l291/sets.json') == Path('l291/sets.sha256').read_text().split()[0], 'L291 sets sha'
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
           'torch.set_num_threads(int(os.environ.get("L291_THREADS", "2")))')
head = rep(head, 'MODE = os.environ["L240_MODE"]', 'MODE = os.environ["L291_MODE"]')
head = rep(head, 'WID = int(os.environ.get("L240_WID", "0"))', 'WID = int(os.environ.get("L291_WID", "0"))')
head = rep(head, 'NW = int(os.environ.get("L240_NW", "6"))', 'NW = int(os.environ.get("L291_NW", "2"))')
head = rep(head, "assert hashlib.sha256(Path('l240/A2_ADDENDUM.md').read_bytes()).hexdigest()==Path('l240/A2_ADDENDUM.sha256').read_text().split()[0]",
           "assert hashlib.sha256(Path('l291/PREREG.md').read_bytes()).hexdigest()==Path('l291/PREREG.sha256').read_text().split()[0]\n"
           "assert hashlib.sha256(Path('l291/sets.json').read_bytes()).hexdigest()==Path('l291/sets.sha256').read_text().split()[0]")
head = rep(head, "    if 'l240' in p.parts: continue", "    if 'l240' in p.parts or 'l290' in p.parts or 'l291' in p.parts: continue")
head = rep(head, 'OUT = "l240"', 'OUT = "l291"')
head = [t for s in head for t in s.split('\n')]   # the two-line sha replacement becomes two elements
_ins = head.index("assert hashlib.sha256(Path('l291/sets.json').read_bytes()).hexdigest()==Path('l291/sets.sha256').read_text().split()[0]")
h2 = head[:_ins] + head[_ins + 1:]          # drop the ONE inserted line, then compare positionally
assert len(head) == i_sc25 + 1 and sum(1 for a, b in zip(h2, L(1, i_sc25)) if a != b) == 7, 'head: replacement count'

# ---- verbatim slices of the A2 block ----
menu = L(i_s221, i_cert)
assert menu[0].startswith('S221=json.load') and menu[-1].startswith('assert CERT_MENU==11,') and len(menu) == 19
cut = L(i_cut, i_ret)
assert cut[0] == 'def _cut240(name,targets):' and cut[-1] == '    return out' and len(cut) == 29

BLOCK = r'''
# ======================= L291 ARMS BLOCK (L291 PREREG s2; sets re-derived here) =======================
SETS=json.load(open('l291/sets.json'))
SETS_SHA=hashlib.sha256(Path('l291/sets.json').read_bytes()).hexdigest()
assert SETS['prereg_sha256']==prereg_sha(), ('sets were not built against the frozen PREREG (STOP)',SETS['prereg_sha256'],prereg_sha())
N0=set(SETS['noop'])
_pm=S221['L221_primary']['per_metric']
USED={m:sorted(int(j) for j in _pm[m]['feasible_edges']) for m in ('abs','crofts','hop')}
assert [len(USED[m]) for m in ('abs','crofts','hop')]==[11,30,46], USED
assert USED['abs']==EJ and USED=={m:sorted(int(j) for j in SETS['used'][m]) for m in USED}, ('used-set drift (STOP)',USED)
assert all(14 in USED[m] for m in USED)
assert [int(SY69[j]) for j in range(69)]==[int(_m['syn']) for _m in SETS['menu']], 'menu raw synapse drift (STOP)'
assert all(int(loc_wA[TG69[j]])>=0 for j in range(69)), 'a menu edge is unlabelled on cutwA (STOP)'
assert len(set(TG69))==69, 'menu targets not distinct (STOP)'
def _draw291():
    _r=np.random.Generator(np.random.PCG64(29113)); _out={}; _order={}; _meta={}
    for _n in (11,30,46):
        _u=USED[{11:'abs',30:'crofts',46:'hop'}[_n]]
        _t=sum(int(SY69[j]) for j in _u)
        _lo,_hi=int(np.ceil(0.95*_t)),int(np.floor(1.05*_t))
        assert (_lo,_hi)=={11:(200,220),30:(408,450),46:(593,655)}[_n], ('band drift (STOP)',_n,_lo,_hi)
        for _cell,_k in (('w',3),('f',2)):
            for _i in range(1,_k+1):
                _a=f's{_n}{_cell}{_i}'; _nd=0
                while True:
                    _nd+=1
                    assert _nd<=2000000, ('UNDRAWABLE (PREREG s2: report missing, never widen)',_a)
                    _d=[int(j) for j in _r.choice(69,size=_n,replace=False)]
                    if (14 in _d)!=(_cell=='w'): continue
                    _s=sum(int(SY69[j]) for j in _d)
                    if _lo<=_s<=_hi: break
                _out[_a]=sorted(_d); _order[_a]=_d; _meta[_a]=dict(n=_n,cell=_cell,syn_sum=_s,draws=_nd)
    return _out,_order,_meta
STRAT,SORDER,SMETA=_draw291()
assert STRAT=={a:sorted(int(j) for j in v) for a,v in SETS['strat'].items()}, ('stratified subset drift (STOP)',STRAT)
assert SORDER=={a:[int(j) for j in v] for a,v in SETS['strat_draw_order'].items()}, 'stratified draw order drift (STOP)'
assert SMETA=={a:dict(n=v['n'],cell=v['cell'],syn_sum=v['syn_sum'],draws=v['draws']) for a,v in SETS['strat_meta'].items()}, 'stratified meta drift (STOP)'
assert len(STRAT)==15 and len(set(tuple(v) for v in STRAT.values()))==15
assert all((14 in STRAT[a])==(_meta['cell']=='w') and SETS['bands'][str(_meta['n'])][0]<=_meta['syn_sum']<=SETS['bands'][str(_meta['n'])][1] and len(STRAT[a])==_meta['n'] for a,_meta in SMETA.items()), 'a stratified arm is outside its cell or band (STOP)'
FIXARMS291=['gc30f','gh46f']; TW={a:a[:-1] for a in FIXARMS291}
PLAN291={0:['s11w1','s11w2','s11w3','s11f1','s11f2','s30w1','s30w2','s30w3','gc30f'],
         1:['s30f1','s30f2','s46w1','s46w2','s46w3','s46f1','s46f2','gh46f']}
_all291=sum(PLAN291.values(),[])
assert sorted(_all291)==sorted(list(STRAT)+FIXARMS291) and len(_all291)==17 and len(set(_all291))==17, 'PLAN291 != the 17 PREREG arms'
assert sorted(PLAN291)==[0,1] and [len(PLAN291[w]) for w in sorted(PLAN291)]==[9,8]
assert PLAN291=={int(k):v for k,v in SETS['plan'].items()}, 'PLAN291 != sets.json plan (STOP)'
_stored={}
for _p in sorted(Path('l290').glob('arms_w*.json')):
    _e=json.loads(_p.read_text())['edges']
    for _n in ('gc30','gh46'):
        if _n in _e:
            _v=[(r['csr_index'],r['effective_weight'],r['syn'],r['target']) for r in _e[_n]['removed']]
            assert _stored.setdefault(_n,_v)==_v, ('stored L290 group graph differs between workers (STOP)',_n,_p)
assert sorted(_stored)==['gc30','gh46'], ('stored L290 group graphs not found (STOP)',sorted(_stored))
EDGE291={}
for _a in PLAN291[WID]:
    if _a in TW:
        _t=TW[_a]; _u='crofts' if _t=='gc30' else 'hop'
        _rm=_cut240(_a,[TG69[j] for j in USED[_u]])
        assert [(r['csr_index'],r['effective_weight'],r['syn'],r['target']) for r in _rm]==_stored[_t], (_a,'fixed twin is not the stored L290 group graph (STOP)')
        EDGE291[_a]=dict(edge_j=-1,removed=_rm,syn_raw=None,set=USED[_u],contains14=True,eff=len([j for j in USED[_u] if j not in N0]),fixed_gain=True,twin_of=_t)
    else:
        EDGE291[_a]=dict(edge_j=-1,removed=_cut240(_a,[TG69[j] for j in STRAT[_a]]),syn_raw=None,set=STRAT[_a],
                         contains14=bool(14 in STRAT[_a]),eff=len([j for j in STRAT[_a] if j not in N0]),**SMETA[_a])
        assert len(EDGE291[_a]['removed'])==len(STRAT[_a])
assert all(int(WB[a].values().numel())==int(crb[-1])-len(EDGE291[a]['removed']) for a in EDGE291)
atomic_json(f'{OUT}/arms_w{WID}.json',dict(wid=WID,stage='L291-B',menu_n=MENU_N,menu69_n=len(TG69),cert_menu_11=CERT_MENU,
    carrier_col=ccol,carrier=int(GI_CARRIER),base_edges=int(crb[-1]),edges=EDGE291,arms_built=list(PLAN291[WID]),
    fixed=[a for a in PLAN291[WID] if a in FIXARMS291],seeds=B240,archives=archives,prereg=prereg_sha(),sets_sha=SETS_SHA))
if os.environ.get('L291_DRY'):
    log(f'DRY worker {WID}: menu_n {MENU_N} menu69 {len(TG69)} cert_menu {CERT_MENU} | arms {PLAN291[WID]} | sets ok: 15 stratified re-derived, band + e14 cell held, fixed twins == stored L290 group graphs')
    raise SystemExit(0)
'''

# ---- tail: A2 lines i_tail..1651 verbatim but for two literal replacements ----
tail = L(i_tail, 1651)
tail = rep(tail, 'MY_ARMS=PLAN240[WID]; MY_CERT=[]', 'MY_ARMS=PLAN291[WID]; MY_CERT=[]')
tail = rep(tail, "FIXED=[a for a in MY_ARMS if a in ('g11f','nf')]",
           "FIXED=[a for a in MY_ARMS if a in ('gc30f','gh46f')]")
assert sum(1 for a, b in zip(tail, L(i_tail, 1651)) if a != b) == 2, 'tail: replacement count'
gen = head + ['# ======================= L291 ARMS BLOCK (L291 PREREG s2) =======================',
              '# Menu derivation + _cut240(): VERBATIM slices of the certified A2 block (build_l291.py).'] + menu + cut + \
      BLOCK.split('\n')[1:] + tail
txt = '\n'.join(gen)
# forbidden-token audit: the generated file must not plan or build any A2 or L290 arm
for tok in ('PLAN240[WID]', 'PLAN290[WID]', 'NEW240', 'EDGE240', 'EDGE290', 'UNMEAS=', "stage='A2'", "stage='L290-B'",
            'A2_ADDENDUM', "os.environ.get('L240_DRY')", "os.environ.get('L290_DRY')", "'l290/sets.json'", 'L240_', 'L290_'):
    assert tok not in txt, ('forbidden token', tok)
assert txt.count('PLAN291[WID]') == BLOCK.count('PLAN291[WID]') + 1 and BLOCK.count('PLAN291[WID]') == 4 \
    and txt.count('def _cut240(') == 1 and txt.count('def _draw291(') == 1   # 4 in the block (loop, arms_built, fixed list, DRY log) + the tail
Path('l291/edge_run_l291.py').write_text(txt)
print('wrote l291/edge_run_l291.py', len(gen), 'lines | sha256', hashlib.sha256(txt.encode()).hexdigest())
print('head lines', len(head), '| menu slice', len(menu), '| cut slice', len(cut), '| block', len(BLOCK.split('\n')) - 1, '| tail', len(tail))
