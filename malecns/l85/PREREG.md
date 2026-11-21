# L85 PREREG — gait-reachable-mass (written after a read-only derive pass, before the verdict)

Card: LANE.md ideas-42 L85. Deliverable: fixed-family TRIPLE mass table +
fork-oracle closed-loop mass + the REGISTERED NUMERIC distributional gate a
learned gait policy must clear BEFORE any training tick (L6e/L6f protocol,
L80 C4a/C4b window-scoped form).

DISCLOSURE (L80 precedent): derive.py ran FIRST (read-only, ZERO new
rollouts — every number re-derived from stored npz l59/l77/l82/l83/l84 on
the shared 16-seed census grid). Its outputs are pasted below; verdict
(mass_table.py) re-derives independently and asserts equality to every
pasted value. One instrument bug was caught and fixed DURING derive
(dom_freq parabola tuple transcribed permuted — the L35 swapped-unpack
class; symptom: seg1 err_le01 read 0 vs l82's stored 16). Zero rollouts
were ever at risk.

## Family (all noise-shared, census SEEDS = [11,22,33]+101..113, l82 machinery)

nohop trunk: hynohop, hynohop_fb, hynohop_fb07, glide200/300/400, cont, nod,
echo(l84, seg0-only). hybrid trunk: hybrid, hybrid_fb, hyglide300.
`base`(l84) is an alias of hynohop (A3 bit-identity) and is deduped.

## Anchors (all must re-assert in verdict)

- A1 hynohop bit-identical across l59/l77/l82/l83 (mm+fL/fR/eL/eR, 16 seeds) = True
- A2 hybrid bit-identical across l59/l77/l83 = True
- A3 base(l84) == hynohop = True
- A4 echo(l84) vs hynohop_fb07: prefix [0,4000) max|d| = 0.0, first_div set = {4001}
  (predicted: same echo'd seg0 + same echo-off step seg1; they diverge only in
  seg2 where fb07 keeps echo on. Whole-run max|d| 0.507178 is EXPECTED.)
- A5 glide{200,300,400} prefix [0,2000) == hynohop; A5h hyglide300 == hybrid = True
- A6 fb07 vs fb prefix [0,2001] = 0.0 = True
- ACROSS-RUN CERTIFICATION: my re-derived distributions for the 3 l82 arms
  (hynohop, hynohop_fb, hynohop_fb07) must equal results_l82.json EXACTLY
  (seg means/k/wilson/err_le01, duty07 k/mean/wilson/per-seed) — this is the
  instrument check that would have caught the dom_freq bug.

## Pinned family table (TRIPLE — never summed; segs = [seg0, seg1, seg2] duty means)

| arm | segs | seg1 err<=.01 | d07 k | d07 mean | d07 Wilson | on-steps | mass | echo ratio |
|-----|------|----|----|------|--------|----|------|-----|
| hynohop | .605/.375/.488 | 16 | 11 | .547 | (.444,.858) | 4800 | 667.5 | — |
| hynohop_fb | .739/.292/.608 | 16 | 15 | .673 | (.717,.989) | 4800 | 667.5 | .127 |
| hynohop_fb07 | .739/.216/.556 | 16 | 12 | .647 | (.505,.898) | 4800 | 667.5 | .0862 |
| glide200 | .605/.202/.580 | 15 | 11 | .593 | (.444,.858) | 4800 | 667.5 | — |
| glide300 | .605/.366/.517 | 16 | 10 | .561 | (.386,.815) | 4800 | 667.5 | — |
| glide400 | .605/.368/.649 | 16 | 13 | .627 | (.570,.934) | 4800 | 667.5 | — |
| cont | .377/.107/.548 | 12 | 6 | .462 | (.185,.614) | 5600 | 783.8 | — |
| nod | .116/.168/.455 | 16 | 2 | .285 | (.035,.360) | 3600 | 483.8 | — |
| echo(l84) | .739/.216/.466 | 16 | 15 | .603 | (.717,.989) | 4800 | 667.5 | .0431 |
| hybrid | .605/.402/.533 | 16 | 13 | .569 | (.570,.934) | 4800 | 667.5 | — |
| hybrid_fb | .739/.298/.560 | 16 | 13 | .649 | (.570,.934) | 4800 | 667.5 | .1283 |
| hyglide300 | .605/.287/.463 | 16 | 9 | .534 | (.332,.769) | 4800 | 667.5 | — |

Constructive Pareto front: hybrid (k13, seg1 .402, no echo) / fb (k15,
seg1 .292, .127) / glide400 (k13, .368, 0). NO arm holds k>=15 AND seg1>=.3.

New measured statements pinned: (1) seg0-only echo reaches the k=15 ceiling
at ratio .0431 = 34% of fb's echo cost (cheapest k15 arm; its seg2 .466 vs
fb .608 and seg1 .216 = the L84 echo'd-seg0 seg1 tax). (2) The hybrid (hop)
trunk dominates hynohop on BOTH structure axes at equal budget (k 13 v 11,
seg1 .402 v .375; C5's no-hop rule was coined under the RETIRED pooled
worst-seed read).

## Fork oracles (L58 form; per-seed max over noise-shared stored branches;
branch-consistent pick = choose branch per seed maximizing the named axis,
carry that branch's d07 k)

- O1 K0 l84 trunk {hynohop,cont,nod,echo}: seg1 bestfix .375 oracle .590 (+.215,
  pick d07 k=12); seg2 .548/.679 (+.131); d07 .603/.668 (+.065)
- O2 K2000 nohop {hynohop,glide200/300/400}: seg1 .375/.561 (+.186, pick k=12);
  seg2 .649/.759 (+.110); d07 .627/.682 (+.055)
- O3 K2000 echo'd {hynohop_fb,hynohop_fb07}: seg1 .292/.401 (+.109, pick k=14);
  seg2 .608/.719 (+.111); d07 .673/.729 (+.056)
- O4 K2000 hybrid {hybrid,hyglide300}: seg1 .402/.565 (+.163, pick k=10);
  seg2 .533/.599 (+.066); d07 .569/.602 (+.033)

DECISIVE: the branch-consistent oracle pick that maximizes seg1 on the k15
trunk (O3) carries d07 k = 14 < 15 — the union {k>=15 AND seg1 lift} is not
clearable even with per-seed seed knowledge over the whole stored library.

## Realizability (L58 lesson-2 instrument; Spearman over 16 seeds, fork-time
features from the shared prefix)

