# EXPERIMENT brief — fable: L187 relay-silencing + push-pull (SEQUENCED behind L185)

Owner-directed (2026-11-21 ~11:5x). Tests L184's anatomy: the carrier's
influence route runs through relay interneuron GI 75494 (4-edge chains into
both tibia pools); sc40 (gi 559) enters the SAME relay with opposite sign.

## Sequencing (mandatory)

L185 is RUNNING (bg process; banc/l185/ filling). POLL until it is done
(banc/l185/results_l185.json shows all arms complete AND its dispatch
process is gone — check `pgrep -f 'l185'` and the run.out FINAL marker)
before launching ANY worker. While waiting: write the PREREG, build the
harness (transform of YOUR l175 machinery — you built it, extend it).

## Arms (register predictions BEFORE rollouts; fresh key-scanned seeds; 16 each)

- **A1 relay-silence:** activity-clamp GI 75494 on the k=24 base (carrier
  present). Branches: R1-conduit (relay silence mimics carrier removal —
  duty rises) vs R2-carrier-specific (no change).
- **A2 relay-cut:** edge-removal of GI 75494 on the k=24 base. Same
  branches; silence-vs-cut comparison echoes the paper's silW ⊂ cut law.
- **A3 push-pull:** remove sc25 (carrier) AND sc40 (gi 559) together from
  the k=24 base. Branches: R3-cancel (opposite-sign convergence cancels,
  duty ≈ base) vs R3-stack.
- **A4 control:** sc40 alone re-run on this batch (it was 11/16 boundary in
  B39 — a fresh-batch estimate of its own effect belongs in the same table).

Gain rule: every arm re-bisected to its matched operating point (the L175
procedure); fixed-gain twin of A3 optional if time permits.

## Ground rules

Same law as L175/L185: PREREG first (banc/l187/PREREG.md), C0A anchor
mandatory (cutwA reproduces stored EXACTLY), CPU ≤6 workers, wall ≤2 h,
atomic per-seed results writes, writes confined to banc/l187/** + one
LAB-INTENT.md append, no draft/lane edits, no pings, no vision tools.
Deliverables: PREREG, scripts, results json, raw anchors for A1-A4,
banc/l187/L187-FINDINGS.md (≤60 lines), final answer ≤300 words.
