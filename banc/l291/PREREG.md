# L291 PREREG -- WEIGHT-MATCHED comparators for the group question

Frozen 2026-11-25 05:05:35 EST by Miso, tick 281 (LANE.md card L291).
Parent: L290 (PREREG sha 27b6a473bdb2f9d6..., VERDICT NO_DECISION, predictions 0/8).
Rule: no edit after freezing. Amendments only as new dated files. A journaled blocker is a valid tick; a
fabricated number is the only failure.

## s0 The question
L290 could not separate "the metric's ENTRY SET is special" from "the set carries heavy edges, or carries e14".
Its random comparators were UNIFORM (not weight-matched) and 9 of 15 cleared the floor.
STATIC FACT, measured this tick from stored sets before any draw: L290's heaviest-synapse comparators were not
weight-matched either. Raw synapse sums: rw11 359 vs U_abs 210 (1.71x),
rw30 668 vs U_crofts 429 (1.56x), rw46 808 vs U_hop 624 (1.29x).
Q: when a random subset is MATCHED to the used-set on raw synapse sum, does the used set still differ from it,
and is any remaining difference carried by e14's MEMBERSHIP rather than by the rest of the set?

## s1 Declared inputs (SEEN, stored; design input, not L291 data)
- Unit F = 0.00022931491480943385 (A1 noise-twin SD/4, l240/results_l240.json, re-read by L290); eps = 2F = 0.0004586298296188677.
- Used-set effects (stored, in F): g11 +4.34 (A1), gc30 +8.73, gh46 +9.15 (L290). e14 alone +5.46 (A1).
  A1's stored fixed-gain twin of the 11-set: g11f +7.94 (l240/results_l240.json effects, reported, not re-run).
- 69-edge menu raw syn: total 919, per-edge mean 13.3, min 4, max 41. e14 = 20 synapses, weight rank 17 of 69.
- Used-set sums T_n and where they sit in the UNIFORM n-subset sum distribution: U_abs 210 at n 11 (+2.05 SD, pct 0.972);
  U_crofts 429 at n 30 (+0.70 SD, pct 0.754); U_hop 624 at n 46 (+0.28 SD, pct 0.599). SD of a uniform n-subset sum: 31.0 / 41.9 / 39.9.
- SEEN in-band L290 uniform arms (declared so nobody reads L291 as blind): n 11 none (the five r11 arms sum [170, 116, 152, 114, 176] synapses, all e14-free, E [0.99, -4.34, -2.22, -4.69, 1.74] F);
  n 30 [('r30k1', 441, 11.9), ('r30k2', 426, 2.91)] (e14 in ['r30k1']);
  n 46 [('r46k1', 616, 3.87), ('r46k2', 610, 1.92)] (e14 in ['r46k1', 'r46k2']).
- Monte Carlo (2e6 uniform draws per size, l291/static_probe.out): acceptance of the registered band 0.0389 / 0.3090 / 0.5533;
  P(a band draw contains e14) 0.201 / 0.459 / 0.673.

## s2 Design (nothing below is drawn or run until this file is frozen and hashed)
Lineage: byte-identical harness lineage to L240 stage A2 / L290 (l240/edge_run_a2.py sha 2c71eded96e90af03aeb2fc4ca270627667f8879ffac7c7244e81b5b1dcf0496;
generated harness sha pinned by the builder and by the analysis script).
Arms, 17, every one a cut from carrier gi 1110's 69-edge menu (W[target, source] CSR, out-edges in the TARGET rows):
 (i) 15 STRATIFIED subsets. For each size n in (11, 30, 46) with used-set U_n = {11: 'abs', 30: 'crofts', 46: 'hop'}: 3 subsets WITH e14
     (s{n}w1..3) and 2 WITHOUT e14 (s{n}f1..2). Draw: rng = numpy Generator(PCG64(29113)); sizes in order
     11, 30, 46; cells in order w (k = 1..3) then f (k = 1..2); each arm is the FIRST uniform n-subset
     (rng.choice(69, size=n, replace=False)) that has the cell's e14 membership AND a raw synapse sum inside the
     integer band [ceil(0.95 T_n), floor(1.05 T_n)] = [200, 220] / [408, 450] / [593, 655].
     Rejection count is stored per arm. Cap 2,000,000 raw draws per arm: a cap hit is UNDRAWABLE, that arm is
     reported missing and the band is NEVER widened. No re-roll for any other reason: a subset equal to the
     used set (or to another arm) is kept and scored VACUOUS BY IDENTITY.
 (ii) 2 FIXED-GAIN twins: gc30f and gh46f = the stored L290 group graphs (L290 sets.json), at the stored base gain
     g_cutwA = 0.14365819573402408 (edge-not-gain check for the group arms).
Gain rule: every stratified arm is bisected to AF_T in its own process, as in L290 (a per-arm gain bisection is
part of the intervention). Readout windows SETTLE 400 / WIN 6000, 2 threads, float32, as A2.
Seeds 3769-3784 reused (16) so every arm pairs to A1's STORED cutwA traces: a same-draw consistency check,
not an independent replication.
Workers (2): w0 = cutwA + s11w1 s11w2 s11w3 s11f1 s11f2 s30w1 s30w2 s30w3 gc30f;
w1 = cutwA + s30f1 s30f2 s46w1 s46w2 s46w3 s46f1 s46f2 gh46f.
Comparators for the verdict: ONLY the 15 stratified arms. L290's uniform arms are reported beside them, never scored.

