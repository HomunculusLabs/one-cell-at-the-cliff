# Response to referees

**Manuscript:** Removing DNp33-L selectively raises right-tibia antagonist duty
in a perturbed fly connectome model

**Date:** 2026-11-21. **Status of this letter:** drafted for owner review; not
yet in the public repository.

This letter answers three referee rounds and one independent second opinion:

| round | referee | report | verdict |
|---|---|---|---|
| 1 | fable 5.2 | `paper/review_fable.md` | major revision, 12 majors |
| 2 | fable 5.2 | `paper/review_fable_r2.md` | major revision, 7 new majors |
| second opinion | claude.ai fable 5.2, own rebuild | `paper/review_claudeai_fable_20261121.md` | do not send yet |
| 3 | gpt-6.2-astra, different model family | `paper/review_astra_r3.md` | major revision |

The short version. The referees were right about the central control, the
title, the Methods, the readout and the novelty claim. The title has been
replaced with the one the third referee proposed. The mass twin the old title
was built on is silent in the model, and the draft now says so. The identity
statement rests on a single-cell scan with delivered-drive and signed-current
comparators that the second referee specified and the third audited. What is
still open is listed at the end of each section and collected in the closing
section. Nothing in this letter should be read as "addressed" unless it carries
a section pointer and an artifact.

## How to read this letter

- **Section pointers** (§) refer to `paper/DRAFT.md` at sha256 `c60fc1859d94…`
  (2,542 lines). That state is local. The public repository head, commit
  `0861ad9`, carries the previous stage (sha256 `6ec995bfef95…`, 2,481 lines).
  From the title onward the two differ only by the single-edge-cut fold (Table
  3b and its sentences in §2.4, the batch label in §3.7, two sentences in §4)
  and by one name redacted in §7 of the public copy. Every other pointer below
  resolves in the public commit.
- **Bracketed keys** such as [l175.scan] are keys of `paper/numbers.json`
  (151 keys, sha256 `464e5261317f…`). Every number of ours in this letter is
  quoted from that ledger as the draft prints it.
- **Referee figures.** A number marked "(referee's figure)" is quoted from that
  referee's report. It is not in our ledger and the draft does not rest on it.
- **Artifact paths** are relative to the repository root.
- **Status words:** resolved, partial, open. They are our own assessment of the
  current draft, not a referee's.

---

## Round 1 (fable 5.2): the twelve majors

Our adjudication of this report is `banc/l167/ADJUDICATION.md` (with
`adjudication.json` and `PREREG.md`). It confirmed all twelve issues at least
in direction from our own artifacts and refuted none. One component of issue 6
was later corrected, as described there and below.

### 1. Unreported scramble arms; the uniqueness claim. Resolved.

You were right. The carrier-free cohorts existed in our tree and were absent
from the draft and the ledger.

- §2.7 now reports all seven carrier-free cohorts on both sides with the
  untreated base. One reaches the high class on the right: 39/48 on its own
  fresh batches and 41 of 50 on the canonical pool, each count labelled
  [l168.scr, l172.pooled]. It raises both sides, where the carrier's signature
  is crossed [l168.base].
- The abstract and §5 say "sufficient, not unique", and set-dependent.
- §2.6, Table 4 adds what round 2 found: in the continuously driven segment
  that cohort falls from 41 to 9 of 50 [l183.ladder_fast].
- Artifacts: `banc/l168/l168_pools.py`, `banc/l168/static.json`,
  `banc/l168/PREREG.md`.
- Still owed (round 2, N7): §2.7 does not say which base the cohort family is
  cut from, and it prints each cohort's extra mass without stating how far
  short of the window it falls in units of the carrier's own mass.

### 2. The male "non-transfer" was a floor artifact. Resolved as a scoping correction; the experiment is open.

You were right. Our male extraction applied no synapse floor, and the female
release carries an implicit pair-level floor of 3 [l146.release].

- §2.11 re-runs the extraction at the matched floor and reproduces your
  figures: 342 cells and K = 52, against K = 77 for the female graph
  [l170.matched]. It states the status, in capitals, as untested at a matched
  floor and not as "no ladder".
- The abstract makes no male claim. §5 says the male connectome is "untested
  at a matched floor, not shown to lack the ladder". Round 2 caught two
  leftover sentences that contradicted §2.11; both are gone.
- No dynamics were run on the floored male graph, and §2.11 says so. Design
  pins for that run are stored [l170.pins].
- Artifacts: `banc/l170/static.json`, `banc/l170/PREREG.md`.

### 3. The slow line described the stimulus. Resolved.

You were right, and the re-attribution is tighter than the one you proposed.

- The slow line is out of the title, the abstract and the headline results.
  §2.13 rebuilds the drive envelope from the run script and finds its dominant
  line at .100 Hz, where the measured line sits [l171.envelope].
- One refinement to your reading: the line is not the chop's 9-s cycle (.111
  Hz). It is the 10-s alignment of the four off-gaps the protocol leaves
  (vector strength .95, against .17 at the 9-s cycle). §2.13 and §3.3 state
  this.
- §3.3 now states the waveform: 500 steps on and 400 off inside both 0.7-Hz
  segments, continuous in the 1.4-Hz segment [l173.protocol].
- What the envelope does not explain is disclosed: sub-band peaks persist with
  the drive off in 11/16 seeds [l154.band]. §5 records the withdrawal.
- Artifacts: `banc/l171/results.json`, `banc/l171/PREREG.md`.

### 4. Gain re-matching was confounded with the flip. Resolved.

You were right. Every edge-removal flip arm sits +1.06 to +1.30% above the
base gain and the non-flip arms sit within ±0.03% [l173b.gains].

