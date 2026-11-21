# L58 PREREG — gait-reachable-mass (written BEFORE any run)

Task/substrate: l51 verbatim (21,516-node male cord, g .01 / beta 2 / D .05,
SETTLE 400 @0.7 Hz amp .3, WIN 6000, SEGB 0.7/1.4/0.7, DT 10 ms, seeds
11/22/33, ONE generator + shared per-step noise tensor, X cloned per arm).

## Instruments

(a) FAMILY SWEEP (max over FIXED policies, the constructive bound):
  New arms (hop-free, hybrid-family AMPA variants):
    nohop   = hybrid AMPA verbatim (500-on/400-off on 0.7 segs, continuous
              .3 fast seg)  — ANCHOR ARM, must be bit-identical to l55 raw
              hynohop (mm + fL/fR/eL/eR, full window, max|d| = 0)
    off200/off300/off500/off700 = 0.7-seg chop 500-on/X-off
    min5seg = 500-on at each 0.7-seg start then off for the rest of the seg
    fast2   = nohop chop, fast seg continuous at amp .2 (L52 shift point)
    seg2off = nohop chop seg0 + fast cont, seg2 amp 0 (drive floor end)
    seg2a2  = nohop chop, fast cont, seg2 chop at amp .2
  Anchor cells re-derived from STORED raw npz (no rerun, L44 rule — derive
  from artifacts, not log sentences): l51 allw/duty58, l55 hop2k/hop4k/hybrid,
  l39/l50 free if traces carry the pools.
  Anchor asserts: every new arm bit-identical to in-run nohop for all
  k < first AMPA-table divergence (fd_expected computed FROM the tables);
  in-run nohop bit-identical to l55 raw hynohop full window.

(b) FORK ORACLE (receding-horizon, 1-segment greedy, state-conditioned):
  Branches are stored arms that share the noise stream by construction
  (prefix bit-identity asserted): fork A @k=2000 {nohop, hop2k} outcome =
  fast-window duty [2500,4000); fork B @k=4000 {nohop, hop4k} outcome =
  seg2 duty [4500,6000); fork C mid-seg2 {nohop, v43/v49 arms as they
  exist in l56 raw}. Fork state = rolling S_L,S_R at k on the nohop trace
  (window [k-499,k]). Closed-loop = per-seed max over branches; best-fixed
  = max over branches of the per-branch MEAN (same choice every seed);
  closed-loop gap = difference. No claim that greedy 1-segment oracle
  upper-bounds compounding (L6d-0 lesson, disclosed).

## Registered gates + predictions (scored from raw artifacts)

- H1 tracking headroom: some cell with fast-seg err <= .01 on 3/3 seeds AND
  drive-on <= 4800 steps (48 s). [nohop anchor predicts PASS; fast2 tests
  the amp margin.]
- H2 structure headroom (window-scoped): max over family of duty_07 mean
  >= .55. Report per-cell min-seed alongside.
- H3 pooled gate: if NO family cell reaches pooled duty min-seed >= .5 the
  registered reading is GATE-IS-THE-BUG (pooled gate is owned by the L45b
  attractor gas; any learned-policy gate must be window-scoped or
  distributional). If some cell DOES reach it, that cell is the spec.
- H4 drive floor: among cells holding fast lock 3/3 AND duty_07 mean >= .5,
  the minimum drive-on; report the Pareto edge (drive-on vs duty_07).
- P1 slack law inside schedules: off-gap <= 400 steps (4 s) holds duty_07
  (>= .5 mean), off-gap >= 500 steps collapses (mean < .4); collapse is at
  ~5 s regardless of further gap length (L49 gap-length-independence).
- P1b duty-not-gap-limited: off200/off300 duty_07 within .1 of nohop's
  (more frequent chopping does not buy structure beyond slack).
- P2 gas owns pooled: best pooled min-seed < .5 across the family.
- P3 fast2: fast lock holds at amp .2 from chopped entry (err <= .01 3/3)
  AND fast-window duty stays lottery (min-seed < .25).
- P4 seg2off seg2 duty collapses (mean < .15); seg2a2 duty_07 within .1
  of nohop (amp-insensitive at 0.7).
- P5 oracle separability: per-seed hop benefit at fork B decreases
  monotonically with fork-time S_L@4000 (rank corr = -1, n=3 disclosed);
  closed-loop seg2 gain over best-fixed >= +.05.
- P6 free-cell drive floor: free-run (l39/l50) pooled/seg duties within
  .1 of l50's stored verdict when re-derived here (analysis replication).

Metrics verbatim l51: dom_freq on 500-step blocks, seg err = mean |f-target|
over blocks[1:], LOCK_TOL .10, rolling S over 500-step windows sampled every
10 steps, duty = frac of samples with S_L >= .25 AND S_R >= .25, windows
[seg0+500, seg_end), pooled = union over segs, duty_07 = the two 0.7 segs.
Raw npz checkpointed BEFORE analysis (L45a lesson). Score the TRIPLE
separately; never a summed J. CPU-only; P1-labeled; no live changes.
