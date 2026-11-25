# L240 stage A1 -- VERDICT (tick 274, 2026-11-24 17:38 EST)

**Branch (leg 3, complete here): ADD_CONCORDANT.** The 11 realised abs entries, cut as a
GROUP, raise pool activity by G = +9.962e-4 = 4.34 F (95% CI [6.90e-4, 1.30e-3], 15/16 seeds
positive; +5.3% of the base 0.018691). Same sign as the sum of the singles
(S = +1.2465e-3), signed R = G/S = +0.799, inside [0.5, 2.0]. Fixed-gain twin sign-concordant:
G_f = +1.821e-3 = 7.95 F (CI [1.517e-3, 2.126e-3], 16/16; +9.7% of base).

**Floor and split (reported on the 11, NON-BRANCHING at A1; the 69-edge gates are read at A2):**
- FLOOR: F = 2.2931e-4 (noise-twin SD/4), 2F = 4.586e-4. Exactly ONE of 11 singles clears
  2F: `e14` (1110->65443, IN17B004-L) +1.251e-3 = 5.46 F (CI [8.68e-4, 1.63e-3], 15/16 positive,
  saturation 2.36). Next is the relay edge `e67` (1110->75494) at -3.50e-4 = 1.53 F
  (CI [-1.02e-3, +3.19e-4], 12/16 negative, saturation 1.32). The other nine sit at 0.07-0.9 F
  (saturation 0.47-0.98 = a noise redraw). FLOOR11 = 1 of 11, chance expectation 0.55.
- SPLIT: midrank Spearman of the signed mean effect, H1 (3769-3776) vs H2 (3777-3784):
  rho = +0.2727, one-sided permutation p = 0.2087 (100,000 relabelings, PCG64 24011);
  sign agreement 6/11 (chance 5.5). The single-edge ranking is NOT stable across halves.

**What ADD_CONCORDANT hides (the load-bearing read):** `e14` alone is 1.26x the group mean;
the other ten singles sum to -4.5e-6 (zero at this floor). So "the group behaves like the
sum of its parts" here means "the group IS one edge" on this readout -- R = 0.80 is not
evidence that ten floor-level edges add up. Per-edge sign disagreement vs the group: 4 of 11
(e12, e13, e59, e67 negative). Leave-one-in disagreement: 6 of 11, ALL six below 2F; the three
above-floor leave-one-in values (e13, e14, e67) agree.

**Companion, descriptive only (cancellation-free per-pool vector, threshold chosen in analysis):
** N_a = ||mean per-pool effect||_2, vector floor 0.00533. Above 2x floor: e14 0.0227,
e25 0.0158, e67 0.0120, e12 0.0117 (4 of 11); g11 0.0326, g11f 0.0393, nf 0.0031. So three
edges that are AT THE FLOOR on the pool MEAN redistribute activity among pools (e25:
Ti_fL -0.0087 / Ta_aR +0.0086; e67: Pr_aR +0.0090, Ta_bL/Ta_bR -0.0045). The scalar mean is
blind to redistribution; the registered referent is the mean, so the branch reads the mean.
Descriptive duty: e67 raises right-Ti duty 0.396 -> 0.681 (L190's finding, reproduced);
g11 0.623, mid14 0.003 -> 0.152.

**Predictions: 4/5.** P1 FLOOR11 <= 3 TRUE (1). P2 rho < 0.40 TRUE (0.27). P3 same sign and
R < 1 TRUE (0.80). P5 twin concordant TRUE. **P4 FALSE**: the largest single-edge effect is
`e14` (1110->65443), not the relay edge (1110->75494), which is second at 28% of its size.

## Gates (all green before any fresh seed was read)
- PREREG sha `d6c73be3a4c0621bb2db7f6ce6bc1a023be5fc93531772a6ae65937ca04298a0` equal at
  import in all three workers and at analysis. Frozen 17:12-17:14 EST, before any arm, bisect
  or rollout.
- C0A-187a (801/901 vs raw_l135): PASS max 0.0, 46 checks; C0A-187b (3545 vs stored L175
  raws): PASS max 0.0, 25 checks -- in each of the three workers.
- g_cutwA = 0.14365819573402408 stored EXACT. Re-bisected gains 0.142723-0.144508, all inside
  .12-.18; bisect af_final 0.10894-0.10905. Fresh-seed settle af 0.1003-0.1119, inside the
  window (0.095, 0.125).
- Lineage certificate: the `e67` arm's bisected gain 0.14314373373985292 equals L190's stored
  E-edge gain bit for bit -- same graph, same edge, same bisect path.
- cutwA traces bit-identical across the three workers; 1,124 stored traces are (6000,)
  float32 and finite; seeds [801, 901, 3545] + 3769-3784 (block absent from 311 archives).
- Structural CSR asserts passed for all 11 singles and the group (values and columns = base
  minus the removed index; each removed value != 0; exactly one entry per target row).
- Workers: exit 0, 717 s / 721 s / 564 s, 3 x 2 threads, nice +15, hard stop 1500 s not reached.

## Disclosures
1. **PREREG wording vs substrate.** PREREG section 2 says entries are "deleted from the
   carrier's row ... the carrier's row count down". cutwA's CSR is W[target, source], so each
   carrier->target entry lives in the TARGET's row; the carrier's own row has 13 entries (its
   in-degree). The first build's structural assert stopped on exactly that (menu read 13,
   outside [69, 80]) BEFORE any bisect or rollout; the harness then deleted W[target, carrier]
   by L190's recipe and asserts the target row's count. The functional object is the
   registered edge (confirmed by the e67 certificate). The PREREG file is left frozen.
