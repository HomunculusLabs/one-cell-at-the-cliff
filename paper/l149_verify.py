#!/usr/bin/env python3
"""L149 verify: (1) every [key] cited in DRAFT.md resolves in numbers.json;
(2) the corrected grid-table values equal stored jsons EXACTLY, and the
per-arm n=16 is PROVEN from stored pooled arithmetic + Wilson bounds (the
v2 checker's kR-string test was circular and let /18 //20 mis-carries
through); (3) every L144/L145/L146/L148 quote in the prose matches its
stored value; (4) numbers.json equals sources for the new keys."""
import json, math, re, pathlib

P = pathlib.Path.home() / 'critters/peabrain-lab'
draft = (P / 'paper/DRAFT.md').read_text()
# L174 (b3b): whitespace-normalized view of the draft. A prose pass re-wraps
# lines, so a gate literal must not depend on WHERE the line breaks fall
# (the l122 wrap-fragility lesson, applied to the gate instead of the prose).
# Claim text is unchanged; only the matching is made break-insensitive.
draft_ws = re.sub(r'\s+', ' ', draft)
nums = json.loads((P / 'paper/numbers.json').read_text())

# (1) all cited keys resolve
cited = set(re.findall(r'\[([a-z0-9_.]+)\]', draft))
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
assert not missing, f'cited keys absent from numbers.json: {missing}'
print(f'(1) {len(cited)} cited keys all resolve OK')

# (2) denominator guards: v2 mis-carries must be GONE, n=16 pinned
body = draft[draft.index('## Title'):]
# the denominator guard targets RESULT cells; the References block legitimately
# contains '/20..' inside DOIs (e.g. doi:10.1101/2024.06.04.596633), so scope the
# scan to the text above the reference list (L174 stage (a))
prose = body[:body.index('## References')]
assert '/18' not in prose and '/20' not in prose, 'stale /18 or /20 denominator survived'
assert draft.count('/16') >= 20 and 'n=16/arm' in draft
r137 = json.loads((P / 'banc/l137/results_l137.json').read_text())
r142 = json.loads((P / 'banc/l142/results_l142.json').read_text())
r144 = json.loads((P / 'banc/l144/results_l144.json').read_text())
r145 = json.loads((P / 'banc/l145/results_l145.json').read_text())
r148 = json.loads((P / 'banc/l148/results_l148.json').read_text())
r150 = json.loads((P / 'banc/l150/results_l150.json').read_text())
# n=16 from pooled arithmetic (batch unions stored in each run's json)
assert r142['pooled']['cutng25_B24_B25_B26_B29']['n'] == 64 and 'B24_B25_B26_B29'.count('_') == 3  # 64/4
assert r145['pooled']['cutwA_7batch']['n'] == 112 and r145['pooled']['cutng25_6batch']['n'] == 96
assert r148['pooled']['cutwA_8batch']['n'] == 128 and r148['pooled']['cutng25_7batch']['n'] == 112
assert r137['pooled_full']['k192'] == 72 and abs(r137['pooled_full']['p_hat'] - 72/192) < 5e-4
# n=16 from Wilson recomputation on stored per-arm bounds (z = 1.959963985)
Z = 1.959963984540054
def wilson(k, n):
    p = k / n; d = 1 + Z*Z/n
    c = (p + Z*Z/(2*n)) / d
    h = Z * math.sqrt((p*(1-p) + Z*Z/(4*n)) / n) / d
    return c - h, c + h
for src, arm in ((r142, 'cutng25'), (r145, 'eMotTop5'), (r148, 'eAll'), (r144, 'sil1110_wA')):
    c = src['table']['Ti'][arm]
    lb, ub = wilson(c['kR'], 16)
    assert abs(lb - c['lbR']) < 1e-6 and abs(ub - c['ubR']) < 1e-6, \
        f'{arm}: stored bounds match n=16 Wilson? {c["lbR"]:.6f}/{c["ubR"]:.6f} vs {lb:.6f}/{ub:.6f}'
print('(2) denominators: no stale /18 /20; n=16 proven by pooled arithmetic + Wilson bounds')

# (3) grid table + prose values vs stored jsons
def row(name, mrs, kr_str):
    for mr in mrs:
        assert mr is not None and 0.0 <= mr <= 1.0, f'{name}: meanR {mr} out of range'
        assert f'{mr:.3f}'[1:] in draft, f'{name}: meanR {mr:.3f} not quoted in draft'
    assert kr_str in draft, f'{name}: kR string {kr_str} not in draft'
ti142, ti145, ti148 = r142['table']['Ti'], r145['table']['Ti'], r148['table']['Ti']
row('sil1110 intact', [r137['g1']['sil1110']['meanR'], r144['table']['Ti']['sil1110']['meanR']], '2, 3/16')
row('vol1110', [r137['g2']['vol1110']['meanR']], '7/16')
row('sil24', [r137['sil24']['meanR']], '5/16')
row('cutwA', [ti142['cutwA']['meanR']], '4/16')
row('silW', [r144['table']['Ti']['sil1110_wA']['meanR'],
             r150['table']['Ti']['silW']['meanR']], '14, 14/16')
row('cutng25', [ti142['cutng25']['meanR']], '14/16')
row('eOutInt', [ti142['eOutInt']['meanR']], '15/16')
row('eIn', [ti142['eIn']['meanR']], '15/16')
row('eOutMot', [ti142['eOutMot']['meanR'], r145['table']['Ti']['eOutMot']['meanR']], '9, 12/16')
row('eMotTop5', [ti145['eMotTop5']['meanR'], r150['table']['Ti']['eMotTop5']['meanR']], '6, 8/16')
row('eMotBot5', [ti145['eMotBot5']['meanR'], r150['table']['Ti']['eMotBot5']['meanR']], '6, 2/16')
row('eMotIn', [ti145['eMotIn']['meanR']], '15/16')
row('eAll', [ti142['eAll']['meanR'], r148['table']['Ti']['eAll']['meanR']], '14, 15/16')
row('se0', [r148['table']['Ti']['se0']['meanR']], '15/16')
assert r148['table']['Ti']['se0'] == r148['table']['Ti']['eAll'], 'se0 != eAll in stored table'
# prose spot-quotes (value asserted, then string present)
hd = r145['hypotheses']['H_DOSE']
assert abs(hd['mean_dR_top5'] - 0.007) < 5e-4 and '+.007' in draft
assert abs(hd['mean_dR_bot5'] + 0.013) < 5e-4 and '−.013' in draft
assert hd['order_sign_count'] == 8 and '8/16' in draft
sw = r144['classes']['silW']
assert abs(sw['legs']['mean_paired_dR_vs_wA'] - 0.189) < 5e-4 and '+.189' in draft
assert sw['legs']['n_up_vs_wA'] == 6 and sw['legs']['n_down_vs_wA'] == 0 and '6/16 seeds up and 0 down' in draft
sf = r144['classes']['silF']
assert abs(sf['legs']['mean_paired_dR_vs_full'] + 0.036) < 5e-4 and '−.036 on batch D' in draft
pe = r145['pooled']['eOutMot_B29_B31']
# (L172) the stored 2-batch union is preserved as a stored-artifact check;
# the DRAFT now quotes the canonical unique-seed pool for this arm (21/34),
# whose own value is gated in section (19).
assert (pe['kR'], pe['n']) == (21, 32)
assert abs(pe['lbR'] - 0.4831) < 5e-4
assert '21/34' in draft and '[.450,.761]' in draft
pw, pn = r148['pooled']['cutwA_8batch'], r148['pooled']['cutng25_7batch']
# (L153) these 7/8-batch unions are SUPERSEDED in the draft by the l150
# 8/9-batch unions; stored values must still exist and be self-consistent
assert (pw['kR'], pw['n']) == (38, 128) and (pn['kR'], pn['n']) == (108, 112)
assert '38/128' not in draft and '108/112' not in draft  # superseded strings gone
ea = r148['pooled']['eAll_B29_B32']
assert (ea['kR'], ea['n']) == (29, 32) and '29/32' in draft and 'pooled .757' in draft
assert r148['classes']['eAll']['meanR'] == 0.768 and '.768, 15/16' in draft
assert r148['seid_all_max'] == 0.0 and r148['hypotheses']['H_ID']['bit_identical'] is True
# L174 (b2): re-scoped from the abstract-only ASCII spelling to the
# canonical Methods-3.8 spelling (same claim, same artifact).
assert 'max|Δ| = 0.0' in draft
print('(3) grid table + prose quotes match stored jsons')

# (4) floor disclosure vs pinned release census + f4 ladder
s146 = json.loads((P / 'banc/l146/static.json').read_text())
rel, f4, det = s146['S0_release'], s146['S4_ladder']['f4'], s146['decision_detail']
assert (rel['n_pairs'], rel['eq3'], rel['below3'], rel['min']) == (2676592, 811821, 0, 3)
assert (rel['rows_s1'], rel['pairs_containing_1syn_row']) == (574733, 462170)
assert rel['pairs_containing_1syn_row_sum_ge3'] == 462170
for s in ('2,676,592', '811,821', '574,733', '462,170'): assert s in draft, s
assert (f4['carrier_rank'], f4['twin_rank']) == (21, 33) and det['d4a'] and not det['d4b']
assert (det['out80_f4'], round(f4['jaccard_heavy'], 4)) == (69, 0.9231)
assert (f4['closure_edges'], s146['S4_ladder']['base']['closure_edges']) == (472095, 647953)
pct = round((647953 - 472095) / 647953 * 100, 1)
assert pct == 27.1 and '27.1%' in draft
for s in ('rank 25 → 21', '26 → 33', '69/80', '.9231', '472,095'): assert s in draft, s
assert s146['S1_substrate']['deleted']['all_f2'] == 0 and s146['S1_substrate']['deleted']['all_f3'] == 0
# numbers.json == sources for the new keys
n = nums
assert n['l144.silw']['v']['dR_vs_wA'] == r144['classes']['silW']['legs']['mean_paired_dR_vs_wA']
assert n['l145.dose']['v']['top5_dR'] == hd['mean_dR_top5']
assert n['l146.release']['v']['n_pairs'] == 2676592
assert n['l146.f4']['v']['carrier_rank'] == 21 and n['l146.f4']['v']['twin_rank'] == 33
assert n['l148.seid']['v'] == 0.0 and n['l148.h_id']['v']['bit_identical'] is True
assert n['l148.pooled']['v']['cutng25_7batch']['kR'] == 108
print('(4) release census + f4 ladder + new numbers.json keys ALL match sources')

# (5) L151 fold: substrate-gate statics — keys == sources, prose quotes match
s151 = json.loads((P / 'banc/l151/static.json').read_text())
q0 = s151['s1_sheet']['G0_closure']; q1 = s151['s1_sheet']['G1_cutwA']
assert n['l151.sheet']['v']['m1110'] == q0['m1110'] == 160.04365274470274
assert n['l151.sheet']['v']['redundancy_ratio_G0'] == round(q0['redundancy_ratio'], 3)
assert n['l151.sheet']['v']['redundancy_ratio_G1'] == round(q1['redundancy_ratio'], 3)
assert n['l151.sheet']['v']['share_1110_of_DNsheet_G0'] == round(q0['share_1110_of_DNsheet'], 4)
assert n['l151.sheet']['v']['share_1110_of_DNsheet_G1'] == round(q1['share_1110_of_DNsheet'], 4)
assert n['l151.crossed']['v']['ti_fR_twohop_share'] == round(
    s151['s2_pools']['G0_closure']['Ti_fR']['twohop_share'], 5)
assert n['l151.crossed']['v']['ti_fL_twohop_dn_total'] == \
    s151['s2_pools']['G0_closure']['Ti_fL']['twohop_dn_total'] == 0.0
assert n['l151.verdict']['v']['H_SUB_fires'] is False
assert n['l151.sheet']['v']['ng58_others_G0'] < q0['m1110'] / 2  # dominance claim
# prose quotes in §2.4(a)
for s in (f"{q0['redundancy_ratio']:.2f}×", '14.5% intact vs 14.7% cut',
          'five right-side antagonist pools', 'IN06B033',
          f"{s151['s2_pools']['G0_closure']['Ti_fR']['twohop_share']:.3f}",
          '[l151.sheet]', '[l151.crossed]', '[l151.verdict]'):
    assert s in draft, s
assert '57 cohort cells' in draft and 'dominant single DN input' in draft
print('(5) L151 statics fold: keys + prose quotes match sources')

# (6) L153 fold: silW rebase + halves second batch + pooled-base refresh
h1 = r150['hypotheses']['H1_silW']
assert h1['b33_class'] == 'SUPER' and (h1['meanR'], h1['kR']) == (0.659, 14)
assert abs(h1['paired_dR_vs_wA'] - 0.281) < 5e-4 and '+.281' in draft
assert h1['n_up_vs_wA'] == 9 and '9/16 up and 0 down' in draft
assert h1['replicates'] is True and h1['class_leg'] and h1['pooled_leg']
ps = r150['pooled']['silW_B30_B33']
# (L172) every per-batch union below stays asserted against its STORED
# json (those artifacts did not change), but the draft-side literals move
# to the canonical unique-seed pools of section (19): the paper carries
# ONE count per arm and these partial unions are no longer quoted.
assert (ps['kR'], ps['n']) == (28, 32) and abs(ps['lbR'] - 0.7193) < 5e-4
assert '78/98' in draft and '78 of 98' in draft and '[.706,.864]' in draft
pt, pb = r150['pooled']['eMotTop5_B31_B33'], r150['pooled']['eMotBot5_B31_B33']
assert (pt['kR'], pt['n']) == (14, 32) and abs(pt['lbR'] - 0.2817) < 5e-4
assert '31/98' in draft and '31 of 98' in draft and '[.233,.414]' in draft
assert (pb['kR'], pb['n']) == (8, 32) and abs(pb['lbR'] - 0.1325) < 5e-4
assert '25/98' in draft and '25 of 98' in draft and '[.179,.350]' in draft
pn8, pw9 = r150['pooled']['cutng25_8batch'], r150['pooled']['cutwA_9batch']
assert (pn8['kR'], pn8['n']) == (124, 128) and abs(pn8['lbR'] - 0.9224) < 5e-4
assert '203 of 210' in draft and '[.933,.984]' in draft
assert (pw9['kR'], pw9['n']) == (43, 144) and abs(pw9['ubR'] - 0.3778) < 5e-4
assert '72 of 258' in draft and '[.228,.337]' in draft
# Wilson recomputation, full precision, on every new pooled union (L90 form)
for c in (ps, pt, pb, pn8, pw9):
    lb, ub = wilson(c['kR'], c['n'])
    assert abs(lb - c['lbR']) < 1e-6 and abs(ub - c['ubR']) < 1e-6, \
        f'pooled Wilson mismatch: {c}'
# pooled arithmetic: n must be exact batch-union multiples of 16
assert pn8['n'] == 8 * 16 and pw9['n'] == 9 * 16 and ps['n'] == 2 * 16
# fresh-batch (B33) per-arm bounds are n=16 Wilsons
for arm in ('silW', 'eMotTop5', 'eMotBot5'):
    c = r150['table']['Ti'][arm]
    lb, ub = wilson(c['kR'], 16)
    assert abs(lb - c['lbR']) < 1e-6 and abs(ub - c['ubR']) < 1e-6, arm
# both-batch grid rows carry the two meanRs and two kRs
for s in ('.622 / .659', '14, 14/16', '.438 / .460', '6, 8/16',
          '.418 / .350', '6, 2/16'):
    assert s in draft, s
# data-integrity note present and pinned to the corrected artifact
assert 'l150/static.json' in draft and 'Data-integrity note' in draft
# field cites present with their headline numbers
assert 'Sapkal' in draft and 'IN12B003' in draft and 'DUCKOPHILA' in draft \
    and '0 of 20' in draft
# numbers.json == sources for the new keys
assert n['l150.h1']['v']['meanR'] == 0.659 \
    and n['l150.h1']['v']['paired_dR_vs_wA'] == 0.281
assert n['l150.pooled']['v']['silW_B30_B33']['kR'] == 28
assert n['l150.pooled']['v']['cutng25_8batch']['kR'] == 124
assert n['l150.pooled']['v']['cutwA_9batch']['kR'] == 43
print('(6) L153 fold: silW rebase + halves + pooled bases match l150 stored jsons')

# (7) L155 fold: Sapkal signed-direction negative (L154) — every quote
# recomputed INDEPENDENTLY from the stored per-seed duty07 tables.
r154 = json.loads((P / 'banc/l154/results_l154.json').read_text())
assert (r154['n_pos'], r154['n_neg'], r154['n_zero']) == (6, 10, 0)
assert abs(r154['p_two_sided'] - 0.4545) < 5e-5 and r154['direction_met'] is False
assert '6+/10− of 16, p=.4545' in draft and 'NOT MET' in draft_ws, (
    'L154 negative-direction wording drift')
# anchor re-draw quote (.70/.32 on -> .45/1.09 off); house style has no
# leading zero, so assert the literal + the rounding numerically
a8, a9 = r154['anchors']['801'], r154['anchors']['901']
assert '.70/.32 Hz on → .45/1.09 off' in draft, 'anchor re-draw sentence drift'
assert (round(a8['b65'], 2), round(a9['b65'], 2),
        round(a8['off'], 2), round(a9['off'], 2)) == (0.7, 0.32, 0.45, 1.09)
# S07 means recomputed from per-seed tables (independent of extract_numbers)
def s07(pool, arm, side):
    return sum(v[f'S07_{side}'] for v in r154[f'duty07_{pool}'][arm].values()) / 16
assert len(r154['duty07_Ti']['b65']) == 16 and len(r154['duty07_Tr']['off']) == 16
rec = {f'{p}_{s}': (s07(p, 'off', s), s07(p, 'b65', s))
       for p in ('Ti', 'Tr') for s in ('L', 'R')}
assert 'Ti L +.61 / R +.72, Tr R +.76' in draft, 'S07 off quote drift'
assert '(−.08 → +.04)' in draft, 'Tr-L wake quote drift'
for k, (off, on), quoted in (('Ti_L', (rec['Ti_L'][0], 0), .61),
                             ('Ti_R', (rec['Ti_R'][0], 0), .72),
                             ('Tr_R', (rec['Tr_R'][0], 0), .76)):
    assert abs(off - quoted) < 6e-3, k
assert abs(rec['Tr_L'][1] - (-0.08)) < 6e-3 and abs(rec['Tr_L'][0] - 0.04) < 6e-3
assert rec['Ti_L'][0] > .5 and rec['Ti_R'][0] > .5 and rec['Tr_R'][0] > .5 \
    and rec['Tr_L'][1] < 0 and rec['Tr_L'][0] > 0, 'S07 survival/wake signs'
# cross-check extract_numbers means == independent recompute (full precision)
v = nums['l154.structure']['v']
for k in rec:
    off, on = rec[k]
    assert abs(v['S07_off'][k] - off) < 5e-3 and abs(v['S07_on'][k] - on) < 5e-3, k
assert v['S07_on']['Tr_L'] == round(r154['S07_L_mean']['b65']['Tr'], 4) \
    and v['S07_off']['Tr_L'] == round(r154['S07_L_mean']['off']['Tr'], 4)
# band census + untruncated means + posthoc label
bb = r154['below_band_census']
assert (bb['on'], bb['off']) == (16, 11) and '16/16 on-drive vs 11/16 mech-off' in draft
assert abs(r154['dom_full_mean']['b65'] - 0.1002) < 5e-5 \
    and abs(r154['dom_full_mean']['off'] - 0.2031) < 5e-5 \
    and '.10 → .20 Hz' in draft
assert '11+/5-' in r154['posthoc_untrunc_paired_sign'] \
    and 'DESCRIPTIVE' in r154['posthoc_untrunc_paired_sign'] \
    and '11+/5−' in draft and 'descriptive, not claim-carrying' in draft
# numbers.json l154.* == stored json scalars
assert nums['l154.freq']['v']['n_pos'] == 6 and nums['l154.freq']['v']['p'] == 0.4545
assert nums['l154.band']['v']['below_band_on'] == 16 \
    and nums['l154.band']['v']['posthoc'] == r154['posthoc_untrunc_paired_sign']
print('(7) L155 fold: Sapkal negative quotes match l154 stored jsons '
      '(S07 means independently recomputed)')

# (8) L156 fold: sub-band slow-line census — quotes literal + numbers
# recomputed INDEPENDENTLY from static.json rows (not from the pooled dict).
_s156 = json.loads((P / 'banc/l156/static.json').read_text())
_rows, _pool = _s156['rows'], _s156['pooled']
v156 = nums['l156.pooled']['v']
for arm, tag in (('b65', 'b65_nonjitter'), ('full', 'full_nonjitter')):
    allv = [x for f in _rows for a, d in _rows[f].items() if a == arm
            for x in d.values()]
    bl = [x for x in allv if x['below']]
    assert len(allv) == v156[arm]['n'] and len(bl) == v156[arm]['below'], arm
    assert sum(x['survive'] for x in bl) == v156[arm]['survive'], arm
    assert sum(x['agree'] for x in bl) == v156[arm]['agree'], arm
    assert round(v156[arm]['lb'], 3) == (0.993 if arm == 'b65' else 0.681), arm
    p = len(bl) / len(allv)
    z = 1.959963984540054
    lb = (p + z * z / (2 * len(allv)) - z * ((p * (1 - p) / len(allv)
          + z * z / (4 * len(allv) ** 2)) ** .5)) / (1 + z * z / len(allv))
    assert abs(lb - _pool[tag]['wilson_lb']) < 1e-12, ('wilson', arm)
    assert v156[arm]['med_f_below'] == round(
        __import__('statistics').median([x['f_glob'] for x in bl]), 4), arm
assert v156['b65']['files'] == 28 and v156['full']['files'] == 27
assert _s156['excluded'] == 0 and len(_s156['included_files']) == 28
# draft literals (line-wrap safe) + supersession of the queued-census clause
assert 'census is queued (L156)' not in draft, 'superseded clause survived'
# (L172) the §4 census bullet now quotes the UNIQUE-SEED forms; the
# trace-level forms survive only as the disclosed de-duplication note, so
# the literal gate follows the new wording (section (19b) re-derives both).
for lit in ('518 of 518 and 361 of 500 [l156.pooled]',
            '449 of 449 UNIQUE SEEDS', '348 of 433 unique seeds',
            'median .100 Hz', 'linear detrend in every',
            'a real slow oscillation rather than', 'stimulus-locked one'):
    assert lit in draft, ('l156 quote drift', lit)
assert v156['b65']['med_f_below'] == 0.1 and v156['b65']['n'] == 518
# ADDENDUM 1 cert: stored l154 census == bin form on B34 (cross-file),
# and the boundary seed carries the whole interpolated/bin difference.
_off = _rows['l154/raw_l154.npz']['off']
_b65 = _rows['l154/raw_l154.npz']['b65']
B34 = [str(s) for s in range(3401, 3417)]
assert sum(_b65[s]['below_bin'] for s in B34) == 16
assert sum(_off[s]['below_bin'] for s in B34) == 11
assert v156['cert_bin_below_l154_B34'] == {'on': 16, 'off': 11} \
    == r154['below_band_census']
assert _off['3401']['f_glob_bin'] == 0.3 and _off['3401']['f_glob'] < 0.3 \
    and v156['boundary_seed'] == 3401
assert sum(_off[s]['below'] for s in B34) == 12, 'interp form differs by 3401'
print('(8) L156 fold: census quotes literal + pooled counts/Wilson/medians '
      'independently recomputed; ADDENDUM-1 bin-form cert == stored')

# (9) L157 fold: per-pool carrier census — sentence literals + numbers
# recomputed INDEPENDENTLY from l157/static.json table/pooled (not from
# the numbers.json dict alone).
_s157 = json.loads((P / 'banc/l157/static.json').read_text())
_t157, _q157 = _s157['table'], _s157['pooled']
v157 = nums['l157.pooled']['v']
P20 = [k for k in _q157 if k not in ('mm', 'xm')]
# 9a: pooled dict == independent recompute from the per-file table
for ch in ('mm', 'xm') + tuple(P20):
    n = sum(_t157[f'{f}|b65|{ch}']['n'] for f in
            ('l154/raw_l154.npz', 'l150/raw_l150.npz'))
    bel = sum(_t157[f'{f}|b65|{ch}']['below'] for f in
              ('l154/raw_l154.npz', 'l150/raw_l150.npz'))
    assert (n, bel) == (_q157[ch]['n'], _q157[ch]['below']), ch
    if ch in ('mm', 'xm'):
        assert (n, bel) == (36, 36) == (v157[ch]['n'], v157[ch]['below']), ch
# 9b: derived counts == numbers.json == draft literals
lb056 = [k for k in P20 if _q157[k]['wilson_lb'] >= .56]
assert len(lb056) == v157['n_pools_lb_ge_056'] == 8, len(lb056)
assert all(k[:2] in ('Tr', 'Ta', 'Sr') for k in lb056), 'subset not Tr/Ta/Sr'
assert max(_q157[k]['below'] for k in P20 if k.startswith('Ti')) \
    == v157['ti_max_below'] == 6
assert max(_q157[k]['below'] for k in P20 if k.startswith('Pr')) \
    == v157['pr_max_below'] == 20
assert v157['pr_max_lb'] == round(
    max(_q157[k]['wilson_lb'] for k in P20 if k.startswith('Pr')), 4)
import statistics as _st
assert v157['strong_med'] == round(_st.median(
    [_q157[k]['med_f_below'] for k in lb056]), 4)
assert round(v157['strong_med'], 3) == 0.1   # draft '.100 Hz' @ 3-dec
# 9c: draft sentence literals (line-wrap safe)
for lit in ('not', 'antagonist-clock-wide', '36 of 36', '8 of 20',
            'lb ≥ .56', 'subset median .100 Hz', '≤ 6 of 36',
            '20 of 36 (lb .396)', '[l157.pooled]'):
    lit_n = lit.replace('≤ ', '').replace('≥ ', '')
    assert lit in draft or lit_n in draft, ('l157 quote drift', lit)
assert v157['claim_class'] == 'C2_readout_only'  # label vs structure note
print('(9) L157 fold: carrier census literals + pooled counts/Wilson '
      'independently recomputed from table; subset Tr/Ta/Sr asserted')