- §2.12 runs the control you asked for, the graph × gain 2×2, on both pairs.
  The carrier-removed graph at the base's lower gain stays high (15/16), and
  the base graph at the higher gain does not flip (2/16) [l169.grid]. The
  carrier-versus-twin pair gives the same answer in both gain columns
  [l169d.grid, l169d.legs].
- §2.9 is rebuilt on the one arm that flips at a bit-identical gain, the
  activity clamp (pooled 78 of 98) [l172.pooled, l173b.gains].
- Round 3 asked for more and §2.2 supplies it: a second batch with every key
  arm also run at the base's own gain (carrier 15 of 16 at .683), and a
  gain-only sweep of the base (slope −.0228 mean duty per +0.1% gain)
  [l185.r1, l185.r2]. §3.4 adopts a fixed-gain rule.
- Artifacts: `banc/l169/results_l169.json`, `banc/l169d/results_l169d.json`,
  `banc/l173b/cert.json`, `banc/l185/results_l185.json`, each with its
  `PREREG.md`.
- Residual: you noted that the margin between the clamp arm and the all-edges
  arm could be the gain step and not settle history. §2.4 now says such gaps
  are "settle history plus gain". §2.9 still attributes that margin to settle
  history alone. The §2.9 sentence is the stale one.

### 5. Robustness was narrower than stated. Partial.

You were right, and this one is only partly fixed.

- Done: §2.10 is retitled "endpoints hold, interior re-draws". §4 has a
  paragraph on network-level fragility. §5 says seed-level certainty is high
  and network-level certainty is not. The abstract carries the floor failure.
- Our adjudication reproduced your per-set finding from our own table: the
  carrier-versus-twin contrast is clear in 3 of 5 jitter sets
  (`banc/l167/ADJUDICATION.md`, row 5; source `banc/l139/results_l139.json`).
  That count is not yet a ledger key.
- Not done: the per-set contrast is not printed in §2.10. §2.10 still calls
  the ensemble "a BROADER family than the critique demanded" and still labels
  the twin "NEUTRAL". §1(c) still says the ensemble answers "directly" a
  critique whose own ensemble is much wider. The ensemble is still five sets
  at 1%. No larger ensemble has been run.

### 6. Floor robustness. Resolved, as a reported failure.

You were right about the conclusion, for a stronger reason than the one given.

- The static part. Our stored floor-4 ladder was already re-derived per floor:
  K goes from 77 to 73, five cells leave and one enters, the carrier moves
  from rank 25 to 21 and the twin from 26 to 33, heavy-cohort Jaccard .9231
  [l169b.forms, l146.f4]. We could not reproduce your re-derived ranks, so
  they are not in the draft. Our first adjudication wrongly confirmed the
  frozen-membership premise from a code-shape heuristic; the correction is at
  the end of `banc/l167/ADJUDICATION.md`.
- The dynamic part, where you were right. The analysis was static with zero
  rollouts. We ran the floor-4 arm with fresh gain bisects, and the effect does
  not transfer: all three floor-4 arms read 0/16 on the right while the
  base-substrate arms reproduce on the same seeds (16/16 and 3/16)
  [l169b2.dyn].
- §4 reports both. The sentence calling Kopel-class critiques inadmissible is
  withdrawn and that screen is described correctly [12]. The abstract says the
  effect "is absent at a stricter synapse floor".
- Artifacts: `banc/l169b/static.json`, `banc/l169b2/results_l169b2.json`,
  `banc/l169b2/PREREG.md`.

### 7. Statistical wording outran the tests. Resolved, with one inconsistency of ours.

You were right on every count.

- §2.14 gives one canonical unique-seed pooled count per arm, with Wilson and
  bootstrap intervals, and reports contrasts as differences with intervals
  [l172.pooled, l172.diffs]. §3.7 states the pooling rule and the unit of
  inference [l172.meta].
- Carrier silencing on the intact network is now "no demonstrated effect". The
  sham sentence is corrected: three shams are a spread, not an interval, and
  the −.088 shift is larger than their .075 range (§2.9) [l137.g1, l137.g3].
- The two 5-edge halves are indistinguishable from the base in both
  directions, and the ten edges together sit between base and carrier (§2.14).
- The left-side difference is reported as small: −.050 [−.084, −.023] (§2.14).
- The censuses are on unique seeds: 449 of 449 and 348 of 433 (§4)
  [l172.census_unique].
- Artifacts: `banc/l172/l172_stats.py`, `banc/l172/stats.json`,
  `banc/l172/PREREG.md`.
- Inconsistency: after round 2 the primary twin test is paired (round 2, item
  5 below). §2.14, consequence (a), still calls the twin "INTERMEDIATE … not
  a neutral one" on the pooled margin, which §2.7 and §3.7 now say must not be
  read as an effect of the deletion.

### 8. Abstract and body disagreed. Partial.

You were right.

- Fixed: the abstract is rewritten (1,653 characters) with every numeric claim
  traced to a ledger key by value (`paper/l158_verify.py`, sections 11 to 16).
  Superseded pools are gone. "Kill to super" is gone, and the base is called
  partial throughout. The printed 12× is 9.72×, and §2.9 now calls it "a ratio
  of two measured masses, not a distance below a mass-only band"
  [l173b.gains]. The glutamatergic control is named as one (Table 4, §2.14).
- Not fixed: §2.8 still says "mid-pack removal-mass rank (34/58)" against
  rank 25 everywhere else, with no ledger key. §2.9 says the ten motor edges
  "land between classes" and, two paragraphs later, that all ten together
  reach the high class; the pooled count is 21 of 34, between base and
  carrier.
- The release statement is now wrong in the other direction. The abstract
  promises nothing, but §6 still says "private tree today". The repository has
  been public since commit `2a91f1c` on 2026-11-21.

### 9. Readout scope. Partial.

You were right.

