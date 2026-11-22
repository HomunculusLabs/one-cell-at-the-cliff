# L210 PREREG — the dominant-mode COEFFICIENT (static, zero rollouts)

Written BEFORE any L210 number was read. Card: LANE.md L210.
Substrate: f4wA (the syn>=4-floored closure substrate L178/L205/L206/L209 use).
Operator: A = |g * W_beta| with g = G_F4WA = 0.15051452517509462, the
ANATOMICAL (row-mask-free, settle-free) form. CSR convention W[target, source].
Zero rollouts, zero settles, zero dynamics.

## What L206 left on the table

L206 measured, on this operator, the carrier's per-out-mass pool arrival mass
at depths 1-10 against the SAME 100 l169c degree-neutral destination swaps:

- deficit ratio median(null)/carrier = 8.378 (d2), 7.641, 9.784, 9.944,
  10.002, 10.156, 10.279, 10.357, **10.38807894033274 (d10)**;
- the carrier's POOL SHARE converges to the null's: .1571 vs .1572 at d10;
- the carrier's cos(x_d, v1) reaches only 0.9649 at d10 (mixing is slow).

The reading L206 wrote down: the avoidance is an AMPLITUDE effect on the
operator's dominant mode, not a distribution effect. If that is right, the
deficit has a closed form in the LEFT eigenvector.

## The statistic (registered)

For a nonnegative operator A with Perron pair (lam1, v1) and left Perron
vector u1 (A^T u1 = lam1 u1), for any source cell c:

    A^d e_c  ->  lam1^d * (u1[c] / (u1 . v1)) * v1      (as d -> inf)

so the pool arrival mass from c obeys

    P_d(c)  ->  lam1^d * K(c),      K(c) := u1[c] * S_v / (u1 . v1)

with S_v := sum of v1 over the 303 pool cells (the 20 semantic pools, key
order as inherited). K(c) is the DOMINANT-MODE COEFFICIENT. It is invariant
to the scaling of u1 and of v1 (both appear once in numerator and denominator
of their own normalisation), which is the only reason it is comparable across
the 101 operators (real + 100 draws).

Per-draw quantities: lam_k, v_k, u_k, K_k computed on THAT draw's operator.
The swap preserves the carrier's out-degree and out-strength multiset exactly
(l169c destination swap), so m_out is identical across draws and cancels in
every ratio reported here.

## Gate cells (SEPARATE objects, L109)

**Q210-1 (PRIMARY, branch-bearing).** The asymptotic prediction of the
depth-10 deficit:

    R_asym := median_k( lam_k^10 * K_k(carrier) ) / ( lam1^10 * K_real(carrier) )

compared to the MEASURED D10 := 10.38807894033274 (L206 stored, re-certified
by CERT-206 before use). Registered branches, in order:

- **B_CLOSED_FORM** iff |R_asym / D10 - 1| <= 0.10 — the avoidance collapses
  to one number and that number is a draft sentence.
- **B_ORDER_ONLY** iff 0.5 <= R_asym / D10 <= 2.0 and not B_CLOSED_FORM — the
  dominant mode explains the sign and order; residual depth structure remains.
- **B_NO_MATCH** otherwise — L206's mechanism sentence must be WEAKENED and
  the depth-invariance has another cause.
- **B_DEGENERATE** if any power iteration fails its convergence bar
  (rel spread of the last 6 growth factors > 1e-6): then no branch is called
  and the tick reports a measurement failure, not a result.

**Q210-2 (registered literal form, NO branch).** The card's own wording is
"the ratio of left-eigenvector overlaps, u1[carrier] vs the null draws'
u1[carrier]". That bare form is reported as
R_bare := median_k(u_k[carrier]) / u1_real[carrier] under the unit-L2
normalisation each power iteration returns, WITH the disclosure, written here
in advance, that an L2 normalisation of u on two different operators is a
CONVENTION and not a canonical comparison; Q210-1's K is the convention-free
version and is the one carrying the branch.

**Q210-3 (CONVERGENCE CEILING; must be reported BEFORE the branch verdict).**
On the REAL operator, C_real := P_10(carrier) / (lam1^10 * K_real(carrier)).
The asymptotic formula is exact only as d -> inf, and the carrier's cos at
d10 is 0.9649, so C_real measures how much room any closed form has. If
|C_real - 1| > 0.10 the 10% bar in Q210-1 is NOT reachable by pointwise
accuracy and a pass can only come from error CANCELLING between numerator and
denominator — in that case the pass is reported as a RATIO-level pass and
explicitly not as a pointwise one. Same quantity reported for the twin and for
the null median.

