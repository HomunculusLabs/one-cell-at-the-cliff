# L231 VERDICT — the LEFT-heavy Perron mode has no SOURCE: it is CORD-WIDE

Branch **B_GLOBAL** (registered, second in the registered order).
Predictions **4 of 6**, both FALSE ones load-bearing.
PREREG `l231/PREREG.md` (written first, nine premise corrections, one
disclosed tooling repair). Static, zero rollouts, zero settles. 85 s on om.

---

## 1. The registered answer

L216 found the anatomical operator's dominant mode strongly left-heavy on
every beta pool cell (A_inf +0.26 to +0.44) and nobody had asked whether that
is a property of the POOLS. Asked nonselectively over 30 units x 5 arms = **78
BH-FDR tests**, the answer is that it is not pool-specific at all:

On the primary arm `f4wA|beta` (the cord substrate, 21,609 side-labelled
cells):

| unit | n_L | n_R | A_v1 | A_tot (count-free) | BH |
|---|---|---|---|---|---|
| pop/all | 10590 | 11019 | **+0.34251** | +0.32486 | * |
| pop/ventral_nerve_cord | 9963 | 10392 | +0.34772 | +0.32906 | * |
| class/sensory | 3507 | 3787 | +0.42324 | +0.39121 | * |
| class/motor | 347 | 381 | +0.41688 | +0.37753 | * |
| class/ventral_nerve_cord_intrinsic | 6107 | 6223 | +0.32464 | +0.31620 | * |
| class/descending | 629 | 628 | +0.02732 | +0.02812 | — |
| pop/neck_connective | 626 | 624 | +0.02676 | +0.02836 | — |
| pool/Pr | 7 | 7 | +0.59041 | +0.59041 | * |
| pool/Tr | 55 | 55 | +0.44422 | +0.44422 | * |
| pool/Sr | 17 | 19 | +0.40872 | +0.36137 | * |
| pool/Ti | 56 | 57 | +0.28663 | +0.27848 | * |
| pool/Ta | 15 | 15 | +0.28243 | +0.28243 | — |

`A_glob = +0.342508` (p 2.0e-04, BH-significant) against a median pool |A| of
0.408720, so **R_glob = 0.8380** — comfortably over the registered 0.50 bar.
The pools are not special: they sit inside a cord-wide left-heaviness that
every super_class of the cord carries, at a level 84% of the pools' own.
4 of 5 pools are BH-significant (Ta is not), 3 of 4 super_classes are.

**The one place inside the cord substrate where the asymmetry STOPS is the
descending population and the neck connective** (+0.027 / +0.027, neither
significant, both at 1,250-1,257 cells where the instrument resolves +0.03
elsewhere). That is the same boundary L217 drew from the other side when it
found the drift CORD-INTRINSIC and independent of descending input: the
descending cells project INTO the asymmetric structure without being part of
it.

## 2. The reconstruction caveat the card demanded — and it REFUTES itself

Registered as the table's first two rows before anything was measured, because
a volume-wide L/R imbalance in proofreading completeness would produce exactly
this finding. Measured (halting census pin): the BANC v626 annotation carries
**left 26,799 / right 53,050** side labels, decomposing as

- optic_lobe L 3,311 / R 27,799 — **8.40 : 1 RIGHT**
- central_brain L 11,462 / R 12,895 — 1.13 : 1 right
- ventral_nerve_cord L 10,070 / R 10,494 — 1.04 : 1 right
- neck_connective L 1,805 / R 1,732 — 1.04 : 1 left

So the confound exists and it is enormous — but **it runs the wrong way**. The
count asymmetry is RIGHT-heavy everywhere the v1 asymmetry is LEFT-heavy:
`rho(A_v1, A_count)` over the primary arm's 12 units is **-0.4718** (negative,
and `F_CONFOUND` did not fire at its 0.70 bar); in the cord, where the finding
lives, the count ratio is 0.96 and the count-free total-mass form reproduces
`A_v1` at **95.0%** of its magnitude (mean |A_v1| 0.32679 vs mean |A_tot|
0.31269). **The left-heaviness is not reconstruction completeness.**

## 3. P4 FALSE, and the count-free currency is why

The registered P4 said the WHOLE-GRAPH population would read RIGHT-heavy,
because its cells are 2:1 right. It read **+0.335930, LEFT-heavy** — and the
post-hoc addendum (`l231/addendum.json`, pure arithmetic on stored rows) shows
precisely why, and it is the most transportable thing in this card.