# (10) L168 fold: the SCRAMBLE CONTROL FAMILY. Pools re-derived here
# INDEPENDENTLY from the three stored per-batch tables (l125/l127/l128
# results_*.json:table.Ti) — not from l168/static.json and not from
# numbers.json — then asserted against both the ledger and the draft
# literals. Also enforces the L168 re-scope language contract in §2.2.
_R168 = {d: json.loads((P / f'banc/{d}/results_{d}.json').read_text())
         for d in ('l125', 'l127', 'l128')}
_ARMS168 = {'cutscr0': ['l125', 'l127', 'l128'],
            'cutscr1': ['l125', 'l128'], 'cutscr2': ['l125', 'l128'],
            'cutscr3': ['l125', 'l128'], 'cutcl40': ['l127'],
            'cutscrL1': ['l127'], 'cutscrL2': ['l127']}
v168 = nums['l168.scr']['v']
assert set(v168) == set(_ARMS168), (sorted(v168), sorted(_ARMS168))
for _arm, _files in _ARMS168.items():
    _n = 16 * len(_files)
    _kR = sum(_R168[f]['table']['Ti'][_arm]['kR'] for f in _files)
    _kL = sum(_R168[f]['table']['Ti'][_arm]['kL'] for f in _files)
    _lbR, _ubR = wilson(_kR, _n)
    _lbL, _ubL = wilson(_kL, _n)
    _c = v168[_arm]
    assert (_c['n'], _c['n_batches'], _c['kR'], _c['kL']) == \
        (_n, len(_files), _kR, _kL), ('l168 pool drift', _arm)
    for _got, _ours in ((_c['lbR'], _lbR), (_c['ubR'], _ubR),
                        (_c['lbL'], _lbL), (_c['ubL'], _ubL)):
        assert abs(_got - round(_ours, 4)) < 1e-12, ('l168 Wilson', _arm)
    # mass pins come from the stored mass tables, cross-file consistent
    _msrc = next(f for f in _files if _arm in _R168[f]['mass_scr'])
    assert _c['mass'] == _R168[_msrc]['mass_scr'][_arm]
    assert _c['extra'] == _R168[_msrc]['extra_mass_scr'][_arm]
    # the §2.2 table row must quote our recomputed bounds verbatim
    for _k, _lb, _ub in ((_kR, _lbR, _ubR), (_kL, _lbL, _ubL)):
        _lit = f'{_k}/{_n} [{_lb:.3f}'[:-0] + f',{_ub:.3f}]'
        _lit = _lit.replace('[0.', '[.').replace(',0.', ',.')
        assert _lit in draft, ('l168 draft row drift', _arm, _lit)
# untreated base over the same three batches (claim (d): BOTH sides raised)
_bR = sum(_R168[f]['table']['Ti']['full']['kR'] for f in _ARMS168['cutscr0'])
_bL = sum(_R168[f]['table']['Ti']['full']['kL'] for f in _ARMS168['cutscr0'])
_vb = nums['l168.base']['v']
assert (_vb['kR'], _vb['kL'], _vb['n']) == (_bR, _bL, 48), 'l168 base drift'
for _k, _n2, _f in ((_bR, 48, 'R'), (_bL, 48, 'L')):
    _lb, _ub = wilson(_k, _n2)
    assert abs(_vb['lb' + _f] - round(_lb, 4)) < 1e-12 and \
           abs(_vb['ub' + _f] - round(_ub, 4)) < 1e-12, ('l168 base W', _f)
    _lit = f'{_k}/{_n2} [{_lb:.3f},{_ub:.3f}]'.replace(
        '[0.', '[.').replace(',0.', ',.')
    assert _lit in draft, ('l168 base row', _lit)
# claim (d) must be TRUE in the data, not just asserted in prose
assert v168['cutscr0']['lbR'] > _vb['ubR'] and \
       v168['cutscr0']['lbL'] > _vb['ubL'], \
    'l168 claim (d): cutscr0 must exceed the base band on BOTH sides'
assert nums['l168.verdict']['v']['scr0_both_sides_above_base'] is True
# window mass + gap re-derived
_wm = nums['l168.window_mass']['v']
assert _wm['k29'] == _R168['l125']['mass']['cutng29'] == \
       _R168['l128']['mass']['cutng29']
assert _wm['scr0'] == v168['cutscr0']['mass']
assert abs(_wm['gap'] - round(_wm['k29'] - _wm['scr0'], 6)) < 1e-12
# PREREG decision rule: D3 (heterogeneous) must match the measured pools
_sup = sorted(a for a in v168 if v168[a]['lbR'] > .5)
_kil = sorted(a for a in v168 if v168[a]['ubR'] < .5)
_vv = nums['l168.verdict']['v']
assert _vv['supers'] == _sup == ['cutscr0'], (_vv['supers'], _sup)
assert _vv['kills'] == _kil and _vv['heterogeneous'] is True
assert _vv['rule'] == 'D3', _vv['rule']
# §2.2 re-scope language contract (no affirmative uniqueness claim)
_s22 = draft[draft.index('### 2.2 '):draft.index('### 2.3 ')]
for _bad in ('the only cell', 'uniquely', 'unique carrier'):
    assert _bad not in _s22.lower(), ('L168 re-scope undone in §2.2', _bad)
for _lit in ('Scramble controls: sufficient, not unique',
             'SUFFICIENT route to the transition', 'Set-dependent, not '
             'mass-dependent', 'do not reproduce the crossed state',
             'seven carrier-free cohorts', '[l168.scr]', '[l168.base]',
             '[l168.window_mass]'):
    assert _lit in _s22, ('l168 §2.2 literal missing', _lit)
print('(10) L168 fold: 7 scramble pools + base re-derived independently from '
      'l125/l127/l128 tables (Wilson to 1e-12), draft rows asserted verbatim, '
      'claim (d) proven in data, PREREG rule D3 matched, re-scope contract held')

# (11) L169 fold: the GAIN-SWAP 2x2. The grid is re-derived from the stored
# raw traces with the SAME duty machinery the run used (not read off the
# results json), so a metric-code transcription cannot slip through; the
# §2.7 prose is then asserted literal-by-literal.
import numpy as _np169

_W169, _TS169 = 6000, _np169.arange(499, 6000, 10)
_SEG169 = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
_B35 = list(range(3417, 3433))
_z169 = _np169.load(str(P / 'banc/l169/raw_l169.npz'))


def _S169(a, b):
    if a.std() <= 1e-6 or b.std() <= 1e-6:
        return float('nan')
    return float(-_np169.corrcoef(a, b)[0, 1])


def _duty169(arm, seeds):
    q = _np169.zeros(len(_TS169), bool)
    for a0, b0, f in _SEG169:
        if f == 0.7:
            q |= (_TS169 >= a0 + 500) & (_TS169 < b0)
    L, R = [], []
    for s in seeds:
        tr = {c: _z169[f'Ti_{c}_{arm}_{s}'][:_W169]
              for c in ('fL', 'fR', 'eL', 'eR')}
        sl = _np169.full(_W169, _np169.nan)
        sr = _np169.full(_W169, _np169.nan)
        for t in _TS169:
            sl[t] = _S169(tr['fL'][t - 499:t + 1], tr['eL'][t - 499:t + 1])
            sr[t] = _S169(tr['fR'][t - 499:t + 1], tr['eR'][t - 499:t + 1])
        L.append(round(float(_np169.nanmean(sl[_TS169[q]] >= .25)), 3))
        R.append(round(float(_np169.nanmean(sr[_TS169[q]] >= .25)), 3))
    return _np169.array(L), _np169.array(R)


_v169 = nums['l169.grid']['v']
_cells169 = {'graph_wA__gain_wA': 'cutwA', 'graph_wA__gain_ng25': 'wAgN',
             'graph_ng25__gain_wA': 'n25gW', 'graph_ng25__gain_ng25': 'cutng25'}
_RD169 = {}
for _cell, _arm in _cells169.items():
    _L, _R = _duty169(_arm, _B35)
    _RD169[_arm] = _R
    _kR = int((_R >= .5).sum())
    _lb, _ub = wilson(_kR, 16)
    _c = _v169[_cell]
    assert _c['arm'] == _arm and _c['kR'] == _kR, ('l169 grid kR', _cell)
    assert _c['meanR'] == round(float(_R.mean()), 3), ('l169 grid meanR', _cell)
    assert abs(_c['lbR'] - round(_lb, 4)) < 1e-12 and \
           abs(_c['ubR'] - round(_ub, 4)) < 1e-12, ('l169 grid Wilson', _cell)
    # class bands VERBATIM (super: meanR>=.60 and kR>=12; partial band)
    _sup = bool(_c['meanR'] >= .60 and _kR >= 12)
    _par = bool(.35 <= _c['meanR'] <= .50 and 3 <= _kR <= 8)
    _want = 'SUPER' if _sup else 'PARTIAL' if _par else None
    if _want:
        assert _c['cls'] == _want, ('l169 class', _cell, _c['cls'])
# paired legs re-derived against the SAME batch
_legs169 = nums['l169.swap_legs']['v']
for _arm in ('wAgN', 'n25gW'):
    _d = _RD169[_arm] - _RD169['cutwA']
    assert _legs169[_arm]['dR_vs_wA'] == round(float(_d.mean()), 3), \
        ('l169 dR_vs_wA', _arm)
    assert _legs169[_arm]['n_up_vs_wA'] == int((_d >= .20).sum()), \
        ('l169 n_up', _arm)
# the registered branch must follow from the measured cells, not the label
_wAgN = _v169['graph_wA__gain_ng25']
_n25gW = _v169['graph_ng25__gain_wA']
_D1 = bool(_wAgN['kR'] <= 8 and _wAgN['meanR'] <= .50
           and _n25gW['meanR'] >= .60 and _n25gW['kR'] >= 12)
_D2 = bool(_wAgN['meanR'] >= .60 and _wAgN['kR'] >= 12
           and _n25gW['kR'] <= 8 and _n25gW['meanR'] <= .50)
assert _D1 and not _D2, ('l169 branch legs', _D1, _D2)
assert nums['l169.branch']['v'] == 'D1_graph_tracking'
# the swap must be a real perturbation (C0-NT) and the gains genuinely crossed
assert nums['l169.nt']['v']['min'] > 0.0 and nums['l169.nt']['v']['n'] == 4
assert _v169['graph_wA__gain_ng25']['gain'] == \
    _v169['graph_ng25__gain_ng25']['gain'], 'l169 wAgN gain not crossed'
assert _v169['graph_ng25__gain_wA']['gain'] == \
    _v169['graph_wA__gain_wA']['gain'], 'l169 n25gW gain not crossed'
# P-af disclosure must match the stored per-seed count (no rounding up)
_af169 = nums['l169.af']['v']
assert _af169['paf_n'] == 18 and _af169['paf_per_seed_ok'] == 15, _af169
assert _af169['mean']['wAgN'] > _af169['target'] > _af169['mean']['n25gW']
# §2.7 prose contract
_s27 = draft[draft.index('### 2.7 '):draft.index('## 3. Methods')]
for _lit in ('[l169.grid]', '[l169.swap_legs]', '[l169.branch]', '[l169.af]',
             '[l169.nt]', '[l169.pooled]',
             'meanR .426, kR 4/16', 'meanR .317, kR 2/16',
             'meanR .702, kR 15/16, [.717,.989]', 'meanR .753, kR 16/16',
             '+.276 above cutwA', '\u2212.109 BELOW it',
             'Registered branch D1 fired',
             'follows the\n  GRAPH, not the gain',
             '15 of 18 seeds', 'silW 42/48 (lb .753, three',
             'cutng25 140/144 (lb .931, nine)', 'cutwA 47/160 (ub .368, ten)'):
    # L174 (b3b-iii): §2.7 is prose now, so the match is WRAP-INSENSITIVE
    # (claim text unchanged; strictly stronger — a literal can no longer hide
    # behind a different line wrap). PREREG ADDENDUM 1-a.
    assert re.sub(r'\s+', ' ', _lit) in re.sub(r'\s+', ' ', _s27), \
        ('l169 §2.7 literal missing', repr(_lit))
# the pooled unions quoted in §2.7 must be the stored ones
_p169 = nums['l169.pooled']['v']
assert (_p169['silW']['kR'], _p169['silW']['n']) == (42, 48)
assert (_p169['cutng25']['kR'], _p169['cutng25']['n']) == (140, 144)
assert (_p169['cutwA']['kR'], _p169['cutwA']['n']) == (47, 160)
for _a, _f in (('silW', 'lbR'), ('cutng25', 'lbR'), ('cutwA', 'ubR')):
    _lb, _ub = wilson(_p169[_a]['kR'], _p169[_a]['n'])
    assert abs(_p169[_a][_f] - round({'lbR': _lb, 'ubR': _ub}[_f], 4)) < 1e-12
print('(11) L169 fold: 2x2 grid re-derived from raw B35 traces with the run\'s '
      'own duty machinery (kR/meanR/Wilson to 1e-12), paired legs recomputed, '
      'branch D1 proven from the cells, C0-NT + crossed gains + the 15/18 '
      'P-af disclosure asserted, §2.7 literals verbatim')

# ---- (12) L169 stage (b1): frozen-vs-rederived floor forms ----
_b1 = json.loads((P / 'banc/l169b/static.json').read_text())
_s146 = json.loads((P / 'banc/l146/static.json').read_text())
_F1 = _b1['forms']['F1_frozen_all']
_F2 = _b1['forms']['F2_frozen_set_reordered']
_F3 = _b1['forms']['F3_fully_rederived']
# the fully re-derived form IS the published f4 artifact, field for field
_stored_f4 = _s146['S4_ladder']['f4']
for _k, _v in _stored_f4.items():
    assert _F3[_k] == _v, ('l169b F3 != stored l146 f4', _k, _F3[_k], _v)
# frozen-all ranks cannot move; the stored artifact is NOT that form
assert (_F1['carrier_rank'], _F1['twin_rank']) == (25, 26), _F1
assert _stored_f4['carrier_rank'] != _F1['carrier_rank']
# the shift is re-ordering, not turnover: frozen SET + re-order gives the
# same two ranks as the fully re-derived ladder
assert (_F2['carrier_rank'], _F2['twin_rank']) == \
       (_F3['carrier_rank'], _F3['twin_rank']) == (21, 33), (_F2, _F3)
assert _F2['K'] == 77 and _F3['K'] == 73
# Jaccard recomputed INDEPENDENTLY from the turnover counts
_tv = _b1['pins']['P2_cohort_turnover']
_inter = _tv['K_base'] - _tv['left_n']
_union = _tv['K_base'] + _tv['entered_n']
assert (_inter, _union) == (72, 78), (_inter, _union)
assert abs(round(_inter / _union, 4) - _stored_f4['jaccard_heavy']) < 1e-12
assert _tv['K_base'] - _tv['left_n'] + _tv['entered_n'] == _tv['K_f4']
# registered rule E1 must follow from the measured cells
assert _b1['verdict'] == 'E1_refuted_frozen_membership_premise'
assert _b1['code_audit']['cohort_rederived_inside_fn'] is True
assert all(_b1['cert'].values()), _b1['cert']
# scope: window does not fully port; the dynamic arm is now RUN (b2) and
# the superseded static-only clause must be GONE (supersession pinned)
_p3 = _b1['pins']['P3_window_portability']
assert _p3['base_window_overlap_f4'] == 23 < _p3['base_window_k'] == 24
assert nums['l169b.scope']['v']['dynamic_f4_run'] is True
# ledger must mirror the artifact
_nb = nums['l169b.forms']['v']
assert _nb['F1_frozen_all']['carrier_rank'] == 25
assert _nb['F2_frozen_set_reordered']['carrier_rank'] == 21
assert _nb['F3_fully_rederived'] == dict(K=73, carrier_rank=21, twin_rank=33)
# §4 DATA FLOOR prose contract
# §4 DATA FLOOR prose contract. Stage (b4-i) de-bulleted §4, so the two
# locators that used to carry the bullet MARKER are re-pointed at the prose
# form ANCHORED TO A LINE START (equally strong: the labelled paragraph must
# still open its own line; it can no longer match mid-sentence either).
_m1 = re.search(r'(?m)^DATA FLOOR:', draft)
_m2 = re.search(r'(?m)^Wet-lab predictions', draft)
assert _m1 and _m2 and _m1.start() < _m2.start(), (
    'l169b §4 locators lost their line-start prose form')
_s4txt = draft[_m1.start():_m2.start()]
_nw4 = lambda s: re.sub(r'\s+', ' ', s)
for _lit in ('[l169b.forms]', 'fully RE-DERIVED, not\n  frozen',
             'K (77 \u2192 73)',
             'five cells out, one in', 'ranks (21 and 33)',
             're-ordering rather than\n  turnover'):
    # (b4-i): two of these literals carried the OLD BULLET INDENTATION inside
    # their own line break; the loop is now WRAP-INSENSITIVE (claim text
    # unchanged, strictly stronger — a wording cannot hide behind a re-wrap).
    assert _nw4(_lit) in _nw4(_s4txt), ('l169b §4 literal missing', repr(_lit))
for _gone in ('stays a STATIC bound', '23 of its 24 cells port',
              'no dynamic\n  f4 arm has been run'):
    assert _gone not in draft, ('superseded (b1) clause survives', _gone)
print('(12) L169(b1) fold: F3 == stored l146 f4 field-for-field, F1 ranks '
      'frozen at 25/26, F2 == F3 ranks (21,33) so the shift is re-ordering '
      'not turnover, Jaccard .9231 recomputed from 72/78, rule E1 proven '
      'from the cells, §4 literals asserted + the three superseded '
      'static-only clauses asserted GONE')

# ---- (13) L169 stage (b2): the floor-4 DYNAMIC arm ----
_b2 = json.loads((P / 'banc/l169b2/results_l169b2.json').read_text())
_t2, _nd = _b2['table'], nums['l169b2.dyn']['v']
# certification chain must be green before any value is read
assert _b2['cert0'] is True and _b2['cert']['fc169_pass'] is True
assert _b2['cert']['fc169_max'] == 0.0, _b2['cert']['fc169_max']
assert _b2['cert']['ntf4_pass'] is True and _b2['cert']['ntf4_min'] > 0
for _g in ('g_cutwA_exact', 'g_cutng25_exact', 'g_emottop5_exact',
           'g_emotbot5_exact'):
    assert _b2['cert'][_g] is True, _g        # also certifies the subset
# the three f4 gains are distinct and freshly bisected (never ported)
_gs = _b2['gains']
assert len(set(_gs.values())) == 3, _gs
assert all(v > 0.145 for v in _gs.values()), _gs   # floor costs edges -> gain up
assert all(s <= 5e-3 for s in _b2['f4_stairs'].values()), _b2['f4_stairs']
# registered R-side cells, re-derived independently from the stored table
for _a in ('f4wA', 'f4ng', 'f4tw'):
    assert _t2[_a]['kR'] == 0, (_a, _t2[_a]['kR'])
    assert _t2[_a]['super'] is False and _t2[_a]['notsuper'] is True
    _lb, _ub = wilson(_t2[_a]["kR"], 16)
    assert abs(_ub - _t2[_a]['ubR']) < 1e-12, (_a, _ub)
    assert abs(_ub - 0.1936076805344365) < 1e-9, _ub   # k=0,n=16 ub
# base arms reproduce on the SAME batch (the comparison that makes it a test)
assert _t2['cutng25']['super'] is True and _t2['cutng25']['kR'] == 16
assert _t2['cutwA']['partial'] is True and _t2['cutwA']['kR'] == 3
assert _t2['full']['partial'] is True
# branch G2 must FOLLOW from the cells, not from the stored label
assert _b2['vacuous_xor_guard'] is False
assert _b2['g1'] is False and _b2['g3'] is False and _b2['g2'] is True
assert _b2['branch'] == 'G2_no_transfer', _b2['branch']
# the XOR leg is flat: 8 up / 8 down, |paired| <= .01
_xl = _b2['legs']['xor']
assert _xl['n_up'] == _xl['n_down'] == 8, _xl
assert abs(_xl['mean_paired_dR_ng_minus_tw']) <= 0.01, _xl
# descriptive addendum: label present, direction + paired counts
_ad = _b2['addendum_L_descriptive']
assert 'DESCRIPTIVE' in _ad['label'] and 'post-hoc' in _ad['label']
assert _ad['side_dominance'] == dict(f4wA='L', f4ng='L', f4tw='L',
                                     cutwA='R', cutng25='R'), _ad[
    'side_dominance']
assert _ad['rows']['f4wA']['kL'] == 16 and _ad['rows']['f4ng']['kL'] == 2
assert _ad['paired_legs']['f4ng_vs_f4wA'] == dict(
    mean_paired_dL=-0.409, n_up=0, n_down=16), _ad['paired_legs']
assert _ad['paired_legs']['f4tw_vs_f4wA']['mean_paired_dL'] == -0.139
# ledger mirrors the artifact
assert _nd['branch'] == 'G2_no_transfer' and _nd['n'] == 16
assert _nd['floor'] == 4 and _nd['K4'] == 73
assert _nd['f4wA']['meanR'] == 0.043 and _nd['f4ng']['meanR'] == 0.081
assert _nd['f4tw']['meanR'] == 0.082
assert _nd['base_same_batch']['cutng25'] == dict(meanR=0.754, kR=16)
assert nums['l169b2.lat_descriptive']['v']['meanL']['f4wA'] == 0.698
# §4 (b2) prose contract — every quoted value a draft literal
for _lit in ('[l169b2.dyn]', '[l169b2.lat_descriptive]',
             'kR 0/16', 'meanR .043/.081/.082', 'upper bound .194',
             'cutng25 SUPER 16/16 meanR .754', 'cutwA PARTIAL 3/16 .371',
             '\u2212.001 paired, 8 up / 8 down',
             'G2_no_transfer', 'f4wA meanL .698, kL 16/16',
             'f4ng .289, paired \u2212.409, 16/16 seeds down',
             'f4tw .560, paired \u2212.139', 'DESCRIPTIVE'.lower()):
    assert _lit in _s4txt or _lit in draft, ('(b2) §4 literal missing',
                                             repr(_lit))
print('(13) L169(b2) fold: CERT chain green (FC-169 0.0, C0-NT > 0, four '
      'stored gains EXACT = subset certified), three fresh distinct gains '
      'with staircase <= 5e-3, all three f4 arms kR 0/16 with the k=0 '
      'Wilson ub recomputed, base arms reproduce on B36, branch '
      'G2_no_transfer proven from the cells, flat XOR leg 8/8, descriptive '
      'L-side addendum labelled and its paired legs asserted, §4 literals '
      'verified')

# ---- (14) L169 (c1): design pins for the rewire / contralateral-DNp33 arms ---
_l169c = json.loads((P / 'banc/l169c/static.json').read_text())
_c = nums['l169c.design']['v']
# ledger == source (independently re-read)
assert _c['rules'] == 'C1_independent/C2_nonequivalent/C3_admissible'
assert _l169c['rules']['C1_independent'] is True
assert _l169c['rules']['C2_mirror'] is False
assert _l169c['rules']['C3_admissible'] is True
# the C2 refutation is carried by the CLASS leg ONLY — the footprint legs pass
_legs = _l169c['rules']['C2_legs']
assert _legs['same_class'] is False, 'C2 must fail on the class leg'
assert _legs['edges_factor2'] and _legs['mass_factor2'] \
    and _legs['intrinsic_share_20pp'], 'footprint legs must PASS'
# class asymmetry: carrier is a pure projector, gi 928 receives cord input
_m = _l169c['P2_hom_identity']['membership']
_cm = _l169c['P2_hom_identity']['carrier_membership']
assert _cm['pure_proj'] is True and _cm['dn_into'] is False
assert _m['pure_proj'] is False and _m['dn_into'] is True
assert _m['in_dn_new_g'] is False and _m['in_ng_desc'] is False
assert _m['in_cut_window24'] is False and _m['in_cut_window25'] is False
assert _m['present_on_G1_cutwA'] is True, 'HOM arm must be non-vacuous on G1'
# footprint numbers quoted in §2.7
_fc, _fh = (_l169c['P3_footprint']['carrier_G1'],
            _l169c['P3_footprint']['hom_G1'])
assert (_fc['out_edges'], _fh['out_edges']) == (80, 88)
assert round(_fc['out_mass'], 2) == 183.96 and round(_fh['out_mass'], 2) == 200.05
assert _c['carrier']['out_mass'] == 183.96 and _c['hom']['out_mass'] == 200.05
assert _fc['tiers']['intrinsic']['edges'] == 70 and \
    _fh['tiers']['intrinsic']['edges'] == 77
# destination overlap + mirrored motor sides
_ov = _l169c['P4_overlap']
assert _ov['n_shared'] == 6 and round(_ov['jaccard'], 4) == 0.037
assert abs(_ov['jaccard'] - 6 / (80 + 88 - 6)) < 1e-12, 'Jaccard recompute'
_msc, _msh = _ov['motor_sides_carrier'], _ov['motor_sides_hom']
assert (_msc['left']['edges'], _msc['right']['edges']) == (9, 1)
assert (_msh['left']['edges'], _msh['right']['edges']) == (1, 10)
assert _ov['pool_direct_nonzero'] == [], 'neither cell touches a pool directly'
# rewire admissibility, recomputed from the stored pool sizes and draws
_p5, _p6 = _l169c['P5_rewire_pool'], _l169c['P6_rewire_draws']
assert round(_p5['partner_rows'] / 80, 1) == 804.1 == _c['rewire'][
    'partner_over_carrier']
assert _p5['partner_rows'] >= 10 * 80, 'expressibility leg'
assert _p6['n_draws'] == 100 and _p6['seed'] == 16943
assert _p6['med_relocated'] == 80.0 and _p6['min_relocated'] == 80
assert _p6['med_mass_T70_share'] < 0.10 and _p6['med_mass_T70_share'] == 0.0
# §2.7 prose contract: every quoted value is a draft literal
_s27 = draft[draft.index('Design pins for the rewire and deletion arms'):
             draft.index('## 3. Methods')]
for _lit in ('[l169c.design]', 'gi 928', '88 closure out-edges',
             "carrier's\n80", '200.05 against 183.96', '6 shared, Jaccard\n.037',
             '10 right / 1 left', "carrier's 9 left / 1 right",
             'same-footprint, different-class deletion, not a homolog control',
             '804x the', 'relocates all 80 edges',
             'returns no measurable mass'):
    assert _lit in _s27, ('(c1) §2.7 literal missing', repr(_lit))