- O2 glide300-step delta vs SL_exit rho = -.050 / vs mm_exit +.350
- O2 glide400-step delta vs SL_exit rho = -.500 (ANTI) / vs mm_exit +.226
- O3 fb07-fb seg1 delta vs SL_exit rho = +.088 / vs mm_exit +.206
Weak-to-anti; extends L84's SEED-ONLY verdict to the glide and echo forks.

## REGISTERED GATE — GATE-L85 (the deliverable; census 16 seeds, shared noise, l82 machinery)

For any learned gait policy P:
- G1 tracking: seg1 block-err <= .01 on 16/16 seeds.
- G2a duty_07 (C4b row): k >= 15/16 AND Wilson lb >= .717.
- G2b descriptive budget tier: k>=15 with echo ratio <= .0431 => BUDGET-DOMINANT.
- G3 duty_fast (C4c row, gated SEPARATELY): seg1 duty mean >= .358
  (= .292 + 0.8*(.375 - .292): 80%-capture toward no-lever baseline parity
  from the best k15 arm, L6f capture form).
- G4 budget: entrain on-steps <= 4800 AND echo ratio <= .127.
- UNION {G2a AND G3}: DEMOTED to diagnostic (C4d form, L58 lesson-3 rescope)
  — measured ceiling: no fixed arm, and no branch-consistent oracle pick
  (best: k=14 @ seg1 .401), clears it. Registered degenerate branch (L55):
  an always-fb mimic passes G1/G2a/G4 and FAILS G3 — axis gates are
  non-vacuous; any verdict must name which axis carries a pass.
- TRAINING GO/NO-GO (pre-registered): NO-GO for a learned-gait training tick
  on this branch library — beyond-fixed mass is seed/entry-conditioned
  branch selection only (oracle gaps +.11..+.22 seg1), with fork-time
  realizability weak-to-anti (rho -.5..+.35, n=16). GO only if the branch
  library grows (mid-seg branching arms); any such growth re-measures first
  (this card's protocol).

## Verdict levels for this card

PASS = mass_table.py asserts all anchors + all pasted values equal +
emits table/gate; card Verify line = "l85/ mass table + registered gate;
LAB-INTENT.md L85; no live changes". Any mismatch: ADDENDUM here + verdict
rerun only (zero rollouts to lose).
