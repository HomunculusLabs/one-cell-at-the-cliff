# L104 PREREG — brain-state-intent smoke probe (descriptive, read-only)

Written 2026-11-22 00:4x EST, tick 226, BEFORE any separation statistic was
computed. The only numbers read first are the STATIC CENSUS below (dataset
shape + label/hour contingency), which is what this registration is derived
from (L44 rule: derive the gate from the stored artifact, not from the card
sentence).

## Card

L104 (ideas 51): "once the L102 archive holds >= 50 (brain-state, intent)
pairs: first descriptive probe — read the v783 CX + DN populations
(senses.dn index sets) from archived X, test whether intent separates from
population activity beyond a shuffle null. Read-only, offline; the answer
sizes the future decode card."

Condition MET: loader reports 73 pairs / 73 with intent / 73 unique brains,
74.6 MB, zero pruned references.

## Static census (read BEFORE registration, hence not a result)

- Window 2026-11-16T08:16 -> 2026-11-21T21:09 EST, 73 snapshots, median
  inter-snapshot gap 1.47 h (min 0.02, max 5.25).
- Intent: stay 32, settle 29, to_fence 8, parade 2, to_boot 1, to_pond 1.
- Label sequence is strongly AUTOCORRELATED: 31 runs over 73 samples,
  longest run 8, lag-1 label agreement .583. These are NOT iid samples;
  they are one duck's time series.
- Hour-of-day (EST) contingency:
  - stay    hours 0..14 (max 14)
  - settle  hours 14..23 plus ONE sample at hour 0
  - to_fence hours 1,2,3,7,7,9,11,12  <- entirely INSIDE the stay range
- Therefore stay-vs-settle is a near-deterministic function of circadian
  phase at this sampling, and stay-vs-to_fence is the hour-OVERLAPPING
  contrast where clock phase cannot carry the label.

## Mechanism known in advance (why the naive cell cannot be the claim)

Our own live model drives the CX population TONICALLY with darkness (sleep
follows the sun; skill lesson "Circadian/tonic drives are body-state"). The
intent the world tick emits is itself gated by the sleep axis. So a positive
"CX separates stay from settle" is predicted BY CONSTRUCTION from the clock,
not from a locomotor code. Registering this now so a confounded positive
cannot be reported as a decode result.

## Populations

From senses.py index sets, joined to brain_graph.pt ids: CX, DN_all,
DN_left, DN_right, plus KC and DAN as non-motor comparators, plus
size-matched RANDOM index sets (5 draws per target size, seed 104) as the
specificity control (L139/L169 twin discipline: a population claim needs a
mass/size-matched twin).

## Statistics

- PRIMARY (1-D, assumption-light): population MEAN activity over the
  snapshot's X vector -> AUC (Mann-Whitney) between the two classes of a
  contrast. Reported as |AUC-.5| for null comparison, AUC for direction.
- SECONDARY (multivariate): leave-one-out nearest-centroid, cosine distance,
  on the population subvector -> accuracy vs majority-class baseline.

## Nulls

- N1 IID LABEL SHUFFLE (the card's literal ask): 2000 permutations of the
  contrast's labels, seed 104. p1 = (#{|AUC_perm-.5| >= |AUC_obs-.5|}+1)/2001.
- N2 CIRCULAR-SHIFT NULL (the honest null for a time series): shift the
  73-long label sequence circularly by k=1..72, re-select the samples whose
  SHIFTED label is in the contrast, recompute AUC. Preserves both label
  autocorrelation and X autocorrelation. p2 = (#{|AUC_shift-.5| >=
  |AUC_obs-.5|}+1)/73.
- N3 CLOCK BASELINE: AUC of hour-of-day alone as the score, and AUC of
  snapshot order index alone (drift detector). These are not nulls on the
  brain; they bound how much of the separation the clock already owns.

## Gate cells — ONE OBJECT PER CELL (L109 rule)

- C1 NAIVE (object: stay-vs-settle, iid null). PASS if CX |AUC-.5| >= .20
  and p1 < .05. Explicitly labelled CONFOUNDED: a pass here is not evidence
  of an intent code.
- C2 TEMPORAL (object: stay-vs-settle, autocorrelation-preserving null).
  PASS if p2 < .05. A C1 pass with a C2 fail means the naive null
  over-certified and must be reported as such.
- C3 DISSOCIATION (object: stay-vs-to_fence, the hour-overlapping contrast).
  PASS if CX or DN |AUC-.5| >= .20 with p1 < .05. This is the LOAD-BEARING
  cell: only this contrast can carry an intent claim.
