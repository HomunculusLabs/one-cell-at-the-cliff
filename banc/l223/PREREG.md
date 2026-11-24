# L223 PREREG — the READOUT-SPECIFICITY claim, nulled properly

Written 2026-11-23 ~13:2x, BEFORE l223_static.py existed and BEFORE any L223
number was measured. Static, zero rollouts, zero settles, zero dynamics.

## The claim under test

L212's strongest honest line: the v783 DNp33 carrier's depth-2 deficit is
**12.86x into motor** and only **1.44x into descending**. But those are two
percentiles (.02 and .29) read against the SAME mass-matched cohort through
two DIFFERENT readouts. Nothing in that pair establishes that the carrier is
unusual in its motor-vs-descending CONTRAST: if every cohort cell shows the
same spread between its two legs, the carrier's pair is generic and the
"readout specificity" story is a restatement of the readouts' sizes
(110 motor cells vs 1,301 descending).

The fix the card registers: make the cohort its own control. For EVERY cohort
cell compute BOTH legs in ONE run (so the cohort is identical by construction),
form a per-cell contrast C, and ask whether the carrier's C is extreme in the
cohort's own joint distribution. Readout size cancels because it is common to
every cell's C.

## 0. PREMISE CORRECTIONS (all pre-measurement)

**0a. The two legs already exist on an identical cohort, so no new cohort is
built.** l212_tail.py lines 1-227 compute `CV = {g: Rfast(SUB, g, LAM1)["R"]}`
over `COH_U = COH_C | COH_M` (motor readout) and `CV2 = {g: Rfast(SUB2, g,
LAM1)["R"]}` over the SAME `COH_U` (descending readout), with `SUB2`'s operator
asserted array-identical to `SUB`'s. Re-running that slice as verbatim source
gives the paired table for free; the card's "both legs recomputed in ONE run"
Verify line is therefore satisfied structurally and not by a promise.

**0b. The contrast must be computed per cell, not from the two published
percentiles.** `carrier_pct` and `mirror_pct` are already cohort-relative, so
differencing them is the SAME two-percentile object the card rejects. C is
defined on the per-cell R values and is then percentiled ONCE.

**0c. Which currency carries the branch, declared now (L218 law).** The card
offers two forms. The PRIMARY is the **log-ratio**

    C_log(g) = log(R_motor(g)) - log(R_desc(g))

