# L184 | DNp33-L loss changes shared timing, not overall rhythmic gain
Stored data only; CPU, zero rollouts. The chopped gate reaches the pools more strongly than in base, but a uniform, carrier-specific damping of drive transmission is not supported.

## Methods (specified before results)
Q1: PREREG-analysis.md precedes computation. B39, 16 paired seeds; block intercepts, on/off gate and gated quadrature at 0.7 Hz (outer blocks) or continuous quadrature at 1.4 Hz (middle). Mean of seed amplitudes, not amplitude of the seed mean; paired percentile intervals in q1-contrasts.csv. Separate 5-s-on/4-s-off gate from the faster sinusoid.
Q2: reconstruct the 644,177 cutwA edges from grouped synapses, graph IDs and census signs; verify every outgoing effective mass. Rank all simple, first-pool-hit paths of 1–4 edges by absolute DC small-signal score: product of gain × signed log1p(synapses), inhibitory weights doubled, divided by endpoint pool size (51 flexors, 6 extensors). Unit slope at each recipient; sensitivity sets slopes to zero outside (.05,.95) census mean. No recurrent walks, delays or measured time-resolved slopes: these are candidate routes, not a dynamic transfer function.
Q3–4: duty is the fraction of 500-sample windows with r(flex,ext) ≤ −.25 and both SDs > 1e−6, not −r itself. Step 10 samples; use registered endpoints. Same = matched seed; cross = flex from i, ext from j≠i at identical times. Δsame = Δcross + Δ(same−cross); constant means cancel under centering. Post hoc sensitivity subtracts the Q1 fitted time-varying terms before recomputing duty.

## Q1 | Gate contrast and drive-frequency amplitude give different answers
In 10⁻³ rate units, chopped harmonic amplitude (flex/ext) goes 2.38/33.24 → 4.60/23.51, base → sc25. Paired changes +2.22 [1.52,2.92] and −9.73 [−14.14,−5.36]; same directions against sc26, dmA and dmC. At 1.4 Hz: 3.09/32.84 → 3.97/15.16; extensor amplitude falls despite duty rising from 0 to .510.
Signed gate contrast (on−off, same units) separates the pools: −1.49/+7.00 → −3.24/+21.13. Absolute gate contrast increases in both vs base and mass twin sc26, but dmA matches sc25 in extensor and dmC exceeds sc25 in both. Gate penetration alone cannot explain the carrier-specific duty phenotype. All arm/pool estimates: q1.csv.
Carrier phase in B39 base/twins is not identifiable: xwin and xmean store whole-run cell means, xm a mechanosensory pool. Historical intact graph only (L137, seed 3101): individual carrier harmonic amplitude .0876/.0334 at .7/1.4 Hz, fitted angles −.505/−2.225 rad. A single different graph/seed cannot establish B39 entrainment.

## Q2 | Indirect access to right tibia; only one boundary cell shares a leading relay
93 incident edges: 13 descending inputs, 80 outputs. None goes directly to a right-Ti motor. Of 70 intrinsic targets, 3 directly innervate right-Ti motors (GI 69410, 72158, 75494); 67 do not. The other 10 outputs go to other motors. See edges.csv for every partner, direction, count and sign.
Top unit-slope routes: 1110→75494→74914→74468→10375 (flex, −.0159) and 1110→75494→71392→64322→18563 (ext, −.1281). The census slope proxy retains the flex entry through 75494 but flips its leading score positive; ext enters via 65443. Rankings depend on operating state. top_paths.csv ranks up to ten per pool/model; path_totals.csv includes signed and absolute sums.
Shared carrier targets: sc27 0/98; sc40 3/102, including 75494. sc40’s leading paths share both downstream chains but have opposite signs: partial anatomical convergence, not a weaker same-sign copy. sc27 has a distinct entry route; downstream convergence is not excluded. sc26 0/103, dmA 0/56, dmC 2/58 (neither a shared direct premotor).

## Q3 | Shared timing carries the net duty rise; mean shifts do not enter additively
Changes vs base, ordered Δmean flex / Δmean ext / Δsame duty / Δcross duty / Δsame-specific residual:
    sc25  -0.00123 / +0.00677 / +0.3504 / +0.5246 / -0.1742
    dmA  -0.00146 / -0.00561 / -0.0179 / +0.2788 / -0.2967
    dmC  +0.00238 / +0.00404 / -0.0415 / +0.1895 / -0.2310
    sc27  -0.00024 / +0.00039 / +0.1883 / +0.0722 / +0.1161
    sc40  -0.00051 / +0.00493 / +0.1975 / +0.1613 / +0.0362
