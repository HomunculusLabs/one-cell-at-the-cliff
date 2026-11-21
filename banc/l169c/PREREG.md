# PREREG — L169 stage (c1): design pins + premise tests for the rewire / right-homolog arms

Registered 2026-11-20 ~08:0x EST (tick 194), BEFORE any computation for this
stage. Zero rollouts. House rule precedent: L169 (b1) ran a PREMISE TEST before
building the (b2) dynamic machinery; the same split is applied here because the
card's stage (c) presumes two things it never checked — that a degree-preserving
rewire of the carrier's edges is expressible and non-degenerate, and that gi 928
is a *mirror homolog* control of the carrier gi 1110.

## Substrate convention (verbatim, inherited)

Graphs are built by the l142_run.py extraction, re-used verbatim by
l151_static.py: BANC v626 closure (`keep_new = cord_mask | dn_into | dn_proj`),
masses `|log1p(syn) * sign|` with the flyvis glutamate-inhibitory sign arm,
ladder = out-mass over `dn_new_g` (closure-only pure projectors) cut at 50%
cumulative mass -> K, split glut 19 / non-glut 58, carrier `GI = 1110`
(`ng_desc[24]`), mass twin `319` (`ng_desc[25]`).
Bases: **G0** closure, **G1** cutwA (`ng_desc[:24]` deleted, carrier intact),
**G2** eAll (G1 minus the carrier's 93 incident edges; bit-identical to
cutng25 by the L142b law and L148's se0 identity).

## What stage (c2) will run (registered here, not yet run)

Two rollout arms on the G1 cutwA base, inherited R-side classifiers:

- **REW** — the carrier's closure out-edges degree-preservingly REWIRED
  (placement destroyed, out-degree and each target's in-degree preserved,
  weights travel with the source edge per the L14 focused-null convention).
  G1 and G2 bracket it: same mass and degrees as G1, same loss of specific
  placement as G2. Registered prediction: if the identity cliff is carried by
  WHERE the carrier projects, REW reads like cutng25/eAll (SUPER); if it is
  carried by the carrier's mass/degree alone, REW reads like cutwA (PARTIAL).
- **HOM** — node deletion of gi 928 (DNp33, right side) from the G1 base,
  a specificity control complementary to the mass-matched twin.

## Premise tests and registered rules (this stage)

Every number below is RE-DERIVED inside `l169c_static.py` from the graph and
annotation tables; nothing is quoted from LANE-LOG prose, from l147's stored
census, or from the card text (L44 rule).

**Rule C1 — homolog-arm vacuity / confound.**
If `928 ∈ ng_desc[:25]` the HOM arm is VACUOUS-BY-DESIGN on the G1/G2 bases
(the cell is already deleted there) and (c2) must register an amendment.
Branch `C1_independent` = 928 is not inside the cut window; the arm is an
independent deletion. The cohort membership of 928 (`dn_new_g` / `ng_desc` /
`glut_desc` / `heav`) is reported either way.

**Rule C2 — mirror-equivalence premise (the card's own word, "right homolog").**
Fires `C2_mirror` only if ALL FOUR hold:
 (i) same subnet class as the carrier (both `pure_proj`, i.e. both in
     `dn_new_g`, or both `dn_into`);
 (ii) closure out-edge count within a factor 2 of the carrier's;
 (iii) closure out-mass within a factor 2 of the carrier's;
 (iv) destination tier split (intrinsic / motor_other / vnc_sensory) matching
      the carrier's within 20 percentage points on the intrinsic share.
Any failure fires `C2_nonequivalent`: the HOM arm is then re-labelled in (c2)
as a DIFFERENT-CLASS heavy-DN deletion, never as a mirror control, and the
failing axis is named in the artifact.

**Rule C3 — rewire feasibility and non-degeneracy.**
Protocol (registered): double-edge swaps restricted to the closure DN->cord
edge block (rows whose source is a descending cell present on the base and
whose destination tier is in {intrinsic, motor_other, vnc_sensory}), one swap
proposal per carrier out-edge per draw, multi-edge and self-loop proposals
rejected, weights travel with the source edge, `np.random.default_rng(16943)`,
**100 draws**. The arm is admissible only if
 (a) **expressible**: the partner pool has >= 10x the carrier's out-edge count,
     and >= 95% of the carrier's out-edges are successfully relocated in the
     median draw;
 (b) **non-degenerate**: the median draw returns < 10% of the carrier's
     out-mass to its own T70 sheet (otherwise a rewire cannot isolate
     placement and (c2) must use a different null);
 (c) **degree-neutral**: by construction the base edge COUNT is unchanged;
     asserted exactly, and the per-target in-degree vector of the base is
     asserted unchanged for every draw.
Failure of (a) or (b) registers an amendment naming the replacement null
(candidate: destination-swap within tier, the L11/L14 form) rather than
silently shipping a degenerate rewire.

## Design pins to store (P1-P7)

- **P1** carrier footprint on G1: out-edge count, in-edge count, incident total,
  raw out-mass (the three l134/l151 pins must re-derive EXACT).
- **P2** 928 identity: root id, side, `super_class`, cell type string, NT
  prediction, membership booleans (`cord_mask`/`dn_into`/`dn_proj`/`dn_new_g`).
- **P3** 928 footprint on G0 and G1: out/in edge counts, out-mass, tier split.
- **P4** overlap of 928's destinations with the carrier's T70 sheet and T10
  motor set (counts + Jaccard), and the SIDE composition of each cell's
  motor destinations (the L151 crossed law predicts the carrier reaches
  right-side pools; a true mirror would reach the left).
- **P5** the rewire partner-pool size and the carrier's swappable fraction.
- **P6** per-draw statistics over the 100 registered draws: relocated edge
  count, mass returned to T70, mass landing on motor cells, and the number of
  distinct destination cells.
- **P7** fresh af-matched bisect is REQUIRED for both (c2) arms (REW changes
  no edge count but changes in-degree per target, HOM deletes edges); the
  stored g_cutwA / g_cutng25 values may NOT be re-used. Recorded as a
  requirement, not computed here.

## What this stage may NOT do

No draft edit unless a premise test refutes a clause already in DRAFT.md; no
rollouts; no new numbers.json keys unless a refutation is folded. l151/static.json
is never rewritten (the build script's residual scan refuses any surviving write
to it). CERT-1 re-derives l151's own s1/s2/s3 blocks and asserts them equal to
the stored artifact before any new value is read.
