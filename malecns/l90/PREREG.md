# L90 PREREG — multi-batch gate re-base (registered 2026-11-15 19:1x, BEFORE any rollout)

## Why
L88 post-hoc: the census batch was favorable for duty_07 (hybrid k 13→9 on fresh
501-516; even the 2-arm seed-knowledge oracle only 13/16 fresh) while G3/seg1 is
batch-stable (.40-.50). GATE-L85's G2a row (l85/PREREG.md: "k >= 15/16 AND Wilson
lb >= .717") is calibrated on ONE batch — before any future structure claim is
cited it must be re-based across seed batches, and the L80 C4b echo-lever margin
(hynohop 11/16 → hynohop_fb 15/16, census) re-read under batch variance.

DISCLOSURE (found while pinning thresholds, pre-run): the original G2a lb clause
at n=16 passes at k=15 ONLY through wilson()'s 3-decimal ROUNDING (true lb
.71674 → rounds to .717 ≥ .717); k=16's true lb is .8064. The census bar was
effectively "k ≥ 15/16". The amended form below pins the lb at FULL precision.

## Registered batches (pre-declared; fresh ids never used in the chain)
- B0 census: [11,22,33]+list(range(101,114)) — STORED raw_l87.npz (4 trunks);
  only seeds 11/22/33 re-rolled, as the C0A chain anchor.
- B1: list(range(501,517)) — hybrid STORED raw_l88.npz; re-rolled here as the
  C0D bit-anchor; hynohop / hynohop_fb / hybrid_fb NEW.
- B2: list(range(601,617)) — NEW, all 4 trunks.
- B3: list(range(701,717)) — NEW, all 4 trunks.
Noise-stream fact this relies on (l87 machinery): X0 and the per-step nz are
drawn from ONE generator per seed, once per step, shared across arms — arm
count does not perturb the stream, so new arms on stored seeds are exact.

## Registered arms
The 4 l87 trunks verbatim: hynohop, hynohop_fb, hybrid, hybrid_fb.
AMPA/HOPA/EON tables asserted at build time (l87 write-time asserts kept).

## Registered reads
Per arm x batch: per-seed duty_07 (k = #(d07>=.5), Wilson z=1.96), per-seed
seg1 duty mean + block err (G1 lock), seg1 mean (G3 axis), echo budget ratio
(fb arms). Descriptive: per-arm k distribution ACROSS batches; seg1/seg2
batch-stability (L88's claim measured properly on 4 batches).

## AMENDED G2a (G2a-multi) — the registered form; replaces the census-only row
Pooled Wilson lb at FULL precision >= .717 over the batch union (equal 16-seed
strata, so pooled counts == stratified mean):
- n=64 (B0+B1+B2+B3) → k >= 53 (lb .7179 at 53, .7003 at 52 — verified).
- If an anchor invalidates one batch: n=48 → k >= 41 (lb .7283 at 41, .7042 at 40).
Per-batch k's are REPORTED diagnostics, never gates. (The alternative
"k >= 15 on >= 2 of 3 batches" was considered and REJECTED: dichotomization
wastes seeds — for a true p̂~.85-.9 lever, per-batch k>=15 fires only ~30-60%
of the time, so a real lever fails it routinely.)
G4-multi (reported alongside): pooled mean echo ratio <= .127, per-batch
disclosed. G1/G3 stay per-batch reported; lock misses do NOT drop seeds from
G2a-multi (duty_07 reads seg0+seg2, lock reads seg1 — independent axes;
L88's hybrid 15/16 fresh lock miss is the precedent, disclosed).

## C4b margin re-read — pre-registered outcomes (BBS #54 addendum on WEAKENED/COLLAPSED)
fb = hynohop_fb vs base = hynohop (secondary: hybrid_fb vs hybrid):
- STRENGTHENED: pooled lb(fb) >= .717 AND pooled lb(base) < .717 AND paired
  per-seed d07 delta (fb-base) positive on >= 3 of 4 batches.
- WEAKENED: pooled bar holds (fb clears, base does not) but delta direction
  inconsistent (positive on <= 2 of 4 batches).
- COLLAPSED: pooled lb(fb) < .717 OR pooled lb(base) >= .717 (margin gone).

## Anchors (all must pass BEFORE any read is pinned)
- C0A chain (intended 34th consecutive): trunks re-rolled on census seeds
  11/22/33 == raw_l87.npz BIT-IDENTICAL (mm + fL/fR/eL/eR, max|d| == 0.0).
- C0B metric certification: my cells machinery run on STORED raw_l87.npz
  reproduces results_l87.json distributions per-seed values (d07 per-seed,
  seg means/k/wilson/err_le01) for the 4 trunks EXACTLY (L85 rule).
- C0D: hybrid re-rolled on B1 == raw_l88.npz BIT-IDENTICAL (16 seeds, mm+4
  sigs) AND my cells == l88 stored cells for hybrid on B1 exactly.
- C0E mechanism law on every NEW seed (B1/B2/B3): first divergence of
  mm(fb vs base) == 6 for BOTH fb arms (l66/l77 one-hop echo law; doubles as
  the anti-degenerate check — an all-zero fb arm would violate it).
- C1: settled af in (0.01, 0.9) every arm-seed.
Anchor failure → addendum BEFORE pinning reads (house rule).

## Rollout
l87_branch.py step order verbatim (per-seed generator, shared nz, settle 400,
WIN 6000, G .01 / BETA 2 / D .05 frozen arm-A, FB cell g .1 / delay 5 / sign -1).
CPU-only, torch.manual_seed(0), 8 threads, run from malecns/ (relative data
paths — L76 lesson). raw_l90.npz checkpointed BEFORE analysis; per-seed
raw_partial.npz enables resume; l90_verdict.py re-derives every read from the
stored npz if the inline analysis dies (l77/l79/l82 pattern).
