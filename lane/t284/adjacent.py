#!/usr/bin/env python3
"""Tick-284: append the ADJACENT-PRIOR-ENTRY paragraph to the digest and to
the tail this tick appended to LANE-RESEARCH.md, keeping the two identical.
Guarded: the journal's tail must equal digest.md byte-for-byte first."""
import pathlib, re, sys

LAB = pathlib.Path(__file__).resolve().parent
RESEARCH = LAB.parent.parent / 'LANE-RESEARCH.md'
DIGEST = LAB / 'digest.md'
PREFIX_BYTES = 145227          # LANE-RESEARCH.md before the tick-284 append
HDR = '## 2026-11-25 — tick 284 (research:'
ANCHOR = '## 2026-11-09 — tick 6 (R3: fly sleep consolidation)'

PARA = '''**ADJACENT PRIOR ENTRY -- found by re-reading the journal, not by the topic
probe (the probe searched "synaptic scaling"; the journal says "downscaling"):
the tick-6 R3 rules (lines 71-97 above) are where L293's trouble starts.**
Rule 3 reads: the "prune bottom decile" idea is NOT fly biology -- "replace
with dFB-style global downscale (delta *= 0.98 per deep-sleep tick, preserves
ranking, prevents saturation)". L293 measured the third clause FALSE on the
live duck: the pass preserves ranking (one multiplicative factor) and does not
prevent saturation (0 of 115,728 edges at NIGHT_CAP after 9 nights; the delta
adds +5.3-6.1% of its own mass a night). The arithmetic was always
conditional: a x0.98 factor holds an accumulator still only at a mass where
the nightly add has fallen to 2% of it, and on her it has not. The papers
above are the field's form of the same rules: rule 1 (replay the day's
top-decile event) came from Dag 2019's vFB -> DAN reactivation, and Yan 2026
and Matsuno 2026 both put a REGULATED level on the DAN tone in that window
whose upper side costs the memory its specificity -- Berry 2015's tonic/phasic
split read from the other end. So L295's bound is not a new mechanism to
invent: it is the term rule 3 promised ("prevents saturation") and never had.
'''

raw = RESEARCH.read_bytes()
old = DIGEST.read_text(encoding='utf-8')
head = raw[:PREFIX_BYTES].decode('utf-8')
if raw[PREFIX_BYTES:].decode('utf-8') != old:
    sys.exit('LANE-RESEARCH.md tail != digest.md -- nothing written')
if head.count(ANCHOR) != 1:
    sys.exit(f'R3 anchor count {head.count(ANCHOR)} != 1 -- nothing written')
r3 = head[head.index(ANCHOR): head.index(ANCHOR) + 3200]
r3 = re.sub(r'\s+', ' ', r3)          # the journal hard-wraps inside its quotes
for q in ('"prune bottom decile" idea is NOT fly biology',
          'replace with dFB-style global downscale (delta *= 0.98 per deep-sleep',
          'preserves ranking, prevents saturation'):
    if q not in r3:
        sys.exit(f'R3 quote not found verbatim: {q!r} -- nothing written')
# the R3 section's own line span, derived not typed
first = head[:head.index(ANCHOR)].count('\n') + 1
nxt = head.find('\n## ', head.index(ANCHOR) + 1)
last = head[:nxt].count('\n')
if (first, last) != (71, 97):
    PARA = PARA.replace('lines 71-97 above', f'lines {first}-{last} above')

if 'ADJACENT PRIOR ENTRY' in old:
    print('ALREADY PRESENT -- nothing written')
    sys.exit(0)
new = old.rstrip('\n') + '\n\n' + PARA
if new.count(HDR) != 1:
    sys.exit('header count != 1 -- nothing written')
RESEARCH.write_bytes(raw[:PREFIX_BYTES] + new.encode('utf-8'))
DIGEST.write_text(new, encoding='utf-8')
back = RESEARCH.read_bytes()
assert back[PREFIX_BYTES:].decode('utf-8') == new == DIGEST.read_text(encoding='utf-8')
print(f'adjacent paragraph appended: digest {len(old)} -> {len(new)} chars; '
      f'LANE-RESEARCH.md {len(raw)} -> {len(back)} bytes, {back.count(bytes([10]))} lines; '
      f'R3 section derived at lines {first}-{last}; read-back equal')
