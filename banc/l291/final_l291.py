# Run from banc/ after the L291 workers (tick 281):  python l291/final_l291.py
# Under l291/PREREG.md + sets.json + harness, each sha-pinned below. Re-reads persisted raw arrays only;
# l240/ and l290/ are read-only. MODE is derived from the artefacts: both exit files present and 0 -> FINAL;
# fewer -> PARTIAL (verification ONLY, no effect computed: the verdict needs all three metrics).
# `python l291/final_l291.py selftest` runs the WHOLE pipeline on SYNTHETIC arrays aliased to L290's stored
# arms and halts unless every registered verdict, per-metric label, contrast status and BOTH values of every
# prediction were produced (the L290 lesson: an analysis script that had never been executed halted 4 times
# at 0 bytes of output, and one registered label was unreachable).
from pathlib import Path
import json, os, hashlib, sys, numpy as np
SELFTEST = len(sys.argv) > 1 and sys.argv[1] == 'selftest'
out, l240, l290 = Path('l291'), Path('l240'), Path('l290')
read = lambda d, n: json.loads((d / n).read_text())
sha = lambda d, n: hashlib.sha256((d / n).read_bytes()).hexdigest()
psha, ssha = sha(out, 'PREREG.md'), sha(out, 'sets.json')
assert psha == (out / 'PREREG.sha256').read_text().split()[0], 'PREREG sha mismatch'
assert ssha == (out / 'sets.sha256').read_text().split()[0], 'sets sha mismatch'
assert sha(out, 'edge_run_l291.py') == (out / 'harness.sha256').read_text().split()[0], 'harness drift'
assert sha(l240, 'edge_run_a2.py') == '2c71eded96e90af03aeb2fc4ca270627667f8879ffac7c7244e81b5b1dcf0496', 'A2 harness drift'
R290SHA = sha(l290, 'results_l290.json')
assert R290SHA == '83498d7c933414c7ee02f8ff088bcf62d59ec1bac16bc5ff5d274ff3a0628f5f', 'L290 results drift'
PREREG = (out / 'PREREG.md').read_text()
SETS = read(out, 'sets.json')
assert SETS['prereg_sha256'] == psha and SETS['noop'] == [1, 2, 8, 9, 16, 21, 47, 55]
N0 = set(SETS['noop'])
USED = {m: [int(j) for j in SETS['used'][m]] for m in ('abs', 'crofts', 'hop')}
STRAT = {a: [int(j) for j in v] for a, v in SETS['strat'].items()}
SMETA = SETS['strat_meta']
TWINS = SETS['twins']                      # {'gc30f': 'gc30', 'gh46f': 'gh46'}
RAND = {a: [int(j) for j in v] for a, v in SETS['random'].items()}       # L290 uniform arms: REPORTED beside, never scored
SYN = {int(m['j']): int(m['syn']) for m in SETS['menu']}
TGT = {int(m['j']): int(m['target']) for m in SETS['menu']}
SIZEU = {11: 'abs', 30: 'crofts', 46: 'hop'}
UARM = {'abs': 'g11', 'crofts': 'gc30', 'hop': 'gh46'}
UARM_INV = {v: k for k, v in UARM.items()}
SARMS = sorted(STRAT)
assert len(SARMS) == len(SETS['strat']) == 15 and sorted(TWINS) == ['gc30f', 'gh46f'] and len(RAND) == 15
CMP = {m: [a for a in SARMS if len(STRAT[a]) == len(USED[m])] for m in SIZEU.values()}
assert all(len(CMP[m]) == 5 for m in CMP) and sum(len(v) for v in CMP.values()) == 15
WITH14 = {m: [a for a in CMP[m] if 14 in STRAT[a]] for m in CMP}
FREE14 = {m: [a for a in CMP[m] if 14 not in STRAT[a]] for m in CMP}
assert all(len(WITH14[m]) == 3 and len(FREE14[m]) == 2 for m in CMP)
for m in CMP:
    for c in CMP[m]:
        assert SMETA[c]['cell'] == c[-2] and c[-2] == ('w' if c in WITH14[m] else 'f') and SMETA[c]['n'] == len(STRAT[c]) \
            and SMETA[c]['syn_sum'] == sum(SYN[j] for j in STRAT[c]) and SMETA[c]['contains14'] == (14 in STRAT[c]), (c, 'cell / band bookkeeping')
        assert SETS['bands'][str(len(STRAT[c]))][0] <= SMETA[c]['syn_sum'] <= SETS['bands'][str(len(STRAT[c]))][1], (c, 'outside its band')
