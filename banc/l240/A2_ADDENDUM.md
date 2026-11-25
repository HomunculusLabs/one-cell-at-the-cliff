# L240 A2 ADDENDUM -- the 69-edge gates, the readout declaration, the metric comparison

FROZEN 2026-11-24 19:08 EST (tick 275) BEFORE any A2 arm construction, gain bisect or
rollout. sha256 in `A2_ADDENDUM.sha256`; `edge_run_a2.py` asserts it at import. The A1
PREREG (d6c73be3a4c06...) stays frozen and unedited. This file only fixes what A1's
VERDICT.md "Hand-off to A2" left open, plus one prerequisite A1 did not have.

## 1. The 69-edge menu, derived and certified (prerequisite A1 did not need)

L221's `static.json` stores only 11 `(edge_j, target_gid)` pairs (`used_edge_table`).
The other 58 targets of the 69-edge menu are not stored anywhere in l221/ or l220/
(checked by a recursive walk for lists of length 69/70/80). DERIVATION: the carrier's
(gi 1110) out-edges on the harness base edge list (`emask_wA`), ordered by ascending
target gid; `edge_j` = the position among those with RAW synapse count >= 4 (the f4
floor). This INFERREDS L221's `edge_j` order (CSR column order = ascending local index)
instead of re-executing its enumeration, so it is certified, not assumed.

CERT-MENU-A2, in every worker BEFORE any bisect or rollout (any failure = STOP):
(a) the raw list has exactly MENU_N entries, MENU_N = the CSR menu count of the carrier;
(b) exactly 69 survive `syn >= 4`;
(c) all 11 stored L221 pairs reproduce at their positions (11 of 11).

## 2. Arms

- 58 single-edge arms `e{j}`, j in 0..68 minus EJ (the 11 A1 edges), each exactly one
  CSR entry W[target, carrier] deleted, gain RE-BISECTED per arm (A1's stored-form
  bisect: lo .12 / hi .18, 24 halvings, settle-only AF, same target).
- `cutwA` re-run in every worker (section 3's bit-identity gate).
- NOT re-run: `g11`, `g11f`, `nf`. A1's stored traces are the additivity result and the
  floor.
- NOT run at A2: the 11 cutwA-only sub-floor edges. PREREG s1 called them "A2
  comparators", but no registered gate or comparison reads them. Deferred by this
  sentence, not dropped silently.
- A labelled edge whose target is absent from cutwA is FALSE BY UNMEASURABILITY (PREREG
  s1): recorded in the worker's `arms_w*.json` under `unmeasurable`, removed from that
  worker's plan, counted in the FLOOR count as NOT clearing, and EXCLUDED from the SPLIT
  ranking (the measurable count n is printed beside rho).

## 3. Seeds, pairing, anchors

Seeds 3769-3784 (A1's block; the harness re-derives the block and asserts it). The
pairing partner for every A2 arm is A1's STORED `cutwA` traces (`raw_w0-2.npz`,
`xm_w0-2.npz`). GATE (else VOID, no A2 effect is read): each A2 worker's own `cutwA`
traces equal A1's stored `cutwA` traces EXACTLY for every one of the 16 seeds (`xmean`
and the tracked raw traces, `np.array_equal`), and its bisected `cutwA` gain equals the
stored gain. F = A1's noise-twin floor (2.2931e-4), recomputed from A1's raws and
asserted equal to `results_l240.json`. Anchors 801 / 901 / 3545 bit-exact in every
worker (inherited). Halves H1 = 3769-3776, H2 = 3777-3784, as in A1.

## 4. Readout: ONE primary, declared before any A2 data (the hand-off's first item)

- PRIMARY = the pool MEAN `P_a`, exactly as frozen in PREREG s4. It is NOT switched to
  the vector: the only evidence that the vector ranks more edges is A1's 11 edges,
  already seen, so switching now would select the readout on seen data (a within-band
  pattern seen after the fact is registered next, not banked).
- COMPANION = the unsigned per-pool VECTOR `N_a` (A1's definition). Registered now:
  (i) vector floor `floorN = ||Fp||_2`, Fp = per-pool SE of the stored `nf` vector
  (A1's analysis definition, frozen here); `V69` / `V58` = counts of edges with
  `N > 2*floorN` over all 69 / over the 58 new edges only (the 11 were seen at A1).
  (ii) an EXACT paired sign-flip test per edge in BOTH currencies: all 2^16 = 65,536 sign
  assignments of the 16 per-seed paired differences, two-sided on the mean, one-sided on
  the norm; Benjamini-Hochberg at q = 0.05 over the measurable edges gives `M_rej`
  (mean) and `V_rej` (vector).
- Companion branch, first match, reported beside the primary verdict and never
  overriding it: `V_STRONGER` iff V_rej >= 2*M_rej and V_rej >= 5; `V_WEAKER` iff
  M_rej >= 2*V_rej and M_rej >= 5; otherwise `V_ALIKE`.

## 5. Gates and verdict (PREREG s5, unchanged, read here on the 69)

- FLOOR passes iff >= 14 of 69 edges have |mean_s d_j(s)| > 2F.
- SPLIT passes iff midrank Spearman rho(H1, H2) of the signed mean effect >= +0.40 and
  one-sided permutation p <= 0.001 (100,000 relabelings, PCG64 seed 24011).
- Both pass -> read section 6. Either fails -> **I_INSTRUMENT** (edge granularity too
  fine): NOT the registered escape. It retires only this measurement and promotes the
  GROUP-level arm (quartile edge groups, matched-size random subsets of the menu) to
  primary, as a new card.

## 6. Metric comparison (PREREG s6, verbatim; read ONLY if both gates pass)

For m in {abs, crofts, hop}: `AUC_m` = Mann-Whitney AUC of |mean effect| for used
(j in U_m) vs unused edges over the 69. Comparator `AUC_w,m`: the size-matched set of
the |U_m| heaviest edges by RAW synapse count. 10,000 bootstrap resamples over edges
(RNG seed 24012). ESCAPE iff for EVERY m, AUC_m - AUC_w,m <= +0.05. A metric WINS iff
AUC_m - AUC_w,m >= +0.10 with bootstrap 95% CI excluding 0. Otherwise NO_DECISION.
If the gates fail this section is recorded as NOT READ (not computed, not peeked at).

## 7. Predictions for A2 (registered before the run)

- Q1: the FLOOR gate FAILS (fewer than 14 of 69 clear 2F). Basis: only 1 of the 11
  HEAVIEST entries cleared at A1, and the other 58 are lighter.
- Q2: the SPLIT gate FAILS (rho < +0.40 or p > 0.001).
- Q3: the verdict is I_INSTRUMENT (scored separately because it is the card's branch).
- Q4: `e14` (1110->65443) remains the largest |mean effect| of all 69.
- Q5: companion reads V_STRONGER or V_ALIKE (V_rej > M_rej).

## 8. Compute and writes

7 workers x 2 threads, split BY ARM (9/9/8/8/8/8/8), worker ids 3-9, `cutwA` in every
worker, nice +15, hard stop 1700 s. A1's `edge_run.py` is not touched (A2 runs
`edge_run_a2.py`). Writes confined to banc/l240/ (`arms_w3-9.json`, `raw_w3-9.npz`,
`xm_w3-9.npz`, `gains/anchors/pools/done_w3-9.json`, `run_a2_w*.log`,
`results_l240_a2.json`), the LANE.md bracket, one LANE-LOG line and the research digest.
