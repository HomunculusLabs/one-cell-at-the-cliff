# L232 — the CROSSING-EXISTENCE rate as the PRIMARY (static, zero rollouts)

Registered 2026-11-24, tick 264, BEFORE any depth > 8 was read.
Parent artifacts: l216/static.json (depth table + nulls), l217/static.json
(measured crossings + the degeneracy diagnostic), l230/static.json (the
closed form, which predicted an unmeasured crossing at d 15.03).

## The question

L217 registered a timing contrast on `d_cross` and could not score it: its
handedness null produces a MEASURED crossing in BOTH joints in only 0.0505
of draws (0.194 Ti / 0.271 Tr alone). That 0.0505 was a DEGENERACY
DIAGNOSTIC — post-hoc on L217's own card. This card re-poses the event rate
itself as the PRIMARY statistic, on a question whose null is still unknown:
**does the real wiring produce a sign change in A_cell(d) where a
side-label permutation of the same pool cells does not — and is 0.0505 an
effect or a truncation artifact of DMAX = 8?**

## Premise corrections (registered FIRST, all asserted halting)

- **0a. THE CARD'S "12 cells" IS WRONG BY CONSTRUCTION.** The L216 family has
  `len(SUBS) == 2` substrates (f4wA, cutwA) x 2 operators x 2 joints =
  `len(CELLS) == 8`, not 12. The family of **12 TESTS** is instead formed as
  8 single-joint existence tests + 4 pair-level (substrate x operator)
  both-joints-cross tests. Asserted: `len(SUBS)==2`, `len(CELLS)==8`,
  `JOINTS==("Ti","Tr")`, `DMAX==8`, `NDRAW==2000`.
- **0b. EVERY D = 8 QUANTITY IS OBSERVED-DERIVABLE AND IS SCORED AS
  DESCRIPTION** (L214). L217's `null_frac_cross` for all 8 cells and its
  0.0505 both-cross rate are STORED and re-certified by CERT-217 before
  anything new is read. The NEW quantities are the rates at D > 8, the
  plateau depth D*, and every p-value read at D*.
- **0c. THE DRAW STREAM CANNOT MOVE WITH DEPTH.** `PERM[(J, side)]` is a
  fixed boolean matrix built once from seed 20526 before any depth is read,
  so extending the sweep to D = 40 cannot perturb the null. Proven, not
  assumed: CERT-232X asserts the extended sweep's first 8 depths reproduce
  L216's stored `A_cell` at FLOAT EQUALITY and L216's per-draw null vectors
  at ARRAY EQUALITY.
- **0d. THE STATISTIC IS EXISTENCE, NOT DEPTH.** L217's `dcross` returns the
  LAST sign change, interpolated; the registered statistic is
  `n_sign_changes >= 1 within d <= D`, i.e. `dcross(...) is not None`. The
  interpolated depth is NOT read by any branch here.
- **0e. THE EXISTENCE RATE IS MONOTONE NON-DECREASING IN D BY
  CONSTRUCTION** (it is a cumulative ANY over sign-change indicators), so
  the plateau criterion reduces to a LEVEL condition. Monotonicity is
  asserted as a check, never claimed as a finding.
- **0f. A PLATEAU CAN BE NUMERICALLY FORCED RATHER THAN STRUCTURAL.**
  `A_cell(d) - A_inf` decays as rho^d; once it is below float resolution the
  sign of A_cell(d) is pinned by A_inf and no further crossing is possible.
  Register the per-cell SATURATION depth = smallest d with
  `|A_cell(d) - A_inf| < 1e-12`, and report whether D* sits before or after
  it. A plateau reached only after saturation is reported as numerically
  forced.
- **0g. D_BIG = 40 AND THE GRID D = 2..40 ARE FIXED IN ADVANCE**, not tuned
  to an outcome.
- **0h. UNMEASURABLE IS NOT ABSENT** (L222). A test whose REAL cell does not
  cross within D* has no event to test; it is scored **FALSE BY
  UNMEASURABILITY**, named, and EXCLUDED from the BH family, with m = the
  number of MEASURABLE tests and the rank-1 bar q/m printed against the
  worst resolution floor 1/(NDRAW+1) = 4.9975e-04.
- **0i. A D-DEPENDENT p IS A TRUNCATION ARTIFACT AND MUST BE REPORTED AS
  ONE** — registered in advance, per the card's own wording.

## Registered quantities and branches

**Q1 (primary) — is 0.0505 an effect or a truncation artifact?**
`D*` = smallest D in the grid with
`max over the 8 cells of (rate(D_BIG) - rate(D)) <= 0.01`.
`p_both(D)` = fraction of draws in which BOTH joints cross within d <= D, on
the primary arm f4wA|beta. `ratio = p_both(D*) / p_both(8)`.
Branches, in this registered ORDER:
1. **T_NO_PLATEAU** — no D in the grid satisfies the criterion.
2. **T_TRUNCATION** — `ratio >= 2.0`.
3. **T_STABLE** — `|ratio - 1| < 0.5`.
4. **T_INTERMEDIATE** — otherwise.

**Q2 — the NONSELECTIVE family (Kriegeskorte step 1), BH-FDR q = 0.05.**
12 registered tests at D*: 8 single-joint (p = the cell's null existence
rate) + 4 pair-level (p = the arm's null both-cross rate), each scored only
where the REAL event exists (0h).
Branches: **E_FAMILY_SIG** (>= 1 BH rejection) / **E_FAMILY_NULL** (none).

**Q3 — the omnibus with no multiplicity at all.** `PERM` is indexed by joint
and side, so draw j is one side-relabelling readable across all 8 cells:
`N_cross(j)` = how many of the 8 cells cross within D* under draw j;
`N_real` = how many of the 8 real cells do. `p_omni = mean(N_cross >= N_real)`.
Branches: **O_REAL_EXTREME** (`p_omni <= 0.05`) / **O_REAL_TYPICAL**.

## Predictions (registered before the run)

- **P1** a plateau exists within D_BIG = 40 (`D*` is not None).
- **P2** `p_both(D*) > p_both(8)` — the null's event rate RISES with D.
- **P3** T_TRUNCATION fires (`ratio >= 2.0`).
- **P4** at least one of the 12 tests is BH-rejected at q = 0.05.
- **P5** the real wiring crosses in MORE than 6 of 8 cells at D* — i.e. at
  least one of L217's two censored cells crosses by D* (L230's closed form
  predicted f4wA|crofts|Ti at d 15.03).
- **P6** `p_omni < 0.05`.

## Verify (the card's own line)

CERT-216 and CERT-217 HALTING, re-used as VERBATIM source slices of
l230_tail.py; the null draw stream reproduced at float/array equality before
any new D is read (CERT-232X); no prior artifact written (AST write-site
audit + (size, mtime_ns) fingerprints + md5sum -c on l232/prior.md5 before
and after).
