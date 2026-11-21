# Isolate metric namespace from the simulation. Atomic seed-level summary.
if 'metrics190' not in globals():
    metrics190={}; vs=Path('l187/verdict_l187.py').read_text().splitlines(True)
    exec(''.join(vs[:71]+vs[117:125]),metrics190)
    rows190={}
if seed in FRESH:
    row={}
    for arm in ARMS:
        left,right=metrics190['duty_seeds'](store,arm,[seed],'Ti'); mid=metrics190['duty14_seeds'](store,arm,[seed]); row[arm]=dict(L=float(left[0]),R=float(right[0]),mid=float(mid[0]))
    rows190[str(seed)]=row
atomic_json(f'{OUT}/results_l190.json',dict(status='RAW_COMPLETE' if len(rows190)==16 else 'PARTIAL',seeds=FRESH,rows=rows190,anchors=ANCH_STATE,selection=info,prereg=prereg_sha(),gain={a:GAIN[a] for a in BIS}))
