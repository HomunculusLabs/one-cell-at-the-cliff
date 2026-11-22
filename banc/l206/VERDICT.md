# L206 VERDICT — the avoidance LENGTH SCALE

Run 2026-11-22 (tick 235). PREREG `l206/PREREG.md` registered first.
Artifacts: `l206/{PREREG.md, static.json, run.out, run.err}`.
Code: `l206_{build,mid,tail}.py` -> generated `l206_static.py`.
Zero rollouts, zero settles, zero dynamics, zero RNG outside the
pre-registered null seed 16943. 23 s of compute, CPU only.

## Branches

- **G1 (diffusion / communicability) = `G1_NEVER`.** The carrier's
  lam1-normalised per-mass pool reach is BELOW the null's 5th percentile at
  EVERY depth 1..10 — percentile **0.0 at all ten depths**, 100 draws each.
  No crossing depth exists within 10 hops.
- **G2 (routing / search information) = `G2_SI_HIGH`, percentile 100.0.**
  Carrier SI into the motor pools **22.393 bits** vs null median 18.718
  [p05 17.080, p95 20.624]: all 100 degree-neutral draws are LOWER. The
  route is not missing — **303 of 303 pool cells are reachable** from the
  carrier and the null median reach is also 303 — it is HIDDEN.
- **G3 (registered expectation of disagreement) = AGREE.** Diffusion says
  avoidance (pct 0.0) and routing says avoidance (pct 100.0). The
  registered disagreement did NOT materialise; the two levels confirm each
  other instead of dating the effect.

## The number the card asked for, and the better one it found

The card asked for d*. There is none. What replaces it:

| depth | carrier | null p05 | null med | null p95 | pct | carrier share | null share med | cos(x_d,v1) |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.000e+00 | 8.79e-05 | 2.71e-04 | 5.77e-04 | 0.0 | 0.00000 | 0.05443 | 0.0039 |
| 2 | 4.409e-05 | 2.31e-04 | 3.69e-04 | 5.22e-04 | 0.0 | 0.01651 | 0.09960 | 0.0362 |
| 3 | 5.718e-05 | 3.07e-04 | 4.37e-04 | 5.98e-04 | 0.0 | 0.04620 | 0.13398 | 0.1255 |
| 4 | 4.588e-05 | 3.17e-04 | 4.49e-04 | 6.28e-04 | 0.0 | 0.07204 | 0.14936 | 0.2928 |
| 5 | 4.398e-05 | 3.11e-04 | 4.37e-04 | 6.20e-04 | 0.0 | 0.10497 | 0.15527 | 0.5844 |
| 6 | 4.268e-05 | 3.05e-04 | 4.27e-04 | 6.01e-04 | 0.0 | 0.13095 | 0.15673 | 0.8137 |
| 7 | 4.128e-05 | 2.98e-04 | 4.19e-04 | 6.08e-04 | 0.0 | 0.14556 | 0.15742 | 0.9043 |
| 8 | 4.005e-05 | 2.92e-04 | 4.12e-04 | 5.95e-04 | 0.0 | 0.15274 | 0.15742 | 0.9374 |
| 9 | 3.899e-05 | 2.87e-04 | 4.04e-04 | 5.91e-04 | 0.0 | 0.15589 | 0.15737 | 0.9540 |
| 10 | 3.808e-05 | 2.82e-04 | 3.96e-04 | 5.86e-04 | 0.0 | 0.15714 | 0.15721 | 0.9649 |

Deficit ratio (null median / carrier) by depth:
na, 8.38, 7.64, 9.78, 9.94, 10.00, 10.16, 10.28, 10.36, **10.39** — it does
not shrink; it rises and flattens toward a **depth-invariant ~10.4x**.

