# L240 PREREG -- WHICH METRIC, decided by DYNAMICS (stage A1: the per-EDGE instrument on the carrier's 11 realised entries)

FROZEN 2026-11-24 17:14 EST (tick 274) BEFORE any arm construction, gain bisect or
rollout. sha256 in `PREREG.sha256`; the harness asserts it at import. Header time =
time of writing (+/- 2 min; the sha file's mtime is the record).

## 0. Question and staging

Card L240 + [L252 AMENDMENT, arXiv 2611.22234]. L221 left three nested first-hop
entry sets on the same wiring (abs 11, Crofts 30, hop-feasible 46 of a 69-edge menu).
The card asks which set a BIOLOGICAL routing claim should use, decided by a
DYNAMICAL referent: each out-edge's causal contribution to POOL ACTIVITY in the
rate model. The amendment gates that instrument (floor / cross-split / additivity)
BEFORE any metric comparison, because a null from an unusable instrument looks
exactly like a null.

The card is larger than one tick. Stages, all under this one frozen design:

- A1 (this run): the 11 realised abs entries as SINGLE-EDGE ablations + the
  11-as-GROUP arm + its fixed-gain twin + the noise-twin arm. A1 carries the
  ADDITIVITY leg (complete here) and REPORTS floor / split on the 11 (non-branching).
- A2 (later run, same file): the remaining 58 menu edges as single-edge arms
  -> the registered 69-edge FLOOR and SPLIT gates, then the metric comparison.
- A3 (later card): nonselective replication over the cohort's quartiles (the
  card's registered DEMOTION: the carrier sits at cohort percentile 0.286).
- A4: draft-sentence retirement, only on a registered escape.

No result of A1 licenses a cohort claim: the carrier is a SELECTED unit.

## 1. Substrate (disclosed choice)

`cutwA` -- the certified dynamics base (k=24, unfloored, 644,176 edges; stored gain
g_cutwA = 0.14365819573402408 must reproduce EXACT). NOT f4wA: L221 measured its
sets on f4wA, but no stored rollout traces exist for f4wA in this harness, so a
fresh f4wA run would have no bit-exact anchor. The used-sets therefore enter as
EDGE MEMBERSHIP LABELS: each label is realised on cutwA as the CSR entry
(source gi 1110 -> target gid) taken from L221's stored `used_edge_table`
(edge_j 4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67). A labelled edge with no cutwA
entry is scored FALSE BY UNMEASURABILITY and reported, never dropped silently.
The carrier's cutwA menu is larger than 69 (L220: 80) -- the count is asserted in
[69, 80] and recorded, and the extra sub-floor edges are A2 comparators.

## 2. Arms (one generator pair per seed: every arm sees the SAME per-step noise tensor = paired noise, L36)

- `cutwA`: base, stored gain.
- `e{j}` (11): exactly one CSR entry deleted from the carrier's row. Gain RE-BISECTED
  per arm (stored-form: lo .12 / hi .18, 24 halvings, settle-only AF, target
  .10905611018339793) = af-matched, so the operating point is not the intervention.
- `g11`: all 11 entries deleted as a GROUP; gain re-bisected.
- `g11f`: the g11 graph at the base gain (fixed-gain twin; readout-honesty law).
- `nf`: the base graph at the base gain, SAME initial state, INDEPENDENT noise
  stream (generators seeded seed+1,000,000 and seed+1,000,000+9000) = the
  paired-noise arm's own spread.

Deletion is asserted structurally per arm: values and columns equal the base's
minus exactly the removed index, the carrier's row count down by the number
removed, every removed value != 0. No twin is selected in A1 (the 11 are L221's
stored set; no choice is made here).

## 3. Seeds and anchors

Fresh paired block 3769-3784 (16), by the lineage rule: scan every `*.npz` under
peabrain-lab for `_<int>.npy` member tokens, take the first 16-block from 3641
stepping 32 with an empty intersection (311 archives, 1,034 tokens at PREREG time;
the harness re-derives it and this file PINS the block). Halves: H1 = 3769-3776,
H2 = 3777-3784. Anchors 801 / 901 (vs raw_l135, C0A-187a) and 3545 (vs the stored
L175 raws, C0A-187b): max |delta| == 0.0 over 22 keys + af BEFORE any fresh seed.
Any anchor failure = VOID, no fresh seed is read.

## 4. Readout (the referent is POOL ACTIVITY; no SI-index proxy)

- `P_a(s)` = mean over the pool-cell union of the 20 lineage leg pools
  (Ti/Tr/Ta/Sr/Pr x f/e/a/b x L/R) of the whole-window mean activity
  `xmean_a(s)[c]`. PRIMARY currency.
- Companion (cancellation-free): the 20-vector of per-pool means, `N_a(s)` =
  ||mean_s (P_pools,a(s) - P_pools,cutwA(s))||_2. Reported beside every primary
  number; the branches read the primary.
- Paired effect `d_a(s) = P_a(s) - P_cutwA(s)`; mean, SD, SE = SD/4, 95% CI by
  t(15) = 2.131449546.
- Descriptive only: per-pool signs, the lineage antiphase duty (Ti).

## 5. Registered legs

(1) FLOOR CHECK. `n(s) = P_nf(s) - P_cutwA(s)`; floor scale `F = SD_s(n)/4`
  (the SE a pure-noise twin has). Edge j CLEARS the floor iff |mean_s d_j(s)| > 2F.
  Chance clear rate 0.05 (binomial 69: 3.45 +- 1.81). 69-edge GATE (A2): FLOOR
  PASSES iff >= 14 of 69 clear. Saturation companion per edge:
  median_s |d_j(s)| / median_s |n(s)| (~1 = a noise redraw).
  A1: reported on the 11, non-branching.

(2) CROSS-SPLIT STABILITY. Rank edges by SIGNED mean effect in H1 and in H2;
  midrank Spearman rho; one-sided permutation p, 100,000 relabelings, RNG
  PCG64 seed 24011. 69-edge GATE (A2): PASSES iff rho >= +0.40 and p <= 0.001.
  Companion: sign-agreement fraction between halves (chance .50).
  A1: reported on the 11, non-branching.

(3) ADDITIVITY (complete at A1). `G(s) = P_g11(s) - P_cutwA(s)`, `S(s) = sum_j d_j(s)`,
  `R = mean G / mean S`. All off-floor tests use the same 2F. Branch, first match:
  - ADD_INERT_GROUP      |mean G| <= 2F (the 11 as a group do not move pool activity);
  - ADD_SUM_AT_FLOOR     mean G off the floor but |mean S| <= 2F;
  - ADD_SIGN_DISCORDANT  sign(mean G) != sign(mean S);
  - ADD_SUB              same sign, R < 0.5 (L25 target-overlap law predicts this);
  - ADD_CONCORDANT       same sign, 0.5 <= R <= 2.0;
  - ADD_SUPER            same sign, R > 2.0.
  Sign disagreement is also reported per edge: sign(mean d_j) vs sign(mean G), and
  the leave-one-in form (mean G - sum_{k != j} mean d_k) vs sign(mean d_j).
  Gain-form twin: G_f = P_g11f - P_cutwA; concordant iff sign(mean G) == sign(mean G_f).

If (1) or (2) fails at A2 the verdict is I_INSTRUMENT (edge granularity too fine),
which is NOT the escape: it retires only this measurement and promotes the
GROUP-level arm (quartile edge groups, matched-size random subsets of the menu).

## 6. Metric comparison (read at A2 only, and only if both gates pass)

For m in {abs, crofts, hop}: `AUC_m` = Mann-Whitney AUC of |mean effect| for used
(j in U_m) vs unused edges over the 69. Comparator: `AUC_w,m` for the size-matched
set of the |U_m| heaviest edges by RAW synapse count. 10,000 bootstrap resamples
over edges (RNG seed 24012).
- ESCAPE (registered by the card): fires iff for EVERY m, AUC_m - AUC_w,m <= +0.05
  -> the first-hop-funnel family is a property of the length metric; it is dropped
  from the draft and the retired sentences are named.
- A metric WINS iff AUC_m - AUC_w,m >= +0.10 with bootstrap 95% CI excluding 0.
- Otherwise: NO_DECISION (reported as such).
Signed-effect companions are reported, never branched on.

## 7. Predictions for A1 (registered before the run)

- P1 FLOOR: <= 3 of the 11 singles clear 2F (chance expectation 0.55).
- P2 SPLIT: rho_H1,H2 over the 11 edges < +0.40.
- P3 ADD: sign(mean G) == sign(mean S) and R < 1 (sub-additive).
- P4: the relay edge (j = 67, the L190 E-edge) has the largest |mean effect| of the 11.
- P5: the fixed-gain group twin is sign-concordant with the rematched group arm.

## 8. Gates, compute, writes

PREREG sha at import; C0A-187a / C0A-187b bit-exact; cutwA gain == stored EXACT;
every re-bisected gain inside .12-.18 (else DISCLOSED); structural CSR asserts;
finite traces; af in the window. Compute: 3 workers x 2 threads, split BY ARM
(w0 e4 e12 e13 e14 e25 | w1 e38 e39 e59 e62 e64 | w2 e67 g11 g11f nf), cutwA riding
in every worker, nice +15, hard stop 1500 s. Writes confined to banc/l240/ plus the
LANE.md bracket, one LANE-LOG line and the research digest.
