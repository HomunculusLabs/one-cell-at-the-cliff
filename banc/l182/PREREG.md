# PREREG — L182: the pooled-count DRIFT GATE (meta, ZERO rollouts)

Written BEFORE any gate output is read. No rollouts, no graph build, no
torch, no RNG. The only inputs are stored artifacts: `banc/l172/stats.json`
(the canonical pooled table L172 stage (a) produced) and the live
`paper/DRAFT.md`. The live draft is READ-ONLY in this run; every tamper
test runs on a COPY under `banc/l182/`.

Card (LANE.md L182): "The defect L172 fixed was not a wrong number but two
unions of the same arm in two sections. Add a verifier section that
extracts every `k/n` token from the draft body, resolves it to an arm via
l172.pooled, and FAILS if any arm appears with two different denominators
outside an explicitly whitelisted family-matched table."
Verify: "the gate fails on a deliberately re-introduced per-batch cell,
then passes on the current draft."

## Why this card before L181 (registered interpretation)

L181 is the FIRST unchecked item by line order and it is deliberately not
taken by this cron tick: its deliverable lands numbers in `paper/DRAFT.md`,
and the draft is in the owner-handoff state (mtime 18:55, sha c32a7d186642,
the in-session residue-fold child landed at 19:0x). The ticks-217/218
non-draft rule for cron ticks still holds. L182 is also the INSTRUMENT that
would verify L181's propagation, so building the gate first is the right
dependency order rather than a dodge.

## The classifier (fixed here, derived from the data, not tuned)

CANON_N = the 15 `n` values in `l172.pooled`. Measured property asserted by
the gate itself: no canonical n is a multiple of 16 (13 of 15 are
`16*batches + 2`, the two extra being the forward-chain anchor seeds; the
two closure arms are 513). Batch size is 16, so the per-batch unions L172
replaced are exactly the multiples of 16.

- BATCHMULT = {16, 32, ..., 160} (one to ten batches).
- A `k/n` token is SEED-FORM iff its denominator is in CANON_N or
  BATCHMULT. Every other denominator (census counts, cell counts, DOIs,
  dates, 0/240 scan columns, 361/500, 38/49 ...) is IGNORED and its
  multiset is REPORTED, never judged. The 160 cap is registered precisely
  so the §2.1 scan column `/240` is outside the classifier.

## Scope

Body = from the `## Title` line to the `## References` line, exclusive.
The changelog banner above `## Title`, the reference list and the trailing
`## Verification` block are OUT of scope and that is asserted.

## Resolution rule (registered BEFORE measurement)

ARM_PHRASES: arm -> regexes, built from §2.14's own table (code name in
backticks plus its parenthetical reader label) and the prose aliases the
body uses. Each arm's phrase set must match at least one body site or the
gate fails (a stale phrase may not silently cover nothing).

UNIT = the markdown table row if the line starts with `|`, else the
sentence. Within a unit, if the number of arm-phrase hits equals the number
of SEED-FORM tokens, they are paired IN ORDER (i-th phrase to i-th token).
Any other count is UNRESOLVED and reported. Order-pairing is registered
because both table shapes need it: §2.14 is `| arm | k/n | ...` (1 and 1)
and the contrast table is `| A - B | kA/nA vs kB/nB |` (2 and 2), where a
nearest-preceding rule would mis-assign the first token.

## Gate cells (one object per cell; L109 rule, and L180's own lesson)

- D1 PRIMARY: no arm resolves to two DIFFERENT CANON_N denominators.
- D2 PRIMARY: every resolved CANON_N denominator equals that arm's own
  canonical n.
- D3 SECONDARY: every resolved BATCHMULT denominator is covered by a
  declared EXEMPT region (a family-matched table, keyed by its heading) and
  that arm's canonical count also appears in the body (the reconciliation
  requirement). Each exemption must be non-vacuous.
- D4 WELL-POSEDNESS: CANON_N disjoint from BATCHMULT; every arm phrase set
  non-vacuous; scope boundaries present.
