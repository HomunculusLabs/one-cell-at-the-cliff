# L200 FINDINGS — the ru2 left-tibia phenotype (B44 3705-3720, n=16 every arm, FINAL)

**Registered branch: M = `M1_unique_no_left_signature`, status READ, gain forms AGREE on every arm.** ru2's left flip replicates, neither left-drive-matched twin shows it, it does not route through the carrier (it survives the carrier held at base and the carrier removed) — and it carries no left 1.4-Hz signature, so the full "mirror-carrier" branch M1 is NOT met. A4 (wiring): `A4_no_laterality_contrast`. M2 and M3 are rejected by their registered tests.

ru2 = **gi 70994, IN07B031-R, inhibitory cord interneuron** (re-derived from `l198/selection.json`; the brief's gi 67353 is ru4).
PREREG stage 1 sha db03c33d5997bc51 frozen 20:26:14 before the selection / wiring code was written; selection + A4 + FREEZE 20:30:44 before any rollout. Certs green: C0A cutwA == raw_l135 EXACT in all 6 workers (322 checks) + vs L175 @3545 (175) + vs L187 @3609 (195) + **vs L198 @3673 incl. the stored ru2 arm itself (239)**, all max 0.0; g_cutwA ×6 / g_sc25 / g_l2 ×2 == stored floats EXACT; CERT-X 2310 checks 0.0; CERT-SUB on four new graphs; CERT-REPLAY (clamped carrier trace == base's, 34 in-run + 32 verdict checks, 0.0); CERT-NULL (replay on the base == base, 48 checks, 0.0); metric reproduces four stored L198 rows EXACT. One thread per worker (new for the lineage) kept bit-identity.

| arm | removed / transform | gain d% | LEFT k | meanL | class | dL vs base [95% CI] | RIGHT k / mean / class | R 1.4-Hz | carrier rate |
|---|---|---|---|---|---|---|---|---|---|
| cutwA | — (base) | 0 | 1 | .293 | NOT-SUPER | — | 4 / .430 / NOT | .000 | .380 |
| **l2 / l2F** | ru2 70994 | −0.300 / 0 | 16 / 16 | .843 / .819 | SUPER / SUPER | +.550 [+.465, +.636] / +.525 | 9 / .533 INT · 12 / .542 INT | .000 | .591 / .612 |
| lt1 / lt1F | twin 71926 | +0.015 / 0 | 1 / 1 | .280 / .288 | NOT / NOT | −.013 [−.120, +.093] / −.005 | 1 / .188 NOT · 0 / .204 NOT | .000 | .380 / .384 |
| lt2 / lt2F | twin 68609 | −0.446 / 0 | 2 / 1 | .308 / .270 | NOT / NOT | +.015 [−.081, +.112] / −.023 | 5 / .427 NOT · 1 / .357 NOT | .000 | .347 / .372 |
| **l2k / l2kF** | ru2, carrier replay-clamped | −0.300 / 0 | 16 / 16 | .898 / .904 | SUPER / SUPER | +.605 [+.526, +.683] / +.611 | 10 / .547 INT · 9 / .513 INT | .000 | .380 (= base, exact) |
| **l2c / l2cF** | ru2 + carrier | −0.644 / 0 | 16 / 16 | .902 / .952 | SUPER / SUPER | +.609 [+.530, +.689] / +.659 | **3 / .296 NOT · 4 / .313 NOT** | **.000** | — |
| sc25 | carrier 1110 | +1.244 | 0 | .137 | NOT | −.156 [−.224, −.087] | 15 / .783 SUPER | .585 | — |
| l2h | homolog 67738 (silent) | −0.049 | 0 | .214 | NOT | −.079 [−.172, +.014] | 4 / .393 NOT | .000 | .380 |

Left 1.4-Hz middle value is ≤ .057 in every arm (l2 .000).

## What was measured

1. **A1 — the flip replicates exactly.** Left 16/16 .843 (L198: 16/16 .840), 16/16 .819 at the base gain. Pooled over both batches 32/32, mean .842, lowest seed .57; base 1/32, .277. The carrier's rate rises again, .380 → .591 (paired +.211 [+.194, +.227]). The right side is INTERMEDIATE again (9/16 .533; L198 10/16 .541).
2. **A2 — neither left-drive-matched twin does it (M3 rejected).** lt1 1/16 .280, lt2 2/16 .308; fixed gain 1/16 and 1/16. Paired below ru2 by −.564 [−.678, −.449] and −.535 [−.606, −.464]. Both twins match ru2's delivered drive onto the 1,910-cell left-tibia premotor pool to 0.5%.
3. **A3 — the flip does not route through the carrier (M2 rejected).** With the carrier's whole rate trajectory replayed from the same-seed base rollout (carrier .380, exact), the left flip is intact: 16/16 .898, retained fraction 1.10 (fixed gain 1.16). With the carrier removed outright it is intact too: 16/16 .902. The clamp is not inert — at fixed gain it adds +.085 [+.027, +.143] — so the carrier's rise slightly opposes the flip rather than carrying it.
4. **M1's signature leg fails.** No left 1.4-Hz signature under ru2 removal (.000 here, .000 in the stored L198 batch). The carrier's fingerprint on the right has no left counterpart.
5. **A4 — the wiring is not a mirror.** LI2 (two-hop laterality onto tibia motor pools): carrier +.174, ru2 −.048 (registered bars +.20 / −.20). ru2 projects to both premotor pools evenly (5 edges each side; 45.7th percentile of 10,109 cord interneurons). Direct-target overlap 3 of 80 / 61 (Jaccard .022; mirrored-by-type .040); zero overlap between the carrier's right-premotor targets and ru2's left-premotor targets.
6. **Not predicted (P6 wrong), seen: removing ru2 abolishes the carrier-removal phenotype on the right.** Carrier removed alone: right 15/16 .783 with the 1.4-Hz signature at .585 (10 seeds ≥ .5). Carrier + ru2 removed: right 3/16 .296, 1.4-Hz .000 (fixed gain 4/16 .313, .000). Paired l2c − sc25: chopped −.487 [−.591, −.384], 1.4-Hz −.585 [−.704, −.467], all 16 seeds lower; the double removal sits below the base as well (−.135 [−.244, −.025]). So the coupling the brief asked about exists in the opposite direction: ru2's left effect does not need the carrier, but the carrier's right effect needs ru2.

## Reading

Supported: the left flip is a property of this cell among the cells tested — replicated on two batches, both gain forms, absent in two left-drive-matched twins, independent of the carrier's rate and of the carrier's presence. Not supported: "ru2 is to the left what the carrier is to the right." The two differ in sign, weight, laterality of wiring and in the 1.4-Hz fingerprint, and they share almost no targets. The relation found is asymmetric: ru2 is necessary for the carrier-removal right-side regime (chopped duty and 1.4-Hz signature both), while the carrier is irrelevant to ru2's left flip.

## Caveats

- **Two twins bound "unique" weakly, and neither matches ru2's shape** (fixed in `SELECTION.md` before rollouts): lt1 delivers 6.8× more drive to the right premotor pool than the left (its removal lowers the RIGHT duty, −.242 [−.332, −.153]); lt2 is left-only with 14% of ru2's total drive. Rank 4 (gi 67125), the one bilateral candidate, was not rolled. T = 0 says "these two do not", not "no cell does".
- **The homolog arm is uninformative as a mirror test.** IN07B031-L (gi 67738) is silent on the base (census x̄ ≈ 0), so its removal is a near-null by construction (right 4/16 .393). The asymmetry IN07B031-R active (.30) / -L silent is a base-state fact, not a result of this card.
- Item 6 is post hoc and one batch. Its fixed-gain comparator (`sc25F`) was not rolled here (its slot went to the homolog arm); L198's other-batch sc25F was 15/16 .700, 1.4-Hz .345. The re-matched contrast is same-batch and paired.
- The replay clamp holds one cell's output. It excludes a route through the carrier's rate; it cannot exclude routes through cells the carrier does not drive.
- A4 is one-hop / two-hop static weight; LI2's population distribution is bimodal (43% ≤ −.20, 49% ≥ +.20), so "balanced" is the unusual profile, and the ±.20 bar was set before seeing that.
- One model class, one base (k=24), chopped 0.7-Hz classifier + 1.4-Hz panel only.

## What it would change (nothing edited)

- The L198 side note can be stated as a result: removing IN07B031-R flips the left tibia 32/32 seeds over two batches, independent of the carrier.
- The carrier's right-side claim gains a dependency it did not have: its chopped rise and its 1.4-Hz signature both vanish when ru2 is absent (one batch, post hoc — needs its own registered card before any wording moves).
- "Mirror" language should not be used for ru2.

**Next.** (i) Register item 6 as its own card: `l2c` vs `sc25` with `sc25F` / `l2cF` same-batch, second batch, and ru2 replay-clamped at base under carrier removal (is it ru2's rate change, +.030 under sc25, or its presence?). (ii) Roll rank 4 (gi 67125) and two further bilateral, balanced twins. (iii) A left-side search for what ru2 gates: its two-hop weight lands mostly on the tibia extensor pools of both sides (−95.5 left, −105.3 right).

**Predictions.** Held: P1 (l2 left SUPER, both gain forms), P2 (carrier rate ≥ .50: .591), P3 (T = 0), P4 modal (clamp arm stays SUPER), P5 (no left signature). Wrong: P6 — I gave .70 to the carrier-removal right phenotype surviving ru2's absence; it did not (its .50 left-SUPER half occurred). Low-probability events that did not occur: P7 A4_mirror (.30), P8 homolog literal mirror (.35 — set before I knew the homolog was silent).

Files: `results_l200.json`, `verdict.out`, `addendum.py/.json/.out`, `selection.json` + `SELECTION.md`, `a4_wiring.json`, `static.json`, `raw_w0-5.npz`, `xm_w0-5.npz`, `anchors_w0-5.json`, `gains_w0-5.json`, `PREREG.md` + `PREREG.sha256` + `FREEZE.json`, scripts `ref_probe.py`, `build_ru2.py` → `ru2_run.py`, `build_verdict.py` → `verdict_l200.py`, `run_all.sh`. Wall 20:18 → 20:58 (rollouts 20:31-20:53, 6 workers × 1 thread, CPU only).
