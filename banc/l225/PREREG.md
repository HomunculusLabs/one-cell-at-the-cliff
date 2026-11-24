# L225 PREREG — the TYPE-LEVEL null applied NONSELECTIVELY, with FDR

Registered BEFORE any L225 number was measured. Static, zero rollouts, zero
settles, zero dynamics. Writes `l225/static.json` ONLY.

## The question

L213 gave L207's cell-TYPE reading the type-level null it never had: the
DNp33 type median sits at null percentile .0145 / .0105 / .0130 on the three
L207 substrates under 2000 within-mass-stratum type-label permutations. That
is **one preselected type**. It says nothing about how many of the ~426
>=2-member descending types clear the same bar by chance. This card is
Kriegeskorte, Simmons, Bellgowan & Baker (Nat Neurosci 12:535-540, 2009)
policy step (1): the NONSELECTIVE whole-population analysis with
multiple-comparison correction, which their policy prefers BEFORE any
selection. F_COMMON is therefore the honest headline their policy predicts,
not a disappointing outcome.

- **Q225-1 (PRIMARY, branch-bearing)**: score EVERY >=2-member descending
  cell type's median R against the SAME within-mass-stratum permutation null,
  apply Benjamini-Hochberg at alpha = 0.05 over those m types, and count the
  survivors in the LOW direction.
- **Q225-2 (DESCRIPTIVE with a registered rule, no branch)**: do the
  survivors share an annotation (side / region / nerve / hemilineage /
  neurotransmitter_predicted / cell_class / flow) that names a cheaper
  explanation than "DNp33 specifically"?
- **Q225-3 (DESCRIPTIVE, no branch)**: is the carrier's first-hop MENU SIZE
  (out-degree) unusual among the survivor types or typical of them?

## Branches (registered)

- **F_UNIQUE** — DNp33 is the ONLY type surviving BH on the primary substrate.
- **F_SMALL_FAMILY** — 2..10 types survive.
- **F_COMMON** — more than 10 types survive.
- **F_DEGENERATE** — the seed-continuity gate fails, or the resolution floor
  (0a) makes the registered branch set unreachable, or DNp33 has < 2 present
  members on a substrate. Every escape SHORT-CIRCUITS (L222): it returns
  before any survivor count is read, and the unreached questions are recorded
  UNSCORED BY ESCAPE, never as nulls.

Substrate rule: the branch is called on the PRIMARY substrate G0_closure;
the other two are reported and a disagreement is disclosed, never averaged.

## Premise corrections (all pre-measurement)

**0a — A PERMUTATION FDR HAS A RESOLUTION FLOOR, AND AT L213's DRAW COUNT THE
REGISTERED BRANCH F_UNIQUE IS UNREACHABLE BY CONSTRUCTION.** A one-sided
add-one permutation p-value over B draws cannot go below `p_min = 1/(B+1)`.
BH rejects the rank-1 test only if `p_1 <= alpha/m`. MEASURED ARITHMETIC
(l225_probe.py, run before this PREREG was finished): at B = 2000 and
m = 426, `p_min = 4.998e-04` against a rank-1 threshold of `1.174e-04`, so
**no type can be rejected at rank 1 whatever the data says**, and the
smallest number of floor-tied types that BH can reject at all is **5**. That
is a property of the INSTRUMENT, not of the brain: porting L213's null
unchanged would have manufactured a guaranteed "no type survives" answer and
the F_UNIQUE branch could never have fired. Registered fix: run the per-type
sweep at **B = 20000** (p_min 5.00e-05 < 1.174e-04, so a single floor type is
rejectable), and require the FIRST 2000 draws of that stream to be the SAME
draws L213 used, so the extension is CONTINUITY and not replacement. The
floor is recomputed in-script from the measured m per substrate and the
branch set is asserted reachable BEFORE the survivor count is read; if it is
not, F_DEGENERATE fires.

**0b — SEED CONTINUITY IS A VERIFIED PROPERTY, NOT AN ASSUMPTION.** Probed
(l225_probe.py): `perm_within` consumes exactly `n_strata` `rng.permutation`
calls per draw regardless of data, so the first 2000 draws of a
`default_rng(21342)` stream are a bit-exact PREFIX of a 20000-draw stream
(verified True) and draw 2001 differs from draw 1 (verified True). The card's
Verify line is implemented as **CERT-SEED**: my per-type kernel's DNp33
column over the first 2000 draws must reproduce l213's stored `null_pct`,
`null_median`, `null_p05`, `null_p95` and `type_median` at FLOAT EQUALITY
before any other type's statistic is read.

