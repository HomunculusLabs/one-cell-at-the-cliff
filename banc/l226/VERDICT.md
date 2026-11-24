# L226 VERDICT — the FLOOR currency OUT OF SAMPLE

**Branch: O_TRANSPORTS (registered). Predictions 6 of 6.**
Tick 258, 2026-11-23. PREREG `l226/PREREG.md` frozen before `l226_run.py`
existed. Zero amendments.

## Headline

The lane's **first genuinely out-of-sample test** in this family passed. On
a fresh 16-seed batch **B38 (3801-3816)** that did not exist when the
decision rule was frozen, the pre-named cell `Tr|f4ng` reads
**rho +0.8000, p_up .00460** — significant at the registered alpha .05,
**rank 1 of 10 by p_up for the third consecutive batch** — and the
population sign currency reads **8/10** against the card's registered bar
of 7. Both legs of the card's registered prediction held.

L214's `p_C = .0465` was a null-corrected DESCRIPTION of a pattern already
observed in the post-hoc leg (Kriegeskorte et al. 2009). It is now a
**prediction that held**. The three-batch joint replication adds its own
number: **C3 = 1 cell (`Tr|f4ng|up`), p_C3 = .00205** against the extended
L214 null — 22.7x smaller than the two-batch description, and earned rather
than described.

| | B36 (observed) | B37 (observed) | **B38 (out of sample)** |
|---|---|---|---|
| `Tr\|f4ng` rho | +0.7588 | +0.9118 | **+0.8000** |
| p_up | .00070 | .00075 | **.00460** |
| p_up rank of 10 | 1 | 1 | **1** |
| sign agreement | 8/10 | 9/10 | **8/10** |
| BH q=.10 survivors | 2 | 1 | **2** |

B38's own BH at q = .10 keeps `Tr|f4ng|up` (smallest p of 20) plus one
other, and the batch's gains landed on the stored values EXACTLY.

## What the cost slice bought, and the certification it needed

The card demanded a slice ("cost is the binding constraint"). Only the five
arms all three batches share were rolled out — 423 s against l175f's 793 s.
But dropping arms changes the **rollout** loop, and the only subset result
on record (l169b2 CERT-2 / C0-SUB) certified the **settle** subset.

**CERT-SUBSET, measured: 230 bit-identity checks (5 arms x 22 keys + af,
2 anchor seeds) at max abs diff exactly 0.0e+00.** The L139 spectator law
is now a rollout claim, not a settle-only one: the generator stream is
ARMS-independent (one `nz_o`/`nz_a` draw per step regardless), and the
measurement proves it rather than assuming it.

## The addendum: B38 refutes L214's Q4 "ACCOUNTED" leg

Declared POST-HOC, unregistered, no branch. `Ti|f4wA` was L214's
**registered exception** — the cell a pass had to account for — scored
ACCOUNTED because in both prior batches (a) `|mean_A|` ranked in the
bottom 3 of 10 **and** (b) neither tail cleared alpha .05, so "its currency
value is near zero and its sign is noise".

Out of sample, clause (a) holds (|mean_A| .02435, rank 2/10) and
**clause (b) fails: p_dn .00830**, and `Ti|f4wA|dn` survives B38's own BH.
L214's Q4 would score **UNACCOUNTED** on B38. The magnitude clause holds
3/3 batches; the no-significance clause 2/3.

**Why:** over all 30 cells (3 batches x 10, 30 distinct values — no tie
inflation), Spearman(`|mean_A|`, `|rho|`) = **+0.2979**. The 30%
smallest-`|mean_A|` cells still carry mean `|rho|` 0.2098 with a **max of
0.6029**. A near-zero currency MEAN does not bound the per-seed
CORRELATION — L214's Q4 used a MAGNITUDE screen to excuse a CORRELATION
result, and B38 is where that screen broke.

**What actually carries L214's reading:** `Ti|f4wA`'s rho across the three
batches is `[-0.2647, +0.0706, -0.6029]` — signs `[-1, +1, -1]`, UNSTABLE —
while `Tr|f4ng` is `[+0.7588, +0.9118, +0.8000]`, 3/3 positive. Per batch,
2-3 of 20 one-tailed hypotheses clear .05 against 1.0 expected by chance,
and the cross-batch consistency count is
`{Tr|f4ng|up: 3, Tr|f4tw|up: 2, Ti|f4wA|dn: 1, Ti|cutwA|up: 1,
Tr|cutwA|up: 1}`. L214's *conclusion* survives on the SIGN-INSTABILITY
clause; its *test* does not. **The cross-batch filter is the instrument
that separates signal from multiplicity here; a within-batch magnitude
screen is not.**

## Predictions

