# PREREG — L169 stage (c2): the REW + HOM rollout arms

Registered 2026-11-20 ~10:40 EST (tick 196), BEFORE any computation of this
stage. Lane tick 196. Parent card: LANE.md L169 (ideas 87, external-review
pre-posting controls). Stage (c1) = banc/l169c (premise tests + design pins,
rules C1/C2/C3). This stage spends rollouts.

## Question

(c1) established, statically, that the carrier gi 1110 (DNp33-L) reaches the
antagonist pools only 2-hop and that a degree-preserving rewire of its 80
closure out-edges is expressible and non-degenerate. The dynamic question the
static census cannot answer:

does the PARTIAL -> SUPER flip need the carrier's edges to be REMOVED, or only
to be DISPLACED? And does deleting a cell with a near-identical out-footprint
but a different subnet class flip it too?

## Substrate convention (verbatim, inherited)

l142_run.py extraction, re-used verbatim by l151/l169c: BANC v626 closure
(`keep_new = cord_mask | dn_into | dn_proj`), masses `|log1p(syn) * sign|`
with the flyvis glutamate-inhibitory sign arm, ladder over `dn_new_g` cut at
50% cumulative mass -> K, carrier `GI_CARRIER = 1110` (`ng_desc[24]`).
Base for both new arms: **G1 = cutwA** (`ng_desc[:24]` deleted, carrier
INTACT). No synapse floor (this is the base substrate, not (b2)'s f4).

## Arms (4 new; 12 inherited arms ride along)

- `rew1`, `rew2`, `rew3` — the cutwA NODE SET and EDGE COUNT verbatim, with
  the carrier's 80 closure out-edges degree-preservingly REWIRED. Draws
  **0, 1, 2** of the registered `np.random.default_rng(16943)` stream from
  (c1)'s protocol, re-derived in-run by the same loop (weights travel with
  the source edge, L14 convention; destinations exchanged with partner rows
  in the closure DN->cord block; multi-edge and self-loop proposals
  rejected). Three draws, not one, because a single rewire draw is a
  lottery read (L41/L56 class).
- `hom` — the cutwA node set minus gi **928** (DNp33-R). (c1) rule C2 fired
  NONEQUIVALENT: 928 is a near-perfect FOOTPRINT mirror (88 vs 80 out-edges,
  out-mass 200.05 vs 183.96, intrinsic share .855 vs .870) but a DIFFERENT
  SUBNET CLASS (it receives cord input, so the pure-projector rule never
  admits it to `dn_new_g` and no cut window contains it). This arm is a
  SAME-FOOTPRINT DIFFERENT-CLASS deletion and is labelled as such
  everywhere; it is NOT a homolog control.

Each of the four arms gets its OWN fresh af-matched bisect to
AF_T = 0.10905611018339793 (L118-L131 criteria; stored g_cutwA may NOT be
re-used — REW redistributes per-target in-degree, HOM removes edges).

Inherited arms (full, b65, cutwA, cutng25, silW, eMotTop5, eMotBot5, wAgN,
n25gW, f4wA, f4ng, f4tw) ride along for forward-chain anchors and the
stored-gain certification; nothing about them is re-claimed here.

Batch: FRESH **B37 = 3481-3496** (n=16), anchors 801/901 first. Range
verified absent from all 72 stored raw npzs by key scan before registration
(L157 rule: enumerate from stored KEYS, never batch-number memory).

## Metric (inherited verbatim, no new instrument)

`duty_07` per side on the Ti antagonist pair over the 0.7-Hz windows, the
l109/l111/l113 rounding path (round per seed, then mean) as implemented in
l169_verdict.py / l169b2_verdict.py. Per arm: `kR` = seeds with R-side duty
>= .5 of 16, `meanR`, `meanL`, `kL`, Wilson 95% on kR/16.

House classifiers (verbatim):
- SUPER:   meanR >= .60 and kR >= 12
- PARTIAL: .35 <= meanR <= .50 and 3 <= kR <= 8
- NOT-SUPER (control form): kR <= 8 and meanR <= .50

## Certification block (must be green BEFORE any B37 value is read)

- **CERT-1 (FC-169B2, forward chain, L120 form)**: the 12 inherited arms at
  seeds 801/901 are BIT-IDENTICAL to `l169b2/raw_l169b2.npz` (max|d| == 0.0
  over mm/xm + 20 pool traces + af). Adding arms consumes no generator
  draws, so a non-zero here = stream break = VOID. The inherited FC-169 /
  C0A-150 / FC-144 / FC-145 anchors also re-run unchanged.