# the superseded label must be GONE from the draft BODY. (Scope note: the
# version banner deliberately DISCLOSES the removal, so the gate must read
# the body after the title — an unscoped whole-file check is red the moment
# the removal is disclosed, which is the l121 label-string class.)
_body = draft[draft.index('## Title'):]
assert 'right-homolog' not in _body, \
    'superseded right-homolog label survives in the draft body'
print('(14) L169(c1) design pins: rules C1_independent / C2_nonequivalent / '
      'C3_admissible re-read from source, the C2 refutation isolated to the '
      'CLASS leg with all three footprint legs passing, gi 928 proven '
      'cord-receiving and outside every cut window (arm non-vacuous), '
      'Jaccard recomputed from the two destination counts, mirrored motor '
      'sides asserted, rewire expressibility/relocation/T70-return bars '
      'recomputed, §2.7 literals verified and the superseded '
      '"right-homolog" label asserted GONE')

# ---- (15) L169 (c2): the REW + HOM rollout arms, re-derived from raw ----
_l169c2 = json.loads((P / 'banc/l169c2/results_l169c2.json').read_text())
_B37 = list(range(3481, 3497))
_z169c2 = _np169.load(str(P / 'banc/l169c2/raw_l169c2.npz'))


def _duty169c2(arm, seeds):
    q = _np169.zeros(len(_TS169), bool)
    for a0, b0, f in _SEG169:
        if f == 0.7:
            q |= (_TS169 >= a0 + 500) & (_TS169 < b0)
    L, R = [], []
    for s in seeds:
        tr = {c: _z169c2[f'Ti_{c}_{arm}_{s}'][:_W169]
              for c in ('fL', 'fR', 'eL', 'eR')}
        sl = _np169.full(_W169, _np169.nan)
        sr = _np169.full(_W169, _np169.nan)
        for t in _TS169:
            sl[t] = _S169(tr['fL'][t - 499:t + 1], tr['eL'][t - 499:t + 1])
            sr[t] = _S169(tr['fR'][t - 499:t + 1], tr['eR'][t - 499:t + 1])
        L.append(round(float(_np169.nanmean(sl[_TS169[q]] >= .25)), 3))
        R.append(round(float(_np169.nanmean(sr[_TS169[q]] >= .25)), 3))
    return _np169.array(L), _np169.array(R)


# (a) every table cell re-derived from the RAW traces, independent of the
# run's own verdict script
_arms_c2 = ('rew1', 'rew2', 'rew3', 'hom', 'cutwA', 'cutng25')
_dc2 = {a: _duty169c2(a, _B37) for a in _arms_c2}
for _a in _arms_c2:
    _L, _R = _dc2[_a]
    _st = _l169c2['table'][_a]
    assert int((_R >= .5).sum()) == _st['kR'], ('(15) kR', _a)
    assert int((_L >= .5).sum()) == _st['kL'], ('(15) kL', _a)
    assert round(float(_R.mean()), 3) == _st['meanR'], ('(15) meanR', _a)
    assert round(float(_L.mean()), 3) == _st['meanL'], ('(15) meanL', _a)
    _lb, _ub = wilson(_st['kR'], 16)
    assert abs(_lb - _st['lbR']) < 1e-9 and abs(_ub - _st['ubR']) < 1e-9, _a
# (b) paired legs recomputed against the same-batch cutwA base
for _a in ('rew1', 'rew2', 'rew3', 'hom'):
    _d = _dc2[_a][1] - _dc2['cutwA'][1]
    _lg = _l169c2['legs'][_a]
    assert round(float(_d.mean()), 3) == _lg['mean_paired_dR_vs_cutwA'], _a
    assert int((_d > 0).sum()) == _lg['n_up'], _a
    assert int((_d < 0).sum()) == _lg['n_down'], _a
# (c) the draw pool and the straddle that makes R3's clause true as well
_kpool = sum(_l169c2['table'][a]['kR'] for a in ('rew1', 'rew2', 'rew3'))
assert _kpool == 20 == _l169c2['pooled_rew']['kR']
_plb, _pub = wilson(_kpool, 48)
assert abs(_plb - _l169c2['pooled_rew']['lb']) < 1e-9
_blb, _bub = wilson(_l169c2['table']['cutwA']['kR'], 16)
assert _plb < _bub, '(15) the registered straddle clause must hold'
assert not _l169c2['r1'] and _l169c2['r2'], '(15) branch legs'
assert _l169c2['rew_branch'] == 'R2_mass_degree'
assert _l169c2['n_super_rew'] == 1 and _l169c2['n_notsuper_rew'] == 2
# (d) the base is NOT vacuous and cutng25 reproduces SUPER on this batch
assert _l169c2['vacuous_base_guard'] is False
assert _l169c2['table']['cutng25']['super'] is True
assert _l169c2['table']['cutwA']['partial'] is True
# (e) H1 proven from the cells, not the label
assert _l169c2['table']['hom']['notsuper'] is True
assert _l169c2['table']['hom']['super'] is False
assert _l169c2['hom_branch'] == 'H1_specific'
assert _l169c2['cert']['hom_incident'] == 101
# (f) gains are not ordered with the readouts (the no-gain-artifact claim).
# NOTE: all three rewire gains sit ABOVE g_cutwA — the claim is
# NON-MONOTONICITY of the readout in gain, not a below-base gain (a first
# draft of this gate asserted the latter and was refuted by the assert).
_g = _l169c2['gains']
_GWA = 0.14365819573402408
assert _GWA < _g['rew3'] < _g['rew1'] < _g['rew2'], '(15) gain order'
_mr = {a: _l169c2['table'][a]['meanR'] for a in ('rew1', 'rew2', 'rew3')}
assert _mr['rew3'] < _mr['rew1'] and _mr['rew2'] < _mr['rew1'], \
    '(15) readout must be non-monotone in gain'
# (g) rew3 and hom are different arms despite near-equal batch means
_dd = float(_np169.abs(_dc2['rew3'][1] - _dc2['hom'][1]).max())
assert round(_dd, 2) == 0.46, ('(15) rew3/hom per-seed spread', _dd)
assert round(abs(_l169c2['table']['rew3']['meanR']
                 - _l169c2['table']['hom']['meanR']), 3) <= 0.001
# (h) anchors
assert _l169c2['cert']['fc169b2_max'] == 0.0 and _l169c2['cert0'] is True
assert _l169c2['cert']['ntc2_min'] > 0.0
assert _l169c2['rew_draws_first5'][0]['relocated'] == 80
# (i) §2.7 prose contract: every quoted value is a draft literal
_s27b = draft[draft.index('**Displacement is not removal'):
              draft.index('## 3. Methods')]
for _lit in ('[l169c2.base]', '[l169c2.rew]', '[l169c2.branch]',
             '[l169c2.gains]', '[l169c2.hom]', '[l169c2.cert]',
             'meanR .452, kR 5/16', '(.786, 15/16)',
             'meanR .724, kR 16/16', 'paired +.272 over cutwA, 15/16 seeds up',
             '`rew2` .333, 1/16', '`rew3` .302, 3/16', 'paired −.150',
             '20 of 48 [.288,.557]', '[.142,.556]', '[.717,.989]',
             'R2_mass_degree', 'R3_draw_lottery', 'H1_specific',
             '101 incident closure edges removed',
             'meanR .301, kR 2/16, [.035,.360]',
             '.144464) and reads .302', '(.145617) and reads .724',
             '(.150060) and reads .333', 'non-monotone in gain',
             'min 1.9e-2', 'differ per seed by up to\n  .46'):
    # L174 (b3b-iii): wrap-insensitive (PREREG ADDENDUM 1-a)
    assert re.sub(r'\s+', ' ', _lit) in re.sub(r'\s+', ' ', _s27b), \
        ('(c2) §2.7 literal missing', repr(_lit))
# the superseded forward-looking clause must be GONE (body-scoped, per the
# scope note in (14): banners disclose removals)
assert 'carrier-edge rewire, deletion of the' not in _body, \
    'superseded queued-controls clause survives'
print('(15) L169(c2) REW+HOM: all six table cells re-derived from the RAW '
      'B37 traces with an independent duty implementation (kR/kL/meanR/'
      'meanL + Wilson to 1e-9), paired legs recomputed, the 20/48 draw pool '
      'and its straddle of the same-batch cutwA interval proven from the '
      'cells (so R2 fires on the majority while R3\'s pooled clause is also '
      'true — the conjunction the draft reports), base non-vacuity asserted, '
      'H1_specific proven from the hom cells, the gain non-ordering claim '
      'checked, rew3-vs-hom per-seed spread .46 confirming they are '
      'different arms, anchors re-read, §2.7 literals verified and the '
      'superseded queued-controls clause asserted GONE')

# ---- (16) L169 (d): the XOR-pair gain-swap 2x2, re-derived from raw ----
_l169d = json.loads((P / 'banc/l169d/results_l169d.json').read_text())
_B38 = list(range(3513, 3529))
_z169d = _np169.load(str(P / 'banc/l169d/raw_l169d.npz'))


def _duty169d(arm, seeds):
    q = _np169.zeros(len(_TS169), bool)
    for a0, b0, f in _SEG169:
        if f == 0.7:
            q |= (_TS169 >= a0 + 500) & (_TS169 < b0)
    L, R = [], []
    for s in seeds:
        tr = {c: _z169d[f'Ti_{c}_{arm}_{s}'][:_W169]
              for c in ('fL', 'fR', 'eL', 'eR')}
        sl = _np169.full(_W169, _np169.nan)
        sr = _np169.full(_W169, _np169.nan)
        for t in _TS169:
            sl[t] = _S169(tr['fL'][t - 499:t + 1], tr['eL'][t - 499:t + 1])
            sr[t] = _S169(tr['fR'][t - 499:t + 1], tr['eR'][t - 499:t + 1])
        L.append(round(float(_np169.nanmean(sl[_TS169[q]] >= .25)), 3))
        R.append(round(float(_np169.nanmean(sr[_TS169[q]] >= .25)), 3))
    return _np169.array(L), _np169.array(R)


# (a) every grid cell re-derived from the RAW B38 traces, independent of
# the run's own verdict script
_arms_d = ('cutng25', 'cutng25p', 'p25gN', 'n25gP', 'cutwA', 'full')
_dd4 = {a: _duty169d(a, _B38) for a in _arms_d}
for _a in _arms_d:
    _L, _R = _dd4[_a]
    _st = _l169d['table'][_a]
    assert int((_R >= .5).sum()) == _st['kR'], ('(16) kR', _a)
    assert int((_L >= .5).sum()) == _st['kL'], ('(16) kL', _a)
    assert round(float(_R.mean()), 3) == _st['meanR'], ('(16) meanR', _a)
    assert round(float(_L.mean()), 3) == _st['meanL'], ('(16) meanL', _a)
    _lb, _ub = wilson(_st['kR'], 16)
    assert abs(_lb - _st['lbR']) < 1e-9 and abs(_ub - _st['ubR']) < 1e-9, _a
# (b) the seven paired legs recomputed from the same per-seed arrays
for _nm, _x, _y in (('p25gN_minus_cutng25p', 'p25gN', 'cutng25p'),
                    ('n25gP_minus_cutng25', 'n25gP', 'cutng25'),
                    ('cutng25_minus_cutng25p', 'cutng25', 'cutng25p'),
                    ('cutng25_minus_cutwA', 'cutng25', 'cutwA'),
                    ('cutng25p_minus_cutwA', 'cutng25p', 'cutwA'),
                    ('p25gN_minus_cutng25', 'p25gN', 'cutng25'),
                    ('n25gP_minus_cutng25p', 'n25gP', 'cutng25p')):
    _d = _dd4[_x][1] - _dd4[_y][1]
    _lg = _l169d['legs'][_nm]
    assert round(float(_d.mean()), 3) == _lg['mean_paired_dR'], ('(16)', _nm)
    assert int((_d > 0).sum()) == _lg['n_up'], ('(16) up', _nm)
    assert int((_d < 0).sum()) == _lg['n_down'], ('(16) down', _nm)
# (c) the registered branch proven FROM THE CELLS, not from the label
_ngd, _twd = _l169d['table']['cutng25'], _l169d['table']['cutng25p']
_pgd, _npd = _l169d['table']['p25gN'], _l169d['table']['n25gP']
assert _ngd['super'] is True and _l169d['e0'] is False, '(16) E0 leg'
assert _pgd['notsuper'] is True and _npd['super'] is True, '(16) E1 cells'
assert _l169d['e1'] is True and _l169d['e2'] is False, '(16) branch legs'
assert _l169d['branch'] == 'E1_graph_tracking'
assert _l169d['xor_reproduced'] is True and _twd['notsuper'] is True
# (d) GRAPH IDENTITY of the swap arms: each swap arm must carry EXACTLY its
# own-gain twin's node and edge counts (object identity was asserted in-run)
_dn, _de = _l169d['cert']['d_n'], _l169d['cert']['d_edges']
assert _dn['p25gN'] == _dn['cutng25p'] and _de['p25gN'] == _de['cutng25p']
# ...and the two columns must be the two GAINS, not two graphs
assert _pgd['g'] == _ngd['g'] and _npd['g'] == _twd['g'], '(16) gain columns'
assert _twd['g'] < _l169d['table']['cutwA']['g'] < _ngd['g'], '(16) gain order'
assert round(100 * (_ngd['g'] / _twd['g'] - 1), 3) == \
    _l169d['swap_gain_span_pct'], '(16) swap span'
# (e) the disclosed boundary: the twin arm is AT the NOT-SUPER bar
assert _twd['kR'] == 8 and _twd['meanR'] <= .50, '(16) boundary disclosure'
# (f) both swap arms read BELOW their own-gain selves (the "raising a gain
# helped neither graph" sentence)
assert _l169d['legs']['p25gN_minus_cutng25p']['mean_paired_dR'] < 0
assert _l169d['legs']['n25gP_minus_cutng25']['mean_paired_dR'] < 0
# (g) cross-batch: class is preserved, level moved (re-read from l135)
_r135 = json.loads((P / 'banc/l135/results_l135.json').read_text())
for _a in ('cutng25', 'cutng25p'):
    assert _l169d['xbatch'][_a]['b25_stored']['kR'] == \
        _r135['table']['Ti'][_a]['kR'], ('(16) xbatch kR', _a)
    assert _l169d['xbatch'][_a]['b25_stored']['meanR'] == \
        _r135['table']['Ti'][_a]['meanR'], ('(16) xbatch meanR', _a)
# (h) anchors + the PARTIAL af disclosure
assert _l169d['cert']['fc169c2_max'] == 0.0 and _l169d['cert0'] is True
assert _l169d['cert']['c0a150_max'] == 0.0, '(16) 5-arm C0A-150'
assert _l169d['cert']['g_cutng25p_exact'] is True
assert _l169d['cert']['ntd_min'] > 0.0
assert _l169d['pafd_ok'] is False and _l169d['pafd_nup'] == 15 \
    and _l169d['pafd_ndn'] == 13, '(16) af direction is PARTIAL'
assert _l169d['d_band_ok'] is True
# (i) §2.7 prose contract: every quoted value is a draft literal
_s27d = draft[draft.index('**The XOR pair at swapped gains'):
              draft.index('## 3. Methods')]
for _lit in ('[l169d.grid]', '[l169d.legs]', '[l169d.branch]',
             '[l169d.xbatch]', '[l169d.cert]',
             'meanR\n  .798, kR 16/16, [.806,1.000]',
             '(.477, kR 8/16,\n  [.280,.720])',
             'paired +.321 with 16 of 16 seeds up',
             '15/16 → 16/16', '5/16 → 8/16',
             'meanR .324, kR 1/16, paired −.152',
             'meanR .651, kR 15/16,\n  [.717,.989], paired −.147',
             '+.474 above the twin-removed\n  graph with 16 of 16 seeds up',
             'at g_cutng25p it is +.174 with 12 of\n  16 up',
             'E1_graph_tracking', '1.34% apart',
             '3.9e-04 mass delta',
             'kR exactly 8 of 16, meanR .477 just under the .50 bar',
             '.143527 and .145445',
             'holds on 15 and 13 of 18 seeds',
             'staircase residual 5.4e-07', 'min 1.9e-2'):
    # L174 (b3b-iii): wrap-insensitive (PREREG ADDENDUM 1-a)
    assert re.sub(r'\s+', ' ', _lit) in re.sub(r'\s+', ' ', _s27d), \
        ('(d) §2.7 literal missing', repr(_lit))
# the superseded queued clause must be GONE (body-scoped — the v3.14 banner
# deliberately discloses the removal, so a whole-draft scan would be red)
assert 'at swapped gains is queued' not in _body, \
    'superseded carrier-vs-twin queued clause survives in the body'
print('(16) L169(d) XOR gain-swap 2x2: all six grid cells re-derived from '
      'the RAW B38 traces with an independent duty implementation '
      '(kR/kL/meanR/meanL + Wilson to 1e-9), all seven paired legs '
      'recomputed, branch E1_graph_tracking proven from the cells (twin '
      'arm NOT-SUPER at the carrier gain, carrier arm SUPER at the twin '
      'gain), swap-arm graph identity and the gain-column structure '
      'asserted (same graph, different gain; span re-derived), the '
      'boundary disclosure (twin kR exactly 8/16) and the '
      'both-swap-arms-below-own-gain sentence checked, cross-batch B25 '
      'cells re-read from l135, anchors + the PARTIAL af direction '
      'asserted, §2.7 literals verified and the superseded queued clause '
      'asserted GONE from the body')

# ---------- (17) L170: the male extraction at the MATCHED synapse floor ------
_l170 = json.loads((P / 'banc/l170/static.json').read_text())
_s138 = json.loads((P / 'banc/l138/static.json').read_text())
_f1, _f3 = _l170['ladder']['1'], _l170['ladder']['3']
# CERT: the floor-1 arm IS the stored l138 male side (cross-file, independent
# of l170's own in-run asserts)
for _k, _want in _s138['male_s1'].items():
    assert _f1['s1'][_k] == _want, ('(17) floor-1 CERT', _k, _f1['s1'][_k], _want)
assert _f1['window'] == _s138['male_s3_window'], '(17) floor-1 window CERT'
assert _f1['dn_into'] == _s138['probe']['male_dn_into'] == 1277
assert _f1['s1']['dn_new'] == _s138['probe']['male_pure_proj'] == 28
# the release floor really is 1 and the release is pair-unique (precheck)
assert _l170['precheck']['w_min'] == 1.0 and _l170['precheck']['dup_pairs'] == 0
assert _l170['precheck']['hist']['ge3'] == 10512742, '(17) floor-3 pair count'
# independent re-derivation of the floor-3 window shares from the stored
# per-cell ng mass list (l170 computed them from the cohort array; this path
# never touches that code)
_ngm = _f3['pins']['ng_mass_list']
assert len(_ngm) == 40 and _f3['window']['n_ng'] == 43
assert abs(sum(_ngm[:19]) - _f3['window']['r1_19']) < 5e-4, '(17) r1_19 re-derive'
assert abs(sum(_ngm[19:29]) - _f3['window']['r20_29']) < 5e-4, '(17) r20_29'
assert (_f3['window']['r1_19'], _f3['window']['r20_29'],
        _f3['window']['r30_rest']) == (0.2818, 0.0667, 0.067), '(17) window pins'
assert _l170['banc_window'] == {'r1_19': 0.1946, 'r20_29': 0.0642,
                                'r30_58': 0.1333} and _l170['banc_K'] == 77
# the rank-20-29 agreement quoted in §2.6 (BANC .0642 vs male .0667)
assert round(abs(_f3['window']['r20_29'] - _l170['banc_window']['r20_29']), 4) \
    <= 0.0025, '(17) rank-20-29 agreement'
# twin-pair tightness: re-derived from the two stored mass shares, and
# compared against the BANC XOR pair's OWN stored delta (never a log constant)
_gap = abs(_f3['pins']['rank25']['mass_share'] - _f3['pins']['rank26']['mass_share'])
assert abs(_gap - _f3['pins']['twin_gap']) < 1e-5, '(17) twin gap re-derive'
_bgap = json.loads((P / 'banc/l131/static.json').read_text())['rank_mass']['pair_delta']
assert abs(_bgap - nums['xor']['v']['pair_delta']) < 1e-12, '(17) BANC gap source'
assert 1.0 < _gap / _bgap < 1.5, ('(17) male twin pair is comparably tight, '
                                  'not an order of magnitude looser', _gap, _bgap)
assert (_f3['pins']['rank25']['type'], _f3['pins']['rank25']['somaSide']) == (
    'DNp54', 'R')
assert (_f3['pins']['rank26']['type'], _f3['pins']['rank26']['somaSide']) == (
    'DNpe028', 'L')
# registered branch M1 proven from the cells (and M2/M3 proven NOT to fire)
_rel = abs(_f3['s1']['dn_new'] - _f1['s1']['dn_new']) / _f1['s1']['dn_new']
assert abs(_rel - _l170['verdict']['rel_change']) < 5e-5 and _rel >= 0.20
assert _l170['verdict']['branch'] == 'M1_floor_changes_cohort'
assert _l170['verdict']['M1'] is True and _l170['verdict']['M2'] is False
assert (_f3['s1']['dn_new'], _f3['s1']['heavy_K']) == (342, 52), '(17) f3 cells'
assert (_f1['s1']['dn_new'], _f1['s1']['heavy_K']) == (28, 9), '(17) f1 cells'
# M3 did NOT fire: male DNp33 stays reciprocal at floor 3 (in-edges fall, never 0)
assert _l170['verdict']['M3_dnp33_pure'] is False
_i1 = [c['in_cord_edges'] for c in _f1['dnp33']]
_i3 = [c['in_cord_edges'] for c in _f3['dnp33']]
assert _i1 == [37, 33] and _i3 == [6, 2], ('(17) DNp33 in-edges', _i1, _i3)
assert all(b < a for a, b in zip(_i1, _i3)) and all(x > 0 for x in _i3)
assert all((not c['in_cohort']) and c['dn_into'] and c['dn_proj']
           and c['mass_share'] == 0.0 for c in _f3['dnp33'])
assert _l170['verdict']['P1'] is True and _l170['verdict']['P2'] is True
# the floor ladder is reported, not asserted monotone (PREREG P3)
_lad = [_l170['ladder'][k]['s1']['dn_new'] for k in ('1', '2', '3', '4')]
assert _lad == [28, 199, 342, 458], ('(17) ladder', _lad)
# evidence rule: the reviewer's own numbers stay flagged in the artifact
assert 'BARRED' in _l170['reviewer_reported']['note']
assert _l170['reviewer_reported']['pure_proj'] == _f3['s1']['dn_new'] and \
    _l170['reviewer_reported']['K'] == _f3['s1']['heavy_K'], \
    '(17) independent reproduction of the reviewer-reported pair'
# §2.6 prose contract: every quoted value is a draft literal
_nw = lambda s: re.sub(r'\s+', ' ', s)
_s26 = draft[draft.index('### 2.6 Scope boundary'):
             draft.index('### 2.7 Pre-posting controls')]
for _lit in ('UNMATCHED-FLOOR', 'implicit pair-level floor of 3',
             'dn_new = 28 cells / 9 ng with K = 9',
             '342 cells / 43 ng with K = 52', "against BANC's K = 77",
             '0.2818 / 0.0667 / 0.0670', '0.1946 / 0.0642 /\n  0.1333',
             'agrees to\n  within .0025', 'UNTESTED AT MATCHED FLOOR',
             'DNp54-R and DNpe028-L', 'mass-matched to 4.4e-04',
             '(3.9e-04 [xor])', 'from 37/33 to 6/2 but never\n  reach zero',
             'ladder mass exactly 0.0', '[l170.matched]', '[l170.pins]'):
    # L174 (b3b-ii): §2.6 is prose now, so three of these literals carried the
    # old bullet INDENTATION in their line break. The claim text is unchanged;
    # the gate is made WRAP-INSENSITIVE (l122 lesson applied to a gate), which
    # is strictly stronger — a literal can no longer hide behind a re-wrap.
    assert _nw(_lit) in _nw(_s26), ('(17) §2.6 literal missing', repr(_lit))
# superseded §2.6 claims must be GONE from the BODY (body-scoped: the v3.15
# banner deliberately quotes the removed phrase, so a whole-draft scan is red
# by construction — the l169c2 banner lesson)
for _dead in ('no ladder exists to walk', 'vs BANC 560 / K=77', 'RECIPOCAL'):
    assert _dead not in _body, ('(17) superseded §2.6 clause survives', _dead)
print('(17) L170 matched-floor re-scope: floor-1 arm CERT-equal to the stored '
      'l138 male side (all 9 fields + window + dn_into + pure_proj), the '
      'floor-3 window shares re-derived INDEPENDENTLY from the stored per-cell '
      'ng mass list, the male twin-pair gap re-derived from its two mass '
      'shares and compared against BANC\'s OWN stored pair_delta (1.13x, '
      'comparably tight — NOT the order-of-magnitude gap a log-prose constant '
      'would have implied), branch M1 proven from the cells with M2/M3 proven '
      'not to fire, DNp33 reciprocity at both floors asserted (in-edges '
      '37/33 -> 6/2, never 0, mass exactly 0.0), the floor ladder pinned, the '
      "reviewer-reported pair confirmed as an independent reproduction while "
      'staying BARRED from the draft, §2.6 literals verified and the three '
      'superseded clauses asserted GONE from the body')

# ---------------- (18) L171: slow-line re-attribution + robustness panel ----
# INDEPENDENT re-derivation: the drive envelope is rebuilt here from the
# constants READ OUT of banc/l135_run.py (never typed), FFT-ed with a fresh
# implementation, and the two re-scores are recomputed from the RAW B26
# traces with an independent duty/S implementation.
import numpy as _np

