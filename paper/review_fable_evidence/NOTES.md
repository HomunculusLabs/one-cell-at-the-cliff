# Reviewer working notes (scratch; survives context compaction)

DRAFT.md sha256 b32c9781…febe8, 514 lines, 31,814 bytes, mtime 2026-11-19 21:44. Paper dir last touched 23:10 (before my session 23:15).
Verify scripts (re-run 23:55): l143 EXIT=0 ALL GREEN; l149 EXIT=0 ALL GREEN; l158 EXIT=0 ALL GREEN (71 tokens subset of v3.6 allowlist); l159 EXIT=0 PASS (0 sentences >60 words in abstract/§1).
A 5th script l161_verify.py (mtime 23:10) exists in paper/ — NOT in my allowed list, not run.
Figures: lab/paper PNG == published copy byte-identical for all three (cmp). Fig1 2520x1140, Fig2 1260x690, Fig3 2520x1200.
VISION: vision_analyze fails with Anthropic 400 `chat_template_kwargs: Extra inputs are not permitted` (profile auxiliary.vision extra_body meant for LAN JEV-27B-VL endpoint is sent to a provider that rejects it). 1 success early (Fig 3), 6 failures (Fig1 x3 incl. JPEG, Fig2 x2, Fig3 x1). Not image-related. Did not edit config.

## Stats recomputed by me (stats_probe.py -> out_stats.txt)
twin 12/32=.375 [.229,.547] vs cutwA 43/144=.299 [.230,.378]: diff +.076, Fisher p=.41
twin incl B28 21/48=.438 [.307,.577] vs cutwA 12-batch 55/192=.286: p=.056 ; same three batches 21/48 vs 14/48: p=.20
carrier 124/128 vs twin 12/32: p=1.2e-13
eMotTop5 14/32=.438 vs base 43/144: p=.146 ; eMotBot5 8/32=.25 vs base: p=.67
eOutMot(all10) 21/32=.656 [.483,.796] vs top5: p=.131 (NS) ; vs bot5 p=.0023 ; vs base p=.0002 ; vs carrier 124/128 p=3e-6
silW 28/32=.875 [.719,.950] vs cutng25 same batches 32/32: p=.113 ; vs cutwA same batches 10/32: p=8e-6
rank-24 step: cutng23 0/80 vs cutwA 55/192: p=3.6e-10 (kill->partial is ALSO a one-cell step; rank-24 cell = id 585)
intact full 66/176=.375 [.307,.448] vs cutwA 55/192=.286: p=.076 (PARTIAL class ~ intact baseline)
Wilson 5/5 lb .566 ; 4/5 [.376,.964] ; 0/64 ub .057
.0544/.005599 = 9.72x (draft says 12x)
Re-bisected gain relative to cutwA (.143658): FLIP arms cutng25 +1.24%, eOutInt +1.30%, eIn +1.09%, eAll +1.24%, eOutAll +1.24%, eMotIn +1.06% ; NON-FLIP arms cutng25p -0.09%, eMotTop5 -0.03%, eMotBot5 +0.01%, eOutMot -0.57% (intermediate). Others: cutng23 +2.30%, cutng29 +0.42%, cutng19 +4.60%, cut58 +7.32%, cutk5 -2.67%, full +6.59% (g_full=.153125).

## B26 (l135) per-pair table kL/kR of 16 (visible in results_l135.json table)
Ti: b65 16/16 ; full 3/4 ; cutk5 1/0 ; cut19(glut) 15/0 ; cutng19 1/0 ; cutng23 1/0 ; cutwA 1/5 ; cutng25 0/15 ; cutng25p 2/5 ; cutng26 0/16 ; cutng29 0/15 ; cut58 16/0 ; cut(all77) 16/0
Tr: b65 0/16 ; full 0/6 ; rest ~0.  Sr: b65 16/0 ; full 0/4 ; cut58 16/0.  Ta, Pr ~0 everywhere.
=> baseline strongly lateralized; only Ti carries the ladder; cut58 "kill" on R is SUPER on L (16/16).

