import numpy as np
z = np.load("l103/raw_l103.npz")
TS = np.arange(499, 6000, 10)
WIN = 6000
qf = np.zeros(WIN, bool)
qf[500:2000] = True
qf[4500:6000] = True
for p in ("LT", "FR"):
    for s in ("L", "R"):
        tr = np.array([z[f"{p}_{s}_cfn_{seed}"]
                       for seed in (11, 801, 901, 1001)])
        w = tr[:, qf]
        print(f"{p}_{s}: mean {w.mean():.4f} | frac windows >=0.05 "
              f"{(w.mean(1) >= .05).mean():.3f} | max {w.max():.3f}")
