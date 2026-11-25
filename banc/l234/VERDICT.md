# L234 VERDICT — the TWO-MODE closed form, and K2's own null

Tick 266, 2026-11-24. PREREG `l234/PREREG.md` registered first, nine premise
corrections, ONE disclosed tooling repair, ZERO amendments to any registered
quantity. Static, zero rollouts. Branches **Q1 CF_PARTIAL / Q2
K2_SEPARATED**. Predictions **5 of 6** — and the one FALSE is the card.

---

## Q1 (leg a) — the third mode is REAL, CLEAN, and NOT ENOUGH

Double Hotelling deflation (against the Perron pair *and* L218's subdominant
pair) resolves a third eigenpair about as cleanly as this operator ever does:

- signed Rayleigh quotient **+25.9512564246914** (right) / **+25.95125642469329**
  (left) — real, POSITIVE, and agreeing to 13 digits;
- relative residual **4.759e-12 / 5.706e-12** against the registered
  `RES_BAR = 1e-3` (L218's own mode-2 residuals were 7.0e-09 / 3.5e-09, so
  mode 3 resolves ~1,000x tighter);
- distinct from mode 2: `|lam3|/|lam2| = 0.96305`, well clear of the
  degeneracy escape;
- `r3 = lam3/lam1 = +0.8598886179489906`, `gap2 = 0.8928793607351002`.

The direct coefficient, built exactly as A2 was (PREREG 0c):
`K3 = u3[c]*S_v3/(u3.v3) = +4.1548458553e-04`, **A3 = K3/K = +0.07778958**.

**The two-mode closed form improves L218's band by 3.691x and still misses by
3.1%.** `e(d) = A2*r2^d + A3*r3^d` reads max relative error **0.03146926**
over d=10..50 against the one-mode **0.11616512** — worst at **d=10** (the
whole miss is at the shallow end; at d=50 it is **0.00210571**). The
registered `CF_TWO_MODE` bar was 0.01, so the branch is **CF_PARTIAL** and
**P1 is TRUE**.

**The miss is the MODE STRUCTURE, not the coefficient.** The descriptive
one-free-parameter companion (A3 fitted by least squares with r3 FIXED at the
measurement) moves A3 0.07779 -> **0.08705** and the error only 0.03147 ->
**0.02398**: a 12% change in the coefficient buys a 24% change in the error
and still leaves 2.4%. A fourth mode is required, and the stored-data probe
said so in advance — the one-mode residual's per-hop log-ratio is not
constant (first -0.253992, last -0.145012, spread 0.114516, `l234/probe.out`).

**A NEW LAW, and it is recursive: an anchor-implied mode coefficient is
biased UPWARD by every mode it omits, and the bias COMPOUNDS down the
spectrum.** L218 measured `A2_direct/A2_implied = 0.883834883418044` (the
d10 anchor over-states A2 by 1.13x). This card's two-point anchor implies
`A3 = 0.11857515` against the direct **0.07778958** — ratio **0.65604**, an
over-statement of **1.52x**. The anchor absorbs the entire omitted tail, so
the deeper the mode the worse its anchor estimate. Register the DIRECT
eigenvector construction as primary; an anchor-implied coefficient is a
diagnostic of what you left out, not an estimate of what you kept.

Predictions: **P2 TRUE** (signed lam3 > 0, as the single-signed positive
residual demanded), **P3 TRUE** (gap3 0.85989 in the registered [0.82, 0.90]),
**P4 TRUE** (A3 0.07779 in [0.0593, 0.2372]).

## Q2 (leg b) — K2's null exists now, and it does NOT behave like K's

L218 computed 100 per-draw K2 values and discarded them; this card re-computed
them exactly (CERT-234C, 100 float equalities) and stored them.

| | K (dominant) | K2 (subdominant) |
|---|---|---|
| real | 0.005341134141887085 | 0.0029754868499497085 |
| draw median | 0.06089767702943477 | 0.013353031615544683 |
| suppression fold | **11.402x** | **4.488x** |
| percentile | **0.000** | **0.200** |
| draws < 0 | **0 of 100** | **15 of 100** |

**P5 is FALSE and it is the card**: the branch is **K2_SEPARATED**, not
`K2_FLOOR`. The two marginals are NOT at the same floor.

