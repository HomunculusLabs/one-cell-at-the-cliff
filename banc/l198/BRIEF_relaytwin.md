# EXPERIMENT brief — L198 relay-matched twin, then gate-jitter v2 (chained)

Owner-directed (2026-11-21 ~18:4x, evening wave). Two rollout jobs,
chained: run L198 first, THEN gate-jitter v2 (the lane's L197 card,
redesigned with power).

## L198 — the relay-matched cord-interneuron twin (closes L187's caveat)

The relay (GI 75494) reaches SUPER on the chopped classifier alone, but
no matched twin for cord interneurons exists — "the relay does it" is
not yet special to THIS interneuron. Fix that:
- Selection (PREREG before choosing): among cord interneurons NOT in any
  prior arm, pick the cell minimizing |log(drive ratio)| to the relay's
  delivered drive on the k=24 base (3-seed census; drive = x_mean ×
  out|w|), tie-break mass; register top-5 runners-up.
- Arm: remove that cell from the k=24 base, 16 seeds, re-bisected gain
  (your L187/L190 harness, C0A anchors mandatory).
- Branches: **T1 relay-special** (twin does not reach SUPER nor the
  1.4-Hz signature), **T2 relay-generic** (twin matches the relay's
  profile), **T3 intermediate**. Also record the twin's 1.4-Hz middle
  value either way.

## Then: gate-jitter v2 (the lane's L197 design — read it first)

Read LANE.md's L197 card (gate-jitter v2, "the discriminator with
POWER"). Implement per its spec: the v1 design underpowered the
aligned-vs-elapsed contrast (interval −.156..+.126); v2 must register a
power analysis (effect size from v1's +.275 elevation; n needed to
resolve a .10 aligned-elapsed difference at the seeds level), then run
the powered n. If the card's spec conflicts with feasibility (CPU/time),
PREREG the amended design and say why. Predictions registered first.

## Rules

PREREG per experiment before rollouts; fresh key-scanned seeds; C0A
anchors; CPU ≤6 workers total across the chain; writes to banc/l198/**
and banc/l197b/** (v2) + one LAB-INTENT append each. Wall ≤3 h for the
chain. Final answer ≤250 words: T-branch, v2 verdict, what changed.
