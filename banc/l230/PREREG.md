# L230 PREREG — the CROSSING-PHASE law (static, zero rollouts)

Written 2026-11-23 ~23:50 EST, tick 262, BEFORE l230_static.py existed and
before any L230 quantity was computed by machinery. Premise corrections below
are read from STORED artifacts (l216/static.json, l217/static.json) and are
declared, with their values, so nothing in this card can be back-dated.

## The question

L216 turned L209's "decay" into a CROSSING: on the beta operator every pool
cell starts right-heavy at depth 1 (A_cell < 0) and ends left-heavy at the
Perron asymptote (A_inf > 0), and the two joints differ only in WHEN. L216's
own two-term model is

    A_cell(d) = A_inf + K * rho^d

so the crossing depth has a closed form

    d_cross = log(-A_inf / K) / log(rho)

i.e. the PHASE is fixed by exactly two numbers — the asymptote A_inf and the
depth-1 overlap K — with the SAME rho for both joints on a substrate x
operator. L230 asks what sets the phase: is the Ti-vs-Tr crossing difference
carried by K (how right-heavy the DIRECT drive is) or by A_inf (where the
asymptote sits)?

## 0. Premise corrections (ALL pre-measurement, from stored artifacts)

**0a. THE WHOLE OF Q1 AND Q2 IS OBSERVED-DERIVABLE AND IS SCORED AS
DESCRIPTION.** Every input to the closed form (A(1..8), A_inf, rho) is stored
in l216/static.json, and the measured d_cross is stored in l217/static.json.
Therefore the closed form, the residual against the measured crossing, the
exact additive attribution and the Q1 branch are ARITHMETIC ON STORED VALUES.
Per L214, registration here buys a DECISION RULE and multiplicity discipline,
never inference. I state the arithmetic I did in my head before writing this
file: for the primary pair f4wA|beta the stored asymptotes are A_inf(Ti)
0.2866252046577441 and A_inf(Tr) 0.4442160473631981 (ratio 0.6452), rho =
0.8928793607351003, and L217's stored measured crossings are 4.076075685116105
(Ti) and 1.252243179691547 (Tr), D_meas = 2.8238. The A_inf term of the
decomposition is therefore log(0.6452)/log(rho) ~ +3.87 hops against a total
of 2.82, so P1 below is registered WITH that knowledge and is DESCRIPTION.
The honest consequence: the inferential content of this card is Q3 alone.

**0b. L217 ALREADY OWNS THE MEASURED-CROSSING NULL AND FOUND IT DEGENERATE.**
l217/static.json Q1_crossing_phase: branch PHASE_DEGENERATE, D_real null,
null_frac_both_cross 0.0505 over 2000 draws. L230 must NOT re-pose that
contrast; it re-poses it in the CLOSED-FORM currency, whose crossing event
does not require the crossing to land inside d <= 8.

**0c. THE CROSSING IS A BETA-OPERATOR STATEMENT; 2 of 4 CROFTS CELLS DEVIATE.**
From stored `fits[*].crosses_zero`: 6 of 8 cells cross inside d<=8 — all four
beta cells, plus cutwA|crofts|Tr and f4wA|crofts|Tr. The card's sentence
"every beta cell" is correct; its sentence "all 8 cells" is not a statement
about a measured crossing. Scored as written anyway.

**0d. THE CLOSED FORM IS DEFINED ON ONE MORE CELL THAN THE MEASUREMENT.**
Pre-measured sign structure (stored A_inf and A(1), K := (A(1)-A_inf)/rho):
A_inf > 0 on 7 of 8 cells and K < 0 on 8 of 8, so -A_inf/K > 0 (the closed
form exists) on 7 of 8 — including f4wA|crofts|Ti, which is CENSORED in the
measurement (no sign change by d=8) but whose two-term model predicts a
crossing beyond depth 8. The single cell where the closed form does NOT exist
is cutwA|crofts|Ti, whose asymptote is NEGATIVE (-0.008413002252988949): same
sign as K, so the model says it never crosses, in agreement with the censored
measurement for a principled reason. This is registered as a premise, not a
result.

**0e. THE RESIDUAL LEG IS UNMEASURABLE ON THE CENSORED CELLS (L222).** For
f4wA|crofts|Ti there is a closed-form d_cross and NO measured one, so
|d_cf - d_meas| does not exist. It is scored FALSE BY UNMEASURABILITY, never
as a small residual, and the registered escape SHORT-CIRCUITS that cell's leg.

