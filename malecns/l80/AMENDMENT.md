# L80 — L57 substrate-contract amendment: structure row goes WINDOW-SCOPED (parked for the owner)

Status: **PROPOSAL — parked for the owner on BBS bill/agent-bbs#54.** The live L57
table in LAB-INTENT.md is unchanged until his word (L75 precedent). Evidence
re-derived this tick from STORED artifacts only (L44 rule): l77/results_l77.json,
l79/results_l79.json (both census n=16, seeds 11,22,33,101-113); l59 numbers
carried by l77's bit-identical anchors (23rd/25th chain anchors).

## Why (the evidence trail)

- **The pooled gate is a fair coin under EVERY tested intervention.** l59:
  P(pooled duty >= .5) = 8/16 BOTH schedule arms, Wilson [.28,.72]. l77 adds
  the echo arms: hynohop_fb 8/16 [.28,.72], hybrid_fb 10/16 [.386,.815] — no
  pooled Wilson lower bound clears .5 in any of four arms. l79's re-prime
  arms even LOWER pooled (.460/.432 vs .489/.513).
- **The 0.7-seg window is where interventions reproducibly move structure.**
  l77: echo lifts duty_07 mean .547 -> .673 (nohop family, +.126) and
  .569 -> .649 (hybrid, +.080); floor lifts too (min .297 -> .437,
  .317 -> .447); S_L rescue at seg0 (.445 -> .579). Lock stays pristine
  (seg1 err <= .01: 16/16 all four arms). Echo budget 12.7-12.8% of
  entrain mass.
- **The fast-seg (1.4 Hz continuous) window is entry-state-conditional and
  has NO known positive lever.** L52: from chopped entry the fast lock is
  free; from continuous entry structure collapses (duty {.24/.16/.12} ->
  {0/.1/0}). l77: echo leaves it untouched-to-worse (seg1 .375 -> .292 /
  .402 -> .298). l79: the L58 chop-gap re-prime — structure-forming on the
  0.7 chop — is TOXIC inside 1.4-continuous (W_post .249 vs twin .411,
  paired -.162, 13/16 non-pos; d_early negative from the first
  straddle window, deepening with dwell to -.223 = no re-formation
  signature). Second protocol-bound instance: drive-regime numbers do not
  port between protocols in either direction.

## BEFORE / AFTER (contract rows)

### Row C4 (before, tail)

> "...structure gates go DISTRIBUTIONAL/window-scoped — P(window duty >= .5)
> with CI, duty07 >= .7 mean, drive on the Pareto edge (spec handed to kanban
> t_7fa32128, L61)"

### Rows C4a/C4b/C4c/C4d (after — C4 split into its four commitments)

| # | Contract row (what a controller may/must do) | Lane | The number that matters | M/X |
|---|---|---|---|---|
| C4a | TRACKING row: seg1 err <= .01 per seed. Tracking is FREE — never trade structure for it | L51/L59/L77 | 16/16 seeds <= .01 in ALL four l77 arms (errs .0001-.0027); 13/19 l58 cells lock 3/3 | M |
| C4b | STRUCTURE row, WINDOW-SCOPED: gates read duty_07 (the 0.7-Hz chopped segs) ONLY, distributional form P(duty_07 >= .5) with Wilson 95% CI at census n=16 + mean/min reported. ONE measured lever: the L66 content-cell echo (g .1, NEGATIVE, delay 50 ms; budget ~12.7% entrain mass) — lifts mean +.126/+.080 AND the distributional head 11/16 lb .444 -> 15/16 lb .717 (nohop family). MALE substrate only — L78: does not transport to female BANC (donor sham carries 96% there) | L59/L66/L77/L78 | duty_07 mean .547/.569 -> .673/.649; P(>=.5) 11/16 [.444,.858] -> 15/16 [.717,.989] (nohop); hybrid 13/16 [.570,.934] both; min .297 -> .437 | M |
| C4c | FAST-SEG structure row: 1.4-Hz-continuous-window duty is ENTRY-STATE-CONDITIONAL (L52) and is NOT a gate — report as diagnostic. No tested lever rescues it: echo untouched-to-worse, chop-gap re-prime TOXIC (drive-regime non-portability, 2nd instance). ONE untested positive shape remains: L34 reflex-arc re-host (L81, opposite sign) | L52/L77/L79 | seg1 .375 -> .292 (echo), .411 -> .249 W_post (re-prime, paired -.162, 13/16 non-pos, no re-formation); L81 pending | M |
| C4d | POOLED duty_all: DEMOTED to a reported diagnostic, never a gate — a fair coin owned by the attractor gas (L70: left-biased lottery, per-seed re-roll) under every tested intervention | L59/L70/L77/L79 | 8/16 [.28,.72] both l59 arms; 8/16 + 10/16 [.386,.815] l77 fb arms; no pooled Wilson lb >= .5 anywhere | M |

### Row D5 (amendment text appended)

> D5 tail adds: "endgame-schedule evidence (L77): the echo does NOT bias the
> pooled coin (10/16, coin-compatible) — its benefit is duty_07-scoped
> (C4b); female BANC replication FAILED as content (L78: donor sham carries
> 96%, lock cost real, R3 no-harm fails every dose) — the cell keeps its
> MALE-ONLY flag and never-a-default label."

## Disclosures

1. **P(duty_07 >= .5) Wilson reads are derived POST HOC this tick** from
   stored l77 arrays (the .5-threshold form was pre-registered for POOLED in
   l59; applying it to duty_07 is this amendment's proposal). Numbers are
   motivating evidence, not a pre-registered pass. Wilson unadjusted for the
   4-arm family.
2. **No donor-sham arm on the HYBRID schedule**: L66's content certification
   (sham -.001) ran on the nohop/l55 schedule; l77's hybrid_fb has echo
   on/off only. The C4b lever claim leans on the nohop-family sham +
   bit-identical wiring (C0x cross-run probe). A hybrid-schedule sham is the
   one symmetry run still open if the owner wants it (cheap: 2 arms x 16 seeds).
3. L81 untested — if reflex-arc re-host lifts the fast window, C4c upgrades
   from "no lever" to "one lever, opposite-sign"; amendment revisits.

## What this buys the endgame (kanban t_7fa32128)

A learned CX-side controller gets gates it can actually OWN: tracking (free),
0.7-window structure (real lever + distributional headroom 11/16 -> 15/16),
fast-window honesty (diagnostic until a lever exists), budget stated on the
Pareto edge. No more gating on a coin.
