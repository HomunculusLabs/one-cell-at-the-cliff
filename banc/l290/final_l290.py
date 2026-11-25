# Run from banc/ after the L290 workers (tick 277). Stage B under l290/PREREG.md
# (27b6a473...) + sets.json (0a48800b...). Re-reads persisted raw arrays only.
# MODE is derived from the artefacts: all three exit files present and 0 -> FINAL; fewer ->
# PARTIAL (verification ONLY, no effect computed: the branches are registered on 25 arms).
from pathlib import Path
import json, os, hashlib, numpy as np
out, l240 = Path('l290'), Path('l240')
read = lambda d, n: json.loads((d / n).read_text())
sha = lambda d, n: hashlib.sha256((d / n).read_bytes()).hexdigest()
psha, ssha = sha(out, 'PREREG.md'), sha(out, 'sets.json')
assert psha == (out / 'PREREG.sha256').read_text().split()[0], 'PREREG sha mismatch'
assert ssha == (out / 'sets.sha256').read_text().split()[0], 'sets sha mismatch'
assert sha(out, 'edge_run_l290.py') == '4c60ce6e8e81029b66d4e187d9c80bf872cee63a927daa3ad937eaeba1724c89', 'harness drift'
SETS = read(out, 'sets.json')
assert SETS['prereg_sha256'] == psha and SETS['noop'] == [1, 2, 8, 9, 16, 21, 47, 55]
N0 = set(SETS['noop'])
USED = {m: [int(j) for j in SETS['used'][m]] for m in ('abs', 'crofts', 'hop')}
GROUPS = {a: [int(j) for j in v] for a, v in SETS['random'].items()}
GROUPS.update({'gc30': USED['crofts'], 'gh46': USED['hop']})
GROUPS.update({f'rw{n}': [int(j) for j in SETS['raw'][str(n)]] for n in (11, 30, 46)})
RAND = sorted(SETS['random'])
FIXT = {'e14f': 'e14', 'e25f': 'e25', 'e67f': 'e67', 'e12f': 'e12', 'e27f': 'e27'}
PLAN = sorted(list(GROUPS) + list(FIXT))
assert len(GROUPS) == 20 and len(RAND) == 15 and len(PLAN) == 25
SAME = {tuple(x) for x in SETS['same_set_pairs']}
SIZEU = {11: 'abs', 30: 'crofts', 46: 'hop'}
UARM = {'abs': 'g11', 'crofts': 'gc30', 'hop': 'gh46'}
W = (0, 1, 2)
A1W, A2W_ALL = (0, 1, 2), (3, 4, 5, 6, 7, 8, 9)


def _exit(w):
    p = out / f'exit_w{w}'
    return p.read_text().strip() if p.exists() else None


EXIT = {w: _exit(w) for w in W}
FIN0 = tuple(w for w in W if EXIT[w] is not None)
assert all(EXIT[w] == '0' for w in FIN0), ('a finished L290 worker exited non-zero', EXIT)
FINAL = len(FIN0) == 3
# tick 278 FIX (bookkeeping only, no statistic touched): L290 workers are stored under key w + 10.
# The pre-fix script keyed them 0-2 -- the SAME keys as A1's l240 workers -- so the L290 load
# OVERWROTE A1's done/Z/X/anch, the "cutwA == A1 stored" gate could only ever compare L290
# w1/w2 with L290 w0, and A1's arms fell out of W_OF (halt 2: "an arm name is owned by two
# workers: gc30"). File names keep the true worker id (k - 10); statistics read by key only.
FIN = tuple(w + 10 for w in FIN0)
seeds = list(range(3769, 3785))
ANCH = [801, 901, 3545]
CTR = [1110, 75494, 559, 74914]
STORED_G = 0.14365819573402408
armsj, done, anch, Z, X = {}, {}, {}, {}, {}
trace_count = pool_count = 0
for w in A1W + A2W_ALL:
    done[w] = read(l240, f'done_w{w}.json')
for w in A1W:
    anch[w] = read(l240, f'anchors_w{w}.json')
for w in A1W + A2W_ALL:      # tick 278 FIX: A2 workers' arrays are READ below (`single`, all 69 edges)
    Z[w], X[w] = np.load(l240 / f'raw_w{w}.npz'), np.load(l240 / f'xm_w{w}.npz')
