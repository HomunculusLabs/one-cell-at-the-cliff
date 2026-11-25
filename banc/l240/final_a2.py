# Run from banc/ after the L240 A2 workers (tick 275+). Stage A2 under the A1 PREREG
# (d6c73be3...) + A2_ADDENDUM (0c55e34d...). Re-reads persisted raw arrays only.
# MODE is derived from the artefacts, never chosen by hand: all seven A2 exit files
# present -> FINAL (the 69-edge FLOOR and SPLIT gates -> I_INSTRUMENT or the metric
# comparison; the declared vector companion; predictions Q1-Q5). Fewer -> PARTIAL:
# verification ONLY, no effect is computed (the gates are registered on the 69).
from pathlib import Path
import json, os, hashlib, numpy as np
out = Path('l240')
read = lambda n: json.loads((out / n).read_text())
sha = lambda n: hashlib.sha256((out / n).read_bytes()).hexdigest()
psha, asha = sha('PREREG.md'), sha('A2_ADDENDUM.md')
assert psha == (out / 'PREREG.sha256').read_text().split()[0], 'PREREG sha mismatch'
assert asha == (out / 'A2_ADDENDUM.sha256').read_text().split()[0], 'ADDENDUM sha mismatch'
EJ = [4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67]
NEWJ = [j for j in range(69) if j not in EJ]
assert len(NEWJ) == 58
SIZE = [9, 9, 8, 8, 8, 8, 8]
PLAN, _k = {}, 0
for _i, _n in enumerate(SIZE):
    PLAN[3 + _i] = NEWJ[_k:_k + _n]
    _k += _n
assert _k == 58
A1PLAN = {0: EJ[:5], 1: EJ[5:10], 2: [67]}
A1W, A2W_ALL = (0, 1, 2), (3, 4, 5, 6, 7, 8, 9)
def _exit(w):
    p = out / f'exit_a2_w{w}'
    return p.read_text().strip() if p.exists() else None
EXIT = {w: _exit(w) for w in A2W_ALL}
A2W = tuple(w for w in A2W_ALL if EXIT[w] is not None)
assert all(EXIT[w] == '0' for w in A2W), ('a finished A2 worker exited non-zero', EXIT)
FINAL = len(A2W) == 7
# raw_w*.npz is rewritten after EVERY seed while a worker runs, so "the npz exists" is not
# "the worker finished": only an exit file (written by launch_a2.sh after the python exits)
# admits a worker, and a non-zero exit code halts here.
assert all(EXIT[w] is None or EXIT[w] == '0' for w in A2W_ALL), ('an A2 worker exited non-zero', EXIT)
ALLJ = EJ + NEWJ
seeds = list(range(3769, 3785))
ANCH = [801, 901, 3545]
CTR = [1110, 75494, 559, 74914]
STORED_G = 0.14365819573402408
armsj, done, anch, Z, X = {}, {}, {}, {}, {}
trace_count = 0
pool_count = 0
for w in A1W + A2W:
    armsj[w], done[w] = read(f'arms_w{w}.json'), read(f'done_w{w}.json')
    anch[w] = read(f'anchors_w{w}.json')
    assert done[w]['seeds'] == ANCH + seeds, (w, done[w]['seeds'])
    assert done[w]['prereg_sha256'] == psha == armsj[w]['prereg'], (w, 'PREREG sha')
    assert done[w]['ctr_cells'] == CTR, (w, 'ctr cells')
    assert anch[w]['c0a135_pass'] and anch[w]['c0a175_pass'], (w, 'anchors')
    assert anch[w]['c0a135_max'] == 0.0 and anch[w]['c0a175_max'] == 0.0, (w, 'anchors max')
    assert anch[w]['c0a135_checks'] == 46 and anch[w]['c0a175_checks'] == 25, (w, 'anchor coverage')
    assert anch[w]['c0a135_pairs'] == [['cutwA', 'cutwA']] and anch[w]['c0a175_arms'] == ['cutwA'], (w, 'anchor arms')
    assert anch[w]['g_cutwA_stored_exact'] and anch[w]['g_cutwA'] == STORED_G, (w, 'stored base gain')
    assert done[w]['gain']['cutwA'] == STORED_G, (w, 'stored base gain')
    assert armsj[w]['seeds'] == seeds, (w, 'seeds')
    Z[w], X[w] = np.load(out / f'raw_w{w}.npz'), np.load(out / f'xm_w{w}.npz')
    for k in Z[w].files:
        _pp = k.split('_')
        if len(_pp) == 3 and _pp[0][1:].isdigit() and _pp[2].isdigit():
            x = Z[w][k]
            assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k)
            trace_count += 1
        elif len(_pp) == 4 and _pp[0] in ('Ti', 'Tr', 'Ta', 'Sr', 'Pr'):
            # the 20 POOL traces (<Class>_<pool>_<arm>_<seed>) = the readout itself
            x = Z[w][k]
            assert x.shape == (6000,) and x.dtype == np.float32 and np.isfinite(x).all(), (w, k)
            pool_count += 1
