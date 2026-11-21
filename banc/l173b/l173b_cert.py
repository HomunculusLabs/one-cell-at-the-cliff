#!/usr/bin/env python3
"""L173 stage (b) CERT — run BEFORE any draft line is edited.

PREREG: banc/l173b/PREREG.md (rules T1-T4, CERT-1..6, branches B2 > B1).
ZERO rollouts, zero RNG, no torch. Arithmetic over STORED values only.
Every gain is read from a stored anchors.g_* field (rule T1).
"""
import json, pathlib, sys

P = pathlib.Path('/home/t3rpz/critters/peabrain-lab')
R = lambda rel: json.loads((P / rel).read_text())

r137 = R('banc/l137/results_l137.json')
r142 = R('banc/l142/results_l142.json')
r144 = R('banc/l144/results_l144.json')
r145 = R('banc/l145/results_l145.json')
r148 = R('banc/l148/results_l148.json')
r150 = R('banc/l150/results_l150.json')
s172 = R('banc/l172/stats.json')
out = {'prereg': 'banc/l173b/PREREG.md', 'rollouts': 0}

# ---------------------------------------------------------------- CERT-1
# silW's gain is EXACTLY its base's, in both of its batches, and all five
# files that store g_cutwA agree (rule T3: exact equality, no tolerance).
g_wA = r142['anchors']['g_cutwA']
for tag, src in (('l144', r144), ('l145', r145), ('l148', r148), ('l150', r150)):
    assert src['anchors']['g_cutwA'] == g_wA, f'CERT-1: g_cutwA differs in {tag}'
g_silW_b30 = r144['anchors']['g_sil1110_wA']
g_silW_b33 = r150['anchors']['g_silW']
c1 = (g_silW_b30 == g_wA) and (g_silW_b33 == g_wA)
branch = 'B1_silW_gain_unchanged' if c1 else 'B2_silW_gain_differs'
assert c1, f'CERT-1 FAILED -> branch B2: {g_silW_b30!r} {g_silW_b33!r} vs {g_wA!r}'
out['cert1'] = {'g_cutwA': g_wA, 'g_silW_B30': g_silW_b30,
                'g_silW_B33': g_silW_b33, 'exact_equal': True,
                'files_agreeing_on_base_gain': 5}
out['branch'] = branch

# ---------------------------------------------------------------- CERT-2
# Percent gain deltas vs the base, re-derived at full precision (T2),
# with the flip/non-flip partition taken from the STORED class booleans (P1).
GAINS = {  # arm -> (gain, source json path)
    'cutng25':  (r142['anchors']['g_cutng25'],  'l142:anchors.g_cutng25'),
    'eOutInt':  (r142['anchors']['g_eOutInt'],  'l142:anchors.g_eOutInt'),
    'eIn':      (r142['anchors']['g_eIn'],      'l142:anchors.g_eIn'),
    'eAll':     (r142['anchors']['g_eAll'],     'l142:anchors.g_eAll'),
    'eOutAll':  (r142['anchors']['g_eOutAll'],  'l142:anchors.g_eOutAll'),
    'eMotIn':   (r145['anchors']['g_eMotIn'],   'l145:anchors.g_eMotIn'),
    'eMotTop5': (r145['anchors']['g_eMotTop5'], 'l145:anchors.g_eMotTop5'),
    'eMotBot5': (r145['anchors']['g_eMotBot5'], 'l145:anchors.g_eMotBot5'),
    'eOutMot':  (r145['anchors']['g_eOutMot'],  'l145:anchors.g_eOutMot'),
    'silW':     (g_silW_b33,                    'l150:anchors.g_silW'),
}
pct = {a: (g - g_wA) / g_wA * 100.0 for a, (g, _) in GAINS.items()}

