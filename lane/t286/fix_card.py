"""Exact repair of the L295 card's tick-284 tail in LANE.md after two fuzzy patch slips. Once-only guards."""
PB = "/home/t3rpz/critters/peabrain"
P = f"{PB}/LANE.md"
txt = open(P, encoding="utf-8").read()
lines = txt.split("\n")
n_before = len(lines)

bad1 = "      the aversive cluster and their variable is      DAN DRIVE at"
good1 = "      the aversive cluster and their variable is DAN DRIVE at"
assert txt.count(bad1) == 1, f"bad1 count {txt.count(bad1)}"
txt = txt.replace(bad1, good1)

good_tail = (good1 + "\n      consolidation, ours is reward-DAN REST.]\n"
             "      [tick 286, 11-25 12:0x: SLICE 1 SHIPPED — the card's proposal (1)")
assert txt.count(good_tail) == 1, f"good_tail count {txt.count(good_tail)}"
assert "drives at consolidation" not in txt, "garbled line still present"
assert "is      DAN" not in txt

open(P, "w", encoding="utf-8").write(txt)
back = open(P, encoding="utf-8").read()
bl = back.split("\n")
i = next(k for k, l in enumerate(bl) if "their variable is DAN DRIVE at" in l)
print(" repaired region:")
for k in range(i - 1, i + 4):
    print(f"  {k+1}|{bl[k]}")
print(f" lines {n_before} -> {len(bl)} (expect +23 vs the 12112 pre-patch)")
print(" tick 286 note occurrences:", back.count("[tick 286, 11-25 12:0x: SLICE 1 SHIPPED"))
print(" unchecked boxes:", sum(1 for l in bl if l.startswith("- [ ]")), "| L295 still open:", any(l.startswith("- [ ] L295.") for l in bl))
print(" ideas 134 header intact:", "## ideas 134 (seeded 2026-11-25, tick 284 research" in back)
