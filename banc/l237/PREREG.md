# L237 PREREG — WHY do those 69 cells have low u1? the destination-geometry leg

Registered 2026-11-24 (tick 269) BEFORE any measurement of this card's
quantities. Static, zero rollouts, no RNG except the registered permutation
seeds below. Writes `l237/static.json` ONLY.

## The question

L219 decomposed the carrier's left-Perron overlap `u1[c]` over its 69
out-edges and found the deficit lives in **target QUALITY**: `Q = mean(u1 over
the 69 targets) / mean(u1) = 0.18102` (stored `l219/static.json
Q219_1_primary.real.Q`), i.e. the carrier points at cells whose u1 is 5.5x
below the graph mean, while its alignment term is ~1.11. A decomposition is
not a mechanism. This card asks what makes those 69 destination cells low-u1
cells, against the population the l169c null itself draws from: the MENU, the
block's 49,076 edge destinations over 9,803 distinct cells.

## Premise corrections (registered FIRST, before any new measurement)

**0a — u1 is a LEFT Perron vector, so the card's nesting order leads with the
wrong side of the operator.** Identity (I), already asserted HALTING inside
SLICE R, is `lam1 * u1[s] = sum over s's OUT-edges of w_e * u1[t_e]`. So
`u1[t]` is determined by `t`'s own OUT structure, not by its in-structure. The
card's registered nesting is "(i) in-mass alone, (ii) in-mass + out-mass,
(iii) super_class fixed effects, (iv) the Perron-residual high-leverage
cells". That order is KEPT verbatim so the comparison is the card's and not a
convenient one, and the structural asymmetry is registered as a PREDICTION
(P1) rather than used to rewrite the question.

**0b — the three-term decomposition is an EXACT IDENTITY, not a model.**
`u1[t] = (m_out(t)/lam1) * Q(t) * align(t)` holds to float resolution for
every cell with a measurable Q, so a model containing all three wins by
construction and held-out scoring CANNOT fix that (held-out protects against
overfitting, not against an identity). The three-term form is therefore
EXCLUDED from the nested model comparison and reported as a DECOMPOSITION
whose residual is a halting gate.

**0c — the outcome has EXACT ZEROS (L236 amendment 0L).** u1 has exact zeros
on this graph, so any log-scale fit is undefined on part of its own
population (L224: a zero in the outcome is a MODEL-FAMILY verdict, not a
missing value). Registered in advance: the zero fraction of u1 on the menu and
on the 69 targets is measured and reported BEFORE any fit; the PRIMARY scoring
currency is the MIDRANK Spearman (L221), which admits zeros as a tie group;
the log-OLS reading is a DISCLOSED SECONDARY on the `u1 > 0` subset, reported
beside the zero fraction's covariance with every predictor and with
super_class.

**0d — held-out scoring.** 5-fold CV, folds assigned by one permutation of the
menu-cell index at seed 23701. Outcome `y = midrank(u1)` computed ONCE over
the full population (the rank transform is shared across folds: this leaks the
marginal distribution only, which is intrinsic to a rank regression, and is
disclosed rather than hidden). Score = midrank Spearman of prediction against
`y` on the HELD-OUT fold, averaged over folds, per-fold values reported.

**0e — in-mass and out-mass are correlated on this graph.** rho(in-mass,
out-mass) over the menu is reported FIRST, because a nested gain of ~0 can
mean "redundant with what is already in the model" rather than
"uninformative", and the two readings are different claims.

**0f — Q1's comparison population is the EDGE-weighted menu, not the cell
set.** The l169c null relocates the carrier's edges onto a random block edge
destination, so the honest reference for "are the 69 a biased draw" is a draw
of 69 EDGE destinations from MENU (49,076 edges), matching L219's own null
rather than a uniform draw over 9,803 cells.

