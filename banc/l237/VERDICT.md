# L237 VERDICT — WHY do those 69 cells have low u1?

Run 2026-11-24 (tick 269). `l237_static.py` 1,841 lines sha256
`e6500e681a50cd64`, **13.8 s** on om, `nice -n 15 timeout 1700`, peabrain venv.
PREREG `l237/PREREG.md` registered FIRST, with twelve premise corrections
(0a-0L) and **ZERO amendments** to any registered quantity.

## Branches

| question | branch |
|---|---|
| Q1 composition of the 69 vs the edge-weighted menu | **C_TYPICAL** |
| Q2 nested held-out prediction of u1[t] | **PARTIAL** |
| Q2b the identity decomposition (the mechanism) | **M_RECURSES** |
| Q3 robustness | **H_ROBUST** |

Predictions **4 of 6** correct (P1 F, P2 T, P3 F, P4 T, P5 T, P6 T), and both
FALSE ones are load-bearing.

## The answer: the 69 are ORDINARY CELLS POINTING AT LOW-u1 CELLS

**Not taxonomy.** The 69 targets' super_class composition is
indistinguishable from the menu's: VNC-intrinsic 88.41% vs 84.83%, motor
11.59% vs 12.46%, sensory 0.00% vs 2.71%; `D_max` **0.0358** at permutation
p **0.56365** (B = 20,000 draws of 69 edge destinations from the 49,076-edge
menu, PREREG 0f), **0 of 3** classes BH-rejected, none tied at the floor.
P3 registered C_BIASED and is **FALSE**.

**Not size.** Every local-geometry median of the 69 sits essentially ON the
menu median — in-mass 11.0145 vs 10.2841, out-mass 7.8989 vs 7.9706,
in-degree 23 vs 21, out-degree 15 vs 17 — while their u1 is **0.012595** of
the graph mean against the menu's **0.263745**, a **20.9x** gap. These are
perfectly ordinary cells by every local count.

**It recurses.** PREREG 0L's identity decomposition is exact (`identity_err`
**0.0**, 0.00 ulp): the 69's log-u1 deficit `-2.275634` splits as
`log m_out +0.112468` + `log Q -2.358916` + `log align -0.029186`, i.e. shares
**m_out -0.0494 / Q +1.0366 / align +0.0128**. **103.7% of the deficit is
their own targets' u1**, and their out-mass is a **SUPPRESSOR** (slightly
larger than the menu's, pushing u1 UP) — the third instance of L211/L233's
admit-every-sign law. Q2b = **M_RECURSES**, P4 **TRUE**. The carrier points at
cells that are low-u1 for exactly the same reason it is: one hop further out.

**The zero set is closed, by proof.** 429 of 9,803 menu cells have u1 exactly
0 (**4.38%**, P6 TRUE), and CERT-237Z partitions them exactly: **369** have no
out-edges at all (u1 = 0 BY PROOF from identity (I), PREREG 0k) and **60**
have out-edges but an all-zero-u1 target set. Zero-cell median out-degree
**0.0** vs **18.0** for the rest.

## Q2: the card's own escape is refuted, but only by its companion

The card registered the honest escape "if in-degree alone explains u1[t], the
deficit is 'it points at low-in-degree cells'". Measured held-out (5-fold,
midrank Spearman, seed 23701, outcome `midrank(u1)` over all 9,803 cells):

| model | held-out rho | gain |
|---|---|---|
| M1 log1p(in-mass) | **0.329087** | — |
| M2 + log1p(out-mass) | 0.668301 | **+0.339214** |
| M3 + super_class fixed effects | 0.688110 | +0.019810 |
| M4 + log1p(in/out-degree) | 0.715779 | +0.027669 |
| *(diagnostic)* out-mass ALONE | **0.669052** | — |

