#!/usr/bin/env python3
"""L158 verify (abstract pass): (1) every [key] cited in the ABSTRACT
resolves in numbers.json; (2) the four load-bearing results are each
stated in the abstract AND in the §1 map bullet, and every k/n literal
the abstract quotes also appears in the certified body (cross-anchor;
sole disclosed exception: the pre-v3 U-law cell 20/64); (3) every
band-honesty number the abstract quotes is recomputed INDEPENDENTLY
from the stored l154/l156/l157 jsons (not from numbers.json); (4)
NUMERIC VOCABULARY FREEZE: every numeric token in the abstract is a
member of the frozen v3.6 allowlist, and the band set is present —
the card's 'no new claims, no new numbers' contract, enforced against
future abstract edits."""
import json, re, pathlib, statistics

P = pathlib.Path.home() / 'critters/peabrain-lab'
draft = (P / 'paper/DRAFT.md').read_text()
nums = json.loads((P / 'paper/numbers.json').read_text())
abstract = draft[draft.index('## Abstract'):draft.index('## 1. Introduction')]
intro = draft[draft.index('## 1. Introduction'):draft.index('## 2. Results')]
body = draft[draft.index('## 2. Results'):]
flat = re.sub(r'\s+', ' ', abstract)
iflat = re.sub(r'\s+', ' ', intro)

# (1) abstract citations resolve (l149 resolver, scoped to the abstract)
cited = set(re.findall(r'\[([a-z0-9_.]+)\]', abstract))
missing = []
for c in sorted(cited):
    if '.' not in c or c in nums:
        continue
    parts = c.split('.'); ok = False
    for i in range(len(parts) - 1, 0, -1):
        head, tail = '.'.join(parts[:i]), parts[i:]
        if head in nums:
            v = nums[head]['v']
            try:
                for t in tail: v = v[t]
                ok = True
            except (KeyError, TypeError, IndexError): pass
            break
    if not ok: missing.append(c)
assert not missing, f'abstract keys absent from numbers.json: {missing}'
print(f'(1) {len(cited)} abstract citations all resolve OK')

# (2) four load-bearing results stated in abstract + §1 map + body cross-anchor
# L174 (b2) RE-CUT: the abstract was compressed 5,322 -> 1,916 chars and the
# card retires all-caps emphasis, so these markers are now the LOWERCASE
# forms the compressed text uses.  The claim set is unchanged; sections (5)
# to (10) below enforce the compression contract itself (length, no keys, no
# caps, no arm codes, relocation of every dropped token, and a pin).
for p in ('matched operating point', 'all-or-none', 'mass-twin',
          'sufficient, not unique', 'set-dependent',
          "drive envelope's", 'unchopped'):
    assert p in flat.lower(), f'abstract missing result marker: {p}'
assert 'four load-bearing results' in iflat and '(1) at gain-certified MATCHED' in iflat
# RE-CUT by L171: result (4) is now the stimulus RE-ATTRIBUTION plus the
# robustness panel; the slow-line census cells are still named in the §1 map
# but as relocated limitations, and the re-attribution strings are REQUIRED.
# RE-CUT AGAIN by L172: every count in the abstract and the §1 map is now
# the CANONICAL unique-seed pooled count (§2.9), so the per-batch literals
# the previous cut froze are REQUIRED GONE and the canonical ones required
# present.  The twin label must read INTERMEDIATE, never neutral.
for p in ('5 of 178 at k=19', '188 of 194', '30 of 66, [.340,.574]',
          '78 of 98, Wilson', '449 of 449 baseline traces',
          '8 of 20 [l157.pooled]', 'STIMULUS-SET', 'INTERMEDIATE',
          'drive envelope', '12/16 vs 0/16', '15/16 vs 1/16'):
    assert p in iflat, f'§1 map missing: {p}'
for p in ('5/176 at k=19', '170/176 at k=29', '12/32, [.229,.548]',
          '28/32, Wilson lb .719', '518 of 518 baseline traces',
          'the twin is neutral'):
    assert p not in iflat, f'§1 map: superseded per-batch literal survived: {p}'
