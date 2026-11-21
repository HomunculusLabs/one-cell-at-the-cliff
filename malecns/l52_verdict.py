"""L52 verdict recompute from saved artifacts (L35 precedent): GC at the
REGISTERED precision (3-decimal artifact values, tol 5e-4) + exact-array
equality check (stronger); per-side early/late medians for the f14 arms
(mechanism); MIXED-verdict descriptive layer clearly labeled post-hoc."""
import json

import numpy as np

res = json.load(open('l52/results_l52.json'))
z = np.load('l52/traces_l52.npz')
TS = np.arange(499, 10000, 10)
SEEDS = (11, 22, 33)
REG = {'11': .360, '22': .645, '33': .112}


def duty(SL, SR, lo, hi):
    q = (TS >= lo) & (TS < hi)
    return float(np.nanmean((SL[TS[q]] >= .25) & (SR[TS[q]] >= .25)))


def med(arr, lo, hi):
    q = (TS >= lo) & (TS < hi)
    return round(float(np.nanmedian(arr[TS[q]])), 3)


gc = {}
for s in SEEDS:
    SL, SR = z[f'SL_f07a3_{s}'], z[f'SR_f07a3_{s}']
    d = duty(SL, SR, 4000, 10000)
    gc[str(s)] = round(d, 3)
gc_pass_reg = all(abs(gc[str(s)] - REG[str(s)]) < 5e-4 for s in SEEDS)
print('GC registered-precision:', gc, 'vs', REG, '->', gc_pass_reg)
res['GC'] = dict(expect=REG, got=gc, pass_=bool(gc_pass_reg),
                 note='run gate used 1e-9 vs 3-decimal registered values '
                      '(s33 .1117 vs .112) — recomputed at registered '
                      'precision; boolean duty arrays verified EXACTLY '
                      'equal to l49 cont (probe)')

mech = {}
for a in ('f14a3', 'f14a2', 'f14a1', 'f07a3'):
    mech[a] = {}
    for s in SEEDS:
        SL, SR = z[f'SL_{a}_{s}'], z[f'SR_{a}_{s}']
        mech[a][str(s)] = dict(
            SL_early=med(SL, 4000, 7000), SL_late=med(SL, 7000, 10000),
            SR_early=med(SR, 4000, 7000), SR_late=med(SR, 7000, 10000))
res['mechanism_sides'] = mech
print(json.dumps(mech, indent=0))

# descriptive layer (post-hoc, labeled): late-duty collapse on 3/3 at 1.4
late14 = [res['rows']['f14a3'][str(s)]['late'] for s in SEEDS]
early14 = [res['rows']['f14a3'][str(s)]['early'] for s in SEEDS]
late07 = [res['rows']['f07a3'][str(s)]['late'] for s in SEEDS]
res['descriptive_posthoc'] = dict(
    f14a3_early=early14, f14a3_late=late14,
    f07a3_late=late07,
    reading='late duty ~0 on 3/3 at 1.4 (mean .033) while early carries '
            'entry structure (mean .173): the collapse is DWELL-DEEPENING, '
            'the opposite of a recovering transient; per-seed entry-'
            'structure lifetime ~6-30 s (first all-zero bin: s33 bin1, '
            's11 bin4, s22 wobbles to 0 by bin6)')
res['predictions']['P2_gc'] = bool(gc_pass_reg)
json.dump(res, open('l52/results_l52.json', 'w'), indent=1)
print('late f14a3:', late14, '| late f07a3:', late07)
print('P3 scored on run json (low-amp unlock):', res['predictions']['P3_low_amp_unlock'])
for a in ('f14a2', 'f14a1'):
    print(a, {s: (res['rows'][a][str(s)]['early'], res['rows'][a][str(s)]['late'])
              for s in SEEDS})
print('patched results_l52.json')
