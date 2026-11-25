# Isolate metric namespace from the simulation. Atomic progress record (per seed).
if 'pools240' not in globals():
    pools240 = {pk: [int(i) for i in np.atleast_1d(POOLS['cutwA'][pk])] for pk in POOLS['cutwA']}
    atomic_json(f'{OUT}/pools_w{WID}.json', dict(
        wid=WID, pools=pools240, n_pools=len(pools240),
        n_union=len(set(sum(pools240.values(), []))), sizes={pk: len(v) for pk, v in pools240.items()}))
done240 = [int(_s) for _s in FRESH if f'mm_cutwA_{_s}' in store]
atomic_json(f'{OUT}/progress_w{WID}.json', dict(
    wid=WID, arms=['cutwA'] + MY_ARMS, seeds_done=done240, prereg=prereg_sha(),
    gain={a: GAIN[a] for a in ['cutwA'] + MY_ARMS}, secs=time.time() - t0))
