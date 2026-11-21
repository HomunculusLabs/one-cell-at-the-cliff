# L94 PREREG — female-closure-rebase (LANE.md ideas 48, tick 119)

Pinned BEFORE any L94 rollout. Every expected value below is derived from
STORED artifacts (L44 rule): l92/static.json + raw_l92.npz (substrate, g*),
l93/raw_l93.npz (closure base traces + pre-derived anchor cells in
l94/prederive_anchor.json), l91/raw_l91.npz + results_l91.json (protocol,
donor law, certification targets), l68/raw_l68.npz (echo donors).

## Question

L91 measured the female endgame multibatch on the l65 subnet (g 0.14):
Ti base 48/48 batch-ROBUST, Tr side-split L .16-.17 / R .95-.98. L92's law
says the closure substrate (keep = cord | dn_into | dn_proj) is the honest
one and measurably CHANGED the base (deader both sides at anchors). Re-run
the L91 protocol on the CLOSURE substrate: (Q1) does female Ti
batch-robustness survive the closure? (Q2) does the Tr side-split persist
or re-draw? This becomes the substrate the endgame contract cites.

## Substrate (L92, pinned)

- Closure subnet: n 21,809 / edges 647,953 / n_old 21,249 / dn_new 560.
  Assert vs l92/static.json: n_old/n_new/edges_old/edges_new/pool_sizes
  (Ti 50/51/6/6, Tr 31/31/24/24)/mech 4848/dng100 2/dn46_in_subnet 3.
- Gain g* = 0.153125 (l92 stored bisect to af_target 0.109056).
- Noise law (L92 two-generator, verbatim): gen(seed) draws ONLY old-cell
  tensors (randn(21249,1) for X0 then one per settle/win step) = l91's
  exact draw order; gen2(seed+9000) draws the 560-cell stream. Joint
  settle advances Xo(old subnet, g*) and Xc(closure) — l93 verbatim —
  so old-cell noise is bit-identical to l91/l92/l93 streams.
- Schedule l91 verbatim: SEGB 0.7/1.4/0.7, AMPA chop 500-on/400-off seg0+2,
  continuous seg1, SETTLE 400, WIN 6000, ENT_AMP 0.1, BETA 2, D 0.2
  (DNg100 tonic), TAU/DT/RMAX 0.05/0.01/1.0, BG/NOISE 0.02/0.01.

## Arms (5, all cloned from the same post-settle state)

- cfn — base trunk (no treatment).
- cfn_fb — echo cell verbatim (gfb .1, delay 5, sign −1) reading closure
  Tr-ANTAG mean; donor = l68 hyb01 Tr-ANTAG mean, cyclic law verbatim
  (anchors NEXT {11→22,22→33,33→11}; fresh: ANCHOR[batch.index(seed)%3]).
- csham — donor-driven sham echo (transport control, L78/L91 form).
- cfh — hop volley: DNge046 ALL in-subnet cells [270, 302, 366]
  (l92 static dn46_pos; 2 DNn + the un-buried DNi cell), amp 0.5,
  VW 40 steps at k∈[2000,2040)∪[4000,4040) (male l59/l90 trunk form).
- cfh_fb — hop + echo.

## Batches / gate

- ANCHOR [11,22,33] (anchors only, not pooled); fresh B4 801-816,
  B5 901-916, B6 1001-1016 (never used in the lineage). n_pool = 48.
- G2a-multi VERBATIM L90/L91: pooled Wilson lb FULL precision >= .717,
  k_min 41/48; asserts wilson_lb_full(41,48) >= .717 > wilson_lb_full(40,48)
  and the l90 stored n=32 pin (28, not 27 — L44 instance #5).

## Anchors (all must pass before any read)

- C0A: cfn (mm, xm, 8 pool traces) == l93 raw base BIT-IDENTICAL
  (max|d| == 0.0) seeds 11/22/33 — 37th consecutive chain anchor.
- C0B (certification, L85 rule): my verdict metric code on raw_l91.npz
  arms fn/fn_fb/fsham reproduces results_l91.json EVERY pinned read
  (per-batch k/wilson/duty07/seg1/seg2/L/R means, pooled rows, anchor
  duty_07, budget fn_fb .2511) BEFORE pinning any new L94 number.
- C0P-1 echo law (all 51 seeds): cfn_fb vs cfn fd_xm == 5, fd_mm == 6;
  csham vs cfn fd_mm == 6 (l66/l91 stored one-hop law).
- C0P-2 hop law: cfh vs cfn fd_mm ∈ {2001..2006} (l92 stored range at
  amp .5, transitions); L93 ADDENDUM-1 escape clause: a larger fd is the
  volley cell's X rise-time (burial diagnostic), disclosed — never a
  wiring-fail read. cfh_fb vs cfn_fb same law.
- C1: post-settle af ∈ (0.01, 0.9) every seed, EQUAL across arms.
- C2: every treatment arm diverges (dm > 0 vs cfn, all 51 seeds). A
  bit-identical cfh would mean the trunk port died again (L91 dead-channel
  class) → ADDENDUM before reads.

## Pre-derived anchor pins (my-form cells on stored l93 base, EXACT once C0A holds)

- cfn Ti duty_07 {11: .073, 22: .517, 33: .200};
  Ti d07L {.153, .600, .500}; Ti d07R {.510, .767, .393}.
- cfn Tr duty_07 {.027, .003, .037};
  Tr d07L {.057, .047, .037}; Tr d07R {.560, .457, .253}.
- Context pins (l65, l91 stored): fn Ti anchors {.937, 1.0, 1.0} →
  the closure measurably deader on Ti at anchors (1/3 >= .5).

## Registered expectations (claim levels)

- E1 (Q1, MEASUREMENT, no directional gate): cfn Ti G2a-multi —
  clears = Ti robustness SURVIVES the closure; fails = closure-fragile
  (anchor-informed prior: 1/3 anchors >= .5 → expect FAIL; disclose either).
- E2 (Q2): Tr side-split PERSISTS if per-batch duty07L_mean <
  duty07R_mean − .10 on >= 2/3 batches for cfn (sign test; magnitude
  free to move off the l65 ceiling).
- E3: echo cell lift fb−cfn on Ti and Tr (means over 48); sham share =
  mean sham lift / mean fb lift; disclose carry (>= .5) per transport law.
- E4: hop arms first LIVE trunk-port read female-side: report dm, per-side
  duty deltas, per-batch k; NO wins-claim (P1; direction read only).
- E5: budget echo ratio diagnostic (l91 female .2511 = the pin to compare).

## Honesty clauses

- Dynamics are P1-form (fixed per-arm drive re-applied); the substrate
  rebase IS the claim — no policy/win statement from this card.
- Raw npz checkpoint BEFORE analysis; verdict re-derivable from raw
  (crash-isolated verdict script); resume-safe partial saves.
- CPU-only (torch threads 8); no live modules, no services, sessions/ untouched.
