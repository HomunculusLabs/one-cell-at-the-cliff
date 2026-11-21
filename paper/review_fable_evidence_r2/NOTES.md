# Round-2 referee running log (fable 5.2)

Start: 2026-11-21 10:11 EST. Interpreter for all probes:
~/critters/peabrain/.venv/bin/python (torch+numpy, no scipy), CUDA_VISIBLE_DEVICES="".
All writes confined to paper/review_fable_r2.md and paper/review_fable_evidence_r2/.

## 10:11 pins (00_sha256_at_start.txt)
- DRAFT.md a1848d890195bb25a34b... 1,654 lines / 108,031 bytes — matches the brief. Copy kept at snap1/DRAFT.md.a1848d89.
- numbers.json 238bf2d3..., CLAIM-MAP.md 64ecc3d8..., references.bib 9ff16bbd...
- l149_verify.py was 9934180c... at 10:11:51.

## 10:12 Task 1 — six verify scripts (02_verify_exit_statuses.txt, verify_*.out)
- l143 exit 0, l158 exit 0, l159 exit 0, l161 exit 0, l174 exit 0.
- l149 exit 1: AssertionError at line 2183, "(24) identifier digits removed != the declared lane IDs".
  Checks (1)-(23) printed green before the failure.
- OBSERVED: l149_verify.py changed under me. sha 9934180c... (10:11:51, mtime 10:11:45) ->
  4a580136... (mtime 10:12:13, 174,531 bytes) by the time it ran. Somebody is editing the gate
  while the review runs. DRAFT.md and numbers.json unchanged across the run. Snapshot of the
  failing version kept in snap1/. Will re-run l149 later and record every state seen.
- l158 has a write path (creates banc/l174b2/abstract_pin_b2.txt if absent). File existed
  (Nov 20 23:52) so the branch did not fire; checked before running.