for w in A1W:
    assert done[w]['arms'] == ['cutwA'] + [f'e{j}' for j in A1PLAN[w]] + ([] if w < 2 else ['g11', 'g11f', 'nf']), (w, 'A1 arms')
UNM = set()
for w in A2W:
    assert armsj[w]['stage'] == 'A2' and armsj[w]['addendum'] == asha, (w, 'addendum sha')
    assert armsj[w]['cert_menu_11'] == 11 and armsj[w]['menu69_n'] == 69, (w, 'CERT-MENU-A2')
    assert armsj[w]['menu_n'] == 80 and armsj[w]['base_edges'] == 644177, (w, 'menu / base edges')
    UNM |= {int(u['edge_j']) for u in armsj[w]['unmeasurable']}
    built = [int(a[1:]) for a in armsj[w]['arms_built']]
    assert built == [j for j in PLAN[w] if j not in UNM], (w, built, 'arms built != plan')
    assert done[w]['arms'] == ['cutwA'] + armsj[w]['arms_built'], (w, 'done arms')
    assert done[w]['secs'] < 1700, (w, 'hard stop', done[w]['secs'])
    assert all(.12 <= done[w]['gain'][a] <= .18 for a in ['cutwA'] + armsj[w]['arms_built']), (w, 'gain window')
ALLA2 = [f'e{j}' for w in A2W for j in [int(a[1:]) for a in armsj[w]['arms_built']]]
assert len(set(ALLA2)) == len(ALLA2) and set(ALLA2) <= {f'e{j}' for j in NEWJ}, 'A2 arm set'
assert len(ALLA2) + len(UNM) == sum(len(PLAN[w]) for w in A2W), 'arms built + unmeasurable != plan'
W_OF = {f'e{j}': next(w for w in A1W + A2W if f'e{j}' in done[w]['arms']) for j in ALLJ if f'e{j}' in ALLA2 or j in EJ}
for a, w in W_OF.items():
    for s in seeds:
        for g in CTR:
            assert f'c{g}_{a}_{s}' in Z[w].files, (a, s, g)
        assert f'xmean_{a}_{s}' in X[w].files and f'af_{a}_{s}' in Z[w].files, (a, s)
pools = read('pools_w0.json')
assert all(pools['pools'] == read(f'pools_w{w}.json')['pools'] for w in A1W[1:] + A2W), 'pool index sets differ'
xm = lambda w, a, s: X[w][f'xmean_{a}_{s}'].astype(np.float64)
ALLSEEDS = ANCH + seeds
raw_cut = [k for k in Z[0].files if k.startswith(tuple(f'c{g}_' for g in CTR)) and '_cutwA_' in k and int(k.rsplit('_', 1)[1]) in ALLSEEDS]
assert len(raw_cut) == 4 * 19

# ---------------- A2_ADDENDUM s3 GATE: A2's cutwA == A1's stored cutwA, exactly ----------------
ident = dict(
    xmean=bool(all(np.array_equal(xm(w, 'cutwA', s), xm(0, 'cutwA', s)) for w in A2W for s in ALLSEEDS)),
    raw=bool(all(np.array_equal(Z[w][k], Z[0][k]) for w in A2W for k in raw_cut)),
    af=bool(all(np.array_equal(np.atleast_1d(Z[w][f'af_cutwA_{s}']), np.atleast_1d(Z[0][f'af_cutwA_{s}'])) for w in A2W for s in ALLSEEDS)))
assert ident['xmean'] and ident['raw'] and ident['af'], ('VOID: A2 cutwA traces != A1 stored', ident)
enc = lambda o: o.item() if hasattr(o, 'item') else str(o)


def atomic(name, obj):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=1, default=enc))
    os.replace(tmp, out / name)