- Fixed: §2.6 says the k = 58 "kill" is a side switch (left side 253 of 258).
  Mean duty with a bootstrap interval sits beside every count (§2.14). The
  unchopped re-score now covers the whole ladder (Table 4), every scan arm
  (Table 1) and the relay arms (Table 3), not one contrast.
- §2.3 reports the pool rates and says what the statistic is: "the sign of the
  correlation between small fluctuations of a near-silent flexor pool and
  bursts in a small extensor pool". §4 has a paragraph headed "One readout
  family".
- Not fixed: the draft still does not say that the other four antagonist pairs
  read 0/16 on the lesion arms. Our adjudication confirmed that from our own
  table (`banc/l167/ADJUDICATION.md`, row 9; `banc/l135/results_l135.json`).
  The 0.3-Hz high-pass re-score exists for the carrier-versus-twin pair on one
  batch only (§2.13) [l171.panel].

### 10. "Two-factor law" was not coherent. Resolved.

You were right. §2.9 is rebuilt on the clamp arm at unchanged gain and the
label is gone. The two bit-identities are in §3.8 as construction checks. The
cohort-clamp arm is disclosed as a label match "with NO demonstrated
separation" [l137.sil24]. §2.8 is labelled observation, not mechanism.
Artifacts: `banc/l173b/cert.json`, `banc/l173b/PREREG.md`.

### 11. Not yet a manuscript. Partial.

You were right, and the remaining distance is real.

- Done: abstract within the limit; §1 to §5 in prose; a Discussion (§5);
  Methods with the update equation, constants, drive waveform, operating
  point, cohort and class definitions and pooling rule (§3.1 to §3.9); 45
  references, with your 20 missing citations at entries 14 to 33, and the
  ApproxBrain, FlyHack and Kopel characterisations corrected (§1(a), §1(c),
  §4). The abstract no longer says "brain-and-nerve-cord": no brain neuron is
  simulated, and §3.1 says so.
- Not done: the file still opens with a 533-line changelog under the heading
  "WORKING DRAFT — preprint skeleton". The abstract heading says "(draft)".
  §2.6 to §2.14 and §3 still carry all-caps emphasis and arm codes. The §7
  author note is stale ("13 entries"). Entries 38 to 45 list first authors
  only. The draft has no figure captions.
- Artifacts: `banc/l173/methods.json`, `banc/l173/PREREG.md`,
  `banc/l174a/raw/`, `paper/references.bib`; gates `paper/l158_verify.py`,
  `paper/l159_verify.py`, `paper/l174_verify.py`.

### 12. Figures. Open.

You were right, and nothing here is fixed. Figures 1 to 3 are the round-1
files. Round 2 added that Fig. 2's printed counts no longer match the canonical
table and that it still says "inert".

Two new figures were commissioned today (`paper/figures/BRIEF_figs.md`): a
scatter of the scan (`paper/figures/fig4_scatter.svg`) and a three-readout
panel (`paper/figures/fig5_threepanel.svg`), each with a caption file beside
it. They landed while this letter was being written. They are not referenced
from the draft, no referee has seen them, and no visual check has been run on
them. The light-background redraw of Figures 1 to 3 from the canonical pools
has not started.

**Round-1 tally, our assessment:** resolved 1, 2, 3, 4, 6, 7, 10; partial 5,
8, 9, 11; open 12.

---

## Round 2 (fable 5.2): the adjudicated claims

Before any draft edit we recomputed each claim under our own tree
(`LANE-LOG.md`, line 416). The log line counts seven: the silent twin, the
unchopped re-score, the Methods mismatch, the abstract and Discussion
contradictions, the paired twin test, the scramble pooling with the pool
rates, and the rate-ceiling cells. Your scripts re-ran to output identical to
your stored files.

The third referee corrected our description of that step, and the correction
is accepted: these were re-runs of referee code and checks against code and
prose, not seven independent replications. N5 was not on that line. It is
answered below as item 8.

You also reported that every pooled count, interval and p-value you recomputed
from raw traces matched the draft. Thank you for doing that from the traces
and not from our tables.

### 1. N1, the mass twin is a silent cell. Confirmed; this changed the paper.

You were right, and this is the most important finding of the three rounds.
Our own lab book called the cell "the SILENT twin" and the draft did not. That
failure is ours.

- Verified by: reading the stored census (`banc/l137/raw_l137.npz`) by cell
  id, which reproduced both of your rates; finding the phrase in
  `LAB-INTENT.md` and the label "near-vacuous" on the twin's clamp arm in
  `banc/l137/results_l137.json`. Your figures are intact-network rates. The
  third referee pointed out that the rate on the cut base is the one that
  matters, and that is the one the ledger now carries.
- The experiment you specified was run: each of the 34 window cells removed
  one at a time from the 24-cell base, 16 seeds per arm, with a census of each
  cell's rate on that base, plus two delivered-drive twins chosen by a rule
  fixed before any rollout (§2.1, Table 1) [l175.scan, l175.meta].
- On the cut base the twin fires at .0005 against the carrier's .3891 and
  delivers .0015 of the carrier's drive [l175.census, l175.meta]. §2.1 has a
  paragraph headed "The mass twin is silent, and we say so". §2.7 repeats it.
- Result: only the carrier reaches the high class (16 of 16; base 5 of 16).
  The two drive twins read 5 of 16 and 2 of 16. Of the 13 other active window
  cells none reaches it, including 7 that deliver more drive than the carrier
  [l175.null, l175.branch].
- The title is replaced, and its rationale block says why. §2.7's heading is
  now "static-mass controls" and its first paragraph says the heading "no
  longer claims that they isolate identity".
- Artifacts: `banc/l175/PREREG.md` (hash prefix `7af87de7b1552896`),
  `banc/l175/results_l175.json`, `banc/l175/selection.json`,
  `banc/l175/L175-FINDINGS.md`.
