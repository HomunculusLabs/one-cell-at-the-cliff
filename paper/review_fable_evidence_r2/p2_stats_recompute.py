#!/usr/bin/env python3
"""Round-2 referee probe 2: pooled statistics recomputed from out_duty_rows.json
(which p1 derived from RAW npz). Own Wilson / Newcombe / Fisher (log-gamma
hypergeometric, not the lab's comb() form). Compares against the DRAFT's
printed values, which are typed in below BY HAND FROM THE DRAFT TEXT."""
import json, math, os, collections, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'out_duty_rows.json')))
ROWS = D['rows']
Z = 1.959963984540054


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return max(0., c - h), min(1., c + h)


def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def lchoose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher2(a, b, c, d):
    """two-sided Fisher exact, [[a,b],[c,d]], sum of tables with prob <= observed."""
    n = a + b + c + d
    r1, c1 = a + b, a + c
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    lp = [lchoose(r1, x) + lchoose(n - r1, c1 - x) - lchoose(n, c1) for x in range(lo, hi + 1)]
    l0 = lp[a - lo]
    return min(1.0, sum(math.exp(v) for v in lp if v <= l0 + 1e-9))


# ---------------------------------------------------------------- inventory
lab = json.load(open('/home/t3rpz/critters/peabrain-lab/banc/l172/stats.json'))
ADM = set(lab['admissibility']['admissible'])
allfiles = sorted({r['file'] for r in ROWS})
print('files with Ti traces:', len(allfiles), '| lab-admissible:', len(ADM),
      '| admissible-but-missing-from-my-rows:', sorted(ADM - set(allfiles)))
print('non-admissible files I also scored:', sorted(set(allfiles) - ADM))

ALIAS = {'sil1110_wA': 'silW'}          # the lab pools these two names; flagged in the report


def pool(arm, files=None, side='R', key='duty07', alias=True):
    """unique-seed union; returns dict seed -> duty, plus dup stats."""
    seen, dup, bad = {}, 0, 0
    for r in ROWS:
        a = ALIAS.get(r['arm'], r['arm']) if alias else r['arm']
        if a != arm:
            continue
        if files is not None and r['file'] not in files:
            continue
        v = r[key + side]
        if r['seed'] in seen:
            dup += 1
            bad += abs(seen[r['seed']] - v) > 1e-6
            continue
        seen[r['seed']] = v
    return seen, dup, bad


def kn(arm, files=ADM, side='R', key='duty07'):
    s, dup, bad = pool(arm, files, side, key)
    v = np.array(list(s.values()))
    return int((v >= .5).sum()), len(v), float(v.mean()) if len(v) else float('nan'), dup, bad


DRAFT = {   # arm: (k, n, wilson lo, wilson hi, mean duty) as PRINTED in DRAFT §2.9
    'b65': (513, 513, .993, 1.000, .995), 'full': (207, 513, .362, .447, .457),
    'cutk5': (0, 226, .000, .017, .032), 'cutng19': (5, 178, .012, .064, .220),
    'cutng23': (0, 82, .000, .045, .084), 'cutwA': (72, 258, .228, .337, .404),
    'cutng25': (203, 210, .933, .984, .766), 'cutng25p': (30, 66, .340, .574, .459),
    'cutng29': (188, 194, .934, .986, .768), 'cut58': (1, 258, .001, .022, .220),
    'silW': (78, 98, .706, .864, .644), 'eMotTop5': (31, 98, .233, .414, .412),
    'eMotBot5': (25, 98, .179, .350, .372), 'eOutMot': (21, 34, .450, .761, .569),
}
print('\n== A. canonical pooled counts (lab-admissible files, unique seeds), mine vs DRAFT §2.9')
mine = {}
allok = True
for arm, (dk, dn, dlo, dhi, dm) in DRAFT.items():
    k, n, m, dup, bad = kn(arm)
    lo, hi = wilson(k, n)
    ok = (k, n) == (dk, dn) and abs(lo - dlo) < 6e-4 and abs(hi - dhi) < 6e-4 and abs(m - dm) < 6e-4
    allok &= ok
    mine[arm] = (k, n)
    print('%-9s mine %3d/%3d [%.3f,%.3f] mean %.3f dup %2d inconsistent %d | draft %3d/%3d [%.3f,%.3f] %.3f  %s'
          % (arm, k, n, lo, hi, m, dup, bad, dk, dn, dlo, dhi, dm, 'MATCH' if ok else 'MISMATCH'))
print('A all match:', allok)

