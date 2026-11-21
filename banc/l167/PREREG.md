# L167 PREREG — review adjudication protocol (stage a)

Registered 2026-11-20 ~01:35 EST, BEFORE running `l167_adjudicate.py`.
Card: ideas 86 / L167 (external fable-5.2 referee report, major revision).

## Scope of this stage

Stage (a) ONLY: adjudicate the 12 major issues against OUR OWN stored
artifacts, seed response cards. Explicitly OUT of scope this tick: any
DRAFT.md edit, any numbers.json edit, any rollout, any figure redraw.
The reviewer's rewritten abstract is RAW MATERIAL, not an input to this stage.

## Verdict vocabulary (registered before any read)

- CONFIRMED — the issue is reproduced from our own artifacts (code fact,
  stored json value, or a statistic re-derived here from our stored k/n).
- REFUTED — our artifacts contradict the reviewer's claim.
- PARTIAL — the direction holds but the reviewer's attribution overreaches,
  or holds only under a narrower scope.
- REVIEWER-REPORTED — the claim requires a computation we do NOT have on
  disk. It is recorded, NOT adopted, and a reproduction card is seeded.
  A REVIEWER-REPORTED number may never enter the draft this tick.

## Evidence rule (the honesty clause for this card)

The reviewer's probe outputs in `paper/review_fable_evidence/` are treated as
CLAIMS, not evidence. Every CONFIRMED verdict must cite an artifact path under
`banc/` or `paper/` that is ours, and every statistic quoted in a CONFIRMED
verdict must be recomputed inside `l167_adjudicate.py` from our stored values.

## CERT block (asserted before any verdict is printed)

1. Our Wilson implementation reproduces the ledger's stored `pooled.cutng25`
   lb/ub to 5e-5 and l150's stored full-precision `lbR` to 1e-9.
2. Fisher self-tests: a symmetric 2x2 returns p = 1.0 exactly; a fully
   disjoint 4/0 vs 0/4 table returns its analytic value.

If any CERT assert fails the script dies and the tick reports BLOCKED.

## Registered convergence note

Reviewer issue 3 (slow line = stimulus chop) is independently confirmed by our
own L162 (evoked + echo-locked, off-arm lock collapse .979 -> .072). This
convergence was banked BEFORE the review arrived (LANE-LOG tick 188), so it is
reported as agreement, not as a new finding.
