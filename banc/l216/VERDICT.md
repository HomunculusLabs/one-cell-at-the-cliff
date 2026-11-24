# L216 VERDICT — the DEPTH-DECAY LAW

Branch **R_SPECTRAL** (registered), on the primary cell, at 0.17% error.
PREREG: `l216/PREREG.md` (written first, with the premise correction).
Artifacts: `l216/static.json`, `l216/run.out`, `l216/run.err`, `l216/build.out`.
Code: `l216_{build,head,tail}.py` -> generated `l216_static.py` (1,356 lines,
eight verbatim certified source slices + one head + one new tail).
35 s, CPU, zero rollouts / zero settles / zero dynamics.

## The headline

**The depth-decay of the side contrast IS one spectral number.**

    primary cell (f4wA, beta, Ti)
    r_deep  = 0.891375   (OLS of log|A_cell(d) - A_inf| on d, d = 4..8,
                          rms log residual 0.00338)
    gap     = 0.892879   (|lam2|/lam1, Hotelling deflation, converged,
                          rel spread 3.09e-10)
    |r - gap| / gap = 0.0017   against a registered 0.10 bar

Six of the eight substrate x operator x joint cells clear the same 10% bar;
all eight clear the factor-2 order bar. The two misses are both `cutwA`
Crofts cells (11.6% / 14.3%), discussed below.

## The premise correction was the whole card

The PREREG established, before any measurement, that `A_cell(d)` is a
normalised contrast whose limit is the **Perron asymmetry**
`A_inf = asym(per-cell means of v1)`, not zero, so the quantity decaying at
the spectral rate is `A_cell(d) - A_inf`. The card's literal `c * r^d` is the
special case `A_inf == 0`. That is now measured on both sides:

**(a) A_inf is large, positive and outside the handedness null.**

    f4wA  beta Ti  A_inf +0.28663  pct_abs 1.000  [null -0.0924, +0.0925]
    f4wA  beta Tr  A_inf +0.44422  pct_abs 1.000  [null -0.1190, +0.1163]
    cutwA beta Ti  A_inf +0.25698  pct_abs 1.000  [null -0.0865, +0.0908]
    cutwA beta Tr  A_inf +0.40652  pct_abs 1.000  [null -0.1098, +0.1070]

The asymptotic arrival distribution of the anatomical operator is **strongly
LEFT-heavy on every beta cell**, at the top of 2000 membership permutations.

**(b) The card's own model fits an order of magnitude worse and in the wrong
direction.** On the primary cell the bare fit gives `r_bare = 1.0725` — i.e.
*growth* — with rms log residual **1.15857** against the corrected fit's
**0.00338** (a 343x worse fit), and `r_bare > 1` on five of the eight cells.
Its per-hop level ratios on the primary cell are

    0.667, 0.506, 0.070, 12.145, 2.013, 1.464, 1.289

which is not an exponential at all. This is the misspecification *measured*
rather than asserted.

## The correction overturns L209's reading of its own number

L209 reported (and the L216 card quoted) that the Ti asymmetry "decays, it
does not merely fail a bar — roughly a halving per hop... a deep static
handedness is not merely absent, it is *erased* by depth." Extended to
depth 8, the primary series is

    d:      1        2        3        4        5        6        7        8
    A_cell -0.09569 -0.06382 -0.03228 -0.00226 +0.02741 +0.05519 +0.08083 +0.10418

It does **not** decay to zero. It **crosses zero at d ~ 4** and climbs
monotonically toward `A_inf = +0.2866`. The "halving per hop" was the signal
passing through zero on its way from the depth-1 right-heavy drive to a
left-heavy asymptote, and the apparent halving is an artifact of taking
ratios of levels across a sign change. Nothing in L209's *stored numbers*
changes (all 412 of them reproduced here at float equality); the sentence
built on them does.

