# L50 PREREG — always-driven-trajectory (written BEFORE any run)

Task (LANE.md ideas-24, verbatim intent): stepped frequency target 0.7 -> 1.4
-> 0.7 Hz with the entrain drive CONTINUOUSLY on (L48's spec line: keep the
drive ON when bilateral structure is needed), hops for the up-transition
(L39), NO stop segments. Score = tracking err + bilateral S duty + total
drive-on time (the cost metric). Compare against drive-budgeted variants:
how much extra drive time does structure-keeping cost?

P1-labeled descriptive lab demo. CPU-only. No live changes. Owner movement
law respected (lab demo, never app motion).

## Machinery (l39/l42/l49-verbatim)

- Substrate: MaleCNS cord 21,516 nodes / 2,977,920 edges, frozen l32 arm-A
  (g .01, beta 2, D .05 on DNg100), tau .05, DT 10 ms, RMAX 1, BG .02,
  NOISE .01, SETTLE 400, WIN 6000 (60 s), SEGB = [(0,2000,.7),(2000,4000,1.4),
  (4000,6000,.7)] = l39's exact task minus the stop.
- ONE generator per seed; X0 drawn first; ONE shared per-step noise tensor
  across arms (L36/l39 convention) — anchors depend on it.
- Global phase accumulator (never resets): settle 400 steps @0.7, then
  per-step @ target(k). Mech drive = amp * (0.5 + 0.5*sin(ph)).
- Hop volley: DNge046_L (2 cells), amp .5, steps [2000,2040) AND [4000,4040)
  (l39 fired at BOTH transitions — verified in l39 source line 146).
- Per-arm AMPA (amp vs k) and HOPA (bool vs k) tables computed BEFORE the
  run with asserts — no inline conditionals in the step loop (L39v1/L43v1
  lesson; also the L48 write-time exclusion lesson: ent carries NO hop).

## Arms (5) x seeds {11, 22, 33}

- free  : amp 0 always, no hops.             [anchor to l39 free]
- ent   : amp .3 all steps (incl. settle), no hops. [anchor to l39 ent]
- allw  : amp .3 all steps (incl. settle), hops at both transitions.
          = l39 ent_h046 = the ALWAYS-DRIVEN full stack. [anchor l39 ent_h046]
- duty58: per-segment 500-on/400-off cycles (on [c*900, c*900+500) within
          each segment, clipped at segment end; on at segment starts),
          hops at both transitions. Drive-on: 12.0 s/segment.
          The BUDGETED controller built on L49's 5-s slack (4-s gaps < 5 s).
- min5  : on only [seg, seg+500) per segment (5-s prime), hops at both
          transitions. The NAIVE budget controller: 15-s off spans = 3x the
          measured slack. Drive-on: 5.0 s/segment.

Settle (400 steps): amp .3 for ent/allw/duty58/min5 (l39 convention — its
settle carried mech drive for all non-free arms; required for bit-identity).
Drive-on totals (incl. settle): free 0 s, ent/allw 64.0 s, duty58 40.0 s,
min5 19.0 s.

## Gates (registered BEFORE the run)

- C0 ANCHORS (hard): free, ent, allw mm traces bit-identical to
  l39/traces.npz over [0,6000) (max|d| == 0.0); duty58, min5 prefixes
  bit-identical to ent over [0,500) (first off-step = 500).
- C1 WIRING: AMPA/HOPA asserts pass; af in (0.01, 0.9) every arm (L30
  probe); first_div vs ent: allw = 0 at k=2000 (volley), duty58/min5 = 500
  (first off step); volley_max > 1e-6 for all hop arms.
- A0 ANALYSIS ANCHOR: my per-segment pooled S / SL / SR on the l39
  measurement spans reproduce l39's stored segment values for free/ent/allw
  (|dS| < 5e-3) — proves my S code before new reads.
- P1 ALLW REPLICATION (from l39 stored): seg1 track_err <= stored+0.005
  per seed (.001/.002/.001 expected); seg2 ttl <= 2 blocks for >= 2/3 seeds.
- P2 DUTY58 SURVIVAL (the slack claim, from L49 gap5 HELD): per-seed
  overall duty_both(duty58) >= duty_both(allw) - 0.15. Descriptive
  companion (not gated): paired per-TS-sample duty diff vs allw, and
  duty split over on-window vs off-window TS samples.
- P3 MIN5 COLLAPSE (from L49: every gap >= 10 s collapses at ~5.5 s
  sustained): duty_both(min5) < 0.5 * duty_both(allw) in the seed mean;
  collapse latency into each 15-s off span (first sustained 5-s both-fail
  window starting >= off_start+499) lands 4-8 s past off_start for >= 2/3
  seeds. Tracking companion (descriptive): err on off-span blocks.
- COST TABLE (the deliverable): per arm — drive_on_s, per-seg track_err,
  ttl, duty_both (per-seg and overall, measurement spans = l39's
  [seg*2000+500, (seg+1)*2000), rolling 5-s windows step 10, both SL&SR
  >= .25), SL/SR medians, f_seg. Headline: marginal drive seconds per
  unit of bilateral duty across min5 -> duty58 -> allw.

## Verdict shape

Structure-keeping costs X s of drive per Y duty at this op point; the
budgeted duty58 arm either buys near-allw structure at 40/64 drive (slack
harvested — controller spec: duty-cycle the drive) or loses the S_L ceiling
faster than continuous drive does (the ceiling is re-build-limited, L49).
min5 expected to fail per L49 — its failure number IS the cost curve's
lower anchor. Any gate failure ships as a layered finding with the table.

## Pre-run disclosures

- No stop segments, no DNg88 drive anywhere in L50.
- Down-transition hop kept at 4000 (l39-verbatim for the anchor) though
  L42 found the down-shift re-locks without it; allw is defined as the
  l39-verbatim controller so anchors stay anchor-grade.
- Rolling 5-s S windows cannot isolate a 4-s gap (window shorter than gap
  needs); duty58 off-window reads are inherently blended — disclosed, and
  why P2 gates on per-segment duty, not off-window isolation.