- **CERT-2 (stored-form bisects, also the settle-subset certification)**:
  g_cutwA == 0.14365819573402408, g_cutng25 == 0.1454454553127289,
  g_eMotTop5 == 0.1436134350299835, g_eMotBot5 == 0.14367126345634465 must
  re-land EXACT.
- **CERT-REW (the rewire draws)**: the in-run re-derivation of the (c1)
  rewire loop reproduces `l169c/static.json` `P6_rewire_draws` field-for-field
  on the first FIVE draws (relocated / moved / mass_T70 / mass_motor / n_dst)
  and `P5_rewire_pool` (block_edges 64408, partner_rows 64328,
  chance_mass_share_T70 0.007001381033343076). Carrier pins P1 re-derive
  EXACT (80 out-edges, out-mass 183.96376182027785).
- **CERT-REW-DEGREE**: for each of rew1/rew2/rew3 the built CSR has EXACTLY
  the cutwA edge count (any coalescing loss = a multi-edge slipped through =
  STOP), the edge mask `keep[src] & keep[dst_mod]` is elementwise IDENTICAL
  to cutwA's, and the global destination multiset over the touched rows is
  preserved exactly (asserted per draw inside the loop).
- **CERT-HOM**: 928 is present on cutwA, is NOT in any cut window, and its
  deletion removes exactly its 88 out + 13 in = 101 incident closure edges;
  pool sizes / mech size / dng100 size unchanged (S92 pins).
- **C0-NT (non-triviality)**: each new arm's `mm` trace at 801/901 must
  differ from cutwA's (max|d| > 0) and the three rew arms must differ from
  each other. A bit-identical pair = the rewire or the deletion never
  entered the step loop = VOID (L35/L39 dead-channel class).
- **P-af**: each new arm's settled staircase residual |af - AF_T| is
  DISCLOSED, never assumed 0; gate at 5e-3. The rollout af (6000 extra
  steps) is a different quantity and is disclosed only.

## Registered outcome branches

REW decision is by MAJORITY over the three draws (>= 2 of 3 in a class) AND
the pooled n=48 Wilson lower bound vs the same-batch cutwA upper bound:

- **R1_placement** — REW SUPER on >= 2 of 3 draws (and pooled lb > cutwA ub).
  Destroying WHERE the carrier projects is sufficient to flip the readout:
  the cliff is carried by placement, and the honest wording is that the
  carrier's specific targeting (not its presence) is the load-bearing thing.
- **R2_mass_degree** — REW NOT-SUPER on >= 2 of 3 draws. Displacing the
  carrier's mass does NOT flip the readout; only removal does. The cliff
  then needs the mass/degree GONE, not mis-aimed, and §2.7 must say that
  a degree-preserving rewire is bracketed by cutwA, not by cutng25.
- **R3_draw_lottery** — the three draws split (no 2-of-3 majority) or the
  pooled bound straddles. Report as draw-dependent (L41/L56 re-draw class),
  claim nothing about placement vs mass.
- **H1_specific** — `hom` NOT-SUPER. A same-footprint different-class
  deletion does not flip the readout => the flip is not "any heavy DN
  deletion", strengthening the identity claim on the class axis.
- **H2_nonspecific** — `hom` SUPER. A cell outside the cohort flips it too
  => the specificity claim must be re-scoped to "sufficient, not unique"
  on the CLASS axis as well (the L168 wording, one level up).

A branch may be read only from the measured cells, never from a label.
Degenerate-pass guard (L55): if the same-batch cutwA base is itself SUPER
the XOR is vacuous and the verdict states that fact first.

## Scope and honesty constraints

- n = 16 per arm, ONE batch (B37); REW pooled n = 48 across three DRAWS of
  one batch — that is a draw pool, NOT a seed-batch pool, and is labelled so
  (it does not satisfy the L88/L90 multi-batch re-basing rule).
- A rewire destroys placement AND the in-degree pattern of the carrier's
  targets at once; it cannot separate those two. Stated as a limitation.
- The HOM arm changes the node count by one (L142b/L148 law: an isolated
  node is visible only to the af DENOMINATOR) — the af offset is reported.
- No draft edit until the verdict block is green and the branch is read from
  the cells; numbers.json keys and l149_verify section follow the fold.