- Still owed: you found that 3 or 4 of the 10 cells in each scramble cohort
  are silent (referee's figure). The draft does not report the activity of the
  scramble cohorts' cells.

### 2. N2, the robustness panel was applied to one contrast. Confirmed; folded for the ladder, not for everything.

You were right: we had taken up the half that helped.

- Verified by: re-running your
  `paper/review_fable_evidence_r2/p5_unchopped_and_envelope.py`, whose output
  was identical to your stored `out_p5_unchopped.txt` for every arm, and
  auditing the duty implementation in `p1_duty_from_raw.py` (same directory)
  against our convention.
- §2.6, Table 4 re-scores the whole cohort ladder in the continuous segment on
  the canonical pools. It uses your stored per-seed rows
  (`paper/review_fable_evidence_r2/out_duty_rows.json`), admitted only because
  their chopped column reproduces our canonical count for all eleven arms
  [l183.ladder_fast, l183.ladder_fast_meta].
- The text now says what you said. The non-monotone window is specific to the
  chopped readout: the largest cut goes from 1 of 258 to 186 of 258. The
  carrier-free cohort's entry into the class is specific to it too (41 to 9 of
  50). The mass twin shows nothing there (0 of 66). The carrier step persists:
  0 of 258 on the base, 132 of 210 with the carrier removed.
- Tables 1 and 3 carry the same column for every scan and relay arm
  [l184.threepanel, l187.arms]. §3.6 defines the three panels and §4 says they
  are three views of one statistic.
- Still owed. §2.6 opens with "k=58 kills again … a WINDOW" before the next
  paragraph qualifies it. The gain-swap cells of §2.12 are not re-scored in
  the continuous segment in the draft. The high-pass panel is not extended.
  The cross-seed panel is not computed for the cohort pools (Table 4's caption
  says so).
- On "pick one primary readout": the chopped duty remains the registered
  readout and the other two panels are descriptive (§3.6). We have not
  re-chosen, and §2.13 explains why a window swapped after the fact cannot
  become primary.

### 3. N3, Methods did not describe the model that was run. Confirmed; fixed.

You were right on all four legs.

- Verified by: reading the weight construction in `banc/l135_run.py` and the
  header of `banc/build_graph_banc.py` against the Methods sentence in the
  snapshot you reviewed. The run code and the draft disagreed, and the code is
  what ran.
- Weights. §3.1 withdraws the sentence in so many words: "An earlier draft
  stated that weights were in-degree normalized. That sentence described no
  code that was run and is withdrawn." The weight is the natural logarithm of
  one plus the synapse count, signed by predicted transmitter, with negative
  weights multiplied by β = 2.0 [l135.weights].
- Sign rule. §3.1 prints the sign table, including the glutamate override.
- Substrate. §3.1 defines three cell sets: 20,521 cord cells; the baseline
  network of 21,249 with the 728 descending neurons that receive cord input;
  and the closure of 21,809 cells and 647,953 edges, on which every removal
  arm runs [l92.substrate].
- What is left out. No brain neuron and no ascending neuron is simulated, so
  every descending neuron has lost its brain input. §3.1 then states your
  consequence as ours: the baseline network is structured in 513 of 513 seeds
  and the closure in 207 of 513, so "the removal ladder is the removal of
  ectopically active cells from a network they degraded".
- §3.2 prints the per-cell equation and fixes the bound the third referee
  flagged: the rate is bounded above only. §4 carries a paragraph on model
  class and construction. §1(e) says the nearest cord model treats descending
  neurons as controlled inputs and ours lets them run free.
- Artifacts: `banc/l135_run.py`, `banc/build_graph_banc.py`,
  `banc/l92/static.json`, `banc/l173/methods.json` [l173.model].

### 4. N4, abstract and Discussion contradicted the body. Confirmed; four of five fixed.

You were right.

- Verified by: reading the three lines you cited in the stored snapshot
  (`paper/review_fable_evidence_r2/snap1/DRAFT.md.a1848d89`).
- Male ladder: fixed (round 1, item 2).
- "9.72× below any band in which mass alone reproduces the step": withdrawn
  from the abstract, §1 and §5. It survives only in §2.9 as a ratio of two
  measured masses, followed by "§2.7 shows that no such band exists".
- "Converts kill to super": gone.
- Wet-lab: §4 no longer says predictions are not derived. §5 states one, with
  its conditions.
- "One canonical pooled count per arm … everywhere": not yet true. §2.12 still
  prints an intermediate set of pools (42/48, 140/144, 47/160) and the grid in
  §2.9 still prints two-batch pools. They are labelled, but the sentence
  overstates.

### 5. N6, the twin's p = .008 borrowed base seeds. Confirmed; fixed.

You were right. On the twin's own 66 seeds both arms are structured on 7,
neither on 24, the twin alone on 23 and the base alone on 12. The exact
McNemar p is .0895 and the paired mean duty difference is +.048
[l172.paired_twin].

- Verified by: re-running your
  `paper/review_fable_evidence_r2/p2_stats_recompute.py` to identical output,
  then deriving the same table in our own extractor from the per-seed rows.
- §3.7 makes the paired test primary wherever two arms share seeds, and says
  pooled-margin tests "are not used to claim an effect of a deletion".
- §2.7 says the twin-versus-base difference "is therefore not resolved on
  paired seeds". The abstract carries no twin p-value and no "intermediate,
  not neutral".
- Artifact: `banc/l172/stats.json` (per-seed rows).
- Residual: §2.7 still says, two paragraphs earlier, that the twin "is not
  neutral and the question is not underpowered at the canonical pool". See
  also round 1, item 7.

### 6. N7, scramble pooling and near-silent pools. Confirmed; partly fixed.

You were right.