VAC = {m: [a for a in CMP[m] if STRAT[a] == USED[m]] for m in CMP}       # VACUOUS BY IDENTITY (PREREG s2): kept, never re-rolled
# registered labels are read from the frozen PREREG text, never from memory
for tok in ('(c) I_INSTRUMENT_AT_GROUP', '(a) SET_BEYOND_WEIGHT', '(b) E14_MEMBERSHIP_NOT_WEIGHT', '(w) WEIGHT_CARRIES',
            '(n) NOT_SPECIAL_AT_WEIGHT', 'else NO_DECISION', 'fewer than 8 of the 15 stratified arms clear the floor',
            'at least 2 metrics', 'p_adv_down <= 0.01', 'VACUOUS BY IDENTITY', 'EDGE_NOT_GAIN_GROUP'):
    assert tok in PREREG, ('a registered label is missing from the PREREG text', tok)
for k in range(1, 8):
    assert f'\n P{k}  ' in PREREG, ('prediction not registered', k)
K_BAR, PMIN, NMET = 8, 0.01, 2

W = (0, 1)                                   # L291 worker file ids
_exit = lambda w: (out / f'exit_w{w}').read_text().strip() if (out / f'exit_w{w}').exists() else None
EXIT = {w: _exit(w) for w in W}
FIN0 = tuple(w for w in W if EXIT[w] is not None)
FINAL = (not SELFTEST) and len(FIN0) == 2 and all(EXIT[w] == '0' for w in FIN0)
if not SELFTEST:
    assert all(EXIT[w] == '0' for w in FIN0), ('a finished L291 worker exited non-zero', EXIT)
seeds = list(range(3769, 3785))
ANCH = [801, 901, 3545]
CTR = [1110, 75494, 559, 74914]
ALLSEEDS = ANCH + seeds
STORED_G = 0.14365819573402408
SRC = {20: (l290, 0), 21: (l290, 1)} if SELFTEST else {20: (out, 0), 21: (out, 1)}     # L291 worker keys 20-21
K290 = {10: 0, 11: 1, 12: 2}                  # L290 workers under keys 10-12 (as final_l290.py)
done, anch, armsj, Z, X = {}, {}, {}, {}, {}
for w in (0, 1, 2):
    done[w] = read(l240, f'done_w{w}.json')
    anch[w] = read(l240, f'anchors_w{w}.json')
    Z[w], X[w] = np.load(l240 / f'raw_w{w}.npz'), np.load(l240 / f'xm_w{w}.npz')
for k, w in K290.items():
    done[k] = read(l290, f'done_w{w}.json')
    anch[k] = read(l290, f'anchors_w{w}.json')
    armsj[k] = read(l290, f'arms_w{w}.json')
    Z[k], X[k] = np.load(l290 / f'raw_w{w}.npz'), np.load(l290 / f'xm_w{w}.npz')


def check_arrays(k, d):
    """shape / finiteness / exact key coverage, on any worker's arrays that are READ (final_l290.py form)."""
    tc = pc = 0
    for kk in Z[k].files:
        pp = kk.split('_')
        if len(pp) == 3 and pp[0][1:].isdigit() and pp[2].isdigit():
            x = Z[k][kk]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (k, kk); tc += 1
        elif len(pp) == 4 and pp[0] in ('Ti', 'Tr', 'Ta', 'Sr', 'Pr'):
            x = Z[k][kk]; assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (k, kk); pc += 1
    for a in d['arms']:
        for s in (ANCH + seeds if a == 'cutwA' else seeds):
            assert f'xmean_{a}_{s}' in X[k].files and f'af_{a}_{s}' in Z[k].files, (k, a, s)
            assert bool(np.isfinite(X[k][f'xmean_{a}_{s}']).all()), (k, a, s, 'xmean finite')
        if a != 'cutwA':
            assert not any(f'xmean_{a}_{s}' in X[k].files or f'af_{a}_{s}' in Z[k].files for s in ANCH), (k, a, 'stray anchor key')
    return tc, pc


trace_count = pool_count = 0
for w in K290:                                # L290 arrays are read (used-set arms + uniform comparators): same gates
    d = done[w]
    assert d['seeds'] == ALLSEEDS and d['ctr_cells'] == CTR and d['secs'] < 1700, (w, 'L290 seeds / ctr cells / hard stop')
    assert anch[w]['c0a135_pass'] and anch[w]['c0a175_pass'], (w, 'L290 anchors')
    trace_count, pool_count = [a + b for a, b in zip((trace_count, pool_count), check_arrays(w, d))]