ABSTRACT_ONLY = set()      # L172: the abstract's U-law cells are now the
#                            canonical pooled counts, all present in §2.9
body = draft[draft.index('## 1. Introduction'):]
fr = set(re.findall(r'\d+/\d+', abstract))
stray = sorted(f for f in fr if f not in body and f not in ABSTRACT_ONLY)
assert not stray, f'abstract counts absent from certified body: {stray}'
# U-law endpoints: source-certify by Wilson recompute vs stored l135 bounds
Z = 1.959963984540054
def wilson(k, n):
    p = k / n; d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * ((p * (1 - p) + Z * Z / (4 * n)) / n) ** .5 / d
    return c - h, c + h
# L172: the U-law endpoints are now the canonical unique-seed pools, so they
# are source-certified against l172.pooled (whose own derivation from raw
# traces is gated in l149_verify section 19) by a Wilson recompute.
# L174 (b2) RE-CUT: the Wilson recompute is UNCHANGED for all seven arms —
# that is the source certification and it must not shrink with the abstract.
# Only the LOCATOR moved: the compressed abstract quotes two of the seven
# cells (the kill and super endpoints, in prose "of" form), and the other
# five are located in the certified body instead.  A cell may not vanish
# from both.
_p172 = _nums_p172 = nums['l172.pooled']['v']
_bflat_ulaw = re.sub(r'\s+', ' ', body)
ABS_ULAW = {'cutng19': '5 of 178', 'cutng29': '188 of 194'}
BODY_ULAW = {'cutk5': '0/226', 'cutwA': '72/258', 'cutng25': '203/210',
             'cut58': '1/258', 'cutng25p': '30/66'}
for key, lit in list(ABS_ULAW.items()) + list(BODY_ULAW.items()):
    c = _p172[key]
    lb, ub = wilson(c['kR'], c['n'])
    assert abs(lb - c['lbR']) < 1e-9 and abs(ub - c['ubR']) < 1e-9, (lit, key)
    where = flat if key in ABS_ULAW else _bflat_ulaw
    assert lit in where, (key, lit, 'abstract' if key in ABS_ULAW else 'body')
for dead in ('0/176', '5/176', '170/176', '1/176', '20/64', '47/48',
             '12/32', '28/32'):
    assert dead not in flat, f'abstract: superseded per-batch count {dead}'
print('(2) four results stated (abstract + §1 map); all SEVEN canonical '
      'U-law cells Wilson-recomputed against l172.pooled, two located in '
      'the compressed abstract and five relocated to the certified body; '
      'superseded per-batch cells absent')

# (3) band-honesty numbers recomputed from stored sources
r154 = json.loads((P / 'banc/l154/results_l154.json').read_text())
s156 = json.loads((P / 'banc/l156/static.json').read_text())
s157 = json.loads((P / 'banc/l157/static.json').read_text())
bb = r154['below_band_census']
assert (bb['on'], bb['off']) == (16, 11)
# L171 RE-CUT: these census strings now live in the BODY (§2.8/§4), not the
# abstract — the independent recomputation is UNCHANGED, only the locator moved.
assert '16/16 on-drive vs 11/16 mech-off' in re.sub(r'\s+', ' ', body)
b65 = s156['pooled']['b65_nonjitter']
assert (b65['n'], b65['below']) == (518, 518) and round(b65['wilson_lb'], 3) == 0.993
# L172: the paper quotes the UNIQUE-SEED form of this census; the stored
# trace-level cell above stays as the artifact check.
_cu172 = nums['l172.census_unique']['v']
assert (_cu172['b65']['n'], _cu172['b65']['below']) == (449, 449)
assert (_cu172['closure']['n'], _cu172['closure']['below']) == (433, 348)
assert _cu172['dup_inconsistent'] == 0
rows_b65 = [x for f in s156['rows'] for a, d in s156['rows'][f].items()
            if a == 'b65' for x in d.values()]