`A_v1 = asym(M_L/n_L, M_R/n_R)` is a per-CELL mean. If the two hemispheres
carry EQUAL total Perron mass, then `A_v1 == -A_n` identically. Measured on
the whole-graph `all` population: `A_v1 +0.335930`, `-A_n +0.328800`, residual
**+0.00717**; the count-free `A_tot = asym(M_L, M_R) = +0.00806`. **The whole
brain+cord graph's dominant mode is side-balanced to 0.8% on 79,849 cells**,
and its entire apparent left-heaviness in the per-cell currency is the
optic-lobe reconstruction artifact wearing a 1/n disguise. Two whole-graph
units have A_v1 and A_tot of OPPOSITE SIGN: `wg/pop/optic_lobe` +0.66203 vs
**-0.26126**, and `wg/class/optic_lobe_intrinsic` +0.25446 vs **-0.88818**.

The cord is the opposite case — nearly balanced counts, so the two currencies
agree (+0.34772 vs +0.32906 on the VNC population) — which is what makes the
registered B_GLOBAL verdict count-free as well as significant, and what makes
L216's own A_inf (Ti 56/57, Tr 55/55 cells) safe as published.

So the honest scope statement: **the asymmetry is GLOBAL WITHIN THE CORD and
CORD-SPECIFIC at whole-graph scale.** Both halves of that sentence needed a
different currency to say.

## 4. Predictions, scored as written

| | registered | measured | result |
|---|---|---|---|
| P1 | `A_glob > 0` | +0.342508 | **TRUE** |
| P2 | `R_glob < 0.50` (not B_GLOBAL) | 0.8380 | **FALSE** — this IS the branch |
| P3 | >= 3 of 5 pools BH-significant | 4 | **TRUE** |
| P4 | whole-graph `all` RIGHT-heavy | +0.335930 | **FALSE** — section 3 |
| P5 | `\|rho(A_v1,A_count)\| < 0.70` | -0.4718 | **TRUE** |
| P6 | >= 1 super_class BH-sig with `\|A\| >= 0.10` | 3 | **TRUE** |

Registration NOT amended. Both failures are the card's content: P2 is the
registered branch firing, P4 is the reconstruction confound refuting itself in
the currency the addendum had to introduce.

## 5. Method laws earned here

1. **A PER-UNIT-MEAN asymmetry and a TOTAL-MASS asymmetry are different
   statistics, and they can differ by the WHOLE effect.** A per-cell mean
   carries a hidden `1/n`: when the per-side counts differ, `A_cell == -A_n`
   exactly at equal total mass, so the per-cell form reports a confound as a
   finding. Measured: +0.335930 vs +0.00806 = **42x**, with two sign flips.
   Register the count-free companion beside any per-unit-mean asymmetry, and
   report the identity residual `A_v1 + A_n` per unit.
2. **A family-wide CORRELATION screen cannot detect a confound that is an
   exact IDENTITY on a subset.** The registered `F_CONFOUND` instrument read
   rho -0.4718 (primary) and -0.4787 (whole graph) and correctly did not fire
   — yet the whole-graph units are almost entirely count-driven. The
   per-unit identity residual found in one line what the Spearman could not
   find at all; a confound screen needs a per-unit form, not only a rank
   correlation over heterogeneous units.
3. **A RELATIVE-error bracket on a ratio of a DIFFERENCE is conditioned by
   `1/|the ratio|`.** CERT-231A halted on its first run at `cutwA|crofts|Ti`
   (A_inf -0.008413): relative difference 8.454e-15 against 8*eps, because
   `asym` amplifies a relative perturbation of its summands by 1/|A| = 118.9.
   A statistic bounded in [-1,1] is gated on its ABSOLUTE resolution — the
   repaired gate passes at max **1.943e-16** absolute, and the relative value
   is reported beside its conditioning factor. Disclosed as a tooling repair
   made after the PREREG; it changes no registered quantity.
4. **A nonselective family needs its resolution floor checked against its own
   BH rank-1 bar before any rejection is quoted.** m = 78, rank-1 bar
   6.410e-04, worst floor 2.000e-04 = REJECTABLE with 3.2x headroom; 29 of 78
   tests used an EXACT enumerated null with no floor at all.

## 6. Verification

- **SLICE A** = `l216_static.py` lines 1-1360 VERBATIM (slice sha256
  `6a3760d0b387a807`, whole file `8d4740020fcd2a7b`), the literal PREFIX cut
  before the parent's writer, **AST-proven write-free on its own AST**. Both
  shas are re-derived in the builder AND asserted present in
  `l230_static.py`'s own generated banner — the inherited pin is read off
  disk, never retyped. PARENT PIN: `l216_tail.py` sha `d9cb45022621452b` is a
  literal SUFFIX of the parent and the value its banner records. CUT audit is
  STRUCTURAL by AST: 7 cut lines parse to 4 bare calls `[makedirs, dump, log,
  log]`.