def check_arms_file(w):
    """L291 structure gate (needs only arms_w< w>.json): stage, shas, plan, and every arm == its registered set."""
    a = read(out, f'arms_w{w}.json')
    assert a['wid'] == w and a['stage'] == 'L291-B' and a['prereg'] == psha and a['sets_sha'] == ssha, (w, 'stage / shas')
    assert a['menu_n'] == 80 and a['menu69_n'] == 69 and a['cert_menu_11'] == 11 and a['base_edges'] == 644177, (w, 'CERT-MENU')
    plan = a['arms_built']
    assert sorted(plan) == sorted(SETS['plan'][str(w)]) and len(plan) == len(set(plan)), (w, 'arms_built != sets.json plan')
    assert sorted(set(plan)) == sorted(a['edges']), (w, 'edges != arms_built')
    for arm, e in a['edges'].items():
        st = USED[UARM_INV[TWINS[arm]]] if arm in TWINS else STRAT[arm]
        assert e['set'] == st and len(e['removed']) == len(st), (w, arm, 'deleted entries')
        assert all(r['csr_index'] >= 0 and r['effective_weight'] != 0 for r in e['removed']), (w, arm, 'removed entry')
        assert [r['target'] for r in sorted(e['removed'], key=lambda r: r['target'])] == sorted(TGT[j] for j in st), (w, arm, 'deleted targets != set')
        if arm in TWINS:
            assert e['fixed_gain'] is True and e['twin_of'] == TWINS[arm] and arm in a['fixed'], (w, arm, 'twin flags')
        else:
            assert 'fixed_gain' not in e and arm not in a['fixed'], (w, arm, 'a stratified arm is flagged fixed')
            assert e['contains14'] == (14 in st) and e['eff'] == len([j for j in st if j not in N0]), (w, arm, 'contains14 / eff')
            assert (e['n'], e['cell'], e['syn_sum'], e['draws']) == (SMETA[arm]['n'], SMETA[arm]['cell'], SMETA[arm]['syn_sum'], SMETA[arm]['draws']), (w, arm, 'meta')
    assert sorted(sum((SETS['plan'][k] for k in SETS['plan']), [])) == sorted(SARMS + sorted(TWINS)), 'the two plans are not the 17 PREREG arms'
    return a


def check_twins_vs_stored(a):
    """the fixed twins ARE the stored L290 group graphs (same check the harness ran, re-read here)."""
    for arm, b in TWINS.items():
        if arm not in a['edges']:
            continue                       # each twin lives on ONE worker
        key = lambda r: (r['csr_index'], r['effective_weight'], r['syn'], r['target'])
        st = sorted([key(r) for r in read(l290, 'arms_w0.json')['edges'][b]['removed']])
        assert sorted([key(r) for r in a['edges'][arm]['removed']]) == st and len(st) == len(USED[UARM_INV[b]]), (arm, 'twin != stored L290 group graph')
        TWIN_CHECKED.add(arm)


TWIN_CHECKED = set()
for w in W:
    check_twins_vs_stored(check_arms_file(w))
assert TWIN_CHECKED == set(TWINS), ('a fixed twin was never compared to its stored group graph', TWIN_CHECKED)

OWN = {}


def own(key, name, arm):
    assert arm not in OWN, ('an arm name is owned by two workers', arm)
    OWN[arm] = (key, name)


for w in (0, 1, 2):
    for a in done[w]['arms']:
        if a != 'cutwA' or 'cutwA' not in OWN:
            own(w, a, a)
for k in K290:
    for a in done[k]['arms']:
        if a != 'cutwA':
            own(k, a, a)
if SELFTEST:
    _by = {11: [f'r11k{k}' for k in range(1, 6)], 30: [f'r30k{k}' for k in range(1, 6)], 46: [f'r46k{k}' for k in range(1, 6)]}
    ALIAS = {a: _by[len(STRAT[a])][(int(a[-1]) - 1) if a[-2] == 'w' else (3 + int(a[-1]) - 1)] for a in SARMS}
    ALIAS.update({'gc30f': 'gc30', 'gh46f': 'gh46'})
    for a in SARMS + sorted(TWINS):
        own(OWN[ALIAS[a]][0], ALIAS[a], a)
    GATE_KEYS = (10, 11)                      # the cutwA gate is exercised on L290's w0 / w1 arrays
else:
    for w in FIN0:
        k = 20 + w
        done[k], anch[k], armsj[k] = read(out, f'done_w{w}.json'), read(out, f'anchors_w{w}.json'), read(out, f'arms_w{w}.json')
        Z[k], X[k] = np.load(out / f'raw_w{w}.npz'), np.load(out / f'xm_w{w}.npz')
        for a in done[k]['arms']:
            if a != 'cutwA':
                own(k, a, a)
    GATE_KEYS = tuple(20 + w for w in FIN0)
MISSING = [a for a in SARMS + sorted(TWINS) if a not in OWN]          # L291 arms whose worker has not finished
assert not (FINAL and MISSING), ('FINAL mode with arms missing', MISSING)
assert all(a in OWN for a in ['g11', 'gc30', 'gh46', 'e14', 'nf'] + sorted(RAND)), 'a stored context arm is missing'
pools = read(l240, 'pools_w0.json')
xm = lambda k, a, s: X[k][f'xmean_{a}_{s}'].astype(np.float64)
raw_cut = [k for k in Z[0].files if k.startswith(tuple(f'c{g}_' for g in CTR)) and '_cutwA_' in k and int(k.rsplit('_', 1)[1]) in ALLSEEDS]
assert len(raw_cut) == 4 * 19
raw_all = [k for k in Z[0].files if '_cutwA_' in k]

