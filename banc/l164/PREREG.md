# L164 PREREG — slow-line ORIGIN, the ROLLOUT arm: one shared clock or
# independent oscillators? (fresh rollouts, phase freedom injected)

Card: LANE.md ideas 84, L164 ("the admissible test L162 named").

## Why this card exists (the L162 degeneracy, restated from the artifact)

L162 ADDENDUM 2/3 recorded that its D-axis is **uninterpretable by
construction** on the stored substrate: every carrier pool's .100 Hz
component has a phase that is REPRODUCIBLE ACROSS ROLLOUTS
(`l162/static.json` I4'/PLV_self .962-.997; pair PLV .941-.995, 28/28
locked), because the drive protocol — the chopped 0.7/1.4/0.7 Hz mech
sinusoid — starts at the SAME phase on every rollout. A seed-shuffled
null then carries the same deterministic component as the matched arm,
so coherence cannot separate "one shared clock" from "independent
oscillators that are each separately locked to the protocol".

The admissible fix is to make the ROLLOUT ORIGIN stop carrying the
phase: give the drive a random per-seed onset phase. Then PLV_self
measures whether a channel's .100 Hz phase is set by the PROTOCOL
(falls when the protocol phase is freed) and the PAIR PLV becomes a
genuine shared-clock measurement (two pools that share one internal
oscillator keep a fixed phase RELATION even when the common origin is
scrambled).

## Substrate (pinned)

- Graph: **b65** only = `keep_old` closure (cord + dn_into), the
  claim-carrying arm of L157/L162. Built by the l154_run.py extraction
  VERBATIM (same `build`/`wb`, same glut-sign rule, same pools/mech/
  motor/DNg100 derivation). G65 = 0.14 stored constant, BETA 2.0,
  D (DNg100) 0.2, ENT_AMP 0.1, TAU .05, DT .01, BG .02, NOISE .01,
  SETTLE 400, WIN 6000, SEGB [(0,2000,.7),(2000,4000,1.4),(4000,6000,.7)].
- Channels: the 20 L101 antagonist pools + mm + xm, (6000,) at DT .01.
- CARRIER / CONTROL sets DERIVED from `l157/static.json` exactly as
  l162c_phase.py derives them (wilson_lb >= 0.5 -> 8 carriers;
  below <= 6 -> 9 controls). Assert 8 / 9. 28 carrier pairs,
  36 control pairs.
- Target bin: full-trace rfftfreq(6000, .01)[6] == 0.1 Hz to 1e-12.

## The intervention (exactly what "random onset phase" means here)

Per seed s an integer offset `o_s` in [0, 900) is drawn from
`np.random.default_rng(164)` (deterministic, recorded). The SEGMENT
SKELETON is untouched (regime timing identical across seeds, so the
dynamical regime is not an arm difference); the DRIVE's own phase is
offset in two places that together define it:

1. chop gate: `((k - seg0 + o_s) % 900) < 500` inside the chopped
   segments (base: `o_s = 0`); segment 1 stays fully on, as in base.
2. carrier phase: the accumulator starts at
   `psi_s = 2*pi*0.7*DT*o_s` instead of 0, then integrates target(k)*DT
   as in base.

Arms:
- **fix** — `o_s = 0` for every seed (the stored protocol, re-run on
  fresh seeds). Positive control + C0A anchor.
- **rnd** — `o_s` as drawn. Identical substrate, gain, noise stream,
  initial condition; the drive waveform is the ONLY difference.

Both arms share ONE generator pair per seed and the l154 draw order
(gen: n_old draws, gen2: n_add draws, every settle and run step), so
the arms are paired-noise (L36) and the fix arm is bit-comparable to
the stored b65 rollouts.

Seeds: fresh batch **B42 = 4201-4216** (16 seeds; absence-verified
against every stored npz before launch, L157 rule) + anchors 801/901
on the fix arm only.

## PRE-MEASUREMENT, registered to run BEFORE any rollout (L146/L55)

The intervention is only admissible if it actually frees the drive's
.100 Hz phase. `l164_drive.py` computes the drive scalar sequence
s[k] (the exact expression added to `drive[mech]`) for `o_s = 0` and
for all 16 drawn offsets, and reports at bin 6:

