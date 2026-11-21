# L175 (b) FINDINGS — single-cell scan + drive-matched twin (batch 3545-3560, n=16 every arm, FINAL)

**Branch fired: D2_identity_carried** (read order E0 > D1 > D2 > D3; PREREG sha256 7af87de7b1552896, registered before any rollout). Certs green: generic plumbing == lineage cutng25/cutng25p (static); g_cutwA x5 / g_sc25 / g_sc26 == stored floats EXACT; C0A 322 bit-identity checks vs raw_l135 max 0.0; cutwA identical across workers (1728 checks); metric reproduces results_l135 EXACT.

- **Carrier 16/16, meanR 0.758 (Wilson lb 0.806) — the only SUPER among 34 window arms + 2 twins.** Base 5/16 0.408; mass twin 319 2/16 0.378.
- **Drive-matched twins do not flip.** dmA gi 511 (DNge046, inhibitory, drive x1.003 of carrier) 5/16 0.390; dmC gi 1480 (DNpe019, same class + sign as carrier, x1.006) 2/16 0.366. They agree.
- **Active cells do not flip.** 14 of 34 window cells are active on the k=24 base (carrier x_mean 0.389; mass twin 0.0005). Of the 13 other active cells, 0 SUPER; of the 10 at carrier-scale drive (>= .5x), 0; 7 deliver MORE than the carrier (x1.46-4.16), 0 SUPER. Spearman(drive, meanR) = +0.19 over the 14 active cells (excitatory only: +0.55, n=8).

