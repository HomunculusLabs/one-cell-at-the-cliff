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

L190b FOLLOW-UP (2026-11-21, stage 7; receipt in LANE-LOG and
banc/l190b_worklog.md).  The single-edge cut (banc/l190) enters as four more
declared edits and six l190.* keys.  Sections (1)-(4) and (6) are unchanged
and now run over the stage-7 ledger; section (5) GAINS the L190 re-derivation
(every table cell recomputed from the stored per-seed rows, the registered
branch rules re-applied, each sentence-level reading of the new text proved);
the four finalization pins at the end of (5) are re-pinned to the stage-7
state with the retired values kept beside them.  Nothing was removed.

L197 REPAIRS (2026-11-21, stage 8; receipt in LANE-LOG and
banc/l197_worklog.md).  The fourth-round referee's three minor repairs enter
as eleven more declared edits and five keys (l139.sets, l139.gains,
l139.contrast, l175.null_centre, l197.reference).  Sections (1), (2), (4) and
(6) are unchanged and run over the stage-8 ledger.  Section (3) gains ONE
declared non-measurement class, the figure label ("Fig. 4"), the sibling of
the table label already declared; the predicate self-test still fires.
Section (5) GAINS the L197 re-derivation (the per-set jitter table recounted
from the stored cells, the registered super rule re-applied per cell, the
null centre and its interval recomputed from the stored per-seed duties, the
reference contrast and its Newcombe interval recomputed, and one check per
sentence-level reading); the four finalization pins are re-pinned to the
stage-8 state with the retired values kept beside them.  NEW section (7): the
figure layer resolves (every cited figure file exists under paper/, Figs 1-5
are each cited, the three legacy figures are byte-identical to their lab
originals, and both figure verifiers exit 0).  Nothing was removed.

RESIDUE FOLD (2026-11-21 evening, stage 9; receipt in LANE-LOG and
banc/residue_worklog.md).  Sixteen more declared edits and NO new key: the
yardstick calibration carried into the abstract and the Discussion (two
edits, every number a placeholder on l197.reference), entries 38-45 with full
author lists (two edits; audited against stored primary records by
l174_verify (9)), and twelve formatting edits over 2.6-2.12 and section 3.
Sections (1)-(4), (6) and (7) are unchanged and run over the stage-9 ledger;
no class was added to section (3).  Section (5) GAINS the stage-9 block: the
yardstick readings re-derived, and for every formatting edit a proof that it
is de-emphasis only (the citation keys are identical, no digit run is added,
and the only digit runs removed are the declared repeats of a cell id or of
an arm code's digits).  Two of the four finalization pins move (the text
ledger and the built body); numbers.json and l183_fold.py are unchanged and
keep their stage-8 pins.  Nothing was removed.

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
    # L197 (2026-11-21; receipt in LANE-LOG): the figure label, sibling of the
    # table label above.  Section (7) below checks what the label points at.
    (r'\bFigs?\.? \d+', 'figure label'),
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
# ---- L190b follow-up fold (stage 7): the single-edge cut and its sham ------
r190 = json.load(open(os.path.join(B, 'l190', 'results_l190.json')))
sel190 = json.load(open(os.path.join(B, 'l190', 'selection.json')))
pre190 = open(os.path.join(B, 'l190', 'PREREG.md')).read()
EAn, EMn = nums['l190.arms']['v'], nums['l190.meta']['v']
ESn = nums['l190.selection']['v']
ck(r190['status'] == 'FINAL' and r190['controls_pass'] is True
   and EMn['controls_pass'] is True, '(5) l190 run not final / controls')
ck(nums['l190.summary']['v'] == r190['summary'] and ESn == r190['selection']
   == sel190['edges'] and nums['l190.gain']['v'] == r190['gain'],
   '(5) l190.summary / selection / gain are not the stored dicts verbatim')
_T15 = 2.131449546                      # two-sided 95% t quantile, 15 df
_sd190 = [str(x) for x in r190['seeds']]
ck(sorted(EAn) == ['base', 'carrier', 'edge', 'sham']
   and sorted(d['code'] for d in EAn.values()) == sorted(r190['summary']),
   '(5) l190 arm set')