- C4 SPECIFICITY (object: population identity). PASS if the named
  population's |AUC-.5| exceeds the MAX over its 5 size-matched random
  draws on the same contrast. A fail means separation is bulk/global drive,
  not population-specific.

No branch word is formed by ANDing cells across objects; each cell is
reported with its own object named.

## Registered predictions

- P1: C1 PASSES and is confounded (CX AUC >= .85 on stay-vs-settle).
- P2: the clock baseline N3 hour-of-day reaches |AUC-.5| >= .45 on
  stay-vs-settle, i.e. hour alone nearly saturates the contrast.
- P3: C3 FAILS or is unreadable at n=8 vs 32 -> the archive as currently
  sampled cannot size the decode card; the finding is a SAMPLING
  prescription, not a decode result.
- P4: C4 FAILS on stay-vs-settle (random size-matched populations separate
  nearly as well as CX), because our own null-duck verdict says global
  drive/mood chemistry is BULK-path while only KC/DAN-class structure is
  wiring-faithful.
- P5: DN_left vs DN_right mean activity carries NO readable side asymmetry
  for the directed intents (to_fence/to_boot/to_pond) at these n; reported
  descriptively only, no gate.

## Branches

- B_CONFOUND_ONLY: C1 pass, C3 fail -> the dataset separates circadian
  phase, not intent; card ships as a sampling prescription.
- B_INTENT_CODE: C3 pass with C4 pass -> a genuine population-specific
  intent signal survives the hour-matched contrast; sizes a decode card.
- B_BULK: C3 pass with C4 fail -> separation real but not population
  specific; decode card must use a learned readout over the whole state,
  not a named population.
- B_DEAD: C1 fail -> probe is underpowered; report n needed.

## Scope / discipline

Read-only. No live service touched, sessions/ never mutated (archive copies
only), paper/DRAFT.md untouched, zero rollouts, zero graph build, CPU only.
All RNG seeded (104). Artifacts under lane/l104/.

---

# ADDENDUM 1 (written 2026-11-22 01:0x, AFTER the first probe exit, BEFORE
# the addendum measurements — two instrument defects found in my own run)

## A1. The clock baseline N3 is INVALID as written (circular variable, linear
instrument). `hour` AUC came out .517 on stay-vs-settle, which looks like
"the clock does not own the contrast" and is the opposite of the truth: the
static census in this PREREG was itself computed with a spurious -5 h shift
(captured_at already carries -05:00, so `t.hour` IS local EST). The real
contingency is stay = local hours ~05-19 (day), settle = local ~19-04
(night) — settle STRADDLES MIDNIGHT, so its hour values are both the
largest and the smallest in the sample and a rank/linear AUC collapses to
.5 by construction. This is the L108 class (an inherited band/instrument
that is a ratio instrument, not a location instrument) one level down: a
linear statistic on a circular coordinate.
REPLACEMENT, registered now: (i) the best ARC classifier — over all
(start, width) arcs on the 24 h circle at 0.5 h resolution, the maximum
accuracy of "hour in arc => settle"; (ii) AUC on circular distance from
midnight, min(h, 24-h). Both are CLOCK baselines, not brain reads.
- A-P1: the arc classifier reaches >= 95% accuracy on stay-vs-settle.

## A2. Every population, including the size-matched RANDOM controls,
separates stay-vs-settle at AUC ~.998. That is the signature of a GLOBAL
ACTIVITY LEVEL shift, not of any population. Two instruments added:
(i) WHOLE-BRAIN mean activity AUC as the bulk reference;
(ii) a GLOBAL-NORMALISED per-population read, pop_mean / whole_brain_mean,
     with the identical N1/N2 nulls — this is the honest population-
     specificity instrument, and it is what C4 should have used on a
     substrate whose global level moves.
- A-P2: whole-brain mean AUC >= .99 on stay-vs-settle (pure level shift).
- A-P3: after global normalisation CX RETAINS |AUC-.5| >= .20 on
  stay-vs-settle (CX being the darkness-driven clock population). If the
  normalised read dies for CX too, the stronger statement follows: at this
  sampling the archive carries circadian LEVEL and nothing population-
  specific, which is a sharper sampling prescription for the decode card.
- C4 is RE-READ on the normalised instrument; the raw-mean C4 result stands
  as reported (it fails, and the failure is explained by the level shift).

No gate cell is loosened and no branch word changes: C3 (the hour-
overlapping dissociation contrast) already failed on the raw instrument and
is re-read on the normalised one for completeness.
