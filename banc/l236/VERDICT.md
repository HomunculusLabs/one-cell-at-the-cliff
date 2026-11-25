# L236 VERDICT — the 11.4x is NOT special: 270 cells read higher, and the homolog reads higher still

Branch **PARTIAL** (registered), predictions **1 of 6** — and the five FALSE
ones are the card. Static: zero rollouts, zero settles, zero dynamics.
PREREG `l236/PREREG.md` written before `l236_tail.py` existed and before any
per-cell ratio was computed. Amendment **0L** forced by a halting gate
(disclosed below). Total run **19.9 s**.

## The question, and the one-pass instrument

L219's Q219-3 showed that a menu-matched, weight-matched null reproduces
L210's full 11.4x deficit to 0.65% while holding `u1` completely fixed. This
card asks it NONSELECTIVELY over the whole population that null is built from.

**PREREG 0b, written before measuring, is what made the pass cost 8.8 s:** by
linearity, `E[S_draw] = m_out * mu_MENU` for ANY weight multiset, so

    r_mean(c) = m_out(c) * mu_MENU / S_c = Q_menu / (Q_c * align_c)

is a CLOSED FORM — the draws are needed only for the tail probability, and
"weight-matched" is cosmetic for the ratio and load-bearing only for its
variance. L219's own currency `r_med` is additionally **biased downward at low
out-degree** (the null's median/mean runs 0.182 at n_out 1 -> 0.971 at 69,
measured in the probe), so over a population whose out-degree spans 1-456 it is
not a comparable currency. The branch was registered on `r_mean`;
Spearman(`r_mean`, `r_med`) = **+0.9946**, so the ordering survives the choice.

## The population: 1,253 cells, and the carrier is at the 78th percentile

