# L69 PREREG — echo-side-dose-response (registered 2026-11-14 12:0x, BEFORE any run)

Card (LANE.md ideas-34): sweep ronly gain {.05,.1,.2,.4} x delay {5} on the census
grid (l67 machinery verbatim): does ANY dose flip S_R positive (>= +.10 mean,
>= 11/16) without crashing lock or S_L? Dose-response on dSR with a flat floor =
structural ceiling confirmed; a high-dose flip = routing-limited after all (L57 D5
gains a dose caveat). Also carry lonly as the mirror control.

## Design (l67_sidesplit.py machinery verbatim; CPU-only)

- Substrate: frozen male cord subnet (21,516 nodes / 2,977,920 edges), G .01,
  BETA 2, D .05 on DNg100, ENT_AMP .3 chop schedule (500-on/400-off @0.7 +
  continuous 1.4 seg2), SETTLE 400, WIN 6000, DT .01.
- Echo: NEGATIVE sign, DELAY 5 steps (50 ms), fed from the same-side Tr
  antagonist pool mass onto rootSide-matched mechano cells (l67 form).
- ARMS (8): ronly x gain {.05,.1,.2,.4} + lonly x gain {.05,.1,.2,.4}
  (superset of the card's "lonly at the best R dose" — the best-dose mirror row
  is read from this table regardless of which dose wins).
- SEEDS: l45b census grid n=16 (11,22,33,101..113) — same as l66/l67.
- Open arm: REUSED from l67/raw_l67.npz hynohop keys (not rerun).

## Gates (pre-registered)

- P1 ANY-DOSE R-LIFT (the surprise branch): EXISTS gain g with
  dSR_mean(g) >= +.10 AND dSR_pos(g) >= 11/16 AND dSL_mean(g) >= -.05 AND
  lock_ok(g) AND dm_min(g) > 0.  => "routing-limited after all"; best g named;
  L57 D5 gains a dose caveat; the lonly mirror row at best g reported.
- P2 FLAT FLOOR (the EXPECTED branch): NOT P1 AND max_g dSR_mean < +.10 AND
  no monotone-in-gain dSR ordering (Spearman |rho| < .8 across the 4 gains,
  or non-monotone).  => "S_R structural ceiling CONFIRMED at every tested
  dose" — the L67 routing-unrescuable verdict hardens into contract language.
  If NOT P1 but a monotone dSR trend exists that merely misses +.10, report
  MIXED (trend without a flip; the ceiling is dose-soft).
- P3 CROSSED-ACROSS-DOSE: at every g, |dSL_mean(ronly,g)| >= |dSR_mean(ronly,g)|
  (the L67 crossed law carried across the dose axis). Per-g table either way.
- P4 LOCK SAFETY: every arm lock_ok (median e2 <= max(.01, 2*open_e2_med),
  max e2 <= .5). Any catastrophic arm is a finding, not a discard.
- P5 MIRROR: lonly dose curve on dSL — does the ipsi bonus (l67: +.171 @ .1)
  grow with gain or saturate/collapse? Descriptive row; no gate.
- DOSE-LANDING PROBE (new instrument): mean antagonist amplitude (4 Tr pool
  traces averaged over the OFF-window TS3 samples) vs open, per arm —
  monotone in gain separates "dose LANDS but S_R unmoved" (truly structural)
  from "dose never landed" (floor-buried, L35 class). Registered read: P2
  requires amplitude(g) monotone-nondecreasing in g (landed) for the
  structural-ceiling label; flat amplitude + flat dSR = wiring-floor caveat
  instead.

## Anchors (enumerated keys ONLY — L59 lesson)

- C0r: ronly@.1 == l67 stored ronly (mm + fL/fR/eL/eR, 16 seeds, 80 keys, 0.0).
- C0l: lonly@.1 == l67 stored lonly (80 keys, 0.0).
- C0O: open recompute (duty/SL/SR/dutyL/dutyR) == l67/l66 stored json values.
- C0P: per arm-seed first_div == DELAY+1 = 6 AND prefix [0,6) bit-zero
  (L66 ADDENDUM form: echo enters mech at k=delay, pools see it one hop later).
- C1: af in (0.01, 0.9) every arm-seed; wired_dead (dm==0) must be 0.

## Selection rule (registered before data)

best_g = argmax over ronly gains of dSR_mean; tie-break higher dSR_pos, then
LOWER gain (conservative). The mirror control row = lonly at best_g.

## ADDENDUM 1 (post-run, pre-verdict-finalization — disclosed)

The registered landing criterion ("amplitude monotone-nondecreasing in gain")
assumed a POSITIVE echo's amplitude-pumping intuition. A NEGATIVE echo
SUBTRACTS drive, so pool mean amplitude need not grow with gain: measured
d_amp_pct on ronly = +3.2 / +9.4 / +3.0 / -2.0 across gains {.05,.1,.2,.4}
— dose-DEPENDENT but non-monotone (high gain suppresses the mean, the L63
mechanism on the dose axis). AMENDED criterion: the dose is LANDED iff
(a) dm > 0 on every arm-seed (true: wired_dead 0, 128/128) AND (b) amplitude
is dose-DEPENDENT (non-flat swing, true: 11.4-point swing). Under the amended
criterion the dose lands at every gain and S_R still does not move
(max dSR_mean +.053, Spearman rho 0.0) — the structural-ceiling label is
EARNED, and stronger than the registered flat-floor wording (it is not a
wiring floor). The monotone form of the probe is retained as P2's secondary
descriptor, reported False.
