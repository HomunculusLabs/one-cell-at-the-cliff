# L198 SELECTION (stage 2) — frozen before any rollout

Produced by the zero-rollout static pass (`L198_MODE=static twin_run.py`) under PREREG sha c9fff8791fff1161 (stage 1, frozen 18:44:49 before this code first ran). Rule and pool: PREREG §Selection rule. Stored census only (seeds 801 / 901 / 3561).

Pool: 12385 cord interneurons on the k=24 base not in any prior arm (9006 with positive drive, 2069 active x̄ > .05). Relay reference drive 86.503 (x̄ 0.3289 × out|w| 263.0; raw mass 131.5; 51 out / 58 in; inhibitory).

| arm | gi | type / side | sign | glut | x̄ | out\|w\| eff | drive | drive ratio | mass ratio | out / in edges | direct onto Ti pools | edges to/from carrier, relay, 74914 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tw (PICK) | 73008 | IN17B003 / right | -1 | False | 0.1456 | 594.2 | 86.493 | 0.99988 | 2.260 | 151 / 44 | none | none |
| ru1 | 67561 | IN21A049 / left | -1 | True | 0.4787 | 180.5 | 86.426 | 0.99911 | 0.686 | 43 / 23 | Ti_fL 5e -25.7 | none |
| ru2 | 70994 | IN07B031 / right | -1 | True | 0.2994 | 287.8 | 86.173 | 0.99619 | 1.094 | 61 / 52 | none | none |
| ru3 | 64787 | IN02A030 / right | -1 | True | 0.2528 | 340.7 | 86.127 | 0.99566 | 1.296 | 90 / 14 | none | none |
| ru4 | 67353 | IN02A026 / left | -1 | True | 0.2195 | 391.2 | 85.887 | 0.99288 | 1.488 | 96 / 91 | none | none |
| ru5 | 71153 | IN06B066 / right | -1 | False | 0.5246 | 166.1 | 87.164 | 1.00764 | 0.632 | 40 / 28 | none | none |

Notes fixed now, before rollouts: all six are inhibitory VNC interneurons (the relay's sign) with no direct edge to or from the carrier, the relay or gi 74914. The pick (IN17B003-R) matches drive to 1.2e-4 but reaches it differently from the relay: lower rate (.146 vs .329) through a wider, heavier output (151 vs 51 edges; raw mass x2.26). None of the six has a direct edge onto a RIGHT-Ti pool (the relay has one, 8 syn onto a right flexor MN); ru1 has 5 edges onto LEFT flexor MNs. These are limits on "matched" and are not repaired by re-selection.

Arms as registered: `tw` = wA - 73008 (re-bisected) carries the T-branch; `twF` fixed gain; `ru1..ru5` secondary.