**Q210-4 (the honest version of "depth-invariant": the SPECTRAL GAP).**
|lam2| / lam1 by Hotelling deflation on the real operator (x <- A x, then
x <- x - v1 * (u1.x)/(u1.v1), renormalise; growth factor tracked over 400
iterations, rel spread of the last 6 reported). A complex subdominant pair
will NOT converge under real power iteration: that outcome is reported as
NOT_CONVERGED with the observed range, never as a number.

**Q210-5 (descriptive cohort, no branch).** K(n)/m_out(n) for all 35 L178
actors (carrier, mass-matched twin gi 290, 33-cell ng family) and the
carrier's rank in that cohort. L178 put the carrier at rank 33 of 35 on
depth-2 per-mass reach; if the dominant-mode coefficient is the mechanism, the
rank should be reproduced. Reported as a consistency read, with L207's lesson
noted: a percentile against a 35-cell cohort has 35-cell resolution.

## Certification (all halting; nothing new is read until these are green)

Inherited FREE, as verbatim certified source slices (L85), no lab module
imported (L175):

- CERT-HEAD1 = l151_static.py lines 1-319 (sha256 e6245e8306dc8a0f expected)
- CERT-HEAD2 = l178_tail.py lines 7-149 (CERT-F4, the three gains at float
  equality, f4wA 21,789 / 469,618, CSR orientation, all 20 pool sizes)
- MID = l206_mid.py (the csr_rows/csr_cols bridge + its invariant)
- CERT-HEAD3 = l178_tail.py lines 348-458 (CERT-REW = l169c P6 + the 100 draws)
- CERT-HEAD4 = l206_tail.py lines 22-263, which re-runs **CERT-178** (420
  stored L178 anatomical values at float equality), the lam1 power iteration,
  the depth-1..10 sweep with its own float-equality self-check against L178,
  the 100-draw null construction and **CERT-NULL** (8 stored Q2b statistics).

NEW gates in this card's tail:

- **CERT-206 (HALTING)**: every field of L206's stored 10 G1 rows
  (carrier, null_med, null_p05, null_p95, pct, ratio_med_over_carrier,
  carrier_share, null_share_med, carrier_cos_v1) plus deficit_ratio_tail_mean
  and lam1 reproduced by FLOAT EQUALITY (==) from the re-run sweep and nulls,
  using the SOURCE's own expressions (L206 lesson: a float-equality claim is a
  claim about the expression, not just the operands). ~91 values. Halts.
- **CERT-MV (HALTING)**: the bincount matvec used for the 202 extra power
  iterations reproduces the certified np.add.at jmatvec by EXACT array
  equality on four probe vectors (ones, e_carrier, V1, a seeded random), in
  both index orders; and the transpose is the SAME function with the index
  arrays swapped (no new transpose machinery), checked by the bilinear
  identity u.(Ax) == (A^T u).x at rel diff < 1e-12.
- **CERT-LEFT**: the LEFT power iteration's growth factor equals LAM1 to
  rel < 1e-9 (two independent iterations on one operator must agree on the
  spectral radius) and the right-iteration replay with bincount reproduces
  LAM1 and V1 (|cos - 1| < 1e-12).
- **CERT-REBUILD (HALTING)**: my per-draw operator reconstruction (from the
  slice's own stored `changed` lists) reproduces the slice's stored null pool
  arrival mass NP_[i, d] for all 100 draws x 10 depths by FLOAT EQUALITY,
  using np.add.at exactly as the certified null loop does. 1,000 values.
  If this is green the 100 draw operators ARE the certified ones.

## Predictions (recorded before measuring)

1. Q210-1 -> **B_CLOSED_FORM**. (Share converged to the null's to 4 decimals
   and the deficit ratio's last-three spread is < 0.4%; amplitude-only is the
   natural reading.)
2. Q210-2: R_bare within 25% of R_asym (the convention is loose but not wild).
3. Q210-3: |C_real - 1| > 0.10 — I expect C_real in [0.75, 1.00), BELOW the
   asymptote, because the carrier's lam1-normalised per-mass value is still
   falling ~2% per hop at d10.
4. Q210-4: |lam2|/lam1 in [0.75, 0.95] (1 - cos .9649 at d10 implies slow
   mixing), converged.
5. Q210-5: the carrier is in the bottom 3 of the 35-actor K/m_out cohort.

## Out of scope (named, not silently dropped)

- No dynamics: the gated/row-masked operator, the settle, and the saturation
  mask are all absent by construction (this is the anatomical leg; L178's
  gated leg was twin-side labile and is not revisited here).
- No second substrate: cutwA / the Crofts operator are not swept here; L209
  already showed Crofts is a different OPERATOR, not a normalisation.
- No new rollouts, no live change, no draft edit.
