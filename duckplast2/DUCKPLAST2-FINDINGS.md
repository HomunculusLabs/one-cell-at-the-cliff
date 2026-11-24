# DUCKPLAST2 — plasticity v2, aimed at the routing layer (offline, 2026-11-21)

PREREG sha256 367f6339...06679d, locked 20:26:48 before any step. Sources
identical to v1 (SOURCES.sha256). Evidence: score.log, scores.json, out/.

## What ran

Three-factor signed rule on every synapse INTO the cells that feed her mood
axes and motor readout: 946,999 edges onto 5,499 cells (FEAR 995, JOY/SAL
3,293, MOTOR 1,211), eta 0.05, band 20% of |w0|, through her brain's native
`active_delta` hook. Frozen arm same seeds. 2 seeds x 2 arms; each = S1
battery, day 1, S2, day 2, S3, day 3, RETEST with updates off. 24
conversations x 8 turns per battery; a day = 1,920 world ticks at 45 s with
her own `world_tick`, forage and night-pass logic on a simulated clock.
43k native steps per job, 45-49 min each, 4 cores, no GPU.

Anchor: frozen S1 reproduces v1's stored frozen arm exactly (192/192 turns
per seed, labels and axes, max abs diff 0.0). Routing identical across
arms in every session. Frozen drift 0. Weight matrix never written.

## Predictions vs outcomes (RETEST, plastic minus frozen, paired)

- Q1 SUPPORTED. Kindness arcs: food_joy +0.0170 per turn (band +.002 to
  +.08; both seeds +0.0170; 100% of turns positive). Salience +0.046 (in
  band), cx move +0.103. Frozen noise floor: 0.0003 / 0.0005 / 0.002.
  Grows by session: food_joy .0086, .0142, .0161, .0170.
- Q2-any (the brief's Q2) SUPPORTED: 12 near-threshold flips (6 per seed)
  vs 0 from re-drawn noise. Every one is a mood tag, neutral -> curious.
- Q2-action NOT supported: 0 reply-intent and 0 ambient-intent flips in
  384 RETEST turns, and 0 in all 1,536 paired turns across sessions.
- Q3 SUPPORTED. picked_up turn 5 is neutral frozen, curious plastic in
  both seeds at every session; the salience gap grows .0139, .0154, .0164,
  .0175. Tag flips per seed by session: 2/1, 5, 5, 6.
- Q4 SUPPORTED. Bedtime and all night-turn decisions identical (8 settle
  positives); quiet probe hunger/sleep differences 0.0; bedtime sleep
  within 0.004; all 24 rake/umbrella turns keep to_boot at fear 1.0; nest
  ticks within 5% on all six days; a night pass fired every night.
- Structural predictions held: reply intent never moved; looming fear is
  pinned at 1.0 in both arms.

## Drift census (seed 0; seed 1 matches to the third decimal)

Changed edges 687k after S1, 726k of 947k at the end. Mean relative drift
2.2% -> 3.1% -> 3.7% over the three sessions (JOY/SAL +6.4%, MOTOR +2.7%,
FEAR -0.5%). At the cap after S1/S2/S3: 63.7k / 78.3k / 88.4k; each night's
x0.98 downscale pulls them back to 19.6%. Max drift 20.0%, no sign flips.

## Why the scores moved and the actions did not

- The only neural-coupled action comparator she can reach is food_joy > .60
  (to_pond). Frozen food_joy is bimodal (seed 0): 159 of 192 turns at or
  below .35, 33 at .61 or above, nothing between. The largest shift plasticity bought
  was +0.083. No turn sits where a flip is available.
- fear > .40 is set by the injected looming cells (saturated) or by body
  decay; sleep > .70 is body-set in conversation; hunger and trust have no
  neurons behind them. Reply intent is a lookup on the keyword route.
- The shift is not kindness-specific. Every arc class moved up: anger arcs
  +.011 food_joy and +.086 cx move; swat move .750 -> .905. This rule buys
  a general gain on appetitive and motor readouts.
- One fear effect: the shiny-gift arc's octopamine-fed fear fell .187 ->
  .147 (arc mean -.034).

## Exploratory: her solo life

Day 1 is a clean paired comparison until the arms first differ. In both
seeds the first difference is at dusk: the frozen duck's ambient intent
turns to settle at tick 541 / 537, the plastic duck's 2 / 1 ticks later,
and she nests later (seed 1: 2 ticks; seed 0: she forages first). Cause:
higher salience at forage events shaves her sleep axis by about .011.
After that the world rng streams de-align, so later days are counts only:
nest ticks lower in all six day-pairs, mean -1.3%. Two seeds; not a
registered endpoint.

## Side finding in her live code (read-only, not touched)

From night 2 on, `consolidate_night` never replays the day. The small-hours
pass (a post-midnight forage) stamps the date, which blocks that evening's
pass; the day's events are then dropped as stale at midnight. Sim: night 1
replayed swat, swat, water x3 at 18:36, every later pass replayed one
`water` at 00:0x. Her live diary archive shows the same: 11-16 18:47, then
00:01-00:08 "water" passes every night since. Wants an owner decision.

## Deviations and scope

1. Budget: no rung projected under 55 min; R2 (2 seeds, idle ticks hold X)
   projected 56 and was taken. Seeds 0 and 1 only.
2. A second lab lane loaded the box during S1; throughput only.
3. A mechanical smoke run (out/smoke_*) happened after the lock; nothing
   was changed after it. Scorer had one print bug fixed before final use.
Scope: stimulus-window assay (first 200 ms of each observe is neural), no
speech generation, shared delta across visitors (live deltas are
per-visitor), two seeds whose noise is ~50x smaller than the effects.

## Verdict

She reads differently and moves with more vigor; she does not pick a
different action in conversation. No live rollout proposed. The next lever
is the comparator placement, which is a routing-code question for the
owner, not a plasticity one.
