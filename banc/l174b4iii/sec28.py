BLOCK = r'''
# ---------------------------------------------------------------------------
# (28) L174 stage (b4-iii-a): the lane-ID / internal-artefact strip, plus the
# §6/§7 PREMISE FINDING and the frozen all-caps PARTITION the remaining strip
# stages inherit. Everything below is re-derived from stored artefacts
# (banc/l174b4iii/{draft_pre.md,caps_partition.json,emit_report.json}), never
# from the stage's own prose.
_B4III = P / 'banc/l174b4iii'
_pre28 = (_B4III / 'draft_pre.md').read_text()
_rep28 = json.loads((_B4III / 'emit_report.json').read_text())
_part28 = json.loads((_B4III / 'caps_partition.json').read_text())
_LANE28 = re.compile(r'\bL\d{2,3}\b')
_SCOPE_A28, _SCOPE_B28 = '## 1. Introduction', '## 7. Author/submit notes'
_sc28 = draft[draft.index(_SCOPE_A28):draft.index(_SCOPE_B28)]
_pre_sc28 = _pre28[_pre28.index(_SCOPE_A28):_pre28.index(_SCOPE_B28)]

# the 13 declared edits, re-listed here so the gate is independent of emit.py
_E28 = [
    ('### 2.5 Robustness: endpoints hold, interior re-draws (L139)',
     '### 2.5 Robustness: endpoints hold, interior re-draws'),
    ('matched synapse floor (L138, L170)', 'matched synapse floor'),
    ('and after L169 (b2) we do not assume a static', 'and we do not assume a static'),
    ('the rewire and the deletion (L169 stages a\u2013d)', 'the rewire and the deletion'),
    ('is the\nL172 statistics pass', 'is the\n\u00a72.9 statistics pass'),
    ('does not ride on it (L156, L157, L162, L171)', 'does not ride on it'),
    ("with L162's evoked phase lock", 'with the evoked phase lock'),
    ('recorded in\nthe lane log', 'recorded in\nthe project log'),
    ('what the interval means (L172)', 'what the interval means'),
    ('novelty sweep logged in\nLANE-RESEARCH.md 2026-11-18.',
     'novelty sweep run on\n2026-11-18.'),
    ('- Code: lane scripts + PREREG chain under peabrain-lab/banc/ (release form\n'
     '  TBD by owner \u2014 private tree today; a public release needs owner decision).',
     '- Code: analysis scripts + the preregistration chain under\n'
     '  peabrain-lab/banc/ (release form TBD by owner \u2014 private tree today; a\n'
     '  public release needs owner decision).'),
    ('2026-11-19 (L152) and re-resolved', '2026-11-19 and re-resolved'),
    ('set-dependently so (L168).**', 'set-dependently so.**'),
]
assert len(_E28) == 13 == _rep28['n_edits'], '(28) declared-edit count pin'

# T4': each old form was unique in the pre-image and is GONE; each new form present
_chk28 = _pre28
for _o, _n in _E28:
    assert _pre28.count(_o) == 1, ('(28) old form not unique in the pre-image', _o[:40])
    assert _o not in draft, ('(28) an old form survived', _o[:40])
    assert _n in draft, ('(28) a new form is missing', _n[:40])
    _chk28 = _chk28.replace(_o, _n, 1)
# T7 STRONG: pre-image + the declared edits == the live draft, whole file
assert _chk28 == draft, '(28) T7: pre-image + the 13 declared edits != the live draft'

# T10 ZERO RESIDUE in scope (the gate that caught the hand-built list's miss)
assert not _LANE28.findall(_sc28), ('(28) lane IDs left in §1-§6',
                                    sorted(set(_LANE28.findall(_sc28))))
for _a in ('LANE-RESEARCH', 'lane log', 'lane scripts'):
    assert _a not in _sc28, ('(28) internal-artefact reference left in §1-§6', _a)
assert len(_LANE28.findall(_pre_sc28)) == 13, '(28) pre-image lane-ID census pin'
_refpre28 = draft[draft.index('## References'):draft.index('[1] ')]
assert '(L152)' not in _refpre28, '(28) the References preamble still carries a lane ID'

# OUT OF SCOPE, byte-identical (declared with reasons in the PREREG)
assert draft[:draft.index(_SCOPE_A28)] == _pre28[:_pre28.index(_SCOPE_A28)], \
    '(28) out of scope changed: banner / title block / abstract'
assert draft[draft.index(_SCOPE_B28):draft.index('## References')] == \
    _pre28[_pre28.index(_SCOPE_B28):_pre28.index('## References')], \
    '(28) out of scope changed: §7 Author/submit notes'

# THE PREMISE FINDING: §6 is a data-availability list (journal house style) and
# §7 is a note to the owner, not a manuscript section. Both are DECLARED kept
# as lists, so a later stage cannot "fix" them without re-reading the premise.
_s6_28 = draft[draft.index('## 6. Data & code'):draft.index(_SCOPE_B28)]
_s7_28 = draft[draft.index(_SCOPE_B28):draft.index('## References')]
assert len(re.findall(r'^- ', _s6_28, re.M)) == 4, '(28) §6 list-item count pin'
assert len(re.findall(r'^- ', _s7_28, re.M)) == 1, '(28) §7 list-item count pin'
assert _LANE28.findall(_s7_28), '(28) §7 keeps its lane IDs BY DECLARATION'
assert 'lane scripts' not in _s6_28 and 'PREREG' not in _s6_28, \
    '(28) §6 still names the internal script tree'
assert 'analysis scripts + the preregistration chain' in re.sub(r'\s+', ' ', _s6_28), \
    '(28) §6 replacement wording missing'

# T1: measurement multiset identical whole-draft; identifier digits by name
assert _meas(_pre28) == _meas(draft), '(28) T1 breach: a MEASUREMENT moved'
assert sorted(_CIT_B4.findall(_pre28)) == sorted(_CIT_B4.findall(draft)), \
    '(28) T1 breach: the citation-key multiset moved'
_gone28 = sorted((_idc(_pre28) - _idc(draft)).elements())
assert _gone28 == ['138', '139', '152', '156', '157', '162', '162', '168',
                   '169', '169', '170', '171', '172', '172', '2'], \
    ('(28) identifier digits removed != the 13 declared edits', _gone28)
assert sorted((_idc(draft) - _idc(_pre28)).elements()) == [], \
    '(28) an identifier digit ENTERED the draft'

# T11: the FROZEN all-caps partition (b4-iii-c) inherits, and the proof that
# this stage applied NONE of it beyond the class it owns.
assert _part28['counts'] == {'STRIP_EMPHASIS': 129, 'DEFER_BATCH': 12,
                             'DEFER_LANE': 11, 'KEEP_ACRONYM': 9,
                             'KEEP_CELLID': 5, 'CLASS_LABEL_lowercase': 5,
                             'NOTATION_spell_out': 4, 'KEEP_PROPER': 3,
                             'KEEP_SYMBOL': 1}, '(28) partition class counts'
assert len(_part28['class']) == 179 and sum(_part28['occ'].values()) == 310, \
    '(28) partition census pin'
_keep28, _defer28, _strip28 = (set(_part28['keep']), set(_part28['defer']),
                               set(_part28['strip']))
assert _keep28 | _defer28 | _strip28 == set(_part28['class']), '(28) partition incomplete'
assert not (_keep28 & _defer28) and not (_keep28 & _strip28) \
    and not (_defer28 & _strip28), '(28) partition classes overlap'
assert (len(_keep28), len(_defer28), len(_strip28)) == (18, 23, 138), \
    '(28) partition sizes'
_CAPS28 = re.compile(r"\b[A-Z][A-Z0-9\|\-\']{2,}\b")
_b15 = lambda t: t[t.index('## 1. Introduction'):t.index('## 6. Data & code')]
_cp28 = __import__('collections').Counter(_CAPS28.findall(_b15(_pre28)))
_co28 = __import__('collections').Counter(_CAPS28.findall(_b15(draft)))
_owned28 = {_t for _t, _c in _part28['class'].items() if _c == 'DEFER_LANE'} | {'LANE-RESEARCH'}
assert all(_co28.get(_t, 0) == 0 for _t in _owned28), \
    '(28) the owned caps class was not driven to zero'
_leak28 = {_t: (_cp28.get(_t, 0), _co28.get(_t, 0)) for _t in set(_cp28) | set(_co28)
           if _t not in _owned28 and _cp28.get(_t, 0) != _co28.get(_t, 0)}
assert not _leak28, ('(28) a caps class this stage does NOT own moved', _leak28)
assert sum(_n for _t, _n in _cp28.items() if _t not in _owned28) == 296, \
    '(28) non-owned caps occurrence pin'

# measurements, and the one line-count change (the §6 bullet re-wrap)
assert (_rep28['raw_delta'], _rep28['vis_delta']) == (-101, -87), '(28) char-delta pins'
assert len(draft.split('\n')) == len(_pre28.split('\n')) + 1, \
    '(28) exactly one declared re-wrap may change the line count'
assert _rep28['prose_over78_new'] == [] and _rep28['grew_past78'] == [], \
    '(28) house width: the strip may not push a prose line over 78'
assert _rep28['s28_heading_len'] == [109, 84], '(28) §2.8 heading shrink pin'
assert 'v3.29 = L174 stage (b4-iii-a)' in draft[:draft.index('## Title')], \
    '(28) the banner must record the (b4-iii-a) stage'
print('(28) L174 (b4-iii-a) the lane-ID strip: branch S1_strip_only proved from '
      'the frozen pre-image \u2014 13 declared edits (4 subsection headings, 6 prose '
      'sites, \u00a76, the References preamble and the \u00a72.2 bold lead the '
      'hand-built list MISSED and the zero-residue gate caught), \u00a71-\u00a76 now '
      'carries ZERO lane IDs and zero internal-artefact references, '
      'pre-image + the 13 edits == the live draft byte for byte, the '
      'MEASUREMENT multiset and the citation keys IDENTICAL with the 15 '
      'removed identifier digit runs asserted BY NAME, every out-of-scope '
      'range (banner, title block, abstract, \u00a77) byte-unchanged; PREMISE '
      'FINDING: \u00a76 stays a 4-item data-availability list (journal house '
      'style) and \u00a77 stays a note to the owner, out of manuscript scope and '
      'keeping its lane IDs by declaration; and the all-caps PARTITION is '
      'frozen for (b4-iii-c) \u2014 179 distinct / 310 occurrences split 18 KEEP / '
      '23 DEFER / 138 STRIP, with every non-owned class proved occurrence-'
      'identical so a derivation stage cannot leak into an application')
'''
src = open('/home/t3rpz/critters/peabrain-lab/paper/l149_verify.py').read()
TAIL = 'print("L149 verify: ALL GREEN")'
assert src.count(TAIL) == 1
assert '(28) L174 stage (b4-iii-a)' not in src, 'section (28) already spliced'
open('/home/t3rpz/critters/peabrain-lab/paper/l149_verify.py','w').write(src.replace(TAIL, BLOCK.strip('\n') + '\n\n' + TAIL))
print('section (28) spliced')
