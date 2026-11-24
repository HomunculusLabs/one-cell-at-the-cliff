"""l225_probe.py -- PREREG premise probes, run BEFORE the card is written.
No card artifact is written. Two questions:
 (1) is np.median(A, axis=1) BIT-IDENTICAL to a per-row np.median loop?
     (decides whether CERT-FAST can be np.array_equal or needs a tolerance)
 (2) does a default_rng stream CONTINUE deterministically past the first
     N_CERT perm_within draws? (decides whether the extended FDR sweep can
     reproduce l213's 2000-draw null exactly as a PREFIX)
"""
import numpy as np

rng0 = np.random.default_rng(99)
ok = True
for s in (2, 3, 4, 5, 6, 7, 8, 11):
    A = rng0.random((400, s)) * 10.0 ** rng0.integers(-6, 2, size=(400, 1))
    fast = np.median(A, axis=1)
    slow = np.array([np.median(A[i]) for i in range(A.shape[0])])
    eq = np.array_equal(fast, slow)
    ok = ok and eq
    print(f"size {s:2d}: array_equal {eq}  maxabs {np.abs(fast - slow).max():.3e}")
print("Q1 verdict: axis-median bit-identical to per-row loop =", ok)


def perm_within(st, rng, n_strata=10):
    idx = np.arange(len(st))
    out = idx.copy()
    for s in range(n_strata):
        sel = idx[st == s]
        out[sel] = rng.permutation(sel)
    return out


st = np.repeat(np.arange(10), 129)
a = np.random.default_rng(21342)
first = [perm_within(st, a) for _ in range(2000)]
b = np.random.default_rng(21342)
both = [perm_within(st, b) for _ in range(5000)]
pref = all(np.array_equal(first[i], both[i]) for i in range(2000))
tailnew = not np.array_equal(both[2000], both[0])
print("Q2 verdict: first 2000 draws are a PREFIX of the 5000-draw stream =",
      pref, "| draw 2001 differs from draw 1 =", tailnew)

# resolution-floor arithmetic, registered in advance
for B in (2000, 20000):
    for m in (426, 411, 409):
        pmin = 1.0 / (B + 1)
        thr1 = 0.05 * 1 / m
        need = int(np.ceil(m * pmin / 0.05))
        print(f"B={B:6d} m={m}: p_min {pmin:.3e} vs BH rank-1 thr {thr1:.3e} "
              f"-> rank-1 rejectable {pmin <= thr1} | min #floor-tied types "
              f"for any rejection = {need}")
