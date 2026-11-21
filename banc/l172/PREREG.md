# PREREG — L172 stage (a): the statistics pass (ZERO rollouts)

Card (LANE.md L172): one pooled count per arm everywhere; differences WITH
intervals instead of "contains .5"; mean duty with bootstrap CIs beside k/n;
unique seeds only; state the unit of inference explicitly; disclose
twin-vs-base as underpowered rather than "neutral"; delete the
"-.088 inside the .075 sham spread" sentence and replace it with the n=3
sham caveat.

Written BEFORE any new number is read. No rollouts, no graph build, no
torch. Every value is re-derived from STORED artifacts (raw npz traces,
stored results json, stored l156 census rows) with my own metric
implementation.

## Stage split (registered here, honestly)

- Stage (a), THIS run: the canonical unique-seed pooled table (k/n +
  full-precision Wilson + mean duty + bootstrap CI per arm), the
  unique-seed census forms, the difference-with-interval table, the
  unit-of-inference statement, and the three wording fixes the card names.
- Stage (b), appended to the queue if (a) overruns: propagating the
  canonical counts into every remaining table cell of §2.3-§2.6 and the
  figures (figures are L174's job anyway).

## Metric (fixed, inherited, not re-tuned)

Per seed, per side: S(t) = -corr(flexor(t-499..t), extensor(t-499..t)) on
the Ti pools; duty = mean over the q07 window of 1[S >= .25]; the q07
window is the 0.7-Hz segments with a 500-step lead-in dropped, i.e.
TS = arange(499, 6000, 10) restricted to SEGB = [(0,2000,.7),
(2000,4000,1.4),(4000,6000,.7)] segments with f == 0.7 and t >= start+500.
kR = number of seeds with duty_R >= .50. Classes: KILL kR = 0, PARTIAL
0 < kR/n < .5-ish per the draft's own bands, SUPER by the published
Wilson-lb test. No band is re-defined in this run.

## ADMISSIBILITY RULE (A) — which files may enter an arm's pooled count

A file f contributes arm X iff ALL of:
- A1 f carries Ti_{fL,fR,eL,eR}_X_<seed> keys with first axis 6000.
- A2 f's run script's constant block is IDENTICAL to l135_run.py's:
  TAU .05, DT .01, RMAX 1.0, BG .02, NOISE .01, SETTLE 400, WIN 6000,
  SEG 2000, SEGB [(0,2000,.7),(2000,4000,1.4),(4000,6000,.7)].
  Asserted by PARSING the constants out of each run script (l171 §18
  form), never by trusting the narrative.
- A3 where f's results json stores a gain for X, it equals the canonical
  gain for X to 1e-9 (canonical = the modal stored value).
- A4 the seed has not already been counted for X (dedupe by seed, first
  admissible file wins). Jittered-gain replicates (l139 j1-j5) are
  EXCLUDED from the canonical count and reported separately as a
  different-network ensemble (they re-roll the SAME seeds on jittered
  weights, so they are not extra noise seeds of one network).

## UNIT OF INFERENCE (registered statement)

A noise seed of ONE fixed network: one graph, one bisected gain, one drive
protocol; the only thing resampled is the noise stream (and the X0 draw it
seeds). Every interval in the paper is therefore a statement about
seed-to-seed variability of that single network, NOT about variability
across connectomes, specimens, extraction cohorts or gains. The gain
ensemble (5 jitter sets) and the cross-connectome arms are the only places
where the network itself varies, and they are reported separately.

## CERT (must pass BEFORE any new number is read)

- CERT-1 l156 census: re-derive from the stored per-seed `rows` the stored
  pooled cells b65 (below 518 / n 518 / lb) and full (below 361 / n 500 /
  survive 331 / agree 80) field-for-field, plus med_f_below.
- CERT-2 metric: my duty implementation reproduces the stored per-batch
  cells EXACTLY (kR, meanR to the stored 3-dp rounding) for four
  independent run/arm pairs: l142 cutng25, l145 eMotTop5, l150 silW,
  l169d cutng25.
- CERT-3 Wilson: my wilson(k,n) reproduces stored lbR/ubR for those cells
  to < 1e-9.
- If any CERT fails, the run stops and journals the failure (L171 run-1
  precedent).

## BRANCHES (precedence as written)

- S3_dup_inconsistent (checked FIRST): a duplicate (arm, seed) record
  disagrees between two admissible files on duty_R beyond 1e-6 => the
  bit-identity assumption behind forward-chain anchors is broken for the
  metric; report as a data-integrity finding and STOP folding counts.
- S2_class_moves: the canonical unique-seed pooled count changes at least
  one arm's CLASS as stated in the draft (kill / partial / super) =>
  the moved claim is the headline and is re-scoped in the draft.
- S1_counts_stable: every class survives; the fold is numeric only
  (one pooled count per arm, intervals, bootstrap CIs).

## PREDICTIONS (scored, both directions reported)

- P1 the recurring duplicate seeds are exactly the forward-chain anchors
  (a small fixed set, expected {801, 901}), and dedupe removes only them.
- P2 the published pooled n for an arm equals 16 x (number of contributing
  batches) and the per-batch 16-seed blocks are disjoint => the published
  counts were ALREADY unique-seed clean (the card's unique-seed worry bites
  the l156 CENSUS, which pooled traces, not the duty counts).
- P3 the l156 census unique-seed form has n < 518 and keeps lb >= .98;
  the closure form has n < 500 and its p_hat moves by < .10.
- P4 the twin-vs-base difference interval (Newcombe hybrid-score) CONTAINS
  0 => "neutral" is unsupported in BOTH directions and the honest label is
  underpowered.
- P5 the bootstrap CI (10,000 percentile resamples, seed 1720) on each
  arm's pooled mean duty has width > 0 and contains the point estimate.
- P6 the canonical maximal union is LARGER than every union the draft
  currently quotes for cutwA and cutng25 (the draft quotes two unions per
  arm; the canonical replaces both).

## EVIDENCE RULE

The reviewer's own numbers (449 unique of 518, 348/433, p = .41, 55/192)
stay REVIEWER-REPORTED and are BARRED from the draft. Only values this
run derives independently may be folded. Agreement or disagreement with
the reviewer's figures is recorded in this log and CLAIM-MAP only.

## NO-DRAFT-EDIT CLAUSE

No claim's direction or scope changes unless a registered branch fires.
The three wording fixes the card names are pre-authorized: the
unit-of-inference statement (addition), the twin label (neutral ->
underpowered, P4-gated), and the sham sentence (deleted and replaced by
the n=3 caveat, which is a factual correction the reviewer and our own
stored l137.g3 both support: 3 random-cell shams is a spread of three
numbers, not an interval).
