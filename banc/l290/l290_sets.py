# Run from banc/ AFTER l290/PREREG.md is frozen:  python l290/l290_sets.py
# Materialises the L290 PREREG s3 sets from the stored 69-edge menu (L240 A1/A2 arms
# files) into l290/sets.json + sets.sha256. The harness re-derives every set from its
# own live menu and asserts equality before any bisect (build_l290.py, L290 ARMS BLOCK).
from pathlib import Path
import hashlib, json, os
import numpy as np

out = Path('l290')
psha = hashlib.sha256((out / 'PREREG.md').read_bytes()).hexdigest()
assert psha == (out / 'PREREG.sha256').read_text().split()[0], 'PREREG sha mismatch'
assert not (out / 'sets.json').exists(), 'sets.json exists (never re-materialise; amend instead)'
N0 = {1, 2, 8, 9, 16, 21, 47, 55}

# ---- the stored 69-edge menu: position j -> (target, raw syn) ----
menu = {}
for p in sorted(Path('l240').glob('arms_w*.json')):
    a = json.loads(p.read_text())
    for name, e in a['edges'].items():
        if name[0] == 'e' and name[1:].isdigit():
            r = e['removed'][0]
            j = int(name[1:])
            assert j not in menu and r['csr_index'] >= 0, (name, p)
            menu[j] = dict(j=j, target=int(r['target']), syn=int(r['syn']),
                           effective_weight=float(r['effective_weight']), sign=float(r['sign']))
assert sorted(menu) == list(range(69)), (len(menu), 'stored menu is not 0..68')
assert len({m['target'] for m in menu.values()}) == 69, 'menu targets not distinct'
S221 = json.load(open('l221/static.json'))
tb = S221['Q221_b_target_reach']['used_edge_table']
assert all(menu[int(r['edge_j'])]['target'] == int(r['target_gid']) for r in tb), 'stored L221 pairs'
EJ = [int(r['edge_j']) for r in tb]
syn = [menu[j]['syn'] for j in range(69)]

# ---- used-sets (L221 stored) ----
pm = S221['L221_primary']['per_metric']
used = {m: sorted(int(j) for j in pm[m]['feasible_edges']) for m in ('abs', 'crofts', 'hop')}
assert [len(used[m]) for m in used] == [11, 30, 46], used
assert used['abs'] == EJ
assert len(set(used['abs']) & set(used['crofts'])) == 10
assert set(used['crofts']) < set(used['hop']) and set(used['abs']) < set(used['hop'])
assert all(14 in used[m] for m in used)

# ---- raw comparators: n heaviest by raw synapse count, ties by ascending j ----
raw, ties = {}, {}
order = sorted(range(69), key=lambda j: (-syn[j], j))
for n in (11, 30, 46):
    raw[n] = sorted(order[:n])
    ties[n] = int(sum(1 for j in order[n:] if syn[j] == syn[order[n - 1]]))

# ---- random subsets: PCG64(29013), draw order (11,30,46) x k=1..5 ----
rng = np.random.Generator(np.random.PCG64(29013))
rand, rand_order = {}, {}
for n in (11, 30, 46):
    for k in range(1, 6):
        d = [int(j) for j in rng.choice(69, size=n, replace=False)]
        assert len(set(d)) == n
        rand_order[f'r{n}k{k}'] = d
        rand[f'r{n}k{k}'] = sorted(d)

sets = {}
for m, a in (('crofts', 'gc30'), ('hop', 'gh46')):
    sets[a] = used[m]
for n in (11, 30, 46):
    sets[f'rw{n}'] = raw[n]
sets.update(rand)
assert len(sets) == 20, (len(sets), 'gc30, gh46, 3 raw comparators, 15 random subsets')

# SAME-SET rule (PREREG s3): a comparator equal to its used-set is the SAME arm
same = [(m, x) for m in ('abs', 'crofts', 'hop')
        for x in (f'rw{len(used[m])}',) + tuple(f'r{len(used[m])}k{k}' for k in range(1, 6)) if sets[x] == used[m]]
res = dict(card='L290 sets', rule='L290 PREREG s3', prereg_sha256=psha,
           numpy=np.__version__, menu=[menu[j] for j in range(69)], used=used,
           raw={str(n): raw[n] for n in raw}, raw_boundary_ties_left_out={str(n): ties[n] for n in ties},
           random=rand, random_draw_order=rand_order, same_set_pairs=same, noop=sorted(N0),
           contains14={a: (14 in s) for a, s in sets.items()},
           eff={a: len([j for j in s if j not in N0]) for a, s in sets.items()})
tmp = out / 'sets.json.tmp'
tmp.write_text(json.dumps(res, indent=1))
os.replace(tmp, out / 'sets.json')
ssha = hashlib.sha256((out / 'sets.json').read_bytes()).hexdigest()
(out / 'sets.sha256').write_text(f'{ssha}  sets.json\n')
os.chmod(out / 'sets.json', 0o444); os.chmod(out / 'sets.sha256', 0o444)

# ---- report (predictions S1/S2/N1 of PREREG s6 are scored from THIS materialisation) ----
print('sets.json sha256', ssha, '| numpy', np.__version__)
print('USED sizes', {m: len(v) for m, v in used.items()}, '| abs^crofts', len(set(used['abs']) & set(used['crofts'])),
      '| abs-crofts', sorted(set(used['abs']) - set(used['crofts'])), 'crofts-abs', sorted(set(used['crofts']) - set(used['abs'])),
      '| hop-crofts', len(set(used['hop']) - set(used['crofts'])))
print('RAW ties left out at the boundary', ties)
for n in (11, 30, 46):
    print(f'RW_{n}: syn range {syn[order[n - 1]]}..{syn[order[0]]} | has14', 14 in raw[n],
          '| overlap with U', {m: len(set(raw[n]) & set(used[m])) for m in used})
print('S1 |RW11 ^ U_abs| =', len(set(raw[11]) & set(used['abs'])), '-> TRUE' if 7 <= len(set(raw[11]) & set(used['abs'])) <= 10 else '-> FALSE')
print('S2 14 in RW11 =', 14 in raw[11], '-> TRUE' if 14 in raw[11] else '-> FALSE')
for m in used:
    k = len(set(used[m]) & N0)
    print(f'U_{m}: n {len(used[m])} eff {len(used[m]) - k} no-ops {sorted(set(used[m]) & N0)}')
n_c, n_h = len(set(used['crofts']) & N0), len(set(used['hop']) & N0)
print('N1 crofts in 2-4:', 2 <= n_c <= 4, '| hop in 4-6:', 4 <= n_h <= 6)
print('SAME-SET pairs (VACUOUS BY IDENTITY):', same)
for a in sorted(sets, key=lambda a: (len(sets[a]), a)):
    print(f'  {a:7s} n {len(sets[a]):2d} eff {res["eff"][a]:2d} has14 {int(res["contains14"][a])} syn-sum {sum(syn[j] for j in sets[a]):6d}')
