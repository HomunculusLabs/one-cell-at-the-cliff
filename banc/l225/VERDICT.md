# L225 VERDICT — the TYPE-LEVEL null applied NONSELECTIVELY, with FDR

**Branch: F_SMALL_FAMILY (registered). Predictions 3 of 6.**
**Headline (corrected in the addendum — the parent's auto-generated
sentence was wrong): DNp33's TYPE-level avoidance does NOT survive
multiplicity correction.**

Static, zero rollouts, zero settles, zero dynamics. PREREG `l225/PREREG.md`
written first. Artifacts: `l225/static.json`, `l225/addendum.json`.
Code: `l225_{build,mid,tail}.py` -> `l225_static.py` (sha
`43dbee573ba67c62`, 1,746 lines), `l225b_{build,tail}.py` ->
`l225b_static.py` (sha `86edefc17b5c2b8c`, a literal PREFIX of the parent
at line 1735 plus the addendum tail).

## What was measured

Every >=2-member descending cell type on the three L207/L213 substrates was
scored against the SAME within-mass-stratum type-label permutation null
L213 used for DNp33 alone — same seed (21342), same `perm_within`, the
first 2,000 draws asserted bit-identical to L213's — extended to 20,000
draws, and the family corrected with Benjamini-Hochberg at alpha .05.

| | G0_closure | G1_cutwA | F4_f4wA |
|---|---|---|---|
| types (m) | 426 | 411 | 409 |
| survivors, LOW | **5** | **2** | **1** |
| survivors, HIGH | 9 | 7 | 9 |
| DNp33 p (uncorrected) | .01555 | .01150 | .01375 |
| DNp33 BH q | **.1573** | **.1423** | **.1915** |
| DNp33 survives | **False** | **False** | **False** |
| DNp33 rank by p | 42 / 426 | 31 / 411 | 29 / 409 |

Survivors: **oviDNa_b** (all three substrates — the only one), DNpe046
(two), DNp13 / DNg82 / DNge005 (G0 only). DNp33 survives on none.

## Premise 0a — the finding that had to come before the measurement

**A permutation FDR has a RESOLUTION FLOOR, and at L213's draw count the
registered F_UNIQUE branch was unreachable by construction.** `p_min =
1/(B+1)`; BH rejects rank 1 only if `p_1 <= alpha/m`. At B = 2,000 and
m = 426: `4.998e-04` vs `1.174e-04` — **no type could be rejected at rank 1
whatever the data said**, and the smallest number of floor-tied types BH
could reject at all was **5**. Porting L213's null unchanged would have
manufactured a guaranteed "nothing survives" answer. Registered fix:
B = 20,000 (p_min `5.00e-05`, one floor type now rejectable), with the
first 2,000 draws required to BE L213's draws. The fix was **load-bearing**:
on G1 and F4 the survivors sit AT the floor (2 and 1 types), so at L213's
draw count they would have been invisible too.

## The addendum (declared POST-HOC; no branch, no bar, no prediction)

**(A) The parent's auto-generated `headline` string is wrong, and the
artifact proves it against itself.** The registered branch set
{F_UNIQUE, F_SMALL_FAMILY, F_COMMON, F_DEGENERATE} is defined on a COUNT of
survivors. F_SMALL_FAMILY fired correctly at 5 — and the prose generator
then said "DNp33 is one of a small family of 5 types surviving", because its
author assumed that if few types survived the actor would be among them. The
parent's own `dnp33_survives` field says `False`. The addendum asserts that
contradiction rather than describing it. **Method law: a branch defined on a
COUNT cannot answer a MEMBERSHIP question — when the card asks whether a
specific unit is special, the actor's membership must be INSIDE the branch
definition, or the verdict sentence gets generated from an assumption the
measurement never made.**

**(B) MAGNITUDE, not power.** DNp33's p is estimated from 310 / 229 / 274
null draws at or below the real value out of 20,000; the Wilson 95% interval
for the underlying tail probability is [.01388, .01731] / [.01007, .01302] /
[.01218, .01541] against a BH requirement of **.00493 / .00377 / .00355** at
its own rank (and 1.17e-04 at rank 1). The interval excludes the requirement
on all three substrates: **no draw count can ever make this p
BH-significant.** The draw count was the limitation on the FAMILY (premise
0a), never on the actor.

**(C) The type-level signal is REAL in aggregate — which is exactly why one
preselected type cannot carry it.** 63 of 426 types clear the uncorrected
p <= .05 bar against 21.3 expected by chance (**2.96x**; 2.82x and 2.84x
elsewhere), and **38 types sit at or below DNp33's own L213 percentile of
.0145**. The card's framing was right: a null pct of .013 on ONE preselected
type says nothing about how many of 426 clear it by chance.

**(D) The cheaper explanation exists — and it belongs to the SURVIVORS, not
to the actor.** Q225-2's registered shared-annotation rule fired on
G1_cutwA: hemilineage **SMPpv1** at survivor share 1.000 vs background .017,
enrichment p .0005 against a Bonferroni bar .05/25 = .002; the survivors'
modal neurotransmitter there is **gaba** (share 1.000 vs background .187).
DNp33 is `putative_primary` / `acetylcholine`. On the primary substrate the
rule does NOT fire (SMPpv1 share .400, p .0055 vs bar .00192), so P6 scores
TRUE and the G1 firing is disclosed.