2. **Harness fixes after the freeze, all caught by asserts before any rollout:** a missing
   seed-block alias, the CSR orientation above, a regex escape, and the noise-twin wiring
   index. No gain, selection or rollout existed when they were made.
3. **Analysis-script corrections before any reporting.** The first final.py used branch labels
   that are NOT in the PREREG (ADDITIVE / UNRESOLVED / NON-ADDITIVE, unsigned R) plus a
   mis-sized worker plan, hand-typed anchor counts (L190's 92/50 instead of this run's 46/25),
   a pool-dict compare that included the worker id, and a trace-key test that matched nothing
   (0 traces "verified"). Corrected to the PREREG's six-way first-match branch with signed R;
   results_l240.json was rewritten, numbers unchanged (same raws).
4. `sc25` rides in the harness for lineage completeness but is not an L240 arm, so the anchors
   cover the base graph only.
5. **Budget:** about 45 min against the 35 min budget (12 min of worker wall time, the rest
   reading and the fixes above).
6. The carrier's cutwA menu is 80 edges (recorded; PREREG section 1 anticipated it). The
   metric comparison is over L221's 69-edge menu; the 11 cutwA-only edges are comparators.
7. **Three edge counts, not reconciled from the artefacts.** PREREG section 1 says cutwA has
   644,176 edges; L220's stored count is 644,177; the harness reports 639,164 after removing
   its 77 cut columns. The differences are plausibly the edges into the removed cells and the
   lineage's one added edge, but I did not check that arithmetic.

## Not licensed by A1
No metric comparison (that is A2: the remaining 58 menu edges, the 69-edge FLOOR gate
">= 14 clear" and SPLIT gate "rho >= +0.40 and p <= 0.001", then AUC vs the raw-synapse
comparator). No cohort claim (A3: the carrier is a selected unit, percentile 0.286). No draft
retirement (A4, escape only).

## Hand-off to A2 (for the next tick; fix in an addendum BEFORE any A2 rollout)
- The 11-on-11 numbers say the single-edge ranking is at the floor and unstable; whether that
  is I_INSTRUMENT is decided by the 69-edge gates, not here.
- Register the readout question first: the pool MEAN (the referent) and the unsigned per-pool
  VECTOR rank different edges (e25 and e67 are floor-level on the mean, 2-3x the vector floor).
  A2 needs one declared primary and the other as companion, chosen before its data exist.
