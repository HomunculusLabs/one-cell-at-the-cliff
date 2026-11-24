# L215 PREREG — the dead-left-trochanter resurrection (static, zero rollouts)

Tick 245, 2026-11-23. Written BEFORE any L215 value was computed. Zero
rollouts, zero settles, zero dynamics, zero new RNG except the one declared
membership-permutation null. Reads stored artifacts read-only.

## 0. PREMISE CORRECTIONS (written before measuring)

**(0a) The card's `lam1^d` normalisation is a provable NO-OP here, and the
normalisation that is NOT a no-op is the per-substrate GAIN.** The card asks
for "the L206 lam1^d normalisation so the depths are comparable". Every
quantity this card measures lives at depth d = 1 (direct in-edges onto the
pools), and every cross-substrate statistic below is either a RATIO (L209's
law: invariant to any global rescaling of the operator) or a per-side SHARE.
Dividing by lam1^1 therefore cannot move any registered number. What DOES
differ between the two substrates in the rollouts that produced the dead/alive
observation is the **bisected gain**: `g_cutwA = 0.14365819573402408` vs
`g_f4wA = 0.15051452517509462` (stored in `l169b2/raw_l169b2.npz`, ratio
**1.04773**). The floored arm runs its operator ~4.8% hotter by construction
of the op-point match. Every absolute (non-ratio) cross-substrate comparison
below is therefore reported in BOTH currencies — raw and gain-scaled — and
the gain-scaled one is PRIMARY. lam1^d is reported as a measured no-op, not
applied as a correction. If |relative change in any registered ratio under
lam1^1 division| > 1e-9 the no-op claim is FALSE and must be reported as such.

**(0b) A depth-1 static account of these pools has ALREADY FAILED ONCE on the
sibling joint, and that is the honest prior.** L208's VERDICT records the
dissociation: L205 measured the LEFT Ti pools as carrying ~18% LESS per-cell
in-mass, yet they run HOTTER dynamically on every arm (f4wA lvl .1845 L vs
.1187 R) — "static drive does not predict dynamic level, even in sign". So
`B_NEITHER` below is a live branch, not a formality, and a PASS here would be
depth-1 succeeding exactly where its sibling failed.

**(0c) Selection status, named not hidden (Kriegeskorte 2009, digested
tick 243).** The Tr_L pools were SELECTED for this card by being the dead
side in L208's post-hoc floor leg. Everything measured here is therefore a
DESCRIPTION of a selected object. The null in Q4 is a handedness null on a
preselected pool and buys multiplicity discipline inside the pool, never a
p-value for "a pool". The Ti leg (Q3) is the out-of-selection comparator and
is the only leg whose reading is not conditioned on the selection.

## 1. Anchors asserted BEFORE any new number (halting)

- CERT-205 (float equality): every stored value of `l205/static.json`
  `c4_floor_retention` for Ti and Tr (both sides: n_edges_cutwA,
  n_edges_floor_eligible, edge_retention, mass_cutwA, mass_floor_eligible,
  mass_retention, median_syn, frac_syn_lt4, plus both L/R ratios) reproduced
  by this run's own edge arrays = 36 float equalities. Includes the C4 finding
  the card cites: `Tr edge_retention_ratio_L_over_R = 1.013747143709093` and
  `Ti = 0.9796818164438116`.
- CERT-TBL (float equality): `l205/static.json["table"]["Tr"]["cutwA"]` and
  `["f4wA"]` M_L / M_R / M_fL / M_fR / M_eL / M_eR / A_cell, and the same
  seven for Ti = 28 float equalities, reproduced from this run's arrays.
- CERT-G (float equality): `g_cutwA` and `g_f4wA` read from
  `l169b2/raw_l169b2.npz` equal the two literals in 0a exactly.
- Inherited substrate pins (from the verbatim slices): cutwA 21785 nodes /
  644177 edges, f4wA 21789 / 469618, f4-eligible wA edges 469256, pool sizes
  invariant on both substrates with zero L/R overlap.
- L208 premise asserts: `l208/addendum_floor.json` still labelled POST-HOC and
  `l208/static.json["branch"] == "H_UNREGISTERED_SHAPE"`.

Any failure HALTS before a single L215 statistic is read.

## 2. Definitions (fixed here)

For substrate S in {cutwA, f4wA} and pool-side P (union of flexor+extensor
cells on one side of one joint, the L205 `GROUPS` convention):

- `Mp(S,P)` = sum of `vals_all[e]` over edges e of S with dst in P and
  `vals_all[e] > 0`   (EXCITATORY in-mass)
- `Mm(S,P)` = sum of `|vals_all[e]|` over edges e of S with dst in P and
  `vals_all[e] < 0`   (INHIBITORY in-mass)
