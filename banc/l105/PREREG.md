# L105 PREREG — closure-free-run-scan (zero-drive antagonist self-ordering)

Registered BEFORE any rollout. All inherited expectations derived from STORED
artifacts (L44 rule): raw_l101.npz, raw_l103.npz, results_l101.json,
results_l103.json, l65/results_l65.json.

## Question

L94/L101/L103's "no robust base pair on the closure substrate" verdict was
measured UNDER the chopped sinusoidal entrainment trunk (+ tonic DNg100 D=.2,
settle-sin always on). The l65 EXTRACTION substrate self-ordered antagonist
antiphase at zero drive (stored: ladder_arm B, ladder_real_S = 0.7196, Ti,
l65/results_l65.json). Open cell in the matrix: does the L92 closure substrate
self-order at ZERO sinusoidal drive? Either the l65 self-ordering was an
extraction-rule property (expected) or the closure substrate has a masked
second life sign.

## Design

Machinery l101_run.py VERBATIM (extraction, two-generator noise law, joint
settle, AMPA/PHI schedule, DNg100 tonic), pools = 5 pairs x 4 sides (l101) +
LT/FR x 2 sides (l103 tokens) + Ti_aL/Ti_bR cert pools. ARMS:

- cfn    — l101 verbatim (settle sin ON, WIN AMPA schedule, D=.2). CERT arm.
- free   — NO sinusoid anywhere (settle + WIN), D=.2 kept.
- freenod — NO sinusoid, D=0 (In all zeros).

Seeds: ANCHOR [11,22,33] + B4 801-816 + B5 901-916 + B6 1001-1016 (51).
Per arm, generators re-seeded identically (gen seed, gen2 seed+9000) → all
arms share the per-seed noise stream; cfn must be bit-identical to stored.

## Anchors + gates (run script asserts; verdict re-derives from npz)

- C0A-101: cfn == raw_l101.npz BIT-IDENTICAL: mm/xm all 51 seeds, Ti/Tr 4
  pools x 6 cert seeds, af_cfn exact-equal all 51. Expected 0.0 (40th chain
  anchor held this in tick 127; this is the 41st).
- C0A-103: cfn == raw_l103.npz BIT-IDENTICAL: LT/FR 4 pools x all 51 seeds,
  Ti_aL/Ti_bR x 3 cert seeds. Expected 0.0.
- C1: 0.01 < af < 0.9 every arm/seed; cfn af == stored exact.
- C0D: free != cfn (max|d mm| > 0 — proves the drive wiring differs; an
  all-zero diff would mean the drive never mattered, L35 class).
- C0B (verdict Part 1, must PASS before any L105 pin — L85 rule): this
  script's cells/tables code reproduces results_l101.json (5 pairs x per-batch
  7 reads + pooled + side + nan + lock) AND results_l103.json (LT/FR pooled +
  per-batch k/kL/kR + flyhack real/shift means) EXACTLY.
- Wilson bar pin: wilson_lb_full(41,48) >= .717 > wilson_lb_full(40,48).

## Registered predictions (P1 primary; never-fires branches explicit)

- P1 (PRIMARY, expected FAIL/never-fires): free-run self-ordering = any of
  5 pairs clearing G2a-multi (pooled lb >= .717 over 48 fresh, k >= 41) on
  the free arm, both-sides duty_07 cell. NO pair clears → "the extraction
  rule owned the self-ordering" (completes the L94 substrate law). ANY pair
  clears → second life sign, P3 secondary REQUIRED before any claim.
- P2: freenod == free bit-identical (L35 D-law: tonic DNg100 carries nothing;
  male precedent). Both branches disclosed: if NOT identical, D-carried mass
  exists on closure — descriptive, no gate, disclose magnitude.
- P3 (FlyHack two-sided secondary, tick-126 amendment): computed
  UNCONDITIONALLY on the best free cell (max pooled p-hat among 5 pairs
  both-sides duty_07 + LT/FR LR cells): shift-500 phase-shift null; positive
  claim requires margin real_mean - shift500_mean > 0. Never-fires branch:
  if P1 fails everywhere, P3 reads as the clean-negative confirmation.
- P4 (paired, descriptive): per-seed duty_07 delta (free - cfn) per pair +
  sign counts — L79-class check whether removing drive RAISES structure
  (drive-toxicity inversion). No gate; disclose.

## Disclosures fixed at registration

- Seg windows (0.7/1.4/0.7 + 500-step guards) are TIME-FIXED conventions
  carried from the driven protocol; free-run has no drive boundaries — kept
  for cell-for-cell comparability with l94/l101/l103 tables.
- Unpaired LT/FR use the l103 contralateral-homologue LR cell (antagonism
  semantically undefined for unpaired pools — definitional port, disclosed
  there, inherited here).
- l65 citation is a DIFFERENT metric form (single-window S at their scan
  point, g .01/beta 2) vs our duty cells — directional comparison only.
- Budget: 3 arms x 51 seeds, CPU ~10 min; raw npz checkpointed pre-analysis;
  resume-safe partial.
