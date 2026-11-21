#!/usr/bin/env python3
"""L183 verify -- the master fold as a permanent gate.

 (1) the frozen pre-image is the stored artifact the previous manuscript stage
     registered by hash (no new pre-image file was written);
 (2) REPLAY: paper/DRAFT.md from the title onward equals, byte for byte,
     edits(renumber(pre-image)) rebuilt from the declared ledger
     (l183_fold.py + l183_text.py) and numbers.json, up to the stage the
     ledger says the draft has reached; the changelog banner is the pre-tick
     banner (pinned by hash) plus exactly this fold's declared entries;
 (3) NO HAND-TYPED MEASUREMENT: in every declared edit, each digit run that
     is not a {{placeholder}} resolved from numbers.json, and was not already
     in the text the edit replaces, must belong to a DECLARED class of
     non-measurement token (section references, citation markers, ledger
     keys, arm codes, rank labels, cell identifiers, protocol constants);
 (4) every sentence the fold authors is at most 60 words (the house rule,
     applied to all new text, not only the abstract and section 1);
 (5) the measured keys the fold added to numbers.json are re-derived here
     from their stored sources (cell by cell for every table), and the
     ledger file itself is pinned by hash;
 (6) cited-field statements about other papers trace to the stored, verified
     prior-art digest.

Run: python3 paper/l183_verify.py     (stdlib only; zero rollouts)
"""
import csv, hashlib, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l183_fold as F      # noqa: E402
import l183_text as TXT    # noqa: E402

LAB = F.LAB
B = os.path.join(LAB, 'banc')
live = open(os.path.join(HERE, 'DRAFT.md')).read()
nums = F.load_nums()
STAGE = TXT.CURRENT_STAGE
fails = []


