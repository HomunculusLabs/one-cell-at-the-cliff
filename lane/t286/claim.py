"""Tick 286 CLAIM on L295 (PREREG-on-stored-day_logs slice). Idempotent."""
import os
import time

LOG = "/home/t3rpz/critters/peabrain/LANE-LOG.md"
tag = "tick 286 |"

txt = open(LOG, encoding="utf-8").read()
if tag in txt:
    print("ALREADY PRESENT -- not appending again")
    raise SystemExit(0)

l1, l5, l15 = os.getloadavg()
with open("/proc/meminfo") as f:
    mem = {ln.split(":")[0]: int(ln.split()[1]) for ln in f if ":" in ln}
avail_gb = mem["MemAvailable"] / 1048576
sw_used = (mem["SwapTotal"] - mem["SwapFree"]) / 1048576
sw_tot = mem["SwapTotal"] / 1048576
stamp = time.strftime("%Y-%m-%d %H:%M")

line = (
    f"\ntick 286 | {stamp} | L295 (THE NIGHT PASS REPLAYS ONLY HER OWN POST-MIDNIGHT WATER, AND NOTHING BOUNDS THE WORLD DELTA; "
    "slice = the card's own ORDER, first half: PREREG on the STORED day_logs, zero rollouts; the live rule stays parked on the owner question) | CLAIM — "
    "hour 11 at wakeup = build tick; no LANE-HALT; archive pre-step ran (snap_20261125_115240 diary=50 day_log=100 hoard=286 mood=happy:low intent=to_fence); "
    "GPU 1% / 7.4 GiB = the live ducks + desktop only, no train/harness process; fly duck active, same PID 2706698, NRestarts 0, /needs 200. "
    f"Box at claim: load {l1:.1f} on 16 cores, ~{avail_gb:.0f} GB available, swap {sw_used:.0f} of {sw_tot:.0f} GB used with nothing of mine running. "
    "Precedence: tick-259 reading unchanged for L97/L174/L179/L181/L192/L197-L204; the L241-L289 backlog (49 cards) is still un-re-classified (the tick-277 curation-debt disclosure stands). "
    "L294 is NOT taken this tick: its claim by tick 285 (10:50) is 62 min old at wakeup = FRESH under the 2 h rule, and that tick died on HTTP 429 (the cron run is recorded FAILED) "
    "after writing banc/l294/claim_t285.txt + survey2.py and nothing else (no PREREG, no static script, no result; one log line, no outcome). "
    "The claim is honored as written: it goes stale at 12:50, so the next tick takes L294. L295 is the next unchecked item in file order (the L294 head is claimed; L97/L174/... are tick-259 non-takeable). "
    "This tick: one record of every stored type BEFORE any loop (L293 build law), then PREREG in lane/l295/ naming the rules and the branch BEFORE any rule is scored on a day_log, then one static script through its last write."
)

with open(LOG, "a", encoding="utf-8") as f:
    f.write(line if txt.endswith("\n") else "\n" + line)

after = open(LOG, encoding="utf-8").read()
n = after.count(tag)
print(f"appended; '{tag}' now occurs {n}x; log lines = {after.count(chr(10))}")
print(line[:260])
