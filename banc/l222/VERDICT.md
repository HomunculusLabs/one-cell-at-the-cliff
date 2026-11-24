# L222 VERDICT — the BILATERAL BREAK is not a last-hop floor artifact, and the branch floor does not exist

Tick 253, 2026-11-23. Static, zero rollouts / zero settles / zero dynamics.
PREREG: `l222/PREREG.md` (written first). Artifacts: `l222/static.json`,
`l222/addendum.json`. Runtime 533.6 s (`nice -n 15 timeout 1700`).

## BRANCH: F_DEGENERATE_ACTOR (a registered escape, not the card's table)

The card registered F_ARTIFACT / F_SURVIVES / F_MIXED on
`gap_4 = |mirror_pct - carrier_pct|` at a global syn>=4 floor. **That branch is
unreachable**, and the reason is the tick's headline anatomical fact:

> **Every single in-brain out-edge of BOTH v783 DNp33 cells is below BANC's
> f4 threshold.** `frac_edges_below4 = 1.0000` for both.

| | out-edges | syn=1 share | syn_max | out-mass F1 | F2 | F4 |
|---|---|---|---|---|---|---|
| carrier (left) | 34 | 85.3% | 3 | 25.882 | 5.781 | **0.000** |
| mirror (right) | 31 | 93.5% | 2 | 22.298 | 2.197 | **0.000** |

At syn>=4 both actors have zero surviving out-mass, so `R`, the log-out-mass
matched cohort and the percentile do not EXIST — they are not small. 199 of
1,303 v783 descending cells die the same way (1,104 eligible at F=4; 1,273 at
F=1). The **finest measurable floor is F=2** (= min of the two syn_max values).

This is the L208-class measurement-capability verdict, and it quantifies
L212's own deepest stated limitation ("a descending neuron's real output
LEAVES this volume") with a number instead of a sentence: the whole v783 leg
rests on a 34-edge and a 31-edge out-neighbourhood that is 85-94%
single-synapse.

## The three currencies DISAGREE IN SIGN at the finest measurable floor

PREREG 0b registered that the card's gap is a difference of percentiles
against **two different** mass-matched cohorts, and that a floor relocates
both. Measured, global F=2:

| currency | F=1 | F=2 | direction |
|---|---|---|---|
| **registered gap** (two cohorts) | 0.230 | **0.360** | GROWS |
| gap_union (one common cohort) | 0.2377 | **0.0828** | collapses 2.9x |
| gap_cohC (carrier's cohort) | 0.230 | **0.090** | collapses 2.6x |
| ratio_R (cohort-free) | 6.2667 | **2.0356** | collapses 3.1x |
| ratio_P2 (cohort-free) | 5.3991 | **0.7737** | **INVERTS** |

The registered statistic moves the **opposite way** from every
cohort-controlled and cohort-free reading of the same substrate. The mechanism
is measured, not asserted: the carrier's cohort is **85.7% new** members at
F=2 (Jaccard 0.1429) and the mirror's is **93.6% new** (0.0638), while the
actors' out-masses collapse differentially (carrier keeps 22.3%, mirror 9.9%,
so `ratio_m_out` 0.862 -> 0.380). Since `R = P2 / (lam1^2 * m_out)`, the
mirror's R stays high only because its denominator fell harder — and the
percentile then scores it against a near-disjoint set of cells.

**Method law:** when an intervention relocates the comparison SET, a
two-cohort percentile GAP is not a contrast on the actors — it is a contrast
on two different populations, and it can report the opposite sign from the
within-distribution and cohort-free readings of the identical data. Register
the common-cohort and cohort-free companions and read them BEFORE the branch.

## The LOCAL floor is the clean instrument, and the break SURVIVES it

PREREG 0c registered the floor applied ONLY to edges landing in the 110-cell
motor readout — it deletes the sub-threshold last hops while leaving the
graph, lam1 and the cohort essentially fixed (99.95% / 99.92% of edges kept,
lam1 552.6325 / 552.6309 vs 552.6341, cohort Jaccard 0.92 / 0.89):

