# EXPERIMENT brief — L199: the tone-phase registered test (fable, anthropic-pinned)

Owner-directed (2026-11-21 ~20:2x, budget-window wave). L197b's post hoc
hypothesis, now registered properly: the carrier-deletion phenotype is a
change in the pools' PHASE RELATION to the external 0.7-Hz tone.

## Design (PREREG before any computation)

- Data: stored L197b raws (banc/l197b/, n=96/arm, both designs S and W)
  + L186 raws. ZERO new rollouts required for the primary test.
- Instrument (fix tick-216's error): the pair-segment phase statistic —
  per pair-segment, the rotation between the two seeds' gate lags induces
  a tone-phase offset; compute the duty/anticorrelation CONDITIONED on
  that offset (in-phase / mid / antiphase bins), NOT averaged across
  independent lags. Register bin edges and the statistic exactly.
- Registered branches: **PH1** deletion changes the sign/shape of the
  phase-conditioned profile (base: co-move at half-rotation; removed:
  alternate at zero — per the post hoc) vs **PH0** no profile difference
  beyond pooled elevation. Register the contrast bands.
- Secondary (small rollouts allowed, ≤4 arms × 16 seeds): a direct
  tone-phase manipulation — shift the tone phase of the drive by half a
  period for one arm; does the phenotype follow the shift? (The causal
  version of the correlational test.)
- Also: draft-fold note for the lane — L186's "unresolved" line can now
  read "no internal rhythm; timing locks to the external tone phase"
  (cite l197b items 3-4); leave the DRAFT edit to a gated fold card, do
  NOT edit DRAFT.md here.

## Rules

PREREG first; C0A anchors for any rollout; CPU ≤6; writes to
banc/l199/** + one LAB-INTENT append. Wall ≤2 h. Final answer ≤250 words.
