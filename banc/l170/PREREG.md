# L170 PREREG — male matched-floor extraction (ours)

Registered 2026-11-20 ~13:55 EST, tick 198, BEFORE any floor>=2 number is
computed. Static card: ZERO rollouts, no RNG, CPU only.

## Why

Our male closure-mirror extraction (`l138_static.py`, stored
`l138/static.json`) applies **no synapse floor**, while the BANC v626
connections release carries an **implicit pair-level floor of 3** (measured and
pinned in L146, `banc/l146/static.json`). DRAFT §2.6 therefore compares a
floor-1 male ladder against a floor-3 BANC ladder and concludes "the ladder
does not transfer". That conclusion is, as the external review (L167, item I2)
pointed out, an **unmatched-floor comparison**.

This card reproduces the male extraction *ourselves* at the matched floor and
then either walks that ladder or re-scopes §2.6.

## Feasibility pre-check (ran BEFORE this registration, L146 + L125 rule)

`l170_precheck.py` -> `l170/precheck.json` (stored):
MaleCNS `connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather`
carries 25,568,639 rows, **one row per ordered body pair (0 duplicate pairs)**,
weight min **1.0** / max 2591. Effective release floor = **1**, with 10,295,463
weight-1 pairs (40.3%). So floor >= 3 is **ADMISSIBLE and non-vacuous**
(deletes 58.9% of pairs; 10,512,742 of 25,568,639 survive) — the L146
vacuous-by-dataset failure mode does NOT apply here, unlike on the BANC side.

Because the male release is pair-unique, "collapse then floor" and "floor" are
the same operation on this file; no groupby is needed before the floor (the
BANC side already collapses per-neuropil rows upstream in the verbatim head).

## Substrate and arms

Head block = `l138_static.py` lines 1..(before `out = dict(design=`) VERBATIM,
asserted byte-identical by `l170_build.py`, so every BANC pin (L92/L107/L121/
L131/L134 k-ladder, rank twins 1110/319, K/mass_split) and every male form
re-runs as free certification. `l138/static.json` is NEVER rewritten.

`male_ladder(floor)` re-runs the l138 male closure-mirror extraction verbatim in
form, over the edge subset `weight >= floor`:

- A1 floor=1 — **CERT arm** (release floor; must reproduce l138 exactly)
- A2 floor=2 — ladder rung (descriptive)
- A3 floor=3 — **the matched-floor arm** (BANC's implicit floor)
- A4 floor=4 — the strongest admissible BANC floor (L169 b1/b2 arm), ladder rung

## CERT block (all must pass before any floor>=2 number is read)

- **CERT-1**: `male_ladder(1)` == `l138/static.json:male_s1` EXACTLY on all 8
  fields (n_keep_old 21516, n_keep_new 21544, dn_new 28, added_edges 1942,
  added_dn_out_edges 787, dn_new_glut 0, dn_new_ng 9, heavy_K 9) plus
  heavy_mass_share 0.5187.
- **CERT-2**: the floor-1 DNp33 rows reproduce `l138/static.json:probe.male_dnp33`
  (gi 616 R: 222 out / 37 in; gi 1342 L: 224 out / 33 in) and
  `male_pure_proj` 28, `male_dn_into` 1277, `male_dn_total` 1314.
- **CERT-3**: verbatim-head pins green (printed by the head itself).

## Pre-registered predictions

- **P1 (direction)**: dn_new(floor 3) > dn_new(floor 1) = 28. Mechanism:
  `dn_into` membership needs only ONE cord->DN edge, and at floor 1 97.2% of
  male DNs qualify (`male_dn_into_frac` .972); raising the floor strips weak
  cord->DN edges, so DNs that keep a strong descending projection but lose
  their weak ascending input move INTO the pure-projector cohort.
- **P2 (direction)**: male DNp33's cord IN-edge count falls from 37/33.
- **P3 (descriptive, NOT a gate)**: the floor ladder 1->4 for dn_new / K is
  reported as a monotonicity read, not asserted monotone — a DN can also LOSE
  `dn_proj` and drop out of the cohort, so both directions are admissible.
- **P4 (feasibility)**: at floor 1 the male ng ladder has only 9 cells, so the
  BANC window shares (r1_19 / r20_29 / r30_58) are undefined on the male side
  (stored null). If floor 3 gives n_ng >= 29 the window comparison becomes
  computable for the first time.

## Registered branches (EXPLICIT precedence, M1 before M2)

- **M1_floor_changes_cohort** — fires if `|dn_new(3) - 28| / 28 >= 0.20`.
  Verdict: §2.6's cross-graph ladder comparison was an unmatched-floor
  comparison. Required fold: re-scope §2.6 to "untested at matched floor",
  state OUR floor-3 cohort size and K, and store the floor-3 ladder as design
  pins for a future dynamic walk (which is a rollout card, NOT this one).
- **M2_floor_neutral** — fires only if M1 does not AND `|K(3) - 9| <= 1`.
  Verdict: the floor is not the explanation; §2.6's no-transfer claim stands
  as measured, and gains a one-line floor-matched robustness sentence.
- **M3_dnp33_pure** (SECONDARY, binary, both directions registered): whether
  male DNp33 (the cross-graph anchor cell, reciprocal at floor 1 with ladder
  mass exactly 0) enters the pure-projector cohort at floor 3. Reported either
  way; it does not override M1/M2.

## Evidence rule (inherited from L167)

The reviewer's own floor-3 numbers (**342 pure-projection DNs, K=52**) are
REVIEWER-REPORTED. They may NOT enter the draft. After this run we may state
only OUR measured numbers; any agreement/disagreement with the reviewer is
recorded in LANE-LOG / ADJUDICATION, never cited as evidence in the draft.

## Scope / no-overreach clauses

- This card produces NO dynamic result. Whether the identity cliff expresses on
  a floor-3 MALE substrate is **untested** after this card; saying otherwise
  would be the L169 (b1)->(b2) static/dynamic conflation the lane already paid
  for once (L94 substrate-rule law).
- The floor is applied ONLY to the male side. The BANC side is already at its
  native floor 3, which is exactly what makes the comparison matched.
- No live changes, no service edits, no `l138/` or `l151/` or `l146/` rewrites.