- T TAMPER: three deliberate defects on a COPY of the draft, each required
  to turn a NAMED cell red: (T1) the §2.14 carrier cell 203/210 -> 124/128
  (a real pre-L172 per-batch union) => D2; (T2) a second canonical
  denominator for the clamp arm, 78/98 -> 78/258 => D1; (T3) delete the
  cutscr0 reconciliation clause => D3.

## Declared exempt regions (the family-matched tables)

The card names three families. I enumerate them from the DRAFT instead of
from the card sentence (L44 rule), and register in advance that the census
may find MORE than three; a region found this way is declared with its
heading and reason, and a region the card named but the draft does not
contain is reported as vacuous rather than quietly dropped.

Seed list (to be confirmed or corrected against the body):
1. §2.7 scramble cohort table — seven cohorts + base on the same 3 fresh
   batches; family-matching is a FEATURE (the card's own words), and the
   body already reconciles it ("39/48 on its own fresh batches [l168.scr];
   41 of 50 on the canonical pool [l172.pooled]").
2. §2.10 gain-ensemble cells — per-jitter-set by construction, must NOT be
   pooled (§2.9/§2.10 admissibility rule).
3. §2.12 rewire / hom / swap arms — 2 batches each, not yet canonical.
4. §2.1 single-cell scan table — 34 deletions on one shared batch. NOT in
   the card's list of three; if the census finds it, that gap in the card
   is part of the finding.

## Predictions (registered, scored honestly)

- Q1: D4 passes and the §2.14 table resolves 1:1 (14 of the 15 canonical
  arms appear there; cutscr0 lives in §2.7 instead).
- Q2: all three tampers turn their NAMED cell red, none of them any other
  primary cell.
- Q3: D1 and D2 pass on the live draft — the pre-L172 two-union defect is
  genuinely gone from CANON-class cells.
- Q4: D3 does NOT pass cleanly on the first census: I expect at least one
  BATCHMULT cell outside the three regions the card names (§2.1 is the
  candidate), so the honest first-run outcome is a named list handed to
  L181 rather than a green board.

## Branches (registered, degenerate branch included — L55 rule)

- A_GREEN: D1-D4 and T all pass with exactly the declared exemptions. The
  card's Verify line is met as written.
- B_LIVE_DRIFT: tampers pass, D1 or D2 red on the live draft. The gate has
  found a real inconsistency; it is NAMED and handed to L181, the gate
  ships red, and the card is checked off for the INSTRUMENT with the drift
  recorded as owed work.
- C_REGION_GAP: D1/D2 green, D3 red only on regions the card's three-family
  list omits. The gate ships with the enumerated region set, the card's
  list is corrected in the bracket, and L181 inherits the explicit rule
  statement it already owes for family-matched tables.
- D_VACUOUS: a gate that cannot fail (no tamper turns a cell red, or no
  token resolves at all) is reported as vacuous, never as a pass.

## ADDENDUM 1 (written after the first census, BEFORE any verdict is read)

The first census showed the resolver, not the draft, was wrong: prose
sentences name an arm as a COMPARATOR, so sentence-level co-occurrence
mis-attributes. Measured false attributions: "30 of 66 ... above the base"
and "flip-completing on the cut base (pooled 78 of 98" both resolved to
`cutwA` because 'base' was the only phrase in the unit — which is how
`cutwA` came out carrying four denominators [34, 66, 98, 258]. Prose
attribution by co-occurrence is UNSOUND and cannot carry a gate.

AMENDMENT: D1/D2/D3 are scoped to TABLE ROWS ONLY (the label column
resolves the row's tokens). That is where the canonical pooled counts live
and where the defect L172 fixed actually lived — two different unions in
two sections' tables. Prose tokens become a reported DIAGNOSTIC census,
explicitly not a gate axis. All three tampers survive the amendment (T1/T2
are table cells; T3 is a body substring check, not an attribution).
