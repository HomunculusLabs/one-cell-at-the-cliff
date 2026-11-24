# L215 VERDICT — the dead-left-trochanter resurrection

Tick 245, 2026-11-23. PREREG `l215/PREREG.md` written first. ZERO rollouts,
zero settles, zero dynamics. Static edge arrays only; the one RNG is the
declared membership-permutation null (seed 21521, 2000 draws). Runtime 3 s.

## Registered branch: **D_DEGENERATE** — the escape I declared in advance

`S_sign` is a ratio of signed differences, and the PREREG declared that if
`|dNET_act|` falls below 1% of the pool's own gain-scaled mass scale the
ratio carries direction only. On the actor `Tr_L`, `|dNET_act| = 0.0946`
against a degeneracy bar of **0.50946** — a factor of 5.4 inside it. So the
registered primary statistic is denominator-unstable on the very cell the
card is about, and no BULK/SIGN claim is made from it. **Three of the four
pool-sides trip the same bar** (Ti_L, Tr_L, Tr_R; only Ti_R clears it), which
is the stronger statement: the ratio was the wrong instrument for the whole
table, not just for the actor.

## What the degeneracy-free legs say, and they are not quiet

### 1. The depth-1 account is not silent — it is ANTI-PREDICTIVE

The floor **lowers** the net depth-1 drive onto every pool-side, including
the one it is supposed to resurrect:

| pool | n | cutwA Mp / Mm / NET | f4wA Mp / Mm / NET | ret |
|------|---|---------------------|--------------------|-----|
| Ti_L | 56 | 8783.2 / 7348.1 / **1435.1** | 7743.2 / 6527.4 / **1215.8** | .88465 |
| Ti_R | 57 | 10789.8 / 8866.0 / **1923.8** | 9627.4 / 8011.1 / **1616.4** | .89737 |
| Tr_L | 55 | 9862.8 / 9642.0 / **220.8** | 8912.9 / 8736.7 / **176.2** | .90489 |
| Tr_R | 55 | 10130.4 / 9988.0 / **142.4** | 9083.7 / 8987.1 / **96.6** | .89822 |

`Tr_L`'s net depth-1 drive falls **20.2%** (220.8 → 176.2) across exactly the
substrate change that takes its dynamic level from **.0002 → .022** (L208's
stored cutwA/f4wA pool means). Gain-scaled the drop is smaller but still a
drop (`dNET_act = −0.0946`, and the 4.8% gain lift `g_f4wA/g_cutwA = 1.04773`
is already inside that number). A dead pool waking up on *less* direct drive
is not a depth-1 phenomenon; the arrow points the other way.

This **replicates L208's dissociation on a second joint and in a stronger
form**. There, static per-cell in-mass mispredicted which Ti side runs hotter
(a sign mismatch of a level). Here the *change* in static net drive
mispredicts the *change* in level. Depth-1 in-mass has now failed as a
predictor of this family's dynamics twice, on different quantities.

### 2. The card's registered mechanism is refuted by DIRECTION, not by power

The hypothesis was an inhibition-specific sub-floor asymmetry: the floor
strips disproportionately much **inhibition** from the left Tr. Measured, the
directional confirmation leg (`frac_of_inh > frac_of_exc`) is **FALSE on all
four pool-sides**:

- Tr_L: the floor removes 9.63% of the excitatory in-mass and **9.39%** of
  the inhibitory — relatively *less* inhibition, not more.
- Tr_R 10.33% / 10.02%; Ti_L 11.84% / 11.17%; Ti_R 10.79% / 9.66%.

Sub-floor (syn < 4) edges are slightly **excitation-enriched** everywhere.
That is internally consistent with `S_sign > 0` in all four cells (+.3494,
+.5005, +.6836, +.7961): stripping proportionally more excitation makes NET
fall *faster* than a sign-neutral rescaling predicts. The sign decomposition
carries real content — it simply points the opposite way to the card.

### 3. Q1 confirms the bulk is side-symmetric, exactly as registered

`ret(Tr_L)/ret(Tr_R) = 1.00742` (bar ≤ 1.05) → `BULK_SYMMETRIC TRUE`,
reproducing L205's C4 mass-retention ratio 1.0074 from this run's own arrays.
Ti's ratio is 0.98583. So the card's premise that the floor's bulk effect is
near-side-symmetric is correct — it just leaves nothing for the asymmetry to
be made of.

### 4. Q2b: no relu crossing, as predicted

`NET(cutwA, Tr_L) = +220.80`, `NET(f4wA, Tr_L) = +176.16`. Both positive;
`CROSSES FALSE`. The Tr pools are motor neurons sitting on a near-balanced
excitation/inhibition budget (inhibitory fraction **.4943 / .4965** on
cutwA L/R vs .4555 / .4511 on Ti) — which is itself the most suggestive
anatomical fact in the table: **Tr is the near-balanced joint and Ti is not**,
and near-balance is exactly the regime where a small network-level change can
flip a pool between dead and alive. That is a pointer, not a measurement.

