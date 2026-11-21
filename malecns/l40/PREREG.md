# L40 PREREG — release-composition (written before any run)

Question (LANE.md ideas-18, L40): does a RELEASE drive (negative tonic on
ceiling-pinned DNg88, the L38 STOP channel) compose with a positive HOP
(DNge046_L free side, L38/L39 viable channel) — stop-and-go as ONE gesture
vocabulary — or does the release rupture what the hop needs?

Substrate: L32 arm-A frozen (g .01, beta 2, D=0 — L35 proved drive inert;
NO mech entrainment here, keeping the release measurement pure — the L39
entrain+hop+release join is a LATER card if this composes). Identical
21,516 nodes / 2,977,920 edges assert. Paired control+arms, ONE generator,
ONE shared per-step noise (L36); drives enter AFTER settle (L36); per-arm
drive table, no inline conditionals (L39 v1 bug); af op-point assert every
arm every phase; dm probes on the DRIVE CELLS per sub-window (L35/L36/L38).

Window: 400 settle, then 10,400 steps: PRE 0-2500 (measure 500:2500),
ON 2500-5500 split 2a 2500:4000 / 2b 4000:5500 (measure 2750:4000,
4250:5500), POST 5500:10400 (measure 6000:10400). Seeds 11/22/33.

Arms: free (bit-identity gate), hop (046L +0.2 tonic, ON), rel (88 −8
tonic, ON), joint (both ON), stagg_rh (rel 2a then hop 2b = stop-then-go),
stagg_hr (hop 2a then rel 2b = go-then-stop), hop_2b (hop only in 2b —
isolates the release AFTEREFFECT on a later hop).

Readouts (per phase/sub-phase window, burn-ins above): S(Tr) pooled fL+fR
vs eL+eR (L32/L39 form) + per-side SL/SR; rhythm (ratio, f) on Ti-flexor
pool mean (L38 form) AND motor-mean (L39 form); dm@046L, dm@88 per
sub-window; af per phase; X[046L].mean, X[88].mean (pin state).

PRE-REGISTERED claim levels:
- C0 substrate: ctl f_Ti(PRE) within .05 of L38 spot controls {0.80, 2.04,
  1.91}; ctl S(PRE) >= .40 each seed; free arm dm == 0.0 EXACTLY (all steps).
- C1 drives land: hop arms dm@046L > .01 in every sub-window where the hop
  fires; rel arms dm@88 > .01 likewise (per seed).
- C2 release-stops (L38 anchor reproduced in-phase): rel ON-window S < .15
  in >=2/3 seeds while ctl >= .40.
- C3 stop-then-go (the constructive question): stagg_rh 2b — hop freq shift
  |f_arm − f_ctl| >= .3 Hz in >=2/3 seeds (hop still lands after a stop) AND
  POST S(stagg_rh) >= .25 in >=2/3 seeds (vocabulary survives sequencing).
  PASS = stop-and-go composes; FAIL + POST S dead = release is a RUPTURE
  (one-way stop), equally informative.
- C4 simultaneity: joint ON-window S < .15 (release dominates structure)
  vs S >= .25 (hop protects) — layered read either way; plus POST S(joint)
  reported against the stop-then-go POST.
- C5 no lasting damage: every arm POST rhythm ratio >= 10 (rhythm exists
  after all drives off) — if any arm stays dead in POST, that arm's stop is
  irreversible at this timescale (label it, do not bury it).

Estimand label: P1 (per-class tonic drives re-applied on real wiring;
composition/additivity question, not a wins-claim — tick-37 rule). No
WHEN-claims beyond L21 delay bounds. Descriptive lab demo; owner movement
law respected; no live changes.

## ADDENDUM (post-run analysis fixes, disclosed — rollouts deterministic,
## unchanged bit-for-bit; gates amended to the pre-registered TEXT, not to
## desired outcomes; v1 numbers preserved in run history)

- C0 v1 compared MY 20 s PRE window (5-25 s post-settle) to L38's 45 s
  window (15-60 s) — a window artifact: the free cord MIGRATES across
  attractor frequencies, so epoch-mismatched freq anchors disagree by up to
  1.15 Hz with nothing wrong. Amended: anchor on the SAME epoch (1500:6000),
  where the shared-noise control reproduces L38 EXACTLY (0.800/2.044/1.911).
  The substrate-identity claim was always additionally carried by the
  21,516/2,977,920 asserts + free-arm bit-identity (dm 0.0, 3/3 seeds).
- C1 v1 selected checked sub-windows with generic predicates (not the
  drive's own schedule), producing false "failures" on windows where the
  drive was OFF. Amended: windows chosen by each drive's schedule; OFF
  windows now registered as the negative control (dm must be EXACTLY 0.0 —
  it is, 3/3 seeds, every arm; no arm leakage, the L39 v1 lesson holds).
- C2 v1 gated on BOTH sub-windows < .15 — stricter than the PREREG's own
  text ("ON-window S"). Amended to the text: continuous ON window; the
  2a/2b split is retained and reported as the kill's ONSET KINETICS
  (2a partial .15/.15/.23 -> 2b dead .13/.04/.04; the ~15 s kill time is
  itself a finding).
- C1 addendum 2: the off-window negative control is only valid for windows
  that PRECEDE the arm's first drive. In staggered arms, off-windows after
  the first drive measure CARRYOVER divergence (the earlier drive's lasting
  effect — the composition signal itself), never leakage; v1 gated them and
  "failed" s_rh/s_hr on it. Amended: gate pre-first-drive windows only
  (dm exactly 0.0 required); carryover windows reported ungated.
