#!/usr/bin/env python3
"""L182 — the pooled-count DRIFT GATE (meta, zero rollouts).

The defect L172 stage (a) fixed was not a wrong number but TWO UNIONS OF
THE SAME ARM in two sections.  This gate makes that class of defect
permanently detectable: it extracts every k/n token from the draft body,
resolves it to an arm via the canonical l172.pooled table, and fails when
an arm carries two different denominators outside an explicitly declared
family-matched region.

PREREG: banc/l182/PREREG.md (written before any output was read).
Inputs are stored artifacts only; paper/DRAFT.md is READ-ONLY here (tamper
tests run on copies under banc/l182/).

Usage:
    python3 l182_driftgate.py              # live draft + the three tampers
    python3 l182_driftgate.py <draft.md>   # census one file, no tampers
"""
import json
import pathlib
import re
import sys

P = pathlib.Path(__file__).resolve().parent.parent          # peabrain-lab/
DRAFT = P / 'paper' / 'DRAFT.md'
STATS = P / 'banc' / 'l172' / 'stats.json'
OUT = P / 'banc' / 'l182'

# ---------------------------------------------------------------- classifier
POOLED = json.loads(STATS.read_text())['pooled']
CANON_N = {a: v['n'] for a, v in POOLED.items()}
CANON_K = {a: (v['kR'], v['kL']) for a, v in POOLED.items()}
BATCHMULT = {16 * i for i in range(1, 11)}                  # 1..10 batches

TOKEN = re.compile(r'(\d{1,4})\s*(?:/|of)\s*(\d{1,4})')

# Arm phrases: the §2.14 table's own code names + its parenthetical reader
# labels + the prose aliases the body uses.  'carrier' excludes
# 'carrier-free' (that gloss belongs to the scramble cohort arm).
ARM_PHRASES = {
    'b65':      [r'`b65`', r'\bb65\b', r'un-cut baseline'],
    'full':     [r'`full`', r'intact closure'],
    'cutk5':    [r'`cutk5`', r'\bcutk5\b', r'glut control'],
    'cutng19':  [r'`cutng19`', r'\bcutng19\b', r'k ?= ?19'],
    'cutng23':  [r'`cutng23`', r'\bcutng23\b', r'k ?= ?23'],
    'cutng29':  [r'`cutng29`', r'\bcutng29\b', r'k ?= ?29'],
    'cut58':    [r'`cut58`', r'\bcut58\b', r'k ?= ?58'],
    'cutwA':    [r'`cutwA`', r'\bcutwA\b', r'k ?= ?24', r'\bbase\b'],
    'cutng25':  [r'`cutng25`(?!p)', r'\bcutng25\b(?!p)', r'k ?= ?25',
                 r'\bcarrier\b(?!-free)'],
    'cutng25p': [r'`cutng25p`', r'\bcutng25p\b', r'twin-XOR', r'\btwin\b'],
    'silW':     [r'`silW`', r'\bsilW\b', r'\bclamp\b'],
    'eMotTop5': [r'`eMotTop5`', r'\beMotTop5\b', r'5 heavy', r'heavy motor edges'],
    'eMotBot5': [r'`eMotBot5`', r'\beMotBot5\b', r'5 light', r'light motor edges'],
    'eOutMot':  [r'`eOutMot`', r'\beOutMot\b', r'10 motor edges'],
    'cutscr0':  [r'`cutscr0`', r'\bcutscr0\b', r'scramble'],
}
# ADDENDUM 2: two tiers.  CODE = the arm's own code token (backticked or
# bare, plus the clamp arm's first-batch name sil1110); GLOSS = prose
# aliases.  A label column resolves on CODE hits alone when it has any.
CODE_N = {'b65': 1, 'full': 1, 'cutk5': 2, 'cutng19': 2, 'cutng23': 2,
          'cutng29': 2, 'cut58': 2, 'cutwA': 2, 'cutng25': 2,
          'cutng25p': 2, 'silW': 3, 'eMotTop5': 2, 'eMotBot5': 2,
          'eOutMot': 2, 'cutscr0': 2}
