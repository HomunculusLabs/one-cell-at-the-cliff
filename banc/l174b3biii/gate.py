#!/usr/bin/env python3
"""L174 (b3b-iii) step 3 — splice section (25) into l149_verify.py, above the
final ALL GREEN print. Kept as a script (not a hand edit) so the inserted
block is reproducible from this run's artifacts.

Builder lesson applied (tick 207 ADDENDUM 2 / l142): splice on a UNIQUE
opener with a count==1 guard, never an exact-match over a long block.
"""
import os, re, sys

V = "/home/t3rpz/critters/peabrain-lab/paper/l149_verify.py"
ANCHOR = 'print("L149 verify: ALL GREEN")'

SECTION = r'''
# ---------------------------------------------------------------- (25)
# L174 stage (b3b-iii): bullets -> prose in §2.7, the pre-posting controls —
# the FINAL slice of (b3b), under the same FORMAT-ONLY contract as (23)/(24).
# Everything below is re-derived from the frozen pre-image, and the section
# that owned the old §2.7 freeze ((24)) now proves the handoff against this
# stage's pre-image instead (the L120 forward-chain anchor form).
_B33 = P / 'banc/l174b3biii'
_pre_b33x = (_B33 / 'span_pre.txt').read_text()
_i_b33 = draft.index('### 2.7 Pre-posting controls')
_j_b33 = draft.index('### 2.8 The slow line')
_now_b33 = draft[_i_b33:_j_b33]
_ws_b33 = re.sub(r'\s+', ' ', _now_b33)

# census: §2.7's 16 bullet lines -> 0
assert len(_BUL_B3B.findall(_pre_b33x)) == 16, '(25) pre-image bullet count'
assert len(_BUL_B3B.findall(_now_b33)) == 0, '(25) a bullet line survived in §2.7'
# with that, the WHOLE of §1-§2 is bullet-free and stage (b3b) is complete
_body_12 = draft[draft.index('## 1. Introduction'):draft.index('## 3. Methods')]
assert len(_BUL_B3B.findall(_body_12)) == 0, \
    '(25) §1-§2 must carry no bullet lines once (b3b) is complete'

# T1: numeric and citation multisets IDENTICAL (sorted lists, not sets)
assert sorted(_NUM_B3B.findall(_pre_b33x)) == sorted(_NUM_B3B.findall(_now_b33)), \
    '(25) T1 breach: the §2.7 numeric multiset moved'
assert sorted(_CIT_B3B.findall(_pre_b33x)) == sorted(_CIT_B3B.findall(_now_b33)), \
    '(25) T1 breach: the §2.7 citation-key multiset moved'
assert len(_NUM_B3B.findall(_now_b33)) == 248 \
    and len(_CIT_B3B.findall(_now_b33)) == 22, '(25) token-count pins'

# T3: every harvested verifier literal survives. SEVEN carried the old bullet
# indentation inside their own line break (PREREG ADDENDUM 1-a, declared by
# the harvest BEFORE the rewrite); those are checked wrap-insensitively and
# the three l149 loops that own them were made break-insensitive rather than
# re-worded. Two further multiline literals live in the non-bullet
# "Design pins" paragraph and must therefore still be BYTE-exact.
_lit_b33 = json.loads((_B33 / 'literals.json').read_text())
assert _lit_b33['report']['literals_in_span'] == 166 \
    and _lit_b33['report']['literals_multiline'] == 9, '(25) literal count pins'
_EXEMPT_B33 = ['follows the\n  GRAPH, not the gain',
               'differ per seed by up to\n  .46',
               'meanR\n  .798, kR 16/16, [.806,1.000]',
               '(.477, kR 8/16,\n  [.280,.720])',
               'meanR .651, kR 15/16,\n  [.717,.989], paired \u2212.147',
               '+.474 above the twin-removed\n  graph with 16 of 16 seeds up',
               'at g_cutng25p it is +.174 with 12 of\n  16 up']
assert all(_e in _pre_b33x for _e in _EXEMPT_B33), \
    '(25) the declared wrap-fragile literals must come from the pre-image'
_miss_b33, _exempt_b33 = [], []
for _s in _lit_b33['literals']:
    if _s in _now_b33:
        continue
    if _s in _EXEMPT_B33:
        assert re.sub(r'\s+', ' ', _s) in _ws_b33, \
            '(25) declared wrap-fragile literal lost: %r' % _s
        _exempt_b33.append(_s)
    else:
        _miss_b33.append(_s)
assert not _miss_b33, '(25) literal(s) lost: %r' % _miss_b33[:4]
assert sorted(_exempt_b33) == sorted(_EXEMPT_B33), \
    '(25) the exemption set must be exactly the seven declared literals'
assert len(_lit_b33['literals']) - len(_exempt_b33) == 159, \
    '(25) verbatim-literal count pin'
# the raw-passthrough proof: the two Design-pins multiline literals are
# BYTE-exact, so that paragraph was never reflowed
for _s in ("carrier's\n80", '6 shared, Jaccard\n.037'):
    assert _s in _now_b33, '(25) raw-passthrough literal lost: %r' % _s

# T6: the two bold leads survive verbatim at a line start, and the three
# non-bullet paragraphs come through unchanged
for _lead in ('**Displacement is not removal, and the class axis is specific',
              '**The XOR pair at swapped gains: identity wins in both gain columns'):
    assert re.search(r'(?m)^' + re.escape(_lead), _now_b33), \
        '(25) bold lead not at line start: %r' % _lead
for _para in ('Scope: one fresh batch per new cell, and a two-point gain probe cannot',
              'Design pins for the rewire and deletion arms are stored [l169c.design]. The',
              'With stage (d) the four pre-posting controls of this section are complete:'):
    assert _para in _now_b33, '(25) non-bullet paragraph altered: %r' % _para[:48]

# every pre-image bullet opener is GONE as a bullet (derived from the frozen
# pre-image, never hand-listed), and no line in §2.7 begins a list item
for _m in re.finditer(r'(?m)^- (.+)$', _pre_b33x):
    assert ('- ' + _m.group(1)) not in _now_b33, \
        '(25) bullet opener survived: %r' % _m.group(1)[:56]
# the three openers that were already full sentences were de-dashed by the
# PARSER (nothing retyped); the thirteen label-colon fragments were authored
for _frag in ('Registered branch D1 fired [l169.branch]',
              'Read at FIXED gain, the contrast is maximal [l169d.legs]',
              'Registered branch E1_graph_tracking fired [l169d.branch]'):
    assert _frag in _ws_b33, '(25) de-dashed opener missing: %r' % _frag
for _frag in ('The 2x2 on Ti right-side duty divides along both axes',
              'Paired on the same batch [l169.swap_legs], `n25gW` sits',
              'The probe and its anchors are reported next.',
              'The batch unions were re-pooled with B35',
              'On the rewire arm [l169c2.rew], three independent draws',
              'The registered reading [l169c2.branch] is that the 2-of-3 majority',
              'This is not a gain artifact [l169c2.gains]',
              'On the deletion arm [l169c2.hom], deleting gi 928',
              'The anchors hold [l169c2.cert]: all twelve inherited arms',
              'The own-gain diagonal reproduces on B38',
              'Off the diagonal [l169d.grid], the twin graph run',
              'The boundaries are reported honestly.',
              'The anchors hold [l169d.cert]. All sixteen inherited arms are'):
    assert _frag in _ws_b33, '(25) authored opener missing: %r' % _frag

# PREREG ADDENDUM 1-b: l159 scans the abstract and §1 ONLY, so §2 has never
# been under the >60-word rule. The pre-image's longest §2.7 sentence was 67
# words (a bullet can carry that, a prose paragraph should not); the stage-(d)
# anchors block was split at its own clause boundaries and the discipline is
# permanent from here.
_sent_b33 = [_x for _x in re.split(r'(?<=[.!?])\s+', _ws_b33) if _x.strip()]
_long_b33 = max(len(_x.split()) for _x in _sent_b33)
assert _long_b33 <= 60, '(25) a §2.7 sentence of %d words survives' % _long_b33
assert _long_b33 == 52, '(25) longest-sentence pin'
_pre_sent_b33 = [_x for _x in re.split(r'(?<=[.!?])\s+',
                                       re.sub(r'\s+', ' ', _pre_b33x)) if _x.strip()]
assert max(len(_x.split()) for _x in _pre_sent_b33) == 68, \
    '(25) the pre-image carried a 68-token sentence (67 words + the dash)'

assert len([_p for _p in _now_b33.split('\n\n') if _p.strip()]) == 19, \
    '(25) paragraph count pin'
assert _vis(_now_b33) - _vis(_pre_b33x) == 108, '(25) visible-char delta pin'
assert len(_now_b33) < len(_pre_b33x), '(25) raw char direction pin'
assert 'v3.26 = L174 stage (b3b-iii)' in draft[:draft.index('## Title')], \
    '(25) the banner must record the (b3b-iii) stage'

print('(25) L174 (b3b-iii) bullets -> prose in \u00a72.7: branch B1_format_only '
      'proved from the frozen pre-image — the last 16 bullet lines in \u00a71-\u00a72 '
      'are gone (\u00a71-\u00a72 now carries ZERO, so stage (b3b) is complete), the '
      'numeric (248) and citation-key (22) multisets IDENTICAL, 159 of 166 '
      'harvested literals verbatim with exactly the seven declared '
      'wrap-fragile ones checked normalized and the two Design-pins '
      'multiline literals still BYTE-exact (the raw-passthrough proof), both '
      'bold leads at line starts, all 16 pre-image openers gone as bullets '
      '(3 de-dashed by the parser, 13 authored), 19 paragraphs, the longest '
      'sentence cut from 67 words to 52 under a NEW \u00a72.7 60-word rule that '
      'l159 (abstract+\u00a71 only) could never see, visible chars +108')

'''

src = open(V).read()
# the guard token must be UNIQUE to this section: the first 40 chars of the
# block are a '# ----' divider that section (24) already carries
assert "'(25) " not in src, "section (25) is already spliced"
assert src.count(ANCHOR) == 1, "anchor must occur exactly once, found %d" % src.count(ANCHOR)
out = src.replace(ANCHOR, SECTION.lstrip("\n") + ANCHOR)
if "--apply" not in sys.argv:
    print("DRY RUN: would insert %d chars above the ALL GREEN print" % len(SECTION))
    sys.exit(0)
open(V, "w").write(out)
print("SPLICED section (25) into l149_verify.py")
