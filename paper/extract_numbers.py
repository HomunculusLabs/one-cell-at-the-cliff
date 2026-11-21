#!/usr/bin/env python3
"""L140: extract every headline number for the preprint DRAFT from stored
results jsons ONLY (L44 rule — never from log prose). Writes numbers.json with
per-value provenance; prints a compact quote-table."""
import json, os

B = os.path.expanduser('~/critters/peabrain-lab/banc')
OUT = {}
def put(key, val, src):
    OUT[key] = {'v': val, 'src': src}

# ---- Fig-1 dose table (consolidated, independently re-summed by l136) ----
p = json.load(open(f'{B}/l136/plot_data.json'))
put('subnet', p['banc_subnet'], 'l136/plot_data.json:banc_subnet')
put('n_runs_summed', len(p['pooled']['full']['mean_R_runs']),
    'l136/plot_data.json:pooled.full.mean_R_runs (count)')
for arm in p['pooled']:
    c = p['pooled'][arm]
    put(f'pooled.{arm}', dict(k=c['k'], n=c['n'], p_hat=round(c['p_hat'],4),
        lb=round(c['lb'],4), ub=round(c['ub'],4)),
        f'l136/plot_data.json:pooled.{arm}')
put('xor', p['xor'], 'l136/plot_data.json:xor')
if 'dose_l135' in p: put('dose_l135', p['dose_l135'], 'l136/plot_data.json:dose_l135')

# ---- gain-ensemble robustness (L139) ----
r = json.load(open(f'{B}/l139/results_l139.json'))
for arm, c in r['sustain'].items():
    put(f'sustain.{arm}', dict(frac=c['frac'], n=c['n'], prior=c['prior'],
        classes=c['classes']), 'l139/results_l139.json:sustain.'+arm)
g_full = [round(r['gains'][s]['full'],4) for s in sorted(r['gains'])]
put('gains.full.spread', g_full, 'l139/results_l139.json:gains.*.full')
put('jitter_note', r['jitter_note'], 'l139/results_l139.json:jitter_note')
put('full_kR_sets', r['full_kR'], 'l139/results_l139.json:full_kR')

# ---- identity XOR pooled (L135 rebases) ----
q = json.load(open(f'{B}/l135/results_l135.json'))
def find_pooled(d, path=''):
    out = {}
    for k, v in d.items():
        if k == 'pooled': out[path+k] = v
        elif isinstance(v, dict): out.update(find_pooled(v, path+k+'.'))
    return out
for path, v in find_pooled(q).items():
    keep = {a: dict(k=c.get('k'), n=c.get('n'),
                    lb=round(c['lb'],4), ub=round(c['ub'],4))
            for a, c in v.items() if isinstance(c, dict) and 'lb' in c}
    if keep: put('l135.'+path, keep, 'l135/results_l135.json:'+path)

# ---- cross-connectome boundary (L138) ----
s = json.load(open(f'{B}/l138/static.json'))
put('l138.banc', s['banc'], 'l138/static.json:banc')
put('l138.male_s2_dnp33', s['male_s2_dnp33'], 'l138/static.json:male_s2_dnp33')
put('l138.male_s1', s['male_s1'], 'l138/static.json:male_s1')

# ---- mechanism: two-factor law, activity vs edges (L141 = l137 run) ----
m = json.load(open(f'{B}/l137/results_l137.json'))
put('l137.g1', dict(
    sil1110=dict(meanR=m['g1']['sil1110']['meanR'], kR=m['g1']['sil1110']['kR'],
                 paired_dR=m['g1']['sil1110']['legs']['mean_paired_dR'],
                 in_full_band=m['g1']['sil1110']['in_band']),
    census_x_mean=round(m['census']['sil1110']['x_mean'], 3),
    dm_mm_max=round(m['dm']['sil1110']['dm_mm_max'], 4),
    b_wiring=m['g1']['b_wiring']), 'l137/results_l137.json:g1+dm+census')
put('l137.g2', dict(vol1110_dR=m['g2']['vol1110']['legs']['mean_paired_dR'],
                    volrand_dR=m['g2']['volrand']['legs']['mean_paired_dR'],
                    direction=m['g2']['direction']),
    'l137/results_l137.json:g2')
put('l137.g3', dict(silrand_meanR=m['g3']['silrand_meanR'],
                    spread=m['g3']['spread']), 'l137/results_l137.json:g3')
put('l137.sil24', dict(meanR=m['sil24']['meanR'], kR=m['sil24']['kR'],
                       partial=m['sil24']['partial'],
                       meanL=m['sil24']['meanL'], kL=m['sil24']['kL'],
                       dR=m['sil24']['legs']['mean_paired_dR'],
                       cutwA_l135_b26=m['sil24']['cutwA_l135_b26']),
    'l137/results_l137.json:sil24')
put('l137.pooled_full', dict(k=m['pooled_full']['k192'], n=192,
    p_hat=round(m['pooled_full']['p_hat'], 3),
    lb=round(m['pooled_full']['lb'], 4), ub=round(m['pooled_full']['ub'], 4)),
    'l137/results_l137.json:pooled_full')
put('l137.vol1110', dict(meanR=m['table']['Ti']['vol1110']['meanR'],
                         kR=m['table']['Ti']['vol1110']['kR'],
                         meanL=m['table']['Ti']['vol1110']['meanL'],
                         kL=m['table']['Ti']['vol1110']['kL']),
    'l137/results_l137.json:table.Ti.vol1110')  # L152: grid figure row

# ---- mechanism: edge-footprint ladder (L142) ----
e = json.load(open(f'{B}/l142/results_l142.json'))
ti = e['table']['Ti']
put('l142.ti', {a: dict(kL=c['kL'], kR=c['kR'], meanL=c['meanL'],
    meanR=c['meanR']) for a, c in ti.items()}, 'l142/results_l142.json:table.Ti')
put('l142.h2a', e['hypotheses']['H2a'], 'l142/results_l142.json:hypotheses.H2a')
put('l142.h2b', e['hypotheses']['H2b'], 'l142/results_l142.json:hypotheses.H2b')
put('l142.h3', e['hypotheses']['H3'], 'l142/results_l142.json:hypotheses.H3')
put('l142.aeall', dict(a_eall_max=e['anchors']['a_eall_max'],
    g_eAll=e['anchors']['g_eAll'], g_cutng25=e['anchors']['g_cutng25'],
    gains_equal=e['anchors']['g_eall_vs_g25']['equal'],
    e_edges=e['anchors']['e_edges']),
    'l142/results_l142.json:anchors')
put('l142.pooled', e['pooled'], 'l142/results_l142.json:pooled')
put('l142.window', dict(n_wA=e['static']['window']['n_wA'],
    n_edges=e['static']['window']['n_edges_wA']),
    'l142/results_l142.json:static.window')

# ---- L149 fold: substrate-gated clamp (L144), dose footprint (L145),
# release floor (L146), grid close (L148) ----
c = json.load(open(f'{B}/l144/results_l144.json'))
put('l144.silw', dict(meanR=c['classes']['silW']['meanR'], kR=c['classes']['silW']['kR'],
    dR_vs_wA=c['classes']['silW']['legs']['mean_paired_dR_vs_wA'],
    n_up=c['classes']['silW']['legs']['n_up_vs_wA'],
    n_down=c['classes']['silW']['legs']['n_down_vs_wA']),
    'l144/results_l144.json:classes.silW')
put('l144.silf', dict(meanR=c['classes']['silF']['meanR'], kR=c['classes']['silF']['kR'],
    dR_vs_full=c['classes']['silF']['legs']['mean_paired_dR_vs_full']),
    'l144/results_l144.json:classes.silF')

d = json.load(open(f'{B}/l145/results_l145.json'))
hd = d['hypotheses']
put('l145.dose', dict(top5_dR=hd['H_DOSE']['mean_dR_top5'],
    bot5_dR=hd['H_DOSE']['mean_dR_bot5'],
    order_sign_count=hd['H_DOSE']['order_sign_count'],
    top5=dict(meanR=d['table']['Ti']['eMotTop5']['meanR'],
              kR=d['table']['Ti']['eMotTop5']['kR']),
    bot5=dict(meanR=d['table']['Ti']['eMotBot5']['meanR'],
              kR=d['table']['Ti']['eMotBot5']['kR'])),
    'l145/results_l145.json:hypotheses.H_DOSE+table.Ti')
put('l145.mot', dict(meanR=hd['H_REPLIC']['meanR'], kR=hd['H_REPLIC']['kR'],
    dR_vs_wA=d['classes']['mot']['legs']['mean_paired_dR_vs_wA'],
    n_up=d['classes']['mot']['legs']['n_up_vs_wA']),
    'l145/results_l145.json:hypotheses.H_REPLIC+classes.mot')
put('l145.motin', dict(meanR=hd['H_COMBO']['meanR'], kR=hd['H_COMBO']['kR']),
    'l145/results_l145.json:hypotheses.H_COMBO')
put('l145.pooled', d['pooled'], 'l145/results_l145.json:pooled')

e6 = json.load(open(f'{B}/l146/static.json'))
put('l146.release', e6['S0_release'], 'l146/static.json:S0_release')
f4 = e6['S4_ladder']['f4']; det = e6['decision_detail']
put('l146.f4', dict(K=f4['K'], n_glut=f4['n_glut'], n_ng=f4['n_ng'],
    carrier_rank=f4['carrier_rank'], twin_rank=f4['twin_rank'],
    jaccard_heavy=f4['jaccard_heavy'], out80_f4=det['out80_f4'],
    carrier_eq3=e6['S3_carrier']['out80']['eq3'],
    closure_edges_f4=f4['closure_edges'],
    closure_edges_base=e6['S4_ladder']['base']['closure_edges'],
    d4a=det['d4a'], d4b=det['d4b'],
    f2f3_deleted=dict(all_f2=e6['S1_substrate']['deleted']['all_f2'],
                      all_f3=e6['S1_substrate']['deleted']['all_f3'])),
    'l146/static.json:S4_ladder.f4+decision_detail+S3_carrier')

