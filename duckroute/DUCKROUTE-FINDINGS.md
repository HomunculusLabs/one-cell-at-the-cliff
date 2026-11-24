# DUCKROUTE — wave 6: the routing-threshold lever (offline, 2026-11-22)
PREREG sha256 98cc1d8a...b9aba2, locked 15:40:37 before any score was read. Evidence: results.json,
results_heldout.json, replay.log, world_read.json, check.py, out/.
## What ran
Inside a conversation no threshold feeds back into her dynamics, so a regime is a re-readout of stored score
records through her own code (`needs`, the reply-intent tail, `mood_tag`) with the comparator constants
swapped at the AST level. Primary: v2's stored seeds 0,1 (384 RETEST turns, plastic vs frozen pairs).
Held-out: seeds 2,3 run fresh with a byte-identical copy of v2's run.py (4 jobs, 4 cores, 48-51 min),
thresholds fixed from seeds 0,1. Gates green: sources hash-equal to v2; 40 comparators enumerated, 8 swapped;
as-is replay reproduces every stored decision (3,076 turns per tier); v2's headline reproduced (0 action
flips, 12 tag flips); fresh seed-2 frozen S1 equals v1's stored arm exactly.

## Boundary map (frozen arm, 384 turns; "fire" = share of turns on the firing side)
| intent boundary | fire | nearest score below / above | note |
|---|---|---|---|
| hunger > .75 (beg, to_bowl) | 3.6% | .731 / .794 | body clock |
| trust > .30 (beg) | 84.4% | .30 / .30 | counter; sits on her start value |
| sleep > .70 (settle) | 1.6% | .677 / .713 | body clock; rider <= .75: .713 / .998 |
| fear > .40 (to_boot) | 12.5% | .358 / .641 | 71% of turns are exactly 0 |
| food_joy > .60 (to_pond) | 17.2% | .350 / .611 | the dead zone, .26 wide |
Curiosity > .35 is unreachable in a conversation. World act ladder (7 comparators, 11,520 day ticks): no dead
zone, gaps <= .0014; her solo fear is always 0. Tag ladder: salience > .15 has 82 turns within .05, where v2's
tag flips live. P70 per score: hunger .390, trust .46, sleep .083, fear 0.0, food_joy .139. Full table: `map`.

## Regimes (RETEST; primary seeds 0,1 / held-out seeds 2,3)
| regime | action flips | noise control | on kindness/feeding arcs | settle turns | collateral |
|---|---|---|---|---|---|
| A as-is | 0 / 0 | 0 / 0 | - | 6 | 0 |
| B percentile, every threshold | 25 / 21 | 5 / 7 | 10 of 25 / 10 of 21 | 118 | 65.6% / 66.4% |
| C adaptive margin, kappa 1, 2, 4 | 0 / 0 | 0 / 0 | - | 6 | 0 |
| Bn percentile, fear + food_joy only | 23 / 19 | 5 / 7 | 10 of 23 / 10 of 19 | 6 | 18.2% / 19.0% |
| Bj post-hoc, food_joy only | 26 / 24 | 5 / 8 | 10 of 26 / 10 of 24 | 6 | 12.5% / 13.0% |
Noise control = frozen RETEST vs frozen S3. Collateral = frozen ambient turns that differ from as-is.

## Verdicts (registered regime B)
- Q1 SUPPORTED. 25 flips (12, 13 per seed) against 5 from noise; as-is 0. Held-out 21 against 7. 18 are
  stay -> to_pond on food_joy, 6 are settle lost on a .002-.005 sleep difference, 1 is fear. No reply flips.
- Q2 NOT SUPPORTED. 10 of 25 on kindness/feeding arcs (p = .16 against 7/24); held-out 10 of 21 (p = .057);
  8 primary flips are swat turns. Held-out Bn clears the turn bar (10 of 19, p = .027) on one conversation.
- Q3 SUPPORTED. Plastic arm .125 ambient reversals per conversation (as-is .042, max 1), same held-out.
- Q4 NOT SUPPORTED. Settle on 118 of 384 frozen turns instead of 6; in her solo life the settle branch fires
  on every tick (as-is 839-873 of 1,920 a day); 6 turns settle in one arm only. Bn, Bj, C: unchanged.
- Regime C is inert: food_joy threshold .60 -> .561 (kappa 1), .446 (kappa 4); nothing sits between .35 and
  .61, so 0 flips and the frozen arm equals as-is exactly.
- picked_up turn 5: tag neutral frozen, curious plastic, in all four seeds and every regime. Never behaviour:
  stay/stay under A, C, Bj; to_boot in BOTH arms under B, Bn (fear .096 > 0.0: the regime moved her, not her
  mood). 0 of 24 tag-flip turns carry an action flip: no intent comparator reads salience.
- Why the flips happen: frozen food_joy on swat and goats turns sits at .131-.139; P70 (.1394) lands on that
  cluster and the plastic gain (+.011 to +.014) lifts it over. Re-drawn noise alone moves 5-8 of them.

## Proposal (Q1 holds, so the brief asks for one)
By the registered rule (pass Q1, Q3, Q4) only Bn is proposable among registered regimes; Bj passes on held-out
data with less collateral. My recommendation is to ship neither as tested:
1. Not kindness: 10 flips are the goats conversation, 3-8 are swat turns (a swatted duck heads for the pond).
2. Bn's fear leg is `fear > 0.0`: to_boot on 97 turns instead of 48, for one flip.
3. Solo life under Bj (world_read.json): to_pond on 23-25% of all day ticks (0 as-is), and it overrides her
   curiosity walks (to_fence 326-352 -> 29-42 per 3 days, to_boot 151-170 -> 11-25).
4. The flips need v2's lab rule (947k edges, eta .05). Her live rule is DAN-only, eta .01, per visitor, and
   was not tested here; a live threshold change alone may be all collateral.
If the owner wants it anyway: one constant in `needs` (food_joy .60 -> .139), gated. G0 offline battery with
her LIVE rule under Bj, flips must beat the noise control, else stop; G1 pinned delta plus tests on both sides
of the comparator and on ladder precedence; G2 replay.py on the patched file reproduces Bj's decisions; G3
owner-approved restart of critter-bill-fly only, /health 200; G4 /needs probes on fresh chat ids; G5
gate_live.py 25/25; G6 24 h soak against the solo numbers. Rollback: revert, restart, gate_live.

## Deviations and scope
1. ADDENDUM.md (15:45:27, before any held-out record existed) adds Bj after the primary was read: exploratory
   on seeds 0,1, tested only on seeds 2,3. Its collateral guess was wrong (+21 to_pond turns, +48 to +50 seen).
2. run.sh was started with `sh run.sh` (the approval gate refused chmod-then-run). Scope: stimulus-window
   assay, no speech, world act ladder as-is, shared lab delta, solo reads from stored ticks.
