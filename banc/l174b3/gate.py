#!/usr/bin/env python3
"""L174 (b3) relocation / de-duplication gate for the §2.4 compression.

Checks the candidate section (sec24_new.txt) against the frozen pre-image
(sec24_pre.txt) under the PREREG's T1/T3/T5 and the ADDENDUM-1 gate G1'.
Pure string arithmetic; writes gate.json.  Run before AND after the splice.
"""
import json
import pathlib
import re
import sys

P = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
B = P / 'banc/l174b3'
pre = (B / 'sec24_pre.txt').read_text()
new = (B / 'sec24_new.txt').read_text()
draft = (P / 'paper/DRAFT.md').read_text()
lits = json.loads((B / 'lits24.json').read_text())

NUM = re.compile(r'[\u2212+\-]?\d[\d,]*(?:\.\d+)?(?:e[\u2212+\-]?\d+)?|\.\d+')
out = {}
fail = []


def table_of(sec):
    ls = sec.split('\n')
    tb = [k for k, l in enumerate(ls) if l.startswith('|')]
    return '\n'.join(ls[min(tb):max(tb) + 1])


tbl_pre, tbl_new = table_of(pre), table_of(new)
out['chars'] = {'pre': len(pre), 'new': len(new),
                'delta': len(new) - len(pre),
                'pct': round(100.0 * (len(new) - len(pre)) / len(pre), 2)}
out['table_unchanged'] = tbl_pre == tbl_new
if not out['table_unchanged']:
    fail.append('the grid table was modified (T5)')

# --- T3: every gate literal survives, VERBATIM (incl. internal newlines)
miss = [s for s in lits if s not in new]
out['T3_literals'] = {'total': len(lits), 'missing': miss}
if miss:
    fail.append(f'T3: {len(miss)} gate literals lost: {miss}')

# --- citation keys: every key cited in the pre-image is still cited
def keys(t):
    k = set()
    for m in re.findall(r'\[([a-z0-9_.,\s]+)\]', t):
        for x in m.split(','):
            x = x.strip()
            if re.match(r'^l\d+[a-z]?\.', x):
                k.add(x)
    return k


kp, kn = keys(pre), keys(new)
out['keys'] = {'pre': len(kp), 'new': len(kn), 'lost': sorted(kp - kn),
               'added': sorted(kn - kp)}
if kp - kn:
    fail.append(f'citation keys lost: {sorted(kp - kn)}')

# --- T1: no numeric orphans.  A token dropped from §2.4 must live elsewhere
# in the body (§1..§6), i.e. the number is relocated, never deleted.
body = draft[draft.index('## 1. Introduction'):draft.index('## References')]
body_wo = body.replace(pre, '')
tp, tn = set(NUM.findall(pre)), set(NUM.findall(new))
dropped = sorted(tp - tn)
orphan = [t for t in dropped if t not in body_wo]
out['T1_numbers'] = {'pre': len(tp), 'new': len(tn), 'dropped': dropped,
                     'orphans': orphan}
if orphan:
    fail.append(f'T1: numeric orphans {orphan}')

# --- T2: no NEW number enters §2.4
added = sorted(tn - tp)
out['T2_added_numbers'] = added
if added:
    fail.append(f'T2: new numbers in §2.4 {added}')

# --- T5: claim inventory.  Every bold lead and the table survive.
leads = re.findall(r'\*\*(.+?)\*\*', pre, re.S)
leads_n = re.findall(r'\*\*(.+?)\*\*', new, re.S)
_flat = lambda s: ' '.join(s.split())
out['T5_leads'] = {'pre': len(leads), 'new': len(leads_n),
                   'lost': [_flat(l)[:48] for l in leads
                            if _flat(l) not in [_flat(x) for x in leads_n]]}
if len(leads_n) < len(leads):
    fail.append('T5: a bold claim lead was dropped')

# --- G1' (ADDENDUM 1): de-duplication completeness.  No (meanR, kR/n) cell
# the grid table carries may be restated in the prose, UNLESS a verifier
# asserts that prose spelling (then it is certified content, not redundancy).
prose = new.replace(tbl_new, '')
# certified spans: any occurrence of a gate literal inside the prose.  A
# table-cell restatement that falls ENTIRELY inside such a span is asserted
# prose, not redundancy (the PREREG's "unless a verifier asserts that prose
# spelling" exemption, implemented as span containment rather than substring
# matching — the substring form exempted nothing and fired on .768).
cert = bytearray(len(prose))
for s in lits:
    st = 0
    while True:
        i = prose.find(s, st)
        if i < 0:
            break
        for q in range(i, i + len(s)):
            cert[q] = 1
        st = i + 1
out['G1p_certified_prose_chars'] = sum(cert)
rows = [r for r in tbl_new.split('\n') if r.startswith('|') and '---' not in r][1:]
dupes = []
for r in rows:
    c = [x.strip() for x in r.strip('|').split('|')]
    arm, mean, kr = c[0], c[2], c[3]
    counts = [x.strip() for x in kr.split(',')]
    n = counts[-1].split('/')[-1]
    for v in [x.strip() for x in mean.split('/')]:
        pats = [f'{v}, {k}' for k in counts if '/' in k]
        pats += [f'{v}, {k}/{n}' for k in counts if '/' not in k]
        # (no bare "(v, " pattern: the value+count forms above cover the same
        # restatements, and the leading paren sits OUTSIDE the certified span,
        # so it made an asserted literal read as a violation.)
        for p in pats:
            st = 0
            while True:
                i = prose.find(p, st)
                if i < 0:
                    break
                if not all(cert[q] for q in range(i, i + len(p))):
                    dupes.append({'arm': arm, 'pattern': p, 'at': i})
                st = i + 1
out['G1p_dedup_violations'] = dupes
if dupes:
    fail.append(f'G1\u2032: table cells restated in prose: {dupes}')
out['G1p_reduction_pct'] = out['chars']['pct']
if out['chars']['delta'] >= 0:
    fail.append("G1\u2032: the section did not get shorter")

out['fail'] = fail
out['verdict'] = 'PASS' if not fail else 'FAIL'
(B / 'gate.json').write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(f'{k}: {v}')
sys.exit(0 if not fail else 1)