# ---------------- gate: every worker's cutwA == A1's stored cutwA, exactly ----------------
gate = {k: dict(
    xmean=bool(all(np.array_equal(xm(k, 'cutwA', s), xm(0, 'cutwA', s)) for s in ALLSEEDS)),
    raw=bool(all(np.array_equal(Z[k][kk], Z[0][kk]) for kk in raw_cut)),
    raw_all=bool(set(kk for kk in Z[k].files if '_cutwA_' in kk) == set(raw_all)
                 and all(np.array_equal(np.atleast_1d(Z[k][kk]), np.atleast_1d(Z[0][kk])) for kk in raw_all)),
    af=bool(all(np.array_equal(np.atleast_1d(Z[k][f'af_cutwA_{s}']), np.atleast_1d(Z[0][f'af_cutwA_{s}'])) for s in ALLSEEDS))) for k in GATE_KEYS}
assert all(all(g.values()) for g in gate.values()), ('VOID: a worker cutwA trace != A1 stored', gate)
GAINS = {}
if not SELFTEST:
    for w in FIN0:
        k = 20 + w
        a, d = armsj[k], done[k]
        assert a['prereg'] == d['prereg_sha256'] == psha and a['sets_sha'] == ssha, (w, 'stage / shas')
        assert d['seeds'] == ALLSEEDS and d['ctr_cells'] == CTR, (w, 'seeds / ctr cells')
        assert anch[k]['c0a135_pass'] and anch[k]['c0a175_pass'], (w, 'anchors')
        assert anch[k]['c0a135_max'] == 0.0 and anch[k]['c0a175_max'] == 0.0, (w, 'anchors max')
        assert anch[k]['c0a135_checks'] == 46 and anch[k]['c0a175_checks'] == 25, (w, 'anchor coverage')
        assert anch[k]['g_cutwA_stored_exact'] and anch[k]['g_cutwA'] == STORED_G == d['gain']['cutwA'], (w, 'stored base gain')
        assert d['prereg_sha256'] == psha and d['secs'] < 1700, (w, 'PREREG sha / hard stop', d['secs'])
        assert d['arms'] == ['cutwA'] + a['arms_built'], (w, 'done arms')
        assert pools['pools'] == read(out, f'pools_w{w}.json')['pools'], (w, 'pool index sets differ')
        for arm in d['arms']:
            assert .12 <= d['gain'][arm] <= .18, (w, arm, 'gain window')
            if arm in TWINS:
                assert d['gain'][arm] == STORED_G, (w, arm, 'fixed twin gain')
        trace_count, pool_count = [x + y for x, y in zip((trace_count, pool_count), check_arrays(k, d))]
        GAINS.update({arm: d['gain'][arm] for arm in d['arms']})
assert 'g11f' in done[2]['arms'] and done[2]['gain']['g11f'] == STORED_G, 'A1 fixed twin of the 11-set not found'
enc = lambda o: o.item() if hasattr(o, 'item') else str(o)


def atomic(name, obj):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=1, default=enc))
    os.replace(tmp, out / name)


# ================= readout: P_a(s) = pool-union mean of the whole-window mean =================
R1 = read(l240, 'results_l240.json')
R290 = read(l290, 'results_l290.json')
PK = sorted(pools['pools'])
U = sorted(set(sum(pools['pools'].values(), [])))
P0 = {arm: np.array([xm(kk, nm, s)[U].mean() for s in seeds]) for arm, (kk, nm) in OWN.items()}
BASE = P0['cutwA']
F = float((P0['nf'] - BASE).std(ddof=1) / 4)
assert abs(F - R1['noise_twin']['F']) <= 1e-18, ('F drift vs A1', F, R1['noise_twin']['F'])
eps = 2 * F
t15 = 2.131449546
for arm in ['g11', 'gc30', 'gh46'] + sorted(RAND):          # loader certified against L290's STORED effects
    assert abs(float((P0[arm] - BASE).mean()) / F - R290['arms'][arm]['in_F']) <= 1e-9, (arm, 'stored L290 effect not reproduced')
