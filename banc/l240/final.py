# Run from banc/ after the three L240 workers. Re-read persisted raw arrays, not simulator memory.
# Stage A1 (PREREG d6c73be3...): FLOOR CHECK, CROSS-SPLIT STABILITY, ADDITIVITY on the 11 realised abs entries.
from pathlib import Path
import json, os, re, hashlib, numpy as np
out = Path('l240')
read = lambda n: json.loads((out / n).read_text())
psha = hashlib.sha256((out / 'PREREG.md').read_bytes()).hexdigest()
assert psha == (out / 'PREREG.sha256').read_text().split()[0], 'PREREG sha mismatch'
EJ = [4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67]
SING = [f'e{j}' for j in EJ]
PLAN = {0: SING[:5], 1: SING[5:10], 2: ['e67', 'g11', 'g11f', 'nf']}
ALL = ['cutwA'] + SING + ['g11', 'g11f', 'nf']
CTR = [1110, 75494, 559, 74914]
armsj, done, anch, Z, X = {}, {}, {}, {}, {}
trace_count = 0
for w in range(3):
    armsj[w], done[w] = read(f'arms_w{w}.json'), read(f'done_w{w}.json')
    anch[w] = read(f'anchors_w{w}.json')
    assert done[w]['arms'] == ['cutwA'] + PLAN[w], (w, done[w]['arms'])
    assert done[w]['seeds'] == [801, 901, 3545] + list(range(3769, 3785)), done[w]['seeds']
    assert done[w]['prereg_sha256'] == psha == armsj[w]['prereg'], 'PREREG sha'
    assert done[w]['ctr_cells'] == CTR, done[w]['ctr_cells']
    assert anch[w]['c0a135_pass'] and anch[w]['c0a175_pass'], 'anchors'
    assert anch[w]['c0a135_max'] == 0.0 and anch[w]['c0a175_max'] == 0.0, 'anchors max'
    # the lineage anchors cover the base graph only (sc25 is not an L240 arm): 46 checks vs raw_l135 + 25 vs stored L175 raws
    assert anch[w]['c0a135_checks'] == 46 and anch[w]['c0a175_checks'] == 25, 'anchor coverage'
    assert anch[w]['c0a135_pairs'] == [['cutwA', 'cutwA']] and anch[w]['c0a175_arms'] == ['cutwA'], 'anchor arms'
    assert done[w]['gain']['cutwA'] == 0.14365819573402408, 'stored base gain'
    assert all(a in done[w]['gain'] for a in PLAN[w]), 'gain table'
    Z[w], X[w] = np.load(out / f'raw_w{w}.npz'), np.load(out / f'xm_w{w}.npz')
    for k in Z[w].files:
        kk = k[:-4] if k.endswith('.npy') else k   # NpzFile.files carries no suffix
        _pp = kk.split('_')
        if kk.startswith('c') and len(_pp) == 3 and _pp[0][1:].isdigit() and _pp[2].isdigit():
            x = Z[w][k]
            assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), k
            trace_count += 1
seeds = list(range(3769, 3785))
assert armsj[0]['seeds'] == armsj[1]['seeds'] == armsj[2]['seeds'] == seeds
W_OF = {a: next(w for w in range(3) if a in done[w]['arms']) for a in ALL}
for a in SING + ['g11', 'g11f', 'nf']:
    for s in seeds:
        for g in CTR:
            assert f'c{g}_{a}_{s}' in Z[W_OF[a]].files, (a, s, g)
        assert f'xmean_{a}_{s}' in X[W_OF[a]].files, (a, s)
