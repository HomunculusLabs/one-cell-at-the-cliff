# L79 PREREG — fast-window rehosting class (ideas-38, L52's named open lever)

Registered BEFORE any rollout. Tick 105, 2026-11-15.

## Question

L52: fast-seg (1.4 Hz) structure toxicity is entry-state-conditional and
dwell-deepened (entry structure dies with seed lifetime 6-30 s; "the lever
is NOT dwell and NOT amp — it is a different state class"). The one untested
shape: a POST-TRANSITION re-prime — one 5-s chopped head immediately after
the frequency step, before continuous fast drive. L58 measured the
structure-forming unit: 200-step (2-s) off-gaps between 5-s on-blocks
(off200 chop, +.193 duty07 vs the spec schedule).

## Design (machinery l77_census.py verbatim, FB lines removed)

- Arms (4): `hynohop` (l59 verbatim, anchor), `hybrid` (l59 verbatim,
  anchor), `reprime` = hynohop + off-gap, `hyreprime` = hybrid + off-gap.
- Off-gap: AMPA[2500:2700] = 0 on the treatment arms ONLY. Steps 2000-2500
  (5 s on at the 1.4 carrier) are IDENTICAL to baseline; steps 2700-4000
  resume continuous 1.4. The transition instant, carrier phase (PHI), and
  hop volley tables (hybrid arms) are untouched.
- Seeds: l45b census grid [11,22,33]+[101..113], n=16. CPU-only, shared
  per-step noise tensor across arms (one generator per seed).
- DRIVE_ON: 4800 baseline arms / 4600 treatment arms (the intervention
  REMOVES 200 on-steps; budget row P5).

## Anchors (all must pass before any verdict is read)

- C0a: hynohop bit-identical to l59/raw_l59.npz (mm + fL/fR/eL/eR),
  seeds {11,22,33}, max|d| == 0.0.
- C0b: hybrid bit-identical to l59, same form.
- C0P-1 (prefix fork): reprime-vs-hynohop and hyreprime-vs-hybrid
  max|d| == 0.0 over steps [0,2500) on mm + 4 traces, 16/16 each.
- C0P-2 (first divergence): first index with any mm/tr diff > 0 == 2501
  for both treatment arms, 16/16 each. Law: the AMPA gap changes mech
  drive at k=2500; motor reads it one hop later. Stored-verified form:
  l77 results json first_div == 6 = 5+1 for all 32 arm-seeds (echo at 5).
- C1: settled active fraction in (0.01, 0.9) every arm-seed.
- C2: dm > 0 (wired, not dead) every treatment arm-seed.
- AMPA/HOPA write-time asserts before any rollout (L58/L77 class):
  treatment tables equal twin tables outside [2500,2700); hop sums 2*40 on
  hybrid arms only; DRIVE_ON values exact.

## Windows (TS grid 499+10k; S windows 5 s = 500 samples)

- seg1 row VERBATIM (TS in [2500,4000)): continuity with stored l59/l77
  distributions (hynohop .375 / hybrid .402 means, same seeds).
- W_post PRIMARY: TS in [3200,4000) — every S window lies fully inside the
  resumed continuous drive [2701,4000]. The L52 dwell question: does
  structure survive 5-13 s of resumed continuous 1.4 after the re-prime?
- W_early: TS in [2500,3200) — straddle windows (0-40% gap content). The
  2-s gap cannot be isolated at 5-s S resolution; disclosed.
- Baselines are read at the SAME TS masks (their steps 2500-4000 are all
  driven; arms differ only in history). W_post split [3200,3600) vs
  [3600,4000) reported (L52 lifetimes 6-30 s bracket the resume).

## Registered reads (descriptive, window-scoped, never a pooled gate)

- P1 (primary): W_post duty distributions, paired per seed
  (reprime−hynohop, hyreprime−hybrid): deltas, mean/median/min, flips,
  P(duty>=.25) with Wilson. Claim levels: HELP = mean delta >= +.10 AND
  >= 11/16 deltas >= 0; HURT = mirrored; else NULL/INCONCLUSIVE.
- P2 (post-gap lock): per-block dom-freq err vs 1.4 on blocks [3000,3500)
  and [3500,4000); gate >= 12/16 arms with mean err <= .01 (L59 bar).
  Straddle block [2500,3000) reported, EXCLUDED by construction (contains
  the gap). Blocks [2000,2500) are C0P-1-identical to baseline.
- P3 (mechanism discriminator): W_early vs W_post delta ordering.
  Re-formation predicts W_early delta >= W_post delta (structure appears
  at the gap first); a re-roll lottery (L55/L56 law) predicts W_post
  moving with W_early flat/scattered. Descriptive sign-report.
- P4 (anatomy): W_post misses decomposed per side (SL-owned / SR-owned /
  both; L59/L46 form).
- P5 (budget): drive-on 4600 vs 4800 (−4.2%); the structure/lock/budget
  triple reported, never summed.

## Hops (L55/L56 re-roll law, pre-registered interpretation)

Hybrid volley tables verbatim on both hybrid arms — the pairing shares
volleys, isolating the gap. A W_post flip WITH W_early flat reads as
lottery, not re-formation; report which read carries any claim.

## Disciplines

raw_l79.npz checkpointed BEFORE analysis (l77 class); verdict re-derived
from stored artifacts by l79_verdict.py; no live changes; sessions
untouched.
