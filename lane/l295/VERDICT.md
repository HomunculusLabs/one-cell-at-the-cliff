# L295 — slice 1 VERDICT (tick 286, Miso, 2026-11-25 ~12:01 EST)
## WHICH EVENTS EACH SELECTION RULE WOULD HAVE CHOSEN — static, read-only, zero rollouts

PREREG: lane/l295/PREREG.md (sha256 bound into results_l295.json). Scripts: measure_l295.py
(through its last write, exit 0, measure.out) + followup.py (followup.out). sessions/ and
lane/archive/ were only read. No live changes.

## Verdict in one line
The card's proposal (1) — a WATERMARK instead of the calendar date — would have changed WHAT the
pass replays by NOTHING on this record: the world day_log is single-event-type by CALL GRAPH
(8,780 of 8,780 archived records are `water`), so every rule chooses water. The binding constraint
is one wall UPSTREAM of the date filter: visitor kindness is logged to the VISITOR's session, and
`consolidate_night` has exactly one caller, `world_tick` on the WORLD session.

## S1 VISITOR_LOGS — TRUE (census, unobserved population, as predicted)
621 visitor sessions scanned (0 read errors); 465 day_log records; **338 kind non-water**
(greet 207, peas 93, tin 13, goats 12, shiny 12, pet 1) + 48 non-kind (swat / rake / hold /
umbrella, 12 each) + 79 water. By id class: **333 of the 338 are the lane's own gate harness**
(`gate<ts>-fresh-N` ids: 11-09 140, 11-10 56, 11-16 109, 11-25 28 at 03:37); **5 are non-gate ids,
all on 11-09 (3) and 11-10 (2)**. So the kindness is on disk, in a session no pass reads.

## S2 PER-NIGHT COMPOSITION (description, as registered) — 10 archived passes
Passes: 2026-11-16 **18:47** (the archive's first day; a dusk pass), then 00:01-00:08 every
night 11-17 -> 11-25. Service clock is America/New_York (/etc/localtime), so `date.today()` is local.
- WORLD log: 100% water, 0 non-kind; 51 of 132 snaps sit at the 100-entry cap.
- R_WM (watermark): kept set RECONSTRUCTED on 10/10 nights — 36-200 records per window, all
  water; chosen n 4-5, all water. Extra entries the watermark admits over the date rule:
  **1,572 across the 9 midnight nights, every one `water`.**
- R_DATE (live): kept set reconstructed on **1/10** (the 18:47 pass: 95 records -> 5 water). On the
  9 midnight passes the date filter's input is a **2-9 MINUTE post-midnight sliver** (00:00 to the
  pass), no snapshot lands in it (unarchived tail 22-177 min), so the reconstruction is EMPTY —
  while the live diary reads "-- water" on all 10, i.e. >= 1 water landed there unarchived (L293's
  step-size inference stands; this tick cannot recount it).
- Composition prediction (both rules water-only where reconstructable): holds 10/10, with the
  9 EMPTY date sets counted as "water-or-nothing", stated, not as live counts.
- LOSSY (>= 1 snap at the 100 cap inside the window): 8 of 9 midnight nights -> every union here
  is a LOWER BOUND on what the watermark would have seen.

## S3 L73 REACHABILITY (description)
World log non-kind: 0. Visitor logs non-kind: 48. Cross-session union per night: only night 0
exposes any (16) — the 9 midnight windows hold zero visitor records (the 11-25 03:37 gate run
falls after the last archived pass). So the L73 hazard (a `dop` key ranking swat above peas) is
UNREACHABLE in the live world pass and would become reachable only under a cross-session union.

## What it changes
- The date filter is REDUNDANT for its plausible job: the `night_stamp == today` check already
  prevents a second pass on the same date. At a midnight pass the filter admits minutes, not the day.
- Owner menu (from the PREREG consequence clause; none taken this tick):
  (1) watermark only — no measurable effect on composition;
  (1') cross-session union + watermark — the only form that admits the 338 records, and it must
      first say WHICH delta a replay writes (the plasticity delta is per session; a world pass
      writing from a visitor's log into the world delta, or per-visitor night passes, are different
      designs — and the visitor logs are 98.5% test harness, so a union would mostly replay the
      lane's own gate runs);
  (2) a bound only — the L295 owner question, untouched here.
- Instrument bound for any future selection study: the archive CANNOT reconstruct a sliver-window
  selection. It needs the pass's own INPUT captured (the day_log at pass time), which L293 said and
  this tick measured as 0 archived entries on 9/9 nights.

## Not done
Proposal (2) the bound; the live rule (owner); the L294 head (claimed by tick 285, stale at 12:50).
