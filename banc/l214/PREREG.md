# L214 PREREG — the FLOOR currency, registered

Written BEFORE any new number is read. Tick 244 (2026-11-22), lane item
L214. ZERO new rollouts: every value comes from the already-stored
`l169b2/raw_l169b2.npz` (batch B36, seeds 3449-3464) and
`l175f/raw_l175f.npz` (batch B37, seeds 3701-3716), opened READ-ONLY and
never rewritten (L175: a lab run script is a SCRIPT, not a library — no lab
module is imported; helper code arrives as VERBATIM SOURCE SLICES).

## PREMISE CORRECTION, registered first (this is the load-bearing part)

The card says the floor leg "is UNREGISTERED — register it properly here."
It cannot be registered in the inferential sense, and pretending otherwise
would be the exact failure L213 taught and the tick-243 Kriegeskorte read
named. The facts:

- The 20 per-cell point estimates of the floor currency (rho, p_up, p_dn,
  mean_A, sign_agree for 2 batches x 2 pairs x 5 arms) were ALREADY
  COMPUTED in the post-hoc addendum `l208/addendum_floor.json` (tick 237),
  and were re-printed during this tick's scoping before this PREREG was
  written. They are OBSERVED.
- Registration AFTER observation does not restore independence between the
  selection of a statistic and its test (Kriegeskorte et al. 2009,
  LANE-RESEARCH.md tick 243). A p-value computed here on an already-seen
  point estimate is a DESCRIPTION of a selected statistic, not a test of a
  hypothesis.

Therefore this PREREG registers a **DECISION RULE**, not a fresh test, and
says so in the verdict. What it legitimately buys:

1. **Multiplicity discipline** committed before the corrections are
   computed: the card's own rule (20 hypotheses per batch at alpha .05
   expects ~1 hit per batch by chance, so only cross-batch replication
   counts) is converted into a numeric branch rather than left as prose.
2. **Null distributions that are genuinely unknown right now.** Every
   point estimate is observed; the NULLS are not. Nobody has computed what
   cross-batch replication count is expected by chance under the sign-flip
   ensemble, nor the BH-adjusted status, nor the paired null for the
   floor-vs-ceiling head-to-head. The branches below ride on those.

**Declared openly and not hidden in a footnote:** any quantity that is an
arithmetic function of the 20 observed point estimates (C_obs itself, the
BH survivor identities, the Q4 ranks) is OBSERVED-DERIVABLE and is reported
as description. The branch-deciding quantities are the null-corrected ones.

**The de-circularising instrument this card cannot have:** both batches
were inside the post-hoc leg, so neither is out-of-sample. A genuinely
out-of-sample test of the floor currency needs a THIRD seed batch, which
requires new rollouts and is excluded by this card's own constraint. That
is seeded as a follow-on item, not substituted for here.

## Registered substrate, window and currency

- Window `W`: the 0.7-Hz measurement segments, n_W = 3000 steps (asserted).
- Currency (PRIMARY, unchanged in form from the post-hoc leg, taken as a
  VERBATIM SOURCE SLICE so it is bit-identical):
  `A = floR - floL`, where `flo` = fraction of the window at or below
  BG = 0.02, pooled over the pair's two pools on that side.
  `dS = dutyL - dutyR`. Positive rho = the LESS floor-pinned side carries
  MORE antiphase duty.
- Pairs: **Ti** primary, **Tr** second. Arms: the five both batches share —
  `f4wA`, `f4ng`, `f4tw` (floored), `cutwA`, `cutng25` (base). Each arm x
  pair is a SEPARATE object (L109): 10 cells per batch, 20 total.
- Permutation machinery unchanged: exact-sign flips of `dS`, N_PERM =
  20,000, PERM_SEED = 20837 (the same draws as the post-hoc leg, so the
  reproduction gate is exact).

## Registered questions and branch tables

### Q1 (PRIMARY) — cross-batch joint replication, null-corrected

`C_obs` = number of the 10 arm x pair cells whose exact-sign-permutation
p < 0.05 on the SAME tail in BOTH batches.

Null: for each of the 20,000 draws, each cell's permuted rho is converted
to a self-ranked p against that cell's own null ensemble; B36 draw `j` is
paired with B37 draw `sigma(j)` under a registered index permutation
(PAIR_SEED = 51423) so the two batches are INDEPENDENT under the null.
`C_null[j]` = the same count on the permuted data. `p_C = mean(C_null >=
C_obs)`.

