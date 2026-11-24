"""duck wave-6 replay harness. OFFLINE, read-only on everything outside duckroute/.

Re-reads stored v2-format score records through HER routing code: `needs`, the intent
tail of `_reply_inside` (bridge.py) and `MoodState.axes/mood_tag` (mood.py) are
source-sliced and executed on the stored post-turn axes, with the placed comparator
constants replaced at the AST level by THR[key]. No dynamics are stepped here.

argv: seeds to score as the held-out tier (optional), e.g. `replay.py 2 3`
Writes results.json (primary) and results_heldout.json (if seeds given).
"""
import ast, hashlib, json, math, os, sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import numpy as np

D = Path(__file__).resolve().parent; L = D.parent; P = L.parent / 'peabrain'; U = L.parent / 'puddle'
V2 = L / 'duckplast2'
pin = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PREREG = pin(D / 'PREREG.md')
assert PREREG == (D / 'PREREG.sha256').read_text().split()[0], 'prereg changed after lock'
sys.path.insert(0, str(L))
from scenarios import SCENARIOS
ARC = {s['name']: s['arc'] for s in SCENARIOS}
ORDER = [s['name'] for s in SCENARIOS]
KF = {n for n, a in ARC.items() if a in ('kindness', 'feeding')}
assert len(ORDER) == 24 and len(KF) == 7
HELD = [int(x) for x in sys.argv[1:]]
GATES = {}

# ---------------- G1: sources ----------------
want = dict(l.split()[::-1] for l in (V2 / 'SOURCES.sha256').read_text().splitlines())
src_now = {}
for rel, h in want.items():
    p = (V2 / rel).resolve(); src_now[p.name] = pin(p)
    assert src_now[p.name] == h, f'G1 source drifted: {rel}'
src_now['brain_graph.pt'] = pin(P / 'brain_graph.pt')

def load(seed, arm, base):
    r = json.loads((base / f'seed{seed}_{arm}.json').read_text())
    assert r['seed'] == seed and r['arm'] == arm and not r['smoke'] and r['k_idle'] == 0
    assert all(r['sources'][k] == v for k, v in src_now.items()), 'G1 record sources differ from live'
    assert [c['tag'] for c in r['census']] == ['S1', 'D1', 'S2', 'D2', 'S3', 'D3', 'R']
    return r
REC = {(s, a): load(s, a, V2 / 'out') for s in (0, 1) for a in ('frozen', 'plastic')}
GATES['G1_sources'] = dict(ok=True, files=sorted(src_now))

# ---------------- source-slice her routing ----------------
bmod = ast.parse((P / 'bridge.py').read_text())
bcls = next(n for n in bmod.body if isinstance(n, ast.ClassDef) and n.name == 'DuckBridge')
env = {'os': os, '__file__': str(D / 'lab_slice.py')}
for n in bmod.body:
    if isinstance(n, ast.Assign):
        exec(compile(ast.Module([n], []), 'bridge', 'exec'), env)
