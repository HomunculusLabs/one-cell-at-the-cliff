# L222 PREREG — the BILATERAL BREAK: synapse-floor artifact, or real?

Written BEFORE the generated script existed and BEFORE any L222 number was
measured. Static, zero rollouts, zero settles, zero seeds (the only RNG in the
inherited pipeline is CERT-MV's probe vector, seed 21200, inherited verbatim).

Tick 253, 2026-11-23, hour 11 at wakeup = build tick.

## The claim under test (L212, stored in l212/static.json)

The v783 DNp33 pair is ASYMMETRIC where BANC's was symmetric:

- carrier (left, root 720575940604103084): R 1.6001329420295532e-06,
  pct **0.020**, rank 3 of 100, P1 **0.0**, P2 12.648220345819931,
  m_out 25.88201175203073
- mirror (right, root 720575940633165452): R 1.0027621125362924e-05,
  pct **0.250**, rank 26 of 100, P1 **0.6931471805599453**
  (= log1p(1) = EXACTLY ONE collapsed-pair synapse onto the motor readout),
  P2 68.28868545807632, m_out 22.29849281357462

Registered gap, the card's own definition: `gap = |mirror_pct - carrier_pct|`.
At no floor (the L212 state) gap_1 = |0.250 - 0.020| = **0.230**.

A one-synapse edge sits at the proofreading/detection floor, and v783 carries
NO synapse floor at all, so the question is whether the break is anatomy or
instrument.

## Premise corrections (written before measuring; each changes what is askable)

**(0a) THE FLOOR IS APPLIED TO THE COLLAPSED PAIR, NOT TO PER-NEUROPIL ROWS.**
l212_head collapses 16,847,997 feather rows into 15,091,983 unique (pre,post)
pairs by SUMMING syn_count (the BANC pair rule), so ~1.76M rows are the same
pair seen in a second neuropil. The floor registered here is `w_syn >= F` on
the SUMMED pair weight — the same object BANC's f4 floor acts on. Consequence
for the headline: the mirror's "exactly one synapse" is one synapse TOTAL
across all neuropils, not one per neuropil, which is the reading that makes
"at the detection floor" correct. A per-row floor is a DIFFERENT operation and
is explicitly NOT performed.

**(0b) THE REGISTERED GAP IS A DIFFERENCE OF PERCENTILES AGAINST TWO
DIFFERENT COHORTS.** `matched_cohort` selects the k=100 v783 descending cells
NEAREST THE ACTOR in log out-mass, so carrier_pct is scored against COH_C and
mirror_pct against COH_M (l212 reports cohort_union_n 122, i.e. the two
cohorts overlap but are not equal). A floor changes `om` for every cell, so it
relocates BOTH cohorts as well as the actors. `gap` is therefore not a
within-distribution contrast, and a change in it can come from cohort
RELOCATION rather than from the actors. The branch stays on the card's
definition, and these cohort-free / cohort-COMMON companions are registered
alongside it, to be read BEFORE the branch is called (the L223 rho-first rule,
the L213 "a conditional gate must inherit the prior claim's null" lesson):

- cohort-free: `ratio_R = mirror_R / carrier_R` (at no floor = 6.2680) and
  `ratio_P2 = mirror_P2 / carrier_P2` (at no floor = 5.3990). These need no
  cohort at all and are invariant to the lam1 normalisation (L209's no-op law,
  since both actors share lam1 at a given floor — their m_out differ, so
  ratio_R is NOT a pure mass ratio).
- cohort-COMMON: both actors scored against ONE cohort — the UNION
  COH_C ∪ COH_M, and separately against COH_C alone — so
  `gap_common = |mirror_pct_common - carrier_pct_common|` is a genuine
  within-distribution contrast.

**(0c) A GLOBAL FLOOR CONFOUNDS TWO MECHANISMS, SO A LOCAL FLOOR IS
REGISTERED AS ITS CONTROL.** The card's floor is global ("built by the SAME
l212_head expression"), which simultaneously (i) deletes the sub-threshold
edges INTO the readout and (ii) rewrites lam1, every cell's out-mass, and the
cohort. A floor applied ONLY to edges whose DESTINATION is in the 110-cell
motor readout isolates (i) while holding om, lam1 and the cohort fixed at
their unfloored values. Registered as declared leg (e) LOCAL-FLOOR,
descriptive, NO branch depends on it.

**(0d) `floor = 1` IS PROVABLY A NO-OP, which is what makes the floored
builder gateable.** Gated in-run by asserting `w_syn.min() >= 1`, so the
floor-1 mask is all-True and the generic floored builder must reproduce the
verbatim `build_v783` at EXACT array equality (CERT-FLOORGEN) and the whole
l212 result table at FLOAT equality (CERT-212) before any floored number is
read.

## Registered legs

**(a) ANATOMICAL (card-required).** For BOTH actors, the complete per-target
edge table into the 110-cell motor readout: motor cell gi + root_id +
cell_type + nerve + side + collapsed syn_count + log1p weight, at every floor.
Plus the DEPTH-1 arrival P1 per actor per floor, per nerve pool.

**(b) THE REGISTERED GAP (primary).** `gap_F` for F in {1, 2, 4} on the
GLOBAL floor, carrier_pct and mirror_pct reported separately at every floor,
so floor-sensitivity of the L212 PRIMARY number is visible on its own.

**(c) COHORT-FREE + COHORT-COMMON companions** per 0b, at every floor.

**(d) SUBSTRATE REPORT (card-required).** For each floor: surviving pair
count, retention fraction vs 15,091,983, lam1 + its power-iteration relative
spread, both actors' om, cohort identity Jaccard vs the floor-1 cohort.

**(e) LOCAL-FLOOR control** per 0c, at F in {2, 4}.

**(f) BETA_L = 1.0 robustness** at the branch floor F=4 only (l212's Q3
pattern), reported, no branch.

## Registered branch table (the card's, verbatim)

Read on `gap_4` = the GLOBAL syn>=4 floor:

- **F_ARTIFACT** — gap_4 < 0.10
- **F_SURVIVES** — gap_4 >= 0.15
- **F_MIXED** — 0.10 <= gap_4 < 0.15

Degenerate escapes registered in advance (they pre-empt the branch):

- **F_DEGENERATE_ACTOR** — either actor has om == 0 at F=4 (nothing to score).
- **F_DEGENERATE_COHORT** — `matched_cohort` cannot fill k=100 at F=4, or the
  cohort's zero-R fraction exceeds 0.50 (l212's own V_DEGENERATE bar).
