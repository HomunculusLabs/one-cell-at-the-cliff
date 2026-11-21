# L87 PREREG — mid-seg-branch-library (ideas 43, GO condition from L85)

Question: can MID-SEG1 echo toggles (decision points k in {2500,3000,3500}) give a
chooser policy realizable online branches that clear GATE-L85 jointly (G2a k>=15
duty_07 Wilson lb>=.717 AND G3 seg1 mean >= .358, G1 lock 16/16, G4 budget caps)?
L86 closed seg0-entry combos (E2 tax law); the only untested entry class is MID-seg
(L84 causal dissociation left the draw mostly seed-attractor identity).

## Stored derivations (l85/mass_table.json + l86/results_l86.json, L44 rule)
- Trunk cells (census 16, re-certified in-run below):
  hynohop     segs .605/.375/.488 k07 11  d07m .547
  hynohop_fb  segs .739/.292/.608 k07 15  d07m .673  (the k15 ceiling arm, ratio .127)
  hybrid      segs .605/.402/.533 k07 13  d07m .569  (the G3-passing arm, .402>=.358)
  hybrid_fb   segs .739/.298/.560 k07 13  d07m .649
  echo(l84, nohop+seg0-only) segs .739/.216/.466 k07 15 ratio .0431 (G2b tier arm)
- Union(hybrid, hybrid_fb) per-seed max d07: k = 16/16; seg1 of pick-by-d07 = .359
  (knife-edge over G3 .358) => the ORACLE already clears with seed knowledge over
  two stored arms; GO therefore rides on REALIZABILITY, not existence.

## Arms (12, one shared-noise rollout per seed; census seeds 11,22,33,101..113)
Trunks (re-rolled as fork bases, double as chain anchors):
  hynohop, hynohop_fb, hybrid, hybrid_fb  (HOPA on the hybrid family only)
New latch arms (EON flip at k; latch persists to 6000):
  nh_on2500 / nh_on3000 / nh_on3500   (EON[k]=k>=K, from bare hynohop)
  nh_off2500 / nh_off3000 / nh_off3500 (EON[k]=k<K, from hynohop_fb)
  hy_on2500  (EON[k]=k>=2500, from bare hybrid)
  hy_off2500 (EON[k]=k<2500, from hybrid_fb)
AMPA identical everywhere (drive-on 4800 asserted); echo cell verbatim l66
(gfb .1, delay 5, sign -1). No glide start-time variant: DISCLOSED scope cut
(glide realizability measured ANTI in L85 derived.json; stored glide arms still
enter the oracle via mass_table per_seed lists — zero extra rollouts).

## Anchors (all must pass before any read; addendum if not)
- A1 hynohop == l59/raw_l59.npz (mm+fL/fR/eL/eR, [:6000], 16 seeds) bit-identical
- A2 hybrid  == l59 raw bit-identical
- A3 hynohop_fb == l77/raw_l77.npz bit-identical
- A4 hybrid_fb  == l77 raw bit-identical                    (32nd chain anchor)
- A5 latch wiring: for every latch arm vs its trunk: prefix max over [0,K]
  INCLUSIVE == 0.0 AND motor first-divergence == K+1 EXACT (l86 A3 law: gate
  flip at K enters mech drive at K, motor traces see it at K+1)
- A6 certification vs l85/mass_table.json on all 4 trunk arms: seg means, seg k,
  seg wilson, seg err_le01, duty07 mean/k/wilson, per_seed seg1 + d07 — every
  pinned value equal (wilson compared as LIST, l86 instrument fix)
- A7 budget: hynohop_fb + hybrid_fb echo_mass_mean/ratio equal to mass_table
  budget.echo pinned values (tol .1 mass / .001 ratio)
- C1 settled af in (0.01, 0.9) every arm/seed
- Degenerate branch: any latch arm bit-identical to its trunk (dm==0) = EON never
  applied -> arm excluded, disclosed, NO verdict from it (L55 rule).

## Registered reads (before rollouts)
- R1 single-arm gates: every arm's G1 (seg1 err_le01==16), G2a, G3, G4
  (ratio<=.127; on-latch arms have strictly less echo). E1 PARETO MOVER if any
  NEW arm alone clears G2a AND G3 (no chooser needed -> schedule candidate).
- R2 oracle (existence, diagnostic per L85 demotion): O-MIDSEG = the 12 in-run
  arms; O-LIB-ALL = O-MIDSEG + 8 stored mass_table arms. Pick rules:
  P1 lexicographic (max d07, tie seg1) -> k, wilson, seg1 mean;
  P2 max seg1 subject to d07>=.5 -> k, seg1 mean. GO1 = P1 or P2 clears
  k>=15 AND seg1>=.358 on O-MIDSEG. [Stored hint: 2-arm subset already k16/.359
  => GO1 expected PASS.]
- R3 realizability (LOAD-BEARING): 4 forks at K=2500 (nh base: hynohop;
  nh-fb base: hynohop_fb; hy base: hybrid; hy-fb base: hybrid_fb). Fork-time
  features from the BASE trunk trace: SL_med[2300,2500), SR_med[2300,2500),
  mm_med[2400,2500). Targets: d_seg1 = latch−trunk seg1 duty, d_d07. Spearman
  both directions per feature (L84 rule). Induced rule family: latch iff
  feature >= median (and <= median), per fork x feature x direction — a rule's
  per-seed picks scored on k + seg1 mean. GO2 = ANY single rule clears
  k>=15 AND seg1>=.358. Expected FAIL (L84 seed-identity law); register that.
- GO for a future training tick = GO1 AND GO2. NO-GO outcome if GO1-only:
  oracle mass not realizable at the registered rule class — C4b echo lever
  stands as the only structure row lever, C4c stays diagnostic.
