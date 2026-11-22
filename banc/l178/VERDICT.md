# L178 VERDICT — branch **B_CARRIER_LOW**

Registered branch fired: `r2 <= 0.80` → **B_CARRIER_LOW**, a path signature in
the direction *opposite* to the obvious hypothesis. The carrier does NOT reach
the motor pools more than its mass-matched twin over short paths; it reaches
them **far less**, and less than chance relocations of its own edges.

Substrate f4wA (n 21,789 / 469,618 edges), gain g_f4wA 0.15051452517509462,
20 semantic pools, carrier gi 1110 / twin gi 290, PREREG `l178/PREREG.md`.

## Gates (each a separate object)

| gate | result |
|---|---|
| Q5 instrument (halting) | **PASS** — one-step rel err 2.552e-03 < 1e-2 |
| Q1 claim (r2) | **B_CARRIER_LOW** — r2 = 0.0 gated, **0.503 anatomical**; r3 = 0.0 gated, **0.241 anatomical** |
| Q2 null (gated) | PASS, percentile 0.0 — but rests on a zero, see Q2b |
| Q2b null (anatomical, the claim-bearing one) | **PASS** — carrier 0.0402 vs null med 0.336 [p05 0.210, p95 0.476], percentile **0.0** of 100; depth-3 percentile 0.0 |
| Q3 mass-restatement branch | **NOT degenerate** — Spearman(P2abs, m_out) = 0.1398 gated, **−0.021 anatomical** over 35 ng actors (bar was ≥0.95) |
| Q4 polarization | carrier PI2 **0.906** vs twin 0.645; PI3 **0.840** vs twin 0.272 (anatomical). Gated carrier PI = NaN (zero signed reach) |
| Q6 top-k certification | exhaustive depth-2 enumeration == matvec for all 35 actors, rel diff 0.0 |

## What the numbers say

1. **Zero gated short-path reach, exactly.** At the settled operating point the
   carrier has **0 depth-2 walks** into any of the 20 pools (exhaustive
   enumeration: `n_paths = 0`), and 0 at depth 3. Its mass-matched twin has 3
   such paths (total 0.1174). This holds on all three settle seeds (3/3).
2. **It is wiring, not only gating.** With the row mask removed (pure
   `|g·W_beta|`), the carrier still reaches pools at **0.0402 per unit
   out-mass vs the twin's 0.0798** (ratio 0.503) and **1.57 vs 6.53** at
   depth 3 (ratio 0.241). Among the 35 ng actors the carrier ranks **33rd of
   35** on anatomical depth-2 reach per unit mass, against a family median of
   0.398 — roughly **10× below** the family.
