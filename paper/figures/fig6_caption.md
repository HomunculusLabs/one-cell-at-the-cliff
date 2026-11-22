**Figure 6 — the circuit: a carrier, a relay, and a cord interneuron the carrier's phenotype needs.** BANC female cord, k=24 cutwA base, rate model at the certified matched operating point. Every number in the figure and in this caption is read from a stored artifact; the table below gives the pointer for each one, and `fig6_verify.py` resolves every pointer against the files themselves.

**(A) Wiring, schematic.** Node positions are arbitrary; counts and signs are not. The carrier DNp33-L (gi 1110, descending, excitatory) has 80 output edges and none onto a tibia motor neuron. 3 of them land on direct right-tibia premotor cells (L184 Q2). One of those is the inhibitory relay IN06B033-L (gi 75494), reached by a 21-synapse edge. The relay has 1 direct edge (8 synapses) onto the right tibia flexor pool (51 motor neurons). Cutting only the carrier-to-relay edge raised the right chopped duty by +0.223. Removing the carrier on the same seeds raised it by +0.370, so the edge cut gives 60% of the carrier's shift. That is a point ratio with no interval. The edge cut's 1.4-Hz duty was 0.000 (L190). The carrier's other 77 outputs (67 onto cord interneurons, 10 onto other motor neurons) are drawn as a fan. They are the candidate substrate of the 1.4-Hz signature by elimination only, because relay removal and the edge cut both leave that signature at base (L187, L190). The inhibitory cord interneuron ru2, IN07B031-R (gi 70994, 61 outputs), sends 5 edges into the left tibia premotor pool (1,910 cells) and 5 into the right one (2,219). Its signed two-hop weight goes mostly onto both extensor pools (−95.5 left, −105.3 right). Its two-hop laterality index LI2 is −0.048, against the carrier's +0.174. The two cells share 3 of 80 / 61 direct targets (Jaccard 0.022), and their mirrored premotor target sets do not overlap (J 0.0). The base rates are carrier 0.39, ru2 0.30 and relay 0.33 (L200 A4, L198).

**(B) Asymmetric necessity.** L200 batch B44: 16 seeds per arm, fresh seeds 3705–3720. Bars show mean duty, dots individual seeds, and open diamonds the same arm at the base gain (`l2F`, `l2kF`, `l2cF`). Removing the carrier raises the right chopped duty to 0.783, with a 1.4-Hz signature of 0.585. Removing ru2 as well brings the right duty down to 0.296 and the signature to 0.000. On paired seeds the double removal minus carrier removal is −0.487 [−0.591, −0.384]. On the left, removing ru2 flips the duty to 0.843, +0.550 [+0.465, +0.636] above base (0.293). The flip stays intact when the carrier's whole rate trajectory is replay-clamped at its base value (0.898, carrier rate 0.38 = base 0.38) and when the carrier is removed outright (0.902). So ru2's left effect does not need the carrier, while the carrier's right-side regime needs ru2. Dashed lines mark the registered bars: SUPER mean 0.60 on the chopped readouts and signature mean 0.25 on the 1.4-Hz readout. The k row counts seeds with duty ≥ .5. Limits: the right-side wipe (item 6 of L200) is post hoc and comes from one batch. Its registered replicate, L202, which also supplies the base-gain carrier comparator sc25F and the ru2 activity clamp, had not landed when this figure was drawn, so its slot is marked pending. The carrier-only arm has no base-gain form in this batch.

**(C) Phase rotation.** L199 dataset S: 96 seeds, W150 window, 500-step pulse. Left: mean cross-seed duty of right-tibia pair-segments, binned by the tone offset between the two seeds' segments into eight octants. The octants are descriptive, and 360° repeats 0°. Dashed lines and shading show the registered first-harmonic preferred offset θ ± SE: base +172° (SE 4), carrier removed +55° (SE 5). The rotation is Δθ −118° [−131, −104]. The registered label is Hq: the removed graph falls outside the 0 ± 45° band, so the pools do not go to antiphase. Right: tone phase of the right flexor and extensor peaks (first harmonic; arrow length = resultant R). In the base graph the two pools peak together: flexor 102°, extensor 108°, difference −5°. With the carrier removed the flexor barely moves (93°) while the extensor moves to −150° and loosens its locking (R 0.95 → 0.70). The difference becomes −116°, about a third of a period. Scope: under the 250-step pulse (dataset W) the rotation is only −39°, so the phrase "500-step pulse" must travel with this panel.

Scope of the whole figure: one model class, one base (k=24), the chopped 0.7-Hz classifier plus the 1.4-Hz panel. The wiring in A is one-hop and two-hop static weight, not a measured transfer function.

