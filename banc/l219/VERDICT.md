# L219 VERDICT — the u1 deficit is TARGET QUALITY, and the weights point the other way

Branch **TARGET_QUALITY** (registered), Q219-3 **WM_REPRODUCES**.
Predictions **4 of 5** (P4 FALSE, with its SIGN inverted — see below).
Static: zero rollouts, zero settles, zero dynamics. PREREG `l219/PREREG.md`
written before `l219_tail.py` existed and before any L219 number was measured.

## The identity, and what it resolves to

Under `A[dst,src]`, `lam1*u1[c] = sum_e w_e u1[t_e]` over the carrier's out-edges
(identity I, measured rel **4.21e-16**). In the scale-invariant currency the
PREREG registered (L218's law),

    U(c) = (m_out / lam) * Q(c) * align(c)        (identity II, max rel 8.29e-16)

with `U = u[c]/mean(u)`, `Q = mean_e u[t_e]/mean(u)`, `align = weighted/unweighted`
mean of the same 69 target importances.

| | carrier (real) | l169c draws (median) | ratio |
|---|---|---|---|
| `U` | 0.169624 | 1.934112 | **11.4024** (per-draw product median) |
| `Q` (target QUALITY) | 0.181022 | 2.293065 | **12.6673** |
| `align` (target CHOICE) | 1.113626 | 1.000144 | **0.8981** |
| `lam` | 30.179788 | 30.179083 | 0.999977 |
| `m_out` | 25.393987 | 25.393987 | 1 by construction (CERT-WMULT) |

`rQ = 12.67 > 5` and `rA = 0.90 <= 5`, so the registered bar lands on
**TARGET_QUALITY** with no ambiguity. The carrier's 69 out-edges point at cells
whose left-Perron importance averages **0.181x an average node's** — 5.5x below
the graph mean, 12.7x below what relocation offers — while its weight-to-target
alignment is essentially the only thing working in its favour.

Median composition is NOT used: `rQ` and `rA` are separate marginals, `11.4024`
is the median of the PER-DRAW product, and Spearman(log Q, log align) = +0.134
says the two factors barely trade off.

## P4 is wrong by SIGN, and that is the second finding

I registered `align_real < 1.0` (heavy edges on its worst targets). Measured
**1.113626**, at percentile **0.92** of its own 100 draws: the real wiring's
weights sit on its *above*-average targets more than 92% of relocations do. The
alignment is a **+11% partial compensation** against an 1140% deficit. Target
choice in the weight-alignment sense is not merely absent — it points the other
way, and it is nearly maxed out while doing so.

Q219-2 says why it cannot matter here: the carrier's out-weight Gini is
**0.1493** (the family median is 0.1530, the twin 0.1489 — a near-constant of
this cohort under log1p synapse weighting), while its contribution Gini is
**0.8351**. Spearman(`w_e`, `u1[t_e]`) = **+0.067**. Nearly-flat weights
multiplying a heavy-tailed target-importance vector: the concentration of
`c_e = w_e u1[t_e]` (top-1 target 25.4% of `S_car`, top-10 83.2%) is entirely
the `u1[t]` tail. A statistic whose spread is 0.15 cannot explain an 11.4x gap.
The top contributor is one target at 2.83x mean importance carrying a quarter of
the carrier's whole Perron overlap.

## Q219-3: the deficit needs NO eigenvector change at all

Holding the **real u1 completely fixed**, keeping the carrier's exact 69
weights, and redrawing only its targets from the l169c relocation menu
(`loc_f4[dst_all[pool_rows]]`, 49,076 block edge destinations / 9,803 distinct
cells, 2000 draws, seed 21901):

- median `S_draw / S_car` = **11.4757** vs L210's full-null `K_ratio_med`
  **11.4016** — **0.65% apart**, from an instrument with no eigendecomposition
  of any perturbed operator in it.
- `S_car` percentile **0.0000** (0 of 2000).
- the semi-analytic null's `Q_med` **2.30737** vs the real draws' own `Q_med`
  **2.293065** — 0.6% apart. The 100 relocated operators' target quality is
  reproduced by resampling targets against the unperturbed eigenvector.

So the 11.4x is not a spectral consequence of rewiring. It is a statement about
*which cells the carrier's 69 out-edges land on*, measurable against the fixed
graph.

### The card's literal null would have understated it 2.4x

The node-uniform leg (the card's literal "graph-wide distribution") reads only
**4.7309**. Its own `Q_med` is **0.95607** — the built-in positive control: a
uniformly drawn node averages the graph mean by construction. The l169c menu is
**2.4x richer** than a uniform node because it is *edge-destination weighted*
(in-degree weighted within the DN→cord block), and the real null samples that
menu. **Method law: when a semi-analytic null stands in for a structural one,
its SAMPLING LAW is load-bearing — matching the real null's menu and drawing
nodes uniformly differ here by 2.4x, i.e. more than the entire effect most cards
report.** Both legs are reported; the menu-matched one is the registered primary
precisely because it is the one the real null actually draws from.

## Honest limits

- Cohort comparisons are DESCRIPTIVE (PREREG 0c, Kriegeskorte 2009): the carrier
  was selected for being extreme on a related statistic. Its `Q` is the lowest
  of 33 family actors (family median 2.3413, p05 0.2202; twin 1.1796) and its
  `align` sits at family percentile 0.848 — both quoted as description, with the
  branch resting on the two nulls that relocate the carrier's OWN edges.
- One substrate (f4wA), one operator (anatomical ABS), one null family.
- A decomposition is not a mechanism: "its targets are globally unimportant"
  pushes the question down to *why those cells have low `u1`*, which is the
  destination-geometry card (L237, seeded) and must declare its relation to
  L233.
- **Q219-5, declared in the PREREG:** L211 asked this question in the
  search-information currency and put the excess in the REMAINDER with the first
  hop inside its nulls. L219's "the menu, not the weights" agrees with L211's
  "selection, not the first-hop menu size" in spirit; it is CITED to L211 and
  not re-banked as independent evidence.

## Verification

**8,906 halting float equalities in this card's own three new gates**, on top of
L210's and L206's re-running free inside the verbatim slices.

- **CERT-219P** (1,106): every `l210/static.json` headline value plus all 100
  `rows_per_draw` rows x 11 fields reproduced at float equality, and L210's
  branch asserted still `B_CLOSED_FORM`, BEFORE any L219 quantity was read.
- **CERT-WMULT** (7,200): the PREREG 0a premise MEASURED, not assumed — in all
  100 draws the carrier's out-degree is exactly 69, the sorted out-weight vector
  is float-identical to the real one, and the full (weight, target) multiset
  rebuilt two independent ways (from `null_changed` relocations and from the
  draw's own `(ls2, ld2, va2)` arrays) agrees by EXACT ARRAY EQUALITY.
- **CERT-219D** (600): `lam`, `lam_left`, `K`, `u_car`, `spread_r`, `spread_l`
  for all 100 draws reproduced at float equality from my own operator rebuild —
  this is what proves the `u_k` vectors read here ARE the certified draws' left
  Perron vectors (the parent stores the scalars, not the vectors).
- Identity (I) and (II) gated at rel < 1e-12 for the real wiring, all 100 draws,
  and all 35 cohort actors (measured max 8.29e-16).
- SIX verbatim source slices, forbidden-token audited, no lab module imported
  (L175); FIVE inherited sha pins plus the l210 parent pin asserted by the
  BUILDER. Generated sha256 `fcef1ff55e0beedb2fdd5619e95705b63bb6acfb76603f5d3fa01e0e18715f0a`.
- Six prior artifacts opened READ-ONLY with (size, mtime_ns) fingerprinted
  before and asserted unchanged after; `md5sum -c` green against
  `l219/prior.md5` before the run.

Artifacts: `l219/{PREREG.md, static.json, VERDICT.md, run.out, run.err,
build.out, prior.md5}`, code `l219_{build,tail}.py -> l219_static.py`
(1,672 lines).
