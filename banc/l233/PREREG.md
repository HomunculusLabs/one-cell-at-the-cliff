# L233 — PREREG: does the DESTINATION GEOMETRY explain the asymptote?

Registered 2026-11-24, tick 265 (cron), BEFORE any statistic on the Perron
vector `v1` was computed in this card. Static, zero rollouts, no new RNG
(the null draws are SLICE A's fixed `PERM` boolean matrices).

## The question

L217 refuted the SOURCE-population account of the leftward drift BY
HOMOGENEITY (every super_class and both NT signs carry it in proportion to
their mass), so the asymmetry is a property of the POOLS' OWN IN-WIRING.
L216's asymptote is `A_inf = asym(mean_L(v1), mean_R(v1))` over a joint's
pool cells. This card asks what distinguishes the LEFT pool cells from
their RIGHT homologs in `v1`:

- (a) raw IN-DEGREE,
- (b) IN-MASS,
- (c) position in the Perron mode independent of both (the residual after
  regressing `log v1` on `log in-mass` within pool),
- (d) a small number of high-leverage cells.

Honest escape, named in advance: **if (a)/(b) explain it, the asymptote is a
degree statement and the whole A_inf family demotes to a description of the
pools' in-degree asymmetry — which L205 already measured, and that would be
the finding.**

## PREMISE CORRECTIONS (all written before any v1 statistic)

**0a — the card's "contralateral twin" leg does NOT exist at CELL
granularity.** Feasibility probe `l233_probe.py` (annotations only, no v1,
no connectivity; output `l233/probe.out`): all 8 pool-sides carry a
`cell_type` on 100% of cells, but **ZERO cell types are one-to-one across
sides** in either joint — every shared type has multiplicity > 1 on at least
one side (Ti: 8 shared types, 54 of 56/57 cells pairable; Tr: 13 shared
types, **only 39 of 55** pairable). The homolog leg is therefore registered
at **TYPE granularity**: per shared type, the mean of `v1` on each side.
A cell-level twin is scored FALSE BY UNMEASURABILITY (the L222 rule).

**0b — there are TWO in-mass currencies and they are different objects.**
L205's certified `INMASS` is `|log1p(syn)|` summed over in-edges (no
inhibitory rescaling). The operator that GENERATES `v1` is `OPS[s][op]`,
whose entries apply `BETA_L` to inhibitory edges (beta arm) and divide by
`sqrt(tot_i * tot_j)` (Crofts arm). The **operator-native in-mass**
(`m_op` = row-sum of `OPS[s][op]`) is the quantity whose asymmetry could
mechanically produce `A_inf`; L205's mass is the registered COMPANION and
the PIN. The primary regression uses `m_op`.

**0c — in-degree is operator-INVARIANT within a substrate** (a row count),
so it yields 2 distinct vectors, not 4; its asymmetry is reported per
substrate and re-used across both operators.

**0d — the share is a RATIO OF A DIFFERENCE and is conditioned by
1/|denominator|** (the L175 / L231 CERT-231A law). Registered gate:
`|D_y| >= 0.01` on the log scale for a share to be read as a MAGNITUDE;
below it the share is reported as a DIRECTION with its conditioning factor
`1/|D_y|` printed beside it. `D_y`, `b*D_x` and `D_r` are reported in
ABSOLUTE units in every case.

**0e — a ZERO in the outcome is a model-family verdict** (the L224 law).
The zero fractions of `v1`, `m_op`, `m_205` and in-degree within every pool
are MEASURED and asserted BEFORE any log is taken; if any are nonzero the
log leg runs on the nonzero subset with the dropped count and its side
breakdown reported, and the rank (Spearman, midrank) leg — which admits
zeros — becomes the primary for that cell.

**0f — EFFECTIVE FAMILY WIDTH (the L232 law, registered in advance).**
`PERM` is keyed by `(joint, group)` only, so ONE draw is ONE side
relabelling of Ti (serving 4 cells = 2 substrates x 2 operators) and ONE of
Tr (the other 4). The family of 8 cells consumes **TWO independent
randomisations**. Therefore: the PRIMARY instruments of this card are
MAGNITUDES (the explained share, the top-1 leverage share, the
mirror-matched retention), per the L231 law that a magnitude ratio should
carry a branch and significance only qualify it; permutation percentiles are
reported per cell as DESCRIPTION, and any aggregate significance claim is
made with a multiplicity-free omnibus over the shared draw index, never a
BH family of 8.

**0g — count-free companion (the L231 law).** `A_cell` is a per-unit mean
and silently carries `1/n`. Pool side counts are Ti 56 L / 57 R and Tr 55 /
55, so the `A_tot` companion is computed for every asymmetry in this card
and the identity residual `A_cell + A_n` is reported per cell.

**0h — rank statistics are MIDRANK** (the L221 law) and the distinct-value
count of every ranked vector is printed beside its rho. Spearman/midrank
arrive as a VERBATIM SLICE of `l231_tail.py`, not re-implemented.