Base mean rates .02600/.02621. Mean within-window −r rises .214 → .480 for sc25. The cross-seed increment is 150% of the net increment because the same-specific residual shrinks; 82% is the ratio of cross to same duty *in sc25*, not a fraction of the treatment effect. Neither is causal mediation.
Subtracting gate alone leaves Δsame +.357; tone alone +.210; both +.209 (40% attenuation vs +.350). Δcross after both is still +.407. The simple gate step is not necessary for the observed excess in this subtraction; delayed responses or other shared temporal structure can survive it.
Next experiment: cross carrier present/removed with independently jittered gate onset schedules, matched on-time, tone, gain and noise; record GI 1110 and both pools. Test whether cross-seed duty follows realigned gate transitions rather than common elapsed time, and whether carrier phase predicts the pool response. Not run.

## Q4 | Right-Ti duty across B39
Each cell is mean duty (number with duty ≥ .5); matched columns out of 16 seeds, chopped cross out of 240 ordered, nonindependent pairs. threepanel.csv retains precision.
| Arm | Chopped | Continuous 1.4 Hz | Cross-seed, chopped |
|---|---:|---:|---:|
| cutwA | 0.408 (5) | 0.000 (0) | 0.097 (0) |
| sc25 | 0.758 (16) | 0.510 (8) | 0.622 (193) |
| sc26 | 0.378 (2) | 0.005 (0) | 0.101 (0) |
| sc27 | 0.596 (11) | 0.000 (0) | 0.169 (4) |
| sc28 | 0.441 (6) | 0.000 (0) | 0.133 (1) |
| sc29 | 0.422 (7) | 0.000 (0) | 0.086 (0) |
| sc30 | 0.531 (10) | 0.000 (0) | 0.174 (2) |
| sc31 | 0.435 (4) | 0.000 (0) | 0.200 (3) |
| sc32 | 0.414 (5) | 0.000 (0) | 0.115 (0) |
| sc33 | 0.270 (0) | 0.109 (0) | 0.084 (1) |
| sc34 | 0.210 (0) | 0.000 (0) | 0.080 (0) |
| sc35 | 0.361 (2) | 0.005 (0) | 0.124 (0) |
| sc36 | 0.355 (4) | 0.001 (0) | 0.111 (2) |
| sc37 | 0.368 (4) | 0.031 (0) | 0.058 (0) |
| sc38 | 0.340 (3) | 0.000 (0) | 0.079 (0) |
| sc39 | 0.547 (11) | 0.000 (0) | 0.168 (2) |
| sc40 | 0.605 (11) | 0.000 (0) | 0.258 (15) |
| sc41 | 0.297 (3) | 0.000 (0) | 0.060 (0) |
| sc42 | 0.379 (3) | 0.003 (0) | 0.090 (0) |
| sc43 | 0.412 (6) | 0.000 (0) | 0.107 (0) |
| sc44 | 0.489 (11) | 0.000 (0) | 0.121 (0) |
| sc45 | 0.462 (4) | 0.000 (0) | 0.111 (0) |
| sc46 | 0.485 (9) | 0.000 (0) | 0.102 (0) |
| sc47 | 0.297 (2) | 0.310 (3) | 0.120 (0) |
| sc48 | 0.497 (9) | 0.000 (0) | 0.138 (0) |
| sc49 | 0.310 (2) | 0.000 (0) | 0.130 (0) |
| sc50 | 0.526 (9) | 0.000 (0) | 0.207 (5) |
| sc51 | 0.369 (5) | 0.000 (0) | 0.104 (1) |
| sc52 | 0.506 (8) | 0.000 (0) | 0.146 (3) |
| sc53 | 0.483 (9) | 0.000 (0) | 0.166 (3) |
| sc54 | 0.401 (3) | 0.001 (0) | 0.181 (4) |
| sc55 | 0.476 (7) | 0.000 (0) | 0.110 (0) |
| sc56 | 0.408 (5) | 0.000 (0) | 0.134 (2) |
| sc57 | 0.468 (6) | 0.000 (0) | 0.134 (1) |
| sc58 | 0.316 (3) | 0.003 (0) | 0.087 (1) |
| dmA | 0.390 (5) | 0.004 (0) | 0.376 (36) |
| dmC | 0.366 (2) | 0.192 (0) | 0.287 (19) |