## s3 Readout and statistics (inherited from L290 s4, unchanged)
P_a(s) = mean over the 303-cell pool union of the whole-window mean activity (xmean), arm a, seed s, 16 seeds.
d_a(s) = P_a(s) - P_cutwA(s) with A1's stored cutwA; E_a = mean_s d_a(s); reported in F.
Arm-vs-arm: Delta(u,x)(s) = P_u(s) - P_x(s); D = mean; SE = SD/4; exact two-sided sign-flip test over 2^16.
Advantage A = sign(E_u) * D; p_adv = P(null >= A).
EXCEEDS: A >= eps and p_adv <= 0.01. EXCEEDED_BY: A <= -eps and p_adv_down <= 0.01. else WITHIN.
Companion readout (descriptive, no branch): per-pool 20-vector unsigned norm N_a against the A1 vector floor.

## s4 Registered verdict (FIRST MATCH), companions, predictions
For each metric m in (abs, crofts, hop), u = its used-set arm, comparators = its 5 stratified arms
(W = with e14, F = e14-free): exW = number of W comparators u EXCEEDS, exF = the same over F,
by = number of comparators (either cell) that EXCEED u, within = 5 - exW - exF - by.
 (c) I_INSTRUMENT_AT_GROUP: fewer than 8 of the 15 stratified arms clear the floor (|E| > eps).
 (a) SET_BEYOND_WEIGHT:<m>: some m with exW + exF == 5 (all five weight-matched comparators EXCEEDED).
 (b) E14_MEMBERSHIP_NOT_WEIGHT: at least 2 metrics with exF == 2 and exW == 0.
 (w) WEIGHT_CARRIES: at least 2 metrics with exW == 0, exF == 0 and by == 0 (all five WITHIN).
 (n) NOT_SPECIAL_AT_WEIGHT: at least 2 metrics with exW + exF == 0 and by >= 1.
 else NO_DECISION.
The instrument check is FIRST (L290 had it third): a used set beating five floor-level comparators says
nothing about weight. Per-metric labels are stored beside the verdict.
Companions (reported, never gating):
 (g) WEIGHT_LIFTS_E14FREE, paired on the same 16 seeds, per size: mean P over the size's e14-free stratified
     arms minus mean P over its e14-free L290 uniform arms; sign-flip p.
 (h) midrank Spearman of E with effective size among the 15 stratified arms (reported only if >= 10 distinct values).
 (f) EDGE_NOT_GAIN_GROUP: gc30f, gh46f sign-concordant with gc30, gh46 and |E_f - E_b| <= eps; 2 of 2 to fire.
Predictions (registered before any L291 set exists):
 P1  n_clear >= 8 of 15.
 P2  exF == 2 in at least 2 of 3 metrics (the used sets beat their e14-free weight-matched subsets).
 P3  abs reads exF == 2 and exW == 0.
 P4  hop is NOT an E14_MEMBERSHIP metric: exW >= 1.
 P5  EDGE_NOT_GAIN_GROUP fires 2 of 2.
 P6  (g) at n = 11 is positive with p_up <= 0.01.
 P7  VERDICT is neither WEIGHT_CARRIES nor I_INSTRUMENT_AT_GROUP.

## s5 Compute and honesty
nice +15, 2 threads, timeout 1700 per worker, at most 2 workers per background call and 3 concurrent; each worker
admitted only through its exit-code file. Both workers exit 0 -> FINAL; otherwise PARTIAL: verification only, no
effect read, branches NOT read (the verdict needs all three metrics).
Writes confined to banc/l291/ plus the LANE.md bracket, the LANE-LOG lines and the research digest. Prior dirs
read-only. sessions/ never touched. The fly duck is never touched: same PID, NRestarts 0, /needs probed before
and after. The analysis script is executed end-to-end on a synthetic set BEFORE any worker finishes (L290 lesson).
Gates per worker (inherited, a failure VOIDS the worker): anchors 801, 901 bit-exact; cutwA traces bit-identical
to A1's stored l240/raw_w0-2 and xm_w0-2; bisected cutwA gain == 0.14365819573402408; F == 0.00022931491480943385.

## s6 Disclosures
- DEVIATION FROM THE CARD TEXT. The card said e14 membership is "REPORTED, never conditioned on". This PREREG
  conditions it: 3 with / 2 without e14 per size. Reason: under pure sum-stratification P(no e14-bearing draw in 5)
  at n = 11 is about (1 - 0.201)^5 = 0.33, so the card's own e14-versus-weight question
  would be left to a coin toss on set composition. No L291 effect exists; the allocation is fixed before any draw.
- The static facts in s0/s1 were measured this tick from STORED sets and effects (L221, L240, L290) before the
  freeze. They are why the band is +-5 % and why the raw comparators of L290 cannot answer this question.
- Tick budget: 35 min from 04:58 EST. The rollouts alone need about 18-20 min after the build, so this tick is
  expected to overrun by roughly 20 min. Disclosed here and in the lane log.