CONSTS = {k: v for k, v in env.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
mmod = ast.parse((P / 'mood.py').read_text())
mcls = next(n for n in mmod.body if isinstance(n, ast.ClassDef) and n.name == 'MoodState')
BF = {n.name: n for n in bcls.body if isinstance(n, ast.FunctionDef)}
MF = {n.name: n for n in mcls.body if isinstance(n, ast.FunctionDef)}

# the intent tail of _reply_inside: `intent = INTENTS.get(sit, "stay")` + the beg override that follows
rb = BF['_reply_inside'].body
ti = next(i for i, v in enumerate(rb) if isinstance(v, ast.Assign) and ast.unparse(v.targets[0]) == 'intent')
assert ast.unparse(rb[ti].value).startswith('INTENTS.get(sit') and isinstance(rb[ti + 1], ast.If)
assert ast.unparse(rb[ti + 2].targets[0]) == 'pre'          # the tail ends where speech begins
tail = ast.parse('def reply_tail(sit, event, session):\n    pass\n    return intent').body[0]
tail.body = [rb[ti], rb[ti + 1], tail.body[-1]]

SCORES = ('food_joy', 'hunger', 'sleep', 'trust', 'fear', 'salience', 'curiosity')
def score_of(expr):
    hit = [k for k in SCORES if k in expr]
    return hit[0] if len(hit) == 1 else None
def numeric(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool): return float(n.value)
    if isinstance(n, ast.Name) and n.id in CONSTS: return float(CONSTS[n.id])
    return None

# ---- inventory: every Compare against a numeric constant / module constant, enumerated from the AST
SCOPE = [('reply_tail', tail, 'INTENT/reply'), ('needs', BF['needs'], 'INTENT/needs'),
         ('world_tick', BF['world_tick'], 'ACT/world'), ('mood_tag', MF['mood_tag'], 'TAG'),
         ('consolidate_night', BF['consolidate_night'], 'GATE/night'), ('dream', BF['dream'], 'GATE/night'),
         ('cx_intent', BF['cx_intent'], 'MOTOR')]
INV = []
for fname, fn, klass in SCOPE:
    for n in ast.walk(fn):
        if isinstance(n, ast.Compare) and len(n.ops) == 1 and numeric(n.comparators[0]) is not None:
            left = ast.unparse(n.left)
            INV.append(dict(func=fname, klass=klass, left=left, op=type(n.ops[0]).__name__, thr=numeric(n.comparators[0]),
                            score=score_of(left), line=n.lineno, const=ast.unparse(n.comparators[0])))

KEYMAP = {('hunger', 'Gt'): 'hunger', ('sleep', 'LtE'): 'sleep_rider', ('sleep', 'Gt'): 'sleep',
          ('trust', 'Gt'): 'trust', ('fear', 'Gt'): 'fear', ('food_joy', 'Gt'): 'food_joy'}
class Sub(ast.NodeTransformer):
    def __init__(self): self.hits = []
    def visit_Compare(self, n):
        self.generic_visit(n)
        c = n.comparators[0]
        if len(n.ops) == 1 and isinstance(c, ast.Constant) and isinstance(c.value, (int, float)):
            key = KEYMAP.get((score_of(ast.unparse(n.left)), type(n.ops[0]).__name__))
            if key:
                self.hits.append((key, float(c.value)))
                n.comparators = [ast.Subscript(value=ast.Name('THR', ast.Load()), slice=ast.Constant(key), ctx=ast.Load())]
        return n
def compile_sub(fn):
    sub = Sub(); fn2 = sub.visit(ast.parse(ast.unparse(fn)).body[0])
    exec(compile(ast.fix_missing_locations(ast.Module([fn2], [])), 'bridge', 'exec'), env)
    return sub.hits
hits_needs = compile_sub(BF['needs']); hits_tail = compile_sub(tail)
# ---------------- G2: AST audit ----------------
assert hits_needs == [('hunger', .75), ('sleep_rider', .75), ('trust', .30), ('sleep', .7), ('fear', .4), ('food_joy', .6)], hits_needs
assert hits_tail == [('hunger', .75), ('trust', .30)], hits_tail
inv_needs = [(e['score'], e['op'], e['thr']) for e in INV if e['func'] == 'needs']
assert sorted(inv_needs, key=str) == sorted([('hunger', 'Gt', .75), ('sleep', 'LtE', .75), ('trust', 'Gt', .30), ('sleep', 'Gt', .7),
                                             ('fear', 'Gt', .4), (None, 'Gt', 0.0), ('food_joy', 'Gt', .6),
                                             ('curiosity', 'Gt', .35)], key=str), inv_needs
assert [(e['score'], e['op'], e['thr']) for e in INV if e['func'] == 'reply_tail'] == [('hunger', 'Gt', .75), ('trust', 'Gt', .30)]
ASIS = dict(hits_needs)
GATES['G2_ast'] = dict(ok=True, substituted=dict(needs=len(hits_needs), reply_tail=len(hits_tail)), inventory=len(INV))

for nm in ('axes', 'mood_tag'):
    exec(compile(ast.Module([MF[nm]], []), 'mood', 'exec'), env)
AX = ('fear', 'food_joy', 'salience', 'sleep', 'hunger', 'trust')
class Mood:
    axes = env['axes']; mood_tag = env['mood_tag']
    def __init__(self, row):
        for k in AX: setattr(self, k, row[k])
class Host:
    needs = env['needs']
    @contextmanager
    def session_turn(self, session): yield
    def synapse_trust(self, session): return 0.0          # display only; no comparator reads it
    def cx_intent(self, session): return None             # continuous readout, not part of the ladder
HOST = Host(); THR = env['THR'] = {}
def decide(row, thr):
    THR.clear(); THR.update(thr)
    st = SimpleNamespace(mood=Mood(row))
    reply = env['reply_tail'](row['sit'], row['event'], st)
    nd = HOST.needs(st); a = st.mood.axes()
    comp = dict(hunger=a['hunger'] > thr['hunger'], sleep_rider=a['sleep'] <= thr['sleep_rider'], sleep=a['sleep'] > thr['sleep'],
                fear=a['fear'] > thr['fear'], food_joy=a['food_joy'] > thr['food_joy'], trust=row['trust'] > thr['trust'],
                hunger_reply=row['hunger'] > thr['hunger'])
    return dict(reply=reply, amb=nd['intent'], tag=nd['mood'], comp=comp)

# ---------------- G3: regime-A replay reproduces every stored decision ----------------
def g3(recs):
    n = bad = 0
    for r in recs.values():
        rows = [x for ses in r['sessions'].values() for nm in ORDER for x in ses[nm]] + r['quiet']
        for x in rows:
            d = decide(x, ASIS); n += 1
            bad += (d['reply'], d['amb'], d['tag']) != (x['intent'], x['ambient'], f"{x['mood']}:{x['level']}")
    return n, bad
n, bad = g3(REC); assert n == 4 * (4 * 192 + 1) and bad == 0, ('G3', n, bad)
GATES['G3_replay'] = dict(ok=True, turns=n, mismatches=bad)

# ---------------- thresholds ----------------
PLACED = ('hunger', 'trust', 'sleep', 'fear', 'food_joy')
calib = {k: np.array([x[k] for s in (0, 1) for nm in ORDER for x in REC[(s, 'frozen')]['sessions']['S1'][nm]], dtype=float) for k in AX}
assert all(len(v) == 384 for v in calib.values())
P70 = {k: float(np.percentile(calib[k], 70)) for k in PLACED}
B = dict(hunger=P70['hunger'], trust=P70['trust'], sleep_rider=P70['sleep'], sleep=P70['sleep'], fear=P70['fear'], food_joy=P70['food_joy'])
BN = dict(ASIS, fear=P70['fear'], food_joy=P70['food_joy'])
STAGE = dict(S1=None, S2='D1', S3='D2', R='R')
def drift(rec, ses):
    st = STAGE[ses]
    if st is None: return 0.0, 0.0
    c = next(c for c in rec['census'] if c['tag'] == st)
    return c['FEAR']['mean_abs_rel'], c['JOY_SAL']['mean_abs_rel']
def margin(base, rec, ses, kappa):
    df, dj = drift(rec, ses)
    return dict(base, fear=base['fear'] * (1 - kappa * df), food_joy=base['food_joy'] * (1 - kappa * dj))
REG = {'A': lambda rec, ses: ASIS, 'B': lambda rec, ses: B, 'C': lambda rec, ses: margin(ASIS, rec, ses, 1),
       'Bn': lambda rec, ses: BN, 'C2': lambda rec, ses: margin(ASIS, rec, ses, 2),
       'C4': lambda rec, ses: margin(ASIS, rec, ses, 4), 'BC': lambda rec, ses: margin(B, rec, ses, 1)}
REGISTERED = tuple(REG)
# ADDENDUM.md (post-hoc, declared before any held-out record existed): food_joy-only placement.
assert pin(D / 'ADDENDUM.md') == (D / 'ADDENDUM.sha256').read_text().split()[0], 'addendum changed after lock'
BJ = dict(ASIS, food_joy=P70['food_joy'])
REG['Bj'] = lambda rec, ses: BJ

# ---------------- the boundary map ----------------
def dist(v, op, thr, view=None):
    v = np.asarray(v, float); w = v if view is None else np.asarray(view, float)
    fire = {'Gt': w > thr, 'Lt': w < thr, 'LtE': w <= thr, 'GtE': w >= thr}[op]
    below = v[v <= thr]; above = v[v > thr]
    return dict(n=len(v), q={str(q): round(float(np.percentile(v, q)), 4) for q in (0, 10, 25, 50, 70, 75, 90, 100)},
                fire_share=round(float(fire.mean()), 4), thr_pct_rank=round(float((v < thr).mean()), 4),
                nearest_below=None if not len(below) else round(float(below.max()), 4),
                nearest_above=None if not len(above) else round(float(above.min()), 4),
                gap=None if not (len(below) and len(above)) else round(float(above.min() - below.max()), 4),
                within_05=int((np.abs(v - thr) <= .05).sum()))
def battery_vals(recs, seeds, ses, k):
    return [x.get(k, 0.0) for s in seeds for nm in ORDER for x in recs[(s, 'frozen')]['sessions'][ses][nm]]
TICK = dict(fear=2, food_joy=3, salience=4, sleep=5, hunger=6, curiosity=7)
def world_vals(recs, seeds, k):
    return [t[TICK[k]] for s in seeds for d in recs[(s, 'frozen')]['days'] for t in d['ticks']]
def build_map(recs, seeds):
    out = []
    for e in INV:
        m = dict(e)
        if e['score'] is None or e['klass'] == 'MOTOR':
            m['note'] = 'not a score comparator (state flag, rng, clock or time window)'
        elif e['klass'] in ('INTENT/reply', 'INTENT/needs', 'TAG'):
            if e['score'] == 'curiosity':
                m['note'] = 'unreachable in a conversation session (no curiosity, no curious_at); degenerate 0.0'
            else:
                rounded = e['left'].startswith('a[')
                for ses in ('S1', 'R'):
                    v = battery_vals(recs, seeds, ses, e['score'])
                    m[ses] = dist(v, e['op'], e['thr'], [round(x, 3) for x in v] if rounded else None)
                m['source'] = 'frozen battery, post-turn'
        elif e['score'] in TICK:
            m['world'] = dist(world_vals(recs, seeds, e['score']), e['op'], e['thr'])
            m['source'] = 'frozen day ticks, post-act values rounded 5 dp (the comparator read the pre-act value)'
        else:
            m['note'] = 'world-session trust is not stored per tick'
        out.append(m)
    return out

# ---------------- evaluation ----------------
def binom_tail(k, n, p):
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))) if n else None
def reversals(seq): return sum(seq[t] == seq[t + 2] != seq[t + 1] for t in range(len(seq) - 2))
SCORE_OF_KEY = dict(hunger='hunger', trust='trust', sleep_rider='sleep', sleep='sleep', fear='fear', food_joy='food_joy')