3. **Below every degree-neutral relocation of its own edges.** All 100
   l169c-protocol destination swaps (which preserve its out-degree, its
   out-weight multiset and every target's in-degree) give the carrier **more**
   pool reach than its real wiring: median 0.336 vs real 0.0402, percentile
   0.0 at both depth 2 and depth 3. The carrier's out-edges are placed so as
   to *avoid* short paths to the motor pools.
4. **Anatomy of the avoidance.** Only **5 of the carrier's 69 targets** carry
   any out-edge into a pool cell, versus 19 of the twin's 97 and a family
   median of **22** (0 of 33 family cells have zero). Direct pool mass is 0.0
   for the carrier (the L151/L169c crossed law re-confirmed) while the twin
   has 1.79 — the "twin" is not even a pure 2-hop actor.
5. **Less reach, more polarization.** What little the carrier does reach is
   far more differential across antagonist partners: PI2 0.906 vs 0.645,
   PI3 0.840 vs 0.272. Direction, not magnitude (see disclosure 2).
6. **Not a mass restatement** (the card's registered degenerate branch did not
   fire): path reach and out-mass are essentially uncorrelated across the ng
   family (ρ = −0.021 anatomical).

## Disclosures

1. **The gated leg is twin-side labile.** Across the three settle masks the
   carrier is 0.0 in 3/3, but the twin reads 0.117 / 0.363 / **0.0** — so the
   gated r2 is 0.0, 0.0 and undefined (0/0). Only the ANATOMICAL leg is
   seed-free, and every claim above is stated on it. The gated numbers are
   reported as a consistent-direction companion, never as the claim.
2. **PI is a direction here.** The carrier's absolute depth-2 pool mass (6.77)
   is ~2.5× smaller than the twin's (17.2); a polarization ratio computed on
   the smaller of two small numbers is a direction, not a magnitude (L175 law).
3. **Only 19 of 303 pool cells are active** at this operating point (6.3%),
   which is why the gated reads collapse toward zero at all. This is a
   property of the operating point, disclosed, not a defect of the actors.
4. **Row masks are not seed-stable** (Jaccard vs seed 801: 0.716 and 0.817) —
   a further reason the claim is carried anatomically.
5. **Q2/Q2b are geometry nulls at the real operating point**, not re-settled
   dynamics nulls (l169c P7 requires a fresh af-matched bisect per draw).
6. The three L164/L152/walk limitations registered in the PREREG stand: the
   Liu/Ganguli/Baccus theorem does not apply to a recurrent non-additive
   readout; the linearization point is a phase snapshot; depth-3 sums are
   operator powers (walks with revisits), not simple paths.
7. The card's "ng-family cells as the known SUPER arm" is absent from f4wA by
   construction; the family arm is the ng tail (ranks 23–55, 33 cells), as
   registered in the PREREG.

## Mechanistic reading (one sentence for the draft)

At matched out-mass the carrier is not a privileged *driver* of the antagonist
pools but a privileged *avoider* of them: its 69 out-edges land almost entirely
on cord interneurons that do not themselves project to motor pools (5 of 69 vs
a family median of 22), giving it 2× less depth-2 and 4× less depth-3
anatomical pool reach than its mass-matched twin and less than all 100
degree-neutral relocations of its own edges — so whatever the carrier's
dynamic effect is, it is not a short-path drive of the readout, and the
identity cliff needs a longer-loop or network-state explanation.

## Certifications

- CERT-HEAD: `l178_static.py` head = `l151_static.py` lines 1-319 byte-for-byte
  (sha256 `e6245e8306dc8a0f…`), forbidden-token audit passed; tail sha256
  `b7d1930a4c560ebe…`. No lab module imported (L175).
- CERT-F4: f4 ladder re-derived and asserted field-for-field against
  l169b/static.json F3 (K4 73, carrier rank 21, gi 319 rank 33, twin gi 290,
  mass gap 2.44e-05, jaccard 0.9231, closure 472,095, wA 469,256); f4wA
  n 21,789 / edges 469,618 against l169b2/run.out; three stored gains at
  FLOAT EQUALITY.
- CERT-REW: the l169c destination-swap transcription reproduced
  l169c/static.json P6 EXACTLY on the original cutwA block (100 draws, seed
  16943: med_relocated 80.0, min 80, med_moved 80.0, med_mass_T70 0.0,
  med_mass_motor_share 0.1090891270920994, med_n_dst 80.0, per_draw_first5
  field-for-field) before the floor-4 adaptation was used.
- CSR orientation `W[target, source]` asserted against the carrier's atlas row
  (69 out in the column index, 12 in the row span).
- Op point asserted per seed (af 0.10978 / 0.10955 / 0.11015, band
  [0.095, 0.125], AF_T 0.10906, stored rollout af 0.10889).
- Q6 brute force: exhaustive depth-2 enumeration equals the matvec total for
  all 35 actors (rel diff 0.0), so the search machinery is exact.

Artifacts: `l178/{PREREG.md, static.json, run.out, run.err, VERDICT.md}`,
code `l178_{build,tail}.py` → generated `l178_static.py`. Runtime 8 s, CPU
only, zero rollout batches (3 × 400-step settles + 2 nonlinear steps).
