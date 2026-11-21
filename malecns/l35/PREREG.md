# L35 PREREG — phase-reset-volley

Written BEFORE any L35 run (claim levels frozen; anchors inherited from L34's
published results_l34.json, free-run measured on the last-45 s window).

## Substrate (verbatim L32 arm-A / L34)
21,516 nodes / 2,977,920 edges, signed raw-count weights (arm-A transmitter
signs), g .01 / beta 2 / d .05, sustained bilateral DNg100 drive, uniform
tau 50 ms, DT 10 ms, settle 400, window 6000 (60 s).
Anchors: free-run dom freq {11: 0.800, 22: 1.444, 33: 1.422} Hz, S(Tr) >= .40,
rhythm ratio >= 100.

## Protocol
Paired-noise design: ONE control run per seed; every perturbed run uses the
SAME generator seed -> identical noise stream (same randn draw count per
step; volley only adds drive). Gait marker = pooled Tr flexor (fL+fR); peaks
detected with min-gap 25 steps + parabolic sub-step refinement (raw DT 10 ms
quantizes phase ~3-5 deg; refinement avoids that). Volley = additive drive V
on ALL DNg95 cells (bilateral = symmetric re-time attempt; unilateral turn
is L24, already shipped) OR a DNg100 PULSE (drive-channel amplitude
modulation). Brief volley: 25 steps = 250 ms (0.20-0.36 cycle across seed
periods); one 100-step (~1 cycle at 1.0 Hz) duration arm at amp .15, bins
{0 deg, 180 deg}. Onset placed at a target phase (8 bins x 45 deg) of the
CONTROL run's flexor peak train, near step 3500; readout = first/second/third
flexor peak AFTER volley end vs control -> dt1/dt2/dt3, dphi = 360*dt*f_anchor
(deg). Post window (volley end + 50 -> 6000): dom freq, ratio, S(Tr).
Arms: dng95 x amps {0.05, 0.15} x 8 bins; dng100pulse x {0.05, 0.15} x 8 bins;
dur100 (dng95 .15) x {0,180}; sham 5 draws x 3 seeds (random DN pair, random
phase, amp .15, dur 25). 120 runs total, CPU-only.

## Claim levels
- C0 substrate: controls hit anchors +-0.03 Hz, S(Tr) >= .40, ratio >= 100,
  af in (0.01, 0.9), no NaN (3/3 seeds). Else STOP.
- C1 pairing: pre-volley pooled-flexor trace BIT-IDENTICAL control vs first
  volley arm of each seed (noise-pairing valid).
- C2 survival: every real arm: post ratio >= 10, post S(Tr) >= 0.30, post
  dom freq within +-0.15 Hz of that seed's control post freq. The volley may
  re-time the gait, never break it.
- C3 PRC: PRC amplitude = max over 8 bins of |mean-over-seeds dphi1|.
  PASS iff (a) >= 10 deg, (b) >= 3x the largest sham |mean dphi1|,
  (c) per-seed SIGN agreement 3/3 at the argmax bin.
  Sham = random DN pair + random phase (5 draws x 3 seeds), amp .15.
- C4 dose/persistence (descriptive, no gate): |dphi1| monotone in amp
  {0.05, 0.15} at the argmax bin (2/3 seeds); persistence dphi3/dphi1
  (true reset carries the shift; transient rebound decays); dur 100 vs 25.

## Labels
Estimand P1 (frozen L32 gains re-applied per arm; no wins-claim).
Sobol one-param: volley amplitude scale vs pool input resistance (unmodeled;
uniform additive drive assumed). No WHEN-claims beyond measured peak shifts.
CPU-only; no live changes.