for _lab, _d in EAn.items():
    _Rv = [r190['rows'][x][_d['code']]['R'] for x in _sd190]
    _Mv = [r190['rows'][x][_d['code']]['mid'] for x in _sd190]
    _Dv = [r190['rows'][x][_d['code']]['R'] - r190['rows'][x]['cutwA']['R']
           for x in _sd190]
    _dm = sum(_Dv) / len(_Dv)
    _hf = _T15 * (sum((x - _dm) ** 2 for x in _Dv) / (len(_Dv) - 1)) ** .5 \
        / len(_Dv) ** .5
    ck(_d['n'] == len(_Rv) == 16 and _d['kR'] == sum(x >= .5 for x in _Rv)
       and near(_d['meanR'], sum(_Rv) / 16, 1e-9)
       and _d['kmid'] == sum(x >= .5 for x in _Mv)
       and near(_d['meanmid'], sum(_Mv) / 16, 1e-9),
       '(5) l190.arms.%s: counts / means != the stored per-seed rows' % _lab)
    ck(near(_d['vs_base']['mean'], _dm, 1e-9)
       and near(_d['vs_base']['ci95'][0], _dm - _hf, 1e-6)
       and near(_d['vs_base']['ci95'][1], _dm + _hf, 1e-6)
       and _d['vs_base']['n_up'] == sum(x > 0 for x in _Dv),
       '(5) l190.arms.%s: paired contrast != recomputed from the rows' % _lab)
    ck(near(_d['gain_delta_pct'], (r190['gain'][_d['code']]
                                   / r190['gain']['cutwA'] - 1) * 100, 6e-4),
       '(5) l190.arms.%s: gain shift' % _lab)
# the registered rules (banc/l190/PREREG.md), re-applied here to the recounts
_BDn = nums['l175.bands']['v']
ck('mean\u2265.60 and k\u226512' in pre190
   and (_BDn['super_meanR_min'], _BDn['super_kR_min']) == (0.6, 12)
   and 'middle-segment R duty \u2265.25' in pre190
   and EMn['fingerprint_min_meanmid'] == 0.25
   and 'absolute paired mean shift <.10' in pre190,
   '(5) l190 registered bars are not the ones the text applies')
_sup = lambda d: d['meanR'] >= .60 and d['kR'] >= 12
_fp = lambda d: d['meanmid'] >= .25
ck(all(_sup(d) == d['super'] and _fp(d) == d['fingerprint'] for d in EAn.values())
   and not _sup(EAn['base']) and _sup(EAn['carrier']) and _fp(EAn['carrier']),
   '(5) l190 super / fingerprint flags, or the two controls')
_e, _s = EAn['edge'], EAn['sham']
ck(_sup(_e) and not _fp(_e) and _e['vs_base']['mean'] >= .10
   and _e['vs_base']['ci95'][0] > 0 and EMn['branch_edge'] == 'B3-partial',
   '(5) the edge cut is not the registered partial branch')
ck(not _sup(_s) and not _fp(_s) and abs(_s['vs_base']['mean']) < .10
   and EMn['branch_sham'] == 'B2-edge-inert'
   and _s['vs_base']['ci95'][0] < 0 < _s['vs_base']['ci95'][1],
   '(5) the sham is not base-like by the registered rule')
ck(near(EMn['edge_share_of_carrier'], _e['vs_base']['mean']
        / EAn['carrier']['vs_base']['mean'], 6e-4)
   and _e['vs_base']['mean'] < EAn['carrier']['vs_base']['mean'],
   '(5) l190 edge share of the carrier shift')
# sentence-level readings of the stage-7 text
ck(_e['kR'] == A['rsilW']['kR'] == A['pp']['kR'] == _BDn['super_kR_min'],
   '(5) "three of them sit on a band edge" (edge cut, clamp, double removal)')
ck(_e['kmid'] == _s['kmid'] == EAn['base']['kmid'] == 0 and _e['meanmid'] == 0
   and max(_e['meanmid'], _s['meanmid'], EAn['base']['meanmid'],
           max(_m14[a] for a in _present), r187['base']['mean14'])
   < min(EAn['carrier']['meanmid'], min(_m14[a] for a in _absent)),
   '(5) "no graph that keeps the carrier shows the signature in either batch"')
_Cn = nums['l187.contrasts']['v']
ck(_Cn['occ_minus_rcut']['ci95'][0] > 0
   and _Cn['occF_minus_rcutF']['ci95'][0] < 0 < _Cn['occF_minus_rcutF']['ci95'][1]
   and max(_Cn['occ_minus_rcut']['mean'], _Cn['occF_minus_rcutF']['mean'])
   < A['sc25F']['vs_base']['mean'],
   '(5) "a smaller chopped increment, resolved at re-matched gains and not at '
   'the base gain"')
ck(_e['gain_delta_pct'] < 0 and R2['slope_meanR_per_0p1pct'] < 0
   and abs(_s['gain_delta_pct']) < .01,
   '(5) the gain caveat: the edge arm re-bisects DOWN and a lower gain raises '
   'the base duty')
_rl = nums['l187.relay']['v']
ck(ESn['E-edge']['source'] == S['sc25']['gi']
   and ESn['E-edge']['target'] == ESn['E-sham']['target'] == _rl['cell']['gi']
   and ESn['E-edge']['syn'] == _rl['carrier_to_relay']['syn']
   and abs(ESn['E-sham']['syn'] - ESn['E-edge']['syn']) == 1
   and ESn['E-edge']['effective_weight'] > 0 < ESn['E-sham']['effective_weight']
   and ESn['E-sham']['DN'] is True
   and ESn['E-sham']['source'] not in {v.get('gi') for v in S.values()}
   and EMn['n_sham_candidates'] == len(sel190['candidates']) == 1
   and sel190['candidates'][0][3:] == [ESn['E-sham']['source'],
                                       ESn['E-sham']['syn']],
   '(5) the edge / sham description (carrier -> relay, count-matched '
   'excitatory descending-neuron source outside the scan window, sole '
   'candidate)')