def ck(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


# ------------------------------------------------------------------ (1)
raw_pre = open(F.PRE_PATH).read()
ck(hashlib.sha256(raw_pre.encode()).hexdigest() == F.PRE_SHA,
   '(1) the stored pre-image moved')
rep_prev = json.load(open(os.path.join(B, 'l174b4iiic', 'emit_report.json')))
ck(rep_prev['post_sha'] == F.PRE_SHA,
   "(1) the pre-image is not the previous stage's registered post-image")
print('(1) pre-image = banc/l174b4iiic/draft_post_preview.md, sha %s == the '
      "post_sha the previous stage's emit_report registered" % F.PRE_SHA[:16])

# ------------------------------------------------------------------ (2)
i_t = live.index(F.T)
banner, body = live[:i_t], live[i_t:]
want = F.build_body(nums, upto=STAGE)
if body != want:
    k = next((n for n, (a, b) in enumerate(zip(body, want)) if a != b),
             min(len(body), len(want)))
    fails.append('(2) REPLAY MISMATCH at title-relative offset %d: live %r vs '
                 'ledger %r' % (k, body[k - 40:k + 40], want[k - 40:k + 40]))
OLD_BANNER_SHA = '903835b965aa554b62a52d17776cd0611ec546fadd25dfe84a1600cd6d10f6df'
entry = TXT.BANNER_HEAD + ''.join(TXT.STAGE_NOTES[k]
                                  for k in range(1, STAGE + 1)) if STAGE else ''
if STAGE:
    ck(banner.endswith('\n' + entry + '\n'),
       "(2) the banner does not end with exactly this fold's declared entries")
    old_banner = banner[:len(banner) - len(entry) - 1]
else:
    old_banner = banner
ck(hashlib.sha256(old_banner.rstrip('\n').encode()).hexdigest() == OLD_BANNER_SHA,
   '(2) the pre-tick changelog banner moved')
ck(old_banner.startswith(raw_pre[:raw_pre.index(F.T)].rstrip('\n')),
   "(2) the banner no longer extends the stored pre-image's banner")
n_applied = sum(1 for e in TXT.EDITS if e['stage'] <= STAGE)
print('(2) REPLAY: title-onward body (%d bytes) == ledger(pre-image) byte for '
      'byte at stage %d (%d of %d declared edits applied%s); banner = the '
      'pinned pre-tick banner + this fold\'s declared entries'
      % (len(body), STAGE, n_applied, len(TXT.EDITS),
         ', renumber applied' if STAGE >= 2 else ''))

# ------------------------------------------------------------------ (3)
EXEMPT = [   # (regex, the declared class it removes)
    (r'\{\{[^{}]+\}\}', 'placeholder resolved from numbers.json'),
    (r'\u00a7\d+(?:\.\d+)?', 'section reference'),
    (r'\[\d+(?:, \d+)*\]', 'numeric citation marker'),
    (r'\[[a-z][a-z0-9_.]*(?:,\s+[a-z][a-z0-9_.]*)*\]', 'number-ledger key'),
    (r'`[^`\n]*`', 'arm code / file name in backticks'),
    (r'\branks? \d+(?: (?:to|and) \d+)?', 'ladder rank label'),
    (r'\brank-\d+\b', 'ladder rank label'),
    (r'\b(?:DN[a-z]*\d+(?:-[LR])?|IN\d+[A-Z]\d+|GAL4)\b', 'cell / tool name'),
    (r'\b(?:Table|Tables|entry|entries|Entries|[Ss]tage) \d+(?:-\d+)?',
     'table / reference-entry / stage label'),
    (r'\b(?:0\.7|1\.4)[- ]Hz\b', 'drive-segment frequency (protocol, 3.3)'),
    (r'\+0\.1%', 'unit of the gain slope'),
    (r'\b95%', 'confidence level'),
    (r'\b(?:24 heavy|24 other|24 heaviest|24-cell)\b',
     'size of the base cut, k = 24 (arm definition, 3.5)'),
    (r'\b16-seed\b', 'batch size (3.7)'),
    (r'\b[MNP] = B\d\d\b', 'internal batch code in the declared 3.7 mapping'),
    (r'\(18601 to 18616\)', 'seed range identifying batch Q'),
    (r'\b2026-11-21\b', 'date'),
    (r'\bv626\b', 'connectome release version'),
    (r'paper/priorart_terra_20261121\.md', 'stored file name'),
    (r'paper/l183_(?:verify|text)\.py', 'stored file name'),
    (r'\b50 nodes each\b', 'field number of entry 41, traced in (6)'),
    (r'(?m)^\d+\. ', 'reference-list numbering'),
    (r'doi:\S+', 'identifier'),
    (r'\(\d{4}\)', 'publication year'),
    (r'\(see also\n\s+entry 15,', 'cross-reference'),
    (r'(?m)^#+ \d+(?:\.\d+)?\.? ', 'section-heading number'),
    (r'10\u207b\u00b3', 'unit exponent'),
    (r'ln\(1 \+ n', 'the constant in log1p (3.2 equation)'),
    (r's\u2c7c [<>] 0', 'sign condition in the 3.2 equation'),
    (r'\bfloor-4\b', 'name of the stricter-floor substrate (section 4)'),
]
_DIG = re.compile(r'\d[\d,]*(?:\.\d+)?')


def typed_digits(e):
    t = e['new']
    for rx, _ in EXEMPT:
        t = re.sub(rx, ' ', t)
    new_toks = _DIG.findall(t)
    old_src = e['old'] if e['kind'] == 'rep' else ''
    for rx, _ in EXEMPT:
        old_src = re.sub(rx, ' ', old_src)
    old_toks = _DIG.findall(old_src)
    left = []
    for tok in new_toks:           # multiset difference: retained old text
        if tok in old_toks:
            old_toks.remove(tok)
        else:
            left.append(tok)
    return left


n_ph = 0
for e in TXT.EDITS:
    left = typed_digits(e)
    ck(not left, '(3) %s: hand-typed digits outside every declared class: %s'
       % (e['id'], left[:8]))
    n_ph += len(re.findall(r'\{\{[^{}]+\}\}', e['new']))
# sensitivity self-test: the predicate must FIRE on a typed measurement
_probe = dict(kind='rep', old='x', new='x and a mean duty of .758 on 16 seeds')
ck(typed_digits(_probe) == ['758', '16'] or typed_digits(_probe) == ['.758', '16']
   or len(typed_digits(_probe)) == 2, '(3) the typed-digit predicate is blind')
print('(3) no hand-typed measurement: %d placeholders across %d declared edits, '
      'every other digit run is retained pre-image text or one of %d declared '
      'non-measurement classes; predicate self-test fires'
      % (n_ph, len(TXT.EDITS), len(EXEMPT)))

# ------------------------------------------------------------------ (4)
def sents(t):
    t = re.sub(r'\s+', ' ', t)
    for a in ('Fig.', 'e.g.', 'i.e.', 'cf.', 'vs.', 'et al.'):
        t = t.replace(a, a.replace('.', '\x00'))
    return [x.replace('\x00', '.') for x in re.split(r'(?<=[.!?])\s+', t)
            if x.strip()]


worst = (0, '')
for e in TXT.EDITS:
    if e['id'].startswith('E25b'):          # the reference entries
        continue
    new = F.render(e['new'], nums)
    for para in new.split('\n\n'):
        if any(l.startswith(('|', '#', '    ')) for l in para.split('\n')):
            continue
        for s in sents(para):
            worst = max(worst, (len(s.split()), e['id'] + ': ' + s[:70]))
# an edit that splices into an old paragraph can inherit a clause on each
# side, so the splice sentences are measured on the BUILT text by l149 (31)
# and l159; here every authored paragraph is measured whole.
ck(worst[0] <= 60, '(4) an authored sentence of %d words: %s' % worst)
print('(4) longest authored sentence: %d words (limit 60)' % worst[0])

# ------------------------------------------------------------------ (5)
def near(a, b, tol=6e-4):
    return abs(a - b) <= tol


r175 = json.load(open(os.path.join(B, 'l175', 'results_l175.json')))
S = nums['l175.scan']['v']
src = {'cutwA': r175['base'], 'dmA': r175['twins']['dmA'],
       'dmC': r175['twins']['dmC']}
src.update({a['arm']: a for a in r175['window']})
ck(sorted(src) == sorted(S) and len(S) == 37, '(5) scan arm set != source')
for a, c in src.items():
    v = S[a]
    ck((v['kR'], v['n'], v['kL']) == (c['kR'], c['n'], c['kL'])
       and v['meanR'] == c['meanR'] and v['cls'] == c['cls'],
       '(5) l175.scan.%s != results_l175.json' % a)
ck(r175['branch'] == nums['l175.verdict']['v'] == 'D2_identity_carried',
   '(5) registered branch')
ck(sum(1 for a in r175['window'] if a['cls'] == 'SUPER') == 1
   and [a['arm'] for a in r175['window'] if a['cls'] == 'SUPER'] == ['sc25'],
   '(5) the carrier is not the single super arm in the source')
tp = {r['arm']: r for r in csv.DictReader(
    open(os.path.join(B, 'l184', 'threepanel.csv')))}
TPn = nums['l184.threepanel']['v']
ck(sorted(tp) == sorted(TPn) == sorted(S), '(5) panel arm set')
for a, r in tp.items():
    v = TPn[a]
    ck((v['chopped_k'], v['fast_k'], v['cross_k'])
       == (int(r['chopped_k']), int(r['fast_k']), int(r['cross_k']))
       and near(v['fast_mean'], float(r['fast_mean']))
       and near(v['cross_mean'], float(r['cross_mean'])),
       '(5) l184.threepanel.%s != threepanel.csv' % a)
    ck(int(r['chopped_k']) == S[a]['kR'], '(5) panel chopped k != scan k: ' + a)
r185 = json.load(open(os.path.join(B, 'l185', 'results_l185.json')))
R1 = nums['l185.r1']['v']
for a, v in r185['R1'].items():
    for form in ('rematched', 'fixed'):
        ck((R1[a][form]['kR'], R1[a][form]['meanR'], R1[a][form]['cls'])
           == (v[form]['kR'], v[form]['meanR'], v[form]['cls']),
           '(5) l185.r1.%s.%s' % (a, form))
    p = v['pooled_b39_b40_rematched']
    ck(R1[a]['pooled_b39_b40_rematched']['kR'] == p['kR']
       == v['rematched']['kR'] + S[a]['kR'] and p['n'] == 32,
       '(5) pooled two-batch count is not the sum of its batches: ' + a)
R2 = nums['l185.r2']['v']
ck(R2['kR'] == r185['R2']['kR'] and R2['deltas_pct'] == r185['R2']['deltas_pct']
   and near(R2['slope_meanR_per_0p1pct'], r185['R2']['slope_meanR_per_0p1pct'], 1e-4)
   and r185['R2']['gain_alone_super'] == [], '(5) l185.r2')
# the gain-null slope, recomputed: per-seed least-squares slopes are stored;
# their mean is the reported slope.
_ps = r185['R2']['per_seed_slopes']
ck(near(sum(_ps) / len(_ps), R2['slope_meanR_per_0p1pct'], 1e-4)
   and sum(1 for x in _ps if x < 0) == R2['n_seeds_negative_slope'],
   '(5) gain-null slope != mean of the stored per-seed slopes')
R3 = nums['l185.r3']['v']
ck((R3['kR'], R3['meanR'], R3['cls'], R3['gi']) ==
   (r185['R3']['arm']['kR'], r185['R3']['arm']['meanR'],
    r185['R3']['arm']['cls'], r185['R3']['arm']['gi']), '(5) l185.r3')
ck(r185['branches']['D2_hardened'] is True, '(5) l185 hardened flag')
r186 = json.load(open(os.path.join(B, 'l186', 'results_l186.json')))
for k, v in r186['contrasts'].items():
    w = nums['l186.contrasts']['v'][k]
    ck(near(w['value'], v['value']) and near(w['ci95'][0], v['ci95'][0])
       and near(w['ci95'][1], v['ci95'][1]), '(5) l186.contrasts.' + k)
ck(r186['branch'] == nums['l186.branch']['v'] == 'E3-mixed/unresolved',
   '(5) l186 branch')
_d = r186['contrasts']['D']['ci95']
ck(_d[0] < 0 < _d[1], '(5) the clock contrast interval no longer straddles 0 '
   '-- "unresolved" would be the wrong word')
r187 = json.load(open(os.path.join(B, 'l187', 'results_l187.json')))
A = nums['l187.arms']['v']
for a, c in r187['arms'].items():
    ck((A[a]['kR'], A[a]['meanR'], A[a]['cls'], A[a]['k14'], A[a]['mean14'])
       == (c['kR'], c['meanR'], c['cls'], c['k14'], c['mean14']),
       '(5) l187.arms.' + a)
for k, c in r187['contrasts'].items():
    w = nums['l187.contrasts']['v'][k]
    ck(near(w['mean'], c['mean']) and near(w['ci95'][0], c['ci95'][0])
       and near(w['ci95'][1], c['ci95'][1]), '(5) l187.contrasts.' + k)
# statements of the form "arms X read a to b" name their extreme arms by
# placeholder; prove those arms ARE the extremes
_absent = ['sc25', 'sc25F', 'pp', 'ppF', 'occ', 'occF']
_present = ['rsilW', 'rcut', 'rcutF', 'sc40', 'sc40F']
_m14 = {a: r187['arms'][a]['mean14'] for a in r187['arms']}
ck(min(_absent, key=_m14.get) == 'pp' and max(_absent, key=_m14.get) == 'occ'
   and max(_present, key=_m14.get) == 'rsilW'
   and max(_m14[a] for a in _present) < min(_m14[a] for a in _absent)
   and min(('rcut', 'rcutF', 'rsilW'), key=_m14.get) == 'rcut',
   '(5) the 1.4-Hz extremes named in section 2.4 are not the extremes')
_gs = nums['l187.gain_slopes']['v']
ck(all(_gs[a]['slope_per_0p1pct'] > 0 for a in ('sc25', 'pp', 'occ'))
   and _gs['sc40']['slope_per_0p1pct'] < 0 and _gs['rcut']['slope_per_0p1pct'] < 0
   and min(('sc25', 'pp', 'occ'), key=lambda a: _gs[a]['slope_per_0p1pct']) == 'sc25'
   and max(('sc25', 'pp', 'occ'), key=lambda a: _gs[a]['slope_per_0p1pct']) == 'pp',
   '(5) gain-slope signs / extremes named in section 2.4')
# section 2.1 statements read off the scan
ck(S['sc33']['kR'] == 0 and S['sc34']['kR'] == 0 and S['sc33']['sign'] > 0
   and S['sc34']['sign'] > 0, '(5) ranks 33/34 statement')
ck(max(S, key=lambda a: S[a]['meanR']) == 'sc25',
   '(5) "its duty is the highest in the table"')
ck(r187['branches']['A2'] == 'R1_conduit' and r187['branches']['A1']
   == 'A1_unresolved' and r187['branches']['A3'] == 'R3_stack',
   '(5) l187 registered branches')
# paired twin: an independent recount from the stored per-seed arrays
ps = json.load(open(os.path.join(B, 'l172', 'stats.json')))['per_seed']
tw = dict(zip(ps['cutng25p']['seeds'], ps['cutng25p']['dutyR']))
bs = dict(zip(ps['cutwA']['seeds'], ps['cutwA']['dutyR']))
b_, c_ = (sum(1 for s in tw if tw[s] >= .5 and bs[s] < .5),
          sum(1 for s in tw if tw[s] < .5 and bs[s] >= .5))
p_mc = min(1.0, sum(math.comb(b_ + c_, i) for i in range(0, min(b_, c_) + 1))
           * 2 / 2 ** (b_ + c_))
PT = nums['l172.paired_twin']['v']
ck((PT['twin_only'], PT['base_only'], PT['n']) == (b_, c_, len(tw))
   and near(PT['mcnemar_p'], p_mc, 6e-5) and PT['twin_k'] == 30
   == nums['l172.pooled']['v']['cutng25p']['kR'], '(5) l172.paired_twin')
ck(p_mc > .05, '(5) the paired twin test is resolved -- the text says it is not')
# the batch mapping declared in section 3.7 (letters -> internal codes)
ck(r186['seeds'] == list(range(18601, 18617)), '(5) batch Q seed range')
for _l, _code in (('l175', 'B39'), ('l185', 'B40'), ('l187', 'B41')):
    ck(_code in open(os.path.join(B, _l, 'PREREG.md')).read(),
       '(5) batch code %s is not the one %s registered' % (_code, _l))
ck(r175['seeds'][0] == 3545 and r185['seeds'][0] == 3577
   and r187['seeds'][0] == 3609, '(5) batch first seeds')
# Table 4: the ladder in the continuous segment, re-pooled independently
_rows = json.load(open(os.path.join(HERE, 'review_fable_evidence_r2',
                                    'out_duty_rows.json')))['rows']
_adm = set(json.load(open(os.path.join(B, 'l172', 'stats.json')))
           ['admissibility']['admissible'])
LFn = nums['l183.ladder_fast']['v']
for _arm, _d in LFn.items():
    _seen = {}
    for _r in _rows:
        if _r['arm'] == _arm and _r['file'] in _adm:
            _seen.setdefault(_r['seed'], _r)
    _v = list(_seen.values())
    _pool = nums['l172.pooled']['v'][_arm]
    ck((len(_v), sum(x['duty07R'] >= .5 for x in _v)) == (_pool['n'], _pool['kR'])
       == (_d['n'], _d['chopped_k']),
       '(5) ladder %s: stored rows do not reproduce the canonical pool' % _arm)
    ck(sum(x['duty14R'] >= .5 for x in _v) == _d['fast_k']
       and near(sum(x['duty14R'] for x in _v) / len(_v), _d['fast_mean']),
       '(5) ladder %s: continuous-segment cell' % _arm)
_cuts = ['cutk5', 'cutng19', 'cutng23', 'cutwA', 'cutng25p', 'cutng25', 'cutng29', 'cut58']
ck(max(_cuts, key=lambda a: LFn[a]['fast_k'] / LFn[a]['n']) == 'cut58'
   and all(LFn[a]['fast_k'] == 0 for a in ('full', 'cutwA', 'cutk5', 'cutng19',
                                           'cutng23', 'cutng25p'))
   and len(LFn) == 11
   and LFn['cutng25']['fast_k'] > 0
   and LFn['cutscr0']['fast_k'] / LFn['cutscr0']['n'] < .5,
   '(5) the readings of Table 4 stated in section 2.6')
s92 = json.load(open(os.path.join(B, 'l92', 'static.json')))
SUB = nums['l92.substrate']['v']
ck(all(SUB[k] == s92[k] for k in SUB) and SUB['n_new'] - SUB['n_old']
   == SUB['dn_new'] and SUB['cord'] + SUB['dn_into'] == SUB['n_old'],
   '(5) l92.substrate / closure arithmetic')
NUMBERS_SHA = '592f7680796ef43f662bb910c0a57893f752a4ee654ed24d2f8c523a84b9782a'
# the ledger and the built body are pinned too: a later stage that edits
# either has to re-pin here deliberately (and say why in the lane log)
LEDGER_SHA = {'l183_text.py': 'd1d8e0735bf176947d04daa8d7fd702dc87cde6d3ad2d608a2a05ec55824d028',
              'l183_fold.py': '698922e3b836f49936e8445fc16da38c7652e9b71025ac049ddb6db9bb0850e9'}
BODY_SHA = 'e62c81f6f5ccf8efd95df6e8de314d287257663f41b2b1e1239695ff12434d23'
for _f, _want in LEDGER_SHA.items():
    _got = hashlib.sha256(open(os.path.join(HERE, _f), 'rb').read()).hexdigest()
    ck(_got == _want, '(5) %s moved since the fold was finalized (%s)'
       % (_f, _got[:12]))
ck(hashlib.sha256(body.encode()).hexdigest() == BODY_SHA,
   '(5) the built body moved since the fold was finalized')
_h = hashlib.sha256(open(os.path.join(HERE, 'numbers.json'), 'rb').read()).hexdigest()
if NUMBERS_SHA is not None:
    ck(_h == NUMBERS_SHA, '(5) numbers.json moved since the fold was finalized '
       '(%s)' % _h[:12])
print('(5) added keys re-derived from source: 37 scan arms + 37 panel rows + '
      'both gain forms of 6 replication arms + the gain null (slope == mean of '
      '16 stored per-seed slopes) + the signed-current twin + 3 jitter '
      'contrasts + %d relay arms + %d relay contrasts; McNemar recounted from '
      'the per-seed arrays (b=%d, c=%d, p=%.4f); closure arithmetic holds; '
      'numbers.json sha %s%s'
      % (len(r187['arms']), len(r187['contrasts']), b_, c_, p_mc, _h[:12],
         ' == pin; ledger and built body pinned' if NUMBERS_SHA else ' (pin set at finalization)'))

# ------------------------------------------------------------------ (6)
prior = re.sub(r'\s+', ' ', open(os.path.join(
    HERE, 'priorart_terra_20261121.md')).read())
FIELD = ['equally sized 50-node lesions',
         'three-interneuron rhythm circuit across four datasets',
         'individual E1 or E2 silencing in the full simulation abolishes leg '
         'motor rhythms',
         'volume control greatly reduced death associations',
         'lesion volume, age and sex as covariates',
         'laser killing of cell precursors']
for s in FIELD:
    ck(s in prior, '(6) cited-field statement not in the verified digest: ' + s)
print('(6) %d cited-field statements traced to paper/priorart_terra_20261121.md'
      % len(FIELD))

print()
if fails:
    print('L183 VERIFY: %d FAILURE(S)' % len(fails))
    for f in fails:
        print('  - ' + f)
    sys.exit(1)
print('L183 verify: ALL GREEN (stage %d)' % STAGE)
