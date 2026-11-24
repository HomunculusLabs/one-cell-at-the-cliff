# L221 PREREG — the FIRST-HOP FUNNEL: skew, target reach, or metric artifact?

Registered 2026-11-23, tick 251, BEFORE `l221_tail.py` existed and before any
L221 quantity was computed. Substrate f4wA (L211's own). Static: zero
rollouts, zero settles, zero dynamics, no RNG of my own (the 100 draws are
the certified l169c destination-swap draws, seed 16943, rebuilt by the
inherited slices).

## The parent finding this card interrogates

L211 (certified, `l211/static.json`): the carrier's realised mean first hop is
5.847280040722828 bits using `n_distinct_first_hops == 11` for all 303 pool
cells, against a 69-edge menu whose uniform allocation costs
log2(69) = 6.108524456778169 and whose median edge costs 6.195185880629637 —
and against a null median of 16.0 distinct first hops. So the real wiring
funnels pool traffic through fewer, fatter first steps than relocated
destinations do.

## 0. Premise corrections, written before the measurement

### 0a. The parent's "distinct first hops" counts distinct COSTS, not EDGES

Reading the certified machinery rather than the sentence describing it (the
L220 law): `fh_summary` computes
`n_distinct_first_hops=int(len(set(round(pf[i], 12) for i in fin)))` where
`pf` carries `T_L[e]`. That is a count of distinct first-hop **costs in
bits**. Two different out-edges with equal weight — and the f4wA weights are
`log1p(syn_count)` of INTEGER synapse counts above a floor of 4, so exact
ties are a real possibility, not a measure-zero worry — collapse into one.

Consequence: **the card's leg (b) is not answerable from the parent at all.**
"Which 11 targets" is a question about edge identity, and the parent stored
only a cardinality of a set of floats. Registered: the primary object of this
card is `n_distinct_first_hop_EDGES`, measured by a walker that inherits the
first-hop EDGE INDEX, with the cost count reported beside it. If they differ,
L211's 11 is a LOWER BOUND on the realised edge set and must be said that way.

### 0b. Leg (a) is analytically degenerate as literally written

For a FIXED source u, both inherited metrics are strictly DECREASING
functions of the same edge weight A[e]:

- length `L_L[e] = -log10(A[e] / A_max)`
- transition `T_L[e] = -log2(A[e] / s_out(u))`, and `s_out(u)` is constant
  over u's own out-edges.

Therefore:

1. "the rank correlation between an edge's weight and whether it is ever used
   as a first hop" is EXACTLY minus the same rank correlation computed on
   `T_L`, and exactly minus the one computed on `L_L`. These are ONE
   statistic, not three. It is reported once, with the identity stated.
2. The shortest first step out of the source IS its heaviest out-edge **by
   construction**. "Fatter first steps" is the default direction of the
   metric, not a discovery. A positive weight/used correlation is therefore
   *expected* and carries no evidential weight on its own; only its MAGNITUDE
   and the fraction of the menu never used are informative.
3. The carrier's out-weight Gini was already measured by L219 (0.1493, family
   median 0.1530, twin 0.1489 — a near-constant of this cohort under log1p
   weighting). **DECLARED DESCRIPTION** (Kriegeskorte 2009 / the L214 rule):
   I read it while scoping, so it cannot carry a branch here.

What survives with content is leg (c): whether the used set survives a metric
whose weight transform is NOT a monotone function of A[e]. Registered in
advance as the two independent sub-legs this splits into:

- **Metric 2 (Crofts/Estrada strength form)**, `A_c = A / sqrt(s_i s_j)` with
  `s` the certified `s_tot` (l206_tail.py line 129-130, already in the
  inherited slice, so the transform is not re-transcribed). This re-orders the
  carrier's out-edges by their TARGETS' total strength and changes BOTH path
  selection and the transition law. A genuine re-ranking.
- **Metric 3 (plain hop count)**, `L = 1` on every edge with `T_L`
  UNCHANGED. This changes ONLY path selection and removes weight from it
  entirely. This is the strongest test of the artifact hypothesis, and it is
  the one whose result I would believe over the other two.

