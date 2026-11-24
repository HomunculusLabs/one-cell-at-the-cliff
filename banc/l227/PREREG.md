# L227 PREREG — the MIRROR COEFFICIENT as a required pre-step

Written BEFORE the measurement script exists and BEFORE any simulation is
run. Tick 257 (2026-11-23), lane item L227. ZERO rollouts, zero GPU: every
empirical input is read from already-stored jsons
(`l214/static.json`, `l214/addendum.json`, `l208/static.json`,
`l200/results_l200.json`, `l202/results_l202.json`), opened READ-ONLY and
never rewritten. No lab module is imported (L175).

L226, the first unchecked item above this one, is the ROLLOUT card; this
tick's `nvidia-smi` read 99% utilisation, so the lane ground rule ("if
utilization >80% ... do a read/verify-only tick instead") sends the tick to
the next static card. L226 stays unchecked.

## PREMISE CORRECTIONS, registered first

### 0a — one of the card's four pairs is an ALGEBRAIC IDENTITY, not a pair

The card asks for the mirror coefficient of `lvl vs margin`. L208's own
stored definition makes the margin currency the LEVEL currency with its
sign flipped: `margin = RMAX - lvl`, so for any two sides
`dM = (RMAX - lvl_R) - (RMAX - lvl_L) = -(lvl_L - lvl_R)`. The mirror is
EXACT with slope -1, by construction, for every cell, and no measurement
can make it anything else. Consequence, proved rather than predicted:
Spearman is invariant under a strictly increasing transform and flips sign
under a strictly decreasing one, so for a mirror pair
`rho_M = -rho_A` cellwise, hence `|rho_M| = |rho_A|` cellwise, hence the
L214 head-to-head statistic `D = mean(|rho_A| - |rho_M|)` is IDENTICALLY
ZERO and its sign-flip permutation p is 1 — **a magnitude head-to-head on
an exact mirror pair has exactly zero power, no matter how different the
two currencies' directional content is.** That is the analytic arm the card
asked for, and it needs no simulation.

Registered as a GATE, not a prediction (the identity is arithmetic):
`mean_dM == -(lvlL - lvlR)` on all 20 stored cells. It is checked with a
tolerance DERIVED FROM THE DATA (`4 * eps * max|lvl|`), never at float
equality and never at a guessed bar: `mean_dM` is a mean of per-seed
differences while `lvlL`/`lvlR` are means of per-seed levels, so the two
expressions differ in summation order. L218's law — an exact-arithmetic
no-op licenses the SCIENCE, never the float-equality GATE; L216/L224 — a
bar must be derived, never fixed in advance.

### 0b — one of the card's four pairs is DEGENERATE BY DATA

`flo vs fhi` cannot be measured: `fhi95L/R` and `fhi90L/R` are stored and
are **identically 0.0 on all 20 cells** (read during scoping, so this is
OBSERVED and is reported as DESCRIPTION, never as a prediction). A Spearman
against a constant vector is undefined (zero variance), so the pair scores
`C_DEGENERATE` and carries no threshold. This is L208's operating point
restated with a number: at a sparse relu operating point nothing is near
ceiling, so the ceiling-side currency never fires at all.

### 0c — the fourth pair lives in a DIFFERENT family and has no shared regression

`duty vs S-mean` is stored in `l200/results_l200.json` and
`l202/results_l202.json` — a different substrate family (the sc25 / l2c
cord graphs, different seeds, different cells). The L214 head-to-head is
`mean(|rho_A| - |rho_M|)` where each `rho` is a WITHIN-cell rank
correlation of one currency against a SHARED dominance variable; l200/l202
store per-arm scalars with no such shared regression, so the magnitude
instrument does not exist there. The pair is therefore scored
`C_NOT_APPLICABLE` for the threshold rule, and its mirror coefficient is
measured anyway, as DESCRIPTION, to serve as the **not-a-mirror positive
control**: if every pair the lane ever measured were a near-mirror, a
threshold rule would be vacuous.

### 0d — the card quotes the WRONG MIRROR COEFFICIENT for its own statistic