**(E) What L213's claim becomes.** The percentile itself is REPRODUCED here
at float equality and reads .01555 at 10x the draws — it is a correct
measurement. What changes is that it is UNCORRECTED. The TYPE-level
avoidance claim for DNp33 is **withdrawn as an inferential claim and
retained as a DESCRIPTION of a cell selected for being extreme**
(Kriegeskorte 2009). The CELL-level claims of L206-L212 are untouched: they
were already labelled selected, and their de-circularising leg is L212's
independent-specimen v783 reading. What the family GAINS is a nonselective
finding it did not have: there is a small, substrate-consistent set of
descending types that avoid the motor pools beyond multiplicity-corrected
chance, headed by **oviDNa_b**.

## Q225-3 (descriptive) — the menu size, premise 0g honoured

L211's "69-target menu" is the l169c/b65 operator's number. ON THESE
substrates the carrier's out-degree is **80 / 80 / 69** against population
medians 42 / 41 / 30 (percentile .718 / .732 / .766) — a HIGH-out-degree
cell, and the survivor types' member cells are higher still (median
69.5 / 92.0 / 76.5). The coincidence with 69 on F4_f4wA is just that.

## Predictions

- **P1 FALSE** — registered F_COMMON (>10 survivors); measured
  F_SMALL_FAMILY (5).
- **P2 FALSE** — registered DNp33 q <= .05; measured **.1573**. This is the
  prediction whose failure IS the finding.
- **P3 TRUE** — >= 10 types with a smaller p; measured 41.
- **P4 FALSE** — registered LOW/HIGH counts differ >= 2x; measured 5 vs 9
  (1.8x). The HIGH side is comparably populated, so the procedure detects
  type-level structure in BOTH directions.
- **P5 TRUE** — CERT-SEED reproduced L213's stored DNp33 null on all three
  substrates (15 checks at float equality).
- **P6 TRUE** — no annotation category names a cheaper explanation at the
  registered bar on the primary substrate (G1 firing disclosed above).

## Certification

- **CERT-213 (HALTING, 289)** — every stored leaf of l213/static.json except
  runtime_s at float/int/str equality, coverage DERIVED FROM THE ARTIFACT,
  by re-EXECUTING L213's pipeline as a verbatim source slice. The CERT-213
  block itself is inherited as **l224_tail.py lines 48-124 VERBATIM** — the
  gate re-used as SOURCE, never re-implemented.
- **CERT-SEED (HALTING, 15)** — the DNp33 column over the first 2,000 draws
  of the 20,000-draw stream reproduces l213's `null_pct`, `null_median`,
  `null_p05`, `null_p95` and `type_median` at FLOAT EQUALITY on all three
  substrates. The extension is CONTINUITY, not replacement.
- **CERT-GRP (HALTING, 12)** — the rebuilt >=2-member grouping asserted
  against L213's stored `n_types_ge2`, `n_cells_in_types`,
  `dnp33_members` and `type_median` before any sweep ran.
- **CERT-FAST (HALTING, 9)** — the padded axis-median kernel EXACTLY
  `np.array_equal` to a per-type `np.median` loop on real AND permuted R
  (licensed by premise 0e's bit-identity probe at sizes 2-11, max abs diff
  0.000e+00).
- **CERT-225 (HALTING, 63)** in the addendum — the parent's branch-bearing
  stored values at float/int/str equality before any addendum number read.
- Inherited free: CERT-178 (420), CERT-207 (522), CERT-T (272), CERT-F4, the
  three stored gains, the CSR orientation, all 20 pool sizes.
- **PARENT PIN 1**: l213_tail.py a literal SUFFIX of l213_static.py (sha
  `7131bfef8d6e4ac8`), every head slice a substring in order, no trailing
  bytes. **PARENT PIN 2**: l224_tail.py a literal SUFFIX of l224_static.py
  (sha `4df587a0dc143358`) — which proves CERT-213 arrives as the code that
  actually ran in L224.
- Negative audit: exactly ONE write in the parent (to l225/static.json) and
  ONE in the addendum (to l225/addendum.json); the addendum prefix asserted
  to contain ZERO writes; 15 inherited function bodies asserted
  not re-transcribed; no lab module imported (L175); forbidden-token audit;
  `ast.parse` on both generated files. `md5sum -c l225/prior.md5` (13 files)
  GREEN before and after; `l225/parent.md5` GREEN after the addendum;
  l213/static.json and l225/static.json opened read-only with
  (size, mtime_ns) fingerprinted before and asserted unchanged after.

**Two self-inflicted build failures, disclosed, both caught by this card's
own gates**: (1) `assert "CERT-ADD" not in h7` halted the build because the
inherited slice's OWN PROSE names CERT-ADD — the tick-248 bare-token trap in
a new place, repaired by gating on the BLOCK (`_nadd = 0`, `MM = {}`) rather
than the token; (2) `assert h6_full in par2` halted because l224_static.py
carries l213_tail lines 1-430, not the whole file — repaired to assert the
SLICE, which is the stronger and correct statement.

Runtime: 27.2 s parent (L225 body 14.2 s; 20,000 draws x 3 substrates in
~4 s each), 28.3 s addendum, `nice -n 15 timeout 1700` on om, CPU only.
