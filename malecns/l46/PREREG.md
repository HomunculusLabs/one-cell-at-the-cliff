# L46 PREREG — post-stop recovery kinetics (written before any run)

Question (L44 tick-62 disclosed note, ideas-22): in L44 the MOST protected
arm during the stop (h40: S_med_during .39-.59) showed ~ZERO antagonist
structure at the 20-s post window (S_med_after -.037/+.020/+.032) while
h0 (S_dur .07-.16) and h20 (.42-.54) recovered (.37-.51). Is that a WINDOW
ARTIFACT (recovery is slow, not lost) or a real COST of deep entrain
history (post-stop structure impairment the controller must budget)?

## Design (l44 machinery verbatim, one change: post window length)

SETTLE=400 free; STOP0=4000; STOPD=2000 (stop = DNg88 += -8.0 on
[4000,6000), unchanged); POST=12000 steps = 120 s (vs l44's 20 s);
WIN=18000. Arms H in {0, 20, 40} s of 0.7 Hz mech entrainment ending at
STOP0 (ENT_AMP 0.3, global continuous phase incl. settle prefix). G=0.01,
BETA=2, D=0.05 tonic DNg100 (inert per L35, kept for machinery identity).
Seeds 11/22/33. ONE generator + ONE shared per-step noise tensor per seed
(L36); X0 drawn first. Substrate assert 21,516 / 2,977,920; af assert
0.01<af<0.9 per arm (L30). Raw npz checkpoint (ALL pools the analysis
reads: mm/fL/fR/eL/eR/x88/xc) BEFORE analysis (L43/L45a lessons).

## Metrics

Rolling S(Tr) = -corr(fL+fR, eL+eR) over 500-step windows sampled every
10 steps (l44 def). Post reads on [6000,18000):
- S_med_early  = median S over [6000,12000)  (first 60 s post)
- S_med_late   = median S over [12000,18000) (last 60 s post)
- S_med_20s    = median S over [6000,8000)   (l44's window, premise check)
- lat_first    = first post sample with S >= .25 (steps after stop-off;
                 None if never)
- duty_early/late = mean(S >= .25) per window
- f_late       = rhythm2 peak freq of mm over [12000,18000)
- core_late_post = mean X(core 30) over [12000,18000) vs stop-end
In-run premise check: S_med_20s must match l44's stored S_med_after
(h40 ~ 0, h0/h20 >= .25) — comes free from C0 bit-identity.

## Gates (pre-registered)

- C0 anchor: (a) prefix bit-identity max|mm_l46 - mm_l44| == 0.0 over the
  shared [0,8000) window, all 9 arm-seed pairs (6th consecutive anchored
  run; noise-stream replication is the design). If nonzero: disclose
  max|d|, fall back to numeric anchor (max|d| < 1e-6 AND S_med_20s equal
  to l44 stored at 3 dp). (b) Premise replicated: h40 S_med_20s < .25 3/3
  AND h0/h20 S_med_20s >= .25 in >= 2/3 each.
- C1 drives: x88min < 0.5 every arm/seed (stop un-pins); dm_lands =
  max|mm_h40 - mm_h0| over [3500,4000) > 0, 3/3 (entrain entered).
- C2 VERDICT (the ship):
  * SLOW-RECOVERY (window artifact): h40 S_med_late >= .25 in 3/3 while
    h40 S_med_20s < .25 3/3 -> latency table is the deliverable.
  * IMPAIRED (cost of protection): h40 S_med_late < .25 in >= 2/3 seeds
    while h0 S_med_late >= .25 in >= 2/3 -> protection buys in-stop S at
    the price of post-stop structure; controller spec gains a recovery
    budget line after stops on deeply-entrained cords.
  * MIXED otherwise (e.g. h0 also wanders late = L45b gas; read the table,
    compare h40 vs h0 late-gap as the descriptive contrast).
- C3 secondary (descriptive, no gate): f_late per arm (0.7 Hz memory
  persistence into late post, L44 found h40 carried 0.6 through the stop);
  core_late_post relaxation vs stop-end; lat_first/duty for h0/h20.

Honest expectations: if the 20-s h40 zero is real and slow, S(t) should
show a rising trend through the post window (latency >> 20 s). If the gas
simply re-rolls the S_R axis (L45b: spontaneous migration is the floor),
h40 late S could land anywhere — then the verdict is MIXED and the honest
deliverable is the h40-vs-h0 late distribution over a 120-s window with
the spontaneous floor named. No WHEN-claim beyond latency bounds at this
fidelity (L15/L21); P1-labeled throughout; CPU-only; no live changes.
