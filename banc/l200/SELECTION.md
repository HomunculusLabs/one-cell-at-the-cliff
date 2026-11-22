# L200 SELECTION + A4 (stage 2) — frozen before any rollout

Produced by the zero-rollout static pass (`L200_MODE=static ru2_run.py`, 20:28:01) under PREREG sha db03c33d5997bc51 (stage 1, frozen 20:26:14 before this code was written). Rules: PREREG §A2 / §A4. Stored census only (801 / 901 / 3561).

## A2 left-matched twins

Pools: left-Ti premotor PM_L 1910 cells, PM_R 2219, shared 108. Candidate pool 7274 inhibitory cord interneurons not in any prior arm (3222 with positive dL). Reference ru2 gi 70994 (IN07B031-R): dL 7.977 through 5 edges; dR 6.635 through 5 edges; not itself premotor.

| rank | arm | gi | type / side | x̄ | dL | dL ratio | dR | total-drive ratio | edges PM_L / PM_R | out / in | direct onto Ti MNs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ref | l2 | 70994 | IN07B031 / right | .299 | 7.977 | 1 | 6.635 | 1 | 5 / 5 | 61 / 52 | none |
| 1 | **lt1** | 71926 | IN14A074 / right | .719 | 7.951 | .9968 | 53.777 | .955 | 3 / 19 | 30 / 35 | none |
| 2 | **lt2** | 68609 | IN01B040 / left | .159 | 7.935 | .9947 | 0 | .139 | 10 / 0 | 15 / 20 | none |
| 3 | — | 10317 | IN13B075 / right | .338 | 8.087 | 1.0137 | 0 | .368 | 6 / 0 | 21 / 45 | Ti_fL 1e, Ti_eL 1e (is itself PM_L) |
| 4 | — | 67125 | IN00A048 / left | .248 | 7.854 | .9846 | 7.298 | .286 | 9 / 8 | 30 / 56 | none |
| 5 | — | 67756 | IN09A043 / left | .199 | 8.127 | 1.0188 | 8.214 | .168 | 7 / 7 | 14 / 14 | none |

None of the five has an edge to or from the carrier or ru2.

Limits on "matched", fixed now and not repaired by re-selection: **lt1** matches ru2's left drive to 0.3% and its total drive to 5%, but it sends 6.8x more drive to the RIGHT premotor pool than to the left (ru2 is balanced, 6.6 vs 8.0) — it is a right-heavy cell that happens to deliver ru2's left dose. **lt2** is purely left-directed (no right premotor edge) with 14% of ru2's total drive. Neither has ru2's bilateral profile; rank 4 (67125) does and is not rolled (the rule registers ranks 1-2).

## Homolog arm (secondary)

Candidates IN07B031 / left in the base, not prior: gi 67738, 68321. Pick by the registered rule (largest census total drive) = **gi 67738** -> arm `l2h` in worker 0's second slot (so `sc25F` is not rolled). Limit, fixed now: **the homolog is silent on the base** (census x̄ ≈ 0, total drive 1e-4 of ru2's; 77 out / 44 in edges). Removing a silent cell is expected to be a near-null by construction, so `l2h` cannot test "literal mirror" in the sense P8 intended; it is rolled as registered and reported as such. The asymmetry itself (IN07B031-R x̄ .30, IN07B031-L x̄ 0) is a base-state fact.

## A4 wiring (zero rollouts) — label `A4_no_laterality_contrast`

| cell | side / sign | out edges | onto PM_L (edges, Σ\|w\|) | onto PM_R | LI1 | two-hop abs L / R | **LI2** | two-hop signed fL / eL / fR / eR |
|---|---|---|---|---|---|---|---|---|
| carrier 1110 (DNp33) | left / + | 80 | 2, 3.6 | 3, 7.6 | +.363 | 19.6 / 27.9 | **+.174** | 0 / +8.1 / −13.6 / −5.9 |
| ru2 70994 | right / − | 61 | 5, 26.6 | 5, 22.2 | −.092 | 157.5 / 143.2 | **−.048** | −22.2 / −95.5 / +2.7 / −105.3 |
| lt1 71926 | right / − | 30 | 3, 11.1 | 19, 74.8 | +.742 | 159.9 / 1106.1 | +.747 | −148.5 / −11.4 / −307.2 / +134.6 |
| lt2 68609 | left / − | 15 | 10, 49.9 | 0, 0 | −1 | 968.7 / 0 | −1 | +344.8 / −64.3 / 0 / 0 |
| l2h 67738 | left / − | 77 | 4, 13.1 | 4, 13.2 | +.002 | 78.5 / 136.7 | +.270 | −11.5 / −67.0 / −27.9 / −108.8 |

Registered criterion (LI2 carrier ≥ +.20 AND ru2 ≤ −.20) not met: the carrier leans right but under the bar (+.174), and ru2's route to the tibia motor pools is bilaterally balanced (−.048; 45.7th percentile of 10,109 cord interneurons, whose LI2 distribution is itself bimodal: 43% ≤ −.20, 49% ≥ +.20). Target overlap is near zero: 3 shared direct targets of 80 / 61 (J_same .022), J_mirror .040 on typed + sided targets, and zero overlap (same or mirrored) between the carrier's 3 right-premotor targets and ru2's 5 left-premotor targets. **The wiring does not show ru2 as the carrier's left-side mirror**: ru2 is a heavier, sign-opposite, bilaterally projecting interneuron whose two-hop weight lands mostly on the tibia EXTENSOR pools of both sides (−95.5 left, −105.3 right).

Arms as registered: `l2`/`l2F`, `lt1`/`lt1F` = wA − 71926, `lt2`/`lt2F` = wA − 68609, `l2c`/`l2cF`, `l2k`/`l2kF`, `sc25`, `l2h` = wA − 67738.
