# L174 stage (b3b-iii) — PREREG (bullets -> prose, §2.7)

Written BEFORE any draft edit. Tick 210, 2026-11-21.
Zero rollouts, zero RNG, no graph build. The only compute is string
arithmetic over the stored draft and the six stored verifier sources.

## Scope

Stage (b3b) was sliced by section group in tick 208 after measuring the
per-section bullet census: (b3b-i) §1 + §2.1 + §2.2 + §2.3 = 15 bullets
(SHIPPED tick 208), (b3b-ii) §2.5 + §2.6 + §2.8 = 11 (SHIPPED tick 209),
(b3b-iii) §2.7 = 16 bullets (THIS TICK, the final and heaviest slice: the
pre-posting controls carry the largest citation-key load in the body).
The census is RE-DERIVED this tick, not inherited.

EDIT SPAN (T4): the exact draft slice from `### 2.7 Pre-posting controls`
through the character immediately before `### 2.8 The slow line`, frozen
byte-exact as `span_pre.txt` per the tick-207 ADDENDUM 2 lesson (freeze the
EXACT slice, never a re-joined line list). This stage needs NO frozen
sub-slice: tick 209's instrument existed only because §2.7 sat inside that
tick's natural span. Here the span is §2.7 itself.

NOTE on structure: §2.7 already contains two BOLD-LEAD paragraphs (stage c2
and stage d openers) and its three bullet groups hang off three different
lead paragraphs. The groups are treated as three independent unit groups so
a paragraph boundary cannot migrate between them.

## Contract

T1  FORMAT-ONLY, and provably so: the span's NUMERIC TOKEN MULTISET and its
    CITATION-KEY MULTISET must be IDENTICAL before and after. Inherited from
    (b3b-i)/(b3b-ii) unchanged — a bullets-to-prose pass has no business
    moving a number or a citation key, so the allowed delta is the empty
    set. Any needed exception is a PREREG ADDENDUM written before the
    splice. Pins are recorded by harvest.py below.
T2  No number enters that numbers.json does not already carry — satisfied
    vacuously by T1 (no number enters at all).
T3  Every verifier literal that currently lives in the span survives
    VERBATIM, and no verifier may be edited to make a prose choice pass.
    ONE declared exception class, inherited: a literal whose match depends
    on the OLD BULLET INDENTATION (a literal containing `\n` plus
    continuation spaces) cannot survive de-indentation by construction. For
    these the gate is made WRAP-INSENSITIVE (assert against a
    whitespace-normalized view) rather than re-worded — claim text
    unchanged, and the normalization makes the loop STRICTLY stronger
    because a literal can no longer hide behind a different wrap. The
    exception set must be EXACTLY the set harvest.py declares BEFORE the
    rewrite; any other literal failure is a real failure fixed in the prose.
T4  The span above is the only part of DRAFT.md this stage may edit, proven
    by a single-block substitution `d[:i] + new + d[j:]` after asserting
    `d[i:j] == span_pre.txt`. emit.py refuses a second run.
T5  The six paper verifies stay green, and the span's bullet census drops
    from 16 to 0. With that the whole §1-§2 bullet census reaches 0 and
    stage (b3b) is complete.
T6  The two existing bold leads survive VERBATIM and remain at paragraph
    starts; the closing scope paragraphs (the "Scope:" paragraph, the
    "Design pins" paragraph and the stage-(d) completion paragraph) are not
    bullet blocks and must come through byte-unchanged.

## Certification (before any edit)

CERT-1  All SIX paper verifies green on the PRE-edit draft, stored under
        raw/cert1_*.txt. A stage that starts red cannot attribute its own
        failures. [DONE: six exit 0.]
CERT-2  numbers.json copied FIRST to numbers_pre.json and asserted
        BYTE-IDENTICAL at the end. [DONE: sha 238bf2d37f51, the inherited
        value.]
CERT-3  The span frozen as the EXACT draft slice; emit.py asserts the live
        span equals the freeze before splicing and refuses a second run.
CERT-4  The transform is PARSED, not typed: bullet blocks are found by
        regex, every opener is matched to exactly one declared rewrite-map
        entry, and the run fails on any unmapped block or unused entry.
        Openers that are already full sentences declare `new=None` and the
        PARSER strips the `- ` (tick-209 de-dash-by-parser contribution),
        so nothing that needs no re-authoring is retyped.

## Branches (precedence order, checked in this order)

