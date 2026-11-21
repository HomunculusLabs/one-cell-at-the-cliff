# L162 PREREG — slow-line ORIGIN probe: one shared clock or independent
# per-pool oscillators? (STATIC, zero rollouts, read-only)

Card: LANE.md ideas 84, L162. L157 established the ~.100 Hz line is NOT
clock-wide: 8 of 20 antagonist pools carry it (Tr/Ta/Sr subset) while Ti is
dead and the aggregates mm/xm show 36/36. This card asks the MECHANISM
question that census cannot answer: do the 8 carrier pools share ONE
oscillator, or do they each oscillate near .100 Hz independently (coherent
only after aggregation)?

## Data (pinned, read-only — same artifacts as L157)

- `l154/raw_l154.npz` (B34): arms {b65, off} x seeds {801, 901, 3401-3416}.
- `l150/raw_l150.npz` (B33): arms incl b65 x seeds {801, 901, 3365-3380}
  (ADDENDUM-1-corrected grid, re-derived from the npz key scan in-script,
  L44 rule — never typed from log prose).
- Channels: the 20 L101 antagonist pools + mm + xm, (6000,) at DT .01.
- Scope: arm b65 on BOTH files (36 traces/channel pooled) is the
  claim-carrying arm. Arm off (l154, 18) is DESCRIPTIVE secondary.

## Target frequency bin (exactness pinned)

- Full trace: WIN 6000, DT .01 -> FBIN 1/60 Hz; the .100 Hz line lands on
  bin 6 EXACTLY (assert |fr[6] - 0.1| < 1e-12).
- Welch segments: L 2000 (20 s), hop 1000 (50% overlap) -> K = 5 segments,
  segment FBIN 1/20 = .05 Hz; .100 Hz lands on segment bin 2 EXACTLY
  (assert < 1e-12). Hann window, mean removed per segment.

## Cell sets (DERIVED from l157/static.json, not typed)

- CARRIER = pools with pooled wilson_lb >= 0.5 (expect 8: Tr_fL, Tr_eL,
  Tr_eR, Ta_aL, Ta_aR, Ta_bR, Sr_aL, Sr_bL). Assert len == 8.
- CONTROL = pools with pooled below <= 6/36 (expect 8: Ti_fL, Ti_fR,
  Ti_eL, Ti_eR, Pr_aL, Pr_aR, Pr_bL, Sr_aR). Assert len == 8.
