"""Score duck plasticity v2 against PREREG.md. Reads out/seed*_{frozen,plastic}.json
(falls back to .partial.json and says so). Writes scores.json + score.log text to stdout."""
import collections, json, statistics as st, sys
from pathlib import Path
D = Path(__file__).resolve().parent; O = D / 'out'
sys.path.insert(0, str(D.parent))
from scenarios import SCENARIOS
ARC = {s['name']: s['arc'] for s in SCENARIOS}
SEEDS = [0, 1]
ACT_B = [('hunger', .75), ('trust', .30), ('sleep', .70), ('sleep', .75), ('fear', .40), ('food_joy', .60)]
TAG_B = [('fear', .08), ('fear', .25), ('fear', .50), ('trust', .15), ('trust', .20), ('trust', .55), ('salience', .15),
         ('salience', .30), ('hunger', .75), ('hunger', .90), ('food_joy', .35), ('food_joy', .60), ('sleep', .75)]
mean = lambda v: st.mean(v) if v else float('nan')
P = print

def load(seed, arm):
    f = O / f'seed{seed}_{arm}.json'; partial = False
    if not f.exists(): f = O / f'seed{seed}_{arm}.partial.json'; partial = True
    return json.loads(f.read_text()), partial

H = {}; PARTIAL = []
for s in SEEDS:
    for a in ('frozen', 'plastic'):
        H[s, a], part = load(s, a)
        if part: PARTIAL.append((s, a))
SESS = [k for k in ('S1', 'S2', 'S3', 'R') if all(k in H[key]['sessions'] for key in H)]
FINAL = 'R' if 'R' in SESS else SESS[-1]
S = dict(seeds=SEEDS, partial=PARTIAL, sessions=SESS, final=FINAL, prereg=H[0, 'frozen']['prereg'])
P('duck plasticity v2 — score. prereg', S['prereg']); P('sessions scored:', SESS, '| final =', FINAL, '| partial files:', PARTIAL)
P('steps/seconds per job:', {f'{k[0]}{k[1][0]}': (v['steps'], round(v['seconds'])) for k, v in H.items()})

def turns(seed, arm, sess):
    for n, arc in H[seed, arm]['sessions'][sess].items():
        for i, x in enumerate(arc): yield n, i + 1, x
def pairs(seed, sa, sb, arm_a='frozen', arm_b='plastic'):
    return [(n, i, x, y) for (n, i, x), (_, _, y) in zip(turns(seed, arm_a, sa), turns(seed, arm_b, sb))]
near = lambda x, B: any(abs(x[k] - b) <= .05 for k, b in B)
act = lambda x: (x['intent'], x['ambient']); tag = lambda x: (x['mood'], x['level']); anyd = lambda x: act(x) + tag(x)

# ---- anchor: frozen S1 vs v1's stored frozen arm (same keys)
try:
    V1 = json.loads((D.parent / 'duckplast' / 'results.json').read_text())['histories']
    anc = {}
    for s in SEEDS:
        v = next(h for h in V1 if h['seed'] == s and h['eta'] == 0)['battery']; mm = 0; mx = 0.0; n = 0
        for nme, i, x in turns(s, 'frozen', 'S1'):
            y = v[nme][i - 1]; n += 1
            mm += any(x[k] != y[k] for k in ('sit', 'event', 'mood', 'level', 'intent'))
            mx = max(mx, abs(x['fear'] - y['fear']), abs(x['hunger'] - y['hunger']), abs(x['sleep'] - y['sleep']),
                     abs(x['trust'] - y['body']), abs(x['cx']['move'] - y['cx']['move']))
        anc[s] = dict(turns=n, label_mismatches=mm, max_abs_diff=mx)
    S['anchor_v1'] = anc; P('ANCHOR frozen S1 vs v1 stored frozen:', anc)
except Exception as e: P('anchor unavailable', repr(e))

