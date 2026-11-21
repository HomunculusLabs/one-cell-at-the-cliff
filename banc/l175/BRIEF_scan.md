# EXPERIMENT brief — fable 5.2 as experimenter: L175 stage (b) scan + drive-matched twin

Owner-directed (Discord, 2026-11-21 ~10:4x). You are the EXPERIMENTER this
time, not a referee. You execute two pre-registered experiments in
`~/critters/peabrain-lab/`. The lab's discipline is mandatory and
is what makes your results admissible.

## Context (30 seconds)

The preprint's central two-cell contrast (carrier removal flips a regime
transition; its mass-matched twin does not) has an adjudicated confound:
the twin is a near-silent cell (x_mean .0033 vs carrier .454 — confirmed
from `banc/l137/raw_l137.npz`). So the control matches static removal mass
but not delivered drive. Round-2 referee report: `paper/review_fable_r2.md`
§N1 (read it). Your experiments decide whether the finding is
drive-carried, identity-carried, or mixed.

## Ground rules (house law — violating any makes the run inadmissible)

1. **PREREG FIRST.** Write `banc/l175/PREREG.md` BEFORE any rollout:
   branches, predictions, pins, selection rules, seed ranges. No peeking.
2. **Re-derive, never trust prose.** Every ID / gain / count comes from
   stored tables + scripts with asserts (`l131_static.py`, `l135_run.py`,
   `results_l135.json`, `results_l150.json`, `banc/l137/raw_l137.npz`,
   `banc/l169d/PREREG.md`). Numbers in this brief or in logs are HINTS;
   assert them from artifacts or discard them.
3. **Transform certified machinery.** Your run script must be a count-
   asserted ADDITIVE transform of `banc/l150_run.py` / `l169d` lineage
   code (copy, extend, assert the unchanged parts reproduce stored values:
   the cutwA base arm of your harness MUST reproduce stored cutwA results
   EXACTLY — that is your C0A anchor; gain g_cutwA must equal the stored
   float exactly).
4. **Fresh seeds, key-scanned.** Pick a seed range absent from every
   stored npz (scan keys before registering). 16 seeds per confirmatory
   arm; 8 seeds per scan arm is acceptable (declare the power tradeoff in
   the PREREG).
5. CPU-only, ≤6 worker processes, no GPU, no touching the live duck
   services, no DRAFT.md edits, no LANE.md checkbox flips, no cron, never
   ping the owner. Do not use vision_analyze (route-broken).
6. Everything survives your session ending: incremental writes to
   `banc/l175/run.out`, results json written atomically at each arm.
7. Wall-time target ≤ 90 min. If you cannot finish, ensure PREREG +
   pilot + partial results + a resume plan exist, then say so.

## Experiment 1 — single-cell scan (the decisive scatter)

On the k=24 base (cutwA lineage), remove EACH cell of the removal window
ranks 25–58 (the ~34-cell window that includes the carrier at its bottom
edge; re-derive the exact window and IDs from `l131_static.py` +
`results_l135.json` with asserts) ONE AT A TIME, as a single-cell cut:
- arms: one per window cell (the carrier arm and twin arm of the lineage
  are your positive/negative controls — reproduce or you have nothing)
- seeds: 8 per arm (16 for carrier/twin/base controls)
- readout: the paper's right-tibia classifier exactly as the lineage
  computes it (transform, don't re-implement)
- covariates per arm: x_mean of EVERY window cell + you MUST also dump
  x_mean for all closure cells in three reference k=24-base seeds
  (needed for Experiment 2's drive computation)
- output: `banc/l175/results_l175.json` — per cell: {gi, rank, x_mean
  (k=24 base), out_mass, delivered_drive = x_mean × out|w| onto closure,
  kR, kL, n, mean duty R/L}, classifier verdict per the paper's bands

## Experiment 2 — drive-matched twin (the missing control)

Selection rule — register BEFORE seeing any scan outcome (selection on
covariates only):
- candidate pool: closure cells NOT in removal-window ranks 1–58 and not
  used in any prior arm; drive = x_mean (k=24 base, 3-seed mean) ×
  absolute out-weight onto closure targets
- pick argmin |log(drive_cand / drive_carrier)|; tie-break: smaller
  |log(mass_cand / mass_carrier)|; record the top-5 runner-ups
- arm: remove that one cell from the k=24 base, 16 seeds, same readout
- output: same row schema, in the same results json

## Pre-registered branches (write your own precise versions in the PREREG;
this is the shape)

- **D1 drive-carried**: scan outcome is (monotone-)ordered by delivered
  drive among active cells, and the drive-matched twin flips like the
  carrier → title reframes to "delivered drive, not removal mass"
- **D2 identity-carried**: active cells (> .05) mostly do NOT flip, the
  drive-matched twin does not flip, carrier still does → identity claim
  with a distribution behind it
- **D3 mixed**: declare the pattern honestly; propose the discriminator
- Register quantitative bands (what kR count counts as "flips" at n=8/16)
  BEFORE running. Report which branch fired with the numbers.

## Deliverables

1. `banc/l175/PREREG.md` (before any run)
2. `banc/l175/scan_run.py` (+ build script if you use one)
3. `banc/l175/results_l175.json` + `census_k24.npz` (full-closure x_mean)
4. `banc/l175/run.out`, `banc/l175/L175-FINDINGS.md` (≤60 lines: branch
   fired, the scatter in a table, what it changes for the title)
5. Final chat answer ≤300 words: branch, headline numbers, ETA of what
   you did not finish
6. Append one line to `LAB-INTENT.md` §L175 (absolute-path style, like
   the other entries): what ran, how verified

Do NOT edit: DRAFT.md, numbers.json, LANE*.md, any existing banc/l1*/
artifacts, the live services. Your writes: banc/l175/** and one
LAB-INTENT.md append, nothing else.