The card says "the ceiling/floor pair at r -.856 already sits past the
threshold". `-0.8556390977443609` is the stored Spearman between the two
currencies' per-cell MEANS (`mean_A` vs `mean_dM`). The `D` statistic is
not computed from currency means; it is computed from the per-cell
correlations, whose stored mirror coefficient is
`spearman_rhoA_rhoM = -0.6766917293233082`. Two different mirror
coefficients for the same pair, differing by 0.179. **A threshold rule must
be stated in the currency the instrument actually consumes**, so the rule
is registered in the `rho`-mirror currency and the card's `-0.856` is
reported beside it as the currency-level mirror. Both are OBSERVED (read
during scoping) and are DESCRIPTION.

### 0e — the within-cell mirror is NOT available from the jsons

The simulation's generative mirror parameter is a WITHIN-cell, per-seed
correlation; the stored jsons give only per-cell aggregates. Rather than
reach into the npz (the card restricts inputs to stored jsons), the
simulation reports, at every grid point, the INDUCED across-cell
`Spearman(rho_A, rho_M)` so the grid can be read in the one currency that
IS measurable from storage. The threshold is reported in that currency.

### 0f — observation status

Everything read while scoping is DESCRIPTION and carries no branch
(Kriegeskorte et al. 2009; the L214 rule): the 20 stored `rho_A` and
`rho_M` values, L214's `q3` block (`D = 0.04088235294117647`,
`p_D = 0.46245`, `mean_absrhoA`, `mean_absrhoM`, `sign_agree_floor = 17`,
`sign_agree_ceiling = 4`, branch `H_TIE`), the addendum's two mirror
coefficients and both binomial p-values, the `fhi` degeneracy and the
`lvl/margin` identity. Every branch and every prediction below rides on
SIMULATED power curves and on the duty/S-mean mirror, none of which has
been computed by anyone.

### 0g — every registered escape SHORT-CIRCUITS (L222)

If the beta calibration fails to reach its target band, or if a power
curve is non-monotone beyond the registered tolerance, the run reports
`M_DEGENERATE` and STOPS before any threshold is read. A flag that does not
change control flow is documentation, not a guard.

## Registered design

### The two instruments, head to head on identical simulated data

- **MAG** (the L214 instrument): `D = mean_over_cells(|rho_A| - |rho_M|)`,
  null = paired sign-flip of the per-cell difference vector, `N_PERM =
  2000`, two-tailed on `|D|`. Registered reduction from L214's 20,000 with
  its reason: the sign-flip null of a 20-vector has 2^20 distinct draws, and
  2000 random draws give p resolution 1/2001, which is adequate against
  alpha .05 — and the cost is `N_SIM x |grid| x N_PERM`.
  MAG counts as a SUCCESS only when `p_D <= .05 AND D > 0`, i.e. the test
  must prefer the right currency, not merely reject.
- **SGN** (the comparison L214 reported but did not branch on): each
  currency's sign agreement with its OWN registered predicted direction
  (`rho_A > 0`, `rho_M > 0`), two-tailed exact binomial against 10/20.
  SGN counts as a SUCCESS only when A's test is significant IN its
  predicted direction AND M's test is significant in the direction
  OPPOSITE its own prediction — the configuration that says "these two are
  mirrors of one quantity and the registered direction decides which is
  the currency".

### The generative model (fixed before running)

