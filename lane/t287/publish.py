#!/usr/bin/env python3
"""Tick 287: append the L294 entry to the publish digest (idempotent: gated on the entry HEADER)."""
import hashlib

DIG = "/home/t3rpz/.hermes/profiles/maple/playground/website/publish/peabrain.md"
ENT = "/home/t3rpz/critters/peabrain/lane/t287/digest_entry.md"
HEAD = "## L294 — what predicts a weight-matched set's effect"

txt = open(DIG, encoding="utf-8").read()
entry = open(ENT, encoding="utf-8").read()
if HEAD in txt:
    print("DIGEST: entry already present; nothing appended")
else:
    assert txt.endswith("\n"), "digest does not end with a newline"
    assert txt.count("## L29") >= 2
    body = entry.strip("\n")
    open(DIG, "a", encoding="utf-8").write("\n" + body + "\n")
    after = open(DIG, encoding="utf-8").read()
    print("DIGEST appended: lines %d -> %d | header count %d | ends with newline %s" % (
        txt.count("\n"), after.count("\n"), after.count(HEAD), after.endswith("\n")))
    print("sha256", hashlib.sha256(after.encode("utf-8")).hexdigest())
