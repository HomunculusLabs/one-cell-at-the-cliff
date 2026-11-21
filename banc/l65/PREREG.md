# L65 PREREG — banc-oppoint + female L32 antiphase replication (tick 86, 2026-11-14)

Written BEFORE any rollout. Graph: peabrain-lab/banc/banc_graph.pt (BANC v626 female,
N=80,635, in-deg normalized, log1p weights, sign per source NT; glut=EXC arm A default).
L32 machinery form: l32_antigonism.py (male). Deviations from male L32, labeled up front:

- D1: weights = log1p(syn_count) RAW within subnet (no indeg norm inside the cord
  subnet — same "no indegree norm" deviation L32 labeled), sign per source NT.
- D2: pools from SEMANTIC peripheral_target_type (male used type names):
  Ti flex = {accessory_,}tibia_flexor_muscle (101), Ti ext = tibia_extensor_muscle (12),
  Tr flex = {accessory_,}trochanter_flexor_muscle (62),
  Tr ext = {tergo,sterno_,}trochanter_extensor_muscle (48).
- D3: NO legblock tier — BANC flat table has no neuromere column (nerve/
  body_part_effector tag efferent cells only). Ladder = density + degree, 3 draws
  each (item minimum 3; male used 2).
- D4: subnet = super_class in {sensory, ventral_nerve_cord_intrinsic, motor} AND
  region == ventral_nerve_cord, + descending cells with edges INTO that cord set
  (male form: vnc classes + DN-into-cord).

## Registered claims

- C0 structural anchors (must ALL pass before any verdict is read):
  - pools non-empty inside subnet: Ti flex >= 90, Ti ext >= 10, Tr flex >= 50,
    Tr ext >= 40; DNg100 == 2 cells inside subnet.
  - arm A/B share identical COO structure (nnz + src/dst arrays equal); neg
    fraction B > A (glut share flipped).
  - MS degree draws preserve in/out degree EXACTLY (assert) and nnz.
  - every reported run af in (0.01, 0.9), NaN-free.
- P1 op-point (full 80,635 graph, stored normalized W, no drive, SETTLE 400,
  af = mean(X > .05)): bisect gain g to af in [0.13, 0.17]. PASS = bracket found;
  report g* (context: male landed 0.885 under its own normalization). This is a
  measurement, not a male-match gate.
- P2 replication (subnet, L32 scan form: GRATIOS [0.7, 1.0, 1.4] x BETAS
  [0.5, 1, 2, 4] x DS [0.05, 0.2, 0.8], seeds {11,22}, 8 s window; confirm 60 s
  x seeds {11,22,33} on frozen best per arm):
  PASS  = frozen best setting gives mean S >= 0.30 on >= 1 pair, with >= 2/3
          confirm seeds S > 0 on that pair and depth >= 0.03 every confirm seed.
  PARTIAL = same form with mean S in [0.15, 0.30).
  FAIL  = no readable setting (all depths < 0.03) or mean S < 0.15.
  Male reference: S(Tr) +.49.
- P3 ladder (on the higher-real-S arm, frozen setting, 60 s, 3 seeds x 3 draws
  per tier): wiring-specific PASS = max over degree draws of mean S(best pair)
  <= real mean S(best pair) - 0.15. Density tier expected <= real (report only).
- P4: report arm A vs B real S; no gate (informational: glut sign question).

Falsifier note: if P2 FAILs on real wiring, P3 is moot (nothing to credit wiring
with) — journal as negative replication, no ladder verdict claimed.

Checkpoint discipline: scan json + confirm/ladder raw pool traces (4 pools x 60 s
x per seed/run) saved to l65/raw_l65.npz BEFORE analysis; verdict re-derivable
from checkpoint alone.
