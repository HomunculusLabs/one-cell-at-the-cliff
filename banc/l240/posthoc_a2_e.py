# L240 A2 fifth POST-HOC probe (tick 276, unregistered, non-branching):
# the 8 bit-identical arms -- was the edge actually DELETED? Reads the harness's
# own record (arms_w*.json: removed[0] = csr_index / effective_weight / sign / syn /
# target) and the settle-only operating point of the target if the harness stored
# it. Read-only.
import json
from pathlib import Path
out = Path('l240')
noop = ['e1', 'e2', 'e8', 'e9', 'e16', 'e21', 'e47', 'e55']
ctrl = ['e37', 'e61', 'e42', 'e43', 'e45', 'e27']
rec = {}
for w in range(0, 10):
    f = out / f'arms_w{w}.json'
    if not f.exists():
        continue
    A = json.loads(f.read_text())
    for name, e in A['edges'].items():          # dict keyed by arm name
        if name in noop or name in ctrl:
            rec.setdefault(name, (w, e))
print('arms file keys of worker 3:', sorted(json.loads((out / 'arms_w3.json').read_text()).keys()))
w0, e0 = rec['e1']
print('edge record keys:', sorted(e0.keys()), '| removed[0] keys:', sorted(e0['removed'][0].keys()))
print('top-level keys mentioning settle/af/oppoint:', [k for k in json.loads((out / f'arms_w{w0}.json').read_text()) if any(t in k.lower() for t in ('settle', 'af', 'op', 'x0', 'xmean'))])
for k in noop + ctrl:
    w, e = rec[k]
    r = e['removed']
    assert len(r) == 1, (k, len(r))
    r = r[0]
    print(f"{k} (w{w}): csr_index {r.get('csr_index')} | effective_weight {r.get('effective_weight')!r} | syn {r.get('syn')} | sign {r.get('sign')} | "
          f"target {r.get('target')} | syn_raw {e.get('syn_raw')!r}")
# a nonzero effective weight for every one = the deletion removed real mass
bad = [k for k in noop if not rec[k][1]['removed'][0].get('effective_weight')]
print('no-op arms whose removed edge has a ZERO/absent effective weight (would mean a silent non-deletion):', bad)