for w in FIN:
    armsj[w], done[w], anch[w] = read(out, f'arms_w{w - 10}.json'), read(out, f'done_w{w - 10}.json'), read(out, f'anchors_w{w - 10}.json')
    assert armsj[w]['stage'] == 'L290-B' and armsj[w]['prereg'] == psha and armsj[w]['sets_sha'] == ssha, (w, 'stage / shas')
    assert armsj[w]['menu_n'] == 80 and armsj[w]['menu69_n'] == 69 and armsj[w]['cert_menu_11'] == 11, (w, 'CERT-MENU')
    assert armsj[w]['base_edges'] == 644177, (w, 'base edges')
    for a, e in armsj[w]['edges'].items():
        n_rm = len(GROUPS[a]) if a in GROUPS else 1
        assert len(e['removed']) == n_rm and (a not in GROUPS or e['set'] == GROUPS[a]), (w, a, 'deleted entries')
        assert all(r['csr_index'] >= 0 and r['effective_weight'] != 0 for r in e['removed']), (w, a, 'removed entry')
    Z[w], X[w] = np.load(out / f'raw_w{w - 10}.npz'), np.load(out / f'xm_w{w - 10}.npz')
for w in A1W + FIN:
    d = done[w]
    assert d['seeds'] == ANCH + seeds and d['ctr_cells'] == CTR, (w, 'seeds / ctr cells')
    assert anch[w]['c0a135_pass'] and anch[w]['c0a175_pass'], (w, 'anchors')
    assert anch[w]['c0a135_max'] == 0.0 and anch[w]['c0a175_max'] == 0.0, (w, 'anchors max')
    assert anch[w]['c0a135_checks'] == 46 and anch[w]['c0a175_checks'] == 25, (w, 'anchor coverage')
    assert anch[w]['g_cutwA_stored_exact'] and anch[w]['g_cutwA'] == STORED_G == d['gain']['cutwA'], (w, 'stored base gain')
    for k in Z[w].files:
        pp = k.split('_')
        if len(pp) == 3 and pp[0][1:].isdigit() and pp[2].isdigit():
            x = Z[w][k]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k); trace_count += 1
        elif len(pp) == 4 and pp[0] in ('Ti', 'Tr', 'Ta', 'Sr', 'Pr'):
            x = Z[w][k]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k); pool_count += 1
    for a in d['arms']:
        # tick 278 FIX (coverage check only, no statistic touched): the harness runs cutwA on
        # anchors + seeds (arms_for, edge_run_l290.py L1334) and every other arm on the 16
        # seeds only -- the same npz structure as A1 (l240) and final_a2.py's own form.
        for s in (ANCH + seeds if a == 'cutwA' else seeds):
            assert f'xmean_{a}_{s}' in X[w].files and f'af_{a}_{s}' in Z[w].files, (w, a, s)
            assert bool(np.isfinite(X[w][f'xmean_{a}_{s}']).all()), (w, a, s, 'xmean finite')   # tick 278 FIX
        if a != 'cutwA':   # exact coverage: no stray anchor-seed trace on a non-control arm
            assert not any(f'xmean_{a}_{s}' in X[w].files or f'af_{a}_{s}' in Z[w].files for s in ANCH), (w, a, 'stray anchor key')
    if w in FIN:
        assert d['prereg_sha256'] == psha, (w, 'PREREG sha')
        assert d['secs'] < 1700, (w, 'hard stop', d['secs'])
        assert d['arms'] == ['cutwA'] + armsj[w]['arms_built'], (w, 'done arms')
        for a in d['arms']:
            assert .12 <= d['gain'][a] <= .18, (w, a, 'gain window')
            if a in FIXT:
                assert d['gain'][a] == STORED_G, (w, a, 'fixed twin gain')
