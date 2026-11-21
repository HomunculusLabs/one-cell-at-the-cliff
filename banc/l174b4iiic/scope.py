#!/usr/bin/env python
"""Scope the (b4-iii-c) slice: enumerate every caps occurrence inside the
three sections this slice owns (1 Introduction / 3 Methods / 4 Limitations),
classify the live-census UNCLASSIFIED tokens found there, and print the
exact site list the emit step will consume.
"""
import json, re, pathlib, collections

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
OUT = ROOT / 'banc' / 'l174b4iiic'
cen = json.loads((OUT / 'census.json').read_text())
lines = (ROOT / 'paper' / 'DRAFT.md').read_text().split('\n')
heads = cen['headings']

SCOPE = ['## 1. Introduction', '## 3. Methods',
         '## 4. Limitations (honest, per card)']

# section line ranges (1-based inclusive)
rng = {}
for n, (ln, h) in enumerate(heads):
    end = heads[n + 1][0] - 1 if n + 1 < len(heads) else len(lines)
    rng[h] = (ln, end)
for s in SCOPE:
    print(s, rng[s], 'lines', rng[s][1] - rng[s][0] + 1)

part = json.loads((ROOT / 'banc/l174b4iii/caps_partition.json').read_text())
cls = dict(part['class'])
for b in ['B26', 'B27', 'B29', 'B30', 'B31', 'B32', 'B33', 'B34', 'B35', 'B37', 'B38']:
    cls[b] = 'KEEP_MAPPING'
cls['B1-B4'] = 'DEFER_BRANCH'

inscope = collections.Counter()
unk = collections.Counter()
unk_sites = collections.defaultdict(list)
strip_sites = []
for t, sl in cen['sites'].items():
    for ln, sec in sl:
        if sec not in SCOPE:
            continue
        c = cls.get(t, '<UNCLASSIFIED>')
        inscope[c] += 1
        if c == '<UNCLASSIFIED>':
            unk[t] += 1
            unk_sites[t].append((ln, sec))
        if c in ('STRIP_EMPHASIS', 'CLASS_LABEL_lowercase'):
            strip_sites.append((ln, t, c, sec))

print('\nin-scope class counts:', dict(inscope))
print('\nUNCLASSIFIED in scope (need fresh judgement):', sum(unk.values()),
      'occ /', len(unk), 'distinct')
for t, n in sorted(unk.items()):
    print(f'   {t:<22} x{n}  {unk_sites[t][:4]}')
    for ln, _ in unk_sites[t][:2]:
        print(f'        L{ln}: {lines[ln-1].strip()[:150]}')

print('\nSTRIP/LABEL sites in scope:', len(strip_sites))
json.dump({'scope': SCOPE, 'ranges': {s: rng[s] for s in SCOPE},
           'inscope_counts': dict(inscope), 'unclassified': dict(unk),
           'unclassified_sites': {k: v for k, v in unk_sites.items()},
           'strip_sites': strip_sites},
          open(OUT / 'scope.json', 'w'), indent=1)
print('wrote', OUT / 'scope.json')
