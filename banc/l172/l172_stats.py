"""L172 stage (a): the statistics pass.  ZERO rollouts.

Everything here is re-derived from STORED artifacts with this file's own
metric implementation.  Order is CERT-first (PREREG): the census cells and
the per-batch duty cells must reproduce before any new pooled number is
read.
"""
import json
import math
import os
import re
import zipfile
from collections import defaultdict

import numpy as np

OUT = {}
HERE = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.dirname(HERE)
Z = 1.959963984540054

# ---------------------------------------------------------------- helpers
def wilson(k, n):
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt((p * (1 - p) + Z * Z / (4 * n)) / n) / d
    return max(0.0, c - h), min(1.0, c + h)


def newcombe(k1, n1, k2, n2):
    """Hybrid-score (Newcombe method 10) CI for p1 - p2."""
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = k1 / n1 - k2 / n2
    lo = d - math.sqrt((k1 / n1 - l1) ** 2 + (u2 - k2 / n2) ** 2)
    hi = d + math.sqrt((u1 - k1 / n1) ** 2 + (k2 / n2 - l2) ** 2)
    return d, max(-1.0, lo), min(1.0, hi)


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]] (stdlib only)."""
    from math import comb
    n = a + b + c + d
    r1, c1 = a + b, a + c
    tot = comb(n, c1)

    def pr(x):
        return comb(r1, x) * comb(n - r1, c1 - x) / tot

    p0 = pr(a)
    lo = max(0, c1 - (n - r1))
    hi = min(r1, c1)
    return min(1.0, sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9)))


def boot_ci(vals, nboot=10000, seed=1720):
    v = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(nboot, len(v)))
    means = v[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# --------------------------------------------------- CERT-1: l156 census
rows = json.load(open(os.path.join(BANC, 'l156/static.json')))
st = rows['pooled']
R = rows['rows']
inc = rows['included_files']
assert len(inc) == 28, len(inc)


def census(arm, files):
    below = n = survive = agree = bbin = 0
    fb = []
    for f in files:
        rec = R.get(f, {}).get(arm)
        if not rec:
            continue
        for s, r in rec.items():
            n += 1
            below += bool(r['below'])
            bbin += bool(r['below_bin'])
            survive += bool(r['survive'])
            if r['below']:
                agree += bool(r['agree'])
                fb.append(r['f_glob'])
    return dict(n=n, below=below, below_bin=bbin, survive=survive, agree=agree,
                med_f_below=float(np.median(fb)) if fb else None)


c_b65 = census('b65', inc)
s_b65 = st['b65_nonjitter']
assert (c_b65['n'], c_b65['below'], c_b65['below_bin'], c_b65['survive'], c_b65['agree']) == \
       (s_b65['n'], s_b65['below'], s_b65['below_bin'], s_b65['survive'], s_b65['agree']), (c_b65, s_b65)
assert abs(c_b65['med_f_below'] - s_b65['med_f_below']) < 1e-9
lb, _ = wilson(c_b65['below'], c_b65['n'])
assert abs(lb - s_b65['wilson_lb']) < 1e-9, (lb, s_b65['wilson_lb'])

c_full = census('full', inc)
s_full = st['full_nonjitter']
assert (c_full['n'], c_full['below'], c_full['below_bin'], c_full['survive'], c_full['agree']) == \
       (s_full['n'], s_full['below'], s_full['below_bin'], s_full['survive'], s_full['agree']), (c_full, s_full)
assert abs(c_full['med_f_below'] - s_full['med_f_below']) < 1e-9
lbf, _ = wilson(c_full['below'], c_full['n'])
assert abs(lbf - s_full['wilson_lb']) < 1e-9
print('CERT-1 PASS  l156 census cells re-derived from stored rows: '
      'b65 %d/%d lb %.4f | full %d/%d lb %.4f'
      % (c_b65['below'], c_b65['n'], lb, c_full['below'], c_full['n'], lbf))

# ------------------------------------------ unique-seed census (new read)
def census_unique(arm, files):
    seen, below, n, surv, agr, fb = {}, 0, 0, 0, 0, []
    dupes, dup_bad = 0, []
    for f in files:
        rec = R.get(f, {}).get(arm)
        if not rec:
            continue
        for s, r in rec.items():
            if s in seen:
                dupes += 1
                if seen[s]['below'] != r['below'] or \
                   abs(seen[s]['f_glob'] - r['f_glob']) > 1e-6:
                    dup_bad.append((f, arm, s))
                continue
            seen[s] = r
            n += 1
            below += bool(r['below'])
            surv += bool(r['survive'])
            if r['below']:
                agr += bool(r['agree'])
                fb.append(r['f_glob'])
    return dict(n=n, below=below, survive=surv, agree=agr, dupes=dupes,
                dup_inconsistent=dup_bad,
                med_f_below=float(np.median(fb)) if fb else None,
                seeds=sorted(int(x) for x in seen))


u_b65 = census_unique('b65', inc)
u_full = census_unique('full', inc)
for u in (u_b65, u_full):
    u['lb'], u['ub'] = wilson(u['below'], u['n'])
print('UNIQUE  b65 %d/%d (was %d/%d) lb %.4f  dupes %d inconsistent %d'
      % (u_b65['below'], u_b65['n'], c_b65['below'], c_b65['n'], u_b65['lb'],
         u_b65['dupes'], len(u_b65['dup_inconsistent'])))
print('UNIQUE  full %d/%d (was %d/%d) lb %.4f  dupes %d inconsistent %d'
      % (u_full['below'], u_full['n'], c_full['below'], c_full['n'], u_full['lb'],
         u_full['dupes'], len(u_full['dup_inconsistent'])))
OUT['census_unique'] = {
    'b65': {k: u_b65[k] for k in ('n', 'below', 'survive', 'agree', 'dupes',
                                  'lb', 'ub', 'med_f_below')},
    'full': {k: u_full[k] for k in ('n', 'below', 'survive', 'agree', 'dupes',
                                    'lb', 'ub', 'med_f_below')},
    'stored_trace_forms': {'b65': [s_b65['below'], s_b65['n']],
                           'full': [s_full['below'], s_full['n']]},
    'dup_inconsistent_total': len(u_b65['dup_inconsistent']) + len(u_full['dup_inconsistent']),
}

# ------------------------------------ ADMISSIBILITY A2: constant blocks
CONST = dict(TAU=0.05, DT=0.01, RMAX=1.0, BG=0.02, NOISE=0.01,
             SETTLE=400, WIN=6000, SEG=2000)
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]


def parse_consts(script):
    src = open(script).read()
    got = {}
    m = re.search(r'^TAU, DT, RMAX = ([\d.]+), ([\d.]+), ([\d.]+)', src, re.M)
    if m:
        got.update(TAU=float(m.group(1)), DT=float(m.group(2)), RMAX=float(m.group(3)))
    m = re.search(r'^BG, NOISE = ([\d.]+), ([\d.]+)', src, re.M)
    if m:
        got.update(BG=float(m.group(1)), NOISE=float(m.group(2)))
    m = re.search(r'^SETTLE, WIN = (\d+), (\d+)', src, re.M)
    if m:
        got.update(SETTLE=int(m.group(1)), WIN=int(m.group(2)))
    m = re.search(r'^SEG = (\d+)', src, re.M)
    if m:
        got['SEG'] = int(m.group(1))
    m = re.search(r'^SEGB = (\[.*?\])', src, re.M)
    if m:
        got['SEGB'] = eval(m.group(1))
    return got


# -------------------------------------------- inventory of stored traces
TI = re.compile(r'^Ti_fL_(.+)_(\d+)$')
files = sorted(f for f in
               [os.path.join(d, n) for d in sorted(os.listdir(BANC))
                if os.path.isdir(os.path.join(BANC, d))
                for n in sorted(os.listdir(os.path.join(BANC, d)))
                if n.startswith('raw_') and n.endswith('.npz')]
               if 'partial' not in f)
inv = defaultdict(dict)      # arm -> file -> [seeds]
admissible, rejected = {}, {}
for f in files:
    run = os.path.dirname(f)
    script = os.path.join(BANC, run + '_run.py')
    if not os.path.exists(script):
        cand = [os.path.join(BANC, run, x) for x in os.listdir(os.path.join(BANC, run))
                if x.endswith('_run.py')]
        script = cand[0] if cand else None
    ok, why = False, 'no run script'
    if script and os.path.exists(script):
        got = parse_consts(script)
        miss = {k: (got.get(k), v) for k, v in CONST.items() if got.get(k) != v}
        segok = got.get('SEGB') == SEGB
        ok = (not miss) and segok
        why = 'ok' if ok else f'const mismatch {miss} segb={segok}'
    jitter = '_j' in os.path.basename(f) and 'j0' not in os.path.basename(f)
    if jitter:
        ok, why = False, 'jittered-gain replicate (different network)'
    (admissible if ok else rejected)[f] = why
    if not ok:
        continue
    ks = [n[:-4] for n in zipfile.ZipFile(os.path.join(BANC, f)).namelist()]
    for k in ks:
        m = TI.match(k)
        if m:
            inv[m.group(1)].setdefault(f, []).append(int(m.group(2)))

print('ADMISSIBLE files %d | rejected %d' % (len(admissible), len(rejected)))
for f, w in rejected.items():
    print('   reject %-26s %s' % (f, w))
OUT['admissibility'] = {'n_admissible': len(admissible),
                        'admissible': sorted(admissible),
                        'rejected': rejected,
                        'const_block': CONST, 'segb': SEGB}

# -------------------------------------------------- the duty metric (mine)
TS = np.arange(499, 6000, 10)
QM = np.zeros(len(TS), bool)
for a0, b0, fr in SEGB:
    if fr == 0.7:
        QM |= (TS >= a0 + 500) & (TS < b0)
QTS = TS[QM]


def S(a, b):
    if a.std() <= 1e-6 or b.std() <= 1e-6:
        return float('nan')
    return float(-np.corrcoef(a, b)[0, 1])


_zc = {}


def zopen(f):
    if f not in _zc:
        _zc[f] = np.load(os.path.join(BANC, f))
    return _zc[f]


def duty(f, arm, seed):
    z = zopen(f)
    tr = {c: z[f'Ti_{c}_{arm}_{seed}'][:6000] for c in ('fL', 'fR', 'eL', 'eR')}
    dl, dr = [], []
    for t in QTS:
        dl.append(S(tr['fL'][t - 499:t + 1], tr['eL'][t - 499:t + 1]) >= .25)
        dr.append(S(tr['fR'][t - 499:t + 1], tr['eR'][t - 499:t + 1]) >= .25)
    return float(np.nanmean(dl)), float(np.nanmean(dr))


# ------------------------------------------------- CERT-2 / CERT-3 metric
CERT2 = [('l142/raw_l142.npz', 'l142/results_l142.json', 'cutng25', range(3301, 3317)),
         ('l145/raw_l145.npz', 'l145/results_l145.json', 'eMotTop5', range(3333, 3349)),
         ('l150/raw_l150.npz', 'l150/results_l150.json', 'silW', range(3365, 3381)),
         ('l169d/raw_l169d.npz', 'l169d/results_l169d.json', 'cutng25', range(3513, 3529))]
cert2 = {}
for f, rj, arm, seeds in CERT2:
    _t = json.load(open(os.path.join(BANC, rj)))['table']
    # table shape differs across the lineage: pool-first (l142/l145/l150)
    # vs arm-first (l169x).  Both are stored forms; pick by key presence.
    rs = _t['Ti'][arm] if 'Ti' in _t else _t[arm]
    L = np.array([duty(f, arm, s)[0] for s in seeds])
    Rr = np.array([duty(f, arm, s)[1] for s in seeds])
    kR, kL = int((Rr >= .5).sum()), int((L >= .5).sum())
    assert kR == rs['kR'] and kL == rs['kL'], (f, arm, kR, kL, rs)
    assert round(float(Rr.mean()), 3) == rs['meanR'], (f, arm, Rr.mean(), rs['meanR'])
    lbR, ubR = wilson(kR, len(L))
    assert abs(lbR - rs['lbR']) < 1e-9 and abs(ubR - rs['ubR']) < 1e-9, (f, arm)
    cert2[f'{f}|{arm}'] = dict(kR=kR, kL=kL, meanR=round(float(Rr.mean()), 3))
print('CERT-2/3 PASS  4 stored per-batch cells reproduced exactly (kR, kL, '
      'meanR 3dp) with stored Wilson bounds to 1e-9')
OUT['cert'] = {'l156': {'b65': c_b65, 'full': c_full}, 'metric': cert2}

# ------------------------------- canonical unique-seed pooled per arm
ARMS = ['full', 'b65', 'cutwA', 'cutng25', 'cutng25p', 'cutng19', 'cutng23',
        'cutng29', 'cutk5', 'cut58', 'silW', 'eMotTop5',
        'eMotBot5', 'eOutMot', 'cutscr0']
# ALIAS: l144 named the carrier activity clamp on the cut base
# `sil1110_wA`, l150 onward named the identical manipulation `silW`, and
# the draft already pools the two (its "B30+B33 pooled 28/32").  Pool them
# as ONE arm, deduping the shared forward-chain anchor seeds.
ALIAS = {'silW': ['silW', 'sil1110_wA']}
GAINS = {}
for d in sorted(os.listdir(BANC)):
    p = os.path.join(BANC, d, f'results_{d}.json')
    if os.path.exists(p):
        try:
            g = json.load(open(p)).get('gains')
        except Exception:
            g = None
        if isinstance(g, dict):
            GAINS[d] = {k: v for k, v in g.items() if isinstance(v, (int, float))}

pooled = {}
for arm in ARMS:
    fl = {}
    for tok in ALIAS.get(arm, [arm]):
        for f, ss in inv.get(tok, {}).items():
            fl.setdefault(f, []).extend([(tok, s0) for s0 in ss])
    if not fl:
        continue
    seen, recs, dup, dupbad = {}, [], 0, []
    for f in sorted(fl):
        run = os.path.dirname(f)
        gcan = None
        for d, gg in GAINS.items():
            if arm in gg:
                gcan = gg[arm]
                break
        gstored = GAINS.get(run, {}).get(arm)
        if gcan is not None and gstored is not None and abs(gstored - gcan) > 1e-9:
            continue                       # A3
        for tok, s in sorted(fl[f], key=lambda x: x[1]):
            dR = duty(f, tok, s)
            if s in seen:
                dup += 1
                if abs(seen[s][1] - dR[1]) > 1e-6:
                    dupbad.append((f, s, seen[s][1], dR[1]))
                continue
            seen[s] = dR
            recs.append((f, s, dR[0], dR[1]))
    L = np.array([r[2] for r in recs])
    Rr = np.array([r[3] for r in recs])
    n = len(recs)
    kR, kL = int((Rr >= .5).sum()), int((L >= .5).sum())
    lbR, ubR = wilson(kR, n)
    lbL, ubL = wilson(kL, n)
    bR = boot_ci(Rr)
    bL = boot_ci(L)
    pooled[arm] = dict(dutyR=[round(float(x), 6) for x in Rr],
                       dutyL=[round(float(x), 6) for x in L],
                       n=n, kR=kR, kL=kL, lbR=lbR, ubR=ubR, lbL=lbL, ubL=ubL,
                       meanR=float(Rr.mean()), meanL=float(L.mean()),
                       bootR=[bR[0], bR[1]], bootL=[bL[0], bL[1]],
                       files=sorted({r[0] for r in recs}),
                       n_files=len({r[0] for r in recs}),
                       dup_seeds=dup, dup_inconsistent=dupbad,
                       seeds=sorted(seen))
    print('%-12s n=%3d files=%2d kR=%3d [%.4f,%.4f] meanR=%.3f boot[%.3f,%.3f] '
          'kL=%3d dup=%d bad=%d'
          % (arm, n, pooled[arm]['n_files'], kR, lbR, ubR, Rr.mean(),
             bR[0], bR[1], kL, dup, len(dupbad)))

OUT['pooled'] = {a: {k: v for k, v in d.items()
                     if k not in ('seeds', 'dutyR', 'dutyL')}
                 for a, d in pooled.items()}
OUT['per_seed'] = {a: dict(seeds=d['seeds'], dutyR=d['dutyR'], dutyL=d['dutyL'])
                   for a, d in pooled.items()}
OUT['pooled_seed_sets'] = {a: d['seeds'] for a, d in pooled.items()}

# P1 / P2 / S3
all_dupbad = [b for d in pooled.values() for b in d['dup_inconsistent']]
dupseeds = set()
for a in pooled:
    cnt = defaultdict(int)
    for tok in ALIAS.get(a, [a]):
        for f, ss in inv.get(tok, {}).items():
            for s0 in ss:
                cnt[s0] += 1
    dupseeds |= {s0 for s0, c in cnt.items() if c > 1}
dupseeds = sorted(dupseeds)
OUT['p1_recurring_seeds'] = dupseeds[:20]
OUT['p1_n_recurring'] = len(dupseeds)
OUT['s3_dup_inconsistent'] = all_dupbad
print('P1 recurring seeds (%d): %s' % (len(dupseeds), dupseeds[:12]))
print('S3 duplicate inconsistencies: %d' % len(all_dupbad))

# -------------------------------------- differences WITH intervals
PAIRS = [('twin_vs_base', 'cutng25p', 'cutwA'),
         ('carrier_vs_twin', 'cutng25', 'cutng25p'),
         ('carrier_vs_base', 'cutng25', 'cutwA'),
         ('silW_vs_base', 'silW', 'cutwA'),
         ('silW_vs_carrier', 'silW', 'cutng25'),
         ('eMotTop5_vs_base', 'eMotTop5', 'cutwA'),
         ('eMotBot5_vs_base', 'eMotBot5', 'cutwA'),
         ('eOutMot_vs_base', 'eOutMot', 'cutwA'),
         ('eOutMot_vs_carrier', 'eOutMot', 'cutng25'),
         ('base_vs_full', 'cutwA', 'full'),
         ('cutng23_vs_base', 'cutng23', 'cutwA'),
         ('scr0_vs_base', 'cutscr0', 'cutwA')]
diffs = {}
for name, a, b in PAIRS:
    if a not in pooled or b not in pooled:
        continue
    A, B = pooled[a], pooled[b]
    d, lo, hi = newcombe(A['kR'], A['n'], B['kR'], B['n'])
    p = fisher(A['kR'], A['n'] - A['kR'], B['kR'], B['n'] - B['kR'])
    diffs[name] = dict(a=a, b=b, ka=A['kR'], na=A['n'], kb=B['kR'], nb=B['n'],
                       diff=d, lo=lo, hi=hi, fisher_p=p,
                       contains_zero=bool(lo <= 0 <= hi))
    print('%-20s %3d/%-3d vs %3d/%-3d  d=%+.3f [%+.3f,%+.3f] p=%.4g %s'
          % (name, A['kR'], A['n'], B['kR'], B['n'], d, lo, hi, p,
             'CONTAINS 0' if lo <= 0 <= hi else ''))
# left-side death leg
if 'cutng25' in pooled and 'cutwA' in pooled:
    A, B = pooled['cutng25'], pooled['cutwA']
    d, lo, hi = newcombe(A['kL'], A['n'], B['kL'], B['n'])
    diffs['left_carrier_vs_base'] = dict(
        a='cutng25.L', b='cutwA.L', ka=A['kL'], na=A['n'], kb=B['kL'], nb=B['n'],
        diff=d, lo=lo, hi=hi,
        fisher_p=fisher(A['kL'], A['n'] - A['kL'], B['kL'], B['n'] - B['kL']),
        contains_zero=bool(lo <= 0 <= hi))
    print('left_carrier_vs_base %3d/%-3d vs %3d/%-3d  d=%+.3f [%+.3f,%+.3f] p=%.4g'
          % (A['kL'], A['n'], B['kL'], B['n'], d, lo, hi,
             diffs['left_carrier_vs_base']['fisher_p']))
OUT['diffs'] = diffs

# ----------------------------------------------- sham spread (n=3 caveat)
g3 = json.load(open(os.path.join(BANC, 'l137/results_l137.json')))['g3']
sham = g3['silrand_meanR']
OUT['sham'] = dict(n=len(sham), values=sham, spread=max(sham) - min(sham),
                   stored_spread=g3['spread'])
print('sham n=%d values=%s spread=%.3f (stored %.3f)'
      % (len(sham), sham, max(sham) - min(sham), g3['spread']))

# branch
if all_dupbad:
    branch = 'S3_dup_inconsistent'
else:
    branch = 'S1_counts_stable'      # class comparison is folded by hand below
OUT['branch_dup'] = branch
OUT['unit_of_inference'] = ('a noise seed of ONE fixed network (one graph, '
                            'one bisected gain, one drive protocol); intervals '
                            'describe seed-to-seed variability of that network, '
                            'not variability across connectomes, cohorts or gains')
json.dump(OUT, open(os.path.join(HERE, 'stats.json'), 'w'), indent=1)
print('WROTE', os.path.join(HERE, 'stats.json'))
