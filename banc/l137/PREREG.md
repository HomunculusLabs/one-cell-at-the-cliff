# L137 PREREG — dnp33-dynamic-probe: Zhang static arm + dynamic design card (ideas 71, tick 160)

Card (LANE.md ideas-70/71): L134 showed first-order statics cannot predict
the carrier (1110 mid-pack on every wiring metric). Tick-158 field fold
(Zhang 2610.00690): shared input is a SECOND-order handle — in BANC and
MaleCNS shared-input predicts DN-DN interconnection complementarily to
spatial overlap. This tick = (S) zero-rollout static arm + (D) the
registered design card for the dynamic probe; the RUN is a follow-up slice
(l137_run, next tick). PREREG BEFORE any static number is computed.

## S. Static arm: in-mass-weighted shared-in-neighbor overlap (zero rollouts)

Substrate: banc_graph.pt extraction VERBATIM l134_static.py (pins
re-asserted: l92 n_old/n_new/dn_new, l107 cut K/mass_share/n_cut, l121
k19/k29/k58 drop_ids, l131 rank25==1110 / rank26==319). Family = the
ng-58 (ng_desc, heavy-77 minus glut-19). Twins: 1110 (DNp33-L, rank 25,
the X1 carrier) and 319 (DNpe025-R, rank 26, base-neutral 2 batches).

