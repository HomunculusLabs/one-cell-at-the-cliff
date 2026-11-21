# L48 PREREG — repair-release-shaping (written BEFORE any run)

Question: L47 showed the 20-s re-entrain restart is DRIVE-HELD (S_R -.49 ->
+.68..+.78 during the drive) and its HARD-OFF release persists nothing (post
duty(both>=.25) = 0.000, 9/9 cells; release re-runs the L39/L41 attractor
lottery: 2/3 seeds hop to f 1.51/1.63 both-sides-negative, core .246->.196).
Does a GRADED release (entrain amp ramped 0.3 -> 0 over 10/30/60 s) or a
LONGER full-amp dwell (60/120 s then hard-off) carry the during-drive
bilateral structure across the release into a SELECTED bilateral attractor?

## Arms (all share the l47 prefix: ent 0.7 Hz amp .3 [0,4000) + stop DNg88 -8
## [4000,6000); seeds 11/22/33; substrate l32-frozen, asserted 21,516 /
## 2,977,920; one generator, one shared per-step noise tensor)

- norepair — no drive after 6000 (l46 h40 / l47 norepair; ANCHOR, full
  [0,18000) bit-identity to l47/traces_l47.npz; window extended to 24000 =
  new data: does SL+|SR- EVER self-repair by 220 s post-stop?)
- rep0 — ent [6000,8000), hard-off at 8000 (ANCHOR, full [0,18000)
  bit-identity to l47 rep0)
- ramp10 / ramp30 / ramp60 — ent full amp [6000,8000), then LINEAR amp
  ramp 0.3 -> 0 over [8000,9000) / [8000,11000) / [8000,14000)
- dwell60 / dwell120 — ent full amp [6000,12000) / [6000,18000), hard-off

WIN = 24000 steps (240 s; global 0.7 Hz phase accumulator runs throughout,
l47-verbatim). Release-off step OFF = {rep0 8000, ramp10 9000, ramp30 11000,
ramp60 14000, dwell60 12000, dwell120 18000}.

## Windows & metrics (all pre-declared)

- DUR = [6000,8000) full-amp phase (identical drive in every treatment arm):
  SL_dur/SR_dur medians — premise check vs l47 rep0 (SR_dur +.68..+.78).
- RAMP = [8000, 8000+ramp_len): SL/SR medians DURING the fade (is structure
  lost early or only at low amp?).
- POST = [OFF, OFF+6000) (60 s, same length every arm): SL/SR/SP medians,
  duty_both = frac of TS steps with SL>=.25 AND SR>=.25, f_post (rhythm2 on
  mm), core_post (mean xc), lat_both_s (first both>=.25 after OFF).
  norepair comparison window = [18000,24000) (its "late" extension).
- f_dur on mm DUR; hop_at_release = f_post - f_dur.
- State naming (L45b census axes): f-band (<=1.0 "0.7-band", 1.0-1.8
  "1.4-band", >1.8 "fast") x (SL sign, SR sign).

## Gates (pre-registered)

- C0 anchors: norepair AND rep0 mm bit-identical to l47 stored traces over
  [0,18000) (max|d| == 0.0); every treatment arm bit-identical to norepair
  over [0,6000) AND to rep0 over [0,8000) (shared-prefix construction, no
  arm leakage). af in (0.01,0.9) every arm/seed.
- C1 drive lands: dm = max|mm(arm)-mm(norepair)| over DUR > 0 every
  treatment arm/seed; x88min < .5 during stop (un-pins, l47-verbatim).
- C2 REPAIR-FOUND (per arm): 3/3 seeds with duty_both(POST) >= .5 AND
  SL_med(POST) >= .25 AND SR_med(POST) >= .25. PARTIAL-POOLED if not but
  3/3 seeds SP_med(POST) >= .25. Else NOT-REPAIRED.
- C3 state selected: f_post vs the 0.7 memory (norepair anchor f_late
  ~.72), core_post vs core_dur; a repair landing in a NEW bilateral state
  is fine — NAME it (band x side signs).
- C4 latency + hop: lat_both_s from OFF; hop_at_release, with f_dur
  anchored (~.70 expected, locked drive).

## Honesty notes

- n=3 seeds; ramp/dwell conclusions at seed-consistency level, same as the
  L44-L47 chain. Spontaneous-repair floor: l46/l47 measured duty 0.000 out
  to 120 s on this exact state — norepair's [18000,24000) extension IS the
  floor probe here (no separate paired counterfactual exists for a
  drive-history-bearing arm; disclosed).
- L45b census: free-cord bilateral S_R+ states exist during entrainment
  only; if a ramp arm "repairs", C3 must say whether the state is in the
  census or new (rep0's hop state was NOT in the census).
- Deviations: journal in this file as addenda, never silent.
