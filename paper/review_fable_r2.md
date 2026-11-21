# Referee report, round 2 — fable 5.2 (claude-fable-5-2, official Anthropic route)

Reviewed: `paper/DRAFT.md` at sha256 `a1848d890195bb25a34b…` (1,654 lines, 108,031 bytes), the
state named in the brief. Review window 2026-11-21 10:11–10:30 EST. A byte copy of that state
is at `review_fable_evidence_r2/snap1/DRAFT.md.a1848d89`; all line numbers below refer to it.

Three things to know before reading the rest:

- **The draft and one gate were edited while I reviewed.** `DRAFT.md` moved to sha
  `d76fa7d6…` at 10:20:34 (one 19-line changelog paragraph added; body byte-identical, diff
  saved). `l149_verify.py` had three different hashes during the window (see Task 1), and
  `CLAIM-MAP.md` and `banc/l174b4iiib/` also changed. Before/after file listings are saved.
- **No vision and no rollouts**, as instructed. Figure findings come from SVG parsing. Every
  statistic I report is recomputed from the stored raw `.npz` traces with my own code.
- **Nothing outside my two output locations was written by me.** The one verify script with a
  write path (`l158_verify.py` creates a pin file if absent) was checked first; the file existed.

## Verdict

**Major revision.** The numbers are honest: every pooled count, interval and p-value I
recomputed from raw traces matches the draft. Six of the twelve round-1 majors are resolved,
five are partly resolved and one (figures) is untouched.

The verdict stays at major revision because of what the recomputation turned up beyond the
round-1 list:

1. The mass-matched twin, the control the title is built on, is a cell that is silent in the
   model. The lab's own log says so; the draft does not.
2. The "unchopped segment" re-score is used in the abstract to support the identity contrast,
   but applied to the rest of the paper it reverses the first headline result (k=58 goes from
   1/258 to 186/258) and removes the "one scramble supers" result (41/50 to 9/50).
3. Methods describe a different weight rule and a different substrate from the ones the code runs.
4. The abstract and Discussion assert things the body has retracted.

The carrier effect itself survives all of this and in one respect gets stronger (carrier
132/210 against base 0/258 in the unchopped segment). What does not survive as written is the
framing: "mass-twin controls isolate identity, not mass" and "a non-monotone, all-or-none
window". Fixing item 1 needs new rollouts, not editing.

## Task 1 — verify scripts

Interpreter `~/critters/peabrain/.venv/bin/python`, `CUDA_VISIBLE_DEVICES=""`.
Outputs in `review_fable_evidence_r2/verify_*.out`; statuses in `02_verify_exit_statuses.txt`.

| script | exit | note |
|---|---|---|
| l143_verify.py | 0 | all green |
| l149_verify.py | **1**, then 0 | see below |
| l158_verify.py | 0 | all green; abstract pinned at 1,916 chars (I recounted: 1,916) |
| l159_verify.py | 0 | pass |
| l161_verify.py | 0 | all green |
| l174_verify.py | 0 | all green |

`l149_verify.py` failed at 10:12 with `AssertionError: (24) identifier digits removed != the
declared lane IDs`, after printing checks (1)–(23) green. Its hash was `9934180c…` when I
pinned it at 10:11:51, `4a580136…` when it ran, and `9595db3d…` at 10:18:47. Re-run at
10:19:59 on that third version: exit 0, 28 checks green, with `DRAFT.md` unchanged in between.
The diff between the failing and passing gate (361 lines, saved) re-points token-count pins for
the batch relabel (B26 → "batch A", counts 400 → 395 and 247 → 243). `banc/l174b4iiib/` was
being written at the same time. So the lane agent was mid-stage: the draft had been edited at
10:08 and the gate had not caught up.

Two consequences. The draft was dispatched for review with one of six gates red. And the gate
went green by editing its pins to match the draft, which is what these gates are: they detect
change in the draft's token sets and check ledger equality. They do not check that a sentence
follows from the data. Every problem in Task 4 passes all six.

