# LETTER brief — the response-to-reviewers document

Owner-directed (2026-11-21 ~14:0x). Draft the public response letter for
the three referee rounds + the independent second opinion.

## Sources (read-only)

- paper/review_fable.md (round 1: 12 majors)
- paper/review_fable_r2.md + evidence (round 2: silent twin, Methods,
  unchopped selectivity, paired p, pooling)
- paper/review_claudeai_fable_20261121.md (independent rebuild; Alstott;
  56-cell fixed-gain scan)
- paper/review_astra_r3.md + evidence (cross-family; cross-seed
  time-locking; D2 confirmation; title demand)
- ~/critters/peabrain/LANE-LOG.md (today's in-session lines:
  the adjudications, experiments L175-L191, receipts)
- paper/DRAFT.md (the current folded state — where each fix landed)

## Task

paper/RESPONSE-LETTER.md, one section per reviewer:
- Round 1 (fable): each of the 12 majors → resolved/partial + where in
  the draft (section pointer) + the artifact that closed it
- Round 2 (fable): the 7 adjudicated claims → our verification + the fix
- Second opinion (claude.ai fable): silent twin confirmed; Alstott
  folded; its 56-cell scan vs our gain-matched L175/L185 (both stated)
- Round 3 (astra): D2 independently confirmed; cross-seed finding → the
  three-readout panel; title adopted; McNemar primary; what remains open
  (gate-jitter unresolved, relay-matched twin pending, single batch
  classes) stated honestly as limitations, not hidden
- Closing: the verification machinery (gates, prereg, anchors) and the
  public repo/commit for every claim

## Rules

- Every "we fixed X" must carry a section pointer + artifact path; every
  number from numbers.json. No defensive prose; referees were right where
  they were right — say so.
- Writes ONLY paper/RESPONSE-LETTER.md (+ one LAB-INTENT.md append). No
  draft edits, no gate files. Wall ≤1 h. Final answer ≤150 words.
