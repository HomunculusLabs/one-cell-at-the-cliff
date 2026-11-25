# L235 PREREG — the CURRENCY-INVERSION audit, asked NONSELECTIVELY

Registered 2026-11-24 ~07:30 EST (tick 267), BEFORE any cohort-level number
was computed. Static, zero rollouts, zero settles, zero RNG beyond the
certified per-draw rebuild that already exists in the parent's REB.

## The question

L218 placed its carrier at percentile **0.940** in the scale-invariant
currency A2 = K2/K and at **0.100** in the bare unit-L2 currency |u2[c]| —
same cell, same 100 draws, opposite sides. That reading was taken on the cell
SELECTED for being extreme (Kriegeskorte 2009 step 1 violated), so the
inversion is currently a description. Ask it nonselectively over all **35**
actors of the L178 cohort against the SAME 100 l169c draws.

## Premise corrections (registered first; ZERO amendments to any registered quantity)

- **0a. The actor set.** `ACTORS` in the parent is the 35-actor L178 cohort
  (carrier + rank-4 twin + 33 family cells), and the parent's own
  `assert len(ACTORS) == 35` is what proves it. Every statistic below is
  computed for all 35, carrier included.
- **0b. The two currencies are NOT two independent instruments — they differ
  by an IDENTITY.** `coeff(u, v, c) = u[c] * v[POOL].sum() / (u . v)` and the
  pool sum is **actor-independent**, so within a draw k
  `A2_k(c) = (u2_k[c] / u1_k[c]) * C_k` with
  `C_k = (S_v2_k/(u2_k.v2_k)) / (S_v1_k/(u1_k.v1_k))` the SAME constant for
  every actor. The scale-invariant currency is therefore the bare currency
  divided by u1[c], times an actor-independent per-draw constant. Registered
  consequence: `pct_u1` is a THIRD percentile that must be measured, the
  identity is asserted in code (not correlated), and the card reports a
  four-step LADDER pu2 -> pR -> pA2abs -> pA2 isolating (i) the u1 division,
  (ii) the per-draw constant, (iii) the sign.
- **0c. A2 is SIGN-INDEFINITE and |u2| is sign-definite by construction**
  (L234's law). L218's published pair is therefore a SIGNED percentile against
  an ABSOLUTE one. Both forms are registered: `pA2` (signed, the published
  form, PRIMARY because it is the one that produced the 0.940) and `pA2abs`
  (the currency-matched companion). The sign step is the ladder's third rung.
- **0d. u1 is strictly positive by Perron-Frobenius**, so its null cannot
  straddle zero and `pct_u1` signed == absolute (L234's sign law, applied in
  advance rather than discovered).
- **0e. Resolution floor.** 100 draws cap every percentile at 0.01; the
  registered disagreement bar of 0.5 is 50x the floor, so the bar is not
  resolution-limited. `pct == 0.0` means "below all 100 draws" and nothing
  finer.
- **0f. Rank statistics are MIDRANK** (L221), by the certified `midrank` /
  `spearman` slice from l231_tail.py, with the distinct-value count printed
  for every rank statistic (L227: percentiles over 100 draws take at most 101
  values, so ties are expected and cap a rank correlation below its analytic
  value).
- **0g. The disclosure the card itself names.** Unit-L2 normalisation of u2 on
  two DIFFERENT operators is a CONVENTION, not a canonical comparison. A
  cohort-wide disagreement rate is therefore a statement about the convention
  and is NOT evidence either currency is "wrong"; the scale-invariant A2 stays
  the branch-carrying form by construction, in this card and in L218.
- **0h. Selection.** The carrier's own numbers are DESCRIPTION (it was
  selected on a related statistic); the inferential objects are the cohort
  rate, the cohort rank correlations and the ladder means over 35 actors.
- **0i. The cost slice is an INTERVENTION until measured (L226).** SLICE A is
  cut at line 1624, i.e. immediately BEFORE the parent's own per-draw
  deflation loop (372 s), and this card's own loop replaces it while
  capturing all 35 actors instead of one. That is admitted ONLY by exact
  reproduction of the stored carrier results: l218/static.json's entire
  `Q218_3_u2` draw block, l218's `Q210_2_bare` u1 block, `Q210_1_primary`'s K
  percentile, and l234/static.json's 100 stored per-draw K2 values, all at
  FLOAT EQUALITY (CERT-235B, halting). If any one of them fails the run
  halts and the card reports a blocker.

## Registered quantities

Per actor c (35) over the 100 l169c draws:
`pA2 = mean(A2_k(c) < A2_real(c))`, `pA2abs` (absolute form), `pu2 =
mean(|u2_k[c]| < |u2_real[c]|)`, `pu1 = mean(u1_k[c] < u1_real[c])`,
`pR = mean(|u2_k[c]/u1_k[c]| < |u2_real/u1_real|)`, `pK`, `pK2`.
Disagreement `D(c) = |pA2 - pu2|`, companion `Dabs(c) = |pA2abs - pu2|`.
Ladder rungs `s1 = |pR - pu2|`, `s2 = |pA2abs - pR|`, `s3 = |pA2 - pA2abs|`.

## Branch (registered bars, no post-hoc movement)

- `rate = mean(D > 0.5)` over the 35 actors.
- `rate >= 0.25` -> **I_CONVENTION**: the inversion is a property of the two
  normalisations, the L218 method law generalises, and the publishable
  reading is "a scale-invariant and a bare percentile are different
  currencies cohort-wide".
- `rate <= 3/35` AND the carrier disagrees -> **I_CARRIER**: the inversion is
  a property of the carrier's own u1 suppression and the publishable reading
  is about THAT cell, not about the currencies.
- otherwise -> **I_MIXED**: report the rate and the ladder, publish neither
  generalisation.

## Predictions (registered before the loop ran)

- **P1** branch == I_CONVENTION (rate >= 0.25).
- **P2** midrank Spearman(pA2, pu2) over 35 actors lies in [-0.5, +0.5] (the
  two currencies are not rank-equivalent).
- **P3** the 0b identity holds for every actor x draw at relative error
  <= 64 eps (3,500 assertions, halting).
- **P4** the carrier's D ranks in the TOP 5 of 35 (descending).
- **P5** mean(s1) > mean(s2): the u1 division moves the percentile more than
  the actor-independent per-draw constant does.
- **P6** mean(s3) >= 0.05: the sign step is not negligible cohort-wide
  (L234's sign law generalises past the carrier).

## Limitations registered in advance

One substrate (f4wA), one operator (|g*W_beta|), one null family (the l169c
destination swaps), one graph (BANC v626 cord-free f4wA block); L207's
cross-null law applies. 100 draws. The cohort is L178's 35 actors, which is
itself a selected family (DN-adjacent), so "cohort-wide" means within that
family. No new eigen-decomposition machinery: modes 1 and 2 only.
