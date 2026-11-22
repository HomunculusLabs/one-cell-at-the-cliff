# L202 FINDINGS — ru2-necessity replicate, bilateral twin, activity vs presence, chain batches (B45 3737-3752, n=16 every arm, FINAL)

**Registered labels: W = `W1_wipe_replicates` in BOTH gain forms (AGREE) · T = `T1_bilateral_specific` (READ; lt4 and lt5 both no flip) · N = `N3_partial` (re-matched `band`, fixed `signature_only`; gain form DEPENDENT — neither registered pole) · S = `S_partial` (both forms) · C: edge `B3-partial` and sham `B2-edge-inert` replicate, rcut / rcutF do NOT re-class SUPER.** No unregistered shape.

PREREG sha 626be3aa86b63f75 frozen 15:40:16 before the harness was written; FREEZE 15:45:50 before any rollout; all 12 frozen files re-hash unchanged after the run. Certs green: C0A cutwA == raw_l135 EXACT in all 4 workers (230 checks) + vs L175 @3545 (125) + L187 @3609 incl. rcut / rcutF (220) + **L190 @3641 incl. my re-built edge / sham arms (202)** + L198 @3673 (266) + **L200 @3705 incl. sc25, l2c, l2cF, l2 — the wipe's own source arms (258)**, all max 0.0; seven stored gains reproduced EXACT (cutwA ×4, sc25 ×2, l2c, l2, rcut, edge, sham); CERT-X 1518 checks 0.0; CERT-REPLAY (clamped ru2 trace == base's, 34 in-run + 32 verdict) 0.0; CERT-NULL (ru2 replayed onto the base == base, 48) 0.0; metric reproduces five stored L200 rows EXACT; independent re-derivation of every per-seed duty with separate code (816 values) max diff 0.0.

| arm | removed / transform | gain d% | RIGHT k | meanR | class | dR vs base [95% CI] | R 1.4-Hz mean (k) | LEFT k / mean |
|---|---|---|---|---|---|---|---|---|
| cutwA | — (base) | 0 | 5 | .417 | NOT-SUPER | — | .000 (0) | 2 / .284 |
| **sc25 / sc25F** | carrier 1110 | +1.244 / 0 | 16 / 14 | .810 / .689 | SUPER / SUPER | +.394 [+.285, +.502] / +.272 [+.139, +.406] | .562 (7) / .366 (4) | 0 / .180 · 0 / .269 |
| **l2c / l2cF** | carrier + ru2 70994 | −0.644 / 0 | 1 / 2 | .351 / .329 | NOT / NOT | −.065 [−.158, +.028] / −.088 [−.220, +.044] | **.000 (0) / .000 (0)** | 16 / .952 · 16 / .950 |
| **s2k / s2kF** | carrier removed, ru2 replay-clamped at base trajectory | +1.244 / 0 | 7 / 6 | .502 / .419 | INTERMEDIATE / NOT | +.085 [+.006, +.164] / +.003 [−.090, +.095] | .212 (3) / .402 (7) | 1 / .300 · 4 / .339 |
| l2 | ru2 | −0.300 | 11 | .548 | INTERMEDIATE | +.132 [+.022, +.242] | .000 | **16 / .870** |
| **lt4 / lt4F** | bilateral twin 67125 | +0.958 / 0 | 0 / 3 | .182 / .328 | NOT / NOT | −.235 [−.331, −.140] / −.089 [−.185, +.008] | .110 / .018 | **1 / .200 · 0 / .190** |
| lt5 | bilateral twin 67756 | −0.006 | 4 | .359 | NOT | −.058 [−.170, +.054] | .000 | **0 / .205** |
| t4c / t4cF | carrier + twin 67125 | +2.230 / 0 | 12 / 8 | .588 / .521 | INTERMEDIATE / INTERMEDIATE | +.172 [+.062, +.281] / +.104 [−.035, +.243] | **.860 (15) / .678 (13)** | 0 / .207 · 0 / .209 |
| rcut / rcutF | relay 75494 | −0.126 / 0 | 10 / 11 | .516 / .539 | INTERMEDIATE / INTERMEDIATE | +.100 [−.056, +.255] / +.122 [+.000, +.244] | .000 / .000 | 1 / .298 · 0 / .252 |
| edge | edge 1110→75494 only | −0.358 | 14 | .618 | SUPER | +.201 [+.105, +.297] | .000 | 2 / .337 |
| sham | edge 48→75494 only | −0.001 | 6 | .481 | NOT | +.065 [−.041, +.170] | .005 | 1 / .268 |

