# PREREG — duck wave-6: the routing-threshold lever (offline lab)

Locked 2026-11-22 before any score value from the v2 records was read for
this experiment and before any step was run. What I looked at before
locking, all static or prior summaries: BRIEF_routing.md; her live source
(bridge.py, mood.py — read-only); duckplast2's PREREG, FINDINGS, run.py,
run.sh, RUNG.md; scenarios.py; the KEY NAMES and lengths of the stored v2
json files (no values); the lab skill notes. From the v2 findings I know
these summary facts: frozen food_joy is bimodal (159 of 192 turns <= .35,
33 >= .61, seed 0); plastic shifts food_joy +.017, salience +.046, cx move
+.10 on every arc class; 0 action flips and 12 tag flips at RETEST under
the live thresholds. I have not seen any per-turn distribution.
SHA-256 of this file goes to PREREG.sha256; every script asserts it.

## 0. Design in one paragraph

Inside a conversation no threshold feeds back into her dynamics: reply
intent, ambient intent and the mood tag are read out after the turn's
neural window, and nothing downstream reads them (speech is cut, as in
v1/v2). So the v2 runs already hold the complete score record under "the
SAME plasticity v2 used", and a regime is a re-readout of those records
through HER routing code with the comparator constants substituted at the
AST level (source-sliced `needs`, the intent tail of `_reply_inside`, and
`MoodState.mood_tag`/`axes`; no port by hand). Primary data: the stored v2
records, seeds 0 and 1, both arms (duckplast2/out/, read-only). Held-out
tier: seeds 2 and 3 run fresh with a byte-identical copy of v2's run.py
(sha256 asserted equal), K_idle 0, 1 thread each, 4 jobs on 4 cores.
The world-tick act ladder stays as-is in every regime (section 1), so the
plastic trajectory is the same in all regimes by construction.

## 1. Boundary inventory and scope (static)

Enumerated by the harness from the AST (every Compare against a numeric
constant or module constant), not hand-picked. Expected inventory:

INTENT class — in placement scope (conversation-facing `intent` field):
- reply beg override: mood.hunger > .75, mood.trust > .30 (unrounded)
- needs ladder: a.hunger > .75, a.sleep <= .75 (rider), mood.trust > .30,
  a.sleep > .70, a.fear > .40, a.food_joy > .60 (a.* rounded to 3 dp),
  curiosity > CURIOSITY_GATE (.35; unreachable in a conversation session:
  no curiosity and no curious_at — mapped as degenerate, left as-is).

Mapped but NOT placed, with reasons:
- world_tick act ladder (fear > .4, sleep > .75, hunger > .85 / .70,
  curiosity > .35, fear > .2, food_joy < .15): her solo self-care policy.
  Its scores have their own world-life distribution, not the 24-arc
  battery's; mapped on the stored frozen day ticks.
- mood_tag ladder (mood.py; fear .25/.50/.08, trust .15/.20/.55, salience
  .30/.15, hunger .75/.90, food_joy .35/.60, sleep .75): outside
  bridge.py, and her talking layer was trained on these tag semantics.
  Mapped on the battery; as-is in every regime.
- consolidate/dream gates (darkness .6, sleep .6/.8) and cx_intent (no
  comparator; continuous): listed only.

Map statistics per boundary (frozen arm, S1 and RETEST, seeds 0+1 pooled):
n, quantiles (0,10,25,50,70,75,90,100), share of turns on the firing side,
the threshold's percentile rank, the nearest score below and above the
threshold (the dead-zone gap), and the count within +-.05.

## 2. Regimes

Calibration set for every percentile: frozen arm, S1 battery, seeds 0 and
1 pooled (384 post-turn values, full precision), numpy linear-interpolated
70th percentile. Evaluation is on RETEST (different noise keys).

