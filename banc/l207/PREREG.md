# L207 PREREG — is the avoidance the CELL or the LADDER SLOT?

Registered 2026-11-22 ~12:55 EST (tick 236), BEFORE any L207 value was read.
Static, zero rollouts, zero settles, zero dynamics, CPU only.

## The question

L178 measured, on the floor-4 substrate f4wA, that the carrier (gi 1110,
DNp33-L, pure-projecting descending) reaches the 20 semantic motor pools at
depth 2 with per-unit-out-mass walk mass 0.0402 against a 33-cell family
median 0.398 (rank 33 of 35), and L206 showed that deficit is depth-invariant
(~10.4x at every depth 1..10, percentile 0.0 vs 100 degree-neutral swaps) and
is a ~10x smaller coefficient on the operator's dominant mode rather than a
path-length effect.

But every one of those reads lives on ONE substrate, where the comparison
family is MASS-ORDERED: the carrier occupies ladder slot 21 of the floor-4 ng
ladder, and a slot effect (whoever sits at that out-mass rank avoids) cannot
be separated from a cell effect (THIS cell avoids) on f4wA alone.

## Substrates and ladders (all already on disk, head-certified)

| key | keep / emask | ladder | carrier slot |
|---|---|---|---|
| G0_closure | keep_new / emask_n | ng_desc (58, no syn floor) | 25 |
| G1_cutwA | keep_wA / emask_wA | ng_desc present tail (34) | 25 (first present) |
| F4_f4wA | keep_f4 / emask_f4 | ng4 (55, syn>=4) | 21 |

The carrier therefore occupies TWO DISTINCT SLOTS across the three
substrates, and two slots are occupied by OTHER cells:

- `SLOT21_closure` := ng_desc[20] — the cell that sits in the carrier's
  floor-4 slot on the closure ladder (present on G0; REMOVED on G1_cutwA,
  which is why the slot leg is asked on the closure substrate — registered
  here, not discovered later).
- `SLOT25_f4` := ng4[24] — the cell that sits in the carrier's closure slot
  on the floor-4 ladder (present on f4wA, since only ng4[:20] are removed).

## The statistic (one object, declared in full)

R(cell, substrate) := [ complete length-2 ABS walk mass of the anatomical
operator A = |W_beta| from the cell into the union of the 20 semantic motor
pools ] / ( lam1(A)^2 * m_out(cell, substrate) )

