# L232 VERDICT — the CROSSING-EXISTENCE rate as the PRIMARY

Tick 264, 2026-11-24. PREREG `l232/PREREG.md` registered first, zero
amendments to any registered quantity. Static, zero rollouts, 28 s on om
(`nice -n 15 timeout 1700`). Artifact `l232/static.json`.
Branches: **Q1 T_TRUNCATION / Q2 E_FAMILY_NULL / Q3 O_REAL_EXTREME**.
Predictions **5 of 6** (P4 FALSE).

## Headline

**L217's 0.0505 was a truncation artifact, and it more than doubles at the
plateau.** The null's both-joints crossing rate on the primary arm
f4wA|beta rises monotonically with the depth horizon — 0.0075 (D=2), 0.0185
(D=4), **0.0505 (D=8, L217's number)**, 0.0755, 0.0910, 0.0980, **0.1090
(D*=30)**, 0.1150 (D=40) — a ratio of **2.158** over the registered 2.0
bar. The honest event rate for "a side relabelling makes both joints cross"
is ~0.11, not ~0.05.

**Asked nonselectively, nothing survives BH-FDR.** Of the registered
12-test family, 10 are measurable (2 are FALSE BY UNMEASURABILITY: the real
`cutwA|crofts|Ti` cell never crosses within D=40, which takes its arm with
it). The smallest p in the family is `arm/f4wA|crofts` at **0.047** against
a rank-1 bar of **0.005** — it misses by 9.4x. The resolution floor
4.9975e-04 sits **10.0x below** that bar, so the family fails by
**MAGNITUDE, not by power**. Every single-joint p is between 0.18 and 0.35.

**The only thing that fires is the multiplicity-free omnibus.** `PERM` is
keyed by (joint, side) only, so draw j is ONE side relabelling readable
across all 8 cells at once. **7 of 8 real cells cross by D*=30** against a
null whose per-draw count has mean **2.179** and median 2 —
`p_omni = 28/2000 = 0.0140`. The BH family, which treats the same data as 12
exchangeable tests, both diluted the signal and was blind to the dependence
that makes the joint statistic readable.

## The dependence structure is the caveat AND the reason the omnibus works

The null count histogram is conspicuously lumpy on EVEN values —
0:589, 1:118, 2:590, 3:124, 4:387, 5:54, 6:110, 7:13, 8:15 — because one
draw's Ti relabelling acts on 4 cells (2 substrates x 2 operators) and its
Tr relabelling on the other 4. **The omnibus's effective width is TWO
relabellings, not eight cells.** The permutation null carries that
dependence EXACTLY by construction, which is precisely why it is the right
instrument here and why the BH family is the wrong one: BH's independence/
PRDS framing is imposed on 12 tests that are really 2 objects. The real
value 7 is itself an ODD count, and odd counts are rare in the null
(13+15 = 28 draws at >= 7) — that is the whole p-value, stated honestly.

## The plateau is structural, not numerical

PREREG 0f required the distinction. `|A_cell(d) - A_inf| < 1e-12` is reached
by **NONE** of the 8 cells within D=40 (`saturation_depth` is null for all
8), so `plateau_numerically_forced = False`: D*=30 is where the null's own
event supply is exhausted, not where float resolution pins the sign.
Worst remaining rise to D=40: 0.2505 (D=2), 0.1900 (D=4), **0.1230 (D=8)**,
0.0835, 0.0540, 0.0345, 0.0220, **0.0090 (D=30, under the 0.01 tol)**.

## Two free cross-reads on L230 (DESCRIPTION, no branch)

- **L230's closed form predicted a crossing for the cell L217 censored**:
  `f4wA|crofts|Ti` at d 15.03. It DOES cross — measured interpolated
  `d_cross` **19.479**, first existence at D=20. The closed form
  under-predicted by **4.45 hops (29%)**, which is exactly the size L230's
  own amplification law anticipates on the Crofts arm: 1/|log rho| = 40.2 at
  rho 0.9755, so a sub-1% rate error buys ~4.5 hops.
- **L230's premise 0d holds**: `cutwA|crofts|Ti` (A_inf -0.008413, same sign
  as K) does **not** cross by D=40 — the model's refusal to predict a
  crossing agrees with the measurement for a principled reason.

## Predictions, scored as registered

| | registered | measured | |
|---|---|---|---|
| P1 | a plateau exists within D=40 | D* = 30 | **TRUE** |
| P2 | p_both(D*) > p_both(8) | 0.1090 > 0.0505 | **TRUE** |
| P3 | T_TRUNCATION (ratio >= 2.0) | 2.158 | **TRUE** |
| P4 | >= 1 BH rejection at q=.05 | 0 of 10 measurable | **FALSE** |
| P5 | real crosses in > 6 of 8 cells | 7 of 8 | **TRUE** |
| P6 | p_omni < 0.05 | 0.0140 | **TRUE** |

