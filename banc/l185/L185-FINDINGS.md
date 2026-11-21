# L185 FINDINGS — fresh-batch replication + gain-only null + signed-current twin (batch 3577-3592, n=16 every arm, FINAL)

**Branches fired: R1 `REP_D2` · gain form `GAIN_ROBUST` · R2 `GAIN_SENSITIVE_NEGATIVE` · R3 `S2_NO_FLIP` → `D2_hardened` = true.**
PREREG sha256 f1f7150240e629f5, registered 11:57 before any rollout; R3 pick computed after it, before any rollout; all 13 pinned script/static shas unchanged at the end (`PREREG.sha256`). Rollouts 11:58-12:15 (17 min, 6 workers x 2 threads, CPU).
Certs green: stored-form bisect re-run in every worker == stored floats EXACT (g_cutwA x6 + all six L175 gains); C0A vs `raw_l135` 368 checks max 0.0; one stored B39 seed (3545) re-rolled for base + six arms vs the L175 raws, 300 checks max 0.0; cutwA identical across workers (2185); generic base alias `g000` == cutwA on all 19 seeds (437); metric reproduces `results_l135` AND the stored `results_l175` rows EXACT.

## R1 — what replicated (rematched = L175's stored re-bisected gain; fixed = base gain g_cutwA)

| arm | gi | re-bisect shift | rematched kR, meanR, class | fixed kR, meanR, class | fixed − rematched (paired) | B39 | pooled B39+B40 |
|---|---|---|---|---|---|---|---|
| cutwA (base) | - | 0 | 3/16 .370 not (partial) | same arm | - | 5/16 .408 | 8/32 |
| sc25 carrier | 1110 | +1.24% | **15/16 .770 SUPER** | **15/16 .683 SUPER** | -.088 (t -1.9) | 16/16 .758 | **31/32 .764 SUPER** |
| sc26 mass twin | 319 | -0.09% | 4/16 .424 not (partial) | 4/16 .390 not (partial) | -.034 | 2/16 .378 | 6/32 .401 |
| sc27 boundary | 707 | -0.28% | 4/16 .422 not (partial) | 7/16 .424 not (partial) | +.001 | 11/16 .596 | 15/32 .509 interm. |
| sc40 boundary | 559 | -1.13% | 12/16 .538 interm. | 3/16 .341 not | **-.198 (t -3.1, 0 up / 8 down)** | 11/16 .605 | 23/32 .572 interm. |
| dmA drive twin | 511 | +0.11% | 5/16 .406 not (partial) | 8/16 .478 not (partial) | +.073 | 5/16 .390 | 10/32 .398 |
| dmC drive twin | 1480 | +3.31% | 2/16 .382 not | 2/16 .409 not | +.027 | 2/16 .366 | 4/32 .374 |

- **The carrier flip replicates** on a fresh batch (Wilson lb .717) and **does not depend on the gain re-match**: at the base's own gain it is still 15/16, +.312 over the same-gain base (t 4.8, 11 seeds up >= .20, 0 down).
- **All three twins and the base stay in the strict NOT-SUPER band**, in both gain forms.
- **Neither boundary cell promotes.** sc27 regressed to the null (11/16 -> 4/16). sc40 stays elevated under its re-bisected gain (12/16, but meanR .538 < .60, so INTERMEDIATE on both batches and pooled) and **loses the elevation entirely at fixed gain** (3/16, -.030 vs base): it is what its -1.13% gain shift produces, not a deletion effect.

## R2 — gain-only null (base graph, no deletion)

| gain shift | -0.50% | -0.25% | 0 | +0.25% | +0.50% |
|---|---|---|---|---|---|
| kR / 16 | 8 | 8 | 3 | 2 | 3 |
| meanR | .470 | .474 | .370 | .311 | .266 |