- Verified by: our own `banc/l172/stats.out`, which already read 41/50 for
  that arm while the abstract printed the other pool; and the pool-rate block
  of your re-run `paper/review_fable_evidence_r2/out_p2_stats.txt`.
- Both scramble counts now appear with labels: 39/48 on the cohort's own fresh
  batches, 41 of 50 on the canonical pool (§1, §2.7). The abstract uses the
  canonical one.
- Pool rates are reported: flexor .0260 to .0248 and extensor .0262 to .0330
  between base and carrier removal (§2.3) [l184.q3]. §2.3 says both pools sit
  near the background current.
- Still owed: the scramble family's base and mass shortfall (round 1, item 1)
  and the non-tibia pairs (round 1, item 9).

### 7. The rate-ceiling cells. Confirmed; folded.

Verified in the same stored census as item 1. §3.1 says some deafferented
descending neurons are silent and some sit near the ceiling, and gives the two
window cells with mean rates 1.000 and .994 on the base [l175.scan].

### 8. N5, seed-level certainty and network-level fragility. Right; partial.

This was not on our adjudication line, and it should have been. The jitter
data are ours and say what you say.

- Done: §4 "Network-level fragility"; the robustness paragraph of §5; the
  floor clause in the abstract. "Gain-robust at its endpoints" is gone from
  the abstract.
- Not done: the per-network carrier-versus-comparator table; an ensemble of 20
  or more networks at 1%, 5% and 10%; and citing the weight-noise analysis of
  [4] as the robustness benchmark.

### Other points from round 2

- **The gate that was red at dispatch.** You were right twice. The draft went
  out with one of six gates red in mid-edit. And the gates check ledger
  equality and frozen token sets, not whether a sentence follows from the
  data. The closing section returns to this.
- **Wet-lab view.** §5 now states the intact-animal prediction as a null, the
  assay, the predicted sign and side, and three outcomes that would count
  against the model. §4 says a left-right difference within one bilateral pair
  in one specimen "is more economically explained by reconstruction or
  individual variation than by cell-type function". §5 says we know of no
  functional study of the type and have verified no driver line.
- **Preregistration.** §3.8 has a paragraph headed "What preregistered means
  here": hash agreement is an integrity check, not an external timestamp, and
  several earlier stages are re-analyses of stored data.
- **Base-arm homogeneity.** You asked whether any batch was discarded or
  re-run on the base arm's value. The draft does not answer, and this letter
  will not improvise an answer. The four later batches whose base count is in
  the draft read 5, 3, 6 and 5 of 16 [l175.scan, l185.base, l187.base,
  l190.arms], still inside the 3 to 6 range you flagged. The pattern continues
  and is unexplained.
- **Related work.** Li et al. (bioRxiv, 2026) and Erickson et al. (Current
  Biology, 2026) are not yet cited. Reference 8 still lacks volume and pages.
- **Prose.** §2.1 to §2.5 name arms in words and give each code once per
  table. §2.6 to §2.14 do not yet. The Sapkal paragraph is still in §1.
- **Figures.** See round 1, item 12.

---

## Second opinion (claude.ai fable 5.2, independent rebuild)

This document was supplied by the owner and was not one of our dispatches. Its
author rebuilt the network from the raw connectome tables in separate code and
reproduced the stored pins (21,809 cells, 647,953 edges) and the headline
dynamics. That is the first reproduction of the model outside our code, and we
are grateful for it.

### 1. The silent twin. Confirmed independently.

