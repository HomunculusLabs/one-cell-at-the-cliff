# L229 VERDICT — near-balance as a POPULATION question

Branch: **B_FLOOR_DEGENERATE** (registered, fired first in the registered
order). Predictions **3 of 6** TRUE, and all three FALSE ones are
load-bearing. PREREG `l229/PREREG.md`, registered before `l229_tail.py`
existed and before any L229 quantity was measured. Static: ZERO rollouts,
zero settles, zero new dynamics; every dynamic number read from the stored
npz, opened read-only and fingerprinted before and after.

## 1. The answer: the near-balance hypothesis does NOT survive its own population

L215's suggestive observation was that Tr is the near-balanced joint
(inh_frac .4943/.4965 vs Ti's .4555/.4511) and Tr is the joint with a dead
side. Asked nonselectively over all ten cord pool-sides:

| leg | rho(near, range) | exact two-sided p |
|---|---|---|
| PRIMARY B36 (12 arms) | **-0.030303** | 0.9460 |
| REPLICATION B37 (fresh seeds) | -0.115152 | 0.7589 |
| MENU COMPANION B35 (7 arms) | -0.090909 | 0.8113 |
| relative range (rng/mean) B36 | +0.066667 | 0.8651 |
| mean level B36 | +0.066667 | 0.8651 |
| f4wA substrate B36 | +0.054545 | 0.8916 |
| menu-matched 7 arms inside B36 | -0.090909 | 0.8113 |

Nearness-to-balance explains essentially none of the rank variance in dynamic
range, in every currency, on both substrates, in all three batches. P2
(positive) is FALSE; the point estimate is *negative* and indistinguishable
from zero.

**The reason this is informative rather than merely underpowered is the
reliability control.** `rho(range_B36, range_B37) = +0.963636`, exact
two-sided p = 4.905e-05 — the dynamic-range statistic is almost perfectly
reproducible across a fresh seed batch. The instrument works; the predictor
does not predict. At n=10 a null is registered as uninformative about small
effects (PREREG 0i), but a predictor at rho -0.03 against an outcome measured
at rho +0.96 reliability is not a power story.

## 2. THE HEADLINE IS A METHOD RESULT, AND PREREG 0a IS WHY IT EXISTS

**2 of 10 pool-sides sit ABOVE inh_frac 0.5** — Ta_L at 0.561114 and Ta_R at
0.522940 — so `near = -|inh_frac - 0.5|` and raw `inh_frac` are NOT
rank-identical (P1 FALSE). And the two currencies do not merely differ in
magnitude, they land on opposite sides of a registered branch bar:

- `rho(near, range_B36)` = **-0.030303** (the hypothesis's own quantity)
- `rho(inh_frac, range_B36)` = **-0.454545**, exact two-sided p 0.1912

-0.4545 clears the registered |0.40| band. Had the currency not been
registered in advance, this card would have reported a moderate INVERSION —
"balance predicts stability" — that is entirely an artifact of using a ratio
as a proxy for nearness past the range where the proxy is monotone. The two
Ta pool-sides are inhibition-dominated, so raw inh_frac ranks them as the
*least* balanced when they are in fact among the more balanced, and they
happen to be the two smallest-mass pool-sides with the lowest levels.

**The transportable law**: a NEARNESS hypothesis stated in terms of a RATIO
is only testable while every unit sits on one side of the ratio's centre, and
that premise is a MEASUREMENT, not an assumption. Register the centred
currency, measure the count of units past the centre, and report both. This
is the L218 overlap-currency law and the L227 mirror law arriving a third
time, now on an index with a meaningful centre.

## 3. The selected observation does not even survive as a RANKING (P3 FALSE)

Registered: Tr_L and Tr_R are the two most-balanced pool-sides. Measured
`near` ranking, most balanced first:

`Pr_R -0.002941` > `Tr_R -0.003539` > `Tr_L -0.005660` > `Sr_R -0.009280` >
`Pr_L -0.014540` > `Sr_L -0.022129` > `Ta_R -0.022940` > `Ti_L -0.044481` >
`Ti_R -0.048938` > `Ta_L -0.061114`

Tr_R and Tr_L are ranks 9 and 8 of 10 — **Pr_R (7 cells, promotor/remotor) is
the most balanced pool-side in the cord**, and it is not notably labile
(range 0.079185, rank 5 of 10). The Ti-vs-Tr contrast L215 noticed is real
and reproduces exactly (CERT-215R, 68 float equalities), but it is a contrast
between two of ten units, and the population ordering it suggested is wrong.

## 4. The registered escape FIRED and it short-circuits the population claim

**B_FLOOR_DEGENERATE**: `Ta_L`'s maximum level over all twelve B36 arms is
0.031168, below the registered dead bar BG + 2*NOISE = 0.04. `Pr_L` is
additionally dead in B35 (max 0.022655) while alive in B36/B37 (max 0.071352
/ 0.085242) — the same pool-side, dead or alive depending on which arm menu
it is offered, which is itself the lability phenomenon the card was chasing,
observed in the wrong currency. P6 TRUE, as registered.

Per the L222 rule the escape CHANGES CONTROL FLOW: `population_claim_available`
is False, and the surviving-subset reading is computed only on this branch —
n = 9, `rho(near, range) = -0.416667`, **p withheld rather than approximated**
because the exact n=10 enumeration does not apply at n=9 and the card
registered no n=9 null. The all-ten correlation is still reported above; the
branch records that the ten units are not ten comparable units.

## 5. Confounds: not confounded, but the range tracks SIZE more than balance

`|rho(near, n_cells)| = 0.238542` and `|rho(near, TOT)| = 0.272727` — both
below the registered 0.70 bar, so **B_CONFOUNDED did not fire**. But the
largest associations in the whole card (after the reliability control) are the
outcome's own size legs: `rho(range, TOT) = +0.393939` (p 0.2632) and
`rho(range, n_cells) = +0.373104` (ties present: n_cells has 7 distinct
values in 10, so p is withheld per PREREG 0f). Dynamic range is better
predicted by how much in-mass a pool-side receives than by how balanced that
mass is — a direction for L263 below, not a claim here.

## 6. Certification

- **CERT-215R (halting, 68 float equalities)** — L215's own ROWS loop
  re-executed with the inherited certified `signed_in` and compared field by
  field against `l215/static.json`, with the coverage bar DERIVED FROM THE
  ARTIFACT (`set(got) == set(stored[sname])` per sub-dict, plus a summed
  count recomputed from the stored dict's own lengths). A hand-typed bar of
  36 HALTED the first run at the true value 68 — the L224 law (derive the
  coverage bar from the artifact, never guess it) caught on its first use
  here.
- **CERT-208L (halting, 202 float equalities)** — `lvl`, `fhi95`, `fhi90`,
  `flo` and `pmax` for both joints x five ARMS5 arms x two batches x two
  sides reproduced at FLOAT EQUALITY from my own window rebuild, using
  l208's exact expression (`np.concatenate(cols).astype(np.float64)` then
  `.mean()` — L206: a float-equality claim is a claim about the expression),
  plus l208's own stored window counts. This is what licenses reading `lvl`
  for six new pool-sides and twelve arms.
- **CERT-W (halting)** — six window/segment literals asserted present in
  `l169b2_run.py`'s TEXT (read as text, never imported), `|W| == 3000`,
  `|W_on| == 1400`.
- **Pool-side construction gated against the certified masks** — all 20 pool
  sizes pinned via S92 + S101 inside the inherited HEAD1, a/b disjointness
  asserted per pool-side, and the four Ti/Tr masks asserted ARRAY-IDENTICAL
  to HEAD3's certified `SIDEMASK` (so the six new pool-sides are built by the
  same construction that reproduces the certified four).
- **EXACT null, no resolution floor** — all 3,628,800 label assignments
  enumerated; 166 attainable rho values; minimum attainable two-sided p
  5.511e-07. Every reported p is exact, and every rank statistic is MIDRANK
  with its distinct-value count printed (two legs have ties and their p is
  withheld rather than approximated).
- **Slices, verbatim and sha-pinned, never imported (L175)** — HEAD1
  l151_static.py 1-319 `e6245e8306dc8a0f`, HEAD2 l178_tail.py 22-83
  `66112b0c221d02d8`, HEAD3 l215_tail.py 1-164 `2fb8c7f54a56e5f1` (parent
  file `dbc507e8f48530ae`, asserted a literal SUFFIX of l215_static.py AND
  equal to the TAIL sha that file's own banner records), HEAD4
  l169b2_verdict.py 13-63 `de636f4a18ee789b`. Generated sha
  `ad76ed3c38c48cdc` before the coverage repair; final generated script
  rebuilt after it. HEAD3's 238 cut lines audited STRUCTURALLY to own
  `ROWS = {}`, `Q1 = dict(`, `json.dump(` and `o["branch"] = ` while the
  slice is asserted to contain none of them. AST Import/ImportFrom walk
  proves no lab module is imported; AST Call walk proves EXACTLY ONE write
  site (`l229/static.json`) with `open(...,"w")` and `json.dump` on the same
  line and no `savez`/`to_csv`/`write_text`/`os.replace` anywhere. Final
  generated script `l229_static.py`, 1,091 lines, sha256
  `b7413ee719100561` (tail `8cb5b85ff2c7970c`); the pre-repair build was
  `ad76ed3c38c48cdc` and was rebuilt after the coverage fix.
- `md5sum -c l229/prior.md5` (7 files incl. all three npz) GREEN before and
  after; (size, mtime_ns) fingerprints on all three npz and on
  l215/static.json and l208/static.json asserted unchanged after the run.

## 7. Disclosed

- Two build-time halts, both repaired to something stronger: the hand-typed
  CERT-215R count (above), and an AST write audit that counted
  `json.dump(o, open(p,"w"))` as two writes — repaired to a write-SITE audit
  that asserts the dump and the open are the same line, which is strictly
  stronger than a count.
- The f4wA substrate companion flips the primary's sign (+0.0546 vs -0.0303).
  Both are inside noise and both give the same branch, so this is reported as
  a sign instability at zero effect, not as a substrate disagreement.
- `near` is computed on an ANATOMICAL in-mass ratio under the log1p ladder
  convention; it is not a measured E/I current balance, and the dynamic level
  is a pool MEAN (l208's declared limit: the per-cell ceiling fraction is not
  recoverable from stored traces). Measured ceiling fraction is 0.0000 on all
  ten pool-sides in all arms except Pr_L in B35 at 0.0001, so the L260
  saturation correction is free here — which is exactly why PREREG 0c
  required measuring it rather than assuming it.
- PREREG 0h observation status honoured: L215's four Ti/Tr `inh_frac` values
  and three of l208's Ti `lvl` values were read while scoping and were
  declared DESCRIPTION in advance; every branch sat on unobserved quantities
  (the six Ta/Sr/Pr inh_frac values, all ten 12-arm ranges, every
  correlation).

## 8. What this changes

The "balance predicts lability" reading of L215 is **retired as a population
claim** and kept only as a two-unit contrast. Any draft sentence that leans on
Tr's near-balance to explain its dead side must say so about Tr specifically,
with Pr_R named as the counterexample (more balanced, unremarkably labile).
The reusable gains are the exact n=10 enumerated null (free for any future
ten-unit lane leg), the certified ten-pool-side population object, and the
centred-currency law in §2.