g = json.load(open(f'{B}/l148/results_l148.json'))
put('l148.h_id', dict(bit_identical=g['hypotheses']['H_ID']['bit_identical'],
    max_abs_diff=g['hypotheses']['H_ID']['max_abs_diff'],
    n_keys=g['hypotheses']['H_ID']['n_keys'],
    n_seeds=g['hypotheses']['H_ID']['n_seeds']),
    'l148/results_l148.json:hypotheses.H_ID')
put('l148.seid', g['seid_all_max'], 'l148/results_l148.json:seid_all_max')
put('l148.eall', dict(meanR=g['classes']['eAll']['meanR'], kR=g['classes']['eAll']['kR'],
    dR_vs_wA=g['classes']['eAll']['legs']['mean_paired_dR_vs_wA'],
    n_up=g['classes']['eAll']['legs']['n_up_vs_wA']),
    'l148/results_l148.json:classes.eAll')
put('l148.pooled', g['pooled'], 'l148/results_l148.json:pooled')

# ---- L151 fold: substrate-gate statics (static redundancy REFUTED, crossed
# ---- pathway named; observation label) ----
h = json.load(open(f'{B}/l151/static.json'))
s0 = h['s1_sheet']['G0_closure']; s1_ = h['s1_sheet']['G1_cutwA']
put('l151.sheet', dict(
    m1110=s0['m1110'], ng58_others_G0=s0['m_ng58_others'],
    ng58_others_G1=s1_['m_ng58_others'],
    share_1110_of_DNsheet_G0=round(s0['share_1110_of_DNsheet'], 4),
    share_1110_of_DNsheet_G1=round(s1_['share_1110_of_DNsheet'], 4),
    redundancy_ratio_G0=round(s0['redundancy_ratio'], 3),
    redundancy_ratio_G1=round(s1_['redundancy_ratio'], 3)),
    'l151/static.json:s1_sheet')
tfr = h['s2_pools']['G0_closure']['Ti_fR']; tfl = h['s2_pools']['G0_closure']['Ti_fL']
put('l151.crossed', dict(
    ti_fR_twohop_share=round(tfr['twohop_share'], 5),
    ti_fL_twohop_dn_total=tfl['twohop_dn_total'],
    ti_fL_sheet_edges='zero (no T70->Ti_fL edge exists)',
    intermediary='gi75494 IN06B033 left, cut-invariant dn_in 30.86, carries all five R-side pools',
    pools_R_shared=['Ti_fR', 'Tr_fR', 'Ta_aR', 'Sr_bR', 'Pr_bR']),
    'l151/static.json:s2_pools+followup_named_intermediaries')
put('l151.verdict', h['verdict'], 'l151/static.json:verdict')

# ---- L153 fold: silW batch rebase + eMot halves second batch (L150) ----
w = json.load(open(f'{B}/l150/results_l150.json'))
h1w = w['hypotheses']['H1_silW']
put('l150.h1', dict(b33_class=h1w['b33_class'], meanR=h1w['meanR'],
    kR=h1w['kR'], paired_dR_vs_wA=h1w['paired_dR_vs_wA'],
    n_up_vs_wA=h1w['n_up_vs_wA'],
    b30_meanR=h1w['b30_ctx']['meanR'],
    b30_dR=h1w['b30_ctx']['paired_dR_vs_wA']),
    'l150/results_l150.json:hypotheses.H1_silW')
put('l150.pooled', w['pooled'], 'l150/results_l150.json:pooled')

# ---- L155 fold: Sapkal signed-direction negative (L154 dynamic arms) ----
# Means RECOMPUTED from the stored per-seed duty07 tables (never log prose).
r = json.load(open(f'{B}/l154/results_l154.json'))
def _s07_means(tbl):
    out = {}
    for pool in ('Ti', 'Tr'):
        for side in ('L', 'R'):
            vals = [v[f'S07_{side}'] for v in tbl[pool].values()]
            out[f'{pool}_{side}'] = round(sum(vals) / len(vals), 4)
    return out
m_on, m_off = (_s07_means({'Ti': r['duty07_Ti']['b65'], 'Tr': r['duty07_Tr']['b65']}),
               _s07_means({'Ti': r['duty07_Ti']['off'], 'Tr': r['duty07_Tr']['off']}))
put('l154.freq', dict(n_pos=r['n_pos'], n_neg=r['n_neg'],
    p=round(r['p_two_sided'], 4), direction_met=r['direction_met'],
    anchor_801_on=round(r['anchors']['801']['b65'], 4),
    anchor_801_off=round(r['anchors']['801']['off'], 4),
    anchor_901_on=round(r['anchors']['901']['b65'], 4),
    anchor_901_off=round(r['anchors']['901']['off'], 4)),
    'l154/results_l154.json:sign test + anchors')
put('l154.structure', dict(S07_on=m_on, S07_off=m_off,
    duty_asym_Ti_on=round(r['duty07_asym_Ti_mean']['b65'], 4),
    duty_asym_Ti_off=round(r['duty07_asym_Ti_mean']['off'], 4)),
    'l154/results_l154.json:duty07 tables (recomputed means)')
put('l154.band', dict(
    below_band_on=r['below_band_census']['on'],
    below_band_off=r['below_band_census']['off'],
    dom_full_on=round(r['dom_full_mean']['b65'], 4),
    dom_full_off=round(r['dom_full_mean']['off'], 4),
    posthoc=r['posthoc_untrunc_paired_sign']),
    'l154/results_l154.json:band census + posthoc label')

# L156 fold: sub-band slow-line census (static, PREREG + ADDENDUM 1 first)
import statistics
_l156 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', 'banc', 'l156', 'static.json')))
_p, _r = _l156['pooled'], _l156['rows']
def _med_below(arm):
    vals = [v['f_glob'] for f in _r for a, d in _r[f].items() if a == arm
            for v in d.values() if v['below']]
    return round(statistics.median(vals), 4)
def _bin_below(arm, seeds):
    return sum(_r['l154/raw_l154.npz'][arm][str(s)]['below_bin'] for s in seeds)
put('l156.pooled', dict(
    b65=dict(n=_p['b65_nonjitter']['n'], below=_p['b65_nonjitter']['below'],
             files=_p['b65_nonjitter']['files'],
             lb=round(_p['b65_nonjitter']['wilson_lb'], 4),
             survive=_p['b65_nonjitter']['survive'],
             agree=_p['b65_nonjitter']['agree'],
             med_f_below=_med_below('b65')),
    full=dict(n=_p['full_nonjitter']['n'], below=_p['full_nonjitter']['below'],
              files=_p['full_nonjitter']['files'],
              lb=round(_p['full_nonjitter']['wilson_lb'], 4),
              survive=_p['full_nonjitter']['survive'],
              agree=_p['full_nonjitter']['agree'],
              med_f_below=_med_below('full')),
    cert_bin_below_l154_B34=dict(on=_bin_below('b65', range(3401, 3417)),
                                 off=_bin_below('off', range(3401, 3417))),
    boundary_seed=3401),
    'banc/l156/static.json:pooled + rows (PREREG ADDENDUM 1: stored l154 '
    'census = un-interpolated bin argmax; seed 3401 bin 0.3 vs interp .298253)')

_l157 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', 'banc', 'l157', 'static.json')))
_q = _l157['pooled']
POOLS20 = [k for k in _q if k not in ('mm', 'xm')]
put('l157.pooled', dict(
    mm=dict(n=_q['mm']['n'], below=_q['mm']['below'],
            lb=round(_q['mm']['wilson_lb'], 4)),
    xm=dict(n=_q['xm']['n'], below=_q['xm']['below'],
            lb=round(_q['xm']['wilson_lb'], 4)),
    pools={k: dict(below=_q[k]['below'],
                   lb=round(_q[k]['wilson_lb'], 4)) for k in POOLS20},
    n_pools_lb_ge_056=sum(1 for k in POOLS20 if _q[k]['wilson_lb'] >= .56),
    n_pools_lb_ge_05=sum(1 for k in POOLS20 if _q[k]['wilson_lb'] >= .5),
    ti_max_below=max(_q[k]['below'] for k in POOLS20 if k.startswith('Ti')),
    pr_max_below=max(_q[k]['below'] for k in POOLS20 if k.startswith('Pr')),
    pr_max_lb=round(max(_q[k]['wilson_lb'] for k in POOLS20
                        if k.startswith('Pr')), 4),
    strong_med=round(statistics.median([_q[k]['med_f_below'] for k in POOLS20
                                        if _q[k]['wilson_lb'] >= .56]), 4),
    claim_class=_l157['claim_class'], files=2),
    'banc/l157/static.json:pooled (PREREG + ADDENDUM 1: l150 seed pin '
    '3365-3380 re-derived from npz; per-pool carrier census B33+B34)')

# ---- scramble control family (L168: carrier-free mass-matched cohorts) ----
_l168 = json.load(open(f'{B}/l168/static.json'))
_p168 = _l168['pool']
put('l168.scr', {a: dict(
        n=c['n'], n_batches=c['n_batches'],
        kR=c['kR'], lbR=round(c['lbR'], 4), ubR=round(c['ubR'], 4),
        kL=c['kL'], lbL=round(c['lbL'], 4), ubL=round(c['ubL'], 4),
        mass=_l168['mass'][a], extra=_l168['extra_mass'][a])
     for a, c in _p168.items()},
    'banc/l168/static.json:pool+mass+extra_mass (l168_pools.py, re-derived '
    'from l125/l127/l128 results_*.json:table.Ti; CERT-1..4 green)')
_b168 = _l168['base_full_48']
put('l168.base', dict(n=_b168['n'], kR=_b168['kR'], kL=_b168['kL'],
    lbR=round(_b168['lbR'], 4), ubR=round(_b168['ubR'], 4),
    lbL=round(_b168['lbL'], 4), ubL=round(_b168['ubL'], 4)),
    'banc/l168/static.json:base_full_48 (untreated `full` arm, same 3 batches)')
put('l168.window_mass', dict(k29=_l168['window_mass_k29'],
    scr0=_l168['mass']['cutscr0'],
    gap=_l168['mass_gap_scr0_vs_k29']),
    'banc/l168/static.json:window_mass_k29 + mass.cutscr0 + gap')