**0f. K HAS TWO DEFENSIBLE CURRENCIES; THE CARD'S OWN WORDS PICK ONE.** The
card says "the depth-1 overlap K", so the PRIMARY currency is the depth-1
anchor K_anchor = (A(1) - A_inf) / rho with rho = the stored spectral gap
|lam2|/lam1, shared by both joints on a substrate x operator. The companion
currency is L216's stored deep fit, K_fit = sign(resid) * c_deep with the
cell's OWN r_deep in place of rho — which breaks the "same rho for both
joints" premise and is therefore reported beside the primary, never swapped
into the branch (L218/L227/L229: register which currency carries the branch).
Stored `resid` has a CONSTANT sign on all 8 cells, so sign(resid) is
well defined.

**0g. rho IS THE SPECTRAL GAP, AND IT IS SHARED WITHIN A SUBSTRATE x
OPERATOR BY CONSTRUCTION** (stored `gaps`): cutwA|beta 0.8981757358357637,
cutwA|crofts 0.9574233066787261, f4wA|beta 0.8928793607351003, f4wA|crofts
0.9754528114820759. Both joints of a pair read the same number, which is what
makes the log-decomposition additive.

**0h. THE DECOMPOSITION IS AN EXACT IDENTITY, NOT A FIT.** With a shared rho,

    d_cross(J) = [ln(A_inf(J)) - ln(|K(J)|)] / ln(rho)
    D := d_cross(Ti) - d_cross(Tr) = T_A + T_K
    T_A = ln(A_inf_Ti / A_inf_Tr) / ln(rho)
    T_K = -ln(|K_Ti| / |K_Tr|) / ln(rho)

so the attribution needs no estimator. The identity is ASSERTED at a tolerance
DERIVED from the term magnitudes (L216/L224: never a fixed tolerance).

**AMENDMENT 0h-i (added 2026-11-24 ~00:2x, DISCLOSED, pre-outcome).** This
line was first written as `[ln(-A_inf) - ln(|K|)]/ln(rho)`, which is a
notation slip: on a crossing cell A_inf > 0 and K < 0, so the minus sign in
`-A_inf/K` is carried entirely by K and the correct split is
`[ln(A_inf) - ln(|K|)]/ln(rho)`. The slip evaluated log(negative) = nan and
the identity's OWN assert halted the run before any Q1 quantity was computed
or written; the T_A / T_K definitions above were already correct (they consume
the positive ratio A_inf_Ti/A_inf_Tr) and are unchanged. No outcome was
observed between the halt and the repair. This is the only amendment.

**0i. A CLOSED-FORM d_cross IS HEAVY-TAILED IN THE NULL.** d_cf -> +-inf as
K_null -> 0, so no MOMENT of the null distribution is admissible. Every Q3
read is a PERCENTILE or a rate, the null's median/IQR are reported instead of
its mean, and the resolution floor 1/(B+1) = 1/2001 = 4.9975e-04 is printed
beside every percentile (L225).

**0j. THE CEILING/SATURATION CORRECTION DOES NOT APPLY.** This is the
ANATOMICAL operator (L164): no rates, no relu, no gate. tick 260's L260
saturation amendment is out of scope here and is NOT silently inherited.

## 1. Registered quantities

For all 8 substrate x operator x joint cells: rho, A_inf, A(1), K_anchor,
cf_defined, d_cf (primary currency), d_meas (L217's stored expression,
re-derived here by its verbatim function), resid = |d_cf - d_meas|, and the
K_fit companion. For each substrate x operator PAIR with both joints
cf-defined: D_cf, T_A, T_K, share_K = |T_K| / (|T_A| + |T_K|), and the A_inf
ratio A_inf_Ti / A_inf_Tr.

