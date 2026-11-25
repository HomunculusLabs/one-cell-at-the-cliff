# Run from banc/:  python l291/static_probe.py
# STATIC, read-only design input for the L291 PREREG: the stored 69-edge menu's raw
# synapse counts, the three used-sets' synapse sums, and (Monte Carlo, no rollout) the
# acceptance rate of candidate stratification bands for uniform n-subsets. Nothing here
# is an L291 outcome; no L291 set exists yet.
import json
import numpy as np

S = json.load(open('l290/sets.json'))
menu = {int(m['j']): m for m in S['menu']}
syn = np.array([menu[j]['syn'] for j in range(69)])
N0 = set(S['noop'])
used = {m: sorted(int(j) for j in S['used'][m]) for m in ('abs', 'crofts', 'hop')}
raw = {int(n): v for n, v in S['raw'].items()}

print('menu syn: n', len(syn), 'sum', int(syn.sum()), 'mean %.2f sd %.2f min %d max %d' % (
    syn.mean(), syn.std(), syn.min(), syn.max()))
order = sorted(range(69), key=lambda j: (-syn[j], j))
print('rank (by raw syn, ties by j): j:syn  [* = no-op N0]')
for r, j in enumerate(order):
    flag = 'N0' if j in N0 else '  '
    print('  %2d  j%2d syn %4d %s  used: %s%s%s' % (
        r + 1, j, syn[j], flag, 'A' if j in used['abs'] else '.', 'C' if j in used['crofts'] else '.',
        'H' if j in used['hop'] else '.'))
T = {}
for m in used:
    T[m] = int(syn[used[m]].sum())
    print('U_%-6s n %2d  eff %2d  syn-sum %5d  e14 share %.3f  no-op syn-sum %d' % (
        m, len(used[m]), len([j for j in used[m] if j not in N0]), T[m],
        syn[14] / T[m], sum(syn[j] for j in used[m] if j in N0)))
print('e14: syn', int(syn[14]), 'weight rank', order.index(14) + 1, 'of 69 | in raw sets:',
      {n: (14 in raw[n]) for n in raw})
SIZE2M = {11: 'abs', 30: 'crofts', 46: 'hop'}
for n in (11, 30, 46):
    um = used[SIZE2M[n]]
    print('RW_%d syn-sum %d | U(n=%d) syn-sum %d | overlap %d' % (
        n, int(syn[raw[n]].sum()), n, T[SIZE2M[n]], len(set(raw[n]) & set(um))))

rng = np.random.Generator(np.random.PCG64(29199))
ND = 2_000_000
for n, m in ((11, 'abs'), (30, 'crofts'), (46, 'hop')):
    sums = np.empty(ND, np.int64)
    has14 = np.empty(ND, bool)
    for b in range(0, ND, 200000):
        k = min(200000, ND - b)
        for i in range(k):
            d = rng.choice(69, size=n, replace=False)
            sums[b + i] = syn[d].sum()
            has14[b + i] = 14 in d
    mu, sd = sums.mean(), sums.std()
    pct = float((sums < T[m]).mean())
    print('n %2d uniform-subset syn-sum: mean %.1f sd %.1f | U sum %d = %.2f sd, percentile %.3f' % (
        n, mu, sd, T[m], (T[m] - mu) / sd, pct))
    # exact finite-population SD of a uniform n-subset sum (check on the Monte Carlo)
    var = (syn.var() * n * (69 - n) / 68.0)
    print('    exact SD of an n-subset sum (finite population): %.1f' % var ** 0.5)
    for lab, band in (('+/-5%', 0.05 * T[m]), ('+/-10%', 0.10 * T[m]), ('+/-0.25sd', 0.25 * sd),
                      ('+/-0.5sd', 0.5 * sd)):
        inb = np.abs(sums - T[m]) <= band
        print('    band %-9s width %6.1f  accept %.4f  (expected raw draws per subset %.0f)  P(e14|band) %.3f  P(e14|out) %.3f' % (
            lab, band, inb.mean(), 1.0 / max(inb.mean(), 1e-12), has14[inb].mean() if inb.any() else float('nan'),
            has14[~inb].mean()))
