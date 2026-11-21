# L174 stage (b3b-ii) — PREREG (bullets -> prose, §2.5 / §2.6 / §2.8)

Written BEFORE any draft edit. Tick 209, 2026-11-21.
Zero rollouts, zero RNG, no graph build. The only compute is string
arithmetic over the stored draft and the six stored verifier sources.

## Scope

Stage (b3b) was sliced by section group in tick 208 after measuring the
per-section bullet census: (b3b-i) §1 + §2.1 + §2.2 + §2.3 = 15 bullets
(SHIPPED, tick 208), (b3b-ii) §2.5 + §2.6 + §2.8 = 11 bullets (THIS TICK),
(b3b-iii) §2.7 = 16 bullets (the pre-posting controls, heaviest citation-key
load). The census is re-derived this tick, not inherited: §2.5 3, §2.6 4,
§2.7 16, §2.8 4.

EDIT SPAN (T4): the exact draft slice from `### 2.5 Robustness` through the
character immediately before `### 2.9 Statistics`, frozen byte-exact as
`span_pre.txt` (15,472 chars, 247 lines) per the tick-207 ADDENDUM 2 lesson
(freeze the EXACT slice, never a re-joined line list).

§2.7 LIES INSIDE THAT SPAN and belongs to (b3b-iii). It is excluded by a
BYTE-IDENTITY GATE, not by span surgery: `sev_pre.txt` is the §2.7 slice and
emit.py asserts that exact byte string appears in the new span. This keeps
the single-block substitution proof of T4 while proving §2.7 untouched (the
P3 instrument of tick 208, promoted from a sub-block to a whole subsection).

## Contract

T1  FORMAT-ONLY, and provably so: the span's NUMERIC TOKEN MULTISET and its
    CITATION-KEY MULTISET must be IDENTICAL before and after (411 numeric
    tokens, 37 citation-key tokens). Inherited from (b3b-i) unchanged — a
    bullets-to-prose pass has no business moving a number, so the allowed
    delta is the empty set. Any needed exception is a PREREG ADDENDUM
    written before the splice.
T2  No number enters that numbers.json does not already carry — satisfied
    vacuously by T1 (no number enters at all).
T3  Every verifier literal that currently lives in the EDITABLE text
    survives VERBATIM, and no verifier may be edited to make a prose choice
    pass. ONE declared exception class, registered here because the harvest
    found it BEFORE the rewrite: a literal whose match depends on the OLD
    BULLET INDENTATION (a literal containing `\n` plus continuation spaces)
    cannot survive de-indentation by construction. harvest.py found exactly
    three, all in l149_verify section (17)'s §2.6 prose contract:
    `'0.1946 / 0.0642 /\n  0.1333'`, `'agrees to\n  within .0025'` and
    `'from 37/33 to 6/2 but never\n  reach zero'`. For these the gate is
    made WRAP-INSENSITIVE (assert against a whitespace-normalized view)
    rather than re-worded — the l122 wrap-fragility lesson applied to a
    gate: the claim text is unchanged, the gate stops depending on line
    breaks, and the normalization makes the loop STRICTLY stronger because
    a literal can no longer hide behind a different wrap. The
    literal-aware reflow additionally keeps each phrase contiguous.
    Any OTHER literal failure is a real failure and gets fixed in the prose.
T4  The span above is the only part of DRAFT.md this stage may edit, proven
    by a single-block substitution `d[:i] + new + d[j:]` after asserting
    `d[i:j] == span_pre.txt`; and §2.7 inside it is proven byte-identical.
T5  The six paper verifies stay green, and the span's bullet census drops
    from 27 to 16 (§2.7's, untouched).

## Certification (before any edit)

CERT-1  All six paper verifies GREEN on the PRE-edit draft, stored under
        raw/cert1_*.txt. A stage that starts red cannot attribute its own
        failures. (Run with the peabrain venv python: l149 section (20)
        needs torch.) DONE: six exit 0.
CERT-2  numbers.json copied FIRST to numbers_pre.json (sha 238bf2d37f51)
        and asserted BYTE-IDENTICAL at the end of the tick.
CERT-3  span_pre.txt frozen from the live draft, and emit.py asserts the
        live span equals that freeze before splicing; emit.py refuses a
        second run.
CERT-4  The block transform is parsed, not typed: emit.py finds the bullet
        blocks by regex, asserts exactly 11 EDITABLE blocks (plus §2.7's 16
        inside the frozen sub-slice), and asserts every opener matches
        exactly one entry of a declared rewrite map (count==1 per entry, no
        unmapped block, no unused map entry).

## Branches (precedence: B2 before B1 — the silent failure first)

B2_tokens_moved   If the numeric or citation multiset differs at all, the
                  pass is NOT format-only. Report it as such, do not
                  rationalize the delta, and either fix the prose or write
                  an addendum naming the exact tokens and why.
B1_format_only    Multisets identical, every editable literal present,
                  bullet census 27 -> 16, §2.7 byte-identical, all six
                  verifies green. The expected branch.
B3_literal_lost   A literal outside the three declared wrap-fragile ones
                  cannot be preserved in readable prose. Then the prose
                  yields: re-author the sentence around the literal.

## Pins (derived this tick, not remembered)

P1  span_pre.txt: 15,472 chars, 247 lines, 27 bullet lines (16 of them
    §2.7's), 411 numeric tokens (173 distinct), 37 citation-key tokens
    (32 distinct).
P2  232 verifier literals occur in the span; 125 occur NOWHERE else in the
    draft; 103 touch text this stage may edit; 12 are multiline, of which
    exactly 3 touch editable text (the declared T3 exception class).
P3  §2.7 (`### 2.7 Pre-posting controls` through the character before
    `### 2.8 The slow line`) is byte-identical after the splice.
P4  Markdown TABLE lines are emitted verbatim (de-indented only) and never
    reflowed — reflowing a pipe table destroys it. The §2.8 robustness
    panel's 4-row table must survive as a table.
P5  §2.8's four bold claim leads (`**Re-attribution ...**` etc.) survive
    verbatim as paragraph lead-ins. This is the SAME prose form §2.7
    already uses twice (`**Displacement is not removal ...**`), so the
    conversion makes §2.8 consistent with the house style already in the
    manuscript rather than inventing one.
P6  Char delta is REPORTED, never gated; the honest measure is the
    VISIBLE-character delta (whitespace stripped), because de-indenting a
    wrapped bullet body lowers the raw count and reads as deletion
    (the tick-208 instrument).

## Predictions (scored in the log either way)

Q1  The VISIBLE-char delta comes out slightly positive (+50 to +400): only
    §2.5's three label-ish openers need new words; §2.6's four and §2.8's
    four are already full sentences and convert by dropping `- `.
Q2  Most of the 103 editable literals survive with ZERO prose care,
    because stripping leading whitespace from a wrapped body line cannot
    break a single-line literal. The at-risk set is the 3 multiline
    literals plus §2.5's 3 opener lines.
Q3  The l159 gate stays green untouched: it covers the abstract and §1
    only, and this stage edits neither. The long-sentence discipline is
    still self-imposed inside the span (no new sentence over 45 words).
Q4  §2.8 needs no opener re-authoring at all, so the diff there is pure
    de-indentation plus paragraph breaks — the cleanest of the three
    section groups despite carrying the table.
