"""L99 offline gate: deep-hunger wake (owner-approved 11-16, BBS #54).

Owner call (verbatim "yay, B, yay!", one hop Bill -> Miso, Discord
2026-11-16 ~11:40 EST): B = stir past ~.85 hunger, forage once, back
to nest.

GATES
  1. baseline: 40-tick seeded ladder (stir never fires) is BIT-IDENTICAL
     pre-vs-post including the legacy unseeded diary t-draws (seeded
     global) -- the delta adds zero rng draws on unchanged paths
  2. stir fires: forced night, sleep .9, hunger .9 -> act forage_pond,
     hunger lands [.5,.65], stir text, entry carries L100 clock_s stamps
  3. back to nest: the tick AFTER a stir (hunger now < .85) nests again
  4. threshold: hunger .85 asleep -> nest; .86 -> stir (strictly above)
  5. shiny path: forced 12% hit -> hoard +1, parade_ticks 3, parade
     diary entry, stir text names the SHINY
  6. draw discipline: a stir consumes exactly 2 rng draws (relief +
     find); a plain nest consumes 0
  7. needs() rider: asleep+hungry -> settle (not beg); awake+hungry ->
     beg; drowsy-not-nested (.74) + hungry -> beg still; asleep+fed ->
     settle (unchanged path)
  8. water event logged for tonight's consolidation (_log_event)
  9. night sim: 40 forced-night ticks, hunger hand-driven at the live
     accrual rate -- she never sits at 1.0, acts alternate nest/stir
"""
import os
import random
import sys

os.environ["PEBRAIN_FORCE_HOUR"] = "3"            # deep night, before imports
sys.path.insert(0, "/home/t3rpz/critters/peabrain")

import bridge                                     # noqa: E402
from bridge import DuckBridge                     # noqa: E402

ok = fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name}")
    else:
        fail += 1
        print(f"  FAIL {name} {extra}")


class CountRng:
    def __init__(self, r):
        self.r, self.n = r, 0

    def random(self):
        self.n += 1
        return self.r.random()


def night_session(b, hunger=0.5, sleep=0.9):
    s = b.open_session(seed=7)
    s.diary = []
    s.mood.hunger = hunger
    s.mood.sleep = sleep
    s.mood.fear = 0.0
    s.curiosity = 0.0
    s.day_log = []
    return s


def main():
    b = DuckBridge()

    print("gate 1: seeded baseline bit-identity (stir never fires)")
    pre = __import__("json").load(open("lane/l99/seed_pre.json"))
    post = __import__("json").load(open("lane/l99/seed_post.json"))
    check("40-tick ladder bit-identical", pre == post)
    check("ladder exercised forage+nest",
          any(t["act"] == "forage_pond" for t in post)
          and any(t["act"] == "nest" for t in post))

    print("gate 2: stir fires at hunger .9 asleep")
    s = night_session(b, hunger=0.9)
    crng = CountRng(random.Random(5))
    act = b.world_tick(s, rng=crng)
    check("act forage_pond", act == "forage_pond", act)
    check("hunger relieved to [.5,.65]",
          0.5 <= s.mood.hunger <= 0.65, s.mood.hunger)
    e = s.diary[-1]
    check("stir text", "stirred from the nest" in e["text"], e["text"])
    check("L100 stamps inherited", "clock_s" in e and "n" in e, e)

    print("gate 3: back to nest after the stir")
    import datetime as _dt
    s.dream_pool = []          # isolate the ladder: consolidate_night
    s.night_stamp = _dt.date.today()   # repopulates dream_pool (bridge 315)
    crng = CountRng(random.Random(6))   # and dream() rolls rng on a live pool
    act = b.world_tick(s, rng=crng)     # -- stamp short-circuits both
    check("nests again", act == "nest", act)
    check("nest draws 0 rng", crng.n == 0, crng.n)

    print("gate 4: threshold boundary")
    for h, want in ((0.85, "nest"), (0.86, "forage_pond")):
        s = night_session(b, hunger=h)
        act = b.world_tick(s, rng=random.Random(1))
        check(f"hunger {h} -> {want}", act == want, act)

    print("gate 5: shiny path")
    s = night_session(b, hunger=0.9)
    h0 = s.hoard
    # draw 1 = relief (.1*x), draw 2 = find roll (.05 < .12 -> shiny)
    it = iter([0.5, 0.05])
    crng = CountRng(type("G", (), {"random": lambda self_: next(it)})())
    act = b.world_tick(s, rng=crng)
    check("shiny stir act", act == "forage_pond", act)
    check("hoard +1", s.hoard == h0 + 1, (h0, s.hoard))
    check("parade_ticks 3", getattr(s, "parade_ticks", 0) == 3)
    check("stir text names SHINY", "SHINY" in s.diary[-2]["text"],
          s.diary[-2]["text"])
    check("parade diary entry", any(e["act"] == "parade" for e in s.diary))

    print("gate 6: draw discipline")
    s = night_session(b, hunger=0.9)
    crng = CountRng(random.Random(9))
    b.world_tick(s, rng=crng)
    check("stir consumes exactly 2 draws", crng.n == 2, crng.n)

    print("gate 7: needs() rider")
    s = night_session(b, hunger=0.8, sleep=0.8)
    s.mood.trust = 0.9
    check("asleep+hungry -> settle", b.needs(s)["intent"] == "settle",
          b.needs(s)["intent"])
    s2 = night_session(b, hunger=0.8, sleep=0.1)
    s2.mood.trust = 0.9
    check("awake+hungry -> beg", b.needs(s2)["intent"] == "beg",
          b.needs(s2)["intent"])
    s3 = night_session(b, hunger=0.8, sleep=0.74)
    s3.mood.trust = 0.9
    check("drowsy-not-nested -> beg still", b.needs(s3)["intent"] == "beg",
          b.needs(s3)["intent"])
    s4 = night_session(b, hunger=0.3, sleep=0.8)
    check("asleep+fed -> settle", b.needs(s4)["intent"] == "settle",
          b.needs(s4)["intent"])

    print("gate 8: water event logged")
    s = night_session(b, hunger=0.9)
    b.world_tick(s, rng=random.Random(3))
    check("day_log water entry",
          any(ev.get("ev") == "water" for ev in s.day_log), s.day_log[-1:])

    print("gate 9: 40-tick night sim (live accrual ~.03/tick)")
    s = night_session(b, hunger=0.5)
    acts, hmax = [], 0.0
    for i in range(40):
        if i:                                   # accrue ~45 s per tick
            s.mood.hunger = min(1.0, s.mood.hunger + 0.032)
            s.mood.sleep = 0.9                  # still deep night
            s.mood.fear = 0.0
        acts.append(b.world_tick(s, rng=random.Random(100 + i)))
        hmax = max(hmax, s.mood.hunger)
    stirs = acts.count("forage_pond")
    check("never maxed", hmax < 1.0, hmax)
    check("stirs happened 2..8", 2 <= stirs <= 8, stirs)
    check("mostly nesting", acts.count("nest") >= 20, acts.count("nest"))
    check("hunger ends mid-band", 0.4 <= s.mood.hunger <= 0.9,
          s.mood.hunger)

    print(f"\n{ok} pass, {fail} fail")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