- Reuse seeds 3769-3784 with the stored cutwA and nf traces as the pairing partners so all 69
  edges share one base; the singles are independent, so 5-6 single-thread workers fit a tick.

## Files (banc/l240/)
PREREG.md + PREREG.sha256; build.py -> edge_run.py (sha 29bb9ad627e0a921); checkpoint.py;
raw_w0-2.npz, xm_w0-2.npz, gains_w*.json, arms_w*.json, anchors_w*.json, pools_w*.json,
done_w*.json, run_w*.log; final.py -> results_l240.json (sha 838f9e0b5f5e739d) + final_stdout.txt.

---

## A2 PROGRESS -- tick 275, 2026-11-24 19:25 EST (stage A2 SLICED: 26 of 58 new arms banked, NO effect read)

The A1 hand-off asked for an A2 addendum BEFORE any A2 rollout, then the 58
remaining menu edges. The rollouts did not fit one tick on this box, so this
section records what was frozen, what was banked and verified, what was NOT
read, and the exact resume. The final A2 verdict is still to come.

### Frozen before any A2 arm construction, bisect or rollout
- `A2_ADDENDUM.md`, sha256
  `0c55e34d2d63c3b62494645ff5e8ba6fbadc5813d08a79bd6ff0a29b255c56a3`
  (pin file written 18:52:07 EST). DISCLOSURE: its header says "19:08 EST" --
  a mistyped clock in the header. The file's own mtime and the sha pin are the
  record; the file is frozen and was NOT edited to fix the header.
- A1's `PREREG.md` (sha d6c73be3...98a0) and `edge_run.py` (sha 29bb9ad6...)
  are untouched. `build_a2.py` asserts both and builds `edge_run_a2.py` from
  the same pinned lineage slices (57-line diff vs the A1 harness: the worker
  plan, the menu/plan asserts, DRY logging; g11/g11f/nf are not rebuilt).
- DRY run 18:52:16-24, before any rollout: menu_n 80, menu69 69, cert_menu 11,
  unmeasurable []. Every real worker re-derives and logs the same numbers.

### What the addendum fixes (summary -- the file is authoritative)
1. Readout: PRIMARY stays the pool MEAN. Switching to the vector after A1's
   11 edges were already seen would pick the readout on the data. The unsigned
   per-pool VECTOR is the COMPANION, with its own floor and an exact sign-flip
   test per edge + BH over 58 -> V_STRONGER / V_WEAKER / V_ALIKE. Mean wins ties.
2. Seeds 3769-3784 are re-used; A1's STORED cutwA traces are the pairing
   partners, admitted only if A2's re-run cutwA is bit-identical to them.
