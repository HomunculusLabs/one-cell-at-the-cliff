# L213 PREREG — TYPE or CLASS? (static, zero rollouts)

Registered 2026-11-22 ~20:30 EST, tick 242, BEFORE any type-level aggregate,
class aggregate, or permutation draw was computed. Zero rollouts, zero
settles, no RNG except the registered label permutations.

## The question

L207 established that BOTH members of the bilateral DNp33 pair sit at
percentile 0.06-0.10 of a mass-matched cohort of present descending cells,
on all three substrates, for the anatomical statistic

    R(c) = P2(c) / (lam1^2 * m_out(c))

with P2 = depth-2 |weight| reach into the 20 semantic leg-motor pools,
BETA_L = 2.0 on inhibitory edges, m_out = total |log1p(syn)*sign| out-mass.
L207's verdict called that "a cell-TYPE property". This card asks whether
that is right, against the obvious alternative:

  (i) a **DNp33 type** property, or
  (ii) a property of the broader **class** the carrier belongs to —
       pure-PROJECTING descending cells (`dn_proj & ~dn_into`, the l169c
       `pure_proj` flag).

## PREMISE CORRECTION, found in scoping and written BEFORE any measurement

`l213_scope.py` (scoping only, writes nothing) reports:

    DNp33 present members: [928, 1110]
    DNp33 pure_proj flags: [False, True]

**The carrier (gi 1110, DNp33-L) is pure_proj; its contralateral homolog
(gi 928, DNp33-R) is NOT** (it has at least one cord -> DN edge, so
`dn_into` is True and `pure_proj` is False). The two cells L207 found to
avoid at pct .06-.10 sit in DIFFERENT classes under the very flag
hypothesis (ii) proposes as the explanation.

This is registered as a premise because it changes what the card can
conclude, and it changes it BEFORE the numbers:

- Hypothesis (ii) in its strong form ("the avoidance is the pure_proj
  class") is already strained: a class cannot explain a property shared by
  a member and a non-member. It is NOT yet refuted — the class could be low
  AND the mirror low for an unrelated reason — which is exactly why Q3 is
  registered as a per-cell, within-own-class conditional and not as a single
  pooled test.
- Q3 therefore reads the carrier inside the pure_proj class and the mirror
  inside the NON-pure_proj class. Registering one pooled "within pure_proj"
  number would have been the wrong instrument and would have silently
  dropped the mirror (L109: gates are separate cells).
- The scoping script read no R value, no reach, no eigenvalue, and wrote no
  artifact; its entire output is the membership counts quoted here.

## Population, substrates, statistic (all fixed here)

- Substrates: the three L207 substrates, built by the certified generic
  `build_sub` — `G0_closure` (n 21809 / 647953), `G1_cutwA`
  (21785 / 644177), `F4_f4wA` (21789 / 469618).
- Population per substrate: every **present descending** cell
  (`keep & dn_all`) with `m_out > 0`. The carrier and the mirror are IN the
  population (they are part of the type and class distributions they are
  being read against).
- Statistic: R exactly as above, anatomical, g-free (L209: R is invariant to
  a global rescaling of the operator, so cross-substrate comparison needs no
  re-bisected gain).
- lam1 per substrate from the certified `power_iter_sub`, rel spread < 1e-6
  asserted or the run STOPS.

## The three gates, as SEPARATE cells (L109) — never ANDed

### Q213-1 TYPE: where does DNp33's type median fall?

Group the population by `cell_type` (non-empty, not "nan"); keep types with
>= 2 present members. Type statistic = median R of its present members.
DNp33 has exactly 2 present members on the closure, so its "median" is the
mean of two values — stated as a 2-point statistic everywhere.

NULL (type-level, as the card requires — NOT L207's per-cell cohort
percentile): stratify the population into MASS STRATA by log m_out
(10 equal-count strata, boundaries by quantile, assert per-stratum counts),
then permute the R vector WITHIN each stratum. Every draw preserves (a) each
type's size, (b) each type's stratum composition, (c) the per-stratum count
vector — asserted exactly on EVERY draw. 2000 draws, seed registered below.
Read: the null distribution of the DNp33 type median, and the percentile of
the real value in it.

Branches (four cells):
- `T_TYPE_LOW`      null pct <= 0.05
- `T_TYPE_TYPICAL`  0.05 < null pct < 0.95
- `T_TYPE_HIGH`     null pct >= 0.95
- `T_DEGENERATE`    any stratum assert fails, DNp33 has < 2 present members
                    on a substrate, or a power iteration fails.

Verdict rule across substrates: the branch is called by the modal reading
with >= 2 of 3 substrates agreeing; a 1/1/1 split is `T_MIXED` and reported
as no call.

### Q213-2 CLASS: are pure_proj cells shifted low as a class?

Statistic: median R of pure_proj present cells minus median R of
non-pure_proj present cells, in log10 R (a ratio of medians, reported as the
ratio too). NULL: permute the pure_proj FLAG within the same mass strata,
2000 draws, same per-stratum asserts. Read the real difference's percentile.

Branches: `C_CLASS_LOW` (pct <= 0.05) / `C_CLASS_TYPICAL` / `C_CLASS_HIGH`
(pct >= 0.95) / `C_DEGENERATE`. Same >= 2-of-3 rule.

### Q213-3 CONDITIONAL: is DNp33 still extreme WITHIN its own class?

For each actor, its percentile among the present cells of ITS OWN class:
carrier within pure_proj, mirror within non-pure_proj (the premise
correction above). Fraction of class members STRICTLY SMALLER (low =
avoider), same `pct_of` convention as L207.

Branches:
- `D_TYPE_SURVIVES`  both actors <= 0.10 on the substrate
- `D_CLASS_EXPLAINS` both actors > 0.10 (the avoidance was the class)
- `D_SPLIT`          one <= 0.10, one > 0.10
- `D_DEGENERATE`     an actor absent from the substrate

Same >= 2-of-3 rule. NOTE, registered: this is a WITHIN-CLASS percentile and
NOT mass-matched, so it is a different null from L207's cohort and its
MAGNITUDE does not transport (L207's own cross-null law). It answers
"extreme within the class", nothing more.

## Derived reading (not a branch)

- (i) TYPE property reads iff Q3 = `D_TYPE_SURVIVES`.
- (ii) CLASS property reads iff Q2 = `C_CLASS_LOW` AND Q3 = `D_CLASS_EXPLAINS`.
- Anything else is stated as a mixture, with the premise correction as the
  reason the strong class reading was already unlikely.

## Honest limits, written first

1. With only 2 present members a type median is a 2-POINT statistic. The
   strongest verdict available is a DIRECTION, never a magnitude. No
   "Nx deficit" headline will be attached to the type median.
2. One type, one class flag, one statistic, one null family. The class
   question is asked of `pure_proj` ONLY because that is the flag the card
   names; other partitions of descending cells are not tested.
3. Anatomical leg only (no row mask, no settle, no seed) — wiring geometry,
   not an operating point (L164).
4. The within-stratum permutation holds mass and type SIZE but not
   neurotransmitter, side, or neuropil composition.

## Predictions (scored, honest either way)

- Q213-P1: Q1 = `T_TYPE_LOW` on >= 2 of 3 substrates.
- Q213-P2: Q2 = `C_CLASS_TYPICAL` — I do NOT expect pure_proj to be a low
  class. Reason: `dn_proj` is by definition "has an out-edge into a cord
  cell", which should if anything RAISE pool reach; the `~dn_into` half is
  about what the cell RECEIVES and should be near-neutral for an out-reach
  statistic.
- Q213-P3: Q3 = `D_TYPE_SURVIVES` on all 3 substrates.
- Q213-P4: the MIRROR's within-non-pure_proj percentile <= 0.10 on all 3
  substrates (the sharp consequence of the premise correction).
- Q213-P5: DNp33's type-median null percentile <= 0.02 on >= 2 of 3
  substrates (sharper than the P1 branch bar).

## Verification plan (the card's Verify line, made halting)

- **CERT-SRC**: the script is GENERATED from verbatim, sha256-asserted source
  slices of already-certified scripts (l151_static.py 1-319, l178_tail.py
  7-149, l206_mid.py, l206_tail.py 22-121, l207_tail.py slices for
  `build_sub` / `reach_sub` / `power_iter_sub` / `Rstat` / `pct_of`), with a
  forbidden-token audit. NO lab module is imported (L175: a lab run script is
  a SCRIPT, not a library).
- **CERT-207 (HALTING)**: before any type or class aggregate is read, the
  verbatim `reach_sub`/`Rstat` path must reproduce, at FLOAT EQUALITY, every
  R / R1 / P2 / m_out in L207's stored `ladder_table` for all three
  substrates (58 + 34 + 35 = 127 cells x 4 fields = 508 values) AND the two
  slot comparators (gi 80 at closure slot 21, gi 32072 at f4wA slot 25) AND
  L207's stored Q2 mirror_R / carrier_R per substrate. l207/static.json is
  opened READ-ONLY with size+mtime_ns fingerprinted before and asserted
  unchanged after (L175: never rewrite another card's artifact).
- **CERT-T**: the fast census kernel (two transposed matvecs give P1 and P2
  for ALL sources at once, using the same `np.add.at` expression with the
  index arrays swapped — the L210/CERT-MV transpose identity) is GATED, never
  trusted: it must agree with the verbatim `reach_sub` on all 127 L207 ladder
  cells plus both actors to max relative difference < 1e-12 (the summation
  ORDER differs, so float equality is not claimed — L206's expression law),
  and the bilinear identity 1_pools^T A^2 e_c == e_c^T (A^T)^2 1_pools is
  asserted on probes.
- Per-stratum count vector asserted EXACT on every one of the 2000 draws,
  both nulls; a single failure raises and the branch reads `*_DEGENERATE`.
- Pool sizes invariant on all three substrates with zero overlap (inherited
  asserts in `build_sub`).
- Writes `l213/static.json` ONLY.

## Registered constants

    BETA_L = 2.0          (inherited, L207 convention)
    N_DRAWS = 2000
    SEED = 21342
    N_STRATA = 10
    PCT_BAR = 0.10        (Q3 actor bar, L207's bar)
    NULL_BAR = 0.05       (Q1/Q2 null-percentile bar)
    GI_CARRIER = 1110, GI_MIR = 928, TYPE = "DNp33"
