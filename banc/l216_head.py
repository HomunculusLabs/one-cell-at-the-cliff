# ================= L216 HEAD (constants, before the L209 slice) ===========
# Everything above this line is VERBATIM source: l151_static.py 1-319,
# l178_tail.py 7-149, the l206_mid bridge, l206_tail.py 22-121 (CERT-178 =
# 420 stored L178 anatomical values at FLOAT EQUALITY, reach(), power_iter,
# LAM1, V1), l207_tail.py 26-146 (gain invariance + the GENERIC substrate
# builder + CERT-GEN), and l210_tail.py's three machinery defs (mv, pi_dir,
# lam2_defl) VERBATIM. Below: L216's constants, then l209_tail.py lines
# 34-226 VERBATIM (L205's seven substrates, GROUPS, the shared permutation
# draws, side_stats_from/decorate, CERT-205, the two L216 substrates, the
# beta/Crofts operators with their lam1, and arrivals()), then the L216 body.
# PREREG: l216/PREREG.md (registered first). Writes l216/static.json ONLY.
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

o["design"] = (
    "L216 the DEPTH-DECAY LAW. Per-side arrival mass r_d = A^d 1 of the "
    "ANATOMICAL operator into the Ti/Tr pools on cutwA vs f4wA, depths 1..8, "
    "beta (g=1) and Crofts/Estrada operators. PREMISE CORRECTION registered "
    "FIRST: A_cell(d) is a normalised contrast whose limit is the Perron "
    "asymmetry A_inf = asym(v1 per-cell means), NOT zero, so the quantity "
    "that decays at the spectral rate is A_cell(d) - A_inf and the card's "
    "bare c*r^d is a special case asserting A_inf == 0. Primary estimator = "
    "OLS of log|A_cell(d) - A_inf| on d over the ASYMPTOTIC range d=4..8 "
    "(unobserved when the PREREG was written); tested against gap = "
    "|lam2|/lam1 of the SAME operator by Hotelling deflation. "
    "PREREG l216/PREREG.md.")
o["prereg"] = "l216/PREREG.md"
with open("l216_static.py") as _bf:
    o["banner"] = "".join([next(_bf) for _ in range(14)])

log("=" * 72)
log(f"[L216] depth-decay law | NDRAW {NDRAW} seed {SEED_PERM} DMAX {DMAX}")