def world_settle(rec, thr):
    out = []
    for d in rec['days']:
        c = 0
        for t in d['ticks']:
            h, s = round(t[6], 3), round(t[5], 3)
            c += (not (h > thr['hunger'] and s <= thr['sleep_rider'])) and s > thr['sleep']
        out.append(int(c))
    return out

def evaluate(recs, seeds):
    res = {}
    dec = {}
    for rg, tf in REG.items():
        for s in seeds:
            for arm in ('frozen', 'plastic'):
                rec = recs[(s, arm)]
                for ses in ('S1', 'S2', 'S3', 'R'):
                    thr = tf(rec, ses)
                    dec[(rg, s, arm, ses)] = ({nm: [decide(x, thr) for x in rec['sessions'][ses][nm]] for nm in ORDER}, dict(thr))
    def flips(rg, s, ses):
        dF, tF = dec[(rg, s, 'frozen', ses)]; dP, tP = dec[(rg, s, 'plastic', ses)]; out = []
        for nm in ORDER:
            for i in range(8):
                f, p = dF[nm][i], dP[nm][i]
                if (f['reply'], f['amb']) != (p['reply'], p['amb']):
                    xf = recs[(s, 'frozen')]['sessions'][ses][nm][i]; xp = recs[(s, 'plastic')]['sessions'][ses][nm][i]
                    near = any(abs(xf[SCORE_OF_KEY[k]] - t[k]) <= .05 for t in (tF, tP) for k in SCORE_OF_KEY)
                    out.append(dict(seed=s, conv=nm, turn=i + 1, arc=ARC[nm], event=xf['event'], reply=[f['reply'], p['reply']],
                                    amb=[f['amb'], p['amb']], near=bool(near),
                                    crossed=[k for k in f['comp'] if f['comp'][k] != p['comp'][k]],
                                    food_joy=[xf['food_joy'], xp['food_joy']], fear=[xf['fear'], xp['fear']],
                                    sleep=[xf['sleep'], xp['sleep']]))
        return out
    tagflips = {s: [(nm, i) for nm in ORDER for i in range(8)
                    if dec[('A', s, 'frozen', 'R')][0][nm][i]['tag'] != dec[('A', s, 'plastic', 'R')][0][nm][i]['tag']] for s in seeds}
    for rg in REG:
        o = {}
        fl = [f for s in seeds for f in flips(rg, s, 'R')]
        o['thr_frozen_R'] = dec[(rg, seeds[0], 'frozen', 'R')][1]
        o['thr_plastic_R'] = {s: dec[(rg, s, 'plastic', 'R')][1] for s in seeds}
        o['flips_R'] = fl
        o['N_all'] = len(fl); o['N_near'] = sum(f['near'] for f in fl)
        o['N_by_seed'] = {s: sum(f['seed'] == s for f in fl) for s in seeds}
        o['reply_flips'] = sum(f['reply'][0] != f['reply'][1] for f in fl)
        o['ambient_flips'] = sum(f['amb'][0] != f['amb'][1] for f in fl)
        cr = {}
        for f in fl:
            for k in f['crossed']: cr[k] = cr.get(k, 0) + 1
        o['crossed'] = cr
        tr = {}
        for f in fl:
            k = '->'.join(f['amb']); tr[k] = tr.get(k, 0) + 1
        o['ambient_transitions'] = tr
        o['flips_by_session'] = {ses: [len(flips(rg, s, ses)) for s in seeds] for ses in ('S1', 'S2', 'S3', 'R')}
        # noise control: frozen R vs frozen S3, same regime
        o['noise_control'] = int(sum((dec[(rg, s, 'frozen', 'R')][0][nm][i]['reply'], dec[(rg, s, 'frozen', 'R')][0][nm][i]['amb'])
                                     != (dec[(rg, s, 'frozen', 'S3')][0][nm][i]['reply'], dec[(rg, s, 'frozen', 'S3')][0][nm][i]['amb'])
                                     for s in seeds for nm in ORDER for i in range(8)))
        # collateral vs regime A, frozen R
        tot = len(seeds) * 192
        o['collateral_ambient'] = sum(dec[(rg, s, 'frozen', 'R')][0][nm][i]['amb'] != dec[('A', s, 'frozen', 'R')][0][nm][i]['amb']
                                      for s in seeds for nm in ORDER for i in range(8)) / tot
        o['collateral_reply'] = sum(dec[(rg, s, 'frozen', 'R')][0][nm][i]['reply'] != dec[('A', s, 'frozen', 'R')][0][nm][i]['reply']
                                    for s in seeds for nm in ORDER for i in range(8)) / tot
        for arm in ('frozen', 'plastic'):
            h = {}
            for s in seeds:
                for nm in ORDER:
                    for x in dec[(rg, s, arm, 'R')][0][nm]: h[x['amb']] = h.get(x['amb'], 0) + 1
            o[f'ambient_hist_{arm}'] = dict(sorted(h.items()))
            h = {}
            for s in seeds:
                for nm in ORDER:
                    for x in dec[(rg, s, arm, 'R')][0][nm]: h[x['reply']] = h.get(x['reply'], 0) + 1
            o[f'reply_hist_{arm}'] = dict(sorted(h.items()))
        # Q2
        byarc = {}
        for f in fl: byarc[f['arc']] = byarc.get(f['arc'], 0) + 1
        kf = sum(f['conv'] in KF for f in fl); convs = sorted({(f['seed'], f['conv']) for f in fl})
        o['Q2'] = dict(by_arc=byarc, n=len(fl), kf=kf, share=None if not fl else kf / len(fl), base=7 / 24,
                       binom_tail=binom_tail(kf, len(fl), 7 / 24), convs_with_flip=len(convs),
                       convs_kf=sum(c[1] in KF for c in convs), by_event={},
                       supported=None if not fl else bool(kf / len(fl) >= .5 and binom_tail(kf, len(fl), 7 / 24) < .05))
        for f in fl: o['Q2']['by_event'][str(f['event'])] = o['Q2']['by_event'].get(str(f['event']), 0) + 1
        # Q3
        q3 = {}
        for arm in ('frozen', 'plastic'):
            rv = [reversals([x['amb'] for x in dec[(rg, s, arm, 'R')][0][nm]]) for s in seeds for nm in ORDER]
            q3[arm] = dict(mean=float(np.mean(rv)), max=int(max(rv)), convs_ge2=int(sum(v >= 2 for v in rv)), total=int(sum(rv)))
        tg = []
        for s in seeds:
            fs = {(f['conv'], f['turn']) for f in fl if f['seed'] == s}
            tg += [reversals([(nm, i + 1) in fs for i in range(8)]) for nm in ORDER]
        q3['paired_toggles'] = dict(mean=float(np.mean(tg)), max=int(max(tg)))
        q3['supported'] = bool(q3['plastic']['mean'] < 1.0)
        o['Q3'] = q3
        # Q4
        bad_i = []; pos = {'frozen': 0, 'plastic': 0}; one_arm = []
        for s in seeds:
            dF = dec[(rg, s, 'frozen', 'R')][0]; dP = dec[(rg, s, 'plastic', 'R')][0]
            for nm in ORDER:
                for i in range(8):
                    f, p = dF[nm][i], dP[nm][i]
                    night = nm == 'bedtime' or recs[(s, 'frozen')]['sessions']['R'][nm][i]['sit'] == 'night'
                    if night:
                        if (f['reply'], f['amb']) != (p['reply'], p['amb']): bad_i.append((s, nm, i + 1))
                        pos['frozen'] += 'settle' in (f['reply'], f['amb']); pos['plastic'] += 'settle' in (p['reply'], p['amb'])
                    if (f['amb'] == 'settle') != (p['amb'] == 'settle'): one_arm.append((s, nm, i + 1))
        setR = {(s, nm, i) for s in seeds for nm in ORDER for i in range(8) if dec[(rg, s, 'frozen', 'R')][0][nm][i]['amb'] == 'settle'}
        setA = {(s, nm, i) for s in seeds for nm in ORDER for i in range(8) if dec[('A', s, 'frozen', 'R')][0][nm][i]['amb'] == 'settle'}
        wA = [world_settle(recs[(s, 'frozen')], ASIS) for s in seeds]
        wR = [world_settle(recs[(s, 'frozen')], dec[(rg, s, 'frozen', 'R')][1]) for s in seeds]
        ratio = [[(r / a if a else None) for r, a in zip(x, y)] for x, y in zip(wR, wA)]
        p_i = not bad_i and min(pos.values()) >= 1 and not one_arm
        p_ii = setR == setA
        p_iii = all(v is not None and abs(v - 1) <= .05 for row in ratio for v in row)
        o['Q4'] = dict(i=dict(ok=bool(p_i), night_turn_diffs=bad_i, settle_pos=pos, settle_one_arm=one_arm),
                       ii=dict(ok=bool(p_ii), settle_turns_regime=len(setR), settle_turns_A=len(setA),
                               added=len(setR - setA), lost=len(setA - setR)),
                       iii=dict(ok=bool(p_iii), world_settle_ticks_regime=wR, world_settle_ticks_A=wA, ratio=ratio),
                       supported=bool(p_i and p_ii and p_iii))
        # Q1
        o['Q1'] = dict(N_near=o['N_near'], N_all=o['N_all'], noise=o['noise_control'], by_seed=o['N_by_seed'],
                       supported=bool(o['N_near'] >= 10 and o['N_near'] > o['noise_control'] and min(o['N_by_seed'].values()) > 0))
        # item 4
        it = {}
        for s in seeds:
            f = dec[(rg, s, 'frozen', 'R')][0]['picked_up'][4]; p = dec[(rg, s, 'plastic', 'R')][0]['picked_up'][4]
            xf = recs[(s, 'frozen')]['sessions']['R']['picked_up'][4]; xp = recs[(s, 'plastic')]['sessions']['R']['picked_up'][4]
            it[s] = dict(tag=[f['tag'], p['tag']], reply=[f['reply'], p['reply']], amb=[f['amb'], p['amb']],
                         behaviour_differs=bool((f['reply'], f['amb']) != (p['reply'], p['amb'])),
                         salience=[xf['salience'], xp['salience']], food_joy=[xf['food_joy'], xp['food_joy']],
                         fear=[xf['fear'], xp['fear']], sleep=[xf['sleep'], xp['sleep']], hunger=[xf['hunger'], xp['hunger']])
        o['item4_picked_up_t5'] = it
        fs = {(f['seed'], f['conv'], f['turn']) for f in fl}
        o['tagflip_turns'] = {s: [dict(conv=nm, turn=i + 1, action_flip=(s, nm, i + 1) in fs) for nm, i in tagflips[s]] for s in seeds}
        o['tagflips_with_action'] = sum(t['action_flip'] for v in o['tagflip_turns'].values() for t in v)
        o['structural'] = dict(reply_flips_all_sessions=sum(f['reply'][0] != f['reply'][1] for s in seeds for ses in ('S1', 'S2', 'S3', 'R')
                                                             for f in flips(rg, s, ses)),
                               frozen_equals_A=bool(all(dec[(rg, s, 'frozen', ses)][0] == dec[('A', s, 'frozen', ses)][0]
                                                        for s in seeds for ses in ('S1', 'S2', 'S3', 'R'))))
        res[rg] = o
    return res, {s: len(v) for s, v in tagflips.items()}