### 0c. Hop count has massive ties, so a heap-order "used set" is not well defined

Under `L = 1` there are many optimal paths and the certified dijkstra's heap
order picks one arbitrarily (L206's own `tie_note`: "ties in L are broken by
heap order; disclosed, not controlled"). A realised set measured that way is
not comparable across metrics.

Registered tie-free instrument: the **FEASIBLE first-hop set** = every
out-edge e = (src -> v) that lies on at least one OPTIMAL path from src to at
least one pool cell. Computed by a forward pass over the shortest-path DAG in
increasing distance order, carrying a 69-bit integer MASK of which level-1
out-edges can reach each node (one bit per out-edge; the mask is a Python int,
so this is exact and needs no per-pool search).

- DAG membership test: `d[u] + L[e] <= d[v] + TOL`, with **TOL = 1e-12
  registered in advance**, and the set ALSO reported at TOL = 0.0 so the
  tolerance's effect is visible rather than assumed.
- The registered >=80% agreement bar is scored on the **FEASIBLE** sets
  (tie-free, metric-comparable). The REALISED (heap-order) sets are reported
  beside it and their bar scored too, disclosed as tie-sensitive under
  metric 3.

## 1. The registered bar and branches

The card's bar: *the funnel is REAL if the used-set is >=80% identical across
the three metrics AND the carrier's distinct-first-hop count is below the null
p05.*

Scored as:

- `J_min` = the minimum PAIRWISE Jaccard of the three feasible first-hop
  edge sets (metric1 vs metric2, metric1 vs metric3, metric2 vs metric3).
- `n_edges_real` = the carrier's realised distinct first-hop EDGE count under
  metric 1; `p05_null` = the 5th percentile of `n_distinct_first_hops` over
  the 100 certified draws (the parent stored only the median 16.0, so the p05
  is computed from the rebuilt `NULL_FH`).

| branch | condition |
|---|---|
| **F_REAL** | `J_min >= 0.80` AND `n_edges_real < p05_null` |
| **F_METRIC** | `J_min < 0.80` (the used set is metric-dependent; L211's funnel must be restated as a property of the -log10 domain choice) |
| **F_NOT_NARROW** | `J_min >= 0.80` AND `n_edges_real >= p05_null` |
| **F_BOTH_FAIL** | `J_min < 0.80` AND `n_edges_real >= p05_null` (F_METRIC takes precedence in reporting; this label records that narrowness failed too) |

## 2. The POOL-GEOMETRY control, reported BEFORE the branch

Borrowed from L238's registered demotion escape and **cited to L238, not
re-banked as independent evidence** (the Q219-5 discipline). L238 owns the
cross-substrate identity question; this card owns the mechanism on f4wA.

Nonselectively over all 35 L178 actors (the carrier was SELECTED on a related
statistic, so a cohort census is the only way the narrowness claim is
readable at all), measure `n_distinct_first_hop_EDGES` and the menu size.
Reported, like L223's `rho`-first rule, BEFORE the carrier's branch, because
it decides whether the question is about the carrier:

- If the carrier's count is unremarkable in that census (percentile > 0.20),
  the funnel is a property of the 303 pool cells' entry geometry and NOT of
  the carrier — which demotes this card's framing, and I will say so.

## 3. Leg (b): the used set vs L178's five pool-out-edge targets

L178 stored `n_targets_with_pool_outedge = 5` (carrier) and `19` (twin) but
NOT the identities. The identities are re-derived here from `csr_rows /
csr_cols / POOL_ALL` using L178's own expression, and that re-derivation is
**gated** by asserting my counts equal the stored 5 and 19 at integer
equality (the L219 CERT-219D pattern: a disclosed re-transcription gated by
the parent's stored outputs). Report the realised first-hop targets' global
ids, `cell_type`/`super_class`/`side` from the certified annotations, `T_L`
in bits, and how many pool cells each serves; then the superset / subset /
disjoint relation to the five.

## 4. Predictions (scored, written before the run)

- **P1**: branch **F_REAL**.
- **P2**: `n_distinct_first_hop_EDGES == 11` — no exact `T_L` ties among the
  realised first hops, so the parent's cost count was already the edge count.
- **P3**: at least 3 of L178's five pool-out-edge targets are in the realised
  first-hop set under metric 1.
- **P4**: Spearman(A[e], used-as-first-hop indicator) over the 69 out-edges
  is > 0 (mechanically expected per 0b; registered so the magnitude is on
  record, not as evidence).
- **P5**: the carrier's `n_distinct_first_hop_EDGES` is at or below the 20th
  percentile of the 35-actor nonselective census — i.e. the funnel is at
  least partly carrier-specific rather than pure pool geometry.

## 5. Declared DESCRIPTION (observed while scoping; no branch may rest on it)

Kriegeskorte 2009 / the L214 rule. Read before this PREREG was written:
L211's whole `L211_primary` block (`share_fh` -0.005618879769401901,
`si_mean` 22.39317740345491, `fh_mean` 5.847280040722828,
`fh_share_of_si` 0.2611188191551899, `hop_mean` 3.8052805280528053,
`n_distinct_first_hops` 11, `fh_min` 5.515257714221297, `fh_max`
6.711883423616468, menu min 5.4963012879811535 / med 6.195185880629637 /
max 6.711883423616468, `null_n_distinct_first_hops_med` 16.0, percentiles
fh 45.0 / rem 100.0 / si 100.0); L219's out-weight Gini table and its
Spearman(w_e, u1[t_e]) = +0.067; L178's `n_targets_with_pool_outedge` 5 and
19, `n_targets_active` 25, `pool_outedges_from_targets` 25. Note in
particular that `fh_min` 5.5153 > `menu_min` 5.4963 — the realised cheapest
first hop is NOT the cheapest available edge — which is description, and is
the observation that made 0b worth writing.

## 6. Deferred, deliberately

The cutwA second substrate. L220 measured 11 distinct first-hop COSTS on both
substrates, and L238 is the card that owns the two-substrate IDENTITY
comparison nonselectively with BH-FDR. Doing it here would double-bank it.
This card is f4wA only, and says so in its limitations.

## 7. Verification plan (gates that must be GREEN before any branch is called)

- Ten pieces, NINE verbatim source slices, forbidden-token audited, no lab
  module imported (L175), every inherited sha asserted by the BUILDER against
  the value L220 recorded, plus the two PARENT PINS (l211_tail.py whole-file
  sha == l211_static.py's banner TAIL sha; l220_tail.py whole-file sha ==
  l220_static.py's banner TAIL sha).
- Inherited free: CERT-F4, CERT-178 (420), CERT-NULL (8), CERT-REW, CERT-SI
  (240), CERT-MENU (100), CERT-FH (61,819), CERT-211 (434), CERT-SIGEN
  (1,922,356).
- **CERT-FHE (new, HALTING)**: the edge-index walker's first-hop COST
  (`T_L[fe]`) must equal the certified `dijkstra_si_fh`'s `fh` at EXACT
  equality on all 303 pool cells, and its `dist`/`si` must equal the
  certified `dijkstra_si`, for the carrier, the twin and all 100 draws.
- **CERT-DAG (new, HALTING)**: on metric 1, every pool cell's realised
  first-hop edge must be a MEMBER of that pool cell's feasible mask (a
  realised optimum is feasible by definition — if this fails, the mask is
  wrong), and the feasible set must be a SUPERSET of the realised set.
- **CERT-D5 (new, HALTING)**: the re-derived pool-out-edge target counts
  equal L178's stored 5 (carrier) and 19 (twin).
- **CERT-CROFTS (new, HALTING)**: `power_iter(jv_crofts)` reproduces
  `l206/static.json`'s `lam1_crofts` 0.3881201140476021 — proving the metric-2
  operator is the same object L206 certified — at the convergence level that
  operator actually reaches (`rel_spread_crofts` 1.06e-08, so the bar is
  DERIVED from the measured convergence per the L216 law, not fixed at 1e-9).
- Prior artifacts opened READ-ONLY with (size, mtime_ns) fingerprinted before
  and asserted unchanged after; `md5sum -c` GREEN against `l221/prior.md5`.
