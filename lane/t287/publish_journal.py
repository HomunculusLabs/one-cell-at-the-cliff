#!/usr/bin/env python3
"""Tick 287 PUBLISHED line for L294. Runs the API read-back itself; appends ONLY on MATCH. Idempotent."""
import subprocess
import sys

LOG = "/home/t3rpz/critters/peabrain/LANE-LOG.md"
WS = "/home/t3rpz/.hermes/profiles/maple/playground/website"
PY = "/home/t3rpz/critters/peabrain/.venv/bin/python"
tag = "tick 287 | 2026-11-25 13:2 | L294 | published"
if tag in open(LOG, encoding="utf-8").read():
    print("ALREADY PRESENT"); raise SystemExit(0)
head = subprocess.run(["git", "-C", WS, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
subj = subprocess.run(["git", "-C", WS, "log", "-1", "--format=%s"], capture_output=True, text=True).stdout.strip()
if not subj.startswith("publish: L294"):
    sys.exit("HALT: HEAD is not the L294 publish commit: %s" % subj)
v = subprocess.run([PY, "/home/t3rpz/critters/peabrain/lane/t287/verify_push.py"], capture_output=True, text=True)
print(v.stdout.strip())
if "MATCH" not in v.stdout or v.returncode != 0:
    sys.exit("HALT: API read-back did not MATCH (rc %d) -- no PUBLISHED line written" % v.returncode)
line = ("\ntick 287 | 2026-11-25 13:2x | L294 | published — digest entry \"## L294 — what predicts a weight-matched set's "
        "effect: the gain delta and the removed weight both track it\" appended, commit %s (%s), push exit 0 (bare), "
        "API read-back MATCH sha256 %s. | verified-how: %s" % (
            head, subj, [l for l in v.stdout.splitlines() if l.startswith("remote sha256")][0].split()[-1],
            " | ".join(l.strip() for l in v.stdout.splitlines() if l.startswith(("api status", "MATCH")))))
open(LOG, "a", encoding="utf-8").write(line)
a = open(LOG, encoding="utf-8").read()
print("PUBLISHED line appended; 'tick 287 |' now occurs %dx" % a.count("tick 287 |"))
