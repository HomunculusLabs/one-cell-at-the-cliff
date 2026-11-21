# L64 PREREG — echo-dose-phase-map (registered 2026-11-14 ~03:3x, BEFORE any rollout)

Card: LANE.md ideas-31 L64. L63 tested ONE point (GFB .5, DELAY 10 steps,
positive) and it hurt loop-content-specifically (phase, not mass). This maps
the small honest grid before the endgame loop borrows (or finally rejects)
body feedback.

## Design

- Machinery l63_closed.py verbatim (substrate n=21,516; l55/l59 hybrid-no-hop
  BASE chop schedule 500-on/400-off at 0.7, continuous 1.4 seg2; ENT_AMP .3;
  G .01 / BETA 2 / D .05; SETTLE 400 drive-free; shared-generator noise,
  one nz per step for all arms; echo OFF during settle, L36 rule).
- Grid: gain {.1, .25, .5} x delay {2, 5, 10, 20} steps (20/50/100/200 ms at
  DT 10 ms) x sign {+, -} = 24 fb cells + 1 open control (hynohop, no echo).
  Arm names g{05,025,01}_d{02,05,10,20}_{p,m}. Echo form (l63 verbatim):
  drive[mech,0] += GFB * SIGN * float(own_antag_mass[k - DELAY]), own mass
  recorded post-step; k is the WINDOW index (no echo in settle).
- Seeds 11, 22, 33 (the anchor seeds; 25 arms x 3 seeds = 75 rollouts).
  CPU-only. Raw npz checkpoint BEFORE analysis (L45a rule), incremental per
  seed so a crash costs <= 1 seed.
- Donor sham for the WINNER only (LANE card wording): l63 form, donor =
  l59 stored open hynohop, DONOR[s] = next of SEEDS8 (11<-22, 22<-33,
  33<-101). Run ONLY if a cell passes P1.

## Registered reads (discriminating windows, never pooled — L55/L63 lesson)

- OFF-WINDOW DUTY: fraction of off-gap S-points (w=300 windows, TS3 grid,
  4x400-step gaps) with S_L >= .25 AND S_R >= .25; lift = cell - open.
- SEG2 LOCK ERR: mean per-block dom-freq error in the fast window
  (block 500 steps, tol legacy LOCK_TOL .10; catastrophic flag > .5).
- SEG2 DUTY (fast-window structure), S_L/S_R off-gap medians, off-window
  antagonist amplitude std (mechanism read).

## Registered predictions + verdict rules

- P1 (the card's registered prediction — classical stabilizer): a NEGATIVE
  echo at SHORT delay (d=2 steps = 20 ms, in-phase inhibition) stabilizes:
  SOME gain g in {.1,.25,.5} with mean off-duty lift >= +.10 over open AND
  seg2 err median <= max(.01, 2 x open median) AND no per-seed seg2 err
  > .5 (no catastrophic lock loss). If P1 passes for any cell (any cell of
  the grid, reported which), the winner runs the donor sham and the claim
  additionally requires sham lift < 0.5 x fb lift (l63 form).
- P2 (map verdict, the closure rule): if NO cell in the whole grid clears
  the same conjunction, body-echo feedback is CLOSED at rate fidelity —
  L57's open-loop row stands with a MAP behind it, not a point.
- P3 (phase-not-mass carry): positive-sign harm deepens toward quarter-
  fast-cycle delays (d10/d20) vs short (d2), i.e. lift(d) is non-monotone
  in delay; negative-sign cells at short delay either stabilize (P1) or are
  rectified by the relu floor (dm ~ 0 off-window).
- FLOOR RULE (L35 class, registered): a negative cell with max|d mm| == 0.0
  vs open (beyond its delay prefix) NEVER ENTERED the dynamics — verdict
  for that cell is FLOOR-BURIED, not "failed to help". dm probes read on
  every cell before any verdict.

## Registered anchors (enumerated keys only; diagnostics separate)

- C0: grid hynohop bit-identical to l55/raw_l55.npz — keys mm|fL|fR|eL|eR
  _hynohop_{11,22,33}, window [0,6000), max|d| == 0.0 (18th consecutive
  chain anchor).
- C0x (cross-run wiring replication): grid g05_d10_p bit-identical to
  l63/raw_l63.npz fbh arm — keys mm|fL|fR|eL|eR _fbh_{11,22,33} max|d| == 0.
- C0P: every fb arm bit-identical to hynohop on [0, DELAY) and first
  divergence at exactly k == DELAY.
- C2: echo lands — max|d mm| > 1e-3 for every POSITIVE cell; negative cells
  either land or are flagged floor-buried (P3 rule).
- C1: settled active fraction in (0.01, 0.9) every arm.

Expected budget: ~4-6 min CPU. No live changes; research only.
