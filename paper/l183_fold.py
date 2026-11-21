#!/usr/bin/env python3
"""L183 master fold -- the DECLARED EDIT LEDGER (data + a pure build function).

The live manuscript body (title onward) is, by construction,

    build_body(numbers.json) = edits( renumber( frozen pre-image ) )

where the frozen pre-image is the stored artifact
banc/l174b4iiic/draft_post_preview.md (the post-image the previous manuscript
stage registered by hash).  paper/l183_verify.py replays this file and
requires byte equality with paper/DRAFT.md, so

  * nothing outside a declared edit can have moved, and
  * no number in new text is hand-typed: every measurement is a placeholder
    {{key.path|format}} resolved from paper/numbers.json at build time.

This module has NO side effects on import and never writes a file.
"""
import hashlib, json, os, re, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, '..'))
PRE_PATH = os.path.join(LAB, 'banc', 'l174b4iiic', 'draft_post_preview.md')
PRE_SHA = 'cf4a654146b068588c5efa2d9336055ec11355347f26fa5fafd55421f5cc22c4'
T = '## Title'

# ----------------------------------------------------------------- numbers
ALIAS = {
    'S': 'l175.scan', 'NL': 'l175.null', 'BR': 'l175.branch',
    'CE': 'l175.census', 'ME': 'l175.meta', 'BD': 'l175.bands',
    'CT': 'l175.certs',
    'TP': 'l184.threepanel', 'DS': 'l184.design', 'Q3': 'l184.q3',
    'QR': 'l184.q3_ratios', 'Q1': 'l184.q1', 'SE': 'l184.sens',
    'AN': 'l184.anatomy',
    'B5': 'l185.base', 'R1': 'l185.r1', 'R2': 'l185.r2', 'R3': 'l185.r3',
    'M5': 'l185.meta',
    'JM': 'l186.means', 'JC': 'l186.contrasts', 'JP': 'l186.power',
    'JH': 'l186.phase',
    'A': 'l187.arms', 'AB': 'l187.base', 'C': 'l187.contrasts',
    'F': 'l187.fast', 'RL': 'l187.relay', 'GS': 'l187.gain_slopes',
    'RR': 'l187.relay_rate', 'G7': 'l187.g74914_rate', 'M7': 'l187.meta',
    'S40': 'l187.sc40_pooled',
    'PT': 'l172.paired_twin', 'P': 'l172.pooled',
    'SUB': 'l92.substrate', 'W': 'l135.weights', 'D': 'l173.defs',
    'LF': 'l183.ladder_fast',
    'EA': 'l190.arms', 'EM': 'l190.meta', 'ES': 'l190.selection',
    'ESM': 'l190.summary',
    'REF': 'l197.reference', 'NC': 'l175.null_centre',
    'JT': 'l139.contrast', 'JS': 'l139.sets', 'JG': 'l139.gains',
}
MINUS = '\u2212'
CLS = {'SUPER': 'super', 'INTERMEDIATE': 'intermediate',
       'NOT-SUPER': 'not-super', 'NOT-SUPER/PARTIAL': 'not-super (partial)'}


def resolve(nums, path):
    head = path.split('.', 1)
    if head[0] in ALIAS:
        path = ALIAS[head[0]] + ('.' + head[1] if len(head) > 1 else '')
    parts = path.split('.')
    for i in range(len(parts), 0, -1):
        key = '.'.join(parts[:i])
        if key in nums:
            v = nums[key]['v']
            for t in parts[i:]:
                v = v[int(t)] if isinstance(v, list) else v[t]
            return v
    raise KeyError(path)


def _mag(v, n, strip=True):
    s = f'{abs(v):.{n}f}'
    if strip and s.startswith('0.'):
        s = s[1:]
    return s


def _neg(v, n):
    return v < 0 and float(f'{v:.{n}f}') != 0