- ANATOMICAL: no row mask, no settle, no seed (L178's E_anatomical leg).
- lam1 by power iteration on the nonnegative operator, 400 iterations, per
  substrate, convergence asserted (rel spread of last 6 iterates < 1e-6).
- The lam1^d division is L206's PRIMARY normalisation and it makes R GAIN
  INVARIANT (reach scales g^d, lam1^d scales g^d), which is exactly why the
  comparison across substrates with different bisected gains is admissible;
  this is asserted numerically, not asserted in prose.
- m_out = sum of |vals_all| over that substrate's out-edges of the cell.
- The Crofts/Estrada second leg (tick-233 amendment (b)) is NOT run this
  tick and that is DISCLOSED here in advance: L206 already reported it agrees
  in ORDER and differs in magnitude, and the cross-substrate strength
  normalisation is not neutral under the substrate change. Primary leg only.

pct(cell, substrate) := fraction of that substrate's PRESENT LADDER cohort
(excluding the cell itself) with R STRICTLY SMALLER than the cell's R.
LOW pct = avoider. Registered bar: "extreme avoider" iff pct <= 0.10.

## Gate cells (L109 — SEPARATE objects, never ANDed into one verdict)

- **Q1a** carrier pct on each of the three substrates.
- **Q1b** SLOT21_closure pct (G0) and SLOT25_f4 pct (f4wA).
- **Q1c** Spearman rho between 1-indexed ladder slot and R across each
  substrate's present ladder. Registered bar: |rho| >= 0.5 means ladder slot
  predicts avoidance (slot structure present).
- **Q2** the MIRROR cell: gi 928 = DNp33-R, the carrier's contralateral
  homolog as identified in l169c P2_hom_identity (pt_root_id
  720575941451941498, descending, acetylcholine, present on G0/G1 and on
  f4wA; NOT a ladder member, so its cohort is a MASS-MATCHED one — the 100
  present descending cells nearest in log out-mass, excluding carrier and
  mirror). The carrier is reported on the SAME cohort rule so the mirror has
  a like-for-like comparator. This is a MATCHED-COHORT null, NOT the l169c
  degree-neutral rewire null; stated here so it is never written up as one.
- **Q3** the v783 cross-connectome handle (EXPLORATORY, L78 non-transport law
  applies): does the carrier or the mirror carry an inline fafb_783_match_id?
  Registered in advance: even a present match may leave the question
  UNANSWERABLE, because v783 is a BRAIN-ONLY volume with no leg motor
  neurons, so "its downstream readout" has no counterpart — if so the honest
  output is that structural verdict plus a sliced follow-on item, never a
  substituted statistic.

## Branch table — Q1 (SIGN x BAND, the L205 lesson: cover all cells)

- **B_CELL** — carrier pct <= 0.10 on ALL three substrates AND BOTH slot
  comparators inside (0.10, 0.90).
- **B_SLOT** — carrier pct > 0.10 on at least one substrate AND BOTH slot
  comparators <= 0.10.
- **B_BOTH** — carrier pct <= 0.10 on all three AND at least one slot
  comparator <= 0.10.
- **B_NEITHER** — carrier pct > 0.10 somewhere AND both comparators > 0.10.
- **UNREGISTERED_SHAPE** — anything else; reported under that name with the
  measured cells, never mapped onto the nearest registered label.

Q2 branches: **M_AVOIDS** (mirror pct <= 0.10 on >= 2 of 3 substrates),
**M_TYPICAL** (inside (0.10, 0.90) on >= 2), **M_HIGH** (>= 0.90 on >= 2),
**M_MIXED** otherwise.

## Predictions (scored afterwards, wrong is informative)

- Q207-1: Q1 lands **B_CELL**. The carrier was identified by DELETION
  phenotype (L169b2/L175), and L206's finding is a global coefficient on the
  dominant mode, which is a property of a cell's wiring, not of a rank.
- Q207-2: Q1c |rho| < 0.5 on all three substrates (no slot structure).
- Q207-3: Q2 lands **M_AVOIDS** — homologous cells should carry homologous
  wiring, so the mirror avoids too.
- Q207-4: Q3 is UNANSWERABLE-BY-VOLUME (no leg motor counterpart in v783),
  independent of whether a match id exists.

## Verify (the card's own line, plus the house certifications)

- PREREG first (this file).
- L178's f4wA numbers reproduced BEFORE any new substrate is read:
  CERT-HEAD3 is l206_tail.py lines 22-121 VERBATIM, whose CERT-178 block is
  HALTING over 420 stored anatomical values at FLOAT EQUALITY.
- The generic substrate builder is certified against the certified
  specialisation: build_sub(keep_f4, emask_f4) must reproduce the
  head-built f4wA CSR index arrays and value vector EXACTLY
  (np.array_equal), and reach_sub must reproduce reach() on f4wA at FLOAT
  EQUALITY. Only then is it applied to G0/G1.
- Gain invariance asserted numerically (g=1 operator x G_F4WA^2 vs L178
  stored depth-2, rel diff < 1e-12).
- All 20 pool sizes asserted invariant on all three substrates, zero L/R
  overlap; substrate node/edge counts asserted against stored pins.
- No lab module imported (L175: a lab run script is a SCRIPT, never a
  library); every inherited slice is a VERBATIM source slice with its sha256
  recorded and a forbidden-token audit.
- Writes l207/static.json ONLY. sessions/ untouched. No live change.
