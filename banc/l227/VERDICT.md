# L227 VERDICT — the MIRROR COEFFICIENT as a required pre-step

Tick 257, 2026-11-23. Branch **M_CROSSES** (registered). Predictions
**4 of 5**; the one FALSE prediction is the card's own registered
expectation, and it is false for an instructive reason.

L226 (the first unchecked item) is the ROLLOUT card and `nvidia-smi` read
99% utilisation at wakeup, so the ground rule sent this tick to the next
static card. L226 stays unchecked.

## The card had four currency pairs. Three of them are not pairs.

| pair | class | mirror coefficient | why |
|---|---|---|---|
| `lvl` vs `margin` | **C_ANALYTIC_MIRROR** | **-1 by proof** | `margin = RMAX - lvl`, so `dM = -(lvlL - lvlR)` on all 20 cells (max residual 2.776e-17 against a data-derived tolerance of 1.798e-16; 3 of 20 at float equality). Spearman flips sign under a strictly decreasing map, so `rho_M == -rho_A` cellwise, `|rho_M| == |rho_A|` cellwise, and `D ≡ 0`: the magnitude head-to-head has **exactly zero power on this pair, by proof, before any measurement**. |
| `flo` vs `fhi` | **C_DEGENERATE** | undefined | `fhi95L/R` and `fhi90L/R` are identically 0.0 on all 20 cells (80 checks). A Spearman against a constant does not exist. At this sparse relu operating point the ceiling-side currency never fires. |
| `duty` vs `S-mean` | **C_NOT_APPLICABLE** | **+0.9999829** | `mean<side>` IS the mean of the per-seed `duty<side>` list (branch **A_ROUNDED**: 56 units, 4 at float equality, max residual 5.000e-04 = a 3-decimal store). One quantity at two granularities, and l200/l202 have no shared within-cell regression, so the magnitude instrument does not exist there. Kept as the **not-a-mirror positive control**. |
| `A` vs `dM` | **C_EMPIRICAL_NEAR_MIRROR** | `r_rho` **-0.6830**, `r_cur` **-0.8556** | the only genuine pair of distinct candidate currencies in the family. |

So the answer to "how often does this pre-step bite" is: in this family,
**every time it was askable**.

## Two corrections to the lane's own stored numbers

**The stored rho-level mirror coefficient is tie-mishandled.**
`l214_addendum.py` line 37 ranks by `np.argsort(np.argsort(x))` — ordinal
ranks, the bug class L221 named — and `rho_M` has 19 distinct values over
20 cells (`0.1588235294117647` twice). The stored
`spearman_rhoA_rhoM = -0.6766917293233082` is the ordinal value; the
AVERAGE-rank (midrank) value is **-0.682963568418539**, a move of 0.0063.
The currency-level coefficient has no ties and reproduces at float equality
either way — which is exactly why only one of the two moved. Found by
reading the source, not the summary.

**And rounding a stored value manufactures ties from the other direction.**
`duty` vs its own mean is a perfect monotone aggregation whose Spearman
should be exactly 1, and it reads **0.9999829**, because the 3-decimal
store collapses 56 distinct unrounded values to 55 distinct stored ones.
Same law, opposite cause: ties cap a rank correlation below its analytic
value whether they come from a tie-blind estimator or from a rounded file.

**Each instrument has its OWN mirror coefficient, and the card conflated
them.** Read from source (`l214_tail.py` 207-211), L214's sign comparison
is `#cells{ sign(mean_A) == sign(mean_dS) } = 17` vs
`#cells{ sign(mean_dM) == sign(mean_dS) } = 4` — computed on the per-cell
CURRENCY MEANS, not on the signs of the correlations (`#(rho_A > 0)` is 15,
not 17; `#(rho_M > 0)` is 8, not 4). So MAG consumes the correlations
(`r_rho`) and SGN consumes the currency means (`r_cur`): the card's quoted
-0.856 is **SGN's coefficient used to justify a statement about MAG**.

## The simulation, and why the card's expectation is false as stated

