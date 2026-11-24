# L213 VERDICT — TYPE or CLASS? The class gap is MASS, and so was my conditional

Branches as registered: **Q1 = T_TYPE_LOW** / **Q2 = C_CLASS_TYPICAL** /
**Q3 = D_CLASS_EXPLAINS** → derived reading **MIXTURE**.
Predictions **3 of 5**. Static, zero rollouts, 18.8 s (+16.1 s addendum), CPU.
PREREG: `l213/PREREG.md` (registered first, including the premise correction).
Artifacts: `l213/{PREREG.md, static.json, addendum.json, VERDICT.md, run.out,
run.err, addendum.out, addendum.err}`.
Code: `l213_{build,tail}.py` → generated `l213_static.py`;
`l213b_{build,tail}.py` → generated `l213_addendum.py`; `l213_scope.py`.

## Premise correction, registered before any measurement

`l213_scope.py` found that **the carrier (gi 1110, DNp33-L) is `pure_proj`
and its contralateral homolog (gi 928, DNp33-R) is NOT** — the mirror has a
cord→DN edge, so `dn_into` is True. The two cells L207 found avoiding at
pct .06-.10 sit in DIFFERENT classes under the very flag hypothesis (ii)
proposes as the explanation. Written into the PREREG before any aggregate,
and it is why Q3 was registered as a per-actor, within-OWN-class conditional
rather than one pooled "within pure_proj" number.

## Headline

Population: every present descending cell with `m_out > 0` on the three L207
substrates — **1288 / 1264 / 1260** cells, **426 / 411 / 409** `cell_type`s
with ≥ 2 present members, **560 / 536 / 535** `pure_proj`.

**Q1 TYPE — the type median is LOW once mass is held.** DNp33's 2-member
type median R is 2.759e-05 / 2.759e-05 / 3.337e-05. Against 2000
within-mass-stratum type-label permutations (10 equal-count strata, per-
stratum counts asserted exact on every draw) the null median is
4.11e-04 / 4.45e-04 / 4.80e-04 and the real value sits at null percentile
**0.0145 / 0.0105 / 0.0130** → `T_TYPE_LOW` on all three. Raw, the same type
median is only at the **13.1 / 14.1 / 16.9th percentile** of the 409-426 type
medians — so conditioning on mass is what makes it extreme, by roughly a
factor of ten in percentile.

**Q2 CLASS — a 4x raw class gap that is ENTIRELY mass composition.**
`pure_proj` medians are 3.7-4.1x BELOW non-`pure_proj`
(ratio 0.273 / 0.248 / 0.241, dlog10 −0.564 / −0.605 / −0.618). Permuting the
flag within the same mass strata puts that difference at null percentile
**0.166 / 0.228 / 0.170** → `C_CLASS_TYPICAL` on all three. The reason is in
the addendum: median out-mass is **37.6 vs 139.2** (pure vs non-pure) on the
closure, a 3.7x mass gap producing the 3.7x R gap. **A large raw class
difference, null-corrected to nothing.**

**Q3 CONDITIONAL — fired `D_CLASS_EXPLAINS`, and the instrument is why.**
Raw within-class percentiles: carrier **0.318 / 0.336 / 0.407** inside
`pure_proj`, mirror **0.144 / 0.152 / 0.153** inside non-`pure_proj`. Both
above the registered 0.10 bar on all three substrates, so the branch reads
`D_CLASS_EXPLAINS` and the derived reading is `MIXTURE`. That is what I
registered and it is reported as measured.

## The addendum (UNREGISTERED, post hoc, descriptive) — and it reconciles them

Q1 and Q3 are not two readings of the cell; they are two nulls, and the
PREREG said in advance that Q3's is not mass-matched. One quantity decides
which applies — where the actors sit in their own class's MASS distribution:

- **The carrier is at mass percentile 0.921 / 0.963 / 0.978 inside
  `pure_proj`** — very nearly the heaviest pure-projecting descending cell
  there is. The mirror is at 0.654 / 0.655 / 0.692 inside non-`pure_proj`.