**But the separation is first a SIGN phenomenon, and that is this card's
headline method law** (`l234/addendum_sign.json`, post-hoc, 7 gates, pure
arithmetic on certified stored values): **K's null is strictly positive BY
PERRON-FROBENIUS — 0 of 100 draws negative — while K2's straddles zero (15 of
100), so a raw percentile is not a comparable currency between the two
modes.** Of the 20 draws below K2_real, **15 are below because they are
NEGATIVE** and only **5** because they are smaller in magnitude. Conditioned
on the 85 positive draws the carrier's subdominant overlap sits at pct
**0.05882** against K's **0.000**, with suppression folds 11.402x vs 5.321x
(positive-draw median) = a **2.54x** ratio. L218's claim — the carrier avoids
the dominant mode HARDER than the subdominant one — SURVIVES, in a currency
that has to be named. (Free consistency check: `|K2|` percentile reads
**0.100**, exactly L218's stored `u2_carrier_percentile_absval = 0.1`.)

**And the second law, which L218 could not have seen: a RATIO can sit at the
94th percentile while BOTH of its components sit at or near the 0th.**
`A2 = K2/K` has pct **0.94** (L218's stored value, re-certified here) while K
is below all 100 draws and K2 below 80 of them — because the ratio's
numerator and denominator are both suppressed and the denominator more so.
The ratio's percentile neither implies nor is implied by its marginals': they
are three different claims and L218 had only one of them.

## Q3 — the compose check (description, no branch)

`median(K2_k)/median(K_k) = 0.21926997` vs `median(K2_k/K_k) = 0.21115719`:
relative disagreement **0.03842** > the 1% bar, so **P6 is TRUE**. PREREG 0g
made concrete — the two are different statistics, and here they differ by
3.8%, small enough that L218's reported ratio-median was not misleading and
large enough that quoting one as the other is wrong.

## Predictions

| | registered | measured | |
|---|---|---|---|
| P1 | Q1 == CF_PARTIAL | CF_PARTIAL | **TRUE** |
| P2 | signed lam3 > 0 | +25.95126 | **TRUE** |
| P3 | gap3 in [0.82, 0.90] | 0.8598886 | **TRUE** |
| P4 | A3 in [0.0593, 0.2372] | 0.0777896 | **TRUE** |
| P5 | Q2 == K2_FLOOR | K2_SEPARATED | **FALSE** |
| P6 | compose gap > 1% | 0.038421 | **TRUE** |

## Certification

- **SLICE A** = `l218_static.py` lines **1-1691 VERBATIM**, slice sha256
  `ff3e3ae95b2cd21f`, parent whole-file `ff2f2a5d83d55ee6`, a literal PREFIX
  cut immediately before L218's own predictions/writer block and AST-PROVEN
  write-free. THREE PINS, none hand-typed as a fact about bytes: (1) the
  parent's first 10 lines **equal `l218/static.json["banner"]`** — the
  generated script's own banner as recorded INSIDE the artifact it produced;
  (2) `l218_tail.py` whole-file sha `5db068f586f3f097` equals the TAIL sha
  that banner records AND is a literal SUFFIX of the parent; (3) the slice
  assigns 30 `o[...]` measurement keys and **none** of the parent's five
  verdict keys (structural, by AST). The 72 CUT lines are audited by AST to
  own exactly `{predictions, amendments, limitations, priors_readonly,
  rows_per_draw_recomputed}` and the parent's writer.
- **CERT-234A (HALTING, 661)** — every leaf of `l218/static.json` outside
  those five keys, reproduced from this run's own `o` at FLOAT EQUALITY, on a
  coverage bar **661 DERIVED from the artifact's own leaf count** over 30
  keys. This re-runs, as the code that actually produced the artifact,
  **CERT-218T (1224)**, **CERT-W50 (1010)**, CERT-DEFLV, CERT-206 (94),
  CERT-MV, CERT-LEFT, CERT-REBUILD (1000), CERT-178 (420), CERT-NULL,
  CERT-F4, CERT-REW, the NO-OP (3.32e-15) and Q218-1/2/3 in full.
- **CERT-234B (HALTING, 6)** — `defl_multi` / `defl_resid_multi` called with
  the SINGLE Perron pair are bit-for-bit the certified `defl_pair` /
  `defl_resid` on the eigenvalue, the iterate (array equality) and every
  convergence field, in BOTH directions. A new kernel is admitted only by
  exact agreement with the certified one.
- **CERT-234C (HALTING, 100)** — every per-draw `K2_k/K_k` reproduces the
  slice's own certified `A2K[k]` at FLOAT EQUALITY, plus the per-draw Perron
  `lam` pin. The derived shortcut this card DECLINED (`A2K*KK`) disagrees by
  max rel **1.776e-16** = 0.8 ulp: the cost slice would have been safe, and
  we only know that because we paid for it once (L226).
- AST: no lab module imported (L175); exactly ONE write site
  (`l234/static.json`), one `makedirs`.
- `md5sum -c l234/prior.md5` (9 files) GREEN before and after; (size,
  mtime_ns) on 6 prior artifacts asserted unchanged across the run.
- Generated `l234_static.py` **2080 lines**, sha256 `eabc47284581401498`...;
  run **414 s** on om, `nice -n 15 timeout 1700`, peabrain venv.

## Disclosed: one gate halt, and it cost a full slice re-run

The FIRST run halted at `assert _n234a >= 1000` with the true value **661** —
and 661 was already the artifact-DERIVED coverage bar the line above had just
matched. The hand-typed floor came from CERT-218T's **1224 internal checks**,
which is not the artifact's **leaf count**; conflating an internal check
count with a stored leaf count is the trap. **This is the FOURTH instance of
L224's law (a coverage bar must be DERIVED from the artifact, never guessed)
and the first where the guessed bar was the ONLY thing that failed.** Repaired
by deriving the floor from the artifact's own core blocks
(`Q218_1_primary, Q218_2_rate, Q218_3_u2, profile, cert_218t, cert_w50,
Q210_1_primary, Q210_4_gap, cert_206, cert_rebuild`). Cost: one full 372 s
SLICE A re-execution. No registered quantity changed. A second hand-typed
`== 100` in CERT-234C was repaired to
`len(S218["rows_per_draw_recomputed"])` by the same reasoning before the
re-run.

## Limitations (as registered)

One substrate (f4wA), one operator `|g*W_beta|`, one null family (the l169c
destination swaps), one carrier. 100 draws cap every percentile at 0.01
resolution, so `pct == 0.0` means "below all 100 draws" and nothing finer.
`e(d)` is a RATIO profile, so a mode coefficient here is a ratio of overlap
coefficients, not an amplitude in any physical unit. **No per-draw THIRD mode
was computed**: Q1 is a real-operator question and the card registered no K3
null, so A3 has no null of its own — exactly the gap this card closed for K2,
reopened one mode deeper. The fitted-A3 companion has one free parameter and
is DESCRIPTION.