for w in A2W_ALL:             # tick 278 FIX: A2 arrays are read by `single` -> the same finite gates on what is read
    d = done[w]
    assert d['seeds'] == ANCH + seeds and d['ctr_cells'] == CTR, (w, 'A2 seeds / ctr cells')
    assert d['secs'] < 1700, (w, 'A2 hard stop', d['secs'])
    _an2 = read(l240, f'anchors_w{w}.json')
    assert _an2['c0a135_pass'] and _an2['c0a175_pass'], (w, 'A2 anchors')
    for k in Z[w].files:
        pp = k.split('_')
        if len(pp) == 3 and pp[0][1:].isdigit() and pp[2].isdigit():
            x = Z[w][k]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k); trace_count += 1
        elif len(pp) == 4 and pp[0] in ('Ti', 'Tr', 'Ta', 'Sr', 'Pr'):
            x = Z[w][k]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k); pool_count += 1
    for a in d['arms']:
        for s in (ANCH + seeds if a == 'cutwA' else seeds):
            assert bool(np.isfinite(X[w][f'xmean_{a}_{s}']).all()), (w, a, s, 'A2 xmean finite')
W_OF = {}
for w in A1W + A2W_ALL + FIN:
    for a in done[w]['arms']:
        if a != 'cutwA':
            assert a not in W_OF, ('an arm name is owned by two workers', a)
            W_OF[a] = w
assert all(a in W_OF for a in PLAN), ('missing arms', [a for a in PLAN if a not in W_OF])
pools = read(l240, 'pools_w0.json')
assert all(pools['pools'] == read(out, f'pools_w{w}.json')['pools'] for w in FIN0), 'pool index sets differ'
ALLSEEDS = ANCH + seeds
xm = lambda w, a, s: X[w][f'xmean_{a}_{s}'].astype(np.float64)
raw_cut = [k for k in Z[0].files if k.startswith(tuple(f'c{g}_' for g in CTR)) and '_cutwA_' in k and int(k.rsplit('_', 1)[1]) in ALLSEEDS]
assert len(raw_cut) == 4 * 19

# ---------------- gate: every L290 worker's cutwA == A1's stored cutwA, exactly ----------------
raw_all = [k for k in Z[0].files if '_cutwA_' in k]       # tick 278 FIX: PREREG s2 = xmean + raw POOL traces + af
gate = {w: dict(
    xmean=bool(all(np.array_equal(xm(w + 10, 'cutwA', s), xm(0, 'cutwA', s)) for s in ALLSEEDS)),
    raw=bool(all(np.array_equal(Z[w + 10][k], Z[0][k]) for k in raw_cut)),
    raw_all=bool(set(k for k in Z[w + 10].files if '_cutwA_' in k) == set(raw_all)
                 and all(np.array_equal(np.atleast_1d(Z[w + 10][k]), np.atleast_1d(Z[0][k])) for k in raw_all)),
    af=bool(all(np.array_equal(np.atleast_1d(Z[w + 10][f'af_cutwA_{s}']), np.atleast_1d(Z[0][f'af_cutwA_{s}'])) for s in ALLSEEDS))) for w in FIN0}
assert all(all(g.values()) for g in gate.values()), ('VOID: an L290 cutwA trace != A1 stored', gate)
enc = lambda o: o.item() if hasattr(o, 'item') else str(o)


def atomic(name, obj):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=1, default=enc))
    os.replace(tmp, out / name)


base = dict(card='L290 stage B', prereg_sha256=psha, sets_sha256=ssha, harness_sha256=sha(out, 'edge_run_l290.py'), seeds=seeds,
            workers={w: dict(arms=done[w + 10]['arms'], secs=done[w + 10]['secs']) for w in FIN0}, exit_codes={w: EXIT[w] for w in W},
            anchors={w: dict(c0a135_max=anch[w + 10]['c0a135_max'], c0a175_max=anch[w + 10]['c0a175_max']) for w in FIN0},
            cutwA_gate={w: gate[w] for w in FIN0}, cutwA_arrays_compared=len(raw_all), trace_arrays_verified=trace_count, pool_traces_verified=pool_count,
            gains={a: done[W_OF[a]]['gain'][a] for a in W_OF}, sets={a: GROUPS[a] for a in GROUPS})
if not FINAL:
    base.update(status='PARTIAL', effects_read=False, missing_arms=[a for a in PLAN if a not in W_OF],
                note='fewer than 3 L290 workers finished: verification only, no effect computed, branches NOT read')
    atomic('results_l290_partial.json', base)
    print('PARTIAL: workers', FIN0, 'of 3 | exit', EXIT, '| cutwA gate', gate)
    print('no effect read; branches NOT read; missing arms', base['missing_arms'])
    raise SystemExit(0)

