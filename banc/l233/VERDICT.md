# L233 — VERDICT: the asymptote is NOT a degree statement. It is the OPPOSITE of one.

Tick 265 (cron), 2026-11-24. Static, zero rollouts, no new RNG.
PREREG `l233/PREREG.md` registered FIRST, with nine premise corrections and
ZERO amendments to any registered quantity. Run 0.31 s body on om,
`nice -n 15 timeout 1700`, peabrain venv. Artifact `l233/static.json`.

## Branches

- **Q1 = `D_MODE`** — `share_m_op` on the primary arm (f4wA|beta), mean over
  joints, **−0.0899** against bands [0.30, 0.70). `demotes_A_inf_family =
  false`: the card's own escape is NOT taken.
- **Q2 = `L_DISTRIBUTED`** — `lev1` 0.0413 (Ti) / 0.0298 (Tr) against a 0.50
  bar.
- **Q3 = `H_ROBUST`** — Ti retention **0.9838**, same sign; Tr **1.0194**.

Predictions **2 of 6** (P1, P6 TRUE; P2, P3, P4, P5 FALSE) — and all four
failures are load-bearing.

## The finding

L217 killed the SOURCE account by homogeneity; this card asked whether the
pools' own in-wiring supplies the asymptote. It does not — **it pulls the
other way.**

Primary arm, f4wA|beta:

| | Ti | Tr |
|---|---|---|
| `A_inf` (v1, per-cell mean) | **+0.286625** | **+0.444216** |
| `A_mop` (operator-native in-mass) | **−0.095690** | **−0.012566** |
| `A_indeg` (raw in-degree) | **−0.088835** | **−0.008880** |
| `A_m205` (L205's in-mass, STORED) | **−0.096787** | **−0.011792** |
| within-pool slope `b` (log v1 ~ log m_op) | +0.7742 | +0.7731 |
| `D_logv1` = mean_L − mean_R | +0.75359 | +0.91159 |
| explained `b·D_x` | **−0.11680** | **−0.02261** |
| mode residual `D_r` | **+0.87039** | **+0.93420** |
| `share_m_op` | **−0.1550** | **−0.0248** |

Inside the pool, `log v1` rises with `log in-mass` at Spearman **+0.7296 /
+0.6253** (midrank; 113/110 distinct values) and slope **+0.77** — local
in-wiring really does set a cell's Perron weight. But the LEFT side has
**less** in-mass and **lower** in-degree while carrying **more** v1, so the
explained part of the drift is **negative** and the mode residual carries
**115.5% (Ti) / 102.5% (Tr)** of it. In-degree is a **suppressor** of this
asymmetry, not an explanation of it. Every one of the four predictor
currencies and all 8 cells agree in sign: `A_mop`, `A_indeg`, `A_m205` are
negative on **0 of 8** cells positive, while `A_inf` is positive on **7 of 8**
(the exception is the known A_inf ≈ 0 cell).

**Every mirror-matched motor-neuron TYPE carries it.** On the primary arm,
**8 of 8** shared Ti types and **13 of 13** shared Tr types have a higher
mean Perron weight on the LEFT (exact two-sided sign tests p **0.0078** and
**0.0002**), mean log-ratio **+0.6186** and **+1.1627** — left homologs sit
at **1.86x** and **3.20x** their right partners. Restricting to
mirror-matched cells (112/113 Ti, 84/110 Tr) changes `A_inf` by **1.6%** and
**+1.9%**: unlike L231's optic lobe, this is NOT a composition effect.

## Method laws

**(1) A STRONG WITHIN-UNIT CORRELATION LICENSES NOTHING ABOUT A BETWEEN-UNIT
CONTRAST, AND CAN CARRY THE OPPOSITE SIGN.** rho +0.63…+0.96 within pool,
slope +0.77, and a between-side share of **−0.155** — a textbook
sign-reversal. NAMED PRIOR ART, cite don't claim: Simpson's paradox
(Simpson 1951), Robinson's ecological-correlation reversal (1950), the
within/between regression decomposition (Neuhaus & Kalbfleisch 1998). The
lane rule: a "does X explain Y" leg must register a **SIGNED** share with a
`S_SUPPRESSOR` label, because bands written as [0.30, 0.70) / ≥0.70 silently
assume the predictor can only help. This is L211's "a pre-registered share
band must admit every sign its own definition allows" recurring two cards
later from the opposite direction.

**(2) NORMALISING A LEVERAGE STATISTIC BY THE QUANTITY WHOSE NULL IS NEAR
ZERO TURNS ITS NULL INTO A TEST OF THE DENOMINATOR.** `lev1 = max|ΔA|/|A|`
had null means **2.19–33.74** against real 0.03–0.05 and `pct_up` **0.000** —
which says "the real |A_inf| is large", not "leverage is unusually even".
Report absolute leverage too (max|ΔA| = **0.0118** on Ti). And the single
cell clearing the 0.50 bar (cutwA|crofts|Ti, `lev1` **0.8948**) is exactly
the A_inf = **−0.008413** cell that halted L231's CERT-231A: at 1/|A| =
118.9, one cell moves 89% of it. The registered Q2 read the PRIMARY arm,
which is why the branch is uncontaminated and P4 is FALSE.

**(3) WHEN A NULL'S EFFECTIVE WIDTH IS 2, A SIGN-COUNT OMNIBUS OVER 8 CELLS
CANNOT RESOLVE BETTER THAN ~1/4 — AND THE INSTRUMENT THAT WORKS RANDOMISES
OVER A DIFFERENT OBJECT.** (Extends L232.) `p_omni(A_inf)` = **0.1620** from
a histogram piling at 4 (463/2000), while the TYPE-level exact sign test —
randomising over 8 and 13 mirror-matched types instead of 2 side labels —
reads **0.0078** and **0.0002** on the same cells. The tell was free: the
`A_indeg` omnibus histogram is occupied on **even counts only**
({0:500, 2:47, 4:919, 6:57, 8:477}), because in-degree is operator-invariant
so its 8 cells are 4 vectors counted twice. Disclosed self-inflicted
instrument choice: the sign omnibus discards magnitude, and the per-cell
magnitude percentile was already at the resolution floor
(`A_cell_pct_abs` = **1.000** on both primary cells, floor 4.9975e-04) — so
the omnibus added nothing here beyond the width diagnostic.

**(4) AN IDENTITY GATE'S ABSOLUTE BAR MUST BE CONDITIONED ON ITS OPERANDS'
MAGNITUDES, NOT ITS RESULT'S.** CERT-233B halted on its first run at
cutwA|crofts|Tr with |err| **2.887e-15** against a PREREG bar
of 8·eps = 1.776e-15, because the identity cancels log-scale operands
(|log v1| ≈ 14) to produce a result of order 0.1. Repaired by deriving the
scale from each cell's own fitted magnitudes: max err/scale **2.355e-16** =
**1.06 ulp**. Same shape as L231's CERT-231A, now for an IDENTITY rather
than a ratio. Tooling repair, disclosed, no registered quantity changed.

## Premise corrections that mattered

- **0a** — the card's "contralateral twin" does NOT exist at cell
  granularity: **zero** cell types are one-to-one across sides in either
  joint (Ti 8 shared types / 54 pairable cells, Tr 13 / 39). Registered at
  TYPE granularity instead, scored FALSE BY UNMEASURABILITY at cell level
  (L222) — and the type-level form turned out to be the card's strongest
  instrument.
- **0b** — two in-mass currencies: L205's `|log1p(syn)|` sum vs the
  OPERATOR-NATIVE row sum of `OPS[s][op]` (BETA_L on inhibition, Crofts
  degree normalisation). The primary uses the operator's own mass; L205's is
  the pin. They agree in sign and to ~1% here.
- **0c** — in-degree is operator-INVARIANT within a substrate (4 vectors,
  not 8); this is what produced law (3)'s even-count diagnostic.
- **0d** — a share is a ratio of a difference, conditioned by 1/|D_y|. The
  registered 0.01 readability bar was too permissive: cutwA|crofts|Ti passed
  it at D_y = 0.0144 (1/|D_y| = **69.4**) and read share **−5.8902**, which
  is a DIRECTION, not a magnitude. Reported with its conditioning factor.
- **0e** — the zero census ran before any log: **0 zeros** over 8 cells x 4
  vectors, so the log leg is full-population (L224).
- **0f** — PERM is keyed by (joint, group) only → effective family width
  **2**, so primaries are MAGNITUDES and percentiles are description.
- **0g** — count-free companion: Ti `A_tot` **+0.278482** vs `A_cell`
  +0.286625 with identity residual `A_cell + A_n` = **+0.277776** at side
  counts 56/57; Tr identical (55/55). The asymmetry is NOT count-driven
  (contrast L231's whole-graph read).

## Verification

- **SLICE A** = `l216_static.py` 1-1360 VERBATIM (slice sha
  `6a3760d0b387a807`, whole-file `8d4740020fcd2a7b`, both re-derived in the
  builder AND asserted present in `l232_static.py`'s own banner), literal
  PREFIX cut before the parent's writer, AST-proven write-free → CERT-F4,
  CERT-178 (420), CERT-GEN (44), CERT-205 (250), CERT-GAP (10), CERT-209
  (412) and the lam1 NO-OP (7.19e-14) re-run FREE as the code that produced
  `l216/static.json`. PARENT PIN: `l216_tail.py` sha `d9cb45022621452b` a
  literal SUFFIX and the value its banner records at line 12. CUT audit
  STRUCTURAL by AST: 7 lines → exactly 4 bare calls
  [makedirs, dump, log, log].
- **SLICE B** = `l217_tail.py` 245-258 (`b26c0ab47cf0e2bb`), AST-proven to
  define exactly `[dcross]`.
- **SLICE C** = `l230_tail.py` 39-211 (`23b0e840aa278c10`) — L230's OWN
  certification block re-used as source (L225) → **CERT-216 1,903** float
  equalities on an artifact-derived 1,900 bar, **NO-OP 128**, **CERT-AINF
  152**, **CERT-217 174**; audited positively and negatively by AST.
- **SLICE D** = `l231_tail.py` 429-450 (`887a396073745d80`; whole-file
  `879539c97fbe4d93` = the sha `l231_static.py`'s banner records, and the
  text is literal substring of that file) — L231's `midrank` + `spearman`,
  the L221 tie law in certified form, AST-proven to define exactly those
  two and nothing else, stable-mergesort assertion included.
- **CERT-233A (HALTING, 88)** — every `A_inf` field reproduced from `AINF`
  at FLOAT EQUALITY and `A_m205` reproduced from `l205/static.json` at FLOAT
  EQUALITY: leg (b) of the card is a STORED, already-certified quantity, not
  a new measurement.
- **CERT-233B (HALTING, 32 + 92)** — the OLS identity `D_y == b·D_x + D_r`
  exact to 1.06 ulp per cell per predictor set, and the closed-form
  leave-one-out equal to direct recomputation on the reduced cell set for a
  deterministic 10% cell sample.
- **CERT-233C (HALTING, 34)** — pool sizes, 100% `cell_type` coverage,
  per-side distinct-type counts and the shared-type census asserted EXACTLY
  as `l233/probe.out` declared them before any v1 was read.
- AST import walk: no lab module imported (L175). AST write-site walk:
  exactly ONE write, `json.dump(..., open('l233/static.json','w'))`, plus one
  `makedirs('l233')`; all FOUR slices independently proven write-free.
  `md5sum -c l233/prior.md5` (8 files) GREEN before and after.
- Generated `l233_static.py` 2,166 lines sha `6c95ac06b9674a41`
  (head `b9e4245761a1b363`, tail `422f77e6c20a5762`).

## What it changes

The `A_inf` family (L205 → L232) survives its own registered demotion test.
The pools' leftward Perron asymmetry is a **position-in-the-mode** property:
left pool cells are more central to the cord's dominant mode **despite**
receiving less local drive, every mirror-matched type carries it, and the
destination's local in-wiring would predict the opposite sign. The open
question moves one hop upstream — not "who drives the pools" (L217: nobody
in particular) and not "how much drive do they get" (this card: less on the
left) but **through which paths**. Follow-ons L275–L277 in `ideas 129`.
