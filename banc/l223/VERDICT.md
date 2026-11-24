# L223 VERDICT — the READOUT-SPECIFICITY claim, nulled properly

**Branch: S_SPECIFIC** (registered). **Predictions 5 of 6.**
Static, zero rollouts. `l223_static.py` 233.0 s, `l223b_static.py` 237.2 s,
both `nice -n 15 timeout 1700` on om.

## The question

L212 published 12.86x into motor and 1.44x into descending as the carrier's
"readout specificity". Those are two percentiles against the same cohort, which
does not establish that the carrier is unusual in its motor-vs-descending
CONTRAST. The card's fix: make the cohort its own control.

## Q223-0 (read FIRST, as the card demanded): the question IS answerable

`rho_spearman(R_motor, R_desc)` across the cohort = **0.4776** (COH_C), 0.4343
(COH_M), 0.4238 (COH_U), against a 0.95 degeneracy bar. The two legs share
about 23% of rank variance — they are correlated (same cell, same m_out
denominator, overlapping depth-2 walks) but they are not the same measurement.
**S_DEGENERATE does not fire**, so the contrast carries information, and this
number had to be read before the carrier's was looked at.

## Q223-1 PRIMARY: S_SPECIFIC

C_log(g) = log R_motor(g) − log R_desc(g), cohort-free per cell (PREREG 0c).

| | C_log | ratio motor/desc | pct in own cohort | rank |
|---|---|---|---|---|
| carrier (DNp33 left) | **−4.5867** | 0.01021 | **0.0404** | 5 / 99 |
| mirror (DNp33 right) | −2.7915 | 0.0613 | 0.3434 | 35 / 99 |
| cohort median | −2.2283 | 0.1077 | — | — |

Carrier z in cohort **−2.054**; mirror z −0.382. Cohort C_log spread
min −5.136 / p05 −4.371 / median −2.228 / p95 −0.957 / max −0.177, sd 1.055.
One cohort cell excluded for a zero motor leg (zero fraction 0.01, far under
the registered 0.10 escape, so the escape did not fire and C_log stayed
primary).

**The carrier's deficit really is motor-SPECIFIC, not a restatement of readout
size.** Size cancels in C because it enters every cell's two legs the same way,
and the carrier still sits at the 4th percentile of the contrast.

## Q223-2 HOMOLOG + the L222 companion set

- own cohorts: carrier .0404 vs mirror .3434, gap **.3030**
- common (union) cohort: carrier .0331 vs mirror .3388, gap **.3058**
- cohort-FREE: C_mirror − C_carrier = **+1.7952**, i.e. the carrier is
  **6.02x** more motor-specific in its deficit than its own contralateral twin.

All three currencies agree in sign and in magnitude to .003 of a percentile
gap — L222's cohort-relocation failure mode is checked and absent here, which
is what makes the bilateral break safe to call directional.

## Q223-3 / the l223b ADDENDUM: the one prediction that failed, and why

**P5 FAILED**: |pct_log − pct_rank| = **0.1496** for the carrier (.0404 vs
.1900) against a registered 0.10 bar, while the mirror's two currencies agree
to 0.0134. Under the companion currency the carrier reads **S_GENERIC**: the
registered primary clears the 0.10 bar and the companion does not. **Disclosed
plainly — the binary call is currency-dependent; the DIRECTION is not** (both
currencies put carrier below mirror).

The POST-HOC addendum (`l223b`, declared post-hoc, no branch, no bar) asks the
only question that decides what that means, nonselectively: score EVERY cohort
cell exactly the way the carrier was scored (leave-one-out against the other
98) and place the carrier's disagreement in the cohort's own distribution.

- carrier disagreement 0.1496 sits at percentile **0.586** of the cohort's own
  (median 0.1224, mean 0.1367, p90 0.2776, max 0.4082).
  **The disagreement is dead typical. It is a statement about the two
  currencies, not about this cell.**
- rho(C_log, C_rank) across the cohort = **0.8339** — strongly but not
  perfectly concordant.
- the compression is measured and directional: the 20 most motor-specific
  cells by C_log sit at mean pct_log .0969 but mean pct_rank .1592, a
  **+0.0622** shift, while the cohort-wide mean shift is **−0.0043**.

**METHOD LAW (the transportable thing here): a RANK-DIFFERENCE contrast
systematically COMPRESSES the tail a specificity question lives in, so it can
fail to clear a bar that the magnitude currency clears on the same data — and
the way to tell "this cell is special" from "these currencies differ" is to
score every cohort member the same way and percentile the DISAGREEMENT itself.**
Here that reads .586 = generic. This is L218's currency law one step further:
L218 showed two currencies of one quantity can land a cell on opposite sides of
a null; L223 shows the disagreement can be a property of the cohort, measurable,
and therefore not a reason to doubt the primary that was registered in advance.

## Predictions

| | registered | measured | |
|---|---|---|---|
| P1 | branch S_SPECIFIC | S_SPECIFIC | **TRUE** |
| P2 | rho(COH_C) in [0.40, 0.95) | 0.4776 | **TRUE** |
| P3 | carrier pct < mirror pct | .0404 < .3434 | **TRUE** |
| P4 | excluded zeros <= 2 | 1 | **TRUE** |
| P5 | \|pct_log − pct_rank\| <= 0.10 | 0.1496 | **FALSE** |
| P6 | mirror pct > 0.10 | 0.3434 | **TRUE** |