3. Arms: the 58 remaining menu edges as single-edge cuts with re-bisected gain
   (A1's bracket and halvings); cutwA re-run in every worker. The 11 cutwA-menu
   edges outside the 69 are raw syn < 4 and are NOT run -- recorded here, not
   dropped silently; no registered gate reads them.
4. Gates, unchanged and registered on the 69: FLOOR >= 14 singles clear 2F
   (chance expectation 0.55); SPLIT rho(H1,H2) >= +0.40 with p <= 0.001. Any
   failure -> I_INSTRUMENT (the instrument retires, not the science) and the
   group-level leg is promoted.
5. Metric comparison only if both gates pass: ESCAPE iff every metric's AUC is
   within +0.05 of the raw-synapse comparator; WINS iff some metric beats it by
   >= +0.10 with a bootstrap CI excluding 0; else NO_DECISION. Signed
   companions are reported, never branched on.
6. Predictions registered: Q1 FLOOR fails; Q2 SPLIT fails; Q3 I_INSTRUMENT;
   Q4 e14 stays the largest single-edge effect; Q5 more vector than mean
   rejections.

### Banked and verified this tick (`final_a2.py` PARTIAL -> results_l240_a2_partial.json)
- Workers 3, 4, 5 exit 0 at 19:20:07 / 19:20:06 / 19:18:30
  (1297.7 / 1295.9 / 1199.0 s), cutwA + 9 / 9 / 8 new single-edge arms:
  e0-e3,e5-e9 | e10,e11,e15-e21 | e22,e23,e24,e26-e30 = 26 arms x 16 seeds.
- Anchors: C0A-135 (46 checks) and C0A-175 (25 checks) pass at max 0.0 in all
  three workers; the stored base gain 0.14365819573402408 reproduces exactly.
- Pairing gate for the seed reuse: A2's cutwA traces are BIT-IDENTICAL to A1's
  stored cutwA traces -- 228 raw control arrays, the settled means and the af
  scalars all equal (the script halts otherwise).
- Traces: 3,016 control traces and 15,080 pool traces (20 pools x 754
  arm-seeds, A1 + A2), every one (6000,) float32 and finite. The finite check
  inherited from A1's analysis matched only the 4 control traces per arm-seed;
  it was widened to the 20 pool traces after the first PARTIAL run and the run
  repeated. Verification only -- PARTIAL mode computes no effect.
- Gains: all 26 inside the PREREG bracket, 0.1427106 (e27) to 0.1438324 (e0).
  Six are bit-identical to the base gain (e1, e2, e8, e9, e16, e21): the cut
  does not move the settle-only active fraction at bisection resolution. That
  is an operating-point fact from the gain tables, NOT the pool readout, and
  it enters no gate.

### NOT done, NOT read
- 32 of the 58 new arms have no completed run: workers 6 and 7
  (e31-e37,e40 | e41-e48) and workers 8 and 9 (e49-e56 |
  e57,e58,e60,e61,e63,e65,e66,e68).
- No effect was computed. The 69-edge FLOOR and SPLIT gates, the metric
  comparison and predictions Q1-Q5 are UNREAD and stay registered.
- Box at 19:21 with nothing of mine running: 7.7 GiB available, swap 29.8 of
  31.2 GiB used.

### Compute incident (disclosed)
- 18:52:2x -- the addendum's plan, 7 workers in ONE background call, was killed
  at 18:52:47 by the kernel's cgroup OOM killer. Every background call is its
  own scope with MemoryMax = 4 GiB; a worker is 1.22-1.25 GiB. No worker
  reached an exit line and every log ended on the torch warnings. Found with
  `journalctl -k` (constraint=CONSTRAINT_MEMCG, oom_memcg=.../
  hermes-worker-proc_d2e94e2800e9.scope).
- Re-launched as batch A (workers 3,4,5 at 18:58:33: 3.69 GiB anon under the
  4.00 GiB cap, 751 limit events, 0 kills) and batch B (6,7 at 19:00:17, a
  second scope).
- With five workers: swap 31.2 of 31.2 GiB (0 free), 76-84 s per seed against
  ~55 s, workers 3 and 4 projected to hit the 1700 s hard stop about a minute
  short of the end, and the fly duck's /needs stopped answering quickly. Batch
  B was therefore stopped on purpose at 19:07:16 (workers 6 and 7 at their
  first seed; partial files removed, logs kept as run_a2_w6/w7.stopped-1907.log).
- Fly duck /needs, every probe 200 OK, timed: 0.58 s and 0.79 s, then > 5 s
  (my own 5 s client timeout) and 4.15 s with five workers up; 2.89 s and
  15.08 s with three up; 6.3 s, 0.23 s, 0.06 s with none. Same PID, NRestarts
  0. Measured at 19:17: 135 MiB resident and 1.6 GiB in swap -- the slowness
  is that swapped working set competing for RAM, not CPU (CPU pressure 0.00).
  Swap read 30.2 of 31.2 GiB used BEFORE the re-launch and 30.4 GiB 43 s after
  batch A started, so the pressure is not this tick's alone; this tick made it
  worse and I have no clean no-load baseline from before the runs.
- Tick ran ~47 min against the 35 min budget.

### Resume (next tick: ~20 min of rollouts + analysis)
1. From banc/: `sh l240/launch_a2.sh 6 7` and `sh l240/launch_a2.sh 8 9`, each
   as its OWN background call (<= 2 workers per call = the 4 GiB cap; four
   concurrent = ~5 GiB). Read `free -m` first: if available < 8 GiB, run one
   pair at a time.
2. When all seven `l240/exit_a2_w*` files exist: `python l240/final_a2.py`. It
   selects FINAL by itself from the exit files and reads the gates; a missing
   exit file keeps it in verification-only mode, a non-zero one halts it.
3. Then append the A2 verdict here, the LANE.md bracket, the LANE-LOG line and
   the research digest.

### Files added in banc/l240/ this tick
A2_ADDENDUM.md + A2_ADDENDUM.sha256; build_a2.py -> edge_run_a2.py (75,404 B);
dry_a2_w3.log; launch_a2.sh; final_a2.py -> results_l240_a2_partial.json +
partial_a2_stdout.txt; run_a2_w3-5.log, exit_a2_w3-5, raw_w3-5.npz, xm_w3-5.npz,
gains/arms/anchors/pools/progress/done_w3-5.json; run_a2_w6/w7.stopped-1907.log;
launch_a2*.started.

## A2 VERDICT -- tick 276, 2026-11-24 20:53 EST (stage A2 FINAL: all 69 edges, I_INSTRUMENT)

### Admission (derived from artefacts, not hand-selected)
- Seven `exit_a2_w3..w9` files, all 0. 58 arms built over workers 3-9 (10/10/9/9/9/9/9).
- 5,368 control traces + 26,840 pool traces finite; cutwA gate xmean / raw / af all
  identical to A1's stored traces (532 raw arrays compared).
- PREREG sha d6c73be3... and ADDENDUM sha 0c55e34d... asserted inside the script.
- Workers 6-9 this tick: 1357 / 1355 / 1350 / 1342 s = 79-80% of the 1700 s hard stop,
  2 threads each, four concurrent (two background calls of two), nice +15.

### Gates (registered; read on all 69)
- FLOOR: 4 of 69 clear 2F, bar >= 14 -> FAIL. e14 +5.46 F, e27 +2.91 F,
  e45 +2.40 F, e43 +2.19 F. By subset: 1 of 11 seen at A1, 3 of 58 new. Chance at a
  2-SD bar gives 3.1 of 69 (4.6%); A1's own rate scaled up gives 3.45.
- SPLIT: midrank Spearman H1 x H2 rho +0.2996 (bar +0.40), one-sided permutation
  p 0.00644 (bar 0.001), sign agreement 46 of 69 -> FAIL.
- VERDICT: I_INSTRUMENT. The metric comparison is NOT READ (never computed, never
  written): `metric_comparison = {"status": "NOT READ"}`.

### Predictions (registered before the data): 5 of 5
Q1 FLOOR fails TRUE (4 < 14) | Q2 SPLIT fails TRUE (rho 0.2996 < 0.40, p 0.0064 >
0.001) | Q3 I_INSTRUMENT TRUE | Q4 e14 stays the largest |mean effect| TRUE |
Q5 V_rej > M_rej TRUE (5 > 1).

### Companion (declared in the addendum; never overrides the verdict)
- Vector floor floorN 0.0053337 (identical to A1's descriptive 0.00533). V69 5, V58 1.
- Exact paired sign-flip test, all 2^16 assignments enumerated: MEAN rejects 1
  (e14, p 6.10e-05 = 4/65536); VECTOR rejects 5 (e14 3.05e-05, e25 3.05e-05,
  e67 9.16e-05, e27 7.02e-04, e12 7.93e-04) -> V_STRONGER, as registered
  (V_rej >= 2*M_rej and V_rej >= 5).
- MEAN: sum of the 69 signed means +6.520e-3; e14 alone is 19.2% of it; top five by
  |mean|: e14, e27, e45, e43, e49.

### What the companion does NOT license (post hoc, unregistered, non-branching)
1. Four of the five vector rejections are edges SEEN at A1 on these same 16 seeds --
   A1's descriptive companion named exactly e14, e25, e67, e12. Their exact p-values
   are a new statistic on seen data, i.e. descriptive. On the 58 UNSEEN edges alone:
   vector rejects 1 (e27, p 7.02e-04 against a rank-1 bar of 8.62e-04 = 0.81x),
   mean rejects 0 (smallest e43 2.81e-03). The companion's DIRECTION holds on unseen
   edges; its registered branch bar (>= 5) is met only by counting seen edges.
2. A vector rejection beside a null mean is a seed-stable per-pool PATTERN whose mean
   cancels: e25 +0.07 F with 7 of 16 seeds negative, e12 -0.21 F with 8 of 16.
3. The gain path is not separated at single-edge level. All five vector-rejected arms
   were re-bisected, with |delta gain| 1.6e-4 to 9.5e-4 -- among the largest in the
   menu (e27 -9.48e-4, e12 -9.35e-4, e25 +8.50e-4) -- while 15 of 69 arms needed no
   compensation at all. So a per-arm pattern may be the gain compensation (the
   operating point) as much as the edge. A1 separated the two only for the group
   (fixed-gain twin +7.95 F beside the re-bisected +4.34 F).
4. Shared-control caveat: every arm is paired to the SAME stored cutwA, so per-edge
   effects share a common component. The 69 signed means average +0.412 F (43 of 69
   positive, sum +28.4 F) -- BELOW the noise twin's own offset against that same
   control (+0.691 F, SE 1.000 F). A shared offset of that size accounts for the whole
   sum, so the SIGN of the sum of singles is not evidence of a collective effect.
   Arm-vs-arm contrasts only; never arm-vs-zero for a group claim.

### Disclosures
1. ANALYSIS-SCRIPT CORRECTION, before any output. The first FINAL run of
   `final_a2.py` (sha256 5c509648c1038028...) halted on its own sign-matrix
   self-check (line 251): line 250 built row 0 of the 2^16 sign matrix as all -1
   while the check (and the mean self-check below it) needs all +1. Stdout was
   0 bytes and no results file was written, so no gate or effect had been seen.
   Fixed by the global negation `1 - 2*bit` (file now sha256 38b5839b19ee5efc...),
   which leaves the exact two-sided test unchanged: the 2^16 assignments are closed
   under global negation, so |SGN @ d| has the same multiset and every p-value is
   identical (checked on a random vector before the re-run). PREREG, ADDENDUM and
   both harnesses are unedited. Kept: `final_a2_pre_fix_tick276.py`, and the halted
   run's empty stdout + traceback as `final_a2_run1_halted_{stdout,stderr}.txt`.
2. `posthoc_a2.py` was written before the effects existed; `posthoc_a2_b.py` was
   written after seeing them. Both unregistered and non-branching.
3. Tick ran ~44 min against the 35 min budget (23 min of rollouts, then the halt
   and its fix).
4. Compute: four workers, nice +15. Swap free fell to 41-82 MiB during the run
   (28-30 GiB held by other processes); fly duck /needs 0.86-7.15 s during the run,
   200 on every probe, same PID 3896241, NRestarts 0.

### What this decides
- The single-edge causal contribution to pool activity on this carrier's 69-edge menu
  sits at the measurement floor. One edge is reproducible: e14 (1110 -> 65443,
  20 synapses) +5.46 F, 15 of 16 seeds positive, CI [3.78, 7.10] F. Three more clear
  2F, which is what chance gives at a 2-SD bar.
- The cross-half ranking is better than chance and below both registered bars:
  weakly stable, not stable enough to carry a ranking.
- So the metric comparison is not read. L221's three nested first-hop entry sets
  (11 / 30 / 46 of 69) are neither confirmed nor retired by dynamics at single-edge
  granularity. I_INSTRUMENT is not the ESCAPE.
- The question moves to GROUP granularity, the promotion the addendum registered,
  as a NEW card (L290). No finer re-run on this carrier.
- A4 (retirement) is escape-only and is not triggered. A3 (cohort quartiles) has no
  single-edge finding to transport; the group-level card inherits the requirement.

### Files (banc/l240/)
`results_l240_a2.json` (sha256 fcbf91d043571a0e...), `final_a2_stdout.txt`,
`final_a2.py` (corrected), `final_a2_pre_fix_tick276.py`, `final_a2_run1_halted_*`,
`posthoc_a2.py` -> `posthoc_a2.json`, `posthoc_a2_b.py` -> `posthoc_a2_b_stdout.txt`,
`run_a2_w6-9.log`, `exit_a2_w6-9`, `raw_w6-9.npz`, `xm_w6-9.npz`,
`gains/arms/anchors/pools/progress/done_w6-9.json`, `run_a2_w8/w9.oom-1852.log`
(the 18:52 OOM logs, renamed not deleted).

### Post-hoc addendum -- tick 276, 21:05 EST (after the A2 verdict above; unregistered, non-branching)
Written after the gates were read. Nothing here changes the verdict.

1. EIGHT OF THE 69 EDGES ARE EXACT NO-OPS. e1, e2, e8, e9, e16, e21, e47, e55:
   mean, per-pool vector and CI are all exactly 0, because all 320 pool traces of
   each arm (20 pools x 16 seeds x 6000 steps) are BIT-IDENTICAL to the base's
   stored traces (max |diff| 0.0; `posthoc_a2_d.py`). Not a silent non-deletion:
   the harness record shows a removed edge with a nonzero effective weight for
   every one (1.79-3.66 = log1p of 5-38 synapses), all sign +1, csr index and
   target recorded (`posthoc_a2_e.py`). So deleting a 35-synapse (e1 -> 4945) or
   a 38-synapse (e47 -> 68414) excitatory out-edge of the carrier changes
   nothing the leg pools ever see.
2. MOST OTHER "EFFECTS" ARE DIVERGENCE LOTTERIES. Number of an arm's 320 pool
   traces still bit-identical to the base: e37 302, e61 285, e42 267 (near
   no-ops: identical on most seeds, a few depart) against e43 26, e14 24, e45 23,
   e27 14. An arm either tracks the control exactly or departs; the tiny mean of
   a near no-op is a handful of departing seeds, not a small push.
3. THE REGISTERED FLOOR IS MILDLY CONSERVATIVE, AND THE VERDICT DOES NOT MOVE.
   F comes from the noise twin (base graph, INDEPENDENT noise stream) while the
   arms are paired to the control; the arms' own paired SE over the 61 non-zero
   arms is 0.08-1.50 F (median 0.65 F). Against each arm's own paired SE, 5 of 69
   clear 2 SE (e14, e27, e45, e43, e18) against 4 under the registered floor;
   uncorrected exact sign-flip p < 0.05 for 4 of 69 (chance 3.45). Either way the
   count is chance-level (`posthoc_a2_c.py`).
4. CORRECTION TO `posthoc_a2.py`. Its sign-count histogram counts an all-zero
   arm as "16 of 16 positive" (`(d < 0).sum()` = 0), so its "12 edges with >= 15
   of 16 seeds one-sided" is the 8 exact no-ops plus e14, e42 (+0.14 F, own SE
   0.19 F), e37 (-0.08 F) and e61 (+0.01 F). Only e14 is an effect. Classify
   exact zeros before any sign count.
5. NOT DONE ON PURPOSE. The no-ops were not crossed with the three metric sets:
   that is the registered metric comparison in another currency, and it is NOT
   READ. It is registered FIRST in L290's PREREG instead.
6. PROBE DISCLOSURES. The first run of `posthoc_a2_d.py` keyed the base traces
   by pool suffix only (the 20 pools are 5 classes x 4 suffixes) and compared Ti
   traces against another class; its output is kept as
   `posthoc_a2_d_run1_INVALID_key-collision_stdout.txt` and was not used. The
   chance count quoted as "~3.2 of 69" in the text above is 3.1 (4.6% of 69);
   corrected in place.

Files: `posthoc_a2_b.py` -> `posthoc_a2_b_stdout.txt`, `posthoc_a2_c.py` ->
`posthoc_a2_c_stdout.txt`, `posthoc_a2_d.py` -> `posthoc_a2_d_stdout.txt`,
`posthoc_a2_e.py` -> `posthoc_a2_e_stdout.txt`.
