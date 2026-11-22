# PREREG — L177: the beta ladder vs the field's monotone-inhibition law

Written 2026-11-21 ~22:3x (cron tick 224, Miso) BEFORE any new rollout.
Substrate: l65 BANC female cord subnet (n 21,249 = 20,521 cord + 728 dn_into;
627,051 raw log1p edges), sign arm **B** (flyvis glutamate->inhibitory — the
arm that carries the L65 antiphase result), pools Ti (101 flex / 12 ext) and
Tr (62 / 48) from `peripheral_target_type` tokens.

## 0. Card correction (L44 rule — stored artifacts, not the card sentence)

The L177 card states beta "has sat pinned at 2 since L32/L65 and was never
laddered". **That is wrong and the run must say so.** `l65_banc_oppoint.py`
line 28 pins `BETAS = [0.5, 1.0, 2.0, 4.0]` and `l65/scan_l65.json` stores a
36-row beta x g-ratio x d scan **per sign arm** (8 s window, seeds 11/22).
beta=2 is therefore a **selection** on that table, not an arbitrary pin.

What the stored ladder is NOT, and why L177(b) still has to run:
 1. **g was a RATIO grid (0.7/1.0/1.4 x gstar), never re-bisected per rung**,
    so the operating point slides with beta — arm B af at g/gstar 1.0 goes
    .2757 -> .1441 -> .0864 -> .0485 across beta .5 -> 4.0 (**5.68x**).
    Every S difference in the stored table is beta-and-op-point confounded.
 2. 8 s window (vs the 60 s confirm), 2 seeds, no per-side decomposition.
 3. The frozen cell (arm B: g/gstar 1.40, beta 2.0, d 0.2) was **selected on
    this very table**, so its S is selection-inflated by construction.

## 1. Stage (a) — the stored pre-measurement (DONE this tick, zero rollouts)

`l177_prem.py` -> `l177/static_prem.json`, `l177/prem.out`. Measured:

**M1 — shape.** Arm B, S_Ti, 9 paired (g-ratio, d) cells walked over beta:
**0 of 9 monotone-increasing**; 7/9 carry an **interior maximum** (3 at
beta=1.0, 4 at beta=2.0), 2/9 non-monotone with an edge max. Best cells:
g/gstar 1.40 gives .  -.055 / +.575 / **+.873** / +.077 across beta .5/1/2/4.
Arm A is unreadable at beta 0.5 (af .43-.50, saturated, S = nan 9/9).

**M2 — the confound.** af is **monotone DECREASING in beta** in both arms
(arm B medians .2757 / .1441 / .0864 / .0485; arm A .4632 / .2373 / .1268 /
.0923). The beta=4 rungs sit far BELOW the L11/L65 op band; the beta=0.5
rungs sit far above it (arm A saturated).

**M3 — drive inertness, free (L35 probe, already answered for beta <= 2).**
In BOTH arms, at beta 0.5 / 1.0 / 2.0 the three drive levels d = 0.05 / 0.2 /
0.8 give **identical af and identical S to every printed digit** — the
sustained DNg100 drive is inert exactly as L35 found on the male cord. At
beta = 4.0 the d-rows **separate** (arm A g/gstar 1.0: S_Ti -.616 / -.550 /
-.418; arm B 0.70: +.007 / +.011 / +.091). Drive visibility appears to be
beta-gated.

## 2. Stage (b) — the registered ladder (rollouts; this is what gets run)

