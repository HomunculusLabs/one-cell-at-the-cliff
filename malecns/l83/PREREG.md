# L83 PREREG — glide-entry (LANE.md ideas 41, tick 109)

Registered BEFORE any rollout. Expected twin values RE-DERIVED this tick from
`l81/results_l81.json` (stored cells; L44 rule — never from log sentences).

## Question

The one untested ENTRY envelope (L79 gap/re-prime and L81 volley exhausted
POST-transition shapes; L82 showed the echo's fast-seg cost is entry-carried):
instead of the 0.7-chop -> 1.4 STEP at k=2000, GLIDE the entrain frequency
0.7 -> 1.4 (linear chirp, phase-continuous, amp continuous .3) across
G ∈ {200, 300, 400} steps, then hold 1.4. Does the fast window's structure
distribution lift vs the step entry at EQUAL drive budget (glide replaces the
step's frequency, adds no mass)? Lock + budget alongside (the triple, never
summed).

## Machinery (l81 verbatim unless named)

- Substrate: frozen L32 arm-A cord (21,516 nodes / 2,977,920 edges asserted),
  G .01 / BETA 2 / D .05, SETTLE 400 @0.7 Hz, WIN 6000, DT 10 ms.
- Schedule: chop 500-on/400-off @0.7 Hz segs, continuous .3 @1.4 seg1;
  hybrid-family hop volleys at 2000 & 4000 (HOP_VW 40, HOP_AMP .5, DNge046_L).
- Census seeds n=16 ([11,22,33]+101..113), ONE generator per seed, X0 cloned
  per arm, shared per-step noise tensor (L45b/L36 form).
- ARMS (6): hynohop, hybrid (twins), glide200, glide300, glide400 (nohop
  family), hyglide300 (hybrid family).
- Glide: f(k) = 0.7 + (1.4-0.7)*(k-2000)/G for k in [2000, 2000+G), else
  target(k); phase accumulated once per step (l39 convention). Prefix
  [0,2000) uses identical arithmetic => PHIT prefix EXACT-equal to the twin's
  PHI (asserted at build). Post-glide carrier carries a CONSTANT phase offset
  vs the twin (phase-continuous chirp; the drive is the only clock — covariant
  in every phase read; offset measured + disclosed).
- AMPA table IDENTICAL for all arms (glide alters frequency only);
  DRIVE_ON = 4800 every arm (assert). Amp-mass ratio per arm from per-arm sin
  table (~1.0, reported).

## Windows (l81 verbatim; all fully inside the 1.4 hold for every G, glide
ends <= 2400 < 2500)

- wearly (2500, 3200); wpost PRIMARY (3200, 4000); wpost_late (3600, 4000).
- f_glide (descriptive): dom_freq of block (2000, 2500) — contains the glide
  (twins: their re-lock transient block).
- lock_post: blocks (3000,3500), (3500,4000), err vs 1.4; straddle block
  (2400,2900) err vs 1.4 = post-glide re-lock, window common to all arms.
- seg1 row lock reads are CONFOUNDED for glide arms (blocks inside the glide
  chase a moving target) — disclosed; lock gates read lock_post/straddle only.

## Reads

- P1 per glide arm (paired vs twin): d_post = wpost(glide) - wpost(twin) per
  seed; verdict HELP if mean >= +.10 AND n_up >= 11; HURT if mean <= -.10 AND
  n_down >= 11; else NULL/INCONCLUSIVE. k(wpost >= .25) + Wilson vs twin k.
- P1b dose ordering: glide300-glide200, glide400-glide300 paired means.
- P2 lock: lock_post err<=.01 count (gate) + straddle mean (descriptive).
- P4 miss anatomy: wpost < .25 seeds decomposed SL/SR/both-owned.
- P5 budget: drive-on steps equal by construction; mass ratios.

## Anchors

- C0a/C0b: twins bit-identical to l59/raw_l59.npz (mm + fL/fR/eL/eR, seeds
  11/22/33, full [0,6000)) — 28th consecutive chain anchor.
- C0T: twin wpost arrays == l81 stored cells EXACTLY (twins re-roll
  bit-identically; analysis deterministic).
- C0P-1: glide arms prefix [0,2000) bit-identical to twin, 16/16 seeds,
  mm + 4 traces.
- C0P-2: first divergence glide-vs-twin in {2000, 2001} — direct drive-table
  swap at k=2000 predicts 2000; one-step indexing tolerance disclosed
  (NEW-intervention form; measured law reported either way).
- C1: settled af in (0.01, 0.9) every arm-seed. wired_dead = 0 (dm > 0 every
  glide arm-seed).
- Build-time asserts: PHIT prefix exact-equal; AMPA all-arms-equal;
  DRIVE_ON 4800; HOPA twin parity (glide arms == hynohop none;
  hyglide300 == hybrid both).

## Registered predictions (discriminating; L55 rule)

- E1 (L52 entry-state law): the glide does NOT rescue the fast window —
  band d_post_mean in [-.15, +.10] every glide arm (NULL/HURT-leaning per
  L41 gentle-ramps / L48 adiabatic-release / L79 / L81 lineage).
- E2 (L34 Arnold tracking): the cord TRACKS the chirp — lock_post err<=.01
  on >= 14/16 per glide arm (a lock crash is itself the finding, L63 family).
- E3 (window-locality): sign(d_wearly) == sign(d_wpost) per arm (no
  dwell-deepening divergence; wpost_late co-read for the L79 late-deepening
  signature).
- E4 (miss anatomy): misses stay SL-owned (share >= .5).
- Degenerate branch: a glide arm bit-identical to its twin (dm == 0) = WIRING
  bug (L35/L39/L43 class), not a channel verdict — fix and rerun before P1.

## Expected twin baselines (from l81 stored json, re-read tick 109)

hynohop wpost mean .411 k 9/16 Wilson [.332,.769] | wearly .334 | seg1 .375
lock 16/16 .0009. hybrid wpost .422 k 8/16 | wearly .379 | seg1 .402
lock 16/16 .0009.

## Checkpoints

raw_partial per seed; raw_l83.npz BEFORE analysis; analysis crash =>
verdict re-derives from checkpoint, zero reruns. CPU-only; no live changes.
