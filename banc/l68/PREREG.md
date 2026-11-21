# L68 PREREG — banc-entrain-replication, slice A (op-point reuse + entrain probe)

Question (LANE.md ideas-33 L68): the L34–L66 entrainment contract is male-cord
measured. Does the female BANC cord (L65 substrate: same-sex, frozen arm-B
settings g .14 / beta 2 / DNg100 tonic d .2, raw log1p weights, flyvis
glut-INH sign arm) ENTRAIN under the core l55 schedule row — chopped 0.7 Hz
(500-on/400-off) segs + continuous 1.4 Hz fast seg — and hold off-window
antagonist structure?

## Substrate (L65 verbatim, no re-tuning)
- Subnet: 20,521 cord (region==ventral_nerve_cord, super_class in
  sensory/vnc_intrinsic/motor) + 728 dn_into = 21,249; 627,051 edges.
- Pools (semantic peripheral_target_type): Ti flex 101 / ext 12; Tr flex 62 /
  ext 48; L/R via `side` column (assert splits non-empty).
- Sign arm B: glutamate -> inhibitory (np.where(is_glut, -abs, sign_a)).
- Frozen: g .14, beta 2.0 (negatives scaled), DNg100 tonic d .2 (2 cells),
  TAU .05 / DT .01 / RMAX 1 / BG .02 / NOISE .01, SETTLE 400, WIN 6000.
- Mech channel (registered choice): subnet sensory cells with cell_function
  in {tactile, proprioception} — the direct analog of the male
  mechanosensory_tactile+proprioceptive class (3,588/6,370 = 56% of male vnc
  sensory; female 4,848/7,407 = 65%). Count asserted + registered.

## Arms (seeds 11/22/33)
- l65conv  — L65 run() verbatim, lone rollout, own generator (drive-free
             settle then I-only window): C0 bit-identity anchor vs
             l65/raw_l65.npz B traces.
- open     — free-run: DNg100 tonic only, no mech ever (l59 open form);
             shared-noise multi-arm group.
- hyb03 / hyb01 — l55 hybrid AMPA schedule verbatim (chop 500-on/400-off on
             both 0.7 segs, continuous fast seg), global phase accumulator
             stepping at target freq (settle at 0.7, drive-on during settle
             at the arm amp — l55 convention), amp .3 / .1 (dose guard:
             female g is 14x male's; .3 may saturate).
Multi-arm group: ONE generator, X0 drawn once + cloned per arm, ONE shared
per-step noise tensor (L36/L45b lessons). DRIVE_ON assert: 400 + 4,400 = 4,800.

## Readouts (l55 forms verbatim)
- Per-500-step-block dom_freq (parabolic) + err vs seg target; LOCK_TOL .10.
- Per-side S on 500-step rolling windows, per pair (Ti AND Tr; Ti registered
  PRIMARY — L65's stronger pair .68-.76 vs .48-.51).
- duty per seg over [seg0+500, seg0+2000): mean( SL>=.25 & SR>=.25 );
  duty_07, duty_all.
- af assert (0.01, 0.9) every arm; NaN assert.

## Gates
- C0 ANCHORS: l65conv max|d| == 0.0 on all 15 keys x 3 seeds vs
  l65/raw_l65.npz (B_s{s}_{Ti,Tr}_{f,e} + B_s{s}_mm); subnet asserts
  (n, edges, pool sizes, DNg100==2, mech count); open rhythm ratio > 100
  (L65 671–1009x) AND open S(Ti) > .40 (L65 .683/.712/.764).
- G1 ENTRAINS (the card's question): at the BEST amp arm (lowest fast-seg
  mean err), fast-seg err <= LOCK_TOL on >= 2/3 seeds AND 0.7-seg err
  <= LOCK_TOL on >= 2/3 seeds.
- G2 STRUCTURE: at the same arm, mean duty_07 >= .30 on >= 2/3 seeds.
  (Male reference duty_07 .45–.64; .30 registered as the minimal
  replication floor given the female's stronger intrinsic S — disclosed.)
- G3 op point: af in range everywhere, no NaN, no dead channel (mech drive
  changes the trace: hyb03 vs open max|d| > 0 in-window).
- VERDICT MAP: G1+G2 -> REPLICATES (census follow-up card if picked);
  G1 only -> ENTRAINS-NO-STRUCTURE (contract row carries a structure
  male-only flag); G1 fail -> NO-ENTRAIN (contract rows carry male-only
  flags; slice B not run).

## Registered prediction (prior, scored either way)
G1 PASS (L65's strong intrinsic rhythm should lock to periodic drive, L34
male analogy); G2 uncertain — the female's higher intrinsic S(Ti) helps but
chop off-windows may not hold structure; this read is the informative one.
Flat-amp risk: if .3 saturates (af > .5 in-window or S collapses to NaN-free
noise), hyb01 is the registered fallback for G1/G2 reads.

## ADDENDUM 1 (post-rollout, pre-final-verdict, 2026-11-14 08:5x)
Registered G1 (block-argmax lock err) read 0/3 on both 0.7 and fast segs —
but the probe's open-arm f/ratio labels were crossed (L35 class, caught by
magnitude sanity; raw unaffected) and the spectra showed drive-frequency
power ABSENT in open and PRESENT in driven arms, with several "misses" at
exact subharmonics (0.7 = 1.4/2). Amended operationalization, registered
BEFORE re-reading: n:m spectral entrainment = P_mm(f_drive) on the driven
arm / same read on open arm (paired seeds), per drive frequency, best amp
per frequency; plus P at f_drive/2 and 2*f_drive and the chop envelope
(0.111 Hz) for texture. G1' PASS = ratio > 10 on >= 2/3 seeds at some amp.
G1 (1:1 razor lock, the male l55 row) still scored as registered: FAIL.
Verdict map gains the PARTIAL arm: G1 fail + G1' pass + G2 pass =
PARTIAL REPLICATION (tracking row male-only, structure row generalizes).
No new rollouts; all reads from l68/raw_l68.npz.