- D1 drive power |S[6]|^2 under fix and rnd (is there a .100 Hz line in
  the drive at all?),
- D2 **PLV_drive** across the 16 rnd offsets (and across the 16
  identical fix copies, which must be 1.0 by construction),
- D3 the circular spread of arg S[6].

**GATE (pre-registered, halting):** if `PLV_drive(rnd) >= 0.4` the
design is VACUOUS-BY-CONSTRUCTION and the tick reports
`B_VACUOUS_DESIGN` — the rollouts are NOT run as the primary (an
amendment naming a stronger randomisation is written first). If
`PLV_drive(rnd) < 0.4` the design is well-posed and the rollouts
proceed. The gate's number is reported either way.

## Instruments (machinery copied VERBATIM from l162c_phase.py)

- `phase_of(x) = angle(rfft(x - mean(x))[6])`, `plv(ph) = |mean e^{i ph}|`.
- **PLV_self(channel, arm)** = plv over the 16 B42 seeds of that
  channel's own bin-6 phase. Under free phases E[PLV] = sqrt(pi/(4n))
  = **0.2216** at n = 16 (reported as the floor beside every number).
- **pair PLV(A,B,arm)** = L162 I2 VERBATIM: dphi_s =
  angle(X_A[6] conj(X_B[6])), PLV over seeds, Rayleigh p = exp(-n PLV^2).
- **evoked fraction** ev = |mean_s X_s[6]|^2 / mean_s |X_s[6]|^2
  (L162 I5 form), per channel per arm.

## Registered branches (the card's two, plus the two failure modes)

Read on the **rnd** arm, CARRIER channels / CARRIER pairs, medians:

- **B_SHARED** (one clock): median carrier PLV_self < 0.4 AND median
  carrier pair PLV >= 0.8.
- **B_INDEPENDENT**: median carrier PLV_self < 0.4 AND median carrier
  pair PLV < 0.8 — the .100 Hz line is protocol-driven per pool and the
  aggregate coherence was an aggregation emergent.
- **B_NOT_FREED**: median carrier PLV_self >= 0.4 on rnd — the
  injection did not free the pools' phase even though it freed the
  drive's (reported as an instrument/propagation result, NOT a clock
  verdict).
- **B_MIXED**: anything else; name the coherent subset.

Positive control (must hold or the whole read is void): median carrier
PLV_self on the **fix** arm >= 0.8, reproducing L162's .962-.997 on
fresh seeds. Negative arm: the 9 CONTROL (dead-pool) channels and their
36 pairs are reported beside the carriers on both arms; no registered
threshold counts them (L162 ADDENDUM 1 rule).

One object per gate cell (L109): the PLV_self cell and the pair-PLV
cell are reported separately and never ANDed into a single branch word
without both numbers printed.

## CERT chain (halting, before any arm is read)

- **CERT-A analytic** (l162c CERT-6 VERBATIM): PLV_self of a pinned
  0.1 Hz ensemble > 0.999; of a uniform-offset ensemble < 0.05.
- **C0A-164 bit-identity**: the **fix** arm at seeds 801/901 must
  reproduce `l150/raw_l150.npz` stored `b65` traces for all 22 channels
  to **max|d| = 0.0**, and af to float equality. This proves the
  re-implementation (trimmed extraction, new drive code at o_s = 0) is
  the stored protocol and not a look-alike.
- **CERT-sets**: CARRIER/CONTROL derived from l157/static.json, len
  8 / 9, disjoint.
- **CERT-bin**: |rfftfreq(6000,.01)[6] - 0.1| < 1e-12.
- **B42 absence**: no stored npz under banc/ contains `mm_b65_42xx`.
- **op point** (L30): af in (0.01, 0.9) asserted per seed per arm, and
  the fix-arm af medians reported against l150's stored b65 band.

## Outputs

`l164/drive_static.json` (pre-measurement), `l164/raw_l164.npz`
(checkpointed the moment the rollouts finish, L43), `l164/results.json`
(per-channel PLV_self + ev tables, per-pair PLV tables, branch verdict),
`l164/run.out`. No live changes, no draft edit, sessions/ untouched.
