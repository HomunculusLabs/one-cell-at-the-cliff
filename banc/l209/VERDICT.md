# L209 VERDICT — does the handedness appear DEEPER?

Tick 238, 2026-11-22. Static, zero rollouts / zero settles / zero dynamics,
18 s CPU. PREREG: `l209/PREREG.md` (written and committed before any number).
Artifacts: `l209/static.json`, `l209/run.out`, `l209/run.err`.
Code: `l209_{build,tail}.py` -> generated `l209_static.py` (1,103 lines, four
verbatim certified source slices + one new tail).

## Branch: `D_NULL_RIGHTWARD` — the registered expectation, and it holds on all four Ti cells

Primary cell (Ti, f4wA, depth 2, beta operator, lam1-normalised):
`A_cell = -0.0638`, two-sided `pct_abs = 0.755` — INSIDE the membership
permutation null, sign NEGATIVE (right-heavy), i.e. "nothing deep, direction
continues depth 1". All four Ti depth x substrate cells land in the same
branch cell; `D_DEPTH_DISAGREE = False`. **The dominance flip stays
dynamics-owned** (L45b class) — now at depth 2 and 3, not just depth 1.

Predictions **4 of 4 correct** (Q209-1 branch, Q209-2 no-op, Q209-3 Crofts
sign agreement on Ti, Q209-4 paired delta inside its null at Ti d2-d3).

## The positive content: the Ti asymmetry DECAYS, it does not merely fail a bar

|A_cell| for Ti under the beta operator, by depth:

- cutwA: 0.0882 -> 0.0584 -> 0.0302  (per-hop ratios 0.662, 0.517)
- f4wA:  0.0957 -> 0.0638 -> 0.0323  (per-hop ratios 0.667, 0.506)
- two-sided percentile: 0.881 -> 0.728 -> 0.413 (cutwA);
  0.900 -> 0.755 -> 0.427 (f4wA)

The two substrates agree to three decimals in the RATIO while differing in
level, so the decay is a property of the operator's mixing and not of the
syn>=4 floor. Reading: the rightward side bias is a DIRECT-DRIVE (depth-1)
feature that the wiring actively homogenises with path length — roughly a
halving per hop. A deep static handedness is not merely absent, it is
*erased* by depth, which is a stronger statement than "inside the null".

## Unregistered and kept: the trochanter INVERTS with depth

Tr under the beta operator crosses zero and goes LEFT-heavy, monotonically:

- cutwA: -0.0162 -> +0.0314 -> +0.0728 (pct_abs 0.303 -> 0.563 -> 0.908)
- f4wA:  -0.0126 -> +0.0372 -> +0.0801 (pct_abs 0.226 -> 0.629 -> 0.929)

That is the direction the floored arms' dynamic L-dominance would want, and it
rises with depth — but it does NOT clear the registered 0.95 bar (max 0.929),
so it is reported as a direction and a trend, never as an established
asymmetry. Two further honesty legs cut against it:

1. **It is operator-dependent.** Under the required Crofts/Estrada second leg
   (`W/sqrt(s_i s_j)`), Tr stays NEGATIVE at every depth on both substrates
   (-0.0253 -> -0.0097 -> +0.0032 on f4wA). The strength normalisation removes
   the drift entirely. Ti, by contrast, agrees in sign across both operators at
   every depth (Q209-3) — so the one trend pointing the "useful" way is
   precisely the one that fails the second normalisation leg.
2. **The floor's deep nudge is statistically outside but substantively tiny.**
   The paired delta A_cell(f4wA) - A_cell(cutwA) on Tr is outside its paired
   null at depth 2 and 3 (pct_up 0.9895 / 0.9990) and in the LEFTWARD
   direction — but the delta is +0.0058 / +0.0073 against a null sd of ~0.003.
   The null is tight because the draws are shared and paired; a direction that
   clears a tight paired null is not a magnitude that can explain a 12-16/16
   seed dominance flip. Reported as a direction only (L175 law).

L205's C3 result is reproduced inside the same table as a control: the Ti
depth-1 paired delta is outside its null (pct_abs 0.983) in the wrong
direction, and by depth 3 it is inside (0.443).

## Registered no-op, measured

