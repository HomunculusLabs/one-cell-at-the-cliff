"""duck plasticity v2 — one arm-seed job. OFFLINE ONLY.
Her live modules are imported read-only (-B, no pycache); her routing code is
source-sliced from bridge.py (never instantiating DuckBridge: no LLM, no
service, no session files). All writes land in duckplast2/out/.

argv: seed arm(frozen|plastic) K_idle n_threads [smoke]
"""
import ast, hashlib, json, os, random, sys, time, zlib
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

D = Path(__file__).resolve().parent; L = D.parent; P = L.parent / 'peabrain'; U = L.parent / 'puddle'
SEED = int(sys.argv[1]); ARM = sys.argv[2]; K_IDLE = int(sys.argv[3]); NT = int(sys.argv[4])
SMOKE = len(sys.argv) > 5
assert ARM in ('frozen', 'plastic')
ETA = 0.05 if ARM == 'plastic' else 0.0
ETA_NIGHT = 2 * ETA
BAND = 0.20
sys.path[:0] = map(str, (P, U, L)); os.environ['PEBRAIN_FORCE_HOUR'] = '12'
pin = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PREREG = pin(D / 'PREREG.md')
assert PREREG == (D / 'PREREG.sha256').read_text().split()[0], 'prereg changed after lock'

import torch
torch.set_num_threads(NT); torch.set_num_interop_threads(1); torch.manual_seed(0); torch.set_grad_enabled(False)
from brain import FlyBrain
from senses import DuckSenses
from mood import MoodState, darkness_now
from engine import PuddleMind
from scenarios import SCENARIOS

# ---- source-slice her routing: every top-level constant + the pure routing methods
mod = ast.parse((P / 'bridge.py').read_text())
cls = next(n for n in mod.body if isinstance(n, ast.ClassDef) and n.name == 'DuckBridge')
env = {'os': os, '__file__': str(D / 'lab_slice.py'), 'torch': torch}
for n in mod.body:
    if isinstance(n, ast.Assign):
        exec(compile(ast.Module([n], []), 'bridge', 'exec'), env)
DIARY = []
env['diary_append'] = lambda s, act, text, t: DIARY.append(act)     # lab stub: memory only
WANT = ('synapse_trust', 'cx_intent', '_reply_inside', 'needs', 'world_tick', '_dabble', 'dream')
for n in cls.body:
    if isinstance(n, ast.FunctionDef) and n.name in WANT:
        if n.name == '_reply_inside':       # cut immediately before speech
            cut = next(i for i, v in enumerate(n.body)
                       if isinstance(v, ast.Assign) and ast.unparse(v.targets[0]) == 'pre')
            n.body = n.body[:cut] + ast.parse('return sit,event,mood,level,intent').body
        exec(compile(ast.fix_missing_locations(ast.Module([n], [])), 'bridge', 'exec'), env)
KIND, MEAN = env['KIND_EVENTS'], env['MEAN_EVENTS']
assert env['NIGHT_ETA'] / env['PLAS_ETA'] == 2.0

t0 = time.monotonic()
b = FlyBrain(str(P / 'brain_graph.pt'), 'cpu'); b.op_gain = .95 / b.rho
s = DuckSenses(b, str(P / 'data/neuron_annotations.tsv'))

# ---- the declared plastic set: every CSR entry INTO the intent-feeding readout cells
N = b.N
pop = torch.full((N,), -1, dtype=torch.int8)                       # precedence FEAR > JOY/SAL > MOTOR
pop[s.dn['all']] = 2
for k in ('serotonin', 'dopamine'): pop[b.mod_idx[k]] = 1
pop[s.probes['DAN']] = 1
pop[b.mod_idx['octopamine']] = 0; pop[s.probes['LC']] = 0
rows = torch.nonzero(pop >= 0).flatten()
crow = b.W.crow_indices().long(); cnt = crow[rows + 1] - crow[rows]
idx = torch.cat([torch.arange(crow[r], crow[r + 1]) for r in rows.tolist()])
src = b.W.col_indices()[idx].long(); dst = rows.repeat_interleave(cnt)
w0 = b.W.values()[idx].clone(); aw = w0.abs(); cap = BAND * aw
epop = pop[dst].long(); coef = torch.where(epop == 0, -1.0, 1.0) * aw
POPS = ('FEAR', 'JOY_SAL', 'MOTOR')
cells = [int((pop == i).sum()) for i in range(3)]; edges = [int((epop == i).sum()) for i in range(3)]
assert cells == [995, 3293, 1211] and edges == [238989, 398951, 309059] and len(idx) == 946999, (cells, edges)
d = torch.zeros_like(w0)
W_SUM0 = float(b.W.values().double().sum())

def apply_rule(event, eta):
    v = 1.0 if event in KIND else -1.0 if event in MEAN else 0.0
    if not eta or not v: return
    xs, xd = b.X[src], b.X[dst]
    d.add_(eta * v * coef * xs * xd * ((xs > .05) & (xd > .05))).clamp_(-cap, cap)
    b.active_delta = (src, dst, d)          # her brain's native per-step delta hook

