# L238 PREREG — are the ELEVEN realised first hops the SAME eleven targets on both substrates?

Registered 2026-11-24 ~11:3x EST, tick 270, BEFORE the generated script existed
and before any identity-level first-hop quantity was measured. Static; zero
rollouts, zero settles, zero dynamics.

## The question

L220 measured `n_distinct_first_hops == 11` for the carrier on f4wA (menu 69)
AND on cutwA (menu 80), against a null median of 16.0 on both. The TARGET
IDENTITIES were never recorded, so "the funnel is invariant across substrates"
is currently a coincidence of two counts. This card records the realised
first-hop EDGE SET on both substrates for every actor, then asks whether the
two sets are the same set — nonselectively over the cohort, because 11-on-both
was found on the selected cell.

## Observation status (Kriegeskorte 2009; the L214 rule)

Read while scoping, therefore DESCRIPTION in this card, never inference:

* L220 `static.json` `L220_cohort`: `all_actors` has **36** names (carrier,
  twin, 33 `famNN_gi`, mirror_928); **4** are absent from cutwA (twin,
  fam00_307, fam01_585, fam02_32072); 32 present including the mirror.
  Carrier on cutwA: reach 303, `n_distinct_first_hops` 11, fh_mean 5.969401,
  si_mean 23.111887, hop_mean 3.795380; mirror_928 on cutwA: 9 distinct.
  Carrier on f4wA (L211): 303 reached, 11 distinct, fh_mean 5.847280.
* The lane's L221b note that on the real wiring 11 costs were 11 edges was
  read as a one-line skill lesson; which substrate it was measured on was NOT
  looked up, and is treated here as unmeasured on both.

**No identity-level set, overlap, load or per-actor count has been computed
by anyone, including me.** Every branch and prediction below is placed on
such a quantity.

## PREMISE CORRECTIONS

* **0a — "ELEVEN" is a count of COSTS, not of edges.** `fh_summary` (certified
  l211_tail.py 131-147) returns `len(set(round(pf[i], 12) for i in fin))`:
  the number of distinct first-hop T_L VALUES over reached pool cells. Two
  out-edges with equal T_L to 1e-12 collapse to one. The identity-level count
  is therefore a MEASUREMENT (prediction P4), not a premise of this card.
* **0b — the family width 31 is DERIVED from the stored artifact**, never
  typed: `len(all_actors) - n_absent_from_cutwA - 1 (the mirror)` = 36 - 4 - 1
  = 31, asserted against the stored `absent` list. The mirror is reported as
  the bilateral companion, not as a 32nd family member (it is not in L211's
  family and L211 reported it apart).
* **0c — menu nesting is MEASURED per actor, not assumed.** The overlap null
  uses the per-actor union of the two out-edge TARGET-ID menus, N = |M_f4 ∪
  M_cut|, K = |M_f4|, n = |M_cut|, however they nest.
* **0d — an edge's identity is its TARGET's global id** (the source is the
  actor). T_L in bits is `-log2(A_uv / s_out(u))`, so it differs between the
  substrates by a per-source normaliser: T_L is reported per substrate and
  compared across them ONLY as a rank (descriptive), never as a magnitude.
* **0e — loads are counted on each substrate's own reached pool cells, and
  the primary load correlation is on the COMMON pool cells** (global ids
  present on both substrates and reached on both), so a pool-set difference
  cannot masquerade as a load change.
* **0f — ties.** Loads are integers: midrank Spearman (L221), reported only
  with >= 3 distinct values on both sides, otherwise UNMEASURABLE and scored
  FALSE BY UNMEASURABILITY (L222). The union form gives unmatched edges load
  0 and is the companion.
* **0g — "realised" means "used by the certified shortest-path tree."** The
  inherited walker keeps ONE predecessor per cell under strict `<` relaxation
  and heap order; equal-length alternative first hops are not counted. This is
  the definition L211/L220 already used, disclosed, not a claim about all
  shortest paths.