# ---- pairing sanity: routing identical across arms
S['routing_mismatch'] = {k: sum((x['sit'], x['event']) != (y['sit'], y['event']) for s in SEEDS for _, _, x, y in pairs(s, k, k)) for k in SESS}
P('routing (sit,event) mismatches plastic vs frozen by session:', S['routing_mismatch'])

# ---- drift census
P('\nDRIFT (plastic arms; relative to |w0|, band 0.20):')
S['drift'] = {}
for s in SEEDS:
    assert all(c['ALL']['changed'] == 0 for c in H[s, 'frozen']['census']), 'frozen arm drifted'
    for c in H[s, 'plastic']['census']:
        row = {p: (c[p]['changed'], c[p]['at_cap'], round(c[p]['mean_signed_rel'], 4), round(c[p]['max_abs_rel'], 4)) for p in ('FEAR', 'JOY_SAL', 'MOTOR')}
        S['drift'][f"{s}:{c['tag']}"] = c
        P(f" seed {s} {c['tag']:>2}: ALL changed {c['ALL']['changed']:>7,}/{c['ALL']['edges']:,} at_cap {c['ALL']['at_cap']:>7,} mean|rel| {c['ALL']['mean_abs_rel']:.4f} | (changed, at_cap, mean signed rel, max) {row}")
P(' frozen drift = 0 in every census: True; band/sign asserts passed inside run.py at every checkpoint')

# ---- Q1 + shift distributions
def shift(seed, sess, key, sel):
    return [(y['cx']['move'] - x['cx']['move']) if key == 'move' else y[key] - x[key] for n, i, x, y in pairs(seed, sess, sess) if sel(n, x)]
kind = lambda n, x: ARC[n] == 'kindness'
P('\nQ1 kindness arcs (plastic - frozen, paired), by session:')
q1 = {}
for key in ('food_joy', 'salience', 'move', 'fear'):
    q1[key] = {k: [mean(shift(s, k, key, kind)) for s in SEEDS] for k in SESS}
    P(f'  mean d {key:9}', {k: [round(v, 5) for v in vs] for k, vs in q1[key].items()})
fj = q1['food_joy'][FINAL]; allfj = [v for s in SEEDS for v in shift(s, FINAL, 'food_joy', kind)]
floor = None
if 'S3' in SESS and 'R' in SESS:
    floor = {key: mean([abs((y['cx']['move'] - x['cx']['move']) if key == 'move' else y[key] - x[key]) for s in SEEDS
                        for n, i, x, y in pairs(s, 'S3', 'R', 'frozen', 'frozen') if kind(n, x)]) for key in ('food_joy', 'salience', 'move')}
q1v = .002 <= mean(fj) <= .08 and all(v > 0 for v in fj)
sal = q1['salience'][FINAL]; mv = q1['move'][FINAL]
S['Q1'] = dict(supported=q1v, mean_d_food_joy=mean(fj), per_seed=fj, band=[.002, .08], share_turns_gt0=mean([v > 0 for v in allfj]),
               median=st.median(allfj), max=max(allfj), secondary_salience=dict(mean=mean(sal), per_seed=sal, band=[.005, .12], in_band=.005 <= mean(sal) <= .12 and all(v > 0 for v in sal)),
               secondary_move=dict(mean=mean(mv), per_seed=mv, positive=all(v > 0 for v in mv)), noise_floor_mean_abs=floor, by_session=q1)
P(f"  Q1 primary {'SUPPORTED' if q1v else 'NOT supported'}: mean d food_joy {mean(fj):+.5f} (band +.002..+.08), per seed {[round(v, 5) for v in fj]}, share of turns >0 {S['Q1']['share_turns_gt0']:.2f}, median {S['Q1']['median']:+.5f}, max {S['Q1']['max']:+.5f}")
P(f"  secondary: d salience {mean(sal):+.5f} (band +.005..+.12: {S['Q1']['secondary_salience']['in_band']}); d cx move {mean(mv):+.5f} (>0: {S['Q1']['secondary_move']['positive']}); frozen noise floor mean|d| {floor}")
P('\nShift by arc class at', FINAL, '(mean over turns and seeds; share>0):')
S['arc_shift'] = {}
for arc in sorted(set(ARC.values())):
    sel = lambda n, x, a=arc: ARC[n] == a; row = {}
    for key in ('food_joy', 'salience', 'fear', 'move', 'sleep'):
        v = [u for s in SEEDS for u in shift(s, FINAL, key, sel)]; row[key] = (round(mean(v), 5), round(mean([u > 0 for u in v]), 2))
    S['arc_shift'][arc] = row; P(f'  {arc:10}', row)