**0c — L213's `pct` IS A PERCENTILE, NOT A P-VALUE.** `(null < real)/B` uses
a strict `<` and can be exactly 0, which has no place in a BH ladder.
Registered: `p = (1 + #{null <= real}) / (B + 1)`, the standard add-one
one-sided permutation p-value (Phipson & Smyth, Stat Appl Genet Mol Biol 9:39,
2010 — NAMED prior art: cite, don't claim). L213's `pct` convention is
reported beside it as the continuity companion.

**0d — DIRECTION AND ITS SYMMETRY CONTROL.** The claim is LOW R (avoidance),
so every type is tested one-sided LOW. The HIGH-direction survivor count is
computed too, as a descriptive symmetry check: if the high side carries a
comparable count, the procedure is detecting type-level structure in general
rather than avoidance in particular.

**0e — BIT-IDENTICAL FAST MEDIAN.** Probed: `np.median(A, axis=1)` is
`np.array_equal` to a per-row `np.median` loop at sizes 2,3,4,5,6,7,8,11
(max abs diff 0.000e+00), so **CERT-FAST** can be an EXACT array equality
rather than a tolerance (the L224 x1.0 probe pattern).

**0f — OBSERVATION STATUS (Kriegeskorte 2009 / the L214 rule).** I read
l213/static.json's whole Q1 block while scoping, so DNp33's type median, its
percentile among type medians (.1315 / .1411 / .1687) and its 2000-draw null
percentile are observation-derivable and are declared **DESCRIPTION**. Every
branch sits on quantities the stored artifact does not determine: the
per-type null for the other ~425 types, the BH ladder, the survivor counts.
Separately and more importantly, the SELECTION HISTORY is stated here as the
card demands: gi 1110 entered this chain because L178 found it extreme on a
depth-2 path statistic, and L206/L207/L210/L211/L213 then measured closely
related path statistics on the same cell on the same graph — so the carrier's
own null percentiles are valid as DESCRIPTIONS of a selected cell, never as
p-values for "a cell". This card's survivor count is the first quantity in
the family that is not conditioned on that selection.

**0g — THE CARD'S "69-TARGET MENU" IS A DIFFERENT SUBSTRATE'S NUMBER.**
L211's CERT-MENU 69 is the carrier's out-degree on the l169c/b65 operator,
not on the three L207/L213 BANC substrates this card measures. Registered:
Q225-3 measures out-degree ON THESE SUBSTRATES (`np.bincount(sub["cols"])`,
cols = SOURCE in the certified orientation) and reports 69 only as a
cross-substrate note. M_UNMEASURABLE escape if out-degree is unavailable.

**0h — THE 2-POINT LIMIT CARRIES OVER.** DNp33 has exactly 2 present members,
so its type median is a 2-point statistic: direction only, never a magnitude
(L213 limit 1). Every other type's median inherits the same caveat scaled by
its own size, and type SIZE is held by the permutation (the index permutation
moves R values between cells, never changes any type's membership count).

## Predictions (registered before measuring)

- **P1**: the branch is F_COMMON (> 10 survivors) on the primary substrate.
- **P2**: DNp33's own BH q-value on the primary substrate is <= 0.05 (it
  survives its own nonselective test).
- **P3**: DNp33 is NOT the smallest p-value among the m types — at least 10
  types have a strictly smaller p.
- **P4**: the LOW and HIGH survivor counts differ by at least 2x (the
  avoidance direction is not symmetric with the enrichment direction).
- **P5**: CERT-SEED reproduces l213's four stored DNp33 null values at float
  equality on all three substrates.
- **P6**: no single annotation category covers >= 50% of the survivor types
  at the registered Bonferroni-corrected enrichment bar (i.e. Q225-2 does NOT
  name a cheaper explanation).

## Verify (the card's own line, implemented)

- PREREG written first (this file).
- CERT-207 (522) + CERT-T (272) + CERT-178 (420) + CERT-F4 + the three stored
  gains + all 20 pool sizes arrive as INHERITED VERBATIM SOURCE and re-run
  free, via the l224 head-slice chain.
- **CERT-213 (HALTING)**: every stored leaf of l213/static.json except
  runtime_s reproduced at float/int/str equality, with the coverage bar
  DERIVED FROM THE ARTIFACT (count the stored leaves, require exact
  coverage — the L224 lesson), by RE-EXECUTING L213's pipeline as a verbatim
  source slice. The CERT-213 block itself is inherited as a verbatim slice of
  l224_tail.py, not re-implemented (the L211 re-execution rule).
- **CERT-SEED (HALTING)**: as 0b.
- **CERT-GRP (HALTING)**: my rebuilt >=2-member type grouping asserted to
  match l213's stored `n_types_ge2`, `n_cells_in_types`, `dnp33_members` and
  `type_median` per substrate before any sweep runs.
- **CERT-FAST (HALTING)**: as 0e, exact array equality on real data.
- **PARENT PIN (HALTING)**: l213_tail.py asserted a literal SUFFIX of
  l213_static.py and every head slice a literal substring in order, so
  CERT-213 arrives as the code that ACTUALLY produced the artifact.
- Negative audit: writes only to l225/, no lab module imported (L175),
  forbidden-token audit, ast.parse, md5 of every prior artifact before and
  after.

## Limitations (written in advance)

- One statistic (R), one null family (within-mass-stratum type-label
  permutation), one annotation release, three non-independent substrates.
- BH controls the FDR over TYPE medians, not over cells; a type's median is
  as weak as its member count.
- The permutation holds log-out-mass stratum and type size, but not
  neurotransmitter, side, neuropil or hemilineage composition — so a survivor
  family sharing one of those is exactly what Q225-2 can only DESCRIBE.
- Anatomical leg only: no row mask, no settle, no seed (L164).
- A nonselective survivor count de-circularises the TYPE claim; it does not
  de-circularise the per-cell claims in L206-L212, which keep their selected
  status (Kriegeskorte step (3), an independent specimen, is L212's v783 leg).
