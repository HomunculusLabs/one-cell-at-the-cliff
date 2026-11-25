# L290 PREREG — WHICH METRIC, at GROUP granularity (L240 stage B: B1 group arms + B2 fixed-gain twins)

FROZEN before any L290 arm is constructed, before any L290 gain bisect or rollout, and
BEFORE any L290 set is materialised. The rules for the sets are pinned here; `sets.json`
is derived from these rules AFTER the freeze and the harness re-derives every set from its
own live menu and asserts equality before any bisect. No edit after freezing: amendments
only as new dated files. The sidecar `PREREG.sha256` carries the freeze timestamp.

## 0. Question and staging

L240 (tick 276, I_INSTRUMENT) found the per-edge causal ranking unreadable on all 69 menu
edges of carrier gi 1110 (FLOOR 4/69, SPLIT rho +0.30 vs .40) and left L221's question —
which first-hop entry set a routing claim should use: 11 abs / 30 Crofts / 46 hop — NOT
READ. L290 asks it at the group: does the set of edges a length metric ACTUALLY uses move
the fly's motor pools differently from (i) as many heaviest raw-synapse edges and (ii) as
many random menu edges?

Stages: B1 = the group arms (this file, s3) and B2 = five fixed-gain twins (s3). B2 is read
only after B1's verdict is fixed by s5; B2 enters no B1 branch. Stage A3 (the cohort's
quartiles) is NOT run here and is required before any claim if (b) fires.

## 1. What is already seen (declared design input, not L290 data)

- A1/A2 single-edge and g11 results on the same seeds (results_l240.json, results_l240_a2.json):
  G = E_g11 = +9.9618e-4 (4.34 F), S = +1.2465e-3, R = G/S = 0.799, e14 (1110->65443)
  alone = +1.25e-3 = 5.46 F = 1.26x the whole group, the other ten sum to ~0 at the floor.
- 8 edges are BIT-IDENTICAL no-ops for pool traces: j in N0 = {1, 2, 8, 9, 16, 21, 47, 55}.
- 14 is in all three L221 entry sets (checked against l221/static.json before this freeze).
- Consequence, faced here rather than after the run: every used-set contains the ONE
  reproducible edge, so "used-set vs random subset" is confounded with e14 membership by
  construction. This PREREG makes that covariate explicit (s5 SUPPORT condition, branch d).
- The five B2 edges carried the largest gain compensations of the menu (|dgain| 1.6e-4 to
  9.5e-4) and A1 separated edge from gain only for the 11-group (g11f concordant).
- Seeds are A1's block 3769-3784, deliberately REUSED so every arm pairs to the same stored
  cutwA traces. e14's single effect was established on these same 16 noise draws: a
  with-e14 subset reproducing it is a consistency check on the same draws, not an
  independent replication.

PREMISE CORRECTION (from stored l221/static.json, no rollout involved): the card calls the
three sets "nested". They are not: abs-11 and crofts-30 share 10 edges and differ by one
edge each way; crofts-30 is a subset of hop-46 (hop adds 16) and abs-11 is a subset of
hop-46. abs and Crofts are therefore nearly the same set and can hardly be told apart
dynamically except through those two edges; the informative size step is 30 -> 46.

## 2. Substrate, seeds, gates (inherited unchanged from the L240 PREREG + A2_ADDENDUM)

- cutwA, stored base gain g_cutwA = 0.14365819573402408 must reproduce EXACT; AF_T =
  0.10905611018339793; SETTLE, WIN = 400, 6000.
- Seeds 3769-3784 (16), anchors first: 801, 901 (bit), 3545 (L175 reproduction). The seed
  block is re-derived by the scan and asserted equal to 3769-3784 (l240/ and l290/ excluded).
- Every L290 arm pairs to A1's STORED cutwA traces (l240/raw_w0-2, xm_w0-2).
- Per-worker GATE (all before any fresh seed): anchors bit-exact (C0A-187a/187b, FC-150);
  the worker's own cutwA traces bit-identical to A1's stored ones (xmean + raw pool
  traces + af); its bisected cutwA gain == stored; F == A1's noise-twin floor
  2.2931491480943385e-4 (recomputed from A1 raws, |diff| <= 1e-18). Any failure = the
  worker is VOID and no arm of it is read.