pools = read('pools_w0.json')
assert pools['pools'] == read('pools_w1.json')['pools'] == read('pools_w2.json')['pools'], 'pool index sets differ across workers'
PK = sorted(pools['pools'])
U = sorted(set(sum(pools['pools'].values(), [])))
xm = lambda w, a, s: X[w][f'xmean_{a}_{s}'].astype(np.float64)
ident = bool(all(np.array_equal(xm(0, 'cutwA', s), xm(w, 'cutwA', s)) for w in (1, 2) for s in seeds))
BASE = {w: np.array([xm(w, 'cutwA', s)[U].mean() for s in seeds]) for w in range(3)}
PPBASE = {w: np.array([[xm(w, 'cutwA', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) for w in range(3)}
P = {a: np.array([xm(W_OF[a], a, s)[U].mean() for s in seeds]) for a in ALL}
PP = {a: np.array([[xm(W_OF[a], a, s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) for a in ALL}
D = {a: P[a] - BASE[W_OF[a]] for a in ALL if a != 'cutwA'}


def midrank(x):
    x = np.asarray(x, float); n = len(x); o = np.argsort(x, kind='mergesort'); r = np.empty(n); i = 0
    while i < n:
        j = i
        while j + 1 < n and x[o[j + 1]] == x[o[i]]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(a, b):
    ra = midrank(a) - midrank(a).mean(); rb = midrank(b) - midrank(b).mean()
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / den) if den > 0 else float('nan')


def perm_p(a, b, B=100000, seed=24011):
    ra = midrank(a); ra = ra - ra.mean(); rb = midrank(b); rb = rb - rb.mean()
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum()); obs = float((ra * rb).sum())
    rng = np.random.Generator(np.random.PCG64(seed))
    null = (ra[None, :] * rb[np.argsort(rng.random((B, len(a))), axis=1)]).sum(1)
    return dict(rho=obs / den, p_one_sided=float((1 + (null >= obs).sum()) / (B + 1)), B=B)


# ---------------- FLOOR CHECK ----------------
n = P['nf'] - BASE[2]
F = float(n.std(ddof=1) / 4)
tab = {}
for a in D:
    d = D[a]; m = float(d.mean()); sd = float(d.std(ddof=1)); half = 2.131449546 * sd / 4
    tab[a] = dict(mean=m, sd=sd, CI=[m - half, m + half], k_neg=int((d < 0).sum()), per_seed=d.tolist())
clear = {f'e{j}': bool(abs(tab[f'e{j}']['mean']) > 2 * F) for j in EJ}
FLOOR11 = int(sum(clear.values()))
sat = {f'e{j}': float(np.median(np.abs(D[f'e{j}'])) / np.median(np.abs(n))) for j in EJ}

# ---------------- CROSS-SPLIT STABILITY ----------------
A1 = [float(D[f'e{j}'][:8].mean()) for j in EJ]; A2 = [float(D[f'e{j}'][8:].mean()) for j in EJ]
sp = perm_p(A1, A2)
sign_agree = int(sum(np.sign(A1[i]) == np.sign(A2[i]) for i in range(11)))

# ---------------- ADDITIVITY (PREREG section 5 leg 3: first-match branch, signed R) ----------------
G = float(D['g11'].mean()); Gf = float(D['g11f'].mean())
m = {a: tab[a]['mean'] for a in SING}
S = float(sum(m[a] for a in SING))
R = float(G / S) if S != 0 else float('inf')
sg, ss = float(np.sign(G)), float(np.sign(S))
if abs(G) <= 2 * F:
    branch = 'ADD_INERT_GROUP'
elif abs(S) <= 2 * F:
    branch = 'ADD_SUM_AT_FLOOR'
elif sg != ss:
    branch = 'ADD_SIGN_DISCORDANT'
elif R < 0.5:
    branch = 'ADD_SUB'
elif R <= 2.0:
    branch = 'ADD_CONCORDANT'
else:
    branch = 'ADD_SUPER'
disagree = [a for a in SING if np.sign(m[a]) != sg]
LOO = {a: dict(looin=float(G - (S - m[a])), sign_looin=float(np.sign(G - (S - m[a]))), sign_edge=float(np.sign(m[a])),
               disagree=bool(np.sign(G - (S - m[a])) != np.sign(m[a]))) for a in SING}
loo_disagree = [a for a in SING if LOO[a]['disagree']]
per_seed_S = np.sum([D[a] for a in SING], axis=0)
per_seed_rho = spearman(D['g11'], per_seed_S)
ci = lambda x: [float(x.mean() - 2.131449546 * x.std(ddof=1) / 4), float(x.mean() + 2.131449546 * x.std(ddof=1) / 4)]

# ---------------- companion (descriptive): per-pool mean-effect vector norms ----------------
Nv = {a: (PP[a] - PPBASE[W_OF[a]]).mean(0) for a in D}
Nn = {a: float(np.linalg.norm(v)) for a, v in Nv.items()}
Fp = (PP['nf'] - PPBASE[2]).std(0, ddof=1) / 4
floorN = float(np.sqrt((Fp ** 2).sum()))
clearN = {f'e{j}': bool(Nn[f'e{j}'] > 2 * floorN) for j in EJ}
base_frac = {a: float(np.abs((PP[a] - PPBASE[W_OF[a]])).sum(1).mean() / np.abs(PP[a]).sum(1).mean()) for a in D}

# ---------------- lineage certificate: e67 IS L190's E-edge graph ----------------
g190 = json.load(open('l190/gains_w0.json'))['gain']
assert done[2]['gain']['e67'] == g190['E-edge'], 'e67 gain != stored L190 E-edge gain'
s190 = json.load(open('l190/selection.json'))
lineage_e67 = dict(bisected_gain=done[2]['gain']['e67'], equals_L190_E_edge_gain=True, L190_E_edge=g190['E-edge'])

# ---------------- predictions ----------------
pred = {1: bool(FLOOR11 <= 3), 2: bool(sp['rho'] < 0.40), 3: bool(sg == ss and R < 1),
        4: bool(max(EJ, key=lambda j: abs(tab[f'e{j}']['mean'])) == 67), 5: bool(np.sign(G) == np.sign(Gf))}
score = int(sum(pred.values()))

# ---------------- af / gains ----------------
gains = {a: done[W_OF[a]]['gain'][a] for a in ALL}
af = {a: [float(np.min(np.atleast_1d(Z[W_OF[a]][f'af_{a}_{s}']))), float(np.max(np.atleast_1d(Z[W_OF[a]][f'af_{a}_{s}'])))] for a in ALL}

# ---------------- descriptive duty (L190 idiom) ----------------
duty = None
try:
    v = Path('l187/verdict_l187.py').read_text().splitlines(True); m = {}
    exec(''.join(v[:71] + v[117:125]), m)
    duty = {}
    for a in ALL:
        w = W_OF[a]
        duty[a] = dict(Ti_R=float(np.mean([m['duty_seeds'](Z[w], a, [s], 'Ti')[1][0] for s in seeds])),
                       Ti_L=float(np.mean([m['duty_seeds'](Z[w], a, [s], 'Ti')[0][0] for s in seeds])),
                       mid14=float(np.mean([m['duty14_seeds'](Z[w], a, [s])[0] for s in seeds])))
except Exception as e:  # descriptive only; never hides a primary number
    duty = dict(error=repr(e))

enc = lambda o: o.item() if hasattr(o, 'item') else str(o)
res = dict(
    card='L240 stage A1', status='FINAL', prereg_sha256=psha, seeds=seeds, halves=dict(H1=seeds[:8], H2=seeds[8:]),
    workers={w: dict(arms=done[w]['arms'], secs=done[w]['secs']) for w in range(3)},
    anchors={w: dict(c0a135_pass=anch[w]['c0a135_pass'], c0a175_pass=anch[w]['c0a175_pass'],
                     c0a135_max=anch[w]['c0a135_max'], c0a175_max=anch[w]['c0a175_max']) for w in range(3)},
    trace_arrays_verified=trace_count, cutwA_identical_across_workers=ident,
    menu_n=armsj[0]['menu_n'], base_edges={w: armsj[w]['base_edges'] for w in range(3)}, lineage_e67=lineage_e67,
    edges={a: armsj[W_OF[a]]['edges'][a] for a in SING + ['g11']},
    readout=dict(pool_cells=len(U), n_pools=len(PK), pool_sizes={pk: len(pools['pools'][pk]) for pk in PK},
                 base_mean=float(P['cutwA'].mean()), per_seed_base=P['cutwA'].tolist()),
    gains=gains, af_range=af, effects=tab, noise_twin=dict(per_seed=n.tolist(), sd=float(n.std(ddof=1)), F=F),
    floor=dict(F=F, twoF=2 * F, clears=clear, FLOOR11=FLOOR11, chance_expectation=0.55, P1_le3=bool(FLOOR11 <= 3), sat=sat,
               note='A1 reports on the 11 abs entries, non-branching; the 69-edge gate (>= 14 clear) is read at A2'),
    split=dict(H1=A1, H2=A2, rho11=sp['rho'], p11=sp['p_one_sided'], B=sp['B'], sign_agree=sign_agree, P2_rho_lt_0p40=bool(sp['rho'] < 0.40),
               note='A1 reports on the 11 abs entries, non-branching; the 69-edge gate (rho >= .40 and p <= .001) is read at A2'),
    additivity=dict(G=G, G_f=Gf, S=S, R=R, sign_G=sg, sign_S=ss, branch=branch, G_CI=ci(D['g11']), Gf_CI=ci(D['g11f']),
                    twoF=2 * F, sign_disagree=disagree, leave_one_in=LOO, looin_disagree=loo_disagree,
                    gain_twin_concordant=bool(np.sign(G) == np.sign(Gf)), per_seed_rho_G_vs_S=per_seed_rho),
    companion=dict(note='descriptive; threshold chosen in analysis, not registered', N=Nn, floorN=floorN, clears=clearN,
                   vectors={a: Nv[a].tolist() for a in D}, abs_L1_change_over_base=base_frac),
    predictions=pred, score=score, duty_descriptive=duty)
tmp = out / 'results_l240.json.tmp'
tmp.write_text(json.dumps(res, indent=1, default=enc))
os.replace(tmp, out / 'results_l240.json')
print('ident', ident, 'traces', trace_count, 'menu', armsj[0]['menu_n'], 'pool cells', len(U), 'base', round(float(P['cutwA'].mean()), 6))
print('F', round(F, 8), 'FLOOR11', FLOOR11, clear)
print('means', {a: round(tab[a]['mean'], 7) for a in tab})
print('k_neg', {a: tab[a]['k_neg'] for a in tab})
print('rho11', round(sp['rho'], 4), 'p11', round(sp['p_one_sided'], 4), 'sign_agree', sign_agree)
print('ADD', branch, 'G', G, 'Gf', Gf, 'S', S, 'R', R, 'disagree', disagree)
print('N', {a: round(Nn[a], 8) for a in Nn}, 'floorN', floorN, clearN)
print('pred', pred, 'score', score)
print('af', af)
print('duty', duty)