P('Raw peak shifts at', FINAL, '(event turns only, mean):', end=' ')
pk = collections.defaultdict(list)
for s in SEEDS:
    for n, i, x, y in pairs(s, FINAL, FINAL):
        if x['peak'] and y['peak']:
            for k in ('lc', 'oct', 'ser', 'dan', 'dop', 'dn'): pk[k].append(y['peak'][k] - x['peak'][k])
S['peak_shift'] = {k: mean(v) for k, v in pk.items()}; P({k: round(v, 5) for k, v in S['peak_shift'].items()})

# ---- Q2 flips
def flips(seed, sa, sb, arm_a, arm_b, dec, B, ref_sess):
    ref = {(n, i): x for n, i, x in turns(seed, 'frozen', ref_sess)}; out = []
    for n, i, x, y in pairs(seed, sa, sb, arm_a, arm_b):
        if (B is None or near(ref[n, i], B)) and dec(x) != dec(y): out.append((n, i, dec(x), dec(y)))
    return out
P('\nQ2 flips at', FINAL, '(N = plastic vs frozen, paired; C = frozen', FINAL, 'vs frozen S3, noise re-draw):')
S['Q2'] = {}
for name, dec, B in (('action', act, ACT_B), ('tag', tag, TAG_B), ('any', anyd, ACT_B + TAG_B)):
    nn = {s: sum(near(x, B) for _, _, x in turns(s, 'frozen', FINAL)) for s in SEEDS}
    N = {s: flips(s, FINAL, FINAL, 'frozen', 'plastic', dec, B, FINAL) for s in SEEDS}
    C = {s: flips(s, 'S3', FINAL, 'frozen', 'frozen', dec, B, FINAL) for s in SEEDS} if 'S3' in SESS and FINAL == 'R' else {s: [] for s in SEEDS}
    Nall = {s: flips(s, FINAL, FINAL, 'frozen', 'plastic', dec, None, FINAL) for s in SEEDS}
    nN = sum(map(len, N.values())); nC = sum(map(len, C.values()))
    ok = nN > nC and nN >= len(SEEDS) and sum(bool(v) for v in N.values()) >= 2
    S['Q2'][name] = dict(supported=ok, near_turns=nn, N=nN, C=nC, N_by_seed={s: len(v) for s, v in N.items()}, all_turn_flips={s: len(v) for s, v in Nall.items()},
                         N_list={s: v for s, v in N.items()}, C_list={s: v for s, v in C.items()}, all_list={s: v for s, v in Nall.items()})
    P(f"  Q2-{name:6} {'SUPPORTED' if ok else 'NOT supported'}: near-threshold turns/seed {nn}; N {nN} {S['Q2'][name]['N_by_seed']} vs C {nC}; flips over ALL 192 turns/seed {S['Q2'][name]['all_turn_flips']}")
    for s in SEEDS:
        for f in Nall[s]: P(f'      seed {s} {f[0]} t{f[1]}: {f[2]} -> {f[3]}', '' if f in N[s] else '(not near-threshold)')
        for f in C[s]: P(f'      [noise] seed {s} {f[0]} t{f[1]}: {f[2]} -> {f[3]}')
