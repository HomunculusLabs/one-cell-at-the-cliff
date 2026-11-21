#!/usr/bin/env python3
"""L174 (b2): splice the compressed abstract into DRAFT.md. Idempotent-
refusing: exits nonzero if the new abstract is already in place."""
import pathlib, re, hashlib, sys
P = pathlib.Path.home()/'critters/peabrain-lab'
dp = P/'paper/DRAFT.md'
d = dp.read_text()
new = (P/'banc/l174b2/abstract_new.txt').read_text().strip()
frozen = (P/'banc/l174b2/abstract_v321.txt').read_text()
i, j = d.index('## Abstract (draft)'), d.index('## 1. Introduction')
cur = d[i:j]
if new[:60] in cur:
    sys.exit('REFUSE: compressed abstract already spliced')
assert cur == frozen, 'abstract block differs from the CERT-3 freeze'
blk = '## Abstract (draft)\n\n' + new + '\n\n'
d2 = d[:i] + blk + d[j:]
# version banner bump
d2 = d2.replace('# WORKING DRAFT — preprint skeleton (L140 + L143)',
                '# WORKING DRAFT — preprint skeleton (L140 + L143)', 1)
dp.write_text(d2)
a2 = d2[d2.index('## Abstract (draft)'):d2.index('## 1. Introduction')]
flat = re.sub(r'\s+',' ', a2.split('\n',2)[2]).strip()
print('spliced. abstract body flat chars =', len(flat))
print('draft chars', len(d), '->', len(d2))
print('abstract block sha', hashlib.sha256(a2.encode()).hexdigest()[:16])
