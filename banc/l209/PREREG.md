# L209 PREREG — does the handedness appear DEEPER?

Registered 2026-11-22, tick 238, BEFORE any L209 number was computed.
Static, zero rollouts, zero settles, zero dynamics. CPU.

## The question

L205 measured the Ti/Tr per-side **depth-1 in-mass** asymmetry and found the
L/R split INSIDE a membership-permutation null on both families (two-sided
percentile .877 base / .898 floored), pointing RIGHT (A_cell = −0.0897 cutwA /
−0.0968 f4wA, i.e. the LEFT pools carry ~18% LESS per cell) — the opposite of
the floored arms' dynamic L-dominance. Verdict then: the dominance flip is a
dynamics/attractor property, not depth-1 wiring.

This card asks the natural continuation: **is there a deeper static
handedness?** Per-side depth-2 and depth-3 walk mass arriving into the Ti/Tr
pools on cutwA vs f4wA, under the same 2000 shared membership draws.

## The statistic (registered in full)

Operator (orientation A[dst, src], the certified CSR convention):
`A = |W_beta|` with g = 1 — the ANATOMICAL linearized operator of L178/L206
(no row mask, no settle, no seed), built per substrate by L207's **certified
generic builder** `build_sub` (CERT-GEN).

Source-free arrival vector: `r_d = A^d 1`, i.e. `r_0 = 1`, `r_d = A r_{d-1}`.
`r_d[j]` = total mass of all length-d walks ending at cell j, summed over all
sources. `r_1` **is** the in-mass, so depth 1 is L205's row (up to the BETA_L
reweighting of inhibitory edges, see "the depth-1 anchor" below).

Per joint J ∈ {Ti, Tr}, with the pool cells and side labels taken from
`POOL_G[f"{J}_{{f,e}}{{L,R}}"]` exactly as L205 took them:

    M_L(d) = sum of r_d over the L flexor + L extensor pool cells
    M_R(d) = sum of r_d over the R flexor + R extensor pool cells
    A_cell(d) = (M_L/n_L − M_R/n_R) / (M_L/n_L + M_R/n_R)     [A > 0 = LEFT heavier]

## Normalisation legs (and a registered no-op)

- **PRIMARY: leading-eigenvalue division.** `A_hat = A / lam1(A)` by power
  iteration per substrate (convergence asserted, rel spread of last 6 < 1e-6),
  so the printed per-side LEVELS are comparable across depths instead of being
  dominated by the operator's own growth.
- **REGISTERED NO-OP, written before measuring:** `A_cell` is a RATIO, so it is
  invariant under any GLOBAL positive rescaling of the operator, including
  `lam1^d` and the gain g. The normalisation therefore cannot change the gate
  statistic or its percentile; it only rescales the reported levels. This is
  asserted numerically (unnormalised vs lam1-normalised A_cell agreeing to
  rel < 1e-10 at every depth/substrate/joint), never claimed in prose.
- **SECOND LEG (required by the card): Crofts/Estrada** `W/sqrt(s_i s_j)` with
  `s = s_out + s_in` per substrate, the same expression L206 used. This is a
  per-edge reweighting and therefore NOT a no-op — it is a genuinely different
  operator and is scored as its own leg (its own lam1, its own null percentiles).

## The null

The L205 membership-permutation null (L45b/L70 handedness class): per pool
group (J, f) and (J, e), permute the L/R labels among that group's cells
holding the per-side COUNTS exact; NDRAW = 2000, SEED_PERM = 20526, draws
constructed in L205's exact key order ((Ti,f), (Ti,e), (Tr,f), (Tr,e)) so the
stream is identical, and SHARED across substrates/depths/operators so every
paired delta is paired. `pct_up` = fraction of draws with null ≤ real;
`pct_abs` = fraction with |null| ≤ |real| (two-sided band).

## Halting gates (run BEFORE any L209 number is read)

1. **CERT-HEAD1..4** — four verbatim source slices (sha256 + literal-substring
   assert + forbidden-token audit, NO lab module imported, L175): l151_static.py
   1-319, l178_tail.py 7-149 (CERT-F4 + the three stored gains at float
   equality + the CSR orientation + all 20 pool sizes), the l206_mid bridge,
   l206_tail.py 22-121 (**CERT-178**: 420 stored anatomical values of L178 at
   FLOAT EQUALITY, 35 actors × depths 1-3 × P/S/per-mass/PI, plus reach() and
   lam1), l207_tail.py 26-146 (gain invariance + the generic builder +
   **CERT-GEN**: 44 checks that the generic machinery reproduces the certified
   f4wA specialisation exactly).
   This is what reproduces the card's required L178 anchor (carrier depth-2
   per-unit-out-mass 0.0402 / twin 0.0798, r2 0.503) before anything new.