20 cells x 16 seeds (L214's design), 400 datasets per grid point, mirror
grid `lam = 0.0 … 1.0` plus a 0.01 refinement across the crossing interval,
`beta` calibrated to L214's measured `mean|rho_A| = 0.3293` (hit 0.3286).
MAG = L214's `mean(|rho_A| - |rho_M|)` with a 2000-draw paired sign-flip
null, scored a success only when `p_D <= .05 AND D > 0`. SGN = both
currencies' exact binomial sign tests significant in OPPOSITE directions.

- **P2 TRUE, exactly**: at `lam = 1` the per-cell difference vector is
  identically zero (`max|diff| == 0.0`), `p_D == 1.0` in every one of the
  400 datasets, and MAG power is **0.000**. The 0a proof, measured.
- MAG power falls monotonically: **0.575 → 0.228 → 0.000** across the grid.
- **P3 FALSE.** The crossing is at `lam 0.92`, `|r_rho| = 0.830`; the
  measured pair sits at 0.683, so it does **not** reach the crossing
  threshold, and `retro_flags_L214_Q3` is False.

## The addendum, and the finding the crossing was hiding

Declared post-hoc, unregistered, pure arithmetic on certified values
(`l227/addendum.json`), because **the parent's auto-generated
`rule.one_line` recommends the SIGN comparison at the crossing, where the
parent's own stored field says that comparison has power 0.075.** The
addendum asserts that contradiction against stored fields (L225's law: a
branch defined on one object cannot answer a question about another —
here a CROSSING cannot answer "at what mirror does MY instrument stop
working"). SGN's power tops out at **0.135** over the whole grid at n = 20.

**The threshold is not a number: it is a 2-D condition in (mirror, effect
size).** The `|mirror r|` at which MAG loses half its power is **0.2386**
at the lane's own measured effect size and **0.7941** at `beta = 0.50` — a
factor of 3.3. The card asked for a one-line rule of the form "if
|mirror r| > X"; **that rule does not exist as a single number**, and the
only unconditional mirror-only statement is the analytic one at |r| = 1.

**The card's expectation is false as stated and true in substance.** At the
measured mirror and the lane's own effect size, MAG was running at
**23.4% power**, so L214's Q3 read `H_TIE` at roughly one-quarter power:
"tie" was never distinguishable from "difference" on that data. That is
the retro-flag the card wanted — delivered by POWER AT THE MEASURED
MIRROR, not by a crossing criterion that depends on how bad the rival
instrument happens to be.

## The pre-step, as it should actually be written (rule_v2)

1. Name which currency each candidate instrument CONSUMES, and compute the
   mirror coefficient in THAT currency, with AVERAGE (midrank) ranks.
2. If the two currencies are related by a strictly monotone map — check the
   DEFINITIONS, not the data — the magnitude head-to-head has exactly zero
   power. Do not register it. This fires before any measurement.
3. Otherwise compute the ACHIEVED POWER of the magnitude test at the
   measured mirror AND the measured effect size (20 cells x 16 seeds costs
   seconds). Register the magnitude test only if that power clears a stated
   bar.
4. If it does not, the honest verdict on a null is "underpowered
   instrument", never "tie" — and the remedy is more cells or a different
   statistic, NOT automatically the sign comparison, whose own power at
   n = 20 topped out at 0.135 across the entire mirror grid.

## Gates

- **CERT-214 (halting, 31)** — L214's whole Q3 block reproduced from the
  stored jsons at FLOAT EQUALITY, including `p_D = 0.46245` re-derived by
  re-running its registered 20,000-draw `HH_SEED = 77041` sign-flip null,
  both `sign_agree` counts, the branch string, and the addendum's mirror
  block in the STORED (ordinal) convention; plus all 20 `mean_dS` values
  asserted identical between `l214` and `l208` (the dominance column must
  be the same object).
- **Expression form, reported not asserted** (L206): `mean_absrhoA` and
  `mean_absrhoM` each reproduce exactly, but their DIFFERENCE misses the
  stored `D` by **+6.939e-17** while the PAIRED per-cell difference mean
  reproduces it exactly — the paired form is the code that ran.
- **CERT-RANK (halting, 11)** — the fast midrank kernel is
  `np.array_equal` to a slow `np.unique`-style reference on five probes
  including all-tied and integer-valued vectors and on a 7x20x16 block, and
  every rank vector sums to `n(n+1)/2`.
- **CERT-SIM (halting, 4)** — the `lam = 1` degeneracy measured, not
  assumed.
- **CERT-AGG (56)**, **CERT-227 (19)** in the addendum, five input jsons
  `(size, mtime_ns)`-fingerprinted before and asserted unchanged after,
  `md5sum -c l227/prior.md5` and `l227/parent.md5` GREEN before and after,
  exactly one write per script.
- **One gate halt, disclosed**: the addendum's `mirror_r == 1.0` assert
  fired at 0.9999829. The repair is a BRACKET plus a counted mechanism
  (56 → 55 distinct values), strictly stronger than the equality it
  replaced — and it is how the rounding-tie finding was discovered at all.

## Limitations

Gaussian generative model with a linear mirror (the analytic arm is
untouched by this; intermediate `lam` is not). The real pair's WITHIN-cell
mirror is not recoverable from the stored jsons, so the measured pair is
placed on the grid through the induced across-cell coefficient.
`N_PERM_SIM = 2000` vs L214's 20,000 (registered in advance with its cost
reason). `beta` is calibrated against an OBSERVED value and is therefore a
nuisance parameter and description; the branch rides on curve shape.
SGN's success criterion requires both binomial tests significant in
opposite directions — a looser reading would move the crossing further
toward low `|r|`, i.e. it would strengthen the addendum's conclusion, not
weaken it.