S['flips_by_session'] = {k: {nm: [len(flips(s, k, k, 'frozen', 'plastic', dec, None, k)) for s in SEEDS] for nm, dec in (('reply', lambda x: x['intent']), ('ambient', lambda x: x['ambient']), ('tag', tag))} for k in SESS}
P('  flips over all turns by session [per seed]:', S['flips_by_session'])
reply_total = sum(v for k in SESS for v in S['flips_by_session'][k]['reply'])
loom = [(x['fear'], y['fear'], x['intent'], y['intent']) for s in SEEDS for k in SESS for n, i, x, y in pairs(s, k, k) if x['event'] in ('rake', 'umbrella')]
S['structural'] = dict(reply_intent_flips_all_sessions=reply_total, looming_turns=len(loom), looming_fear_min=[min(a for a, *_ in loom), min(b for _, b, *_ in loom)])
P(f"  structural: reply-intent flips over all sessions {reply_total} (predicted 0); rake/umbrella turns {len(loom)}, min fear frozen/plastic {S['structural']['looming_fear_min']} (predicted 1.0)")
# margins to the action comparators: how far is the nearest cheap flip?
marg = {}
for k, b in (('food_joy', .60), ('fear', .40), ('sleep', .70)):
    xs = [(abs(x[k] - b), n, i, round(x[k], 4), round(y[k], 4)) for s in SEEDS[:1] for n, i, x, y in pairs(s, FINAL, FINAL)]
    marg[f'{k}@{b}'] = sorted(xs)[:4]
S['nearest_action_margins_seed0'] = marg; P('  nearest turns to neural-coupled action boundaries (|margin|, scenario, turn, frozen, plastic), seed 0:', marg)

# ---- Q3
P('\nQ3 picked_up turn 5:')
q3 = {}
for k in SESS:
    q3[k] = [dict(frozen=tag(H[s, 'frozen']['sessions'][k]['picked_up'][4]), plastic=tag(H[s, 'plastic']['sessions'][k]['picked_up'][4]),
                  sal_f=H[s, 'frozen']['sessions'][k]['picked_up'][4]['salience'], sal_p=H[s, 'plastic']['sessions'][k]['picked_up'][4]['salience']) for s in SEEDS]
    P(f'  {k}:', [(r['frozen'], r['plastic'], round(r['sal_f'], 4), round(r['sal_p'], 4), round(r['sal_p'] - r['sal_f'], 4)) for r in q3[k]])
dsal = {k: mean([r['sal_p'] - r['sal_f'] for r in q3[k]]) for k in SESS}
rep = all(r['frozen'] == ('neutral', 'low') and r['plastic'] == ('curious', 'low') for r in q3[FINAL])
stronger = 'S1' in dsal and 'S3' in dsal and 'R' in dsal and dsal['S3'] > dsal['S1'] and dsal['R'] > dsal['S1']
S['Q3'] = dict(supported=rep and stronger, replicates=rep, strengthens=stronger, mean_d_salience=dsal, detail=q3)
P(f"  Q3 {'SUPPORTED' if rep and stronger else 'NOT supported'}: replicates at {FINAL} in every seed {rep}; strengthens (S3>S1 and R>S1) {stronger}; mean d salience {({k: round(v, 5) for k, v in dsal.items()})}")

# ---- Q4
P('\nQ4 no forgetting:')
bed = [(x, y) for s in SEEDS for n, i, x, y in pairs(s, FINAL, FINAL) if n == 'bedtime']
night = [(x, y) for s in SEEDS for n, i, x, y in pairs(s, FINAL, FINAL) if x['sit'] == 'night']
settles = sum('settle' in act(x) for x, y in bed)
i_ok = all(act(x) == act(y) for x, y in bed) and settles > 0 and all(act(x) == act(y) for x, y in night)
bed_sleep = max(abs(x['sleep'] - y['sleep']) for x, y in bed)
if all('quiet' in H[s, a] for s in SEEDS for a in ('frozen', 'plastic')):
    qd = [max(abs(H[s, 'frozen']['quiet'][0][k] - H[s, 'plastic']['quiet'][0][k]) for s in SEEDS) for k in ('hunger', 'sleep')]