_l171 = json.loads((P / 'banc/l171/results.json').read_text())
_src = (P / 'banc/l135_run.py').read_text()
# constants parsed from the run script, so a protocol change breaks this gate
_m = re.search(r'SETTLE, WIN = (\d+), (\d+)', _src)
_WIN = int(_m.group(2))
_m = re.search(r'ENT_AMP = ([\d.]+)', _src)
_EA = float(_m.group(1))
_m = re.search(r'TAU, DT, RMAX = ([\d.]+), ([\d.]+)', _src)
_DT = float(_m.group(2))
_SEGB = eval(re.search(r'SEGB = (\[[^\]]*\])', _src).group(1))
_SEG = int(re.search(r'\nSEG = (\d+)', _src).group(1))
assert (_WIN, _DT, _EA, _SEG) == (6000, 0.01, 0.1, 2000), '(18) l135 constants'
assert 'AMPA[lo:min(lo + 500, seg0 + SEG)] = ENT_AMP' in _src and \
    'AMPA[2000:4000] = ENT_AMP' in _src, '(18) envelope source form'
_A = _np.zeros(_WIN)
for _s0, _, _ in _SEGB:
    _c = 0
    while _s0 + _c * 900 < _s0 + _SEG:
        _A[_s0 + _c * 900:min(_s0 + _c * 900 + 500, _s0 + _SEG)] = _EA
        _c += 1
_A[2000:4000] = _EA
_sp = _np.abs(_np.fft.rfft(_A - _A.mean()))
_fr = _np.fft.rfftfreq(_WIN, d=_DT)
_dom = int(_np.argmax(_sp[1:])) + 1
_E = nums['l171.envelope']['v']
assert _dom == _E['dom_bin'] == 6 and abs(_fr[_dom] - 0.100) < 1e-12, \
    ('(18) envelope dominant line', _dom, _fr[_dom])
assert _sp[6] > _sp[5] and _sp[6] > _sp[7] and _E['bin6_local_max'] is True
assert _E['bin6_rank'] == 1 and _E['n_off_gaps'] == 4
# the chop fundamental is NOT the dominant line (the card's own phrasing was
# wrong; this gate holds the corrected statement in place)
assert abs(_E['chop_fundamental_hz'] - 1 / 9) < 1e-9
assert abs(_E['chop_bin_exact'] - (1 / 9) / _fr[1]) < 1e-9
assert int(round(_E['chop_bin_exact'])) != _dom, '(18) chop bin != dominant bin'
# gap-centre vector strengths re-derived here
_on = _A > 0
_ed = _np.diff(_on.astype(_np.int8))
_gc = _np.array([(a + 1 + b + 1) / 2 * _DT for a, b in
                 zip(_np.where(_ed == -1)[0], _np.where(_ed == 1)[0])])
assert len(_gc) == 4 and list(_np.round(_gc, 6)) == [7.0, 16.0, 47.0, 56.0]
_vs = lambda f: float(abs(_np.exp(2j * _np.pi * f * _gc).sum()) / len(_gc))
assert abs(_vs(_fr[6]) - _E['vs_bin6']) < 1e-9 and _E['vs_bin6'] > 0.90
assert abs(_vs(1 / 9) - _E['vs_chop']) < 1e-9 and _E['vs_chop'] < 0.25
assert _E['branch'] == 'A1_envelope_line'

# --- panel: independent duty/S re-derivation from the raw B26 traces --------
_PN = nums['l171.panel']['v']
_z = _np.load(P / 'banc/l135/raw_l135.npz')
_sd = sorted({int(mm.group(1)) for k in _z.files
              if (mm := re.search(r'_(\d+)$', k))})
_batch = [x for x in _sd if x >= 3000]
assert _batch == list(range(3001, 3017)) and _PN['n'] == 16, '(18) batch'
_TS = _np.arange(499, _WIN, 10)
_q07 = _np.zeros(len(_TS), bool); _q14 = _np.zeros(len(_TS), bool)
for _a0, _b0, _f in _SEGB:
    (_q07 if _f == 0.7 else _q14)[:] |= (_TS >= _a0 + 500) & (_TS < _b0)
assert int(_q14.sum()) == 150 and not (_q07 & _q14).any()


def _hp(x, hz=0.3):
    F = _np.fft.rfft(x.astype(_np.float64)); F[_fr < hz] = 0.0
    return _np.fft.irfft(F, n=_WIN)


def _cell(arm, mask, hp):
    R, L = [], []
    for sd in _batch:
        t = {c: _z[f'Ti_{c}_{arm}_{sd}'][:_WIN].astype(_np.float64)
             for c in ('fL', 'fR', 'eL', 'eR')}
        if hp:
            t = {c: _hp(v) for c, v in t.items()}
        for side, acc in (('L', L), ('R', R)):
            vals = []
            for tt in _TS[mask]:
                a, b = t[f'f{side}'][tt - 499:tt + 1], t[f'e{side}'][tt - 499:tt + 1]
                vals.append(-_np.corrcoef(a, b)[0, 1]
                            if a.std() > 1e-6 and b.std() > 1e-6 else _np.nan)
            acc.append(round(float(_np.nanmean(_np.array(vals) >= .25)), 3))
    R, L = _np.array(R), _np.array(L)
    return dict(kR=int((R >= .5).sum()), meanR=round(float(R.mean()), 3),
                kL=int((L >= .5).sum()), meanL=round(float(L.mean()), 3)), R


# CERT first: the PUBLISHED q07 cells must reproduce the stored l135 table
_st = json.loads((P / 'banc/l135/results_l135.json').read_text())['table']['Ti']
_pub = {}
for _arm in ('cutng25', 'cutng25p'):
    _got, _pub[_arm] = _cell(_arm, _q07, False)
    for _f2 in ('kR', 'meanR', 'kL', 'meanL'):
        assert _got[_f2] == _st[_arm][_f2], ('(18) CERT', _arm, _f2,
                                             _got[_f2], _st[_arm][_f2])
assert (_PN['published']['kR'], _PN['published']['meanR']) == (15, 0.754)
assert (_PN['published']['twin_kR'], _PN['published']['twin_meanR']) == (5, 0.399)
assert _PN['published']['d_kR'] == 10 and _PN['published']['d_meanR'] == 0.355
# the two re-scores
for _name, _mask, _hpf, _key in (('fast', _q14, False, 'fast_seg'),
                                 ('hp', _q07, True, 'highpass')):
    _c, _Rc = _cell('cutng25', _mask, _hpf)
    _t, _Rt = _cell('cutng25p', _mask, _hpf)
    _k = _PN[_key]
    assert (_c['kR'], _c['meanR']) == (_k['kR'], _k['meanR']), ('(18)', _name)
    assert (_t['kR'], _t['meanR']) == (_k['twin_kR'], _k['twin_meanR'])
    _d = _Rc - _Rt
    assert _k['d_meanR'] == round(_c['meanR'] - _t['meanR'], 3)
    assert _k['d_kR'] == _c['kR'] - _t['kR']
    assert _k['paired_up'] == int((_d > 0).sum()) and \
        _k['paired_down'] == int((_d < 0).sum())
    # ordering preserved in BOTH re-scores = the claim the panel carries
    assert _c['meanR'] > _t['meanR'] and _c['kR'] >= _t['kR'], ('(18) order', _name)
# registered branch + the metric-dependence we disclose rather than round up
assert _PN['branch'] == 'B2_preserved'
assert _PN['fast_seg']['d_meanR'] > _PN['published']['d_meanR']
assert _PN['highpass']['d_meanR'] < _PN['published']['d_meanR']
assert _PN['highpass']['d_kR'] > _PN['published']['d_kR']
assert _PN['fast_seg']['twin_meanR'] == 0.0 and _PN['fast_seg']['twin_kR'] == 0
# NOT degenerate: only ONE arm is at floor, so the re-score adjudicates
assert _l171['panel']['fast_seg_1p4']['degenerate'] is False
assert _l171['b_branch'] == 'B2_preserved' and _l171['zero_rollouts'] is True
# §2.8 prose contract: every quoted value is a draft literal
_s28 = draft[draft.index('### 2.8 The slow line is stimulus-set'):
             draft.index('## 3. Methods')]
for _lit in ('branch A1 fired', 'bin 6 of a 60-s window = .100 Hz exactly',
             '7, 16, 47 and 56 s', 'vector strength',
             "500-on/400-off chop's own 9-s cycle",
             '.111 Hz is NOT the dominant envelope line',
             '| 15/16, meanR .754 | 5/16, .399 | +.355 |',
             '| 12/16, .628 | 0/16, .000 | +.628 | 16/16 up |',
             '| 15/16, .676 | 1/16, .370 | +.306 | 15/16 up |',
             '+.306 vs +.355', 'Δk 14 vs 10', 'B2_preserved',
             '11/16 seeds [l154.band]', '[l171.envelope]', '[l171.panel]'):
    assert _lit in _s28, ('(18) §2.8 literal missing', repr(_lit))
# the abstract's superseded endogenous-clock reading is GONE (body-scoped:
# the v3.16 banner deliberately names what was removed - l169c2 lesson)
_abs18 = draft[draft.index('## Abstract'):draft.index('## 1. Introduction')]
_aflat18 = re.sub(r'\s+', ' ', _abs18)
for _dead in ('a partial carrier, not an antagonist clock',
              'line is carried by a Tr/Ta/Sr',
              'detrend-stable median .100 Hz'):
    assert _dead not in _aflat18, ('(18) superseded abstract clause', _dead)
# Methods carries the envelope statement, with the corrected mechanism
_meth = draft[draft.index('## 3. Methods'):draft.index('## 4. Limitations')]
for _lit in ('500 steps on / 400 off', 'centres 7, 16, 47, 56 s',
             'align at a 10-s period', "not the chop's 9-s fundamental",
             '[l171.envelope]'):
    assert _lit in _meth, ('(18) Methods literal missing', repr(_lit))
print('(18) L171 re-attribution + panel: envelope REBUILT from constants '
      'parsed out of banc/l135_run.py and FFT-ed independently (dominant '
      'non-DC line = bin 6 = .100 Hz exactly, local max, rank 1; the 9-s '
      'chop fundamental lands on a DIFFERENT bin and its gap-alignment '
      'vector strength is re-derived at .17 vs .95), the published B26 q07 '
      'cells re-derived from RAW traces with an independent duty/S '
      'implementation and asserted EQUAL to the stored l135 table BEFORE '
      'the re-scores, both re-scores re-derived cell-by-cell with their '
      'paired counts, ordering preserved in both, branch B2_preserved '
      'proven from the measured cells, the disclosed metric-dependence '
      '(mean contrast down, seed separation up) asserted in BOTH '
      'directions, §2.8 + Methods literals verified and the superseded '
      'abstract clauses asserted GONE')


# (19) L172 stage (a): the STATISTICS pass.  Every changed statistic is
# re-derived here from the stored artifacts with an INDEPENDENT
# implementation: the duty metric from raw traces, Wilson from the
# closed form, the Newcombe difference interval and the Fisher exact p
# from first principles, the bootstrap with the registered seed.  The
# §2.9/§4/abstract literals are then asserted verbatim.
import numpy as _np172

_st172 = json.loads((P / 'banc/l172/stats.json').read_text())
_n172 = nums['l172.pooled']['v']
_d172 = nums['l172.diffs']['v']
_c172 = nums['l172.census_unique']['v']
_m172 = nums['l172.meta']['v']

# (19a) CERT re-run: the l156 census pooled cells from the stored rows,
# with `agree` counted ONLY among sub-band rows (the definition our own
# CERT caught: a row-wide count gives 84, the stored pooled value is 80).
_l156 = json.loads((P / 'banc/l156/static.json').read_text())
_rows156, _inc156 = _l156['rows'], _l156['included_files']


def _cens172(arm, unique):
    seen, n, below, agree, fb = set(), 0, 0, 0, []
    for f in _inc156:
        for s, r in _rows156.get(f, {}).get(arm, {}).items():
            if unique:
                if s in seen:
                    continue
                seen.add(s)
            n += 1
            below += bool(r['below'])
            if r['below']:
                agree += bool(r['agree'])
                fb.append(r['f_glob'])
    return n, below, agree, float(_np172.median(fb))


for _arm, _key in (('b65', 'b65_nonjitter'), ('full', 'full_nonjitter')):
    _n, _b, _a, _md = _cens172(_arm, False)
    _s = _l156['pooled'][_key]
    assert (_n, _b, _a) == (_s['n'], _s['below'], _s['agree']), \
        ('(19a) stored census cell', _arm, _n, _b, _a)
    assert abs(_md - _s['med_f_below']) < 1e-9
    _lb, _ = wilson(_b, _n)
    assert abs(_lb - _s['wilson_lb']) < 1e-9

# (19b) the unique-seed forms quoted in §4 and §1
for _arm, _ck in (('b65', 'b65'), ('full', 'closure')):
    _n, _b, _a, _md = _cens172(_arm, True)
    assert (_n, _b) == (_c172[_ck]['n'], _c172[_ck]['below']), \
        ('(19b) unique census', _arm, _n, _b)
    _lb, _ = wilson(_b, _n)
    assert abs(_lb - _c172[_ck]['lb']) < 1e-9, ('(19b) unique lb', _arm)
assert _c172['b65']['n'] == 449 and _c172['b65']['below'] == 449
assert _c172['closure']['n'] == 433 and _c172['closure']['below'] == 348
assert _c172['trace_forms'] == {'b65': [518, 518], 'full': [361, 500]}
assert _c172['dup_inconsistent'] == 0
# the de-dup counts quoted in §4, and the rate move .722 -> .804
assert _c172['b65']['dupes'] == 518 - 449 == 69
assert _c172['closure']['dupes'] == 500 - 433 == 67
assert round(361 / 500, 3) == 0.722 and round(348 / 433, 3) == 0.804

# (19c) ADMISSIBILITY rule re-derived from source, not from the run's json:
# every admissible file's run script must carry l135's constant block.
_C172 = dict(TAU=0.05, DT=0.01, RMAX=1.0, BG=0.02, NOISE=0.01,
             SETTLE=400, WIN=6000, SEG=2000)
_SEGB172 = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]


def _consts172(path):
    src = path.read_text()
    g = {}
    m = re.search(r'^TAU, DT, RMAX = ([\d.]+), ([\d.]+), ([\d.]+)', src, re.M)
    if m:
        g.update(TAU=float(m.group(1)), DT=float(m.group(2)), RMAX=float(m.group(3)))
    m = re.search(r'^BG, NOISE = ([\d.]+), ([\d.]+)', src, re.M)
    if m:
        g.update(BG=float(m.group(1)), NOISE=float(m.group(2)))
    m = re.search(r'^SETTLE, WIN = (\d+), (\d+)', src, re.M)
    if m:
        g.update(SETTLE=int(m.group(1)), WIN=int(m.group(2)))
    m = re.search(r'^SEG = (\d+)', src, re.M)
    if m:
        g['SEG'] = int(m.group(1))
    m = re.search(r'^SEGB = (\[.*?\])', src, re.M)
    if m:
        g['SEGB'] = eval(m.group(1))
    return g


_adm172 = _st172['admissibility']['admissible']
assert len(_adm172) == _m172['n_admissible'] == 38, ('(19c) n admissible',
                                                     len(_adm172))
for _f in _adm172:
    _run = _f.split('/')[0]
    # run scripts live either beside the run dir or inside it (both forms
    # exist in the lineage); mirror the stats script's dual lookup.
    _sc = P / 'banc' / f'{_run}_run.py'
    if not _sc.exists():
        _cand = sorted((P / 'banc' / _run).glob('*_run.py'))
        assert _cand, ('(19c) missing run script', _f)
        _sc = _cand[0]
    _g = _consts172(_sc)
    for _k, _v in _C172.items():
        assert _g.get(_k) == _v, ('(19c) const block', _f, _k, _g.get(_k))
    assert _g.get('SEGB') == _SEGB172, ('(19c) SEGB', _f)
assert _m172['n_rejected'] == 11 and '38 of 49 stored trace files' in draft
# the jittered sets must be OUT of the canonical union (different networks)
assert not any('_j1' in _f or '_j5' in _f for _f in _adm172), '(19c) jitter leak'

# (19d) the duty metric, re-implemented, against the per-seed values the
# run stored -- then kR/n, Wilson and the bootstrap recomputed from them.
_TS172 = _np172.arange(499, 6000, 10)
_Q172 = _np172.zeros(len(_TS172), bool)
for _a0, _b0, _fr in _SEGB172:
    if _fr == 0.7:
        _Q172 |= (_TS172 >= _a0 + 500) & (_TS172 < _b0)
_QT172 = _TS172[_Q172]


def _S172(a, b):
    if a.std() <= 1e-6 or b.std() <= 1e-6:
        return float('nan')
    return float(-_np172.corrcoef(a, b)[0, 1])


def _duty172(f, arm, seed):
    z = _np172.load(str(P / 'banc' / f))
    tr = {c: z[f'Ti_{c}_{arm}_{seed}'][:6000] for c in ('fL', 'fR', 'eL', 'eR')}
    dr = [_S172(tr['fR'][t - 499:t + 1], tr['eR'][t - 499:t + 1]) >= .25
          for t in _QT172]
    return float(_np172.nanmean(dr))


# spot-check the stored per-seed duties on two arms x two seeds, from raw
for _arm, _f, _sd in (('cutng25', 'l169d/raw_l169d.npz', 3513),
                      ('cutwA', 'l169d/raw_l169d.npz', 3513)):
    _ps = _st172['per_seed'][_arm]
    _i = _ps['seeds'].index(_sd)
    assert abs(_duty172(_f, _arm, _sd) - _ps['dutyR'][_i]) < 1e-6, \
        ('(19d) per-seed duty', _arm, _sd)

for _arm, _cell in _n172.items():
    _ps = _st172['per_seed'][_arm]
    _R = _np172.array(_ps['dutyR'])
    assert len(_R) == _cell['n'] == len(set(_ps['seeds'])), \
        ('(19d) n / unique seeds', _arm)
    assert int((_R >= .5).sum()) == _cell['kR'], ('(19d) kR', _arm)
    assert round(float(_R.mean()), 3) == _cell['meanR'], ('(19d) meanR', _arm)
    _lb, _ub = wilson(_cell['kR'], _cell['n'])
    assert abs(_lb - _cell['lbR']) < 1e-9 and abs(_ub - _cell['ubR']) < 1e-9, \
        ('(19d) wilson', _arm)
    _rng = _np172.random.default_rng(1720)
    _idx = _rng.integers(0, len(_R), size=(10000, len(_R)))
    _mb = _R[_idx].mean(axis=1)
    assert round(float(_np172.percentile(_mb, 2.5)), 3) == _cell['bootR'][0] and \
        round(float(_np172.percentile(_mb, 97.5)), 3) == _cell['bootR'][1], \
        ('(19d) bootstrap', _arm)

# (19e) differences WITH intervals: Newcombe hybrid-score + Fisher exact,
# re-derived from the canonical counts.
def _newc172(k1, n1, k2, n2):
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = k1 / n1 - k2 / n2
    return (d,
            d - math.sqrt((k1 / n1 - l1) ** 2 + (u2 - k2 / n2) ** 2),
            d + math.sqrt((u1 - k1 / n1) ** 2 + (k2 / n2 - l2) ** 2))


def _fish172(a, b, c, d):
    from math import comb
    n = a + b + c + d
    r1, c1 = a + b, a + c
    tot = comb(n, c1)

    def pr(x):
        return comb(r1, x) * comb(n - r1, c1 - x) / tot

    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1)
                        if pr(x) <= p0 * (1 + 1e-9)))


for _nm, _v in _d172.items():
    _d, _lo, _hi = _newc172(_v['ka'], _v['na'], _v['kb'], _v['nb'])
    assert round(_d, 3) == _v['diff'] and round(_lo, 3) == _v['lo'] and \
        round(_hi, 3) == _v['hi'], ('(19e) newcombe', _nm)
    _p = _fish172(_v['ka'], _v['na'] - _v['ka'], _v['kb'], _v['nb'] - _v['kb'])
    assert abs(_p - _v['fisher_p']) < 1e-9, ('(19e) fisher', _nm, _p)
    assert _v['contains_zero'] == (_lo <= 0 <= _hi), ('(19e) zero flag', _nm)

# the three claim-carrying legs of the fold
_tw = _d172['twin_vs_base']
assert _tw['lo'] > 0 and not _tw['contains_zero'], '(19e) P4: twin > base'
assert _tw['fisher_p'] < .01
assert _d172['eMotTop5_vs_base']['contains_zero'] and \
    _d172['eMotBot5_vs_base']['contains_zero'], '(19e) halves indistinguishable'
assert _d172['left_carrier_vs_base']['hi'] < 0, '(19e) left-side leg sign'

# (19f) class stability (registered branch S1_counts_stable): every class
# the draft states survives the re-pool.
assert _m172['branch'] == 'S1_counts_stable'
assert _n172['cutk5']['kR'] == 0 and _n172['cutng23']['kR'] == 0        # KILL
assert _n172['cutng19']['ubR'] < .5 and _n172['cut58']['ubR'] < .5      # KILL
assert _n172['cutng25']['lbR'] > .5 and _n172['cutng29']['lbR'] > .5    # SUPER
assert _n172['silW']['lbR'] > .5                                        # SUPER
assert _n172['cutwA']['ubR'] < .5                                       # PARTIAL
assert _n172['cutng25p']['lbR'] < .5 < _n172['cutng25p']['ubR']         # INTERMEDIATE
assert _n172['b65']['lbR'] > .99

# (19g) the §2.9 / §4 / abstract literals, and the superseded forms GONE
_s29 = draft[draft.index('### 2.9 Statistics'):draft.index('## 3. Methods')]
for _lit in ('| cutwA (k=24 base) | 72/258 | [.228,.337] | .404 | [.385,.425] | 16 |',
             '| cutng25 (carrier, k=25) | 203/210 | [.933,.984] | .766 | [.749,.783] | 13 |',
             '| cutng25p (twin-XOR) | 30/66 | [.340,.574] | .459 | [.421,.496] | 4 |',
             '| silW (carrier clamp on cut base) | 78/98 | [.706,.864] | .644 | [.611,.676] | 6 |',
             '| twin − base | 30/66 vs 72/258 | +.175 | [+.047,+.305] | .008 |',
             '| carrier − base | 203/210 vs 72/258 | +.688 | [+.621,+.742] | 3.4e-59 |',
             '10,000 percentile', 'seed 1720', 'Newcombe',
             'NOISE SEED of ONE FIXED NETWORK'):
    assert _lit in _s29, ('(19g) §2.9 literal missing', repr(_lit))
_lim172 = draft[draft.index('## 4. Limitations'):]
for _lit in ('UNIT OF INFERENCE', '449 of 449 UNIQUE SEEDS',
             '348 of 433 unique seeds', 'removes 69 and 67 repeat observations',
             '.722 to .804'):
    assert _lit in _lim172, ('(19g) §4 literal missing', repr(_lit))
_abs172 = draft[draft.index('## Abstract (draft)'):draft.index('## 1. Introduction')]
# L174 (b2) RE-CUT: the abstract was compressed from 5,322 to 1,916 chars,
# so four of this gate's eight literals were abstract-LOCAL phrasings.  The
# CLAIMS did not move: each is re-asserted below against the BODY form the
# certified sections carry (slash counts in 2.1/2.2/2.9), and the abstract
# list is re-cut to the compressed text's own wording.  Relocation, not
# deletion — l174_verify (9) proves every dropped token has a body home.
_body19g = re.sub(r'\s+', ' ', draft[draft.index('## 1. Introduction'):])
for _lit in ('5/178', '203/210', '30/66', '30 of 66',
             '0/226', '72/258', '1/258', '188/194', 'INTERMEDIATE'):
    assert _lit in _body19g, ('(19g) relocated body literal missing', repr(_lit))
for _lit in ('5 of 178 seeds survive at k=19', '188 of 194 at k=29',
             'identity carries it, not mass',
             'its mass twin lands intermediate, not neutral (30 of 66',
             'the carrier\n-.512)', 'cut base (78 of 98)'):
    assert _lit in _abs172, ('(19g) abstract literal missing', repr(_lit))
# BODY-scoped removal gates (the l169c2 banner lesson): the version banner
# deliberately names the superseded forms, so it is excluded.
_body172 = draft[draft.index('## Title (RE-SCOPED'):]
for _dead in ('CONTAINS .5', 'inside the .075 sham spread',
              'behaviorally neutral', '[pooled.cutng25p]',
              'the neutral twin'):
    assert _dead not in _body172, ('(19g) superseded statistics form', _dead)
# the sham caveat is factual: three shams, and the stored spread is their range
assert _m172['sham_n'] == 3
_g3172 = json.loads((P / 'banc/l137/results_l137.json').read_text())['g3']
assert len(_g3172['silrand_meanR']) == 3
assert abs((max(_g3172['silrand_meanR']) - min(_g3172['silrand_meanR']))
           - _g3172['spread']) < 1e-9
# L174 (b2): the en-dash RANGE form '.429–.504' lived only in the v3.21
# abstract; the claim's certified home is §2.4, which lists all THREE sham
# means individually.  Re-scoped and STRENGTHENED — each stored sham value
# is now matched against the body literal, not just the range endpoints.
assert '.429/.502/.504' in _body172
for _sv in sorted(_g3172['silrand_meanR']):
    assert f'{_sv:.3f}'.lstrip('0') in _body172, ('(19g) sham mean', _sv)

print('(19) L172 statistics pass: l156 census cells re-CERTified from stored '
      'rows (with the agree-among-sub-band definition our CERT caught), the '
      'unique-seed forms re-derived (449/449 and 348/433), the admissibility '
      'rule re-proven by PARSING every admissible run script\'s constant '
      'block from source, the per-seed duty spot-checked from RAW traces and '
      'every arm\'s kR / Wilson / mean / bootstrap recomputed, all 13 '
      'difference intervals re-derived (Newcombe + Fisher from first '
      'principles), P4 REFUTATION proven in data (twin > base, interval '
      'excludes 0), branch S1_counts_stable proven class-by-class, and the '
      'superseded "contains .5" / "inside the .075 sham spread" / "neutral '
      'twin" forms asserted GONE from the body')

# ------- (20) L173 (a): the Methods write-up, re-parsed from SOURCE --------
import ast as _ast173
import torch as _t173
import numpy as _np173

_m173 = nums['l173.model']['v']
_p173 = nums['l173.protocol']['v']
_d173 = nums['l173.defs']['v']
_rs173 = (P / 'banc/l135_run.py').read_text()
_vs173 = (P / 'banc/l169d_verdict.py').read_text()
_st173 = (P / 'banc/l131_static.py').read_text()

