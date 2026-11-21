# L176 PREREG — composite-antiphase-metric re-read (ZERO rollouts, stored traces only)

Written BEFORE any composite number was computed (tick 217, 2026-11-21 ~14:1x EST).
Card: LANE.md L176. Source instrument: Guba, Kovalev, Zharinov, Demin, Kazantsev,
arXiv 2611.22639v1 (q-bio.NC, 17 Nov 2026), eq. (18):

    S_composite = (w_plv*PLV + w_amp*A + w_ph*Ph) / (w_plv + w_amp + w_ph) * g(P)
    g(P) = exp(-alpha * max(0, P - 2)),  P = max(P_flex_env, P_ext_env)

with PLV from the Hilbert analytic signal in a 1-10 Hz band, A = flexor/extensor
amplitude balance, Ph = proximity of the phase shift to 180 deg.

## 0. WHAT THE SOURCE ACTUALLY PUBLISHES (checked against the v1 HTML this tick)

Verified by reading arxiv.org/html/2611.22639v1 directly (not the digest):
* `w_amp ~= 0.963` IS published.
* `w_plv`, `w_ph` individually are NOT published.
* `alpha` is NOT published — the paper says only "with alpha optimized jointly
  with the weights".
* `A` and `Ph` are described in words ("amplitude balance", "phase shift
  proximity to 180 deg") with NO formula.
* `P` is defined: `max(P_flex_env, P_ext_env)`, envelope peak count, penalty
  above 2. The peak-detection rule is NOT published.

CONSEQUENCE, registered up front: this is NOT a case of "fix the weights to
their published values" (the card's wording, written from the digest). The
field-standard instrument is UNDER-SPECIFIED in its own paper, so every missing
piece is a DECLARED CONVENTION of ours, pinned here before computing, plus a
sensitivity ladder. We are testing our claims under a faithful reconstruction,
and we say so in exactly those words. No parameter is fitted on our traces
(an L162 A2/A3 post-hoc) — the ladder is reported, never selected from.

## 1. DECLARED CONVENTIONS (pinned, no fitting)

C1 Analytic signal: per trace, over the FULL 6000-step record, remove the mean,
   rfft, zero every bin outside [f_lo, f_hi], double the kept positive bins,
   irfft-free inverse via complex ifft => analytic band-limited signal.
   env = |z|, phase = angle(z). Pure numpy (no scipy on this box).
C2 Band, PRIMARY = the published 1-10 Hz. fs = 1/DT = 100 Hz.
C3 Band, ADDENDUM (registered here, not post hoc): 0.3-10 Hz, the lineage's own
   lock band. REASON, and this is a pre-run prediction: our substrate's drive
   segments are 0.7 Hz and 1.4 Hz, so the published 1-10 Hz band TRUNCATES the
   0.7-Hz segment's fundamental, which is exactly the L108 trap (an inherited
   band is a RATIO instrument, never a LOCATION instrument). Both bands are
   reported side by side; the 1-10 Hz read is labelled "as published".
C4 A = min(mean env_flex, mean env_ext) / max(...) over the window, in [0,1].
C5 Ph = 1 - |180 - |dphi_deg|| / 180, where dphi is the circular mean of
   (phase_flex - phase_ext) over the window, in [0,1]; 1.0 at exact antiphase.
C6 PLV = |mean exp(i*(phase_flex - phase_ext))| over the window.
C7 P: strict local maxima of the window envelope with value >=
   env_min + 0.25*(env_max - env_min) (a 25%-of-range prominence floor),
   counted per pool, P = max of the two.
C8 Weights, PRIMARY: w_amp = 0.963 (published), residual 0.037 split EQUALLY
   w_plv = w_ph = 0.0185 (sum 1.0). alpha PRIMARY = 1.0.
C9 Sensitivity ladder (reported, never selected): alpha in {0.0, 0.5, 1.0, 2.0}
   and weight splits {equal-residual (primary), all-residual-to-PLV,
   all-residual-to-Ph, uniform 1/3-1/3-1/3}.
