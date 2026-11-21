# L45a PREREG — Pugliese-style pruning screen on our intrinsic regime
Written 2026-11-12 23:5x, BEFORE any run. Amendment source: tick-61 (Nature
2026-10-28 digest; their stochastic pruning isolates E1=IN17A001 -> E2=INXXX466
-> I1=IN16B036 (+I2=IN19A007/E3=IN19B012 FANC variant), 86% of 4096 screens).

## Substrate (frozen, l32 arm A / l33-l44 lineage verbatim)
21,516 nodes / 2,977,920 signed edges; G=.01, BETA=2, D=.05 (inert, L35);
TAU .05, DT .01, BG .02, NOISE .01; SETTLE 400; free-run (no mech, no stop).
Seeds 11/22/33. ONE generator + ONE shared per-step noise tensor per seed
across all arms (L36 rule).

## Arms (activity clamp X[cells]=0 every step, ON [4000,9000), post [9000,11000))
- base — no clamp (anchor arm)
- c_E1 c_E2 c_I1 c_I2 c_E3 c_X464 — whole-type clamps, 6 cells each
  (X464 = INXXX464, DNb08's top intrinsic target + top-triad E1)
- c_core3all — E1+E2+I1 all neuromeres (18 cells; their named 3-loop, scaled)
- c_coreAll — all 6 named types (36 cells)
- c_E1T1 — E1 cells of T1 only (2 cells; per-leg modularity)
- c_coreT1 — E1+E2+I1 cells of T1 (6 cells; the per-leg 3-loop transplant)
- rnd1 rnd2 rnd3 — 3 random vnc_intrinsic types with the same 6-cell
  {T1,T2,T3}x{L,R} structure, rng seed 7, core types excluded (effect null)

## Pre-registered claims
- C0 anchors (base): per-seed f_pre in {0.80,1.44,1.42} +-0.05 Hz measured on
  [3400,4000); pre ratio >= 60; S base >= .38. (L33/L44 free-run attractors.)
- C1 mechanics: every clamp arm prefix [0,4000) BIT-IDENTICAL to base
  (max|d| 0.0 exactly); clamped cells' X max == 0.0 during the window;
  af in (0.01,0.9) all arms.
- C2 core-kill (the transplant question): KILL(if) median during-ratio < 5
  AND median S_during < .1 on >= 2/3 seeds. Registered prior: at 6-cell scale
  in-degree dilution makes a kill UNLIKELY; the deliverable is the measured
  effect either way. A kill on any arm triggers the contingency below.
- C3 ranking: per-arm effect = max(|dS|, |df|/1.0 Hz, log10(pre/during ratio))
  vs the rnd spread (max rnd effect = null bar). A named type "carries rhythm
  mass" if its effect > 2x the rnd bar on >= 2/3 seeds.
- C4 modularity: c_E1T1 / c_coreT1 effects vs their whole-type/3all parents.
- C5 restore-if-dies: post ratio >= 5 by end of [9000,11000) on every seed
  for arms whose clamp landed (C1) — any kill must be clamp-caused.
- Static context (interpretation, not gated): each clamped set's in-weight
  share onto Tr flexor/ext MN pools and total out-weight onto the cord.

## Contingency (only if a kill appears)
Re-run the killing arm + base on ONE l32 density-null rewired draw (same
protocol) to test wiring-specificity; full ladder is out of tick budget and
would be journaled as follow-up.

## Windows
during-metrics on [4100,8900) (5-s S windows stride 10, l44 form); post on
[9100,11000). f/ratio via rhythm2 (0.5-10 Hz band, peak/median power).

## ADDENDUM 1 (post-run, disclosed) — C0 anchor window resolution
Registered band (±0.05 Hz) was written at L33's 45-s-window resolution; this
run's pre window is 6 s (600 steps) -> FFT bin 0.167 Hz. Measured f_pre
{0.833, 1.50, 1.50} each land on the NEAREST BIN of the anchors {0.80, 1.44,
1.42} (bin edges .75/.917 and 1.417/1.583). C0 read as PASS at window
resolution; ratio>=60 and S>=.38 PASS unamended. (L34/L44 window lesson
again: register anchor bands on the measurement window.)

## ADDENDUM 2 (post-run, disclosed) — mediator probe
The coreAll-vs-E1 paradox (36-cell clamp inert, 6-cell E1 clamp maximal)
triggered an UNPLANNED 5-arm probe (base / c_E1 / c_I2E3 / c_E1I2E3 /
c_E1X464, 3 seeds, same machinery/noise, l45_probe.py 100 s). base and c_E1
reproduced the main run BIT-EXACTLY (r_dur/S_dur identical to 3 decimals =
anchor-grade); probe arms are P1-labeled like the rest.