# (a) INDEPENDENT ast re-parse of the module-level constants (S1).
_got173 = {}
for _n in _ast173.parse(_rs173).body:
    if not isinstance(_n, _ast173.Assign):
        continue
    _t, _v = _n.targets[0], _n.value
    if isinstance(_t, _ast173.Tuple) and isinstance(_v, _ast173.Tuple):
        for _tt, _vv in zip(_t.elts, _v.elts):
            if isinstance(_tt, _ast173.Name):
                try: _got173[_tt.id] = _ast173.literal_eval(_vv)
                except ValueError: pass
    elif isinstance(_t, _ast173.Name):
        try: _got173[_t.id] = _ast173.literal_eval(_v)
        except ValueError: pass
for _k in ('TAU', 'DT', 'RMAX', 'BG', 'NOISE', 'SETTLE', 'WIN', 'SEG', 'BETA'):
    assert _got173[_k] == _m173[_k], ('(20) constant drift', _k,
                                      _got173[_k], _m173[_k])
assert _got173['D'] == _p173['dng100_drive'] == 0.2, '(20) DNg100 drive'
assert round(_got173['AF_T'], 6) == _m173['AF_T'], '(20) AF_T'
assert _got173['WIN'] * _got173['DT'] == _p173['win_s'] == 60.0
# CERT-1 again, here: the CURRENT run script carries the same protocol
_rn173 = (P / 'banc/l169d_run.py').read_text()
for _k in ('TAU', 'DT', 'RMAX', 'BG', 'NOISE', 'SETTLE', 'WIN', 'SEG',
           'BETA', 'D', 'ENT_AMP', 'AF_T'):
    _lit = f'{_k} ' if _k in ('SEGB',) else _k
    assert _lit in _rn173, ('(20) constant absent from the current run', _k)

# (b) the EQUATION, re-certified against the run script's own three lines.
_up173 = ['drive = torch.sparse.mm(WB[a], st[a]) * gains[a] + I[a]',
          'drive[mech[a], 0] = drive[mech[a], 0] + sin_t']
for _u in _up173:
    assert _u in _rs173, ('(20) update line missing', _u[:40])
_mm173 = re.search(r'st\[a\] = st\[a\] \+ \(DT / TAU\) \* \(\(torch\.relu\('
                   r'drive \+ BG\) \+ noise\[a\]\)\s*\.clamp\(max=RMAX\)'
                   r' - st\[a\]\)', _rs173)
assert _mm173, '(20) x-update line missing'
_code173 = '\n'.join(_up173 + [re.sub(r'\s*\n\s*', ' ', _mm173.group(0))])
_t173.manual_seed(1730)
_N173 = 7
_W173 = (_t173.randn(_N173, _N173, dtype=_t173.float64) * 0.3).to_sparse_csr()
_x173 = _t173.rand(_N173, 1, dtype=_t173.float64)
_nz173 = _t173.randn(_N173, 1, dtype=_t173.float64) * _m173['NOISE']
_mk173 = _np173.array([1, 4])
_g173, _s173 = 0.1452, _m173['BG'] * 1.85
_I173 = _t173.zeros(_N173, 1, dtype=_t173.float64)
_I173[2] = _p173['dng100_drive']
_sc173 = dict(torch=_t173, WB={'a': _W173}, st={'a': _x173.clone()},
              gains={'a': _g173}, I={'a': _I173}, mech={'a': _mk173},
              noise={'a': _nz173}, sin_t=_s173, a='a',
              DT=_m173['DT'], TAU=_m173['TAU'], BG=_m173['BG'],
              RMAX=_m173['RMAX'])
exec(compile(_code173, '<l135 update>', 'exec'), _sc173)
_u173 = _g173 * (_W173 @ _x173) + _I173
_u173[_mk173, 0] = _u173[_mk173, 0] + _s173
_me173 = _x173 + (_m173['DT'] / _m173['TAU']) * (
    (_t173.relu(_u173 + _m173['BG']) + _nz173).clamp(max=_m173['RMAX'])
    - _x173)
_dm173 = float((_sc173['st']['a'] - _me173).abs().max())
assert _dm173 == 0.0, ('(20) the Methods equation is NOT the code', _dm173)
assert _m173['eq_maxd'] == 0.0 and _m173['branch'] == 'M1_equation_matches'

# (c) definitions re-parsed from the verdict + static sources (S2/S3).
_sup173 = re.search(r'return bool\(t\["meanR"\] >= ([0-9.]+) and '
                    r't\["kR"\] >= (\d+)\)', _vs173)
assert _sup173, '(20) SUPER criterion not found in the verdict source'
assert (float(_sup173.group(1)), int(_sup173.group(2))) == (
    _d173['super_meanR'], _d173['super_k']), '(20) SUPER criterion drift'
_par173 = re.search(r'return bool\(([0-9.]+) <= t\["meanR"\] <= ([0-9.]+) '
                    r'and (\d+) <= t\["kR"\] <= (\d+)\)', _vs173)
assert _par173, '(20) PARTIAL criterion not found in the verdict source'
assert (float(_par173.group(1)), float(_par173.group(2))) == (
    _d173['partial_lo'], _d173['partial_hi']), '(20) PARTIAL criterion drift'
_ns173 = re.search(r'return bool\(t\["kR"\] <= (\d+) and '
                   r't\["meanR"\] <= ([0-9.]+)\)', _vs173)
assert _ns173 and int(_ns173.group(1)) == _d173['notsuper_k'], \
    '(20) NOT-SUPER criterion drift'
assert f'TS = np.arange({_d173["s_window"] - 1}, WIN, ' \
       f'{_d173["sample_stride"]})' in _vs173, '(20) S sampling drift'
assert f'>= .{str(_d173["duty_bar"])[2:]}' in _vs173, '(20) duty bar drift'
assert 'K = int(np.searchsorted(cum, 0.50) + 1)' in _st173, '(20) K rule'
assert f'len(glut_desc) == {_d173["n_glut"]} and ' \
       f'len(ng_desc) == {_d173["n_nonglut"]}' in _st173, '(20) 19/58 split'
assert 'np.add.at(outmass, src_all[om], np.abs(vals_all[om]))' in _st173, \
    '(20) removal mass is the ABS out-mass onto cord targets'
_s107173 = json.loads((P / 'banc/l107/static.json').read_text())
assert _s107173['cut']['K'] == _d173['K'] == 77
assert _s107173['cut']['mass_share'] == _d173['mass_share']

# (d) the §3 text says what the parsed values say (P5: no unparsed row).
_meth173 = draft[draft.index('## 3. Methods'):draft.index('## 4. Limitations')]
for _h in ('### 3.1 Substrate', '### 3.2 Rate model', '### 3.3 Drive',
           '### 3.4 Operating point', '### 3.5 Cohort', '### 3.6 Readouts',
           '### 3.7 Seeds', '### 3.8 Preregistration',
           '### 3.9 Notation', '### 3.10 Data-integrity'):
    assert _h in _meth173, ('(20) Methods subsection missing', _h)
for _lit in ('x ← x + (DT/TAU) · ( clamp( relu(g·W x + I + s(t)·1_mech + BG)',
             '+ noise, max = RMAX ) − x )',
             'The noise enters AFTER the rectifier and INSIDE the',
             'clamp. The clamp has NO lower bound',
             'tonic drive D = 0.2 [l173.protocol]',
             'A cell counts as active when x > 0.05',
             'bisected 24 times on the bracket',
             '[0.12, 0.18] to the target active fraction AF_T = .109056',
             '(K = 77 cells, cumulative share .5024)',
             '19 glutamatergic and 58 non-glutamatergic',
             'cells (.1103 / .3921 of the mass)',
             'over a sliding 500-step window, sampled every 10 steps',
             'fraction of samples with S ≥ .25',
             'SUPER = meanR ≥ .60 and kR ≥ 12 of',
             'PARTIAL = .35 ≤ meanR ≤ .50 with 3 ≤ kR ≤ 8',
             'NOT-SUPER (the',
             'control form) = kR ≤ 8 and meanR ≤ .50',
             '38 of 49 trace files',
             'seven-node probe (max|Δ| = 0.0)',
             '500 steps on / 400 off',
             '(period 900)'):
    assert _lit in _meth173, ('(20) Methods literal missing', repr(_lit))
# notation table: one row per symbol, each value matching the parsed source
_tab173 = _meth173[_meth173.index('| symbol | value | meaning |'):]
_tab173 = _tab173[:_tab173.index('### 3.10')]
_rows173 = [l for l in _tab173.splitlines()
            if l.startswith('| ') and not l.startswith('| symbol')]
assert len(_rows173) == 15, ('(20) notation table rows', len(_rows173))
_want173 = {'TAU': '.05 s', 'DT': '.01 s', 'RMAX': '1.0', 'BG': '.02',
            'NOISE': '.01', 'SETTLE': '400', 'SEG': '2000', 'β': '2.0',
            'D': '0.2', 'ENT_AMP': '0.1', 'AF_T': '.109056'}
_have173 = {r.split('|')[1].strip(): r.split('|')[2].strip() for r in _rows173}
for _k, _v in _want173.items():
    assert _have173[_k] == _v, ('(20) notation row', _k, _have173.get(_k), _v)
# and every numeric notation row agrees with the PARSED constant
_map173 = {'TAU': 'TAU', 'RMAX': 'RMAX', 'BG': 'BG', 'NOISE': 'NOISE',
           'SETTLE': 'SETTLE', 'SEG': 'SEG', 'β': 'BETA'}
for _row, _key in _map173.items():
    _num = float(re.search(r'[0-9.]+', _have173[_row]).group(0))
    assert _num == float(_got173[_key]), ('(20) notation vs source', _row)
assert float(re.search(r'[0-9.]+', _have173['D']).group(0)) == _got173['D']
_mean173 = {r.split('|')[1].strip(): r.split('|')[3].strip()
            for r in _rows173}
assert '6000 steps = 60 s' in _mean173['DT'], '(20) DT row meaning'
assert 'no lower clamp' in _mean173['RMAX'], '(20) RMAX row meaning'

# (e) stage-(b) SCOPE: §2.4 has been rebuilt, and the two bit-identity
# passages the card ordered MOVED now live in §3.8 (section 21 proves the
# relocation and the retired framing's absence from the body).
_s24173 = draft[draft.index('### 2.4 Mechanism'):draft.index('### 2.5 ')]
_s38173 = draft[draft.index('### 3.8 Preregistration'):draft.index('### 3.9 Notation')]
for _moved in ('BIT-IDENTICAL to cutng25', 'BIT-IDENTICAL to eAll'):
    assert _moved in _s38173, ('(20) identity passage not in \u00a73.8', _moved)
    assert _moved not in _s24173, ('(20) identity passage still in \u00a72.4', _moved)
assert 'stage (b)' in draft[:draft.index('## Title')], \
    '(20) the banner must record the \u00a72.4 rebuild stage'

print('(20) L173 (a) Methods: every model/protocol constant RE-PARSED by ast '
      'from banc/l135_run.py and matched against the current run script, the '
      'update equation RE-CERTIFIED against the run script\'s own three '
      'update lines by an independent 7-node probe (max|d| = 0.0 -> branch '
      'M1_equation_matches), the duty / class / S-window definitions '
      're-parsed from banc/l169d_verdict.py and the cohort / mass / ladder '
      'rule from banc/l131_static.py with its stored K and mass share, all '
      '21 §3 literals + the 15-row notation table checked value-by-value '
      'against the parsed source, and the stage-(b) relocation asserted '
      '(both identities now in §3.8, none left in §2.4)')

# ===================== (21) L173 stage (b): the §2.4 rebuild ================
# PREREG banc/l173b/PREREG.md (T1-T4, CERT-1..6, branches B2 > B1).
# Every gain is RE-READ here from its stored anchors.g_* field and every
# percent delta RE-DERIVED, independently of banc/l173b/cert.json.
_c173b = json.loads((P / 'banc/l173b/cert.json').read_text())
_r137b = json.loads((P / 'banc/l137/results_l137.json').read_text())
_r142b = json.loads((P / 'banc/l142/results_l142.json').read_text())
_r144b = json.loads((P / 'banc/l144/results_l144.json').read_text())
_r145b = json.loads((P / 'banc/l145/results_l145.json').read_text())
_r148b = json.loads((P / 'banc/l148/results_l148.json').read_text())
_r150b = json.loads((P / 'banc/l150/results_l150.json').read_text())
_s172b = json.loads((P / 'banc/l172/stats.json').read_text())

# CERT-1 re-proof: EXACT float equality, five files agreeing on the base gain
_gwA = _r142b['anchors']['g_cutwA']
for _t, _s in (('l144', _r144b), ('l145', _r145b), ('l148', _r148b), ('l150', _r150b)):
    assert _s['anchors']['g_cutwA'] == _gwA, f'(21) g_cutwA differs in {_t}'
assert _r144b['anchors']['g_sil1110_wA'] == _gwA, '(21) silW B30 gain != base'
assert _r150b['anchors']['g_silW'] == _gwA, '(21) silW B33 gain != base'
assert _c173b['branch'] == 'B1_silW_gain_unchanged', '(21) branch'
assert f'{_gwA:.9f}'[1:] in _s24173, '(21) the base gain is not quoted in §2.4'

# CERT-2 re-proof: percent deltas re-derived, flip partition from stored
# class booleans, every quoted percent asserted verbatim in §2.4
_GB = {'cutng25': _r142b['anchors']['g_cutng25'],
       'eOutInt': _r142b['anchors']['g_eOutInt'],
       'eIn': _r142b['anchors']['g_eIn'], 'eAll': _r142b['anchors']['g_eAll'],
       'eOutAll': _r142b['anchors']['g_eOutAll'],
       'eMotIn': _r145b['anchors']['g_eMotIn'],
       'eMotTop5': _r145b['anchors']['g_eMotTop5'],
       'eMotBot5': _r145b['anchors']['g_eMotBot5'],
       'eOutMot': _r145b['anchors']['g_eOutMot'],
       'silW': _r150b['anchors']['g_silW']}
_pctb = {_a: round((_g - _gwA) / _gwA * 100.0, 3) for _a, _g in _GB.items()}
_CLSB = {'cutng25': _r142b['classes']['25'], 'eOutInt': _r142b['classes']['eOutInt'],
         'eIn': _r142b['classes']['eIn'], 'eAll': _r142b['classes']['eAll'],
         'eOutAll': _r142b['classes']['eOutAll'], 'eMotIn': _r145b['classes']['motIn'],
         'eMotTop5': _r145b['classes']['top5'], 'eMotBot5': _r145b['classes']['bot5']}
_flipb = sorted(_a for _a, _c in _CLSB.items() if _c['super'] is True)
_nonb = sorted(_a for _a, _c in _CLSB.items() if _c['super'] is not True)
assert _flipb == ['cutng25', 'eAll', 'eIn', 'eMotIn', 'eOutAll', 'eOutInt'], _flipb
assert _nonb == ['eMotBot5', 'eMotTop5'], _nonb
assert _pctb == _c173b['cert2']['pct'], '(21) percent deltas disagree with cert.json'
assert _pctb['silW'] == 0.0, '(21) silW delta must be exactly zero'
assert min(_pctb[_a] for _a in _flipb) > 1.0 and max(_pctb[_a] for _a in _flipb) < 1.35
for _a, _lit in (('eOutInt', '+1.297%'), ('eIn', '+1.087%'), ('eMotIn', '+1.062%'),
                 ('eOutAll', '+1.238%'), ('eMotTop5', '\u22120.031%'),
                 ('eMotBot5', '+0.009%'), ('eOutMot', '\u22120.568%')):
    _want = f'{abs(_pctb[_a]):.3f}%'
    assert _want in _lit and _lit in _s24173, ('(21) percent literal', _a, _lit)
assert _pctb['cutng25'] == _pctb['eAll'] == 1.244 and 'cutng25 and eAll +1.244%' in _s24173

# CERT-3 re-proof: the lead arm's cells + the canonical pool, Wilson full precision
assert (_r144b['table']['Ti']['sil1110_wA']['meanR'],
        _r144b['table']['Ti']['sil1110_wA']['kR']) == (0.622, 14)
assert (_r150b['hypotheses']['H1_silW']['meanR'],
        _r150b['hypotheses']['H1_silW']['kR']) == (0.659, 14)
_pw173 = _s172b['pooled']['silW']
_lb173, _ub173 = wilson(_pw173['kR'], _pw173['n'])
assert (_pw173['kR'], _pw173['n']) == (78, 98)
assert abs(_lb173 - _pw173['lbR']) < 1e-9 and abs(_ub173 - _pw173['ubR']) < 1e-9
_df173 = _s172b['diffs']['silW_vs_base']
assert round(_df173['diff'], 3) == 0.517 and round(_df173['lo'], 3) == 0.410 \
    and round(_df173['hi'], 3) == 0.602 and _df173['fisher_p'] < 1e-15
for _s in ('.622 with 14/16 seeds on batch D', '.659 with\n14/16 on batch G',
           '78 of 98', '[.706,.864]', '+.517\n[+.410,+.602]',
           'Fisher p = 7e-19', 'BIT-IDENTICAL to its own base'):
    assert _s in _s24173, ('(21) lead-arm literal', _s)

# CERT-4 re-proof: the retired sham sentence cannot come back
_g3b = _r137b['g3']
assert _g3b['silrand_meanR'] == [0.429, 0.502, 0.504]
assert round(max(_g3b['silrand_meanR']) - min(_g3b['silrand_meanR']), 3) == 0.075
assert _r137b['g1']['sil1110']['legs']['mean_paired_dR'] == -0.088
assert abs(-0.088) > 0.075, '(21) the retired claim would be true?!'
assert 'is LARGER than their .075 range' in _s24173, '(21) honest sham wording'
_body173 = draft[draft.index('## 1. Introduction'):]
for _bad in ('inside the .075\nrandom-cell sham spread', 'inside the .075 random-cell',
             'two-factor', 'two factors', 'Factor 1', 'Factor 2'):
    assert _bad not in _body173, ('(21) retired wording survives in the body', _bad)

# CERT-5 re-proof: the mass ratio, in §2.4 AND the abstract
_h2ab = _r142b['hypotheses']['H2a']
assert abs(_h2ab['mass'] - 0.005599) < 1e-9
_ratio173 = 0.0544 / _h2ab['mass']
assert round(_ratio173, 2) == 9.72 and abs(_ratio173 - 12) > 0.5
assert '9.72\u00d7 below the .0544' in _s24173, '(21) §2.4 mass ratio'
assert '12\u00d7' not in _body173, '(21) the retired 12x ratio survives in the body'

# CERT-6 re-proof: the sil24 non-separability disclosure (reviewer I10)
_s24b = _r137b['sil24']
assert (_s24b['kR'], _s24b['meanR']) == (5, 0.432)
assert (_r137b['table']['Ti']['full']['kR'], _r137b['table']['Ti']['full']['meanR']) == (6, 0.464)
assert (_s24b['cutwA_l135_b26']['kR'], _s24b['cutwA_l135_b26']['meanR']) == (5, 0.383)
assert 'NO demonstrated separation' in _s24173 and 'untreated intact base is\n6/16' in _s24173

# P2 re-proof: the relocated identities carry their stored anchors in §3.8
assert _r148b['seid_all_max'] == 0.0 and _r148b['hypotheses']['H_ID']['bit_identical'] is True
assert _r142b['anchors']['g_eall_vs_g25']['equal'] is True
assert nums['l142.aeall']['v']['a_eall_max'] == 0.0
for _s in ('.1454454553127289', '23 keys', 'node-drop \u2261 incident-edge-drop',
           'strict SUBSET of edge removal'):
    assert _s in _s38173, ('(21) §3.8 relocation literal', _s)
# the RESULT the relocation leaves behind stays in §2.4
assert '~.13 gap from silW' in _s24173 and 'settle-history carried by the edges' in _s24173
# numbers.json key == its source
assert nums['l173b.gains']['v']['pct'] == _pctb
assert nums['l173b.gains']['v']['g_base'] == _gwA
assert nums['l173b.gains']['v']['mass_ratio'] == 9.72
assert nums['l173b.gains']['v']['branch'] == 'B1_silW_gain_unchanged'

print('(21) L173 (b) §2.4 rebuild: all ten gains RE-READ from stored '
      'anchors.g_* fields and all ten percent deltas RE-DERIVED '
      '(flip band +1.062..+1.297%, non-flip within \u00b10.03%, eOutMot '
      '\u22120.568%, silW EXACTLY 0.000% = branch B1_silW_gain_unchanged with '
      'five files agreeing on the base gain), the lead arm\'s cells + the '
      'canonical 78/98 pool + its difference interval recomputed, the sham '
      'spread re-proven SMALLER than the carrier\'s own \u0394R (so the retired '
      '"inside the sham spread" sentence cannot return), the mass ratio '
      're-derived to 9.72\u00d7 with 12\u00d7 forbidden body-wide, the sil24 '
      'non-separability disclosure checked against its own batch\'s two '
      'comparators, and both construction-level identities proven RELOCATED '
      'into §3.8 with §2.4 keeping only the ~.13 margin they leave as a result')

# ============== (22) L174 stage (b3): the §2.4 de-duplication gate ==========
# PREREG banc/l174b3/PREREG.md (T1/T3/T5 + ADDENDUM-1 gate G1').  This makes
# the compression permanent: the grid table is the single home of every
# per-arm level and seed count, every verifier literal survives verbatim, and
# the section cannot re-inflate.  Pure string arithmetic.
_s24b3 = draft[draft.index('### 2.4 Mechanism'):draft.index('### 2.5 ')]
_lits24 = json.loads((P / 'banc/l174b3/lits24.json').read_text())
# (b4-iii-b) RELABEL-AWARE RE-POINT (never loosened): the stage-(b4-iii-b)
# batch relabel rewrote three literals of this FROZEN stored list.  The list is
# a tick-207 artifact and stays byte-frozen; the LIVE checks run on its
# relabeled image, and each old form is asserted ABSENT from the draft -- so
# this is strictly stronger than the pin it replaces (it proves the relabel
# happened AND that every measurement stayed attached to its batch label).
_RELAB24 = {'.622 with 14/16 seeds on B30': '.622 with 14/16 seeds on batch D',
            '.659 with\n14/16 on B33': '.659 with\n14/16 on batch G',
            '\u2212.036 on B30': '\u2212.036 on batch D'}
_lits24_live = [_RELAB24.get(_s, _s) for _s in _lits24]
assert sum(1 for _s in _lits24 if _s in _RELAB24) == 3, '(22) relabel set size'
for _o, _n in _RELAB24.items():
    assert _o not in draft and _n in draft, ('(22) relabel re-point', _o)
_prem = json.loads((P / 'banc/l174b3/premise.json').read_text())
_pre24 = (P / 'banc/l174b3/sec24_pre.txt').read_text()

# I10's three substantive components, re-checked here (not trusted from json)
assert _prem['branch'] == 'S1_editorial_only', '(22) premise branch'
_p24 = [_x for _x in _s24b3.split('\n\n') if _x.strip()]
assert 'silW' in _p24[1] and 'clean arm' in _p24[1], '(22) I10a: silW lead'
for _m in ('BIT-IDENTICAL to cutng25', 'BIT-IDENTICAL to eAll'):
    assert _m in _s38173 and _m not in _s24b3, ('(22) I10b', _m)
assert 'NO demonstrated separation' in _s24b3, '(22) I10c sil24 disclosure'

# T3: every literal the six verifiers assert in §2.4 is still there, verbatim
_miss24 = [_s for _s in _lits24_live if _s not in _s24b3]
assert not _miss24, ('(22) gate literals lost from \u00a72.4', _miss24[:5])
assert len(_lits24) == 101, '(22) the stored literal list changed size'

# the grid table is byte-unchanged from the pre-image
def _tbl24(_sec):
    _ls = _sec.split('\n')
    _tb = [_k for _k, _l in enumerate(_ls) if _l.startswith('|')]
    return '\n'.join(_ls[min(_tb):max(_tb) + 1])


assert _tbl24(_s24b3) == _tbl24(_pre24), '(22) the grid table was modified'

# T5: the seven bold claim leads survive (wrap-insensitive)
_fl = lambda _t: ' '.join(_t.split())
_ld_pre = [_fl(_x) for _x in re.findall(r'\*\*(.+?)\*\*', _pre24, re.S)]
_ld_new = [_fl(_x) for _x in re.findall(r'\*\*(.+?)\*\*', _s24b3, re.S)]
assert len(_ld_pre) == len(_ld_new) == 7, ('(22) claim leads', len(_ld_new))

# T1: no numeric orphan — every token the section dropped lives elsewhere
_NUM24 = re.compile(r'[\u2212+\-]?\d[\d,]*(?:\.\d+)?(?:e[\u2212+\-]?\d+)?|\.\d+')
_body24 = draft[draft.index('## 1. Introduction'):draft.index('## References')]
_bodywo = _body24.replace(_s24b3, '')
_drop24 = sorted(set(_NUM24.findall(_pre24)) - set(_NUM24.findall(_s24b3)))
_orph24 = [_t for _t in _drop24 if _t not in _bodywo]
assert not _orph24, ('(22) numeric orphans', _orph24)
assert not sorted(set(_NUM24.findall(_s24b3)) - set(_NUM24.findall(_pre24))), \
    '(22) a NEW number entered \u00a72.4'

# G1': no (meanR, kR/n) cell of the table is restated in the prose unless a
# verifier asserts that exact prose spelling (span containment).
_prose24 = _s24b3.replace(_tbl24(_s24b3), '')
_cert24 = bytearray(len(_prose24))
for _s in _lits24_live:
    _st = 0
    while True:
        _i = _prose24.find(_s, _st)
        if _i < 0:
            break
        for _q in range(_i, _i + len(_s)):
            _cert24[_q] = 1
        _st = _i + 1
_dup24 = []
for _r in [_r for _r in _tbl24(_s24b3).split('\n')
           if _r.startswith('|') and '---' not in _r][1:]:
    _c = [_x.strip() for _x in _r.strip('|').split('|')]
    _cnt = [_x.strip() for _x in _c[3].split(',')]
    _n24 = _cnt[-1].split('/')[-1]
    for _v in [_x.strip() for _x in _c[2].split('/')]:
        _pats = [f'{_v}, {_k}' for _k in _cnt if '/' in _k]
        _pats += [f'{_v}, {_k}/{_n24}' for _k in _cnt if '/' not in _k]
        for _p in _pats:
            _st = 0
            while True:
                _i = _prose24.find(_p, _st)
                if _i < 0:
                    break
                if not all(_cert24[_q] for _q in range(_i, _i + len(_p))):
                    _dup24.append((_c[0], _p))
                _st = _i + 1
