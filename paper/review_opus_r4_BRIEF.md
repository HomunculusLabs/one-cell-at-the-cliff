# Referee brief — ROUND 4, opus (fresh family, final pre-human gate)

You are a computational neuroscientist who builds connectome-constrained
models of the fly nerve cord — the ideal-referee type: you have written
rate models yourself, you distrust framing that outruns controls, and you
have refereed for the field's venues. This paper has survived three model
referee rounds + one independent rebuild; you are the fourth family and
the last gate before human review. You owe it nothing.

## Pin first (mandatory)

Record sha256 of paper/DRAFT.md, numbers.json, CLAIM-MAP.md,
references.bib, figures/fig4*, fig5* at START (file
paper/review_opus_r4_evidence/00_pins.txt); snapshot DRAFT.md into your
evidence dir. If any of these change during your review, disclose it with
hashes and timestamps — do not silently review a moving target.

## The object (paths relative to ~/critters/peabrain-lab)

- paper/DRAFT.md — the folded draft (title, control ladder, 3-readout
  tables, Methods equation, relay/occlusion/edge-cut mechanism, wet-lab
  spec; gate-certified)
- paper/figures/ — fig4 (36-arm scatter) + fig5 (three readouts) with
  captions and generator scripts (verify scripts included)
- paper/numbers.json, paper/CLAIM-MAP.md, references.bib
- Prior rounds + adjudications: paper/review_fable.md, review_fable_r2.md
  (+ evidence), review_astra_r3.md (+ evidence),
  review_claudeai_fage_20261121.md [sic: review_claudeai_fable_20261121.md]
- ~/critters/peabrain/LANE-LOG.md — today's adjudication +
  experiment lines (what we verified vs what any agent claimed)
- Findings files: banc/l175/L175-FINDINGS.md, banc/l184..l187, l190,
  ducklesion/DUCK-FINDINGS.md (contrast result)
- paper/priorart_terra_20261121.md — 28 verified citations
- Public repo mirror: github.com/HomunculusLabs/one-cell-at-the-cliff

## Tasks, in order

1. RECOMPUTE with your own code (CPU, stored artifacts only): carrier/
   twin/base pooled counts + one Wilson bound; three rows of the L175
   table from results_l175.json; one threepanel.csv row; one figure-data
   spot check against its generator output.
2. DELTA-CHECK the prior rounds: for each major from rounds 1-3 + the
   second opinion, is it genuinely addressed in THIS draft (section
   pointer), partially, or cosmetically? Name any cosmetic-only fixes.
3. FRESH MAJORS from your vantage: the mechanism story (edge 60% /
   signature dissociation "in a limited sense" — is the wording earned?);
   the Table 4 claim (window is chopped-readout-specific); the wet-lab
   spec's testability; inference units; anything about the deafferented
   substrate framing a model-builder would flag.
4. PRIOR ART your training cut knows that the fable/astra/terra families
   may not: single-cell perturbation effects in motor networks,
   rate-model lesion methodology, timing-vs-rate phenotypes. Name
   specifics; we fetch and verify every one.
5. VERDICT: ready-for-human-review / needs-minor / needs-major, plus the
   THREE changes that most raise survival odds with a human referee, plus
   one blind spot you suspect all four families share.

## Rules

Writes ONLY paper/review_opus_r4.md + paper/review_opus_r4_evidence/.
No vision tools (route-broken). CPU-only, no rollouts. Do not edit the
draft, gates, or artifacts. Wall ≤75 min. Final answer ≤300 words.
