#!/usr/bin/env python3
"""L168: pool the scramble-control family from STORED results jsons only.

Zero rollouts. CERT block (PREREG CERT-1..4) must pass before any new number
is read. Writes banc/l168/static.json at full precision.
"""
import json, math, pathlib

B = pathlib.Path.home() / 'critters/peabrain-lab/banc'
Z = 1.959963984540054


def wilson(k, n):
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt((p * (1 - p) + Z * Z / (4 * n)) / n) / d
    return c - h, c + h


R = {d: json.loads((B / d / f'results_{d}.json').read_text())
     for d in ('l125', 'l127', 'l128')}
# batch identity derived from the stored pooled k_b* keys, never log prose
BATCH = {'l125': 'b20', 'l127': 'b22', 'l128': 'b23'}
pscr = R['l128']['pooled_scr']
assert sorted(k for k in pscr['cutscr0'] if k.startswith('k_b')) == \
    ['k_b20', 'k_b22', 'k_b23'], 'cutscr0 batch union drift'
assert sorted(k for k in pscr['cutscr1'] if k.startswith('k_b')) == \
    ['k_b20', 'k_b23'], 'cutscr1 batch union drift'
assert sorted(k for k in R['l127']['pooled_scr0'] if k.startswith('k_b')) == \
    ['k_b20', 'k_b22'], 'scr0 2-batch prefix drift'

ARMS = {  # arm -> files that ran it (order = batch order)
    'cutscr0': ['l125', 'l127', 'l128'],
    'cutscr1': ['l125', 'l128'],
    'cutscr2': ['l125', 'l128'],
    'cutscr3': ['l125', 'l128'],
    'cutcl40': ['l127'],
    'cutscrL1': ['l127'],
    'cutscrL2': ['l127'],
}

# ---- CERT-1: stored per-batch Wilson bounds are n=16 Wilson on stored k ----
n_cert1 = 0
for arm, files in ARMS.items():
    for f in files:
        c = R[f]['table']['Ti'][arm]
        for side in ('L', 'R'):
            lb, ub = wilson(c['k' + side], 16)
            assert abs(lb - c['lb' + side]) < 1e-9 and \
                   abs(ub - c['ub' + side]) < 1e-9, (arm, f, side)
            n_cert1 += 1
print(f'CERT-1 PASS: {n_cert1} stored side-bounds == n=16 Wilson on stored k '
      f'(<1e-9)')

# ---- pool (right side = the claim axis; left side folded for claim (d)) ----
POOL = {}
for arm, files in ARMS.items():
    kR = sum(R[f]['table']['Ti'][arm]['kR'] for f in files)
    kL = sum(R[f]['table']['Ti'][arm]['kL'] for f in files)
    n = 16 * len(files)
    lbR, ubR = wilson(kR, n)
    lbL, ubL = wilson(kL, n)
    POOL[arm] = dict(
        n=n, n_batches=len(files), batches=[BATCH[f] for f in files],
        kR=kR, p_hatR=kR / n, lbR=lbR, ubR=ubR,
        kL=kL, p_hatL=kL / n, lbL=lbL, ubL=ubL,
        kR_by_batch={BATCH[f]: R[f]['table']['Ti'][arm]['kR'] for f in files},
        kL_by_batch={BATCH[f]: R[f]['table']['Ti'][arm]['kL'] for f in files},
        meanR_by_batch={BATCH[f]: R[f]['table']['Ti'][arm]['meanR']
                        for f in files},
        meanL_by_batch={BATCH[f]: R[f]['table']['Ti'][arm]['meanL']
                        for f in files},
    )

# ---- CERT-2: our pool == stored l128 pooled_scr rows ----
n_cert2 = 0
for arm in ('cutscr0', 'cutscr1', 'cutscr2', 'cutscr3'):
    st, ours = pscr[arm], POOL[arm]
    nk = [k for k in st if k.startswith('k') and not k.startswith('k_b')]
    assert len(nk) == 1, (arm, nk)
    assert int(nk[0][1:]) == ours['n'], (arm, nk, ours['n'])
    assert st[nk[0]] == ours['kR'], (arm, st[nk[0]], ours['kR'])
    assert abs(st['p_hat'] - ours['p_hatR']) < 1e-12, arm
    assert abs(st['lb'] - ours['lbR']) < 1e-12 and \
           abs(st['ub'] - ours['ubR']) < 1e-12, arm
    for bk, v in ((k, v) for k, v in st.items() if k.startswith('k_b')):
        assert ours['kR_by_batch'][bk[2:]] == v, (arm, bk)
    n_cert2 += 1
print(f'CERT-2 PASS: {n_cert2} pooled rows reproduce stored l128 pooled_scr '
      f'(k, p_hat, lb, ub <1e-12 + per-batch decomposition)')

