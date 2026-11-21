# L154 PREREG — Sapkal deprivation arm (card: ideas 81, tick 175 seed)

Field source: Sapkal et al. bioRxiv 2026.04.29.721658v2 (digested LANE-RESEARCH
tick 175). Two-stage card: (a) STATIC join, zero rollouts; (b) DYNAMIC arms
ONLY IF (a) joins. This tick = (a) + registration of (b).

## Vocabulary (exact strings, both spellings carried)

Sapkal motif per digest: IN17A001, IN3A006, INXX464, INXX466 (expanded),
IN19A007, + added IN12B003, IN9A002. Pugliese family (tick-61 pins): IN17A001,
INXXX466 (THREE X — the card's two-X INXX466 is a different string, both
carried), IN16B036, IN19A007, IN19B012. 19B/19A hemi-lineage census by
prefix.

## Already-observed format facts (probe 2026-11-19 12:4x, pre-registered as
## pins, not hypotheses)

- MALE (body-annotations feather, `type` exact): IN12B003=6, IN17A001=6,
  INXXX466=6, IN19A007=6, IN16B036=6, IN19B012=6; IN9A002=0, IN3A006=0,
  INXX464=0, INXX466(2X)=0. (IN12B003 = the Sapkal-ADDED name joins male,
  6 cells = one per leg neuropil, same shape as the Pugliese family.)
- MALE flexor vocabulary (`type`): 'Ti flexor MN' 37 + 'Acc. ti flexor MN' 47;
  'Tr flexor MN' 35 + 'Acc. tr flexor MN' 22; extensor 'Ti extensor MN' 12 /
  'Tr extensor MN' 11. Male weights UNSIGNED (sign rides NT feather).
- MALE IN19B* prefix census: 309 cells. IN19A* many types (top IN19A117 21).

## H-STATIC (falsifiable, this tick)

- H1 JOIN-BANC: >=4 of the 10 carried names join BANC with >=1 cell via
  reviewed-matches (valid=='t') OR manc_121_match_id; IN12B003 counted
  explicitly (l62 pinned the Pugliese 5 at 24/30 in-graph; new pin needed).
- H2 SIGN-ANCHOR: IN19A007 predicted NT is inhibitory-class {gaba, glutamate}
  (CONVENTION DISCLOSED: glutamate-as-inhibitory is the L65 winning-arm
  convention, not a BANC fact) on male consensus/predicted NT AND on BANC
  NT predictions where joined; AND male IN19A007 out-edges onto the flexor
  pools (Ti/Tr flexor MN + Acc. variants) number >0.
- H3 SAPKAL-FLEXOR (one-sided): male IN12B003 out-mass onto flexor pools >
  onto extensor pools (Sapkal: strong tibia-FLEXOR influence). Reversed or
  equal = disclosed, not failed-run.
- H4 CENSUS (descriptive pins, no gate): 19B and 19A prefix counts on male +
  BANC; per-name join table both graphs, full precision.

GO/NO-GO for (b): H1 AND H2 both pass. Any H3 outcome disclosed either way.

## (b) DYNAMIC ARMS — registered now, run only on GO (next tick)

Substrate: l65 BANC cord subnet exactly as the l150 lineage's `b65` arm
(same graph slice, same G65 gain, DNg100 command `D` ON in BOTH arms).
Deafferentation analog: the mech sensory sinusoid (0.7 Hz, ENT_AMP, applied
to mech[a] every step incl. settle) REMOVED for the ENTIRE run in the off
arm — the command stays, the sensory drive goes (Sapkal FeCO-silencing
analog at rate fidelity).

- Arms: `on` (l150 b65 form verbatim) vs `off` (identical except the
  `drive[mech,0] += sin_t` line never executes). One generator pair per
  seed shared by both arms (same X0, same noise draw count/order); the off
  arm diverges from step 1 of settle BY DESIGN (drive differs) — prefix
  bit-identity NOT an anchor here.
