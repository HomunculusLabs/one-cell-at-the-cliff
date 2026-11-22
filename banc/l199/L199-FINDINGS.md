# L199 FINDINGS — the tone-phase registered test (FINAL)

**Registered verdicts.** Part A (3-bin conditioned profile, stored raws): **`PH1_sign`** — S `PH1_sign`, L186 `PH1_sign`, W `PH_weak` (direction only, no reversal). Part D (causal, 64 fresh rollouts): **`CA1`** — the phenotype follows the tone phase; the sign refinement `CA1_sign` is NOT met. Part B (signed-offset profile, new instrument): S `Hq`, W `Hq`, L186 `H1`. Part C (direct pool phase): S `Dq`, W `Dq`, L186 `D1`.
PREREG sha 01e23ae1c711012e, frozen 20:27:51 before any L199 statistic or rollout; every frozen file still hashes to FREEZE.json; no post-freeze code change. Certs: CERT-197b (this instrument reproduces L197b's stored I, A_inphase, A_antiphase, pooled A with intervals and all six addendum bin means, 1e-12); C0A unshifted cutwA + sc25 @801/901 == raw_l135 EXACT in all 3 workers (276 checks, max 0.0); both gains == stored floats EXACT x3; all 32 gates canonical; manipulation check tone(phi0) + tone(phiPI) == ENT_AMP x gate, max deviation 5.6e-16; fresh seeds 19931..19946 (+ tags 69931..69946) key-scanned against 268 npz.

## Part A — the brief's instrument (in / mid / antiphase bins of each pair-segment's own tone offset)

| | S (96 seeds, W150) | W (96 seeds, 250-step pulse) | L186 (16 seeds, W150) |
|---|---|---|---|
| base duty in / mid / anti | .186 / .236 / .465 | .113 / .169 / .329 | .190 / .257 / .413 |
| carrier removed in / mid / anti | .423 / .299 / .298 | .232 / .239 / .342 | .493 / .320 / .250 |
| base slope (in − anti) | −.278 [−.308, −.249] | −.216 [−.251, −.182] | −.223 [−.340, −.106] |
| removed slope | **+.125 [+.075, +.176]** | −.110 [−.160, −.060] | **+.243 [+.121, +.366]** |
| interaction I | +.403 [+.345, +.462] | +.106 [+.044, +.169] | +.466 [+.274, +.658] |
| pooled elevation | +.049 | +.068 | +.083 |
| label | PH1_sign | PH_weak | PH1_sign |

What this adds over L197b, and what it does not: S's and W's interaction and point profiles were already known (PREREG §"already seen"); W's label was fixed by a stored number. New here: the intervals on the per-graph sign claims (S's removed slope excludes 0), L186's per-graph profile (a second batch with the reversal), and W's removed slope being NEGATIVE with an interval below 0 — under the 250-step pulse the profile shifts but does not reverse.

## Part D — the causal version (same gates, tone shifted half a period in one arm)

Same 16 seeds, same settle state, same noise, canonical gate in all four arms; the only difference between a same-phase pair and a cross-phase pair is the tone.

| duty (W150, distinct seeds) | phi0–phi0 | phiPI–phiPI | cross |
|---|---|---|---|
| base (cutwA) | .175 | .210 | .505 / .483 |
| carrier removed (sc25) | .372 | .469 | .300 / .349 |
| elevation sc25 − cutwA | **+.197 [+.108, +.286]** | **+.258 [+.159, +.357]** | **−.170 [−.220, −.119]** |

