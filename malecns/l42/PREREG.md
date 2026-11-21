# L42 PREREG — entrain-hop-stop-stack (written before any run)

Endgame stack demo on the frozen L32 substrate (g .01 / beta 2 / D .05, 21,516
nodes / 2,977,920 edges asserted): ONE controller using all three measured
primitives {entrain, hop, stop} through a target trajectory WITH a stop
segment, plus recovery-latency gates (tick-58 amendment: structure repair is
POST-disturbance recovery, entrain amp is the knob; NO volley-envelope gates —
L41 negative).

## Task (DT 10 ms, steps)

settle 400 @0.7 Hz (l39-exact) then:
- seg0 [0, 2000):    target 0.7 Hz  — entrain only
- seg1 [2000, 4000): target 1.4 Hz  — hop volley @2000 (l39 form: DNge046_L,
  amp .5, 40-step square) — ANCHOR REGION: identical drives to l39 seg1
- seg2 [4000, 5000): STOP 10 s — target 0 Hz: mech drive OFF for every
  entraining arm; stack arms add DNg88 tonic -8.0 (L38/L40 stop channel)
- seg3 [5000, 7000): RESTART — target 0.7 Hz, mech drive back ON; stack arms
  fire the restart hop @5000 (same volley form)

PHI accumulator replicates l39 exactly over [0,4000) (settle@0.7, seg0 0.7,
seg1 1.4); phase FROZEN during seg2; resumes 0.7 at seg3.

## Arms (drive table, no inline conditionals — L39 v1 lesson)

- free:    no drive ever
- ent:     mech entrain amp .3 (no volleys, no stop drive)
- entstop: ent + DNg88 -8 during [4000,5000)            (isolates restart hop)
- stack:   ent + hop@2000 + hop@5000 + DNg88 -8 [4000,5000)
- stack_lo: stack with entrain amp .03 (repair-knob sweep point, L34)

One generator per seed, ONE shared per-step noise tensor for all arms (L36);
X0 draw and draw order identical to l39/l41 (bit-identity requirement).
af assert after settle per arm: 0.01 < af < 0.9.

## Pre-registered gates

- C0 ANCHORS (must PASS): max|mm diff| == 0.0 for
  free   vs l39 free    over [0,6000),
  ent    vs l39 ent     over [0,4000),
  stack  vs l39 ent_h046 over [0,4000)   (2nd volley at 4000 excluded),
  entstop vs own ent    over [0,4000).
- C1 LANDS: stack hop1 volley_max > 1e-6 & first_div == 0; stop lands:
  max|X_stack - X_ent| over stop window > 1e-6 AND DNg88 un-pins
  (min mean x88 during stop < 0.5, from pinned ~1.0); restart hop lands:
  max|X_stack[hopL] - X_ent[hopL]| over [5000,5040) > 1e-6.
- C2 TRACKING: (a) stack seg1 track_err <= max(.05, l39 ent_h046 seg1 + .001)
  3/3 seeds; (b) restart lock: stack first block (from seg3 start) with
  err <= .10 within 2 blocks (<=10 s) in >= 2/3 seeds; entstop reported as
  the no-restart-hop decomposition.
  [amendment pre-run: track_err/ttl computed with l39's exact convention
   (skip first 1 block = 5 s of each segment) for anchor comparability;
   stricter 10-s skip dropped. Disclosed here BEFORE any data.]
- C3 STOP: stack rhythm ratio (l40 rhythm2, mm, 0.5-10 Hz) over [4000,5000)
  < 5 in 3/3 seeds while ent keeps >= 20 in 3/3; kill latency (first 100-step
  chunk with ratio < 5) <= 1000 steps.
- C4 RECOVERY (the honest gate, tick-58 amendment): rolling S(t) =
  -corr(fL+fR, eL+eR) over [t-499,t] (5-s window, every 10 steps); recovery
  from event e = first t >= e with S >= .25 AND min S over [t, t+250] >= .25
  (persistence, L35). GATE: stack recovery after RESTART (e=5040) within
  seg3 in <= 1000 steps (10 s) in >= 2/3 seeds. ALSO REPORT (no gate — L41
  showed structure loss can persist a segment; the numbers are the
  deliverable): stack after HOP1 (e=2040), ent after freq-step (e=2000),
  entstop after restart (e=5000).
- C5 REPAIR KNOB (exploratory, P1): stack (.3) recovery-after-restart
  < stack_lo (.03) in >= 2/3 seeds (L34: .3 re-hosts, .03 locks without
  re-hosting). Table reported either way.

Estimand label: P1 (real-tuned gains re-applied; no wins-claim). Descriptive
lab demo only — owner movement law; no live changes.
