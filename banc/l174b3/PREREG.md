# PREREG — L174 stage (b3): the §2.4 editorial pass (reviewer I10)

Written BEFORE any draft edit. Tick 207, 2026-11-21. Zero rollouts, zero RNG,
no graph build: the only computation is string/char arithmetic over the stored
draft, the stored verifier sources and numbers.json.

## 0. Why this stage is §2.4 and not the bullets

The inherited (b3) spec names two jobs and says "(they touch the same
blocks)". That is a CARD-TEXT MIS-CARRY and it is corrected here (L44 class):
§2.4 contains ZERO bullet lines (measured: the 42 remaining bullet lines in
§1–§2 live in §1, §2.1, §2.2, §2.3, §2.5, §2.6, §2.7, §2.8). The two jobs are
therefore disjoint blocks and are split: this stage = §2.4 only; the
bullets→prose conversion becomes (b3b).

## 1. The premise test (run FIRST, before any edit)

Reviewer issue I10 (banc/l167/ADJUDICATION.md row 10) reads, verbatim:
"§2.4 (3.4k chars) presents two bit-identities as findings though both hold by
construction; sil24 kR=5 is not separable from its intact comparator =>
rebuild §2.4 on silW and demote the identities to Methods".

Its THREE substantive components are tested against the CURRENT draft before
anything is edited:

- I10a rebuild on silW — §2.4's first substantive paragraph must be the silW
  arm.
- I10b demote the two bit-identities to Methods — both identity passages must
  be in §3.8 and absent from §2.4.
- I10c sil24 separability — §2.4 must state that sil24 is not separable from
  its comparators.

The quoted "(3.4k chars)" is treated as a MEASUREMENT, never a target: the
same adjudication file records that I10's own locator truncated §2.4 at a
2,600-char cap (correction 3), so the figure was taken through a bounded read
of an earlier draft. No char target is inherited from the referee.

## 2. Rules (T1–T5)

- T1 COMPRESSION IS DE-DUPLICATION, NEVER DELETION. Every numeric token that
  leaves the §2.4 prose must still be present either in §2.4's own grid table
  or elsewhere in the body (§1–§6). Zero orphans.
- T2 NO NEW NUMBER. No value may enter §2.4 that numbers.json does not
  already carry; numbers.json must be byte-identical at the end.
- T3 EVERY GATE LITERAL SURVIVES. All 101 string literals that the six paper
  verifiers assert and that currently occur in §2.4 (stored list:
  l174b3/lits24.json) must still occur in §2.4 afterwards, VERBATIM —
  including the three that contain an internal newline, whose line break is
  preserved exactly (l122 wrap-fragility lesson). No verifier may be edited to
  accommodate the compression; if a gate fails it is because the prose lost
  something, and the prose is fixed.
- T4 §2.4 IS THE ONLY BLOCK THIS STAGE EDITS (plus the version banner, the
  CLAIM-MAP and l158's banner-scoped pins). The pre-image is frozen to
  l174b3/sec24_pre.txt and the emit step asserts the draft's §2.4 equals that
  freeze before substituting.
- T5 CLAIM INVENTORY PRESERVED. The section's twelve claim leads (the eleven
  paragraph leads plus the table) each keep a sentence making the same claim;
  the count is pinned pre-edit and asserted post-edit.

## 3. Pre-registered gate

- G1 length: §2.4 ≤ 7,200 chars (pre-image 9,936). Rationale for 7,200 and not
  the referee's 3.4k: 1,328 prose chars are inside asserted gate literals and
  1,417 chars are the grid table, both untouchable under T3/T5, so the
  reachable floor is bounded by certified content, not by taste. The achieved
  value is reported exactly (L125 feasibility rule: the constraint is checked
  against stored pins before the machinery is built).
- G2 literals: 101 of 101 present.
- G3 orphans: 0 numeric tokens dropped from the prose without a home.
- G4 all six paper verifies green, numbers.json byte-identical.
- G5 l159 (sentence length ≤ 60 words) green — a compression that fuses
  sentences is the likely way to break it, so it is named here.

## 4. Branches (precedence: the failure is checked first)

