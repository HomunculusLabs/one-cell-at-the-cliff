"""Cross-check the numbers quoted in DUCKROUTE-FINDINGS.md against the stored results. Read-only."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
R = json.loads((D / 'results.json').read_text()); H = json.loads((D / 'results_heldout.json').read_text())
v = [x['fear'] for s in (0, 1) for c in json.loads((D.parent / 'duckplast2' / 'out' / f'seed{s}_frozen.json').read_text())['sessions']['S1'].values() for x in c]
print('fear == 0 share', sum(x == 0 for x in v) / len(v), '| rounds to 0', sum(round(x, 3) == 0 for x in v) / len(v))
for T, X in (('primary', R['primary']), ('heldout', H['heldout'])):
    for rg in ('B', 'Bn', 'Bj'):
        fl = X[rg]['flips_R']
        d = [f['food_joy'][1] - f['food_joy'][0] for f in fl if 'food_joy' in f['crossed']]
        fz = [f['food_joy'][0] for f in fl if 'food_joy' in f['crossed']]
        sl = sorted({round(abs(f['sleep'][1] - f['sleep'][0]), 4) for f in fl if 'sleep' in f['crossed']})
        print(T, rg, 'fj gain', round(min(d), 4), round(max(d), 4), '| frozen fj', round(min(fz), 4), round(max(fz), 4),
              '| sleep diffs', sl, '| all near', X[rg]['N_near'] == X[rg]['N_all'])
    print(T, 'BC', X['BC']['N_all'], 'Q4', X['BC']['Q4']['supported'], '| reply flips by regime',
          [X[k]['structural']['reply_flips_all_sessions'] for k in X])
print('minutes', [(s, a, round(json.loads((D / 'out' / f'seed{s}_{a}.json').read_text())['seconds'] / 60, 1)) for s in (2, 3) for a in ('frozen', 'plastic')])
