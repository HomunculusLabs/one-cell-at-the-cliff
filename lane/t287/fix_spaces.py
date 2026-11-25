#!/usr/bin/env python3
"""Repair the stray spaces the fuzzy patcher left in the new L297 card (LANE.md) and in finish.py."""
BAD = "that would).      (c) The n-11 reversal"
GOOD = "that would). (c) The n-11 reversal"
for path in ("/home/t3rpz/critters/peabrain/LANE.md", "/home/t3rpz/critters/peabrain/lane/t287/finish.py"):
    t = open(path, encoding="utf-8").read()
    n = t.count(BAD)
    if n == 0 and GOOD in t:
        print(path.split("/")[-1], "already clean"); continue
    if n != 1:
        raise SystemExit("HALT %s: BAD occurs %dx" % (path, n))
    open(path, "w", encoding="utf-8").write(t.replace(BAD, GOOD))
    a = open(path, encoding="utf-8").read()
    print(path.split("/")[-1], "repaired: BAD now %dx, GOOD %dx, bytes %d -> %d" % (a.count(BAD), a.count(GOOD), len(t.encode()), len(a.encode())))
