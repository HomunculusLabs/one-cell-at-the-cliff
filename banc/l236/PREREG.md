# L236 PREREG — is the 11.4x SPECIAL, or is it the MENU?

Written BEFORE `l236_tail.py` existed and BEFORE any per-cell L236 ratio was
computed. Static: zero rollouts, zero settles, zero dynamics. Substrate f4wA,
operator `A = |W_beta| * g_f4wA` (the anatomical ABS form), left Perron vector
`U1` exactly as L210/L218/L219 certify it.

Parent card: L219 (`l219/PREREG.md`, `l219/static.json`), whose Q219-3 showed
that a *menu-matched, weight-matched* null reproduces L210's full 11.4x to
0.65% while holding `u1` completely fixed — so the whole quantity is computable
for EVERY cell in one pass, with no eigendecomposition per draw. This card asks
it NONSELECTIVELY (Kriegeskorte 2009 step 1; the L231/L233/L235 discipline).

## 0. Premise corrections, written in advance

### (0a) The card's two populations are ONE population — MEASURED, not assumed

The card says "for all 35 L178 actors AND for every DN-source cell in the
l169c block". `l236_probe.py` (SLICE P = `l219_static.py` lines 1-989 verbatim
+ a description-only tail) measured: the block has **1,253 distinct DN source
cells**, all **35** L178 actor locals are already among them, and the union is
**exactly 1,253**. So there is ONE family of size 1,253 and no cross-population
multiplicity to manage. DESCRIPTION (probe output, `l236/probe.out`).

### (0b) The "weight-matched" null's MEAN is analytic and weight-INDEPENDENT

For a cell with out-weights `w` and `k = |w|` out-edges, drawing targets `T`
i.i.d. uniform from the menu gives, by linearity and for ANY weight multiset,

    E[S_draw] = (sum_e w_e) * mean(u1[MENU]) = m_out * mu_MENU          (A)

So matching the null to the cell's own weight multiset cannot move the null's
**mean** at all — it only shapes its **variance**. Two consequences, both
registered:

1. The RATIO has a closed form and needs no draws:
   `r_mean(c) := m_out(c) * mu_MENU / S_c = Q_menu / (Q_c * align_c)`.
   The draws are needed ONLY for the tail probability.
2. L219's own currency, `r_med = median_B(S_draw)/S_c`, is **biased downward
   at low out-degree**, because the null's median/mean ratio is degree
   dependent. The probe measured it: **0.182** (n_out 1), 0.385 (2), 0.556 (3),
   **0.646** (5), **0.832** (10), **0.944** (40), **0.971** (69). Across a
   population whose out-degree runs 1-456 (median 30) `r_med` is therefore NOT
   a comparable currency, while `r_mean` is degree-free by (A).

