# L174 stage (b3b) — PREREG (bullets -> prose, §1 through §2.3)

Written BEFORE any draft edit. Tick 208, 2026-11-21.
Zero rollouts, zero RNG, no graph build. The only compute is string
arithmetic over the stored draft and the stored verifier sources.

## Scope

Stage (b3b) as inherited from tick 207 names "the 42 bullet lines in §1-§2
-> prose". Measured census (harvest.py, stored literals.json): 42 bullet
lines live in §1 (6), §2.1 (4), §2.2 (4), §2.3 (1), §2.5 (3), §2.6 (4),
§2.7 (16), §2.8 (4). That is more prose than one tick can write honestly,
so (b3b) is SLICED by section group and this tick takes the first group:

  (b3b-i)   THIS TICK — §1 Introduction + §2.1 + §2.2 + §2.3 = 15 bullets
  (b3b-ii)  §2.5 + §2.6 + §2.8 = 11 bullets
  (b3b-iii) §2.7 = 16 bullets (the pre-posting controls, heaviest key load)

Rationale for taking §1 first: it is the block a referee reads first and the
only one covered by the l159 long-sentence gate, so it is where a prose pass
can break something that matters.

EDIT SPAN (T4): the exact draft slice from `## 1. Introduction` through the
character immediately before `### 2.4 Mechanism`. Frozen byte-exact as
`span_pre.txt` (14,409 chars, 226 lines) per the tick-207 ADDENDUM 2 lesson
(freeze the EXACT slice, never a re-joined line list). No other draft block,
and no numbers.json key, may change.

## Contract

T1  FORMAT-ONLY, and provably so: the span's NUMERIC TOKEN MULTISET and its
    CITATION-KEY MULTISET must be IDENTICAL before and after. This is
    strictly stronger than (b2)'s relocation rule and (b3)'s de-duplication
    rule, both of which permitted a token to leave its block. A
    bullets-to-prose pass has no business moving a number at all, so the
    allowed delta is the empty set. Any needed exception is a PREREG
    ADDENDUM written before the splice.
T2  No number enters that numbers.json does not already carry — satisfied
    vacuously by T1 (no number enters at all).
T3  Every verifier literal that currently lives in the span survives
    VERBATIM, and no verifier may be edited to make a prose choice pass.
    ONE declared exception class, registered here because the harvest found
    it BEFORE the rewrite: a literal whose match depends on the OLD BULLET
    INDENTATION (a literal containing `\n` plus continuation spaces) cannot
    survive de-indentation by construction. harvest.py found exactly two —
    `'NOT\n  MET'` (l149_verify) and `'not that\n    identity matters'`
    (l174_verify). For these the gate is made WRAP-INSENSITIVE (assert
    against a whitespace-normalized view of the draft) rather than
    re-worded, which is the l122 wrap-fragility lesson applied to a gate:
    the claim text is unchanged, the gate stops depending on line breaks.
    Both are additionally written so the phrase lands on ONE line, so the
    old exact form would pass too. Any OTHER literal failure is a real
    failure and gets fixed in the prose.
T4  The span above is the only part of DRAFT.md this stage may edit, proven
    by a single-block substitution `d[:i] + new + d[j:]` after asserting
    `d[i:j] == span_pre.txt`.
T5  Prose must not create long sentences: l159 (zero >60-word sentences in
    abstract/§1) stays green, and the 42-bullet census must drop to 27.

## Certification (before any edit)

CERT-1  All six paper verifies GREEN on the PRE-edit draft, stored under
        raw/cert1_*.txt. A stage that starts red cannot attribute its own
        failures. (Run: all six exit 0.)
CERT-2  numbers.json copied FIRST to numbers_pre.json (sha 238bf2d37f51)
        and asserted BYTE-IDENTICAL at the end of the tick.
CERT-3  span_pre.txt frozen from the live draft, and emit.py asserts the
        live span equals that freeze before splicing; emit.py refuses a
        second run.
CERT-4  The block transform is parsed, not typed: emit.py finds the bullet
        blocks by regex, asserts exactly 15, and asserts every opener
        matches exactly one entry of a declared rewrite map (count==1 per
        entry, no unmapped block, no unused map entry). Body lines are
        de-indented mechanically; only the opener lines are re-authored.

## Branches (precedence: B2 before B1 — the silent failure first)

B2_tokens_moved   If the numeric or citation multiset differs at all, the
                  pass is NOT format-only. Report it as such, do not
                  rationalize the delta, and either fix the prose or write
                  an addendum naming the exact tokens and why.
B1_format_only    Multisets identical, all literals present, bullet census
                  42 -> 27, all six verifies green. The expected branch.
B3_literal_lost   A literal outside the two declared wrap-fragile ones
                  cannot be preserved in readable prose. Then the prose
                  yields: re-author the sentence around the literal.

## Pins (derived, not remembered)

P1  span_pre.txt: 14,409 chars, 226 lines, 15 bullet lines, 355 numeric
    tokens (188 distinct), 45 citation-key tokens (35 distinct).
P2  99 verifier literals occur in the span; 59 of them occur NOWHERE else
    in the draft; 2 are multiline (the declared T3 exception class).
P3  The scramble block of §2.2 (the mass-matched cohort table, its three
    numbered findings, the row-provenance paragraph) is NOT a bullet list
    and is NOT touched: a numbered enumeration is prose convention, and
    the referee's complaint was bullet lines. Asserted by a byte-identity
    check on that sub-block.
P4  l159's >60-word count stays 0, and no new sentence exceeds 45 words.
P5  Char delta is REPORTED, never gated (a prose pass may legitimately
    grow: removing a label-colon opener costs words).

## Predictions (scored in the log either way)

Q1  The char delta comes out slightly POSITIVE (+1 to +4%): label-colon
    openers ("Framing:", "Substrate:", "Non-monotone:") become subjects and
    verbs, which costs characters. If it comes out negative, something was
    deleted — check against T1.
Q2  Most of the 99 literals survive with ZERO prose care, because stripping
    leading whitespace from a wrapped body line cannot break a single-line
    literal. The at-risk set is the 15 opener lines only.
Q3  The l159 gate stays green without intervention, because this pass
    splits no sentences and merges none — it only removes markers.
