# L240 A2 POST-HOC DESCRIPTIVES (tick 276). Reads results_l240_a2.json AFTER
# final_a2.py has written it. Non-branching, unregistered, labelled post hoc:
# (a) the per-edge SIGN-COUNT histogram and the exact sign-flip test's attainable
#     p-values against its own BH rank-1 bar (the L225/L232 resolution-floor duty);
# (b) FLOOR clears split by subset (the 11 edges seen at A1 vs the 58 new);
# (c) the largest-member share of the sum of singles over the 58 new only.
# Nothing here resembles the metric comparison (NOT READ when the gates fail).
from pathlib import Path
import json, math
out = Path('l240')
R = json.loads((out / 'results_l240_a2.json').read_text())
assert R['status'] == 'FINAL'
EJ = [4, 12, 13, 14, 25, 38, 39, 59, 62, 64, 67]
eff = R['effects']
meas = sorted(int(a[1:]) for a in eff)
m = len(meas)
q = 0.05
bar1 = q / m
# (a) sign-count histogram
hist = {k: 0 for k in range(17)}
for a in eff.values():
    hist[a['k_neg']] += 1
att = {}
for k in range(9):
    p = 2 * sum(math.comb(16, i) for i in range(k + 1)) / 65536
    att[k] = dict(p_two_sided=p, min_k_neg_consistency=f'{16 - k}/16 one sign',
                  max_bh_rank_rejectable=(int(math.floor(p * m / q)) if p <= bar1 * m else 0))
n_cons15 = sum(hist[k] for k in (0, 1, 15, 16))
n_cons14 = sum(hist[k] for k in (0, 1, 2, 14, 15, 16))
# (b) FLOOR clears by subset
cl = R['floor']['clears']
sub = {}
for name, js in (('seen11', EJ), ('new58', [j for j in meas if j not in EJ])):
    sub[name] = dict(n=len(js), clears=int(sum(cl[f'e{j}'] for j in js)))
# (c) largest-member share over the 58 new only
new = [(abs(eff[f'e{j}']['mean']), j) for j in meas if j not in EJ]
new.sort(reverse=True)
S_new = sum(eff[f'e{j}']['mean'] for j in meas if j not in EJ)
absum_new = sum(v for v, _ in new)
top = [dict(edge=f'e{j}', target=eff[f'e{j}']['target'], syn=eff[f'e{j}']['syn'],
            mean_F=eff[f'e{j}']['in_units_of_F'], k_neg=eff[f'e{j}']['k_neg'],
            H1_F=eff[f'e{j}']['H1'] / R['floor']['F'], H2_F=eff[f'e{j}']['H2'] / R['floor']['F'])
       for _, j in new[:8]]
res = dict(label='POST HOC, unregistered, non-branching (tick 276)', n_measurable=m,
           sign_count_hist={str(k): hist[k] for k in range(17)},
           n_edges_ge15_of_16_one_sign=n_cons15, n_edges_ge14_of_16_one_sign=n_cons14,
           signflip_attainable=att, bh_rank1_bar=bar1,
           M_rej=R['companion']['M_rej'], V_rej=R['companion']['V_rej'],
           floor_clears_by_subset=sub,
           new58=dict(S_signed=S_new, S_abs=absum_new,
                      top1_share_of_abs_sum=new[0][0] / absum_new if absum_new else None,
                      top1_share_of_abs_S=new[0][0] / abs(S_new) if S_new else None, top8=top),
           n_positive_mean=int(sum(1 for a in eff.values() if a['mean'] > 0)),
           n_abs_gt_1F=int(sum(1 for a in eff.values() if abs(a['in_units_of_F']) > 1)),
           n_abs_gt_2F=int(sum(1 for a in eff.values() if abs(a['in_units_of_F']) > 2)),
           n_abs_gt_3F=int(sum(1 for a in eff.values() if abs(a['in_units_of_F']) > 3)),
           median_abs_in_F=sorted(abs(a['in_units_of_F']) for a in eff.values())[m // 2])
(out / 'posthoc_a2.json').write_text(json.dumps(res, indent=1))
print('POST HOC (unregistered): measurable', m)
print('sign-count hist (k_neg -> n):', ' '.join(f'{k}:{hist[k]}' for k in range(17) if hist[k]))
print('edges >=15/16 one sign:', n_cons15, '| >=14/16:', n_cons14, '| BH rank-1 bar', round(bar1, 6))
for k in range(4):
    print(f"  k_neg<={k} or >={16 - k}: p = {att[k]['p_two_sided']:.3e} -> rejectable up to BH rank {att[k]['max_bh_rank_rejectable']}")
print('M_rej', R['companion']['M_rej'], 'V_rej', R['companion']['V_rej'], R['companion']['branch'])
print('FLOOR clears by subset:', sub)
print('new58: S_signed', S_new, 'S_abs', absum_new, 'top1 share of abs sum', res['new58']['top1_share_of_abs_sum'],
      'top1 share of |S|', res['new58']['top1_share_of_abs_S'])
print('n |mean| > 1F / 2F / 3F:', res['n_abs_gt_1F'], res['n_abs_gt_2F'], res['n_abs_gt_3F'],
      '| n positive', res['n_positive_mean'], '| median |effect| in F', round(res['median_abs_in_F'], 3))
for t in top:
    print(f"  {t['edge']} -> {t['target']} syn {t['syn']}: {t['mean_F']:+.2f} F, k_neg {t['k_neg']}, H1 {t['H1_F']:+.2f} F, H2 {t['H2_F']:+.2f} F")
