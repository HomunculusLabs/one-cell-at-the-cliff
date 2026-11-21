# L41 PREREG — structure-preserving transitions (written before any run)

Question (LANE.md ideas-19, L41): L39's winner (entrain + DNge046_L hop) tracks
the stepped target but transitions dip/invert antagonist antiphase (min seg
S(Tr) -0.316; sub-.25 cells at seed11 seg2 .205 and seed33 seg2 .164). Can any
of the three registered transition guards hold seg S >= .25 through EVERY
transition in 3/3 seeds while keeping the hop's tracking win?

Substrate: L39 controller verbatim — L32 arm-A frozen (g .01, beta 2,
D .05 tonic on DNg100), mech entrain amp .3 sinusoid tracking
0.7 -> 1.4 -> 0.7 Hz (SEG 2000 steps = 20 s/segment; DT 10 ms), WIN 6000 +
400 settle. Identical 21,516 nodes / 2,977,920 edges assert. Paired arms, ONE
generator, ONE shared per-step noise tensor (L36) — free/ent/base arms must be
BIT-IDENTICAL to l39's stored free/ent/ent_h046 (anchor C0). Drives enter
after settle (l39 form: mech at seg0 freq during settle, volley only in WIN);
af op-point assert every arm; per-arm drive table (no inline conditionals —
L39 v1 bug); dm probes on the volley cells (L35/L36/L38).

Arms (all entrain-tracking; hop channel DNge046 as in L39; base volley =
square 40 steps = 400 ms, amp .5, 2 L cells -> per-cell mass 20, arm total 40):
- free     — no drive (bit-identity gate vs l34/l39)
- ent      — entrain only (no hop control)
- base     — L39 ent_h046 verbatim: SQUARE volley, 40 steps, amp .5 on the
             2 DNge046 L cells, fired AT each segment boundary
- ramp_mm  — same cells/onset, TRIANGLE envelope 200 steps (2 s: rise 1 s,
             fall 1 s), peak 20/101 = .1980 (mass-matched: 101 x peak = 20)
- ramp_pm  — triangle 200 steps, peak .5 (peak-matched; per-cell mass 50.5)
- phase    — square 40/amp .5 L cells, but onset DELAYED to the next
             L-flexor-peak drive phase (timing rule below)
- side     — square 40 at boundary, SPLIT across mirror halves:
             DNge046_L amp .25 AND DNge046_R amp .25 (per-cell mass 10;
             4-cell total 40 = base)
- combo    — triangle 200 steps, DNge046_L peak .1 + DNge046_R peak .1
             (per-cell mass 10.1; 4-cell total ~40 = base), PHASE-timed onset

Phase-timing rule (pre-registered): drive phase phi[i] = the exact phase l39's
controller uses at WIN step i (accumulated 2*pi*f_seg*DT, including the settle
prefix at seg0 frequency). phi_fL = CIRCULAR MEAN of phi at local maxima of
the left Tr-flexor pool mean fL over steps [1000,2000) of seg0 (the entrained
0.7 Hz segment — uses only data BEFORE the first transition). Volley onset for
a transition at step t = first k > t where (phi[k]-phi_fL) mod 2pi <
(phi[k-1]-phi_fL) mod 2pi (phase just passed the flexor-peak phase; bounded
search t..t+300, fallback t with disclosure). ASSUMPTION (labeled): the
flexor-phase offset is frequency-invariant across the 0.7/1.4 Hz segments
(L34 phase-locking first-order carry).

Readouts per arm/seed: segment S(Tr) (L39 form: slice seg*2000+500,
(seg+1)*2000), S_trans (the 500 steps right at each transition, segs 1-2,
descriptive cost curve), SL/SR per segment, track_err/ttl (L39 form),
dm@046L and dm@046R vs ent (first_div relative to the arm's OWN onset,
volley_max), af after settle.

PRE-REGISTERED claim levels:
- C0 anchors: (a) free_f on l39's exact window (last 45 s, lo .5) within .03
  of {0.800, 1.444, 1.422}; (b) base arm BIT-IDENTICAL to l39/results_l39.json
  ent_h046: all segment S and track_err equal within 1e-6, dm first_div 0 /
  volley_max within 1e-6. C0 fails -> fix wiring before reading anything.
- C1 volleys land: every hop arm dm@046L volley_max > 1e-6 per seed; first_div
  in [0, env_len) relative to own onset. (phase arms: onset is the detected
  step; recorded explicitly.)
- P1 (prediction, not a gate): dm@046R == 0.0 EXACTLY for side/combo — L38
  census says the R mirror is ceiling-pinned (positive amp invisible). If it
  lands instead, the split arm is MORE than a gentler L hop — report either.
- G1 structure (the card's gate): arm passes G1 iff ALL 9 (seed, segment)
  S(Tr) >= .25. (base FAILS by construction on 3 cells — its numbers are the
  comparison floor.)
- G2 tracking held: per seed, track_err(seg1) <= max(0.05, base(seg1)) AND
  mean(track_err segs 1-2) <= base mean + 0.03.
- VERDICT per candidate arm: PASS = C1 and G1 and G2. Layered report on any
  fail (which cells lift, which still dip; S_trans cost profile). If no
  candidate passes, the honest ship is the measured best lift + mechanism.

Estimand label: P1-form (fixed per-class drive recipes re-applied on real
wiring; structure/cost question, no wins-claim beyond the registered gates).
No WHEN-claims beyond L21 delay bounds. Descriptive lab demo; owner movement
law respected (never app motion); no live changes; CPU-only.
