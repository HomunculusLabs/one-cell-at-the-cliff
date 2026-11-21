# PREREG — L174 stage (b4-iii-a): the lane-ID / internal-artifact strip + the §6/§7 premise test

Written BEFORE any draft byte changed. Tick 213, 2026-11-21.
Pre-edit pins: DRAFT.md sha256 6fe70fbaf11fddbde2861b5f57ad11b2ee25fe8122a0c2c9903eec8b61ca92cf,
numbers.json sha256 238bf2d37f51…, CERT-1 six verifies exit 0 (raw/cert1_*.txt).

## 0. Why this stage is a SLICE, and the census that forced it

Census RE-DERIVED this tick (census.py, caps.py — never inherited from the card):
the card's one line "strip … lane/batch codes and 81 all-caps tokens from the body"
measures, on the live v3.28 draft, as THREE disjoint jobs of very different shape:

| job | scope | size |
|---|---|---|
| (b4-iii-a) THIS TICK: lane IDs + internal-artifact references | §1–§6 + References preamble | 12 declared edit sites |
| (b4-iii-b) batch codes B## | §1, §2, §4 | 22 occurrences, 14 distinct |
| (b4-iii-c) all-caps emphasis | §1–§4 | 310 occurrences, 179 distinct |

They are NOT one job. A lane ID carries nothing to a reader and is DELETABLE.
A batch code carries real information (which paired comparison was run
within which batch) and therefore needs a reader-facing RELABEL plus a
Methods mapping — a deletion would destroy a disclosure, which T1 of every
stage in this lineage forbids. An all-caps token needs a per-token judgement
(acronym vs identifier vs emphasis) before anything may be touched. So this
tick ships (a), DERIVES AND FREEZES the classification instrument (b4-iii-c)
needs, and leaves both applications to their own stages.

## 1. The premise test (3rd+ deliberate use of the (b1) split)

The card's stage text says the strip "also owns §5/§6's remaining bullets".
Those sections are now §6 Data & code (4 list items) and §7 Author/submit
notes (1). PREMISE, measured by reading them rather than the card summary:

- §6 Data & code is a DATA-AVAILABILITY list. Every venue this draft targets
  wants it as a list; converting it to prose would make it worse, not better.
  NOT CONVERTED — registered as a premise finding.
- §7 Author/submit notes is not a manuscript section at all: it names the
  owner, assigns venue choice to him, and carries "TODO before review".
  NOT CONVERTED, and declared OUT OF MANUSCRIPT SCOPE for every remaining
  strip stage — a block that will not be submitted cannot owe a reader
  anything.

Consequence registered here so it cannot be read later as an oversight: §7's
two lane IDs (L152 ×2) SURVIVE this strip by declaration, and the gate
asserts §7 is byte-UNCHANGED rather than clean.

## 2. Scope, declared with reasons

IN SCOPE — §1 Introduction through §6 Data & code, plus the References
preamble paragraph: every lane ID matching `\bL\d{2,3}\b` and every
internal-artifact reference (`LANE-RESEARCH.md`, "the lane log", "lane
scripts").

OUT OF SCOPE, each with its reason and each asserted BYTE-UNCHANGED:
1. the pre-§1 Title block (lines 403–425) — title alternates plus a
   retirement rationale: editorial apparatus of the same class as the
   changelog banner, owned by (b4-iv);
2. §7 Author/submit notes — the premise finding above;
3. batch codes B## — stage (b4-iii-b);
4. all-caps tokens — stage (b4-iii-c);
5. the provenance keys `[l1NN.field]` — NOT internal codes in the relevant
   sense: they are the by-value trace table's resolvable keys (l158 §(6)
   asserts every one of them against numbers.json) and the card never asked
   for them.

## 3. Contract (inherits (b3b)/(b4-i) unchanged where it applies)

- **T1 STRIP-ONLY.** The allowed delta is exactly the declared removals plus
  their minimal grammatical repair. The WHOLE DRAFT's numeric-token multiset
  and citation-key multiset must be IDENTICAL before and after. A lane ID is
  not a numeric token under the harvest's regex (`L139` is not a number), so
  this is a real constraint, not a tautology.
- **T4' DECLARED SPARSE EDITS.** This stage is not a single-block
  substitution: the sites are scattered. So each edit is a declared
  `(old, new)` pair that must match EXACTLY ONCE in the frozen pre-image,
  whose `new` form must not already occur, applied against the frozen slice.
  emit.py refuses a second run.
- **T7-STRONG content-word sequence.** pre-image + declared edits == live,
  over the WHOLE draft, with content words = every alphanumeric token outside
  the closed connective set used by (b4-i). A content word may not enter,
  leave or move except as the declared pairs say.
- **T3 literals.** Every verifier literal verbatim, with any exception
  DECLARED FROM THE HARVEST BEFORE the rewrite (tick-206/208 rule). No
  verifier may be edited to make a prose choice pass; a locator may be
  re-pointed only to an equally strong form.
- **T10 ZERO-RESIDUE.** After the edit, the regex finds ZERO lane IDs and
  zero internal-artifact references in §1–§6 + the References preamble, AND
  every out-of-scope range is byte-unchanged.
- **T11 PARTITION (the instrument (b4-iii-c) inherits).** The stored caps
  classification must PARTITION all 179 distinct tokens: keep ∪ strip = all,
  keep ∩ strip = ∅, every member reasoned by class. ZERO caps tokens are
  applied this tick; the gate asserts the caps occurrence count is UNCHANGED,
  so a derivation stage structurally cannot leak into an application.
- **T5** six verifies green after.

## 4. Branch precedence (failure-first)

1. `S3_literal_lost` — any verifier literal lost without a declared, equally
   strong re-point.
