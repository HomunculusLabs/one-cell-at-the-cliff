# Referee brief — ROUND 3, CROSS-FAMILY (gpt-6.2-astra, owner-dispatched 2026-11-21)

## Why you, why now
Rounds 1 and 2 of model-refereeing were both claude-fable-5-2 (API dispatch),
plus one claude.ai-hosted fable second opinion (owner-pasted). All three
converged on the same core findings — but they are the same model family,
so family-shared blind spots are a live concern. You are a DIFFERENT family,
dispatched deliberately. You owe this paper nothing but honesty.

## What exists now (read these; all paths relative to ~/critters/peabrain-lab)

- `paper/DRAFT.md` — the preprint draft (v3.8+; Methods/abstract known
  issues are being repaired by the lab's own lane, NOT yet in this draft —
  review what is there)
- `paper/numbers.json`, `paper/CLAIM-MAP.md` — ledger + claim→artifact map
- `paper/review_fable.md` — round-1 referee report (12 majors)
- `paper/review_fable_r2.md` + `paper/review_fable_evidence_r2/` — round-2
  report (major revision; silent-twin, Methods mismatch, unchopped
  selectivity, paired-p, pooling) + full recomputation evidence
- `paper/review_claudeai_fable_20261121.md` — independent claude.ai fable
  second opinion (own reimplementation from raw tables; its own 56-cell
  fixed-gain scan; found Alstott 2009 prior art we had missed)
- `LAB-INTENT.md` §L175 + `LANE-LOG.md` (in ~/.hermes path below) — our
  adjudication of every round-2 claim (7/7 CONFIRMED under our tree, code
  + probes rerun) and the experiment dispatches
  - lane log: ~/critters/peabrain/LANE-LOG.md
- `banc/l175/` — THE NEW EXPERIMENTS (single-cell scan + drive-matched
  twin), PREREG-first, gain-re-matched per arm, 16 seeds; check
  `banc/l175/verdict_l175.out` / `results_l175.json` — if the run shows
  FINAL=True, analyze it fully; if still partial, say so and analyze the
  rest
- `banc/l135/`, `banc/l150/`, `banc/l169*/` — certified lineage arms +
  raw anchor traces; `banc/banc_graph.pt` — the substrate
- Public repo (same content): github.com/HomunculusLabs/one-cell-at-the-cliff

## Tasks, in order

1. **Independent recomputation (your own code, CPU-only):** pick at least
   the carrier/twin/base pooled counts and one Wilson bound from the
   stored results JSONs; recompute. State whether they match the draft.
2. **Adjudicate the adjudication:** our LANE-LOG records round-2's 7
   claims CONFIRMED with specific probes (reruns bit-identical, census
   means, code greps). Spot-check at least two of them yourself. Did we
   verify honestly, or launder the referee's numbers?
3. **Judge the decisive experiments:** read `banc/l175/PREREG.md` and the
   results table. Branch D1 (drive-carried) / D2 (identity-carried) /
   D3 (mixed) was pre-registered. Which fired, with what numbers? Does
   the drive-matched twin flip or not? What does that do to the title
   "mass-twin controls isolate identity — not removal mass"?
4. **Cross-family novelty sweep — your training cut may differ from the
   fable family's:** what prior art do YOU know for (a) lesion-location
   dependence (we now cite Alstott 2009 — who else? C. elegans
   single-cell ablation lineage? stroke/lesion-mapping literature?),
   (b) single-cell ablation flipping a network regime, (c) matched-mass
   or matched-drive lesion controls? Name specific papers; we will fetch
   and verify each.
5. **Your verdict:** accept / minor / major / reject-and-rescope, plus the
   THREE changes that would most raise your score, plus one thing the
   fable family may have missed that you would check.

## Hard constraints

- READ-ONLY on everything except your two output locations:
  - report → `~/critters/peabrain-lab/paper/review_astra_r3.md`
  - evidence → `~/critters/peabrain-lab/paper/review_astra_evidence_r3/`
    (NOTES.md running log; save probes continuously)
- No vision tools on figures (analytic SVG checks only). CPU-only, no GPU,
  no training, no new rollouts beyond ≤2 quick probes if needed for task 1.
- Do NOT edit DRAFT.md, numbers.json, LANE*.md, LAB-*.md, banc/l*/,
  and never touch live services. Timebox ~60-75 min.
- Final chat answer ≤300 words: verdict, which adjudications you confirmed,
  which branch fired, your top-3 changes.
