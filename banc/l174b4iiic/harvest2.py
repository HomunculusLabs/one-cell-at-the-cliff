#!/usr/bin/env python
"""Second-order literal scan: the blind spots the first harvest could not see.

Three blind-spot classes, all found the hard way this tick:
  (1) ESCAPE SEQUENCES — a verifier literal written with '\\n' is not a
      substring of the draft (which has a real newline), so a presence test
      misses it. Compare whitespace-NORMALISED forms.
  (2) SECTION-SCOPED GATES — a gate that slices the draft (e.g. everything
      from '## 4. Limitations' onward) can break while the literal is still
      present WHOLE-DRAFT, because the changelog banner quotes the same
      prose. Test presence inside the EDITED SECTION RANGES, not the draft.
  (3) REGEX / TOKEN-LIST GATES — a pattern built by re.search or taken from
      a python list is not a draft-quoting string literal at all; it can only
      be found by matching the owned tokens against the verifier source.

This script reports (1) and (2); (3) is handled by the declared fixes in
repoint.py.
"""
import json, re, pathlib

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
OUT = ROOT / 'banc' / 'l174b4iiic'
pre = (OUT / 'draft_pre.md').read_text()
post = (ROOT / 'paper' / 'DRAFT.md').read_text()
cen = json.loads((OUT / 'census.json').read_text())
scope = json.loads((OUT / 'scope.json').read_text())

hl = sorted(cen['headings'])
lines_pre, lines_post = pre.split('\n'), post.split('\n')
rngs = []
for n, (ln, h) in enumerate(hl):
    end = hl[n + 1][0] - 1 if n + 1 < len(hl) else len(lines_pre)
    if h in ('## 1. Introduction', '## 4. Limitations (honest, per card)'):
        rngs.append((ln, end))
pre_sec = '\n'.join(sum([lines_pre[a - 1:b] for a, b in rngs], []))
post_sec = '\n'.join(sum([lines_post[a - 1:b] for a, b in rngs], []))
nw = lambda s: re.sub(r'\s+', ' ', s)
pre_n, post_n = nw(pre_sec), nw(post_sec)

LIT = re.compile(r'"[^"\n]*"|\'[^\'\n]*\'')
VER = ['l143_verify.py', 'l149_verify.py', 'l158_verify.py',
       'l159_verify.py', 'l161_verify.py', 'l174_verify.py']
bad = []
for v in VER:
    src = (ROOT / 'paper' / v).read_text()
    for m in LIT.finditer(src):
        raw = m.group(0)[1:-1]
        if len(raw) < 6:
            continue
        for body in {raw, raw.replace('\\n', '\n').replace('\\u2192', '\u2192')}:
            b = nw(body)
            if b and b in pre_n and b not in post_n:
                bad.append({'file': v,
                            'line': src.count('\n', 0, m.start()) + 1,
                            'lit': raw})
                break

seen, uniq = set(), []
for b in bad:
    k = (b['file'], b['lit'])
    if k not in seen:
        seen.add(k); uniq.append(b)
print('SECTION-SCOPED / ESCAPE-FORM literals broken by the slice:', len(uniq))
for b in uniq:
    print(f"  {b['file']}:{b['line']}  {b['lit'][:120]!r}")
json.dump(uniq, open(OUT / 'literals2.json', 'w'), indent=1)
print('wrote', OUT / 'literals2.json')
