# L208 VERDICT — the less-saturated-side hypothesis

Tick 237, 2026-11-22. PREREG `l208/PREREG.md` written first. ZERO new
rollouts: 10,240 stored pool-mean traces read from `l169b2/raw_l169b2.npz`
(B36, seeds 3449-3464) and `l175f/raw_l175f.npz` (B37, 3701-3716),
read-only, fingerprints asserted unchanged after the run.

## Registered branch: H_UNREGISTERED_SHAPE

On the Ti primary, B36 has **no** arm significant in either tail; B37 has
**one** in the lower tail (`cutng25` rho −.524, p_dn .0229). That is not
H3_NULL_BAND (a hit exists), not H2_INVERTED (only one batch), not
H4_SPLIT (no opposite-sign significance) — the deliberate catch-all fires.
H0_VOID did **not** fire: median |marginL − marginR| over the Ti arms is
0.0652 (bar 0.005), so the sides' operating levels genuinely differ and the
hypothesis was testable.

## The result is the between-arm leg, and it refutes by SIGN

The Ti margin side is **R on all five arms, in both batches** (dM = marginL
− marginR is −.055 to −.109 everywhere, matched to <.005 across batches per
arm), while stored side-dominance is **L** on the three floored arms and
**R** on the two base arms. Agreement 2/5, identically in B36 and B37.

So the explanatory variable is **floor-INVARIANT** while the thing it must
explain **FLIPS**. The dominance flip cannot be a saturation-margin effect,
and this is stronger evidence than a null would have been: on the floored
arms the dominant side is the one with LESS margin (higher level), the
exact opposite of the hypothesis.

Dissociation worth recording: L205 measured the left Ti pools as having 18%
LESS per-cell in-mass, yet they run **hotter** dynamically on every arm
(e.g. f4wA lvl .1845 L vs .1187 R). Static drive does not predict dynamic
level, even in sign.

## The ceiling leg is VACUOUS-BY-SUBSTRATE, measured not assumed

`fhi95 = fhi90 = 0.00000` in all 20 arm x pair x batch cells, and the
largest pool-mean reached anywhere in 60 s is **pmax 0.7744** (B37 Ti f4ng
left). At an ~11%-active operating point the pool mean never approaches
RMAX = 1.0, so "distance from the ceiling" carries no information about
being near a ceiling — it is simply "low level". That is why the registered
currency was the wrong one (see the method lesson).

## POST-HOC floor leg (`l208/addendum_floor.json`) — the live nonlinearity

`flo` (fraction of the window at or below BG = 0.02) was a REGISTERED
measurement but no test on it was registered, so everything here carries
no registered claim; the registered version is queue item **L214**.

Re-scored in the floor currency (A = floR − floL = how much less
floor-pinned the LEFT side is), sign agreement with side dominance is
**8/10 (B36) and 9/10 (B37)** arm x pair cells, against 2/5 for the ceiling
margin on Ti. Within-seed Spearman is positive in 7/10 and 8/10 cells, and
one cell **replicates**: `Tr|f4ng` rho **+.759 (p .0007)** and **+.912
(p .0008)** — the same cell that read −.691 / −.909 in the margin currency.
Same data, two currencies, opposite verdicts.

Mechanism sketch, descriptive: the left trochanter pools are essentially
**dead** on the base arms (flo_L .996 / 1.000, lvl .0002 / .0000 on cutwA /
cutng25) and **alive** on the floored arms (flo_L .562-.660, lvl .022-.026).
The syn>=4 floor resurrects them — consistent with L205's C4 mechanism leg,
which found Tr's edge-retention ratio INVERTS (1.0137 L / 1.0074 R, the
floor strips relatively less from the left Tr).

One honest exception: `Ti|f4wA` — the carrier-intact floored arm that is the
headline L175 phenotype — disagrees in BOTH batches (left Ti is more
floor-pinned AND dominant). Its left-dominance is explained by neither
currency.

## Measurement-capability limit (registered before measuring)

Stored traces are **pool MEANS** (`tr[a][kk][k] = X[a][POOLS[a][kk]].mean()`),
so the fraction of CELLS at the ceiling is not recoverable from stored data
and was never substituted for. Everything above is a pool-mean statistic.

## Disclosures

1. The drive is pulsed (500-on / 400-off inside each 0.7-Hz segment), so the
   primary margin is a mixture over tone-on and tone-off phases. The
   declared tone-on companion `rho_on` differs materially in several cells
   (B37|Ti|f4wA +.062 -> −.535), reported, not used for any branch.
2. Multiplicity: 20 cells x 2 tails at bar .05 expects ~1 hit per tail per
   batch; single significant cells are reported as such, and only `Tr|f4ng`
   (both batches, both currencies, p <= .011) survives replication.
3. The Tr leg is the registered SECOND leg; the branch is called on Ti only.
4. Anatomical side convention and pool membership are inherited from the
   stored runs, not re-derived.

## Predictions: 3 of 4

- Q208-1 **WRONG** (registered H3_NULL_BAND; measured H_UNREGISTERED_SHAPE).
- Q208-2 **CORRECT** — margin sign does not flip with the floor (one
  distinct value across all five arms), so it cannot explain the flip.
- Q208-3 **CORRECT** — fhi95 ~ 0 everywhere; the ceiling leg is
  uninformative and the margin leg is carried entirely by `lvl`.
- Q208-4 **CORRECT** — `flo` is nonzero and strongly side-asymmetric
  (up to 1.000 vs .304).

## Method lesson (now in the skill)

At a SPARSE operating point, "saturation margin" and "aliveness" are the
SAME number with OPPOSITE meanings: margin-from-ceiling = RMAX − lvl, and a
low lvl in a relu network means DEAD, not roomy. Measure which nonlinearity
the system is actually near (pmax, fhi) BEFORE choosing a currency — here
pmax never exceeded .774 and fhi90 was identically 0, so the registered
currency was sign-inverted relative to the informative one, and the same
stored traces supported opposite within-seed verdicts in the two framings.

## Verification

- Head = `l169b2_verdict.py` lines 13-63 **byte-for-byte**, sha256
  `de636f4a18ee789b` (51 lines), asserted a literal slice of the source,
  forbidden-token audited (no `savez` / `open(` / `json.dump` /
  `write_text` / `os.replace` / `pickle`); **no lab module imported** (L175).
- **CERT-ADD halting gate**: 109 stored B36 values reproduced EXACTLY
  before any L208 number was read — meanL/kL/meanR/kR for all five arms,
  all 16 per-seed L duties per arm, and the three stored `paired_legs`
  (`mean_paired_dL`, `n_up`, `n_down`).
- **CERT-175F halting gate**: 180 stored B37 values reproduced EXACTLY
  (five arms x 4 summary fields, plus all per-seed L and R arrays).
- **CERT-CONST**: every dynamics constant asserted against the run script's
  own source literals; AMPA rebuilt from its own construction; |W| asserted
  = 3000 and |W_on| = 1400.
- Both npz opened read-only; size + mtime_ns fingerprinted before and
  asserted unchanged after, in both the primary and the addendum run.
- The addendum re-ran CERT-ADD (100 values) and asserted its head sha
  matches the one stored in `l208/static.json`.

Artifacts: `l208/{PREREG.md, static.json, addendum_floor.json, VERDICT.md,
run.out, run.err, add.out, add.err}`; code `l208_{build,tail}.py` ->
generated `l208_static.py`, `l208_{build_add,add_tail}.py` ->
generated `l208_addendum.py`.
