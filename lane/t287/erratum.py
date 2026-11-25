#!/usr/bin/env python3
"""Tick 287 erratum: VERDICT.md said T1's p is '+0.013' from the 0.10 bar; the stored q is 0.08785
so the margin is 0.0122. Fix VERDICT.md (exact replace, once-only) and append an erratum line to
LANE-LOG.md (append-only). The margin is COMPUTED from the stored artifact, not typed."""
import json

RES = "/home/t3rpz/critters/peabrain-lab/banc/l294/results_l294.json"
VER = "/home/t3rpz/critters/peabrain-lab/banc/l294/VERDICT.md"
LOG = "/home/t3rpz/critters/peabrain/LANE-LOG.md"

q = json.load(open(RES))["qvals"]["T1"]["q"]
d = 0.10 - q
print("stored T1 q", q, "| margin to the 0.10 bar", d, "-> %.4f" % d)

BAD, GOOD = "T1's p 0.013 higher", "T1's p %.4f higher" % d
v = open(VER, encoding="utf-8").read()
if GOOD in v:
    print("VERDICT already corrected")
elif v.count(BAD) == 1:
    open(VER, "w", encoding="utf-8").write(v.replace(BAD, GOOD))
    a = open(VER, encoding="utf-8").read()
    print("VERDICT corrected: BAD %dx GOOD %dx" % (a.count(BAD), a.count(GOOD)))
else:
    raise SystemExit("HALT: BAD occurs %dx" % v.count(BAD))

tag = "L294 | erratum"
log = open(LOG, encoding="utf-8").read()
if tag in log:
    print("ERRATUM already present")
else:
    open(LOG, "a", encoding="utf-8").write(
        "\ntick 287 | 2026-11-25 13:2x | L294 | erratum — the shipped line's 'T1 +0.013 higher -> C' is a rounding "
        "slip: the stored q is %.5f, so the margin to the 0.10 bar is %.4f (computed from results_l294.json, not "
        "typed). VERDICT.md line corrected the same way. No result, label or prediction changes." % (q, d))
    print("ERRATUM appended; 'tick 287 |' now occurs %dx" % open(LOG, encoding="utf-8").read().count("tick 287 |"))
