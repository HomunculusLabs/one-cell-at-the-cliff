#!/usr/bin/env python
"""(b4-iii-c-i) emit: apply the 64 declared case-only edits to paper/DRAFT.md
and the 16 declared verifier-literal re-points, then write the report.

CERT-3: refuses to run unless the live draft equals draft_pre.md byte for
byte, and refuses a second run (the post-state no longer equals the freeze).
CERT-4: every edit is a parsed (line, col, old, new) tuple; the old form is
asserted present at that exact column before splicing.
T15: every edit is asserted case-only (old.lower() == new.lower()).
"""
import json, sys, pathlib, hashlib, collections

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
OUT = ROOT / 'banc' / 'l174b4iiic'
DRAFT = ROOT / 'paper' / 'DRAFT.md'
DRY = '--apply' not in sys.argv

plan = json.loads((OUT / 'plan_i.json').read_text())
pre = (OUT / 'draft_pre.md').read_text()
live = DRAFT.read_text()
assert live == pre, ('CERT-3: live draft differs from the freeze — either a '
                     'concurrent edit or a second run. Refusing.')

# ---- T15 case-only -----------------------------------------------------------
for p in plan:
    assert p['old'].lower() == p['new'].lower(), ('T15 violated', p)
assert len(plan) == 64, len(plan)

lines = pre.split('\n')
by_line = collections.defaultdict(list)
for p in plan:
    by_line[p['line']].append(p)

for L, ps in by_line.items():
    ln = lines[L - 1]
    out, last = [], 0
    for p in sorted(ps, key=lambda q: q['col']):
        assert ln[p['col']:p['col'] + len(p['old'])] == p['old'], ('CERT-4', p)
        out.append(ln[last:p['col']]); out.append(p['new'])
        last = p['col'] + len(p['old'])
    out.append(ln[last:])
    lines[L - 1] = ''.join(out)
post = '\n'.join(lines)

# ---- T7-STRONG / T15 whole-draft --------------------------------------------
assert len(post) == len(pre), (len(post), len(pre))
assert post.lower() == pre.lower(), 'T15 whole-draft: not a case-only change'
assert post != pre
sorted_pre = sorted(pre.lower())
assert sorted_pre == sorted(post.lower())

# ---- the 16 declared verifier-literal re-points -----------------------------
broken = json.loads((OUT / 'literals.json').read_text())['broken']
def retrans(body):
    """transform a literal body by the same parsed rule: it is a slice of the
    pre-draft, so locate it and read the post-draft slice back."""
    i = pre.find(body)
    assert i >= 0 and pre.find(body, i + 1) == -1 or i >= 0, body
    return post[i:i + len(body)]

repoints = []
for lit in broken:
    new = retrans(lit['body'])
    assert new.lower() == lit['body'].lower(), (lit['body'], new)
    assert new != lit['body'], lit['body']
    repoints.append({'file': lit['file'], 'old': lit['body'], 'new': new})

# de-duplicate (two verifiers may pin the same literal)
seen, rp = set(), []
for r in repoints:
    k = (r['file'], r['old'])
    if k in seen:
        continue
    seen.add(k); rp.append(r)

# DRY-RUN OWN-CATCH 1: literal NESTING. l149 pins both
# 'cutwA PARTIAL 3/16 .371' and the longer
# 'cutwA PARTIAL 3/16 .371). The f4ng-vs-f4tw', so replacing the SHORT form
# first rewrites the inside of the LONG one and the long form "vanishes".
# Re-point LONGEST FIRST: the long form's replacement already carries the
# short form's new text, and the short OLD form survives only at its own
# standalone site, so each count assert stays meaningful.
rp.sort(key=lambda r: -len(r['old']))

vsrc = {}
for r in rp:
    f = ROOT / 'paper' / r['file']
    src = vsrc.get(r['file'], f.read_text())
    n = src.count(r['old'])
    assert n >= 1, ('literal vanished', r)
    vsrc[r['file']] = src.replace(r['old'], r['new'])
    r['n_sites'] = n

print('draft edits        :', len(plan))
print('literal re-points  :', len(rp), 'in', sorted({r["file"] for r in rp}))
for r in rp:
    print(f"   {r['file']:<16} x{r['n_sites']}  {r['old'][:70]!r}")
print('byte delta         :', len(post) - len(pre))
print('visible delta      :', sum(1 for c in post if not c.isspace()) -
      sum(1 for c in pre if not c.isspace()))
print('pre  sha', hashlib.sha256(pre.encode()).hexdigest()[:16])
print('post sha', hashlib.sha256(post.encode()).hexdigest()[:16])

if DRY:
    (OUT / 'draft_post.md').write_text(post)
    print('\nDRY RUN — wrote draft_post.md only. Re-run with --apply.')
    sys.exit(0)

DRAFT.write_text(post)
for fn, src in vsrc.items():
    (ROOT / 'paper' / fn).write_text(src)
json.dump({'n_edits': len(plan), 'repoints': rp,
           'pre_sha': hashlib.sha256(pre.encode()).hexdigest(),
           'post_sha': hashlib.sha256(post.encode()).hexdigest(),
           'byte_delta': 0, 'visible_delta': 0},
          open(OUT / 'emit_report.json', 'w'), indent=1)
print('\nAPPLIED.')
