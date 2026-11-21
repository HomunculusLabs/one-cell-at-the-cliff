# L81 PREREG — reflex-arc re-host (registered BEFORE any rollout, 2026-11-15 08:5x)

Card: LANE.md ideas-40 L81. The remaining L52 shape with a measured prior:
after the frequency step, instead of a gap (L79, HURT), a brief STRONG
sinusoidal mechano volley at the 1.4 carrier through the reflex arc
(L34's re-hosting regime), then back to continuous .3.

## Design (l79 machinery verbatim; the volley replaces the gap)

- Substrate/loop: l79_reprime.py verbatim (l32 arm-A frozen G .01 / BETA 2 /
  D .05, 21,516 nodes / 2,977,920 edges asserted, settle 400 @0.7, WIN 6000,
  SEGB 0.7|1.4|0.7, census SEEDS n=16, one generator + shared per-step noise
  tensor across arms, CPU-only).
- Volley window VOL = [2500, 2800) (3 s, inside L79's straddle window, starts
  exactly at the L79 gap start). During VOL the mechano drive amp is
  ENT_AMP*{2,3} = {.6,.9} riding the SAME 1.4-carrier phase (drive formula
  unchanged — amp*(0.5+0.5 sin PHI[k])); outside VOL the table is the twin's
  verbatim (continuous .3 in the fast seg). No off-steps anywhere: drive-on
  stays 4800 for every arm.
- ARMS: hynohop, hybrid (twins, l59 anchors), rehost2x, rehost3x (twin
  hynohop), hyrehost2x, hyrehost3x (twin hybrid; same hop volleys at
  TRANS as hybrid).
- AMP {1x} arm: registered as the NO-OP PARITY CONTROL, proven by TABLE
  ASSERT only (AMPA[1x] == twin elementwise by construction), NOT rolled
  out — a 1x "volley" at continuous-.3 baseline is the same waveform the
  baseline already plays (degenerate branch registered per L55: it can
  carry no information and must not be counted as an arm).
- Amp disclosure (card): {1x, 2x, 3x} free-parameter sweep; 1x = parity
  control, 2x/3x are the treatment arms.

## Anchors (forms diffed against STORED values, L44/L77 rule)

- C0a/C0b: hynohop/hybrid == l59/raw_l59.npz BIT-IDENTICAL (mm + fL/fR/eL/eR,
  seeds 11/22/33, max|d| == 0.0) — 26th consecutive chain anchor.
- C0P-1: prefix [0, 2500) max|d| == 0.0 for every volley arm vs its twin,
  every seed (mm + 4 traces).
- C0P-2: first float32-visible divergence == 2501 for every volley arm-seed
  (l79 STORED: {2501: 32/32} for the -0.3-class delta at k=2500; the law is
  drive-enters-mech-at-k, pools one hop later). ADDENDUM branch pre-registered:
  if the 3x delta (+0.6-class) becomes float32-visible at k=2500 the FORM
  (entry 2500, visibility 2500|2501) governs — amend with measured counts,
  never post-hoc per-seed.
- C1: settled active fraction 0.01 < af < 0.9 every arm/seed.
- wired_dead: dm == 0.0 in any volley arm-seed = wiring bug (positive amp
  onto mech cannot be absorbed; L39/L43 class), verdicts void.

## Registered reads (windows verbatim from l79)

- W_EARLY (2500,3200) EXPOSURE (contains the volley), W_POST (3200,4000)
  PRIMARY (fully inside resumed continuous .3), W_POST_LATE (3600,4000).
- P1 per family x dose (2x,3x): paired d_post/d_early/d_late vs twin
  (per-seed, same noise stream), mean, n_up, k(duty_wpost >= .25) per arm,
  Wilson n=16. Verdict: HELP if d_post_mean >= +.10 and n_up >= 11;
  HURT if <= -.10 and n_down >= 11; else NULL/INCONCLUSIVE (l79 thresholds).
- P1b dose ordering (descriptive): d_post(3x) - d_post(2x) per family —
  monotone help, monotone hurt, or non-monotone/lottery.
- P2 lock: lock_post (blocks 3000/3500 vs 1.4, mean |err|, count <= .01) +
  lock_straddle ([2500,3000) vs 1.4) per arm. The volley may tax the
  straddle window; the razor read is lock_post.
- P4 miss decomposition for volley arms: misses SL-owned / SR-owned / both
  (duty_wpost < .25), l79 form.
- P5 budget: entrain mass ratio per arm vs baseline (amp-weighted; drive-on
  steps equal by design), reported with the triple, never summed.
- Expectations registered BEFORE data: L34 prior says strong sinusoidal
  drive re-hosts antiphase (help), L63/L79 toxicity family says extra
  perturbation energy at a transition can hurt. Primary honest outcome is
  whatever d_post says at the l79 thresholds; NO direction is assumed.
  Secondary prediction (discriminating): if re-hosting is real it must show
  in d_post >= d_early ordering (structure persists past the volley), while
  a perturbation-only effect decays (|d_late| < |d_early|).

## Honesty clauses

- Window-scoped distributional reads only; pooled duty_all demoted to
  diagnostic (L80). Lock + budget reported alongside (the triple).
- CPU-only; raw npz checkpointed BEFORE analysis; sessions/ untouched; no
  live changes; analysis crash => re-derive from raw npz, zero reruns.
