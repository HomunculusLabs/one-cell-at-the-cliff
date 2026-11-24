# L219 PREREG — is the u1 deficit TARGET CHOICE or TARGET QUALITY?

Written BEFORE l219_tail.py existed and BEFORE any L219 number was measured.
Static, zero rollouts, zero settles, zero dynamics. Substrate f4wA, operator
`A = |W_beta| * g_f4wA` (the anatomical ABS form), actor = the L178/L206/L207/
L210 carrier (gi 1110, local LC_CAR), out-degree 69.

## 0. The object, and three premise corrections written in advance

L210 reduced the carrier's depth-invariant pool-reach deficit to ONE scalar,
the left-Perron overlap `K(c) = u1[c] * S_v / (u1 . v1)`, and L218 then showed
that closed form is EXACT (0.061% at d=50). The card asks what makes `u1[c]`
small. Under our `A[dst, src]` convention the left Perron relation is

    lam1 * u1[s] = sum_{e: src(e)=s} A[dst(e), s] * u1[dst(e)]

so with `E_c` = the carrier's out-edges, `w_e = A[t_e, c]`, `t_e = dst(e)`:

    S_car := sum_{e in E_c} w_e * u1[t_e] = lam1 * u1[c]                    (I)

### (0a) The card's "the weight distribution does the work" CANNOT mean the multiset

The l169c degree-neutral null relocates destinations with each weight
travelling with its SOURCE (L211's law, and `rewire_draws` sets
`extra_an = abs(G_F4WA * _vnp[cidx])`, i.e. the moved edge keeps its own
value). So the carrier's out-weight MULTISET is invariant across all 100 draws
by construction and cannot carry one point of the 11.4x. The only reading of
"the weight distribution does the work" that is not vacuous is weight-target
ALIGNMENT: whether the carrier's heavy edges sit on its LOW-importance
targets specifically. That is the quantity registered as TARGET CHOICE below.
The multiset invariance is not assumed — it is a HALTING gate (CERT-WMULT).

### (0b) The currency that carries the branch, registered before measuring (L218)

`u` is returned unit-L2 by `pi_dir`, and a unit-L2 normalisation across two
different operators is a CONVENTION (L210's own disclosure; L218 Q218-3 then
measured the same cell at percentile 0.940 in the invariant currency and 0.100
in the bare one). So the PRIMARY currency here is the scale-invariant

    U(c) := u[c] / mean(u)      Q(c) := mean_{e in E_c}(u[t_e]) / mean(u)
    align(c) := [ (1/m_out) sum_e w_e u[t_e] ] / mean_{e in E_c}(u[t_e])

with `m_out = sum_e w_e`. `U` and `Q` are invariant to the scale of `u`;
`align` is a ratio of two means of the SAME vector and is invariant on its
own. Identity (I) divided by `mean(u)` gives, EXACTLY,

    U(c) = (m_out / lam) * Q(c) * align(c)                                 (II)

which is the product decomposition the card asks for. The bare unit-L2
`u[c]` and the bare `mean_e u[t_e]` are reported BESIDE the invariant forms,
never instead of them. Identity (II) is gated per draw at rel < 1e-12.

### (0c) Observation status (Kriegeskorte 2009; the L214 rule)

While scoping I read `l210/static.json` and `l218/static.json` summary blocks.
Therefore the following are OBSERVED-DERIVABLE and are declared DESCRIPTION,
never branch-bearing: `K_REAL`, `u1[LC_CAR] = 4.0973e-04`, the null `u_car`
median/p05/p95 and the carrier's 0.0 percentile in it, `K_ratio_med 11.4016`,
`R_bare 11.4039`, `lam1 30.179788`, the gap 0.8928794, `D10 10.38807894033274`,
and L218's `C_car`/`A2` numbers. Every branch below is placed on an object I
have NOT seen: the per-target contribution table, `Q` and `align` (real and
per-draw), the weight-matched semi-analytic nulls, and the cohort tables.

Selection caveat, registered: the carrier was SELECTED for being extreme on a
related statistic, so every carrier-vs-COHORT percentile (the 35 L178 actors)
is DESCRIPTIVE. The branch rests only on carrier-vs-its-OWN-nulls contrasts,
which are legitimate because those nulls relocate the carrier's OWN edges.

## 1. Registered quantities and nulls

- **N1 — the l169c draws (100, seed 16943, the certified stream).** Per draw
  k: rebuild the operator exactly as L210's loop does, run `pi_dir` in BOTH
  directions, and require float equality with `l210/static.json`
  `rows_per_draw[k]` on `lam`, `lam_left`, `K`, `u_car` BEFORE any L219
  quantity is read from `u_k` (CERT-219D). Then record `U_k`, `Q_k`,
  `align_k`, `m_out_k`, identity-(II) residual.
