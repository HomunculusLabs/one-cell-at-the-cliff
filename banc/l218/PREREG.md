# L218 PREREG — the CONVERGENCE CORRECTION as its own object (static, zero rollouts)

Written BEFORE any L218 number was read. Card: LANE.md L218 (ideas 106).
Substrate: f4wA (the syn>=4-floored closure substrate L178/L205/L206/L209/L210 use).
Operator: A = |g * W_beta| with g = G_F4WA = 0.15051452517509462, the
ANATOMICAL (row-mask-free, settle-free) form. CSR convention W[target, source].
Zero rollouts, zero settles, zero dynamics. Nulls: the SAME 100 l169c
degree-neutral destination swaps L178/L206/L210 use (seed 16943).

---

## 0. PREMISE CORRECTIONS AND OBSERVATION STATUS (written before the script existed)

### 0a. The card's "converges to the u1-overlap ratio" has TWO forms and they are not the same number

L210's closed form is

    P_d(c) -> lam1^d * K(c),   K(c) := u1[c] * S_v / (u1 . v1),

so the asymptotic prediction of the measured deficit at depth d is

    R_asym(d) := median_k( lam_k^d * K_k ) / ( lam1^d * K_REAL ).

The card says "converges to the u1-overlap ratio", which reads as the
DEPTH-FREE quantity K_ratio_med := median_k(K_k)/K_REAL. Those differ by the
factor median_k(lam_k)^d / lam1^d, which L210 measured as 0.99977 at d=10 and
which therefore moves by roughly five times as much at d=50. The two forms are
BOTH reported; **R_asym(50) is the PRIMARY** because it is the correct
asymptotic statement for a finite depth, and the depth-free K_ratio_med is
reported beside it as the card's literal wording with the lam-power factor
printed explicitly. Registering this now so the choice cannot be made after
seeing which one passes.

### 0b. L209's no-op law applies and is re-measured, not assumed

Every registered L218 quantity is a RATIO of masses at the SAME depth, so a
global rescaling of the operator cannot move it (L209). The lam1^d division in
R_asym appears once in numerator and once in denominator of the comparison
with D_d and cancels; this is asserted as a measured NO-OP, not asserted in
prose.

### 0c. OBSERVATION STATUS (Kriegeskorte 2009; the L214 rule)

While scoping this tick I read the SUMMARY fields of `l210/static.json` and
`l210/VERDICT.md`. The following are therefore OBSERVED and are declared
**DESCRIPTION**, not test outcomes:

- D10 = 10.38807894033274 (L206 stored, CERT-206 pinned)
- R_asym(10) = 11.3985, ratio R_asym/D10 = 1.0973, bar 0.10 -> B_CLOSED_FORM
- R_bare = 11.4039, K_ratio_med = 11.4016
- C_real = P_10/(lam1^10 K_REAL) = 1.2030; C_twin = 1.1755;
  C_null_med = 1.1029 [p05 0.9864, p95 1.2245]
- lam1 = 30.179788269078884; null lam median 30.179083, min 30.176121;
  lam_ratio_med_pow10 = 0.99977
- |lam2| = 26.9469 (Hotelling deflation, rel spread last-6 3.09e-10),
  gap = |lam2|/lam1 = 0.8928793607351002, gap^10 = 0.322
- u1[carrier] = 4.0973e-04 real vs null median 4.6726e-03, percentile 0.0
- carrier K/m_out = 3.166e-05, rank 4 of 35, family median 4.602e-04
- L206's deficit profile d2..d10: 8.378, 7.641, 9.784, 9.944, 10.002,
  10.156, 10.279, 10.357, 10.38808
- cos(x_10, v1) carrier 0.9649

I have NOT read any individual row of `rows_per_draw` (the per-draw lam_k,
K_k, u_car table); those are consumed only through the halting gate below.

Genuinely UNOBSERVED when this file was written, and therefore the only
objects branches are placed on:

1. the deficit profile D_d for d = 11..50 (and hence D_50)
2. R_asym(d) for d > 10
3. the per-hop ratio of the convergence correction (its rate)
4. the SIGN structure of the correction (whether lam2 is positive, negative,
   or an unresolved/complex pair)
5. the subdominant left-overlap of the carrier, u2[carrier] and K2(carrier),
   on the real operator and on all 100 draws
6. every residual/resolution diagnostic of the deflated eigenpairs

### 0d. The card's "no per-draw power iterations needed" is NOT taken

The card says L210 already stored lam_k/K_k/u_car per draw, so forward walks
suffice. The card's own Verify line, however, demands those stored values be
reproduced at float equality before any d>10 number is read — and reproducing
them IS the per-draw power iteration. This card therefore RE-RUNS L210's whole
measurement block as a verbatim source slice (the L213 pattern: slice the
parent tail at the end of its measurement block, cutting its writer), which
makes CERT-206 and CERT-REBUILD re-run for free as halting gates and makes the
per-draw table a reproduced object rather than a read one. Disclosed as a cost
decision (minutes of CPU) taken in favour of the stronger gate.

---

## 1. The statistics (registered)