| | registered | measured | |
|---|---|---|---|
| P1 | Q1 = O_TRANSPORTS | O_TRANSPORTS | TRUE |
| P2 | actor p_up < .05 | .00460 | TRUE |
| P3 | SA38 >= 7 | 8 | TRUE |
| P4 | actor has smallest p_up of 10 | rank 1 | TRUE |
| P5 | actor survives B38's BH | survivor | TRUE |
| P6 | CERT-SUBSET max == 0.0 exactly | 0.0e+00 | TRUE |

## Gates

- **CERT-FLO (40)** + **CERT-RHO (100)** — L208's stored `flo` values and
  the post-hoc leg's 20 rho/p_up/p_dn/mean_A/mean_dS at FLOAT EQUALITY,
  re-run FREE because the frozen rule arrives as `l214_tail.py` lines 1-95
  VERBATIM (slice 3), cut exactly at L214's own gate exit.
- **PARENT PIN (halting)** — `l214_tail.py` asserted a literal SUFFIX of
  `l214_static.py` (sha b1b4cd430e4765a2), with slices 1/2 literal
  substrings in order: the frozen rule is provably the code that produced
  `l214/static.json`.
- **CERT-BH (8)** — the BH procedure re-implemented in the tail reproduces
  L214's stored per-batch survivor sets, counts, smallest p and its name
  EXACTLY, on both batches, before B38's BH is read.
- **CERT-SGN (3)** — per-batch sign agreement 8/10 + 9/10 == L214's stored
  17/20, in the PREREG-0d currency (per-cell MEANS, not rho signs).
- **CERT-Q1 (6)** — the self-ranked cross-batch null reproduces L214's
  stored `p_C` .0465 and all three `C_null` moments at FLOAT EQUALITY,
  which is what licenses extending it to a third batch.
- **CERT-SUBSET (230, halting)**, **CERT-GAIN (7 bisects EXACT, halting)**,
  **CERT-SEP (halting)** in the run script.
- **CERT-226 (64, halting)** in the addendum, before any addendum number.
- Builder audits: the run script's diff is STRUCTURAL for deletions (every
  removed line proven inside one of three declared excision slices) and
  regex-audited for additions — 131 deletions / 67 additions, 0
  unexplained. The addendum prefix is AST-verified to contain ZERO writes
  (every `open()` mode is "r"). No lab module imported (L175), checked by
  AST rather than substring.
- `md5sum -c l226/prior.md5` (9 files) GREEN before and after;
  `l226/parent.md5` GREEN after the addendum; all npz and prior-json
  (size, mtime_ns) fingerprints asserted unchanged, including
  `l226/raw_l226.npz` itself.

## Disclosures

- **The card's 7/10 sign bar is not an alpha-.05 test.** Exact one-sided
  binomial P(X >= 7 | n=10, p=.5) = **0.1719**, registered and reported
  beside the branch (PREREG 0e) so the bar cannot be read as a level.
- **A stale inherited log string.** The verbatim FC-169B2 block prints
  "12 arms x 22 keys" because that sentence came with the slice; `len(ARMS)`
  is 5 and the authoritative number is CERT-SUBSET's COUNTED 230 =
  2 x (22 + 1) x 5. Read the machinery, not the sentence describing it.
- **Scope.** B38 is a fresh SEED batch on the same substrate, drive, window
  and gains. It tests seed-level generalisation only — not a fresh
  specimen, not a fresh protocol.
- Q3's three-batch null is a declared EXTENSION of L214's machinery (a
  second permutation from the same `PAIR_SEED` stream), gated by CERT-Q1
  but not independently validated as an instrument.
- Two self-inflicted build halts, both caught by this card's own audits and
  both repaired to something strictly stronger: a bare-token negative audit
  on `"l175f/raw` fired on the B38 **absence-scan list** (which must name
  those files), repaired to a structural line-set assert; and a bare-token
  L175 import guard on `"from l2"` fired on the tail's own **prose**
  (a comment citing `l214_tail.py` line numbers), repaired to an AST import
  walk. That is the bare-token trap for the fifth and sixth time — it is
  now fixed at the root in both builders.
- Budget overrun disclosed: ~95 min against 35. The rollout batch alone was
  423 s; the two build halts, the verdict build and the addendum are the
  rest.

## Artifacts

`banc/l226/{PREREG.md, VERDICT.md, static.json, addendum.json,
anchors_run.json, raw_l226.npz, raw_partial.npz, run.{out,err},
verdict.{out,err}, addendum.{out,err}, prior.md5, parent.md5}`;
code `banc/l226_build.py -> l226_run.py`,
`banc/l226_build_verdict.py + l226_tail.py -> l226_static.py`,
`banc/l226b_build.py + l226b_tail.py -> l226b_static.py`.