- Inherited free as the code that produced `l216/static.json`: CERT-F4,
  CERT-178 (420), CERT-GEN (44), **CERT-205 (250)**, **CERT-GAP (10)**,
  **CERT-209 (412)** and the lam1 NO-OP (max rel 7.19e-14).
- **SLICE C** = `l230_tail.py` lines 39-128 VERBATIM (sha
  `3695df8db996d839`) — L230's OWN CERT-216 block re-used rather than
  re-implemented: **CERT-216 GREEN 1,903 float equalities** against a
  coverage bar **1,900 DERIVED from `l216/static.json`'s own leaf count**,
  plus the NO-OP re-asserted (128). Audited positively (CERT-216, leafcmp,
  leaves, `_f216 = os.stat`) and NEGATIVELY by AST (defines exactly
  `[leafcmp, leaves]`; no `dcross`, no `D_cf`, no `share_K`, no branch, no
  writer) and proven write-free.
- **CERT-231A (HALTING, 8 cells)**: the general per-unit statistic reproduces
  every CERT-216-pinned `A_inf` within **1.943e-16 absolute** (bar 8*eps =
  1.776e-15) — this is the card's own Verify line, discharged on all 8 cells
  rather than the required 4.
- **CERT-231B (HALTING, 44 structural checks)**: the ten pool-sides rebuilt by
  L229's construction with all 20 `S101` per-side sizes pinned, the four
  Ti/Tr masks asserted **ARRAY-IDENTICAL** to the `GROUPS` object L216 itself
  used, and every pool cell's annotation `side` asserted to agree with its
  pool name.
- **CENSUS PIN (HALTING)**: the side census and both extreme region rows
  (optic_lobe 3311/27799, VNC 10070/10494) asserted exactly as the PREREG
  declared them.
- **PERRON RESIDUAL** printed for every arm (L217's law): cord beta
  1.34e-16 / 1.44e-16, cord Crofts 3.68e-09 / 2.81e-05, **whole|beta
  1.881e-14 -> RESOLVED** at the registered 1e-03 bar, with the four
  certified cord arms as the calibration reference.
- **NULL**: 29 of 78 tests EXACT (full enumeration, assignment count asserted
  equal to `C(n, n_small)`, no resolution floor); the rest sampled at seed
  231231 with the tier registered in advance. Every null's mean asserted
  within 0.5 sd of zero, with mean and median both stored.
- Rank statistics MIDRANK with distinct-value counts printed (12/10/12 on the
  cord arms, 30/28/30 on the whole-graph arm).
- AST `Import`/`ImportFrom` walk: no lab module imported (L175). AST
  write-SITE walk: exactly ONE write, `json.dump(..., open('l231/static.json',
  'w'))` on one statement, plus one `makedirs('l231')`; both slices
  independently proven write-free.
- `md5sum -c l231/prior.md5` (7 files: l205/l209/l210/l215/l216/l92/l101)
  GREEN before AND after; `(size, mtime_ns)` on l216/l209/l210 asserted
  unchanged after the run; the addendum re-asserts `l231/static.json`'s own
  fingerprint after writing.
- Generated `l231_static.py` 2,143 lines sha **91fb58b054e49aa5** (head
  `ea1a7152c6d879a8`, tail `879539c97fbe4d93`). Run `nice -n 15 timeout
  1700`, peabrain venv, 85 s total / 56 s body.

## 7. Limitations (as stored)

(1) the whole-graph arm is BETA only — the Crofts reweighting lives inside the
certified `SUBS` loop and was not re-implemented outside it (PREREG 0d);
(2) restricted units are `keep_wA`-intersected on every arm so arms are
compared on identical cell sets, and one extra `Pr_bL` cell that exists
unrestricted is in no unit; (3) the union null is NOT L216's within-group
null — both are stored for Ti/Tr; (4) any whole-graph asymmetry is confounded
with reconstruction completeness BY CONSTRUCTION, which is why the branch
rests on the cord; (5) large units rest on 5,000 sampled draws (floor
1.9996e-04), small units are exact; (6) `A_inmass` is in each arm's OWN
operator currency; (7) `A_tot` and the identity residual are POST-HOC
DESCRIPTION, carried by no branch.