## What was measured

1. **The wipe replicates, with its fixed-gain comparator.** Re-matched: l2c − sc25 = −.459 [−.553, −.365], 16/16 seeds lower; 1.4-Hz .562 → .000 (−.562 [−.731, −.394]). Fixed gain, same batch (the comparator L200 owed): l2cF − sc25F = −.360 [−.473, −.248], 15/16 lower; 1.4-Hz .366 → .000. Pooled with L200's batch: −.473 [−.539, −.407], **32/32 seeds lower**; the 1.4-Hz duty is exactly .000 in every double-removal seed of both batches and both gain forms (64 rollouts). The left flip is untouched (16/16 .952).
2. **Neither bilateral twin flips the left tibia.** lt4 1/16 .200 (fixed 0/16 .190), lt5 0/16 .205, against ru2's 16/16 .870 on the same seeds (lt4 − l2 = −.670 [−.749, −.592]; lt5 − l2 = −.665 [−.723, −.607]). With L200's two: 0 of 4 left-drive-matched cells, two of them matched on ru2's bilateral shape. Pooled ru2 left flip: 48/48 seeds, mean .851, three batches.
3. **Activity vs presence: neither pole.** With ru2 present and wired but held on its base trajectory, the chopped rise is mostly lost — s2k − sc25 = −.309 [−.383, −.235], 16/16 lower (fixed −.270 [−.384, −.155]); retained fraction .33 (fixed .25) — yet it stays above the cut, +.150 [+.064, +.236] (fixed +.091 [−.042, +.223], not resolved). The 1.4-Hz signature survives the clamp where it never survives the cut: .212 re-matched (retained .38, under the .25 bar), .402 at base gain (retained 1.10, over the bar; vs the cut +.402 [+.235, +.568], 13 seeds up, 0 down). So the signature needs ru2 there and emitting; the chopped-duty rise needs ru2 free to respond.
4. **The twin does not reproduce the wipe, and does not land on S1 either.** Carrier + twin 67125: right 12/16 .588 (misses SUPER on the mean leg by .012), above the ru2 double removal by +.237 [+.118, +.356], below carrier removal by −.222 [−.350, −.093]; fixed 8/16 .521. Its 1.4-Hz signature is the strongest in the table: .860, 15/16 seeds (fixed .678, 13/16) — higher than carrier removal alone (+.298 [+.154, +.441]).
5. **Chain batches.** Single-edge cut: SUPER again (14/16 .618, +.201 [+.105, +.297], no signature) — two batches pooled 26/32, +.212 [+.132, +.293]. Sham: base-like again (+.065 [−.041, +.170]; pooled +.042 [−.031, +.116]); edge − sham same seeds +.136 [+.048, +.225]. Relay removal: INTERMEDIATE in both gain forms on this batch, re-matched CI spanning 0. Three batches: rcut SUPER / INTERMEDIATE / INTERMEDIATE, 35/48, +.216 [+.139, +.294]; rcutF SUPER / SUPER / INTERMEDIATE, 38/48, +.221 [+.158, +.283].

## Reading