## Scramble lanes (l125/l127/l128) — NOT reported in DRAFT results
cutscr0 = k19 + ranks 30-39 (max-mass scramble, mass .2490, EXCLUDES carrier 1110): Ti kR 12/16 (B20), 12/16 (B22), 15/16 (B23) pooled 39/48 = .8125 [.681,.898]; classifier: restore/super TRUE; kL also high 12,10,13.
cutscr1 (.2422): 0/16, 0/16 KILL ; cutscr2 (.2409): 6,6 -> 12/32 partial ; cutscr3 (.2388): 6, 11 -> 17/32 ; cutscrL1 10/16 ; cutscrL2 4/16 ; cutcl40 0/16.
l125 verdict text: "COUNT-CARRIED: a scramble SUPER-RAISES — the flip is count/dose, placement story dead; disclosed".
extra_mass_scr: .0544 (scr0), .0476, .0463, .0442.

## My BANC floor probe (banc_floor_ladder.py; membership RE-DERIVED under floor; reproduces paper at floor 3)
floor>=3: dn_new 560, K 77 (ng 58, glut 19), carrier rank 25, twin 26, cells at ranks 24/25/26 = [585, 1110, 319]; right homolog 928 NOT in cohort.
floor>=4: dn_new 688, K 88 (ng 76, glut 12), carrier rank 46, twin 72, ng-set Jaccard vs floor-3 = .354
floor>=5: dn_new 767, K 100 (ng 88), carrier rank 54, twin 76, homolog 928 enters at rank 49, Jaccard .270
Draft §4 says f4: carrier rank 25->21, heavy-cohort Jaccard .9231, twin 26->33 (apparently membership frozen).

## Draft text observations
- Abstract quotes stale pools (k24 20/64, k25 47/48) while §2.2 has 43/144 and 124/128.
- Abstract: "removing it converts kill→super" but k=24 base is PARTIAL.
- "−.088, inside the .075 sham spread": |−.088| > .075.
- §2.2 rank 25 vs §2.3 "mid-pack removal-mass rank (34/58)".
- "all 10 SUPER" (abstract) vs "half-step→SUPER; significantly between" (body).
- In-text cites missing from reference list: Sapkal bioRxiv 2026.04.29.721658; DUCKOPHILA; DNp01 wet-lab (no cite). Listed but uncited in body: Shiu(2), Pugliese(4), Schlegel(11), Dallmann(13).
- Abstract promises release of prereg+anchor protocol; §5 says release TBD/private.
- Fig 3 referenced only once, inside Limitations; no captions for any figure.
- My rewritten abstract fits arXiv: 1572 chars / 235 words (arXiv limit 1920 chars).

