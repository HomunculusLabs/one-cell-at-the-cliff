# L146 PREREG — synapse-floor robustness of the identity cliff (STATIC, zero rollouts)

Registered 2026-11-19 ~01:45 EST, BEFORE any L146 computation (lane rule;
L160/L137 precedent: hypotheses first, pinned numbers second).

## Motivation

Kopel et al. 2611.23320 (digested tick 167): their preregistered 5-criterion
BANC compartment test holds ONLY when single-synapse connections are counted
(C2/C3 fail at a 2-3-synapse floor), traced to BANC's 22% identified-neuron
attachment rate — field evidence that single-synapse edges are LOAD-BEARING
in BANC. Our banc_graph (v626) was built with NO min-synapse filter (the L62
"fidelity knob" left permissive). The identity cliff's carrier
(1110/DNp33-L, ladder mass .0064, 80 out-edges / 13 in-edges) is exactly
the weak-edge class a floor deletes.

## Conventions (registered BEFORE measuring)

- The graph collapses per-NEUROPIL rows by SUMMING syn_count per
  (pre,post) pair (L62 identity check: 2,676,592 unique pairs). A FLOOR
  therefore acts on the PAIR-LEVEL SUMMED count (post-collapse), NOT on
  per-neuropil rows. Disclosed as OUR convention; Kopel's floor is on
  connections. Secondary descriptor only: the pre-collapse per-ROW
  syn distribution.
- FLOOR ARMS: f2 = keep pairs with summed syn_count >= 2 (delete ==1);
  f3 = keep >= 3 (delete <=2). No other floors this card.
- Graph vals are log1p(summed_syn) * sign, so a floor changes BOTH edge
  existence AND surviving edge weights only through re-derivation of the
  ladder (weights of surviving pairs are unchanged; masses renormalize
  against the floor-filtered dn out-cord total).

## S0 pin block (must be GREEN before any L146 number)

Re-pin the base table EXACT, asserts lifted verbatim from
l145_static.py / l131 pins: closure counts (n_old/n_new/dn_new == l92
static.json), cut K/mass_share + n_cut (l107), glut19/other58 split
{0.1103, 0.3921} + ng58 == cut58 set, rank twins ng_desc[24]==1110 and
ng_desc[25]==319, ladder mass/edge pins cutk5 .0425/647252, ng19
.1946/644729, ng23 .222/644282, wA .2286/644177, ng25 .235/644084,
ng25p .2346/644072, ng26 .2411/643979, ng29 .2588/643623, k58 edges ==
cut58 arm, carrier edge counts out=80 (int 70 / mot 10) / in=13, and the
10 motor-edge syn values == l145/static.json motor_edges_ranked EXACT.

## Census (deterministic, no RNG, zero rollouts)

- S1 SUBSTRATE: summed-syn histogram of (a) all in-graph pairs,
  (b) closure (keep_new) edges, (c) wA-window edges. Report share at
  ==1, ==2, >=3 and edges deleted by f2/f3. Secondary: per-ROW shares.
- S2 NG-58 COHORT: in-closure out-edge and in-edge summed-syn histograms
  for the 58 non-glut heavy cells; per-cell share of edges at ==1.
- S3 CARRIER FOOTPRINT: summed-syn distribution of 1110's 80 out
  (70 intrinsic / 10 motor) + 13 in edges; counts surviving f2/f3.
- S4 LADDER RE-DERIVATION under f2/f3 (the load-bearing read): recompute
  per-dn_new out-cord mass from floor-filtered pairs; report new K (50%
  share), heavy-K membership Jaccard vs base heavy-77, glut/ng split
  counts, ng rank of 1110 and of 319, re-derived ladder mass_removed for
  k19/k25/wA/k29 forms, and wA-window surviving edge counts.

## Registered decision rule (from the card, made numeric)

- D1 SURVIVES := under f2: 1110 in the new heavy-K non-glut cohort AND
  >= 60% of its 80 out-edges survive AND 319 also in-cohort. Then floor
  arms are REGISTERED as a follow-up run card (fresh bisects, criteria
  VERBATIM L118-L131, never port gains un-bisected) — static table ships
  this tick; the run is a new card, not this one.
- D2 BREAKS := either floor removes 1110 from the cohort, reorders the
  carrier/twin identity pair, or deletes >= 40% of the carrier's
  out-edges. Then the measured disclosure IS the result: preprint
  robustness/limitation amendment + a number for the L62 note; no arms.
- D3 PARTIAL (anything else): disclose both, queue the decision to the
  paper fold (L149-class), label which side the evidence leans.
- Statics BOUND what a floor deletes; they make NO dynamic claim (L134
  law: statics could not predict the carrier forward; here they bound a
  deletion backward — different direction, still static).

## ADDENDUM A (registered 2026-11-19 ~02:0x, BEFORE computing f4)

The registered f2/f3 arms ran and came out VACUOUS-BY-RELEASE (L55
degenerate-arm class, disclosed): the v626 connections release contains
2,676,592 unique pairs and EVERY pair sums to >= 3 (811,821 exactly at 3;
574,733 single-synapse ROWS exist but only as intra-pair breakdowns —
462,170 pairs contain a 1-syn row yet still sum >= 3). f2/f3 delete
nothing anywhere; D1's "survives" is vacuous in the strong sense and is
NOT read as a robustness pass.

- A1: f4 (keep summed >= 4) is the FIRST informative floor on this data;
  it deletes the 811,821 at-3 pairs (~30.3% of the release). Register:
  S4 ladder re-derivation under f4 (K, glut/ng split, Jaccard, carrier +
  twin rank, prefix masses, closure/wA surviving edges) + exactly-at-3
  counts (eq3) for closure, ng-58 out/in, carrier out80/int70/in13.
- A2 (registered verdict frame): D4a := carrier stays in heavy-K ng cohort
  with its rank window (rank within 19..29) under f4 AND >= 60% of its 80
  edges survive -> robustness extends to the strongest admissible floor
  (disclosed as data-floor-bounded, not a Kopel answer). D4b := carrier
  drops from cohort OR < 60% edges -> the measured limitation IS the
  result: the identity cliff is contingent on the release's implicit
  floor-3; preprint limitation line + L62 note number. D4c anything else:
  disclose both sides.
- No dynamic arms either way (statics bound deletions; a dynamic f4 run
  would be a new card only if the owner asks).

