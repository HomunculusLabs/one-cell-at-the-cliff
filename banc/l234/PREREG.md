# L234 PREREG — the TWO-MODE closed form, and K2's own null

Registered: 2026-11-24, tick 266, BEFORE any third-mode number exists and
before any per-draw K2 is computed. Static, zero rollouts, zero settles.
Substrate: f4wA anatomical operator `|g*W_beta|`, the 100 l169c destination
swaps. One write: `l234/static.json`.

Parent card: L218 (`l218/static.json`), whose entire measurement block is
re-executed here as SLICE A = `l218_static.py` lines 1-1691 VERBATIM (a
literal PREFIX cut immediately before L218's own predictions/writer block).

---

## What L218 left open

L218 established, on the carrier's convergence correction
`e(d) = C_car(d) - 1`:

- the one-mode closed form `e(d) = A2 * r2^d` with `r2 = GAP = 0.8928793607351002`
  and `A2 = K2/K = 0.5570889573086877` measured DIRECTLY from the deflated
  eigenpair, worst relative error **0.1161651165819561** over d10-50 and
  **0.018751052033734623** at d50;
- `A2_implied_by_d10_anchor = 0.6303088594492495`, so
  `A2_direct/A2_implied = 0.883834883418044` — L218's own card says that
  0.884 ratio "is the THIRD mode at d10, unmeasured";
- `A2 = K2/K` is the ratio, and K2 has **no null of its own** in the stored
  artifacts: `rows_per_draw_recomputed` carries per-draw `K` but not per-draw
  `K2` (verified in `l234/probe.out`), so only `A2_percentile = 0.94` exists
  while K's own percentile is `0.0`.

## Premise corrections (registered first; nine)

**0a. SLICE A is a PREFIX of the generated parent, not of the tail.**
`l218_tail.py` is a literal SUFFIX of `l218_static.py` and its whole-file
sha256 `5db068f586f3f097` is the value `l218_static.py`'s own banner records;
the parent's banner (its first 10 lines) is itself stored inside
`l218/static.json["banner"]`, so the chain
`banner-in-json == banner-in-script` is what proves SLICE A is the code that
ACTUALLY produced the artifact this card certifies against. All three are
asserted in the builder and re-asserted at run time.

**0b. The closed form must use the SIGNED ratio, not the gap.** L218 wrote
`A2 * GAP^d` with `GAP = |lam2|/lam1`; that is only the right object because
L218 measured `lam2_signed_rayleigh = +26.9469...` (positive). A third real
eigenvalue may be NEGATIVE, in which case its term is
`A3 * (lam3/lam1)^d = A3 * (-1)^d * gap3^d` and ALTERNATES. The registered
form is therefore `e(d) = A2*r2^d + A3*r3^d` with `r_k = lam_k/lam1` SIGNED,
`r2` pinned to GAP only after asserting `sign(lam2_signed) > 0`.

**0c. A3 must be the SAME construction as A2.** `A3 = K3/K` with
`K3 = u3[c] * S_v3 / (u3 . v3)`, which is invariant to the arbitrary sign and
scale of both u3 and v3 exactly as K2 is. A FITTED A3 is a different object
(one free parameter) and is reported as a DESCRIPTIVE companion only.

**0d. The eigenpair gate is the RESIDUAL, never the convergence spread**
(L217). Both the right and the left doubly-deflated iterations must reach
relative residual `<= RES_BAR = 1e-3` (L218's own bar, where it measured
~7e-9), and the SIGNED Rayleigh quotients of the two sides must agree in
sign. Failing either is a legitimate **CF_UNRESOLVED** outcome, and in that
case the one-mode form with its 11.6% band is the reportable object — the
card says so in advance.

**0e. A new deflation kernel is admitted only by exact agreement with the
certified one.** `defl_multi` (a list of Hotelling pairs) called with the
SINGLE pair `(V1,U1)` must reproduce `defl_pair` bit-for-bit on the
eigenvalue, the iterate and every convergence field; `defl_resid_multi` with
one pair must likewise reproduce `defl_resid`. CERT-234B, halting.

**0f. The per-draw K2 is RE-COMPUTED, not derived.** `K2_k` could be derived
as `A2K[k] * KK[k]` from the slice's own arrays, but that is a float
division followed by a multiplication and is not bit-exact. The registered
path re-runs the deflation for all 100 draws and gates each draw on
`K2_k / KK[k] == A2K[k]` at FLOAT EQUALITY (CERT-234C, halting, 100 checks).
The derived shortcut is computed anyway and its max relative disagreement
with the exact value is REPORTED, as a measurement of the cost slice this
card declined to take (L226).

**0g. Medians do not compose.** `median(K2_k)/median(K_k)` and
`median(K2_k/K_k)` are DIFFERENT statistics; the card requires both, and the
stored `A2_draw_med = 0.21115719052097356` is the second one.

**0h. A percentile floor is a resolution statement.** With 100 draws the
finest non-zero percentile is 0.01; `pct == 0.0` means "below all 100 draws"
and nothing finer. Reported as such, never as a p-value.

**0i. The residual's shape is DERIVABLE FROM STORED ARTIFACTS and is
therefore DESCRIPTION, not a finding** (L214). `l234/probe.out` reads
`l218/static.json` only and already establishes: the one-mode residual
`R(d) = e(d) - A2*r2^d` is single-signed POSITIVE on d10-50 with ZERO sign
changes; its per-hop log-ratio is NOT constant (first -0.253992, last
-0.145012, median -0.143824, spread 0.114516), so the residual is not one
clean geometric mode; a two-point (d10,d50) estimate implies
`r3 = 0.850857` (lam3 25.6787) and `A3 = 0.118575`, and that implied
two-mode form still misses by max **3.2559%** over d10-50. These are the
quantities the card's PREDICTIONS are registered against — the predictions
are about the MEASURED third eigenpair reproducing them, which is not
derivable from anything stored.

---

## Registered questions and branches

**Q1 (leg a) — does a measured third mode close the closed form?**
Compute the third eigenpair of the f4wA operator by DOUBLE Hotelling
deflation (against the Perron pair and the subdominant pair), gate per 0d,
form `A3 = K3/K` per 0c, and read
`relerr(d) = |A2*r2^d + A3*r3^d - e(d)| / |e(d)|` over d = 10..50.

- `CF_UNRESOLVED` — the third pair fails 0d's residual/sign gate.
- `CF_TWO_MODE` — max relerr over d>=10 **< 0.01**.
- `CF_PARTIAL` — max relerr >= 0.01 but at least **2x** better than L218's
  one-mode 0.1161651165819561.
- `CF_NO_IMPROVEMENT` — otherwise.

**Q2 (leg b) — K2's own null, beside K's.** Store the 100 per-draw K2, and
read `pct_K2 = mean(K2_k < K2_real)` against K's stored `0.0`.

- `K2_FLOOR` — `pct_K2 == 0.0`: the carrier's subdominant overlap is
  suppressed at the same floor as its dominant overlap, and the ratio A2
  (pct 0.94) is the ONLY instrument that separates the two modes.
- `K2_SEPARATED` — `pct_K2 > 0.0`: the two marginals genuinely differ in how
  extreme they are.

**Q3 — the compose check (description, no branch).** Report
`median(K2_k)/median(K_k)` beside `median(K2_k/K_k)` and their relative
disagreement, per 0g.

## Predictions (6)

- **P1**: Q1 branch == `CF_PARTIAL`. (Reason, disclosed as stored-derived:
  the residual's per-hop log-ratio spread is 0.1145, so one more geometric
  mode cannot close d10 to 1%.)
- **P2**: the measured SIGNED `lam3 > 0` (the residual is single-signed
  positive with zero sign changes).
- **P3**: `gap3 = |lam3|/lam1` in **[0.82, 0.90]**.
- **P4**: direct `A3 = K3/K` in **[0.0593, 0.2372]** (within 2x of the
  two-point implied 0.118575 — the L218-P5 analogue).
- **P5**: Q2 branch == `K2_FLOOR`.
- **P6**: `median(K2_k)/median(K_k)` differs from `median(K2_k/K_k)` by more
  than **1%** relative (0g made concrete).

## Halting gates

- **CERT-234A** — every leaf of `l218/static.json` outside
  {predictions, amendments, limitations, priors_readonly,
  rows_per_draw_recomputed} reproduced from this run's own `o` dict at FLOAT
  EQUALITY, on a coverage bar DERIVED from the artifact's own leaf count
  (L224). This subsumes CERT-218T (1224) and CERT-W50 (1010), which re-run
  inside SLICE A as the code that produced them.
- **CERT-234B** — 0e's kernel admission, exact float equality.
- **CERT-234C** — 0f's 100 per-draw ratio equalities.
- AST audits: no lab module imported (L175); exactly ONE write site; SLICE A
  proven write-free on its own AST; the cut lines audited STRUCTURALLY by AST
  (not by bare tokens — the repeated lesson).
- `md5sum -c l234/prior.md5` green before and after; (size, mtime_ns)
  fingerprints on every prior artifact unchanged.

## Limitations (registered)

One substrate (f4wA), one operator, one null family (l169c destination
swaps), one carrier. 100 draws caps every percentile at 0.01 resolution.
`e(d)` is a RATIO profile, so a mode's "coefficient" here is a ratio of
overlap coefficients and not an amplitude in any physical unit. No per-draw
third mode is computed: Q1 is a real-operator question and the card does not
register a K3 null.
