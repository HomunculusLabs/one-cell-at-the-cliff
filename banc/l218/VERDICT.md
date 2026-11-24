# L218 VERDICT — the CONVERGENCE CORRECTION as its own object

Branch **CF_EXACT** (registered) on the primary, **RATE_SPECTRAL** on the
rate, **U2_NULL** on the overlap leg — the last by ONE DRAW. Predictions 4/5.
PREREG: `l218/PREREG.md` (written first). Artifacts: `l218/static.json`,
`l218/run.out`, `l218/run.err`, `l218/build.out`, `l218/prior.md5`. Code:
`l218_build.py` + `l218_tail.py` -> generated `l218_static.py` (1,708 lines).
338 s of tail after the parent block, CPU, zero rollouts / settles / dynamics.

## The headline

**L210's closed form is not approximate — it is exact, and the 9.7% by which
it overshot at depth 10 is the spectral gap, measured twice from two
independent instruments that agree to 0.08%.**

- Primary: `C_prof(50) = D_50 / R_asym(50) = 0.999394`, i.e. **0.061% off**
  against a registered 1% bar -> **CF_EXACT**.
- `D_50 = 11.37931` vs `R_asym(50) = 11.38621`. The card's literal depth-free
  form `K_ratio_med = 11.40164` is 0.196% off (`D50/K_ratio_med = 0.998042`),
  three times worse than the primary — exactly the lam-power factor
  `median(lam_k)^50 / lam1^50 = 0.998833` that PREREG 0a registered as the
  reason to make R_asym(d) primary before either number was seen.
- The deficit profile is monotone and converging, not flat:

      d:      2       5      10      15      20      25      30      40      50
      D:  8.378   9.944  10.388  10.849  11.106  11.251  11.331  11.368  11.379
   C_car:  1.393   1.389   1.203   1.109   1.061   1.034   1.019   1.006   1.002

  `C_car(10) = 1.2030` (L210's measured overshoot) closes to **1.00197** at
  d50, and `C_prof` goes 0.735 -> 0.911 -> **0.999394**.

## The rate: a mass profile measures the spectral gap

`Q218-2 = RATE_SPECTRAL`. The per-hop ratio of the normalised correction
`C_car(d) - 1` over d = 20..45 has median **0.8921719**, range
[0.890752, 0.892297], against the certified gap `|lam2|/lam1 = 0.8928794`:
**|diff| = 7.07e-04**, 0.079% of the gap, against a registered 0.02 absolute
bar. The ratio rises monotonically across that window *toward* the gap, which
is the signature of a third mode decaying out from below.

That is a **double determination of the same number by instruments that share
nothing**: one is a 50-depth forward mass sweep with no eigenvector anywhere in
it; the other is a Hotelling deflation. And the PREREG registered the mass
sweep as the FALLBACK precisely because it needs no eigenvector — which is the
instrument L217 wanted and did not have when its third operator's dominant
spectrum turned out non-simple.

No sign alternation anywhere in d = 15..50, so lam2 is real and POSITIVE —
confirmed independently by the signed Rayleigh quotient on the deflated
operator, **+26.946910 in BOTH directions**, matching |lam2| = 26.946910 to
eight digits with residuals **7.04e-09 / 3.54e-09** (L217's law: diagnose an
eigenpair with its residual). All 101 eigenpairs resolved, max residual
7.08e-09 against a 1e-03 bar.

The rate is a property of the OPERATOR, not of the carrier: the draws' own
rates sit at median 0.889687 [p05 0.8812, p95 0.9107] and the real carrier is
inside them. What differs between the carrier and the draws is the
**amplitude** of the correction, not its rate — which is what the third leg is
about.

## The third leg: the same cell on OPPOSITE sides of the null, depending on the currency

`Q218-3 = U2_NULL`, and it is the most interesting miss on the card.

The scaling- and sign-invariant statistic
`A2 = K2(carrier)/K(carrier)`, with
`K2(c) = u2[c] * S_v2 / (u2 . v2)` the exact subdominant analogue of L210's K:

- `A2_real = +0.557089` vs draw median **+0.211157** — **2.638x** the null
  median, percentile **0.940**, and `|A2 - median| = 0.346` so it is a
  MAGNITUDE and not the direction-only reading the PREREG reserved for small
  absolute differences.
- But the registered bar was `percentile >= 0.95`, and the carrier sits
  **0.0049 below the null p95** (+0.5571 vs +0.5620). 94 of 100 draws are
  smaller. **U2_NULL**, registered, and P4 is FALSE by one draw.

L207's law, verbatim: against a 100-draw cohort one draw is one percentile
point, so a bar placed at 0.95 cannot separate 94 from 95. The reportable
object is the 2.64x elevation at p94, not a significance call.

**And the card's LITERAL form answers the opposite question.** The bare
unit-L2 `|u2[carrier]| = 3.228e-04` sits at percentile **0.100** — the draw
median is 1.551e-03, so the carrier is **4.8x BELOW** its nulls on the
subdominant overlap, where A2 puts it 2.6x ABOVE.

That is not a contradiction, it is the decomposition. `A2 = K2/K`, and the
carrier's dominant-mode overlap K is itself 11.4x suppressed (L210: percentile
0.0, every one of 100 draws larger). The carrier avoids BOTH modes. It avoids
the **dominant** one harder than the **subdominant** one, and a differential
avoidance of exactly that shape IS a slower approach to the dominant mode.
Stated in the invariant currency, with no median-composition step: the
carrier's subdominant-to-dominant overlap RATIO is 2.64x its nulls'.

