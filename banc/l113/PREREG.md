# L113 PREREG — cut58 mirror slice (registered 2026-11-17 00:1x, BEFORE any rollout)

Question (ideas 57): L111 showed removing the 19 glutamatergic heavy
(cut19) partially restores Ti_L (14/16, .663 — 57% of the L-restore from
22% of heavy cord out-mass) while Ti_R dies harder than cut-77 (.045 vs
.121). The mirror completes the 2x2: cut58 = closure minus the 58
NON-glutamatergic heavy (glut-19 KEPT; .3921 removed vs .1103 kept).
Is the residual L-restore mass/placement-carried (the 58 also carry it)
or glut-19-specific? And does R survive removing the 58?

## Arms (l111 machinery VERBATIM — graphs, gains, draw order)

- full  = closure (21,809), g .153125
- b65   = l65 (21,249), g .14
- cut   = closure minus heavy-77, g .14510760426521305 (re-bisected,
          asserted == l107 stored EXACT)
- cut19 = closure minus glut-19, g re-bisected deterministically and
          asserted == l111 stored .15096808075904844 EXACT (NEW anchor
          C0A(c19); same machinery + seeds 11/22/33 -> must reproduce)
- cut58 = closure minus the 58 NON-glut heavy (NEW arm; g bisected fresh
          to AF_T 0.10905611018339793, bracket [.12,.18]; staircase
          DISCLOSED, L92/L107 rule)
- cut19 retained in the arm list BECAUSE this run doubles as L114's
  second batch (below); it adds ZERO new RNG draws (noise is sliced from
  the shared nzn), so full/b65/cut/cut19 streams stay bit-identical to
  l111 on shared seeds — that IS the anchor.

## Static pins (asserted in-run; STOP+journal on any miss)

- K 77, mass_share .5024, n_new 21,809, n_cut == l107 static n_cut.
- glut count among heavy-77 == 19; non-glut == 58; n_cut58 == 21,751.
- mass_split recomputed == (.1103, .3921) EXACT (l111 stored pair).
- pool/mech/dng100 sizes == l92 pins for cut58 too.

## Seeds

- Anchors 801, 901 vs raw_l111 (l111 itself C0A-cert vs l109; one-hop,
  disclosed). All four shared arms checked (full/b65/cut/cut19).
- FRESH B10 = 1401-1416, verified ABSENT from raw_l94/raw_l107/
  raw_l109/raw_l111 file keys pre-launch (L44 #6). Sample = B10, n=16/arm.

## Registered gates (per-side duty07 Ti cells; l109/l111 rounding path
## EXACT: round per-seed to 3 then mean; k = seeds with duty >= .5;
## Wilson full-precision)

- P0 anchor: full/b65/cut/cut19 vs raw_l111 on 801+901: max|d| == 0.0
  over mm, xm, Ti{fL,fR,eL,eR}, af. MUST PASS before any read.
  Plus g_cut == stored EXACT and g_cut19 == stored EXACT.
- P1 PRIMARY (cut58 Ti_L, B10) — the mirror mass/placement test:
  * MASS/PLACEMENT-carried residual: kL >= 12 AND meanL >= .70
    (removing .3921 mass restores L at least as far as removing .1103
    did — cut19 B9 .663; the 58 hold 78% of heavy mass)
  * GLUT-ALONE (L-restore is 19-specific): kL <= 8 AND meanL <= .55
    (L stays closure-like; full B9 .407 k4)
  * between the bands = MIXED; report as such, never round up.
- P2 side action (cut58 Ti_R, B10; descriptive, PAIRED leg included
  because full-R is the known batch-drawn axis, L109):
  * R-STAYS (glut-alone R-kill stands): kR >= 8 (card's full-like band)
    OR paired leg kR_cut58 >= kR_full(B10) AND meanR_cut58 >=
    meanR_full(B10) - .10; disclose which leg fired.
  * R-KILLED-BY-58 (L111 verdict needs revision): kR <= 4 AND
    meanR <= .30.
  * else intermediate, disclosed.
- P3 ladder sanity on B10 (L109 batch-stable set): cut kL >= 12;
  b65 kL == 16 AND kR == 16; cut19 kL >= 12 (its own batch stability —
  feeds P6). full base cells NOT gated (batch-drawn, L109 disclosure).
- P4 health: af in (0.01, 0.9) every arm/seed (in-run assert);
  b65 mean-af band [.105056, .113056].
- P5 DISCLOSURE (tick-136 amendment): removed-58 .3921 vs kept-19 .1103
  cord out-mass beside the duty table; duty-form cells ONLY.
- P6 (L114 rebase read — condition met: the MIXED call rides a .037
  margin): pooled B9+B10 (n=32) cut19 Ti cells:
  * transmitter arm CONFIRMED: kL32 >= 24 AND meanL32 >= .70
  * mass/placement leg: kL32 <= 20 OR meanL32 <= .55
  * else MIXED persists (L111 verdict stands, disclosed at 2 batches).
  Per-batch k stays diagnostic (L88/L90); Wilson lb over 32 reported
  unrounded. Gates the L114 box only, not L113's.

## Non-binding expectation

cut19's L-restore at only 22% of mass removed points glut-specific; if
so cut58 stays closure-like on L (kL<=8). But L93 taught
perturbation-vs-content — MIXED is fully plausible. The gate covers all
outcomes honestly.
