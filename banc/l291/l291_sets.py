# Run from banc/:  python l291/l291_sets.py   -> writes l291/sets.json + l291/sets.sha256
# Materialises the 15 stratified subsets EXACTLY as l291/PREREG.md s2 (i) registers them. Refuses to run
# against a PREREG whose sha file does not match, and refuses to overwrite an existing sets.json.
import hashlib
import json
from pathlib import Path

import numpy as np

out = Path('l291')
assert not (out / 'sets.json').exists(), 'sets.json exists: no edit after freezing (STOP)'
psha = hashlib.sha256((out / 'PREREG.md').read_bytes()).hexdigest()
assert psha == (out / 'PREREG.sha256').read_text().split()[0], 'PREREG sha mismatch (STOP)'
S = json.loads(Path('l290/sets.json').read_text())
syn = [int(m['syn']) for m in S['menu']]
USED = {m: sorted(int(j) for j in S['used'][m]) for m in ('abs', 'crofts', 'hop')}
SIZEU = {11: 'abs', 30: 'crofts', 46: 'hop'}
BAND = {n: (int(np.ceil(0.95 * sum(syn[j] for j in USED[SIZEU[n]]))),
            int(np.floor(1.05 * sum(syn[j] for j in USED[SIZEU[n]])))) for n in SIZEU}
prereg = (out / 'PREREG.md').read_text()
assert '[%d, %d] / [%d, %d] / [%d, %d]' % (BAND[11] + BAND[30] + BAND[46]) in prereg, ('band not the frozen one', BAND)
rng = np.random.Generator(np.random.PCG64(29113))
STRAT, ORDER, META = {}, {}, {}
for n in (11, 30, 46):
    lo, hi = BAND[n]
    for cell, k in (('w', 3), ('f', 2)):
        for i in range(1, k + 1):
            a = f's{n}{cell}{i}'
            nd = 0
            while True:
                nd += 1
                assert nd <= 2000000, ('UNDRAWABLE (PREREG s2: report missing, never widen)', a)
                d = [int(j) for j in rng.choice(69, size=n, replace=False)]
                if (14 in d) != (cell == 'w'):
                    continue
                s = sum(syn[j] for j in d)
                if lo <= s <= hi:
                    break
            STRAT[a], ORDER[a] = sorted(d), d
            META[a] = dict(n=n, cell=cell, syn_sum=s, draws=nd, eff=len([j for j in d if j not in set(S['noop'])]),
                           contains14=bool(14 in d))
assert len(STRAT) == 15 and len(set(tuple(v) for v in STRAT.values())) == 15, 'duplicate stratified arm'
N0 = set(S['noop'])
PLAN = {0: ['s11w1', 's11w2', 's11w3', 's11f1', 's11f2', 's30w1', 's30w2', 's30w3', 'gc30f'],
        1: ['s30f1', 's30f2', 's46w1', 's46w2', 's46w3', 's46f1', 's46f2', 'gh46f']}
for w in (0, 1):
    assert ' '.join(PLAN[w]) in prereg, ('worker plan not the frozen one', w)
sets = dict(card='L291', prereg_sha256=psha, seed=29113, band=0.05, max_draws=2000000,
            bands={str(n): list(BAND[n]) for n in BAND},
            menu=S['menu'], used=S['used'], raw=S['raw'], random=S['random'], noop=S['noop'],
            strat=STRAT, strat_draw_order=ORDER, strat_meta=META, twins={'gc30f': 'gc30', 'gh46f': 'gh46'},
            plan={str(k): v for k, v in PLAN.items()},
            same_set=[a for a, v in STRAT.items() if v in [USED[m] for m in USED]],
            dup_pairs=[])
(out / 'sets.json').write_text(json.dumps(sets, indent=1))
h = hashlib.sha256((out / 'sets.json').read_bytes()).hexdigest()
(out / 'sets.sha256').write_text(f'{h}  sets.json\n')
print('sets.json sha256', h, '| PREREG', psha[:16], '| bands', BAND, '| same_set', sets['same_set'])
for a in sorted(STRAT, key=lambda a: (META[a]['n'], a)):
    M = META[a]
    print('  %-6s n %2d %s e14 %d  sum %4d (U %4d, %+4d)  eff %2d  raw draws %d' % (
        a, M['n'], M['cell'], M['contains14'], M['syn_sum'], sum(syn[j] for j in USED[SIZEU[M['n']]]),
        M['syn_sum'] - sum(syn[j] for j in USED[SIZEU[M['n']]]), M['eff'], M['draws']))