P4 is the load-bearing failure: the per-unit existence test is generic
everywhere, and the effect lives only in the aggregate.

## Certification

- **SLICE A** = `l216_static.py` 1-1360 VERBATIM (slice sha
  `6a3760d0b387a807`, whole-file `8d4740020fcd2a7b`) — a literal PREFIX cut
  before the parent's writer, AST-proven write-free, both shas re-derived
  AND asserted present in `l230_static.py`'s own generated banner. Re-runs
  CERT-F4 / CERT-178 (420) / CERT-GEN (44) / CERT-205 (250) / CERT-GAP (10)
  / CERT-209 (412) and the lam1 NO-OP (7.19e-14) for free.
- **PARENT PIN**: `l216_tail.py` sha `d9cb45022621452b` is a literal SUFFIX
  of SLICE A's source and the value that file's banner records at line 12.
- **CUT AUDIT**: the 7 cut lines parse to exactly 4 bare calls
  `[makedirs, dump, log, log]` (AST, never a line count).
- **SLICE B** = `l217_tail.py` 245-258 VERBATIM (sha `b26c0ab47cf0e2bb`),
  AST-proven to define exactly `[dcross]` and nothing else.
- **SLICE C** = `l230_tail.py` 39-211 VERBATIM (sha `23b0e840aa278c10`;
  whole-file `e9be8999c9d9d351` asserted present in l230's banner) = L230's
  OWN certification block, re-used rather than re-implemented (L225) →
  **CERT-216 GREEN 1,903** float equalities on an artifact-derived 1,900
  bar, **NO-OP 128**, **CERT-AINF 152**, **CERT-217 174**. Audited
  positively and NEGATIVELY by AST (defines exactly `[leafcmp, leaves]`; no
  `LOGRHO = {}` / `CF = {}` / `share_K` / `D_cf` / branch / predictions /
  writer) and independently proven write-free.
- **CERT-232X (HALTING, 128)**: the D=40 sweep's first 8 depths reproduce
  L216's stored `A_cell` at FLOAT EQUALITY **and** L216's 2000-draw null
  vectors at ARRAY EQUALITY, per cell per depth — the measurement that
  proves extending the horizon did not move the draw stream (PREREG 0c).
- **CERT-232D (HALTING, 25)**: the existence curves read at D=8 reproduce
  L217's stored per-cell null crossing rates, its censoring flags, its
  finite-draw counts, and its both-joints rate **0.0505 EXACTLY** — the new
  instrument tied to the stored primary with zero new freedom.
- Monotonicity in D asserted (never claimed): `np.diff >= 0` on all 8 null
  curves and all 8 real curves.
- AST import walk: no lab module imported (L175). AST write-site walk:
  exactly ONE write, `json.dump(..., open('l232/static.json','w'))`, plus
  one `makedirs('l232')`; all three slices independently write-free.
- `md5sum -c l232/prior.md5` (8 files incl. l217) GREEN before and after;
  (size, mtime_ns) on l216/l217/l209/l210 asserted unchanged after the run.
- Generated `l232_static.py` 1,985 lines sha `621dffb890fbb12d`
  (head `c8895f3b5ce40cfd`, tail `1c0c28bd4cb9c2ce`).

## Method laws

1. **A BH FAMILY CAN BE BOTH DILUTED AND DEPENDENCE-BLIND WHILE A
   MULTIPLICITY-FREE OMNIBUS ON THE SAME DRAWS IS THE ONLY READABLE
   INSTRUMENT.** Here the 12 "tests" are 2 objects: one permutation draw
   relabels 4 cells at a time, so BH's rank-1 bar q/m divides by a count
   that overstates the family's width while the per-unit p's are all generic
   (0.18-0.35). The permutation null over the SHARED draw index carries the
   dependence exactly and needs no correction at all (p 0.0140). Before
   building a BH family, ask how many INDEPENDENT randomisations its members
   consume — and if the answer is fewer than m, register the joint statistic
   as the primary and BH as the per-unit description.
2. **AN EVENT-EXISTENCE RATE IS A FUNCTION OF THE OBSERVATION HORIZON, AND
   THE HORIZON IS USUALLY INHERITED FROM AN UNRELATED DECISION.** DMAX=8 was
   L216's depth-decay choice; read as an event rate it inflated the
   real-vs-null contrast by 2.158x. Measure the rate's own plateau in the
   horizon BEFORE quoting it, and separate a structural plateau from a
   numerically forced one by the per-unit saturation depth (here: no cell
   saturates within D=40, so the plateau is real).

## Limitations

See `P["limitations"]` in the artifact (7 clauses), notably: every D=8
quantity is observed-derivable and scored as DESCRIPTION (PREREG 0b); the
unmeasurable tests SHRINK m and therefore LOOSEN every BH bar, so
`m_measurable` is stored beside `m_registered`; and the null is L205's
within-pool side-label permutation, which cannot speak to reconstruction
completeness (L231's caveat).
