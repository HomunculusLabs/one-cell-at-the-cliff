# L240 A2 second POST-HOC probe (tick 276, unregistered, non-branching):
# (1) BH over the 58 UNSEEN edges only, in both currencies (the declared companion
#     branch is on the 69, and 4 of its 5 vector rejections were edges seen at A1
#     on these same reused seeds);
# (2) the shared-control caveat: every arm is paired to the SAME stored cutwA, so
#     per-edge effects share a common component; the noise twin's own mean offset
#     in F is the scale of that component;
# (3) gains of the rejected / clearing edges vs the stored base gain.
from pathlib import Path
import json
out = Path('l240')
R = json.loads((out / 'results_l240_a2.json').read_text())
R1 = json.loads((out / 'results_l240.json').read_text())
EJ = [4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67]
eff, C = R['effects'], R['companion']
F = R['floor']['F']
new = [int(a[1:]) for a in eff if int(a[1:]) not in EJ]
assert len(new) == 58
def bh(p):
    s = sorted(p.items(), key=lambda kv: kv[1]); m = len(s); k = 0
    for i, (a, v) in enumerate(s, 1):
        if v <= 0.05 * i / m:
            k = i
    return [a for a, _ in s[:k]], {a: v for a, v in s[:max(k, 3)]}
for name, key in (('MEAN', 'p_signflip_mean'), ('VECTOR', 'p_signflip_vec')):
    p = {f'e{j}': C[key][f'e{j}'] for j in new}
    rej, top = bh(p)
    print(f'BH over the 58 unseen edges, {name}: rejected {len(rej)} {rej} | rank-1 bar {0.05 / 58:.3e} | smallest 3:',
          {a: '%.2e' % v for a, v in top.items()})
seen = [f'e{j}' for j in EJ]
for name, key in (('MEAN', 'p_signflip_mean'), ('VECTOR', 'p_signflip_vec')):
    p = {a: C[key][a] for a in seen}
    rej, top = bh(p)
    print(f'BH over the 11 seen edges, {name}: rejected {len(rej)} {rej} | rank-1 bar {0.05 / 11:.3e}')
nt = R1['noise_twin']['per_seed']
import statistics
print(f'noise twin (A1, nf - cutwA): mean {sum(nt) / 16 / F:+.3f} F (SE {statistics.stdev(nt) / 4 / F:.3f} F), sd {statistics.stdev(nt):.3e}, F {F:.6e}')
m69 = [e['mean'] for e in eff.values()]
print(f'per-edge signed means over 69: mean {sum(m69) / 69 / F:+.3f} F, median {statistics.median(m69) / F:+.3f} F, '
      f'positive {sum(1 for v in m69 if v > 0)}/69, S_all {sum(m69):.4e} = {sum(m69) / F:.1f} F')
mn = [eff[f'e{j}']['mean'] for j in new]
print(f'per-edge signed means over the 58 new: mean {sum(mn) / 58 / F:+.3f} F, S {sum(mn):.4e} = {sum(mn) / F:.1f} F, '
      f'positive {sum(1 for v in mn if v > 0)}/58')
G = dict(R['gains'])            # the 58 A2 arms
G.update({a: g for a, g in R1['gains'].items() if a.startswith('e') and isinstance(g, float)})  # the 11 A1 arms
base = 0.14365819573402408
same = [a for a in sorted(G, key=lambda a: int(a[1:])) if G[a] == base]
print(f'arms with gain == stored base gain: {len(same)} of {len(G)} {same}')
for a in ['e14', 'e25', 'e67', 'e12', 'e27', 'e43', 'e45']:
    g = G.get(a)
    print(f'  {a}: gain {g!r}' + ('' if not isinstance(g, float) else f' (delta {g - base:+.3e})'))
sp = R['gates']
print('SPLIT: rho', round(sp['rho'], 4), 'p', sp['p'], 'sign agree', sp['sign_agree'], '/', sp['n_measurable'])
above = [a for a, e in eff.items() if abs(e['in_units_of_F']) > 1]
print('edges with |mean| > 1F:', len(above), sorted(above, key=lambda a: -abs(eff[a]['mean'])))
print('A1 companion (descriptive) above-floor edges were: e14, e25, e67, e12; vector floor A1 0.00533 vs floorN now', C['floorN'])
