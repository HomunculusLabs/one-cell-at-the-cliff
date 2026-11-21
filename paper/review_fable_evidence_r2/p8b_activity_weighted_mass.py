#!/usr/bin/env python3
"""Round-2 probe 8b: activity of the cells each control removes. Sources: the lab's stored l137
census (intact closure, ONE seed 3101) via out_p8_census_xmean.json; cohort memberships from
banc/l125,l127,l128,l133 static.json. Static mass per set as stored. Read-only."""
import json, os
B = '/home/t3rpz/critters/peabrain-lab/banc'
c = json.load(open('out_p8_census_xmean.json'))
xm = dict(zip(c['ids'], c['x_mean']))
p25 = json.load(open(os.path.join(B, 'l133/static.json')))['xor25p']['cutng25p']['drop_ids']
wA = sorted(set(p25) - {319})
scr = {}
for f in [x for x in ['l125/static.json', 'l127/static.json', 'l128/static.json', 'l126/static.json'] if os.path.exists(os.path.join(B, x))]:
    d = json.load(open(os.path.join(B, f))).get('scr', {})
    for k, v in d.items():
        scr.setdefault(k, v)
k19 = sorted(set(scr['cutscr0']['drop_ids']) - set(scr['cutscr0']['extra_ids_desc']))
r2024 = sorted(set(wA) - set(k19))
def desc(name, ids, mass=None):
    xs = sorted(((xm.get(i, float('nan')), i) for i in ids), reverse=True)
    act = sum(1 for x, _ in xs if x > .05)
    print('%-28s n=%2d  static mass %s  sum(x_mean)=%.3f  active(>.05): %d  silent(<.01): %d | %s'
          % (name, len(ids), ('%.4f' % mass) if mass is not None else '  -   ', sum(max(x, 0) for x, _ in xs), act,
             sum(1 for x, _ in xs if x < .01), ' '.join('%d:%.2f' % (i, x) for x, i in xs)))
print('k19 prefix is the scramble base: %d cells; cutwA adds ranks 20-24: %s' % (len(k19), r2024))
desc('k=19 prefix', k19)
desc('ranks 20-24 (k19 -> cutwA)', r2024)
desc('CARRIER (rank 25, id 1110)', [1110], 0.006436)
desc('TWIN (rank 26, id 319)', [319], 0.006045)
print()
for k in sorted(scr):
    v = scr[k]
    ex = v.get('extra_ids_desc') or sorted(set(v['drop_ids']) - set(k19))
    desc(k + ' extra cells', ex, v.get('extra_mass'))
print('\nright-side outcome (canonical unique seeds, from out_p2): cutscr0 41/50 | cutscr3 18/34 | cutscrL1 11/18 | cutscr2 12/34 | cutscrL2 4/18 | cutcl40 0/18 | cutscr1 0/34')