The second opinion measured the twin at 0.0004 against the carrier's 0.39 on
the cut base (referee's figures). Our census gives .0005 against .3891
[l175.census]. The fix is round 2, item 1. The remark that the draft and claim
map never mentioned it was true.

### 2. Methods weight rule; fragility; "preregistered".

All three were right and converge with round 2. See round 2, items 3 and 8,
and §3.8. The pool sizes the second opinion quotes for the scored side, 51
flexor and 6 extensor motor neurons, are now in §3.1 and §4 [l187.relay].

### 3. Novelty and Alstott et al. (2009). Folded.

You were right. Our sweep was bound to arXiv keyword queries and missed a 2009
journal paper.

- §1 now cites it [41] and says: "location-dependence at matched lesion size
  is established prior art" and "we do not claim the size-matched design as
  ours".
- A third-family prior-art dig then corrected our own first note on that
  paper. We had written that it lacked a mass control. It compared lesions of
  equal size, 50 nodes each (`paper/priorart_terra_20261121.md`).
- The gap paragraph of §1 is rewritten as a conjunction and ends: "Absence
  from our sweeps is not evidence of priority."

### 4. Family-internal review.

You were right that rounds 1 and 2 came from one model family. Round 3 went to
a different family and the prior-art dig to a third. Every referee so far is
still a language model. No one who builds connectome-constrained models of the
fly nerve cord has read this draft, and the second opinion's call for such a
reader stands unmet.

### 5. Two points of fact

- The Habib preprint the second opinion could not find is entry [36],
  doi:10.64898/2026.10.26.762043, with its fields copied from the bioRxiv API
  and stored under `banc/l174b/raw/`.
- "Her raw traces aren't in the repo" is closer to right than our own note on
  the document allowed. Four anchor trace files are release assets
  (`v0.1-lineage`: `raw_l135.npz`, `raw_l169.npz`, `raw_l169c2.npz`,
  `raw_l169d.npz`). No trace file is in the git tree. The raw traces of the
  experiments in §2.1 to §2.5 are not public yet.

### 6. The 56-cell fixed-gain scan and our scans, side by side

Both are stated here. They are not pooled.

| | second opinion (referee's figures) | our scan, §2.1 | our replication, §2.2 |
|---|---|---|---|
| implementation | own code, from raw tables | lab code | lab code |
| gain | the base's gain for every arm | re-bisected per arm | both forms |
| seeds per arm | 8 | 16 | 16, fresh batch |
| cells removed | 56: 13 silent cohort cells, the carrier, 35 other active cells, and 7 barely active ones left out of the table | 34 window cells and 2 drive twins | carrier, mass twin, 2 drive twins, 2 edge-of-band cells, 1 signed-current twin |
| selection fixed before the run | not stated | yes, with hash | yes, with hash |
| base | 3/16, in its 16-seed reproduction | 5/16, .408 | 3/16, .370 |
| carrier | .72, 8/8 | 16/16, .758 | 15/16 .770 re-matched; 15/16 .683 at the base's gain |
| mass twin | .36 | 2/16, .378 | 4/16 .424; 4/16 .390 |
| silent-cell null | .42 ± .05; all 13 within .34 to .49 | 20 cells: 2 to 11 of 16, mean .340 to .605 | gain-only null: 8 to 2 of 16 over a 1% gain span |
| other active cells | 1 up (.62), 9 down, 25 unchanged | 13 cells: none in the high class; ranks 33 and 34 at 0/16 | not re-run |

Sources for our columns: [l175.scan, l175.null, l185.base, l185.r1, l185.r2].

Where the two agree. The carrier is the strongest upward mover and the only
one among its cohort siblings, and the mass twin sits in the noise. At the
base's own gain, which is the second opinion's design, our carrier arm reads
15 of 16.

Where they differ, and what we can and cannot say.

- Our silent-cell null is wider. Part of that is the gain re-match: the
  gain-only slope reproduces R² = .358 of the mean-duty spread of the scan arms
  with small gain shifts, and .453 for the silent ones [l185.r2]. We have not
  run the full scan at fixed gain, so we cannot say the rest would close.
- The second opinion reports that roughly a third of active-cell deletions
  move the readout, mostly downward. Our registered classifier is
  one-directional, so we have no registered count of downward movers. §2.1
  notes the two arms at 0 of 16 and says "Not reaching the super class is not
  the same as having no effect". We have neither reproduced nor contradicted
  "9 down".
- The draft does not cite the second opinion's scan. It is a different
  implementation, arm selection, gain rule and batch size. The third referee
  called it "useful corroboration, not a pooled replication", and our evidence
  rule keeps referee numbers out of the draft until we reproduce them. Whether
  §2.1 should carry one sentence pointing to it is an owner decision.

The three fixes the second opinion asked for before sending are done: the
twin's rate is reported and activity-matched twins replace it as the control
(§2.1), the single-cell null distribution is Table 1, and the Methods sentence
is withdrawn (§3.1).

---

## Round 3 (gpt-6.2-astra, cross-family)

This round tested something the first two could not: whether the readout
passes on traces that never interacted. It did, and that changed what the
paper says the effect is.

### 1. Independent arithmetic and the audit of our adjudication

You reproduced the historical pools from raw traces and upheld the round-2
adjudication, with the refinement recorded above (re-runs and checks, not
seven replications). Your reminder that these are "intervals for noise seeds
on a specified model" is the position of §2.14 and §4.

### 2. The scan decision (D2), independently confirmed

You scored all 37 arms on all 16 seeds from raw and confirmed the 322 anchor
comparisons and the 1,728 cross-worker comparisons [l175.certs]. The registered
branch in which the flip follows the cell and not its delivered drive stands
[l175.verdict]. Each limit you attached to it is now in §2.1:

- the classifier is one-directional and coarse, and none of 13 in the high
  class does not mean none of 13 affected (ranks 33 and 34 read 0 of 16);
- the silent-cell null is wide: 2 to 11 structured seeds of 16, mean duty .340
  to .605 [l175.null];
- across the 33 non-carrier arms the readout falls as the re-bisected gain
  rises (ρ = −.723; −.833 among the silent cells), the carrier runs against
  that trend, and rank 47 bisected to an outlying gain (+10.28%);
- the drive match is real (×1.003 and ×1.006) and it is unsigned,
  time-averaged and pooled over all targets [l175.census].

Your objection that such a scalar need not match what reaches the scored pools
was right. §2.2 answers it with a registered signed-current twin: the nearest
of 4,751 active cells, relative distance .003, reads 2 of 16 at .345
[l185.r3]. It is one batch and one definition, over paths of at most two
synapses. A waveform-replay comparator and a target-resolved comparator beyond
two synapses have not been run. §5 adopts your conclusion: none of these
comparisons "isolates identity from every possible description of what a cell
delivers".

Artifacts: `banc/l175/results_l175.json`, `banc/l185/results_l185.json`,
`banc/l185/PREREG.md` (hash prefix `f1f7150240e629f5`),
`banc/l185/L185-FINDINGS.md`, `paper/review_astra_evidence_r3/`.

### 3. The cross-seed finding, and the three-readout panel it produced

You were right, and this is the most consequential result of the round. We
re-ran your `locked.py` and it reproduces (`LANE-LOG.md`, line 421).

- Table 1 now gives three readouts for every scan arm: the registered chopped
  duty, the continuous 1.4-Hz segment and the cross-seed pairing
  [l184.threepanel]. §3.6 defines them.
- §2.3 reports your result. With the carrier removed the mean duty is .758 for
  true pairs and .622 for cross-seed pairs, and 193 of 240 ordered pairs clear
  the bar. On the base the values are .408 and .097, with 0 of 240.
- The decomposition goes further than your report. The cross-seed duty rises
  by +.525 between base and carrier removal while the same-seed duty rises by
  +.350, and the run-specific remainder shrinks (−.174) [l184.q3]. §2.3
  carries your instruction that the two duties "must not be subtracted to
  obtain a variance fraction".
- In the continuous segment the carrier-removed arm keeps 8 of 16 at .510
  while the base and the scan twins score 0. §2.3 repeats your caveat: applied
  descriptively, the bands put no arm in the high class there.
- The template-residual analysis you asked for was done on stored traces:
  removing the fitted gate and tone templates leaves a deletion effect of
  +.209 [l184.sens].
- The wording follows. The abstract says "a change in shared timing, not
  rate". §5 says we describe the readout "as antiphase duty and not as
  endogenous motor organisation".
- Artifacts: `paper/review_astra_evidence_r3/locked.py`, `locked.csv`,
  `b39-arms.csv`; `banc/l184/threepanel.csv`, `banc/l184/q3.csv`,
  `banc/l184/sensitivity.csv`, `banc/l184/PREREG-analysis.md`,
  `banc/l184/L184-FINDINGS.md`.

### 4. Title. Adopted unchanged.

The title is the form you proposed. The rationale block under it records why
the old one was wrong: it credited a silent twin with isolating identity, and
it called a band crossing an all-or-none regime transition. The §2 preamble
adds: "Crossing a registered band classifies one readout on one graph. It is
not evidence of a bifurcation." Table 1 labels the base partial, not killed.

Three things are not yet consistent with the new title.

- "Not delivered drive" appears with its definition (mean rate times outgoing
  weight, unsigned) and not with the word "scalar". Adding the word is cheap.
- Sections kept from the cohort lineage still speak for the old title. §2.12
  says "The claim the title makes, however, rides the twin-XOR pair" and that
  cell identity "carries the transition on BOTH sides of the pair". Result (2)
  in §1 opens with "carried by one cell's identity, not its removal mass"
  before qualifying it. These sentences are wrong about the current paper.
- The README of the public repository still carries the retired title and
  retired claims. It must be rewritten before a reader is pointed at the
  repository.

### 5. Paired inference. McNemar is primary.

Done as you and round 2 asked: §3.7 "Paired inference", §2.7, and
[l172.paired_twin] (p = .0895 on 66 paired seeds, against the pooled .008).
§2.2 adds your caution in general form: once the gain or the graph changes,
same-seed pairing buys no variance reduction, so paired differences are read
as differences of batch means.

### 6. Your three changes

**(1) Make the measured contrast the paper.** Done in text and tables: title,
abstract, the full scan with continuous effects, twins, gains and low-rate
controls (Table 1), chopped and continuous readouts side by side including the
reversed historical endpoint (Table 4), and the cross-seed control. Not done
as a plot: see round 1, item 12.

**(2) Validate on a frozen second batch.** Done as batch N (§2.2, Table 2):
the carrier, the mass twin, both drive twins, the two edge-of-band cells and
the base, each at re-matched and at fixed gain, plus a five-point gain sweep
of the base alone.

- The carrier replicates in both gain forms and is 31 of 32 pooled over the
  two batches.
- Your concern about gain covariation was right, and rank 40 is the worked
  example: it stays elevated at its re-matched gain (12 of 16) and loses the
  elevation at the base's gain (3 of 16). Rank 27 regressed to the null (11 of
  16, then 4 of 16).
- The wire-jitter and floor-4 failures stay visible in the abstract, §4 and
  §5.

Two follow-ups went beyond your request and bound our own claim. Removing one
cord interneuron downstream of the carrier reaches the high class alone on the
chopped readout (13 of 16), without the carrier's 1.4-Hz signature (§2.4,
Table 3) [l187.arms]. Cutting only the carrier's edge onto it gives 12 of 16
at .624 with a 1.4-Hz duty of .000, and a count-matched sham reads 5 of 16
(Table 3b) [l190.arms]. So the chopped classifier alone is not specific to the
carrier, and §2.4 and §4 say so. Artifacts: `banc/l187/results_l187.json`,
`banc/l187/PREREG.md` (hash prefix `98034281b435e961`),
`banc/l190/results_l190.json`, `banc/l190/PREREG.md` (hash prefix
`48e882a264434dd0`), `banc/l190/L190-FINDINGS.md`.