B2_tokens_moved   (CHECKED FIRST) — the numeric or citation-key multiset
    differs before/after. This is the failure that silently weakens the
    paper, so it is read before any success branch. Action: restore the
    frozen pre-image, report the delta, no splice stands.
B1_format_only    — both multisets identical, census 16 -> 0, all literals
    verbatim except the declared indentation class, six verifies green.
B3_literal_lost   — a literal outside the declared exception class fails.
    Action: fix the PROSE, never the gate.

## Predictions (scored in the log either way)

Q1  VISIBLE (whitespace-stripped) character count rises by +50..+400: the
    openers that need authoring gain subjects and verbs, the rest are
    de-indented. RAW chars fall (de-indentation removes two spaces per
    continuation line) — tick 208 scored a raw-direction prediction WRONG
    for exactly this reason, so the honest measure is the visible delta.
Q2  The multiline-literal exception set is SMALL (0..5) and is fully
    predicted by the harvest before the rewrite.
Q3  l159 (no sentence over 60 words) stays green without re-splitting any
    inherited sentence: de-dashing does not lengthen sentences, and any
    authored opener is written under 45 words.
Q4  A MAJORITY of the 16 openers are already full sentences and therefore
    declare `new=None` (the tick-209 rate was 8 of 11).
Q5  §2.7 carries the heaviest citation-key load of the body, so this span's
    citation-key multiset is larger than (b3b-ii)'s 37.

---

## ADDENDUM 1 (written BEFORE any draft byte changed)

**A1-a. The T3 exception set is SEVEN, not the 0..5 Q2 predicted.**
harvest.py found nine multiline verifier literals in the span. TWO of them
(`"carrier's\n80"`, `'6 shared, Jaccard\n.037'`) live in the non-bullet
"Design pins" paragraph, which this stage passes through as raw lines, so
they are NOT at risk and are not exempted. The remaining SEVEN sit inside
bullet bodies and carry the OLD BULLET INDENTATION inside their own line
break, so they cannot survive de-indentation by construction:

    l149 (11)   'follows the\n  GRAPH, not the gain'
    l149 (15i)  'differ per seed by up to\n  .46'
    l149 (16i)  'meanR\n  .798, kR 16/16, [.806,1.000]'
    l149 (16i)  '(.477, kR 8/16,\n  [.280,.720])'
    l149 (16i)  'meanR .651, kR 15/16,\n  [.717,.989], paired −.147'
    l149 (16i)  '+.474 above the twin-removed\n  graph with 16 of 16 seeds up'
    l149 (16i)  'at g_cutng25p it is +.174 with 12 of\n  16 up'

All seven are in l149_verify.py and in exactly three loops — section (11)'s
`_s27`, (15i)'s `_s27b` and (16i)'s `_s27d` prose contracts. Those three
loops are made WRAP-INSENSITIVE (matched against a whitespace-normalized
view) rather than re-worded, exactly as tick 209 did for §2.6's three: the
claim text is unchanged and the gate becomes STRICTLY stronger, because a
literal can no longer hide behind a different wrap. Q2 is scored WRONG and
the reason is structural — §2.7 is the most number-dense subsection in the
body, so more of its gate literals straddle a line break.

**A1-b. Sentence-length discipline inside the span, and a new gate for it.**
l159_verify scans the ABSTRACT and §1 ONLY, so the >60-word rule has never
covered §2. Measured on the frozen pre-image, §2.7's longest sentence is the
stage-(d) anchors bullet at 67 words (68 counting the dash). A bullet can
carry that; a prose paragraph should not, and this stage is what turns it
into one. Registered here, before the splice:

  * that one block (and only that one) is re-authored over its FULL body
    (`eat` consumes every body line) and split at its existing clause
    boundaries into three sentences, no token moved — T1 still binds;
  * the next-longest, the stage-(c2) anchors sentence at 48 words, is left
    INTACT and disclosed rather than quietly rewritten;
  * a NEW permanent gate asserts no sentence in §2.7 exceeds 60 words, so
    the discipline l159 cannot see for §2 is enforced for this section from
    now on. Registered expectation: longest §2.7 sentence <= 55 words after
    the pass.

**A1-c. Q4 is expected to fail and is scored as it falls.** Q4 predicted a
MAJORITY of openers would need no authoring (tick 209 ran 8 of 11). §2.7's
openers are overwhelmingly `Label [key]: clause` fragments — the census of
the frozen pre-image shows only three full-sentence openers (blocks 3, 13,
14). This is recorded as a property of the SECTION (a controls catalogue
written as a table of verdicts), not as a miss in the machinery.