Branch table (four cells + catch-all, L205):

| branch | condition |
|---|---|
| **F_REPLICATES** | C_obs >= 1 and p_C <= 0.05 |
| **F_MARGINAL** | C_obs >= 1 and 0.05 < p_C <= 0.20 |
| **F_NULL** | C_obs >= 1 and p_C > 0.20 |
| **F_NONE** | C_obs == 0 (no cell replicates; the currency fails its own rule) |
| catch-all | anything else (e.g. a degenerate null with zero variance) is
  reported as **F_DEGENERATE** and carries no claim |

### Q2 — Benjamini-Hochberg, per batch, at q = 0.10

BH over the 20 hypotheses within each batch (10 cells x 2 tails),
registered q = 0.10. Reported: survivor count per batch, survivor
identities, and whether any cell survives in BOTH batches on the same
tail. Registered reading: a survivor set that is non-empty per batch but
shares no cell across batches is a FALSE-DISCOVERY-SHAPED result and is
reported as such; only a cross-batch survivor supports the currency.

### Q3 — head-to-head against the refuted ceiling currency

The ceiling currency `M` (`dM`, stored per cell in `l208/static.json`
`arms`) was refuted by sign in L208 (agreement 2/5 on Ti). Head-to-head on
the SAME 20 cells with the SAME dS:

- `D = mean_over_20_cells(|rho_A| - |rho_M|)`.
- Null: paired sign-flip of the per-cell difference vector, 20,000 draws,
  HH_SEED = 77041. `p_D` two-tailed on |D|.
- Also reported: sign agreement of each currency with dominance over all
  20 cells (floor vs ceiling), computed identically.

| branch | condition |
|---|---|
| **H_FLOOR_BETTER** | D > 0 and p_D <= 0.05 |
| **H_TIE** | p_D > 0.05 |
| **H_CEIL_BETTER** | D < 0 and p_D <= 0.05 |
| catch-all | **H_DEGENERATE** if the difference vector is identically zero |

### Q4 — the registered exception: `Ti|f4wA`

L208 already found that `Ti|f4wA` — the carrier-intact floored arm that is
the headline L175 phenotype — disagrees in sign in BOTH batches and is
explained by NEITHER currency. The card requires that a pass account for
it. This leg is OBSERVED-DERIVABLE and is registered as a DESCRIPTIVE
accounting, not a test:

- **ACCOUNTED** if, in BOTH batches, `|mean_A|` for `Ti|f4wA` ranks in the
  bottom 3 of the 10 cells AND neither tail's p clears 0.05 — i.e. its
  currency value is near zero and its sign is noise, so a sign
  disagreement there is uninformative rather than contradictory.
- **UNACCOUNTED** otherwise.

A Q1 pass with Q4 = UNACCOUNTED is reported as a **PARTIAL pass**, per the
card.

## Predictions (written before running; scored honestly, not amended)

1. **P1**: Q1 fires **F_REPLICATES** (p_C <= 0.05).
2. **P2**: Q3 gives D > 0 with p_D <= 0.05 (**H_FLOOR_BETTER**) — the floor
   currency tracks dominance better than the refuted ceiling currency.
3. **P3**: floor sign agreement over all 20 cells >= 17/20 while ceiling
   sign agreement over the same 20 cells <= 12/20.
4. **P4**: Q4 = **ACCOUNTED**.
5. **P5**: every BH survivor in Q2 is a **Tr** cell (the effect lives in
   the trochanter pair, not the tibia pair).

## Verify (the card's own line)

- PREREG written first (this file).
- The L208 stored `flo` values reproduced at FLOAT EQUALITY from the npz
  BEFORE any new number is read (40 equalities: floL/floR x 20 cells).
- The post-hoc addendum's 20 rho + p_up + p_dn reproduced at FLOAT
  EQUALITY from the same PERM_SEED machinery (60 equalities) — the
  currency is bit-identical, not re-implemented.
- Both batches reported.
- No npz rewritten: (size, mtime_ns) fingerprints asserted unchanged;
  `l208/static.json` and `l208/addendum_floor.json` likewise.
- Helper code arrives as VERBATIM SOURCE SLICES with sha256 asserted by the
  builder against the values earlier ticks recorded; no lab module imported.