P1 registered NOT_IN_STRUCTURE (`rho1 < 0.30`) and is **FALSE by 0.029087** —
in-mass lands in PARTIAL. But **out-mass alone reads 0.669052 = 2.03x
in-mass alone**, it is the identity's own operand (PREREG 0a), and
`rho(in-mass, out-mass) = 0.509430` (PREREG 0e, measured FIRST). So in-mass's
bar-clearing performance is largely **borrowed** through its correlation with
the right side of the operator, not owned. P2 TRUE at 3.4x its bar; P5 TRUE
(taxonomy adds +0.0198 < 0.05 over M2) — geometry beats taxonomy here.
Q3 **H_ROBUST**: the PARTIAL label survives both the log-currency arm
(rho1 0.379206, n 9,374) and the out-degree>=1 arm (rho1 0.364763, n 9,434).

## The homolog, again more extreme

Right DNp33 (gi **928**, read in code from `l207/static.json
Q2_mirror.mirror_identity.gi`, never hand-typed): n_out 74, Q **0.165627** =
**0.915x** the carrier's 0.181022, align 1.052162, `D_max` vs menu **0.0271**
(also typical). Consistent with L236's r_mean 13.5481 > 11.7118: the DNp33
TYPE points at low-u1 cells on both sides, and both sides' targets are
composition-typical. CERT-237H asserts all three stored homolog values at
float equality.

## Method laws

**1. A PREDICTOR ON THE WRONG SIDE OF AN IDENTITY CAN CLEAR A REGISTERED BAR
PURELY THROUGH ITS CORRELATION WITH THE RIGHT SIDE.** u1 is a LEFT Perron
vector, so `lam1*u1[t]` is a sum over `t`'s OUT-edges — in-mass is on the
wrong side of the operator by construction, and it still scored held-out
0.329087 and crossed a registered 0.30 bar. What tells borrowed signal from
owned signal is not the bar: it is the right-side-ALONE companion (0.669052 =
2.03x) and the predictor-predictor correlation (0.509430), both of which
PREREG 0a/0e required BEFORE the branch. Register the structurally-correct
predictor's solo score and the cross-correlation whenever a nested comparison
leads with a quantity the model's own identity does not contain.

**2. A COMPOSITION TEST'S FAMILY CAN BE NARROWER THAN ITS LEVEL COUNT BECAUSE
SHARES SUM TO 1** (the L232/L233 effective-width law, third instance, first on
a compositional statistic): the menu carries only **3** super_classes whose
shares are constrained to sum to 1, so the per-class family has **2** free
dimensions, not 3 — the BH rank-1 bar 0.016667 is computed against an
overstated width, and the `D_max` omnibus (p 0.56365) is the readable
instrument. Count the FREE dimensions of a compositional family, not its
categories.

**3. "ORDINARY ON EVERY LOCAL COUNT" IS A POSITIVE RESULT WHEN THE OUTCOME IS
A GLOBAL EIGENVECTOR.** All four local-geometry medians of the 69 are within
7% of the menu median while their u1 is 20.9x below it. A statistic defined by
a fixed point of the whole operator can be extreme on cells that are
unremarkable at every finite radius — so "we annotated them and they look
normal" refutes the local-geometry family rather than failing to find
anything.

## Verification (48,181 halting checks)

- **SLICE P** = `l219_static.py` 1-989 VERBATIM (sha `1e180562748807ed`,
  parent whole-file `fcef1ff55e0beedb`), a literal PREFIX, AST-proven
  write-free. **SLICE H** 1231-1281 (`34331f4f3a3f20d5`), **SLICE R**
  1284-1309 (`36d0d5bedb2bc307`), **SLICE T** 1459-1474
  (`da753da5eedbb46d`), **SLICE C** 1476-1501 (`755ed04d9dabc384`),
  **SLICE M** 1536-1545 (`20ac0206903d5d1a`) — every sha bit-identical to the
  values L236's own build measured, independently re-derived here.
