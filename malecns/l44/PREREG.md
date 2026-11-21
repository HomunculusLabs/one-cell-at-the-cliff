# L44 PREREG — entrain-history-protection (written before any run)

Question (LANE ideas-21, tick 60): L43 found NO stop dose parks an ENTRAINED
cord while L40's stop killed the intrinsic (never-entrained) cord in ~15 s.
Is protection GRADED in entrain-history length (a resistance curve) or
THRESHOLDED (basin entry)? Tick-61 amendment: record whether the stop ever
silences the NAMED walking-CPG core cells (IN17A001/INXXX466/IN16B036/
IN19A007/IN19B012 — 6 cells each in our annotations) specifically.

## Arms (all share ONE generator + ONE per-step noise tensor per seed, L36)

SETTLE=400 free (NO mech during settle — differs from l43, whose settle
entrained; L40's kill control settled free). WIN=8000. G=0.01, BETA=2,
D=0.05 tonic DNg100 (inert per L35, kept for machinery identity).
ENT_AMP=0.3 @ 0.7 Hz mech sinusoid, GLOBAL continuous phase.

Arm H ∈ {0, 5, 10, 20, 40} s (h=100·H steps):
- free   [0, 4000−h)
- entrain 0.7 Hz mech [4000−h, 4000)
- STOP: DNg88 += −8.0 on [4000, 6000)   (fixed 20 s, −8; all arms incl. H=0)
- post free [6000, 8000)

No hop anywhere (isolates history). Seeds 11/22/33.

## Metrics

late_ratio = rhythm2 peak/median power of mm[5500:6000] (l43 def; <5 = dead);
pre_ratio = mm[3500:4000]; kill_latency = first 1-s stop window with ratio<5;
S_med_during = median rolling S(Tr) over [4000,6000) (500-step windows/10);
x88min = min X[DNg88] over stop; core pool xc = mean X over the 30 core
cells (assert per-type count==6 in cord subset, non-empty hard) with
core_late_hist (mean X [3500,4000)), core_late_stop ([5800,6000)),
core_ratio_late = rhythm2(xc[5500:6000]), motor analogs; per-type windowed
means for the table.

## Gates (pre-registered)

- C0 anchor (L40 numeric, not bit-identical — stop onset 4000 vs L40's 2500,
  20 s vs 30 s): H=0 late_ratio < 5 in >= 2/3 seeds with finite kill_latency.
  3/3 = strong; fewer = disclose and still read the curve.
- C1 drives land + no leakage: (a) dm(H40 vs H0) = max|X diff| on [3500,4000)
  > 0, 3/3 (entrain lands); (b) prefix bit-identity max|mm_H − mm_0| == 0.0
  on [0, 4000−100·H) for H ∈ {5,10,20}, 3/3 (no arm wiring leak, L39-v1
  class); (c) x88min < 0.5 every arm/seed (stop un-pins).
- C2 the curve (median late_ratio + protected fraction = #seeds with
  late_ratio >= 5, per H):
  * THRESHOLD/basin-entry: some adjacent H pair jumps >= 10x in median
    late_ratio AND protected fraction <= 1/3 -> 3/3.
  * GRADED: median rises to protection with every step-gain < 10x, or >= 3
    distinct protected-fraction levels across H.
  * else MIXED — report the table, no forcing.
- C3 core cells: in protected arms (late_ratio >= 5), is core_ratio_late
  also >= 5 (core survives with motor) or < 5 (stop silences the CPG core
  SPECIFICALLY while motor output persists)? In killed H=0 seeds expect
  both < 5. Descriptive, P1-labeled (rate model).

Anchor expectations from L40/L43: intrinsic kill ratio<5 by ~15 s; entrained
cord late ratio 87-171 (43's history was 40 s). If H=0 does NOT kill in some
seed (20 s @ −8 shorter than L40's 30 s), that is data — disclosed, curve
still read on relative ratios + S_med_during.

Substrate assert 21,516 / 2,977,920; af assert 0.01<af<0.9 per arm (L30).
CPU-only; raw.npz checkpoint before analysis; no live changes.

## ADDENDUM 1 (post-run, DISCLOSED — 22:4x, before verdict rewritten)

C0 as written (late_ratio < 5) FAILED with 0/3 kills — and the failure is
INFORMATIVE: L40's OWN stored rel-arm numbers (results_l40.json win.rel
r_mm during its 30-s stop: 2a 334-590, 2b 183-874, never < 5) show the L40
kill was NEVER a rhythm-ratio kill — it was STRUCTURE: rel S 2b .13/.04/.04
vs ctl .45/.46/.52. The LANE text's "expect ratio < 5" mis-carried L40's
claim onto the ratio metric. Amended anchor (C0'): h0 S_med_during < 0.25
in 3/3 = the L40 structural kill reproduced at 20 s @ -8. Gates C1-C3
unchanged; C2's discriminator additionally read on S_med_during >= 0.25
(protection) per seed, and f_late as a secondary frequency-fingerprint
read. Post-run window caveat disclosed: S_med_after window is 20 s
([6000,8000)) vs L40's 44 s post window.