put('l168.verdict', _l168['verdict'],
    'banc/l168/static.json:verdict (PREREG decision rule D1/D2/D3)')

# ---- L169: pre-posting control (a), the GAIN-SWAP 2x2 (B35, n=16) ----
_l169 = json.load(open(f'{B}/l169/results_l169.json'))
put('l169.grid', {k: dict(arm=v['arm'], gain=v['gain'], meanR=v['meanR'],
                          kR=v['kR'], lbR=round(v['lbR'], 4),
                          ubR=round(v['ubR'], 4), cls=v['cls'])
                  for k, v in _l169['grid'].items()},
    'banc/l169/results_l169.json:grid (graph x gain 2x2, B35 n=16 each)')
put('l169.swap_legs', {a: dict(
        dR_vs_wA=_l169['cls'][a]['legs']['mean_paired_dR_vs_wA'],
        n_up_vs_wA=_l169['cls'][a]['legs']['n_up_vs_wA'],
        dR_vs_ng25=_l169['cls'][a]['legs']['mean_paired_dR_vs_ng25'])
    for a in ('wAgN', 'n25gW')},
    'banc/l169/results_l169.json:cls.{wAgN,n25gW}.legs (paired, same batch)')
put('l169.branch', _l169['branch'],
    'banc/l169/results_l169.json:branch (PREREG D1/D2/D3)')
put('l169.af', dict(target=_l169['p4']['af_target'],
                    mean={a: _l169['p4']['af_mean'][a]
                          for a in ('cutwA', 'wAgN', 'cutng25', 'n25gW')},
                    mismatch=_l169['p4']['af_mismatch'],
                    paf_per_seed_ok=sum(
                        1 for d in _l169['paf'].values()
                        if d['wAgN_above'] and d['n25gW_below']),
                    paf_n=len(_l169['paf'])),
    'banc/l169/results_l169.json:p4.af_mean/af_mismatch + paf (P-af direction)')
put('l169.pooled', {a: dict(kR=v['kR'], n=v['n'], lbR=round(v['lbR'], 4),
                            ubR=round(v['ubR'], 4), meanR=v['meanR'])
                    for a, v in _l169['pooled'].items()},
    'banc/l169/results_l169.json:pooled (batch unions incl B35)')
put('l169.nt', dict(min=round(min(_l169['nt'].values()), 4),
                    n=len(_l169['nt'])),
    'banc/l169/results_l169.json:nt (C0-NT swap-vs-own-gain mm separation)')

# ---- L169 stage (b1): frozen-vs-rederived floor forms (static) ----
_l169b = json.load(open(f'{B}/l169b/static.json'))
_fm = _l169b['forms']
_tv = _l169b['pins']['P2_cohort_turnover']
put('l169b.forms', dict(
        F1_frozen_all={k: _fm['F1_frozen_all'][k]
                       for k in ('K', 'carrier_rank', 'twin_rank')},
        F2_frozen_set_reordered={k: _fm['F2_frozen_set_reordered'][k]
                                 for k in ('K', 'carrier_rank', 'twin_rank')},
        F3_fully_rederived={k: _fm['F3_fully_rederived'][k]
                            for k in ('K', 'carrier_rank', 'twin_rank')},
        turnover=dict(K_base=_tv['K_base'], K_f4=_tv['K_f4'],
                      left_n=_tv['left_n'], entered_n=_tv['entered_n'],
                      jaccard_heavy=_tv['jaccard_heavy'])),
    'banc/l169b/static.json:forms + pins.P2_cohort_turnover (l169b_static.py, '
    'additive transform of l146_static.py; CERT-1/2/3 green)')
_p3, _p4 = _l169b['pins']['P3_window_portability'], _l169b['pins']['P4_twin_design']
put('l169b.scope', dict(
        verdict=_l169b['verdict'],
        cohort_rederived_inside_fn=_l169b['code_audit'][
            'cohort_rederived_inside_fn'],
        dynamic_f4_run=True,
        window_overlap_f4=_p3['base_window_overlap_f4'],
        f4_xor=_p3['f4_xor_forms'],
        f4_twin=dict(name=_p4['nearest'][0]['name'],
                     rank=_p4['nearest'][0]['rank'],
                     gap=_p4['nearest'][0]['gap'])),
    'banc/l169b/static.json:verdict + code_audit + pins.P3/P4 (PREREG '
    'l169b/PREREG.md rule E1/E2/E3); dynamic_f4_run flipped False->True by '
    'L169 stage (b2) — the ONLY pre-existing key this fold changes')

# ---- L169 stage (b2): the floor-4 DYNAMIC arm (rollouts, B36 n=16) ----
_l169b2 = json.load(open(f'{B}/l169b2/results_l169b2.json'))
_t2 = _l169b2['table']
put('l169b2.dyn', dict(
        branch=_l169b2['branch'],
        batch=_l169b2['batch'], n=_l169b2['n_seeds'],
        floor=_l169b2['floor'], K4=_l169b2['K4'],
        gains={k: round(v, 9) for k, v in _l169b2['gains'].items()},
        f4wA=dict(meanR=_t2['f4wA']['meanR'], kR=_t2['f4wA']['kR'],
                  ubR=_t2['f4wA']['ubR']),
        f4ng=dict(meanR=_t2['f4ng']['meanR'], kR=_t2['f4ng']['kR'],
                  ubR=_t2['f4ng']['ubR']),
        f4tw=dict(meanR=_t2['f4tw']['meanR'], kR=_t2['f4tw']['kR'],
                  ubR=_t2['f4tw']['ubR']),
        base_same_batch=dict(
            cutwA=dict(meanR=_t2['cutwA']['meanR'], kR=_t2['cutwA']['kR']),
            cutng25=dict(meanR=_t2['cutng25']['meanR'],
                         kR=_t2['cutng25']['kR']),
            full=dict(meanR=_t2['full']['meanR'], kR=_t2['full']['kR'])),
        xor_leg=_l169b2['legs']['xor'],
        fc169_max=_l169b2['cert']['fc169_max'],
        ntf4_min=_l169b2['cert']['ntf4_min'],
        stairs=_l169b2['f4_stairs']),
    'banc/l169b2/results_l169b2.json:branch + table + legs + cert '
    '(PREREG l169b2/PREREG.md, branches G1-G4 registered pre-run; '
    'CERT-0 + CERT-METRIC green)')
_ad = _l169b2['addendum_L_descriptive']
put('l169b2.lat_descriptive', dict(
        label='DESCRIPTIVE post-hoc (registered axis is R-side)',
        meanL={a: _ad['rows'][a]['meanL'] for a in
               ('f4wA', 'f4ng', 'f4tw', 'cutwA', 'cutng25')},
        kL={a: _ad['rows'][a]['kL'] for a in
            ('f4wA', 'f4ng', 'f4tw', 'cutwA', 'cutng25')},
        paired=_ad['paired_legs'], side_dominance=_ad['side_dominance']),
    'banc/l169b2/results_l169b2.json:addendum_L_descriptive rows + paired_legs '
    '(l169b2_addendum.py; post-hoc, carries no registered claim)')

_l169c = json.load(open(f'{B}/l169c/static.json'))
put('l169c.design', dict(
        rules=_l169c['rules']['C1_label'] + '/' + _l169c['rules']['C2_label']
        + ('/C3_admissible' if _l169c['rules']['C3_admissible'] else
           '/C3_inadmissible'),
        carrier=dict(out_edges=_l169c['P3_footprint']['carrier_G1']['out_edges'],
                     out_mass=round(_l169c['P3_footprint']['carrier_G1']
                                    ['out_mass'], 2)),
        hom=dict(gi=_l169c['P2_hom_identity']['identity']['gi'],
                 out_edges=_l169c['P3_footprint']['hom_G1']['out_edges'],
                 out_mass=round(_l169c['P3_footprint']['hom_G1']
                                ['out_mass'], 2),
                 pure_proj=_l169c['P2_hom_identity']['membership']['pure_proj'],
                 in_cut_window25=_l169c['P2_hom_identity']['membership']
                 ['in_cut_window25']),
        overlap=dict(shared=_l169c['P4_overlap']['n_shared'],
                     jaccard=round(_l169c['P4_overlap']['jaccard'], 4)),
        rewire=dict(partner_over_carrier=round(
            _l169c['P5_rewire_pool']['partner_over_carrier'], 1),
            med_relocated=_l169c['P6_rewire_draws']['med_relocated'],
            med_mass_T70_share=round(
                _l169c['P6_rewire_draws']['med_mass_T70_share'], 4))),
    'banc/l169c/static.json:rules + P3_footprint + P4_overlap + P5/P6 '
    '(PREREG l169c/PREREG.md, rules C1-C3 registered pre-computation; '
    'CERT-1 re-derives l151 s1/s2/s3 EXACT)')

# ---- L169 stage (c2): the REW + HOM rollout arms (B37, n=16 per arm) ----
_l169c2 = json.load(open(f'{B}/l169c2/results_l169c2.json'))
_t3 = _l169c2['table']


def _cell3(a):
    return dict(meanR=_t3[a]['meanR'], kR=_t3[a]['kR'],
                lbR=round(_t3[a]['lbR'], 4), ubR=round(_t3[a]['ubR'], 4),
                meanL=_t3[a]['meanL'], kL=_t3[a]['kL'],
                g=round(_t3[a]['g'], 9) if _t3[a]['g'] is not None else None,
                super=_t3[a]['super'], notsuper=_t3[a]['notsuper'])


put('l169c2.base', dict(batch=_l169c2['batch'], n=_l169c2['n_seeds'],
                        cutwA=_cell3('cutwA'), cutng25=_cell3('cutng25'),
                        full=_cell3('full'),
                        vacuous_base_guard=_l169c2['vacuous_base_guard']),
    'banc/l169c2/results_l169c2.json:table (same-batch base reproduction)')