- `NET(S,P)  = Mp - Mm` ; `TOT(S,P) = Mp + Mm` (TOT == L205's unsigned mass)
- per-cell forms divide by `n(P)`; gain-scaled forms multiply by `g(S)`.
- REMOVED (sub-floor) quantities use the edge set `emask_wA & ~pm4` restricted
  to dst in P, split by sign the same way: `Rp(P)`, `Rm(P)`.
- `ret(P) = TOT(f4wA,P) / TOT(cutwA,P)` (unsigned mass retention).

## 3. Registered questions, bars pinned UNROUNDED

**Q1 — BULK side-symmetry (descriptive + one bar).** Report Rp/Rm/TOT/ret for
Tr_L, Tr_R, Ti_L, Ti_R. BULK_SYMMETRIC := `|ret(Tr_L)/ret(Tr_R) - 1| <= 0.05`.
Registered expectation: TRUE (L205 measured .9049 / .8982 = 1.0074).

**Q2 — the SIGN-NEUTRAL counterfactual (PRIMARY).** The sign-neutral
prediction is that the floor strips each sign class in proportion to total
mass: `NET_pred(P) = NET(cutwA,P) * ret(P)`. Define

    dNET_act(P)  = g_f4wA*NET(f4wA,P)/n(P)  -  g_cutwA*NET(cutwA,P)/n(P)
    dNET_pred(P) = g_f4wA*NET_pred(P)/n(P)  -  g_cutwA*NET(cutwA,P)/n(P)
    S_sign(P)    = (dNET_act - dNET_pred) / dNET_act

- `BULK_ACCOUNTS(P)` := `|S_sign(P)| < 0.25`
- `SIGN_ACCOUNTS(P)` := `S_sign(P) >= 0.50` AND the directional confirmation
  `Rm(P)/Mm(cutwA,P) > Rp(P)/Mp(cutwA,P)` (the floor strips a LARGER fraction
  of the inhibitory mass than of the excitatory mass onto P).

**Q2b — the relu-crossing check (registered, no branch of its own).** Report
the sign of `NET(cutwA,Tr_L)` and `NET(f4wA,Tr_L)`. CROSSES := the first is
<= 0 and the second > 0. Registered expectation: I do NOT expect a literal
sign flip of total in-mass (the pools are motor neurons receiving mostly
cholinergic drive); the honest prediction is that both are positive and the
mechanism, if real, lives in the MAGNITUDE of the net, not in its sign.

**Q3 — SPECIFICITY (the out-of-selection leg).** The same table on Ti, where
neither side is dead. SILENT_ON_Ti := `|S_sign(Ti_L)| < 0.25` AND
`|S_sign(Ti_R)| < 0.25`.

**Q4 — handedness null.** 2000 shared membership permutations (seed 21521,
per-side counts held EXACT on every draw, the L205/L45b instrument) of the
cells within each joint, giving the null distribution of the per-side
asymmetry of the INHIBITORY REMOVAL FRACTION
`A_inh(J) = (rm_L - rm_R)/(rm_L + rm_R)` where `rm_X = Rm(X)/TOT(cutwA,X)`.
Report the two-sided percentile for Tr and for Ti.

## 4. FOUR-CELL BRANCH TABLE (on Tr_L, the card's actor)

|                      | SIGN_ACCOUNTS true | SIGN_ACCOUNTS false |
|----------------------|--------------------|---------------------|
| BULK_ACCOUNTS true   | **B_BOTH**         | **B_BULK**          |
| BULK_ACCOUNTS false  | **B_SIGN**         | **B_NEITHER**       |

- **B_SIGN** = the card's registered expectation: the resurrection is carried
  by an inhibition-specific sub-floor asymmetry.
- **B_BULK** = the floor's near-symmetric bulk stripping is enough.
- **B_BOTH** = both criteria fire (possible when S_sign lands in no man's
  land is NOT possible by construction; B_BOTH requires |S_sign|<0.25 and
  S_sign>=0.50 simultaneously, i.e. it is UNREACHABLE — declared here as a
  deliberately empty cell so the table is honest about its own geometry).
- **B_NEITHER** = the depth-1 anatomical account fails in both forms; the
  resurrection is not a depth-1 in-mass phenomenon at all.

**D_DEGENERATE escape (declared in advance, L175's denominator law).** If
`|dNET_act(Tr_L)|` is smaller than 1% of `g_cutwA*TOT(cutwA,Tr_L)/n`, S_sign
is a ratio with a near-zero denominator and carries direction only; in that
case the branch is reported as `D_DEGENERATE` with the raw masses, and no
BULK/SIGN claim is made.

## 5. PREDICTIONS (scored as registered, never amended)

- P1: BULK_SYMMETRIC TRUE.
- P2: Q2b CROSSES FALSE (both NETs positive — see 0b/Q2b).
- P3: the branch is **B_SIGN** (the card's own registered expectation).
- P4: SILENT_ON_Ti TRUE (the specificity leg holds).
- P5: the Q4 Tr percentile is more extreme than the Ti percentile.

## 6. Verify

CERT-205 (36) + CERT-TBL (28) + CERT-G (2) = 66 float equalities green and
halting; substrate/pool pins green; `l205/static.json`, `l208/static.json`,
`l208/addendum_floor.json` and both npz md5/fingerprints unchanged after the
run; branch table printed with every cell's inputs; lam1 no-op measured and
reported; predictions scored.
