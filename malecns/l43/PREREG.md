# L43 PREREG — stop-dose-resurrection (written before any run)

L42 left two unmeasured numbers on the {entrain, hop, stop} stack: (1) the
entrained-release regime's KILL DOSE (does any stop duration x amp reach the
L40 intrinsic-cord kill level, rhythm2 ratio < 5 — or is the entrained cord
stop-resistant because entrain re-hosts through the release?); (2) RESURRECTION
latency — after a stop that DOES park the cord, steps from stop-off to
persistent rolling S >= .25 under entrain amp .3 ALONE (l42's C4 was scoped
re-lock-not-resurrection precisely because nothing died; L41/L42 say repair is
post-disturbance).

## Substrate + task (l42-verbatim, DT 10 ms)

Frozen L32 substrate (g .01 / beta 2 / D .05; 21,516 nodes / 2,977,920 edges
asserted). settle 400 @0.7 Hz, then per-arm target schedule t_a(k):

- [0, 2000):    0.7 Hz — entrain amp .3
- [2000, 4000): 1.4 Hz + hop volley @2000 (DNge046_L amp .5, 40-step square,
  l39/l42 EXACT form) — ANCHOR REGION, drive identical for every arm
- [4000, 4000+dur): STOP for dose arms (target 0, mech OFF, DNg88 tonic amp
  in {-4, -8, -12}); `entx` keeps target 0.7 (drive ON) with DNg88 -12 x 30 s;
  `ent` never gets a release (target 0.7 from 4000 on)
- post (stop-off -> 11000): 0.7 Hz entrain for every arm, NO hop (pure
  resurrection), WIN = 11000 for all arms

dur in {1000, 2000, 3000} steps (10/20/30 s) -> arms d10a4..d30a12 (9) + ent
+ entx = 11. Per-arm phase accumulator = l42 recursion with t_a; ONE generator
per seed, ONE shared per-step noise tensor (L36); X0 draw + order identical to
l39/l41/l42 (bit-identity requirement). af assert after settle per arm.

## Pre-registered gates

- C0 ANCHORS (must PASS, max|mm diff| == 0.0 vs l42/traces.npz):
  all 9 dose arms + entx vs l42 `stack` over [0,4000);
  d10a8 vs l42 `stack` over [0,5000) (same stop window);
  ent vs l42 `ent` over [0,4000).
- C1 STOPS LAND: min DNg88 X during stop < 0.5 (un-pin) for all 9 dose arms.
- C2 KILL DOSE EXISTS: some cell with LATE-STOP rhythm2 ratio < 5 (L40 kill
  level; late-stop = last 500 steps of the stop window) on >= 2/3 seeds.
  Deliverable = the full 3x3 dose table (ratio, depth, kill latency in-stop).
- C3 DOSE ORDERING (descriptive, no hard gate): median late-stop ratio at -12
  < at -4, separately at each duration; report all three comparisons.
- C4 RE-HOST TEST (deepest dose 30 s / -12): entx (release + drive ON)
  late-window ratio >= 5 on >= 2/3 seeds AND during-release rolling-S median
  >= .25 on 3/3, while d30a12 (release + drive OFF) late < 5 on >= 2/3 =>
  "entrain re-hosts through the release" (L34 reflex-arc mechanism active
  DURING the release). Both killed => the 10-s stop-resistance L42 saw was
  basin memory / insufficient dose, not re-hosting. ent (no release) ratio/S
  reported as the reference row.
- C5 RESURRECTION: for every PARKED cell (late-stop ratio < 5): steps from
  stop-off to persistent rolling S >= .25 (l42 recovery form: S[t] >= .25 AND
  min of next 250 samples >= .25) under entrain .3 alone; None = does not
  resurrect within the post window. Deliverable = latency table; the number,
  not a gate, is the ship.

## Analysis notes

rhythm2 band [0.5, 10] Hz; rolling S = 500-step window every 10 steps on
L/R-summed Ti flexor vs extensor traces (l42 form); kill latency = first 1-s
block inside the stop with ratio < 5. P1-labeled descriptive lab demo, no
WHEN-claims beyond L21 bounds; CPU-only; no live changes.

## Addendum (post-v1, pre-verdict — disclosed)

v1 BUG: `target_a` collapsed the entx case — entx ran with drive OFF during
the release and came out BIT-EQUAL to d30a12 (the C4 arm never existed).
Same class as L39 v1 (drive wiring leaked into a control arm; third instance
— lesson recorded). Fix: explicit DRIVE_THROUGH set; entx re-run LONE on the
same per-seed noise stream (raw.npz checkpoint holds the 11 v1 arms); anchor
entx-vs-l42 stack [0,4000) max|d| = 0.0 proves the lone-run stream replicates
exactly (L41 instrument). C4 evaluated on the fixed arm.
Analysis-scope notes (also disclosed): `kill_latency` can catch TRANSIENT 1-s
dips (entx seed 11: 16 s) that recover — read it with late_ratio, never alone.
