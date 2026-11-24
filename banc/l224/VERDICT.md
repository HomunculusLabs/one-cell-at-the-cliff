# L224 — the MASS-NEUTRAL statistic. VERDICT

Tick 255, 2026-11-23. PREREG `l224/PREREG.md` (written first, six premise
corrections). Static, zero rollouts, zero settles, zero dynamics.
Generated scripts: `l224_static.py` (sha256 `4df587a0dc143358`, 1,730 lines),
`l224b_static.py` (sha256 `04c72ce89009b08e`, addendum).

## BRANCH: **K_DEGENERATE** — a REGISTERED escape, fired and short-circuited

`FIT-UNMEASURABLE`: the P2 == 0 exclusion fraction is **0.0978 / 0.1013 /
0.1508** (G0_closure / G1_cutwA / F4_f4wA) against a registered bar of 0.05.
**The card's primary estimator family is undefined on a tenth to a sixth of its
own population.** `log(P2)` does not exist for 126 / 128 / 190 of the 1288 /
1264 / 1260 present descending cells, so a log-log fit of P2 on m_out can only
be computed on a subpopulation SELECTED ON ITS OWN OUTCOME. The escape
short-circuited before any fit, exponent, residual or percentile was read
(premise correction 0f: a registered escape must change control flow).

Predictions: **P5 FALSE** (the branch IS degenerate). P1-P4 and P6 are
**UNSCORED BY ESCAPE** and are recorded as such — never as nulls (L222's
false-by-unmeasurability discipline). The addendum values that *would* have
scored them are reported below as POST-HOC description.

## The addendum (declared POST-HOC, unregistered, no branch, no bar)

### (A) The exclusion is not random — it is selection on the outcome AND on the class flag

| | G0_closure | G1_cutwA | F4_f4wA |
|---|---|---|---|
| cells with P2 == 0 | 126 / 1288 | 128 / 1264 | 190 / 1260 |
| median m_out, zero vs non-zero | 18.59 vs 97.31 (5.24x) | 18.59 vs 94.98 (5.11x) | 13.63 vs 84.05 (6.17x) |
| rho(1[P2>0], m_out) | +0.3909 | +0.3961 | +0.4664 |
| zero fraction, pure_proj vs non | 0.139 vs 0.066 | 0.146 vs 0.069 | 0.213 vs 0.105 |

The dropped cells are systematically LOW out-mass, and the zero rate is **2x
higher in `pure_proj`** — the very class flag whose contrast L213 measured. So
the card's exclusion would have been correlated with both the predictor and the
grouping variable.

### (B)+(C) THE HEADLINE: the EXCLUSION moves the exponent ~14-22x more than the ESTIMATOR does

| | k_NEUT full (no exclusion) | k_NEUT subpop | k_OLS subpop | k_TS | k_RMA |
|---|---|---|---|---|---|
| G0_closure | **1.9528** | 1.5935 | 1.5682 [1.4902, 1.6490] | 1.5811 | 2.0854 |
| G1_cutwA | **2.0057** | 1.6093 | 1.5835 [1.5050, 1.6682] | 1.5972 | 2.1120 |
| F4_f4wA | **2.1719** | 1.5154 | 1.4858 [1.4088, 1.5643] | 1.5057 | 2.0081 |

Restricted to the SAME cells, rank-bisection and log-log OLS agree to
**+0.0253 / +0.0258 / +0.0296**. Adding the zeros back moves the exponent by
**+0.3593 / +0.3965 / +0.6565** — 14x, 15x and 22x the estimator difference.
All three OLS bootstrap CIs (2000 resamples, seed 22402) EXCLUDE the
exclusion-free value.

`k_NEUT` is the exclusion-free instrument because `R_k = P2/(lam1^2 m_out^k)`
is **exactly 0 for every k** whenever P2 == 0: those cells hold a tied bottom
rank at every exponent, so the bisection is defined on the whole population.
Gated: the R_k zero SET is k-invariant over k in [0, 6] (no underflow ties),
rho(k) is monotone on the grid actually used, and rho at k=1 **IS** L213's
published +0.5319431776009682 to < 1e-12.

Secondary, worth a line: the errors-in-variables correction and the exclusion
removal land in the same place from different directions — `k_RMA = k_OLS/|r|`
(|r| = 0.752 / 0.750 / 0.740) gives 2.0854 / 2.1120 / 2.0081 against
k_NEUT_full 1.9528 / 2.0057 / 2.1719, within 0.13 / 0.11 / 0.16. Two
independent corrections, one answer near k ~ 2. Agreement-grade, not an
identity.

### (D) Pearson 1897 confirmed, and the correct null is NOT zero

Component shuffling (P2 permuted across cells, m_out held, 2000 draws,
seed 22401), full population:

| k | measured rho | SPURIOUS median [p05, p95] | Pearson-corrected excess |
|---|---|---|---|
| 0 (control) | +0.7995 | **-0.0000** [-0.0471, +0.0451] | +0.7995 |
| 1 (L213's published +0.5319) | +0.5319 | **-0.3635** [-0.4020, -0.3244] | **+0.8955** |
| 1.5682 (k_OLS) | +0.2155 | -0.4985 | +0.7139 |
| 1.9528 (k_NEUT) | -0.0000 | **-0.5651** | **+0.5651** |

(G1 and F4 agree: spurious at k=1 of -0.3573 / -0.3405, excess +0.8951 /
+0.8852.) The k=0 arm is the built-in positive control — with no denominator
the shuffled index is uncorrelated with m_out to four decimals, which is what
makes -0.3635 legible as the denominator's own footprint rather than an
artifact of the shuffle.

**So L213's +0.53 UNDERSTATES the real P2-mass dependence by 1.68x against the
correct null.** And at the neutralising exponent the index reads exactly zero
while independent components would read **-0.5651** — a "mass-neutral"
statistic is neutral in the measured currency and **+0.5651 away from
independence of its own components**. That is the card's registered caveat
("a k that zeroes the residual rho is a DESCRIPTIVE reparametrisation and not a
better model of the biology") with a number on it.

Also visible: `|rho_resid(k_OLS)|` = **+0.2155** on the FULL population versus
~0.025-worth of residual on the subpopulation it was fitted to. An exponent
fitted on an outcome-selected sample does not neutralise the population it was
meant to describe.

### (E) Q224-3: mass matching is IRREPLACEABLE (the card's own registered conclusion for a failure)

Premise correction 0c's 2x2, G0_closure, at the exclusion-free k* = 1.9528:

| actor | mass-matched R | raw class R | class R_k | d(primary) | pop R | pop R_k | d(companion) |
|---|---|---|---|---|---|---|---|
| carrier | 0.0500 | 0.3179 | 0.1911 | **0.1411** | 0.2430 | 0.1607 | 0.1107 |
| mirror | 0.0700 | 0.1442 | 0.1209 | 0.0509 | 0.2065 | 0.1421 | 0.0721 |

A single global exponent recovers roughly HALF the distance from the raw
within-class percentile to the mass-matched one and stops: 0.3179 -> 0.1911
against a target of 0.0500. At k_OLS it is worse (0.2393, d 0.1893). The
mirror lands closer (d 0.0509) — consistent with its mass-matched cohort
having been tight already (log-mass spread 0.138 vs the carrier's 0.530). All
three substrates agree in direction and magnitude.

## METHOD LAWS (the transportable part)

1. **A ZERO in the outcome is a MODEL-FAMILY verdict, not a missing value.**
   Before fitting any power law by logs, measure the outcome's zero fraction
   AND the zeros' covariance with the predictor and with every grouping
   variable the card will use. Here the zeros are 9.8-15.1% of the population,
   5.1-6.2x lower in mass, and 2x enriched in one of the two classes under
   test.
2. **When an estimator needs an exclusion and a rival does not, the
   EXCLUSION is the comparison worth making — not the estimators.** Measured
   here: estimator-vs-estimator on identical cells differs by 0.025-0.030,
   while the same estimator with and without the excluded cells differs by
   0.359-0.657. Report both decompositions or you will attribute a sample
   effect to a method choice.
3. **A statistic "neutralised" against its own denominator is still far from
   independence of its components,** and the component-shuffling null is what
   says how far (here: zero vs a spurious -0.5651). Report the achieved zero
   AND the spurious baseline at the SAME exponent.
4. **A coverage bar on a certification must be DERIVED FROM THE ARTIFACT,
   never guessed.** (Self-inflicted, disclosed below.)

## GATES (all HALTING, all before any L224 number was read)

- **CERT-213 = 289** stored leaves of `l213/static.json` (every key except
  `runtime_s`) reproduced at float/int/str equality by a recursive leaf compare,
  and reproduced by RE-EXECUTING L213's pipeline as a **verbatim source slice**
  (`l213_tail.py` lines 1-430, its runtime stamp and its writer CUT) rather
  than by re-implementing it (the L211 lesson). Coverage is proven, not
  assumed: the comparator's visit count is asserted EQUAL to a leaf count
  computed from the stored artifact itself.
- **CERT-ADD = 33** — `l213/addendum.json`'s three `rho_R_vs_mout_population`,
  its per-class rhos, and both actors' within-class RAW and MASS-MATCHED
  percentiles, all at FLOAT equality through the addendum's own expressions.
  This is what pins the population R vector (premise correction 0a: the stored
  artifact does not contain the vector).
- **CERT-RANK = 18** — the inherited `rankvec` PROVEN an average-rank (midrank)
  estimator on this data before any rank statistic is read: no tie group split,
  rank sum == n(n+1)/2, #distinct values == #distinct ranks. Tick 252's law as a
  gate, not a memory; argsort-of-argsort would fail the tie-group check.
- **CERT-K1 = 6** — `R_k(k=1)` `np.array_equal` to the inherited R on all three
  substrates (`x ** 1.0` verified a float no-op on a 10,000-element probe before
  the card was written).
- **CERT-FAST = 15** — the numpy midrank kernel EXACTLY array-equal to
  `rankvec` on all twelve population vectors, and the numpy Spearman within
  **0.00e+00** relative of `spearman_l`.
- **CERT-OLS / CERT-RMA** — OLS residual orthogonality < 1e-10 and the
  identity `k_RMA == k_OLS/|r|` < 1e-12, so RMA is a GATE and `k_RMA >= k_OLS`
  is an identity rather than a prediction (premise correction 0e).
- **CERT-224 = 19 / CERT-ZK = 18** (addendum) — the parent's stored
  branch-bearing values at float/int equality before any addendum number was
  read; the R_k zero set k-invariant over k in [0, 6]; the k=1 full-population
  rho equal to L213's published value.
- Inherited and re-run FREE inside the slice: CERT-178 (420), CERT-207 (522),
  CERT-F4, CERT-T (272, max rel 9.05e-16), the three stored gains, the CSR
  orientation, all 20 pool sizes.
- **PARENT PIN** — `l213_tail.py` asserted a literal SUFFIX of
  `l213_static.py` (sha256 `7131bfef8d6e4ac8`) and all six head slices
  asserted literal substrings IN ORDER with no trailing bytes, which is what
  proves CERT-213 arrives as the code that ACTUALLY produced
  `l213/static.json`.
- Addendum construction: `l224b_static.py` is a literal PREFIX of
  `l224_static.py` (lines 1-1427), cut immediately BEFORE the registered
  short-circuit, with the prefix asserted to contain **ZERO writes** — so the
  addendum cannot touch the parent artifact. Every parent gate re-ran free in
  3.4 s of addendum time.
- Negative audit: exactly three writes in the parent, all to
  `l224/static.json`; exactly one in the addendum, to `l224/addendum.json`;
  fifteen inherited function bodies asserted NOT re-transcribed; no lab module
  imported (L175); forbidden-token audit green; `ast.parse` on both generated
  files.
- `md5sum -c l224/prior.md5` (10 files) GREEN before and after;
  `l224/parent.md5` GREEN after the addendum; `l213/static.json`,
  `l213/addendum.json` and `l224/static.json` opened READ-ONLY with
  `(size, mtime_ns)` fingerprinted before and asserted unchanged after.

## SELF-INFLICTED FAILURES, DISCLOSED (both caught by this card's own gates)

1. **`assert _n213 >= 400` halted the first run at 289.** The bar was a
   GUESSED magnitude about another card's artifact — the same error shape as a
   fixed convergence bar (L216). Repaired by DERIVING the bar from the artifact
   itself (count the stored leaves, require exact coverage), which is strictly
   stronger than the guess it replaced. It halted before any L224 number was
   read, so no registered quantity was affected. Evidence kept at
   `l224/run_attempt1.{out,err}`.
2. **The addendum prefix cut at line 1428 included the escape's leading
   comment,** failing the builder's "prefix ends at the FIT block" assert
   (cut moved to 1427). An off-by-one caught for free by a structural gate
   rather than by a wrong number.

Also disclosed: the first launch used the system `python3`, which has no
pandas; the lab venv `~/critters/peabrain/.venv/bin/python` is required.

## HONEST LIMITS

One population, one depth (P2), one statistic, one weighting (log1p), three
substrates that share a graph and most cells and are therefore NOT three
independent replications. No dynamics, no operating point, no rollouts. The
component-shuffling null destroys any real covariance between numerator and
denominator — it bounds what an index gives under independence, it does not
model the biology. `k_NEUT` is a descriptive reparametrisation, not a model.
Both actors' percentiles are DESCRIPTIONS OF A SELECTED CELL (Kriegeskorte
2009): gi 1110 entered this chain because L178 found it extreme on a related
depth-2 statistic. This is biometry, not connectomics — it transfers because
the mathematics is about ratios, not organs (Pearson 1897).

Refs: Pearson 1897 Proc R Soc 60:489-498; Jackson & Somers 1991 Oecologia
86:147-151; Forstmeier 2018 bioRxiv 10.1101/298786; Atchley et al 1976 Syst
Zool 25:137-148; Kriegeskorte et al 2009 Nat Neurosci 12:535-540.
