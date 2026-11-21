# Claim → artifact map (release README)

Every number quoted in `paper/DRAFT.md`, mapped to the run that produced it,
the stored artifact it was extracted from, and the verify step that certifies
it. Research-only (L161); the owner release decision for L152 is untouched.

## Path roots

- banc/... and paper/... paths resolve under `~/critters/peabrain-lab/`
- peabrain-figs/... paths resolve under
  `~/.hermes/profiles/maple/playground/website/publish/`
  (the private miso/workshop repo's served tree — same place the digest lives)
| Title + abstract (v3.32, master fold) | the measured contrast and its control ladder: one of 34 single-cell deletions lifts the readout; mass, delivered-drive, class-and-sign and signed-current comparators stay low; two batches; fixed gain; gain-only null; cross-seed and 1.4-Hz panels; sufficiency, not uniqueness | l175.scan l175.null l185.r1 l185.r2 l185.r3 l184.threepanel l184.design l172.pooled l187.arms | B43, B44, B45, B47 |
| §2.1 the single-cell scan (Table 1) | 34 window cells + 2 drive twins, three readouts per arm; only the carrier reaches the super class; the mass twin is silent; the null is wide and covaries with gain | l175.scan l175.null l175.branch l175.census l175.meta l175.certs l175.bands l175.verdict l184.threepanel | B43, B44 |
| §2.2 replication, gain-only null, signed-current twin (Table 2) | the contrast replicates at fixed and re-matched gain; neither edge-of-band cell promotes; the base moves between 8 and 2 of 16 on gain alone; the signed-current twin does not flip | l185.base l185.r1 l185.r2 l185.r3 l185.meta l185.certs l185.branches l187.sc40_pooled | B45 |
| §2.3 shared timing, not rate | cross-seed pairing, pool rates, harmonic amplitudes, template subtraction, anatomy of the carrier's outputs | l184.threepanel l184.q1 l184.q1_twins l184.q3 l184.q3_ratios l184.sens l184.anatomy l184.design | B44 |
| §2.4 the downstream interneuron (Table 3) | relay cut / clamp, push-pull, occlusion: neither registered pole; the 1.4-Hz panel separates carrier-absent from carrier-present arms | l187.base l187.arms l187.contrasts l187.fast l187.relay l187.relay_rate l187.g74914_rate l187.gain_slopes l187.meta l187.certs l187.branches l187.sc25_pooled | B47 |
| §2.5 which clock (gate-jitter) | UNRESOLVED and underpowered by construction (window overlap) | l186.means l186.contrasts l186.branch l186.power l186.phase | B46 |
| §2.6 Table 4 + §2.7 paired twin + §3.1 substrate and weights | the ladder in the continuous segment; paired McNemar on the twin's own seeds; the deafferented closure; signed log1p weights with the glutamate override | l183.ladder_fast l183.ladder_fast_meta l172.paired_twin l92.substrate l135.weights | B48 |

## Conventions

- DRAFT quotes `value [key]`. `key` is either a top-level key of
  `paper/numbers.json` (145 keys) or a dotted subkey walk into one
  (resolver = paper/l149_verify.py §1). Multi-key brackets
  `[a, b]` split on commas.
- `paper/numbers.json` is regenerated ONLY by `paper/extract_numbers.py`
  from stored run jsons (L44 rule: never from log prose). Each entry
  carries its `src` (`artifact:subpath`); `paper/l161_verify.py` re-walks
  every walkable src and value-compares against the stored artifact.
- Raw rollouts: each dynamic lane stores `raw_lNNN.npz` (+ `anchors_run.json`
  bit-identity chain) the moment it finishes; C0A anchors certify re-runs
  bit-identical against them.

## §-by-§ claim table (draft locus → keys → block)

| Draft locus | Claim | numbers.json keys (root) | Block |
|---|---|---|---|
| Abstract R1 / §1 R1 / §2.1 | U-law dose cliff at matched operating points | pooled.cutk5 cutng19 cutwA cutng25 cutng29 cut58 full; xor + xor.steps; subnet; n_runs_summed | B1 |
| Abstract R2 / §1 R2 / §2.2 | identity-not-mass twin XOR | xor (+ pair_delta); pooled.cutng25 cutng25p; l150.pooled (+cutng25_8batch, cutwA_9batch) | B1, B10 |
| Abstract R2 / §1 R2 / §2.2 | scramble controls: set-dependent SUFFICIENCY (not uniqueness) | l168.scr l168.base l168.window_mass l168.verdict | B19 |
| Abstract R2 / §2.4a | substrate-gated activity flip | l137.sil24 l137.g1 l137.g3 l137.g2 l144.silf l144.silw l150.pooled (+silW_B30_B33) l150.h1 l151.sheet l151.crossed l151.verdict l137.vol1110 l137.pooled_full | B2, B6, B10, B11 |
| Abstract R2 / §2.4b | edge footprint + bit-identity | l142.h2a h2b h3 aeall pooled ti window; l145.dose mot motin pooled (+eOutMot_B29_B31); l148.eall h_id pooled seid; l150.pooled (+eMotTop5/eMotBot5_B31_B33) | B5, B7, B9, B10 |
| Abstract R3 / §2.5 | gain ensemble: endpoints hold, interior re-draws | sustain.cutng23 cutng25 cutng25p cutng29 cutwA; gains.full.spread; jitter_note; full_kR_sets | B4 |
| §2.7 | pre-posting control: flip tracks the GRAPH, not the gain (2x2 swap) | l169.grid l169.swap_legs l169.branch l169.af l169.pooled l169.nt | B20 |
| §4 DATA FLOOR | the f4 floor read is fully re-derived (K, cohort, order) | l169b.forms l169b.scope | B21 |
| §4 DATA FLOOR | the dynamic floor-4 arm does NOT transfer the R-side cliff (branch G2); left-side read is descriptive only | l169b2.dyn l169b2.lat_descriptive | B22 |
| §2.7 | design pins for the queued rewire / contralateral-DNp33 arms: footprint mirror, not a cohort mirror; rewire admissible | l169c.design | B23 |
| §2.7 | displacement is not removal (rewire draws bracketed by the carrier-INTACT base, R2+R3 conjunction); the same-footprint different-class deletion does not flip (H1) | l169c2.base l169c2.rew l169c2.branch l169c2.gains l169c2.hom l169c2.cert | B24 |
| §2.7 | the XOR pair run fully crossed against both bisected gains: identity wins in BOTH gain columns (branch E1) | l169d.grid l169d.legs l169d.branch l169d.xbatch l169d.cert | B25 |
| §3 Methods | the model, protocol and definitions, every constant PARSED from source; the update equation certified against the run script's own lines | l173.model l173.protocol l173.defs | B29 |
| §2.4 lead arm / §3.8 identities | silW is the ONE flip arm at an unchanged gain; every edge-cut flip arm moves the gain +1.06..+1.30%; the two bit-identities relocated to Methods; the mass ratio corrected to 9.72x | l173b.gains | B30 |
| Abstract scope / §2.6 | cross-connectome boundary, re-scoped at the matched synapse floor (branch M1); UNTESTED AT MATCHED FLOOR, design pins stored | l138.male_s1 l138.male_s2_dnp33 l138.banc l170.matched l170.pins | B3, B26 |
| Abstract result 4 / §1 map / §2.8 / §3 Methods / §4 | the slow line is STIMULUS-SET (envelope line .100 Hz) and the identity contrast survives both re-scores (branch B2_preserved) | l171.envelope l171.panel | B27 |
| Abstract / §1 map / §2.1 / §2.2 / §2.4 / §2.9 / §4 | ONE canonical unique-seed pooled count per arm, differences with intervals, bootstrap CIs, unit of inference; twin relabelled INTERMEDIATE (P4 refuted) | l172.pooled l172.diffs l172.census_unique l172.meta | B28 |
| Abstract R4 / §1 R4 / §4 | band-relative frequency honesty + carrier subset | l156.pooled l154.band l157.pooled | B13, B14, B15 |
| §1 Sapkal amendment | deafferentation direction NOT met; structure survives | l154.freq l154.structure | B13 |
| §2.3 | carrier anatomy (observation, no keyed numbers) | — (sources: `banc/l134/static.json`, `banc/l137/static.json`) | B18, B2 |
| §4 DATA FLOOR | implicit 3-syn release floor; f4 admissibility | l146.release l146.f4 | B8 |
| Fig 1 | dose + XOR figure | draw-time asserts vs `banc/l136/plot_data.json` | B1 |
| Fig 2 | clamp-vs-cut grid figure | draw-time asserts vs numbers.json | B12 |
| Fig 3 | carrier-census figure | draw-time asserts vs `banc/l157/static.json` | B16 |
| References | 37 entries primary-source verified; entries 14-37 copied from stored live API records; bidirectional in-text citation gate | `paper/references.bib` `banc/l174a/refs.json` `banc/l174b/refs_b.json` | B12, B31, B32 |
| §2.4 editorial | reviewer I10's substantive asks were already shipped (silW lead, identities in §3.8, sil24 non-separability); the residue was length, closed by de-duplication at zero claim loss | — (no keyed numbers: string/char arithmetic over `banc/l174b3/`) | B34, B30 |
| Abstract/§1 prose gates | numeric vocabulary freeze + sentence length | — | B17 |
| Abstract compression (v3.22) | <= 1,920 chars, no citation keys, no caps, no arm codes; every dropped cell relocated to the body; 19-row claim->key trace table; hash pin | — (sources: `banc/l174b2/abstract_v321.txt`, `banc/l174b2/abstract_pin_b2.txt`) | B33 |
| §1-§2.3 prose (v3.24) | 15 bullet lines converted to prose as a FORMAT-ONLY transform: both token multisets identical to the frozen pre-image, 184/184 verifier literals verbatim, scramble block byte-unchanged | — (sources: `banc/l174b3b/span_pre.txt`, `banc/l174b3b/literals.json`) | B35 |
| §2.5/§2.6/§2.8 prose (v3.25) | 11 more bullet lines converted to prose under the same FORMAT-ONLY contract: both token multisets identical (411 numeric, 37 keys), 229/232 verifier literals verbatim with three declared wrap-fragile ones normalized, §2.7 proven BYTE-IDENTICAL inside the same edit span, the robustness-panel table still a table | — (sources: `banc/l174b3bii/span_pre.txt`, `banc/l174b3bii/sev_pre.txt`, `banc/l174b3bii/literals.json`) | B36 |
| §2.7 prose (v3.26) | the last 16 bullet lines in §1-§2 converted to prose under the same FORMAT-ONLY contract: both token multisets identical (248 numeric, 22 keys), 159/166 verifier literals verbatim with seven declared wrap-fragile ones normalized, the two non-bullet "Design pins" literals still BYTE-exact (the raw-passthrough proof), the longest sentence cut 67 -> 52 words under a new §2.7-scoped 60-word gate | — (sources: `banc/l174b3biii/span_pre.txt`, `banc/l174b3biii/literals.json`) | B37 |
| §4 prose (v3.27) | §4's 10 bullet lines converted to prose and its seven >60-word sentences split at their own clause boundaries, so §1-§4 carries no list item: both token multisets identical (166 numeric, 18 keys), the section's CONTENT-WORD SEQUENCE identical under all thirteen declared edits, 135/140 verifier literals verbatim (three wrap-fragile, two bullet-MARKER slice locators re-pointed at the line-start prose form), longest sentence 107 -> 53 words under a new §4-scoped gate, §2.8's 70-word sentence disclosed and deferred | — (sources: `banc/l174b4i/span_pre.txt`, `banc/l174b4i/literals.json`, `banc/l174b4i/emit_report.json`) | B38 |
| all-caps de-emphasis of §1 + §4 (v3.31) | the two pure-prose sections carry no all-caps emphasis: 64 declared occurrences (26 in §1, 38 in §4) lowered to the house form §5 already uses, with the outcome-class labels becoming lowercase defined terms; PROVED CASE-ONLY over the whole draft (title-onward length identical, exactly 412 differing bytes, every one an uppercase letter replaced by its lowercase self), so the visible-character and byte deltas are exactly zero and both multisets are identical with no named removal and no named addition; §2 Results and everything from §5 onward byte-IDENTICAL; premise finding — §5 carries zero caps tokens and is the style reference, §3 Methods hosts MODEL SYMBOLS plus one position-split token so its slice is deferred | — (sources: `banc/l174b4iiic/draft_pre.md`, `banc/l174b4iiic/census.json`, `banc/l174b4iiic/scope.json`, `banc/l174b4iiic/plan_i.json`, `banc/l174b4iiic/emit_report.json`) | B42 |
| batch-code relabel + the §3.7 mapping (v3.30) | the `B<n>` shape splits into three classes the frozen partition had conflated: 19 prose batch codes (11 distinct) now carry the reader-facing labels A-L assigned in RUN ORDER with I and O skipped, 6 occurrences inside stored artefact keys stay byte-exact because they are filenames, and 4 preregistered BRANCH labels are declared out of scope; §3.7 Methods gains the bijective mapping as the one declared home of the internal codes; a letter scheme adds no digit run, so the measurement multiset is identical with no removed-run disclosure needed and every removed identifier run is a declared relabel; pre-image + the declared edits == the live draft byte for byte from the title onward | — (sources: `banc/l174b4iiib/draft_pre.md`, `banc/l174b4iiib/classify.json`, `banc/l174b4iiib/emit_report.json`, `banc/l174b4iiib/caps_partition_amend.json`) | B41 |
| lane-ID strip + the §6/§7 premise finding (v3.29) | §1-§6 and the References preamble carry no lane identifier and no internal-artefact reference: 13 declared edits (five subsection-heading parentheticals, §2.2's bold lead, one deleted stage pointer, one re-pointed §2.9 cross-reference, the log/script-tree renames, the sweep date's file citation) with pre-image + the 13 edits reproducing the live draft byte for byte, the measurement multiset and citation keys identical, and the 15 removed identifier digit runs asserted by name; §6 stays a data-availability list and §7 stays out of manuscript scope by registered premise; the all-caps judgement is frozen as a partition of 179 distinct tokens (18 keep / 23 defer / 138 strip) with zero applied | — (sources: `banc/l174b4iii/draft_pre.md`, `banc/l174b4iii/caps_partition.json`, `banc/l174b4iii/census.json`, `banc/l174b4iii/emit_report.json`) | B40 |
| §5 Discussion (v3.28) | the manuscript's Discussion, authored as §5 between §4 and the renumbered data note (§6) / author notes (§7): 825 words over 7 paragraphs, born clean (no list item, lane ID, batch code, all-caps token, provenance key or NEW numeric value — every number it quotes appears verbatim elsewhere in the draft), both §1 novelty narrowings restated, carrier stated as sufficient-not-only, robustness reported as the endpoints/interior split, under its own 60-word rule at 52; and §2.8's inherited 70-word sentence CLOSED by one declared content-preserving split that is byte- and visible-neutral (70 -> 56 words, all 69 literals verbatim, zero exceptions) | — (sources: `banc/l174b4ii/s28_pre.txt`, `banc/l174b4ii/s28_post.txt`, `banc/l174b4ii/disc.txt`, `banc/l174b4ii/literals.json`, `banc/l174b4ii/emit_report.json`) | B39 |

## Lane blocks

### B1 — L135+L136: dose ladder, identity XOR, Fig 1
- scripts: `banc/l135_build.py` `banc/l135_run.py` `banc/l135_static.py`
  `banc/l135_verdict.py` `banc/l135/l135_precheck.py` `banc/l136/l136_extract.py`
  `banc/l136/l136_table.py` `banc/l136/l136_fig.py` `banc/l136/l136_qa.py`
  `banc/l136/l136_publish_verify.py`
- artifacts: `banc/l136/plot_data.json` `banc/l136/table.md`
  `banc/l135/results_l135.json` `banc/l135/raw_l135.npz`
  `banc/l135/anchors_run.json`; PREREG `banc/l135/PREREG.md`
- published: `peabrain-figs/l136_transition_law.png` `peabrain-figs/l136_table.md`
- verify: `paper/l143_verify.py` §1–§3; `paper/l149_verify.py` §1–§3;
  `banc/l136/l136_publish_verify.py`; draw-time asserts in `banc/l136/l136_fig.py`
- keys: pooled.cutk5 pooled.cutng19 pooled.cutwA pooled.cutng25 pooled.cutng25p pooled.cutng29 pooled.cut58 pooled.cutng23 pooled.cutng26 pooled.full subnet n_runs_summed xor dose_l135 l135.pooled

### B2 — L137: clamp family on intact subnet (batch B27)
- scripts: `banc/l137_build.py` `banc/l137_precheck.py` `banc/l137_run.py`
  `banc/l137_static.py` `banc/l137_vbuild.py` `banc/l137_verdict.py`
- artifacts: `banc/l137/results_l137.json` `banc/l137/static.json`
  `banc/l137/raw_l137.npz` `banc/l137/anchors_run.json`; PREREG `banc/l137/PREREG.md`
- verify: `paper/l143_verify.py` §2–§3; `paper/l149_verify.py` §3 (grid table)
- keys: l137.g1 l137.g2 l137.g3 l137.sil24 l137.pooled_full l137.vol1110

### B3 — L138: cross-connectome boundary (MaleCNS mirror, static)
- scripts: `banc/l138_probe.py` `banc/l138_static.py`
- artifacts: `banc/l138/static.json`; PREREG `banc/l138/PREREG.md`
- verify: `paper/l143_verify.py` §3
- keys: l138.banc l138.male_s1 l138.male_s2_dnp33

### B4 — L139: gain-jitter ensemble (5 af-matched sets + base)
- scripts: `banc/l139_build.py` `banc/l139_precheck.py` `banc/l139_run.py`
  `banc/l139_driver.sh` `banc/l139_verdict.py`
- artifacts: `banc/l139/results_l139.json` `banc/l139/raw_l139_j0.npz`
  `banc/l139/raw_l139_j1.npz` `banc/l139/raw_l139_j2.npz` `banc/l139/raw_l139_j3.npz`
  `banc/l139/raw_l139_j4.npz` `banc/l139/raw_l139_j5.npz` (+ anchors_j0..j5);
  PREREG `banc/l139/PREREG.md`
- verify: `paper/l143_verify.py` §3
- keys: sustain.cutng23 sustain.cutng25 sustain.cutng25p sustain.cutng29 sustain.cutwA gains.full.spread jitter_note full_kR_sets

### B5 — L142: carrier edge ladder (batch B29)
- scripts: `banc/l142_build.py` `banc/l142_run.py` `banc/l142_static.py`
  `banc/l142_static_build.py` `banc/l142_vbuild.py` `banc/l142_verdict.py`
- artifacts: `banc/l142/results_l142.json` `banc/l142/static.json`
  `banc/l142/raw_l142.npz` `banc/l142/anchors_run.json`; PREREG `banc/l142/PREREG.md`
- verify: `paper/l149_verify.py` §2–§3; `paper/l143_verify.py` §2–§3
- keys: l142.h2a l142.h2b l142.h3 l142.aeall l142.pooled l142.ti l142.window

### B6 — L144: silW substrate-gated flip (batch B30)
- scripts: `banc/l144_build.py` `banc/l144_run.py` `banc/l144_verdict.py`
- artifacts: `banc/l144/results_l144.json` `banc/l144/raw_l144.npz`
  `banc/l144/anchors_run.json`; PREREG `banc/l144/PREREG.md`
- verify: `paper/l149_verify.py` §3 + §6
- keys: l144.silf l144.silw

### B7 — L145: motor-sheet dose halves + combo (batch B31)
- scripts: `banc/l145_build.py` `banc/l145_run.py` `banc/l145_static.py`
  `banc/l145_static_build.py` `banc/l145_verdict.py`
- artifacts: `banc/l145/results_l145.json` `banc/l145/static.json`
  `banc/l145/raw_l145.npz` `banc/l145/anchors_run.json`; PREREG `banc/l145/PREREG.md`
- verify: `paper/l149_verify.py` §3 + §6; ranking-defect correction pinned in
  `banc/l150/static.json` (see §3 data-integrity note in DRAFT)
- keys: l145.dose l145.mot l145.motin l145.pooled

### B8 — L146: release synapse floor (static)
- scripts: `banc/l146_static.py` `banc/l146/release_floor_addendum.py`
- artifacts: `banc/l146/static.json`; PREREG `banc/l146/PREREG.md`
- verify: `paper/l149_verify.py` §4
- keys: l146.release l146.f4

### B9 — L148: se0 ≡ eAll bit-identity (batch B32)
- scripts: `banc/l148_build.py` `banc/l148_precheck.py` `banc/l148_run.py`
  `banc/l148_verdict.py`
- artifacts: `banc/l148/results_l148.json` `banc/l148/raw_l148.npz`
  `banc/l148/anchors_run.json`; PREREG `banc/l148/PREREG.md`
- verify: `paper/l149_verify.py` §3
- keys: l148.eall l148.h_id l148.pooled l148.seid

### B10 — L150: pooled rebases + ranking fix (static + fresh batch B30/B33 unions)
- scripts: `banc/l150_build.py` `banc/l150_precheck.py` `banc/l150_rank_probe.py`
  `banc/l150_run.py` `banc/l150_static_fix.py` `banc/l150_verdict.py`
- artifacts: `banc/l150/results_l150.json` `banc/l150/static.json`
  `banc/l150/raw_l150.npz` `banc/l150/anchors_run.json`; PREREG `banc/l150/PREREG.md`
  (+ ADDENDUM 1: seed pin re-derived from npz keys, L44 #11)
- verify: `paper/l149_verify.py` §6
- keys: l150.h1 l150.pooled

### B11 — L151: static redundancy decomposition (static)
- scripts: `banc/l151_static.py` `banc/l151_followup.py`
- artifacts: `banc/l151/static.json`; PREREG `banc/l151/PREREG.md`
- verify: `paper/l149_verify.py` §5
- keys: l151.sheet l151.crossed l151.verdict

### B12 — L152: references + Fig 2 (owner-gated card, shipped in-session)
- scripts: `paper/l152_fig2.py` `paper/l152_qa.py`
- artifacts: `paper/references.bib` `paper/fig_l152.png` `paper/fig_l152.svg`
- published: `peabrain-figs/l152_clamp_cut_grid.png` `peabrain-figs/l152_clamp_cut_grid.svg`
- verify: pre-ink asserts in `paper/l152_fig2.py` (every plotted value vs
  numbers.json; Wilson recompute dev<1e-12) + `paper/l152_qa.py`; grid values
  re-certified by `paper/l149_verify.py` §3
- keys: (figure consumes B2/B6/B7/B9/B10 keys; adds `l137.vol1110`)

### B13 — L154: deafferentation direction test (fresh batch B34, paired)
- scripts: `banc/l154_build.py` `banc/l154_run.py` `banc/l154_static.py`
  `banc/l154_verdict.py`
- artifacts: `banc/l154/results_l154.json` `banc/l154/static.json`
  `banc/l154/raw_l154.npz` `banc/l154/anchors_run.json`; PREREG `banc/l154/PREREG.md`
- verify: `paper/l149_verify.py` §7
- keys: l154.band l154.freq l154.structure

### B14 — L156: sub-band slow-line census (static, 28 stored batches)
- scripts: `banc/l156_static.py`
- artifacts: `banc/l156/static.json`; PREREG `banc/l156/PREREG.md` (+ ADDENDUM 1)
- verify: `paper/l149_verify.py` §8; `banc/l156/verify_push.py`
- keys: l156.pooled

### B15 — L157: per-pool carrier census (fresh batches B33/B34, static)
- scripts: `banc/l157_static.py`
- artifacts: `banc/l157/static.json`; PREREG `banc/l157/PREREG.md` (+ ADDENDUM 1)
- verify: `paper/l149_verify.py` §9; `banc/l157/verify_push.py`
- keys: l157.pooled

### B16 — L160: Fig 3 (carrier census figure)
- scripts: `banc/l160/fig_l160.py` `banc/l160/l160_qa.py`
- artifacts: `banc/l160/fig_l160.png` `banc/l160/fig_l160.svg`
- published: `peabrain-figs/l160_slowline_carrier.png` `peabrain-figs/l160_slowline_carrier.svg`
- verify: draw-time asserts in `banc/l160/fig_l160.py` (all Wilson lbs
  recomputed from stored k/n, dev<1e-12) + `banc/l160/l160_qa.py`
- keys: (figure-only; consumes `l157.pooled` + `l156.pooled`)

### B17 — L158/L159: abstract freeze + prose gates (paper hygiene)
- scripts: `paper/extract_numbers.py` `paper/l158_verify.py` `paper/l159_verify.py`
- artifacts: `paper/numbers.json` (65 keys, byte-stable on regeneration)
- verify: self
- keys: (meta — covers all)

### B18 — L134: carrier anatomy statics (§2.3, observation-labeled)
- scripts: `banc/l134_static.py`
- artifacts: `banc/l134/static.json`
- verify: prose cites the artifact directly; no keyed numbers
- keys: (none — observation block)

### B19 — L168: scramble controls (carrier-free mass-matched cohorts, static)
- scripts: `banc/l168/l168_pools.py`
- artifacts: `banc/l168/static.json`; PREREG `banc/l168/PREREG.md`
- upstream rollout sources (no new rollouts in L168):
  `banc/l125/results_l125.json` `banc/l127/results_l127.json`
  `banc/l128/results_l128.json` (`table.Ti`, `mass_scr`, `extra_mass_scr`,
  `pooled_scr`, `pooled_scr0`) — the arms themselves were run in L125/L127/L128
- verify: `paper/l149_verify.py` §10 (pools re-derived independently from the
  three stored tables, Wilson to 1e-12, draft rows asserted verbatim, claim
  (d) proven in data, PREREG rule D3 matched) + CERT-1..4 inside
  `banc/l168/l168_pools.py` (stored per-batch bounds, stored `pooled_scr`
  rows, the 2-batch `pooled_scr0` prefix, cross-file mass consistency)
- keys: l168.scr l168.base l168.window_mass l168.verdict

### B20 — L169: pre-posting control (a), the gain-swap 2x2 (rollouts, B35)
- scripts: `banc/l169_build.py` (count-asserted additive transform of
  `banc/l150_run.py`), `banc/l169_run.py`, `banc/l169_verdict.py`
- artifacts: `banc/l169/raw_l169.npz` (9 arms x 18 seeds incl anchors 801/901),
  `banc/l169/raw_partial.npz`, `banc/l169/anchors_run.json`,
  `banc/l169/results_l169.json`, `banc/l169/run.out`, `banc/l169/verdict.out`;
  PREREG `banc/l169/PREREG.md` (2x2 cells, class bands, C0-NT probe, P-af
  direction and the D1/D2/D3 branches registered before the run)
- anchors: C0A-169 vs `banc/l135/raw_l135.npz` (4 shared arms x 22 keys x
  2 seeds, max 0.0); FC-144 `silW` vs `banc/l144/raw_l144.npz:sil1110_wA`;
  FC-145 `eMotTop5`/`eMotBot5` vs `banc/l145/raw_l145.npz`; fresh bisects
  reproduce the stored `g_cutwA`/`g_cutng25`/`g_eMotTop5`/`g_eMotBot5` EXACT;
  B35 absence across 36 stored npzs; B-cert vs six stored Ti tables
  (l135 B26, l142 B29, l144 B30, l145 B31, l148 B32, l150 B33)
- verify: `paper/l149_verify.py` §11 (2x2 re-derived from the raw B35 traces
  with the run's own duty machinery, Wilson to 1e-12, paired legs recomputed,
  branch D1 proven from the measured cells, C0-NT + crossed gains + the 15/18
  P-af disclosure asserted, §2.7 literals verbatim)
- re-verify: `python banc/l169_verdict.py` then `python paper/l149_verify.py`
- keys: l169.grid l169.swap_legs l169.branch l169.af l169.pooled l169.nt

### B21 — L169 stage (b1): frozen-vs-rederived floor forms (static, zero rollouts)
- scripts: `banc/l169b_build.py` (1-site additive transform of
  `banc/l146_static.py`, residual scan + py_compile), `banc/l169b_static.py`
- artifacts: `banc/l169b/static.json` (four registered forms F0/F1/F2/F3,
  code audit, design pins P1-P5, verdict), `banc/l169b/static.out`,
  `banc/l169b/static_l146cert.json` (the re-derived l146 census, CERT-1);
  PREREG `banc/l169b/PREREG.md` (forms, CERT block, E1/E2/E3 rule and the
  (b2) design pins registered before any computation)
- anchors: CERT-1 re-derived l146 census == stored `banc/l146/static.json`
  on all 10 keys `l146_static.py` writes (the extra `S0_release` key is
  written by `banc/l146/release_floor_addendum.py` — subset compare
  disclosed, L110 class); CERT-2 F1 ranks 25/26 by construction; CERT-3
  `ladder(4)` reproduces the stored `S4_ladder.f4` field-for-field
- verify: `paper/l149_verify.py` §12 (F3 vs stored f4 field-for-field, F1
  frozen ranks, F2 == F3 ranks so the shift is re-ordering not turnover,
  Jaccard .9231 recomputed independently from 72/78, rule E1 proven from
  the cells, static-only scope + §4 literals verbatim)
- re-verify: `python banc/l169b_static.py` then `python paper/l149_verify.py`
- keys: l169b.forms l169b.scope

### B22 — L169 stage (b2): the floor-4 DYNAMIC arm (rollouts, B36 n=16)
- scripts: `banc/l169b2_build.py` (24-rep count-asserted transform of
  `banc/l169_run.py`, residual scan with an explicit input/docstring
  whitelist + py_compile), `banc/l169b2_run.py`, `banc/l169b2_verdict.py`,
  `banc/l169b2_addendum.py` (post-hoc left-side read, separate key)
- artifacts: `banc/l169b2/raw_l169b2.npz` (12 arms x 18 seeds, checkpointed
  before analysis), `banc/l169b2/raw_partial.npz`,
  `banc/l169b2/anchors_run.json`, `banc/l169b2/results_l169b2.json`,
  `banc/l169b2/run.out`, `banc/l169b2/verdict.out`; PREREG
  `banc/l169b2/PREREG.md` (substrate convention, three arms, classifiers,
  CERT block, G1-G4 branches and the vacuous-XOR guard — all registered
  before the run)
- anchors: CERT-1 FC-169 forward chain, 9 inherited arms x 22 keys x 2
  seeds vs `banc/l169/raw_l169.npz` max 0.0e+00; CERT-2 four stored-form
  bisects EXACT (g_cutwA / g_cutng25 / g_eMotTop5 / g_eMotBot5) — which is
  also the certification that restricting `settle_states` to the arm under
  bisect is a no-op (L139 spectator law); CERT-3 the in-run floor-4 ladder
  == `banc/l169b/static.json` F3 field-for-field (K 73, ranks 21/33,
  Jaccard .9231, 472,095 closure edges) plus the f4 twin gi 290 and its
  2.4e-05 mass gap; C0-NT(b2) every f4 arm separated from its base
  counterpart and from the other f4 arms (min 2.87e-02); B36 absence across
  38 stored npzs; CERT-METRIC the verdict's helper copy reproduces l169's
  stored B35 cells (cutwA / wAgN / n25gW, 4 fields each) EXACTLY
- verify: `paper/l149_verify.py` §13 (CERT chain, three distinct fresh
  gains with staircase <= 5e-3, all three f4 arms kR 0/16 with the k=0
  Wilson bound recomputed, base arms reproducing on B36, branch
  G2_no_transfer proven from the cells, flat XOR leg 8/8, the DESCRIPTIVE
  left-side addendum labelled and its paired legs asserted, §4 literals)
- re-verify: `python banc/l169b2_build.py && python banc/l169b2_run.py`
  then `python banc/l169b2_verdict.py && python banc/l169b2_addendum.py`
  then `python paper/l149_verify.py`
- keys: l169b2.dyn l169b2.lat_descriptive

## Methods constants (disclosed provenance)

- "staircase residuals disclosed, all < 6.4e-4" (§3): the per-arm
  |af_final − target| residuals live in the run logs, e.g.
  `banc/l150/run.out` (af_final 0.109035 vs target 0.10906 → 2.5e-5); the
  largest residual printed across stored lane logs is 5.23e-04. The 6.4e-4
  constant is a loose ceiling written in prose — it is NOT itself a stored
  artifact value (provenance gap flagged by L161; candidate one-word tighten
  to "5.3e-4" for the next owner-gated prose pass; no draft edit made here).
- Everything else in §3 (subnet rule, NT joins, gain bisection, frozen
  criteria) is certified by the per-lane PREREGs + C0A anchor chains listed
  in each block.

### B23 — L169 stage (c1): design pins for the two queued (c) arms (static)
- keys: l169c.design
- scripts: `banc/l169c_build.py` (1-site ADDITIVE transform of
  `banc/l151_static.py`: lines 1-319 verbatim + `banc/l169c_tail.py`;
  splice anchor count-asserted, residual scan refusing any surviving WRITE
  to a prior artifact, single `json.dump` target asserted, py_compile),
  `banc/l169c_static.py` (generated), `banc/l169c_tail.py`
- artifacts: `banc/l169c/static.json` (P1-P7 design pins + rules C1-C3),
  `banc/l169c/static.out`, `banc/l169c/static.err`; PREREG
  `banc/l169c/PREREG.md` (the REW and HOM arms, rules C1 vacuity / C2
  mirror-equivalence / C3 rewire feasibility, and the rewire protocol with
  its seed and draw count — all registered before any computation)
- anchors: CERT-1 the verbatim head re-derives l151's own s1/s2/s3 blocks
  and they equal `banc/l151/static.json` field-for-field (415 scalar
  fields, subset compare on s1 because `signed_1110_out_G1` is appended
  after that block — L110 class, disclosed); the head's own L142/L134 pins
  re-run as free certification (80 out / 13 in / 93 incident, out-mass
  183.96376182027785, T70 70 + T10 10, `ng_desc[24] == 1110`); per-draw
  degree-neutrality asserted exactly (the destination multiset over every
  touched row is preserved in all 100 draws); `banc/l151/static.json`
  never rewritten (mtime unchanged)
- verify: `paper/l149_verify.py` §14 (rules re-read from source, the C2
  refutation isolated to the class leg with all three footprint legs
  passing, gi 928 proven cord-receiving and outside every cut window,
  Jaccard recomputed from the two destination counts, mirrored motor sides,
  rewire bars recomputed, §2.7 literals and the superseded label asserted
  GONE)

### B24 — L169 stage (c2): displacement is not removal; the class axis is specific
- keys: l169c2.base l169c2.rew l169c2.branch l169c2.gains l169c2.hom l169c2.cert
- claim: a degree-preserving rewire of the carrier's 80 closure out-edges
  is bracketed by the carrier-INTACT base, not by carrier removal (2 of 3
  registered draws NOT-SUPER and BELOW cutwA, one draw SUPER; draw pool
  20/48 [.288,.557] straddling cutwA's [.142,.556]); and deleting a
  same-footprint different-class cell (gi 928, 101 incident edges) does not
  flip the readout (meanR .301, kR 2/16, paired −.150)
- evidence: `banc/l169c2/` (PREREG.md with branches R1-R3 + H1-H2
  registered pre-run, l169c2_build.py count-asserted additive transform of
  l169b2_run.py + residual scan, raw_l169c2.npz, results_l169c2.json,
  run.out, verdict.out); fresh B37 3481-3496, n=16 per arm, fresh
  af-matched bisect per arm (gains .145617/.150060/.144464/.143731)
- anchors: FC-169B2 12 inherited arms x 22 keys x 2 seeds vs
  `l169b2/raw_l169b2.npz` max 0.0e+00; C0A-150/FC-144/FC-145/FC-169 all
  0.0; four stored-form bisects EXACT; CERT-REW = the in-run rewire draws
  == `l169c/static.json` P5/P6 field-for-field; CERT-HOM 101 incident
  edges; C0-NT(c2) min 1.85e-2; staircase residuals <= 5.9e-4
- verify: `paper/l149_verify.py` §15 (all six table cells re-derived from
  the RAW B37 traces with an independent duty implementation, paired legs
  recomputed, the draw pool and its straddle proven from the cells so the
  R2/R3 conjunction is justified, base non-vacuity, H1 proven from the hom
  cells, gain non-ordering, rew3-vs-hom per-seed spread .46, §2.7 literals
  verbatim)

### B25 — L169 stage (d): the XOR pair at swapped gains; identity wins in both gain columns
- keys: l169d.grid l169d.legs l169d.branch l169d.xbatch l169d.cert
- claim: the twin-XOR pair (cutng25 = carrier gi 1110 removed vs cutng25p =
  mass-twin gi 319 removed, 3.9e-04 mass delta) run FULLY CROSSED against
  {own af-matched gain, the other arm's} keeps the carrier-removed graph on
  top in BOTH gain columns (+.474 at g_cutng25 with 16/16 seeds up, +.174
  at g_cutng25p with 12/16): the twin graph does not reach SUPER at the
  carrier arm's higher gain (meanR .324, kR 1/16) and the carrier graph
  stays SUPER at the twin arm's lower gain (.651, kR 15/16) — registered
  branch E1_graph_tracking. Own-gain diagonal reproduces on a fresh batch
  (cutng25 .798 16/16 SUPER, cutng25p .477 8/16 NOT-SUPER at the band
  boundary, disclosed)
- evidence: `banc/l169d/` (PREREG.md with branches E0-E3 registered in
  explicit precedence pre-run, l169d_build.py count-asserted additive
  transform of l169c2_run.py + residual scan, l169d_verdict_build.py
  verbatim helper slice with a helper-survival assert, raw_l169d.npz,
  results_l169d.json, run.out, verdict.out); fresh B38 3513-3528, n=16 per
  arm; gain span 1.337% (g .143526574 vs .145445455)
- anchors: FC-169C2 16 inherited arms x 22 keys x 2 seeds vs
  `l169c2/raw_l169c2.npz` max 0.0e+00; C0A-150 EXTENDED to 5 arms so
  `cutng25p` is bit-identical to `l135/raw_l135.npz` (max 0.0) = the new
  arm's free wiring certificate; CERT-3 five stored-form bisects EXACT
  (incl. g_cutng25p); CERT-METRIC == l169c2's stored B37 cells; C0-NT(d)
  min 1.92e-2; staircase residual 5.4e-07; P-af direction PARTIAL (15/18
  up, 13/18 down), disclosed
- verify: `paper/l149_verify.py` §16 (all six grid cells re-derived from
  the RAW B38 traces with an independent duty implementation, all seven
  paired legs recomputed, branch E1 proven from the cells, swap-arm graph
  identity + gain-column structure + re-derived span, the twin-arm boundary
  disclosure, the both-swap-arms-below-own-gain sentence, cross-batch B25
  cells re-read from l135, §2.7 literals verbatim and the superseded
  queued clause asserted GONE from the body)

### B26 — L170: the male extraction at a MATCHED synapse floor (static, zero rollouts)
- keys: l170.matched l170.pins
- claim: §2.6's cross-connectome boundary was an UNMATCHED-FLOOR comparison
  and we corrected it ourselves. Our male closure mirror applied no synapse
  floor while the BANC release carries an implicit pair-level floor of 3; at
  the matched floor the same extraction gives dn_new 342 cells / 43 ng with
  K = 52 (floor 1: 28 / 9, K = 9) and the window shares become computable
  for the first time (male 0.2818 / 0.0667 / 0.0670 vs BANC 0.1946 / 0.0642
  / 0.1333 — the rank-20–29 window agrees to .0025). Registered branch
  M1_floor_changes_cohort (rel change 11.21). What survives the match: male
  DNp33 stays RECIPROCAL at both floors (cord in-edges 37/33 → 6/2, never
  0, ladder mass exactly 0.0), so M3_dnp33_pure did NOT fire. Status is
  UNTESTED AT MATCHED FLOOR — no dynamics were run on the floored male
  substrate (L169 b2 is the standing warning against static→dynamic
  inference)
- evidence: `banc/l170/` (PREREG.md with M1/M2/M3 + P1–P4 registered pre-run,
  precheck.json = the MaleCNS release floor census that made floor 3
  admissible and non-vacuous — min weight 1.0, 0 duplicate pairs, 10,512,742
  of 25,568,639 pairs surviving, static.json, static.out);
  `banc/l170_precheck.py`, `banc/l170_build.py`, `banc/l170_static.py`
- anchors: `l170_static.py` keeps `l138_static.py`'s head VERBATIM (12,691
  chars, byte-identity asserted at build time), so every BANC pin in it
  (L92/L107/L121/L131 k-ladder + rank twins 1110/319 + K/mass_split) re-ran
  as free certification; CERT-1/2 = the floor-1 arm reproduces the stored
  l138 male side EXACTLY (all 9 s1 fields, window, dn_into 1277, pure_proj
  28, both DNp33 rows, ng top-10, the 9-entry ng mass list); residual scan
  refuses any write outside `l170/` (single json.dump target) and
  `l138/static.json` is read-only and never rewritten (mtime unchanged)
- design pins for a future dynamic walk: floor-3 ranks 25/26 = DNp54-R /
  DNpe028-L, mass gap 4.4e-04 of cohort mass — 1.13x BANC's own XOR pair
  delta (3.9e-04), so an analogous mass-twin test is constructible; floor
  ladder dn_new {1: 28, 2: 199, 3: 342, 4: 458}, K {9, 46, 52, 59}
- evidence rule: the reviewer's floor-3 numbers (342 / K=52) stay
  REVIEWER-REPORTED and are NOT cited in the draft; our run reproduces them
  independently, which is recorded here and in LANE-LOG only
- verify: `paper/l149_verify.py` §17 (floor-1 CERT cross-file against
  `l138/static.json`, floor-3 window shares re-derived independently from
  the stored per-cell ng mass list, twin gap re-derived from its two mass
  shares and compared against BANC's own stored `pair_delta`, branch M1
  proven from the cells with M2/M3 proven not to fire, DNp33 reciprocity
  and the floor ladder pinned, §2.6 literals verbatim and three superseded
  clauses asserted GONE from the body)

### B27 — L171: slow-line re-attribution + two-window robustness panel (zero rollouts)

- claim: the sub-band .100 Hz line is STIMULUS-SET (the drive envelope's own
  dominant spectral line is .100 Hz exactly), so it leaves the abstract and
  the §1 four-result list; and the identity contrast does NOT ride on it —
  re-scored in the unchopped 1.4-Hz segment (12/16 vs 0/16, paired 16/16)
  and after a 0.3-Hz high-pass (15/16 vs 1/16), the carrier-vs-twin ordering
  is preserved (registered branch B2_preserved, not "cleaner")
- keys: l171.envelope l171.panel
- prereg: `banc/l171/PREREG.md` (A1/A2/A3 attribution branches; B1-B4
  robustness branches with the DEGENERATE branch checked first per re-score;
  the mech-off counter-evidence registered as a MANDATORY disclosure; P1-P6)
- script: `banc/l171_rescore.py` (zero rollouts, no RNG, no graph build)
- artifacts: `banc/l171/results.json`, `banc/l171/run.out`; inputs
  `banc/l135/raw_l135.npz` (B26 traces + the two l133 anchor seeds),
  `banc/l135/results_l135.json` (the published table), `banc/l135_run.py`
  (the envelope source), `banc/l154/results_l154.json` (mech-off census),
  `banc/l162/addendum3.json` (the evoked phase lock)
- CERT: the published q07 cells are reproduced EXACTLY (kR 15/16 meanR .754;
  twin 5/16 meanR .399; kL/meanL too) and the stored Wilson bounds re-derived
  to < 1e-9 BEFORE any new window or filter is read; the measurement n = 16 is
  DERIVED (the stored k=0 Wilson ub .19360768 identifies n=16, so the npz's two
  extra forward-chain anchor seeds are excluded, not assumed); the high-pass is
  self-tested on synthetic input (.05 Hz attenuated > 100x, 1.4 Hz preserved to
  2e-15) before it touches a pool trace
- own-catch (disclosed): the CARD asked Methods to state "the 0.1-Hz peak is
  the 9-s stimulus cycle". That sentence is WRONG and the run refutes it — the
  chop fundamental (.111 Hz) is not the envelope's dominant line; the four
  surviving off-gaps (7, 16, 47, 56 s) are phase-aligned at a 10-s period
  (vector strength .95 vs .17), which is why the envelope peaks at .100 Hz.
  The corrected mechanism is what the draft states and what §18 gates
- own-catch (disclosed): numbers.json was regenerated WITHOUT first copying
  the pre-tick file, so the house byte-identity check could not be run in its
  usual form. Substitute: the generator diff is purely ADDITIVE and a
  regenerate-without-the-l171-block run reproduces all 89 pre-existing keys
  byte-identically (`json.dumps(sort_keys=True)` equality)
- verify: `paper/l149_verify.py` §18 (envelope rebuilt from constants PARSED
  out of `banc/l135_run.py`, FFT and gap-alignment vector strengths
  re-derived, all published + re-scored cells recomputed from the RAW traces
  with an independent duty/S implementation, both paired counts, branch
  B2_preserved proven from the cells, the metric-dependence asserted in both
  directions, §2.8 + Methods literals verbatim, superseded abstract clauses
  asserted GONE); `paper/l158_verify.py` freeze RE-CUT to v3.16 (the
  re-attribution tokens and language are now REQUIRED in the abstract, and an
  endogenous-clock re-assertion is forbidden)

### B28 — L172: the statistics pass (zero rollouts)

- claim: every arm carries ONE canonical pooled count — the maximal
  UNIQUE-SEED union over all admissible stored batches (38 of 49 trace
  files; jittered-gain sets excluded as different networks) — reported as
  k/n + full-precision Wilson + mean duty + bootstrap CI, with every
  contrast given as a DIFFERENCE with a Newcombe interval and a Fisher
  exact p instead of an "interval contains .5" reading; the unit of
  inference is a noise seed of ONE fixed network, stated explicitly
- the registered branch S1_counts_stable fired (every class survives the
  re-pool) but registered prediction P4 is REFUTED: at the canonical pool
  the mass-twin sits +.175 [+.047,+.305] (Fisher p = .008) ABOVE the
  untreated-cut base, so "behaviourally neutral" was a small-pool
  artefact and the twin is relabelled INTERMEDIATE — the card's own
  prescription ("disclose as underpowered") is superseded by the data
- keys: l172.pooled l172.diffs l172.census_unique l172.meta
- prereg: `banc/l172/PREREG.md` (admissibility rule A1-A4, the unit of
  inference, CERT-1/2/3, branches S3_dup_inconsistent > S2_class_moves >
  S1_counts_stable, predictions P1-P6, the evidence rule barring the
  reviewer's own figures from the draft, the no-draft-edit clause)
- script: `banc/l172/l172_stats.py` (zero rollouts, no graph build; RNG
  only for the registered bootstrap, seed 1720)
- artifacts: `banc/l172/stats.json` (pooled + per-seed duties + diffs +
  census + admissibility), `banc/l172/stats.out`, `banc/l172/inv2.json`
- CERT: (1) the stored l156 census cells re-derived from the stored
  per-seed rows field-for-field, which caught the stored `agree`
  definition (counted only among sub-band rows: a row-wide count gives 84
  where the stored pooled value is 80); (2) the duty implementation
  reproduces four stored per-batch cells EXACTLY (l142 cutng25, l145
  eMotTop5, l150 silW, l169d cutng25 — kR, kL, meanR at the stored 3-dp
  rounding) with stored Wilson bounds to 1e-9, BEFORE any pooled number
  was read
- predictions scored: P1 PARTIAL (the recurring seeds are the two
  forward-chain anchors PLUS a 16-seed block that two early runs both
  rolled — 18 in total, not 2); P2 HELD (published pooled n = 16 x
  batches and the blocks are disjoint, so the duty counts were already
  unique-seed clean — the card's unique-seed worry bit the CENSUS, which
  pooled traces); P3 HELD (449/449 keeps lb .992; closure moves .722 ->
  .804, inside the registered .10 band); P4 REFUTED (above); P5 HELD;
  P6 HELD (the canonical union exceeds every union the draft quoted)
- S3 did NOT fire: zero disagreeing repeat observations across files, so
  the forward-chain bit-identity assumption holds at the METRIC level too
- independent agreement, recorded here and BARRED from the draft per the
  evidence rule: the reviewer's own unique-seed figures (449 of 518 and
  348/433) match our independent derivation exactly
- verify: `paper/l149_verify.py` §19 (census CERT re-run with the
  agree-among-sub-band definition, both unique-seed forms, the
  admissibility rule re-proven by PARSING every admissible run script's
  constant block from source, per-seed duty spot-checked from RAW traces,
  every arm's kR/Wilson/mean/bootstrap recomputed, all 13 difference
  intervals re-derived from first principles, the P4 refutation proven in
  data, branch S1 proven class-by-class, superseded forms asserted GONE
  from the body); `paper/l158_verify.py` freeze RE-CUT to v3.17 (the
  canonical counts are REQUIRED in the abstract and the superseded
  per-batch cells are FORBIDDEN); `paper/l161_verify.py` §1 required-key
  set re-cut to the canonical keys


### B29 — L173 (a): the Methods write-up (zero rollouts)

- claim: §3 now states the model the paper actually ran — the update
  equation, every constant, the DNg100 tonic drive D = 0.2 (absent from
  every earlier draft), the chopped sinusoid, the active-fraction target
  and its bisect, the cohort / removal-mass / ladder definitions, the
  duty and class criteria, the pooling rule, and a 15-row notation table
- method: nothing is transcribed. Every value is PARSED at write time —
  model constants by ast from `banc/l135_run.py` (and asserted identical
  in the CURRENT run script `banc/l169d_run.py`, CERT-1, 15 constants),
  duty / S-window / class criteria from `banc/l169d_verdict.py` (and
  asserted unchanged since `banc/l135_verdict.py`), the cohort rule from
  `banc/l131_static.py` against the stored K = 77 / share .5024, and the
  pooling rule from `banc/l172/stats.json`
- the one computation: the card's prescribed update equation is
  CERTIFIED against the run script's own three update lines by a
  deterministic 7-node probe — max|Δ| = 0.0, branch M1_equation_matches,
  so the equation in §3.2 is the code's semantics and not a paraphrase
  (the probe also pins the two details prose gets wrong: the noise enters
  AFTER the rectifier and INSIDE the clamp, and the clamp has no lower
  bound)
- scope: stage (a) of the card only. §2.4 is NOT rebuilt here and keeps
  its present wording and both bit-identity passages; the banner says so
  and the verifier asserts it
- keys: l173.model l173.protocol l173.defs
- prereg: `banc/l173/PREREG.md` (source-of-truth rules S1-S4, CERT-1/2/3,
  branches M2_equation_differs > M1_equation_matches, pins P1-P5, the
  stage (a)/(b) split)
- script: `banc/l173_methods.py` (zero rollouts, no graph build; the only
  RNG is the fixed-seed 7-node equation probe) -> `banc/l173/methods.json`
- verify: `paper/l149_verify.py` §20 (constants RE-PARSED by an
  independent ast walk, the equation probe re-run from scratch, the
  verdict/static definitions re-parsed, all 21 §3 literals and all 15
  notation rows checked value-by-value against the parsed source, and the
  stage-(a) scope asserted)

### B30 — L173 (b): the §2.4 rebuild around the gain-clean arm (zero rollouts)

- claim: the carrier's channel can be isolated WITHOUT a gain change.
  silW (clamp the carrier's activity on the cutwA PARTIAL base) flips to
  SUPER at a gain BIT-IDENTICAL to its own base's — g =
  .14365819573402408, EXACT float equality in both of its batches (l144
  `g_sil1110_wA`, l150 `g_silW`), with five files agreeing on the base
  gain — while every edge-removal flip arm carries a +1.06..+1.30%
  af-matched gain increase (eOutInt +1.297, cutng25/eAll +1.244, eOutAll
  +1.238, eIn +1.087, eMotIn +1.062) and the two non-flip motor halves
  sit within ±0.03% (eMotTop5 −0.031, eMotBot5 +0.009; intermediate
  eOutMot −0.568). Identity and gain CO-VARY across the edge ladder;
  silW breaks the covariance from the activity side and §2.7's graph ×
  gain 2×2 closes it from the wiring side
- branch: B1_silW_gain_unchanged (registered precedence B2 > B1)
- honesty repairs in the same fold: the "−.088 inside the .075 sham
  spread" wording leaves §2.4 (|−.088| is LARGER than the three shams'
  range, so the arm reads "no demonstrated effect"); sil24 discloses a
  class-label match with NO demonstrated separation from either
  comparator at n = 16 (5/16 vs intact 6/16 vs cut 5/16, same batch);
  the carrier-mass ratio is corrected from 12× to 9.72×
  (.0544/.005599) in §2.4 and the abstract
- relocation: both construction-level identities (eAll ≡ cutng25; se0 ≡
  eAll) now live in Methods §3.8 as sanity checks; §2.4 keeps only the
  ~.13 silW→eAll margin they leave as a result. The "two-factor law"
  framing is retired body-wide
- keys: l173b.gains
- prereg: `banc/l173b/PREREG.md` (source-of-truth T1-T4, CERT-1..6,
  branches B2_silW_gain_differs > B1_silW_gain_unchanged, pins P1-P4,
  and a registered SCOPE EXTENSION for the mass-ratio correction)
- script: `banc/l173b/l173b_cert.py` (zero rollouts, zero RNG,
  arithmetic over stored values only) -> `banc/l173b/cert.json`
- verify: `paper/l149_verify.py` §21 (all ten gains re-read from stored
  `anchors.g_*` fields and all ten percent deltas re-derived
  independently of cert.json, the flip partition taken from stored class
  booleans, the pool and its difference interval recomputed, the sham
  spread re-proven smaller than the carrier's own ΔR, the mass ratio
  re-derived, the relocation and the retired framing's body-wide absence
  asserted) + `paper/l158_verify.py` (freeze re-cut: 9.72 REQUIRED,
  "12× below" FORBIDDEN in the abstract)

### B31 — L174 stage (a): the reference pass and the corrected characterizations

- claim: the reviewer's missing-citation list is cited (22 new entries,
  numbers 14-35), every one of the 35 entries is cited at least once in the
  body, and three cited-work characterizations are corrected — ApproxBrain
  DOES report single-interneuron necessity (mean task distance .017 over 32
  held-out parameter draws), FlyHack's instability is across comparison
  model / intervention form / trained solution, and the Kopel-class caveat
  on BANC is about synapse DETECTION (22% of detected synapses land on an
  identified neuron) rather than about pair weights.
- prereg: `banc/l174a/PREREG.md` (R1 primary-only, R2 match evidence, R3
  version honesty, R4 no renumber, R5 the reviewer's text is raw material;
  CERT-1/2/3; branches A2_approxbrain_necessity_confirmed > A1; P1-P4)
- branch taken: **A2_approxbrain_necessity_confirmed** (our own stored digest
  carries the necessity result, so the novelty contrast narrows)
- scripts: `banc/l174a/l174a_refs.py` (round 1 + CERT-1),
  `banc/l174a/l174a_refs2.py` (eLife assessment records filtered,
  bioRxiv API), `banc/l174a/l174a_refs3.py` (bioRxiv's current 10.64898
  prefix + the MANC record), `banc/l174a/l174a_emit.py` (formats ONLY),
  `banc/l174a/l174a_splice.py` (appends, never renumbers)
- artifacts: `banc/l174a/refs.json` (23 accepted records + CERT-1 table),
  `banc/l174a/raw/` (every raw API response), `banc/l174a/emit_bib.txt`,
  `banc/l174a/emit_list.md`
- verify: `paper/l174_verify.py` (7 checks: bidirectional citation gate,
  list integrity, bib <-> list, per-entry provenance against the stored
  records, required/retired characterization text, cited field numbers
  traced to our LANE-RESEARCH digests, numbers.json byte-identity)
- zero rollouts, zero RNG, no measured value changed

### B32 — L174 stage (b1): the tick-204 novelty narrowing (references 36/37)

- claim: identity beating cell NUMBER in a connectome-constrained fly model
  is prior art (Habib, Petr & Rust on MaleCNS v1.0: 37 descending neurons
  removed from a 1,000-cell mask leave 57.4% of intact steering distance vs
  101.0% for 37 other cells from the SAME mask; 100 cells restored by
  motor-control priority reach 62.5% vs 10.1% for a random hundred; matched
  identities 60.0% vs 6.7% for non-target identities at the same 100
  positions), so §1 states our contrast as four specific things — matching
  currency (count vs removal mass), resolution (a class vs one cell and one
  mass twin), readout (a decoded behavioural scalar through a hand-built
  open-loop controller vs an emergent in-network structure statistic) and
  direction/substrate (remove-then-add on the male CNS vs removal on the
  female cord) — and the gap paragraph no longer claims identity-over-count
  as such. Their claim is scoped as TYPE-DEPENDENT INTEGRATION because 89 of
  their 100 matched cells copy a reflected same-type neighbour. §4 carries
  their 15%-amplitude threshold-proximity disclosure beside our gain
  ensemble, their unit-of-inference convergence, and a cross-specimen
  string-join limitation citing topology-only female-VNC typing.
- prereg: `banc/l174b/PREREG.md` (R1 primary-only, R2 acceptance = title
  overlap >= .60 AND an author-surname match, R3 the 10.64898 prefix with a
  legacy-DOI control fetch, R4 no renumber, R5 field numbers only from our
  own stored digests; CERT-1..4; branches N2_record_differs > N1; P1-P5; Q1-Q3)
- branch taken: **N1_identity_prior_art_confirmed** (both records accepted
  at title overlap 1.000 with surname matches; the Habib record's own
  abstract independently carries the 6.5%-at-2,000 and .04-.95 straightness
  numbers our digest attributes to it)
- scripts: `banc/l174b/l174b_refs.py` (primary fetch + R2 acceptance + the
  legacy-DOI control), `banc/l174b/l174b_emit.py` (formats and splices ONLY;
  refuses to run twice, never renumbers)
- artifacts: `banc/l174b/refs_b.json`, `banc/l174b/raw/` (both details
  responses + both legacy controls), `banc/l174b/abstract_pin.txt`,
  `banc/l174b/numbers_pretick.json`, `banc/l174b/draft_pretick.md`
- verify: `paper/l174_verify.py` sections (8)/(8b)/(8c)/(8d) — per-entry
  provenance against the stored records (DOI, version, posted date, >= .90
  title overlap), both legacy DOIs asserted unresolved, 21 required
  narrowing texts present with the superseded gap sentence asserted GONE, a
  predicate sensitivity self-test, 9 field numbers traced to our
  LANE-RESEARCH digests, and the Abstract block pinned byte-identical
- zero rollouts, zero RNG, no measured value changed

### B33 — L174 stage (b2): the abstract compression (relocation, not deletion)

- claim: the abstract can meet the card's print contract — <= 1,920 chars,
  no inline citation keys, no all-caps emphasis, no arm/lane/batch codes —
  without losing a single claim, because every cell it drops has a home in
  the certified body.
- measured: v3.21 abstract 5,322 flattened chars / 102 numeric tokens ->
  v3.22 1,916 chars / 31 tokens; all 76 dropped tokens present in the body
  (9 of them slash->prose re-formattings of cells the abstract still
  states); 0 relocation orphans; caps tokens {BANC}; arm-code matches 0;
  longest sentence 53 words
- PREREG: `banc/l174b2/PREREG.md` (T1 relocation-not-deletion, T2 no new
  number, T3 nothing retired comes back, T4 abstract-only edit; CERT-1..4;
  branches R2_relocation_incomplete > R1_relocation_complete; P1-P5)
- branch taken: **R1_relocation_complete** — zero numeric orphans. But R2
  DID fire at the PHRASE level and is disclosed: four gates keyed on
  abstract-LOCAL spellings whose claims live in the body under different
  wording (`max|Δ| = 0.0` in Methods 3.8, the sham means `.429/.502/.504`
  in §2.4, five of seven U-law cells in §2.1/§2.9). Each was re-scoped to
  the body form, never loosened; the sham check got STRONGER (all three
  stored values matched, not just the range endpoints).
- scripts: `banc/l174b2/emit.py` (single-block splice; asserts the
  pre-image equals the CERT-3 freeze, refuses to run twice),
  `banc/l174b2/measure.py` (length / caps / code / token scan),
  `banc/l174b2/reloc.py` (the numeric relocation read)
- artifacts: `banc/l174b2/abstract_v321.txt` (the frozen pre-image),
  `banc/l174b2/abstract_new.txt`, `banc/l174b2/abstract_pin_b2.txt`,
  `banc/l174b2/numbers_pretick.json`, `banc/l174b2/raw/` (CERT-1 baseline
  + every post-edit verify run)
- verify: `paper/l158_verify.py` re-cut to the v3.22 contract — section (2)
  keeps the Wilson recompute for all SEVEN U-law cells and only moves five
  locators to the body, section (4) becomes a TWO-PLACE vocabulary contract
  (28 abstract-required tokens, 30 relocated cells each asserted in the
  body, every retired cell still forbidden), and NEW sections (5)-(10) are
  the length gate, the 19-row claim -> numbers.json trace table asserted BY
  VALUE plus 9 declared non-measurement tokens, the caps gate, the arm-code
  gate, the relocation gate against the frozen pre-image, and a hash pin;
  `paper/l174_verify.py` P3 re-pinned to the compressed block
- disclosed degenerate pass (L55 rule): with 102 -> 31 tokens the
  retired-cell guard had fewer chances to fail, so it is reported as a
  guard that held, not as evidence
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B34 — L174 stage (b3): the §2.4 editorial pass (de-duplication, I10)

- claim: reviewer I10's three SUBSTANTIVE asks were already satisfied before
  this stage (the section is built on silW, both construction-level
  bit-identities live in Methods §3.8, sil24 is disclosed as not separable
  from either comparator), so I10's residue is editorial length — and length
  can be removed from a certified Results section without touching a claim,
  by making the grid table the single home of every per-arm level and seed
  count.
- measured: §2.4 9,937 -> 8,562 chars (-13.8%); 101 of 101 verifier literals
  survive VERBATIM (including the three that contain an internal newline);
  24 of 24 citation keys survive; the grid table is byte-unchanged; the seven
  bold claim leads are intact; of 143 numeric tokens the 12 that left the
  section are each present elsewhere in the body (0 orphans) and 0 new
  numbers entered; 1,258 prose chars sit inside asserted literals
- premise test (run BEFORE any edit, `banc/l174b3/premise.py`): I10a silW
  lead True, I10b both identities in §3.8 and absent from §2.4 True, I10c
  "NO demonstrated separation" present True -> branch
  **S1_editorial_only**. The referee's quoted "3.4k chars" is a MEASUREMENT,
  not a target: the same adjudication file records that I10's locator
  truncated §2.4 at a 2,600-char cap.
- PREREG: `banc/l174b3/PREREG.md` (T1 de-duplication-never-deletion, T2 no
  new number, T3 every gate literal survives and no verifier may be edited to
  fit, T4 §2.4-only edit, T5 claim inventory; branches
  S2_premise_not_satisfied > S1_editorial_only > S3; P1-P5) with TWO
  addenda: ADDENDUM 1 withdraws our own 7,200-char cap as MIS-DERIVED (it
  subtracted only literal chars and assumed the rest was padding) and
  replaces it with G1' de-duplication completeness plus a reported >=10%
  reduction, because a char cap on certified prose rewards deleting
  disclosures; ADDENDUM 2 records the freeze correction (the first freeze lost
  the span's trailing newline, so emit.py's pre-image assert failed and wrote
  nothing).
- G1' sensitivity self-test: the de-duplication gate FAILS on the frozen
  pre-image with five restated cells (eOutInt .781/15,16, eIn .793/15,16,
  eOutMot .525/9,16 and .632/12,16, eMotIn .801/15,16) and PASSES on the
  compression — a gate that cannot fail on the old text measures nothing.
- method note (the tick-206 lesson applied PRE-edit): all 101 verifier string
  literals occurring in §2.4 were enumerated BEFORE the rewrite, 62 of them
  occurring nowhere else in the draft. Result: all six paper verifies came up
  green on the FIRST post-splice run, against four honest gate failures when
  the same class of edit was done without the enumeration.
- scripts: `banc/l174b3/premise.py` (I10 premise test + pins),
  `banc/l174b3/gate.py` (T1/T3/T5 + G1', writes `gate.json`),
  `banc/l174b3/emit.py` (single-block splice, asserts the pre-image equals
  the freeze, refuses to run twice)
- artifacts: `banc/l174b3/sec24_pre.txt` (frozen pre-image),
  `banc/l174b3/sec24_new.txt`, `banc/l174b3/lits24.json`,
  `banc/l174b3/premise.json`, `banc/l174b3/gate.json`,
  `banc/l174b3/draft_pre_b3.md`, `banc/l174b3/numbers_pre.json`,
  `banc/l174b3/raw/` (CERT-1 baseline + every post-edit verify run)
- verify: `paper/l149_verify.py` NEW section (22) makes the de-duplication
  permanent — it re-reads the stored literal list, re-asserts all 101 in
  §2.4, re-checks the byte-unchanged table, re-runs G1' span containment, and
  caps the section length so it cannot re-inflate
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B35 — L174 stage (b3b-i): bullets to prose in §1, §2.1, §2.2, §2.3

- claim: converting 15 of the draft's 42 bullet lines into prose is a
  FORMAT-ONLY transform, and it is proved so rather than asserted — the
  edited span's numeric-token multiset (355) and citation-key multiset (45)
  are IDENTICAL before and after. That contract is strictly stronger than
  stage (b2)'s relocation rule or stage (b3)'s de-duplication rule, both of
  which permitted a token to leave its block.
- branch B1_format_only (precedence put B2_tokens_moved first, as the silent
  failure); B3_literal_lost fired twice during construction and both times
  the PROSE yielded, never a gate
- scope: §1 Introduction (6 bullets), §2.1 (4), §2.2 (4), §2.3 (1). The
  remaining 27 bullets are sliced as (b3b-ii) §2.5/§2.6/§2.8 and (b3b-iii)
  §2.7.
- result: 15 bullet lines -> 0; 24 paragraphs; all 184 harvested verifier
  literals verbatim; the §2.2 scramble block (table + three numbered
  findings) byte-unchanged because a numbered enumeration is prose
  convention, not a bullet list; raw chars -2.48% (de-indentation) while
  VISIBLE chars +145, which is the honest direction for a pass that turns
  label-colon fragments into subjects and verbs
- method contribution — the literal-aware reflow: prose is re-wrapped to 78
  columns with every asserted literal treated as an unbreakable atom, so
  cosmetic line breaks can no longer break a gate (the l122 wrap-fragility
  lesson turned into a tool, reusable by (b3b-ii) and (b3b-iii))
- own-catch, and the tick's transferable lesson: run 1 harvested literals at
  a >=8-char floor, which dropped SHORT number phrases — the reflow then
  split `'0 of 20'` across a line and l149 went honestly red. A numeric
  MULTISET gate is blind to that class (both tokens survive; only their
  adjacency is lost), so the pre-image was restored, the floor lowered to 4
  chars with a punctuation-only filter, and the splice re-run: 184/184
  literals verbatim, zero wrap exemptions needed.
- two gates were made BREAK-INSENSITIVE rather than re-worded (claim text
  unchanged): l149's `'NOT\n  MET'` and l174's `'not that\n    identity
  matters'` depended on the old bullet INDENTATION. l174's four
  required/forbidden loops now normalize whitespace on both sides, which
  also STRENGTHENS the forbidden checks (a superseded wording cannot
  re-enter under a different line wrap).
- scripts: `banc/l174b3b/harvest.py` (freeze + literal harvest),
  `banc/l174b3b/emit.py` (block parse, rewrite map, reflow, gates,
  single-block splice, refuses to run twice), `banc/l174b3b/restore.py`
- artifacts: `banc/l174b3b/PREREG.md` (+ the slice rationale),
  `span_pre.txt`, `span_post.txt`, `span_post_run1.txt` (the rejected first
  splice, kept as evidence), `literals.json`, `emit_report.json`,
  `numbers_pre.json`, `raw/` (CERT-1 baseline + post-edit verify runs)
- verify: `paper/l149_verify.py` NEW section (23) re-derives everything from
  the frozen pre-image — bullet counts, both multisets, all 184 literals,
  the scramble byte-identity, the prose openers (normalized), the paragraph
  count and the visible-char delta — and pins the banner stage
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B36 — L174 stage (b3b-ii): bullets to prose in §2.5, §2.6, §2.8

- claim: the remaining prose conversion outside §2.7 is also FORMAT-ONLY and
  proved so — the edited span's numeric-token multiset (411) and
  citation-key multiset (37) are IDENTICAL before and after, under the same
  contract stage (b3b-i) registered.
- branch B1_format_only (precedence put B2_tokens_moved first); no literal
  was lost outside the three declared wrap-fragile ones
- scope: §2.5 (3 bullets), §2.6 (4), §2.8 (4). §2.7's 16 remain as stage
  (b3b-iii); §4/§5/§6 bullets belong to stage (b4).
- method contribution — a FROZEN SUB-SLICE inside the edit span: the span
  runs §2.5 through §2.9 and therefore contains §2.7, which belongs to a
  later slice. Rather than splicing two disjoint spans, §2.7 is frozen as
  `sev_pre.txt` and asserted byte-identical inside the new span. The
  single-block substitution proof of T4 survives intact, and the next slice
  inherits its material untouched. This promotes tick 208's scramble-block
  instrument from a sub-block check to a whole-subsection one.
- method contribution — DE-DASH BY PARSER: 8 of the 11 openers were already
  full sentences, so the map declares them `new=None` and the parser strips
  `- ` instead of a human retyping the line. Nothing that needs no
  re-authoring gets retyped, which removes the whole typo class from those
  blocks; only §2.5's three label-ish fragments were authored.
- result: 11 bullet lines -> 0 (span census 27 -> 16, all 16 §2.7's); 26
  paragraphs; 229 of 232 harvested literals verbatim; §2.7 byte-identical;
  the §2.8 robustness-panel table emitted de-indented and never reflowed
  (markdown tables are the one prose unit a reflow destroys); §2.8's four
  bold claim leads kept as paragraph lead-ins, which is the form §2.7
  already used twice, so the conversion adopts a house style already in the
  manuscript rather than inventing one; raw chars -0.57% while VISIBLE chars
  +48
- the three declared exceptions were found by the harvest BEFORE the
  rewrite: `'0.1946 / 0.0642 /\n  0.1333'`, `'agrees to\n  within .0025'`
  and `'from 37/33 to 6/2 but never\n  reach zero'` are §2.6 literals whose
  match depended on the old bullet INDENTATION. The l149 §(17) loop was made
  WRAP-INSENSITIVE (claim text unchanged) rather than re-worded — a
  normalized check is strictly stronger, since a literal can no longer hide
  behind a different wrap.
- own-catch, pre-splice: the block parser's frozen-region guard was written
  as `nb < sev_last`, which is correct for text BEFORE §2.7 and wrong for
  §2.8 after it — the §2.8 robustness panel's table then fell out of its
  bullet block and the P4 table gate caught it on the dry run, before any
  draft byte changed. A frozen-range guard must test MEMBERSHIP of the
  range, never a one-sided bound.
- disclosure: the span carries one 70-word sentence (§2.8's envelope
  disclosure). It is inherited, not authored here — it measured 71 words
  with the bullet dash counted — and belongs to the stage (b4) prose
  discipline. The longest sentence authored this stage is 41 words.
- scripts: `banc/l174b3bii/harvest.py` (freeze span + §2.7 sub-slice +
  literal harvest at the 4-char floor), `banc/l174b3bii/emit.py` (block
  parse across blank lines, rewrite map with parser de-dash, table-aware
  chunking, literal-aware reflow, gates, single-block splice, refuses to run
  twice)
- artifacts: `banc/l174b3bii/PREREG.md`, `span_pre.txt`, `sev_pre.txt`,
  `span_post.txt`, `span_post_preview.txt`, `literals.json`,
  `emit_report.json`, `numbers_pre.json`, `raw/` (CERT-1 baseline + the
  post-edit verify runs incl. the one honest l149 red)
- verify: `paper/l149_verify.py` NEW section (24) re-derives everything from
  the frozen pre-image — the 27 -> 16 bullet census with §2.7's 16 isolated,
  both multisets, all 232 literals with the exemption set asserted to be
  EXACTLY the three declared ones, §2.7's byte-identity and position, the
  table rows and one row's content, the four bold leads at paragraph starts,
  the absence of all eleven bullet openers, the three authored openers
  (normalized), the paragraph count and the visible-char delta — and pins
  the banner stage
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B37 — L174 stage (b3b-iii): bullets to prose in §2.7

- claim: the final prose conversion in §1-§2 is FORMAT-ONLY and proved so —
  §2.7's numeric-token multiset (248) and citation-key multiset (22) are
  IDENTICAL before and after, under the same contract stages (b3b-i) and
  (b3b-ii) registered. With it, §1-§2 carries no bullet list at all and
  stage (b3b) is complete.
- branch B1_format_only (precedence put B2_tokens_moved first); no literal
  was lost outside the seven declared wrap-fragile ones
- scope: §2.7's 16 bullets, the heaviest citation-key load in the body.
  §4/§5/§6 bullets and the inherited 70-word §2.8 sentence belong to stage
  (b4).
- method contribution — the RAW-PASSTHROUGH PROOF. Nine multiline verifier
  literals live in this span, but only seven are at risk: the other two
  (`"carrier's\n80"`, `'6 shared, Jaccard\n.037'`) sit in the non-bullet
  "Design pins" paragraph, which the transform passes through as raw lines.
  Asserting those two BYTE-exact while the seven bullet-internal ones are
  normalized turns the exemption into evidence: it proves the untouched
  paragraphs were never reflowed, rather than merely claiming it.
- method contribution — a RETIRED FREEZE BECOMES A FORWARD-CHAIN ANCHOR.
  Section (24) pinned §2.7 byte-identical against the LIVE draft, which is
  exactly what this stage changes. Rather than deleting that pin, it now
  asserts `sev_pre.txt == banc/l174b3biii/span_pre.txt` — tick 209's handoff
  proven against the NEXT stage's own frozen pre-image. That is strictly
  stronger than the live check it replaces, because it still holds after the
  section has been edited (the L120 forward-chain anchor form). The same
  re-scope moves (24)'s census, paragraph and visible-char pins onto its own
  edit region (span minus the live §2.7), so its measurement — 7 -> 16
  paragraphs, visible chars +48 — survives verbatim, and the §2.7-only
  literals are deferred to section (25) using the harvest's own `n_in_sev`
  field rather than a hand-written list.
- prose-discipline finding: `l159_verify` scans the ABSTRACT and §1 ONLY, so
  §2 has never been under the >60-word sentence rule. The stage-(d) anchors
  bullet carried a 67-word sentence (68 tokens with the dash) — a bullet can
  hold that, a prose paragraph should not, and this stage is what turns it
  into one. It is the one block re-authored over its FULL body (`eat=5`),
  split at its existing clause boundaries into three sentences with no token
  moved, and a NEW permanent §2.7-scoped 60-word gate now enforces the
  discipline l159 cannot see for §2. The next-longest, the stage-(c2)
  anchors sentence at 48 words, is disclosed and left INTACT rather than
  quietly rewritten.
- result: 16 bullet lines -> 0 (and §1-§2 as a whole 0); 19 paragraphs; 159
  of 166 harvested literals verbatim; both bold claim leads at line starts;
  the three non-bullet paragraphs unchanged; longest sentence 67 -> 52
  words; raw chars -0.2% while VISIBLE chars +108
- the seven declared exceptions were found by the harvest BEFORE the
  rewrite: `'follows the\n  GRAPH, not the gain'`, `'differ per seed by up
  to\n  .46'`, `'meanR\n  .798, kR 16/16, [.806,1.000]'`, `'(.477, kR
  8/16,\n  [.280,.720])'`, `'meanR .651, kR 15/16,\n  [.717,.989], paired
  −.147'`, `'+.474 above the twin-removed\n  graph with 16 of 16 seeds up'`
  and `'at g_cutng25p it is +.174 with 12 of\n  16 up'`. All seven are l149
  literals carrying the old bullet INDENTATION inside their own line break,
  in exactly three loops — §(11), §(15i) and §(16i) — each made
  WRAP-INSENSITIVE (claim text unchanged) rather than re-worded, as §(17)
  was one stage earlier.
- disclosure, scored predictions: Q2 predicted 0..5 wrap-fragile literals
  and the answer is SEVEN — §2.7 is the most number-dense subsection, so
  more of its gate literals straddle a line break. Q4 predicted that a
  MAJORITY of openers would need no authoring (8 of 11 one stage earlier)
  and only 3 of 16 did — §2.7 is a controls catalogue written as a table of
  verdicts, so `Label [key]: clause` is its native form. Both are properties
  of the SECTION, not misses in the machinery. Q1 (visible +50..+400) and Q3
  (l159 untouched) hold.
- own-catch: the gate splicer's idempotence guard tested the first 40
  characters of the inserted block, which are a `# ----` divider section
  (24) already carries, so it refused to run on a clean file. The guard
  token must be UNIQUE to the block it protects.
- scripts: `banc/l174b3biii/harvest.py` (freeze span + literal harvest at
  the 4-char floor), `banc/l174b3biii/emit.py` (block parse, rewrite map
  with parser de-dash, literal-aware reflow, gates, single-block splice,
  refuses to run twice), `banc/l174b3biii/gate.py` (splices section (25) on
  a unique opener with a count==1 guard)
- artifacts: `banc/l174b3biii/PREREG.md` (+ ADDENDUM 1 a/b/c written before
  the splice), `span_pre.txt`, `span_post.txt`, `span_post_preview.txt`,
  `literals.json`, `emit_report.json`, `numbers_pre.json`, `raw/` (CERT-1
  baseline + the post-edit verify runs)
- verify: `paper/l149_verify.py` NEW section (25) re-derives everything from
  the frozen pre-image — the 16 -> 0 census plus the §1-§2-wide zero, both
  multisets, all 166 literals with the exemption set asserted to be EXACTLY
  the seven declared ones, the two Design-pins literals BYTE-exact, both
  bold leads at line starts, the three non-bullet paragraphs, the absence of
  every pre-image bullet opener (derived from the pre-image, not listed by
  hand), the 3 de-dashed and 13 authored openers (normalized), the
  paragraph count, the sentence-length rule with both the 67-word pre-image
  and the 52-word result pinned, and the visible-char delta — and pins the
  banner stage
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B38 — L174 stage (b4-i): §4 Limitations to prose + the sentence splits

- claim: the §4 conversion is FORMAT-ONLY and proved so — §4's numeric-token
  multiset (166) and citation-key multiset (18) are IDENTICAL before and
  after, and so is the section's CONTENT-WORD SEQUENCE. With it, §1-§4
  carries no bullet list at all.
- branch B1_format_only (precedence put B2_tokens_moved first); no literal
  was lost outside two declared exception classes
- scope: §4's 10 bullets and the seven >60-word sentences inside them. §5
  (data availability, where a list is journal house style) and §6 (author
  notes, not a manuscript section) are deliberately NOT converted — their
  premise is tested in stage (b4-iii), not assumed from the card's summary
  phrase. The Discussion, the lane/batch-code and all-caps strip, the
  changelog banner and the inherited 70-word §2.8 sentence remain (b4-ii)
  to (b4-iv).
- method contribution — T7, the CONTENT-PRESERVING SENTENCE SPLIT. The seven
  over-length sentences live in BODY text, which the (b3b) opener-rewrite map
  cannot reach, so each is split by a declared (old, new) pair applied to the
  joined paragraph text before reflow. Each pair must match exactly once,
  must carry an identical numeric and citation-key multiset locally, and must
  leave the content-word sequence identical — where content words are all
  alphanumeric tokens outside a CLOSED connective set (`and`, `while`, `so`,
  `therefore`). The permanent gate proves it the strong way: the frozen
  pre-image with all thirteen declared edits applied (11 splits + 2 authored
  openers) must reproduce the live section's content-word sequence exactly,
  so an undeclared word cannot enter, leave or move.
- method contribution — a SECOND verifier-literal exception class. Tick 208
  found literals whose match depends on the old bullet INDENTATION; §4
  carries two whose match depends on the bullet MARKER itself (`'- DATA
  FLOOR:'`, `'- Wet-lab predictions'`). Those two are not content checks at
  all: they are l149 SLICE LOCATORS for the §4 floor-4 contract. They are
  re-pointed at the prose form anchored to a LINE START, which is equally
  strong (the labelled paragraph must still open its own line, and the
  locator can no longer match mid-sentence) rather than loosened.
- prose-discipline finding: §4 carried the LONGEST sentences in the
  manuscript — seven over 60 words, the worst at 107 — which the bullet form
  concealed because `l159_verify` scans the abstract and §1 only. Eleven
  clause-boundary edits bring the longest to 53 under a new permanent
  §4-scoped gate whose splitter PROTECTS abbreviations, so a false split at
  "Fig." cannot satisfy it. The one remaining offender in the body, §2.8's
  70-word envelope disclosure, is pinned as a DISCLOSED exception (measured
  per paragraph with table paragraphs excluded, so a flattened markdown table
  cannot mask it) and left for stage (b4-ii).
- result: 10 bullet lines -> 0 (and §1-§4 as a whole 0); 11 paragraphs; 135
  of 140 harvested literals verbatim; 8 openers de-dashed by the PARSER and
  only the 2 true fragments authored; longest sentence 107 -> 53 words; raw
  chars -2.9% and VISIBLE chars -14
- disclosure, scored predictions: Q1 predicted a POSITIVE visible-char delta
  (+50..+600) and the answer is -14 — SCORED WRONG, and instructively: a
  sentence split DROPS conjunctions (7 connectives removed against 2
  inserted), so the first prose stage of this lineage that edits sentence
  structure rather than line structure is the first one that shrinks. Q5
  (<25 inserted connectives) holds at 2 but for the opposite reason to the
  one predicted. Q2 (3..9 wrap-fragile literals) holds at 3, Q3 (l159
  untouched) and Q4 (a majority of openers need no authoring: 8 of 10) hold.
- own-catch: `emit.py` proved the content-word sequence PER SPLIT only, which
  is blind to the opener re-authoring; the permanent gate's whole-span form
  went red on the first run and was re-formed as "pre-image plus declared
  edits == live", which is strictly stronger. A per-edit invariant is not a
  per-section invariant.
- own-catch: the numeric regex swallows a TRAILING COMMA (it must, for
  thousands separators like 2,676,592), so the clause boundary that turns
  `'10-15, and'` into `'10-15. The'` read as a changed numeric token. A
  trailing comma is punctuation, which T7 is allowed to edit, so every
  numeric multiset in this stage is compared with trailing commas stripped
  while the DIGITS still compare exactly (PREREG ADDENDUM 2).
- scripts: `banc/l174b4i/harvest.py` (freeze span + literal harvest at the
  4-char floor + the sentence scan the split list is derived from),
  `banc/l174b4i/emit.py` (block parse, rewrite map with parser de-dash, T7
  splits with the content-sequence proof, literal-aware reflow, gates,
  single-block splice, refuses to run twice)
- artifacts: `banc/l174b4i/PREREG.md` (+ ADDENDUM 1 a/b and 2),
  `span_pre.txt`, `span_post.txt`, `span_post_preview.txt`, `literals.json`,
  `emit_report.json`, `numbers_pre.json`, `raw/` (CERT-1 baseline + the
  post-edit verify runs)
- verify: `paper/l149_verify.py` NEW section (26) re-derives everything from
  the frozen pre-image — the 10 -> 0 census plus the §1-§4-wide zero, both
  multisets, all 140 literals with the two exception sets asserted to be
  EXACTLY the declared members, the absence of every pre-image bullet opener
  (derived from the pre-image, not listed by hand), the 8 de-dashed and 2
  authored openers, each split's old form ABSENT and new form PRESENT, the
  whole-section content-sequence proof, the sentence rule with the 107-word
  pre-image and the 53-word result pinned, the §2.8 disclosed exception at
  70 words, the paragraph count and the negative visible-char delta — and
  pins the banner stage
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B39 — L174 stage (b4-ii): the Discussion, and the §2.8 closure

- claim: the manuscript gets a Discussion (§5), and the one >60-word sentence
  left in §1-§4 — §2.8's 70-word envelope disclosure, pinned by l149 §(26)
  precisely so closing it would be gate-visible — is closed
- prereg: `banc/l174b4ii/PREREG.md` (+ ADDENDUM 1: the registered raw-char
  prediction was derived for an em-dash-boundary split; the comma-boundary
  split actually used is byte-neutral, strictly stronger than registered)
- scripts: `banc/l174b4ii/harvest.py` (freeze §2.8 + harvest every verifier
  literal in it + the per-paragraph sentence scan, table paragraphs
  excluded), `banc/l174b4ii/emit.py` (the two edits, their gates, the
  length-preserving literal-aware reflow, the single-block splice; refuses
  to run twice)
- artifacts: `s28_pre.txt`, `s28_post.txt`, `disc_src.txt`, `disc.txt`,
  `literals.json`, `emit_report.json`, `numbers_pre.json`, `raw/` (CERT-1
  baseline, the dry run, the apply run and the post-edit verify runs)
- measured: ONE declared content-preserving split (`, so` -> `. So`) closes
  the 70-word sentence; §2.8's numeric (87) and citation-key (3) multisets
  identical, visible AND raw length identical, paragraph count identical, so
  l149 §(24)'s pins on the same region needed no re-point; all 69 harvested
  literals verbatim with ZERO exceptions; longest §2.8 sentence 70 -> 56,
  where 56 is an INHERITED sentence rather than a piece of the split. §5 is
  825 words over 7 paragraphs, longest sentence 52, born clean against stage
  (b4-iii)'s strip work and introducing no numeric value that is not already
  verbatim elsewhere in the draft
- verify: `paper/l149_verify.py` NEW section (27) re-derives both edits from
  the stored pre-images — the T7 strong form (pre-image + declared edits ==
  live §2.8), the content-word sequence, both multisets, byte/visible/
  paragraph neutrality, all 69 literals, the 70 -> 56 closure with the new
  longest sentence identified, then §5's existence, position between §4 and
  §6, paragraph count, the six T8 absence classes, the no-new-number proof,
  its own 60-word rule, the house width, the T9 required/forbidden strings,
  the §1-§5 zero-list-item fact, the two renumbered headings and the banner
  stage pin. §(26)'s 70-word pin is RE-POINTED at the stored pre-image
  (proved to have existed and to be gone), never deleted
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B40 — L174 stage (b4-iii-a): the lane-ID strip, the §6/§7 premise finding, and the frozen all-caps partition

- claim: §1-§6 and the References preamble carry no lane identifier and no
  internal-artefact reference, with every removal proved to be a removal of
  PROVENANCE and not of content; §6/§7 are settled by a registered premise
  test rather than converted; and the all-caps judgement the remaining strip
  stages need is derived ONCE and frozen
- prereg: `banc/l174b4iii/PREREG.md` (+ ADDENDUM 1: the inherited numeric
  harvest has no left word boundary and counts the digits INSIDE an
  identifier, so a strip stage fails a MEASUREMENT gate without moving a
  measurement — re-formed as measurement tokens plus the removed identifier
  digit runs asserted BY NAME; + ADDENDUM 2: the hand-built edit list was
  incomplete and the zero-residue gate named the miss; + ADDENDUM 3: T11
  re-formed to read the stored partition, since the caps regex also matches
  the very class this stage removes)
- scripts: `banc/l174b4iii/census.py` (the per-section lane/batch/caps
  census that forced the three-way slice), `caps.py`, `caps_partition.py`
  (the frozen partition, zero draft bytes touched), `harvest.py` (verifier
  literals at risk), `emit.py` (the 13 declared edits, their gates, the
  residue scan, the out-of-scope byte-identity; refuses to run twice)
- artifacts: `draft_pre.md`, `draft_post.md`, `caps_partition.json`,
  `literals.json`, `census.json`, `emit_report.json`, `raw/cert1_*.txt`
- measured: 13 lane-ID occurrences -> 0 in §1-§6 + the References preamble;
  13 declared edits; measurement multiset and citation keys IDENTICAL; the
  15 removed identifier digit runs asserted by name with none added; raw
  chars -101, visible -87; the §2.8 heading 109 -> 84 chars; one declared
  re-wrap is the only line-count change; partition of 179 distinct caps
  tokens (310 occurrences) into 18 KEEP / 23 DEFER / 138 STRIP
- premise finding (registered, not assumed): §6 Data & code stays a 4-item
  data-availability list because that is journal house style, and §7
  Author/submit notes is a note to the owner rather than a manuscript
  section — out of manuscript scope for every remaining strip stage, keeping
  its own identifiers by declaration and asserted BYTE-UNCHANGED
- gate: `l149_verify.py` section (28) re-derives all of it from the stored
  artefacts, including the T7 strong form (pre-image + the 13 edits == the
  live draft from the title onward, byte for byte), the zero-residue scan,
  the partition's own completeness/disjointness, the proof that every caps
  class this stage does NOT own is occurrence-identical, and the banner
  entry's numbers bounded to this stage's own censuses. Five inherited pins
  in §(23)/§(24)/§(25)/§(27) are RE-POINTED through the declared edits —
  never loosened and never deleted: the +145/+48/+108 visible-char
  measurements of (b3b-i)/(b3b-ii)/(b3b-iii) survive VERBATIM by decomposing
  each span's delta against this stage's own frozen pre-tick draft
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B42 — L174 stage (b4-iii-c-i): the all-caps de-emphasis of §1 and §4

- claim: §1 Introduction and §4 Limitations read as journal prose rather than
  as a lab log — no all-caps emphasis survives in either — and the edit is
  proved to have changed nothing but letter case anywhere in the manuscript
- prereg: `banc/l174b4iiic/PREREG.md` (T1'' de-emphasis-only with both
  multisets identical, T15 CASE-ONLY as the stage's strongest gate, T10
  zero-residue scoped to the two sections, T11' partition; branches
  C3_literal_lost > C2_meaning_moved > C1_deemphasis_only)
- premise finding (registered, read not assumed): a fresh live census after
  the (b4-iii-b) relabel shows §5 Discussion carries ZERO all-caps tokens of
  any class (stage (b4-ii) wrote it in the house form), so §5 is the style
  reference rather than workload; §3 Methods is a different KIND of job
  because four tokens there are MODEL SYMBOLS inside the state equation and
  the parameter table and one token splits by POSITION inside §3 alone (a
  licence name versus an emphasis phrase); and §2 Results is the bulk — so
  the stage was sliced by kind, not by size
- measured: 64 declared occurrences lowered (26 in §1, 38 in §4); title-onward
  length identical with exactly 412 differing bytes, every one an uppercase
  letter replaced by its lowercase self; visible-character and byte deltas
  EXACTLY ZERO; measurement and citation-key multisets identical with no named
  removal and no named addition (tick 213 needed 15 named removals, tick 214
  needed 11 named mapping rows); §2 Results and everything from §5 onward
  byte-IDENTICAL; KEEP survivors pinned (§1: CPG, CPG-, IN12B003, S07, XOR;
  §4: BANC, BANC', EMG, XOR)
- method contributions: a LITERAL HARVEST CANNOT SEE a gate whose pattern is
  built by regex or taken from a token list — two such gates broke after the
  harvest reported clean, and a second-order scan (`harvest2.py`) was needed
  for the escape-sequence and section-SCOPED classes the first harvest missed
  (the changelog banner quotes the edited prose, so a whole-draft presence
  test passes while a §4-scoped gate fails); LINE-START IS NOT SENTENCE-START
  in a hard-wrapped draft (the first rule capitalised seven mid-sentence wrap
  openers, caught by reading the previous line); a global file-level string
  replace cannot tell a literal quoting the LIVE draft from one quoting a
  STORED PRE-IMAGE (one pre-image side was lowered and restored); and nested
  literals must be re-pointed LONGEST FIRST or the short form rewrites the
  long one's interior
- gate: permanent as `l149_verify` section (30), with §(23)/§(26)/§(29)
  re-pointed through this stage (case-insensitive literal images plus the
  retired all-caps form asserted ABSENT — strictly stronger than either check
  alone, and bounded by (30)'s whole-draft case-only proof)
- scripts: `banc/l174b4iiic/{census.py,scope.py,plan_i.py,harvest.py,harvest2.py,emit.py,sec30.py}`

### B41 — L174 stage (b4-iii-b): the batch-code relabel and the §3.7 mapping

- claim: the manuscript body no longer quotes internal batch codes, yet the
  disclosure they carried (which paired comparison ran within which batch) is
  preserved exactly, by a bijective reader-facing label scheme plus one
  declared mapping block in Methods
- prereg: `banc/l174b4iiib/PREREG.md` (T1' relabel-only with both multisets
  identical, T12 bijection + mapping, T13 artefact keys are FILENAMES and stay
  byte-exact, T14 declared reflow; branches R3_literal_lost >
  R2_measurement_moved > R1_relabel_only)
- premise finding (registered, read not assumed): the `B<n>` shape covers TWO
  semantic classes and tick 213's frozen partition conflated them — `B1-B4` is
  a PREREGISTERED BRANCH range, not a batch — so the partition is AMENDED
  (DEFER_BATCH -> KEEP_MAPPING 11 + DEFER_BRANCH 1, still 179 distinct tokens)
  rather than applied, and (b4-iii-c) must KEEP the codes inside the mapping
  block
- design choice, with its reason registered: labels are LETTERS, not numbers,
  because a letter adds no digit run (so the measurement gate needs no new
  exclusion class — the (b4-iii-a) ADDENDUM-1 lesson) and because the labels
  sit beside seed counts where a numeric label invites a misread; I and O are
  skipped; the order is the internal codes' own run order, which keeps the
  draft's "fresh batch X" claims monotone in the label
- scripts: `banc/l174b4iiib/census.py`, `classify.py` (the three-class
  classification, purely syntactic), `harvest.py` (verifier literals at risk,
  tested in BOTH overlap directions), `plan.py`, `reflow.py`, `emit.py` (19
  declared substitutions, 2 declared reflows, 1 mapping insertion, 14 gates;
  refuses to run twice), `sec29.py`
- artifacts: `draft_pre.md`, `draft_post.md`, `classify.json`, `plan.json`,
  `reflow.json`, `literals.json`, `emit_report.json`,
  `caps_partition_amend.json`, `raw/cert1_*.txt`
- measured: 39 `B<n>` occurrences classified as 19 BATCH prose / 6
  ARTEFACT_KEY / 4 BRANCH / 10 banner / 0 §7; 19 substitutions (6 bare, 13
  `batch <letter>`); measurement multiset and citation keys IDENTICAL; the 19
  removed identifier runs and the 11 entered mapping rows asserted BY NAME;
  body-only raw delta +40, mapping block 589 chars, title-onward +630; both
  re-wrapped paragraphs keep their line counts; five verifier literals
  re-pointed with their measurements still attached
- gate: `l149_verify.py` section (29) re-derives the whole transform from the
  frozen pre-image by the stage's own parsed rule (never from emit.py's
  report), proves the T7 strong form byte for byte from the title onward,
  scans the LIVE draft for residue, re-reads the §(28) lane-ID property on
  live bytes, and pins the bijection, the amendment and every delta; §(22)
  through §(27) are RE-POINTED through this stage's declared edits and its own
  frozen pre-tick draft, so (b3b-i)'s +145, (b3b-ii)'s +48, (b3b-iii)'s +108,
  (b4-i)'s -14 and (b4-iii-a)'s -25/-51/-15/21 all survive VERBATIM with the
  relabel's cost split out
- zero rollouts, zero RNG, no measured value changed, numbers.json
  byte-identical

### B43 — L175: the single-cell scan on the k=24 base and the drive-matched twins (batch B39, n=16 per arm)

- claim: of the 34 single-cell removals from ladder ranks 25-58 on the k=24
  base, only the carrier (rank 25, DNp33-L) meets the registered super
  criterion; neither delivered-drive twin does, and no other active window
  cell does, including the seven that deliver more than the carrier
- disclosed with it: the mass twin is silent on the cut base, the silent-cell
  null is wide, and the null covaries with the re-bisected gain
- keys: l175.scan l175.null l175.branch l175.verdict l175.bands l175.certs l175.census l175.meta
- prereg: `banc/l175/PREREG.md` (branch order E0 > D1 > D2 > D3; branch
  D2_identity_carried fired)
- artifacts: `banc/l175/results_l175.json`, `banc/l175/L175-FINDINGS.md`,
  `banc/l175/selection.json`, `banc/l175/static.json`
- gate: `paper/l183_verify.py` re-derives every scan-table cell from the
  stored json and replays the fold

### B44 — L184: shared timing, not rhythmic gain (zero rollouts, stored scan batch)

- claim: the carrier-removed arm keeps most of its chopped-window duty when
  flexor and extensor traces are paired across DIFFERENT runs, and it is the
  one scan arm with a substantial continuous 1.4-Hz duty; mean pool rates and
  a uniform change in drive transmission do not account for the flip
- keys: l184.threepanel l184.design l184.q3 l184.q3_ratios l184.q1 l184.q1_twins l184.sens l184.anatomy
- prereg: `banc/l184/PREREG-analysis.md`
- artifacts: `banc/l184/threepanel.csv`, `banc/l184/q3.csv`, `banc/l184/q1.csv`,
  `banc/l184/q1-contrasts.csv`, `banc/l184/sensitivity.csv`,
  `banc/l184/edges.csv`, `banc/l184/overlap.csv`, `banc/l184/L184-FINDINGS.md`

### B45 — L185: fresh-batch replication, gain-only null, signed-current twin (batch B40)

- claim: the carrier flip replicates on a fresh batch at the re-matched gain
  AND at the base's own gain; every twin and the base stay below the super
  band in both gain forms; a gain-only sweep of the base moves its duty with
  no cell removed; a signed-current-matched twin does not flip
- keys: l185.base l185.r1 l185.r2 l185.r3 l185.branches l185.certs l185.meta
- prereg: `banc/l185/PREREG.md` (+ `banc/l185/PREREG.sha256`)
- artifacts: `banc/l185/results_l185.json`, `banc/l185/L185-FINDINGS.md`,
  `banc/l185/selection_s2.json`

### B46 — L186: the gate-jitter discriminator (16 paired jitter schedules) — UNRESOLVED

- claim: the deletion contrast survives re-alignment to the jittered gate, but
  neither clock (gate-aligned vs elapsed time) wins by the registered margin;
  the registered jitter is smaller than the readout window, so the run is
  underpowered for the discrimination and the status is stated as unresolved
- keys: l186.means l186.contrasts l186.phase l186.branch l186.power
- prereg: `banc/l186/PREREG.md`
- artifacts: `banc/l186/results_l186.json`, `banc/l186/L186-FINDINGS.md`,
  `banc/l186/t216_power.json`, `banc/l186/t216_verify.json`

### B47 — L187: relay silencing and cut, push-pull, occlusion (batch B41)

- claim: neither registered pole — removing the downstream interneuron on the
  carrier's route raises the chopped duty by itself but without the carrier's
  1.4-Hz signature, the carrier's effect survives the relay's removal, the
  opposite-sign input does not cancel it, and a relay clamped from t = 0 is the
  relay-cut graph by construction
- keys: l187.base l187.arms l187.contrasts l187.relay l187.branches l187.sc40_pooled l187.sc25_pooled l187.certs l187.fast l187.gain_slopes l187.relay_rate l187.g74914_rate l187.meta
- prereg: `banc/l187/PREREG.md` (+ `banc/l187/PREREG.sha256`)
- artifacts: `banc/l187/results_l187.json`, `banc/l187/addendum.json`,
  `banc/l187/L187-FINDINGS.md`

### B48 — L183 master fold: paired twin inference, substrate census, parsed weight rule

- claim: on the 66 seeds the mass twin ran on, the twin-vs-base contrast is
  not resolved by the paired exact test (the pooled-margin p = .008 is kept as
  a pooled statement only); the simulated network is the deafferented closure
  defined by the census; edge weights are signed log1p synapse counts with
  the glutamate override and the inhibitory scale, as parsed from source
- claim (Table 4): the cohort ladder re-scored in the continuously driven
  1.4-Hz segment on its canonical pools is no longer a window — the closure,
  the base and the cuts below it show no structured seed, carrier removal
  keeps 132 of 210, the k = 58 cut is the strongest cut arm and the heaviest
  carrier-free cohort drops out of the class; the chopped column of the same
  stored rows reproduces l172.pooled exactly for all eleven arms
- keys: l172.paired_twin l92.substrate l135.weights l183.ladder_fast l183.ladder_fast_meta
- artifacts: `banc/l172/stats.json`, `banc/l92/static.json`,
  `banc/l135_run.py`, `banc/build_graph_banc.py`,
  `paper/review_fable_evidence_r2/out_duty_rows.json` (+ its script
  `paper/review_fable_evidence_r2/p1_duty_from_raw.py`)
- referee inputs: `paper/review_fable_r2.md`, `paper/review_astra_r3.md`,
  `paper/review_claudeai_fable_20261121.md`, `paper/priorart_terra_20261121.md`
- gate: `paper/l183_verify.py` (fold replay from the stored pre-image
  `banc/l174b4iiic/draft_post_preview.md`) and `paper/l174_verify.py` (7)

## How to re-verify the whole package

```
cd ~/critters/peabrain-lab
python3 paper/l161_verify.py   # this map: coverage, paths, provenance walks
python3 paper/l149_verify.py   # draft quotes == stored jsons (10 sections)
python3 paper/l143_verify.py   # mechanism table + numbers.json == sources
python3 paper/l158_verify.py   # abstract numeric vocabulary freeze
python3 paper/l159_verify.py   # sentence-length gate
python3 paper/l174_verify.py   # references + bidirectional citation gate
python3 paper/l183_verify.py   # master fold: byte replay of the declared edit
                               # ledger from the stored pre-image, no
                               # hand-typed number, added keys re-derived
```

Since the master fold (v3.32) the draft body is built, not typed:
`python3 paper/l183_emit.py` writes `DRAFT.md` as the pinned changelog banner
plus `l183_fold.build_body(numbers.json)`, i.e. the stored pre-image
`banc/l174b4iiic/draft_post_preview.md` under the declared renumber and the
declared edit ledger `paper/l183_text.py`. To change the manuscript, change
the ledger (or `extract_numbers.py`) and re-emit; a hand edit of `DRAFT.md`
fails the replay in l183, l149 (31), l158 (11) and l174 (8d).