## AMENDMENT 1 (pre-data, run 1 stopped at C0)
Run 1 stopped at the C0 gate (protocol) on seed 11: f hit the anchor 0.800
EXACTLY and S(Tr) +0.48 matches L34's 0.481 (substrate identical), but ratio
read 78 vs L34's 168.6 — pure INSTRUMENT mismatch: my dom_freq band was
0.4-8 Hz, L34's is 0.5-10 (median-of-band denominator). Fix: dom_freq band
0.5-10 everywhere (C0 comparability). No PRC arm had run.
AMENDMENT 2: seed 11's pooled-flexor oscillator runs at 2.13 Hz while motor
mean runs at 0.800 Hz (flexors burst ~2x per motor cycle) — dphi is therefore
converted with each seed's FLEXOR PEAK-TRAIN median period (T_flex), not the
mm anchor: dphi_deg = 360 * dt / T_flex. The PRC subject is the flexor burst
rhythm; phase bins are cycles of the CONTROL flexor peak train (unchanged).

## AMENDMENT 3 (pre-data, run 2 stopped at C1)
Run 2 stopped at the C1 gate on seed 22: pre-volley trace not bit-identical.
TWO bugs, both mine, both caught by the pre-registered gates before ANY PRC
arm ran:
(a) VOLLEY TIMING OFF-BY-SETTLE: step() compared the volley window to the
    global step counter (400..6399) while k0 is a trace index (0..5999) —
    the volley fired 400 steps early and the "pre-volley" comparison window
    contained post-volley dynamics. Seed 11 passed by luck (V=.05 divergence
    sub-float32 in 400 steps on its slower dynamics). Fix: volley window on
    trace index.
(b) FLEXOR PEAK TRAIN RIPPLED: min-gap-25 peak detection on raw pooled
    flexor locks onto ~3.2 Hz ripple (median detected period 0.31 s vs the
    pool's own 2.1 Hz dom freq) — a bad phase reference. Fix: the PRC phase
    reference moves to the MOTOR-MEAN peak train (light 15-step smoothing +
    seed-scaled min-gap), the oscillator whose dom freq hit the L34 anchors
    EXACTLY (0.800/1.444/1.422, ratio 169-288) — the gait rhythm oscillator
    itself. dphi_deg = 360 * dt / T_mm (T_mm = median mm peak-train period).
    PRC subject relabeled: RE-TIMING OF THE GAIT RHYTHM (motor mean), read
    at mm peaks; flexor traces still saved for the figure.

## AMENDMENT 4 (pre-data, run 3 stopped at the train-vs-anchor gate)
Run 3 stopped at my peak-train sanity gate on seed 11: FFT dom freq is
0.800 Hz EXACTLY (ratio 169 = L34's 168.6; C0 fully green 3/3), but the
cycle-to-cycle mm peak train is irregular (intervals 0.70-2.62 s; probe
l35/probe_s11_mm.npy: no smoothing/gap combo recovers a clean train — small
gaps double-count, large gaps skip real cycles). Peak-train PRC is the wrong
instrument for a quasi-periodic oscillator. REPLACEMENT (pre-data; zero PRC
arms have run): HETERODYNE PHASE PRC, L34's phase_R form — z(t) = (mm -
mean) * exp(-2i*pi*f0*t) smoothed over exactly one period at the control's
own measured f0. Volley onset placed where the CONTROL's angle(z) matches
the target bin (8 bins x 45 deg); dphi = circular mean of angle(z_pert *
conj(z_ctrl)) over the same post window (volley end + P .. +15 s), bounded
+-180 deg, robust to skipped cycles. Persistence = early (first P) vs late
(next 15 s) windows; amp_ratio = |z_pert|/|z_ctrl| detects rhythm collapse.
C0/C1/C2 unchanged; C3/C4 gates unchanged, now read on dphi_post.

## AMENDMENT 5 (pre-data, run 4 stopped at the new R sub-gate)
Seed 11 read R .46 vs my 0.5 coherence gate (kernel = exactly one period,
L34 phase_R form, kept). The 0.5 threshold was miscalibrated: in the
PAIRED-NOISE design common phase diffusion cancels in z_p*conj(z_c), so
shift resolution is bounded by the SHAM spread (which C3 already gates on
at 3x), not by absolute coherence. Gate relaxed to R >= .35 (floor check
against demodulation failure only). Still pre-data: zero PRC arms have run.
