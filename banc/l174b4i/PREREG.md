# PREREG — L174 stage (b4-i): §4 Limitations, bullets -> prose + a prose-discipline gate

Written 2026-11-21 06:0x EST, BEFORE any draft byte changed, BEFORE the
harvest ran and BEFORE any rewrite was authored. Tick 211 of the peabrain
lane. Zero rollouts, zero RNG, no graph build: the only compute is string
arithmetic over the stored draft and the six stored verifier sources.

## Why this slice, and the census it is derived from

Stage (b3b) is COMPLETE (ticks 208/209/210): §1-§2 carries no bullet list.
The card's remaining (b4) text names FOUR jobs — a Discussion, the §4/§5/§6
bullets, the body-wide lane/batch-code + all-caps strip, and the 40-line
changelog banner (LAST) — plus one inherited debt (the 70-word §2.8
sentence). Those are not one tick.

Census RE-DERIVED this tick from the live draft (house rule: never inherit a
count from a summary sentence — L44):

    §3 Methods           0 bullet lines
    §4 Limitations      10 bullet lines   <- THIS TICK
    §5 Data & code       4
    §6 Author/submit     1
    Verification         2

and the sentence-length scan of §4 (flattened per bullet block) returns
SEVEN sentences over 60 words: 107, 77, 72, 68, 66, 65, 65.

So (b4) slices as:
  (b4-i)   THIS TICK — §4's ten bullets -> prose, and the seven over-length
           sentences the conversion drags into prose, under a new permanent
           §4-scoped sentence gate.
  (b4-ii)  the Discussion + the inherited 70-word §2.8 sentence.
  (b4-iii) the body-wide lane/batch-code + all-caps strip.
  (b4-iv)  the 40-line changelog banner (LAST, per the card).

§5/§6 are deliberately NOT in this slice and the PREMISE for touching them
at all is tested in (b4-iii): §5 is a data-availability section (a list is
journal house style there) and §6 is not a manuscript section at all (author
notes to the owner). Nothing is converted on the strength of the card's
summary phrase alone.

## Contract (inherited from (b3b-i)/(b3b-ii)/(b3b-iii), unchanged)

- T1 FORMAT-ONLY, allowed delta EMPTY: the edited span's numeric-token
  multiset and citation-key multiset must be IDENTICAL before and after.
- T2 no new number may enter the draft.
- T3 every verifier literal inside the editable text survives VERBATIM, with
  ONE declared exception class — literals whose match depends on the OLD
  BULLET INDENTATION (a line break with two leading spaces inside the literal
  itself). The exception set is enumerated by the harvest BEFORE the rewrite
  and the owning verifier loops are made WRAP-INSENSITIVE (claim text
  unchanged, strictly stronger). NO verifier may be edited to make a prose
  choice pass.
- T4 single-block substitution: one span, frozen as the EXACT draft slice
  (tick-207 ADDENDUM 2), asserted equal to the freeze before splicing;
  emit.py refuses a second run.
- T5 all six paper verifies green after, and the §4 bullet census 10 -> 0.

## NEW this stage: T7, the sentence-split contract

