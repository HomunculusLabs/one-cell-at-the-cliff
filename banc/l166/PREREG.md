# L166 — F-axis HELD-OUT pre-registration (honesty debt from L162 ADDENDUM 3)

Written **BEFORE** any held-out number is read. Tick 230, 2026-11-22.

## 1. The debt, stated exactly

L162 ADDENDUM 3 (`l162/addendum3.json`, instrument `l162c_phase.py`) reports an
F axis — *within-rollout* magnitude-squared coherence (MSC) at the .100 Hz
segment bin — as:

    F1_carrier_coherent  clears-f 23/28 carrier vs 2/36 control
    med MSC 0.6961098419357329 (carrier) vs 0.18493588764305458 (control)
    analytic floor 1/K = 0.200, calibration_ok = True, both files same side
    per file: l154 23/28 (ctl 2/36) 0.6595985215890314 / 0.19000325984303945
              l150 24/28 (ctl 2/36) 0.7189227147072201 / 0.16455886214390858

and labels itself **DESCRIPTIVE-STRONG** because the *recombination* (which
bars, which counts, which calibration window) was written with that table in
hand. The components were pre-registered; the recombination was not. Per the
L88/L90 re-basing rule the claim is not citable until the SAME bars survive on
data the recombination never saw.

## 2. The bars, pinned unrounded, before the held-out read

**Partition** (NOT re-derived per arm — the b65-derived partition IS the claim
under test): re-derive from `l157/static.json` with `l162_static.py`'s own
`wilson_lb` (Z = 1.959963984540054) by

    CARRIER = pools with wilson_lb >= 0.5        (expect 8)
    CONTROL = pools with below <= 6              (expect 9)

asserted equal to the stored lists, never quoted. 28 carrier pairs, 36 control
pairs.

**Instrument**: `l162_static.py` lines 1-106 and 206-218 are EXEC'd as a
verbatim source slice (sha256 recorded) — `seg_vec` (Hann, SEG 2000, HOP 1000,
K = 5, BIN_SEG = 2 = .100 Hz), `msc_matrix`, `pair_read` (matched = diagonal,
shuffled = off-diagonal), `clears`. No re-transcription (L85).

**F-axis bars** (exactly `l162c_phase.py` lines 103-124):

    clear_f(pair)   := msc_matched_med >= 0.5
    n_clear_f       := #clear_f over the 28 carrier pairs
    F1 iff  n_clear_f >= 22  AND  med_carrier >= 2.0 * med_control
                             AND  calibration_ok
    calibration_ok  :=  0.5*FLOOR <= med_control <= 2.0*FLOOR,
                        FLOOR = 1/K = 0.2 exactly  ->  [0.1, 0.4]
    F2 iff  n_clear_f <= 7 ;  else F3_mixed

Comparator for a single 18-seed batch is the **per-file** stored pair (23/28,
24/28), not the 36-seed pooled 23/28.

## 3. Held-out sets, with their strength stated honestly

- **H1 PRIMARY — fresh batch B44, seeds 4401-4418 (18, matching per-file n).**
  b65 arm only, `l166_run.py` = `l164_run.py`'s certified extraction with the
  `rnd` arm removed. Anchors 801/901 re-run and required BIT-IDENTICAL to
  `l150/raw_l150.npz` stored b65 (max|d| = 0.0) before any B44 trace is read.
  This is the true L88/L90 re-basing: same condition, data that did not exist
  when the recombination was written.
- **H2 SECONDARY, WEAK — the l154 `off` arm.** Its MSC rows ARE stored in
  `l162/static.json["i1"]` and were printed by `l162_static.py` (line 399) at
  the time, so it is *held out from the recombination* but not unseen.
  Descriptive confirmation only; it can never carry the re-basing.
- **H3 SECONDARY, FREE — the six remaining l150 arms** (full, cutwA, cutng25,
  silW, eMotTop5, eMotBot5). MSC has never been computed on them anywhere.
  Carries L165's scoping debt onto this instrument.

## 4. Pre-registered predictions

- **Q1 (primary)** H1 lands F1 with n_clear_f >= 22 and calibration_ok.
  *Predicted CORRECT*: L165 already showed b65's across-seed lock replicates on
  disjoint batches (.9840 B33 vs .9838 B34); MSC is a within-rollout read of the
  same drive-locked line.
- **Q2** H2 (`off`) lands F2 (n_clear_f <= 7). *Predicted CORRECT but not
  certain*: L165 put the off arm's across-seed PLV at the free floor, and MSC is
  a DIFFERENT instrument (within-rollout, no cross-seed phase) — within-rollout
  coherence could survive drive removal via shared broadband noise. A non-F2
  here is a real finding about the instrument, not a failure of the card.
- **Q3** H3: the carrier-vs-control separation FAILS or INVERTS (med_carrier <
  2*med_control, or med_control > med_carrier) on >= 4 of the 6 lesion arms —
  direct transport of L165's PLV_self non-transport to the MSC instrument.
- **Q4 (fold rule, registered in advance)** DRAFT §4 fold happens IFF Q1 passes.
  The folded sentence MUST carry both inherited qualifiers: (a) L164 — the
  protocol is phase-pinned, so this is drive-*following* coherence, never an
  intrinsic clock; (b) L165 — if Q3 holds, the sentence is scoped to the b65
  substrate and may not say "carrier pools" unqualified.

## 5. Branches

- **B_REBASED** — Q1 passes: the DESCRIPTIVE-STRONG label is discharged to a
  held-out-confirmed claim, fold per Q4 with qualifiers.
- **B_SHRUNK** — H1 n_clear_f in [8, 21] (F3): no fold; the draft text is
  re-scoped to the measured count.
- **B_LOST** — H1 n_clear_f <= 7 (F2): the recombination does not survive
  re-basing; the claim is withdrawn and reported against myself.

## 6. Discipline

One object per gate cell (L109): the count bar, the ratio bar and the
calibration bar are reported SEPARATELY and the failing one is named. Floor
report before any counterfactual (L146). C0A-166 is a HALTING anchor — 64
stored pooled MSC values + the 6 stored F-axis aggregates must reproduce to
float equality from the stored npz BEFORE a single held-out value is computed.
Op point asserted per seed (L30). Raw B44 checkpointed before analysis (L43).
No live change, no draft edit in this tick; the fold itself is a draft-writing
item and the draft is in owner-handoff state, so a passing Q1 ships the fold as
a card, not as an edit.