- **Slope = -0.0228 meanR per +0.1% gain** (SE .0062, 95% CI [-.036, -.0095]; 13/16 seeds negative; kR-rate slope -.040 per +0.1%). A 1% gain span moves the base from 8/16 to 2-3/16 with no cell removed. No gain-only arm is SUPER (max 8/16, .474).
- It is 0.76x the L175 scan's cross-arm slope (-.0299, arms within +-.5%) and reproduces R² = .36 of those 25 arms' meanR spread (.45 for the 18 silent cells). So roughly a third to a half of the scan's null spread is pure gain sensitivity; the remainder is not attributed here (the next point is a candidate).
- Pairing is void off the exact gain: per-seed duty of the shifted arms correlates with the same-seed base at r = -.22 to +.24 (paired-difference sd .26-.31 vs between-seed sd .15-.21). "Same-seed" contrasts carry no variance reduction once the gain or graph changes.
- The carrier runs against this: +1.24% gain should lower duty, and it is the highest arm.

## R3 — signed-current-matched twin

- Registered current (PREREG §R3): J = g·x̄·(direct + g·gated one-relay) onto the right-tibia flexor / extensor pools. Carrier: **(-0.00214, 0)** — zero direct input, a small net-inhibitory relayed current onto the flexors (~1/10 of the background term .02).
- **The astra's loophole was real:** L175's drive twins do not match it — dmA delivers (0, 0) (dist_rel 1.00, rank 212 of 4,751), dmC (0, -0.0115) onto the extensors (dist_rel 5.5, rank 4,339).
- Pick (rule frozen before selection): **gi 1508, DNg19-R**, descending, excitatory like the carrier, J = (-0.002145, 0), **dist_rel .003**, unsigned drive x1.40. Brute-force path recount agrees.
- **It does not flip: 2/16, meanR .345, NOT-SUPER** (Wilson ub .36; -.025 vs base), at a re-bisected gain of -0.31% — a shift that by R2 alone pushes duty up.

## Caveats (they bound how hard this can be leaned on)

1. R3 is one batch and one definition. The match holds under the registered linear-regime gate (and with the lower gate alone, .003) but not ungated (dist_rel 20.4). The pick is rail-saturated (x̄ .997) and is a DN with cord input, not a pure projector like the carrier. It matches a time-averaged, linearized, path-length <= 2 current — not phase, not longer paths.
2. sc40 is not a clean null: 23/32 pooled under its own re-bisected gain. The fixed-gain arm explains it, on one batch.
3. P5 failed: fixed − rematched did not follow the base's gain slope on the deletion graphs (carrier -.088 where +.28 was implied; sc27 0). Gain dependence is graph-specific; R2's slope should not be extrapolated across arms or beyond +-.5% (the all-arm extrapolation fits worse than no model).
4. Chopped 0.7-Hz right-tibia classifier only; one base (k=24); one model class.
5. Process: partial verdicts (m = 6, 7, 13) were printed while workers ran; code and bands were frozen and hashed first, nothing was changed. The results json was refreshed per completed seed by the orchestrator (20 s poll), not by the workers.

## What it changes

Keep "identity". The contrast now stands on two batches (carrier 31/32; mass twin 6/32; two unsigned drive twins 10/32 and 4/32), on both gain forms, plus one signed-current twin (2/16). Honest wording: "cell identity, not removal mass, delivered drive, or signed current onto the right tibia (<= 2 synapses)". Add to Methods/Limitations: the base's duty moves -.023 per +0.1% gain, so any non-carrier elevation that rides a re-bisected gain shift needs its fixed-gain arm (sc40 is the worked example).

**Predictions:** 8 of 9 correct (P1 carrier SUPER, P2 twins/base not, P3 no promotion, P4 carrier SUPER at fixed gain, P6, P7 slope -.0228 inside [-.050, -.010], P8, P9); P5 wrong (2 of 4 signs).
**Next:** (i) second batch for s2t; (ii) a gain sweep ON the carrier-deleted graph (P5's miss says its gain curve differs); (iii) the unchopped panel on these raws (zero rollouts).

Files: `PREREG.md`, `PREREG.sha256`, `build_rep.py` -> `rep_run.py`, `build_verdict.py` -> `verdict_l185.py`, `run_all.sh`, `static.json`, `selection_s2.json`, `results_l185.json`, `verdict.out`, `run.out`, raws `raw_w0..5.npz` (w0 sc25 + base, w4 dmA, w5 dmC + s2t; every arm kept) + `xm_w*.npz`.
