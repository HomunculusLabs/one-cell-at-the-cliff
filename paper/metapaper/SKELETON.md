# META-PAPER SKELETON — adversarial cross-family agent review (draft 0)

Status: skeleton, 2026-11-22, writer claude-opus-5.5 (BRIEF_meta.md). Not a
draft. Every number carries a source key; the receipts are the data.

## Source keys (paths relative to /home/t3rpz/critters/peabrain-lab/)

    LL   /home/t3rpz/critters/peabrain/LANE-LOG.md   (LL:n = line n)
    R1   paper/review_fable.md          round 1, fable-5.2, 2026-11-19/20
    R2   paper/review_fable_r2.md       round 2, fable-5.2, 2026-11-21
    SO   paper/review_claudeai_fable_20261121.md  hosted claude.ai fable-5.2
    R3   paper/review_astra_r3.md       round 3, gpt-6.2-astra
    R4   paper/review_opus_r4.md        round 4, claude-opus-5
    RL   paper/RESPONSE-LETTER.md       PA  paper/priorart_terra_20261121.md
    SK   ~/.hermes/profiles/maple/skills/research/adversarial-agent-review/SKILL.md
    EV   paper/metapaper/evidence/  (jobs.tsv + counts.py -> counts.out;
         commits.tsv, releases.tsv = gh API pulls, fetched_at.txt)
    F:x  banc/x/X-FINDINGS.md (or ducklesion/, duckplast/, duckplast2/)

Counts marked [EV:counts.out] are recomputed by `python3 EV/counts.py`.

## Title candidates

1. Gates check numbers, referees check sentences: cross-family model review
   of a connectome-model preprint
2. Rotate the referee: a receipts-first case study of adversarial agent
   review on one computational-neuroscience preprint
3. Adjudicate before believing: five model-referee rounds, thirteen
   referee-run experiments, and the claims that did not survive