ARM_PHRASES['silW'].insert(2, r'sil1110')
_PAT = {a: re.compile('|'.join(p)) for a, p in ARM_PHRASES.items()}
_CODE = {a: re.compile('|'.join(p[:CODE_N[a]])) for a, p in ARM_PHRASES.items()}

# Declared family-matched regions: heading substring -> reason.  Enumerated
# from the draft (PREREG: the card names three; §2.1 is the fourth candidate).
EXEMPT_REGIONS = {
    '### 2.1': 'single-cell scan: 34 deletions on ONE shared batch '
               '(family-matching is the design)',
    '### 2.2': 'replication table: per-batch by design — the section IS the '
               'batch-to-batch replication claim (region NOT in the card)',
    '### 2.7': 'scramble cohort table: seven cohorts + base on the same 3 '
               'fresh batches (family-matched by design, card item (i))',
    '### 2.10': 'gain-ensemble cells: per-jitter-set by construction, must '
                'NOT be pooled (card item (ii))',
    '### 2.12': 'rewire/hom/swap arms: 2 batches each, not yet canonical '
                '(card item (iii))',
}
# Arms whose family-matched quote additionally requires the canonical count
# to appear in the body (the reconciliation requirement, D3).
RECONCILE = ['cutscr0']


# ADDENDUM 4: arms the body quotes POOLED counts for that are NOT in
# l172.pooled at all.  A row whose label leads with one of these is
# UNCANONICAL: its tokens are censused for L181, never attributed to a
# canonical arm ('eAll (cutwA base)' is the eAll manipulation, not the base).
NONCANON = re.compile(r'`?(eAll|eOutInt|eIn|eMotIn|se0|vol1110|sil24|'
                      r'sc\d\d|scr\d|hom|swap|rewire)\b')


def body_of(text):
    """Body = '## Title' .. '## References', exclusive of the banner."""
    lines = text.split('\n')
    try:
        lo = next(i for i, l in enumerate(lines) if l.startswith('## Title'))
        hi = next(i for i, l in enumerate(lines) if l.startswith('## References'))
    except StopIteration:
        raise SystemExit('scope boundaries missing')
    return lines, lo, hi


def arms_in(s, pats=None):
    """Deduped arm hits in offset order (first occurrence per arm)."""
    hits = sorted((m.start(), a) for a, p in (pats or _PAT).items()
                  for m in p.finditer(s))
    out = []
    for _, a in hits:
        if a not in out:
            out.append(a)
    return out


def units(lines, lo, hi):
    """Yield (lineno, heading, unit_text, is_row)."""
    head = ''
    for i in range(lo, hi):
        l = lines[i]
        if l.startswith('#'):
            head = l.strip()
            continue
        if l.lstrip().startswith('|'):
            yield i + 1, head, l, True
        else:
            for sent in re.split(r'(?<=[.;:])\s+', l):
                if sent.strip():
                    yield i + 1, head, sent, False


