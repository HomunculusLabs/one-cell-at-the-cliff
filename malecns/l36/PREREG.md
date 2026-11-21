# L36 PREREG — DN floor-viability census (written before any data)

Substrate: IDENTICAL to l32/l33/l34/l35 (asserted): cord + dn_into subgraph,
arm-A signs (ACh/glut +1, GABA -1, amines +0.2, unknown +0.3), raw-count
weights, uniform tau .05, DT .01, BG .02, NOISE .01, SETTLE 400, frozen
regime g .01 / beta 2. Census runs have I = 0 (l35_probe3 proved D=.05 on
DNg100 bit-identical to I=0 — the control regime is drive-free).

u := mm(Wb, X)*G + BG  (pre-relu pre-clamp; l35_probe2 definition, verbatim).
Census: seeds 11/22/33, 600 steps (6 s ≈ 8 rhythm cycles) post-settle, over
ALL descending cells in the sub; per TYPE aggregate:
  u_max (max over cells x steps x seeds), u_mean, frac_pos (frac u>0),
  cells_free (per-cell u_max > 0), cells_a015 (> -0.15), cells_a08 (> -0.8).
Join l31/cx_dn.csv (dn_type) for family (w_flex/ext/jump), laterality
(nL/nR/org), CX mass/hop. family := argmax family with weight >= .25.

Claim levels (pre-registered):
- C1 ANCHORS: DNg100 u_max < -1 (floor-buried, L35 measured ~-16);
  DNg95 NEAR-FLOOR: u_max in [-.15, +.10] AND u_mean < 0 AND frac_pos < 0.5.
  [AMENDED pre-rerun, tick 53, disclosed: original band top +.02 was
  under-specified for the max-over-statistic — L35 read 25-step volley
  windows (u_max <= -.064 absorbed / >= -.038 landed); a FREE 6-s window
  samples higher maxima, first run observed +0.047 with DNg100 exact
  (-15.78 ~= L35's -16, the wiring-proof anchor). Added window-robust
  u_mean/frac_pos conditions. DNg100 band untouched — it is the
  miswiring detector and it PASSED first try.]
- C2 VOCABULARY: count atlas-family types (some family weight >= .25) with
  u_max > 0 ("freely viable") vs > -.15 ("viable at amp <= .15") vs > -.8.
  Vocabulary non-empty := >= 5 freely-viable family types. If fewer, the
  honest verdict is "tonic drive needs amp"; report the threshold table.
  [AMENDED run-4, tick 53, disclosed: the MDN spot-check (dm EXACTLY 0 at
  amps .2/.8 with u_max +4.46, frac_pos 1.0, mean_X = 1.0000) taught that
  u_max > 0 is INSUFFICIENT — cells pinned at the clamp ceiling carry no
  upward dynamic range. Added two-sided criterion C2b "viable-modulating":
  >= 1 cell with u_max > 0 AND per-cell mean X < .95; plus a
  ceiling_pinned count. C3 ABSORBED relabels CEILING-PINNED when dm==0
  with u_max>0 and mean_X>=.95 — the L35 floor/ceiling amp-taxonomy, now
  with a census-side predictor.]
- C3 SPOT-CHECK (dynamic, P1-labeled): top viable type per family
  (w_family >= .25, u_max > -.05; rank cells_free then u_max), tonic amps
  {.2, .8}, 3 seeds, 60-s window, ALL metrics on last 45 s (L34 window
  lesson). PASS := (a) dm probe max|dX| > .01 (not bit-identical, L35
  instrument) AND (b) |df| > .05 Hz or |dS(Tr)| > .05 vs paired same-seed
  control in >= 2/3 seeds. Branch if (a) passes but (b) fails everywhere:
  "participates but does not modulate at tonic amp" — a real L33-shaped
  finding, reported as such. Anchor arms: DNg100 amp .8 expected
  BIT-IDENTICAL (dm == 0); DNg95 amp .2 expected dm > 0.
- af assert 0.01 < af < 0.9 in every rollout (L30/L11 probe).

No WHEN-claims; no live changes; CPU-only.
