# L214 VERDICT — the FLOOR currency, registered

Tick 244, 2026-11-22. PREREG `l214/PREREG.md` written FIRST. Zero new
rollouts (runtime 182 s, CPU). Artifacts: `l214/static.json`,
`l214/addendum.json`, `l214/run.out`, `l214/addendum.out`.

## Branch: **PASS** — Q1 F_REPLICATES / Q3 H_TIE / Q4 ACCOUNTED

## What registration could and could not buy (the premise, registered first)

The card asked for the post-hoc floor leg to be "registered properly." It
cannot be registered in the inferential sense: the 20 per-cell point
estimates were already computed in `l208/addendum_floor.json` (tick 237)
and re-read during this tick's scoping. Registration after observation does
not restore independence between selection and test (Kriegeskorte et al.
2009, digested tick 243). The PREREG therefore registered a **DECISION
RULE**, declared every observed-derivable quantity as description, and put
the branches on the three quantities that were genuinely unknown when it
was written: the permutation NULL of the cross-batch count, the BH-adjusted
status, and the paired null of the head-to-head. The de-circularising
instrument this card could not have is a THIRD seed batch (both batches
were inside the post-hoc leg) — seeded as a follow-on, not substituted for.

## Q1 (PRIMARY) — cross-batch joint replication: **F_REPLICATES**

`C_obs = 1` of 10 arm x pair cells significant on the same tail in BOTH
batches: **`Tr|f4ng` up** (p_up .0007 B36 / .0008 B37). Under the sign-flip
ensemble with independently paired batch draws (PAIR_SEED 51423, 20,000
draws), the expected count is **0.0474** (max 2), giving **p_C = 0.0465** —
inside the registered <= 0.05 band, but only just. Reported as such: a
single replicating cell at p_C .0465 is a pass, not a strong one, and the
card's own multiplicity rule is what makes it a pass at all (within either
batch alone, 20 hypotheses at alpha .05 expect ~1 hit, and both batches
indeed produced hits that do NOT replicate).

## Q2 — Benjamini-Hochberg at q = 0.10: survivors, one shared

B36: 2/20 survive (`Tr|f4ng|up`, `Tr|cutwA|up`). B37: 1/20 (`Tr|f4ng|up`).
Shared across batches: **`Tr|f4ng|up`** — the Q1 cell, and the only one.
`Tr|cutwA` survives BH in B36 (p_up .0084) and dies in B37 (p_up .2640):
exactly the false-discovery-shaped pattern the PREREG said to expect from
within-batch multiplicity.

## Q3 — head-to-head vs the refuted ceiling currency: **H_TIE**, and the
## registered statistic was the wrong currency for the question

mean|rho_A| 0.3293 vs mean|rho_M| 0.2884, D = **+0.0409**, p_D **.4625** —
a tie. But the directional content is not close: sign agreement with
dominance over the same 20 cells is **floor 17/20** (binomial two-tailed
p .00258) vs **ceiling 4/20** (p .01182). The ceiling currency is not
noisy, it is **INVERTED** — significantly below the 10/20 chance line.

The POST-HOC addendum (`l214/addendum.json`, arithmetic only on already
certified values, parent md5-verified unchanged afterwards) says why the
magnitude test could not see this: the two currencies are near-mirrors.
Spearman(mean_A, mean_dM) = **-0.8556** (opposite sign in 13/20 cells) and
Spearman(rho_A, rho_M) = **-0.6767** (opposite sign in 15/20). Since
`dM = lvlR - lvlL` and `A = floR - floL`, both are "which side is more
active" read through different nonlinearities — so |rho| is nearly
invariant between them BY CONSTRUCTION, while the sign is the entire
difference. They are not EXACT mirrors (|r| .68-.86, not 1.0), so the
magnitude leg was a real if underpowered comparison; it simply tested the
one feature the two currencies share.

**The transportable lesson**: when two candidate currencies are mirrors of
one underlying quantity, a MAGNITUDE head-to-head is structurally unable to
separate them and will return a tie however different their directional
content is. Register the comparison in the currency where they can differ —
here SIGN — and measure the mirror coefficient BEFORE choosing the
statistic. The PREREG's catch-all (`H_DEGENERATE` if the difference vector
is identically zero) was too narrow: near-degeneracy, not exact
degeneracy, is the case that actually occurs.

## Q4 — the registered exception `Ti|f4wA`: **ACCOUNTED**

In BOTH batches the headline L175 arm's currency value is essentially zero
and its sign is noise: |mean_A| .0351 (rank 2/10) B36, .0346 (rank 2/10)
B37, both in the registered bottom-3, and neither tail clears alpha
(.8441/.1588 and .3800/.6242). Its sign disagreement with dominance is
therefore uninformative rather than contradictory — which is an accounting,
not an explanation: the floor currency still has nothing positive to say
about the arm that carries the phenotype.

## Predictions: 4/5 (registration NOT amended)

| # | prediction | result |
|---|---|---|
| P1 | Q1 = F_REPLICATES | **TRUE** (p_C .0465) |
| P2 | Q3 = H_FLOOR_BETTER | **FALSE** (H_TIE, D +.041, p_D .462) |
| P3 | floor sign >= 17/20 and ceiling <= 12/20 | **TRUE** (17 vs 4) |
| P4 | Q4 = ACCOUNTED | **TRUE** |
| P5 | every BH survivor is a Tr cell | **TRUE** (3/3) |

P2 failed for an instrument reason, and that failure is the tick's most
useful output: I registered the magnitude currency for a question whose
answer lives in the sign. Scored FALSE as registered.

## Verification

- PREREG written before any new number (file timestamps; the scoping read
  of the already-observed addendum table is declared in the PREREG itself).
- Helper code as VERBATIM SOURCE SLICES, sha asserted by the builder:
  slice 1 = `l169b2_verdict.py` 13-63 `de636f4a18ee789b` (asserted EQUAL to
  the value `l208_build_add.py` recorded and `l208/static.json` stores — a
  moved source HALTS the build); slice 2 = `l208_add_tail.py` 55-72
  `595f869b450e2d25` (`flo_side` + `spearman`, so the currency is
  bit-identical to the post-hoc leg). Forbidden-token audit on both; no lab
  module imported (L175); generated sha `b1b4cd430e4765a2`.
- **CERT-FLO (halting, 40 FLOAT EQUALITIES)**: every stored `floL`/`floR`
  in `l208/static.json` reproduced from the npz BEFORE any new number was
  read, as the card's Verify line requires.
- **CERT-RHO (halting, 100 FLOAT EQUALITIES)**: all 20 cells' `rho`,
  `p_up`, `p_dn`, `mean_A`, `mean_dS` reproduced from the same PERM_SEED
  20837 / 20,000-draw machinery.
- Premise asserts: head sha matches, `l208` branch is still
  `H_UNREGISTERED_SHAPE`, the addendum is still labelled POST-HOC.
- No artifact rewritten: `(size, mtime_ns)` fingerprints asserted unchanged
  for both npz and both prior jsons, and `md5sum -c` on
  `l208/static.json`, `l208/addendum_floor.json` and (after the addendum
  ran) `l214/static.json` all read OK.