Measure: for cells a,b, cos(v_a, v_b) where v_c[s] = sum of |w(s->c)| over
in-edges — computed BOTH on closure edges (emask_n; the substrate the
dynamics runs on = PRIMARY) and on the full graph (all in-graph edges =
robustness column, closer to Zhang's all-partner form). Overlap profiles
are over the 56 family cells excluding both twins.

Registered reads (deterministic, no RNG — the ng-58 empirical distribution
IS the reference class, L70 over-representation form; rank p = rank/58
under exchangeability, disclosed as such):

- Z1 (DISCRIMINATING, primary): carrier outscores neutral twin on family
  overlap — ALL THREE legs required:
  (i) mean_fam(1110) > mean_fam(319) over the same 56 cells;
  (ii) paired cell-level sign test: cos(1110,f) > cos(319,f) on >= 31/56
       family cells;
  (iii) rank(1110) < rank(319) in the 58-internal fam_mean ranking.
- Z2 (flip-relevant subsets): same three legs on the always-cut core
  (ranks 1-19, present in every ng arm) and on the completion band
  (ranks 20-24, the k20->k24 partial climb).
- Z3 (Zhang interconnection column): direct |w| mass of twin<->family
  edges (both directions); reported, predicts nothing on its own.
- Z4 (registered else-branch): if Z1 fails -> statics AGAIN cannot
  separate carrier from twin at any order we can measure; the mechanism
  hunt stays DYNAMIC and the design card below is the only open path.
  Registered interpretation, not a failure.

Covariates disclosed: in-degree + in-mass of both twins (cosine grows
with degree overlap by construction; the within-family ranking is the
control), twin-pair cos(1110,319), and each twin's top-5 overlap partners
by rank position (core vs band vs tail) for the writeup.

## D. Dynamic design card (l137_run, next tick; registered NOW)

Question: WHY does removing 1110 (with ranks 1-24) flip kill->super while
removing mass-twin 319 does nothing? Two mechanisms are live:
(ACTIVITY) the cell's ongoing drive suppresses Ti_R structure — removing
its firing releases the rhythm; (WIRING) its edge footprint / the
renormalization that follows removal reorganizes the sheet — activity is
irrelevant. The clamp arm separates them by construction: clamping
X[1110]=0 removes ACTIVITY with the WIRING untouched.

Substrate + machinery: l133/l135 verbatim (extraction, pools via
peripheral_target_type, draw order, noise streams, verdict criteria
VERBATIM L118-L131: KILL meanR <= m0-.10 & kR <= 4 & paired dR <= -.20;
SUPER meanR >= .60 & kR >= 12; PARTIAL meanR in [.35,.50] & kR 3..8;
RESTORE meanR >= .45 & kR >= 12). Fresh B27 = 3101-3116, absence
asserted across ALL stored npzs pre-run (l135_precheck form). Gains: the
intact-closure graph is IDENTICAL for every clamp/volley arm -> ONE gain
(full, stored-form re-bisect lands EXACT); no per-arm bisect needed
unless an arm changes the graph (none do — clamps act on X, volleys on
drive; both enter AFTER settle, L36 law). ANCH = [801, 901] + C0A chain
retained + B-cert (l135 B26 table) BEFORE any B27 read.

Pre-run viability probe (ONE base rollout, seed 3101, zero extra arms —
L95 form): window u/X census for 1110, 319, all ng-58. Classifies the
clamp-no-op risk BEFORE the grid: if baseline mean_X(1110) < .01 the
clamp is near-vacuous (cell already silent -> mechanism leans WIRING by
census, arm kept with disclosure); if mean_X >= .95 the cell is
ceiling-pinned (clamp = the only visible direction, disclosed).

ARMS (intact closure substrate; 18 seeds each):
- full (base; extends the pooled full column, noisy 2-10/16, never a
  point — secondary by LANE precedent).
- sil1110 — X[1110] := 0 every step, settle-end through window (L2
  opto form; out-edges REMAIN — activity-only removal).
- sil319 — neutral-twin clamp (within-graph control, L133/L135 form).
- silrand1..3 — clamp ONE random ng-58 cell per draw (seeded, exclude
  both twins): the L78/L91 sham class; their spread is the perturbation
  floor. NO bare-arm claim — every clamp credit = arm minus this spread.
- vol1110 — tonic positive drive onto 1110 after settle (amp = census
  |u_min| + .1, one value, no amp sweep this tick); paired sham volrand
  (same amp, random ng cell). If Z1 fired, prediction: drive pushes
  toward KILL/partial (mirror of removal->super); if 1110 is
  buried/pinned the census decides and the arm discloses.
- SECONDARY population arm sil24 — clamp ALL ranks 1-24 (the wA window
  as a population): the class-level clamp twin of cutwA. If sil24
  reproduces even PARTIAL while sil1110 alone does nothing, the flip is
  a POPULATION-drive effect that 1110 merely completes (L20 class-vs-
  cell lesson, resolved by direct test).

Gates (registered outcomes, decided on B27 + pooled extension):
- G1 (the discriminator): sil1110 vs sil319 paired per-seed dR +
  classification.
  (a) sil1110 SUPER/PARTIAL while sil319 inside full's band -> ACTIVITY
      mechanism: the cell's ongoing drive carries the suppression;
      edge-removal unnecessary. Strongest possible single-cell result.
  (b) sil1110 ≈ sil319 (inside sham spread / full band, dm probe run)
      -> WIRING mechanism: the flip rides the edge footprint +
      renormalization; the clamp cannot reach it. Mechanism named, not
      a failure.
  (c) sil1110 outside spread in the WRONG direction -> L35/L38 class,
      census re-read before any wording.
- G2: vol1110 direction (secondary, sham-referenced).
- G3: sham-spread cell — silrand defines the floor; report arm-vs-spread
  for every clamp (L91 73%-sham-share lesson: the sham share IS a
  headline number, not a footnote).
- dm probe every arm (L35/L30): max|dX| vs unclamped control on the
  same noise stream; af assert; prefix bit-identity where applicable.
- Pooled Wilsons unrounded (L90); batch labels vocabulary-checked
  (L109); every pinned number re-derived from stored jsons (L44).

Budget note: ~10 arms x 18 seeds + probe ~ 1800-2200 s CPU (l133/l135
class). NOT run this tick — this tick ships PREREG + static + design.

## ADDENDUM (pre-run, tick 164 — L141 execution; registered BEFORE launch)

- A1 (no bisect phase): every arm runs the intact full graph at stored
  G_NEW (b65 at G65). NO re-bisect loops are run; certification is
  full/b65 BIT-IDENTITY at 801/901 vs raw_l113 AND raw_l135 (chain root
  + latest run). Reproducing the stored trajectories bit-for-bit at the
  stored gains subsumes the af-equality a re-bisect targets. The cut-
  graph build is retained verbatim ONLY for its pins + sil24's cell set
  (== cutwA drop ids, asserted == l131 stored); no cut arm is rolled out.
- A2 (B-cert form, zero-rollout L85): l137_verdict.py recomputes l135's
  FULL 13-arm Ti table from stored raw_l135.npz B26 traces and asserts
  == results_l135.json EXACT (rounding path verbatim) BEFORE any B27
  read, plus the C0B l113 5-arm cert (metric atoms) — BEFORE any new
  number.
- A3 (draws pinned): rng = np.random.default_rng(20261118); 4 draws
  without replacement from ng-58 minus {1110, 319} -> silrand1..3,
  volrand in draw order; IDs recorded in the raw npz; asserted non-twin.
- A4 (probe): ONE full-arm-only base rollout at seed 3101 (L95 form)
  records window u = drive + BG and X for {1110, 319} + all ng-58;
  VAMP = |u_min(1110)| + 0.1 (PREREG value, one number); clamp-no-op
  classification per PREREG (mean_X < .01 near-vacuous -> census leans
  WIRING; >= .95 ceiling-pinned, disclosed). FREE anchor: probe traces
  must equal the main-pass full@3101 traces bit-identically (same-
  generator deterministic reroll).
- A5 (G1 operationalization): "inside full's band" := no KILL/SUPER/
  PARTIAL classification AND |meanR - m0| < .10 AND kR within full kR
  +- 4. (a) sil1110 SUPER or PARTIAL while sil319 in-band -> ACTIVITY.
  (b) both unclassified AND |meanR_1110 - meanR_319| <= .10 AND kR gap
  <= 4 -> WIRING (dm read reported). (c) sil1110 KILL or meanR <=
  m0 - .10 -> census re-read before wording (L35/L38).
- A6 (dm form): per arm-seed dm = max|mm_a - mm_full| and max|xm_a -
  xm_full| over the window (L30/L35 form), from raw traces; dm == 0.0
  = arm bit-identical to full (channel-never-crossed instrument).
- A7 (pooled): the full column pooled union extends B16..B27 (n=192);
  every intervention arm is single-batch B27 n=16 (disclosed as such).