## Task 2 — delta-check of the 12 round-1 majors

Wording follows `review_fable.md`; the brief's shorthand list differs in places (its item 9 is
the "other pairs are 0/16" component of round-1 major 9).

| # | round-1 major | verdict | evidence |
|---|---|---|---|
| 1 | Scramble arms unreported; uniqueness overclaim | **RESOLVED** | Title, abstract, §2.2 table, `l168.scr`. Residuals: counts are 39/48 where the paper's own canonical rule gives 41/50 (N7); "mass-matched" is loose (N7); result is scoring-window dependent (N2). |
| 2 | Male non-transfer was a floor artifact | **PARTIAL** | §2.6 (line 869) now says "UNTESTED AT MATCHED FLOOR, not 'no ladder'". But the abstract (line 476) still says "the male connectome admits no such ladder", and the new Discussion (line 1513) says "the ladder does not transfer to the male connectome at a matched synapse floor (§2.6)". §2.6 ran no dynamics on the floored male graph. The Discussion sentence is new and false. |
| 3 | Slow line described the stimulus | **RESOLVED** | Out of the headline; §3.3 states the chop; §2.8 re-attributes. I rebuilt the envelope: dominant line .100 Hz, next .1167 Hz at 47% (`out_p5_unchopped.txt`). |
| 4 | Gain re-matching confounded with the flip | **RESOLVED** | §2.4 gain table; §2.7 two 2×2 designs. All eight cells reproduce from raw (`out_p7_controls.txt`). Caveat under N2. |
| 5 | Jitter robustness narrower than stated | **PARTIAL** | §2.5 now says the interior re-draws. Still missing: the per-set carrier-vs-twin contrast, which the lab's own adjudication confirmed as clear in 3 of 5 sets. "a BROADER family than the critique demanded" is still there (line 845). Ensemble is still five sets at 1%. See N5. |
| 6 | Floor robustness only with membership frozen | **RESOLVED** | §4: membership re-derived, the dynamic floor-4 arm was run, and its failure is reported plainly (all three arms 0/16; reproduced from raw). The Kopel sentence is corrected. The consequence is not in the abstract (N5). |
| 7 | Statistical wording outruns the tests | **RESOLVED** | Twin relabelled, sham sentence fixed, unique seeds, difference intervals, unit of inference stated. A new problem with the twin p-value is N6. |
| 8 | Abstract/body inconsistencies | **PARTIAL** | Fixed: superseded pools, 12× → 9.72×, key-less numbers. Not fixed: "converts kill to super" (line 465; the step is partial → super, base 72/258); "rank (34/58)" (line 706) against rank 25 elsewhere, with no ledger key; "We release the preregistration…" (line 481) against "private tree today" (line 1554). New ones are listed in N4. |
| 9 | Readout scope | **PARTIAL** | Fixed: k=58 is described as a side switch (§2.1); mean duty with bootstrap intervals added. Not fixed: the draft never says the other four antagonist pairs are 0/16 in the lesion arms; the unchopped re-score is reported for one contrast only (N2). |
| 10 | §2.4 incoherent as a "two-factor law" | **RESOLVED** | Rebuilt on the unchanged-gain clamp arm; identities moved to §3.8; sil24 non-separation disclosed. |
| 11 | Not yet a manuscript | **PARTIAL** | Now present: 1,916-char abstract, prose §1–§5, Discussion, Methods with equation, 37 references cited in text. Still present: a changelog banner of about 430 lines above the title, the heading "WORKING DRAFT — preprint skeleton", 222 all-caps tokens of four or more letters between the abstract and §5 (126 distinct; 212 without BANC), no figure captions, §7 author notes ("13 entries"). Methods contain errors (N3). The abstract's second sentence still reads "We run a female Drosophila brain-and-nerve-cord connectome"; no brain neuron is simulated. |
| 12 | Figures | **UNRESOLVED** | Files unchanged since round 1 (11-18 and 11-19). Fig. 2 now disagrees with the text: its labels read 43 of 144, 28 of 32, 124 of 128, 21 of 32, 14 of 32, 8 of 32 where the table has 72/258, 78/98, 203/210, 21/34, 31/98, 25/98; it still says "inert", a word the text withdrew; it carries a lane tag. Text is 3.5–4.3 pt (Fig. 2) and 2.8–3.1 pt (Fig. 3) at 6.5-inch width on a dark background. Fig. 1 has no SVG. The draft says the redraw stage is open. |

