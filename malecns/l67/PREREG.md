# L67 PREREG — side-split-echo (registered 2026-11-14 07:2x, BEFORE any rollout)

Question (LANE.md ideas-33): L66 showed the bilateral negative content cell
(g .1, sign −, delay 5) rescues S_L everywhere (all 16 seeds >= .409) and
never touches S_R (.153 -> .186); both census misses were SR-marginal. Does
a SIDE-SPLIT echo (each side's own antagonist mass onto its own root-side
mech only; rootSide join 0.9997 from L60) lift the untouched side
(S_R) without re-rolling the rescued side — or does unilateral echo behave
like L60's asymmetric drive (re-roll lottery / crossed effect)?

## Arms (all stepped in ONE shared per-step noise stream, l66 form)
- bi     = L66 content cell verbatim (pooled 4-pool ANTAG mean onto ALL mech),
           gain .1, sign −1, delay 5. ANCHOR arm.
- lonly  = L-side mass (mean over fL∪eL) onto mechL only.
- ronly  = R-side mass (mean over fR∪eR) onto mechR only.
- split  = lonly + ronly together (mL->mechL, mR->mechR).
- open   = NOT rerun: read from l66/raw_l66.npz hynohop traces (16 seeds),
           value-anchored against results_l66.json open block (C0O).

Substrate/schedule/metrics: l66_census.py verbatim (chop 500/400 @0.7 Hz +
continuous 1.4 seg2, DT 10 ms, OFFS windows, TS3 3-s grid, 300-sample S
windows, seg2 lock via dom_freq on 500-step blocks). NEW per-side reads:
dutyL = mean(SL >= .25), dutyR = mean(SR >= .25) over the same off-window
sample set as duty_off's bilateral duty.

## Anchors (enumerated keys only; L59 lesson)
- C0  : bi bit-identical to l66 stored g01_d05_m on ALL 16 seeds
        (mm + fL/fR/eL/eR, full 6000 window, max|d| == 0.0).
- C0O : open metrics recomputed from l66 stored traces == results_l66.json
        open block (off, SL, SR arrays exact to stored rounding).
- C0s : each side arm vs l66-stored open: prefix [0, delay+1) bit-identical
        (max|d| == 0.0) AND first_div == delay+1 (= 6) on mm+traces for every
        arm/seed (L66 ADDENDUM-1 form: echo enters mech at k=delay, pools
        see it one hop later).
- C0w : write-time wiring probe (dry step): lonly echo support ∩ mechR empty,
        ronly support ∩ mechL empty, split support == mechL∪mechR exactly,
        mechU untouched by side arms (touched by bi); len(mechL),len(mechR)>0.
- C1  : settled af in (0.01, 0.9) every stepped arm/seed.

## Pre-registered predictions (scored BEFORE any "branch" language)
P1 (G1, side-tunable content — branch A): ronly mean dSR >= +.10 AND
    P(dSR > 0) >= 11/16 AND mean dSL >= −.05 (no S_L re-roll) AND lock_ok.
P2 (ipsi-selectivity): lonly mean dSL >= +.10 AND dSL > dSR (own side first).
P3 (crossed test — L60 form): under ronly mean dSL <= +.05; CROSSED is
    flagged if mean|dSL| >= mean|dSR| under ronly.
P4 (lock pristine): all four fb arms lock_ok (e2 median <= max(.01, 2×open
    median), e2 max <= .5, catastrophic cat flag recorded).
P5 (split constructive): split dSL >= +.10 AND dSR >= +.10 AND lock_ok.

Branch B (lottery/crossed, L60 class) is SELECTED if P1 FAILS and (P3 crossed
fires OR lonly fails its own side (dSL < bi dSL − .10) OR >= 5/16 seeds flip
dSR sign between ronly and split). Both branches registered; report which
carries the verdict. Vacuous-pass guard (L55): dm_min > 0 required for every
side arm (echo landed); any gate passing with dm_min == 0 is reported as
wired-dead, not as a win. Paired per-seed deltas vs the SAME seeds' open
(L45b rule). n=16 census seeds (l45b grid), no sham (content already
established L66; this is a mechanism card).

Budget: ~35 min CPU. No live changes.
