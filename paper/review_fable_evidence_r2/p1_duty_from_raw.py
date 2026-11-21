#!/usr/bin/env python3
"""Round-2 referee probe 1: per-(file, arm, seed) tibia duty from RAW npz traces.

Independent implementation (rolling Pearson via sliding_window_view, not the
lab's per-window np.corrcoef loop). Reads banc/*/raw_l*.npz ONLY; writes ONLY
into the evidence dir. No rollouts, CPU only.

Definitions taken from DRAFT §3.6 (and nothing else):
  S = -Pearson(flexor pool mean, extensor pool mean) over a 500-step window,
  sampled every 10 steps, per side; duty = fraction of samples with S >= .25
  inside the 0.7-Hz segments, dropping the first 500 steps of each segment.
A flat window (std <= 1e-6) is counted as "not structured" (the lab's code does
the same: nan >= .25 is False) and is ALSO counted separately here.
"""
import json, os, re, sys, time, zipfile
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

BANC = '/home/t3rpz/critters/peabrain-lab/banc'
OUT = os.path.dirname(os.path.abspath(__file__))
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
ENDS = np.arange(499, 6000, 10)                 # window = [t-499, t]
Q07 = np.zeros(len(ENDS), bool)
Q14 = np.zeros(len(ENDS), bool)
for a0, b0, fr in SEGB:
    m = (ENDS >= a0 + 500) & (ENDS < b0)
    if fr == 0.7:
        Q07 |= m
    else:
        Q14 |= m


def rollS(f, e):
    """-corr over each 500-step window ending at ENDS; nan where flat."""
    F = swv(f.astype(np.float64), 500)[::10][:len(ENDS)]
    E = swv(e.astype(np.float64), 500)[::10][:len(ENDS)]
    Fc = F - F.mean(1, keepdims=True)
    Ec = E - E.mean(1, keepdims=True)
    sf = F.std(1)
    se = E.std(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        r = (Fc * Ec).mean(1) / (sf * se)
    r[(sf <= 1e-6) | (se <= 1e-6)] = np.nan
    return -r


TI = re.compile(r'^Ti_fL_(.+)_(\d+)$')
files = sorted(os.path.join(d, n) for d in sorted(os.listdir(BANC))
               if os.path.isdir(os.path.join(BANC, d))
               for n in sorted(os.listdir(os.path.join(BANC, d)))
               if n.startswith('raw_') and n.endswith('.npz') and 'partial' not in n)
rows = []
t0 = time.time()
for f in files:
    names = [n[:-4] for n in zipfile.ZipFile(os.path.join(BANC, f)).namelist()]
    pairs = [TI.match(k).groups() for k in names if TI.match(k)]
    if not pairs:
        print('no Ti traces', f, flush=True)
        continue
    z = np.load(os.path.join(BANC, f))
    nbad = 0
    for arm, seed in pairs:
        try:
            tr = {c: z[f'Ti_{c}_{arm}_{seed}'] for c in ('fL', 'fR', 'eL', 'eR')}
        except KeyError:
            nbad += 1
            continue
        if min(len(v) for v in tr.values()) < 6000:
            nbad += 1
            continue
        tr = {c: v[:6000] for c, v in tr.items()}
        sR = rollS(tr['fR'], tr['eR'])
        sL = rollS(tr['fL'], tr['eL'])
        rec = dict(file=f, arm=arm, seed=int(seed))
        for side, s in (('R', sR), ('L', sL)):
            rec['duty07' + side] = float(np.mean(np.nan_to_num(s[Q07], nan=-9) >= .25))
            rec['duty14' + side] = float(np.mean(np.nan_to_num(s[Q14], nan=-9) >= .25))
            rec['nan07' + side] = int(np.isnan(s[Q07]).sum())
            rec['medS07' + side] = float(np.nanmedian(s[Q07])) if np.isfinite(s[Q07]).any() else None
        # pool activity in the scored 0.7-Hz region (steps 500-2000, 4500-6000)
        idx = np.r_[500:2000, 4500:6000]
        for c in ('fR', 'eR', 'fL', 'eL'):
            rec['mean_' + c] = float(tr[c][idx].mean())
            rec['sd_' + c] = float(tr[c][idx].std())
        rows.append(rec)
    print('%-28s arms*seeds=%5d skipped=%d  t=%.0fs' % (f, len(pairs), nbad, time.time() - t0), flush=True)
json.dump(dict(n_windows_q07=int(Q07.sum()), n_windows_q14=int(Q14.sum()), rows=rows),
          open(os.path.join(OUT, 'out_duty_rows.json'), 'w'))
print('rows', len(rows), 'q07 windows', int(Q07.sum()), 'q14 windows', int(Q14.sum()))