2. **CERT-205 (new, HALTING)** — L205's stored handedness table reproduced by
   FLOAT EQUALITY from my own re-derived permutation draws: for both joints ×
   all 7 L205 substrates, the fields M_L, M_R, m_L, m_R, A_tot, A_cell,
   A_cell_pct_up, A_cell_pct_abs, A_tot_pct_up, null_A_cell_mean/p05/p95/sd,
   plus both paired `_delta_f4wA_minus_cutwA` dicts. This certifies the RNG
   stream, the side convention, the pool membership AND the depth-1 anchor in
   one gate. No L209 number may be read until it is green.
3. **Pool invariance re-asserted** on every substrate used (all 20 pool sizes
   == S92 pool_sizes, zero L/R overlap) — re-asserted, not assumed.

## The depth-1 anchor, stated honestly before measuring

L205's in-mass used `|vals_all| = log1p(syn)` with NO inhibitory BETA_L
scaling; the walk operator carries `|W_beta|` (inhibitory edges scaled by
BETA_L). Depth-1 of the walk table therefore need NOT equal L205's A_cell —
the two differ by exactly that reweighting. Both are reported in the depth-1
row (`A_cell_raw` = L205's convention, reproduced to float equality as gate 2;
`A_cell_beta` = the walk operator's own depth 1) and the difference is
disclosed as a convention difference, never smoothed over.

## Branch table — SIGN × BAND, four cells (the L205 method lesson)

Primary cell: **Ti, f4wA, depth 2, beta operator, lam1-normalised.**
Band: OUTSIDE = `pct_abs >= 0.95`; INSIDE otherwise. Sign: of `A_cell`.

- `D_DEEP_LEFT`   — OUTSIDE and A_cell > 0: a positive deep handedness pointing
  LEFT, i.e. the surprise this card was written to catch, and the sign that
  would match the floored arms' dynamic L-dominance.
- `D_DEEP_RIGHT`  — OUTSIDE and A_cell < 0: deep handedness in the SAME
  direction as L205's depth-1 rightward bias (static R, dynamic L — the
  dissociation deepens).
- `D_NULL_LEFTWARD`  — INSIDE and A_cell > 0: nothing deep, direction flipped
  relative to depth 1.
- `D_NULL_RIGHTWARD` — INSIDE and A_cell < 0: nothing deep, direction
  continues depth 1. **REGISTERED EXPECTATION** (the honest prior from L205:
  depth 1 showed nothing, so deeper reads should also show nothing and the
  dominance flip stays dynamics-owned).

Consistency flag `D_DEPTH_DISAGREE` is reported (not a branch) when depth 2 and
depth 3, or cutwA and f4wA, land in different cells.

## Predictions (scored after)

- **Q209-1**: branch = `D_NULL_RIGHTWARD`.
- **Q209-2**: the lam1 normalisation is a measured no-op for A_cell
  (max rel diff < 1e-10 over all depth × substrate × joint cells).
- **Q209-3**: the Crofts leg agrees in SIGN with the beta leg on Ti at depths
  2-3 on both substrates (L206 found Crofts agrees in order, differs in
  magnitude).
- **Q209-4**: the paired delta A_cell(f4wA) − A_cell(cutwA) at depths 2-3 stays
  inside its paired null (|pct| not extreme), i.e. the syn≥4 floor does not
  create a deep handedness either — unlike depth 1, where the paired delta
  was OUTSIDE its null in the wrong direction (L205 C3).

## Declared limitations

- ANATOMICAL leg only: wiring geometry, not an operating point (L164).
- Operator powers are walks WITH revisits, not paths; the pool cells are
  themselves reachable, so deeper arrivals include recurrent mass.
- The null is a HANDEDNESS (membership-permutation) null, not a degree-
  preserving rewire null — magnitudes from the two are never swapped (L207's
  cross-null caution).
- Depth-1 convention difference as stated above.
- No neuromere column exists on BANC, so no legblock tier is possible.