- Pairs: all 28 unordered CARRIER pairs; all 28 unordered CONTROL pairs
  (matched n, the instrument's own negative arm).
- mm/xm excluded from pairs (they CONTAIN carrier mass by construction;
  reported separately as a trivially-coherent sanity row).

## Instruments

I1 WITHIN-SEED magnitude-squared coherence (MSC) at .100 Hz.
  MSC = |sum_k X_k conj(Y_k)|^2 / (sum_k |X_k|^2 * sum_k |Y_k|^2) at
  segment bin 2, K = 5. Matched arm = both channels from the SAME seed.
  NULL arm = SEED-SHUFFLED: same channel pair, channel A from seed s and
  channel B from seed s' != s, ALL ordered mismatches within a file
  (18*17 = 306 per pair per file, deterministic, no RNG).
  Under independence E[MSC] ~ 1/K = 0.2 (plus overlap bias, which the
  shuffled arm carries identically).

I2 ACROSS-SEED phase-locking value (PLV) of the pair's phase difference
  at full-trace bin 6: dphi_s = angle(X_A[6] * conj(X_B[6])) per seed;
  PLV = |mean_s exp(i dphi_s)| over the 36 pooled b65 seeds; Rayleigh
  p = exp(-n * PLV^2). Under uniform phases E[PLV] = sqrt(pi/(4n))
  = 0.1478 at n = 36. I2 asks a DIFFERENT question than I1: whether the
  phase RELATION is set by the wiring (reproducible across rollouts) or
  drawn per rollout.

I3 (DESCRIPTIVE ONLY, tie-degeneracy disclosed up front) within-seed
  frequency concordance: per seed, interp dom_freq(lo=0) across the 8
  carriers -> within-seed SD; vs within-carrier SD across seeds. L157's
  med_f_below values are all .100/.101, so a both-small (bin-pinned)
  outcome is EXPECTED and carries no information (L95 tie-degeneracy
  class) — reported, never claim-carrying.

## Registered claim classes — COHERENCE axis (decides the card)

A carrier pair CLEARS if median matched MSC >= 0.5 AND median matched MSC
>= 2x median shuffled MSC (per file, over that file's 18 seeds / 306
shuffles).
- D1 SHARED CLOCK: >= 22 of 28 carrier pairs clear, AND carrier median
  matched MSC > CONTROL median matched MSC.
- D2 INDEPENDENT OSCILLATORS: <= 7 of 28 carrier pairs clear (matched
  ~ shuffled) — the aggregate line is an aggregation emergent.
- D3 MIXED / CLUSTERED: 8..21 clear — name the coherent SUBSET and its
  anatomy (within-joint? within-side? Tr/Ta/Sr block?).

## Registered claim classes — PHASE axis (orthogonal, reported alongside)

- P1 PHASE REPRODUCIBLE: >= 14 of 28 pairs with PLV >= 0.5 and Rayleigh
  p < 0.01 -> the relation is wiring-set.
- P2 PHASE LOTTERY: <= 7 of 28 pairs at PLV >= 0.5 -> compatible with one
  shared clock whose phase offsets are a free attractor coordinate
  (L45b/L48 lottery class), NOT evidence against a shared clock.
- P3 MIXED: 8..13.
Both axes are reported; a D-class verdict is never inferred from the P
axis and vice versa.

## Draft-fold decision rule (registered)

Fold ONE observation sentence into DRAFT §4 iff the COHERENCE class
(D1/D2/D3) is the SAME on both files independently AND the class-defining
census holds on the POOLED read (D1: >= 22/28 pooled; D2: <= 7/28 pooled;
D3: the named subset reproduces on both files). Otherwise: LAB-INTENT
observation only, no draft edit. Observation fold only — no new mechanism
claims either way (L149/L157 precedent). If folded, the sentence's numbers
are added to numbers.json under `l162.*` and a new l149_verify section
re-derives them independently.

## CERT chain (before any new read)

CERT-1 analytic: (a) MSC of two .100 Hz sinusoids with a fixed +0.6 rad
  offset plus small noise -> > 0.95; (b) MSC of two independent white
  noise traces -> within [0, 0.75] and clearly below (a); (c) PLV of a
  fixed-offset ensemble -> > 0.999; (d) PLV of a uniform-random-offset
  ensemble (fixed arithmetic phases, no RNG: 2*pi*j/36) -> < 0.05.
CERT-2 reader identity: my loader + VERBATIM l157 dom_freq/bin_argmax/
  wilson_lb machinery must reproduce l157/static.json `pooled` rows for
  ALL 22 channels EXACTLY (n, below, below_bin, wilson_lb, survive,
  med_f_below) — proves the loader and the seed grid are the census ones.
CERT-3 bin exactness: full-trace fr[6] and segment fr[2] both == 0.1 Hz
  to 1e-12.
CERT-4 set derivation: CARRIER/CONTROL derived from l157/static.json and
  asserted len 8 / 8, disjoint, and (named-set check) equal to the sets
  L157's own run.out table implies.

## Output

`l162/static.json` (full precision: per-file + pooled pair tables for both
instruments, class verdicts, I3 descriptive block) + printed tables.
Deterministic, no RNG, zero rollouts, read-only over npz/json.

## ADDENDUM 1 (pre-read, registered before any L162 instrument output)

CERT-4 fired: the PREREG's CONTROL expectation ("expect 8: Ti_fL, Ti_fR,
Ti_eL, Ti_eR, Pr_aL, Pr_aR, Pr_bL, Sr_aR") was typed from L157's prose
summary ("Ti is dead and Pr dead"). The stored artifact
`l157/static.json` has NINE pools at pooled below <= 6/36: that list PLUS
**Tr_fR (0/36)** — a dead pool inside the Tr joint whose sibling Tr_fL is
a carrier. L44 class (re-derive pins from stored artifacts, never log
prose); caught by the registered assert BEFORE any instrument output.

Amendment: CONTROL = ALL pools with pooled below <= 6 (9 pools -> 36
unordered control pairs). The control arm is a NEGATIVE arm only and its
pair count enters no registered threshold — D1/D2/D3 bars count CARRIER
pairs (28, unchanged) and the single control-facing clause is a MEDIAN
comparison (count-insensitive). No other change; the carrier set and all
decision bars stand exactly as registered.

## ADDENDUM 2 (registered AFTER the I1/I2 primary read, BEFORE any
## residual-instrument output — disclosure + admissible null)

Observed: carrier pairs give matched MSC median .660/.719 (l154/l150) but
the SEED-SHUFFLED null arm is ALSO high (.46-.93 per pair), so 0/28 pairs
clear the registered 2x bar and the registered rule formally returns
**D2_independent with fold YES**. That pass is **DEGENERATE (L55 class)**
and is NOT reported as an independent-oscillator finding, for a stated
mechanistic reason:

a seed-shuffled MSC is an independence null ONLY if each channel's .100 Hz
component has a per-rollout random phase. I2 shows the opposite at
ceiling: carrier-pair PLV .941-.995, Rayleigh p <= 1.4e-14, 28/28 locked
(control 10/36). A component whose phase is reproducible across rollouts
is locked to the rollout's own time origin, so channel A from seed s is
coherent with channel B from seed s' just as well as with seed s — the
null arm carries the SAME deterministic component as the matched arm and
the ratio is pinned near 1 by construction (observed .74-1.63). The
registered D-axis therefore cannot separate the card's two hypotheses on
this substrate, and the primary verdict is recorded as
`D_axis_degenerate_protocol_locked`.

ADMISSIBLE instrument (registered now, zero rollouts, same artifacts):

I4 RESIDUAL (induced) coherence. Per (file, arm, channel) subtract the
  across-seed ensemble MEAN trace (n = 18 per file) and recompute I1 on
  the residuals: the deterministic protocol-locked component is removed,
  leaving the per-rollout induced part. (Full-ensemble-mean subtraction
  costs a known 1/n self-subtraction bias, borne IDENTICALLY by matched
  and shuffled arms — disclosed, not corrected.)
  A carrier pair CLEARS-r if residual matched MSC median >= 2x residual
  shuffled MSC median (the absolute .5 bar is dropped: residual power is
  a small fraction of total, so an absolute bar would be a power gate, not
  a coherence gate).
  - D1r SHARED CLOCK: >= 22 of 28 carrier pairs clear-r AND carrier
    residual matched median > control residual matched median -> the two
    pools' per-rollout jitter is shared = one clock.
  - D2r INDEPENDENT: <= 7 of 28 clear-r -> each carrier pool's induced
    .100 Hz part is its own; the shared part is entirely the evoked
    (protocol-locked) component.
  - D3r MIXED: 8..21 -> name the subset.

I5 EVOKED FRACTION (diagnostic, per channel): ev = |mean_s X_s[6]|^2 /
  mean_s |X_s[6]|^2 at the full-trace .100 Hz bin, per (file, arm). ev
  near 1 = deterministic/evoked, near 0 = induced/free-running. Reported
  for all 22 channels; quantifies the contamination named above.

REVISED fold rule (supersedes the fold clause for this card): fold ONE
observation sentence into DRAFT §4 iff the I4 class (D1r/D2r/D3r) is the
SAME on both files AND its pooled census holds. The degenerate D-axis
result is reported in LAB-INTENT and in the digest as a METHOD note, never
as a draft claim.

I3 contamination disclosure: the within-seed SD across carriers (.112 Hz)
mixes seeds whose dom_freq is the FAST line (not every carrier seed is
below-band), so I3 is uninformative as written — descriptive only, as
registered.

## ADDENDUM 3 (CERT-5 fired: I4 WITHDRAWN before any data read; the
## well-posed instrument + an honesty label on the recombined F axis)

CERT-5 (the registered analytic self-test on I4) FAILED at the shared-clock
branch: ratio 1.00, not >= 2. Mechanism, stated: with a single Fourier bin,
the ensemble-mean-subtracted residual of a jittered oscillator is RANK-1 —
every seed's residual is the SAME waveform times a seed-dependent
coefficient — and magnitude-squared coherence is scale-invariant, so MSC
= 1 in the matched AND the shuffled arm. I4 is therefore withdrawn as
degenerate BEFORE any L162 data touched it (zero data-informed choices in
this withdrawal; the self-test alone decided it). I5 (evoked fraction) is
retained.

The deeper point the two failures share: if each channel's own .100 Hz
phase is locked to the rollout time origin, there is NO per-rollout phase
freedom for two pools to share or not share, and the card's
shared-clock-vs-independent dichotomy is not a distinction this ensemble
can express (two deterministic same-frequency oscillators are trivially
phase-locked). That makes the per-channel phase reproducibility the
decisive measurement, not any pair null.

I4' PER-CHANNEL PHASE REPRODUCIBILITY (new, well-posed): per channel,
  PLV_self = |mean_s exp(i phi_s)| over the 36 pooled b65 seeds, where
  phi_s = angle(X_s[bin 6]); plus circular SD.
  - E1 EVOKED / DICHOTOMY-NOT-EXPRESSED: median carrier PLV_self >= 0.8
    on both files -> the line is time-origin-locked in each carrier pool;
    the card's question is NOT separable on this ensemble and the
    admissible future test is named (rollout-side: randomize drive-onset
    phase per rollout, or long single rollouts testing segment-wise
    relative-phase drift) as a new queue item, NOT claimed here.
  - E2 INDUCED: median carrier PLV_self <= 0.4 -> per-rollout phase
    freedom EXISTS, and I2's pair PLV (.941-.995, 28/28 locked) then IS a
    shared-clock claim.
  - E3 MIXED: in between.

I6 WITHIN-ROLLOUT COHERENCE vs the DEAD-POOL ARM + ANALYTIC FLOOR
  (replaces the shuffle null with calibrated references): a carrier pair
  CLEARS-f if pooled matched MSC median >= 0.5 (the absolute bar from the
  ORIGINAL registered `clears` rule, unchanged); carrier-vs-control
  comparison is D1's own second clause, also original. Calibration check:
  the CONTROL arm's matched median must sit within [0.5x, 2x] of the
  analytic independence floor 1/K = 0.2.
  - F1 CARRIER-COHERENT: >= 22/28 clear-f AND carrier matched median
    >= 2x control matched median AND the calibration check holds.
  - F2 NOT COHERENT: <= 7/28. F3 MIXED: 8..21.

HONESTY LABEL (binding): ADDENDUM 3 is written with the I1 table already
in hand. Both F-axis components were pre-registered (the .5 absolute bar;
the carrier-vs-control median clause), but their SATISFACTION was visible
when this recombination was written. Therefore the F axis is reported as
**DESCRIPTIVE-STRONG, not a pre-registered pass**, and the REVISED FOLD
RULE is superseded once more: **NO draft edit this tick regardless of
outcome.** The F/E results go to LAB-INTENT + the digest as a method note
plus a descriptive finding, and a NEW queue item pre-registers the F-axis
bars on HELD-OUT data (the l154 off arm and the remaining l150 arms, plus
a fresh seed batch) per the L88/L90 re-basing rule before any draft
sentence is written.
