# L174 stage (a) — PREREG: references pass + cited-work characterizations

Registered 2026-11-20 ~20:15 EST, BEFORE any fetch, any bib edit, any draft edit.
Card: LANE.md L174 (manuscript + figures + references pass, zero rollouts, do LAST).

## Scope (this stage only)

L174 is three independent passes. By dependency order the REFERENCE LIST must
exist before the prose pass can carry numeric citation markers, so this stage
takes:

- (a1) the reviewer's missing-citation list (Namiki, Stürner, Cheong, Braun,
  Cande, Azevedo, Lesser, Takemura, Eckstein, Liu & Wilson, Otchy, Wolff &
  Ölveczky, Jonas & Kording, Keinan, Fakhar & Hilgetag, Prinz, Beiran &
  Litwin-Kumar, Yan, Randi, von Reyn) + Sapkal + a DUCKOPHILA cite;
- (a2) the corrected ApproxBrain / FlyHack / Kopel characterizations, with the
  novelty contrast NARROWED because ApproxBrain does report single-interneuron
  necessity;
- (a3) in-text numeric citation markers (the adjudicated count today is 1).

OUT OF SCOPE for stage (a), seeded as L174 (b)/(c): the abstract rewrite and
<=1,920-char cap, bullets->prose, the Discussion section, the changelog/lane-code/
all-caps strip, and the three figure redraws. NO number in numbers.json changes,
NO measured claim is added, zero rollouts, zero RNG.

## Source-of-truth rules (binding)

- R1 PRIMARY ONLY. Every bibliographic field written into references.bib or the
  draft list is COPIED PROGRAMMATICALLY from a live primary API response
  (Crossref `api.crossref.org/works`, arXiv `export.arxiv.org/api/query`) stored
  raw under l174a/raw/. No field typed from memory. A reference I cannot match
  to a primary record is DROPPED from this pass and journaled, never guessed.
- R2 MATCH EVIDENCE. Each accepted record stores its query, the matched DOI/arXiv
  id, and a token-overlap score between the intended title and the returned
  title; acceptance needs score >= .6 AND an author-surname match.
- R3 VERSION HONESTY. Where a work exists as both preprint and journal article,
  the journal record is preferred (`type == journal-article`); if only the
  preprint record exists it is cited AS a preprint.
- R4 NO RENUMBER. Existing entries 1-13 keep their numbers (l149/l158 literal
  gates and CLAIM-MAP rows depend on the draft text around them); new entries
  append from 14.
- R5 The reviewer's own text (review_fable.md) is RAW MATERIAL: a name on their
  list is a lead to verify, never a citation to paste (L167 evidence rule).

## Certifications (run BEFORE any draft edit)

- CERT-1: all 13 existing references.bib entries re-resolved against a primary
  API; stored title/DOI compared to the bib file. A mismatch is reported, not
  silently corrected.
- CERT-2: the ApproxBrain / FlyHack / Kopel corrections are taken from OUR OWN
  stored digests in LANE-RESEARCH.md (grep-verified quotes), not from the
  reviewer's summary.
- CERT-3: numbers.json is byte-identical pre/post this stage (a reference pass
  may not move a measured value). Pre-tick copy taken FIRST.

## Branches (precedence, decided by the data)

1. **A2_approxbrain_necessity_confirmed** — our stored digest confirms
   ApproxBrain reports individual necessity of the three Pugliese interneurons
   over held-out draws. Then §1(a) must be REWRITTEN: the novelty contrast
   narrows to (i) emergent transition in an uncurated bulk-extracted subnet and
   (ii) the mass-twin control, and the words claiming they show "no
   sufficiency/necessity" leave the draft.
2. **A1_approxbrain_as_written** — the digest does NOT support it; the existing
   characterization stands and the card's instruction is answered with evidence.

Precedence: A2 > A1 (the stronger correction wins if the data supports it).

## Pins (checked, not assumed)

- P1: in-text numeric citation markers today == 1 (re-counted by the verifier
  before the pass, matching l167's adjudication cell).
- P2: after the pass every in-text marker [n] resolves to an existing numbered
  entry, and every numbered entry is cited at least once (bidirectional gate).
- P3: references.bib key count == draft numbered-entry count.
- P4: all five existing paper verifiers stay green; the abstract's l158 token
  freeze is untouched by this stage (no abstract edit).

## Verification

PREREG first (this file) -> fetch + CERT -> branch read -> draft/bib edits ->
NEW paper/l174_verify.py (bidirectional citation gate + characterization
literals + the retired wording asserted gone) -> all five existing verifiers ->
LAB-INTENT.md -> LANE.md -> digest push + byte-verify.
