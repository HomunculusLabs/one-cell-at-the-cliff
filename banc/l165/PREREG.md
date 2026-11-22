# L165 PREREG — "echo-lock dose": the 7-arm PLV_self / evoked scan

Registered 2026-11-22 ~04:15 EST, BEFORE any new measurement. Card: LANE.md
L165 (ideas 85). Zero rollouts, zero RNG, read-only on stored artifacts
(`l150/raw_l150.npz`, `l154/raw_l154.npz`, `l162/addendum3.json`,
`l157/static.json`). Machinery IMPORTED/COPIED VERBATIM from
`l162c_phase.py` (L85 rule).

## PREMISE CORRECTION (written before measuring; L44 + tick-224 class)

The card says the l154 off-arm kicker shows the lock disappears "WITHOUT the
b65 echo", and registers "if echo-specific, b65 >> the cut/sil arms". Reading
the SOURCE (not the summary):

- `l154_run.py` L619-624 + its docstring L3-6: the `off` arm is the b65 graph
  **VERBATIM, same CSR object**, same stored G65=0.14, DNg100 command ON —
  what is removed is the **mechanosensory sinusoid for the entire run
  including settle** (the Sapkal FeCO-deafferentation analog). There is no
  body-echo term in this family at all. "Echo" is a MISNAME on the card: the
  l154 contrast is DRIVE PRESENT vs DRIVE ABSENT.
- `l150_run.py` L885-889 and L917-922: `sin_t` is added to `drive[mech[a]]`
  inside `for a in ARMS` — i.e. **every one of the 7 l150 arms carries the
  identical sinusoid by construction**. The card's registered contrast
  ("b65 >> the cut/sil arms") is therefore VACUOUS-BY-DATASET in the
  direction it was written (L146 class): no l150 arm is a drive-off arm.

So the card's question is re-posed, and this is the registered question:
the l154 off arm already supplies the drive-off pole; the l150 arms supply
**six structural lesions at fixed drive**. The honest test is a SPECIFICITY
test — does the .100 Hz lock track DRIVE PRESENCE, or is it also destroyed by
cutting cells / clamping / dropping motor edges?

## L164 CAVEAT (registered, binding on the write-up)

Tick 228 (L164) established that in this protocol every rollout ends settle at
a fixed drive phase, so PLV_self across seeds is dominated by the EVOKED
(protocol-pinned) component: freeing the onset phase collapsed it .984 → .282.
Consequence registered in advance: **this table is a drive-following /
evoked-locking measure and may NOT be written up as an intrinsic-clock
claim.** Any sentence of the form "arm X has its own clock" is out of scope
for L165 by pre-registration.

## Instruments (verbatim from l162c_phase.py)

WIN 6000, DT 0.01, BIN_FULL 6 (asserted == 0.100 Hz to 1e-12), 20 antagonist
pools + mm + xm = 22 channels, seeds = the 18 stored (801, 901, B33
3365-3380), identical seed list for every arm. PLV_self = |mean exp(i*phase)|
over seeds of the bin-6 FFT phase; evoked fraction = |mean X|^2 / mean|X|^2;
circular sd = degrees(sqrt(-2 ln r)). CARRIER (8) / CONTROL (9) sets
RE-DERIVED from `l157/static.json` by l162c's own rule (wilson_lb >= .5 /
below <= 6), then asserted equal to the stored lists in addendum3.json.

## HALTING anchors (run BEFORE any new arm is read; mismatch = STOP)

- **CERT-6** analytic self-test verbatim: pinned > .999, free < .05.
- **C0A-165**: recomputed PLV_self for arm b65 on l150 must equal all 22
  stored `addendum3.json["plv_self"]["l150/raw_l150.npz|<ch>"]` values to
  float equality (not rounded), and the 22 stored
  `i5_evoked_fraction["l150/raw_l150.npz|b65|<ch>"]` likewise.
- Bin assert + per-arm af range assert (0.01, 0.9) on the stored af scalars.

## Registered branches (one object per gate cell, L109)

- **A_GENERIC_LOCK** (my prediction): all six non-b65 l150 arms have carrier
  median PLV_self >= .80. Verdict sentence: the .100 Hz lock is a
  drive-following property, invariant to every structural lesion in the
  L135-L150 family, and the l154 off arm is the only condition that abolishes
  it. CONSTRUCTIVE-EXPECTED is disclosed as such (L55): the informative
  residue is then (a) the per-arm dephasing MAGNITUDE and (b) whether any
  lesion moves the CONTROL pools.
- **A_LESION_SENSITIVE**: at least one arm has carrier median PLV_self <= .40.
  Name the arm; that lesion abolishes drive-following and becomes a card.
- **A_MIXED**: otherwise; report the ordering, claim nothing stronger.

Secondary, pre-registered bars:

- **S1 pattern invariance**: Spearman rho of the 22-channel PLV_self vector,
  each arm vs b65. Bar rho >= .70 = the lock's CHANNEL PATTERN is
  lesion-invariant, not merely its median.
- **S2 control pools**: CONTROL median PLV_self per arm; registered
  expectation = stays below the carrier median in every arm. A lesion that
  RAISES the control median above .8 is reported as a recruitment event.
- **S3 evoked fraction** must track PLV_self per arm (Spearman over the 22
  channels >= .8 within each arm) — these are two reads of one quantity and
  a divergence means an implementation bug, not a finding.
- **S4 dose read** (the card's word "dose"): arms ordered by removed mass
  (full 0, b65 0, eMotTop5/eMotBot5 5 edges, cutwA .2286, cutng25 .235,
  silW = cutwA graph + 1 clamped unit) vs carrier median PLV_self. Registered
  as DESCRIPTIVE ONLY, n=7 arms is not a dose-response test.

## Scope

No rollouts, no RNG, no graph build, CPU only. No live changes, sessions/
untouched, paper/DRAFT.md untouched (owner-handoff state). Artifacts:
l165/{PREREG.md, results_l165.json, run.out}. Code: l165/l165_scan.py.