- K (within − cross): base **−.301 [−.356, −.246]**; removed +.096 [−.002, +.194]; **K_I +.397 [+.288, +.506]** (S's correlational I was +.403).
- The elevation reappears when BOTH partners are shifted (E_PP − E_00 +.061 [−.067, +.189]) and inverts when only one is. A gate-edge-locked timing predicts no difference between these classes; the gates are identical.
- `CA1_sign` fails on one condition: the removed graph's K interval touches 0 at the 150-step window. At v1's 500-step window (descriptive) it is +.245 [+.110, +.381] and K_I +.492 [+.358, +.626].
- Pool peaks move with the tone: phiPI − phi0 peak phase against the unshifted tone +157 / −172 (base flexor / extensor), +167 / −164 (removed).

## Parts B and C — what the phase relation actually is (the correction to the post hoc)

| | S | W | L186 | Part D batch (phi0 / phiPI) |
|---|---|---|---|---|
| B: preferred offset theta, base | +172 (SE 4) | +173 (SE 5) | +169 (SE 12) | — |
| B: theta, carrier removed | **+55 (SE 5)** | +134 (SE 9) | +32 (SE 10) | — |
| B: rotation dtheta | **−118 [−131, −104]** | −39 [−59, −20] | −136 [−173, −99] | — |
| C: flexor − extensor peak phase, base | −5 (R .77) | +5 (R .68) | −7 (R .74) | +10 / −22 |
| C: same, carrier removed | **−116 (R .77)** | −76 (R .49, dispersed) | −129 (R .80) | −94 / −126 |

1. **"Co-move" holds for the base graph everywhere**: flexor and extensor peak at the same tone phase (within ±22 deg in five batches), and the cross-seed anticorrelation peaks at a half-period offset (theta 169–173).
2. **"Alternate" is too strong for the carrier-removed graph.** The pools do not go to antiphase. Their relation rotates by about a third of a period: −116 (S), −129 (L186), −94 / −126 (fresh batch) — between quadrature and antiphase. The folded 3-bin profile reads this as a sign reversal because cos is positive there; the signed instrument puts S's preferred offset at +55 [+44, +65], outside the registered 0 ± 45 band (`Hq`). L186 lands inside it (`H1`, +32, wide interval). The two instruments agree: theta − 180 = −125 vs direct −116 in S.
3. **It is the extensor that moves (descriptive, no registered band).** Flexor peak tone phase: 102 → 93 (S), 102 → 92 (L186). Extensor: 108 → −150 (S), 110 → −137 (L186), 109 → −172 (fresh phi0), and its locking loosens (R .95 → .70–.82).
4. **Under the 250-step pulse (W) the rotation is a third the size** (−39 deg; direct phase dispersed, R .49). Design-dependent, as L197b already reported for the elevation.

## Predictions

Correct: Q1; Q2 (all three); Q3; Q4 (I, base slope; label was a coin flip between sign and shape); Q5's base-near-180 and W-not-H1; Q6 (base co-move everywhere; S removed = intermediate, my modal call); Q7 certs, base K, CA1, E_PP. Wrong: Q5's "theta_sc25 within 0 ± 45 in S" (.55) and its modal label H1 (.50) — S is Hq.

## Limits

- Part A on S and W is a formalised re-read of partly seen data; the out-of-sample weight is L186's per-graph profile, Parts B–C (never computed before) and Part D.
- Part D is one 16-seed batch, one shift (half a period), canonical schedule; it shifts the whole-window tone and so does not separate tone phase at gate onset from tone phase during the pulse (phiPI's own elevation runs higher than phi0's, +.061, interval spans 0).
- Cross-seed duty of the right tibia pair, one model class, AF-matched gains. First-harmonic phases are of rate traces, not synaptic latencies.

## Draft-fold note (NOT applied — for a gated fold card)

- §2.5 "Which clock the timing follows is unresolved" (DRAFT.md ~l.1272; echoed ~l.599, ~l.629, abstract note ~l.493) can now read: **"no internal rhythm; the timing locks to the phase of the external 0.7-Hz tone"** — cite L197b items 3–4 (partner-undriven elapsed elevation +.010 [−.013, +.034] / +.015 [−.007, +.036]; elevation signed by tone phase) and L199 Part D (tone shifted half a period at identical gates: elevation +.197 / +.258 same-phase, −.170 cross-phase; K_I +.397 [+.288, +.506]).
- Supported phenotype sentence: "removing the carrier rotates the extensor's phase against the tone by about a third of a period while the flexor's is unchanged; the base pools peak together." Do NOT write "alternate" or "antiphase" for the carrier-removed graph.
- Scope words that must travel with it: 500-step pulse; weaker and non-reversing under a 250-step pulse.

**Next (cards, not run):** (i) a tone-RESET arm (tone phase restarted at each gate onset) to split onset phase from in-pulse phase; (ii) a graded shift (quarter / three-quarter period) to trace the profile causally and test the −120 deg reading directly; (iii) why the extensor: which input sets its tone phase once the carrier is gone.

Files: `PREREG.md` + `PREREG.sha256` + `FREEZE.json`, `ph.py`, `selftest.py/.json`, `analyze_primary.py` → `results_primary.json`, `primary.out`, `segduty_{S,W,V1}.npz`; `build_tp.py` → `run_tp.py`, `run_all.sh`, `raw_w0-2.npz`, `xm_w0-2.npz`, `analyze_causal.py` → `results_causal.json`, `causal.out`, `segduty_causal.npz`; `verdict.out`. Rollouts 20:27–20:34, 3 workers × 2 threads, CPU only, concurrent with L200.
