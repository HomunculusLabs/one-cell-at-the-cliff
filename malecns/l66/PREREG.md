# L66 PREREG — content-cell-census (registered 2026-11-14 ~06:1x, BEFORE any rollout)

Card: LANE.md ideas-32 L66. L64 found ONE loop-content window (g .1, sign −,
delay 5 = 50 ms) at n=3 anchor seeds. Before it enters L57 row D: census weight
+ point-vs-basin neighborhood.

## Design

- Machinery l64_grid.py / l64_sham.py verbatim (substrate n=21,516; base chop
  schedule 500-on/400-off at 0.7 Hz, continuous 1.4 Hz seg2; ENT_AMP .3;
  G .01 / BETA 2 / D .05; SETTLE 400 echo-free; shared-generator noise, one
  nz per step for all arms; echo OFF during settle; echo form
  drive[mech,0] += GFB * SIGN * mass[k-DELAY], window index k; own mass =
  mean of the 4 Tr antagonist pool traces recorded post-step).
- Census: SEEDS = [11,22,33] + range(101,114) (l45b census grid, n=16).
  Arms (11): OPEN (hynohop, no echo) | FB = g01_d05_m (gain .1, −, delay 5)
  | SHAM = sham_d05m (donor mass trace, same gain/sign/delay) | 8 NEIGHBORS
  delay {3,4,6,8} x gain {.05,.15}, sign − (n{005,015}_d{03,04,06,08}_m).
- Donor (l63/l64 form extended to census n): l59 STORED hynohop 4-trace mean;
  DONOR[s] = next census seed cyclic (11<-22<-33<-101<-...<-113<-11; never
  self). Donor completeness asserted before rollouts.
- 11 arms x 16 seeds = 176 rollouts, CPU-only, incremental raw_partial.npz
  per seed (L45a rule), full raw npz checkpoint BEFORE analysis.

## Registered reads (discriminating windows, never pooled — L55/L63 lesson)

- OFF-WINDOW DUTY per (arm,seed): fraction of off-gap S-points (w=300, TS3
  grid, 4x400-step gaps) with S_L >= .25 AND S_R >= .25; lift = arm − open,
  PAIRED per seed (L45b rule).
- Per-side decomposition: S_L / S_R off-gap means per seed (L46/L59 form).
- SEG2 LOCK per (arm,seed): mean per-block (500 steps, blocks starting
  2500/3000/3500) dom-freq |err| vs 1.4; catastrophic flag > .5; "lock
  preserved" = median err <= max(.01, 2 x open median) AND max err <= .5.
- DM probe per fb/neighbor arm: max|d mm| vs OPEN beyond the delay prefix;
  FLOOR-BURIED verdict if exactly 0.0 (L35 class).

## Registered predictions + verdict rules

- G1 (L57 row D entry gate, the card's wording): P(fb lift > 0) >= 11/16
  (Wilson 95% CI reported) AND mean sham lift <= 0.5 x mean fb lift.
  PASS = content cell enters L57 row D as a measured option; FAIL = stays
  n=3 anchor-only finding.
- G2 (point vs basin): a neighbor CARRIES CONTENT if mean lift >= +.05 AND
  P(lift>0) >= 11/16 AND lock preserved AND dm > 0. BASIN if >= 5/8 carry;
  POINT if <= 2/8; MIXED if 3-4/8.
- P3 (miss anatomy, L56/L59 law): on census seeds where fb off-duty < open,
  the marginal side is S_L (S_L < S_R) — predicted on >= 2/3 of miss seeds;
  vacuous if G1 hits 16/16 (register that branch explicitly).
- Degenerate branch (L55 rule): fb arm bit-identical to OPEN beyond the
  delay prefix on ANY seed = WIRED-DEAD flag for that seed; G1 is not scored
  on a fully bit-identical arm (wiring bug -> fix + rerun). All 16
  bit-identical = run void.

## Registered anchors (enumerated keys ONLY; diagnostics get their own check)

- C0: OPEN bit-identical to l55/raw_l55.npz seeds 11/22/33 (keys
  mm|fL|fR|eL|eR _hynohop_{s}, [0,6000), max|d| == 0.0) — 19th consecutive
  chain anchor.
- C0x: in-run FB g01_d05_m bit-identical to l64/raw_l64.npz same key set,
  seeds 11/22/33, 0.0 (cross-run wiring replication).
- C0P: every echo arm's first divergence from OPEN == its delay step
  (first_div index == delay) unless dm == 0 (then floor-buried, disclosed).
- C0v (value anchors from l64 STORED results, L44 rule): fb off-duty seeds
  11/22/33 == [.432, .477, .523] (tol .003), OPEN == [.227, .250, .386],
  fb dm >= .01.

## ADDENDUM 1 (post-run, pre-verdict — gate-logic fix, rollouts untouched)

C0P as registered ("first_div == delay") was derived from LANE-LOG's summary
sentence; L64's STORED results.json (the artifact, L44 rule) shows first_div
= delay + 1 for EVERY cell (d5->6, d2->3, d10->11, d20->21, 3/3 seeds):
the echo enters mech drive at k=delay, mech->pool is 2-hop, so recorded
pool means first differ at delay+1. Corrected anchor: first_div == delay+1
for all 10 echo arms x 16 seeds AND center fb/sham first_div == l64 stored
values (bit-identity implies it). Run-1 C0P False was the GATE's error, not
the run's (l59 class). Re-derived from stored json; zero reruns.