## Ledger facts (numbers.json, 660 leaf keys)
pooled.full 66/176 .375 [.3069,.4485]; pooled.cutwA 20/64 (Fig1 data; l150 has 43/144); pooled.cutng25 47/48 (l150: 124/128); pooled.cutng23 0/64; twin 12/32.
xor: m25 .006436, m26 .006045, delta 3.9e-4; steps 24->25 +.371, 24->25p +.016, 25p->26 +.444.
"+.256" in abstract: NOT in ledger under a relevant key (only l133/results_l133.json line 820 mean_paired_dR); "+.317" = dose_l135.legs.25.mean_paired_dR. Abstract cites no key for the pair.
l137.g1 sil1110 meanR .376 kR 2 paired_dR -.088 "in_full_band": true ; g3 silrand_meanR [.429,.502,.504] spread .075 ; sil24 meanR .432 kR 5 kL 0 meanL .119 dR -.032 (comparator cutwA from B26: kR 5 meanR .383).
l146.f4: K=73, n_ng 55, n_glut 18, carrier_rank 21, twin_rank 33, jaccard_heavy .9231, out80_f4 69, carrier_eq3 11, edges 647,953 -> 472,095.
l138: BANC dn33 cells: 928 right, 1110 left; window shares r1_19 .1946, r20_29 .0642, r30_58 .1333 ; male: dn_new 28, ng 9, glut 0, heavy_K 9.
jitter_note: "1% iid multiplicative on base edge table, default_rng(2001..2005), post-log1p signed vals"; g_full across sets [.1531 base, .1750, .1487, .1491, .1614, .1617] = -2.9%..+14.3% vs base.
l134 ng58_profile for 1110: rank_out_n 39, rank_out_mass 34 (= draft's "34/58"), rank_intr 20, rank_pool 27, rank_motor 9; heavy_rank 31 of 77; NT acetylcholine predicted (verified: null); manc match 12064.
No scramble (scr) keys in numbers.json at all.

## l139 jitter classes per set 1..5 (prior)
cutwA (PARTIAL): NEUTRAL-INT, OTHER, OTHER, KILL, SUPER -> 0/5
twin cutng25p (NEUTRAL-INT): OTHER, PARTIAL, PARTIAL, KILL, SUPER -> 0/5
carrier cutng25: SUPER x5 ; cutng29: SUPER,SUPER,SUPER,NEUTRAL-INT,SUPER ; cutng23: KILL x4, OTHER
per-seed flips vs base (of 16): cutwA 9,3,4,4,12 ; carrier 2,2,5,4,5 ; twin 8,8,7,9,6 ; ng29 1,3,1,7,3 ; ng23 1,0,1,0,0
batch_note: "single batch B28 per set; sustain over SETS not seeds"

## Intact-base clamp arms, Ti (kL, kR, meanL, meanR) of 16
B27 l137: full (3,6,.362,.464) ; sil1110 (8,2,.484,.376) ; sil319 (2,6,.314,.424) ; silrand (6,5,.429,.429) (3,8,.391,.502) (5,8,.413,.504) ; vol1110 (3,7,.354,.486) ; volrand (3,9,.32,.541) ; sil24 (0,5,.119,.432)
B30 l144: full (3,6,.382,.428) ; cutwA (1,5,.231,.433) ; cutng25 (0,16,.103,.714) ; sil1110 (4,3,.446,.392) ; sil1110_wA (1,14,.306,.622)
B33 l150: full (5,8,.409,.494) ; cutwA (0,5,.217,.379) ; cutng25 (0,16,.145,.817) ; silW (0,14,.283,.659) ; eMotTop5 (1,8,.231,.46) ; eMotBot5 (0,2,.204,.35)
=> sil1110 on intact: R down both batches (6->2, 6->3), L up (3->8, 3->4); below all 3 shams on R.
silW gain: GAIN["sil1110_wA"] = G_CUTWA_STORED (no re-bisect) -> the ONLY flip arm at unchanged gain.

## Slow line = stimulus chop envelope (envelope_probe.py)
drive(sin*chop) spectrum: 0.7 Hz 1.0 ; 0.1 Hz 0.933 ; chop envelope alone peaks at 0.1 Hz.
l154 B34 arm b65 (drive on, n=18): median frac power @0.1 Hz .196 ; median corr(motor-mass, chop envelope) +.552 (min +.513, max +.618) ; sensory mean corr +.621 ; peak bin 0.1 Hz in 17/18.
l154 arm off (mech drive off): frac power @0.1 Hz .022 ; corr -.025 ; peak bins scattered.

## Census pseudo-replication (census_probe.py on l156/static.json)
b65: 518 traces = 449 unique seeds (seed 801 in 28 files, 901 in 27 files, 1401-1416 x2). All 27 non-0.1 (.0167-bin) traces are seed 901. unique: 449/449 lb .9915.
full: 500 traces = 433 unique seeds; unique-seed sub-band 348/433 = .804 [.764,.838] vs reported 361/500 = .722 (lb .681).

## MaleCNS floor probe (male_floor_probe.py, venv python) — validated: reproduces paper's dn_new 28 / heavy K 9 at floor>=1
Male weights file has NO floor: min weight 1; 10,295,463 pairs at w=1, 4,760,434 at w=2 (of 25,568,639). BANC release floor = 3.
floor>=1: DN into 1277 of 1314, dn_new 28, K 9 (paper's numbers)
floor>=2: dn_new 199, K 46 ; floor>=3 (BANC-matched): DN into 963, dn_new 342, heavy K 52 ; floor>=4: 458, K 59 ; floor>=5: 541, K 70
Male DNp33 at floor>=3: R has 6 cord in-edges, L has 2 -> both still in base (not in cohort); at >=5 R becomes pure-projection.
=> "28 vs 560 / no ladder to walk" is a threshold mismatch (>=1 vs >=3). Transfer is UNTESTED, not negative.

## BANC floor probe v2 (banc_floor_ladder2.py) — validated: reproduces paper f4 exactly under FROZEN membership
floor 3: DN-into 728, dn_new 560, K 77 (58 ng/19 glut), closure edges 647,953, carrier 25, twin 26
floor 4 FROZEN: K 73 (55/18), edges 472,095, carrier 21, twin 33, heavy Jaccard .9231  (== paper l146.f4)
floor 4 RE-DERIVED: DN-into 588, dn_new 688, K 88 (76/12), carrier 46, twin 72, heavy Jaccard .3525, ng Jaccard .3535, 35 of ng58 remain, first-24 overlap 9/24
floor 5 FROZEN: K 70, carrier 16, twin 25, Jaccard .909 ; RE-DERIVED: dn_new 767, K 100 (88/12), carrier 54, twin 76, Jaccard .273, first-24 overlap 5/24
l146 PREREG: "STATIC, zero rollouts"; "No dynamic arms either way".

## Model + readout (from l135_run.py / l135_verdict.py) — NOT in draft Methods
TAU .05, DT .01, RMAX 1.0, BG .02, NOISE .01 (added after ReLU, before upper clamp), SETTLE 400, WIN 6000 (60 s), D=0.2 tonic input into DNg100 cells, ENT_AMP .1 raised sinusoid into mechanosensory cells at .7/1.4/.7 Hz in 2000-step segments.
x <- x + (DT/TAU)*( clamp(relu(g*W x + I + sin[mech] + BG) + noise, max=RMAX) - x )
Chop: AMPA on 500 of every 900 steps in the two 0.7-Hz segments; middle 1.4-Hz segment fully on (lines 551-557).
AF = mean(x > 0.05) after 400-step settle, mean of 3 anchor seeds (11,22,33); AF_T = .109056; bisect g in [.12,.18]. G_NEW .153125 (full), G65 .14 (b65).
Readout: S = -Pearson r between the two antagonist pool traces in sliding 500-step (5 s) windows every 10 steps; duty = fraction of windows in the 0.7-Hz (chopped) segments (excluding first 500 steps of each) with S >= .25; seed counts toward k if duty >= .5; meanR = mean duty. Pools: Ti/Tr (f,e), Ta/Sr/Pr (a,b).
=> readout window (5 s) == chop on-block (5 s); readout only in chopped segments.

## l139 per-set Ti kR/16 (set 0 = unjittered B28)
set0: full 8 | ng23 0 | wA 3 | ng25 14 | 25p 9 | ng29 16
set1: 7 | 1 | 10 | 16 | 13 | 15 ; set2: 6 | 0 | 0 | 16 | 5 | 13 ; set3: 4 | 1 | 3 | 13 | 6 | 15 ; set4: 9 | 0 | 1 | 14 | 0 | 9 ; set5: 4 | 0 | 15 | 13 | 13 | 13
carrier-vs-twin contrast clear in sets 2,3,4 (16v5, 13v6, 14v0); absent in set 5 (13v13), weak in set 1 (16v13).
gains per set: full .1531,.1750,.1487,.1491,.1614,.1617 ; cutwA .1437,.1431,.1442,.1435,.1437,.1427 (range ~1%) ; cutng25 .1454,.1440,.1453,.1441,.1451,.1438 ; => "±8%" applies only to the untreated arm.

## Citation audit
Body has 0 numeric cite markers. Never named in body: Shiu(2), Pugliese(4), Schlegel(11), Dallmann(13). In body but not in References/bib: Sapkal bioRxiv 2026.04.29.721658, DUCKOPHILA; "DNp01 jump etc." uncited. DNg100 never mentioned in the draft though the model drives it tonically (D=0.2).
Abstract: 3,962 chars/568 words with keys; 3,521 chars/537 words without keys (arXiv limit 1,920). 14 all-caps emphasis words in abstract; 119 all-caps tokens (>=4 letters) in body; 35 bullet lines; body 3,136 words.

## Readout probe on stored B26 traces (readout_probe.py; validation row reproduces results_l135 exactly)
Scoring windows in 0.7-Hz segments: 300; fully drive-ON: 2; straddling an on/off edge: 298.
arm: orig kR(mean) | high-pass 0.3 Hz | 1.4-Hz unchopped segment
full 4/16 (.44) | 1/16 (.25) | 0/16 (.03) ; cutng19 0 (.20) | 0 (.05) | 0 (.03) ; cutng23 0 (.09) | 0 (.09) | 0 (.00)
cutwA 5/16 (.38) | 5/16 (.35) | 0/16 (.02) ; cutng25 15/16 (.75) | 15/16 (.68) | 12/16 (.63) ; twin 5/16 (.40) | 1/16 (.37) | 0/16 (.00)
cutng26 16 (.84) | 16 (.78) | 7/16 (.51) ; cutng29 15 (.80) | 15 (.75) | 12/16 (.57) ; cut58 0/16 (.28) | 0/16 (.06) | 13/16 (.70)
per-seed R duty sorted: full .21 .31 .32 .33 .37 .38 .40 .43 .46 .47 .47 .49 .51 .52 .58 .73 (unimodal around the .5 cut)
cutwA .07 .09 .11 .14 .18 .24 .38 .41 .44 .48 .49 .53 .56 .63 .64 .72 ; cutng25 .48 .62 .64 .67 .70 .75 .76 .76 .79 .81 .82 .82 .83 .83 .87 .92 ; twin .14 .20 .21 .24 .30 .39 .43 .44 .44 .47 .48 .50 .51 .52 .55 .56
Ti_R pool power <0.3 Hz: full .32, cutwA .13, cutng25 .38 ; at 0.1-Hz bin .044, .011, .118.

## Misc verified
cutk5 = 5 heaviest GLUTAMATERGIC cells (l117 PREREG: "mass_removed .0425 (38.5% of glut-19 mass)") -> not a point on the ng ladder; Fig 1 prints removed mass 0.000 under it.
xm = X[mech].mean() (mechanosensory driven population), mm = X[motor].mean(). Draft calls xm "X-motor"; Fig 3 groups mm/xm as "motor-mass aggregates".
l157 pooled n=36 = l150 b65 (18) + l154 b65 (18); anchors 801/901 in both -> 34 unique seeds. Fig 3 footer says "3 file-arm combos x n=12".
Fig 2 whisker = line from meanR dot to Wilson lb of pooled k/n (l152_fig2.py 117-118): two statistics on one axis; dot meanR single-batch, k/n pooled.
Fig 1: panel A title says "monotone in cells removed"; footer "11 seed batches B17-B26" (should be B16-B26); annotation +.334 (L126) vs text +.371; pools stale (20/64, 47/48).
Fisher: sil1110 intact R 5/32 vs matched full 12/32 p=.088 (L 12/32 vs 6/32 p=.16); left death 0/48 vs 5/64 p=.07; left baseline 47/176 vs cutwA 5/64 p=.0013; twin B28 9/16 vs base 3/16 p=.066;
jitter carrier vs twin: set1 16v13 p=.23; set2 16v5 p=7e-5; set3 13v6 p=.029; set4 14v0 p=5e-7; set5 13v13 p=1. scr0 39/48 [.681,.898] vs carrier arm p=.0013.
Refs verified online 2026-11-19: all 13 exist. Sapkal = "Central versus peripheral neural control of a coordinated walking pattern in Drosophila" bioRxiv 10.64898/2026.04.29.721658. DUCKOPHILA = GitHub repo first-it-consulting/duckophila + FlyWire forum post (not a paper).
Kopel abstract: 2 of 5 registered criteria fail "when connections of one or two synapses are removed" (not a critique paper). FlyHack: conclusions depend on comparison model, intervention, circuit representation, trained solution (50-model flyvis ensemble). ApproxBrain: 148-neuron circuit; removing any one of its 3 interneurons destroys adequacy; certified on 32 held-out parameter draws; sufficiency set-valued. Minnick: 172,433-neuron spiking BANC model with degree/sign-preserving rewiring null (95% -> 18%).
