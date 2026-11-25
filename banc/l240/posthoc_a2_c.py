# L240 A2 third POST-HOC probe (tick 276, unregistered, non-branching):
# IS THE REGISTERED FLOOR FAIR FOR PAIRED ARMS?
# F comes from the noise twin (base graph, INDEPENDENT noise stream = unpaired),
# while every arm is PAIRED to the same stored cutwA (same per-step noise). If an
# arm tracks the control closely its paired difference noise is smaller than the
# unpaired twin's, and 2F is conservative for that arm. The stored 95% CI lets the
# paired SD be recovered exactly: half = t15 * sd / 4.
import json, math
import statistics as st
R = json.loads(open('l240/results_l240_a2.json').read())
R1 = json.loads(open('l240/results_l240.json').read())
eff, C = R['effects'], R['companion']
F = R['floor']['F']; sd_noise = 4 * F
t15 = 2.131449536
EJ = [4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67]
nt = R1['noise_twin']['per_seed']
print(f'noise twin per-seed sd {st.stdev(nt):.4e} (= 4F = {sd_noise:.4e}) | its own mean {sum(nt) / 16 / F:+.3f} F')
rows = []
for a, e in eff.items():
    half = (e['CI'][1] - e['CI'][0]) / 2
    se = half / t15
    zero = (e['CI'][1] == e['CI'][0])
    if zero:
        print(f'ZERO-WIDTH CI: {a} mean {e["mean"]!r} CI {e["CI"]!r} k_neg {e["k_neg"]} H1 {e["H1"]!r} H2 {e["H2"]!r} target {e["target"]} syn {e["syn"]} '
              f'p_mean {C["p_signflip_mean"][a]!r} p_vec {C["p_signflip_vec"][a]!r} N {C["N"][a]!r} gain {R["gains"].get(a, "A1")!r}')
    rows.append(dict(a=a, j=int(a[1:]), mean=e['mean'], mF=e['mean'] / F, se=se, ratio=(se / F if se else 0.0),
                     t=(abs(e['mean']) / se if se else float('nan')), k=e['k_neg'], zero=zero, pm=C['p_signflip_mean'][a], pv=C['p_signflip_vec'][a]))
rows = [r for r in rows if not r['zero']] or rows
ratios = sorted(r['ratio'] for r in rows)
q = lambda xs, p: xs[min(len(xs) - 1, int(p * len(xs)))]
print(f'paired SE / F over 69 edges: min {ratios[0]:.3f} q25 {q(ratios, .25):.3f} median {q(ratios, .5):.3f} q75 {q(ratios, .75):.3f} max {ratios[-1]:.3f}')
print(f'edges whose paired SE is below 0.5F: {sum(1 for x in ratios if x < 0.5)} | below 0.25F: {sum(1 for x in ratios if x < 0.25)} | above 2F: {sum(1 for x in ratios if x > 2)}')
paired_clear = [r for r in rows if abs(r['mean']) > 2 * r['se']]
print(f'edges with |mean| > 2 x own paired SE: {len(paired_clear)} of 69 ->', [(r['a'], round(r['mF'], 2), round(r['ratio'], 2)) for r in sorted(paired_clear, key=lambda r: -abs(r['mF']))])
print(f'edges with uncorrected exact sign-flip p_mean < 0.05: {sum(1 for r in rows if r["pm"] < 0.05)} of 69 (chance 3.45)')
print('--- the 12 edges with >= 15 of 16 seeds on one side ---')
for r in sorted([r for r in rows if r['k'] <= 1 or r['k'] >= 15], key=lambda r: -abs(r['mF'])):
    print(f"  {r['a']} mean {r['mF']:+.2f} F | paired SE {r['ratio']:.3f} F (ratio to noise-twin SE {r['ratio']:.3f}) | |mean|/SE {r['t']:.1f} | k_neg {r['k']} | p_mean {r['pm']:.2e} p_vec {r['pv']:.2e} | {'seen' if r['j'] in EJ else 'new'}")
print('--- median |mean|/SE by k_neg class ---')
for lo, hi in ((0, 1), (2, 3), (4, 6), (7, 9), (10, 16)):
    xs = [r['t'] for r in rows if lo <= r['k'] <= hi]
    ys = [r['ratio'] for r in rows if lo <= r['k'] <= hi]
    if xs:
        print(f'  k_neg {lo}-{hi}: n {len(xs)} median |mean|/SE {st.median(xs):.2f} median paired SE/F {st.median(ys):.3f}')
