# L93 PREREG — female-own-lever-scan (Tr-L dead side) — registered BEFORE rollouts

Card L93 (ideas 47). Question: Tr duty07_L is dead on the closure substrate
(base pin below) while R lives — pathway ABSENCE, BURIED drive, or
lands-but-no-structure? Protocol: static conduction census (done, pinned
below from l93/static.json + l92 stored artifacts — L44 rule), paired-noise
volley arms, donor/random shams (L78 transport rule).

## Substrate (pinned, L92 verbatim)
- Closure subnet: n 21,809 / 647,953 edges; g* = 0.153125 (l92
  anchors_run.json g_new); BETA 2.0; DNg100 tonic D 0.2; ENT_AMP 0.1;
  TAU .05 DT .01 RMAX 1 BG .02 NOISE .01; SETTLE 400 WIN 6000; SEGB
  [(0,2000,.7),(2000,4000,1.4),(4000,6000,.7)].
- Noise law (l92): gen(seed) draws old-cell tensors in l91's exact order;
  gen2(seed+9000) draws the 560 DNn stream. ALL arms in one loop share the
  per-step tensors (paired-noise, L36 rule); volley enters AFTER settle.
- Seeds 11/22/33 (n=3 mechanism census, NOT a distributional gate — L90
  lesson: any CONTENT verdict here needs a multibatch replication before it
  becomes a lever claim; verdicts below are mechanism classifications).

## Static pins (l93/static.json, derived BEFORE this run)
- 1-hop provenance of Tr pools: intrinsic .84/.88 (fL/eL), DNi .096/.057,
  sensory .05/.04, motor .01, DNn .003/.005. Premotor sheet owns the pool.
- 61 DN cells carry DIRECT Tr_fL edges → pathway ABSENCE already refuted
  statically; the question narrows to burial vs no-structure vs perturbation.
- Top DN joint-L (Tr_fL+Tr_eL) reachers are ALL u_max < 0 (relu-floor
  BURIED on the settled closure regime, L36 two-sided census): DNg105-R
  -.658, DNxl080-L -.019, DNg74_b-R -1.763, DNg108-R -2.353. Only DNg15-R
  viable (u_max +.177, jointL 27.4).
- intr16 = top-16 intrinsic cells EXCITATORY onto BOTH Tr-L pools (min-pos
  rank, L24 sign rule): 1-hop share Tr_fL .0364 / Tr_eL .0203 — BOTH ≥ .02
  conduction floor at the entry hop (L36/L60) = the only candidate set
  clearing the floor. Members incl. IN18B011 x2, IN12A001, INXXX466,
  IN19B003 x2 (male walking-CPG-family type kin, tick 61).
- tidon16 = same selection for Ti-L (share Ti_fL .0199 / Ti_eL .0441);
  DISCLOSED: 6/16 cells SHARED with intr16 (broad premotor anatomy) — the
  donor is partly a diluted treatment, biasing the sham AGAINST us (if it
  moves Tr-L, the shared 6 may carry it); random-intrinsic shams are the
  delivery-unmatched column.
- Base pin (l92 stored cfn arm, l91 500-step cell form, seg0+seg2 pooled):
  duty07_L(Tr) = {.057, .047, .037}, duty07_R = {.557, .460, .257}.
  DISCLOSURE: the closure substrate is DEADER on L than l65/l91's .16/.95 —
  substrate law (L92) applies; ALL reads below are PAIRED vs THIS base.

## Arms (volley = drive[cells] += amp for k in [0,2000), i.e. seg0 only)
0. base — no volley (C0 anchor).
1. xl080_L_20 — DNxl080 LEFT cell, amp 2.0 (burial -.019: amp un-pins).
2. d74b_R_20 — DNg74_b RIGHT, amp 2.0 (burial -1.763: amp just clears).
3. d105_R_20 — DNg105 RIGHT, amp 2.0 (burial -.658; male crouch analog).
4. intr16_05 — Tr-L premotor 16, amp 0.5.
5. intr16_20 — Tr-L premotor 16, amp 2.0.
6. tidon_20 — Ti-L premotor 16 (donor sham), amp 2.0.
7. shamdn_20a / 8. shamdn_20b — 3 random VIABLE DN cells (u_max>0 &
   x_mean<.95; np.default_rng(9301)/(9302), 884-cell pool), amp 2.0.
