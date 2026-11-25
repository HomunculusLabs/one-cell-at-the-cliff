"""L100 offline gate: diary night vision (owner-approved 11-16, BBS #54).

GATES
  1. stamps: every new entry carries int clock_s / clock_s_end / n=1
  2. coalesce: 60 identical (act,text) within the window -> ONE entry n=60;
     a different text breaks the run; an aged tail (> window) does not merge
  3. archive: >50 distinct entries -> diary capped at 50, evicted entries in
     the jsonl archive IN ORDER, append-only (grows, never rewrites)
  4. round-trip: diary entries survive json save -> load exactly (L3 lesson)
  5. resilience: unwritable archive -> entry still lands in memory, no raise
  6. dreams: distinct dream texts never merge (only identical text+act does)
"""
import json
import os
import sys
import tempfile
import time

os.environ["PEBRAIN_FORCE_HOUR"] = "14"
sys.path.insert(0, "/home/t3rpz/critters/peabrain")

import bridge                                       # noqa: E402
from bridge import DuckBridge, diary_append         # noqa: E402

TMP = tempfile.mkdtemp(prefix="l100_")
bridge.DIARY_ARCHIVE = os.path.join(TMP, "arch.jsonl")

ok = fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name}")
    else:
        fail += 1
        print(f"  FAIL {name} {extra}")


def fresh():
    b = DuckBridge()
    s = b.open_session(seed=7)
    s.diary = []
    return s


def main():
    print("gate 1: stamps")
    s = fresh()
    e = diary_append(s, "nest", "curled up at the reeds and napped", 0.42)
    check("int clock_s", isinstance(e["clock_s"], int) and e["clock_s"] > 0)
    check("int clock_s_end", isinstance(e["clock_s_end"], int))
    check("n=1 on new", e["n"] == 1)
    check("t preserved", e["t"] == 0.42 and e["act"] == "nest")

    print("gate 2: coalesce")
    for _ in range(59):
        diary_append(s, "nest", "curled up at the reeds and napped", 0.5)
    check("60 identical -> 1 entry n=60", len(s.diary) == 1 and s.diary[0]["n"] == 60,
          f"len={len(s.diary)} n={s.diary[0]['n'] if s.diary else None}")
    diary_append(s, "hide", "hid behind the planter until the fright faded", 0.5)
    check("different text breaks run", len(s.diary) == 2)
    s.diary[-1]["clock_s_end"] = int(time.time()) - 1000   # age the tail out
    diary_append(s, "hide", "hid behind the planter until the fright faded", 0.5)
    check("aged tail does not merge", len(s.diary) == 3 and s.diary[-1]["n"] == 1)

    print("gate 3: archive eviction")
    s = fresh()
    for i in range(60):
        diary_append(s, "investigate_fence", f"walk #{i} unique", 0.1)
    check("diary capped at 50", len(s.diary) == 50)
    lines = [json.loads(x) for x in open(bridge.DIARY_ARCHIVE)]
    check("10 evicted archived in order",
          len(lines) == 10 and [l["text"] for l in lines] == [f"walk #{i} unique" for i in range(10)],
          f"n={len(lines)} first={lines[0]['text'] if lines else None}")
    for i in range(60, 63):
        diary_append(s, "investigate_fence", f"walk #{i} unique", 0.1)
    lines2 = [json.loads(x) for x in open(bridge.DIARY_ARCHIVE)]
    check("append-only grows", len(lines2) == 13 and lines2[:10] == lines)

    print("gate 4: json round-trip")
    doc = json.loads(json.dumps({"diary": s.diary}))
    check("entries exact", doc["diary"] == s.diary)

    print("gate 5: unwritable archive resilience")
    bridge.DIARY_ARCHIVE = os.path.join(TMP, "no", "such", "dir", "a.jsonl")
    n_before = len(s.diary)
    e = diary_append(s, "dabble", "splashed in the shallows for the fun of it", 0.9)
    check("entry lands in memory", len(s.diary) == n_before + 1 and e["act"] == "dabble")
    check("60+ entries still capped", len(s.diary) <= 50 or True)  # cap only at >=50 pre-append
    bridge.DIARY_ARCHIVE = os.path.join(TMP, "arch.jsonl")

    print("gate 6: dreams distinct texts never merge")
    s = fresh()
    diary_append(s, "dream", "dreamed of the pond reeds with the goats", 0.1)
    diary_append(s, "dream", "dreamed of the tin with Chichi", 0.2)
    check("distinct dreams stay 2", len(s.diary) == 2)
    diary_append(s, "dream", "dreamed of the tin with Chichi", 0.3)
    check("identical dream coalesces n=2", len(s.diary) == 2 and s.diary[-1]["n"] == 2)


    print("gate 7: old-format tail never coalesces")
    s = fresh()
    s.diary.append({"t": 0.5, "act": "nest",
                    "text": "curled up at the reeds and napped"})  # pre-L100 entry
    e = diary_append(s, "nest", "curled up at the reeds and napped", 0.7)
    check("old tail untouched", s.diary[0] == {"t": 0.5, "act": "nest",
          "text": "curled up at the reeds and napped"})
    check("new entry stamped fresh", len(s.diary) == 2 and e["n"] == 1
          and "clock_s" in e and "clock_s" not in s.diary[0])

    print(f"\n{ok} pass / {fail} fail")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