base = dict(card='L240 stage A2', prereg_sha256=psha, addendum_sha256=asha, seeds=seeds, halves=dict(H1=seeds[:8], H2=seeds[8:]),
            workers_a2={w: dict(arms=done[w]['arms'], secs=done[w]['secs']) for w in A2W}, exit_codes={w: EXIT[w] for w in A2W_ALL},
            anchors={w: dict(c0a135_pass=anch[w]['c0a135_pass'], c0a175_pass=anch[w]['c0a175_pass'],
                             c0a135_max=anch[w]['c0a135_max'], c0a175_max=anch[w]['c0a175_max']) for w in A2W},
            trace_arrays_verified=trace_count,
            pool_traces_verified=pool_count,
            cutwA_gate=dict(xmean_identical_to_A1=ident['xmean'], raw_identical_to_A1=ident['raw'], af_identical=ident['af'],
                            raw_arrays_compared=len(raw_cut) * max(1, len(A2W))),
            menu=dict(cutwA_menu_n=80, menu69_n=69, cert_menu_11=11, unmeasurable=sorted(UNM)),
            arms_built=ALLA2, n_arms_built=len(ALLA2), gains={f'e{j}': done[W_OF[f'e{j}']]['gain'][f'e{j}'] for j in
                                                               [int(a[1:]) for a in ALLA2]})
if not FINAL:
    base.update(status='PARTIAL', effects_read=False,
                note='fewer than 7 A2 workers finished: verification only, no effect computed, gates NOT read (registered on the 69)')
    atomic('results_l240_a2_partial.json', base)
    print('PARTIAL: A2 workers', A2W, 'of 7 | arms built', len(ALLA2), 'of 58 | traces', trace_count, '| cutwA gate', ident)
    print('no effect read; gates NOT read')
    raise SystemExit(0)

