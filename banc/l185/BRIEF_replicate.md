# EXPERIMENT brief — fable as replicator: L185 fresh-batch + gain null + signed-current twin

Owner-directed (Discord, 2026-11-21 ~11:3x). The scan gave D2 on one batch.
This card hardens it. All rollouts are transforms of YOUR certified L175
harness (same seeds/keys discipline, C0A anchors mandatory: the cutwA base
must reproduce stored results EXACTLY in every worker before any new arm).

Working set: `/home/t3rpz/critters/peabrain-lab/banc/l175/` (your harness),
`banc/l175/selection.json` (census data for twin selection).

## Arms (register ALL in `banc/l185/PREREG.md` BEFORE any rollout)

**R1 — fresh-batch replication (the L90 rule).** New seed batch (fresh
range, key-scanned absent from every stored npz), 16 seeds each:
- sc25 (carrier), sc26 (mass twin), dmA (gi 511), dmC (gi 1480),
  sc27 (gi 707), sc40 (gi 559) — six arms at their L175 re-bisected gains
- THE SAME six arms at FIXED base gain g_cutwA (the astra's ask: separate
  the gain-re-matching from the deletion effect)
- base cutwA (anchor arm, both gain forms coincide)
→ 13 arms × 16 seeds. Register predictions: which arms replicate SUPER/
boundary; the fixed-vs-rematched contrast per arm.

**R2 — gain-only null.** Base network (NO deletion), gain swept ±0.5% in
5 steps around g_cutwA, 16 seeds each → 5 arms. This isolates how much of
the scan's meanR spread (ρ(gain,meanR) = −.72) is pure gain sensitivity.
Register: predicted meanR slope per +0.1% gain.

**R3 — signed-current-matched twin (closes the astra's last drive
loophole).** The drive twins matched UNSIGNED pooled output. Select (zero
rollouts, from census_k24 + graph): the non-window cell minimizing
|signed current onto right-Ti premotor − carrier's| (signed = sign-aware
sum over paths of length ≤2; state the exact formula in the PREREG before
selecting). Then ONE arm: that cell removed from the k=24 base, 16 seeds,
re-bisected gain. Register prediction under D2 (no flip).

## Ground rules (same law as L175)

- PREREG first (all arms + predictions + pins). Fresh key-scanned seeds.
- C0A anchor: cutwA reproduces stored EXACTLY per worker; all stored gain
  floats reused exactly; metric identical to results_l135.
- CPU-only, ≤6 workers, wall-time target ≤2.5 h; incremental atomic
  results writes (`banc/l185/results_l185.json` per completed seed).
- Writes confined to `banc/l185/**` + one LAB-INTENT.md append (§L185).
- No draft edits, no lane files, never ping anyone, no vision tools.
- Deliverables: PREREG, run scripts, results json, raw npz anchors for
  sc25/dmA/dmC/base + the R3 twin arm, `banc/l185/L185-FINDINGS.md`
  (≤70 lines: what replicated, the gain-null slope, did the signed twin
  flip), final chat answer ≤300 words.