- **R still rises with out-mass despite being divided by it**:
  Spearman(R, m_out) = **+0.532 / +0.538 / +0.545** population-wide,
  +0.51 / +0.50 / +0.53 within `pure_proj`, +0.41 / +0.42 / +0.43 within
  non-`pure_proj`. P2 grows faster than linearly in out-mass (more out-edges
  = more second-hop opportunities), so the per-mass normalisation does NOT
  make the statistic mass-neutral.
- Re-read the within-class percentile on the **100 nearest class members in
  log out-mass** and it collapses to the L207 range:
  carrier **0.050 / 0.080 / 0.090** (9.39x / 9.48x / 6.95x deficit,
  log-mass spread 0.530 / 0.643 / 0.667), mirror **0.070 / 0.070 / 0.060**
  (19.61x / 19.72x / 20.12x, spread 0.138 / 0.138 / 0.120).

So **L207's numbers reproduce WITHIN each actor's own class** once the class
cohort is mass-matched, and the mirror's ~20x reproduces L207's "~20x" almost
exactly. The class explains nothing — Q2 says the class carries no
null-corrected shift at all, and there is nothing for a null class to
explain.

## What this card actually settles

- Against (ii): the `pure_proj` class is **not** a low-R class once mass is
  held, and the carrier is not extreme-by-virtue-of-membership — it is
  extreme among its own mass peers, inside the class and out of it.
- For (i): the DNp33 **type** median is low at null pct ~0.013 under a
  type-level, mass-stratified label permutation — the type-level null the
  card asked for, which L207 never had.
- Honest ceiling: with 2 present members the type median is a **2-point
  statistic**. The direction replicates on three substrates with a proper
  type-level null; no magnitude is claimed from it.
- The registered branch table says `MIXTURE`. The post-hoc reconciliation
  says `TYPE`. Both are in this verdict, labelled, and the branch is not
  retro-fitted.

## METHOD LESSON (self-inflicted, and the most transportable thing here)

**A conditional gate meant to adjudicate a prior claim must inherit the
prior claim's null, not a simpler convenient one.** L207's claim was made
against a MASS-MATCHED cohort. I registered Q3 against a RAW within-class
percentile, disclosed that it was a different null — and then let it carry a
branch anyway. It fired `D_CLASS_EXPLAINS` purely because the carrier is a
92nd-98th-percentile-mass cell being compared to a class whose bulk is
lighter. The disclosure was not a substitute for the right instrument: a
branch on a weaker null is a branch that can answer the wrong question.
Same family as L207's resolution lesson and L211's share-band lesson.

Second, narrower: **a per-unit normalisation does not make a statistic
scale-neutral.** R is explicitly divided by `m_out` and still correlates
+0.53 with it. Measure the residual rho before using a normalised statistic
to compare cells of different size.

## Predictions, scored

| id | registered | measured | ok |
|---|---|---|---|
| P1 | Q1 = T_TYPE_LOW on ≥ 2 of 3 | all three | ✓ |
| P2 | Q2 = C_CLASS_TYPICAL | all three | ✓ |
| P3 | Q3 = D_TYPE_SURVIVES on all 3 | D_CLASS_EXPLAINS on all 3 | ✗ |
| P4 | mirror within-class pct ≤ 0.10 on all 3 | .144 / .152 / .153 | ✗ |
| P5 | type-median null pct ≤ 0.02 on ≥ 2 of 3 | .0145 / .0105 / .0130 | ✓ |

P3 and P4 failed for the SAME reason — the raw within-class null — and the
addendum shows both would have passed under a mass-matched one (.05-.09 and
.06-.07). Scored false as registered; the registration is not amended.

## Verification

