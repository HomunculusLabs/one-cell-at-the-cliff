# L110 PREREG — heavy-vs-light intrinsic-target profile diff (STATIC, zero rollouts)

Written BEFORE any new computation. Card: do the removed 77 heavy projectors
differ from the kept 483 light dn_new in intrinsic-target PROFILE (tiers/cell
types hit, sign mix, side-of-target) in a way that predicts L109's
side-specific action? Feeds the family decomposition.

## Dynamic facts to explain (pinned, results_l109.json, n=32 B7+B8)

- Ti duty07 per side: full(L .394/R .440), b65(.997/.996), h65(.966/.984),
  cut(L .853 kL 32/32 / R .164 kR 0/32). Tr fresh: full(.037/.416),
  b65(.149/.973), cut(.077/.366).
- Reading: heavy-77 (in full, OUT of cut) carry the Ti_L kill; light-483
  (in BOTH full and cut) carry the Ti_R kill; Tr_L dead in every arm;
  Tr_R kill also light-carried (cut does not restore it).

## Sets (re-derived l107_static.py verbatim, lines 19-160)

- heavy = cut_drop (top cord-out-mass 77 of 560 dn_new), light = rest 483.

## C0 certification (HARD STOP if fail, before any new read)

- C0A: pins vs l107/static.json EXACT: n_old 21249, n_new 21809, dn_new 560,
  edges_old 627051, edges_new 647953, K 77, mass_share 0.5024, n_cut 21732,
  edges_cut 639164, cut.families dict EXACT (DNpe055:3 ... DNg24:2).
- C0B: my per-pool direct added edges/mass == static.json pool_direct_in
  EXACT (8 pools x 2 fields; e.g. Ti_eL 13/32.815, Tr_eL 28/63.27).
  This certifies the edge-list/val/sign plumbing my new reads ride on.

## Registered reads (shape is the claim — magnitude is TAUTOLOGICAL:
## heavy are the top-mass cells by construction; only side-asymmetry,
## sign composition, and type enrichment are informative)

- R1 (PRIMARY): signed 2-hop mass dn->intrinsic->pool for each of the 8
  Ti/Tr pools, closure wiring only (emask_n), v(d,t)*v(t,p), split
  heavy/light. Side asymmetry A = (S_f+S_e)|L − (S_f+S_e)|R over
  (|S_L|+|S_R|) per set, per joint. Null: 1000 random 77-of-560 subsets,
  z = (A_heavy_real − mean)/sd. Also per-pool signed table.
- R2: sign mix onto intrinsic targets: fraction of |mass| negative
  (glut-flipped) per set, subset null; plus source-cell NT composition
  (predicted transmitter) heavy vs light.
- R3: target-side profile: mass-weighted side (ann side L/R) of intrinsic
  targets, heavy vs light, subset null AND target-side permutation null
  (L70 rule).
- R4: cell-type enrichment: per intrinsic cell_type, heavy |mass| share vs
  subset-null mean (z); top ±5 reported. Cross-check top types' own
  out-share onto Ti pools (premotor-ness).
- R5 (prediction gates, preregistered):
  P1: A_heavy(Ti) < A_light(Ti) with |z|>=2 on at least the heavy side
     read — heavy more L-suppressive than light (or light more
     R-suppressive), in signed 2-hop terms: predicts cut restores L,
     keeps R dead.
  P2: the SIGN of (A_light − A_heavy) names the side cut fails to restore
     (R). If gates fail null-consistently (|z|<2): verdict = honest
     NEGATIVE — side-specific action is NOT predicted by static profile;
     mechanism is placement/attractor-dynamic, not profile-static.
- R6 (descriptive, no gate): hop-1 vs hop-2 mass share of the added DNs'
  total influence onto Ti_L vs Ti_R (path depth at which each side's
  influence enters; L60 depth rule).

## Outputs

- l110/results_l110.json (all reads + nulls + gates) + full per-type table
  l110/types_l110.json. No rollouts, no live changes.

## Known traps honored

- CSR/edge orientation: everything here rides the (src,dst,val) triple
  directly — no CSR construction (L62 trap n/a). C0B certifies it.
- Permutation nulls drawn with fixed seed 1100, drawn AFTER C0 passes.
- Target 'side' from ann.side lower-cased; cells with side '' excluded
  from R3 side counts but counted (disclosed).

## ADDENDUM 1 (registered AFTER first results, POST-HOC, disclosed)

The first run's R2 source-NT counts show heavy 19/77 glutamate vs light
25/483 (~3x) — not covered by any registered z. ADDENDUM computes, labeled
post-hoc-descriptive:
- A1: hypergeometric z for each NT count heavy vs the 560 pool.
- A2: per-DN-family signed 2-hop Ti_fL/Ti_fR sums (top contributors —
  the family decomposition's target list).
- A3: per-cell dominance: how many of the 77 heavy cells carry >50% of
  the heavy Ti_fL signed mass (concentration of the mirror).
None of these gates anything; they scope the follow-up card.