### Per-number artifact pointers

Pointer aliases:
- `l184e` = `banc/l184/edges.csv`
- `l190r` = `banc/l190/results_l190.json`
- `l198s` = `banc/l198/static.json`
- `l200a4` = `banc/l200/a4_wiring.json`
- `l200s` = `banc/l200/selection.json`
- `l200r` = `banc/l200/results_l200.json`
- `l199p` = `banc/l199/results_primary.json`

`ratio(a;b)` and `sub(a;b)` are the only derived values (a/b, a−b of two stored numbers). Bar heights, seed dots, base-gain diamonds, octant points, θ lines and phase arrows carry their pointers as `data-src` on the SVG element; the first table lists every number printed as text in the figure, the second every number in the caption prose, in order of appearance.

#### Figure text

| element | value (stored) | shown as | artifact pointer |
|---|---|---|---|
| `t0` | 1110 | 1110 | `l200a4/cells/carrier/gi` |
| `t1` | 80 | 80 | `l200a4/cells/carrier/out_edges` |
| `t2` | 75494 | 75494 | `l198s/relay/cell/gi` |
| `t3` | 51 | 51 | `l198s/relay/out_edges` |
| `t4` | 70994 | 70994 | `l200a4/cells/ru2/gi` |
| `t5` | 61 | 61 | `l200a4/cells/ru2/out_edges` |
| `t6` | 51 | 51 | `l198s/relay/direct_onto/Ti_fR/targets` |
| `t7` | 6 | 6 | `l198s/relay/direct_onto/Ti_eR/targets` |
| `t8` | 2219 | 2,219 | `l200s/PM_R_n` |
| `t9` | 1910 | 1,910 | `l200s/PM_L_n` |
| `t10` | 50 | 50 | `l200a4/cells/ru2/direct_onto/Ti_fL/targets` |
| `t10` | 6 | 6 | `l200a4/cells/ru2/direct_onto/Ti_eL/targets` |
| `t12` | 21 | 21 | `l198s/relay/carrier_to_relay/syn` |
| `t13` | 1 | 1 | `l198s/relay/direct_onto/Ti_fR/n_edges` |
| `t13` | 8 | 8 | `l198s/relay/direct_onto/Ti_fR/syn` |
| `t15` | 3 | 3 | `l200a4/cells/carrier/one_hop/PM_R/edges` |
| `t16` | 0.22281250000000002 | +0.223 | `l190r/summary/E-edge/delta` |
| `t17` | 0.37012500000000004 | +0.370 | `l190r/summary/sc25/delta` |
| `t17` | 0.6019925700776765 | 60% | `ratio(l190r/summary/E-edge/delta;l190r/summary/sc25/delta)` |
| `t19` | 0.0 | 0.000 | `l190r/summary/E-edge/mid` |
| `t20` | 77 | 77 | `sub(l184e?direction=out#count;l184e?target_class=direct right-Ti premotor#count)` |
| `t20` | 80 | 80 | `l184e?direction=out#count` |
| `t20` | 3 | 3 | `l184e?target_class=direct right-Ti premotor#count` |
| `t23` | 67 | 67 | `l184e?target_class=ventral_nerve_cord_intrinsic#count` |
| `t24` | 10 | 10 | `l184e?target_class=other motor#count` |
| `t25` | 5 | 5 | `l200a4/cells/ru2/one_hop/PM_R/edges` |
| `t26` | 5 | 5 | `l200a4/cells/ru2/one_hop/PM_L/edges` |
| `t27` | -95.46391430399075 | −95.5 | `l200a4/cells/ru2/two_hop/Ti_eL/signed` |
| `t27` | -105.29919748751833 | −105.3 | `l200a4/cells/ru2/two_hop/Ti_eR/signed` |
| `t29` | -0.04751471539703847 | −0.048 | `l200a4/LI2_ru2` |
| `t29` | 0.17399138353637195 | +0.174 | `l200a4/LI2_carrier` |
| `t31` | 3 | 3 | `l200a4/overlap/n_shared` |
| `t31` | 80 | 80 | `l200a4/overlap/n_targets_carrier` |
| `t31` | 61 | 61 | `l200a4/overlap/n_targets_ru2` |
| `t31` | 0.021739130434782608 | 0.022 | `l200a4/overlap/J_same` |
| `t35` | 0.0 | 0.0 | `l200a4/overlap/premotor/J_mirror` |
| `t36` | 0.3891147971153259 | 0.39 | `l200a4/cells/carrier/x_mean` |
| `t36` | 0.2994140883286794 | 0.30 | `l200a4/cells/ru2/x_mean` |
| `t36` | 0.3289374311765035 | 0.33 | `l198s/relay/census_x_mean_3seed` |
| `t39` | 0.6 | 0.60 | `l200r/bands/super_mean_min` |
| `t40` | 0.43 | 0.43 | `l200r/base/meanR` |
| `t41` | 4 | 4 | `l200r/base/kR` |
| `t42` | 0.783 | 0.78 | `l200r/arms/sc25/meanR` |
| `t43` | 15 | 15 | `l200r/arms/sc25/kR` |
| `t44` | 0.533 | 0.53 | `l200r/arms/l2/meanR` |
| `t45` | 9 | 9 | `l200r/arms/l2/kR` |
| `t46` | 0.547 | 0.55 | `l200r/arms/l2k/meanR` |
| `t47` | 10 | 10 | `l200r/arms/l2k/kR` |
| `t48` | 0.296 | 0.30 | `l200r/arms/l2c/meanR` |
| `t49` | 3 | 3 | `l200r/arms/l2c/kR` |
| `t50` | 0.25 | 0.25 | `l200r/bands/signature_mean14_min` |
| `t51` | 0.0 | 0.00 | `l200r/base/mean14R` |
| `t52` | 0 | 0 | `l200r/base/k14R` |
| `t53` | 0.585 | 0.58 | `l200r/arms/sc25/mean14R` |
| `t54` | 10 | 10 | `l200r/arms/sc25/k14R` |
| `t55` | 0.0 | 0.00 | `l200r/arms/l2/mean14R` |
| `t56` | 0 | 0 | `l200r/arms/l2/k14R` |
| `t57` | 0.0 | 0.00 | `l200r/arms/l2k/mean14R` |
| `t58` | 0 | 0 | `l200r/arms/l2k/k14R` |
| `t59` | 0.0 | 0.00 | `l200r/arms/l2c/mean14R` |
| `t60` | 0 | 0 | `l200r/arms/l2c/k14R` |
| `t61` | 0.6 | 0.60 | `l200r/bands/super_mean_min` |
| `t62` | 0.293 | 0.29 | `l200r/base/meanL` |
| `t63` | 1 | 1 | `l200r/base/kL` |
| `t64` | 0.137 | 0.14 | `l200r/arms/sc25/meanL` |
| `t65` | 0 | 0 | `l200r/arms/sc25/kL` |
| `t66` | 0.843 | 0.84 | `l200r/arms/l2/meanL` |
| `t67` | 16 | 16 | `l200r/arms/l2/kL` |
| `t68` | 0.898 | 0.90 | `l200r/arms/l2k/meanL` |
| `t69` | 16 | 16 | `l200r/arms/l2k/kL` |
| `t70` | 0.902 | 0.90 | `l200r/arms/l2c/meanL` |
| `t71` | 16 | 16 | `l200r/arms/l2c/kL` |
| `t72` | -0.4872 | −0.487 | `l200r/contrasts/R_l2c_minus_sc25/mean` |
| `t72` | -0.5906 | −0.591 | `l200r/contrasts/R_l2c_minus_sc25/ci95/0` |
| `t72` | -0.3838 | −0.384 | `l200r/contrasts/R_l2c_minus_sc25/ci95/1` |
| `t72` | 0.585 | 0.585 | `l200r/arms/sc25/mean14R` |
| `t72` | 0.0 | 0.000 | `l200r/arms/l2c/mean14R` |
| `t77` | 0.5504 | +0.550 | `l200r/arms/l2/L_vs_base/mean` |
| `t77` | 0.4651 | +0.465 | `l200r/arms/l2/L_vs_base/ci95/0` |
| `t77` | 0.6357 | +0.636 | `l200r/arms/l2/L_vs_base/ci95/1` |
| `t77` | 0.6047 | +0.605 | `l200r/arms/l2k/L_vs_base/mean` |
| `t77` | 0.6092 | +0.609 | `l200r/arms/l2c/L_vs_base/mean` |
| `t82` | 172.3453838008853 | +172 | `l199p/datasets/S/B/graphs/cutwA/theta/value` |
| `t82` | 3.935793370010476 | 4 | `l199p/datasets/S/B/graphs/cutwA/theta/se` |
| `t84` | 54.61250206206472 | +55 | `l199p/datasets/S/B/graphs/sc25/theta/value` |
| `t84` | 5.4340221643121875 | 5 | `l199p/datasets/S/B/graphs/sc25/theta/se` |
| `t86` | -117.73288173882057 | −118 | `l199p/datasets/S/B/dtheta/value` |
| `t86` | -130.97885046023407 | −131 | `l199p/datasets/S/B/dtheta/ci95/0` |
| `t86` | -104.48691301740708 | −104 | `l199p/datasets/S/B/dtheta/ci95/1` |
| `t89` | 101.79866393295053 | 102 | `l199p/datasets/S/C/cutwA/alpha/Ti_fR/mean_deg` |
| `t89` | 0.8820369923041153 | 0.88 | `l199p/datasets/S/C/cutwA/alpha/Ti_fR/R` |
| `t91` | 107.94476073987653 | 108 | `l199p/datasets/S/C/cutwA/alpha/Ti_eR/mean_deg` |
| `t91` | 0.9480734389321386 | 0.95 | `l199p/datasets/S/C/cutwA/alpha/Ti_eR/R` |
| `t93` | 93.32491195778663 | 93 | `l199p/datasets/S/C/sc25/alpha/Ti_fR/mean_deg` |
| `t93` | 0.9723355000442814 | 0.97 | `l199p/datasets/S/C/sc25/alpha/Ti_fR/R` |
| `t95` | -150.25411825521732 | −150 | `l199p/datasets/S/C/sc25/alpha/Ti_eR/mean_deg` |
| `t95` | 0.7015053431204614 | 0.70 | `l199p/datasets/S/C/sc25/alpha/Ti_eR/R` |
| `t97` | -5.081101934997697 | −5 | `l199p/datasets/S/C/cutwA/Delta/mean_deg` |
| `t97` | -116.01801641082564 | −116 | `l199p/datasets/S/C/sc25/Delta/mean_deg` |

