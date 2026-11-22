"""L199 builder: count-asserted transform of the certified L186 harness
banc/l186/run.py (sha-pinned; L197b's run_v2.py has the same parent) ->
banc/l199/run_tp.py. Run from banc/. The ONLY changes: seed/tag list
(per-worker slice), output paths, PREREG freeze asserts, the gate block
(canonical schedule for every rollout), the tone-phase shift (+pi for tags
>= 50000, +0.0 otherwise), the RNG seed of a tag (= its base seed), a stored
tone trace, and a .tmp.npz-tolerant key-scan (L200 writes concurrently).
Dynamics, bisect, RNG mapping, C0A anchor: VERBATIM."""
import hashlib
import py_compile

s = open("l186/run.py").read()
SHA = hashlib.sha256(s.encode()).hexdigest()
assert SHA == "0f283b58c67ffccab539e7654da69fdb46925992cff27715712dd7ad25934dcb", SHA
MARK = "# ---------------- rollouts ----------------"
assert s.count(MARK) == 1
N = 0


def rep(old, new, tail=False):
    """Replace exactly one site (tail=True: the site must be unique within the
    rollout section; the head is left untouched)."""
    global s, N
    if tail:
        head, tl = s.split(MARK)
        assert tl.count(old) == 1, (old[:60], tl.count(old))
        s = head + MARK + tl.replace(old, new)
    else:
        assert s.count(old) == 1, (old[:60], s.count(old))
        s = s.replace(old, new)
    N += 1


rep("B39=list(range(18601,18617)); SEEDS=ANCH_BIT+B39\n",
    "import hashlib\n"
    "_FRZ = json.load(open('l199/FREEZE.json'))\n"
    "assert hashlib.sha256(open('l199/PREREG.md','rb').read()).hexdigest() == _FRZ['prereg_sha256'], 'PREREG changed after freeze (STOP)'\n"
    "BASE = list(range(19931, 19947)); TAGOFF = 50000\n"
    "assert _FRZ['causal_seeds'] == BASE and _FRZ['tag_offset'] == TAGOFF\n"
    "assert NW == 3 and 0 <= WID < NW\n"
    "B39 = BASE[WID::NW] + [TAGOFF + x for x in BASE[WID::NW]]   # phi0 seeds, then phiPI tags\n"
    "SEEDS = ANCH_BIT + B39\n")
rep('OUT="l186"\n', 'OUT="l199"\n')
rep("    if archive.parts[0]==OUT: continue\n",
    "    if archive.parts[0]==OUT or archive.name.endswith('.tmp.npz'): continue\n")
rep("RAW_PATH,XM_PATH=OUT+'/raw.npz',OUT+'/xm.npz'; GAINS_PATH=OUT+'/gains.json'\n",
    "RAW_PATH,XM_PATH=OUT+f'/raw_w{WID}.npz',OUT+f'/xm_w{WID}.npz'; GAINS_PATH=OUT+f'/gains_w{WID}.json'\n")
rep("ANCH_PATH=OUT+'/anchors.json'\n", "ANCH_PATH=OUT+f'/anchors_w{WID}.json'\n")
rep("    if seed not in ANCH_BIT:\n"
    "        for b,j in zip((0,4000),np.random.default_rng(np.random.SeedSequence([186,seed])).integers(-300,301,2)):\n"
    "            AMPA[b+900:b+1400]=0\n"
    "            AMPA[b+900+j:b+1400+j]=ENT_AMP\n",
    "    assert np.array_equal(AMPA, canonical)          # L199: canonical gate for EVERY rollout\n"
    "    _SHIFT = math.pi if seed >= TAGOFF else 0.0     # phiPI tag: tone shifted half a 0.7-Hz period\n"
    "    _RS = seed - TAGOFF if seed >= TAGOFF else seed  # RNG seed of a tag = its base seed\n"
    "    assert (seed in ANCH_BIT and _SHIFT == 0.0 and _RS == seed) or (seed in B39 and _RS in BASE)\n"
    "    tone_tr = np.zeros(WIN, np.float64)\n")
rep("    gen = torch.Generator().manual_seed(seed)\n"
    "    gen2 = torch.Generator().manual_seed(seed + 9000)\n",
    "    gen = torch.Generator().manual_seed(_RS)\n"
    "    gen2 = torch.Generator().manual_seed(_RS + 9000)\n", tail=True)
rep("        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k])) if AMPA[k] > 0 else 0.0\n",
    "        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(PHI[k] + _SHIFT)) if AMPA[k] > 0 else 0.0\n"
    "        tone_tr[k] = sin_t\n")
rep("    store[f'GI1110_cutwA_{seed}']=carrier\n",
    "    store[f'GI1110_cutwA_{seed}']=carrier\n"
    "    store[f'tone_{seed}']=tone_tr\n")
rep('log(f"rollouts done {time.time()-t0:.0f}s")\n',
    'log(f"rollouts done {time.time()-t0:.0f}s")\n'
    "assert json.load(open(ANCH_PATH))['c0a_pass']\n"
    "atomic_json(OUT+f'/done_w{WID}.json', dict(wid=WID, nw=NW, seeds=SEEDS, n_fresh=len(B39),\n"
    "    gain={a: GAIN[a] for a in ['cutwA']+MY_ARMS}, prereg_sha256=_FRZ['prereg_sha256'], secs=time.time()-t0))\n"
    'log(f"worker {WID} DONE {time.time()-t0:.0f}s")\n')
tl = s.split(MARK)[1]
assert "186" not in tl, "stale v1 schedule code"
assert tl.count("manual_seed(") == 2 and tl.count("manual_seed(_RS") == 2
for keep in ("            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]\n"
             "            if sin_t > 0:\n"
             "                drive[mech[a], 0] = drive[mech[a], 0] + sin_t\n"
             "            t = torch.relu(drive + BG)\n"
             "            t = (t + noise[a]).clamp(max=RMAX)\n"
             "            X[a] = X[a] + (DT / TAU) * (t - X[a])\n",
             "        sp += 2 * math.pi * 0.7 * DT\n        sin_t = ENT_AMP * (0.5 + 0.5 * math.sin(sp))\n        for a in ARMS:\n            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]\n",
             "        carrier[k]=X['cutwA'][loc_wA[1110],0].item()\n",
             "    store[f'gate_{seed}']=AMPA>0\n",
             "canonical=AMPA.copy()\nfor seed in SEEDS:\n    AMPA=canonical.copy()\n"):
    assert s.count(keep) == 1, keep[:50]
open("l199/run_tp.py", "w").write(s)
py_compile.compile("l199/run_tp.py", doraise=True)
print(f"l199/run_tp.py written: {s.count(chr(10))} lines, {N} rep sites, src sha {SHA[:12]}")
