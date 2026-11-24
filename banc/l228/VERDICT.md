# L228 VERDICT — the DEPTH-2 account of the resurrection

Tick 259, 2026-11-23. PREREG `l228/PREREG.md` written first, ZERO amendments.
Zero rollouts, zero settles, zero dynamics. Static edge arrays only; the one
RNG is the declared membership-permutation null (seed 22821, 2000 draws).
Runtime **4 s**.

## Registered branch: **D2_RISES_EVERYWHERE**. Predictions **3 of 6**, and all three FALSE ones are load-bearing.

| | claim | result |
|---|---|---|
| P1 | branch == `D2_RISES_SPECIFIC` (the card as written) | **FALSE** — `D2_RISES_EVERYWHERE` |
| P2 | `RISE(Tr_L)` — d2 rises where d1 fell | **TRUE** (+5.1128) |
| P3 | `share_neg(Tr_L) > 0.50` (the card's mechanism) | **FALSE** (+0.3061) |
| P4 | `d2_gain(Ti_L) > d2_gain(Ti_R)` — the L/R sign depth-1 gets wrong | **TRUE** |
| P5 | Q4 Tr `pct_two` < Ti `pct_two` | **TRUE** (.1700 vs .8360) |
| P6 | Spearman(dynamic fold, relative dd2) > 0 | **FALSE** (−0.2000) |

P1's failure was predicted BEFORE measurement by premise correction 0e, which
read L208's stored levels and found that **all four** pool-sides rise across
the floor (Tr_L 110.7x, Ti_R 4.58x, Ti_L 2.29x, Tr_R 1.76x). The card's
four-cell table was written as if the resurrection were Tr_L-specific. It is
not; Tr_L is only the pool that crosses from dead. So `D2_RISES_EVERYWHERE` is
the branch that MATCHES the dynamics and `D2_RISES_SPECIFIC` would have been
the mismatch — the registered expectation was wrong in the direction that
makes the result better.

## 1. The depth-2 term SIGN-FLIPS the depth-1 verdict, on all four pool-sides

| pool | dd1_gain (L215) | d1 ratio | dd2_gain | rel dd2 | sign flip | dyn fold |
|------|-----------------|----------|----------|---------|-----------|----------|
| Ti_L | −0.5190 | .8472 | **+6.2269** | .9011 | yes | 2.29x |
| Ti_R | −0.6297 | .8402 | **+6.4461** | .9145 | yes | 4.58x |
| Tr_L | **−0.0946** | **.7978** | **+5.1128** | .9229 | yes | **110.74x** |
| Tr_R | −0.1211 | .6787 | **+3.0500** | .9513 | yes | 1.76x |

Depth-1 net drive FALLS on every pool-side (L215, re-certified here at float
equality). Depth-2 signed drive RISES on every pool-side. `d2` is **negative**
everywhere (−56.7 to −75.4 in the primary g²-scaled currency): these pools sit
under net two-hop INHIBITION, and the floor relieves ~5-10% of it. So the
answer to the card's question is that **depth 2 is not anti-predictive — it
agrees in sign with the dynamics where depth 1 disagreed, on 4/4 pool-sides.**

## 2. The strongest result is the one nobody selected for: depth 2 recovers the L/R ORDERING depth 1 gets wrong

`l228/ordering.json` (post-hoc, pure arithmetic on certified values, 10 gates):

| joint | dynamics | depth-1 says | agrees | depth-2 says | agrees |
|-------|----------|--------------|--------|--------------|--------|
| Ti | L hotter (.1845 > .1187) | R higher (+3.2677 vs +4.2681) | **no** | L higher (−56.72 vs −68.94) | **yes** |
| Tr | R hotter (.0765 > .0221) | L higher (+0.4821 vs +0.2645) | **no** | R higher (−61.21 vs −59.62) | **yes** |

**Depth-1: 0 of 2. Depth-2: 2 of 2.** This is L208's dissociation — the one
that has now failed depth-1 twice on different quantities — resolved by adding
exactly one hop. Scored as DESCRIPTION with its resolution floor named: two
joints give four sign patterns, so the smallest achievable coin-flip
probability is 1/4 = .25 (L225's law). It is two data points, and it is the
only leg here that is not explained by the bulk effect in §3, because mass
retention is side-symmetric (`ret2` .8161/.8147 on Ti, .8312/.8272 on Tr) and
this leg reads the LEVEL, not the change.

## 3. The honest deflation: the depth-2 RISE is BULK, not sign structure

Because `d2 < 0` everywhere, removing ~18% of the two-hop mass makes `d2`
rise *generically*. The sign-neutral counterfactual (L215's instrument, one
depth up: `d2_pred = d2_cutwA * ret2`) says so directly: `|S2_sign| < 0.25` on
**three of four** pool-sides (Ti_L −.0533, Ti_R −.2357, Tr_L −.1357), i.e. the
bulk mass-retention prediction accounts for 86-105% of the measured rise, and
the residual sign restructuring **dampens** it rather than driving it. Only
Tr_R has a large residual (−.8898).

Unlike L215, all four pool-sides CLEAR the degeneracy bar here (|dd2| 3.05-6.45
against bars 1.79-2.36), so the ratio is readable for the first time in this
family — and what it says is that the depth-2 rise is not a sign-specific
phenomenon. "d2 rises" is therefore a weak mechanism: it would hold for almost
any edge deletion on a net-inhibited pool. The ORDERING result in §2 is the
part that bulk cannot produce.

## 4. The card's registered mechanism is REFUTED on the actor and CONFIRMED off it

The clause was "the rise should be carried by sources whose own net in-mass is
NEGATIVE" (the disinhibition relay). Measured share of `dd2` carried by the
`net_in_cutwA < 0` class:

- Ti_L **+0.5895**, Ti_R **+0.5579** — clears .50
- Tr_L **+0.3061** — fails; the actor's rise is carried by net-POSITIVE
  sources (share_pos +0.6939)
- Tr_R **−0.0921** — the net-negative class pushes the *wrong way*

So the relay story holds on the two pools nobody selected and fails on the one
the card was written for. The quadrant table (0h bookkeeping, raw units) says
what actually carries Tr_L's rise: the largest single term is
`exc_srcneg` **+46,219** — the floor removing EXCITATORY edges from
net-inhibited sources, whose two-hop contribution was negative precisely
because their sources are suppressed — partly cancelled by `inh_srcneg`
**−34,315** (the genuine disinhibition quadrant shrinking, which costs the
pool positive drive). The relay is real but it is one hop shorter and the
dominant sign is the opposite of the hypothesis.

## 5. P6: depth 2 gets the ORDER right and the MAGNITUDE nowhere near

Relative `dd2` is .9011 / .9145 / .9229 / .9513 — a 5-10% band — against
dynamic folds spanning 1.76x to 110.74x. Spearman(fold, rel dd2) = **−0.2000**
(exact permutation p_up .6250, floor .0417). A linear two-hop term that moves
by 8% cannot encode a 110x fold change: that fold lives in the relu gate, in
*which units are above threshold*, not in the anatomical expansion. This is
the quantitative version of the card's own escape clause and it points at the
same instrument.

## 6. Two premise corrections that a GATE found, both disclosed

**(a) 0f and 0g contradicted each other, and the assert caught it.** 0f said
sources with `net_in == 0` contribute nothing to `d2`; 0g registered a FIXED
baseline classification. Both are defensible alone and incompatible together:
a source with `net_in_cutwA == 0` can acquire `net_in_f4wA != 0`, so under the
registered fixed classification the zero class is a null class **only on the
arm whose net defines it**. `assert parts["zero"] == 0.0` halted on
`Ti_R / f4wA`. Repaired to the true statement (exact zero asserted on the
BASELINE arm; measured on the floored arm) plus a three-class
`neg + zero + pos == dd2` identity. Numerically the zero class is negligible
(max share of absolute two-hop mass **9e-05**, on Ti_R only) — but the
decomposition identity was wrong until the gate fired. **METHOD LAW: a
degeneracy guard must be scoped to the ARM whose own quantity defines the
degeneracy — a "null class" defined on a baseline is not null on a perturbed
substrate, and two separately-correct premise corrections can be jointly
inconsistent.** (L218's scope-your-guards law, from a new direction.)

**(b) A hand-typed pin contradicted bytes already certified.** The premise
assert `abs(_D1R - 0.7978345214963712) < 1e-12` halted at the true
0.7978346519279342 — I had retyped a literal from a 6-decimal print. Repaired
at the root: the pin is now DERIVED from `l215/static.json`'s own stored NETs
(both already pinned at float equality by CERT-215) with a BRACKET
`0.79 < r < 0.81` for the human-readable claim. That is the
tick-251/254/256/257 lesson — **derive probes and pins from the file, never
retype them** — hitting a PIN rather than a push probe for the first time.

## 7. A method law from the currency, worth more than the card

**A SHARE of a cross-substrate DIFFERENCE is not invariant to per-substrate
rescaling, and the rescaling can flip its SIGN.** `share_neg` computed on raw
`d2` vs on the registered g²-scaled `d2`:

| pool | raw share_neg | g²-scaled share_neg |
|------|---------------|---------------------|
| Ti_L | +0.5967 | +0.5895 |
| Ti_R | +0.5836 | +0.5579 |
| Tr_L | **+0.4229** | **+0.3061** |
| Tr_R | **+0.2994** | **−0.0921** |

Both arms are divided by the same cell count but multiplied by DIFFERENT gains
(g²_f4wA/g²_cutwA = 1.09773), so each class's contribution to the difference is
reweighted asymmetrically. On Tr_R this moves a +30% share to a **negative**
one. L209's law ("a ratio is invariant to a global rescale") does not apply
here because the rescale is not global — it differs per substrate by
construction of the op-point match. Register which currency carries a share
statistic, exactly as L218 demanded for overlap and L227 for mirrors.

## 8. What this does to the depth-k family

Depth 1: anti-predictive in sign, 0/2 on ordering. Depth 2: correct in sign on
4/4, correct in ordering on 2/2, and quantitatively hopeless (8% vs 110x) with
its *change* explained by bulk on 3/4. The registered escape did NOT fire
(`escape_fired False`), so the depth-k family stays — but it stays as a
**side-ordering** instrument, not as an account of the resurrection's
magnitude. The named next instrument is unchanged and is now better motivated:
the LINEARISED GATED operator at the actual operating point (L178 class),
because the 110x lives in the gate.

## Certification

- **CERT-215 (HALTING, 76 float equalities)** — every stored
  `l215/static.json` `rows[*][cutwA|f4wA]` field (Mp, Mm, NET, TOT, n_edges,
  NET_per_cell, NET_gain, inh_frac) on all four pool-sides, plus `n_cells`,
  `ret` and `Q2_sign_neutral[*].dNET_act`, reproduced from this run's own
  arrays **using the parent's own expression** (separated ± sums then
  subtract — L206's law), plus `branch == "D_DEGENERATE"` and the lam1-no-op
  flag.
- **CERT-D2 (HALTING, 86)** — the two-hop kernel proven, never trusted:
  6 exact `np.array_equal` checks (`np.bincount` vs `np.add.at`, on `net_in`
  and on both the signed and absolute two-hop accumulations, both substrates)
  plus **80 definitional `math.fsum` per-cell probes** (40 random pool cells x
  2 arms) against bars DERIVED from each cell's own `sum|contrib|`
  (`8·eps·Σ|c|`), never a fixed tolerance (L216/L224).
- **Inherited FREE** via `l215_tail.py` lines 1-157 BYTE-FOR-BYTE: CERT-205
  (36), CERT-TBL (28), CERT-G (2), the substrate pins (cutwA 21785/644177,
  f4wA 21789/469618, eligible 469256), pool sizes invariant on both substrates
  with zero L/R overlap, and the L208 branch / POST-HOC-label premise asserts.
- **PARENT PIN (HALTING)** — `l215_tail.py` sha256 `dbc507e8f48530ae` equals
  the value `l215_static.py`'s own generated banner recorded, AND is a literal
  **SUFFIX** of `l215_static.py`: the inherited slice is provably the code
  that produced `l215/static.json`.
- **HEAD3 line-set audit** — the slice is exactly lines 1-157 of a 402-line
  file and the 245 cut lines are asserted to OWN L215's measurement and writer
  (`def signed_in(`, `ROWS = {}`, `Q4 = {}`, `o["branch"] = BRANCH`,
  `json.dump(o,`) while the slice is asserted not to contain them —
  structural, not a bare-token scan (the tick-248/251/256/257/258 trap).
- **AST audits in the builder** — an `ast` Import/ImportFrom walk proves no lab
  module is imported (L175) and an `ast` Call walk proves the generated script
  contains **exactly one** write (`l228/static.json`), located in the tail.
- `md5sum -c l228/prior.md5` (5 files) GREEN before AND after; `(size,
  mtime_ns)` fingerprints on `l205/static.json`, `l208/static.json`,
  `l208/addendum_floor.json`, `l215/static.json` asserted unchanged after the
  run; the ordering script fingerprints its own two inputs the same way.
- Generated sha256 `aea81b0191d49176` (1,027 lines); HEAD3 sha
  `e42be32bd499b9c9`.

## Limits

1. Uniform-X anatomical expansion: `net_in` is the depth-1 drive onto a source
   assuming unit activity everywhere. The real system is relu-gated and ~16.8%
   active (L208), so `d2` is an ANATOMICAL two-hop quantity, not the
   operating-point two-hop gain. §5 is the measured cost of that.
2. The Tr_L pools were SELECTED for being dead (L208's post-hoc floor leg):
   every Tr_L number is a DESCRIPTION of a selected object, and Q4 is a
   handedness null on a preselected pool (Kriegeskorte 2009). Disclosed: Tr's
   `A_dd2` = +0.2527 at `pct_up` .085 does NOT clear .05 two-tailed (.170) —
   P5 is a comparison of two percentiles, not a significance claim.
3. `ret2` mixes the floor with the small node-set change (cutwA drops
   `ng_desc[:24]`, f4wA drops `ng4[:20]`); the node-matched eligible
   comparator is inherited from the L215 slice.
4. n = 4 pool-sides and n = 2 joints: every cross-pool rank statistic has an
   exact permutation floor (1/24 and 1/4) and is DESCRIPTION.
5. The source-class decomposition is classified on the BASELINE arm (0g);
   2,145 nodes migrate class across the floor and the per-arm classification
   is a diagnostic only. The 0a hybrid diagnostic says the edge-set change
   alone accounts for only −2.73% of Tr_L's `dd2` — i.e. the rise is carried
   by the change in the SOURCES' states, not by the missing edges per se.

## Artifacts

`banc/l228/{PREREG.md, VERDICT.md, static.json, ordering.json, prior.md5,
build.out, run.out, run.err}`; code `banc/l228_{build,tail}.py` ->
`l228_static.py`, `banc/t259_ordering.py`.
