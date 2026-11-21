# L111 PREREG — glutamate-subset ladder slice (registered 2026-11-16 22:5x, BEFORE any rollout)

Question (ideas 56, from L110's addendum): the closure subnet's Ti_L kill
(L107/L109: cut-77 restores L, collapses R) — is it TRANSMITTER-carried (the
19 glutamatergic cells of the heavy-77; l110: glut-enriched 19/77, z +5.9,
heavy->Ti_fL signed 2-hop mass +1821 = 4.6x light) or MASS/PLACEMENT-carried
(the heavy mass as such, transmitter irrelevant)?

## Arms (l107/l109 machinery VERBATIM — graphs, stored gains, draw order)

- full  = closure (21,809), g .153125
- b65   = l65 (21,249), g .14
- cut   = closure minus heavy-77 (l107 stored g .14510760426521305;
          re-bisected here and asserted == stored EXACT)
- cut19 = closure minus the 19 GLUTAMATERGIC cells of the heavy-77 (NEW arm;
          g bisected fresh to AF_T 0.10905611018339793, bracket [.12,.18];
          |af_final - target| staircase DISCLOSED, L92/L107 rule)
- h65 dropped (gain-innocessce settled 32/32 twice: l107 B4, l109 B7+B8).

## Static pins (asserted in-run; STOP+journal on any miss)

- K 77, mass_share .5024, n_new 21,809, n_cut == l107 static n_cut.
- glut count among cut_drop == 19 (l110 addendum). != 19 -> STOP.
- n_cut19 == 21,790; pool/mech/dng100 sizes == l92 pins for cut19 too.

## Seeds

- Anchors 801, 901 vs raw_l109 (l109 was itself C0A-certified vs l94/l107;
  one-hop anchor, disclosed).
- FRESH B9 = 1301-1316, verified ABSENT from raw_l94/raw_l107/raw_l109 file
  keys pre-launch (L44 #6). Sample = B9 only, n=16/arm.
- RNG: l109 draw order verbatim; cut19 adds ZERO new draws -> full/b65/cut
  streams must be bit-identical to l109 on shared seeds (this IS the anchor).

## Registered gates (per-side duty07 Ti cells; l109 rounding path EXACT:
## round per-seed to 3 then mean; k = seeds with duty >= .5; Wilson full-
## precision over n=16)

- P0 anchor: full/b65/cut vs raw_l109 on 801+901: max|d| == 0.0 over
  mm, xm, Ti{fL,fR,eL,eR}, af. MUST PASS before any read.
- P1 PRIMARY (cut19 Ti_L, B9) — the transmitter test:
  * TRANSMITTER-carried: kL >= 12/16 AND meanL >= .70
    (left restores toward cut's .836-.870)
  * MASS/PLACEMENT-carried: kL <= 8/16 AND meanL <= .55
    (left stays closure-like .367-.395)
  * between the bands = MIXED; report as such, never round up.
- P2 side action (cut19 Ti_R, B9; pre-registered bands, descriptive):
  * R-collapses-too: kR <= 4  -> the 19 carry BOTH side actions
  * R-stays-closure-like: kR >= 8 -> side actions dissociate by transmitter
- P3 ladder sanity on B9 (structure cells must replicate; L109 batch-stable
  set): cut kL >= 12; b65 kL == 16 AND kR == 16. full base cells NOT gated
  (batch-drawn axis, L109 disclosure).
- P4 health: af in (0.01, 0.9) every arm/seed; b65 mean-af band
  [.105056, .113056].
- P5 DISCLOSURE (tick-136 amendment, 2611.14498 LERS lesson): beside the
  duty table, the cord out-mass share of the removed 19 vs the kept 58 heavy
  cells (they sum to .5024 of dn_new cord out-mass); per-window normalized
  cells (duty form) ONLY — never raw mass across arms.

## Non-binding expectation

The l110 mirror signature points glut-left; but if the 19 carry little of
the heavy mass, MIXED or mass-carried is fully plausible (L93 taught
perturbation-vs-content). The gate covers all three outcomes honestly.