Tally: 6 resolved, 5 partial, 1 unresolved, 0 regressed.

## Task 3 — headline statistics recomputed from raw traces

Method: `p1_duty_from_raw.py` computes tibia duty for every arm × seed in every
`banc/*/raw_l*.npz` (44 files, 6,506 rows) from the definition in §3.6, using rolling Pearson
over sliding windows rather than the lab's per-window loop. `p2_stats_recompute.py` pools
unique seeds and computes Wilson, Newcombe and Fisher with my own implementations. Output:
`out_p2_stats.txt`. I used the lab's list of 38 admissible files and did not re-derive the
admissibility rule; the six excluded files with tibia traces are the five jitter sets and one
pre-protocol file, as the draft says.

**All of it matches.**

| quantity | my recomputation | draft |
|---|---|---|
| carrier (cutng25) | 203/210, [.933,.984], mean duty .766 | same |
| twin (cutng25p) | 30/66, [.340,.574], .459 | same |
| base (cutwA) | 72/258, [.228,.337], .404 | same |
| clamp (silW) | 78/98, [.706,.864], .644 | same |
| k=19 / k=29 / k=58 | 5/178, 188/194, 1/258 | same |
| carrier − twin | +.512 [+.388,+.628], p = 3.85e-20 | +.512 [+.388,+.628], 3.8e-20 |
| carrier − base | +.688 [+.621,+.742], p = 3.37e-59 | same, 3.4e-59 |
| twin − base | +.175 [+.047,+.305], p = .0076 | same, .008 |
| clamp − base | +.517 [+.410,+.602], p = 6.68e-19 | same, 6.7e-19 |

All 14 pooled cells of §2.9 and all 12 difference rows match to the printed precision, with
zero inconsistent repeat seeds. The §2.7 and §4 control cells (gain swaps, three rewire draws,
the same-footprint deletion, the three floor-4 arms, both sides) also reproduce from raw.

One number in the abstract does not follow the paper's own rule: the scramble arm is printed as
39 of 48, while the canonical unique-seed union gives 41/50 (the lab's own `l172/stats.out`
also says 41/50).

## Task 4 — fresh majors

### N1. The mass twin is a silent cell, so the central control does not control what is claimed

The title says mass-twin controls isolate cell identity rather than removal mass. "Removal
mass" (§3.5) is the summed absolute out-weight of a cell. In a rate model a cell acts on its
targets through g·W·x, so a cell with x ≈ 0 delivers nothing however large its out-weights are.

The lab's stored census (`banc/l137/raw_l137.npz`, intact closure, one seed, all 58 ladder
cells) gives:

- carrier, id 1110: mean rate **.454**
- twin, id 319: mean rate **.0033**, 137× lower
- 26 of the 58 ladder cells are above the paper's own "active" bar of .05; 20 are below .01

The lab knows this. `LAB-INTENT.md` lines 6386–6387 call id 319 "the SILENT twin (x_mean
.0033)", and `results_l137.json` labels the arm that clamps it "near-vacuous". The draft quotes
the carrier's .454 (§2.4) and never mentions the twin's value; `numbers.json` does not hold it.

So the two-cell comparison matches static weight and leaves delivered drive unmatched by two
orders of magnitude. What it shows is that removing an active cell differs from removing a
silent one. That is weaker than "identity, not mass", and a reader who knew the twin was silent
would not accept it as a mass control. The same applies to the scramble cohorts: 3 or 4 of the
10 cells in each are silent (`out_p8b_activity_weighted.txt`).

