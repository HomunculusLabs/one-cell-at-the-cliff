"""L145 build: emit l145_run.py from l142_run.py via count-asserted reps.
Laws applied: l123 (full-indent anchoring, count-pin shared patterns),
l131 (enumerate all plumbing sites), l126 (context whitelist), l142b
(def-order). Residual scan over CODE lines at the end."""
import re
import py_compile

SRC = open("l142_run.py").read()


def rep(old, new, count=1):
    global SRC
    n = SRC.count(old)
    assert n == count, (f"rep site count {n} != {count}", old[:70])
    SRC = SRC.replace(old, new)


# ---- REP 1: header docstring (unique opener, whole block) ----
i0 = SRC.index('"""L142 run:')
i1 = SRC.index('"""', i0 + 10) + 3
NEWDOC = '''"""L145 run: eOutMot MIDDLE-DOSE read on fresh B31. PREREG
l145/PREREG.md FIRST (registered before this build). Arms: full, b65,
cutwA (partial base), cutng25 (super reference, pooled n=96) + 4 edge
arms on the cutwA NODE SET (1110 kept as a cell): eOutMot(10) re-roll,
eMotTop5(5)/eMotBot5(5) = |vals|-rank motor split, eMotIn(23) = motor
out + in edges. Edge arms share cutwA init + per-step noise EXACTLY
(fork-grade paired reads). Spectator arms keep graphs + pins verbatim,
never advanced (l139 law). FRESH B31 3333-3348 (absent all stored npzs
incl l142 + l144). Anchors: stored gains EXACT (cutwA/cutng25), C0A-145
vs raw_l135 (4 arms x 24 keys x 801/901 == 0.0), FC-142 forward chain
(eOutMot bisect + traces vs raw_l142 == 0.0). CPU-only; raw checkpoint
BEFORE analysis.
"""'''
SRC = SRC[:i0] + NEWDOC + SRC[i1:]

# ---- REP 2: ARMS + GAIN ----
rep('''ARMS = ["full", "b65", "cutwA", "cutng25",
        "eOutInt", "eOutMot", "eOutAll", "eIn", "eAll"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            eOutInt=None, eOutMot=None, eOutAll=None, eIn=None,
            eAll=None)''',
    '''ARMS = ["full", "b65", "cutwA", "cutng25",
        "eOutMot", "eMotTop5", "eMotBot5", "eMotIn"]
GAIN = dict(full=G_NEW, b65=G65, cutwA=None, cutng25=None,
            eOutMot=None, eMotTop5=None, eMotBot5=None, eMotIn=None)
G_EMOT_L142 = 0.14284219264984138  # l142 stored, FC-142 EXACT assert''')

# ---- REP 3: batch tokens ----
rep('B29 = list(range(3301, 3317))  # fresh, absent l107..l137 + l139 j0-j5',
    'B31 = list(range(3333, 3349))  # fresh, absent all stored npzs incl l142/l144')
rep('SEEDS = ANCH + B29                  # anchors FIRST: early wiring verdict',
    'SEEDS = ANCH + B31                  # anchors FIRST: early wiring verdict')
rep('FRESH = B29', 'FRESH = B31')

# ---- REP 4: E_ARMS + e_drop + E_EDGES assert ----
rep('''E_ARMS = ("eOutInt", "eOutMot", "eOutAll", "eIn", "eAll")''',
    '''E_ARMS = ("eOutMot", "eMotTop5", "eMotBot5", "eMotIn")''')
rep('''e_drop = {"eOutInt": out_int_e, "eOutMot": out_mot_e,
          "eOutAll": _sel_out, "eIn": in_sel_e,
          "eAll": _sel_out | in_sel_e}
E_EDGES = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert E_EDGES == {"eOutInt": 70, "eOutMot": 10, "eOutAll": 80,
                   "eIn": 13, "eAll": 93}, E_EDGES''',
    '''# L145 dose split: rank the 10 motor edges by |vals| = log1p(syn) DESC,
# tiebreak global edge pos ASC (l145/static.json pins the exact split)
_mp = np.where(out_mot_e)[0]
_mo = _mp[np.lexsort((_mp, -np.log1p(w_syn[_mp])))]
_top5 = np.zeros_like(emask_wA)
_top5[_mo[:5]] = True
_bot5 = np.zeros_like(emask_wA)
_bot5[_mo[5:]] = True
assert int(_top5.sum()) == 5 and int(_bot5.sum()) == 5
assert np.array_equal(np.where(_top5 | _bot5)[0],
                      np.where(out_mot_e)[0]), "top5|bot5 != eOutMot"
e_drop = {"eOutMot": out_mot_e, "eMotTop5": _top5, "eMotBot5": _bot5,
          "eMotIn": out_mot_e | in_sel_e}
E_EDGES = {a: int((emask_wA & e_drop[a]).sum()) for a in E_ARMS}
assert E_EDGES == {"eOutMot": 10, "eMotTop5": 5, "eMotBot5": 5,
                   "eMotIn": 23}, E_EDGES''')