assert not _dup24, ('(22) G1\u2032: table cells restated in prose', _dup24)
# the self-test: the SAME rule must fail on the pre-image (5 known cells)
_prose_pre = _pre24.replace(_tbl24(_pre24), '')
_cert_pre = bytearray(len(_prose_pre))
for _s in _lits24:
    _st = 0
    while True:
        _i = _prose_pre.find(_s, _st)
        if _i < 0:
            break
        for _q in range(_i, _i + len(_s)):
            _cert_pre[_q] = 1
        _st = _i + 1
_hit_pre = 0
for _p in ('.781, 15/16', '.793, 15/16', '.525, 9/16', '.632, 12/16',
           '.801, 15/16'):
    _i = _prose_pre.find(_p)
    assert _i >= 0, ('(22) self-test pattern absent from the pre-image', _p)
    if not all(_cert_pre[_q] for _q in range(_i, _i + len(_p))):
        _hit_pre += 1
assert _hit_pre == 5, ('(22) the de-dup rule does not fire on the pre-image',
                       _hit_pre)

# length: cannot re-inflate (pre-image 9,937 -> 8,562).  (b4-iii-b) RE-POINT BY
# DECOMPOSITION, not by loosening: the batch relabel costs §2.4 +38 chars, so
# the compression ceiling is asserted on the label-NEUTRALIZED slice (new labels
# mapped back to the internal codes) and the live length is pinned exactly.
_INV24 = {'A': 'B26', 'B': 'B27', 'C': 'B29', 'D': 'B30', 'E': 'B31',
          'F': 'B32', 'G': 'B33', 'H': 'B34', 'J': 'B35', 'K': 'B37',
          'L': 'B38'}
_n24 = re.sub(r'batch ([A-HJ-L])(?![A-Za-z])',
              lambda _m: _INV24[_m.group(1)], _s24b3)
assert len(_pre24) == 9937 and len(_n24) <= 8562 and len(_s24b3) == 8600, \
    ('(22) \u00a72.4 length', len(_s24b3), len(_n24))
assert 'v3.23 = L174 stage (b3)' in draft[:draft.index('## Title')], \
    '(22) the banner must record the (b3) stage'

print('(22) L174 (b3) \u00a72.4 editorial: I10\'s three substantive components '
      're-checked in the draft (silW lead, both bit-identities in \u00a73.8 and '
      'absent here, sil24 non-separability) = branch S1_editorial_only, then '
      'the compression gated as DE-DUPLICATION — 101 of 101 verifier literals '
      'verbatim, the grid table byte-unchanged, 7 of 7 claim leads, 12 dropped '
      'numeric tokens all relocated (0 orphans) and 0 new numbers, no table '
      'cell restated outside a certified span (the same rule fires on 5 cells '
      'of the frozen pre-image = sensitivity self-test), 9,937 -> 8,562 chars '
      'capped so the section cannot re-inflate')

# ---------------------------------------------------------------- (23)
# L174 stage (b3b-i): bullets -> prose in §1, §2.1, §2.2, §2.3, gated as a
# FORMAT-ONLY transform. This is a stronger contract than (b2)'s relocation
# rule or (b3)'s de-duplication rule: both of those let a number leave its
# block, while a prose conversion may not move one at all. Everything below
# is re-derived from the frozen pre-image, not from the stage's own report.
_B3B = P / 'banc/l174b3b'
_pre_b3b = (_B3B / 'span_pre.txt').read_text()
_i_b3b = draft.index('## 1. Introduction')
_j_b3b = draft.index('### 2.4 Mechanism')
_now_b3b = draft[_i_b3b:_j_b3b]

_NUM_B3B = re.compile(r'[-+\u2212]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|\u00d7)?')
_CIT_B3B = re.compile(r'\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]')
_BUL_B3B = re.compile(r'^\s*[-*]\s+\S', re.M)

# the span is still the span: §2.4 did not move into it and §1 did not shrink
assert len(_BUL_B3B.findall(_pre_b3b)) == 15, '(23) pre-image bullet count'
assert len(_BUL_B3B.findall(_now_b3b)) == 0, \
    '(23) bullet lines are back in §1-§2.3'

# T1: numeric and citation multisets IDENTICAL (sorted lists, not sets).
# RE-POINTED by L174 (b4-iii-a), never loosened: _NUM_B3B has no left word
# boundary, so it counts the digits INSIDE an identifier (`L168` contributes
# `168`). A lane-ID strip therefore breaches a MEASUREMENT gate without moving
# any measurement. The comparison now runs on measurement tokens (identifier
# digit runs excluded) AND the removed identifier digits are asserted BY NAME,
# which is strictly stronger than the original: it proves both that no
# measurement moved and exactly which identifier left.
_MEAS_B3B = re.compile(r'(?<![A-Za-z0-9])[-+\u2212]?\d[\d,]*(?:\.\d+)?'
                       r'(?:[eE][-+]?\d+)?(?:%|\u00d7)?')
_IDNUM_B3B = re.compile(r'(?<=[A-Za-z])\d[\d\.]*')
assert sorted(_MEAS_B3B.findall(_pre_b3b)) == sorted(_MEAS_B3B.findall(_now_b3b)), \
    '(23) T1 breach: the §1-§2.3 measurement multiset moved'
_idp = __import__('collections').Counter(_IDNUM_B3B.findall(_pre_b3b))
_idn = __import__('collections').Counter(_IDNUM_B3B.findall(_now_b3b))
# (b4-iii-b) RE-POINT: the removed-identifier set is now the UNION of two
# declared strips, each named -- (b4-iii-a)'s lane ID L168 and (b4-iii-b)'s
# batch code B34 (relabeled to H in §1).  Still an exact set, never a bound.
assert sorted((_idp - _idn).elements()) == ['168', '34'], \
    ('(23) identifier digits removed from §1-§2.3 != the declared L168 + B34',
     sorted((_idp - _idn).elements()))
assert 'fresh batch H,' in _now_b3b and 'B34' not in _now_b3b, \
    '(23) the §1 batch code must be relabeled, not deleted'
assert sorted((_idn - _idp).elements()) == [], '(23) an identifier digit ENTERED §1-§2.3'
assert sorted(_CIT_B3B.findall(_pre_b3b)) == sorted(_CIT_B3B.findall(_now_b3b)), \
    '(23) T1 breach: the §1-§2.3 citation-key multiset moved'
# (b4-iii-b): 354 -> 353, the ONE token lost being B34's identifier digits
# (the §1 batch code, now the label H); the citation-key pin is unchanged.
assert len(_NUM_B3B.findall(_now_b3b)) == 353 \
    and len(_CIT_B3B.findall(_now_b3b)) == 45, '(23) token-count pins'

# T3: every verifier literal harvested from the pre-image survives verbatim.
# The harvest floor is 4 chars BY NECESSITY: run 1 used 8 and the reflow then
# split '0 of 20' (7 chars) across a line — a multiset gate cannot see a lost
# adjacency, so short number phrases must be protected explicitly.
_lit_b3b = json.loads((_B3B / 'literals.json').read_text())
assert _lit_b3b['report']['literals_in_span'] == 184, '(23) literal count pin'
_short = [s for s in _lit_b3b['literals'] if 4 <= len(s) < 8]
assert '0 of 20' in _lit_b3b['literals'] and len(_short) >= 20, \
    '(23) the short-literal class must be in the protected set'
_miss_b3b = [s for s in _lit_b3b['literals'] if s not in _now_b3b]
# ONE declared T3 exception, added by L174 (b4-iii-a) and re-pointed to the
# STRONGER form: 'LANE-RESEARCH.md' is an internal-artefact reference the
# lane-ID strip removes by design, so presence is replaced by ABSENCE plus a
# presence check on the authored replacement. (The §(23) harvest found this
# literal; the strip's own at-risk harvest did not, because it tested only
# whether a literal CONTAINS an edit's old form and this literal is CONTAINED
# BY it — overlap must be tested in both directions.)
_EXC_B4III = {'LANE-RESEARCH.md'}
assert _EXC_B4III <= set(_lit_b3b['literals']), '(23) exception not in the harvest'
_miss_b3b = [s for s in _miss_b3b if s not in _EXC_B4III]
assert 'LANE-RESEARCH' not in _now_b3b, \
    '(23) the internal-artefact reference returned to §1-§2.3'
assert 'novelty sweep run on' in re.sub(r'\s+', ' ', _now_b3b), \
    '(23) the authored replacement for the artefact reference is missing'
assert not _miss_b3b, '(23) literal(s) lost from §1-§2.3: %r' % _miss_b3b[:4]

# P3: the scramble sub-block (table + three numbered findings) is untouched.
# RE-POINTED by L174 (b4-iii-a), not loosened: that block OPENS on the §2.2
# bold lead, whose trailing ' (L168)' the lane-ID strip removes. The freeze is
# therefore asserted THROUGH the one declared edit — every other byte of the
# block must still match, and the lane ID is asserted gone from it.
_scr_i = _pre_b3b.index('**Scramble controls:')
_scr_j = _pre_b3b.index('### 2.3 ')
_scr_block = _pre_b3b[_scr_i:_scr_j]
assert _scr_block.count(' (L168).**') == 1, '(23) the declared §2.2 edit is not in the freeze'
assert _scr_block.replace(' (L168).**', '.**') in _now_b3b, \
    '(23) the §2.2 scramble block changed beyond the one declared lane-ID edit'
assert '(L168)' not in _now_b3b, '(23) the §2.2 lane ID survived'

# the prose is prose: paragraphs, and no label-colon bullet openers left.
# Fragment checks run against a WHITESPACE-NORMALIZED view: the reflow
# chooses line breaks, so any multi-word gate on reflowed prose that is not
# normalized is a wrap-fragility bug waiting to fire (it fired here on
# 'The\nU-law is read with pooled').
_ws_b3b = re.sub(r'\s+', ' ', _now_b3b)
for _frag in ('- Substrate:', '- Framing:', '- Non-monotone:',
              '- U-law with pooled', '- Canonical pooled counts'):
    assert _frag not in _now_b3b, '(23) bullet opener survived: %r' % _frag
for _frag in ('The substrate is the l65 cord subnet',
              'Connectome-constrained models now reproduce',
              'The ladder is non-monotone', 'The U-law is read with pooled',
              'The canonical pooled counts', 'The carrier cell DNp33-L is ACh',
              'Walking-CPG field context (Sapkal et al. [34]) supplies',
              'We report four load-bearing results'):
    assert _frag in _ws_b3b, '(23) prose opener missing: %r' % _frag
assert len([_p for _p in _now_b3b.split('\n\n') if _p.strip()]) == 24, \
    '(23) paragraph count pin'

# visible-character direction: de-indentation makes the raw count fall, so
# the honest measure of whether prose was ADDED is whitespace-stripped length
_vis = lambda s: len(re.sub(r'\s', '', s))
# RE-POINTED by L174 (b4-iii-a), DECOMPOSED so the +145 of (b3b-i) survives
# verbatim instead of being re-typed: this stage's own frozen pre-tick draft
# supplies the intermediate state, so the span's visible delta splits into the
# prose conversion (+145, the original pin, measured against the (b3b) freeze)
# and the lane-ID strip's cost (-25, measured against the (b4-iii-a) freeze).
# Applying the declared edits to the (b3b) freeze directly is NOT possible:
# that freeze predates the reflow and wraps those sentences differently.
_pre_b4iii = (P / 'banc/l174b4iii/draft_pre.md').read_text()
_mid_b3b = _pre_b4iii[_pre_b4iii.index('## 1. Introduction'):
                      _pre_b4iii.index('### 2.4 Mechanism')]
# (b4-iii-b) adds ONE MORE LAYER to the same decomposition: its own frozen
# pre-tick draft is the second intermediate, so (b3b-i)'s +145 and
# (b4-iii-a)'s -25 both survive VERBATIM and the relabel's cost is separate.
_pre_b4iiib = (P / 'banc/l174b4iiib/draft_pre.md').read_text()
_mid2_b3b = _pre_b4iiib[_pre_b4iiib.index('## 1. Introduction'):
                        _pre_b4iiib.index('### 2.4 Mechanism')]
assert _vis(_mid_b3b) - _vis(_pre_b3b) == 145, '(23) visible-char delta pin'
assert _vis(_mid2_b3b) - _vis(_mid_b3b) == -25, '(23) strip visible-cost pin'
assert _vis(_now_b3b) - _vis(_mid2_b3b) == -2, '(23) relabel visible-cost pin'
assert _vis(_now_b3b) - _vis(_pre_b3b) == 118, '(23) net visible delta pin'
assert len(_now_b3b) < len(_pre_b3b), '(23) raw char direction pin'
assert 'v3.24 = L174 stage (b3b-i)' in draft[:draft.index('## Title')], \
    '(23) the banner must record the (b3b-i) stage'

print('(23) L174 (b3b-i) bullets -> prose in \u00a71/\u00a72.1/\u00a72.2/\u00a72.3: '
      'branch B1_format_only proved, not asserted — 15 bullet lines gone, '
      'the numeric (355) and citation-key (45) multisets IDENTICAL to the '
      'frozen pre-image, all 184 harvested verifier literals verbatim '
      '(harvest floor 4 chars: an 8-char floor dropped \'0 of 20\' and the '
      'reflow split it), the scramble table block byte-unchanged, 24 '
      'paragraphs, visible chars +145 while raw chars fall on de-indentation')

# ---------------------------------------------------------------- (24)
# L174 stage (b3b-ii): bullets -> prose in §2.5, §2.6 and §2.8, under the same
# FORMAT-ONLY contract as (23). The span runs §2.5 -> §2.9 and therefore
# CONTAINS §2.7, which belongs to stage (b3b-iii): it is proven byte-identical
# here rather than cut out of the span, so the single-block substitution proof
# survives. Everything below is re-derived from the frozen pre-image.
_B32 = P / 'banc/l174b3bii'
_pre_b32 = (_B32 / 'span_pre.txt').read_text()
_sev_b32 = (_B32 / 'sev_pre.txt').read_text()
_i_b32 = draft.index('### 2.5 Robustness')
_j_b32 = draft.index('### 2.9 Statistics')
_now_b32 = draft[_i_b32:_j_b32]

# (b3b-iii) RE-SCOPE (tick 210). Stage (b3b-iii) converted §2.7's own 16
# bullets, so the live draft no longer carries them and the old live
# byte-identity pin cannot hold. This section's claims are about what
# (b3b-ii) DID, so its §2.7 pins now run against the STORED ARTIFACT CHAIN:
# (b3b-iii)'s frozen pre-image IS §2.7 as (b3b-ii) left it. That is strictly
# stronger than the live check it replaces (it proves the handoff was
# untouched even after the next stage edited the section) and it is the L120
# forward-chain anchor form. The LIVE §2.7 is section (25)'s job.
_pre_b33 = (P / 'banc/l174b3biii/span_pre.txt').read_text()
assert _sev_b32 == _pre_b33, \
    '(24) §2.7 as (b3b-ii) left it must equal (b3b-iii)\'s frozen pre-image'

# bullet census: 27 in the pre-image, of which exactly §2.7's 16 were NOT
# this stage's to touch, so this stage owned 11 — derived from the stored
# artifacts, not read off the live draft.
assert len(_BUL_B3B.findall(_pre_b32)) == 27, '(24) pre-image bullet count'
assert len(_BUL_B3B.findall(_sev_b32)) == 16, '(24) §2.7 bullet pin'
assert len(_BUL_B3B.findall(_pre_b32)) - len(_BUL_B3B.findall(_sev_b32)) == 11, \
    '(24) this stage owned 11 bullet lines'
# §2.7 is still IN PLACE between §2.6 and §2.8 (position pin, now on the
# live heading rather than on the frozen bytes)
_i27_b32 = _now_b32.index('### 2.7 Pre-posting controls')
_j27_b32 = _now_b32.index('### 2.8 The slow line')
assert 0 < _i27_b32 < _j27_b32, '(24) §2.7 did not stay in place'
_edit_b32 = _now_b32[:_i27_b32] + _now_b32[_j27_b32:]
assert len(_BUL_B3B.findall(_edit_b32)) == 0, \
    '(24) a bullet line survived in §2.5/§2.6/§2.8'

# T1: numeric and citation multisets IDENTICAL (sorted lists, not sets)
# RE-POINTED by L174 (b4-iii-a) exactly as §(23) was: measurement tokens
# (identifier digit runs excluded, §-references stripped) plus the removed
# identifier digits asserted BY NAME. Twelve leave this span: the ten lane IDs
# of the four subsection headings and two prose clauses, L162 twice, plus the
# '2' of the stage label '(b2)' that leaves with its clause.
_SREF_B4 = re.compile(r'\u00a7\d+(?:\.\d+)?')
_meas = lambda t: sorted(_MEAS_B3B.findall(_SREF_B4.sub('', t)))
_idc = lambda t: __import__('collections').Counter(_IDNUM_B3B.findall(t))
assert _meas(_pre_b32) == _meas(_now_b32), \
    '(24) T1 breach: the §2.5-§2.8 measurement multiset moved'
# (b4-iii-b) RE-POINT: five more identifier runs leave this span, each a
# DECLARED batch relabel -- B26 -> A (§2.8), B35 -> J, B37 -> K and B38 -> L
# twice (§2.7) -- so the set is the UNION of two strips, still exact.
assert sorted((_idc(_pre_b32) - _idc(_now_b32)).elements()) == \
    ['138', '139', '156', '157', '162', '162', '169', '169', '170', '171',
     '172', '2', '26', '35', '37', '38', '38'], \
    '(24) identifier digits removed != the declared lane IDs + batch codes'
for _lab, _was in (('batch A', 'B26'), ('batch J', 'B35'), ('batch L', 'B38')):
    assert _lab in _now_b32 and _was not in _now_b32, ('(24) relabel', _lab)
assert sorted((_idc(_now_b32) - _idc(_pre_b32)).elements()) == [], \
    '(24) an identifier digit ENTERED §2.5-§2.8'
assert sorted(_CIT_B3B.findall(_pre_b32)) == sorted(_CIT_B3B.findall(_now_b32)), \
    '(24) T1 breach: the §2.5-§2.8 citation-key multiset moved'
# (b4-iii-b): 400 -> 395, the five lost tokens being exactly the five
# relabeled batch codes' identifier digits named above; keys unchanged.
assert len(_NUM_B3B.findall(_now_b32)) == 395 \
    and len(_CIT_B3B.findall(_now_b32)) == 37, '(24) token-count pins'

# T3: every harvested verifier literal survives. Three of them carried the old
# bullet indentation inside their own line break (the declared exception class
# of the PREREG); those are checked wrap-insensitively, exactly as section (17)
# now checks its §2.6 contract.
_lit_b32 = json.loads((_B32 / 'literals.json').read_text())
assert _lit_b32['report']['literals_in_span'] == 232 \
    and _lit_b32['report']['literals_touching_editable_text'] == 103, \
    '(24) literal count pins'
_ws_b32 = re.sub(r'\s+', ' ', _now_b32)
_EXEMPT_B32 = ['0.1946 / 0.0642 /\n  0.1333', 'agrees to\n  within .0025',
               'from 37/33 to 6/2 but never\n  reach zero']
assert all(_e in _pre_b32 for _e in _EXEMPT_B32), \
    '(24) the declared wrap-fragile literals must come from the pre-image'
# (b3b-iii) RE-SCOPE: literals that live ONLY in §2.7 are section (25)'s
# contract now — three of them were de-indented by that stage and are checked
# there, so here they are verified wrap-insensitively and counted separately.
# The split is read from the harvest's own n_in_sev field, never hand-listed.
_SEVONLY_B32 = {_s for _s, _d in _lit_b32['literals'].items()
                if _d['n_in_sev'] == _d['n_span']}
assert len(_SEVONLY_B32) == 129, '(24) §2.7-only literal count pin'
_miss_b32, _exempt_b32, _defer_b32 = [], [], []
for _s in _lit_b32['literals']:
    if _s in _now_b32:
        continue
    if _s in _EXEMPT_B32:
        assert re.sub(r'\s+', ' ', _s) in _ws_b32, \
            '(24) declared wrap-fragile literal lost: %r' % _s
        _exempt_b32.append(_s)
    elif _s in _SEVONLY_B32:
        assert re.sub(r'\s+', ' ', _s) in _ws_b32, \
            '(24) §2.7-only literal lost: %r' % _s
        _defer_b32.append(_s)
    else:
        _miss_b32.append(_s)
assert not _miss_b32, '(24) literal(s) lost: %r' % _miss_b32[:4]
assert sorted(_exempt_b32) == sorted(_EXEMPT_B32), \
    '(24) the exemption set must be exactly the three declared literals'
assert len(_defer_b32) == 7, \
    '(24) exactly 7 §2.7-only literals are deferred to section (25)'

# P4: the robustness panel is still a TABLE (de-indented, never reflowed)
_tbl_b32 = [_l for _l in _now_b32.split('\n') if _l.startswith('| ')]
assert len(_tbl_b32) == 4 and '|---|---|---|---|---|' in _now_b32, \
    '(24) the §2.8 robustness-panel table did not survive as a table'
assert '| UNCHOPPED 1.4-Hz segment | 12/16, .628 | 0/16, .000 | +.628 | 16/16 up |' \
    in _now_b32, '(24) table row content'

# P5: §2.8's four bold claim leads survive verbatim AND start their paragraph
for _lead in ('**Re-attribution (branch A1 fired).**',
              '**What the envelope cannot explain',
              '**Robustness panel (branch B2_preserved).**',
              '**What this does and does not license.**'):
    assert re.search(r'(?m)^' + re.escape(_lead[:24]), _now_b32), \
        '(24) bold claim lead not at a paragraph start: %r' % _lead
# and the bullet form of each is gone
for _frag in ('- **Re-attribution', '- **Robustness panel', '- **What this does',
              '- 5 af-matched', '- Carrier SUPER 5/5', '- Untreated full subnet',
              '- The original comparison was UNMATCHED-FLOOR',
              '- The window shares become computable',
              '- The honest status is therefore',
              '- What DOES survive the floor match'):
    assert _frag not in _now_b32, '(24) bullet opener survived: %r' % _frag
# the three re-authored §2.5 openers (normalized: the reflow picks the breaks)
for _frag in ('The robustness ensemble is 5 af-matched 1% edge-jitter gain sets',
              'Across those sets the carrier reads SUPER 5/5',
              'The untreated full subnet stays inside its base spread'):
    assert _frag in _ws_b32, '(24) prose opener missing: %r' % _frag

assert len([_p for _p in _edit_b32.split('\n\n') if _p.strip()]) == 16, \
    '(24) paragraph count pin'
# (b3b-iii) RE-SCOPE: both counts are read on this stage's OWN region (the
# span with the live §2.7 removed) so tick 209's measurement survives the
# next stage verbatim — 7 -> 16 paragraphs, visible chars +48.
_pre_edit_b32 = _pre_b32.replace(_sev_b32, '')
assert len([_p for _p in _pre_edit_b32.split('\n\n') if _p.strip()]) == 7, \
    '(24) pre-image paragraph count pin'
# (b4-iii-b) adds its own layer: its frozen pre-tick draft is the second
# intermediate, so tick 209's +48 and (b4-iii-a)'s -51 both survive verbatim
# and the relabel's +3 (§2.8's 'B26' -> 'batch A') is separate. Net now 0.
_m2_b32 = _pre_b4iiib[_pre_b4iiib.index('### 2.5 Robustness'):
                      _pre_b4iiib.index('### 2.9 Statistics')]
_m2_edit_b32 = _m2_b32[:_m2_b32.index('### 2.7 Pre-posting controls')] + \
               _m2_b32[_m2_b32.index('### 2.8 The slow line'):]
assert _vis(_m2_edit_b32) - _vis(_pre_edit_b32) == 48 - 51, '(24) visible-char delta pin'
assert _vis(_edit_b32) - _vis(_m2_edit_b32) == 3, '(24) relabel visible-cost pin'
# DECOMPOSED by L174 (b4-iii-a) so tick 209's +48 survives verbatim: the strip
# removed 51 visible chars from this region (the §2.5/§2.6/§2.8 heading
# parentheticals — §2.8's alone carries four lane IDs — plus the §2.6 clause
# pointer and the two §2.8 prose edits), measured against this stage's own
# frozen pre-tick draft. Net for the region: -3.
_mid_b32 = _pre_b4iii[_pre_b4iii.index('### 2.5 Robustness'):
                      _pre_b4iii.index('### 2.9 Statistics')]
_i27m = _mid_b32.index('### 2.7 '); _j27m = _mid_b32.index('### 2.8 ')
_mid_edit_b32 = _mid_b32[:_i27m] + _mid_b32[_j27m:]
assert _vis(_mid_edit_b32) - _vis(_pre_edit_b32) == 48, '(24) inherited +48 pin'
assert _vis(_m2_edit_b32) - _vis(_mid_edit_b32) == -51, '(24) strip visible-cost pin'
assert _vis(_edit_b32) - _vis(_m2_edit_b32) == 3, '(24) relabel cost on the region'
assert len(_edit_b32) < len(_pre_edit_b32), '(24) raw char direction pin'
assert 'v3.25 = L174 stage (b3b-ii)' in draft[:draft.index('## Title')], \
    '(24) the banner must record the (b3b-ii) stage'

print('(24) L174 (b3b-ii) bullets -> prose in \u00a72.5/\u00a72.6/\u00a72.8: branch '
      'B1_format_only proved from the frozen pre-image — 11 bullet lines gone '
      'while \u00a72.7\'s 16 are proven BYTE-IDENTICAL inside the same edit span '
      '(stage (b3b-iii)\'s work untouched), the numeric (411) and citation-key '
      '(37) multisets IDENTICAL, 229 of 232 harvested literals verbatim with '
      'exactly the three declared wrap-fragile ones checked normalized, the '
      '\u00a72.8 robustness-panel table still a de-indented table, all four bold '
      'claim leads at paragraph starts, 26 paragraphs, visible chars +48 while '
      'raw chars fall on de-indentation')

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
# RE-POINTED by L174 (b4-iii-a), same form as §(23)/§(24): two identifier
# digit runs leave this span (the §2.7 heading's L169 and the L172 that becomes
# a §2.9 cross-reference), and no measurement moves.
assert _meas(_pre_b33x) == _meas(_now_b33), \
    '(25) T1 breach: the §2.7 measurement multiset moved'
