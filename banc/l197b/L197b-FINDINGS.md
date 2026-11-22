# L197b FINDINGS — gate-jitter v2, the discriminator with power (n = 96 seeds per design arm, FINAL)

**Registered verdict: `NO_VOTE`** — both design arms carry the `R0_no_elevation` flag (pooled deletion elevation < .15 on BOTH clocks at these resolutions), so by PREREG no clock branch is read. Beside the flag, the clock class is **`E3_equal_resolved` in both arms**: the aligned − elapsed difference D is now pinned inside ±.10 (half-width .027 / .028; v1's was .141). **Mechanism panel (registered secondary): S = `M_tone`, W = `M_unassigned` (same direction, under the bar); no `M_internal` in either arm.**
PREREG sha 86a2a99515383ed6, frozen 18:56:01 before any v2 rollout. Certs green: C0A unjittered cutwA + sc25 @801/901 == raw_l135 EXACT in all 6 workers (552 checks, max 0.0); both gains == stored floats EXACT ×6; every stored gate array == the registered schedule; overlap gate from the drawn schedule S .228 / W .230 (≤ .25); CERT-V1 (the generalised readout reproduces `results_l186.json` to 1e-12); 192 fresh seeds key-scanned against 254 npz.

| | S: v1 schedule, 150-step window | W: 250-step pulse, band 1000, 250-step window |
|---|---|---|
| duty aligned / elapsed / same-seed, base | .281 / .229 / .334 | .195 / .186 / .305 |
| same, carrier removed | .330 / .334 / .585 | .263 / .213 / .425 |
| **A** aligned elevation | +.049 [+.037, +.061] | +.068 [+.045, +.090] |
| **T** elapsed elevation | +.105 [+.080, +.130] | +.027 [+.008, +.047] |
| **D = A − T** | **−.056 [−.082, −.029]** | **+.040 [+.012, +.068]** |
| T_on (partner driven) / share of windows | +.167 [+.134, +.199] / .61 | +.070 [+.038, +.101] / .24 |
| T_off (partner undriven) | +.010 [−.013, +.034] | +.015 [−.007, +.036] |
| A, tone in phase / antiphase | +.237 [+.202, +.272] / −.166 [−.196, −.136] | +.119 [+.077, +.161] / +.013 [−.028, +.054] |
| in-phase − antiphase | **+.403 [+.345, +.462]** | +.106 [+.044, +.169] |
| card's tone instrument verbatim, rho (sc25 / base) | +.015 / −.006 | −.023 / −.006 |
| same statistic at pair-SEGMENT level | +.216 / −.475 | −.136 / −.315 |

## What was measured

1. **Neither clock wins, and that is now a resolved statement.** D is −.056 in S and +.040 in W — opposite signs, both intervals inside ±.10, both excluding the registered ±.10 margin for E1 / E2. v1 could not say this (D −.015 [−.156, +.126], power .28 for a .10 difference; here ≥ .92 by the registered analysis, realised half-width .03).
2. **The pooled elevation is small at fine resolution because it is signed by tone phase, not because it is absent.** In S the carrier-removal elevation is +.237 for pair-segments whose gate lag leaves the 0.7-Hz tone in phase and −.166 for those it puts in antiphase; pooled over all rotations they cancel to +.049. The same-seed elevation is intact (+.251 in S, +.120 in W).
3. **No internal rhythm.** With the partner seed undriven the elapsed-clock elevation is +.010 [−.013, +.034] (S) and +.015 [−.007, +.036] (W): upper bounds a quarter of the .15 bar. The elapsed-clock elevation lives entirely in windows where both seeds are being driven (T_on).
4. **The dichotomy the card inherited was mis-posed.** The external tone runs on elapsed time while a gate is open, so "elapsed" was never the internal-rhythm pole. The shared timing is locked to the external tone's phase during drive: not to the gate edge (that would give an elevation at every rotation — antiphase is −.166 / +.013), and not to a free-running clock (item 3).
5. **Tick 216's "tone confound cleared" does not stand.** The card's instrument, carried verbatim, again reads "not predictive" (|rho| ≤ .023, all four cells) — because it rotates the MEAN of the two outer segments' independent lags, which carries no phase information. At pair-segment level the same statistic is −.475 / +.216 (S) and −.315 / −.136 (W).
6. **Arm W: the phenotype is weaker under a 250-step pulse** (same-seed elevation +.120 vs +.251), and the tone split shrinks with it (+.106, CI above 0, under the registered .15 bar → `M_unassigned`). S and W are two designs, not replicates.

## Post hoc (`addendum.py`, zero rollouts, written after the verdict was read)

- **v1's own readout (500-step window) on S's 96 fresh seeds** — S uses v1's schedule law, so this is L186 as run, six times over: A +.222 [+.192, +.252], T +.225 [+.194, +.257], D −.003 [−.031, +.024]; in phase +.469, antiphase −.033. v1's elevation replicates at its own resolution, and D is zero there too.
- **Which graph carries the split (S, aligned duty in phase / mid / antiphase):** base .186 / .236 / **.465**; carrier removed **.423** / .299 / .298. On the base graph the cross-seed flexor-extensor anticorrelation appears mostly when the partner is rotated half a tone period — the two pools move TOGETHER relative to the tone; with the carrier removed it appears at zero rotation — they alternate. Read that way the deletion phenotype is a change in the pools' phase relation to the external tone. One batch, post hoc: a hypothesis for a registered test, not a result.

## Deviations (declared)

- Card (i) amended before freeze: its "jitter ≥ 1000 with the 500-step window" cannot pass its own .25 overlap gate (.417; passing needs a 1824-step band, which does not fit); pulse and window shortened to 250 steps (PREREG §Design).
- One post-freeze plumbing fix in `analyze_v2.py`: the schedule stores onsets relative to each segment, the readout takes absolute steps. The frozen script stopped on its own bounds assert before computing any v2 statistic; fix = one conversion + a gate-position assert; frozen original kept as `analyze_v2.frozen.py`; `gj.py` (the readout) untouched, sha-asserted.
- The v1-data pilot (and its tone-split observation) was seen before registration and is disclosed in the PREREG; the fresh batch confirms it in S on 96 new seeds.

## What it would change (nothing edited)

- The draft may keep "the carrier-removal elevation survives independently jittered gate onsets" (replicated: +.22 on either clock, 96 seeds, v1's window).
- Withdraw "the cross-seed structure is not locked to the shared elapsed-time tone". Supported wording: "the shared timing follows the phase of the external 0.7-Hz drive while the pools are driven; it does not persist on elapsed time when the partner is undriven, and it is not carried by the gate edge."
- No internal-rhythm claim (E2) is available from this design or v1's.

**Next.** (i) registered test of the co-active → alternating reading: per-seed phase of each pool against the tone, base vs carrier-removed (stored traces, zero rollouts); (ii) a tone-RESET design (tone phase restarted at each gate onset) is the only way to separate gate from tone experimentally.

**Predictions.** Correct: P1; P2 (S: R0 flag, E3_equal_resolved, D in (−.10, 0)); P3's class and sign for W; P5 no internal rhythm; P7 half-widths. Wrong: P3's "A ≥ .10 in W" (+.068); P4 (M_tone in both — W fell under the bar); P6 (segment-level rho for sc25 +.216, I registered > +.25; the verbatim-instrument half held).

Files: `results_l197b.json`, `verdict.out`, `addendum.py/.json/.out`, `pairmat_S.npz`, `pairmat_W.npz`, `schedule.json`, `pilot.json`, `PREREG.md` + `PREREG.sha256` + `FREEZE.json`, `gj.py`, `build_v2.py` → `run_v2.py`, `analyze_v2.py` (+ `.frozen.py`), `run_all.sh`, `raw_w0-5.npz`, `xm_w0-5.npz`. Rollouts 19:06-19:24, 6 workers × 2 threads, CPU only, after L198 FINAL.
