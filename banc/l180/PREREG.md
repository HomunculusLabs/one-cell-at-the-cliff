# L180 PREREG — floor-sensitivity of the BANC-side cohort rule (tick 221, 2026-11-21)

Written BEFORE any computation. ZERO rollouts, zero RNG, no graph build, no
live change, no draft edit. Pure static derivation from the same verbatim
extraction as `l92_static.py` (annotations + NT predictions + the collapsed
connections release), every input read-only with mtimes asserted unchanged.

## The question

L170 measured, on the MALE (MaleCNS) graph, that the DN cohort's membership is
floor-sensitive: the "new" cohort (`dn_new = dn_proj & ~dn_into`) goes
28 -> 199 -> 342 cells over synapse floors 1 -> 2 -> 3 (stored
`l170/static.json` ladder; verdict `rel_change` 11.2143, i.e. ~12x).

The BANC side has never been asked the mirror question. Our closure subnet
(`l92_static.py`) keeps `cord | dn_into | dn_proj`, giving
cord 20,521 | DNi 728 | DNn 560 (dn_proj 1,287), and the 560 DNn cells are
precisely the cells the l65 rule dropped because they have NO cord->DN
in-edge. So on BANC the marginality lives on the OTHER side of the rule: it is
the 728 `dn_into` cells whose admission can rest on a single weak cord->DN
edge, and the 560 move when that admission is withdrawn.

## Hard constraint from L146 (checked first, not assumed)

The BANC v626 connections release carries an implicit pair-level synapse floor
of 3 (all 2,676,592 post-collapse pairs sum >= 3; pinned in
`banc/l146/static.json`). Therefore:

- the BANC ladder CANNOT be run at floors 1 or 2 — those rungs are vacuous by
  dataset (L146 class), so a rung-for-rung comparison against the male's
  1 -> 2 -> 3 ladder is NOT available;
- the BANC baseline rung IS floor 3, which is the male ladder's LAST rung;
- the first admissible counterfactual rungs are 4 and 5 (the card's own ask).

FLOOR REPORT FIRST: histogram the cord->DN pair weights before any
counterfactual number is read, and assert min == 3. If the min is not 3, halt
and disclose (the L146 pin would be wrong and every rung below it vacuous).

## C0S-180 CERT (runs FIRST, halts on mismatch)

Re-derive, from the verbatim extraction, and assert EXACTLY equal to the
stored `l92/static.json`:

n_old 21249, n_new 21809, cord 20521, dn_into 728, dn_proj 1287, dn_new 560,
edges_old 627051, edges_new 647953, all 9 edge blocks (cord->cord 560236,
cord->DNi 5322, cord->DNn 0, DNi->cord 53329, DNi->DNi 8164, DNi->DNn 2189,
DNn->cord 14279, DNn->DNi 3047, DNn->DNn 1387), the 8 pool sizes
(Ti 50/51/6/6, Tr 31/31/24/24), mech 4848, motor 728, dng100 2,
dn46_in_subnet 3, dn46_pos [270, 302, 366].

No counterfactual number is reported unless the CERT passes 100%.
(L85 rule: the extraction is copied from `l92_static.py`, never re-invented.)

## Measurements (declared before compute)

M1 MARGINALITY CENSUS of the 728 dn_into cells. Per cell: the number of
cord->DN in-pairs, and `maxsyn` = the largest collapsed `syn_count` among
them. A cell survives a floor f iff maxsyn >= f. Report:
- the count of cells admitted by EXACTLY ONE cord->DN pair;
- the count with maxsyn == 3 (evicted from dn_into at floor 4) and
  maxsyn <= 4 (evicted at floor 5);
- the median/quartiles of the in-pair count and of maxsyn.

M2 MIRROR CENSUS of the 560 dn_new cells on their ADMITTING side: per cell the
number of DN->cord out-pairs and maxsyn over them (dn_new membership requires
dn_proj, which a floor can also withdraw).

M3 LADDER, two declared floor regimes, both reported (neither selected):
- (A) GLOBAL floor (the mirror of L170's `edges_kept`): drop every collapsed
  pair with syn_count < f, then recompute cord_mask (unchanged, annotation-
  derived), dn_into, dn_proj, dn_new, n_new, edges_old, edges_new.
- (B) cord->DN-ONLY floor: apply f only to the cord->DN edge class, which
  isolates the disqualification margin from every other graph change.
f in {3 (baseline), 4, 5}; f = 6 and f = 10 reported as extra diagnostic rungs
so the trend is visible beyond the two rungs the card names.

M4 DECOMPOSITION of any change in the 560: every cell leaving/entering dn_new
is classified as
- MIGRATION (lost its cord->DN in-edges, so dn_into -> dn_new),
- EVICTION (lost its DN->cord out-edges, so it leaves dn_proj entirely), or
- STAY.
dn_new_f = (stay) + (migration) - (eviction of former dn_new). Report the
three counts, not just the net.

M5 SENSITIVITY NUMBER comparable to L170's: `rel_change` computed the same way
(`(dn_new_hi - dn_new_lo) / dn_new_lo`) over the BANC-admissible span 3 -> 5,
reported BESIDE the male's 1 -> 3 value with the span difference stated in the
same sentence. Also report the PER-STEP change 3 -> 4 against the male's
2 -> 3 step so one honest rung-matched comparison exists.

## Pre-registered predictions (scored either way)

- Q1: the BANC per-step sensitivity (3 -> 4, regime A) is SMALLER than the
  male's last step (2 -> 3, which was 199 -> 342 = +71.9%), because BANC's
  baseline already sits at the male ladder's top rung.
- Q2: dn_into membership is NOT predominantly single-edge: fewer than 25% of
  the 728 cells are admitted by exactly one cord->DN pair.
- Q3: the 560 RISES under a floor in regime B (cord->DN-only: cells can only
  migrate in, never be evicted) and the direction in regime A is NOT
  registered — regime A has both channels open, so M4's decomposition is the
  claim-carrier.
- Q4: THICK margin — the §4 sentence lands as cohort-rule ROBUSTNESS rather
  than fragility, defined as: at floor 4 regime A the 560 moves by less than
  the male's 11.2x, AND fewer than 10% of the 728 dn_into cells are evicted.

## Branches (declared, mutually exclusive)

- B_ROBUST: Q4's two conditions both hold -> the draft gains a §4 ROBUSTNESS
  sentence (BANC cohort rule is floor-stable over its admissible span) with
  the male contrast and the span asymmetry stated.
- B_FRAGILE: either condition fails -> §4 FRAGILITY sentence naming the
  evicted count and the rung at which it happens.
- B_VACUOUS: if the histogram shows the cord->DN class already has min > 3 so
  that floor 4 deletes nothing, disclose the vacuous rung (L55/L146 class) and
  register the first ADMISSIBLE rung as an in-run addendum.

## Verification

- C0S-180 CERT first, 100% or halt.
- Floor histogram printed before any ladder number.
- Input mtimes (data/dv_11842997, data/dv_11845666, data/dv_11837016,
  banc_graph.pt, l92/static.json, l170/static.json) asserted unchanged at the
  end; `mtimes_unchanged` written into the results json.
- Outputs: `l180/{results_l180.json, census_dn_into.csv, census_dn_new.csv,
  run.out}`. No draft edit (manuscript is in owner-handoff state); the §4
  sentence is RECORDED ON THE CARD for whichever engine owns the draft.