**METHOD LAW, the most transportable thing on this card: when a vector
statistic admits both a scale-invariant form and a bare unit-norm form, those
two can place the SAME cell on OPPOSITE sides of the SAME null — register
which one carries the branch before measuring, and report both.** L210
registered exactly this disclosure for the dominant mode and it turned out
VACUOUS there (bare 11.4039 vs invariant 11.3985, 0.047% apart). On the
subdominant mode the same disclosure is load-bearing and decides the sign of
the answer. A convention that was harmless one mode down is not harmless here.

### The one-mode closed form, and what the residual is

`C_car(d) - 1 = A2 * gap^d` with the DIRECTLY measured A2 has max relative
error **11.6%** over d = 10..50 and **1.88%** at d50. The A2 implied by
inverting the d10 anchor is 0.6303 vs the direct 0.5571 (ratio **0.8838**) —
P5 TRUE inside its registered factor-2 band, and the 12% shortfall IS the
third mode's contribution at d10, consistent with the per-hop ratio
approaching the gap from below. One mode accounts for the correction to ~12%;
two modes would close it.

## Predictions: 4 of 5

| cell | registered | measured | |
|---|---|---|---|
| P1 | CF_EXACT | CF_EXACT (C_prof(50) 0.999394) | correct |
| P2 | D_50 in [11.2, 11.6], > D10 | 11.37931 | correct |
| P3 | RATE_SPECTRAL, not ALTERNATING | RATE_SPECTRAL (0.8922 vs 0.8929) | correct |
| P4 | U2_HIGH (pct >= 0.95) | U2_NULL (pct 0.940, 0.0049 below p95) | **wrong** |
| P5 | direct A2 in [0.315, 1.26] | 0.557089 (0.884x the d10-implied 0.630) | correct |

Registration NOT amended on any branch-bearing quantity. Two disclosed
amendments, both caught by this card's own gates, neither moving a registered
number:

- **A1** — the PREREG's `OVERFLOW_DEGENERATE` guard says "any P_d ... zero"
  and fired at d=1, where `P_1 == 0` is not degeneracy but a structural
  anatomical fact: the carrier's 69 out-edges reach NO pool cell directly.
  L206 already records this (`deficit_ratio_by_depth[0]` is `None`, by the
  same cut). The guard is scoped to d >= 2, exactly L206's own reporting
  range; d=1 is recorded, never used. **Lesson: a numerical degeneracy guard
  must not be phrased so broadly that it fires on a known anatomical zero —
  scope it to the depths the registered statistics are READ at.**
- **A2** — `D_d` was first computed as `median(P_null)/P_real`. L206's SOURCE
  divides BOTH by `(LAM1**(d+1) * m_out_carrier)` first, and that
  normalisation — a provable NO-OP in exact arithmetic — **moves the last
  bit**: 10.388078940332742 vs the stored 10.38807894033274. The d=10 anchor
  gate halted the run. L206's law a third time: a float-equality claim is a
  claim about the EXPRESSION, not just the operands. **Corollary worth
  keeping: a mathematical NO-OP is not a FLOATING-POINT no-op, so re-use the
  parent's expression character for character even where the algebra says the
  factor cancels.**

## Certification (all halting, all green before the number it gates)

Inherited free as verbatim certified source slices (L85), no lab module
imported (L175), with **five INHERITED sha pins asserted by the BUILDER**
against the values L210 recorded in its own banner (l151_static.py 1-319
`e6245e8306dc8a0f`, l178_tail.py 7-149 `6e2e8fa4bd19eced`, l206_mid.py
`febbc390ad4f1a02`, l178_tail.py 348-458 `5bb7b56e6b6487d5`, l206_tail.py
22-263 `772a2410e76516e5`) plus a **PARENT PIN**: l210_tail.py's whole-file
sha256 `f254178d4c1a96c0` must equal the TAIL sha that `l210_static.py`'s own
generated banner recorded — otherwise the CERT-210M slice would not be the
code that produced the table CERT-218T certifies against.

