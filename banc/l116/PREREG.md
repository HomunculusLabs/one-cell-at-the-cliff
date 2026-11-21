# L116 PREREG — flip-joint-scan (registered 2026-11-17 03:0x, BEFORE any rollout)

Question (ideas 58 card): cut58 (closure minus the 58 NON-glut heavy)
flips Ti — L restored (.790 16/16) while R dies (.207 0/16) — but leaves
Tr_R alive (5/16 .472). Is that side-flip pattern Ti-specific or
joint-heterogeneous across the WHOLE semantic antagonist vocabulary
(Ti, Tr, Ta, Sr, Pr from peripheral_target_type, L101 form)?

## Design (l113 machinery VERBATIM — graphs, gains, draw order, arms)

- All 5 arms retained (full/b65/cut/cut19/cut58) — NOT fresh rollouts of
  a new design: this is a REPLICATION-FORM EXTENSION readout of l113's own
  B10 trajectories with the pool set extended from 2 pairs (Ti/Tr, f/e
  naming) to 5 pairs (Ta/Sr/Pr NEW in l101 a/b naming; Ti/Tr keep f/e
  names so C0A keys match). Disclosed: B10 1401-1416 is l113's OWN batch —
  the Ta/Sr/Pr reads are new pool extractions of the SAME trajectories,
  not an independent batch; Ti/Tr columns must come out bit-identical
  (that is the anchor, not a finding).
- Gains: g_cut + g_cut19 re-bisected, asserted == stored EXACT (l107/l111
  values); g_cut58 re-bisected, asserted == l113 stored
  0.15417299151420596 EXACT (NEW C0A(c58) deterministic-anchor class).
- Pool extension (l101/l101_run.py patterns VERBATIM): Ta = tarsus
  depressor(agonist)/levator; Sr = sternal anterior/posterior rotator;
  Pr = promotor(agonist)/remotor. Sizes pinned from l101/static.json:
  Ta 12/12/3/3, Sr 6/6/11/13, Pr 4/4/3/3 (aL/aR/bL/bR); Ti/Tr a/b sizes
  cross-checked == l92 f/e sizes (50/51/6/6, 31/31/24/24) — catches any
  extraction drift between l101 and l113 forms.
- Small-pool disclosure (registered in advance): Ta_b/Sr_a/Pr pools hold
  3-13 cells/side; S on a 3-cell pool mean is noisy — duty reads there
  carry wide seed spread and NO gate may rest on them alone.

## Static pins (asserted in-run; STOP+journal on any miss)

- All l113 pins unchanged (K 77, mass .5024, n_new 21,809, n_cut58 21,751,
  glut 19/non-glut 58, mass_split (.1103, .3921), mech/dng100 sizes).
- NEW: 12 new pool sizes == l101/static.json, all arms (drops are DNs;
  motor cells never dropped — sizes identical across arms).

## Registered anchors (MUST PASS before any new read)

- P0/C0A FULL-BATCH: every stored key of l113's schema (mm, xm,
  Ti{fL,fR,eL,eR}, Tr{...}, af) over ALL 18 seeds (801, 901, 1401-1416)
  x ALL 5 arms == raw_l113.npz EXACT, max|d| == 0.0. (Strongest chain
  anchor yet — first full-batch one; 46th consecutive.)
- C0B certification BEFORE any new pin: the pair-generalized verdict
  machinery (SIGS param a/b vs f/e) run on STORED raw_l113.npz must
  reproduce results_l113.json table_b10 + tr_b10 for ALL 5 arms, every
  pinned read EXACT (kL/kR/meanL/meanR; l109/l113 rounding path: round
  per-seed to 3, then mean; k = duty >= .5).
- C1 health: 0.01 < af < 0.9 every arm/seed; b65 af-mean band
  [.105056, .113056].

## Registered read (descriptive; primary table = 5 pairs x 5 arms x sides)

- Per pair P, per side: duty07 mean + k (B10, n=16, same 0.7-seg
  windows/rounding as l113). Base (full-arm) EXPECTATION bands from
  l101's 51-seed distribution (registered so surprises are visible):
  Ti L~.38/R~.43-.49, Tr L~.03-.05/R~.37-.42, Ta L~.34-.36/R~.01
  (INVERTED), Sr L~.14/R~.39-.43, Pr both ~0-.11 (floor).
- Registered flip classification per pair (cut58 vs full, B10):
  * FLIP-L:  meanL(cut58) - meanL(full) >= +.20
  * KILL-R:  meanR(cut58) - meanR(full) <= -.20
  * pair classes: "Ti-like flip" (FLIP-L + KILL-R), "L-only" (FLIP-L,
    R within ±.20), "R-spared" (explicit naming for the Tr pattern:
    FLIP-L with R >= full - .10), "no-flip" (neither), "inverted" (any
    R-side restoration on the Ta pattern). Reported per pair; NO pooled
    both-sides cell decides anything (L109 per-side rule).
- Registered expectation (falsifiable): if the flip is a generic
  attractor-lottery response of driven-joint pools, pairs with base
  structure on a side (Tr_R, Sr_R, Ta_L) should MOVE on that side under
  cut58; if the kill is Ti-wiring-specific, only Ti moves. Ta_L is the
  sharpest test (the one L-dominant base side outside Ti).
- Honesty clause: Pr is registered as expected-floor (no structure to
  flip); a Pr "no-flip" is a floor artifact, never evidence of
  specificity.