- A  as-is control: live constants.
- B  percentile placement (the brief's regime b): every placed threshold
  = P70 of its own score. Comparators that share a score share the value
  (hunger: reply and needs; trust: reply and needs; sleep: rider and
  settle). Applied as full-precision floats, comparators unchanged.
- C  adaptive margin (the brief's regime c), on the as-is base:
  thr = thr_asis * (1 - kappa * D), D = mean absolute relative drift of
  the population that feeds the score, read from that arm's census at the
  stage (RETEST: census R; secondary sessions: the census at the START of
  that battery, 0 for S1). fear <- FEAR, food_joy <- JOY_SAL. hunger,
  sleep, trust, curiosity are body clocks with no plastic edges behind
  them: D = 0, unchanged. kappa = 1 is primary (relative threshold drop =
  mean relative synaptic drift, no free parameter). The frozen arm has
  D = 0, so frozen-under-C equals frozen-under-A.

Declared secondaries, all reported, none selected:
- Bn: percentile placement on the neural-coupled comparators only (fear,
  food_joy); hunger, sleep, trust as-is.
- C2, C4: kappa = 2 and 4 (dose rungs).
- BC: B thresholds with the kappa = 1 margin.

## 3. Definitions

Paired = plastic vs frozen, same seed, session, conversation, turn,
same regime. Registered endpoint = RETEST (updates off), seeds 0+1,
384 turns. Sessions S1-S3 are secondary (growth).

- Action flip: reply intent or ambient intent differs within a pair.
  Near-threshold = the frozen value of some placed-class score lies
  within +-.05 of that regime's boundary for it (either arm's boundary
  under C). Attributed to the comparator(s) whose outcome differs.
- Noise control: frozen RETEST vs frozen S3 under the same regime.
- Collateral: share of frozen RETEST turns whose ambient (and separately
  reply) intent under the regime differs from regime A.
- Reversal (flip-flop): in one conversation's ambient sequence, an index
  t with A[t] == A[t+2] != A[t+1]. Rate = mean reversals per
  conversation (8 turns).
- Kindness/feeding arcs = scenarios with arc label kindness or feeding
  (7 of 24: kindness_slow, goats, slow_trust_build, pet_shy_first,
  feeding_joy, water_rain, tin_tease_no_food); base rate 7/24.
- Settle turn = ambient intent settle. World settle read (stored days):
  a tick reaches the settle branch iff not (hunger > thr_h and sleep <=
  thr_rider) and sleep > thr_s, on the stored tick axes.

## 4. Predictions (the brief's Q1-Q4, operationalised)

Q1. Under B, near-threshold action flips N >= 10 (pooled), N > the noise
control, and N > 0 in each seed; under A, N <= 1 (v2 found 0).
Forecast 65%. Note: P70 puts 30% of frozen turns on the firing side of
every placed comparator by construction, so flips need only local score
density at P70. Q1 alone is not evidence that B is a good lever; Q2-Q4
and collateral carry that.
  Same table for Bn (forecast 60%), C (forecast 10%: a ~.04 margin
  against a ~.25 dead zone), C2, C4, BC.

Q2. Under B, the share of action flips on kindness/feeding arcs is
>= .50 and the one-sided exact binomial tail against 7/24 is < .05
(turn level; the conversation-level count is reported next to it since
turns in one conversation are not independent). Forecast 35% — v2's
shift was not kindness-specific. Not evaluable if N = 0.

Q3. Under B, plastic arm, RETEST: mean ambient reversals per
conversation < 1.0. Forecast 70%. Reported next to it: regime A's rate,
the frozen arm, the max per conversation, conversations with >= 2, and
toggles of the paired flip indicator.

Q4. Settle/sleep behaviour unchanged, three parts, all required:
(i) within-regime, RETEST: every bedtime-scenario turn and every `night`
turn has identical reply and ambient intent in both arms, at least one
settle positive survives, and no turn anywhere has settle in exactly one
arm; (ii) cross-regime, frozen RETEST: the set of settle turns equals
regime A's; (iii) world settle read, frozen arm: settle-branch tick
count per day within +-5% of regime A's on all six seed-days.
Forecast for B: 15%. I expect (ii) and (iii) to fail: the sleep
threshold lands inside the daytime cluster and settle fires on a large
share of noon turns. For Bn, C, C2, C4 parts (ii) and (iii) hold by
construction (hunger, sleep and trust comparators are untouched and sit
above fear and food_joy in the ladder) and (i) reduces to v2's Q4; Q4 is
a live test only for B and BC.

Structural (all regimes): reply-intent flips = 0 (hunger and trust are
arm-identical body clocks); frozen-under-C decisions equal regime A.

Item 4 log, every regime, each seed: picked_up turn 5 (frozen tag, plastic
tag, reply and ambient intent per arm, margins) and, for each of v2's
RETEST tag-flip turns, whether the regime also shows an action flip there.

## 5. Gates (halting unless stated)

G1 live sources hash-equal to duckplast2/SOURCES.sha256 and the graph hash
   in the v2 records.
G2 AST audit: every numeric Compare in the scoped functions is matched to
   an inventory entry; unmatched or missing halts.
G3 with regime A constants the replay reproduces the stored reply intent,
   ambient intent, mood and level on 100% of stored turns (4 files x 4
   sessions x 192, plus the quiet probe).
G4 regime A re-readout reproduces v2's stored headline: 0 action flips
   and 12 tag flips at RETEST.
G5 (held-out tier only) duckroute/run.py sha256 == duckplast2/run.py;
   fresh seed-2 frozen S1 equals v1's stored seed-2 frozen arm (labels,
   fear, hunger, sleep, body trust; max abs diff 0.0). Seed 3 has no
   stored reference and rides on the same certified harness.

## 6. Held-out tier

Seeds 2 and 3, thresholds frozen from the seed-0/1 calibration, same
definitions, Q1 bar >= 10 over the two seeds. Reported separately as
replication; it cannot rescue or overturn the primary verdicts. A run cut
by the wall is scored only if its RETEST battery completed.

## 7. Reporting commitments

- Every regime gets the full Q1-Q4 table, collateral, attribution by
  comparator, flips by arc class and by session.
- If Q1 holds, a live-rollout PROPOSAL is written (brief). What it may
  propose is bound by the data: a regime is proposable only if it passes
  Q1, Q3 and Q4; among those, the lowest collateral is named. If none
  passes, the proposal section says so and states the owner decision
  instead. A proposal is a document; nothing live is touched.
- No tuning after lock: no other percentile, no other kappa, no other
  calibration set, no re-runs. Deviations forced by bugs are listed.
- CPU <= 4, no GPU, wall <= 2.5 h from 15:35. Writes only in duckroute/.
