#!/usr/bin/env python3
"""Round-2 probe 3: what is the 'antagonist structure' statistic made of?
RAW traces of one batch (l169d = batch L, the stage-(d) XOR batch), right tibia.
Reconstructs the drive s(t) from DRAFT §3.3 constants. Read-only."""
import numpy as np, math
z = np.load('/home/t3rpz/critters/peabrain-lab/banc/l169d/raw_l169d.npz')
WIN, DT, ENT = 6000, .01, .1
amp = np.zeros(WIN)
for seg0 in (0, 2000, 4000):
    c = 0
    while seg0 + c * 900 < seg0 + 2000:
        lo = seg0 + c * 900
        amp[lo:min(lo + 500, seg0 + 2000)] = ENT
        c += 1
amp[2000:4000] = ENT
f = np.r_[np.full(2000, .7), np.full(2000, 1.4), np.full(2000, .7)]
phi = np.cumsum(2 * math.pi * f * DT)
s = amp * (.5 + .5 * np.sin(phi))
idx = np.r_[500:2000, 4500:6000]
seeds = sorted({int(k.rsplit('_', 1)[1]) for k in z.keys() if k.startswith('Ti_fR_cutwA_')})
print('batch L seeds', len(seeds), '| BG = .02, active threshold in DRAFT 3.4 = .05, RMAX = 1.0')
print('arm       | flexR: mean  p05   p95  frac>.05 corr(s) | extR: mean  p05   p95  frac>.05 corr(s) | corr(flex,ext) whole scored region')
for arm in ['b65', 'full', 'cutwA', 'cutng25p', 'cutng25', 'p25gN', 'n25gP']:
    acc = []
    for sd in seeds:
        try:
            fR = z[f'Ti_fR_{arm}_{sd}'][:6000].astype(float); eR = z[f'Ti_eR_{arm}_{sd}'][:6000].astype(float)
        except KeyError:
            continue
        a, b, ss = fR[idx], eR[idx], s[idx]
        acc.append([a.mean(), np.percentile(a, 5), np.percentile(a, 95), (a > .05).mean(), np.corrcoef(a, ss)[0, 1],
                    b.mean(), np.percentile(b, 5), np.percentile(b, 95), (b > .05).mean(), np.corrcoef(b, ss)[0, 1],
                    np.corrcoef(a, b)[0, 1]])
    if not acc:
        print(arm, 'absent'); continue
    m = np.mean(acc, 0)
    print('%-9s |        %.4f %.4f %.4f  %.3f   %+.2f  |       %.4f %.4f %.4f  %.3f   %+.2f  | %+.2f   (n=%d)'
          % (arm, *m, len(acc)))
