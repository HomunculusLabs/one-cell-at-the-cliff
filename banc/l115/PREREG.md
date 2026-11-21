# L115 PREREG — random-19-subset flip control (registered 2026-11-17 01:3x, BEFORE any rollout)

Question (ideas 58): L113 showed EITHER half of the heavy-77 alone (glut-19,
.1103 cord out-mass; non-glut-58, .3921) produces the FULL cut phenotype on
B10 (L restored kL 15-16 / meanL .696-.790; R dead kR 0 / meanR .026-.207).
If that flip is a pure MASS/THRESHOLD mechanism, a RANDOM 19-of-77 (expected
removed mass ~.124, hypergeometric) should flip too. If WHICH-19 matters,
random draws fail to restore L (stay in the full band: B9 k4 .407 / B10
k5 .402) and the glut-19 keep per-mass specificity.

## Arms (l113 machinery VERBATIM — graphs, gains, draw order)

- full, b65, cut, cut19 — bit-identity anchors vs raw_l113 on 801/901;
  g_cut re-bisected + asserted == l107 stored .14510760426521305 EXACT;
  g_cut19 re-bisected + asserted == l111 stored .15096808075904844 EXACT.
- cutR1, cutR2, cutR3 = closure minus RANDOM 19-of-heavy-77 subsets.
  Draw rule (pinned): numpy default_rng(1150), three successive
  rng.choice(77, size=19, replace=False) picks, POSITIONAL on heav
  (the mass-desc-order heavy array); drops = np.sort(heav[pick]);
  draws asserted distinct. numpy RNG is DISJOINT from the torch
  settle/noise generators -> zero impact on any other arm's stream.
  g for each cutR bisected FRESH to AF_T .10905611018339793
  (staircase disclosed per L92/L107).
- cut58 arm DROPPED (settled on B10; l111 precedent for dropping settled arms).

## Static pins (asserted in-run; STOP+journal on any miss)

- K 77, mass_share .5024, n_new 21,809, n_cut == l107 static, glut19 == 19,
  mass_split == (.1103, .3921) EXACT.
- Each n_cutRi == 21,790 (= n_new - 19); draws pairwise distinct.
- DNg100 NOT in heavy-77 (pre-verified pre-launch this tick: 2 cells,
  0 overlap; asserted in-run STOP if violated) -> no random draw can
  touch the DNg100 drive channel.
- Per-draw removed mass (of heavy cord out-mass) + glut count disclosed.

## Seeds

- Anchors 801, 901 vs raw_l113 (l113 itself C0A-cert vs l111; one-hop,
  disclosed). All four shared arms checked (full/b65/cut/cut19).
- FRESH B11 = 1501-1516, verified ABSENT from raw_l94/raw_l107/raw_l109/
  raw_l111/raw_l113 keys pre-launch (L44 #6). Sample = B11, n=16/arm.

## Registered gates (per-side duty07 Ti cells; l109/l111/l113 rounding path
## EXACT: round per-seed to 3 then mean; k = seeds with duty >= .5;
## Wilson full-precision)

- P0 anchor: full/b65/cut/cut19 vs raw_l113 on 801+901: max|d| == 0.0
  over mm, xm, Ti{fL,fR,eL,eR}, af. MUST PASS before any read.
  Plus g_cut == stored EXACT and g_cut19 == stored EXACT.
- P1 PRIMARY (random-flip test, per draw arm d on B11):
  * FLIP (mass/threshold phenotype): kL_d >= 12 AND meanL_d >= .70
    AND kR_d <= 4 (the cut19/cut58 envelope: L at cut level, R dead).
  * NO-FLIP (subset-class specificity): kL_d <= 8 OR meanL_d <= .55
    (L stays in the full/closure band).
  * else MIXED for that draw (incl. L-restored-but-R-alive partials —
    disclosed via P2).
  AGGREGATE: MASS/THRESHOLD LAW if >= 2/3 draws FLIP;
  SUBSET-CLASS-SPECIFIC if 0/3 FLIP AND >= 2/3 NO-FLIP; else MIXED.
  Per-draw removed-mass vs kL read is DESCRIPTIVE (n=3, no rank gate —
  L95 tie-degenerate rule).
- P2 R-side (descriptive + paired, batch-drawn axis disclosed, L109):
  kR_d vs full-B11 kR; paired leg (kR_d >= kR_full AND meanR_d >=
  meanR_full - .10) reported per draw.
- P3 ladder sanity on B11 (L109 batch-stable set): cut kL >= 12;
  b65 kL == 16 AND kR == 16; cut19 kL >= 12.
- P4 health: af in (0.01, 0.9) every arm/seed (in-run assert);
  b65 mean-af band [.105056, .113056]; cutR staircases disclosed.
- P5 DISCLOSURE (tick-136 amendment): per-draw removed mass, glut count,
  and cell overlap with the glut-19 set, beside the duty table;
  duty-form cells ONLY.
- P6 DIAGNOSTIC ONLY (gates nothing; L114 box already closed MIXED):
  pooled cut19 B9+B10+B11 (n=48) kL/meanL/Wilson — third batch for the
  pooled-48 table. Per-batch k stays diagnostic (L88/L90).

## Non-binding expectation

L113's redundancy (either half alone) predicts >= 2/3 random-19 FLIP —
a pure mass/threshold attractor flip at this granularity. If they fail,
the specific heavy placements (not transmitter class alone — L113 already
dissolved that) carry per-mass specificity. MIXED fully plausible (L93).

## ADDENDUM 1 (registered 2026-11-17 01:5x, BEFORE the rerun; attempt 1
## aborted IN BISECT with zero rollouts run)

cutR3's bracket af(0.18) = 0.10724 < AF_T .109056: the inherited [.12,.18]
bracket (l113) does not contain the target for this random subnet. The
fresh-bisect bracket for the three RANDOM arms widens to [.12,.32]; the
cut and cut19 re-bisect asserts are untouched (both already passed ==
stored EXACT on attempt 1 and are deterministic). Consequence disclosed:
all three random-arm gains re-bisect from the wider interval, so R1/R2
gains differ from attempt 1's printout (.168290/.152681 — void, never
used). No rollout consumed RNG before the abort; raw_partial absent;
the rerun is a clean restart. Descriptive note: cutR3 needing g > .18
(the highest gain in the lineage) is itself a subnet-stiffness read,
disclosed in P4.
