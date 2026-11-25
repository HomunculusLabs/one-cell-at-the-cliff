# L235 VERDICT — the currency inversion is ONE CELL's u1 suppression

Branch **I_CARRIER**. Predictions **4 of 6** TRUE; the one that matters (P1)
is FALSE and it is the card. Static, zero rollouts. Run 548.7 s on om,
`nice -n 15 timeout 1700`, peabrain venv. Artifact `l235/static.json`.

## Q235-1 (PRIMARY): asked nonselectively, the inversion does NOT generalise

Over all **35** L178 actors against the SAME 100 l169c draws, the registered
disagreement `D = |pA2 - p|u2||` exceeds the registered 0.5 bar for
**1 of 35** actors — `rate = 0.0286` against the registered `>= 0.25` bar for
I_CONVENTION and `<= 3/35` for I_CARRIER — and the one actor **is the
carrier** (D **0.840**, pA2 0.940 vs p|u2| 0.100, rank **1 of 35**). Second
place is fam30_1557 at 0.44; the cohort **median D is 0.070**, mean 0.120.
The absolute-matched companion gives the same 1/35.

So **BRANCH = I_CARRIER**, and per the PREREG the publishable reading is the
one about that CELL: L218's law ("a statistic's scale-invariant form and its
bare unit-norm form can place the same cell on OPPOSITE sides of the same
null") is true as stated but its SCOPE is now measured — it is not a generic
property of the two normalisations across this cohort, it is what happens
when the denominator of the scale-invariant form is itself extreme.

**The carrier is the UNIQUE cell whose u1 percentile is 0.000** (below all
100 draws) in a cohort whose pu1 runs 0.000 - 0.920 with median **0.310**;
it is likewise the unique `pK == 0.0` cell. That is the whole mechanism.

## Q235-3 (the ladder): for the carrier it is 100% the u1 rung

PREREG 0b registered the two currencies as related by an IDENTITY, not as two
independent instruments: within draw k,
`A2_k(c) = (u2_k[c] / u1_k[c]) * C_k` with `C_k` the SAME constant for every
actor. Asserted per actor per draw — **3,500 checks, max relative error
5.682e-16 against a 64-eps bar of 1.421e-14** (P3 TRUE).

The four-rung ladder `p|u2| -> pR -> pA2abs -> pA2` therefore decomposes the
published disagreement exactly:

- carrier: **s1 (u1 division) = 0.840, s2 (per-draw constant) = 0.000,
  s3 (sign) = 0.000** — pA2 == pA2abs == pR == 0.940. Every bit of the 0.840
  is the division by u1.
- cohort means: s1 **0.0769** > s2 **0.0471** (P5 TRUE) > s3 **0.0429**.
  s2 is nonzero on 32 of 35 actors, s3 on only **8 of 35** (max 0.46 on
  fam30_1557) — P6 FALSE by 0.0071 against the registered 0.05 bar.
- `C_k` is nearly constant across the null: **[0.7066979, 0.7086156]**,
  median 0.7071822, 0.027% spread, **never negative** in 100 draws. So the
  scale-invariant currency IS the bare currency divided by u1 to four digits,
  measurable before any null is run.

## Q235-2 (rank, MIDRANK per L221): the currencies are not rank-equivalent

Spearman(pA2, p|u2|) = **+0.248385** (24/24 distinct values) — inside the
registered [-0.5, +0.5] (P2 TRUE). The absolute-matched form rises to
**+0.554487**, so the SIGN currency — which fires on only 8 of 35 cells —
carries a large share of the rank discordance. Once u1 is divided out the
remaining constant barely re-ranks anything: Spearman(pR, pA2abs) =
**+0.908817**.

**Spearman(pu1, D) = +0.014456.** The identity-level mediator has
essentially ZERO cohort rank correlation with the outcome it fully explains
in the one case where the outcome exists, because 34 of 35 cells sit at or
near the floor (median D 0.070) and the statistic has no variance to track.

## Method laws

1. **AN IDENTITY-LEVEL MEDIATOR CAN HAVE ZERO COHORT RANK CORRELATION WITH
   THE OUTCOME IT FULLY EXPLAINS.** Here u1 accounts for 100.0% of the
   carrier's disagreement (s1 0.840, s2 = s3 = 0.000) and the carrier is the
   unique pu1 == 0 cell, yet rho(pu1, D) over 35 reads +0.0145. A cohort
   correlation asks whether the mediator tracks the outcome's VARIANCE; a
   pointwise decomposition asks whether it accounts for a PARTICULAR case.
   When the outcome is extreme-value dominated these answers come apart
   completely — report the per-unit LADDER beside the cohort rho, and never
   read a null cohort correlation as "the mediator is not the mechanism".
   (Converse of L233's law, which warned that a strong WITHIN-unit
   correlation licenses nothing BETWEEN units; here a null BETWEEN-unit
   correlation licenses nothing against a WITHIN-unit identity.)
