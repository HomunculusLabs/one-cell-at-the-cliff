# L216 PREREG — the DEPTH-DECAY LAW

Tick 246, 2026-11-23. Static, zero rollouts / zero settles / zero dynamics.
Written and saved BEFORE `l216_static.py` was generated or run.

## The card

> extend the arrival sweep to depths 1..8, fit `A_cell(d) = c * r^d` (report
> the fit residual, and report r per substrate per operator), and test r
> against the spectral prediction — the side-contrast mode's decay should be
> governed by the subdominant spectrum, so compute lam2/lam1 of the SAME
> operator (deflated power iteration, convergence reported) and register in
> advance which of three branches holds: (i) r matches lam2/lam1 within 10%,
> (ii) matches in order only, (iii) no match.

---

## PREMISE CORRECTION 0a — the card's model has a provably wrong asymptote

`A_cell(d)` is not an amplitude, it is a **normalised contrast**:

    A_cell(d) = (mL_d - mR_d) / (mL_d + mR_d),   m_d = per-cell mean of A^d 1

Expand the seed `1` in the operator's eigenbasis, `1 = sum_k c_k v_k`:

    x_d = A^d 1 = c1 lam1^d v1 * [ 1 + (c2/c1) rho^d (v2/v1) + ... ],
    rho = lam2/lam1

so with `P_k^L` the per-cell mean of `v_k` over the LEFT pool cells,

    A_cell(d) = [ (P1L-P1R) + (c2/c1) rho^d (P2L-P2R) + ... ]
                / [ (P1L+P1R) + (c2/c1) rho^d (P2L+P2R) + ... ]

    ==>  A_cell(d)  ->  A_inf = (P1L - P1R) / (P1L + P1R)   as d -> inf,
         and         A_cell(d) - A_inf  ~  K * rho^d.

**The quantity that decays at the spectral rate is `A_cell(d) - A_inf`, not
`A_cell(d)`.** The card's bare `c * r^d` is the special case `A_inf = 0`, i.e.
it asserts that the dominant (Perron) mode is *exactly side-symmetric on these
pools*. That is a measurable claim, not an assumption, and nothing in L205 or
L209 ever measured it. `A_inf` is computable directly from the right Perron
vector `v1` — the scalar `c1` and the normalisation of `v1` both cancel in the
ratio, so `A_inf` needs no eigen-coefficient, only `v1` itself.

This correction is not cosmetic. L209's stored `|A_cell|` per-hop ratios are
.662/.517 (cutwA Ti) and .667/.506 (f4wA Ti) — **not constant**, which a true
`c r^d` forbids — and on Tr they are 1.94/2.32 and 2.96/2.15, i.e. **greater
than one**, because Tr crosses zero. A ratio-of-levels on a signal with a
nonzero asymptote is uninterpretable, and on a sign-crossing one it is not
even bounded. Fitting `c r^d` to a sign-crossing series is the error this card
would otherwise commit.

## PREMISE CORRECTION 0b — quantities already derivable from stored artifacts

Per Kriegeskorte 2009 (digested tick 243) and the L214 rule: registration
after observation buys a decision rule, never inference. The depth-1..3
`A_cell` values are stored in `l209/static.json` and I read them while scoping
this card. Therefore the **successive-difference ratios at d=1..3** are
OBSERVED-DERIVABLE and are declared DESCRIPTION, not evidence. I state them
here in full so no later number can be presented as a surprise:

    ratio_12_3 := (A(3)-A(2)) / (A(2)-A(1))

    cutwA beta   Ti 0.945853   Tr 0.868966
    f4wA  beta   Ti 0.990024   Tr 0.861006
    cutwA crofts Ti 0.099544   Tr 0.824643
    f4wA  crofts Ti 0.540945   Tr 0.823641

(Under the corrected model `A(d) = A_inf + K rho^d`, successive differences
are `K rho^d (rho-1)` and their ratio is exactly `rho`, with `A_inf` cancelling
— which is why this three-point quantity is the cheapest preview of the
registered statistic and why it must be declared.)