# ---- REP 5: A0 block -> retired (law settled in l142 static) ----
rep('''# A0 structural law (PREREG): eAll edge positions == cutng25 node-drop
_keep25 = keep_new.copy()
_keep25[ng_desc[:25]] = False
_em25 = _keep25[src_all] & _keep25[dst_all]
assert np.array_equal(np.where(emask_wA & ~e_drop["eAll"])[0],
                      np.where(_em25)[0]), "A0 eAll != cutng25 (STOP)"''',
    '''# A0 retired (eAll==cutng25 law settled in l142 static + run);
# L145 subset law asserted inline at the e_drop block above.''')

# ---- REP 6: g_eall block -> FC-142 gain cert ----
rep('''g_eall_vs_g25 = dict(g_eAll=GAIN["eAll"], g_cutng25=GAIN["cutng25"],
                     equal=bool(GAIN["eAll"] == GAIN["cutng25"]))
log(f"A-EALL branch: {g_eall_vs_g25}")''',
    '''# FC-142 (L120 law): eOutMot bisect must re-land l142's stored gain
g_emot_exact = bool(GAIN["eOutMot"] == G_EMOT_L142)
assert g_emot_exact, ("eOutMot bisect drift vs l142", GAIN["eOutMot"])
log("FC-142 gain cert: g_eOutMot == l142 stored EXACT")''')

# ---- REP 7: st dict (14-space), X dict (13-space), noise x3 (21-space) ----
rep('''              eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),
              eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),
              eAll=Xc_wA.clone(),''',
    '''              eOutMot=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
              eMotBot5=Xc_wA.clone(), eMotIn=Xc_wA.clone(),''')
rep('''             eOutInt=Xc_wA.clone(), eOutMot=Xc_wA.clone(),
             eOutAll=Xc_wA.clone(), eIn=Xc_wA.clone(),
             eAll=Xc_wA.clone(),''',
    '''             eOutMot=Xc_wA.clone(), eMotTop5=Xc_wA.clone(),
             eMotBot5=Xc_wA.clone(), eMotIn=Xc_wA.clone(),''')
rep('''                     eOutInt=nzn[wA_pos_in_new], eOutMot=nzn[wA_pos_in_new],
                     eOutAll=nzn[wA_pos_in_new], eIn=nzn[wA_pos_in_new],
                     eAll=nzn[wA_pos_in_new],''',
    '''                     eOutMot=nzn[wA_pos_in_new],
                     eMotTop5=nzn[wA_pos_in_new],
                     eMotBot5=nzn[wA_pos_in_new], eMotIn=nzn[wA_pos_in_new],''',
    count=3)  # settle_states + seed-loop settle + WIN (l123 three-dict law)

# ---- REP 8: savez block ----
rep('''np.savez_compressed("l142/raw_l142.npz", K=K,
                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
                    g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],
                    g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"],
                    g_eAll=GAIN["eAll"],''',
    '''np.savez_compressed("l145/raw_l145.npz", K=K,
                    g_cutwA=GAIN["cutwA"], g_cutng25=GAIN["cutng25"],
                    g_eOutMot=GAIN["eOutMot"],
                    g_eMotTop5=GAIN["eMotTop5"], g_eMotBot5=GAIN["eMotBot5"],
                    g_eMotIn=GAIN["eMotIn"],''')
rep('log("raw_l135.npz checkpointed BEFORE analysis")',
    'log("raw_l145.npz checkpointed BEFORE analysis")')

# ---- REP 9: _prevs + B31 absence ----
rep('''          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",
          "l113/raw_l113.npz"]''',
    '''          "l139/raw_l139_j4.npz", "l139/raw_l139_j5.npz",
          "l113/raw_l113.npz", "l142/raw_l142.npz", "l142/raw_partial.npz",
          "l144/raw_l144.npz", "l144/raw_partial.npz"]''')
rep('''    assert not any(f"mm_full_{s}" in _zp.files for s in B29), \\
        ("B29 collides with " + _p + " (STOP)")
log(f"B29 absence across {len(_prevs)} stored npzs: PASS")''',
    '''    assert not any(f"mm_full_{s}" in _zp.files for s in B31), \\
        ("B31 collides with " + _p + " (STOP)")
log(f"B31 absence across {len(_prevs)} stored npzs: PASS")''')