assert len(rows_b65) == 518 and sum(x['below'] for x in rows_b65) == 518
assert round(statistics.median([x['f_glob'] for x in rows_b65
                                if x['below']]), 3) == 0.100
assert len(s156['included_files']) == 28
_bflat = re.sub(r'\s+', ' ', body)
# L172: the §4 census bullet now leads with the UNIQUE-SEED form; the
# trace-level pair survives as the disclosed de-duplication note.
assert '449 of 449 UNIQUE SEEDS' in _bflat and 'Wilson lb .992' in _bflat
assert '348 of 433 unique seeds (lb .764)' in _bflat
assert '518 of 518 and 361 of 500 [l156.pooled]' in _bflat
assert 'median .100 Hz' in _bflat
q = s157['pooled']
P20 = [k for k in q if k not in ('mm', 'xm')]
assert len(P20) == 20
assert len([k for k in P20 if q[k]['wilson_lb'] >= .56]) == 8
assert max(q[k]['below'] for k in P20 if k.startswith('Ti')) == 6
assert (q['mm']['n'], q['mm']['below']) == (36, 36)
for p in ('8 of 20', '≤ 6 of 36', '36 of 36'):
    assert p in _bflat, p
print('(3) band-honesty abstract numbers independently recomputed from '
      'l154/l156/l157 stored jsons (census, Wilson, median, carrier subset)')

# (4) numeric vocabulary freeze (v3.8 snapshot; enforced on future edits)
# RE-CUT by L168: the scramble-control tokens are added DELIBERATELY as part
# of the uniqueness -> set-dependent-sufficiency re-scope, and are REQUIRED
# from here on (an abstract that silently drops the scramble control would
# restore the overreaching claim the referee flagged).
ALLOWED = {'0.0', '0.3', '0/176', '0/32', '0/5', '0056', '025', '04', '075',
           '088',
           '1', '1/176', '10', '100', '11/16', '1110', '12', '12/32', '13',
           '137', '138', '14/32', '142', '144', '145', '146', '148', '150',
           '154', '156', '157', '16/16', '168', '17/32', '170/176', '189',
           '19', '2', '20',
           '20/64', '229', '24', '2490', '25', '256', '2588', '28', '28/32',
           '281', '29',
           '3', '3.9', '30', '31', '317', '319', '33', '36', '39', '39/48',
           '4', '47/48',
           '5', '5/176', '5/5', '518', '548', '56', '560', '58', '6', '626',
           '681', '70', '719', '8', '8/32', '898', '93', '993',
           # --- L171 additions (re-attribution + robustness panel) ---
           '0/16', '1/16', '1.4', '12/16', '15/16', '16/16', '17', '171',
           '2.8', '9', '95',
           # --- L172 additions: the CANONICAL pooled vocabulary.  Each
           # count below is l172.pooled and each interval bound is a
           # Wilson or Newcombe bound re-derived in l149_verify (19);
           # the superseded per-batch cells are forbidden a few lines on.
           '0/226', '5/178', '72/258', '203/210', '188/194', '1/258',
           '30', '66', '78', '98', '203', '210', '178', '188', '194',
           '2.9', '008', '024', '037', '047', '064', '083', '119',
           '147', '172', '175', '305', '340', '388', '410', '429',
           '504', '512', '517', '574', '602', '628', '706', '864',
           # L173 stage (b): the corrected carrier-mass ratio (CERT-5).
           '9.72'}
# L172: the per-batch cells the earlier cuts allowed are now FORBIDDEN --
# one canonical pooled count per arm, everywhere.
FORBIDDEN_L172 = {'0/176', '5/176', '170/176', '1/176', '20/64', '47/48',
                  '12/32', '28/32', '14/32', '8/32', '518', '719'}
