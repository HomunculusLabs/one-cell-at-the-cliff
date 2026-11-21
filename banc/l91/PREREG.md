# L91 PREREG — banc-endgame-rebase (female BANC cord, L90 multibatch protocol port)

Register BEFORE rollouts. All expected values derived from STORED artifacts
(results_l68.json, raw_l68.npz, raw_l78.npz, scan_l78.json — L44 rule; no log
sentences trusted where stored values exist).

## Substrate (l78_run.py verbatim, no edits)

BANC female v626 subnet 21,249 nodes / 627,051 edges, glut-INH sign arm
(gsign_b), G=.14 BETA=2.0 D=.2 (L65 arm-B frozen), ENT_AMP=.1, settle 400,
WIN 6000, SEGB 0.7/1.4/0.7, chop 500-on/400-off + continuous seg1 (l68 hyb01
table; drive-on 4800 incl settle). Pools Ti [50,51,6,6], Tr [31,31,24,24],
mech 4848, DNg100 2. Echo cell = male literal (gfb .1, sign −1, delay 5),
source ANTAG = Tr 4-pool mean (l78 fbn_g01 verbatim).

## Arms (5, one shared-noise group per seed; male L90 trunk vocabulary)

- fn      = hyb01 schedule alone (male "nohop" analog)
- fn_fb   = fn + literal echo cell throughout (male hynohop_fb analog)
- fh      = fn + HOP volleys: HOP_AMP .5, 40 steps at k∈[2000,2040)∪[4000,4040)
            on the DNge046 cells IN-SUBNET (male hybrid analog)
- fh_fb   = fh + echo cell
- fsham   = fn + donor sham (g .1, −, delay 5), donor = l68 stored hyb01
            ANTAG-mean trace, cyclic {11,22,33} by seed index mod 3
            (l78 next-seed-cyclic for seeds 11/22/33)

## Seeds

ANCHOR = [11,22,33] (bit-identity + certification ONLY, excluded from table).
B1=501-516, B2=601-616, B3=701-716 → pooled n=48.

## DISCLOSED deviations from the male L90 protocol (substrate-forced)

1. HOP TARGET: male = DNge046 somaSide L ×2. Female subnet has exactly ONE
   DNge046 cell, side RIGHT (probe run pre-PREREG from annotations+conn).
   Hop mass halved vs male. C2 dm probe must confirm it lands.
2. PRIMARY PAIR = Ti (male table reads Tr). Derived from stored l68: female
   Ti carries the antiphase (S_Ti .64-.74 open arm; hyb01 seg0/2 duty
   .90-1.0), Tr is the side-split pair (SL −.18..−.41 / SR .53-.75). Tr read
   retained as secondary.
3. LOCK: female never passed a male-form block-err gate (l68 G1_entrains
   FALSE, seg1 err .79-.94 on hyb01); l68's spectral-ratio proxy passed
   (43.7/59.1/37.6 @0.7, 29.5/235.1/54.2 @1.4). We REPORT male-form err as
   diagnostic and register G1p = per-seg dom-ratio >= 10 on mm (rhythm
   present), no frequency-target gate.
4. Op point differs (G .14 vs male .01; D .2 vs .05) — L65 frozen, not tuned
   to male numbers.

## Anchors (all must pass before any verdict read)

- C0A: fn on 11/22/33 == l68 stored hyb01 BIT-IDENTICAL (mm + Ti/Tr × 4
  sigs × 3 seeds). C0A2: fn_fb == l78 stored fbn_g01 BIT-IDENTICAL (same
  seeds, mm + 8 sigs) — same generator, same draw order (X0 once, then one
  shared nz per step; stream is arm-count invariant).
- C0P: fd(fn_fb vs fn): xm == 5, mm == 6 (l78 stored law). fd(fsham vs fn):
  mm == 6. fd(fh vs fn): mm > 2000 (exact set reported; one-or-two W-hops
  from a DN entry is wiring-dependent, disclosed). fd(fsham xm) reported.
- C2: dm > 0 for every treatment arm × seed (hop + echo + sham all land).
- C1: settled af ∈ (0.01, 0.9) every arm × seed.
- C0B certification (L85 rule): verdict machinery re-derives l78's STORED
  duty reads on the shared arms (open, fbn_g01) with l78's own 300-step
  form — duty_slow/duty_off/duty_fast/Ti_duty07 must equal results_l78.json
  EXACTLY on all 3 seeds.

## Registered reads (male L90 machinery verbatim where stated)

- Table cell = duty_07: 500-sample rolling S windows (TS=499..WIN step 10),
  per-side S = −corr(flex,ext) same side, duty = mean over 0.7-seg meas
  windows (MEAS0=500) of (SL>=.25 & SR>=.25). PRIMARY on Ti, secondary on Tr.
- Per-seed seg rows (duty, SL, SR medians, f_seg, male err diagnostic),
  duty_all, per-side duty07_L / duty07_R (side-split question, descriptive).
- G2a-multi (PRIMARY, fn trunk): pooled full-precision Wilson lb over n=48,
  k = #seeds duty_07(Ti) >= .5; gate lb >= .717 ⇔ k >= 41/48 (pin:
  wilson_lb_full(41,48) >= .717 > wilson_lb_full(40,48)). Same for all arms.
- C4b-analog: fn_fb vs fn on Ti (stored-derived EXPECTATION: flat-to-TAX —
  l78 taxed the healthy pair, worst −.29) and on Tr (EXPECTATION: lift,
  sham-carried ~96% per l78). Outcome classes male L90 form, adapted:
  base-clears ⇒ lever moot; else fb-lb>=.717 & pos batches>=2/3 ⇒
  lever-real (then sham share MUST be reported next to it).
- G1p lock (ratio>=10 per seg per seed, fn trunk expectation 3/3 from
  stored l68 spectral), budget (echo ratio vs entrain mass; female literal
  cell EXPECTED ~.25 = 2× male .127, from l78).

## Registered expectations (from stored artifacts, falsifiable)

- E1: fn duty_07(Ti) anchor seeds ≈ .94-1.0 (derived seg0/seg2 duties
  .901-1.0). E1b: fn duty_07(Tr) anchor ≈ .04-.20.
- E2: fn_fb Tr duty_07 > fn (lift), fn_fb Ti duty_07 <= fn (ceiling tax).
- E3: fsham carries >= 50% of fn_fb's Tr duty_07 lift (l78: 96%).
- E4: hop arm (fh) = EXPLORATORY, no directional gate registered; C2 dm and
  fd window are its only gates. Descriptive: first look at a DN volley
  inside the female endgame schedule.
- E5 (the card's question): if fn clears G2a-multi ⇒ female base structure
  is batch-robust (male collapsed to p̂ .61); if fn fails ⇒ female
  duty_07(Ti) batch-collapses like male. Per-side duty read adjudicates
  whether collapse is a both-sides loss or a side-split (SL dies, SR holds).

## Out of scope / honesty

No live changes; sessions/ untouched; results only + LAB-INTENT + digest.
Male G4 budget cap (.127) does NOT transfer (op point differs) — budget is
reported, not gated. If runtime exceeds tick budget: B3 may be dropped to a
disclosed n=32 table (k>=27/32 pin holds by the l90 assert) — amendment
BEFORE unblinding, never after.
