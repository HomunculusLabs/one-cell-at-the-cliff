#!/usr/bin/env python3
"""t287: append this tick's CLAIM line to LANE-LOG.md (append-only, once-only guard)."""
import os

LOG = os.path.expanduser("~/critters/peabrain/LANE-LOG.md")
LINE = (
    "\ntick 287 | 2026-11-25 13:05 | L294 (WHAT PREDICTS A WEIGHT-MATCHED SET EFFECT; "
    "static re-analysis of STORED arrays, PREREG first, zero rollouts) | CLAIM — hour 13 at "
    "wakeup = build tick; no LANE-HALT; archive pre-step ran (snap_20261125_130408 diary=50 "
    "day_log=100 hoard=287 mood=happy:high intent=to_pond); GPU 0% / 7.6 GiB = the live ducks "
    "+ desktop only, no train/harness process; fly duck active, same PID 2706698, NRestarts 0, "
    "/needs 200 in 0.293 s. Box at claim: load 2.4 on 16 cores, ~8 GB available, swap 28 of 30 "
    "GB used with nothing of mine running. Precedence: tick-259 reading unchanged for "
    "L97/L174/L179/L181/L192/L197-L204; the L241-L289 backlog (49 cards) is still "
    "un-re-classified (the tick-277 curation-debt disclosure stands). L294 is the tick-286 "
    "handoff (\"Next: L294\"): tick 285's claim (10:5x) is 2h14m old at wakeup = stale since "
    "12:50; that tick died on HTTP 429 after writing banc/l294/claim_t285.txt + survey2.py and "
    "nothing else (no survey2.out, no PREREG, no static script, no result). This tick RE-TAKES "
    "L294: run survey2.py (structure only, no covariate scored against an effect), then PREREG "
    "with the covariate family and the description/prediction split registered BEFORE any "
    "covariate is scored against an effect, then one static script run through its last write.\n"
)

txt = open(LOG, encoding="utf-8").read()
GUARD = "tick 287 | 2026-11-25 13:05 | L294"
if GUARD in txt:
    print("ALREADY PRESENT — not appended")
else:
    if not txt.endswith("\n"):
        txt += "\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(LINE)
    print("appended; occurrences now:", open(LOG, encoding="utf-8").read().count(GUARD))