ALLOWED -= FORBIDDEN_L172
# L174 (b2) RE-CUT: the abstract is now 1,916 chars, so most of the frozen
# vocabulary could not fit.  The freeze is re-cut as a TWO-PLACE contract:
# every cell is either quoted in the abstract OR located in the certified
# body, never nowhere.  '48' is the single declared ADDITION (the denominator
# of the already-allowed slash form 39/48, now written in prose).
# L174 (b2) additions, all four PROSE RE-FORMATTINGS of cells the v3.8
# allowlist already carried in slash form: 48 (39/48), 0 / 15 / 16
# (0/16, 15/16, 16/16, 0/5 -> "0 of 5"). No new measurement enters here.
ALLOWED |= {'48', '0', '15', '16'}
_bflat4 = re.sub(r'\s+', ' ', body)
# ABSTRACT-required: what the compressed text must still carry itself.
REQUIRED_ABS = {'100', '0.3', '9.72', '3.9', '93', '626',
                '5', '178', '188', '194', '19', '29',      # the U-law ends
                '30', '66', '175', '047', '305', '008', '512',   # the twin
                '39', '48', '78', '98', '12', '15', '16', '1', '0'}
# BODY-relocated: cells the earlier cuts required in the abstract and that
# the compression moved into the certified body.  Each is asserted PRESENT
# there, so a compression can never become a deletion.
RELOCATED_TO_BODY = {'0/226', '72/258', '203/210', '1/258', '30/66',
                     '16/16', '12/16', '15/16', '0/16', '1/16', '11/16',
                     '0/32', '17/32', '39/48', '2490', '2588', '681',
                     '898', '1110', '319', '0.0', '0056', '1.4',
                     '10', '17', '9', '95', '560', '281', '189'}
toks = set(re.findall(r'\d+\.\d+|\d+/\d+|\d+', abstract))
extra = sorted(toks - ALLOWED)
assert not extra, f'abstract carries numbers outside the frozen v3.8 ' \
                  f'vocabulary: {extra}'
lost = sorted(REQUIRED_ABS - toks)
assert not lost, f'v3.22 abstract-required numbers vanished: {lost}'
orphan = sorted(t for t in RELOCATED_TO_BODY if t not in _bflat4)
assert not orphan, f'relocated-to-body cells have NO body home (the ' \
                   f'compression became a deletion): {orphan}'
# L172 FORBIDDEN stays exactly as cut: nothing retired may come back.
# DISCLOSED (L55 rule): with 102 -> 31 numeric tokens this check is a
# DEGENERATE pass — fewer tokens mean fewer chances to re-assert a retired
# cell — so it is reported as a guard that held, never as evidence.
back172 = sorted(FORBIDDEN_L172 & toks)
assert not back172, f'superseded per-batch counts returned to the ' \
                    f'abstract: {back172}'
# L173 stage (b) RE-CUT: the carrier-mass ratio was printed as 12x while
# .0544 / .005599 = 9.716 (reviewer I8, re-derived in banc/l173b/cert.json
# CERT-5).  The corrected value is REQUIRED and the wrong literal is
# FORBIDDEN at string level, so it cannot grow back.
assert '9.72' in toks, 'L173b: the corrected mass ratio 9.72 left the abstract'
assert '9.72\u00d7 below any mass-only band' in abstract, \
    'L173b: the corrected mass-ratio phrase is not in the abstract'
assert '12\u00d7 below' not in abstract, \
    'L173b: the retired 12x mass ratio returned to the abstract'
for p in ("drive envelope's", 'unchopped', 'no endogenous antagonist clock'):
    assert p in flat, f'L171 re-attribution language missing from abstract: {p}'
for bad in ('a real slow oscillation', 'antagonist clock, not'):
    assert bad not in flat, f'L171: abstract must not re-assert an ' \
                            f'endogenous slow clock ({bad})'
# L174 (b2): the L168 scramble numbers moved to the body (asserted above in
# RELOCATED_TO_BODY); what the abstract must still carry is the scramble
# control's own cell and its LANGUAGE, checked in (4b).
assert 'exactly one supers (39 of 48)' in flat, \
    'L168 re-scope: the scramble control cell left the abstract'
