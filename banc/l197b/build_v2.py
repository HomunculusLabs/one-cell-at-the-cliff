"""L197b builder: count-asserted transform of the certified L186 harness
banc/l186/run.py (itself sliced from l175/scan_run.py by l186/build.py) ->
banc/l197b/run_v2.py. Run from banc/. The ONLY changes: seed list (per-worker
slice of the pre-drawn schedule), output paths, PREREG/schedule freeze
asserts, and the gate-schedule block (two design arms instead of one). The
dynamics, bisect, RNG mapping, C0A anchor, GI-1110 recording are VERBATIM."""
import hashlib
import py_compile

s = open("l186/run.py").read()
SHA = hashlib.sha256(s.encode()).hexdigest()
assert SHA == "0f283b58c67ffccab539e7654da69fdb46925992cff27715712dd7ad25934dcb", SHA
N = 0


def rep(old, new):
    global s, N
    assert s.count(old) == 1, (old[:60], s.count(old))
    s = s.replace(old, new)
    N += 1


rep("B39=list(range(18601,18617)); SEEDS=ANCH_BIT+B39\n",
    "sys.path.insert(0, 'l197b')\n"
    "import gj\n"
    "import hashlib\n"
    "SCHED = json.load(open('l197b/schedule.json'))\n"
    "_FRZ = json.load(open('l197b/FREEZE.json'))\n"
    "assert hashlib.sha256(open('l197b/PREREG.md','rb').read()).hexdigest() == _FRZ['prereg_sha256'], 'PREREG changed after freeze (STOP)'\n"
    "assert hashlib.sha256(open('l197b/schedule.json','rb').read()).hexdigest() == _FRZ['schedule_sha256'], 'schedule changed after freeze (STOP)'\n"
    "assert SCHED['gate']['pass'] is True, 'overlap gate REFUSED — no rollout'\n"
    "assert all(SCHED['arms'][a]['overlap']['mean_overlap'] <= .25 for a in ('S', 'W'))\n"
    "SEEDS_S, SEEDS_W = SCHED['arms']['S']['seeds'], SCHED['arms']['W']['seeds']\n"
    "assert NW == 6 and 0 <= WID < NW\n"
    "B39 = SEEDS_S[WID::NW] + SEEDS_W[WID::NW]   # this worker's fresh seeds\n"
    "SEEDS = ANCH_BIT + B39\n")
rep('OUT="l186"\n', 'OUT="l197b"\n')
rep("RAW_PATH,XM_PATH=OUT+'/raw.npz',OUT+'/xm.npz'; GAINS_PATH=OUT+'/gains.json'\n",
    "RAW_PATH,XM_PATH=OUT+f'/raw_w{WID}.npz',OUT+f'/xm_w{WID}.npz'; GAINS_PATH=OUT+f'/gains_w{WID}.json'\n")
rep("ANCH_PATH=OUT+'/anchors.json'\n", "ANCH_PATH=OUT+f'/anchors_w{WID}.json'\n")
rep("    if seed not in ANCH_BIT:\n"
    "        for b,j in zip((0,4000),np.random.default_rng(np.random.SeedSequence([186,seed])).integers(-300,301,2)):\n"
    "            AMPA[b+900:b+1400]=0\n"
    "            AMPA[b+900+j:b+1400+j]=ENT_AMP\n",
    "    if seed not in ANCH_BIT:\n"
    "        _arm = 'S' if seed in SEEDS_S else 'W'\n"
    "        _P = gj.DESIGN[_arm]['pulse']\n"
    "        _on = gj.draw_onsets(_arm, seed)\n"
    "        assert _on == SCHED['arms'][_arm]['onsets'][str(seed)], 'schedule drift (STOP)'\n"
    "        for b,o in zip((0,4000),_on):\n"
    "            AMPA[b+900:b+1400]=0\n"
    "            assert not AMPA[b+500:b+1800].any()\n"
    "            AMPA[b+o:b+o+_P]=ENT_AMP\n"
    "        assert np.array_equal(AMPA>0, gj.expected_gate(_arm, _on))\n"
    "    else:\n"
    "        assert np.array_equal(AMPA, canonical)\n")
rep('log(f"rollouts done {time.time()-t0:.0f}s")\n',
    'log(f"rollouts done {time.time()-t0:.0f}s")\n'
    "assert json.load(open(ANCH_PATH))['c0a_pass']\n"
    "atomic_json(OUT+f'/done_w{WID}.json', dict(wid=WID, nw=NW, seeds=SEEDS, n_fresh=len(B39),\n"
    "    gain={a: GAIN[a] for a in ['cutwA']+MY_ARMS}, prereg_sha256=_FRZ['prereg_sha256'], secs=time.time()-t0))\n"
    'log(f"worker {WID} DONE {time.time()-t0:.0f}s")\n')
assert "186" not in s.split("# ---------------- rollouts ----------------")[1], "stale v1 schedule code"
for keep in ("            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]\n"
             "            if sin_t > 0:\n"
             "                drive[mech[a], 0] = drive[mech[a], 0] + sin_t\n"
             "            t = torch.relu(drive + BG)\n"
             "            t = (t + noise[a]).clamp(max=RMAX)\n"
             "            X[a] = X[a] + (DT / TAU) * (t - X[a])\n",
             "        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0\n",
             "        carrier[k]=X['cutwA'][loc_wA[1110],0].item()\n",
             "    store[f'gate_{seed}']=AMPA>0\n"):
    assert s.count(keep) == 1, keep[:50]
open("l197b/run_v2.py", "w").write(s)
py_compile.compile("l197b/run_v2.py", doraise=True)
print(f"l197b/run_v2.py written: {s.count(chr(10))} lines, {N} rep sites, src sha {SHA[:12]}")
