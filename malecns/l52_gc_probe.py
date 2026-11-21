import json

import numpy as np

res = json.load(open('l52/results_l52.json'))
print('GC block:', json.dumps(res['GC']))
z52 = np.load('l52/traces_l52.npz')
z49 = np.load('l49/traces_l49.npz')
TS = np.arange(499, 10000, 10)
q = (TS >= 4000) & (TS < 10000)
for s in (11, 22, 33):
    SL, SR = z52[f'SL_f07a3_{s}'], z52[f'SR_f07a3_{s}']
    b52 = (SL[TS[q]] >= .25) & (SR[TS[q]] >= .25)
    SL9, SR9 = z49[f'SL_cont_{s}'][:10000], z49[f'SR_cont_{s}'][:10000]
    b49 = (SL9[TS[q]] >= .25) & (SR9[TS[q]] >= .25)
    print(f's{s}: duty52={np.nanmean(b52):.10f} duty49={np.nanmean(b49):.10f} '
          f'equal={np.array_equal(b52, b49)}')
print('rows f07a3:', json.dumps(res['rows']['f07a3'], indent=0)[:400])
print('gates:', res['gates'], '| verdict:', res['verdict'])
print('predictions:', res['predictions'])
print('f14 rows:')
for s in ('11', '22', '33'):
    print(' ', s, res['rows']['f14a3'][s])