4. What four model families missed together: calibrating the yardstick in
   agent peer review (strong if §5's shared-blind-spot result holds up)

Working pick: (1). It names the central finding without overclaiming the
method's generality (we have n = 1 paper).

## Abstract (draft, ~190 words; trim at draft stage)

A rate-model study of a fly nerve-cord connectome was built by a
pre-registered, anchor-certified agent lane with automated verify gates that
check every quoted number against a ledger. The gates were green while the
framing was wrong: three referee reports say so in nearly the same words
[R1:22-23; R2:63-66; SO:40], and the authors' response letter concedes it
[RL:794-795]. We report what happened when the draft was instead attacked by
model referees from rotating families: five review instances from three
model lines across two vendors (fable-5.2 x3 incl. one hosted instance,
gpt-6.2-astra, claude-opus-5) [EV:counts.out], each given the artifact tree
rather than the prose, each adjudicated by recomputation before any fix,
and some re-dispatched as experimenters (13 completed pre-registered
experiments, 8 fable / 5 astra [EV:counts.out]). The title, the central
control and fourteen drafted claims died or narrowed (§3.4); the
verdict moved from major revision x3 to minor [R1:15; R2:20; R3:75; R4:9]. The last referee named a
blind spot all families shared: none audited the outcome band itself
[R4:595-613]. We describe the procedure, its costs, and why model referees
do not replace a human from the field, who has not yet read the paper
[RL:846].

## §1 The problem

1.1 Internal verification certifies values, not inferences.
- The lane's gates (six, later seven scripts) assert number == ledger key,
  frozen abstract contracts, byte-replay of declared edits [RL:783-793].
- R1: "All four verify scripts pass, but they check value-vs-ledger
  equality, not whether claims follow" [R1:22-23].
- R2: "Every problem in Task 4 passes all six" [R2:66]; R2 also caught one
  gate going green by having its pins re-pointed mid-review [R2:54-65].
- SO: the "six verification gates check that numbers match the ledger, not
  that statements are true" [SO:40]. RL: "Every stale sentence listed above
  passes all seven gates" [RL:795-796].
- The R1 critique was adjudicated by the lab itself: 12/12 CONFIRMED at
  least in direction, zero refuted [LL:370]. Every framing defect R1 raised
  was real and had survived ~190 internal ticks (R1 adjudication = tick 189
  [LL:370]).
- Claim for the paper: value-level verification and inference-level review
  are different instruments; the second needs an adversary.

1.2 Same-family review converges — on hits AND on misses.
- R2 (API fable) and SO (hosted fable, own rebuild, own code) converged
  independently on the same three defects: silent mass twin, Methods weight
  rule, fragility [SO:7-10; R2:27-33]. Convergence = replication of hits.
- SO named the family-internal problem itself: "The existing referee round
  was another instance of this same model, so it wasn't independent"
  [SO:67]; lab acknowledged and rotated [LL:418; RL:526-532].
- Items no fable instance raised, raised by other families:
  (a) cross-seed (shift-predictor) test: carrier keeps .6217 of .7581
      chopped duty with flexor/extensor from different seeds; base
      .4077 -> .0971 [R3:57] (astra);
  (b) audit of OUR adjudication: "not seven independent replications"
      [R3:31] (astra);
  (c) the band calibration: SUPER frozen on a damaged substrate; b65
      513/513 .995 vs closure 207/513 [R4:218-244, 595-613] (opus);
  (d) prior-art lineages differ per family: fable-SO -> Alstott 2009
      [SO:42]; astra -> Honey & Sporns, Luccioli, Boes, Prinz [R3:63-65];
      opus -> STG single-cell lineage, shift predictor [R4:452-503].
- HONEST LIMIT (must stay in §1): R1 had already flagged stimulus-envelope
  tracking (median r=+.55) [R1:41-45], an ancestor of (a). Family is
  confounded with round order and draft maturity (514 -> 1,654 lines between
  R1 and R2 [R1:3; R2:4]). §1.2 is suggestive, not a controlled comparison.

## §2 The method (five components; codified in SK)

2.1 Family rotation; hosted instances count once [SK:30-33].
- Route probe before dispatch: FABLE-ROUTE-OK [LL:410], ASTRA-ROUTE-OK
  [LL:419], OPUS-ROUTE-OK [LL:441].
- Reserve one fresh family for the finished object as the final pre-human
  gate and ask it for the shared blind spot [SK:84-86] — R4 did both
  [R4:1, 593].

2.2 Artifact-first refereeing [SK:25-29].
- The reviewable object = draft + number ledger + claim map + runnable gates
  + raw traces, public: 10 commits [EV:commits.tsv], release v0.1-lineage
  5 assets, 1,011,317,322 bytes [EV:releases.tsv]; fresh-clone replicator
  path: six gates green from a zero-context clone [LL:414].
- Referees recompute with their own code: R2 recomputed 44 raw files /
  6,506 rows [R2:92-96]; R3 scored all 37 arms x 16 seeds from raw [R3:35];
  R4 own Wilson/Newcombe/Spearman, imported no lab function [R4:5-7].
- Referees pin shas and disclose drift: R2 [R2:9-12], R4 [R4:20-23].

2.3 Adjudicate before believing [SK:45-49].
- Verdict vocabulary registered first: CONFIRMED/REFUTED/PARTIAL/
  REVIEWER-REPORTED; reviewer probe outputs are claims, not evidence
  [LL:370].
- Tallies: R1 12/12 confirmed [LL:370]; R2 7/7 verifiable confirmed, one
  nit (27/60 not 26/58) [LL:416]; R3 all historical pools reproduced
  [LL:421]; R4 every recompute exact [LL:446].
- Adjudication cuts both ways (keep these; they are the method working):
  our note that SO was wrong about raw traces was itself wrong — "closer to
  right than our own note allowed" [RL:539-543]; R3 downgraded our "7/7" to
  reruns + checks [R3:31].

2.4 Referees as experimenters [SK:56-60].
- A family that reviewed is dispatched on the next pre-registered card,
  same PREREG / anchor (C0A) discipline as internal runs, and scores its own
  predictions. 13 landed, 2 in flight at skeleton time (L202, duckroute)
  [EV:counts.out].
- Self-scored wrong predictions: 14 across 8 experiments [EV:counts.out;
  per-file: F:l175 P3/P4, F:l185 P5, F:l187 P3/P5c, F:l197b, F:l198 P2,
  F:l199 Q5, F:l200 P6, duckplast P1/P2].
- Anchor certs before any new number is read (max diff 0.0): 322 / 368+300
  / 322+48 / 92 / 92+50 comparisons [RL:809-819].

2.5 Receipts public; credit referees [SK:65-67].
- Every report + evidence dir committed alongside the draft
  [EV:commits.tsv rows f00a19e, 4dbfab6, 722a64b]. RL credits referees per
  claim [RL:870-871].

Mechanics to describe in Methods (not novel, but reproducible): self-
contained BRIEF files per referee (e.g. paper/review_astra_r3_BRIEF.md,
paper/review_opus_r4_BRIEF.md); writes confined to report + evidence dir;
<=300-word final answers [SK:39-44]; fold agents CLAIM the scheduler item
before editing [SK:50-55; LL:432].

## §3 The case study (one preprint, 2026-11-19 to 2026-11-21)

3.1 Object. A fly cord connectome rate model; claim: deleting one
descending neuron (DNp33-L) raises right-tibia antagonist duty. Draft size
514 lines at R1 [R1:3] -> 1,654 at R2 [R2:4] -> 2,481 after the master fold
[LL:437] -> 2,694 at skeleton time (wc -l paper/DRAFT.md, 2026-11-22).

3.2 Participants and roles [EV:jobs.tsv, counts.out].

    role                 model line           n   receipts
    referee              fable-5.2            3   R1, R2, SO (hosted)
    referee              gpt-6.2-astra        1   R3
    referee              claude-opus-5        1   R4
    experimenter         fable-5.2            8   F:l175 l185 l187 l197b
                                                  l198 l199 l200 duckplast2
    experimenter         gpt-6.2-astra        5   F:l184 l186 l190
                                                  ducklesion duckplast
    prior art / figures  gpt-6.1-terra        2   PA (28 fetched cites
                                                  [LL:427]); figs 4/5 [LL:444]
    manuscript folds     fable-5.2            5   L183 L190b L197 residue RL
    digest               glm-5.3              1   [LL:427]
    lane cron body       glm-5.3              -   [LL:464]

Correction to the brief: "4 families + 1 hosted instance" holds only if
terra (non-referee) is counted; referee lines are 3, vendors 2. "~20
experiments" is 13 completed + 2 in flight; with the 5 folds and 2 figure
jobs the day's dispatched jobs total 25 [EV:counts.out, 30 rows minus 5
reviews]. Use the measured numbers.

