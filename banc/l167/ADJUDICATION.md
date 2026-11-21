# L167 stage (a) — adjudication of the fable-5.2 referee report

Run 2026-11-20 ~01:35-02:1x EST. PREREG: `banc/l167/PREREG.md` (verdict
vocabulary + evidence rule registered before any read). Script:
`banc/l167/l167_adjudicate.py`; full output `banc/l167/run.out`; machine-readable
`banc/l167/adjudication.json`. Zero rollouts. DRAFT.md and numbers.json
UNTOUCHED this stage (mtimes still 2026-11-19 21:44 / 21:36).

CERT block passed before any verdict printed: our Wilson reproduces the
ledger's stored `pooled.cutng25` lb/ub to 5e-5 and l150's full-precision `lbR`
to 1e-9; Fisher self-tests exact on a symmetric and a disjoint 2x2.

## Verdict table (issue -> verdict -> finding -> our artifact)

| # | Verdict | Finding re-derived from OUR artifacts | Artifact |
|---|---------|----------------------------------------|----------|
| 1 | CONFIRMED | 0 scramble mentions in DRAFT, 0 scr keys in numbers.json; our own cutscr0 = **39/48** right-side [.681,.898] over 3 batches with kL 12/10/13 also high => the carrier is **sufficient, not unique**, and cutscr0 is not the crossed state | banc/l125,l127,l128/results_*.json:table.Ti.cutscr0 |
| 2 | CONFIRMED (methodological) | our male extraction applies **no synapse floor** (zero floor filters in l138 code) while the BANC release carries an implicit floor of **3** => the 28-cell/K=9 male cohort is an UNMATCHED-floor comparison. The reviewer's matched-floor 342/K=52 stays REVIEWER-REPORTED | banc/l138_static.py + numbers.json:l146.release.min |
| 3 | CONFIRMED | drive IS chopped in code (500 of every 900 steps in both 0.7-Hz segments, middle segment full-on) and our Methods states **neither the chop nor any drive waveform**. Independent convergence with our own L162 (evoked + echo-locked) | banc/l135_run.py:AMPA block + banc/l162/static.json |
| 4 | CONFIRMED (direction) / PARTIAL (attribution) | stored gains vs g_cutwA=.1436582: flip arms +1.06..+1.30% (cutng25 +1.244, eOutInt +1.297, eIn +1.087, eAll +1.244, eOutAll +1.238, eMotIn +1.062) vs non-flip ±0.03% (eMotTop5 −.031, eMotBot5 +.009) and eOutMot −0.568%. **silW flips at g_cutwA unchanged** => gain is a real untested confound but cannot be the whole mechanism | banc/l1*/results_l1*.json:g_* (scanned) |
| 5 | CONFIRMED | per-set carrier-vs-twin Fisher from our own l139 table: set0 14v9 p=.113, s1 16v13 p=.226, s2 16v5 p=7e-5, s3 13v6 p=.029, s4 14v0 p≈0, s5 13v13 p=1.0 => contrast clear in **3 of 5 jitter sets** though cutng25 stays SUPER 5/5; the ±8% gain span is the **untreated** arm's | banc/l139/results_l139.json |
| 6 | CONFIRMED (scope) / REVIEWER-REPORTED (floor-4 re-derived) — **SCOPE COMPONENT LATER REFUTED, see the L169(b1) correction below** | code check: the cohort array is defined **1x before** the floor loop and **0x inside** it => our floor robustness (rank 21, Jaccard .9231) is conditional on **frozen membership**, which the draft never says | banc/l146_static.py + numbers.json:l146.f4 |
| 7 | CONFIRMED | twin 12/32 vs base 43/144 Fisher **p=.406** (underpowered, not a demonstrated null); the draft's "−.088 inside the .075 sham spread" is **false on its face**; our own l156 rows = **518 traces from 449 unique seeds** (18 seeds repeat across files) => the census is pseudo-replicated | numbers.json:pooled.cutng25p,l150.pooled,l137.g1/g3 + banc/l156/static.json:rows |
| 8 | CONFIRMED | abstract still quotes superseded pools 20/64 and 47/48 while the body carries 43/144 and 124/128; the mass ratio prints 12x but recomputes to **9.72x** (.0544/.005599); "kill→super" labels a PARTIAL→SUPER step => prose-vs-ledger drift the value-equality gates cannot see | paper/DRAFT.md + numbers.json:l142.h2a.mass |
| 9 | CONFIRMED | our own B26 table: on the lesion arms (cutwA, cutng25) every non-tibia pair is **exactly 0/16 on both sides**; the only non-zero non-Ti counts are on the untreated baseline (`full`: Tr 0/6, Sr 0/4, Ta 2/0) => readout scope is **one antagonist pair of five** | banc/l135/results_l135.json:table |
| 10 | CONFIRMED (editorial) | §2.4 (3.4k chars) presents two bit-identities as findings though both hold by construction; sil24 kR=5 is not separable from its intact comparator => rebuild §2.4 on silW and demote the identities to Methods | paper/DRAFT.md §2.4 + numbers.json:l137.sil24 |
| 11 | CONFIRMED | measured: 37 bullet lines, 81 distinct all-caps tokens, **1** numeric citation marker in text, abstract **3,964 chars** (arXiv cap 1,920), **no update equation** => still a skeleton | paper/DRAFT.md (counted) |
| 12 | CONFIRMED (analytic) | Fig 1 panel-A text says "monotone" while the draft argues NON-monotone; script batch label "B17-B26"; the +.334 annotation conflicts with the text's +.371 => stale labels, print redraw needed. Reviewer had NO vision (6/7 calls failed) so contrast/point-size findings remain analytic | banc/l136/l136_fig.py, paper/l152_fig2.py, banc/l160/fig_l160.py |

