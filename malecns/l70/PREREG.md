# L70 PREREG — sl-sr-baseline-anatomy (static, CPU-only, no rollouts)

Item L70 (ideas-34) + tick-90 amendment (2610.19949 reciprocity arm).

Question: the open-cord baseline gas is LEFT-handed (open SL .326 vs SR .153,
census n=16, l66/l67 stored). Is the handedness WIRING-carried (static L/R
asymmetry, side-permutation-enriched) or STATE/SEED texture (per-seed re-roll)?

## Substrate
Male cord subnet VERBATIM l67 stage A: n=21,516 nodes / 2,977,920 signed edges
(keep = vnc_{sensory,intrinsic,motor} + dn_into). Effective weights = the
census regime's actual drive matrix: Wb_vals = gw * sign(src), inhibitory x
BETA 2.0 (l67 line 224-226 form). Side var: somaSide (MNs + intrinsic);
sensory not side-labeled for mass reads (L60: somaSide NaN ~all sensory).
Asserts: n, edge count, DNg100==2, all 8 pools non-empty.

## Metrics (pre-registered)
- M1 POOL INPUT ASYMMETRY: per pool (Ti/Tr x flex/ext x L/R, 8 pools):
  in_mass_eff = sum |Wb| onto pool; in_deg = #unique presyn cells;
  LI_mass = (L-R)/(L+R) per joint x family (4 values). NULL: 100 draws
  shuffling somaSide labels among that joint-family's MN members (L count
  fixed), z = (obs - mu)/sd of the null LI distribution. BONUS decomposition:
  per-pool in-mass by SOURCE side (ipsi/contra/no-label).
- M2 DNg100 SIDE LOADING: per cell, out-mass_eff by TARGET somaSide, split
  motor/intrinsic targets; pooled pair LI. NULL: 100 draws shuffling somaSide
  among all side-labeled subnet cells (counts fixed), z on pooled LI. Also:
  direct mass onto the 8 pools per side.
- M3 RECIPROCAL MOTIFS (tick-90 arm): sheet = premotor vnc_intrinsic (>=1
  out-edge onto motor) UNION motor cells; induced directed subgraph.
  recip pair = both directions present. fraction = recip_pairs /
  connected_unordered_pairs. ER baseline at same density p (ordered pairs,
  self-loops excluded): frac_ER = p^2/(2p-p^2); over-rep = fraction/frac_ER.
  Per side: fraction with BOTH members side-L (resp R); cross fraction;
  LI_recip = (fL-fR)/(fL+fR). NULL: 100-draw side-shuffle among labeled sheet
  cells (counts fixed), z. Secondary: intrinsic-only induced subgraph.
- M4 STORED-TRACE HANDEDNESS (no new rollouts): per-seed open S_L/S_R from
  l66/raw_l66.npz hynohop traces (16 census seeds), l67 duty_off windows
  verbatim (OFFS x TS3, 300-step S windows). h = SL - SR per seed; mean, sd,
  range, sign count. Cross-check: mean of per-seed SL/SR must match stored
  l66 open census SL .326 / SR .153 within 0.01 (same traces, same windows).
- M5 FEMALE CROSS-GRAPH: same M3 census on the BANC female cord subnet
  (l68 loader verbatim, sheet = premotor VNC intrinsic + motor by
  super_class, side via ann.side 'left'/'right').

## Verdict rules (pre-registered)
- G1 WIRING-CARRIED: any of M1 (4 LI_mass), M2 (pooled LI), M3 (LI_recip)
  has |z| >= 3 AND sign matches the dynamic bias direction (L-loaded wiring
  <-> SL healthier, the S_L .326 > S_R .153 gap to explain). Winner's
  extreme cells NAMED.
- G2 STATE/SEED TEXTURE: G1 fails on every metric. Strength scaled by M4:
  per-seed h > 0 on >= 13/16 seeds = biased coin (wiring sets a bias,
  lottery sets the instance); else fair re-roll (L59 miss migration is the
  signature).
- G3 reciprocity over-rep vs ER: paper whole-brain 1.68e3x; ours expected
  >> 1. If < 2x, motif axis dead here (honest negative, recorded).
- G4 free prediction (stability<-reciprocity, from L65/L68 bilateral-healthy
  female): female BANC premotor recip fraction comparable-or-higher than
  male (>= 0.5x male counts as comparable band; < 0.5x = prediction
  falsified, reported either way).

## Caveats adopted (tick 90, lane-wide)
MS-rewiring does NOT preserve reciprocal pairs -> recurrent-structure claims
(L32 substrate, L45 census) carry this caveat unless a reciprocity-matched
null tier is run (future card if G1 lands on M3).

## Anchors
A1: substrate asserts exact (l67 numbers above).
A2: M4 recompute == l66 stored open means (tol 0.01).
A3: raw_l70.npz checkpoints per-draw null distributions + observed metrics
BEFORE verdict reading; results_l70.json written after.
A4: all z's computed from the stored draws (re-derivable offline).
