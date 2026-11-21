# L154 build: transform l150_run.py -> l154_run.py (count-asserted splices).
# PREREG l154/PREREG.md + ADDENDUM 2 registered BEFORE this build.
# Transform: ARMS -> [b65(on), off]; off = b65 substrate VERBATIM (same CSR
# object, same G65), mech sinusoid removed ENTIRE run (settle + WIN);
# settle_states/bisect block DELETED (no bisects: stored G65 constant);
# seeds ANCH 801/901 + B34 3401-3416; anchors vs raw_l150.npz b65.
import py_compile

SRC = "l150_run.py"
DST = "l154_run.py"
s = open(SRC).read()
n0 = len(s)


def splice_unique(s, opener, closer_inc, new, keep_opener=False):
    i = s.count(opener)
    assert i == 1, ("opener count", opener[:50], i)
    a = s.index(opener)
    j = s.count(closer_inc)
    assert j == 1, ("closer count", closer_inc[:50], j)
    b = s.index(closer_inc, a) + len(closer_inc)
    return s[:a] + new + s[b:]


def rep(s, old, new, count):
    c = s.count(old)
    assert c == count, ("rep count", old[:60], c, count)
    return s.replace(old, new)


# 1. docstring
DOC = '''"""L154 run: Sapkal deprivation arms (PREREG l154/PREREG.md FIRST +
ADDENDUM 2, registered before this build). Arms: b65 (= on, l150 form
VERBATIM — C0A-154 bit-anchor vs raw_l150.npz at 801/901) and off (b65
graph VERBATIM same CSR object, same stored G65=0.14, DNg100 command D ON,
mech sensory sinusoid REMOVED for the ENTIRE run incl. settle — Sapkal
FeCO-deafferentation analog at rate fidelity). FRESH B34 3401-3416 +
anchors 801/901. No bisects (graph-identity gain, l144 A1 form). CPU-only;
raw checkpoint BEFORE analysis. Metric machinery + verdict: l154_verdict.py.
"""'''
s = splice_unique(s, '"""L150 run:', 'own batch — see its results json; not re-rolled here.)\n"""', DOC)

# 2. ARMS / GAIN
s = rep(s, '''ARMS = ["full", "b65", "cutwA", "cutng25", "silW", "eMotTop5",
        "eMotBot5"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            silW=None, eMotTop5=None, eMotBot5=None)  # silW below (graph-id)''',
        '''ARMS = ["b65", "off"]   # on = b65 (l150 verbatim); off = same graph,
#  sinusoid removed entire run (l154/PREREG.md + ADDENDUM 2)
GAIN = dict(b65=G65, off=G65)  # stored constant both arms, graph-identity''', 1)

# 3. seeds
s = rep(s, '''ANCH = [801, 901]                   # bit-identity anchors (excluded from sample)
B33 = list(range(3365, 3381))  # fresh (batch lineage in PREREG)
SEEDS = ANCH + B33                  # anchors FIRST: early wiring verdict
FRESH = B33''',
        '''ANCH = [801, 901]              # C0A-154 vs l150 STORED b65 (ADDENDUM 2:
#  11/22/33 were l150's BISECT anchors — mis-carry corrected from artifacts)
B34 = list(range(3401, 3417))  # fresh batch (absence-verified, ADDENDUM 2)
SEEDS = ANCH + B34             # anchors FIRST: early wiring verdict
FRESH = B34''', 1)

# 4. off aliases (before AMPA block)
OFFAL = '''# ---- L154: off = b65 substrate VERBATIM, mech sinusoid removed ----
POOLS["off"] = POOLS["b65"]
mech["off"] = mech["b65"]
motor["off"] = motor["b65"]
dng100["off"] = dng100["b65"]
WB["off"] = WB["b65"]   # same CSR object: graph identical by construction
N_OF["off"] = N_OF["b65"]

AMPA = np.zeros(WIN, np.float64)'''
s = rep(s, "AMPA = np.zeros(WIN, np.float64)", OFFAL, 1)

