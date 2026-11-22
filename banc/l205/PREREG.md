# L205 PREREG — the floor-4 handedness static (L175 G4's unrun half)

Registered 2026-11-22 ~10:15 EST, tick 234, BEFORE any L205 number was read.
Zero rollouts, zero settles, zero dynamics. CPU only. No live changes.

## The observation this card interrogates

L175 (tick 231) measured, descriptively, per-seed SIDE DOMINANCE of the Ti
antagonist antiphase statistic S and found it substrate-dependent and
batch-reproducible (5/5 arms across B36 and B37):

- FLOORED arms are LEFT-dominant: f4wA 16/16 seeds S_L > S_R, f4tw 16/16,
  f4ng 12/16.
- BASE arms are RIGHT-dominant: cutwA 3/16 seeds S_L > S_R, cutng25 1/16.

The STATIC question was never asked: **is the flip already visible in the
wiring?**

## Substrates (all seven, both sides, reported whether or not they gate)

Base family (no edge floor):
- `base_closure` = emask_n (G0, the L151 head's closure)
- `cutwA`        = emask_wA (drop ng_desc[:24])
- `cutng25`      = emask_25 (drop ng_desc[:25])

Floored family (pair-level edge floor syn_count >= 4, `pm4`):
- `f4_closure` = emask_n & pm4
- `f4wA`       = keep_f4 (drop ng4[:20]) & pm4   [the L178/L169b2 substrate]
- `f4ng`       = drop ng4[:21], & pm4
- `f4tw`       = drop ng4[:20] + ng4[21], & pm4

Arm definitions are the l169b2_run.py F4_DROP convention verbatim. The f4
edge count is asserted == the stored 469,618 (f4wA) and the base counts
against the stored L151 pins, before any L205 value is read.

## Instrument (the primary object)

Per substrate E, per joint J in {Ti, Tr}, per side s in {L, R}:

- `n_s`  = pool size = |J_f{s}| + |J_e{s}| (node-level, substrate-invariant
           by the L151/L178 pool pins — asserted, not assumed)
- `M_s`  = total in-mass = sum over edges of E with dst in (J_f{s} U J_e{s})
           of |log1p(syn)*sign| (the ladder convention, the house mass)
- `m_s`  = M_s / n_s (per-cell in-mass; registered as the PRIMARY form
           because Ti pool sizes are themselves asymmetric, 50/51 flexor)
- `A_cell` = (m_L - m_R) / (m_L + m_R)   PRIMARY asymmetry
- `A_tot`  = (M_L - M_R) / (M_L + M_R)   companion

Sign convention registered: **A > 0 means LEFT carries more in-mass.** The
dynamic dominance is L-dominant on floored arms, so H_STATIC predicts
A_cell(floored) > 0.

## Null (L45b/L70 handedness class — permute membership before hunting wiring)

MEMBERSHIP PERMUTATION, 2000 draws, seed 20526, numpy default_rng:
within each antagonist group of a joint (the 101 Ti flexor cells, the 12 Ti
extensor cells; 62 Tr flexor, 48 Tr extensor), permute the L/R side labels
while holding the per-side counts EXACTLY at the real values (Ti 50/51 and
6/6; Tr 31/31 and 24/24). Per-cell in-mass vectors are computed ONCE per
substrate from the real wiring; the null re-splits those same cells between
sides. The null therefore asks: *is the L/R split of in-mass more extreme
than a random relabelling of these same motor cells?*

Percentiles are reported as the fraction of draws with null statistic
<= real (one-sided-up) and the two-sided |A| percentile. Draws are SHARED
across substrates (one permutation matrix) so the paired delta below is a
genuine paired null.

## Gate cells — SEPARATE objects, never ANDed (L109)

- **C1 FLOORED (branch-bearing).** On `f4wA`, Ti: A_cell > 0 AND
  one-sided-up percentile >= 0.95.
- **C2 BASE (branch-bearing).** On `cutwA`, Ti: A_cell < 0 AND
  one-sided-up percentile <= 0.05.
- **C3 FLIP (branch-bearing).** delta = A_cell(f4wA) - A_cell(cutwA) > 0 AND
  the paired delta's one-sided-up percentile >= 0.95.
- **C4 MECHANISM (descriptive, no branch).** Per-side edge-count and
  in-mass retention under the floor (what fraction of each side's cutwA
  in-edges and in-mass has syn_count >= 4), the full 7-substrate x 2-side
  table, and the per-sub-pool (flexor vs extensor) decomposition.
- **C5 SHARED-DRIVE COMPANION (descriptive, no branch).** Per side, the
  shared-source in-mass between the flexor and extensor pool
  (sum over sources of min(mass_to_flex, mass_to_ext)) and its L/R
  asymmetry under the same permutation null. Registered because S is a
  flexor-extensor CORRELATION and common drive is the nearer static
  analogue than bulk in-mass; it carries NO branch this tick.

## Branches, registered now

- **H_STATIC** — C1 fires AND C3 fires: the floored graph's left Ti pools
  already carry significantly more in-mass than a membership relabelling
  allows, and the floor MOVES the asymmetry leftward. The dynamic dominance
  flip then has an anatomical precursor and is, to that extent, an
  edge-floor bookkeeping effect.
- **H_DYNAMIC** — C1 does NOT fire because the real A_cell sits INSIDE the
  null band: in-mass asymmetry is not wiring-carried at this depth, so the
  dominance flip is a dynamics/attractor property (L45b class).
- **H_STATIC_NOFLIP** — C1 fires but C3 does NOT: the wiring is L-biased in
  in-mass on BOTH families, so a static in-mass asymmetry exists but cannot
  explain the substrate-DEPENDENT flip. Registered explicitly because it is
  a live possibility and would otherwise be reported as a half-H_STATIC.

## Honest limits, written before measuring

1. An in-mass is a DEPTH-1 anatomy read. The dynamic S is a within-side
   flexor-extensor correlation. A static in-mass asymmetry is a plausible
   precursor, not a necessary one: H_DYNAMIC firing does NOT prove the
   wiring is side-symmetric at every depth, only at this one. C5 exists to
   soften exactly this gap and is descriptive.
2. The Ti flexor pools are already SIZE-asymmetric (50 L / 51 R). That is
   why A_cell (per-cell) is primary and A_tot is the companion — a bulk-mass
   asymmetry of ~1% could be pure pool size.
3. `A` is a RATIO. Per the L175 denominator law it is reported as a
   direction with its absolute masses printed beside it, never as a
   magnitude on its own.
4. The permutation null preserves per-side COUNTS but not any other
   anatomical covariate (neuromere is unavailable on BANC — the L65 law).
   It is a handedness null, not a degree null, and is labelled as such.
5. P1-form estimand: no gains, no op point, no re-tuning — this is pure
   anatomy, so the P1/P2 distinction does not bite here.

## Verify (the card's own line)

- Graph build NOT re-written: `l205_static.py` is GENERATED with
  HEAD1 = `l151_static.py` lines 1-319 byte-for-byte (the l142_run.py
  extraction + ladder + pools) and HEAD2 = `l178_tail.py` lines 22-83
  byte-for-byte (CERT-F4: the f4 ladder re-derivation + the stored-gain
  float-equality leg), both sha256-pinned and asserted to be literal
  slices of their sources, with a forbidden-token audit. DISCLOSURE: the
  card said "imported from l169b2_run.py"; a literal `import` is forbidden
  by the L175 lesson (a lab run script is a SCRIPT — importing it rewrites
  its artifacts), so the verbatim-source-slice form is used instead and
  this substitution is disclosed in the verdict.
- f4 edge set re-derived by the stored convention, count asserted
  == 469,618 (and 472,095 closure / 469,256 wA).
- Both substrate families and BOTH sides reported, gating or not.
