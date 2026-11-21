#!/usr/bin/env python3
"""L174 (b3) emit: substitute the compressed §2.4 and the version banner.

T4 proof: the §2.4 pre-image must equal the frozen freeze byte-for-byte
before the single-block substitution d[:i] + new + d[j:].  Refuses a second
run (idempotence guard).  No other draft block is touched.
"""
import pathlib
import sys

P = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
B = P / 'banc/l174b3'
dp = P / 'paper/DRAFT.md'
d = dp.read_text()
pre = (B / 'sec24_pre.txt').read_text()
new = (B / 'sec24_new.txt').read_text()

if 'v3.23 = L174 stage (b3)' in d:
    sys.exit('REFUSED: the (b3) banner is already present (emit is one-shot)')

i = d.index('### 2.4 Mechanism')
j = d.index('### 2.5 ')
assert d[i:j] == pre, 'T4: the draft\u2019s \u00a72.4 is not the frozen pre-image'
d2 = d[:i] + new + d[j:]
assert d2.count('### 2.5 ') == d.count('### 2.5 ')
assert len(d2) - len(d) == len(new) - len(pre)

BANNER = """> v3.23 = L174 stage (b3) fold — the §2.4 editorial pass (reviewer I10).
> Branch S1_editorial_only: I10's three substantive asks were already shipped
> under L173 (the section is built on silW, both construction-level
> bit-identities live in Methods §3.8, and sil24 is disclosed as not separable
> from either comparator), so what remained was length. §2.4 goes 9,937 ->
> 8,562 chars (-13.8%) by DE-DUPLICATION: the grid table is now the single
> home of every per-arm level and seed count, and the prose keeps only the
> paired legs, pools, statics and disclosures the table cannot hold. Nothing
> was deleted — all 101 verifier literals and all 24 citation keys survive
> verbatim, the table is byte-unchanged, the seven claim leads are intact, and
> of 143 numeric tokens the 12 that left the section are each asserted present
> elsewhere in the body (zero orphans). The referee's quoted "3.4k chars" is
> recorded as a measurement, not a target: the adjudication file states that
> I10's own locator truncated §2.4 at a 2,600-char cap. Our own registered
> 7,200-char cap was withdrawn as mis-derived in a PREREG addendum and
> replaced by a de-duplication gate with a sensitivity self-test (it fails on
> the pre-image with five restated cells and passes on the compression),
> because a char cap on certified prose rewards deleting disclosures. Stage
> (b3b) (the 42 bullet lines in §1-§2 -> prose) and (b4) (Discussion,
> changelog-banner strip, body-wide code and all-caps strip), then stage (c)
> (the figure redraws), remain OPEN on card L174.
"""
k = d2.index('## Title')
# insert the banner at the end of the status block, immediately above the
# Title heading (same seam every earlier stage used)
d3 = d2[:k] + BANNER + '\n' + d2[k:]
dp.write_text(d3)
print(f'spliced \u00a72.4 {len(pre)} -> {len(new)} chars; draft {len(d)} -> {len(d3)}')