OUT = dict(prereg=PREREG, gates=GATES, asis=ASIS, P70=P70, regimes_static=dict(A=ASIS, B=B, Bn=BN),
           drift_R={f'{s}_{a}': dict(zip(('FEAR', 'JOY_SAL'), drift(REC[(s, a)], 'R'))) for (s, a) in REC},
           inventory=INV)
OUT['map'] = build_map(REC, (0, 1))
res, tagn = evaluate(REC, (0, 1))
# ---------------- G4: regime A reproduces v2's stored headline ----------------
v2s = json.loads((V2 / 'scores.json').read_text())
assert res['A']['N_all'] == 0 == v2s['Q2']['action']['N'] and sum(tagn.values()) == 12 == v2s['Q2']['tag']['N'], (res['A']['N_all'], tagn)
wa = [(a, b) for s in (0, 1) for a, b in [(sum(t[1] == 'settle' for d in REC[(s, 'frozen')]['days'] for t in d['ticks']),
                                           sum(world_settle(REC[(s, 'frozen')], ASIS)))]]
GATES['G4_v2_headline'] = dict(ok=True, action_flips_A=0, tag_flips=tagn)
GATES['world_settle_anchor'] = dict(stored_vs_reread=wa, note='stored ambient==settle ticks vs regime-A settle read (reported, not halting)')
OUT['primary'] = res
OUT['registered_regimes'] = list(REGISTERED); OUT['posthoc_regimes'] = ['Bj']
asrun = json.loads((D / 'results_primary_asrun.json').read_text())['primary']     # the pre-addendum run, kept verbatim
now = json.loads(json.dumps(res, default=str))
assert all(now[rg] == asrun[rg] for rg in REGISTERED), 'a registered regime moved when Bj was added'
(D / 'results.json').write_text(json.dumps(OUT, indent=1, allow_nan=False, default=str))

