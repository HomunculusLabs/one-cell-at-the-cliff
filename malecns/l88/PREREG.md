# L88 PREREG — fresh-seed replication of a pre-registered 2-feature mid-seg rule
(ideas 44; the GO condition L87 itself registered: "2-feature follow-up must
pre-register on these cells + FRESH-seed replication")

Question: does the lineage's strongest realizability signal (L87 fork features,
|rho| .735 dd07-vs-SL / .535 ds1-vs-SR) cash out as an ONLINE 2-feature rule on
FRESH seeds? Split-sample design: rule family + thresholds fixed on the census
16 (stored l87 cells only), gates scored ONCE on 16 fresh seeds (501-516) that
no chain run has ever touched.

## Phase 1 — stored-only search (no rollouts)
- Features verbatim l87 fork_feats on the 4 fork bases (hynohop, hynohop_fb,
  hybrid, hybrid_fb) recomputed from l87/raw_l87.npz: SL2500 = median SL over
  TS∩[2300,2500), SR2500 same, mm2500 = mean mm over [2400,2500).
- CERTIFICATION (before any new number): the recomputed features must
  reproduce all 24 STORED single-feature rules in results_l87.json exactly
  (k, seg1_mean, picks per seed) — else addendum, nothing else runs.
- 2-feature family (96 rules): fork (4) x feature pair ({SL,SR}, {SL,mm},
  {SR,mm}) x per-feature condition (v>=thr or v<thr, 4 combos) x combiner
  (AND, OR). thr = CENSUS median of that feature at that fork (frozen —
  policy, not oracle). Latch iff combiner(cond1, cond2).
- Census scoring of a rule = per-seed pick (latch or base) scored on the
  picked arm's stored cells: d07 = duty_07, s1 = segs[1].duty,
  lock = segs[1].err <= .01. k = #(d07>=.5); Wilson(16).
- Selection order (deterministic, registered): sort by
  (census_clears DESC, seg1_mean DESC, k DESC, rule_index ASC) where
  census_clears = (16/16 picked lock) AND k>=15 AND wilson lb>=.717 AND
  seg1_mean>=.358. Winner = rank 0; runner-up = rank 1. Both recorded
  BEFORE phase 2. If NOTHING census-clears: the rank-0 rule still goes
  fresh (confirmatory; expected NO-GO disclosed here).
- G4 note: bases are echo-free or fb (ratio .127); latches are strict
  subsets of fb's echo — per-seed ratio <= .127 by construction (asserted
  in code, not a discriminator).

## Phase 2 — rollouts (l87 machinery verbatim, CPU)
- Roll ONLY the winner fork's two arms: base + its latch@2500. Seeds:
  census 16 (validation) + fresh 501-516 (deliverable). One generator per
  seed, shared per-step noise tensor across arms (l87 form).
- The rule applies ONLINE: features read from the BASE arm's in-flight
  trace at K=2500 (window [2300,2500) is prefix-identical between the two
  arms by the latch law, so the decision is well-posed mid-run); census
  thresholds frozen.
- Anchors (all must pass before any verdict read):
  - C0V census re-roll BIT-IDENTICAL to raw_l87.npz for both arms, all 16
    seeds: mm + fL/fR/eL/eR + mA where applicable (33rd chain anchor).
  - C0F latch law on BOTH batches: latch-vs-base prefix max|d| over [0,2500]
    == 0.0 AND motor first-divergence == 2501 EVERY seed (l86/l87 law).
  - C0E feature certification (phase 1, above).
  - C1 settled af in (0.01, 0.9) every arm/seed both batches.
  - C0M entrain_mass == l87 meta pinned value.
  - Degenerate (L55 rule): if the latch is bit-identical to base on any
    FRESH seed (dm==0), that seed's branch does not exist — disclose; the
    rule is scored as-is (a dead branch reads as base) AND the degeneracy
    is reported; if it flips any gate, verdict = NO-GO-degenerate.
- Gates scored ONCE on fresh 16, WINNER ONLY (multiple-testing guard; the
  runner-up's fresh numbers are reported only if it shares the winner's
  fork — same two rollouts — and are labeled DESCRIPTIVE, never the GO call):
  G1 = 16/16 picked lock; G2a = k>=15 AND Wilson lb >= .717;
  G3 = picked seg1 mean >= .358; G4 = DRIVE_ON 4800 + per-seed echo
  ratio <= .127 on the picked EON/traces.
- GO for the endgame = G1 AND G2a AND G3 AND G4 on fresh. A fixed rule that
  clears IS the policy (training optional; L89 holdout confirm card).
  NO-GO closes the 2-feature class: C4b echo lever + C4c diagnostic stand;
  L80 amendment final pending the owner.

## Registered expectations (directional, L55 spirit)
- E1: the census winner uses SL2500 (the .735 carrier), most likely at a
  nohop fork. If the winner ignores SL, the L87 signal did not cash into
  the rule class — report as signal-decay.
- E2 (honest): census-clearing is knife-edge at best (single-feature best
  k15/.329; 2-arm union oracle k16/.359) — the registered prior is that
  phase 1 finds a census-clearing rule only via selection bias, and fresh
  seeds expose it. Either outcome is the deliverable; no re-tuning on
  fresh, no second fresh batch.