def fmt(v, spec):
    if spec == 'i':
        assert float(v) == int(v), v
        return str(int(v))
    if spec == 'k':
        return f'{int(v):,}'
    if spec == 'raw':
        return str(v)
    if spec == 'cls':
        return CLS[v]
    if spec == 'e':
        return f'{v:.1e}'
    if spec == 'pc0':
        return str(round(v * 100))
    if spec == 'deg0':
        return f'{abs(v):.0f}'
    m = re.fullmatch(r'([a-z]+)(\d)', spec)
    kind, n = m.group(1), int(m.group(2))
    if kind == 'f':                      # .758   (leading zero stripped)
        return (MINUS if _neg(v, n) else '') + _mag(v, n)
    if kind == 's':                      # +.351 / (minus).029
        return (MINUS if _neg(v, n) else '+') + _mag(v, n)
    if kind == 'p':                      # percent magnitude: 1.24
        return _mag(v, n, strip=False)
    if kind == 'sp':                     # signed percent: +1.24
        return (MINUS if _neg(v, n) else '+') + _mag(v, n, strip=False)
    if kind == 'm':                      # rate x 1000: 2.38
        return (MINUS if _neg(v * 1000, n) else '') + _mag(v * 1000, n, False)
    if kind == 'sm':
        return (MINUS if _neg(v * 1000, n) else '+') + _mag(v * 1000, n, False)
    if kind == 'x':                      # multiplier: 1.003
        return _mag(v, n, strip=False)
    raise ValueError(spec)


def _ci(d):
    mid = d.get('mean', d.get('value', d.get('diff')))
    lo, hi = d['ci95']
    return f"{fmt(mid, 's3')} [{fmt(lo, 's3')}, {fmt(hi, 's3')}]"


_PH = re.compile(r'\{\{([^{}]+)\}\}')


def render(tpl, nums):
    def sub(m):
        body = m.group(1)
        if body.startswith('kn:'):
            d = resolve(nums, body[3:]); return f"{d['kR']} of {d['n']}"
        if body.startswith('ks:'):
            d = resolve(nums, body[3:]); return f"{d['kR']}/{d['n']}"
        if body.startswith('ci:'):
            return _ci(resolve(nums, body[3:]))
        if body.startswith('TABLE:'):
            return TABLES[body[6:]](nums)
        path, spec = body.split('|')
        return fmt(resolve(nums, path), spec)
    return _PH.sub(sub, tpl)


def wrap(block):
    """Deterministic re-wrap of prose paragraphs at 78 columns.  Headings,
    table rows and indented (equation) lines pass through untouched."""
    out = []
    tail = block[len(block.rstrip('\n')):]
    block = block.rstrip('\n')
    for para in block.split('\n\n'):
        lines = para.split('\n')
        if any(l.startswith(('|', '#', '    ')) for l in lines):
            out.append(para)
        else:
            out.append(textwrap.fill(' '.join(l.strip() for l in lines),
                                     width=78, break_long_words=False,
                                     break_on_hyphens=False))
    return '\n\n'.join(out) + tail


# ------------------------------------------------------------------ tables
def _cell_name(c, extra=''):
    return f"{c['cell_type']}-{'L' if c['side'] == 'left' else 'R'}{extra}"


def table_scan(nums):
    S = resolve(nums, 'S'); TP = resolve(nums, 'TP')
    npair = resolve(nums, 'DS.n_cross_pairs')
    rows = ['| rank | removed cell (arm code) | sign | rate | drive | gain | '
            'chopped 0.7 Hz | continuous 1.4 Hz | cross-seed, chopped | class |',
            '|---|---|---|---|---|---|---|---|---|---|']
    order = ['cutwA'] + [f'sc{r}' for r in range(25, 59)] + ['dmA', 'dmC']
    assert sorted(order) == sorted(S) == sorted(TP), 'scan arms != panel arms'
    role = {'sc25': ', the carrier', 'sc26': ', the mass twin',
            'dmA': ', drive twin of any class',
            'dmC': ", drive twin of the carrier's class"}
    for a in order:
        c, t = S[a], TP[a]
        assert t['chopped_k'] == c['kR'] and abs(
            t['chopped_mean'] - c['meanR']) < 1.1e-3, ('panel != scan', a)  # both 3-dp
        res = (f"{c['kR']}/{c['n']} {fmt(c['meanR'], 'f3')} | "
               f"{t['fast_k']}/{c['n']} {fmt(t['fast_mean'], 'f3')} | "
               f"{t['cross_k']}/{npair} {fmt(t['cross_mean'], 'f3')} | "
               f"{CLS[c['cls']]} |")
        if a == 'cutwA':
            rows.append(f'| — | none: the base, 24-cell cut (`cutwA`) | — | — '
                        f'| — | 0 | {res}')
            continue
        rows.append(
            f"| {c['rank'] if c['rank'] else '—'} | "
            f"{_cell_name(c, role.get(a, ''))} (`{a}`) | "
            f"{'+' if c['sign'] > 0 else MINUS} | "
            f"{fmt(max(c['x_mean'], 0.0), 'f3')} | "
            f"{fmt(max(c['drive_ratio'], 0.0), 'x2')} | "
            f"{fmt(c['gain_pct'], 'sp2')}% | {res}")
    return '\n'.join(rows)