def show(tag, res):
    print(f'\n== {tag} ==')
    print('regime  N_near N_all noise seeds   Q1    Q2share(kf/n,p)        Q3 rev P/F     Q4 i/ii/iii   collat  tagflip+act')
    for rg, o in res.items():
        q2 = o['Q2']; q3 = o['Q3']; q4 = o['Q4']
        print(f"{rg:6} {o['N_near']:6} {o['N_all']:5} {o['noise_control']:5} {str(list(o['N_by_seed'].values())):8} {str(o['Q1']['supported'])[0]}"
              f"   {q2['kf']}/{q2['n']} p={q2['binom_tail'] if q2['binom_tail'] is None else round(q2['binom_tail'], 4)} {str(q2['supported'])[0]}"
              f"   {q3['plastic']['mean']:.3f}/{q3['frozen']['mean']:.3f} max{q3['plastic']['max']} {str(q3['supported'])[0]}"
              f"   {int(q4['i']['ok'])}/{int(q4['ii']['ok'])}/{int(q4['iii']['ok'])} {str(q4['supported'])[0]}"
              f"   {o['collateral_ambient']:.3f}  {o['tagflips_with_action']}")
print('gates', json.dumps(GATES)); print('ASIS', ASIS); print('P70', {k: round(v, 5) for k, v in P70.items()})
print('drift_R', OUT['drift_R'])
show('primary seeds 0,1 (RETEST, 384 turns)', res)

