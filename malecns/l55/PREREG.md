# L55 PREREG — hop-scheduling for the pooled gate (written BEFORE any run)

Task (LANE.md ideas-26, verbatim intent): L51's bonus arm showed the pooled
duty gate (.5) is within reach by HOP SCHEDULING alone — nohop pooled .496
vs hybrid .484 with tracking intact (the L39 lock-buying volley COSTS
structure when the lock is already free from chopped entry). Test hop
scheduling as a 2x2 FACTORIAL over (entry hop, exit hop) on the hybrid AMPA
schedule, plus the LANE-registered conditional policy. Pooled duty table
3 arms x 3 seeds minimum (nohop / hop-at-segment-start / conditional); the
factorial cells hop4k and hybrid are the completion + chain anchors.

P1-labeled descriptive lab demo. CPU-only. No live changes. Owner movement
law respected (lab evidence, never app motion).

## Machinery (l51-verbatim, nothing re-tuned)

- Substrate: MaleCNS cord 21,516 nodes / 2,977,920 edges, frozen l32 arm-A
  (g .01, beta 2, D .05 on DNg100), tau .05, DT 10 ms, RMAX 1, BG .02,
  NOISE .01, SETTLE 400 @0.7, WIN 6000, SEGB = [(0,2000,.7),(2000,4000,1.4),
  (4000,6000,.7)], ENT_AMP .3, hop DNge046_L amp .5 window 40 steps,
  LOCK_TOL .10, seeds {11,22,33}. AMPA = hybrid everywhere: duty58's exact
  500-on/400-off table on seg0/seg2, amp .3 CONTINUOUS on seg1.
- ONE generator per seed, X0 first, ONE shared per-step noise tensor across
  arms (l39-l51 convention — anchors depend on it). Arm set does not touch
  the stream (draws are arm-independent); C0a/C0b prove it.
- Static AMPA/HOPA tables for all arms except `cond`, with write-time
  asserts; no inline drive conditionals in the step loop (L39v1/L43v1/L48).

## Arms (5) x seeds {11,22,33}

- hynohop: hybrid AMPA, NO hops.              [C0a anchor vs l51]
- hop2k  : hybrid AMPA, hop ONLY [2000,2040) — "hop-at-segment-start".
- hop4k  : hybrid AMPA, hop ONLY [4000,4040) — exit hop, completes the
           2x2 factorial. EXPLORATORY label (not in the LANE 3-arm minimum).
- cond   : hybrid AMPA, NO static hop; DYNAMIC decision at k == KD = 3000
           (10 s into the 20-s fast segment): err_KD = |dom_freq(
           mm_cond[2000:3000]) - 1.4|; FIRE hop on [3000,3040) iff
           err_KD > THR = 0.05, else never. THR sits between the observed
           free lock (block-err .0007-.0027, l51) and the l39 continuous-
           entry miss (.21-.29). The decision is a deterministic function
           of the cond arm's own trace (no RNG at decision time).
- hybrid : hops BOTH transitions.              [C0b anchor vs l51]

All hops ride AMPA-on windows by construction; drive-on = 4800 steps for
every arm (hop volleys are not counted, l39-l51 convention, disclosed).

## Anchors (C0/C1) — all exact, no tolerance

- C0a: hynohop bit-identical to l51/raw_l51.npz mm over full [0,6000),
  3/3 seeds, max|d| == 0.0.
- C0b: hybrid bit-identical to l51/raw_l51.npz mm over full [0,6000),
  3/3 seeds, max|d| == 0.0 (13th consecutive chain anchor class).
- C0c: first_div vs hynohop exactly: hop2k == 2000, hop4k == 4000,
  hybrid == 2000 (3/3 seeds); cond == 3000 if fired, else FULL-trace
  bit-identity max|d| == 0.0 (never-fired marker).
- C1: volley-window max|d| vs hynohop > 1e-6 for hop2k/hop4k/hybrid (and
  cond iff fired); af in (0.01, 0.9) every arm-seed.

## Gates + predictions (registered before the run)

- G-L55 / P1 (the LANE-registered prediction): cond duty_all >= .5 on
  >= 2/3 seeds AND cond seg1 tracking err <= .01 on 3/3 seeds.
  HONESTY NOTE: l51's stored hynohop already reads [.511,.464,.513] —
  P1 can pass DEGENERATELY if cond never fires; the discriminating
  predictions are P2/P3.
- P2: cond NEVER fires at amp .3 (err_KD < .05 on 3/3; l51 block-err
  .0007-.0027 says the lock is free from chopped entry).
- P3: the ENTRY hop carries the structure cost: hop2k seg1 duty <
  hynohop seg1 duty on >= 2/3 seeds (l51 hybrid was worse on 3/3:
  .133/.627/.0 vs .22/.8/.213).
- P4 (exploratory, NO directional prediction): exit hop (hop4k) seg2 duty
  vs hynohop — l51 hints seed-lottery (hybrid helped s22 .147->.673,
  hurt s33 .66->.48); recorded only, no gate.

## Verdict mapping (pre-registered)

- P1 & P2 pass -> the pooled gate is met by hop DELETION; the conditional
  is vacuous at amp .3 (lock free, nothing to buy); controller spec: drop
  the L39 hops from chopped entry entirely.
- P1 pass, P2 fail -> conditional earns its keep on >= 1 seed; report
  where and what it rescued.
- P1 fail -> pooled gate NOT reachable by fast-segment hop scheduling;
  name the window that owns each seed's miss (l51 hint: s22's miss lives
  in the 0.7 windows — seg2 .147 — which no fast-segment hop can touch).

## Analysis windows

Verbatim l51: TS = arange(499,6000,10); rolling 500-sample per-side S on
Ti/Tr flexor/extensor MN pools; duty = both per-side S >= .25; measurement
spans [seg0+500, seg0+2000); duty_all pools all three seg windows, duty_07
the two 0.7 segs; seg err = mean over BLK=500 blocks excluding each
segment's first; ttl = first post-first block with err <= .10. Raw npz
checkpoint BEFORE analysis (L45a lesson) carrying every pool the metrics
read (mm + all four antagonist pools + x046 + cond's err_KD/fired record).