For each of `n_cells = 20` cells and `n_seeds = 16` seeds (L214's design):

    t ~ N(0,1)                                  # the dominance variable dS
    A = beta*t + sqrt(1-beta^2)*e,   e ~ N(0,1) # the floor currency
    M = -(lam*A) + sqrt(1-lam^2)*f,  f ~ N(0,1) # the mirror currency

`rho_A = Spearman(A, t)`, `rho_M = Spearman(M, t)` within each cell, with
AVERAGE (midrank) ranks (L221: argsort-of-argsort is input-order dependent
and is a bug class). `lam` is the within-cell mirror strength; `lam = 1`
makes `M = -A` exactly, the 0a degenerate case.

- Grid: `LAM = [0.0, 0.1, ..., 1.0]` (11 points), plus a registered
  refinement pass at 0.01 steps across the bracketing interval of the
  crossing if one exists.
- `N_SIM = 400` datasets per grid point.
- `beta` is calibrated ONCE by bisection on a held-apart calibration draw
  so that the simulated `mean|rho_A|` at `lam = 0` matches L214's measured
  `mean_absrhoA = 0.32926470588235296` to within 0.005 (declared: a
  nuisance calibration against an OBSERVED value, hence description; the
  branch rides on the SHAPE of the power curves, which is unknown). A
  secondary arm at a fixed `beta = 0.50` is run as a robustness read.
- Seeds, registered now: `CAL_SEED = 22702`, `SIM_SEED = 22701`,
  `PERM_SEED = 22703`.

### Branch table (four cells + catch-all, L205)

| branch | condition |
|---|---|
| **M_CROSSES** | a grid point exists where `power_MAG < power_SGN`, and the smallest such point has induced `r_rho` strictly inside (-1, 0) |
| **M_MAG_DOMINATES** | `power_MAG >= power_SGN` at every grid point (no threshold exists; the card's expectation is refuted) |
| **M_SGN_DOMINATES** | `power_SGN > power_MAG` at EVERY grid point including `lam = 0` (the rule is unconditional: always register the sign comparison) |
| **M_DEGENERATE** | catch-all: calibration misses its band, a power curve is non-monotone beyond tolerance, or `lam = 1` fails to give `D` identically zero |

### Registered predictions

- **P1**: branch is `M_CROSSES`.
- **P2**: `power_MAG` at `lam = 1.0` is EXACTLY `0.0` (the 0a proof says
  `D ≡ 0`, so the permutation p is 1 in every simulated dataset).
- **P3**: the threshold `X` (the `|r_rho|` at the crossing) is `<= 0.6767`,
  i.e. the measured A-vs-dM mirror already sits past it — which
  retro-flags L214's own Q3 as the wrong instrument. (The card's
  expectation, restated in the 0d currency.)
- **P4**: the duty/S-mean mirror coefficient is POSITIVE (the pair is
  co-current, not a mirror) — the not-a-mirror control.
- **P5**: at `lam = 0`, `power_MAG > power_SGN` (with no mirror, the
  magnitude instrument is the better one; if this fails the rule is
  unconditional rather than thresholded).

### Verify (the card's own line)

- Every empirical input value read from the stored jsons and reproduced at
  FLOAT EQUALITY: L214's `q3` block and the addendum's mirror block
  recomputed from the stored per-cell `rho` tables (CERT-214), and L208's
  identity plus `fhi` degeneracy (CERT-208, tolerance derived from the
  data).
- No artifact rewritten: `md5sum -c l227/prior.md5` GREEN before and after;
  the five input jsons fingerprinted by `(size, mtime_ns)` before and
  asserted unchanged after; exactly ONE write in the script, to
  `l227/static.json`.
- The simulation seeded and its grid registered before running (this file).

---

## AMENDMENT 1 — written after `l227_probe.py` (which WRITES NOTHING) and
## before the measurement script exists. Every item below is a PRE-
## MEASUREMENT correction; no registered branch is relaxed, two are sharpened.

### 0h — the stored mirror coefficient is TIE-MISHANDLED, and the repair is visible

`l214_addendum.py` line 37 computes Spearman as
`np.argsort(np.argsort(x))` — ORDINAL (argsort-of-argsort) ranks, the bug
class L221 named. The `rho_M` vector has **19 distinct values over 20
cells** (`0.1588235294117647` occurs twice), so the convention matters:
the stored `spearman_rhoA_rhoM = -0.6766917293233082` is the ordinal value,
and the AVERAGE-rank (midrank) value is **-0.682963568418539**. The
currency-level coefficient has no ties and reproduces at float equality
either way, which is exactly why only one of the two moved.
Registered as a GATE in both conventions: reproduce the stored value with
the stored convention (float equality) AND report the midrank repair, with
the tie group named. The lane's own rho-mirror number is corrected by
0.0063 — small, and the point is that it was corrected by reading the
source rather than the summary (L220's law).

### 0i — the two instruments consume DIFFERENT GRANULARITIES, so each has its own mirror coefficient

Read from source (`l214_tail.py` 207-211), L214's sign comparison is
`sign_agree_floor = #cells{ sign(mean_A) == sign(mean_dS) } = 17` and
`sign_agree_ceiling = #cells{ sign(mean_dM) == sign(mean_dS) } = 4`. It is
computed on the per-cell CURRENCY MEANS, **not** on the signs of the
correlations (`#(rho_A > 0)` is 15, not 17, and `#(rho_M > 0)` is 8, not
4). So SGN is not a sign version of MAG; it is a different statistic at a
different granularity.

This REFINES 0d rather than replacing it: **each instrument has its own
mirror coefficient.** MAG consumes the per-cell correlations, so its mirror
coefficient is `r_rho` (-0.6830 midrank / -0.6767 as stored); SGN consumes
the per-cell currency means, so its mirror coefficient is `r_cur`
(-0.8556). The card's quoted -0.856 is SGN's, used to justify a statement
about MAG. The threshold is therefore registered as a PAIR of thresholds,
one per currency, and the simulation reports BOTH induced coefficients at
every grid point.

Consequence for the design: the simulation's SGN instrument is implemented
as L214 implemented it (per-cell currency means vs the per-cell mean of the
dominance variable), not as a sign test on the correlations. The success
criterion is unchanged: A's binomial significant in its predicted
direction AND M's significant in the direction opposite its own.

### 0j — `D` reproduces only from the PAIRED difference vector (expression form)

Measured in the probe: `mean_absrhoA` and `mean_absrhoM` both reproduce at
FLOAT EQUALITY as `float(np.abs(arr).mean())`, but their DIFFERENCE misses
the stored `D` by +6.939e-17, while `mean(|rho_A| - |rho_M|)` computed on
the paired per-cell vector reproduces `D` EXACTLY. Two mathematically
identical expressions, one of which is the code that ran (L206: a
float-equality claim is a claim about the EXPRESSION). Registered: the
CERT-214 gate asserts the PAIRED form at float equality and REPORTS the
difference-of-means residual rather than asserting it.

### 0k — P4 is DOWNGRADED to description; the sharper question replaces it

During the probe I read `l200`/`l202` arm records and saw that `meanL`
appears to be the mean of the per-seed `dutyL` list (sc25: `meanL = 0.137`
against an eyeballed mean of ~0.1375). So "duty vs S-mean" is not a pair of
candidate currencies at all — it is **one quantity and its own
cell-level mean**, whose mirror coefficient is positive by aggregation.
Prediction P4 ("the mirror is positive") is therefore OBSERVED-derivable
and is withdrawn as a prediction and retained as description.

Replacing it, on a quantity nobody has computed: is the relation an exact
aggregation identity, or is `mean` STORED ROUNDED? Branch, registered now
over all 28 arms (12 in l200, 16 in l202, both sides):

| branch | condition |
|---|---|
| **A_IDENTITY** | `meanX == mean(dutyX)` at float equality on all 56 (arm, side) units |
| **A_ROUNDED** | every unit agrees to within 5e-4 but not at float equality (a 3-decimal rounded store) |
| **A_DIFFERENT** | any unit disagrees by more than 5e-4 (the two really are different statistics) |

**P4' (registered)**: branch is `A_ROUNDED`. The structural conclusion for
the threshold rule is unchanged and was already registered in 0c: the pair
scores `C_NOT_APPLICABLE` because no shared within-cell regression exists
for a magnitude head-to-head, and it serves as the not-a-mirror control
(its coefficient is positive, so the rule's threshold is not triggered
everywhere).

### Net count of the card's four "pairs"

Registered reading, with three of the four settled before any simulation
runs: `lvl/margin` is an exact sign-flip IDENTITY (0a), `flo/fhi` is
DEGENERATE BY DATA (0b), `duty/S-mean` is a quantity and its own MEAN
(0k) — so **the family contains exactly ONE genuine pair of distinct
candidate currencies, `A` vs `dM`**, and the measured table is three
structural degeneracies plus one measurement. That is itself the answer to
"how often does this pre-step bite": in this family, every time it was
askable.
