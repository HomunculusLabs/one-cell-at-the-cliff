#!/usr/bin/env python
"""L174 (b4-iii-c) census: re-derive the all-caps token distribution on the
LIVE draft (post-(b4-iii-b)) and locate every occurrence by section, so the
stage can be sliced by section with a frozen, size-measured scope.

Zero rollouts. Pure string arithmetic over paper/DRAFT.md + the frozen
partition artefacts of ticks 213/214.
"""
import json, re, sys, hashlib, collections, pathlib

ROOT = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
DRAFT = ROOT / 'paper' / 'DRAFT.md'
OUT = ROOT / 'banc' / 'l174b4iiic'
OUT.mkdir(parents=True, exist_ok=True)

txt = DRAFT.read_text()
lines = txt.split('\n')
print('DRAFT sha256', hashlib.sha256(txt.encode()).hexdigest()[:16],
      'bytes', len(txt), 'lines', len(lines))

# ---- section index (## headings at top level) -------------------------------
heads = []
for i, ln in enumerate(lines):
    if re.match(r'^## ', ln):
        heads.append((i, ln.strip()))
for i, h in heads:
    print(f'  L{i+1:5d}  {h[:88]}')

def sec_of(lineno):
    """0-based line -> the heading governing it (or '<front>')."""
    cur = '<front>'
    for i, h in heads:
        if i <= lineno:
            cur = h
        else:
            break
    return cur

# ---- caps token regex: same form as tick 213's caps.py ---------------------
CAPS = re.compile(r"\b[A-Z][A-Z0-9][A-Z0-9'\-]*\b")

part = json.loads((ROOT / 'banc/l174b4iii/caps_partition.json').read_text())
amend = json.loads((ROOT / 'banc/l174b4iiib/caps_partition_amend.json').read_text())
cls = dict(part['class'])
cls.update(amend['class_after'] if isinstance(amend.get('class_after'), dict) else {})
# the amendment file stores class_after as a count in some forms; re-apply the
# documented amendment explicitly so the partition we use is unambiguous.
BATCH = ['B26', 'B27', 'B29', 'B30', 'B31', 'B32', 'B33', 'B34', 'B35', 'B37', 'B38']
for b in BATCH:
    cls[b] = 'KEEP_MAPPING'
cls['B1-B4'] = 'DEFER_BRANCH'

occ = collections.Counter()
by_sec = collections.defaultdict(collections.Counter)
sites = collections.defaultdict(list)
for i, ln in enumerate(lines):
    for m in CAPS.finditer(ln):
        t = m.group(0)
        occ[t] += 1
        s = sec_of(i)
        by_sec[s][cls.get(t, '<UNCLASSIFIED>')] += 1
        sites[t].append((i + 1, s))

unk = sorted(t for t in occ if t not in cls)
print('\ndistinct live caps tokens:', len(occ), 'occurrences:', sum(occ.values()))
print('UNCLASSIFIED (new since the tick-213 census):', len(unk))
for t in unk:
    print('   ', t, occ[t], sites[t][:3])

print('\nper-section class table (live):')
order = ['STRIP_EMPHASIS', 'CLASS_LABEL_lowercase', 'NOTATION_spell_out',
         'KEEP_PROPER', 'KEEP_CELLID', 'KEEP_ACRONYM', 'KEEP_SYMBOL',
         'KEEP_MAPPING', 'DEFER_BRANCH', 'DEFER_LANE', '<UNCLASSIFIED>']
hdr = f"{'section':<46}" + ''.join(f'{c[:9]:>11}' for c in order)
print(hdr)
tot = collections.Counter()
for s in ['<front>'] + [h for _, h in heads]:
    if s not in by_sec:
        continue
    row = by_sec[s]
    tot.update(row)
    print(f'{s[:45]:<46}' + ''.join(f'{row.get(c,0):>11}' for c in order))
print(f"{'TOTAL':<46}" + ''.join(f'{tot.get(c,0):>11}' for c in order))

json.dump({'draft_sha': hashlib.sha256(txt.encode()).hexdigest(),
           'n_distinct': len(occ), 'n_occ': sum(occ.values()),
           'occ': dict(occ),
           'unclassified': unk,
           'per_section': {k: dict(v) for k, v in by_sec.items()},
           'sites': {k: v for k, v in sites.items()},
           'headings': [[i + 1, h] for i, h in heads]},
          open(OUT / 'census.json', 'w'), indent=1)
print('\nwrote', OUT / 'census.json')