_prior_seeds = (set(r175['seeds']) | set(r185['seeds']) | set(r186['seeds'])
                | set(r187['seeds']))
ck(r190['seeds'] == list(range(EMn['seed_lo'], EMn['seed_hi'] + 1))
   and len(r190['seeds']) == EMn['n_seeds'] == 16
   and _prior_seeds.isdisjoint(r190['seeds']),
   '(5) batch R is not a fresh 16-seed block')
ck(open(os.path.join(B, 'l190', 'PREREG.sha256')).read().split()[0]
   == r190['prereg'] == hashlib.sha256(open(os.path.join(
       B, 'l190', 'PREREG.md'), 'rb').read()).hexdigest()
   and r190['prereg'].startswith(EMn['prereg_sha256']),
   '(5) l190 preregistration hash')
_c190 = nums['l190.certs']['v']
ck(_c190['c0a135_max'] == 0.0 == _c190['c0a175_max']
   and r190['anchors']['c0a135_pass'] and r190['anchors']['c0a175_pass']
   and _c190['g_cutwA_stored_exact'] is True, '(5) l190 anchor certificates')
print('(5) L190 (stage 7): 4 arms x 16 seeds recounted from the stored rows '
      '(edge %d/16 %.3f, %+.3f [%+.3f, %+.3f]; sham %d/16 %.3f); registered '
      'branch rules re-applied (edge = partial, sham = base-like); edge share '
      '%.3f; sole sham candidate; seeds %d-%d fresh; prereg hash == file'
      % (_e['kR'], _e['meanR'], _e['vs_base']['mean'], *_e['vs_base']['ci95'],
         _s['kR'], _s['meanR'], EMn['edge_share_of_carrier'],
         EMn['seed_lo'], EMn['seed_hi']))
# ---- L197 repairs (stage 8): jitter table, yardstick, null centre ----------
r139 = json.load(open(os.path.join(B, 'l139', 'results_l139.json')))
JSn, JGn = nums['l139.sets']['v'], nums['l139.gains']['v']
JTn = nums['l139.contrast']['v']
_A3 = ('cutwA', 'cutng25p', 'cutng25')        # base, base + mass twin, carrier
_SETS = ['0', '1', '2', '3', '4', '5']
_JIT = _SETS[1:]
ck(sorted(JSn) == sorted(JGn) == sorted(r139['sets']) == sorted(r139['gains'])
   == _SETS, '(5) l139 set labels')
ck(all(JSn[s][a] == {k: r139['sets'][s][a][k] for k in ('kR', 'meanR', 'cls')}
       and JGn[s][a] == r139['gains'][s][a] for s in _SETS for a in _A3)
   and all(sorted(JSn[s]) == sorted(JGn[s]) == sorted(_A3) for s in _SETS),
   '(5) l139.sets / l139.gains are not the stored cells verbatim')
# the registered super rule, re-applied to every cell of Table 5
ck(all(_sup(r139['sets'][s][a]) == (r139['sets'][s][a]['cls'] == 'SUPER')
       for s in _SETS for a in _A3),
   '(5) a stored class label of Table 5 disagrees with the registered super rule')
ck(sorted(nums['sustain.cutng25']['v']['classes']) == _JIT
   and all(nums['sustain.' + a]['v']['classes'][s] == r139['sets'][s][a]['cls']
           for s in _JIT for a in _A3),
   '(5) Table 5 classes != the class-sustain keys section 2.10 already cites')
_k139 = lambda s, a: r139['sets'][s][a]['kR']
_hold139 = {}
for _s in _SETS:
    _b, _t, _c = (r139['sets'][_s][a] for a in _A3)
    _hold139[_s] = (_sup(_c) and not _sup(_b) and not _sup(_t)
                    and _c['kR'] > _b['kR'] and _c['kR'] > _t['kR'])
    _p = JTn['per_set'][_s]
    ck(_p['carrier_minus_base'] == _c['kR'] - _b['kR']
       and _p['carrier_minus_twin'] == _c['kR'] - _t['kR']
       and _p['holds'] is _hold139[_s]
       and _p['n_super'] == sum(_sup(x) for x in (_b, _t, _c))
       and near(_p['base_gain_delta_pct'], (r139['gains'][_s]['cutwA']
                                           / r139['gains']['0']['cutwA'] - 1) * 100),
       '(5) l139.contrast.per_set.%s != recomputed from the stored cells' % _s)
