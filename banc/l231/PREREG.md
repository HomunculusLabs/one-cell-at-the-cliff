# L231 PREREG — does the LEFT-heavy Perron mode have a SOURCE?

Registered 2026-11-24 ~01:1x EST, BEFORE the generated script existed and
BEFORE any left/right asymmetry of any Perron vector was read outside the four
values L216 already stored. Static, zero rollouts, zero settles.

Lane item (LANE.md, ideas 112, seeded by tick 246):

> L231. does the LEFT-heavy Perron mode have a SOURCE? ... Ask it
> NONSELECTIVELY (Kriegeskorte step 1, as L229 does for near-balance):
> compute the per-cell Perron overlap v1 for ALL ten cord pool-sides and for
> the whole labelled population, and test the left-right asymmetry of v1 (a)
> over the pools, (b) over every super_class, and (c) over the cord subnet
> alone vs the whole graph, with BH-FDR across the whole family rather than a
> percentile on a preselected pool. Register in advance that a left-heavy v1
> on the WHOLE graph would make the pool finding a restatement of a global
> asymmetry (interesting but not pool-specific), and that the honest branches
> are GLOBAL, POOL_SPECIFIC and CLASS_SPECIFIC. Name the reconstruction
> caveat in the PREREG: a volume-wide L/R imbalance in proofreading
> completeness would produce exactly this, so include the per-side cell COUNT
> and total edge mass as the first two rows of the table. Verify: CERT-216
> halting; v1 recomputed by the certified pi_dir and asserted equal to L216's
> A_inf on the four beta cells at float equality.

---

## 0. PREMISE CORRECTIONS AND OBSERVATION STATUS (written before the script)

### 0a. OBSERVED BEFORE REGISTRATION — the four A_inf values and the side census

Per the L214 rule (registration after observation buys a DECISION RULE and
multiplicity discipline, never inference) and Kriegeskorte 2009 (digested tick
243), everything I had already seen is stated here IN FULL and scored as
DESCRIPTION, never as a prediction that held:

1. L216's eight stored A_inf values were read while scoping this card and are
   quoted in tick 246's and tick 262's log entries. The four BETA pool cells:
   `f4wA|beta|Ti +0.28663`, `f4wA|beta|Tr +0.44422`, `cutwA|beta|Ti +0.25698`,
   `cutwA|beta|Tr +0.40652`, all at `A_cell_pct_abs` 1.000 against L216's 2000
   membership permutations. Crofts: `f4wA|crofts|Ti +0.1343` (pct .994),
   `cutwA|crofts|Ti -0.008413002252988949` (pct .178, inside its null).
   CONSEQUENCE: for the two JOINTS Ti and Tr, on all four cord arms, leg (a)
   is OBSERVED-DERIVABLE and is reported as DESCRIPTION. The registered
   branch is placed on quantities nobody has computed: the three NEW joints
   (Ta, Sr, Pr), every super_class, every population-level unit, the whole
   graph arm, the confound correlations, and the BH-FDR family decision.

2. A TOOLING PROBE (`l231_probe.py`, run before this PREREG, output stored at
   `l231/probe.out`) was executed to decide whether the certified generic
   substrate builder `build_sub()` accepts a whole-graph keep mask. It reads
   NO Perron vector and NO asymmetry. What it showed, now DESCRIPTION:
   - `Nall = 80635`, every graph node carries a `super_class` annotation,
     `cord_mask = 20521`.
   - All 20 `S92["pool_sizes"]` pins hold under `keep = ALL`, so `build_sub`
     will not halt on the whole graph. ONE `S101` size differs under
     `keep = ALL`: `Pr_bL` is 3 on the cord substrates and 4 unrestricted.
   - SIDE CENSUS of the 80,635 annotated-in-graph cells:
     `left 26799 / right 53050 / midline 11 / unlabelled 775`, decomposing by
     region as ventral_nerve_cord L 10070 R 10494 (ratio 0.960),
     central_brain L 11462 R 12895 (0.889), **optic_lobe L 3311 R 27799
     (0.119)**, neck_connective L 1805 R 1732 (1.042).

   The optic-lobe figure IS the reconstruction caveat this card was told to
   name, measured: BANC v626 reconstructs one optic lobe far more completely
   than the other, so the WHOLE-GRAPH labelled population is right-heavy in
   cell COUNT by 8.4:1 inside the optic lobe and 2.0:1 overall. The cord
   subnet, where L216's finding lives, is nearly balanced in count (0.960).
   This is registered as the reason the whole-graph arm CANNOT adjudicate the
   pool finding on its own and why the region-stratified populations below are
   registered as its honest comparators.

