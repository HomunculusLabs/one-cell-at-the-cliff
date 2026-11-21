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

---

## ADDENDUM 2 — STAGE (b1): the l169b2 arm-keyed CERT reader
Written tick 218 (2026-11-21 ~15:2x EST) BEFORE any stage-(b1) number was
computed. Zero rollouts; `l169b2/raw_l169b2.npz` read-only.

### Why (b1) exists at all
Stage (a)'s loop was `tbl = r["table"]; for pk in PAIRS: if pk not in tbl:
continue`. `l169b2/results_l169b2.json["table"]` is keyed by ARM
(f4wA/f4ng/f4tw/full/cutwA/cutng25), not by pair, so neither "Ti" nor "Tr"
matched and the whole l169b2 run was silently skipped: stage (a)'s 176 CERT
checks are exactly (13 l135 arms + 9 l169 arms) x 2 pairs x 4 fields.
The floor-4 twin pair therefore has NO composite read yet. This addendum adds
one, with its own CERT.

### B1 PAIR IDENTITY — derived from the STORED artifact, not from memory
(L44/L107 rule.) `l169b2/PREREG.md` line 54 reads, verbatim:
"`duty_07` per side on the Ti antagonist pair over the 0.7-Hz windows, the
l109/l111/l113 rounding path (round per seed, then mean) as implemented in
l169_verdict.py." The arm-keyed table is therefore the **Ti** pair, and only
Ti. No Tr values are stored for l169b2, so **Tr carries no CERT and is
excluded from every registered (b1) cell** (an uncertified pair would be an
L85 violation); Tr is not computed.

### B1-CERT (gate; runs FIRST, halts the stage on one mismatch)
Machinery: the stage-(a) functions are IMPORTED from `comp.py`, not
re-implemented (certified-code reuse; a second transcription is the L85 risk).
* B1-CERT-1, aggregate: all 6 table arms x {kL, kR, meanL, meanR} = 24 exact
  equalities against `results_l169b2.json["table"]`.
* B1-CERT-2, per-seed: `addendum_L_descriptive["rows"][arm]["perseedL"]`
  carries the 16 per-seed L-side duty values. Those are a STRONGER anchor than
  the aggregate, so all of them are checked: 5 arms x 16 = 80 exact equalities.
  Registered up front (L110 rule): that addendum block holds FIVE arms, not
  six (`full` has no row) — the comparison is a SUBSET compare over the stored
  keys, and the arm count 5 is asserted explicitly rather than assumed 6.
* Total registered: 104 exact checks. Seeds = B36 3449-3464; anchors 801/901
  excluded from every statistic (stage-(a) convention, unchanged).

### B1 CELLS (conventions C1-C10 inherited verbatim, nothing re-tuned)
* PRIMARY-b1 (identity axis, threshold-free): carrier **f4wA** vs floor-4 mass
  twin **f4tw**, paired within seed, per side, per band, over the full declared
  ladder (4 weight sets x 4 alphas). Registered reads per cell: sign of the
  paired mean, k_up/16, paired mean with jackknife CI, ci_excl_0, and whether
  the composite's sign AGREES with the stored duty delta on that same side.
* SECONDARY-b1 (rank axis): Spearman rho between the 6 arms' composite means
  and their stored duty means, per side, per band.
* XOR LEG (registered, descriptive): f4ng vs f4tw paired composite difference.
  The stored leg is `mean_paired_dR_ng_minus_tw` = -0.001 with an 8/8 seed
  split and `vacuous_xor_guard` false (branch G2_no_transfer). If the composite
  SEPARATES these two arms where our duty metric could not, that is an
  instrument finding and gets said in those words — it does not revive the XOR
  selection claim.
* DEGENERATE + BAND-FLOOR branches: identical definitions to stage (a),
  re-scored on this run.

### B1 PREDICTIONS (scored after)
* Qb1 B1-CERT passes 104/104 (the metric and window convention are inherited
  verbatim, so a failure means a convention drift, not a composite finding).
* Qb2 The floor-4 arms' registered axis was R-side duty and it came out DEAD
  (stored meanR .043-.082, branch G2_no_transfer), so the identity signal lives
  on the L side here: predict the L-side f4wA-vs-f4tw paired sign POSITIVE with
  CI excluding 0 (stored duty .698 vs .560), and the R side NOT separated.
  This is the opposite side from stage (a)'s readout — say so.
* Qb3 Amplitude balance A again carries the variance (degenerate branch does
  not fire) and the rank axis is weaker than the identity axis, as in (a).
* Qb4 g(P) collapses again (P > 2 in the large majority of windows), so the
  alpha=0 rung is the readable one; reported, not selected.

### READ-ONLY
No npz written; input mtime asserted unchanged. No draft edit (the paper is in
the owner-handoff state as of 15:0x — stage (b1) is lab evidence only).


---

## ADDENDUM 3 — STAGE (b2): the l65 FEMALE-CORD Ti/Tr reads (written BEFORE compute)

Stage (b2) of the card: "the l65 Ti/Tr reads (different segment/window
convention = separate CERT)". Zero rollouts, stored `banc/l65/raw_l65.npz`
read-only (mtime asserted unchanged), stored `banc/l65/results_l65.json` as the
CERT target. No draft edit (owner-handoff state).

### WHAT l65 IS, and why it needs its own reader
l65 (L65, 2026-11-14) is the female BANC cord subnet L32 replication: subnet
21,249 cells / 627,051 edges, pools from `peripheral_target_type`
(Ti flex 101 / ext 12, Tr flex 62 / ext 48), sustained DNg100 drive at the
frozen (g, beta, d) per arm, CONF_WIN 6000 steps at DT .01 = 60 s. Its
conventions differ from the l135/l169/l169b2 lineage in FOUR ways, each of
which breaks a stage-(a)/(b1) assumption:

* W1 NO SIDES. Pools are bilateral (`Ti_f`, `Ti_e`), so the L/R decomposition
  that carried stage (a)'s inversion and (b1)'s floored-axis rule does not
  exist here. The floored-axis question therefore has to be asked per ARM.
* W2 NO DRIVE SEGMENTS. One sustained drive for the whole record, so there is
  no 0.7-Hz measurement mask: l65's own window is `slice(int(.25*T), T)` =
  steps 1500-5999.
* W3 ONE WHOLE-WINDOW S, not a sliding trace: S = -corrcoef(flex, ext) over
  that single 4500-step window, and depth = max(ptp(flex), ptp(ext)) with
  l65's own readability bar depth >= 0.03.
* W4 THE ARM AXIS IS WIRING, NOT IDENTITY. There is no carrier/twin pair here.
  The arms are two NT-sign arms (A = glut-EXC, B = glut-INH) x 3 confirm seeds
  {11, 22, 33}, plus the rewiring LADDER: density draws 0-2 and degree
  (Maslov-Sneppen) draws 0-2, same 3 seeds, same frozen setting.

### DECLARED CONVENTIONS (pinned pre-compute; C1-C9 inherited verbatim)
* D1 COMPONENT CODE IS IMPORTED, NOT RE-TRANSCRIBED (the (b1) rule): `analytic`,
  `peak_count`, `comp_windows`, `composite`, `spearman`, `jack_ci`, `W_AMP`,
  `WEIGHT_SETS`, `ALPHAS`, `BANDS`, `PRIM_*`, `PROM` all come from
  `banc/l176/comp.py`. `comp_windows` reads the module-global window list
  `TSQ`, so the l65 window convention is installed by REBINDING `comp.TSQ`
  before the call -- the component arithmetic is byte-identical to the
  certified stage-(a) code.
* D2 WINDOW CONVENTION, PRIMARY (the l65-native analogue of C10): trailing
  500-step windows, stride 10, entirely inside l65's own measurement slice =
  `TS_b2 = arange(1999, 6000, 10)` (401 windows; earliest end-point
  1500 + 499). Composite per arm/seed = mean over those windows.
* D3 WINDOW CONVENTION, ADDENDUM read (reported, never selected): ONE
  whole-measurement-window composite over steps 1500-5999, which matches the
  extent of the stored S exactly. Reported beside D2 so a window artefact
  cannot hide inside the primary.
* D4 Bands, weights, alphas, prominence floor: inherited (pub 1-10 Hz and
  sub 0.3-10 Hz; primary weights equal-residual; alpha ladder {0, .5, 1, 2};
  PROM .25). The (a)/(b1) gate finding means alpha=0 is expected to be the only
  readable rung again; it is REPORTED, not selected.

### B2-CERT (runs FIRST, halts on mismatch; L85 rule)
Reproduce from the stored traces alone, with l65's own window and metric code
(copied verbatim from `l65_banc_oppoint.py` lines 234-241):
96 per-seed values = 8 arms (A, B, density0-2, degree0-2) x 3 seeds x 2 pairs
x {S, depth}, PLUS the aggregate `ladder_real_S` (0.7195787507714315 = the mean
over confirm seeds of arm B's S(Ti)). Stored values are FULL precision, so the
bar is |diff| <= 1e-12 with the max error reported. Any failure halts before a
single composite number is read.

### FLOOR REPORT FIRST (the (b1) rule, now mandatory)
(b1) proved the composite is UNSAFE on a floored axis: amplitude balance has no
silence floor, so a dead pool pair can return a confident wrong-sign
separation. So before any wiring verdict, report per arm/pair: stored depth,
pool mean rates, and the `floor` fraction from `comp_windows`, and classify each
arm/pair as OFF-FLOOR (depth >= l65's own 0.03 bar) or FLOORED. Every composite
comparison that involves a FLOORED cell is reported as UNINTERPRETABLE-BY-RULE,
not as a finding. The stored depths already say which way this will go (real
arms .079-.288, ladder draws .006-.025), and that is the point of the cell.

### REGISTERED CELLS
* PRIMARY (wiring axis): does L65's claim -- real female wiring self-orders
  antagonist antiphase, degree-MS draws do not (stored S(Ti) .7196 real vs max
  .019 across degree draws) -- survive the composite? Per pair, compare arm B
  against each ladder draw at the shared seeds {11, 22, 33}, paired within
  seed. n = 3, so the claim-carrier is SIGN CONSISTENCY (3/3) plus the per-seed
  values; jackknife CIs on n=3 are reported as a courtesy and explicitly NOT
  the gate. PASS = real > every degree draw on 3/3 seeds for the pair whose
  stored verdict the draft cites (Ti), AND the floor report says arm B/Ti is
  off-floor.
* SECONDARY (rank axis): Spearman of per-arm composite against per-arm stored
  mean S across all 8 arms, per pair, per band. The stored ordering is
  B > A >> ladder. Reported with the floored-cell caveat attached.
* TERTIARY (NT-sign arm axis): does the composite preserve B > A -- the
  cross-connectome sign flip that is one of L65's two published findings --
  per pair, paired within seed (n=3, sign consistency again)?
* DEGENERATE branch: A_range < 0.05 across the 8 arms => the composite is a
  monotone transform of our own metric and the cell is VACUOUS (L55 class).
* BAND-FLOOR branch: the C3 diagnostic, re-scored here. Note l65's rhythm sits
  at 0.56-1.15 Hz, so the published 1-10 Hz band truncates part of the
  fundamental on some arms -- the same L108 question, third instance.

### B2 PREDICTIONS (scored after)
* Qb2-1 B2-CERT passes 97/97 (96 per-seed + the aggregate). A failure here is
  a convention drift in MY reader, never an l65 finding.
* Qb2-2 THE PRIMARY GAP SHRINKS BUT SURVIVES IN SIGN on Ti: the ladder draws
  are FLOORED (stored depth .006-.025 < .03), so their amplitude-balance term
  is unconstrained by silence and will not sit near zero the way their S does.
  Predict real > null 3/3 on Ti with a composite gap much SMALLER in relative
  terms than the stored S gap (.72 vs <= .019), and predict at least one
  individual ladder draw reads NON-trivially high on the composite -- which is
  a warning about the instrument, not about l65's wiring claim.
* Qb2-3 The NT-sign arm ordering B > A survives (both arms are off-floor, so
  this is the comparison the composite is actually licensed to make).
* Qb2-4 g(P) annihilates a third time (P > 2 in the large majority of windows)
  and the band-floor fraction stays 0.0000 a third time.

### READ-ONLY
No npz written; input mtimes asserted unchanged; no live service touched; no
draft edit. Artifacts: `banc/l176/{comp_b2.py, results_l176b2.json, run_b2.out}`.

================================================================================
# ADDENDUM 4 — stage (b3), the MALE replication (written tick 220, 2026-11-21
# ~17:4x EST, BEFORE any stage-(b3) composite number was computed)
================================================================================

## b3.0 FEASIBILITY FINDING — the card's named substrate HAS NO TRACES (L125 class)

The card says "(b3) the male L32 replication". Checked FIRST, before building any
machinery: `malecns/l32/` contains PREREG.md, scan_l32.json, results_l32.json,
run.out and NOTHING ELSE — no npz, no stored pool traces. L32 stored only its
SCALAR metrics (per-arm/per-seed S(Ti), S(Tr), depth, rhythm, af). The Guba
composite needs per-pool TIME SERIES (flexor and extensor envelopes), so the
card's literal substrate is INFEASIBLE for a zero-rollout stage. This is the
L125 rule applied to our own card: feasibility-check the numeric/data constraint
against stored artifacts BEFORE building the machinery.

Registered amendment, with a DETERMINISTIC closest-achievable substrate (L125's
"dead spec becomes the run's strongest arm" form):

  SUBSTITUTE SUBSTRATE = `malecns/l50` (raw_l50.npz, results_l50.json).

Why l50 is the honest closest achievable male substrate, all four checked before
writing this addendum:
  (i)  MALE graph, the L32-descended self-rhythmic cord regime (meta: g 0.01,
       beta 2.0, d 0.05, tau 0.05, 21,516 nodes / 2,977,920 edges);
  (ii) it stores the FOUR per-side antagonist pool traces (fL/fR/eL/eR) for
       every arm and seed — the composite's required inputs;
  (iii) its window convention is BIT-COMPATIBLE with comp.py's: WIN 6000,
       DT 0.01, SEGB [(0,2000,0.7),(2000,4000,1.4),(4000,6000,0.7)], MEAS0 500,
       TS = arange(499,6000,10). Unlike stage (b2) this needs NO TSQ rebinding
       for the 0.7-Hz primary; the per-segment reads of D4 below are the only
       window addition, and they are a SUPERSET of comp.Q07;
  (iv) it has stored per-side S values and duties computed by its OWN code
       (l50_traj.py S_of / s_arrays / wmed), so a B3-CERT is possible.
l50's antagonist pair is Tr ONLY (l50_traj.py line 236 reads PAIRS["Tr"]), so Ti
is EXCLUDED, not computed uncertified — the (b1) rule.

## b3.1 DECLARED CONVENTIONS (additions only; C1-C9 of the main PREREG stand)

D4 WINDOW: per-SEGMENT trailing-500 windows, TS_seg = TS[(TS >= a0+MEAS0) &
   (TS < b0)] for each of the three SEGB segments, installed by rebinding
   comp.TSQ (the stage-(b2) mechanism, so the arithmetic stays byte-identical to
   the certified stage-(a) code). The 0.7-Hz segments (0 and 2) are the PRIMARY
   reads; segment 1 (1.4 Hz) is read because l50's headline finding lives there.
D5 FLOOR: depth = max(ptp(flex window-block), ptp(ext window-block)) over the
   segment's measurement span, bar 0.03 — the same readability bar l65/(b1)
   used. Reported BEFORE any verdict, per (b1)'s rule that the composite is
   UNSAFE on a floored axis.
D6 ARM AXIS: l50's five arms are DRIVE SCHEDULES (free, ent, allw, duty58,
   min5), not identities and not wiring. So (b3) has NO identity cell; its
   licensed cells are ORDERING and per-side structure.
D7 PER-TERM FIRST: per (b2)'s method law, the per-term (A-only / PLV-only /
   Ph-only) decomposition is computed and REPORTED FROM THE START, not derived
   after a surprise.

## b3.2 CELLS

PRIMARY (ordering): Spearman of the arm-mean composite against the arm-mean
  stored structure (per side, per segment, both bands, alpha=0 and alpha=1):
  rho >= +0.5 on both 0.7-Hz segments = the composite reproduces l50's male
  schedule ordering.
PRIMARY (the two registered l50 findings, re-asked of the instrument):
  P-A CHOP>CONTINUOUS: stored mean duty_all duty58 .576 > allw .285 / ent .307.
     Does composite(duty58) > composite(allw) and > composite(ent)?
  P-B FAST-SEG TOXICITY: stored seg1 mean duty allw .022 vs free .538.
     Does composite(allw, seg1) < composite(free, seg1)?
  Each scored per side and per band; 3/3 seeds required for a "reproduces".
SECONDARY: per-term ranks (A-only, PLV-only, Ph-only) vs the same stored
  structure, to say WHICH term carries or inverts the male ordering.
BRANCHES: M1_transfers (primary ordering rho >= +.5 and both P-A/P-B reproduce)
  > M2_partial (one of the two reproduces, or ordering survives on one side
  only) > M3_inverts (rho <= -.3 or either registered finding reversed).
DEGENERATE: if composite range across arms < .05, or if every cell is floored by
  D5, the cell is UNINTERPRETABLE-BY-RULE and reported as such (b2 precedent).

## b3.3 PREDICTIONS (scored honestly, wrong ones disclosed)

Qb3-1: The gate annihilates a FOURTH time (frac P>2 near 1.0, alpha=1 collapses
  the composite to near-zero), so alpha=0 is again the only readable rung.
Qb3-2: The dominant amplitude term A will again be the inverting term on at
  least one side, and the minority phase terms (PLV/Ph) will track the stored
  structure better than the composite does — (b2)'s law transporting to the male
  graph. If A tracks POSITIVELY here, (b2)'s law is substrate-specific and I say
  so in those words.
Qb3-3: P-B (fast-segment toxicity, a near-dead vs healthy contrast) is the leg
  most at risk from the (b1) floored-axis failure: allw seg1 is nearly silent
  (stored duty .022) and silent pools are perfectly amplitude-BALANCED, so I
  predict the composite REVERSES P-B (reports allw seg1 >= free seg1).
Qb3-4: The band-floor fraction is 0.0000 a fourth time (that band prediction has
  now been wrong three times; registered again for the record).

### READ-ONLY
No npz written; input mtimes asserted unchanged; no live service touched; no
draft edit. Artifacts: `banc/l176/{comp_b3.py, results_l176b3.json, run_b3.out}`.
