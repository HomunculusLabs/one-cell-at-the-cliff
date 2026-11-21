# L60 PREREG — side-asymmetric-entrain (registered 2026-11-13 22:5x, pre-rollout)

Substrate/regime: l59-verbatim (l32 arm-A frozen g .01 / beta 2 / d .05, TAU .05,
DT 10 ms, SETTLE 400, WIN 6000, SEGB 0.7/1.4/0.7, ENT_AMP .3, no hops = hynohop
schedule). Seeds = the 8 hynohop MISSES of l59 (duty_all < .5):
[22, 101, 103, 104, 107, 109, 111, 112] — S_L-owned anatomy in 7/8 (l59 P3).

ARMS (drive applied as amp*(0.5+0.5*sin phi) onto mech cells; per-side split):
- a100: amp_L = amp (SYMMETRIC) — must be BIT-IDENTICAL to l59 raw_l59.npz
  hynohop on every seed (mm + fL/fR/eL/eR), C0 anchor. Implementation keeps the
  single index-add for r==1.0 (bit-identity guard).
- a125: amp_L = 1.25 * amp on rootSide-L mech only.
- a150: amp_L = 1.50 * amp.
- r080: amp_L = 0.80 * amp (direction control).
Non-L mech cells (R + the 1 unknown) always get the baseline amp.

## Static (done first, l60/l60_static.json)
- P0a join: mech somaSide is NaN (3586/3588) — card branch "not side-joinable"
  fires on somaSide, but rootSide joins 0.9997 (1789 L / 1798 R / 1 unknown).
  Card proceeds on rootSide (axon-root side; leg afferent somata are peripheral).
- P0b input-share (Minnick 2% floor): 1-hop direct ipsi share .0066-.0216
  (mean .0141) — BELOW the 2% floor on 6/8 pools; BUT 2-hop via-intrinsic
  ipsi/contra mass ratio 10.2-32.8x on every pool. Conduction to the antagonist
  pools rides the 2-hop sheet (L21/L34), and that pathway is strongly
  ipsi-resolved. Registered read: the floor flags the DIRECT path only; the
  asymmetry lever is expected to act through the 2-hop ipsi channel. If ALL
  dynamic arms are bit-identical to a100 → the split drive never crossed a
  nonlinearity (L35 dm-probe rule) — report as wired-dead, do not force.

## Dynamic predictions (registered BEFORE any rollout)
- P1 DOSE (repair read): mean S_L-side duty (fraction of window TS with
  SL >= .25, over the 3 seg windows) rises with ratio: a150 > a125 > a100,
  gate = a150 - a100 >= +.10 (above lottery scatter, disclosed n=8).
- P2 GATE: # seeds with duty_all >= .5 at best asym arm >= 6/8 (baseline is
  0/8 by construction — miss set).
- P3 LOCK: per-seg mean block err <= .01 on >= 6/8 seeds in every arm
  (tracking was free 16/16 symmetric; asymmetry must not break it).
- P4 NO-CRASH: mean S_R-side duty per arm >= a100 mean - .10 (boost L must
  not buy L by killing R).
- P5 DIRECTION: S_L-side duty under r080 NOT above a100 (no backward gain);
  per-seed paired S_L duty: a125 > r080 on >= 6/8 seeds.
- Paired reads: all arms share the per-step noise tensor + X0 per seed
  (L45b rule); per-seed deltas reported beside means (lottery honesty).
- C0 anchor: a100 vs l59 raw (mm, fL, fR, eL, eR) max|d| == 0.0 on ALL 8
  seeds; first_div machinery unused (no hops) — instead assert per-seed dm
  (a125 - a100) > 0 and (r080 - a100) < 0 at some step (drive actually
  entered differentially; L35 lesson, else "no response" is unreadable).
- C1: af in (0.01, 0.9) post-settle every arm (L30 rollout-wiring probe).

Scope: descriptive lab demo on the l45b census miss set; no live changes;
no WHEN-claims. If P1 passes but P2 fails: asymmetry lifts the marginal side
without flipping the pooled gate → the gate stays distributional (L59) and
the spec gains a per-side repair lever note. If P1 fails: side-asymmetric
mechano entrain closes negative → side-resolved input remains DN volleys
(L24/L37).

## ADDENDUM 1 (registered pre-rollout, 2026-11-13 23:0x)
- The ratio applies ONLY at k >= 0 (measurement window); SETTLE is symmetric
  for every arm so all arms share the identical settled state and diverge
  purely from the window drive (paired read, L45b rule). Side effect: the
  asym arms' first divergence step must be 0 (dm first_div == 0 asserted).
- dm probe carried per arm-pair (first_div / vmax) — an asym arm
  bit-identical to a100 would mean the split drive never crossed a
  nonlinearity (L35) and cannot be read as "no effect" without it.
- dutySL/dutySR = per-side window duty (fraction of TS windows with
  SL >= .25 / SR >= .25) — the P1/P4 readout is per-side, not the pooled
  both-sides duty (L46 decomposition rule).