C10 Window convention = OURS, unchanged: trailing 500-step windows at
   TS = arange(499, 6000, 10), restricted to the 0.7-Hz segment measurement
   masks (t >= seg_start + 500 and t < seg_end) with
   SEGB = [(0,2000,0.7), (2000,4000,1.4), (4000,6000,0.7)]. One convention,
   both sides decomposed (L46), exactly as the stored duty metric uses it.

## 2. SCOPE (this tick = stage (a); stage (b) appended to the card)

Stage (a), THIS tick: the BANC lineage arms the draft cites, from stored npz —
  l135/raw_l135.npz (13 table arms), l169/raw_l169.npz (9), l169b2/raw_l169b2.npz
  (6 table arms), pairs Ti and Tr, both sides, the arm's own 16-seed batch
  (the 801/901 anchors excluded from every statistic).
Stage (b), appended to L176 as a sub-item: the l65 Ti/Tr reads (different
  segment/window convention — a separate CERT) and the male L32 replication.

## 3. CELLS

CERT (gate, runs FIRST, before any composite number is printed): re-implement
  the stored metric from the stored traces and reproduce every arm's stored
  kL/kR/meanL/meanR in results_l135.json / results_l169.json /
  results_l169b2.json EXACTLY, including the rounding path (round per seed to
  3, then mean of rounded, rounded to 3). L85 rule: a bit-identical input
  anchor cannot catch a metric-code bug. A single mismatch halts the tick.

PRIMARY (identity axis, threshold-free): does the carrier-vs-twin paired sign
  survive under the composite? Pairs: (cutwA, silW) on l169 and l169b2 — the
  published mass-matched twin — and (f4wA, f4tw) on l169b2 (floor-4 twin).
  Statistic: per-seed window-mean composite, paired within seed, on the RIGHT
  side (the draft's readout side) and on the LEFT, reported separately.
  Registered cells: SIGN of the paired mean difference, the number of seeds
  with the carrier arm above the twin (k/16), and the paired mean with a
  jackknife CI. Threshold-free by construction, so no theta is needed.

SECONDARY (rank axis): Spearman rho between the arms' composite means and the
  arms' STORED duty means, per run, per side, per pair.

DEGENERATE BRANCH (registered, L55 class): if A (amplitude balance) is
  near-constant across arms (range < 0.05) then the composite is a monotone
  transform of its phase terms on our traces and the check is VACUOUS for the
  dominant term — disclose it as such and say which term carries the variance.

OPPOSITE BRANCH (registered): if a stored verdict FLIPS under the composite,
  the draft gains a metric-sensitivity paragraph and the claim is QUALIFIED,
  not quietly rewritten.

BAND-FLOOR DIAGNOSTIC (L108, mandatory): report the fraction of windows whose
  band-restricted envelope mean sits below 1% of the unfiltered window mean
  (i.e. the band ate the signal), per band. An "as published" read on a
  substrate whose fundamental is outside the band is an instrument-substrate
  mismatch finding, not a metric verdict.

## 4. PREDICTIONS (scored after)

Q1 The 1-10 Hz band will substantially attenuate the 0.7-Hz segment (band-floor
   diagnostic > 0 for a nontrivial fraction of windows), so the "as published"
   read will be noisier than the 0.3-10 Hz read.
Q2 A will NOT be near-constant across arms (the degenerate branch will not
   fire) because the lineage's partial/kill arms change pool amplitudes.
Q3 The carrier-vs-twin paired sign will SURVIVE on the right side under the
   0.3-10 Hz band (our identity claim is not an artifact of the correlation
   instrument), and the rank-order Spearman will be positive but < 0.9
   (the amplitude term adds information our S does not have).
Q4 g(P) will be near-1 for most windows at alpha 1.0 (a 5-s window of a 0.7-Hz
   rhythm carries ~3.5 cycles, so P will often exceed 2 — scored honestly; if
   P > 2 is the rule rather than the exception, g becomes a near-constant
   discount and that must be disclosed).

## 5. READ-ONLY DISCIPLINE

No npz is written. mtimes of every input npz asserted unchanged at the end.
Zero rollouts, zero RNG, no graph build, no live-service change, no draft edit
(the L190b manuscript child owns paper/DRAFT.md this tick).
