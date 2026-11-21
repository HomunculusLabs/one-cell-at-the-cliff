# EXPERIMENT brief — L190 the single-edge cut (the surgical test)

Owner-directed (2026-11-21 ~13:0x). The carrier's influence route runs
through relay GI 75494; the carrier→relay edge carries 21 synapses. The
surgical question: does cutting ONLY that edge reproduce (or remove) any
part of the carrier phenotype?

## Arms (PREREG first; fresh key-scanned seeds; 16 each; your L187 harness)

- **E-edge:** on the k=24 base, remove ONLY the 1110→75494 edge (21 syn,
  sign per the graph). Registered branches: **B1-edge-carries** (edge-cut
  ≈ carrier-cut: SUPER + 1.4-Hz signature), **B2-edge-inert** (≈ base),
  **B3-partial** (chopped duty moves without the signature, relay-like).
- **E-sham:** remove a DIFFERENT single 20-22-syn edge into 75494 from a
  non-window cell (registered selection rule: closest synapse count, DN
  source, argmin |log(syn ratio)|, frozen before selection). Negative
  control for "any big edge into the relay does it".
- **Anchors:** standard C0A set (cutwA reproduces stored EXACT); one
  unjittered sc25 seed pair re-rolled vs stored.
- Also store per-step traces of 1110, 75494, 559, 74914 for every
  arm/seed (same convention as L187) — zero extra cost, feeds the phase
  analysis.

## Ground rules

Identical law to L187: transform of the certified harness, PREREG frozen
before rollouts, CPU ≤4 workers (L183 manuscript agent is running
concurrently — keep cores modest), wall ≤1 h, atomic per-seed writes to
banc/l190/results_l190.json, writes confined to banc/l190/** + one
LAB-INTENT.md append. Deliverables: PREREG, scripts, results, raws,
banc/l190/L190-FINDINGS.md (≤50 lines), final answer ≤250 words.