print('\n== B. contrasts, mine vs DRAFT §2.9 difference table')
CON = [('carrier-base', 'cutng25', 'cutwA', +.688, +.621, +.742, 3.4e-59),
       ('carrier-twin', 'cutng25', 'cutng25p', +.512, +.388, +.628, 3.8e-20),
       ('twin-base', 'cutng25p', 'cutwA', +.175, +.047, +.305, .008),
       ('clamp-base', 'silW', 'cutwA', +.517, +.410, +.602, 6.7e-19),
       ('clamp-carrier', 'silW', 'cutng25', -.171, -.263, -.095, 2.9e-06),
       ('10mot-base', 'eOutMot', 'cutwA', +.339, +.162, +.491, 1.4e-04),
       ('10mot-carrier', 'eOutMot', 'cutng25', -.349, -.517, -.202, 3.1e-08),
       ('top5-base', 'eMotTop5', 'cutwA', +.037, -.064, +.147, .51),
       ('bot5-base', 'eMotBot5', 'cutwA', -.024, -.119, +.083, .69),
       ('k23-base', 'cutng23', 'cutwA', -.279, -.337, -.211, 1.7e-10),
       ('base-full', 'cutwA', 'full', -.124, -.191, -.053, 8.3e-04)]
okB = True
for name, a, b, dd, dlo, dhi, dp in CON:
    (k1, n1), (k2, n2) = mine[a], mine[b]
    d, lo, hi = newcombe(k1, n1, k2, n2)
    p = fisher2(k1, n1 - k1, k2, n2 - k2)
    ok = abs(d - dd) < 6e-4 and abs(lo - dlo) < 6e-4 and abs(hi - dhi) < 6e-4 and abs(math.log10(p) - math.log10(dp)) < .03
    okB &= ok
    print('%-14s %3d/%3d vs %3d/%3d d=%+.3f [%+.3f,%+.3f] p=%.3g | draft %+.3f [%+.3f,%+.3f] p=%.2g %s'
          % (name, k1, n1, k2, n2, d, lo, hi, p, dd, dlo, dhi, dp, 'MATCH' if ok else 'MISMATCH'))
kL1, nL1, *_ = kn('cutng25', side='L')
kL2, nL2, *_ = kn('cutwA', side='L')
d, lo, hi = newcombe(kL1, nL1, kL2, nL2)
print('LEFT carrier-base %d/%d vs %d/%d d=%+.3f [%+.3f,%+.3f] p=%.3g | draft 0/210 vs 13/258 -.050 [-.084,-.023] 4.0e-04'
      % (kL1, nL1, kL2, nL2, d, lo, hi, fisher2(kL1, nL1 - kL1, kL2, nL2 - kL2)))
print('B all match:', okB)

print('\n== C. is the TWIN contrast robust to HOW it is pooled? (twin = cutng25p)')
tw, _, _ = pool('cutng25p', ADM)
ba, _, _ = pool('cutwA', ADM)
ca, _, _ = pool('cutng25', ADM)
common = sorted(set(tw) & set(ba))
print('twin seeds %d; of these also run on the base arm: %d; also on carrier arm: %d'
      % (len(tw), len(common), len(set(tw) & set(ca))))
kt = sum(tw[s] >= .5 for s in common)
kb = sum(ba[s] >= .5 for s in common)
b01 = sum((tw[s] >= .5) and not (ba[s] >= .5) for s in common)
b10 = sum((ba[s] >= .5) and not (tw[s] >= .5) for s in common)
pm = min(1., 2 * sum(math.comb(b01 + b10, i) for i in range(0, min(b01, b10) + 1)) / 2 ** (b01 + b10))
print('SAME-SEED (paired) twin %d/%d vs base %d/%d ; discordant twin-only %d, base-only %d ; exact McNemar p=%.3g'
      % (kt, len(common), kb, len(common), b01, b10, pm))
d, lo, hi = newcombe(kt, len(common), kb, len(common))
print('  same-seed unpaired form: d=%+.3f [%+.3f,%+.3f] Fisher p=%.3g'
      % (d, lo, hi, fisher2(kt, len(common) - kt, kb, len(common) - kb)))
dd = np.array([tw[s] - ba[s] for s in common])
rng = np.random.default_rng(7)
bs = dd[rng.integers(0, len(dd), (20000, len(dd)))].mean(1)
print('  paired mean-duty difference twin-base on common seeds: %+.3f boot95 [%+.3f,%+.3f]; seeds up %d down %d'
      % (dd.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), (dd > 0).sum(), (dd < 0).sum()))
print('per-file twin vs base (same file):')
for f in sorted({r['file'] for r in ROWS if r['arm'] == 'cutng25p'}):
    t = [r for r in ROWS if r['file'] == f and r['arm'] == 'cutng25p']
    b = {r['seed']: r for r in ROWS if r['file'] == f and r['arm'] == 'cutwA'}
    c = {r['seed']: r for r in ROWS if r['file'] == f and r['arm'] == 'cutng25'}
    print('  %-24s %s twin %2d/%2d  base %2d/%2d  carrier %2d/%2d' % (
        f, 'ADM' if f in ADM else 'not', sum(r['duty07R'] >= .5 for r in t), len(t),
        sum(v['duty07R'] >= .5 for v in b.values()), len(b),
        sum(v['duty07R'] >= .5 for v in c.values()), len(c)))

