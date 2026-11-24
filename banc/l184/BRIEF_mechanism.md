# EXPERIMENT brief — astra as mechanist: L184 mechanism analysis (ZERO new rollouts)

Owner-directed (Discord, 2026-11-21 ~11:3x). You found the cross-seed
time-locking; now explain it. Everything here is analysis of STORED raw
traces + stored wiring. No new rollouts. CPU-only.

Working set: `/home/t3rpz/critters/peabrain-lab/`
- `banc/l175/raw_w*.npz`, `raw_census.npz`, `census_k24.npz`, `xm_*.npz`,
  `results_l175.json`, `selection.json`, `verdict_l175.out` (FINAL scan)
- `banc/l135/raw_l135.npz` (historical anchors), `banc/l172/stats.json`
- `banc/banc_graph.pt` (substrate), `banc/l131_static.py` (cohort derivations)
- Your own round-3 evidence (`paper/review_astra_evidence_r3/`) is a
  legitimate starting point — extend your own probes.

## Questions, in priority order

**Q1 — envelope transmission (the headline).** The drive is chopped at
0.7 Hz with a 1.4-Hz continuous middle. Hypothesis H-env: DNp33-L normally
*damps* transmission of the drive envelope into right-tibia pools; removing
it raises envelope penetration, and the duty increase is envelope-locked.
Test on stored B39 traces: (i) per arm, quantify the 0.7-Hz (and 1.4-Hz)
envelope amplitude IN the right flexor/extensor pool rates (spectral or
envelope-correlation with the known drive schedule); (ii) does carrier
removal increase it relative to base/twins? (iii) is the carrier itself
entrained to the drive phase in arms where it exists (base, twin arms)?
Register the analysis plan in `banc/l184/PREREG-analysis.md` FIRST (bands,
windows, seeds), then compute.

**Q2 — pathway anatomy (where does its influence flow).** From the stored
graph + census: enumerate the carrier's incident edges (93, stored);
classify targets: direct right-Ti premotor / other motor / interneuron.
Compute the top-k linearized contribution paths carrier→right-Ti pools
(the lab's queued L178 idea — realize it properly; state the linearization
assumptions). Compare the target sets of sc27 (gi 707) and sc40 (gi 559) —
the two boundary cells — with the carrier's: weak-same-pathway or
unrelated? Also: dmA/dmC target overlap with carrier.

**Q3 — per-pool decomposition of the duty change.** Duty = −corr(flex,ext).
For base vs sc25 (and dmA/dmC/sc27/sc40): decompose the change into (a)
flexor mean-rate change, (b) extensor mean-rate change, (c) within-run
correlation change vs (d) cross-run (envelope) component (your locked.py
machinery). Which term carries the +.35?

**Q4 — the 3-panel table.** All 37 arms × {chopped, unchopped-1.4Hz,
cross-seed} columns, one table, stored as
`banc/l184/threepanel.csv` + a rendered markdown table in the findings doc.

## Ground rules

- Zero new rollouts. Stored data + your code only.
- Writes confined to: `banc/l184/**` and one `LAB-INTENT.md` append (§L184).
- No DRAFT.md / numbers.json / LANE*.md / banc/l1xx-existing edits.
- Register Q1's analysis plan BEFORE computing it; Q2-Q4 are descriptive —
  still state methods before results in the findings doc.
- Timebox ~60-75 min. Final chat answer ≤300 words: is H-env supported,
  what fraction of the carrier's effect is envelope-locked, what is the
  pathway picture, and the one experiment that would most discriminate.
- Deliverables: `banc/l184/PREREG-analysis.md`, probe scripts + outputs in
  `banc/l184/`, `banc/l184/L184-FINDINGS.md` (≤70 lines).
