# PREREG — L174 stage (b4-ii): the Discussion, and closing the §2.8 70-word sentence

Written BEFORE any draft byte changed. Tick 212, 2026-11-21.
Inherits the stage-(b3b)/(b4-i) contract unchanged except where stated.

## What this stage does

Two edits, and nothing else:

1. **E1 — the inherited long sentence.** §2.8's envelope-disclosure sentence
   is the ONE >60-word sentence left in §1-§4; l149 §(26) pinned it at 70
   words precisely so that closing it would be gate-visible. It is split
   content-preservingly under instrument **T7** (declared `(old, new)` pairs,
   ported from stage (b4-i)).
2. **E2 — a Discussion.** The card asks for a Discussion and the manuscript
   has none. It is authored as new prose, inserted as `## 5. Discussion`
   immediately before the present `## 5. Data & code`, which renumbers to
   `## 6.` and pushes `## 6. Author/submit notes` to `## 7.`

ZERO rollouts, zero RNG, no graph build. The only compute is string
arithmetic over the stored draft and the six stored verifier sources.
No measured value changes; numbers.json must be byte-identical at the end.

## Placement rationale (registered, so it cannot be rationalised later)

The Discussion goes AFTER §4 Limitations rather than between §2 and §3
because (i) §4 is already the scope half of a discussion and the two read
in sequence, and (ii) inserting ahead of Methods would renumber §3.1-§3.10
and §4, i.e. four headings plus ten subsection numbers plus every verifier
slice that locates them, for a typesetting preference the owner will make
at submission anyway. Final section ORDER for the venue is explicitly left
to stage (c)/owner; this stage commits the TEXT, not the running order.

## Contract

- **T1 (format-only, E1 only).** The §2.8 numeric-token multiset and the
  citation-key multiset are IDENTICAL before and after (trailing commas
  stripped, (b4-i) ADDENDUM 2). Allowed delta: EMPTY.
- **T2 (E1 is neutral to its neighbours' gates).** The E1 edit must be
  VISIBLE-CHARACTER-NEUTRAL and PARAGRAPH-NEUTRAL, so l149 §(24)'s pins on
  this very region (visible delta +48, 16 paragraphs, the four bold leads,
  the robustness-panel table) hold with NO re-point. Registered because it
  is a design constraint on how the split may be written, not a hope: the
  splits are punctuation-for-punctuation (`, so` -> `. So`, ` — but` ->
  `. But`), which keeps whitespace-stripped length constant.
- **T3 (literals).** Every verifier literal living in §2.8 survives
  verbatim. Declared exception classes, both inherited: wrap-fragile
  literals (match depends on a line break) checked normalized, and
  bullet/punctuation-marker literals re-pointed at an equally strong form.
  The exception set must be found by the HARVEST, before the rewrite.
- **T4 (substitution).** Both edits are single-block substitutions against
  EXACT frozen draft slices (tick-207 ADDENDUM 2). emit.py asserts the live
  slice equals its freeze before splicing and refuses a second run.
- **T5 (suite).** All six paper verifies green after, numbers.json
  byte-identical (cmp against numbers_pre.json).
- **T7 (content-preserving split).** Each split is a declared `(old, new)`
  pair matching exactly once; the section's CONTENT-WORD SEQUENCE (every
  alphanumeric token outside the closed connective set
  `{and, while, so, therefore}`) is identical before and after. Proved the
  STRONG way (stage (b4-i) ADDENDUM 3): pre-image + all declared edits ==
  live section, so no undeclared word can enter, leave or move.
- **T8 (the Discussion is born clean).** The Discussion must carry, by
  construction and by assert: zero list items; zero sentences over 60
  words; zero lane IDs (`L\d{2,3}`) and zero batch codes (`B\d{2}`); zero
  all-caps emphasis tokens (>=3 letters, outside a declared acronym
  allowlist); zero numbers.json bracket provenance keys and zero NEW
  numeric citation markers. Rationale: stage (b4-iii) owns stripping those
  four classes from the body, and a section authored today must not add to
  its work. Every number the Discussion quotes must already appear VERBATIM
  elsewhere in the draft (no new measured value enters the manuscript in a
  prose stage).
- **T9 (no claim inflation).** The Discussion may not assert uniqueness of
  the carrier, may not state or imply that "identity matters" is novel
  (both narrowings in §1 stand), and must point to §4 for limitations
  rather than re-litigating them. Checked as forbidden/required strings.

## Branches (pre-registered, precedence top-down)

- **B2_tokens_moved** — if either §2.8 multiset differs, the split moved a
  number or a key: revert to the frozen pre-image and report the breach.
- **B3_literal_lost** — if a harvested literal is lost and is not in a
  declared exception class: revert and report.
- **B4_neighbour_gate_broken** — if l149 §(24)'s pins on §2.5-§2.8 go red,
  the E1 edit was not neutral: revert and re-write the split, never loosen
  §(24).
- **B1_clean** — both edits land, all six verifies green: ship, and make
  the measurement permanent as l149 §(27).

## Predictions (scored in the log, wrong answers reported as wrong)

- Q1. The §2.8 visible-char delta is EXACTLY 0 and the raw delta is
  NEGATIVE (two punctuation characters become one each, and ` — ` loses a
  space). Band: visible 0, raw -1 or -2.
- Q2. The new longest §2.8 sentence is 40-55 words (the bold lead plus the
  short first clause is far shorter; the long tail clause is the binding
  one).
- Q3. Zero harvested §2.8 literals need an exception (the three (b3b-ii)
  wrap-fragile ones live in §2.6, not §2.8).
- Q4. The Discussion lands at 850-1,200 words over 6-8 paragraphs with its
  longest sentence under 55 words.
- Q5. l159 stays green and untouched: its scope is the abstract and §1, and
  the Discussion's own sentence rule is registered in l149 §(27) instead
  (the (b4-i) precedent — extend the gate that owns the region).

## Gate to be made permanent (l149 NEW section (27))

Re-derives from the frozen pre-images: the §2.8 split (both multisets, the
whole-section content-sequence proof, each split's old form absent and new
form present exactly once, the new longest sentence, visible-neutrality);
the §(26) 70-word pin RE-POINTED at the stored pre-image (the pin is not
deleted, it becomes "the pre-image carried 70, the live section carries
<=60" — strictly stronger); the Discussion's existence, position between
§4 and §6, paragraph count, zero list items, the 60-word rule, the four
T8 absence classes, the T9 required/forbidden strings, and the fact that
every number it quotes appears elsewhere in the draft; plus the v3.28
banner stage pin and the two renumbered headings.