**0g — multiplicity.** The per-super_class composition tests form a BH-FDR
family; the permutation resolution floor `1/(B+1)` is reported against the
rank-1 bar `q/m` (L225), and the number of classes tied AT the floor is
reported (L236's floor-tie law).

**0h — the bilateral homolog is the cheapest control available (L207/L212),
and L236 measured it DISAGREEING BY BEING MORE EXTREME.** The right DNp33's
global id is READ IN CODE from `l207/static.json Q2_mirror.mirror_identity.gi`
(never hand-typed; the derive-never-retype law) and its targets' Q and
super_class composition are reported beside the carrier's.

**0i — RELATION TO L233, DECLARED UP FRONT (the Q219-5 discipline).** L233
asked whether destination geometry explains the `A_inf` asymptote in the
ARRIVAL currency on the BANC cord subnet and found operator-native in-mass is
a SUPPRESSOR (signed share -0.155 / -0.025, residual carrying 115.5%/102.5%).
L237 asks the analogous question in the DEPARTURE currency (the left Perron
vector) on the f4wA block. If both come back "in-structure does not explain
it", that is ONE mechanism — the left Perron vector is an out-reach quantity
by identity — and must NOT be banked as two findings. This card cites L233 and
says so explicitly in its limitations.

**0j — the leverage leg is DESCRIPTION.** The high-residual cells of the best
non-identity model are identified and annotated, with no branch resting on
them (they are selected for being extreme on the model's own residual;
Kriegeskorte 2009).

**0k — out-degree 0 implies u1 == 0 BY PROOF, not by measurement.** Identity
(I) gives `lam1 * u1[s] = sum over s's out-edges`, so a cell with no
out-edges has u1 exactly 0, and so does a cell all of whose targets have
u1 == 0. Registered as a HALTING gate (every zero-u1 menu cell satisfies one
of the two), never as a finding.

**0L — the mechanistic leg (Q2b), which is the card's actual answer.** Because
0b's identity holds for every measurable cell, "why is u1 low on these 69
cells" has an EXACT answer in the identity's own currency: decompose the 69
targets' mean log-u1 deficit against the menu's into the three log terms
(m_out, Q, align), whose shares sum to 1 BY IDENTITY. Registered as a signed
share with every sign its definition admits (L211/L233): a term may be a
SUPPRESSOR.

## Registered questions and branches

**Q1 — composition.** Are the carrier's 69 target edges a biased draw from
the edge-weighted menu in super_class? Statistic `D_max = max_class |share_69
- share_menu|`, permutation null B = 20,000 draws of 69 edge destinations from
MENU at seed 23702; per-class two-sided permutation p with BH-FDR.
Branches: **C_BIASED** if the D_max permutation p < 0.05; **C_TYPICAL**
otherwise.

**Q2 — what predicts u1[t]?** Nested, in the card's own order, scored held-out
per 0d on the 9,803 menu cells:
`M0` intercept; `M1` log1p(in-mass); `M2` + log1p(out-mass);
`M3` + super_class fixed effects; `M4` + log1p(in-degree), log1p(out-degree).
Branch on `rho1 = held-out Spearman of M1`:
**IN_STRUCTURE_EXPLAINS** if `rho1 >= 0.70` — and then the carrier's deficit
is "it points at low-in-degree cells" and must be restated that way
everywhere, including L210's and L218's framing (the card's registered honest
escape); **PARTIAL** if `0.30 <= rho1 < 0.70`; **NOT_IN_STRUCTURE** if
`rho1 < 0.30`.

**Q2b — the identity decomposition (0L).** Shares of the 69 targets' log-u1
deficit carried by log m_out, log Q and log align, summing to 1 at float
resolution. Bands: **M_OUT_MASS** if the m_out share >= 0.50;
**M_RECURSES** if the Q share >= 0.50 (the deficit is their own targets'
deficit — it recurses rather than resolving into a local quantity);
**M_ALIGN** if the align share >= 0.50; **M_MIXED** if none reaches 0.50.
Any share may be negative (a SUPPRESSOR), per L211/L233.

**Q3 — robustness.** The Q2 branch recomputed (i) on the `u1 > 0` subset in
the log currency, (ii) with the menu restricted to cells of out-degree >= 1.
Branch **H_ROBUST** if the Q2 branch label is unchanged under both, else
**H_FRAGILE**.

## Predictions (registered before measurement)

- **P1** Q2 branch = **NOT_IN_STRUCTURE** (`rho1 < 0.30`), because u1 is an
  out-edge identity (0a).
- **P2** `rho_heldout(M2) - rho_heldout(M1) >= 0.10`: adding the out-side
  predictor is the step that buys the prediction.
- **P3** Q1 = **C_BIASED** (D_max permutation p < 0.05).
- **P4** Q2b = **M_RECURSES** (the Q share >= 0.50): the 69 cells are low-u1
  because THEIR targets are low-u1, not because they are small cells.
- **P5** super_class adds < 0.05 held-out Spearman over M2 (geometry beats
  taxonomy on this graph).
- **P6** the u1 zero fraction on the menu is in (0, 0.05).

## Certification (HALTING)

- **SLICE P** = `l219_static.py` lines 1-989 VERBATIM (literal PREFIX):
  data, annotations, pools, f4wA, the CSR, CERT-F4/REW/178/NULL/206/MV/LEFT,
  the l169c block mask, and the certified left Perron vector U1.
- **SLICE MID1** = `l236_mid1.py` VERBATIM; **SLICE MID2** = `l236_mid2.py`
  VERBATIM — L225's law: re-use a prior card's CERTIFICATION BLOCK as a source
  slice rather than re-implementing it. These carry CERT-236A (artifact-derived
  coverage over the keys the slices assign) and CERT-236B (the whole stored
  `Q219_2_table`, 35 actors x 9 fields).
- **SLICE H** = `l219_static.py` 1231-1281 (gini219/_rank219/spear219/
  decomp219); **SLICE R** = 1284-1309 (the carrier's 69 out-edges, identities
  (I) and (II)); **SLICE T** = 1459-1474; **SLICE C** = 1476-1501;
  **SLICE M** = 1536-1545 (the MENU).
- **SLICE D** = `l231_tail.py` 429-450 VERBATIM (midrank/spearman, bit-
  identical to the slice L233 and L235 used).
- **CERT-237D (HALTING)** — this card's vectorised decomposition reproduces
  SLICE H's `decomp219` on EVERY measurable menu cell, field by field, at
  float equality. A new kernel is admitted only by exact agreement with the
  certified one (the CERT-MV/CERT-236K pattern).
- **CERT-237Z (HALTING)** — 0k's proof: every zero-u1 menu cell has
  out-degree 0 or all-zero-u1 targets.
- **GATE-IDENT (HALTING)** — Q2b's three log shares sum to 1 at float
  resolution, with the bar DERIVED from the operands' magnitudes, never from
  the result's (L233's law).
- Pins: the parent's own banner records `l219_tail.py`'s sha and that tail is a
  literal SUFFIX of the parent; `l219/static.json` has no banner of its own
  (DISCLOSED by L236). `md5sum -c l237/prior.md5` GREEN before and after;
  read-only artifact `(size, mtime_ns)` unchanged after the run. AST walks
  prove no lab module imported (L175), every kept slice write-free, and
  exactly ONE write site.
