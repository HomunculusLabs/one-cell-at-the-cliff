# L34 PREREG — rhythm-entrainment (written before any scan)

Question: does the L32 self-pacing cord rhythm LOCK to periodic mechanosensory
drive (entrainment), or is it autonomous and drive-refractory? Decides whether
body-level feedback (L26 bridge form) can phase-stabilize gait.

Substrate: L32/L33 verbatim — cord subnetwork (assert 21,516 nodes /
2,977,920 edges), arm-A signs, beta 2, G .01, DT .01, TAU .05, sustained
bilateral DNg100 drive D=.05, seeds {11,22,33}, SETTLE 400, WIN 60 s.
Perturbation: bilateral sinusoidal current on ALL vnc_sensory mechano cells
(L29 channel), I = A*(0.5+0.5*sin(2*pi*f_d*t)) — substrate-vibration form,
symmetric (tests phase-locking, not steering).
Grid: f_d in {0.7, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0} Hz x
A in {0.01, 0.03, 0.1, 0.3} x 3 seeds, + 3 free-run seeds. af op-point
assert (0.01<af<0.9) and NaN assert in EVERY run (L30/L33 rule).

Readouts (window: last 45 s, first 15 s of drive skipped):
  f_free  = per-seed dominant freq of all-motor mean, 0.5-10 Hz band.
  f_mot   = same, per driven run (parabolic sub-bin peak).
  P@f_d   = DFT power exactly at f_d (integer cycles); SNR gate =
            P@f_d(run) / P@f_freeband(free-run same seed at f_d) >= 5
            BEFORE any phase readout (L19 rule: no gate on undriven pool).
  R       = phase concentration of motor mean rel drive at f_d
            (heterodyne exp(-i2pi f_d t), moving-average over exactly one
            drive period, circular resultant over window). Sham control:
            same R computed on the FREE-RUN trace (no drive) at same f_d.
  S_pooled(Tr), rhythm ratio, free-peak height vs free-run (regime health).

Claim levels (verdict = highest C passed, pre-registered):
  C0 SUBSTRATE: free-run reproduces L32/L33 — S(Tr) >= +.40 all seeds,
     rhythm ratio >= 100x, f_free per-seed {0.800, 1.444, 1.422} Hz
     (+-0.03). [AMENDED pre-grid after probe l34/probe.out: l33's json
     rhythm read the FULL 60 s (transient included) -> "1.33-1.43"; its
     saved last-45-s traces FFT to the anchors above and my rerun is
     BIT-IDENTICAL (max|diff| 0.0) — the substrate is unchanged, the
     window was. Anchors are on the pre-registered measurement window.]
  C1 SURVIVAL: gentlest amp (A=.01): rhythm still present every seed
     (ratio >= 10x, dominant peak in-band). (Report at all amps.)
  C2 FREQUENCY LOCK (the claim): some (f_d, A) with |f_free - f_d| >= .15 Hz
     where |f_mot - f_d| <= .03 Hz in >= 2/3 seeds AND SNR gate passed.
     PASS = entrainment; FAIL = autonomous (or uncoupled — distinguish by
     whether P@f_d ever passes the gate: gate-pass + free peak intact =
     FORCED SUPERPOSITION (L28 class), gate-fail = drive cannot couple at
     this gain regime).
  C3 PHASE LOCK: in every C2 cell, R >= .5 in >= 2/3 seeds while sham R
     at same f_d < .3 (concentration is drive-caused).
  C4 TONGUE: locking set at A=.3 strictly wider than at A=.01 (Arnold
     tongue grows with amp), or documented flat/absent.

P1-labeled descriptive; no WHEN-claims; no live changes; CPU-only.
