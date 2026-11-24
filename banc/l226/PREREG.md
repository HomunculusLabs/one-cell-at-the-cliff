# L226 PREREG — the FLOOR currency OUT OF SAMPLE (third seed batch B38)

Written BEFORE l226_run.py existed and BEFORE any B38 number exists.
Tick 258 (2026-11-23), lane item L226. This is the lane's FIRST genuinely
out-of-sample test in this family: B36 (l169b2, seeds 3449-3464) and B37
(l175f, seeds 3701-3716) were BOTH inside the post-hoc leg that discovered
the floor currency (l208/addendum_floor.json, tick 237), so L214's
p_C = .0465 is a null-corrected DESCRIPTION of an already-observed pattern
and not a test (Kriegeskorte, Simmons, Bellgowan & Baker 2009).

## Premise corrections, registered first (all pre-measurement)

### 0a — THE SLICE ITSELF NEEDS A CERTIFICATION NOBODY HAS RUN YET

The card says "slice to the two pairs and five arms, nothing else" because
cost is the binding constraint (the full 12-arm l175f pipeline cost 793 s).
But dropping arms changes the ROLLOUT loop, and the only subset result on
record is l169b2's CERT-2 / C0-SUB, which certified the SETTLE subset
(arms=[arm] inside `settle_states`, proven by four stored-form bisects
landing EXACT). Nobody has certified that dropping arms from the 6000-step
ROLLOUT loop is a numerical no-op.

It should be, by the L139 spectator law: `gen` draws `nz_o` (n_old) and
`gen2` draws `nz_a` (n_add) ONCE PER STEP regardless of `ARMS`, the per-arm
noise is a slice of the same `nzn`, and the arms never touch each other's
state. Registered as a GATE rather than assumed:

- **CERT-SUBSET (halting)**: the inherited FC-169B2 block, whose loops run
  over `ARMS`, is restricted to the five registered arms by construction.
  All five arms x 22 keys (mm, xm, and all 20 pool-mean traces) x 2 anchor
  seeds (801, 901) + the 5 settled `af` values must be BIT-IDENTICAL
  (max abs diff == 0.0) to `l169b2/raw_l169b2.npz`. Any non-zero means a
  stream or substrate break: the run is **VOID** and no B38 value may be
  read. This converts the L139 spectator law from a settle-only claim into
  a rollout claim, measured.
- **CERT-GAIN (halting)**: the five gains are re-bisected FRESH, never
  ported, and must land EXACTLY on the stored values —
  `cutwA` 0.14365819573402408 (l123), `cutng25` 0.1454454553127289 (l131),
  `f4wA` 0.15051452517509462, `f4ng` 0.16230986118316648,
  `f4tw` 0.15261898636817928 (l169b2). The two eMot bisects are retained
  (they cost ~50 s and buy two more stored-gain pins for free).
- **CERT-SEP (halting)**: the inherited C0-NT(b2) separation — each f4 arm
  distinguishable from its base counterpart and from the other two f4 arms
  — must stay PASS, else the floor never entered the step loop.
- **B38 absence (L157)**: `B38 = range(3801, 3817)` key-scanned absent from
  every stored raw npz, with `l175f/raw_l175f.npz` and
  `l175f/raw_partial.npz` ADDED to the scan list (l175f_run.py's own list
  stops at l169b2).

The five arms are the ones all three batches share: `f4wA`, `f4ng`,
`f4tw` (floored) and `cutwA`, `cutng25` (base). The two pairs are **Ti**
and **Tr**. 10 cells.

### 0b — THE FROZEN RULE IS A SOURCE SLICE, NOT A RE-IMPLEMENTATION

The card's Verify line requires "the L214 rule re-executed as a verbatim
source slice, not re-implemented". Registered construction:

- `l214_tail.py` **lines 1-95 VERBATIM** (constants, window, the two
  reproduction gates) is the head of the verdict script. Because its
  `PATHS` names only B36/B37, running it re-executes **CERT-FLO (40
  stored `flo` values at FLOAT EQUALITY)** and **CERT-RHO (100 post-hoc
  rho/p_up/p_dn/mean_A/mean_dS at FLOAT EQUALITY)** for free, BEFORE any
  B38 number is read — so the currency is bit-identical by construction.
- The currency atoms arrive the same way L214 got them: slice 1 =
  `l169b2_verdict.py` 13-63 (sha de636f4a18ee789b), slice 2 =
  `l208_add_tail.py` 55-72 (sha 595f869b450e2d25). No lab module is
  imported (L175).
- **PARENT PIN (halting)**: `l214_tail.py` is asserted to be a literal
  SUFFIX of `l214_static.py` (sha to be pinned by the builder), which is
  what proves the frozen rule arrives as the code that ACTUALLY RAN.

The per-cell estimator is therefore frozen bit-for-bit: `A = floR - floL`
pooled over the pair's two pools, `dS = dutyL - dutyR`, Spearman over the
16 seeds, exact-sign-flip null with **N_PERM = 20000, PERM_SEED = 20837**.
The `SIGNS` matrix is (20000, 16) and B38 has 16 seeds, so the SAME sign
draws apply — the rule is frozen, not re-derived. `p_up` = mean(null >= rho),
`ALPHA` = 0.05.

### 0c — OBSERVATION STATUS