Registration NOT amended. All premise corrections (0a–0e) were pre-measurement.

## Disclosed: a PREREG arithmetic slip, caught by the run

PREREG 0e stated the observed-derivable carrier C_log as −4.5884 and the mirror
as −2.7914. The exact values are **−4.58674** and **−2.791512**; the mirror was
right to 5 figures, the carrier's was my own hand arithmetic, off by 0.0017.
The script's own exact recomputation from the two published R values matches the
measured C_log to the last bit, which CONFIRMS 0e's claim that these quantities
were observation-derivable (and therefore DESCRIPTION, carrying no branch) —
only my transcription of one of them was imprecise. No registered quantity and
no branch depended on it.

## Gates (all HALTING)

- **CERT-212 — 139** stored l212/static.json values (Q1/Q2/Q3, lam1, the
  rescale no-op, both readouts, nt_mix and all five inherited cert blocks)
  reproduced at float/int equality by a recursive leaf compare, by RE-RUNNING
  L212's pipeline as a verbatim source slice, never re-implementing it (L211).
  Inherited as a verbatim slice of `l222_tail.py` lines 26-88, cut BEFORE its
  `del SUB2, SUB3, CV2, CV3` so this card keeps the descending leg it needs.
- **CERT-PAIR — 11** (new): CV (motor) and CV2 (descending) cover the IDENTICAL
  cohort key set COH_U on operators asserted `array_equal` in jv, rows and
  cols; both actors' entries equal L212's published R values at float equality;
  m_out is identical across legs. This is what makes "both legs in one run so
  the cohort is identical" a STRUCTURAL fact rather than a promise — the card's
  own Verify line.
- **CERT-RANK — 252** (new): the inherited `rankvec` is verified to be an
  AVERAGE-rank (midrank) estimator ON THIS DATA before any C_rank is read —
  every tie group's members receive one identical rank, the rank sum equals
  n(n+1)/2, and distinct-value count equals distinct-rank count. The tick-252
  midrank law converted from a memory into a gate; argsort-of-argsort would
  fail the tie-group check.
- **CERT-223 — 16** (addendum): the parent's own branch-bearing values
  reproduced at float equality before any addendum number was read.
- CERT-783 (6), CERT-L207 (8), CERT-MV (4), CERT-GATE (22+10) and the rescale
  NO-OP all arrive as inherited verbatim SOURCE and re-ran for free.
- **PARENT PIN 1**: the builder reconstructs `l212_static.py` byte-for-byte
  (sha b32c576b5145487e) from the three pinned sources.
  **PARENT PIN 2**: `l222_tail.py` is asserted to be a literal SUFFIX of
  `l222_static.py` (sha 730ac82cb12f4740), which is what proves CERT-212
  arrives as the code that actually ran rather than a file with the right name.
- Negative audit: the generated script contains exactly TWO writes, both
  pointing at l223 (OUT re-pointed); the tail re-transcribes none of the
  sixteen inherited function bodies; forbidden-token audit green. The addendum
  is a literal PREFIX of `l223_static.py` lines 1-818 with ONE declared
  modification (the inherited V_DEGENERATE escape, whose write targets the
  parent artifact, replaced by `assert SPR < 1e-6`; SPR measured 4.11e-16), so
  the prefix contains ZERO writes — asserted.
- `md5sum -c l223/prior.md5` GREEN (8 files) before the run and after;
  `l223/parent.md5` GREEN after the addendum; l212/static.json and
  l223/static.json opened READ-ONLY with (size, mtime_ns) fingerprinted before
  and asserted unchanged after. No lab module imported (L175).
- Generated shas: parent **d1b06d9df0df2582** (911 lines), addendum
  **3b2863da71aac9f7** (959 lines).

## Limitations (stated, not repaired)

- v783's cohort mass match is LOOSE: log-spread 0.3163 / 0.3486 against the
  <=0.15 bar L212 registered and FAILED (Q212-5). Every percentile inherits it.
- v783 is BRAIN-ONLY, and L222 measured that ALL in-brain out-edges of BOTH
  actors sit below synapse 4, so the descending readout is a within-volume
  stand-in for "everything else this cell talks to", not its real targets.
- COH_C is 100 cells: one cell is one percentile point (L207), and a 0.10 bar
  cannot separate 0.10 from 0.11.
- ANATOMICAL leg only — no mask, no settle, no seed, no rollouts. Operator
  powers are walks WITH revisits, not paths (L164).
- The contrast cancels readout SIZE only to the extent size enters both legs
  the same way; it does not cancel readout-specific DEGREE structure (L233).
- The addendum is POST-HOC and descriptive: no registered bar, no prediction.

## Artifacts

`banc/l223/{PREREG.md, VERDICT.md, static.json, addendum.json, run.{out,err},
addendum.{out,err}, prior.md5, parent.md5}`;
code `banc/l223_{build,tail}.py -> l223_static.py`,
`banc/l223b_{build,tail}.py -> l223b_static.py`.
