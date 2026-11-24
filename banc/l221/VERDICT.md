# L221 VERDICT — the FIRST-HOP FUNNEL is the LENGTH METRIC, and it is not the carrier's

Branch **F_METRIC** (registered). Predictions **3 of 5** (P1 FALSE, P5 FALSE).
Substrate f4wA. Static: 43 s, CPU, zero rollouts / settles / dynamics, no RNG
of my own. PREREG `l221/PREREG.md`, registered first with three premise
corrections written before `l221_tail.py` existed. Clean on the FIRST attempt.

## The primary

The card's bar: the funnel is REAL if the used-set is >=80% identical across
three metrics AND the distinct-first-hop count is below the null p05.

| metric | realised edges | distinct costs | feasible edges | si_mean | hop_mean |
|---|---|---|---|---|---|
| abs `-log10(A/A_max)` | **11** | 11 | **11** | 22.3932 | 3.8053 |
| crofts `A/sqrt(s_i s_j)` | **30** | 30 | **30** | 18.5460 | 3.1749 |
| hop `L == 1`, T_L kept | **23** | 15 | **46** | 18.7628 | 3.1749 |

- `J_min(feasible)` = **0.2391** against the 0.80 bar -> **F_METRIC**.
- `J_min(realised)` = 0.3226. Pairwise feasible: abs|crofts 0.3226,
  abs|hop 0.2391, **crofts|hop 0.6522**.
- Narrowness, by contrast, PASSES: 11 realised edges vs null p05 **15.0**
  (null median **21.0**, min/max over 100 draws), carrier percentile 0.0.

So the two halves of the registered bar split: the carrier's abs-metric first
hop really is narrower than any of its 100 degree-neutral draws, and the
used-set is **not** metric-invariant. The honest statement of L211's
unregistered finding is therefore **metric-specific**: under the `-log10`
length metric the carrier's 303 pool cells enter through 11 of 69 out-edges;
under the Crofts strength form 30; under plain hop count 46 are feasible.

### The two metrics that do NOT use -log10 agree with each other far better

`crofts|hop` = 0.6522 vs abs's 0.3226 / 0.2391. The disagreement localises to
the `-log10(A/A_max)` domain choice specifically — which is exactly the
artifact leg (c) was registered to test, and it fires.

## POST-HOC, DESCRIPTIVE: the sets are NESTED, not different

Pure arithmetic on the stored sets (`t251_containment.py`, asserts green, no
new measurement). Declared post-hoc because the PREREG registered only the
symmetric Jaccard:

- abs realised **⊆** hop realised: containment **1.0000** (11 of 11; Jaccard
  0.4783 only because hop has 23).
- abs feasible **⊆** hop feasible: containment **1.0000** (11 of 11; Jaccard
  0.2391 only because hop has 46).
- abs -> crofts containment **0.9091** (10 of 11; the single exception is
  edge j=38, IN27X014-left).

**Method law, and the most transportable thing in this tick: a SYMMETRIC
set-overlap bar cannot distinguish "a different set" from "a nested subset",
and when the candidate sets differ in SIZE by 2-4x the bar is structurally
unpassable.** The registered 0.80 Jaccard was unreachable the moment hop's
feasible set turned out to be 46 edges, *even if abs's 11 were a perfect
subset* — which they are. The branch call F_METRIC is correct as registered
and the directed containment is what says what actually happened: the
`-log10` metric does not route pool traffic through *different* entry edges,
it selects **fewer of the same ones**. Register the directed containment
fraction alongside any future set-agreement bar.

## The POOL-GEOMETRY control DEMOTES this card's framing, and it is reported first