**0i — the greedy "how many cells must be dropped" count is a SELECTION
procedure.** It is declared DESCRIPTION, real-data only, with no branch on
it. The registered leverage statistic is the top-1 leave-one-out share,
which has a permutation null.

## REGISTERED QUANTITIES

Per cell `(substrate, operator, joint)`, 8 cells; arms = (f4wA, cutwA) x
(beta, crofts); PRIMARY ARM = **f4wA | beta**.

1. `A_inf` = `side_stats_from(v1[pool_f], v1[pool_e], J)["A_cell"]`
   (L216's expression; certified by SLICE C's CERT-AINF).
2. `A_indeg`, `A_mop`, `A_m205` — the same expression on in-degree,
   operator-native in-mass, and L205's in-mass, each with its own
   permutation percentile and `A_tot` companion.
3. `rho_mop`, `rho_m205`, `rho_deg` = midrank Spearman of `log v1` against
   each predictor within the joint's pool (the L207/L213 prerequisite).
4. `share_mop`, `share_deg`, `share_both` = `b*D_x / D_y` from the OLS of
   `log v1` on the predictor(s) over the joint's pool cells, with
   `D_y = mean_L(log v1) - mean_R(log v1)` and the exact identity
   `D_y = b*D_x + D_r` asserted.
5. `lev1` = `max_i |A_inf^{-i} - A_inf| / |A_inf|` (leave-one-out), with its
   permutation null and the Gini of `|ΔA_i|`.
6. `A_inf_shared` = `A_inf` recomputed over mirror-matched cells only, plus
   the per-shared-type log-ratio `log(mean_L(v1,t)/mean_R(v1,t))`, its
   sign count and an EXACT two-sided sign test.

## BRANCHES (registered in order)

**Q1 — does local in-wiring explain the asymptote?** On the primary arm,
mean of `share_mop` over the two joints:
- `D_DEGREE` if `>= 0.70` → the A_inf family DEMOTES to L205's in-mass
  asymmetry description (the card's own escape).
- `D_PARTIAL` if in `[0.30, 0.70)`.
- `D_MODE` if `< 0.30` → the asymmetry is a position-in-the-mode property
  beyond local in-wiring.

**Q2 — is it a few cells?**
- `L_CONCENTRATED` if `lev1 >= 0.50` on the primary arm (either joint).
- `L_DISTRIBUTED` otherwise.

**Q3 — does the mirror-matched subset keep it?** On the primary arm, Ti:
- `H_ROBUST` if `A_inf_shared` has the same sign as `A_inf` and
  `|A_inf_shared| >= 0.50 |A_inf|`.
- `H_COMPOSITION` otherwise → the asymmetry rides on cell types present on
  only one side, i.e. an annotation/reconstruction composition effect of the
  kind L231 found in the optic lobe.

## PREDICTIONS (registered before measurement)

- **P1** `rho_mop >= +0.50` on the primary arm for BOTH joints.
- **P2** `sign(A_m205) == sign(A_inf)` on the primary arm for BOTH joints.
- **P3** Q1 = `D_PARTIAL`.
- **P4** Q2 = `L_DISTRIBUTED` on all 8 cells (`lev1 < 0.50` everywhere).
- **P5** on substrate f4wA, mean over joints, `share_mop(crofts)` is LOWER
  than `share_mop(beta)` by more than 0.20 (Crofts divides by
  `sqrt(degree)`, so its Perron mode should be less degree-explained).
- **P6** Q3 = `H_ROBUST`.

## VERIFY

- SLICE A = `l216_static.py` lines 1-1360 VERBATIM (literal PREFIX, cut
  before the parent's writer, AST-proven write-free) — re-runs CERT-F4,
  CERT-178, CERT-GEN, CERT-205, CERT-GAP, CERT-209 and the lam1 NO-OP.
- SLICE C = `l230_tail.py` lines 39-211 VERBATIM — CERT-216 / NO-OP /
  CERT-AINF / CERT-217 re-used as source (the L225 law).
- SLICE D = `l231_tail.py` lines 429-450 VERBATIM — midrank + spearman.
- **CERT-233A (HALTING)**: `A_inf` recomputed here equals every
  `AINF[cell]["A_cell"]` at FLOAT EQUALITY, and `A_m205` equals
  `l205/static.json`'s stored `A_cell` for both substrates at FLOAT
  EQUALITY (leg (b) is a STORED, already-certified quantity).
- **CERT-233B (HALTING)**: the OLS identity `D_y == b*D_x + D_r` to
  `<= 8*eps` absolute, per cell per predictor set; and the leave-one-out
  recomputation equals a direct `side_stats_from` on the reduced cell set
  at float equality for a sampled 10% of cells.
- **CERT-233C (HALTING)**: pool membership, side counts and the mirror-match
  census asserted exactly as `l233/probe.out` declared them.
- AST import audit (no lab module, L175), AST write-site audit (exactly ONE
  write: `l233/static.json`), `md5sum -c l233/prior.md5` GREEN before and
  after, `(size, mtime_ns)` on every prior artifact unchanged.