because it is COHORT-FREE by construction — a cell's C_log depends only on that
cell, so the carrier's own value cannot move when the comparison set moves
(L222's cohort-relocation law, applied prophylactically). The registered
COMPANION is the **rank difference**

    C_rank(g) = (midrank_motor(g) - midrank_desc(g)) / n

with midranks (average ranks) taken over the common pool COH_C + {carrier}
(n = 101) using the inherited `rankvec`, which is already an average-rank
implementation — the tick-252 midrank law is satisfied by the inherited
machinery, not by a new estimator. **Both are reported; only C_log branches.**

**0d. Zero handling, with a SHORT-CIRCUITING escape (L222 lesson: a registered
escape must change control flow).** l212 records `cohort_zero_frac_carrier =
0.01` on the motor leg, so `log(0)` is reachable. Cells with R_motor == 0 or
R_desc == 0 are EXCLUDED from the C_log vectors and the count is reported. If
the excluded fraction of COH_C exceeds **0.10**, branch
**S_ZERO_DEGENERATE**, the primary SWITCHES to C_rank (which handles zeros as
ties), and the C_log legs are not read — implemented as an `if/else` that skips
the C_log branch block, not as a flag.

**0e. OBSERVATION STATUS (Kriegeskorte 2009; the L214 rule).** While scoping I
read l212/static.json in full. The following are therefore
**OBSERVED-DERIVABLE and declared DESCRIPTION, carrying no branch**:
carrier R_motor 1.6001329420295532e-06, mirror R_motor 1.0027621125362924e-05,
carrier R_desc 1.5709137920956863e-04, mirror R_desc 1.6350700753680461e-04;
hence carrier C_log = -4.5884 and mirror C_log = -2.7914 (and their difference,
-1.797, i.e. the carrier is ~6.0x more motor-specific in its deficit than its
own contralateral twin) are DESCRIPTION. Also observed: both legs' cohort
MEDIANS (2.0581589159220384e-05 / 2.2586693781832335e-04), zero fractions
(.01 / .00), ranks (3 / 30) and percentiles (.02 / .29 carrier, .25 / .36
mirror); so the ratio-of-medians log(-2.3963) is DESCRIPTION too.
**NOT observed, and where every branch lives**: the per-cell joint distribution
of (R_motor, R_desc) over the cohort, its Spearman rho, the distribution of
C_log and C_rank, and every percentile of a contrast. A median of ratios is not
a ratio of medians, so nothing above determines the branch.

## 1. Registered quantities, in the order they are READ

**Q223-0 (read FIRST, as the card demands): rho_spearman(R_motor, R_desc)**
over COH_C, over COH_M and over COH_U, via the inherited `spearman_l`
(midranks). This decides whether the question is answerable at all.

**Q223-1 PRIMARY BRANCH** (read second, and only if Q223-0 is not degenerate):
`pct_of(C_log(carrier), [C_log(g) for g in COH_C])` = fraction of the carrier's
own cohort with a STRICTLY SMALLER C_log (inherited `pct_of`; low = the
carrier's deficit is more motor-specific than the cohort's).

**Q223-2 HOMOLOG LEG** (L207/L212's cheapest control): the same percentile for
the mirror against COH_M, plus both actors scored against the UNION cohort
COH_U (the L222 common-cohort companion) and the COHORT-FREE raw C_log values.

**Q223-3 COMPANION CURRENCY**: the C_rank percentiles for both actors, and the
agreement |pct_log - pct_rank| per actor.

**Q223-4 DESCRIPTIVE**: cohort C_log quantiles (min/p05/median/p95/max), the
carrier's integer rank, the count of excluded zero cells, and the mass-match
log-spread carried forward (.3163 / .3486 — L212's honest Q212-5 FAILURE
against the <=0.15 bar; stated as a limit, not repaired here).

## 2. BRANCH TABLE (registered; evaluated in this order)

| branch | condition |
|---|---|
| **S_ZERO_DEGENERATE** | excluded-zero fraction of COH_C > 0.10 (0d; short-circuits) |
| **S_DEGENERATE** | rho_spearman(R_motor, R_desc) over COH_C >= 0.95 — the two legs carry the same information, the contrast is uninformative, and THAT is the finding |
| **S_SPECIFIC** | carrier C_log percentile <= 0.10 |
| **S_GENERIC** | otherwise |

## 3. PREDICTIONS (registered before measurement)

- **P1** branch == **S_SPECIFIC**.
- **P2** rho_spearman over COH_C lands in **[0.40, 0.95)** — positive (both
  legs share the m_out denominator and overlapping depth-2 paths) but below
  the degeneracy bar (the destinations are disjoint cell sets).
- **P3** carrier C_log percentile **<** mirror C_log percentile (the homolog
  leg orders the same way the raw values do).
- **P4** excluded-zero count over COH_C **<= 2**.
- **P5** |carrier pct_log - carrier pct_rank| **<= 0.10** (the two currencies
  agree for this actor — the check L218 showed can fail).
- **P6** mirror C_log percentile **> 0.10**, i.e. the mirror is NOT specific
  (if both twins are specific, the claim is about the TYPE, not the break).

## 4. VERIFY (the card's own line, plus this card's additions)

- CERT-SRC: every inherited slice re-runs as VERBATIM SOURCE (l212_head in
  three pieces with OUT re-pointed, the three l207_tail function slices,
  l212_tail 1-227 with its writer CUT) — CERT-783, CERT-L207, CERT-MV,
  CERT-GATE, lam1, the rescale NO-OP and Q1/Q2/Q3 all re-run for free.
- CERT-212 (HALTING): the stored l212/static.json Q1/Q2/Q3 table reproduced at
  float equality by RE-RUNNING L212's pipeline, inherited as a verbatim slice
  of l222_tail.py lines 26-88 (re-use as SOURCE, never re-implementation —
  the L211 lesson).
- CERT-PAIR (HALTING, new): CV and CV2 cover the IDENTICAL key set COH_U; the
  two legs' operators are array-equal except for the readout mask; and the
  carrier/mirror entries of CV/CV2 equal the stored Q1/Q2 carrier_R/mirror_R
  at float equality — i.e. the paired table IS the published one.
- CERT-RANK (HALTING, new): `rankvec` is verified to be an AVERAGE-rank
  (midrank) implementation on the actual data — every tie group's members
  receive an identical rank and the rank sum equals n(n+1)/2 exactly — before
  any C_rank number is read.
- PARENT PIN: the builder reconstructs l212_static.py byte-for-byte from the
  three pinned sources; inherited whole-file shas asserted; forbidden-token
  audit; no lab module imported (L175).
- l212/static.json and l207/static.json opened READ-ONLY with (size, mtime_ns)
  fingerprinted before and asserted unchanged after; md5sum -c against
  l223/prior.md5 green before the run.

## 5. LIMITATIONS carried forward (stated, not repaired)

- The v783 mass match is LOOSE: log-spread .3163 / .3486 against the <=0.15 bar
  L212 registered and FAILED (Q212-5). Every percentile here inherits that.
- v783 is brain-only; a DN's real output leaves this volume (L222 measured that
  ALL of both actors' in-brain out-edges sit below synapse 4). The descending
  readout is a within-volume stand-in for "everything else this cell talks to".
- COH_C is 100 cells, so one cell is one percentile point (L207's resolution
  law); a .10 bar cannot separate .10 from .11.