- Seeds: 16 fresh (B34) + 3 anchor seeds (11/22/33).
- ANCHOR (C0A chain, L120 form): `on` arm must reproduce l150's STORED
  b65 traces at anchor seeds BIT-IDENTICALLY (max|d| == 0 on saved mm/pool
  channels). L85 certification: this certifies the reimplementation before
  any off-arm read.
- Reads (window discipline L34: metric window == anchor window, both = the
  full WIN window, stated in code):
  1. dom_freq of motor-mm trace (FFT, dominant bin, untruncated spectrum
     read + band argmax-at-floor check per L108).
  2. duty per side (duty07 form) on Ti/Tr antagonist pools.
  3. per-side S (flexor-vs-extensor anticorr) for Ti and Tr, both sides.
  4. npz SAVES all four antagonist pools + mm per arm/seed (checkpoint
     lesson: save every channel the metrics read).
- SAPKAL-SIGNED PREDICTION (discriminating read): paired per-seed sign of
  dom_freq(off) − dom_freq(on); wet-lab direction = OFF SPEEDS (more
  positive deltas than negative, binomial 16). Secondary: duty moves
  toward 0.5 under off; S survives (|S| off not collapsed to noise floor).
  OPPOSITE direction = model-class divergence, reported as a finding, never
  bent (honesty clause).
- No gate on duty/S magnitudes (L88 batch-swing disclosure applies); the
  dom_freq paired sign is the claim-carrier.

## RESULTS ADDENDUM (2026-11-19 12:5x, run l154_static.py, static.json)

- H1 JOIN-BANC **PASS**: 6/10 names join BANC via reviewed-matches
  (IN12B003=6, INXXX466=5, IN17A001=4, IN19A007=5, IN16B036=6, IN19B012=4;
  Pugliese-5 sum = 24 == l62 pin exactly). manc_121_match_id column: 0 for
  all (dead join path for this vocabulary). IN9A002 / IN3A006 / INXX464 /
  INXX466(2X) join NEITHER graph — paper-local aliases; the card's two-X
  INXX466 is a spelling of INXXX466 (three-X, the real release name).
- H2 SIGN-ANCHOR **PASS**: IN19A007 NT gaba on male (consensus+predicted+
  celltype, 6/6) AND BANC (5/5) — no glutamate-convention dependence; male
  flexor projection 61 edges / 2001 mass vs extensor 13 / 328 (6.1x).
- H3 SAPKAL-FLEXOR **PASS (with disclosure)**: IN12B003 male flexor 20e/173
  vs extensor 8e/85 (2.0x mass); BANC flex 18e/120 vs ext 5e/59 (direction
  holds). Disclosure: IN12B003's DIRECT flexor mass is modest vs its total
  out-mass (173/22747 = 0.8%) and vs IN19A007 (2001) / IN19B012 (5121);
  Sapkal's "strong flexor influence" is a functional claim — likely
  mediated, not direct-mass.
- H4 CENSUS pinned: male IN19A* 545 cells/116 types, IN19B* 309/72; BANC rm
  IN19A* 282/90, IN19B* 224/62. Motif NT table (male, 6/6 each): IN17A001
  ACh, INXXX466 ACh, IN19B012 ACh, IN16B036 glut, IN19A007 gaba, IN12B003
  gaba — Pugliese E1/E2/E3/I1/I2 labels match predicted NTs exactly, and
  the Sapkal-added IN12B003 is inhibitory as published. IN19B012 (E3, ACh)
  is the family's strongest DIRECT flexor driver (male 5121/85e, BANC
  4733/59e) — excitatory-onto-flexors, the under-called flexor-power line.
- GO/NO-GO: **GO** for (b) dynamic arms (next tick), per registered form.

## ADDENDUM 2 (2026-11-19 13:5x, pre-run — anchor seeds corrected from
## STORED artifacts, L44 rule instance #10)