**THE MECHANISM, and it is the result.** The carrier's pool SHARE
(fraction of its whole broadcast landing in the 303 motor-pool cells)
converges to **0.15714 at depth 10, against the null's 0.15721 and the
33-cell family's 0.15721** — indistinguishable to four decimals. So by
depth ~9-10 the carrier's influence is distributed EXACTLY like everyone
else's; what stays ~10x smaller is the AMPLITUDE of its projection onto
the operator's dominant mode (lam1 = 30.180, power iteration, rel spread
of the last six iterates 1.2e-16). The avoidance is therefore **not a
path-length phenomenon at all**: it is a reduced coefficient on the
dominant mode, global and depth-invariant, and it cannot be rescued by
allowing longer loops. Draft sentence licensed: *the identity cliff is
not a feedforward drive of the readout at ANY path length up to 10 hops.*

Carrier rank among the 35 ng actors by per-mass pool reach: **33 of 35 at
every depth 2..10** (stable), 13 of 35 at depth 1 (where 22 actors tie at
exactly zero — disclosed, the depth-1 rank is a tie artifact).

## Search information, in the field's currency

- carrier 22.393 bits (min 10.377, median 21.459, mean L-distance 1.490)
- twin gi 290 20.202 bits (min 6.908, mean L-distance 1.392)
- family median 20.270 (range 15.305 - 24.578); carrier rank 32 of 35
- null median 18.718, p05 17.080, p95 20.624, 100/100 draws below the
  carrier, null median reach 303/303

+3.675 bits over the null median = the route is ~12.8x less likely to be
found by a walker following the transition probabilities. Because the
destination swaps move targets but leave every weight with its SOURCE, the
null preserves the carrier's out-strength EXACTLY — so the SI excess
cannot be an out-strength artifact. Field-legible sentence, both halves
now measured: **the carrier has low communicability AND high search
information into the motor pools at matched out-mass.**

## N2 — the Crofts/Estrada leg (tick-233 amendment (b))

lam1(Ahat) = 0.388120. Depth-2: carrier 0.017987 vs twin 0.032690 vs
family median 0.095370; carrier rank 32 of 35. The field normalisation
AGREES with N1 in ordering (carrier near the bottom of the family) and
differs in magnitude, exactly as registered. No null on this leg
(disclosed in static.json): the swaps are out-strength-neutral but not
total-strength-neutral under sqrt(s_i s_j), so a Crofts null would not be
the registered null — ordering check only.

## Predictions: 1 of 4

- Q206-1 **WRONG**: `G1_VACUOUS` did not fire. The carrier's walk reaches
  only cos 0.9649 with v1 by depth 10 (bar 0.99); only 12 of 35 actors
  converge within 10 hops (earliest fam12_549 and fam22_1022 at d 5).
- Q206-2 **WRONG, and in the opposite direction**: the deficit does not
  shrink with depth, it GROWS from 8.38 to 10.39 and flattens.
- Q206-3 **WRONG, strongly**: SI separates the carrier at percentile
  100.0, not inside the null. I predicted a single cell's 69 out-edges
  could not move a global shortest-path geometry; they can, because the
  statistic is about which neighbourhood the 69 edges LAND in, not about
  how much mass they carry.
- Q206-4 **CORRECT**: the Crofts leg agrees in order (rank 32 of 35).

## Honesty / limitations

1. The json's `deficit_ratio_tail_spread` = 0.0 is a ONE-ELEMENT artifact:
   with d_conv undefined the "tail" is depth 10 alone. The real evidence
   for depth-invariance is the sequence 10.00 / 10.16 / 10.28 / 10.36 /
   10.39 over depths 5-10 — rising and flattening, not a measured
   asymptote. Stated as a trend, never as a converged limit.
2. My registered convergence diagnostic (cos > 0.99) was too strict for
   the statistic that actually saturates: the pool SHARE is at the null's
   value by depth 9 while cos is still 0.954. The depth-resolved question
   dies in the SHARE currency well before the registered bar fires — a
   prereg instrument mismatch, disclosed, and the amplitude statistic
   stays informative throughout.
