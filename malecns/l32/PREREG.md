# L32 PREREG — wiring-borne-antagonism (written 2026-11-11 23:50, BEFORE any scan)

Replication of 2609.38665 (walking in the wiring) on OUR MaleCNS male_graph cord.
Question: does real cord wiring order ANTAGONIST ANTIPHASE under a uniform-param
rate model with SUSTAINED bilateral DNg100 drive — direct tension with our
L16 ("wiring smears time, never orders it") and L28 (antiphase only via
anti-phase DN DRIVE).

## Model form (paper-faithful, deviations labeled)
- Subnetwork: cord cells (vnc_sensory + vnc_intrinsic + vnc_motor) + all DNs
  with >=1 edge into that set. Edges restricted to this node set.
- Weights: RAW signed synapse counts (NOT male_graph.pt's log1p/indegree
  normalization — the paper fixes weights to signed counts; labeled deviation).
- Sign arms (THE candidate missing ingredient):
  A "ours"   : ACh +, glut +EXCITATORY, gaba -, modulators +0.2, unknown +0.3
  B "flyvis" : ACh +, glut -INHIBITORY, gaba -, modulators +0.2, unknown +0.3
- Dynamics: uniform tau 0.05 s (NO per-class taus — that is the point), DT 0.01,
  RMAX 1, BG 0.02, NOISE 0.01; t = relu(g * (W_beta @ X) + d*DNg100_mask + BG).
  3 global params ONLY: gain g, inhibition scale beta (|negative weights| x
  beta), DNg100 drive d (sustained, bilateral, applied after settle).
- Drive: constant d on both DNg100 cells for the whole window (paper form).

## Scan (pre-registered)
- Calibration pass finds the g decade where the settled active fraction
  (0.02, 0.60) at beta=1, d=0; grid placement only.
- Scan grid per sign arm: g x [0.5,0.7,1.0,1.4,2.0] x calib_g; beta in
  {0.5,1,2,4}; d in {0.05,0.2,0.8}. 60 settings/arm, 8-s window, 2 seeds.
- Pools: the pairs our MaleCNS type vocabulary names — Ti (Ti/ti flexor MN vs
  Ti extensor MN) and Tr (Tr/tr flexor MN vs Tr extensor MN). The paper's
  ThC-first hierarchy is NOT nameable in our atlas; mapping gap labeled.
- Per-run op-point assert (L30 rule): af in (0.01, 0.9), no NaN, else setting
  invalid.
- Depth/SNR gate (L19 rule): a pair is READABLE only if both pool-mean traces
  modulate ptp >= 0.03 in the window; S on an unreadable pair is not a number.
- FROZEN SETTING per arm (pre-registered criterion): argmax over settings of
  mean S = mean_pair(-corr(flx_pool, ext_pool)) over READABLE pairs, computed
  after a 2-s transient, require >=1 readable pair else arm FAILS C1.

## Claim levels (fixed now, before scanning)
- C1 RHYTHM: real wiring, some scanned setting, has a readable pair with
  detrended pool-trace FFT peak/median power ratio >= 8 in 0.5-10 Hz.
  (Paper: rhythm appears in every rewired net too — C1 is not the claim.)
- C2 ANTAGONISM IS WIRING-BORNE (the replication claim): at the frozen
  setting, confirmation = 60-s window x 3 seeds:
    (i)  real mean S over seeds, best pair, >= 0.15; AND every seed S > 0;
    (ii) LADDER: real mean S (best pair) > every null draw's mean S (same
         pair, same frozen setting, 3 seeds) + 0.05 margin;
    ladder tiers (>=2 draws each, evaluated at the frozen setting, on the
    arm with the higher real S — the other arm reported scan+confirmation
    only, no C2 claim for it):
      density  : ER, same edge count, |w| i.i.d. from empirical distribution,
                 sign i.i.d. with the arm's negative fraction;
      degree   : global Maslov-Sneppen on the subgraph, weights+signs travel
                 with source (abs() weights nowhere in the swap bookkeeping —
                 L21 rule);
      legblock : MS swaps restricted WITHIN (src_block x dst_block) cells,
                 block = {S(sensory), DN, T1, T2, T3, A(abdominal), X(nan)}
                 from somaNeuromere — preserves the inter-segment mass matrix
                 (the L30 object) exactly while scrambling inside.
- C3 ATTRIBUTION verdict:
  - C2 passes ONLY under arm B -> the missing ingredient was the SIGN RULE
    (glutamate inhibitory);
  - C2 passes under BOTH arms -> the missing ingredient was inhibition SCALE
    (beta) / sustained drive, not signs;
  - C2 FAILS under both -> 2609.38665 does not port to our model class at
    rate fidelity; our L16/L28 boundary stands and the difference is their
    construction (spiking/nonlinear units, subnetwork extraction, or readout),
    to be named in the digest.
- No WHEN-claim beyond correlation structure (L15/L21): S is a correlation
  statistic, no phase-lead claims.
