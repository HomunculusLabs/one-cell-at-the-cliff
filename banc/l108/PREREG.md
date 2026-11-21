# L108 PREREG — free-rhythm-descriptor (zero rollouts, pure analysis)

Registered BEFORE any computation. All machinery inherited from stored
artifacts (L44 rule): raw_l105.npz (mm traces 3 arms x 51 seeds), raw_l101.npz
(cfn certified bit-identical, C0A tick 128 = 41st chain anchor),
results_l105.json, results_l101.json.

## Question

L105 found "RHYTHM WITHOUT STRUCTURE": free-run lock 48/48 (intrinsic rhythm
persists at zero drive) while antagonist structure is absent everywhere.
This card gives that rhythm its number: is the zero-drive rhythm the SAME
attractor family as the driven one (frequency distribution, seed spread,
Arnold-band placement) or a different intrinsic attractor?

## Registered metric definitions (pinned pre-compute, L34 window lesson)

- Code inherited VERBATIM from l105_verdict.py: `dom_ratio` = peak/median
  rfft power in the 0.3-10 Hz band; segment windows = SEGB
  [(0,2000,0.7),(2000,4000,1.4),(4000,6000,0.7)] @ DT .01 (20 s each).
- NEW read `dom_freq(x, w)` = freq of the band argmax (same band, same
  windows). Resolution: 20 s window -> 0.05 Hz bins; full 60 s -> 1/60 Hz
  bins. Disclosed, never smoothed.
- Windows registered: per-segment (lock machinery, cfn segments map to drive
  0.7/1.4/0.7) AND full-trace 6000. Stationarity read = per-seed dom_freq
  agreement across the three free-arm segments.
- Spectral ratio = dom_ratio as stored. Activity level = mm mean (descriptive).

## Certification (L85 rule, must PASS before any L108 pin)

This script's lock machinery on stored npz must reproduce EXACTLY:
- l105 tables free lock = 48, freenod lock = 48 (on raw_l105.npz, ALLFRESH 48)
- l101 anchors lock = 48 (on raw_l101.npz cfn = certified same traces)

## Registered expectations (descriptive card; branches disclosed, no gate)

- E1: cfn dom_freq sits at drive per segment (seg0/seg2 ~0.7, seg1 ~1.4 Hz;
  ± one 20-s bin .05) for ~= the lock count — lock 48 already says ratio>=10;
  the freq read should confirm WHERE.
- E2 (open, from L45b/L105 lineage attractors {0.7, 1.44, 1.42} on male +
  l65 female): free/freenod dom_freq lands somewhere in 0.7-1.6 Hz. The
  deliverable is the DISTRIBUTION (single attractor vs spread) + per-seed
  stationarity — either branch is informative, neither is a failure.
- E3: freenod ~= free per-seed (P2 max|d| .033, seeds 11/33 bit-identical ->
  identical freqs there by construction; seed 22 may differ; disclose count).
- No pooled-mean verdict over mixed regimes (L55/L63): report per-segment and
  per-arm tables, pooled only as distribution summary.

## Verify line (card)

freq table + seed spread; no new rollouts; LAB-INTENT.md L108.

## ADDENDUM 1 (registered post-hoc, BEFORE full-table compute)

Validity threat found by the 5-seed discovery probe: the free-arm in-band
argmax lands AT the 0.3 Hz band floor for a share of seeds; global peaks sit
at 0.10-0.30 Hz, i.e. the registered band edge truncates the dominant
component. The registered reads above stay as-registered; the following
DIAGNOSTIC reads (labeled DIAG in all outputs) are added to characterize the
slow component honestly:
- DIAG-A global peak: argmax over 0.02-10 Hz of the same spectrum, per
  arm/seed (full trace + seg1 window), + share of seeds whose band argmax
  equals the floor bin (validity-threat quantification).
- DIAG-B driven-line SNR for cfn: power at the exact drive frequency
  (bin nearest 0.7 for seg0/2, 1.4 for seg1) / band median — "line present
  but sub-dominant" vs "line absent", never eyeballed.
- DIAG-C freenod same reads (D-effect on the slow component).
