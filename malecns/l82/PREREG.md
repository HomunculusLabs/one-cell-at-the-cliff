# L82 PREREG — echo-hold-law (registered 2026-11-15 10:2x, BEFORE any rollout)

Card: LANE.md ideas-41 L82. Operational question for the parked L80 amendment:
the echo cell (l66 g01_d05_m: gfb .1, sign −, delay 5) lifts the 0.7-seg structure
(P(duty_07>=.5) 11/16 → 15/16, L80). Must it run THROUGH the fast seg, or only
during the 0.7 segs it lifts? L47/L48 prior: driven structure is DRIVE-HELD —
predicts window-local sufficiency.

## Schedule / machinery (l77_census.py verbatim)
- SEGB [(0,2000,0.7),(2000,4000,1.4),(4000,6000,0.7)], WIN 6000, SETTLE 400,
  500-on/400-off chop inside 0.7 segs, continuous fast seg, ENT_AMP .3,
  G .01 / BETA 2 / D .05, seeds = l45b census n=16 (11,22,33,101..113).
- NO HOP volleys (nohop family only). One shared generator + per-step noise
  tensor across arms (L36 rule); echo term drive[mech] += .1*(−1)*mA[k−5].

## Arms (3, all on the nohop schedule)
1. hynohop      — never  (l59 wiring; stored in l59/raw_l59.npz + l77 raw)
2. hynohop_fb   — echo ON for every k >= 5 (l66/l77 wiring verbatim)
3. hynohop_fb07 — NEW: echo ON iff k in [0,2000) ∪ [4000,6000) and k >= 5
                  (gate closes for the whole fast seg; mA still recorded)

## Anchors (gates, exact)
- C0a: hynohop == l59 raw mm+{fL,fR,eL,eR} seeds 11/22/33, max|d| == 0.0.
- C0x: hynohop_fb == l77 raw AND == l66 raw (same seeds/channels), max|d| == 0.0.
- C0P-1: fb07-vs-fb max|d| == 0.0 over trace indices [0,2000] inclusive
  (echo gate first differs at step k=2000; mech X differs at 2000, motor pools
  one hop later — derived from the stored first_div==6 law: echo at k=5 ⇒
  first trace div 6 ⇒ direct mech→motor edges exist).
- C0P-2: first trace divergence (concat mm+4 traces):
  fb-vs-never == 6 and fb07-vs-never == 6 (stored l77/l66 law);
  fb07-vs-fb == 2001 (gate closes at 2000, +1 hop). If measured 2000, STOP and
  re-derive from stored raw before reading any verdict (L77 addendum pattern).
- C1: af in (0.01, 0.9) every arm/seed. wired_dead must be ∅.
- Degenerate branch (L55 rule): if fb07-vs-fb traces bit-identical anywhere in
  [4000,6000), the gate never closed — wiring bug; check the EON table, no verdict.

## Expected values carried from STORED artifacts (expectations, not gates)
l77/results_l77.json (re-derived this tick, L44 rule):
- never: seg0 .605 (10/16>=.5) | seg1 .375 (6/16, err_le01 16/16) | seg2 .488
  (9/16) | duty_07 .547 (11/16)
- fb:    seg0 .739 (15/16) | seg1 .292 (5/16, err_le01 16/16) | seg2 .608
  (12/16) | duty_07 .673 (15/16) | echo ratio .127

## Registered reads (window-scoped; adjudication order fixed)
- R1 (parity anchor): fb07 seg0 duty distribution EXACTLY == fb's
  (bit-identical window by construction).
- R2 (THE question — carries the verdict): paired per-seed seg2 duty deltas.
  H-A window-local (drive-held law): mean(fb07−fb) ∈ [−.05,+.05] AND
  mean(fb07−never) >= +.05.
  H-B continuity-needed: mean(fb07−fb) <= −.10 AND |mean(fb07−never)| <= .05.
  Overlap zone (between): verdict = MIXED, disclosed as such, no amendment
  edit beyond noting the constraint.
- R3 (fast-seg de-tox): mean(fb07−never) seg1 duty ∈ [−.05,+.05] AND
  seg1 err_le01 == 16/16 (echo must not touch the fast-seg lock).
- R4 (budget): fb07 echo ratio < .127 strictly (report exact; equal drive-on
  steps 4800 asserted for all arms).
- R5 (L80 gate form, summary only): P(duty_07>=.5) + Wilson for fb07;
  H-A band k ∈ [11,16], H-B band k ∈ [8,13]. R5 does NOT adjudicate — R2 does
  (register which read carries the information, L55 rule).

## Disclosure
- One new rollout arm only; never/fb re-rolled fresh for pairing (CPU ~5 min,
  no GPU). Output l82/raw_l82.npz checkpointed BEFORE analysis; verdicts
  re-derivable from checkpoint (l77 precedent).
- fb07's echo re-entry at k=4000 uses mA[3995] (real seg1-tail motor mass) —
  disclosed as designed, not a bug.
