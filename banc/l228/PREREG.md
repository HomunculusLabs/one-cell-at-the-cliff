# L228 PREREG — the DEPTH-2 account of the resurrection (static, zero rollouts)

Tick 259, 2026-11-23. Written BEFORE any L228 value was computed. Zero
rollouts, zero settles, zero dynamics. Reads stored artifacts read-only. The
only RNG is the one declared membership-permutation null (seed 22821, 2000
draws).

The card: L215 showed the depth-1 net drive onto the left Tr pools FALLS 20.2%
across the floor while the pools go from dead (.0002) to alive (.022), so
depth-1 is ANTI-PREDICTIVE and the resurrection must be a network effect. Ask
it at depth 2: `d2(P) = sum over edges e into P of vals[e] * net_in(src[e])`
on cutwA vs f4wA, per side, per joint, gain-scaled, with the SAME sign-neutral
counterfactual and the SAME membership null.

## 0. PREMISE CORRECTIONS (all written before measuring)

**(0a) A depth-2 operator must be read on ONE substrate, not a hybrid.** The
card's formula names two objects — the edge set into P, and `net_in` of the
sources. Both must come from the SAME substrate, otherwise `d2` is a chimera
whose difference mixes an edge-set change with a source-state change. Both are
therefore taken from the arm under test, so `d2` is exactly the second term of
that arm's own linearised expansion (`1' W_S^2 1` restricted to P). The
hybrid (f4wA edges x cutwA `net_in`) is computed and reported as a DIAGNOSTIC
decomposition only; it carries no branch and no prediction.

**(0b) The gain scaling at depth 2 is g^2, not g.** L215 reported depth-1
quantities as `g * NET/n`. A depth-2 term carries the gain TWICE, so the
primary currency here is `g^2 * d2/n`. This is not cosmetic: the measured
op-point gains are `g_cutwA = 0.14365819573402408` and
`g_f4wA = 0.15051452517509462` (ratio **1.04773**), so the floored arm's
depth-2 lift from gain alone is **1.04773^2 = 1.09774** — twice the depth-1
lift. Registering `g^1` would understate the floored arm's depth-2 drive by
4.8%. Both currencies are stored; `g^2` is PRIMARY. (L209's law says a global
rescale cannot move a RATIO; it moves every ABSOLUTE cross-substrate
difference, which is what the directional primary here is.)

**(0c) The DIRECTIONAL leg is PRIMARY and the ratio is a conditional
refinement — L215's own lesson.** L215's registered primary `S_sign` was a
ratio of signed differences and it came back DENOMINATOR-UNSTABLE on three of
four pool-sides (`D_DEGENERATE`). The depth-2 analogue `S2_sign` is defined
below with the same 1%-of-own-mass-scale degeneracy bar, computed, and read
ONLY on pool-sides that clear it. The branch is carried by the SIGN of
`dd2_gain` — a quantity with no denominator.

**(0d) Selection status, named not hidden (Kriegeskorte 2009).** The Tr_L
pools were SELECTED for this family by being the dead side in L208's post-hoc
floor leg. Every Tr_L number here is a DESCRIPTION of a selected object. The
Q4 null is a handedness null on a preselected pool: it buys multiplicity
discipline INSIDE the pool, never a p-value for "a pool". The Ti leg is the
out-of-selection comparator.

**(0e) THE DYNAMIC EFFECT IS NOT SPECIFIC TO Tr_L, SO THE CARD'S FOUR-CELL
TABLE MISLABELS WHICH BRANCH CONFIRMS THE MECHANISM.** Read from
`l208/static.json["arms"]` BEFORE building anything, the stored B36 pool
levels rise across the floor on ALL FOUR pool-sides:

| pool | cutwA lvl | f4wA lvl | fold |
|------|-----------|----------|------|
| Tr_L | 0.000199 | 0.022063 | **110.9x** |
| Tr_R | 0.043483 | 0.076546 | 1.76x |
| Ti_L | 0.080565 | 0.184510 | 2.29x |
| Ti_R | 0.025893 | 0.118692 | 4.58x |

So `D2_RISES_EVERYWHERE` is the branch CONSISTENT with the dynamics, and
`D2_RISES_SPECIFIC` would be a MISMATCH. Tr_L is not the only pool that wakes
up — it is the only one that crosses from dead, and it has by far the largest
fold change. The card's registered expectation (specific rise) is kept as
written and scored as written (P1), because a registration is not amendable
after the fact for convenience; what is added, pre-measurement, is a FOLD-RANK
leg: does the relative `dd2` rank the four pool-sides in the dynamic
fold-change order Tr_L > Ti_R > Ti_L > Tr_R? With n = 4 the permutation
resolution floor is 1/24 = .0417 (L225's law), so this leg is DESCRIPTION with
its exact permutation p printed, never a branch.

**(0f) The ZERO class in `net_in` is a real category, not a missing value
(L224).** Sources with `net_in == 0.0` contribute exactly nothing to `d2` at
any weight. Their count and their share of the edge set are measured and
reported BEFORE the sign decomposition, and the three-class decomposition
(neg / zero / pos) is asserted to sum to `d2` exactly rather than assuming the
zero class is empty.

**(0g) The sign decomposition must use a FIXED classification, or it measures
two things at once.** The card's mechanism clause is "the rise should be
carried by sources whose own net in-mass is NEGATIVE". A source's `net_in`
sign can itself change across the floor, so classifying each source on its OWN
arm would confound "which sources carry the rise" with "which sources changed
class". The registered classification is therefore `sign(net_in_cutwA[src])` —
the BASELINE arm, fixed — and the per-arm classification is reported as a
diagnostic (with the class-migration count) only.

**(0h) The sign bookkeeping of a two-hop term is not intuitive and is stated
here in advance.** A contribution `vals[e] * net_in(src[e])` is POSITIVE when
both factors are negative, i.e. an INHIBITORY edge from a source that is
itself net-inhibited is a DISINHIBITING two-hop term. That is exactly the
relay the card hypothesises, so the registered mechanism clause is scored on
the signed share of `dd2` carried by the `net_in_cutwA < 0` class, and the
four quadrants (sign of `vals[e]` x sign of `net_in`) are tabulated.

**(0i) The sign-neutral counterfactual needs a depth-2 definition.** L215's
was `NET_pred = NET_cutwA * ret` with `ret` the pool's own absolute in-mass
retention. The depth-2 analogue uses the two-hop absolute mass
`TOT2 = sum |vals[e]| * |net_in(src[e])|`: `ret2 = TOT2_f4wA / TOT2_cutwA` and
`d2_pred = d2_cutwA * ret2`. This is the same object — "what the floor would
do if it stripped mass without touching the sign balance" — one depth up.

## 1. Anchors asserted BEFORE any new number (halting)

- **Inherited free (verbatim slices):** CERT-205 (36 float equalities),
  CERT-TBL (28), CERT-G (2), the substrate pins (cutwA 21785 nodes / 644177
  edges, f4wA 21789 / 469618, floor-eligible 469256), pool sizes invariant on
  both substrates with zero L/R overlap, and the L208 branch /
  POST-HOC-label premise asserts — all of them re-run because
  `l215_tail.py` lines 1-157 arrive BYTE-FOR-BYTE.
- **PARENT PIN (halting):** `l215_tail.py` is asserted a literal SUFFIX of
  `l215_static.py` and its sha256[:16] must equal `dbc507e8f48530ae`, the
  value `l215_static.py`'s own generated banner recorded. That is what proves
  the inherited slice is the code that actually produced `l215/static.json`.
- **CERT-215 (float equality, HALTING):** every stored `l215/static.json`
  `rows[*][cutwA|f4wA]` field (Mp, Mm, NET, TOT, n_edges, NET_per_cell,
  NET_gain, inh_frac) on all four pool-sides, plus `ret` and
  `Q2_sign_neutral[*].dNET_act`, reproduced from THIS run's own arrays using
  the parent's own expression. Includes the card's premise number:
  `rows["Tr_L"]["f4wA"]["NET"] / rows["Tr_L"]["cutwA"]["NET"] == 0.797835...`
  (the 20.2% fall) and `branch == "D_DEGENERATE"`.
- **CERT-D2 (HALTING):** the fast two-hop kernel is proven, never trusted.
  (i) a `np.bincount` implementation is `np.array_equal` to an `np.add.at`
  implementation on both substrates and on both the signed and absolute
  accumulations; (ii) on 40 pool cells the definitional per-cell sum computed
  by `math.fsum` over that cell's own in-edges agrees with the kernel within a
  bar DERIVED from the data (`8 * eps * sum|contrib|` for that cell, L216/L224
  — derive the bar, never fix it); (iii) the neg/zero/pos class decomposition
  sums to the undecomposed `d2` within the same derived bar.
- Read-only `(size, mtime_ns)` fingerprints on `l205/static.json`,
  `l208/static.json`, `l208/addendum_floor.json`, `l215/static.json` and
  `l169b2/raw_l169b2.npz`, asserted unchanged after the run; `md5sum -c
  l228/prior.md5` GREEN before and after. No lab module imported (L175).

## 2. Registered quantities

For each pool-side P in {Ti_L, Ti_R, Tr_L, Tr_R} and each arm S in
{cutwA, f4wA}, with `E_S` the arm's edge mask and `n` the pool-side's cell
count:

- `net_S[v] = sum_{e in E_S, dst[e]=v} vals[e]` (signed depth-1 net in-mass)
- `d2_S(P) = sum_{e in E_S, dst[e] in P} vals[e] * net_S[src[e]]`
- `TOT2_S(P) = sum_{e in E_S, dst[e] in P} |vals[e]| * |net_S[src[e]]|`
- `d2_gain_S(P) = g_S^2 * d2_S(P) / n`  **(PRIMARY currency)**
- `dd2_gain(P) = d2_gain_f4wA(P) - d2_gain_cutwA(P)`  **(PRIMARY statistic)**
- `ret2(P) = TOT2_f4wA(P) / TOT2_cutwA(P)`;
  `d2_pred(P) = d2_cutwA(P) * ret2(P)`;
  `dd2_pred(P) = g_f4wA^2 * d2_pred/n - g_cutwA^2 * d2_cutwA/n`
- `S2_sign(P) = (dd2_gain - dd2_pred) / dd2_gain`, read ONLY when
  `|dd2_gain| >= 0.01 * g_cutwA^2 * TOT2_cutwA(P) / n` (the degeneracy bar)
- `share_neg(P) = dd2_gain_[net_cutwA<0 sources] / dd2_gain`, read ONLY when
  the same degeneracy bar is cleared

## 3. Branch table (exhaustive, evaluated in this order)

Let `RISE(P) = dd2_gain(P) > 0`.

1. `D2_DEGENERATE` — the actor Tr_L fails its degeneracy bar, i.e.
   `|dd2_gain(Tr_L)| < bar(Tr_L)`. (Declared live in advance: three of four
   pool-sides tripped the analogous bar at depth 1.)
2. `D2_FALLS` — not `RISE(Tr_L)`.
3. `D2_RISES_EVERYWHERE` — `RISE(Tr_L)` and `RISE(Ti_L)` and `RISE(Ti_R)`.
4. `D2_RISES_SPECIFIC` — `RISE(Tr_L)` and at least one Ti side does not rise.

## 4. Predictions (scored as written, no amendment after measurement)

- **P1** (the card's registered expectation, as written):
  `branch == "D2_RISES_SPECIFIC"`.
- **P2** (the directional primary): `RISE(Tr_L)` is TRUE — d2 rises for the
  pool whose d1 fell 20.2%.
- **P3** (the card's mechanism clause): `share_neg(Tr_L) > 0.50` — the rise is
  carried by sources whose own net in-mass is negative.
- **P4** (the OUT-OF-SELECTION leg): `d2_gain_f4wA(Ti_L) >
  d2_gain_f4wA(Ti_R)`. Depth-1 in-mass gets this L/R ordering WRONG (L208's
  dissociation: Ti_L runs hotter at .1845 vs .1187 while carrying LESS
  depth-1 mass). If depth 2 is the right depth, it fixes the sign on a pool
  nobody selected.
- **P5** (the same membership null as L215): `Q4 Tr pct_two < Ti pct_two`.
- **P6** (the fold-rank leg, DESCRIPTION-scored): Spearman between the four
  pool-sides' relative `dd2` and their stored dynamic fold-change is > 0.

## 5. Registered escape (written in advance)

If `D2_FALLS` — i.e. depth 2 is ALSO anti-predictive — the honest conclusion
is that **no static depth-k account explains this resurrection**, the depth-k
family leaves the draft, and the named next instrument is the LINEARISED GATED
operator at the actual operating point (the L178 class), because the quantity
that differs between a dead pool and a live one is which units are ABOVE
threshold, and no ungated static expansion can see that. This escape
SHORT-CIRCUITS: no mechanism claim is made from `share_neg` in that case
(L222's law — a registered escape must change control flow, not merely be
documented).

## 6. Limits (written in advance)

- Everything is a uniform-X expansion: `net_in` is the depth-1 drive onto a
  source under the assumption every unit is at unit activity. The real system
  is relu-gated and sparse (L208: 16.8% active), so `d2` is an ANATOMICAL
  two-hop quantity, not the operating-point two-hop gain.
- `ret2` mixes the floor with the small node-set change (cutwA drops
  `ng_desc[:24]`, f4wA drops `ng4[:20]`); the node-matched eligible comparator
  is inherited from the slice and reported beside it.
- `D2_RISES_SPECIFIC` and `D2_RISES_EVERYWHERE` are both reachable; `P1` and
  the 0e analysis are in deliberate tension and that tension is the point.
- n = 4 pool-sides: every cross-pool rank statistic has a 1/24 resolution
  floor and is DESCRIPTION.