**Score: 12/12 CONFIRMED at least in direction.** Two carry an explicit
REVIEWER-REPORTED component (I2 matched-floor male ladder, I6 floor-4
re-derived membership) that may not enter the draft until we reproduce it.
Nothing in the report was REFUTED. The core twin-XOR claim is untouched and
the reviewer re-scored it in our favour (124/128 vs 12/32, their p=1.2e-13 —
our own recompute of the same table gives the twin-vs-base p=.406 that makes
the *neutrality* wording, not the XOR, the thing to fix).

## Five defects I caught in my own adjudication script (disclosed)

Run 1 printed all 12 verdicts; four of them had no data behind them, and a
fifth was self-contradictory. All five were caught before any report:

1. **I5 printed "0/0 sets"** — a recursive path matcher returned `{}` and the
   verdict text rendered a confident sentence over an empty dict. Fixed to read
   `results_l139.json:sets.<set>.<arm>.kR` directly with `assert len(sets)==6`.
   This is the L55-class failure (a verdict that cannot fail) in its worst
   form: a *fabricated-looking* pass. **New house rule: any verdict string that
   interpolates a collection must assert that collection non-empty first.**
2. **I8/I11 measured the wrong text** — `draft.split("\n## ")[0]` captured the
   title block, not the abstract (2,730 vs the real 3,964 chars), so the
   stale-pool checks read False on a draft that does carry them. Fixed with a
   heading-anchored locator + a length assert.
3. **I10 truncated §2.4** at a 2,600-char cap before its bit-identity
   sentences, reading False on a section that contains them. Fixed to the
   `### 2.4 ... ### 2.5` span with a length assert.
4. **I6 regex matched a COMMENT** ("S4 ladder re-derivation") and reported
   membership as re-derived — the exact opposite of the code's behaviour.
   Fixed to count cohort-array definitions before vs inside the floor loop.
5. **I3 was self-contradictory** ("the draft never states it (mention found:
   True)") because `duty.cycle` matched the READOUT's duty metric. Fixed to ask
   the precise question of the Methods section only.

Lesson (one line, transferable): **a verdict-table script needs the same
locator/assert discipline as a metric script** — grep-shaped evidence must be
anchored and length-asserted, and an interpolated collection must be asserted
non-empty, or the table reads confident where it is blind.

## What this stage deliberately did NOT do

No DRAFT.md edit, no numbers.json edit, no figure redraw, no rollout, no use of
the reviewer's rewritten abstract. Response cards seeded as ideas 87
(L168-L174). All five paper verify scripts re-run ALL GREEN after the tick.

## CORRECTION (L169 stage b1, 2026-11-20 tick 192) — I6 scope component REFUTED

My own I6 check counted cohort-array definition *sites* before vs inside the
floor loop. The per-floor cohort in `l146_static.py` is re-derived inside the
`ladder()` **function** (called once per floor), which a before/inside-loop
site count cannot see — the same heuristic class that already mis-read a
comment in run 1. Re-derived under our tree
(`banc/l169b/static.json`, PREREG `banc/l169b/PREREG.md` registered first,
rule E1 fired):

- an ast parse of `ladder()` shows `K`, `heav_f` and `ng_desc_f` all assigned
  inside the function body; `ladder(4)` reproduces the stored
  `S4_ladder.f4` field-for-field (CERT-3).
- a genuinely FROZEN form (F1: base cohort, base order, f4 masses) returns
  carrier rank **25** and twin **26** by construction. The published f4
  numbers are **21 / 33**, so the stored artifact is NOT the frozen form.
- new decomposition: freezing the cohort SET and re-ordering alone (F2)
  already gives 21 / 33, so the carrier's rank shift is **re-ordering**, not
  cohort turnover (turnover is 5 cells out / 1 in, K 77 → 73,
  Jaccard 72/78 = .9231).

Score update: **11/12 CONFIRMED, 1 CONFIRMED-with-its-scope-component-
refuted**. The reviewer's floor-4 re-derived NUMBERS remain
REVIEWER-REPORTED and barred from the draft. What the draft genuinely owed
and now carries (§4 DATA FLOOR, v3.10): an explicit statement of what the
f4 ladder re-derives, plus the honest label that f4 is a **static bound**
with no dynamic arm run (stage b2 debt). Design pins for b2 are in
`banc/l169b/static.json:pins` — at f4 the XOR window becomes cut-first-20
vs cut-first-21 over a re-derived ladder (base window ports 23 of 24
cells), and the carrier's mass-nearest f4 neighbour is DNpe005-R at rank 22
(gap 2.4e-05), because the base twin DNpe025-R falls to rank 33.