print('\n== D. batch homogeneity of the k/n arms (are seeds exchangeable across batches?)')


def homog(arm, side='R'):
    per = collections.OrderedDict()
    seen = set()
    for r in ROWS:
        a = ALIAS.get(r['arm'], r['arm'])
        if a != arm or r['file'] not in ADM or r['seed'] in seen:
            continue
        seen.add(r['seed'])
        per.setdefault(r['file'], []).append(r['duty07' + side] >= .5)
    ks = np.array([sum(v) for v in per.values()])
    ns = np.array([len(v) for v in per.values()])
    keep = ns >= 8                      # drop files contributing only stray non-duplicate anchors
    ks, ns = ks[keep], ns[keep]
    p = ks.sum() / ns.sum()
    if p in (0, 1):
        return ks, ns, float('nan'), float('nan')
    chi = float((((ks - ns * p) ** 2) / (ns * p * (1 - p))).sum())
    rng = np.random.default_rng(11)
    flat = np.r_[np.ones(ks.sum()), np.zeros(ns.sum() - ks.sum())]
    cnt = 0
    B = 20000
    for _ in range(B):
        rng.shuffle(flat)
        kk = np.add.reduceat(flat, np.r_[0, np.cumsum(ns)[:-1]])
        cnt += (((kk - ns * p) ** 2) / (ns * p * (1 - p))).sum() >= chi - 1e-12
    return ks, ns, chi, (cnt + 1) / (B + 1)


for arm in ['full', 'cutwA', 'cutng25p', 'cutng25', 'silW', 'eMotTop5', 'eMotBot5', 'cutng19']:
    ks, ns, chi, p = homog(arm)
    print('%-9s per-batch k: %s  n: %s  chi2=%.1f df=%d  permutation p=%.4f'
          % (arm, list(ks), sorted(set(ns.tolist())), chi, len(ks) - 1, p))

print('\n== E. the five 1%-jitter networks (l139): carrier vs twin vs base, right side')
for j in range(6):
    f = 'l139/raw_l139_j%d.npz' % j
    out = []
    cells = {}
    for arm in ['full', 'cutng23', 'cutwA', 'cutng25p', 'cutng25', 'cutng29']:
        v = [r['duty07R'] for r in ROWS if r['file'] == f and r['arm'] == arm]
        cells[arm] = (sum(x >= .5 for x in v), len(v), float(np.mean(v)) if v else float('nan'))
        out.append('%s %2d/%2d (%.2f)' % (arm, *cells[arm]))
    kc, nc, _ = cells['cutng25']
    kt_, nt_, _ = cells['cutng25p']
    kb_, nb_, _ = cells['cutwA']
    print('set j%d | %s | carrier-vs-twin Fisher p=%.3g | twin-vs-base p=%.3g'
          % (j, ' | '.join(out), fisher2(kc, nc - kc, kt_, nt_ - kt_), fisher2(kt_, nt_ - kt_, kb_, nb_ - kb_)))

print('\n== F. what are the classes made of? tibia pool activity in the scored windows (lab-admissible, unique seeds)')
print('arm        n   meanR-duty | flexR mean  sd | extR mean  sd | flat-window count (R) | median S (R)')
for arm in ['b65', 'full', 'cutk5', 'cutng19', 'cutng23', 'cutwA', 'cutng25p', 'cutng25', 'cutng29', 'cut58', 'silW']:
    seen = {}
    for r in ROWS:
        a = ALIAS.get(r['arm'], r['arm'])
        if a == arm and r['file'] in ADM and r['seed'] not in seen:
            seen[r['seed']] = r
    v = list(seen.values())
    g = lambda k: float(np.mean([x[k] for x in v]))
    ms = [x['medS07R'] for x in v if x['medS07R'] is not None]
    print('%-9s %4d  %.3f | %.4f %.4f | %.4f %.4f | %5d of %d | %.3f'
          % (arm, len(v), g('duty07R'), g('mean_fR'), g('sd_fR'), g('mean_eR'), g('sd_eR'),
             sum(x['nan07R'] for x in v), len(v) * D['n_windows_q07'], float(np.median(ms)) if ms else float('nan')))

print('\n== G. scramble arm under the canonical rule vs the count the DRAFT prints (39/48)')
for arm in ['cutscr0', 'cutscr1', 'cutscr2', 'cutscr3', 'cutcl40', 'cutscrL1', 'cutscrL2']:
    k, n, m, dup, bad = kn(arm)
    kl, nl, *_ = kn(arm, side='L')
    print('%-9s canonical unique-seed R %2d/%2d  L %2d/%2d' % (arm, k, n, kl, nl))

print('\n== H. every arm name present in admissible files (inventory for the single-cell-scan question)')
inv = collections.Counter()
for r in ROWS:
    if r['file'] in ADM:
        inv[r['arm']] += 1
print(sorted(inv.items()))
