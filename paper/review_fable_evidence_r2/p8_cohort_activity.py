#!/usr/bin/env python3
"""Round-2 probe 8: how active is each ladder cell? Uses the lab's OWN stored census
(banc/l137/raw_l137.npz: census_ids / census_u / census_x — one intact-closure rollout,
seed 3101, all 58 non-glutamatergic ladder cells) and the stored ladder masses. Read-only."""
import numpy as np, json, os
B = '/home/t3rpz/critters/peabrain-lab/banc'
z = np.load(os.path.join(B, 'l137/raw_l137.npz'))
ids = z['census_ids'].tolist(); X = z['census_x']; U = z['census_u']
print('census arrays:', len(ids), 'cells | x shape', X.shape, '| u shape', U.shape)
xm = X.mean(axis=1) if X.shape[0] == len(ids) else X.mean(axis=0)
# ladder order + masses
cand = None
for f in ['l131/static.json', 'l133/static.json', 'l135/static.json', 'l134/static.json', 'l136/plot_data.json']:
    p = os.path.join(B, f)
    if os.path.exists(p):
        s = json.load(open(p))
        txt = json.dumps(s)
        print(f, 'top keys:', list(s.keys())[:14])
json.dump(dict(ids=ids, x_mean=[float(v) for v in xm]), open('out_p8_census_xmean.json', 'w'))
order = np.argsort(-xm)
print('\ncells with mean rate > .05 (the paper\'s "active" bar): %d of %d ; < .01: %d' % ((xm > .05).sum(), len(ids), (xm < .01).sum()))
print('carrier 1110 x_mean %.4f | twin 319 x_mean %.4f | ratio %.0fx' % (xm[ids.index(1110)], xm[ids.index(319)], xm[ids.index(1110)] / max(xm[ids.index(319)], 1e-9)))
print('sorted x_mean (id:x):', ' '.join('%d:%.3f' % (ids[i], xm[i]) for i in order))