3. ANATOMICAL leg only (no row mask, no settle): this is the wiring's walk
   geometry, not an operating point (L164). Operator powers are walks WITH
   revisits, not simple paths (inherited L178 limitation).
4. The null is a GEOMETRY null (degree-neutral destination swaps of the
   carrier's own edges, both halves applied), not a re-settled dynamics
   null.
5. SI implementation choices, disclosed: L = -log10(A/A_max) with
   A_max = 2.0566 (domain choice); ties in L broken by heap order; SI
   accumulated along the L-selected path during relaxation.
6. lam1 = 30.18 means raw depth-10 sums are ~30^10 larger than depth-1 —
   the lam1^d normalisation is load-bearing, and the scale-free pool share
   is reported beside it so a normalisation artifact cannot hide.

## Certification (all ran BEFORE any L206 value was read)

- CERT-HEAD1: `l151_static.py` lines 1-319 byte-for-byte, sha256
  `e6245e8306dc8a0f...` — identical to the head sha L178 and L205 recorded.
- CERT-HEAD2: `l178_tail.py` lines 7-149 byte-for-byte (sha256
  `6e2e8fa4bd19eced`): CERT-F4 re-ran in full (K4 73, carrier rank 21, twin
  gi 290, mass gap 2.44e-05, jaccard 0.9231, closure 472,095, wA 469,256,
  f4wA n 21,789 / edges 469,618, family 33), the three stored gains at
  FLOAT EQUALITY, the CSR orientation check, all 20 pool sizes.
- CERT-HEAD3: `l178_tail.py` lines 348-458 byte-for-byte (sha256
  `5bb7b56e6b64`): CERT-REW (l169c P6 reproduced EXACTLY on the original
  cutwA block, 100 draws seed 16943) + the floor-4 draws + the edge->CSR map.
- MID (sha256 `febbc390ad4f`) is TWO lines of bridge code, each
  re-certified against the CSR invariant and the stored orientation counts.
- Forbidden-token audit on all three slices; NO lab module imported (L175:
  a lab run script is a SCRIPT, never a library).
- **CERT-178 (halting): 420 stored anatomical values reproduced by FLOAT
  EQUALITY** (35 actors x depths 1-3 x P/S/per-mass/PI) from
  `l178/static.json` E_anatomical.all_actors, before any depth > 3 was read.
- **CERT-NULL (halting): all 8 stored `Q2b_null_anatomical` statistics
  reproduced by FLOAT EQUALITY** from my own null construction (median,
  p05, p95, q25, q75 at depth 2, median at depth 3, carrier percentile at
  depths 2 and 3).
- Sweep self-check: the depth-1..3 values of the 10-depth sweep match
  L178's stored values at max rel diff **0.0** over all 35 actors.
- Power iteration convergence asserted (rel spread of the last six iterates
  1.18e-16 abs leg, 1.06e-08 Crofts leg).

## Method lesson (new, self-inflicted, caught in-run)

A FLOAT-EQUALITY claim is a claim about the EXPRESSION, not just the
operands: `sum(x[idx].sum() for ...)` over numpy scalars and
`sum(float(x[idx].sum()) for ...)` over Python floats gave different last
bits on this graph, and the first version failed the stored-value assert on
the twin while passing on the carrier (whose depth-1 value is exactly 0).
Mirror the certified script's reduction expression character-for-character
when asserting equality — then record the max rel diff anyway.

## References folded for L174 (prior art, not a threat to the identity claim)

Seguin/Sporns/Zalesky NRN 24:557-574 (2023); Estrada & Hatano PRE 77:036111
(2008); Rosvall et al PRE 72:046117 (2005); Goni et al PNAS 111:833-838
(2014); Avena-Koenigsberger/Misic/Sporns NRN 19:17-33 (2018); Winding et al
Science 379:eadd9330 (2023) — the in-insect precedent.
