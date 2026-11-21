# L84 PREREG — seg0-entry-library (written BEFORE rollouts)

Card: LANE.md ideas-42 L84. Question: is the seg1 (fast-seg) structure draw
summarized by a LOW-DIM seg0-exit feature (a controller could SET it), or is
it trace-level (only re-rollable)? L82 proved the echo's fast-seg cost is
seg0-carried; L59 P5 measured entry S_L ↔ pooled duty (+.612, nohop); L83
added a speed axis. This card makes seg0 the ONLY thing that varies.

## Arms (seg1/seg2 IDENTICAL for every arm = l59 hynohop form; no hops anywhere)

- `base`  : l59 hynohop verbatim — seg0 chop 500-on/400-off @0.7 (AMPA .3).
- `cont`  : seg0 CONTINUOUS 0.7 entrain (AMPA[0:2000)=.3); seg1/2 unchanged.
- `nod`   : seg0 NO mech drive (AMPA[0:2000)=0); seg1/2 unchanged.
- `echo`  : seg0 = base chop + l66 content-cell echo ON during [0,2000) ONLY
            (drive[mech] += .1 * -1.0 * mA[k-5], mA = mean X over the Tr
            antagonist pools fL/fR/eL/eR — l82-verbatim), echo OFF from 2000.

Settle (400 steps, continuous .3 @0.7) and X0/noise stream identical across
arms and to l59/l82 (ONE generator per seed, one shared per-step randn).
Budget is NOT equalized here (mechanism card, not an intervention trial):
reported per arm (drive-on steps, amp mass, echo mass) in P5.

## Registered exit features (computed on the seg0 tail, before the k=2000 step)

- F1 SL_exit   = median S_L over TS ∩ [1500,2000)
- F2 SR_exit   = median S_R over TS ∩ [1500,2000)
- F3 both_exit = duty(both S>=.25) over TS ∩ [1500,2000)
- F4 mm_exit   = mean motor mass over [1900,2000)
- F5 cpg_exit  = mean X over the named CPG core pool (IN17A001/INXXX466/
                 IN16B036/IN19A007/IN19B012, l44 tick-61 set) over [1900,2000)
- F6 f0_exit   = dom_freq(mm[1200:2000)) — DESCRIPTIVE ONLY, never eligible
                 for the verdict.

Primary outcome Y1 = seg1 duty (both S>=.25 over TS ∩ [2500,4000)); secondary
Y2 = wpost duty ([3200,4000)). Label = Y1 >= .25.

## Registered prediction protocol (n = 4 arms x 16 census seeds = 64)

- P2 univariate AUC (Mann-Whitney) of each of F1-F5 vs the label, POOLED.
  Disclosed: a univariate rank AUC has no fit parameters — LOSO is vacuous;
  pooled only. The controller-relevant causal read is the WITHIN-seed one.
- P3 multivariate leave-one-seed-out: logistic regression on F1-F5
  (standardized on the 60 training samples), predict the held-out seed's 4
  samples; AUC over pooled held-out scores.
- P4 within-seed: per seed, Spearman rho of feature vs Y1 across the 4 arms;
  report mean rho + sign count (register sign>=0 in >=11/16 seeds as
  consistent); plus demeaned pooled AUC (feature-minus-seed-mean vs
  label-minus... vs outcome demeaned — rank AUC on deviations, descriptive).

## Registered verdict levels (pre-committed)

- SETTABLE (low-dim exit summary): some F in {F1..F5} with pooled AUC >= .75
  AND within-seed demeaned AUC >= .70 AND LOSO multivariate AUC >= .70.
- SEED-ONLY (trace-level): all F1..F5 pooled AUC < .65 AND demeaned AUC
  < .65 AND LOSO < .60. (Entry features correlate across seeds only — the
  draw rides seed identity, not a settable summary.)
- PARTIAL: anything between; name which reads separate.

## Registered discriminating expectations

- E1: SL_exit pooled AUC >= .65 (L59 P5 prior, entry S_L ↔ duty).
- E2 library spans: both_exit(nod) < both_exit(base) per-seed in >= 13/16
  (entry manipulation actually moves the exit state; if not, AUC question is
  underpowered — disclose, no verdict).
- E3 DISCRIMINATING: within-seed demeaned AUC of the best feature decides
  SETTABLE (>= .70) vs trace-level (< .60).
- E4: LOSO multivariate vs best univariate (does the feature LIBRARY add
  prediction beyond the best single summary?).

## Registered degenerate branches (L55 rule)

- DRAW-SEED-LOCKED: if Y1 is constant within every seed (all 4 arms same
  draw), demeaned AUC is undefined — that IS the verdict: the seg1 draw is
  seed-locked, entry manipulation never moves it. Report per-arm equality.
- NULL-VARIANCE: Y1 constant across all 64 → no AUC, arm table only.
- Echo-wiring failure: if C0x fails while C0a passes, verdicts restricted to
  base/cont/nod (disclose).

## Anchors (enumerated keys only; L59 anchor-gate rule)

- C0a: base arm == l59 raw hynohop BIT-IDENTICAL (mm + fL/fR/eL/eR), all 16
  seeds, max|d| == 0. If C0a fails: STOP before analysis, fix wiring.
- C0x: echo arm prefix [0,2000) == l82 raw hynohop_fb prefix BIT-IDENTICAL
  (mm + 4 sigs; the echo runs in both up to 2000), all 16 seeds.
- C0x2: first divergence of echo arm vs l82 fb == 2001 (echo off enters mech
  at 2000, motor one hop later — l66/l77/l82 stored law).
- C0P first-divergence laws (vs base, own run): echo == 6 (mA delay 5, motor
  one hop later), cont == 501, nod == 1.
  ADDENDUM 1 (pre-run, L44/L77 rule — anchor derived from the stored
  one-hop law, not the summary sentence): the amp/echo enters drive[mech]
  at k, and the compared traces (mm + Tr MN pools) are MOTOR pools that see
  the mech change one step later — l77 measured {6:16} for echo-vs-never at
  delay 5, l83 measured {2001:64} for a k=2000 drive change. So cont (amp
  differs at k=500) first-diverges at 501 and nod (amp differs at k=0) at 1.
  The originally drafted 500/0 forms are amended BEFORE any rollout.
- C1: settled active fraction in (0.01, 0.9) every arm/seed.
- C2: arms wired (dm > 0 vs base post-2000 for cont/nod — state diverged);
  echo vs base dm > 0.

Windows/windows-law: TS = arange(499, WIN, 10), S over 500-step trailing
windows (l59/l83 verbatim). CPU-only; raw npz checkpointed BEFORE analysis;
no live changes; sessions untouched.