put('l169c2.rew', dict(
        rew1=_cell3('rew1'), rew2=_cell3('rew2'), rew3=_cell3('rew3'),
        legs={a: _l169c2['legs'][a] for a in ('rew1', 'rew2', 'rew3')},
        pooled=dict(kR=_l169c2['pooled_rew']['kR'],
                    n=_l169c2['pooled_rew']['n'],
                    lb=round(_l169c2['pooled_rew']['lb'], 4),
                    ub=round(_l169c2['pooled_rew']['ub'], 4),
                    note=_l169c2['pooled_rew']['note']),
        base_bounds={k: [round(v[0], 4), round(v[1], 4)]
                     for k, v in _l169c2['base_bounds'].items()}),
    'banc/l169c2/results_l169c2.json:table + legs + pooled_rew '
    '(3 registered rewire draws, one batch each)')
put('l169c2.branch', dict(rew=_l169c2['rew_branch'],
                          hom=_l169c2['hom_branch'],
                          n_super_rew=_l169c2['n_super_rew'],
                          n_notsuper_rew=_l169c2['n_notsuper_rew'],
                          r1=_l169c2['r1'], r2=_l169c2['r2']),
    'banc/l169c2/results_l169c2.json:rew_branch/hom_branch '
    '(PREREG l169c2/PREREG.md, R1-R3 + H1-H2 registered pre-run)')
put('l169c2.gains', {a: round(v, 9) for a, v in _l169c2['gains'].items()},
    'banc/l169c2/results_l169c2.json:gains (fresh af-matched bisect per arm)')
put('l169c2.hom', dict(cell=_cell3('hom'), leg=_l169c2['legs']['hom'],
                       incident=_l169c2['cert']['hom_incident'],
                       n=_l169c2['c2_n']['hom'],
                       edges=_l169c2['c2_edges']['hom']),
    'banc/l169c2/results_l169c2.json:table.hom + legs.hom + cert '
    '(same-footprint different-class deletion)')
put('l169c2.cert', dict(fc169b2_max=_l169c2['cert']['fc169b2_max'],
                        ntc2_min=round(_l169c2['cert']['ntc2_min'], 4),
                        cert0=_l169c2['cert0'],
                        gains_distinct=_l169c2['cert']['c2_gains_distinct'],
                        stairs=_l169c2['c2_stairs'],
                        rew_draws_first5=_l169c2['rew_draws_first5']),
    'banc/l169c2/results_l169c2.json:cert + c2_stairs + rew_draws_first5 '
    '(CERT-1 forward chain, CERT-REW vs l169c static, C0-NT(c2))')

# ---- L169 stage (d): the XOR-pair gain-swap 2x2 (B38, n=16 per arm) ----
_l169d = json.load(open(f'{B}/l169d/results_l169d.json'))
_t4 = _l169d['table']


def _cell4(a):
    return dict(meanR=_t4[a]['meanR'], kR=_t4[a]['kR'],
                lbR=round(_t4[a]['lbR'], 4), ubR=round(_t4[a]['ubR'], 4),
                meanL=_t4[a]['meanL'], kL=_t4[a]['kL'],
                g=round(_t4[a]['g'], 9) if _t4[a]['g'] is not None else None,
                super=_t4[a]['super'], partial=_t4[a]['partial'],
                notsuper=_t4[a]['notsuper'])


put('l169d.grid', dict(batch=_l169d['batch'], n=_l169d['n_seeds'],
                       cutng25=_cell4('cutng25'),
                       cutng25p=_cell4('cutng25p'),
                       p25gN=_cell4('p25gN'), n25gP=_cell4('n25gP'),
                       cutwA=_cell4('cutwA'), full=_cell4('full'),
                       swap_gain_span_pct=_l169d['swap_gain_span_pct']),
    'banc/l169d/results_l169d.json:table (XOR pair x {own gain, other '
    "arm's gain}, fresh batch B38, paired noise)")
put('l169d.legs', _l169d['legs'],
    'banc/l169d/results_l169d.json:legs (paired per-seed dR within B38)')
put('l169d.branch', dict(branch=_l169d['branch'], e0=_l169d['e0'],
                         e1=_l169d['e1'], e2=_l169d['e2'],
                         xor_reproduced=_l169d['xor_reproduced']),
    'banc/l169d/results_l169d.json:branch '
    '(PREREG l169d/PREREG.md, E0-E3 registered pre-run with precedence)')
put('l169d.xbatch', dict(xbatch=_l169d['xbatch'], note=_l169d['xbatch_note']),
    'banc/l169d/results_l169d.json:xbatch (B38 vs the stored B25 cells of '
    'l135/results_l135.json:table.Ti)')
put('l169d.cert', dict(fc169c2_max=_l169d['cert']['fc169c2_max'],
                       c0a150_max=_l169d['cert']['c0a150_max'],
                       ntd_min=round(_l169d['cert']['ntd_min'], 4),
                       cert0=_l169d['cert0'],
                       g_cutng25p_exact=_l169d['cert']['g_cutng25p_exact'],
                       d_stair=_l169d['d_stair'],
                       pafd_ok=_l169d['pafd_ok'],
                       pafd_nup=_l169d['pafd_nup'],
                       pafd_ndn=_l169d['pafd_ndn']),
    'banc/l169d/results_l169d.json:cert (CERT-1 FC-169C2 16 arms, CERT-2 '
    'C0A-150 extended to cutng25p vs raw_l135, CERT-3 stored bisects, '
    'C0-NT(d), P-af direction)')

# ---- L170: the male extraction at the MATCHED synapse floor (static) ----
_l170 = json.load(open(f'{B}/l170/static.json'))
_L1, _L3 = _l170['ladder']['1'], _l170['ladder']['3']
put('l170.matched', dict(
    floor1=dict(dn_new=_L1['s1']['dn_new'], dn_new_ng=_L1['s1']['dn_new_ng'],
                K=_L1['s1']['heavy_K'], window=_L1['window'],
                dn_into=_L1['dn_into'], edges=_L1['edges_kept']),
    floor3=dict(dn_new=_L3['s1']['dn_new'], dn_new_ng=_L3['s1']['dn_new_ng'],
                K=_L3['s1']['heavy_K'], window=_L3['window'],
                dn_into=_L3['dn_into'], edges=_L3['edges_kept']),
    banc_window=_l170['banc_window'], banc_K=_l170['banc_K'],
    dnp33_in_cord=dict(
        floor1=[c['in_cord_edges'] for c in _L1['dnp33']],
        floor3=[c['in_cord_edges'] for c in _L3['dnp33']],
        in_cohort_floor3=[c['in_cohort'] for c in _L3['dnp33']]),
    branch=_l170['verdict']['branch'], rel_change=_l170['verdict']['rel_change'],
    M3_dnp33_pure=_l170['verdict']['M3_dnp33_pure'],
    P1=_l170['verdict']['P1'], P2=_l170['verdict']['P2'],
    release_floor=_l170['precheck']['w_min'],
    dup_pairs=_l170['precheck']['dup_pairs']),
    'banc/l170/static.json:ladder + verdict + precheck (PREREG '
    'banc/l170/PREREG.md, M1/M2/M3 registered pre-run; floor-1 arm '
    'CERT-equal to the stored l138 male side)')
put('l170.pins', dict(
    rank25=_L3['pins']['rank25'], rank26=_L3['pins']['rank26'],
    twin_gap=_L3['pins']['twin_gap'], ng_top10=_L3['pins']['ng_top10'],
    ladder_dn_new={k: _l170['ladder'][k]['s1']['dn_new'] for k in ('1', '2', '3', '4')},
    ladder_K={k: _l170['ladder'][k]['s1']['heavy_K'] for k in ('1', '2', '3', '4')}),
    'banc/l170/static.json:ladder.3.pins + the floor ladder 1-4 '
    '(design pins for a future dynamic walk; NOT a dynamic result)')


# ---- L171: slow-line re-attribution + robustness panel (zero rollouts) --
_l171 = json.load(open(f'{B}/l171/results.json'))
_e = _l171['envelope']
put('l171.envelope', dict(
    bin_hz=_e['bin_hz'], dom_bin=_e['dom_bin'], dom_hz=_e['dom_hz'],
    bin6_rank=_e['bin6_rank'], bin6_local_max=_e['bin6_local_max'],
    top5_hz=_e['top5_hz'], chop_fundamental_hz=_e['chop_fundamental_hz'],
    chop_bin_exact=_e['chop_bin_exact'], gap_centers_s=_e['gap_centers_s'],
    vs_bin6=_e['vs_bin6'], vs_chop=_e['vs_chop'],
    n_off_gaps=_e['n_off_gaps'], branch=_l171['a_branch']),
    'banc/l171/results.json:envelope (the drive envelope AMPA rebuilt '
    'from banc/l135_run.py and FFT-ed on its own; PREREG banc/l171/'
    'PREREG.md branch A1 registered pre-run)')
put('l171.panel', dict(
    n=_l171['n_seeds'], seeds=[_l171['seeds'][0], _l171['seeds'][-1]],
    published=dict(
        kR=_l171['panel']['q07_published']['cutng25']['kR'],
        meanR=_l171['panel']['q07_published']['cutng25']['meanR'],
        twin_kR=_l171['panel']['q07_published']['cutng25p']['kR'],
        twin_meanR=_l171['panel']['q07_published']['cutng25p']['meanR'],
        d_meanR=_l171['pub_contrast'], d_kR=_l171['pub_d_kR']),
    fast_seg=dict(
        kR=_l171['panel']['fast_seg_1p4']['cutng25']['kR'],
        meanR=_l171['panel']['fast_seg_1p4']['cutng25']['meanR'],
        twin_kR=_l171['panel']['fast_seg_1p4']['cutng25p']['kR'],
        twin_meanR=_l171['panel']['fast_seg_1p4']['cutng25p']['meanR'],
        **{k: _l171['panel']['fast_seg_1p4']['contrast'][k]
           for k in ('d_meanR', 'd_kR', 'paired_up', 'paired_down')}),
    highpass=dict(
        kR=_l171['panel']['highpass_0p3']['cutng25']['kR'],
        meanR=_l171['panel']['highpass_0p3']['cutng25']['meanR'],
        twin_kR=_l171['panel']['highpass_0p3']['cutng25p']['kR'],
        twin_meanR=_l171['panel']['highpass_0p3']['cutng25p']['meanR'],
        **{k: _l171['panel']['highpass_0p3']['contrast'][k]
           for k in ('d_meanR', 'd_kR', 'paired_up', 'paired_down')}),
    branch=_l171['b_branch']),
    'banc/l171/results.json:panel (stored B26 traces re-scored; the '
    'published q07 cells reproduced EXACT first, CERT P1/P2)')


