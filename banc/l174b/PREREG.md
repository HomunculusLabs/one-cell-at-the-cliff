# L174 stage (b1) PREREG — the tick-204 novelty narrowing + references 36/37

Written BEFORE any fetch, any draft edit and any verifier change.
Zero rollouts, zero RNG, no graph build, no torch.

## Scope (what this stage is and is NOT)

L174 has three stages. (a) references, shipped tick 203. (b) the manuscript
prose pass. (c) the figure redraws. Stage (b) is itself too large for one
tick, so it is sliced here:

- (b1) THIS TICK: the MANDATORY field amendment of tick 204 — reference 36
  (Habib, Petr & Rust) and reference 37 (Matsliah et al.) added under the
  l174a PRIMARY-ONLY rule, the §1 novelty narrowing written as the four-way
  contrast the amendment specifies, the two limitation/convergence sentences
  the amendment requires, and the citation gate extended to cover them.
- (b2) NEXT: abstract <= 1,920 chars, bullets -> prose, a Discussion
  section, strip the changelog banner + lane/batch codes + the all-caps
  tokens, and reviewer I10's §2.4 compression.
- (c) LAST: the three figure redraws.

Out of scope this tick, asserted by the verifier: the Abstract block (the
v3.8 vocabulary freeze stays intact), every §2 results number, numbers.json,
and all three figures.

## Source-of-truth rules (inherited from l174a, restated)

- R1 PRIMARY-ONLY. Every bibliographic field of entries 36 and 37 is copied
  programmatically out of a live primary API response stored under
  `banc/l174b/raw/`. Nothing is typed from memory or from a search snippet.
- R2 ACCEPTANCE. A fetched record is accepted only if the title token
  overlap with our probe title is >= 0.60 AND at least one author surname
  from our digest appears in the record's author list.
- R3 bioRxiv's CURRENT DOI prefix is 10.64898 (the 10.1101/<date>.<id> form
  of the same identifier returns "no posts found"); the cite carries the
  record's own DOI and version.
- R4 Entries 1-35 are NEVER renumbered. New entries append as 36, 37.
- R5 Every FIELD number about another group's paper that enters the draft
  must appear verbatim in our own stored digest (LANE-RESEARCH.md), never
  from the record abstract alone and never from a search snippet.

## Certifications (all must pass BEFORE a draft line is edited)

- CERT-1: `paper/l174_verify.py` is ALL GREEN on the pre-edit draft (the
  stage-(a) gate is the baseline; a stage that starts red cannot attribute
  its own failures).
- CERT-2: the reference list has exactly 35 entries pre-edit and
  `references.bib` has 35 keys (count pin, so an append cannot silently
  overwrite).
- CERT-3: `paper/numbers.json` sha256 equals the pre-tick copy taken FIRST
  (`banc/l174b/numbers_pretick.json`), checked again at the end.
- CERT-4: every field number this stage splices is asserted present in
  LANE-RESEARCH.md (R5), by the verifier, not by eye.

## Branches (precedence declared)

- N2_record_differs (CHECKED FIRST, takes precedence): if either fetched
  record fails R2, or the Habib record's own title/abstract does not carry
  the focal-loss + cell-replacement + connectome-model-of-steering framing
  our digest attributes to it, then the narrowing is NOT written this tick:
  journal the mismatch as a blocker, leave §1 alone, and re-open the card.
- N1_identity_prior_art_confirmed: records accepted -> write the narrowing
  exactly as the tick-204 amendment specifies, i.e. (i) matching currency
  (count vs mass), (ii) resolution (class vs one cell + one mass twin),
  (iii) readout (decoded behavioural scalar through a hand-built open-loop
  controller vs an emergent in-network structure statistic), (iv) direction
  and substrate (remove-then-add on male CNS vs removal on the female
  cord), with the cite SCOPED as type-dependent integration because 89 of
  their 100 matched cells copy a reflected same-type neighbour.

## Pins

- P1: reference entries 35 -> 37; bib keys 35 -> 37; numbering contiguous.
- P2: `l174_verify.py` in-text marker tokens >= the entry count, uncited 0.
- P3: the Abstract block is byte-identical pre/post (sha256 pin), so the
  l158 freeze cannot be disturbed by this stage.
- P4: no sentence I add to §1 or §4 exceeds 60 words (l159 gate).
- P5: §1's "gap this paper fills" paragraph must no longer claim novelty for
  identity-over-count as such; it may claim only the narrowed contrast.

## Predictions (scored, not assumed)

- Q1: the bioRxiv details API returns the Habib record under
  10.64898/2026.10.26.762043 with a version >= 1 and a 2026-10 date.
- Q2: the Matsliah record is version 2 and licensed CC-BY-ND (our digest
  disclosed an abstract-level read for that reason); if the licence field
  says otherwise, the disclosure line is corrected rather than kept.
- Q3: `l174_verify.py` gate (6) will need the tick-204 numbers added; the
  gate must FAIL first on the new strings and pass only after they are
  listed, proving the gate is live rather than decorative.