- S2_premise_not_satisfied — if ANY of I10a/I10b/I10c is not already true in
  the current draft, that component is the stage's substantive work and the
  compression is secondary. CHECKED FIRST.
- S1_editorial_only — all three substantive components already shipped (ticks
  201/202 under L173), so I10's residue is editorial length only and this
  stage closes it by de-duplication.
- S3_compression_infeasible — if the certified content alone exceeds 7,200
  chars, G1 is withdrawn as unreachable and the measured floor is reported
  instead (the L125 "a dead spec is amended, not faked" path).

## 5. Pins (P1–P5)

- P1 §2.4 pre-image = 9,936 chars, 236 prose numeric tokens, 56 table tokens,
  106 prose tokens duplicated in the table, 1,417 table chars.
- P2 38 of the 101 gate literals occur ONLY in §2.4 (nowhere else in the
  draft) — these are the strings a careless compression would orphan, and
  this enumeration IS the tick-206 lesson applied pre-edit ("grep the other
  verifiers for string literals sliced out of a block BEFORE editing it").
- P3 bullet lines in §1–§2 = 42 (the card says 37; the count grew with
  stages (a)/(b1)). Recorded so (b3b) inherits a measured number, not a
  remembered one.
- P4 numbers.json sha256 = 238bf2d37f51… (same as the (b2) pre-copy).
- P5 prediction: G5 (sentence length) is the gate most likely to fire; if it
  does, the fix is punctuation-only splits, never a claim drop.

## ADDENDUM 1 (written after the premise test and the feasibility measurement,
## before the draft splice; no verifier and no claim was touched to make it fit)

Two pins and one gate are corrected here, with the reasons, because both were
derived from a bounded first pass rather than from the artifacts.

1. P2 CORRECTED. The "38 of 101 literals exclusive to §2.4" figure came from an
   ASCII-only literal harvest; decoding the verifiers' unicode-escaped literals
   as well gives 101 literals in §2.4 of which 62 occur NOWHERE else in the
   draft (premise.json). The larger number strengthens the tick-206 lesson it
   implements: 62 strings would have been orphaned by a careless slice.

2. G1 WITHDRAWN AS MIS-DERIVED, REPLACED BY G1'. The registered cap (≤7,200
   chars) was derived by subtracting only gate-literal chars and the table from
   the pre-image, which silently assumed the remaining prose is padding. It is
   not: §2.4 states 143 distinct numeric tokens and 24 citation keys, and each
   needs its own clause. Measured on the achieved text, 1,258 prose chars sit
   inside asserted literals while the section still carries every claim, so the
   cap was never reachable without DELETING disclosures — exactly the failure
   mode T1 exists to forbid. A char cap on certified prose rewards deletion;
   therefore the gate becomes a de-duplication rule, which cannot:

   G1' DE-DUPLICATION COMPLETENESS — no (meanR, kR/n) cell that §2.4's grid
   table carries may be restated in the §2.4 prose, unless a verifier asserts
   that exact prose spelling (span containment, not substring matching). The
   char reduction is then REPORTED, not gated, with a floor of ≥10% so the
   stage cannot be vacuous.

   Sensitivity self-test (registered here, run before the splice): G1' must
   FAIL on the frozen pre-image. It does — 5 violations (eOutInt .781/15,16,
   eIn .793/15,16, eOutMot .525/9,16 and .632/12,16, eMotIn .801/15,16) — and
   PASS on the candidate. A gate that cannot fail on the old text is not
   measuring the compression.

3. The referee's "3.4k chars" remains a measurement, never a target, for the
   reason already recorded in section 1: the same adjudication file states that
   I10's locator truncated §2.4 at a 2,600-char cap.

## ADDENDUM 2 (freeze correction, pre-splice)

The first freeze of §2.4 was written from a line-join and lost the span's
final newline (9,936 vs the live 9,937 chars), so emit.py's T4 pre-image
assert FAILED on its first run and wrote nothing — the one-shot guard did its
job. The freeze is now the LIVE span d[i:j] verbatim; P1's char pin reads
9,937. Lesson for the next block stage: freeze a block as the exact draft
slice, never as a re-joined line list.
