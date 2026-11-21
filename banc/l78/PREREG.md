# L78 PREREG — banc-echo-replication (registered 2026-11-15 04:5x, BEFORE any rollout)

Card: LANE.md ideas-38 L78. Question: does the male content-cell echo
(g .1, sign −, delay 5 steps = 50 ms; L64/L66) have a counterpart on the
FEMALE BANC cord, or is L57 row D5 male-only? 3 anchor seeds; census only
if content carries (slice B).

## Substrate (l68 extraction verbatim, no re-derivation)
- banc_graph.pt subnet: n=21,249 / 627,051 edges / glut->INH sign (L65 arm B),
  G=.14, BETA=2.0, D=.2 on DNg100 (2 cells), TAU .05, DT .01, RMAX 1,
  BG .02, NOISE .01, SETTLE 400, WIN 6000, SEGB 0.7/1.4/0.7 Hz.
- mech = vnc sensory tactile+proprioception (4,848 cells).
- Pools per side: Tr (31-31 flex / 24-24 ext) AND Ti (50-51 / 6-6).
- Schedule = l68 hyb01 AMPA table VERBATIM (chop 500-on/900-period slow segs,
  continuous fast seg, ENT_AMP .1, settle at arm amp, settle phase @0.7 Hz).

## HEADROOM derivation (from STORED l68/l68/results_l68.json, L44 rule —
## this is why the female read is NOT the male read)
- Ti pair: bilateral-healthy at ceiling (duty_07 .94/1.0/1.0) -> no lift
  headroom; Ti becomes the NO-HARM read.
- Tr pair: SIDE-SPLIT, real headroom — slow-seg duty .019/.34/.059-.107
  (seg0) and .018-.059 (seg2); Tr SL median NEGATIVE (-.18/-.00/-.41 seg0,
  -.29/-.14/-.15 seg2) while Tr SR healthy (.53-.75). The male's marginal
  side was SL too (open SL .326 vs SR .153) — the rescue question
  transposes: can an echo move female Tr SL above 0 with SR preserved?

## Arms (5, ONE shared-noise group per seed, ONE generator, X0 drawn once;
## echo OFF during settle (k<0), enters drive[mech] AFTER sin_term from
## k >= delay; echo source = ANTAG mean = Tr{fL,fR,eL,eR} pooled, male form)
1. open    — hyb01 replica (anchor arm)
2. fbn_g01 — gfb .1, sign −1, delay 5   (literal male content cell)
3. fbp_g01 — gfb .1, sign +1, delay 5   (sign re-derivation; L65: sign
              conventions are graph-empirical — glut flipped male->female,
              the echo winner is NOT assumed to transfer)
4. fbn_g03 — gfb .0333, sign −1, delay 5 (BUDGET-MATCHED: male echo/entrain
              ratio at amp .3 scales to amp .1 -> .1*(.1/.3); the literal
              cell on female is ~3x male's 12.7% budget)
5. sham_g01— donor sham, gfb .1, sign −1, delay 5; donor = NEXT-seed cyclic
              hyb01 ANTAG-mean trace from l68/raw_l68.npz (11<-22, 22<-33,
              33<-11), same schedule, mass-matched, content-free (l66 form)

Seeds 11, 22, 33 (l68 anchor seeds).

## Registered reads
- R1 PRIMARY headroom: Tr duty over slow-seg windows (both sides >= .25,
  300-step rolling S sampled every 10 steps; chop OFF windows
  (500,900),(1400,1800),(4500,4900),(5400,5800) AND full slow segs
  excluding first 500 steps). Open baseline registered above.
  CONTENT = lift(fb − open) > 0 on >= 2/3 seeds AND sham lift <= 0.5 x fb
  lift on the same window.
- R2 side-rescue: median Tr SL over slow segs > 0 in >= 2/3 seeds with
  Tr SR median >= .25 preserved (male L66 signature transposed).
- R3 no-harm ceiling: Ti duty_07 per seed must stay >= open − .05
  (open .94/1.0/1.0). Drop beyond = TOXIC branch (L63 form).
- R4 lock (female spectral form — razor lock known dead, l68): per-seg
  dom_freq ratio; fb arms must keep ratio >= 0.5 x open ratio per seed.
- R5 budget: mean|echo| / mean sin_term over drive-on steps; expect
  fbn_g01 ~3x male 12.7%, fbn_g03 ~12.7% (report, no gate).

## Anchors (explicit KEY enumeration only — L59/L77 rule)
- C0a BIT-IDENTITY: open arm == l68/raw_l68.npz hyb01 for keys mm + Tr/Ti
  x {fL,fR,eL,eR} x seeds {11,22,33}: max|d| == 0.0 (adding arms to the
  shared-noise group must not move a shared arm — L45b/L77 form).
- C0P first divergence of MOTOR mm (fb arms vs open): registered value 6
  (echo enters mech at k=5; mm reads motor one hop downstream — derived
  from l66 STORED results_l66.json first_div==6 every seed, NOT from the
  log sentence; L77 rule).
- C1 af assert per arm post-settle: 0.01 < af < 0.9 (l68 form).
- C2 dm probe: every fb/sham arm must diverge from open (max|d mm| > 0)
  — a bit-identical treatment arm means wiring leak/dead channel (L35/L39).

## Verdict shapes (pre-registered)
- CONTENT-GENERALIZES: R1 or R2 passes (any arm) under its sham control
  -> slice B census n=16 + budget-matched sham before any L57 edit.
- MALE-ONLY: no arm lifts, no harm (R3/R4 clean).
- TOXIC: R3 or R4 crash — female echo harmful at these doses (L63 form).

No live changes. sessions/ untouched. Raw npz checkpoint BEFORE analysis.
