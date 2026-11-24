# L217 VERDICT — the crossing phase, the three-operator sign table, and the
# source population that carries the leftward drift

Branch **Q1 = PHASE_DEGENERATE** (a declared, registered outcome, and the
reason it fired is the tick's first finding). Branch **Q4 = CORD_CARRIES**.
Predictions **3/5**. Registration NOT amended; one TOOLING fix made after the
PREREG and disclosed below; PREREG amendment 0a-i was written before the
generated script existed and before any number was measured.

Run: `l217_static.py` (1,718 lines, generated), 820 s, CPU, zero rollouts,
zero settles, zero dynamics.

-------------------------------------------------------------------------------
## 1. Q1 — the registered primary is UNSCOREABLE, and that is informative

Real crossing depths on f4wA beta are exactly the description the PREREG
stated in advance: d_cross(Ti) = 4.0761, d_cross(Tr) = 1.2522, one sign change
each. The registered inferential object was the NULL for their difference, and
the null cannot supply one:

  fraction of the 2000 handedness draws in which Ti crosses:  0.194
  fraction in which Tr crosses:                               0.271
  fraction in which BOTH cross (the usable pairs):            **0.051**

against the registered degeneracy bar of 0.25. The branch therefore fires
PHASE_DEGENERATE and NO D statistic is reported. This is the honest reading:
under the membership-permutation null a sign change is a RARE EVENT, so a null
built to test "when does it cross" spends 95% of its draws with nothing to
time. The instrument is wrong for the question, and the registered guard is
what said so rather than a number that would have looked fine.

**The transportable method lesson: a null that rarely produces the EVENT you
are timing cannot test its TIMING.** Register the event-existence RATE before
registering a timing contrast — had this card measured "does the series cross
at all" first, the degeneracy would have been visible before the timing
statistic was designed.

POST-HOC, clearly labelled as such and carrying no branch: the 0.051 both-cross
fraction is itself a candidate statistic — the real wiring produces a crossing
in both joints where only ~5% of label-permuted draws do. It is post-hoc,
derived from the degeneracy diagnostic itself, and is seeded as L232 with the
event-rate registered as PRIMARY rather than reported here as a result.

Descriptive crossing census over all 12 cells (substrate x operator x joint):
8 of 12 cross within d<=8 with exactly one sign change; the 4 censored cells
are cutwA crofts Ti, f4wA crofts Ti and both f4wA rw cells. Both cutwA crofts
series — genuinely unobserved when the PREREG was written — behave as the
amendment predicted: Tr crosses at 3.1915, Ti does not cross by d8, i.e. the
same Tr-before-Ti ordering the beta operator shows, three hops later.

-------------------------------------------------------------------------------
## 2. Q2 — the three-operator sign table, and a THIRD LEG THAT DOES NOT EXIST

  cutwA Ti   SPLIT                 beta +0.25698 (1.000) | crofts -0.00841 (0.178) | rw -0.16369 (0.889)
  cutwA Tr   SPLIT                 beta +0.40652 (1.000) | crofts +0.03922 (0.873) | rw +0.05408 (0.478)
  f4wA  Ti   THIRD_LEG_UNRESOLVED  beta +0.28663 (1.000) | crofts +0.13428 (0.994) | rw  (unresolved)
  f4wA  Tr   THIRD_LEG_UNRESOLVED  beta +0.44422 (1.000) | crofts +0.13146 (1.000) | rw  (unresolved)

P3 TRUE (SPLIT on cutwA Ti and cutwA Tr). The certified two-operator sub-table
is readable everywhere and says the opposite thing on the two substrates:
f4wA BOTH_AGREE on both joints (beta and Crofts both strongly positive), cutwA
SPLIT on both (Crofts inside its own null). Per the L216 amendment that SPLIT
is reported WITH the asymptote signs beside it and is NOT read as "operator-
dependent therefore not a wiring property": on cutwA the Crofts asymptote is
not of the opposite sign, it is indistinguishable from zero (Ti -0.0084 at
pct 0.178), which is a resolution statement about the operator, not a
disagreement about the wiring.

**The `rw` third leg could not be built on f4wA, and the reason is structural,
not computational.** The source-normalised random walk T_pq = W_pq/s_p is
(near-)stochastic, so lam1 ~ 1 and the subdominant eigenvalue sits directly
beneath it. Escalating the power-iteration budget 400 -> 3200 -> 25600 ->
102400 (a factor of 256) moved the eigenvalue not at all and moved the
eigenpair residual not at all:

  iters    400:  lam1_R 0.999902344   residual_R 6.782e-03
  iters   3200:  lam1_R 0.999900003   residual_R 6.781e-03
  iters  25600:  lam1_R 0.999900003   residual_R 6.781e-03
  iters 102400:  lam1_R 0.999900003   residual_R 6.781e-03

A converged eigenvalue with a stuck residual is a stable 2-cycle of the
normalised map, i.e. a dominant spectrum that is not simple — on f4wA the
source-normalised walk has (at least) a +lam/-lam pair, so it has NO unique
asymptotic arrival distribution and A_inf is not a quantity this card is
entitled to read. The iterate's A_inf reads exactly +1.000000 / -1.000000,
the signature of total localisation onto one side, and it is recorded in the
json as unresolved rather than reported as a measurement. cutwA's rw operator
IS resolved (residual 4.3e-06 / 1.2e-05 at 400 iterations) and contributes
normally, which is what makes the f4wA failure a statement about f4wA rather
than about the code.

**The transportable method lesson: diagnose an eigenpair with its RESIDUAL,
never with the iteration's convergence SPREAD.** The spread for f4wA rw read
2.00e-04 and looked like an ordinary nearly-converged iteration; the residual
read 6.78e-03 and was the only thing that distinguished "needs more iterations"
from "this operator has no Perron vector". The spread proxy would have passed
a laxer bar and published +1.000000 as an asymptote.

TOOLING FIX, disclosed, made after the PREREG and changing no registered
quantity: the inherited `rel_spread < 1e-6` convergence assert is calibrated to
the beta operators (which converge to 1e-16) and is a statement about the
iteration budget, not the operator. It was replaced by the direct Perron
residual with a bar DERIVED from what the claim needs (A_inf is a ratio of sums
of v1 entries, so a relative eigenvector error eps perturbs A_inf by O(eps),
and the claims are signs plus 0.95 percentiles against nulls of half-width
0.05-0.12, so 1e-3 is three orders of margin). Calibration reference printed
in the same run: beta 1.3e-16 / 1.4e-16, Crofts 3.7e-09 / 2.8e-05. This is the
same class of fix as L216's derived convergence bar, one level deeper.

P2 is scored FALSE by the registered rule and reported as an INSTRUMENT
FAILURE, not as a sign disagreement — the f4wA rw asymptote does not exist.

-------------------------------------------------------------------------------
## 3. Q3 — the mechanism leg: NO source population carries the drift

The decomposition is exact (sum_g A^d 1_g == A^d 1 to max rel 2.58e-15 over
every partition and every decomposed depth; `arrivals_from` is certified
ARRAY-IDENTICAL to the certified `arrivals` at x0 = 1 across 16 depth vectors).

f4wA, beta, drift share vs MASS share, and each group's OWN A_cell:

  Ti d8  (total A_cell +0.10418)
    vnc_intrinsic  drift .809  mass .761   A +0.1108
    descending     drift .122  mass .108   A +0.1169
    sensory        drift .068  mass .130   A +0.0549
    motor          drift .001  mass .001   A +0.1012
  Tr d8  (total A_cell +0.24487)
    vnc_intrinsic  drift .773  mass .758   A +0.2495
    descending     drift .125  mass .114   A +0.2696
    sensory        drift .102  mass .127   A +0.1956
    motor          drift .001  mass .001   A +0.1786
  NT sign, Ti d8: I drift .681 mass .699 A +0.1016 | E drift .319 mass .301 A +0.1102
  NT sign, Tr d8: I drift .692 mass .699 A +0.2424 | E drift .308 mass .301 A +0.2505

**Every group's share of the drift tracks its share of the MASS, and every
group's own asymmetry is close to the total.** Excitatory and inhibitory
sources are indistinguishable (A +0.110 vs +0.102 at Ti, +0.251 vs +0.242 at
Tr, against drift shares that match their mass shares to within 0.02). The
card's mechanism hypothesis — that some identifiable population carries the
leftward drift — is REFUTED BY HOMOGENEITY: the asymmetry is the same wherever
the walk starts, so it is a property of the pools' own in-wiring geometry at
the destination, not of any source class.

The single real differentiation in the table: SENSORY sources are the
consistently weakest carrier and the only group whose drift share sits well
BELOW its mass share — .068 drift on .130 mass at Ti d8, with its own A_cell
+0.0549, barely half the total +0.1042. Reported as the one asymmetric row,
descriptive, no branch.

**Method note worth keeping: report each group's OWN A_cell beside its share.**
The share column alone cannot distinguish "this group carries the effect" from
"this group is simply big"; the per-group asymmetry column is what turns a
share table into the homogeneity statement that is the actual result.

-------------------------------------------------------------------------------
## 4. Q4 — CORD_CARRIES, and it carries essentially all of it

  Ti: A_cell(cord-only sources, d8) +0.10263 vs all-sources +0.10418, ratio 0.9852
  Tr: A_cell(cord-only sources, d8) +0.24171 vs all-sources +0.24487, ratio 0.9871

Same sign on both joints and both ratios ~0.99 against a 0.5 bar. P4 TRUE
(the cord carries 0.9165 of the drift at d=2 against a >0.5 bar) and P5 TRUE.
The descending shell is 10.8-11.4% of the arrival mass and contributes a
proportional 12.2-12.5% of the drift: the left-heavy asymptote is a
CORD-INTRINSIC property of the female BANC wiring and does not need the
descending input to exist. Consistent with, and strengthening, L65's finding
that the real female cord subnet self-orders antagonist structure without
descending drive.

-------------------------------------------------------------------------------
## 5. Predictions

  P1 FALSE  — PHASE_DEGENERATE, not PHASE_SEPARATED (the null, not the effect)
  P2 FALSE  — unscoreable: the f4wA rw asymptote does not exist (instrument)
  P3 TRUE   — SPLIT on cutwA|Ti and cutwA|Tr
  P4 TRUE   — cord drift share at d2 = 0.9165 > 0.5
  P5 TRUE   — CORD_CARRIES

Both failures are instrument failures caught by registered guards, which is
the outcome a PREREG is for. Neither is a wiring claim that went the other way.

-------------------------------------------------------------------------------
## 6. Certification

  **884 HALTING FLOAT EQUALITIES before any L217 number was read**:
    CERT-205  250  (free, inside the verbatim L209 slice)
    CERT-GAP   10  (free, inside the verbatim L216 slice)
    CERT-209  412  (free, inside the verbatim L216 slice)
    CERT-216  212  (this card's own required anchor: 8 cells x 8 depths of
                    A_cell + 8 x 17 A_inf fields + 4 operator-substrate pairs
                    x lam1/lam2/gap)
  plus CERT-178 420 and CERT-GEN 44 re-running free inside the verbatim heads.

  CERT-SEED  16 depth vectors, np.array_equal: `arrivals_from(x0=1)` is
             ARRAY-IDENTICAL to the certified `arrivals()` on both substrates
             before any decomposition was read (L44).
  ADDITIVITY max rel 2.58e-15 over every partition x depth (halting).
  rw_in d=1 identity EXACT (3.77e-15 cutwA / 4.88e-15 f4wA) over 20,887 and
             20,043 in-mass-positive nodes (halting) — the theorem that
             justifies excluding the card's literal third operator.
  NO-OP      lam1^d normalisation re-measured as a no-op for beta/Crofts
             (7.19e-14, free in the slice) and for rw (4.96e-14).
  PERRON RESIDUAL gate on all six claim-bearing operator/substrate pairs.
  l209/l210/l216 static.json opened READ-ONLY, (size, mtime_ns) fingerprinted
             before and asserted unchanged after; md5 prior list taken before
             the run (l217/prior.md5).

  TEN VERBATIM SOURCE SLICES, forbidden-token audited, no lab module imported
  (L175), with SIX INHERITED sha pins asserted by the BUILDER plus a SEVENTH
  parent pin: l216_tail.py's whole-file sha256 must equal the TAIL sha that
  l216_static.py's own generated banner recorded, so slicing a parent that has
  moved since it produced l216/static.json HALTS the build. The CERT-216M
  slice (l216_tail.py 1-204) is cut at the end of the parent's measurement
  block so every parent gate re-runs for free while the parent's own
  fits/verdict/writer block is excluded — asserted positively (CERT-GAP,
  CERT-209, pi_sub, gap_sub, PERRON, GAPS present) and negatively
  (o["branch"], o["fits"], o["predictions"], fit_exp, os.makedirs absent).
  Generated sha256 44799852a17f3fc4.

-------------------------------------------------------------------------------
## 7. What this licenses, and what it does not

LICENSED: the left-heavy asymptotic arrival asymmetry of the anatomical
operator on the BANC female cord is (a) cord-intrinsic — reproduced to ~99% by
cord-origin walks alone, (b) source-homogeneous — no super_class and neither NT
sign carries it beyond its mass share, (c) a destination-geometry property, and
(d) present on both substrates under both certified operators on f4wA, with the
Crofts resolution failing on cutwA rather than disagreeing.

NOT LICENSED: any statement about WHEN each joint crosses relative to the other
(the null cannot time a rare event), and any statement about the
source-normalised random walk's asymptote on f4wA (that operator has no Perron
vector). Both are named, both are seeded as follow-ons, neither is reported as
a number.