`A_cell` is a ratio and therefore invariant under global rescaling of the
operator. Measured: max relative difference between the unnormalised and the
lam1^d-normalised A_cell over all 24 depth x substrate x operator x joint
cells = **7.19e-14**. The lam1^d leg (the card's "primary normalisation")
therefore changes only the printed LEVELS, not the gate statistic or its
percentile — registered as a no-op before measuring, confirmed after. The
Crofts leg is the only normalisation that can move the answer, because it is a
per-edge reweighting, i.e. a different operator.

Spectral side-numbers: lam1(beta) = 227.779875 (cutwA) vs 200.510803 (f4wA) —
the syn>=4 floor costs the operator ~12% of its dominant growth; the f4wA
value is float-identical to the head's certified `LAM1_G1`.

## Depth-1 convention, disclosed not smoothed

The walk operator carries BETA_L on inhibitory edges; L205's in-mass did not.
Depth-1 therefore differs slightly between conventions, in the same direction
in all four cells: Ti -0.0882 (beta) vs -0.0897 (L205 raw) on cutwA, -0.0957
vs -0.0968 on f4wA; Tr -0.0162 vs -0.0155 and -0.0126 vs -0.0118. Same sign
everywhere, so the depth-1 anchor is unaffected by the convention.

## Verification

Four verbatim source slices + one bridge, forbidden-token audited, **no lab
module imported** (L175):

- CERT-HEAD1 `l151_static.py` 1-319 (sha256 e6245e8306dc8a0f — identical to the
  head sha L178/L205/L206/L207 recorded, asserted a literal PREFIX, so the
  whole L151/L142/L134/L92/L101 pin set re-ran free).
- CERT-HEAD2 `l178_tail.py` 7-149 (sha256 6e2e8fa4bd19eced) re-running CERT-F4
  in full (K4 73, carrier rank 21, twin gi 290, mass gap 2.44e-05, f4wA n
  21,789 / edges 469,618, family 33), the three stored gains at FLOAT EQUALITY,
  the CSR orientation (carrier out 69 / in 12) and all 20 pool sizes.
- MID `l206_mid.py` (sha256 febbc390ad4f).
- CERT-HEAD3 `l206_tail.py` 22-121 (sha256 29a830839ebc7837) carrying
  **CERT-178 HALTING = 420 stored anatomical values at FLOAT EQUALITY** (35
  actors x depths 1-3 x P/S/per-mass/PI — this is the card's required L178
  anchor, carrier depth-2 per-mass 0.0402 / twin 0.0798 / r2 0.503 included)
  and lam1(A_abs) = 30.179788 (rel spread 1.18e-16).
- CERT-HEAD4 `l207_tail.py` 26-146 (sha256 e3aa8d3d40b79326) re-running the
  gain-invariance assertions (lam1 rel 1.18e-16, depth-2 rel 1.31e-16) and
  **CERT-GEN (44 checks)**: the generic substrate builder / reach_sub /
  power_iter_sub reproduce the certified f4wA specialisation at float equality.
- **CERT-205 (new, HALTING)**: **250 stored L205 values reproduced by FLOAT
  EQUALITY** before any L209 number was read — 2 joints x 7 substrates x 17
  fields (M_L/M_R/m_L/m_R/A_tot/A_cell/M_fL/M_fR/M_eL/M_eR + three percentiles
  + four null moments) plus both paired `_delta_f4wA_minus_cutwA` dicts. This
  one gate certifies the RNG stream (seed 20526, draw order asserted ==
  L205's), the side convention, the pool membership AND the depth-1 anchor.
- Substrate pins asserted pre-read (f4wA 469,618 / f4 closure 472,095 /
  floor-eligible wA 469,256 / cutwA 644,177 / cutng25 644,084 / closure ==
  S92 edges_new; cutwA n 21,785 / f4wA n 21,789); all 20 pool sizes invariant
  on all seven L205 substrates with zero L/R overlap; every pool cell asserted
  present on both L209 substrates; all four power iterations asserted converged
  (rel spread <= 1.06e-08); GROUPS key ORDER asserted == L205's, because a
  different order would silently change the RNG stream.
- The build script also asserts the TAIL does not re-transcribe any certified
  function (`build_sub`, `reach_sub`, `power_iter_sub`, `reach`, `power_iter`).

## Limitations (as registered)

Anatomical leg only — wiring geometry, not an operating point (L164). Operator
powers are walks WITH revisits, not paths; the pool cells are themselves
reachable, so deeper arrivals include recurrent mass. `r_d = A^d 1` is
source-FREE (summed over all sources): it is the depth-d generalisation of
in-mass, not a per-actor reach. The null is a handedness
(membership-permutation) null, not a degree-preserving rewire null — the two
nulls' magnitudes are never swapped (L207's cross-null caution). No neuromere
column exists on BANC, so no legblock tier is possible.