else: qd = [float('nan')] * 2
ii_ok = max(qd) <= .01 and bed_sleep <= .02
lm = [(x, y) for s in SEEDS for n, i, x, y in pairs(s, FINAL, FINAL) if x['event'] in ('rake', 'umbrella')]
iii_ok = all(x['intent'] == y['intent'] == 'to_boot' and y['fear'] >= x['fear'] - .02 for x, y in lm)
world = {}; iv_ok = True
for s in SEEDS:
    for dd_f, dd_p in zip(H[s, 'frozen']['days'], H[s, 'plastic']['days']):
        af = [t[0] for t in dd_f['ticks']]; ap = [t[0] for t in dd_p['ticks']]
        nf, npl = af.count('nest'), ap.count('nest'); div = next((i for i, (a, c) in enumerate(zip(af, ap)) if a != c), None)
        amb_div = next((i for i, (a, c) in enumerate(zip(dd_f['ticks'], dd_p['ticks'])) if a[1] != c[1]), None)
        ok = abs(npl - nf) <= .05 * nf and len(dd_f['passes']) >= 1 and len(dd_p['passes']) >= 1; iv_ok &= ok
        world[f"{s}:D{dd_f['day']}"] = dict(nest=[nf, npl], ok=ok, first_act_divergence_tick=div, first_ambient_divergence_tick=amb_div,
                                            act_diff_ticks=sum(a != c for a, c in zip(af, ap)), ambient_diff_ticks=sum(a[1] != c[1] for a, c in zip(dd_f['ticks'], dd_p['ticks'])),
                                            acts_frozen=dict(collections.Counter(af)), acts_plastic=dict(collections.Counter(ap)),
                                            ambient_frozen=dict(collections.Counter(t[1] for t in dd_f['ticks'])), ambient_plastic=dict(collections.Counter(t[1] for t in dd_p['ticks'])),
                                            passes_frozen=[(p['hour'], p['date'], [c[0] for c in p['chosen']], p['written']) for p in dd_f['passes']],
                                            passes_plastic=[(p['hour'], p['date'], [c[0] for c in p['chosen']], p['written']) for p in dd_p['passes']],
                                            hoard=[dd_f['hoard'], dd_p['hoard']])
ndays = min(len(H[k]['days']) for k in H)
q4 = i_ok and ii_ok and iii_ok and iv_ok and ndays == 3
S['Q4'] = dict(supported=q4, i_settle_identical=i_ok, bedtime_settle_positives=settles, night_turns=len(night), ii_baseline=ii_ok, quiet_max_abs=qd, bedtime_max_d_sleep=bed_sleep,
               iii_threat=iii_ok, looming_turns=len(lm), iv_world=iv_ok, days_scored=ndays, world=world)
P(f"  (i) bedtime+night decisions identical {i_ok} ({settles} frozen settle positives over {len(bed)} bedtime turns; {len(night)} night turns)")
P(f"  (ii) quiet probe max |d hunger|, |d sleep| {qd}; bedtime max |d sleep| {bed_sleep:.5f} -> {ii_ok}")
P(f"  (iii) {len(lm)} rake/umbrella turns keep to_boot and fear {iii_ok}")
P(f"  (iv) world sleep phase {iv_ok} (days scored {ndays}):")
for k, w in world.items():
    P(f"     {k}: nest frozen/plastic {w['nest']} ok={w['ok']}; first act divergence tick {w['first_act_divergence_tick']} ({w['act_diff_ticks']} differing ticks); ambient first {w['first_ambient_divergence_tick']} ({w['ambient_diff_ticks']} differing)")
    P(f"        acts F {w['acts_frozen']}"); P(f"        acts P {w['acts_plastic']}")
    P(f"        ambient F {w['ambient_frozen']} | P {w['ambient_plastic']}")
    P(f"        passes F {w['passes_frozen']}"); P(f"        passes P {w['passes_plastic']}")
P(f"  Q4 {'SUPPORTED' if q4 else 'NOT supported'}")
P('\nVERDICTS:', {q: (S[q]['supported'] if q != 'Q2' else {k: v['supported'] for k, v in S['Q2'].items()}) for q in ('Q1', 'Q2', 'Q3', 'Q4')})
(D / 'scores.json').write_text(json.dumps(S, indent=1, default=str))
