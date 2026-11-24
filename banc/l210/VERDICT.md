# L210 VERDICT — the dominant-mode COEFFICIENT

Branch **B_CLOSED_FORM** (registered), on the primary cell, at the threshold.
PREREG: `l210/PREREG.md` (written first). Artifacts: `l210/static.json`,
`l210/run.out`, `l210/run.err`. Code: `l210_build.py` + `l210_tail.py` ->
generated `l210_static.py`. 5m47s, CPU, zero rollouts / settles / dynamics.

## The headline

L206's depth-invariant ~10.39x carrier pool-reach deficit **does have a closed
form, and it is one number: the carrier's LEFT-Perron overlap.**

- u1[carrier] = 4.0973e-04 real vs **4.6726e-03** null median (100 l169c
  degree-neutral destination swaps), percentile **0.0** — every one of the 100
  draws gives the carrier a larger dominant-mode overlap than its real wiring.
- Predicted depth-10 deficit R_asym = median_k(lam_k^10 K_k) / (lam1^10 K_real)
  = **11.3985** vs the stored measured D10 = **10.38808** -> ratio **1.0973**,
  inside the registered |.|<=0.10 bar **by 0.27 percentage points**. This is a
  threshold-clearing pass and is written that way everywhere.

The prediction is carried ENTIRELY by the overlap, which is what makes it a
closed form rather than a fit:

- lam1 is essentially swap-invariant: 30.179788 real vs median 30.179083
  (min 30.176121), so even raised to the 10th power the eigenvalue factor
  moves the prediction by **0.023%** (lam_ratio_med_pow10 = 0.99977).
- K_ratio_med = 11.4016 vs R_asym 11.3985: the pool-sum and (u.v) factors
  cancel.
- Q210-2's bare form (the card's literal wording, unit-L2 u) = **11.4039**,
  agreeing with the scaling-invariant K form to **0.047%**. The convention
  disclosure registered in advance turned out to be unnecessary — but it was
  registered, and that is why the agreement is evidence instead of luck.

## The 9.7% residual is itself measured, not left as slack

Q210-3 (reported BEFORE the branch, as registered) refutes my recorded
prediction by DIRECTION: C_real = P_10/(lam1^10 K_real) = **1.2030**, i.e. the
carrier sits **above** its asymptote at depth 10, not below. The nulls sit
above too but less: C_null_med = **1.1029** [p05 .9864, p95 1.2245]; the twin
1.1755. So |C_real - 1| = 0.203 > 0.10 and **pointwise accuracy of the closed
form is NOT reachable at depth 10** — the Q210-1 pass is a RATIO-level pass in
which the two convergence errors partly cancel, exactly as the PREREG said it
would have to be.

And the surviving part of the residual is accounted for:

    C_real / C_null_med = 1.0907   vs   R_asym / D10 = 1.0973

The 9.7% overshoot IS the carrier's slower approach to the dominant mode
(the small remaining difference is median-of-products vs product-of-medians).
The honest sentence: the deficit factorises into an exact dominant-mode term
(11.40x) and a depth-dependent convergence correction (1.09x at d10) that
decays as the walk mixes.

## Q210-4: why "depth-invariant" needed the gap

|lam2| = **26.9469** by Hotelling deflation, converged tight (rel spread of
the last 6 growth factors 3.09e-10), so lam2/lam1 = **0.89288**. Then
(lam2/lam1)^10 = **0.322** — a third of the subdominant amplitude is still
present at depth 10, which is exactly why cos(x_10, v1) is only 0.9649 and why
L206's deficit was still drifting upward (10.279 -> 10.357 -> 10.388) rather
than sitting flat. "Depth-invariant" is a good description of the ratio's
behaviour and a bad description of its convergence.

## Q210-5: the cohort read, consistent in direction, one rank off