**REGISTERED: the branch is carried by `r_mean`.** `r_med` at B draws is
reported beside it as the L219-comparable companion (the carrier's `r_med` must
reproduce L219's stored **11.4757** at float equality, CERT-236C), never
instead of it. This is the L218/L228/L233 "register which currency carries the
branch" law applied before the measurement rather than after.

### (0c) Observation status (L214; Kriegeskorte 2009)

While scoping I read `l219/static.json`'s `Q219_2_table` family medians
(Q 2.3413, align 1.0121) and `Q219_3_weight_matched` (carrier `r_med`
11.4757). Therefore the **35-actor cohort's** ratio distribution is
OBSERVED-DERIVABLE by arithmetic (median `r_mean` ~ 0.98) and is declared
**DESCRIPTION**, never branch-bearing. Every branch and every prediction below
is placed on the **1,253-cell block population**, on its BH-FDR verdict, and on
the homolog — none of which I have computed or read.

### (0d) The BH family's RESOLUTION FLOOR decides whether the leg exists (L225)

With m = 1,253 the BH rank-1 bar at q = 0.05 is **q/m = 3.9904e-05**, while a
permutation p-value's floor is `1/(B+1)`. At L219's B = 2,000 the floor is
4.9975e-04 = **12.5x too coarse**: no cell could be rejected at rank 1 and the
card's FDR leg would be unreachable BY CONSTRUCTION. **REGISTERED: B = 30,000
for every cell** (floor 3.3332e-05 < 3.9904e-05), uniform, with NO adaptive
escalation. The artifact prints the floor against the rank-1 bar.

### (0e) Direction, and the second family

The deficit claim is "S_c is LOW", so the registered one-sided p is
`p_low(c) = (1 + #{S_draw <= S_c}) / (B + 1)`. `p_high` (targets unusually
important) is a SEPARATE family and gets its own BH; it is reported, and the
two are never pooled.

### (0f) The menu null is CRUDE, so a large rejection count is not a result

The menu is uniform over block edge destinations and ignores neuropil, side and
cell type, so many cells will have targets atypical of the pooled block.
**REGISTERED IN ADVANCE: the count of BH rejections is NOT the instrument.**
The instruments are (i) the population distribution of `r_mean` and (ii) the
carrier's RANK in it. A large rejection count is reported as a property of the
null's crudeness, never as a finding.

### (0g) Degree confound screen (L213)

`r_mean` is scale-free in `m_out` by construction but may still track
out-DEGREE (more targets -> sample mean closer to the menu mean). Registered
screen: Spearman(`r_mean`, `n_out`) and Spearman(`r_mean`, log `m_out`) over
the 1,253 cells, midrank (L221). If either |rho| >= 0.30 the carrier's
population percentile is ALSO read inside a degree-matched sub-cohort
(`n_out` in [55, 83] = 69 +/- 20%) and that reading, not the raw one, carries
P2.

### (0h) The homolog leg (L207/L212: a homolog that DISAGREES is as informative)

The bilateral homolog is the right DNp33, whose global id is **read from
`l207/static.json["Q2_mirror"]["mirror_identity"]["gi"]` in code** and never
hand-typed (the L228/L251-257 derive-never-retype law). Its `r_mean`, rank,
`p_low` and `q` are reported whether or not they agree with the carrier.

### (0i) The positive control is an EXACT identity, and it is HALTING (L224)

Because `MENU` is literally the multiset of destinations of the block's own
edges, the **edge-count-weighted** mean of each cell's unweighted mean target
importance equals `mu_MENU` EXACTLY:

    sum_c (sum_{e in blk(c)} u1[t_e]) / sum_c n_blk(c) == mu_MENU        (B)

So the population's target-importance distribution is CENTRED by construction
and only its SHAPE is informative: if the median cell reads ~1x, the
centring is doing it; if the median cell reads ~5x, `u1`'s tail is. Gate (B) at
rel < 1e-12 (HALTING), on the carrier-INCLUSIVE block so the menu's own
carrier exclusion is accounted for explicitly.

### (0j) All out-edges vs block out-edges

L219's carrier statistic used ALL 69 operator out-edges, which for the carrier
are all block edges. For a general block DN they need not be. **PRIMARY uses
ALL operator out-edges** (so the carrier's numbers are bit-identical to L219's)
and the block-restricted companion is reported, together with each cell's
block-edge fraction and Spearman(`r_mean`, block fraction).

### (0k) What the cost slice is, and what admits it (L226/L235)

`l236_static.py` does NOT re-run L219's 100-draw per-draw eigendecomposition
(the ~370 s loop behind `cert_219p`/`cert_rebuild`/`cert_219d`). It is built
from four VERBATIM slices of `l219_static.py` — SLICE P (1-989, the operator +
CSR + block mask + certified `U1`), SLICE H (1231-1282, the helpers), SLICE C
(1476-1493, the 35-actor cohort loop), SLICE W (1548-1556, `wm_null`) — and the
cut is admitted ONLY by exact reproduction of the parent's STORED output:
CERT-236A (every leaf under the 15 keys SLICE P assigns, bar DERIVED from the
artifact per L224), CERT-236B (the whole `Q219_2_table`, including all 35
actors x 9 fields, at float equality), CERT-236C (the carrier's real decomp,
identity (I) and (II), the stored menu shape, and L219's own `wm_null` at seed
21901 reproducing stored `r_med` 11.4757 / `S_car` percentile / `Q_med` /
`align_med`). The generalised per-cell kernel is admitted by EXACT agreement
with SLICE W's `wm_null` on the carrier (the CERT-MV pattern).

## 1. The registered question and its branch

**Q236-1 (PRIMARY).** Over the 1,253 block DN source cells, what is the median
`r_mean`, and where does the carrier sit?

- `median r_mean >= 5.0`  -> **MENU_PROPERTY**: the 11.4x is a property of the
  MENU being edge-destination weighted while individual cells are not, and the
  whole K-deficit family (L206/L210/L218/L219) demotes to a restatement of
  "the block's edge-destination law is not the node law". This MUST be said in
  the digest if it fires.
- `1.6 <= median r_mean < 5.0` -> **PARTIAL**.
- `median r_mean < 1.6` -> **CELL_SPECIFIC**: the deficit is cell-specific and
  L237 (why those targets have low `u1`) is the next question.

**Q236-2.** BH-FDR over the 1,253 `p_low` values at q = 0.05: the carrier's
rank, its q, the number of rejections, and the resolution floor against the
rank-1 bar.

**Q236-3.** The homolog (0h), reported whether it agrees or not.

**Q236-4 (DESCRIPTION).** The 35-actor cohort, for continuity with L219 — and
declared observed-derivable by 0c.

## 2. Predictions (registered before any per-cell ratio was computed)

- **P1**: Q236-1 lands on **CELL_SPECIFIC** (population median `r_mean` < 1.6).
- **P2**: the carrier is in the TOP 10 of 1,253 by `r_mean` (at most 9 cells
  strictly above it); read in the degree-matched cohort instead if 0g bites.
- **P3**: the fraction of cells with `r_mean >= 5.0` is <= 0.05.
- **P4**: the population `r_mean` distribution is right-skewed with
  median/mean <= 0.80.
- **P5**: |Spearman(`r_mean`, `n_out`)| < 0.30 (the degree screen does not
  bite).
- **P6**: the homolog's `r_mean` lies strictly between 1.0 and the carrier's
  (a partially-agreeing homolog).

## 3. Registered escapes

- If MENU_PROPERTY fires, the digest and the draft must restate the K-deficit
  family as a statement about the block's edge-destination law, and L237 is
  rewritten as a question about the MENU rather than about the carrier.
- If the degree screen (0g) bites at |rho| >= 0.30, the raw population
  percentile is NOT reported as the carrier's standing; the degree-matched one
  is, and P2 is scored on it.
- If the BH family's floor turns out not to clear the rank-1 bar after the
  measured m (e.g. because some cells are dropped), the FDR leg is scored
  FALSE BY UNMEASURABILITY (L222) rather than loosened.
- No live change. No draft edit. `sessions/` untouched.
