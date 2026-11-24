# Cross-arch twin check: l217 on the Mac Studio (arm64) — FAILED (expected gate)

Date: 2026-11-23 ~03:04-03:06 EST. Owner-approved offload trial (Bill, #miso
game-harness-lane thread), gate defined in skill peabrain-flybrain
`references/compute-offload.md` before any Mac result becomes canonical.

## Method

- Full banc lineage rsynced om → homelab (t3rpz@192.168.50.86, Mac Studio,
  Darwin arm64, 24c/192G; env `~/critters/peabrain/.venv-mac` =
  python3.14.6 / numpy 2.5.5 / pandas 3.1.1 / torch 2.15.0 arm64 CPU).
- Identical `l217_static.py` executed in the synced copy (same inputs; om's
  official run had already completed 03:03 EXIT=0, 820s,
  static.json md5 7a40a2453c319239730d2a917050be04 — untouched throughout).

## Result

Died ~2 min in at an INHERITED cert pin (traceback: run.mac-arm64.err):

    AssertionError: ('Ti', 'base_closure', 'null_A_cell_mean',
      0.0013305471397729528   # recomputed on arm64
      0.0013305471397729565   # stored (x86 lineage value)
      'CERT-205')

abs diff 3.7e-18, rel ~2.8e-15 — last-ulp float-reduction drift between
x86 (om, torch cu13x lineage) and arm64 (Mac). The pin fired LOUDLY: no
silent currency mixing, no artifact written. The gate works.

## Verdict (now lane law)

- banc `l*_static.py` and anything carrying inherited EXACT pins CANNOT run
  on the Mac. Not fixable by tolerance — the discipline is EXACT by design.
- Statics stay on om, launched pre-niced:
  `nice -n 15 timeout 1700 ~/critters/peabrain/.venv/bin/python lNNN_static.py`
  (nice is inherited by the python child; renice-after only mid-flight).
- Mac Studio remains valid for PIN-FREE compute: builds/compiles, MLX/llama
  inference, TTS (already serving), fresh Mac-native lineages that start and
  stay on one host. Env verified ready (see compute-offload.md).
