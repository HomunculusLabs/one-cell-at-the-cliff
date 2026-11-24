# ================= L217 HEAD (constants, before the L209/L216 slices) =====
# Everything above this line is VERBATIM source: l151_static.py 1-319,
# l178_tail.py 7-149, the l206_mid bridge, l206_tail.py 22-121 (CERT-178 =
# 420 stored L178 anatomical values at FLOAT EQUALITY, reach(), power_iter,
# LAM1, V1), l207_tail.py 26-146 (gain invariance + the GENERIC substrate
# builder + CERT-GEN), and l210_tail.py's three machinery defs (mv, pi_dir,
# lam2_defl) VERBATIM. Below: L217's constants, then l209_tail.py lines
# 34-226 VERBATIM (L205's seven substrates, GROUPS, the shared permutation
# draws, side_stats_from/decorate, CERT-205, the two substrates, the
# beta/Crofts operators with their lam1, and arrivals()), then l216_tail.py
# lines 1-204 VERBATIM (pi_sub/gap_sub, CERT-GAP, CERT-209, the lam1^d no-op
# re-measurement, the depth 1..8 TABLE/NULLS, the Perron asymptotes AINF and
# the spectral GAPS), then the L217 body.
# PREREG: l217/PREREG.md (registered first, with amendment 0a-i written
# before this file was generated). Writes l217/static.json ONLY.
# Zero rollouts, zero settles, zero dynamics.
import os

NDRAW = 2000
SEED_PERM = 20526
JOINTS = ("Ti", "Tr")
DMAX = 8
DMAX_CERT = 3
DEEP = (4, 5, 6, 7, 8)
PCT_HI = 0.95
GAP_BAR = 0.10
ORDER_LO, ORDER_HI = 0.5, 2.0
# L217's own constants
OPS3 = ("beta", "crofts", "rw")
DEC_DEPTHS = (2, 3, 8)
D_SEP_BAR = 1.0
NULL_CROSS_FRAC_BAR = 0.25
CORD_FRAC_BAR = 0.5

o["design"] = (
    "L217 the CROSSING PHASE, the three-operator SIGN table, and the SOURCE "
    "population that carries the leftward drift. Re-posed per the L216 "
    "amendment: the primary asks WHEN each joint crosses (d_cross with its "
    "own null, computed per permutation draw on the shared stream), not "
    "WHETHER Tr is special. Premise correction 0a registered FIRST: the "
    "card's literal third operator W/s_in is ROW-stochastic under our "
    "A[dst,src] convention, so r_1 == 1 identically and it cannot carry a "
    "sign table — it is measured as a degeneracy probe and EXCLUDED, and the "
    "third leg is the SOURCE-normalised random walk T_pq = W_pq/s_p (Seguin "
    "2022/2023, tick-233 digest). Mechanism leg: the EXACT additive source "
    "decomposition r_d^(g) = A^d 1_g by super_class, by NT sign and by "
    "cord-vs-descending. PREREG l217/PREREG.md.")
o["prereg"] = "l217/PREREG.md"
with open("l217_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(15)])

log("=" * 72)
log(f"[L217] crossing phase + 3-operator sign table | NDRAW {NDRAW} "
    f"seed {SEED_PERM} DMAX {DMAX}")
