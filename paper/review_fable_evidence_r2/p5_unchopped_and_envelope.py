#!/usr/bin/env python3
"""Round-2 probe 5: (a) the dose ladder re-scored in the UNCHOPPED 1.4-Hz segment
(same S, same .25 bar, same .50 seed bar; windows ending in steps 2500-3999),
canonical lab-admissible unique-seed pools; (b) drive-envelope spectrum."""
import json, os, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'out_duty_rows.json')))
ADM = set(json.load(open('/home/t3rpz/critters/peabrain-lab/banc/l172/stats.json'))['admissibility']['admissible'])
Z = 1.959963984540054
def wil(k, n):
    p = k / n; den = 1 + Z*Z/n; c = (p + Z*Z/(2*n))/den; h = Z*math.sqrt(p*(1-p)/n + Z*Z/(4*n*n))/den
    return max(0, c-h), min(1, c+h)
print('arm        | published 0.7-Hz chopped: kR/n  meanR | UNCHOPPED 1.4-Hz: kR/n [Wilson]  meanR | LEFT unchopped kL/n')
for arm in ['b65', 'full', 'cutk5', 'cutng19', 'cutng23', 'cutwA', 'cutng25p', 'cutng25', 'cutng26', 'cutng29', 'cut58', 'cutscr0', 'cutscr1']:
    seen = {}
    for r in D['rows']:
        if r['arm'] == arm and r['file'] in ADM and r['seed'] not in seen:
            seen[r['seed']] = r
    v = list(seen.values()); n = len(v)
    k07 = sum(x['duty07R'] >= .5 for x in v); k14 = sum(x['duty14R'] >= .5 for x in v); kl = sum(x['duty14L'] >= .5 for x in v)
    lo, hi = wil(k14, n)
    print('%-9s  | %3d/%3d  %.3f | %3d/%3d [%.3f,%.3f]  %.3f | %3d/%3d'
          % (arm, k07, n, np.mean([x['duty07R'] for x in v]), k14, n, lo, hi, np.mean([x['duty14R'] for x in v]), kl, n))
# (b) envelope
amp = np.zeros(6000)
for seg0 in (0, 2000, 4000):
    c = 0
    while seg0 + c*900 < seg0 + 2000:
        lo = seg0 + c*900; amp[lo:min(lo+500, seg0+2000)] = 1; c += 1
amp[2000:4000] = 1
F = np.abs(np.fft.rfft(amp - amp.mean())); fr = np.fft.rfftfreq(6000, .01)
top = np.argsort(-F)[:5]
print('\nenvelope spectrum top bins (Hz, rel. amp):', [(round(float(fr[i]), 4), round(float(F[i]/F.max()), 3)) for i in top])
print('on-fraction of the 60 s window: %.3f ; scored (0.7-Hz, post-500) samples with drive ON: %.3f'
      % (amp.mean(), np.r_[amp[500:2000], amp[4500:6000]].mean()))