def table_rep(nums):
    S = resolve(nums, 'S'); R1 = resolve(nums, 'R1'); B5 = resolve(nums, 'B5')
    R3 = resolve(nums, 'R3')
    cell = lambda d: f"{d['kR']}/{d['n']} {fmt(d['meanR'], 'f3')}"
    rows = ['| removed cell (arm code) | gain shift | batch M | '
            'batch N, re-matched gain | batch N, base gain | '
            'pooled M + N, re-matched |',
            '|---|---|---|---|---|---|',
            f"| none: the base (`cutwA`) | 0 | {cell(S['cutwA'])} | "
            f"{cell(B5)} | same arm | "
            f"{S['cutwA']['kR'] + B5['kR']}/{S['cutwA']['n'] + B5['n']} |"]
    names = [('sc25', 'the carrier'), ('sc26', 'the mass twin'),
             ('sc27', 'edge-of-band cell, rank 27'),
             ('sc40', 'edge-of-band cell, rank 40'),
             ('dmA', 'drive twin of any class'),
             ('dmC', "drive twin of the carrier's class")]
    for a, role in names:
        r = R1[a]; p = r['pooled_b39_b40_rematched']
        assert r['gi'] == S[a]['gi']
        rows.append(
            f"| {_cell_name(S[a])}, {role} (`{a}`) | "
            f"{fmt(r['rematched']['gain_delta_pct'], 'sp2')}% | "
            f"{cell(S[a])} | {cell(r['rematched'])} | {cell(r['fixed'])} | "
            f"{p['kR']}/{p['n']} {fmt(p['meanR'], 'f3')} |")
    rows.append(
        f"| {_cell_name(R3)}, signed-current twin (`s2t`) | "
        f"{fmt(R3['gain_delta_pct'], 'sp2')}% | — | {cell(R3)} | — | — |")
    return '\n'.join(rows)


def table_null(nums):
    R2 = resolve(nums, 'R2')
    hd = ['gain shift'] + [('0' if d == 0 else fmt(d, 'sp2') + '%')
                           for d in R2['deltas_pct']]
    return '\n'.join([
        '| ' + ' | '.join(hd) + ' |',
        '|' + '---|' * len(hd),
        '| structured seeds of 16 | ' + ' | '.join(str(k) for k in R2['kR']) + ' |',
        '| mean duty | ' + ' | '.join(fmt(m, 'f3') for m in R2['meanR']) + ' |'])


def table_relay(nums):
    A = resolve(nums, 'A'); AB = resolve(nums, 'AB')
    cell = lambda d: f"{d['kR']}/{d['n']} {fmt(d['meanR'], 'f3')}"
    fast = lambda d: f"{d['k14']}/{d['n']} {fmt(d['mean14'], 'f3')}"
    rows = ['| manipulation (arm codes) | gain shift | chopped, re-matched | '
            'chopped, base gain | vs base at base gain [95% CI] | '
            '1.4 Hz, re-matched | 1.4 Hz, base gain |',
            '|---|---|---|---|---|---|---|',
            f'| none: the base (`cutwA`) | 0 | — | {cell(AB)} | — | — | '
            f'{fast(AB)} |']
    for name, rm, fx in (('carrier removed', 'sc25', 'sc25F'),
                         ('relay clamped inside the window', None, 'rsilW'),
                         ('relay removed', 'rcut', 'rcutF'),
                         ('carrier and rank-40 cell removed', 'pp', 'ppF'),
                         ('rank-40 cell removed', 'sc40', 'sc40F'),
                         ('carrier and relay removed', 'occ', 'occF')):
        codes = f'`{rm}` / `{fx}`' if rm else f'`{fx}`'
        g = fmt(A[rm]['gain_delta_pct'], 'sp2') + '%' if rm else '0 (base gain)'
        rows.append(
            f"| {name} ({codes}) | {g} | "
            f"{cell(A[rm]) if rm else '—'} | {cell(A[fx])} | "
            f"{_ci(A[fx]['vs_base'])} | {fast(A[rm]) if rm else '—'} | "
            f"{fast(A[fx])} |")
    return '\n'.join(rows)


