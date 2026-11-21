# L37 PREREG — steering-revisited on VIABLE channels (written before any scan)

Motivation: L33's "tonic bias cannot steer" verdict used DNg95 (L36 census:
u_max 0.047, frac of steps the bias enters ~.011 — the bias mostly never
entered the circuit). L36 shipped 34 viable-modulating DN types whose tonic
drive DOES land and frequency-modulates the intrinsic rhythm. This card
re-runs the L33 unilateral-bias grid with three L36-viable flex channels and
asks the steering question with channels that actually enter the circuit.

Substrate: l32 frozen verbatim (g .01, beta 2, d .05, arm-A signs, uniform
tau .05, DT .01, SETTLE 400, WIN 6000 steps = 60 s). ALL quoted metrics on
the last 45 s (0.25*WIN slice — L34 window rule, same window for metric,
trace, and FFT). Unilateral TONIC bias applied AFTER settle (L36 rule —
drive-during-settle lands on a different attractor).

Channels (L36 census viable-modulating flex, two-sided rule):
  DNge059  ipsi   u_max 4.52  n=2 (1L/1R)  top target Tr flexor MN
  DNg105   crossed u_max 3.58 n=2 (1L/1R)  top target Ti flexor MN (L24: all-inhibitory)
  DNge046  crossed u_max 2.66 n=4 (2L/2R)  top target Acc. tr flexor MN
Static edge-sign composition onto Ti/Tr flexor MNs measured in-script
(exc vs inh weight, per target side); predicted turn sign is DERIVED from
measured org x sign: turn = (massL - massR)/(massL + massR) pooled Ti+Tr
flexor MNs; ipsi-excitatory drive-L -> +; crossed-excitatory drive-L -> -;
crossed-inhibitory drive-L -> + (suppresses contra flexors).

Arms (3 seeds 11/22/33 each, paired lockstep):
  base (no steer)
  {3 channels x L-side x amps [.05, .2, .8]}
  {3 channels x R-side x .8}          (mirror sign control, L24 form)
  2 random DN pairs x .8              (pool excludes channel types + DNg100)

Instruments (L35/L36): ONE generator per seed, ONE shared per-step noise
tensor for base and steer arm; first_div = first window step with
max|Xs - Xb| > 1e-6; dm = max|Xs - Xb| over window; every steer arm must
have dm > 1e-4 (bit-identical = drive never entered = attribution void).
Base re-run inside every pair, bit-identity vs seed reference asserted.
af assert 0.01 < af < 0.9 (L30 wiring probe) on base AND steer.

Claim levels:
  C0 anchors: base S_Tr pooled in [+.30, +.60] every seed; rhythm ratio
     >= 50; base turn_Ti flexor in [+.05, +.25] (L33 wiring-set +.13).
  C1 survival: every steer arm keeps S_Tr pooled >= +.30 all seeds.
  C2 revival: at amp .8, |turn - turn_base| >= .15 with 3/3 seeds matching
     the org x sign DERIVED predicted sign, for >= 1 channel.
  C3 dose-response: |turn - turn_base| non-decreasing across [.05, .2, .8]
     3/3 seeds for >= 1 channel.
  C4 nulls: each random pair at .8 shows |shift| < the best channel's
     |shift| OR sign not 3/3 seed-consistent.
Verdict map (pre-registered):
  C2 (+C3) PASS -> steering-by-tonic-bias REVIVES; L33 amended (negative
     was a channel-choice artifact).
  C2 FAIL, frequency shift present -> speed-without-steering: the cord is
     a throttle, CX owns direction (consistent with L31).
  C1 FAIL -> viable channels break the rhythm they modulate; frequency
     modulation is not steering-compatible in this regime.
Amendments only pre-grid; any post-hoc change disclosed in LAB-INTENT.
