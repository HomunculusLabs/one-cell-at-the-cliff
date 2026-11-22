# L205 VERDICT — the floor-4 handedness static

Tick 234, 2026-11-22. PREREG `l205/PREREG.md` registered first. Code
`l205_build.py` -> generated `l205_static.py`; tail `l205_tail.py`. Artifacts
`l205/{PREREG.md, static.json, run.out, run.err, VERDICT.md}`. Zero rollouts,
zero settles, CPU only, 3 s. No live changes.

## Branch: H_UNREGISTERED_SHAPE — and that is the headline

The registered branch space was (H_STATIC, H_DYNAMIC, H_STATIC_NOFLIP). None
fired. The measured shape is one I did not register:

**the static in-mass handedness points RIGHT on BOTH substrate families —
the same direction as the BASE arms' dynamic dominance and the OPPOSITE
direction from the FLOORED arms' L-dominance — and the floor's own static
nudge moves it FURTHER RIGHT.**

H_DYNAMIC's precondition was "A_cell sits INSIDE the null band". The real
A_cell sits at the band's LOW edge (one-sided-up percentile 0.048), i.e.
outside-low rather than inside, so the registered H_DYNAMIC cell could not
fire even though its *conclusion* is what the three legs below support.
That is a pre-registration defect, not a measurement defect, and it is
disclosed as such (method lesson at the bottom).

## The numbers

Ti, per-cell in-mass (PRIMARY form; `A > 0` = LEFT heavier), 2000 shared
membership-permutation draws, seed 20526:

| substrate | family | m_L | m_R | A_cell | pct_up | two-sided \|A\| pct |
|---|---|---|---|---|---|---|
| base_closure | base | 288.60 | 345.34 | −0.0895 | 0.058 | — |
| cutwA | base | 288.06 | 344.84 | **−0.0897** | **0.058** | **0.877** |
| cutng25 | base | 288.06 | 344.84 | −0.0897 | 0.058 | — |
| f4_closure | floor4 | 255.32 | 309.83 | −0.0965 | 0.049 | — |
| f4wA | floor4 | 254.83 | 309.45 | **−0.0968** | **0.048** | **0.898** |
| f4ng | floor4 | 254.83 | 309.45 | −0.0968 | 0.048 | — |
| f4tw | floor4 | 254.83 | 309.42 | −0.0967 | 0.048 | — |

Null band (f4wA): [−0.0961, +0.1008], sd 0.0603.

Tr: A_cell −0.0155 (base) / −0.0118 (floored), two-sided \|A\| percentile
0.29 / 0.22 — squarely inside the null on both families.

Paired delta on the SAME draws, Ti: `A_cell(f4wA) − A_cell(cutwA)` =
**−0.00707**, one-sided-up percentile **0.0135**, paired null
[−0.00534, +0.00532], sd 0.00329 (|z| ≈ 2.15). Tr: +0.00369, pct 0.912,
null [−0.00443, +0.00449] — at the upper edge, opposite sign, so the two
joints do not even agree on the floor's direction.

### Gate cells (L109, separate objects)

- **C1 FLOORED — FAIL.** A_cell(f4wA) = −0.0968 is NEGATIVE: the floored
  graph's left Ti pools carry *less* in-mass, 18% less per cell. The
  registered prediction for H_STATIC was the opposite sign.
- **C2 BASE — FAIL on the percentile, PASS on the sign.** A_cell(cutwA) =
  −0.0897 < 0 as registered, but pct_up 0.058 > 0.05. One-sided-marginal.
- **C3 FLIP — FAIL.** delta = −0.00707 < 0: the floor moves the asymmetry
  RIGHTWARD while the dynamics move LEFTWARD. Outside the paired null in the
  WRONG direction.
- **C4 MECHANISM (descriptive) — the delta's cause is identified.** On a
  FIXED node set (cutwA) the left Ti pools have fewer in-edges (6,964 vs
  8,296) and a higher fraction of sub-floor synapses (19.28% vs 17.61%), so
  the syn≥4 floor strips relatively more from the left: edge retention
  0.8072 L vs 0.8239 R (ratio 0.9797), mass retention 0.8847 vs 0.8972
  (ratio 0.9860). Median synapse count is 7 on both sides. For Tr the ratio
  inverts (1.0137 / 1.0074) — the floor is near-side-symmetric in bulk and
  its residual handedness is joint-specific and tiny.
- **C5 SHARED-DRIVE COMPANION (descriptive) — null-inside and
  floor-invariant.** The statistic nearest in KIND to the dynamic S (common
  drive: per side, Σ_sources min(mass→flexor, mass→extensor) into the Ti
  pair): cutwA L 1356.17 / R 1790.01, A = −0.1379, percentile 0.206, null
  [−0.2651, +0.2639]; f4wA L 1118.46 / R 1481.40, A = −0.1396, percentile
  0.221, null [−0.2855, +0.2923]. Inside the handedness null on both
  substrates, and the floor shifts it by 0.0017 — nothing.

## What this licenses