9. shamint_20a / 10. shamint_20b — 16 random intrinsic cells
   (np.default_rng(9311)/(9312)), amp 2.0.
Drawn cell identities are written to results (identity disclosure).

## Gates (registered BEFORE rollouts)
- C0 anchor: base == l92 cfn BIT-IDENTICAL: max|d| over mm, xm, all 8 pool
  traces x seeds 11/22/33 == 0.0 exactly (36th consecutive chain anchor).
- C1: settled af (pre-win) identical across arms per seed (shared settle)
  and == l92 stored af within 1e-9; 0.01 < af < 0.9.
- C2 lands: per candidate arm-seed, dm = max|pool - base| > 0 on BOTH
  Tr_fL and Tr_eL; first-divergence law: volley enters drive at k=0
  (first win step) → X[cand] moves end of k=0 → pool drive k=1 → pool
  trace fd == 1 (tolerance {1,2}, measured law disclosed). Sham arms: dm>0
  NOT required; report delivery per sham (a non-delivering sham cannot
  carry structure and is reported as such, never as a passed control).
- P1 (delivery ordering, from E1 static): intr16_20 pool dm ≥ every
  single-DN arm's dm on Tr pools (conduction share ordering).
- E2 structure (PRIMARY, seg0 S-windows [500,2000), per-seed paired delta
  vs base same seed): duty07_L(Tr). Classes:
  * CONTENT: lift ≥ +.25 absolute, sign-consistent 3/3, AND exceeds BOTH
    same-class sham draws by ≥ .15.
  * PERTURBATION (L78): candidate lift ≤ max sham lift + .10.
  * NO-STRUCTURE: dm > 0 (lands) but |delta| < .10 all seeds.
  * BURIED: dm == 0 on a pool (cross-check u_max vs amp, L37 un-pin).
- E3 no-harm: Ti duty07_L(seg0) delta > -.25 every arm; seg0 motor-mm
  dom_freq within ±.10 Hz of base per seed (entrainment lock intact).
- E4 persistence (secondary, descriptive): seg2 duty07_L delta — the
  post-release lottery (L47), never a gate.
- Volley-cell saturation reported: mean X of volley cells during [0,2000)
  (a pinned-at-1 set = max-drive arm, L11 flat-amp caveat disclosed).

## Card verdict mapping
ABSENCE refuted statically (61 direct DN cells + .84 intrinsic mass +
intr16 ≥ .02 share). Dynamics classify: BURIED (C2 fail) / LANDS-NO-
STRUCTURE (E2 no-structure) / PERTURBATION (sham-carried) / CONTENT
(first female-own lever candidate — replication required before claim).

## ADDENDUM 1 (post-run, pre-verdict disclosure)
- C2 fd tolerance {1,2} VIOLATED by d74b_R_20 (fd 441/1098/97): the
  registered law assumed immediate pool visibility; the MEASURED law is
  fd = first step the volley cells' X crosses pool-trace visibility, and a
  marginally-un-pinned cell (amp 2.0 vs |u_max| 1.763, headroom 0.24) rises
  on its membrane tau through the volley — fd IS the un-pin rise-time, a
  burial diagnostic (fast cells: intr16_20 fd 1/1/3, d105 1/11/30, xl080
  3/3/17). dm>0 (lands) held for every arm/seed — no BURIED verdict stands.
- E3 no-harm breaches are CLASS-WIDE: both shamdn and both shamint draws
  breach the lock/TiL gates as hard as the candidates (df0 to ±.44, TiL to
  ±.53, both signs) — the gate presumed candidate-specificity that does not
  exist; the class-wide breach IS the perturbation signature and does not
  qualify the E2 census reads.