PRIMARY PAIR: **f4wA|beta** (L216's primary cell's substrate x operator, and
L217's Q1 cell).

## 2. Registered branches

**Q1 (DESCRIPTION + decision rule), evaluated on the PRIMARY pair in the
PRIMARY currency, in this order:**

1. `PHASE_MODEL_INSUFFICIENT` — if max over the pair's two joints of
   |d_cf - d_meas| > 0.5 hops. The card: "if the two disagree by more than
   half a hop the two-term model is insufficient at crossing depth and that
   is the finding." This branch SHORT-CIRCUITS: the attribution below is
   still computed and reported, but it cannot carry the verdict.
2. `PHASE_FROM_K` — share_K >= 2/3 AND 0.5 <= A_inf ratio <= 2.0.
3. `PHASE_FROM_K_DESPITE_AINF` — share_K >= 2/3 and the A_inf ratio outside
   [0.5, 2.0]. Registered because the card's clause (i) is a CONJUNCTION of
   two conditions that can disagree, and a "carried by K" verdict with a
   large asymptote ratio is a different finding from one without.
4. `PHASE_FROM_AINF` — share_K <= 1/3.
5. `PHASE_MIXED` — otherwise (1/3 < share_K < 2/3).

**Q3 (the INFERENTIAL leg; the instrument L217 named and could not build),
on the PRIMARY pair, using L216's own 2000 membership-permutation draws
(seed 20526, per-side counts held exact):**

For each draw, A_inf_null and A_null(1) give K_null and a closed-form
crossing depth exactly as for the real wiring. Registered IN THIS ORDER:

1. `CF_NULL_DEGENERATE` — if the fraction of draws in which BOTH joints'
   closed form is defined is < 0.50. Then the D_cf percentile is WITHHELD,
   not approximated (L229), and the Q3 verdict is an INSTRUMENT verdict.
2. `CF_SEPARATED` — pct_abs(|D_cf|) >= 0.95 among the draws where both are
   defined.
3. `CF_NOT_SEPARATED` — otherwise.

The existence RATE is registered as the FIRST read, before any contrast on
the event (L217's own law).

## 3. Predictions

- **P1 (DESCRIPTION, declared under 0a):** Q1 branch == `PHASE_FROM_AINF`.
- **P2 (DESCRIPTION, declared under 0a):** the two-term model's residual
  |d_cf - d_meas| <= 0.5 hops on BOTH primary joints (i.e. Q1 does not route
  to PHASE_MODEL_INSUFFICIENT).
- **P3 (blind):** the closed form's JOINT existence rate in the null is
  >= 0.50 — the cf currency rescues L217's unscoreable contrast.
- **P4 (blind):** that rate is at least 2x L217's stored measured-crossing
  joint rate of 0.0505.
- **P5 (blind):** Q3 branch == `CF_SEPARATED`.
- **P6 (blind):** the real primary share_K is NOT extreme against its own
  null, pct_abs(share_K) <= 0.95 — the K-vs-A_inf attribution is a generic
  property of any L/R split of these cells, not a wiring-specific one.

## 4. Verify (the card's own line, plus what this build adds)

- **CERT-205 and CERT-209 HALTING** — inherited for free: l230_static.py is
  l216_static.py lines 1-1360 VERBATIM (a literal PREFIX cut immediately
  before the parent's writer), AST-verified to contain ZERO write sites, so
  every pin, CERT-F4, CERT-178, CERT-GEN, CERT-205, CERT-GAP and CERT-209
  re-runs as the code that actually produced l216/static.json.
- **CERT-216 (HALTING)** — l216/static.json `table` (all 64 depth cells),
  `A_inf` (8 cells), `gaps` (4) and `fits` (8) reproduced from this run's own
  in-memory objects at FLOAT EQUALITY before any crossing is read, with the
  coverage bar DERIVED FROM THE ARTIFACT (stored field sets and leaf counts,
  never a hand-typed number — L224/L225).
- **THE NO-OP RE-ASSERTED** — MAXREL == stored `norm_noop_max_rel_diff`, and
  every cell's stored `A_cell_unnormalised` / `A_cell_norm_rel_diff`
  reproduced at float equality.
- **CERT-217 (HALTING)** — L217's stored `d_cross`, `n_sign_changes`,
  `censored`, `null_frac_cross` and the three null d_cross percentiles
  reproduced at FLOAT EQUALITY on the 8 beta/crofts cells, using L217's
  `dcross` function as a sha-pinned VERBATIM SLICE (l217_tail.py lines
  245-258), which certifies both the crossing expression and that this run's
  permutation draw stream IS L216's and L217's.
- **CERT-AINF (HALTING)** — the per-draw A_inf null vector is obtained by
  calling the certified `side_stats_from` on the stored Perron vector, and is
  gated by asserting that the SAME call reproduces every stored A_inf field
  (including its percentiles) at float equality.
- Prior artifacts untouched: md5sum -c l230/prior.md5 GREEN before and after,
  plus (size, mtime_ns) fingerprints on l205/l209/l210/l216/l217 static.json.

## 5. Limitations (carried, plus new)

- ANATOMICAL leg only: wiring geometry, not an operating point (L164).
- Q1 and Q2 are DESCRIPTION (0a). Q3 is the only inferential object.
- Operator powers are walks WITH revisits, not paths.
- The two-term model is L216's, with a single rho per substrate x operator;
  a genuinely two-mode residual would show up as a residual failure, which is
  why PHASE_MODEL_INSUFFICIENT is registered first.
- The null is a membership permutation within the handedness class: it
  relocates the L/R labels of the same pool cells and holds the per-side
  counts exact. It cannot speak to pool MEMBERSHIP or to reconstruction
  completeness asymmetry.
- No neuromere column exists on BANC, so no legblock tier is possible.