1. **The dominance flip is NOT an edge-floor bookkeeping effect at depth 1.**
   Every static leg either points the wrong way (C1, C3) or shows nothing
   (C5, Tr). The floored arms' left-side antiphase self-orders on the side
   with *less* in-mass and *less* common drive — a dynamics/attractor
   property, the L45b class, as H_DYNAMIC would have claimed had its
   precondition been written to cover a sign inversion.
2. **Static handedness itself is marginal, not established.** The
   one-sided-up percentile 0.048 looks like a pass only because the null is
   symmetric about zero and the real value is negative; the honest two-sided
   test of "is this L/R split more extreme than relabelling these same
   cells" gives 0.877 (base) and 0.898 (floored) — it does NOT clear 0.95.
   The R-heavy in-mass bias is reported as a DIRECTION with its absolute
   masses, never as an established wiring asymmetry.
3. **The one genuinely outside-null static effect runs against the
   dynamics.** That is stronger evidence against H_STATIC than a null
   result would have been: there IS a small, detectable, mechanistically
   explained (C4) floor-induced handedness shift, and it is anti-correlated
   with the dominance flip it was proposed to explain.
4. **New hypothesis, NOT measured here (seeded, not claimed):** the left Ti
   pools are the less-driven side (m_L 255 vs m_R 309, −18%; shared drive
   −0.14). Lower drive sits further from the RMAX saturation ceiling, and
   L178 already measured that only 19 of 303 pool cells are active at this
   op point. "Antiphase self-orders on the *less saturated* side" is a
   testable dynamical story and is seeded as a queue item, not asserted.

## Verification

- **CERT-HEAD1.** `l205_static.py` is GENERATED; HEAD1 = `l151_static.py`
  lines 1-319 BYTE-FOR-BYTE, sha256 `e6245e8306dc8a0f…` — IDENTICAL to the
  head sha L178 recorded, so the same L151/L142/L134/L92/L101 pin set
  re-ran as free certification before any L205 value was read
  (`[pins] ladder+graphs GREEN`).
- **CERT-HEAD2.** HEAD2 = `l178_tail.py` lines 22-83 BYTE-FOR-BYTE, sha256
  `66112b0c221d02d8…`, asserted a literal slice of its source, first line
  `FLOOR = 4` and last `del _z` asserted. It re-ran CERT-F4 in full:
  K4 73, carrier rank 21, twin gi 290, mass gap 2.44e-05, jaccard 0.9231,
  closure 472,095, wA 469,256, f4wA n 21,789 / edges 469,618, family 33,
  plus the three stored gains at FLOAT EQUALITY
  (0.15051452517509462 / 0.16230986118316648 / 0.15261898636817928).
- **Forbidden-token audit** on both head slices (`"w"`, `'w'`, `import l1`,
  `import l9`, `savez`, `to_csv`, `json.dump`, `write_text`) so running the
  generated script cannot touch l151's or l178's artifacts. NO lab module
  was imported (the L175 lesson: a lab run script is a SCRIPT, never a
  library).
- **DISCLOSURE on the card's verify line.** The card asked for the graph
  build "imported from l169b2_run.py". A literal import is forbidden by the
  L175 lesson, so the verbatim-source-slice form was used instead; the f4
  ladder derivation in HEAD2 is the l169b2_run.py lines 668-701 convention
  byte-for-byte as carried through l178_tail.py, and every stored f4 pin is
  asserted. Substitution registered in the PREREG before the run.
- **Substrate edge counts asserted before any L205 value:** f4wA 469,618;
  f4 closure 472,095; floor-eligible wA 469,256; cutwA 644,177; cutng25
  644,084; closure 647,953 == S92["edges_new"]. f4ng 469,537 / f4tw 469,519
  reported (not previously pinned). XOR design asserted per arm (carrier in
  / out, twin in / out).
- **Pool invariance asserted, not assumed:** all 20 semantic pool sizes
  equal the stored S92 values on ALL SEVEN substrates; no L/R overlap in any
  pool; Ti 50 L / 51 R flexor and 6/6 extensor, Tr 31/31 and 24/24.
- **Null integrity:** per-side counts held EXACT on every one of the 2000
  draws (asserted); draws SHARED across substrates so the delta null is
  genuinely paired; seed 20526 recorded.
- Both substrate families and BOTH sides reported, gating or not (the card's
  own requirement), plus a flexor/extensor decomposition per side.
- Side convention confirmed load-bearing-correct before the direction was
  read: the dynamic duty metric (`l169b2_verdict.s_arrays` -> `Ti_fL/Ti_eL`)
  uses the SAME `POOL_G` keys, built from the same annotation `side` column
  via the same `SIDE_MAP`, as this static. "L" means the same side in both
  measurements.

## Method lesson (self-inflicted, now in the skill)

A signed pre-registered hypothesis needs its branch space to cover the
SIGN-INVERTED outside-band case. I registered H_STATIC (correct sign,
outside band), H_DYNAMIC (inside band) and H_STATIC_NOFLIP (correct sign,
no delta) — and the data landed on *wrong sign, outside band*, which is the
most informative outcome of the four and the only one with no cell. The
fallback `H_UNREGISTERED_SHAPE` caught it honestly instead of silently
mapping it onto the nearest registered label, but the branch table should
have had four cells from the start: sign x band, not a hand-picked three.
