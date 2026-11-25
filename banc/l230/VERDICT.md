# L230 VERDICT — the CROSSING-PHASE law

Run 2026-11-24 ~00:2x EST (tick 262), `l230_static.py` (1,926 lines, sha256
a02e27563a8892ce), 33 s on om, `nice -n 15 timeout 1700`, peabrain venv.
PREREG `l230/PREREG.md` written first, nine premise corrections, **one
disclosed amendment (0h-i, a notation slip in a stated identity, caught by
that identity's own assert before any outcome existed).**

**Q1 branch: `PHASE_MODEL_INSUFFICIENT`** (registered FIRST in the branch
order, and it fired). **Q3 branch: `CF_NOT_SEPARATED`.** Predictions **3 of 6**,
with all three failures load-bearing.

---

## 1. The headline: the closed form's two currencies straddle the bar in
## OPPOSITE directions, and the one that makes the attribution EXACT is the
## one that cannot predict the crossing

L216's two-term model `A_cell(d) = A_inf + K rho^d` gives
`d_cross = log(-A_inf/K)/log(rho)`. The card's own wording fixes `K` as the
depth-1 overlap and `rho` as the spectral gap **shared by both joints** — and
that sharing is exactly what makes the Ti-minus-Tr difference decompose into
an exact additive pair of log terms. Measured against L217's certified
crossing depths:

| cell | d_meas | d_cf (shared gap) | resid | d_cf (own r_deep) | resid |
|---|---|---|---|---|---|
| cutwA beta Ti | 4.1158 | 3.7475 | **0.3684** | 4.1357 | **0.0199** |
| cutwA beta Tr | 1.3401 | 1.3638 | 0.0237 | 1.4262 | 0.0862 |
| cutwA crofts Ti | CENSORED | UNDEFINED | — | — | — |
| cutwA crofts Tr | 3.1915 | 12.1217 | **8.9302** | 3.1782 | **0.0133** |
| f4wA beta Ti | 4.0761 | 3.5425 | **0.5336** | 4.1049 | **0.0288** |
| f4wA beta Tr | 1.2522 | 1.2462 | 0.0061 | 1.4496 | 0.1973 |
| f4wA crofts Ti | CENSORED | 15.0267 | UNMEASURABLE | 12.8489 | — |
| f4wA crofts Tr | 2.7542 | 8.0907 | **5.3364** | 2.0900 | 0.6642 |

Over the 6 cells where a residual exists: the shared-gap currency puts **2 of
6** inside a fifth of a hop (median residual **0.5336**), the own-rate
currency **5 of 6** (median **0.0862**). The registered half-hop bar is
cleared by the companion and missed by the primary — on the primary cell by
**0.5336 vs 0.5000**, i.e. by 6.7%.

That marginality is the finding, not a rounding problem (L210: decompose a
marginal closed-form result, never round it). **Exactness and adequacy are in
tension by construction.** A per-joint rate predicts the crossing but cannot
decompose: with two different rates the Ti-minus-Tr difference is no longer a
difference of two logs over a common `log(rho)`, so there is no `T_A + T_K`
at all. A shared rate decomposes exactly — the identity closed at absolute
error **0.0e+00** (cutwA beta) and **1.8e-15** (f4wA beta) — and misses the
crossing depth. The card asked which of two numbers sets the phase; the
honest answer is that the question is only exactly posable in the currency
that gets the phase slightly wrong.

**The mechanism, declared POST-HOC (pure arithmetic on certified stored
values, no branch): `d_cf` amplifies any rate error by `1/|log rho|`.** From
`d_cf = log(arg)/log(rho)`, a relative error `eps` in the rate moves the
crossing depth by about `d_cf * eps / |log rho|`. The beta operators sit at
`|log rho|` 0.1133 (f4wA) and 0.1074 (cutwA) — amplification ~9x — while the
Crofts operators sit at 0.0249 and 0.0435, amplification **40x and 23x**. So
the same quality of rate estimate is 4.6x more punishing on Crofts, and that
is where the residuals blow up: f4wA crofts Tr's stored rate disagreement
with the gap is only 2.77%, and `8.09 * 0.0277 / 0.0249 = 9.0` hops of
predicted sensitivity against a 6.0-hop observed gap between the two
currencies — same order. On beta the first-order estimate is 0.05 hops
against a 0.51-hop observed gap, i.e. **beta's currency gap is PREFACTOR-
dominated and Crofts's is RATE-dominated.** Two regimes, one formula.

## 2. The attribution, as DESCRIPTION, with its branch short-circuited

PREREG 0a declared Q1 and Q2 observed-derivable and therefore DESCRIPTION
(L214; Kriegeskorte 2009): every input is stored in l216/static.json and the
measured crossings in l217/static.json. The decision rule still ran, and the
model gate — registered first precisely so it could pre-empt the attribution —
fired. Had it passed, both beta pairs would have read `PHASE_FROM_AINF`:

| pair | D_cf | T_A | T_K | share_K | A_inf ratio |
|---|---|---|---|---|---|
| cutwA beta | +2.3837 | **+4.2707** | −1.8870 | 0.3064 | 0.6321 |
| f4wA beta | +2.2963 | **+3.8669** | −1.5706 | **0.2889** | 0.6452 |
| cutwA crofts | unavailable (negative asymptote, PREREG 0d) | | | | |
| f4wA crofts | +6.9361 | −0.8555 | **+7.7915** | **0.9011** | 1.0215 |

On beta the two terms **oppose**: the asymptote alone would separate the
joints by 3.87 hops and the depth-1 drive claws back 1.57, leaving 2.30. On
Crofts the attribution **inverts** — the asymptotes are within 2.2% of each
other (ratio 1.0215) and 90% of the separation is carried by K. **The
attribution is OPERATOR-SPECIFIC, not a property of the wiring**: the same
cells, the same sides, two per-edge reweightings, opposite answers. That is a
descriptive result and it is the most interesting thing in section 2.

## 3. Q3 — the instrument L217 named got built, it WORKS, and the hypothesis
## it was built to test is REFUTED

L217 registered a crossing-phase separation test and could not score it:
its permutation null produced a measured crossing in **both** joints in only
**0.0505** of draws, so the contrast conditioned on an event that almost never
happened (its own law: register the event-existence rate before any contrast
on the event). The closed form does not require the crossing to land inside
d <= 8 — only that the asymptote and the depth-1 term disagree in sign — so
L230 re-poses the identical contrast in a currency whose event is common.

**Existence (registered as the FIRST read):** the closed form is defined in
**0.6500** of draws for Ti, **0.7880** for Tr, and **0.5110** jointly — a
**10.12x** improvement on L217's 0.0505, clearing the registered 0.50 gate and
giving **1,022 usable draws** where L217 had ~101. P3 and P4 both hold.

**DISCLOSED MARGINALITY:** 0.5110 clears 0.50 by 22 draws, and the rate's own
95% normal interval is **[0.4891, 0.5329]** — it straddles the gate. The gate
is therefore not comfortably passed. It does not change the verdict: the
alternative branch was `CF_NULL_DEGENERATE`, an instrument verdict, and the
measured separation percentile is nowhere near its bar.

**The answer: `CF_NOT_SEPARATED`.** |D_cf| = **2.2963** sits at pct_abs
**0.1350** — **86.5% of label-permuted draws produce a LARGER closed-form
crossing separation than the real wiring does** (null median 0.2993, p05
−25.32, p95 +26.73; no moment of this distribution is reported, per PREREG
0i, because d_cf diverges as K -> 0). P5 FALSE. The Ti-vs-Tr phase difference
that L216 and L217 both treated as the striking observation is **not more
extreme than a random relabelling of the same pool cells' sides.**

**And the attribution itself is generic (P6 TRUE):** the real share_K 0.2889
sits at pct_up **0.2715** of 512 defined draws whose own median is **0.5075**.
A random L/R relabelling splits the phase difference about evenly between the
asymptote and the depth-1 term; the real wiring leans to the asymptote, but
well inside the distribution. The asymptote-carried attribution of section 2
is a property of the geometry's generic structure, not of which cells are left.

## 4. Predictions

| | registered | kind | measured | |
|---|---|---|---|---|
| P1 | Q1 == PHASE_FROM_AINF | description | PHASE_MODEL_INSUFFICIENT | **FALSE** |
| P2 | residual <= 0.5 on both primary joints | description | 0.5336 | **FALSE** |
| P3 | cf joint existence rate >= 0.50 | blind | 0.5110 | TRUE |
| P4 | that rate >= 2x L217's 0.0505 | blind | 10.12x | TRUE |
| P5 | Q3 == CF_SEPARATED | blind | CF_NOT_SEPARATED | **FALSE** |
| P6 | share_K pct_up <= 0.95 | blind | 0.2715 | TRUE |

P1 and P2 fail together and that is the registered order working: putting the
model gate ahead of the attribution is what stopped a 3.87-vs-1.57 hop
attribution from being published on top of a closed form that misses its own
measured crossing by half a hop. P5 fails because the instrument finally
existed to ask.

## 5. Verification

- **SLICE A = l216_static.py lines 1-1360 VERBATIM** (sha256
  6a3760d0b387a807; whole-file 8d4740020fcd2a7b), a literal **PREFIX** cut
  immediately before the parent's writer, **AST-proven WRITE-FREE** (0 write
  sites, 0 makedirs), so every pin plus CERT-F4 (73/r21/gi290), CERT-178
  (420), CERT-GEN (44), **CERT-205 (250, halting)**, CERT-GAP (10),
  **CERT-209 (412, halting)** and the lam1 NO-OP re-ran as the code that
  actually produced l216/static.json.