Also already known: **L210 measured lam2/lam1 = 0.8928793607351002** on the
f4wA anatomical operator (Hotelling deflation, converged, rel spread 3.09e-10).
The f4wA *beta* operator of L209 is that same operator up to the scalar gain
`g_f4wA` (lam1 200.51080275455487 x 0.15051452517509462 = 30.179788269078884),
and a spectral RATIO is invariant to a global rescaling (L209's own no-op law).
So the f4wA-beta gap is NOT an unknown of this card.

**What is genuinely unknown when this file is written**, and therefore what
the branches may rest on:

1. `A_inf` on any pool (never computed on any card).
2. `A_cell(d)` for d = 4..8 (never computed).
3. The decay rate estimated in the ASYMPTOTIC range d=4..8.
4. lam2/lam1 for **cutwA** (either operator) and for the **Crofts** operator
   on either substrate — three of the four gaps are unmeasured.
5. Whether the subdominant eigenvalue is real at all on these operators
   (a complex pair does not converge under real deflation).

## The registered statistic

PRIMARY CELL: `(f4wA, beta, Ti)` — the same primary L209 used.

PRIMARY ESTIMATOR (deep range, asymptotic regime, unobserved):

    r_deep = exp( slope of OLS fit of log|A(d) - A_inf| on d, d = 4..8 )

reported with the fit residual (RMS of log residuals) and with the per-hop
successive-difference ratios at every depth so the reader sees the convergence
rather than a bare exponent.

SECONDARY ESTIMATORS, all reported for every substrate x operator x joint:

- `r_full` — the same fit over d = 1..8 (contaminated by higher modes at low d).
- `r_diff(d)` — the per-hop ratio of successive differences, d = 2..7.
- `r_bare` — **the card's literal model**, OLS of log|A_cell(d)| on d over
  d = 1..8 with its residual, so the card's own question is answered and its
  misspecification is shown rather than asserted.

SPECTRAL PREDICTION: `gap = |lam2| / lam1` of the SAME operator on the SAME
substrate, by Hotelling deflation (L210's machinery, sliced verbatim), with
convergence reported and NOT_CONVERGED returned as a non-number.

## Branches (on the PRIMARY cell, primary estimator)

- **(i) R_SPECTRAL** — `|r_deep - gap| / gap <= 0.10`. The homogenisation is
  one spectral number; that is a draft sentence.
- **(ii) R_ORDER** — not (i), but `0.5 <= r_deep/gap <= 2.0`. Order-only match.
- **(iii) R_OTHER** — `r_deep/gap` outside [0.5, 2.0]. The decay has another
  cause (most likely the pools' own recurrent mass, which the walks revisit).
- **R_DEGENERATE** (escape, declared in advance) — the deflation does not
  converge on the primary operator (complex subdominant pair), or the primary
  cell's `|A(d) - A_inf|` falls below 1e-12 inside d=4..8 so the log-fit is
  numerically empty. In either case no branch above is claimed and the card
  reports the failure mode with the non-converged range.

A branch is claimed ONLY on the primary cell. The other seven cells
(2 substrates x 2 operators x 2 joints, minus the primary) are a reported
TABLE, with agreement counted and NOT converted into a second branch.

## Predictions (scored as registered, never amended)

- **P1**: branch **R_SPECTRAL** on the primary cell.
- **P2**: `A_inf` is NOT zero on Tr under the beta operator — specifically
  `A_inf(Tr, f4wA, beta) > +0.05` (left-heavy), i.e. the card's bare model is
  refuted by a measured nonzero asymptote on at least one joint.
- **P3**: the gap is OPERATOR-SPECIFIC — `|gap_crofts - gap_beta| / gap_beta
  > 0.10` on at least one substrate.
- **P4**: cross-substrate agreement in the corrected currency —
  `|r_deep(cutwA) - r_deep(f4wA)| / r_deep(f4wA) <= 0.05` for beta/Ti
  (L209's "same ratios on two substrates" claim, re-asked properly).
- **P5**: my deflation reproduces L210's `lam2 = 26.94691005681583` and
  `gap = 0.8928793607351002` on `jv_abs_an` to FLOAT EQUALITY (same V1, same
  left iteration, same seed 21004, same machinery).

## Verify (halting gates, run BEFORE any L216 number is read)

- **CERT-178** (free, inside CERT-HEAD3): 420 stored L178 anatomical values at
  float equality.
- **CERT-205**: L205's table (2 joints x 7 substrates x 17 fields + 2 paired
  deltas) reproduced at FLOAT EQUALITY — re-run as in L209/L215.
- **CERT-209** (the card's own requirement): the depth-1..3 `A_cell` values of
  ALL 8 substrate x operator x joint cells reproduced from `l209/static.json`
  at **FLOAT EQUALITY** before any depth > 3 is read, together with L209's
  stored lam1 per substrate per operator and its norm no-op value.
- **CERT-GAP**: `lam2` and `gap` on `jv_abs_an` reproduced from
  `l210/static.json` at FLOAT EQUALITY (this is P5 and a gate at once; scored
  as a prediction, asserted as a gate).
- **NO-OP re-assert**: the lam1^d normalisation is re-measured as a no-op for
  `A_cell` at every depth 1..8 (L209's Q209-2 extended), max rel diff < 1e-10.
- Prior artifacts `l205/`, `l209/`, `l210/static.json` opened READ-ONLY with
  (size, mtime_ns) fingerprinted before and asserted unchanged after, plus
  `md5sum -c` green (L175: a lab verdict script is a SCRIPT, never a library —
  no lab module is imported).
- Verbatim source slices only, with INHERITED sha pins asserted by the builder
  against the values L209/L210 recorded, so a moved source HALTS the build.
