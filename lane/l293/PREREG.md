# L293 PREREG — frozen before any L293 measurement ran (tick 282, 2026-11-25 ~06:55 EST)

Question (card): the WORLD session's reward neurons idle at half-maximum. (a) is
the trust delta still growing; (b) what bounds it; (c) what does that do to her.

## Inputs (all read-only; sessions/ is never written)
- READ 1: lane/l293/world_20261125_0530.pt (sha256 18dda81a2db89bee…, source mtime 05:29:35)
- READ 2: lane/l293/world_20261125_063651.pt (sha256 107ca2ab263ec365…, source mtime 06:36:50) — 67 min later
- lane/archive/brain/*.pt (the L98 world-session snapshots, 2026-11-16 → 11-25) + manifest.jsonl + snap_*.json
- constants parsed FROM bridge.py / mood.py source at run time (never retyped); the night
  addition and the axis targets are re-executed as source slices or as the formulas at
  bridge.py L307-311 (stated as a re-implementation, gated where a gate exists).

## Already observed before this registration (description only, not registered)
From lane/l292/boot_ensemble.out (tick 280): world DAN rest 0.4938 vs fresh 0.0751;
dopamine 0.2958 vs 0.1484; GREET targets t_joy 1.029, t_sal 1.352 (fresh 0.1915, 0.7627).
From lane/l292/offline_delta.json: mass 2114, edge max 0.497. From the card: the world
day_log reads "sal": 1.0 on its events.
From reading bridge.py this tick (static, to be confirmed by an AST census in the run):
`_hebbian` is called only in `_reply_inside` (a visitor turn), never in world_tick; the
world session therefore gets additions only from `consolidate_night`.

## (a) GROWTH — registered rule
Statistics: mass = sum(plas_d), edge max, count of non-zero edges, on READ1 vs READ2
(bit-exact tensor compare, no noise in stored tensors) and on every archive snapshot.
- Two reads: GROWING if mass(READ2) > mass(READ1); FLAT if equal; FALLING if smaller.
- Archive (9 days): Theil–Sen slope of mass over snapshot pairs >= 6 h apart, sign test
  (exact binomial, two-sided). GROWING if slope > 0 and p < 0.01; DECAYING if slope < 0
  and p < 0.01; else UNRESOLVED. Report the per-date (America/New_York) median mass and
  the per-date last-to-last change beside it.
Prediction (written before the run): GROWING on both, in STEPS at night with flat
segments between (a night-only accumulator).

## (b) WHAT BOUNDS IT — registered rule
- Census (AST of bridge.py): the enclosing functions of every `_hebbian(` call and of
  the NIGHT_ETA / NIGHT_DOWNSCALE lines; distinct night_stamp dates in the manifest;
  event types in the world day_log; diary acts per date from the archive union.
- Balance, measured on the READ2 state with the night arithmetic: addition A = mass
  added by MAX_REPLAYS replays of the world session's own top-of-log events at
  DREAM_GAIN (pre-clamp and post-clamp), net = 0.98 x (mass + A_post) - mass.
  SIDE: NET_UP if net > 0, NET_DOWN if net < 0.
- Feedback: the same replays with NO delta active: A_world / A_nodelta (>= 1 means the
  delta inflates its own next addition).
- Forward projection (declared simplification: every night replays the same number of
  events; days are idle relaxation under the current night tonic; 2 seeds, 40 nights):
  report mass / DAN rest / pinned-edge count per night. BOUNDED if the mass at night 40
  is < 1.05 x the mass at night 20; else CAP-BOUND (report distance to 0.75 x n_edges).
  Counter-arm: no further night pass for 60 nights (pure 0.98 decay) — nights until
  DAN rest < 0.20, or NOT_REACHED.
No live rule change follows from this tick (card rule).

## (c) WHAT IT DOES TO HER — registered rule
Design: 16 seeds, paired; arms = world (stored X + stored delta) vs fresh (X = 0, no
delta); both settle 1,000 steps under the tonic for the darkness at run time (reported);
each event = the REAL MoodState.observe(0.2, event) from the session's READ2 axes, X
restored to the settled state and the noise re-seeded before every call. Events: greet,
peas, water, shiny, pet, goats, tin, slug (kind) + swat, rake (aversive) + quiet (no
channels = the offset alone). rest = the arm's own settled population means.
- C1 OFFSET_FLOOR: TRUE if t_joy(quiet | world) >= 0.90 AND t_sal(quiet | world) >= 0.90
  (seed means). (Partly observed for greet already: greet is description.)
- C2 AXIS_RESOLUTION: NO_RESOLUTION if, in the world arm, the spread (max - min over the
  8 kind events of the seed-mean) of food_joy after the event and of salience after the
  event are BOTH < 0.05, while in the fresh arm at least one is >= 0.10.
- C3 AVERSIVE_JOY: TRUE if food_joy right after "swat" >= 0.90 in the world arm.
- C4 INCREMENT (descriptive, no branch): per event, t - t(quiet) within arm, world vs
  fresh, paired over seeds (mean, SE, sign count).
- Gate (must pass before any (c) number is read): the source-slice targets reproduce the
  real observe() axes: round(min(t, 1), 3) == axes() after an observe from zeroed axes,
  for every (arm, seed, event).
Also reported: closed-form time for food_joy to fall below 0.35 with no further event
(90 s x ln(joy / 0.35)), per arm and event; the archive's mood tags per date.

## Status vocabulary
(a) GROWING / FLAT / FALLING (two reads) x GROWING / DECAYING / UNRESOLVED (archive)
(b) SIDE x BOUNDED / CAP-BOUND, with the census counts
(c) C1, C2, C3 TRUE / FALSE; a gate failure = NO_READ

## Amendment (pre-data: measure_l293.py had not been run once when this was written; 2026-11-25 06:51:14 EST)
- The file's true write time is 06:41:18 EST (the "~06:55" in the header was an estimate, ~14 min late).
- (b) Balance: A uses exactly MAX_REPLAYS replays (the registered text); the live 10% rule's own
  count for this log is reported beside it as description.
- (b) Counter-arm is RUN to 80 nights (1 seed); the registered read stays at 60 nights
  (NOT_REACHED if DAN rest has not fallen below 0.20 by night 60). Nights 61-80 are past the
  registered horizon: description only.
- (b) One added sensitivity arm, no branch: 1 replay per night, 40 nights (1 seed).
- Census also lists serve.py (where plas_d is loaded/saved): a superset of the registered census.
- (c) The target slice also names `lc` (the looming gate inside observe()); gated the same way.