def census(tag):
    assert torch.all(d.abs() <= cap * (1 + 1e-6)) and torch.all(torch.sign(w0 + d) == torch.sign(w0))
    assert ETA or not d.any()
    out = dict(tag=tag, T=SIM.T)
    for i, nm in enumerate(POPS):
        m = epop == i; r = d[m] / aw[m]
        out[nm] = dict(edges=int(m.sum()), changed=int((r != 0).sum()), at_cap=int((r.abs() >= BAND * (1 - 1e-5)).sum()),
                       mean_abs_rel=float(r.abs().mean()), mean_signed_rel=float(r.mean()), max_abs_rel=float(r.abs().max()))
    r = d / aw
    out['ALL'] = dict(edges=len(d), changed=int((r != 0).sum()), at_cap=int((r.abs() >= BAND * (1 - 1e-5)).sum()),
                      mean_abs_rel=float(r.abs().mean()), max_abs_rel=float(r.abs().max()))
    CENSUS.append(out); print('census', json.dumps(out), round(time.monotonic() - t0), flush=True)

SIM = SimpleNamespace(T=43200.0)
CENSUS, PASSES = [], []
native_step = b.step
STEPS = [0]

class WindowMood(MoodState):
    """v1 stimulus-window assay: first `limit` native steps of an observe call run, X held after."""
    world = False
    def observe(self, seconds, event=None):
        remaining = 20 if (event or not self.world) else K_IDLE
        def bounded(**kw):
            nonlocal remaining
            if remaining:
                remaining -= 1; STEPS[0] += 1
                return native_step(**kw)
            return b.X
        b.step = bounded
        try: return super().observe(seconds, event)
        finally: b.step = native_step

