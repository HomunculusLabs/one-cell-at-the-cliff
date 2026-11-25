# L240 A2 fourth POST-HOC probe (tick 276, unregistered, non-branching):
# TRACE-LEVEL identity of the no-op arms. The results json shows eight arms with
# mean, vector and CI all exactly 0; this compares their 20 pool traces x 16 seeds
# with the base's stored pool traces BIT FOR BIT (np.array_equal on float32).
# Read-only on the npz files.
import json
import numpy as np

out = 'l240'
Z = {w: np.load(f'{out}/raw_w{w}.npz') for w in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
cls = ('Ti', 'Tr', 'Ta', 'Sr', 'Pr')
wk = lambda k: k.split('_')
base_keys = {(wk(k)[0], wk(k)[1], wk(k)[3]): k for k in Z[0].files if len(wk(k)) == 4 and wk(k)[0] in cls and wk(k)[2] == 'cutwA'}
seeds_b = sorted({s for _, _, s in base_keys})
assert len(base_keys) == 20 * len(seeds_b), len(base_keys)   # every seed carries all 20 pools, no key collisions
print('base pool traces in worker 0:', len(base_keys), '| classes', cls, '| suffixes', sorted({p for _, p, _ in base_keys}), '| seeds', len(seeds_b), seeds_b[:3], '...', seeds_b[-2:])
for a in ['e1', 'e2', 'e8', 'e9', 'e16', 'e21', 'e47', 'e55', 'e37', 'e61', 'e42', 'e43', 'e45', 'e27', 'e14']:
    found = [(w, k) for w in Z for k in Z[w].files if len(wk(k)) == 4 and wk(k)[0] in cls and wk(k)[2] == a]
    if not found:
        print(a, 'NO POOL TRACES FOUND'); continue
    ws = sorted({w for w, _ in found})
    same = n = 0; maxd = 0.0; nonzero = []
    for w, k in found:
        p = wk(k); bk = base_keys.get((p[0], p[1], p[3]))
        if bk is None:
            continue
        n += 1
        x, y = Z[w][k], Z[0][bk]
        eq = bool(np.array_equal(x, y))
        same += eq
        d = float(np.abs(x.astype(np.float64) - y.astype(np.float64)).max())
        maxd = max(maxd, d)
        if not eq:
            nonzero.append((p[1], p[3], d))
    print(f'{a}: workers {ws} | pool traces compared {n} | bit-identical to the base trace {same} | max |diff| over the whole 6000-step trace {maxd:.3e}'
          + ('' if not nonzero else f' | differing e.g. {[(c, s, round(d, 5)) for c, s, d in nonzero[:2]]}'))
