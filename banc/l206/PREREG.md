# L206 PREREG — the avoidance LENGTH SCALE (static, zero rollouts)

Registered 2026-11-22 ~11:30 EST, tick 235, BEFORE any L206 value was read.
Card: LANE.md L206 (incl. the tick-233 field amendment, read in full).

## 0. What L178 left open

L178 (branch B_CARRIER_LOW) measured depths 1-3 only on the f4wA floor-4
substrate and found the carrier (gi 1110) BELOW every one of 100
degree-neutral relocations of its own edges at depth 2 AND depth 3
(anatomical leg: carrier 0.0402 per unit out-mass vs null median 0.336
[p05 0.210, p95 0.476], percentile 0.0). The open question: at what depth,
if any, does that reach CROSS the null band?

## 1. Substrate, operator, leg

- Substrate: f4wA (floor-4, carrier-present arm; n 21,789 / edges 469,618).
- PRIMARY LEG = ANATOMICAL (row mask a == 1), i.e. the pure
  A = |g_f4wA * W_beta| operator. Registered reason: it is the SEED-FREE
  leg, it is the leg L178's claim rests on (the gated carrier value is
  identically zero and only 19 of 303 pool cells are active), and the card
  names it ("anatomical leg, the seed-free one"). NO settle, NO rollouts,
  NO RNG beyond the pre-registered null draw seed.
- Walk sums: x_d = A^d e_c, pool reach P_d = sum over the 20 semantic motor
  pools (303 cells). Operator powers = walks with revisits, NOT simple
  paths (inherited L178 limitation, restated).
- Depth range 1..10 inclusive.
- Actors: carrier gi 1110, mass-matched twin gi 290, and the 33-cell ng
  family (ng4 ranks 23-55 present in f4wA) = 35 actors, exactly L178's set.

## 2. Normalisation (two legs, per tick-233 amendment (b))

