# L86 PREREG — hybrid-echo-combo (LANE.md ideas 43, first unchecked item)

Card: L86 hybrid-echo-combo. L85's two best structure facts in ONE arm: the
hop trunk (dominates nohop on both structure axes at equal budget: k 13 v 11,
seg1 .402 v .375) x seg0-only echo (ties the k15 ceiling at ratio .0431).
Question: does the hop lift the echo'd-seg0 arm above the stored Pareto front
(k>=15 AND seg1>=.358), or does the L84 echo'd-seg0 entry tax outrank the hop
(C4c closes for good)?

## Arms (ALL hybrid trunk; census SEEDS = [11,22,33]+101..113, n=16; shared
## per-step noise, ONE generator, l77 step order: mm -> amp -> hop -> echo)

- hybrid       (anchor, no echo; HOPA verbatim l59/l77: DNge046-L 2 cells,
                HOP_AMP .5, HOP_VW 40, TRANS [2000,4000])
- hybrid_fb    (anchor, echo throughout, l66 content cell verbatim
                gfb .1 / delay 5 / sign -1)
- hybrid_e0    (NEW: EON[0:2000) only — echo off from k=2000 on)
- AMPA identical for all arms (l59 hybrid AMPA, 4800 on-steps incl settle).

## Anchors (all must pass; every expected value derived from STORED artifacts)

- A1 hybrid == l59/raw_l59.npz BIT-IDENTICAL, mm + fL/fR/eL/eR, all 16 seeds
  (31st consecutive chain anchor if green).
- A2 hybrid_fb == l77/raw_l77.npz BIT-IDENTICAL, mm + 4 sigs, all 16 seeds.
- A3 hybrid_e0 vs hybrid_fb: prefix indices [0,2000] inclusive max|d| == 0.0;
  first_div == 2001 on every seed (EON flip enters drive at k=2000, MOTOR
  pools see it one hop later — l82 stored {2001} law, l85 A4 {4001} same law);
  NOT degenerate: whole-run max|d| > 0 (else NO VERDICT, fix wiring, reroll).
- A4 echo aliveness: first_div(hybrid_fb vs hybrid) == 6 every seed (l77
  stored fd_histogram hybrid_fb {6:16}); first_div(hybrid_e0 vs hybrid) == 6
  every seed.
- A5 budget (exact mA-gated echo mass, l82 budget block): hybrid_fb echo mass
  == 85.6 (tol .1) ratio .1283 (tol .001) [l85 pinned]; hybrid_e0 echo mass
  == 28.8 (tol .1) ratio band [.0420,.0445] — its mA[0:1995] is bit-identical
  to hybrid_fb's (A3 prefix), whose seg0 equals the nohop echo'd-seg0 family
  (l84/l85 pinned 28.8 / .0431).
- A6 CERTIFICATION (L85 across-run form): my re-derived distributions for
  hybrid and hybrid_fb equal l85/mass_table.json EXACTLY —
  hybrid: seg means [.605,.402,.533], seg k [10,7,9], seg wilson
    [[.386,.815],[.231,.668],[.332,.769]], err_le01 [0,16,0],
    duty07 mean .569 k 13 wilson [.57,.934],
    per-seed seg1 [.133,.627,.0,.347,.5,.793,.893,.007,.233,.207,.713,.0,.407,.7,.0,.873],
    per-seed d07  [.667,.56,.573,.403,.713,.527,.317,.717,.607,.55,.667,.51,.713,.523,.493,.563];
  hybrid_fb: seg means [.739,.298,.56], seg k [15,4,12], seg wilson
    [[.717,.989],[.102,.495],[.505,.898]], err_le01 [0,16,0],
    duty07 mean .649 k 13 wilson [.57,.934],
    per-seed seg1 [.06,.0,.087,.433,.0,.247,.713,.0,.427,.927,.0,.647,.0,.927,.307,.0],
    per-seed d07  [.693,.793,.713,.647,.573,.78,.763,.733,.647,.64,.447,.483,.457,.647,.657,.713].
- A7 parity: hybrid_e0 seg0 cells (duty/SL/SR/f/err) EXACTLY equal hybrid_fb's
  per seed (S windows at TS<2000 read only trace indices <=1999 — the EON
  flip at k=2000 cannot enter them; l82 R1 form).

## Registered reads — GATE-L85 rows applied to hybrid_e0, SEPARATE axes
## (the union {G2a AND G3} stays DEMOTED to diagnostic, L85 C4d form)

- G1 tracking: hybrid_e0 seg1 block-err <= .01 on 16/16 seeds.
- G2a duty_07 (C4b row): k >= 15/16 AND Wilson lb >= .717.
- G2b budget tier: k>=15 with echo ratio <= .0431 => BUDGET-DOMINANT.
- G3 duty_fast (C4c row): seg1 duty mean >= .358 (= .292 + .8*(.375-.292)).
- G4 budget: on-steps <= 4800 AND echo ratio <= .127.

## Verdict levels

- E1 PARETO MOVER: G2a AND G3 both clear — a point NO stored arm reaches
  (stored k15 arms sit seg1 .216-.298; hybrid trunk seg1 .402 at k13) =>
  C4b's one measured lever extends to the hop trunk at ~34% of fb echo cost;
  L87's branch library grows from hybrid_e0.
- E2 TAX LAW WINS: seg1 < .358 => the L84 echo'd-seg0 entry tax outranks the
  hop lift => C4c closes for good (no lever for fast-seg structure). If G2a
  still passes, name the axis split explicitly (always-fb mimic shape:
  G1/G2a/G4 pass, G3 fail — the registered non-vacuous branch, L55).
- Reported, never gating: seg0/seg2 means + paired per-seed deltas of
  hybrid_e0 vs hybrid and vs hybrid_fb (seg1 and seg2), d07 per-seed.
- Degenerate wiring branch: hybrid_e0 bit-identical to hybrid_fb whole-run
  => NO VERDICT (EON never applied); fix wiring, reroll.

## Prediction (mine, non-binding, from the pinned family table)

seg0 -> .739 exact (A7 parity); seg1 -> .21-.31 (E2 likely: nohop fb07's
.216 says echo-off-in-seg1 does not restore the entry-carried cost, and
hybrid_fb pays .298 with echo ON); d07 k genuinely open (seg0 .739 +
hop-rerolled no-echo seg2 ~.46-.56 => per-seed means ~.60-.65, the k>=.5
coin sits near the middle of the seed distribution).