Let, for the real operator and each draw k, with the pool index set = the 303
cells of the 20 semantic pools (key order as inherited):

    P_d        = pool arrival mass at depth d from the carrier, real operator
    P_d^(k)    = the same on draw k's operator
    D_d        = median_k( P_d^(k) ) / P_d                       (the DEFICIT)
    R_asym(d)  = median_k( lam_k^d K_k ) / ( lam1^d K_REAL )
    C_prof(d)  = D_d / R_asym(d)                   (the CONVERGENCE CORRECTION)
    C_car(d)   = P_d / ( lam1^d K_REAL )       (the REAL CELL's own correction)
    C_k(d)     = P_d^(k) / ( lam_k^d K_k )

DEEP = 50. The depth-1..10 segment of every forward walk is asserted at FLOAT
EQUALITY against the certified arrays (SW["carrier"]["P"] for the real walk,
NP_ for the draws) using each one's OWN expression — the real walk through
`sweep_actor`'s expression, the draws through the null loop's expression
(L206's law: a float-equality claim is a claim about the EXPRESSION).

---

## 2. Gate cells (SEPARATE objects, L109)

### Q218-1 (PRIMARY, branch-bearing): does the deficit converge to the closed form?

Registered branches, evaluated IN THIS ORDER:

- **OVERFLOW_DEGENERATE** iff any P_d, P_d^(k), lam_k^d K_k or D_d for
  d <= 50 is non-finite or zero. Then no number past the last finite depth is
  reported and the card is re-posed at a smaller DEEP. (Declared first because
  lam1^50 ~ 1e74 and this is a real float64 risk, not a formality.)
- **CF_EXACT** iff |C_prof(50) - 1| <= 0.01 — the closed form is exact by d50
  and the draft sentence is ONE number.
- **CF_PLATEAU_OTHER** iff not CF_EXACT and the profile has PLATEAUED:
  max over d in [40,50] of |C_prof(d) - C_prof(50)| / |C_prof(50)| <= 0.005.
  Then a third mode (or a non-simple spectrum) carries the remainder and the
  L210 factorisation is INCOMPLETE — the honest sentence names the residual
  factor rather than hiding it in "approximately".
- **NO_PLATEAU** otherwise — the phrase "depth-invariant" is retired in favour
  of a depth PROFILE (L209's law), and the draft reports the profile.

Reported beside the branch, unconditionally: D_50, R_asym(50), K_ratio_med,
the lam-power factor median_k(lam_k)^50 / lam1^50, C_car(50), median_k C_k(50),
and the full D_d / C_prof(d) / C_car(d) profile at d = 1..50.

### Q218-2 (the RATE of the correction; non-branch-bearing, registered)

If the correction is carried by the subdominant mode then
C_car(d) - 1 = A2 * (lam2/lam1)^d with A2 = K2/K, so successive differences
have constant ratio gap = 0.8928793607351002 (certified from L210 by
CERT-GAP-style float equality before use).

- **RATE_ALTERNATING** iff (C_car(d) - 1) changes SIGN between consecutive
  depths anywhere in d = 15..50 — then lam2 is negative or complex and the
  geometric law must be read in |.| with an alternating sign. Declared FIRST
  because it changes what the next statistic means.
- **RATE_SPECTRAL** iff median over d in [20,45] of
  (C_car(d+1) - 1)/(C_car(d) - 1) is within **0.02 ABSOLUTE** of gap.
- **RATE_OTHER** otherwise — report the measured rate and what it implies
  about |lam3|/lam1 or about the deflation.

Registered in advance: this leg needs NO eigenvector, so it survives an
unresolved deflation and is the fallback carrier of the card's second question.

### Q218-3 (the card's second leg: is the carrier's SLOWER mixing a subdominant-overlap effect?)

Primary statistic: **A2 := K2(carrier) / K(carrier)** where
K2(c) := u2[c] * S_v2 / (u2 . v2) is the exact subdominant analogue of K
(u2, v2 = the left/right subdominant vectors from the SAME Hotelling
deflation, seed 21004, iters 400). The carrier's A2 is compared to the 100
draws' A2_k.

- **U2_UNRESOLVED** iff the real operator's deflated eigenpair fails the
  residual gate below. Then no overlap number is used for inference and the
  leg is descriptive; Q218-2 carries.
- **U2_HIGH** iff resolved and the real A2 percentile among the draws >= 0.95
- **U2_LOW** iff resolved and percentile <= 0.05
- **U2_NULL** otherwise.

RESIDUAL GATE (L217's law: diagnose an eigenpair with its RESIDUAL, never the
iteration's convergence spread). For the deflated operator B and converged
unit iterate x, with y = Bx and lam_fit = x . y, define
res_rel = ||y - lam_fit x|| / ||y||. A pair is RESOLVED iff res_rel <= 1e-3.
The real operator's res_rel is printed as the calibration reference beside
every draw's.

MAGNITUDE DISCIPLINE (L175, registered in advance): a tight paired null on a
tiny absolute difference is a DIRECTION, never a magnitude. If
|A2_real - median_k A2_k| < 0.05 the reading is **DIRECTIONAL ONLY** and is
written that way in the verdict however extreme the percentile is.

Reported beside A2: the card's LITERAL form |u2[carrier]| under unit-L2
normalisation, carrying L210 Q210-2's disclosure verbatim — unit-L2
normalisation of a vector on two DIFFERENT operators is a CONVENTION, not a
canonical comparison; A2 is the scaling-invariant form and carries the branch.

---

## 3. Predictions (recorded now; being wrong is a result, not a failure)

- **P1**: Q218-1 = **CF_EXACT**. Reasoning: gap^50 = 0.00347 and the d=10
  anchor implies A2 ~ 0.63, so |C_car(50) - 1| ~ 0.0022; C_prof divides two
  such corrections and should be closer still.
- **P2**: D_50 in [11.2, 11.6] and D_50 > D10 = 10.38807894033274 (the profile
  keeps RISING monotonically from d=7 on, with no overshoot above R_asym).
- **P3**: Q218-2 = **RATE_SPECTRAL**, and NOT RATE_ALTERNATING (L206's d7..d10
  profile rises monotonically, which is the signature of a POSITIVE real
  lam2).
- **P4**: Q218-3 = **U2_HIGH** (real A2 percentile >= 0.95) — the carrier's
  slower approach to the dominant mode IS a subdominant-overlap effect.
- **P5**: the DIRECTLY computed A2 agrees with the value implied by the d=10
  anchor, (C_real - 1)/gap^10 = 0.2030/0.32225 = 0.630, within a factor of 2
  (i.e. A2 in [0.315, 1.26]).

---

## 4. Certification plan (all halting, all green before any L218 number)

- **CERT-210M** = `l210_tail.py` lines 1-326 VERBATIM, sliced to CUT L210's own
  predictions/writer block (L213). Carries CERT-206 (94 stored L206 G1 values
  at float equality incl. the D10 pin), CERT-MV (8 exact array equalities),
  CERT-LEFT, CERT-REBUILD (1,000 stored null values at float equality) and the
  per-draw power iterations that produce rows210. Its slice is asserted to
  contain those gates POSITIVELY and to exclude `o["predictions"]`,
  `os.makedirs` and `json.dump` NEGATIVELY.
- **PARENT PIN**: `l210_tail.py`'s whole-file sha256 must equal the TAIL sha
  that `l210_static.py`'s own generated banner recorded, so slicing a parent
  that MOVED since it produced `l210/static.json` HALTS the build.
- **INHERITED PINS**: the five slice shas L210 recorded in its banner
  (l151_static.py 1-319, l178_tail.py 7-149, l206_mid.py, l178_tail.py
  348-458, l206_tail.py 22-263) asserted by the BUILDER.
- **CERT-218T (HALTING, this card's required anchor)**: every field of every
  row of `l210/static.json`'s `rows_per_draw` (100 draws x 11 fields)
  reproduced at FLOAT EQUALITY from the recomputed rows210, PLUS L210's
  headline scalars (Q210_1 / Q210_2 / Q210_3 / Q210_4 / Q210_5) at float
  equality. Nothing at d > 10 is computed until this is green.
- **CERT-W50 (HALTING)**: the depth-1..10 segment of the extended real walk
  reproduces `SW["carrier"]["P"]` at float equality (10 checks) and the
  depth-1..10 segment of each extended draw walk reproduces `NP_` at float
  equality (1,000 checks), each using its own source expression.
- **CERT-DEFLV (HALTING)**: the vector-returning deflation used for u2/v2 is
  gated by EXACT FLOAT EQUALITY of its returned eigenvalue and convergence
  info against the certified `lam2_defl` on the real operator and on 3 probe
  draws — a new kernel is admitted only by exact agreement with the certified
  one (the CERT-MV pattern).
- **NO-OP re-measured**: a global rescale of the operator must move every
  registered L218 ratio by < 1e-12 relative.
- **FINITENESS**: every depth of every walk asserted finite and positive.
- Prior artifacts (`l178/static.json`, `l206/static.json`, `l210/static.json`,
  `l210_static.py`) opened READ-ONLY, (size, mtime_ns) fingerprinted before and
  asserted unchanged after, plus `md5sum -c` against `l218/prior.md5` taken
  before the run (L175).

## 5. What this card cannot establish (named now)

- One substrate (f4wA), one operator (|g W_beta|), one null family (the l169c
  destination swaps). L207's cross-null law stands: a different null gives a
  different magnitude.
- A closed form is still not a mechanism. Even CF_EXACT only moves the
  avoidance to "where the carrier's 69 out-edges point, weighted by the
  targets' own left-Perron importance" — that decomposition is L219/L211 and
  this card must not re-bank it.
- The carrier was SELECTED for being extreme on a related statistic
  (Kriegeskorte 2009): every carrier-specific number here is a DESCRIPTION of
  a selected object. The 100 draws are a null for the WIRING, not a null for
  the selection.
- Depth 50 is not infinity. CF_EXACT at d50 is a statement about d50 with a
  measured rate attached, never about the limit.
