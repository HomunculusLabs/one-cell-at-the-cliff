"""Descriptive (not registered): her solo-life ambient under the food_joy-only placement, from stored day ticks.
Exact where it can be: the food_joy branch sits below hunger/sleep/fear/parade and above curiosity/stay, so a
stored ambient of stay / to_fence / to_boot-by-curiosity becomes to_pond iff round(food_joy,3) > thr."""
import json, collections
from pathlib import Path
D = Path(__file__).resolve().parent
P70 = json.loads((D / 'results.json').read_text())['P70']['food_joy']
out = {}
for base, seeds in ((D.parent / 'duckplast2' / 'out', (0, 1)), (D / 'out', (2, 3))):
    for s in seeds:
        r = json.loads((base / f'seed{s}_frozen.json').read_text())
        a = collections.Counter(); b = collections.Counter(); fear_hi = 0
        for d in r['days']:
            for act, amb, fear, fj, sal, sleep, hunger, cur in d['ticks']:
                a[amb] += 1
                below = amb in ('stay', 'to_fence') or (amb == 'to_boot' and round(fear, 3) <= .4)   # branches under food_joy
                b['to_pond' if (below and round(fj, 3) > P70) else amb] += 1
        out[s] = dict(asis=dict(a), Bj=dict(b), ticks=sum(a.values()))
        print(s, 'as-is', dict(a), '\n   Bj  ', dict(b))
(D / 'world_read.json').write_text(json.dumps(out, indent=1))
