# L52 PREREG — why-is-fast-segment-toxic (ideas-25)

Written BEFORE any run. Registered anchors re-derived from STORED artifacts
(`l49/traces_l49.npz`, cont arm), not from log summaries (L44 lesson).

## Question

L50 measured the continuous-1.4-Hz segment as structure-TOXIC
(allw seg1 duty .022 vs free .538). Is that collapse a RE-LOCK TRANSIENT
that settles with dwell (L41's transient reading) or a SELECTED attractor
held for the whole segment (L41's selection reading)? Decides whether a
structure-preserving fast gait needs DWELL or is impossible at amp .3
(and whether a different ENTRAIN AMP — L34's knob — buys it).

## Design

Lineage substrate verbatim (l49/l50/l51): 21,516 nodes / 2,977,920 edges,
G .01 / beta 2 / D .05, DT 10 ms, TAU .05, BG .02, NOISE .01, SETTLE 400
(0.7 Hz, amp .3), shared h40 history [0,4000) = 0.7 Hz amp .3 continuous.
Treatment window [4000,10000) = 60 s, NO transitions inside, no hops, no
stop. One generator + shared per-step noise tensor, X0 drawn once per seed
and cloned per arm (L36/L45b rule). Seeds 11/22/33.

Arms (7): frequency x amp over treatment —
f07a3 (the control + ANCHOR arm: schedule-identical to l49 cont through
step 10000), f07a2, f07a1, f14a3 (canonical toxic arm), f14a2, f14a1.
Phase: single accumulator per arm, continuous across settle/history/
treatment, stepping at the arm's treatment frequency from k=4000 (l39
convention; f07 arms reduce exactly to l49's 0.7 ramp).

## Metrics

Per-side rolling antagonist S (500-step window, every 10 steps; l51 form).
duty(bin) = fraction of TS samples in bin with BOTH SL >= .25 and SR >= .25.
Bins: 10 x 600 steps (6 s) over treatment; early = [4000,7000) (first 20 s),
late = [7000,10000) (last 20 s); slope = duty_late - duty_early.
Lock: dominant mm frequency over treatment halves and full window;
locked iff |f_hat - target| <= .10 (l39 convention).

## Gates (pre-registered)

- C0 ANCHOR: f07a3 mm bit-identical to l49/traces_l49.npz mm_cont over
  [0,10000), max|d| == 0.0, 3/3 seeds; SL/SR arrays equal too (same
  computation on identical traces). Any nonzero -> run VOID, fix wiring.
- C1 WIRING: af in (0.01,0.9) all arms/seeds; write-time AMPA/phase table
  asserts; dm probe first_div(f14a3 vs f07a3) == 4000 exactly 3/3 (the
  frequency step must land).
- GC CONTROL: f07a3 duty over [4000,10000) reproduces the stored-artifact
  values {.360, .645, .112} (s11/s22/s33) — derived 11-13 from
  l49/traces_l49.npz on THIS window (140-s-window values .16/.43/.56 do
  NOT apply; L34 window lesson).
- G_TRANSIENT (f14a3): duty_late >= .25 AND slope >= +.20, 3/3 seeds.
- G_SELECTION (f14a3): duty <= .10 in EVERY 6-s bin AND duty_late < .15,
  3/3 seeds.
- Otherwise MIXED: deliver the per-seed/per-bin table.
- Sensitivity (t70 field rule): full amp x freq table with
  {duty_early, duty_late, slope, lock err, verdict label}; the canonical
  (.3) verdict is labeled HOLDS / SHIFTED / FLIPS at .2 and .1.

## Registered predictions

- P1: f14a3 = SELECTION (L41: the disturbance SELECTS the post-transition
  attractor; L50's uniform .022 across the segment supports held-low).
- P2: GC passes exactly (anchor identity).
- P3: 1.4 lock degrades with amp (L34 Arnold tongue) — if f14a1/f14a2 do
  not lock (err > .10), the toxicity question is moot at that amp (no fast
  gait exists to hold structure IN); label those cells UNLOCKED.
- P4 (band, no gate): 0.7 arms at .2/.1 stay within duty [.05,.70].

## Verdict shape

TRANSIENT -> "fast gait needs dwell, budget ~recovery time";
SELECTION -> "impossible at .3; the amp table says whether any amp buys
both lock and structure"; MIXED -> seed table, no single number.

## ADDENDUM 1 (run-1 C0 failure, disclosed before rerun)

Run-1 C0 FAILED (mm diffs .08-.13 vs l49 cont): my settle applied the
0.7-Hz amp-.3 mech drive during SETTLE (the l39/l50/l51 convention), but
l49's settle is a PURE intrinsic settle — the mech drive is guarded by
`k >= 0` and starts at window step 0. Two settle conventions coexist in
the lineage; the anchor arm must match l49's. Fixed; no analysis of run-1
was read beyond the C0 numbers (registered VOID rule). Phase accumulation
(400 settle steps + per-arm window increments) is order-identical to l49's
precomputed PHI for the 0.7 arms.

## ADDENDUM 2 (run-3 outcomes, disclosed)

Run-3 C0 PASS (12th consecutive chain anchor): f07a3 mm AND SL/SR
bit-identical to l49 cont [0,10000), max|d| 0.0 x9 arrays. Run-2's
residual divergence was a DOUBLE settle phase (explicit pre-accumulation
loop + step_all's own k<0 increments; ph_end 475.0 = 10,800 increments vs
457.4 = 10,400) — caught by ph_end arithmetic after mm[0]-equal/mm[1]-
diverge localized it to the step-0 drive. GC run-gate compared 10-decimal
duty against the 3-decimal REGISTERED values at 1e-9 (s33 .1117 vs .112)
— recomputed at registered precision (5e-4): PASS, and the boolean duty
arrays are EXACTLY equal to l49 cont's (stronger than registered).
Formal verdict stays MIXED (neither pre-registered gate fired); the
dwell-deepening reading is labeled post-hoc in results_l52.json.