3.3 Verdict trajectory.
- R1 major [R1:15]; R2 major, 6 resolved / 5 partial / 1 unresolved / 0
  regressed of 12 [R2:88]; R3 major, "carrier result HOLDS" [R3:75];
  R4 NEEDS MINOR REVISION, 21 resolved / 3 partial / 2 cosmetic / 1
  unresolved / 0 regressed [R4:9, 169].
- Human gate declared GO after R4 repairs [LL:449]; no human from the field
  has read it [RL:846].

3.4 Claims that died, and what replaced them (core table of the paper).

    # | claim (as drafted)            | killed by       | replaced by
    1 | "mass-twin controls isolate   | R2 N1: twin      | 34-cell scan: carrier
      |  identity"                    | x .0033 intact,  | only SUPER of 34 + 2
      |                               | .0005 cut base   | drive twins [F:l175];
      |                               | [R2:124-140;     | replicated 15/16 fresh
      |                               |  LL:416]         | & fixed gain [F:l185]
    2 | "one cell" / unique           | R1 #1: scramble  | "sufficient, not
      |                               | cutscr0 39/48    | unique" [R4:140]
      |                               | (canon. 41/50)   |
      |                               | [R1:27-33;R2:118]|
    3 | male connectome: no ladder    | R1 #2: floor     | "untested at matched
      |                               | artifact, 342 DNs| floor" [R4:141]
      |                               | K=52 at >=3      |
      |                               | [R1:34-39]       |
    4 | 0.1-Hz "slow line" finding    | R1 #3: it is the | out of headline;
      |                               | 9-s stimulus chop| Methods states chop
      |                               | [R1:40-45]       | [R2:77]
    5 | "two-factor law"              | R1 #10 [R1:87-93]| rebuilt on silW clamp
      |                               |                  | [R2:84]
    6 | non-monotone all-or-none      | R2 N2: unchopped | "the window closes";
      | window                        | k=58 1/258 ->    | Table 4 both readouts
      |                               | 186/258 [R2:155- | [LL:438; R4:351-362]
      |                               | 170]             |
    7 | floor robustness              | R1 #6; floor-4   | failure printed
      |                               | dynamic 0/16 x3  | [R4:145]
      |                               | [R2:80]          |
    8 | Methods: in-degree normalized | R2 N3, SO #2     | log1p(syn) x sign
      |                               | [R2:187-196]     | printed [R4:154]
    9 | twin p=.008 (paired)          | R2 N6; McNemar   | McNemar primary
      |                               | .0895 [R3:28]    | [R4:157]
   10 | endogenous / internal timing  | R3 cross-seed    | "no internal rhythm;
      |                               | .6217/.7581      | locks to tone phase",
      |                               | [R3:57]          | causal shift +.397
      |                               |                  | [F:l197b; F:l199]
   11 | SUPER = regime transition     | R4 M2: b65       | "partial rescue, not
      |                               | 513/513 .995     | a transition" in
      |                               | [R4:218-244]     | abstract [LL:459]
   12 | jitter robustness (5/5 sets)  | R4 M1: set 5     | per-set Table 5
      |                               | base 15/16 SUPER | printed [LL:449]
      |                               | [R4:182-216]     |
   13 | silent cells "deliver nothing"| R4 M4: 8 of 20   | relabel requested
      |                               | fire 2-10%       | [R4:323-325]
      |                               | [R4:294-325]     |
   14 | novelty: location-dependent   | SO #4 Alstott;   | conjunction-only
      | lesion effects; broad priority| PA (28 cites)    | novelty [LL:427;
      |                               | [SO:42; PA:7-9]  | PA:81-87]

