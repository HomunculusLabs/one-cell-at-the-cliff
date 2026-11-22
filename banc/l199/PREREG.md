# PREREG — L199: the tone-phase registered test

Registered 2026-11-21 ~20:30 EST, BEFORE any L199 statistic is computed on any
trace and before any L199 rollout (no raw, gains or results file exists under
`banc/l199/`). Owner-directed (`banc/l199/BRIEF_tonephase.md`). Experimenter =
Miso session (claude-fable-5-2). L200 runs concurrently in its own directory.

What exists at registration: this text; `ph.py` (instrument); `selftest.py`
(SYNTHETIC traces only); `analyze_primary.py`; `build_tp.py` -> `run_tp.py`;
`analyze_causal.py`; `freeze.py`; `run_all.sh`.

## Hypothesis under test (L197b's post hoc, verbatim source: L197b-FINDINGS)

The carrier-deletion phenotype (sc25 vs cutwA, right tibia) is a change in the
pools' PHASE RELATION to the external 0.7-Hz tone: on the base graph the
cross-seed flexor-extensor anticorrelation appears when the partner is rotated
half a tone period (the pools CO-MOVE relative to the tone); with the carrier
removed it appears at zero rotation (they ALTERNATE).

## What has ALREADY been seen (disclosed; this limits what Part A can add)

The brief's instrument is not new to these data. On L197b's stored raws:
- the INTERACTION this test turns on, I = (in - anti)_sc25 - (in - anti)_cutwA,
  is algebraically L197b's registered `A_in_minus_anti`, already computed with
  intervals: S +.403 [+.345, +.462], W +.106 [+.044, +.169];
- the per-graph 3-bin POINT values (addendum.json, post hoc): S cutwA
  .186 / .236 / .465 and sc25 .423 / .299 / .298 (in / mid / anti); W cutwA
  .113 / .169 / .329 and sc25 .232 / .239 / .342;
- on L186 (pilot.json): the pooled contrast in phase / antiphase at W = 150,
  +.303 / -.163 (difference +.466 [+.274, +.658]); L186's stored phase
  secondary (carrier-present only): Ti_fR -100 deg, Ti_eR -90 deg vs GI 1110.

Consequences, stated before computing anything:
1. On S and W, PH1-vs-PH0 at the level of "is there a profile difference" is
   ALREADY decided by L197b (S yes; W direction only, under the .15 bar). Part
   A's 3-bin read of S and W is a formalisation with intervals, not an
   out-of-sample confirmation, and W's label below is fixed by a stored number.
2. NOT yet seen, and therefore what is actually at risk here: (a) intervals on
   the per-graph SIGN claims (S's sc25 slope is +.125 as a point value — its
   interval is unknown); (b) L186's per-graph profile; (c) the SIGNED-offset
   instrument (Part B — never computed on any dataset); (d) the direct
   per-seed pool phase against the tone (Part C — never computed for sc25);
   (e) the causal rollouts (Part D — fresh seeds, the only fully
   out-of-sample test).

## Datasets (Parts A-C: stored raws, ZERO rollouts)

