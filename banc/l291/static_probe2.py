# Run from banc/:  python l291/static_probe2.py
# STATIC design input, read-only: L290's STORED effects (results_l290.json) against each arm's
# raw synapse sum -- which of L290's uniform random subsets already sit inside the +/-5 % band
# of its size's used-set, and how the 69 SINGLE-edge effects relate to raw weight. Nothing here
# is an L291 outcome.
import json
import numpy as np

S = json.load(open('l290/sets.json'))
R = json.load(open('l290/results_l290.json'))
menu = {int(m['j']): m for m in S['menu']}
syn = {j: int(menu[j]['syn']) for j in range(69)}
N0 = set(S['noop'])
used = {m: sorted(int(j) for j in S['used'][m]) for m in ('abs', 'crofts', 'hop')}
G = {a: sorted(int(j) for j in v) for a, v in S['random'].items()}
G.update({'gc30': used['crofts'], 'gh46': used['hop'], 'rw11': sorted(S['raw']['11']),
          'rw30': sorted(S['raw']['30']), 'rw46': sorted(S['raw']['46'])})
F = R['F']
A = R['arms']
UARM = {11: 'g11', 30: 'gc30', 46: 'gh46'}
T = {11: sum(syn[j] for j in used['abs']), 30: sum(syn[j] for j in used['crofts']),
     46: sum(syn[j] for j in used['hop'])}
print('F', F, '| used-set E (F):', {u: round(A[u]['in_F'], 2) for u in UARM.values()},
      '| sums', T)
rows = []
for a in sorted(G, key=lambda a: (len(G[a]), a)):
    n = len(G[a])
    ss = sum(syn[j] for j in G[a])
    e = A[a]['in_F'] if a in A else (A['g11']['in_F'] if a == 'gc30' and False else None)
    e = A['g11']['in_F'] if a == 'gc30' and False else e
    inb = abs(ss - T[n]) <= 0.05 * T[n]
    rows.append((a, n, ss, A[a]['in_F'], 14 in G[a], len([j for j in G[a] if j not in N0]), inb, ss - T[n]))
print('arm      n  syn-sum     E(F)  e14  eff  in +/-5% band  sum-U')
for a, n, ss, e, h14, eff, inb, d in rows:
    print('%-7s %2d  %6d  %+7.2f   %d  %3d    %s   %+d' % (a, n, ss, e, int(h14), eff, 'YES' if inb else ' no', d))
x = np.array([r[2] for r in rows], float)
y = np.array([r[3] for r in rows], float)


def spear(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


rnd = [r for r in rows if r[0].startswith('r')]
print('L290 15 uniform random arms: Spearman(E, syn-sum) %+.3f | with e14 %d, without %d' % (
    spear(np.array([r[2] for r in rnd]), np.array([r[3] for r in rnd]),
          np.array([1.0 if r[4] else 0.0 for r in rnd]).sum()), sum(1 for r in rnd if not r[4])))
print('in-band L290 uniform arms by size:', {n: [r[0] for r in rnd if r[1] == n and r[6]] for n in (11, 30, 46)})
se = R['descriptive']['single_effects']
sj = np.array([se[f'e{j}'] / F for j in range(69)])
ws = np.array([syn[j] for j in range(69)], float)
print('SINGLE edges (69): Spearman(E_single, raw syn) %+.3f | clearing 2F: %s' % (
    spear(sj, ws), [(j, int(ws[j]), round(float(sj[j]), 2), 'e14' if j == 14 else '') for j in range(69) if abs(sj[j]) > 2]))
for lo, hi in ((4, 6), (7, 9), (10, 19), (20, 1000)):
    m = (ws >= lo) & (ws <= hi)
    print('  syn %d-%d: n %2d  mean single E %+.2f F  sd %.2f' % (lo, hi, int(m.sum()), sj[m].mean(), sj[m].std()))
