# L224 — the MASS-NEUTRAL statistic. PREREG (written BEFORE l224_tail.py existed)

Lane item: LANE.md `- [ ] L224. the MASS-NEUTRAL statistic`, ideas 109 (tick 242),
with the tick-243 (hour-21 research) field amendment folded onto the card.
Static, zero rollouts, zero settles, zero dynamics. Tick 255, 2026-11-23.

Parent: `l213/static.json` + `l213/addendum.json`. Substrates: the three L207/L213
BANC substrates `G0_closure`, `G1_cutwA`, `F4_f4wA`. Population: every PRESENT
descending cell with `m_out > 0` on that substrate (n = 1288 / 1264 / 1260, the
stored `population` block).

PRIMARY SUBSTRATE (registered): **G0_closure** (L213's first substrate, the
un-cut closure graph). All three are reported; the headline branch is read on
G0_closure and substrate disagreement is reported explicitly, never averaged.

---

## 0. PREMISE CORRECTIONS (all written before the generated script existed)

**0a — "reproduce l213/static.json's population R vector EXACTLY" is not
literally available: the artifact does not store the vector.** `l213/static.json`
stores only `population.{n, n_named, n_pure}` per substrate. The achievable —
and strictly stronger — gate is to RE-RUN L213's own population block as a
VERBATIM SOURCE SLICE (L211: certify by re-execution, never re-implementation)
and then assert, at float/int equality, **every stored leaf of
l213/static.json** except `runtime_s` (CERT-213), plus the three stored
`rho_R_vs_mout_population` values of `l213/addendum.json` recomputed through the
addendum's OWN expression `spearman_l([float(x) for x in R], [float(x) for x in
m_out])` (CERT-ADD). Those two gates pin the R vector, the population
membership, the lam1 values and the rank estimator together. Registered as
HALTING.

**0b — the k=1 case.** `R_k = P2/(lam1^2 * m_out^k)` at k=1 must be BIT-identical
to L213's inherited `R`, not merely close: `x ** 1.0 == x` exactly in IEEE754
(pre-verified on a 10,000-element probe, no data read), so the whole expression
is a float no-op. Registered as `np.array_equal` HALTING (CERT-K1). If it fails
at ulp level the finding is L218's law again (a mathematical no-op is not a
floating-point no-op) and is reported as such, never rounded away.

**0c — the card's Q3 changes TWO things at once.** The card asks whether the
actors' "UNMATCHED POPULATION percentile under R_k reproduces their mass-MATCHED
percentile under R (.05-.09 / .06-.07)". But the stored mass-matched percentile
is a WITHIN-CLASS 100-nearest-log-mass cohort (l213_addendum.py: `_ci` = the
actor's own pure_proj / non-pure_proj class, then the 100 nearest in log m_out).
So the card's comparison moves the COMPARISON SET (class cohort -> whole
population) *and* the STATISTIC (R -> R_k) in one step, which is exactly the
L222 cohort-relocation failure mode. Registered: measure the full 2x2 per actor
per substrate —

| | R | R_k* |
|---|---|---|
| whole population | `pct_pop_R` | `pct_pop_Rk` |
| within own class | `pct_cls_R` (= L213's stored `R_pct_in_class_raw`, GATED) | `pct_cls_Rk` |

and read **`pct_cls_Rk` vs the stored mass-matched `pct_mm_R`** as the PRIMARY
Q3 comparison (only the statistic changes), with the card's literal
`pct_pop_Rk` vs `pct_mm_R` reported as the COMPANION. Both are reported for both
actors on all three substrates.

**0d — OBSERVATION STATUS (Kriegeskorte 2009 / the L214 rule).** While scoping I
read `l213/static.json` and `l213/addendum.json`. Therefore the following are
DESCRIPTION and carry no branch: the population sizes; lam1 per substrate; both
actors' R, P2-derived R, m_out; `rho_R_vs_mout_population` = +0.5319431776009682
/ +0.5378751622578909 / +0.5447150100010776; the within-class raw percentiles
(.3179/.3358/.4075 carrier, .1442/.1525/.1531 mirror); the mass-matched
percentiles (.05/.08/.09 carrier, .07/.07/.06 mirror); `median_mout_pure` vs
`median_mout_nonpure`; the Q1/Q2/Q3 branches. Every branch below is placed on an
object the stored summaries do NOT determine: the fitted exponents, the
COMPONENT-SHUFFLED spurious baselines, the residual rho at any k != 1, the
neutralising exponent, and any R_k percentile.

Selection history, stated per Kriegeskorte: gi 1110 entered this chain because
L178 found it extreme on a depth-2 path statistic, and L206-L213/L222/L223
measured related path statistics on the same cell on the same graph. All
carrier/mirror percentiles here are DESCRIPTIONS OF A SELECTED CELL. L224's
Q1/Q2 legs are population-level and selection-free; only Q3 is about the actors.

**0e — Theil-Sen does not substitute for an errors-in-variables leg** (field
amendment (b), Forstmeier 2018). Registered estimator set: OLS (the card's
named primary), Theil-Sen (outlier-robust), RMA/reduced-major-axis
(errors-in-variables). RMA satisfies the algebraic identity
`k_RMA = k_OLS / |pearson_r|`, so it is registered as a GATE (CERT-RMA, rel diff
< 1e-12), not as an independent measurement, and `k_RMA >= k_OLS` is an
IDENTITY, not a prediction.

**0f — every registered escape SHORT-CIRCUITS** (L222): `K_DEGENERATE` returns
before any Q2/Q3 number on that substrate is read, and the degenerate flag
changes control flow rather than documenting it.

---

## 1. DEFINITIONS

- `P2(c)` = depth-2 pool reach from c, the inherited fast census (CERT-T gated).
- `m_out(c)` = `sub["om"][c]`, log1p-weighted out-mass.
- `R(c) = P2/(lam1^2 * m_out)` — L207's statistic, inherited verbatim.
- `R_k(c) = P2/(lam1^2 * m_out^k)`.
- `logm = log(m_out)`, `logp = log(P2)`. Cells with `P2 == 0` are EXCLUDED from
  the fit population (log(0)) and the excluded count is reported; if more than
  5% of a substrate's population is excluded that substrate is reported
  FIT-UNMEASURABLE and short-circuits (L222 false-by-unmeasurability).
- `rho(x, y)` = the inherited `spearman_l` (an AVERAGE-rank / midrank estimator,
  proven on THIS data by CERT-RANK before use — tick 252's law as a gate).
- Fast numpy midrank + Spearman kernels are admitted ONLY by gates: exact array
  equality against `rankvec` and relative difference < 1e-12 against
  `spearman_l` (summation order differs, so float equality is deliberately NOT
  claimed — the L206 expression law).

Seeds, registered now: `SEED_SPUR = 22401`, `SEED_BOOT = 22402`,
`B_SPUR = 2000`, `B_BOOT = 2000`.

---

## 2. REGISTERED QUESTIONS

### Q224-0 (REQUIRED FIRST LEG — field amendment (a), Pearson 1897 / Jackson & Somers 1991)

**The measured +0.53 is currently compared against ZERO, and zero is the wrong
null for an index correlated with its own denominator.** Measure the SPURIOUS
baseline by COMPONENT SHUFFLING: for each of `B_SPUR` draws, permute the P2
vector across cells (numerator and denominator decoupled, m_out held), form
`R_sh = P2_perm/(lam1^2 * m_out^k)` and compute `rho(R_sh, m_out)`. Report
median / p05 / p95 at k = 1 and at the fitted k*, and the PEARSON-CORRECTED
EXCESS `delta(k) = rho_measured(k) - median(rho_spurious(k))`.

This leg is read BEFORE any fit and BEFORE Q2's bar is scored.

### Q224-1 — the exponent

`k_OLS` = OLS slope of `logp ~ a + k*logm`; `k_TS` = Theil-Sen (median pairwise
slope); `k_RMA = sign(r)*sd(logp)/sd(logm)` (gated as an identity). Bootstrap
percentile CI (2.5/97.5) for `k_OLS` over `B_BOOT` cell resamples at
`SEED_BOOT`. Also `k_NEUT`: the exponent that zeroes `rho(R_k, m_out)` on REAL
data, by bisection on a bracket whose MONOTONICITY is gated (rho must be
monotone non-increasing on the grid actually used; a non-monotone bracket is
`K_DEGENERATE`).

### Q224-2 — the residual

`rho_resid(k) = rho(R_k, m_out)` reported at k = 1, `k_OLS`, `k_TS`, `k_NEUT`.
Registered bar (re-expressed per amendment (a)): the NEUTRALITY bar stays
`|rho_resid(k_OLS)| <= 0.05` — a descriptive property of the reparametrisation,
not a null test — and it is reported BESIDE `rho_spurious(k_OLS)` so that the
achieved zero is read against the nonzero value independent components would
give at the same exponent. A zero residual is a DESCRIPTIVE reparametrisation,
NOT a better model of the biology (the card's own registered caveat).

### Q224-3 — does the reparametrisation replace the mass match?

The 0c 2x2 per actor per substrate. PRIMARY: `|pct_cls_Rk* - pct_mm_R| <= 0.05`
for BOTH actors. COMPANION: the card's literal `|pct_pop_Rk* - pct_mm_R|`.
If Q224-3 fails, the registered conclusion is **"mass matching is
irreplaceable"**, never "R_k is wrong" (the card's own instruction).

---

## 3. BRANCHES (four cells, L109), read on G0_closure

- **K_DEGENERATE** — any primary fit not converged, or `k_OLS` outside
  [0.5, 3.0], or a non-monotone rho bracket, or a FIT-UNMEASURABLE substrate.
  Short-circuits (0f).
- **K_NEUTRALISES** — `|rho_resid(k_OLS)| <= 0.05` AND Q224-3 PRIMARY within
  0.05 for both actors.
- **K_PARTIAL** — exactly one of those two conditions holds.
- **K_FAILS** — neither holds.

## 4. PREDICTIONS (registered, scored)

- **P1** `k_OLS in [1.00, 2.00]` on all three substrates (P2 superlinear in
  out-mass — L213's lesson, never measured as an exponent).
- **P2** `median(rho_spurious(k=1)) <= -0.30`: with components decoupled the
  index anti-correlates strongly with its own denominator, so the stored +0.53
  UNDERSTATES the real P2-mass dependence relative to the correct null.
- **P3** `k_NEUT >= k_OLS` on all three substrates (Forstmeier predictor-noise
  attenuation biases the OLS slope LOW, so the neutralising exponent is larger).
- **P4** `|rho_resid(k_OLS)| <= 0.05` on G0_closure.
- **P5** branch is NOT `K_DEGENERATE`.
- **P6** Q224-3 PRIMARY FAILS on G0_closure: `max over actors |pct_cls_Rk* -
  pct_mm_R| > 0.05` — a single global exponent cannot reproduce a LOCAL mass
  match, so mass matching is irreplaceable.

`k*` for Q2/Q3 purposes = `k_OLS` (the card's named primary estimator),
registered now; `k_TS` and `k_NEUT` legs are reported beside it.

## 5. VERIFY (all HALTING, all before any L224 number is read)

- **CERT-213** — every stored leaf of `l213/static.json` except `runtime_s`,
  reproduced at float/int/str equality by a recursive leaf compare, by
  RE-EXECUTING L213's pipeline as a verbatim source slice.
- **CERT-ADD** — the three stored `rho_R_vs_mout_population` at FLOAT equality
  through the addendum's own expression.
- **CERT-207 (522)** and **CERT-T (272)** and CERT-F4 / CERT-178 (420) arrive as
  inherited verbatim source and re-run free.
- **CERT-RANK** — `rankvec` proven an average-rank (midrank) estimator on THIS
  data: every tie group shares one rank, rank sum == n(n+1)/2, #distinct values
  == #distinct ranks.
- **CERT-K1** — `R_k(1)` array-equal to the inherited R.
- **CERT-FAST** — numpy rank kernel exactly array-equal to `rankvec`; numpy
  Spearman within 1e-12 relative of `spearman_l`.
- **CERT-OLS** — at `k_OLS` the Pearson correlation between the log residual and
  `logm` is 0 to < 1e-10 (OLS orthogonality; gates the fit implementation).
- **CERT-RMA** — `k_RMA == k_OLS/|r|` to < 1e-12.
- **PARENT PIN** — `l213_tail.py` asserted a literal SUFFIX of `l213_static.py`
  and each inherited head slice asserted a literal substring of it, so CERT-213
  arrives as the code that ACTUALLY RAN.
- `md5sum -c l224/prior.md5` green before AND after; `l213/static.json`,
  `l213/addendum.json`, `l207/static.json` opened READ-ONLY with
  `(size, mtime_ns)` fingerprinted before and asserted unchanged after; no lab
  module imported (L175); forbidden-token audit on the generated script;
  exactly ONE write, to `l224/static.json`.

## 6. HONEST LIMITS (stated before measuring)

One population, one depth, one statistic, three non-independent substrates
sharing a graph. A power-law reparametrisation is biometry, not biology
(Pearson 1897 transfers because the mathematics is about ratios, not organs).
No dynamics, no operating point, no rollouts.