Draft-stage TODO: row 13's fold status (check DRAFT.md §2.1 wording at
draft time; not verified for this skeleton).

3.5 Claims the referees STRENGTHENED (keep — the method is not only a
shrinker).
- Carrier vs base in the unchopped segment 0/258 -> 132/210 [R2:35-36].
- Carrier flip at the base's own gain 15/16, +.312, t 4.8 [F:l185 R1].
- Relay occlusion: carrier effect survives relay removal, +.142 chopped,
  1.4-Hz signature +.709 [F:l187 item 3].
- Edge cut 1110->75494 (21 syn) 12/16 SUPER, no 1.4-Hz signature, sham
  5/16 [F:l190] = the bottleneck-vs-distributed dissociation.
- Post hoc, carded not claimed: ru2 double removal 15/16 .783 -> 3/16 .296
  [F:l200; LL:466].

3.6 Method transfer to a second subject (the duck brain).
- Lesion scan on a 139,255-cell / 15,091,983-edge graph: 0/8 decision flips
  from any single clamp incl. twins; whole-pool clamp 0/8 hides vs intact
  4/8 [F:ducklesion]. Same procedure, opposite architecture verdict
  (population readout) = the method does not manufacture bottlenecks.
- Plasticity v1: P1/P2 not supported, 0 reply-intent changes [F:duckplast];
  v2: 0 action flips in 1,536 paired turns [LL:468].