_holds = [int(s) for s in _JIT if _hold139[s]]
_adv = [int(s) for s in _JIT if not _hold139[s]]
ck(JTn['hold_sets'] == _holds == [1, 2, 3, 4] and JTn['n_sets_hold'] == 4
   and JTn['n_jitter_sets'] == 5 and JTn['n_networks'] == 6
   and _adv == [JTn['adverse_set']] == [5] and _hold139['0'],
   '(5) "the title contrast holds in 4 of the 5 jitter sets ... and does not '
   'hold in set 5" / "In sets 1 to 4"')
ck(all(JTn['per_set'][str(s)]['n_super'] == 1 for s in _holds),
   '(5) "the only one of the three in the super class" in the holding sets')
for _lab, _a in (('base', 'cutwA'), ('twin', 'cutng25p'), ('carrier', 'cutng25')):
    _pp = JTn['pooled'][_lab]
    ck(_pp['kR'] == sum(_k139(s, _a) for s in _JIT) and _pp['n'] == 16 * 5
       and near(_pp['meanR'], sum(r139['sets'][s][_a]['meanR'] for s in _JIT) / 5),
       '(5) l139.contrast.pooled.%s' % _lab)
_Pn = JTn['pooled']
ck(_Pn['carrier_minus_base'] == _Pn['carrier']['kR'] - _Pn['base']['kR'] > 0
   and _Pn['carrier_minus_twin'] == _Pn['carrier']['kR'] - _Pn['twin']['kR'] > 0
   and _Pn['carrier']['meanR'] > max(_Pn['base']['meanR'], _Pn['twin']['meanR']),
   '(5) "holds summed over them"')
ck(JTn['n_seeds'] == 16 and '3201-3216' in open(os.path.join(
       B, 'l139', 'PREREG.md')).read()
   and 'same B28 seed = same noise draw in every set' in open(os.path.join(
       B, 'l139', 'PREREG.md')).read(),
   '(5) "The same 16 seeds run in every network"')
_th = JTn['tightest_hold']
_ts = str(_th['set'])
ck(_th['set'] == min(_holds, key=lambda s: _k139(str(s), 'cutng25')
                     - _k139(str(s), 'cutng25p'))
   and _th['carrier_minus_twin'] == _k139(_ts, 'cutng25') - _k139(_ts, 'cutng25p')
   and (_th['twin_kR'], _th['twin_meanR']) == (
       _k139(_ts, 'cutng25p'), r139['sets'][_ts]['cutng25p']['meanR'])
   and _th['twin_kR'] >= _BDn['super_kR_min']
   and _BDn['super_meanR_min'] - .01 < _th['twin_meanR'] < _BDn['super_meanR_min'],
   '(5) "The narrowest of the four is set 1 ... just under the band\'s mean bar"')
_ad = JTn['adverse']
_as = str(JTn['adverse_set'])
ck((_ad['base_kR'], _ad['twin_kR'], _ad['carrier_kR'])
   == tuple(_k139(_as, a) for a in _A3)
   and all(_sup(r139['sets'][_as][a]) for a in _A3)
   and _ad['base_minus_carrier'] == _ad['base_kR'] - _ad['carrier_kR'] == 2
   and _ad['carrier_minus_twin'] == 0
   and near(_ad['base_gain_delta_pct'], JTn['per_set'][_as]['base_gain_delta_pct'], 1e-9),
   '(5) set 5: "the base reaches the super class with the carrier still in it '
   '... the twin arm reaches it too ... 2 seeds below the base and level with '
   'the twin arm"')


