#!/usr/bin/env python3
"""L174 (b3) premise test: is reviewer I10 already satisfied by the current
draft?  Run BEFORE any edit (PREREG section 1).  No edits, no RNG."""
import json
import re
import pathlib

P = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
d = (P / 'paper/DRAFT.md').read_text()
s24 = d[d.index('### 2.4 Mechanism'):d.index('### 2.5 ')]
s38 = d[d.index('### 3.8 Preregistration'):d.index('### 3.9 Notation')]
adj = (P / 'banc/l167/ADJUDICATION.md').read_text()

out = {}

# the referee row, read from the artifact rather than from memory
row = [l for l in adj.split('\n') if l.startswith('| 10 |')]
assert len(row) == 1, 'I10 row not found'
row = row[0]
out['i10_row'] = row.strip()
assert 'rebuild \u00a72.4 on silW' in row and 'demote the identities to Methods' in row
assert '3.4k chars' in row
# the adjudication's own correction: the 3.4k came through a truncated read
assert 'truncated \u00a72.4' in adj and '2,600-char cap' in adj
out['char_quote_is_measurement_not_target'] = True

# I10a: the first substantive paragraph is the silW arm
paras = [p for p in s24.split('\n\n') if p.strip()]
first = paras[1] if paras[0].startswith('### ') or len(paras[0]) < 220 else paras[0]
out['i10a_first_para_head'] = first.strip().split('\n')[0][:90]
i10a = 'silW' in first and 'clean arm' in first
out['i10a_rebuilt_on_silW'] = bool(i10a)

# I10b: both bit-identities live in Methods §3.8 and not in §2.4
moved = ('BIT-IDENTICAL to cutng25', 'BIT-IDENTICAL to eAll')
i10b = all(m in s38 and m not in s24 for m in moved)
out['i10b_identities_in_3_8_only'] = bool(i10b)
out['i10b_detail'] = {m: {'in_3.8': m in s38, 'in_2.4': m in s24} for m in moved}

# I10c: sil24 is disclosed as non-separable
i10c = 'NO demonstrated separation' in s24 and 'untreated intact base is\n6/16' in s24
out['i10c_sil24_disclosed'] = bool(i10c)

# the sil24 cells, re-read from the source results file (not from the prose)
r137 = json.loads((P / 'banc/l137/results_l137.json').read_text())
out['sil24_cells'] = {'kR': r137['sil24']['kR'], 'meanR': r137['sil24']['meanR'],
                      'intact_full_kR': r137['table']['Ti']['full']['kR'],
                      'cutwA_b26_kR': r137['sil24']['cutwA_l135_b26']['kR']}
assert out['sil24_cells']['kR'] == 5

# P1 pins
lines = s24.split('\n')
tb = [k for k, l in enumerate(lines) if l.startswith('|')]
table = '\n'.join(lines[min(tb):max(tb) + 1])
prose = s24.replace(table, '')
tok = lambda t: re.findall(r'[\u2212+\-]?\d[\d,]*(?:\.\d+)?(?:e[\u2212+\-]?\d+)?|\.\d+', t)
pt, tt = tok(prose), set(tok(table))
out['P1'] = {'chars': len(s24), 'table_chars': len(table),
             'prose_numeric_tokens': len(pt), 'table_tokens': len(tt),
             'prose_tokens_in_table': sum(1 for x in pt if x in tt)}

lits = json.loads((P / 'banc/l174b3/lits24.json').read_text())
rest = d.replace(s24, '')
out['P2'] = {'gate_literals_in_2_4': len(lits),
             'exclusive_to_2_4': sum(1 for s in lits if s not in rest)}
out['P3_bullets_1_2'] = sum(
    1 for l in d[d.index('## 1. Introduction'):d.index('## 3. Methods')].split('\n')
    if re.match(r'^\s*[-*] ', l))

branch = 'S1_editorial_only' if (i10a and i10b and i10c) else 'S2_premise_not_satisfied'
out['branch'] = branch
(P / 'banc/l174b3/premise.json').write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(f'{k}: {v}')
print('BRANCH:', branch)