**(3) Make the model and estimand reconstructible.** Done in §3.1 to §3.7:
closure against baseline network, missing upstream inputs, signed log weights,
gain target and residuals, readout windows, and the paired test in place of
the .008 claim. The abstract and the new tables are generated from the ledger
with canonical and fresh-only pools labelled. Two parts are not done.

- Figures are not regenerated.
- The older precedents are only partly cited. Chalfie et al. [38] and Alstott
  et al. [41] are in §1. Honey & Sporns (2008), Luccioli et al. (2014),
  Soloperto et al. (2016), Boes et al. (2015) and Prinz et al. (2003) are not
  in the draft or the bibliography. Our prior-art dig did not cover them, and
  no citation enters without a fetched primary record, so they are queued.
  Luccioli et al. bears most directly on a single-cell-switch novelty claim.
  §1 already disclaims the invention of single-cell ablation scans, and the
  citation is still owed.

### 7. What remains open, stated as limitations

These are in the draft as limitations. None of them is resolved.

- **Which clock the timing follows: unresolved.** §2.5 and §4. The deletion
  contrast survives independently jittered gate onsets under both clocks:
  +.275 [+.179, +.371] gate-aligned and +.290 [+.181, +.400] at equal elapsed
  time. Their difference is −.015 [−.156, +.126], and the registered branch is
  mixed and unresolved [l186.contrasts, l186.branch]. The run could not have
  resolved it. The jitter band was 600 steps against a 500-step readout
  window, so paired windows share 62% of their samples on average
  [l186.power]. That was a design error of ours, found after the run
  (`banc/l186/t216_power.py`). A run with at least 1,000 steps of jitter has
  not been done.
- **No relay-matched twin.** §2.4 and §4. Nothing in the draft says how often
  removing an active inhibitory cord interneuron lifts this readout. The
  identity statement is scoped to descending window cells and their twins.