# ---- L172 stage (a): the statistics pass (zero rollouts) ----------------
# ONE pooled count per arm: the maximal unique-seed union over every
# admissible stored batch (admissibility rule A in banc/l172/PREREG.md:
# identical constant block parsed from each run script, matching stored
# gain, jittered-gain sets excluded as different networks, seeds deduped).
_l172 = json.load(open(f'{B}/l172/stats.json'))
_pool = _l172['pooled']
put('l172.pooled', {a: dict(
    n=_pool[a]['n'], kR=_pool[a]['kR'], kL=_pool[a]['kL'],
    lbR=_pool[a]['lbR'], ubR=_pool[a]['ubR'],
    meanR=round(_pool[a]['meanR'], 3),
    bootR=[round(_pool[a]['bootR'][0], 3), round(_pool[a]['bootR'][1], 3)],
    n_files=_pool[a]['n_files'], dup_seeds=_pool[a]['dup_seeds'])
    for a in sorted(_pool)},
    'banc/l172/stats.json:pooled (canonical unique-seed union per arm; '
    'CERT-1 l156 census cells + CERT-2/3 four stored per-batch duty cells '
    'reproduced EXACTLY before any pooled number was read)')
put('l172.diffs', {k: dict(
    ka=v['ka'], na=v['na'], kb=v['kb'], nb=v['nb'],
    diff=round(v['diff'], 3), lo=round(v['lo'], 3), hi=round(v['hi'], 3),
    fisher_p=v['fisher_p'], contains_zero=v['contains_zero'])
    for k, v in _l172['diffs'].items()},
    'banc/l172/stats.json:diffs (Newcombe hybrid-score CI for the '
    'difference of two independent proportions + two-sided Fisher exact, '
    'computed on the canonical pooled counts)')
put('l172.census_unique', dict(
    b65=dict(below=_l172['census_unique']['b65']['below'],
             n=_l172['census_unique']['b65']['n'],
             lb=_l172['census_unique']['b65']['lb'],
             dupes=_l172['census_unique']['b65']['dupes']),
    closure=dict(below=_l172['census_unique']['full']['below'],
                 n=_l172['census_unique']['full']['n'],
                 lb=_l172['census_unique']['full']['lb'],
                 dupes=_l172['census_unique']['full']['dupes']),
    trace_forms=_l172['census_unique']['stored_trace_forms'],
    dup_inconsistent=_l172['census_unique']['dup_inconsistent_total']),
    'banc/l172/stats.json:census_unique (the l156 slow-line census '
    'de-duplicated to unique seeds; forward-chain anchor re-rolls are '
    'repeat observations of the same seed, 0 inconsistencies)')
put('l172.meta', dict(
    n_admissible=_l172['admissibility']['n_admissible'],
    n_rejected=len(_l172['admissibility']['rejected']),
    n_recurring_seeds=_l172['p1_n_recurring'],
    dup_inconsistent=len(_l172['s3_dup_inconsistent']),
    sham_n=_l172['sham']['n'], sham_spread=_l172['sham']['spread'],
    unit=_l172['unit_of_inference'], branch=_l172['branch_dup']),
    'banc/l172/stats.json:admissibility+sham+unit (unit of inference = a '
    'noise seed of ONE fixed network)')


# ---------------- L173 (a): Methods constants, PARSED from source -------
_l173 = json.load(open(f'{B}/l173/methods.json'))
put('l173.model', dict(
    TAU=_l173['model']['TAU'], DT=_l173['model']['DT'],
    RMAX=_l173['model']['RMAX'], BG=_l173['model']['BG'],
    NOISE=_l173['model']['NOISE'], SETTLE=_l173['model']['SETTLE'],
    WIN=_l173['model']['WIN'], SEG=_l173['model']['SEG'],
    BETA=_l173['model']['BETA'], AF_T=_l173['model']['AF_T'],
    af_threshold=_l173['model']['af_threshold'],
    equation=_l173['model']['equation'], branch=_l173['model']['branch'],
    eq_maxd=_l173['model']['eq_maxd']),
    'banc/l173/methods.json:model (every constant parsed by ast from '
    'banc/l135_run.py and asserted identical in banc/l169d_run.py; the '
    'equation certified against the run script\'s own three update lines '
    'by a deterministic 7-node probe, max|d| = 0.0)')
put('l173.protocol', dict(
    chop_on=_l173['protocol']['chop_on'], chop_off=_l173['protocol']['chop_off'],
    chop_period=_l173['protocol']['chop_period'],
    dng100_drive=_l173['protocol']['dng100_drive'],
    bisect_iters=_l173['protocol']['bisect_iters'],
    bisect_bracket=_l173['protocol']['bisect_bracket'],
    win_s=_l173['protocol']['win_s']),
    'banc/l173/methods.json:protocol (chop geometry + the DNg100 tonic '
    'drive + the gain-bisect schedule, parsed from banc/l135_run.py)')
put('l173.defs', dict(
    K=_l173['defs']['K'], mass_share=_l173['defs']['mass_share'],
    n_glut=_l173['defs']['n_glut'], n_nonglut=_l173['defs']['n_nonglut'],
    duty_bar=_l173['defs']['duty_bar'], seed_bar=_l173['defs']['seed_bar'],
    s_window=_l173['defs']['s_window'],
    sample_stride=_l173['defs']['sample_stride'],
    super_meanR=_l173['defs']['super_meanR'],
    super_k=_l173['defs']['super_k'],
    partial_lo=_l173['defs']['partial_lo'],
    partial_hi=_l173['defs']['partial_hi'],
    notsuper_k=_l173['defs']['notsuper_k']),
    'banc/l173/methods.json:defs (cohort/ladder rule parsed from '
    'banc/l131_static.py + duty and class criteria parsed from '
    'banc/l169d_verdict.py, both re-asserted against stored pins)')

_l173b = json.load(open(f'{B}/l173b/cert.json'))
put('l173b.gains', dict(
    g_base=_l173b['cert1']['g_cutwA'],
    silW_exact_equal=_l173b['cert1']['exact_equal'],
    pct=_l173b['cert2']['pct'], flip_band=_l173b['cert2']['flip_band'],
    flip_arms=_l173b['cert2']['flip_arms'],
    nonflip_arms=_l173b['cert2']['nonflip_arms'],
    mass_ratio=_l173b['cert5']['ratio'],
    sham_spread=_l173b['cert4']['spread_max_minus_min'],
    carrier_intact_dR=_l173b['cert4']['carrier_intact_dR'],
    branch=_l173b['branch']),
    'banc/l173b/cert.json:cert1+cert2+cert4+cert5 (every gain read from a '
    'stored anchors.g_* field; percent deltas re-derived at full precision; '
    'silW == its base gain as EXACT float equality in both batches; the '
    'mass ratio .0544/.005599 recomputed, retiring the printed 12x)')


# ---- L183 master fold (additive block; every pre-existing key above is ----
# ---- byte-identical): the single-cell scan (l175), the timing analysis ----
# ---- (l184), the replication / gain null / signed-current twin (l185), ----
# ---- the gate-jitter discriminator (l186), the relay / push-pull arms  ----
# ---- (l187), the paired twin inference (l172 per-seed), the substrate  ----
# ---- census (l92) and the weight rule PARSED from the run source.      ----
import csv as _csv183, re as _re183, math as _m183