Design, pinned:
 - **Rungs** beta in {1.0, 1.5, 2.0, 3.0, 4.0} (the card's ladder). Arm B only.
 - **Fresh af-matched bisect per rung** to the l65 op point (target af = the
   arm-B frozen af **0.1038**, tolerance |af - target| reported, not assumed;
   L107 staircase rule: disclose the residual). Report the **gain spread**
   across rungs (L139: in-degree renormalization makes small weight changes a
   broad effective-gain family; beta changes are NOT small — expect a wide
   spread and say so).
 - **Same seeds every rung** (paired reads): 16 seeds, batch pinned in the
   runner's assert block and enumerated from the stored npz keys at write
   time (L157 rule — do not type batch numbers from memory).
 - **Windows**: 60 s confirm window (CONF_WIN 6000, DT .01), settle 400.
 - **Per-SIDE decomposition mandatory** (L46/L101): S_Ti_L, S_Ti_R, S_Tr_L,
   S_Tr_R reported separately; a both-sides AND cell may never be the only
   read.
 - **Drive-relevance probe per rung** (L35): a d = 0 arm at every rung,
   bit-identity checked against the d = 0.2 arm. M3 predicts bit-identity at
   beta <= 2 and divergence at beta >= 3-4.
 - **Floor/viability census per rung** (L36/L38): u_max and mean_X per pool,
   so a floor-pinned pool is never read as lost structure (P3).

## 3. Registered predictions

 - **P1 (the field's law, the null to beat)** — Guba's DC arm: S increases
   MONOTONICALLY in beta. Cell: S_Ti pooled over seeds is non-decreasing on
   all four rung steps.
 - **P2 (our L50 family)** — non-monotone with an interior optimum.
   Cell: argmax over rungs is interior (1.5 / 2.0 / 3.0) on >= 2 of the 4
   per-side S series.
 - **P3 (saturation then collapse)** — high-beta rungs collapse S *and* the
   viability census shows pool floor-pinning (mean_X at/near 0 or u_max < 0).
   Cell: S drop at beta >= 3 accompanied by a census flag.
 - **P4 (the af-matching fork — the one this run exists for)**. The stored
   table says P2 at *unmatched* gain. Under **af-matched** rungs:
   - **P4a**: the interior optimum SURVIVES -> beta non-monotonicity is a
     property of the wiring, and we have a real cross-model discriminator
     against the field's monotone law.
   - **P4b**: the ladder becomes MONOTONE -> our stored shape was an
     operating-point artifact, the field's law holds in our model class, and
     the L65 beta=2 pin is re-read as "the rung whose free gain happened to
     land in band". **P4b is a perfectly good result and must be reported as
     a correction to our own prior reading, not buried.**
 - **P5 (drive gating, from M3)** — the d=0 bit-identity breaks at beta >= 3.

Branch names: `B_MONOTONE` (P1), `B_INTERIOR` (P2/P4a), `B_COLLAPSE` (P3),
`B_ARTIFACT` (P4b). Report WHICH cell carries the verdict and name any
failing condition (L109: one object per gate cell — do NOT AND a shape claim
with a viability claim).

## 4. Verification contract

 - **C0S-177 (static cert, runs FIRST, halts on mismatch)**: re-derive from
   the release + banc_graph.pt and assert EXACT against l65's stored values —
   subnet n 21249, edges 627051, cord 20521, dn_into 728, pools Ti 101/12 and
   Tr 62/48, arm-B gstar 0.1, frozen (g 0.14, beta 2.0, d 0.2, af 0.1038).
 - **C0A-177 (forward-chain bit-identity anchor)**: the beta = 2.0 rung run
   at l65's frozen g (0.14, i.e. the UN-rematched gain) on seeds 11/22/33
   must reproduce `l65/raw_l65.npz` keys `B_s{11,22,33}_{Ti,Tr}_{f,e}` to
   max |d| = 0.0. This rung is a re-run of existing work and must reproduce
   EXACTLY (L41/L120 forward-chain form). If it does not, HALT and report —
   do not analyse any new rung.
 - **Op-point assert on every rung before any arm is read** (L30): settled
   active fraction vs the rung's own bisected target; a rollout that fails it
   is void.
 - **Checkpoint raw pool traces to npz the moment each rung finishes** (L43),
   including every pool the registered metrics read (all four antagonist
   pools per side + the S trace if computed in-run; L45a rule).
 - No live-module changes, no draft edits (paper/DRAFT.md is in owner-handoff
   state), writes confined to `banc/l177/`.

## 5. Limit stated up front (goes in any write-up)

beta is OUR free parameter. A monotone result is **model-class agreement**,
not a measurement of the fly; an interior optimum is a statement about this
rate model on this connectome at a matched operating point. Neither direction
licenses a claim about biological reciprocal-inhibition gain.