# 5. DELETE settle machinery + bisects (settle_states dead: main loop
#    re-implements settle inline; no bisects — stored G65, l144 A1 form)
a = s.index("# ---------------- settle machinery (l94 two-generator form) ----------------")
b = s.index("# ---------------- rollouts ----------------")
NOBIS = '''# ---------------- L154: no bisects (stored G65 constant) ----------------
assert G65 == 0.14, "G65 constant drifted"
assert GAIN["b65"] == GAIN["off"] == G65, "gain identity broken (STOP)"
log(f"gains: b65=off=G65={G65} stored constant (graph-identity, no bisect)")

'''
s = s[:a] + NOBIS + s[b:]

# 6. resume paths -> OWN dir (l118 class: never follow a prior run's partial)
s = rep(s, '''if os.path.exists("l150/raw_partial.npz"):
    z = np.load("l148/raw_partial.npz")''',
        '''if os.path.exists("l154/raw_partial.npz"):
    z = np.load("l154/raw_partial.npz")''', 1)

# 7. skip-check token (arm set changed)
s = rep(s, 'if f"mm_full_{seed}" in store:', 'if f"mm_b65_{seed}" in store:', 1)

# 8. X dict: off shares b65's X0 (L45b: draw once, clone per arm)
s = rep(s, "             b65=Xo65.clone())",
        "             b65=Xo65.clone(), off=Xo65.clone())", 1)

# 9. noise dicts (2 sites after deletion: main settle + WIN)
s = rep(s, "b65=nz_o)", "b65=nz_o, off=nz_o)", 2)

# 10. sin guards (settle_states copy died with the block; 2 sites remain)
s = rep(s, '''            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            drive[mech[a], 0] = drive[mech[a], 0] + sin_t''',
        '''            drive = torch.sparse.mm(WB[a], X[a]) * GAIN[a] + Iv[a]
            if a != "off":   # L154 off: no mech sinusoid, entire run
                drive[mech[a], 0] = drive[mech[a], 0] + sin_t''', 1)
s = rep(s, "            if sin_t > 0:",
        '            if sin_t > 0 and a != "off":   # L154 off: sensory drive gone', 1)

# 11. partial checkpoint path
s = rep(s, 'np.savez("l150/raw_partial.npz", **store)',
        'np.savez("l154/raw_partial.npz", **store)', 1)

# 12. final savez -> lean l154 form
a = s.index('np.savez_compressed("l150/raw_l150.npz", K=K,')
b = s.index('log("raw_l150.npz checkpointed BEFORE analysis")')
b += len('log("raw_l150.npz checkpointed BEFORE analysis")')
s = s[:a] + '''np.savez_compressed("l154/raw_l154.npz", g65=G65,
                    arms=np.array(ARMS), batches=np.array(SEEDS),
                    ent_amp=ENT_AMP, **store)
log("raw_l154.npz checkpointed BEFORE analysis")''' + s[b:]