E14 = float((P0['e14'] - BASE).mean()) if 'e14' in P0 else None
assert E14 is not None and abs(E14 / F - R290['arms']['e14']['in_F']) <= 1e-9, 'stored e14 effect not reproduced'
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
_a0 = P0['gc30'] - BASE
assert abs(float(SGN[0] @ _a0) / 16.0 - float(_a0.mean())) < 1e-15, 'sign matrix self-check'
_z, _p, _m = np.zeros(16), np.ones(16), np.r_[np.ones(15), -1.0]
assert flip(_z)['p_two'] == 1.0 and flip(_z)['p_up'] == 1.0 and flip(_z)['p_down'] == 1.0, 'flip self-check (all-zero arm reads p 1, never a count)'
assert abs(flip(_p)['p_up'] - 1 / 65536) < 1e-12 and abs(flip(_p)['p_two'] - 2 / 65536) < 1e-12, 'flip self-check (resolution floor)'
assert abs(flip(-_p)['p_two'] - 2 / 65536) < 1e-12 and abs(flip(-_p)['p_up'] - 1.0) < 1e-12, 'flip self-check (sign reversal)'
assert abs(flip(_m)['p_two'] - 34 / 65536) < 1e-12 and abs(flip(_m)['p_up'] - 17 / 65536) < 1e-12, 'flip self-check (15 of 16)'
IDENT = [[a, b] for a in P0 for b in P0 if a < b and np.array_equal(P0[a], P0[b])]
assert not IDENT or SELFTEST, ('two arms share one activity array', IDENT)      # a renamed arm is not an arm
for w in K290:                                # the L290 arrays were READ: their anchors are re-asserted on the stored maxima
    assert anch[w]['c0a135_max'] == 0.0 and anch[w]['c0a175_max'] == 0.0, (w, 'L290 anchor maxima')


def analyse(P):
    """PREREG s3-s4 on a dict arm -> 16 per-seed pool means. Nothing in here writes a file."""
    E = {a: float((P[a] - BASE).mean()) for a in P}

    def contrast(m, x):
        u = UARM[m]
        sg = float(np.sign(E[u]))
        g = flip(sg * (P[u] - P[x])); adv = sg * g['D']
        p_adv, p_opp = g['p_up'], g['p_down']
        st = 'EXCEEDS' if (adv >= eps and p_adv <= PMIN) else ('EXCEEDED_BY' if (adv <= -eps and p_opp <= PMIN) else 'WITHIN')
        st_l290 = 'EXCEEDS' if (adv >= eps and p_adv <= PMIN) else ('EXCEEDED_BY' if (adv <= -eps and (1 - p_adv) <= PMIN) else 'WITHIN')
        return dict(advantage=adv, in_F=adv / F, D=g['D'], SE=g['SE'], p_two=g['p_two'], p_adv=p_adv, p_opp=p_opp, status=st, status_l290_form=st_l290)

    MET = {}
    for m in ('abs', 'crofts', 'hop'):
        u = UARM[m]
        rows = {c: contrast(m, c) for c in CMP[m]}
        exW = sum(rows[c]['status'] == 'EXCEEDS' for c in WITH14[m])
        exF = sum(rows[c]['status'] == 'EXCEEDS' for c in FREE14[m])
        by = sum(rows[c]['status'] == 'EXCEEDED_BY' for c in CMP[m])
        within = sum(rows[c]['status'] == 'WITHIN' for c in CMP[m])
        assert exW + exF + by + within == len(CMP[m]), (m, 'status partition')
        if exW + exF == len(CMP[m]):
            label = 'SET_BEYOND_WEIGHT'
        elif exF == len(FREE14[m]) and exW == 0:
            label = 'E14_MEMBERSHIP'
        elif exW == 0 and exF == 0 and by == 0:
            label = 'WEIGHT_CARRIES'
        elif exW + exF == 0 and by >= 1:
            label = 'NOT_SPECIAL'
        else:
            label = 'MIXED'
        MET[m] = dict(arm=u, n=len(USED[m]), eff=len([j for j in USED[m] if j not in N0]), syn_sum=sum(SYN[j] for j in USED[m]), E=E[u], in_F=E[u] / F,
                      exW=exW, exF=exF, by=by, within=within, label=label, vacuous=VAC[m],
                      comparators={c: {k: v for k, v in r.items() if k != 'SE'} for c, r in rows.items()})
    clear = {a: bool(abs(E[a]) > eps) for a in SARMS}
    n_clear = int(sum(clear.values()))
    cnt = lambda L: sum(1 for m in MET if MET[m]['label'] == L)

    def verdict():
        if n_clear < K_BAR:
            return 'I_INSTRUMENT_AT_GROUP'
        if any(MET[m]['label'] == 'SET_BEYOND_WEIGHT' for m in MET):
            return 'SET_BEYOND_WEIGHT:' + next(m for m in MET if MET[m]['label'] == 'SET_BEYOND_WEIGHT')
        if cnt('E14_MEMBERSHIP') >= NMET:
            return 'E14_MEMBERSHIP_NOT_WEIGHT'
        if cnt('WEIGHT_CARRIES') >= NMET:
            return 'WEIGHT_CARRIES'
        if cnt('NOT_SPECIAL') >= NMET:
            return 'NOT_SPECIAL_AT_WEIGHT'
        return 'NO_DECISION'
    V = verdict()
    tw = {}
    for f, b in TWINS.items():
        tw[f] = dict(E_fixed=E[f], E_bisected=E[b], sign_agree=bool(np.sign(E[f]) == np.sign(E[b])), diff=abs(E[f] - E[b]),
                     diff_in_F=abs(E[f] - E[b]) / F, within=bool(abs(E[f] - E[b]) <= eps))
    f_ok = all(t['sign_agree'] and t['within'] for t in tw.values())
    lift = {}
    for n, m in SIZEU.items():
        fu = [a for a in RAND if len(RAND[a]) == n and 14 not in RAND[a]]
        if FREE14[m] and fu:
            g = flip(np.mean([P[a] for a in FREE14[m]], axis=0) - np.mean([P[a] for a in fu], axis=0))
            lift[n] = dict(strat=FREE14[m], uniform=fu, D=g['D'], in_F=g['D'] / F, p_up=g['p_up'], p_two=g['p_two'],
                           positive=bool(g['D'] > 0 and g['p_up'] <= PMIN))
        else:
            lift[n] = dict(strat=FREE14[m], uniform=fu, positive=None, note='UNMEASURABLE: an empty cell')
    eff = [len([j for j in STRAT[a] if j not in N0]) for a in SARMS]
    Es = [E[a] for a in SARMS]
    rho = spearman(Es, eff) if (len(set(Es)) >= 10 and len(set(eff)) >= 10) else None
    pred = dict(P1=bool(n_clear >= K_BAR),
                P2=bool(sum(1 for m in MET if MET[m]['exF'] == len(FREE14[m])) >= NMET),
                P3=bool(MET['abs']['exF'] == len(FREE14['abs']) and MET['abs']['exW'] == 0),
                P4=bool(MET['hop']['exW'] >= 1),
                P5=bool(f_ok),
                P6=bool(lift[11]['positive']),
                P7=bool(V not in ('WEIGHT_CARRIES', 'I_INSTRUMENT_AT_GROUP')))
    assert sum(bool(v) for v in pred.values()) == sum(int(v) for v in pred.values())
    return dict(verdict=V, n_clear=n_clear, clear=clear, per_metric=MET, twins=tw, EDGE_NOT_GAIN_GROUP=f_ok, lift=lift,
                rho_E_eff_strat=rho, predictions=pred, score=int(sum(bool(v) for v in pred.values())), E=E)