- mtime snapshot of paper/ and banc/ taken before the runs: 01_mtime_snapshot_before.txt.
- Brief's paraphrase of the 12 round-1 majors does not match review_fable.md in places
  (e.g. brief #9 "lesion arms 0/16 both sides unreported" vs actual #9 "readout scope").
  Delta-check uses review_fable.md's wording, as the brief instructs.

## 10:13-10:16 Task 3 — headline statistics from RAW traces
- p1_duty_from_raw.py: own duty implementation (rolling Pearson via sliding windows) over every
  banc/*/raw_l*.npz with tibia traces -> out_duty_rows.json (6,506 arm x seed rows, 44 files).
- p2_stats_recompute.py -> out_p2_stats.txt. Own Wilson / Newcombe / Fisher (log-gamma form).
  - A: all 14 canonical pooled cells of DRAFT 2.9 MATCH (k, n, Wilson, mean duty), using the lab's
    list of 38 admissible files. carrier 203/210, twin 30/66, base 72/258, silW 78/98, etc.
    0 inconsistent repeat seeds.
  - B: all 12 difference rows MATCH (d, Newcombe CI, Fisher p).
  - C: NEW. All 66 twin seeds were also run on the base arm. Same seeds: twin 30/66 vs base 19/66,
    exact McNemar p = .09; unpaired on those seeds d = +.167 [+.002,+.319], Fisher p = .07; paired
    mean-duty difference +.048, bootstrap [-.004,+.101]. The abstract's p = .008 exists only when
    192 base seeds the twin never ran on are added to the comparator.
  - D: batches look exchangeable (permutation chi-square p .22-.82) EXCEPT cutwA is under-dispersed:
    16 batches all 3-6 of 16 (chi2 4.3 on 15 df, upper-tail p .9975 => lower tail ~.003).
    Checked for an outcome-based void rule: PREREG void clauses I read (l169, l169c2, l169d) are
    bit-identity/plumbing only. Unexplained; reported as a question, low weight.
  - E: 1%-jitter sets from raw (right side k/16): carrier vs twin vs base =
    j1 16/13/10, j2 16/5/0, j3 13/6/3, j4 14/0/1, j5 13/13/15. Carrier-vs-twin Fisher p:
    .23, 7e-5, .03, 5e-7, 1.0. In j5 the k=24 base is already 15/16 without touching the carrier.
  - F: tibia pool mean rates in the scored windows (0-1 scale, BG .02, "active" bar .05):
    flexor R .014-.027 in every arm; extensor R .026-.034 in the cut/carrier/twin arms,
    .13-.20 in b65/full/cut58.
  - G: scramble arms under the paper's own canonical rule: cutscr0 = 41/50 (R), 37/50 (L). The draft
    prints 39/48 and 35/48 (abstract, 1, 2.2, 5). The lab's own l172/stats.out also has 41/50.
- p3_readout_anatomy.py -> out_p3_readout.txt (batch L raw traces): in cutwA / twin / carrier the
  flexor pool mean is above .05 in 0.5-1.5% of scored samples (5th-95th pct .017-.037 on base);
  extensor above .05 in 17-26%. Flexor corr with the drive ~0, extensor +.18..+.33.
  Caveat: only pool means are stored, so a minority of strongly active flexor cells cannot be excluded.
- p5_unchopped_and_envelope.py -> out_p5_unchopped.txt. Same statistic scored in the unchopped
  1.4-Hz segment, canonical pools:
    b65 513/513 | full 0/513 | cutk5 0/226 | k19 0/178 | k23 0/82 | cutwA 0/258 | twin 0/66 |
    carrier 132/210 | k26 37/66 | k29 108/194 | k58 186/258 | cutscr0 9/50 | cutscr1 0/34
  => k=58 goes from 1/258 (published, "kills again") to 186/258; intact closure 207/513 -> 0/513;
     the one scramble that "supers" (41/50) -> 9/50; twin "intermediate" -> 0/66 (= base 0/258).
  Envelope spectrum: dominant non-DC line .100 Hz (rel 1.0), .1167 Hz at .47 — the draft's
  re-attribution reproduces.

## 10:17 code-vs-Methods checks
- banc/l135_run.py build(): vals = log1p(syn_count) * sign; glutamate forced negative; inhibitory
  x BETA. grep for normal/indeg in l135_run.py, l169d_run.py, l173_methods.py: no normalization of
  weights anywhere (l169d only asserts in-degree preserved by the rewire). banc/l173/methods.json
  contains neither "normal" nor "log1p". DRAFT 3.1 says "Edge weights are in-degree normalized
  ... [l173.model]" — not what the code does, and not in the key it cites.
- build_graph_banc.py NT_CLASS: gaba/histamine -1; dopamine/serotonin/octopamine +0.2; tyramine and
  unknown +0.3. Not in Methods.
- p4_substrate_census.py -> out_p4_substrate.txt: cord_mask = sensory + VNC-intrinsic + motor with
  region == ventral_nerve_cord = 20,521. Ascending classes (1,840 + 509 + 5) are excluded.
  n_old 21,249 (= 20,521 + 728 cord-receiving DNs) is arm "b65"; n_new 21,809 adds 560 DNs that
  project to the cord and receive NO cord input ("pure projectors") — every cohort arm cuts from
  those 560. DRAFT 3.1 describes only n_old. No brain neuron is simulated.
- "rank (34/58)" in DRAFT 2.3 (line 706) has no ledger key; ladder rank is 25 everywhere else.

## 10:20 l149 re-run
- l149_verify.py changed again (sha 9595db3d..., mtime 10:18:47); exit 0, 28 checks green.
  DRAFT.md still a1848d89. Diff fail->green saved (l149_gate_diff_fail_to_green.diff, 361 lines):
  pins re-pointed for the batch relabel (B26 -> batch A, etc.; token counts 400->395, 247->243).
  banc/l174b4iiib/ is being written live (files stamped 10:19-10:20): the lane agent is mid-stage.
  So the 10:12 red was the gate lagging the draft's 10:08 edit, and it went green by editing pins.

## 10:21-10:27 figures, controls recheck, neighbours, cohort activity
- p6_fig_svg_qa.py -> out_p6_fig.txt. Published figure files unchanged since round 1 (l136 PNG 11-18,
  no SVG; l152 SVG 11-19 21:46; l160 SVG 11-19 20:50). Dark background #282c34. At 6.5-in width text
  is 3.5-4.3 pt (l152) and 2.8-3.1 pt (l160); 98-100% of text under 7 pt.
  fig_l152.svg <text> labels carry superseded pools: cutwA "43 of 144", silW "28 of 32", cutng25
  "124 of 128", eOutMot "21 of 32", eMotTop5 "14 of 32", eMotBot5 "8 of 32"; the withdrawn word
  "inert"; lane tag "L152". Draft table has 72/258, 78/98, 203/210, 21/34, 31/98, 25/98.
- DRAFT.md changed at 10:20:34 -> sha d76fa7d6..., 1,673 lines. diff vs my a1848d89 snapshot
  (draft_diff_a1848d89_to_live.diff): one 19-line changelog paragraph (v3.30) added to the banner;
  body byte-identical. All my line numbers are for the a1848d89 snapshot (live = +19 in the body).
- p7_controls_recheck.py -> out_p7_controls.txt: every 2.7 / 4 control cell reproduces from raw on
  the fresh 16 seeds (gain-swap 2x2, XOR swap, three rewire draws, hom, three f4 arms, both sides).
  Abstract = 1,916 flattened chars. Same file lists the abstract/Discussion sentences that
  contradict the body (male ladder lines 476/1513 vs 869; "kill to super" 465; release 481 vs 1554;
  wet-lab 1465 vs 1539; "own removal mass" 619/1505; "13 entries" 1563; "(34/58)" 706).
  Unchopped re-score of the control cells: n25gW 2/16 and n25gP 4/16 against 9/16 for the same
  graph at its own gain; rew2 8/16 (published 1/16).
- p8 / p8b -> out_p8_cohort_activity.txt, out_p8b_activity_weighted.txt, from the lab's stored
  l137 census (intact closure, ONE seed 3101, all 58 ladder cells):
  carrier 1110 x_mean .454; twin 319 x_mean .0033 (137x lower). 26 of 58 ladder cells are above
  the .05 "active" bar, 20 are below .01, two sit at the RMAX ceiling (736 .999, 585 .986).
  LAB-INTENT.md line 6386-6387 already calls 319 "the SILENT twin (x_mean .0033)"; results_l137.json
  labels the sil319 arm "near-vacuous". The draft and numbers.json carry only the carrier's .454.
  Scramble cohorts = the k=19 prefix + 10 other cells (not the k=24 base); 3-4 of each 10 are silent.
  NOT checked: the twin's activity on the cut base (not stored; no rollouts allowed).
- Web (search snippets only, full texts not read): Habib et al. abstract/numbers match the draft's
  quotes (57.4% / 101.0% / 62.5 / 10.1 / 60.0 / 6.7) and state that the model "generates testable
  predictions for genetic ablation experiments". Not cited by the draft: Li, Ping, Zhang & Wang,
  bioRxiv 10.64898/2026.08.21.745055 (fitted whole-brain model perturbed at cell and synapse
  resolution); Erickson et al., Curr Biol 2026, doi 10.1016/j.cub.2026.10.049 (DNa10, one DN pair,
  activation + silencing + imaging). Pugliese et al. (the draft's ref 4) report weight-noise
  robustness "up to 10%" on sigma 0-50%; this draft's ensemble is 1%. Minnick et al.'s reference
  list gives Bates et al. as Nature 656, 957-970 (2026); draft ref 8 has no volume/pages.
- No version control under peabrain-lab (git: not a repository). PREREG.md timestamps are file mtimes.

## 10:28 close-out
- Report written: paper/review_fable_r2.md. Verdict: major revision. Delta-check 6 resolved /
  5 partial / 1 unresolved / 0 regressed.
- Counts used in the report re-measured on the a1848d89 snapshot: 430 banner lines before the title;
  222 all-caps tokens (>=4 letters) between the abstract and section 5 (126 distinct, 212 without BANC);
  section 1 first paragraph = 258 words, 10 bracketed keys, 9 all-caps words.
- 03_mtime_snapshot_after.txt vs 01_...before.txt: files that changed outside my output locations
  during the window = DRAFT.md, CLAIM-MAP.md, l149_verify.py, review_fable_r2_dispatch.log,
  banc/l174b4iiib/{caps_partition_amend.json, draft_post.md, sec29.py, verify_push.py}. None of my
  commands write to those paths (my probes write only into this directory; verify scripts were
  grepped for write calls first; l158's pin file kept its Nov 20 23:52 mtime).
- Not done: admissibility rule re-derivation; bootstrap CIs; static ladder masses; floor extractions;
  CLAIM-MAP audit; reference audit beyond Habib; any vision; any rollout.