- Menu: the carrier's out-edges on emask_wA, ascending target gid; position j among those
  with raw syn >= 4. CERT-MENU-A2 unchanged (menu_n in [69, 80], exactly 69 survive, the 11
  stored L221 (edge_j, target) pairs reproduce).

## 3. Sets and arms

Sets (rules pinned; materialised by `l290_sets.py` into `sets.json`; re-derived and
asserted in-harness):
- U_abs = L221 abs feasible_edges (11) = A1's g11 (EJ). U_crofts = L221 crofts
  feasible_edges (30). U_hop = L221 hop feasible_edges (46). Asserted sizes 11/30/46,
  |U_abs ^ U_crofts| = 10, U_crofts < U_hop, U_abs < U_hop, 14 in all three.
- Raw comparator RW_n (n = 11, 30, 46): the n menu edges with the largest raw synapse
  count; ties broken by ascending menu position (= ascending target gid). The number of
  edges tied with the n-th weight but left out is REPORTED (a boundary tie makes the
  comparator rule-dependent; the rule stands and the tie is disclosed).
- Random subsets r(n,k), k = 1..5, n in (11, 30, 46): numpy Generator(PCG64(29013)), drawn
  in that order, `choice(69, size=n, replace=False)`. Never re-rolled for any reason.
- contains14(S) = [14 in S]. Effective size eff(S) = |S \ N0|. Both nominal and effective
  sizes are reported for every arm (the card's effective-size rule), and every e14 label
  is fixed by the set, before the run.
- SAME-SET rule: if a comparator equals its used-set as a SET, it is the SAME arm: scored
  VACUOUS BY IDENTITY (neither agreement nor difference; excluded from that metric's
  branches and reported).

Arms (25 new rollouts, all paired to the same stored cutwA). Deletion = exactly the CSR
entries W[target, carrier] (out-edges sit in the TARGET rows), `_cut240` form VERBATIM
(one entry per target row, distinct rows, every removed value != 0, row counts down by
|S|, each target's raw edge unique). An absent or duplicate target = STOP, never a silent
drop.
- B1, gain RE-BISECTED per arm (A1 stored form: lo .12 / hi .18, 24 halvings, settle-only
  AF): `gc30` (U_crofts), `gh46` (U_hop), `rw11`, `rw30`, `rw46`, `r{n}k{k}` x 15.
  `g11` is NOT re-run: A1's stored traces are the abs used-set arm.
- B2, FIXED gain (no bisect; gain held at the stored base value): `e14f e25f e67f e12f e27f`
  — the five edges whose per-pool vector rejected in L240's companion, each exactly the
  single-edge graph at g_cutwA. Their re-bisected counterparts are A1/A2's stored arms.
- Not run: nf and g11f (A1 stored), the 11 cutwA-only edges (still deferred).

## 4. Readout (unchanged: L240 PREREG s4 / A2_ADDENDUM s4)

P_a(s) = pool MEAN over the 303-cell union of whole-window mean activity (PRIMARY);
per-pool 20-vector as the unsigned companion. d_a(s) = P_a(s) - P_cutwA(s), E_a = mean_s.
Arm-vs-arm: Delta_{a,b}(s) = P_a(s) - P_b(s), D_ab = mean_s, SE = SD/4; exact sign-flip
test over the 2^16 assignments of the 16 seed signs on the mean (two-sided p, and the
one-sided tail p_up for D > 0). Every branch contrast in s5 is arm-vs-arm; nothing is read
against zero, because the shared stored control carries a common component (+0.41 F/edge
vs the noise twin's own +0.69 F).

## 5. Registered comparisons, margins and branches

eps = 2F = 4.586298296188677e-4 (the floor in effect units). For metric m in
{abs, crofts, hop} with used-set arm U_m (g11 stored / gc30 / gh46), n_m = |U_m|, and
comparators C_m = {rw,n_m} U {r(n_m,k), k = 1..5} minus SAME-SET members:

  advantage  A_m(X) = sign(E_{U_m}) * D_{U_m,X}   (> 0: the used-set moves pool activity
  further in its own direction than X does).

  m EXCEEDS X        iff A_m(X) >= eps and p_up <= 0.01.
  m IS EXCEEDED BY X  iff A_m(X) <= -eps and (1 - p_up) <= 0.01.
  otherwise WITHIN/UNRESOLVED (reported with D, SE and both p; never read as equivalence
  on its own).

Verdict, FIRST MATCH over the whole card:
  (a) ESCAPE — every metric has no comparator it exceeds and none that exceeds it. The
      entry-set claim is a property of the length metric alone; the draft sentences are
      retired by name in the L221 follow-ups.
  (b) WINS — some metric m satisfies ALL of:
        raw:      A_m(rw,n_m) >= eps and p_up <= 0.001;
        random:   A_m(r) > 0 for every one of its non-vacuous random subsets, with
                  A_m(r) >= eps and p_up <= 0.01 for at least 4 of the 5;
        SUPPORT:  at least one e14-CONTAINING comparator exists among m's non-vacuous
                  comparators, and every e14-containing comparator is EXCEEDED by m.
      A metric that passes raw and random but has NO e14-containing comparator is labelled
      CONFOUNDED_BY_E14 and cannot win. If several win, name the one with the largest
      raw advantage. Then A3 (the cohort's quartiles) before any claim.
  (c) I_INSTRUMENT_AT_GROUP — fewer than K = 8 of the 15 random arms clear the floor
      (|E_r| > 2F, the A2 FLOOR definition on the same shared control). Groups of 11-46
      edges are still below this carrier's floor: the metric question is undecidable by
      single-carrier dynamics in this model class. STOP: no finer or coarser re-run on
      this carrier.
  else NO_DECISION — reported as such.

Companion branches (reported beside whichever verdict fires; they never override it):
  (d) SINGLE-EDGE CARRIER — over the 15 random subsets r (all sizes, U = the used-set of
      r's size): every r with 14 in r has |E_U - E_r| <= eps AND every r with 14 not in r
      has E_U - E_r >= eps, AND at least one r contains 14. (The used-sets' whole
      advantage over random subsets is e14 membership.)
  (e) INSTRUMENT WITHOUT e14 — among the random subsets without e14, at least 4 clear the
      floor. (Reported with its support count; if fewer than 8 e14-free subsets exist it is
      UNMEASURABLE.)
  (f) EDGE NOT GAIN (B2) — every fixed-gain twin is sign-concordant with its re-bisected
      arm and |E_f - E_b| <= 2F: 5 of 5 required.

## 6. Predictions (registered before any L290 rollout and before any set is materialised)

- S1  |RW_11 ^ U_abs| is 7, 8, 9 or 10 (the raw comparator is neither the abs set nor a
      stranger to it).
- S2  14 is in RW_11 (hence in RW_30 and RW_46, which are nested by construction), so the
      raw comparator of every metric carries e14 support.
- N1  exact no-ops inside U_crofts: 2-4; inside U_hop: 4-6 (hypergeometric means 3.5 and
      5.3 on 8/69; U_abs has 0, a known premise, not scored).
- R1  every random subset containing e14 clears the floor, and at most 1 subset without
      e14 clears it.
- R2  all three used-sets have E > 0 and |E_{U_m} - E_e14| <= 2F (E_e14 = A1's stored
      +1.25e-3): each group's effect is e14's effect within the floor.
- R3  verdict I_INSTRUMENT_AT_GROUP with companion (d) TRUE.
- R4  fewer than 8 of the 15 random arms clear the floor.
- R5  companion (f) holds (edge, not gain).

Each is scored TRUE / FALSE after the run; nothing above is edited to fit.

## 7. Compute, writes, honesty

4 workers (ids 0-3), 2 threads each, nice +15, hard stop 1700 s per worker, at most 2
workers per background call and at most 3 concurrent (tick 275-276 measured: 5 workers
pushed swap to its cap and slowed the fly duck; 7 in one call were memcg-killed). The fly
duck is never touched: same PID, NRestarts 0, /needs fast are probed before and after.
Writes are confined to banc/l290/ plus the LANE.md bracket, the LANE-LOG lines and the
research digest. Tick budget 35 min; any overrun is disclosed in the log line. A journaled
blocker is a valid tick; a fabricated number is the only failure.