def census(path):
    text = pathlib.Path(path).read_text()
    lines, lo, hi = body_of(text)
    body = '\n'.join(lines[lo:hi])
    resolved, unresolved, ignored, noncanon = [], [], [], []

    for ln, head, unit, is_row in units(lines, lo, hi):
        toks = [(int(m.group(1)), int(m.group(2)), m.start())
                for m in TOKEN.finditer(unit)]
        if not toks:
            continue
        seed = [t for t in toks if t[1] in CANON_N.values() or t[1] in BATCHMULT]
        ignored += [t[1] for t in toks if t not in seed]
        if not seed:
            continue
        if is_row:
            col1 = unit.split('|')[1] if unit.count('|') >= 2 else unit
            nc = NONCANON.search(col1)
            code = arms_in(col1, _CODE)
            if nc and (not code or nc.start() < min(
                    m.start() for a in code for m in [_CODE[a].search(col1)]
                    if m)):
                noncanon += [(ln, head, t[0], t[1], nc.group(1),
                              unit.strip()[:100]) for t in seed]
                continue
            # ADDENDUM 3a: in a label column the FIRST code token is the
            # row's SUBJECT ('sil1110 on cutwA base' is the clamp arm, not
            # the base); only the GLOSS tier order-pairs (contrast rows).
            arms = [code[0]] if code else arms_in(col1)
        else:
            arms = arms_in(unit)
        # ADDENDUM 1: prose co-occurrence is UNSOUND (a sentence names an arm
        # as a comparator), so only TABLE ROWS resolve; prose is diagnostic.
        if not is_row or not arms:
            unresolved += [(ln, head, t[0], t[1], unit.strip()[:90]) for t in seed]
            continue
        if len(arms) == len(seed) and len(arms) > 1:
            pairs = list(zip(arms, seed))
        else:
            pairs = [(arms[0], t) for t in seed]
        for a, (k, n, _o) in pairs:
            resolved.append({'arm': a, 'k': k, 'n': n, 'line': ln,
                             'head': head, 'row': is_row,
                             'pooled_marked': 'pooled' in
                             unit[max(0, _o - 14):_o].lower(),
                             'cls': 'CANON' if n == CANON_N[a] else
                                    ('BATCH' if n in BATCHMULT else 'OTHERCANON'),
                             'text': unit.strip()[:110]})
    return resolved, unresolved, ignored, body, noncanon


def gate(path, verbose=True):
    resolved, unresolved, ignored, body, noncanon = census(path)
    rep = {'path': str(path), 'n_noncanon_pooled':
           sum(1 for x in noncanon if 'pooled' in x[5].lower()),
           'noncanon': noncanon, 'n_resolved': len(resolved),
           'n_unresolved': len(unresolved), 'ignored_denoms':
           sorted(set(ignored))}

    # ---- D4 well-posedness
    d4 = []
    if set(CANON_N.values()) & BATCHMULT:
        d4.append('CANON_N intersects BATCHMULT')
    for a, pat in _PAT.items():
        if not pat.search(body):
            d4.append(f'arm phrase set vacuous: {a}')
    if not resolved:
        d4.append('no token resolved (vacuous gate)')
    rep['D4'] = {'pass': not d4, 'detail': d4}

    # ---- D1 / D2 on CANON-class cells
    byarm = {}
    for r in resolved:
        if r['cls'] in ('CANON', 'OTHERCANON'):
            byarm.setdefault(r['arm'], set()).add(r['n'])
    d1 = {a: sorted(ns) for a, ns in byarm.items() if len(ns) > 1}
    rep['D1'] = {'pass': not d1, 'detail': d1}

    CANON_TABLE = '### 2.14'
    d2 = [{'arm': r['arm'], 'cell': f"{r['k']}/{r['n']}", 'canon': CANON_N[r['arm']],
           'line': r['line'], 'head': r['head'], 'text': r['text']}
          for r in resolved
          if r['cls'] == 'OTHERCANON'
          or (r['head'].startswith(CANON_TABLE) and r['n'] != CANON_N[r['arm']])]
    rep['D2'] = {'pass': not d2, 'detail': d2}

    # ---- D3 (ADDENDUM 3b): a POOLED-MARKED token must be canonical.
    # Per-batch cells are admissible anywhere (the sections are built on
    # per-batch class reads); what may not drift is a cell the draft itself
    # calls pooled.  The region list below is kept as a DIAGNOSTIC census.
    d3, used = [], set()
    for r in resolved:
        if r['cls'] == 'BATCH':
            reg = next((h for h in EXEMPT_REGIONS if r['head'].startswith(h)),
                       None)
            used.add(reg or r['head'][:9])
            if r['pooled_marked']:
                d3.append({'arm': r['arm'], 'cell': f"{r['k']}/{r['n']}",
                           'canon': CANON_N[r['arm']], 'line': r['line'],
                           'head': r['head'], 'text': r['text']})
    vac = [h for h in EXEMPT_REGIONS if h not in used]
    recon = []
    for a in RECONCILE:
        kR, _ = CANON_K[a]
        n = CANON_N[a]
        if not (f'{kR}/{n}' in body or f'{kR} of {n}' in body):
            recon.append(f'{a}: canonical {kR}/{n} absent from body')
    rep['D3'] = {'pass': not d3 and not recon, 'uncovered': d3,
                 'vacuous_regions': vac, 'reconcile_fail': recon,
                 'regions_used': sorted(used)}

    rep['PRIMARY'] = rep['D1']['pass'] and rep['D2']['pass'] and rep['D4']['pass']
    rep['ALL'] = rep['PRIMARY'] and rep['D3']['pass']

    if verbose:
        print(f"--- l182 drift gate on {path}")
        print(f"    uncanonical-arm rows: {len(noncanon)} tokens, "
              f"{rep['n_noncanon_pooled']} of them POOLED-marked")
        print(f"    resolved {len(resolved)}  unresolved {len(unresolved)}  "
              f"ignored denoms {rep['ignored_denoms']}")
        for cell in ('D1', 'D2', 'D3', 'D4'):
            print(f"    {cell}: {'PASS' if rep[cell]['pass'] else 'FAIL'}  "
                  f"{json.dumps({k: v for k, v in rep[cell].items() if k != 'pass'})[:420]}")
        print(f"    PRIMARY {rep['PRIMARY']}  ALL {rep['ALL']}")
    return rep, resolved, unresolved


