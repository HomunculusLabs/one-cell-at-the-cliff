# L220 PREREG — the L211 TRANSPORT leg on the BASE UNFLOORED cutwA substrate

Registered 2026-11-23 ~07:3x EST, tick 250, BEFORE the generated script
existed and before any cutwA quantity was measured. Static; zero rollouts,
zero settles, zero dynamics.

## The question

L211 decomposed L206's search-information (SI) excess into a FIRST-HOP term
(-log2 T of the carrier's own chosen out-edge) and a REMAINDER (its targets
onward), on the **f4wA** (synapse-floor-4) substrate only, against 100
degree-neutral destination-swap draws (l169c, seed 16943). It found
`B_REMAINDER`. The card's deferred leg asks whether that split **transports**
to the **cutwA** base substrate, which applies no synapse floor
(21,785 cells / 644,177 edges vs f4wA's 21,789 / 469,618).

## PREMISE CORRECTION 0a — the null EXISTS on cutwA and is already certified

The card says "cutwA has no stored SI null, so either the l169c swap must be
re-run on that substrate or the leg is descriptive — decide in the PREREG".

**Decided here: re-run it, because it is the l169c NATIVE null.** Inspecting
the certified machinery (l178_tail.py 348-458, inherited verbatim by L206,
L211, L218, L219 and this card) shows `rewire_draws` is already generic in its
masks, and `CERT-REW` calls it with the **wA** block:

    _dnw      = dn_all & keep_wA
    _blk_wA   = emask_wA & _dnw[src_all] & cord_of_dst
    _sel_car_wA = emask_wA & (src_all == GI_CARRIER)
    rewire_draws(_blk_wA, _sel_car_wA, 100, 16943, T70, motor_G)

and gates the result at float equality against `l169c/static.json`
`P6_rewire_draws` (medians + the first five per-draw rows). The f4wA null that
L206/L211 used is the **derived** one (`_blk_f4`), not the stored one. So the
cutwA leg is NOT condemned to be descriptive: the degree-neutral
destination-swap null is native to cutwA and its summary statistics are pinned
by a stored artifact. The certified `rewire_draws` is called UNCHANGED with
those certified cutwA arguments, and the call is gated (CERT-REWCUT, halting)
against l169c's stored values BEFORE any SI number on cutwA is read.

Consequence: the primary is SCOREABLE, not descriptive. Registered as such.

## PREMISE CORRECTION 0b — the carrier's out-degree on cutwA is 80, KNOWN IN ADVANCE

The card instructs "the out-degree is NOT 69 there — read the real count,
never assume it". It is **80**, and this is not a measurement of mine: it is a
PIN asserted inside the inherited head (l151_static.py lines 126-133:
`sel_out_n.sum() == 80` and the out-edge SET asserted array-identical between
the base closure and wA). I read it while scoping. Therefore:

* The menu-size leg of the card's branch (iii) is **RESOLVED IN ADVANCE** and
  is reported as a descriptive fact, not as a branch outcome.
* **Cross-substrate comparison rule, registered**: a first-hop cost in bits is
  read against its OWN substrate's uniform-allocation baseline
  `log2(out-degree)` — 6.108524456778169 on f4wA (69 edges) vs
  log2(80) = 6.321928094887363 on cutwA — never against the other
  substrate's. Any bare fh_mean difference between substrates is therefore
  decomposed into (baseline shift) + (selection), and only the second is a
  claim about wiring.
* Branch (iii) survives only in its **reachability** form (see branches).

## PREMISE CORRECTION 0c — the gain currency, and the no-op is MEASURED not assumed

L206 built the f4wA SI index from the G-scaled anatomical operator
`A = jv_abs_an = |G_F4WA * v|`; the certified generic substrate builder
(`build_sub`, CERT-GEN) returns a **g = 1** operator, which is what L209 used
for cutwA. `L_uv = -log10(A/A_max)` and `T_uv = A_uv/s_out(u)` are both
mathematically INVARIANT to a positive global rescale of A, so the choice is a
no-op in exact arithmetic — but L209's law says a mathematical no-op is not a
floating-point no-op. Registered:

* f4wA SI numbers are taken from the certified **G-scaled** index, so CERT-SI
  and CERT-211 hold at float equality.
* cutwA uses its own **g = 1** index (L209's convention for that substrate).
* The induced discrepancy is **MEASURED on f4wA** by building both indices and
  reporting max |dL_L|, max |dT_L| and the resulting d(si_mean), d(fh_mean) on
  the carrier. If any of those exceeds 1e-9 in relative terms the
  cross-substrate comparison is reported with that error bar attached rather
  than silently.

## PREMISE CORRECTION 0d — share_fh is a ratio of SIGNED differences

L211's own method lesson: registering `share_fh in [0.00, 0.25]` scored a
CORRECT branch call FALSE at a measured -0.0056, because
`share_fh = D_fh / D_total` is a ratio of signed differences and admits
negative values by its own definition. Every band registered below admits
every sign its definition allows.

## OBSERVATION STATUS (Kriegeskorte 2009; the L214 rule)

I read `l211/static.json` and the L206 G2 block while scoping. The following
are therefore **OBSERVED-DERIVABLE** and are declared **DESCRIPTION**, never
inference, in this card. Stated in full so nothing can be retro-fitted:

f4wA (L211): branch `B_REMAINDER`; share_fh -0.005618879769401901;
D_total +3.5815652597499934 = D_fh -0.0201243845808019 + D_rem
+3.6016896443307953; carrier n_reach 303, si_mean 22.39317740345491,
fh_mean 5.847280040722828, rem_mean 16.54589736273208, fh_share_of_si
0.2611188191551899, hop_mean 3.8052805280528053, dist_mean 1.489994386339637,
n_distinct_first_hops 11, fh_min 5.515257714221297, fh_max 6.711883423616468;
menu n 69, log2 6.108524456778169, min 5.4963012879811535, med
6.195185880629637, max 6.711883423616468, null n_distinct med 16.0;
null means si 18.811612143704917 fh 5.86740442530363 rem 12.944207718401286
hop 3.203993399339934 dist 1.2235333741117298; percentiles fh 45.0 rem 100.0
si 100.0 hop 100.0 dist 100.0; cohort family fh-share med 0.2834957374928224,
twin 0.30678634491249146, mirror_928 0.246, carrier rem rank 32/35, fh rank
26/35. L206 G2: carrier SI percentile 100.0, null_si_med 18.71799427882452,
null_si_p05 17.0799..., null_si_p95 20.6240..., family_si_mean_med
20.269773413028425, n_pool_cells 303-reachable-of-N_POOL. l151 pin: carrier
out-degree 80 on cutwA and on the base closure.

**Every branch and every prediction below is placed on a cutwA quantity, none
of which has been computed by anyone.**

## Registered branches (primary)

Primary statistic: `share_fh(cutwA) = D_fh / D_total`, with
`D_x = carrier_x - mean_over_100_draws(x)` and
`D_total = D_fh + D_rem` (additivity asserted < 1e-9, halting).

* **T_TRANSPORTS** — `share_fh(cutwA) <= 0.40`. The split is
  substrate-independent; the remainder dominance is not a floor artifact.
* **T_INVERTS** — `share_fh(cutwA) >= 0.60`. The single most damaging
  counterfactual to L211: the remainder dominance would be an artifact of the
  synapse floor.
* **T_SPLIT** — `0.40 < share_fh(cutwA) < 0.60`.
* **T_DEGENERATE** — `D_total <= 0`, any non-finite term, or the carrier
  reaching `<= N_POOL_cut // 2` pool cells on cutwA (branch (iii)'s surviving
  reachability form). No share is reported in this case; the guard speaks.

## Registered predictions (scored, not amended afterwards)

* **P1** — branch `T_TRANSPORTS`.
* **P2** — `|share_fh(cutwA)| <= 0.25` (magnitude band; both signs admitted).
* **P3** — the funnel transports: cutwA realised
  `n_distinct_first_hops <= 0.35 * 80 = 28`.
* **P4** — the L206 G2 finding transports: carrier SI percentile on cutwA
  `>= 95.0` against its own 100 cutwA draws.
* **P5** — within-source stability: `|fh_share_of_si(cutwA) - 0.2611188191551899| <= 0.10`.

## Secondary, registered in advance

* `fh_share_of_si` (= fh_mean / si_mean) is a WITHIN-SOURCE decomposition that
  needs no null at all. It is reported for both substrates and is the transport
  statement that survives even under T_DEGENERATE.
* The 35-actor cohort (+ mirror gi 928 if present in keep_wA) on cutwA is
  **DESCRIPTIVE**: the 100 draws swap the CARRIER's out-edges and are not a
  null for any other source (L211's limitation, inherited verbatim).
* The first-hop menu INVARIANCE across draws is re-**MEASURED** on cutwA
  (CERT-MENUCUT, halting), never inherited from f4wA: if it holds, D_fh on
  cutwA is again a SELECTION effect among a fixed 80-edge menu, by
  construction, and the verdict must say so (L211's law: name what the null
  cannot move BEFORE decomposing against it).

## Registered gates (all HALTING)

1. **CERT-SI** — every leaf of the rebuilt `o["G2_search_information"]`
   (the verbatim L206 SI block, re-executed) equals `l206/static.json` at
   FLOAT EQUALITY.
2. **CERT-FH** — the first-hop walker (a VERBATIM SOURCE SLICE of
   l211_tail.py lines 92-147, not a re-transcription) agrees with the
   certified `dijkstra_si` at EXACT equality on every pool cell, for the
   carrier, the twin and all 100 f4wA draws; rebuilt null median/p05/p95
   float-identical to the certified block.
3. **CERT-211** (this card's required anchor) — the full `L211_primary` and
   `L211_cohort` blocks of `l211/static.json` reproduced from my own re-run at
   FLOAT EQUALITY, by recursive leaf compare, BEFORE any cutwA number is read.
   This is what licenses calling the cutwA result a TRANSPORT test.
4. **CERT-SIGEN** — ONE generic SI-index builder, applied to f4wA, reproduces
   the certified f4wA specialisation by EXACT ARRAY / LIST equality on
   `START`, `END`, `L_L`, `T_L`, `TGT0`, `pos_in_sorted` and `A_max`, before it
   is applied to cutwA (the CERT-MV / L44 discipline the card asks for).
5. **CERT-REBIND** — after rebinding the module globals to cutwA and back,
   `dijkstra_si(LC_CAR, TGT0)` on f4wA is BIT-IDENTICAL to the pre-rebind
   result on every pool cell: the rebind is reversible and leaked nothing.
   (The card asks for the UNCHANGED certified dijkstra on rebound globals;
   this is the gate that makes that safe.)
6. **CERT-REWCUT** — `rewire_draws` on the cutwA block reproduces
   `l169c/static.json` `P6_rewire_draws` medians and first-five rows at float
   equality (0a).
7. **CERT-MENUCUT** — the cutwA 80-edge menu bit-identical across all 100
   cutwA draws, with `min(relocated) >= 1`.
8. Free inside the verbatim heads: CERT-F4, the three stored gains, the CSR
   orientation, the 20 pool sizes, CERT-178 (420 values), CERT-REW,
   CERT-NULL (8 values), CERT-GEN.
9. Degeneracy guards are SCOPED to the quantities actually read (L218 A1):
   positivity of out-strength per substrate, finiteness of every reported
   mean, never a blanket zero test.

## Named limits (in advance)

* TWO substrates, ONE operator family (anatomical |W_beta|), ONE null family
  (degree-neutral destination swaps, seed 16943) — L207's law: a deficit
  magnitude is null-specific and does not transport. This card tests transport
  of a SHARE, which is dimensionless, not of a magnitude.
* The SI length transform divides by A_max (a domain choice, disclosed; the
  field normalises weights to (0,1] first) and ties in L are broken by heap
  order, not controlled. Inherited from L206 unchanged.
* cutwA and f4wA differ in BOTH their edge set and the carrier's out-degree
  (80 vs 69), so a share comparison is the only honest cross-substrate read;
  bare bit magnitudes are reported with their own log2(out-degree) baselines.
* Relation to L211 declared (the Q219-5 discipline): this is L211's own
  deferred leg, cites L211, and does NOT re-bank L211's finding as independent
  evidence.