### 0b. "per-cell Perron overlap v1" — the statistic, and why it is A_inf's own

L216's asymptote is `A_inf = asym(per-cell MEANS of v1)` over a joint's left
and right pool cells, computed by the certified `side_stats_from`. This card's
statistic is the SAME functional applied to an arbitrary unit:

    A(U) = (mL - mR) / (mL + mR),  mL = sum_{c in U_L} v1[c] / |U_L|

with v1 the nonnegative right Perron vector of the arm's operator, taken from
`PERRON[(sname, op)][1]` — i.e. produced by the certified `pi_dir` inside
SLICE A, the same object whose pool values CERT-216 pins at float equality.
A(U) > 0 means LEFT-heavy. This is a per-CELL mean, so it is not a count
statistic by construction; whether it is nevertheless count-dependent is the
registered confound leg 5 below.

### 0c. UNITS are defined ONCE on the GLOBAL index and intersected with keep_wA

For an arm comparison to be meaningful the units must be identical across
arms, and the cord-subnet v1 exists only on the cord substrate's nodes.
Therefore every unit is defined as a GLOBAL boolean cell mask intersected with
`keep_wA`, and the SAME cell sets are scored on every arm including the whole
graph. Disclosed consequence of 0a-2: the one extra `Pr_bL` cell that exists
unrestricted is NOT in any unit, so the whole-graph arm is scored on the cord
substrate's cells, not on a larger pool.

### 0d. Leg (c)'s whole-graph arm is registered on the BETA operator ONLY