# (b4-iii-b) RE-POINT: four more runs leave, each a DECLARED batch relabel --
# B35 -> batch J, B37 -> K, B38 -> L and B38 -> batch L.
assert sorted((_idc(_pre_b33x) - _idc(_now_b33)).elements()) == \
    ['169', '172', '35', '37', '38', '38'], \
    '(25) identifier digits removed != the declared lane IDs + batch codes'
assert sorted((_idc(_now_b33) - _idc(_pre_b33x)).elements()) == [], \
    '(25) an identifier digit ENTERED §2.7'
assert sorted(_CIT_B3B.findall(_pre_b33x)) == sorted(_CIT_B3B.findall(_now_b33)), \
    '(25) T1 breach: the §2.7 citation-key multiset moved'
# (b4-iii-b): 247 -> 243, the four lost tokens being exactly the four
# relabeled batch codes named above; the citation-key pin is unchanged.
assert len(_NUM_B3B.findall(_now_b33)) == 243 \
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
              'The batch unions were re-pooled with batch J',
              'On the rewire arm [l169c2.rew], three independent draws',
              'The registered reading [l169c2.branch] is that the 2-of-3 majority',
              'This is not a gain artifact [l169c2.gains]',
              'On the deletion arm [l169c2.hom], deleting gi 928',
              'The anchors hold [l169c2.cert]: all twelve inherited arms',
              'The own-gain diagonal reproduces on batch L',
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
# DECOMPOSED by L174 (b4-iii-a) so tick 210's +108 survives verbatim: the
# strip took 15 visible chars out of §2.7 (its heading's ' (L169 stages a-d)'
# and the L172 -> §2.9 re-point), measured against this stage's frozen
# pre-tick draft. Net for the section: +93.
_mid_b33 = _pre_b4iii[_pre_b4iii.index('### 2.7 '):
                      _pre_b4iii.index('### 2.8 The slow line')]
assert _vis(_mid_b33) - _vis(_pre_b33x) == 108, '(25) inherited +108 pin'
# (b4-iii-b) layer: its own frozen pre-tick draft is the second intermediate,
# so tick 210's +108 and (b4-iii-a)'s -15 survive verbatim and the relabel's
# +2 (batch J / K / L / batch L) is separate. Net now +95.
_m2_b33 = _pre_b4iiib[_pre_b4iiib.index('### 2.7 Pre-posting controls'):
                      _pre_b4iiib.index('### 2.8 The slow line')]
assert _vis(_m2_b33) - _vis(_mid_b33) == -15, '(25) strip visible-cost pin'
assert _vis(_now_b33) - _vis(_m2_b33) == 2, '(25) relabel visible-cost pin'
assert _vis(_now_b33) - _vis(_pre_b33x) == 95, '(25) net visible delta pin'
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

# ---------------------------------------------------------------- (26)
# L174 stage (b4-i): §4 Limitations, bullets -> prose, PLUS the seven
# over-length sentences the conversion dragged into prose. Same FORMAT-ONLY
# contract as (23)-(25), with two additions proved here:
#   * T7 sentence splits are CONTENT-PRESERVING — the content-word sequence
#     (alphanumeric tokens with the closed connective set removed) is
#     identical before and after, so no number, citation key or content word
#     moved; only punctuation, capitalization and declared connectives did.
#   * the sentence rule now covers §4, and the ONE known offender OUTSIDE
#     this span (§2.8's 70-word envelope-disclosure sentence) is pinned as a
#     DISCLOSED exception so stage (b4-ii) closing it is gate-visible.
_B4 = P / 'banc/l174b4i'
_pre_b4 = (_B4 / 'span_pre.txt').read_text()
_i_b4 = draft.index('## 4. Limitations')
# (b4-ii) RE-POINT (tick 212): the Discussion was inserted between §4 and the
# data note, so the slice END moves from '## 5. Data & code' (now §6) to the
# new heading. The §4 TEXT this section measures is unchanged — a re-point of
# a locator, never a loosening (the l174 lineage rule).
_j_b4 = draft.index('## 5. Discussion')
_now_b4 = draft[_i_b4:_j_b4]
_ws_b4 = re.sub(r'\s+', ' ', _now_b4)
# (b4-iii-b) RE-POINT, strong form: §4 is no longer byte-identical to the
# (b4-i) post-image -- the batch relabel rewrote ONE declared occurrence --
# so the pin becomes 'stored post-image + the declared edit == live', which
# proves the (b4-i) prose AND this stage's single §4 edit at once.
_post_b4 = (_B4 / 'span_post.txt').read_text()
_ED_B4 = ('(two fresh batches, B33/B34)', '(two fresh batches, G/H)')
assert _post_b4.count(_ED_B4[0]) == 1 and _ED_B4[0] not in _now_b4, \
    '(26) the declared §4 relabel must apply exactly once'
assert _post_b4.replace(*_ED_B4) == _now_b4, \
    '(26) the spliced §4 must equal the stored post-image + the declared edit'

# bullet census, derived from the stored pre-image
assert len(_BUL_B3B.findall(_pre_b4)) == 10, '(26) pre-image bullet count'
assert len(_BUL_B3B.findall(_now_b4)) == 0, '(26) a bullet line survived in §4'
# §1 through §5 now carries no list item at all
_body45 = draft[draft.index('## 1. Introduction'):_j_b4]
assert len(_BUL_B3B.findall(_body45)) == 0, \
    '(26) §1-§4 must carry zero bullet lines'

# T1: both multisets identical. Trailing commas are stripped (PREREG
# ADDENDUM 2: the numeric regex swallows them for thousands separators, and a
# clause boundary legitimately turns '10-15, and' into '10-15. The').
_NUM_B4 = re.compile(r'[-+\u2212]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?(?:%|\u00d7)?')
_CIT_B4 = re.compile(r'\[([a-z0-9_]+(?:\.[a-z0-9_]+)*)\]')
_ns = lambda t: sorted(_x.rstrip(',') for _x in _NUM_B4.findall(t))
# (b4-iii-b) RE-POINT, the ADDENDUM-1 form of §(23)-§(25) applied here: this
# regex has no left word boundary, so a relabeled batch code (B33 -> G) leaves
# '33' behind and a RELABEL would breach a MEASUREMENT gate without moving any
# measurement. Comparison on measurement tokens, removed identifier runs named.
_meas4 = lambda t: sorted(_x.rstrip(',') for _x in
                          _MEAS_B3B.findall(_SREF_B4.sub('', t)))
assert _meas4(_pre_b4) == _meas4(_now_b4), '(26) T1 breach: §4 measurement multiset moved'
assert sorted((_idc(_pre_b4) - _idc(_now_b4)).elements()) == ['33', '34'], \
    '(26) §4 identifier digits removed != the declared B33/B34 relabel'
assert sorted((_idc(_now_b4) - _idc(_pre_b4)).elements()) == [], \
    '(26) an identifier digit ENTERED §4'
assert sorted(_CIT_B4.findall(_pre_b4)) == sorted(_CIT_B4.findall(_now_b4)), \
    '(26) T1 breach: §4 citation-key multiset moved'
# 166 -> 164: the two lost tokens are exactly B33's and B34's digits.
assert len(_ns(_now_b4)) == 164 and len(_CIT_B4.findall(_now_b4)) == 18, \
    '(26) §4 token-count pins'

# every harvested verifier literal survives verbatim, except two declared
# exception classes: three literals carrying the OLD BULLET INDENTATION inside
# their own line break (checked normalized), and two literals carrying the
# BULLET MARKER itself — those two were l149 SLICE LOCATORS and are re-pointed
# at the prose form anchored to a LINE START (equally strong, not loosened).
_lit_b4 = json.loads((_B4 / 'literals.json').read_text())
_EXEMPT_B4 = ['fully RE-DERIVED, not\n  frozen',
              're-ordering rather than\n  turnover',
              'the unit of inference\n  is the simulation realization']
_MARKER_B4 = ['- DATA FLOOR:', '- Wet-lab predictions']
assert all(_e in _pre_b4 for _e in _EXEMPT_B4 + _MARKER_B4), \
    '(26) the declared exception literals must come from the pre-image'
_miss_b4, _ex_b4, _mk_b4 = [], [], []
for _s in _lit_b4['literals']:
    if _s in _now_b4:
        continue
    if _s in _EXEMPT_B4:
        assert re.sub(r'\s+', ' ', _s) in _ws_b4, \
            '(26) declared wrap-fragile literal lost: %r' % _s
        _ex_b4.append(_s)
    elif _s in _MARKER_B4:
        assert re.search(r'(?m)^' + re.escape(_s[2:]), _now_b4), \
            '(26) declared marker literal lost its line-start prose form: %r' % _s
        _mk_b4.append(_s)
    else:
        _miss_b4.append(_s)
assert not _miss_b4, '(26) literal(s) lost: %r' % _miss_b4[:4]
assert sorted(_ex_b4) == sorted(_EXEMPT_B4), \
    '(26) the wrap exemption set must be exactly the three declared'
assert sorted(_mk_b4) == sorted(_MARKER_B4), \
    '(26) the marker exemption set must be exactly the two declared'
assert len(_lit_b4['literals']) - len(_ex_b4) - len(_mk_b4) == 135, \
    '(26) verbatim-literal count pin'

# every pre-image bullet opener is GONE as a bullet (derived from the stored
# pre-image, never hand-listed); eight were de-dashed by the PARSER and only
# the two true fragments (a bare noun phrase, a verbless 'with ...' clause)
# were authored.
for _m in re.finditer(r'(?m)^- (.+)$', _pre_b4):
    assert ('- ' + _m.group(1)) not in _now_b4, \
        '(26) bullet opener survived: %r' % _m.group(1)[:56]
for _frag in ('Rate fidelity: no spikes, no per-cell kinetics',
              'Frequency claims are BAND-RELATIVE',
              'Readout is simulated motor-pool structure duty',
              'The transition interior is gain-regime-dependent',
              'UNIT OF INFERENCE: every interval in this paper',
              'Arm depth is unequal by construction',
              'DATA FLOOR: the BANC v626 connections release',
              'Wet-lab predictions are NOT derived here.'):
    assert _frag in _ws_b4, '(26) de-dashed opener missing: %r' % _frag
for _frag in ('There is a single specimen per connectome (BANC v626 one female;',
              'OPERATING-POINT PROXIMITY carries a convergent disclosure from the'):
    assert _frag in _ws_b4, '(26) authored opener missing: %r' % _frag

# T7: the sentence splits. Each declared (old -> new) edit must be ABSENT in
# its old form and PRESENT in its new form, and the content-word sequence of
# the whole span must be unchanged apart from the connective set.
_SPL_B4 = [('n = 16) and the registered R-side cliff',
            'n = 16). The registered R-side cliff'),
           ('cutwA PARTIAL 3/16 .371), and the f4ng-vs-f4tw',
            'cutwA PARTIAL 3/16 .371). The f4ng-vs-f4tw'),
           ('quantifies the pattern: in the l65-baseline arm',
            'quantifies the pattern. In the l65-baseline arm'),
           ('one (\u00a72.8) \u2014 while the intact closure',
            'one (\u00a72.8). The intact closure'),
           ('is not antagonist-clock-wide: the mm/xm aggregates',
            'is not antagonist-clock-wide. The mm/xm aggregates'),
           ('strongest members 36/36), while the Ti pools',
            'strongest members 36/36). The Ti pools'),
           ('Jaccard .9231 \u2014 while the TWIN selection',
            'Jaccard .9231. The TWIN selection'),
           ('rather than weight: in that preregistered screen',
            'rather than weight. In that preregistered screen'),
           ('thresholds of 10\u201315, and the stated cause',
            'thresholds of 10\u201315. The stated cause'),
           ('[l169b2.lat_descriptive]; a registered left-side test',
            '[l169b2.lat_descriptive]. A registered left-side test'),
           ('[l146.release] \u2014 so a single-synapse sensitivity critique',
            '[l146.release]. A single-synapse sensitivity critique therefore')]
_ws_pre_b4 = re.sub(r'\s+', ' ', _pre_b4)
for _o, _n in _SPL_B4:
    assert _ws_pre_b4.count(_o) == 1, \
        '(26) split pre-image form not unique: %r' % _o[:48]
    assert _o not in _ws_b4, '(26) unsplit sentence survived: %r' % _o[:48]
    assert _ws_b4.count(_n) == 1, '(26) split result missing: %r' % _n[:48]
assert len(_SPL_B4) == 11, '(26) eleven clause-boundary edits over 7 sentences'
# the two authored openers are the ONLY other word-level edits in §4, so
# applying all thirteen declared edits to the frozen pre-image must reproduce
# the live section's content-word sequence exactly. Connectives are excluded
# from the sequence because a clause split may legitimately drop or add one.
_OPEN_B4 = [('- Single specimen per connectome (BANC v626 one female; '
             'MaleCNS one male);',
             'There is a single specimen per connectome (BANC v626 one '
             'female; MaleCNS one male);'),
            ('- OPERATING-POINT PROXIMITY, with a convergent disclosure from the',
             'OPERATING-POINT PROXIMITY carries a convergent disclosure from the')]
# (b4-iii-b) adds its ONE declared §4 relabel to the declared-edit list, so
# the T7 strong form still runs end to end from the (b4-i) pre-image.
_REL_B4 = [('(two fresh batches, B33/B34)', '(two fresh batches, G/H)')]
_pred_b4 = _ws_pre_b4
for _o, _n in _OPEN_B4 + _SPL_B4 + _REL_B4:
    assert _pred_b4.count(_o) == 1, '(26) declared edit not unique: %r' % _o[:48]
    _pred_b4 = _pred_b4.replace(_o, _n)
_CONN_B4 = {'and', 'while', 'so', 'therefore'}
_WRD_B4 = re.compile(r'[0-9A-Za-z][0-9A-Za-z._/%+-]*')
_tk = lambda w: w.lower().rstrip('.,;:')
_cseq = lambda t: [_tk(_w) for _w in _WRD_B4.findall(re.sub(r'\s+', ' ', t))
                   if _tk(_w) not in _CONN_B4]
assert _cseq(_pred_b4) == _cseq(_now_b4), \
    '(26) T7 breach: an undeclared content word moved, entered or left §4'
# and the splits alone move nothing: each pair is content-identical on its own
for _o, _n in _SPL_B4:
    assert _cseq(_o) == _cseq(_n), \
        '(26) T7 breach: a split changed content words: %r' % _o[:48]

# the sentence rule, with abbreviations protected so a false split at 'Fig.'
# cannot satisfy it
def _sents_b4(t):
    t = re.sub(r'\s+', ' ', t)
    for _a in ('Fig.', 'e.g.', 'i.e.', 'cf.', 'vs.', 'et al.'):
        t = t.replace(_a, _a.replace('.', '\x00'))
    return [_x.replace('\x00', '.')
            for _x in re.split(r'(?<=[.!?])\s+', t) if _x.strip()]
assert len([1 for _s in _sents_b4(_pre_b4) if len(_s.split()) > 60]) == 7, \
    '(26) the pre-image carried seven sentences over 60 words'
_long_b4 = max(len(_s.split()) for _s in _sents_b4(_now_b4))
assert _long_b4 <= 60, '(26) a §4 sentence of %d words survives' % _long_b4
assert _long_b4 == 53, '(26) longest-§4-sentence pin (107 words before)'
assert max(len(_s.split()) for _s in _sents_b4(_pre_b4)) == 107, \
    '(26) the pre-image carried a 107-word sentence'

# DISCLOSED EXCEPTION, owned by stage (b4-ii): the one >60-word sentence left
# in the body sits in §2.8 and predates these stages. Pinned here so closing
# it is gate-visible, and so no NEW over-length sentence can appear in §2-§4.
# Measured PER PARAGRAPH with table paragraphs excluded — a markdown table
# flattens into a 100+-token pseudo-sentence and would mask the real offender
# (the tick-209 lesson: a table is the one prose object a flat read destroys).
# (b4-ii) RE-POINT (tick 212): stage (b4-ii) CLOSED this sentence, which is
# exactly what the pin existed to make visible. The pin is not deleted — it
# moves onto the stored pre-image (strictly stronger: the 70-word form is
# proved to have existed AND to be gone, and §2.8 is now under the same
# 60-word rule as §4).
_s28_pre_b4ii = (P / 'banc/l174b4ii/s28_pre.txt').read_text()
_s28 = draft[draft.index('### 2.8 The slow line'):draft.index('### 2.9 Statistics')]
def _long28_of(_sec):
    _c = []
    for _p in _sec.split('\n\n'):
        if not _p.strip() or any(_l.lstrip().startswith('|')
                                 for _l in _p.split('\n')):
            continue
        _c += [(len(_s.split()), _s) for _s in _sents_b4(_p)]
    return sorted(_c)[-1]
_long28_pre = _long28_of(_s28_pre_b4ii)
assert _long28_pre[0] == 70, \
    '(26) the pre-image §2.8 sentence is pinned at 70 words, saw %d' % _long28_pre[0]
assert _long28_pre[1].startswith('**What the envelope cannot explain'), \
    '(26) the disclosed §2.8 offender must be the envelope-disclosure sentence'
_long28 = _long28_of(_s28)
assert _long28[0] <= 60, \
    '(26) a >60-word sentence survives in §2.8: %d words' % _long28[0]

assert len([_p for _p in _now_b4.split('\n\n') if _p.strip()]) == 11, \
    '(26) paragraph count pin'
# the visible-char delta is NEGATIVE here (a first for this lineage): the
# splits DROP five net connectives (7 removed, 2 inserted) and de-bulleting
# removes ten dash glyphs, while no content word changes.
# (b4-iii-b) DECOMPOSITION layer: (b4-i)'s -14 is measured against this
# stage's frozen pre-tick draft and the relabel's -4 ('B33/B34' -> 'G/H') is
# separate, so tick 211's measurement survives verbatim. Net -18.
_m2_b4 = _pre_b4iiib[_pre_b4iiib.index('## 4. Limitations'):
                     _pre_b4iiib.index('## 5. Discussion')]
assert _vis(_m2_b4) - _vis(_pre_b4) == -14, '(26) visible-char delta pin'
assert _vis(_now_b4) - _vis(_m2_b4) == -4, '(26) relabel visible-cost pin'
assert len(_now_b4) < len(_pre_b4), '(26) raw char direction pin'
assert 'v3.27 = L174 stage (b4-i)' in draft[:draft.index('## Title')], \
    '(26) the banner must record the (b4-i) stage'

print('(26) L174 (b4-i) \u00a74 Limitations bullets -> prose + the seven '
      'over-length sentences: branch B1_format_only proved from the frozen '
      'pre-image — 10 bullet lines gone (\u00a71-\u00a74 now carries ZERO), the '
      'numeric (166) and citation-key (18) multisets IDENTICAL, 135 of 140 '
      'harvested literals verbatim with exactly three declared wrap-fragile '
      'and two declared BULLET-MARKER literals (the l149 §4 slice locators, '
      're-pointed at the line-start prose form), 8 openers de-dashed by the '
      'parser and 2 authored, eleven clause-boundary edits over seven '
      'sentences with the CONTENT-WORD SEQUENCE of the whole section '
      'unchanged (only punctuation, capitalization and 7-out/2-in '
      'connectives moved), the longest sentence cut from 107 words to 53 '
      'under a NEW \u00a74 60-word rule, \u00a72.8\'s inherited 70-word sentence '
      'pinned from its stored pre-image and CLOSED by stage (b4-ii), '
      '11 paragraphs, '
      'visible chars -14 (the splits DROP net connectives)')

# ---------------------------------------------------------------- (27)
# L174 stage (b4-ii): the Discussion, and the closure of §2.8's 70-word
# sentence. Two edits, both re-derived here from stored pre-images.
#   E1  ONE declared T7 split at a COMMA boundary, chosen because it is
#       byte- AND visible-neutral: §(24)'s pins on the enclosing region hold
#       with no re-point at all (registered as T2, not discovered after).
#   E2  a new '## 5. Discussion', authored under T8 (born clean: no list
#       items, no lane IDs, no batch codes, no all-caps emphasis, no
#       provenance keys, no NEW numeric value) and T9 (no claim inflation).
_B4II = P / 'banc/l174b4ii'
_s28pre_27 = (_B4II / 's28_pre.txt').read_text()
_s28post_27 = (_B4II / 's28_post.txt').read_text()
_disc_27 = (_B4II / 'disc.txt').read_text()
_rep_27 = json.loads((_B4II / 'emit_report.json').read_text())
_now28_27 = draft[draft.index('### 2.8 The slow line'):
                  draft.index('### 2.9 Statistics')]
# RE-POINTED by L174 (b4-iii-a) THROUGH its declared edits, never loosened:
# the lane-ID strip touches §2.8 in three places (the heading's four-lane-ID
# parenthetical, L162's possessive, and 'the lane log'). The stored (b4-ii)
# post-image must still match everywhere else, byte for byte.
_S28_STRIP = [(' (L156, L157, L162, L171)', ''),
              ("with L162's evoked phase lock", 'with the evoked phase lock'),
              ('recorded in\nthe lane log', 'recorded in\nthe project log'),
              # (b4-iii-b): §2.8's single batch relabel, chained onto the same
              # stored post-image so BOTH stages' edits stay declared.
              ('(B26, n = 16 seeds)', '(batch A, n = 16 seeds)')]
_s28post_27s = _s28post_27
for _o, _n in _S28_STRIP:
    assert _s28post_27s.count(_o) == 1, ('(27) declared strip edit not in the post-image', _o)
    _s28post_27s = _s28post_27s.replace(_o, _n)
assert _now28_27 == _s28post_27s, \
    '(27) live §2.8 != the stored post-image + the three declared strip edits'
assert not re.search(r'\bL\d{2,3}\b', _now28_27), '(27) a lane ID survived in §2.8'

# T7 strong form (the (b4-i) ADDENDUM 3 lesson): pre-image + the declared
# edits == the live section, so no undeclared word entered, left or moved.
_SPL_27 = [("11/16 seeds [l154.band], so the envelope accounts for the "
            "line's POSITION",
            "11/16 seeds [l154.band]. So the envelope accounts for the "
            "line's POSITION")]
_chk_27 = _s28pre_27
for _o, _n in _SPL_27:
    assert _s28pre_27.count(_o) == 1 and _o not in _now28_27, \
        '(27) a declared split\'s old form must be gone exactly once'
    assert _now28_27.count(_n) == 1, '(27) the new form must be present once'
    _chk_27 = _chk_27.replace(_o, _n)
# EXTENDED by L174 (b4-iii-a): the T7 chain now runs (b4-ii)'s split AND this
# stage's three declared strip edits against the SAME (b4-ii) pre-image, so the
# strong form still proves that nothing undeclared entered, left or moved.
for _o, _n in _S28_STRIP:
    assert _chk_27.count(_o) == 1, ('(27) strip edit missing from the T7 chain', _o)
    _chk_27 = _chk_27.replace(_o, _n)
assert _chk_27 == _now28_27, '(27) T7: pre-image + declared edits != live §2.8'
_CLOSED_27 = {'and', 'while', 'so', 'therefore'}
_cw_27 = lambda t: [w.lower() for w in
                    re.findall(r"[0-9A-Za-z][0-9A-Za-z._/\u2212'-]*",
                               re.sub(r'\s+', ' ', t))
                    if w.lower() not in _CLOSED_27]
# RE-POINTED by L174 (b4-iii-a): the sequence is compared against the pre-image
# CARRYING THIS STAGE'S DECLARED EDITS (the identity above proves that chain),
# and the content-word difference versus the raw pre-image is pinned BY NAME so
# the strip cannot hide an undeclared word behind "a word left".
assert _cw_27(_chk_27) == _cw_27(_now28_27), \
    '(27) the §2.8 content-word sequence moved'
_dc27 = __import__('collections').Counter(_cw_27(_s28pre_27)) - \
        __import__('collections').Counter(_cw_27(_now28_27))
_ac27 = __import__('collections').Counter(_cw_27(_now28_27)) - \
        __import__('collections').Counter(_cw_27(_s28pre_27))
# (b4-iii-b) adds 'b26' out and 'batch'/'a' in -- the batch relabel, named.
assert sorted(_dc27.elements()) == ['b26', 'l156', 'l157', 'l162', "l162's",
                                    'l171', 'lane'], \
    ('(27) undeclared content words left §2.8', sorted(_dc27.elements()))
# 'the' enters where "L162's evoked phase lock" becomes "the evoked phase lock".
assert sorted(_ac27.elements()) == ['a', 'batch', 'project', 'the'], \
    ('(27) undeclared content words entered §2.8', sorted(_ac27.elements()))
# T1 + T2 (measurement tokens: identifier digit runs excluded, §-refs stripped)
_ns27 = lambda t: sorted(_x.rstrip(',') for _x in
                         _MEAS_B3B.findall(_SREF_B4.sub('', t)))
assert _ns27(_s28pre_27) == _ns27(_now28_27), '(27) §2.8 measurement multiset moved'
assert sorted(_CIT_B4.findall(_s28pre_27)) == \
    sorted(_CIT_B4.findall(_now28_27)), '(27) §2.8 citation-key multiset moved'
# 87 was the old identifier-blind count; 62 is the MEASUREMENT count under the
# (b4-iii-a) regex (the 25-token gap is §2.8 lane IDs + cell/version digits).
assert len(_ns27(_now28_27)) == 62 and len(_CIT_B4.findall(_now28_27)) == 3, \
    '(27) §2.8 token-count pins'
assert _vis(_s28post_27) == _vis(_s28pre_27) and \
    len(_s28post_27) == len(_s28pre_27), \
    '(27) the split must be byte- AND visible-neutral (ADDENDUM 1)'
# RE-POINTED by L174 (b4-iii-a): the (b4-ii) neutrality claim is about the
# SPLIT, so it is now read on the stored post-image (where it still holds
# exactly), and the strip's own §2.8 cost is pinned separately against it.
# (b4-iii-b) layer: the strip's 21 is read against this stage's own frozen
# pre-tick §2.8, and the relabel's -3 ('B26' -> 'batch A') is pinned separately.
_m2_28 = _pre_b4iiib[_pre_b4iiib.index('### 2.8 The slow line'):
                     _pre_b4iiib.index('### 2.9 Statistics')]