- Agent-raised live-code flag (consolidate_night): code mechanism CONFIRMED
  by direct read, diary evidence UNVERIFIED, fix staged not applied
  [LL:468, 493] — adjudicate-before-believing applied to a side claim.

3.7 Errors the pipeline itself made (owned, all receipted).
- Gate pins re-pointed during folds; receipted, "no assertion deleted"
  stated, checkable [RL:796-800].
- Draft dispatched to R2 with one of six gates red [R2:63].
- Board-ID collision between two engines on one board [LL:433].
- Reference misattribution (entry 42, Rangaraju -> Ona Wu) caught in the
  residue fold [LL:459].
- Brief typo in a cell id caught by the experimenter's re-derivation
  (ru2 = 70994 not 67353) [LL:466].
- Lane claim refuted by a later referee-family experiment: "tone confound
  cleared" [LL:461].

## §4 Costs and limits

4.1 Cost (honest: tokens and dollars were NOT instrumented).
- Wall clock only: R2 review window 10:11-10:30 [R2:4]; R4 pinned 14:22
  [R4:20], landed 14:5x [LL:446]; L185 rollouts 17 min [F:l185 line 4];
  L190 one worker 505 s [F:l190]. The in-session trail runs 10:0x -> 21:5x
  on 2026-11-21 [LL:409, 493].
- Spend was gated by an owner budget window (account pinning until 11-23)
  [LL:464, 492]. Draft-stage TODO: pull provider usage for the window, or
  state that cost is unmeasured. Do not estimate.
- Folding cost: every fold re-runs 7 gates [LL:449]; concurrent writers are
  the one collision the lane cannot repair [LL:433].

4.2 Model referees are not the human bar.
- SO: "an AI person can judge the agent's process but not the neuroscience"
  [SO:67]; RL open item 1 [RL:846]; SK:87-89.
- The meta-paper must not claim the preprint is correct — only that the
  defects listed in §3.4 were found and fixed before a human read it.

4.3 Family count vs coverage.
- Three referee lines, two vendors [EV:counts.out]; the band blind spot
  survived all of them [R4:595-613]. More families is not more coverage
  if every referee receives the same certified tree and the same question
  frame (R4's own structural argument, R4:610-613).
- Coverage proxy to report at draft stage: distinct issue classes first
  raised per round (needs a coded issue list; not yet built — TODO, build
  from R1-R4 major headings + SO 1-5).

4.4 When it is overkill.
- No artifact tree: referees "produce prose opinions" [SK:28-29].
- Small claims with no framing layer (a single measured number).
- Before internal gates exist: R1-class editorial defects (bullets,
  all-caps, abstract length 3,521 chars [R1:20-21]) are cheaper to catch
  with a checklist than a referee.

## §5 Threats to validity — of the METHOD

5.1 n = 1 paper, no control arm. No same-family-only 4-round arm, no
human-only arm, no planted-defect recall test. Family is confounded with
round order, draft maturity, and the prior reports each referee was shown
(delta-check tasks [R2:68-88; R4:132-169]). Proposed fix: planted-defect
study on a frozen draft, family order randomized.

5.2 Non-blind, anchored rounds. Each referee saw earlier reports; only SO
rebuilt from raw tables blind to our pipeline [SO:3-6]. Convergence in
§1.2 may be anchoring, not independent discovery.

5.3 Zero refuted claims. R1 12/12, R2 7/7 confirmed [LL:370, 416]. Either
referees were accurate or adjudication was lenient. The adjudicator was the
same in-session engine that dispatched the referees [LL:410-493]; an
independent adjudication audit happened once (R3:21-31). Report it as a
threat, not as referee accuracy.

5.4 Did the pipeline bias the science?
- Agenda capture: the day's experiment sequence (L175 -> L184 -> L185 ->
  L186 -> L187 -> L190 -> L197b -> L199) was chosen in response to referee
  asks [LL:417, 422, 424, 428]. Each card was pre-registered; the SEQUENCE
  was not. Forking paths live between cards.
