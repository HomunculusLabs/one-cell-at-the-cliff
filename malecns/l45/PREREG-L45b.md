# PREREG L45b — attractor census + channel transition edges (slice b of L45)

Written BEFORE the run. Machinery: l45_prune.py substrate verbatim
(21,516 nodes / 2,977,920 edges, g .01 / beta 2.0 / D .05 inert, TAU .05,
DT .01, SETTLE 400, one generator, one shared per-step noise tensor across
arms; CPU). No live changes.

## Design

- Census: 16 base seeds (11, 22, 33 anchors + 101..113), WIN 11000 (110 s).
  State measured per segment: SEG-A [500:2500], SEG-B [2500:5000],
  SEG-C [7500:11000] (post-drive window doubles as census C for the 8
  transition seeds' base arms).
- State axes (L45a amendment: S-sign MUST be a state axis):
  fband from rhythm2 on motor-mean trace (slow < 1.0, mid 1.0-1.8,
  fast2 1.8-2.6, fast3 > 2.6; FLAT if ratio < 5) x signL x signR,
  where S_side = median sliding 500-step anti-corr of that side's
  Ti+Tr flexors vs extensors; '+' S > .15, '-' S < -.15, '0' else.
- Transition channels (6): tonic I[chan] += AMP from step 5000 (t 50 s) to
  end — d_DNg110 (+0.25), d_DNge046 (+0.25), d_DNg95 (+0.25),
  d_DNg88rel (RELEASE, -8.0, L40 rel_amp), d_E1 IN17A001 (+0.25),
  d_X464 INXXX464 (+0.25). E1/X464 join per L45a verdict.
  Seeds 11,22,33,101..105 (8). FROM-state = SEG-B (shared pre-drive),
  TO-state = SEG-C.
- dm probe (L35/L37 discipline): channel pool mean X in SEG-C vs base arm
  same seed; dm == 0.0 exactly -> label pinned/buried, NOT an edge.
- Paired counterfactual (L41: transitions can be attractor selection):
  a channel is credited edge from->to ONLY if to != base arm's own SEG-C
  state on the same seed (base spontaneous migration is the null).

## Registered anchors (derived from STORED artifacts, L44 lesson)

- l40/results_l40.json ctl pre window [500:2500]: seed 11 f 1.35 SL .66
  SR .27; seed 22 f 1.45 SL .61 SR .08; seed 33 f 0.70 SL .49 SR .74
  (migrates to f 1.45 by post). l45a ANCH f_pre (window [3400:4000]):
  {.80, 1.44, 1.42}. Known attractor bands: slow 0.6-0.95, mid 1.25-1.55;
  L36 drive-shifted band 2.0-3.4; L40 late migration 3.3-3.5.
- C0 (substrate): across the 3 anchor seeds x SEG-A/B reads (6 reads),
  >= 5 land in {slow, mid} bands; median census r_mm >= 60 (l45a bar);
  median SEG-A S_L > 0 (l40: SL .49-.68 at base).
- C1 (mechanics): settle af in (0.01, 0.9) all arms; prefix bit-identity
  max|d mm| over steps < 5000 == 0.0 for every channel arm vs base
  (same seed); clamp-free run, no clamps this slice.
- C2 (census): table of distinct states with counts + within-run
  migrations (band or sign change between segments). Pre-registered
  expectation from l40/l33/l45a: mid-band dominates; slow exists; SR
  varies (sign axis populated); >= 2 distinct states across 16 seeds.
  Deviations are findings, disclosed, not failures.
- C3 (edges): from->to counts per channel with base-counterfactual
  column; DNg88rel TO-state expected FLAT/killed = STOP edge (l40
  rel kill S .45 -> .04-.15); DNge046/DNg110 expected mid->fast hops
  (l36 census, 0.8-2.0 -> 2.0-3.4). Rhythm-death TO-states are labeled
  STOP, never steering (L37 pairing rule).

## Disclosure rules

Vision QA may substitute analytic checks (per-pane ink, no-overflow) if
the vision endpoint is down — disclosed in the log. Any window/recipe
deviation from the above gets an addendum here BEFORE the verdict is read.

## ADDENDUM 1 (pre-verdict, 01:3x) — C1 caught a shared-init bug in v1

v1's run_seed drew X0 inside the dict comprehension: every arm got a
DIFFERENT init, so prefix bit-identity failed (max d 0.077) and transition
FROM-states were not shared. Fix = l45a-verbatim (draw X0 once, clone per
arm). Census base arm init is the same first draw, but the step-noise
stream shifts (v1 consumed 7 init draws, v2 consumes 1), so base
trajectories differ between versions — C0 anchors are band-level and
re-checked on the rerun. No verdict was read from v1.

## ADDENDUM 2 (post-verdict refinement, disclosed) — MOVED vs HELD split

The C3 edge table credits any TO != base's own SEG-C. Post-hoc, from the
raw npz checkpoint (same label recipe, verified to reproduce in-run labels),
each credited edge splits into: MOVED (arm left FROM; base stayed) vs HELD
(arm stayed at FROM; base drifted spontaneously). In a system where 11/16
base seeds migrate per 60 s, HELD is a stabilization claim, MOVED a drive
claim — both reported separately. L36's registered mid->fast hop expectation
for DNg110/DNge046 FAILED at census amp/window (0 fast-band TO states);
recorded as a finding, not a gate failure (expectation was a citation from
a different drive regime, per L44's anchor rule).