Supported: the carrier-removal right-side regime (chopped rise and 1.4-Hz signature) requires ru2 — registered, two batches, both gain forms, every seed. Supported: among four left-drive-matched cells, only ru2 flips the left tibia. Not supported as either registered pole: "presence is enough" or "needs ru2's free activity" — the two readouts split. In this model class a cell acts only through its rate (a cell held at 0 from t = 0 IS the cut graph, L187), so "wiring without activity" is the cut; what the clamp adds is that base-level output keeps the signature alive but not the chopped rise.

## Caveats

- **N is one batch and gain-form dependent.** The re-matched signature (.212, 3 seeds ≥ .5) sits just under the bar and the fixed one (.402) over it; a second batch can move either label.
- **The clamp cannot separate ru2's mean rate from its timing — but the post hoc numbers point at timing** (`addendum.py`, descriptive): ru2's free trajectory under carrier removal correlates only r ≈ .32 with the base trajectory replayed (range .18–.54), while its mean moves +.025 re-matched and −.018 at base gain. Opposite-signed mean shifts, same loss of the chopped rise.
- **S is one twin, one batch.** The twin is not inert on the right (alone: 0/16 .182, −.235 [−.331, −.140] re-matched; fixed −.089, n.s.) and t4c re-bisects by +2.23%, the largest shift here, so its chopped shortfall against sc25 mixes the twin's own effect with gain. It carries 29% of ru2's total drive. "Specific to ru2" is bounded by one control.
- **Double removal vs base is not resolved on this batch** (−.065 [−.158, +.028]; L200 −.135 [−.244, −.025]; pooled −.100 [−.169, −.031]). The wipe is a return to roughly base level, not clearly below it.
- **The relay's SUPER label is not stable across batches**; its pooled effect is. On this batch the single-edge cut reads at least as high as removing the whole relay (edge − rcut not registered; descriptive).
- edge / sham still have no fixed-gain twin (not rolled: slot budget at 4 CPU). The clamp holds one cell's output and says nothing about which downstream route carries the dependence. One model class, one base (k=24), chopped 0.7-Hz classifier + 1.4-Hz panel.
- A second, unrelated 4-process run (`duckroute`, not this card's) shared the machine throughout; every bit-identity anchor held, so it cost wall time only.

## What it would change (nothing edited)

- L200 item 6 can be stated as a registered result: carrier-removal phenotype abolished without ru2, 32/32 seeds, both gain forms, signature .57 → .000.
- "ru2 unique" becomes "0 of 4 matched cells, two bilateral" — still a bound, not a census.
- Relay: quote the pooled effect (+.22, three batches), not a class. Edge cut: two batches, SUPER both times, no signature.
- `paper/figures/fig6` holds an L202 slot marked pending and is built to fail loudly once `results_l202.json` exists; that rebuild belongs to the figure lane.

**Next.** (i) N second batch plus the control that splits mean from timing: ru2 clamped to a CONSTANT at its base window mean, and ru2 replayed from a different seed's base rollout. (ii) Two more bilateral twins as carrier double removals, second batch for t4c. (iii) Fixed-gain edge / sham.

**Predictions.** Held: P1 (W1 both forms, all 16 seeds lower, signature ≤ .10), P2 (controls, both forms), P3 (lt4 and lt5 NOT-SUPER), P4 (l2 and l2c left SUPER), P8 (edge B3, sham B2). Wrong: P5 (modal N1 at .50; got N3, which I gave .30), P6 (modal S1 at .65; got S_partial, .20), P7 (rcut .70 and rcutF .60 SUPER; both INTERMEDIATE).

Files: `results_l202.json`, `verdict.out`, `addendum.py/.json/.out`, `static.json`, `raw_w0-3.npz`, `xm_w0-3.npz`, `anchors_w0-3.json`, `gains_w0-3.json`, `done_w0-3.json`, `PREREG.md` + `PREREG.sha256` + `FREEZE.json`, scripts `ref_probe.py`, `build_nec.py` → `nec_run.py`, `build_verdict.py` → `verdict_l202.py`, `run_all.sh`. Wall 15:35 → 16:18 (rollouts 15:46–16:13, 4 workers × 1 thread, CPU only).
