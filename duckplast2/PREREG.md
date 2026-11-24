# PREREG — duck plasticity v2 (routing-aimed), offline lab

Locked 2026-11-21 before any dynamics were stepped for this experiment: no
pilot, no calibration, no timing run. What I did look at before locking,
all of it static or prior: her live source (bridge.py, mood.py, senses.py,
brain.py, puddle/engine.py — read-only), the v1 folder (duckplast/, incl.
its stored frozen-arm results), and a static census of the graph file
(cell and edge counts, |w| quantiles; torch.load only, zero steps).
SHA-256 of this file is written to PREREG.sha256 and asserted by run.py.

## 0. Where her decisions are actually made (static reading)

- Reply intent = `INTENTS[sit]` lookup on the keyword router's situation,
  plus one override (`beg` if intent is stay, no event, hunger > .75 and
  trust > .30). Hunger and trust are body clocks / event counters. No
  neuron feeds this.
- Ambient intent = `bridge.needs()` ladder: hunger>.75 (&sleep<=.75) ->
  beg/to_bowl; sleep>.70 -> settle; fear>.40 -> to_boot; food_joy>.60 ->
  to_pond; else stay. Neural-coupled comparator inputs: fear (LC looming +
  octopamine means), food_joy (serotonin + DAN means), and sleep only
  through the salience shave (dopamine mean).
- Mood tag = `mood.mood_tag()` ladder on fear .25/.50/.08, salience
  .30/.15, food_joy .35/.60, plus body axes.
- World-tick act ladder: fear>.40, sleep>.75, hunger>.85/.70, curiosity,
  food_joy<.15.
- Motor readout `cx_intent`: continuous, DN population mean vs CX_BASE.

## 1. Plastic cell set, rule, band (exact)

Postsynaptic target cells (5,499 of 139,255), all CSR entries INTO them
(946,999 of 15,091,983 edges, 6.3%; 16.0% inhibitory):

- FEAR = LC looming probe (762) U octopamine cells (259) -> 995 cells,
  238,989 input edges. Population sign s = -1.
- JOY/SAL = serotonin (2,347) U dopamine (945) U DAN probe (331; 330
  already in dopamine) -> 3,293 cells, 398,951 edges. s = +1.
- MOTOR = descending neurons (1,303) minus the 92 already in the sets
  above -> 1,211 cells, 309,059 edges. s = +1.
  (Precedence FEAR > JOY/SAL > MOTOR for cells in two sets.)
- Body-only comparators (hunger, trust, curiosity) have no cells to aim
  at and are untouched.

Rule (three-factor, event-gated, signed, weight-proportional). After each
routed turn that carries a sensory event, with x = rates at the end of the
turn's observe call (window assay, section 2):

    d_e += eta * v(event) * s(post) * |w0_e| * x_pre * x_post
           only where x_pre > .05 and x_post > .05
    d_e clipped to [-0.20*|w0_e|, +0.20*|w0_e|]      (band: <=20% drift)

v = +1 for her own KIND_EVENTS tuple (pet, greet, goats, peas, tin, water,
shiny, slug), -1 for her MEAN_EVENTS tuple (swat, hose), 0 otherwise
(rake, umbrella, hold, no event). eta_day = 0.05. Positive d adds drive
(excitatory entries grow, inhibitory entries weaken); no sign flips are
possible inside the band. Applied through her brain's native
`active_delta` hook; the weight matrix itself is never written. The
native DAN-only `_hebbian` is stubbed out in both arms (v1 convention).
Frozen arm: eta = 0 everywhere, same seeds, same code path.

Night consolidation: lab port of `consolidate_night` on a simulated
clock — same gate (dark >= .6, sleep > .6, once per sim date, same-date
events only), same selection (top decile by dopamine at acquisition, >=1,
<=5 replays), DREAM_GAIN .3, 20 native steps per replay, writes for
KIND events only at eta_night = 0.10 (her 2x ratio), then one global
x0.98 downscale of d per pass. Same band.

## 2. Assay

v1's stimulus-window assay, unchanged for comparability: the first 20
native 10-ms steps of every observe call run neurally, X is held for the
rest; mood/body clocks integrate full time. Original 24 scenarios x 8
turns, original order and gaps, noon forced. Each conversation is a fresh
visitor state (mood, router, activity re-seeded); only d persists.
Speech generation is cut exactly as in v1 (source-sliced `_reply_inside`).
Ambient intent comes from the source-sliced native `needs()`.

Timeline per arm and seed: S1 battery -> day 1 -> S2 battery -> day 2 ->
S3 battery -> day 3 -> RETEST battery with updates off in both arms, plus
a one-turn quiet probe ("the clouds are grey").

A "day" = 1,920 world ticks at 45 s on a persistent world state, hour
advanced per tick from 12:00, using her source-sliced `world_tick` and
`_dabble` with lab stubs for wall-clock, diary and consolidation (nothing
is written to her sessions dir). Forage `water` events use the 20-step
window; idle ticks use K_idle steps. Battery events are appended to the
world day log (her 100-entry cap applies).