Caveats (descriptive, NOT registered — they bound how hard D2 can be leaned on):
1. **The null is wide.** Removing one of the 20 silent cells (delivers ~nothing) gives kR 2-11/16, meanR 0.340-0.605. All 10 INTERMEDIATE arms (7 of them silent cells) sit inside that range; sc27 (11/16, 0.596) and sc40 (11/16, 0.605) sit at the SUPER boundary (kR >= 12 and meanR >= .60). The mass twin's 2/16 is one draw from this null, not a control.
2. **The null covaries with gain.** Over the 33 non-carrier arms meanR vs the arm's own re-bisected gain: Spearman -0.72 (-0.83 among silent cells, whose gain shifts are at most 1.13%). The carrier goes AGAINST it (+1.24% gain, highest meanR), so the gain trend does not explain its flip; it does suggest the k=24 base is gain-sensitive at the sub-percent level (not tested directly here: discriminator ii).
3. sc47 bisected to an outlier gain (+10.3%, staircase residual 8.4e-04); read that arm (2/16) with care. sc33 and sc34 (active, excitatory) go the other way: 0/16.
4. One batch; chopped 0.7-Hz classifier only (referee N2's unchopped panel not run; the raws are stored, so it costs zero rollouts); drive = mean rate x out-weight, not target-matched. Rule deviation: results json was refreshed atomically per completed SEED (seed-outer loop), not per arm.

**Title.** Keep "identity"; do not reframe to "delivered drive". The evidence should move off the silent mass twin onto this table: 1 of 34 window cells and 0 of 2 drive-matched twins flip. Honest wording: "cell identity, not removal mass or delivered drive (one batch)", with the twin's silence and the null width disclosed.
**Next (discriminators).** (i) second fresh batch for sc25 / dmA / dmC / sc27 / sc40 (L90 rule); (ii) cutwA gain sweep +-0.5% in 5 steps = the gain-only null; (iii) unchopped panel on these raws.
**Predictions.** P1 controls reproduce: correct. P2 carrier active, <17 active: correct (14). P3 my modal guess was D3 (.45): wrong, D2 fired. P4 dmA not a DN: wrong (it is).

| arm | rank | gi | type | sign | x_mean (k=24) | out_mass | drive / carrier | gain d% | kR | meanR | kL | meanL | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cutwA | - | - | base | + | nan | nan | nan | +0.00 | 5/16 | 0.408 | 0 | 0.207 | not (partial) |
| sc25 | 25 | 1110 | DNp33 | + | 0.3891 | 0.00644 | 1.00 | +1.24 | 16/16 | 0.758 | 0 | 0.132 | SUPER |
| sc26 | 26 | 319 | DNpe025 | + | 0.0005 | 0.00604 | 0.00 | -0.09 | 2/16 | 0.378 | 0 | 0.275 | not |
| sc27 | 27 | 707 | DNpe055 | + | 0.0408 | 0.00596 | 0.11 | -0.28 | 11/16 | 0.596 | 0 | 0.299 | interm. |
| sc28 | 28 | 354 | DNg109 | + | -0.0000 | 0.00591 | -0.00 | -0.07 | 6/16 | 0.441 | 1 | 0.308 | not (partial) |
| sc29 | 29 | 32271 | DNge132 | + | -0.0001 | 0.00588 | -0.00 | -0.02 | 7/16 | 0.422 | 2 | 0.282 | not (partial) |
| sc30 | 30 | 1266 | DNg38 | - | 0.0194 | 0.00584 | 0.10 | -0.53 | 10/16 | 0.531 | 0 | 0.285 | interm. |
| sc31 | 31 | 228 | DNge141 | - | 0.2533 | 0.00568 | 1.65 | +0.81 | 4/16 | 0.435 | 8 | 0.499 | not (partial) |
| sc32 | 32 | 549 | DNpe025 | + | 0.0000 | 0.00562 | 0.00 | -0.04 | 5/16 | 0.414 | 2 | 0.291 | not (partial) |
| sc33 | 33 | 725 | DNp44 | + | 0.1096 | 0.00561 | 0.27 | +0.51 | 0/16 | 0.270 | 1 | 0.311 | not |
| sc34 | 34 | 890 | DNp53 | + | 0.3627 | 0.00552 | 0.85 | +0.01 | 0/16 | 0.210 | 2 | 0.299 | not |
| sc35 | 35 | 808 | DNg56 | - | 0.4200 | 0.00551 | 2.01 | -0.92 | 2/16 | 0.361 | 5 | 0.433 | not |
| sc36 | 36 | 924 | DNp22 | + | -0.0001 | 0.00541 | -0.00 | +0.00 | 4/16 | 0.355 | 1 | 0.284 | not (partial) |
| sc37 | 37 | 779 | DNp44 | + | 0.3481 | 0.00520 | 0.78 | +1.35 | 4/16 | 0.368 | 7 | 0.444 | not (partial) |
| sc38 | 38 | 456 | DNpe050 | + | 0.0243 | 0.00503 | 0.06 | +0.01 | 3/16 | 0.340 | 2 | 0.317 | not |
| sc39 | 39 | 826 | DNg56 | - | 0.3489 | 0.00498 | 1.49 | -0.07 | 11/16 | 0.547 | 0 | 0.181 | interm. |
| sc40 | 40 | 559 | DNge084 | - | 0.0343 | 0.00492 | 0.19 | -1.13 | 11/16 | 0.605 | 0 | 0.280 | interm. |
| sc41 | 41 | 692 | DNge043 | - | 0.9935 | 0.00471 | 4.16 | -0.04 | 3/16 | 0.297 | 0 | 0.212 | not |
| sc42 | 42 | 32097 | DNp15 | + | -0.0000 | 0.00456 | -0.00 | +0.00 | 3/16 | 0.379 | 0 | 0.270 | not (partial) |
| sc43 | 43 | 1509 | DNge175 | + | -0.0000 | 0.00454 | -0.00 | -0.00 | 6/16 | 0.412 | 1 | 0.273 | not (partial) |
| sc44 | 44 | 722 | DNge043 | - | 0.0001 | 0.00453 | 0.00 | -0.33 | 11/16 | 0.489 | 0 | 0.271 | interm. |
| sc45 | 45 | 618 | DNpe050 | + | 0.0200 | 0.00449 | 0.05 | -0.21 | 4/16 | 0.462 | 1 | 0.241 | not (partial) |
| sc46 | 46 | 1022 | DNp67 | + | 0.0004 | 0.00447 | 0.00 | -0.12 | 9/16 | 0.485 | 4 | 0.288 | interm. |
| sc47 | 47 | 1038 | DNge101 | - | 0.3848 | 0.00432 | 1.52 | +10.28 | 2/16 | 0.297 | 3 | 0.357 | not |
| sc48 | 48 | 32005 | DNg24 | - | 0.0075 | 0.00426 | 0.03 | -0.32 | 9/16 | 0.497 | 1 | 0.270 | interm. |
| sc49 | 49 | 643 | DNge084 | - | 0.0651 | 0.00422 | 0.34 | +0.57 | 2/16 | 0.310 | 0 | 0.195 | not |
| sc50 | 50 | 736 | DNge006 | + | 1.0000 | 0.00416 | 1.86 | -0.54 | 9/16 | 0.526 | 0 | 0.249 | interm. |
| sc51 | 51 | 1543 | DNge016 | + | -0.0001 | 0.00411 | -0.00 | -0.00 | 5/16 | 0.369 | 0 | 0.253 | not (partial) |
| sc52 | 52 | 1557 | DNge096 | - | 0.0201 | 0.00407 | 0.08 | -0.23 | 8/16 | 0.506 | 0 | 0.282 | interm. |
| sc53 | 53 | 1060 | DNp15 | + | 0.8797 | 0.00401 | 1.46 | -0.25 | 9/16 | 0.483 | 2 | 0.340 | interm. |
| sc54 | 54 | 262 | DNp64 | + | 0.0977 | 0.00357 | 0.22 | +0.20 | 3/16 | 0.401 | 0 | 0.113 | not (partial) |
| sc55 | 55 | 1673 | DNge016 | + | -0.0001 | 0.00356 | -0.00 | -0.08 | 7/16 | 0.476 | 2 | 0.326 | not (partial) |
| sc56 | 56 | 651 | DNg24 | - | 0.0171 | 0.00352 | 0.06 | -0.26 | 5/16 | 0.407 | 1 | 0.339 | not (partial) |
| sc57 | 57 | 1224 | DNp51 | + | -0.0000 | 0.00342 | -0.00 | -0.29 | 6/16 | 0.468 | 0 | 0.246 | not (partial) |
| sc58 | 58 | 1489 | DNpe004 | + | 0.3718 | 0.00341 | 0.57 | +0.43 | 3/16 | 0.316 | 0 | 0.242 | not |
| dmA (twin, any class) | - | 511 | DNge046 | - | 0.2591 | 0.00114 | 1.00 | +0.11 | 5/16 | 0.390 | 0 | 0.143 | not (partial) |
| dmC (twin, carrier class) | - | 1480 | DNpe019 | + | 0.6192 | 0.00273 | 1.01 | +3.31 | 2/16 | 0.366 | 0 | 0.155 | not |
