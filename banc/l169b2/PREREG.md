# L169 stage (b2) PREREG — the floor-4 DYNAMIC arm

Registered 2026-11-20 ~06:45 EST, BEFORE any computation of this stage.
Lane tick 193. Parent card: LANE.md L169 (ideas 87, external-review
pre-posting controls). Stage (b1) = banc/l169b (static premise test +
design pins). This stage spends rollouts.

## Question

Referee issue I6 asked whether the identity cliff survives a synapse
floor. (b1) refuted the "frozen membership" premise and stored the design
pins. This stage asks the DYNAMIC question the static census cannot:

at the strongest admissible pair-level synapse floor (>= 4), does adding
the single carrier cell to the cut window still flip the antagonist-duty
readout from PARTIAL to SUPER, and does its mass-matched twin still not?

## Substrate convention (registered)

The floor acts on edges, not nodes: node set = `keep_new` (the l92/l107
closure) VERBATIM, edge set = closure edges with pair-level summed
`syn_count >= 4`. This is exactly the convention the stored l146 ladder
used (`closure_edges = (emask_n & pm).sum()`, `pm = w_syn >= floor`), so
the (b1) pins apply unchanged. Node-set re-derivation under the floor is
explicitly NOT done (it would change K, the cohort and the pools at once);
scope every number below to this convention.

## Arms (3 new; 9 inherited arms ride along)

Ladder re-derived at floor 4 (F3 form, the one (b1) certified):
`ng4` = non-glut heavy cohort in descending floor-4 out-mass order.

- `f4wA`  — closure @ floor 4, cut `ng4[:20]` (carrier INTACT; the f4
  analogue of cutwA, per (b1) pin P3 `intact_k = 20`).
- `f4ng`  — closure @ floor 4, cut `ng4[:21]` (carrier DNp33-L gi 1110
  INCLUDED at f4 rank 21; the f4 analogue of cutng25, pin `cut_k = 21`).
- `f4tw`  — closure @ floor 4, cut `ng4[:20] + ng4[21]` (the mass-nearest
  f4 twin DNpe005-R gi 290, f4 rank 22, mass gap 2.4e-05 per pin P4; the
  f4 analogue of cutng25p). NOT a positional prefix by construction.

Each f4 arm gets its OWN fresh af-matched bisect to AF_T =
0.10905611018339793 (never a ported gain, L118-L131 criteria).

Inherited arms (full, b65, cutwA, cutng25, silW, eMotTop5, eMotBot5,
wAgN, n25gW) are kept in ARMS for forward-chain anchors and the
stored-gain certification; nothing about them is re-claimed here.

Batch: FRESH B36 = 3449-3464 (n=16), anchors 801/901 first. Seed range
verified absent from all 81 stored raw npzs by key scan before registration
(L157 rule: enumerate from stored KEYS, never batch-number memory).

## Metric (inherited verbatim, no new instrument)

`duty_07` per side on the Ti antagonist pair over the 0.7-Hz windows, the
l109/l111/l113 rounding path (round per seed, then mean) as implemented in
l169_verdict.py. Per arm: `kR` = seeds with R-side duty >= .5 of 16,
`meanR`, `meanL`, `kL`, Wilson 95% on kR/16.

House classifiers (verbatim from l169_verdict.py):
- SUPER:   meanR >= .60 and kR >= 12
- PARTIAL: .35 <= meanR <= .50 and 3 <= kR <= 8
- NOT-SUPER (control form): kR <= 8 and meanR <= .50

## Certification block (must be green BEFORE any B36 value is read)

- CERT-1 (forward chain, L120 form): the 9 inherited arms at seeds
  801/901 are BIT-IDENTICAL to `l169/raw_l169.npz` (max|d| == 0.0 over
  mm/xm + 20 pool traces + af). Adding arms consumes no generator draws,
  so a non-zero here = stream break = VOID.
- CERT-2 (also the subset certification, C0-SUB): the inherited
  stored-form bisects re-land EXACT — g_cutwA == 0.14365819573402408,
  g_cutng25 == 0.1454454553127289, g_eMotTop5 == 0.1436134350299835,
  g_eMotBot5 == 0.14367126345634465. This stage restricts `settle_states`
  to the arm under bisect (L139 spectator law applied to the bisect, arms
  are independent and the noise draws are global) — these four EXACT
  re-landings are the certification that the restriction is a no-op.
- CERT-3 (static pins): the floor-4 re-derivation inside the run script
  reproduces `l169b/static.json` F3 field-for-field — K == 73, n_ng == 55,
  carrier rank == 21, twin-319 rank == 33, jaccard == 0.9231, closure
  edges == 472095, wA edges == 469256, prefix masses .1988/.2342/.2405/
  .2649 — and `ng4[21]` == gi 290 (DNpe005-R) with |mass gap| rounding to
  2.4e-05.
- C0-NT (non-triviality): each f4 arm's `mm` trace at 801/901 must differ
  from its base counterpart (max|d| > 0) and from the other two f4 arms.
  A bit-identical pair = the floor or the cut never entered the step loop
  = VOID (L35/L39 dead-channel class).
- P-af: each f4 arm's settled active fraction is within 5e-3 of AF_T;
  the staircase residual |af - AF_T| is DISCLOSED, never assumed 0.

## Registered outcome branches

- **G1_cliff_survives_floor4** — `f4ng` SUPER and `f4wA` NOT-SUPER and
  `f4tw` NOT-SUPER. The identity cliff (carrier, not mass) reproduces on
  the floor-4 substrate; the I6 robustness question is answered
  dynamically in the affirmative.
- **G2_no_transfer** — `f4ng` not SUPER. The cliff does not express on the
  floor-4 substrate; the published static robustness is then a
  STATIC-ONLY property and §4's scope clause must say so (L94 class:
  substrate-rule-specific, never ported).
- **G3_position_route** — `f4ng` SUPER and `f4tw` ALSO SUPER. At floor 4
  the 21st window slot flips regardless of which cell fills it = the
  identity claim is floor-contingent and the honest wording is
  window-position sufficiency at this floor.
- **G4_mixed** — anything else (e.g. f4wA already SUPER = window
  re-ordering moved the base rate). Report the cells, claim nothing.

Negative/degenerate-pass guards: if `f4wA` is already SUPER the XOR is
VACUOUS (L55 class) and the branch is G4 with that fact stated first; a
branch may not be read from a label, only from the measured cells.

## Scope and honesty constraints

- n = 16, ONE batch (B36). Any number entering the draft is labelled
  single-batch; no pooled Wilson across batches is claimed for the f4
  arms (the base arms' pooled numbers are untouched).
- The floor-4 substrate deletes 27.14% of closure edges. Per L94, a
  structure result measured on one substrate rule does not port to
  another; the f4 arms are compared to EACH OTHER at their own matched
  operating points, never to base-substrate magnitudes.
- Re-ordering is part of the treatment, not a confound to remove: (b1)
  showed the f4 window is a re-ordered prefix (23 of 24 base cells
  present). Any G1/G3 wording must say "at the f4-re-derived window".
- Fold rule: fold into DRAFT §4's data-floor scope clause (and §2 if G1)
  ONLY if CERT-1/2/3 + C0-NT are green. Otherwise journal the blocker and
  leave DRAFT.md + numbers.json untouched.