- **CERT-SRC**: generated from six verbatim sha256-asserted slices
  (l151_static.py 1-319 `e6245e8306dc8a0f`, l178_tail.py 7-149
  `6e2e8fa4bd19eced`, l206_mid.py `febbc390ad4f`, l206_tail.py 22-121
  `29a830839ebc7837`, l207_tail.py 48-112 `946dab653fe60b16` = `build_sub` /
  `reach_sub` / `power_iter_sub`, l207_tail.py 199-241 `340c0432c85c6e7b` =
  `Rstat` / `pct_of` / `rankvec` / `spearman_l`), every inherited sha
  asserted against the value L210/L211/L212 recorded, forbidden-token
  audited, boundary anchors asserted, and the tail asserted NOT to
  re-transcribe any certified function. No lab module imported (L175).
  So CERT-F4, the three stored gains at float equality, the CSR orientation,
  all 20 pool sizes and **CERT-178's 420 stored values at FLOAT EQUALITY**
  re-ran as free certification before any L213 value was read.
  Generated sha256 `7131bfef8d6e4ac8`.
- **CERT-207 (HALTING), 522 checks at FLOAT EQUALITY**: every stored
  `R`/`R1`/`P2`/`m_out` of all 127 present ladder cells across the three
  substrates (58+34+35), both slot comparators (gi 80 closure slot 21,
  gi 32072 f4wA slot 25), and L207's stored Q2 mirror/carrier R and m_out
  per substrate — all reproduced by the verbatim `Rstat`/`reach_sub` path
  BEFORE any type or class aggregate was read. `l207/static.json` opened
  READ-ONLY with (size, mtime_ns) fingerprinted before and asserted
  unchanged after; L207's verdict strings asserted.
- **CERT-T, 272 checks**: the fast census kernel (two transposed matvecs give
  P1 and P2 for ALL 1288 sources at once, the same `np.add.at` expression
  with rows/cols swapped — the L210/CERT-MV transpose identity) is GATED,
  never trusted: max relative difference vs verbatim `reach_sub`
  **9.05e-16** against a 1e-12 bar on both actors and all 127 ladder cells.
  Float equality deliberately NOT claimed (the summation ORDER differs —
  L206's expression law).
- Per-stratum count vector asserted EXACT on **every one of 12,000 draws**
  (2000 × 3 substrates × 2 nulls); the Q2 null additionally asserts the
  pure_proj count invariant per draw.
- Premise asserts halting: carrier `pure_proj` True, mirror False, mirror
  `dn_into` and `dn_proj` both True, both actors' `cell_type == "DNp33"`.
- Substrate pins: n/edges 21809/647953, 21785/644177, 21789/469618; three
  power iterations converged (rel spread 1.25e-16 / 1.25e-16 / 1.42e-16);
  pool sizes invariant with zero overlap (inherited `build_sub` asserts).
- **Addendum isolation**: `l213_addendum.py` is generated from the same
  certified stack plus `l213_tail.py` lines **1-221 only** (cut before the
  registered Q blocks and before the parent's `json.dump`), with builder
  asserts that the slice carries CERT-207/CERT-T/the premise and does NOT
  contain `Q1_type`/`Q2_class`/`Q3_conditional`/`json.dump(o`, that the tail
  never opens `l213/static.json`, and that it writes `l213/addendum.json`
  only. Verified after the run: `md5sum -c` on `l213/static.json` **OK** —
  the parent artifact is byte-identical (L175).
- Writes `l213/static.json` and `l213/addendum.json` only. Zero rollouts,
  zero settles, zero dynamics, CPU.

## Limitations

1. DNp33 has 2 present members: the type median is a 2-POINT statistic.
2. One type, one class flag, one statistic. Other descending partitions
   (nerve, neuropil, NT, side) are untested.
3. ANATOMICAL leg only — wiring geometry, not an operating point (L164).
4. The within-stratum permutation holds log-mass stratum and type SIZE but
   not neurotransmitter, side, or neuropil composition.
5. The addendum's mass-matched class cohort is a THIRD null; its magnitude
   transports to neither Q3's raw class nor L207's whole-descending cohort
   (L207 cross-null law).
6. The three substrates share a graph and most cells — not three
   independent replications.