What I did not check: the twin's activity on the cut base. It is not stored and I was not
permitted rollouts. The census is one seed.

Required: disclose the twin's activity; add comparators matched on delivered drive (mean rate ×
out-weight, measured on the cut base). The cheapest decisive experiment is a single-cell scan:
remove each of the other 33 ladder cells in turn from the k=24 base, 16 seeds each, and report
each cell's rate and outcome. That gives a distribution in place of n = 1.

### N2. The robustness panel is applied to one contrast; applied to the others it changes the paper

§2.8 re-scores the carrier-vs-twin pair in the unchopped 1.4-Hz segment and the abstract quotes
it (12 of 16 against 0 of 16). I applied the identical statistic and thresholds to every arm at
the canonical pools (`out_p5_unchopped.txt`):

| arm | published (0.7-Hz chopped) | unchopped 1.4-Hz |
|---|---|---|
| intact closure | 207/513 | **0/513** |
| k=19 | 5/178 | 0/178 |
| k=24 base | 72/258 | 0/258 |
| twin | 30/66 | 0/66 |
| carrier (k=25) | 203/210 | 132/210 |
| k=29 | 188/194 | 108/194 |
| k=58 | **1/258** | **186/258** |
| heaviest scramble (cutscr0) | 41/50 | **9/50** |
| carrier-cut graph at the lower gain (two batches) | 15/16, 15/16 | 2/16, 4/16 |

Consequences:

- Headline result 1 (a non-monotone window in which "k=58 kills again") is a property of the
  chopped scoring window. In the unchopped segment k=58 is the strongest lesion arm.
- "Sufficient, not unique: exactly one scramble supers" does not hold in the unchopped segment.
- The twin's "intermediate, not neutral" status disappears (0/66 against 0/258).
- The "graph, not gain" reading weakens: the carrier-cut graph at the lower gain falls from 9/16
  to 2/16 and 4/16.
- The carrier step gets cleaner: 0/258 → 132/210.

Round 1 reported the same pattern on one batch (baseline 0/16, k=58 13/16). The draft took up
the half that helps and left out the half that does not. A robustness panel has to be shown for
every headline cell or for none.

### N3. Methods do not describe the model that was run

Checked against `banc/l135_run.py` and `build_graph_banc.py` (`out_p4_substrate.txt`, NOTES).

- **Weights.** §3.1 says "Edge weights are in-degree normalized … [l173.model]". The code uses
  `log1p(synapse count) × sign`, with no normalization anywhere in the run scripts, and the
  cited ledger key contains neither fact. Jitter is applied "post-log1p" per the ledger.
- **Sign rule.** Not stated. Glutamate is forced inhibitory; dopamine, serotonin and octopamine
  are +0.2; tyramine and unknown are +0.3.
- **Substrate.** §3.1 describes "the cord plus the descending neurons that receive cord input".
  That is the 21,249-cell network the paper calls b65. Every cohort arm runs on a different
  network: b65 plus 560 descending neurons that project to the cord and receive no cord input.
  That 21,809-cell "closure" is never defined.
- **What is left out.** Ascending neurons are excluded from the "cord" (1,840 cells annotated
  ascending, 509 sensory-ascending). No brain neuron is simulated, so the 560 added descending
  neurons have lost all their brain input; their activity is set by each other and by the
  background current. Two of them sit at the rate ceiling (.999 and .986).

The last point matters for interpretation and is not in Limitations. The network without those
560 cells is structured in 513/513 seeds. Adding them drops it to 207/513. The entire dose
ladder is the removal of ectopically active, deafferented descending neurons from a network
they degraded. The nearest cord rate model (the draft's reference 4) activates descending
neurons in a screen, as inputs under the experimenter's control (from an excerpt of its
preprint; I did not read the full text).

### N4. The abstract and Discussion contradict the body

Lines from the reviewed snapshot; list in `out_p7_controls.txt`.

- Male connectome: abstract line 476 and Discussion line 1513 against §2.6 line 869 (see
  delta-check 2).
