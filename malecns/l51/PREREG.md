# L51 PREREG — structure-aware-hybrid-schedule (written BEFORE any run)

Task (LANE.md ideas-25, verbatim intent): L50's table implies CONTINUOUS drive
in tracking-critical segments (the fast 1.4), DUTY-CYCLED 5-on/4-off where
structure matters (the 0.7 segments). Run the hybrid on the same task and
score the triple: does it hold allw-level tracking (seg1 err <= .01) at
duty58-level structure (duty >= .5)? If yes, the endgame controller spec is
complete; if no, the conflict is irreducible at amp .3 and the honest
controller carries both numbers separately.

P1-labeled descriptive lab demo. CPU-only. No live changes. Owner movement
law respected (lab evidence, never app motion).

## Machinery (l50-verbatim, nothing re-tuned)

- Substrate: MaleCNS cord 21,516 nodes / 2,977,920 edges, frozen l32 arm-A
  (g .01, beta 2, D .05 on DNg100), tau .05, DT 10 ms, RMAX 1, BG .02,
  NOISE .01, SETTLE 400 @0.7, WIN 6000, SEGB = [(0,2000,.7),(2000,4000,1.4),
  (4000,6000,.7)], ENT_AMP .3, hop DNge046_L amp .5 steps [2000,2040) and
  [4000,4040), LOCK_TOL .10, seeds {11,22,33}.
- ONE generator per seed, X0 first, ONE shared per-step noise tensor across
  arms (l39/l50 convention — anchors depend on it).
- Per-arm AMPA/HOPA tables computed BEFORE the run, with write-time asserts;
  no inline conditionals in the step loop (L39v1/L43v1/L48 lessons).

## Arms (4) x seeds {11,22,33}

- allw   : amp .3 all steps + hops both transitions. = l50 allw. [chain anchor]
- duty58 : per-seg 500-on/400-off + hops both transitions. = l50 duty58.
- hybrid : duty58's EXACT table on seg0 and seg2 (on at segment starts,
           clipped at segment end), amp .3 CONTINUOUS on seg1 [2000,4000),
           + hops at both transitions. Drive-on = 400 + 1200 + 2000 + 1200
           = 4800 steps = 48.0 s (44 s of the 60-s task; the queue's
           "~44 s of 64").
- hynohop: AMPA identical to hybrid, NO hops — the hop-wiring reference and
           a bonus datum (does a chopped-entry continuous 1.4 lock without
           the hop? l39's continuous-entry ent did not: err .21-.29).

## Anchors (C0/C1) — all must be exact, no tolerance

- C0a: hybrid bit-identical to duty58 over [0,2500) (settle + seg0 + seg1's
  first on-window): max|d mm| == 0.0, 3/3 seeds. (Identical AMPA+HOPA there
  by construction — the LANE sketch's "prefix = allw through seg1" is
  infeasible with a duty-cycled seg0; this is the strongest prefix the
  construction permits, registered here as the correction.)
- C0b: first_div(hybrid, allw) == 500 exactly; first_div(hybrid, duty58)
  == 2500 exactly; first_div(allw, duty58) == 500 exactly (3/3 seeds).
- C0c: allw and duty58 in this run bit-identical to l50/traces_l50.npz
  mm traces over the full [0,6000): max|d| == 0.0 (11th consecutive chain
  anchor; also re-verifies the shared-noise stream replication).
- C1: first_div(hybrid, hynohop) == 2000 exactly (hop wiring; nothing else
  differs) with volley-window max|d| > 1e-6; af in (0.01, 0.9) every arm.

## Gates (registered before the run)

- G1 TRACKING (allw-level): hybrid seg1 mean err <= .01 on 3/3 seeds
  (l50 allw: .001/.0013/.001).
- G2 STRUCTURE primary (pooled, duty58-level, the queue's literal duty):
  hybrid mean duty_all >= .5 AND no seed < .45 (l50 duty58 mean .576;
  duty = both per-side S >= .25, rolling 5 s window, seg spans skip first
  5 s — l50 convention verbatim).
- G2' STRUCTURE window-scoped (secondary, diagnostic): hybrid mean duty
  over the two 0.7-seg measurement windows >= .5.

## Verdict mapping (pre-registered)

- G1 & G2 pass  -> hybrid spec COMPLETE (pooled).
- G1 & G2' pass, G2 fail -> the conflict is irreducible AT THE FAST WINDOW
  at amp .3: continuous 1.4 buys the lock and is structure-toxic in-window
  (L50), so no schedule can serve both there; the hybrid is the honest
  controller in window-scoped form and carries both numbers separately.
- G1 fail, or G2' fail -> conflict irreducible beyond scheduling; name the
  window that broke.

## Predictions (registered, to be scored)

- P-a: G1 PASS (hybrid seg1 err .001-.01; the 2000 hop lands from a
  chopped entry state — uncertain, that is the measurement).
- P-b: G2 FAIL (~.30-.45): fast-window duty under continuous 1.4 ~.02-.13
  (l50 allw .022) drags the pooled mean below .5 even if 0.7 windows hit
  ~.6 (duty58 seg0/seg2: .64/.636).
- P-c: G2' PASS (~.55-.65); hybrid on/off split inside 0.7 windows both
  >= .4 (L50: off windows cost nothing).
- P-d: hynohop seg1 err > .01 on >= 1 seed (chopped entry does not
  obviously lock without the hop).

## Analysis windows

Verbatim l50: TS = arange(499,6000,10); rolling 500-sample per-side S;
measurement spans [seg0+500, seg0+2000); seg err = mean over BLK=500 blocks
excluding the first block of each segment; ttl = first block (post-first)
with err <= .10. Raw npz checkpoint BEFORE analysis (L45a lesson) carrying
every pool the metrics read (mm + all four antagonist pools + x046 + SL/SR).