# flip partition from the stored CLASS BOOLEANS of each arm's defining
# ladder run (P1), not from memory. Key spellings differ per file:
# l142 keys the cohort arm as '25'; l145 keys the motor arms top5/bot5/
# mot/motIn. eOutMot is NOT in either partition: its own two batches
# disagree (l142 super False .525/9, l145 'mot' super True .632/12), so
# it is carried as the disclosed INTERMEDIATE arm.
CLS = {'cutng25': r142['classes']['25'], 'eOutInt': r142['classes']['eOutInt'],
       'eIn': r142['classes']['eIn'], 'eAll': r142['classes']['eAll'],
       'eOutAll': r142['classes']['eOutAll'], 'eMotIn': r145['classes']['motIn'],
       'eMotTop5': r145['classes']['top5'], 'eMotBot5': r145['classes']['bot5']}
flips = sorted(a for a, c in CLS.items() if c['super'] is True)
nonflip = sorted(a for a, c in CLS.items() if c['super'] is not True)
assert set(flips) == {'cutng25', 'eOutInt', 'eIn', 'eAll', 'eOutAll', 'eMotIn'}, flips
assert set(nonflip) == {'eMotTop5', 'eMotBot5'}, nonflip
assert r142['classes']['eOutMot']['super'] is False and r145['classes']['mot']['super'] is True
for a in flips:
    assert 1.00 <= pct[a] <= 1.35, f'CERT-2: flip arm {a} delta {pct[a]:.3f}% out of band'
for a in ('eMotTop5', 'eMotBot5'):
    assert abs(pct[a]) <= 0.05, f'CERT-2: non-flip {a} delta {pct[a]:.3f}% out of band'
assert -0.60 <= pct['eOutMot'] <= -0.50, f"CERT-2: eOutMot {pct['eOutMot']:.3f}%"
assert pct['silW'] == 0.0, f"CERT-2: silW delta must be exactly 0, got {pct['silW']!r}"
out['cert2'] = {'g_base': g_wA,
                'pct': {a: round(pct[a], 3) for a in sorted(pct)},
                'flip_arms': flips, 'nonflip_arms': nonflip,
                'flip_band': [round(min(pct[a] for a in flips), 3),
                              round(max(pct[a] for a in flips), 3)],
                'src': {a: s for a, (_, s) in GAINS.items()}}

# ---------------------------------------------------------------- CERT-3
sw, h1 = r144['classes']['silW'], r150['hypotheses']['H1_silW']
assert (r144['table']['Ti']['sil1110_wA']['meanR'], r144['table']['Ti']['sil1110_wA']['kR']) == (0.622, 14)
assert (h1['meanR'], h1['kR']) == (0.659, 14)
assert abs(sw['legs']['mean_paired_dR_vs_wA'] - 0.189) < 5e-4
assert (sw['legs']['n_up_vs_wA'], sw['legs']['n_down_vs_wA']) == (6, 0)
assert abs(h1['paired_dR_vs_wA'] - 0.281) < 5e-4 and h1['n_up_vs_wA'] == 9
pool = s172['pooled']['silW']


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return c - h, c + h


lb, ub = wilson(pool['kR'], pool['n'])
assert (pool['kR'], pool['n']) == (78, 98), pool
assert abs(lb - pool['lbR']) < 1e-9 and abs(ub - pool['ubR']) < 1e-9
dif = s172['diffs']['silW_vs_base']
out['cert3'] = {'b30': [0.622, 14, 0.189, 6, 0], 'b33': [0.659, 14, 0.281, 9],
                'pooled': {'kR': pool['kR'], 'n': pool['n'],
                           'lbR': pool['lbR'], 'ubR': pool['ubR'],
                           'meanR': pool['meanR']},
                'diff_vs_base': {'diff': dif['diff'], 'lo': dif['lo'],
                                 'hi': dif['hi'], 'fisher_p': dif['fisher_p']}}