Nonselective over all 35 L178 actors (borrowed from L238's registered
demotion escape, **cited to L238 and not re-banked**; reported BEFORE the
branch per L223's rho-first rule):

- carrier **11** realised entry edges vs census median **14.0**, range
  **[5, 22]**, menu median 64 -> carrier percentile **0.286**.
- fraction-of-menu-used: carrier percentile **0.257**, census median 0.2063.
- Spearman(menu size, realised count) = **+0.3056** — bigger menus buy only
  slightly wider funnels.

**0.286 > 0.20, so `demotes_card` is TRUE.** Every one of these 35 cells
enters the same 303 pool cells through a handful of edges; 11 is unremarkable
among them. The narrow funnel is substantially a property of the **303 pool
cells' entry geometry**, not of the carrier. L211's "the real wiring funnels
pool traffic through fewer, fatter first steps" survives *against the null*
(11 < p05 15) but not *against the cohort*, and L238's escape — written one
tick earlier for a different reason — is what caught it.

## Leg (a): one statistic, mechanically expected, and my estimator broke a true identity

PREREG 0b declared in advance that weight-vs-used, T_L-vs-used and L_L-vs-used
are ONE statistic up to sign (both metrics are strictly decreasing in A[e] at
a fixed source) and that a positive rho is mechanically expected, not evidence.

- The 11 used edges carry **18.6%** of the carrier's out-mass and sit at
  out-weight ranks **[2, 7, 11, 13, 15, 16, 19, 23, 25, 48, 60]** of 69 —
  heavy-biased, but with two entries deep in the light tail (48, 60), and the
  single heaviest out-edge (rank 1) is **not** used.
- The parent read `identity_holds == False` (+0.2280 vs −0.1898). **The
  identity is true and the parent's estimator was wrong** — see the addendum.

## The addendum (l221b, POST-HOC, parent's writer cut, every gate re-run free)

`l221b_static.py` = `l221_static.py` lines 1-1812 VERBATIM (the parent sliced
at the leg-(a) log, writer/predictions/primary/leg-(b) CUT — the L213 pattern)
+ `l221b_tail.py`. 39 s. Parent `md5sum -c` GREEN afterwards.

**A. The rank identity holds EXACTLY under average ranks.**
`rho(w, used)` = **+0.272282** = `−rho(T_L, used)` = `−rho(L_L, used)`, both
`|err| = 0.000e+00`. The parent's estimator was `np.argsort(np.argsort(x))`,
an **ordinal** rank that assigns distinct ranks to tied values by array
position — and reversing the value order does not reverse positional
tie-breaking. The carrier's 69 out-edges have only **28 distinct weights**
(41 tied edges, largest tie group **10**, 47 of 69 ordinal ranks not
mirrored), because `log1p` of integer synapse counts above a floor of 4
produces heavy ties. **CERT-MONO (HALTING, 2,346)**: all 69·68/2 pairwise
order comparisons confirm T_L and L_L are exact order-reversals of the weight
— PREREG 0b's premise asserted, not trusted, which is what makes this a gate
on the estimator rather than an opinion.

**Method law: a tie-handling convention can refute a true analytic identity.
Average-rank the Spearman, or the sign identity you proved on paper will read
FALSE in the output.**

**B. The parent's 11-vs-16 comparison was in the wrong currency and
understated itself by 31%.** PREREG 0a flagged that `n_distinct_first_hops`
counts distinct *costs*; for the carrier the two agree (11 edges = 11 costs,
tie deficit **0**). For the **null** they do not: median **21.0 edges** vs
**16.0 costs**, median tie deficit **5.0**, and **99 of 100 draws** carry
ties. So L211's headline ratio is **1.909x in EDGES** vs **1.455x in COSTS** —
a cost-count contrast mixes narrowness with tie structure, and the clean
edge-currency contrast is the LARGER one.

## Leg (b): the entry points, and the two-pathway split

11 used edges -> 11 distinct targets, all but one ventral-cord intrinsic
(`relation = overlapping`; **4 of 5** of L178's pool-out-edge targets
realised, 4 of 5 feasible; 4 of the 11 used targets carry a pool out-edge):

| edge j | target gid | cell_type / side | T_L bits | pool cells served | pool out-edges | in L178's five |
|---|---|---|---|---|---|---|
| 14 | 65443 | IN17B004 L | 5.792 | **113** | 0 | no |
| 13 | 65290 | IN17B001 L | 6.040 | 55 | 0 | no |
| 64 | 72158 | IN27X014 R | 5.750 | 55 | 1 | **yes** |
| 67 | 75494 | IN06B033 L | 5.770 | 52 | 10 | **yes** |
| 25 | 66466 | IN17B004 L | 5.998 | 9 | 0 | no |
| 59 | 70458 | INXXX467 R | 6.438 | 7 | 12 | **yes** |
| 38 | 68053 | IN27X014 L | 5.840 | 5 | 0 | no |
| 12 | 64961 | IN02A019 R | 5.712 | 3 | 0 | no |
| 39 | 68338 | IN11B012 L | 5.515 | 2 | 0 | no |
| 4 | 8509 | i2 L (motor) | 5.605 | 1 | 0 | no |
| 62 | 71155 | IN06B042 R | 6.712 | 1 | 1 | **yes** |

**Four edges carry 275 of 303 pool cells (90.8%)** — the funnel inside the
funnel. And the split is anatomically legible: the two highest-traffic entry
points (j=14 IN17B004-L, 113 cells; j=13 IN17B001-L, 55 cells) carry **zero**
direct pool out-edges, while the L178-five members (j=67, j=59) carry 10 and
12. So the carrier reaches the motor pools through *both* a short direct-ish
route and a longer high-traffic indirect route, and the indirect one carries
more of the load. Note also that `fh_min` 5.5153 > `menu_min` 5.4963: the
realised cheapest first hop is not the cheapest available edge.

## Predictions

| # | registered | measured | |
|---|---|---|---|
| P1 | branch F_REAL | **F_METRIC** | FALSE |
| P2 | `n_distinct_first_hop_EDGES == 11` | **11** | TRUE |
| P3 | >=3 of L178's five realised | **4** | TRUE |
| P4 | `spearman(A_e, used) > 0` | +0.2280 (ordinal) / **+0.2723** (avg-rank) | TRUE |
| P5 | carrier count at/below the 20th census percentile | **0.286** | FALSE |

P1 and P5 are the two that mattered and both are FALSE: the funnel is
metric-specific AND it is not the carrier's. Registration was NOT amended;
the three premise corrections were all pre-measurement.

## Verification

**97,185 halting checks in this card's five new gates + 2,346 in the
addendum's sixth**, on top of ~1.99M re-running FREE inside the nine verbatim
slices.

- **CERT-D5 (6)** — L178's `n_targets` / `n_targets_with_pool_outedge` /
  `pool_outedges_from_targets` re-derived from its own expression and gated at
  INTEGER equality against the stored 5 (carrier) and 19 (twin). The parent
  never stored the identities, so the re-derivation is necessary and is
  therefore gated (the L219 CERT-219D pattern). Carrier's five:
  local `[14369, 16409, 17104, 18104, 21439]`.
- **CERT-CROFTS** — `power_iter(jv_crofts)` reproduces `l206/static.json`'s
  `lam1_crofts` 0.3881201140476021 at rel **0.000e+00**, against a bar
  **DERIVED** from that operator's own measured `rel_spread_crofts`
  (1.059e-07 = 10x) rather than a fixed 1e-9 (the L216 law).
- **CERT-FHE (93,930)** — the edge-index walker's `dist`/`si`/`hop` and
  `T_L[first-hop edge]` equal the certified `dijkstra_si` / `dijkstra_si_fh`
  at EXACT equality on all 303 pool cells for the carrier, the twin and all
  100 draws. The modified walker is GATED, never trusted (L210 CERT-MV).
- **CERT-DAG (909 = 303 x 3)** — every realised first hop is a MEMBER of its
  pool cell's feasible bitmask, and the realised set is a SUBSET of the
  feasible set, on all three metrics. Plus the mask sweep is asserted to reach
  a FIXPOINT (2 sweeps on every metric) — necessary because zero-length edges
  exist (`L_L == 0` for the `A_max` edge), so equal-distance propagation is
  real.
- **CERT-EDGEIDX** — `build_si_index`'s edge index map is a function of
  `csr_cols` ALONE (stable argsort), so `START`/`END`/`TGT0` are asserted
  IDENTICAL across the three metrics. Without this the three used-sets would
  not be comparable at all, and the whole card would be meaningless.
- **CERT-MONO (2,346, addendum)** — above.
- Inherited FREE: CERT-F4 + the gains at float equality + CSR orientation
  (69 out / 12 in) + the 20 pool sizes; CERT-REW (l169c P6); CERT-178's 420
  stored anatomical values + CERT-NULL's 8; **CERT-SI 240**; **CERT-MENU
  100**; **CERT-FH 61,819**; **CERT-211 434**; **CERT-SIGEN 1,922,356**.
- NINE verbatim source slices, forbidden-token audited, no lab module imported
  (L175). Seven inherited sha pins asserted by the BUILDER against the values
  L220 recorded, plus **TWO PARENT PINS**: `l211_tail.py` whole-file
  `01344b557db98d29` == what `l211_static.py`'s banner recorded, and
  `l220_tail.py` whole-file `8620a357d74f6f3e` == what `l220_static.py`'s
  banner recorded. **CERT-220SL = l220_tail.py lines 47-128**, sliced to CUT
  every cutwA block, the 0c gain leg and the writer, asserted positively
  (CERT-211, `build_si_index`, CERT-SIGEN) and negatively (`SUB_CUT`,
  `build_sub`, CERT-REWCUT/MENUCUT/WALKCUT/REBIND, all three L220 result
  blocks, `json.dump`).
- Generated sha **356598824b1f2a75**; addendum **a399d93ce5102a91**.
  `md5sum -c l221/prior.md5` GREEN (13 files) before the run; four prior
  `static.json` fingerprinted (size, mtime_ns) before and asserted unchanged
  after; `l221/parent.md5` re-verified GREEN after the addendum.

## Limitations

1. ONE substrate (f4wA). The cutwA leg is **deliberately deferred to L238**,
   which owns the two-substrate first-hop IDENTITY comparison nonselectively
   with BH-FDR; doing it here would double-bank it.
2. ONE null family (l169c degree-neutral destination swaps) — L207's
   cross-null law.
3. The null relocates only the CARRIER's destinations, so the 35-actor census
   is a DESCRIPTIVE cohort read. Its only job is the demotion check.
4. The out-weight Gini and L219's Spearman(w_e, u1[t_e]) are DESCRIPTION
   (observed while scoping, PREREG 0b.3 / section 5).
5. Metric 3 keeps `T_L` fixed and changes only path SELECTION; metric 2
   changes both. Agreement across all three would have been evidence about the
   length metric's domain choice, not about the transition law in general.
6. The feasible set is "feasible up to TOL = 1e-12" on the weighted metrics;
   the TOL = 0.0 set is reported beside it and is IDENTICAL on all three
   metrics here, so the tolerance did nothing.
7. A used-set is not a mechanism. Which of the three metrics a *biological*
   routing claim should use is undecided by anything in this card and needs a
   dynamical referent — seeded as L240.

## Artifacts

`banc/l221/{PREREG.md, static.json, addendum.json, VERDICT.md, run.out,
run.err, addendum.out, addendum.err, prior.md5, parent.md5}`; code
`banc/l221_{build,tail}.py` -> `l221_static.py` (1,987 lines),
`banc/l221b_{build,tail}.py` -> `l221b_static.py` (2,001 lines),
`banc/t251_containment.py`.