class Host:
    synapse_trust = env['synapse_trust']; cx_intent = env['cx_intent']; reply = env['_reply_inside']
    needs = env['needs']; world_tick = env['world_tick']; _dabble = env['_dabble']; dream = env['dream']
    CX_BASE, CX_SPAN = next(ast.literal_eval(n.value) for n in cls.body
                            if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == '(CX_BASE, CX_SPAN)')
    brain = b; senses = s; learn = True; peek = False

    @contextmanager
    def session_turn(self, session):                      # lab port: sim clock, no wall clock, no X swap
        if getattr(session, 'world', False) and not self.peek:
            idle = min(SIM.T - session.last_seen, 600.0)
            if idle > 1.0: session.mood.observe(idle)
            session.last_seen = SIM.T
        yield

    def _hebbian(self, session, event):                   # the declared v2 rule replaces her DAN-only write
        if self.learn: apply_rule(event, ETA)

    def _log_event(self, session, event):                 # lab port: sim-clock stamp, into the world day log
        if not event: return
        pk = session.mood.last_peak or {}
        WORLD.day_log.append({'ev': event, 't': SIM.T, 'dan': round(pk.get('dan', 0.0), 4),
                              'kc': round(pk.get('kc', 0.0), 4), 'dop': round(pk.get('dop', 0.0), 4),
                              'sal': session.mood.salience})
        WORLD.day_log = WORLD.day_log[-100:]

    def consolidate_night(self, w):                       # lab port of her L3 pass on the simulated calendar
        today = int(SIM.T // 86400)
        log = [e for e in w.day_log if int(e['t'] // 86400) == today]
        if darkness_now() < 0.6 or w.mood.sleep <= 0.6 or w.night_stamp == today or not log:
            w.day_log = log; return None
        w.night_stamp = today
        ranked = sorted(log, key=lambda e: -e['dop'])
        n = max(1, min(env['MAX_REPLAYS'], int(len(ranked) * env['TOP_FRAC'] + 0.999))); chosen = ranked[:n]
        dreamed, written = [], []
        with self.session_turn(w):
            for e in chosen:
                ev = e['ev']; I = s.input_for(ev) * env['DREAM_GAIN']
                for _ in range(20):
                    native_step(I=I, gain=b.op_gain); STEPS[0] += 1
                if ev in KIND:
                    apply_rule(ev, ETA_NIGHT); written.append(ev)
                dreamed.append(ev)
            d.mul_(env['NIGHT_DOWNSCALE'])
        w.mood.learn_pressure = min(0.2, 0.05 * len(chosen)); w.day_log = []
        w.dream_pool = list(dict.fromkeys(dreamed)); w.dreams_tonight = 0
        PASSES.append(dict(T=SIM.T, hour=round(SIM.T / 3600 % 24, 2), date=today, n_log=len(log),
                           log_events=sorted(set(e['ev'] for e in log)),
                           chosen=[(e['ev'], e['dop'], int(e['t'])) for e in chosen], written=written))
        return 'consolidate'

h = Host()
AX = ('fear', 'food_joy', 'salience', 'sleep', 'hunger', 'trust')

def conversation(name, msgs, gaps, keystr, learn):
    key = zlib.crc32(keystr.encode()) & 0x7fffffff
    b.gen.manual_seed(key); b.seed(); m = WindowMood(s); m.observe(30)
    st = SimpleNamespace(mood=m, mind=PuddleMind(env['CARD'], random.Random(key)), plas_d=d)
    h.learn = learn; out = []
    for i, text in enumerate(msgs):
        if i: m.observe(gaps[i - 1])
        sit, event, mood, level, intent = h.reply(text, st)
        row = dict(sit=sit, event=event, mood=mood, level=level, intent=intent, ambient=h.needs(st)['intent'],
                   cx=h.cx_intent(st), peak=dict(m.last_peak) if m.last_peak else None)
        row.update({k: float(getattr(m, k)) for k in AX}); out.append(row)
    return out

def battery(tag, learn):
    os.environ['PEBRAIN_FORCE_HOUR'] = '12'; out = {}
    for sc in SCEN:
        n = sc['name']
        keystr = f'{n}|{SEED}' if tag == 'S1' else f'{n}|{SEED}|{tag}'      # S1 = v1's key (anchor)
        out[n] = conversation(n, sc['messages'], sc['gaps'], keystr, learn)
    print('battery', tag, 'steps', STEPS[0], round(time.monotonic() - t0), flush=True)
    return out

def day(k):
    b.gen.manual_seed(zlib.crc32(f'world|{SEED}|D{k}'.encode()) & 0x7fffffff); b.seed()
    base = SIM.T; ticks = []; npass = len(PASSES)
    for i in range(1, NTICK + 1):
        SIM.T = base + i * TICK_S
        os.environ['PEBRAIN_FORCE_HOUR'] = repr(SIM.T / 3600 % 24)
        act = h.world_tick(WORLD, WRNG)
        m = WORLD.mood; h.peek = True; amb = h.needs(WORLD)['intent']; h.peek = False     # read-only poll
        ticks.append([act, amb, round(m.fear, 5), round(m.food_joy, 5), round(m.salience, 5),
                      round(m.sleep, 5), round(m.hunger, 5), round(WORLD.curiosity, 5)])
    os.environ['PEBRAIN_FORCE_HOUR'] = '12'
    print('day', k, 'steps', STEPS[0], 'passes', len(PASSES) - npass, round(time.monotonic() - t0), flush=True)
    return dict(day=k, ticks=ticks, passes=PASSES[npass:], hoard=WORLD.hoard)

SCEN = SCENARIOS if not SMOKE else [x for x in SCENARIOS if x['name'] in ('kindness_slow', 'picked_up')]
NTICK, TICK_S = (1920, 45.0) if not SMOKE else (96, 900.0)
NDAY = 3 if not SMOKE else 1
assert abs(NTICK * TICK_S - 86400) < 1e-6

# her solo life: one persistent world state (mood, drives, day log, rng)
b.gen.manual_seed(zlib.crc32(f'world|{SEED}'.encode()) & 0x7fffffff); b.seed()
wm = WindowMood(s); wm.observe(30); wm.world = True
WORLD = SimpleNamespace(mood=wm, world=True, last_seen=SIM.T, plas_d=d, diary=[], day_log=[], night_stamp=None,
                        curiosity=0.0, curious_at=None, hoard=0, parade_ticks=0)
WRNG = random.Random(zlib.crc32(f'worldrng|{SEED}'.encode()) & 0x7fffffff)

R = dict(seed=SEED, arm=ARM, eta=ETA, eta_night=ETA_NIGHT, band=BAND, k_idle=K_IDLE, threads=NT, smoke=SMOKE, prereg=PREREG,
         sources={p.name: pin(p) for p in (P / 'bridge.py', P / 'brain.py', P / 'senses.py', P / 'mood.py', U / 'engine.py',
                                           L / 'scenarios.py', P / 'brain_graph.pt')},
         cells=dict(zip(POPS, cells)), edges=dict(zip(POPS, edges)), graph_edges=b.W._nnz(), sessions={}, days=[])
OUT = D / 'out'; OUT.mkdir(exist_ok=True); STEM = f"{'smoke_' if SMOKE else ''}seed{SEED}_{ARM}"
def checkpoint():                       # progress survives a wall cut; scored only if the full file is missing
    R.update(census=CENSUS, steps=STEPS[0], seconds=time.monotonic() - t0)
    tmp = OUT / (STEM + '.partial.tmp'); tmp.write_text(json.dumps(R, allow_nan=False)); tmp.replace(OUT / (STEM + '.partial.json'))
for k in range(1, NDAY + 1):
    R['sessions'][f'S{k}'] = battery(f'S{k}', True); census(f'S{k}'); checkpoint()
    R['days'].append(day(k)); census(f'D{k}'); checkpoint()
R['sessions']['R'] = battery('R', False)
R['quiet'] = conversation('probe_quiet', ['the clouds are grey'], [], f'probe_quiet|{SEED}|R', False)
census('R')
assert float(b.W.values().double().sum()) == W_SUM0, 'weight matrix was written'      # W itself never touched
R.update(census=CENSUS, steps=STEPS[0], seconds=time.monotonic() - t0, diary_acts=len(DIARY))
(OUT / (STEM + '.json')).write_text(json.dumps(R, allow_nan=False))
print('done', STEPS[0], 'steps', round(R['seconds']), 's', flush=True)