| tag | raws | seeds | pulse | readout (window W, starts rel. flexor seed's onset) |
|---|---|---|---|---|
| S | l197b/raw_w0-5.npz | 19001..19096 | 500 | W 150, -75..+425 step 10 (L197b's registered S readout) |
| W | l197b/raw_w0-5.npz | 19201..19296 | 250 | W 250, -125..+125 step 10 (L197b's registered W readout) |
| V1 | l186/raw.npz | 18601..18616 | 500 | W 150, -75..+425 step 10 (same schedule law as S; the S readout) |

Onsets: l197b/schedule.json (segment-relative -> absolute [o0, 4000 + o1],
gate-position asserted against every stored gate array) and
l186/results_l186.json (absolute). Graphs: cutwA (base), sc25 (carrier removed).

## Instrument — the pair-SEGMENT phase statistic (fixes tick 216's error)

Unit event = ordered pair-segment (segment g in {first, last outer}, flexor
seed i, extensor seed j, i != j). `l197b/gj.py` UNCHANGED (sha asserted):
h_G(g,i,j) = fraction of start offsets with Pearson r <= -.25 (both SDs > 1e-6)
between flexor seed i's window at its own onset + offset and extensor seed j's
window at ITS own onset + the same offset (aligned clock), graph G.
Each pair-segment's OWN gate lag L = on_i - on_j (never a mean of the two
segments' independent lags) induces the tone-phase offset
psi = (L / 142.857) mod 1; folded rotation rot = |psi - .5| * 2.

### Part A — registered 3-bin conditioned profile (the brief's instrument)

Bin edges: **in-phase rot >= .75** (offset within +-1/8 period of 0);
**mid .25 < rot < .75**; **antiphase rot <= .25** (within +-1/8 period of a
half period). P_G(bin) = sum(h_G * 1[bin]) / sum(1[bin]) over ordered
off-diagonal pairs and both segments (`gj.ratio`).
- slope S_G = P_G(in) - P_G(anti)   (> 0: anticorrelation at zero rotation =
  ALTERNATE; < 0: at half rotation = CO-MOVE)
- interaction I = S_sc25 - S_cutwA
- pooled elevation E = aligned duty sc25 - cutwA over all pair-segments
- descriptive: curvature P(mid) - (P(in) + P(anti)) / 2 per graph; pair-segment
  counts per bin.
Intervals: delete-one-seed jackknife, normal 95% (`gj.jack`; the seed is the
unit, pairs are not independent).

Contrast bands, per dataset (.15 = the lineage's standing effect bar and
L197b's M_tone bar; +-.10 = its registered equivalence margin):
- **PH1_sign** — I >= .15 with CI above 0, AND S_cutwA < 0 with CI below 0,
  AND S_sc25 > 0 with CI above 0 (the post hoc as stated: co-move -> alternate).
- **PH1_shape** — I >= .15 with CI above 0, but not both sign conditions (the
  deletion reshapes the profile without a reversal).
- **PH_weak** — CI(I) above 0 but I < .15.
- **PH0** — CI(I) inside (-.10, +.10): no profile difference beyond the
  pooled elevation E.
- **PH_rev** — I <= -.15 with CI below 0.  **PH_unresolved** — anything else.

**Part A verdict:** `PH1` if S and V1 are both PH1_sign or PH1_shape and W is
not PH0 (suffix `_sign` only if S and V1 are both PH1_sign; W is stated
beside it as the short-pulse design); `PH0` if at least two datasets are PH0;
otherwise `MIXED`, each stated. Fixed in advance by stored numbers: W =
PH_weak; S is PH1_sign or PH1_shape. Open: S's sign-vs-shape, V1 entirely.

### Part B — signed-offset profile (registered; never computed before)

The folded rotation cannot see a quarter-period relation and discards lead vs
lag. Per dataset and graph, OLS over all ordered off-diagonal pair-segments:
h_G = m + a cos(2 pi psi) + b sin(2 pi psi). Preferred offset
**theta_G = atan2(b, a)** (the tone-phase offset of the flexor seed's gate
behind the extensor seed's at which cross-seed anticorrelation is most
frequent), amplitude R_G = sqrt(a^2 + b^2). If both pools follow the tone with
peak phases alpha_f, alpha_e, theta = (alpha_f - alpha_e) + 180 deg: co-move ->
180, alternate -> 0. Jackknife (delete-one-seed) SE of theta_G from the
wrapped replicate deviations; same for dtheta = wrap(theta_sc25 - theta_cutwA).
8-bin signed profile (psi octants centred 0, 45, ...) stored, descriptive.
- **H1** — theta_cutwA within 180 +- 45 AND theta_sc25 within 0 +- 45, both
  with SE(theta) <= 22.5 deg.
- **H0** — |dtheta| + 1.96 SE(dtheta) < 45 deg (same preferred offset; the
  deletion scales or lifts the profile only).
- **Hq** — both SE(theta) <= 22.5 deg, neither H1 nor H0: the profile ROTATES
  by dtheta (a phase-relation change, but not co-move -> alternate); angle
  reported.
- **Hu** — an SE(theta) > 22.5 deg: preferred offset not determinable.

### Part C — direct pool phase against the tone (registered secondary)

Per seed, graph, pool (Ti_fR, Ti_eR): OLS of the stored trace over the two
displaced pulses [onset, onset + pulse) on [segment intercepts, cos PHI,
sin PHI], PHI = the harness's elapsed tone phase (re-derived: cumulative
2 pi f DT, f = .7 / 1.4 / .7 Hz by segment). alpha = atan2(b_sin, a_cos);
fits with amplitude <= 1e-6 omitted. Delta = wrap(alpha_f - alpha_e) per seed
(positive = flexor peaks later). Per dataset and graph: circular mean, resultant
R, n; paired per-seed shift wrap(Delta_sc25 - Delta_cutwA) circular mean + R.
Labels (R >= .5 required, else `dispersed`): **co-move** |mean| <= 60 deg;
**alternate** |mean| >= 120 deg; **intermediate** otherwise.
- **D1** base co-move AND removed alternate; **D0** same label in both graphs
  and |paired shift| <= 30 deg; **Dq** otherwise (shift reported).
Same-seed traces share noise; this is a within-seed measurement and is read
beside Part B's cross-seed theta - 180, not instead of it.

## Part D — causal tone-phase manipulation (rollouts: 4 arms x 16 seeds)

Arms = {cutwA, sc25} x {phi0, phiPI}, the SAME 16 fresh seeds 19931..19946 in
all four (identical settle, noise stream and stored-form gains). Gate =
the CANONICAL unjittered schedule for every seed (zero gate lag between any
two rollouts). phiPI: the window tone is `ENT_AMP * (0.5 + 0.5 sin(PHI + pi))`
at every one of the 6000 steps (a half-period shift at 0.7 Hz; the tone is
mirrored about its mean); settle untouched, so phi0 and phiPI start from the
identical state. Storage tag of a phiPI rollout = seed + 50000 (RNG seed
unchanged). Every pair of rollouts therefore shares the gate exactly; only
the tone phase differs: 0 for same-phi pairs, half a period for cross-phi
pairs. A gate-edge-locked timing predicts NO difference between the classes.

Readout: the S readout (W 150, starts -75..+425 step 10) at onsets 900 / 4900.
Per graph G, distinct-seed ordered pairs only, both segments:
- within_G = mean duty over the phi0-phi0 and phiPI-phiPI blocks;
- cross_G = mean over the phi0-phiPI and phiPI-phi0 blocks;
- K_G = within_G - cross_G (the causal analogue of S_G);
  **K_I = K_sc25 - K_cutwA** (the causal analogue of I);
- E_00, E_PP, E_X = sc25 - cutwA duty in the phi0-phi0, phiPI-phiPI, cross
  blocks.
Delete-one-seed jackknife over the 16 base seeds (a deleted seed leaves both
phi arms). Bands:
- **CA1** (the phenotype follows the tone) — K_I >= .15 with CI above 0 AND
  E_PP > 0 with CI above 0 (it reappears intact when BOTH partners are
  shifted). Refinement **CA1_sign**: also K_cutwA < 0 (CI below 0) and
  K_sc25 > 0 (CI above 0).
- **CA0** (not carried by tone phase) — CI(K_I) inside (-.10, +.10).
- **CA_weak** CI(K_I) above 0, K_I < .15; **CA_rev** K_I <= -.15, CI below 0;
  **CA_unresolved** otherwise.
Read only if: C0A exact in every worker; gains == stored floats; every stored
gate == canonical; manipulation check **MC**: stored tone(phi0) + tone(phiPI)
== ENT_AMP * gate to 1e-12 at all 6000 steps for all 16 seeds, and the two
tone traces differ. Descriptive beside it: same-seed duty per phi; the
same-seed cross-phi duty; Part C's Delta per graph and phi; v1's 500-step
readout; duty of the cross-phi blocks separately.
Power, honestly: n = 16 is the brief's cap. L186's n = 16 SE of the in - anti
contrast was .098 with 25% of pair-segments per bin; here every pair-segment
is in a class (4x), so SE(K_I) ~ .05-.08: power > .95 for an effect of S's
size (.40), about .5 for one at the .15 bar.

## Certification

- Part A CERT-197b: recomputed `A_in_minus_anti` (S, W) == results_l197b.json
  and the six per-graph bin means == addendum.json, to 1e-12; `gj.py` sha ==
  l197b FREEZE; every stored gate == its registered schedule.
- Part D: **C0A** — unjittered, unshifted cutwA + sc25 @801/901 bit-identical
  to l135/raw_l135.npz on 22 traces + af (92 checks per worker) BEFORE any
  fresh rollout; non-zero = that worker VOID. Gains: stored-form bisect ==
  0.14365819573402408 / 0.1454454553127289 EXACT. Fresh-seed key-scan: no
  numeric token of any member name in any lab npz equals 19931..19946 or
  69931..69946 (at freeze, re-asserted in each worker). `run_tp.py` = a
  count-asserted transform of the hash-pinned `l186/run.py`.
- `selftest.py` (synthetic sinusoid pools with a planted Delta): the
  instrument must recover theta = Delta + 180 and Delta before freeze.

## Predictions (registered, scored)

- Q1 (.90): CERT-197b passes exactly.
- Q2: S — S_cutwA < 0, CI below 0 (.97); S_sc25 > 0, CI above 0 (.85);
  label PH1_sign (.85).
- Q3: W — sc25 slope NEGATIVE with CI below 0, i.e. no reversal under the
  250-step pulse (.80).
- Q4: V1 — I >= .15, CI above 0 (.90); S_cutwA CI below 0 (.80); label
  PH1_sign (.45), PH1_shape (.45).
- Q5: Part B — S: theta_cutwA within 180 +- 45 (.80); theta_sc25 within
  0 +- 45 (.55); H1 in S (.50), Hq (.35). W: not H1 (.75).
- Q6: Part C — base labelled co-move in all three datasets (.75); removed
  labelled alternate in S (.40), intermediate (.45).
- Q7: Part D — certs + MC pass (.90); K_cutwA < 0 with CI below 0 (.75);
  CA1 (.70); CA1_sign (.40); E_PP CI above 0 (.75).

## Scope

One model class; the movable pulse of the 0.7-Hz segments at graph-specific
AF-matched gains; cross-seed duty of the right tibia pair. Parts A-C are
correlational re-reads of stored batches (S and W partly seen, as disclosed);
Part D is one 16-seed batch at the canonical schedule and a single shift
(half a period). Part D shifts the whole window tone, not the gate; it does
not separate tone phase at gate ONSET from tone phase during the pulse. No
DRAFT / numbers.json / LANE edit; FINDINGS carries a draft-fold NOTE only.

## Compute and writes

Parts A-C: one process, <= 2 threads. Part D: 3 workers x 2 threads (CPU <= 6),
nice 5, per-seed atomic checkpoints. Wall <= 2 h from dispatch (~20:20).
Writes: `banc/l199/**` and one LAB-INTENT.md section append.