base_info = dict(card='L291', prereg_sha256=psha, sets_sha256=ssha, harness_sha256=sha(out, 'edge_run_l291.py'), l290_results_sha256=R290SHA,
                 seeds=seeds, K=K_BAR, eps=eps, F=F, exit_codes={w: EXIT[w] for w in W},
                 cutwA_gate={k: gate[k] for k in GATE_KEYS}, cutwA_arrays_compared=len(raw_all),
                 trace_arrays_verified=trace_count, pool_traces_verified=pool_count,
                 vacuous_by_identity=VAC, same_set_as_used=SETS['same_set'], dup_pairs=SETS['dup_pairs'])

if SELFTEST:
    # ================= SYNTHETIC coverage run: every registered branch must be reachable =================
    need = ['g11', 'gc30', 'gh46', 'nf'] + SARMS + sorted(TWINS) + sorted(RAND)
    assert all(a in P0 for a in need), ('selftest arms missing', [a for a in need if a not in P0])
    blend = lambda u, c: BASE + c * (P0[u] - BASE)
    noise = P0['nf'] - BASE
    SC = {}

    def scenario(name, **kw):
        P = {a: P0[a].copy() for a in need}
        for f, b in TWINS.items():
            P[f] = P0[b].copy()
        for m in CMP:
            for c in CMP[m]:
                u = UARM[m]
                P[c] = kw['all'](m, c, u) if 'all' in kw else (kw['W'](m, c, u) if c in WITH14[m] else kw['F'](m, c, u))
        SC[name] = analyse(P)
        return SC[name]
    scenario('aliased', all=lambda m, c, u: P0[c])
    scenario('instrument', all=lambda m, c, u: BASE + 0.2 * (-1) ** (len(c) + int(c[-1])) * noise)

    def fresh():                              # twins concordant with their stored group arm, comparators untouched
        P = {a: P0[a].copy() for a in need}
        for f, b in TWINS.items():
            P[f] = P0[b].copy()
        return P
    P = fresh()
    for m in CMP:
        for c in CMP[m]:
            P[c] = blend(UARM[m], 0.1 if m == 'abs' else 0.5)
    SC['set_beyond'] = analyse(P)
    for f, b in TWINS.items():
        P[f] = P0[b].copy()
    for m in CMP:
        for c in CMP[m]:
            P[c] = blend(UARM[m], 0.1 if m == 'abs' else 0.5)
    SC['set_beyond'] = analyse(P)
    scenario('membership', W=lambda m, c, u: P0[u], F=lambda m, c, u: blend(u, 0.1))
    scenario('weight_carries', all=lambda m, c, u: P0[u] + 0.05 * noise)
    scenario('not_special', all=lambda m, c, u: P0[u] + 0.6 * (P0[u] - BASE))
    P = fresh()
    for m in CMP:
        for c in CMP[m]:
            u = UARM[m]
            if m == 'abs':
                P[c] = P0[u] if c in WITH14[m] else blend(u, 0.1)
            elif m == 'crofts':
                P[c] = (blend(u, 0.5) if c == 's30w2' else P0[u])
            else:
                P[c] = (blend(u, 0.5) if c == 's46w1' else P0[u])
    SC['no_decision'] = analyse(P)
    P = fresh()
    P['gc30f'] = BASE - 0.3 * (P0['gc30'] - BASE)
    P['gh46f'] = blend('gh46', 0.3)
    for m in CMP:
        for c in CMP[m]:
            P[c] = P0[UARM[m]] + 0.05 * noise
    SC['twins_fail'] = analyse(P)
    P = fresh()
    for m in CMP:
        for c in CMP[m]:
            P[c] = blend('g11', 2.0) if c in FREE14['abs'] else P0[UARM[m]] + 0.05 * noise
    SC['lift_11'] = analyse(P)
    seen_v = sorted({r['verdict'] for r in SC.values()})
    seen_l = sorted({M['label'] for r in SC.values() for M in r['per_metric'].values()})
    seen_s = sorted({c['status'] for r in SC.values() for M in r['per_metric'].values() for c in M['comparators'].values()})
    seen_p = {k: sorted({r['predictions'][k] for r in SC.values()}) for k in SC['aliased']['predictions']}
    form_diff = [(n, m, c) for n, r in SC.items() for m, M in r['per_metric'].items() for c, v in M['comparators'].items() if v['status'] != v['status_l290_form']]
    print('SELFTEST scenarios:', sorted(SC))
    for n, r in SC.items():
        print(f"  {n:14s} -> {r['verdict']:26s} n_clear {r['n_clear']:2d} labels {[r['per_metric'][m]['label'] for m in ('abs', 'crofts', 'hop')]} "
              f"(exW/exF/by) {[(r['per_metric'][m]['exW'], r['per_metric'][m]['exF'], r['per_metric'][m]['by']) for m in ('abs', 'crofts', 'hop')]} "
              f"twins {r['EDGE_NOT_GAIN_GROUP']} lift11 {r['lift'][11]['positive']} pred {''.join(str(int(v)) for v in r['predictions'].values())}")
    print('  verdicts seen', seen_v, '| labels', seen_l, '| statuses', seen_s)
    print('  prediction values seen', seen_p, '| PREREG-form vs L290-form status differences', form_diff)
    ok = (set(seen_v) >= {'I_INSTRUMENT_AT_GROUP', 'SET_BEYOND_WEIGHT:abs', 'E14_MEMBERSHIP_NOT_WEIGHT', 'WEIGHT_CARRIES', 'NOT_SPECIAL_AT_WEIGHT', 'NO_DECISION'}
          and set(seen_l) >= {'SET_BEYOND_WEIGHT', 'E14_MEMBERSHIP', 'WEIGHT_CARRIES', 'NOT_SPECIAL', 'MIXED'}
          and set(seen_s) >= {'EXCEEDS', 'EXCEEDED_BY', 'WITHIN'}
          and all(v == [False, True] for v in seen_p.values()) and not form_diff)
    atomic('selftest_l291.json', dict(passed=bool(ok), verdicts_seen=seen_v, labels_seen=seen_l, statuses_seen=seen_s, prediction_values_seen=seen_p,
                                      form_differences=form_diff, scenarios={n: dict(verdict=r['verdict'], n_clear=r['n_clear'], predictions=r['predictions']) for n, r in SC.items()}))
    print('SELFTEST', 'PASS: every registered branch reachable, both values of every prediction produced' if ok else 'FAIL: a registered branch or prediction value is UNREACHABLE (STOP)')
    raise SystemExit(0 if ok else 3)