### 5. Q4 inverts the expected specificity

The handedness null on the inhibitory-removal asymmetry
`A_inh = (rm_L − rm_R)/(rm_L + rm_R)`, 2000 membership permutations with
per-side counts held exact:

- **Ti: A_inh +0.07716, two-sided percentile .0350**, outside the null band
  [−.0607, +.0611] — a real left-biased inhibitory stripping.
- **Tr: A_inh −0.03472, two-sided percentile .2950**, inside the band.

So the joint where *neither* side is dead carries the handedness-asymmetric
inhibitory stripping, and the joint with the dead side does not. P5 was
registered the other way round and is scored FALSE.

`SILENT_ON_Ti` also reads FALSE (|S_sign| .349 / .501), but with the
disclosure that Ti_L is itself D_DEGENERATE, so only Ti_R's .5005 is a
magnitude at all.

## Predictions, scored as registered (never amended): 2/5

- **P1 TRUE** — BULK_SYMMETRIC.
- **P2 TRUE** — no relu crossing; I registered that I did not expect one.
- **P3 FALSE** — branch is D_DEGENERATE, not B_SIGN. The card's own
  expectation was wrong in direction, and my prediction inherited it.
- **P4 FALSE** — SILENT_ON_Ti false (partly an instrument artifact: Ti_L is
  degenerate; disclosed, not amended).
- **P5 FALSE** — and inverted: Tr .2950 vs Ti .0350.

## Method lesson (the transportable one)

**A degeneracy guard on a ratio-of-differences must be scaled by the POOL, not
by the difference, and when it trips on most cells of the table the statistic
is wrong for the table.** I registered `D_DEGENERATE` correctly (bar = 1% of
the gain-scaled pool mass) and it fired on 3 of 4 cells. The legs that stayed
readable are the ones that are **not** ratios of differences: the sign of
`dNET`, and the directional comparison `frac_of_inh` vs `frac_of_exc`. Those
two, not `S_sign`, carried the whole verdict. Next time, register the
degeneracy-free directional leg as PRIMARY and the ratio as the magnitude
refinement conditional on the bar clearing.

Second, smaller: **a premise-correction that names a no-op can still earn its
place by naming what is NOT a no-op.** The card asked for a `lam1^d`
normalisation; at d = 1 with ratio statistics it is provably inert (measured:
a global ×3.7 rescale moved every registered S_sign by ≤ 1.11e-16). The
normalisation that *does* bite across these two substrates is the bisected
gain, 1.04773 — and it is inside every number above.

## Limits

- Depth-1 in-mass under a uniform-X approximation. The honest next question is
  the depth-2 (network) account, seeded as L228.
- The `Tr_L` pools were **selected** for being dead (L208's post-hoc floor
  leg). Every number here describes a selected object; Q4 is a handedness
  null on a preselected pool, not a p-value for "a pool". The Ti leg is the
  out-of-selection comparator and is the only one not conditioned on the
  selection — which is also where the one significant null result landed.
- `ret()` mixes the floor with the small node-set change (cutwA drops
  `ng_desc[:24]`, f4wA drops `ng4[:20]`); the node-matched eligible leg is
  stored beside it in `l215/static.json` (`elig_nodematched`,
  `ret_nodematched`).
- `B_BOTH` is unreachable by construction; declared in the PREREG so the
  four-cell table is honest about its own geometry.

## Verify

CERT-205 = **36 float equalities** (every stored `c4_floor_retention` value
for Ti and Tr, both sides, plus both L/R ratios) + CERT-TBL = **28 float
equalities** (`table[J][cutwA|f4wA]` M_L/M_R/M_fL/M_fR/M_eL/M_eR/A_cell) +
CERT-G = **2** (`g_cutwA`, `g_f4wA` from `l169b2/raw_l169b2.npz`) = **66
float equalities, all halting, all before any L215 statistic was read**.
Two verbatim source slices with inherited sha pins asserted against the
values L205's banner recorded (`l151_static.py` 1-319 `e6245e8306dc8a0f`,
`l178_tail.py` 22-83 `66112b0c221d02d8`); generated sha
`dbc507e8f48530ae`; forbidden-token audit on both heads; no lab module
imported. Substrate pins cutwA 21785/644177, f4wA 21789/469618, eligible
469256, and the exact partition `469256 + 174921 == 644177`. Per-pool
sign-split partition asserted to 1e-9 on every row. Pool sizes invariant on
both substrates with zero L/R overlap. Permutation draw counts asserted exact
on all 4000 draws. `l205/static.json`, `l208/static.json` and
`l208/addendum_floor.json` opened read-only with (size, mtime_ns)
fingerprinted before and asserted unchanged after; md5sum -c green.