def table_ladder(nums):
    """the cohort ladder on its canonical pools: chopped vs continuous."""
    LF = resolve(nums, 'LF'); P = resolve(nums, 'P')
    rows = ['| network or cut (arm code) | seeds | chopped 0.7 Hz | '
            'continuous 1.4 Hz | 95% Wilson, continuous |',
            '|---|---|---|---|---|']
    for arm, lab in (('b65', 'baseline network, before the projectors are added'),
                     ('full', 'closure, nothing removed'),
                     ('cutk5', 'glutamatergic control cut'),
                     ('cutng19', 'k = 19'), ('cutng23', 'k = 23'),
                     ('cutwA', 'k = 24, the base'),
                     ('cutng25p', 'k = 24 plus the mass twin'),
                     ('cutng25', 'k = 25, carrier removed'),
                     ('cutng29', 'k = 29'), ('cut58', 'k = 58'),
                     ('cutscr0', 'heaviest carrier-free cohort')):
        d = LF[arm]
        assert (d['chopped_k'], d['n']) == (P[arm]['kR'], P[arm]['n']), arm
        rows.append('| %s (`%s`) | %d | %d/%d %s | %d/%d %s | [%s, %s] |' % (
            lab, arm, d['n'], d['chopped_k'], d['n'], fmt(d['chopped_mean'], 'f3'),
            d['fast_k'], d['n'], fmt(d['fast_mean'], 'f3'),
            fmt(d['fast_lb'], 'f3'), fmt(d['fast_ub'], 'f3')))
    return '\n'.join(rows)


def table_edge(nums):
    """the single-edge cut and its count-matched sham: one batch, the same
    seeds in all four arms, every arm at its own re-matched gain."""
    EA = resolve(nums, 'EA'); ES = resolve(nums, 'ES'); SM = resolve(nums, 'ESM')
    rows = ['| manipulation (arm code) | synapses cut | gain shift | '
            'chopped 0.7 Hz | vs base [95% CI] | continuous 1.4 Hz | '
            'registered reading |',
            '|---|---|---|---|---|---|---|']
    assert sorted(d['code'] for d in EA.values()) == sorted(SM), 'edge arms'
    for lab, name in (('base', 'none: the base'),
                      ('carrier', 'carrier removed'),
                      ('edge', 'carrier-to-relay edge cut'),
                      ('sham', 'sham edge cut')):
        d = EA[lab]; s = SM[d['code']]
        assert (d['kR'], d['meanR'], d['meanmid'], d['super'], d['fingerprint']) \
            == (s['kR'], s['meanR'], s['mid'], s['SUPER'], s['fingerprint']), lab
        base = lab == 'base'
        syn = (str(ES[d['code']]['syn']) if d['code'] in ES
               else '—' if base else 'the whole cell')
        reading = 'reference' if base else '%s, %s' % (
            CLS['SUPER'] if d['super'] else CLS['NOT-SUPER'],
            'signature' if d['fingerprint'] else 'no signature')
        rows.append(
            f"| {name} (`{d['code']}`) | {syn} | "
            f"{'0' if base else fmt(d['gain_delta_pct'], 'sp3') + '%'} | "
            f"{d['kR']}/{d['n']} {fmt(d['meanR'], 'f3')} | "
            f"{'—' if base else _ci(d['vs_base'])} | "
            f"{d['kmid']}/{d['n']} {fmt(d['meanmid'], 'f3')} | {reading} |")
    return '\n'.join(rows)