| | gap | gap_union | ratio_R | ratio_P2 | carrier pct | mirror pct |
|---|---|---|---|---|---|---|
| unfloored | 0.230 | 0.2377 | 6.2667 | 5.3991 | 0.020 | 0.250 |
| local F=2 | 0.210 | 0.2240 | 5.9035 | 4.9280 | 0.080 | 0.290 |
| local F=4 | **0.250** | **0.2520** | **7.9930** | 6.6723 | 0.050 | 0.300 |

Deleting every sub-threshold edge into the motor readout — **including the
mirror's famous single synapse** — leaves the asymmetry intact and at syn>=4
makes it *stronger* (ratio_R 6.27 -> 7.99). So the bilateral break is **not a
detection-floor artifact of the last hop**. Whatever the global floor does to
the gap, it does not do it by removing weak edges into the readout.

## L212's one-synapse story is a coincidence, not a mechanism

Leg (a), card-required, measured: the carrier has **0** direct motor edges
(so `P1 = 0.0` exactly on all five floors — the card's halting assert, GREEN);
the mirror has **exactly 1**, to CB0810 (nerve AN, right, root
720575940611008718) with collapsed syn_count **1**.

Three independent reads say that edge does not carry the split:

1. global F=2 removes it: the mirror's percentile goes **0.250 -> 0.440**, i.e.
   *up*, away from the carrier.
2. local F=2 removes it (plus other weak last hops): mirror **0.250 -> 0.290**,
   again up.
3. **the L222b addendum removes exactly that one edge and nothing else**, and
   it is the decisive read: `closes_the_break = False`.

| | unfloored | one edge dropped | delta |
|---|---|---|---|
| carrier pct | 0.020 | 0.020 | **0.000** |
| mirror pct | 0.250 | 0.250 | **0.000** |
| gap | 0.230 | 0.230 | **0.000** |
| ratio_R | 6.2667 | **6.3313** | **+0.0645** (widens) |
| ratio_P2 | 5.3991 | 5.2851 | -0.1140 |
| mirror P2 | 68.2887 | 66.8473 | -1.4414 = **2.111% of it** |
| mirror P1 | 0.693147 | 0.000000 | -log1p(1), by construction |
| lam1 | 552.6340796 | 552.6340795 | -1.17e-07 |
| ranks | 3 / 26 | 3 / 26 | unchanged |

Deleting the one synapse removes the mirror's *entire* depth-1 motor arrival
and **2.111%** of its depth-2 motor mass, moves both percentiles by exactly
zero, and moves the cohort-free ratio the *wrong* way (+1.0%).
`l222/parent.md5` GREEN after the addendum.

**The recorded L212 lesson "the DEPTH-1 term explains the depth-2 percentile
before the percentile does" is refuted as a mechanism.** `P1 = 0.693147 =
log1p(1)` was a true and striking observation sitting *next to* the finding;
it is not its cause. The half of that lesson which survives is the other half:
a homolog that disagrees is as informative as one that agrees.

## Predictions: 2 of 6

- **Q222-1 WRONG** — registered F_SURVIVES, measured F_DEGENERATE_ACTOR. I
  predicted the wrong *kind* of answer: I reasoned about whether the effect
  would survive the floor and never asked whether the ACTORS would.
- **Q222-2 CORRECT** — carrier P1 == 0.0 on all 3 global + 2 local floors.
- **Q222-3 CORRECT** — mirror P1 == 0.0 exactly at global F=2 (its single
  direct motor edge is its entire depth-1 motor arrival).
- **Q222-4 / -5 / -6 scored FALSE BY UNMEASURABILITY**, and that is recorded
  as such rather than as a null: there is no `carrier_pct`, no `ratio_R` and
  no cohort at F=4. For the record, at the finest measurable floor Q222-5
  would have *passed* (ratio_R 2.0356 > 2.0) and Q222-6 would have passed
  decisively (Jaccard 0.1429 < 0.80).

## Verification

| gate | checks | mode |
|---|---|---|
| **CERT-212** (halting) | **139** | float/int equality, recursive, vs stored l212/static.json |
| **CERT-FLOORGEN** (halting) | **15** | EXACT array_equal: the floored builder at F=1 IS `build_v783` |
| **CERT-MONOTONE** (halting) | **6** | nesting + om monotonicity over 139,255 cells / 15,091,983 edges |
| CERT-783 | 6 | inherited verbatim (ids array-equal, N 139255, pairs 15091983 == live nnz) |
| CERT-L207 | 8 | inherited verbatim (both DNp33 ids, left/right, descending) |
| CERT-MV | 4 + 3/floor | EXACT array_equal (bincount == np.add.at), re-run at EVERY floor |
| CERT-GATE | 22 + 22/floor | float equality vs the verbatim `reach_sub` / `power_iter_sub` / `Rstat` |
| CERT-DROPGEN (addendum) | 10 | EXACT array_equal: the drop builder with an empty drop set IS `build_v783` |

Construction: `l222_static.py` is generated from **l212_head.py sliced into
three literal pieces** (lines 1-26 / 28-116 / 123-241) so that two blocks are
CUT — line 27's `OUT = .../l212` (re-pointed to l222) and lines 117-122, the
graceful-blocker block whose write targets `OUT/static.json`, replaced by a
strictly stronger halting assert — plus the **three l207_tail.py function
slices** L212 itself inherited (shas fce1e71189eb1ed7 / 340c0432c85c6e7b /
f4585bcc52f7ab0a) and **l212_tail.py lines 1-227 = L212's entire measurement
pipeline with its predictions/limitations/writer block cut**. Generated sha
`730ac82cb12f4740` (1,090 lines).

**PARENT PIN (halting):** the builder reconstructs `l212_static.py`
byte-for-byte from those very three source files (sha `b32c576b5145487e`),
which is what proves the whole-file pins (`acbaef527a278ae1` /
`f7b533d6c384b943` / `1891ffdc3090b5b0`) are the code that produced
`l212/static.json` — not merely files with the right names.

`md5sum -c l222/prior.md5` GREEN (7 files) before the run;
`l212/static.json` and `l207/static.json` opened READ-ONLY with (size,
mtime_ns) fingerprinted before and asserted unchanged after; no lab module
imported (L175). The addendum is a literal PREFIX slice of `l222_static.py`
(lines 1-906) with ONE declared modification — the inherited V_DEGENERATE
escape at lines 432-436 is the prefix's only write and it targets
`OUT/static.json` = the parent artifact, so it is replaced by a strictly
stronger halting assert (`SPR < 1e-6`; measured 4.11e-16) and the resulting
prefix contains **zero writes**. Generated sha `5e0c476ed1d0dd71`.
`l222/parent.md5` re-verified GREEN after.

**Two self-inflicted failures, both disclosed and both caught by gates.**

(1) `run_attempt1.err`: the main run crashed with `ValueError: math domain
error` inside the verbatim `matched_cohort` — `math.log(0.0)` on the
degenerate actor. The F_DEGENERATE_ACTOR escape was registered and its flag
*was* set, but the leg then continued into cohort selection instead of
returning. **A registered degenerate escape must SHORT-CIRCUIT the leg, not
merely set a flag** — a flag that does not change control flow is
documentation, not a guard. Fixed by returning a substrate-report-only leg
with every cohort field explicitly `None`.

(2) `addendum_attempt2.err`: the addendum's own drop gate asserted
`om_before - om_after == log1p(1)` at float equality and failed at
0.6931471805599436 vs 0.6931471805599453. Correct behaviour from a
wrong-strictness gate: `om` is an `np.add.at` accumulation over 31 edges, so a
**difference of two sums is not the removed summand** (the L218 law). Re-armed
with a bar DERIVED from the operand's own ulp (`np.spacing(om)` = 3.553e-15),
measured error 1.665e-15 = **0.47 ulp**, bar 4 ulp. (`addendum_attempt1.err`
is a third, trivial one: re-pointing OUT tripped the parent's own
`OUT.endswith("/l222")` assert, which is why the final addendum keeps OUT
verbatim and cuts the inherited writer instead.)

Both crashes are kept as evidence rather than quietly rebuilt.