# ================= FINAL: all 58 new arms present =================
MEAS = [j for j in ALLJ if j not in UNM]
assert set(W_OF) == {f'e{j}' for j in MEAS}
R1 = read('results_l240.json')
PK = sorted(pools['pools'])
U = sorted(set(sum(pools['pools'].values(), [])))
BASE = np.array([xm(0, 'cutwA', s)[U].mean() for s in seeds])
PPBASE = np.array([[xm(0, 'cutwA', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds])
P = {f'e{j}': np.array([xm(W_OF[f'e{j}'], f'e{j}', s)[U].mean() for s in seeds]) for j in MEAS}
PP = {f'e{j}': np.array([[xm(W_OF[f'e{j}'], f'e{j}', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds]) for j in MEAS}
P['nf'] = np.array([xm(2, 'nf', s)[U].mean() for s in seeds])
PP['nf'] = np.array([[xm(2, 'nf', s)[pools['pools'][pk]].mean() for pk in PK] for s in seeds])
D = {f'e{j}': P[f'e{j}'] - BASE for j in MEAS}
V = {f'e{j}': PP[f'e{j}'] - PPBASE for j in MEAS}
n = P['nf'] - BASE
Vn = PP['nf'] - PPBASE
F = float(n.std(ddof=1) / 4)
assert abs(F - R1['noise_twin']['F']) <= 1e-18, ('F drift vs A1', F, R1['noise_twin']['F'])
t15 = 2.131449546


def midrank(x):
    x = np.asarray(x, float); nn = len(x); o = np.argsort(x, kind='mergesort'); r = np.empty(nn); i = 0
    while i < nn:
        j = i
        while j + 1 < nn and x[o[j + 1]] == x[o[i]]:
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


# ---------------- FLOOR (69) ----------------
mean_e = {f'e{j}': float(D[f'e{j}'].mean()) for j in MEAS}
tab = {}
for a in D:
    d = D[a]; m = float(d.mean()); half = t15 * float(d.std(ddof=1)) / 4
    tab[a] = dict(mean=m, CI=[m - half, m + half], k_neg=int((d < 0).sum()), per_seed=d.tolist())
clear = {j: (bool(abs(mean_e[f'e{j}']) > 2 * F) if j in MEAS else False) for j in ALLJ}
FLOOR69 = int(sum(clear.values()))
sat = {f'e{j}': float(np.median(np.abs(D[f'e{j}'])) / np.median(np.abs(n))) for j in MEAS}
FLOOR_PASS = bool(FLOOR69 >= 14)

# ---------------- SPLIT (69, measurable edges) ----------------
H1 = {f'e{j}': float(D[f'e{j}'][:8].mean()) for j in MEAS}
H2 = {f'e{j}': float(D[f'e{j}'][8:].mean()) for j in MEAS}
sp = perm_p([H1[f'e{j}'] for j in MEAS], [H2[f'e{j}'] for j in MEAS])
sign_agree = int(sum(bool(np.sign(H1[f'e{j}']) == np.sign(H2[f'e{j}'])) for j in MEAS))
SPLIT_PASS = bool(sp['rho'] >= 0.40 and sp['p_one_sided'] <= 0.001)
VERDICT = 'GATES_PASS' if (FLOOR_PASS and SPLIT_PASS) else 'I_INSTRUMENT'

# ---------------- metric comparison (PREREG s6; READ only if both gates pass) ----------------
S221 = json.load(open('l221/static.json'))
pm = S221['L221_primary']['per_metric']
syn = {}
for j in EJ:
    syn[j] = int(armsj[W_OF[f'e{j}']]['edges'][f'e{j}']['removed'][0]['syn'])
for j in NEWJ:
    if j in MEAS:
        syn[j] = float(armsj[W_OF[f'e{j}']]['edges'][f'e{j}']['syn_raw'])
assert len(syn) == len(MEAS)


def auc(x, used):
    x = np.asarray(x, float); used = np.asarray(used, bool)
    r = midrank(x); nu = int(used.sum()); nv = int((~used).sum())
    if nu == 0 or nv == 0:
        return float('nan')
    return float((r[used].sum() - nu * (nu + 1) / 2.0) / (nu * nv))


METRIC = dict(status='NOT READ', reason='')
if VERDICT == 'GATES_PASS':
    METRIC['status'] = 'READ'
    eff = np.array([abs(mean_e[f'e{j}']) for j in MEAS]); sy = np.array([float(syn[j]) for j in MEAS])
    rng = np.random.Generator(np.random.PCG64(24012))
    for m in ('abs', 'crofts', 'hop'):
        used = np.array([j in set(pm[m]['feasible_edges']) for j in MEAS])
        order = np.lexsort((np.arange(len(MEAS)), -sy)); top = order[:int(used.sum())]
        usedw = np.zeros(len(MEAS), bool); usedw[top] = True
        a_m, a_w = auc(eff, used), auc(eff, usedw)
        diffs = []
        for _ in range(10000):
            idx = rng.integers(0, len(MEAS), len(MEAS))
            am, aw = auc(eff[idx], used[idx]), auc(eff[idx], usedw[idx])
            if not (np.isnan(am) or np.isnan(aw)):
                diffs.append(am - aw)
        diffs = np.array(diffs)
        METRIC[m] = dict(n_used=int(used.sum()), AUC_m=a_m, AUC_w=a_w, diff=a_m - a_w, boot_n=int(len(diffs)),
                         boot_CI=[float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))])
    ds = {m: METRIC[m]['diff'] for m in ('abs', 'crofts', 'hop')}
    win = [m for m in ds if ds[m] >= 0.10 and METRIC[m]['boot_CI'][0] > 0]
    METRIC['branch'] = 'ESCAPE' if all(v <= 0.05 for v in ds.values()) else ('WINS:' + ','.join(win) if win else 'NO_DECISION')
else:
    METRIC['reason'] = f'FLOOR_PASS={FLOOR_PASS} ({FLOOR69}/69), SPLIT_PASS={SPLIT_PASS} (rho {sp["rho"]:.4f}, p {sp["p_one_sided"]:.4f})'

# ---------------- companion (declared in A2_ADDENDUM s4) ----------------
Nn = {f'e{j}': float(np.linalg.norm(V[f'e{j}'].mean(0))) for j in MEAS}
Fp = Vn.std(0, ddof=1) / 4
floorN = float(np.sqrt((Fp ** 2).sum()))
clearN = {j: (bool(Nn[f'e{j}'] > 2 * floorN) if j in MEAS else False) for j in ALLJ}
V69 = int(sum(clearN.values()))
V58 = int(sum(clearN[j] for j in NEWJ))
# tick 276 CORRECTION (after the workers, before any output): the first FINAL run
# halted on the self-check below -- this line built row 0 as all -1 while the check
# (and the mean self-check further down) needs all +1. Fixed by the global
# negation 1 - 2*bit; the 2^16 assignments are closed under global negation, so
# |SGN @ d| has the SAME multiset and every p-value is unchanged (checked on a
# random vector before re-running). Pre-fix file kept: final_a2_pre_fix_tick276.py
SGN = (1 - 2 * ((np.arange(65536, dtype=np.int64)[:, None] >> np.arange(16)[None, :]) & 1)).astype(np.float64)
assert SGN.shape == (65536, 16) and bool((SGN[0] > 0).all()) and bool(SGN[1, 0] < 0)
_a0 = f'e{MEAS[0]}'
assert abs(float(SGN[0] @ D[_a0]) / 16.0 - float(D[_a0].mean())) < 1e-15, 'sign matrix self-check'


def bh(p, q=0.05):
    p = np.asarray(p, float); mm = len(p); ps = np.sort(p)
    ok = ps <= q * np.arange(1, mm + 1) / mm
    return int(np.max(np.nonzero(ok)[0]) + 1) if ok.any() else 0


p_mean, p_vec = {}, {}
for j in MEAS:
    d = D[f'e{j}']; obs = abs(float(d.mean()))
    nul = np.abs(SGN @ d / 16.0)
    p_mean[j] = float((nul >= obs - 1e-12 * max(1.0, obs)).mean())
    v = V[f'e{j}']; obsN = Nn[f'e{j}']
    nulN = np.linalg.norm((SGN @ v) / 16.0, axis=1)
    p_vec[j] = float((nulN >= obsN - 1e-12 * max(1.0, obsN)).mean())
M_rej = bh([p_mean[j] for j in MEAS])
V_rej = bh([p_vec[j] for j in MEAS])
if V_rej >= 2 * M_rej and V_rej >= 5:
    cbranch = 'V_STRONGER'
elif M_rej >= 2 * V_rej and M_rej >= 5:
    cbranch = 'V_WEAKER'
else:
    cbranch = 'V_ALIKE'

# ---------------- predictions ----------------
top = max(MEAS, key=lambda j: abs(mean_e[f'e{j}']))
pred = {1: bool(not FLOOR_PASS), 2: bool(not SPLIT_PASS), 3: bool(VERDICT == 'I_INSTRUMENT'), 4: bool(top == 14),
        5: bool(V_rej > M_rej)}
S_all = float(sum(mean_e.values()))
shares = sorted(((abs(mean_e[f'e{j}']), j) for j in MEAS), reverse=True)
res = dict(base, status='FINAL',
           gates=dict(FLOOR_count=FLOOR69, FLOOR_pass=FLOOR_PASS, bar=14, SPLIT_pass=SPLIT_PASS,
                      rho=sp['rho'], p=sp['p_one_sided'], sign_agree=sign_agree, n_measurable=len(MEAS), verdict=VERDICT),
           floor=dict(F=F, twoF=2 * F, clears={f'e{j}': clear[j] for j in ALLJ}, sat=sat,
                      note='unmeasurable edges count as NOT clearing (A2_ADDENDUM s2)'),
           effects={f'e{j}': dict(edge_j=j, target=int(armsj[W_OF[f'e{j}']]['edges'][f'e{j}']['removed'][0]['target']),
                                  syn=syn[j], mean=mean_e[f'e{j}'], CI=tab[f'e{j}']['CI'], k_neg=tab[f'e{j}']['k_neg'],
                                  in_units_of_F=mean_e[f'e{j}'] / F, H1=H1[f'e{j}'], H2=H2[f'e{j}']) for j in MEAS},
           sum_of_singles=dict(S_all=S_all, top1_share=float(shares[0][0] / abs(S_all)) if S_all else None,
                               top1_edge=f'e{shares[0][1]}', top5=[f'e{j}' for _, j in shares[:5]]),
           metric_comparison=METRIC,
           companion=dict(primary='pool MEAN (PREREG s4, unchanged)', floorN=floorN, N=Nn, V69=V69, V58=V58,
                          p_signflip_mean={f'e{j}': p_mean[j] for j in MEAS}, p_signflip_vec={f'e{j}': p_vec[j] for j in MEAS},
                          M_rej=M_rej, V_rej=V_rej, branch=cbranch),
           predictions=pred, score=int(sum(pred.values())))
atomic('results_l240_a2.json', res)
print('FINAL: cutwA gate', ident, 'traces', trace_count, 'measurable', len(MEAS), 'unmeas', sorted(UNM))
print('F', F, 'FLOOR69', FLOOR69, 'pass', FLOOR_PASS, '| SPLIT rho', round(sp['rho'], 4), 'p', sp['p_one_sided'], 'agree', sign_agree, 'pass', SPLIT_PASS)
print('VERDICT', VERDICT, '| metric', METRIC['status'], METRIC.get('branch', METRIC.get('reason')))
print('sum singles', S_all, 'top1 share', res['sum_of_singles']['top1_share'], 'top', res['sum_of_singles']['top5'])
print('companion floorN', floorN, 'V69', V69, 'V58', V58, 'M_rej', M_rej, 'V_rej', V_rej, cbranch)
print('pred', pred, 'score', res['score'])