def _rank183(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r

def _spear183(a, b):
    ra, rb = _rank183(a), _rank183(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** .5
    return num / den

_r175 = json.load(open(f'{B}/l175/results_l175.json'))
assert _r175['status'] == 'FINAL'
_gb175 = _r175['base']['gain']
def _arm175(a):
    d = dict(kR=a['kR'], kL=a['kL'], n=a['n'], meanR=a['meanR'],
             meanL=a['meanL'], lbR=a['lbR'], ubR=a['ubR'], cls=a['cls'],
             gain_pct=round(100 * a['gain_delta_vs_wA'] / _gb175, 2))
    if a.get('gi') is not None:
        d.update(rank=a['rank'], gi=a['gi'], cell_type=a['cell_type'],
                 side=a['side'], sign=a['eff_sign'],
                 x_mean=round(a['x_mean'], 4), out_mass=round(a['out_mass'], 5),
                 drive_ratio=round(a['drive_ratio_to_carrier'], 3),
                 active=a['active'])
    return d
_scan175 = {'cutwA': _arm175(_r175['base'])}
for _a in _r175['window']:
    _scan175[_a['arm']] = _arm175(_a)
for _k in ('dmA', 'dmC'):
    _scan175[_k] = _arm175(_r175['twins'][_k])
put('l175.scan', _scan175,
    'banc/l175/results_l175.json:base + window[34] + twins (re-keyed by arm '
    'name; gain_pct = 100 x gain_delta_vs_wA / base gain; x_mean, out_mass '
    'and drive_ratio rounded for display, counts and duties as stored)')
_win175 = [a for a in _r175['window']]
_nc175 = [a for a in _win175 if a['arm'] != 'sc25']
_sil175 = [a for a in _nc175 if not a['active']]
_act175 = [a for a in _nc175 if a['active']]
_over175 = [a for a in _act175 if a['drive_ratio_to_carrier'] > 1.0]
_gp175 = lambda a: 100 * a['gain_delta_vs_wA'] / _gb175
put('l175.null', dict(
    n_window=len(_win175), n_noncarrier=len(_nc175),
    n_silent=len(_sil175), n_active_other=len(_act175),
    silent_kR_min=min(a['kR'] for a in _sil175),
    silent_kR_max=max(a['kR'] for a in _sil175),
    silent_meanR_min=min(a['meanR'] for a in _sil175),
    silent_meanR_max=max(a['meanR'] for a in _sil175),
    n_super=sum(a['cls'] == 'SUPER' for a in _win175),
    n_intermediate=sum(a['cls'] == 'INTERMEDIATE' for a in _win175),
    n_not=sum(a['cls'].startswith('NOT-SUPER') for a in _win175),
    active_other_super=sum(a['cls'] == 'SUPER' for a in _act175),
    n_overdrive=len(_over175),
    overdrive_min=round(min(a['drive_ratio_to_carrier'] for a in _over175), 2),
    overdrive_max=round(max(a['drive_ratio_to_carrier'] for a in _over175), 2),
    overdrive_super=sum(a['cls'] == 'SUPER' for a in _over175),
    rho_gain_meanR_noncarrier=round(_spear183(
        [_gp175(a) for a in _nc175], [a['meanR'] for a in _nc175]), 3),
    rho_gain_meanR_silent=round(_spear183(
        [_gp175(a) for a in _sil175], [a['meanR'] for a in _sil175]), 3),
    silent_gain_abs_max=round(max(abs(_gp175(a)) for a in _sil175), 2),
    max_gain_arm=max(_nc175, key=_gp175)['arm'],
    max_gain_pct=round(max(_gp175(a) for a in _nc175), 2)),
    'banc/l175/results_l175.json:window (DERIVED here from the stored per-arm '
    'rows: the silent-cell null range, the class counts, the cells delivering '
    'more than the carrier, and Spearman(re-bisected gain shift, meanR) with '
    'average ranks over the 33 non-carrier arms and over the silent subset)')
_bi175 = _r175['branch_inputs']
put('l175.branch', dict(
    controls_ok=_bi175['controls_ok'], n_window=_bi175['n_window'],
    n_active=_bi175['n_active'], n_active_exc=_bi175['n_active_exc'],
    n_active_inh=_bi175['n_active_inh'], A_n=_bi175['A_n'],
    F_A_frac=_bi175['F_A_frac'], H_n=_bi175['H_n'],
    F_H_frac=_bi175['F_H_frac'], silent_n=_bi175['silent_n'],
    rho_all_drive_meanR=round(_bi175['rho_all_drive_meanR'], 3),
    rho_exc_drive_meanR=round(_bi175['rho_exc_drive_meanR'], 3)),
    'banc/l175/results_l175.json:branch_inputs')
put('l175.verdict', _r175['branch'], 'banc/l175/results_l175.json:branch')
put('l175.bands', dict(_r175['bands']), 'banc/l175/results_l175.json:bands')
put('l175.certs', dict(
    c0a175_checks=_r175['certs']['c0a175_checks'],
    c0a175_max=_r175['certs']['c0a175_max'],
    cert_x_checks=_r175['certs']['cert_x_checks'],
    cert_x_max=_r175['certs']['cert_x_max'],
    cert_g_stored_exact=_r175['certs']['cert_g_stored_exact']),
    'banc/l175/results_l175.json:certs')
_sel175 = _r175['selection']
put('l175.census', dict(
    carrier=dict(gi=_sel175['carrier']['gi'],
                 out_edges=_sel175['carrier']['out_edges'],
                 x_mean=round(_sel175['carrier']['x_mean'], 4),
                 delivered_drive=round(_sel175['carrier']['delivered_drive'], 3)),
    mass_twin_319=dict(gi=_sel175['mass_twin_319']['gi'],
                       out_edges=_sel175['mass_twin_319']['out_edges'],
                       x_mean=round(_sel175['mass_twin_319']['x_mean'], 4),
                       delivered_drive=round(
                           _sel175['mass_twin_319']['delivered_drive'], 3)),
    dmA=dict(pool_n=_sel175['dmA']['pool_n']),
    dmC=dict(pool_n=_sel175['dmC']['pool_n'])),
    'banc/l175/results_l175.json:selection')
put('l175.meta', dict(
    n_seeds=len(_r175['seeds']), seed_lo=min(_r175['seeds']),
    seed_hi=max(_r175['seeds']), n_arms=len(_scan175),
    twin_drive_ratio=round(_sel175['mass_twin_319']['delivered_drive']
                           / _sel175['carrier']['delivered_drive'], 4),
    prereg_sha256=_r175['prereg_sha256'][:16], status=_r175['status']),
    'banc/l175/results_l175.json:seeds + selection + prereg_sha256 (batch '
    'size, seed range, arm count and the mass twin\'s delivered-drive ratio '
    'derived from the stored fields)')

# -- L184: zero-rollout analysis of the stored scan batch (csv artifacts) --
_tp184 = {r['arm']: r for r in _csv183.DictReader(open(f'{B}/l184/threepanel.csv'))}
put('l184.threepanel', {a: dict(
    chopped_k=int(r['chopped_k']), chopped_mean=round(float(r['chopped_mean']), 3),
    fast_k=int(r['fast_k']), fast_mean=round(float(r['fast_mean']), 3),
    cross_k=int(r['cross_k']), cross_mean=round(float(r['cross_mean']), 3))
    for a, r in _tp184.items()},
    'banc/l184/threepanel.csv:one row per arm (chopped 0.7-Hz duty, the '
    'continuous 1.4-Hz segment, and the cross-seed chopped pairing; k = '
    'seeds or ordered pairs with duty >= .5)')
_n184 = len(_r175['seeds'])     # l184 re-scores the stored scan batch
put('l184.design', dict(n_seeds=_n184, n_cross_pairs=_n184 * (_n184 - 1),
                        n_arms=len(_tp184)),
    'banc/l184/threepanel.csv:row count (seed count read from the scan batch '
    'it re-scores, banc/l175/results_l175.json seeds; cross pairs = ordered '
    'i != j pairs of those seeds)')
_q3184 = {r['arm']: r for r in _csv183.DictReader(open(f'{B}/l184/q3.csv'))}
put('l184.q3', {a: {k: round(float(_q3184[a][k]), 5) for k in (
    'flex', 'ext', 'mean_neg_r_same', 'same', 'cross', 'residual',
    'delta_flex', 'delta_ext', 'delta_same', 'delta_cross', 'delta_residual')}
    for a in ('cutwA', 'sc25', 'sc26', 'sc27', 'sc40', 'dmA', 'dmC')},
    'banc/l184/q3.csv:rows cutwA sc25 sc26 sc27 sc40 dmA dmC (same-seed vs '
    'cross-seed duty decomposition; deltas are arm minus base)')
put('l184.q3_ratios', dict(
    cross_over_same_increment=round(float(_q3184['sc25']['delta_cross'])
                                    / float(_q3184['sc25']['delta_same']), 3),
    cross_over_same_level=round(float(_q3184['sc25']['cross'])
                                / float(_q3184['sc25']['same']), 3)),
    'banc/l184/q3.csv:rows sc25 (two ratios DERIVED here: delta_cross / '
    'delta_same, and cross / same within the carrier-removed arm)')
_q1184 = {(r['arm'], r['segment'], r['pool'], r['metric']): float(r['mean'])
          for r in _csv183.DictReader(open(f'{B}/l184/q1.csv'))}
_q1c184 = {(r['ref'], r['segment'], r['pool'], r['metric']): r
           for r in _csv183.DictReader(open(f'{B}/l184/q1-contrasts.csv'))}
def _q1cell(seg, pool, metric):
    c = _q1c184[('cutwA', seg, pool, metric)]
    return dict(base=round(_q1184[('cutwA', seg, pool, metric)], 8),
                sc25=round(_q1184[('sc25', seg, pool, metric)], 8),
                diff=round(float(c['sc25_minus_ref']), 8),
                lo=round(float(c['lo']), 8), hi=round(float(c['hi']), 8))
put('l184.q1', dict(
    chopped=dict(f=dict(amp=_q1cell('chopped', 'f', 'amp'),
                        gate=_q1cell('chopped', 'f', 'gate')),
                 e=dict(amp=_q1cell('chopped', 'e', 'amp'),
                        gate=_q1cell('chopped', 'e', 'gate'))),
    fast=dict(f=dict(amp=_q1cell('fast', 'f', 'amp')),
              e=dict(amp=_q1cell('fast', 'e', 'amp')))),
    'banc/l184/q1.csv:arm means + banc/l184/q1-contrasts.csv rows ref=cutwA '
    '(drive-frequency harmonic amplitude and signed on-off gate contrast per '
    'pool, rate units; paired percentile intervals as stored)')
put('l184.q1_twins', {a: dict(
    f_abs_gate=round(_q1184[(a, 'chopped', 'f', 'abs_gate')], 8),
    e_abs_gate=round(_q1184[(a, 'chopped', 'e', 'abs_gate')], 8))
    for a in ('cutwA', 'sc25', 'sc26', 'dmA', 'dmC')},
    'banc/l184/q1.csv:rows metric=abs_gate segment=chopped (absolute on-off '
    'gate contrast per pool for the base, the carrier-removed arm and the '
    'three scan twins)')
_sn184 = {(r['arm'], r['template']): r
          for r in _csv183.DictReader(open(f'{B}/l184/sensitivity.csv'))}
put('l184.sens', {t: dict(
    d_same=round(float(_sn184[('sc25', t)]['same'])
                 - float(_sn184[('cutwA', t)]['same']), 4),
    d_cross=round(float(_sn184[('sc25', t)]['cross'])
                  - float(_sn184[('cutwA', t)]['cross']), 4))
    for t in ('original', 'minus_gate', 'minus_tone', 'minus_both')},
    'banc/l184/sensitivity.csv:rows sc25 and cutwA (carrier-minus-base duty '
    'after subtracting the fitted gate and/or tone template, DERIVED as the '
    'difference of the two stored rows)')
_ed184 = list(_csv183.DictReader(open(f'{B}/l184/edges.csv')))
_ov184 = {r['arm']: r for r in _csv183.DictReader(open(f'{B}/l184/overlap.csv'))}
put('l184.anatomy', dict(
    n_incident=len(_ed184),
    n_in=sum(r['direction'] == 'in' for r in _ed184),
    n_out=sum(r['direction'] == 'out' for r in _ed184),
    n_out_premotor=sum(r['target_class'] == 'direct right-Ti premotor'
                       for r in _ed184),
    n_out_intrinsic_other=sum(r['target_class'] == 'ventral_nerve_cord_intrinsic'
                              for r in _ed184),
    n_out_other_motor=sum(r['target_class'] == 'other motor' for r in _ed184),
    n_out_intrinsic=sum(r['target_class'] in ('direct right-Ti premotor',
                                              'ventral_nerve_cord_intrinsic')
                        for r in _ed184),
    overlap={a: dict(gi=int(r['gi']), out=int(r['out']), shared=int(r['shared']),
                     direct_premotor=int(r['direct_premotor']),
                     shared_premotor=int(r['shared_premotor']))
             for a, r in _ov184.items()}),
    'banc/l184/edges.csv:all 93 incident edges by direction and target class '
    '+ banc/l184/overlap.csv (targets shared with the carrier, per comparator)')

# -- L185: fresh-batch replication, gain-only null, signed-current twin ----
_r185 = json.load(open(f'{B}/l185/results_l185.json'))
assert _r185['status'] == 'FINAL'
def _cell185(c):
    return dict(kR=c['kR'], kL=c['kL'], n=c['n'], meanR=c['meanR'],
                lbR=c['lbR'], ubR=c['ubR'], cls=c['cls'],
                gain_delta_pct=round(c['gain_delta_pct'], 3))
put('l185.base', _cell185(_r185['base']), 'banc/l185/results_l185.json:base')
put('l185.r1', {a: dict(
    gi=v['gi'], rematched=_cell185(v['rematched']), fixed=_cell185(v['fixed']),
    fixed_minus_rematched={k: v['fixed_minus_rematched'][k]
                           for k in ('mean', 't', 'n_up', 'n_dn')},
    fixed_vs_base_same_gain={k: v['fixed_vs_base_same_gain'][k]
                             for k in ('mean', 't', 'n_up', 'n_dn')},
    pooled_b39_b40_rematched=dict(v['pooled_b39_b40_rematched']))
    for a, v in _r185['R1'].items()},
    'banc/l185/results_l185.json:R1')
_R2 = _r185['R2']
put('l185.r2', dict(
    deltas_pct=_R2['deltas_pct'], kR=_R2['kR'],
    meanR=[round(x, 3) for x in _R2['meanR']],
    slope_meanR_per_0p1pct=round(_R2['slope_meanR_per_0p1pct'], 4),
    slope_se=round(_R2['slope_se'], 4),
    slope_ci95=[round(x, 4) for x in _R2['slope_ci95']],
    slope_kRfrac_per_0p1pct=_R2['slope_kRfrac_per_0p1pct'],
    n_seeds_negative_slope=_R2['n_seeds_negative_slope'],
    label=_R2['label'], gain_alone_super=len(_R2['gain_alone_super']),
    kR_max=max(_R2['kR']), kR_min=min(_R2['kR']),
    span_pct=max(_R2['deltas_pct']) - min(_R2['deltas_pct']),
    scan_comparison=dict(
        within_half_pct=dict(_R2['scan_comparison']['within_half_pct']),
        silent_within_half_pct=dict(
            _R2['scan_comparison']['silent_within_half_pct']))),
    'banc/l185/results_l185.json:R2 (gain-only null on the base graph; '
    'meanR, slope, se and ci rounded for display; gain_alone_super is the '
    'LENGTH of the stored empty list; kR_max, kR_min and span_pct derived '
    'from the stored lists)')
_s2 = _r185['R3']['arm']
put('l185.r3', dict(
    gi=_s2['gi'], cell_type=_s2['cell_type'], side=_s2['side'],
    eff_sign=_s2['eff_sign'], x_mean=round(_s2['x_mean'], 3),
    dist_rel=round(_s2['dist_rel'], 4), drive_ratio=round(_s2['drive_ratio'], 2),
    J=[round(x, 6) for x in _s2['J']],
    carrier_J=[round(x, 6) for x in _s2['carrier_J']],
    kR=_s2['kR'], kL=_s2['kL'], n=_s2['n'], meanR=_s2['meanR'],
    lbR=_s2['lbR'], ubR=_s2['ubR'], dR_vs_wA=_s2['dR_vs_wA'],
    gain_delta_pct=round(_s2['gain_delta_pct'], 3), cls=_s2['cls'],
    pool_n=_r185['R3']['selection']['pool_S_active_n']),
    'banc/l185/results_l185.json:R3.arm + R3.selection.pool_S_active_n (the '
    'signed-current-matched twin; J = registered relayed current onto the '
    'right-tibia flexor and extensor pools)')
put('l185.branches', {k: _r185['branches'][k] for k in
                      ('R1', 'gain_form', 'R2', 'R3', 'D2_hardened')},
    'banc/l185/results_l185.json:branches')
put('l185.certs', {k: _r185['certs'][k] for k in (
    'c0a_vs_raw_l135_checks', 'c0a_vs_l175_raw_checks', 'c0a_max',
    'cert_x_checks', 'cert_x_max', 'cert_g_stored_exact')},
    'banc/l185/results_l185.json:certs')
put('l185.meta', dict(
    n_seeds=len(_r185['seeds']), seed_lo=min(_r185['seeds']),
    seed_hi=max(_r185['seeds']), prereg_sha256=_r185['prereg_sha256'][:16]),
    'banc/l185/results_l185.json:seeds + prereg_sha256 (seed range derived)')

# -- L186: gate-jitter discriminator (16 paired jitter schedules) ----------
_r186 = json.load(open(f'{B}/l186/results_l186.json'))
assert _r186['status'] == 'FINAL'
put('l186.means', {a: {k: round(v, 3) for k, v in d.items()}
                   for a, d in _r186['means'].items()},
    'banc/l186/results_l186.json:means')
put('l186.contrasts', {k: dict(value=round(v['value'], 3),
                               ci95=[round(x, 3) for x in v['ci95']])
                       for k, v in _r186['contrasts'].items()},
    'banc/l186/results_l186.json:contrasts')
put('l186.phase', {k: dict(n=v['n'], degrees=round(v['degrees'], 1),
                           R=round(v['R'], 2))
                   for k, v in _r186['phase'].items()},
    'banc/l186/results_l186.json:phase (pool peak relative to the carrier, '
    'degrees and resultant length rounded for display)')
put('l186.branch', _r186['branch'], 'banc/l186/results_l186.json:branch')
_p186 = json.load(open(f'{B}/l186/t216_power.json'))
put('l186.power', dict(
    jitter_band_steps=_p186['jitter_band_steps'],
    window_steps=_p186['window_steps'],
    mean_window_overlap=round(_p186['mean_window_overlap'], 2),
    frac_pairs_overlap_ge_half=round(_p186['frac_pairs_overlap_ge_half'], 2),
    frac_pairs_disjoint=round(_p186['frac_pairs_disjoint'], 2),
    needed_jitter_for_disjoint_windows=_p186[
        'needed_jitter_for_disjoint_windows'],
    n_seeds=len(_r186['seeds']), n_anchor_checks=_r186['anchors']['n_checks'],
    c0a_max=_r186['anchors']['c0a_max']),
    'banc/l186/t216_power.json:(whole file, the power adjudication of the '
    'registered +-300-step jitter against the 500-step readout window) + '
    'banc/l186/results_l186.json seeds and anchors')

# -- L187: relay silencing / cut, push-pull, occlusion (B41, n = 16) -------
_r187 = json.load(open(f'{B}/l187/results_l187.json'))
assert _r187['status'] == 'FINAL'
def _cell187(c):
    return dict(kR=c['kR'], kL=c['kL'], n=c['n'], meanR=c['meanR'],
                lbR=c['lbR'], ubR=c['ubR'], cls=c['cls'],
                gain_delta_pct=round(c['gain_delta_pct'], 3),
                k14=c['k14'], mean14=c['mean14'],
                x_relay=c['x_relay'], x_74914=c['x_74914'],
                vs_base=dict(mean=round(c['vs_base']['mean'], 3),
                             ci95=[round(x, 3) for x in c['vs_base']['ci95']]))
put('l187.base', _cell187(_r187['base']), 'banc/l187/results_l187.json:base')
put('l187.arms', {a: _cell187(c) for a, c in _r187['arms'].items()},
    'banc/l187/results_l187.json:arms')
put('l187.contrasts', {k: dict(mean=round(v['mean'], 3),
                               ci95=[round(x, 3) for x in v['ci95']],
                               n_up=v['n_up'], n_dn=v['n_dn'])
                       for k, v in _r187['contrasts'].items()},
    'banc/l187/results_l187.json:contrasts')
_rl187 = _r187['relay']
put('l187.relay', dict(
    cell=dict(gi=_rl187['cell']['gi'], cell_type=_rl187['cell']['cell_type'],
              side=_rl187['cell']['side'], eff_sign=_rl187['cell']['eff_sign'],
              super_class=_rl187['cell']['super_class']),
    in_edges=_rl187['in_edges'], out_edges=_rl187['out_edges'],
    carrier_to_relay=dict(syn=_rl187['carrier_to_relay']['syn']),
    sc40_to_relay=dict(syn=_rl187['sc40_to_relay']['syn']),
    pool_sizes={k: v['targets'] for k, v in _rl187['direct_onto'].items()},
    census_x_mean_3seed=round(_rl187['census_x_mean_3seed'], 3),
    sc40_census_x_mean=round(_rl187['sc40_census_x_mean'], 3)),
    'banc/l187/results_l187.json:relay (pool_sizes re-keyed from '
    'direct_onto.*.targets, the motor-neuron count of each tibia pool)')
put('l187.branches', {k: _r187['branches'][k] for k in (
    'header', 'A1', 'A2', 'A2_fixed', 'A2_gain_form', 'relay', 'A3',
    'A3_fixed', 'A4')}, 'banc/l187/results_l187.json:branches')
put('l187.sc40_pooled', {f: {k: _r187['sc40_pooled'][f][k]
                             for k in ('kR', 'n', 'meanR', 'cls')}
                         for f in ('rematched', 'fixed')},
    'banc/l187/results_l187.json:sc40_pooled')
put('l187.sc25_pooled', {f: dict(_r187['sc25_pooled'][f])
                         for f in ('rematched', 'fixed')},
    'banc/l187/results_l187.json:sc25_pooled')
_cs187 = _r187['certs']
put('l187.certs', dict(
    c0a_vs_raw_l135_checks=_cs187['c0a_vs_raw_l135_checks'],
    c0a_max=_cs187['c0a_max'], fc150_checks=_cs187['fc150_checks'],
    fc150_max=_cs187['fc150_max'], cert_silcut_pass=_cs187['cert_silcut_pass'],
    cert_x_checks=_cs187['cert_x_checks'], cert_x_max=_cs187['cert_x_max']),
    'banc/l187/results_l187.json:certs')
_ad187 = json.load(open(f'{B}/l187/addendum.json'))
put('l187.fast', {f"{r['a']}_minus_{r['b']}": dict(
    mean_a=r['mean_a'], mean_b=r['mean_b'], diff=r['diff'], ci95=r['ci95'],
    n_pos=r['n_pos'], n_neg=r['n_neg'])
    for r in _ad187['fast_1p4Hz_paired']},
    'banc/l187/addendum.json:fast_1p4Hz_paired (list re-keyed as a_minus_b; '
    'post hoc and descriptive by the addendum\'s own note)')
put('l187.gain_slopes', {r['graph']: dict(
    carrier_present=r['carrier_present'],
    rematch_shift_pct=r['rematch_shift_pct'],
    rematched_minus_fixed=r['rematched_minus_fixed'], ci95=r['ci95'],
    slope_per_0p1pct=r['slope_per_0p1pct'])
    for r in _ad187['gain_form_slopes']},
    'banc/l187/addendum.json:gain_form_slopes (list re-keyed by graph; post '
    'hoc and descriptive by the addendum\'s own note)')
put('l187.relay_rate', dict(_ad187['relay_rate']),
    'banc/l187/addendum.json:relay_rate')
put('l187.g74914_rate', dict(_ad187['g74914_rate']),
    'banc/l187/addendum.json:g74914_rate')
put('l187.meta', dict(
    n_seeds=len(_r187['seeds']), seed_lo=min(_r187['seeds']),
    seed_hi=max(_r187['seeds']), prereg_sha256=_r187['prereg_sha256'][:16],
    silcut_anchor_seeds=len(_cs187['cert_silcut']),
    silcut_max=max(max(v['head_max'], v['full_max'])
                   for v in _cs187['cert_silcut'].values())),
    'banc/l187/results_l187.json:seeds + certs.cert_silcut (seed range and '
    'the construction-identity certificate: relay clamped from t = 0 versus '
    'relay cut, maximum absolute trace difference over the anchor seeds)')

# -- paired twin inference on the twin's own seeds (referee N6 / r3) -------
_ps172 = _l172['per_seed']
_tw = dict(zip(_ps172['cutng25p']['seeds'], _ps172['cutng25p']['dutyR']))
_bs = dict(zip(_ps172['cutwA']['seeds'], _ps172['cutwA']['dutyR']))
_cm = sorted(set(_tw) & set(_bs))
assert len(_cm) == len(_tw) == 66
_bp = sum(_tw[s] >= .5 and _bs[s] >= .5 for s in _cm)
_bn = sum(_tw[s] < .5 and _bs[s] < .5 for s in _cm)
_to = sum(_tw[s] >= .5 and _bs[s] < .5 for s in _cm)
_bo = sum(_tw[s] < .5 and _bs[s] >= .5 for s in _cm)
_nd = _to + _bo
_pmc = min(1.0, 2 * sum(_m183.comb(_nd, i) for i in range(min(_to, _bo) + 1))
           / 2 ** _nd)
put('l172.paired_twin', dict(
    n=len(_cm), both_pos=_bp, both_neg=_bn, twin_only=_to, base_only=_bo,
    twin_k=_bp + _to, base_k=_bp + _bo, mcnemar_p=round(_pmc, 4),
    mean_duty_diff=round(sum(_tw[s] - _bs[s] for s in _cm) / len(_cm), 3)),
    'banc/l172/stats.json:per_seed (cutng25p vs cutwA on the 66 seeds the '
    'twin ran on; duty >= .5 seed bar; exact two-sided McNemar on the '
    'discordant pairs, DERIVED here)')

# -- substrate census + the weight rule, the latter PARSED from source -----
_s92 = json.load(open(f'{B}/l92/static.json'))
put('l92.substrate', {k: _s92[k] for k in (
    'n_old', 'n_new', 'cord', 'dn_into', 'dn_proj', 'dn_new', 'edges_old',
    'edges_new')},
    'banc/l92/static.json:(top-level fields n_old n_new cord dn_into dn_proj '
    'dn_new edges_old edges_new; asserted equal at run time by '
    'banc/l135_run.py)')
_bg183 = open(f'{B}/build_graph_banc.py').read()
_rs183 = open(f'{B}/l135_run.py').read()
_nt183 = {m.group(1): float(m.group(3)) for m in _re183.finditer(
    r'"(\w+)": \("(\w+)", ([-0-9.]+)\)', _bg183)}
_dflt183 = float(_re183.search(r'NT_CLASS\.get\(n, \("unk", ([0-9.]+)\)\)',
                               _bg183).group(1))
for _need in ('gsign_b2 = np.where(is_glut[gsrc], -np.abs(gsign_a2), gsign_a2)',
              'vals = (np.log1p(gcount) * gsign_b2).astype(np.float32)',
              'vals[neg] *= BETA', '.clamp(max=RMAX) - X[a])',
              'X0o = (BG + NOISE * torch.randn(n_old, 1, generator=gen))'
              '.clamp(0, 1)',
              'cord_cls = np.isin(sup, ["sensory", '
              '"ventral_nerve_cord_intrinsic", "motor"])',
              'keep_new = cord_mask | dn_into | dn_proj'):
    assert _need in _rs183, ('l135 source line drifted', _need)
put('l135.weights', dict(
    signs=_nt183, default_sign=_dflt183, weight_is_signed_log1p_count=True,
    glut_forced_negative=True, beta_on_negatives=True, upper_clamp_only=True,
    init_clip_0_1=True, cord_classes=['sensory', 'ventral_nerve_cord_intrinsic',
                                      'motor'],
    closure_is_cord_plus_dn_into_plus_dn_proj=True),
    'banc/l135_run.py:build() + wb() + the update and init lines (each '
    'asserted present verbatim in the source) with the per-transmitter sign '
    'table parsed from banc/build_graph_banc.py NT_CLASS')

# ---- L183 (late add): the cohort ladder re-scored in the continuously driven
# 1.4-Hz segment.  Source: the per-seed duty rows the second-round referee
# derived from the raw traces (stored with their script,
# paper/review_fable_evidence_r2/p1_duty_from_raw.py), pooled HERE by the
# canonical rule of L172 (admissible files only, first occurrence of each
# seed).  Tie to our own pools: the chopped column of the same rows must
# reproduce l172.pooled kR/n EXACTLY for every arm, or this block refuses.
_r2rows = json.load(open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'review_fable_evidence_r2', 'out_duty_rows.json')))
_adm183 = set(_l172['admissibility']['admissible'])
_Z183 = 1.959963984540054


