#!/usr/bin/env python3
"""L149 (draft-fold): re-derive the WHOLE-RELEASE pair-level synapse histogram
from the raw BANC v626 connections file (dv_11842997) and pin it into
l146/static.json as S0_release. Deterministic, zero RNG, zero rollouts.
The card's quoted release numbers (2,676,592 pairs / 811,821 at 3 / 462,170
pairs containing a 1-syn row / 574,733 one-syn rows) lived only in log prose
(L44 violation to quote); this pins them as an artifact."""
import json, gzip, csv, collections, io, os

D = os.path.expanduser('~/critters/peabrain-lab/banc/data/dv_11842997')
with open(D, 'rb') as f: magic = f.read(2)
raw = gzip.open(D, 'rt') if magic == b'\x1f\x8b' else open(D, 'rt', encoding='utf-8', errors='replace')
first = raw.readline()
print('header:', first.strip()[:200])
raw.seek(0)
rd = csv.DictReader(io.StringIO(first + raw.read()) if False else raw)
cols = None
pair_syn = collections.Counter()
rows_1syn = 0; rows_2syn = 0; n_rows = 0
pairs_with_1syn_row = set()
for row in rd:
    n_rows += 1
    if cols is None:
        for a,b,s in (('pre_pt_root_id','post_pt_root_id','syn_count'),
                      ('root_pre','root_post','syn_count'),
                      ('pre_root_id','post_root_id','syn_count')):
            if a in row and b in row and s in row: cols=(a,b,s); break
        assert cols, f'cols? {list(row)[:8]}'
    a,b,s = cols
    k = (row[a], row[b]); n = int(float(row[s]))
    pair_syn[k] += n
    if n == 1: rows_1syn += 1; pairs_with_1syn_row.add(k)
    elif n == 2: rows_2syn += 1
tot = collections.Counter(pair_syn.values())
n_pairs = len(pair_syn)
eq3 = tot.get(3, 0)
below3 = sum(v for k_, v in tot.items() if k_ < 3)
pairs_1syn_ok = sum(1 for k in pairs_with_1syn_row if pair_syn[k] >= 3)
out = {
 'n_rows': n_rows, 'n_pairs': n_pairs, 'eq3': eq3, 'min': min(tot),
 'below3': below3, 'rows_s1': rows_1syn, 'rows_s2': rows_2syn,
 'pairs_containing_1syn_row': len(pairs_with_1syn_row),
 'pairs_containing_1syn_row_sum_ge3': pairs_1syn_ok,
 'note': ('L149 addendum, re-derived from dv_11842997 raw rows '
          '(pre/post pairs summed over per-neuropil breakdowns); pins the '
          'release-level floor census quoted by card L149(c).'),
}
print(json.dumps(out, indent=1))
sp = os.path.expanduser('~/critters/peabrain-lab/banc/l146/static.json')
s = json.load(open(sp))
s['S0_release'] = out
json.dump(s, open(sp, 'w'), indent=1, sort_keys=True)
print('pinned into l146/static.json:S0_release')