- **PARENT PIN (halting):** l216_tail.py (sha256 d9cb45022621452b) asserted a
  literal **SUFFIX** of l216_static.py **and** equal to the sha that file's
  own generated banner records.
- **CUT AUDIT — STRUCTURAL, by AST:** the 7 cut lines parse to exactly 4
  statements, all bare calls `[makedirs, dump, log, log]`, proven to own the
  parent's writer while SLICE A holds none of it. (A hand-typed count of 5
  halted the first build at the true 6 — the derive-never-retype law, this
  time on a COUNT; repaired to the structural form.)
- **SLICE B = l217_tail.py lines 245-258 VERBATIM** (sha256
  b26c0ab47cf0e2bb), AST-proven to define exactly `["dcross"]` and nothing
  else, so the measured crossing is produced by the expression that wrote
  l217/static.json (L206/L211).
- **CERT-216 (HALTING, 1,903 checks)** — l216/static.json `table` (all 64
  depth cells), `A_inf` (8), `gaps` (4) and `fits` (8) reproduced from this
  run's own in-memory objects at **FLOAT EQUALITY** by the parent's own
  expressions, with the coverage bar **1,900 DERIVED from the artifact's own
  leaf count** plus 3 structural pins (L224/L225), before any crossing was
  read. Key sets compared for **equality** at every level of the recursion.