- LEG N1 (PRIMARY, this card's originally registered one): divide the
  depth-d sum by lam1^d where lam1 = leading eigenvalue of A measured by
  POWER ITERATION and reported. Keeps depths comparable and is the only
  leg carrying the spectral-death diagnostic (branch iii).
- LEG N2 (FIELD, reported beside it, never instead): the Crofts/Estrada
  strength normalisation Ahat_ij = A_ij / sqrt(s_i * s_j) applied BEFORE
  the walk sum (s = total strength of the node; stated as our reading of
  the review's convention), with its own lam1 reported. Makes the number
  comparable to the communicability literature; has no spectral-death
  diagnostic, hence not primary.
- DECLARED COMPANION (not a new primary): the pool SHARE
  share_d = P_d / total_d where total_d = sum of x_d over ALL nodes. This
  is scale-free by construction and immune to spectral death; it is
  reported for every depth and actor so that a normalisation artefact
  cannot hide.
- Per-mass form: all cross-actor comparisons divide by the actor's own
  out-mass m_out (L178 convention; the null preserves out-mass exactly).

## 3. Gate cells (SEPARATE objects, L109 — never ANDed)

### G1 — the crossing depth (diffusion / communicability leg)

Statistic: carrier normalised per-mass pool reach vs the 100-draw null
band at the SAME depth, both under N1. Band = [p05, p95] of the null.

Branch table (SIGN x BAND = four cells, the L205 lesson applied):
- G1_NEVER        : carrier below p05 at every depth 1..10.
- G1_INTO_BAND    : first depth d* where carrier enters [p05, p95] and
                    stays inside at d*; avoidance is depth-limited, d* is
                    the number worth a draft sentence.
- G1_THROUGH_ABOVE: first depth d* where carrier exceeds p95 (crosses the
                    band from below to above) — over-reach, the opposite
                    sign of the depth-2/3 finding.
- G1_VACUOUS      : the comparison dies before any crossing because the
                    walk has converged to the leading eigenvector of A —
                    registered operationally as cos(x_d/|x_d|, v1) > 0.99,
                    past which every actor reports the SAME pool share by
                    construction and an actor-identity comparison is
                    uninformative. If this fires, the convergence depth
                    d_conv is the reportable number and no crossing claim
                    is made beyond it.
- G1_UNREGISTERED_SHAPE: anything else (deliberate catch-all; L205).

### G2 — SEARCH INFORMATION (routing leg, its OWN cell)

Per tick-233 amendment (c). Definitions as implemented, stated here:
- Weights normalised to (0,1] by Wn = A / A.max() (our implementation of
  the length transform's domain requirement; DISCLOSED as a choice).
- Length L_uv = -log10(Wn_uv) >= 0. Shortest paths computed on L
  (Dijkstra, hand-rolled: no scipy in this venv).
- Transition probability T_uv = A_uv / s_out(u).
- SI(c -> t) = -log2(prod T along the L-shortest path from c to t),
  accumulated DURING the Dijkstra relaxation along the L-shortest path
  (so it is the SI of the path the length metric selects).
- Reported per actor: min SI over the 303 pool cells, mean SI over
  reachable pool cells, n unreachable, and the L-distance of the chosen
  path. Compared carrier vs twin vs family median vs the SAME 100 null
  draws (amendment (e)).

Branch table:
- G2_SI_HIGH      : carrier SI (mean over reachable pool cells) at or
                    above the 95th percentile of the null = the route
                    exists but is HIDDEN (our avoidance claim in the
                    field's currency).
- G2_SI_LOW       : at or below the 5th percentile.
- G2_SI_INSIDE    : inside the null band.
- G2_UNREACHABLE  : the carrier cannot reach a majority (>50%) of pool
                    cells at all, in which case SI is undefined for them
                    and the cell reports reachability instead.
- G2_UNREGISTERED_SHAPE: catch-all.

NOTE, registered: the length transform is a REAL change of object. Our
depth is HOP COUNT; theirs is COST-weighted. A 3-synapse heavy route is
"short" to them and depth-3 to us. G1 and G2 therefore measure different
things on purpose.

### G3 — the registered expectation of DISAGREEMENT (descriptive, no bar)

Per amendment (d): on 1000 HCP subjects diffusion beat routing for
structure-function correspondence and navigation made it WORSE. We
register in advance that a G1/G2 DISAGREEMENT (e.g. low communicability
but ALSO low search information) is INFORMATIVE — it dates the carrier's
avoidance to a broadcast-vs-route level — and is NOT an instrument
failure. No bar, no pass/fail.

## 4. Null (amendment (e): unchanged)

The SAME 100 l169c degree-neutral destination swaps (seed 16943) L178
used, applied to the floor-4 block, both halves of each swap applied,
out-degree / out-weight multiset / every target's in-degree preserved.
Every added measure is reported against this null.

## 5. Certification BEFORE any L206 value is read

- CERT-HEAD1: head = l151_static.py lines 1-319 BYTE-FOR-BYTE
  (expected sha256 prefix e6245e8306dc8a0f, as recorded by L178 and L205).
- CERT-HEAD2: l178_tail.py lines 7-149 BYTE-FOR-BYTE — this re-runs
  CERT-F4 (K4 73, carrier rank 21, twin gi 290, mass gap 2.44e-05,
  jaccard 0.9231, closure 472,095, wA 469,256, f4wA n 21,789 /
  edges 469,618, family 33), the three stored gains at FLOAT EQUALITY,
  the CSR orientation check and all 20 pool sizes, as FREE certification.
- CERT-HEAD3: l178_tail.py lines 348-458 BYTE-FOR-BYTE — re-runs CERT-REW
  (l169c P6 reproduced exactly on the original cutwA block) and builds the
  floor-4 draws with the identical generator, plus the edge->CSR map.
- NO lab module is imported (L175: a lab run script is a SCRIPT, never a
  library). Slices are EXEC'd verbatim source, forbidden-token audited.
- CERT-178: the depth-1/2/3 anatomical census must reproduce L178's stored
  E_anatomical.all_actors for ALL 35 actors (P1/P2/P3abs, S1/S2/S3sgn,
  per-mass, PI) by FLOAT EQUALITY (==, not rounded) before any depth > 3
  is read. HALTING.
- CERT-NULL: my null operator construction must reproduce L178's stored
  Q2b_null_anatomical statistics (null_P2_med, p05, p95, q25, q75,
  null_P3_med, carrier_percentile_P2/P3) by FLOAT EQUALITY. HALTING.

## 6. Predictions (scored after)

- Q206-1: the walk converges to the leading eigenvector FAST on this
  recurrent operator, so G1_VACUOUS is the most likely branch and d_conv
  will be small (<= 6). Reason: dense recurrent cord graph, lam1 well
  separated.
- Q206-2: before convergence, the carrier's deficit SHRINKS with depth
  (the relative gap null_med/carrier narrows monotonically from depth 2),
  because mixing erases source identity.
- Q206-3: SI will NOT separate the carrier from the null (G2_SI_INSIDE) —
  a single cell's 69 out-edges barely move a global shortest-path
  geometry, and the carrier's avoidance is a MASS allocation effect, not a
  topological-distance effect.
- Q206-4: the Crofts leg (N2) will agree with N1 in ORDER (carrier below
  the family) but not in magnitude.

## 7. Scope / what this card does NOT do

- No rollouts, no settle, no dynamics. Nothing here is a claim about the
  dynamic phenotype; the operator is the L178 linearization's anatomical
  shell (L164: not an operating point).
- No draft edit (paper/ is in owner-handoff state).
- Reference candidates from amendment (f) are NOT folded into the draft
  here; they are recorded in the VERDICT for L174.