Seven sentences over 60 words live in §4 BODY text, not in openers, so the
(b3b) opener-rewrite map cannot reach them. Each is split at its OWN clause
boundaries by a declared (old, new) pair applied to the joined paragraph text
before reflow, and each pair must satisfy, by assert:

  (a) `old` occurs EXACTLY ONCE in the span pre-image (normalized);
  (b) the numeric-token and citation-key multisets of `old` and `new` are
      identical (a local check, strictly stronger than T1's span-wide one);
  (c) the alphanumeric word sequence of `old` is a SUBSEQUENCE of `new`'s —
      nothing deleted, nothing reordered — and the EXTRA words are exactly
      the connectives declared for that split. No content word may be
      invented and no number may move.

Punctuation and capitalization are the only free edits. This is the same
discipline tick 210 used for §2.7's single 67-word sentence, promoted to an
instrument with an explicit subsequence proof.

## The new permanent gate, and its disclosed exception

l159_verify scans the ABSTRACT and §1 only; tick 210 added a §2.7-scoped
60-word rule when de-bulleting moved text into that blind spot. This stage
extends the rule to §4 the same way (new l149_verify section), and because
the blind spot is now mapped, the gate also PINS the one known pre-existing
offender outside its own span — §2.8's 70-word envelope-disclosure sentence
— as a DISCLOSED exception with its word count asserted, so (b4-ii) closing
it is gate-visible rather than silent. Disclose-and-leave-intact, never
quietly rewrite material another stage owns (tick-210 rule).

## Branches (precedence top-down)

- B2_tokens_moved — any numeric or citation token enters/leaves the span, or
  a T7 subsequence proof fails. STOP, restore the freeze, report the breach.
- B3_literal_lost — a harvested verifier literal is lost outside the declared
  wrap-fragile class. STOP, restore, report.
- B1_format_only — the conversion lands with both multisets identical, every
  literal verbatim or declared-exempt, census 10 -> 0, zero sentences over
  60 words in §4. SHIP.

## Predictions (scored in the log, wrong predictions reported as wrong)

- Q1 visible-character delta (whitespace-stripped) is POSITIVE, +50..+600:
  de-bulleting removes indentation (raw chars may fall) while sentence
  splitting adds connectives.
- Q2 the wrap-fragile exception class has 3..9 members (§2.7 had 7, §2.6 had
  3; §4 is number-dense and heavily indented).
- Q3 l159_verify is untouched and stays green (it does not scan §4).
- Q4 a MAJORITY of the ten openers need no authoring (de-dash only): §4's
  bullets read as full sentences more often than §2.7's verdict catalogue.
- Q5 the seven splits need fewer than 25 inserted connective words in total.

## CERT (before any edit)

- CERT-1 all SIX paper verifies green on the PRE-edit draft, stdout stored
  under raw/cert1_*.txt.
- CERT-2 numbers.json copied FIRST with its sha256 recorded, and asserted
  BYTE-IDENTICAL at the end of the tick.
- CERT-3 the span frozen as the EXACT draft slice; emit.py asserts the live
  span equals the freeze before substituting and refuses a second run.
- CERT-4 the transform is PARSED, not typed: bullet blocks found by regex,
  every opener matched to exactly one declared map entry, no unmapped block
  and no unused entry; tables get their own unit type (tick-209 lesson) and
  any frozen region is tested by RANGE MEMBERSHIP, never a one-sided bound.

## ADDENDA

ADDENDUM 1-a (written PRE-SPLICE, from the harvest). The T3 exception class
has THREE members in this span, all l149 literals carrying the old bullet
INDENTATION inside their own line break: 'fully RE-DERIVED, not\n  frozen',
're-ordering rather than\n  turnover' (both in the §4 floor-4 contract loop,
now checked normalized) and 'the unit of inference\n  is the simulation
realization' (l174_verify, already wrap-insensitive — no edit needed).

ADDENDUM 1-b (written PRE-SPLICE, from the harvest). A SECOND exception class
not seen in (b3b): two literals contain the BULLET MARKER itself, '- DATA
FLOOR:' and '- Wet-lab predictions'. They are not content checks — they are
l149 SLICE LOCATORS for the §4 floor-4 contract — so they are re-pointed at
the prose form anchored to a LINE START with re.M. That is equally strong
(the labelled paragraph must still open its own line, and a locator that was
previously satisfiable anywhere in the file can no longer match mid-sentence),
not a loosening. Declared here so the exemption cannot be invented later.

ADDENDUM 2 (written PRE-SPLICE, during the dry run). The numeric regex
swallows a TRAILING COMMA, which it must for thousands separators like
2,676,592. A clause boundary that legitimately turns '10-15, and' into
'10-15. The' therefore reads as a CHANGED numeric token. Trailing commas are
punctuation, which T7 is allowed to edit, so every numeric multiset in this
stage is compared with trailing commas stripped; the DIGITS of every token
still compare exactly.

ADDENDUM 3 (written POST-SPLICE, disclosed as such — it strengthens the
permanent gate, it does not relax any registered bar). emit.py proved T7(c)
PER SPLIT, which is structurally blind to word-level edits made anywhere else
in the span — and this stage makes two, the authored openers T1/T3 allow. The
permanent gate's whole-span content-sequence form went RED on its first run
because of exactly that, and was re-formed as: the frozen pre-image with all
THIRTEEN declared edits applied (11 splits + 2 authored openers) must
reproduce the live section's content-word sequence exactly. That is strictly
stronger than what was registered. Transferable: a per-edit invariant is not
a per-section invariant, and the section-level form is the one worth making
permanent.

ADDENDUM 4 (written POST-SPLICE, gate construction). The §2.8 disclosed
exception must be measured PER PARAGRAPH with table paragraphs excluded: read
flat, §2.8's robustness-panel table becomes a 115-token pseudo-sentence and
masks the real 70-word offender (the tick-209 lesson — a markdown table is
the one prose object a flat read destroys — now in a sentence-metric form).