- "9.72× below any band in which mass alone reproduces the step" (abstract, §1, §2.4, §5). The
  denominator .0544 is the extra mass of one cohort, the heaviest scramble. §2.2 says in its
  own words that outcome among these cohorts is "not monotone — not even ordered — in removed
  mass". The paper therefore shows no mass-only band, and the ratio has no referent. Separately,
  §1 (line 619) and §5 (line 1505) attach 9.72× to "the carrier's own removal mass"; that mass
  is .00644, which gives 8.45×. The 9.72 figure belongs to the 70 intrinsic out-edges (.005599).
- "Removing DNp33-L converts kill to super" (line 465): the base it converts is partial.
- §4 line 1465 "Wet-lab predictions are NOT derived here" against §5 line 1539 "a spiking or
  wet-lab replication can refute that".
- "One canonical pooled count per arm … everywhere" (§2.9) against §2.7's third set of pools
  (42/48, 140/144, 47/160), the grid's "pooled 29/32", and the scramble counts.

### N5. Seed-level certainty, network-level fragility

The unit-of-inference statement (§2.9, §3.7, §4) is correct and clearly written. Its
consequence is not carried through. P-values such as 3.4e-59 measure how reproducibly one
deterministic network does the same thing under different noise. A biologist's question is
whether a slightly different network does it. The draft's own data answer that:

- 1% weight jitter, five networks, right-side k/16 for carrier / twin / base from raw:
  16/13/10, 16/5/0, 13/6/3, 14/0/1, 13/13/15. The carrier-vs-twin contrast is absent in two of
  five (Fisher p = .23 and 1.0). In the last set the base is already at 15/16 with the carrier
  in place.
- Dropping 3-synapse pairs abolishes the right-side effect entirely (§4; reproduced).
- A degree-preserving rewire of the carrier's edges flips in one of three draws (§2.7).

The abstract's summary is "gain-robust at its endpoints". The ensemble jitters weights, not
gains, and the title's claim is the carrier-vs-twin contrast, which is an interior comparison.
The floor-4 result is not in the abstract. For scale, the draft's reference 4 perturbs weights
with noise from 0 to 50% and reports rhythms robust to 10% (from a search-result excerpt of its
preprint; I did not read the full text). BANC's own synapse-attachment rate, quoted in §4, is
22%.

### N6. The twin's "p = .008" depends on borrowing base seeds the twin never ran on

All 66 twin seeds were also run on the base arm. On those seeds (`out_p2_stats.txt`, block C):

- twin 30/66 against base 19/66; exact McNemar p = .09
- paired mean-duty difference +.048, bootstrap 95% interval [−.004, +.101]

The abstract's p = .008 appears only when 192 further base seeds are added to the comparator.
The batches are exchangeable by my permutation test, so that pooling is defensible, and the
effect estimate (+.17 in seed proportion) is the same either way. But the claim "intermediate,
not neutral" is a dichotomised reading of a +.05 shift in mean duty whose paired interval
includes zero, it vanishes in the unchopped segment (N2), and the cell removed is silent (N1).
It should not be an abstract-level finding with a p-value.

### N7. The readout sits in near-silent motor pools

Mean pool rates in the scored windows, on the model's 0–1 scale with background .02
(`out_p2_stats.txt` block F, `out_p3_readout.txt`):

- Right tibia flexor pool (101 cells): .014–.027 in every arm, including the un-cut baseline.
  In the base, twin and carrier arms it exceeds the paper's own "active" bar of .05 in 0.5–1.5%
  of scored samples.
- Right tibia extensor pool (12 cells): .026–.034 in the base, twin and carrier arms, above .05
  in 17–26% of samples.

"Antagonist structure" in the arms that carry the headline contrast is therefore the sign of
the correlation between small fluctuations of a flexor pool at background and bursts in a
12-cell extensor pool. That may still be a legitimate model statistic. It is not what a reader
will picture from "tibia antagonist structure", and the draft never reports pool rates. Only
pool means are stored, so a minority of strongly active flexor cells cannot be excluded.