#### Caption prose

| # | value (stored) | shown as | artifact pointer |
|---|---|---|---|
| `cap0` | 1110 | 1110 | `l200a4/cells/carrier/gi` |
| `cap1` | 80 | 80 | `l200a4/cells/carrier/out_edges` |
| `cap2` | 3 | 3 | `l184e?target_class=direct right-Ti premotor#count` |
| `cap3` | 75494 | 75494 | `l198s/relay/cell/gi` |
| `cap4` | 21 | 21 | `l198s/relay/carrier_to_relay/syn` |
| `cap5` | 1 | 1 | `l198s/relay/direct_onto/Ti_fR/n_edges` |
| `cap6` | 8 | 8 | `l198s/relay/direct_onto/Ti_fR/syn` |
| `cap7` | 51 | 51 | `l198s/relay/direct_onto/Ti_fR/targets` |
| `cap8` | 0.22281250000000002 | +0.223 | `l190r/summary/E-edge/delta` |
| `cap9` | 0.37012500000000004 | +0.370 | `l190r/summary/sc25/delta` |
| `cap10` | 0.6019925700776765 | 60% | `ratio(l190r/summary/E-edge/delta;l190r/summary/sc25/delta)` |
| `cap11` | 0.0 | 0.000 | `l190r/summary/E-edge/mid` |
| `cap12` | 77 | 77 | `sub(l184e?direction=out#count;l184e?target_class=direct right-Ti premotor#count)` |
| `cap13` | 67 | 67 | `l184e?target_class=ventral_nerve_cord_intrinsic#count` |
| `cap14` | 10 | 10 | `l184e?target_class=other motor#count` |
| `cap15` | 70994 | 70994 | `l200a4/cells/ru2/gi` |
| `cap16` | 61 | 61 | `l200a4/cells/ru2/out_edges` |
| `cap17` | 5 | 5 | `l200a4/cells/ru2/one_hop/PM_L/edges` |
| `cap18` | 1910 | 1,910 | `l200s/PM_L_n` |
| `cap19` | 5 | 5 | `l200a4/cells/ru2/one_hop/PM_R/edges` |
| `cap20` | 2219 | 2,219 | `l200s/PM_R_n` |
| `cap21` | -95.46391430399075 | −95.5 | `l200a4/cells/ru2/two_hop/Ti_eL/signed` |
| `cap22` | -105.29919748751833 | −105.3 | `l200a4/cells/ru2/two_hop/Ti_eR/signed` |
| `cap23` | -0.04751471539703847 | −0.048 | `l200a4/LI2_ru2` |
| `cap24` | 0.17399138353637195 | +0.174 | `l200a4/LI2_carrier` |
| `cap25` | 3 | 3 | `l200a4/overlap/n_shared` |
| `cap26` | 80 | 80 | `l200a4/overlap/n_targets_carrier` |
| `cap27` | 61 | 61 | `l200a4/overlap/n_targets_ru2` |
| `cap28` | 0.021739130434782608 | 0.022 | `l200a4/overlap/J_same` |
| `cap29` | 0.0 | 0.0 | `l200a4/overlap/premotor/J_mirror` |
| `cap30` | 0.3891147971153259 | 0.39 | `l200a4/cells/carrier/x_mean` |
| `cap31` | 0.2994140883286794 | 0.30 | `l200a4/cells/ru2/x_mean` |
| `cap32` | 0.3289374311765035 | 0.33 | `l198s/relay/census_x_mean_3seed` |
| `cap33` | 3705 | 3705 | `l200r/seeds/0` |
| `cap34` | 3720 | 3720 | `l200r/seeds/15` |
| `cap35` | 0.783 | 0.783 | `l200r/arms/sc25/meanR` |
| `cap36` | 0.585 | 0.585 | `l200r/arms/sc25/mean14R` |
| `cap37` | 0.296 | 0.296 | `l200r/arms/l2c/meanR` |
| `cap38` | 0.0 | 0.000 | `l200r/arms/l2c/mean14R` |
| `cap39` | -0.4872 | −0.487 | `l200r/contrasts/R_l2c_minus_sc25/mean` |
| `cap40` | -0.5906 | −0.591 | `l200r/contrasts/R_l2c_minus_sc25/ci95/0` |
| `cap41` | -0.3838 | −0.384 | `l200r/contrasts/R_l2c_minus_sc25/ci95/1` |
| `cap42` | 0.843 | 0.843 | `l200r/arms/l2/meanL` |
| `cap43` | 0.5504 | +0.550 | `l200r/arms/l2/L_vs_base/mean` |
| `cap44` | 0.4651 | +0.465 | `l200r/arms/l2/L_vs_base/ci95/0` |
| `cap45` | 0.6357 | +0.636 | `l200r/arms/l2/L_vs_base/ci95/1` |
| `cap46` | 0.293 | 0.293 | `l200r/base/meanL` |
| `cap47` | 0.898 | 0.898 | `l200r/arms/l2k/meanL` |
| `cap48` | 0.38 | 0.38 | `l200r/arms/l2k/x_carrier` |
| `cap49` | 0.38 | 0.38 | `l200r/base/x_carrier` |
| `cap50` | 0.902 | 0.902 | `l200r/arms/l2c/meanL` |
| `cap51` | 0.6 | 0.60 | `l200r/bands/super_mean_min` |
| `cap52` | 0.25 | 0.25 | `l200r/bands/signature_mean14_min` |
| `cap53` | 96 | 96 | `l199p/datasets/S/n` |
| `cap54` | 150 | 150 | `l199p/datasets/S/W` |
| `cap55` | 500 | 500 | `l199p/datasets/S/pulse` |
| `cap56` | 172.3453838008853 | +172 | `l199p/datasets/S/B/graphs/cutwA/theta/value` |
| `cap57` | 3.935793370010476 | 4 | `l199p/datasets/S/B/graphs/cutwA/theta/se` |
| `cap58` | 54.61250206206472 | +55 | `l199p/datasets/S/B/graphs/sc25/theta/value` |
| `cap59` | 5.4340221643121875 | 5 | `l199p/datasets/S/B/graphs/sc25/theta/se` |
| `cap60` | -117.73288173882057 | −118 | `l199p/datasets/S/B/dtheta/value` |
| `cap61` | -130.97885046023407 | −131 | `l199p/datasets/S/B/dtheta/ci95/0` |
| `cap62` | -104.48691301740708 | −104 | `l199p/datasets/S/B/dtheta/ci95/1` |
| `cap63` | 101.79866393295053 | 102 | `l199p/datasets/S/C/cutwA/alpha/Ti_fR/mean_deg` |
| `cap64` | 107.94476073987653 | 108 | `l199p/datasets/S/C/cutwA/alpha/Ti_eR/mean_deg` |
| `cap65` | -5.081101934997697 | −5 | `l199p/datasets/S/C/cutwA/Delta/mean_deg` |
| `cap66` | 93.32491195778663 | 93 | `l199p/datasets/S/C/sc25/alpha/Ti_fR/mean_deg` |
| `cap67` | -150.25411825521732 | −150 | `l199p/datasets/S/C/sc25/alpha/Ti_eR/mean_deg` |
| `cap68` | 0.9480734389321386 | 0.95 | `l199p/datasets/S/C/cutwA/alpha/Ti_eR/R` |
| `cap69` | 0.7015053431204614 | 0.70 | `l199p/datasets/S/C/sc25/alpha/Ti_eR/R` |
| `cap70` | -116.01801641082564 | −116 | `l199p/datasets/S/C/sc25/Delta/mean_deg` |
| `cap71` | -39.06000948217678 | −39 | `l199p/datasets/W/B/dtheta/value` |
