
## L202 — ru2-necessity registered replicate + bilateral twin + chain batches (2026-11-22, experiment dispatch)

INTENT: confirm L200's post hoc item 6 (removing ru2 = gi 70994 abolishes the
carrier-removal right-side regime) as a registered card with the fixed-gain
comparator L200 owed; roll the bilateral twin L200's two-twin bound missed
(rank 4, gi 67125; rank 5, gi 67756 added); ask whether the carrier phenotype
needs ru2's activity or its presence (ru2 replay-clamped at its base
trajectory on the carrier-removed graph vs ru2 cut); give the mechanism chain
fresh batches (rcut / rcutF, L190's edge / sham). 16 arms x 16 fresh seeds
(B45 3737-3752), 4 workers x 1 thread. PREREG sha 626be3aa86b63f75 frozen
15:40:16 before the harness was written; FREEZE 15:45:50 before rollouts; no
post-freeze code change (12 frozen files re-hash equal).

RESULT (C0A 1301 checks vs raw_l135 / L175 / L187 / L190 / L198 / L200 all max
0.0, incl. my re-built L190 edge arms and L200's own sc25 / l2c / l2cF / l2;
seven stored gains EXACT; CERT-X 1518; CERT-REPLAY 66; CERT-NULL 48; metric
reproduces five L200 rows; independent duty re-derivation 816 values 0.0):
- **W = W1_wipe_replicates, both gain forms.** l2c - sc25 -.459 [-.553,-.365],
  16/16 lower, 1.4-Hz .562 -> .000; fixed l2cF - sc25F -.360 [-.473,-.248],
  15/16, .366 -> .000. Pooled B44+B45 -.473 [-.539,-.407], 32/32 lower; the
  1.4-Hz duty is exactly 0 in all 64 double-removal rollouts.
- **T = T1_bilateral_specific.** lt4 left 1/16 .200 (fixed 0/16 .190), lt5 0/16
  .205, ru2 16/16 .870 same seeds. 0 of 4 matched cells flip (2 bilateral).
- **N = N3_partial, gain-form DEPENDENT (neither pole).** ru2 held on its base
  trajectory: chopped rise mostly lost (s2k - sc25 -.309 [-.383,-.235];
  retained .33 / .25 fixed) but above the cut (+.150 [+.064,+.236]); 1.4-Hz
  signature survives (.212 re-matched, .402 fixed; cut .000). The signature
  needs ru2 present and emitting; the chopped rise needs ru2 free. Post hoc:
  free vs replayed ru2 trajectory r ~ .32, mean shift +.025 / -.018 —
  timing, not mean, is the candidate.
- **S = S_partial.** Carrier + twin 67125: right 12/16 .588 (.012 under the
  SUPER mean bar), +.237 [+.118,+.356] above the ru2 double removal, 1.4-Hz
  .860 (15/16) — the twin does not wipe; it strengthens the signature.
- **C.** Edge cut B3-partial again (14/16 .618, +.201 [+.105,+.297]; pooled
  26/32); sham B2 again. Relay removal INTERMEDIATE both forms this batch
  (three batches: rcut 35/48 +.216 [+.139,+.294]; rcutF 38/48 +.221) — the
  effect is stable, the SUPER label is not.
Predictions 12 of 16 sub-items; wrong: N modal, S modal, rcut, rcutF.
Owed: N second batch + constant-rate and other-seed replay controls; more
bilateral double removals; fixed-gain edge / sham. fig6's pending L202 slot
now has its input (the figure scripts fail loudly by design until rebuilt).
Artifacts banc/l202/{PREREG.md, PREREG.sha256, FREEZE.json, static.json,
nec_run.py, verdict_l202.py, results_l202.json, verdict.out, addendum.*,
L202-FINDINGS.md, raw_w0-3.npz, xm_w0-3.npz}. No DRAFT / LANE edits.