TAMPERS = [
    ('T1_perbatch_carrier', '| cutng25 (carrier, k=25) | 203/210 |',
     '| cutng25 (carrier, k=25) | 124/128 |', 'D2'),
    ('T2_second_union_clamp', '| silW (carrier clamp on cut base) | 78/98 |',
     '| silW (carrier clamp on cut base) | 78/258 |', 'D1'),
    # T3 (re-registered): D3's reconciliation cell claims the canonical count
    # appears SOMEWHERE in the body, so a one-site deletion cannot test it --
    # the first attempt removed the §1 prose clause while the §2.7 table cell
    # still carried 41/50 and D3 stayed green (a correct non-failure).  The
    # tamper must therefore remove every canonical mention of the arm.
    # ...so T3 is a TWO-SITE tamper (table cell + prose clause).
    ('T3_drop_reconciliation', [('41/50 .623', '.623'), ('41 of 50', '50')],
     None, 'D3'),
]

if __name__ == '__main__':
    if len(sys.argv) > 1:
        gate(sys.argv[1])
        raise SystemExit(0)

    OUT.mkdir(exist_ok=True)
    live, res, unres = gate(DRAFT)
    src = DRAFT.read_text()
    tam = {}
    for name, old, new, cell in TAMPERS:
        edits = old if isinstance(old, list) else [(old, new)]
        txt = src
        for o, n in edits:
            assert txt.count(o) >= 1, f'{name}: anchor {o!r} absent'
            txt = txt.replace(o, n)
        p = OUT / f'tamper_{name}.md'
        p.write_text(txt)
        print()
        r, _, _ = gate(p)
        turned = not r[cell]['pass']
        others = [c for c in ('D1', 'D2', 'D3', 'D4')
                  if c != cell and r[c]['pass'] != live[c]['pass']]
        tam[name] = {'target': cell, 'target_red': turned,
                     'collateral': others, 'all': r['ALL']}
        print(f"    TAMPER {name}: target {cell} red = {turned}; "
              f"collateral changes {others}")
        assert turned, f'{name} did not turn {cell} red — gate is vacuous'
        p.unlink()

    rep = {'live': live, 'tampers': tam,
           'canon_n': CANON_N, 'exempt_regions': EXEMPT_REGIONS,
           'resolved': res, 'unresolved': unres,
           'draft_sha_note': 'see run.out'}
    (OUT / 'gate_l182.json').write_text(json.dumps(rep, indent=1))
    print(f"\n    tampers 3/3 turned their named cell red")
    print(f"    LIVE: PRIMARY {live['PRIMARY']}  ALL {live['ALL']}")
    raise SystemExit(0 if live['PRIMARY'] else 1)