The Crofts reweighting is constructed inside SLICE A's `for sname, s in
SUBS.items()` loop, which cannot be applied to a new substrate without
re-implementing the expression outside certified code (L206: a float claim is
a claim about the expression; L211: re-execute, do not re-implement). The
whole-graph arm is therefore registered on beta only, which is L216's primary
operator. This is a SCOPE LIMIT registered in advance, not a result.

### 0e. The whole-graph Perron may NOT EXIST, and that is a registered outcome

L217 measured a stable 2-cycle on one of its operators: a dominant spectrum
that is not simple, diagnosed by the eigenpair RESIDUAL and not by the
iteration's convergence spread. The whole graph is a different, much larger
and plausibly less connected operator. Registered in advance:

- The arm's Perron pair is accepted only if the relative residual
  `||A v - lam v|| / (lam ||v||) < 1e-3`, with the residual PRINTED beside the
  `rel_spread_last6` for every arm including the four certified cord arms as a
  calibration reference (L216/L217: a convergence bar is derived from the
  iteration's own measured convergence).
- If the bar fails, the whole-graph arm is recorded `UNRESOLVED` and its tests
  are EXCLUDED from the BH family. The registered branch does NOT depend on
  it: the branch is evaluated on the cord subnet's own global population,
  which is in the family regardless.

### 0f. The NULL: membership permutation holding per-side COUNTS fixed

For each unit, permute the left/right labels among the unit's own cells,
holding `n_L` and `n_R` exactly. Two regimes, chosen by the unit's own size,
registered in advance:

- If `C(n, n_L) <= 200000`: ENUMERATE every assignment. The p-value is EXACT
  and has no resolution floor (the L229/L225 law).
- Else if `n <= 5000`: 20000 draws, `np.random.default_rng(231231)`,
  p = (1 + #{|A_null| >= |A_real|}) / 20001, resolution floor 4.99975e-05.
- Else (`n > 5000`): 5000 draws, same generator, p = (1 + ...) / 5001,
  resolution floor 1.99960e-04. The tiering is a COMPUTE decision registered
  before any p-value exists: a permutation draw costs O(n), the large units
  are the whole-graph populations at n ~ 8x10^4, and 1.99960e-04 still sits
  below the BH rank-1 bar for the expected family size (reported in 0i), so
  the family's strongest members remain rejectable (the L225 law). Every
  reported p carries its own regime and its own floor.

The floor and the BH rank-1 bar are REPORTED together (L225: a draw count
binds whether the family's strongest members are rejectable at all).

### 0g. This null is NOT L216's null, and both are reported for Ti/Tr

L216's `side_stats_from` permutes within the flexor group and within the
extensor group SEPARATELY, holding four per-group side counts. This card's
null permutes within the pool-side UNION, holding two counts — because the six
new pool-sides and every super_class and population unit have no flexor/
extensor split, and one null must cover the whole family. These are DIFFERENT
nulls on the same real value. Registered: for Ti and Tr the stored L216
percentile is reported BESIDE the union-null p on every cord arm, and any
disagreement is reported as a null-definition fact, never as a measurement
change.

### 0h. The REAL statistic is gated against the certified one as a BRACKET, not a float equality

My general unit sum `v1[cells_L].sum()/nL` and `side_stats_from`'s
`mf[isLf].sum() + me[isLe].sum()` are the same real number computed by
DIFFERENT expressions, so they need not agree in the last bits (L218: a
mathematical no-op is not a floating-point no-op). Registered: the card's
float-equality requirement is discharged by CERT-216, which pins the
`side_stats_from` values against `l216/static.json`; my general form is then
gated against those certified values by a DERIVED bracket
`max rel diff < 8 * eps` with the measured maximum reported.

### 0i. BH-FDR family definition, fixed before any p-value is read

The family is EVERY (unit, arm) pair for which the unit has `n_L >= 2` and
`n_R >= 2` on that arm's substrate, over all units of legs (a), (b) and (c)
and all RESOLVED arms. Benjamini-Hochberg at `q = 0.05` across the whole
family. `m`, the rank-1 bar `0.05/m`, and the resolution floor are reported
before any rejection is quoted. Ties in p (expected, because enumerated
p-values are discrete) are handled by the standard BH step-up on sorted p.

### 0j. UNITS enumerated in advance

Leg (a) POOLS, 5 units: for `J in [Ti, Tr, Ta, Sr, Pr]`, the union of the two
antagonist pools on each side, i.e. exactly L229's ten `SIDEMASK10` pool-sides
paired into five L/R units. Ti and Tr are OBSERVED (0a-1); Ta, Sr, Pr are new.

Leg (b) SUPER_CLASS: every `super_class` label present on the arm's substrate
with at least 2 left and 2 right cells. The set is DERIVED from the data, not
hand-listed, and its membership is reported.

Leg (c) POPULATIONS, two scopes:

- RESTRICTED (scored on every arm, units identical across arms per 0c):
  `all` (every cord-substrate cell with side in {left, right}), plus the
  region-stratified `ventral_nerve_cord`, `central_brain`, `optic_lobe`,
  `neck_connective` wherever the 2-per-side rule is met.
- WHOLE-GRAPH NATIVE (scored on the `whole|beta` arm ONLY, because the
  cord-subnet v1 is not defined on brain cells): the same five populations
  AND every `super_class`, taken over all 80,635 annotated graph cells
  without the `keep_wA` restriction. This is the scope in which the card's
  own sentence lives — "a left-heavy v1 on the WHOLE graph would make the
  pool finding a restatement of a global asymmetry" — and it is the scope the
  optic-lobe count artifact of 0a-2 inhabits.

### 0k. Reconstruction caveat rows 1 and 2, as the card demands

For EVERY unit on EVERY arm the table's first two rows are:

- row 1: `n_L`, `n_R`, and `A_n = asym(n_L, n_R)` — the per-side CELL COUNT.
- row 2: `M_in_L`, `M_in_R` and `A_inmass = asym(M_in_L/n_L, M_in_R/n_R)` —
  total |log1p(syn)*sign| edge mass arriving at each side's cells on that
  arm's substrate, per cell.

### 0l. PRIMARY arm and primary unit

PRIMARY ARM = `f4wA|beta` (L216's own registered primary). PRIMARY UNIT for
the branch = the cord substrate's `all` population.

---

## 1. REGISTERED BRANCHES (first match wins, evaluated on the PRIMARY arm)

Let `A_glob = A(all population, f4wA|beta)` and
`R_glob = |A_glob| / median_{J in 5 pools} |A(U_POOL[J], f4wA|beta)|`.

The whole-population test has n ~ 2x10^4 cells against the pools' 14-113, so
its null is far tighter and BH significance there is close to automatic. The
branch is therefore MAGNITUDE-first: `R_glob` carries it, significance only
qualifies (the L207/L225 resolution law).

1. **B_SIGN_OPPOSED** — `sign(A_glob) != sign(median_J A(U_POOL[J]))` AND
   `A_glob` is BH-significant. (The pools would then carry a LOCAL
   left-heaviness against a globally right-heavy mode: the most informative
   cell, and it has no prior.)
2. **B_GLOBAL** — `R_glob >= 0.50`. The pool finding restates a global
   asymmetry.
3. **B_PARTIAL_GLOBAL** — `0.15 <= R_glob < 0.50`. A global asymmetry exists
   and the pools amplify it.
4. **B_POOL_SPECIFIC** — `R_glob < 0.15` AND at least 3 of 5 pools BH-significant.
5. **B_CLASS_SPECIFIC** — `R_glob < 0.15` AND fewer than 3 of 5 pools
   BH-significant AND at least one super_class BH-significant with `|A| >= 0.10`.
6. **B_UNREGISTERED_SHAPE** — anything else (the L205 catch-all cell; a branch
   table must admit every shape its own definitions allow).

Registered flag, reported with whichever branch fires:

- **F_CONFOUND** fires if `|rho(A_v1, A_n)| >= 0.70` with matching sign over
  the primary arm's family units, i.e. the Perron asymmetry substantially
  tracks the per-side cell-count imbalance. Rank statistics are MIDRANK with
  the distinct-value count printed (L221/L227); a tied-to-meaninglessness leg
  has its p WITHHELD rather than approximated (L229).

---

## 2. PREDICTIONS (scored as written; 0a declares what was already observed)

- **P1.** `A_glob > 0` on the primary arm — the cord subnet's whole labelled
  population is LEFT-heavy in per-cell Perron overlap. [UNOBSERVED]
- **P2.** `R_glob < 0.50`, i.e. the branch is NOT B_GLOBAL. [UNOBSERVED]
- **P3.** At least 3 of the 5 pools are BH-significant on the primary arm.
  [PARTIALLY OBSERVED: Ti and Tr sit at L216's pct_abs 1.000 under a
  DIFFERENT null (0g), so only Ta/Sr/Pr are unobserved — declared, and the
  prediction is scored as written.]
- **P4.** On the whole-graph arm (if RESOLVED) the WHOLE-GRAPH NATIVE
  `all`-population asymmetry is RIGHT-heavy (`A < 0`), because that
  population's cell count is right-heavy 2.0:1 overall and 8.4:1 inside the
  optic lobe. [The COUNTS are observed (0a-2); the v1 asymmetry is not.]
- **P5.** `|rho(A_v1, A_n)| < 0.70` on the primary arm — F_CONFOUND does not
  fire. [UNOBSERVED]
- **P6.** At least one super_class is BH-significant with `|A| >= 0.10` on the
  primary arm. [UNOBSERVED]

---

## 3. VERIFICATION PLAN (halting gates, all BEFORE any L231 number is read)

- **SLICE A** = `l216_static.py` lines 1-1360 VERBATIM, the literal PREFIX cut
  immediately before the parent's writer, AST-proven write-free on its own AST
  (the L230 construction, re-used). Re-runs CERT-F4, CERT-178, CERT-GEN,
  **CERT-205 (250)**, **CERT-GAP (10)**, **CERT-209 (412)** and the lam1 NO-OP
  as the code that actually produced `l216/static.json`, and leaves
  `PERRON / AINF / GAPS / FITS / TABLE / CELLS / SUBS / LOCAL / GROUPS /
  side_stats_from / decorate / pi_sub / build_sub / POOL_G` in memory.
- **PARENT PIN**: `l216_tail.py` is a literal SUFFIX of `l216_static.py` and
  its sha256 is exactly what that file's own generated banner records.
- **SLICE C** = `l230_tail.py` lines 39-128 VERBATIM — L230's own
  **CERT-216** block plus `leafcmp`/`leaves` and the NO-OP re-assertion, so
  the ~1,900-equality artifact-derived coverage gate runs as the code that
  passed it in tick 262, not as a re-implementation (the L225 law:
  re-use a prior card's CERTIFICATION BLOCK as a verbatim source slice).
  Its coverage bar is DERIVED from `l216/static.json`'s own leaf count.
- **CERT-231A (HALTING)**: my general unit statistic reproduces the four (and
  all eight) certified `A_inf` values within the derived bracket of 0h, with
  the measured max relative difference reported.
- **CERT-231B (HALTING)**: the five pool units' cell masks are rebuilt by
  L229's `SIDEMASK10` construction and the Ti/Tr masks asserted ARRAY-IDENTICAL
  to the pools that `GROUPS` carries, with all 20 `S101`/`S92` per-side sizes
  pinned.
- **PERRON RESIDUAL** printed for every arm, bar per 0e, UNRESOLVED allowed.
- **EXACT-NULL GATE**: for every enumerated unit, the enumeration count is
  asserted equal to `C(n, n_L)` and the null's own mean asserted ~0 to a
  derived tolerance (a side-symmetric null must be centred).
- `md5sum -c l231/prior.md5` GREEN before AND after the run over every prior
  artifact read, with `(size, mtime_ns)` fingerprints asserted unchanged.
- AST `Import`/`ImportFrom` walk proves no lab module is imported (L175); AST
  write-SITE walk proves exactly one write, targeting `l231/static.json`.
- No live change, no draft edit, `sessions/` untouched.
