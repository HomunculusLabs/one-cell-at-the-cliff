# L63 PREREG — closed-loop-cord, slice A (registered 2026-11-14 02:1x, BEFORE rollouts)

Card: LANE.md ideas-30 L63. Minnick 2610.33881: senses-off motor replay 2.0% vs
94.0% closed-loop. All our cord experiments are open-loop on the sensory side.
Smallest honest closed loop at rate fidelity: delayed, attenuated copy of the
measured antagonist-pool motor mass fed back onto vnc_sensory mechano —
BRIDGE-level (L12 form), labeled body-level, NOT fake cord wiring.

## Design (machinery l59_ensemble.py verbatim + feedback arms)

- Substrate: male cord (21,516 nodes / 2.98M edges / beta 2 / G .01 / D .05
  DNg100), DT 10 ms, SETTLE 400, WIN 6000. One generator per seed, ONE shared
  per-step noise tensor, X0 drawn once and cloned per arm (L45b form).
- SEEDS8 = [11, 22, 33, 101, 105, 109, 111, 113] (subset of l45b census grid;
  n=8 disclosed — distributional reads get Wilson CIs, no point gates).
- Feedback: drive[mech] += GFB * m[k-DELAY] for k >= DELAY (zero during settle
  and first DELAY steps; zero-filled history). m[k] = mean X over the four Tr
  antagonist pools (fL,fR,eL,eR) of THAT arm at step k. GFB = 0.5, DELAY = 10
  steps (100 ms proprioceptive latency). Body-level, disclosed as such.
- ARMS (5, x 8 seeds):
  - hynohop — base schedule (500-on/400-off chop in 0.7 segs, fast seg
    continuous, no hops), NO feedback. = l55/l59 hynohop replica.
  - fbh — base schedule + true delayed self feedback (GFB .5).
  - sham — base schedule + SAME GFB but signal = donor seed's OPEN hynohop
    4-pool mean trace from l59/raw_l59.npz (same composition, same marginals,
    zero causal correlation with this arm's motor state). Donor = next seed
    in SEEDS8 (wrap). Separates "extra drive mass" from "loop content".
  - openL — LONG-GAP schedule: 500-on/700-off chop (7 s gaps, at/beyond the
    L58 open-loop 5-7 s hold edge; L49 single-prime collapse 5.49-5.69 s),
    fast seg continuous, no feedback.
  - fbL — long-gap schedule + true feedback (GFB .5).
- AMPA tables asserted at write time (on/off spans per family); DRIVE_ON
  reported per family (not asserted equal across families).

## Registered outcomes

- C0 (chain anchor, 17th): hynohop == l55/raw_l55.npz hynohop BIT-IDENTICAL
  (max|d| 0.0 on mm + fL/fR/eL/eR, seeds 11/22/33, full WIN).
- C0L: openL == l55 hynohop bit-identical for k < 900 (schedules share
  0-500 on / 500-900 off; divergence at 900).
- C0P (prefix): fbh, sham == hynohop for k < DELAY (feedback cannot act
  before its lag) — max|d| 0.0.
- C2 (feedback LANDS, L35 lesson): max|d(fbh - hynohop)| > 1e-3 over WIN.
  If not: wiring dead, all reads void, journal and stop.
- C1: settled active fraction in (0.01, 0.9) every arm (L30 probe).
- P1 (slack, base): duty_off(fbh) - duty_off(hynohop) >= +0.10 mean, where
  duty_off = fraction of S300 windows (300-step antagonist anticorrelation,
  both sides >= .25) FULLY inside >=400-step drive-off intervals.
  Specificity: sham lift < half the fbh lift (else it is mass, not loop).
- P1L (slack extension, long gaps): duty_off(fbL) >= duty_off(openL) + 0.10
  mean; and fbL per-seg lock err (l59 block form) not worse than openL by
  > 0.02 median (feedback must not break relock after gaps).
- P2 (tracking guard, base): per-seg err (l59 block form) median fbh <=
  max(0.01, 2x hynohop median) — no lock loss.
- P3 (fast-window toxicity, L52): seg2 duty (l59 500-window form) fbh -
  hynohop >= +0.10 mean = softening; sham smaller than fbh lift.
- Secondary (not gated): off-window antagonist mass std ratio fbh/hynohop;
  per-side SL300/SR300 decomposition in off windows (L46 form).
- Arnold-tongue widening (L34): NOT RUN this slice (frequency sweep is
  slice B if any P passes; disclosed).

Verdict rule (card): any of P1/P1L/P3 pass = first measured closed-loop
benefit, body-level, cited to Minnick. None pass with C2 green = the open-loop
assumption of the L57 cord controller spec is SAFE, cited, at (GFB .5,
DELAY 100 ms).

## Honesty notes

- n=8 seeds (census subset), Wilson CIs, no point-claim gates at this n.
- Feedback adds real input current during nominal "off" windows — that is the
  mechanism under test, not a confound; the sham arm carries the mass control.
- Donor traces come from l59 stored raw npz (deterministic open runs).
- All raw traces checkpointed to npz BEFORE analysis (L45a).
