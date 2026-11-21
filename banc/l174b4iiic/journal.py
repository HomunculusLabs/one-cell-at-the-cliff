#!/usr/bin/env python
"""Append the L174(b4-iii-c-i) journal section to peabrain-lab/LAB-INTENT.md
by ABSOLUTE path (the tick-152 split-cwd trap: a relative append from banc/
silently creates a stray file)."""
import pathlib, re

P = pathlib.Path('/home/t3rpz/critters/peabrain-lab/LAB-INTENT.md')
txt = P.read_text()
assert 'L174 (b4-iii-c-i)' not in txt, 'section already appended'
before = len(re.findall(r'(?m)^## ', txt))

SEC = """
## L174 (b4-iii-c-i) — the all-caps de-emphasis of §1 and §4 (tick 215, 2026-11-21)

Stage (b4-iii-c) was sliced THREE ways, and the slice is by KIND rather than
size. A fresh live census (`banc/l174b4iiic/census.py`) re-derived the
all-caps distribution after the (b4-iii-b) relabel and produced three facts
the card's one line did not anticipate:

1. §5 Discussion carries ZERO all-caps tokens of any class. Stage (b4-ii)
   wrote it in the lowercase house form, so §5 is this stage's STYLE
   REFERENCE, not its workload — and §(30) now pins it caps-free so a later
   stage cannot re-emphasise it.
2. §3 Methods is a different KIND of job. Four tokens there are MODEL SYMBOLS
   living inside the state equation and the parameter table (BG, DT, TAU,
   WIN — and tick 213's partition classified TAU and WIN at TOKEN level as
   NOTATION/STRIP), and one token splits by POSITION inside §3 alone: `CC BY
   4.0` the licence name versus `BY CONSTRUCTION` the emphasis. §3 also hosts
   the eleven KEEP_MAPPING codes, which must survive byte-exact. Deferred as
   slice (c-ii).
3. §2 Results is the bulk (89 strip + 36 class labels + 16 tokens needing
   fresh judgement). Deferred as slice (c-iii).

This slice therefore took §1 Introduction and §4 Limitations, where every
owned occurrence is unambiguous de-emphasis. Branch C1_deemphasis_only.

### Measured

64 declared occurrences lowered (26 in §1, 38 in §4), with the five
outcome-class labels becoming the lowercase defined terms §5 already uses.
The edit is PROVED CASE-ONLY over the whole draft: title-onward length
identical, exactly 412 differing bytes, every one an uppercase letter
replaced by its lowercase self. Visible-character and byte deltas are
therefore EXACTLY ZERO — a first for this lineage, whose earlier stages cost
+145/+48/+108/−14/−87/+40 — and both the measurement and citation-key
multisets are identical with NO named removal and NO named addition (tick 213
needed 15 named removed digit runs, tick 214 needed 11 named mapping rows).
§2 Results and everything from §5 onward are byte-IDENTICAL. KEEP survivors
are occurrence-pinned: §1 CPG, CPG-, IN12B003, S07, XOR; §4 BANC, BANC',
EMG, XOR.

### Four method contributions, all inheritable

1. **A literal harvest cannot see a gate built from a regex or a token
   list.** The first harvest found and re-pointed 16 broken verifier literals
   and reported clean — then two gates broke anyway: an
   `re.search(r'(?m)^DATA FLOOR:')` locator in l149 §(26)'s prose contract,
   and an `INTERMEDIATE` entry inside l158's required §1-map token list.
   Neither is a draft-quoting string literal in the harvest's sense. A strip
   or de-emphasis stage must scan the verifier SOURCES for its owned tokens,
   not only for their quoted literals.
2. **A whole-draft presence test cannot see a section-scoped gate.** The
   changelog banner QUOTES the edited prose, so `'UNIT OF INFERENCE'` stayed
   present draft-wide while the §4-scoped gate that reads it (`_lim172 =
   draft[draft.index('## 4. Limitations'):]`) failed. The second-order scan
   (`harvest2.py`) tests presence inside the EDITED SECTION RANGES — and also
   decodes escape sequences, a third blind spot: the first harvest's
   `"[^"\\n]*"` literal regex reads `'fully RE-DERIVED, not\\n  frozen'` as a
   two-character backslash-n that appears nowhere in the draft, so a real
   breakage looked clean. The scan over-reports on short tokens (`'PARTIAL'`
   used as a stored-artefact class name), so each hit is adjudicated by
   reading its USE, never applied blindly.
3. **Line-start is not sentence-start in a hard-wrapped draft.** The first
   transform rule treated a token at column 0 as sentence-initial and
   capitalised SEVEN mid-sentence wrap openers — "Fixed network" for a
   sentence that began on the previous line, and the same for SUFFICIENT,
   ORDER, SUFFICIENCY, MASS-, CARRIER, COSTS. The fixed rule reads the
   PREVIOUS line's ending (blank, heading, `.` or `:`), and the fix was
   applied by restoring the freeze and RE-RUNNING the parsed transform, never
   by hand-editing the draft — the parsed-not-typed discipline is what made a
   seven-site rule error a one-command repair.
4. **A global file-level replace cannot tell a live-draft quote from a
   stored-pre-image quote.** `emit.py`'s `str.replace` over l149_verify.py
   lowered the PRE-IMAGE side of a `_SPL_B4` pair (`'cutwA PARTIAL 3/16
   .371), and the f4ng-vs-f4tw'` quotes the (b4-i) stored span, which still
   carries the uppercase form), and the gate caught it with
   "split pre-image form not unique". Pre-image quotes must stay verbatim.
   Related: nested literals must be re-pointed LONGEST FIRST, or replacing
   the short form rewrites the long one's interior and the long form
   "vanishes" (caught on the first dry run).

### Gate

Permanent as `l149_verify` section (30): T15 case-only over the whole draft
(same length, 412 upper→lower byte differences, nothing else), the
out-of-scope byte identities computed TITLE-RELATIVE — an own-catch, because
the banner gains this stage's own entry and every absolute offset shifts —
the KEEP survivor sets for both edited sections, §5's caps-free pin, the
class labels in their house form, and both multisets. §(23), §(26) and §(29)
are re-pointed THROUGH this stage: their frozen literal pins now accept
case-insensitive images WITH the retired all-caps form asserted ABSENT, which
is strictly stronger than either check alone and is bounded by §(30)'s
whole-draft case-only proof. §(26) additionally pins §4's pre-strip caps
census (39 distinct / 45 occurrences) and its 7 surviving KEEP occurrences,
and declares that exactly ONE of its two bullet-marker locators was
de-emphasised so the exemption cannot silently cover a second label.

Six paper verifies green; `numbers.json` byte-identical (sha 238bf2d37f51).
DRAFT v3.31, CLAIM-MAP B42. Evidence `banc/l174b4iiic/`.
"""
P.write_text(txt.rstrip('\n') + '\n' + SEC)
after = len(re.findall(r'(?m)^## ', P.read_text()))
print(f'LAB-INTENT.md sections {before} -> {after}, bytes {len(txt)} -> '
      f'{len(P.read_text())}')