K/m_out (the depth-infinity analogue of L178's per-mass reach) puts the carrier
at **3.166e-05, rank 4 of 35** (cohort percentile .086), **14.5x below** the
33-cell ng family median (4.602e-04) and 5.8x below the mass-matched twin
(1.841e-04). Registered prediction was bottom-3; measured rank 4. L207's lesson
applies verbatim — against a 35-cell cohort one rank is 2.9 percentile points,
so "bottom 3" vs "rank 4" is a statement about cohort resolution, not about
the cell. Bottom six: fam26_1543, fam17_32097, fam27_1509, **carrier**,
fam08_924, fam07_890.

## What this does NOT establish (named, not buried)

- A closed form is not a mechanism. u1[carrier] = (1/lam1) * sum_t
  A[t,carrier] u1[t]: the deficit has been moved from "pool reach at depth d"
  to "where its 69 out-edges point, weighted by the targets' own importance".
  That decomposition is L219 (seeded this tick); L211 asks the same question in
  the routing/search-information currency and must not double-count the claim.
- Anatomical leg only: no row mask, no settle, no saturation. L178's gated leg
  was twin-side labile and is not revisited.
- One substrate (f4wA), one operator (|g W_beta|). L209 already showed Crofts
  is a different OPERATOR, not a normalisation.
- The nulls are the l169c destination swaps: out-degree and out-strength
  multiset preserved exactly, target in-degree preserved, both halves applied.
  A different null gives a different magnitude (L207's cross-null law).

## Predictions: 3 of 5

| cell | registered | measured | |
|---|---|---|---|
| Q210-1 | B_CLOSED_FORM | B_CLOSED_FORM (ratio 1.0973) | correct |
| Q210-2 | R_bare within 25% of R_asym | 1.00047 | correct |
| Q210-3 | C_real in [0.75, 1.00) | 1.2030 (above, not below) | **wrong** |
| Q210-4 | gap in [0.75, 0.95], converged | 0.89288, converged | correct |
| Q210-5 | carrier bottom 3 of 35 | rank 4 | **wrong** |

## Certification (all halting, all green before any L210 number was read)

Inherited free as verbatim certified source slices (L85), no lab module
imported (L175):

- CERT-HEAD1 l151_static.py 1-319, sha256 `e6245e8306dc8a0f` — identical to
  the head sha recorded by L178/L205/L206/L207/L209, asserted a literal
  PREFIX, so the whole L151/L142/L134/L92/L101 pin set re-ran free.
- CERT-HEAD2 l178_tail.py 7-149, sha256 `6e2e8fa4bd19eced` — CERT-F4 (K4 73,
  carrier rank 21, twin gi 290, mass gap 2.44e-05, f4wA n 21,789 / edges
  469,618, family 33), the three gains at FLOAT EQUALITY, CSR orientation
  (carrier out 69 / in 12), all 20 pool sizes.
- MID l206_mid.py sha256 `febbc390ad4f` (CSR bridge + its invariant).
- CERT-HEAD3 l178_tail.py 348-458, sha256 `5bb7b56e6b6487d5` — CERT-REW
  (l169c P6 reproduced exactly, 100 draws, seed 16943) + the draw map.
- CERT-HEAD4 l206_tail.py 22-263, sha256 `772a2410e76516e5` — **CERT-178**
  (420 stored L178 anatomical values at float equality), lam1 by power
  iteration (rel spread 1.18e-16), the depth-1..10 sweep with its own
  float-equality self-check vs L178 (max rel diff 0.0), the 100-draw null
  construction and **CERT-NULL** (8 stored Q2b statistics).

New in this card:

- **CERT-206 (HALTING)**: 94 stored L206 G1 values reproduced by FLOAT
  EQUALITY — 10 depths x 9 fields (carrier, null med/p05/p95, percentile,
  deficit ratio, carrier share, null share median, cos) + lam1 + tail mean +
  tail spread + the D10 pin. Caught one real defect: my first transcription of
  the tail mean averaged all depths while L206's expression cuts at d_conv
  (None -> DMAX, so its "tail" is the d10 value alone). The gate halted the
  run; the L206 lesson (a float-equality claim is a claim about the
  EXPRESSION) bit again and was caught by the gate, not by a wrong number.
- **CERT-MV (HALTING)**: the bincount matvec used for the 202 extra power
  iterations reproduces the certified np.add.at jmatvec by EXACT array
  equality on 4 probes x 2 index orders (8/8, max diff 0.0); the transpose is
  the SAME function with the index arrays swapped (no new machinery), bilinear
  identity u.(Ax) == (A^T u).x at rel diff 0.0.
- **CERT-LEFT**: right-iteration replay reproduces LAM1 at rel 0.0 and V1 at
  |cos-1| 2.2e-16; the independent LEFT iteration agrees on the spectral
  radius at rel 2.35e-16 (spread 3.53e-16) and returns a nonnegative vector.
- **CERT-REBUILD (HALTING)**: 1,000 stored null values (100 draws x depths
  1-10) reproduced by FLOAT EQUALITY from my own per-draw operator rebuild
  using the certified null loop's own np.add.at construction — so the 100
  operators eigendecomposed here ARE the certified ones.
- Convergence asserted per draw: 100/100 draws converged on BOTH directions
  (rel spread < 1e-6) and left/right lam1 agree to < 1e-9, so B_DEGENERATE
  did not fire.

Total: 420 + 8 + 94 + 8 + 1,000 = **1,530 float-equality / exact-equality
checks** green before the branch was called.
