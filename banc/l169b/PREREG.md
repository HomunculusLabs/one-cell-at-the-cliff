# L169 stage (b1) PREREG — is the f4 floor robustness FROZEN-membership or RE-DERIVED? (STATIC, zero rollouts)

Registered 2026-11-20 ~05:25 EST, BEFORE any l169b computation (lane rule;
L146/L167/L168/L169 precedent: hypotheses first, pinned numbers second).

## Why this slice exists (premise test before machinery)

L169 stage (b) as carded reads: "a floor-4 dynamic arm with RE-DERIVED
membership (our I6 showed the published robustness is frozen-membership-
only)". That premise comes from my OWN adjudication script
(`l167_adjudicate.py`), whose I6 check counts *cohort-array definition
sites* before vs inside the floor loop — a CODE-SHAPE heuristic. The same
script's run 1 already produced four verdicts with no data behind them
(disclosed in `l167/ADJUDICATION.md`), one of them an I6 regex that matched
a COMMENT and inverted the membership finding. House rule L44 (5 prior
instances, latest L157): re-derive an inherited anchor/premise from the
STORED ARTIFACTS and CODE before building machinery on it.

So stage (b) splits:
- **(b1), this card**: static premise test + the design pins a dynamic f4
  arm needs. Zero rollouts, no RNG.
- **(b2), next tick**: the f4 dynamic arm itself (fresh bisect, never a
  ported gain).

Nothing in the reviewer's report is being re-litigated on reviewer
numbers: per the L167 evidence rule, reviewer probe outputs are CLAIMS,
and every value below is recomputed under our tree.

## Registered forms (defined BEFORE measuring)

All four use the l146 convention: floors act on PAIR-LEVEL SUMMED
syn_count (post-collapse, L62 form); dn out-cord mass = sum of |log1p|
weights on out-rows into cord; the ladder is DESC by mass; K = the
smallest prefix reaching 50% of total dn out-cord mass; `ng` = the
non-glutamatergic subset of the heavy-K cohort.

- **F0 BASE** — floor 1 (= the release's effective floor 3): the stored
  base ladder. Pins: K 77, n_glut 19, n_ng 58, carrier_rank 25,
  twin_rank 26.
- **F1 FROZEN-ALL** — cohort set = base heavy-77, ORDER = base ng_desc,
  masses re-derived at floor 4. Registered as a form whose carrier/twin
  ranks CANNOT move (25 / 26 by construction); it exists to show what a
  genuinely frozen-membership f4 read would have printed. Its prefix
  masses DO move (floor denominator + surviving weights).
- **F2 FROZEN-SET, RE-ORDERED** — cohort SET frozen to the base heavy-77,
  order re-derived by f4 out-mass. Ranks free. Isolates how much of any
  rank shift is re-ordering vs cohort turnover.
- **F3 FULLY RE-DERIVED** — K, cohort membership and order all re-derived
  at floor 4. Hypothesis: this is what `l146/static.json:S4_ladder.f4`
  already contains.

## Certification block (must be GREEN before any verdict is read)

- **CERT-1**: this script is a verbatim additive transform of
  `l146_static.py`; its re-derived `out_json` must equal the STORED
  `l146/static.json` EXACTLY, key for key (L85 rule: certify the copy
  against the prior run's stored verdict before pinning anything new).
  It writes to `l169b/static_l146cert.json` — `l146/static.json` is
  NEVER rewritten.
- **CERT-2**: F1 must return carrier_rank 25 and twin_rank 26 exactly
  (the by-construction self-test; any other value means my frozen form
  is mis-implemented).
- **CERT-3**: F3 must reproduce the stored f4 field-for-field (K,
  n_glut, n_ng, jaccard_heavy, carrier_rank, twin_rank, all four
  prefix masses, closure_edges, wA_edges).
- **CODE AUDIT**: report whether the cohort arrays (`heav_f`,
  `ng_desc_f`) and `K` are assigned INSIDE the per-floor function (i.e.
  per call) in `l146_static.py`, by parsing the function body — not by a
  whole-file regex. The I6 heuristic's failure mode, if any, is a
  disclosed METHOD NOTE, never a finding.

## Registered decision rule

- **E1 REFUTED** := (stored f4 == F3 field-for-field) AND (stored f4
  carrier_rank != F1 carrier_rank) AND (stored f4 jaccard_heavy < 1).
  Then I6's frozen-membership SCOPE component is REFUTED against our own
  artifacts: the published f4 robustness already re-derives K, cohort and
  order. Fold = (a) a correction row in `l167/ADJUDICATION.md` (the review
  score becomes 11/12 confirmed + 1 scope-component refuted, the
  reviewer's floor-4 re-derived NUMBER stays REVIEWER-REPORTED and barred),
  (b) ONE scope clause in the draft's DATA FLOOR bullet stating what the
  f4 ladder re-derives and that it remains a STATIC bound (no dynamic f4
  claim), (c) stage (b2) keeps the dynamic debt.
- **E2 CONFIRMED** := stored f4 == F1 (ranks frozen). Then the draft's
  floor sentence gets the frozen-membership caveat the reviewer asked
  for, and (b2) becomes the load-bearing card.
- **E3 PARTIAL** := anything else (e.g. membership re-derived but K
  frozen, or stored matching neither form). Disclose both sides and label
  which way the evidence leans.
- The abstract is NOT touched under any branch (v3.8 vocabulary freeze,
  `l158_verify.py`). No new rollout numbers enter the draft from this card.

## Design pins for (b2) — DESCRIPTIVE, no claims

Registered as measurements a dynamic f4 arm needs, with no hypothesis
attached (L134 law: statics bound deletions, they do not predict
dynamics):

- P1 carrier footprint at f4 by tier: out80 / out_int70 / out_mot10 /
  in13 survivors (stored json has f2/f3 survivors and out80_f4 only).
- P2 cohort turnover: which base-heavy cells leave the f4 cohort and
  which enter; the ng-side set difference.
- P3 window portability: |base ng_desc[:24] ∩ f4 ng_desc_f[:24]| — the
  wA cut window is a POSITIONAL prefix, so a dynamic f4 arm cuts a
  different cell set unless this overlap is 24.
- P4 twin design at f4: the carrier's mass-nearest ng neighbour under f4
  and the mass gap, because the base twin (319) sits at f4 rank 33 — the
  carrier-vs-twin XOR design does not port unmodified.
- P5 the f4 graph's edge budget (closure, wA window) and the explicit
  note that a dynamic f4 arm requires a FRESH af-matched bisect on the
  f4 graph (L118-L131 criteria verbatim; never port a gain).