if HELD:
    assert pin(D / 'run.py') == pin(V2 / 'run.py'), 'G5 run.py is not the v2 harness'
    HR = {(s, a): load(s, a, D / 'out') for s in HELD for a in ('frozen', 'plastic')}
    assert all(r['prereg'] == PREREG for r in HR.values())
    n, bad = g3(HR); assert bad == 0, ('G3 held-out', n, bad)
    g5 = None
    if 2 in HELD:
        v1 = json.loads((L / 'duckplast' / 'results.json').read_text())
        h = next(h for h in v1['histories'] if h['seed'] == 2 and h['eta'] == 0)
        lab = 0; mx = 0.0
        for nm in ORDER:
            for a, b in zip(h['battery'][nm], HR[(2, 'frozen')]['sessions']['S1'][nm]):
                lab += any(a[k] != b[k] for k in ('sit', 'event', 'mood', 'level', 'intent'))
                mx = max(mx, *(abs(a[k1] - b[k2]) for k1, k2 in (('fear', 'fear'), ('hunger', 'hunger'), ('sleep', 'sleep'), ('body', 'trust'))))
        assert lab == 0 and mx == 0.0, ('G5', lab, mx)
        g5 = dict(ok=True, turns=192, label_mismatches=lab, max_abs_diff=mx)
    hres, htag = evaluate(HR, tuple(HELD))
    HO = dict(prereg=PREREG, seeds=HELD, gates=dict(G3_replay=dict(turns=n, mismatches=bad), G5_v1_anchor_seed2=g5, run_py=pin(D / 'run.py')),
              tag_flips=htag, drift_R={f'{s}_{a}': dict(zip(('FEAR', 'JOY_SAL'), drift(HR[(s, a)], 'R'))) for (s, a) in HR},
              map=build_map(HR, tuple(HELD)), heldout=hres,
              frozen_fire_share_at_P70={k: float((np.array([x[k] for s in HELD for nm in ORDER for x in HR[(s, 'frozen')]['sessions']['R'][nm]]) > P70[k]).mean())
                                        for k in PLACED})
    (D / 'results_heldout.json').write_text(json.dumps(HO, indent=1, allow_nan=False, default=str))
    print('held-out gates', json.dumps(HO['gates']), 'tag flips', htag)
    show(f'held-out seeds {HELD} (RETEST)', hres)