def table_jitter(nums):
    """the weight-jitter ensemble, per network: the three arms of the title
    contrast with the carrier-removed arm's count difference from each
    comparator.  The row in which the contrast does not hold is printed like
    every other row."""
    JS = resolve(nums, 'JS'); JG = resolve(nums, 'JG'); JT = resolve(nums, 'JT')
    low = {'SUPER': 'super', 'KILL': 'kill', 'PARTIAL': 'partial',
           'NEUTRAL-INT': 'neutral', 'OTHER': 'other'}
    n = JT['n_seeds']
    sint = lambda v: (MINUS if v < 0 else '+' if v > 0 else '') + str(abs(v))
    cell = lambda d: f"{d['kR']}/{n} {fmt(d['meanR'], 'f3')} {low[d['cls']]}"
    rows = ['| network | base gain shift | base (`cutwA`) | '
            'base cut plus the mass twin (`cutng25p`) | carrier removed (`cutng25`) | '
            'carrier \u2212 base, seeds | carrier \u2212 twin, seeds | '
            'title contrast |',
            '|---|---|---|---|---|---|---|---|']
    assert sorted(JS) == sorted(JG) == sorted(JT['per_set']) \
        and len(JS) == JT['n_networks'] == JT['n_jitter_sets'] + 1
    for s in sorted(JS, key=int):
        b, t, c = JS[s]['cutwA'], JS[s]['cutng25p'], JS[s]['cutng25']
        p = JT['per_set'][s]
        assert p['carrier_minus_base'] == c['kR'] - b['kR'] \
            and p['carrier_minus_twin'] == c['kR'] - t['kR'], s
        assert abs(p['base_gain_delta_pct']
                   - (JG[s]['cutwA'] / JG['0']['cutwA'] - 1) * 100) < 6e-4, s
        rows.append(
            f"| {'unjittered' if s == '0' else 'jitter set ' + s} | "
            f"{'0' if s == '0' else fmt(p['base_gain_delta_pct'], 'sp2') + '%'} | "
            f"{cell(b)} | {cell(t)} | {cell(c)} | "
            f"{sint(p['carrier_minus_base'])} | {sint(p['carrier_minus_twin'])} | "
            f"{'holds' if p['holds'] else 'does not hold'} |")
    P = JT['pooled']
    pc = lambda d: f"{d['kR']}/{d['n']} {fmt(d['meanR'], 'f3')}"
    assert all(P[a]['kR'] == sum(JS[s][c]['kR'] for s in JS if s != '0')
               for a, c in (('base', 'cutwA'), ('twin', 'cutng25p'),
                            ('carrier', 'cutng25')))
    rows.append(
        f"| jitter sets 1 to {JT['n_jitter_sets']}, summed | \u2014 | "
        f"{pc(P['base'])} | {pc(P['twin'])} | {pc(P['carrier'])} | "
        f"{sint(P['carrier_minus_base'])} | {sint(P['carrier_minus_twin'])} | "
        f"\u2014 |")
    return '\n'.join(rows)


TABLES = {'scan': table_scan, 'rep': table_rep, 'null': table_null,
          'relay': table_relay, 'ladder': table_ladder, 'edge': table_edge,
          'jitter': table_jitter}

# ---------------------------------------------------------------- renumber
# old Results subsection -> new (the scan block takes 2.1-2.5).
RENUMBER = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10, 6: 11, 7: 12, 8: 13, 9: 14}


def renumber(text):
    text = re.sub(r'\u00a72\.([1-9])(?!\d)',
                  lambda m: f'\u00a72.{RENUMBER[int(m.group(1))]}', text)
    text = re.sub(r'(?m)^### 2\.([1-9]) ',
                  lambda m: f'### 2.{RENUMBER[int(m.group(1))]} ', text)
    # the one bare section pointer in the body (Limitations)
    assert text.count('gain-regime-dependent (2.5)') == 1
    return text.replace('gain-regime-dependent (2.5)',
                        'gain-regime-dependent (\u00a72.10)')


# ------------------------------------------------------------------- edits
# ('rep', old, new, wrap_new) : old occurs EXACTLY once; replaced by new.
# ('span', start, end, new, wrap_new) : [start, end) replaced; both unique.
# Anchors are written in the RENUMBERED numbering.  `reason` is the receipt.
sys.path.insert(0, HERE)
from l183_text import EDITS, CURRENT_STAGE  # noqa: E402  (the text ledger)


