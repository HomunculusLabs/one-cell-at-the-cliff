"""l234_probe.py — PRE-PREREG feasibility probe, STORED ARTIFACTS ONLY.

Reads l218/static.json (already certified) and nothing else. No operator, no
eigenvector, no new measurement. Its only job is to decide, BEFORE the PREREG
is written, (i) whether a third mode is even visible in the one-mode residual
and (ii) what brackets the card may legitimately register for the measured
(r3, A3) — per L214: a quantity derivable from stored artifacts is DESCRIPTION,
so it is declared here and the PREDICTION is that the *measured* third
eigenpair reproduces it.
"""
import json
import math

import numpy as np

S = json.load(open("l218/static.json"))
CCAR = np.array(S["profile"]["C_car"], dtype=float)
GAP = float(S["Q210_4_gap"]["gap"])
LAM1 = float(S["Q210_4_gap"]["lam1"])
A2 = float(S["Q218_3_u2"]["A2_real"])
K_REAL = float(S["Q218_3_u2"]["K_real"])
K2_REAL = float(S["Q218_3_u2"]["K2_real"])
DEEP = len(CCAR)
DS = np.arange(1, DEEP + 1)

E = CCAR - 1.0                       # the deficit's convergence correction
ONE = A2 * GAP ** DS                 # L218's one-mode closed form
R = E - ONE                          # the residual the card calls mode 3

print(f"stored: GAP {GAP!r} LAM1 {LAM1!r} A2 {A2!r}")
print(f"stored: K {K_REAL!r} K2 {K2_REAL!r} A2*K == K2 ? "
      f"{A2 * K_REAL == K2_REAL}")
print(f"stored relerr d10 {S['Q218_3_u2']['closed_form_max_relerr_d10_50']!r} "
      f"d50 {S['Q218_3_u2']['closed_form_relerr_d50']!r}")

# reproduce L218's own one-mode relative error, as a probe self-check
rel = np.abs(ONE - E) / np.abs(E)
print(f"probe one-mode relerr: d10 {rel[9]:.6f}  max(d10-50) {rel[9:].max():.6f}"
      f"  d50 {rel[-1]:.6f}")

print("\n d   e(d)         one-mode      residual      resid/e      sign")
for d in (10, 15, 20, 25, 30, 35, 40, 45, 50):
    j = d - 1
    print(f"{d:3d}  {E[j]:.6e}  {ONE[j]:.6e}  {R[j]:+.6e}  "
          f"{R[j] / E[j]:+.5f}   {'+' if R[j] > 0 else '-'}")

sgn = np.sign(R[9:])
print(f"\nresidual sign over d10-50: all positive {bool((sgn > 0).all())} | "
      f"all negative {bool((sgn < 0).all())} | sign changes "
      f"{int((np.diff(sgn) != 0).sum())}")

# the implied third mode: log-linear fit of the residual over d>=10
j0 = 9
dd = DS[j0:].astype(float)
y = np.log(np.abs(R[j0:]))
b, a = np.polyfit(dd, y, 1)
r3_fit = math.exp(b)
A3_fit = math.exp(a)
print(f"\nlog-linear fit of |residual| on d10-50: r3 {r3_fit:.6f} "
      f"(lam3 {r3_fit * LAM1:.4f})  A3 {A3_fit:.6f}")
pred = A3_fit * r3_fit ** dd
print(f"fit relerr on the residual itself: max {np.abs(pred / np.abs(R[j0:]) - 1).max():.4f}")

# two-point estimate (d10, d50) — independent of the fit's weighting
r3_2pt = (abs(R[49]) / abs(R[9])) ** (1.0 / 40.0)
A3_2pt = abs(R[9]) / r3_2pt ** 10
print(f"two-point (d10,d50): r3 {r3_2pt:.6f} (lam3 {r3_2pt * LAM1:.4f})  "
      f"A3 {A3_2pt:.6f}")

# how good would a TWO-mode form be with these implied values?
two = A2 * GAP ** DS + A3_2pt * r3_2pt ** DS
rel2 = np.abs(two - E) / np.abs(E)
print(f"implied two-mode relerr d10-50: max {rel2[9:].max():.6f} "
      f"d10 {rel2[9]:.6f} d50 {rel2[-1]:.6f}")
print(f"ratio r3/r2 {r3_2pt / GAP:.6f}  (a 4th mode shows as curvature here)")

# is the residual's own decay CLEAN (single geometric) or curved?
lr = [float(np.log(abs(R[j + 1]) / abs(R[j]))) for j in range(j0, DEEP - 1)]
print(f"per-hop log-ratio of the residual: first {lr[0]:+.6f} "
      f"last {lr[-1]:+.6f} median {float(np.median(lr)):+.6f} "
      f"spread {max(lr) - min(lr):.6f}")

# leg (b) feasibility: what IS derivable about K2's null from stored data?
print("\n--- leg (b) stored-data census ---")
for k in ("A2_draw_med", "A2_p05", "A2_p95", "A2_percentile",
          "u2_carrier_percentile_absval", "u2_draw_med_absval"):
    print(f"  Q218_3_u2.{k} = {S['Q218_3_u2'][k]!r}")
print(f"  Q210_1.null_K_med = {S['Q210_1_primary']['null_K_med']!r}")
print(f"  Q210_1.carrier_K_percentile = "
      f"{S['Q210_1_primary']['carrier_K_percentile']!r}")
print(f"  per-draw K stored? {'K' in S['rows_per_draw_recomputed'][0]}  "
      f"n={len(S['rows_per_draw_recomputed'])}")
print(f"  per-draw K2 stored? "
      f"{'K2' in S['rows_per_draw_recomputed'][0]} <- the card's premise")
KK = np.array([r["K"] for r in S["rows_per_draw_recomputed"]], dtype=float)
print(f"  median(K_k) {float(np.median(KK)):.8e} == stored null_K_med "
      f"{float(np.median(KK)) == S['Q210_1_primary']['null_K_med']}")
print(f"  K2_real/K_real {K2_REAL / K_REAL:.6f} == stored A2 {A2 == K2_REAL / K_REAL}")
print(f"  NOT derivable: median(K2_k), pct(K2_k < K2_real)  -> the card's leg")
