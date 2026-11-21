#!/usr/bin/env python3
"""L159 verify (title+prose pass): sentence-length outlier scan — no >60-word sentences in the
abstract or §1 (card Verify line). Reports the top offenders either way."""
import re, pathlib

draft = (pathlib.Path.home() / 'critters/peabrain-lab/paper/DRAFT.md').read_text()
sections = {
    'abstract': draft[draft.index('## Abstract'):draft.index('## 1. Introduction')],
    'intro': draft[draft.index('## 1. Introduction'):draft.index('## 2. Results')],
}
worst = []
for name, sec in sections.items():
    # join wrapped lines; bullets are sentence-ish units; split on . ! ? followed
    # by space+capital or end — keep it simple: split on sentence enders.
    text = re.sub(r'\s+', ' ', sec)
    # strip the header itself
    text = re.sub(r'^## [^.]*? (draft|Introduction) ', ' ', text, count=1)
    sents = re.split(r'(?<=[.!?]) +', text)
    for s in sents:
        w = len(s.split())
        if w > 5:  # ignore fragments/headers
            worst.append((w, name, s[:110]))
worst.sort(reverse=True)
over = [(w, n, s) for w, n, s in worst if w > 60]
for w, n, s in worst[:8]:
    print(f'{w:3d}w [{n}] {s}')
print(f'\nSENTENCES OVER 60 WORDS: {len(over)}')
assert not over, f'{len(over)} over-length sentences: {[ (w, s[:60]) for w, _, s in over[:3] ]}'
print('L159 sentence scan: PASS (no >60-word sentences in abstract/§1)')