def _rk197(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for q in range(i, j + 1):
            out[o[q]] = (i + j) / 2 + 1
        i = j + 1
    return out


def _sp197(a, b):
    ra, rb = _rk197(a), _rk197(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / (
        sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** .5


_bg = [r139['gains'][s]['cutwA'] for s in _SETS]
_bk = [_k139(s, 'cutwA') for s in _SETS]
_by_gain = [k for _, k in sorted(zip(_bg, _bk))]
ck(JTn['base_kR_by_set'] == _bk
   and JTn['base_gain_lowest_set'] == int(min(_SETS, key=lambda s: _bg[int(s)]))
   == JTn['adverse_set'] == JTn['base_kR_highest_set']
   and near(JTn['rho_base_gain_kR'], _sp197(_bg, _bk))
   and all(x >= y for x, y in zip(_by_gain, _by_gain[1:]))
   and _ad['base_gain_delta_pct'] < 0,
   '(5) "the base re-bisects to the lowest gain of the six networks ... the '
   'base\'s count falls as its gain rises"')
ck(R2['slope_meanR_per_0p1pct'] < 0 and R2['deltas_pct'][2] == 0.0
   and min(R2['kR'][:2]) > R2['kR'][2],
   '(5) "On the unjittered graph a lower gain alone raises the base (2.2)"')
# the centre of the silent-cell null, from the stored per-seed duties
NCn = nums['l175.null_centre']['v']
_NLn = nums['l175.null']['v']
_sil = [a for a in r175['window'] if not a['active']]
_car = next(a for a in r175['window'] if a['arm'] == 'sc25')
_bD = r175['base']['dutyR']
_mb = sum(_bD) / 16
_armm = [sum(a['dutyR']) / 16 for a in _sil]
_sd_ = [sum(a['dutyR'][i] for a in _sil) / len(_sil) - _bD[i] for i in range(16)]
_m = sum(_sd_) / 16
_hf = _T15 * (sum((x - _m) ** 2 for x in _sd_) / 15) ** .5 / 4
ck(len(_sil) == NCn['n'] == _NLn['n_silent'] == 20
   and all(len(a['dutyR']) == 16 for a in _sil) and len(_bD) == 16
   and near(NCn['mean'], _m, 1e-9) and near(NCn['base_duty'], _mb, 1e-9)
   and near(NCn['mean_duty'], sum(_armm) / 20, 1e-9)
   and NCn['n_above'] == sum(x > _mb for x in _armm)
   == sum(a['meanR'] > r175['base']['meanR'] for a in _sil)
   and NCn['n_above'] + NCn['n_below'] == 20,
   '(5) l175.null_centre: mean / counts != recomputed from the per-seed duties')
ck(near(NCn['over_seeds']['mean'], _m, 1e-9)
   and near(NCn['over_seeds']['ci95'][0], _m - _hf, 1e-9)
   and near(NCn['over_seeds']['ci95'][1], _m + _hf, 1e-9)
   and NCn['over_seeds']['n_up'] == sum(x > 0 for x in _sd_)
   and NCn['over_seeds']['n'] == 16,
   '(5) l175.null_centre.over_seeds != recomputed paired t interval')
ck(_m > 0 and NCn['n_above'] > NCn['n_below']
   and NCn['over_seeds']['ci95'][0] < 0 < NCn['over_seeds']['ci95'][1],
   '(5) "above the base as a point estimate and is not resolved from zero"')
_gp = [a['gain_delta_vs_wA'] / r175['base']['gain'] * 100 for a in _sil]
ck(near(NCn['mean_gain_pct'], sum(_gp) / 20, 1e-9) and NCn['mean_gain_pct'] < 0
   and all(near(a['gain_delta_vs_wA'] / r175['base']['gain'] * 100,
               S[a['arm']]['gain_pct'], 6e-3) for a in _sil),
   '(5) "re-bisect to gains that average ... below the base\'s"')
ck(near(NCn['carrier_minus_centre'], sum(_car['dutyR']) / 16 - sum(_armm) / 20, 1e-9)
   and max(_armm) < sum(_car['dutyR']) / 16
   and max(a['meanR'] for a in _sil) == _NLn['silent_meanR_max'] < _car['meanR'],
   '(5) "The carrier\'s mean duty stands ... above it and above every arm in '
   'the null"')
# the reference network: recomputed from the Table 4 pools and the stored rows
REFn = nums['l197.reference']['v']
for _lab, _arm in (('reference', 'b65'), ('closure', 'full'), ('base', 'cutwA'),
                   ('carrier', 'cutng25')):
    _d = REFn[_lab]
    ck(_d['code'] == _arm and all(_d[k] == LFn[_arm][k] for k in
                                  ('n', 'chopped_k', 'chopped_mean', 'fast_k',
                                   'fast_mean')),
       '(5) l197.reference.%s != the Table 4 pool (itself re-pooled above)' % _lab)


def _wil(k, n, z=1.959963984540054):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** .5) / den
    return max(0.0, c - h), min(1.0, c + h)


def _newc(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    (l1, u1), (l2, u2) = _wil(k1, n1), _wil(k2, n2)
    d = p1 - p2
    return d, d - ((p1 - l1) ** 2 + (u2 - p2) ** 2) ** .5, \
        min(1.0, d + ((u1 - p1) ** 2 + (p2 - l2) ** 2) ** .5)


_Rr, _Cc = REFn['reference'], REFn['closure']
for _key, _col in (('fast_diff', 'fast_k'), ('chopped_diff', 'chopped_k')):
    _d, _lo, _hi = _newc(_Rr[_col], _Rr['n'], _Cc[_col], _Cc['n'])
    ck(near(REFn[_key]['diff'], _d, 1e-9) and near(REFn[_key]['ci95'][0], _lo, 1e-9)
       and near(REFn[_key]['ci95'][1], _hi, 1e-9),
       '(5) l197.reference.%s != recomputed Newcombe interval' % _key)
_seedset = lambda arm: {r['seed'] for r in _rows
                        if r['arm'] == arm and r['file'] in _adm}
ck(REFn['same_seeds'] is (_seedset('b65') == _seedset('full'))
   and len(_seedset('b65')) == _Rr['n'] and len(_seedset('full')) == _Cc['n'],
   '(5) l197.reference.same_seeds')
ck(_Rr['chopped_k'] == _Rr['fast_k'] == _Rr['n'] and _Cc['fast_k'] == 0
   and REFn['fast_diff']['diff'] == 1.0 and REFn['fast_diff']['ci95'][0] > .98,
   '(5) "structured in every seed" / the reference-minus-closure contrast')
_others = [a for a in LFn if a != 'b65']
ck(max(abs(LFn[a][c] / LFn[a]['n'] - LFn[b][c] / LFn[b]['n'])
       for a in _others for b in _others for c in ('chopped_k', 'fast_k')) < 1.0
   == REFn['fast_diff']['diff'],
   '(5) "Adding the projectors is the largest effect in this paper": a '
   'contrast between two networks that both hold the projectors reaches the '
   'maximum too')
_car_ref = REFn['carrier']
ck(REFn['base']['chopped_mean'] < _car_ref['chopped_mean'] < _Rr['chopped_mean']
   and near(REFn['carrier_below_reference'],
            _Rr['chopped_mean'] - _car_ref['chopped_mean'], 1e-9)
   and REFn['carrier_below_reference'] > .2
   and _car_ref['fast_k'] < _car_ref['n']
   and near(REFn['carrier_above_base'],
            _car_ref['chopped_mean'] - REFn['base']['chopped_mean'], 1e-9),
   '(5) "between the base and the baseline network ... a partial recovery, '
   'not a transition beyond it"')
ck((REFn['super_meanR_min'], REFn['super_kR_min'])
   == (_BDn['super_meanR_min'], _BDn['super_kR_min'])
   and _car_ref['chopped_mean'] >= REFn['super_meanR_min']
   and _Rr['chopped_mean'] - REFn['super_meanR_min'] > .3,
   '(5) "The band\'s floor ... sits far below that level"')
print('(5) L197 (stage 8): Table 5 = 6 networks x 3 arms == the stored cells, '
      'registered super rule re-applied per cell; contrast holds in sets %s and '
      'summed (%d/%d vs base %d, twin %d), does NOT hold in set %d (base %d, '
      'twin %d, carrier %d of 16); null centre %+.3f [%+.3f, %+.3f] over 16 '
      'seeds, %d of %d arms above the base; reference minus closure %+.3f '
      '[%+.3f, %+.3f] (Newcombe), carrier %.3f between base %.3f and reference '
      '%.3f'
      % (_holds, _Pn['carrier']['kR'], _Pn['carrier']['n'], _Pn['base']['kR'],
         _Pn['twin']['kR'], JTn['adverse_set'], _ad['base_kR'], _ad['twin_kR'],
         _ad['carrier_kR'], _m, _m - _hf, _m + _hf, NCn['n_above'], NCn['n'],
         REFn['fast_diff']['diff'], *REFn['fast_diff']['ci95'],
         _car_ref['chopped_mean'], REFn['base']['chopped_mean'],
         _Rr['chopped_mean']))
# ---- residue fold (stage 9): the calibration echo and the formatting pass ---
import collections as _col9
if STAGE >= 9:
    _e9 = {e['id']: e for e in TXT.EDITS if e['stage'] == 9}
    _fmt9 = sorted(k for k in _e9 if '-fmt-' in k)
    ck(len(_e9) == 16 and len(_fmt9) == 12 and all(e['kind'] == 'rep'
                                                   for e in _e9.values()),
       '(5) stage 9 is not the sixteen declared replacements')
    _abs9 = re.sub(r'\s+', ' ', F.render(_e9['E60-abstract-yardstick']['new'], nums))
    _dis9 = re.sub(r'\s+', ' ', F.render(_e9['E61-discussion-yardstick']['new'], nums))
    _R9, _B9, _C9 = REFn['reference'], REFn['base'], REFn['carrier']
    # "without the descending neurons that receive no cord input the model
    # scores k of n" / "Before they are added the network is structured in
    # every seed": the reference pool IS the network before the pure
    # projectors, and it is structured in every seed on both readouts
    ck(_R9['code'] == 'b65' and _R9['chopped_k'] == _R9['fast_k'] == _R9['n']
       and SUB['n_new'] - SUB['n_old'] == SUB['dn_new'] > 0
       and 'receive no cord input the model scores %d of %d' % (_R9['chopped_k'], _R9['n']) in _abs9
       and 'structured in every seed (%d of %d' % (_R9['chopped_k'], _R9['n']) in _dis9,
       '(5) stage 9: "the model scores k of n" / "structured in every seed"')
    # "a partial rescue toward that level ..., not a transition beyond it":
    # the carrier-removed pool lies strictly between the base and the
    # reference, on the canonical pooled seeds both sentences name
    ck(_C9['code'] == 'cutng25' and _B9['code'] == 'cutwA'
       and _B9['chopped_mean'] < _C9['chopped_mean'] < _R9['chopped_mean']
       and _C9['chopped_k'] < _C9['n']
       and all(x in t for t in (_abs9, _dis9)
               for x in ('partial rescue', 'not a transition beyond it'))
       and 'pooled mean duty %s against %s' % (F.fmt(_C9['chopped_mean'], 'f3'),
                                              F.fmt(_R9['chopped_mean'], 'f3')) in _abs9
       and 'between the base (%s)' % F.fmt(_B9['chopped_mean'], 'f3') in _dis9,
       '(5) stage 9: the partial-rescue reading is not what the pools say')
    ck('flip' not in _abs9 and 'transition' not in
       _abs9.replace('not a transition beyond it', ''),
       '(5) stage 9: the abstract still words the result as a flip or a '
       'transition')
    ck(_abs9 in re.sub(r'\s+', ' ', body) and _dis9.split('(\u00a72.1). ', 1)[1].strip()
       in re.sub(r'\s+', ' ', body[body.index('## 5. Discussion'):
                                   body.index('## 6. Data & code')]),
       '(5) stage 9: the calibration sentences are not in the abstract and '
       'in the Discussion of the built body')
    # the formatting edits are de-emphasis only
    _DIG9 = lambda t: _col9.Counter(x.rstrip(',') for x in _DIG.findall(t))
    _KEY9 = lambda t: sorted(re.findall(r'\[[a-z][a-z0-9_.]*(?:,\s+[a-z][a-z0-9_.]*)*\]',
                                       re.sub(r'\s+', ' ', t)))
    _REMOVED9 = {   # the only digit runs a formatting edit may drop, and why
        'E71-fmt-twin-ranks': {'1110': 1, '319': 1},   # each cell id was printed twice
        'E77-fmt-sustain': {'25': 1},                  # the bare code "25p"
        'E78-fmt-gain-grid': {'25': 3},                # the code "cutng25", three times
    }
    _NOTATION9 = {'XOR', 'NOISE', 'DN', 'CI'}          # terms and symbols, not emphasis
    _caps_gone = 0
    for _id in _fmt9:
        _o, _n = _e9[_id]['old'], F.render(_e9[_id]['new'], nums)
        _do, _dn = _DIG9(_o), _DIG9(_n)
        ck(not (_dn - _do) and dict(_do - _dn) == _REMOVED9.get(_id, {}),
           '(5) %s: a formatting edit moved a number (added %s, removed %s)'
           % (_id, dict(_dn - _do), dict(_do - _dn)))
        ck(_KEY9(_o) == _KEY9(_n), '(5) %s: a formatting edit moved a ledger key' % _id)
        _co = set(re.findall(r'\b[A-Z]{2,}(?:[- ][A-Z]{2,})*\b', _o))
        _cn = set(re.findall(r'\b[A-Z]{2,}(?:[- ][A-Z]{2,})*\b', _n))
        ck(_cn <= _NOTATION9 and _cn <= _co and len(_co - _cn) >= 1,
           '(5) %s: capitalised emphasis left in, or none removed: %s'
           % (_id, sorted(_cn - _NOTATION9)))
        _caps_gone += len(_co - _cn)
    ck(re.findall(r'(?m)^### (2\.\d+|3\.\d+) ', body) ==
       re.findall(r'(?m)^### (2\.\d+|3\.\d+) ', F.build_body(nums, upto=8)),
       '(5) stage 9 renumbered or restructured a Results / Methods subsection')
    print('(5) residue fold (stage 9): yardstick reading re-derived for the '
          'abstract and the Discussion (reference %d of %d, carrier %.3f between '
          'base %.3f and reference %.3f); %d formatting edits are de-emphasis '
          'only (%d capitalised tokens gone, keys identical, no digit run '
          'added, removed runs == the declared code / id repeats); subsection '
          'headings unchanged' % (_R9['chopped_k'], _R9['n'], _C9['chopped_mean'],
                                  _B9['chopped_mean'], _R9['chopped_mean'],
                                  len(_fmt9), _caps_gone))
# L190b PIN UPDATE (2026-11-21; receipt in LANE-LOG).  OLD (stage 6, the master
# fold's finalization): numbers.json 592f7680796e..., l183_text.py
# d1d8e0735bf1..., l183_fold.py 698922e3b836..., built body e62c81f6f5cc....
# NEW: the stage-7 values below.  REASON: the owner-directed follow-up adds
# six l190.* keys (every pre-existing key byte-identical: l174 (7)), four
# declared edits and one table builder.  The pins are re-set, not loosened:
# same four files, same whole-file equality.
# L197 PIN UPDATE (2026-11-21; receipt in LANE-LOG + banc/l197_worklog.md).
# OLD (stage 7, the L190b follow-up): numbers.json 464e5261317f6fd3...,
# l183_text.py 0af399b5aa46f6f3..., l183_fold.py 360e61c23c651843..., built
# body 8c8db0d49dd6f00c....  NEW: the stage-8 values below.  REASON: the
# owner-directed fourth-round repairs add five keys (every pre-existing key
# byte-identical: l174 (7)), eleven declared edits and one table builder.
# The pins are re-set, not loosened: same four files, same whole-file equality.
# RESIDUE-FOLD PIN UPDATE (2026-11-21 evening; receipt in LANE-LOG +
# banc/residue_worklog.md).  OLD (stage 8, the L197 repairs): l183_text.py
# 22ec57a34935180b..., built body 1863b3cd1325e52a....  NEW: the stage-9
# values below.  REASON: the owner-directed residue fold adds sixteen declared
# edits (no key, no table builder).  UNCHANGED and still pinned at their
# stage-8 values: numbers.json c8f0c4205e73... and l183_fold.py
# b5feccb4d589....  The pins are re-set, not loosened: same four files, same
# whole-file equality.
NUMBERS_SHA = 'c8f0c4205e732c9bfee006c05a1201877b80af25f7405c95aa65e6a27b7a3962'
# the ledger and the built body are pinned too: a later stage that edits
# either has to re-pin here deliberately (and say why in the lane log)
LEDGER_SHA = {'l183_text.py': '270e80883dac87b706b88540ef7bd27d6c814d442a03f1ed7c032e2f85f3e7f4',
              'l183_fold.py': 'b5feccb4d58986ea2635d8a4f0fd7727feafa09ec6b60a42cc89a6511d43c277'}
BODY_SHA = '9e8c64cb4d7e751d1e148e0713dd24789b69791815e4612f84122c9d176555ba'
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

# ------------------------------------------------------------------ (7)
# L197 (stage 8): the figure layer resolves.
import subprocess  # noqa: E402
FIGS = {1: ['figures/l136_transition_law.png'],
        2: ['figures/l152_clamp_cut_grid.png', 'figures/l152_clamp_cut_grid.svg'],
        3: ['figures/l160_slowline_carrier.png', 'figures/l160_slowline_carrier.svg'],
        4: ['figures/fig4_scatter.png', 'figures/fig4_scatter.svg',
            'figures/fig4_caption.md'],
        5: ['figures/fig5_threepanel.png', 'figures/fig5_threepanel.svg',
            'figures/fig5_caption.md']}
ck('peabrain-figs/' not in body, '(7) a peabrain-figs/ path is still cited')
_cited = {int(x) for x in re.findall(r'\bFigs?\.? (\d+)', body)}
ck(_cited == set(FIGS), '(7) figures cited in the body: %s (want 1-5)'
   % sorted(_cited))
_paths = set(re.findall(r'figures/[A-Za-z0-9_]+\.(?:png|svg|md)', body))
ck(_paths <= {p for v in FIGS.values() for p in v}
   and all(FIGS[n][0] in _paths for n in FIGS),
   '(7) a cited figure path is not in the declared figure table, or a '
   "figure's file is never named: %s" % sorted(_paths))
for _n, _v in FIGS.items():
    for _p in _v:
        ck(os.path.isfile(os.path.join(HERE, _p))
           and os.path.getsize(os.path.join(HERE, _p)) > 1000,
           '(7) Fig. %d: %s is missing under paper/' % (_n, _p))
_sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
for _copy, _orig in (('figures/l136_transition_law.png', ('banc', 'l136', 'fig_l136.png')),
                     ('figures/l152_clamp_cut_grid.png', ('paper', 'fig_l152.png')),
                     ('figures/l152_clamp_cut_grid.svg', ('paper', 'fig_l152.svg')),
                     ('figures/l160_slowline_carrier.png', ('banc', 'l160', 'fig_l160.png')),
                     ('figures/l160_slowline_carrier.svg', ('banc', 'l160', 'fig_l160.svg'))):
    _o = os.path.join(LAB, *_orig)
    ck(os.path.isfile(os.path.join(HERE, _copy)) and os.path.isfile(_o)
       and _sha(os.path.join(HERE, _copy)) == _sha(_o),
       '(7) %s is not byte-identical to its lab original %s'
       % (_copy, '/'.join(_orig)))
_fv = {}
for _v in ('fig4_verify.py', 'fig5_verify.py'):
    _r = subprocess.run([sys.executable, os.path.join(HERE, 'figures', _v)],
                        capture_output=True, text=True)
    _fv[_v] = re.findall(r'checks run: (\d+)', _r.stdout)
    ck(_r.returncode == 0 and 'ALL PASS' in _r.stdout,
       '(7) paper/figures/%s does not exit 0' % _v)
print('(7) figure layer: Figs %s cited, %d cited paths all resolve under '
      'paper/, no peabrain-figs/ path left, 5 legacy files byte-identical to '
      'their lab originals, fig4_verify (%s checks) and fig5_verify (%s checks) '
      'exit 0'
      % (sorted(_cited), len(_paths), ''.join(_fv['fig4_verify.py']),
         ''.join(_fv['fig5_verify.py'])))

print()
if fails:
    print('L183 VERIFY: %d FAILURE(S)' % len(fails))
    for f in fails:
        print('  - ' + f)
    sys.exit(1)
print('L183 verify: ALL GREEN (stage %d)' % STAGE)