- **F_DEGENERATE_POWER** — power-iteration relative spread >= 1e-6 at any
  floor; bar inherited from l212, and per L216 it is the operator's OWN
  measured convergence that licenses it (floor-1 measured 4.1e-16).

## Predictions (registered; scored as stated)

- **Q222-1** branch = **F_SURVIVES**. Reasoning: the percentile is carried by
  P2 (depth-2 mass, 68.3 vs 12.6 = 5.4x), and a single direct synapse
  contributes to P2 only through motor->motor edges, which are few. The 5.4x
  is a statement about where the mirror's depth-1 TARGETS sit, not about the
  one-synapse edge itself.
- **Q222-2** carrier P1 == 0.0 exactly, on all three global floors and both
  local floors (card-required assert; it has no direct motor edge to lose, and
  floors only remove edges).
- **Q222-3** mirror P1 == 0.0 exactly at F=2. FALSIFIABLE AND SHARP: if
  mirror P1 > 0 at F=2 then it carries additional direct motor edges with
  syn>=2 and L212's "exactly one synapse" reading was incomplete rather than
  wrong.
- **Q222-4** |carrier_pct_4 - 0.020| <= 0.10 (the L212 primary number is
  floor-insensitive).
- **Q222-5** ratio_R stays > 2.0 at F=4 (the cohort-free currency keeps the
  break).
- **Q222-6** carrier cohort identity Jaccard(F=4 vs F=1) < 0.80 — the floor
  RELOCATES the cohort, so any gap movement must be read against 0b. (l212's
  BETA_L=1 leg already measured 0.709 for a much gentler perturbation.)

## Verification plan (halting gates, before any L222 number is read)

- **CERT-783 + CERT-L207** re-run VERBATIM by inheriting l212_head.py whole as
  a sha-pinned literal PREFIX (ids array-equal, N 139255, live nnz, meta pins,
  DN 1303 / motor 110, both match ids present, DNp33 left/right).
- **CERT-212 (HALTING)** — every stored value in l212/static.json's
  Q1_primary, Q2_secondary_descriptive and Q3_robust_beta1 reproduced at FLOAT
  equality from this run's own floor-1 rebuild, plus lam1 552.6340796478873
  and the rescale no-op. l212/static.json opened READ-ONLY with (size,
  mtime_ns) fingerprinted before and asserted unchanged after (L175: a lab
  script is never imported).
- **CERT-FLOORGEN (HALTING)** — the generic floored builder at F=1 is EXACTLY
  array-equal to the verbatim `build_v783` on jv / rows / cols / om, with
  identical n_edges and pool_l (the L207 CERT-GEN pattern).
- **CERT-MV / CERT-GATE** inherited: the bincount kernel asserted array-equal
  to the verbatim `np.add.at` kernel, and reach_fast / power_iter_fast / Rfast
  asserted float-equal to the verbatim `reach_sub` / `power_iter_sub` / `Rstat`
  slices — re-run at EVERY floor, not only at floor 1.
- **CERT-MONOTONE (HALTING)** — the floored edge sets are strictly NESTED
  (F=4 subset of F=2 subset of F=1) asserted on the surviving index arrays,
  and om is asserted monotone non-increasing in F for every one of the 139,255
  cells. A floor that is not nested is not a floor.
- Builder asserts the three inherited l207_tail slice shas (fce1e71189eb1ed7,
  340c0432c85c6e7b, f4585bcc52f7ab0a) AND the l212_head.py whole-file sha, runs
  the forbidden-token audit, and asserts the tail re-transcribes none of the
  inherited function bodies.
- md5sum -c GREEN against l222/prior.md5 before the run.

## Declared limits (inherited + new)

- EXPLORATORY, inheriting every L212 limitation verbatim (changed readout,
  changed volume, changed body segment; a DN's real output leaves this volume;
  mass-matched cohort percentile is NOT the l169c degree-neutral rewire null;
  v783 'unknown' top_nt scored at magnitude 0.3).
- v783's cohort mass match is LOOSE (log-spread 0.316 / 0.349 vs the 0.15 bar
  l212 registered and failed) — carried forward as a stated limit, and it is
  exactly why the cohort-free currency is registered.
- A floor is not a model of proofreading error; it is a monotone deletion of
  weak edges. "Artifact" here means "the contrast does not survive deletion of
  edges at the detection floor", never "the edge is false".
- No live change, no draft edit, sessions/ untouched.
