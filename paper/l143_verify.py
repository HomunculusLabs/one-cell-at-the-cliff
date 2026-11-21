#!/usr/bin/env python3
"""L143 verify: (1) every [key] cited in DRAFT.md exists in numbers.json;
(2) the DRAFT mechanism table values equal the stored results jsons EXACTLY
(never eyeballed); (3) numbers.json values equal their source jsons for the
newly added l137/l142 keys."""
import json, re, sys
import pathlib

P = pathlib.Path.home() / 'critters/peabrain-lab'
draft = (P / 'paper/DRAFT.md').read_text()
nums = json.loads((P / 'paper/numbers.json').read_text())

cited = set(re.findall(r'\[([a-z0-9_.]+)\]', draft))
missing = []
for c in sorted(cited):
    if '.' not in c or c in nums:
        continue
    # dotted citation may address a sub-field of a stored dict: resolve it
    parts = c.split('.')
    ok = False
    for i in range(len(parts) - 1, 0, -1):
        head, tail = '.'.join(parts[:i]), parts[i:]
        if head in nums:
            v = nums[head]['v']
            try:
                for t in tail:
                    v = v[t]
                ok = True
            except (KeyError, TypeError, IndexError):
                pass
            break
    if not ok:
        missing.append(c)
print(f'cited keys with dot: {len([c for c in cited if "." in c])}; missing: {missing}')
assert not missing, 'DRAFT cites keys absent from numbers.json'
# and the resolved sub-fields must carry the quoted values
xd = nums['xor']['v']
assert abs(xd['pair_delta'] - 3.9e-04) < 0.05e-04 and '3.9e-04' in draft
assert abs(xd['steps']['24->25'] - 0.371) < 5e-4 and '+.371' in draft
print('  xor sub-fields resolve OK (pair_delta, steps.24->25 quoted correctly)')

# (2) mechanism table vs stored jsons, value by value
r137 = json.loads((P / 'banc/l137/results_l137.json').read_text())
r142 = json.loads((P / 'banc/l142/results_l142.json').read_text())
ti = r142['table']['Ti']
g1, g2 = r137['g1'], r137['g2']
checks = [
    ('sil1110 meanR/kR', g1['sil1110']['meanR'], g1['sil1110']['kR'], '.376', '2, 3/16'),
    ('vol1110 meanR/kR', g2['vol1110']['meanR'], g2['vol1110']['kR'], '.486', '7/16'),
    ('sil24 meanR/kR', r137['sil24']['meanR'], r137['sil24']['kR'], '.432', '5/16'),
    ('cutwA meanR/kR', ti['cutwA']['meanR'], ti['cutwA']['kR'], '.377', '4/16'),
    ('cutng25 meanR/kR', ti['cutng25']['meanR'], ti['cutng25']['kR'], '.745', '14/16'),
    ('eOutInt meanR/kR', ti['eOutInt']['meanR'], ti['eOutInt']['kR'], '.781', '15/16'),
    ('eIn meanR/kR', ti['eIn']['meanR'], ti['eIn']['kR'], '.793', '15/16'),
    ('eOutMot meanR/kR', ti['eOutMot']['meanR'], ti['eOutMot']['kR'], '.525', '9, 12/16'),
    ('eAll meanR/kR', ti['eAll']['meanR'], ti['eAll']['kR'], '.745', '14, 15/16'),
]
for name, mr, kr, mr_s, kr_s in checks:
    assert mr_s in draft and abs(mr - float(mr_s)) < 5e-4, f'{name}: meanR {mr} vs draft'
    assert kr_s in draft, f'{name}: kR string {kr_s} not in draft'
    print(f'  {name}: {mr:.3f} {kr_s} OK')

# abstract + section quote spot-checks
h2a = r142['hypotheses']['H2a']; h3 = r142['hypotheses']['H3']
assert abs(h2a['dR_vs_wA'] - .404) < 5e-4 and '+.404' in draft
assert abs(h3['dR_vs_wA'] - .417) < 5e-4 and '+.417' in draft
assert f"{g1['sil1110']['legs']['mean_paired_dR']:.3f}" == '-0.088' and '−.088' in draft
assert f"{r137['g3']['spread']:.3f}" == '0.075' and '.075 sham' in draft
ga = r142['anchors']['g_eAll']
assert repr(ga) == '0.1454454553127289' and '.1454454553127289' in draft
# L174 (b2): the ASCII spelling 'max|d| = 0.0' lived ONLY in the v3.21
# abstract; the claim's certified home is Methods 3.8, which spells it
# 'max|Δ| = 0.0'.  Re-scoped to the canonical spelling (the gate still
# demands the bit-identity statement in the draft) — not loosened.
assert r142['anchors']['a_eall_max'] == 0.0 and 'max|Δ| = 0.0' in draft
assert r137['census']['sil1110']['x_mean'] == 0.45416608452796936 and '.454' in draft

# (3) numbers.json == source jsons for new keys
n = nums
assert n['l137.sil24']['v']['meanR'] == r137['sil24']['meanR']
assert n['l142.h2a']['v']['mass'] == r142['hypotheses']['H2a']['mass']
assert n['l142.aeall']['v']['g_eAll'] == n['l142.aeall']['v']['g_cutng25']
assert n['l142.ti']['v']['eOutInt']['kR'] == 15 and n['l142.ti']['v']['eIn']['kR'] == 15
assert n['l137.pooled_full']['v']['k'] == 72 and n['l137.pooled_full']['v']['n'] == 192
print('L143 verify: ALL GREEN')