# ---- REP 10: a_eall block -> FC-142 trace cert ----
rep('''a_eall = {}
for s in (801, 901):
    for key in C0A142_KEYS:
        a_eall[f"{key}_{s}"] = float(np.abs(
            store[f"{key}_eAll_{s}"] - store[f"{key}_cutng25_{s}"]).max())
a_eall_max = max(a_eall.values())
log(f"A-EALL eAll vs cutng25 in-run: max {a_eall_max:.1e} "
    f"(gains equal: {g_eall_vs_g25['equal']})")''',
    '''z142c = np.load("l142/raw_l142.npz")
fc142 = {}
for s in (801, 901):
    for key in C0A142_KEYS:
        fc142[f"142_{key}_eOutMot_{s}"] = float(np.abs(
            store[f"{key}_eOutMot_{s}"] - z142c[f"{key}_eOutMot_{s}"][:WIN]).max())
    fc142[f"142_af_eOutMot_{s}"] = abs(float(store[f"af_eOutMot_{s}"])
                                       - float(z142c[f"af_eOutMot_{s}"]))
fc142_max = max(fc142.values())
fc142_pass = bool(all(v == 0.0 for v in fc142.values()))
log(f"FC-142 eOutMot vs raw_l142 (24 keys x 2 seeds): "
    f"{'PASS' if fc142_pass else 'FAIL'} (max {fc142_max:.1e})")''')

# ---- REP 11: out dict + anchors json path + final log ----
rep('''           g_eOutInt=GAIN["eOutInt"], g_eOutMot=GAIN["eOutMot"],
           g_eOutAll=GAIN["eOutAll"], g_eIn=GAIN["eIn"], g_eAll=GAIN["eAll"],''',
    '''           g_eOutMot=GAIN["eOutMot"],
           g_eMotTop5=GAIN["eMotTop5"], g_eMotBot5=GAIN["eMotBot5"],
           g_eMotIn=GAIN["eMotIn"], g_emot_exact=g_emot_exact,''')
rep('''           n_seeds=len(SEEDS), g_eall_vs_g25=g_eall_vs_g25,
           a_eall_max=a_eall_max,''',
    '''           n_seeds=len(SEEDS), fc142_max=fc142_max, fc142_pass=fc142_pass,''')
rep('json.dump(out, open("l142/anchors_run.json", "w"), indent=1)',
    'json.dump(out, open("l145/anchors_run.json", "w"), indent=1)')
rep('''log(f"C0A-142 {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a142_max']:.1e}) | A-EALL max {a_eall_max:.1e} | "
    f"done {time.time()-t0:.0f}s")''',
    '''log(f"C0A-145 {'PASS' if out['c0a_pass'] else 'FAIL'} "
    f"(max {out['c0a142_max']:.1e}) | FC-142 "
    f"{'PASS' if fc142_pass else 'FAIL'} (max {fc142_max:.1e}) | "
    f"done {time.time()-t0:.0f}s")''')

# ---- REP 12: raw_partial paths (resume = run's OWN output, l118 direction ok) ----
rep('if os.path.exists("l142/raw_partial.npz"):',
    'if os.path.exists("l145/raw_partial.npz"):')
rep('np.savez("l142/raw_partial.npz", **store)',
    'np.savez("l145/raw_partial.npz", **store)')

# ---- REP 6b: bisect gains-dict signature (4th plumbing copy, l131 law;
# caught by the residual scan on first build) ----
rep('''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutng25=g, cutng25p=g, cutng23=g,
                                  cutng26=g, cutk5=g, eOutInt=g, eOutMot=g,
                                  eOutAll=g, eIn=g, eAll=g))''',
    '''        st = settle_states(s, dict(full=G_NEW, b65=G65, cut=g, cut19=g,
                                  cut58=g, cutng19=g, cutng29=g, cutwA=g,
                                  cutng25=g, cutng25p=g, cutng23=g,
                                  cutng26=g, cutk5=g, eOutMot=g,
                                  eMotTop5=g, eMotBot5=g, eMotIn=g))''')

# ---- residual scan: no old tokens on CODE lines (l126 context whitelist) ----
OLD = ["eOutInt", "eOutAll", "eAll", '"eIn"', "eIn=", "g_eIn",
       "B29", "g_eall", "a_eall", "raw_l142.npz\", K=K"]
res = []
for ln, line in enumerate(SRC.split("\n"), 1):
    s = line.strip()
    if not s or s.startswith("#") or s.startswith('"""') or '"""' in s[:4]:
        continue  # comment/docstring context whitelist
    for tok in OLD:
        if tok in line:
            res.append((ln, tok, line.strip()[:80]))
assert not res, ("RESIDUAL old-arm tokens on code lines", res[:10])
# legit input references that MUST survive:
for must in ['np.load("l135/raw_l135.npz")', 'np.load("l142/raw_l142.npz")',
             '"l142/raw_l142.npz", "l142/raw_partial.npz"',
             '"l144/raw_l144.npz", "l144/raw_partial.npz"']:
    assert must in SRC, ("missing legit input ref", must)
assert SRC.count("eMotTop5") >= 6 and SRC.count("eMotIn") >= 6
open("l145_run.py", "w").write(SRC)
py_compile.compile("l145_run.py", doraise=True)
print(f"l145_run.py emitted + compiled OK ({SRC.count(chr(10)) + 1} lines)")
print("residual scan: CLEAN | input-direction refs verified present")