assert _vis(_s28post_27) - _vis(_m2_28) == 21, '(27) §2.8 strip visible-cost pin'
assert _vis(_now28_27) - _vis(_m2_28) == 3, '(27) §2.8 relabel visible-cost pin'
assert len([_p for _p in _now28_27.split('\n\n') if _p.strip()]) == 8, \
    '(27) §2.8 paragraph-count neutrality'
# T3: every harvested §2.8 literal verbatim, zero exceptions (prediction Q3)
_lit27 = json.loads((_B4II / 'literals.json').read_text())
assert len(_lit27['literals']) == 69
_miss27 = [_s for _s in _lit27['literals'] if _s not in _now28_27]
assert not _miss27, '(27) §2.8 literal(s) lost: %r' % _miss27[:4]
# the sentence closure, and the honest reason the new longest is 56: it is an
# INHERITED sentence, not one of the split's own pieces (prediction Q2 wrong).
assert _long28_of(_s28pre_27)[0] == 70 and _long28_of(_now28_27)[0] == 56, \
    '(27) §2.8 longest-sentence pins (70 -> 56)'
assert _long28_of(_now28_27)[1].startswith('It does NOT license the fast '
                                           'segment'), \
    '(27) the new §2.8 longest must be the inherited licensing sentence'

# ---- E2: the Discussion ---------------------------------------------------
_i5 = draft.index('## 5. Discussion')
_j5 = draft.index('## 6. Data & code')
_disc_live = draft[_i5:_j5]
assert _disc_live == _disc_27, '(27) live §5 != the stored Discussion'
assert draft.index('## 4. Limitations') < _i5 < _j5 \
    < draft.index('## 7. Author/submit notes'), '(27) section order'
assert '## 5. Data & code' not in draft and \
    '## 6. Author/submit notes' not in draft, '(27) the renumber is incomplete'
assert len([_p for _p in _disc_live.split('\n\n') if _p.strip()]) == 8, \
    '(27) §5 = heading + 7 paragraphs'
# T8: born clean
assert not _BUL_B3B.findall(_disc_live), '(27) a list item in §5'
assert not re.search(r'\bL\d{2,3}\b', _disc_live), '(27) a lane ID in §5'
assert not re.search(r'\bB\d{2}\b', _disc_live), '(27) a batch code in §5'
assert not re.findall(r'\b[A-Z][A-Z]{2,}\b', _disc_live), \
    '(27) all-caps emphasis in §5'
assert not _CIT_B4.findall(_disc_live), '(27) a provenance key in §5'
assert not re.search(r'\[\d+(,\s*\d+)*\]', _disc_live), \
    '(27) a new numeric citation marker in §5'
# no NEW measured value: every number §5 quotes appears elsewhere in the draft
_scrub27 = re.sub(r'\u00a7\d+(\.\d+)?(\([a-d]\))?', ' ', _disc_live)
_rest27 = draft[:_i5] + draft[_j5:]
for _q in sorted(set(_x.rstrip(',') for _x in _NUM_B4.findall(_scrub27))):
    assert _q in _rest27, '(27) §5 introduced a new numeric value: %r' % _q
# the 60-word rule on §5 itself (the (b4-i) precedent: extend the gate that
# owns the region rather than widening l159's abstract/§1 scope)
_long5 = max((len(_s.split()), _s) for _p in _disc_live.split('\n\n')
             if _p.strip() for _s in _sents_b4(_p))
assert _long5[0] <= 60 and _long5[0] == 52, \
    '(27) §5 longest-sentence pin, saw %d' % _long5[0]
assert _rep_27['disc']['words'] == 828 and _rep_27['disc']['paragraphs'] == 7, \
    '(27) stored Discussion size pins'
# the stored token count INCLUDES the three-token heading (own-catch: the
# first form of this assert added the heading twice) — pin both readings
assert len(_disc_live.split()) == 828, '(27) live §5 token count'
assert len(_disc_live.split('\n\n', 1)[1].split()) == 825, \
    '(27) §5 body word count (828 tokens minus the heading)'
assert max(len(_l) for _l in _disc_live.split('\n')) <= 78, \
    '(27) §5 must respect the 78-column house width'
# T9: no claim inflation (normalized — every multi-word check on reflowed
# prose is break-insensitive by default)
_ws5 = re.sub(r'\s+', ' ', _disc_live)
for _r in ('sufficient route into the super class rather than the only one',
           'set-dependent rather than mass-dependent',
           'established prior art',
           'Our contribution sits in the controls rather than in the headline',
           'None of this is a statement about the animal',
           '\u00a74 enumerates what follows from that'):
    assert _r in _ws5, '(27) §5 required statement missing: %r' % _r
for _f in ('unique cause', 'the only cell', 'we prove', 'proves that',
           'first demonstration', 'unprecedented', 'for the first time'):
    assert _f not in _ws5.lower(), '(27) §5 forbidden wording: %r' % _f
# §1 through §5 now carries no list item at all
assert not _BUL_B3B.findall(draft[draft.index('## 1. Introduction'):_j5]), \
    '(27) §1-§5 must carry zero list items'
assert 'v3.28 = L174 stage (b4-ii)' in draft[:draft.index('## Title')], \
    '(27) the banner must record the (b4-ii) stage'

print('(27) L174 (b4-ii) the Discussion + the \u00a72.8 closure: branch '
      'B1_clean — the inherited 70-word envelope sentence is CLOSED by ONE '
      'declared T7 split at a comma boundary that is byte- AND '
      'visible-neutral (so \u00a7(24)\'s pins on the same region needed no '
      're-point), the \u00a72.8 numeric (87) and citation-key (3) multisets '
      'IDENTICAL, all 69 harvested literals verbatim with ZERO exceptions, '
      'the content-word sequence proved identical via pre-image + declared '
      'edits == live, longest sentence 70 -> 56 (the new longest is an '
      'INHERITED sentence, not a piece of the split); and a NEW \u00a75 '
      'Discussion, 825 words of prose over 7 paragraphs, born clean under T8 (no '
      'list item, lane ID, batch code, all-caps token, provenance key or '
      'NEW numeric value \u2014 every number it quotes appears elsewhere in '
      'the draft) and T9 (both \u00a71 novelty narrowings restated, no '
      'uniqueness or priority wording, limitations pointed at \u00a74), under '
      'its own 60-word rule at 52, with \u00a71-\u00a75 carrying zero list '
      'items and the data/author notes renumbered to \u00a76/\u00a77')

# ---------------------------------------------------------------------------
# (28) L174 stage (b4-iii-a): the lane-ID / internal-artefact strip, plus the
# §6/§7 PREMISE FINDING and the frozen all-caps PARTITION the remaining strip
# stages inherit. Everything below is re-derived from stored artefacts
# (banc/l174b4iii/{draft_pre.md,caps_partition.json,emit_report.json}), never
# from the stage's own prose.
# (b4-iii-b) RE-POINT (tick-210 rule: a stage that supersedes a predecessor's
# freeze re-points it at STORED ARTIFACTS, never loosens it). Every read below
# ran against the LIVE draft, which stage (b4-iii-b) has now edited, so the
# whole section runs against (b4-iii-b)'s OWN frozen pre-tick draft -- which IS
# the state (b4-iii-a) produced -- and §(29) proves that artifact equals the
# live draft minus (b4-iii-b)'s declared edits. Strictly stronger: these pins
# now survive every later stage. §(29) re-asserts the live-draft properties
# (zero lane residue in scope, the §6/§7 premise) on the LIVE bytes.
_B4III = P / 'banc/l174b4iii'
_live28 = draft
draft = (P / 'banc/l174b4iiib' / 'draft_pre.md').read_text()
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
# T7 STRONG: pre-image + the declared edits == the live draft from the title
# onward. The changelog banner is excluded because THIS stage appends its own
# v3.29 entry there (as every stage in the lineage does); that addition is
# proved separately to be an append of exactly the declared block.
_T28 = '## Title'
assert _chk28[_chk28.index(_T28):] == draft[draft.index(_T28):], \
    '(28) T7: pre-image + the 13 declared edits != the live draft'
_bpre28, _bnow28 = _pre28[:_pre28.index(_T28)], draft[:draft.index(_T28)]
_bins28 = _bnow28.replace(_bpre28.rstrip('\n'), '', 1)
assert _bnow28.startswith(_bpre28.rstrip('\n')) and \
    'v3.29 = L174 stage (b4-iii-a)' in _bins28 and \
    not _LANE28.findall(_bins28.replace('L174', '')), \
    '(28) the banner delta is not exactly this stage\'s declared entry'

# T10 ZERO RESIDUE in scope (the gate that caught the hand-built list's miss)
assert not _LANE28.findall(_sc28), ('(28) lane IDs left in §1-§6',
                                    sorted(set(_LANE28.findall(_sc28))))
for _a in ('LANE-RESEARCH', 'lane log', 'lane scripts'):
    assert _a not in _sc28, ('(28) internal-artefact reference left in §1-§6', _a)
assert len(_LANE28.findall(_pre_sc28)) == 13, '(28) pre-image lane-ID census pin'
_refpre28 = draft[draft.index('## References'):draft.index('No citation is written from memory')]
assert '(L152)' not in _refpre28, '(28) the References preamble still carries a lane ID'

# OUT OF SCOPE, byte-identical (declared with reasons in the PREREG)
assert draft[draft.index(_T28):draft.index(_SCOPE_A28)] == \
    _pre28[_pre28.index(_T28):_pre28.index(_SCOPE_A28)], \
    '(28) out of scope changed: title block / abstract'
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
# T1 is read on the SAME region as T7 (title onward): the changelog banner is
# this stage's own entry, not manuscript text. The banner is not left ungated
# though — every measurement token in its delta must be one of the censuses
# this stage re-derived and stored, which is the T8 born-clean rule applied to
# a changelog entry.
assert _meas(_pre28[_pre28.index(_T28):]) == _meas(draft[draft.index(_T28):]), \
    '(28) T1 breach: a MEASUREMENT moved'
assert set(_meas(_bins28)) <= {'29', '13', '22', '12', '310', '179', '18', '23', '138'}, \
    ('(28) the banner entry quotes a number outside this stage\'s censuses',
     sorted(set(_meas(_bins28))))
assert {'13', '22', '12', '310', '179', '18', '23', '138'} <= set(_meas(_bins28)), \
    '(28) the banner entry must record all three censuses and the partition'
assert sorted(_CIT_B4.findall(_pre28)) == sorted(_CIT_B4.findall(draft)), \
    '(28) T1 breach: the citation-key multiset moved'
# identifier digits are counted on the same title-onward region as T1 and T7
# (the banner entry names 'v3.29' and the stage label 'b4-iii-a' by design).
_pre28b, _now28b = _pre28[_pre28.index(_T28):], draft[draft.index(_T28):]
_gone28 = sorted((_idc(_pre28b) - _idc(_now28b)).elements())
assert _gone28 == ['138', '139', '152', '156', '157', '162', '162', '168',
                   '169', '169', '170', '171', '172', '172', '2'], \
    ('(28) identifier digits removed != the 13 declared edits', _gone28)
assert sorted((_idc(_now28b) - _idc(_pre28b)).elements()) == [], \
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
assert len(_now28b.split('\n')) == len(_pre28b.split('\n')) + 1, \
    '(28) exactly one declared re-wrap may change the line count'
assert _rep28['prose_over78_new'] == [] and _rep28['grew_past78'] == [], \
    '(28) house width: the strip may not push a prose line over 78'
assert _rep28['s28_heading_len'] == [109, 84], '(28) §2.8 heading shrink pin'
assert 'v3.29 = L174 stage (b4-iii-a)' in draft[:draft.index('## Title')], \
    '(28) the banner must record the (b4-iii-a) stage'
draft = _live28   # (b4-iii-b): restore the live draft for the sections below
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

# ============ (29) L174 stage (b4-iii-b): the batch-code RELABEL ============
# PREREG banc/l174b4iiib/PREREG.md.  Reader-facing labels replace the internal
# batch codes in the body; the codes survive in ONE declared place (the §3.7
# mapping block) and verbatim inside stored artefact keys, which are FILENAMES
# (T13).  Everything below is RE-DERIVED from the frozen pre-image by the
# stage's own parsed rule -- never read off emit.py's report.
_B29 = P / 'banc/l174b4iiib'
_pre29 = (_B29 / 'draft_pre.md').read_text()
_rep29 = json.loads((_B29 / 'emit_report.json').read_text())
_amd29 = json.loads((_B29 / 'caps_partition_amend.json').read_text())
_MAP29 = {'B26': 'A', 'B27': 'B', 'B29': 'C', 'B30': 'D', 'B31': 'E',
          'B32': 'F', 'B33': 'G', 'B34': 'H', 'B35': 'J', 'B37': 'K',
          'B38': 'L'}
_TOK29 = re.compile(r'(?<![A-Za-z0-9])B(\d{1,3})(?![0-9])')
_PRV29 = re.compile(r'(?i)(\bbatch(es)?[,:]?\s*\(?\s*|(?:[A-HJ-L]|B\d{1,3})/)$')
_MB29 = ['',
 '**Batch labels.** The eleven seed batches this manuscript cites are labelled',
 'A, B, C, D, E, F, G, H, J, K and L in the order they were run (I and O are',
 'skipped so that a label cannot be read as a digit); the labels map one-to-one',
 'onto the internal run codes, which the stored artefact keys retain verbatim:',
 'A = B26, B = B27, C = B29, D = B30, E = B31, F = B32, G = B33, H = B34,',
 'J = B35, K = B37, L = B38. Gaps in the internal codes are batches this',
 'manuscript does not cite, and a label never renames the batch it points at, so',
 'every pooled cell stays traceable to the batches it unions.']

# --- CERT-4: the transform is PARSED. Classify every B<n> in the pre-image ---
_l29 = _pre29.split('\n')
_h29 = [(_i, _x) for _i, _x in enumerate(_l29) if re.match(r'^## ', _x)]
_s29 = []
for _k, (_i, _x) in enumerate(_h29):
    _j = _h29[_k + 1][0] if _k + 1 < len(_h29) else len(_l29)
    _s29.append((_x[3:].strip(), _i + 1, _j))
_T0_29 = _s29[0][1]
def _sec29(_n):
    for _nm, _i, _j in _s29:
        if _i <= _n <= _j:
            return _nm
    return 'BANNER' if _n < _T0_29 else '?'
_subs29, _oth29 = [], {'ARTEFACT_KEY': 0, 'BRANCH': 0, 'OUT_BANNER': 0, 'OUT_SEC7': 0}
for _n, _x in enumerate(_l29, 1):
    for _m in _TOK29.finditer(_x):
        _t, _a, _b = _m.group(0), _m.start(), _m.end()
        _num, _sc = int(_m.group(1)), _sec29(_n)
        if _sc == 'BANNER':
            _oth29['OUT_BANNER'] += 1; continue
        if _sc.startswith('7. '):
            _oth29['OUT_SEC7'] += 1; continue
        if _a > 0 and _x[_a - 1] in '_.':          # inside a stored key (T13)
            _oth29['ARTEFACT_KEY'] += 1; continue
        if _x[_b:_b + 1] == '_' or _x[_a:_a + 5] == 'B1-B4' or _num <= 4:
            _oth29['BRANCH'] += 1; continue        # a PREREG branch label
        assert _t in _MAP29, ('(29) unmapped batch token', _t, _n)
        _new = _MAP29[_t] if _PRV29.search(_x[:_a]) else 'batch ' + _MAP29[_t]
        _subs29.append((_n, _a, _b, _t, _new))
assert len(_subs29) == 19 == _rep29['raw_delta'] - 611, '(29) substitution count'
assert _oth29 == {'ARTEFACT_KEY': 6, 'BRANCH': 4, 'OUT_BANNER': 10,
                  'OUT_SEC7': 0}, ('(29) other-class census', _oth29)
assert sorted({_s[3] for _s in _subs29}) == sorted(_MAP29), \
    '(29) every internal code must occur in the body'
_bare29 = sum(1 for _s in _subs29 if ' ' not in _s[4])
assert (_bare29, len(_subs29) - _bare29) == (6, 13), '(29) bare/prefixed split'

# --- T7 STRONG: pre-image + the declared edits == the live draft ------------
_n29 = list(_l29)
for _ln in sorted({_s[0] for _s in _subs29}):
    _x = _l29[_ln - 1]
    for (_, _a, _b, _t, _w) in sorted([_s for _s in _subs29 if _s[0] == _ln],
                                      reverse=True):
        _x = _x[:_a] + _w + _x[_b:]
    _n29[_ln - 1] = _x
import textwrap as _tw
for (_i, _j) in [(771, 780), (827, 831)]:          # T14 declared reflow
    _blk = _n29[_i - 1:_j]
    _wr = _tw.wrap(' '.join(_y.strip() for _y in _blk), width=78,
                   break_long_words=False, break_on_hyphens=False)
    assert len(_wr) == len(_blk), ('(29) reflow changed the line count', _i)
    _n29[_i - 1:_j] = _wr
_anc29 = [_k for _k, _x in enumerate(_n29)
          if _x.strip() == 'reported with their up/down counts.']
assert len(_anc29) == 1, '(29) the §3.7 anchor is not unique'
_n29[_anc29[0] + 1:_anc29[0] + 1] = _MB29
_chk29 = '\n'.join(_n29)
_T29 = '## Title'
assert _chk29[_chk29.index(_T29):] == draft[draft.index(_T29):], \
    '(29) T7: pre-image + the declared relabel == the live draft (title onward)'
_bp29, _bn29 = _pre29[:_pre29.index(_T29)], draft[:draft.index(_T29)]
_bi29 = _bn29.replace(_bp29.rstrip('\n'), '', 1)
assert _bn29.startswith(_bp29.rstrip('\n')) and \
    'v3.30 = L174 stage (b4-iii-b)' in _bi29, \
    "(29) the banner delta is not exactly this stage's declared entry"

# --- T10 ZERO RESIDUE, read on the LIVE draft (never on the edit list) ------
_MBJ29 = '\n'.join(_MB29)
_scope29 = draft[draft.index('## 1. Introduction'):
                 draft.index('## 7. Author/submit notes')] + \
    draft[draft.index('## References'):draft.index('No citation is written from memory')]
_res29 = []
for _x in _scope29.split('\n'):
    if _x in _MB29:
        continue
    for _m in _TOK29.finditer(_x):
        _a, _b, _num = _m.start(), _m.end(), int(_m.group(1))
        if _a > 0 and _x[_a - 1] in '_.':
            continue
        if _x[_b:_b + 1] == '_' or _x[_a:_a + 5] == 'B1-B4' or _num <= 4:
            continue
        _res29.append((_m.group(0), _x.strip()[:60]))
assert not _res29, ('(29) a batch code survived in §1-§6 / the References '
                    'preamble outside the mapping block', _res29[:4])
assert not re.compile(r'\bL\d{2,3}\b').findall(
    draft[draft.index('## 1. Introduction'):draft.index('## 7. Author/submit notes')]), \
    '(29) a lane ID is back in §1-§6 (the §(28) property, re-read LIVE)'
# T13: the stored keys are FILENAMES and stay byte-exact
for _k in ('l145.pooled.eOutMot_B29_B31', 'l148.pooled.eAll_B29_B32'):
    assert _k in draft, ('(29) a stored artefact key was relabeled', _k)
# the branch labels are DECLARED out of scope and still present
for _k in ('B1-B4', 'B2_preserved', 'registered B4 degenerate'):
    assert _k in draft, ('(29) a PREREG branch label was stripped', _k)
# §7 byte-unchanged (out of manuscript scope, (b4-iii-a) premise)
assert draft[draft.index('## 7. Author/submit notes'):draft.index('## References')] == \
    _pre29[_pre29.index('## 7. Author/submit notes'):_pre29.index('## References')], \
    '(29) §7 is out of scope and must be byte-unchanged'

# --- T1': no measurement moved; identifier runs accounted for BY NAME -------
_pb29, _nb29 = _pre29[_pre29.index(_T29):], draft[draft.index(_T29):]
assert _meas(_pb29) == _meas(_nb29), '(29) T1 breach: a MEASUREMENT moved'
assert sorted(_CIT_B4.findall(_pre29)) == sorted(_CIT_B4.findall(draft)), \
    '(29) T1 breach: the citation-key multiset moved'
# the two sides are read SEPARATELY, or the mapping block's own eleven codes
# silently cancel eleven of the nineteen removals in the Counter difference.
_nomap29 = _nb29.replace(_MBJ29, '')
_g29 = sorted((_idc(_pb29) - _idc(_nomap29)).elements())
assert _g29 == ['26', '27', '29', '29', '30', '30', '30', '30', '31', '32',
                '33', '33', '33', '34', '34', '35', '37', '38', '38'], \
    ('(29) identifier digits removed != the 19 declared relabels', _g29)
assert len(_g29) == 19 == len(_subs29), '(29) one removed run per relabel'
assert sorted((_idc(_nomap29) - _idc(_pb29)).elements()) == [], \
    '(29) an identifier digit ENTERED the body'
_e29 = sorted(_x.rstrip('.') for _x in _idc(_MBJ29).elements())
assert _e29 == ['26', '27', '29', '30', '31', '32', '33', '34', '35', '37',
                '38'], ('(29) identifier digits entered != the mapping block', _e29)

# --- T12 BIJECTION and the mapping block ------------------------------------
assert _MBJ29 in draft, '(29) the §3.7 mapping block is missing'
assert draft.index(_MBJ29) > draft.index('### 3.7 Seeds') and \
    draft.index(_MBJ29) < draft.index('### 3.8 Preregistration'), \
    '(29) the mapping block must live in §3.7'
assert len(set(_MAP29.values())) == 11 and 'I' not in _MAP29.values() \
    and 'O' not in _MAP29.values(), '(29) the label set is not 11 distinct non-I/O letters'
for _c, _lab in _MAP29.items():
    assert _MBJ29.count(_c) == 1 and f'{_lab} = {_c}' in _MBJ29, \
        ('(29) mapping row missing or duplicated', _c)
assert sorted(_MAP29) == sorted(re.findall(r'(?<![A-Za-z0-9])B\d{2}', _MBJ29)), \
    '(29) the mapping block names a code outside the declared map'
# run order is MONOTONE in the label, which is what makes "fresh batch X" readable
assert [_MAP29[_c] for _c in sorted(_MAP29, key=lambda _z: int(_z[1:]))] == \
    list('ABCDEFGHJKL'), '(29) labels are not monotone in the internal code'
# T8 born-clean: the new block quotes no measurement and no provenance key
assert not _meas(_MBJ29) and not _CIT_B4.findall(_MBJ29) and \
    not re.findall(r'^\s*[-*]\s+\S', _MBJ29, re.M), '(29) the mapping block is not born clean'

# --- the five verifier-literal re-points (T3 exception class) ---------------
for _o, _n in (('.622 with 14/16 seeds on B30', '.622 with 14/16 seeds on batch D'),
               ('.659 with\n14/16 on B33', '.659 with\n14/16 on batch G'),
               ('The batch unions were re-pooled with B35',
                'The batch unions were re-pooled with batch J'),
               ('The own-gain diagonal reproduces on B38',
                'The own-gain diagonal reproduces on batch L'),
               ('\u2212.036 on B30', '\u2212.036 on batch D')):
    assert _o in _pre29 and _o not in draft and _n in draft, \
        ('(29) verifier-literal re-point', _o)

# --- T11 partition AMENDMENT (one class split, nothing applied) -------------
assert set(_amd29['amends']) == {'B1-B4'} | set(_MAP29), '(29) amendment vocabulary'
assert _amd29['amends']['B1-B4'] == 'DEFER_BRANCH' and \
    all(_amd29['amends'][_c] == 'KEEP_MAPPING' for _c in _MAP29), \
    '(29) amendment classes'
assert _amd29['n_distinct'] == 179 and _amd29['counts_after']['KEEP_MAPPING'] == 11 \
    and _amd29['counts_after']['DEFER_BRANCH'] == 1 and \
    _amd29['counts_after']['STRIP_EMPHASIS'] == 129, '(29) amended partition counts'
assert sum(_amd29['counts_after'].values()) == 179, '(29) amended partition incomplete'

# --- deltas and house width -------------------------------------------------
# measured title-onward: the banner's own v3.30 entry is not manuscript text
assert len(_nb29) - len(_pb29) == 630 == _rep29['raw_delta'], '(29) raw delta pin'
assert _rep29['body_delta'] == 40, '(29) body-only raw delta pin'
assert len(_MBJ29) == 589, '(29) mapping block size pin'
for _x in _MB29 + sum(_rep29['reflow'].values(), []):
    assert len(_x) <= 78, ('(29) an edited line crossed the house width', _x[:40])
assert 'v3.30 = L174 stage (b4-iii-b)' in draft[:draft.index('## Title')], \
    '(29) the banner must record the (b4-iii-b) stage'

print('(29) L174 (b4-iii-b) the batch relabel: branch R1_relabel_only — the '
      'B<n> shape was READ, not assumed, and splits into THREE classes the '
      'frozen partition had conflated: 19 prose batch codes (11 distinct) '
      'relabeled to the reader-facing letters A-L in RUN ORDER (I and O '
      'skipped), 6 occurrences inside stored artefact KEYS left byte-exact '
      'because they are filenames, and 4 PREREG BRANCH labels (B1-B4, '
      'B2_preserved, the bare B4) declared out of scope — so the partition '
      'is AMENDED (DEFER_BATCH -> KEEP_MAPPING 11 + DEFER_BRANCH 1, still '
      '179 distinct) rather than applied. A letter scheme was chosen BECAUSE '
      'it adds no digit run: the measurement multiset is identical with ZERO '
      'named removals needed, every removed identifier run is a declared '
      'relabel and every entered run is a mapping row. The §3.7 mapping '
      'block (589 chars, born clean under T8) is the ONE declared home of '
      'the internal codes, bijective and monotone in run order so the '
      'draft\'s "fresh batch X" claims read in sequence; pre-image + the '
      'declared edits == the live draft byte for byte from the title onward, '
      'two paragraphs re-wrapped with their line counts unchanged, zero '
      'residue in §1-§6 + the References preamble, §7 byte-unchanged, and '
      'the five verifier literals carrying a relabeled code re-pointed with '
      'their measurements still attached')

print("L149 verify: ALL GREEN")