#!/usr/bin/env python
"""T3 literal harvest for (b4-iii-c-i): find every string literal in the six
verifier sources that overlaps an owned old form, testing overlap in BOTH
directions (the tick-213 Q2 lesson: a literal may be CONTAINED BY an edit's
old form as well as contain it).

Also reports which literals contain the surrounding draft text being edited,
so a literal that pins a whole edited sentence is caught even when the caps
token alone is a common word.
"""
import json, re, pathlib, collections

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
OUT = ROOT / 'banc' / 'l174b4iiic'
plan = json.loads((OUT / 'plan_i.json').read_text())
pre = (OUT / 'draft_pre.md').read_text().split('\n')

VERIFIERS = ['l143_verify.py', 'l149_verify.py', 'l158_verify.py',
             'l159_verify.py', 'l161_verify.py', 'l174_verify.py']

# string literals, single/double quoted, incl. triple-quoted blocks
LIT = re.compile(r'"""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\'')

lits = []
for v in VERIFIERS:
    src = (ROOT / 'paper' / v).read_text()
    for m in LIT.finditer(src):
        s = m.group(0)
        body = s.strip('"\'')
        if not body:
            continue
        line = src.count('\n', 0, m.start()) + 1
        lits.append({'file': v, 'line': line, 'body': body})
print('string literals harvested:', len(lits))

# the edited SENTENCE context for each edit: the full line, pre and post
edits_by_line = collections.defaultdict(list)
for p in plan:
    edits_by_line[p['line']].append(p)

def apply_line(i):
    ln = pre[i - 1]
    out, last = [], 0
    for p in sorted(edits_by_line[i], key=lambda q: q['col']):
        assert ln[p['col']:p['col'] + len(p['old'])] == p['old'], (i, p)
        out.append(ln[last:p['col']]); out.append(p['new'])
        last = p['col'] + len(p['old'])
    out.append(ln[last:])
    return ''.join(out)

hits = []
for L in sorted(edits_by_line):
    old_line, new_line = pre[L - 1], apply_line(L)
    toks = {p['old'] for p in edits_by_line[L]}
    for lit in lits:
        b = lit['body']
        # direction A: the literal contains a chunk of the OLD line that changes
        # direction B: an old form contains the literal
        touched = False
        for t in toks:
            if t in b and len(b) >= len(t):
                # the literal mentions the token; does it mention it as part of
                # draft text that this edit changes?
                touched = True
            if b in t:
                touched = True
        if not touched:
            continue
        # does applying the edit break this literal's presence in the draft?
        hits.append({'file': lit['file'], 'vline': lit['line'],
                     'lit': b[:160], 'draft_line': L, 'toks': sorted(toks)})

print('candidate literal/edit overlaps:', len(hits))

# the decisive test: which harvested literals are PRESENT in the pre-draft and
# ABSENT from the post-draft?
post_lines = list(pre)
for L in sorted(edits_by_line):
    post_lines[L - 1] = apply_line(L)
pre_txt, post_txt = '\n'.join(pre), '\n'.join(post_lines)

broken = []
seen = set()
for lit in lits:
    b = lit['body']
    if len(b) < 4 or (lit['file'], b) in seen:
        continue
    seen.add((lit['file'], b))
    if b in pre_txt and b not in post_txt:
        broken.append(lit)
print('\nLITERALS BROKEN BY THE SLICE:', len(broken))
for lit in broken:
    print(f"  {lit['file']}:{lit['line']}  {lit['body'][:150]!r}")

json.dump({'n_lits': len(lits), 'overlaps': len(hits),
           'broken': broken}, open(OUT / 'literals.json', 'w'), indent=1)
(OUT / 'draft_post_preview.md').write_text(post_txt)
print('\nvisible-char delta (non-space):',
      sum(1 for c in post_txt if not c.isspace()) -
      sum(1 for c in pre_txt if not c.isspace()))
print('byte delta:', len(post_txt) - len(pre_txt))
print('wrote', OUT / 'literals.json', 'and the post preview')