`l214/static.json` was read in full during this tick's scoping, so every
B36/B37 number is OBSERVED and is reported as DESCRIPTION, including: the
single replicating cell `Tr|f4ng|up`, its p_up (.0007 / .00075, the
smallest of 20 in both batches), the BH survivor sets, and the sign
agreements 8/10 (B36) and 9/10 (B37) which sum to L214's published 17/20.
**Nothing about B38 is observation-derivable** — the batch does not exist
as this file is written. That is the whole point of the card.

### 0d — WHICH CURRENCY THE SIGN BAR CONSUMES (the L227 law)

The card's ">= 7/10 sign agreement" is ambiguous until the currency is
named. Frozen from `l214_tail.py` lines 208-211: agreement is
`sign(mean_A) == sign(mean_dS)` over the per-cell CURRENCY MEANS, NOT over
the signs of the per-cell correlations. (L227 measured those as different
objects: mirror coefficient -.8556 on means vs -.6830 on rhos.)

### 0e — THE CARD'S 7/10 BAR IS NOT A SIGNIFICANCE LEVEL (disclosed)

Under a fair-coin null, P(X >= 7 | n=10, p=.5) = 176/1024 = **0.1719**. The
7/10 bar is a REPLICATION threshold the card chose, not an alpha-.05 test.
Registered: the bar carries the branch exactly as the card wrote it, and
the exact one-sided binomial p is reported BESIDE it so the branch cannot
be mistaken for a test. (L227: name the achieved power / the real level
instead of letting a convenient bar masquerade as one.)

### 0f — ONE-TAILED BY REGISTRATION

The card names the `up` tail for `Tr|f4ng` (B36/B37 both had p_up tiny and
p_dn ~.999). Registered: the PRIMARY is `p_up`, one-tailed, as the card
froze it. `p_dn` is reported for completeness and carries no branch.

## Registered questions and branch table

### Q1 (PRIMARY) — the frozen L214 rule, out of sample

- `p_up(B38 | Tr, f4ng)` against ALPHA = 0.05.
- `SA38` = sign agreement over the 10 B38 cells, against the card's bar 7.

| branch | condition |
|---|---|
| **O_TRANSPORTS** | p_up < .05 AND SA38 >= 7 — the currency and the cell both replicate out of sample |
| **O_CELL_FAILS** | p_up >= .05 AND SA38 >= 7 — the CURRENCY transports but the single cell was a within-batch hit (the card's own first failure reading) |
| **O_CURRENCY_FAILS** | p_up >= .05 AND SA38 < 7 — the floor leg was a two-batch coincidence and L208's descriptive mechanism loses its only quantitative support (the card's own second failure reading) |
| **O_CELL_ONLY** | p_up < .05 AND SA38 < 7 — the cell replicates while the population currency does not |
| catch-all | **O_VOID** if CERT-SUBSET, CERT-GAIN or CERT-SEP fails; the script HALTS and no B38 value is read |

### Q2 (companion, registered) — BH within B38

Benjamini-Hochberg over B38's own 20 hypotheses (10 cells x 2 tails) at
q = 0.10, the same procedure and level as L214's Q2. Reported: survivor
count, identities, smallest p.

### Q3 (companion, registered) — three-batch joint replication

`C3` = number of the 10 cells whose p < ALPHA on the SAME tail in ALL
THREE batches. Reported with its own permutation null built the same way
L214's Q1 null was (self-ranked per-cell p's, independent per-batch index
permutations from PAIR_SEED = 51423, extended to a third batch by taking
a second permutation from the same stream — DECLARED as an extension of
L214's machinery, not a new instrument).

### Q4 (descriptive) — per-cell table

All 10 B38 cells: rho, p_up, p_dn, mean_A, mean_dS, sign agreement, and the
rank of |mean_A|. Reported beside B36/B37 for reading, never for a branch.

## Predictions (written before the batch exists; scored honestly)

1. **P1**: Q1 fires **O_TRANSPORTS** (the card's own registered prediction).
2. **P2**: `p_up(Tr|f4ng)` < 0.05 in B38.
3. **P3**: `SA38` >= 7.
4. **P4**: `Tr|f4ng|up` has the SMALLEST p_up of the 10 B38 cells (it did in
   both prior batches).
5. **P5**: `Tr|f4ng|up` survives B38's own BH at q = 0.10.
6. **P6**: CERT-SUBSET max abs diff == 0.0 EXACTLY — the arm subset is a
   bit-exact no-op in the rollout loop, not merely a close one.

## Verify (the card's own line, made concrete)

- This PREREG written and frozen BEFORE `l226_run.py` existed.
- `l226_run.py` MECHANICALLY DERIVED from `l175f_run.py` by `l226_build.py`
  with a declared edit set (arms, batch, paths, three excisions whose
  only reason is that they read arms this card does not roll out, one
  rewritten output block) and a difflib audit that every changed line is
  explained.
- The L214 rule re-executed as a VERBATIM SOURCE SLICE (0b), with its two
  reproduction gates re-run free before any B38 value is read.
- `l226/raw_l226.npz` checkpointed BEFORE analysis and never rewritten;
  (size, mtime_ns) fingerprinted around the verdict.
- `l169b2/raw_l169b2.npz`, `l175f/raw_l175f.npz`, `l208/static.json`,
  `l208/addendum_floor.json` and `l214/static.json` opened READ-ONLY with
  fingerprints asserted unchanged after.
