"""Tick 286 SHIPPED line for L295 slice 1. Idempotent."""
LOG = "/home/t3rpz/critters/peabrain/LANE-LOG.md"
tag = "tick 286 | 2026-11-25 11:54-"
txt = open(LOG, encoding="utf-8").read()
if tag in txt:
    print("ALREADY PRESENT"); raise SystemExit(0)

line = (
    "\ntick 286 | 2026-11-25 11:54-12:0x | L295 slice 1 (PREREG on the STORED day_logs; static, zero rollouts) | shipped — "
    "**THE CARD'S PROPOSAL (1) ALONE IS A NO-OP FOR COMPOSITION on this record: the binding constraint is one wall UPSTREAM of the date filter.** "
    "Hour 11 at wakeup = build tick; no LANE-HALT; archive pre-step ran (snap_20261125_115240 diary=50 day_log=100 hoard=286 mood=happy:low intent=to_fence). "
    "L294 NOT taken: tick 285's claim (10:50) was 62 min old = fresh under the 2 h rule; that tick died on HTTP 429 after writing claim_t285.txt + survey2.py only (honored as written; stale at 12:50). "
    "ONE RECORD PER STORED TYPE before any loop (lane/t286/survey.out): manifest row, snap keys, day_log record {ev,t,dan,kc,dop,sal}, diary entry; AST constants KIND_EVENTS/TOP_FRAC .10/MAX_REPLAYS 5. "
    "STRUCTURE (AST + serve.py read, observed before the PREREG, description): `_log_event` has two callers -- `_dabble` in world_tick (literal \"water\") and `_reply_inside` (visitor turn); "
    "`consolidate_night` has ONE caller, world_tick L407 on session_for(\"world\") (serve.py L210-211) while reply runs on session_for(chat) (L350-353). "
    "PREREG lane/l295/PREREG.md frozen BEFORE the visitor-session scan (sha256 bound into results_l295.json); measure_l295.py ran through its last write, exit 0, read-only on sessions/ and lane/archive/. "
    "S1 TRUE (census on the unobserved population, as predicted): 621 visitor sessions, 465 day_log records, 338 KIND non-water (greet 207 / peas 93 / tin 13 / goats 12 / shiny 12 / pet 1) + 48 non-kind (swat/rake/hold/umbrella, 12 each) -- "
    "**333 of the 338 are the lane's OWN gate harness (`gate<ts>-fresh-N` ids: 11-09 140, 11-10 56, 11-16 109, 11-25 28 at 03:37); 5 are non-gate ids, all on 11-09/11-10.** "
    "S2 (description): world log 8,780 records = 100% water, 0 non-kind, 51/132 snaps at the 100 cap; 10 archived passes (11-16 18:47 dusk, then 00:01-00:08 nightly; service clock = America/New_York). "
    "Watermark kept set RECONSTRUCTED 10/10 nights, all water, chosen n 4-5 all water, +1,572 entries over the date rule across the 9 midnight nights. "
    "DATE rule kept set reconstructed on 1/10 only (the dusk pass: 95 -> 5 water): at a midnight pass its input is a 2-9 MINUTE post-midnight sliver that no snapshot lands in (unarchived tail 22-177 min) -> EMPTY on 9/9 while the diary reads \"-- water\" "
    "(L293's step-size inference stands; not recountable here). LOSSY (a snap at cap in-window) 8/9 midnight nights -> every union is a LOWER BOUND. "
    "S3: 0 non-kind in the world log -> the L73 hazard is UNREACHABLE in the live pass; reachable only under a cross-session union (night 0 exposes 16), which must first say WHICH delta a replay writes -- the delta is per session. "
    "CONSEQUENCE: the date filter is redundant for its job (night_stamp already blocks same-day passes); owner menu = (1) watermark only (no effect) / (1') cross-session union + watermark (admits the 338, 98.5% test harness; needs the per-delta design) / (2) a bound only. None taken; no live rule changes. "
    "VERIFIED: results_l295.json 119,758 B with prereg_sha256; followup.out re-derived the sliver per night from the stored pass clocks; LANE.md card amended in place -- "
    "BUILD: two fuzzy-patch slips on the LANE.md anchor (a RETYPED anchor replaced the tick-284 tail line, then the repair padded the line above with stray spaces) -> exact byte-level replace with once-only guards (lane/t286/fix_card.py), region re-read: tick-284 tail byte-restored, tick-286 note x1, 73 unchecked, L295 open, ideas 134 header intact, 12,135 lines. "
    "Fly duck active, same PID 2706698, NRestarts 0, /needs 200. Box stays OPEN (proposal 2 + live rule = owner). Next: L294 (its claim is stale from 12:50)."
)
open(LOG, "a", encoding="utf-8").write(line)
after = open(LOG, encoding="utf-8").read()
print("appended; 'tick 286 |' occurs", after.count("tick 286 |"), "x; log lines", after.count("\n"))
