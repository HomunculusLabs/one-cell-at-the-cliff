# L295 PREREG — slice 1: WHICH EVENTS EACH SELECTION RULE WOULD HAVE CHOSEN
## frozen before the visitor-session scan and before any per-night rule reconstruction ran
## (tick 286, Miso; file written 2026-11-25 ~12:07 EST; lane/t286/prereg_l295.py stamps the exact second)

Question (card, ORDER first half): on the STORED day_logs, which events would each
selection rule have chosen at the hour the pass runs — and does the card's proposal (1)
(a watermark instead of the calendar date) admit anything the live rule drops?

## Inputs (all read-only; sessions/ and lane/archive/ are never written)
- lane/archive/snap_*.json (132, 2026-11-16 05:56 -> 11-25 11:52) + manifest.jsonl = the WORLD
  session only (L98 archive design), each snap carrying its day_log at capture time (capped 100).
- sessions/*.json other than world = VISITOR sessions, json.load only.
- constants parsed from bridge.py by AST (KIND_EVENTS, TOP_FRAC, MAX_REPLAYS); the n rule is
  re-executed as the source expression `int(len(ranked) * TOP_FRAC + 0.999)`, max(1, min(MAX_REPLAYS, .)).

## Already observed BEFORE this registration (description only; nothing below branches on it)
- Call graph (AST, lane/t286/survey.out): `_log_event` has two callers — `_dabble` (inside
  world_tick, literal "water") and `_reply_inside` (visitor turn, `event`); `consolidate_night`
  has ONE caller, world_tick L407. serve.py: world_tick runs on session_for("world") (L210-211);
  reply runs on session_for(chat) (L350-353).
- Archive census: 8,780 day_log records over 132 snaps, every one `ev == "water"`.
- From L293 (tick 282): the pass stamps at 00:08-01:00 local; the day_log at pass time is NOT archived.

## Rules (both evaluated on the WORLD log as reconstructed from the archive)
- R_DATE (live, bridge.py L286-297): at pass time t_k keep entries whose LOCAL date == date(t_k);
  rank by `dop` desc; n per the source expression.
- R_WM (card proposal 1): at t_k keep entries with t in (t_{k-1}, t_k] (since the previous pass);
  same rank, same n. Previous pass t_{k-1} from the diary's `consolidate` entries (deduped by clock_s).
- Reconstruction = UNION of day_log records across snapshots captured in (t_{k-1}, t_k], keyed (ev, t).
  Entries evicted by the 100-cap between two consecutive snapshots are unrecoverable; a window in
  which any snapshot's log is at len 100 is flagged LOSSY and the union is a LOWER BOUND.

## Registered
- S1 VISITOR_LOGS (census on an UNOBSERVED population; TRUE/FALSE, no p — a count):
  across visitor sessions, at least one stored day_log record has ev in KIND_EVENTS and ev != "water".
  Prediction: TRUE. If TRUE the kindness is on disk, in a session no pass reads (wall 1 = session scope).
  If FALSE the loss is upstream of `_log_event` and wall 1 is moot — read serve.py L340-355 next.
- S2 PER-NIGHT COMPOSITION (DESCRIPTION — observed-derivable, no null, no branch; the structural
  prediction is stated so a miss is visible): for every archived pass, the EVENT COMPOSITION of
  R_DATE_chosen and R_WM_chosen. Predicted: both 100% water on every night, because the world log is
  single-type by call graph. Reported beside it: |R_WM kept| vs |R_DATE kept| per night (how many more
  entries the watermark admits), KIND count in each chosen set, LOSSY flag.
- S3 L73 REACHABILITY (DESCRIPTION): a `dop` key can select a non-KIND event only if one is IN the log.
  Count non-KIND records in (a) every world snapshot log, (b) every visitor log, (c) what a
  cross-session union would have exposed per night. Not a proposal: the plasticity delta is
  PER SESSION (bridge: one delta vector per visitor, never the shared W), so a union rule must
  first say WHICH delta a replay writes — an owner design question, not this tick's.

## Consequence clause (written first)
If S1 is TRUE and S2 is both-water on every night: proposal (1) ALONE changes what the pass
replays by NOTHING on this record — the binding constraint is session scope, not the calendar
date. The owner's menu is then (1) watermark only (no measurable effect), (1') a cross-session
union + watermark (admits visitor kindness; needs the per-visitor-delta design above), or
(2) a bound only (the L295 owner question). This tick takes none of them; no live rule changes.

## Status vocabulary
S1 TRUE / FALSE (+ n visitor sessions, n records, event census)
S2 N nights; composition per rule per night; WATER_ONLY n/N; LOSSY n/N
S3 non-KIND counts (a) (b) (c)
