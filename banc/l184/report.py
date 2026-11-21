from pathlib import Path
import csv
P=Path(__file__).resolve().parent
def rows(f):return list(csv.DictReader((P/f).open()))
lines='''# L184 | DNp33-L loss changes shared timing, not overall rhythmic gain
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
'''.splitlines();q={r['arm']:r for r in rows('q3.csv')};
for a in ['sc25','dmA','dmC','sc27','sc40']:
 r=q[a];lines.append('    '+a+'  '+' / '.join(format(float(r['delta_'+n]),'+.5f' if n in ['flex','ext'] else '+.4f') for n in ['flex','ext','same','cross','residual']))
lines+=['Base mean rates .02600/.02621. Mean within-window −r rises .214 → .480 for sc25. The cross-seed increment is 150% of the net increment because the same-specific residual shrinks; 82% is the ratio of cross to same duty *in sc25*, not a fraction of the treatment effect. Neither is causal mediation.','Subtracting gate alone leaves Δsame +.357; tone alone +.210; both +.209 (40% attenuation vs +.350). Δcross after both is still +.407. The simple gate step is not necessary for the observed excess in this subtraction; delayed responses or other shared temporal structure can survive it.','Next experiment: cross carrier present/removed with independently jittered gate onset schedules, matched on-time, tone, gain and noise; record GI 1110 and both pools. Test whether cross-seed duty follows realigned gate transitions rather than common elapsed time, and whether carrier phase predicts the pool response. Not run.','','## Q4 | Right-Ti duty across B39','Each cell is mean duty (number with duty ≥ .5); matched columns out of 16 seeds, chopped cross out of 240 ordered, nonindependent pairs. threepanel.csv retains precision.','| Arm | Chopped | Continuous 1.4 Hz | Cross-seed, chopped |','|---|---:|---:|---:|'];
for r in rows('threepanel.csv'):lines.append('| '+r['arm']+' | '+' | '.join(f"{float(r[n+'_mean']):.3f} ({r[n+'_k']})" for n in ['chopped','fast','cross'])+' |');
assert len(lines)<=70 and len(rows('threepanel.csv'))==37;(P/'L184-FINDINGS.md').write_text('\n'.join(lines)+'\n');print(len(lines),'lines')