- Post hoc results generated in the same day as their follow-ups (L200
  "bombshell" carded as L202, not claimed [LL:466, 493]).
- Shrinkage bias: referees reward hedging; the paper "that survives is
  smaller" [RL:870]. A real effect could be under-claimed. Check: list any
  claim R4 said cost "less than the lab fears" [R4:211-215].
- Shared infrastructure: same artifact tree, same certification frame for
  every referee [R4:610-613].
- Vendor overlap: referees span 2 vendors; this skeleton's writer (opus-
  5.5) is the same vendor and model line-adjacent to R4 (claude-opus-5).
  Disclose in the author note.

5.5 What a human might have caught that no family did — hypotheses to
REGISTER before the human read (score afterwards; do not edit after):
- H1 the band/yardstick question in a first pass [R4:614-615].
- H2 whether a deafferented, brain-input-free substrate says anything about
  flies at all (R4 M9, R4:419) — significance, not correctness.
- H3 wet-lab feasibility: the only doable experiment predicts a null
  [R4:395-399].
- H4 field-specific prior art that model recall and arXiv sweeps both miss
  (pre-arXiv classics were missed until SO [SO:42; SK:61-64]).
- H5 something on none of these lists. Its rate is the real measurement.
Plan: freeze H1-H5 in paper/metapaper/PREREG_human.md (sha recorded) before
the Sauers handoff [LL:449]; score hits after.

## References (verified digests only)

Case-study primary sources (all in the public repo or this tree):
- HomunculusLabs/one-cell-at-the-cliff, commits 2a91f1c..f8600c9
  [EV:commits.tsv]; release v0.1-lineage [EV:releases.tsv].
- Referee reports R1, R2, SO, R3, R4; response letter RL; skill SK.

Literature, fetch-verified in the lab's digests:
- Alstott J, Breakspear M, Hagmann P, Cammoun L, Sporns O (2009). Modeling
  the impact of lesions in the human brain. PLOS Comput Biol.
  doi:10.1371/journal.pcbi.1000408 [PA:37; paper/references.bib:388-397,
  Crossref-copied]. (Role: the prior art the in-window sweep missed.)
- Pugliese et al. (2026). Connectome simulations identify a central pattern
  generator for fly walking. Nature. doi:10.1038/s41586-026-11195-y
  [PA:53; LL:427]. (Role: strongest neighbor found by the terra dig.)
- Habib, Petr & Rust (2026). Focal neuronal loss and cell replacement in a
  connectome model of fly steering. bioRxiv. doi:10.64898/2026.10.26.762043
  [PA:41; RL:536-538]. (Role: missed by SO, resolved by the lab.)
- Bey et al. (2026). Testing hypothesized neural substrates with lesions.
  bioRxiv. doi:10.64898/2026.11.18.767704 [PA:31]. (Role: matching does not
  automatically resolve confounding [PA:87].)

NOT citable yet (memory-only or unfetched; SK:71-72 forbids):
- every R4 §4 item (R4 itself: "I have not fetched them" [R4:446-448]);
- R3 §5 items not in PA (Honey & Sporns 2008, Luccioli 2014, Soloperto
  2016, Boes 2015, Prinz 2003) — RL lists them as owed [RL:857-858];
- ALL literature on LLM-as-reviewer / automated peer review: no verified
  digest exists in this tree. Draft-stage card: fetch-verify a related-work
  set before §1 is written. Nothing from model memory.

## Draft-stage cards (seeded here, not dispatched)

- M1 build the coded issue list (R1-R4, SO) -> per-round first-raise table
  (§4.3 coverage proxy).
- M2 freeze PREREG_human.md (§5.5) before the human handoff.
- M3 pull provider usage for the burn window or declare cost unmeasured.
- M4 related-work fetch-verify sweep (agent review / LLM referees).
- M5 verify row 13 fold status in DRAFT.md; re-read §3.4 against the draft
  at draft time.