The registered "3 anchor seeds (11/22/33)" for the C0A chain is a MIS-CARRY:
in l150_run.py, [11, 22, 33] are the P1-BISECT anchor seeds (settle-only af
bracket), NOT rollout seeds. l150's STORED b65 rollout traces (raw_l150.npz,
key scan this tick) exist at seeds {801, 901} (its excluded-from-sample
rollout anchors) + B33 3365-3380. AMENDED before any run:

- C0A-154 anchors: seeds 801/901 vs raw_l150.npz b65 channels (22 keys: mm,
  xm, 20 pools + af), max|d| == 0.0 required, STOP on fail. Count 2 (not 3)
  — anchors are wiring certs, excluded from the sample either way.
- Fresh batch B34 = 3401-3416 (16 seeds; absence-verified across every npz
  on disk this tick, zero collisions — in-run re-assert over the lineage
  list + raw_l150 included).
- on-arm gain: stored constant G65=0.14 for BOTH arms (graph identical by
  construction — off shares b65's CSR object; no fresh bisect, l144 A1
  graph-identity form; af reported per arm, identity NOT asserted because
  drive differs by design).
- Metric provenance: S_of / dom_freq / duty07 machinery copied from
  l94_verdict.py; CERTIFIED before any L154 read by recomputing duty_07 for
  l94 arm 'cfn' at its stored anchor seeds 11/22/33 and asserting equal to
  results_l94.json table_Ti.cfn.anchor {11: .073, 22: .517, 33: .2} (L85
  rule; rounding path single-seed round(,3)).
- Secondary 'duty moves toward 0.5' operationalized honestly: duty07 is an
  antiphase-window fraction, NOT a step-cycle duty — the reported read is
  the L/R duty07 ASYMMETRY |duty07_L − duty07_R| (paired off vs on) +
  per-side duty07 deltas, disclosed as the nearest analog at this readout.
- dom_freq discipline: claim-carrier = house band form (0.3-10 Hz, parabola
  refines), full-WIN window both arms (L34: metric window == anchor
  window); untruncated-spectrum read + band-argmax-at-floor flag reported
  as diagnostics (L108).

## RESULTS ADDENDUM (b) (2026-11-19 14:0x, run l154_run.py + l154_verdict.py)

- WIRING CERTS ALL GREEN: C0A-154 b65(on) vs l150 STORED at 801/901 max|d|
  0.0e+00 (22 keys + af — off arm consumed zero extra draws as designed);
  B34 absence 34 npzs; metric machinery CERT vs l94 stored cfn duty_07
  {11:.073, 22:.517, 33:.2} EXACT + dom_freq analytic self-test 0.7/1.4 Hz.
- dm probe (L35): min max|mm off-on| = .0260 over 18 seeds — channel ALIVE.
- **CLAIM NOT MET**: paired dom_freq(off)-dom_freq(on), registered band form,
  full WIN: +6 / -10 / 0 zeros, two-sided p = .4545. Wet-lab direction
  (deafferentation SPEEDS the CPG, Sapkal) does NOT transfer to this rate
  model — reported as model-class divergence per the honesty clause.
- Diagnostics that EXPLAIN it: (i) global spectral peak sits BELOW the
  0.3-10 band in 16/16 on seeds and 11/16 off (untrunc mean .100 -> .203
  Hz) — the motor rhythm the band metric tracks rides a slow oscillation
  (L108 class); (ii) anchors 801/901 on .700/.316 vs off .449/1.089 —
  removal re-DRAWS the attractor per seed (L41/L56 lottery class), no
  parametric throttle. Consistent with lineage law: the sensory sinusoid
  was the ENTRAINER (L34 frequency-pulling); remove it and the cord reverts
  to its intrinsic attractor draw, direction seed-dependent.
- Secondary: duty07 L/R asym Ti .013 -> .047 (paired +.034 — symmetrization
  analog NOT met either, small); S07 antiphase SURVIVES off (Ti L .606 /
  R .715; Tr R .762, Tr L weak-positive .043 vs on -.083) — structure does
  not need the sensory drive, matching Sapkal's CPG-central claim on the
  structure axis while diverging on the frequency axis.
- Post-hoc (labeled): untrunc paired sign in results json.
