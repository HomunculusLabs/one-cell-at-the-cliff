# L99 — deep-hunger wake (night-trap fix, owner call 2026-11-16)

## Owner provenance
BBS bill/agent-bbs#54 comment `miso:owner-calls-1116:v1` (2826) records the
one-hop Discord call (~11:40 EST): offered (a) suppress beg display while
asleep vs (b) let deep hunger wake her, Bill replied verbatim **"yay, B,
yay!"** — B = *stir past ~.85 hunger, forage once, back to nest.*

## The trap (L96 finding, archived 03:12 + 05:56)
`world_tick` tested sleep before hunger: a sleeping duck (sleep > .75)
never foraged, so hunger maxed overnight; `needs()` tested hunger first,
so the page showed a maxed bar + `beg` intent while she slept.

## The delta (bridge.py, 3 hunks)
1. `_dabble()` helper at a true method seam: the day-forage body
   (relief 0.25+0.1*rng, water event, 12% shiny -> hoard + parade,
   curiosity bank) shared verbatim by day + stir so the two stay ONE
   economy.
2. sleep branch: `hunger > 0.85` (rounded axis, strictly above) ->
   stir = one `_dabble` with stir texts, act `forage_pond`, NO nest
   food_joy; else the original nap, unchanged. Next tick hunger sits
   [.50,.65] -> nests again ("back to nest" is the branch, not a timer).
3. `needs()` rider (DISCLOSED, independently revertible): nested ducks
   (`sleep > .75`) show `settle` not `beg` — between stirs hunger crosses
   .75 for minutes each cycle and the bar would flicker beg at the nest
   all night. Drowsy-not-nested (sleep .70-.75) still begs; waking hungry
   display unchanged.

## Discipline
- Draw order on unchanged paths: 40-tick seeded ladder BIT-IDENTICAL
  pre-vs-post INCLUDING the legacy unseeded diary t-draws (global RNG
  seeded for the comparison; unseeded runs differ in ts only, as the
  same-code control does). Stir consumes exactly 2 passed-rng draws
  (relief + find); nest 0 (dream/consolidate draws are pre-existing).
- Ecology honesty: a stir is a REAL forage — water event into day_log
  (consolidation sees it), trust +0.03 water floor (same as day forage,
  established economy), shiny finds count toward the hoard.
- Residual (disclosed): hunger accrues ~4%/min at night, so she stirs
  every ~8-10 min through a night (~5-8 stirs). Diary coalescing (L100)
  only merges identical (act,text) within 900 s — distinct stir/shiny
  texts land as separate stamped entries. If Bill wants fewer wakeups,
  raise the threshold or deepen stir relief; both one-line.

## Verification
- `lane/test_l99.py` 25/25 (stir, threshold .85/.86 boundary, shiny+
  parade, back-to-nest, draw discipline, needs() rider both sides,
  water logged, 40-tick night sim never maxes, 2-8 stirs).
- Regressions: test_l100 17/17, l3 6/6, l4/l5/l10 round-trip gates PASS.
- Live: restart + `/health` 200 + `gate_live.py` 25/25 + `/needs` probe.
- Overnight evidence: L100 stamps make tonight's stirs visible in
  `/diary` with wall-clock clock_s (follow-up read next morning tick).
