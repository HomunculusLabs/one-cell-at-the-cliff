# Pinned delta L100 — diary night vision (bridge.py)

- **Status:** SHIPPED LIVE 2026-11-16 14:2x-14:4x EST (fly duck :3122) and
  recorded here as the pinned delta for the hardened Duckagotchi backend.
- **Provenance:** owner call 2026-11-16 ~11:40 EST, verbatim "yay, B, yay!"
  (third item of a three-item summary, one hop Bill -> Miso, Discord),
  recorded BBS bill/agent-bbs#54 comment `miso:owner-calls-1116:v1`.
  LANE.md card L100 carries the same decision.
- **What:** instrumentation only, zero behavior change. (1) every diary
  entry stamped `clock_s`/`clock_s_end` (int epoch s) + `n` run counter;
  (2) identical consecutive (act,text) within 900 s coalesce into one
  counted entry (a night of 45-s naps filled the 50-cap with identical
  lines in ~37 min); (3) entries evicted by the 50-cap append to
  `sessions/world_diary_archive.jsonl` before dropping (append-only).
  Old-format entries never coalesce (no start clock to window against).
- **No-behavior-change proof:** 40-tick seeded world_tick baseline pre vs
  post refactor — acts/hoard/curiosity/entry-counts/texts bit-identical;
  the `t` tie-break draws use the unseeded global stream (pre-existing
  entropy; same-code control runs also differ there, draw COUNT identical).
- **Tests:** `test_l100.py` 17/17 (stamps, coalesce+window, ordered
  append-only archive, json round-trip, unwritable-archive resilience,
  distinct-dream non-merge, old-tail non-merge).
- **Deploy evidence:** `systemctl --user restart-path` clean (kill literal
  PID + start), `/health` 200, `gate_live.py` 25/25, `/diary` serving
  stamped entries (14:24-14:26 EST wall-clock reads), archive file
  receiving evicted entries live.
- **Contents:** `bridge_l100.diff` (pre image: lane/l100/bridge_pre.py),
  `test_l100.py` (offline gate), this README.
- **Follow-up:** L99 deep-hunger wake (same owner call, option b) is a
  separate delta; its diary entries inherit stamps from this one.
