# L171 PREREG — slow-line re-attribution + robustness panel

Registered 2026-11-20 ~15:0x EST, BEFORE any new number is computed.
Card: LANE.md L171 (ideas 87, external-review response #4).
Zero rollouts: every arm re-scores STORED traces (banc/l135/raw_l135.npz,
18 seeds 801/901/3001-3016, arms cutng25 = carrier-cut and cutng25p =
mass-twin-cut). No W is built, no bisect is run, no RNG is drawn.

## Evidence rule (inherited from L167, binding)

The reviewer's own re-scoring ("the carrier-vs-twin contrast gets
CLEANER under the fast-segment / high-pass reads") is a CLAIM, not
evidence. Nothing from the review report enters the draft. Every value
below is re-derived inside `l171_rescore.py` from our stored artifacts,
and the published cells are reproduced EXACTLY first (CERT block).

## Instruments

**A. Envelope attribution (static, no traces).** Rebuild the drive
envelope AMPA exactly as `banc/l135_run.py` builds it (SEGB three
segments, 500-on/400-off chop inside each 2000-step segment,
`AMPA[2000:4000]` continuous override), assert it byte-equal to the
l135 construction, and take its own real FFT over the full WIN = 6000
samples (bin spacing 1/60 Hz at DT 0.01). The question: does the
measured .100 Hz line (= bin 6) coincide with a line of the STIMULUS
ENVELOPE's spectrum?

**B. Fast-segment re-score.** The published duty excludes the 1.4-Hz
segment by construction (`q07` masks to the 0.7-Hz segments). Re-score
the identical S/duty pipeline with the measurement window set to
TS in [2000 + MEAS0, 4000) — the UNCHOPPED segment — and report
kR/kL/meanR/meanL + Wilson for cutng25 and cutng25p.

**C. High-pass re-score.** Brick-wall high-pass each of the four pool
traces (full 6000-sample trace, rFFT, zero every bin with
f < 0.3 Hz INCLUDING DC, irFFT), then run the identical S/duty
pipeline in the PUBLISHED q07 window. Reported alongside A/B as a
robustness panel, never as a replacement readout.

## Branches (precedence explicit, after the L169c2 R2/R3 ambiguity)

Attribution axis, evaluated in order:

- **A1_envelope_line** — bin 6 (.100 Hz) is a local maximum of the
  envelope spectrum AND within the envelope's top-5 non-DC lines.
  Verdict: the .100 Hz line is stimulus-envelope-attributable; the
  Methods gains the 9-s cycle statement and the abstract/§1 headline
  loses the endogenous-clock reading.
- **A2_envelope_near** — bin 6 is NOT a local max / not top-5, but the
  chop fundamental (1/9 s = .1111 Hz, bin 6.67) IS the envelope's
  dominant non-DC line and bin 6 lies within one bin of it. Verdict:
  PARTIAL re-attribution — the envelope sets the sub-band SCALE and the
  measured bin is the nearest resolvable one; the Methods states the
  9-s cycle AND the 0.67-bin offset explicitly, and no claim is made
  that the two are the same frequency.
- **A3_no_envelope_line** — neither holds. Verdict: re-attribution
  REFUTED; the slow line stays in the draft as measured, and the card's
  Methods sentence is NOT written.

Independent of A1-A3, the **mech-OFF counter-evidence is registered as
a mandatory disclosure**: our own [l154.band] carries 11/16 mech-off
seeds sub-band, i.e. sub-band peaks exist with the drive off. Whatever
A-branch fires, the draft must say that the ENVELOPE can explain the
LINE'S POSITION and (per L162) its PHASE LOCK, but cannot explain the
existence of sub-band power with no drive.

Robustness axis:

- **B1_cleaner** — in BOTH re-scores the carrier-vs-twin ordering is
  preserved and the paired contrast (meanR difference) is >= the
  published q07 contrast. Verdict: robustness panel strengthens the
  main result; fold as such.
- **B2_preserved** — ordering preserved in both, contrast smaller in at
  least one. Verdict: robust-but-not-cleaner; fold with the smaller
  numbers quoted.
- **B3_regime_dependent** — ordering preserved in one re-score and
  LOST (or reversed) in the other. Verdict: report the re-score that
  fails as a scope limit of the readout, name which window carries it.
- **B4_degenerate** — in a re-score BOTH arms sit at floor (both
  meanR <= .05 and both kR = 0) or both at ceiling. That re-score
  CANNOT adjudicate (L55 degenerate-pass class) and is reported as
  vacuous. Explicitly expected to be LIVE for the fast-segment arm:
  L50/L79 measured continuous fast-segment drive as structure-TOXIC
  (duty .022 driven vs .538 undriven) on the male cord, so a floor
  read in B is a prediction of the prior law, not a failure of this
  instrument.

Precedence: B4 is checked FIRST per re-score and removes that re-score
from the B1/B2/B3 decision; if BOTH re-scores are degenerate the panel
is reported as not-adjudicable and the abstract surgery proceeds on the
A-axis alone.

## Pins (asserted in-run before any verdict is read)

- P1 CERT: our re-implementation of the published pipeline reproduces
  `l135/results_l135.json:table.Ti.cutng25` = kR 15, meanR .754,
  kL 0, meanL .123 and `table.Ti.cutng25p` = kR 5, meanR .399, kL 2,
  meanL .301 EXACTLY (rounded-per-seed path, n = 18).
- P2 CERT: Wilson on the stored k reproduces the stored lbR/ubR for
  both arms to < 1e-9.
- P3 envelope: AMPA has exactly 4 off-gaps, total on-steps asserted,
  and the rebuild is elementwise identical to l135's own loop output.
- P4 high-pass: the filter is checked on synthetic input (a .05 Hz
  sine is attenuated > 100x; a 1.4 Hz sine is preserved to < 1e-6
  relative error) BEFORE it touches any pool trace.
- P5 windows: the fast-segment mask contains exactly 150 TS points and
  shares ZERO points with q07.
- P6 seeds: the 18 seeds are read from the npz keys, never typed
  (L157 batch-vocabulary rule).

## Draft folds permitted by this card

Abstract + §1 headline (4) re-written on the A-branch verdict; a new
Methods sentence on the 9-s cycle; a new robustness paragraph in §3/§4
carrying the panel; numbers.json + l149_verify section 18 + CLAIM-MAP
B27. The l158 abstract vocabulary freeze is deliberately RE-CUT (L168
precedent) because the abstract changes by design. No rollouts, no live
changes.
