# L229 PREREG — the NEAR-BALANCE hypothesis, asked as a POPULATION question

Registered 2026-11-23 ~22:35 EST (tick 261), BEFORE the generated script
existed and BEFORE any L229 quantity was measured. Static. ZERO rollouts,
zero settles, zero new dynamics: every dynamic number is read from the
stored npz (l150 / l169b2 / l175f), opened READ-ONLY and fingerprinted.

## The claim under test

L215's most suggestive unplanned number: the Tr pool-sides sit at inhibitory
fraction .4943 / .4965 while Ti sits at .4555 / .4511 — Tr is the
near-balanced joint and Tr is the joint with the dead side. Near-balance is
the regime where a small network change flips a pool between dead and alive,
so the hypothesis is **balance predicts lability**. The selected-pool version
of that claim is unfalsifiable; this card asks it NONSELECTIVELY over all ten
cord pool-sides (Ti, Tr, Ta, Sr, Pr x L/R) — Kriegeskorte 2009 step (1).

## PREMISE CORRECTIONS, written before the script exists

**(0a) THE HYPOTHESIS'S QUANTITY IS NEARNESS-TO-BALANCE, NOT inh_frac.**
`inh_frac = Mm/(Mp+Mm)` is monotone in nearness ONLY while every pool-side
sits BELOW 0.5. L215 observed four values, all below; the six unobserved
pool-sides are not guaranteed to be. The registered primary currency is
therefore `near = -|inh_frac - 0.5|` (larger = more balanced), with raw
`inh_frac` reported beside it, and the count of pool-sides with
inh_frac > 0.5 MEASURED and printed. If that count is 0 the two currencies
are rank-identical by construction and the distinction costs nothing; if it
is > 0 the branch is read on `near` and the raw reading is reported as the
L218/L227 currency companion. (A currency must be registered before it is
measured, and a share/index statistic's currency can flip its sign.)

**(0b) THE SUBSTRATE THAT DEFINES inh_frac MUST BE NAMED.** L215 computed
inh_frac on two substrates (cutwA, f4wA). The dynamic arms span BOTH. The
registered primary is **cutwA** — the base unfloored wA substrate, which is
the graph all three batches' `cutwA` arm actually ran on and the one whose
pool sizes are pinned invariant. f4wA is the registered robustness companion
and the two must agree in branch; a disagreement is itself the finding.

**(0c) DYNAMIC RANGE IS NON-MONOTONE IN LEVEL AND THE CEILING IS REAL.**
`max lvl - min lvl over arms` is small both when a pool-side is DEAD at the
tonic floor in every arm and when it is SATURATED at RMAX in every arm (L208:
at a sparse operating point, margin-from-ceiling and aliveness are the same
number with opposite meanings; L260: brain.py is relu + clamp(max=RMAX=1.0),
so local gain is 0 at the ceiling). Registered BEFORE measuring: report per
pool-side the mean level over arms, the pooled-mean ceiling fraction
(`fhi95`), and the floor fraction (`flo`), and register the degeneracy
escape **B_FLOOR_DEGENERATE** — if any pool-side's max level over all arms is
below BG + 2*NOISE = 0.04, its range is a dead-pool artifact and it is
reported separately from the correlation rather than silently ranked.

**(0d) THE THREE BATCHES HAVE DIFFERENT ARM MENUS AND DIFFERENT SEEDS.**
l150 carries 7 arms, l169b2 and l175f carry 12 (the same 12). A range is a
max-minus-min over a MENU, so a range computed over 7 arms and one computed
over 12 are not the same statistic (the L220 law: when the menu size changes,
a bare difference is not the effect). Registered: PRIMARY = B36 (l169b2,
12 arms, seeds 3449-3464), REPLICATION = B37 (l175f, same 12 arms, fresh
seeds 3701-3716), MENU COMPANION = B35 (l150, 7 arms, seeds 3365-3380).
The branch is read on the PRIMARY; B37 is the seed-level replication and B35
is reported as a different-menu reading, never pooled with them.

**(0e) THE SIZE CONFOUND MUST BE MEASURED, NOT ASSUMED AWAY.** The six
unobserved pool-sides are 7-19 cells (Pr 7/7, Ta 15/15, Sr 17/19) against
Ti/Tr's 55-57 — a 8x size span. Both quantities can depend on size: inh_frac
is a ratio over fewer in-edges, and a pool-MEAN trace over 7 cells is noisier
than over 56. Registered confound legs: Spearman(near, n_cells),
Spearman(near, TOT in-mass), Spearman(range, n_cells), Spearman(range,
TOT), plus the registered escape **B_CONFOUNDED** below.

**(0f) TIES AND RANK CONVENTION.** All rank correlations are MIDRANK
(average-rank) Spearman, never argsort-of-argsort (L221: argsort-of-argsort
is input-order dependent and a tie convention can refute a true identity).
The number of DISTINCT values in each ranked vector is measured and printed;
if any vector has fewer than 10 distinct values the tie structure is reported
with the statistic.

**(0g) THE NULL IS EXACTLY ENUMERABLE AT n=10 AND THEREFORE HAS NO
RESOLUTION FLOOR.** 10! = 3,628,800 label assignments. The membership
permutation null the card asks for is computed by EXACT ENUMERATION over all
3,628,800 permutations of the pool-side labels, so the p-value is exact and
the L225 resolution-floor problem does not arise. Minimum attainable
two-sided p = 2/3,628,800.

**(0h) OBSERVATION STATUS (Kriegeskorte 2009 / the L214 rule).** While
scoping I read: L215's stored `inh_frac` for all four Ti/Tr pool-sides on
both substrates (.4555/.4511/.4943/.4965 cutwA), and l208's stored `lvlL`/
`lvlR` for Ti on three of the five ARMS5 arms in B36. Those are DESCRIPTION,
declared here in advance. Every registered branch sits on quantities nobody
has computed: the six Ta/Sr/Pr inh_frac values, all ten 12-arm dynamic
ranges, and the n=10 rank correlation itself. I have NOT read any Ta/Sr/Pr
inh_frac, any pool-side range, or any correlation between them.

**(0i) n=10 IS UNDERPOWERED BY CONSTRUCTION AND A NULL IS UNINFORMATIVE.**
Per the card's own instruction, the registered object is an EFFECT-SIZE BAND,
not a significance bar. At n=10 a midrank Spearman of +0.70 is roughly the
two-sided .025 point; |rho| < 0.40 at n=10 cannot distinguish a real small
effect from nothing. A null therefore scores **B_UNINFORMATIVE**, NOT
"refuted" — and that is registered here so the verdict cannot be written as a
refutation after the fact.

## REGISTERED BRANCHES (exactly one fires; checked in this order)

1. **B_FLOOR_DEGENERATE** — any pool-side has max-over-arms level < 0.04
   (0c). The correlation is still reported, but on the surviving pool-sides
   AND on all ten, and the branch records that the population is not ten
   comparable units. SHORT-CIRCUITS the "population answer" claim (L222: a
   registered escape must change control flow, not just be a flag).
2. **B_CONFOUNDED** — |Spearman(near, n_cells)| >= 0.70 or
   |Spearman(near, TOT)| >= 0.70. Then whatever the primary reads is a size
   or mass statistic wearing balance's clothes and must be reported as such.
3. **B_BALANCE_PREDICTS** — rho(near, range) on the PRIMARY >= +0.70 AND
   rho on B37 has the SAME SIGN AND rho on B35 has the same sign.
4. **B_SUGGESTIVE** — primary rho >= +0.40 (but < 0.70) or (primary >= +0.70
   with a companion sign disagreement). Names what a second batch would buy.
5. **B_INVERTS** — primary rho <= -0.40. The hypothesis is backwards:
   balance would predict STABILITY.
6. **B_UNINFORMATIVE** — |primary rho| < 0.40 (0i).

## REGISTERED PREDICTIONS (scored as written, pass or fail)

- **P1**: all ten pool-sides have inh_frac < 0.5, so `near` and `inh_frac`
  are rank-identical (0a) and the currency distinction costs nothing.
- **P2**: rho(near, range) on the primary is POSITIVE (any magnitude).
- **P3**: Tr_L and Tr_R are the two most-balanced of the ten pool-sides
  (i.e. `near` ranks 9 and 10 of 10) — the selected-pool observation
  generalises to a population ranking.
- **P4**: the primary branch is NOT B_BALANCE_PREDICTS — at n=10 with a
  mass/size span of 8x I expect B_SUGGESTIVE or B_UNINFORMATIVE. Registering
  the modest expectation in advance is the point.
- **P5**: the three batches agree in SIGN on rho(near, range).
- **P6**: at least one pool-side fires B_FLOOR_DEGENERATE's condition
  (max level < 0.04) — I expect at least one of the small Pr/Sr/Ta
  pool-sides to be dead in every arm.

## CERTIFICATION PLAN (halting gates, before any L229 number is read)

- **Inherited verbatim slices, sha-pinned, never imported (L175):**
  HEAD1 = l151_static.py lines 1-319 (graph, POOL_G, keeps, pool-size pins
  for all 20 pools via S92 + S101); PRE = l215's hand-written `o = {...}`
  line (HEAD2 writes into it); HEAD2 = l178_tail.py lines 22-83 (the f4
  ladder, pm4/keep_f4/emask_f4, the stored-gain leg); HEAD3 = l215_tail.py
  lines 1-163 (CERT-G / CERT-205 / CERT-TBL / the substrate pins / SIDEMASK
  for Ti,Tr / the certified `signed_in`); HEAD4 = l169b2_verdict.py lines
  13-63 (the certified npz helper atom: WIN/SEGB/MEAS0/PAIRS/PREF/s_arrays/
  duty_seeds/side_k). Every inherited sha asserted by the BUILDER against the
  value the parent's own generated banner recorded. HEAD3's cut lines are
  audited STRUCTURALLY (line-set + ownership of `ROWS = {}` / `json.dump`),
  never by a bare token scan (the tick-248/251/256/257/258 trap). An AST
  Import/ImportFrom walk proves no lab module is imported; an AST Call walk
  proves the generated script contains EXACTLY ONE write (l229/static.json).
- **CERT-215R (halting)**: re-run L215's own ROWS loop for Ti/Tr on both
  substrates with the inherited `signed_in` and assert every stored
  l215/static.json rows field at FLOAT EQUALITY. This is what licenses
  extending inh_frac to six new pool-sides.
- **CERT-208L (halting)**: reproduce l208/static.json `arms[*]` lvlL, lvlR,
  fhi95L/R, floL/R for both joints x ARMS5 x B36,B37 at FLOAT EQUALITY from
  my own window rebuild, plus the window pins |W| == 3000. This is what
  licenses reading `lvl` for six new pool-sides and twelve arms.
- **CERT-W (halting)**: the window/segment/constant literals asserted present
  in l169b2_run.py's TEXT (l208's CERT-CONST pattern, read as text).
- md5sum -c l229/prior.md5 GREEN before AND after; (size, mtime_ns)
  fingerprints on every npz and prior json asserted unchanged after the run.

## LIMITS DECLARED IN ADVANCE

One connectome (BANC v626 female cord), one operating-point family, pool
MEANS only (the per-cell ceiling fraction is not recoverable from stored
traces — l208's own declared limit), ten units, and the six new pool-sides
are 7-19 cells. inh_frac is an ANATOMICAL in-mass ratio under the log1p
ladder convention, not a measured E/I current balance. This card cannot
establish causality in either direction: a correlation between balance and
lability over ten pool-sides is a population DESCRIPTION with a null, and the
registered band is what would justify spending a second batch.
