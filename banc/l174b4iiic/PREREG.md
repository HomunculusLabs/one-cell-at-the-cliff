# L174 stage (b4-iii-c-i) — PREREG

Date: 2026-11-21 (tick 215). Lane item: L174 (ideas 87), stage (b4-iii-c),
slice (i). Zero rollouts, zero RNG, no graph build, no torch: the only
compute is string arithmetic over `paper/DRAFT.md`, the six stored verifier
sources, and the frozen caps partition of ticks 213/214.

## 0. Premise finding that defines the slice (registered BEFORE any edit)

A fresh live census (`census.py`, run first) re-derives the all-caps
distribution after the (b4-iii-b) relabel: 225 of the 940 live occurrences
are UNCLASSIFIED against tick 213's frozen partition, and 178 of those sit
in the changelog banner, which stage (b4-iv) owns. Inside the manuscript the
census produces three facts the card's one line does not anticipate:

1. **§5 Discussion carries ZERO caps tokens in any class.** Tick 212 wrote
   it in the lowercase house form, so §5 is this stage's STYLE REFERENCE
   rather than its workload — it needs no edit at all.
2. **§3 Methods is a different KIND of job.** Four tokens are MODEL SYMBOLS
   there (`BG`, `DT`, `TAU`, `WIN`) living inside the state equation and the
   parameter table, two of which (`TAU`, `WIN`) tick 213 classified as
   NOTATION/STRIP at TOKEN level; and one token splits by POSITION inside
   §3 alone (`BY`: the licence name `CC BY 4.0` versus the emphasis `BY
   CONSTRUCTION`). §3 also hosts the eleven KEEP_MAPPING codes of
   (b4-iii-b), which must survive byte-exact. So §3 needs an
   OCCURRENCE-level judgement plus block protection: it becomes slice (ii).
3. **§2 Results is the bulk** (89 STRIP + 36 class labels + 16
   unclassified): slice (iii).

This slice therefore owns the two PURE-PROSE sections, §1 Introduction and
§4 Limitations, where every owned occurrence is unambiguous de-emphasis.
This is the same premise discipline as tick 213 (§6/§7) and tick 214 (the
three `B<n>` classes): read the census, classify by position, and slice by
KIND rather than by size.

## 1. Contract (inherited, unchanged unless named)

- **T1'' DE-EMPHASIS ONLY.** The whole-draft measurement-token multiset and
  the citation-key multiset are IDENTICAL pre and post. Measurement tokens
  use the (b4-iii-a) ADDENDUM-1 form (digit runs with no preceding
  alphanumeric, §-refs stripped). A case change cannot move a number, so
  unlike tick 213 this slice should need ZERO removed-run disclosure; if it
  needs one, that is a defect, not a disclosure.
- **T3 LITERALS VERBATIM** modulo harvest-declared exceptions. Overlap
  between an edit's old form and a verifier literal is tested in BOTH
  directions (the tick-213 Q2 lesson): literal contains old form, AND old
  form contains literal.
- **T4' DECLARED SPARSE EDITS.** Every edit is a (line, column, old, new)
  tuple derived by the stage's own parsed rule from an EXACT frozen
  pre-image; `emit.py` asserts the live draft equals the freeze before
  splicing and REFUSES a second run.
- **T5** all six paper verifies green before (CERT-1) and after.
- **T7-STRONG** pre-image + the declared edits == the live draft BYTE FOR
  BYTE from the title block onward.
- **T8 BORN CLEAN** — not applicable: this slice adds no new text.
- **T10 ZERO RESIDUE, SCOPED.** After the edit, the caps regex finds no
  owned-class occurrence inside §1 and §4; every byte outside those two
  section ranges is UNCHANGED except the changelog banner's own new entry.
- **T11' PARTITION.** The frozen partition's non-owned classes stay
  occurrence-identical inside the slice; the owned classes
  (STRIP_EMPHASIS, CLASS_LABEL_lowercase) go to zero inside the slice and
  are UNTOUCHED outside it.
- **T15 CASE-ONLY (new).** Every edit is a pure case change: for each edit,
  `old.lower() == new.lower()`, and the draft's letter multiset modulo case
  is identical pre and post. This is the strongest available gate on a
  de-emphasis stage and it makes "a word was lost" unprovable rather than
  merely unobserved.

## 2. Transform rule (deterministic, parsed not typed)

An owned occurrence is replaced by its lowercase form, EXCEPT when it is
sentence-initial — the token starts the line, or the preceding non-space
text ends in `.` or `:` — in which case only its first letter stays
uppercase. The rule is applied by `plan_i.py` to the frozen pre-image and
re-derived independently inside the verifier; no replacement is typed by
hand.

Class labels (`SUPER`, `PARTIAL`, `INTERMEDIATE`, `KILL`, `NOT-SUPER`)
follow §5's existing lowercase house form, which is why they are owned here
rather than deferred.

## 3. Certifications

- **CERT-1** all six paper verifies GREEN on the PRE-edit draft, exit codes
  stored under `raw/`.
- **CERT-2** `numbers.json` copied FIRST and asserted BYTE-IDENTICAL at the
  end (`cmp`), at least twice.
- **CERT-3** the whole draft frozen as `draft_pre.md`; emit asserts equality
  and refuses a second run.
- **CERT-4** the transform PARSED not typed: every owned occurrence in the
  two section ranges is accounted for, the sentence-initial split is
  asserted by count, and no edit outside the ranges exists.

## 4. Branches (precedence, checked in this order)

1. **C3_literal_lost** — a verifier literal or required string contains an
   owned old form and cannot be re-pointed to a strictly-stronger form.
   Then the edit is withdrawn for that site and the site is disclosed.
2. **C2_meaning_moved** — T15 or T1'' fails: some edit is not a pure case
   change. Then the whole slice is withdrawn.
3. **C1_deemphasis_only** — T15 and T1'' hold and the slice is applied.

## 5. Predictions (scored in the log)

- **Q1** Six verifies green with a SMALL number of verifier-literal
  re-points (registered band: 1–12), because §1/§4 are the sections whose
  claim language the suite pins hardest.
- **Q2** The measurement multiset is identical with ZERO removed digit runs
  (a case change cannot move a number) — a stronger form of tick 214's Q2.
- **Q3** `l159_verify` (the >60-word sentence gate) is untouched and green:
  a case change moves no word boundary.
- **Q4** Visible-character delta is EXACTLY ZERO (registered: `|Δ| == 0`
  outside the banner entry). This is the first stage of this lineage whose
  edit cost is provably zero bytes.
- **Q5** `l158_verify`'s frozen abstract vocabulary is untouched: the
  abstract is out of scope and byte-identical.

## 6. Out of scope, declared

§2 Results, §3 Methods (slices iii and ii), §5 Discussion (needs nothing),
§6 Data & code and §7 Author/submit notes (tick 213's premise declaration),
the References list, and the changelog banner (stage b4-iv), which this
slice modifies only by appending its own entry.
