#!/usr/bin/env python
"""(b4-iii-c-i) plan: §1 Introduction + §4 Limitations only.

Premise finding that drives the slice: tick 213's partition is TOKEN-level,
but several tokens are MODEL SYMBOLS in §3 Methods (BG, DT, TAU, WIN inside
the state equation and the parameter table) and EMPHASIS in prose, and one
token is split by position in §3 alone (BY: "CC BY 4.0" the licence name vs
"BY CONSTRUCTION" the emphasis). §3 therefore needs an OCCURRENCE-level
judgement plus protection of the §3.7 mapping block, which is a different
KIND of job from a prose de-emphasis. This slice takes the two pure-prose
sections; §3 becomes (b4-iii-c-ii), §2 Results (b4-iii-c-iii).

Deterministic transform rule:
  an owned occurrence (STRIP_EMPHASIS / CLASS_LABEL_lowercase / the declared
  OF) is replaced by its lowercase form, EXCEPT when it is sentence-initial
  (the token starts the line, or the preceding non-space characters end in
  '.', ':', or the line is a heading), in which case only the first letter
  is kept uppercase.
"""
import json, re, pathlib, collections

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
OUT = ROOT / 'banc' / 'l174b4iiic'
cen = json.loads((OUT / 'census.json').read_text())
lines = (ROOT / 'paper' / 'DRAFT.md').read_text().split('\n')

SCOPE = ['## 1. Introduction', '## 4. Limitations (honest, per card)']
part = json.loads((ROOT / 'banc/l174b4iii/caps_partition.json').read_text())
cls = dict(part['class'])
OWNED = {'STRIP_EMPHASIS', 'CLASS_LABEL_lowercase'}
# declared occurrence-level additions for THIS slice (§4 only)
DECLARED_STRIP = {('OF', 1424)}

CAPS = re.compile(r"\b[A-Z][A-Z0-9][A-Z0-9'\-]*\b")
heads = {h: ln for ln, h in cen['headings']}
rng = {}
hl = sorted(cen['headings'])
for n, (ln, h) in enumerate(hl):
    end = hl[n + 1][0] - 1 if n + 1 < len(hl) else len(lines)
    rng[h] = (ln, end)

plan = []
for s in SCOPE:
    a, b = rng[s]
    for i in range(a, b + 1):          # 1-based, heading line included
        ln = lines[i - 1]
        for m in CAPS.finditer(ln):
            t = m.group(0)
            c = cls.get(t, '<UNCLASSIFIED>')
            owned = c in OWNED or (t, i) in DECLARED_STRIP
            if not owned:
                continue
            pre = ln[:m.start()].rstrip()
            # OWN-CATCH (post-apply, rule fixed here): LINE-START is NOT
            # SENTENCE-START in a hard-wrapped draft. "...over noise seeds of
            # one / FIXED NETWORK — one graph" wraps mid-sentence, so the old
            # `pre == ''` clause capitalised "Fixed network" wrongly. A
            # sentence starts only when the preceding non-space text on the
            # line ends in '.' or ':', or when the token opens a line whose
            # PREVIOUS line is blank, a heading, or itself ends in '.' or ':'.
            if pre != '':
                sent_init = pre.endswith(('.', ':'))
            else:
                prev = lines[i - 2].rstrip() if i >= 2 else ''
                sent_init = (prev == '' or prev.startswith('#') or
                             prev.endswith(('.', ':')))
            new = t.lower()
            if sent_init:
                new = t[0] + t[1:].lower()
            plan.append({'line': i, 'col': m.start(), 'old': t, 'new': new,
                         'cls': c, 'sent_init': bool(sent_init), 'sec': s,
                         'prev': (lines[i - 2].rstrip()[-40:] if i >= 2 else '')})

print('owned occurrences in slice:', len(plan))
cc = collections.Counter(p['cls'] for p in plan)
print('by class:', dict(cc))
print('sentence-initial (first letter kept):',
      sum(1 for p in plan if p['new'][0].isupper()))
print()
for p in plan:
    mark = '^' if p['new'][0].isupper() else ' '
    print(f"{mark} L{p['line']:5d} {p['old']:<20} -> {p['new']:<20} | "
          f"{lines[p['line']-1].strip()[:92]}")

json.dump(plan, open(OUT / 'plan_i.json', 'w'), indent=1)
print('\nwrote', OUT / 'plan_i.json')
