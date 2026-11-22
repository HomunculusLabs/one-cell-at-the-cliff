# L207 VERDICT — the avoidance is the CELL TYPE, not the ladder slot

Branches: **Q1 = B_NEITHER** (registered letter) / **Q2 = M_AVOIDS**.
Predictions 3 of 4. Static, zero rollouts, 17 s, CPU.
PREREG: `l207/PREREG.md` (registered before any value was read).
Artifacts: `l207/{PREREG.md, static.json, VERDICT.md, run.out, run.err}`.
Code: `l207_{build,tail}.py` -> generated `l207_static.py`.

## Headline

Across three substrates on which the carrier (gi 1110, **DNp33-L**,
acetylcholine, pure-projecting descending) occupies **two different ladder
slots**, its lam1^2-normalised depth-2 per-out-mass reach into the 20
semantic motor pools is 3.2e-05 / 3.2e-05 / 4.4e-05 — **rank 5 of 58
(closure), 5 of 34 (cutwA), 3 of 35 (f4wA)**, a 6.5-6.9x deficit against each
cohort's median — while the cells that OCCUPY its slots sit mid-pack
(**gi 80 at closure slot 21: pct 0.351; gi 32072 at f4wA slot 25: pct
0.235**) and ladder slot does not predict R anywhere
(**rho = -0.089 / -0.047 / +0.292**, all inside the registered |rho| < 0.5).

And the leg that turns this from a negative into a positive: the carrier's
**contralateral homolog gi 928 = DNp33-R avoids at least as hard** — pct
**0.060 on all three substrates** against a tight mass-matched cohort of 100
present descending cells (log-mass spread <= 0.12), R 2.3e-05 against a
cohort median 4.3-4.8e-04 = a **~20x** deficit; the carrier on the same
cohort rule reads pct 0.090-0.100 and ~15x. Both members of the bilateral
DNp33 pair are in the bottom ~6-10% of mass-matched descending cells on every
substrate.

**So: not a slot, and not an individual cell either — a cell-TYPE property.**

## Why the branch reads B_NEITHER anyway (the honest part)

B_CELL required carrier pct <= 0.10 on all three substrates. It is 0.070 /
**0.121** / 0.059. The cutwA miss is **one cohort step**: with 33 other
present ladder cells, one rank = 0.030, and the carrier is rank 5 there
exactly as it is rank 5 on the closure ladder (the same 4 cells are below
it). The registered bar was written for cohorts of 58 and applied to a cohort
of 34; that is a **resolution** failure of my bar, not a change in the cell.
Reported as B_NEITHER because that is what I registered, with the shape named:
carrier low-and-stable on all three, slot occupants mid-band, no slot
structure — i.e. the DATA fall in B_CELL's shape and miss B_CELL's threshold.

## Magnitudes do not transport between nulls

L206 measured the carrier at **percentile 0.0 / ~10.4x** against 100
degree-neutral destination swaps. Against the **ladder cohort** here it is
6.5-6.9x at pct 0.06-0.12, and against the **mass-matched descending cohort**
~15x at pct 0.09-0.10. Same cell, same statistic, three nulls, three
magnitudes. The rewire null is the only one that holds the cell's own
out-degree and out-strength fixed; the two cohort nulls are comparability
cohorts and nothing more. Never quote one magnitude as the other's.

## Substrate invariance (unregistered, worth keeping)

Carrier R is 3.20548e-05 on the closure and 3.20568e-05 on cutwA — removing
the 24 heaviest ng ladder cells (3,776 edges) moves the normalised statistic
by 6e-05 relative. The floor-4 substrate moves it to 4.4e-05 (+38%), i.e. the
syn>=4 floor matters and the ladder deletion does not.

## Q3: structurally unanswerable on this volume pair, and now sliced

Both cells DO carry inline v783 matches (carrier 720575940604103084, mirror
720575940633165452), so the identification is free. But v783 is a
**brain-only** volume: the 831 motor cells this statistic reads into have no
counterpart there, so the measurement cannot be made, let alone transported
(L78). Sliced to L212 rather than answered with a substituted statistic.

## Certification (all GREEN before any L207 value was read)

- **CERT-HEAD1** l151_static.py 1-319 VERBATIM, sha256 `e6245e8306dc8a0f` —
  identical to the head sha L178/L205/L206 recorded, asserted a literal
  PREFIX; the whole L151/L142/L134/L92/L101 pin set re-ran free.
- **CERT-HEAD2** l178_tail.py 7-149 VERBATIM, sha256 `6e2e8fa4bd19eced` —
  CERT-F4 in full (K4 73, carrier rank 21, twin gi 290, gap 2.44e-05, f4wA
  n 21,789 / edges 469,618, family 33) + the three stored gains at FLOAT
  EQUALITY + CSR orientation (carrier out 69 / in 12) + all 20 pool sizes.
- **MID** l206_mid.py, sha256 `febbc390ad4f`.
- **CERT-HEAD3** l206_tail.py 22-121 VERBATIM, sha256 `29a830839ebc7837` —
  **CERT-178 HALTING: 420 stored anatomical values reproduced by FLOAT
  EQUALITY** (35 actors x depths 1-3 x P/S/per-mass/PI) plus lam1(A_abs) =
  30.179788 by power iteration (rel spread 1.18e-16).
- **CERT-GEN (HALTING, new)**: the generic substrate builder, reach_sub and
  power_iter_sub reproduce the certified f4wA specialisation at float
  equality — 44 checks: CSR row/col arrays and |values| by `array_equal`,
  pool-local index arrays and their KEY ORDER, reach_sub == reach() per depth
  per pool, the G-scaled form == L178's stored carrier/twin P1/P2, and
  power_iter_sub == LAM1 exactly. Only then were G0/G1 built.
- **GAIN-INVARIANCE asserted numerically**, not in prose: lam1 rel diff
  1.18e-16, depth-2 rel diff 1.31e-16, so the cross-substrate comparison
  needs no per-substrate gain bisect.
- Substrate pins asserted: G0 n/edges == S92 (21,809 / 647,953), G1 21,785 /
  644,177, f4wA 21,789 / 469,618; all 20 pool sizes invariant with zero L/R
  overlap on all three; carrier slot 25 in ng_desc and 21 in ng4 asserted;
  the PREREG's claim that slot-21's occupant is REMOVED on cutwA asserted
  (not discovered); homolog identity cross-checked annotations vs l169c
  P2_hom_identity.
- No lab module imported (L175). Forbidden-token audit on all three slices.
- Writes `l207/static.json` ONLY. sessions/ untouched. No live change.

## Limitations (as registered)

Anatomical leg only — wiring geometry, not an operating point (L164). Walks
with revisits, not paths. Crofts/Estrada leg not run (PREREG-disclosed).
Percentile resolution differs across cohorts (1/33 = 0.030). The mirror leg
is a mass-matched COHORT percentile, never the l169c rewire null. Each
substrate is scored against the ladder it was derived with — the carrier's
slot difference (25 vs 21) IS the design.

## Predictions, scored

- Q207-1 **WRONG**: registered B_CELL, measured B_NEITHER (by one cohort
  step on the smallest cohort; shape correct, threshold missed).
- Q207-2 CORRECT: |rho(slot, R)| < 0.5 on all three (-0.089 / -0.047 / 0.292).
- Q207-3 CORRECT: M_AVOIDS — and the mirror avoids HARDER than the carrier.
- Q207-4 CORRECT: Q3 unanswerable by volume regardless of match ids.