# 13. tail: anchors vs l150 STORED b65 + B34 absence
a = s.index("# ---------------- C0A-142 (L142): anchors vs raw_l135 + B29 absence -----")
TAIL = '''# ---------------- C0A-154: b65 vs l150 STORED + B34 absence ----------------
import os as _os
_prevs = ["l115/raw_l115.npz", "l117/raw_l117.npz", "l118/raw_l118.npz",
          "l119/raw_l119.npz", "l120/raw_l120.npz", "l121/raw_l121.npz",
          "l122/raw_l122.npz", "l123/raw_l123.npz", "l124/raw_l124.npz",
          "l125/raw_l125.npz", "l126/raw_l126.npz", "l127/raw_l127.npz",
          "l128/raw_l128.npz", "l131/raw_l131.npz", "l133/raw_l133.npz",
          "l135/raw_l135.npz", "l137/raw_l137.npz",
          "l139/raw_l139_j0.npz", "l139/raw_l139_j1.npz",
          "l139/raw_l139_j2.npz", "l139/raw_l139_j3.npz",
          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",
          "l113/raw_l113.npz", "l142/raw_l142.npz",
          "l144/raw_l144.npz", "l145/raw_l145.npz",
          "l142/raw_partial.npz", "l144/raw_partial.npz",
          "l145/raw_partial.npz", "l148/raw_l148.npz",
          "l148/raw_partial.npz", "l150/raw_l150.npz",
          "l150/raw_partial.npz"]
# prior runs ONLY — never this run's own output (l118/L120 direction law:
# B34 lives in OUR partial by design)
_prevs = [p for p in _prevs if _os.path.exists(p)]
for _p in _prevs:
    _zp = np.load(_p)
    assert not any(f"mm_b65_{s_}" in _zp.files for s_ in B34), \\
        ("B34 collides with " + _p + " (STOP)")
log(f"B34 absence across {len(_prevs)} stored npzs: PASS")
_poolkeys154 = []
for _pk, (_ag, _bg) in (("Ti", ("f", "e")), ("Tr", ("f", "e")),
                        ("Ta", ("a", "b")), ("Sr", ("a", "b")),
                        ("Pr", ("a", "b"))):
    for _c in (_ag, _bg):
        for _s in ("L", "R"):
            _poolkeys154.append(f"{_pk}_{_c}{_s}")
C0A154_KEYS = ["mm", "xm"] + _poolkeys154
z150c = np.load("l150/raw_l150.npz")
assert all(f"{_k}_b65_{s_}" in z150c.files for _k in C0A154_KEYS
           for s_ in (801, 901)), "C0A-154 coverage miss"
c0a154 = {}
for s_ in (801, 901):
    for key in C0A154_KEYS:
        c0a154[f"{key}_b65_{s_}"] = float(np.abs(
            store[f"{key}_b65_{s_}"] - z150c[f"{key}_b65_{s_}"][:WIN]).max())
    c0a154[f"af_b65_{s_}"] = abs(float(store[f"af_b65_{s_}"])
                                 - float(z150c[f"af_b65_{s_}"]))
c0a154_max = max(c0a154.values())
c0a154_pass = bool(all(v == 0.0 for v in c0a154.values()))
out154 = dict(g65=G65, n_seeds=len(SEEDS), anchors=ANCH, fresh=FRESH,
              c0a154_max=c0a154_max, c0a154_pass=c0a154_pass,
              b34_absence_npzs=len(_prevs))
json.dump(out154, open("l154/anchors_run.json", "w"), indent=1)
log(f"C0A-154 b65 (on) vs l150 STORED ({len(C0A154_KEYS)} keys x 2 seeds + af): "
    f"{'PASS' if c0a154_pass else 'FAIL'} (max {c0a154_max:.1e}) | "
    f"done {time.time()-t0:.0f}s")
assert c0a154_pass, "C0A-154 FAIL (STOP before verdict)"
'''
s = s[:a] + TAIL

open(DST, "w").write(s)
py_compile.compile(DST, doraise=True)

# residual scan (code lines; comment/docstring lines whitelisted by context)
import re as _re
bad = []
for ln, line in enumerate(s.splitlines(), 1):
    st = line.strip()
    if st.startswith("#") or st.startswith('"""'):
        continue
    if st and all(_re.match(r'^"?[^"]+\.npz"?$', t.strip().rstrip(','))
                  for t in st.strip('[]').split(',') if t.strip()):
        continue  # deliberate cross-run input/output path list entries
    for tok in ("B33", "mm_full_", '"l150/raw_partial', '"l148/raw_partial',
                "bisect_af_mean", "settle_states", "ARMS = [\"full\""):
        if tok in line:
            bad.append((ln, tok, line.strip()[:70]))
assert not bad, ("residual scan FAIL", bad[:8])
assert s.count('a != "off"') == 2
assert s.count("b65=nz_o, off=nz_o)") == 2
assert s.count('ARMS = ["b65", "off"]') == 1
assert 'np.load("l150/raw_l150.npz")' in s  # deliberate C0A input
print(f"BUILD OK {SRC} -> {DST}: {n0} -> {len(s)} chars; "
      f"py_compile + residual scan PASS")
