# L217 PREREG — the crossing phase, the three-operator sign table, and the
# source population that carries the leftward drift

Registered BEFORE l217_static.py was built or run. Static, zero rollouts,
zero settles, zero dynamics. Substrates cutwA and f4wA, joints Ti and Tr.

-------------------------------------------------------------------------------
## 0. PREMISE RE-POSING (the L216 amendment, carried out explicitly)

The card as originally written asks whether the "Tr DEEP INVERSION" is real and
whether the Crofts operator "erases" it. L216 (tick 246) refuted that premise
with the same machinery: extended to depth 8, BOTH joints invert and both beta
asymptotes sit at percentile 1.000 of the handedness null (f4wA beta Ti A_inf
+0.28663, Tr +0.44422). So the depth-2/3 Ti/Tr dissociation L209 saw is a
difference in CROSSING PHASE on a shared left-heavy Perron mode, not a
difference in kind. The LANE.md item carries that amendment and instructs:
re-pose the primary as WHEN each joint crosses, not WHETHER Tr is special.

Three further premise corrections are registered here, before measuring.

### 0a. The card's literal third operator is DEGENERATE for this readout

The card names the third leg "the random-walk form W/s_in". Our operator
convention is A[dst, src] (L209's `arrivals`: `y[rows] += v * x[cols]`), so
dividing every edge by the IN-strength of its TARGET makes A ROW-stochastic.
The readout is r_d = A^d 1. For a row-stochastic A, r_1 = 1 on every node with
nonzero in-mass, and therefore r_d = 1 for all d: the statistic is CONSTANT in
depth and A_cell(d) is the same number at every depth by construction. That is
not a weak leg, it is a provable no-op, and it cannot carry a sign table.

REGISTERED: measure it rather than assert it. `rw_in` is built, and a HALTING
assert requires max |r_d - 1| over in-mass-positive nodes < 1e-10 at every
depth 1..8. If that assert passes, `rw_in` is reported as a MEASURED
DEGENERACY and is excluded from the sign table with its reason recorded.

[AMENDMENT 0a-i, written BEFORE l217_static.py was built and before ANY number
was measured, disclosed as an amendment rather than silently applied. The
paragraph above overstates what is provable. r_1 = 1 on every in-mass-positive
node is a theorem (each row of A sums to exactly 1). At d >= 2 that is NOT
exact: a node whose own in-mass is zero contributes r_1 = 0, so mass leaks out
of the recursion through zero-in-degree sources and r_d < 1 downstream of them
by an amount that is a statement about the substrate's SOURCE NODES, not about
wiring asymmetry. Registered instead: the d=1 identity is HALTING (max |r_1 -
1| over in-mass-positive nodes < 1e-10); the d >= 2 deviation is MEASURED and
reported with the zero-in-degree node count; and `rw_in` is excluded from the
sign table EITHER WAY, because under it A_cell(d) measures zero-in-degree
leakage rather than the quantity the sign table is about. The exclusion is
therefore not contingent on the measurement.]

The non-degenerate random-walk form, and the one the field actually uses, is
the SOURCE-normalised transition matrix T_pq = W_pq / s_p (Seguin, Sporns &
Zalesky 2023 / Seguin et al. 2022, digested at tick 233 as the search-
information transition matrix). Under A[dst, src] that is division by the
OUT-strength of the SOURCE, i.e. column-stochastic, and r_d = A^d 1 is then the
forward-diffused mass of a unit started at every node — a genuine, non-constant
depth profile. REGISTERED: `rw` (source-normalised) is the third operator leg.
Nodes with zero out-mass keep a zero column (no self-loop is invented); the
resulting lam1 is reported, not assumed to be 1.

### 0b. Observation status (Kriegeskorte 2009; the L214 rule)

While scoping this card I read l216/static.json, which stores A_cell(d) for
d=1..8 for all eight beta/Crofts cells. The crossing depths of those eight
series are therefore OBSERVED-DERIVABLE and are stated here in full, as
DESCRIPTION, before any new number is read:

  f4wA  beta   Ti: -.09569 -.06382 -.03228 -.00226 +.02741 +.05519 +.08083 +.10418  -> crosses between d4 and d5
  f4wA  beta   Tr: -.01257 +.03725 +.08014 +.11961 +.15567 +.18851 +.21822 +.24487  -> crosses between d1 and d2
  f4wA  crofts Ti: -.05601 -.04706 -.04223 -.03564 -.03095 -.02624 -.02228 -.01868  -> does NOT cross by d8
  f4wA  crofts Tr: -.02533 -.00971 +.00316 +.01157 +.01942 +.02532 +.03045 +.03455  -> crosses between d2 and d3
  cutwA beta   Ti: -.08819 -.05840 -.03021 -.00310 +.02368 +.04858 +.07145 +.09220  -> crosses between d4 and d5
  cutwA beta   Tr: -.01620 +.03143 +.07282 +.10983 +.14321 +.17325 +.20018 +.22420  -> crosses between d1 and d2
  (the two cutwA crofts series were NOT inspected and are genuinely unobserved)

CONSEQUENCE, registered: the d_cross POINT ESTIMATES on the beta and Crofts
operators are DESCRIPTION, not evidence. Registration cannot buy inference on
a quantity already derivable from a stored artifact. What IS unobserved, and
what this card's branches are therefore placed on, is:

  (i)   the NULL distribution of d_cross and of the Ti-minus-Tr crossing gap
        (never computed on any card);
  (ii)  the entire `rw` operator leg (never built);
  (iii) the SOURCE decomposition of the arrival mass (never computed);
  (iv)  the cord-restricted drift (never computed);
  (v)   the two cutwA crofts series.

Branches below fire ONLY on (i)-(v). Every observed-derivable quantity is
labelled `description=true` in the output json.

### 0c. What the asymptote leg can and cannot say

A_inf is read off the RIGHT Perron vector and does not decompose by source
(the Perron vector is a fixed point, not a walk from an origin). The source
decomposition is therefore performed on A_cell(d) at d in {2, 3, 8}, with d=8
standing in as the near-asymptotic probe and the pre-asymptotic residue
|A_cell(8) - A_inf| reported beside every d=8 number. No claim is made that
the d=8 decomposition IS the asymptotic decomposition.

-------------------------------------------------------------------------------
## 1. Substrates, operators, pools, null

Substrates: cutwA (21,785 nodes / 644,177 edges) and f4wA (21,789 / 469,618),
built by the certified generic builder. Operators per substrate:

  beta   = |log1p(syn)*sign| with BETA_L applied to inhibitory edges (g=1)
  crofts = beta / sqrt(s_tot(src) * s_tot(dst))        (Crofts/Estrada)
  rw     = beta / s_out(src)                            (Seguin T_pq = W_pq/s_p)
  rw_in  = beta / s_in(dst)                             (the card's literal
                                                         form; degeneracy probe)

Each operator gets its own lam1 by the certified power iteration, and
`arrivals` is always run on A/lam1 (L209's no-op-verified normalisation).

Pools: Ti and Tr flexor/extensor, per side, L205 membership, invariant across
substrates. Null: the SHARED membership permutation draws (NDRAW 2000, seed
20526, L205's stream), per-side counts held exact. Every null A_cell series is
read from the SAME draw index across depths, so a null draw has a coherent
depth profile and therefore its own crossing depth.

-------------------------------------------------------------------------------
## 2. d_cross: definition, fixed in advance

Given A_cell(1..8) for a cell, let the LAST sign change be between depths d and
d+1 (A(d) and A(d+1) strictly opposite in sign). Then

    d_cross = d + |A(d)| / (|A(d)| + |A(d+1)|)

(linear interpolation of the zero on the straight segment). If there is no sign
change in 1..8, d_cross is CENSORED (None) and the cell is recorded as
sign-constant with its constant sign. The number of sign changes is recorded.
"Last" rather than "first" is registered because the object of interest is
arrival INTO the asymptotic sign, and a series may wobble early.

-------------------------------------------------------------------------------
## 3. Registered questions, gates and branches (each a SEPARATE cell, L109 —
   never ANDed into one verdict)

### Q1 PRIMARY — is the Ti/Tr crossing-phase gap bigger than the handedness
null allows? (substrate f4wA, operator beta)

  D_real = d_cross(Ti) - d_cross(Tr), both real series.
  Null: for each of the 2000 draws j, compute d_cross from the null series
  nA_cell[j, 1..8] for Ti and for Tr (paired by draw index j), take
  D_null[j] = d_cross_Ti[j] - d_cross_Tr[j] over draws where BOTH cross.
  pct_abs = fraction of usable draws with |D_null| <= |D_real|.

  BRANCH (primary cell only):
    PHASE_SEPARATED   if |D_real| >= 1.0 AND pct_abs >= 0.95
    PHASE_NULL        if pct_abs < 0.95
    PHASE_DEGENERATE  if fewer than 25% of draws cross (null uninformative)
                      or either real series is censored
  Registered in advance: PHASE_DEGENERATE is a real outcome, not a failure, and
  it is reported as "the instrument cannot see this" rather than as a null.

### Q2 — the three-operator SIGN table

For each substrate x joint, the signs of A_inf under {beta, crofts, rw}, each
with its own pct_abs against the SAME draws and the 0.95 bar.

  ALL_THREE_AGREE    all three same sign AND all three pct_abs >= 0.95
  ALL_THREE_INSIDE   all three pct_abs < 0.95
  SPLIT              anything else

Registered in advance, per the L216 amendment: 2-of-3 agreement is NOT a pass,
and SPLIT may NOT be read as "operator-dependent and therefore not a wiring
property" without stating the asymptote SIGNS; an operator that agrees in sign
while failing the percentile bar is reported as a weak agreement, never as a
disagreement. The same table is also reported at d=2 and d=3 (the L209 object)
as DESCRIPTION for beta/crofts and as evidence for rw only.

### Q3 — which SOURCE population carries the leftward drift?

The decomposition is exact and linear: for a partition {g} of the substrate's
nodes, r_d^(g) = A^d 1_g and sum_g r_d^(g) = r_d identically. A HALTING assert
requires that additivity to rel < 1e-10 at every depth used.

  Partition A: source super_class (sensory / ventral_nerve_cord_intrinsic /
               motor / descending / other), from the BANC annotations.
  Partition B: source effective NT sign (E = sign>0 and not glutamate;
               I = sign<0 or glutamate; U = unlabelled).
  Partition C: cord (cord_mask) vs non-cord (the descending shell).

  Per group: dcell_g = M_L^(g)/n_L - M_R^(g)/n_R, and share_g = dcell_g /
  sum_g dcell_g. Reported at d in {2, 3, 8}, substrate f4wA, operator beta,
  both joints. DESCRIPTIVE — no branch — except Q4 below.

### Q4 — does the drift survive restricting sources to the cord?

  CORD_CARRIES    if sign(A_cell_cord(8)) == sign(A_cell_all(8)) for BOTH
                  joints AND |A_cell_cord(8)| >= 0.5 * |A_cell_all(8)| for both
  CORD_PARTIAL    if the signs match for both joints but the magnitude bar
                  fails on at least one
  CORD_FAILS      if the sign differs on at least one joint

  (f4wA, beta. A_cell_cord(d) is computed from the cord-only source indicator,
  i.e. the same exact decomposition restricted to one group.)

### Q5 — HALTING instrument gates, run BEFORE any L217 number is read

  CERT-205  (free, inside the verbatim L209 slice) — L205's 2 joints x 7
            substrates x 17 fields + 2 paired deltas at float equality.
  CERT-GAP  (free, inside the verbatim L216 slice) — L210's lam2/gap/lam1 and
            six growth factors at float equality.
  CERT-209  (free, inside the verbatim L216 slice) — 412 stored L209 values.
  CERT-216  (NEW, this card's own required anchor) — every stored
            l216/static.json A_cell (8 cells x 8 depths), every stored A_inf
            (8 cells x 17 fields) and every stored gap (4 operator-substrate
            pairs x lam1/lam2/gap) reproduced at FLOAT EQUALITY.
  Additivity assert (Q3) and the rw_in degeneracy assert (0a) are halting.
  Pool invariance across substrates is re-asserted (free, in the slice).

-------------------------------------------------------------------------------
## 4. Predictions (scored, registration not amended afterwards)

  P1. Q1 lands on PHASE_SEPARATED.
  P2. The `rw` (source-normalised) operator gives A_inf of the SAME SIGN as
      beta on f4wA for both joints (i.e. the left-heavy asymptote is not an
      artifact of the unnormalised edge weights).
  P3. Q2 lands on SPLIT for at least one of the four substrate x joint cells
      (driven by cutwA crofts Ti, whose A_inf L216 measured inside the null).
  P4. In Partition C, the CORD group carries more than 50% of dcell at d=2 on
      f4wA beta Ti (the cord is the bulk of the substrate).
  P5. Q4 lands on CORD_CARRIES.

-------------------------------------------------------------------------------
## 5. Limitations, registered in advance

  - ANATOMICAL leg only: wiring geometry, not an operating point (L164).
  - Operator powers are walks WITH revisits, not paths.
  - r_d = A^d 1 is the depth-d generalisation of in-mass, not a per-actor reach.
  - The source decomposition attributes a walk to its ORIGIN, not to its last
    hop; a cord-origin walk may traverse descending cells and vice versa.
  - `rw` normalises by out-strength, so it DOWN-weights hub sources by
    construction; a sign agreement with beta is therefore informative, a
    magnitude comparison between operators is not.
  - d=8 is a near-asymptotic probe, not the asymptote (0c).
  - The d_cross point estimates for beta/crofts are description (0b).
  - No neuromere column exists on BANC, so no legblock tier is possible.