Also still undisclosed from round 1: the other four antagonist pairs are 0/16 in the lesion
arms. And the scramble family: its base is the k=19 prefix, not the k=24 base (the draft does
not say), and its "mass-matched" cohorts carry .0439–.0544 extra mass against the window's
.0642. That shortfall of .0098–.0203 is 1.5 to 3.2 times the carrier's whole mass.

## Scoping, controls and the wet-lab view

**Is the model-class scoping honest everywhere?** In §4 and the last Discussion paragraph, yes.
In the abstract and title, mostly: "in a fly connectome model" is right, "brain-and-nerve-cord
connectome … as a rate model" is not, since the brain is absent. The missing brain input and
missing ascending neurons are not disclosed anywhere (N3).

**Is the mass-matched versus count-matched distinction from Habib et al. crisp?** Not yet. The
four-way contrast in §1(d) is clearly written, and the draft's quotes of their numbers match
the bioRxiv abstract and full-text excerpts I retrieved. But its two supports fail. The claim
that 37 mask cells "carry only a fraction of 37 descending neurons' out-mass" is asserted about
their data, not computed. The 9.72× figure has no referent (N4). And the draft's own currency
matches static weight while ignoring activity (N1), which is the same weakness it attributes to
count matching. Their abstract also states that the model "generates testable predictions for
genetic ablation experiments"; this draft derives none.

**What a Drosophila bench referee would ask for before caring.**

1. A prediction in an intact animal. The only manipulation here that is possible in a fly is
   silencing DNp33 on one side with everything else intact, and the model's answer is "no
   demonstrated effect" (§2.4). The effect needs 24 other descending-neuron types removed first.
   Say so, and say what the intact-animal prediction is, even if it is a null.
2. An assay. For a tibia flexor/extensor claim: leg motor-neuron or premotor calcium imaging in
   the cord, or femur–tibia joint kinematics on a ball, with unilateral DNp33 silencing and
   activation. State whether a driver line for DNp33 exists and what is known about the type.
   My search surfaced no functional study of it.
3. Mirror symmetry. The effect is carried by the left DNp33. The right one is excluded from the
   cohort because it has a few cord inputs at the 3-synapse floor, and deleting it does nothing
   on either side (2/16 right, 2/16 left, from raw). A left–right difference within one
   bilateral pair in one specimen is more likely reconstruction or individual variation than
   cell-type function. The paper should say this.
4. Descending neurons as controlled inputs, not free-running units (N3).

**Related-work gaps** (found by search on 2026-11-21; I read result excerpts, not full texts):

- Li, Ping, Zhang & Wang, bioRxiv 10.64898/2026.08.21.745055: a connectome-constrained
  whole-brain model fitted to calcium recordings, then perturbed at single-cell and
  single-synapse resolution. This is the closest "which cell matters" neighbour with data
  behind the model and belongs in §1.
- Erickson et al., Current Biology, online 2026-11-13, doi 10.1016/j.cub.2026.10.049: one
  descending-neuron pair (DNa10) established by activation, silencing, imaging and connectomics.
  It is the current bench standard for a single-descending-neuron claim and belongs in §1(c).
- Reference 4's weight-noise analysis should be cited as the robustness benchmark (N5).
- Reference 8 lacks volume and pages; another paper's reference list gives Nature 656, 957–970.
  Reference 15 is cited as a 2024 preprint; check for the journal version.

**Prose for a mixed audience.** §1's first paragraph is unreadable cold: four results, ten
bracketed keys and nine all-caps words in 258 words, before the reader knows what a cohort,
a twin or "structure" is. Arm codes run through §2 without a table defining them in plain words (cutwA appears 29
times, cutng25 26 times). §2.7 reports four experiments in the order they were run,
not the order a reader needs. The Discussion is the best-written section and shows the
register the rest should reach. The Sapkal paragraph in §1 reports a failed prediction of the
authors' own in the middle of the introduction; it belongs in Results or Limitations.

