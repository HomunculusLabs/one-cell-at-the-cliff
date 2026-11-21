# L77 PREREG — echo-on-endgame-census (registered 2026-11-15 03:4x, PRE-DATA)

QUESTION: L59 measured the endgame pooled structure gate is a FAIR COIN
(hynohop 8/16, hybrid 8/16, Wilson [.28,.72]) at census n=16 (results_l59.json,
re-derived from raw this run, not memory). L66 measured the bilateral negative
echo (g .1, 50 ms delay) lifts OFF-window duty +.186 census-confirmed,
content=TRUE (donor sham -.001), lock pristine — but never ON the endgame
task. Does running the content-cell echo ON the two endgame schedules bias
the pooled coin?

ARMS (l59_ensemble.py machinery verbatim; echo wiring l66_census.py verbatim):
- hynohop    : l59 open twin (base chop, no hop, no echo)    [C0a anchor]
- hybrid     : l59 hybrid twin (chop + hop volleys @trans)   [C0b anchor]
- hynohop_fb : open schedule + echo (g .1, sign -, delay 5) [C0x anchor vs l66 g01_d05_m]
- hybrid_fb  : hybrid schedule + echo                       [NEW — the card's arm]
Echo: drive[mech] += .1 * (-1) * mA[k-5]; mA = mean X over the four Tr
antagonist pools (ANTAG def l66-verbatim), post-step write at index k;
applied only k >= 5 (never during settle); ALL arms share ONE per-step
noise tensor; X0 drawn once per seed and cloned per arm (L45b rule).

SEEDS: l45b census grid [11,22,33]+[101..113], n=16. CPU-only.

REGISTERED READS (the triple, never summed):
- P1 GATE (primary = hybrid_fb, secondary = hynohop_fb): k = #(pooled
  duty_all >= .5) per arm (l59 cells machinery verbatim: TS stride 10,
  499-back S windows, MEAS0 500, duty_all over all three seg meas windows).
  BIASED if k >= 11/16 with P2 intact. Paired per-seed flips reported.
- P2 LOCK: seg1 fast-window block-argmax err <= .01 count per arm (l59
  form; twins were 16/16). Arm PASS if count >= 12/16. A lock crash
  OVERRIDES P1 (toxic-biased, not a lever — L63 class).
- P3 DRIVE BUDGET: per-mech-cell echo mass = gfb * sum(mA[k-5]) over the
  window, and its ratio to per-mech-cell entrain mass
  (sum amp*(0.5+0.5 sin) over on-steps). Reported alongside, never summed.
- P4 SIDE ANATOMY: per-seg SL/SR means per arm; miss anatomy sl_share for
  fb arms (L66 prediction: rescue is S_L-loaded — does that signature
  hold on the endgame schedules?).

ANCHORS:
- C0a: hynohop arm == l59/raw_l59.npz (mm + fL/fR/eL/eR), seeds {11,22,33},
  every max|d| == 0.0 — 23rd consecutive chain anchor.
- C0b: hybrid arm == l59 raw, same, == 0.0.
- C0x: hynohop_fb == l66/raw_l66.npz arm g01_d05_m (mm + 4 channels),
  seeds {11,22,33}, == 0.0 (cross-run wiring probe: the l59-form step loop
  must reproduce l66's fb arm bit-exactly — same noise stream, same mA law).
- C0P: first_div(fb vs twin) == 5 for EVERY seed of BOTH fb arms; dm > 0
  for every fb arm-seed (wired-dead list must be EMPTY).
- C1: settled active fraction in (0.01, 0.9) for all arms/seeds.

DEGENERATE BRANCHES (registered — L55/L35/L39 rules):
- D1: k == 8/16 (unchanged coin) with dm > 0 => REAL NEGATIVE (echo content
  does not transfer to the endgame schedules) — a valid verdict, not vacuous.
- D2: any fb arm-seed with dm == 0.0 => INVALID RUN (wiring bug class);
  diagnose before reading any verdict.
- D3: P1 pass + P2 fail => TOXIC-BIASED verdict; the triple decides.
- D4: twin arms' distributions NOT matching l59 stored values => INVALID
  (anchors are value-checked, not just bit-checked — L44 rule).

EXPECTATION (falsifiable): the echo's lift concentrates in the 0.7 segs
(off-window duty is where l66 measured content); the fast-seg structure
lottery persists (L52 entry-state law); so hybrid_fb k predicted in [9,13]
with duty_07 lifting more than seg1 duty. A k of 16/16 with duty_07 ~ 1.0
would CONTRADICT the L52 entry-state law => suspect wiring first (D2).

## ADDENDUM 1 (registered 2026-11-15 04:1x, PRE-VERDICT, post-analysis-crash)
C0P amendment — THIRD instance of the L44 class, disclosed: the registered
`first_div == 5` was copied from l66's C0P *sentence*, but l66's STORED
results json carries first_div == 6 for every g01_d05_m seed (its own
c0p_ok False, fixed there by its ADDENDUM 1; pools see the mech echo one
hop later — delay+1). Correct anchor: first_div == 6 for all 32 fb
arm-seeds. Measured: histogram {hynohop_fb: {6:16}, hybrid_fb: {6:16}} —
matches l66 stored EXACTLY. C0P amended PASS.
Also disclosed: run-1 analysis crashed at the cells loop (l59 tuple-form
`dom_freq(...)[0]` over l66's single-value dom_freq) — rollouts were
already checkpointed to raw_l77.npz; the FULL analysis was re-derived from
the checkpoint by l77_verdict.py, zero reruns (L45a rule). C1 (af) verified
in-run pre-crash. All bit-anchors C0a/C0b/C0x re-derived from raws in the
verdict script, all 0.0.