# ================= FINAL: all 25 arms present =================
R1 = read(l240, 'results_l240.json')
PK = sorted(pools['pools'])
U = sorted(set(sum(pools['pools'].values(), [])))
BASE = np.array([xm(0, 'cutwA', s)[U].mean() for s in seeds])
PPBASE = np.array([[xm(0, 'cutwA', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds])
ARMS = PLAN + ['g11', 'e14', 'e25', 'e67', 'e12', 'e27']
assert all(a in W_OF for a in ARMS)
P = {a: np.array([xm(W_OF[a], a, s)[U].mean() for s in seeds]) for a in ARMS}
PP = {a: np.array([[xm(W_OF[a], a, s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) for a in ARMS}
n = np.array([xm(2, 'nf', s)[U].mean() for s in seeds]) - BASE
Vn = np.array([[xm(2, 'nf', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) - PPBASE
F = float(n.std(ddof=1) / 4)
assert abs(F - R1['noise_twin']['F']) <= 1e-18, ('F drift vs A1', F, R1['noise_twin']['F'])
eps = 2 * F
t15 = 2.131449546
# sign matrix (tick 276 corrected form, final_a2.py VERBATIM)
SGN = (1 - 2 * ((np.arange(65536, dtype=np.int64)[:, None] >> np.arange(16)[None, :]) & 1)).astype(np.float64)
assert SGN.shape == (65536, 16) and bool((SGN[0] > 0).all()) and bool(SGN[1, 0] < 0)


def flip(d):
    d = np.asarray(d, float); obs = float(d.mean()); nul = SGN @ d / 16.0
    tol = 1e-12 * max(1.0, abs(obs))
    return dict(D=obs, SE=float(d.std(ddof=1) / 4), p_two=float((np.abs(nul) >= abs(obs) - tol).mean()),
                p_up=float((nul >= obs - tol).mean()), p_down=float((nul <= obs + tol).mean()))


def midrank(x):
    x = np.asarray(x, float); o = np.argsort(x, kind='mergesort'); r = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = midrank(a) - midrank(a).mean(), midrank(b) - midrank(b).mean()
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / den) if den > 0 else float('nan')


# ---------------- self-checks BEFORE any effect is read ----------------
_a0 = P['gc30'] - BASE
assert abs(float(SGN[0] @ _a0) / 16.0 - float(_a0.mean())) < 1e-15, 'sign matrix self-check'
_z, _p, _m = np.zeros(16), np.ones(16), np.r_[np.ones(15), -1.0]
assert flip(_z)['p_two'] == 1.0 and flip(_z)['p_up'] == 1.0 and flip(_z)['p_down'] == 1.0, 'flip self-check (all-zero arm reads p 1, never a count)'
assert abs(flip(_p)['p_up'] - 1 / 65536) < 1e-12 and abs(flip(_p)['p_two'] - 2 / 65536) < 1e-12, 'flip self-check (resolution floor)'
assert abs(flip(-_p)['p_two'] - 2 / 65536) < 1e-12 and abs(flip(-_p)['p_up'] - 1.0) < 1e-12, 'flip self-check (sign reversal)'   # tick 278 FIX: input was _m, a 15/16 vector
assert abs(flip(_m)['p_two'] - 34 / 65536) < 1e-12 and abs(flip(_m)['p_up'] - 17 / 65536) < 1e-12, 'flip self-check (15 of 16: C(16,0)+C(16,1) = 17 a side)'   # tick 278 FIX: derived, not typed from a run
PB = {w: np.array([xm(w, 'cutwA', s)[U].mean() for s in seeds]) for w in FIN}
assert all(np.array_equal(PB[w], BASE) for w in FIN), 'worker bases != A1 base'
for w in FIN:
    for a in armsj[w]['edges']:
        if a in GROUPS:
            assert [r['target'] for r in sorted(armsj[w]['edges'][a]['removed'], key=lambda r: r['target'])] == \
                   sorted(SETS['menu'][j]['target'] for j in GROUPS[a]), (w, a, 'deleted targets != set')

D = {a: P[a] - BASE for a in ARMS}
E = {a: float(D[a].mean()) for a in ARMS}
Nn = {a: float(np.linalg.norm((PP[a] - PPBASE).mean(0))) for a in ARMS}
floorN = float(np.sqrt(((Vn.std(0, ddof=1) / 4) ** 2).sum()))
E14 = E['e14']


def contrast(u, x):
    """PREREG s5: advantage of used-set arm u over comparator x, both arm-vs-arm."""
    assert u != x and GROUPS.get(u, USED['abs']) != GROUPS[x], (u, x)
    sg = float(np.sign(E[u]))
    f = flip(P[u] - P[x]); adv = sg * f['D']
    # tick 278 FIX (PREREG s4/s5 verbatim): the tested statistic is the ADVANTAGE A = sign(E_u) * D and
    # "the one-sided tail p_up" is P(null >= A). The tick-277 lines chose the tail by the sign of A, so
    # for a used-set with E > 0 a comparator that significantly EXCEEDED it read WITHIN (IS EXCEEDED BY
    # = A <= -eps and 1 - p_up <= 0.01 could not fire) and such a metric still counted as ESCAPES.
    g = flip(sg * (P[u] - P[x]))
    assert abs(g['D'] - adv) < 1e-15 and abs(g['p_two'] - f['p_two']) < 1e-12 and abs(g['SE'] - f['SE']) < 1e-15, (u, x, 'symmetry')
    p_adv, p_opp = g['p_up'], g['p_down']
    st = 'EXCEEDS' if (adv >= eps and p_adv <= 0.01) else ('EXCEEDED_BY' if (adv <= -eps and (1 - p_adv) <= 0.01) else 'WITHIN')
    _pa, _po = (f['p_up'], f['p_down']) if adv > 0 else (f['p_down'], f['p_up'])       # the tick-277 rule, RECORDED, never read
    st277 = 'EXCEEDS' if (adv >= eps and _pa <= 0.01) else ('EXCEEDED_BY' if (adv <= -eps and _po <= 0.01) else 'WITHIN')
    return dict(advantage=adv, in_F=adv / F, D=f['D'], SE=f['SE'], p_two=f['p_two'], p_adv=p_adv, p_opp=p_opp, status=st,
                tick277_status=st277, tie_mass=p_adv + p_opp - 1)


MET, win, conf, escape_all = {}, [], [], True
for m in ('abs', 'crofts', 'hop'):
    u = UARM[m]; nm = len(USED[m])
    cmp_ = [f'rw{nm}'] + [f'r{nm}k{k}' for k in range(1, 6)]
    assert all(len(GROUPS[c]) == nm for c in cmp_)
    rows = {c: contrast(u, c) for c in cmp_ if (m, c) not in SAME}
    raw_c = f'rw{nm}'
    raw_ok = raw_c in rows and rows[raw_c]['status'] == 'EXCEEDS' and rows[raw_c]['advantage'] >= eps and rows[raw_c]['p_adv'] <= 0.001
    rnd = [c for c in rows if c != raw_c]
    n_exc = sum(1 for c in rnd if rows[c]['status'] == 'EXCEEDS')
    all_pos = all(rows[c]['advantage'] > 0 for c in rnd)
    e14c = [c for c in rows if 14 in GROUPS[c]]
    support = bool(e14c) and all(rows[c]['status'] == 'EXCEEDS' for c in e14c)
    esc = all(r['status'] == 'WITHIN' for r in rows.values())
    if raw_ok and all_pos and n_exc >= 4 and support:
        label = 'WINS'
    elif raw_ok and all_pos and n_exc >= 4 and not e14c:       # tick 278 FIX: PREREG s5 (b) "has NO e14-containing comparator"
        label = 'CONFOUNDED_BY_E14'
    elif esc:
        label = 'ESCAPES'
    else:
        label = 'NO_CLEAN_RESULT'
    MET[m] = dict(arm=u, n=nm, eff=len([j for j in USED[m] if j not in N0]), E=E[u],
                  comparators={c: {k: v for k, v in r.items() if k != 'SE'} for c, r in rows.items()},
                  raw_leg=raw_ok, random_exceeded=f'{n_exc} of {len(rnd)}', random_all_positive=all_pos,
                  e14_comparators=e14c, support=support, escapes=esc, label=label)
    if label == 'WINS':
        win.append(m)
    if label == 'CONFOUNDED_BY_E14':
        conf.append(m)
    escape_all &= esc

clear = {a: bool(abs(E[a]) > eps) for a in RAND}
K = 8
n_clear = int(sum(clear.values()))
UA = {a: UARM[SIZEU[len(GROUPS[a])]] for a in RAND}          # each random subset's own-size used-set
with14 = [a for a in RAND if 14 in GROUPS[a]]
free14 = [a for a in RAND if 14 not in GROUPS[a]]
d_same = {a: bool(abs(E[UA[a]] - E[a]) <= eps) for a in with14}
d_below = {a: bool(E[UA[a]] - E[a] >= eps) for a in free14}
d_ok = bool(with14) and all(d_same.values()) and all(d_below.values())
n_free_clear = int(sum(clear[a] for a in free14))
e_ok = (n_free_clear >= 4) if len(free14) >= 8 else None
if escape_all:
    VERDICT = 'ESCAPE'
elif win:
    VERDICT = 'WINS:' + max(win, key=lambda m: MET[m]['comparators'][f'rw{len(USED[m])}']['advantage'])
elif n_clear < K:
    VERDICT = 'I_INSTRUMENT_AT_GROUP'
else:
    VERDICT = 'NO_DECISION'
tw = {f: dict(E_fixed=E[f], E_bisected=E[b], sign_agree=bool(np.sign(E[f]) == np.sign(E[b])), diff=abs(E[f] - E[b]), diff_in_F=abs(E[f] - E[b]) / F,
              within=bool(abs(E[f] - E[b]) <= eps), dgain=done[W_OF[b]]['gain'][b] - STORED_G) for f, b in FIXT.items()}
f_ok = all(t['sign_agree'] and t['within'] for t in tw.values())
r1_ok = all(clear[a] for a in with14) and n_free_clear <= 1
r2_ok = all(E[UARM[m]] > 0 for m in UARM) and all(abs(E[UARM[m]] - E14) <= eps for m in UARM)
S1n = len(set(SETS['raw']['11']) & set(USED['abs']))
pred = dict(S1=bool(7 <= S1n <= 10), S2=bool(14 in SETS['raw']['11']),
            N1=bool(2 <= len(set(USED['crofts']) & N0) <= 4 and 4 <= len(set(USED['hop']) & N0) <= 6),
            R1=bool(r1_ok), R2=bool(r2_ok), R3=bool(VERDICT == 'I_INSTRUMENT_AT_GROUP' and d_ok), R4=bool(n_clear < K), R5=bool(f_ok))
single = {j: float(np.array([xm(W_OF[f'e{j}'], f'e{j}', s)[U].mean() for s in seeds]).mean() - BASE.mean()) for j in range(69)}
sumU = {m: float(sum(single[j] for j in USED[m])) for m in USED}
effr = [len([j for j in GROUPS[a] if j not in N0]) for a in RAND]
_sts277 = [r['tick277_status'] for M in MET.values() for r in M['comparators'].values()]
VERDICT277 = 'ESCAPE' if all(s == 'WITHIN' for s in _sts277) else VERDICT        # EXCEEDS is identical under both rules
res = dict(base, status='FINAL', verdict=VERDICT,
           amendment_tick278=dict(contrasts_status_changed=[f'{m}:{c}' for m in MET for c, r in MET[m]['comparators'].items()
                                                     if r['status'] != r['tick277_status']], verdict_under_tick277_rule=VERDICT277), K=K, eps=eps, F=F, floorN=floorN, per_metric=MET,
           instrument=dict(random_clears=clear, n_clear=n_clear, bar=K, with_e14=with14, without_e14=free14,
                           without_e14_clear=n_free_clear, companion_e=e_ok),
           single_edge_carrier=dict(fires=d_ok, same_effect_as_used_set=d_same, used_set_exceeds=d_below),
           twins=dict(rows=tw, EDGE_NOT_GAIN=f_ok), predictions=pred, score=int(sum(pred.values())),
           set_predictions=dict(S1_overlap=S1n, S2_raw11_has14=bool(14 in SETS['raw']['11']), noop_crofts=sorted(set(USED['crofts']) & N0),
                                noop_hop=sorted(set(USED['hop']) & N0)),
           arms={a: dict(E=E[a], CI=[E[a] - t15 * float(D[a].std(ddof=1)) / 4, E[a] + t15 * float(D[a].std(ddof=1)) / 4], in_F=E[a] / F,
                         k_neg=int((D[a] < 0).sum()), N=Nn[a], N_clear=bool(Nn[a] > 2 * floorN),
                         n=len(GROUPS[a]) if a in GROUPS else 1, eff=len([j for j in GROUPS[a] if j not in N0]) if a in GROUPS else None,
                         has14=bool(a in GROUPS and 14 in GROUPS[a]),
                         syn_sum=int(sum(SETS['menu'][j]['syn'] for j in GROUPS[a])) if a in GROUPS else None,
                         gain=done[W_OF[a]]['gain'][a], per_seed=D[a].tolist()) for a in ARMS},
           descriptive=dict(
               note="DESCRIPTIVE, no branch: a sum of members' SINGLE effects shares one control, so its sign is not a group claim (L240)",
               used={m: dict(R=E[UARM[m]] / sumU[m] if sumU[m] else None, S=sumU[m], G=E[UARM[m]],
                             e14_share_of_S=abs(single[14] / sumU[m]) if sumU[m] else None, e14_minus_G=abs(E14 - E[UARM[m]]),
                             members_clearing=int(sum(1 for j in USED[m] if abs(single[j]) > eps))) for m in USED},
               rho_E_eff_random=spearman([E[a] for a in RAND], effr), rho_E_synsum_random=spearman([E[a] for a in RAND], [sum(SETS['menu'][j]['syn'] for j in GROUPS[a]) for a in RAND]),
               mean_E_random_with_e14=float(np.mean([E[a] for a in with14])) if with14 else None,
               mean_E_random_without_e14=float(np.mean([E[a] for a in free14])) if free14 else None,
               single_effects={f'e{j}': single[j] for j in range(69)}))
assert set(res['arms']) == set(ARMS) and len(res['per_metric']) == 3 and res['score'] == sum(bool(v) for v in pred.values())
atomic('results_l290.json', res)
print('FINAL: cutwA gate', all(all(g.values()) for g in gate.values()), '| traces', trace_count, 'pools', pool_count, '| F', F, 'eps', eps)
print('AMEND tick278: contrasts whose status the PREREG-exact tail rule changed', len(res['amendment_tick278']['contrasts_status_changed']),
      res['amendment_tick278']['contrasts_status_changed'], '| verdict under the tick-277 rule', VERDICT277)
print('VERDICT', VERDICT, '| WINS', win, '| CONFOUNDED_BY_E14', conf, '| escapes all', escape_all)
for m in MET:
    M = MET[m]
    print(f"  {m:6s} {M['arm']} n {M['n']} eff {M['eff']} E {M['E']:+.3e} ({M['E'] / F:+.2f} F) raw_leg {M['raw_leg']} random {M['random_exceeded']} "
          f"all+ {M['random_all_positive']} e14cmp {M['e14_comparators']} support {M['support']} -> {M['label']}")
    for c, r in M['comparators'].items():
        print(f"      vs {c:6s} adv {r['advantage']:+.3e} ({r['in_F']:+.2f} F) p_adv {r['p_adv']:.5f} p_opp {r['p_opp']:.5f} {r['status']}"
              + (f"  [tick277 rule read {r['tick277_status']}]" if r['status'] != r['tick277_status'] else ''))
print('random clears', n_clear, 'of 15 (bar', K, ') | with e14', [int(clear[a]) for a in with14], '| without', n_free_clear, 'of', len(free14))
print('SINGLE-EDGE CARRIER', d_ok, '| EDGE NOT GAIN', f_ok, {f: (round(t['diff_in_F'], 2), t['sign_agree']) for f, t in tw.items()})
print('pred', pred, 'score', res['score'], '| rho(E,eff)', round(res['descriptive']['rho_E_eff_random'], 4),
      '| R used', {m: round(v['R'], 3) for m, v in res['descriptive']['used'].items()})
for a in ARMS:
    r = res['arms'][a]
    print(f"  {a:6s} E {r['E']:+.3e} ({r['in_F']:+6.2f} F) k_neg {r['k_neg']:2d} N {r['N']:.3e} {'clr' if r['N_clear'] else '   '} n {r['n']:2d} eff {r['eff']} e14 {int(r['has14'])} dg {r['gain'] - STORED_G:+.2e}")