The block has **1,253 distinct DN source cells** and — measured, not assumed —
all 35 L178 actors are already among them (union exactly 1,253: PREREG 0a
turned the card's two populations into one).

| | value |
|---|---|
| population median `r_mean` | **1.6461** |
| p25 / p75 / p95 | 0.6673 / **8.6972** / 113.35 |
| fraction with `r_mean >= 5` | **0.3403** |
| fraction with `r_mean >= 11.4` | **0.2173** |
| carrier `r_mean` | **11.7118** |
| carrier rank (cells strictly higher) | **271** of 1,253 |
| carrier percentile | **0.7829** |

**272 of 1,252 measurable cells have a LARGER deficit than the carrier's
headline 11.4x.** The branch bars were registered at >= 5.0 (MENU_PROPERTY) and
< 1.6 (CELL_SPECIFIC); the measured median **1.6461** lands on **PARTIAL**, and
it misses CELL_SPECIFIC by **0.046**. The honest reading is the one the card
registered as its escape, at reduced strength: a large part of the 11.4x is the
MENU being edge-destination weighted while individual cells are not. `Q_menu` =
**2.3610**, i.e. a menu draw is 2.36x an average node's importance, and PREREG
0i's **exact** positive control (gate B, rel **1.52e-16**) proves the
population is CENTRED by construction, so everything above 1 is `u1`'s tail,
not the carrier.

**P1 FALSE** (registered CELL_SPECIFIC, measured PARTIAL).
**P2 FALSE** (registered top 10; measured rank 271, and 17 in the
degree-matched cohort). **P3 FALSE** (registered <= 5%; measured **34.0%**).
**P4 TRUE** (median/mean 0.0045 <= 0.80). **P5 FALSE** (the screen bites).
**P6 FALSE** (the homolog is ABOVE the carrier).

## The homolog DISAGREES — by being MORE extreme

Right DNp33 (gi **928**, read in code from
`l207/static.json["Q2_mirror"]["mirror_identity"]["gi"]`, never hand-typed):
`r_mean` **13.5481** against the left's 11.7118 = **1.1568x**, n_out 74,
Q 0.16563, align 1.0522, rank 241, percentile 0.8077.

So the deficit is **bilaterally consistent** — which makes it a property of the
DNp33 **TYPE**, not of one cell, and L206/L210/L218/L219's "the carrier"
framing should read "the DNp33 type". But P6 registered "strictly between 1.0
and the carrier's" and the homolog overshot it: a homolog can disagree by
being MORE extreme, which is the third face of the L207/L212 law.

## The FDR leg exists and still cannot single the carrier out

PREREG 0d sized the draws so the leg would not be unreachable BY CONSTRUCTION
(L225): m = 1,253, BH rank-1 bar `q/m` = **3.9904e-05**, so B = 30,000 giving a
floor `1/(B+1)` = **3.3332e-05** < the bar. It cleared. And it still did not
help: **177 cells sit AT the floor**, so the carrier's p is the floor, **0
cells are strictly smaller**, and its BH q is **2.3596e-04** at rank 177 — not
rank 1. **427 of 1,253** cells are rejected at q = 0.05 (and 190 in the
opposite direction), exactly the dilution PREREG 0f registered in advance as
"not the instrument".

**NEW METHOD LAW: A RESOLUTION FLOOR DOES NOT ONLY CAP A p-VALUE, IT TIES THE
UNITS AT IT.** Clearing the rank-1 bar makes rejection *possible*; it does not
make a selected unit *distinguishable*. Register the expected number of
floor-tied units, not just the floor — the quantity that decides whether the
leg can identify anything is `#{p == 1/(B+1)}`, and no feasible B fixes it when
177 cells have zero draws below their real value.

## The degree screen bit — and made the carrier MORE extreme

PREREG 0g registered the confound screen at |rho| >= 0.30. Measured
(midrank, via the parent's certified `spear219`): Spearman(`r_mean`, n_out)
**-0.4544**, (`r_mean`, log m_out) **-0.4345**, (`r_mean`, block fraction)
**+0.2864**. The screen **bites**, so P2 is scored on the degree-matched
cohort (n_out in [55, 83], n = **171**): carrier rank **17**, percentile
**0.8947** — matching moved it UP, not down.

**NEW METHOD LAW: A SCREEN THAT BITES IS NOT AUTOMATICALLY A DEFLATION.** The
registered expectation for a confound screen is that controlling it shrinks the
selected unit's standing; here it grew it (.783 -> .895) because low-degree
cells carry most of the raw tail. Register the DIRECTION the matched reading is
allowed to move, not just the bar.

## The zero class: amendment 0L, forced by a halting gate

The first run died in the parent's own `decomp219` on
`assert mq > 0.0` — because the left Perron vector has **exact zeros**, so a
block DN all of whose targets sit at the Perron floor has `S_c == 0` and its
ratio is **UNDEFINED, not large** (L224: a zero in the outcome is a
model-family verdict, not a missing value). Repaired at the root rather than
excluded: `dec236` drops the assertion, the bounded zero-admitting currency
`d_mean = (S_c/m_out)/mu_MENU` becomes the ranking primary (median 0.6068,
carrier 0.0854), and `r_mean = 1/d_mean` is quoted only where defined.
Measured: **1 cell of 1,253** (n_out 1, block fraction 1.0, not BH-rejected).
`dec236` is admitted by **CERT-236D: 6,260 float equalities** against the
parent's certified `decomp219` on every cell where `decomp219` is defined.

## Continuity, and what the card leaves standing

The 35-actor cohort (DESCRIPTION, observed-derivable per PREREG 0c): median
`r_mean` **1.0405**, p05 0.3334, p95 12.1226, and the carrier is rank **3 of
35** — two L178 actors are already more extreme than it inside L219's own
cohort.

What survives: the carrier's and the homolog's deficits are real, large, and
bilaterally consistent; the closed form of L218 and the decomposition of L219
are untouched (both re-certified here at float equality). What does not: the
claim that **11.4x** is a distinguishing property of this cell. It is a common
value in this block.

## Verification

- **SLICE P** = `l219_static.py` lines **1-989** VERBATIM (sha
  `1e180562748807ed`), a literal PREFIX; **SLICE H** 1231-1281
  (`34331f4f3a3f20d5`), **SLICE R** 1284-1309 (`36d0d5bedb2bc307`), **SLICE T**
  1459-1474 (`da753da5eedbb46d`), **SLICE C** 1476-1501 (`755ed04d9dabc384`),
  **SLICE M** 1536-1545 (`20ac0206903d5d1a`), **SLICE W** 1548-1556
  (`5cdb3bfed741e1ed`). Parent whole-file `fcef1ff55e0beedb`.
- **PINS**: the parent's own generated banner records `TAIL = l219_tail.py
  sha256 3debfdf00691b662`, and that tail is a literal **SUFFIX** of the parent
  -> the parent is the script `l219_build.py` produced. DISCLOSED: unlike
  L234/L235 there is **no banner-inside-artifact pin available** for L219 — its
  stored `banner` key carries L210's — so this card's identity rests on the
  tail-sha + suffix pin plus the float-equality coverage below. Fixed forward:
  this card stores its OWN banner at `o["banner_l236"]`, read from the running
  script itself, so L236's successors get that pin for free.
- **LINE-SET AUDIT**: the seven slices are disjoint and ordered, 1,127 parent
  lines kept and **545 CUT**, with the cut region asserted to own the parent's
  per-draw loop (`WM = wm_null(MENU, 2000, 21901)`), its `Q219_2_table` and
  `Q219_3_weight_matched` writers and its `json.dump` — and the kept slices
  proven write-free **by AST**, never by a token scan.
- **CERT-236A (HALTING, 86)** — every leaf of `l219/static.json` under the 16
  keys the slices assign, at FLOAT EQUALITY, on a bar **DERIVED from the
  artifact's own leaf count** (floor 82 from its core blocks; L224 applied in
  advance). The 86 *leaves* re-run **CERT-178's 420**, CERT-206's 94, CERT-MV's
  8, CERT-F4, CERT-REW, CERT-NULL and CERT-LEFT as *internal* checks inside
  SLICE P — the L234 distinction between a stored leaf count and an internal
  check count, respected this time.
- **CERT-236B (HALTING, 424)** — the whole stored `Q219_2_table`, including all
  **35 actors x 9 fields**, reproduced at float equality from the parent's own
  SLICE T + SLICE C cohort machinery. This is what admits extending
  `decomp219` to 1,253 cells.
- **CERT-236C (HALTING, 17)** — the stored `Q219_3` menu shape (49,076 edges /
  9,803 cells), `S_car`, `ratio_med` **11.4757**, S percentiles, `Q_med`,
  `align_med`, `ratio_Q`, `ratio_align` and `Q219_1_primary.real`'s five
  carrier fields, all at float equality.
- **CERT-236K** — `wm_cell` (the generalised kernel) is **bit-identical**
  (`np.array_equal`) to the parent's `wm_null` on the carrier at seed 21901,
  2,000 draws. A new kernel admitted only by exact agreement with the certified
  one (the CERT-MV pattern).
- **CERT-236D (HALTING, 6,260)** — amendment 0L's `dec236` equals `decomp219`
  on 5 fields x every measurable cell.
- **GATE B (HALTING)** — PREREG 0i's exact positive control: the edge-count
  weighted mean of each cell's unweighted mean target importance equals the
  block's edge-destination mean at rel **1.52e-16**, which simultaneously
  proves the per-cell grouping partitions the block edges exactly.
- Halting total **6,787**. AST Import/ImportFrom walk proves no lab module is
  imported (L175); AST write-site walk proves exactly **one** `json.dump`
  (-> `l236/static.json`) and one `makedirs`.
- `md5sum -c l236/prior.md5` (8 files) GREEN before AND after; (size,
  mtime_ns) fingerprints on all 8 asserted unchanged after the run.
- Generated `l236_static.py` **1,751 lines** sha `033665492b93baf9`; run
  **19.9 s** on om, `nice -n 15 timeout 1700`, peabrain venv.
- **COST SLICE (L226/L235)**: the parent's ~370 s per-draw eigendecomposition
  loop is CUT, which is why a 1,253-cell nonselective pass costs **less than a
  twentieth** of the single-cell card it generalises. The cut is admitted only
  by CERT-236A/B/C/D reproducing the parent's stored output.
- DISCLOSED: two gate halts (the `_fmed`/`_fpct` slice boundary, and
  amendment 0L's `mq > 0`), plus one hand-typed slice-range string in the
  certification summary that contradicted the build's own ranges — repaired at
  the root by deriving it from the running script's own banner (the
  derive-never-retype law, now on its fourth distinct surface: push probes,
  pins, premise literals, and a provenance string).
- No live change, no draft edit (`paper/` untouched), `sessions/` untouched.