Noise keys: S1 uses v1's key crc32("name|seed") so the frozen S1 arm can
be compared against v1's stored frozen arm (reported as an anchor, max
abs diff; not a gate). Later sessions use crc32("name|seed|S<k>"). Arms
are paired on every key. Seeds 0,1,2.

Budget ladder, resolved once by a timing-only benchmark of the unmodified
native step AFTER this lock (reports ms/step only): R0 = 3 seeds, K_idle
2; R1 = 2 seeds (0,1), K_idle 2; R2 = 2 seeds, K_idle 0. Take the first
rung whose projected wall is <= 55 min; execution mode (N single-thread
processes on 4 cores vs fewer 4-thread processes) = whichever projects
faster. CPU <= 4 throughout, GPU not used.

## 3. Logged per turn (full precision)

fear, food_joy, salience, sleep, hunger, trust; raw peaks lc, dan, kc,
oct, ser, dop, dn; cx move/turn/arousal; sit, event, reply intent,
ambient intent, mood tag. Per world tick: act and axes.

Intent scores = the comparator inputs as signed margins: s_pond =
food_joy - .60, s_boot = fear - .40, s_settle = sleep - .70, s_beg =
min(hunger - .75, trust - .30), s_move = cx move; mood margins on
fear .25/.50, salience .15/.30, food_joy .35/.60.

Near-threshold turn (for a decision class) = a turn whose FROZEN RETEST
value of any comparator input of that class lies within +-.05 of its
boundary. Action class boundaries: hunger .75, trust .30, sleep .70/.75,
fear .40, food_joy .60. Tag class boundaries: fear .08/.25/.50, trust
.15/.20/.55, salience .15/.30, hunger .75/.90, food_joy .35/.60,
sleep .75.

Noise floor ("frozen control" for flips and shifts) = frozen RETEST vs
frozen S3: same weights, re-drawn noise.

## 4. Predictions

All paired, plastic minus frozen, same seed and noise key, at RETEST
unless stated. "Supported" needs the band on the seed mean AND the right
sign in every seed.

Q1 (intent-score shift on kindness arcs). On the four kindness arcs
(kindness_slow, goats, slow_trust_build, pet_shy_first; 32 turns/seed),
mean paired shift in food_joy (the s_pond input) is in [+0.002, +0.08].
Secondary, same turns: salience shift in [+0.005, +0.12]; cx move shift
> 0. Outside the band on the high side = direction supported, band
missed. Forecast: 75% for the primary.

Q2 (near-threshold flips > frozen control). N = near-threshold turns
whose decision differs plastic-vs-frozen; C = the same turns differing
frozen RETEST vs frozen S3. Supported iff N > C, N >= 3 over seeds (>= 2
on a 2-seed rung), and N > 0 in at least 2 seeds.
- Q2-any: decision = reply intent, ambient intent or mood tag. This is
  the brief's Q2. Forecast: 80%.
- Q2-action: decision = reply or ambient intent only. Forecast: 40%. My
  reading is that the neural-coupled action comparators are either
  body-set or saturated; the only cheap flips I can see are stay <->
  to_pond where food_joy passes .60.
- Structural: reply-intent flips = 0 over all turns and sessions (no
  neuron feeds it). Fear on rake/umbrella turns stays 1.0 in both arms
  (LC cells are the injected channel and saturate).

Q3 (v1 mood-tag shift replicates and strengthens). picked_up turn 5 is
(neutral, low) frozen and (curious, low) plastic at RETEST in every seed;
and the paired salience shift on that turn is larger at S3 than at S1 and
larger at RETEST than at S1 (seed means). Forecast: 70%. Not registered:
whether the flip already shows in S1 (partial drift by conversation 14).

Q4 (no forgetting). All four must hold:
(i) every reply and ambient decision in the bedtime scenario identical,
with at least one positive settle, and every `night` turn in the battery
identical; (ii) quiet probe |d hunger| <= .01 and |d sleep| <= .01, and
bedtime per-turn |d sleep| <= .02; (iii) every rake/umbrella turn keeps
reply intent to_boot with fear >= frozen - .02; (iv) nest-tick count per
day within +-5% of frozen and at least one consolidation pass per night
in both arms. Forecast: 80% ((iv) is the fragile one — world rng streams
de-align after the first act flip).

## 5. Reporting commitments

- Drift census per population after every session and day: changed, at
  cap, mean/max relative drift, sign and band checks, frozen drift = 0.
- Score-shift distributions (mean, median, share of turns > 0, noise
  floor) for every arc class, not just kindness; aversive arcs are the
  specificity read.
- Which events each night pass replayed and wrote. From static reading
  her date-stamp gate may let a small-hours pass block the next evening's
  pass; reported as observed, not tuned around.
- World-act histograms per day and first divergence tick: exploratory.
- Headline rule: "she chose differently" only for a reproducible ACTION
  change (Q2-action) at RETEST with updates off. Tag-only change = she
  reads differently and acts the same. A null is reported as a null.
- No tuning, no seed selection, no re-runs with other eta. Any deviation
  forced by a bug is listed in the findings with the reason.
- No live rollout; if results warranted one it would be a separate
  proposal.