- **CERT-210M** = `l210_tail.py` lines 1-326 VERBATIM (sha
  `c8daf059beff0258`), sliced to CUT L210's own predictions/writer block
  (L213), asserted POSITIVELY to contain CERT-206 / CERT-MV / CERT-LEFT /
  CERT-REBUILD / `def mv` / `def pi_dir` / `def lam2_defl` / `def coeff` /
  `rows210.append` / seed 21004, and NEGATIVELY to exclude
  `o["predictions"]`, `o["rows_per_draw"]`, `os.makedirs` and `json.dump`.
  Re-ran L210's whole measurement block for free: CERT-178 **420**,
  CERT-NULL **8**, CERT-206 **94**, CERT-MV **8**, CERT-LEFT, CERT-REBUILD
  **1,000** — all GREEN, and the 100 per-draw power iterations recomputed
  rather than read.
- **CERT-218T (HALTING, this card's required anchor) = 1,224 float
  equalities** before any d>10 number was read: **1,100** from the per-draw
  table (100 draws x 11 fields of `rows_per_draw`, recursive leaf compare at
  float equality) and **124** from L210's headline and certification blocks
  (Q210-1/2/3/4/5, cert_206, cert_mv, cert_rebuild, cert_178, cert_null,
  spectral). Plus the registered pins asserted rather than assumed:
  `gap == 0.8928793607351002`, `D10 == 10.38807894033274`, L210 branch still
  `B_CLOSED_FORM`.
- **CERT-W50 (HALTING) = 1,010 float equalities**: the depth-1..10 segment of
  every extended walk (1 real + 100 draws) reproduces the certified arrays
  exactly — the real walk through `sweep_actor`'s own pool-sum expression, the
  draws through the null loop's (the two differ in where `float()` is applied
  and are NOT interchangeable). This is also the gate on the one DISCLOSED
  re-transcription in the tail: the per-draw operator rebuild, which is not
  exposed as a function in the parent.
- **ANCHOR CONTINUITY (HALTING)**: `D_prof(10) == D10`,
  `R_asym(10) == L210's R_asym`, `C_car(10) == L210's C_real`, all at float
  equality — the extension is literally continuous with the parent.
- **CERT-DEFLV (HALTING)**: `defl_pair`, the vector-returning deflation, is
  admitted only by EXACT float equality of its eigenvalue and every
  convergence field against the certified `lam2_defl` on the real operator
  plus 3 probe draws (the CERT-MV pattern: a new kernel is gated by exact
  agreement with the certified one), and its real-operator eigenvalue asserted
  equal to the parent's stored `LAM2`.
- **NO-OP re-measured** (L209, measured not asserted): a global x3.7 rescale
  moves `C_car` by max **3.32e-15** over all 50 depths and the per-draw
  correction by **4.00e-15** over 5 x 50. The one remaining step — a positive
  scalar commutes with the median over draws — is arithmetic and is disclosed
  as such rather than claimed as measured.
- **FINITENESS / POSITIVITY** asserted at every depth of every walk (the
  float64 overflow risk is real: `lam1^50 ~ 1e74`).
- Four prior artifacts (`l178/static.json`, `l206/static.json`,
  `l210/static.json`, `l210_static.py`) opened READ-ONLY with
  (size, mtime_ns) fingerprinted before and asserted unchanged after, plus
  `md5sum -c` against `l218/prior.md5` taken before the run (L175).

**This card's own two new halting gates: 2,234 float equalities.** L210's
1,530 re-ran free inside the slice.

## What this does NOT establish (named, not buried)

- One substrate (f4wA), one operator (|g W_beta|), one null family (the l169c
  destination swaps). L207's cross-null law stands.
- A closed form is still not a mechanism. CF_EXACT only moves the avoidance to
  "where the carrier's 69 out-edges point, weighted by the targets' own
  left-Perron importance" — that is L219/L211 and is NOT re-banked here.
- The carrier was SELECTED for being extreme on a related statistic
  (Kriegeskorte 2009). Every carrier-specific number here is a DESCRIPTION of
  a selected object; the 100 draws null the WIRING, not the selection.
- Depth 50 is not infinity. CF_EXACT is a statement about d50 with a measured
  rate attached.
- The two-mode closed form was NOT fitted — only the one-mode form was tested,
  and its 11.6% worst-case residual is a pointer, not a measurement of lam3.