2. `S2_content_moved` — T7-strong or either multiset fails.
3. `S1_strip_only` — all edits applied, multisets identical, out-of-scope
   byte-unchanged, zero residue.

Checked in that order; the failures are checked first because a silent
content loss is the failure that weakens the paper while looking like a win.

## 5. Declared edits (12)

Each is `(old, new)`; the parenthetical-drop form removes the lane
parenthetical and nothing else.

1. §2.5 heading: drop ` (L139)`
2. §2.6 heading: drop ` (L138, L170)`
3. §2.6 prose: `and after L169 (b2) we do not assume a static` → `and we do
   not assume a static` — the lane ID is the only pointer in that clause and
   it points at a stage, not a section, so it is DELETED rather than
   re-pointed; re-pointing it at §2.7 would assert a correspondence
   (L169(b2) ≠ §2.7's stages a–d) the draft has not established. Disclosed.
4. §2.7 heading: drop ` (L169 stages a–d)`
5. §2.7 prose: `is the\nL172 statistics pass` → `is the\n§2.9 statistics
   pass` — here the lane ID DOES function as a section cross-reference and is
   re-pointed, not deleted.
6. §2.8 heading: drop ` (L156, L157, L162, L171)`
7. §2.8 prose: `with L162's evoked phase lock` → `with the evoked phase lock`
8. §2.8 prose: `recorded in\nthe lane log` → `recorded in\nthe project log`
9. §2.9 heading: drop ` (L172)`
10. §1 prose: `logged in\nLANE-RESEARCH.md 2026-11-18` → `run on\n2026-11-18`
11. §6: `lane scripts + PREREG chain` → `analysis scripts + the
    preregistration chain` (the one caps token this stage touches, declared,
    because it sits inside a lane-vocabulary edit)
12. References preamble: drop ` (L152)`

## 6. Predictions (scored in the log, wrong answers reported as wrong)

- **Q1** visible-char delta NEGATIVE, in −60…−200. This is the first stage of
  the lineage whose job IS deletion; (b4-i) already broke the
  positive-delta streak at −14 by splitting sentences.
- **Q2** ZERO verifier literals need exemption: lane IDs sit in heading TAILS
  (all heading locators are prefixes) and prose parentheticals.
- **Q3** l159 stays green and untouched — deletion cannot lengthen a
  sentence.
- **Q4** the caps partition puts ≥120 of the 179 distinct tokens in STRIP.
- **Q5** no verifier locator needs re-pointing for the four heading edits.

---

## PREREG ADDENDUM 1 (written at the failing assert, BEFORE any draft byte changed)

T1 as registered compared the numeric-token multiset with the harvest regex
this lineage has used since (b3b): `[-+]?\d[\d,\.eE+\-/]*`. That regex has no
left word boundary, so it matches the DIGITS INSIDE an identifier — `L139`
contributes the token `139`, `B30` contributes `30`, `v3.28` contributes
`3.28`. A stage whose entire job is deleting identifiers therefore fails T1
BY CONSTRUCTION, and the claim the gate was meant to protect (no MEASUREMENT
enters or leaves) is not the claim it was testing.

Re-formed, strictly more honest in both directions:

1. §-references are stripped before the harvest. This is not new: it is the
   house form (b4-ii) registered for its own no-new-number proof, and it is
   required here because declared edit 5 re-points a lane ID to a section
   cross-reference (`L172` → `§2.9`), which must not read as a new
   measurement.
2. A numeric match IMMEDIATELY PRECEDED BY A LETTER is an identifier-internal
   digit run (`L139`, `B30`, `DNp33`, `v3.28`) and is excluded from the
   measurement multiset.
3. Those excluded runs are not simply dropped from view: the gate ALSO
   asserts the exact multiset of identifier digit runs that left the scope
   equals the declared lane IDs, so the strip is accounted for by name
   rather than hidden behind a loosened regex.

Nothing about the content-word (T7-strong) or citation-key legs changes.

## PREREG ADDENDUM 2 (dry run, before any draft byte changed)

The declared-edit list of §5 was HAND-BUILT from the context scan and was
INCOMPLETE: it missed `(L168)` at the end of §2.2's bold lead
(`**Scramble controls: sufficient, not unique — and set-dependently so
(L168).**`). T10, which asserts that the regex finds ZERO residue rather than
that the declared edits were applied, failed on the dry run and named the
token. Declared edit 13 is added (drop ` (L168)`), and `168` joins the
identifier-digit accounting.

The transferable rule, and the reason T10 was registered in this shape: a
strip stage must gate on RESIDUE, never on its own enumeration of sites. The
enumeration is exactly the artefact most likely to be incomplete, so a gate
that only re-checks the declared list can never catch the site the author did
not see.

## PREREG ADDENDUM 3 (dry run, before any draft byte changed)

T11 as registered ("the caps occurrence count is UNCHANGED, so a derivation
stage cannot leak into an application") is self-contradictory on this stage:
the caps regex also matches the DEFER_LANE class (`L139` … `L172`) and the
`LANE-RESEARCH` member of NOTATION, which are precisely the tokens
(b4-iii-a) removes. Re-formed by READING THE STORED PARTITION instead of
counting blindly:

- every caps token whose stored class is NOT `DEFER_LANE` and which is not
  `LANE-RESEARCH` must be occurrence-identical before and after — so the 139
  STRIP members, the 18 KEEP members and the 12 DEFER_BATCH members are all
  provably untouched by this stage;
- every `DEFER_LANE` member must fall to ZERO occurrences.

This is strictly stronger than the registered form: it does not merely show
a count did not move, it shows WHICH classes may not move and that the one
class this stage owns moved to completion.