The same correction dissolves L209's "unregistered and kept: the trochanter
INVERTS with depth" as a **Tr-specific** finding. Tr inverts earlier
(`A_inf` +0.444 vs Ti's +0.287, and Tr crosses between d1 and d2) but Ti does
exactly the same thing three hops later. The Ti/Tr dissociation at depths 2-3
is a difference in *crossing phase*, not a difference in kind. **This bears
directly on L217**, whose whole object is "the Tr DEEP INVERSION" — it should
now be posed as *when* each joint crosses, not *whether* Tr is special.

## Why the cross-substrate agreement happens (L209's open claim, answered)

L209 observed the two substrates agreeing to three decimals in ratio while
differing in level and inferred "operator mixing". In the corrected currency
that claim is both sharper and explained:

    r_deep(cutwA, beta, Ti) = 0.892089      gap(cutwA, beta) = 0.898176
    r_deep(f4wA,  beta, Ti) = 0.891375      gap(f4wA,  beta) = 0.892879
    |difference| / r_deep(f4wA) = 0.0008

The substrates agree because **their spectral gaps agree** (0.8982 vs 0.8929,
0.6% apart): the syn>=4 floor removes 27% of the edges and barely moves the
subdominant ratio. The decay is a property of the operator's spectrum, which
is what "operator mixing" should have meant.

## P3 refuted: the gap is NOT strongly operator-specific, yet the misses are

    |gap_crofts - gap_beta| / gap_beta:  cutwA 0.0660,  f4wA 0.0925

Both below the registered 0.10, so **P3 is FALSE** as registered. The Crofts
reweighting moves the gap by only 7-9% — the two operators homogenise at
similar rates even though their lam1 differ by three orders of magnitude.

And yet the only two cells that miss the 10% bar are `cutwA crofts` Ti
(r_deep 0.8465 vs gap 0.9574) and Tr (0.8206 vs 0.9574) — both decaying
*faster* than their gap. The internally consistent reading is visible in the
same table: `cutwA crofts Ti` is the one cell whose `A_inf` is indistinguishable
from zero (**-0.0084, pct_abs 0.178**, inside the null). Where the Perron mode
carries no side contrast, the residual is not dominated by a single
subdominant mode and a third mode sets the observed rate — which is exactly
branch (iii)'s stated alternative, appearing as a *cell* of the table rather
than as the branch. Reported, not explained away.

## Predictions: 4 of 5, registration NOT amended

- **P1 TRUE** — R_SPECTRAL on the primary cell (rel 0.0017).
- **P2 TRUE** — `A_inf(Tr, f4wA, beta) = +0.44422 > 0.05`; the bare model is
  refuted by a measured nonzero asymptote.
- **P3 FALSE** — 0.0660 / 0.0925, both under the registered 0.10.
- **P4 TRUE** — cross-substrate r_deep agreement 0.0008 <= 0.05.
- **P5 TRUE** — L210's `lam2 = 26.94691005681583` and
  `gap = 0.8928793607351002` reproduced at FLOAT EQUALITY (and the f4wA beta
  gap computed independently here agrees with it to rel 1.24e-16, confirming
  the registered scale-invariance argument).

## Method lesson (transportable)

**A convergence-level bar must be DERIVED from the iteration's own measured
convergence, never fixed in advance.** The first run halted on
`|lam1_left - lam1_right| / lam1_right < 1e-9` for `cutwA crofts`: the beta
operators converge to rel spread 1.4e-16 while the Crofts operators converge
only to 4e-10 / 1.3e-08, and a power iteration cannot agree with its transpose
to better than its own convergence. The bar is now
`max(1e-9, 1e3 * max(spread_right, spread_left))` and both spreads are logged
beside every comparison. This is a *tooling* correction made after the PREREG
and is disclosed as such — it changes no registered quantity (the measured
left/right disagreements are 2.10e-09 and 2.35e-09 against derived bars
4.19e-07 and 1.32e-05).

Second, smaller: **the cheapest preview of a decay rate is the ratio of
successive differences, because the asymptote cancels.** On the primary cell
`r_diff` reads 0.990, 0.952, 0.988, 0.936, 0.923, 0.911 — already circling the
gap at depth 2, where the ratio of *levels* read 0.667. The PREREG declared
those d=1..3 values DESCRIPTION because they were derivable from
`l209/static.json` before this card ran (Kriegeskorte 2009); the registered
estimator lived at d=4..8, which was unobserved.

## Verification

- **CERT-178** (free, in CERT-HEAD3): 420 stored L178 anatomical values at
  float equality.
- **CERT-205**: **250** stored L205 values at FLOAT EQUALITY (2 joints x 7
  substrates x 17 fields + 2 paired deltas).
- **CERT-GAP** (halting, and P5 at once): **10** stored L210 values at FLOAT
  EQUALITY — `lam2`, `gap`, `lam1`, the convergence spread and all six growth
  factors — reproduced from `jv_abs_an` with L210's own V1, left vector and
  seed 21004, via the deflation function sliced verbatim.
- **CERT-209** (the card's required anchor): **412** stored L209 values at
  FLOAT EQUALITY (8 cells x 3 depths x 17 fields + 4 lam1 + substrate sizes)
  **before any depth > 3 was read** — the depth-1..3 sweep is run and gated
  first, then the depth-1..8 sweep is run and re-asserted to agree with the
  certified one at every certified depth.
- **CERT-GEN / CERT-F4 / CSR orientation / pool sizes** re-run free inside the
  verbatim heads; `L205 substrate edge counts` and `pool sizes invariant
  across all 7 substrates` green.
- **NO-OP**: the lam1^d normalisation re-measured as a no-op for `A_cell` at
  all 8 depths (max rel diff 7.19e-14 over 64 cells).
- Eight VERBATIM source slices, forbidden-token audited, **six INHERITED sha
  pins** asserted by the builder against the values L209/L210 recorded in
  their own banners (including `l209_tail.py`'s WHOLE-FILE sha
  31a28283be618de0) so a moved source HALTS the build; no lab module imported
  (L175); generated sha `d1bb1b48595745fa`.
- Prior artifacts `l209/static.json` and `l210/static.json` opened READ-ONLY
  with (size, mtime_ns) fingerprinted before and asserted unchanged after;
  `md5sum -c l216/prior.md5` green against the pre-run hashes of
  `l205/`, `l209/`, `l210/static.json`.

Total halting float equalities before any L216 number was read: **672**
(250 + 10 + 412), plus 420 CERT-178 and 44 CERT-GEN inherited free.

## Limitations

See `l216/static.json["limitations"]` — anatomical leg only (not an operating
point, L164); walks with revisits, not paths; `r_d = A^d 1` is source-free;
`A_inf` is exact only in the limit, so any gap to `A_cell(8)` is
pre-asymptotic residue; real Hotelling deflation cannot represent a complex
subdominant pair (all four operators converged, so R_DEGENERATE never fired);
the d=1..3 difference ratios are DESCRIPTION, not evidence; no neuromere
column exists on BANC.
