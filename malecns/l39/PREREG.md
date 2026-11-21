# L39 PREREG — discrete-gait-controller (entrain + hop, 2 primitives)

Written BEFORE any L39 run. Substrate = frozen L32 regime (g .01 / beta 2 /
d .05, arm A), l34 machinery verbatim; anchors from l34 (bit-compatible C0).

## Controller (descriptive lab demo; owner movement law — no live/app claims)

Target trajectory: step 0.7 Hz (20 s) -> 1.4 Hz (20 s) -> 0.7 Hz (20 s),
after the 400-step settle. Drive phase accumulated continuously (no reset
at transitions). WIN 6000 @ DT 10 ms.

Arms (per seed, ONE paired loop, one generator + ONE shared per-step noise
tensor across arms — L36 lesson):
- free:   no drive, no volley (control)
- ent:    mech sinusoid, amp 0.3, fd(t) = target (L34: A=.3 locks + re-hosts S)
- ent_h046: ent + DNge046_L volley, amp 0.5, 400 ms, at each transition step
- ent_h110: ent + DNg110 volley (all 6 cells, both sides viable), amp 0.5,
  400 ms, at each transition step

## Measures
- f_track: dom_freq (parabolic, l34 form) of motor-mean on 5-s blocks
  (12 blocks). Per segment: tracking error = mean |f - target| over blocks
  2-4 (first 5 s = settle allowance); time-to-lock = first block
  |f - target| <= 0.10 Hz (else >15 s, capped).
- S(Tr) pooled + per-side (SL, SR) on last 15 s of each segment; rhythm
  ratio; af assert (0.01 < af < 0.9) EVERY arm.
- dm probes vs ent arm: first_div step + volley-window max|dX| (L35/L36).

## Claim levels
- C0 substrate: free-run f within 0.03 of {11:0.800, 22:1.444, 33:1.422},
  S(Tr) >= 0.40, ratio >= 100.
- C1 hop lands: first_div inside the volley window AND volley max|dX| > 1e-6,
  both channels, 3/3 seeds.
- C2 entrain tracks: ent arm mean tracking error <= 0.15 Hz in >= 2/3 seeds
  AND < 0.5x the free arm's per-seed error.
- C3 hop accelerates: (a) median time-to-lock over the 2 transitions+3 seeds
  strictly smaller than ent for that hop arm, or (b) mean tracking error
  smaller in >= 2/3 seeds; while post-transition segment S(Tr) >= 0.25
  (a hop that only breaks the rhythm CANNOT pass C3).
- C4 survival: ent/ent_hop segment S(Tr) >= 0.25 all seeds/segments; side
  dominance (SL vs SR sign) reported descriptively (metastable flips, L33).

## Honest outcomes
Any FAIL is a finding: hop volleys may be absorbed (relu floor), may not
outlast the volley (L35 relaxation), or may rupture S (L38 DNg88 form).
P1-labeled throughout; no WHEN-claims beyond L21 delay bounds.