- **Single-batch classes.** §4. The class labels of the non-carrier scan arms
  rest on one batch of 16 seeds, and the rank-27 label moved on the second.
  The relay, push-pull and occlusion arms, the edge cut and its sham, and the
  signed-current twin have one batch each. The edge cut exists only at a
  re-bisected gain (−0.358%), on a base where a lower gain raises duty by
  itself, and it has one eligible sham edge [l190.gain, l190.meta].
- **One readout family, one graph.** §4. One antagonist pair on one side, in
  pools near the background rate. The effect is absent at a stricter synapse
  floor, the transition interior re-draws under 1% weight jitter, and a rewire
  of the carrier's own edges flips in one draw of three.
- **No bench data and no prediction for the intact animal beyond a null.** §5.

---

## Closing: the verification machinery, and what it does not verify

**Ledger.** `paper/numbers.json` is generated by `paper/extract_numbers.py`
from stored results. `paper/CLAIM-MAP.md` maps each claim to its script,
artifact and gate section; blocks B43 to B49 cover the experiments of §2.1 to
§2.5.

**Gates.** Seven scripts: `paper/l143_verify.py`, `l149_verify.py`,
`l158_verify.py`, `l159_verify.py`, `l161_verify.py`, `l174_verify.py` and
`l183_verify.py`. They were re-run for this letter at 14:10 EST on 2026-11-21
against the draft and ledger named at the top. All seven exit 0.

What they check: that every quoted number equals its ledger key; that the
abstract meets a frozen contract; that the body from the title on is a byte
replay of a declared edit ledger over a stored pre-image
(`paper/l183_fold.py`, `paper/l183_text.py`); and that no measurement in the
folded text is typed by hand.

What they do not check: whether a sentence follows from the data. Round 2 said
so, and this letter is the evidence. Every stale sentence listed above passes
all seven gates. Gate pins were also re-pointed during today's folds. Each
re-point is receipted with old value, new value and reason in `LANE-LOG.md`
(lines 436, 437 and 440), with the statement that no assertion was deleted or
relaxed. A referee is entitled to check that statement against the gate files'
history.

**Preregistration.** Each run has a `PREREG.md` whose hash is recorded in the
result it governs. The prefixes for the four rollout experiments behind §2.1,
§2.2 and §2.4 are given above; §3.8 lists three of them and does not yet list
the edge cut's. Hash agreement shows a plan was not edited after its result
recorded it. It is not an externally dated registration, and public history
begins on 2026-11-21.

**Anchors.** Before any new number is read, inherited arms are replayed
against stored raw traces and must agree exactly. Every count below came back
with maximum difference 0.0.

| experiment | anchor comparisons | cross-worker comparisons | key |
|---|---|---|---|
| scan (§2.1) | 322 | 1,728 | [l175.certs] |
| replication (§2.2) | 368 and 300 | 2,185 | [l185.certs] |
| relay arms (§2.4) | 322 and 48 | 2,375 | [l187.certs] |
| gate jitter (§2.5) | 92 | — | [l186.power] |
| edge cut (§2.4) | 92 and 50 | — | [l190.certs] |

**Public repository.** github.com/HomunculusLabs/one-cell-at-the-cliff

| commit | content |
|---|---|
| `2a91f1c` | initial public release: draft, lineage, gates, lab books |
| `7c6b2d3` | snapshot with the six gates of that date green |
| `3286d6b` | README correction on release assets |
| `f00a19e` | round-2 report and evidence |
| `4dbfab6` | round-3 report and evidence |
| `0861ad9` | the master fold: new title, abstract, §2.1 to §2.5, Methods, related work, limitations |

At `0861ad9` the tree holds the results, registrations and scripts of every
experiment cited in this letter (`banc/l175`, `l184`, `l185`, `l186`, `l187`,
`l190`), all four referee documents, the three evidence directories of rounds
1 to 3, and the prior-art dig. Every claim of fix above resolves at that
commit, with these exceptions:

- Table 3b and its sentences (the single-edge cut) are in the local draft
  only, with a ledger of 151 keys against the public 145.
- This letter and the two new figure files are local only.
- The raw traces of the experiments in §2.1 to §2.5 are local only.
- The README at that commit still presents the retired title and claims.

**Open items, collected.** Ordered by how much they bear on the claim.

1. No human referee from the field has read the draft.
2. Which clock the shared timing follows (needs a run with wider jitter).
3. No relay-matched twin; relay, edge-cut and signed-current arms are one
   batch each; the edge cut has no fixed-gain form.
4. Network-level robustness: per-set contrast table, a larger weight-noise
   ensemble.
5. Stale sentences from the cohort lineage: §1 result (2), §1(c), §2.6
   opening, §2.7 "not neutral", §2.8 rank, §2.9 settle-history margin and
   ten-edge wording, §2.10 "BROADER" and "NEUTRAL", §2.12 title sentence and
   intermediate pools, §2.14(a), §6 release statement, §7 note.
6. Disclosures owed: non-tibia pairs at 0/16; the scramble family's base, mass
   shortfall and cell activity; the base arm's batch homogeneity.
7. Citations owed: Honey & Sporns, Luccioli et al., Soloperto et al., Boes et
   al., Prinz et al. (2003), Li et al., Erickson et al.; the weight-noise
   benchmark of [4]; volume and pages for [8]; author lists for [38] to [45].
8. Figures: redraw 1 to 3; check the two new ones by eye and bring them and
   their captions into the draft.
9. Manuscript form: the changelog banner, the "WORKING DRAFT" heading,
   all-caps emphasis and arm codes in §2.6 to §3.
10. Public state: push the stage with Table 3b, this letter and the figures;
    rewrite the README; publish the raw traces of §2.1 to §2.5; dated public
    registration for future runs.
11. The male transfer experiment at a matched floor.

We thank all four reviewers. The paper that survives is smaller than the one
first submitted and better supported, and most of the difference is theirs.