def pre_body():
    raw = open(PRE_PATH).read()
    assert hashlib.sha256(raw.encode()).hexdigest() == PRE_SHA, \
        'the stored pre-image moved'
    return raw[raw.index(T):]


def build_body(nums, upto=None):
    body = pre_body()
    if upto is None or upto >= 2:        # the renumber lands with stage 2
        body = renumber(body)
    for n, e in enumerate(EDITS):
        if upto is not None and e['stage'] > upto:
            continue
        new = render(e['new'], nums)
        if e.get('wrap') == 'tail':     # first paragraph is old text: keep
            head, sep, rest = new.partition('\n\n')
            new = head + sep + wrap(rest)
        elif e.get('wrap'):
            new = wrap(new)
        if e['kind'] == 'rep':
            assert body.count(e['old']) == 1, \
                (e['id'], 'anchor count', body.count(e['old']))
            body = body.replace(e['old'], new)
        else:
            assert body.count(e['start']) == 1 and body.count(e['end']) == 1, \
                (e['id'], body.count(e['start']), body.count(e['end']))
            i, j = body.index(e['start']), body.index(e['end'])
            assert i < j, e['id']
            body = body[:i] + new + body[j:]
    return body


def load_nums():
    return json.load(open(os.path.join(HERE, 'numbers.json')))


# ------------------------------------------------------- pin re-point helpers
# Used by the predecessor gates (l149 / l158 / l174).  The tick-210 rule: a
# stage that supersedes a predecessor's freeze re-points it at STORED
# artifacts and never loosens it.  The frozen checks keep certifying the body
# they were written for (the stored, hash-pinned pre-image), and the live
# body is bound to that pre-image by the byte replay below.
def pre_composite(live):
    """the live changelog banner + the stored pre-image body (title onward)."""
    return live[:live.index(T)] + pre_body()


def assert_bound(live, nums=None):
    """live body == ledger(pre-image), byte for byte.  Returns the stage."""
    nums = nums or load_nums()
    want = build_body(nums, upto=CURRENT_STAGE)
    got = live[live.index(T):]
    assert got == want, ('L183 replay: the live body is not '
                         'declared_edits(stored pre-image)')
    return CURRENT_STAGE


def authored(nums=None, upto=None):
    """[(edit id, rendered new text)] for the edits applied so far."""
    nums = nums or load_nums()
    upto = CURRENT_STAGE if upto is None else upto
    return [(e['id'], render(e['new'], nums)) for e in EDITS
            if e['stage'] <= upto]


def harvest_gone(path):
    """Every string literal a gate script asserts ABSENT (a `not in` compare,
    directly or through a loop over a literal tuple / named literal list).
    Lets a successor section re-assert the whole retired-wording set against
    newly authored text without re-typing it."""
    import ast
    tree = ast.parse(open(path).read())
    out, names = set(), {}

    def strs(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            return [n.value]
        if isinstance(n, (ast.Tuple, ast.List, ast.Set)):
            return [s for e in n.elts for s in strs(e)]
        if isinstance(n, ast.Name):
            return names.get(n.id, [])
        return []

    for n in tree.body:
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)):
            v = strs(n.value)
            if v:
                names[n.targets[0].id] = v

    def notin(c):
        return isinstance(c, ast.Compare) and any(
            isinstance(o, ast.NotIn) for o in c.ops)

    for n in ast.walk(tree):
        if notin(n) and not isinstance(n.left, ast.Name):
            out.update(strs(n.left))
        if isinstance(n, ast.For) and isinstance(n.target, ast.Name):
            for sub in ast.walk(n):
                if (notin(sub) and isinstance(sub.left, ast.Name)
                        and sub.left.id == n.target.id):
                    out.update(strs(n.iter))
    return {s for s in out if len(s.strip()) >= 6}


def returned(gone, texts):
    """retired strings that reappear in authored text (whitespace-blind)."""
    flat = [(i, re.sub(r'\s+', ' ', t)) for i, t in texts]
    return sorted((i, g) for g in gone for i, t in flat
                  if re.sub(r'\s+', ' ', g) in t)
