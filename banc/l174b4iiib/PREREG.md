# PREREG — L174 stage (b4-iii-b): the batch-code RELABEL + a Methods mapping
Written BEFORE any draft byte changed. Tick 214, 2026-11-21.

## Scope (inherited contract + what is new)
Inherits (b3b)/(b4-i)/(b4-ii)/(b4-iii-a): T3 verifier literals verbatim modulo
declared exceptions; T4' DECLARED SPARSE EDITS against an EXACT frozen pre-image
(emit.py refuses a second run); T5 six paper verifies green; T7-STRONG
(pre-image + declared edits == live, byte for byte); T10 ZERO RESIDUE; T8
born-clean for any NEW text.

NEW this stage:
- T1' RELABEL-ONLY. No measurement moves: the measurement-token multiset and
  the citation-key multiset are IDENTICAL before and after. A letter scheme is
  chosen over "batch 1..11" FOR THIS REASON — letters add no digit run, so the
  measurement gate needs no new exclusion class (the (b4-iii-a) ADDENDUM-1
  lesson: never loosen a measurement gate to pass a strip). Second reason: the
  labels sit next to seed counts ("fresh batch K, n=16"), where a numeric label
  invites a misread. I and O are skipped so a label cannot read as a digit.
- T12 BIJECTION + MAPPING. The eleven cited batches get labels A,B,C,D,E,F,G,H,
  J,K,L in RUN ORDER (internal codes are chronological, so "fresh batch" claims
  stay monotone in the label); the mapping lives in §3.7 Methods and is the ONE
  declared place the internal codes survive. Gate: one-to-one, each code exactly
  once in the mapping block, every body occurrence relabeled.
- T13 ARTEFACT KEYS ARE NAMES. Batch codes inside stored keys
  (`l145.pooled.eOutMot_B29_B31`, `l148.pooled.eAll_B29_B32`) are FILENAMES, not
  prose: asserted BYTE-UNCHANGED. Relabeling them would break correspondence
  with the stored npz/json on disk.
- T14 DECLARED REFLOW. Three substituted lines cross the 78-col house width;
  exactly two paragraphs (771-780, 827-831) are re-wrapped as declared units.
  No edited line may exceed 78.

## Premise finding (registered, read not assumed)
The `B<n>` shape covers TWO semantic classes, and tick 213's frozen caps
partition conflated them: DEFER_BATCH holds `B1-B4`, which is a PREREGISTERED
BRANCH range, not a batch. Branch labels (`B1-B4`, `B2_preserved`, the bare `B4`
degenerate branch) carry precedence structure a reader needs and are DECLARED
OUT OF SCOPE here, asserted byte-unchanged; the partition is amended (not
rewritten) so DEFER_BATCH splits into KEEP_MAPPING (the 11 batch codes, which
after this stage occur only inside the Methods mapping block, so (b4-iii-c) must
KEEP them) and DEFER_BRANCH (`B1-B4`). Completeness over all 179 distinct tokens
is re-asserted. The banner (out, (b4-iv)) and §7 (out of manuscript scope per
(b4-iii-a)) stay byte-unchanged.

## Census re-derived THIS tick (census.py, classify.py)
39 `B<n>` occurrences in the draft: 19 BATCH prose (11 distinct: B26 B27 B29 B30
B31 B32 B33 B34 B35 B37 B38), 6 ARTEFACT_KEY, 4 BRANCH, 10 in the banner, 0 in §7.

## Substitution rule (deterministic, one rule)
At each BATCH occurrence: bare letter if the preceding text ends in
`batch`/`batches` (optional comma/colon, optional open paren) or in a label
separator `<label>/`; otherwise `batch <letter>`. No block special-case; the
alternative (bare letters inside the "(Batches: ...)" parenthetical) reads
better but needs a second rule, and ambiguity would cost more than repetition.

## Branches (precedence)
R3_literal_lost > R2_measurement_moved > R1_relabel_only.

## Predictions
- Q1: all six paper verifies green after the apply with EXACTLY five verifier
  literal re-points and no other verifier edit. [TRUE/FALSE]
- Q2: the measurement-token multiset is identical with ZERO named removals —
  the first stage in this lineage that needs no removed-run disclosure, because
  a letter scheme deletes identifier runs and adds none. [TRUE/FALSE]
- Q3: l159_verify untouched and green (§1's one edit is a token swap, so no
  sentence changes word count). [TRUE/FALSE]
- Q4: exactly ONE partition class needs amending (DEFER_BATCH splits), and the
  amended partition still covers all 179 distinct tokens. [TRUE/FALSE]
- Q5: the body's "(Batches: ...)" parenthetical survives as CONTENT (it carries
  which ARM ran in which batch; the Methods mapping does not), so this stage
  deletes nothing. [TRUE/FALSE]
