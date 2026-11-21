# L95 PREREG — fd-burial-probe (instrument card)

Register BEFORE any rollout. All expectations derived from STORED artifacts
(raw_l93.npz, results_l93.json, l93/viability.csv, l93_run.py source), per L44 rule.

## Background (stored facts, not predictions)

- L93 measured fd (pool-mean first-divergence, argmax(d>0), shared noise) with
  per-seed values: fast cells 1-35 (Tr_fL), d74b_R @amp 2.0 (u_max -1.763,
  headroom 2.0-1.763-... see pin law) fd {441, 1098, 97}.
- Dynamics (l93_run.py): X += 0.2*((relu(drive+BG)+nz).clamp(1)-X), drive =
  W@X*G_NEW + I (+amp on volley cells, k in [0,2000)); noise SHARED across arms
  -> arm-vs-base trace differences are purely causal, positivity is scale-free.
- Pin law (from dynamics): a buried cell (u(k) <= -BG-... i.e. relu(drive+BG)=0
  when drive+amp+BG <= 0) never diverges -> fd = -1. Un-pin condition at step k:
  u(k) + amp + BG > 0, where u(k) = BASE-arm drive at the cell (bit-identical
  between arms until first opening, because the perturbation is CAUSED by it).
- One-hop law (L77/L83/L86 stored): a drive change entering cell at k appears in
  ONE-HOP-DOWNSTREAM pool traces at k+1.

## Registered prediction law F0 (the instrument)

k_open(arm, seed) = first k in [0,2000) with u_base(k) + amp + BG > 0
  - single-cell volley: u of that cell; multi-cell: k_open = min over cells
    of each cell's first opening (sum of positive contributions is positive).
fd_pred(earliest positively-coupled pool) = k_open + 1 (pool X updates at k+1
  from cell X at k), PLUS a per-(pool,seed) float32-visibility + mixed-coupling
  lag eps >= 0 whose distribution this card MEASURES (not assumes).

## Registered prediction law F2 (the card's naive guess, expected WRONG)

fd ~ c / (amp - |u_max|) hyperbola in static headroom. F2 cannot explain
  fd(xl080)@headroom~1.98 = {3,3,17} vs fd(intr16, ALREADY OPEN u_max>0) =
  {1,1,3}: near-degenerate static headrooms, different fd scales. Report F2
  rank-fit as descriptive only if it survives.

## Fresh probe (l95_probe.py, l93_run.py machinery VERBATIM, CPU-only)

Arms (write-time pinned): base; d74b_R amp in {1.5, 1.8, 2.0, 3.0, 5.0}.
  - 1.5 < pin threshold 1.743 (=1.763-0.02... pin condition: max_k(u)+amp+BG
    <= 0 -> amp <= 1.763-0.02 = 1.743) -> buried-at-2-decimals control.
  - 2.0 == l93 condition (anchor arm).
  - 3.0/5.0 = the card's registered sweep; 1.8 = marginal (+.057 headroom).
Seeds 11/22/33 (same as l93 -> shared noise stream -> bit-identity anchors).
Records: pool/mm/xm traces per arm (fd metric verbatim); per-step u_base(k)
  for ALL l93 volley cells (int16, ti16, xl080, d74b, d105, shamdn_a/b,
  shamint_a/b index arrays from raw_l93.npz) during seg0; d74b cell X trace
  per arm (rise-curve tau check).

## Gates (pinned)

- P1 MONOTONE (card-registered): measured fd(d74b, earliest pool) non-increasing
  in amp over {2.0, 3.0, 5.0} per seed (headroom .237/1.237/3.237 -> earlier
  first crossing). All 3 seeds or disclose.
- P2 CROSSING LAW: measured fd(earliest pool) - (k_open+1) = eps >= 0, and the
  eps distribution over fresh + stored-l93 cells is REPORTED (this is the
  instrument's resolution). Sharp sub-gate: eps <= 8 for >= 2/3 of fresh cells.
- P3 PIN LAW: amp 1.5 -> fd = -1 (no divergence, d==0 everywhere) 3/3 seeds,
  AND recorded u(k)+1.5+BG <= 0 for all k (internal consistency, max <= 0).
- P4 ONE-PROBE CLASSIFICATION (the deliverable): from u_base(k) ALONE predict
  for every l93 arm (a) pinned-at-amp-2.0 (k_open undefined) vs un-pinned —
  must match stored c2 fd == -1 vs finite EXACTLY (count disagreements = 0);
  (b) fd rank: Spearman(k_open+1, measured fd_Tr_fL) >= .90 across the
  un-pinned arm-seed cells (lag jitter tolerated by rank).
- ANCHORS: C0A d74b_2.0 arm == raw_l93 d74b_R_20 traces BIT-IDENTICAL (max|d| 0)
  on mm/xm/8 pools x 3 seeds (38th consecutive chain anchor); C0B base ==
  l93 base == l92 cfn prefix; C0E fd metric recomputed on stored raw_l93 ==
  results_l93 c2 values EXACTLY (metric certification before any new read).
- af op-point assert per seed (0.01 < af < 0.9), l93 verbatim.

## Discipline

- CPU-only; raw checkpoint BEFORE analysis; write-time asserts on amps/cells;
  no live changes; sessions/ untouched. If a gate fails, journal the failure
  honestly (the eps distribution is a measurement, not a pass/fake).
