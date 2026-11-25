#!/usr/bin/env python3
"""Tick-284 digest corrections, found by lane/t284/verify_quotes.py.

The first draft of the digest carried (a) a depth figure typed from memory,
(b) two quotations whose first letter I had lower-cased, (c) a transliterated
greek letter inside a quotation mark, and (d) a model sentence quoted without
its authors' own hedge. Each is replaced here by the text the fetched page
holds; every replacement must match EXACTLY ONCE or nothing is written.

Rewrites lane/t284/digest.md and the matching tail of LANE-RESEARCH.md (the
tail this tick appended), guarded on the byte count the fold reported.
"""
import pathlib, re, sys

LAB = pathlib.Path(__file__).resolve().parent
LANE = LAB.parent.parent
DIGEST = LAB / 'digest.md'
RESEARCH = LANE / 'LANE-RESEARCH.md'
PREFIX_BYTES = 145227          # LANE-RESEARCH.md before the tick-284 append


def flex(s):
    return r'\s+'.join(re.escape(tok) for tok in s.split())


EDITS = [
    ('"this enhancement of engram cell', '"This enhancement of engram cell'),
    ('"this increase does not occur after', '"This increase does not occur after'),
    ('alpha2sc-MBONs', 'α2sc-MBONs'),
    ('Their model sentence: "reactivation of engram cells during consolidation '
     'reinforces memory specificity, while inhibition of engram cell activity',
     'Their model, hedged ("our data are consistent with a model where"):\n'
     '"reactivation of engram cells during consolidation reinforces memory\n'
     'specificity, while inhibition of engram cell activity'),
    ('**READ 1 (full text at head+tail, 13.7k of 17.3k chars; results at quote '
     'level) — Matsuno, Uemura, Miyashita, Kobayashi, Liotta, Kimura, Saitoe et '
     'al., "Aberrant dopaminergic activity during consolidation causes age-related '
     'memory generalization in Drosophila", PLOS Biology 24(4):e3003752 (1 Apr '
     '2026), doi 10.1371/journal.pbio.3003752.** | What they did: aversive',
     '**READ 1 (full-text page as head+tail: 10,259 + 3,478 of its 17,318\n'
     'chars, 3,581 in the middle not read; results at quote level) — Matsuno,\n'
     'Uemura, Miyashita, Kobayashi, Liotta, Kimura, Saitoe et al., "Aberrant\n'
     'dopaminergic activity during consolidation causes age-related memory\n'
     'generalization in Drosophila", PLOS Biology 24(4):e3003752 (1 Apr 2026),\n'
     'doi 10.1371/journal.pbio.3003752.** | What they did: aversive'),
    ('activating PPL1 in YOUNG flies after training (hM1Dq DREADD, N = 5-10) gives',
     'activating PPL1 in YOUNG flies after training (hM1Dq DREADD; N = 5-10 in\n'
     'their Fig 5 legend) gives'),
    ('is causal BOTH ways — PPL1 inhibition after training rescues aged flies, and',
     'is causal BOTH ways — inhibition of PPL1 rescues the aged defects, and'),
    ('significant CS+ vs CS- engram difference in aged flies; Dop2R knockdown in '
     'engram cells reduces generalization;',
     'significant CS+ vs CS- engram difference in aged flies; knocking down\n'
     'Dop2 receptors in engram cells reduces generalization in aged flies;'),
]

old_text = DIGEST.read_text(encoding='utf-8')
new_text = old_text
for i, (old, new) in enumerate(EDITS, 1):
    hits = re.findall(flex(old), new_text)
    if len(hits) != 1:
        sys.exit(f'EDIT {i}: expected exactly 1 match, found {len(hits)} -- nothing written')
    if new in new_text:
        sys.exit(f'EDIT {i}: replacement text already present -- nothing written')
    new_text = re.sub(flex(old), lambda _m, s=new: s, new_text)

raw = RESEARCH.read_bytes()
if len(raw) < PREFIX_BYTES or raw[PREFIX_BYTES:].decode('utf-8') != old_text:
    sys.exit('LANE-RESEARCH.md tail is not the old digest byte-for-byte -- nothing written')
if new_text.count('## 2026-11-25 — tick 284 (research:') != 1:
    sys.exit('header count != 1 in the new digest -- nothing written')

new_raw = raw[:PREFIX_BYTES] + new_text.encode('utf-8')
RESEARCH.write_bytes(new_raw)
DIGEST.write_text(new_text, encoding='utf-8')

back = RESEARCH.read_bytes()
assert back == new_raw and back[PREFIX_BYTES:].decode('utf-8') == new_text
assert DIGEST.read_text(encoding='utf-8') == new_text
print(f'applied {len(EDITS)} edits; digest {len(old_text)} -> {len(new_text)} chars; '
      f'LANE-RESEARCH.md {len(raw)} -> {len(back)} bytes; '
      f'lines {back.count(bytes([10]))}; read-back equal on both files')