# ---------------------------------------------------------------- CERT-4
g3, g1 = r137['g3'], r137['g1']
shams = g3['silrand_meanR']
assert shams == [0.429, 0.502, 0.504] and g3['silrand_kR'] == [5, 8, 8]
spread = round(max(shams) - min(shams), 3)
assert spread == g3['spread'] == 0.075, (spread, g3['spread'])
dR_intact = g1['sil1110']['legs']['mean_paired_dR']
assert dR_intact == -0.088
assert abs(dR_intact) > spread, 'CERT-4: the retired sentence would be true?!'
out['cert4'] = {'shams_meanR': shams, 'shams_kR': g3['silrand_kR'],
                'spread_max_minus_min': spread, 'carrier_intact_dR': dR_intact,
                'abs_dR_gt_spread': True, 'n_shams': 3,
                'dm_mm_max_intact_clamp': r137['dm']['sil1110']['dm_mm_max']}

# ---------------------------------------------------------------- CERT-5
h2a = r142['hypotheses']['H2a']
mass_carrier = h2a['mass']
band = 0.0544            # the any-geometry scattered band, §2.1/§2.2 pin
assert abs(mass_carrier - 0.005599) < 1e-9, mass_carrier
ratio = band / mass_carrier
assert round(ratio, 2) == 9.72, ratio
assert abs(ratio - 12) > 0.5, 'CERT-5: 12x is not within rounding of the ratio'
out['cert5'] = {'band': band, 'carrier_mass': mass_carrier,
                'ratio': round(ratio, 2), 'retired_literal': '12x'}

# ---------------------------------------------------------------- CERT-6
s24 = r137['sil24']
base_intact = r137['table']['Ti']['full']
assert (s24['kR'], s24['meanR']) == (5, 0.432)
assert (base_intact['kR'], base_intact['meanR']) == (6, 0.464)
assert (s24['cutwA_l135_b26']['kR'], s24['cutwA_l135_b26']['meanR']) == (5, 0.383)
out['cert6'] = {'sil24': [s24['kR'], s24['meanR']],
                'intact_base_same_batch': [base_intact['kR'], base_intact['meanR']],
                'cut_base_comparator': [s24['cutwA_l135_b26']['kR'],
                                        s24['cutwA_l135_b26']['meanR']],
                'class_label_match_no_separation': True,
                'kL_death': [s24['kL'], s24['meanL']]}

# ---------------------------------------------------------- P2 relocation pins
ae = r142['anchors']
assert ae['g_eall_vs_g25']['equal'] is True and r142['anchors'].get('a_eall_max', None) in (0.0, None)
a_eall = r142.get('anchors', {}).get('a_eall_max')
if a_eall is None:
    a_eall = json.loads((P / 'paper/numbers.json').read_text())['l142.aeall']['v']['a_eall_max']
assert a_eall == 0.0
assert r148['seid_all_max'] == 0.0 and r148['hypotheses']['H_ID']['bit_identical'] is True
out['relocate'] = {'eAll_vs_cutng25_max_abs': a_eall,
                   'g_eAll_eq_g_cutng25': True,
                   'se0_vs_eAll_max_abs': r148['seid_all_max'],
                   'se0_n_keys': r148['hypotheses']['H_ID']['n_keys'],
                   'se0_n_seeds': r148['hypotheses']['H_ID']['n_seeds'],
                   'destination': 'DRAFT.md section 3.8'}

(P / 'banc/l173b/cert.json').write_text(json.dumps(out, indent=1, sort_keys=True))
print('CERT-1 silW gain EXACTLY its base gain, both batches:', g_wA)
print('CERT-2 flip band %+.3f..%+.3f%% | nonflip %+.3f/%+.3f%% | eOutMot %+.3f%% | silW %+.3f%%' % (
    out['cert2']['flip_band'][0], out['cert2']['flip_band'][1],
    pct['eMotTop5'], pct['eMotBot5'], pct['eOutMot'], pct['silW']))
print('CERT-3 silW cells + canonical pool 78/98 [%.3f,%.3f] reproduced' % (lb, ub))
print('CERT-4 shams %s spread %.3f vs carrier dR %.3f -> |dR| > spread' % (shams, spread, dR_intact))
print('CERT-5 mass ratio %.4f -> 9.72x (retires 12x)' % ratio)
print('CERT-6 sil24 5/16 vs intact base 6/16 vs cut base 5/16 = label match, no separation')
print('BRANCH:', branch)
print('ALL CERT GREEN — draft edits unlocked')