# ---- CERT-3: l127 pooled_scr0 == 2-batch prefix of our cutscr0 pool ----
p0 = R['l127']['pooled_scr0']
k2 = POOL['cutscr0']['kR_by_batch']['b20'] + POOL['cutscr0']['kR_by_batch']['b22']
lb2, ub2 = wilson(k2, 32)
assert p0['k32'] == k2 and abs(p0['lb'] - lb2) < 1e-12 and \
       abs(p0['ub'] - ub2) < 1e-12, 'CERT-3'
print(f'CERT-3 PASS: stored 2-batch scr0 pool {k2}/32 == our 3-batch prefix')

# ---- CERT-4: masses agree across files ----
assert R['l125']['mass_scr'] == R['l128']['mass_scr'], 'mass_scr drift l125/l128'
assert R['l125']['extra_mass_scr'] == R['l128']['extra_mass_scr'], 'extra drift'
assert R['l125']['mass']['cutng29'] == R['l127']['mass']['cutng29'] == \
       R['l128']['mass']['cutng29'], 'window mass drift'
MASS = dict(R['l125']['mass_scr'])
MASS.update({k: v for k, v in R['l127']['mass_scr'].items() if k not in MASS})
EXTRA = dict(R['l125']['extra_mass_scr'])
EXTRA.update({k: v for k, v in R['l127']['extra_mass_scr'].items()
              if k not in EXTRA})
W29 = R['l125']['mass']['cutng29']
assert set(MASS) == set(ARMS), (sorted(MASS), sorted(ARMS))
print(f'CERT-4 PASS: masses consistent across files; k29 window mass {W29}')

# ---- verdict (decision rule D1/D2/D3) ----
scr0 = POOL['cutscr0']
d1 = scr0['lbR'] > .5
supers = [a for a in ARMS if POOL[a]['lbR'] > .5]
kills = [a for a in ARMS if POOL[a]['ubR'] < .5]
heterogeneous = bool(supers) and bool(kills)
rule = 'D3' if (d1 and heterogeneous) else ('D1' if d1 else 'D2')
both_sides_up = scr0['lbR'] > .5 and scr0['p_hatL'] > R['l128']['table']['Ti'][
    'full']['meanL']  # placeholder guard, real both-sides read below
base_kR = {f: R[f]['table']['Ti']['full']['kR'] for f in ARMS['cutscr0']}
base_kL = {f: R[f]['table']['Ti']['full']['kL'] for f in ARMS['cutscr0']}
baseR, baseL = sum(base_kR.values()), sum(base_kL.values())
lbR_b, ubR_b = wilson(baseR, 48)
lbL_b, ubL_b = wilson(baseL, 48)

OUT = dict(
    card='L168', generated='static re-derivation, zero rollouts',
    sources={d: f'{d}/results_{d}.json:table.Ti' for d in R},
    batches=BATCH, pool=POOL, mass=MASS, extra_mass=EXTRA,
    window_mass_k29=W29,
    mass_gap_scr0_vs_k29=round(W29 - MASS['cutscr0'], 6),
    base_full_48=dict(kR=baseR, kL=baseL, n=48, lbR=lbR_b, ubR=ubR_b,
                      lbL=lbL_b, ubL=ubL_b,
                      kR_by_file=base_kR, kL_by_file=base_kL),
    verdict=dict(rule=rule, scr0_super_right=d1,
                 supers=sorted(supers), kills=sorted(kills),
                 heterogeneous=heterogeneous,
                 scr0_both_sides_above_base=bool(
                     scr0['lbR'] > ubR_b and scr0['lbL'] > ubL_b)),
)
(B / 'l168/static.json').write_text(json.dumps(OUT, indent=1))

print()
print(f'{"arm":9} {"mass":7} {"extra":7} {"nb":>2} {"kR/n":>7} '
      f'{"WilsonR":>16} {"kL/n":>7} {"WilsonL":>16}')
for a in ('cutscr0', 'cutscr1', 'cutscr2', 'cutscr3', 'cutcl40',
          'cutscrL1', 'cutscrL2'):
    c = POOL[a]
    print(f'{a:9} {MASS[a]:<7} {EXTRA[a]:<7} {c["n_batches"]:>2} '
          f'{c["kR"]:>3}/{c["n"]:<3} [{c["lbR"]:.3f},{c["ubR"]:.3f}]  '
          f'{c["kL"]:>3}/{c["n"]:<3} [{c["lbL"]:.3f},{c["ubL"]:.3f}]')
print(f'{"full(base)":9} {"-":7} {"-":7} {3:>2} {baseR:>3}/48  '
      f'[{lbR_b:.3f},{ubR_b:.3f}]  {baseL:>3}/48  [{lbL_b:.3f},{ubL_b:.3f}]')
print()
print(f'VERDICT: rule {rule}; scr0 super-right {d1}; supers {sorted(supers)}; '
      f'kills {sorted(kills)}; heterogeneous {heterogeneous}; '
      f'scr0 both sides above base band '
      f'{OUT["verdict"]["scr0_both_sides_above_base"]}')
print(f'mass: scr0 {MASS["cutscr0"]} vs k29 window {W29} '
      f'(gap {OUT["mass_gap_scr0_vs_k29"]})')