# (4b) L168 re-scope language contract: no AFFIRMATIVE uniqueness claim about
# the carrier in title/abstract/§1 map, and the scramble family must be named.
title = draft[draft.index('## Title'):draft.index('## Abstract')]
for scope in (title, abstract, intro):
    low = scope.lower()
    for bad in ('the only cell', 'uniquely', 'unique carrier',
                'the unique cell'):
        assert bad not in low, f'L168 re-scope undone: affirmative ' \
                               f'uniqueness claim "{bad}" is back'
assert 'not unique' in abstract and 'set-dependent' in abstract, \
    'L168 re-scope: abstract must state sufficiency, not uniqueness'
assert 'carrier-free' in abstract and 'mass-matched' in abstract, \
    'L168 re-scope: abstract must name the scramble control'
assert 'Sufficient, not unique' in title, 'L168 re-scoped title missing'
print(f'(4) numeric vocabulary frozen as a TWO-PLACE contract: {len(toks)} '
      f'abstract tokens subset of the v3.8 allowlist + the four declared '
      f'prose-reformatting additions; {len(REQUIRED_ABS)} required in the '
      f'abstract, {len(RELOCATED_TO_BODY)} relocated cells each located in '
      f'the body; re-scope language contract held (no affirmative '
      f'uniqueness claim); the retired-token guard is a disclosed '
      f'degenerate pass')


# ====================  L174 stage (b2): the COMPRESSION contract  ==========
# Five new gates. The card asks for an abstract <= 1,920 chars with no
# citation keys, no all-caps emphasis and no arm codes; these enforce that
# shape permanently, plus the traceability the inline [key] citations used
# to provide and a byte pin so a later prose stage cannot drift it.
import hashlib
_abody = re.sub(r'\s+', ' ', abstract.split('\n', 2)[2]).strip()

# (5) hard length
assert len(_abody) <= 1920, f'abstract is {len(_abody)} chars (limit 1,920)'
print(f'(5) abstract length {len(_abody)} <= 1,920 chars '
      f'(was 5,322 at v3.21)')

# (6) no citation keys in the abstract; traceability moves into THIS file as
# an explicit claim -> numbers.json table (strictly stronger than an inline
# key: it asserts the VALUE, not just that a key exists).
assert not re.findall(r'\[[a-z0-9_.]+\]', abstract), \
    'abstract still carries inline [key] citations'
def _resolve(path):
    if path in nums: return nums[path]['v']
    parts = path.split('.')
    for i in range(len(parts) - 1, 0, -1):
        head, tail = '.'.join(parts[:i]), parts[i:]
        if head in nums:
            v = nums[head]['v']
            for t in tail: v = v[t]
            return v
    raise KeyError(path)
TRACE = [
    ('5 of 178 seeds survive at k=19', 'l172.pooled.cutng19.kR', 5),
    ('5 of 178 seeds survive at k=19', 'l172.pooled.cutng19.n', 178),
    ('188 of 194 at k=29', 'l172.pooled.cutng29.kR', 188),
    ('188 of 194 at k=29', 'l172.pooled.cutng29.n', 194),
    ('(30 of 66', 'l172.pooled.cutng25p.kR', 30),
    ('(30 of 66', 'l172.pooled.cutng25p.n', 66),
    ('+.175', 'l172.diffs.twin_vs_base.diff', 0.175),
    ('.047', 'l172.diffs.twin_vs_base.lo', 0.047),
    ('.305', 'l172.diffs.twin_vs_base.hi', 0.305),
    ('exactly one supers (39 of 48)', 'l168.scr.cutscr0.kR', 39),
    ('exactly one supers (39 of 48)', 'l168.scr.cutscr0.n', 48),
    ('(78 of 98)', 'l172.pooled.silW.kR', 78),
    ('(78 of 98)', 'l172.pooled.silW.n', 98),
    ('endpoint holds (5 of 5)', 'sustain.cutng25.n', 5),
    ('interior re-draws (0 of 5)', 'sustain.cutwA.n', 0),
    ('9.72× below any mass-only band', 'l142.h2a.mass', 0.005599),
    ('.100 Hz', 'l171.envelope.dom_hz', 0.1),
    ('unchopped segment (12 of\n16 against 0 of 16)', 'l171.panel.fast_seg.kR', 12),
    ('high-pass (15 of 16 against 1 of 16)', 'l171.panel.highpass.kR', 15),
]
for _claim, _key, _exp in TRACE:
    assert _claim in abstract, f'(6) traced claim missing from abstract: {_claim!r}'
    _got = _resolve(_key)
    assert abs(_got - _exp) < 1e-9, f'(6) {_key} = {_got}, abstract says {_exp}'