def _wil183(k, n):
    ph = k / n
    den = 1 + _Z183 * _Z183 / n
    c = (ph + _Z183 * _Z183 / (2 * n)) / den
    h = _Z183 * ((ph * (1 - ph) / n + _Z183 * _Z183 / (4 * n * n)) ** .5) / den
    return round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)


_lad183 = {}
for _arm in ('b65', 'full', 'cutk5', 'cutng19', 'cutng23', 'cutwA', 'cutng25p', 'cutng25',
             'cutng29', 'cut58', 'cutscr0'):
    _seen = {}
    for _r in _r2rows['rows']:
        if _r['arm'] == _arm and _r['file'] in _adm183 and _r['seed'] not in _seen:
            _seen[_r['seed']] = _r
    _v = list(_seen.values())
    _n = len(_v)
    _k07 = sum(1 for x in _v if x['duty07R'] >= .5)
    _k14 = sum(1 for x in _v if x['duty14R'] >= .5)
    _pool = OUT['l172.pooled']['v'][_arm]
    assert (_k07, _n) == (_pool['kR'], _pool['n']), \
        ('referee rows do not reproduce the canonical pool', _arm, _k07, _n)
    _lo, _hi = _wil183(_k14, _n)
    _lad183[_arm] = dict(
        n=_n, chopped_k=_k07,
        chopped_mean=round(sum(x['duty07R'] for x in _v) / _n, 3),
        fast_k=_k14, fast_mean=round(sum(x['duty14R'] for x in _v) / _n, 3),
        fast_lb=_lo, fast_ub=_hi,
        fast_kL=sum(1 for x in _v if x['duty14L'] >= .5))
put('l183.ladder_fast', _lad183,
    '../paper/review_fable_evidence_r2/out_duty_rows.json:rows (per-seed duty '
    'rows derived from the raw traces by the stored script '
    'p1_duty_from_raw.py; pooled HERE by the L172 canonical rule; the chopped '
    'column is asserted equal to l172.pooled kR/n for all eleven arms; '
    'continuous-segment counts and Wilson bounds DERIVED here)')
put('l183.ladder_fast_meta', dict(
    n_windows_chopped=_r2rows['n_windows_q07'],
    n_windows_fast=_r2rows['n_windows_q14'], n_rows=len(_r2rows['rows']),
    n_arms=len(_lad183)),
    '../paper/review_fable_evidence_r2/out_duty_rows.json:n_windows_q07 / '
    'n_windows_q14 / rows (count)')

json.dump(OUT, open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'numbers.json'), 'w'), indent=1, sort_keys=True)

# compact quote table
for k in sorted(OUT):
    v = OUT[k]['v']
    print(f'{k} = {json.dumps(v)[:160]}  <- {OUT[k]["src"]}')
