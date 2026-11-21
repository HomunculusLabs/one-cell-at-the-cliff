# L33 PREREG — steering-modulated-rhythm (written before any scan)

Question: does the L32 self-pacing cord regime (sustained bilateral DNg100,
frozen g=0.01 / beta=2.0 / d=0.05, arm A signs) accept steering as GRADED
MODULATION of an ongoing rhythm, or does a unilateral steering bias break
the self-ordered antiphase?

Steering channel: DNg95 unilateral tonic bias (L24: ipsi flexor channel,
excitatory onto Ti/Tr flexors). Bias amps = d* x {0.25, 0.5, 1, 2, 4}.

Claim levels (decided BEFORE the run; P1-labeled descriptive — frozen
real-tuned params reused verbatim on every arm, no per-arm re-tuning):

- C0 anchor: base arm (steer 0) reproduces L32: S(Tr) pooled > +0.15 each
  seed, rhythm_ratio(motor-mean) > 5.
- C1 survival: at EVERY graded amp, per-seed rhythm_ratio > 5 and pooled
  S(Tr) > +0.15 (antiphase survives modulation).
- C2 graded: |turn_flex| (L-vs-R flexor mass asymmetry, post-transient)
  monotone non-decreasing in amp within tolerance 0.02, 3/3 seeds;
  |turn_flex(base)| < 0.05.
- C3 sign: R-side bias at amp d* x 4 flips turn sign vs L-side, 3/3 seeds.
- C4 specificity (descriptive, 2 draws): random DN-pair bias at max amp
  gives |turn| < half of DNg95-L at the same amp.

Sobol one-deciding-param: DNg95 tonic firing RATE is unmeasured — absolute
bias amp is underdetermined; gradedness / sign / survival are the honest
claims. No WHEN-claim (L15/L21). af op-point asserted every run (L30).