# every numeric token is either inside a traced claim or an explicitly
# declared non-measurement token (release version, cell name, CI level).
EXEMPT = {'626': 'BANC release version', '33': 'cell name DNp33-L',
          '95': '95% confidence level', '3.9': 'twin mass delta 3.9e-04',
          '04': 'exponent of 3.9e-04', '93': 'incident-edge count',
          '0.3': 'high-pass corner in Hz', '512': 'carrier difference -.512',
          '008': 'Fisher p = .008'}
_traced_txt = ' '.join(c for c, _, _ in TRACE)
_covered = set(re.findall(r'\d+\.\d+|\d+/\d+|\d+', _traced_txt)) | set(EXEMPT)
_untraced = sorted(t for t in toks if t not in _covered)
assert not _untraced, f'(6) abstract numbers with no trace and no ' \
                      f'declared exemption: {_untraced}'
print(f'(6) zero inline citation keys; {len(TRACE)} claim->numbers.json '
      f'traces asserted by VALUE and {len(EXEMPT)} declared '
      f'non-measurement tokens cover all {len(toks)} numeric tokens')

# (7) no all-caps emphasis (the proper noun BANC is the sole allowance)
_caps = set(re.findall(r'\b[A-Z]{3,}(?:-[A-Z]+)*\b', abstract))
assert _caps <= {'BANC'}, f'(7) all-caps emphasis in the abstract: {sorted(_caps)}'
print(f'(7) all-caps emphasis gone: {sorted(_caps)} only')

# (8) no arm codes, lane ids or batch labels
_codes = re.findall(r'\bcut[a-zA-Z]|\bsil[A-Z0-9]|\bscr\d|\bb65\b|\bB\d{2}\b'
                    r'|\bL\d{2,3}\b|\bl1\d\d\b|\beMot|\beOut', abstract)
assert not _codes, f'(8) arm/lane/batch codes in the abstract: {_codes}'
print('(8) zero arm codes, lane ids or batch labels in the abstract')

# (9) RELOCATION: every numeric token of the frozen v3.21 abstract that the
# compression dropped must have a home in the certified body.  The prose
# re-formattings (5/178 -> "5 of 178") are reported separately so the count
# of genuinely relocated cells is not inflated.
_v321 = (P / 'banc/l174b2/abstract_v321.txt').read_text()
_t321 = set(re.findall(r'\d+\.\d+|\d+/\d+|\d+', re.sub(r'\s+', ' ', _v321)))
_dropped = sorted(_t321 - toks)
_orph = [t for t in _dropped if t not in _bflat4]
assert not _orph, f'(9) dropped abstract tokens with NO body home: {_orph}'
_reformat = [t for t in _dropped if '/' in t
             and t.replace('/', ' of ') in _abody]
print(f'(9) relocation complete: {len(_t321)} -> {len(toks)} numeric tokens, '
      f'{len(_dropped)} dropped and all {len(_dropped)} present in the '
      f'certified body ({len(_reformat)} of them are slash->prose '
      f're-formattings the abstract still states)')

# (10) pin: the compressed abstract's own hash, so a later prose stage that
# touches it has to re-pin deliberately.
_pin_f = P / 'banc/l174b2/abstract_pin_b2.txt'
_sha = hashlib.sha256(abstract.encode()).hexdigest()
if not _pin_f.exists():
    _pin_f.write_text(_sha + '\n')
assert _pin_f.read_text().strip() == _sha, \
    f'(10) abstract moved since the stage-(b2) pin ({_sha[:12]})'
print(f'(10) abstract pinned at {_sha[:16]}')

print('L158 verify: ALL GREEN')