- **NO-OP RE-ASSERTED (128 checks)** — every cell's stored
  `A_cell_unnormalised` and `A_cell_norm_rel_diff` at float equality, and
  MAXREL 7.19e-14 == L216's stored `norm_noop_max_rel_diff`.
- **CERT-217 (HALTING, 174 checks)** — L217's stored `d_cross`,
  `n_sign_changes`, `censored`, `null_frac_cross` and its three null
  percentiles reproduced at FLOAT EQUALITY on all 8 beta/crofts cells, plus
  L217's Q1 branch, its null event rate and both primary crossing depths.
  This certifies the crossing expression **and** that this run's permutation
  draw stream is L216's and L217's.
- **CERT-AINF (HALTING, 152 checks)** — the per-draw A_inf null (2000 x 8) is
  obtained by calling the certified `side_stats_from` on the stored Perron
  vector, gated by asserting the same call reproduces every stored A_inf
  field **including its percentiles** at float equality. The null vector is
  not stored anywhere, so this gate is what licenses using it.
- **Identity asserts at DERIVED tolerances** (never fixed): the split-log
  form against the direct form per cell, and `T_A + T_K == D_cf` per pair
  (0.0e+00 / 1.8e-15 against bars derived from the term magnitudes).
- **AST audits in the builder:** Import/ImportFrom walk proves no lab module
  is imported (L175); a write-**SITE** walk proves exactly ONE write in the
  generated file, `json.dump(..., open('l230/static.json','w'))` on a single
  statement, plus one `makedirs('l230')`.
- `md5sum -c l230/prior.md5` (5 files: l205/l209/l210/l216/l217 static.json)
  **GREEN before and after**; `(size, mtime_ns)` fingerprints on all five
  asserted unchanged after the run.
- No live change, no draft edit, `sessions/` untouched.

## 6. What this changes

- **L217's registered crossing-phase separation is now scored, and it is
  refuted.** Anything downstream that treats the Ti-vs-Tr phase difference as
  a wiring signature must be rewritten: it is at the 13.5th percentile of its
  own membership null.
- **The depth-k / Neumann family keeps the closed form as a DESCRIPTION
  instrument only.** It predicts a crossing depth well in the per-joint rate
  currency and decomposes exactly only in the shared-rate currency, and those
  are different models.
- **New method law (quotable):** when a closed form's parameters admit a
  SHARED and a PER-UNIT estimate, the shared one buys an exact additive
  attribution and the per-unit one buys predictive adequacy — measure both,
  register which carries the branch, and report the amplification factor
  (`1/|log rho|` here) that sets how badly the shared estimate can miss.
- **New method law:** a null's EVENT-EXISTENCE rate is a property of the
  CURRENCY, not of the null. Restating the same contrast in a currency whose
  event is structurally more common took L217's unusable 0.0505 to 0.5110 —
  10.1x, 1,022 usable draws — without a single new draw. When a card dies of
  a degenerate event rate, look for a currency change before declaring the
  question unanswerable.