# ================= REAL: FINAL or PARTIAL, decided by the artefacts =================
if not FINAL:
    base_info.update(status='PARTIAL', effects_read=False, missing_arms=MISSING,
                     note='fewer than 2 L291 workers finished: verification only, no effect computed, branches NOT read')
    atomic('results_l291_partial.json', base_info)
    print('PARTIAL: workers', FIN0, 'of 2 | exit', EXIT, '| cutwA gate', {k: all(g.values()) for k, g in gate.items()})
    print('no effect read; branches NOT read; missing arms', base_info['missing_arms'])
    raise SystemExit(0)

NEED = ['g11', 'gc30', 'gh46', 'e14', 'nf'] + sorted(RAND) + SARMS + sorted(TWINS)
P = {a: P0[a] for a in NEED}
res = analyse(P)
E = res.pop('E')
PPBASE = np.array([[xm(0, 'cutwA', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds])
Vn = np.array([[xm(2, 'nf', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) - PPBASE
floorN = float(np.sqrt(((Vn.std(0, ddof=1) / 4) ** 2).sum()))


def row(a, n=None, eff=None):
    D = P[a] - BASE
    vec = np.array([[xm(*OWN[a], s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) - PPBASE
    N = float(np.linalg.norm(vec.mean(0)))
    return dict(E=E[a], CI=[E[a] - t15 * float(D.std(ddof=1)) / 4, E[a] + t15 * float(D.std(ddof=1)) / 4], in_F=E[a] / F, k_neg=int((D < 0).sum()),
                N=N, N_clear=bool(N > 2 * floorN), n=n if n is not None else (len(STRAT[a]) if a in STRAT else None),
                eff=eff if eff is not None else (len([j for j in STRAT[a] if j not in N0]) if a in STRAT else None),
                has14=bool(14 in (STRAT[a] if a in STRAT else (USED[UARM_INV[TWINS[a]]] if a in TWINS else []))),
                syn_sum=sum(SYN[j] for j in (STRAT[a] if a in STRAT else (USED[UARM_INV[TWINS[a]]] if a in TWINS else []))) if (a in STRAT or a in TWINS) else None,
                draws=SMETA[a]['draws'] if a in STRAT else None, gain=GAINS.get(a), dgain=(GAINS[a] - STORED_G) if a in GAINS else None,
                per_seed=D.tolist())
res.update(base_info, status='FINAL', floorN=floorN,
           strat_meta={a: SMETA[a] for a in SARMS},
           arms={a: row(a) for a in SARMS + sorted(TWINS) + ['g11', 'gc30', 'gh46', 'e14']},
           arms_gain={a: GAINS[a] for a in SARMS + sorted(TWINS) + ['cutwA']},
           uniform_l290_reported_not_scored={a: dict(in_F=E[a] / F, syn_sum=sum(SYN[j] for j in RAND[a]), has14=bool(14 in RAND[a]),
                                                     in_band=bool(SETS['bands'][str(len(RAND[a]))][0] <= sum(SYN[j] for j in RAND[a]) <= SETS['bands'][str(len(RAND[a]))][1]))
                                        for a in sorted(RAND)},
           context=dict(E14_in_F=E14 / F, g11f_in_F=R1['effects']['g11f']['mean'] / F, used_set_twin_g11f_note='A1 stored; NOT re-run in L291'),
           means=dict(strat_with_e14={m: float(np.mean([E[a] for a in WITH14[m]])) / F for m in CMP},
                      strat_free_e14={m: float(np.mean([E[a] for a in FREE14[m]])) / F for m in CMP},
                      uniform_free_e14={m: float(np.mean([E[a] for a in RAND if len(RAND[a]) == len(USED[m]) and 14 not in RAND[a]])) / F for m in CMP}))
assert set(res['arms']) == set(SARMS + sorted(TWINS) + ['g11', 'gc30', 'gh46', 'e14']) and len(res['per_metric']) == 3
atomic('results_l291.json', res)
print('FINAL: cutwA gate', {k: all(g.values()) for k, g in gate.items()}, '| traces', trace_count, 'pools', pool_count, '| F', F, 'eps', eps)
print('VERDICT', res['verdict'], '| n_clear', res['n_clear'], 'of 15 (bar', K_BAR, ') | score', res['score'], '/ 7', res['predictions'])
for m in ('abs', 'crofts', 'hop'):
    M = res['per_metric'][m]
    print(f"  {m:6s} {M['arm']} n {M['n']} eff {M['eff']} sum {M['syn_sum']} E {M['in_F']:+.2f} F | exW {M['exW']} exF {M['exF']} by {M['by']} within {M['within']} -> {M['label']}")
    for c, r in M['comparators'].items():
        print(f"      vs {c:6s} adv {r['in_F']:+6.2f} F p_adv {r['p_adv']:.5f} p_opp {r['p_opp']:.5f} {r['status']}" + (' [L290-form differs]' if r['status'] != r['status_l290_form'] else ''))
print('twins EDGE_NOT_GAIN_GROUP', res['EDGE_NOT_GAIN_GROUP'], {f: (round(t['diff_in_F'], 2), t['sign_agree']) for f, t in res['twins'].items()})
print('lift (g):', {n: (round(v['in_F'], 2), round(v['p_up'], 5), v['positive']) for n, v in res['lift'].items()}, '| rho(E,eff)', res['rho_E_eff_strat'])
for a in SARMS + sorted(TWINS):
    r = res['arms'][a]
    print(f"  {a:6s} E {r['in_F']:+6.2f} F k_neg {r['k_neg']:2d} {'clr' if abs(r['in_F']) > 2 else '   '} vec{'clr' if r['N_clear'] else '   '} "
          f"e14 {int(r['has14'])} sum {r['syn_sum']} draws {r['draws']} dg {r['dgain']:+.2e}")