## Smaller points and questions

- Preregistration is offered as the paper's answer to fragility (§5). The registrations are
  files in a private tree with no version control; their only timestamps are file mtimes, some
  nine to thirty minutes before the results. Several "preregistered" stages are re-analyses of
  data already stored. A reader cannot verify any of this. Give public timestamps or soften the
  word.
- The base arm's per-batch counts are 3 to 6 of 16 in all 16 batches. Binomial sampling at .28
  predicts more spread (permutation lower-tail p ≈ .003; `out_p2_stats.txt` block D). The void
  rules I read are plumbing checks, not outcome checks, so I have no explanation. Was any batch
  discarded or re-run on the base arm's value?
- The clamp arm pools two arm names; fine, but say so in the table caption, not only in §2.9.
- §2.5 still calls the twin "NEUTRAL"; §2.2 relabelled it.

## The three changes that would most raise my score

1. **Replace the n = 1 silent twin with activity-matched controls.** Run the single-cell scan
   on the k=24 base, report each removed cell's rate and rate × out-weight on that base, and
   restate the control currency. Disclose the twin's .0033 whatever the scan shows.
2. **Show the robustness panel for every headline cell and pick one primary readout.** Re-score
   the dose ladder, scrambles and gain swaps in the unchopped segment and after the high-pass,
   report pool rates beside duty, and re-scope "non-monotone window" and "one scramble supers"
   to whatever survives. Enlarge the weight-noise ensemble (20 or more networks at 1%, 5% and
   10%) and report the carrier-vs-comparator contrast per network.
3. **Make Methods, abstract and Discussion say what the code and §2 say.** State the log1p
   weights and the sign rule; define the closure, the absent brain and the excluded ascending
   neurons; remove the male-ladder sentences, "kill to super", the 9.72× "mass-only band" and
   the release sentence; add one explicit intact-animal prediction or delete the wet-lab
   sentence; redraw the figures from the canonical pools.

## Evidence index (`paper/review_fable_evidence_r2/`)

| file | content |
|---|---|
| NOTES.md | running log |
| 00_sha256_at_start.txt, 01_mtime_snapshot_before.txt, 03_mtime_snapshot_after.txt | pins before any run; file listing after |
| 02_verify_exit_statuses.txt, verify_*.out, verify_l149_rerun2.out | Task 1 |
| snap1/ | draft snapshot reviewed; failing and passing copies of l149_verify.py |
| l149_gate_diff_fail_to_green.diff, draft_diff_a1848d89_to_live.diff | what changed during the review |
| p1_duty_from_raw.py, out_duty_rows.json, out_p1_duty.log | duty per arm × seed from raw traces |
| p2_stats_recompute.py, out_p2_stats.txt | Task 3; twin pairing; batch homogeneity; jitter sets; pool rates; scramble pools |
| p3_readout_anatomy.py, out_p3_readout.txt | pool rates and drive correlation, one batch |
| p4_substrate_census.py, out_p4_substrate.txt | what the subnet contains |
| p5_unchopped_and_envelope.py, out_p5_unchopped.txt | unchopped re-score of every arm; envelope spectrum |
| p6_fig_svg_qa.py, out_p6_fig.txt | figure checks |
| p7_controls_recheck.py, out_p7_controls.txt | §2.7 and §4 cells from raw; contradicting sentences with line numbers |
| p8_cohort_activity.py, p8b_activity_weighted_mass.py, out_p8*.txt, out_p8_census_xmean.json | activity of every ladder cell and of each control's removed cells |

## What I did not do

- No independent re-derivation of the admissibility rule, the bootstrap intervals, the static
  ladder masses, or the floor-3/floor-4 extractions.
- No check of `CLAIM-MAP.md` beyond what the gates assert, and no audit of the 37 references
  beyond the Habib entry and the two noted above.
- No visual inspection of any figure.
- No measurement of single-cell activity on the cut base (would need a rollout).