2. **WHEN A METHOD LAW IS DISCOVERED ON A SELECTED UNIT, THE NONSELECTIVE
   VERSION DECIDES WHETHER IT IS A LAW ABOUT THE STATISTICS OR A FINDING
   ABOUT THE UNIT** — and it can come back the second way. L218's inversion
   survives as a fact (it is still 0.940 vs 0.100 on bit-identical data) but
   its generalisation is now refuted at 1/35 against a prereg 0.25 bar. The
   cheap diagnostic that would have predicted it: the two currencies differed
   by an IDENTITY whose extra factor was the actor's own u1, and u1's
   percentile was ALREADY STORED (L210's `carrier_u_percentile = 0.0`).
3. **A RARE CURRENCY STEP CAN DOMINATE A RANK STATISTIC.** The sign rung
   fires on 8 of 35 cells and moves Spearman(pA2, p|u2|) from +0.554 to
   +0.248 — 55% of the rank discordance from 23% of the cells. A currency
   difference's cohort FREQUENCY and its cohort INFLUENCE are different
   numbers (L234's sign law, now measured over a population).

## Predictions

- **P1 FALSE** (registered I_CONVENTION, measured **I_CARRIER**) — the card.
- P2 TRUE (+0.248385 in [-0.5, +0.5]).
- P3 TRUE (identity max rel 5.682e-16 <= 1.421e-14, 3,500 cells).
- P4 TRUE (carrier rank by D = **1** of 35, bar <= 5).
- P5 TRUE (mean s1 0.0769 > mean s2 0.0471).
- **P6 FALSE** (mean s3 0.042857 < 0.05, a 0.0071 miss — the sign step is
  rare, not negligible: 8/35 cells, max 0.46).

## Certification

- **SLICE A = l218_static.py lines 1-1624 VERBATIM** (slice sha
  `5fd5ad299caf5975`, parent whole-file `ff2f2a5d83d55ee6`), a literal PREFIX
  cut immediately BEFORE the parent's own per-draw deflation loop, AST-proven
  write-free. PIN 1: the parent's first 10 lines **equal
  l218/static.json["banner"]**. PIN 2: l218_tail.py whole-file sha
  `5db068f586f3f097` == the TAIL sha that banner records AND a literal SUFFIX
  of the parent. PIN 4 (structural, by AST): the slice assigns **29** o[...]
  keys, which is EVERY non-late key the artifact stores and NONE of the 6
  post-cut keys; the **139** cut lines own the parent's own loop
  (`for k in range(len(rows210))`, two defl_pair calls), its writer and
  exactly `{Q218_3_u2, predictions, amendments, limitations, priors_readonly,
  rows_per_draw_recomputed}`.
- **SLICE D = l231_tail.py lines 429-450 VERBATIM** (sha
  `887a396073745d80`, source whole-file `879539c97fbe4d93` recorded in
  l231_static.py and a literal SUFFIX of it) = L231's certified
  midrank/spearman, AST-proven to define exactly `[midrank, spearman]` with
  the stable-mergesort assertion kept. Same slice sha as L233's SLICE D.
- **CERT-235A (HALTING, 630)** = every leaf of l218/static.json outside the
  6 post-cut keys reproduced at FLOAT EQUALITY on a coverage bar **630
  DERIVED from the artifact's own leaf count** over 29 keys, with a floor
  **495** derived from 10 core blocks (L224's law, applied in advance this
  time). It re-runs CERT-218T (1224), CERT-W50 (1010), CERT-DEFLV, CERT-206
  (94), CERT-MV (8), CERT-LEFT, CERT-REBUILD (1000), CERT-178 (420),
  CERT-NULL (8), CERT-F4, CERT-REW and the NO-OP as the code that ACTUALLY
  produced the artifact.
- **CERT-235B (HALTING, 334)** = this card's OWN 35-actor loop reproduces,
  at float equality: L218's entire stored carrier draw block (A2 median /
  p05 / p95 / percentile 0.940, |u2| percentile 0.100 and median, both
  residual summaries, draws resolved 100), L218's Q210-2 u1 block
  (percentile **0.000**, median, p05, p95), Q210-1's K percentile and median,
  L234's **100** stored per-draw K2 values, the 100 per-draw Perron
  eigenvalues and the 100 per-draw carrier K values. PREREG 0i registered
  the loop replacement as a COST SLICE (L226: an intervention until
  measured) and this is the measurement that admits it: 372 s of the parent's
  own loop replaced by a loop that captures 35 actors instead of 1, proven
  identical on the one actor both compute.
- AST: no lab module imported (L175); exactly ONE write site
  (`l235/static.json`) and one makedirs in the whole generated file.
  `md5sum -c l235/prior.md5` (11 files) GREEN before AND after; 8 prior
  artifacts fingerprint-unchanged (size, mtime_ns) across the run.
- Generated `l235_static.py` **2,049 lines**, sha
  `7ed5d286f81fe7e6018c36637bf93b3c556ae90c3cf8ebcfd5953e921f2ed81b`.

## Disclosures

- The first launch was killed by the TOOL's 60 s foreground cap (the python
  child died with its shell at CERT-REBUILD, before any measurement); the run
  was relaunched as a tracked background process and completed once. No
  partial artifact was written — the single write site is the last statement.
- Budget ~50 min against 35, dominated by the 549 s run.

## Limitations (as registered)

One substrate (f4wA), one operator `|g*W_beta|`, one null family (the l169c
destination swaps); L207's cross-null law applies. 100 draws cap every
percentile at 0.01 resolution. The 35-actor cohort is itself L178's selected
DN-adjacent family, so "cohort-wide" means within that family, not within the
graph — a cohort of 35 cannot resolve a 1/35 rate against a 3/35 bar finely,
and the I_CARRIER call rests on the carrier BEING the one disagreeing cell
rather than on the rate's precision. Unit-L2 normalisation of u2 across
operators is a CONVENTION (PREREG 0g): this rate is a statement about the
convention and is NOT evidence either currency is wrong; A2 = K2/K remains
the branch-carrying form. The carrier's own row is DESCRIPTION
(Kriegeskorte 2009 step 1). Modes 1 and 2 only.