* **0h — the per-actor test is a SET-OVERLAP test, not a wiring null.** The
  L220 draws swap the carrier's edges and are a null for no other source
  (L211's limitation, inherited). The per-actor p-value asks only: do two
  sets of these sizes, drawn from these two menus, overlap this much by
  chance? It says nothing about whether the wiring is special.
* **0i — the two substrates share their edge weights up to the eigenvector**
  (A_uv = |G v|_u |G v|_v products), and routing is by L-lengths, so similar
  realised sets are the mechanically expected outcome. A high Jaccard is a
  TRANSPORT statement about the metric, not evidence that the carrier is
  special. This is why the card's registered escape is read first.

## Registered definitions

For substrate S ∈ {f4wA, cutwA} and actor a: run an edge-identity twin of the
certified first-hop walker (gated, CERT-FE); E_S(a) = set of first-hop CSR
edges used by reached pool cells; identity = target global id.

* `r_S(a)` = |E_S(a)| (edges). `c_S(a)` = distinct T_L costs (the certified
  count).
* load_S(a, e) = number of pool cells of S whose tree uses e; `loadC_S` the
  same on common pool cells.
* `J(a)` = |E_f4 ∩ E_cut| / |E_f4 ∪ E_cut| on target global ids.
* `p(a)` = exact hypergeometric upper tail P(X >= |E_f4 ∩ E_cut|), X ~
  Hypergeom(N = |M_f4 ∪ M_cut|, K = |M_f4|, n = |M_cut|), exact rational
  arithmetic.
* `rhoC(a)` = midrank Spearman of loadC_f4 vs loadC_cut over E_f4 ∩ E_cut;
  `rhoU(a)` = the same over the union with unmatched edges at loadC 0.

## Registered branches (primary, the carrier)

* **SAME_SET** — `J >= 0.70`. The funnel is a property of a fixed small
  target set.
* **SAME_COUNT_DIFFERENT_SET** — `J <= 0.30`. 11-on-both is a coincidence;
  only the count transports.
* **PARTIAL** — `0.30 < J < 0.70`.
* **F_UNREACHABLE** — either realised set is empty: no J is reported and the
  guard speaks instead of a branch.

## Registered escape (read FIRST, it demotes the primary)

**E_POOL** fires iff ALL three hold over the 31 present non-mirror actors:
(e1) median `r_f4(a)` <= 15; (e2) at least 50% of the 31 have `r_f4(a)` in
[8, 14]; (e3) midrank Spearman(`r_f4(a)`, out-degree on f4wA) < +0.50. If (e3)
is UNMEASURABLE (< 3 distinct values on either side) the escape is reported
E_UNDECIDED and forced neither way. If E_POOL fires, the funnel is a property
of the POOL geometry (how few entry routes the pool cells have), not of the
carrier, and L221's framing is demoted with it; the primary is then reported
as a description of one member of a cohort.

## Nonselective companion (Kriegeskorte step 1)

Per-actor `J`, `p`, `r_f4`, `r_cut`, overlap k, N, both out-degrees, for all
31; Benjamini-Hochberg at q = 0.05 with m = 31 (the derived width). Reported:
number of rejections, the carrier's rank and q, the cohort median J, and the
count of actors in each branch band. The mirror is tabulated apart.

## Registered predictions (scored, never amended afterwards)

* **P1** — carrier branch **SAME_SET**.
* **P2** — cohort median `J` over the actors measurable on both substrates
  **>= 0.70** (the nonselective form of P1).
* **P3** — **E_POOL fires** (all three clauses; E_UNDECIDABLE scores FALSE).
* **P4** — the identity count equals the cost count on BOTH substrates for
  the carrier: `r_f4 == c_f4 == 11` and `r_cut == c_cut == 11`.
* **P5** — carrier `rhoC >= 0.70` and MEASURABLE (the per-edge loads
  transport, not only the membership).

## Registered gates (all HALTING)

1. **CERT-SLICE** — l238_static.py lines 1-1916 are a byte-identical copy of
   l220_static.py lines 1-1916 (everything up to the blank line before
   L220's `predictions, scored` header). The build asserts the literal
   prefix and the forbidden-token audit on the TAIL; the tail pins the
   slice's sha256 into its own artifact.
2. **CERT-220** — every leaf of `L211_primary`, `L211_cohort`, `L220_primary`,
   `L220_transport` and `L220_cohort` reproduced from my own re-run equals
   `l220/static.json` at FLOAT EQUALITY, with the coverage bar DERIVED from
   the stored file's own leaf count (exact equality, L224/L234).
3. **CERT-FE** — for EVERY actor on BOTH substrates and EVERY node of the
   graph (not only pool cells): the identity walker's dist / si / fh / hop
   equal the certified `dijkstra_si_fh` exactly, `fh[v] == T_L[fe[v]]`, and
   `START[src] <= fe[v] < END[src]`.
4. **CERT-COST** — per actor and substrate, the certified summary's
   `n_distinct_first_hops` equals a recomputation from the identity
   walker's own costs, and `r <= c` is reported (costs can only collapse).
5. **Fingerprints** — size + mtime_ns of the five parent artifacts
   (l206, l178, l169c, l211, l220 `static.json`) identical before and after
   the run: the slice wrote nothing.
6. Free inside the verbatim slice: CERT-F4, the stored gains, CSR
   orientation, CERT-178, CERT-REW, CERT-SI, CERT-GEN, CERT-211, CERT-SIGEN,
   CERT-REWCUT, CERT-MENUCUT, CERT-WALKCUT, CERT-REBIND, CERT-FH.
7. Degeneracy guards are SCOPED to the quantities read (L218): finiteness of
   every reported mean, a non-empty union before any Jaccard, a non-empty
   menu before any hypergeometric tail.

## Named limits (in advance)

* ONE operator family (anatomical |W_beta|), ONE routing convention (0g),
  two substrates that share their edge weights up to the eigenvector (0i).
* The per-actor p is a size-matched overlap null (0h), not a wiring null; a
  rejected actor is "these two sets agree more than their sizes predict",
  nothing more.
* E_POOL's three thresholds are mine, fixed here before measurement; the
  card's prose says "~11 for most of the 31 regardless of menu size" and the
  numbers are that sentence made checkable, not a calibrated instrument.
* Jaccard is a symmetric set-overlap bar (L221): at very different set sizes
  it is unpassable even by a perfect subset, so the directed containment
  fractions |A∩B|/|A| and |A∩B|/|B| are reported beside it as companions.

## AMENDMENT LOG (appended after registration; the registered text above is untouched)

* **A1 — 2026-11-24 12:53 EST, tick 271** (inheriting tick 270's claim: that
  run died 11:40:06 on HTTP 429 after writing this PREREG and the tail, before
  any build or run). **Attempt 1 HALTED, exit 1**, at l238_static.py:2276 =
  l238_tail.py:360 — `KeyError: 'load'` in `_side`'s DESCRIPTIVE top-1 field
  (`max(r["edges"], key=lambda e: e["load"])`): the realised-edge dicts carry
  `cells`, not `load`. The tail that halted is tick 270's as written (sha256
  dbc10fedc255109c…, mtime 11:38:30). **Halting point, from
  l238/run_attempt1.out:** after CERT-220 (896/896), CERT-FE (8,696,418),
  CERT-COST (72), CERT-REBIND-238 (606), CERT-STAT and CERT-BH were all
  GREEN, and in the FIRST iteration of the per-actor table loop (tail 348) at
  its first `_side` call — before any cross-substrate record (`k`, `J`, `p`,
  `rhoC`, `r_f4` vs `r_cut`), any escape clause or any BH quantity was
  computed or printed. The per-actor realised edge sets and their sizes were
  computed in memory (tail 235-241) but never printed, never compared across
  substrates and never read by anyone. The only L238 premise numbers printed
  before the halt: pools f4wA 303 / cutwA 303 / common 303; actors 36 (mirror
  apart); cutwA-present non-mirror 31; stored absent 4. **FIX:** two
  statements, sort key `e["load"]` -> `len(e["cells"])` (= the registered
  `load_S(a, e)` definition, the expression the adjacent `edges=` comprehension
  already uses). `diff` against the attempt-1 tail (preserved at
  scratch/l238_tail_attempt1.py): 2 statements, 3 removed / 4 added lines,
  nothing else; tail sha256 dbc10fedc255109c -> 2acf38e090b10f3d (612 lines).
  **NO registered definition, branch, bar, escape clause, prediction or gate
  was changed.**
