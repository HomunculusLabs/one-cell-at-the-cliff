# L135 PREREG — cutng25p batch rebase (ideas 70, tick 157)

Card: the W3 band-edge read (.508, kR-leg-in at 7/16, meanR-leg-out by
.008) and the 319-neutral decomposition are SINGLE-BATCH B25 n=16: re-roll
cutng25p on fresh B26 and pool 25p B25+B26 n=32 full-precision Wilson
(L90 form) so "319-alone is an intermediate, not a partial" is citable
robust — or dissolves into batch swing (L88/L90/L124 discipline; the
base full arm is noisy 2-10/16, never cite it as a point).

UNIFORM-ARM-SET INTERPRETATION (registered, L128 precedent): the card
names cutng25p + {full, cutwA, cutng25, cutng26} as PRIMARY, but the run
keeps l133's full 13-arm set VERBATIM — the anchor chains (C0A/C0A-12x
read stored arms at 801/901) and the banked secondaries (S1 cutk5, S3
wA, S4 ng25, endpoints) require exactly those arms; a trimmed set would
break the C0A conjunction for zero savings (rollouts are seed-major).

Pre-run verification DONE (l135/l135_precheck.py, zero rollouts):
- B26 = 3001-3016 ABSENT from all 16 stored npzs (raw_l113 + l115 +
  l117 + l118 + l119 + l120 + l121 + l122 + l123 + l124 + l125 + l126 +
  l127 + l128 + l131 + l133). The run re-asserts before any rollout.
- raw_l133.npz carries ALL 13 arms x {mm,xm,af}+pool keys at 801/901
  (probe 13/13) — C0A-133 chain is free (L120 forward-chain law).
- 25p gain stored-form confirmed from raw_l133.npz: g_cutng25p =
  0.1435265743732452 (== card).

## Run design (l133 machinery VERBATIM: arms, pools, graphs, draw order)

- ARMS (13, unchanged): full, b65, cut, cut19, cut58, cutng19, cutng23,
  cutwA, cutng25, cutng25p, cutng26, cutng29, cutk5.
- FRESH B26 = 3001-3016; ANCH = [801, 901] first; raw checkpoint to
  l135/raw_l135.npz BEFORE analysis; resume via l135/raw_partial.npz
  (own dir, direction-checked).
- Gains: ELEVEN STORED-FORM, ZERO fresh bisects (first all-stored run
  in the lineage — every deterministic re-bisect must land EXACT and is
  asserted): cut (l107), cut19 (l111), cut58 (l113), cutk5 (l117),
  cutng19/cutng29 (l121), cutwA (l123), cutng23/cutng26 (l126), cutng25
  (l131), **cutng25p NEW stored-form (l133 fresh gain 0.1435265743732452)**.
  G_NEW (full) re-bisects as always and is asserted EXACT vs the
  deterministic ladder.

## Anchors (all must PASS before any B26 number is pinned)

- C0A 61st consecutive: 5 stored arms (full, b65, cut, cut19, cut58),
  10 old keys, vs raw_l113 at 801/901 — max must be 0.0.
- C0A-120..C0A-128 retained (22 keys x arms x 2 seeds, max 0.0);
  C0A-131 retained (10 arms vs raw_l131; 25p has no l131 counterpart).
- NEW C0A-133: ALL 13 arms vs raw_l133 (l133 ran every arm at both
  anchor seeds) — the chain extends 9 runs forward.
- B-CERT (C0B line): before ANY B26 read, verdict machinery recomputed
  on raw_l133 B25 must reproduce results_l133.json's Ti table on ALL 13
  arms, exact (rounding-path identical, l109/l111 atom).
- P4 health: af in (0.01, 0.9) all arms/seeds; b65 af-mean band
  [0.105056, 0.113056].

## PRIMARY registered reads (B26; per-batch criteria VERBATIM L118-L133)

Arm KILLs iff meanR <= m0 - .10 AND kR <= 4 AND mean paired dR <= -.20
(m0 = full-arm Ti meanR on B26). RESTORE: meanR >= .45 AND kR >= 12.
SUPER-RAISE: meanR >= .60 AND kR >= 12. PARTIAL band: meanR in [.35,.50]
AND kR in 3..8.

- R1 (INTERMEDIATE-STABLE, the card's claim): B26 25p lands in the
  W3 window (meanR in (.45,.60) AND kR in 4..10 — neither the partial
  band's kR leg nor any super/kill criterion) AND pooled 25p n=32
  Wilson CONTAINS .5 (lb < .5 < ub) -> "319-alone is a batch-stable
  INTERMEDIATE at mass-match; 1110 carries the flip (paired dR +.256),
  319 ~neutral (-.017)" is citable pooled. Decomposition legs carried
  verbatim: paired dR vs full on B26; Ti_L (ng25 L-death vs 25p ~ wA).
- R2 (KILL-DRAW): B26 25p KILLs by the verbatim criterion -> the B25
  .508 read was a draw; the intermediate reading downgrades to
  single-batch, disclosed; report which leg moved.
- R3 (RAISE-DRAW): B26 25p SUPERs or RESTOREs -> W2 (position-thin)
  revives one batch late; report honestly.
- P2 (context legs, same batch): cutng25 SUPER 3rd batch (S4 pooled
  B24+B25+B26 n=48) and cutng26 SUPER — the X1 frame the 25p arm lives
  inside. If either misses on B26, disclose (would weaken the
  decomposition context, not R1 itself).

## Secondaries (disclose, never abort)

- S1: cutk5 KILL 14th consecutive batch (B12..B26); pooled R4 union
  B16..B26 n=176 full-precision Wilson.
- S2: endpoints cutng19/cutng29 11th batch (dR-leg note retained: the
  ng19 dR leg is informational, kR+meanR legs carry the label).
- S3: cutwA PARTIAL band 6th batch (B18 .413/5, B19 .376/4, B21 .365/3,
  B24 .436/6, B25 from stored results, B26).
- P3: transition arms {cutng23, cutwA, cutng26, cutng29} pooled
  B21+B24+B25+B26 n=64; cutng25 pooled B24+B25+B26 n=48; cutng25p
  pooled B25+B26 n=32 (the card read).
- Watch (no gate): Ti_L through the same steps, Sr_R (killed by every
  ng dose, 7+ batches), Tr_R.
- Sanity: cut Ti kL >= 14; b65 kL = kR = 16; cut19 kL >= 12; Sr b65
  cells.
- full-arm B26 band disclosure (never abort): Ti L (.25,.48), R
  (.35,.58); Sr L (.08,.25), R (.30,.50) — l133's windows carried
  forward; a miss is disclosed, not an abort.

## Disclosure list

ZERO fresh bisects (all-stored run; every gain must re-land EXACT);
cutng21/cutng28 not re-run (l126 single-batch points stand); scr/cl
arms not run (l127/l128 stand); the pooled-key namespace extends
(k160->k176, k48->k64, k32->k48 for ng25; 25p k16->k32 with
single_batch retired on success); P4/band cells secondary; the
uniform-arm-set interpretation above.
