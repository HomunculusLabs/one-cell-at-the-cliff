"""L19 post-hoc: WHY did the phasing gate fail in the chain?

Hypothesis (L14 anatomy): the looming->DNp01-04 route drives jump/extensor
MN targets, NOT the flexor pools — tau-tier phasing needs BOTH antagonists
driven (L18's cord reflex arc drove both). Measure per-pool response
amplitude on the seed-mean chain tensor vs the tensor's own noise floor
(tail std, steps 150-220, far from the event).
"""
import json

import numpy as np

d = np.load("l19/gesture_mean.npz")
res = json.load(open("l19/results_l19.json"))
tens = d["tensor"]
tail = tens[:, 150:220]
floor = float(np.mean(tail.std(axis=1)))          # per-cell tail std, mean

pools = {"Ti ext": d["Ti_e"], "Ti flex": d["Ti_f"],
         "Tr ext": d["Tr_e"], "Tr flex": d["Tr_f"],
         "TTMn (jump)": d["ttm"], "leg union": d["leg_u"]}
out = {"tail_noise_floor_mean_trace": floor}
print(f"seed-mean tensor tail noise floor (per-cell std): {floor:.5f}\n")
for name, idx in pools.items():
    tr = tens[idx]                                  # [n_pool, T]
    amp = float(np.abs(tr).max(axis=1).mean())      # mean per-cell peak |dm|
    snr = amp / (floor + 1e-12)
    out[name] = {"n": int(len(idx)), "mean_peak_abs_dm": amp, "snr": snr}
    print(f"{name:12s} n={len(idx):4d}  mean peak |dm| {amp:.5f}  "
          f"SNR vs floor {snr:6.1f}x")
json.dump(out, open("l19/pool_amplitudes.json", "w"), indent=1)
print("\nwrote l19/pool_amplitudes.json")