- **N2 — WEIGHT-MATCHED semi-analytic null, MENU-MATCHED leg (primary for
  Q219-3).** Keep the carrier's 69 out-weights; redraw the 69 targets i.i.d.
  uniformly from the l169c RELOCATION MENU, i.e. `loc_f4[dst_all[pool_rows]]`
  with `pool_rows = where(_blk_f4 & (src_all != GI_CARRIER))`, which is
  exactly the array `rewire_draws` samples its partner edge from (so the
  target distribution is edge-destination-weighted, as in the real null).
  2000 draws, seed 21901. Statistic `S = sum_e w_e u1[T_e]` on the REAL u1.
- **N3 — WEIGHT-MATCHED, NODE-UNIFORM leg (the card's literal "graph-wide").**
  Same, targets i.i.d. uniform over all NL nodes. 2000 draws, seed 21902.
  Reported, not branch-bearing on its own.

## 2. Branches, registered with the full SIGN x BAND table (L205)

**Q219-1 (PRIMARY).** With `rQ = median_k(Q_k) / Q_real` and
`rA = median_k(align_k) / align_real`, bar 5x as the card sets it:

- `TARGET_QUALITY`  : rQ > 5 and rA <= 5
- `TARGET_CHOICE`   : rA > 5 and rQ <= 5
- `BOTH_EXCEED`     : rQ > 5 and rA > 5  (the missing cell, registered)
- `NEITHER`         : rQ <= 5 and rA <= 5 -> report the product decomposition
  and call it neither, as the card instructs
- `DEGENERATE`      : any draw failing convergence, the multiset gate, or the
  identity bar -> no branch is called at all

Median composition is NOT performed (L218): `median(Q*align) != median(Q) *
median(align)`, so `rQ` and `rA` are reported as separate marginals, the
per-draw product ratio `median_k(U_k)/U_real` is reported as its own number,
and the per-draw Spearman between `log Q_k` and `log align_k` is reported so
a reader can see whether the factors trade off.

**Q219-2 (the card's leg (a)).** Per-target contribution table
`c_e = w_e * u1[t_e]`: top-10 (with `w_e`, `u1[t_e]`, share of `S_car`),
Gini of `{c_e}`, Gini of `{w_e}`, Spearman(`w_e`, `u1[t_e]`), and `Q`/`align`
for carrier vs twin (local LC_TWIN) vs the 33-member family (median, p05,
p95). Cohort percentiles DESCRIPTIVE per 0c.

**Q219-3 (the card's leg (b)).** `ratio_wm = median(S_draw) / S_car` on N2.
Registered bar: if `ratio_wm > 5` then "its targets are globally unimportant"
reproduces the deficit WITHOUT touching the graph's eigenvector, and the
QUALITY reading is independently supported; if `ratio_wm <= 2` the deficit
needs the null's global eigenvector change and leg (b) REFUTES the
semi-analytic account. Also report `S_car`'s percentile in N2 and N3.

**Q219-4 (the card's leg (c)).** The N1 per-draw `Q_k` and `align_k`
distributions (median, p05, p95) with the real values' percentiles in each,
plus `median_k(lam_k)/lam1` so the third factor of (II) is quantified rather
than assumed negligible.

**Q219-5 — relation to L211, declared up front per the card.** L211 asked the
same question in the search-information currency and found the whole +3.58-bit
routing excess in the REMAINDER with the first hop INSIDE its nulls. L219 is
a decomposition of the SAME deficit in a different currency; whichever result
agrees, L219 CITES L211 and does NOT re-bank the finding as independent
evidence. Any agreement is reported as one finding measured twice.

## 3. Predictions (scored, never amended after measurement)

- **P1**: Q219-1 lands on `TARGET_QUALITY`.
- **P2**: CERT-WMULT passes — the sorted carrier out-weight vector is FLOAT-
  EQUAL to the real one in all 100 draws, and the out-degree is 69 in all 100.
- **P3**: `ratio_wm` (N2) lands within a factor of 2 of L210's 11.4x, i.e. in
  [5.70, 22.81].
- **P4**: `align_real < 1.0` — the carrier's heavy edges sit on its
  below-average-importance targets.
- **P5**: the carrier's contribution Gini exceeds the 33-family median.

## 4. Guards

- Every `pi_dir` convergence field re-asserted; `U1.min() >= 0` re-asserted.
- Identity (II) per draw and for the real wiring at rel < 1e-12; `S_car ==
  lam1 * u1[LC_CAR]` at rel < 1e-12 (the identity (I) gate).
- Degeneracy: if `mean(u_k) <= 0` or `mean_e u_k[t_e] <= 0` for any draw,
  halt — scoped to exactly the quantities read (L218 A1: a numerical guard
  must not be phrased so broadly that it fires on a known anatomical zero).
- Prior artifacts opened READ-ONLY with (size, mtime_ns) fingerprinted before
  and asserted unchanged after; `md5sum -c` green against `l219/prior.md5`
  before and after the run.
- Code is generated by `l219_build.py` from the SAME six certified verbatim
  slices L218 used plus a new `l219_tail.py`; the five inherited sha pins and
  the l210 parent pin are asserted by the BUILDER (L178/L213 pattern).
