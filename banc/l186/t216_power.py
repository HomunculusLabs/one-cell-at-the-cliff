#!/usr/bin/env python
"""tick-216 addendum: WHY L186 came out E3 (power of the alignment discriminator).

The primary metric correlates 500-step windows at offsets -250..+250 from the
flexor seed's own displaced onset.  The aligned clock takes the extensor seed's
window at ITS onset + the same offset; the elapsed clock takes it at the same
ABSOLUTE time.  The two clocks therefore differ by lag = onset_i - onset_j and
their windows OVERLAP by max(0, 1 - |lag|/500) of their samples.  If that
overlap is large, D is small by construction and E1/E2 are unreachable
regardless of the biology.  Zero rollouts; stored onsets only.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_l186.json")))
seeds = [int(s) for s in R["seeds"]]
onsets = {int(k): [int(v) for v in vs] for k, vs in R["onsets"].items()}
WIN, PER = 500, 1.0 / 0.7 / 0.01

lags, ov = [], []
for si in seeds:
    for sj in seeds:
        if si == sj:
            continue
        for seg in (0, 1):
            L = onsets[si][seg] - onsets[sj][seg]
            lags.append(abs(L))
            ov.append(max(0.0, 1.0 - abs(L) / WIN))
lags, ov = np.array(lags, float), np.array(ov, float)
res = dict(
    n_pair_segments=int(lags.size),
    mean_abs_lag_steps=float(lags.mean()), median_abs_lag_steps=float(np.median(lags)),
    max_abs_lag_steps=float(lags.max()),
    mean_window_overlap=float(ov.mean()), median_window_overlap=float(np.median(ov)),
    frac_pairs_overlap_ge_half=float((ov >= 0.5).mean()),
    frac_pairs_disjoint=float((ov == 0.0).mean()),
    window_steps=WIN, tone_period_steps=PER,
    mean_abs_lag_in_tone_periods=float(lags.mean() / PER),
    jitter_band_steps=600,
    needed_jitter_for_disjoint_windows=int(WIN * 2),
)
print(json.dumps(res, indent=1, sort_keys=True))
print()
print(f"mean |lag| {lags.mean():.0f} steps = {lags.mean()/PER:.2f} tone periods, "
      f"but only {lags.mean()/WIN:.2f} of one correlation window")
print(f"=> aligned and elapsed windows share {100*ov.mean():.0f}% of their samples on average; "
      f"{100*(ov>=.5).mean():.0f}% of pair-segments share half or more, "
      f"{100*(ov==0).mean():.0f}% are disjoint")
print("=> the alignment contrast D is attenuated by construction: the registered")
print("   +-300-step jitter is SMALLER than the 500-step readout window, so the two")
print("   clocks are not independent views.  A decisive rerun needs either")
print(f"   jitter >= {WIN*2} steps (disjoint windows) or a window shorter than the jitter.")
json.dump(res, open(os.path.join(HERE, "t216_power.json"), "w"), indent=1, sort_keys=True)
