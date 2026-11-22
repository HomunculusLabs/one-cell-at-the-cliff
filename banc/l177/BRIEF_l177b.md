# BRIEF — L177(b): the af-matched beta ladder (rollouts)

You are executing stage (b) of lane card L177 on the peabrain lab box.
**Read `~/critters/peabrain-lab/banc/l177/PREREG.md` FIRST and in
full. It is frozen. Do not add, drop or soften a registered cell.**

Stage (a) is already DONE (this is the pre-measurement your run is registered
against): `banc/l177_prem.py` -> `l177/static_prem.json` + `l177/prem.out`.

## What to build

A single runner `banc/l177_run.py` (peabrain venv python:
`~/critters/peabrain/.venv/bin/python`) that:

1. Runs **C0S-177** (static cert) first and halts on any mismatch.
2. Runs **C0A-177** (forward-chain bit-identity anchor): the beta=2.0 rung at
   l65's frozen un-rematched gain g=0.14, d=0.2, seeds 11/22/33, compared
   against `l65/raw_l65.npz` keys `B_s{11,22,33}_{Ti,Tr}_{f,e}` at max|d| =
   0.0. **HALT on failure, report, analyse nothing.** The cleanest route to
   bit-identity is to re-use `l65_banc_oppoint.py`'s own `run()` and its
   noise-draw ORDER verbatim (one generator, shared per-step tensor, settle
   prefix included) — copy it, do not re-derive it.
3. Walks beta in {1.0, 1.5, 2.0, 3.0, 4.0}, **fresh af-matched bisect per
   rung** to target af 0.1038, 16 paired seeds, 60 s windows, with the per-rung
   op-point assert, the d=0 drive-relevance arm, and the u/X viability census.
4. Checkpoints raw pool traces to `l177/raw_l177.npz` as each rung finishes
   (all four antagonist pools **per side** + the S trace), then writes
   `l177/results_l177.json` and a verdict block naming the branch
   (B_MONOTONE / B_INTERIOR / B_COLLAPSE / B_ARTIFACT) and **which cell
   carries it**.

## Hard rules (house discipline, non-negotiable)

- Writes confined to `banc/l177/` + `banc/l177_run.py`. **No live-module
  edits, no `paper/` edits** (DRAFT.md is in owner-handoff state), no
  LANE.md / LANE-LOG.md edits (the cron tick owns those).
- Zero changes to `l65*`, `banc_graph.pt`, or any data file — read-only.
- CSR rule: build via COO -> coalesce() -> to_sparse_csr(), never the raw
  ctor; `W[target, source]`, rows are targets.
- torch.sparse.mm needs [N,1] operands, never a 1-D vector.
- If a registered prediction comes out WRONG, say so in the verdict — a
  disclosed wrong prediction is the run's strongest sentence. If the gate is
  the bug, rescope it as a written PREREG ADDENDUM **before** the read, never
  after.
- GPU: the live duck holds ~7.8 GB. Check `nvidia-smi` before starting and do
  not evict it; CPU with `torch.set_num_threads(8)` is acceptable and is what
  l65 used (the anchor's bit-identity may DEPEND on matching l65's device and
  thread count — match them).
- Budget: if the full 5-rung x 16-seed grid will not finish in ~90 min, run
  the rungs in PREREG order, checkpoint each, and stop cleanly with a
  disclosed partial (rungs completed / rungs owed). A partial with a clean
  cert is a good result; a rushed full grid is not.

## Deliverable

One summary (<= 25 lines) carrying: cert results, the per-rung af residuals
and gain spread, the per-side S table, the branch + the cell that carries it,
every wrong prediction, and the artifact paths. Do not touch the board.