- **SLICE MID1 / MID2** = `l236_mid1.py` (`aedff520261fecaf`) /
  `l236_mid2.py` (`78e30778f3a1d32a`) VERBATIM, each asserted a literal
  SUBSTRING of `l236_static.py` (`033665492b93baf9`) = proof they are the
  bytes that ran inside the certified parent card (L225: re-use a prior card's
  CERTIFICATION BLOCK as a source slice). MID2 audited STRUCTURALLY BY AST
  (defines exactly `[_leaves236]`, assigns `o_cert236a`/`o_cert236b`).
  They carry **CERT-236A** (86 artifact-derived L219 leaves over 16 keys,
  floor 82) and **CERT-236B** (424 leaves = the whole stored `Q219_2_table`,
  35 actors x 9 fields) for free.
- **SLICE D** = `l231_tail.py` 429-450 VERBATIM (`887a396073745d80`,
  bit-identical to the slice L233 and L235 used; source whole-file
  `879539c97fbe4d93`), AST-proven to define exactly `[midrank, spearman]`
  with the stable-mergesort assertion intact.
- **CERT-237D (HALTING, 46,870)** — this card's vectorised `dec237`
  reproduces SLICE H's certified `decomp219` on **all 9,374** measurable menu
  cells across 5 fields at FLOAT EQUALITY; max identity-(II) residual
  1.141e-15. A new kernel is admitted only by exact agreement with the
  certified one (the CERT-MV / CERT-236K pattern).
- **CERT-237Z (HALTING, 798)** — PREREG 0k's proof in both directions.
- **CERT-237H (HALTING, 3)** — the homolog's stored n_out/Q/align at float
  equality against `l236/static.json Q236_3_homolog`.
- **GATE-IDENT (HALTING)** — Q2b's three log shares sum to the measured
  deficit at **0.0 ulp**, with the bar DERIVED from the operands' magnitudes
  (scale 2.3589) and not the result's (L233's law).
- Line-set audit: slices DISJOINT and ordered, **1,118** parent lines kept /
  **554 CUT**, the cut region asserted to own `wm_null(MENU, 2000, 21901)`,
  `Q219_3_weight_matched`, `Q219_4_draw_distributions`, `cert_wmult` and the
  parent's `json.dump`. AST Import/ImportFrom walk proves no lab or live
  module imported (L175); AST write-site walk proves exactly ONE `json.dump`
  (-> `l237/static.json`) and one `makedirs`.
- `md5sum -c l237/prior.md5` (11 files) GREEN before AND after; all 11
  read-only `(size, mtime_ns)` fingerprints asserted unchanged after the run
  (`read_only_fingerprints_stable` True).
- This card stores its OWN banner at `o237["banner_l237"]`, read from the
  running script, so L237's successors inherit the banner pin L219 could not
  give (L236's disclosed gap, fixed forward).

## Limitations

- PREREG 0i, declared UP FRONT: L233 asked the same "does destination geometry
  explain it" question in the ARRIVAL currency on the BANC cord subnet and
  also found in-mass a suppressor. Both results are faces of ONE mechanism —
  the Perron vectors are reach quantities by identity — and are **not banked
  twice**. This card cites L233.
- Q2b's shares are an exact DECOMPOSITION, not a causal attribution: "their
  targets are low-u1" does not name the anatomical fact that makes that
  sub-population low-u1. The recursion terminates somewhere, and this card
  does not find where (-> follow-on).
- 3 of the 69 targets are excluded from Q2b (u1 == 0 or align <= 0): counted,
  not silently dropped (L224). 66 used.
- The 69 were selected by the carrier's own wiring, so every 69-vs-menu
  contrast whose null does not relocate the carrier's edges is DESCRIPTIVE
  (Kriegeskorte 2009). Q1's null does relocate them; the median tables do not.
- The rank transform in Q2 is computed over the full population and shared
  across folds (PREREG 0d) — disclosed, not hidden.
- The leverage leg is DESCRIPTION: the top-1% residual cells of M2 are
  **98 of 98 VNC-intrinsic** against an 84.8% menu share, selected for being
  extreme on the model's own residual.
