#!/usr/bin/env python
"""Append l149_verify section (30): makes L174 stage (b4-iii-c-i) permanent.

Splices immediately BEFORE the final `print("L149 verify: ALL GREEN")` line,
located by its unique opener with a count==1 guard (the l122 lesson: never
exact-match a long block, and never anchor on a heading — the tick-210/211/213
anchor-swallowing lessons).

OWN-CATCH recorded in the source: the first draft of this section indexed the
out-of-scope spans with ABSOLUTE offsets into both texts. That is wrong by
construction — the banner gains this stage's own entry, so the front matter
lengths differ and every absolute offset shifts. All spans are therefore
TITLE-RELATIVE.
"""
import pathlib

P = pathlib.Path('/home/t3rpz/critters/peabrain-lab/paper/l149_verify.py')
src = P.read_text()
ANCH = 'print("L149 verify: ALL GREEN")'
assert src.count(ANCH) == 1, src.count(ANCH)
assert '(30) L174 (b4-iii-c-i)' not in src, 'section (30) already present'

BLOCK = r'''
# ---------------------------------------------------------------- (30)
# L174 stage (b4-iii-c-i): the all-caps de-emphasis of §1 Introduction and
# §4 Limitations. The ONE claim this section carries that no earlier section
# can: the whole draft moved by CASE ALONE. Everything else in the stage is
# bounded by that fact, which is why §(23) and §(26) may re-point their
# frozen literal pins to case-insensitive images without weakening.
# Every span here is TITLE-RELATIVE: the banner gains this stage's entry, so
# absolute offsets into the two texts do not align (own-catch, pre-splice).
_C30 = P / 'banc/l174b4iiic'
_pre30 = (_C30 / 'draft_pre.md').read_text()
_T30 = '## Title'
_a30, _b30 = _pre30[_pre30.index(_T30):], draft[draft.index(_T30):]

# T15 CASE-ONLY, whole draft from the title onward
assert len(_a30) == len(_b30), '(30) the stage changed the draft length'
assert _a30.lower() == _b30.lower(), '(30) the stage moved more than case'
_d30 = [(_p, _q) for _p, _q in zip(_a30, _b30) if _p != _q]
assert _d30 and all(_p.isupper() and _q.islower() for _p, _q in _d30), \
    '(30) every case change must be upper -> lower'
assert len(_d30) == 412, ('(30) the case-delta pin', len(_d30))

# the banner is the ONLY region outside the title block that may differ, and
# it differs by exactly this stage's own entry
_bb30 = draft[:draft.index(_T30)]
assert _bb30.startswith(_pre30[:_pre30.index(_T30)].rstrip('\n')), \
    '(30) the banner prefix moved'
assert 'v3.31 = L174 stage (b4-iii-c-i)' in _bb30, \
    "(30) the banner delta is not this stage's declared entry"

# SCOPE: §2 Results and everything from §5 onward are byte-IDENTICAL, not
# merely case-equal — the strip touched §1 and §4 and nothing else.
for _nm, _lo, _hi in (('2 Results', '## 2. Results', '## 4. Limitations'),
                      ('5 onward', '## 5. Discussion', None)):
    _la, _lb = _a30.index(_lo), _b30.index(_lo)
    _ha = _a30.index(_hi) if _hi else len(_a30)
    _hb = _b30.index(_hi) if _hi else len(_b30)
    assert _a30[_la:_ha] == _b30[_lb:_hb], \
        ('(30) an out-of-scope span changed', _nm)

# the owned classes are driven to ZERO in scope; the KEEP classes survive
# occurrence-for-occurrence (the frozen partition of §(28), as amended by
# §(29)): cell identifiers, the two field acronyms, the operator, the
# specimen name and its possessive.
_CAP30 = _re30 = __import__('re')
_CAPR30 = _re30.compile(r"\b[A-Z][A-Z0-9][A-Z0-9'\-]*\b")
_s1_30 = _b30[_b30.index('## 1. Introduction'):_b30.index('## 2. Results')]
_s4_30 = _b30[_b30.index('## 4. Limitations'):_b30.index('## 5. Discussion')]
assert sorted(set(_CAPR30.findall(_s1_30))) == \
    ['CPG', 'CPG-', 'IN12B003', 'S07', 'XOR'], \
    ('(30) the §1 caps survivors moved', sorted(set(_CAPR30.findall(_s1_30))))
assert sorted(set(_CAPR30.findall(_s4_30))) == \
    ['BANC', "BANC'", 'EMG', 'XOR'], \
    ('(30) the §4 caps survivors moved', sorted(set(_CAPR30.findall(_s4_30))))

# §5 Discussion is the STYLE REFERENCE this stage follows: it carries zero
# all-caps tokens of any class, because stage (b4-ii) wrote it in the house
# form. Pinned here so a later stage cannot re-introduce emphasis there.
assert _CAPR30.findall(
    _b30[_b30.index('## 5. Discussion'):_b30.index('## 6. Data & code')]) == [], \
    '(30) §5 Discussion must stay free of all-caps tokens'

# the outcome-class labels now read as the lowercase defined terms §5 uses
for _t30 in ('super', 'partial', 'intermediate'):
    assert _t30 in _s4_30, ('(30) a class label is not in its house form', _t30)

# MEASUREMENT NEUTRALITY: a case change cannot move a number or a key, so
# both multisets are identical with ZERO removed digit runs — the strongest
# form of this lineage's T1 gate (tick 213 needed 15 named removals, tick 214
# needed 0 removals but 11 named mapping additions; this stage needs neither).
_NUM30 = _re30.compile(r'(?<![A-Za-z0-9])[-+\u2212]?\d[\d,]*(?:\.\d+)?'
                       r'(?:[eE][-+]?\d+)?(?:%|\u00d7)?')
_CIT30 = _re30.compile(r'\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]')
_strip30 = lambda s: _re30.sub(r'\u00a7\s*[\d.]+', '', s)
assert sorted(_NUM30.findall(_strip30(_a30))) == \
    sorted(_NUM30.findall(_strip30(_b30))), \
    '(30) T1: the measurement multiset moved'
assert sorted(_CIT30.findall(_a30)) == sorted(_CIT30.findall(_b30)), \
    '(30) T1: the citation-key multiset moved'

print('(30) L174 (b4-iii-c-i) the all-caps de-emphasis of §1 + §4: branch '
      'C1_deemphasis_only — 64 declared occurrences (26 in §1, 38 in §4) '
      'lowered to the house form, PROVED CASE-ONLY on the whole draft (same '
      'length, 412 differing bytes, every one an upper -> lower letter), so '
      'the visible-character and byte deltas are EXACTLY ZERO and both the '
      'measurement and citation-key multisets are identical with no named '
      'removal and no named addition — the first stage of this pass whose '
      'cost is provably no bytes; §2 Results and everything from §5 onward '
      'are byte-IDENTICAL (the §3 and §2 slices are deferred for a reason '
      'recorded in the PREREG: §3 hosts MODEL SYMBOLS inside the state '
      'equation and the parameter table plus one position-split token, §2 '
      'is the bulk), §5 Discussion needed nothing and is pinned caps-free '
      'as the style reference, and the KEEP survivors are pinned in both '
      'edited sections (§1: CPG, CPG-, IN12B003, S07, XOR; §4: BANC, '
      "BANC', EMG, XOR)")

'''
P.write_text(src.replace(ANCH, BLOCK.lstrip('\n') + ANCH, 1))
print('spliced section (30) before the ALL GREEN print')
