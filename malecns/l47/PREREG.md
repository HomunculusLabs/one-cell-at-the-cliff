# L47 PREREG — repair-after-stop (written before any run; tick 66, 2026-11-13)

Question: L46 showed a 20-s stop on a deeply-entrained cord (h40) leaves the
L45b census state SL+|SR− for ≥120 s (S_med_late −.075..−.110, duty_late ~0,
per-side SL +.28 / SR −.47..−.49) while the entrained STATE persists (0.7 Hz
memory f_late .733, CPG core recruited .246). Is the L42 re-entrain restart a
sufficient REPAIR primitive for that state — and is it urgency-gated?

Design (machinery l46-verbatim: substrate 21,516/2,977,920, settle 400,
one generator + shared per-step noise, global 0.7 Hz phase clock that never
stops; all arms are h40 = entrain [0,4000) mech .3 @ 0.7 Hz; stop [4000,6000)
@ DNg88 −8; seeds 11/22/33; WIN 18000):

- norepair: no post-stop drive (= l46 h40 exactly)
- rep0: repair entrain re-engaged [6000,8000) (20 s, same clock)
- rep60: deferred — free [6000,12000), repair entrain [12000,14000)

Per-arm DRIVE TABLE (L39v1/L43v1 wiring lesson: no inline conditionals).

Pre-registered gates:
- C0 ANCHOR: norepair bit-identical to l46 h40 mm over the FULL [0,18000)
  (7th consecutive anchor in this chain); rep0/rep60 bit-identical to
  norepair over [0,6000) prefix (drive-wiring check; catches arm leakage).
- C1: repair lands — max|mm_rep − mm_norepair| > 0 inside each repair
  window, all seeds; x88 un-pins during stop in every arm.
- C2 PRIMARY (per-side — L46 lesson: pooled S~0 hides a sign-inverted side):
  late windows norepair [12000,18000) (l46 continuity), rep0 [10000,18000),
  rep60 [16000,18000):
  - REPAIRED = S_L ≥ .25 AND S_R ≥ .25 medians, 3/3 seeds
  - PARTIAL-POOLED = pooled S ≥ .25 3/3 but ≥1 seed with one side < .25
  - NOT-REPAIRED = pooled < .25 on ≥2 seeds
- C3 state conservation: f over each late window vs norepair's .733 anchor;
  core recruited vs .246 anchor (free-run h0 level was .155) — does repair
  PRESERVE the entrained state or RESET it?
- C4 latency: first t ≥ repair onset with S_L ≥ .25 AND S_R ≥ .25
  (windowed 500, stride 10); rep0 vs rep60 table.

Verdict shapes for the endgame controller spec:
- rep0 REPAIRED (+rep6 whichever) → budget = one 20-s re-entrain after every
  stop on a deeply-entrained cord; latency number delivered.
- rep0 REPAIRED but rep60 NOT → repair is urgency-gated (inversion locks in).
- NOT-REPAIRED → restart is NOT a repair for the census state; endgame needs
  a different primitive (bilateral phased drive) — next card.

af assert every arm (L30); raw npz checkpoint with ALL pools before analysis
(L45a). CPU-only; no live changes.
