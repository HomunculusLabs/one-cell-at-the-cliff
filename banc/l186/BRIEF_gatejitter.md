# EXPERIMENT brief — astra: L186 the gate-jitter discriminator (your own design)

Owner-directed (2026-11-21 ~12:2x). You proposed this in L184 as "the most
discriminating next experiment." Run it. Sequencing: poll until L187 is
done (banc/l187/verdict.out FINAL marker AND its dispatch process gone)
before launching workers. Write the PREREG while waiting.

## The question

The carrier's duty effect lives in SHARED timing (cross-seed +.52). Is that
timing locked to the EXTERNAL drive gate (realigns with jittered onsets)
or is it an INTERNAL rhythm (runs on elapsed time regardless)?

## Design (yours, from L184 — formalize in PREREG before any rollout)

- Per seed: independently jitter the 0.7-Hz gate onset schedule (draw the
  jitter pattern once per seed from a fixed RNG stream, key-scanned);
  MATCHED on-time, tone, gain and noise across arms (jitter pattern shared
  between paired arms by seed).
- Arms: carrier-present (cutwA base) and carrier-removed (sc25 graph), 16
  seeds each, re-bisected gains per the L175 procedure; a small unjittered
  anchor pair (2 seeds) to C0A against stored results EXACTLY.
- RECORD per rollout: GI 1110's trace (cell-state recording — this is the
  addition your design demands), right flexor + extensor pool rates, the
  gate schedule actually applied.
- Metrics (register bands FIRST): (i) cross-seed duty computed against the
  REALIGNED gate vs against ELAPSED time; (ii) carrier phase vs pool
  response; (iii) whether the carrier-removed elevation survives
  realignment.

## Pre-registered branches

- **E1-external**: cross-seed duty tracks the realigned gate (realigned
  >> elapsed) → the effect is drive-timing-locked; paper says so plainly
- **E2-internal**: cross-seed duty tracks elapsed time, not the gate → an
  internal rhythm unmasked by the deletion; much stronger claim, needs the
  second-batch treatment
- **E3-mixed**: quantify the split

## Ground rules

Transform of the certified harness (do not rewrite dynamics; the only new
code = gate-schedule jitter + GI 1110 recording + realignment metrics).
PREREG first (banc/l186/PREREG.md); fresh key-scanned seeds; C0A anchors
mandatory; CPU ≤6 workers; wall ≤1.5 h after L187 clears; writes confined
to banc/l186/** + one LAB-INTENT.md append; no draft/lane edits; no
vision; never ping anyone. Deliverables: PREREG, scripts,
results_l186.json, raws incl. GI-1110 traces,
banc/l186/L186-FINDINGS.md (≤60 lines), final answer ≤300 words.
